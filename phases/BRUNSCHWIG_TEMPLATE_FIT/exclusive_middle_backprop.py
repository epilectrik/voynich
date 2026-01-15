#!/usr/bin/env python3
"""
EXCLUSIVE MIDDLE BACKWARD PROPAGATION

We found 78.2% of MIDDLEs are product-exclusive in B.
Question: Do A records that contain product-exclusive MIDDLEs
          show distinctive profiles for each product type?

Method:
1. Identify MIDDLEs exclusive to each product type (in B)
2. Find which A folios contain those exclusive MIDDLEs
3. Compare A profiles for folios containing different exclusive sets
"""

import csv
import json
from collections import defaultdict, Counter

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def decompose_token(token):
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    return (prefix, token, '')

def get_product_type(regime):
    if regime == 'REGIME_2':
        return 'WATER_GENTLE'
    elif regime == 'REGIME_1':
        return 'WATER_STANDARD'
    elif regime == 'REGIME_3':
        return 'OIL_RESIN'
    elif regime == 'REGIME_4':
        return 'PRECISION'
    return 'UNKNOWN'

# ============================================================
# LOAD DATA
# ============================================================

# Load REGIME assignments
folio_regime = {}
with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
    for line in f:
        parts = line.split('|')
        if len(parts) >= 3:
            folio = parts[1].strip()
            regime = parts[2].strip()
            if folio.startswith('f') and regime.startswith('REGIME'):
                folio_regime[folio] = regime

# Load all tokens
a_tokens = []
b_tokens = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        prefix, middle, _ = decompose_token(word)

        entry = {'token': word, 'folio': folio, 'prefix': prefix, 'middle': middle}

        if language == 'A':
            a_tokens.append(entry)
        elif language == 'B':
            entry['regime'] = folio_regime.get(folio, 'UNKNOWN')
            entry['product'] = get_product_type(entry['regime'])
            b_tokens.append(entry)

print(f"Loaded {len(a_tokens)} A tokens, {len(b_tokens)} B tokens")
print()

# ============================================================
# FIND PRODUCT-EXCLUSIVE MIDDLES
# ============================================================

print("=" * 70)
print("IDENTIFYING PRODUCT-EXCLUSIVE MIDDLES")
print("=" * 70)
print()

# Group B MIDDLEs by product type
product_middles = defaultdict(set)
for t in b_tokens:
    if t['middle'] and t['product'] != 'UNKNOWN':
        product_middles[t['product']].add(t['middle'])

# Find exclusive MIDDLEs (appear in only one product type)
all_middles = set()
for middles in product_middles.values():
    all_middles.update(middles)

middle_products = defaultdict(set)
for product, middles in product_middles.items():
    for m in middles:
        middle_products[m].add(product)

exclusive_middles = defaultdict(set)
for m, products in middle_products.items():
    if len(products) == 1:
        product = list(products)[0]
        exclusive_middles[product].add(m)

for product in sorted(exclusive_middles.keys()):
    print(f"{product}: {len(exclusive_middles[product])} exclusive MIDDLEs")

total_exclusive = sum(len(m) for m in exclusive_middles.values())
print(f"\nTotal exclusive: {total_exclusive}/{len(all_middles)} ({100*total_exclusive/len(all_middles):.1f}%)")
print()

# ============================================================
# TRACE EXCLUSIVE MIDDLES BACK TO A
# ============================================================

print("=" * 70)
print("TRACING EXCLUSIVE MIDDLES TO CURRIER A")
print("=" * 70)
print()

# Build A folio MIDDLE inventory
a_folio_middles = defaultdict(set)
for t in a_tokens:
    if t['middle']:
        a_folio_middles[t['folio']].add(t['middle'])

# For each A folio, count how many exclusive MIDDLEs it has for each product
a_folio_product_scores = defaultdict(Counter)
for a_folio, middles in a_folio_middles.items():
    for product, excl_middles in exclusive_middles.items():
        overlap = len(middles & excl_middles)
        if overlap > 0:
            a_folio_product_scores[a_folio][product] = overlap

# Classify A folios by dominant product signal
a_folio_classification = {}
for a_folio, scores in a_folio_product_scores.items():
    if scores:
        total = sum(scores.values())
        dominant = max(scores.items(), key=lambda x: x[1])
        dominance = dominant[1] / total if total > 0 else 0
        a_folio_classification[a_folio] = {
            'dominant_product': dominant[0],
            'dominance': dominance,
            'scores': dict(scores),
            'total_exclusive': total
        }

# Show classification results
print("A folio classification by exclusive MIDDLE content:")
print()

classified_counts = Counter(c['dominant_product'] for c in a_folio_classification.values())
for product, count in sorted(classified_counts.items()):
    print(f"  {product}: {count} A folios")

print(f"\n  Unclassified: {len(a_folio_middles) - len(a_folio_classification)} A folios")
print()

# ============================================================
# COMPARE A PROFILES BY PRODUCT CLASSIFICATION
# ============================================================

print("=" * 70)
print("A PREFIX PROFILES BY PRODUCT CLASSIFICATION")
print("=" * 70)
print()

# Group A tokens by their folio's product classification
product_a_tokens = defaultdict(list)
for t in a_tokens:
    classification = a_folio_classification.get(t['folio'])
    if classification:
        product_a_tokens[classification['dominant_product']].append(t)

# Compute PREFIX distribution for each product group
for product in sorted(product_a_tokens.keys()):
    tokens = product_a_tokens[product]
    prefix_counts = Counter(t['prefix'] for t in tokens if t['prefix'])
    total = sum(prefix_counts.values())

    n_folios = len(set(t['folio'] for t in tokens))
    print(f"{product} (n={total} tokens in {n_folios} folios):")

    for p in ['qo', 'ch', 'y', 'sh', 'd', 'ok', 'ot', 'ol', 'or']:
        pct = 100 * prefix_counts.get(p, 0) / total if total > 0 else 0
        if pct > 1:
            bar = '#' * int(pct / 2)
            print(f"  {p:3s}: {pct:5.1f}% {bar}")
    print()

# ============================================================
# STATISTICAL TEST: DO PRODUCTS DIFFER?
# ============================================================

print("=" * 70)
print("PRODUCT DISCRIMINATION TEST")
print("=" * 70)
print()

# Calculate profile vectors
product_profiles = {}
for product, tokens in product_a_tokens.items():
    prefix_counts = Counter(t['prefix'] for t in tokens if t['prefix'])
    total = sum(prefix_counts.values())
    if total > 0:
        product_profiles[product] = {p: prefix_counts.get(p, 0) / total for p in KNOWN_PREFIXES}

# Pairwise differences
print("Profile distances (L1 / 2):")
products = sorted(product_profiles.keys())
for i, p1 in enumerate(products):
    for p2 in products[i+1:]:
        diff = sum(abs(product_profiles[p1].get(p, 0) - product_profiles[p2].get(p, 0))
                   for p in KNOWN_PREFIXES) / 2
        print(f"  {p1} vs {p2}: {diff:.3f}")

print()

# Key discriminators
print("Key discriminating prefixes:")
for prefix in ['y', 'qo', 'ch', 'd', 'sh', 'or']:
    values = {p: 100 * profile.get(prefix, 0) for p, profile in product_profiles.items()}
    if values:
        max_p = max(values.items(), key=lambda x: x[1])
        min_p = min(values.items(), key=lambda x: x[1])
        if max_p[1] > 0 and min_p[1] > 0:
            ratio = max_p[1] / min_p[1]
            if ratio > 1.5:
                print(f"  {prefix}: {max_p[0]} ({max_p[1]:.1f}%) vs {min_p[0]} ({min_p[1]:.1f}%) = {ratio:.1f}x")

# ============================================================
# SPECIFIC PRODUCT SIGNATURES
# ============================================================

print()
print("=" * 70)
print("PRODUCT-SPECIFIC A SIGNATURES")
print("=" * 70)
print()

# Focus on the most interesting comparisons
if 'PRECISION' in product_profiles and 'OIL_RESIN' in product_profiles:
    prec = product_profiles['PRECISION']
    oil = product_profiles['OIL_RESIN']

    print("PRECISION vs OIL_RESIN (key contrast):")
    for p in ['y', 'qo', 'ch', 'd', 'or', 'ok']:
        prec_pct = 100 * prec.get(p, 0)
        oil_pct = 100 * oil.get(p, 0)
        diff = prec_pct - oil_pct
        if abs(diff) > 2:
            direction = "+" if diff > 0 else ""
            print(f"  {p:3s}: PRECISION={prec_pct:5.1f}%, OIL_RESIN={oil_pct:5.1f}% ({direction}{diff:.1f}%)")
    print()

if 'WATER_GENTLE' in product_profiles and 'WATER_STANDARD' in product_profiles:
    gentle = product_profiles['WATER_GENTLE']
    standard = product_profiles['WATER_STANDARD']

    print("WATER_GENTLE vs WATER_STANDARD:")
    for p in ['y', 'qo', 'ch', 'd', 'or', 'ok']:
        g_pct = 100 * gentle.get(p, 0)
        s_pct = 100 * standard.get(p, 0)
        diff = g_pct - s_pct
        if abs(diff) > 2:
            direction = "+" if diff > 0 else ""
            print(f"  {p:3s}: GENTLE={g_pct:5.1f}%, STANDARD={s_pct:5.1f}% ({direction}{diff:.1f}%)")
    print()

# ============================================================
# CONCLUSION
# ============================================================

print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

# Check if y-prefix shows expected pattern
y_values = {p: 100 * profile.get('y', 0) for p, profile in product_profiles.items()}
if y_values:
    max_y = max(y_values.items(), key=lambda x: x[1])
    min_y = min(y_values.items(), key=lambda x: x[1])

    print(f"y-prefix range: {min_y[0]}={min_y[1]:.1f}% to {max_y[0]}={max_y[1]:.1f}%")

    if max_y[0] == 'PRECISION' or max_y[0] == 'WATER_GENTLE':
        print("  -> EXPECTED: y-prefix highest in precision/gentle products")
        print("     (monitoring required for tight tolerances)")
    else:
        print(f"  -> UNEXPECTED: y-prefix highest in {max_y[0]}")
    print()

# Overall finding
profile_diffs = []
for i, p1 in enumerate(products):
    for p2 in products[i+1:]:
        diff = sum(abs(product_profiles[p1].get(p, 0) - product_profiles[p2].get(p, 0))
                   for p in KNOWN_PREFIXES) / 2
        profile_diffs.append(diff)

mean_diff = sum(profile_diffs) / len(profile_diffs) if profile_diffs else 0

if mean_diff > 0.1:
    print(f"FINDING: A records show PRODUCT-SPECIFIC profiles (mean diff={mean_diff:.3f})")
    print()
    print("The two-level model is SUPPORTED:")
    print("  Level 1 (Entry): Individual tokens encode parameters")
    print("  Level 2 (Record): A records containing product-exclusive MIDDLEs")
    print("                    show distinctive PREFIX signatures")
else:
    print(f"FINDING: A record profiles are similar across products (mean diff={mean_diff:.3f})")

# Save results
results = {
    'exclusive_middle_counts': {p: len(m) for p, m in exclusive_middles.items()},
    'a_folio_classifications': {f: c['dominant_product'] for f, c in a_folio_classification.items()},
    'product_prefix_profiles': {p: {k: round(v, 4) for k, v in prof.items()}
                                for p, prof in product_profiles.items()},
    'mean_profile_difference': mean_diff
}

with open('results/exclusive_middle_backprop.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to results/exclusive_middle_backprop.json")
