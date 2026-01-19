#!/usr/bin/env python3
"""
Phase 17, Task 6: Cross-Reference Detection (A<->B)

This script analyzes whether Currier B entries reference Currier A entries,
testing for directional asymmetry and vocabulary correlations.

Output: cross_reference_detection_report.json
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Set, Tuple
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
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
            # CRITICAL: Filter to H-only transcriber track
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

def get_prefix(word: str) -> str:
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return word[:2] if len(word) >= 2 else word

def segment_into_entries(words: List[Dict]) -> Dict[str, List[Dict]]:
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)
    return dict(by_folio)

def get_entry_parts(entry: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    n = len(entry)
    third = n // 3
    return entry[:third], entry[third:2*third], entry[2*third:]

# =============================================================================
# SHARED VOCABULARY ANALYSIS
# =============================================================================

def analyze_shared_vocabulary(a_words: List[Dict], b_words: List[Dict],
                             a_entries: Dict, b_entries: Dict) -> Dict:
    """Analyze vocabulary shared between A and B."""

    # Get vocabularies
    a_vocab = set(w['word'] for w in a_words)
    b_vocab = set(w['word'] for w in b_words)
    shared_vocab = a_vocab & b_vocab
    only_a = a_vocab - b_vocab
    only_b = b_vocab - a_vocab

    # For shared words, analyze distribution by part
    shared_analysis = []

    for word in list(shared_vocab)[:100]:  # Analyze top 100
        # Count in A by part
        a_part1, a_part2, a_part3 = 0, 0, 0
        for folio, entry in a_entries.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue
            p1, p2, p3 = get_entry_parts(entry)
            a_part1 += sum(1 for w in p1 if w['word'] == word)
            a_part2 += sum(1 for w in p2 if w['word'] == word)
            a_part3 += sum(1 for w in p3 if w['word'] == word)

        # Count in B by part
        b_part1, b_part2, b_part3 = 0, 0, 0
        for folio, entry in b_entries.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue
            p1, p2, p3 = get_entry_parts(entry)
            b_part1 += sum(1 for w in p1 if w['word'] == word)
            b_part2 += sum(1 for w in p2 if w['word'] == word)
            b_part3 += sum(1 for w in p3 if w['word'] == word)

        a_total = a_part1 + a_part2 + a_part3
        b_total = b_part1 + b_part2 + b_part3

        if a_total > 0 and b_total > 0:
            shared_analysis.append({
                'word': word,
                'a_total': a_total,
                'b_total': b_total,
                'a_part1_frac': round(a_part1 / a_total, 3) if a_total else 0,
                'b_part1_frac': round(b_part1 / b_total, 3) if b_total else 0,
                'a_in_part1': a_part1 > a_part2 and a_part1 > a_part3,
                'b_in_body': b_part2 + b_part3 > b_part1
            })

    # Find words that are A-heading but B-body
    a_heading_b_body = [
        s for s in shared_analysis
        if s['a_part1_frac'] > 0.6 and s['b_part1_frac'] < 0.4
    ]

    return {
        'total_shared': len(shared_vocab),
        'only_in_a': len(only_a),
        'only_in_b': len(only_b),
        'overlap_jaccard': round(len(shared_vocab) / len(a_vocab | b_vocab), 4),
        'a_heading_appears_in_b_body': {
            'count': len(a_heading_b_body),
            'examples': a_heading_b_body[:20]
        },
        'shared_word_sample': shared_analysis[:30]
    }

# =============================================================================
# HEADING WORDS IN B
# =============================================================================

def analyze_heading_words_in_b(a_entries: Dict, b_entries: Dict) -> Dict:
    """Check if A heading candidates appear in B."""

    # Get A heading candidates (>70% in Part 1)
    a_part1_words = Counter()
    a_total_words = Counter()

    for folio, entry in a_entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue
        p1, p2, p3 = get_entry_parts(entry)
        for w in p1:
            a_part1_words[w['word']] += 1
            a_total_words[w['word']] += 1
        for w in p2 + p3:
            a_total_words[w['word']] += 1

    a_heading_candidates = {
        word for word, total in a_total_words.items()
        if total >= 3 and a_part1_words[word] / total > 0.7
    }

    # Check where these appear in B
    heading_in_b = {}

    for heading in a_heading_candidates:
        b_part1, b_part2, b_part3 = 0, 0, 0
        b_folios = set()

        for folio, entry in b_entries.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue
            p1, p2, p3 = get_entry_parts(entry)

            for w in p1:
                if w['word'] == heading:
                    b_part1 += 1
                    b_folios.add(folio)
            for w in p2:
                if w['word'] == heading:
                    b_part2 += 1
                    b_folios.add(folio)
            for w in p3:
                if w['word'] == heading:
                    b_part3 += 1
                    b_folios.add(folio)

        if b_part1 + b_part2 + b_part3 > 0:
            total_in_b = b_part1 + b_part2 + b_part3
            heading_in_b[heading] = {
                'total_in_b': total_in_b,
                'b_part1': b_part1,
                'b_part2': b_part2,
                'b_part3': b_part3,
                'b_body_fraction': round((b_part2 + b_part3) / total_in_b, 3),
                'appears_in_b_body': b_part2 + b_part3 > b_part1,
                'b_folios': len(b_folios)
            }

    # Count cross-references
    cross_ref_candidates = [
        h for h, info in heading_in_b.items()
        if info['appears_in_b_body']
    ]

    return {
        'a_heading_candidates': len(a_heading_candidates),
        'appear_in_b': len(heading_in_b),
        'appear_in_b_body': len(cross_ref_candidates),
        'cross_reference_rate': round(len(cross_ref_candidates) / len(a_heading_candidates), 3)
            if a_heading_candidates else 0,
        'details': heading_in_b,
        'cross_reference_candidates': cross_ref_candidates
    }

# =============================================================================
# DIRECTIONAL ASYMMETRY TEST
# =============================================================================

def test_directional_asymmetry(a_entries: Dict, b_entries: Dict,
                               a_words: List[Dict], b_words: List[Dict]) -> Dict:
    """Test if B references A (directional asymmetry)."""

    # Get A Part 1 vocabulary
    a_part1_vocab = set()
    a_body_vocab = set()
    for folio, entry in a_entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue
        p1, p2, p3 = get_entry_parts(entry)
        for w in p1:
            a_part1_vocab.add(w['word'])
        for w in p2 + p3:
            a_body_vocab.add(w['word'])

    # Get B Part 1 vocabulary
    b_part1_vocab = set()
    b_body_vocab = set()
    for folio, entry in b_entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue
        p1, p2, p3 = get_entry_parts(entry)
        for w in p1:
            b_part1_vocab.add(w['word'])
        for w in p2 + p3:
            b_body_vocab.add(w['word'])

    # Get corpus-level only-A and only-B vocabulary
    a_vocab = set(w['word'] for w in a_words)
    b_vocab = set(w['word'] for w in b_words)
    only_a = a_vocab - b_vocab
    only_b = b_vocab - a_vocab

    # Test 1: A heading words appearing in B body
    a_headings_in_b_body = a_part1_vocab & b_body_vocab
    a_headings_in_b_body_only = a_headings_in_b_body - b_part1_vocab  # In B body but NOT B Part 1

    # Test 2: B-only words appearing in A Part 1
    b_only_in_a_part1 = only_b & a_part1_vocab

    # Test 3: A-only words appearing in B body
    a_only_in_b_body = only_a & b_body_vocab

    # Directional asymmetry ratio
    # If B references A: a_headings_in_b_body should be HIGH, b_only_in_a_part1 should be LOW
    asymmetry_ratio = (len(a_headings_in_b_body) / len(b_only_in_a_part1)
                      if b_only_in_a_part1 else float('inf'))

    return {
        'a_part1_vocab_size': len(a_part1_vocab),
        'b_body_vocab_size': len(b_body_vocab),
        'a_headings_in_b_body': {
            'count': len(a_headings_in_b_body),
            'exclusive_to_b_body': len(a_headings_in_b_body_only),
            'examples': list(a_headings_in_b_body)[:20]
        },
        'b_only_in_a_part1': {
            'count': len(b_only_in_a_part1),
            'examples': list(b_only_in_a_part1)[:20]
        },
        'a_only_in_b_body': {
            'count': len(a_only_in_b_body),
            'examples': list(a_only_in_b_body)[:20]
        },
        'asymmetry_ratio': round(asymmetry_ratio, 2) if asymmetry_ratio != float('inf') else 'INF',
        'interpretation': {
            'direction': 'B_REFERENCES_A' if asymmetry_ratio > 2 else
                        'A_REFERENCES_B' if asymmetry_ratio < 0.5 else
                        'BIDIRECTIONAL_OR_NONE',
            'evidence': f"A headings appear in B body {len(a_headings_in_b_body)} times, " +
                       f"B-only words in A Part 1: {len(b_only_in_a_part1)}"
        }
    }

# =============================================================================
# ENTRY-LEVEL CORRELATION
# =============================================================================

def compute_entry_correlations(a_entries: Dict, b_entries: Dict) -> Dict:
    """Compute vocabulary overlap between each B entry and all A entries."""

    # Get vocabulary for each A entry
    a_entry_vocabs = {}
    for folio, entry in a_entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue
        a_entry_vocabs[folio] = set(w['word'] for w in entry)

    # For each B entry, find most similar A entries
    b_to_a_correlations = []

    for b_folio, b_entry in b_entries.items():
        if len(b_entry) < MIN_ENTRY_WORDS:
            continue

        b_vocab = set(w['word'] for w in b_entry)

        # Calculate Jaccard with each A entry
        similarities = []
        for a_folio, a_vocab in a_entry_vocabs.items():
            intersection = len(a_vocab & b_vocab)
            union = len(a_vocab | b_vocab)
            jaccard = intersection / union if union > 0 else 0
            if intersection > 2:  # Minimum overlap
                similarities.append({
                    'a_folio': a_folio,
                    'jaccard': round(jaccard, 4),
                    'shared_words': intersection,
                    'shared_examples': list(a_vocab & b_vocab)[:10]
                })

        similarities.sort(key=lambda x: x['jaccard'], reverse=True)

        if similarities:
            b_to_a_correlations.append({
                'b_folio': b_folio,
                'b_word_count': len(b_entry),
                'top_a_matches': similarities[:5],
                'max_jaccard': similarities[0]['jaccard'] if similarities else 0
            })

    # Sort by max correlation
    b_to_a_correlations.sort(key=lambda x: x['max_jaccard'], reverse=True)

    # Statistics
    max_jaccards = [c['max_jaccard'] for c in b_to_a_correlations if c['max_jaccard'] > 0]

    return {
        'b_entries_analyzed': len(b_to_a_correlations),
        'entries_with_correlation': len([c for c in b_to_a_correlations if c['max_jaccard'] > 0.05]),
        'mean_max_jaccard': round(np.mean(max_jaccards), 4) if max_jaccards else 0,
        'max_jaccard_found': max(max_jaccards) if max_jaccards else 0,
        'top_correlations': b_to_a_correlations[:20],
        'interpretation': 'SOME_CORRELATION' if np.mean(max_jaccards) > 0.03 else 'WEAK_CORRELATION'
            if max_jaccards else 'NO_CORRELATION'
    }

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_analysis():
    """Run cross-reference detection analysis."""
    print("=" * 70)
    print("Phase 17, Task 6: Cross-Reference Detection (A<->B)")
    print("=" * 70)

    # Load data
    print("\n[1/6] Loading corpus...")
    all_words = load_corpus()
    currier_a = [w for w in all_words if w['currier'] == 'A']
    currier_b = [w for w in all_words if w['currier'] == 'B']
    print(f"  Currier A: {len(currier_a)} words")
    print(f"  Currier B: {len(currier_b)} words")

    # Segment into entries
    print("\n[2/6] Segmenting into entries...")
    a_entries = segment_into_entries(currier_a)
    b_entries = segment_into_entries(currier_b)

    valid_a = {f: e for f, e in a_entries.items() if len(e) >= MIN_ENTRY_WORDS}
    valid_b = {f: e for f, e in b_entries.items() if len(e) >= MIN_ENTRY_WORDS}
    print(f"  Currier A: {len(valid_a)} valid entries")
    print(f"  Currier B: {len(valid_b)} valid entries")

    # Shared vocabulary analysis
    print("\n[3/6] Analyzing shared vocabulary...")
    shared_vocab = analyze_shared_vocabulary(currier_a, currier_b, valid_a, valid_b)
    print(f"  Shared vocabulary: {shared_vocab['total_shared']} words")
    print(f"  Overlap Jaccard: {shared_vocab['overlap_jaccard']}")
    print(f"  A-heading in B-body: {shared_vocab['a_heading_appears_in_b_body']['count']}")

    # Heading words in B
    print("\n[4/6] Checking heading words in B...")
    heading_in_b = analyze_heading_words_in_b(valid_a, valid_b)
    print(f"  A heading candidates: {heading_in_b['a_heading_candidates']}")
    print(f"  Appear in B: {heading_in_b['appear_in_b']}")
    print(f"  Appear in B body: {heading_in_b['appear_in_b_body']}")

    # Directional asymmetry test
    print("\n[5/6] Testing directional asymmetry...")
    asymmetry = test_directional_asymmetry(valid_a, valid_b, currier_a, currier_b)
    print(f"  A headings in B body: {asymmetry['a_headings_in_b_body']['count']}")
    print(f"  B-only in A Part 1: {asymmetry['b_only_in_a_part1']['count']}")
    print(f"  Asymmetry ratio: {asymmetry['asymmetry_ratio']}")
    print(f"  Direction: {asymmetry['interpretation']['direction']}")

    # Entry-level correlations
    print("\n[6/6] Computing entry-level correlations...")
    correlations = compute_entry_correlations(valid_a, valid_b)
    print(f"  Entries with correlation: {correlations['entries_with_correlation']}")
    print(f"  Mean max Jaccard: {correlations['mean_max_jaccard']}")
    print(f"  Max Jaccard found: {correlations['max_jaccard_found']}")

    # Compile results
    results = {
        'metadata': {
            'analysis': 'Phase 17 Task 6: Cross-Reference Detection',
            'timestamp': datetime.now().isoformat(),
            'currier_a_entries': len(valid_a),
            'currier_b_entries': len(valid_b)
        },
        'shared_vocabulary_analysis': shared_vocab,
        'heading_words_in_b': heading_in_b,
        'directional_asymmetry': asymmetry,
        'entry_level_correlations': correlations,
        'summary': {
            'key_findings': [
                f"Shared vocabulary: {shared_vocab['total_shared']} words (Jaccard: {shared_vocab['overlap_jaccard']})",
                f"{heading_in_b['appear_in_b_body']} A heading words appear in B body (cross-references?)",
                f"Directional asymmetry: {asymmetry['interpretation']['direction']}",
                f"Asymmetry ratio: {asymmetry['asymmetry_ratio']}",
                f"Entry correlation: {correlations['interpretation']} (mean Jaccard: {correlations['mean_max_jaccard']})",
                f"Max entry-entry Jaccard: {correlations['max_jaccard_found']}"
            ],
            'cross_reference_evidence': {
                'a_headings_in_b_body': heading_in_b['appear_in_b_body'],
                'cross_reference_rate': heading_in_b['cross_reference_rate'],
                'direction': asymmetry['interpretation']['direction']
            },
            'constraints_for_decipherment': [
                f"A and B share {shared_vocab['total_shared']} words ({shared_vocab['overlap_jaccard']:.1%} Jaccard)",
                f"Cross-reference direction: {asymmetry['interpretation']['direction']}",
                f"Entry-level correlation: {correlations['interpretation']}",
                f"{heading_in_b['appear_in_b_body']} A heading words found in B body text"
            ]
        }
    }

    # Save results
    output_file = 'cross_reference_detection_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'=' * 70}")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 70}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY: Cross-Reference Detection")
    print("=" * 70)
    for finding in results['summary']['key_findings']:
        print(f"  - {finding}")

    return results

if __name__ == '__main__':
    run_analysis()
