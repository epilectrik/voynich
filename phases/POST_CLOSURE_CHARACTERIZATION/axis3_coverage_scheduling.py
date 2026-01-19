"""
AXIS 3: Coverage Control vs Temporal Scheduling

This axis explicitly separates:
- Coverage logic (order-independent)
- Scheduling logic (order-recoverable)

Questions:
1. Is coverage optimization stable under random reordering? (INVARIANT)
2. Can we detect novelty fronts without folio index? (INVARIANT)
3. Is there a tail pressure signal detectable order-independently? (INVARIANT)
4. What order-dependent signals exist? (LATENT_ORDER_DEPENDENT)

CRITICAL: Any claim about "early" or "late" must be labeled LATENT_ORDER_DEPENDENT.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from typing import Dict, List, Set, Tuple
import random

from pcc_data_loader import (
    PCCDataLoader, permutation_test, bootstrap_ci
)


def test_coverage_stability_under_reordering(entries: List[Dict],
                                              loader: PCCDataLoader) -> Dict:
    """
    Q1: Is coverage optimization stable under random reordering?

    Test: Calculate total coverage metrics that don't depend on order.
    Compare observed folio-level coverage patterns to shuffled baselines.

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q1: Coverage Stability Under Reordering")
    print("-"*60)

    # Order-independent metrics per folio
    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    folio_metrics = []
    for folio, folio_entries in entries_by_folio.items():
        if len(folio_entries) < 3:
            continue

        # Collect all MIDDLEs in folio
        all_middles = set()
        for entry in folio_entries:
            all_middles.update(entry['middles'])

        # Coverage metrics (order-independent)
        metrics = {
            'folio': folio,
            'n_entries': len(folio_entries),
            'total_middles': len(all_middles),
            'middles_per_entry': len(all_middles) / len(folio_entries),
            'mean_entry_middles': np.mean([len(e['middles']) for e in folio_entries]),
            'overlap_ratio': calculate_overlap_ratio(folio_entries, loader)
        }
        folio_metrics.append(metrics)

    print(f"\n  Folios analyzed: {len(folio_metrics)}")

    # Check if coverage per entry is consistent across folios
    middles_per_entry = [m['middles_per_entry'] for m in folio_metrics]
    overlap_ratios = [m['overlap_ratio'] for m in folio_metrics]

    print(f"\n  MIDDLEs per entry across folios:")
    print(f"    Mean: {np.mean(middles_per_entry):.2f}")
    print(f"    Std: {np.std(middles_per_entry):.2f}")
    print(f"    CV (coefficient of variation): {np.std(middles_per_entry)/np.mean(middles_per_entry):.3f}")

    print(f"\n  Overlap ratio across folios:")
    print(f"    Mean: {np.mean(overlap_ratios):.3f}")
    print(f"    Std: {np.std(overlap_ratios):.3f}")

    # Test: is overlap ratio consistent? (low CV = stable coverage)
    cv_overlap = np.std(overlap_ratios) / np.mean(overlap_ratios) if np.mean(overlap_ratios) > 0 else float('inf')

    # Compare to random: shuffle entries across folios and recalculate
    n_permutations = 500
    null_cvs = []

    all_entries = [e for es in entries_by_folio.values() for e in es]
    folio_sizes = {f: len(es) for f, es in entries_by_folio.items() if len(es) >= 3}

    for _ in range(n_permutations):
        shuffled = random.sample(all_entries, len(all_entries))
        idx = 0
        perm_overlaps = []
        for folio, size in folio_sizes.items():
            perm_entries = shuffled[idx:idx + size]
            idx += size
            overlap = calculate_overlap_ratio(perm_entries, loader)
            perm_overlaps.append(overlap)
        if perm_overlaps:
            null_cv = np.std(perm_overlaps) / np.mean(perm_overlaps) if np.mean(perm_overlaps) > 0 else 0
            null_cvs.append(null_cv)

    p_value = permutation_test(cv_overlap, null_cvs, 'less')  # Lower CV = more consistent

    print(f"\n  Observed CV: {cv_overlap:.4f}")
    print(f"  Null mean CV: {np.mean(null_cvs):.4f}")
    print(f"  Permutation p-value (observed < null): {p_value:.4f}")

    if p_value < 0.05:
        verdict = "YES"
        interpretation = "Coverage structure is order-independent and stable"
    elif p_value < 0.10:
        verdict = "WEAK_YES"
        interpretation = "Marginal coverage stability signal"
    else:
        verdict = "NO"
        interpretation = "Coverage not more consistent than random allocation"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")

    return {
        'question': 'Coverage Stability Under Reordering',
        'order_sensitivity': 'INVARIANT',
        'n_folios': len(folio_metrics),
        'mean_middles_per_entry': float(np.mean(middles_per_entry)),
        'cv_overlap': float(cv_overlap),
        'null_mean_cv': float(np.mean(null_cvs)),
        'p_value': float(p_value),
        'verdict': verdict,
        'interpretation': interpretation
    }


def calculate_overlap_ratio(entries: List[Dict], loader: PCCDataLoader) -> float:
    """Calculate average pairwise overlap ratio for entries."""
    if len(entries) < 2:
        return 0.0

    overlaps = []
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            sim = loader.jaccard_similarity(
                entries[i]['middles'], entries[j]['middles']
            )
            overlaps.append(sim)

    return np.mean(overlaps)


def test_novelty_fronts_orderless(entries: List[Dict],
                                   loader: PCCDataLoader) -> Dict:
    """
    Q2: Can we detect novelty fronts without folio index?

    Novelty fronts = regions of high rare-MIDDLE concentration.
    Test if such concentration exists independent of order.

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q2: Novelty Fronts (Order-Independent)")
    print("-"*60)

    # Get rare MIDDLEs
    rare_middles = loader.get_rare_middles(threshold=3)
    print(f"\n  Rare MIDDLEs (appearing <= 3 times): {len(rare_middles)}")

    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    # Calculate rare MIDDLE concentration per folio
    folio_concentrations = {}
    for folio, folio_entries in entries_by_folio.items():
        if len(folio_entries) < 3:
            continue

        total_middles = sum(len(e['middles']) for e in folio_entries)
        rare_count = sum(len(e['middles'] & rare_middles) for e in folio_entries)
        concentration = rare_count / total_middles if total_middles > 0 else 0
        folio_concentrations[folio] = concentration

    concentrations = list(folio_concentrations.values())

    print(f"\n  Folios analyzed: {len(concentrations)}")
    print(f"\n  Rare MIDDLE concentration per folio:")
    print(f"    Mean: {np.mean(concentrations):.4f}")
    print(f"    Std: {np.std(concentrations):.4f}")
    print(f"    Min: {min(concentrations):.4f}")
    print(f"    Max: {max(concentrations):.4f}")

    # Check for non-uniform distribution (some folios are "novelty fronts")
    # Compare variance to Poisson expectation
    if np.mean(concentrations) > 0:
        variance_ratio = np.var(concentrations) / np.mean(concentrations)
    else:
        variance_ratio = 0

    # Chi-square test for uniformity
    n_bins = 4
    observed_counts, bin_edges = np.histogram(concentrations, bins=n_bins)
    expected_count = len(concentrations) / n_bins

    chi2 = sum((o - expected_count)**2 / expected_count for o in observed_counts)
    p_value = 1 - stats.chi2.cdf(chi2, df=n_bins-1)

    print(f"\n  Variance ratio (vs Poisson): {variance_ratio:.4f}")
    print(f"  Chi-square (uniformity): {chi2:.2f}, p = {p_value:.4f}")

    # Identify high-novelty folios
    threshold = np.mean(concentrations) + np.std(concentrations)
    high_novelty = [f for f, c in folio_concentrations.items() if c > threshold]
    print(f"\n  High-novelty folios (>1 std above mean): {len(high_novelty)}")

    if p_value < 0.05 and variance_ratio > 1.5:
        verdict = "YES"
        interpretation = "Non-uniform novelty distribution (novelty fronts exist)"
    elif variance_ratio > 1.2:
        verdict = "WEAK_YES"
        interpretation = "Some novelty concentration above random"
    else:
        verdict = "NO"
        interpretation = "Novelty uniformly distributed across folios"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")
    print(f"  (Novelty fronts detected without reference to folio order)")

    return {
        'question': 'Novelty Fronts (Order-Independent)',
        'order_sensitivity': 'INVARIANT',
        'n_rare_middles': len(rare_middles),
        'n_folios': len(concentrations),
        'mean_concentration': float(np.mean(concentrations)),
        'std_concentration': float(np.std(concentrations)),
        'variance_ratio': float(variance_ratio),
        'chi2': float(chi2),
        'p_value': float(p_value),
        'n_high_novelty_folios': len(high_novelty),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_tail_pressure_orderless(entries: List[Dict],
                                  loader: PCCDataLoader) -> Dict:
    """
    Q3: Is there a tail pressure signal detectable order-independently?

    Tail pressure = entries with high proportion of low-frequency MIDDLEs.
    Test if tail pressure varies systematically across folios.

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q3: Tail Pressure (Order-Independent)")
    print("-"*60)

    all_middles = loader.get_all_middles(entries)

    # Define tail as bottom 25% by frequency
    sorted_middles = sorted(all_middles.items(), key=lambda x: x[1])
    n_tail = len(sorted_middles) // 4
    tail_middles = {m for m, c in sorted_middles[:n_tail]}

    print(f"\n  Tail vocabulary (bottom 25%): {len(tail_middles)} MIDDLEs")

    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    # Calculate tail pressure per folio
    folio_tail_pressure = {}
    for folio, folio_entries in entries_by_folio.items():
        if len(folio_entries) < 3:
            continue

        pressures = []
        for entry in folio_entries:
            if entry['middles']:
                tail_in_entry = entry['middles'] & tail_middles
                pressure = len(tail_in_entry) / len(entry['middles'])
                pressures.append(pressure)

        folio_tail_pressure[folio] = np.mean(pressures) if pressures else 0

    pressures = list(folio_tail_pressure.values())

    print(f"\n  Folios analyzed: {len(pressures)}")
    print(f"\n  Tail pressure per folio:")
    print(f"    Mean: {np.mean(pressures):.4f}")
    print(f"    Std: {np.std(pressures):.4f}")

    # Check for systematic variation by section
    herbal_a_pressure = [p for f, p in folio_tail_pressure.items()
                         if loader.get_section(f) == 'herbal_a']
    herbal_c_pressure = [p for f, p in folio_tail_pressure.items()
                         if loader.get_section(f) == 'herbal_c']

    if herbal_a_pressure and herbal_c_pressure:
        mean_a = np.mean(herbal_a_pressure)
        mean_c = np.mean(herbal_c_pressure)

        u_stat, p_section = stats.mannwhitneyu(
            herbal_a_pressure, herbal_c_pressure,
            alternative='two-sided'
        )

        print(f"\n  Tail pressure by section:")
        print(f"    Herbal A: {mean_a:.4f} (n={len(herbal_a_pressure)})")
        print(f"    Herbal C: {mean_c:.4f} (n={len(herbal_c_pressure)})")
        print(f"    Mann-Whitney p = {p_section:.4f}")
    else:
        p_section = 1.0
        mean_a = mean_c = 0

    # Check for overall non-uniformity
    cv = np.std(pressures) / np.mean(pressures) if np.mean(pressures) > 0 else 0

    print(f"\n  Coefficient of variation: {cv:.4f}")

    if p_section < 0.05:
        verdict = "YES_SECTION"
        interpretation = "Tail pressure differs by section (order-independent signal)"
    elif cv > 0.3:
        verdict = "YES_VARIANCE"
        interpretation = "High tail pressure variance across folios"
    else:
        verdict = "NO"
        interpretation = "Tail pressure uniform across folios"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")

    return {
        'question': 'Tail Pressure (Order-Independent)',
        'order_sensitivity': 'INVARIANT',
        'n_tail_middles': len(tail_middles),
        'n_folios': len(pressures),
        'mean_pressure': float(np.mean(pressures)),
        'std_pressure': float(np.std(pressures)),
        'cv': float(cv),
        'herbal_a_mean': float(mean_a),
        'herbal_c_mean': float(mean_c),
        'p_section': float(p_section),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_order_dependent_signals(entries: List[Dict],
                                  loader: PCCDataLoader) -> Dict:
    """
    Q4: What order-dependent signals exist?

    EXPLICIT LATENT_ORDER_DEPENDENT analysis.
    Test what signals WOULD exist if current order were original.

    ORDER SENSITIVITY: LATENT_ORDER_DEPENDENT
    """
    print("\n" + "-"*60)
    print("Q4: Order-Dependent Signals (LATENT_ORDER_DEPENDENT)")
    print("-"*60)
    print("\n  WARNING: These findings assume current folio order is original.")
    print("  If rebinding occurred, these results are artifacts.")

    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    # Sort folios by numeric index
    import re
    def folio_sort_key(f):
        match = re.search(r'f(\d+)', f)
        return int(match.group(1)) if match else 0

    sorted_folios = sorted(entries_by_folio.keys(), key=folio_sort_key)

    # Track cumulative coverage across folios
    cumulative_middles = set()
    folio_novelty = []  # Proportion of new MIDDLEs at each folio

    for folio in sorted_folios:
        folio_entries = entries_by_folio[folio]
        folio_middles = set()
        for entry in folio_entries:
            folio_middles.update(entry['middles'])

        new_middles = folio_middles - cumulative_middles
        novelty = len(new_middles) / len(folio_middles) if folio_middles else 0
        folio_novelty.append(novelty)

        cumulative_middles.update(folio_middles)

    # Check for declining novelty (expected if order is pedagogical)
    if len(folio_novelty) >= 10:
        # Spearman correlation with position
        positions = list(range(len(folio_novelty)))
        rho, p_trend = stats.spearmanr(positions, folio_novelty)

        print(f"\n  Cumulative novelty analysis:")
        print(f"    First 10 folios avg novelty: {np.mean(folio_novelty[:10]):.3f}")
        print(f"    Last 10 folios avg novelty: {np.mean(folio_novelty[-10:]):.3f}")
        print(f"    Spearman rho (position vs novelty): {rho:.3f}")
        print(f"    p-value: {p_trend:.4f}")

        if p_trend < 0.05 and rho < -0.2:
            order_signal = "DECLINING_NOVELTY"
            interpretation = "Novelty declines with folio position (ORDER DEPENDENT)"
        elif p_trend < 0.05 and rho > 0.2:
            order_signal = "INCREASING_NOVELTY"
            interpretation = "Novelty increases with position (ORDER DEPENDENT)"
        else:
            order_signal = "NO_TREND"
            interpretation = "No systematic novelty trend in current order"
    else:
        rho, p_trend = 0, 1.0
        order_signal = "INSUFFICIENT_DATA"
        interpretation = "Too few folios for trend analysis"

    print(f"\n  ORDER SIGNAL: {order_signal}")
    print(f"  {interpretation}")
    print(f"\n  CRITICAL: This finding is LATENT_ORDER_DEPENDENT")
    print(f"  It would need external codicological validation")

    return {
        'question': 'Order-Dependent Signals',
        'order_sensitivity': 'LATENT_ORDER_DEPENDENT',
        'n_folios': len(sorted_folios),
        'first_10_novelty': float(np.mean(folio_novelty[:10])) if len(folio_novelty) >= 10 else None,
        'last_10_novelty': float(np.mean(folio_novelty[-10:])) if len(folio_novelty) >= 10 else None,
        'spearman_rho': float(rho),
        'p_value': float(p_trend),
        'order_signal': order_signal,
        'interpretation': interpretation
    }


def generate_axis3_report(results: Dict) -> str:
    """Generate formatted AXIS 3 report."""
    report = """
================================================================================
AXIS 3 REPORT: Coverage Control vs Temporal Scheduling
================================================================================

PHASE: Post-Closure Characterization
TIER: 3 (Exploratory characterization)
REBINDING SENSITIVITY: MIXED (see individual tests)

--------------------------------------------------------------------------------
KEY DISTINCTION
--------------------------------------------------------------------------------

This axis separates:
- COVERAGE LOGIC: Order-independent properties (INVARIANT)
- SCHEDULING LOGIC: Order-recoverable patterns (LATENT_ORDER_DEPENDENT)

Any claim about "early" or "late" is LATENT_ORDER_DEPENDENT.

--------------------------------------------------------------------------------
SUMMARY OF FINDINGS
--------------------------------------------------------------------------------

"""
    for q_num, (key, data) in enumerate(results.items(), 1):
        report += f"""
Q{q_num}: {data['question']}
    Order Sensitivity: {data['order_sensitivity']}
    Verdict: {data.get('verdict', data.get('order_signal', 'N/A'))}
    Interpretation: {data['interpretation']}
"""

    report += """
--------------------------------------------------------------------------------
INVARIANT FINDINGS (REBINDING-SAFE)
--------------------------------------------------------------------------------

The following findings do NOT depend on folio order:
"""
    for key, data in results.items():
        if data['order_sensitivity'] == 'INVARIANT':
            report += f"- {data['question']}: {data.get('verdict', 'N/A')}\n"

    report += """
--------------------------------------------------------------------------------
LATENT_ORDER_DEPENDENT FINDINGS (REBINDING-SENSITIVE)
--------------------------------------------------------------------------------

The following findings ASSUME current folio order is original:
"""
    for key, data in results.items():
        if data['order_sensitivity'] == 'LATENT_ORDER_DEPENDENT':
            report += f"- {data['question']}: {data.get('order_signal', 'N/A')}\n"

    report += """
These findings require external codicological validation before interpretation.

--------------------------------------------------------------------------------
WHAT THIS DOES NOT CHANGE
--------------------------------------------------------------------------------

- C476 (coverage optimality) is characterized, not changed
- C478 (temporal scheduling) interpretation is order-dependent
- No new scheduling grammar proposed
- Coverage remains a Tier 2 structural property

--------------------------------------------------------------------------------
IMPLICATIONS
--------------------------------------------------------------------------------

COVERAGE (INVARIANT):
- Coverage properties can be studied without folio order
- Folio-level coverage shows measurable structure

SCHEDULING (LATENT_ORDER_DEPENDENT):
- Any scheduling claims require order recovery
- Current folio order shows signals BUT may be artifact of rebinding

================================================================================
"""
    return report


def main():
    print("="*70)
    print("AXIS 3: Coverage Control vs Temporal Scheduling")
    print("="*70)

    # Load data
    print("\nLoading data...")
    loader = PCCDataLoader()
    entries = loader.get_entries()
    print(f"Loaded {len(entries)} entries")

    # Run all tests
    results = {}

    results['q1_coverage_stability'] = test_coverage_stability_under_reordering(entries, loader)
    results['q2_novelty_fronts'] = test_novelty_fronts_orderless(entries, loader)
    results['q3_tail_pressure'] = test_tail_pressure_orderless(entries, loader)
    results['q4_order_signals'] = test_order_dependent_signals(entries, loader)

    # Generate report
    report = generate_axis3_report(results)
    print(report)

    # Save results
    output_path = Path(__file__).parent / 'axis3_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # Save report
    report_path = Path(__file__).parent / 'AXIS3_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    return results


if __name__ == '__main__':
    main()
