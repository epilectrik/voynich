#!/usr/bin/env python3
"""
Phase 17, Task 4: Folio Feature Database

This script creates a database linking text features (from our analysis)
to visual features (placeholder for manual coding). It prepares the
infrastructure for illustration-vocabulary correlation testing.

Output: folio_feature_database.json
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Set
import numpy as np
from scipy import stats

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
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

MIN_ENTRY_WORDS = 9

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
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

def get_prefix(word: str) -> str:
    for length in [3, 2]:
        if len(word) >= length and word[:length] in KNOWN_PREFIXES:
            return word[:length]
    return word[:2] if len(word) >= 2 else word

def get_suffix(word: str) -> str:
    for length in [4, 3, 2]:
        if len(word) >= length and word[-length:] in KNOWN_SUFFIXES:
            return word[-length:]
    return word[-2:] if len(word) >= 2 else word

def segment_into_entries(words: List[Dict]) -> Dict[str, List[Dict]]:
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)
    return dict(by_folio)

# =============================================================================
# TEXT FEATURE EXTRACTION
# =============================================================================

def extract_text_features(entry: List[Dict]) -> Dict:
    """Extract comprehensive text features from a single entry."""

    n = len(entry)
    if n < MIN_ENTRY_WORDS:
        return None

    # Basic statistics
    words = [w['word'] for w in entry]
    unique_words = set(words)

    # Part division
    third = n // 3
    part1 = entry[:third]
    part2 = entry[third:2*third]
    part3 = entry[2*third:]

    # Extract vocabulary by part
    part1_words = [w['word'] for w in part1]
    part2_words = [w['word'] for w in part2]
    part3_words = [w['word'] for w in part3]

    # Prefix distributions
    all_prefixes = [get_prefix(w) for w in words]
    p1_prefixes = [get_prefix(w) for w in part1_words]
    p2_prefixes = [get_prefix(w) for w in part2_words]
    p3_prefixes = [get_prefix(w) for w in part3_words]

    # Suffix distributions
    all_suffixes = [get_suffix(w) for w in words]
    p1_suffixes = [get_suffix(w) for w in part1_words]
    p3_suffixes = [get_suffix(w) for w in part3_words]

    # Opening and closing words
    opening_word = words[0] if words else ''
    closing_word = words[-1] if words else ''

    # Dominant prefixes by part
    p1_dominant = Counter(p1_prefixes).most_common(1)[0][0] if p1_prefixes else ''
    p2_dominant = Counter(p2_prefixes).most_common(1)[0][0] if p2_prefixes else ''
    p3_dominant = Counter(p3_prefixes).most_common(1)[0][0] if p3_prefixes else ''

    # Heading candidates in Part 1
    heading_candidates = []
    word_counts = Counter(words)
    for w in part1_words:
        # Check if this word is concentrated in Part 1
        p1_count = part1_words.count(w)
        total = word_counts[w]
        if total >= 2 and p1_count / total > 0.7:
            if w not in [h['word'] for h in heading_candidates]:
                heading_candidates.append({
                    'word': w,
                    'part1_count': p1_count,
                    'total_count': total
                })

    return {
        'word_count': n,
        'unique_word_count': len(unique_words),
        'vocabulary_richness': round(len(unique_words) / n, 3),

        'part_lengths': {
            'part1': len(part1),
            'part2': len(part2),
            'part3': len(part3)
        },

        'opening_word': opening_word,
        'opening_prefix': get_prefix(opening_word),
        'closing_word': closing_word,
        'closing_suffix': get_suffix(closing_word),

        'dominant_prefixes': {
            'part1': p1_dominant,
            'part2': p2_dominant,
            'part3': p3_dominant
        },

        'prefix_distribution': dict(Counter(all_prefixes).most_common(10)),
        'suffix_distribution': dict(Counter(all_suffixes).most_common(10)),

        'part1_vocabulary': list(set(part1_words))[:20],
        'part2_vocabulary': list(set(part2_words))[:20],
        'part3_vocabulary': list(set(part3_words))[:20],

        'heading_candidates': heading_candidates[:5]
    }

# =============================================================================
# VISUAL FEATURE PLACEHOLDERS
# =============================================================================

def create_visual_feature_placeholder() -> Dict:
    """Create placeholder structure for visual features to be filled manually."""

    return {
        '_coding_status': 'NOT_CODED',
        '_coder_id': None,
        '_coding_date': None,

        'root': {
            'root_present': None,
            'root_type': None,
            'root_prominence': None
        },

        'stem': {
            'stem_count': None,
            'stem_type': None,
            'stem_thickness': None
        },

        'leaf': {
            'leaf_present': None,
            'leaf_count_category': None,
            'leaf_shape': None,
            'leaf_arrangement': None
        },

        'flower': {
            'flower_present': None,
            'flower_count': None,
            'flower_position': None,
            'flower_shape': None
        },

        'overall': {
            'plant_count': None,
            'container_present': None,
            'symmetry': None,
            'complexity': None,
            'artistic_style': None
        }
    }

# =============================================================================
# CORRELATION TEST FRAMEWORK
# =============================================================================

def create_correlation_test_framework() -> Dict:
    """Define statistical tests for text-visual correlation."""

    return {
        'tests_available': {
            'chi_square': {
                'description': 'Test association between categorical text and visual features',
                'example': 'chi_square(prefix_X_present, root_type)',
                'null_hypothesis': 'No association between prefix and visual feature'
            },
            'mutual_information': {
                'description': 'Measure information shared between text and visual features',
                'example': 'MI(part1_vocabulary, leaf_shape)',
                'interpretation': 'Higher MI = stronger association'
            },
            'jaccard_similarity': {
                'description': 'Compare vocabulary overlap between visual categories',
                'example': 'jaccard(vocab_of_bulbous_roots, vocab_of_tuberous_roots)',
                'interpretation': 'Low Jaccard = distinct vocabularies'
            }
        },

        'hypotheses_to_test': [
            {
                'hypothesis': 'Root type predicts Part 1 vocabulary',
                'text_feature': 'part1_vocabulary',
                'visual_feature': 'root_type',
                'test': 'chi_square'
            },
            {
                'hypothesis': 'Flower presence predicts Part 3 vocabulary',
                'text_feature': 'part3_dominant_prefix',
                'visual_feature': 'flower_present',
                'test': 'chi_square'
            },
            {
                'hypothesis': 'Plant complexity correlates with entry length',
                'text_feature': 'word_count',
                'visual_feature': 'complexity',
                'test': 'correlation'
            },
            {
                'hypothesis': 'Leaf shape categories have distinct heading words',
                'text_feature': 'heading_candidates',
                'visual_feature': 'leaf_shape',
                'test': 'jaccard_similarity'
            }
        ],

        'required_sample_size': {
            'chi_square': 'N >= 20 per category for reliable results',
            'correlation': 'N >= 30 for statistical power',
            'mutual_information': 'N >= 50 recommended'
        }
    }

# =============================================================================
# DATABASE CREATION
# =============================================================================

def create_folio_database(currier: str = 'A') -> Dict:
    """Create comprehensive folio-level feature database."""

    print(f"Loading corpus...")
    all_words = load_corpus()
    corpus = [w for w in all_words if w['currier'] == currier]
    print(f"  {len(corpus)} words in Currier {currier}")

    print(f"Segmenting into entries...")
    entries = segment_into_entries(corpus)
    valid_entries = {f: e for f, e in entries.items() if len(e) >= MIN_ENTRY_WORDS}
    print(f"  {len(valid_entries)} valid entries")

    print(f"Extracting features for each folio...")
    database = {}

    for folio, entry in sorted(valid_entries.items()):
        text_features = extract_text_features(entry)
        if text_features is None:
            continue

        database[folio] = {
            'folio_id': folio,
            'currier': currier,
            'section': entry[0].get('section', '') if entry else '',

            'text_features': text_features,
            'visual_features': create_visual_feature_placeholder(),

            'correlation_ready': False,  # Set to True when visual features coded
            'notes': ''
        }

    return database

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 17, Task 4: Folio Feature Database")
    print("=" * 70)

    # Create database for Currier A
    print("\n[1/3] Creating Currier A database...")
    a_database = create_folio_database('A')

    # Create database for Currier B
    print("\n[2/3] Creating Currier B database...")
    b_database = create_folio_database('B')

    # Create correlation test framework
    print("\n[3/3] Creating correlation test framework...")
    test_framework = create_correlation_test_framework()

    # Compile full database
    full_database = {
        'metadata': {
            'title': 'Voynich Manuscript Folio Feature Database',
            'version': '1.0',
            'date': datetime.now().isoformat(),
            'purpose': 'Link text features to visual features for correlation analysis',
            'status': 'TEXT_FEATURES_COMPLETE, VISUAL_FEATURES_PENDING'
        },

        'statistics': {
            'currier_a_folios': len(a_database),
            'currier_b_folios': len(b_database),
            'total_folios': len(a_database) + len(b_database),
            'visual_coding_complete': 0,
            'correlation_ready': 0
        },

        'currier_a': a_database,
        'currier_b': b_database,

        'correlation_test_framework': test_framework,

        'usage_instructions': {
            'to_add_visual_coding': [
                '1. Open folio_feature_database.json',
                '2. Navigate to currier_a > [folio_id] > visual_features',
                '3. Fill in feature values according to visual_feature_schema.json',
                '4. Set _coding_status to CODED',
                '5. Set _coder_id and _coding_date',
                '6. Set correlation_ready to true'
            ],
            'to_run_correlation': [
                '1. Ensure visual features coded for target folios',
                '2. Use test_framework hypotheses',
                '3. Extract feature pairs, run statistical test',
                '4. Report significant correlations'
            ]
        }
    }

    # Save database
    output_file = 'folio_feature_database.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_database, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'=' * 70}")
    print(f"Database created:")
    print(f"  Currier A folios: {len(a_database)}")
    print(f"  Currier B folios: {len(b_database)}")
    print(f"  Total: {len(a_database) + len(b_database)}")
    print(f"\nSaved to: {output_file}")
    print(f"{'=' * 70}")

    # Print sample entry
    print("\nSample entry (first Currier A folio):")
    sample_folio = list(a_database.keys())[0]
    sample = a_database[sample_folio]
    print(f"  Folio: {sample['folio_id']}")
    print(f"  Word count: {sample['text_features']['word_count']}")
    print(f"  Opening word: {sample['text_features']['opening_word']}")
    print(f"  Heading candidates: {[h['word'] for h in sample['text_features']['heading_candidates']]}")
    print(f"  Visual coding status: {sample['visual_features']['_coding_status']}")

    return full_database

if __name__ == '__main__':
    main()
