#!/usr/bin/env python3
"""
bc_06_complementarity_ratio.py - H4: Complementarity Ratio

Tests H4: Brunschwig verbosity / Voynich constraint shows consistent
inverse relationship.

Prediction: Per-recipe complementarity score (explanation_density / (1 - freedom))
should show low variance if the systems truly partition responsibility.

Threshold: Ratio variance < baseline expectation, chi-squared p < 0.05
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
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_regime_scaffold_mapping():
    """Load regime to scaffold mapping."""
    path = RESULTS_DIR / "bc_regime_scaffold_mapping.json"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: H4 - Complementarity Ratio")
    print("=" * 70)
    print()
    print("Prediction: explanation_density / (1 - freedom) should be stable")
    print("Threshold: Ratio variance < baseline, chi-squared p < 0.05")
    print()

    # Load data
    density_data = load_explanation_density()
    scaffold_data = load_regime_scaffold_mapping()

    if not density_data or not scaffold_data:
        print("ERROR: Required data files not found")
        return None

    recipes = density_data.get('recipes', [])
    regime_metrics = scaffold_data.get('regime_metrics', {})

    # Compute complementarity ratio for each recipe
    # Ratio = explanation_density / constraint_strength
    # Where constraint_strength = 1 - judgment_freedom
    # Higher freedom = lower constraint = should have LOWER explanation density
    # So ratio = density / (1 - freedom) should be stable if they complement

    ratios = []
    by_regime = {}

    for recipe in recipes:
        regime = recipe.get('predicted_regime')
        if regime and regime in regime_metrics:
            density = recipe['metrics']['M6_aggregate_density']
            freedom = regime_metrics[regime]['judgment_freedom_index']

            # Constraint strength = 1 - freedom
            constraint = 1 - freedom

            # Avoid division by zero
            if constraint > 0.01:
                ratio = density / constraint
                ratios.append({
                    'recipe_id': recipe['recipe_id'],
                    'regime': regime,
                    'density': density,
                    'freedom': freedom,
                    'constraint': constraint,
                    'ratio': ratio
                })

                if regime not in by_regime:
                    by_regime[regime] = []
                by_regime[regime].append(ratio)

    if len(ratios) < 20:
        print(f"ERROR: Insufficient data ({len(ratios)} valid ratios)")
        return None

    print(f"Computed {len(ratios)} complementarity ratios")

    # Extract ratio array
    ratio_values = np.array([r['ratio'] for r in ratios])

    print("\n" + "-" * 70)
    print("COMPLEMENTARITY RATIO DISTRIBUTION")
    print("-" * 70)

    print(f"\nOverall ratio statistics:")
    print(f"  Mean: {np.mean(ratio_values):.4f}")
    print(f"  Std: {np.std(ratio_values):.4f}")
    print(f"  CV (std/mean): {np.std(ratio_values)/np.mean(ratio_values):.4f}")
    print(f"  Min: {np.min(ratio_values):.4f}")
    print(f"  Max: {np.max(ratio_values):.4f}")

    # By regime
    print("\nBy regime:")
    for regime in sorted(by_regime.keys()):
        regime_ratios = by_regime[regime]
        print(f"  {regime}: mean={np.mean(regime_ratios):.4f}, std={np.std(regime_ratios):.4f}, n={len(regime_ratios)}")

    # Test for variance reduction
    # Baseline: variance of density alone
    densities = np.array([r['density'] for r in ratios])
    baseline_cv = np.std(densities) / np.mean(densities) if np.mean(densities) > 0 else 0
    ratio_cv = np.std(ratio_values) / np.mean(ratio_values) if np.mean(ratio_values) > 0 else 0

    print("\n" + "-" * 70)
    print("VARIANCE COMPARISON")
    print("-" * 70)

    print(f"\nCoefficient of Variation (CV):")
    print(f"  Density alone: {baseline_cv:.4f}")
    print(f"  Complementarity ratio: {ratio_cv:.4f}")
    print(f"  Reduction: {(baseline_cv - ratio_cv)/baseline_cv * 100:.1f}%")

    variance_reduced = ratio_cv < baseline_cv

    # Levene's test: is ratio variance significantly different from density variance?
    levene_stat, levene_p = stats.levene(ratio_values, densities)

    print(f"\nLevene's test (ratio vs density variance):")
    print(f"  W = {levene_stat:.4f}")
    print(f"  p = {levene_p:.6f}")

    # Bartlett's test for homogeneity across regimes
    regime_groups = [by_regime[r] for r in by_regime if len(by_regime[r]) >= 2]
    if len(regime_groups) >= 2:
        bartlett_stat, bartlett_p = stats.bartlett(*regime_groups)
        print(f"\nBartlett's test (homogeneity across regimes):")
        print(f"  chi² = {bartlett_stat:.4f}")
        print(f"  p = {bartlett_p:.6f}")
        homogeneous = bartlett_p > 0.05
    else:
        bartlett_stat, bartlett_p = 0, 1
        homogeneous = False

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    # Pass criteria:
    # 1. Ratio CV < Density CV (variance reduced by normalization)
    # 2. Ratio variance homogeneous across regimes (Bartlett p > 0.05)

    print(f"\nVariance reduced (ratio CV < density CV): {'PASS' if variance_reduced else 'FAIL'}")
    print(f"  Ratio CV = {ratio_cv:.4f}, Density CV = {baseline_cv:.4f}")

    print(f"\nHomogeneous across regimes (Bartlett p > 0.05): {'PASS' if homogeneous else 'FAIL'}")
    print(f"  p = {bartlett_p:.6f}")

    passed = variance_reduced and homogeneous

    print("\n" + "-" * 70)
    print(f"H4 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    if passed:
        print("\nInterpretation: Complementarity ratio is stable across recipes/regimes.")
        print("Voynich constraint and Brunschwig verbosity partition responsibility consistently.")
    else:
        print("\nInterpretation: Complementarity ratio varies substantially.")
        print("No consistent partitioning of explanation vs enforcement.")

    # Save results
    output = {
        'hypothesis': 'H4',
        'name': 'Complementarity Ratio',
        'prediction': 'Explanation/constraint ratio should be stable if systems complement',
        'threshold': 'Ratio CV < Density CV, homogeneous across regimes',
        'n_recipes': len(ratios),
        'ratio_statistics': {
            'mean': round(float(np.mean(ratio_values)), 4),
            'std': round(float(np.std(ratio_values)), 4),
            'cv': round(float(ratio_cv), 4),
            'min': round(float(np.min(ratio_values)), 4),
            'max': round(float(np.max(ratio_values)), 4)
        },
        'comparison': {
            'density_cv': round(float(baseline_cv), 4),
            'ratio_cv': round(float(ratio_cv), 4),
            'cv_reduction_pct': round(float((baseline_cv - ratio_cv)/baseline_cv * 100) if baseline_cv > 0 else 0, 1)
        },
        'statistics': {
            'levene_w': round(float(levene_stat), 4),
            'levene_p': round(float(levene_p), 6),
            'bartlett_chi2': round(float(bartlett_stat), 4),
            'bartlett_p': round(float(bartlett_p), 6)
        },
        'evaluation': {
            'variance_reduced': bool(variance_reduced),
            'homogeneous': bool(homogeneous),
            'passed': bool(passed)
        },
        'by_regime': {
            regime: {
                'mean': round(float(np.mean(ratios)), 4),
                'std': round(float(np.std(ratios)), 4),
                'n': len(ratios)
            }
            for regime, ratios in by_regime.items()
        }
    }

    output_path = RESULTS_DIR / "bc_complementarity_ratio.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
