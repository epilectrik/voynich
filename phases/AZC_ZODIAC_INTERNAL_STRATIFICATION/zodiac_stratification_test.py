#!/usr/bin/env python3
"""
AZC ZODIAC INTERNAL STRATIFICATION TEST

Question (corrected framing):
> "Do different Zodiac AZC folios preferentially admit different regions of
>  Currier-A incompatibility space, and do those regions align with downstream
>  B-inferred product families?"

This is NOT a test of "product routing through gates."
AZC filters constraint bundles; product types are downstream inferences.

Method:
1. Extract product-associated MIDDLEs from B folios (by REGIME classification)
2. Map those MIDDLEs to Zodiac AZC folios
3. Test for stratification via chi-squared

Interpretation:
- Strong clustering → Zodiac has internal legality stratification
- No clustering → Zodiac multiplicity = pure coverage optimality
"""

import csv
import json
import math
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qok', 'qot', 'qo', 'ch', 'sh', 'ok', 'ot', 'ct', 'ol', 'or', 'al', 'ar', 's', 'k', 'd', 'y', 'o', 'a']

# Zodiac AZC folios (C431: 12 zodiac + f57v)
ZODIAC_FOLIOS = [
    'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
    'f57v'
]

def decompose_token(token):
    """Extract MIDDLE component from token."""
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    # Simple suffix stripping
    suffix = ''
    suffixes = ['dy', 'ey', 'ly', 'ry', 'y']
    for s in suffixes:
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return (prefix, token, suffix)

def get_product_type(regime):
    """Map REGIME to product type."""
    mapping = {
        'REGIME_2': 'WATER_GENTLE',
        'REGIME_1': 'WATER_STANDARD',
        'REGIME_3': 'OIL_RESIN',
        'REGIME_4': 'PRECISION'
    }
    return mapping.get(regime, 'UNKNOWN')

def compute_entropy(counts):
    """Compute Shannon entropy of a distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("AZC ZODIAC INTERNAL STRATIFICATION TEST")
print("=" * 70)
print()
print("Question: Do different Zodiac folios preferentially admit different")
print("          regions of the Currier-A incompatibility space?")
print()

# Load REGIME assignments for B folios
folio_regime = {}
with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
    for line in f:
        parts = line.split('|')
        if len(parts) >= 3:
            folio = parts[1].strip()
            regime = parts[2].strip()
            if folio.startswith('f') and regime.startswith('REGIME'):
                folio_regime[folio] = regime

# Load all tokens from transcription
b_tokens = []
zodiac_tokens = []

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

        prefix, middle, suffix = decompose_token(word)

        entry = {'token': word, 'folio': folio, 'prefix': prefix, 'middle': middle}

        if language == 'B':
            entry['regime'] = folio_regime.get(folio, 'UNKNOWN')
            entry['product'] = get_product_type(entry['regime'])
            b_tokens.append(entry)

        # Check if this is a Zodiac folio
        if folio in ZODIAC_FOLIOS:
            zodiac_tokens.append(entry)

print(f"Loaded {len(b_tokens)} B tokens")
print(f"Loaded {len(zodiac_tokens)} Zodiac AZC tokens")
print()

# ============================================================
# STEP 1: EXTRACT PRODUCT-ASSOCIATED MIDDLES
# ============================================================

print("=" * 70)
print("STEP 1: EXTRACTING PRODUCT-ASSOCIATED MIDDLES FROM B")
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

print("Product-exclusive MIDDLEs in B:")
for product in sorted(exclusive_middles.keys()):
    print(f"  {product}: {len(exclusive_middles[product])} exclusive MIDDLEs")

total_exclusive = sum(len(m) for m in exclusive_middles.values())
print(f"\nTotal exclusive: {total_exclusive}/{len(all_middles)} ({100*total_exclusive/len(all_middles):.1f}%)")
print()

# ============================================================
# STEP 2: MAP MIDDLES TO ZODIAC FOLIOS
# ============================================================

print("=" * 70)
print("STEP 2: MAPPING PRODUCT-ASSOCIATED MIDDLES TO ZODIAC FOLIOS")
print("=" * 70)
print()

# Build Zodiac folio MIDDLE inventory
zodiac_folio_middles = defaultdict(set)
for t in zodiac_tokens:
    if t['middle']:
        zodiac_folio_middles[t['folio']].add(t['middle'])

print(f"Zodiac folios with vocabulary: {len(zodiac_folio_middles)}")
for folio in ZODIAC_FOLIOS:
    count = len(zodiac_folio_middles.get(folio, set()))
    print(f"  {folio}: {count} unique MIDDLEs")
print()

# For each Zodiac folio, count product-associated MIDDLEs
folio_product_counts = defaultdict(Counter)
for folio in ZODIAC_FOLIOS:
    folio_middles = zodiac_folio_middles.get(folio, set())
    for product, excl_middles in exclusive_middles.items():
        overlap = len(folio_middles & excl_middles)
        if overlap > 0:
            folio_product_counts[folio][product] = overlap

# ============================================================
# STEP 3: COMPUTE STRATIFICATION METRICS
# ============================================================

print("=" * 70)
print("STEP 3: STRATIFICATION METRICS")
print("=" * 70)
print()

# Build contingency table for chi-squared
products = sorted(exclusive_middles.keys())
contingency_data = []

print("Product-associated MIDDLE counts per Zodiac folio:")
print()
header = f"{'Folio':<10}" + "".join(f"{p:<18}" for p in products) + "Total"
print(header)
print("-" * len(header))

folio_totals = {}
product_totals = Counter()

for folio in ZODIAC_FOLIOS:
    counts = folio_product_counts.get(folio, Counter())
    row = [counts.get(p, 0) for p in products]
    total = sum(row)
    folio_totals[folio] = total
    for p, c in zip(products, row):
        product_totals[p] += c
    contingency_data.append(row)

    row_str = f"{folio:<10}" + "".join(f"{c:<18}" for c in row) + f"{total}"
    print(row_str)

print("-" * len(header))
totals_row = f"{'Total':<10}" + "".join(f"{product_totals[p]:<18}" for p in products) + f"{sum(product_totals.values())}"
print(totals_row)
print()

# Distribution entropy per product
print("Distribution entropy per product (higher = more spread):")
product_entropies = {}
for i, product in enumerate(products):
    counts = Counter()
    for j, folio in enumerate(ZODIAC_FOLIOS):
        counts[folio] = contingency_data[j][i]
    entropy = compute_entropy(counts)
    product_entropies[product] = entropy
    max_entropy = math.log2(len(ZODIAC_FOLIOS)) if len(ZODIAC_FOLIOS) > 0 else 0
    print(f"  {product}: {entropy:.3f} bits (max possible: {max_entropy:.3f})")
print()

# Enrichment: which folio is most enriched for each product?
print("Enrichment analysis (which folio is most enriched for each product):")
for product in products:
    idx = products.index(product)
    max_folio = None
    max_count = 0
    total_for_product = product_totals[product]
    for j, folio in enumerate(ZODIAC_FOLIOS):
        count = contingency_data[j][idx]
        if count > max_count:
            max_count = count
            max_folio = folio
    if total_for_product > 0:
        pct = 100 * max_count / total_for_product
        print(f"  {product}: {max_folio} has {max_count}/{total_for_product} ({pct:.1f}%)")
print()

# ============================================================
# STEP 4: STATISTICAL TEST
# ============================================================

print("=" * 70)
print("STEP 4: CHI-SQUARED TEST OF INDEPENDENCE")
print("=" * 70)
print()

# Convert to numpy array for chi-squared test
contingency_array = np.array(contingency_data)

# Filter out rows/cols with all zeros
row_sums = contingency_array.sum(axis=1)
col_sums = contingency_array.sum(axis=0)
valid_rows = row_sums > 0
valid_cols = col_sums > 0

filtered_array = contingency_array[valid_rows][:, valid_cols]
filtered_folios = [f for f, v in zip(ZODIAC_FOLIOS, valid_rows) if v]
filtered_products = [p for p, v in zip(products, valid_cols) if v]

print(f"Contingency table: {filtered_array.shape[0]} folios × {filtered_array.shape[1]} products")
print(f"Active folios: {filtered_folios}")
print(f"Active products: {filtered_products}")
print()

if filtered_array.shape[0] >= 2 and filtered_array.shape[1] >= 2:
    chi2, p_value, dof, expected = stats.chi2_contingency(filtered_array)

    print(f"Chi-squared statistic: {chi2:.2f}")
    print(f"Degrees of freedom: {dof}")
    print(f"P-value: {p_value:.6f}")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if p_value < 0.01:
        verdict = "STRONG STRATIFICATION"
        interpretation = "Zodiac has internal legality stratification correlated with downstream product inference"
    elif p_value < 0.05:
        verdict = "WEAK STRATIFICATION"
        interpretation = "Zodiac stratification exists but is shallow"
    else:
        verdict = "NO STRATIFICATION"
        interpretation = "Zodiac multiplicity exists purely for coverage optimality"

    print(f"Verdict: {verdict}")
    print(f"P-value threshold: p < 0.01 for strong, p < 0.05 for weak")
    print()
    print(f"Interpretation: {interpretation}")
    print()

    # Reminder of correct framing
    print("NOTE: This is NOT 'product routing'. AZC filters constraint bundles;")
    print("      product types are downstream inferences from B behavior.")
else:
    chi2 = 0
    p_value = 1.0
    dof = 0
    expected = []
    verdict = "INSUFFICIENT DATA"
    interpretation = "Not enough data for chi-squared test"
    print(f"Verdict: {verdict}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "test": "AZC_ZODIAC_INTERNAL_STRATIFICATION",
    "question": "Do different Zodiac folios preferentially admit different regions of Currier-A incompatibility space?",
    "framing_note": "This is NOT product routing. AZC filters constraint bundles; product types are downstream inferences.",
    "zodiac_folios_analyzed": ZODIAC_FOLIOS,
    "active_folios": filtered_folios,
    "products": filtered_products,
    "exclusive_middle_counts": {p: len(m) for p, m in exclusive_middles.items()},
    "folio_product_matrix": {
        folio: dict(folio_product_counts.get(folio, {}))
        for folio in ZODIAC_FOLIOS
    },
    "distribution_entropies": product_entropies,
    "chi_squared": {
        "statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof)
    },
    "verdict": verdict,
    "interpretation": interpretation,
    "outcome_key": {
        "STRONG_STRATIFICATION": "p < 0.01 - Zodiac has internal legality stratification",
        "WEAK_STRATIFICATION": "0.01 < p < 0.05 - Stratification exists but shallow",
        "NO_STRATIFICATION": "p > 0.05 - Zodiac multiplicity = coverage optimality"
    }
}

with open('results/zodiac_stratification.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to results/zodiac_stratification.json")
