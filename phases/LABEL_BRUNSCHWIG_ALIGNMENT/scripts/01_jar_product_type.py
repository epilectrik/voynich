"""
01_jar_product_type.py - Test if jar MIDDLEs cluster by Brunschwig product type

Question: Do jar label MIDDLEs cluster by Brunschwig product type?

Method:
1. Extract jar MIDDLEs from PHARMA_LABEL_DECODING
2. For each MIDDLE, find its B folio distribution
3. Map B folios to REGIME
4. REGIME -> Fire degree -> Product type
5. Test if jar MIDDLEs cluster by inferred product type

Product type mapping (from BRSC):
- REGIME 1 -> Fire degree 2 -> WATER_STANDARD
- REGIME 2 -> Fire degree 1 -> WATER_GENTLE
- REGIME 3 -> Fire degree 3 -> OIL_RESIN
- REGIME 4 -> Fire degree 4 -> PRECISION (animal)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 1: JAR MIDDLES -> BRUNSCHWIG PRODUCT TYPE")
print("="*70)

# Product type mapping from BRSC
REGIME_TO_PRODUCT = {
    1: 'WATER_STANDARD',  # Fire degree 2
    2: 'WATER_GENTLE',    # Fire degree 1
    3: 'OIL_RESIN',       # Fire degree 3
    4: 'PRECISION'        # Fire degree 4 (animal)
}

# ============================================================
# STEP 1: LOAD FOLIO REGIME PROFILES
# ============================================================
print("\n--- Step 1: Loading Folio REGIME Profiles ---")

# Build REGIME assignment per folio from B tokens
folio_regimes = {}

# We need to determine REGIME for each folio
# Use kernel profiles as proxy (from existing constraint system)
# Simplified: use qo_density and FQ patterns

folio_profiles = defaultdict(lambda: {'k': 0, 'e': 0, 'h': 0, 'total': 0})

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    folio_profiles[t.folio]['total'] += 1

    # Check kernel presence
    if 'k' in m.middle:
        folio_profiles[t.folio]['k'] += 1
    if 'e' in m.middle:
        folio_profiles[t.folio]['e'] += 1
    if 'h' in m.middle or 'ch' in m.middle or 'sh' in m.middle:
        folio_profiles[t.folio]['h'] += 1

# Assign REGIME based on kernel dominance (simplified)
for folio, profile in folio_profiles.items():
    total = profile['total']
    if total == 0:
        continue

    k_rate = profile['k'] / total
    e_rate = profile['e'] / total
    h_rate = profile['h'] / total

    # Simplified REGIME assignment based on kernel profiles
    # R1: Standard (balanced)
    # R2: Gentle (high e, low k)
    # R3: Intense (high k)
    # R4: Precision (low h, high k+e)

    if k_rate > 0.15:  # High k -> R3 or R4
        if h_rate < 0.10:
            folio_regimes[folio] = 4  # Precision
        else:
            folio_regimes[folio] = 3  # Intense
    elif e_rate > 0.12:  # High e -> R2
        folio_regimes[folio] = 2  # Gentle
    else:
        folio_regimes[folio] = 1  # Standard

print(f"Folios with REGIME assignment: {len(folio_regimes)}")
regime_dist = Counter(folio_regimes.values())
print(f"REGIME distribution: {dict(regime_dist)}")

# ============================================================
# STEP 2: LOAD JAR LABELS
# ============================================================
print("\n--- Step 2: Loading Jar Labels ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

jar_labels = []

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            jar_labels.append({
                'token': jar,
                'folio': folio,
                'row': group.get('row', 0)
            })

print(f"Jar labels loaded: {len(jar_labels)}")

# ============================================================
# STEP 3: EXTRACT JAR MIDDLES AND FIND B DISTRIBUTION
# ============================================================
print("\n--- Step 3: Jar MIDDLEs -> B Folio Distribution ---")

# Build MIDDLE -> B folio mapping
middle_to_b_folios = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        middle_to_b_folios[m.middle][t.folio] += 1

# For each jar label, extract MIDDLE and find B distribution
jar_analysis = []

for jar in jar_labels:
    m = morph.extract(jar['token'])
    if not m or not m.middle:
        continue

    middle = m.middle
    b_folios = middle_to_b_folios.get(middle, {})

    if not b_folios:
        # Try substring match for compound MIDDLEs
        for pp_middle in middle_to_b_folios.keys():
            if len(pp_middle) >= 2 and pp_middle in middle:
                b_folios = middle_to_b_folios[pp_middle]
                middle = pp_middle  # Use the matched PP
                break

    if not b_folios:
        continue

    # Map B folios to REGIMEs
    regime_counts = Counter()
    for b_folio, count in b_folios.items():
        regime = folio_regimes.get(b_folio, 1)  # Default to R1
        regime_counts[regime] += count

    # Determine dominant product type
    total_b = sum(regime_counts.values())
    product_scores = {}
    for regime, count in regime_counts.items():
        product = REGIME_TO_PRODUCT[regime]
        product_scores[product] = count / total_b if total_b > 0 else 0

    dominant_product = max(product_scores, key=product_scores.get) if product_scores else 'UNKNOWN'

    jar_analysis.append({
        'jar': jar['token'],
        'folio': jar['folio'],
        'middle': middle,
        'b_folio_count': len(b_folios),
        'total_b_tokens': total_b,
        'regime_distribution': dict(regime_counts),
        'product_scores': product_scores,
        'dominant_product': dominant_product
    })

print(f"Jar labels with B connections: {len(jar_analysis)}")

# ============================================================
# STEP 4: PRODUCT TYPE CLUSTERING ANALYSIS
# ============================================================
print("\n--- Step 4: Product Type Clustering ---")

# Count dominant product types
product_counts = Counter(j['dominant_product'] for j in jar_analysis)

print("\nDominant product type distribution:")
for product, count in product_counts.most_common():
    pct = 100 * count / len(jar_analysis) if jar_analysis else 0
    print(f"  {product}: {count} ({pct:.1f}%)")

# Test against uniform distribution
expected = len(jar_analysis) / 4  # 4 product types
observed = [product_counts.get(p, 0) for p in ['WATER_STANDARD', 'WATER_GENTLE', 'OIL_RESIN', 'PRECISION']]

chi2, p_value = stats.chisquare(observed, [expected] * 4)

print(f"\nChi-square test (uniform null):")
print(f"  Chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.4f}")
print(f"  {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'} (p < 0.05)")

# ============================================================
# STEP 5: DETAILED JAR -> PRODUCT MAPPING
# ============================================================
print("\n--- Step 5: Jar -> Product Type Details ---")

print(f"\n{'Jar Label':<15} {'MIDDLE':<10} {'B Folios':<10} {'Dominant Product'}")
print("-" * 55)
for j in sorted(jar_analysis, key=lambda x: x['dominant_product'])[:20]:
    print(f"{j['jar']:<15} {j['middle']:<10} {j['b_folio_count']:<10} {j['dominant_product']}")

# ============================================================
# STEP 6: PER-FOLIO JAR CLUSTERING
# ============================================================
print("\n--- Step 6: Per-Folio Jar Product Distribution ---")

folio_jar_products = defaultdict(list)
for j in jar_analysis:
    folio_jar_products[j['folio']].append(j['dominant_product'])

print(f"\n{'Folio':<10} {'Jars':<6} {'Products'}")
print("-" * 40)
for folio in sorted(folio_jar_products.keys()):
    products = folio_jar_products[folio]
    product_str = ', '.join(Counter(products).keys())
    print(f"{folio:<10} {len(products):<6} {product_str}")

# Check if jars on same folio have same product type
same_product_folios = 0
total_multi_jar_folios = 0

for folio, products in folio_jar_products.items():
    if len(products) > 1:
        total_multi_jar_folios += 1
        if len(set(products)) == 1:
            same_product_folios += 1

if total_multi_jar_folios > 0:
    coherence = same_product_folios / total_multi_jar_folios
    print(f"\nFolio coherence: {same_product_folios}/{total_multi_jar_folios} ({100*coherence:.0f}%)")
    print("(Folios where all jars map to same product type)")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'jar_product_type',
    'question': 'Do jar MIDDLEs cluster by Brunschwig product type?',
    'summary': {
        'total_jars': len(jar_labels),
        'jars_with_b_connection': len(jar_analysis),
        'product_distribution': dict(product_counts),
        'chi2': float(chi2),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05)
    },
    'folio_coherence': {
        'multi_jar_folios': total_multi_jar_folios,
        'same_product_folios': same_product_folios,
        'coherence_rate': float(coherence) if total_multi_jar_folios > 0 else None
    },
    'jar_details': jar_analysis
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results' / 'jar_product_type.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: JAR -> PRODUCT TYPE CLUSTERING")
print("="*70)

print(f"""
Do jar label MIDDLEs cluster by Brunschwig product type?

Distribution:
  WATER_STANDARD: {product_counts.get('WATER_STANDARD', 0)}
  WATER_GENTLE: {product_counts.get('WATER_GENTLE', 0)}
  OIL_RESIN: {product_counts.get('OIL_RESIN', 0)}
  PRECISION: {product_counts.get('PRECISION', 0)}

Chi-square test (vs uniform):
  Chi2 = {chi2:.2f}, p = {p_value:.4f}

Verdict: {'CLUSTERING DETECTED' if p_value < 0.05 else 'NO SIGNIFICANT CLUSTERING'}

{'Jar labels do NOT distribute uniformly across product types.' if p_value < 0.05 else 'Jar labels distribute uniformly - no product type clustering.'}
""")
