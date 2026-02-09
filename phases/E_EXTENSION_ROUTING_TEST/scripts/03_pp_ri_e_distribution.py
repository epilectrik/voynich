#!/usr/bin/env python3
"""
E_EXTENSION_ROUTING_TEST - Script 03: PP vs RI E-Distribution

Test whether e-extension concentrates in RI vs PP MIDDLEs (Tier B test).

If e-extension concentrates in RI (A-exclusive) vocabulary, that would
explain why it doesn't propagate to B - RI MIDDLEs don't participate
in the PP pipeline that feeds B execution.

This is a more promising test because it works through documented
mechanisms (C498: PP/RI bifurcation).
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

def count_consecutive_e(word):
    """Count maximum consecutive e's in a word."""
    max_consec = 0
    current = 0
    for c in word:
        if c == 'e':
            current += 1
            max_consec = max(max_consec, current)
        else:
            current = 0
    return max_consec

def main():
    print("=" * 70)
    print("PP vs RI E-EXTENSION DISTRIBUTION")
    print("Testing whether e-extension concentrates in RI vocabulary")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    analyzer = RecordAnalyzer()

    # Collect MIDDLEs with their classification and e-metrics
    middle_data = defaultdict(lambda: {
        'occurrences': 0,
        'pp_count': 0,
        'ri_count': 0,
        'infra_count': 0,
        'unknown_count': 0,
        'total_e': 0,
        'max_consec_e': 0,
        'tokens': []
    })

    # Build MIDDLE inventory from Currier A with classification
    print("\nAnalyzing Currier A tokens...")

    # Get all unique folios
    folios = set()
    for token in tx.currier_a():
        folios.add(token.folio)

    # Analyze each folio
    for folio in sorted(folios):
        records = analyzer.analyze_folio(folio)
        for record in records:
            for t in record.tokens:
                m = morph.extract(t.word)
                middle = m.middle if m.middle else ''
                if not middle:
                    continue

                max_consec = count_consecutive_e(t.word)
                total_e = t.word.count('e')

                middle_data[middle]['occurrences'] += 1
                middle_data[middle]['tokens'].append(t.word)
                middle_data[middle]['total_e'] += total_e
                middle_data[middle]['max_consec_e'] = max(
                    middle_data[middle]['max_consec_e'],
                    max_consec
                )

                # Classification
                if t.token_class == 'PP':
                    middle_data[middle]['pp_count'] += 1
                elif t.token_class == 'RI':
                    middle_data[middle]['ri_count'] += 1
                elif t.token_class == 'INFRA':
                    middle_data[middle]['infra_count'] += 1
                else:
                    middle_data[middle]['unknown_count'] += 1

    # Classify each MIDDLE as predominantly PP, RI, or mixed
    pp_middles = []
    ri_middles = []
    mixed_middles = []

    for middle, data in middle_data.items():
        total = data['pp_count'] + data['ri_count'] + data['infra_count'] + data['unknown_count']
        if total == 0:
            continue

        pp_frac = data['pp_count'] / total
        ri_frac = data['ri_count'] / total

        data['pp_fraction'] = pp_frac
        data['ri_fraction'] = ri_frac
        data['mean_e'] = data['total_e'] / total

        if pp_frac >= 0.7:
            pp_middles.append((middle, data))
        elif ri_frac >= 0.7:
            ri_middles.append((middle, data))
        else:
            mixed_middles.append((middle, data))

    print(f"\nMIDDLE Classification:")
    print(f"  PP-dominant (>=70% PP): {len(pp_middles)}")
    print(f"  RI-dominant (>=70% RI): {len(ri_middles)}")
    print(f"  Mixed: {len(mixed_middles)}")

    # Compare e-extension between PP and RI
    print("\n" + "-" * 50)
    print("E-EXTENSION COMPARISON: PP vs RI")
    print("-" * 50)

    pp_max_consec = [d['max_consec_e'] for m, d in pp_middles]
    ri_max_consec = [d['max_consec_e'] for m, d in ri_middles]

    pp_mean_e = [d['mean_e'] for m, d in pp_middles]
    ri_mean_e = [d['mean_e'] for m, d in ri_middles]

    results = {
        'middle_counts': {
            'pp_dominant': len(pp_middles),
            'ri_dominant': len(ri_middles),
            'mixed': len(mixed_middles)
        },
        'max_consecutive_e': {},
        'mean_e_content': {},
        'high_e_distribution': {},
        'summary': {}
    }

    # Test 1: Max consecutive e comparison
    if pp_max_consec and ri_max_consec:
        u_stat, p = stats.mannwhitneyu(pp_max_consec, ri_max_consec, alternative='two-sided')
        pp_mean = np.mean(pp_max_consec)
        ri_mean = np.mean(ri_max_consec)

        results['max_consecutive_e'] = {
            'pp_mean': round(pp_mean, 4),
            'ri_mean': round(ri_mean, 4),
            'effect_size': round(ri_mean - pp_mean, 4),
            'mann_whitney_p': round(p, 6),
            'significant': bool(p < 0.05),
            'ri_higher': bool(ri_mean > pp_mean)
        }

        print(f"\nMax Consecutive E per MIDDLE:")
        print(f"  PP-dominant mean: {pp_mean:.4f}")
        print(f"  RI-dominant mean: {ri_mean:.4f}")
        print(f"  Difference (RI - PP): {ri_mean - pp_mean:.4f}")
        print(f"  Mann-Whitney p: {p:.6f}")
        print(f"  Significant: {p < 0.05}")
        if p < 0.05:
            if ri_mean > pp_mean:
                print(f"  ** RI has HIGHER e-extension than PP **")
            else:
                print(f"  ** PP has HIGHER e-extension than RI **")

    # Test 2: Mean e-content comparison
    if pp_mean_e and ri_mean_e:
        u_stat, p = stats.mannwhitneyu(pp_mean_e, ri_mean_e, alternative='two-sided')
        pp_m = np.mean(pp_mean_e)
        ri_m = np.mean(ri_mean_e)

        results['mean_e_content'] = {
            'pp_mean': round(pp_m, 4),
            'ri_mean': round(ri_m, 4),
            'effect_size': round(ri_m - pp_m, 4),
            'mann_whitney_p': round(p, 6),
            'significant': bool(p < 0.05),
            'ri_higher': bool(ri_m > pp_m)
        }

        print(f"\nMean E-Content per MIDDLE:")
        print(f"  PP-dominant mean: {pp_m:.4f}")
        print(f"  RI-dominant mean: {ri_m:.4f}")
        print(f"  Difference (RI - PP): {ri_m - pp_m:.4f}")
        print(f"  Mann-Whitney p: {p:.6f}")
        print(f"  Significant: {p < 0.05}")

    # Test 3: Where are high-e MIDDLEs (triple+ consecutive)?
    print("\n" + "-" * 50)
    print("HIGH E-EXTENSION MIDDLE DISTRIBUTION")
    print("-" * 50)

    high_e_pp = [(m, d) for m, d in pp_middles if d['max_consec_e'] >= 3]
    high_e_ri = [(m, d) for m, d in ri_middles if d['max_consec_e'] >= 3]
    high_e_mixed = [(m, d) for m, d in mixed_middles if d['max_consec_e'] >= 3]

    total_high_e = len(high_e_pp) + len(high_e_ri) + len(high_e_mixed)

    results['high_e_distribution'] = {
        'threshold': 'triple_e_or_higher',
        'pp_count': len(high_e_pp),
        'ri_count': len(high_e_ri),
        'mixed_count': len(high_e_mixed),
        'total': total_high_e,
        'pp_fraction': round(len(high_e_pp) / total_high_e, 4) if total_high_e > 0 else 0,
        'ri_fraction': round(len(high_e_ri) / total_high_e, 4) if total_high_e > 0 else 0
    }

    print(f"\nMIDDLEs with triple+ consecutive e:")
    print(f"  In PP-dominant: {len(high_e_pp)}")
    print(f"  In RI-dominant: {len(high_e_ri)}")
    print(f"  In Mixed: {len(high_e_mixed)}")
    print(f"  Total: {total_high_e}")

    if total_high_e > 0:
        print(f"\n  PP fraction: {len(high_e_pp)/total_high_e:.1%}")
        print(f"  RI fraction: {len(high_e_ri)/total_high_e:.1%}")

        # Chi-square test for distribution
        # Expected: proportional to overall PP/RI ratio
        pp_total = len(pp_middles)
        ri_total = len(ri_middles)
        total_classified = pp_total + ri_total

        if total_classified > 0:
            expected_pp_frac = pp_total / total_classified
            expected_ri_frac = ri_total / total_classified

            observed = [len(high_e_pp), len(high_e_ri)]
            expected = [total_high_e * expected_pp_frac, total_high_e * expected_ri_frac]

            if min(expected) >= 5:
                # Normalize expected to match observed sum
                expected = [e * sum(observed) / sum(expected) for e in expected]
                chi2, p = stats.chisquare(observed, expected)
                results['high_e_distribution']['chi2'] = round(chi2, 4)
                results['high_e_distribution']['chi2_p'] = round(p, 6)
                results['high_e_distribution']['chi2_significant'] = p < 0.05

                print(f"\n  Chi-square test (vs baseline PP/RI ratio):")
                print(f"    Expected PP: {expected[0]:.1f}, Observed: {observed[0]}")
                print(f"    Expected RI: {expected[1]:.1f}, Observed: {observed[1]}")
                print(f"    Chi2: {chi2:.4f}, p: {p:.6f}")
                print(f"    Significant: {p < 0.05}")

    # List high-e MIDDLEs
    print("\n" + "-" * 50)
    print("HIGH-E MIDDLES INVENTORY")
    print("-" * 50)

    if high_e_ri:
        print(f"\nRI-dominant MIDDLEs with triple+ e:")
        for m, d in sorted(high_e_ri, key=lambda x: -x[1]['max_consec_e'])[:15]:
            print(f"  {m}: max_consec={d['max_consec_e']}, occ={d['occurrences']}, sample={d['tokens'][:3]}")

    if high_e_pp:
        print(f"\nPP-dominant MIDDLEs with triple+ e:")
        for m, d in sorted(high_e_pp, key=lambda x: -x[1]['max_consec_e'])[:15]:
            print(f"  {m}: max_consec={d['max_consec_e']}, occ={d['occurrences']}, sample={d['tokens'][:3]}")

    # Summary
    print("\n" + "=" * 70)
    print("TIER B TEST 1 SUMMARY")
    print("=" * 70)

    ri_higher_max = results['max_consecutive_e'].get('ri_higher', False)
    ri_higher_mean = results['mean_e_content'].get('ri_higher', False)
    max_sig = results['max_consecutive_e'].get('significant', False)
    mean_sig = results['mean_e_content'].get('significant', False)

    if ri_higher_max and max_sig:
        verdict = "E-EXTENSION CONCENTRATES IN RI - explains non-propagation to B"
    elif not ri_higher_max and not ri_higher_mean:
        verdict = "E-EXTENSION CONCENTRATES IN PP - should propagate to B"
    else:
        verdict = "NO CLEAR CONCENTRATION - e-extension distributed across PP/RI"

    results['summary'] = {
        'ri_has_higher_e_extension': ri_higher_max,
        'difference_significant': max_sig or mean_sig,
        'verdict': verdict
    }

    print(f"\n  RI has higher e-extension: {ri_higher_max}")
    print(f"  Difference significant: {max_sig or mean_sig}")
    print(f"\n  VERDICT: {verdict}")

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / '03_pp_ri_e_distribution.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
