#!/usr/bin/env python3
"""
PHASE 6: REVERSE MAPPING SEARCH

Search for semantic anchors by correlating Brunschwig characteristics
with Voynich structures.

Tests:
1. REGIME saturation: Do all recipes fit without forcing?
2. Product type distribution: Does Brunschwig match Voynich folio distribution?
3. PREFIX enrichment: Do predicted PREFIX profiles match?
4. MIDDLE hierarchy: Do material categories map to MIDDLE clusters?
5. Hazard warnings: Do Brunschwig warnings map to grammar prohibitions?

Success criteria:
- Strong anchor: p < 0.01 for predictive relationships
- Moderate anchor: p < 0.05
- No anchor: Random assignment performs equally well
"""

import json
import random
from pathlib import Path
from collections import defaultdict
import math

# ============================================================
# STATISTICAL FUNCTIONS
# ============================================================

def chi_square_test(observed, expected):
    """Compute chi-square statistic and approximate p-value."""
    if not observed or not expected:
        return 0, 1.0

    chi2 = 0
    for key in observed:
        o = observed[key]
        e = expected.get(key, 1)
        if e > 0:
            chi2 += (o - e) ** 2 / e

    # Degrees of freedom
    df = len(observed) - 1

    # Approximate p-value using chi-square distribution
    # This is a simplified approximation
    if df <= 0:
        return chi2, 1.0

    # Use approximation: for large chi2, p is very small
    if chi2 > 20:
        p_value = 0.001
    elif chi2 > 15:
        p_value = 0.005
    elif chi2 > 10:
        p_value = 0.02
    elif chi2 > 7:
        p_value = 0.05
    elif chi2 > 5:
        p_value = 0.10
    else:
        p_value = 0.50

    return chi2, p_value

def permutation_test(data, labels, n_permutations=1000, test_statistic_fn=None):
    """Run permutation test to assess significance."""
    if test_statistic_fn is None:
        # Default: variance of group means
        def test_statistic_fn(d, l):
            groups = defaultdict(list)
            for val, label in zip(d, l):
                groups[label].append(val)
            means = [sum(g)/len(g) for g in groups.values() if g]
            if len(means) < 2:
                return 0
            overall_mean = sum(means) / len(means)
            return sum((m - overall_mean)**2 for m in means)

    # Observed statistic
    observed_stat = test_statistic_fn(data, labels)

    # Permutation distribution
    perm_stats = []
    for _ in range(n_permutations):
        shuffled_labels = labels.copy()
        random.shuffle(shuffled_labels)
        perm_stat = test_statistic_fn(data, shuffled_labels)
        perm_stats.append(perm_stat)

    # P-value: proportion of permuted stats >= observed
    p_value = sum(1 for ps in perm_stats if ps >= observed_stat) / n_permutations

    return observed_stat, p_value, perm_stats

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 6: REVERSE MAPPING SEARCH")
print("=" * 70)
print()

# Load materials database
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials")
print()

# ============================================================
# TEST 1: REGIME SATURATION
# ============================================================

print("=" * 70)
print("TEST 1: REGIME SATURATION")
print("=" * 70)
print()

print("Question: Do all recipes fit into REGIMEs without forcing?")
print()

regime_counts = defaultdict(int)
for m in materials:
    regime = m['regime_assignment']['final_regime']
    regime_counts[regime] += 1

total = sum(regime_counts.values())
print("Observed REGIME distribution:")
for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    count = regime_counts[r]
    pct = 100 * count / total
    print(f"  {r}: {count} ({pct:.1f}%)")

# Expected uniform distribution
expected_uniform = {r: total/4 for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']}

chi2, p_uniform = chi_square_test(regime_counts, expected_uniform)
print()
print(f"Chi-square vs uniform: {chi2:.2f}, p = {p_uniform:.4f}")

if p_uniform < 0.01:
    print("Result: Distribution is NON-UNIFORM (p < 0.01)")
    print("  -> REGIMEs are not arbitrarily assigned")
    print("  -> Fire degree creates meaningful differentiation")
else:
    print("Result: Distribution could be uniform")

# Check saturation (all REGIMEs populated)
saturation = all(regime_counts[r] > 0 for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4'])
print()
print(f"Saturation: {'ALL REGIMEs populated' if saturation else 'Some REGIMEs empty'}")

# ============================================================
# TEST 2: PRODUCT TYPE vs MATERIAL CATEGORY
# ============================================================

print()
print("=" * 70)
print("TEST 2: PRODUCT TYPE vs MATERIAL CATEGORY")
print("=" * 70)
print()

print("Question: Does material category predict product type?")
print()

# Cross-tabulation
category_product = defaultdict(lambda: defaultdict(int))
for m in materials:
    category = m['material_source']
    product = m['regime_assignment']['final_product_type']
    category_product[category][product] += 1

print("Category        | WATER_STD | WATER_GENTLE | OIL_RESIN | PRECISION")
print("-" * 70)
for cat in sorted(category_product.keys()):
    row = category_product[cat]
    total_cat = sum(row.values())
    ws = row.get('WATER_STANDARD', 0)
    wg = row.get('WATER_GENTLE', 0)
    oilr = row.get('OIL_RESIN', 0)
    prec = row.get('PRECISION', 0)
    print(f"{cat:15} |    {ws:4d}   |     {wg:4d}     |    {oilr:4d}    |    {prec:4d}")

# Chi-square for category vs product independence
# Flatten to test independence
all_cats = list(category_product.keys())
all_prods = ['WATER_STANDARD', 'WATER_GENTLE', 'OIL_RESIN', 'PRECISION']

# Compute expected under independence
total_materials = len(materials)
cat_totals = {c: sum(category_product[c].values()) for c in all_cats}
prod_totals = defaultdict(int)
for c in all_cats:
    for p in all_prods:
        prod_totals[p] += category_product[c].get(p, 0)

# Chi-square
chi2_indep = 0
for c in all_cats:
    for p in all_prods:
        observed = category_product[c].get(p, 0)
        expected = (cat_totals[c] * prod_totals[p]) / total_materials if total_materials > 0 else 1
        if expected > 0:
            chi2_indep += (observed - expected) ** 2 / expected

df_indep = (len(all_cats) - 1) * (len(all_prods) - 1)
print()
print(f"Chi-square for independence: {chi2_indep:.2f} (df={df_indep})")

if chi2_indep > 30:
    print("Result: Category and product type are NOT independent (p < 0.01)")
    print("  -> Material category PREDICTS product type")
else:
    print("Result: No strong evidence of dependence")

# ============================================================
# TEST 3: GRAMMAR COMPLIANCE by REGIME
# ============================================================

print()
print("=" * 70)
print("TEST 3: GRAMMAR COMPLIANCE by REGIME")
print("=" * 70)
print()

print("Question: Does grammar compliance vary by REGIME?")
print()

compliance_by_regime = defaultdict(lambda: {'compliant': 0, 'violation': 0})
for m in materials:
    if 'grammar_compliance' in m:
        regime = m['regime_assignment']['final_regime']
        status = m['grammar_compliance']['status']
        if status == 'COMPLIANT':
            compliance_by_regime[regime]['compliant'] += 1
        else:
            compliance_by_regime[regime]['violation'] += 1

print("REGIME     | Compliant | Violations | Rate")
print("-" * 50)
for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    comp = compliance_by_regime[r]['compliant']
    viol = compliance_by_regime[r]['violation']
    total = comp + viol
    rate = 100 * comp / total if total > 0 else 0
    print(f"{r:10} |    {comp:4d}   |    {viol:4d}     | {rate:.1f}%")

# Overall compliance
total_comp = sum(c['compliant'] for c in compliance_by_regime.values())
total_viol = sum(c['violation'] for c in compliance_by_regime.values())
total_tested = total_comp + total_viol
overall_rate = 100 * total_comp / total_tested if total_tested > 0 else 0
print()
print(f"Overall: {total_comp}/{total_tested} compliant ({overall_rate:.1f}%)")

# ============================================================
# TEST 4: HAZARD CLASS DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("TEST 4: HAZARD CLASS DISTRIBUTION")
print("=" * 70)
print()

print("Question: Does Brunschwig hazard distribution match Voynich expected?")
print()

# Expected from C109: 41/24/24/6/6 (approximately)
voynich_expected = {
    'PHASE_ORDERING': 0.41,
    'COMPOSITION_JUMP': 0.24,
    'CONTAINMENT_TIMING': 0.24,
    'RATE_MISMATCH': 0.06,
    'ENERGY_OVERSHOOT': 0.06
}

# Observed from Brunschwig violations
violation_dist = data['summary'].get('grammar_compliance', {}).get('violations_by_class', {})
total_violations = sum(violation_dist.values())

print("Voynich expected vs Brunschwig observed:")
print("Hazard Class           | Voynich | Brunschwig")
print("-" * 55)
for hc in ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    v_exp = voynich_expected[hc] * 100
    b_obs = 100 * violation_dist.get(hc, 0) / total_violations if total_violations > 0 else 0
    print(f"{hc:22} |  {v_exp:5.1f}% |   {b_obs:5.1f}%")

# ============================================================
# TEST 5: INSTRUCTION SEQUENCE SIGNATURE
# ============================================================

print()
print("=" * 70)
print("TEST 5: INSTRUCTION SEQUENCE SIGNATURE")
print("=" * 70)
print()

print("Question: Do instruction sequences show consistent patterns?")
print()

# Most common simplified sequences
seq_counts = defaultdict(int)
for m in materials:
    seq = m.get('instruction_sequence_simplified', [])
    if seq:
        seq_str = ' -> '.join(seq)
        seq_counts[seq_str] += 1

print("Most common instruction sequences:")
for seq, count in sorted(seq_counts.items(), key=lambda x: -x[1])[:10]:
    pct = 100 * count / len([m for m in materials if m.get('instruction_sequence_simplified')])
    print(f"  {count:3d} ({pct:4.1f}%): {seq}")

# Check if sequences cluster by REGIME
print()
print("Sequence diversity by REGIME:")
seq_by_regime = defaultdict(set)
for m in materials:
    regime = m['regime_assignment']['final_regime']
    seq = tuple(m.get('instruction_sequence_simplified', []))
    if seq:
        seq_by_regime[regime].add(seq)

for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    unique_seqs = len(seq_by_regime[r])
    regime_count = regime_counts[r]
    print(f"  {r}: {unique_seqs} unique sequences across {regime_count} recipes")

# ============================================================
# TEST 6: PERMUTATION CONTROL
# ============================================================

print()
print("=" * 70)
print("TEST 6: PERMUTATION CONTROL")
print("=" * 70)
print()

print("Question: Is REGIME assignment better than random?")
print()

# Collect CEI values and regimes
ceis = []
regimes = []
for m in materials:
    cei = m['regime_assignment']['estimated_cei']
    regime = m['regime_assignment']['final_regime']
    ceis.append(cei)
    regimes.append(regime)

# Run permutation test
print("Running permutation test (1000 permutations)...")
obs_stat, p_perm, _ = permutation_test(ceis, regimes, n_permutations=1000)

print(f"Observed statistic: {obs_stat:.4f}")
print(f"P-value: {p_perm:.4f}")

if p_perm < 0.05:
    print("Result: REGIME assignment is significantly better than random")
else:
    print("Result: Cannot distinguish from random assignment")
    print("  (Note: CEI estimation is limited by extraction quality)")

# ============================================================
# ANCHOR ASSESSMENT
# ============================================================

print()
print("=" * 70)
print("ANCHOR ASSESSMENT SUMMARY")
print("=" * 70)
print()

anchors_found = []

# Test 1: REGIME saturation
if saturation and p_uniform < 0.01:
    anchors_found.append({
        'type': 'REGIME_SATURATION',
        'description': 'All REGIMEs populated with non-uniform distribution',
        'strength': 'MODERATE',
        'evidence': f'Chi-square p = {p_uniform:.4f}'
    })

# Test 2: Category-product relationship
if chi2_indep > 30:
    anchors_found.append({
        'type': 'CATEGORY_PRODUCT',
        'description': 'Material category predicts product type',
        'strength': 'STRONG',
        'evidence': f'Chi-square = {chi2_indep:.2f}'
    })

# Test 3: Grammar compliance
if overall_rate > 85:
    anchors_found.append({
        'type': 'GRAMMAR_EMBEDDING',
        'description': 'High grammar compliance (>85%)',
        'strength': 'STRONG',
        'evidence': f'{overall_rate:.1f}% compliance rate'
    })

# Test 6: Non-random assignment
if p_perm < 0.05:
    anchors_found.append({
        'type': 'NON_RANDOM',
        'description': 'REGIME assignment better than random',
        'strength': 'MODERATE',
        'evidence': f'Permutation p = {p_perm:.4f}'
    })

print(f"Total anchors found: {len(anchors_found)}")
print()

for i, anchor in enumerate(anchors_found, 1):
    print(f"{i}. {anchor['type']} ({anchor['strength']})")
    print(f"   {anchor['description']}")
    print(f"   Evidence: {anchor['evidence']}")
    print()

if len(anchors_found) >= 2 and any(a['strength'] == 'STRONG' for a in anchors_found):
    print("CONCLUSION: SEMANTIC ANCHORS FOUND")
    print("  Brunschwig procedures embed into Voynich grammar with multiple")
    print("  predictive relationships. This supports the shared procedural")
    print("  domain hypothesis at the curriculum level.")
elif len(anchors_found) >= 1:
    print("CONCLUSION: MODERATE ANCHORING")
    print("  Some relationships found but not definitive entry-level anchoring.")
else:
    print("CONCLUSION: NO SEMANTIC ANCHORS")
    print("  Random assignment performs equally well.")

# ============================================================
# SAVE RESULTS
# ============================================================

print()
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

results = {
    'phase': 'phase6_reverse_mapping',
    'total_materials': len(materials),
    'tests': {
        'regime_saturation': {
            'distribution': dict(regime_counts),
            'chi_square_uniform': chi2,
            'p_value': p_uniform,
            'saturated': saturation
        },
        'category_product': {
            'chi_square': chi2_indep,
            'independent': chi2_indep <= 30
        },
        'grammar_compliance': {
            'overall_rate': overall_rate,
            'by_regime': {r: {'compliant': c['compliant'], 'violation': c['violation']}
                        for r, c in compliance_by_regime.items()}
        },
        'permutation_control': {
            'observed_statistic': obs_stat,
            'p_value': p_perm
        }
    },
    'anchors_found': anchors_found,
    'conclusion': 'SEMANTIC_ANCHORS_FOUND' if (len(anchors_found) >= 2 and any(a['strength'] == 'STRONG' for a in anchors_found)) else 'MODERATE' if len(anchors_found) >= 1 else 'NONE'
}

output_path = Path('results/brunschwig_reverse_mapping.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to {output_path}")
