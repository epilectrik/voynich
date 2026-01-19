#!/usr/bin/env python3
"""
ats_02_monotonicity.py - H2: Monotonicity Differs by Family

Tests whether Zodiac shows steady decline (rho < -0.7) while A/C shows oscillation (|rho| < 0.5).

Threshold: Mann-Whitney p < 0.05
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

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

ZODIAC_ZONES = ['R1', 'R2', 'R3', 'S1', 'S2']
AC_ZONES = ['C', 'P', 'R', 'S']


def compute_zone_trajectory(placement_vector, zones):
    """Extract zone values in order."""
    return [placement_vector.get(zone, 0.0) for zone in zones]


def compute_monotonicity(trajectory):
    """Compute Spearman correlation with position (monotonicity measure)."""
    if len(trajectory) < 3:
        return np.nan, np.nan

    positions = np.arange(len(trajectory))
    values = np.array(trajectory)

    # Skip if constant
    if np.std(values) == 0:
        return 0.0, 1.0

    rho, p = stats.spearmanr(positions, values)
    return rho, p


def classify_monotonicity(rho):
    """Classify trajectory shape based on monotonicity."""
    if np.isnan(rho):
        return 'UNDEFINED'
    if rho < -0.7:
        return 'STEADY_DECLINE'
    elif rho < -0.3:
        return 'WEAK_DECLINE'
    elif rho <= 0.3:
        return 'OSCILLATORY'
    elif rho <= 0.7:
        return 'WEAK_INCREASE'
    else:
        return 'STEADY_INCREASE'


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H2 - Monotonicity Differs")
    print("=" * 70)
    print()
    print("Prediction: Zodiac rho < -0.7 (steady decline), A/C |rho| < 0.5 (oscillatory)")
    print("Threshold: Mann-Whitney p < 0.05")
    print()

    # Load folio features
    features_path = RESULTS_DIR / "azc_folio_features.json"
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    folios = data['folios']

    # Compute monotonicity by family
    zodiac_rhos = []
    ac_rhos = []
    folio_results = []

    for folio_id, folio_data in folios.items():
        placement = folio_data.get('placement_vector', {})

        if folio_id in ZODIAC_FAMILY:
            family = 'zodiac'
            trajectory = compute_zone_trajectory(placement, ZODIAC_ZONES)
            rho, p = compute_monotonicity(trajectory)
            if not np.isnan(rho):
                zodiac_rhos.append(rho)
        elif folio_id in AC_FAMILY:
            family = 'ac'
            trajectory = compute_zone_trajectory(placement, AC_ZONES)
            rho, p = compute_monotonicity(trajectory)
            if not np.isnan(rho):
                ac_rhos.append(rho)
        else:
            family = 'unknown'
            rho, p = np.nan, np.nan

        classification = classify_monotonicity(rho)
        folio_results.append({
            'folio': folio_id,
            'family': family,
            'rho': rho if not np.isnan(rho) else None,
            'classification': classification,
        })

    # Results
    print("-" * 70)
    print("RESULTS BY FAMILY")
    print("-" * 70)

    print(f"\nZodiac (n={len(zodiac_rhos)}):")
    print(f"  Mean rho: {np.mean(zodiac_rhos):.4f}")
    print(f"  Std rho:  {np.std(zodiac_rhos):.4f}")
    zodiac_steady = sum(1 for r in zodiac_rhos if r < -0.7)
    print(f"  Steady decline (rho < -0.7): {zodiac_steady}/{len(zodiac_rhos)}")

    print(f"\nA/C (n={len(ac_rhos)}):")
    print(f"  Mean rho: {np.mean(ac_rhos):.4f}")
    print(f"  Std rho:  {np.std(ac_rhos):.4f}")
    ac_oscillatory = sum(1 for r in ac_rhos if abs(r) < 0.5)
    print(f"  Oscillatory (|rho| < 0.5): {ac_oscillatory}/{len(ac_rhos)}")

    # Statistical test
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    u_stat, u_pvalue = stats.mannwhitneyu(zodiac_rhos, ac_rhos, alternative='two-sided')
    print(f"\nMann-Whitney U:")
    print(f"  U = {u_stat:.4f}, p = {u_pvalue:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    zodiac_meets = np.mean(zodiac_rhos) < -0.7
    ac_meets = abs(np.mean(ac_rhos)) < 0.5
    significance = u_pvalue < 0.05

    print(f"\nZodiac mean rho < -0.7: {'PASS' if zodiac_meets else 'FAIL'}")
    print(f"  Mean rho: {np.mean(zodiac_rhos):.4f}")

    print(f"\nA/C |mean rho| < 0.5: {'PASS' if ac_meets else 'FAIL'}")
    print(f"  Mean |rho|: {abs(np.mean(ac_rhos)):.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value: {u_pvalue:.4f}")

    # Final verdict - need significance AND family patterns
    passed = significance and (zodiac_meets or ac_meets)
    print("\n" + "-" * 70)
    print(f"H2 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H2',
        'name': 'Monotonicity Differs',
        'prediction': 'Zodiac rho < -0.7, A/C |rho| < 0.5',
        'threshold': 'Mann-Whitney p < 0.05',
        'zodiac': {
            'n': len(zodiac_rhos),
            'mean_rho': float(np.mean(zodiac_rhos)),
            'std_rho': float(np.std(zodiac_rhos)),
            'steady_decline_count': zodiac_steady,
            'rhos': [float(r) for r in zodiac_rhos],
        },
        'ac': {
            'n': len(ac_rhos),
            'mean_rho': float(np.mean(ac_rhos)),
            'std_rho': float(np.std(ac_rhos)),
            'oscillatory_count': ac_oscillatory,
            'rhos': [float(r) for r in ac_rhos],
        },
        'statistics': {
            'u_statistic': float(u_stat),
            'u_pvalue': float(u_pvalue),
        },
        'evaluation': {
            'zodiac_meets_threshold': bool(zodiac_meets),
            'ac_meets_threshold': bool(ac_meets),
            'significant': bool(significance),
            'passed': bool(passed),
        },
        'folio_details': folio_results,
    }

    output_path = RESULTS_DIR / "ats_monotonicity.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
