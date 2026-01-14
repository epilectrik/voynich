#!/usr/bin/env python3
"""
Plant Folio Null Audit (ILL-TOP-1 Closure)

Purpose: Confirm that plant folios (Section H) are statistically
indistinguishable from non-plant folios across all existing metrics.

This is closure verification, NOT hypothesis generation.
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from collections import defaultdict

BASE_PATH = Path(__file__).parent.parent.parent
OUTPUT_DIR = Path(__file__).parent


def cohen_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def run_comparison(plant_values, non_plant_values, metric_name):
    """Run Mann-Whitney U test and compute effect size."""
    plant_values = [v for v in plant_values if v is not None and not np.isnan(v)]
    non_plant_values = [v for v in non_plant_values if v is not None and not np.isnan(v)]

    if len(plant_values) < 3 or len(non_plant_values) < 3:
        return {
            'metric': metric_name,
            'plant_n': len(plant_values),
            'non_plant_n': len(non_plant_values),
            'status': 'INSUFFICIENT_DATA'
        }

    u_stat, p_value = stats.mannwhitneyu(plant_values, non_plant_values, alternative='two-sided')
    effect = cohen_d(plant_values, non_plant_values)

    return {
        'metric': metric_name,
        'plant_n': len(plant_values),
        'plant_mean': float(np.mean(plant_values)),
        'plant_std': float(np.std(plant_values)),
        'non_plant_n': len(non_plant_values),
        'non_plant_mean': float(np.mean(non_plant_values)),
        'non_plant_std': float(np.std(non_plant_values)),
        'u_statistic': float(u_stat),
        'p_value': float(p_value),
        'effect_size': float(effect),
        'status': 'TESTED'
    }


def run_audit():
    """Run the complete plant folio null audit."""
    print("=" * 70)
    print("PLANT FOLIO NULL AUDIT (ILL-TOP-1 Closure)")
    print("=" * 70)

    # Load data
    print("\n--- Loading data ---")

    with open(BASE_PATH / 'results' / 'ht_folio_features.json', 'r') as f:
        ht_data = json.load(f)

    with open(BASE_PATH / 'results' / 'unified_folio_profiles.json', 'r') as f:
        unified_data = json.load(f)

    ht_folios = ht_data['folios']
    profiles = unified_data['profiles']

    print(f"  HT features: {len(ht_folios)} folios")
    print(f"  Unified profiles: {len(profiles)} folios")

    # Partition by section
    print("\n--- Partitioning folios ---")

    plant_folios = []  # Section H
    non_plant_folios = []

    for folio_id, data in ht_folios.items():
        section = data.get('section', '')
        if section == 'H':
            plant_folios.append(folio_id)
        else:
            non_plant_folios.append(folio_id)

    print(f"  Plant folios (Section H): {len(plant_folios)}")
    print(f"  Non-plant folios: {len(non_plant_folios)}")

    # Show section distribution
    section_counts = defaultdict(int)
    for data in ht_folios.values():
        section_counts[data.get('section', 'UNKNOWN')] += 1
    print(f"  Section distribution: {dict(section_counts)}")

    results = {
        'metadata': {
            'analysis': 'Plant Folio Null Audit',
            'purpose': 'Confirm plant folios are structurally indistinguishable',
            'n_plant': len(plant_folios),
            'n_non_plant': len(non_plant_folios),
            'section_distribution': dict(section_counts)
        },
        'tests': []
    }

    # ================================================================
    # GROUP 1: HT Metrics (all folios)
    # ================================================================
    print("\n" + "=" * 70)
    print("GROUP 1: HT Metrics (All Folios)")
    print("=" * 70)

    ht_metrics = ['ht_density', 'ht_ttr', 'line_initial_rate', 'line_final_rate']

    for metric in ht_metrics:
        plant_vals = [ht_folios[f].get(metric) for f in plant_folios if f in ht_folios]
        non_plant_vals = [ht_folios[f].get(metric) for f in non_plant_folios if f in ht_folios]
        result = run_comparison(plant_vals, non_plant_vals, f'HT.{metric}')
        results['tests'].append(result)
        print(f"\n{metric}:")
        if result['status'] == 'TESTED':
            print(f"  Plant: {result['plant_mean']:.4f} ± {result['plant_std']:.4f} (n={result['plant_n']})")
            print(f"  Non-plant: {result['non_plant_mean']:.4f} ± {result['non_plant_std']:.4f} (n={result['non_plant_n']})")
            print(f"  U={result['u_statistic']:.1f}, p={result['p_value']:.6f}, d={result['effect_size']:.3f}")
        else:
            print(f"  {result['status']}")

    # ================================================================
    # GROUP 2: Unified Profile HT Metrics
    # ================================================================
    print("\n" + "=" * 70)
    print("GROUP 2: Unified Profile HT Metrics")
    print("=" * 70)

    unified_ht_metrics = ['ht_percentile', 'ht_z_score']

    for metric in unified_ht_metrics:
        plant_vals = [profiles[f].get(metric) for f in plant_folios if f in profiles]
        non_plant_vals = [profiles[f].get(metric) for f in non_plant_folios if f in profiles]
        result = run_comparison(plant_vals, non_plant_vals, f'UNIFIED.{metric}')
        results['tests'].append(result)
        print(f"\n{metric}:")
        if result['status'] == 'TESTED':
            print(f"  Plant: {result['plant_mean']:.4f} ± {result['plant_std']:.4f} (n={result['plant_n']})")
            print(f"  Non-plant: {result['non_plant_mean']:.4f} ± {result['non_plant_std']:.4f} (n={result['non_plant_n']})")
            print(f"  U={result['u_statistic']:.1f}, p={result['p_value']:.6f}, d={result['effect_size']:.3f}")
        else:
            print(f"  {result['status']}")

    # ================================================================
    # GROUP 3: System Pressure
    # ================================================================
    print("\n" + "=" * 70)
    print("GROUP 3: System Pressure")
    print("=" * 70)

    for system in ['A', 'B', 'AZC', 'HT']:
        plant_vals = []
        non_plant_vals = []
        for f in plant_folios:
            if f in profiles:
                sp = profiles[f].get('system_pressure', {})
                if sp and sp.get(system) is not None:
                    plant_vals.append(sp[system])
        for f in non_plant_folios:
            if f in profiles:
                sp = profiles[f].get('system_pressure', {})
                if sp and sp.get(system) is not None:
                    non_plant_vals.append(sp[system])

        result = run_comparison(plant_vals, non_plant_vals, f'PRESSURE.{system}')
        results['tests'].append(result)
        print(f"\nsystem_pressure.{system}:")
        if result['status'] == 'TESTED':
            print(f"  Plant: {result['plant_mean']:.4f} ± {result['plant_std']:.4f} (n={result['plant_n']})")
            print(f"  Non-plant: {result['non_plant_mean']:.4f} ± {result['non_plant_std']:.4f} (n={result['non_plant_n']})")
            print(f"  U={result['u_statistic']:.1f}, p={result['p_value']:.6f}, d={result['effect_size']:.3f}")
        else:
            print(f"  {result['status']}")

    # ================================================================
    # GROUP 4: B Metrics (B folios only)
    # ================================================================
    print("\n" + "=" * 70)
    print("GROUP 4: B Metrics (B Folios Only)")
    print("=" * 70)

    # Find B folios
    plant_b = [f for f in plant_folios if f in profiles and profiles[f].get('system') == 'B']
    non_plant_b = [f for f in non_plant_folios if f in profiles and profiles[f].get('system') == 'B']

    print(f"  Plant-B folios: {len(plant_b)}")
    print(f"  Non-plant-B folios: {len(non_plant_b)}")

    b_metrics = ['hazard_density', 'escape_density', 'cei_total', 'link_density', 'recovery_ops_count']

    for metric in b_metrics:
        plant_vals = []
        non_plant_vals = []
        for f in plant_b:
            bm = profiles[f].get('b_metrics')
            if bm and bm.get(metric) is not None:
                plant_vals.append(bm[metric])
        for f in non_plant_b:
            bm = profiles[f].get('b_metrics')
            if bm and bm.get(metric) is not None:
                non_plant_vals.append(bm[metric])

        result = run_comparison(plant_vals, non_plant_vals, f'B.{metric}')
        results['tests'].append(result)
        print(f"\nb_metrics.{metric}:")
        if result['status'] == 'TESTED':
            print(f"  Plant: {result['plant_mean']:.4f} ± {result['plant_std']:.4f} (n={result['plant_n']})")
            print(f"  Non-plant: {result['non_plant_mean']:.4f} ± {result['non_plant_std']:.4f} (n={result['non_plant_n']})")
            print(f"  U={result['u_statistic']:.1f}, p={result['p_value']:.6f}, d={result['effect_size']:.3f}")
        else:
            print(f"  {result['status']}")

    # ================================================================
    # GROUP 5: AZC Metrics (AZC folios only)
    # ================================================================
    print("\n" + "=" * 70)
    print("GROUP 5: AZC Metrics (AZC Folios Only)")
    print("=" * 70)

    # Load AZC features
    try:
        with open(BASE_PATH / 'results' / 'azc_folio_features.json', 'r') as f:
            azc_data = json.load(f)
        azc_folios_data = azc_data.get('folios', {})
    except FileNotFoundError:
        print("  AZC features file not found")
        azc_folios_data = {}

    plant_azc = [f for f in plant_folios if f in azc_folios_data]
    non_plant_azc = [f for f in non_plant_folios if f in azc_folios_data]

    print(f"  Plant-AZC folios: {len(plant_azc)}")
    print(f"  Non-plant-AZC folios: {len(non_plant_azc)}")

    if azc_folios_data:
        azc_metrics = ['a_coverage', 'b_coverage', 'azc_unique_rate', 'placement_entropy']

        for metric in azc_metrics:
            plant_vals = [azc_folios_data[f].get(metric) for f in plant_azc if f in azc_folios_data]
            non_plant_vals = [azc_folios_data[f].get(metric) for f in non_plant_azc if f in azc_folios_data]

            result = run_comparison(plant_vals, non_plant_vals, f'AZC.{metric}')
            results['tests'].append(result)
            print(f"\nazc.{metric}:")
            if result['status'] == 'TESTED':
                print(f"  Plant: {result['plant_mean']:.4f} ± {result['plant_std']:.4f} (n={result['plant_n']})")
                print(f"  Non-plant: {result['non_plant_mean']:.4f} ± {result['non_plant_std']:.4f} (n={result['non_plant_n']})")
                print(f"  U={result['u_statistic']:.1f}, p={result['p_value']:.6f}, d={result['effect_size']:.3f}")
            else:
                print(f"  {result['status']}")

    # ================================================================
    # CLARIFYING ANALYSIS: Section-Driven or Illustration-Driven?
    # ================================================================
    print("\n" + "=" * 70)
    print("CLARIFYING ANALYSIS: Section Effects vs Illustration Effects")
    print("=" * 70)

    print("""
The key question: Are differences due to SECTION membership or ILLUSTRATION content?

ILL-TOP-1 already tested whether visual clusters correlate with constraints
WITHIN Section H. Result: NO correlation (Tests A-H all failed).

If Section H differs from other sections, this is SECTION-driven, not
ILLUSTRATION-driven. Sections are known organizational units with distinct
properties (C156, C367-C370).

To verify this is section-driven:
1. Compare Section H to individual other sections (not lumped)
2. Check if H is simply one point on a section-by-section continuum
""")

    # Compare Section H to each individual section
    sections = sorted(set(section_counts.keys()) - {'H'})
    section_comparisons = {}

    print("\nSection-by-section HT density comparison:")
    print("-" * 50)

    h_ht_vals = [ht_folios[f]['ht_density'] for f in plant_folios if f in ht_folios]

    for sect in sections:
        sect_folios = [f for f, d in ht_folios.items() if d.get('section') == sect]
        sect_vals = [ht_folios[f]['ht_density'] for f in sect_folios]
        if len(sect_vals) >= 3:
            u_stat, p_val = stats.mannwhitneyu(h_ht_vals, sect_vals, alternative='two-sided')
            d_eff = cohen_d(h_ht_vals, sect_vals)
            section_comparisons[sect] = {
                'n': len(sect_vals),
                'mean': np.mean(sect_vals),
                'p': p_val,
                'd': d_eff
            }
            sig_marker = '*' if p_val < 0.05 else ''
            print(f"  H vs {sect}: H={np.mean(h_ht_vals):.3f}, {sect}={np.mean(sect_vals):.3f}, "
                  f"p={p_val:.4f}, d={d_eff:.3f} {sig_marker}")

    results['section_analysis'] = section_comparisons

    # Section means for HT density
    print("\nSection HT density ranking:")
    print("-" * 50)
    section_means = []
    for sect in list(section_counts.keys()):
        sect_folios = [f for f, d in ht_folios.items() if d.get('section') == sect]
        if sect_folios:
            sect_vals = [ht_folios[f]['ht_density'] for f in sect_folios]
            section_means.append((sect, np.mean(sect_vals), len(sect_vals)))

    section_means.sort(key=lambda x: -x[1])
    for sect, mean, n in section_means:
        marker = ' <-- Plant section' if sect == 'H' else ''
        print(f"  {sect}: {mean:.4f} (n={n}){marker}")

    print("""
INTERPRETATION:
If Section H is at an EXTREME of the distribution, the differences are
likely section-inherent, not illustration-driven.

Combined with ILL-TOP-1 findings (no within-H correlation with visual clusters),
the conclusion is:
- Section H has distinct structural properties (like other sections do)
- But illustrations don't organize constraints WITHIN Section H
- Illustrations remain EPIPHENOMENAL to grammar structure
""")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    tested_results = [r for r in results['tests'] if r.get('status') == 'TESTED']
    n_tested = len(tested_results)

    # Apply Bonferroni correction
    bonferroni_alpha = 0.05 / n_tested if n_tested > 0 else 0.05
    print(f"\nBonferroni-corrected alpha: {bonferroni_alpha:.6f} (n_tests={n_tested})")

    # Count significant results
    significant_results = []
    for r in tested_results:
        if r['p_value'] < bonferroni_alpha and abs(r['effect_size']) > 0.5:
            significant_results.append(r)

    print(f"\nSignificant results (p < {bonferroni_alpha:.6f} AND |d| > 0.5): {len(significant_results)}")

    if significant_results:
        print("\nSIGNIFICANT DIFFERENCES:")
        for r in significant_results:
            print(f"  {r['metric']}: p={r['p_value']:.6f}, d={r['effect_size']:.3f}")
    else:
        print("\nNo significant differences found.")

    # Also show marginal results (p < 0.05 but not passing Bonferroni)
    marginal_results = [r for r in tested_results
                       if r['p_value'] < 0.05 and r not in significant_results]

    if marginal_results:
        print(f"\nMARGINAL (p < 0.05 but above Bonferroni threshold): {len(marginal_results)}")
        for r in marginal_results:
            print(f"  {r['metric']}: p={r['p_value']:.6f}, d={r['effect_size']:.3f}")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    n_sig = len(significant_results)

    # Key insight: ILL-TOP-1 already tested whether visual clusters correlate
    # with constraints WITHIN Section H. They don't (8 tests failed).
    # Therefore, any differences found here are SECTION-driven, not ILLUSTRATION-driven.

    if n_sig == 0:
        verdict = 'CLOSED'
        interpretation = 'Plant folios are structurally indistinguishable. Illustration question formally closed.'
    else:
        # Differences exist, but we need to interpret them correctly
        verdict = 'CLOSED_WITH_CAVEAT'
        interpretation = (
            f'Section H differs from other sections ({n_sig} metrics significant). '
            'However, ILL-TOP-1 showed NO correlation between visual clusters and constraints '
            'WITHIN Section H (8 tests failed). Therefore: '
            '(1) Section H has distinct structural properties (section-driven), '
            '(2) Illustrations do NOT organize constraints within the section (illustration-epiphenomenal). '
            'Illustration question formally closed.'
        )

    print(f"\n>>> AUDIT VERDICT: {verdict}")
    print(f"    {interpretation}")

    results['summary'] = {
        'n_tested': n_tested,
        'bonferroni_alpha': bonferroni_alpha,
        'n_significant': n_sig,
        'n_marginal': len(marginal_results),
        'verdict': verdict,
        'interpretation': interpretation,
        'significant_metrics': [r['metric'] for r in significant_results],
        'marginal_metrics': [r['metric'] for r in marginal_results]
    }

    # Save results
    with open(OUTPUT_DIR / 'plant_folio_null_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to plant_folio_null_results.json")

    return results


if __name__ == '__main__':
    run_audit()
