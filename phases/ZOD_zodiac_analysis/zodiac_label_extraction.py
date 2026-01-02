#!/usr/bin/env python3
"""
Zodiac Label Extraction

Extract words that appear on zodiac folios, with focus on:
1. Words unique to zodiac pages (not elsewhere in manuscript)
2. Words appearing on only ONE zodiac folio (potential labels)

NO SEMANTIC ASSUMPTIONS - purely distributional analysis.
"""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple


# Standard zodiac folio mappings based on Voynich scholarship
# Note: Some folios have multiple sub-pages with different zodiac signs
ZODIAC_FOLIO_MAP = {
    # f67-f69 appear to be cosmological/astronomical rather than zodiac
    # The main zodiac section is f70-f73
    'f70r1': 'Pisces',       # March sign
    'f70r2': 'Pisces',       # March sign continued
    'f70v1': 'Pisces',       # March sign continued
    'f70v2': 'Aries',        # April sign
    'f71r': 'Taurus',        # April-May sign (bull illustration)
    'f71v': 'Taurus',        # Taurus continued
    'f72r1': 'Gemini',       # May-June sign
    'f72r2': 'Cancer',       # June-July sign
    'f72r3': 'Leo',          # July-August sign
    'f72v1': 'Virgo',        # August-September sign
    'f72v2': 'Libra',        # September-October sign
    'f72v3': 'Scorpio',      # October-November sign
    'f73r': 'Sagittarius',   # November-December sign
    'f73v': 'Capricorn',     # December-January sign
}

# Broader zodiac section (including surrounding cosmological pages)
ZODIAC_SECTION_FOLIOS = [
    'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v',
    'f70r1', 'f70r2', 'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
]

# Core zodiac pages (with clear zodiac imagery)
CORE_ZODIAC_FOLIOS = list(ZODIAC_FOLIO_MAP.keys())


def load_corpus() -> Tuple[List[Dict], Dict[str, List[str]]]:
    """Load corpus and build folio-to-words mapping."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    words = []
    folio_words = defaultdict(list)
    word_folios = defaultdict(set)

    seen = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')

            # Skip empty or special markers
            if not word or word.startswith('*') or len(word) < 2:
                continue

            # Deduplicate
            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({'word': word, 'folio': folio})
                folio_words[folio].append(word)
                word_folios[word].add(folio)

    return words, dict(folio_words), dict(word_folios)


def extract_zodiac_vocabulary(folio_words: Dict[str, List[str]]) -> Dict[str, Dict]:
    """Extract vocabulary statistics for each zodiac folio."""
    results = {}

    for folio in ZODIAC_SECTION_FOLIOS:
        if folio not in folio_words:
            continue

        words = folio_words[folio]
        word_counts = Counter(words)
        unique_words = set(words)

        results[folio] = {
            'zodiac_sign': ZODIAC_FOLIO_MAP.get(folio, 'cosmological'),
            'total_words': len(words),
            'unique_words': len(unique_words),
            'word_list': sorted(unique_words),
            'word_counts': dict(word_counts.most_common())
        }

    return results


def find_zodiac_unique_words(word_folios: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find words that appear ONLY on zodiac pages."""
    zodiac_folios_set = set(ZODIAC_SECTION_FOLIOS)
    core_zodiac_set = set(CORE_ZODIAC_FOLIOS)

    results = {
        'zodiac_section_only': [],  # Only in zodiac section (f67-f73)
        'core_zodiac_only': [],     # Only in core zodiac (f70-f73)
        'zodiac_and_elsewhere': []  # Appears in zodiac AND other sections
    }

    for word, folios in word_folios.items():
        in_zodiac_section = bool(folios & zodiac_folios_set)
        in_core_zodiac = bool(folios & core_zodiac_set)
        only_zodiac = folios.issubset(zodiac_folios_set)
        only_core = folios.issubset(core_zodiac_set)

        if only_zodiac:
            results['zodiac_section_only'].append({
                'word': word,
                'folios': sorted(folios),
                'folio_count': len(folios)
            })
            if only_core:
                results['core_zodiac_only'].append({
                    'word': word,
                    'folios': sorted(folios),
                    'folio_count': len(folios)
                })
        elif in_zodiac_section:
            results['zodiac_and_elsewhere'].append({
                'word': word,
                'zodiac_folios': sorted(folios & zodiac_folios_set),
                'other_folios_count': len(folios - zodiac_folios_set)
            })

    return results


def find_single_folio_words(word_folios: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find words that appear on exactly ONE zodiac folio."""
    results = {}

    for folio in CORE_ZODIAC_FOLIOS:
        single_folio = []
        for word, folios in word_folios.items():
            if folios == {folio}:
                single_folio.append(word)

        if single_folio:
            results[folio] = {
                'zodiac_sign': ZODIAC_FOLIO_MAP.get(folio, 'unknown'),
                'single_folio_words': sorted(single_folio),
                'count': len(single_folio)
            }

    return results


def analyze_potential_labels(single_folio_words: Dict, folio_vocab: Dict) -> Dict:
    """Analyze single-folio words as potential zodiac labels."""
    results = {}

    for folio, data in single_folio_words.items():
        sign = data['zodiac_sign']
        candidates = data['single_folio_words']

        # Prioritize shorter words (labels tend to be short)
        by_length = sorted(candidates, key=len)

        # Find words that appear multiple times on the folio
        folio_counts = folio_vocab.get(folio, {}).get('word_counts', {})
        repeated = [(w, folio_counts.get(w, 0)) for w in candidates if folio_counts.get(w, 0) > 1]
        repeated.sort(key=lambda x: -x[1])

        results[folio] = {
            'zodiac_sign': sign,
            'total_candidates': len(candidates),
            'shortest_words': by_length[:10],
            'repeated_on_folio': repeated[:10],
            'all_candidates': candidates
        }

    return results


def main():
    print("=" * 70)
    print("ZODIAC LABEL EXTRACTION")
    print("Extract potential zodiac label words")
    print("NO SEMANTIC ASSUMPTIONS - distributional analysis only")
    print("=" * 70)
    print()

    # Load corpus
    print("Loading corpus...")
    corpus, folio_words, word_folios = load_corpus()
    print(f"Total word instances: {len(corpus)}")
    print(f"Unique folios: {len(folio_words)}")
    print(f"Unique words: {len(word_folios)}")
    print()

    # Extract zodiac vocabulary
    print("Extracting zodiac section vocabulary...")
    zodiac_vocab = extract_zodiac_vocabulary(folio_words)
    print(f"Zodiac folios with text: {len(zodiac_vocab)}")

    total_zodiac_words = sum(v['total_words'] for v in zodiac_vocab.values())
    print(f"Total words in zodiac section: {total_zodiac_words}")
    print()

    # Show vocabulary per core zodiac folio
    print("--- CORE ZODIAC FOLIO VOCABULARY ---")
    for folio in CORE_ZODIAC_FOLIOS:
        if folio in zodiac_vocab:
            v = zodiac_vocab[folio]
            print(f"{folio} ({v['zodiac_sign']}): {v['total_words']} words, {v['unique_words']} unique")

    print()

    # Find zodiac-unique words
    print("Finding zodiac-unique words...")
    unique_words = find_zodiac_unique_words(word_folios)

    print(f"\n--- ZODIAC-UNIQUE WORDS ---")
    print(f"Words appearing ONLY in zodiac section (f67-f73): {len(unique_words['zodiac_section_only'])}")
    print(f"Words appearing ONLY in core zodiac (f70-f73): {len(unique_words['core_zodiac_only'])}")
    print(f"Words appearing in zodiac AND elsewhere: {len(unique_words['zodiac_and_elsewhere'])}")
    print()

    # Find single-folio words
    print("Finding single-folio words (potential labels)...")
    single_folio = find_single_folio_words(word_folios)

    print(f"\n--- SINGLE-FOLIO WORDS ---")
    for folio, data in single_folio.items():
        print(f"{folio} ({data['zodiac_sign']}): {data['count']} words unique to this folio")

    print()

    # Analyze potential labels
    print("Analyzing potential label candidates...")
    label_candidates = analyze_potential_labels(single_folio, zodiac_vocab)

    print(f"\n--- POTENTIAL LABEL CANDIDATES ---")
    for folio, data in label_candidates.items():
        print(f"\n{folio} ({data['zodiac_sign']}):")
        print(f"  Total single-folio words: {data['total_candidates']}")
        print(f"  Shortest words: {', '.join(data['shortest_words'][:5])}")
        if data['repeated_on_folio']:
            print(f"  Repeated on folio: {data['repeated_on_folio'][:3]}")

    # Compile results
    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Zodiac label extraction - NO SEMANTIC ASSUMPTIONS',
        'zodiac_folio_mapping': ZODIAC_FOLIO_MAP,
        'summary': {
            'total_zodiac_section_folios': len([f for f in ZODIAC_SECTION_FOLIOS if f in zodiac_vocab]),
            'total_core_zodiac_folios': len([f for f in CORE_ZODIAC_FOLIOS if f in zodiac_vocab]),
            'total_words_in_zodiac': total_zodiac_words,
            'zodiac_unique_word_count': len(unique_words['zodiac_section_only']),
            'core_zodiac_unique_count': len(unique_words['core_zodiac_only'])
        },
        'zodiac_vocabulary': zodiac_vocab,
        'zodiac_unique_words': unique_words,
        'single_folio_words': single_folio,
        'label_candidates': label_candidates
    }

    # Save results
    with open('zodiac_unique_words.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to zodiac_unique_words.json")

    # Summary statistics for next step
    print("\n" + "=" * 70)
    print("SUMMARY FOR PHONETIC TESTING")
    print("=" * 70)

    total_candidates = sum(d['total_candidates'] for d in label_candidates.values())
    print(f"\nTotal single-folio words to test: {total_candidates}")

    for folio in CORE_ZODIAC_FOLIOS:
        if folio in label_candidates:
            data = label_candidates[folio]
            print(f"\n{data['zodiac_sign']} ({folio}):")
            candidates = data['all_candidates'][:5]
            for c in candidates:
                print(f"  {c}")


if __name__ == '__main__':
    main()
