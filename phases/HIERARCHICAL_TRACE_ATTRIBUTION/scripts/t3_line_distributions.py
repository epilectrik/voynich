"""
Phase 561 T3: Line-Level Compositional Distributions

Tests whether line-level compositional distributions carry folio-specific
information that folio-averaging missed.

Method:
    A. Extract 15-dimensional line profiles for lines with >= 5 tokens
    B. Within-section distributional tests:
        B1: Variance ratio (within-folio vs within-section)
        B2: Energy distance with permutation null (line-shuffle within section)

Overall T3 PASS: >= 1/2 sub-tests pass.
"""

import json
import math
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
from scipy.spatial.distance import cdist
import os
import time

# Paths
CORPUS_PATH = os.path.join(os.path.dirname(__file__), '..', '..',
    'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL', 'results', 't1_domain_decomposition.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 't3_line_distributions.json')

DOMAIN_NAMES = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
TEST_SECTIONS = ['S', 'H', 'B']
N_PERMS = 300
RNG_SEED = 42

# C1563 routing enrichment map
ROUTING_MAP = {'r': 'ACTIVE', 'y': 'THERMAL', 'h': 'FLOW', 'm': 'ARRANGEMENT'}

FEATURE_NAMES = [
    'k_frac', 't_frac', 'a_frac', 'e_frac', 'o_frac', 'hl_frac',
    'hazard_high_frac', 'hazard_zero_frac',
    'q4_shift', 'close_m_rate', 'safe_pathway_frac',
    'k_q1_peak', 'q0q4_hazard_slope', 'routing_match_rate', 'q4_opaque_rate'
]


def load_corpus():
    with open(CORPUS_PATH) as f:
        data = json.load(f)
    return data['corpus_tokens']


def compute_domain_fracs(tokens):
    """Compute 6-element domain fraction vector from a list of tokens."""
    domain_counts = Counter(t['domain'] for t in tokens)
    total = len(tokens)
    if total == 0:
        return np.full(6, np.nan)
    return np.array([domain_counts.get(d, 0) / total for d in DOMAIN_NAMES])


def compute_line_profile(tokens):
    """Compute the 15-dimensional profile for a single line.

    Args:
        tokens: list of token dicts for this line (already filtered to >= 5)

    Returns:
        np.array of 15 features (may contain NaN for undefined features)
    """
    n = len(tokens)
    profile = np.full(15, np.nan)

    # --- Domain fractions (features 0-5) ---
    domain_fracs = compute_domain_fracs(tokens)
    profile[0] = domain_fracs[0]  # k_frac (THERMAL)
    profile[1] = domain_fracs[1]  # t_frac (FLOW)
    profile[2] = domain_fracs[2]  # a_frac (ACTIVE)
    profile[3] = domain_fracs[3]  # e_frac (STABILITY)
    profile[4] = domain_fracs[4]  # o_frac (ARRANGEMENT)
    profile[5] = domain_fracs[5]  # hl_frac (HEADLESS)

    # --- Hazard fractions (features 6-7), excluding IMMUNE ---
    non_immune = [t for t in tokens if t.get('frame_hazard') != 'IMMUNE']
    if len(non_immune) > 0:
        n_ni = len(non_immune)
        profile[6] = sum(1 for t in non_immune if t['frame_hazard'] == 'HIGH') / n_ni
        profile[7] = sum(1 for t in non_immune if t['frame_hazard'] == 'ZERO') / n_ni
    # else: remain NaN

    # --- q4_shift (feature 8) ---
    # Euclidean distance between Q4 domain distribution and mean(Q1,Q2,Q3) distribution
    q_groups = defaultdict(list)
    for t in tokens:
        q = t.get('quintile')
        if q is not None:
            q_groups[q].append(t)

    q4_tokens = q_groups.get(4, [])
    q123_tokens = []
    for qi in [0, 1, 2, 3]:  # Q1-Q3 means quintiles 0,1,2,3 (non-Q4)
        q123_tokens.extend(q_groups.get(qi, []))

    if len(q4_tokens) > 0 and len(q123_tokens) > 0:
        q4_dist = compute_domain_fracs(q4_tokens)
        q123_dist = compute_domain_fracs(q123_tokens)
        profile[8] = np.linalg.norm(q4_dist - q123_dist)
    # else: NaN

    # --- close_m_rate (feature 9) ---
    # Fraction of tokens at quintile=4 with prev_term_same_line == 'm'
    if len(q4_tokens) > 0:
        m_count = sum(1 for t in q4_tokens if t.get('prev_term_same_line') == 'm')
        profile[9] = m_count / len(q4_tokens)
    else:
        profile[9] = 0.0  # spec says use 0 if no Q4 tokens

    # --- safe_pathway_frac (feature 10) ---
    profile[10] = sum(1 for t in tokens if t.get('is_safe_pathway')) / n

    # --- k_q1_peak (feature 11) ---
    # THERMAL fraction at quintile=0 minus mean THERMAL frac at quintiles 1-4
    q0_tokens = q_groups.get(0, [])
    q1234_tokens = []
    for qi in [1, 2, 3, 4]:
        q1234_tokens.extend(q_groups.get(qi, []))

    if len(q0_tokens) > 0 and len(q1234_tokens) > 0:
        q0_k_frac = sum(1 for t in q0_tokens if t['domain'] == 'THERMAL') / len(q0_tokens)
        q1234_k_frac = sum(1 for t in q1234_tokens if t['domain'] == 'THERMAL') / len(q1234_tokens)
        profile[11] = q0_k_frac - q1234_k_frac
    # else: NaN

    # --- q0q4_hazard_slope (feature 12) ---
    # HIGH hazard frac at Q4 minus ZERO hazard frac at Q0, non-IMMUNE only
    q4_ni = [t for t in q4_tokens if t.get('frame_hazard') != 'IMMUNE']
    q0_ni = [t for t in q0_tokens if t.get('frame_hazard') != 'IMMUNE']

    if len(q4_ni) > 0 and len(q0_ni) > 0:
        q4_high_frac = sum(1 for t in q4_ni if t['frame_hazard'] == 'HIGH') / len(q4_ni)
        q0_zero_frac = sum(1 for t in q0_ni if t['frame_hazard'] == 'ZERO') / len(q0_ni)
        profile[12] = q4_high_frac - q0_zero_frac
    # else: NaN

    # --- routing_match_rate (feature 13) ---
    # Fraction of within-line adjacencies matching C1563 enrichments
    eligible = [t for t in tokens if t.get('prev_term_same_line') in ROUTING_MAP]
    if len(eligible) > 0:
        matches = sum(1 for t in eligible if t['domain'] == ROUTING_MAP[t['prev_term_same_line']])
        profile[13] = matches / len(eligible)
    # else: NaN

    # --- q4_opaque_rate (feature 14) ---
    # OPAQUE terminal_opacity fraction at Q4 (non-null opacity only)
    q4_with_opacity = [t for t in q4_tokens if t.get('terminal_opacity') is not None]
    if len(q4_with_opacity) > 0:
        profile[14] = sum(1 for t in q4_with_opacity if t['terminal_opacity'] == 'OPAQUE') / len(q4_with_opacity)
    # else: NaN

    return profile


def extract_line_profiles(tokens):
    """Extract profiles for all qualifying lines (>= 5 tokens).

    Returns:
        lines: list of dicts with keys: folio, section, paragraph_idx, line, profile (np.array)
        line_keys: list of (folio, paragraph_idx, line) tuples
    """
    # Group tokens by (folio, paragraph_idx, line)
    line_groups = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['paragraph_idx'], t['line'])
        line_groups[key].append(t)

    lines = []
    for key, toks in line_groups.items():
        if len(toks) < 5:
            continue
        profile = compute_line_profile(toks)
        lines.append({
            'folio': key[0],
            'section': toks[0]['section'],
            'paragraph_idx': key[1],
            'line': key[2],
            'n_tokens': len(toks),
            'profile': profile
        })

    return lines


def test_b1_variance_ratio(lines):
    """B1: Variance Ratio Test.

    For each line feature, compute:
        - Within-folio variance: mean variance of the feature across lines within each folio
        - Within-section variance: variance across all lines in the section
        - Ratio = within-folio / within-section

    PASS: ratio < 0.90 for >= 4/15 features across >= 2/3 sections.
    """
    print("\n--- B1: Variance Ratio ---")

    results = {}

    for section in TEST_SECTIONS:
        sec_lines = [l for l in lines if l['section'] == section]
        if len(sec_lines) < 10:
            results[section] = {'status': 'SKIP', 'reason': f'too few lines ({len(sec_lines)})'}
            print(f"  {section}: SKIP (too few lines: {len(sec_lines)})")
            continue

        # Build profile matrix: (n_lines, 15)
        profiles = np.array([l['profile'] for l in sec_lines])
        folios = [l['folio'] for l in sec_lines]

        # Group by folio
        folio_indices = defaultdict(list)
        for i, f in enumerate(folios):
            folio_indices[f].append(i)

        # Keep folios with >= 2 lines
        valid_folios = {f: idx for f, idx in folio_indices.items() if len(idx) >= 2}

        if len(valid_folios) < 3:
            results[section] = {'status': 'SKIP', 'reason': f'too few folios with >=2 lines ({len(valid_folios)})'}
            print(f"  {section}: SKIP (too few folios with >=2 lines: {len(valid_folios)})")
            continue

        feature_results = {}
        n_below_threshold = 0

        for fi, fname in enumerate(FEATURE_NAMES):
            col = profiles[:, fi]

            # Check NaN rate
            nan_mask = np.isnan(col)
            nan_rate = nan_mask.sum() / len(col)
            if nan_rate > 0.5:
                feature_results[fname] = {'status': 'SKIP', 'reason': f'NaN rate {nan_rate:.2f} > 0.50'}
                continue

            # Within-section variance (all non-NaN values)
            valid_col = col[~nan_mask]
            if len(valid_col) < 3:
                feature_results[fname] = {'status': 'SKIP', 'reason': 'too few valid values'}
                continue

            section_var = np.var(valid_col, ddof=0)

            if section_var < 1e-15:
                feature_results[fname] = {'status': 'SKIP', 'reason': 'zero section variance'}
                continue

            # Within-folio variance: for each folio, compute variance of the feature
            # across its lines, then take the mean across folios
            folio_variances = []
            for f, idx in valid_folios.items():
                folio_vals = col[idx]
                folio_valid = folio_vals[~np.isnan(folio_vals)]
                if len(folio_valid) >= 2:
                    folio_variances.append(np.var(folio_valid, ddof=0))

            if len(folio_variances) < 3:
                feature_results[fname] = {'status': 'SKIP', 'reason': 'too few folios with valid variance'}
                continue

            within_folio_var = np.mean(folio_variances)
            ratio = within_folio_var / section_var

            passes = ratio < 0.90
            if passes:
                n_below_threshold += 1

            feature_results[fname] = {
                'status': 'TESTED',
                'within_folio_var': round(float(within_folio_var), 6),
                'section_var': round(float(section_var), 6),
                'ratio': round(float(ratio), 4),
                'pass': passes,
                'n_folios_used': len(folio_variances)
            }

        tested_count = sum(1 for v in feature_results.values() if v.get('status') == 'TESTED')
        results[section] = {
            'status': 'TESTED',
            'n_lines': len(sec_lines),
            'n_folios': len(valid_folios),
            'features': feature_results,
            'n_features_below_090': n_below_threshold,
            'n_features_tested': tested_count,
            'pass': n_below_threshold >= 4
        }

        print(f"  {section}: {n_below_threshold}/{tested_count} features with ratio < 0.90 "
              f"({'PASS' if n_below_threshold >= 4 else 'FAIL'})")
        for fname, fr in feature_results.items():
            if fr.get('status') == 'TESTED':
                print(f"    {fname}: ratio={fr['ratio']:.4f} {'*' if fr['pass'] else ''}")

    # Overall B1 pass: ratio < 0.90 for >= 4 features in >= 2/3 sections
    sections_passing = sum(1 for v in results.values() if v.get('pass', False))
    overall_pass = sections_passing >= 2

    print(f"  B1 overall: {sections_passing}/3 sections pass -> {'PASS' if overall_pass else 'FAIL'}")

    return {
        'per_section': results,
        'sections_passing': sections_passing,
        'pass': overall_pass
    }


def energy_distance(A, B):
    """Multivariate energy distance between two point clouds.

    E = (2/nm)*sum||a_i-b_j|| - (1/n^2)*sum||a_i-a_j'|| - (1/m^2)*sum||b_i-b_j'||

    Handles NaN by using nanmean imputation per-feature before distance computation.
    """
    A = np.array(A, dtype=np.float64)
    B = np.array(B, dtype=np.float64)
    n, m = len(A), len(B)

    if n < 2 or m < 2:
        return np.nan

    # Impute NaN with column means from the combined set
    combined = np.vstack([A, B])
    col_means = np.nanmean(combined, axis=0)
    for c in range(combined.shape[1]):
        if np.isnan(col_means[c]):
            col_means[c] = 0.0

    A_imp = A.copy()
    B_imp = B.copy()
    for c in range(A_imp.shape[1]):
        A_imp[np.isnan(A_imp[:, c]), c] = col_means[c]
        B_imp[np.isnan(B_imp[:, c]), c] = col_means[c]

    # Vectorized pairwise distance computation via cdist
    cross = 2.0 * cdist(A_imp, B_imp, 'euclidean').sum() / (n * m)
    within_a = cdist(A_imp, A_imp, 'euclidean').sum() / (n * n)
    within_b = cdist(B_imp, B_imp, 'euclidean').sum() / (m * m)

    return cross - within_a - within_b


def test_b2_energy_distance(lines, rng):
    """B2: Energy Distance Test with permutation null.

    For each pair of folios within a section, compute energy distance between
    their line profile clouds. Compare to line-shuffle-within-section null
    (300 permutations). Bonferroni correction on number of pairs.

    PASS: >15% of within-section folio pairs show significant difference
    (permutation p < 0.05, Bonferroni-corrected).
    """
    print(f"\n--- B2: Energy Distance Test ({N_PERMS} permutations) ---")

    results = {}

    for section in TEST_SECTIONS:
        t_sec_start = time.time()
        sec_lines = [l for l in lines if l['section'] == section]

        if len(sec_lines) < 10:
            results[section] = {'status': 'SKIP', 'reason': f'too few lines ({len(sec_lines)})'}
            print(f"  {section}: SKIP (too few lines)")
            continue

        # Group by folio
        folio_profiles = defaultdict(list)
        for l in sec_lines:
            folio_profiles[l['folio']].append(l['profile'])

        # Keep folios with >= 3 lines (need enough for meaningful cloud distance)
        valid_folios = {f: np.array(profs) for f, profs in folio_profiles.items() if len(profs) >= 3}

        if len(valid_folios) < 3:
            results[section] = {'status': 'SKIP', 'reason': f'too few folios with >=3 lines ({len(valid_folios)})'}
            print(f"  {section}: SKIP (too few folios)")
            continue

        folio_list = sorted(valid_folios.keys())
        n_folios = len(folio_list)
        pairs = list(combinations(range(n_folios), 2))
        n_pairs = len(pairs)

        # Bonferroni-corrected significance threshold
        alpha_bonf = 0.05 / n_pairs

        # Compute real pairwise energy distances
        real_dists = {}
        for i, j in pairs:
            ed = energy_distance(valid_folios[folio_list[i]], valid_folios[folio_list[j]])
            real_dists[(i, j)] = ed

        # Build flat array of all profiles and folio-size mapping for shuffling
        all_profiles = []
        folio_sizes = []
        for f in folio_list:
            all_profiles.append(valid_folios[f])
            folio_sizes.append(len(valid_folios[f]))
        all_profiles_flat = np.vstack(all_profiles)
        n_total = len(all_profiles_flat)

        # Permutation null: reassign lines to folios within section, preserving counts
        # For each permutation, compute all pairwise energy distances
        # Per-pair p-value = fraction of null where null_distance >= real_distance
        null_exceedance = {pair: 0 for pair in pairs}

        for perm_i in range(N_PERMS):
            if perm_i % 50 == 0:
                print(f"    {section} permutation {perm_i}/{N_PERMS}...", flush=True)
            perm = rng.permutation(n_total)
            shuffled = all_profiles_flat[perm]

            # Reconstruct folio groupings
            null_folios = {}
            idx = 0
            for fi, f in enumerate(folio_list):
                null_folios[fi] = shuffled[idx:idx + folio_sizes[fi]]
                idx += folio_sizes[fi]

            for i, j in pairs:
                null_ed = energy_distance(null_folios[i], null_folios[j])
                if not np.isnan(null_ed) and not np.isnan(real_dists[(i, j)]):
                    if null_ed >= real_dists[(i, j)]:
                        null_exceedance[(i, j)] += 1

        # Compute per-pair p-values
        pair_results = []
        n_significant = 0
        for i, j in pairs:
            p_raw = null_exceedance[(i, j)] / N_PERMS
            significant = p_raw < alpha_bonf
            if significant:
                n_significant += 1
            pair_results.append({
                'folio_a': folio_list[i],
                'folio_b': folio_list[j],
                'energy_distance': round(float(real_dists[(i, j)]), 6) if not np.isnan(real_dists[(i, j)]) else None,
                'p_value': round(float(p_raw), 4),
                'significant': significant
            })

        sig_frac = n_significant / n_pairs if n_pairs > 0 else 0
        section_pass = sig_frac > 0.15

        elapsed_sec = time.time() - t_sec_start
        results[section] = {
            'status': 'TESTED',
            'n_lines': len(sec_lines),
            'n_folios': n_folios,
            'n_pairs': n_pairs,
            'n_significant': n_significant,
            'significant_fraction': round(float(sig_frac), 4),
            'alpha_bonferroni': round(float(alpha_bonf), 6),
            'pass': section_pass,
            'elapsed_seconds': round(elapsed_sec, 1),
            'pair_details': pair_results
        }

        print(f"  {section}: {n_significant}/{n_pairs} pairs significant "
              f"({sig_frac:.1%}), alpha_bonf={alpha_bonf:.4f} "
              f"({'PASS' if section_pass else 'FAIL'}) [{elapsed_sec:.1f}s]")

    # Overall B2 pass: any section passes
    # (spec says >15% of within-section folio pairs across the test)
    # Interpret as: aggregate across all tested sections
    total_pairs = 0
    total_sig = 0
    for sec, res in results.items():
        if res.get('status') == 'TESTED':
            total_pairs += res['n_pairs']
            total_sig += res['n_significant']

    aggregate_frac = total_sig / total_pairs if total_pairs > 0 else 0
    overall_pass = aggregate_frac > 0.15

    print(f"  B2 aggregate: {total_sig}/{total_pairs} pairs significant "
          f"({aggregate_frac:.1%}) -> {'PASS' if overall_pass else 'FAIL'}")

    return {
        'per_section': results,
        'aggregate_significant': total_sig,
        'aggregate_pairs': total_pairs,
        'aggregate_fraction': round(float(aggregate_frac), 4),
        'pass': overall_pass
    }


def main():
    t_start = time.time()
    print("Phase 561 T3: Line-Level Compositional Distributions")
    print("=" * 60)

    # Load corpus
    print("Loading T1 corpus...")
    tokens = load_corpus()
    print(f"  {len(tokens)} tokens loaded")

    # Step A: Extract line profiles
    print("\nStep A: Extracting line profiles (lines with >= 5 tokens)...")
    lines = extract_line_profiles(tokens)
    print(f"  {len(lines)} qualifying lines")

    # Per-section line counts
    sec_counts = Counter(l['section'] for l in lines)
    for s in TEST_SECTIONS:
        n_folios = len(set(l['folio'] for l in lines if l['section'] == s))
        print(f"    {s}: {sec_counts.get(s, 0)} lines across {n_folios} folios")

    # Feature statistics
    profiles = np.array([l['profile'] for l in lines])
    print(f"\n  Feature statistics ({len(lines)} lines):")
    for fi, fname in enumerate(FEATURE_NAMES):
        col = profiles[:, fi]
        valid = ~np.isnan(col)
        if valid.sum() > 0:
            print(f"    {fname}: valid={valid.sum()}/{len(col)}, "
                  f"mean={np.nanmean(col):.4f}, std={np.nanstd(col):.4f}")
        else:
            print(f"    {fname}: all NaN")

    # Step B: Within-section distributional tests
    print("\n" + "=" * 60)
    print("Step B: Within-Section Distributional Tests")
    print("=" * 60)

    rng = np.random.default_rng(RNG_SEED)

    # B1: Variance Ratio
    b1_results = test_b1_variance_ratio(lines)

    # B2: Energy Distance
    b2_results = test_b2_energy_distance(lines, rng)

    # Overall verdict
    sub_tests = [b1_results['pass'], b2_results['pass']]
    pass_count = sum(sub_tests)
    overall_pass = pass_count >= 1

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"B1 (Variance Ratio):   {'PASS' if b1_results['pass'] else 'FAIL'}")
    print(f"B2 (Energy Distance):  {'PASS' if b2_results['pass'] else 'FAIL'}")
    print(f"\nOverall T3: {'PASS' if overall_pass else 'FAIL'} ({pass_count}/2 sub-tests)")
    print(f"Elapsed: {elapsed:.1f}s")

    # Build output (strip numpy arrays from pair_details for JSON serialization)
    b2_output = dict(b2_results)
    b2_per_section = {}
    for sec, res in b2_results['per_section'].items():
        sec_res = dict(res)
        if 'pair_details' in sec_res:
            # Keep only top-20 most significant pairs to limit file size
            pairs_sorted = sorted(sec_res['pair_details'], key=lambda x: x['p_value'])
            sec_res['pair_details_top20'] = pairs_sorted[:20]
            sec_res['pair_details_count'] = len(sec_res['pair_details'])
            del sec_res['pair_details']
        b2_per_section[sec] = sec_res
    b2_output['per_section'] = b2_per_section

    output = {
        'metadata': {
            'phase': 'HIERARCHICAL_TRACE_ATTRIBUTION',
            'task': 'T3',
            'name': 'Line-Level Compositional Distributions',
            'n_corpus_tokens': len(tokens),
            'n_qualifying_lines': len(lines),
            'min_tokens_per_line': 5,
            'n_features': len(FEATURE_NAMES),
            'feature_names': FEATURE_NAMES,
            'test_sections': TEST_SECTIONS,
            'n_permutations': N_PERMS,
            'rng_seed': RNG_SEED,
            'elapsed_seconds': round(elapsed, 1)
        },
        'line_counts_per_section': {s: sec_counts.get(s, 0) for s in TEST_SECTIONS},
        'feature_statistics': {
            fname: {
                'valid_count': int((~np.isnan(profiles[:, fi])).sum()),
                'nan_count': int(np.isnan(profiles[:, fi]).sum()),
                'mean': round(float(np.nanmean(profiles[:, fi])), 6) if (~np.isnan(profiles[:, fi])).sum() > 0 else None,
                'std': round(float(np.nanstd(profiles[:, fi])), 6) if (~np.isnan(profiles[:, fi])).sum() > 0 else None,
            }
            for fi, fname in enumerate(FEATURE_NAMES)
        },
        'B1_variance_ratio': b1_results,
        'B2_energy_distance': b2_output,
        'sub_test_results': {
            'B1': b1_results['pass'],
            'B2': b2_results['pass']
        },
        'pass_count': pass_count,
        'overall_pass': overall_pass
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
