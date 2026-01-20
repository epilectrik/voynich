#!/usr/bin/env python3
"""
ANGLE D: REGISTRY-INTERNAL AS REFERENCE ENTRIES

Hypothesis: If registry-internal vocabulary encodes "fine distinctions below
execution threshold" (C498), then product types with more "reference-only"
materials in Brunschwig (listed but no procedure) should correlate with
higher registry-internal vocabulary density in corresponding A folios.

Method:
1. Load Brunschwig materials, classify as "processed" (has steps) vs "reference" (no steps)
2. Compute reference ratio per product type
3. Load A folio MIDDLE data with 2-track classification
4. Compute registry-internal ratio per folio, aggregate by product type
5. Test correlation: reference ratio vs registry-internal ratio
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    """Extract MIDDLE from token by removing known prefix."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# ============================================================
# DATA LOADING
# ============================================================

def load_brunschwig_materials():
    """Load Brunschwig materials and classify as processed vs reference."""
    with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    materials = data['materials']

    # Classify each material
    processed = []  # Has procedural steps
    reference = []  # No procedural steps (reference only)

    for mat in materials:
        product_type = mat.get('predicted_product_type', 'UNKNOWN')
        steps = mat.get('procedural_steps', [])

        if len(steps) > 0:
            processed.append({
                'name': mat.get('name_normalized', ''),
                'product_type': product_type,
                'n_steps': len(steps)
            })
        else:
            reference.append({
                'name': mat.get('name_normalized', ''),
                'product_type': product_type
            })

    return processed, reference

def load_2track_classification():
    """Load the 2-track MIDDLE classification from C498."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)

    a_exclusive = set(data['a_exclusive_middles'])  # Registry-internal
    a_shared = set(data['a_shared_middles'])        # Pipeline-participating

    return a_exclusive, a_shared

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load MIDDLEs per folio from transcript (H-track, language=A only)."""
    folio_middles = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)

    return folio_middles

# ============================================================
# ANALYSIS
# ============================================================

def compute_reference_ratios(processed, reference):
    """Compute reference ratio per product type."""
    # Count by product type
    processed_counts = Counter(m['product_type'] for m in processed)
    reference_counts = Counter(m['product_type'] for m in reference)

    all_types = set(processed_counts.keys()) | set(reference_counts.keys())

    ratios = {}
    for ptype in all_types:
        proc = processed_counts.get(ptype, 0)
        ref = reference_counts.get(ptype, 0)
        total = proc + ref
        ratios[ptype] = {
            'processed': proc,
            'reference': ref,
            'total': total,
            'reference_ratio': ref / total if total > 0 else 0
        }

    return ratios

def compute_folio_track_ratios(folio_middles, a_exclusive, a_shared, folio_classifications):
    """Compute registry-internal ratio per folio."""
    folio_ratios = {}

    for folio, middles in folio_middles.items():
        if folio not in folio_classifications:
            continue

        reg_count = sum(1 for m in middles if m in a_exclusive)
        pipe_count = sum(1 for m in middles if m in a_shared)
        total = reg_count + pipe_count

        if total > 0:
            folio_ratios[folio] = {
                'product_type': folio_classifications[folio],
                'registry_internal': reg_count,
                'pipeline_participating': pipe_count,
                'total': total,
                'registry_ratio': reg_count / total
            }

    return folio_ratios

def aggregate_by_product_type(folio_ratios):
    """Aggregate registry-internal ratios by product type."""
    type_aggregates = defaultdict(list)

    for folio, data in folio_ratios.items():
        type_aggregates[data['product_type']].append(data['registry_ratio'])

    result = {}
    for ptype, ratios in type_aggregates.items():
        result[ptype] = {
            'n_folios': len(ratios),
            'mean_registry_ratio': sum(ratios) / len(ratios) if ratios else 0,
            'min': min(ratios) if ratios else 0,
            'max': max(ratios) if ratios else 0
        }

    return result

def pearson_correlation(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return None, None

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if denom_x == 0 or denom_y == 0:
        return 0, 1.0

    r = numerator / (denom_x * denom_y)

    # t-test for significance
    if abs(r) < 1:
        t = r * math.sqrt(n - 2) / math.sqrt(1 - r**2)
        # Approximate p-value (for small n, this is rough)
        # For n=4, df=2: t > 4.30 means p < 0.05
        # For n=4, df=2: t > 2.92 means p < 0.10
        df = n - 2
        if df == 2:
            p_approx = 0.05 if abs(t) > 4.30 else (0.10 if abs(t) > 2.92 else 0.50)
        else:
            p_approx = 0.05 if abs(t) > 2.5 else 0.20
    else:
        p_approx = 0.0

    return r, p_approx

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANGLE D: REGISTRY-INTERNAL AS REFERENCE ENTRIES")
    print("=" * 70)
    print()
    print("Hypothesis: Product types with more 'reference-only' Brunschwig")
    print("materials should have higher registry-internal vocabulary density")
    print("in corresponding A folios (per C498 interpretation).")
    print()

    # Load data
    print("Loading data...")
    processed, reference = load_brunschwig_materials()
    a_exclusive, a_shared = load_2track_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Brunschwig materials with procedures: {len(processed)}")
    print(f"  Brunschwig materials without procedures (reference): {len(reference)}")
    print(f"  Registry-internal MIDDLEs: {len(a_exclusive)}")
    print(f"  Pipeline-participating MIDDLEs: {len(a_shared)}")
    print(f"  Classified A folios: {len(folio_classifications)}")
    print()

    # Compute reference ratios per product type
    print("=" * 70)
    print("BRUNSCHWIG REFERENCE RATIOS BY PRODUCT TYPE")
    print("=" * 70)
    print()

    ref_ratios = compute_reference_ratios(processed, reference)

    print(f"{'Product Type':<20} {'Processed':>10} {'Reference':>10} {'Ref Ratio':>10}")
    print("-" * 50)
    for ptype in sorted(ref_ratios.keys()):
        data = ref_ratios[ptype]
        print(f"{ptype:<20} {data['processed']:>10} {data['reference']:>10} {data['reference_ratio']:>10.1%}")
    print()

    # Compute folio track ratios
    print("=" * 70)
    print("REGISTRY-INTERNAL RATIOS BY PRODUCT TYPE")
    print("=" * 70)
    print()

    folio_ratios = compute_folio_track_ratios(folio_middles, a_exclusive, a_shared, folio_classifications)
    type_aggregates = aggregate_by_product_type(folio_ratios)

    print(f"{'Product Type':<20} {'N Folios':>10} {'Mean Reg Ratio':>15} {'Range':>15}")
    print("-" * 60)
    for ptype in sorted(type_aggregates.keys()):
        data = type_aggregates[ptype]
        range_str = f"{data['min']:.1%}-{data['max']:.1%}"
        print(f"{ptype:<20} {data['n_folios']:>10} {data['mean_registry_ratio']:>15.1%} {range_str:>15}")
    print()

    # Correlation test
    print("=" * 70)
    print("CORRELATION TEST")
    print("=" * 70)
    print()

    # Build paired data
    common_types = set(ref_ratios.keys()) & set(type_aggregates.keys())
    common_types.discard('UNKNOWN')

    x_ref = []  # Reference ratios
    y_reg = []  # Registry-internal ratios
    labels = []

    for ptype in sorted(common_types):
        x_ref.append(ref_ratios[ptype]['reference_ratio'])
        y_reg.append(type_aggregates[ptype]['mean_registry_ratio'])
        labels.append(ptype)

    print("Data points:")
    print(f"{'Product Type':<20} {'Ref Ratio':>12} {'Reg-Int Ratio':>15}")
    print("-" * 47)
    for i, ptype in enumerate(labels):
        print(f"{ptype:<20} {x_ref[i]:>12.1%} {y_reg[i]:>15.1%}")
    print()

    r, p = pearson_correlation(x_ref, y_reg)

    if r is not None:
        print(f"Pearson correlation: r = {r:.3f}")
        print(f"Approximate p-value: {p}")
        print()

        if r > 0.5 and p <= 0.10:
            print("RESULT: POSITIVE CORRELATION (supports hypothesis)")
            print("  Product types with more reference materials show higher")
            print("  registry-internal vocabulary density.")
            interpretation = "SUPPORTS C498 interpretation"
        elif r < -0.5 and p <= 0.10:
            print("RESULT: NEGATIVE CORRELATION (contradicts hypothesis)")
            print("  Product types with more reference materials show LOWER")
            print("  registry-internal vocabulary density.")
            interpretation = "CONTRADICTS C498 interpretation"
        else:
            print("RESULT: NO SIGNIFICANT CORRELATION")
            print("  Reference ratio and registry-internal ratio are independent.")
            interpretation = "ORTHOGONAL - no relationship"
    else:
        print("RESULT: Insufficient data for correlation test")
        interpretation = "INSUFFICIENT DATA"
    print()

    # Additional analysis: per-folio breakdown
    print("=" * 70)
    print("DETAILED FOLIO BREAKDOWN")
    print("=" * 70)
    print()

    for ptype in sorted(common_types):
        folios_in_type = [f for f, d in folio_ratios.items() if d['product_type'] == ptype]
        print(f"{ptype}: {len(folios_in_type)} folios")
        for folio in sorted(folios_in_type)[:5]:  # Show first 5
            d = folio_ratios[folio]
            print(f"  {folio}: reg={d['registry_internal']}, pipe={d['pipeline_participating']}, ratio={d['registry_ratio']:.1%}")
        if len(folios_in_type) > 5:
            print(f"  ... and {len(folios_in_type) - 5} more")
        print()

    # Save results
    output = {
        'test': 'REFERENCE_MATERIAL_CORRELATION',
        'date': '2026-01-20',
        'hypothesis': 'Reference ratio correlates with registry-internal ratio',
        'brunschwig': {
            'processed': len(processed),
            'reference': len(reference),
            'by_product_type': ref_ratios
        },
        'voynich': {
            'by_product_type': type_aggregates
        },
        'correlation': {
            'r': r,
            'p_approx': p,
            'n': len(labels),
            'data_points': [
                {'type': labels[i], 'ref_ratio': x_ref[i], 'reg_ratio': y_reg[i]}
                for i in range(len(labels))
            ]
        },
        'interpretation': interpretation
    }

    with open('phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/reference_material_correlation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/reference_material_correlation.json")

if __name__ == '__main__':
    main()
