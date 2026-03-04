"""
A Situation Description Language Tests
========================================

Probes whether Currier A functions as a declarative "situation description
language" — a registry describing WHAT things are, as opposed to B's procedural
instructions for what to DO.

Three predictions from the hypothesis that A encodes material/configuration states:

P6: RI complexity vs B coverage breadth
   - Records with MORE RI (specific) should have NARROWER B folio coverage
   - Records with MORE PP (generic) should have BROADER B folio coverage
   - Negative correlation between RI fraction and B coverage

P8: Within-folio operational compatibility
   - A records on the same folio should describe materials that are
     operationally compatible — their PP MIDDLEs should co-occur more often
     than records on different folios

P10: Terminal and HEAD positional concentration within records
   - l-terminal MIDDLEs should concentrate in MEDIAL positions (state description)
   - o-HEAD MIDDLEs should concentrate in INITIAL positions (arrangement frame)

Constraint grounding:
   C240 (A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY)
   C498 (RI = A-exclusive, PP = bridge vocabulary)
   C384 (No token-level A-B lookup)
   C502 (A-record viability filtering)
   C734 (A-B coverage architecture)
   C1040 (Folio-level paragraph compatibility coherence)
   C1041 (Paragraph complementary diversification)
   C1209 (MIDDLE positional grammar - atom slot syntax)
   C1388 (o-atom arrangement domain marker)
   C1385 (l-terminal state/condition marker)
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
from scipy import stats as sp_stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer, load_middle_classes

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000
random.seed(42)
np.random.seed(42)

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}  # a, e, o, k, t
# Hard-fused terminal: 'dy' counts as a single terminal unit
HARD_FUSED_TERMINALS = {'dy'}


def extract_head_atom(middle):
    """Extract HEAD atom from a MIDDLE. Returns (head, rest) or (None, middle)."""
    if not middle or len(middle) == 0:
        return None, middle
    first_char = middle[0]
    if first_char in HEAD_SET:
        # Check for extensible e: ee, eee, etc.
        if first_char == 'e':
            i = 0
            while i < len(middle) and middle[i] == 'e':
                i += 1
            return middle[:i], middle[i:]
        return first_char, middle[1:]
    return None, middle


def extract_terminal_atom(middle):
    """Extract TERMINAL atom from a MIDDLE. Returns (rest, terminal) or (middle, None)."""
    if not middle or len(middle) == 0:
        return middle, None
    # Check hard-fused terminals first
    for hf in HARD_FUSED_TERMINALS:
        if middle.endswith(hf) and len(middle) > len(hf):
            return middle[:-len(hf)], hf
    last_char = middle[-1]
    if last_char in (TERM_ONLY | FREE):
        return middle[:-1], last_char
    return middle, None


# ============================================================
# Data Loading
# ============================================================

def load_data():
    """Load all necessary data: A records, B MIDDLEs, RI/PP classification."""
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    ri_middles, pp_middles = load_middle_classes()

    # Gather all B MIDDLEs (set of MIDDLEs that appear in B grammar)
    b_middles_by_folio = defaultdict(set)  # folio -> set of MIDDLEs
    b_all_middles = set()
    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle:
            b_middles_by_folio[token.folio].add(m.middle)
            b_all_middles.add(m.middle)

    b_folios = sorted(b_middles_by_folio.keys())
    print(f"  B folios: {len(b_folios)}")
    print(f"  B unique MIDDLEs: {len(b_all_middles)}")

    # Gather A records: group tokens by (folio, line)
    a_records = defaultdict(list)  # (folio, line) -> [Token]
    a_folio_section = {}  # folio -> section
    for token in tx.currier_a():
        key = (token.folio, token.line)
        a_records[key].append(token)
        if token.folio not in a_folio_section:
            a_folio_section[token.folio] = token.section

    # Classify each A record
    records = []
    for (folio, line), tokens in sorted(a_records.items()):
        middles = []
        ri_mids = []
        pp_mids = []
        all_mids = []
        for t in tokens:
            m = morph.extract(t.word)
            if m.middle and m.middle != '_EMPTY_':
                mid = m.middle
                all_mids.append(mid)
                if mid in ri_middles:
                    ri_mids.append(mid)
                elif mid in pp_middles:
                    pp_mids.append(mid)
                # Also check if it's a bridge MIDDLE (appears in B)
                if mid in b_all_middles:
                    middles.append(mid)
        records.append({
            'folio': folio,
            'line': line,
            'section': a_folio_section.get(folio, '?'),
            'tokens': tokens,
            'all_middles': all_mids,
            'ri_middles': ri_mids,
            'pp_middles': pp_mids,
            'bridge_middles': middles,  # MIDDLEs that actually appear in B
            'n_tokens': len(tokens),
        })

    print(f"  A records: {len(records)}")
    print(f"  A folios: {len(set(r['folio'] for r in records))}")
    print(f"  RI MIDDLEs known: {len(ri_middles)}")
    print(f"  PP MIDDLEs known: {len(pp_middles)}")

    return records, b_middles_by_folio, b_folios, b_all_middles, ri_middles, pp_middles, morph


# ============================================================
# P6: RI Complexity vs B Coverage Breadth
# ============================================================

def test_p6(records, b_middles_by_folio, b_folios, b_all_middles):
    """
    P6: Records with more RI (specific) should have narrower B folio coverage.
    Records with more PP (generic) should have broader B folio coverage.
    """
    print("\n" + "="*70)
    print("P6: RI COMPLEXITY vs B COVERAGE BREADTH")
    print("="*70)

    # For each A record, compute:
    # 1. RI fraction = len(ri_middles) / len(all_middles)
    # 2. B folio coverage = number of B folios containing at least one of
    #    this record's bridge MIDDLEs
    data_points = []
    for rec in records:
        n_all = len(rec['all_middles'])
        if n_all == 0:
            continue
        n_ri = len(rec['ri_middles'])
        n_pp = len(rec['pp_middles'])
        ri_frac = n_ri / n_all

        # B folio coverage: how many of the B folios contain at least one
        # of this record's bridge MIDDLEs?
        bridge_set = set(rec['bridge_middles'])
        if len(bridge_set) == 0:
            b_coverage = 0
        else:
            b_coverage = sum(
                1 for bf in b_folios
                if bridge_set & b_middles_by_folio[bf]
            )

        data_points.append({
            'folio': rec['folio'],
            'line': rec['line'],
            'n_tokens': rec['n_tokens'],
            'n_all_middles': n_all,
            'n_ri': n_ri,
            'n_pp': n_pp,
            'n_bridge': len(bridge_set),
            'ri_fraction': ri_frac,
            'b_coverage': b_coverage,
            'b_coverage_frac': b_coverage / len(b_folios),
        })

    print(f"  Records with MIDDLEs: {len(data_points)}")

    ri_fracs = np.array([d['ri_fraction'] for d in data_points])
    b_covs = np.array([d['b_coverage'] for d in data_points])
    n_bridges = np.array([d['n_bridge'] for d in data_points])
    n_all = np.array([d['n_all_middles'] for d in data_points])

    # 1. Raw Spearman correlation
    rho_raw, p_raw = sp_stats.spearmanr(ri_fracs, b_covs)
    print(f"\n  Raw Spearman(RI_frac, B_coverage): rho={rho_raw:.4f}, p={p_raw:.4e}")

    # 2. Control for record length via partial correlation
    # Partial Spearman: rank-transform, then partial correlation
    rank_ri = sp_stats.rankdata(ri_fracs)
    rank_cov = sp_stats.rankdata(b_covs)
    rank_len = sp_stats.rankdata(n_all)

    # Residualize both on record length
    from numpy.polynomial.polynomial import polyfit
    # Use linear regression on ranks
    slope_ri, intercept_ri = np.polyfit(rank_len, rank_ri, 1)
    resid_ri = rank_ri - (slope_ri * rank_len + intercept_ri)
    slope_cov, intercept_cov = np.polyfit(rank_len, rank_cov, 1)
    resid_cov = rank_cov - (slope_cov * rank_len + intercept_cov)
    rho_partial, p_partial = sp_stats.spearmanr(resid_ri, resid_cov)
    print(f"  Partial Spearman (controlling record length): rho={rho_partial:.4f}, p={p_partial:.4e}")

    # 3. Also correlate n_bridge with b_coverage (sanity: more bridges = more coverage)
    rho_bridge, p_bridge = sp_stats.spearmanr(n_bridges, b_covs)
    print(f"  Spearman(n_bridge, B_coverage): rho={rho_bridge:.4f}, p={p_bridge:.4e}")

    # 4. Bin by RI fraction
    bins = [(0.0, 0.001, '0%'), (0.001, 0.26, '1-25%'), (0.26, 0.51, '26-50%'),
            (0.51, 0.76, '51-75%'), (0.76, 1.01, '76-100%')]
    bin_results = []
    for lo, hi, label in bins:
        mask = (ri_fracs >= lo) & (ri_fracs < hi)
        n = mask.sum()
        if n > 0:
            mean_cov = b_covs[mask].mean()
            mean_bridge = n_bridges[mask].mean()
            mean_len = n_all[mask].mean()
            bin_results.append({
                'bin': label,
                'n_records': int(n),
                'mean_b_coverage': round(float(mean_cov), 2),
                'mean_n_bridge': round(float(mean_bridge), 2),
                'mean_record_length': round(float(mean_len), 2),
            })
            print(f"  Bin {label}: n={n}, mean_B_cov={mean_cov:.1f}, mean_bridges={mean_bridge:.1f}, mean_len={mean_len:.1f}")

    # 5. Permutation test
    print("  Running permutation test (1000 shuffles)...")
    perm_rhos = []
    for _ in range(N_PERMUTATIONS):
        shuffled = np.random.permutation(b_covs)
        r, _ = sp_stats.spearmanr(ri_fracs, shuffled)
        perm_rhos.append(r)
    perm_rhos = np.array(perm_rhos)
    z_score = (rho_raw - perm_rhos.mean()) / (perm_rhos.std() + 1e-10)
    perm_p = np.mean(perm_rhos <= rho_raw)  # one-tailed: we expect NEGATIVE
    print(f"  Permutation z={z_score:.3f}, p(rho <= observed)={perm_p:.4f}")

    # Verdict
    is_negative = rho_raw < 0
    is_significant = p_raw < 0.05
    partial_negative = rho_partial < 0
    partial_significant = p_partial < 0.05

    if is_negative and is_significant and partial_negative and partial_significant:
        verdict = "CONFIRMED"
    elif is_negative and is_significant:
        verdict = "PARTIAL (confounded by record length)"
    elif is_negative:
        verdict = "WEAK (correct direction, not significant)"
    else:
        verdict = "FAILED (wrong direction or null)"

    print(f"\n  VERDICT: {verdict}")

    return {
        'test': 'P6_RI_complexity_vs_B_coverage',
        'prediction': 'Negative correlation: more RI = narrower B coverage',
        'n_records': len(data_points),
        'n_b_folios': len(b_folios),
        'raw_spearman_rho': round(rho_raw, 4),
        'raw_spearman_p': float(f'{p_raw:.4e}'),
        'partial_spearman_rho': round(rho_partial, 4),
        'partial_spearman_p': float(f'{p_partial:.4e}'),
        'bridge_coverage_rho': round(rho_bridge, 4),
        'bridge_coverage_p': float(f'{p_bridge:.4e}'),
        'permutation_z': round(z_score, 3),
        'permutation_p_one_tail': round(perm_p, 4),
        'bins': bin_results,
        'verdict': verdict,
    }


# ============================================================
# P8: Within-Folio Operational Compatibility
# ============================================================

def jaccard(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def test_p8(records):
    """
    P8: A records on the same folio should have more PP MIDDLE overlap
    (higher Jaccard) than records on different folios.
    """
    print("\n" + "="*70)
    print("P8: WITHIN-FOLIO OPERATIONAL COMPATIBILITY")
    print("="*70)

    # Build per-record PP MIDDLE sets, grouping by folio
    folio_records = defaultdict(list)
    for rec in records:
        pp_set = set(rec['pp_middles'])
        if len(pp_set) >= 1:  # Need at least 1 PP MIDDLE to compare
            folio_records[rec['folio']].append({
                'line': rec['line'],
                'pp_set': pp_set,
                'section': rec['section'],
            })

    # Filter to folios with 2+ records (need pairs)
    multi_folios = {f: recs for f, recs in folio_records.items() if len(recs) >= 2}
    print(f"  Folios with 2+ PP-bearing records: {len(multi_folios)}")
    print(f"  Total records in these folios: {sum(len(v) for v in multi_folios.values())}")

    # Compute within-folio pairwise Jaccard
    within_jaccards = []
    within_by_section = defaultdict(list)
    for folio, recs in multi_folios.items():
        section = recs[0]['section']
        for i in range(len(recs)):
            for j in range(i+1, len(recs)):
                j_val = jaccard(recs[i]['pp_set'], recs[j]['pp_set'])
                within_jaccards.append(j_val)
                within_by_section[section].append(j_val)

    # Compute between-folio pairwise Jaccard (sample to keep tractable)
    all_folio_keys = list(multi_folios.keys())
    between_jaccards = []
    n_between_samples = min(len(within_jaccards) * 3, 50000)
    for _ in range(n_between_samples):
        f1, f2 = random.sample(all_folio_keys, 2)
        r1 = random.choice(multi_folios[f1])
        r2 = random.choice(multi_folios[f2])
        j_val = jaccard(r1['pp_set'], r2['pp_set'])
        between_jaccards.append(j_val)

    within_arr = np.array(within_jaccards)
    between_arr = np.array(between_jaccards)

    within_mean = within_arr.mean()
    between_mean = between_arr.mean()
    ratio = within_mean / between_mean if between_mean > 0 else float('inf')

    print(f"\n  Within-folio Jaccard: mean={within_mean:.4f}, median={np.median(within_arr):.4f}, n={len(within_jaccards)}")
    print(f"  Between-folio Jaccard: mean={between_mean:.4f}, median={np.median(between_arr):.4f}, n={len(between_jaccards)}")
    print(f"  Ratio (within/between): {ratio:.3f}x")

    # Mann-Whitney U test
    u_stat, u_p = sp_stats.mannwhitneyu(within_arr, between_arr, alternative='greater')
    print(f"  Mann-Whitney U (within > between): U={u_stat:.0f}, p={u_p:.4e}")

    # Permutation test: shuffle records across folios
    print("  Running permutation test (1000 shuffles)...")
    all_records_flat = []
    folio_sizes = {}
    for folio, recs in multi_folios.items():
        folio_sizes[folio] = len(recs)
        for r in recs:
            all_records_flat.append(r)

    perm_ratios = []
    for _ in range(N_PERMUTATIONS):
        shuffled = list(all_records_flat)
        random.shuffle(shuffled)
        # Reassign to folios with original sizes
        idx = 0
        perm_within = []
        for folio in multi_folios:
            sz = folio_sizes[folio]
            group = shuffled[idx:idx+sz]
            idx += sz
            for i in range(len(group)):
                for j in range(i+1, len(group)):
                    perm_within.append(jaccard(group[i]['pp_set'], group[j]['pp_set']))
        if len(perm_within) > 0:
            perm_ratios.append(np.mean(perm_within))

    perm_ratios = np.array(perm_ratios)
    z_score = (within_mean - perm_ratios.mean()) / (perm_ratios.std() + 1e-10)
    perm_p = np.mean(perm_ratios >= within_mean)
    print(f"  Permutation: z={z_score:.3f}, p(perm >= observed)={perm_p:.4f}")
    print(f"  Permutation mean={perm_ratios.mean():.4f}, std={perm_ratios.std():.4f}")

    # Section breakdown
    section_results = {}
    for section, jacs in sorted(within_by_section.items()):
        sec_arr = np.array(jacs)
        section_results[section] = {
            'n_pairs': len(jacs),
            'mean_jaccard': round(float(sec_arr.mean()), 4),
            'median_jaccard': round(float(np.median(sec_arr)), 4),
        }
        print(f"  Section {section}: n={len(jacs)}, mean_Jaccard={sec_arr.mean():.4f}")

    # Verdict
    if within_mean > between_mean and u_p < 0.05 and z_score > 2.0:
        verdict = "CONFIRMED"
    elif within_mean > between_mean and (u_p < 0.05 or z_score > 1.96):
        verdict = "PARTIAL (significant by one test)"
    elif within_mean > between_mean:
        verdict = "WEAK (correct direction, not significant)"
    else:
        verdict = "FAILED (within <= between)"

    print(f"\n  VERDICT: {verdict}")

    return {
        'test': 'P8_within_folio_compatibility',
        'prediction': 'Within-folio PP Jaccard > between-folio PP Jaccard',
        'n_folios': len(multi_folios),
        'n_within_pairs': len(within_jaccards),
        'n_between_pairs': len(between_jaccards),
        'within_mean_jaccard': round(within_mean, 4),
        'between_mean_jaccard': round(between_mean, 4),
        'ratio': round(ratio, 3),
        'mann_whitney_U': round(float(u_stat), 1),
        'mann_whitney_p': float(f'{u_p:.4e}'),
        'permutation_z': round(z_score, 3),
        'permutation_p': round(perm_p, 4),
        'section_breakdown': section_results,
        'verdict': verdict,
    }


# ============================================================
# P10: Terminal and HEAD Positional Concentration
# ============================================================

def test_p10(records, morph):
    """
    P10: l-terminal MIDDLEs should concentrate in MEDIAL positions,
    o-HEAD MIDDLEs should concentrate in INITIAL positions within records.
    """
    print("\n" + "="*70)
    print("P10: TERMINAL AND HEAD POSITIONAL CONCENTRATION")
    print("="*70)

    # For multi-token records, compute normalized position of each token
    # and extract HEAD and TERMINAL atoms
    head_positions = defaultdict(list)   # head_type -> [norm_positions]
    term_positions = defaultdict(list)   # term_type -> [norm_positions]
    headless_positions = []
    n_records_used = 0
    n_tokens_used = 0

    for rec in records:
        n = rec['n_tokens']
        if n < 3:  # Need at least 3 tokens for initial/medial/final distinction
            continue
        n_records_used += 1

        for idx, tok in enumerate(rec['tokens']):
            m = morph.extract(tok.word)
            if not m.middle or m.middle == '_EMPTY_':
                continue

            norm_pos = idx / (n - 1)  # 0=first, 1=last
            mid = m.middle
            n_tokens_used += 1

            head, rest = extract_head_atom(mid)
            _, terminal = extract_terminal_atom(mid)

            if head:
                head_type = head[0] if head[0] in HEAD_SET else head
                head_positions[head_type].append(norm_pos)
            else:
                headless_positions.append(norm_pos)
                head_positions['NONE'].append(norm_pos)

            if terminal:
                term_positions[terminal].append(norm_pos)
            else:
                term_positions['NONE'].append(norm_pos)

    print(f"  Records used (3+ tokens): {n_records_used}")
    print(f"  Tokens analyzed: {n_tokens_used}")

    # --- HEAD atom positional analysis ---
    print("\n  HEAD atom mean positions (0=first, 1=last):")
    head_results = {}
    for h_type in sorted(head_positions.keys()):
        positions = np.array(head_positions[h_type])
        mean_pos = positions.mean()
        std_pos = positions.std()
        n = len(positions)
        # Fraction in first position (norm_pos < 0.1)
        frac_initial = (positions < 0.15).mean()
        # Fraction in medial (0.25 < pos < 0.75)
        frac_medial = ((positions >= 0.25) & (positions <= 0.75)).mean()
        # Fraction in final (pos > 0.85)
        frac_final = (positions > 0.85).mean()
        head_results[h_type] = {
            'n': int(n),
            'mean_pos': round(float(mean_pos), 4),
            'std_pos': round(float(std_pos), 4),
            'frac_initial': round(float(frac_initial), 4),
            'frac_medial': round(float(frac_medial), 4),
            'frac_final': round(float(frac_final), 4),
        }
        print(f"    {h_type:6s}: n={n:5d}, mean={mean_pos:.3f}, "
              f"initial={frac_initial:.3f}, medial={frac_medial:.3f}, final={frac_final:.3f}")

    # --- TERMINAL atom positional analysis ---
    print("\n  TERMINAL atom mean positions:")
    term_results = {}
    for t_type in sorted(term_positions.keys()):
        positions = np.array(term_positions[t_type])
        mean_pos = positions.mean()
        std_pos = positions.std()
        n = len(positions)
        frac_initial = (positions < 0.15).mean()
        frac_medial = ((positions >= 0.25) & (positions <= 0.75)).mean()
        frac_final = (positions > 0.85).mean()
        term_results[t_type] = {
            'n': int(n),
            'mean_pos': round(float(mean_pos), 4),
            'std_pos': round(float(std_pos), 4),
            'frac_initial': round(float(frac_initial), 4),
            'frac_medial': round(float(frac_medial), 4),
            'frac_final': round(float(frac_final), 4),
        }
        print(f"    {t_type:6s}: n={n:5d}, mean={mean_pos:.3f}, "
              f"initial={frac_initial:.3f}, medial={frac_medial:.3f}, final={frac_final:.3f}")

    # --- Key tests ---
    # Test 1: Is o-HEAD more initial than other HEADs?
    o_pos = np.array(head_positions.get('o', []))
    non_o_heads = []
    for h in HEAD_SET:
        if h != 'o' and h in head_positions:
            non_o_heads.extend(head_positions[h])
    non_o_pos = np.array(non_o_heads)

    if len(o_pos) > 0 and len(non_o_pos) > 0:
        u_o, p_o = sp_stats.mannwhitneyu(o_pos, non_o_pos, alternative='less')
        o_initial_frac = (o_pos < 0.15).mean()
        non_o_initial_frac = (non_o_pos < 0.15).mean()
        print(f"\n  o-HEAD vs other HEADs:")
        print(f"    o mean pos={o_pos.mean():.3f}, initial frac={o_initial_frac:.3f}")
        print(f"    non-o mean pos={non_o_pos.mean():.3f}, initial frac={non_o_initial_frac:.3f}")
        print(f"    Mann-Whitney (o < non-o): U={u_o:.0f}, p={p_o:.4e}")
        o_test = {
            'o_mean_pos': round(float(o_pos.mean()), 4),
            'non_o_mean_pos': round(float(non_o_pos.mean()), 4),
            'o_initial_frac': round(float(o_initial_frac), 4),
            'non_o_initial_frac': round(float(non_o_initial_frac), 4),
            'mann_whitney_U': round(float(u_o), 1),
            'mann_whitney_p': float(f'{p_o:.4e}'),
            'o_is_more_initial': bool(o_pos.mean() < non_o_pos.mean()),
        }
    else:
        o_test = {'error': 'insufficient data'}
        p_o = 1.0

    # Test 2: Is l-terminal more medial than other terminals?
    l_pos = np.array(term_positions.get('l', []))
    non_l_terms = []
    for t in TERM_ONLY:
        if t != 'l' and t in term_positions:
            non_l_terms.extend(term_positions[t])
    non_l_pos = np.array(non_l_terms)

    if len(l_pos) > 0 and len(non_l_pos) > 0:
        # l should be more medial = closer to 0.5
        l_dev = np.abs(l_pos - 0.5)
        non_l_dev = np.abs(non_l_pos - 0.5)
        u_l, p_l = sp_stats.mannwhitneyu(l_dev, non_l_dev, alternative='less')
        l_medial_frac = ((l_pos >= 0.25) & (l_pos <= 0.75)).mean()
        non_l_medial_frac = ((non_l_pos >= 0.25) & (non_l_pos <= 0.75)).mean()
        print(f"\n  l-terminal vs other terminals:")
        print(f"    l mean pos={l_pos.mean():.3f}, medial frac={l_medial_frac:.3f}")
        print(f"    non-l mean pos={non_l_pos.mean():.3f}, medial frac={non_l_medial_frac:.3f}")
        print(f"    Mann-Whitney (l closer to 0.5 than non-l): U={u_l:.0f}, p={p_l:.4e}")
        l_test = {
            'l_mean_pos': round(float(l_pos.mean()), 4),
            'non_l_mean_pos': round(float(non_l_pos.mean()), 4),
            'l_medial_frac': round(float(l_medial_frac), 4),
            'non_l_medial_frac': round(float(non_l_medial_frac), 4),
            'mann_whitney_U': round(float(u_l), 1),
            'mann_whitney_p': float(f'{p_l:.4e}'),
            'l_is_more_medial': bool(l_medial_frac > non_l_medial_frac),
        }
    else:
        l_test = {'error': 'insufficient data'}
        p_l = 1.0

    # Test 3: Is headless-MIDDLE more final than headed-MIDDLE?
    # (headless = no HEAD atom = modifiers/terminals only = identity tokens)
    none_pos = np.array(head_positions.get('NONE', []))
    headed_pos_all = []
    for h in HEAD_SET:
        if h in head_positions:
            headed_pos_all.extend(head_positions[h])
    headed_pos = np.array(headed_pos_all)

    if len(none_pos) > 0 and len(headed_pos) > 0:
        u_h, p_h = sp_stats.mannwhitneyu(none_pos, headed_pos, alternative='greater')
        none_final_frac = (none_pos > 0.85).mean()
        headed_final_frac = (headed_pos > 0.85).mean()
        print(f"\n  Headless vs headed MIDDLEs:")
        print(f"    headless mean pos={none_pos.mean():.3f}, final frac={none_final_frac:.3f}")
        print(f"    headed mean pos={headed_pos.mean():.3f}, final frac={headed_final_frac:.3f}")
        print(f"    Mann-Whitney (headless > headed): U={u_h:.0f}, p={p_h:.4e}")
        headless_test = {
            'headless_mean_pos': round(float(none_pos.mean()), 4),
            'headed_mean_pos': round(float(headed_pos.mean()), 4),
            'headless_final_frac': round(float(none_final_frac), 4),
            'headed_final_frac': round(float(headed_final_frac), 4),
            'mann_whitney_U': round(float(u_h), 1),
            'mann_whitney_p': float(f'{p_h:.4e}'),
            'headless_is_more_final': bool(none_pos.mean() > headed_pos.mean()),
        }
    else:
        headless_test = {'error': 'insufficient data'}
        p_h = 1.0

    # --- Permutation test for o-HEAD initial concentration ---
    print("\n  Permutation test for o-HEAD initial bias (1000 shuffles)...")
    real_o_mean = float(o_pos.mean()) if len(o_pos) > 0 else 0.5
    perm_o_means = []
    # For each record, shuffle token positions
    for _ in range(N_PERMUTATIONS):
        perm_o_pos = []
        for rec in records:
            n = rec['n_tokens']
            if n < 3:
                continue
            positions = list(range(n))
            random.shuffle(positions)
            for idx, tok in enumerate(rec['tokens']):
                m = morph.extract(tok.word)
                if not m.middle or m.middle == '_EMPTY_':
                    continue
                head, _ = extract_head_atom(m.middle)
                if head and head[0] == 'o':
                    norm_pos = positions[idx] / (n - 1)
                    perm_o_pos.append(norm_pos)
        if perm_o_pos:
            perm_o_means.append(np.mean(perm_o_pos))

    perm_o_arr = np.array(perm_o_means)
    o_z = (real_o_mean - perm_o_arr.mean()) / (perm_o_arr.std() + 1e-10)
    o_perm_p = np.mean(perm_o_arr <= real_o_mean)  # one-tailed: expect o to be EARLIER
    print(f"  Permutation: z={o_z:.3f}, p(perm <= observed)={o_perm_p:.4f}")
    print(f"  Observed o mean={real_o_mean:.4f}, permuted mean={perm_o_arr.mean():.4f}")

    # Verdict
    o_confirmed = (o_test.get('o_is_more_initial', False) and
                   float(o_test.get('mann_whitney_p', 1)) < 0.05)
    l_confirmed = (l_test.get('l_is_more_medial', False) and
                   float(l_test.get('mann_whitney_p', 1)) < 0.05)
    headless_confirmed = (headless_test.get('headless_is_more_final', False) and
                          float(headless_test.get('mann_whitney_p', 1)) < 0.05)

    n_pass = sum([o_confirmed, l_confirmed, headless_confirmed])
    if n_pass >= 2:
        verdict = "CONFIRMED" if n_pass == 3 else "PARTIAL (2/3 sub-tests)"
    elif n_pass == 1:
        verdict = "WEAK (1/3 sub-tests)"
    else:
        verdict = "FAILED (0/3 sub-tests)"

    print(f"\n  Sub-tests: o-initial={'PASS' if o_confirmed else 'FAIL'}, "
          f"l-medial={'PASS' if l_confirmed else 'FAIL'}, "
          f"headless-final={'PASS' if headless_confirmed else 'FAIL'}")
    print(f"  VERDICT: {verdict}")

    return {
        'test': 'P10_terminal_head_positional_concentration',
        'prediction': 'o-HEAD initial, l-terminal medial, headless final',
        'n_records': n_records_used,
        'n_tokens': n_tokens_used,
        'head_positions': head_results,
        'terminal_positions': term_results,
        'o_head_test': o_test,
        'l_terminal_test': l_test,
        'headless_test': headless_test,
        'o_permutation_z': round(o_z, 3),
        'o_permutation_p': round(o_perm_p, 4),
        'sub_tests_passed': n_pass,
        'verdict': verdict,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("A Situation Description Language Tests")
    print("="*70)

    records, b_middles_by_folio, b_folios, b_all_middles, ri_middles, pp_middles, morph = load_data()

    # Run tests
    p6_result = test_p6(records, b_middles_by_folio, b_folios, b_all_middles)
    p8_result = test_p8(records)
    p10_result = test_p10(records, morph)

    # Overall summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    verdicts = [p6_result['verdict'], p8_result['verdict'], p10_result['verdict']]
    confirmed = sum(1 for v in verdicts if v.startswith('CONFIRMED'))
    partial = sum(1 for v in verdicts if v.startswith('PARTIAL'))
    failed = sum(1 for v in verdicts if v.startswith('FAILED'))

    print(f"  P6  (RI complexity vs B coverage): {p6_result['verdict']}")
    print(f"  P8  (within-folio compatibility):   {p8_result['verdict']}")
    print(f"  P10 (positional concentration):     {p10_result['verdict']}")
    print(f"\n  Confirmed: {confirmed}/3, Partial: {partial}/3, Failed: {failed}/3")

    if confirmed >= 2:
        overall = "STRONG SUPPORT for situation description hypothesis"
    elif confirmed + partial >= 2:
        overall = "MODERATE SUPPORT for situation description hypothesis"
    elif confirmed + partial >= 1:
        overall = "WEAK SUPPORT for situation description hypothesis"
    else:
        overall = "NOT SUPPORTED"
    print(f"  Overall: {overall}")

    # Save results
    results = {
        'meta': {
            'description': 'A Situation Description Language Tests',
            'n_permutations': N_PERMUTATIONS,
            'overall_verdict': overall,
            'verdicts': {
                'P6': p6_result['verdict'],
                'P8': p8_result['verdict'],
                'P10': p10_result['verdict'],
            },
            'counts': {
                'confirmed': confirmed,
                'partial': partial,
                'failed': failed,
            }
        },
        'P6': p6_result,
        'P8': p8_result,
        'P10': p10_result,
    }

    out_path = RESULTS_DIR / 'a_situation_description_tests.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
