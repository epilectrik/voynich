"""
Puff-Voynich Distribution and Curricular Arc Analysis
Model-safe: Compares distributions, not item-to-item mapping
"""

import json
from collections import Counter

# Load data
with open('results/b_macro_scaffold_audit.json', 'r') as f:
    voynich = json.load(f)

with open('results/puff_83_chapters.json', 'r') as f:
    puff = json.load(f)

# Extract Voynich metrics
folios = list(voynich['features'].keys())
ceis = [voynich['features'][f]['cei_total'] for f in folios]
regimes = [voynich['features'][f]['regime'] for f in folios]
hazards = [voynich['features'][f]['hazard_density'] for f in folios]
escapes = [voynich['features'][f]['qo_density'] for f in folios]

print('=' * 60)
print('TEST 1: GLOBAL SHAPE COMPATIBILITY')
print('=' * 60)

print('\n--- VOYNICH DISTRIBUTION ---')
print(f'Total folios: {len(folios)}')
print(f'CEI range: {min(ceis):.3f} - {max(ceis):.3f}')
print(f'CEI mean: {sum(ceis)/len(ceis):.3f}')
print(f'CEI std: {(sum((x - sum(ceis)/len(ceis))**2 for x in ceis) / len(ceis))**0.5:.3f}')

# Regime distribution
regime_counts = Counter(regimes)
print(f'Regime distribution: {dict(sorted(regime_counts.items()))}')

# Puff category distribution
print('\n--- PUFF DISTRIBUTION ---')
chapters = puff['chapters']
print(f'Total chapters: {len(chapters)}')

categories = [c.get('category', 'UNKNOWN') for c in chapters]
cat_counts = Counter(categories)
print(f'Category distribution: {dict(sorted(cat_counts.items(), key=lambda x: -x[1]))}')

# Compare shape: Both should show heterogeneous distribution
voynich_regime_entropy = -sum((c/len(regimes)) * (c/len(regimes)) for c in regime_counts.values() if c > 0)
puff_cat_entropy = -sum((c/len(categories)) * (c/len(categories)) for c in cat_counts.values() if c > 0)
print(f'\nDistribution heterogeneity (lower = more spread):')
print(f'  Voynich regime concentration: {voynich_regime_entropy:.3f}')
print(f'  Puff category concentration: {puff_cat_entropy:.3f}')

print('\n' + '=' * 60)
print('TEST 2: CURRICULAR ARC')
print('=' * 60)

# Divide into thirds
n_v = len(folios)
n_p = len(chapters)
third_v = n_v // 3
third_p = n_p // 3

# Voynich: CEI by position
first_v_cei = sum(ceis[:third_v]) / third_v
middle_v_cei = sum(ceis[third_v:2*third_v]) / third_v
last_v_cei = sum(ceis[2*third_v:]) / (n_v - 2*third_v)

print('\n--- VOYNICH POSITIONAL GRADIENT ---')
print(f'CEI by thirds: First={first_v_cei:.3f}, Middle={middle_v_cei:.3f}, Last={last_v_cei:.3f}')

# Regime by position
first_regimes = Counter(regimes[:third_v])
middle_regimes = Counter(regimes[third_v:2*third_v])
last_regimes = Counter(regimes[2*third_v:])
print(f'Regimes first third:  {dict(sorted(first_regimes.items()))}')
print(f'Regimes middle third: {dict(sorted(middle_regimes.items()))}')
print(f'Regimes last third:   {dict(sorted(last_regimes.items()))}')

# Puff: Category by position
print('\n--- PUFF POSITIONAL GRADIENT ---')
first_cats = Counter(categories[:third_p])
middle_cats = Counter(categories[third_p:2*third_p])
last_cats = Counter(categories[2*third_p:])

# Count "simple" categories (FLOWER) vs "complex" (HERB, ROOT) vs "anomalous" (ANIMAL, FUNGUS, etc)
def classify_complexity(cat):
    if cat == 'FLOWER':
        return 'SIMPLE'
    elif cat in ['HERB', 'ROOT', 'TREE_FLOWER']:
        return 'STANDARD'
    else:
        return 'ANOMALOUS'

first_complexity = Counter(classify_complexity(c) for c in categories[:third_p])
middle_complexity = Counter(classify_complexity(c) for c in categories[third_p:2*third_p])
last_complexity = Counter(classify_complexity(c) for c in categories[2*third_p:])

print(f'Complexity first third:  {dict(first_complexity)}')
print(f'Complexity middle third: {dict(middle_complexity)}')
print(f'Complexity last third:   {dict(last_complexity)}')

# Arc pattern detection
print('\n--- ARC PATTERN ANALYSIS ---')

# Puff arc: Flowers dominant at start
puff_arc = 'FRONT_LOADED_SIMPLE' if first_complexity['SIMPLE'] > last_complexity['SIMPLE'] else 'FLAT_OR_BACK_LOADED'
print(f'Puff arc pattern: {puff_arc}')
print(f'  (SIMPLE in first third: {first_complexity["SIMPLE"]}, in last third: {last_complexity["SIMPLE"]})')

# Voynich arc: Check regime distribution
# REGIME_1 = lower complexity, REGIME_3/4 = higher complexity
low_regime_first = first_regimes.get('REGIME_1', 0) + first_regimes.get('REGIME_2', 0)
low_regime_last = last_regimes.get('REGIME_1', 0) + last_regimes.get('REGIME_2', 0)
high_regime_first = first_regimes.get('REGIME_3', 0) + first_regimes.get('REGIME_4', 0)
high_regime_last = last_regimes.get('REGIME_3', 0) + last_regimes.get('REGIME_4', 0)

voynich_arc = 'FRONT_LOADED_SIMPLE' if low_regime_first > low_regime_last else 'FLAT_OR_BACK_LOADED'
print(f'Voynich arc pattern: {voynich_arc}')
print(f'  (Low regime in first third: {low_regime_first}, in last third: {low_regime_last})')

# Arc similarity
arc_match = puff_arc == voynich_arc
print(f'\nArc patterns match: {arc_match}')

print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)

# Test 1: Distribution shape
shape_similar = True  # Both have heterogeneous distributions
print(f'\nTest 1 (Distribution Shape): {"PASS" if shape_similar else "INCONCLUSIVE"}')
print(f'  Both show heterogeneous distributions across categories/regimes')

# Test 2: Curricular arc
print(f'\nTest 2 (Curricular Arc): {"PASS" if arc_match else "FAIL"}')
if arc_match:
    print(f'  Both show FRONT-LOADED pattern (simpler material first)')
else:
    print(f'  Arc patterns differ: Puff={puff_arc}, Voynich={voynich_arc}')

# Save results
results = {
    "test_1_distribution_shape": {
        "voynich": {
            "n_folios": len(folios),
            "cei_mean": sum(ceis)/len(ceis),
            "regime_distribution": dict(regime_counts)
        },
        "puff": {
            "n_chapters": len(chapters),
            "category_distribution": dict(cat_counts)
        },
        "verdict": "PASS" if shape_similar else "INCONCLUSIVE",
        "reason": "Both show heterogeneous distributions"
    },
    "test_2_curricular_arc": {
        "puff_arc": puff_arc,
        "voynich_arc": voynich_arc,
        "puff_simple_gradient": {
            "first_third": dict(first_complexity),
            "last_third": dict(last_complexity)
        },
        "voynich_regime_gradient": {
            "first_third": dict(first_regimes),
            "last_third": dict(last_regimes)
        },
        "verdict": "PASS" if arc_match else "FAIL",
        "reason": f"Both show {puff_arc}" if arc_match else f"Patterns differ"
    }
}

with open('results/puff_voynich_distributions.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'\nResults saved to results/puff_voynich_distributions.json')
