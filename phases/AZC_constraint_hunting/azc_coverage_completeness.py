"""
F-AZC-012: AZC Coverage Completeness Test

Question: Does AZC collectively cover ALL A-vocabulary tokens that appear in B procedures?

If AZC is a "complete orientation basis", it should cover essentially 100% of the
A-types that B procedures reference. Gaps would indicate incomplete coverage.

Method:
1. Extract all A-types that appear in B procedures
2. Extract union of all A-types in AZC folios
3. Calculate coverage: |B's A-types ∩ AZC's A-types| / |B's A-types|
"""

import json
from collections import defaultdict
from pathlib import Path
import csv


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


def load_tokens_by_system(filepath):
    """Load tokens classified by Currier system."""
    a_tokens = set()
    b_tokens = set()
    azc_tokens = set()

    b_folios = defaultdict(list)
    azc_folios = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
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

            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')

            if is_azc:
                azc_tokens.add(word)
                azc_folios[folio].append(word)
            elif language == 'A':
                a_tokens.add(word)
            elif language == 'B':
                b_tokens.add(word)
                b_folios[folio].append(word)

    return {
        'a_tokens': a_tokens,
        'b_tokens': b_tokens,
        'azc_tokens': azc_tokens,
        'b_folios': dict(b_folios),
        'azc_folios': dict(azc_folios)
    }


def analyze_coverage(data):
    """Analyze whether AZC covers all A-types used by B."""
    a_vocab = data['a_tokens']
    b_vocab = data['b_tokens']
    azc_vocab = data['azc_tokens']

    # A-types that appear in B procedures
    a_in_b = a_vocab & b_vocab

    # A-types that appear in AZC
    a_in_azc = a_vocab & azc_vocab

    # Coverage: what fraction of B's A-types are also in AZC?
    b_a_covered_by_azc = a_in_b & azc_vocab
    coverage_rate = len(b_a_covered_by_azc) / len(a_in_b) * 100 if a_in_b else 0

    # Gap analysis: A-types in B but NOT in AZC
    gap = a_in_b - azc_vocab

    # Bonus: A-types in AZC but NOT in B (excess coverage)
    excess = a_in_azc - b_vocab

    return {
        'a_vocab_size': len(a_vocab),
        'b_vocab_size': len(b_vocab),
        'azc_vocab_size': len(azc_vocab),
        'a_types_in_b': len(a_in_b),
        'a_types_in_azc': len(a_in_azc),
        'a_types_covered': len(b_a_covered_by_azc),
        'coverage_rate': round(coverage_rate, 2),
        'gap_count': len(gap),
        'gap_types': sorted(list(gap))[:50],
        'excess_count': len(excess),
        'excess_types': sorted(list(excess))[:50]
    }


def analyze_per_b_folio_coverage(data):
    """For each B folio, what fraction of its A-types are covered by AZC?"""
    a_vocab = data['a_tokens']
    azc_vocab = data['azc_tokens']

    results = {}
    coverage_rates = []

    for folio, tokens in data['b_folios'].items():
        b_types = set(tokens)

        # A-types used by this B folio
        a_in_this_b = b_types & a_vocab

        # Coverage by AZC
        covered = a_in_this_b & azc_vocab
        coverage = len(covered) / len(a_in_this_b) * 100 if a_in_this_b else 100

        results[folio] = {
            'a_types_used': len(a_in_this_b),
            'a_types_covered': len(covered),
            'coverage_rate': round(coverage, 1)
        }
        coverage_rates.append(coverage)

    return {
        'per_folio': results,
        'mean_coverage': round(sum(coverage_rates) / len(coverage_rates), 1) if coverage_rates else 0,
        'min_coverage': round(min(coverage_rates), 1) if coverage_rates else 0,
        'max_coverage': round(max(coverage_rates), 1) if coverage_rates else 0
    }


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("Loading tokens by system...")
    data = load_tokens_by_system(data_path)

    print(f"  A vocabulary: {len(data['a_tokens'])} types")
    print(f"  B vocabulary: {len(data['b_tokens'])} types")
    print(f"  AZC vocabulary: {len(data['azc_tokens'])} types")

    print("\n" + "="*60)
    print("ANALYSIS: AZC Coverage of B's A-Types")
    print("="*60)

    coverage = analyze_coverage(data)

    print(f"\nA-types appearing in B: {coverage['a_types_in_b']}")
    print(f"A-types appearing in AZC: {coverage['a_types_in_azc']}")
    print(f"A-types in B covered by AZC: {coverage['a_types_covered']}")
    print(f"\n>>> COVERAGE RATE: {coverage['coverage_rate']}% <<<")

    if coverage['gap_count'] > 0:
        print(f"\nGap (A-types in B but not AZC): {coverage['gap_count']}")
        print(f"Examples: {', '.join(coverage['gap_types'][:20])}")
    else:
        print("\nNo gap - AZC covers 100% of B's A-vocabulary!")

    print(f"\nExcess (A-types in AZC but not B): {coverage['excess_count']}")

    print("\n" + "="*60)
    print("PER-FOLIO COVERAGE")
    print("="*60)

    per_folio = analyze_per_b_folio_coverage(data)

    print(f"\nMean coverage per B folio: {per_folio['mean_coverage']}%")
    print(f"Min coverage: {per_folio['min_coverage']}%")
    print(f"Max coverage: {per_folio['max_coverage']}%")

    # Show folios with lowest coverage
    sorted_folios = sorted(per_folio['per_folio'].items(),
                          key=lambda x: x[1]['coverage_rate'])

    print("\nB folios with lowest AZC coverage of their A-types:")
    for folio, stats in sorted_folios[:10]:
        print(f"  {folio}: {stats['coverage_rate']}% ({stats['a_types_covered']}/{stats['a_types_used']})")

    # Build output
    output = {
        'fit_id': 'F-AZC-012',
        'question': 'Does AZC cover all A-types used by B procedures?',
        'aggregate': coverage,
        'per_folio_summary': {
            'mean': per_folio['mean_coverage'],
            'min': per_folio['min_coverage'],
            'max': per_folio['max_coverage']
        },
        'interpretation': {}
    }

    # Interpret
    if coverage['coverage_rate'] >= 99:
        output['interpretation']['conclusion'] = 'AZC is a COMPLETE orientation basis'
        output['interpretation']['evidence'] = f"{coverage['coverage_rate']}% coverage of B's A-vocabulary"
        output['interpretation']['fit_tier'] = 'F2 (CONFIRMED)'
    elif coverage['coverage_rate'] >= 95:
        output['interpretation']['conclusion'] = 'AZC is NEAR-COMPLETE orientation basis'
        output['interpretation']['evidence'] = f"{coverage['coverage_rate']}% coverage with minor gaps"
        output['interpretation']['fit_tier'] = 'F2 (CONFIRMED)'
    else:
        output['interpretation']['conclusion'] = 'AZC coverage is INCOMPLETE'
        output['interpretation']['evidence'] = f"Only {coverage['coverage_rate']}% coverage"
        output['interpretation']['fit_tier'] = 'F3 (PARTIAL)'

    # Save
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_coverage_completeness.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print(f"  {output['interpretation']['conclusion']}")
    print(f"  {output['interpretation']['evidence']}")


if __name__ == '__main__':
    main()
