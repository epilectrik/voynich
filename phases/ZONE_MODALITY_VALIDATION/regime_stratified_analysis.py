#!/usr/bin/env python3
"""
REGIME-STRATIFIED ZONE-MODALITY ANALYSIS

Since we can't directly map recipes to AZC families, we stratify by REGIME
which may proxy for discrimination complexity:
- REGIME_1 (WATER_STANDARD): n=169, baseline
- REGIME_2 (WATER_GENTLE): n=14, gentle handling
- REGIME_3 (OIL_RESIN): n=7, intense extraction
- REGIME_4 (PRECISION): n=7, exact timing

Question: Does the R-SOUND effect differ across REGIMEs?
"""

import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return float('nan')
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    if pooled_std == 0:
        return 0
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def main():
    print("=" * 70)
    print("REGIME-STRATIFIED ZONE-MODALITY ANALYSIS")
    print("=" * 70)
    print()

    # Load data
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    # Build mappings
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}

    # Group by REGIME
    recipes_by_regime = defaultdict(list)
    for recipe_id, ra in ra_recipes.items():
        regime = ra.get('predicted_regime', 'UNKNOWN')
        recipes_by_regime[regime].append(recipe_id)

    print("Recipe distribution by REGIME:")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4', 'UNKNOWN']:
        n = len(recipes_by_regime[regime])
        print(f"  {regime}: {n} recipes")
    print()

    # Get modality for each recipe
    recipe_modality = {}
    for recipe_id in ra_recipes:
        if recipe_id in enh_recipes:
            recipe_modality[recipe_id] = enh_recipes[recipe_id].get('dominant_modality')

    # Stratified analysis by REGIME
    print("=" * 70)
    print("STRATIFIED ANALYSIS BY REGIME")
    print("=" * 70)

    results = {}

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        recipe_ids = recipes_by_regime[regime]
        if len(recipe_ids) < 5:
            print(f"\n{regime}: SKIPPED (n={len(recipe_ids)} < 5)")
            continue

        # Get SOUND vs NONE recipes
        sound_recipes = [r for r in recipe_ids if recipe_modality.get(r) == 'SOUND']
        none_recipes = [r for r in recipe_ids if recipe_modality.get(r) is None]

        print(f"\n{regime} (n={len(recipe_ids)}):")
        print(f"  SOUND: {len(sound_recipes)}, NONE: {len(none_recipes)}")

        if len(sound_recipes) < 3 or len(none_recipes) < 3:
            print(f"  SKIPPED: insufficient contrast")
            continue

        regime_results = {}

        for zone in ['C', 'P', 'R', 'S']:
            sound_vals = np.array([ra_recipes[r]['zone_affinity'].get(zone, 0) for r in sound_recipes])
            none_vals = np.array([ra_recipes[r]['zone_affinity'].get(zone, 0) for r in none_recipes])

            if len(sound_vals) < 2 or len(none_vals) < 2:
                continue

            t, p = stats.ttest_ind(sound_vals, none_vals)
            d = cohens_d(sound_vals, none_vals)

            sig = '*' if p < 0.05 else ''
            print(f"  {zone}-zone: SOUND={np.mean(sound_vals):.3f} vs NONE={np.mean(none_vals):.3f}, "
                  f"t={t:.2f}, p={p:.4f}{sig}, d={d:.2f}")

            regime_results[zone] = {
                'sound_mean': float(np.mean(sound_vals)),
                'none_mean': float(np.mean(none_vals)),
                't': float(t),
                'p': float(p),
                'd': float(d),
                'n_sound': len(sound_recipes),
                'n_none': len(none_recipes)
            }

        results[regime] = regime_results

    # Cross-regime comparison for R-zone
    print()
    print("=" * 70)
    print("CROSS-REGIME COMPARISON: R-SOUND EFFECT")
    print("=" * 70)
    print()

    r_effects = []
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if regime in results and 'R' in results[regime]:
            d = results[regime]['R']['d']
            p = results[regime]['R']['p']
            n = results[regime]['R']['n_sound'] + results[regime]['R']['n_none']
            r_effects.append((regime, d, p, n))
            print(f"{regime}: R-zone d={d:.2f}, p={p:.4f}, n={n}")

    print()
    if len(r_effects) >= 2:
        effects = [e[1] for e in r_effects if not np.isnan(e[1])]
        if effects:
            effect_range = max(effects) - min(effects)
            print(f"Effect range: {effect_range:.2f}")

            if effect_range > 0.5:
                print("[FINDING] R-SOUND effect DIFFERS substantially across REGIMEs (range > 0.5)")
            elif effect_range > 0.3:
                print("[FINDING] R-SOUND effect shows MODERATE variation across REGIMEs (0.3 < range <= 0.5)")
            else:
                print("[FINDING] R-SOUND effect is CONSISTENT across REGIMEs (range <= 0.3)")

    # Also test: do zone affinities differ by REGIME for SOUND recipes specifically?
    print()
    print("=" * 70)
    print("ZONE PROFILES FOR SOUND RECIPES BY REGIME")
    print("=" * 70)
    print()

    sound_by_regime = defaultdict(list)
    for regime, recipe_ids in recipes_by_regime.items():
        for r in recipe_ids:
            if recipe_modality.get(r) == 'SOUND':
                sound_by_regime[regime].append(r)

    print(f"{'REGIME':<12} | {'n':>4} | {'C':>6} | {'P':>6} | {'R':>6} | {'S':>6}")
    print("-" * 55)

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        recipes = sound_by_regime[regime]
        if len(recipes) < 2:
            continue

        c_mean = np.mean([ra_recipes[r]['zone_affinity'].get('C', 0) for r in recipes])
        p_mean = np.mean([ra_recipes[r]['zone_affinity'].get('P', 0) for r in recipes])
        r_mean = np.mean([ra_recipes[r]['zone_affinity'].get('R', 0) for r in recipes])
        s_mean = np.mean([ra_recipes[r]['zone_affinity'].get('S', 0) for r in recipes])

        print(f"{regime:<12} | {len(recipes):>4} | {c_mean:>6.3f} | {p_mean:>6.3f} | {r_mean:>6.3f} | {s_mean:>6.3f}")

    # ANOVA: Does REGIME predict zone affinity for SOUND recipes?
    print()
    print("=" * 70)
    print("ANOVA: REGIME -> ZONE AFFINITY (SOUND recipes only)")
    print("=" * 70)
    print()

    for zone in ['C', 'P', 'R', 'S']:
        groups = []
        for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            recipes = sound_by_regime[regime]
            if len(recipes) >= 2:
                vals = [ra_recipes[r]['zone_affinity'].get(zone, 0) for r in recipes]
                groups.append(vals)

        if len(groups) >= 2:
            # Flatten for ANOVA
            try:
                f, p = stats.f_oneway(*groups)
                sig = '*' if p < 0.05 else ''
                print(f"{zone}-zone: F={f:.2f}, p={p:.4f}{sig}")
            except:
                print(f"{zone}-zone: Could not compute ANOVA")

    # Save results
    print()
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    output = {
        'phase': 'ZONE_MODALITY_VALIDATION',
        'test': 'regime_stratified',
        'question': 'Does REGIME moderate the zone-modality relationship?',
        'recipe_counts': {k: len(v) for k, v in recipes_by_regime.items()},
        'stratified_results': results,
        'r_sound_effects': [{'regime': r, 'd': d, 'p': p, 'n': n} for r, d, p, n in r_effects] if r_effects else []
    }

    # Interpretation
    if r_effects:
        effects = [e[1] for e in r_effects if not np.isnan(e[1])]
        if effects:
            effect_range = max(effects) - min(effects)
            if effect_range <= 0.3:
                output['interpretation'] = 'R-SOUND effect is CONSISTENT across REGIMEs. Conflation is not a major issue.'
            else:
                output['interpretation'] = f'R-SOUND effect VARIES by REGIME (range={effect_range:.2f}). May need regime-specific analysis.'
    else:
        output['interpretation'] = 'Could not test REGIME stratification.'

    output_path = Path('results/regime_stratified_analysis.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {output_path}")
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(output.get('interpretation', 'No interpretation'))

if __name__ == '__main__':
    main()
