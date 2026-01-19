#!/usr/bin/env python3
"""
PHASE 3: MATERIAL INCOMPATIBILITY ALIGNMENT

Question: Do MIDDLE incompatibilities align with real material processing incompatibilities?

Brunschwig's material groupings by fire degree:
- 1st degree (balneum/WATER_GENTLE): rose, lavender, violets (gentle aromatics)
- 2nd degree (warm/WATER_STANDARD): sage, mint, rue (standard waters)
- 3rd degree (seething/OIL_RESIN): juniper, turpentine, pine (resins/oils)
- 4th degree (PRECISION): exact timing operations

From chemistry: Gentle aromatics (1st) are destroyed by high heat required for resins (3rd).
These are processing-INCOMPATIBLE.

Prediction: If MIDDLEs encode material compatibility, then:
- WATER_GENTLE MIDDLEs should be highly INCOMPATIBLE with OIL_RESIN MIDDLEs
- Same-product MIDDLEs should be more COMPATIBLE with each other

Method:
1. Extract MIDDLEs per product type (from B folios)
2. Check cross-product incompatibility rates
3. Compare with same-product incompatibility rates

Success criterion: WATER_GENTLE x OIL_RESIN incompatibility > 95% and higher than same-product rates
"""

import csv
import json
from collections import defaultdict, Counter
from itertools import combinations

# ============================================================
# CONFIGURATION
# ============================================================

REGIME_TO_PRODUCT = {
    'REGIME_2': 'WATER_GENTLE',
    'REGIME_1': 'WATER_STANDARD',
    'REGIME_3': 'OIL_RESIN',
    'REGIME_4': 'PRECISION'
}

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def decompose_token(token):
    """Extract MIDDLE from token."""
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    return (prefix, token, '')

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 3: MATERIAL INCOMPATIBILITY ALIGNMENT")
print("=" * 70)
print()

# Load MIDDLE incompatibility from existing analysis
# Note: The incompatibility data is line-based co-occurrence from AZC folios
# We'll compute this fresh from B folio data

# Load B REGIME assignments
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

b_folio_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        b_folio_regime[folio] = regime

print(f"Loaded {len(b_folio_regime)} B folio REGIME assignments")

# Load transcript and extract line-level co-occurrence
product_middles = defaultdict(set)
line_middles = defaultdict(set)  # (folio, line_num) -> set of middles

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        line_num = row.get('line', '').strip()

        if language != 'B' or folio not in b_folio_regime:
            continue

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        _, middle, _ = decompose_token(word)

        if middle:
            regime = b_folio_regime[folio]
            product = REGIME_TO_PRODUCT.get(regime, 'UNKNOWN')
            if product != 'UNKNOWN':
                product_middles[product].add(middle)
                line_middles[(folio, line_num)].add(middle)

print(f"MIDDLEs per product type:")
for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
    print(f"  {product}: {len(product_middles[product])} unique MIDDLEs")
print()

# ============================================================
# BUILD CO-OCCURRENCE MATRIX
# ============================================================

print("=" * 70)
print("BUILDING CO-OCCURRENCE MATRIX")
print("=" * 70)
print()

# MIDDLEs that co-occur on same line are COMPATIBLE
cooccurrence_pairs = set()
all_middles = set()

for (folio, line_num), middles in line_middles.items():
    all_middles.update(middles)
    for m1, m2 in combinations(middles, 2):
        pair = tuple(sorted([m1, m2]))
        cooccurrence_pairs.add(pair)

total_middles = len(all_middles)
total_possible_pairs = total_middles * (total_middles - 1) // 2
compatible_pairs = len(cooccurrence_pairs)

print(f"Total unique MIDDLEs in B: {total_middles}")
print(f"Total possible pairs: {total_possible_pairs}")
print(f"Compatible pairs (co-occur): {compatible_pairs}")
print(f"Incompatible pairs: {total_possible_pairs - compatible_pairs}")
print(f"Incompatibility rate: {100 * (1 - compatible_pairs/total_possible_pairs):.1f}%")
print()

# ============================================================
# COMPUTE CROSS-PRODUCT INCOMPATIBILITY
# ============================================================

print("=" * 70)
print("CROSS-PRODUCT INCOMPATIBILITY RATES")
print("=" * 70)
print()

def compute_incompatibility_rate(set1, set2):
    """
    Compute what percentage of pairs from set1 x set2 are INCOMPATIBLE
    (i.e., never co-occur on the same line)
    """
    if not set1 or not set2:
        return 0.0, 0, 0

    total_pairs = 0
    incompatible = 0

    for m1 in set1:
        for m2 in set2:
            if m1 == m2:
                continue
            total_pairs += 1
            pair = tuple(sorted([m1, m2]))
            if pair not in cooccurrence_pairs:
                incompatible += 1

    if total_pairs == 0:
        return 0.0, 0, 0

    return incompatible / total_pairs, incompatible, total_pairs

products = ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']
cross_product_rates = {}

print(f"{'Product 1':<20} {'Product 2':<20} {'Incompatibility':<15} {'Pairs':<10}")
print("-" * 70)

# Cross-product incompatibility
for i, p1 in enumerate(products):
    for p2 in products[i:]:
        rate, incompat, total = compute_incompatibility_rate(
            product_middles[p1], product_middles[p2]
        )
        key = f"{p1} x {p2}" if p1 != p2 else f"{p1} (self)"
        cross_product_rates[key] = {
            'rate': rate,
            'incompatible': incompat,
            'total': total
        }
        print(f"{p1:<20} {p2:<20} {100*rate:>6.1f}%         {total:<10}")

# ============================================================
# KEY TEST: WATER_GENTLE vs OIL_RESIN
# ============================================================

print()
print("=" * 70)
print("KEY TEST: WATER_GENTLE vs OIL_RESIN")
print("=" * 70)
print()

# Brunschwig chemistry: gentle aromatics (1st degree) destroyed by high heat (3rd degree)
# These should be processing-INCOMPATIBLE

gentle_resin_key = "WATER_GENTLE x OIL_RESIN"
gentle_resin_rate = cross_product_rates[gentle_resin_key]['rate']

print(f"WATER_GENTLE x OIL_RESIN incompatibility: {100*gentle_resin_rate:.1f}%")
print()

# Compare with same-product rates
gentle_self_rate = cross_product_rates["WATER_GENTLE (self)"]['rate']
resin_self_rate = cross_product_rates["OIL_RESIN (self)"]['rate']

print(f"WATER_GENTLE self-incompatibility: {100*gentle_self_rate:.1f}%")
print(f"OIL_RESIN self-incompatibility: {100*resin_self_rate:.1f}%")
print()

# Cross-product should be HIGHER than self-incompatibility if materials matter
cross_vs_self_gentle = gentle_resin_rate - gentle_self_rate
cross_vs_self_resin = gentle_resin_rate - resin_self_rate

print(f"Cross vs GENTLE self: {100*cross_vs_self_gentle:+.1f} percentage points")
print(f"Cross vs RESIN self: {100*cross_vs_self_resin:+.1f} percentage points")

# ============================================================
# SUCCESS CRITERION CHECK
# ============================================================

print()
print("=" * 70)
print("SUCCESS CRITERION CHECK")
print("=" * 70)
print()

# Success criteria:
# 1. WATER_GENTLE x OIL_RESIN > 95%
# 2. Cross-product incompatibility > same-product incompatibility

threshold_95 = gentle_resin_rate >= 0.95
higher_than_self = (cross_vs_self_gentle > 0) and (cross_vs_self_resin > 0)

print(f"Criterion 1: GENTLE x RESIN >= 95%")
print(f"  Result: {100*gentle_resin_rate:.1f}% {'PASS' if threshold_95 else 'FAIL'}")
print()
print(f"Criterion 2: Cross > Self-incompatibility")
print(f"  vs GENTLE self: {100*cross_vs_self_gentle:+.1f}% {'PASS' if cross_vs_self_gentle > 0 else 'FAIL'}")
print(f"  vs RESIN self: {100*cross_vs_self_resin:+.1f}% {'PASS' if cross_vs_self_resin > 0 else 'FAIL'}")

status = "PASS" if threshold_95 and higher_than_self else "FAIL"
print()
print(f"Overall Status: {status}")

# ============================================================
# BRUNSCHWIG ALIGNMENT INTERPRETATION
# ============================================================

print()
print("=" * 70)
print("BRUNSCHWIG ALIGNMENT INTERPRETATION")
print("=" * 70)
print()

if threshold_95:
    print("MIDDLE incompatibility between WATER_GENTLE and OIL_RESIN")
    print("aligns with Brunschwig's material processing incompatibility:")
    print()
    print("  Brunschwig: Gentle aromatics (1st degree) require balneum.")
    print("  Brunschwig: Resins (3rd degree) require seething heat.")
    print("  Chemistry: These processes are mutually exclusive.")
    print()
    print(f"  Voynich: {100*gentle_resin_rate:.1f}% of GENTLE/RESIN MIDDLE pairs never co-occur.")

if not higher_than_self:
    print()
    print("NOTE: Cross-product incompatibility is NOT higher than self-incompatibility.")
    print("This suggests MIDDLEs have uniform high incompatibility regardless of product type.")
    print("The incompatibility may encode operational constraints, not material constraints.")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'phase': 'phase3_material_incompatibility',
    'question': 'Do MIDDLE incompatibilities align with material processing incompatibilities?',
    'method': 'Line-level co-occurrence in B folios by REGIME/product type',
    'brunschwig_prediction': {
        'statement': 'WATER_GENTLE (1st degree) and OIL_RESIN (3rd degree) should be highly incompatible',
        'reasoning': 'Gentle aromatics destroyed by high heat required for resins'
    },
    'summary': {
        'total_middles': total_middles,
        'total_possible_pairs': total_possible_pairs,
        'compatible_pairs': compatible_pairs,
        'overall_incompatibility_rate': 1 - compatible_pairs/total_possible_pairs
    },
    'cross_product_rates': cross_product_rates,
    'key_test': {
        'gentle_resin_rate': gentle_resin_rate,
        'gentle_self_rate': gentle_self_rate,
        'resin_self_rate': resin_self_rate,
        'cross_vs_gentle_self': cross_vs_self_gentle,
        'cross_vs_resin_self': cross_vs_self_resin,
        'threshold_met': threshold_95,
        'higher_than_self': higher_than_self
    },
    'status': status
}

with open('results/phase3_material_incompatibility.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/phase3_material_incompatibility.json")
