#!/usr/bin/env python3
"""
bc_05_interaction_test.py - H3: Interaction > Main Effects

Tests H3: The freedom x pacing interaction explains more variance
than either main effect alone.

Threshold: Interaction delta-R-squared > 0.05, p < 0.05
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


def compute_r_squared(y_true, y_pred):
    """Compute R-squared."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return 0
    return 1 - (ss_res / ss_tot)


def linear_regression(X, y):
    """Simple linear regression returning coefficients and R-squared."""
    # Add intercept
    X_with_intercept = np.column_stack([np.ones(len(X)), X])
    # OLS solution
    try:
        beta = np.linalg.lstsq(X_with_intercept, y, rcond=None)[0]
        y_pred = X_with_intercept @ beta
        r_squared = compute_r_squared(y, y_pred)
        return beta, r_squared, y_pred
    except:
        return None, 0, None


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: H3 - Interaction Test")
    print("=" * 70)
    print()
    print("Prediction: Freedom x Pacing interaction > main effects alone")
    print("Threshold: Interaction delta-R-squared > 0.05, p < 0.05")
    print()

    # Load data
    density_data = load_explanation_density()
    scaffold_data = load_regime_scaffold_mapping()

    if not density_data or not scaffold_data:
        print("ERROR: Required data files not found")
        return None

    recipes = density_data.get('recipes', [])
    regime_metrics = scaffold_data.get('regime_metrics', {})

    # Build dataset
    data = []
    for recipe in recipes:
        regime = recipe.get('predicted_regime')
        if regime and regime in regime_metrics:
            metrics = regime_metrics[regime]
            data.append({
                'density': recipe['metrics']['M6_aggregate_density'],
                'freedom': metrics['judgment_freedom_index'],
                'pacing': metrics['scaffold_pacing_index']  # rho (negative = uniform)
            })

    if len(data) < 20:
        print(f"ERROR: Insufficient data ({len(data)} recipes)")
        return None

    print(f"Built dataset with {len(data)} recipes")

    # Extract arrays
    y = np.array([d['density'] for d in data])
    freedom = np.array([d['freedom'] for d in data])
    pacing = np.array([d['pacing'] for d in data])

    # Standardize predictors for interaction
    freedom_z = (freedom - np.mean(freedom)) / np.std(freedom) if np.std(freedom) > 0 else freedom
    pacing_z = (pacing - np.mean(pacing)) / np.std(pacing) if np.std(pacing) > 0 else pacing
    interaction = freedom_z * pacing_z

    print("\n" + "-" * 70)
    print("MODEL COMPARISON")
    print("-" * 70)

    # Model 1: Freedom only
    beta1, r2_freedom, _ = linear_regression(freedom_z.reshape(-1, 1), y)
    print(f"\nModel 1 (Freedom only):")
    print(f"  R² = {r2_freedom:.4f}")

    # Model 2: Pacing only
    beta2, r2_pacing, _ = linear_regression(pacing_z.reshape(-1, 1), y)
    print(f"\nModel 2 (Pacing only):")
    print(f"  R² = {r2_pacing:.4f}")

    # Model 3: Freedom + Pacing (main effects)
    X_main = np.column_stack([freedom_z, pacing_z])
    beta3, r2_main, _ = linear_regression(X_main, y)
    print(f"\nModel 3 (Freedom + Pacing):")
    print(f"  R² = {r2_main:.4f}")

    # Model 4: Freedom + Pacing + Interaction
    X_full = np.column_stack([freedom_z, pacing_z, interaction])
    beta4, r2_full, y_pred = linear_regression(X_full, y)
    print(f"\nModel 4 (Full with interaction):")
    print(f"  R² = {r2_full:.4f}")

    # Delta R² from adding interaction
    delta_r2 = r2_full - r2_main

    print(f"\nDelta R² (interaction contribution):")
    print(f"  {delta_r2:.4f}")

    # F-test for interaction significance
    # F = ((R2_full - R2_reduced) / df_diff) / ((1 - R2_full) / df_error)
    n = len(y)
    df_diff = 1  # One additional predictor (interaction)
    df_error = n - 4  # 4 parameters in full model (intercept + 3 predictors)

    if df_error > 0 and r2_full < 1:
        f_stat = ((r2_full - r2_main) / df_diff) / ((1 - r2_full) / df_error)
        p_interaction = 1 - stats.f.cdf(f_stat, df_diff, df_error)
    else:
        f_stat = 0
        p_interaction = 1.0

    print(f"\nF-test for interaction:")
    print(f"  F = {f_stat:.4f}")
    print(f"  p = {p_interaction:.6f}")

    # Check if interaction dominates
    print("\n" + "-" * 70)
    print("DOMINANCE ANALYSIS")
    print("-" * 70)

    print(f"\nMain effect variance explained:")
    print(f"  Freedom alone: {r2_freedom:.4f}")
    print(f"  Pacing alone: {r2_pacing:.4f}")
    print(f"  Combined: {r2_main:.4f}")

    print(f"\nInteraction contribution: {delta_r2:.4f}")

    interaction_dominates = delta_r2 > max(r2_freedom, r2_pacing)
    print(f"\nInteraction > any main effect: {interaction_dominates}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    delta_threshold = delta_r2 > 0.05
    significance = p_interaction < 0.05

    print(f"\nDelta R² > 0.05: {'PASS' if delta_threshold else 'FAIL'}")
    print(f"  delta_r2 = {delta_r2:.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p = {p_interaction:.6f}")

    passed = delta_threshold and significance

    print("\n" + "-" * 70)
    print(f"H3 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    if passed:
        print("\nInterpretation: The interaction term adds significant explanatory power.")
        print("Explanation density depends on the COMBINATION of freedom and pacing.")
    else:
        print("\nInterpretation: Interaction does not dominate main effects.")
        print("Freedom and pacing operate independently (if at all).")

    # Save results
    output = {
        'hypothesis': 'H3',
        'name': 'Interaction > Main Effects',
        'prediction': 'Freedom x Pacing interaction explains more variance than main effects',
        'threshold': 'Delta R² > 0.05, p < 0.05',
        'n_recipes': len(data),
        'model_comparison': {
            'r2_freedom_only': round(float(r2_freedom), 4),
            'r2_pacing_only': round(float(r2_pacing), 4),
            'r2_main_effects': round(float(r2_main), 4),
            'r2_full_model': round(float(r2_full), 4),
            'delta_r2_interaction': round(float(delta_r2), 4)
        },
        'statistics': {
            'f_statistic': round(float(f_stat), 4),
            'p_value': round(float(p_interaction), 6),
            'interaction_dominates_main': bool(interaction_dominates)
        },
        'evaluation': {
            'delta_threshold_met': bool(delta_threshold),
            'significant': bool(significance),
            'passed': bool(passed)
        }
    }

    output_path = RESULTS_DIR / "bc_interaction_test.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
