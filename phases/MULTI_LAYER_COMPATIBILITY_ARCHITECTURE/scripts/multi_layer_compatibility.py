#!/usr/bin/env python3
"""
Phase 381: Multi-Layer Compatibility Architecture

5-test battery examining how three independently-discovered forbidden/
incompatibility layers interact across MIDDLE, PREFIX, and SUFFIX dimensions.

T1: Cross-Layer Independence (MI between C475, C911, C1063)
T2: C475 Community Structure (hub-removed modularity)
T3: Atom Ordering x Kernel Profile (C1065 asymmetry vs C521 direction)
T4: Component-Level Hazard Residual (C109 x three layers)
T5: Terminal Character x Compatibility (C1067 x C475)

All Tier 2 targets. Expert-advisor validated.
"""

import sys
import json
import functools
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy.stats import chi2_contingency, fisher_exact, binomtest
import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS = ROOT / "phases" / "MULTI_LAYER_COMPATIBILITY_ARCHITECTURE" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table."""
    table = np.array(contingency_table)
    if table.sum() == 0:
        return 0.0
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    r, k = table.shape
    return float(np.sqrt(chi2 / (n * (min(r, k) - 1)))) if min(r, k) > 1 else 0.0


def save_result(data, filename):
    """Save result JSON."""
    path = RESULTS / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved: {path}")


def compute_nmi(table):
    """Compute normalized mutual information from a contingency table."""
    table = np.array(table, dtype=float)
    total = table.sum()
    if total == 0:
        return 0.0
    p_joint = table / total
    p_x = table.sum(axis=1) / total
    p_y = table.sum(axis=0) / total

    # Mutual information
    mi = 0.0
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            if p_joint[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += p_joint[i, j] * math.log(p_joint[i, j] / (p_x[i] * p_y[j]))

    # Entropies
    h_x = -sum(px * math.log(px) for px in p_x if px > 0)
    h_y = -sum(py * math.log(py) for py in p_y if py > 0)

    denom = min(h_x, h_y)
    if denom < 1e-10:
        return 0.0
    return mi / denom


# ============================================================
# DATA LOADING
# ============================================================

def reconstruct_middle_list():
    """Reconstruct the 972-element MIDDLE ordering matching t1_compat_matrix.npy."""
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    return all_middles, mid_to_idx


def load_data():
    """Load all shared data for the 5-test battery."""
    morph = Morphology()

    # 1. Compatibility matrix (972x972)
    compat_path = ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    compat_matrix = np.load(compat_path)
    all_middles, mid_to_idx = reconstruct_middle_list()
    print(f"  Compatibility matrix: {compat_matrix.shape}, MIDDLEs: {len(all_middles)}")

    # 2. C911 PREFIX x MIDDLE forbidden pairs
    c911_path = ROOT / 'phases' / 'MIDDLE_SEMANTIC_DEEPENING' / 'results' / 'prefix_middle_interaction.json'
    with open(c911_path, 'r', encoding='utf-8') as f:
        c911_data = json.load(f)
    c911_forbidden = set()
    for pair in c911_data['forbidden_pairs']:
        pfx = None if pair['prefix'] == '(none)' else pair['prefix']
        c911_forbidden.add((pfx, pair['middle']))
    print(f"  C911 forbidden PREFIX x MIDDLE pairs: {len(c911_forbidden)}")

    # 3. C1063 PREFIX x SUFFIX forbidden pairs
    c1063_path = ROOT / 'phases' / 'MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE' / 'results' / 't1_prefix_suffix_forbidden.json'
    with open(c1063_path, 'r', encoding='utf-8') as f:
        c1063_data = json.load(f)
    c1063_forbidden = set()
    for pair in c1063_data['forbidden_pairs']:
        pfx = None if pair['prefix'] == '_BARE_' else pair['prefix']
        sfx = None if pair['suffix'] == '_BARE_' else pair['suffix']
        c1063_forbidden.add((pfx, sfx))
    print(f"  C1063 forbidden PREFIX x SUFFIX pairs: {len(c1063_forbidden)}")

    # 4. C109 forbidden transitions
    c109_path = ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
    with open(c109_path, 'r', encoding='utf-8') as f:
        c109_data = json.load(f)
    c109_transitions = c109_data['transitions']
    print(f"  C109 forbidden transitions: {len(c109_transitions)}")

    # 5. C908 kernel profiles
    c908_path = ROOT / 'phases' / 'MIDDLE_SEMANTIC_MAPPING' / 'results' / 'kernel_middle_correlation.json'
    with open(c908_path, 'r', encoding='utf-8') as f:
        kernel_profiles = json.load(f)

    # 6. C1065 asymmetric atom pairs
    c1065_path = ROOT / 'phases' / 'MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE' / 'results' / 't3_atom_bigram_grammar.json'
    with open(c1065_path, 'r', encoding='utf-8') as f:
        c1065_data = json.load(f)
    c1065_asymmetric = c1065_data['asymmetric_pairs']

    # 7. C1067 terminal character data
    c1067_path = ROOT / 'phases' / 'MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE' / 'results' / 't5_terminal_character_bias.json'
    with open(c1067_path, 'r', encoding='utf-8') as f:
        c1067_terminal = json.load(f)

    # 8. Currier B tokens with morphology
    tx = Transcript()
    b_tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        b_tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        })
    print(f"  Currier B tokens: {len(b_tokens)}")

    return (compat_matrix, all_middles, mid_to_idx,
            c911_forbidden, c1063_forbidden, c109_transitions,
            kernel_profiles, c1065_asymmetric, c1067_terminal,
            b_tokens, morph)


# ============================================================
# T1: CROSS-LAYER INDEPENDENCE
# ============================================================

def run_t1(b_tokens, compat_matrix, all_middles, mid_to_idx, c911_forbidden, c1063_forbidden):
    """Test independence of C475, C911, C1063 constraint layers."""
    print("\n" + "=" * 60)
    print("T1: Cross-Layer Independence")
    print("    Prior: C1003 predicts independence (different morphological axes)")
    print("=" * 60)

    # Compute C475 degree for each MIDDLE (number of compatible MIDDLEs)
    n_mid = len(all_middles)
    c475_degree = {}
    for i, mid in enumerate(all_middles):
        c475_degree[mid] = int(compat_matrix[i].sum())

    # Compute C911 restriction count for each MIDDLE
    c911_restriction = Counter()
    for pfx, mid in c911_forbidden:
        c911_restriction[mid] += 1

    # Compute C1063 restriction count for each PREFIX
    c1063_restriction = Counter()
    for pfx, sfx in c1063_forbidden:
        c1063_restriction[pfx] += 1

    # Bin C475 degree into quartiles
    degrees = [c475_degree.get(mid, 0) for mid in all_middles]
    q25, q50, q75 = np.percentile(degrees, [25, 50, 75])

    def bin_degree(d):
        if d <= q25:
            return 0
        elif d <= q50:
            return 1
        elif d <= q75:
            return 2
        return 3

    # Bin C911 restriction: 0, 1, 2+
    def bin_c911(mid):
        r = c911_restriction.get(mid, 0)
        return min(r, 2)

    # Bin C1063 restriction: 0, 1, 2+
    def bin_c1063(pfx):
        r = c1063_restriction.get(pfx, 0)
        return min(r, 2)

    # Assign bins per token
    token_bins = []
    for t in b_tokens:
        mid = t['middle']
        pfx = t['prefix']
        if mid not in mid_to_idx:
            continue
        b_c475 = bin_degree(c475_degree.get(mid, 0))
        b_c911 = bin_c911(mid)
        b_c1063 = bin_c1063(pfx)
        token_bins.append((b_c475, b_c911, b_c1063))

    print(f"  Tokens with valid MIDDLE in matrix: {len(token_bins)}")

    # Build contingency tables
    pairs = [
        ('C475_degree x C911_restriction', 0, 1, 4, 3),
        ('C475_degree x C1063_restriction', 0, 2, 4, 3),
        ('C911_restriction x C1063_restriction', 1, 2, 3, 3),
    ]

    results_pairs = []
    for name, idx_a, idx_b, n_a, n_b in pairs:
        table = np.zeros((n_a, n_b), dtype=int)
        for bins in token_bins:
            table[bins[idx_a], bins[idx_b]] += 1

        # Remove zero-sum rows/columns for chi2
        row_mask = table.sum(axis=1) > 0
        col_mask = table.sum(axis=0) > 0
        table_clean = table[row_mask][:, col_mask]

        if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
            results_pairs.append({
                'pair': name, 'chi2': 0, 'p': 1.0, 'V': 0.0, 'NMI': 0.0,
                'note': 'insufficient variation'
            })
            print(f"  {name}: insufficient variation")
            continue

        chi2, p, _, _ = chi2_contingency(table_clean)
        v = cramers_v(table_clean)
        nmi = compute_nmi(table_clean)

        results_pairs.append({
            'pair': name,
            'chi2': round(chi2, 1),
            'p': p,
            'V': round(v, 4),
            'NMI': round(nmi, 4),
            'table_shape': list(table_clean.shape),
        })
        print(f"  {name}: chi2={chi2:.1f}, p={p:.2e}, V={v:.4f}, NMI={nmi:.4f}")

    # Permutation null for frequency control (1000 shuffles)
    print("\n  Running permutation null (1000 shuffles)...")
    rng = np.random.default_rng(42)

    # Shuffle C911 restriction assignments across MIDDLEs
    middles_in_matrix = [m for m in all_middles if m in mid_to_idx]
    original_c911_vals = [c911_restriction.get(m, 0) for m in middles_in_matrix]

    null_nmis = {p['pair']: [] for p in results_pairs}

    for _ in range(1000):
        shuffled_c911 = list(original_c911_vals)
        rng.shuffle(shuffled_c911)
        shuffled_c911_map = {m: v for m, v in zip(middles_in_matrix, shuffled_c911)}

        perm_bins = []
        for t in b_tokens:
            mid = t['middle']
            pfx = t['prefix']
            if mid not in mid_to_idx:
                continue
            b_c475 = bin_degree(c475_degree.get(mid, 0))
            b_c911 = min(shuffled_c911_map.get(mid, 0), 2)
            b_c1063 = bin_c1063(pfx)
            perm_bins.append((b_c475, b_c911, b_c1063))

        for pair_info in results_pairs:
            name = pair_info['pair']
            if 'C911' in name:
                if 'C475' in name:
                    idx_a, idx_b, n_a, n_b = 0, 1, 4, 3
                else:
                    idx_a, idx_b, n_a, n_b = 1, 2, 3, 3
                table = np.zeros((n_a, n_b), dtype=int)
                for bins in perm_bins:
                    table[bins[idx_a], bins[idx_b]] += 1
                row_mask = table.sum(axis=1) > 0
                col_mask = table.sum(axis=0) > 0
                table_clean = table[row_mask][:, col_mask]
                if table_clean.shape[0] >= 2 and table_clean.shape[1] >= 2:
                    null_nmis[name].append(compute_nmi(table_clean))

    for pair_info in results_pairs:
        name = pair_info['pair']
        if null_nmis[name]:
            obs_nmi = pair_info['NMI']
            perm_p = np.mean([n >= obs_nmi for n in null_nmis[name]])
            pair_info['perm_null_mean_NMI'] = round(float(np.mean(null_nmis[name])), 4)
            pair_info['perm_null_p'] = round(float(perm_p), 4)
            print(f"  {name} permutation: null_mean={np.mean(null_nmis[name]):.4f}, p={perm_p:.4f}")

    # Verdict: PASS if all NMI < 0.1 and permutation confirms
    all_nmi_low = all(p.get('NMI', 0) < 0.1 for p in results_pairs)
    perm_confirms = all(
        p.get('perm_null_p', 1.0) > 0.05
        for p in results_pairs
        if 'perm_null_p' in p
    )

    if all_nmi_low and perm_confirms:
        verdict = "PASS"
    elif all_nmi_low:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Verdict: {verdict}")
    print(f"  Interpretation: {'Quantitative confirmation of C1003 at forbidden-pair topology level' if verdict == 'PASS' else 'Layers show unexpected coupling'}")

    result = {
        'test': 'T1_cross_layer_independence',
        'verdict': verdict,
        'n_tokens_tested': len(token_bins),
        'c475_degree_quartiles': [float(q25), float(q50), float(q75)],
        'c911_forbidden_count': len(c911_forbidden),
        'c1063_forbidden_count': len(c1063_forbidden),
        'pairs': results_pairs,
        'constraints_referenced': ['C475', 'C911', 'C1063', 'C1003', 'C660'],
    }
    save_result(result, 't1_cross_layer_independence.json')
    return result


# ============================================================
# T2: C475 COMMUNITY STRUCTURE (HUB-REMOVED)
# ============================================================

def run_t2(compat_matrix, all_middles, mid_to_idx, kernel_profiles):
    """Test for community structure in C475 graph after hub removal."""
    print("\n" + "=" * 60)
    print("T2: C475 Community Structure (Hub-Removed)")
    print("    Prior: C987 predicts continuous manifold (no communities)")
    print("=" * 60)

    n = len(all_middles)

    # Build NetworkX graph from compatibility matrix
    G_raw = nx.Graph()
    G_raw.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if compat_matrix[i, j] > 0:
                G_raw.add_edge(i, j)

    n_edges_raw = G_raw.number_of_edges()
    print(f"  Raw graph: {n} nodes, {n_edges_raw} edges")

    # Raw Louvain modularity
    raw_communities = nx.community.louvain_communities(G_raw, seed=42)
    q_raw = nx.community.modularity(G_raw, raw_communities)
    print(f"  Raw Louvain: {len(raw_communities)} communities, Q={q_raw:.4f}")

    # Hub removal: configuration model subtraction
    degrees = np.array([compat_matrix[i].sum() for i in range(n)], dtype=float)
    total_2m = degrees.sum()
    if total_2m == 0:
        total_2m = 1.0

    # Expected adjacency under configuration model
    expected = np.outer(degrees, degrees) / total_2m

    # Residual adjacency
    residual = compat_matrix.astype(float) - expected

    # Also partial out log-frequency (doubly-deconfounded)
    # Use degree as proxy for frequency (C986: hub-frequency rho=-0.792)
    log_freq = np.log1p(degrees)
    log_freq_normed = (log_freq - log_freq.mean()) / max(log_freq.std(), 1e-10)

    # Regress out frequency from each row of residual
    for i in range(n):
        row = residual[i]
        # Simple regression: row_i = a * log_freq + residual
        coef = np.dot(row, log_freq_normed) / max(np.dot(log_freq_normed, log_freq_normed), 1e-10)
        residual[i] -= coef * log_freq_normed

    # Symmetrize
    residual = (residual + residual.T) / 2.0

    # Threshold at 0 for binary graph
    residual_binary = (residual > 0).astype(int)
    np.fill_diagonal(residual_binary, 0)

    # Build residual graph
    G_resid = nx.Graph()
    G_resid.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if residual_binary[i, j] > 0:
                G_resid.add_edge(i, j)

    n_edges_resid = G_resid.number_of_edges()
    print(f"  Residual graph: {n_edges_resid} edges (density={n_edges_resid / max(n*(n-1)//2, 1):.4f})")

    # Louvain on residual
    if n_edges_resid > 0:
        resid_communities = nx.community.louvain_communities(G_resid, seed=42)
        q_resid = nx.community.modularity(G_resid, resid_communities)
    else:
        resid_communities = [{i} for i in range(n)]
        q_resid = 0.0
    print(f"  Residual Louvain: {len(resid_communities)} communities, Q_residual={q_resid:.4f}")

    # Random graph null (degree-matched)
    print("  Computing random graph null (10 samples)...")
    q_randoms = []
    for seed in range(10):
        # Configuration model random graph
        degree_seq = [G_resid.degree(i) for i in range(n)]
        if sum(degree_seq) % 2 == 1:
            degree_seq[0] += 1
        try:
            G_rand = nx.configuration_model(degree_seq, seed=seed)
            G_rand = nx.Graph(G_rand)  # Remove parallel edges
            G_rand.remove_edges_from(nx.selfloop_edges(G_rand))
            if G_rand.number_of_edges() > 0:
                rand_comms = nx.community.louvain_communities(G_rand, seed=42)
                q_rand = nx.community.modularity(G_rand, rand_comms)
                q_randoms.append(q_rand)
        except Exception:
            pass

    q_random_mean = float(np.mean(q_randoms)) if q_randoms else 0.0
    q_signal = q_resid - q_random_mean
    print(f"  Random null: Q_random_mean={q_random_mean:.4f}")
    print(f"  Signal: Q_residual - Q_random = {q_signal:.4f}")

    # Kernel profile alignment for top communities
    # Build MIDDLE -> kernel classification from C908
    kernel_class = {}
    for entry in kernel_profiles.get('k_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            kernel_class[entry['middle']] = 'k'
    for entry in kernel_profiles.get('h_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            if entry['middle'] not in kernel_class:
                kernel_class[entry['middle']] = 'h'
    for entry in kernel_profiles.get('e_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            if entry['middle'] not in kernel_class:
                kernel_class[entry['middle']] = 'e'

    # Report top 5 communities
    community_profiles = []
    sorted_comms = sorted(resid_communities, key=len, reverse=True)[:5]
    for ci, comm in enumerate(sorted_comms):
        members = [all_middles[idx] for idx in comm]
        k_count = sum(1 for m in members if kernel_class.get(m) == 'k')
        h_count = sum(1 for m in members if kernel_class.get(m) == 'h')
        e_count = sum(1 for m in members if kernel_class.get(m) == 'e')
        classified = k_count + h_count + e_count
        community_profiles.append({
            'community': ci,
            'size': len(comm),
            'k_enriched': k_count,
            'h_enriched': h_count,
            'e_enriched': e_count,
            'classified_total': classified,
            'sample_members': members[:10],
        })
        print(f"  Community {ci}: size={len(comm)}, k={k_count}, h={h_count}, e={e_count}")

    # Verdict
    if q_signal > 0.2:
        verdict = "PASS"
    elif q_signal > 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Verdict: {verdict}")
    if verdict == "FAIL":
        print("  Interpretation: Confirms C987 continuous manifold via independent method (modularity vs silhouette)")

    result = {
        'test': 'T2_community_structure',
        'verdict': verdict,
        'n_nodes': n,
        'raw_edges': n_edges_raw,
        'raw_n_communities': len(raw_communities),
        'raw_modularity': round(q_raw, 4),
        'residual_edges': n_edges_resid,
        'residual_n_communities': len(resid_communities),
        'residual_modularity': round(q_resid, 4),
        'random_null_modularity': round(q_random_mean, 4),
        'signal_Q': round(q_signal, 4),
        'community_profiles': community_profiles,
        'constraints_referenced': ['C475', 'C983', 'C986', 'C987', 'C988', 'C908', 'C984'],
    }
    save_result(result, 't2_community_structure.json')
    return result


# ============================================================
# T3: ATOM ORDERING x KERNEL PROFILE
# ============================================================

def run_t3(c1065_asymmetric, kernel_profiles):
    """Test whether asymmetric atom pairs correlate with kernel content."""
    print("\n" + "=" * 60)
    print("T3: Atom Ordering x Kernel Profile")
    print("    Tests C1065 asymmetric pairs against C521 directional bias")
    print("=" * 60)

    # Build kernel classification for atoms
    # Method 1: Direct lookup in C908 profiles
    c908_kernel = {}
    for entry in kernel_profiles.get('k_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            c908_kernel[entry['middle']] = 'k'
    for entry in kernel_profiles.get('h_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            if entry['middle'] not in c908_kernel:
                c908_kernel[entry['middle']] = 'h'
    for entry in kernel_profiles.get('e_enriched', []):
        if entry.get('ratio', 0) > 1.2 and entry.get('p', 1) < 0.01:
            if entry['middle'] not in c908_kernel:
                c908_kernel[entry['middle']] = 'e'

    # Method 2: Character content fallback
    def classify_atom(atom):
        """Classify atom by kernel content. C908 lookup first, then character content."""
        if atom in c908_kernel:
            return c908_kernel[atom], 'c908'
        # Character content fallback
        has_k = 'k' in atom
        has_h = 'h' in atom
        has_e = 'e' in atom
        if has_k and not has_h and not has_e:
            return 'k', 'char'
        if has_h and not has_k and not has_e:
            return 'h', 'char'
        if has_e and not has_k and not has_h:
            return 'e', 'char'
        if has_k and has_e:
            return 'ke', 'char'
        if has_k and has_h:
            return 'kh', 'char'
        if has_h and has_e:
            return 'he', 'char'
        return None, 'none'

    # C521 directional bias rules:
    # h->e FAVORED (7.00x)
    # k->e FAVORED (4.32x)
    # k->h neutral (1.10x)
    # e->h BLOCKED (0.00)
    # h->k SUPPRESSED (0.22x)
    # e->k SUPPRESSED (0.27x)
    # Summary: k and h come BEFORE e. k is roughly neutral with h.
    def c521_predicts(first_class, second_class):
        """Return True if C521 predicts first before second."""
        # k before e: yes (4.32x)
        if first_class in ('k', 'kh') and second_class in ('e',):
            return True
        # h before e: yes (7.00x)
        if first_class in ('h', 'kh') and second_class in ('e',):
            return True
        # e before k: no (0.27x suppressed)
        if first_class in ('e',) and second_class in ('k', 'kh'):
            return False
        # e before h: no (0.00 blocked)
        if first_class in ('e',) and second_class in ('h', 'kh'):
            return False
        # ke before e: mixed kernel, but k component suggests before e
        if first_class in ('ke',) and second_class in ('e',):
            return True
        if first_class in ('e',) and second_class in ('ke',):
            return False
        return None  # No prediction

    # Analyze each asymmetric pair
    print(f"\n  Asymmetric pairs from C1065: {len(c1065_asymmetric)}")
    pair_analyses = []
    kernel_involved = []

    for pair in c1065_asymmetric:
        dominant = pair['dominant']
        subordinate = pair['subordinate']
        # In asymmetric pairs, dominant appears BEFORE subordinate at >80% rate
        # (or subordinate before dominant if fwd=0)
        fwd = pair['fwd']
        rev = pair['rev']

        # Determine which comes first
        if fwd >= rev:
            first_atom = dominant
            second_atom = subordinate
        else:
            first_atom = subordinate
            second_atom = dominant

        first_class, first_method = classify_atom(first_atom)
        second_class, second_method = classify_atom(second_atom)

        prediction = None
        if first_class and second_class:
            prediction = c521_predicts(first_class, second_class)

        analysis = {
            'first': first_atom,
            'second': second_atom,
            'first_class': first_class,
            'first_method': first_method,
            'second_class': second_class,
            'second_method': second_method,
            'rate': pair['rate'],
            'n': pair['total'],
            'c521_predicts_this_order': prediction,
        }
        pair_analyses.append(analysis)

        if prediction is not None:
            kernel_involved.append(analysis)

        class_str = f"{first_class or '?'}→{second_class or '?'}"
        pred_str = f"{'MATCH' if prediction == True else 'MISMATCH' if prediction == False else 'N/A'}"
        print(f"  {first_atom}→{second_atom}: {class_str} [{first_method}/{second_method}] {pred_str}")

    # Statistical test on kernel-involved pairs
    n_kernel = len(kernel_involved)
    n_match = sum(1 for a in kernel_involved if a['c521_predicts_this_order'] == True)
    n_mismatch = sum(1 for a in kernel_involved if a['c521_predicts_this_order'] == False)

    print(f"\n  Kernel-involved pairs: {n_kernel}")
    print(f"  Matches C521: {n_match}")
    print(f"  Mismatches C521: {n_mismatch}")

    # One-sided binomial test: match rate > 50%
    if n_kernel > 0:
        binom_result = binomtest(n_match, n_kernel, 0.5, alternative='greater')
        binom_p = binom_result.pvalue
        match_rate = n_match / n_kernel
    else:
        binom_p = 1.0
        match_rate = 0.0

    print(f"  Match rate: {match_rate:.1%}")
    print(f"  Binomial p (>50%): {binom_p:.4f}")

    # Fisher's exact on 2x2 table (kernel-involved: match/mismatch vs expected under random)
    if n_kernel >= 2:
        # Observed vs expected under 50/50
        table_2x2 = np.array([[n_match, n_mismatch],
                               [n_kernel // 2, n_kernel - n_kernel // 2]])
        _, fisher_p = fisher_exact(table_2x2, alternative='greater')
    else:
        fisher_p = 1.0

    # Classification method breakdown
    n_c908 = sum(1 for a in pair_analyses if a['first_method'] == 'c908' or a['second_method'] == 'c908')
    n_char = sum(1 for a in pair_analyses if a['first_method'] == 'char' or a['second_method'] == 'char')

    # Verdict
    if binom_p < 0.05 and match_rate > 0.60:
        verdict = "PASS"
    elif match_rate > 0.50 and binom_p < 0.10:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Verdict: {verdict}")

    result = {
        'test': 'T3_atom_kernel_correlation',
        'verdict': verdict,
        'n_asymmetric_pairs': len(c1065_asymmetric),
        'n_kernel_involved': n_kernel,
        'n_match_c521': n_match,
        'n_mismatch_c521': n_mismatch,
        'match_rate': round(match_rate, 4),
        'binomial_p': round(binom_p, 4),
        'fisher_p': round(fisher_p, 4),
        'classification_methods': {'c908_involved': n_c908, 'char_involved': n_char},
        'pair_analyses': pair_analyses,
        'constraints_referenced': ['C1065', 'C521', 'C908', 'C873'],
    }
    save_result(result, 't3_atom_kernel_correlation.json')
    return result


# ============================================================
# T4: COMPONENT-LEVEL HAZARD RESIDUAL CHARACTERIZATION
# ============================================================

def run_t4(c109_transitions, compat_matrix, all_middles, mid_to_idx, c911_forbidden, c1063_forbidden, morph):
    """Characterize what C109 forbidden transitions are NOT explained by component layers."""
    print("\n" + "=" * 60)
    print("T4: Component-Level Hazard Residual Characterization")
    print("    Reframed: quantifies gap confirming C627 token-specific mechanism")
    print("=" * 60)

    coverage = []
    for t in c109_transitions:
        src = t['source']
        tgt = t['target']
        src_m = morph.extract(src)
        tgt_m = morph.extract(tgt)

        src_mid = src_m.middle
        tgt_mid = tgt_m.middle

        # Layer A: C475 MIDDLE incompatibility
        c475_blocked = False
        c475_note = ''
        if src_mid in mid_to_idx and tgt_mid in mid_to_idx:
            i, j = mid_to_idx[src_mid], mid_to_idx[tgt_mid]
            c475_blocked = (compat_matrix[i, j] == 0)
            c475_note = f"compat={int(compat_matrix[i, j])}"
        else:
            missing = []
            if src_mid not in mid_to_idx:
                missing.append(f"src '{src_mid}'")
            if tgt_mid not in mid_to_idx:
                missing.append(f"tgt '{tgt_mid}'")
            c475_note = f"not in matrix: {', '.join(missing)}"

        # Layer B: C911 PREFIX x MIDDLE forbidden
        c911_blocks_src = (src_m.prefix, src_mid) in c911_forbidden
        c911_blocks_tgt = (tgt_m.prefix, tgt_mid) in c911_forbidden
        c911_blocked = c911_blocks_src or c911_blocks_tgt

        # Layer C: C1063 PREFIX x SUFFIX forbidden
        c1063_blocks_src = (src_m.prefix, src_m.suffix) in c1063_forbidden
        c1063_blocks_tgt = (tgt_m.prefix, tgt_m.suffix) in c1063_forbidden
        c1063_blocked = c1063_blocks_src or c1063_blocks_tgt

        any_blocked = c475_blocked or c911_blocked or c1063_blocked

        entry = {
            'id': t['id'],
            'source': src,
            'target': tgt,
            'source_decomp': {'prefix': src_m.prefix, 'middle': src_mid, 'suffix': src_m.suffix},
            'target_decomp': {'prefix': tgt_m.prefix, 'middle': tgt_mid, 'suffix': tgt_m.suffix},
            'c475_blocked': c475_blocked,
            'c475_note': c475_note,
            'c911_blocked': c911_blocked,
            'c911_blocks_src': c911_blocks_src,
            'c911_blocks_tgt': c911_blocks_tgt,
            'c1063_blocked': c1063_blocked,
            'any_layer_blocks': any_blocked,
            'source_type': t.get('source_type', ''),
            'target_type': t.get('target_type', ''),
        }
        coverage.append(entry)

        status = 'COVERED' if any_blocked else 'RESIDUAL'
        layers = []
        if c475_blocked:
            layers.append('C475')
        if c911_blocked:
            layers.append('C911')
        if c1063_blocked:
            layers.append('C1063')
        layer_str = '+'.join(layers) if layers else 'NONE'
        print(f"  {t['id']:2d}. {src:8s} -> {tgt:8s}  [{status}] {layer_str}  ({c475_note})")

    # Summary statistics
    n_total = len(coverage)
    n_covered = sum(1 for c in coverage if c['any_layer_blocks'])
    n_c475 = sum(1 for c in coverage if c['c475_blocked'])
    n_c911 = sum(1 for c in coverage if c['c911_blocked'])
    n_c1063 = sum(1 for c in coverage if c['c1063_blocked'])
    n_residual = n_total - n_covered

    print(f"\n  Coverage summary:")
    print(f"    C475 blocks:  {n_c475}/{n_total}")
    print(f"    C911 blocks:  {n_c911}/{n_total}")
    print(f"    C1063 blocks: {n_c1063}/{n_total}")
    print(f"    Any layer:    {n_covered}/{n_total}")
    print(f"    RESIDUAL:     {n_residual}/{n_total}")

    # Characterize residual (what the layers DON'T cover)
    residual_entries = [c for c in coverage if not c['any_layer_blocks']]
    residual_source_types = Counter(c['source_type'] for c in residual_entries)
    residual_target_types = Counter(c['target_type'] for c in residual_entries)

    # Check if residual involves specific MIDDLE pairs that ARE compatible in C475
    # (confirming C627: forbidden transitions operate above component compatibility)
    residual_compatible_in_c475 = sum(
        1 for c in residual_entries
        if c['c475_note'].startswith('compat=1')
    )

    print(f"\n  Residual characterization:")
    print(f"    Residual pairs compatible in C475: {residual_compatible_in_c475}/{n_residual}")
    print(f"    Source types: {dict(residual_source_types)}")
    print(f"    Target types: {dict(residual_target_types)}")

    # Verdict (reframed: low coverage = PASS confirming C627)
    coverage_rate = n_covered / n_total if n_total > 0 else 0
    if coverage_rate < 0.50 and n_residual > 0:
        verdict = "PASS"
        interpretation = f"Component layers cover only {n_covered}/{n_total} forbidden transitions. {residual_compatible_in_c475}/{n_residual} residual pairs are COMPATIBLE in C475, confirming C627: forbidden transitions are a token-specific directional mechanism operating above component-level rules."
    elif coverage_rate <= 0.80:
        verdict = "PARTIAL"
        interpretation = f"Moderate coverage ({n_covered}/{n_total}). Partial component-level explanation with residual."
    else:
        verdict = "FAIL"
        interpretation = f"High coverage ({n_covered}/{n_total}) contradicts C627 token-specific mechanism."

    print(f"\n  Verdict: {verdict}")
    print(f"  {interpretation}")

    result = {
        'test': 'T4_hazard_residual',
        'verdict': verdict,
        'interpretation': interpretation,
        'n_transitions': n_total,
        'n_covered': n_covered,
        'coverage_rate': round(coverage_rate, 4),
        'per_layer': {
            'c475': n_c475,
            'c911': n_c911,
            'c1063': n_c1063,
        },
        'n_residual': n_residual,
        'residual_compatible_in_c475': residual_compatible_in_c475,
        'residual_source_types': dict(residual_source_types),
        'residual_target_types': dict(residual_target_types),
        'coverage_detail': coverage,
        'constraints_referenced': ['C109', 'C475', 'C911', 'C1063', 'C627', 'C996', 'C1000'],
    }
    save_result(result, 't4_hazard_residual.json')
    return result


# ============================================================
# T5: TERMINAL CHARACTER x COMPATIBILITY
# ============================================================

def run_t5(compat_matrix, all_middles, mid_to_idx):
    """Test whether terminal character predicts C475 compatibility."""
    print("\n" + "=" * 60)
    print("T5: Terminal Character x Compatibility")
    print("    Tests C1067 positional bias extends to compatibility structure")
    print("=" * 60)

    n = len(all_middles)

    # Group MIDDLEs by terminal (last) character
    terminal_groups = defaultdict(list)
    for i, mid in enumerate(all_middles):
        if mid:
            terminal_groups[mid[-1]].append(i)

    # Overall baseline compatibility rate
    total_pairs = n * (n - 1) // 2
    total_compat = int(np.triu(compat_matrix, k=1).sum())
    baseline_rate = total_compat / total_pairs if total_pairs > 0 else 0
    print(f"  Overall baseline: {total_compat}/{total_pairs} = {baseline_rate:.4f}")

    # Compute degree for frequency control
    degrees = compat_matrix.sum(axis=1).astype(float)

    # Analyze each terminal character group
    group_results = []
    significant_groups = 0

    for char, indices in sorted(terminal_groups.items()):
        if len(indices) < 5:
            continue

        # Within-group compatibility
        idx_arr = np.array(indices)
        submatrix = compat_matrix[np.ix_(idx_arr, idx_arr)]
        group_n = len(indices)
        group_pairs = group_n * (group_n - 1) // 2
        if group_pairs == 0:
            continue
        group_compat = int(np.triu(submatrix, k=1).sum())
        group_rate = group_compat / group_pairs

        # Frequency control: expected within-group rate from degree-based null
        # Expected compatibility between node i and j ~ deg_i * deg_j / (2m)
        group_degrees = degrees[idx_arr]
        expected_compat = 0.0
        for a in range(group_n):
            for b in range(a + 1, group_n):
                expected_compat += group_degrees[a] * group_degrees[b] / max(degrees.sum(), 1)
        expected_rate = expected_compat / group_pairs if group_pairs > 0 else 0

        # Chi-squared test: observed vs expected (baseline rate)
        expected_compat_baseline = baseline_rate * group_pairs
        if expected_compat_baseline > 0:
            chi2_val = ((group_compat - expected_compat_baseline) ** 2) / expected_compat_baseline + \
                       (((group_pairs - group_compat) - (group_pairs - expected_compat_baseline)) ** 2) / max(group_pairs - expected_compat_baseline, 1)
            from scipy.stats import chi2
            p_val = 1 - chi2.cdf(chi2_val, 1) if group_compat > expected_compat_baseline else 1.0
        else:
            chi2_val = 0
            p_val = 1.0

        # Is it elevated above BOTH baseline and frequency-expected?
        elevated_vs_baseline = group_rate > 2 * baseline_rate
        elevated_vs_frequency = group_rate > expected_rate * 1.5 if expected_rate > 0 else False
        significant = elevated_vs_baseline and p_val < 0.01

        if significant:
            significant_groups += 1

        ratio_baseline = group_rate / baseline_rate if baseline_rate > 0 else 0
        ratio_frequency = group_rate / expected_rate if expected_rate > 0 else 0

        entry = {
            'terminal_char': char,
            'n_middles': group_n,
            'n_pairs': group_pairs,
            'n_compatible': group_compat,
            'within_rate': round(group_rate, 4),
            'baseline_rate': round(baseline_rate, 4),
            'frequency_expected_rate': round(expected_rate, 4),
            'ratio_vs_baseline': round(ratio_baseline, 2),
            'ratio_vs_frequency': round(ratio_frequency, 2),
            'chi2': round(chi2_val, 2),
            'p': p_val,
            'elevated_vs_baseline': elevated_vs_baseline,
            'elevated_vs_frequency': elevated_vs_frequency,
            'significant': significant,
        }
        group_results.append(entry)

        sig_str = " ***" if significant else ""
        print(f"  '{char}': {group_n} MIDDLEs, rate={group_rate:.4f} "
              f"(baseline x{ratio_baseline:.1f}, freq x{ratio_frequency:.1f}) "
              f"p={p_val:.4f}{sig_str}")

    # INITIAL vs FINAL terminal character comparison
    # C1067: INITIAL-biased = p (0.075), l (0.261), k (0.262)
    # C1067: FINAL-biased = c (0.599), i (0.465), d (0.397)
    initial_chars = {'p', 'l', 'k'}
    final_chars = {'c', 'i', 'd'}

    initial_results = [g for g in group_results if g['terminal_char'] in initial_chars]
    final_results = [g for g in group_results if g['terminal_char'] in final_chars]

    initial_mean_rate = np.mean([g['within_rate'] for g in initial_results]) if initial_results else 0
    final_mean_rate = np.mean([g['within_rate'] for g in final_results]) if final_results else 0

    print(f"\n  INITIAL-biased terminals (p, l, k): mean rate = {initial_mean_rate:.4f}")
    print(f"  FINAL-biased terminals (c, i, d): mean rate = {final_mean_rate:.4f}")

    # Verdict
    if significant_groups >= 3:
        verdict = "PASS"
    elif significant_groups >= 1:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n  Significant groups (>2x baseline, p<0.01): {significant_groups}")
    print(f"  Verdict: {verdict}")

    result = {
        'test': 'T5_terminal_compatibility',
        'verdict': verdict,
        'n_middles': n,
        'baseline_rate': round(baseline_rate, 4),
        'total_compatible_pairs': total_compat,
        'total_pairs': total_pairs,
        'n_terminal_groups_tested': len(group_results),
        'n_significant_groups': significant_groups,
        'group_results': sorted(group_results, key=lambda x: x['within_rate'], reverse=True),
        'positional_comparison': {
            'initial_biased_chars': list(initial_chars),
            'initial_mean_rate': round(initial_mean_rate, 4),
            'final_biased_chars': list(final_chars),
            'final_mean_rate': round(final_mean_rate, 4),
        },
        'constraints_referenced': ['C475', 'C1067', 'C985', 'C986'],
    }
    save_result(result, 't5_terminal_compatibility.json')
    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 381: Multi-Layer Compatibility Architecture")
    print("5-test battery | Tier 2 targets | Expert-validated")
    print("=" * 60)

    print("\nLoading data...")
    (compat_matrix, all_middles, mid_to_idx,
     c911_forbidden, c1063_forbidden, c109_transitions,
     kernel_profiles, c1065_asymmetric, c1067_terminal,
     b_tokens, morph) = load_data()

    t1 = run_t1(b_tokens, compat_matrix, all_middles, mid_to_idx, c911_forbidden, c1063_forbidden)
    t2 = run_t2(compat_matrix, all_middles, mid_to_idx, kernel_profiles)
    t3 = run_t3(c1065_asymmetric, kernel_profiles)
    t4 = run_t4(c109_transitions, compat_matrix, all_middles, mid_to_idx, c911_forbidden, c1063_forbidden, morph)
    t5 = run_t5(compat_matrix, all_middles, mid_to_idx)

    # Summary
    summary = {
        'phase': 381,
        'name': 'MULTI_LAYER_COMPATIBILITY_ARCHITECTURE',
        'description': '5-test battery: cross-layer independence, community structure, atom-kernel correlation, hazard residual, terminal-compatibility',
        'tier': 2,
        'tests': [
            {'id': 'T1', 'name': 'Cross-Layer Independence', 'verdict': t1['verdict']},
            {'id': 'T2', 'name': 'C475 Community Structure', 'verdict': t2['verdict']},
            {'id': 'T3', 'name': 'Atom Ordering x Kernel Profile', 'verdict': t3['verdict']},
            {'id': 'T4', 'name': 'Hazard Residual Characterization', 'verdict': t4['verdict']},
            {'id': 'T5', 'name': 'Terminal Character x Compatibility', 'verdict': t5['verdict']},
        ],
        'constraints_referenced': sorted(set(
            t1.get('constraints_referenced', []) +
            t2.get('constraints_referenced', []) +
            t3.get('constraints_referenced', []) +
            t4.get('constraints_referenced', []) +
            t5.get('constraints_referenced', [])
        )),
    }
    save_result(summary, 'multi_layer_compatibility_summary.json')

    print("\n" + "=" * 60)
    print("RESULTS:")
    for t in summary['tests']:
        print(f"  {t['id']}: {t['name']} -> {t['verdict']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
