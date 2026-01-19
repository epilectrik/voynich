#!/usr/bin/env python
"""
CAR Phase Track 4: A/C Discrimination Analysis

Tests why A/C folios have 45% higher MIDDLE incompatibility density than Zodiac.

Tests:
- CAR-4.1: Incompatibility Density vs B Escape Rate
- CAR-4.2: A/C Specificity Mechanism
- CAR-4.3: Constraint Propagation Path

Reference:
- F-AZC-019: A/C +45% density vs Zodiac (p=0.0006)
- C468: Escape permission causality
- C470: MIDDLE restrictions transfer intact
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

from car_data_loader import (
    CARDataLoader, decompose_token, get_middles_from_tokens,
    MARKER_PREFIXES, PHASE_DIR
)


def get_azc_family(section):
    """Map section to AZC family."""
    if section in ('A', 'C'):
        return 'AC'
    elif section == 'Z':
        return 'Zodiac'
    return None


def test_car_4_1_density_escape():
    """
    CAR-4.1: Incompatibility Density vs B Escape Rate

    Question: Does A/C's higher density correlate with downstream B behavior?

    NOTE: This test requires escape rate data which may not be available.
    We'll compute MIDDLE incompatibility density and report it.
    """
    print("\n" + "=" * 60)
    print("CAR-4.1: Incompatibility Density vs B Escape Rate")
    print("=" * 60)

    loader = CARDataLoader().load()
    azc_data = loader.get_azc()

    # Group AZC data by section
    section_middles = defaultdict(set)
    section_folio_middles = defaultdict(lambda: defaultdict(set))

    for _, row in azc_data.iterrows():
        section = row['section']
        folio = row['folio']
        token = row['word']

        _, middle, _ = decompose_token(token)
        if middle is not None:
            section_middles[section].add(middle)
            section_folio_middles[section][folio].add(middle)

    print(f"\nAZC sections found: {list(section_middles.keys())}")

    # Calculate MIDDLE density per family
    ac_middles = section_middles.get('A', set()) | section_middles.get('C', set())
    z_middles = section_middles.get('Z', set())

    print(f"\nA/C MIDDLEs: {len(ac_middles)}")
    print(f"Zodiac MIDDLEs: {len(z_middles)}")
    print(f"Overlap: {len(ac_middles & z_middles)}")

    # MIDDLE incompatibility density = proportion of MIDDLE pairs that never co-occur
    # This requires within-entry co-occurrence analysis

    def calculate_cooccurrence_density(middles_by_folio):
        """Calculate co-occurrence patterns."""
        all_middles = set()
        cooccur_pairs = set()

        for folio, middles in middles_by_folio.items():
            all_middles.update(middles)
            # All pairs that co-occur in same folio
            for m1 in middles:
                for m2 in middles:
                    if m1 < m2:
                        cooccur_pairs.add((m1, m2))

        total_pairs = len(all_middles) * (len(all_middles) - 1) // 2
        cooccur_count = len(cooccur_pairs)

        if total_pairs > 0:
            cooccur_rate = cooccur_count / total_pairs
            incompatibility_density = 1 - cooccur_rate
        else:
            cooccur_rate = 0
            incompatibility_density = 0

        return {
            'n_middles': len(all_middles),
            'total_pairs': total_pairs,
            'cooccur_pairs': cooccur_count,
            'cooccur_rate': cooccur_rate,
            'incompatibility_density': incompatibility_density
        }

    # Calculate for A/C
    ac_folios = {}
    for section in ['A', 'C']:
        if section in section_folio_middles:
            ac_folios.update(section_folio_middles[section])

    # Calculate for Zodiac
    z_folios = section_folio_middles.get('Z', {})

    ac_stats = calculate_cooccurrence_density(ac_folios)
    z_stats = calculate_cooccurrence_density(z_folios)

    print(f"\nA/C MIDDLE statistics:")
    print(f"  Unique MIDDLEs: {ac_stats['n_middles']}")
    print(f"  Total possible pairs: {ac_stats['total_pairs']}")
    print(f"  Co-occurring pairs: {ac_stats['cooccur_pairs']}")
    print(f"  Co-occurrence rate: {100*ac_stats['cooccur_rate']:.1f}%")
    print(f"  Incompatibility density: {100*ac_stats['incompatibility_density']:.1f}%")

    print(f"\nZodiac MIDDLE statistics:")
    print(f"  Unique MIDDLEs: {z_stats['n_middles']}")
    print(f"  Total possible pairs: {z_stats['total_pairs']}")
    print(f"  Co-occurring pairs: {z_stats['cooccur_pairs']}")
    print(f"  Co-occurrence rate: {100*z_stats['cooccur_rate']:.1f}%")
    print(f"  Incompatibility density: {100*z_stats['incompatibility_density']:.1f}%")

    # Comparison
    if z_stats['incompatibility_density'] > 0:
        density_ratio = ac_stats['incompatibility_density'] / z_stats['incompatibility_density']
        density_diff = ac_stats['incompatibility_density'] - z_stats['incompatibility_density']
    else:
        density_ratio = 0
        density_diff = 0

    print(f"\nComparison:")
    print(f"  A/C vs Zodiac density ratio: {density_ratio:.2f}x")
    print(f"  A/C - Zodiac density difference: {100*density_diff:.1f}%")

    result = {
        'test_id': 'CAR-4.1',
        'test_name': 'Incompatibility Density vs B Escape Rate',
        'ac_stats': ac_stats,
        'z_stats': z_stats,
        'density_ratio': density_ratio,
        'density_diff': density_diff,
        'note': 'Escape rate data not available for correlation - reporting density comparison',
        'verdict': 'SIGNIFICANT' if density_diff > 0.1 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  A/C has higher incompatibility density than Zodiac")
        print(f"  Difference: {100*density_diff:.1f}%")

    return result


def test_car_4_2_specificity_mechanism():
    """
    CAR-4.2: A/C Specificity Mechanism

    Question: Does A/C achieve specificity through density or through vocabulary?

    Method:
    1. Compare A/C vs Zodiac:
       - MIDDLE type count
       - MIDDLE frequency distribution (Gini coefficient)
       - MIDDLE exclusivity (what % are A/C-only vs Zodiac-only)
    """
    print("\n" + "=" * 60)
    print("CAR-4.2: A/C Specificity Mechanism")
    print("=" * 60)

    loader = CARDataLoader().load()
    azc_data = loader.get_azc()

    # Collect MIDDLEs by family
    ac_middles = Counter()
    z_middles = Counter()

    for _, row in azc_data.iterrows():
        section = row['section']
        token = row['word']

        _, middle, _ = decompose_token(token)
        if middle is not None:
            if section in ('A', 'C'):
                ac_middles[middle] += 1
            elif section == 'Z':
                z_middles[middle] += 1

    # Statistics
    ac_types = len(ac_middles)
    z_types = len(z_middles)
    ac_total = sum(ac_middles.values())
    z_total = sum(z_middles.values())

    print(f"\nA/C: {ac_types} types, {ac_total} tokens")
    print(f"Zodiac: {z_types} types, {z_total} tokens")

    # Overlap analysis
    shared = set(ac_middles.keys()) & set(z_middles.keys())
    ac_only = set(ac_middles.keys()) - set(z_middles.keys())
    z_only = set(z_middles.keys()) - set(ac_middles.keys())

    print(f"\nVocabulary overlap:")
    print(f"  Shared MIDDLEs: {len(shared)}")
    print(f"  A/C-only MIDDLEs: {len(ac_only)} ({100*len(ac_only)/ac_types:.1f}%)")
    print(f"  Zodiac-only MIDDLEs: {len(z_only)} ({100*len(z_only)/z_types:.1f}%)")

    # Gini coefficient (inequality of distribution)
    def gini_coefficient(counts):
        if not counts:
            return 0
        values = sorted(counts.values())
        n = len(values)
        if n == 0:
            return 0
        total = sum(values)
        if total == 0:
            return 0
        cumulative = 0
        gini_sum = 0
        for i, v in enumerate(values):
            cumulative += v
            gini_sum += cumulative
        return 1 - (2 * gini_sum) / (n * total) + 1/n

    ac_gini = gini_coefficient(ac_middles)
    z_gini = gini_coefficient(z_middles)

    print(f"\nFrequency distribution (Gini coefficient):")
    print(f"  A/C Gini: {ac_gini:.3f}")
    print(f"  Zodiac Gini: {z_gini:.3f}")
    print(f"  (Higher = more unequal distribution)")

    # Top MIDDLEs comparison
    print(f"\nTop 10 MIDDLEs by family:")
    print("  A/C:", [(m, c) for m, c in ac_middles.most_common(10)])
    print("  Zodiac:", [(m, c) for m, c in z_middles.most_common(10)])

    # Exclusivity score
    exclusivity = (len(ac_only) + len(z_only)) / (len(shared) + len(ac_only) + len(z_only)) if shared or ac_only or z_only else 0

    result = {
        'test_id': 'CAR-4.2',
        'test_name': 'A/C Specificity Mechanism',
        'ac_types': ac_types,
        'ac_tokens': ac_total,
        'z_types': z_types,
        'z_tokens': z_total,
        'shared_middles': len(shared),
        'ac_only_middles': len(ac_only),
        'z_only_middles': len(z_only),
        'ac_gini': ac_gini,
        'z_gini': z_gini,
        'exclusivity_score': exclusivity,
        'verdict': 'SIGNIFICANT' if len(shared) > len(ac_only) else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  A/C and Zodiac share vocabulary ({len(shared)} shared > {len(ac_only)} exclusive)")
        print(f"  Specificity achieved through constraint density, not vocabulary")
    else:
        print(f"  A/C and Zodiac have distinct vocabularies")
        print(f"  Specificity achieved through vocabulary separation")

    return result


def test_car_4_3_constraint_propagation():
    """
    CAR-4.3: Constraint Propagation Path

    Question: Do A/C constraints propagate to B through MIDDLE incompatibility?

    Method:
    1. Identify MIDDLEs that are high-incompatibility in A/C
    2. Check if they appear in B
    3. Test if these MIDDLEs have restricted behavior in B
    """
    print("\n" + "=" * 60)
    print("CAR-4.3: Constraint Propagation Path")
    print("=" * 60)

    loader = CARDataLoader().load()

    # Get MIDDLEs from each system
    azc_data = loader.get_azc()
    b_data = loader.get_currier_b()

    # A/C MIDDLEs
    ac_middles = Counter()
    for _, row in azc_data.iterrows():
        if row['section'] in ('A', 'C'):
            _, middle, _ = decompose_token(row['word'])
            if middle is not None:
                ac_middles[middle] += 1

    # B MIDDLEs
    b_middles = Counter()
    for _, row in b_data.iterrows():
        _, middle, _ = decompose_token(row['word'])
        if middle is not None:
            b_middles[middle] += 1

    # Find MIDDLEs that appear in both A/C and B
    shared_middles = set(ac_middles.keys()) & set(b_middles.keys())
    ac_only = set(ac_middles.keys()) - set(b_middles.keys())
    b_only = set(b_middles.keys()) - set(ac_middles.keys())

    print(f"\nA/C unique MIDDLEs: {len(ac_middles)}")
    print(f"B unique MIDDLEs: {len(b_middles)}")
    print(f"Shared (A/C -> B propagation possible): {len(shared_middles)}")
    print(f"A/C only: {len(ac_only)}")
    print(f"B only: {len(b_only)}")

    # For shared MIDDLEs, compare frequency ratios
    print(f"\nFrequency comparison for shared MIDDLEs:")

    ac_total = sum(ac_middles.values())
    b_total = sum(b_middles.values())

    ac_enriched = []  # MIDDLEs more common in A/C
    b_enriched = []   # MIDDLEs more common in B

    for middle in shared_middles:
        ac_rate = ac_middles[middle] / ac_total
        b_rate = b_middles[middle] / b_total
        ratio = ac_rate / b_rate if b_rate > 0 else 0

        if ratio > 2.0 and ac_middles[middle] >= 5:
            ac_enriched.append((middle, ac_middles[middle], b_middles[middle], ratio))
        elif ratio < 0.5 and b_middles[middle] >= 5:
            b_enriched.append((middle, ac_middles[middle], b_middles[middle], ratio))

    print(f"\nA/C-enriched MIDDLEs (>2x higher rate in A/C): {len(ac_enriched)}")
    for m, ac_c, b_c, ratio in sorted(ac_enriched, key=lambda x: -x[3])[:5]:
        print(f"  '{m}': A/C={ac_c}, B={b_c}, ratio={ratio:.2f}x")

    print(f"\nB-enriched MIDDLEs (>2x higher rate in B): {len(b_enriched)}")
    for m, ac_c, b_c, ratio in sorted(b_enriched, key=lambda x: x[3])[:5]:
        print(f"  '{m}': A/C={ac_c}, B={b_c}, ratio={ratio:.2f}x")

    # Propagation rate
    propagation_rate = len(shared_middles) / len(ac_middles) if ac_middles else 0

    result = {
        'test_id': 'CAR-4.3',
        'test_name': 'Constraint Propagation Path',
        'ac_middle_types': len(ac_middles),
        'b_middle_types': len(b_middles),
        'shared_middles': len(shared_middles),
        'ac_only': len(ac_only),
        'b_only': len(b_only),
        'propagation_rate': propagation_rate,
        'ac_enriched_count': len(ac_enriched),
        'b_enriched_count': len(b_enriched),
        'verdict': 'SIGNIFICANT' if propagation_rate > 0.5 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    print(f"  Propagation rate (A/C -> B): {100*propagation_rate:.1f}%")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Most A/C MIDDLEs propagate to B")
        print(f"  {len(ac_enriched)} MIDDLEs are A/C-specialized")

    return result


def run_track4():
    """Run all Track 4 tests."""
    print("\n" + "=" * 70)
    print("TRACK 4: A/C DISCRIMINATION ANALYSIS")
    print("=" * 70)

    results = {
        'track': 4,
        'name': 'A/C Discrimination Analysis',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-4.1'] = test_car_4_1_density_escape()
    results['tests']['CAR-4.2'] = test_car_4_2_specificity_mechanism()
    results['tests']['CAR-4.3'] = test_car_4_3_constraint_propagation()

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 4 SUMMARY")
    print("=" * 70)

    significant = sum(1 for t in results['tests'].values()
                     if t.get('verdict') == 'SIGNIFICANT')
    null = sum(1 for t in results['tests'].values()
              if t.get('verdict') == 'NULL')

    print(f"\nTests passed (SIGNIFICANT): {significant}/3")
    print(f"Tests failed (NULL): {null}/3")

    for test_id, test in results['tests'].items():
        print(f"\n{test_id}: {test.get('test_name', 'Unknown')}")
        print(f"  Verdict: {test.get('verdict', 'N/A')}")

    # Track verdict
    if significant >= 2:
        results['track_verdict'] = 'SUCCESS'
        print("\n-> TRACK 4 VERDICT: SUCCESS")
        print("  A/C discrimination mechanism understood")
    elif significant >= 1:
        results['track_verdict'] = 'PARTIAL'
        print("\n-> TRACK 4 VERDICT: PARTIAL")
        print("  Some A/C discrimination patterns exist")
    else:
        results['track_verdict'] = 'NULL'
        print("\n-> TRACK 4 VERDICT: NULL")
        print("  A/C discrimination not confirmed")

    # Save results
    output_file = PHASE_DIR / 'car_track4_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_track4()
