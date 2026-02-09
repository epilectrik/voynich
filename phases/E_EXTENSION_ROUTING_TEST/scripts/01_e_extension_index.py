#!/usr/bin/env python3
"""
E_EXTENSION_ROUTING_TEST - Script 01: E-Extension Index Computation

Compute e-extension metrics for each Currier A folio:
- Mean e-count per token
- Mean consecutive e-count (ee, eee, eeee patterns)
- Max e-extension observed
- E-extension vocabulary profile

This provides the A-side metrics for routing correlation tests.
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

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

def count_total_e(word):
    """Count total e's in a word."""
    return word.count('e')

def classify_e_extension(max_consec):
    """Classify e-extension level."""
    if max_consec >= 4:
        return 'quadruple'
    elif max_consec == 3:
        return 'triple'
    elif max_consec == 2:
        return 'double'
    elif max_consec == 1:
        return 'single'
    else:
        return 'none'

def main():
    tx = Transcript()
    morph = Morphology()

    # Collect per-folio metrics
    folio_data = defaultdict(lambda: {
        'tokens': [],
        'total_e_counts': [],
        'max_consec_e': [],
        'e_extension_classes': defaultdict(int),
        'middles_with_e': set(),
        'middles_total': set()
    })

    # Process all Currier A tokens
    for token in tx.currier_a():
        folio = token.folio
        word = token.word

        m = morph.extract(word)
        middle = m.middle if m.middle else ''

        total_e = count_total_e(word)
        max_consec = count_consecutive_e(word)
        ext_class = classify_e_extension(max_consec)

        folio_data[folio]['tokens'].append(word)
        folio_data[folio]['total_e_counts'].append(total_e)
        folio_data[folio]['max_consec_e'].append(max_consec)
        folio_data[folio]['e_extension_classes'][ext_class] += 1

        if middle:
            folio_data[folio]['middles_total'].add(middle)
            if 'e' in middle:
                folio_data[folio]['middles_with_e'].add(middle)

    # Compute summary metrics per folio
    results = {
        'folios': {},
        'corpus_summary': {},
        'quadruple_e_tokens': [],
        'triple_e_tokens': []
    }

    all_max_consec = []
    all_total_e = []

    for folio in sorted(folio_data.keys()):
        data = folio_data[folio]
        n_tokens = len(data['tokens'])

        if n_tokens == 0:
            continue

        mean_total_e = sum(data['total_e_counts']) / n_tokens
        mean_max_consec = sum(data['max_consec_e']) / n_tokens
        max_consec_in_folio = max(data['max_consec_e'])

        # E-extension distribution
        ext_dist = dict(data['e_extension_classes'])

        # Fraction of MIDDLEs containing e
        n_middles = len(data['middles_total'])
        n_middles_e = len(data['middles_with_e'])
        middle_e_fraction = n_middles_e / n_middles if n_middles > 0 else 0

        results['folios'][folio] = {
            'n_tokens': n_tokens,
            'mean_total_e': round(mean_total_e, 4),
            'mean_max_consecutive_e': round(mean_max_consec, 4),
            'max_consecutive_e_in_folio': max_consec_in_folio,
            'e_extension_distribution': ext_dist,
            'n_middles': n_middles,
            'n_middles_with_e': n_middles_e,
            'middle_e_fraction': round(middle_e_fraction, 4)
        }

        all_max_consec.extend(data['max_consec_e'])
        all_total_e.extend(data['total_e_counts'])

        # Track extreme e tokens
        for i, word in enumerate(data['tokens']):
            consec = data['max_consec_e'][i]
            if consec >= 4:
                results['quadruple_e_tokens'].append({'folio': folio, 'token': word, 'max_consec': consec})
            elif consec == 3:
                results['triple_e_tokens'].append({'folio': folio, 'token': word, 'max_consec': consec})

    # Corpus-level summary
    results['corpus_summary'] = {
        'n_folios': len(results['folios']),
        'n_tokens': len(all_max_consec),
        'mean_total_e': round(sum(all_total_e) / len(all_total_e), 4) if all_total_e else 0,
        'mean_max_consecutive_e': round(sum(all_max_consec) / len(all_max_consec), 4) if all_max_consec else 0,
        'n_quadruple_e_tokens': len(results['quadruple_e_tokens']),
        'n_triple_e_tokens': len(results['triple_e_tokens']),
        'folios_with_quadruple_e': len(set(t['folio'] for t in results['quadruple_e_tokens'])),
        'folios_with_triple_e': len(set(t['folio'] for t in results['triple_e_tokens']))
    }

    # Identify high-e and low-e folios (top/bottom quartile by mean_max_consecutive_e)
    folio_scores = [(f, d['mean_max_consecutive_e']) for f, d in results['folios'].items()]
    folio_scores.sort(key=lambda x: x[1], reverse=True)

    n = len(folio_scores)
    q1_idx = n // 4

    results['high_e_folios'] = [f for f, s in folio_scores[:q1_idx]]
    results['low_e_folios'] = [f for f, s in folio_scores[-q1_idx:]]

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / '01_e_extension_index.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("=" * 70)
    print("E-EXTENSION INDEX - CURRIER A")
    print("=" * 70)
    print(f"\nCorpus Summary:")
    print(f"  Folios analyzed: {results['corpus_summary']['n_folios']}")
    print(f"  Tokens analyzed: {results['corpus_summary']['n_tokens']}")
    print(f"  Mean total e per token: {results['corpus_summary']['mean_total_e']}")
    print(f"  Mean max consecutive e: {results['corpus_summary']['mean_max_consecutive_e']}")
    print(f"\nExtreme E-Extension:")
    print(f"  Quadruple-e tokens: {results['corpus_summary']['n_quadruple_e_tokens']} in {results['corpus_summary']['folios_with_quadruple_e']} folios")
    print(f"  Triple-e tokens: {results['corpus_summary']['n_triple_e_tokens']} in {results['corpus_summary']['folios_with_triple_e']} folios")

    print(f"\nTop 10 High-E Folios (by mean max consecutive e):")
    for folio, score in folio_scores[:10]:
        data = results['folios'][folio]
        print(f"  {folio}: mean_max_consec={score:.4f}, max_in_folio={data['max_consecutive_e_in_folio']}, n={data['n_tokens']}")

    print(f"\nBottom 10 Low-E Folios:")
    for folio, score in folio_scores[-10:]:
        data = results['folios'][folio]
        print(f"  {folio}: mean_max_consec={score:.4f}, max_in_folio={data['max_consecutive_e_in_folio']}, n={data['n_tokens']}")

    if results['quadruple_e_tokens']:
        print(f"\nQuadruple-E Tokens (eeee+):")
        for t in results['quadruple_e_tokens'][:20]:
            print(f"  {t['folio']}: {t['token']} (max_consec={t['max_consec']})")

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
