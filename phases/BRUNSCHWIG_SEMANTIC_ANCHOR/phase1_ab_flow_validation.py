#!/usr/bin/env python3
"""
PHASE 1: A->B FLOW VALIDATION

Question: Do A folios classified as WATER_GENTLE actually feed B folios in REGIME_2?
          (And similarly for other product types)

Method:
1. Load A folio classifications by product type
2. Extract MIDDLE vocabularies from each A folio
3. Find which B folios share those MIDDLEs
4. Check if activated B folios match expected REGIME

Success criterion: >70% of activated B folios match expected REGIME

REGIME <-> Product Type Mapping (from existing validation):
- REGIME_2 -> WATER_GENTLE (1st degree, balneum)
- REGIME_1 -> WATER_STANDARD (2nd degree)
- REGIME_3 -> OIL_RESIN (3rd degree)
- REGIME_4 -> PRECISION (4th degree)
"""

import csv
import json
from collections import defaultdict, Counter

# ============================================================
# CONFIGURATION
# ============================================================

REGIME_TO_PRODUCT = {
    'REGIME_2': 'WATER_GENTLE',
    'REGIME_1': 'WATER_STANDARD',
    'REGIME_3': 'OIL_RESIN',
    'REGIME_4': 'PRECISION'
}

PRODUCT_TO_REGIME = {v: k for k, v in REGIME_TO_PRODUCT.items()}

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
print("PHASE 1: A->B FLOW VALIDATION")
print("=" * 70)
print()

# Load A folio classifications
with open('results/exclusive_middle_backprop.json', 'r') as f:
    backprop_data = json.load(f)

a_folio_classifications = backprop_data['a_folio_classifications']
print(f"Loaded {len(a_folio_classifications)} A folio classifications")

# Load B REGIME assignments
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Invert: folio -> regime
b_folio_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        b_folio_regime[folio] = regime

print(f"Loaded {len(b_folio_regime)} B folio REGIME assignments")

# Load transcript and extract MIDDLE inventories
a_folio_middles = defaultdict(set)
b_folio_middles = defaultdict(set)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        _, middle, _ = decompose_token(word)

        if middle:
            if language == 'A':
                a_folio_middles[folio].add(middle)
            elif language == 'B':
                b_folio_middles[folio].add(middle)

print(f"Extracted MIDDLEs from {len(a_folio_middles)} A folios, {len(b_folio_middles)} B folios")
print()

# ============================================================
# COMPUTE A->B FLOW
# ============================================================

print("=" * 70)
print("COMPUTING A->B FLOW VIA MIDDLE OVERLAP")
print("=" * 70)
print()

# For each A folio, find B folios with shared MIDDLEs
a_to_b_flow = {}

for a_folio, a_middles in a_folio_middles.items():
    if a_folio not in a_folio_classifications:
        continue

    a_product = a_folio_classifications[a_folio]
    expected_regime = PRODUCT_TO_REGIME.get(a_product)

    if not expected_regime:
        continue

    # Find B folios that share MIDDLEs
    b_matches = []
    for b_folio, b_middles in b_folio_middles.items():
        if b_folio not in b_folio_regime:
            continue

        shared = a_middles & b_middles
        if shared:
            b_regime = b_folio_regime[b_folio]
            b_matches.append({
                'b_folio': b_folio,
                'b_regime': b_regime,
                'shared_count': len(shared),
                'matches_expected': b_regime == expected_regime
            })

    if b_matches:
        a_to_b_flow[a_folio] = {
            'a_product': a_product,
            'expected_regime': expected_regime,
            'b_matches': b_matches,
            'total_b_connections': len(b_matches)
        }

print(f"A folios with B connections: {len(a_to_b_flow)}")
print()

# ============================================================
# VALIDATE FLOW ALIGNMENT
# ============================================================

print("=" * 70)
print("VALIDATING FLOW ALIGNMENT")
print("=" * 70)
print()

# Per-product validation
product_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'by_regime': Counter()})

for a_folio, flow in a_to_b_flow.items():
    product = flow['a_product']
    expected = flow['expected_regime']

    for match in flow['b_matches']:
        product_stats[product]['total'] += 1
        product_stats[product]['by_regime'][match['b_regime']] += 1
        if match['matches_expected']:
            product_stats[product]['correct'] += 1

print("Per-Product A->B Flow Alignment:")
print("-" * 60)

overall_correct = 0
overall_total = 0

for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
    stats = product_stats[product]
    if stats['total'] == 0:
        print(f"{product}: No connections")
        continue

    pct = 100 * stats['correct'] / stats['total']
    print(f"\n{product} (expect {PRODUCT_TO_REGIME[product]}):")
    print(f"  Correct REGIME: {stats['correct']}/{stats['total']} = {pct:.1f}%")
    print(f"  Distribution: {dict(stats['by_regime'])}")

    overall_correct += stats['correct']
    overall_total += stats['total']

print()
print("=" * 70)
overall_pct = 100 * overall_correct / overall_total if overall_total > 0 else 0
print(f"OVERALL A->B FLOW ALIGNMENT: {overall_correct}/{overall_total} = {overall_pct:.1f}%")
print("=" * 70)

# ============================================================
# WEIGHTED ANALYSIS (BY SHARED MIDDLE COUNT)
# ============================================================

print()
print("=" * 70)
print("WEIGHTED ANALYSIS (by shared MIDDLE count)")
print("=" * 70)
print()

weighted_correct = 0
weighted_total = 0

for a_folio, flow in a_to_b_flow.items():
    expected = flow['expected_regime']
    for match in flow['b_matches']:
        weight = match['shared_count']
        weighted_total += weight
        if match['matches_expected']:
            weighted_correct += weight

weighted_pct = 100 * weighted_correct / weighted_total if weighted_total > 0 else 0
print(f"Weighted alignment: {weighted_correct}/{weighted_total} = {weighted_pct:.1f}%")

# ============================================================
# BASELINE COMPARISON
# ============================================================

print()
print("=" * 70)
print("BASELINE COMPARISON")
print("=" * 70)
print()

# Random baseline: each product type maps uniformly to 4 REGIMEs
# Expected accuracy = 25% if flow is random
print(f"Random baseline: 25%")
print(f"Actual: {overall_pct:.1f}%")
print(f"Lift over baseline: {overall_pct - 25:.1f} percentage points")

# Chi-square test
from scipy import stats as scipy_stats

observed = [product_stats[p]['correct'] for p in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']]
totals = [product_stats[p]['total'] for p in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']]
expected_random = [t * 0.25 for t in totals]

try:
    if sum(totals) > 0 and all(e > 0 for e in expected_random):
        chi2, p_value = scipy_stats.chisquare(observed, expected_random)
        print(f"\nChi-square vs random: chi2={chi2:.2f}, p={p_value:.4f}")
        if p_value < 0.05:
            print("Result: SIGNIFICANT (not random)")
        else:
            print("Result: Not significant")
except:
    print("(scipy not available for chi-square test)")

# ============================================================
# SUCCESS CRITERION CHECK
# ============================================================

print()
print("=" * 70)
print("SUCCESS CRITERION CHECK")
print("=" * 70)
print()

SUCCESS_THRESHOLD = 70.0

if overall_pct >= SUCCESS_THRESHOLD:
    print(f"PASS: {overall_pct:.1f}% >= {SUCCESS_THRESHOLD}% threshold")
    status = "PASS"
else:
    print(f"FAIL: {overall_pct:.1f}% < {SUCCESS_THRESHOLD}% threshold")
    status = "FAIL"

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'phase': 'phase1_ab_flow_validation',
    'question': 'Do A folios classified by product type feed B folios in matching REGIMEs?',
    'method': 'MIDDLE vocabulary overlap between A and B folios',
    'regime_product_mapping': REGIME_TO_PRODUCT,
    'summary': {
        'a_folios_tested': len(a_to_b_flow),
        'overall_correct': overall_correct,
        'overall_total': overall_total,
        'overall_pct': overall_pct,
        'weighted_pct': weighted_pct,
        'random_baseline': 25.0,
        'lift_over_baseline': overall_pct - 25.0
    },
    'per_product': {
        product: {
            'correct': product_stats[product]['correct'],
            'total': product_stats[product]['total'],
            'pct': 100 * product_stats[product]['correct'] / product_stats[product]['total'] if product_stats[product]['total'] > 0 else 0,
            'regime_distribution': dict(product_stats[product]['by_regime'])
        }
        for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']
    },
    'success_threshold': SUCCESS_THRESHOLD,
    'status': status
}

with open('results/phase1_ab_flow_validation.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/phase1_ab_flow_validation.json")
