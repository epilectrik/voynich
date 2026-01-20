#!/usr/bin/env python3
"""
ANGLE D (FOLIO-LEVEL): Registry-internal correlation with reference materials

The product-type level test (n=4) was underpowered. This version tests at the
folio level: do individual folios with higher registry-internal ratios cluster
in product types with more reference materials?

Method: Mann-Whitney U test comparing registry-internal ratios between:
- Folios in HIGH-REFERENCE product types (OIL_RESIN, WATER_GENTLE: >60% reference)
- Folios in LOW-REFERENCE product types (PRECISION, WATER_STANDARD: <60% reference)
"""

import csv
import json
from collections import defaultdict
import math

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def load_2track_classification():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles']), set(data['a_shared_middles'])

def load_folio_classifications():
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
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

def mann_whitney_u(x, y):
    """Compute Mann-Whitney U statistic and approximate p-value."""
    nx, ny = len(x), len(y)

    # Rank all values
    combined = [(v, 'x', i) for i, v in enumerate(x)] + [(v, 'y', i) for i, v in enumerate(y)]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties with average rank)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2  # Average rank for ties
        for k in range(i, j):
            ranks[(combined[k][1], combined[k][2])] = avg_rank
        i = j

    # Sum ranks for x
    r1 = sum(ranks[('x', i)] for i in range(nx))

    # U statistic
    u1 = r1 - nx * (nx + 1) / 2
    u2 = nx * ny - u1
    u = min(u1, u2)

    # Z approximation for large samples
    mean_u = nx * ny / 2
    std_u = math.sqrt(nx * ny * (nx + ny + 1) / 12)

    if std_u > 0:
        z = (u - mean_u) / std_u
        # Two-tailed p-value approximation
        # |z| > 1.96 means p < 0.05
        # |z| > 2.58 means p < 0.01
        if abs(z) > 2.58:
            p_approx = 0.01
        elif abs(z) > 1.96:
            p_approx = 0.05
        elif abs(z) > 1.64:
            p_approx = 0.10
        else:
            p_approx = 0.20
    else:
        z = 0
        p_approx = 1.0

    return u, z, p_approx, r1

def effect_size_r(z, n):
    """Compute effect size r from z-score."""
    return abs(z) / math.sqrt(n)

def main():
    print("=" * 70)
    print("ANGLE D (FOLIO-LEVEL): Registry-Internal vs Reference Materials")
    print("=" * 70)
    print()

    # Based on previous analysis:
    # HIGH-REFERENCE types (>60%): OIL_RESIN (80%), WATER_GENTLE (70.8%)
    # LOW-REFERENCE types (<60%): WATER_STANDARD (59.5%), PRECISION (22.2%)

    HIGH_REF_TYPES = {'OIL_RESIN', 'WATER_GENTLE'}
    LOW_REF_TYPES = {'WATER_STANDARD', 'PRECISION'}

    print(f"HIGH-REFERENCE types: {HIGH_REF_TYPES}")
    print(f"LOW-REFERENCE types: {LOW_REF_TYPES}")
    print()

    # Load data
    a_exclusive, a_shared = load_2track_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    # Compute registry-internal ratio per folio
    high_ref_ratios = []
    low_ref_ratios = []

    high_ref_folios = []
    low_ref_folios = []

    for folio, middles in folio_middles.items():
        if folio not in folio_classifications:
            continue

        ptype = folio_classifications[folio]

        reg_count = sum(1 for m in middles if m in a_exclusive)
        pipe_count = sum(1 for m in middles if m in a_shared)
        total = reg_count + pipe_count

        if total < 5:  # Skip folios with too few classified MIDDLEs
            continue

        ratio = reg_count / total

        if ptype in HIGH_REF_TYPES:
            high_ref_ratios.append(ratio)
            high_ref_folios.append((folio, ptype, ratio, reg_count, pipe_count))
        elif ptype in LOW_REF_TYPES:
            low_ref_ratios.append(ratio)
            low_ref_folios.append((folio, ptype, ratio, reg_count, pipe_count))

    print(f"HIGH-REFERENCE folios: {len(high_ref_ratios)}")
    print(f"LOW-REFERENCE folios: {len(low_ref_ratios)}")
    print()

    # Summary statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print()

    high_mean = sum(high_ref_ratios) / len(high_ref_ratios) if high_ref_ratios else 0
    low_mean = sum(low_ref_ratios) / len(low_ref_ratios) if low_ref_ratios else 0

    high_median = sorted(high_ref_ratios)[len(high_ref_ratios)//2] if high_ref_ratios else 0
    low_median = sorted(low_ref_ratios)[len(low_ref_ratios)//2] if low_ref_ratios else 0

    print(f"HIGH-REFERENCE folios (n={len(high_ref_ratios)}):")
    print(f"  Mean registry-internal ratio: {high_mean:.1%}")
    print(f"  Median: {high_median:.1%}")
    print(f"  Range: {min(high_ref_ratios):.1%} - {max(high_ref_ratios):.1%}")
    print()

    print(f"LOW-REFERENCE folios (n={len(low_ref_ratios)}):")
    print(f"  Mean registry-internal ratio: {low_mean:.1%}")
    print(f"  Median: {low_median:.1%}")
    print(f"  Range: {min(low_ref_ratios):.1%} - {max(low_ref_ratios):.1%}")
    print()

    print(f"Difference: {high_mean - low_mean:+.1%} (HIGH - LOW)")
    print()

    # Mann-Whitney U test
    print("=" * 70)
    print("MANN-WHITNEY U TEST")
    print("=" * 70)
    print()

    u, z, p, r1 = mann_whitney_u(high_ref_ratios, low_ref_ratios)
    n_total = len(high_ref_ratios) + len(low_ref_ratios)
    effect_r = effect_size_r(z, n_total)

    print(f"U statistic: {u:.1f}")
    print(f"Z score: {z:.3f}")
    print(f"Approximate p-value: {p}")
    print(f"Effect size (r): {effect_r:.3f}")
    print()

    if p <= 0.05:
        if high_mean > low_mean:
            print("RESULT: SIGNIFICANT - HIGH-REFERENCE folios have HIGHER registry-internal ratio")
            verdict = "SUPPORTS"
        else:
            print("RESULT: SIGNIFICANT - HIGH-REFERENCE folios have LOWER registry-internal ratio")
            verdict = "CONTRADICTS"
    elif p <= 0.10:
        if high_mean > low_mean:
            print("RESULT: MARGINALLY SIGNIFICANT (p < 0.10) - suggests positive relationship")
            verdict = "SUGGESTIVE"
        else:
            print("RESULT: MARGINALLY SIGNIFICANT (p < 0.10) - suggests negative relationship")
            verdict = "SUGGESTIVE_NEGATIVE"
    else:
        print("RESULT: NOT SIGNIFICANT - No relationship detected")
        verdict = "NULL"
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if verdict == "SUPPORTS":
        print("The hypothesis is SUPPORTED:")
        print("  Folios in product types with more reference-only Brunschwig materials")
        print("  have significantly higher registry-internal vocabulary density.")
        print()
        print("  This suggests registry-internal vocabulary may encode 'fine distinctions'")
        print("  that parallel Brunschwig's reference materials - information recorded")
        print("  but not executed.")
    elif verdict == "SUGGESTIVE":
        print("The hypothesis is SUGGESTIVELY SUPPORTED (p < 0.10):")
        print("  There is a trend toward higher registry-internal ratios in")
        print("  high-reference product types, but not at conventional significance.")
        print()
        print("  This is consistent with C498's interpretation but not definitive proof.")
    elif verdict == "CONTRADICTS":
        print("The hypothesis is CONTRADICTED:")
        print("  Folios in high-reference product types have LOWER registry-internal ratios.")
        print("  This is opposite to the C498 prediction.")
    else:
        print("The hypothesis is NEITHER SUPPORTED NOR CONTRADICTED:")
        print("  No significant relationship between reference ratio and registry-internal ratio.")
        print("  The two measures appear to be independent.")
    print()

    # Save results
    output = {
        'test': 'REFERENCE_MATERIAL_FOLIO_LEVEL',
        'date': '2026-01-20',
        'groups': {
            'high_reference': {
                'types': list(HIGH_REF_TYPES),
                'n_folios': len(high_ref_ratios),
                'mean_ratio': high_mean,
                'median_ratio': high_median
            },
            'low_reference': {
                'types': list(LOW_REF_TYPES),
                'n_folios': len(low_ref_ratios),
                'mean_ratio': low_mean,
                'median_ratio': low_median
            }
        },
        'mann_whitney': {
            'u': u,
            'z': z,
            'p_approx': p,
            'effect_size_r': effect_r
        },
        'difference': high_mean - low_mean,
        'verdict': verdict
    }

    with open('phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/reference_material_folio_level.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/reference_material_folio_level.json")

if __name__ == '__main__':
    main()
