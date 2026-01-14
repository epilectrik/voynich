"""
Brunschwig Flower Class Test
Tests whether Voynich's first-third folios match Brunschwig's "simplest class" profile:
- Balneum (water bath) = lowest fire = first degree
- Single pass = minimal intervention
- Minimal hazards

If curricular arc holds, first third should show simpler metrics.
"""

import json
from statistics import mean, stdev

# Load B scaffold data
with open('results/b_macro_scaffold_audit.json', 'r') as f:
    data = json.load(f)

folios = list(data['features'].keys())
n = len(folios)
third = n // 3

first_third = folios[:third]
middle_third = folios[third:2*third]
last_third = folios[2*third:]

print(f"Total folios: {n}")
print(f"First third: {len(first_third)} folios ({first_third[0]} to {first_third[-1]})")
print(f"Last third: {len(last_third)} folios ({last_third[0]} to {last_third[-1]})")

# Extract metrics per third
def get_metrics(folio_list, features):
    metrics = {
        'cei': [],
        'hazard_density': [],
        'near_miss': [],
        'recovery_ops': [],
        'mean_cycle': [],
        'intervention_freq': [],
        'regime_1_count': 0,
        'regime_2_count': 0,
        'regime_3_count': 0,
        'regime_4_count': 0
    }
    for f in folio_list:
        feat = features[f]
        metrics['cei'].append(feat['cei_total'])
        metrics['hazard_density'].append(feat['hazard_density'])
        metrics['near_miss'].append(feat['near_miss_count'])
        metrics['recovery_ops'].append(feat['recovery_ops_count'])
        metrics['mean_cycle'].append(feat['mean_cycle_length'])
        metrics['intervention_freq'].append(feat['intervention_frequency'])

        regime = feat['regime']
        if regime == 'REGIME_1': metrics['regime_1_count'] += 1
        elif regime == 'REGIME_2': metrics['regime_2_count'] += 1
        elif regime == 'REGIME_3': metrics['regime_3_count'] += 1
        elif regime == 'REGIME_4': metrics['regime_4_count'] += 1

    return metrics

first_metrics = get_metrics(first_third, data['features'])
last_metrics = get_metrics(last_third, data['features'])

print("\n" + "="*60)
print("BRUNSCHWIG FLOWER CLASS TEST")
print("="*60)
print("\nIf Voynich follows Brunschwig's 'flowers = simplest' pattern:")
print("- First third should have LOWER CEI (simpler)")
print("- First third should have LOWER hazard_density (safer)")
print("- First third should have FEWER near_miss events")
print("- First third should have MORE recovery_ops (easier recovery)")
print("- First third should have SHORTER cycles (faster process)")
print("- First third should have MORE REGIME_1/2 (simpler regimes)")

print("\n" + "-"*60)
print("METRIC COMPARISON: FIRST THIRD vs LAST THIRD")
print("-"*60)

def compare(name, first_vals, last_vals, expect_first_lower=True):
    f_mean = mean(first_vals)
    l_mean = mean(last_vals)
    direction = "v" if f_mean < l_mean else "^"
    expected = "LOWER" if expect_first_lower else "HIGHER"
    actual = "lower" if f_mean < l_mean else "higher"
    verdict = "MATCH" if (expect_first_lower and f_mean < l_mean) or (not expect_first_lower and f_mean > l_mean) else "MISMATCH"
    print(f"\n{name}:")
    print(f"  First third: {f_mean:.3f}")
    print(f"  Last third:  {l_mean:.3f}")
    print(f"  Direction: First is {actual} ({direction})")
    print(f"  Expected: First should be {expected}")
    print(f"  Verdict: {verdict}")
    return verdict == "MATCH"

results = []

# CEI - expect first lower (simpler)
results.append(compare("CEI Total", first_metrics['cei'], last_metrics['cei'], True))

# Hazard density - expect first lower (safer flowers)
results.append(compare("Hazard Density", first_metrics['hazard_density'], last_metrics['hazard_density'], True))

# Near miss - expect first lower (fewer close calls)
results.append(compare("Near Miss Count", first_metrics['near_miss'], last_metrics['near_miss'], True))

# Recovery ops - expect first HIGHER (easier to recover, more opportunities)
results.append(compare("Recovery Ops", first_metrics['recovery_ops'], last_metrics['recovery_ops'], False))

# Mean cycle - expect first shorter (faster process)
results.append(compare("Mean Cycle Length", first_metrics['mean_cycle'], last_metrics['mean_cycle'], True))

# Intervention frequency - expect first LOWER (minimal intervention for flowers)
results.append(compare("Intervention Frequency", first_metrics['intervention_freq'], last_metrics['intervention_freq'], True))

print("\n" + "-"*60)
print("REGIME DISTRIBUTION")
print("-"*60)
print(f"\nFirst third (Brunschwig 'flower' class prediction: REGIME_1/2 dominant):")
print(f"  REGIME_1: {first_metrics['regime_1_count']}")
print(f"  REGIME_2: {first_metrics['regime_2_count']}")
print(f"  REGIME_3: {first_metrics['regime_3_count']}")
print(f"  REGIME_4: {first_metrics['regime_4_count']}")
low_regime_first = first_metrics['regime_1_count'] + first_metrics['regime_2_count']
high_regime_first = first_metrics['regime_3_count'] + first_metrics['regime_4_count']

print(f"\nLast third (prediction: REGIME_3/4 more common):")
print(f"  REGIME_1: {last_metrics['regime_1_count']}")
print(f"  REGIME_2: {last_metrics['regime_2_count']}")
print(f"  REGIME_3: {last_metrics['regime_3_count']}")
print(f"  REGIME_4: {last_metrics['regime_4_count']}")
low_regime_last = last_metrics['regime_1_count'] + last_metrics['regime_2_count']
high_regime_last = last_metrics['regime_3_count'] + last_metrics['regime_4_count']

print(f"\nSummary:")
print(f"  Low regime (1+2) in first third: {low_regime_first}/{len(first_third)} ({100*low_regime_first/len(first_third):.1f}%)")
print(f"  Low regime (1+2) in last third:  {low_regime_last}/{len(last_third)} ({100*low_regime_last/len(last_third):.1f}%)")
regime_match = low_regime_first > low_regime_last
results.append(regime_match)
print(f"  Verdict: {'MATCH' if regime_match else 'MISMATCH'} - {'First has more low-regime' if regime_match else 'Last has more low-regime'}")

print("\n" + "="*60)
print("OVERALL VERDICT")
print("="*60)
matches = sum(results)
total = len(results)
print(f"\nMetrics matching Brunschwig 'flower = simple' prediction: {matches}/{total}")

if matches >= 5:
    print("\n*** STRONG MATCH ***")
    print("Voynich first-third profiles align with Brunschwig's 'flowers/balneum' class:")
    print("- Lower complexity (CEI)")
    print("- Lower hazards")
    print("- Simpler regime distribution")
    print("This supports: Voynich curricular arc matches Brunschwig's procedural structure")
elif matches >= 4:
    print("\n*** MODERATE MATCH ***")
    print("Majority of metrics align with Brunschwig 'flower' prediction")
else:
    print("\n*** WEAK/NO MATCH ***")
    print("Voynich first-third does not clearly show 'simple flower' profile")

# Save results
results_data = {
    "test": "Brunschwig Flower Class Structural Match",
    "hypothesis": "If curricular arc holds, first third should match 'flowers/balneum' profile",
    "brunschwig_prediction": {
        "first_degree": "balneum (water bath)",
        "material": "flowers, delicate herbs",
        "characteristics": ["lowest fire", "single pass", "minimal hazards", "easy recovery"]
    },
    "first_third": {
        "folios": first_third,
        "n": len(first_third),
        "cei_mean": mean(first_metrics['cei']),
        "hazard_density_mean": mean(first_metrics['hazard_density']),
        "near_miss_mean": mean(first_metrics['near_miss']),
        "recovery_ops_mean": mean(first_metrics['recovery_ops']),
        "mean_cycle_mean": mean(first_metrics['mean_cycle']),
        "intervention_freq_mean": mean(first_metrics['intervention_freq']),
        "regime_distribution": {
            "REGIME_1": first_metrics['regime_1_count'],
            "REGIME_2": first_metrics['regime_2_count'],
            "REGIME_3": first_metrics['regime_3_count'],
            "REGIME_4": first_metrics['regime_4_count']
        }
    },
    "last_third": {
        "folios": last_third,
        "n": len(last_third),
        "cei_mean": mean(last_metrics['cei']),
        "hazard_density_mean": mean(last_metrics['hazard_density']),
        "near_miss_mean": mean(last_metrics['near_miss']),
        "recovery_ops_mean": mean(last_metrics['recovery_ops']),
        "mean_cycle_mean": mean(last_metrics['mean_cycle']),
        "intervention_freq_mean": mean(last_metrics['intervention_freq']),
        "regime_distribution": {
            "REGIME_1": last_metrics['regime_1_count'],
            "REGIME_2": last_metrics['regime_2_count'],
            "REGIME_3": last_metrics['regime_3_count'],
            "REGIME_4": last_metrics['regime_4_count']
        }
    },
    "matches": matches,
    "total_tests": total,
    "verdict": "STRONG" if matches >= 5 else "MODERATE" if matches >= 4 else "WEAK"
}

with open('results/brunschwig_flower_test.json', 'w') as f:
    json.dump(results_data, f, indent=2)

print(f"\nResults saved to results/brunschwig_flower_test.json")
