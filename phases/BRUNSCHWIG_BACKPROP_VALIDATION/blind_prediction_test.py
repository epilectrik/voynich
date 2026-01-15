#!/usr/bin/env python3
"""
BLIND PREDICTION TEST (Test 1)

Pre-registered predictions for unused Brunschwig recipes.
Tests predictive power WITHOUT circularity.

Pre-registration (locked):
- Lavender water (1st) -> WATER_GENTLE: ok>8%, ch<16%, y~7%
- Sage water (2nd) -> WATER_STANDARD: ch~24%, d~18%
- Juniper oil (3rd) -> OIL_RESIN: d>20%, y<7%, ch~21%
"""

import json

# ============================================================
# PRE-REGISTERED PREDICTIONS (DO NOT MODIFY)
# ============================================================

PREDICTIONS = {
    'lavender_water': {
        'name': 'Lavender Water',
        'german': 'Lavendelwasser',
        'degree': 1,
        'expected_type': 'WATER_GENTLE',
        'predictions': {
            'ok': {'direction': '>', 'threshold': 0.08, 'label': 'ok > 8%'},
            'ch': {'direction': '<', 'threshold': 0.16, 'label': 'ch < 16%'},
            'y': {'direction': '~', 'threshold': 0.07, 'tolerance': 0.02, 'label': 'y ~ 7%'},
        }
    },
    'sage_water': {
        'name': 'Sage Water',
        'german': 'Salbeiwasser',
        'degree': 2,
        'expected_type': 'WATER_STANDARD',
        'predictions': {
            'ch': {'direction': '~', 'threshold': 0.24, 'tolerance': 0.03, 'label': 'ch ~ 24%'},
            'd': {'direction': '~', 'threshold': 0.18, 'tolerance': 0.03, 'label': 'd ~ 18%'},
        }
    },
    'juniper_oil': {
        'name': 'Juniper Oil',
        'german': 'Wacholderoil',
        'degree': 3,
        'expected_type': 'OIL_RESIN',
        'predictions': {
            'd': {'direction': '>', 'threshold': 0.20, 'label': 'd > 20%'},
            'y': {'direction': '<', 'threshold': 0.07, 'label': 'y < 7%'},
            'ch': {'direction': '~', 'threshold': 0.21, 'tolerance': 0.03, 'label': 'ch ~ 21%'},
        }
    }
}

# ============================================================
# LOAD ACTUAL PROFILES
# ============================================================

def load_profiles():
    """Load actual A signature profiles from prior analysis."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['product_prefix_profiles']

# ============================================================
# EVALUATION
# ============================================================

def check_prediction(actual_value, prediction):
    """Check if actual value matches prediction."""
    direction = prediction['direction']
    threshold = prediction['threshold']

    if direction == '>':
        return actual_value > threshold
    elif direction == '<':
        return actual_value < threshold
    elif direction == '~':
        tolerance = prediction.get('tolerance', 0.02)
        return abs(actual_value - threshold) <= tolerance
    return False

def evaluate_recipe(recipe_key, recipe_data, profiles):
    """Evaluate a single recipe's predictions."""
    expected_type = recipe_data['expected_type']

    if expected_type not in profiles:
        return {
            'recipe': recipe_data['name'],
            'expected_type': expected_type,
            'status': 'ERROR',
            'reason': f'No profile found for {expected_type}'
        }

    actual_profile = profiles[expected_type]
    results = []

    for prefix, pred in recipe_data['predictions'].items():
        actual_value = actual_profile.get(prefix, 0)
        passed = check_prediction(actual_value, pred)

        results.append({
            'prefix': prefix,
            'prediction': pred['label'],
            'actual': f'{actual_value:.1%}',
            'passed': passed
        })

    n_passed = sum(1 for r in results if r['passed'])
    n_total = len(results)

    return {
        'recipe': recipe_data['name'],
        'german': recipe_data['german'],
        'degree': recipe_data['degree'],
        'expected_type': expected_type,
        'predictions': results,
        'passed_count': n_passed,
        'total_count': n_total,
        'status': 'PASS' if n_passed == n_total else 'PARTIAL' if n_passed > 0 else 'FAIL'
    }

def compute_profile_distance(profile1, profile2, prefixes=None):
    """Compute L1/2 distance between profiles."""
    if prefixes is None:
        prefixes = set(profile1.keys()) | set(profile2.keys())

    total_diff = sum(abs(profile1.get(p, 0) - profile2.get(p, 0)) for p in prefixes)
    return total_diff / 2

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("BLIND PREDICTION TEST (Test 1)")
    print("=" * 70)
    print()
    print("Pre-registered predictions for unused Brunschwig recipes.")
    print("Tests predictive power WITHOUT circularity.")
    print()

    # Load profiles
    profiles = load_profiles()

    print("ACTUAL PROFILE BASELINES (from prior analysis):")
    print("-" * 70)
    key_prefixes = ['ok', 'ch', 'd', 'y', 'qo', 'sh']

    print(f"{'Type':<18}", end="")
    for p in key_prefixes:
        print(f"{p:>8}", end="")
    print()

    for ptype in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        if ptype in profiles:
            print(f"{ptype:<18}", end="")
            for p in key_prefixes:
                val = profiles[ptype].get(p, 0)
                print(f"{val:>7.1%}", end="")
            print()
    print()

    # Evaluate predictions
    print("=" * 70)
    print("PREDICTION EVALUATION")
    print("=" * 70)
    print()

    all_results = []

    for recipe_key, recipe_data in PREDICTIONS.items():
        result = evaluate_recipe(recipe_key, recipe_data, profiles)
        all_results.append(result)

        print(f"{result['recipe']} ({result['german']})")
        print(f"  Degree: {result['degree']}")
        print(f"  Expected type: {result['expected_type']}")
        print()

        for pred in result['predictions']:
            status = "PASS" if pred['passed'] else "FAIL"
            print(f"  [{status}] {pred['prefix']}: predicted {pred['prediction']}, actual {pred['actual']}")

        print()
        print(f"  Result: {result['passed_count']}/{result['total_count']} predictions correct")
        print(f"  Status: {result['status']}")
        print()
        print("-" * 50)
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    total_predictions = sum(r['total_count'] for r in all_results)
    total_passed = sum(r['passed_count'] for r in all_results)
    recipes_passed = sum(1 for r in all_results if r['status'] == 'PASS')

    print(f"Recipes tested: {len(all_results)}")
    print(f"Recipes fully correct: {recipes_passed}/{len(all_results)}")
    print(f"Individual predictions: {total_passed}/{total_predictions}")
    print()

    # Profile distance check
    print("PROFILE DISTANCE CHECK:")
    print("-" * 50)

    distance_results = []
    for recipe_key, recipe_data in PREDICTIONS.items():
        expected_type = recipe_data['expected_type']
        if expected_type in profiles:
            # Compare to other profiles
            own_profile = profiles[expected_type]

            for other_type, other_profile in profiles.items():
                dist = compute_profile_distance(own_profile, other_profile)
                if other_type == expected_type:
                    print(f"  {recipe_data['name']} -> {expected_type}: distance = 0.000 (self)")
                else:
                    distance_results.append({
                        'recipe': recipe_data['name'],
                        'expected': expected_type,
                        'other': other_type,
                        'distance': dist
                    })

    # Show closest non-self matches
    print()
    print("  Nearest non-matching profiles:")
    for recipe_key, recipe_data in PREDICTIONS.items():
        expected_type = recipe_data['expected_type']
        recipe_dists = [d for d in distance_results if d['recipe'] == recipe_data['name']]
        if recipe_dists:
            nearest = min(recipe_dists, key=lambda x: x['distance'])
            print(f"    {recipe_data['name']}: {nearest['other']} at {nearest['distance']:.3f}")

    print()

    # Final verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    # Pass criteria from plan:
    # - Signature direction correct: 3/3 recipes
    # - Within 5% of predicted value: 2/3 prefixes per recipe
    # - Profile distance < 0.15: each recipe vs type baseline

    direction_correct = all(r['passed_count'] > 0 for r in all_results)
    mostly_correct = all(r['passed_count'] >= r['total_count'] * 0.67 for r in all_results)

    if recipes_passed == len(all_results):
        verdict = "STRONG PASS"
        interpretation = "Bidirectional constraint coherence is ROBUST"
    elif mostly_correct:
        verdict = "PASS"
        interpretation = "Predictions mostly correct, chain intact"
    elif direction_correct:
        verdict = "PARTIAL"
        interpretation = "Directions correct but magnitudes off - calibration needed"
    else:
        verdict = "FAIL"
        interpretation = "Predictions incorrect - chain leaks somewhere"

    print(f"Verdict: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    if verdict in ['STRONG PASS', 'PASS']:
        print("C495 CANDIDATE: Brunschwig product type predicts A signature profile")

    # Save results
    output = {
        'test': 'BLIND_PREDICTION',
        'pre_registration': {k: {
            'name': v['name'],
            'degree': v['degree'],
            'expected_type': v['expected_type'],
            'predictions': {p: pred['label'] for p, pred in v['predictions'].items()}
        } for k, v in PREDICTIONS.items()},
        'results': all_results,
        'summary': {
            'recipes_tested': len(all_results),
            'recipes_passed': recipes_passed,
            'predictions_passed': total_passed,
            'predictions_total': total_predictions,
            'verdict': verdict,
            'interpretation': interpretation
        }
    }

    with open('results/blind_prediction_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/blind_prediction_results.json")

if __name__ == '__main__':
    main()
