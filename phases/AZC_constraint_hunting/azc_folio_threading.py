"""
F-AZC-011: AZC Folio Threading Analysis

Exploratory analysis of how AZC folios thread into A and B vocabulary.

Questions:
1. Do different AZC folios reference different subsets of A vocabulary?
2. When B procedures use AZC vocabulary, which AZC folios contribute?
3. Is there structure in the AZC->A and AZC->B threading patterns?

Known constraints:
- C300: 30 AZC folios (9,401 tokens)
- C321: Zodiac vocabulary isolated (Jaccard=0.076 between consecutive)
- C335: 69.8% of B tokens appear in A vocabulary
- C343: A-vocab tokens appear in 2.2x more AZC placements
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


def load_tokens_with_currier(filepath):
    """Load all tokens with Currier A/B classification from TSV file."""
    a_tokens = set()
    b_tokens = set()
    azc_tokens = set()

    a_folios = defaultdict(list)
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
            language = row.get('language', '').strip()  # A or B
            section = row.get('section', '').strip()

            # Skip empty or invalid tokens
            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Classify based on Currier language AND section
            # Section Z, A, C are AZC (Astronomical/Zodiac/Cosmological)
            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')

            if is_azc:
                azc_tokens.add(word)
                azc_folios[folio].append(word)
            elif language == 'A':
                a_tokens.add(word)
                a_folios[folio].append(word)
            elif language == 'B':
                b_tokens.add(word)
                b_folios[folio].append(word)

    return {
        'a_tokens': a_tokens,
        'b_tokens': b_tokens,
        'azc_tokens': azc_tokens,
        'a_folios': dict(a_folios),
        'b_folios': dict(b_folios),
        'azc_folios': dict(azc_folios)
    }


def calculate_vocabulary_overlap(folio_tokens, reference_vocab):
    """Calculate what fraction of folio's vocabulary appears in reference."""
    folio_types = set(folio_tokens)
    if not folio_types:
        return 0, 0, set()

    overlap = folio_types & reference_vocab
    overlap_count = len(overlap)
    overlap_rate = overlap_count / len(folio_types) * 100

    return overlap_count, overlap_rate, overlap


def analyze_azc_folio_threading(data):
    """Analyze how each AZC folio threads into A and B vocabulary."""
    results = {}

    a_vocab = data['a_tokens']
    b_vocab = data['b_tokens']

    for folio, tokens in data['azc_folios'].items():
        types = set(tokens)

        # Overlap with A
        a_overlap_count, a_overlap_rate, a_overlap_types = calculate_vocabulary_overlap(tokens, a_vocab)

        # Overlap with B
        b_overlap_count, b_overlap_rate, b_overlap_types = calculate_vocabulary_overlap(tokens, b_vocab)

        # Endemic (AZC-only)
        endemic = types - a_vocab - b_vocab
        endemic_rate = len(endemic) / len(types) * 100 if types else 0

        # Shared (appears in both A and B)
        shared_with_ab = types & a_vocab & b_vocab
        shared_rate = len(shared_with_ab) / len(types) * 100 if types else 0

        results[folio] = {
            'token_count': len(tokens),
            'type_count': len(types),
            'a_overlap': {
                'count': a_overlap_count,
                'rate': round(a_overlap_rate, 1),
                'types': sorted(list(a_overlap_types))[:20]
            },
            'b_overlap': {
                'count': b_overlap_count,
                'rate': round(b_overlap_rate, 1),
                'types': sorted(list(b_overlap_types))[:20]
            },
            'endemic': {
                'count': len(endemic),
                'rate': round(endemic_rate, 1),
                'types': sorted(list(endemic))[:20]
            },
            'shared_ab': {
                'count': len(shared_with_ab),
                'rate': round(shared_rate, 1)
            }
        }

    return results


def analyze_b_folio_azc_sourcing(data):
    """For each B folio, which AZC folios contribute vocabulary?"""
    results = {}

    # Build AZC vocabulary by folio
    azc_vocab_by_folio = {}
    for folio, tokens in data['azc_folios'].items():
        azc_vocab_by_folio[folio] = set(tokens)

    # All AZC vocabulary
    all_azc_vocab = set()
    for types in azc_vocab_by_folio.values():
        all_azc_vocab.update(types)

    for b_folio, tokens in data['b_folios'].items():
        b_types = set(tokens)

        # What fraction of B vocabulary is in AZC?
        azc_overlap = b_types & all_azc_vocab
        azc_overlap_rate = len(azc_overlap) / len(b_types) * 100 if b_types else 0

        # Which AZC folios contribute?
        azc_sources = {}
        for azc_folio, azc_types in azc_vocab_by_folio.items():
            contrib = b_types & azc_types
            if contrib:
                azc_sources[azc_folio] = {
                    'count': len(contrib),
                    'types': sorted(list(contrib))[:10]
                }

        results[b_folio] = {
            'token_count': len(tokens),
            'type_count': len(b_types),
            'azc_overlap_rate': round(azc_overlap_rate, 1),
            'azc_source_count': len(azc_sources),
            'azc_sources': azc_sources
        }

    return results


def analyze_a_entry_azc_coverage(data):
    """Which A vocabulary types appear in which AZC folios?"""
    # Build reverse index: A type -> which AZC folios contain it
    a_type_to_azc = defaultdict(set)

    for azc_folio, tokens in data['azc_folios'].items():
        azc_types = set(tokens)
        for a_type in data['a_tokens']:
            if a_type in azc_types:
                a_type_to_azc[a_type].add(azc_folio)

    # Analyze distribution
    coverage_dist = defaultdict(int)
    for a_type, azc_folios in a_type_to_azc.items():
        coverage_dist[len(azc_folios)] += 1

    # Types that appear in many AZC folios (high coverage)
    high_coverage = [(t, len(f)) for t, f in a_type_to_azc.items() if len(f) >= 5]
    high_coverage.sort(key=lambda x: -x[1])

    # Types that appear in few AZC folios (low coverage)
    low_coverage = [(t, list(f)) for t, f in a_type_to_azc.items() if len(f) == 1]

    return {
        'total_a_types_in_azc': len(a_type_to_azc),
        'coverage_distribution': dict(coverage_dist),
        'high_coverage_types': high_coverage[:30],
        'low_coverage_count': len(low_coverage),
        'low_coverage_examples': low_coverage[:20]
    }


def calculate_azc_folio_similarity(data):
    """Calculate Jaccard similarity between AZC folios."""
    folios = list(data['azc_folios'].keys())
    folio_types = {f: set(tokens) for f, tokens in data['azc_folios'].items()}

    similarities = {}
    for i, f1 in enumerate(folios):
        for f2 in folios[i+1:]:
            t1, t2 = folio_types[f1], folio_types[f2]
            if t1 and t2:
                jaccard = len(t1 & t2) / len(t1 | t2)
                similarities[f'{f1}:{f2}'] = round(jaccard, 3)

    if not similarities:
        return {
            'mean_jaccard': 0,
            'most_similar': [],
            'least_similar': []
        }

    # Sort by similarity
    sorted_sims = sorted(similarities.items(), key=lambda x: -x[1])

    # Calculate mean similarity
    mean_sim = sum(similarities.values()) / len(similarities) if similarities else 0

    return {
        'mean_jaccard': round(mean_sim, 3),
        'most_similar': sorted_sims[:10],
        'least_similar': sorted_sims[-10:] if len(sorted_sims) >= 10 else sorted_sims
    }


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("Loading tokens by folio with Currier classification...")
    data = load_tokens_with_currier(data_path)

    print(f"  A folios: {len(data['a_folios'])} ({len(data['a_tokens'])} types)")
    print(f"  B folios: {len(data['b_folios'])} ({len(data['b_tokens'])} types)")
    print(f"  AZC folios: {len(data['azc_folios'])} ({len(data['azc_tokens'])} types)")

    if not data['azc_folios']:
        print("\nNo AZC folios found! Check section classification.")
        return

    print("\n" + "="*60)
    print("ANALYSIS 1: AZC Folio Threading to A and B")
    print("="*60)

    threading = analyze_azc_folio_threading(data)

    # Summary by folio
    print("\nPer-folio overlap rates:")
    print(f"{'Folio':<10} {'Tokens':>8} {'Types':>6} {'A%':>6} {'B%':>6} {'Endemic%':>9}")
    print("-"*50)

    a_rates = []
    b_rates = []
    endemic_rates = []

    for folio in sorted(threading.keys()):
        stats = threading[folio]
        print(f"{folio:<10} {stats['token_count']:>8} {stats['type_count']:>6} "
              f"{stats['a_overlap']['rate']:>6.1f} {stats['b_overlap']['rate']:>6.1f} "
              f"{stats['endemic']['rate']:>9.1f}")
        a_rates.append(stats['a_overlap']['rate'])
        b_rates.append(stats['b_overlap']['rate'])
        endemic_rates.append(stats['endemic']['rate'])

    if a_rates:
        print("-"*50)
        print(f"{'MEAN':<10} {'':>8} {'':>6} {sum(a_rates)/len(a_rates):>6.1f} "
              f"{sum(b_rates)/len(b_rates):>6.1f} {sum(endemic_rates)/len(endemic_rates):>9.1f}")

    print("\n" + "="*60)
    print("ANALYSIS 2: AZC Folio Inter-Similarity")
    print("="*60)

    similarity = calculate_azc_folio_similarity(data)
    print(f"\nMean Jaccard similarity: {similarity['mean_jaccard']}")
    print(f"(Compare to C321: 0.076 for consecutive zodiac)")

    if similarity['most_similar']:
        print("\nMost similar pairs:")
        for pair, sim in similarity['most_similar'][:5]:
            print(f"  {pair}: {sim}")

        print("\nLeast similar pairs:")
        for pair, sim in similarity['least_similar'][:5]:
            print(f"  {pair}: {sim}")

    print("\n" + "="*60)
    print("ANALYSIS 3: A-Type Coverage Across AZC Folios")
    print("="*60)

    a_coverage = analyze_a_entry_azc_coverage(data)
    print(f"\nA-types appearing in AZC: {a_coverage['total_a_types_in_azc']}")
    print("\nCoverage distribution (# AZC folios -> # A-types):")
    for n_folios in sorted(a_coverage['coverage_distribution'].keys()):
        count = a_coverage['coverage_distribution'][n_folios]
        print(f"  {n_folios} folio(s): {count} A-types")

    if a_coverage['high_coverage_types']:
        print("\nHigh-coverage A-types (appear in 5+ AZC folios):")
        for token, count in a_coverage['high_coverage_types'][:15]:
            print(f"  {token}: {count} folios")

    print(f"\nLow-coverage A-types (appear in exactly 1 AZC folio): {a_coverage['low_coverage_count']}")

    print("\n" + "="*60)
    print("ANALYSIS 4: B Folio AZC Sourcing")
    print("="*60)

    b_sourcing = analyze_b_folio_azc_sourcing(data)

    if b_sourcing:
        # Summary
        source_counts = [s['azc_source_count'] for s in b_sourcing.values()]
        azc_rates = [s['azc_overlap_rate'] for s in b_sourcing.values()]

        print(f"\nB folios analyzed: {len(b_sourcing)}")
        print(f"Mean AZC vocabulary overlap: {sum(azc_rates)/len(azc_rates):.1f}%")
        print(f"Mean AZC source folios per B: {sum(source_counts)/len(source_counts):.1f}")
        print(f"Range: {min(source_counts)} - {max(source_counts)} source folios")

        # Examples of concentrated vs distributed sourcing
        sorted_b = sorted(b_sourcing.items(), key=lambda x: x[1]['azc_source_count'])

        print("\nB folios with fewest AZC sources:")
        for folio, stats in sorted_b[:5]:
            print(f"  {folio}: {stats['azc_source_count']} sources, {stats['azc_overlap_rate']:.1f}% AZC vocab")

        print("\nB folios with most AZC sources:")
        for folio, stats in sorted_b[-5:]:
            print(f"  {folio}: {stats['azc_source_count']} sources, {stats['azc_overlap_rate']:.1f}% AZC vocab")
    else:
        source_counts = []
        azc_rates = []

    # Build output
    output = {
        'fit_id': 'F-AZC-011',
        'question': 'How do AZC folios thread into A and B vocabulary?',
        'metadata': {
            'a_folios': len(data['a_folios']),
            'b_folios': len(data['b_folios']),
            'azc_folios': len(data['azc_folios']),
            'a_types': len(data['a_tokens']),
            'b_types': len(data['b_tokens']),
            'azc_types': len(data['azc_tokens'])
        },
        'azc_threading': {
            'mean_a_overlap': round(sum(a_rates)/len(a_rates), 1) if a_rates else 0,
            'mean_b_overlap': round(sum(b_rates)/len(b_rates), 1) if b_rates else 0,
            'mean_endemic': round(sum(endemic_rates)/len(endemic_rates), 1) if endemic_rates else 0,
            'per_folio': threading
        },
        'azc_similarity': similarity,
        'a_coverage': a_coverage,
        'b_sourcing': {
            'mean_azc_overlap': round(sum(azc_rates)/len(azc_rates), 1) if azc_rates else 0,
            'mean_source_count': round(sum(source_counts)/len(source_counts), 1) if source_counts else 0,
            'source_count_range': [min(source_counts), max(source_counts)] if source_counts else [0, 0]
        },
        'interpretation': {}
    }

    # Interpret findings
    findings = []

    if a_rates:
        # Finding 1: Variance in A/B threading
        a_variance = max(a_rates) - min(a_rates)
        b_variance = max(b_rates) - min(b_rates)
        if a_variance > 20 or b_variance > 20:
            findings.append(f"High variance in threading: A={a_variance:.0f}pp, B={b_variance:.0f}pp")

        # Finding 2: Endemic rate variation
        endemic_variance = max(endemic_rates) - min(endemic_rates)
        if endemic_variance > 20:
            findings.append(f"Endemic rate varies by {endemic_variance:.0f}pp across AZC folios")

    # Finding 3: Cross-folio similarity
    if similarity['mean_jaccard'] < 0.15:
        findings.append(f"AZC folios have LOW vocabulary overlap (mean Jaccard={similarity['mean_jaccard']})")

    # Finding 4: B sourcing pattern
    if source_counts and max(source_counts) - min(source_counts) > 10:
        findings.append(f"B folios vary widely in AZC sourcing ({min(source_counts)}-{max(source_counts)} sources)")

    output['interpretation']['findings'] = findings
    output['interpretation']['fit_tier'] = 'EXPLORATORY'

    # Save results
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_folio_threading.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for finding in findings:
        print(f"  - {finding}")


if __name__ == '__main__':
    main()
