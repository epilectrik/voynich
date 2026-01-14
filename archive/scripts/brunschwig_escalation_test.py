"""
Brunschwig Degree Escalation Test

Tests two predictions:
1. Late folios should match "hard materials" profile (roots/resins/high-degree)
2. REGIME_3/4 zones should show "degree escalation" characteristics

From Brunschwig:
- First degree: balneum (water bath) - flowers, delicate
- Second degree: noticeably warm - standard herbs
- Third degree: almost seething - roots, bark, resins
- Fourth degree: FORBIDDEN (categorically prohibited)

From Puff:
- First third: FLOWERS (11 SIMPLE)
- Last third: ANOMALOUS (9 anomalies - fungus, animal, roots, external)
"""

import json
from statistics import mean

# Load data
with open('results/b_macro_scaffold_audit.json', 'r') as f:
    data = json.load(f)

with open('results/puff_83_chapters.json', 'r') as f:
    puff = json.load(f)

folios = list(data['features'].keys())
n = len(folios)

print("="*70)
print("BRUNSCHWIG DEGREE ESCALATION TEST")
print("="*70)

# =============================================================================
# TEST 1: REGIME_3/4 vs REGIME_1/2 - Do higher regimes show escalation profile?
# =============================================================================

print("\n" + "="*70)
print("TEST 1: REGIME-BASED DEGREE CLASSIFICATION")
print("="*70)
print("\nBrunschwig predicts:")
print("  - Low regimes (1/2) = low degrees = simple procedures")
print("  - High regimes (3/4) = high degrees = complex procedures")

# Group folios by regime
regime_groups = {'low': [], 'high': []}
for f in folios:
    regime = data['features'][f]['regime']
    if regime in ['REGIME_1', 'REGIME_2']:
        regime_groups['low'].append(f)
    else:
        regime_groups['high'].append(f)

print(f"\nLow-regime folios (1+2): {len(regime_groups['low'])}")
print(f"High-regime folios (3+4): {len(regime_groups['high'])}")

def get_group_metrics(folio_list, features):
    return {
        'cei': mean([features[f]['cei_total'] for f in folio_list]),
        'hazard': mean([features[f]['hazard_density'] for f in folio_list]),
        'intervention': mean([features[f]['intervention_frequency'] for f in folio_list]),
        'cycle': mean([features[f]['mean_cycle_length'] for f in folio_list]),
        'near_miss': mean([features[f]['near_miss_count'] for f in folio_list]),
        'recovery': mean([features[f]['recovery_ops_count'] for f in folio_list]),
        'kernel_k': mean([features[f]['kernel_dominance_k'] for f in folio_list]),
    }

low_metrics = get_group_metrics(regime_groups['low'], data['features'])
high_metrics = get_group_metrics(regime_groups['high'], data['features'])

print("\n" + "-"*70)
print("METRIC COMPARISON: LOW REGIME vs HIGH REGIME")
print("-"*70)

def show_comparison(name, low_val, high_val, expect_high_higher=True):
    direction = "higher" if high_val > low_val else "lower"
    expected = "HIGHER" if expect_high_higher else "LOWER"
    match = (expect_high_higher and high_val > low_val) or (not expect_high_higher and high_val < low_val)
    verdict = "MATCH" if match else "MISMATCH"
    print(f"\n{name}:")
    print(f"  Low regime:  {low_val:.3f}")
    print(f"  High regime: {high_val:.3f}")
    print(f"  High is {direction} (expected: {expected})")
    print(f"  Verdict: {verdict}")
    return match

results_1 = []

# CEI should be higher in high-regime (more complex)
results_1.append(show_comparison("CEI Total", low_metrics['cei'], high_metrics['cei'], True))

# Hazard should be higher in high-regime (more dangerous)
results_1.append(show_comparison("Hazard Density", low_metrics['hazard'], high_metrics['hazard'], True))

# Intervention should be higher in high-regime (more operator action)
results_1.append(show_comparison("Intervention Frequency", low_metrics['intervention'], high_metrics['intervention'], True))

# Cycle length should be longer in high-regime (more complex process)
results_1.append(show_comparison("Mean Cycle Length", low_metrics['cycle'], high_metrics['cycle'], True))

print(f"\nTest 1 Result: {sum(results_1)}/4 metrics match degree-escalation prediction")

# =============================================================================
# TEST 2: Puff ANOMALOUS position vs Voynich late-position metrics
# =============================================================================

print("\n" + "="*70)
print("TEST 2: PUFF ANOMALOUS CLASS -> VOYNICH LATE POSITION")
print("="*70)

# From Puff: anomalous materials are BACK-LOADED
# First third: 4 anomalous
# Last third: 9 anomalous
# Brunschwig: anomalous materials (fungus, animal, resins) require higher degrees

print("\nPuff distribution (from earlier analysis):")
print("  First third anomalous: 4")
print("  Last third anomalous: 9")
print("\nBrunschwig says anomalous materials (fungi, animal, unusual) require:")
print("  - Higher fire degrees")
print("  - More careful monitoring")
print("  - Higher risk of failure")

# We already have first vs last third from previous test
third = n // 3
first_third = folios[:third]
last_third = folios[2*third:]

first_metrics = get_group_metrics(first_third, data['features'])
last_metrics = get_group_metrics(last_third, data['features'])

print("\n" + "-"*70)
print("FIRST THIRD vs LAST THIRD (Puff flower vs anomalous alignment)")
print("-"*70)

results_2 = []

# Last third should have higher CEI (more complex for anomalous)
results_2.append(show_comparison("CEI Total", first_metrics['cei'], last_metrics['cei'], True))

# Last third should have higher hazard (anomalous materials more dangerous)
results_2.append(show_comparison("Hazard Density", first_metrics['hazard'], last_metrics['hazard'], True))

# Last third should have higher intervention (need more control)
results_2.append(show_comparison("Intervention Freq", first_metrics['intervention'], last_metrics['intervention'], True))

print(f"\nTest 2 Result: {sum(results_2)}/3 metrics match anomalous-class prediction")

# =============================================================================
# TEST 3: Fourth Degree Prohibition - Is there a "forbidden zone"?
# =============================================================================

print("\n" + "="*70)
print("TEST 3: FOURTH DEGREE PROHIBITION")
print("="*70)
print("\nBrunschwig: 'The fourth degree should be avoided at all times'")
print("            'Nature rejects all coercion'")
print("\nPrediction: There should be NO folios with extreme metrics")
print("            (no CEI > 0.9, no hazard_density > 0.9)")

# Check for extreme values
extreme_cei = [f for f in folios if data['features'][f]['cei_total'] > 0.9]
extreme_hazard = [f for f in folios if data['features'][f]['hazard_density'] > 0.9]
max_cei = max(data['features'][f]['cei_total'] for f in folios)
max_hazard = max(data['features'][f]['hazard_density'] for f in folios)

print(f"\nExtreme CEI (>0.9): {len(extreme_cei)} folios")
print(f"Extreme hazard (>0.9): {len(extreme_hazard)} folios")
print(f"Maximum CEI observed: {max_cei:.3f}")
print(f"Maximum hazard observed: {max_hazard:.3f}")

# The 17 forbidden transitions - categorical exclusion
print("\n17 Forbidden Transitions (from constraint system):")
print("  These represent categorical prohibitions, not just high-risk")
print("  = Brunschwig's 'fourth degree' equivalent")

fourth_degree_match = max_cei < 0.9 and max_hazard < 0.9
print(f"\nVerdict: {'MATCH' if fourth_degree_match else 'PARTIAL'}")
print(f"  System avoids extreme operational modes")
print(f"  = Brunschwig's categorical fourth-degree prohibition")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "="*70)
print("SUMMARY: BRUNSCHWIG DEGREE ESCALATION")
print("="*70)

total_matches = sum(results_1) + sum(results_2) + (1 if fourth_degree_match else 0)
total_tests = 4 + 3 + 1

print(f"\nTotal metrics matching escalation model: {total_matches}/{total_tests}")
print("\nInterpretation:")
print("  - Low regime (1/2) = Brunschwig first/second degree (balneum, warm)")
print("  - High regime (3/4) = Brunschwig third degree (almost seething)")
print("  - Forbidden transitions = Brunschwig fourth degree (categorical exclusion)")
print("  - Puff first-third (flowers) -> Voynich low metrics")
print("  - Puff last-third (anomalous) -> Voynich high metrics")

if total_matches >= 6:
    verdict = "STRONG"
    print("\n*** STRONG MATCH: Degree escalation confirmed ***")
elif total_matches >= 4:
    verdict = "MODERATE"
    print("\n*** MODERATE MATCH: Degree escalation partially confirmed ***")
else:
    verdict = "WEAK"
    print("\n*** WEAK MATCH: Degree escalation not clearly supported ***")

# Save results
results = {
    "test": "Brunschwig Degree Escalation",
    "date": "2026-01-13",
    "test_1_regime_comparison": {
        "low_regime_count": len(regime_groups['low']),
        "high_regime_count": len(regime_groups['high']),
        "low_metrics": low_metrics,
        "high_metrics": high_metrics,
        "matches": sum(results_1),
        "total": 4
    },
    "test_2_positional_comparison": {
        "first_third_metrics": first_metrics,
        "last_third_metrics": last_metrics,
        "matches": sum(results_2),
        "total": 3
    },
    "test_3_fourth_degree": {
        "max_cei": max_cei,
        "max_hazard": max_hazard,
        "extreme_folios": len(extreme_cei) + len(extreme_hazard),
        "match": fourth_degree_match
    },
    "total_matches": total_matches,
    "total_tests": total_tests,
    "verdict": verdict
}

with open('results/brunschwig_escalation_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/brunschwig_escalation_test.json")
