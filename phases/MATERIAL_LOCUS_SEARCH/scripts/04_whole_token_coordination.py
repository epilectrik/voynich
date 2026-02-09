#!/usr/bin/env python3
"""
Test 4: Whole-Token Variant Coordination as Material Signal

Question: C733 showed that 38% of within-line co-occurrence structure comes from
PREFIX+SUFFIX coordination beyond MIDDLE assignment. Is this coordination
section-specific?

Method:
  1. For Currier B (and A for comparison), extract full morphological decomposition.
  2. For each MIDDLE appearing in 3+ sections with >=10 tokens/section, build
     a "variant profile": distribution of (PREFIX, SUFFIX) combinations.
  3. Chi-square test per MIDDLE for variant distribution across sections.
  4. Cramer's V per MIDDLE.
  5. Mutual information decomposition:
     - MI(variant, section)
     - MI(variant, prefix_class)
     - Residual MI(variant, section | prefix_class)
  6. Permutation test (500 permutations) for significance.
  7. Repeat for Currier A for comparison.

Pass: Residual MI positive and significant (p < 0.01) for Currier B.
Fail: Residual MI < 0.01 bits or not significant.

Phase: MATERIAL_LOCUS_SEARCH
"""

import sys
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================
N_PERMUTATIONS = 500
MIN_SECTIONS = 3
MIN_TOKENS_PER_SECTION = 10
RANDOM_SEED = 42

OUTPUT_PATH = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/whole_token_coordination.json')


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def compute_mi(joint_counts, marginal_x, marginal_y, total):
    """
    Compute mutual information I(X; Y) in bits.

    joint_counts: dict of (x, y) -> count
    marginal_x: dict of x -> count
    marginal_y: dict of y -> count
    total: total number of observations
    """
    mi = 0.0
    for (x, y), c_xy in joint_counts.items():
        if c_xy == 0:
            continue
        p_xy = c_xy / total
        p_x = marginal_x[x] / total
        p_y = marginal_y[y] / total
        if p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def compute_conditional_mi(data_triples, total):
    """
    Compute conditional MI: I(X; Y | Z) = I(X; Y, Z) - I(X; Z)

    data_triples: list of (variant, section, prefix_class) tuples
    total: total count

    Using the chain rule: I(X; Y | Z) = H(X|Z) - H(X|Y,Z)
    Or equivalently: I(X;Y|Z) = I(X; Y,Z) - I(X; Z)

    Where X=variant, Y=section, Z=prefix_class
    """
    # Count joint (variant, (section, prefix_class))
    joint_v_sp = Counter()
    marginal_v = Counter()
    marginal_sp = Counter()

    # Count joint (variant, prefix_class) for I(variant; prefix_class)
    joint_v_p = Counter()
    marginal_p = Counter()

    for variant, section, prefix_class in data_triples:
        joint_v_sp[(variant, (section, prefix_class))] += 1
        marginal_v[variant] += 1
        marginal_sp[(section, prefix_class)] += 1
        joint_v_p[(variant, prefix_class)] += 1
        marginal_p[prefix_class] += 1

    mi_v_sp = compute_mi(joint_v_sp, marginal_v, marginal_sp, total)
    mi_v_p = compute_mi(joint_v_p, marginal_v, marginal_p, total)

    return mi_v_sp - mi_v_p


def cramers_v(contingency, n_rows, n_cols, total):
    """
    Compute Cramer's V from a contingency table (dict of (row, col) -> count).

    contingency: dict of (row_val, col_val) -> count
    n_rows: number of unique row values
    n_cols: number of unique column values
    total: total observations
    """
    # Compute row and column marginals
    row_totals = Counter()
    col_totals = Counter()
    for (r, c), count in contingency.items():
        row_totals[r] += count
        col_totals[c] += count

    # Chi-square statistic
    chi2 = 0.0
    for (r, c), observed in contingency.items():
        expected = (row_totals[r] * col_totals[c]) / total
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    # Also add cells with 0 observed but nonzero expected
    for r in row_totals:
        for c in col_totals:
            if (r, c) not in contingency:
                expected = (row_totals[r] * col_totals[c]) / total
                if expected > 0:
                    chi2 += expected  # (0 - E)^2 / E = E

    k = min(n_rows, n_cols)
    if k <= 1 or total == 0:
        return 0.0, chi2
    v = math.sqrt(chi2 / (total * (k - 1)))
    return v, chi2


def analyze_language(tokens_iter, language_label, morph):
    """
    Run full analysis for one language (A or B).

    Returns a results dict.
    """
    random.seed(RANDOM_SEED)

    # ----------------------------------------------------------
    # Step 1: Extract morphology and build per-MIDDLE data
    # ----------------------------------------------------------
    # We need: for each token -> (MIDDLE, section, variant=(PREFIX, SUFFIX))
    records = []  # list of (middle, section, prefix, suffix)

    for token in tokens_iter:
        m = morph.extract(token.word)
        if m.middle is None or m.is_empty_middle:
            continue

        prefix_label = m.prefix if m.prefix else 'BARE'
        suffix_label = m.suffix if m.suffix else 'BARE'
        records.append((m.middle, token.section, prefix_label, suffix_label))

    total_tokens = len(records)

    # ----------------------------------------------------------
    # Step 2: Group by MIDDLE, filter to qualifying MIDDLEs
    # ----------------------------------------------------------
    # Pre-compute per-MIDDLE, per-section counts
    middle_section_counts = defaultdict(Counter)  # middle -> {section: count}
    for middle, section, prefix, suffix in records:
        middle_section_counts[middle][section] += 1

    qualifying_middles = []
    for mid, sec_counts in middle_section_counts.items():
        # Must appear in 3+ sections
        qualifying_sections = [s for s, c in sec_counts.items() if c >= MIN_TOKENS_PER_SECTION]
        if len(qualifying_sections) >= MIN_SECTIONS:
            qualifying_middles.append(mid)

    qualifying_middles_set = set(qualifying_middles)

    # Filter records to qualifying MIDDLEs only
    filtered_records = [(mid, sec, pfx, sfx) for mid, sec, pfx, sfx in records
                        if mid in qualifying_middles_set]

    # ----------------------------------------------------------
    # Step 3: Per-MIDDLE chi-square and Cramer's V
    # ----------------------------------------------------------
    # Build per-MIDDLE data structures
    middle_data = defaultdict(list)  # middle -> [(section, prefix, suffix), ...]
    for mid, sec, pfx, sfx in filtered_records:
        middle_data[mid].append((sec, pfx, sfx))

    per_middle_results = []
    for mid in sorted(qualifying_middles):
        entries = middle_data[mid]
        n = len(entries)

        # Build contingency table: variant (PREFIX, SUFFIX) vs section
        contingency = Counter()
        variants = set()
        sections = set()
        for sec, pfx, sfx in entries:
            variant = (pfx, sfx)
            contingency[(variant, sec)] += 1
            variants.add(variant)
            sections.add(sec)

        n_variants = len(variants)
        n_sections = len(sections)

        v, chi2 = cramers_v(contingency, n_variants, n_sections, n)

        per_middle_results.append({
            'middle': mid,
            'n_tokens': n,
            'n_sections': n_sections,
            'n_variants': n_variants,
            'chi_square': round(chi2, 2),
            'cramers_v': round(v, 4),
        })

    # ----------------------------------------------------------
    # Step 4: Aggregate MI decomposition
    # ----------------------------------------------------------
    # Build triples for MI computation
    # variant = (PREFIX, SUFFIX), section, prefix_class = PREFIX
    triples_variant_section = []  # (variant, section)
    triples_variant_prefix = []   # (variant, prefix_class)
    full_triples = []             # (variant, section, prefix_class)

    for mid, sec, pfx, sfx in filtered_records:
        variant = f"{pfx}+{sfx}"
        full_triples.append((variant, sec, pfx))
        triples_variant_section.append((variant, sec))
        triples_variant_prefix.append((variant, pfx))

    total_filtered = len(full_triples)

    # MI(variant; section)
    joint_vs = Counter(triples_variant_section)
    marginal_v = Counter(t[0] for t in triples_variant_section)
    marginal_s = Counter(t[1] for t in triples_variant_section)
    mi_variant_section = compute_mi(joint_vs, marginal_v, marginal_s, total_filtered)

    # MI(variant; prefix_class)
    joint_vp = Counter(triples_variant_prefix)
    marginal_v2 = Counter(t[0] for t in triples_variant_prefix)
    marginal_p = Counter(t[1] for t in triples_variant_prefix)
    mi_variant_prefix = compute_mi(joint_vp, marginal_v2, marginal_p, total_filtered)

    # Residual: MI(variant; section | prefix_class)
    residual_mi = compute_conditional_mi(full_triples, total_filtered)

    # ----------------------------------------------------------
    # Step 5: Permutation test
    # ----------------------------------------------------------
    # Shuffle section labels within each MIDDLE, recompute residual MI
    # Build grouped structure: middle -> list of (variant, section, prefix) indices
    middle_groups = defaultdict(list)
    for i, (mid, sec, pfx, sfx) in enumerate(filtered_records):
        middle_groups[mid].append(i)

    null_residual_mis = []
    for perm_i in range(N_PERMUTATIONS):
        # Shuffle sections within each MIDDLE group
        shuffled_sections = list(range(total_filtered))  # placeholder
        section_list = [sec for _, sec, _, _ in filtered_records]
        shuffled_section_list = section_list.copy()

        for mid, indices in middle_groups.items():
            # Get sections for this MIDDLE
            mid_sections = [section_list[i] for i in indices]
            random.shuffle(mid_sections)
            for j, idx in enumerate(indices):
                shuffled_section_list[idx] = mid_sections[j]

        # Rebuild triples with shuffled sections
        perm_triples = []
        for i, (mid, _, pfx, sfx) in enumerate(filtered_records):
            variant = f"{pfx}+{sfx}"
            perm_triples.append((variant, shuffled_section_list[i], pfx))

        perm_residual = compute_conditional_mi(perm_triples, total_filtered)
        null_residual_mis.append(perm_residual)

    # P-value: fraction of null >= observed
    p_value = sum(1 for x in null_residual_mis if x >= residual_mi) / N_PERMUTATIONS

    # Null distribution statistics
    null_mean = sum(null_residual_mis) / len(null_residual_mis)
    null_sorted = sorted(null_residual_mis)
    null_95 = null_sorted[int(0.95 * N_PERMUTATIONS)]
    null_99 = null_sorted[int(0.99 * N_PERMUTATIONS)]

    # ----------------------------------------------------------
    # Step 6: Summary statistics
    # ----------------------------------------------------------
    cramers_values = [r['cramers_v'] for r in per_middle_results]
    mean_cramers = sum(cramers_values) / len(cramers_values) if cramers_values else 0
    median_cramers = sorted(cramers_values)[len(cramers_values) // 2] if cramers_values else 0

    # Count MIDDLEs with "strong" section specificity (V > 0.2)
    strong_middles = [r for r in per_middle_results if r['cramers_v'] > 0.2]

    return {
        'language': language_label,
        'total_tokens_analyzed': total_tokens,
        'qualifying_middles': len(qualifying_middles),
        'total_filtered_tokens': total_filtered,
        'mi_variant_section_bits': round(mi_variant_section, 6),
        'mi_variant_prefix_bits': round(mi_variant_prefix, 6),
        'residual_mi_bits': round(residual_mi, 6),
        'residual_fraction_of_total': round(residual_mi / mi_variant_section, 4) if mi_variant_section > 0 else 0,
        'permutation_test': {
            'n_permutations': N_PERMUTATIONS,
            'observed_residual_mi': round(residual_mi, 6),
            'null_mean': round(null_mean, 6),
            'null_95th_percentile': round(null_95, 6),
            'null_99th_percentile': round(null_99, 6),
            'p_value': round(p_value, 4),
        },
        'cramers_v_summary': {
            'mean': round(mean_cramers, 4),
            'median': round(median_cramers, 4),
            'n_strong_v_gt_0_2': len(strong_middles),
            'fraction_strong': round(len(strong_middles) / len(per_middle_results), 4) if per_middle_results else 0,
        },
        'per_middle_top10': sorted(per_middle_results, key=lambda x: x['cramers_v'], reverse=True)[:10],
    }


# ============================================================
# MAIN
# ============================================================
def main():
    print("Test 4: Whole-Token Variant Coordination as Material Signal")
    print("=" * 65)

    tx = Transcript()
    morph = Morphology()

    # Run for Currier B (primary)
    print("\n--- Currier B Analysis ---")
    b_results = analyze_language(tx.currier_b(), 'B', morph)
    print(f"  Qualifying MIDDLEs: {b_results['qualifying_middles']}")
    print(f"  Filtered tokens: {b_results['total_filtered_tokens']}")
    print(f"  MI(variant; section):        {b_results['mi_variant_section_bits']:.6f} bits")
    print(f"  MI(variant; prefix_class):   {b_results['mi_variant_prefix_bits']:.6f} bits")
    print(f"  Residual MI:                 {b_results['residual_mi_bits']:.6f} bits")
    print(f"  Residual fraction:           {b_results['residual_fraction_of_total']:.4f}")
    print(f"  Permutation p-value:         {b_results['permutation_test']['p_value']}")
    print(f"  Mean Cramer's V:             {b_results['cramers_v_summary']['mean']:.4f}")

    # Run for Currier A (comparison)
    print("\n--- Currier A Analysis ---")
    a_results = analyze_language(tx.currier_a(), 'A', morph)
    print(f"  Qualifying MIDDLEs: {a_results['qualifying_middles']}")
    print(f"  Filtered tokens: {a_results['total_filtered_tokens']}")
    print(f"  MI(variant; section):        {a_results['mi_variant_section_bits']:.6f} bits")
    print(f"  MI(variant; prefix_class):   {a_results['mi_variant_prefix_bits']:.6f} bits")
    print(f"  Residual MI:                 {a_results['residual_mi_bits']:.6f} bits")
    print(f"  Residual fraction:           {a_results['residual_fraction_of_total']:.4f}")
    print(f"  Permutation p-value:         {a_results['permutation_test']['p_value']}")
    print(f"  Mean Cramer's V:             {a_results['cramers_v_summary']['mean']:.4f}")

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    residual_b = b_results['residual_mi_bits']
    p_b = b_results['permutation_test']['p_value']

    if residual_b > 0.01 and p_b < 0.01:
        verdict = 'PASS'
        verdict_detail = (
            f"Residual MI = {residual_b:.6f} bits (> 0.01 threshold), "
            f"p = {p_b} (< 0.01). Section identity carries information about "
            f"token variant selection beyond PREFIX compatibility."
        )
    elif residual_b > 0 and p_b < 0.01:
        verdict = 'MARGINAL_PASS'
        verdict_detail = (
            f"Residual MI = {residual_b:.6f} bits (positive but below 0.01 threshold), "
            f"p = {p_b}. Statistically significant but small effect."
        )
    else:
        verdict = 'FAIL'
        verdict_detail = (
            f"Residual MI = {residual_b:.6f} bits, p = {p_b}. "
            f"Variant coordination explained by PREFIX-MIDDLE compatibility (C911)."
        )

    print(f"\n{'=' * 65}")
    print(f"VERDICT: {verdict}")
    print(f"  {verdict_detail}")

    # ----------------------------------------------------------
    # Comparison summary
    # ----------------------------------------------------------
    comparison = {
        'b_residual_mi': b_results['residual_mi_bits'],
        'a_residual_mi': a_results['residual_mi_bits'],
        'b_over_a_ratio': round(b_results['residual_mi_bits'] / a_results['residual_mi_bits'], 2) if a_results['residual_mi_bits'] > 0 else None,
        'b_p_value': b_results['permutation_test']['p_value'],
        'a_p_value': a_results['permutation_test']['p_value'],
    }

    # ----------------------------------------------------------
    # Output
    # ----------------------------------------------------------
    output = {
        'test': 'whole_token_variant_coordination',
        'phase': 'MATERIAL_LOCUS_SEARCH',
        'test_number': 4,
        'question': 'Is PREFIX+SUFFIX variant coordination section-specific beyond PREFIX-MIDDLE compatibility?',
        'method': {
            'description': 'Mutual information decomposition of variant-section association, controlling for PREFIX class',
            'qualifying_criteria': f'{MIN_SECTIONS}+ sections with {MIN_TOKENS_PER_SECTION}+ tokens each per MIDDLE',
            'permutations': N_PERMUTATIONS,
            'random_seed': RANDOM_SEED,
        },
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'currier_b': b_results,
        'currier_a': a_results,
        'comparison': comparison,
        'references': ['C733', 'C911', 'C728', 'C697', 'C730'],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
