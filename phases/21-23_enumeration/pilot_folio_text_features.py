#!/usr/bin/env python3
"""
Phase 18, Task 2: Pilot Folio Text Feature Extraction

Extracts comprehensive text features for the 30 pilot folios selected for
the visual correlation study. Includes cross-reference analysis with Currier B.

Output: pilot_folio_text_features.json
"""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Set, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'pa', 'py', 'ky', 'ty', 'fa', 'fs', 'ks', 'r*'
]

KNOWN_SUFFIXES = [
    'aiin', 'ain', 'iin', 'in',
    'eedy', 'edy', 'dy',
    'eey', 'ey', 'hy', 'y',
    'ar', 'or', 'ir', 'er',
    'al', 'ol', 'el', 'il',
    'am', 'an', 'en', 'on',
    's', 'm', 'n', 'l', 'r', 'd'
]

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
    """Load the full corpus."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to H (PRIMARY) transcriber track only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')
            section = row.get('section', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'section': section
                })

    return words


def load_pilot_selection() -> List[str]:
    """Load the pilot folio selection."""
    with open('pilot_folio_selection.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['pilot_study_folios']


def load_folio_database() -> Dict:
    """Load the existing folio feature database."""
    with open('folio_feature_database.json', 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# FEATURE EXTRACTION HELPERS
# =============================================================================

def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length and word[:length] in KNOWN_PREFIXES:
            return word[:length]
    return word[:2] if len(word) >= 2 else word


def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    for length in [4, 3, 2, 1]:
        if len(word) >= length and word[-length:] in KNOWN_SUFFIXES:
            return word[-length:]
    return word[-2:] if len(word) >= 2 else word


def segment_entry(words: List[Dict]) -> Dict[str, List[Dict]]:
    """Segment entry into three parts."""
    n = len(words)
    third = n // 3
    return {
        'part1': words[:third],
        'part2': words[third:2*third],
        'part3': words[2*third:]
    }


# =============================================================================
# MAIN FEATURE EXTRACTION
# =============================================================================

def extract_basic_metrics(entry_words: List[str]) -> Dict:
    """Extract basic text metrics."""
    n = len(entry_words)
    unique = set(entry_words)
    return {
        'word_count': n,
        'unique_word_count': len(unique),
        'vocabulary_richness': round(len(unique) / n, 4) if n > 0 else 0
    }


def extract_part_features(parts: Dict[str, List[Dict]]) -> Dict:
    """Extract features for each part."""
    result = {}

    for part_name, part_words in parts.items():
        words = [w['word'] for w in part_words]
        prefixes = [get_prefix(w) for w in words]

        prefix_counter = Counter(prefixes)
        dominant_prefix = prefix_counter.most_common(1)[0][0] if prefix_counter else ''

        result[f'{part_name}_word_count'] = len(words)
        result[f'{part_name}_vocabulary'] = list(set(words))[:30]  # Top 30 unique
        result[f'{part_name}_dominant_prefix'] = dominant_prefix

    return result


def extract_heading_features(entry_words: List[str], folio_id: str,
                              all_a_entries: Dict, all_b_entries: Dict) -> Dict:
    """Extract features about the heading word."""
    if not entry_words:
        return {
            'heading_word': '',
            'heading_prefix': '',
            'heading_suffix': '',
            'heading_length': 0,
            'heading_unique_to_folio': True,
            'heading_in_b': False,
            'heading_b_entry_count': 0,
            'heading_b_folios': []
        }

    heading = entry_words[0]

    # Check if heading is unique to this folio in A
    heading_folios_in_a = []
    for other_folio, words in all_a_entries.items():
        if heading in [w['word'] for w in words]:
            heading_folios_in_a.append(other_folio)

    unique_to_folio = len(heading_folios_in_a) == 1 and heading_folios_in_a[0] == folio_id

    # Check if heading appears in B entries
    b_folios_with_heading = []
    for b_folio, words in all_b_entries.items():
        if heading in [w['word'] for w in words]:
            b_folios_with_heading.append(b_folio)

    return {
        'heading_word': heading,
        'heading_prefix': get_prefix(heading),
        'heading_suffix': get_suffix(heading),
        'heading_length': len(heading),
        'heading_unique_to_folio': unique_to_folio,
        'heading_a_folios': heading_folios_in_a,
        'heading_in_b': len(b_folios_with_heading) > 0,
        'heading_b_entry_count': len(b_folios_with_heading),
        'heading_b_folios': b_folios_with_heading
    }


def extract_affix_distribution(entry_words: List[str]) -> Dict:
    """Extract prefix and suffix distributions."""
    prefixes = [get_prefix(w) for w in entry_words]
    suffixes = [get_suffix(w) for w in entry_words]

    prefix_counts = dict(Counter(prefixes))
    suffix_counts = dict(Counter(suffixes))

    top_prefixes = [p for p, c in Counter(prefixes).most_common(3)]
    top_suffixes = [s for s, c in Counter(suffixes).most_common(3)]

    return {
        'prefix_counts': prefix_counts,
        'prefix_diversity': len(set(prefixes)),
        'top_3_prefixes': top_prefixes,
        'suffix_counts': suffix_counts,
        'suffix_diversity': len(set(suffixes)),
        'top_3_suffixes': top_suffixes
    }


def extract_cross_reference_features(folio_id: str, entry_words: List[str],
                                      parts: Dict, all_b_entries: Dict) -> Dict:
    """Extract cross-reference features with B entries."""
    # Get Part 1 vocabulary (headings/identifiers)
    part1_vocab = set(w['word'] for w in parts['part1'])

    # Count how many Part 1 words appear in B
    part1_in_b = {}
    for word in part1_vocab:
        b_appearances = []
        for b_folio, b_words in all_b_entries.items():
            b_word_list = [w['word'] for w in b_words]
            if word in b_word_list:
                b_appearances.append(b_folio)
        if b_appearances:
            part1_in_b[word] = b_appearances

    # Identify cross-reference candidates
    cross_ref_candidates = []
    for word, b_folios in part1_in_b.items():
        if len(b_folios) >= 1:
            cross_ref_candidates.append({
                'word': word,
                'b_entry_count': len(b_folios),
                'b_folios': b_folios[:5]  # First 5
            })

    return {
        'part1_words_in_b': len(part1_in_b),
        'cross_reference_candidates': cross_ref_candidates[:10]  # Top 10
    }


def extract_all_features_for_folio(folio_id: str, entry: List[Dict],
                                   all_a_entries: Dict,
                                   all_b_entries: Dict,
                                   existing_features: Dict) -> Dict:
    """Extract all features for a single pilot folio."""

    entry_words = [w['word'] for w in entry]
    parts = segment_entry(entry)

    # Basic metrics
    basic = extract_basic_metrics(entry_words)

    # Part-level features
    part_features = extract_part_features(parts)

    # Heading analysis
    heading = extract_heading_features(entry_words, folio_id, all_a_entries, all_b_entries)

    # Affix distribution
    affix = extract_affix_distribution(entry_words)

    # Cross-reference features
    cross_ref = extract_cross_reference_features(folio_id, entry_words, parts, all_b_entries)

    # Combine with existing features from database
    existing = existing_features.get('text_features', {})

    return {
        'folio_id': folio_id,

        # Basic metrics
        'word_count': basic['word_count'],
        'unique_word_count': basic['unique_word_count'],
        'vocabulary_richness': basic['vocabulary_richness'],

        # Part-level features
        'part1_word_count': part_features['part1_word_count'],
        'part1_vocabulary': part_features['part1_vocabulary'],
        'part1_dominant_prefix': part_features['part1_dominant_prefix'],
        'part2_word_count': part_features['part2_word_count'],
        'part2_vocabulary': part_features['part2_vocabulary'],
        'part2_dominant_prefix': part_features['part2_dominant_prefix'],
        'part3_word_count': part_features['part3_word_count'],
        'part3_vocabulary': part_features['part3_vocabulary'],
        'part3_dominant_prefix': part_features['part3_dominant_prefix'],

        # Heading analysis
        'heading_word': heading['heading_word'],
        'heading_prefix': heading['heading_prefix'],
        'heading_suffix': heading['heading_suffix'],
        'heading_length': heading['heading_length'],
        'heading_unique_to_folio': heading['heading_unique_to_folio'],
        'heading_a_folios': heading['heading_a_folios'],
        'heading_in_b': heading['heading_in_b'],
        'heading_b_entry_count': heading['heading_b_entry_count'],
        'heading_b_folios': heading['heading_b_folios'],

        # Affix distribution
        'prefix_counts': affix['prefix_counts'],
        'prefix_diversity': affix['prefix_diversity'],
        'top_3_prefixes': affix['top_3_prefixes'],
        'suffix_counts': affix['suffix_counts'],
        'suffix_diversity': affix['suffix_diversity'],
        'top_3_suffixes': affix['top_3_suffixes'],

        # Cross-reference features
        'part1_words_in_b': cross_ref['part1_words_in_b'],
        'cross_reference_candidates': cross_ref['cross_reference_candidates'],

        # From existing database
        'opening_word': existing.get('opening_word', ''),
        'closing_word': existing.get('closing_word', ''),
        'section': existing_features.get('section', 'H')
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 18, Task 2: Pilot Folio Text Feature Extraction")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading corpus...")
    corpus = load_corpus()
    print(f"  Loaded {len(corpus)} word tokens")

    print("\n[2/5] Loading pilot folio selection...")
    pilot_folios = load_pilot_selection()
    print(f"  Selected {len(pilot_folios)} pilot folios")

    print("\n[3/5] Loading folio database...")
    db = load_folio_database()

    # Segment corpus by folio and currier
    print("\n[4/5] Segmenting corpus...")
    a_entries = defaultdict(list)
    b_entries = defaultdict(list)

    for w in corpus:
        if w['currier'] == 'A':
            a_entries[w['folio']].append(w)
        elif w['currier'] == 'B':
            b_entries[w['folio']].append(w)

    print(f"  Currier A: {len(a_entries)} entries")
    print(f"  Currier B: {len(b_entries)} entries")

    # Extract features for each pilot folio
    print("\n[5/5] Extracting features for pilot folios...")
    pilot_features = {}

    for folio_id in pilot_folios:
        if folio_id not in a_entries:
            print(f"  WARNING: {folio_id} not found in corpus")
            continue

        entry = a_entries[folio_id]
        existing = db['currier_a'].get(folio_id, {})

        features = extract_all_features_for_folio(
            folio_id, entry, dict(a_entries), dict(b_entries), existing
        )
        pilot_features[folio_id] = features

        # Progress indicator
        headings_in_b = "YES" if features['heading_in_b'] else "NO"
        print(f"  {folio_id}: {features['word_count']} words, "
              f"heading='{features['heading_word']}', in_B={headings_in_b}")

    # Compile output
    output = {
        'metadata': {
            'title': 'Pilot Folio Text Features for Visual Correlation Study',
            'phase': 'Phase 18, Task 2',
            'date': datetime.now().isoformat(),
            'folio_count': len(pilot_features),
            'purpose': 'Text features for visual-text correlation analysis'
        },

        'summary_statistics': {
            'total_pilot_folios': len(pilot_features),
            'headings_unique_to_folio': sum(1 for f in pilot_features.values()
                                            if f['heading_unique_to_folio']),
            'headings_appearing_in_b': sum(1 for f in pilot_features.values()
                                           if f['heading_in_b']),
            'mean_word_count': round(sum(f['word_count'] for f in pilot_features.values())
                                     / len(pilot_features), 1),
            'mean_prefix_diversity': round(sum(f['prefix_diversity'] for f in pilot_features.values())
                                           / len(pilot_features), 1)
        },

        'pilot_folios': pilot_features
    }

    # Save
    output_file = 'pilot_folio_text_features.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Pilot folios processed: {len(pilot_features)}")
    print(f"  Headings unique to folio: {output['summary_statistics']['headings_unique_to_folio']}")
    print(f"  Headings appearing in B: {output['summary_statistics']['headings_appearing_in_b']}")
    print(f"  Mean word count: {output['summary_statistics']['mean_word_count']}")
    print(f"  Mean prefix diversity: {output['summary_statistics']['mean_prefix_diversity']}")
    print(f"\nSaved to: {output_file}")

    return pilot_features


if __name__ == '__main__':
    main()
