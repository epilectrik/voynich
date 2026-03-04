"""
A Record HEAD Composition -> B Folio Prediction Test
=====================================================

Does an A record's HEAD composition predict which B folios/programs
use those same MIDDLEs?

Background:
- A records are multi-dimensional specifications with positional HEAD structure
- Bridge MIDDLEs (85) appear in both A and B (C1139, C1140)
- B folios are programs with distinct vocabulary profiles (C531)
- The A->AZC->B pipeline means A specifications should connect to B execution

Tests:
  T1: Census — A records, bridge MIDDLEs, B folio profiles
  T2: A record -> bridge MIDDLEs -> B folios connection graph
  T3: HEAD composition clustering of A records
  T4: Within-cluster vs between-cluster B folio overlap
  T5: Per-HEAD correlation: do k-HEAD-rich A records connect to k-rich B folios?
  T6: Spearman correlation between A-record HEAD vector and mean B-folio HEAD vector
  T7: Permutation test for significance
  T8: Section control (within-section signal)
"""

import sys
import os
import io
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}  # a, e, o, k, t

HEAD_LABELS = ['a', 'e', 'k', 'o', 't', 'NONE']

N_PERMUTATIONS = 1000

# --- Atom Decomposition -------------------------------------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch == 'd' and i + 1 < len(middle) and middle[i + 1] == 'y':
            atoms.append('dy')
            i += 2
            continue
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def get_head(middle):
    """Extract HEAD atom from a MIDDLE string.
    Returns: head_base_char or 'NONE' for headless.
    """
    if not middle:
        return 'NONE'
    atoms = atomize(middle)
    if not atoms:
        return 'NONE'
    first_base = atoms[0][0]
    if first_base in HEAD_SET:
        return first_base
    return 'NONE'


def head_vector(heads_list):
    """Convert a list of HEAD labels to a fraction vector over HEAD_LABELS."""
    counts = Counter(heads_list)
    n = len(heads_list)
    if n == 0:
        return {h: 0.0 for h in HEAD_LABELS}
    return {h: counts.get(h, 0) / n for h in HEAD_LABELS}


# --- Data Loading -------------------------------------------------

def load_data():
    """Load A records, B folio data, and compute bridge MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    # --- Collect A record data ---
    a_lines = defaultdict(list)
    a_sections = {}
    for tok in tx.currier_a():
        if '*' in tok.word or not tok.word.strip():
            continue
        key = (tok.folio, tok.line)
        m = morph.extract(tok.word)
        mid = m.middle if m.middle else ''
        a_lines[key].append({
            'word': tok.word,
            'middle': mid,
        })
        if tok.folio not in a_sections:
            a_sections[tok.folio] = tok.section if hasattr(tok, 'section') else 'UNK'

    # --- Collect B folio data ---
    b_folio_tokens = defaultdict(list)  # folio -> list of middles
    b_sections = {}
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        mid = m.middle if m.middle else ''
        b_folio_tokens[tok.folio].append(mid)
        if tok.folio not in b_sections:
            b_sections[tok.folio] = tok.section if hasattr(tok, 'section') else 'UNK'

    # --- Compute bridge MIDDLEs: PP MIDDLEs present in both A and B ---
    # Collect unique MIDDLEs from A and B
    a_middles_set = set()
    for tokens in a_lines.values():
        for t in tokens:
            if t['middle']:
                a_middles_set.add(t['middle'])

    b_middles_set = set()
    for middles in b_folio_tokens.values():
        for mid in middles:
            if mid:
                b_middles_set.add(mid)

    bridge_middles = a_middles_set & b_middles_set
    print(f"  Bridge MIDDLEs (A intersect B): {len(bridge_middles)}")

    # --- Build A records ---
    a_records = []
    for (folio, line), tokens in a_lines.items():
        if len(tokens) < 2:
            continue  # Skip single-token control operators
        middles = [t['middle'] for t in tokens]
        heads = [get_head(mid) for mid in middles]
        record_bridges = [mid for mid in middles if mid in bridge_middles and mid]
        a_records.append({
            'folio': folio,
            'line': line,
            'section': a_sections.get(folio, 'UNK'),
            'middles': middles,
            'heads': heads,
            'head_vec': head_vector(heads),
            'bridge_middles': record_bridges,
            'n_bridges': len(record_bridges),
        })

    # --- Build B folio profiles ---
    b_profiles = {}
    for folio, middles in b_folio_tokens.items():
        heads = [get_head(mid) for mid in middles]
        # Per-folio MIDDLE set
        middle_set = set(m for m in middles if m)
        b_profiles[folio] = {
            'section': b_sections.get(folio, 'UNK'),
            'n_tokens': len(middles),
            'heads': heads,
            'head_vec': head_vector(heads),
            'middle_set': middle_set,
            'bridge_set': middle_set & bridge_middles,
        }

    return a_records, b_profiles, bridge_middles


# --- Analysis Functions -------------------------------------------

def cosine_sim(vec_a, vec_b, keys):
    """Cosine similarity between two dicts over given keys."""
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    norm_a = math.sqrt(sum(vec_a.get(k, 0)**2 for k in keys))
    norm_b = math.sqrt(sum(vec_b.get(k, 0)**2 for k in keys))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def spearman_rank(x, y):
    """Compute Spearman rank correlation between two lists."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def rank(arr):
        sorted_idx = sorted(range(n), key=lambda i: arr[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and arr[sorted_idx[j]] == arr[sorted_idx[j+1]]:
                j += 1
            mean_rank = (i + j) / 2.0 + 1
            for idx in range(i, j + 1):
                ranks[sorted_idx[idx]] = mean_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)

    d_sq = sum((rx[i] - ry[i])**2 for i in range(n))
    rho = 1 - (6 * d_sq) / (n * (n**2 - 1))

    # Approximate p-value via t-distribution
    if abs(rho) >= 1.0:
        p = 0.0
    else:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho**2))
        # Rough two-tailed p-value using normal approximation for large n
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))

    return rho, p


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


# --- Main ---------------------------------------------------------

def main():
    random.seed(42)
    np.random.seed(42)

    print("=" * 60)
    print("A RECORD HEAD -> B FOLIO PREDICTION TEST")
    print("=" * 60)

    print("\nLoading data...")
    a_records, b_profiles, bridge_middles = load_data()
    print(f"  A records (multi-token): {len(a_records)}")
    print(f"  B folios: {len(b_profiles)}")
    print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

    results = {
        'phase': 'INSTRUCTION_ENCODING_MAP',
        'test': 'a_record_b_folio_prediction',
    }

    # ================================================================
    # T1: CENSUS
    # ================================================================
    print("\n=== T1: Census ===")

    # A records with bridge MIDDLEs
    a_with_bridges = [r for r in a_records if r['n_bridges'] > 0]
    bridge_counts = [r['n_bridges'] for r in a_records]

    print(f"  A records with >= 1 bridge MIDDLE: {len(a_with_bridges)}/{len(a_records)} "
          f"({100*len(a_with_bridges)/len(a_records):.1f}%)")
    print(f"  Mean bridges per record: {np.mean(bridge_counts):.2f}")
    print(f"  Median bridges per record: {np.median(bridge_counts):.0f}")

    # HEAD distribution in A records
    all_a_heads = []
    for r in a_records:
        all_a_heads.extend(r['heads'])
    a_head_dist = Counter(all_a_heads)
    n_a = len(all_a_heads)
    print(f"\n  A record HEAD distribution (n={n_a}):")
    for h in HEAD_LABELS:
        c = a_head_dist.get(h, 0)
        print(f"    {h:>6}: {c:>5} ({100*c/n_a:.1f}%)")

    # HEAD distribution in B folios (pooled)
    all_b_heads = []
    for fp in b_profiles.values():
        all_b_heads.extend(fp['heads'])
    b_head_dist = Counter(all_b_heads)
    n_b = len(all_b_heads)
    print(f"\n  B folio HEAD distribution (n={n_b}):")
    for h in HEAD_LABELS:
        c = b_head_dist.get(h, 0)
        print(f"    {h:>6}: {c:>5} ({100*c/n_b:.1f}%)")

    results['t1_census'] = {
        'n_a_records': len(a_records),
        'n_a_with_bridges': len(a_with_bridges),
        'pct_with_bridges': round(100 * len(a_with_bridges) / len(a_records), 1),
        'mean_bridges_per_record': round(float(np.mean(bridge_counts)), 2),
        'n_bridge_middles': len(bridge_middles),
        'n_b_folios': len(b_profiles),
        'a_head_distribution': {h: round(a_head_dist.get(h, 0) / n_a, 4) for h in HEAD_LABELS},
        'b_head_distribution': {h: round(b_head_dist.get(h, 0) / n_b, 4) for h in HEAD_LABELS},
    }

    # ================================================================
    # T2: CONNECTION GRAPH — A record -> bridge MIDDLEs -> B folios
    # ================================================================
    print("\n=== T2: A Record -> B Folio Connection Graph ===")

    # For each A record, find which B folios contain its bridge MIDDLEs
    # Pre-compute: for each bridge MIDDLE, which B folios contain it
    bridge_to_b_folios = defaultdict(set)
    for folio, prof in b_profiles.items():
        for mid in prof['bridge_set']:
            bridge_to_b_folios[mid].add(folio)

    # Annotate A records with connected B folios
    for rec in a_records:
        connected_folios = set()
        for mid in rec['bridge_middles']:
            connected_folios.update(bridge_to_b_folios.get(mid, set()))
        rec['connected_b_folios'] = connected_folios
        rec['n_connected'] = len(connected_folios)

    a_connected = [r for r in a_records if r['n_connected'] > 0]
    connected_counts = [r['n_connected'] for r in a_records]

    print(f"  A records connected to >= 1 B folio: {len(a_connected)}/{len(a_records)} "
          f"({100*len(a_connected)/len(a_records):.1f}%)")
    print(f"  Mean B folios connected: {np.mean(connected_counts):.1f}")
    print(f"  Median B folios connected: {np.median(connected_counts):.0f}")
    print(f"  Max B folios connected: {max(connected_counts)}")

    # Bridge MIDDLE fan-out
    bridge_fanouts = [len(bridge_to_b_folios.get(mid, set())) for mid in bridge_middles]
    print(f"\n  Bridge MIDDLE fan-out to B folios:")
    print(f"    Mean: {np.mean(bridge_fanouts):.1f}")
    print(f"    Median: {np.median(bridge_fanouts):.0f}")
    print(f"    Range: {min(bridge_fanouts)}-{max(bridge_fanouts)}")

    results['t2_connection_graph'] = {
        'n_a_connected': len(a_connected),
        'pct_a_connected': round(100 * len(a_connected) / len(a_records), 1),
        'mean_b_folios_per_a_record': round(float(np.mean(connected_counts)), 1),
        'median_b_folios_per_a_record': float(np.median(connected_counts)),
        'max_b_folios': int(max(connected_counts)),
        'bridge_fanout_mean': round(float(np.mean(bridge_fanouts)), 1),
        'bridge_fanout_median': float(np.median(bridge_fanouts)),
    }

    # ================================================================
    # T3: B FOLIO HEAD PROFILE FOR EACH A RECORD
    # ================================================================
    print("\n=== T3: Mean Connected B-Folio HEAD Profile Per A Record ===")

    # For each A record, compute mean HEAD vector of its connected B folios
    for rec in a_with_bridges:
        if rec['n_connected'] == 0:
            rec['mean_b_head_vec'] = {h: 0.0 for h in HEAD_LABELS}
            continue
        # Average the HEAD vectors of connected B folios
        accum = {h: 0.0 for h in HEAD_LABELS}
        for bf in rec['connected_b_folios']:
            bv = b_profiles[bf]['head_vec']
            for h in HEAD_LABELS:
                accum[h] += bv.get(h, 0.0)
        n_conn = rec['n_connected']
        rec['mean_b_head_vec'] = {h: accum[h] / n_conn for h in HEAD_LABELS}

    # Cosine similarity between A record HEAD vec and mean connected B-folio HEAD vec
    cosines = []
    for rec in a_with_bridges:
        if rec['n_connected'] > 0:
            cs = cosine_sim(rec['head_vec'], rec['mean_b_head_vec'], HEAD_LABELS)
            cosines.append(cs)
            rec['head_cosine'] = cs

    print(f"  Mean cosine(A HEAD vec, mean connected B HEAD vec): {np.mean(cosines):.4f}")
    print(f"  Std: {np.std(cosines):.4f}")
    print(f"  Median: {np.median(cosines):.4f}")

    results['t3_head_alignment'] = {
        'mean_cosine': round(float(np.mean(cosines)), 4),
        'std_cosine': round(float(np.std(cosines)), 4),
        'median_cosine': round(float(np.median(cosines)), 4),
        'n_records_tested': len(cosines),
    }

    # ================================================================
    # T4: PER-HEAD SPEARMAN CORRELATION
    # ================================================================
    print("\n=== T4: Per-HEAD Spearman Correlation (A record -> connected B folios) ===")

    # For each HEAD type: does the fraction of that HEAD in the A record
    # correlate with the mean fraction of that HEAD in connected B folios?
    eligible = [r for r in a_with_bridges if r['n_connected'] > 0]

    per_head_results = {}
    for h in HEAD_LABELS:
        a_fracs = [r['head_vec'][h] for r in eligible]
        b_fracs = [r['mean_b_head_vec'][h] for r in eligible]

        rho, p = spearman_rank(a_fracs, b_fracs)
        print(f"  {h:>6}: rho={rho:+.4f}, p={p:.4f}, n={len(eligible)}")

        per_head_results[h] = {
            'spearman_rho': round(rho, 4),
            'p_value': round(p, 4),
            'n': len(eligible),
            'a_mean_frac': round(float(np.mean(a_fracs)), 4),
            'b_mean_frac': round(float(np.mean(b_fracs)), 4),
        }

    results['t4_per_head_correlation'] = per_head_results

    # ================================================================
    # T5: PERMUTATION TEST — Is the A->B HEAD alignment significant?
    # ================================================================
    print("\n=== T5: Permutation Test — A->B HEAD Alignment ===")

    # Real metric: mean cosine similarity between A HEAD vec and mean B HEAD vec
    real_mean_cosine = np.mean(cosines)

    # Permute: shuffle which B folios each A record connects to
    # (preserving the number of connections per record)
    all_b_folio_list = list(b_profiles.keys())
    perm_cosines = []

    for _ in range(N_PERMUTATIONS):
        perm_cos = []
        for rec in eligible:
            # Random B folios of same count
            n_conn = rec['n_connected']
            rand_folios = random.sample(all_b_folio_list, min(n_conn, len(all_b_folio_list)))
            # Compute mean HEAD vec of random B folios
            accum = {h: 0.0 for h in HEAD_LABELS}
            for bf in rand_folios:
                bv = b_profiles[bf]['head_vec']
                for h_ in HEAD_LABELS:
                    accum[h_] += bv.get(h_, 0.0)
            mean_rand_b = {h_: accum[h_] / len(rand_folios) for h_ in HEAD_LABELS}
            cs = cosine_sim(rec['head_vec'], mean_rand_b, HEAD_LABELS)
            perm_cos.append(cs)
        perm_cosines.append(np.mean(perm_cos))

    perm_cosines = np.array(perm_cosines)
    perm_mean = float(np.mean(perm_cosines))
    perm_std = float(np.std(perm_cosines))
    z_score = (real_mean_cosine - perm_mean) / (perm_std + 1e-10)
    p_value = float(np.mean(perm_cosines >= real_mean_cosine))

    print(f"  Real mean cosine: {real_mean_cosine:.4f}")
    print(f"  Permuted mean cosine: {perm_mean:.4f} +/- {perm_std:.4f}")
    print(f"  Z-score: {z_score:+.2f}")
    print(f"  P-value (one-tailed): {p_value:.4f}")
    print(f"  Verdict: {'SIGNIFICANT' if z_score > 2.0 else 'NOT SIGNIFICANT'}")

    results['t5_permutation_cosine'] = {
        'real_mean_cosine': round(real_mean_cosine, 4),
        'perm_mean_cosine': round(perm_mean, 4),
        'perm_std': round(perm_std, 4),
        'z_score': round(z_score, 2),
        'p_value': round(p_value, 4),
        'n_permutations': N_PERMUTATIONS,
        'significant': z_score > 2.0,
    }

    # ================================================================
    # T6: WITHIN-CLUSTER VS BETWEEN-CLUSTER B FOLIO OVERLAP
    # ================================================================
    print("\n=== T6: HEAD-Cluster B Folio Overlap ===")

    # Cluster A records by dominant HEAD
    head_clusters = defaultdict(list)
    for rec in eligible:
        dominant = max(HEAD_LABELS, key=lambda h: rec['head_vec'].get(h, 0))
        rec['dominant_head'] = dominant
        head_clusters[dominant].append(rec)

    print(f"  Cluster sizes:")
    for h in HEAD_LABELS:
        if h in head_clusters:
            print(f"    {h:>6}: {len(head_clusters[h])} records")

    # Within-cluster: mean Jaccard of connected B folio sets
    # Between-cluster: mean Jaccard across different clusters
    within_jaccards = []
    between_jaccards = []

    cluster_keys = [h for h in HEAD_LABELS if len(head_clusters.get(h, [])) >= 5]

    for h in cluster_keys:
        recs = head_clusters[h]
        # Within
        for i in range(len(recs)):
            for j in range(i + 1, min(i + 50, len(recs))):  # Cap comparisons
                j_val = jaccard(recs[i]['connected_b_folios'], recs[j]['connected_b_folios'])
                within_jaccards.append(j_val)

    for i_h, h1 in enumerate(cluster_keys):
        for h2 in cluster_keys[i_h + 1:]:
            recs1 = head_clusters[h1]
            recs2 = head_clusters[h2]
            # Sample pairs
            n_pairs = min(200, len(recs1) * len(recs2))
            for _ in range(n_pairs):
                r1 = random.choice(recs1)
                r2 = random.choice(recs2)
                j_val = jaccard(r1['connected_b_folios'], r2['connected_b_folios'])
                between_jaccards.append(j_val)

    within_mean = float(np.mean(within_jaccards)) if within_jaccards else 0.0
    between_mean = float(np.mean(between_jaccards)) if between_jaccards else 0.0
    ratio = within_mean / between_mean if between_mean > 0 else float('inf')

    print(f"\n  Within-cluster mean Jaccard:  {within_mean:.4f} (n={len(within_jaccards)})")
    print(f"  Between-cluster mean Jaccard: {between_mean:.4f} (n={len(between_jaccards)})")
    print(f"  Ratio (within/between): {ratio:.3f}x")

    results['t6_cluster_overlap'] = {
        'within_mean_jaccard': round(within_mean, 4),
        'between_mean_jaccard': round(between_mean, 4),
        'ratio': round(ratio, 3),
        'n_within_pairs': len(within_jaccards),
        'n_between_pairs': len(between_jaccards),
        'cluster_sizes': {h: len(head_clusters.get(h, [])) for h in HEAD_LABELS},
    }

    # ================================================================
    # T7: PER-HEAD CORRELATION WITH B FOLIO HEAD FRACTION
    # ================================================================
    print("\n=== T7: Per-HEAD Bidirectional Correlation (detailed) ===")

    # More detailed: for each HEAD, compare:
    # (a) A record fraction of that HEAD
    # (b) Weighted mean of that HEAD across connected B folios
    # Also test: does HEAD fraction predict B folio dynamical properties?

    # Compute per-B-folio k-fraction etc. for reference
    b_folio_head_profiles = {}
    for folio, prof in b_profiles.items():
        b_folio_head_profiles[folio] = prof['head_vec']

    detailed_per_head = {}
    for h in ['k', 'e', 'o', 'a', 't']:
        a_fracs = []
        b_fracs = []
        for rec in eligible:
            a_frac = rec['head_vec'].get(h, 0)
            # Weighted mean B folio HEAD fraction (weighted by bridge MIDDLEs shared)
            if rec['n_connected'] == 0:
                continue
            b_frac = rec['mean_b_head_vec'].get(h, 0)
            a_fracs.append(a_frac)
            b_fracs.append(b_frac)

        if len(a_fracs) < 10:
            continue

        rho, p = spearman_rank(a_fracs, b_fracs)

        # Also compute: variance of B frac explained
        a_arr = np.array(a_fracs)
        b_arr = np.array(b_fracs)
        if np.std(a_arr) > 0 and np.std(b_arr) > 0:
            pearson_r = float(np.corrcoef(a_arr, b_arr)[0, 1])
        else:
            pearson_r = 0.0

        detailed_per_head[h] = {
            'spearman_rho': round(rho, 4),
            'p_value': round(p, 4),
            'pearson_r': round(pearson_r, 4),
            'r_squared': round(pearson_r**2, 4),
            'a_mean': round(float(np.mean(a_fracs)), 4),
            'a_std': round(float(np.std(a_fracs)), 4),
            'b_mean': round(float(np.mean(b_fracs)), 4),
            'b_std': round(float(np.std(b_fracs)), 4),
            'n': len(a_fracs),
        }

        print(f"  HEAD '{h}': Spearman rho={rho:+.4f} (p={p:.4f}), "
              f"Pearson r={pearson_r:+.4f} (R2={pearson_r**2:.4f})")

    results['t7_detailed_per_head'] = detailed_per_head

    # ================================================================
    # T8: SECTION CONTROL — Within-section signal
    # ================================================================
    print("\n=== T8: Section Control — Within-Section Correlation ===")

    # Test: does the A->B HEAD alignment hold WITHIN sections?
    # (Controls for the possibility that sections drive both A HEAD and B HEAD)

    a_sections_set = set(r['section'] for r in eligible)
    section_controlled = {}

    for sec in sorted(a_sections_set):
        sec_recs = [r for r in eligible if r['section'] == sec and r['n_connected'] > 0]
        if len(sec_recs) < 20:
            continue

        sec_cosines = [cosine_sim(r['head_vec'], r['mean_b_head_vec'], HEAD_LABELS) for r in sec_recs]
        sec_mean = float(np.mean(sec_cosines))

        # Per-head correlations within section
        sec_per_head = {}
        for h in ['k', 'e', 'o']:
            a_f = [r['head_vec'].get(h, 0) for r in sec_recs]
            b_f = [r['mean_b_head_vec'].get(h, 0) for r in sec_recs]
            rho, p = spearman_rank(a_f, b_f)
            sec_per_head[h] = {'rho': round(rho, 4), 'p': round(p, 4)}

        print(f"  Section {sec} (n={len(sec_recs)}): mean cosine={sec_mean:.4f}")
        for h in ['k', 'e', 'o']:
            d = sec_per_head[h]
            print(f"    {h}: rho={d['rho']:+.4f} (p={d['p']:.4f})")

        section_controlled[sec] = {
            'n': len(sec_recs),
            'mean_cosine': round(sec_mean, 4),
            'per_head': sec_per_head,
        }

    results['t8_section_control'] = section_controlled

    # ================================================================
    # T9: PERMUTATION TEST — Per-HEAD significance
    # ================================================================
    print("\n=== T9: Per-HEAD Permutation Tests ===")

    per_head_perm = {}
    for h in ['k', 'e', 'o', 'a', 't']:
        real_a = [r['head_vec'].get(h, 0) for r in eligible]
        real_b = [r['mean_b_head_vec'].get(h, 0) for r in eligible]
        real_rho, _ = spearman_rank(real_a, real_b)

        perm_rhos = []
        for _ in range(N_PERMUTATIONS):
            # Shuffle A-record HEAD fracs
            shuffled_a = real_a.copy()
            random.shuffle(shuffled_a)
            perm_rho, _ = spearman_rank(shuffled_a, real_b)
            perm_rhos.append(perm_rho)

        perm_rhos = np.array(perm_rhos)
        perm_z = (real_rho - float(np.mean(perm_rhos))) / (float(np.std(perm_rhos)) + 1e-10)
        perm_p = float(np.mean(np.abs(perm_rhos) >= abs(real_rho)))

        print(f"  HEAD '{h}': real rho={real_rho:+.4f}, perm mean={np.mean(perm_rhos):+.4f}, "
              f"z={perm_z:+.2f}, p={perm_p:.4f}")

        per_head_perm[h] = {
            'real_rho': round(real_rho, 4),
            'perm_mean_rho': round(float(np.mean(perm_rhos)), 4),
            'perm_std': round(float(np.std(perm_rhos)), 4),
            'z_score': round(perm_z, 2),
            'p_value': round(perm_p, 4),
            'significant': abs(perm_z) > 2.0,
        }

    results['t9_per_head_permutation'] = per_head_perm

    # ================================================================
    # T10: BRIDGE MIDDLE HEAD COMPOSITION — Do shared MIDDLEs carry HEAD?
    # ================================================================
    print("\n=== T10: Bridge MIDDLE HEAD Composition ===")

    bridge_heads = Counter()
    for mid in bridge_middles:
        h = get_head(mid)
        bridge_heads[h] += 1

    n_bridge = len(bridge_middles)
    print(f"  Bridge MIDDLE HEAD distribution (n={n_bridge}):")
    for h in HEAD_LABELS:
        c = bridge_heads.get(h, 0)
        print(f"    {h:>6}: {c:>3} ({100*c/n_bridge:.1f}%)")

    # Compare with overall A HEAD distribution
    print(f"\n  A overall vs Bridge HEAD fractions:")
    for h in HEAD_LABELS:
        a_frac = a_head_dist.get(h, 0) / n_a
        br_frac = bridge_heads.get(h, 0) / n_bridge
        ratio_val = br_frac / a_frac if a_frac > 0 else float('inf')
        print(f"    {h:>6}: A={a_frac:.3f}, Bridge={br_frac:.3f}, ratio={ratio_val:.2f}x")

    results['t10_bridge_head'] = {
        'bridge_head_distribution': {h: round(bridge_heads.get(h, 0) / n_bridge, 4) for h in HEAD_LABELS},
        'bridge_vs_a_ratio': {h: round((bridge_heads.get(h, 0) / n_bridge) / (a_head_dist.get(h, 0) / n_a), 3)
                             if a_head_dist.get(h, 0) > 0 else None
                             for h in HEAD_LABELS},
    }

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Determine overall verdict
    t5_sig = results['t5_permutation_cosine']['significant']
    n_head_sig = sum(1 for h in per_head_perm.values() if h['significant'])
    cluster_ratio = results['t6_cluster_overlap']['ratio']

    if t5_sig and n_head_sig >= 3:
        verdict = "STRONG_PREDICTION"
    elif t5_sig or n_head_sig >= 2:
        verdict = "MODERATE_PREDICTION"
    elif n_head_sig >= 1 or cluster_ratio > 1.1:
        verdict = "WEAK_PREDICTION"
    else:
        verdict = "NO_PREDICTION"

    print(f"\n  Overall verdict: {verdict}")
    print(f"\n  Cosine alignment (A HEAD vec -> mean B HEAD vec):")
    print(f"    Real: {results['t5_permutation_cosine']['real_mean_cosine']:.4f}")
    print(f"    Permuted: {results['t5_permutation_cosine']['perm_mean_cosine']:.4f}")
    print(f"    Z-score: {results['t5_permutation_cosine']['z_score']:+.2f}")
    print(f"    Significant: {t5_sig}")
    print(f"\n  Per-HEAD significant correlations: {n_head_sig}/5")
    for h in ['k', 'e', 'o', 'a', 't']:
        d = per_head_perm[h]
        sig = '*' if d['significant'] else ' '
        print(f"    {sig} {h}: rho={d['real_rho']:+.4f}, z={d['z_score']:+.2f}")
    print(f"\n  Cluster overlap ratio (within/between): {cluster_ratio:.3f}x")
    print(f"\n  Section-controlled tests:")
    for sec, d in section_controlled.items():
        print(f"    {sec}: mean cosine={d['mean_cosine']:.4f}, n={d['n']}")

    results['summary'] = {
        'verdict': verdict,
        'cosine_z_score': results['t5_permutation_cosine']['z_score'],
        'cosine_significant': t5_sig,
        'n_head_significant': n_head_sig,
        'cluster_ratio': cluster_ratio,
        'per_head_rhos': {h: per_head_perm[h]['real_rho'] for h in ['k', 'e', 'o', 'a', 't']},
        'per_head_z_scores': {h: per_head_perm[h]['z_score'] for h in ['k', 'e', 'o', 'a', 't']},
    }

    # Write results
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = RESULTS_DIR / 'a_record_b_folio_prediction.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
