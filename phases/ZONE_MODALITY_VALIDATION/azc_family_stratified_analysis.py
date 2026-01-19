#!/usr/bin/env python3
"""
AZC FAMILY STRATIFIED ANALYSIS

Tests whether zone-modality correlations differ between Zodiac and Non-Zodiac
AZC families, as suggested by expert review.

Key question: Is our R-SOUND correlation (d=0.61) driven by one family?
"""

import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

# Known AZC family membership from constraint system
# Zodiac folios: f67r1, f67r2, f67v1, f67v2, f68r1, f68r2, f68r3, f68v1, f68v2, f68v3,
#                f69r, f69v1, f69v2, f70r1, f70r2, f70v1, f70v2, f71r, f71v, f72r1,
#                f72r2, f72r3, f72v1, f72v2, f72v3, f73r, f73v
# Non-Zodiac (A/C): f57v, f65r, f65v, f66r, f66v, f67r1 (overlaps), f85r1, f85r2, f86v3, f86v4

ZODIAC_FOLIOS = {
    'f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
    'f68v1', 'f68v2', 'f68v3', 'f69r', 'f69v1', 'f69v2', 'f70r1',
    'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2',
    'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'
}

AC_FOLIOS = {
    'f57v', 'f65r', 'f65v', 'f66r', 'f66v', 'f85r1', 'f85r2',
    'f86v3', 'f86v4', 'f86v5', 'f86v6'
}

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
    print("AZC FAMILY STRATIFIED ANALYSIS")
    print("=" * 70)
    print()

    # Load reverse activation results
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    # Load enhanced sensory extraction
    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    # Build recipe mappings
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}

    print(f"Loaded {len(ra_recipes)} recipes with zone affinities")
    print(f"Zodiac folios defined: {len(ZODIAC_FOLIOS)}")
    print(f"A/C folios defined: {len(AC_FOLIOS)}")
    print()

    # Check folio predictions to determine family affinity
    print("=" * 70)
    print("DETERMINING FAMILY AFFINITY PER RECIPE")
    print("=" * 70)
    print()

    recipes_by_family = {'ZODIAC': [], 'AC': [], 'MIXED': [], 'UNKNOWN': []}

    for recipe_id, ra in ra_recipes.items():
        folio_pred = ra.get('folio_prediction', {})
        top_folios = folio_pred.get('top_folios', [])

        if not top_folios:
            recipes_by_family['UNKNOWN'].append(recipe_id)
            continue

        # Check which family the top predicted folios belong to
        zodiac_count = 0
        ac_count = 0

        for folio_info in top_folios[:5]:  # Check top 5 predictions
            folio = folio_info.get('folio', '') if isinstance(folio_info, dict) else str(folio_info)
            # Normalize folio name
            folio_clean = folio.lower().replace('_', '').replace('-', '')

            if any(z.lower().replace('_', '') in folio_clean or folio_clean in z.lower().replace('_', '')
                   for z in ZODIAC_FOLIOS):
                zodiac_count += 1
            elif any(a.lower().replace('_', '') in folio_clean or folio_clean in a.lower().replace('_', '')
                     for a in AC_FOLIOS):
                ac_count += 1

        # Classify recipe by dominant family
        if zodiac_count > ac_count and zodiac_count >= 2:
            recipes_by_family['ZODIAC'].append(recipe_id)
        elif ac_count > zodiac_count and ac_count >= 2:
            recipes_by_family['AC'].append(recipe_id)
        elif zodiac_count > 0 or ac_count > 0:
            recipes_by_family['MIXED'].append(recipe_id)
        else:
            recipes_by_family['UNKNOWN'].append(recipe_id)

    print("Recipe distribution by AZC family affinity:")
    for family, recipes in recipes_by_family.items():
        print(f"  {family}: {len(recipes)} recipes")
    print()

    # If we can't determine family affinity from folio predictions,
    # try using HT oscillation as a proxy (Zodiac = low, A/C = high)
    if len(recipes_by_family['ZODIAC']) < 10 and len(recipes_by_family['AC']) < 10:
        print("Insufficient family classification from folios.")
        print("Attempting HT oscillation proxy method...")
        print()

        # Load HT data if available
        try:
            with open('results/unified_folio_profiles.json', 'r') as f:
                folio_profiles = json.load(f)

            # Get HT densities
            ht_by_recipe = {}
            for recipe_id, ra in ra_recipes.items():
                # Use predicted regime to estimate HT
                regime = ra.get('predicted_regime', '')
                metrics = ra.get('metrics', {})
                ht_by_recipe[recipe_id] = metrics.get('ht_density', 0)

            # Split by median HT (proxy for discrimination complexity)
            ht_values = [v for v in ht_by_recipe.values() if v > 0]
            if ht_values:
                median_ht = np.median(ht_values)
                print(f"Median HT density: {median_ht:.4f}")

                recipes_by_family = {
                    'HIGH_HT': [r for r, ht in ht_by_recipe.items() if ht > median_ht],
                    'LOW_HT': [r for r, ht in ht_by_recipe.items() if ht <= median_ht and ht > 0],
                    'NO_HT': [r for r, ht in ht_by_recipe.items() if ht == 0]
                }

                print("Recipe distribution by HT density (proxy for discrimination):")
                for family, recipes in recipes_by_family.items():
                    print(f"  {family}: {len(recipes)} recipes")
                print()

        except Exception as e:
            print(f"Could not load HT data: {e}")

    # Now run stratified analysis
    print("=" * 70)
    print("STRATIFIED ZONE-MODALITY ANALYSIS")
    print("=" * 70)
    print()

    # Get modality for each recipe
    recipe_modality = {}
    for recipe_id in ra_recipes:
        if recipe_id in enh_recipes:
            recipe_modality[recipe_id] = enh_recipes[recipe_id].get('dominant_modality')

    # For each family, compute SOUND vs zone correlations
    results = {}

    for family, recipe_ids in recipes_by_family.items():
        if len(recipe_ids) < 5:
            print(f"{family}: SKIPPED (n={len(recipe_ids)} < 5)")
            continue

        # Get SOUND recipes in this family
        sound_recipes = [r for r in recipe_ids if recipe_modality.get(r) == 'SOUND']
        none_recipes = [r for r in recipe_ids if recipe_modality.get(r) is None]

        print(f"\n{family} (n={len(recipe_ids)}):")
        print(f"  SOUND recipes: {len(sound_recipes)}")
        print(f"  NONE recipes: {len(none_recipes)}")

        if len(sound_recipes) < 3 or len(none_recipes) < 3:
            print(f"  SKIPPED: insufficient SOUND or NONE recipes")
            continue

        family_results = {}

        for zone in ['C', 'P', 'R', 'S']:
            sound_vals = np.array([ra_recipes[r]['zone_affinity'].get(zone, 0) for r in sound_recipes])
            none_vals = np.array([ra_recipes[r]['zone_affinity'].get(zone, 0) for r in none_recipes])

            t, p = stats.ttest_ind(sound_vals, none_vals)
            d = cohens_d(sound_vals, none_vals)

            sig = '*' if p < 0.05 else ''
            print(f"  {zone}-zone: SOUND={np.mean(sound_vals):.3f} vs NONE={np.mean(none_vals):.3f}, "
                  f"t={t:.2f}, p={p:.4f}{sig}, d={d:.2f}")

            family_results[zone] = {
                'sound_mean': float(np.mean(sound_vals)),
                'none_mean': float(np.mean(none_vals)),
                't': float(t),
                'p': float(p),
                'd': float(d),
                'n_sound': len(sound_recipes),
                'n_none': len(none_recipes)
            }

        results[family] = family_results

    # Compare effect sizes across families
    print()
    print("=" * 70)
    print("CROSS-FAMILY COMPARISON: R-SOUND EFFECT")
    print("=" * 70)
    print()

    r_effects = []
    for family, fam_results in results.items():
        if 'R' in fam_results:
            r_effects.append((family, fam_results['R']['d'], fam_results['R']['p']))
            print(f"{family}: R-zone d={fam_results['R']['d']:.2f}, p={fam_results['R']['p']:.4f}")

    if len(r_effects) >= 2:
        # Test if effects differ significantly
        print()
        # Simple comparison
        effects = [e[1] for e in r_effects]
        if max(effects) - min(effects) > 0.3:
            print("[FINDING] R-SOUND effect SIZE differs across families (delta > 0.3)")
        else:
            print("[FINDING] R-SOUND effect SIZE is consistent across families (delta <= 0.3)")

        # Check if direction is consistent
        directions = [e[1] > 0 for e in r_effects]
        if all(directions) or not any(directions):
            print("[FINDING] R-SOUND effect DIRECTION is consistent across families")
        else:
            print("[WARNING] R-SOUND effect DIRECTION differs across families!")

    # Also test overall: does family membership moderate the effect?
    print()
    print("=" * 70)
    print("INTERACTION TEST: Family x SOUND -> R-zone")
    print("=" * 70)
    print()

    # Collect all data for interaction test
    all_data = []
    family_labels = list(results.keys())

    if len(family_labels) >= 2:
        for family in family_labels:
            recipe_ids = recipes_by_family[family]
            for r in recipe_ids:
                if r in ra_recipes and r in recipe_modality:
                    is_sound = 1 if recipe_modality[r] == 'SOUND' else 0
                    r_zone = ra_recipes[r]['zone_affinity'].get('R', 0)
                    fam_code = family_labels.index(family)
                    all_data.append([is_sound, fam_code, r_zone])

        if len(all_data) > 20:
            data = np.array(all_data)

            # Simple interaction: correlation of SOUND*Family with R-zone
            interaction = data[:, 0] * data[:, 1]
            r_zone = data[:, 2]

            r_int, p_int = stats.pearsonr(interaction, r_zone)
            print(f"Interaction (SOUND x Family) -> R-zone:")
            print(f"  r = {r_int:.3f}, p = {p_int:.4f}")

            if p_int < 0.05:
                print("  [SIGNIFICANT] Family membership MODERATES the SOUND->R-zone effect")
            else:
                print("  [NOT SIGNIFICANT] Family membership does NOT moderate the effect")

    # Save results
    print()
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    output = {
        'phase': 'ZONE_MODALITY_VALIDATION',
        'test': 'azc_family_stratified',
        'question': 'Does AZC family membership moderate zone-modality correlations?',
        'recipe_counts': {k: len(v) for k, v in recipes_by_family.items()},
        'stratified_results': results,
        'interpretation': None
    }

    # Determine interpretation
    if len(results) >= 2:
        r_effects_d = [results[f]['R']['d'] for f in results if 'R' in results[f]]
        if r_effects_d:
            effect_range = max(r_effects_d) - min(r_effects_d)
            if effect_range <= 0.3:
                output['interpretation'] = 'R-SOUND effect is CONSISTENT across AZC families. Family conflation is NOT corrupting results.'
            else:
                output['interpretation'] = f'R-SOUND effect DIFFERS across AZC families (range={effect_range:.2f}). Results may be family-dependent.'
    else:
        output['interpretation'] = 'Insufficient family separation to test stratification.'

    output_path = Path('results/azc_family_stratified.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    # Final summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(output['interpretation'])

if __name__ == '__main__':
    main()
