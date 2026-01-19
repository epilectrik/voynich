#!/usr/bin/env python3
"""
SCB-03: REGIME-ZONE REGRESSION

CONTROL TEST for SEMANTIC_CEILING_BREACH phase.

Question: Does REGIME alone explain zone variance, or is there independent information?

If REGIME alone explains >70% of zone variance, the semantic ceiling is at REGIME level.
If zone carries independent information, modality prediction has additional power.

This test determines whether the two-stage model (Modality + REGIME -> Zone) is
parsimonious or whether zone affinity carries information beyond REGIME membership.
"""

import json
from pathlib import Path
import numpy as np
from collections import defaultdict
from scipy import stats

def load_data():
    """Load zone affinity and regime data."""
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    return ra_data, enh_data

def compute_r_squared(y_actual, y_predicted):
    """Compute R-squared."""
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 0
    return 1 - ss_res / ss_tot

def main():
    print("=" * 70)
    print("SCB-03: REGIME-ZONE REGRESSION")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    ra_data, enh_data = load_data()

    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}

    # Build dataset
    dataset = []
    for recipe_id, ra in ra_recipes.items():
        zone_affinity = ra.get('zone_affinity', {})
        regime = ra.get('predicted_regime', 'UNKNOWN')

        modality = None
        if recipe_id in enh_recipes:
            modality = enh_recipes[recipe_id].get('dominant_modality')

        dataset.append({
            'recipe_id': recipe_id,
            'regime': regime,
            'modality': modality,
            'C': zone_affinity.get('C', 0),
            'P': zone_affinity.get('P', 0),
            'R': zone_affinity.get('R', 0),
            'S': zone_affinity.get('S', 0)
        })

    print(f"Dataset size: {len(dataset)} recipes")
    print()

    # REGIME distribution
    regime_counts = defaultdict(int)
    for d in dataset:
        regime_counts[d['regime']] += 1

    print("REGIME distribution:")
    for regime, count in sorted(regime_counts.items()):
        print(f"  {regime}: {count}")
    print()

    # Compute REGIME means for each zone
    print("=" * 70)
    print("REGIME -> ZONE MEAN PROFILES")
    print("=" * 70)
    print()

    regime_means = {}
    for regime in sorted(regime_counts.keys()):
        if regime == 'UNKNOWN':
            continue
        regime_data = [d for d in dataset if d['regime'] == regime]
        if not regime_data:
            continue

        means = {
            'C': np.mean([d['C'] for d in regime_data]),
            'P': np.mean([d['P'] for d in regime_data]),
            'R': np.mean([d['R'] for d in regime_data]),
            'S': np.mean([d['S'] for d in regime_data])
        }
        regime_means[regime] = means

    print(f"{'REGIME':<12} | {'C':>8} | {'P':>8} | {'R':>8} | {'S':>8} | {'n':>6}")
    print("-" * 60)
    for regime, means in sorted(regime_means.items()):
        n = regime_counts[regime]
        print(f"{regime:<12} | {means['C']:>8.3f} | {means['P']:>8.3f} | {means['R']:>8.3f} | {means['S']:>8.3f} | {n:>6}")
    print()

    # Test 1: REGIME -> Zone explained variance
    print("=" * 70)
    print("TEST 1: REGIME -> ZONE EXPLAINED VARIANCE (R-squared)")
    print("=" * 70)
    print()

    r_squared_by_zone = {}
    for zone in ['C', 'P', 'R', 'S']:
        # Actual values
        y_actual = np.array([d[zone] for d in dataset if d['regime'] != 'UNKNOWN'])
        regimes = [d['regime'] for d in dataset if d['regime'] != 'UNKNOWN']

        # Predicted = REGIME mean
        y_predicted = np.array([regime_means[r][zone] for r in regimes])

        r2 = compute_r_squared(y_actual, y_predicted)
        r_squared_by_zone[zone] = r2

        print(f"{zone}-zone: R-squared = {r2:.3f}")

    overall_r2 = np.mean(list(r_squared_by_zone.values()))
    print()
    print(f"Mean R-squared across zones: {overall_r2:.3f}")
    print()

    if overall_r2 > 0.7:
        regime_verdict = "REGIME alone explains >70% of zone variance (semantic ceiling at REGIME level)"
    elif overall_r2 > 0.3:
        regime_verdict = "REGIME explains moderate variance (30-70%). Zone carries some independent info."
    else:
        regime_verdict = "REGIME explains <30% of zone variance. Zone carries significant independent info."

    print(f"[INTERPRETATION] {regime_verdict}")
    print()

    # Test 2: Does MODALITY add explanatory power beyond REGIME?
    print("=" * 70)
    print("TEST 2: DOES MODALITY ADD BEYOND REGIME?")
    print("=" * 70)
    print()

    # Filter to recipes with modality labels
    labeled = [d for d in dataset if d['modality'] is not None and d['regime'] != 'UNKNOWN']
    print(f"Labeled recipes: {len(labeled)}")
    print()

    # Model 1: REGIME only
    # Model 2: REGIME + MODALITY

    # For simplicity, compute residual variance after REGIME, then check if MODALITY explains residuals

    modality_r2_improvement = {}

    for zone in ['C', 'P', 'R', 'S']:
        # Residuals after REGIME prediction
        y_actual = np.array([d[zone] for d in labeled])
        y_regime_pred = np.array([regime_means[d['regime']][zone] for d in labeled])
        residuals = y_actual - y_regime_pred

        # Group residuals by modality
        modality_residuals = defaultdict(list)
        for d, resid in zip(labeled, residuals):
            modality_residuals[d['modality']].append(resid)

        # Check if modality explains residual variance (ANOVA)
        groups = [np.array(v) for v in modality_residuals.values() if len(v) >= 2]

        if len(groups) >= 2:
            try:
                f_stat, p_val = stats.f_oneway(*groups)

                # Compute eta-squared (effect size)
                ss_between = sum(len(g) * (np.mean(g) - np.mean(residuals))**2 for g in groups)
                ss_total = np.sum((residuals - np.mean(residuals))**2)
                eta_sq = ss_between / ss_total if ss_total > 0 else 0

                sig = '*' if p_val < 0.05 else ''
                print(f"{zone}-zone residuals ~ MODALITY: F={f_stat:.2f}, p={p_val:.4f}{sig}, eta2={eta_sq:.3f}")

                modality_r2_improvement[zone] = {
                    'f_stat': float(f_stat),
                    'p_value': float(p_val),
                    'eta_squared': float(eta_sq),
                    'significant': bool(p_val < 0.05)
                }
            except Exception as e:
                print(f"{zone}-zone: ANOVA failed - {e}")
                modality_r2_improvement[zone] = None
        else:
            print(f"{zone}-zone: Insufficient groups for ANOVA")
            modality_r2_improvement[zone] = None

    print()

    # Check how many zones show significant modality effect
    n_significant = sum(1 for v in modality_r2_improvement.values()
                        if v is not None and v.get('significant', False))

    if n_significant >= 3:
        modality_verdict = "MODALITY adds significant explanatory power to 3+ zones beyond REGIME"
    elif n_significant >= 1:
        modality_verdict = f"MODALITY adds significant explanatory power to {n_significant} zone(s)"
    else:
        modality_verdict = "MODALITY does NOT add significant explanatory power beyond REGIME"

    print(f"[INTERPRETATION] {modality_verdict}")
    print()

    # Test 3: Direct modality -> zone correlation (controlling for REGIME)
    print("=" * 70)
    print("TEST 3: MODALITY-ZONE PARTIAL CORRELATION (CONTROLLING FOR REGIME)")
    print("=" * 70)
    print()

    # Encode modality as SOUND=1, OTHER=0
    sound_indicator = np.array([1 if d['modality'] == 'SOUND' else 0 for d in labeled])

    for zone in ['C', 'P', 'R', 'S']:
        y_actual = np.array([d[zone] for d in labeled])
        y_regime_pred = np.array([regime_means[d['regime']][zone] for d in labeled])
        residuals = y_actual - y_regime_pred

        # Correlation between SOUND indicator and residuals
        r, p = stats.pearsonr(sound_indicator, residuals)

        sig = '*' if p < 0.05 else ''
        direction = '+' if r > 0 else '-'
        print(f"{zone}-zone: SOUND partial correlation r={r:+.3f}, p={p:.4f}{sig} "
              f"({'SOUND increases' if r > 0 else 'SOUND decreases'} {zone})")

    print()

    # Final verdict
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()

    print(f"1. REGIME explanatory power: {overall_r2:.1%}")
    print(f"2. MODALITY beyond REGIME: {n_significant}/4 zones significant")
    print()

    if overall_r2 > 0.7:
        verdict = "REGIME_DOMINANT"
        print("[VERDICT] REGIME is the primary semantic anchor")
        print("Zone affinity is largely determined by REGIME membership.")
    elif n_significant >= 2:
        verdict = "MODALITY_ADDS"
        print("[VERDICT] MODALITY adds explanatory power beyond REGIME")
        print("Two-stage model (MODALITY + REGIME -> Zone) is supported.")
    else:
        verdict = "INDEPENDENT"
        print("[VERDICT] Zone carries independent information")
        print("Neither REGIME nor MODALITY fully explains zone variance.")

    print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    results = {
        'phase': 'SEMANTIC_CEILING_BREACH',
        'test': 'scb_03_regime_zone_regression',
        'question': 'Does REGIME alone explain zone variance?',
        'n_recipes': len(dataset),
        'n_labeled': len(labeled),
        'regime_counts': dict(regime_counts),
        'regime_means': regime_means,
        'regime_r_squared': {
            'by_zone': r_squared_by_zone,
            'mean': overall_r2
        },
        'modality_beyond_regime': modality_r2_improvement,
        'n_zones_modality_significant': n_significant,
        'interpretation': {
            'regime_verdict': regime_verdict,
            'modality_verdict': modality_verdict
        },
        'verdict': verdict
    }

    output_path = Path('results/scb_regime_zone_regression.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    return results

if __name__ == '__main__':
    main()
