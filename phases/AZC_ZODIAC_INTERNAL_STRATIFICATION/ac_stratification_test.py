#!/usr/bin/env python3
"""
AZC A/C FAMILY INTERNAL STRATIFICATION TEST

Same question as Zodiac test, but for A/C family:
> "Do different A/C AZC folios preferentially admit different regions of
>  Currier-A incompatibility space, and do those regions align with downstream
>  B-inferred product families?"

A/C family is already known to have LOW cross-folio consistency (0.340 vs Zodiac 0.945).
Each folio has its own scaffold. Question: does that variance correlate with product types?
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

# Zodiac AZC folios (to EXCLUDE)
ZODIAC_FOLIOS = {
    'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
    'f57v'
}

# A/C family sections (C430)
AC_SECTIONS = {'A', 'C', 'H', 'S'}

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
print("AZC A/C FAMILY INTERNAL STRATIFICATION TEST")
print("=" * 70)
print()
print("Question: Do different A/C AZC folios preferentially admit different")
print("          regions of the Currier-A incompatibility space?")
print()
print("Note: A/C already has LOW cross-folio consistency (0.340).")
print("      Each folio has its own scaffold. Testing if this correlates")
print("      with product type distribution.")
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

# Load all tokens and identify A/C AZC folios
b_tokens = []
ac_tokens = []
ac_folios_found = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        section = row.get('section', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        prefix, middle, suffix = decompose_token(word)
        entry = {'token': word, 'folio': folio, 'prefix': prefix, 'middle': middle}

        if language == 'B':
            entry['regime'] = folio_regime.get(folio, 'UNKNOWN')
            entry['product'] = get_product_type(entry['regime'])
            b_tokens.append(entry)

        # Check if this is an A/C AZC folio (not Zodiac, in A/C sections, no language tag)
        # AZC folios typically don't have A or B language classification
        if folio not in ZODIAC_FOLIOS and section in AC_SECTIONS and language == '':
            ac_tokens.append(entry)
            ac_folios_found.add(folio)

print(f"Loaded {len(b_tokens)} B tokens")
print(f"Loaded {len(ac_tokens)} A/C AZC tokens")
print(f"A/C folios found: {len(ac_folios_found)}")

if len(ac_folios_found) == 0:
    # Try alternative: look for folios that are not A, not B, not Zodiac
    print("\nNo A/C folios found via section tag. Trying alternative detection...")

    # Re-scan looking for unclassified folios
    ac_tokens = []
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

            # A/C AZC folios: not A, not B, not in Zodiac list
            if language not in ['A', 'B'] and folio not in ZODIAC_FOLIOS:
                prefix, middle, suffix = decompose_token(word)
                entry = {'token': word, 'folio': folio, 'prefix': prefix, 'middle': middle}
                ac_tokens.append(entry)
                ac_folios_found.add(folio)

    print(f"Alternative detection: {len(ac_tokens)} tokens, {len(ac_folios_found)} folios")

AC_FOLIOS = sorted(ac_folios_found)
print(f"\nA/C folios: {AC_FOLIOS}")
print()

if len(AC_FOLIOS) < 2:
    print("ERROR: Not enough A/C folios found for analysis.")
    exit(1)

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

# Find exclusive MIDDLEs
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
# STEP 2: MAP MIDDLES TO A/C FOLIOS
# ============================================================

print("=" * 70)
print("STEP 2: MAPPING PRODUCT-ASSOCIATED MIDDLES TO A/C FOLIOS")
print("=" * 70)
print()

# Build A/C folio MIDDLE inventory
ac_folio_middles = defaultdict(set)
for t in ac_tokens:
    if t['middle']:
        ac_folio_middles[t['folio']].add(t['middle'])

print(f"A/C folios with vocabulary: {len(ac_folio_middles)}")
for folio in AC_FOLIOS:
    count = len(ac_folio_middles.get(folio, set()))
    print(f"  {folio}: {count} unique MIDDLEs")
print()

# For each A/C folio, count product-associated MIDDLEs
folio_product_counts = defaultdict(Counter)
for folio in AC_FOLIOS:
    folio_middles = ac_folio_middles.get(folio, set())
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

products = sorted(exclusive_middles.keys())
contingency_data = []

print("Product-associated MIDDLE counts per A/C folio:")
print()
header = f"{'Folio':<10}" + "".join(f"{p:<18}" for p in products) + "Total"
print(header)
print("-" * len(header))

folio_totals = {}
product_totals = Counter()

for folio in AC_FOLIOS:
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
    for j, folio in enumerate(AC_FOLIOS):
        counts[folio] = contingency_data[j][i]
    entropy = compute_entropy(counts)
    product_entropies[product] = entropy
    max_entropy = math.log2(len(AC_FOLIOS)) if len(AC_FOLIOS) > 0 else 0
    print(f"  {product}: {entropy:.3f} bits (max possible: {max_entropy:.3f})")
print()

# Enrichment analysis
print("Enrichment analysis (which folio is most enriched for each product):")
for product in products:
    idx = products.index(product)
    max_folio = None
    max_count = 0
    total_for_product = product_totals[product]
    for j, folio in enumerate(AC_FOLIOS):
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

contingency_array = np.array(contingency_data)

# Filter out rows/cols with all zeros
row_sums = contingency_array.sum(axis=1)
col_sums = contingency_array.sum(axis=0)
valid_rows = row_sums > 0
valid_cols = col_sums > 0

filtered_array = contingency_array[valid_rows][:, valid_cols]
filtered_folios = [f for f, v in zip(AC_FOLIOS, valid_rows) if v]
filtered_products = [p for p, v in zip(products, valid_cols) if v]

print(f"Contingency table: {filtered_array.shape[0]} folios x {filtered_array.shape[1]} products")
print(f"Active folios: {len(filtered_folios)}")
print(f"Active products: {filtered_products}")
print()

if filtered_array.shape[0] >= 2 and filtered_array.shape[1] >= 2:
    chi2, p_value, dof, expected = stats.chi2_contingency(filtered_array)

    print(f"Chi-squared statistic: {chi2:.2f}")
    print(f"Degrees of freedom: {dof}")
    print(f"P-value: {p_value:.6f}")
    print()

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if p_value < 0.01:
        verdict = "STRONG STRATIFICATION"
        interpretation = "A/C folios show internal legality stratification correlated with downstream product inference"
    elif p_value < 0.05:
        verdict = "WEAK STRATIFICATION"
        interpretation = "A/C stratification exists but is shallow"
    else:
        verdict = "NO STRATIFICATION"
        interpretation = "A/C folio diversity does NOT correlate with product types"

    print(f"Verdict: {verdict}")
    print(f"P-value threshold: p < 0.01 for strong, p < 0.05 for weak")
    print()
    print(f"Interpretation: {interpretation}")
    print()
    print("NOTE: A/C already has diverse scaffolds (consistency=0.340).")
    print("      This tests whether that diversity CORRELATES with products,")
    print("      not whether diversity EXISTS.")
else:
    chi2 = 0
    p_value = 1.0
    dof = 0
    verdict = "INSUFFICIENT DATA"
    interpretation = "Not enough data for chi-squared test"
    print(f"Verdict: {verdict}")

# ============================================================
# COMPARISON WITH ZODIAC
# ============================================================

print()
print("=" * 70)
print("COMPARISON: ZODIAC vs A/C")
print("=" * 70)
print()

# Load Zodiac results if available
try:
    with open('results/zodiac_stratification.json', 'r') as f:
        zodiac_results = json.load(f)
    zodiac_p = zodiac_results['chi_squared']['p_value']
    print(f"Zodiac p-value: {zodiac_p:.4f} (NO STRATIFICATION)")
    print(f"A/C p-value:    {p_value:.4f}")
    print()
    if p_value < 0.05 and zodiac_p > 0.05:
        print("FINDING: A/C shows stratification where Zodiac does not!")
        print("         A/C folio diversity IS product-correlated.")
    elif p_value > 0.05:
        print("FINDING: Neither family shows product-correlated stratification.")
        print("         AZC is uniformly product-agnostic.")
except:
    pass

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "test": "AZC_AC_INTERNAL_STRATIFICATION",
    "question": "Do different A/C AZC folios show product-correlated stratification?",
    "ac_folios_analyzed": AC_FOLIOS,
    "active_folios": filtered_folios,
    "products": filtered_products,
    "exclusive_middle_counts": {p: len(m) for p, m in exclusive_middles.items()},
    "folio_product_matrix": {
        folio: dict(folio_product_counts.get(folio, {}))
        for folio in AC_FOLIOS
    },
    "distribution_entropies": product_entropies,
    "chi_squared": {
        "statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof)
    },
    "verdict": verdict,
    "interpretation": interpretation
}

with open('results/ac_stratification.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to results/ac_stratification.json")
