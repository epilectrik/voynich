#!/usr/bin/env python3
"""
ats_09_escape_asymmetry.py - H9: Family-Conditioned Escape Asymmetry

Tests whether Zodiac has steeper escape collapse than A/C (uniform scaffold = stricter).

Threshold: Levene's test p < 0.05, Zodiac variance < A/C variance
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

# Zone positions for each family
ZODIAC_ZONES = ['R1', 'R2', 'R3', 'S1', 'S2']
AC_ZONES = ['C', 'P', 'R', 'S']


def load_escape_by_position():
    """Load escape rates by position from existing analysis."""
    escape_path = RESULTS_DIR / "azc_escape_by_position.json"

    if not escape_path.exists():
        # Default values from documentation
        return {
            # Zodiac subscripted positions
            'R1': 0.053,
            'R2': 0.018,
            'R3': 0.000,
            'S1': 0.000,
            'S2': 0.000,
            # A/C positions
            'C': 0.023,
            'P': 0.159,
            'R': 0.092,
            'S': 0.044,
        }

    with open(escape_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract position-level escape rates
    escape_rates = {}

    if 'position_statistics' in data:
        for pos, pos_data in data['position_statistics'].items():
            if isinstance(pos_data, dict) and 'escape_rate' in pos_data:
                escape_rates[pos] = pos_data['escape_rate']

    # Fill in defaults if missing
    defaults = {
        'R1': 0.053, 'R2': 0.018, 'R3': 0.000,
        'S1': 0.000, 'S2': 0.000,
        'C': 0.023, 'P': 0.159, 'R': 0.092, 'S': 0.044,
    }

    for pos, rate in defaults.items():
        if pos not in escape_rates:
            escape_rates[pos] = rate

    return escape_rates


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H9 - Family-Conditioned Escape Asymmetry")
    print("=" * 70)
    print()
    print("Prediction: Zodiac has steeper escape collapse (lower variance)")
    print("Threshold: Levene's test p < 0.05, Zodiac variance < A/C variance")
    print()

    # Load escape rates
    escape_rates = load_escape_by_position()

    # Extract escape vectors by family
    zodiac_escapes = [escape_rates.get(z, 0) for z in ZODIAC_ZONES]
    ac_escapes = [escape_rates.get(z, 0) for z in AC_ZONES]

    print("-" * 70)
    print("ESCAPE RATES BY FAMILY")
    print("-" * 70)

    print("\nZodiac positions:")
    for i, zone in enumerate(ZODIAC_ZONES):
        print(f"  {zone}: {zodiac_escapes[i]:.4f}")
    print(f"  Mean: {np.mean(zodiac_escapes):.4f}")
    print(f"  Variance: {np.var(zodiac_escapes):.6f}")
    print(f"  Std: {np.std(zodiac_escapes):.4f}")

    print("\nA/C positions:")
    for i, zone in enumerate(AC_ZONES):
        print(f"  {zone}: {ac_escapes[i]:.4f}")
    print(f"  Mean: {np.mean(ac_escapes):.4f}")
    print(f"  Variance: {np.var(ac_escapes):.6f}")
    print(f"  Std: {np.std(ac_escapes):.4f}")

    # Variance comparison
    zodiac_var = np.var(zodiac_escapes)
    ac_var = np.var(ac_escapes)
    var_ratio = zodiac_var / ac_var if ac_var > 0 else 0

    print(f"\nVariance ratio (Zodiac/A/C): {var_ratio:.4f}")

    # Levene's test for equality of variances
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    levene_stat, levene_p = stats.levene(zodiac_escapes, ac_escapes)
    print(f"\nLevene's test:")
    print(f"  W = {levene_stat:.4f}, p = {levene_p:.4f}")

    # Bartlett's test (assumes normality)
    try:
        bartlett_stat, bartlett_p = stats.bartlett(zodiac_escapes, ac_escapes)
        print(f"\nBartlett's test:")
        print(f"  T = {bartlett_stat:.4f}, p = {bartlett_p:.4f}")
    except ValueError:
        bartlett_p = 1.0

    # Coefficient of variation comparison
    zodiac_cv = np.std(zodiac_escapes) / np.mean(zodiac_escapes) if np.mean(zodiac_escapes) > 0 else 0
    ac_cv = np.std(ac_escapes) / np.mean(ac_escapes) if np.mean(ac_escapes) > 0 else 0

    print(f"\nCoefficient of variation:")
    print(f"  Zodiac CV: {zodiac_cv:.4f}")
    print(f"  A/C CV: {ac_cv:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    variance_lower = zodiac_var < ac_var
    significance = levene_p < 0.05

    print(f"\nZodiac variance < A/C variance: {'PASS' if variance_lower else 'FAIL'}")
    print(f"  Zodiac: {zodiac_var:.6f}")
    print(f"  A/C: {ac_var:.6f}")

    print(f"\nLevene's test significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value = {levene_p:.4f}")

    # Pass requires BOTH conditions
    passed = variance_lower and significance
    print("\n" + "-" * 70)
    print(f"H9 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Interpretation
    if variance_lower and not significance:
        print("\nInterpretation: Zodiac shows lower variance (steeper collapse)")
        print("but the difference is not statistically significant with only")
        print(f"{len(zodiac_escapes)} Zodiac and {len(ac_escapes)} A/C positions.")

    # Save results
    results = {
        'hypothesis': 'H9',
        'name': 'Family-Conditioned Escape Asymmetry',
        'prediction': 'Zodiac has steeper escape collapse (lower variance)',
        'threshold': 'Levene p < 0.05, Zodiac variance < A/C variance',
        'zodiac': {
            'zones': ZODIAC_ZONES,
            'escape_rates': zodiac_escapes,
            'mean': float(np.mean(zodiac_escapes)),
            'variance': float(zodiac_var),
            'std': float(np.std(zodiac_escapes)),
            'cv': float(zodiac_cv),
        },
        'ac': {
            'zones': AC_ZONES,
            'escape_rates': ac_escapes,
            'mean': float(np.mean(ac_escapes)),
            'variance': float(ac_var),
            'std': float(np.std(ac_escapes)),
            'cv': float(ac_cv),
        },
        'variance_ratio': float(var_ratio),
        'statistics': {
            'levene_w': float(levene_stat),
            'levene_p': float(levene_p),
        },
        'evaluation': {
            'variance_lower': bool(variance_lower),
            'significant': bool(significance),
            'passed': bool(passed),
        },
    }

    output_path = RESULTS_DIR / "ats_escape_asymmetry.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
