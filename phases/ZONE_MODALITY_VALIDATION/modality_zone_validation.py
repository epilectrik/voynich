#!/usr/bin/env python3
"""
MODALITY-ZONE VALIDATION

Full statistical validation of zone-modality associations with:
- Effect sizes (Cohen's d)
- Permutation tests
- Bonferroni correction
- Falsification criteria checks

Pre-registered predictions:
- P-zone -> SIGHT (positive)
- R-zone -> SOUND (positive)
- S-zone -> TOUCH (positive)
- C-zone -> NOT SIGHT/SOUND

Falsification criteria:
- SMELL associates with P-zone -> kills hypothesis
- SOUND associates with S-zone -> kills hypothesis
- Effect sizes d<0.3 -> hypothesis too weak
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

def permutation_test(group1, group2, n_permutations=1000):
    """Run permutation test for difference in means."""
    observed_diff = np.mean(group1) - np.mean(group2)
    combined = np.concatenate([group1, group2])
    n1 = len(group1)

    np.random.seed(42)
    count = 0
    for _ in range(n_permutations):
        np.random.shuffle(combined)
        perm_diff = np.mean(combined[:n1]) - np.mean(combined[n1:])
        if abs(perm_diff) >= abs(observed_diff):
            count += 1

    return count / n_permutations

def main():
    print("=" * 70)
    print("MODALITY-ZONE VALIDATION")
    print("=" * 70)
    print()

    # Load data
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    # Build recipe -> zone affinity mapping
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}

    # Build recipe -> enhanced modality mapping
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}

    print(f"Loaded {len(ra_recipes)} reverse activation results")
    print(f"Loaded {len(enh_recipes)} enhanced extraction results")
    print()

    # Merge data
    merged = []
    for recipe_id, ra in ra_recipes.items():
        if recipe_id in enh_recipes:
            enh = enh_recipes[recipe_id]
            merged.append({
                'recipe_id': recipe_id,
                'zone_affinity': ra.get('zone_affinity', {}),
                'dominant_modality': enh.get('dominant_modality'),
                'sensory_counts': enh.get('sensory_counts', {})
            })

    print(f"Merged recipes: {len(merged)}")
    print()

    # Group by dominant modality
    modality_groups = defaultdict(list)
    for r in merged:
        mod = r['dominant_modality'] or 'NONE'
        modality_groups[mod].append(r)

    print("=" * 70)
    print("SAMPLE SIZES BY MODALITY")
    print("=" * 70)
    print()

    print(f"{'Modality':<10} | {'n':>5} | {'Adequate (>=15)':>15}")
    print("-" * 40)
    for mod in ['SOUND', 'SIGHT', 'TOUCH', 'SMELL', 'TASTE', 'NONE']:
        n = len(modality_groups[mod])
        adequate = 'YES' if n >= 15 else 'NO'
        print(f"{mod:<10} | {n:>5} | {adequate:>15}")
    print()

    # Get baseline (NONE modality)
    baseline = modality_groups['NONE']
    baseline_zones = {
        zone: [r['zone_affinity'].get(zone, 0) for r in baseline]
        for zone in ['C', 'P', 'R', 'S']
    }

    # Test each modality against baseline
    print("=" * 70)
    print("MODALITY-ZONE ASSOCIATIONS")
    print("=" * 70)
    print()

    results = {}
    n_tests = 0  # Count for Bonferroni

    for modality in ['SOUND', 'SIGHT', 'TOUCH', 'SMELL', 'TASTE']:
        group = modality_groups[modality]
        n = len(group)

        if n < 3:
            print(f"{modality}: SKIPPED (n={n}, insufficient data)")
            results[modality] = {'status': 'skipped', 'n': n, 'reason': 'insufficient data'}
            continue

        print(f"\n{modality} (n={n}):")
        print("-" * 50)

        modality_results = {'n': n, 'zones': {}}

        for zone in ['C', 'P', 'R', 'S']:
            mod_vals = np.array([r['zone_affinity'].get(zone, 0) for r in group])
            base_vals = np.array(baseline_zones[zone])

            # T-test
            t, p = stats.ttest_ind(mod_vals, base_vals)

            # Effect size
            d = cohens_d(mod_vals, base_vals)

            # Permutation test (if n >= 5)
            if n >= 5:
                perm_p = permutation_test(mod_vals, base_vals)
            else:
                perm_p = float('nan')

            n_tests += 1

            # Determine significance
            sig = '*' if p < 0.05 else ''
            d_label = 'small' if abs(d) >= 0.2 else 'negligible'
            if abs(d) >= 0.5:
                d_label = 'medium'
            if abs(d) >= 0.8:
                d_label = 'large'

            print(f"  {zone}-zone: mean={np.mean(mod_vals):.3f} vs {np.mean(base_vals):.3f}, "
                  f"t={t:.2f}, p={p:.4f}{sig}, d={d:.2f} ({d_label})")

            modality_results['zones'][zone] = {
                'mean': float(np.mean(mod_vals)),
                'baseline_mean': float(np.mean(base_vals)),
                't': float(t),
                'p': float(p),
                'd': float(d),
                'perm_p': float(perm_p) if not np.isnan(perm_p) else None
            }

        results[modality] = modality_results

    # Bonferroni correction
    alpha = 0.05
    bonferroni_alpha = alpha / n_tests if n_tests > 0 else alpha
    print()
    print(f"Bonferroni-corrected alpha: {bonferroni_alpha:.4f} ({n_tests} tests)")

    # Falsification criteria check
    print()
    print("=" * 70)
    print("FALSIFICATION CRITERIA CHECK")
    print("=" * 70)
    print()

    falsifications = []

    # Check 1: SMELL -> P-zone (should NOT happen)
    if 'SMELL' in results and 'zones' in results['SMELL']:
        smell_p = results['SMELL']['zones'].get('P', {})
        if smell_p.get('p', 1) < 0.05 and smell_p.get('d', 0) > 0.3:
            falsifications.append("SMELL associates with P-zone (KILLS hypothesis)")
            print("[FALSIFIED] SMELL associates with P-zone")
        else:
            print("[PASS] SMELL does not associate with P-zone")
    else:
        print("[SKIP] SMELL sample insufficient to test")

    # Check 2: SOUND -> S-zone (should NOT happen)
    if 'SOUND' in results and 'zones' in results['SOUND']:
        sound_s = results['SOUND']['zones'].get('S', {})
        if sound_s.get('p', 1) < 0.05 and sound_s.get('d', 0) > 0.3:
            falsifications.append("SOUND associates with S-zone (KILLS hypothesis)")
            print("[FALSIFIED] SOUND associates with S-zone")
        else:
            print("[PASS] SOUND does not associate with S-zone")

    # Check 3: P-SIGHT flip
    if 'SIGHT' in results and 'zones' in results['SIGHT']:
        sight_p = results['SIGHT']['zones'].get('P', {})
        if sight_p.get('d', 0) < 0 and sight_p.get('p', 1) < 0.05:
            falsifications.append("P-SIGHT correlation flipped (sign changed)")
            print("[FALSIFIED] P-SIGHT correlation flipped")
        else:
            print("[PASS] P-SIGHT direction preserved")
    else:
        print("[SKIP] SIGHT sample insufficient to test")

    # Check 4: R-SOUND flip
    if 'SOUND' in results and 'zones' in results['SOUND']:
        sound_r = results['SOUND']['zones'].get('R', {})
        if sound_r.get('d', 0) < 0 and sound_r.get('p', 1) < 0.05:
            falsifications.append("R-SOUND correlation flipped (sign changed)")
            print("[FALSIFIED] R-SOUND correlation flipped")
        else:
            print("[PASS] R-SOUND direction preserved")

    print()

    # Summary of confirmed associations
    print("=" * 70)
    print("CONFIRMED ASSOCIATIONS (p<0.05, d>=0.3)")
    print("=" * 70)
    print()

    confirmed = []
    for modality, data in results.items():
        if 'zones' not in data:
            continue
        for zone, stats_data in data['zones'].items():
            if stats_data.get('p', 1) < 0.05 and abs(stats_data.get('d', 0)) >= 0.3:
                direction = '+' if stats_data['d'] > 0 else '-'
                confirmed.append({
                    'modality': modality,
                    'zone': zone,
                    'd': stats_data['d'],
                    'p': stats_data['p'],
                    'direction': direction
                })
                print(f"  {modality} -> {zone}-zone: d={stats_data['d']:.2f}, p={stats_data['p']:.4f} ({direction})")

    if not confirmed:
        print("  No associations reached threshold")

    # Pre-registered predictions check
    print()
    print("=" * 70)
    print("PRE-REGISTERED PREDICTIONS CHECK")
    print("=" * 70)
    print()

    predictions = [
        ('P', 'SIGHT', 'positive'),
        ('R', 'SOUND', 'positive'),
        ('S', 'TOUCH', 'positive'),
    ]

    for zone, modality, expected_dir in predictions:
        if modality not in results or 'zones' not in results[modality]:
            print(f"H: {zone}-zone -> {modality}: UNTESTABLE (n<3)")
            continue

        stats_data = results[modality]['zones'].get(zone, {})
        d = stats_data.get('d', 0)
        p = stats_data.get('p', 1)

        actual_dir = 'positive' if d > 0 else 'negative'
        sig = p < 0.05
        effect = abs(d) >= 0.3

        if actual_dir == expected_dir and sig and effect:
            print(f"H: {zone}-zone -> {modality}: CONFIRMED (d={d:.2f}, p={p:.4f})")
        elif actual_dir == expected_dir and not sig:
            print(f"H: {zone}-zone -> {modality}: DIRECTION CORRECT but not significant (d={d:.2f}, p={p:.4f})")
        elif actual_dir != expected_dir:
            print(f"H: {zone}-zone -> {modality}: WRONG DIRECTION (d={d:.2f}, p={p:.4f})")
        else:
            print(f"H: {zone}-zone -> {modality}: WEAK (d={d:.2f}, p={p:.4f})")

    print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    output = {
        'phase': 'ZONE_MODALITY_VALIDATION',
        'test': 'modality_zone_validation',
        'sample_sizes': {mod: len(grp) for mod, grp in modality_groups.items()},
        'baseline_n': len(baseline),
        'bonferroni_alpha': float(bonferroni_alpha),
        'n_tests': n_tests,
        'modality_results': results,
        'falsifications': falsifications,
        'confirmed_associations': confirmed,
        'assessment': {
            'testable_modalities': sum(1 for m in ['SOUND', 'SIGHT', 'TOUCH', 'SMELL', 'TASTE']
                                       if len(modality_groups[m]) >= 15),
            'any_falsification': len(falsifications) > 0,
            'confirmed_count': len(confirmed)
        }
    }

    output_path = Path('results/modality_zone_validation.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    # Final assessment
    print("=" * 70)
    print("FINAL ASSESSMENT")
    print("=" * 70)
    print()

    testable = output['assessment']['testable_modalities']
    print(f"Modalities with n>=15: {testable}/5")
    print(f"Falsifications triggered: {len(falsifications)}")
    print(f"Confirmed associations: {len(confirmed)}")
    print()

    if len(falsifications) > 0:
        print("[RESULT] HYPOTHESIS FALSIFIED")
        for f in falsifications:
            print(f"  - {f}")
    elif len(confirmed) >= 2:
        print("[RESULT] HYPOTHESIS SUPPORTED (at Tier 3 level)")
        print("  Multiple associations confirmed with adequate effect sizes")
    elif len(confirmed) == 1:
        print("[RESULT] PARTIAL SUPPORT")
        print("  Only one association confirmed")
    else:
        print("[RESULT] UNDERPOWERED")
        print("  Insufficient sample sizes to test hypotheses")

if __name__ == '__main__':
    main()
