#!/usr/bin/env python3
"""
C-ZONE STRUCTURAL TEST

Tests hypothesis that C-zone correlates with PREPARATION VERBS,
not active sensory modalities (SIGHT, SOUND).

Expert recommendation: C-zone may address "preparation verification"
rather than active sensory monitoring.

Pre-registered predictions:
- C-zone should correlate with preparation_density (r>0.2, p<0.05)
- C-zone should NOT correlate with SIGHT or SOUND (r<0.2)
"""

import json
import re
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

# Preparation verbs (early modern German)
PREPARATION_VERBS = [
    # Taking/gathering
    'nimm', 'nehm', 'sammel', 'samml', 'hol', 'bring',
    # Placing/putting
    'tu', 'leg', 'setz', 'stell', 'gib', 'geb',
    # Filling/pouring
    'füll', 'gieß', 'schütt', 'gie(?:ss|ß)',
    # Measuring
    'mi(?:ss|ß)', 'wieg', 'zähl', 'teil',
    # Preparing
    'bereit', 'mach', 'rüst', 'ordne',
    # Container/equipment
    'kolben', 'gefa(?:ss|ß)', 'helm', 'glas', 'topf',
    # Cutting/processing
    'schneid', 'hack', 'zerklein', 'stoß', 'reib',
]

def normalize_text(text):
    """Normalize early modern German."""
    text = text.lower()
    text = text.replace('ſ', 's')
    text = text.replace('ꝛ', 'r')
    text = text.replace('ů', 'u')
    text = text.replace('ẽ', 'en')
    return text

def count_preparation_verbs(text):
    """Count preparation verbs in text."""
    normalized = normalize_text(text)
    count = 0
    matches = []

    for verb in PREPARATION_VERBS:
        pattern = verb
        found = re.findall(pattern, normalized)
        count += len(found)
        if found:
            matches.extend(found)

    return count, matches

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    if pooled_std == 0:
        return 0
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def main():
    print("=" * 70)
    print("C-ZONE STRUCTURAL TEST")
    print("=" * 70)
    print()

    # Load Brunschwig data
    with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
        bru_data = json.load(f)

    # Load reverse activation results
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    materials = bru_data['materials']
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}

    print(f"Loaded {len(materials)} materials")
    print(f"Loaded {len(ra_recipes)} reverse activation results")
    print()

    # Extract preparation verb density per recipe
    print("=" * 70)
    print("EXTRACTING PREPARATION VERB DENSITY")
    print("=" * 70)
    print()

    recipe_data = []
    all_prep_counts = []
    sample_matches = []

    for material in materials:
        recipe_id = material.get('recipe_id', '')
        if recipe_id not in ra_recipes:
            continue

        steps = material.get('procedural_steps', [])
        total_words = 0
        total_prep_verbs = 0
        step_matches = []

        for step in steps:
            text = step.get('brunschwig_text', '')
            words = len(normalize_text(text).split())
            total_words += words

            prep_count, matches = count_preparation_verbs(text)
            total_prep_verbs += prep_count
            step_matches.extend(matches)

        # Compute preparation density
        prep_density = total_prep_verbs / total_words if total_words > 0 else 0
        all_prep_counts.append(total_prep_verbs)

        # Get zone affinity from reverse activation
        ra = ra_recipes[recipe_id]
        zone_affinity = ra.get('zone_affinity', {})
        sensory_profile = ra.get('sensory_profile', {})

        recipe_data.append({
            'recipe_id': recipe_id,
            'total_words': total_words,
            'total_prep_verbs': total_prep_verbs,
            'prep_density': prep_density,
            'zone_affinity': zone_affinity,
            'sensory_profile': sensory_profile,
            'matches': step_matches[:5]  # Sample matches
        })

        if len(sample_matches) < 10 and step_matches:
            sample_matches.append({
                'recipe': recipe_id,
                'matches': step_matches[:3]
            })

    print(f"Recipes with zone affinity: {len(recipe_data)}")
    print(f"Total preparation verbs found: {sum(all_prep_counts)}")
    print(f"Mean per recipe: {np.mean(all_prep_counts):.1f}")
    print()

    # Sample matches
    print("Sample preparation verb matches:")
    for sm in sample_matches[:5]:
        print(f"  [{sm['recipe']}]: {sm['matches']}")
    print()

    # Extract arrays for correlation
    prep_densities = np.array([r['prep_density'] for r in recipe_data])
    c_affinities = np.array([r['zone_affinity'].get('C', 0) for r in recipe_data])
    p_affinities = np.array([r['zone_affinity'].get('P', 0) for r in recipe_data])
    r_affinities = np.array([r['zone_affinity'].get('R', 0) for r in recipe_data])
    s_affinities = np.array([r['zone_affinity'].get('S', 0) for r in recipe_data])

    # Sensory profiles
    sight_counts = np.array([r['sensory_profile'].get('SIGHT', 0) for r in recipe_data])
    sound_counts = np.array([r['sensory_profile'].get('SOUND', 0) for r in recipe_data])

    # Correlations
    print("=" * 70)
    print("CORRELATION ANALYSIS")
    print("=" * 70)
    print()

    # Test 1: Preparation density vs C-affinity (SHOULD correlate)
    r_prep_c, p_prep_c = stats.pearsonr(prep_densities, c_affinities)
    print("H4: Preparation density -> C-affinity")
    print(f"  r = {r_prep_c:.3f}, p = {p_prep_c:.4f}")
    if r_prep_c > 0.2 and p_prep_c < 0.05:
        print("  [PASS] Significant positive correlation")
    elif r_prep_c > 0:
        print("  [WEAK] Positive but not significant")
    else:
        print("  [FAIL] No positive correlation")
    print()

    # Test 2: C-affinity should NOT correlate with SIGHT
    r_c_sight, p_c_sight = stats.pearsonr(c_affinities, sight_counts)
    print("Negative check: C-affinity vs SIGHT")
    print(f"  r = {r_c_sight:.3f}, p = {p_c_sight:.4f}")
    if abs(r_c_sight) < 0.2:
        print("  [PASS] No significant correlation (as expected)")
    else:
        print("  [WARN] Unexpected correlation with SIGHT")
    print()

    # Test 3: C-affinity should NOT correlate with SOUND
    r_c_sound, p_c_sound = stats.pearsonr(c_affinities, sound_counts)
    print("Negative check: C-affinity vs SOUND")
    print(f"  r = {r_c_sound:.3f}, p = {p_c_sound:.4f}")
    if abs(r_c_sound) < 0.2:
        print("  [PASS] No significant correlation (as expected)")
    else:
        print("  [WARN] Unexpected correlation with SOUND")
    print()

    # Compare C-zone correlation with all zones
    print("=" * 70)
    print("PREPARATION DENSITY vs ALL ZONES")
    print("=" * 70)
    print()

    zone_correlations = {}
    for zone, affinities in [('C', c_affinities), ('P', p_affinities),
                              ('R', r_affinities), ('S', s_affinities)]:
        r, p = stats.pearsonr(prep_densities, affinities)
        zone_correlations[zone] = {'r': r, 'p': p}
        sig = '*' if p < 0.05 else ''
        print(f"  {zone}-zone: r = {r:+.3f}, p = {p:.4f} {sig}")

    print()

    # Check if C-zone has strongest preparation correlation
    c_is_strongest = all(
        abs(zone_correlations['C']['r']) >= abs(zone_correlations[z]['r'])
        for z in ['P', 'R', 'S']
    )
    if c_is_strongest:
        print("[FINDING] C-zone has strongest correlation with preparation density")
    else:
        strongest = max(zone_correlations.keys(), key=lambda z: abs(zone_correlations[z]['r']))
        print(f"[FINDING] {strongest}-zone has strongest correlation with preparation density")
    print()

    # High vs Low preparation recipes
    print("=" * 70)
    print("HIGH vs LOW PREPARATION RECIPES")
    print("=" * 70)
    print()

    median_prep = np.median(prep_densities)
    high_prep = [r for r in recipe_data if r['prep_density'] > median_prep]
    low_prep = [r for r in recipe_data if r['prep_density'] <= median_prep]

    print(f"High preparation density (>{median_prep:.3f}): {len(high_prep)} recipes")
    print(f"Low preparation density (<={median_prep:.3f}): {len(low_prep)} recipes")
    print()

    # Compare zone profiles
    print("Zone affinity comparison:")
    for zone in ['C', 'P', 'R', 'S']:
        high_vals = [r['zone_affinity'].get(zone, 0) for r in high_prep]
        low_vals = [r['zone_affinity'].get(zone, 0) for r in low_prep]

        high_mean = np.mean(high_vals)
        low_mean = np.mean(low_vals)
        t, p = stats.ttest_ind(high_vals, low_vals)
        d = cohens_d(high_vals, low_vals)

        sig = '*' if p < 0.05 else ''
        print(f"  {zone}-zone: High={high_mean:.3f}, Low={low_mean:.3f}, t={t:.2f}, p={p:.3f}, d={d:.2f} {sig}")

    print()

    # Permutation test for C-zone correlation
    print("=" * 70)
    print("PERMUTATION TEST: Prep density -> C-affinity")
    print("=" * 70)
    print()

    observed_r = r_prep_c
    n_permutations = 1000
    null_rs = []

    np.random.seed(42)
    for _ in range(n_permutations):
        shuffled = np.random.permutation(c_affinities)
        null_r, _ = stats.pearsonr(prep_densities, shuffled)
        null_rs.append(null_r)

    null_rs = np.array(null_rs)
    permutation_p = np.mean(np.abs(null_rs) >= np.abs(observed_r))

    print(f"Observed r: {observed_r:.3f}")
    print(f"Null distribution: mean={np.mean(null_rs):.3f}, std={np.std(null_rs):.3f}")
    print(f"Permutation p-value: {permutation_p:.4f}")

    if permutation_p < 0.05:
        print("[PASS] Permutation test confirms significance")
    else:
        print("[FAIL] Permutation test does not confirm significance")
    print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    results = {
        'phase': 'ZONE_MODALITY_VALIDATION',
        'test': 'czone_structural',
        'hypothesis': 'C-zone correlates with preparation verbs, not sensory modalities',
        'preparation_verbs_used': PREPARATION_VERBS,
        'n_recipes': len(recipe_data),
        'statistics': {
            'total_prep_verbs_found': int(sum(all_prep_counts)),
            'mean_per_recipe': float(np.mean(all_prep_counts)),
            'median_prep_density': float(median_prep)
        },
        'correlations': {
            'prep_density_vs_C': {'r': float(r_prep_c), 'p': float(p_prep_c)},
            'prep_density_vs_P': {'r': float(zone_correlations['P']['r']), 'p': float(zone_correlations['P']['p'])},
            'prep_density_vs_R': {'r': float(zone_correlations['R']['r']), 'p': float(zone_correlations['R']['p'])},
            'prep_density_vs_S': {'r': float(zone_correlations['S']['r']), 'p': float(zone_correlations['S']['p'])},
            'C_vs_SIGHT': {'r': float(r_c_sight), 'p': float(p_c_sight)},
            'C_vs_SOUND': {'r': float(r_c_sound), 'p': float(p_c_sound)}
        },
        'permutation_test': {
            'observed_r': float(observed_r),
            'n_permutations': n_permutations,
            'null_mean': float(np.mean(null_rs)),
            'null_std': float(np.std(null_rs)),
            'permutation_p': float(permutation_p)
        },
        'high_low_comparison': {
            'n_high': len(high_prep),
            'n_low': len(low_prep),
            'c_zone_effect': {
                'high_mean': float(np.mean([r['zone_affinity'].get('C', 0) for r in high_prep])),
                'low_mean': float(np.mean([r['zone_affinity'].get('C', 0) for r in low_prep])),
                'd': float(cohens_d(
                    [r['zone_affinity'].get('C', 0) for r in high_prep],
                    [r['zone_affinity'].get('C', 0) for r in low_prep]
                ))
            }
        },
        'findings': {
            'h4_supported': bool(r_prep_c > 0.2 and p_prep_c < 0.05),
            'c_sight_negative_check': bool(abs(r_c_sight) < 0.2),
            'c_sound_negative_check': bool(abs(r_c_sound) < 0.2),
            'c_is_strongest_prep_correlation': bool(c_is_strongest),
            'permutation_significant': bool(permutation_p < 0.05)
        }
    }

    output_path = Path('results/czone_structural_test.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    passed = sum([
        results['findings']['h4_supported'],
        results['findings']['c_sight_negative_check'],
        results['findings']['c_sound_negative_check'],
        results['findings']['permutation_significant']
    ])

    print(f"Tests passed: {passed}/4")
    print()
    print("H4 (C-zone -> preparation): ", "SUPPORTED" if results['findings']['h4_supported'] else "NOT SUPPORTED")
    print("C-zone NOT -> SIGHT: ", "PASS" if results['findings']['c_sight_negative_check'] else "FAIL")
    print("C-zone NOT -> SOUND: ", "PASS" if results['findings']['c_sound_negative_check'] else "FAIL")
    print("Permutation test: ", "PASS" if results['findings']['permutation_significant'] else "FAIL")

if __name__ == '__main__':
    main()
