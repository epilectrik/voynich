#!/usr/bin/env python3
"""
PRODUCT TYPE → A REGISTRY BACKWARD PROPAGATION

Question: If Brunschwig product types (aromatic water, oil, resin) map to specific
          REGIMEs, do different product types "light up" different Currier A patterns?

Chain:
  Brunschwig Product Type
        ↓
    REGIME assignment
        ↓
    B folios in that REGIME
        ↓
    A entries that correlate with those B folios
        ↓
    Do different product types show different A patterns?

Prediction:
  - Aromatic waters (R2/R1) → intervention-permissive A patterns
  - Oils/resins (R3) → commitment-heavy A patterns
  - Precision products (R4) → high-monitoring A patterns
"""

import csv
from collections import defaultdict, Counter
import json

# ============================================================
# BRUNSCHWIG PRODUCT TYPE → REGIME MAPPING
# ============================================================

PRODUCT_REGIME_MAP = {
    'AROMATIC_WATER': ['REGIME_2', 'REGIME_1'],  # First/second degree, gentle
    'ESSENTIAL_OIL': ['REGIME_3'],                # Third degree, intense extraction
    'RESIN_EXTRACT': ['REGIME_3'],                # Fourth degree (dry distillation)
    'PRECISION_DISTILLATE': ['REGIME_4'],         # Any degree requiring exact timing
}

# Reverse mapping for labeling
def get_product_type(regime):
    if regime in ['REGIME_2', 'REGIME_1']:
        return 'AROMATIC_WATER'
    elif regime == 'REGIME_3':
        return 'OIL_OR_RESIN'
    elif regime == 'REGIME_4':
        return 'PRECISION'
    return 'UNKNOWN'

# ============================================================
# KNOWN MORPHOLOGICAL COMPONENTS
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

def decompose_token(token):
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return (prefix, token, suffix)

# ============================================================
# LOAD DATA
# ============================================================

def load_folio_regimes():
    """Load folio -> REGIME mapping from proposed_folio_order.txt"""
    folio_regime = {}
    try:
        with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
            for line in f:
                parts = line.split('|')
                if len(parts) >= 3:
                    folio = parts[1].strip()
                    regime = parts[2].strip()
                    if folio.startswith('f') and regime.startswith('REGIME'):
                        folio_regime[folio] = regime
    except FileNotFoundError:
        print("Warning: proposed_folio_order.txt not found")
    return folio_regime

def load_tokens():
    """Load all tokens with morphological decomposition."""
    a_tokens = []
    b_tokens = []
    azc_tokens = []

    azc_sections = {'Z', 'A', 'C'}

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            prefix, middle, suffix = decompose_token(word)

            entry = {
                'token': word, 'folio': folio,
                'prefix': prefix, 'middle': middle, 'suffix': suffix,
                'placement': placement
            }

            is_azc = section in azc_sections or language not in ('A', 'B')

            if language == 'A':
                a_tokens.append(entry)
            elif language == 'B':
                b_tokens.append(entry)

            if is_azc:
                azc_tokens.append(entry)

    return a_tokens, b_tokens, azc_tokens

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("PRODUCT TYPE -> A REGISTRY BACKWARD PROPAGATION")
    print("=" * 70)
    print()

    # Load data
    folio_regime = load_folio_regimes()
    a_tokens, b_tokens, azc_tokens = load_tokens()

    print(f"Loaded {len(folio_regime)} folio-REGIME mappings")
    print(f"Loaded {len(a_tokens)} A tokens, {len(b_tokens)} B tokens, {len(azc_tokens)} AZC tokens")
    print()

    # Group B folios by product type
    regime_folios = defaultdict(set)
    for folio, regime in folio_regime.items():
        regime_folios[regime].add(folio)

    product_folios = defaultdict(set)
    for regime, folios in regime_folios.items():
        product_type = get_product_type(regime)
        product_folios[product_type].update(folios)

    print("B FOLIOS BY PRODUCT TYPE:")
    print("-" * 50)
    for product, folios in sorted(product_folios.items()):
        print(f"  {product}: {len(folios)} folios")
    print()

    # For each product type, collect A vocabulary that appears in those B folios
    # Since A and B are disjoint, we use AZC as the bridge
    # AZC folios contain vocabulary that constrains B execution

    # Build: which MIDDLEs appear in which B folios
    b_folio_middles = defaultdict(set)
    for t in b_tokens:
        if t['middle']:
            b_folio_middles[t['folio']].add(t['middle'])

    # Build: which MIDDLEs appear in which A folios
    a_folio_middles = defaultdict(set)
    for t in a_tokens:
        if t['middle']:
            a_folio_middles[t['folio']].add(t['middle'])

    # Build: which MIDDLEs appear in AZC with which placements
    middle_placements = defaultdict(Counter)
    for t in azc_tokens:
        if t['middle'] and t['placement']:
            # Normalize placement
            p = t['placement']
            if p.startswith('R'):
                p = 'R'
            elif p.startswith('S'):
                p = 'S'
            middle_placements[t['middle']][p] += 1

    # For each product type, find the characteristic MIDDLEs in B
    print("=" * 70)
    print("MIDDLE ANALYSIS BY PRODUCT TYPE")
    print("=" * 70)
    print()

    product_middles = {}
    for product_type, folios in product_folios.items():
        middles = set()
        for folio in folios:
            middles.update(b_folio_middles.get(folio, set()))
        product_middles[product_type] = middles
        print(f"{product_type}: {len(middles)} unique MIDDLEs in B")

    # Find exclusive MIDDLEs per product type
    print()
    print("EXCLUSIVE MIDDLES (appear in only one product type):")
    print("-" * 50)

    all_product_middles = {}
    for product_type, middles in product_middles.items():
        exclusive = middles.copy()
        for other_type, other_middles in product_middles.items():
            if other_type != product_type:
                exclusive -= other_middles
        all_product_middles[product_type] = exclusive
        print(f"  {product_type}: {len(exclusive)} exclusive MIDDLEs")
        if len(exclusive) <= 10:
            print(f"    Examples: {list(exclusive)[:10]}")

    # Analyze AZC placement preferences by product type
    print()
    print("=" * 70)
    print("AZC PLACEMENT PREFERENCES BY PRODUCT TYPE")
    print("=" * 70)
    print()

    placement_zones = ['C', 'P', 'R', 'S']

    for product_type in sorted(product_folios.keys()):
        middles = product_middles[product_type]

        # Aggregate placement distribution for these MIDDLEs
        zone_counts = Counter()
        total = 0
        for middle in middles:
            for zone, count in middle_placements[middle].items():
                if zone in placement_zones:
                    zone_counts[zone] += count
                    total += count

        print(f"{product_type}:")
        if total > 0:
            for zone in placement_zones:
                pct = 100 * zone_counts[zone] / total
                bar = '#' * int(pct / 2)
                print(f"  {zone}: {pct:5.1f}% {bar}")
        else:
            print("  (no placement data)")
        print()

    # PREFIX distribution by product type
    print("=" * 70)
    print("PREFIX DISTRIBUTION BY PRODUCT TYPE")
    print("=" * 70)
    print()

    for product_type, folios in sorted(product_folios.items()):
        prefix_counts = Counter()
        for folio in folios:
            for t in b_tokens:
                if t['folio'] == folio and t['prefix']:
                    prefix_counts[t['prefix']] += 1

        total = sum(prefix_counts.values())
        print(f"{product_type} (n={total}):")
        for prefix, count in prefix_counts.most_common(8):
            pct = 100 * count / total if total > 0 else 0
            print(f"  {prefix:4s}: {pct:5.1f}%")
        print()

    # Statistical comparison
    print("=" * 70)
    print("PRODUCT TYPE DISCRIMINATION TEST")
    print("=" * 70)
    print()

    # Test: Do different product types show significantly different PREFIX distributions?
    product_prefix_profiles = {}
    for product_type, folios in product_folios.items():
        prefix_counts = Counter()
        for folio in folios:
            for t in b_tokens:
                if t['folio'] == folio and t['prefix']:
                    prefix_counts[t['prefix']] += 1
        total = sum(prefix_counts.values())
        if total > 0:
            product_prefix_profiles[product_type] = {p: c/total for p, c in prefix_counts.items()}

    # Compare profiles pairwise
    print("PREFIX profile differences (Jensen-Shannon-like):")
    products = sorted(product_prefix_profiles.keys())
    for i, p1 in enumerate(products):
        for p2 in products[i+1:]:
            prof1 = product_prefix_profiles[p1]
            prof2 = product_prefix_profiles[p2]
            all_prefixes = set(prof1.keys()) | set(prof2.keys())

            # Simple difference metric
            diff = sum(abs(prof1.get(p, 0) - prof2.get(p, 0)) for p in all_prefixes) / 2
            print(f"  {p1} vs {p2}: {diff:.3f}")

    # Check for diagnostic prefixes
    print()
    print("DIAGNOSTIC PREFIXES (>2x enrichment in one product type):")
    print("-" * 50)

    all_prefixes = set()
    for prof in product_prefix_profiles.values():
        all_prefixes.update(prof.keys())

    for prefix in sorted(all_prefixes):
        values = {pt: prof.get(prefix, 0) for pt, prof in product_prefix_profiles.items()}
        max_val = max(values.values())
        min_val = min(v for v in values.values() if v > 0) if any(v > 0 for v in values.values()) else 0.001

        if max_val > 0 and min_val > 0 and max_val / min_val > 2:
            enriched_in = max(values.items(), key=lambda x: x[1])[0]
            print(f"  {prefix}: enriched in {enriched_in} ({max_val:.1%} vs {min_val:.1%})")

    # Summary
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    # Count exclusive MIDDLEs
    total_exclusive = sum(len(m) for m in all_product_middles.values())
    total_middles = len(set().union(*product_middles.values()))

    print(f"Total unique MIDDLEs across products: {total_middles}")
    print(f"Product-exclusive MIDDLEs: {total_exclusive} ({100*total_exclusive/total_middles:.1f}%)")
    print()

    if total_exclusive / total_middles > 0.1:
        print("FINDING: Product types show MIDDLE discrimination")
        print("         Different Brunschwig products light up different A patterns")
    else:
        print("FINDING: Product types share most MIDDLEs")
        print("         A vocabulary is largely product-agnostic")

    # Save results
    results = {
        'product_folio_counts': {k: len(v) for k, v in product_folios.items()},
        'product_middle_counts': {k: len(v) for k, v in product_middles.items()},
        'product_exclusive_counts': {k: len(v) for k, v in all_product_middles.items()},
        'product_prefix_profiles': product_prefix_profiles,
    }

    with open('results/product_a_correlation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to results/product_a_correlation.json")

if __name__ == '__main__':
    main()
