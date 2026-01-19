"""
AXIS 1: Currier A Entry Structure as Cognitive Interface

Questions (all order-independent):
1. Does closure strength correlate with incompatibility pressure?
2. Does closure correlate with novelty introduction (rare MIDDLEs)?
3. Does closure correlate with adjacency cluster boundaries (local context reset)?
4. Is closure stronger in regions of higher discrimination fragility?

All tests use order-robust statistics.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from typing import Dict, List, Set, Tuple

from pcc_data_loader import (
    PCCDataLoader, get_order_robust_adjacency_pairs,
    permutation_test, bootstrap_ci
)


def test_closure_incompatibility_correlation(entries: List[Dict],
                                             loader: PCCDataLoader) -> Dict:
    """
    Q1: Does closure strength correlate with incompatibility pressure?

    Hypothesis: Entries with higher MIDDLE incompatibility density
    are more likely to end with closure markers.

    ORDER SENSITIVITY: INVARIANT (bag-of-entry statistics)
    """
    print("\n" + "-"*60)
    print("Q1: Closure vs Incompatibility Pressure")
    print("-"*60)

    all_middles = loader.get_all_middles(entries)

    # Calculate incompatibility density for each entry
    densities_with_closure = []
    densities_without_closure = []

    for entry in entries:
        density = loader.calculate_incompatibility_density(
            entry['middles'], all_middles
        )

        if entry['has_any_closure']:
            densities_with_closure.append(density)
        else:
            densities_without_closure.append(density)

    # Statistics
    mean_with = np.mean(densities_with_closure)
    mean_without = np.mean(densities_without_closure)

    # Mann-Whitney U test (non-parametric, order-independent)
    if len(densities_without_closure) > 5:
        u_stat, p_value = stats.mannwhitneyu(
            densities_with_closure, densities_without_closure,
            alternative='greater'
        )
    else:
        u_stat, p_value = 0, 1.0

    # Effect size (Cohen's d)
    pooled_std = np.sqrt(
        (np.var(densities_with_closure) + np.var(densities_without_closure)) / 2
    )
    cohens_d = (mean_with - mean_without) / pooled_std if pooled_std > 0 else 0

    print(f"\n  Entries with closure: {len(densities_with_closure)}")
    print(f"  Entries without closure: {len(densities_without_closure)}")
    print(f"\n  Mean density (with closure): {mean_with:.4f}")
    print(f"  Mean density (without closure): {mean_without:.4f}")
    print(f"  Ratio: {mean_with/mean_without:.3f}x" if mean_without > 0 else "  Ratio: N/A")
    print(f"\n  Mann-Whitney U: {u_stat:.1f}, p = {p_value:.4f}")
    print(f"  Cohen's d: {cohens_d:.3f}")

    # Verdict
    if p_value < 0.05 and cohens_d > 0.1:
        verdict = "YES"
        interpretation = "Closure correlates with higher incompatibility density"
    elif p_value < 0.05:
        verdict = "WEAK_YES"
        interpretation = "Significant but small effect size"
    else:
        verdict = "NO"
        interpretation = "Closure is independent of incompatibility pressure"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")

    return {
        'question': 'Closure vs Incompatibility Pressure',
        'order_sensitivity': 'INVARIANT',
        'n_with_closure': len(densities_with_closure),
        'n_without_closure': len(densities_without_closure),
        'mean_density_with': mean_with,
        'mean_density_without': mean_without,
        'mann_whitney_u': float(u_stat),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_closure_novelty_correlation(entries: List[Dict],
                                     loader: PCCDataLoader) -> Dict:
    """
    Q2: Does closure correlate with novelty introduction?

    Hypothesis: Entries introducing rare MIDDLEs are more likely
    to have closure markers (cognitive bracketing of novel items).

    ORDER SENSITIVITY: INVARIANT (uses global rarity, not first-appearance)
    """
    print("\n" + "-"*60)
    print("Q2: Closure vs Novelty (Rare MIDDLE Introduction)")
    print("-"*60)

    # Get globally rare MIDDLEs (order-independent definition)
    rare_middles = loader.get_rare_middles(threshold=3)
    print(f"\n  Rare MIDDLEs (appearing <= 3 times): {len(rare_middles)}")

    # Calculate rare MIDDLE count per entry
    rare_counts_with_closure = []
    rare_counts_without_closure = []

    has_rare_with_closure = 0
    has_rare_without_closure = 0

    for entry in entries:
        rare_in_entry = entry['middles'] & rare_middles
        rare_count = len(rare_in_entry)

        if entry['has_any_closure']:
            rare_counts_with_closure.append(rare_count)
            if rare_count > 0:
                has_rare_with_closure += 1
        else:
            rare_counts_without_closure.append(rare_count)
            if rare_count > 0:
                has_rare_without_closure += 1

    # Statistics
    mean_rare_with = np.mean(rare_counts_with_closure)
    mean_rare_without = np.mean(rare_counts_without_closure)

    # Chi-square test for proportion with any rare MIDDLE
    n_with = len(rare_counts_with_closure)
    n_without = len(rare_counts_without_closure)

    contingency = [
        [has_rare_with_closure, n_with - has_rare_with_closure],
        [has_rare_without_closure, n_without - has_rare_without_closure]
    ]

    if min(min(contingency[0]), min(contingency[1])) >= 5:
        chi2, p_chi = stats.chi2_contingency(contingency)[:2]
    else:
        chi2, p_chi = 0, 1.0

    # Mann-Whitney for counts
    if n_without > 5:
        u_stat, p_mw = stats.mannwhitneyu(
            rare_counts_with_closure, rare_counts_without_closure,
            alternative='greater'
        )
    else:
        u_stat, p_mw = 0, 1.0

    rate_with = has_rare_with_closure / n_with if n_with > 0 else 0
    rate_without = has_rare_without_closure / n_without if n_without > 0 else 0

    print(f"\n  Rate of rare MIDDLE presence:")
    print(f"    With closure: {rate_with:.1%} ({has_rare_with_closure}/{n_with})")
    print(f"    Without closure: {rate_without:.1%} ({has_rare_without_closure}/{n_without})")
    print(f"    Ratio: {rate_with/rate_without:.2f}x" if rate_without > 0 else "    Ratio: N/A")
    print(f"\n  Mean rare MIDDLE count:")
    print(f"    With closure: {mean_rare_with:.3f}")
    print(f"    Without closure: {mean_rare_without:.3f}")
    print(f"\n  Chi-square (presence): {chi2:.2f}, p = {p_chi:.4f}")
    print(f"  Mann-Whitney (count): U = {u_stat:.1f}, p = {p_mw:.4f}")

    # Verdict
    if p_chi < 0.05 and rate_with > rate_without:
        verdict = "YES"
        interpretation = "Closure entries contain more rare MIDDLEs"
    elif p_chi < 0.10:
        verdict = "WEAK_YES"
        interpretation = "Marginal association with rare MIDDLEs"
    else:
        verdict = "NO"
        interpretation = "Closure is independent of MIDDLE rarity"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")

    return {
        'question': 'Closure vs Novelty (Rare MIDDLEs)',
        'order_sensitivity': 'INVARIANT',
        'n_rare_middles': len(rare_middles),
        'rate_with_closure': rate_with,
        'rate_without_closure': rate_without,
        'mean_rare_with': mean_rare_with,
        'mean_rare_without': mean_rare_without,
        'chi2': float(chi2),
        'p_chi': float(p_chi),
        'mann_whitney_u': float(u_stat),
        'p_mw': float(p_mw),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_closure_adjacency_boundary(entries: List[Dict],
                                    loader: PCCDataLoader) -> Dict:
    """
    Q3: Does closure correlate with adjacency cluster boundaries?

    Hypothesis: Entries ending with closure are more likely to be
    followed by entries with LOW vocabulary overlap (context reset).

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    (depends on within-folio line sequence, but not cross-folio order)
    """
    print("\n" + "-"*60)
    print("Q3: Closure vs Adjacency Cluster Boundaries")
    print("-"*60)

    # Get adjacent pairs
    pairs = get_order_robust_adjacency_pairs(entries)
    print(f"\n  Adjacent entry pairs: {len(pairs)}")

    # Calculate Jaccard similarity for each pair
    jaccard_after_closure = []
    jaccard_after_no_closure = []

    for curr, next_entry in pairs:
        similarity = loader.jaccard_similarity(
            curr['middles'], next_entry['middles']
        )

        if curr['has_any_closure']:
            jaccard_after_closure.append(similarity)
        else:
            jaccard_after_no_closure.append(similarity)

    # Statistics
    mean_after_closure = np.mean(jaccard_after_closure)
    mean_after_no_closure = np.mean(jaccard_after_no_closure)

    # Mann-Whitney test
    if len(jaccard_after_no_closure) > 5:
        u_stat, p_value = stats.mannwhitneyu(
            jaccard_after_closure, jaccard_after_no_closure,
            alternative='less'  # Closure should lead to LOWER similarity
        )
    else:
        u_stat, p_value = 0, 1.0

    # Bootstrap CI for difference
    all_jaccards = jaccard_after_closure + jaccard_after_no_closure
    diff_observed = mean_after_closure - mean_after_no_closure

    print(f"\n  Pairs after closure: {len(jaccard_after_closure)}")
    print(f"  Pairs after non-closure: {len(jaccard_after_no_closure)}")
    print(f"\n  Mean Jaccard similarity:")
    print(f"    After closure: {mean_after_closure:.4f}")
    print(f"    After non-closure: {mean_after_no_closure:.4f}")
    print(f"    Difference: {diff_observed:.4f}")
    print(f"\n  Mann-Whitney U: {u_stat:.1f}, p = {p_value:.4f}")

    # Verdict
    if p_value < 0.05 and diff_observed < 0:
        verdict = "YES"
        interpretation = "Closure marks context reset (lower following similarity)"
    elif p_value < 0.10 and diff_observed < 0:
        verdict = "WEAK_YES"
        interpretation = "Marginal boundary effect"
    else:
        verdict = "NO"
        interpretation = "Closure does not mark adjacency boundaries"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: FOLIO_LOCAL_ORDER")
    print(f"  (Result depends on within-folio line sequence)")

    return {
        'question': 'Closure vs Adjacency Boundaries',
        'order_sensitivity': 'FOLIO_LOCAL_ORDER',
        'n_pairs_after_closure': len(jaccard_after_closure),
        'n_pairs_after_no_closure': len(jaccard_after_no_closure),
        'mean_jaccard_after_closure': mean_after_closure,
        'mean_jaccard_after_no_closure': mean_after_no_closure,
        'difference': diff_observed,
        'mann_whitney_u': float(u_stat),
        'p_value': float(p_value),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_closure_discrimination_fragility(entries: List[Dict],
                                          loader: PCCDataLoader) -> Dict:
    """
    Q4: Is closure stronger in regions of higher discrimination fragility?

    Hypothesis: Entries with many MIDDLEs (complex discrimination bundles)
    or entries using tail-vocabulary MIDDLEs have higher closure rates.

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q4: Closure vs Discrimination Fragility")
    print("-"*60)

    all_middles = loader.get_all_middles(entries)
    total_count = sum(all_middles.values())

    # Define "tail vocabulary" as MIDDLEs in bottom 25% by frequency
    sorted_middles = sorted(all_middles.items(), key=lambda x: x[1])
    n_tail = len(sorted_middles) // 4
    tail_middles = {m for m, c in sorted_middles[:n_tail]}

    print(f"\n  Total unique MIDDLEs: {len(all_middles)}")
    print(f"  Tail vocabulary (bottom 25%): {len(tail_middles)}")

    # Metrics per entry
    results_by_complexity = defaultdict(lambda: {'closure': 0, 'total': 0})
    results_by_tail_usage = defaultdict(lambda: {'closure': 0, 'total': 0})

    for entry in entries:
        # Complexity = number of unique MIDDLEs
        n_middles = len(entry['middles'])
        if n_middles <= 3:
            complexity_bin = 'low (1-3)'
        elif n_middles <= 6:
            complexity_bin = 'medium (4-6)'
        else:
            complexity_bin = 'high (7+)'

        results_by_complexity[complexity_bin]['total'] += 1
        if entry['has_any_closure']:
            results_by_complexity[complexity_bin]['closure'] += 1

        # Tail usage = proportion of MIDDLEs from tail
        tail_overlap = entry['middles'] & tail_middles
        tail_ratio = len(tail_overlap) / len(entry['middles']) if entry['middles'] else 0

        if tail_ratio == 0:
            tail_bin = 'no_tail'
        elif tail_ratio <= 0.25:
            tail_bin = 'low_tail'
        else:
            tail_bin = 'high_tail'

        results_by_tail_usage[tail_bin]['total'] += 1
        if entry['has_any_closure']:
            results_by_tail_usage[tail_bin]['closure'] += 1

    # Print complexity results
    print("\n  Closure rate by MIDDLE complexity:")
    complexity_rates = {}
    for bin_name in ['low (1-3)', 'medium (4-6)', 'high (7+)']:
        data = results_by_complexity[bin_name]
        rate = data['closure'] / data['total'] if data['total'] > 0 else 0
        print(f"    {bin_name}: {rate:.1%} ({data['closure']}/{data['total']})")
        complexity_rates[bin_name] = rate

    # Print tail usage results
    print("\n  Closure rate by tail vocabulary usage:")
    tail_rates = {}
    for bin_name in ['no_tail', 'low_tail', 'high_tail']:
        data = results_by_tail_usage[bin_name]
        rate = data['closure'] / data['total'] if data['total'] > 0 else 0
        print(f"    {bin_name}: {rate:.1%} ({data['closure']}/{data['total']})")
        tail_rates[bin_name] = rate

    # Chi-square test for complexity
    complexity_contingency = [
        [results_by_complexity['low (1-3)']['closure'],
         results_by_complexity['low (1-3)']['total'] - results_by_complexity['low (1-3)']['closure']],
        [results_by_complexity['high (7+)']['closure'],
         results_by_complexity['high (7+)']['total'] - results_by_complexity['high (7+)']['closure']]
    ]

    if min(min(complexity_contingency[0]), min(complexity_contingency[1])) >= 5:
        chi2_complexity, p_complexity = stats.chi2_contingency(complexity_contingency)[:2]
    else:
        chi2_complexity, p_complexity = 0, 1.0

    # Chi-square test for tail
    if results_by_tail_usage['no_tail']['total'] >= 5 and results_by_tail_usage['high_tail']['total'] >= 5:
        tail_contingency = [
            [results_by_tail_usage['no_tail']['closure'],
             results_by_tail_usage['no_tail']['total'] - results_by_tail_usage['no_tail']['closure']],
            [results_by_tail_usage['high_tail']['closure'],
             results_by_tail_usage['high_tail']['total'] - results_by_tail_usage['high_tail']['closure']]
        ]
        chi2_tail, p_tail = stats.chi2_contingency(tail_contingency)[:2]
    else:
        chi2_tail, p_tail = 0, 1.0

    print(f"\n  Chi-square (complexity): {chi2_complexity:.2f}, p = {p_complexity:.4f}")
    print(f"  Chi-square (tail usage): {chi2_tail:.2f}, p = {p_tail:.4f}")

    # Verdict
    complexity_trend = complexity_rates.get('high (7+)', 0) > complexity_rates.get('low (1-3)', 0)
    tail_trend = tail_rates.get('high_tail', 0) > tail_rates.get('no_tail', 0)

    if p_complexity < 0.05 and complexity_trend:
        verdict_complexity = "YES"
    elif p_complexity < 0.10 and complexity_trend:
        verdict_complexity = "WEAK_YES"
    else:
        verdict_complexity = "NO"

    if p_tail < 0.05 and tail_trend:
        verdict_tail = "YES"
    elif p_tail < 0.10 and tail_trend:
        verdict_tail = "WEAK_YES"
    else:
        verdict_tail = "NO"

    if verdict_complexity in ["YES", "WEAK_YES"] or verdict_tail in ["YES", "WEAK_YES"]:
        overall_verdict = "PARTIAL"
        interpretation = f"Complexity: {verdict_complexity}, Tail usage: {verdict_tail}"
    else:
        overall_verdict = "NO"
        interpretation = "Closure is independent of discrimination fragility"

    print(f"\n  VERDICT: {overall_verdict}")
    print(f"  {interpretation}")

    return {
        'question': 'Closure vs Discrimination Fragility',
        'order_sensitivity': 'INVARIANT',
        'complexity_rates': complexity_rates,
        'tail_rates': tail_rates,
        'chi2_complexity': float(chi2_complexity),
        'p_complexity': float(p_complexity),
        'chi2_tail': float(chi2_tail),
        'p_tail': float(p_tail),
        'verdict_complexity': verdict_complexity,
        'verdict_tail': verdict_tail,
        'overall_verdict': overall_verdict,
        'interpretation': interpretation
    }


def generate_axis1_report(results: Dict) -> str:
    """Generate formatted AXIS 1 report."""
    report = """
================================================================================
AXIS 1 REPORT: Currier A Entry Structure as Cognitive Interface
================================================================================

PHASE: Post-Closure Characterization
TIER: 3 (Exploratory characterization)
REBINDING SENSITIVITY: Mostly INVARIANT (1 test FOLIO_LOCAL_ORDER)

--------------------------------------------------------------------------------
SUMMARY OF FINDINGS
--------------------------------------------------------------------------------

"""
    for q_num, (key, data) in enumerate(results.items(), 1):
        verdict = data.get('verdict', data.get('overall_verdict', 'N/A'))
        report += f"""
Q{q_num}: {data['question']}
    Order Sensitivity: {data['order_sensitivity']}
    Verdict: {verdict}
    Interpretation: {data['interpretation']}
"""

    report += """
--------------------------------------------------------------------------------
WHAT THIS DOES NOT CHANGE
--------------------------------------------------------------------------------

- LINE_ATOMIC (C233) remains unchanged
- Entry grammar (opener/content/closure) is confirmed, not new
- No new grammatical rules proposed
- No semantic interpretation of closure
- C384 (no A-B entry coupling) remains binding
- Closure mechanism is structural, not meaningful

--------------------------------------------------------------------------------
IMPLICATIONS
--------------------------------------------------------------------------------

"""
    # Determine overall implications
    verdicts = [r.get('verdict', r.get('overall_verdict', 'N/A')) for r in results.values()]
    if 'YES' in verdicts:
        report += """
POSITIVE FINDINGS:
- Closure correlates with at least one cognitive-load metric
- This supports closure as a human-factors navigation aid
- Entry structure is tuned to discrimination task demands
"""
    else:
        report += """
NULL FINDINGS:
- Closure appears independent of measured complexity metrics
- This suggests closure is a UNIFORM structural feature
- Not dynamically adjusted to discrimination pressure
"""

    report += """
--------------------------------------------------------------------------------
NON-IMPLICATIONS
--------------------------------------------------------------------------------

- Does NOT imply closure has semantic content
- Does NOT create new entry types or classifications
- Does NOT depend on folio ordering (mostly invariant)
- Does NOT reopen Tier 0-2 constraints

================================================================================
"""
    return report


def main():
    print("="*70)
    print("AXIS 1: Currier A Entry Structure as Cognitive Interface")
    print("="*70)

    # Load data
    print("\nLoading data...")
    loader = PCCDataLoader()
    entries = loader.get_entries()
    print(f"Loaded {len(entries)} entries")

    # Run all tests
    results = {}

    results['q1_incompatibility'] = test_closure_incompatibility_correlation(entries, loader)
    results['q2_novelty'] = test_closure_novelty_correlation(entries, loader)
    results['q3_adjacency'] = test_closure_adjacency_boundary(entries, loader)
    results['q4_fragility'] = test_closure_discrimination_fragility(entries, loader)

    # Generate report
    report = generate_axis1_report(results)
    print(report)

    # Save results
    output_path = Path(__file__).parent / 'axis1_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # Save report
    report_path = Path(__file__).parent / 'AXIS1_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    return results


if __name__ == '__main__':
    main()
