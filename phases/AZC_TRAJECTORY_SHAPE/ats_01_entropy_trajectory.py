#!/usr/bin/env python3
"""
ats_01_entropy_trajectory.py - H1: Entropy Trajectory Slope Differs by Family

Tests whether Zodiac and A/C families have different entropy trajectory slopes.
Prediction: Zodiac has more negative slope (widening->narrowing) than A/C.

Threshold: Cohen's d >= 0.5, p < 0.05
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Family definitions (canonical)
ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

# Zone ordering for each family
ZODIAC_ZONES = ['R1', 'R2', 'R3', 'S1', 'S2']
AC_ZONES = ['C', 'P', 'R', 'S']


def compute_zone_trajectory(placement_vector, zones):
    """Extract zone values in order, returning trajectory."""
    trajectory = []
    for zone in zones:
        val = placement_vector.get(zone, 0.0)
        trajectory.append(val)
    return trajectory


def compute_entropy_slope(trajectory):
    """Fit linear regression to trajectory, return slope."""
    if len(trajectory) < 2:
        return np.nan, np.nan, np.nan

    x = np.arange(len(trajectory))
    y = np.array(trajectory)

    # Skip if all zeros or constant
    if np.std(y) == 0:
        return 0.0, 0.0, 1.0

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, r_value**2, p_value


def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))

    if pooled_std == 0:
        return 0.0

    return (np.mean(group1) - np.mean(group2)) / pooled_std


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H1 - Entropy Trajectory Slope")
    print("=" * 70)
    print()
    print("Prediction: Zodiac has more negative slope than A/C")
    print("Threshold: Cohen's d >= 0.5, p < 0.05")
    print()

    # Load folio features
    features_path = RESULTS_DIR / "azc_folio_features.json"
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    folios = data['folios']

    # Compute slopes by family
    zodiac_slopes = []
    ac_slopes = []
    folio_results = []

    for folio_id, folio_data in folios.items():
        placement = folio_data.get('placement_vector', {})

        if folio_id in ZODIAC_FAMILY:
            family = 'zodiac'
            trajectory = compute_zone_trajectory(placement, ZODIAC_ZONES)
            slope, r2, p = compute_entropy_slope(trajectory)
            if not np.isnan(slope):
                zodiac_slopes.append(slope)
        elif folio_id in AC_FAMILY:
            family = 'ac'
            trajectory = compute_zone_trajectory(placement, AC_ZONES)
            slope, r2, p = compute_entropy_slope(trajectory)
            if not np.isnan(slope):
                ac_slopes.append(slope)
        else:
            family = 'unknown'
            trajectory = []
            slope, r2, p = np.nan, np.nan, np.nan

        folio_results.append({
            'folio': folio_id,
            'family': family,
            'trajectory': trajectory,
            'slope': slope if not np.isnan(slope) else None,
            'r_squared': r2 if not np.isnan(r2) else None,
        })

    # Statistical comparison
    print("-" * 70)
    print("RESULTS BY FAMILY")
    print("-" * 70)

    print(f"\nZodiac (n={len(zodiac_slopes)}):")
    print(f"  Mean slope: {np.mean(zodiac_slopes):.4f}")
    print(f"  Std slope:  {np.std(zodiac_slopes):.4f}")

    print(f"\nA/C (n={len(ac_slopes)}):")
    print(f"  Mean slope: {np.mean(ac_slopes):.4f}")
    print(f"  Std slope:  {np.std(ac_slopes):.4f}")

    # Statistical tests
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    # t-test
    t_stat, t_pvalue = stats.ttest_ind(zodiac_slopes, ac_slopes)
    print(f"\nIndependent t-test:")
    print(f"  t = {t_stat:.4f}, p = {t_pvalue:.4f}")

    # Mann-Whitney U (non-parametric)
    u_stat, u_pvalue = stats.mannwhitneyu(zodiac_slopes, ac_slopes, alternative='two-sided')
    print(f"\nMann-Whitney U:")
    print(f"  U = {u_stat:.4f}, p = {u_pvalue:.4f}")

    # Cohen's d
    d = cohens_d(zodiac_slopes, ac_slopes)
    print(f"\nCohen's d: {d:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    # Check prediction direction: Zodiac should be more negative
    direction_correct = np.mean(zodiac_slopes) < np.mean(ac_slopes)
    significance = t_pvalue < 0.05
    effect_size = abs(d) >= 0.5

    print(f"\nPrediction (Zodiac more negative): {'CORRECT' if direction_correct else 'INCORRECT'}")
    print(f"  Zodiac mean: {np.mean(zodiac_slopes):.4f}")
    print(f"  A/C mean:    {np.mean(ac_slopes):.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value: {t_pvalue:.4f}")

    print(f"\nEffect size (|d| >= 0.5): {'PASS' if effect_size else 'FAIL'}")
    print(f"  Cohen's d: {d:.4f}")

    # Final verdict
    passed = direction_correct and significance and effect_size
    print("\n" + "-" * 70)
    print(f"H1 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H1',
        'name': 'Entropy Trajectory Slope Differs',
        'prediction': 'Zodiac has more negative slope than A/C',
        'threshold': 'Cohen\'s d >= 0.5, p < 0.05',
        'zodiac': {
            'n': len(zodiac_slopes),
            'mean_slope': float(np.mean(zodiac_slopes)),
            'std_slope': float(np.std(zodiac_slopes)),
            'slopes': [float(s) for s in zodiac_slopes],
        },
        'ac': {
            'n': len(ac_slopes),
            'mean_slope': float(np.mean(ac_slopes)),
            'std_slope': float(np.std(ac_slopes)),
            'slopes': [float(s) for s in ac_slopes],
        },
        'statistics': {
            't_statistic': float(t_stat),
            't_pvalue': float(t_pvalue),
            'u_statistic': float(u_stat),
            'u_pvalue': float(u_pvalue),
            'cohens_d': float(d),
        },
        'evaluation': {
            'direction_correct': bool(direction_correct),
            'significant': bool(significance),
            'effect_size_met': bool(effect_size),
            'passed': bool(passed),
        },
        'folio_details': folio_results,
    }

    output_path = RESULTS_DIR / "ats_entropy_trajectory.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
