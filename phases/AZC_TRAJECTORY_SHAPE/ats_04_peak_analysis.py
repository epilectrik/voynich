#!/usr/bin/env python3
"""
ats_04_peak_analysis.py - H4: Peak Count Differs by Family

Tests whether A/C has more entropy peaks (>= 1.5) than Zodiac (< 1.0).

Threshold: Poisson rate ratio >= 2.0
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


def count_local_maxima(trajectory):
    """Count peaks (local maxima) in trajectory."""
    if len(trajectory) < 3:
        return 0

    peaks = 0
    for i in range(1, len(trajectory) - 1):
        if trajectory[i] > trajectory[i-1] and trajectory[i] > trajectory[i+1]:
            peaks += 1

    return peaks


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H4 - Peak Count Differs")
    print("=" * 70)
    print()
    print("Prediction: A/C has more peaks (>= 1.5) than Zodiac (< 1.0)")
    print("Threshold: Poisson rate ratio >= 2.0")
    print()

    # Load folio features
    features_path = RESULTS_DIR / "azc_folio_features.json"
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    folios = data['folios']

    # Count peaks by family
    zodiac_peaks = []
    ac_peaks = []
    folio_results = []

    for folio_id, folio_data in folios.items():
        placement = folio_data.get('placement_vector', {})

        if folio_id in ZODIAC_FAMILY:
            family = 'zodiac'
            trajectory = compute_zone_trajectory(placement, ZODIAC_ZONES)
            peaks = count_local_maxima(trajectory)
            zodiac_peaks.append(peaks)
        elif folio_id in AC_FAMILY:
            family = 'ac'
            trajectory = compute_zone_trajectory(placement, AC_ZONES)
            peaks = count_local_maxima(trajectory)
            ac_peaks.append(peaks)
        else:
            family = 'unknown'
            peaks = 0

        folio_results.append({
            'folio': folio_id,
            'family': family,
            'peak_count': peaks,
        })

    # Results
    print("-" * 70)
    print("RESULTS BY FAMILY")
    print("-" * 70)

    zodiac_mean = np.mean(zodiac_peaks) if zodiac_peaks else 0
    ac_mean = np.mean(ac_peaks) if ac_peaks else 0

    print(f"\nZodiac (n={len(zodiac_peaks)}):")
    print(f"  Mean peaks: {zodiac_mean:.4f}")
    print(f"  Peak distribution: {dict(zip(*np.unique(zodiac_peaks, return_counts=True)))}")

    print(f"\nA/C (n={len(ac_peaks)}):")
    print(f"  Mean peaks: {ac_mean:.4f}")
    print(f"  Peak distribution: {dict(zip(*np.unique(ac_peaks, return_counts=True)))}")

    # Poisson rate ratio
    rate_ratio = ac_mean / zodiac_mean if zodiac_mean > 0 else float('inf')
    print(f"\nPoisson rate ratio (A/C / Zodiac): {rate_ratio:.4f}")

    # Statistical test
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    u_stat, u_pvalue = stats.mannwhitneyu(zodiac_peaks, ac_peaks, alternative='two-sided')
    print(f"\nMann-Whitney U:")
    print(f"  U = {u_stat:.4f}, p = {u_pvalue:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    zodiac_meets = zodiac_mean < 1.0
    ac_meets = ac_mean >= 1.5
    rate_ratio_met = rate_ratio >= 2.0

    print(f"\nZodiac mean < 1.0: {'PASS' if zodiac_meets else 'FAIL'}")
    print(f"  Mean peaks: {zodiac_mean:.4f}")

    print(f"\nA/C mean >= 1.5: {'PASS' if ac_meets else 'FAIL'}")
    print(f"  Mean peaks: {ac_mean:.4f}")

    print(f"\nRate ratio >= 2.0: {'PASS' if rate_ratio_met else 'FAIL'}")
    print(f"  Rate ratio: {rate_ratio:.4f}")

    passed = rate_ratio_met
    print("\n" + "-" * 70)
    print(f"H4 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H4',
        'name': 'Peak Count Differs',
        'prediction': 'A/C >= 1.5 peaks, Zodiac < 1.0 peaks',
        'threshold': 'Poisson rate ratio >= 2.0',
        'zodiac': {
            'n': len(zodiac_peaks),
            'mean_peaks': float(zodiac_mean),
            'peaks': zodiac_peaks,
        },
        'ac': {
            'n': len(ac_peaks),
            'mean_peaks': float(ac_mean),
            'peaks': ac_peaks,
        },
        'rate_ratio': float(rate_ratio) if rate_ratio != float('inf') else None,
        'statistics': {
            'u_statistic': float(u_stat),
            'u_pvalue': float(u_pvalue),
        },
        'evaluation': {
            'zodiac_meets_threshold': bool(zodiac_meets),
            'ac_meets_threshold': bool(ac_meets),
            'rate_ratio_met': bool(rate_ratio_met),
            'passed': bool(passed),
        },
        'folio_details': folio_results,
    }

    output_path = RESULTS_DIR / "ats_peak_analysis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
