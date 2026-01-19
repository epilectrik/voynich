#!/usr/bin/env python3
"""
bc_04_scaffold_correlation.py - H2: Explanation vs Scaffold Rigidity

Tests H2: Explanation Density Inversely Correlates with Scaffold Rigidity

Prediction: Recipes mapped to UNIFORM scaffolds (Zodiac) have LOWER
explanation density than recipes mapped to VARIED scaffolds (A/C).

Threshold: Mann-Whitney p < 0.05, effect size d > 0.3
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_explanation_density():
    """Load per-recipe explanation density."""
    path = RESULTS_DIR / "bc_explanation_density.json"
    if not path.exists():
        print(f"ERROR: {path} not found - run bc_01 first")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_regime_scaffold_mapping():
    """Load regime to scaffold mapping."""
    path = RESULTS_DIR / "bc_regime_scaffold_mapping.json"
    if not path.exists():
        print(f"ERROR: {path} not found - run bc_02 first")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: H2 - Scaffold Correlation")
    print("=" * 70)
    print()
    print("Prediction: UNIFORM scaffolds have LOWER explanation density than VARIED")
    print("Threshold: Mann-Whitney p < 0.05, effect size d > 0.3")
    print()

    # Load data
    density_data = load_explanation_density()
    scaffold_data = load_regime_scaffold_mapping()

    if not density_data or not scaffold_data:
        return None

    recipes = density_data.get('recipes', [])
    regime_metrics = scaffold_data.get('regime_metrics', {})

    # Classify recipes by scaffold type
    uniform_densities = []
    varied_densities = []

    for recipe in recipes:
        regime = recipe.get('predicted_regime')
        if regime and regime in regime_metrics:
            m6_density = recipe['metrics']['M6_aggregate_density']
            scaffold_type = regime_metrics[regime]['scaffold_pacing_interpretation']

            if scaffold_type == 'UNIFORM':
                uniform_densities.append(m6_density)
            else:
                varied_densities.append(m6_density)

    print(f"UNIFORM scaffold recipes: {len(uniform_densities)}")
    print(f"VARIED scaffold recipes: {len(varied_densities)}")

    if len(uniform_densities) < 5 or len(varied_densities) < 5:
        print("ERROR: Insufficient data for group comparison")
        return None

    # Descriptive statistics
    print("\n" + "-" * 70)
    print("DESCRIPTIVE STATISTICS")
    print("-" * 70)

    print(f"\nUNIFORM scaffolds (Zodiac-like):")
    print(f"  n = {len(uniform_densities)}")
    print(f"  mean = {np.mean(uniform_densities):.4f}")
    print(f"  std = {np.std(uniform_densities):.4f}")

    print(f"\nVARIED scaffolds (A/C-like):")
    print(f"  n = {len(varied_densities)}")
    print(f"  mean = {np.mean(varied_densities):.4f}")
    print(f"  std = {np.std(varied_densities):.4f}")

    # Mann-Whitney U test
    u_stat, pvalue = stats.mannwhitneyu(uniform_densities, varied_densities, alternative='less')

    # Effect size
    d = cohens_d(uniform_densities, varied_densities)

    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    print(f"\nMann-Whitney U (one-sided: UNIFORM < VARIED):")
    print(f"  U = {u_stat:.2f}")
    print(f"  p = {pvalue:.6f}")

    print(f"\nCohen's d effect size:")
    print(f"  d = {d:.4f}")
    print(f"  Interpretation: {'small' if abs(d) < 0.5 else 'medium' if abs(d) < 0.8 else 'large'}")

    # Direction check
    mean_diff = np.mean(uniform_densities) - np.mean(varied_densities)
    if mean_diff < 0:
        direction = "CORRECT (UNIFORM < VARIED, as predicted)"
    else:
        direction = "OPPOSITE (UNIFORM > VARIED, opposite prediction)"

    print(f"\nDirection: {direction}")
    print(f"  Mean difference: {mean_diff:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    significance = pvalue < 0.05
    effect_threshold = abs(d) > 0.3
    correct_direction = mean_diff < 0

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p = {pvalue:.6f}")

    print(f"\nEffect size (|d| > 0.3): {'PASS' if effect_threshold else 'FAIL'}")
    print(f"  d = {d:.4f}")

    print(f"\nCorrect direction (UNIFORM < VARIED): {'PASS' if correct_direction else 'FAIL'}")

    passed = significance and effect_threshold and correct_direction

    print("\n" + "-" * 70)
    print(f"H2 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    if passed:
        print("\nInterpretation: UNIFORM scaffolds have lower explanation density.")
        print("Where scaffold is rigid (Zodiac-like), Brunschwig explains less.")
    else:
        print("\nInterpretation: No significant difference by scaffold type.")
        print("Explanation density does not vary with scaffold rigidity.")

    # Save results
    output = {
        'hypothesis': 'H2',
        'name': 'Explanation vs Scaffold Rigidity',
        'prediction': 'UNIFORM scaffolds have LOWER explanation density than VARIED',
        'threshold': 'Mann-Whitney p < 0.05, effect size d > 0.3',
        'group_sizes': {
            'uniform': len(uniform_densities),
            'varied': len(varied_densities)
        },
        'descriptive': {
            'uniform': {
                'mean': round(float(np.mean(uniform_densities)), 4),
                'std': round(float(np.std(uniform_densities)), 4)
            },
            'varied': {
                'mean': round(float(np.mean(varied_densities)), 4),
                'std': round(float(np.std(varied_densities)), 4)
            }
        },
        'statistics': {
            'mann_whitney_u': round(float(u_stat), 2),
            'p_value': round(float(pvalue), 6),
            'cohens_d': round(float(d), 4),
            'mean_difference': round(float(mean_diff), 4)
        },
        'evaluation': {
            'significant': bool(significance),
            'effect_threshold_met': bool(effect_threshold),
            'correct_direction': bool(correct_direction),
            'passed': bool(passed)
        }
    }

    output_path = RESULTS_DIR / "bc_scaffold_correlation.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
