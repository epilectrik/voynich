#!/usr/bin/env python3
"""
bc_03_freedom_correlation.py - H1: Explanation vs Judgment Freedom

Tests H1: Explanation Density Inversely Correlates with Judgment Freedom

Prediction: Recipes mapped to LOW judgment freedom zones have LOWER
explanation density than recipes mapped to HIGH freedom zones.

Threshold: Spearman rho < -0.3, p < 0.05
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


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: H1 - Freedom Correlation")
    print("=" * 70)
    print()
    print("Prediction: Explanation density inversely correlates with judgment freedom")
    print("Threshold: Spearman rho < -0.3, p < 0.05")
    print()

    # Load data
    density_data = load_explanation_density()
    scaffold_data = load_regime_scaffold_mapping()

    if not density_data or not scaffold_data:
        return None

    recipes = density_data.get('recipes', [])
    regime_metrics = scaffold_data.get('regime_metrics', {})

    print(f"Loaded {len(recipes)} recipes with explanation density")
    print(f"Loaded {len(regime_metrics)} regime scaffold mappings")

    # Pair each recipe's explanation density with its regime's judgment freedom
    paired_data = []

    for recipe in recipes:
        regime = recipe.get('predicted_regime')
        if regime and regime in regime_metrics:
            m6_density = recipe['metrics']['M6_aggregate_density']
            freedom = regime_metrics[regime]['judgment_freedom_index']
            paired_data.append({
                'recipe_id': recipe['recipe_id'],
                'regime': regime,
                'explanation_density': m6_density,
                'judgment_freedom': freedom
            })

    print(f"\nPaired {len(paired_data)} recipes with scaffold metrics")

    if len(paired_data) < 10:
        print("ERROR: Insufficient data for correlation analysis")
        return None

    # Extract arrays for correlation
    densities = np.array([d['explanation_density'] for d in paired_data])
    freedoms = np.array([d['judgment_freedom'] for d in paired_data])

    # Spearman correlation
    rho, pvalue = stats.spearmanr(freedoms, densities)

    print("\n" + "-" * 70)
    print("CORRELATION ANALYSIS")
    print("-" * 70)

    print(f"\nSpearman correlation:")
    print(f"  rho = {rho:.4f}")
    print(f"  p-value = {pvalue:.6f}")

    # Interpretation
    if rho < 0:
        direction = "NEGATIVE (as predicted: more freedom -> less explanation)"
    else:
        direction = "POSITIVE (opposite prediction: more freedom -> more explanation)"

    print(f"\nDirection: {direction}")

    # By-regime breakdown
    print("\n" + "-" * 70)
    print("BY-REGIME BREAKDOWN")
    print("-" * 70)

    regime_stats = {}
    for regime in sorted(regime_metrics.keys()):
        regime_recipes = [d for d in paired_data if d['regime'] == regime]
        if regime_recipes:
            regime_densities = [r['explanation_density'] for r in regime_recipes]
            freedom = regime_metrics[regime]['judgment_freedom_index']
            regime_stats[regime] = {
                'n': len(regime_recipes),
                'freedom': freedom,
                'mean_density': np.mean(regime_densities),
                'std_density': np.std(regime_densities)
            }
            print(f"\n{regime} (freedom={freedom:.3f}):")
            print(f"  n={len(regime_recipes)}, mean_density={np.mean(regime_densities):.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    rho_threshold = rho < -0.3
    significance = pvalue < 0.05

    print(f"\nSpearman rho < -0.3: {'PASS' if rho_threshold else 'FAIL'}")
    print(f"  rho = {rho:.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p = {pvalue:.6f}")

    passed = rho_threshold and significance

    print("\n" + "-" * 70)
    print(f"H1 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    if passed:
        print("\nInterpretation: Where judgment freedom is LOW, Brunschwig explains MORE.")
        print("This supports explanation-enforcement complementarity.")
    else:
        print("\nInterpretation: No significant inverse correlation found.")
        print("Explanation density does not systematically vary with judgment freedom.")

    # Save results
    output = {
        'hypothesis': 'H1',
        'name': 'Explanation vs Judgment Freedom Correlation',
        'prediction': 'Explanation density inversely correlates with judgment freedom',
        'threshold': 'Spearman rho < -0.3, p < 0.05',
        'n_recipes': len(paired_data),
        'statistics': {
            'spearman_rho': round(float(rho), 4),
            'p_value': round(float(pvalue), 6),
            'direction': 'negative' if rho < 0 else 'positive'
        },
        'evaluation': {
            'rho_threshold_met': bool(rho_threshold),
            'significant': bool(significance),
            'passed': bool(passed)
        },
        'by_regime': regime_stats,
        'paired_data_sample': paired_data[:10]  # First 10 for inspection
    }

    output_path = RESULTS_DIR / "bc_freedom_correlation.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
