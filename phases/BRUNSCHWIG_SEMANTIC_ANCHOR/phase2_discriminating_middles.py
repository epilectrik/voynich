#!/usr/bin/env python3
"""
PHASE 2: EXTRACT DISCRIMINATING MIDDLES

Question: Which MIDDLEs are most diagnostic of each product type?

Method:
1. For each product type, compute MIDDLE enrichment ratio (product vs baseline)
2. Rank MIDDLEs by discrimination power
3. Identify top-10 discriminating MIDDLEs per product type
4. Verify they are disjoint across product types

Success criterion: Top discriminating MIDDLEs are disjoint across product types

Uses B folio MIDDLE inventories since product types are defined via REGIME.
"""

import csv
import json
from collections import defaultdict, Counter
import math

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
print("PHASE 2: EXTRACT DISCRIMINATING MIDDLES")
print("=" * 70)
print()

# Load B REGIME assignments
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Invert: folio -> regime
b_folio_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        b_folio_regime[folio] = regime

print(f"Loaded {len(b_folio_regime)} B folio REGIME assignments")

# Load transcript and extract MIDDLE counts per product type
product_middle_counts = defaultdict(Counter)
baseline_middle_counts = Counter()
product_token_totals = defaultdict(int)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()

        if language != 'B' or folio not in b_folio_regime:
            continue

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        _, middle, _ = decompose_token(word)

        if middle:
            regime = b_folio_regime[folio]
            product = REGIME_TO_PRODUCT.get(regime, 'UNKNOWN')
            if product != 'UNKNOWN':
                product_middle_counts[product][middle] += 1
                baseline_middle_counts[middle] += 1
                product_token_totals[product] += 1

total_tokens = sum(product_token_totals.values())
print(f"Processed {total_tokens} B tokens with MIDDLEs")
for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
    print(f"  {product}: {product_token_totals[product]} tokens")
print()

# ============================================================
# COMPUTE ENRICHMENT RATIOS
# ============================================================

print("=" * 70)
print("COMPUTING MIDDLE ENRICHMENT RATIOS")
print("=" * 70)
print()

def compute_enrichment(middle, product):
    """
    Compute log2 enrichment ratio for a MIDDLE in a product.
    Enrichment = (product_freq / product_total) / (baseline_freq / baseline_total)
    """
    product_count = product_middle_counts[product].get(middle, 0)
    baseline_count = baseline_middle_counts.get(middle, 0)

    if baseline_count == 0 or product_count == 0:
        return 0.0

    product_freq = product_count / product_token_totals[product]
    baseline_freq = baseline_count / total_tokens

    ratio = product_freq / baseline_freq
    return math.log2(ratio)

# Compute enrichment for all MIDDLEs
enrichment_scores = defaultdict(dict)
all_middles = set(baseline_middle_counts.keys())

for middle in all_middles:
    for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        enrichment_scores[product][middle] = compute_enrichment(middle, product)

# ============================================================
# EXTRACT TOP DISCRIMINATING MIDDLES
# ============================================================

print("=" * 70)
print("TOP 10 DISCRIMINATING MIDDLES PER PRODUCT TYPE")
print("=" * 70)
print()

MIN_COUNT = 5  # Minimum occurrences to be considered

discriminating_middles = {}

for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
    # Filter to MIDDLEs with sufficient count in this product
    candidates = [
        (m, enrichment_scores[product][m])
        for m in all_middles
        if product_middle_counts[product].get(m, 0) >= MIN_COUNT
    ]

    # Sort by enrichment (highest = most specific to this product)
    candidates.sort(key=lambda x: x[1], reverse=True)

    top_10 = candidates[:10]
    discriminating_middles[product] = [m for m, _ in top_10]

    print(f"\n{product}:")
    print(f"  {'MIDDLE':<15} {'Enrichment':<12} {'Count':<8} {'Baseline %':<12}")
    print(f"  {'-'*47}")

    for middle, enrichment in top_10:
        count = product_middle_counts[product][middle]
        baseline_pct = 100 * baseline_middle_counts[middle] / total_tokens
        print(f"  {middle:<15} {enrichment:>+.3f}        {count:<8} {baseline_pct:.3f}%")

# ============================================================
# CHECK DISJOINTNESS
# ============================================================

print()
print("=" * 70)
print("CHECKING DISJOINTNESS OF TOP DISCRIMINATORS")
print("=" * 70)
print()

# Check for overlaps
products = ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']
overlap_count = 0
total_comparisons = 0

for i, p1 in enumerate(products):
    for p2 in products[i+1:]:
        set1 = set(discriminating_middles[p1])
        set2 = set(discriminating_middles[p2])
        overlap = set1 & set2
        total_comparisons += 1

        if overlap:
            overlap_count += 1
            print(f"OVERLAP: {p1} vs {p2}: {overlap}")
        else:
            print(f"DISJOINT: {p1} vs {p2}")

print()
disjoint_pct = 100 * (total_comparisons - overlap_count) / total_comparisons
print(f"Disjoint pairs: {total_comparisons - overlap_count}/{total_comparisons} = {disjoint_pct:.1f}%")

# ============================================================
# PRODUCT-EXCLUSIVE ANALYSIS
# ============================================================

print()
print("=" * 70)
print("PRODUCT-EXCLUSIVE MIDDLES ANALYSIS")
print("=" * 70)
print()

# Find MIDDLEs that appear in only one product type
middle_products = defaultdict(set)
for product in products:
    for middle in product_middle_counts[product]:
        if product_middle_counts[product][middle] >= MIN_COUNT:
            middle_products[middle].add(product)

exclusive_middles = defaultdict(list)
for middle, prods in middle_products.items():
    if len(prods) == 1:
        exclusive_middles[list(prods)[0]].append(middle)

print(f"MIDDLEs exclusive to each product (min count {MIN_COUNT}):")
for product in products:
    print(f"  {product}: {len(exclusive_middles[product])} exclusive MIDDLEs")

total_qualified = sum(1 for m, p in middle_products.items() if len(p) >= 1)
total_exclusive = sum(len(v) for v in exclusive_middles.values())
exclusive_pct = 100 * total_exclusive / total_qualified if total_qualified > 0 else 0

print(f"\nTotal exclusive: {total_exclusive}/{total_qualified} = {exclusive_pct:.1f}%")

# ============================================================
# SUCCESS CRITERION CHECK
# ============================================================

print()
print("=" * 70)
print("SUCCESS CRITERION CHECK")
print("=" * 70)
print()

# Success: >80% of product pairs have disjoint top-10 discriminators
# AND exclusive percentage > 50%
disjoint_threshold = 80.0
exclusive_threshold = 50.0

status = "PASS" if disjoint_pct >= disjoint_threshold and exclusive_pct >= exclusive_threshold else "FAIL"

print(f"Disjointness: {disjoint_pct:.1f}% (threshold: {disjoint_threshold}%)")
print(f"Exclusivity: {exclusive_pct:.1f}% (threshold: {exclusive_threshold}%)")
print(f"Status: {status}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'phase': 'phase2_discriminating_middles',
    'question': 'Which MIDDLEs are most diagnostic of each product type?',
    'method': 'Log2 enrichment ratio vs baseline frequency',
    'min_count_threshold': MIN_COUNT,
    'summary': {
        'total_tokens': total_tokens,
        'product_tokens': dict(product_token_totals),
        'total_qualified_middles': total_qualified,
        'total_exclusive_middles': total_exclusive,
        'exclusive_pct': exclusive_pct,
        'disjoint_pairs': total_comparisons - overlap_count,
        'total_pairs': total_comparisons,
        'disjoint_pct': disjoint_pct
    },
    'discriminating_middles': discriminating_middles,
    'exclusive_middles': {k: v for k, v in exclusive_middles.items()},
    'exclusive_counts': {k: len(v) for k, v in exclusive_middles.items()},
    'top_10_enrichments': {
        product: [
            {
                'middle': m,
                'enrichment': enrichment_scores[product][m],
                'count': product_middle_counts[product][m],
                'baseline_pct': 100 * baseline_middle_counts[m] / total_tokens
            }
            for m in discriminating_middles[product]
        ]
        for product in products
    },
    'status': status
}

with open('results/phase2_discriminating_middles.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/phase2_discriminating_middles.json")
