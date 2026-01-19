#!/usr/bin/env python3
"""
ats_03_terminal_compression.py - H3: Terminal Compression Ratio Differs

Tests whether Zodiac has sharper collapse (lower final/peak ratio) than A/C.

Threshold: Difference >= 0.2, p < 0.05
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


def compute_terminal_compression(trajectory):
    """Compute ratio of final zone value to peak value."""
    if len(trajectory) < 2:
        return np.nan

    peak = max(trajectory)
    final = trajectory[-1]

    if peak == 0:
        return np.nan

    return final / peak


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H3 - Terminal Compression Ratio")
    print("=" * 70)
    print()
    print("Prediction: Zodiac has lower compression ratio (sharper collapse)")
    print("Threshold: Difference >= 0.2, p < 0.05")
    print()

    # Load folio features
    features_path = RESULTS_DIR / "azc_folio_features.json"
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    folios = data['folios']

    # Compute compression ratios by family
    zodiac_ratios = []
    ac_ratios = []
    folio_results = []

    for folio_id, folio_data in folios.items():
        placement = folio_data.get('placement_vector', {})

        if folio_id in ZODIAC_FAMILY:
            family = 'zodiac'
            trajectory = compute_zone_trajectory(placement, ZODIAC_ZONES)
            ratio = compute_terminal_compression(trajectory)
            if not np.isnan(ratio):
                zodiac_ratios.append(ratio)
        elif folio_id in AC_FAMILY:
            family = 'ac'
            trajectory = compute_zone_trajectory(placement, AC_ZONES)
            ratio = compute_terminal_compression(trajectory)
            if not np.isnan(ratio):
                ac_ratios.append(ratio)
        else:
            family = 'unknown'
            ratio = np.nan

        folio_results.append({
            'folio': folio_id,
            'family': family,
            'compression_ratio': ratio if not np.isnan(ratio) else None,
        })

    # Results
    print("-" * 70)
    print("RESULTS BY FAMILY")
    print("-" * 70)

    print(f"\nZodiac (n={len(zodiac_ratios)}):")
    print(f"  Mean ratio: {np.mean(zodiac_ratios):.4f}")
    print(f"  Std ratio:  {np.std(zodiac_ratios):.4f}")

    print(f"\nA/C (n={len(ac_ratios)}):")
    print(f"  Mean ratio: {np.mean(ac_ratios):.4f}")
    print(f"  Std ratio:  {np.std(ac_ratios):.4f}")

    difference = np.mean(ac_ratios) - np.mean(zodiac_ratios)
    print(f"\nDifference (A/C - Zodiac): {difference:.4f}")

    # Statistical tests
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    t_stat, t_pvalue = stats.ttest_ind(zodiac_ratios, ac_ratios)
    print(f"\nIndependent t-test:")
    print(f"  t = {t_stat:.4f}, p = {t_pvalue:.4f}")

    u_stat, u_pvalue = stats.mannwhitneyu(zodiac_ratios, ac_ratios, alternative='two-sided')
    print(f"\nMann-Whitney U:")
    print(f"  U = {u_stat:.4f}, p = {u_pvalue:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    direction_correct = np.mean(zodiac_ratios) < np.mean(ac_ratios)
    difference_met = difference >= 0.2
    significance = t_pvalue < 0.05

    print(f"\nDirection (Zodiac < A/C): {'CORRECT' if direction_correct else 'INCORRECT'}")
    print(f"  Zodiac mean: {np.mean(zodiac_ratios):.4f}")
    print(f"  A/C mean:    {np.mean(ac_ratios):.4f}")

    print(f"\nDifference >= 0.2: {'PASS' if difference_met else 'FAIL'}")
    print(f"  Difference: {difference:.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value: {t_pvalue:.4f}")

    passed = direction_correct and difference_met and significance
    print("\n" + "-" * 70)
    print(f"H3 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H3',
        'name': 'Terminal Compression Ratio Differs',
        'prediction': 'Zodiac has lower ratio (sharper collapse)',
        'threshold': 'Difference >= 0.2, p < 0.05',
        'zodiac': {
            'n': len(zodiac_ratios),
            'mean_ratio': float(np.mean(zodiac_ratios)),
            'std_ratio': float(np.std(zodiac_ratios)),
            'ratios': [float(r) for r in zodiac_ratios],
        },
        'ac': {
            'n': len(ac_ratios),
            'mean_ratio': float(np.mean(ac_ratios)),
            'std_ratio': float(np.std(ac_ratios)),
            'ratios': [float(r) for r in ac_ratios],
        },
        'difference': float(difference),
        'statistics': {
            't_statistic': float(t_stat),
            't_pvalue': float(t_pvalue),
            'u_statistic': float(u_stat),
            'u_pvalue': float(u_pvalue),
        },
        'evaluation': {
            'direction_correct': bool(direction_correct),
            'difference_met': bool(difference_met),
            'significant': bool(significance),
            'passed': bool(passed),
        },
        'folio_details': folio_results,
    }

    output_path = RESULTS_DIR / "ats_terminal_compression.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
