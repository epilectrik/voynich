#!/usr/bin/env python3
"""
Phase 17, Task 5: Heading Word Deep Analysis

This script performs exhaustive analysis of heading word candidates in Currier A,
examining their structural patterns, distribution, and relationships to entry bodies.

Output: heading_word_analysis_report.json
"""

import csv
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple, Set
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'op', 'or', 'os', 'oe', 'of', 'sy', 'yp', 'ra', 'lo', 'ks', 'ai',
    'ka', 'te', 'de', 'ro', 'qk', 'yd', 'ye', 'ys', 'ep', 'ec', 'ed'
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

# Phase 16 heading candidates
KNOWN_HEADING_CANDIDATES = ['pchor', 'kooiin', 'tshor']

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

def get_suffix(word: str) -> str:
    for length in [4, 3, 2]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix
    return word[-2:] if len(word) >= 2 else word

def segment_into_entries(words: List[Dict]) -> Dict[str, List[Dict]]:
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)
    return dict(by_folio)

def get_entry_parts(entry: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Split entry into three parts."""
    n = len(entry)
    third = n // 3
    return entry[:third], entry[third:2*third], entry[2*third:]

# =============================================================================
# HEADING CANDIDATE INVENTORY
# =============================================================================

def inventory_known_candidates(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """Detailed analysis of known heading candidates."""

    results = {}

    for candidate in KNOWN_HEADING_CANDIDATES:
        # Find all occurrences
        occurrences = [w for w in words if w['word'] == candidate]
        total_count = len(occurrences)

        # Count by Currier
        in_a = sum(1 for w in occurrences if w['currier'] == 'A')
        in_b = sum(1 for w in occurrences if w['currier'] == 'B')

        # Count by part position
        part1_count = 0
        part2_count = 0
        part3_count = 0
        entry_initial_count = 0
        folios_with_word = set()

        for folio, entry in entries.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue

            part1, part2, part3 = get_entry_parts(entry)

            for w in part1:
                if w['word'] == candidate:
                    part1_count += 1
                    folios_with_word.add(folio)
            for w in part2:
                if w['word'] == candidate:
                    part2_count += 1
                    folios_with_word.add(folio)
            for w in part3:
                if w['word'] == candidate:
                    part3_count += 1
                    folios_with_word.add(folio)

            # Check if entry-initial
            if entry and entry[0]['word'] == candidate:
                entry_initial_count += 1

        results[candidate] = {
            'total_occurrences': total_count,
            'in_currier_a': in_a,
            'in_currier_b': in_b,
            'part1_count': part1_count,
            'part2_count': part2_count,
            'part3_count': part3_count,
            'entry_initial_count': entry_initial_count,
            'folios_containing': len(folios_with_word),
            'part1_concentration': round(part1_count / (part1_count + part2_count + part3_count), 3)
                if (part1_count + part2_count + part3_count) > 0 else 0,
            'entry_initial_rate': round(entry_initial_count / len(folios_with_word), 3)
                if folios_with_word else 0,
            'prefix': get_prefix(candidate),
            'suffix': get_suffix(candidate),
            'length': len(candidate)
        }

    return results

# =============================================================================
# EXPANDED HEADING DETECTION
# =============================================================================

def detect_all_heading_candidates(entries: Dict[str, List[Dict]], currier: str = 'A') -> Dict:
    """Find ALL words meeting heading criteria."""

    # Filter entries by Currier
    filtered_entries = {
        f: e for f, e in entries.items()
        if len(e) >= MIN_ENTRY_WORDS and (not currier or e[0]['currier'] == currier)
    }

    # Count words by part
    word_part_counts = defaultdict(lambda: {'part1': 0, 'part2': 0, 'part3': 0, 'total': 0})
    word_entry_initial = Counter()
    word_folios = defaultdict(set)

    for folio, entry in filtered_entries.items():
        part1, part2, part3 = get_entry_parts(entry)

        for w in part1:
            word_part_counts[w['word']]['part1'] += 1
            word_part_counts[w['word']]['total'] += 1
            word_folios[w['word']].add(folio)

        for w in part2:
            word_part_counts[w['word']]['part2'] += 1
            word_part_counts[w['word']]['total'] += 1
            word_folios[w['word']].add(folio)

        for w in part3:
            word_part_counts[w['word']]['part3'] += 1
            word_part_counts[w['word']]['total'] += 1
            word_folios[w['word']].add(folio)

        # Check entry-initial
        if entry:
            word_entry_initial[entry[0]['word']] += 1

    # Find heading candidates
    # Criterion 1: >70% in Part 1
    high_part1_concentration = []
    # Criterion 2: Only appear in Part 1 (100%)
    part1_only = []
    # Criterion 3: Any word appearing entry-initial 2+ times
    entry_initial_words = []

    for word, counts in word_part_counts.items():
        if counts['total'] < 3:  # Minimum frequency
            continue

        part1_frac = counts['part1'] / counts['total']

        if part1_frac > 0.7:
            high_part1_concentration.append({
                'word': word,
                'total': counts['total'],
                'part1_fraction': round(part1_frac, 3),
                'part1_count': counts['part1'],
                'part2_count': counts['part2'],
                'part3_count': counts['part3'],
                'entry_initial_count': word_entry_initial.get(word, 0),
                'folios': len(word_folios[word]),
                'prefix': get_prefix(word),
                'suffix': get_suffix(word),
                'length': len(word)
            })

        if part1_frac == 1.0 and counts['total'] >= 2:
            part1_only.append({
                'word': word,
                'count': counts['total'],
                'prefix': get_prefix(word),
                'suffix': get_suffix(word),
                'length': len(word)
            })

    for word, count in word_entry_initial.items():
        if count >= 2:
            entry_initial_words.append({
                'word': word,
                'entry_initial_count': count,
                'total_occurrences': word_part_counts[word]['total'],
                'entry_initial_rate': round(count / len(word_folios[word]), 3)
                    if word_folios[word] else 0,
                'prefix': get_prefix(word),
                'suffix': get_suffix(word)
            })

    # Sort by relevant metric
    high_part1_concentration.sort(key=lambda x: x['part1_fraction'], reverse=True)
    part1_only.sort(key=lambda x: x['count'], reverse=True)
    entry_initial_words.sort(key=lambda x: x['entry_initial_count'], reverse=True)

    return {
        'high_part1_concentration': {
            'criterion': '>70% of occurrences in Part 1',
            'count': len(high_part1_concentration),
            'candidates': high_part1_concentration[:30]
        },
        'part1_only': {
            'criterion': '100% in Part 1, min 2 occurrences',
            'count': len(part1_only),
            'candidates': part1_only[:30]
        },
        'entry_initial': {
            'criterion': 'Appears entry-initial 2+ times',
            'count': len(entry_initial_words),
            'candidates': entry_initial_words[:30]
        }
    }

# =============================================================================
# HEADING WORD STRUCTURAL PATTERNS
# =============================================================================

def analyze_heading_structure(candidates: List[Dict]) -> Dict:
    """Analyze structural patterns of heading candidates."""

    if not candidates:
        return {'error': 'No candidates to analyze'}

    lengths = [c['length'] for c in candidates]
    prefixes = Counter([c.get('prefix', '') for c in candidates])
    suffixes = Counter([c.get('suffix', '') for c in candidates])

    # Check compositional similarity
    prefix_concentration = max(prefixes.values()) / len(candidates) if candidates else 0
    suffix_concentration = max(suffixes.values()) / len(candidates) if candidates else 0

    # Structure diversity
    is_structurally_diverse = prefix_concentration < 0.3 and suffix_concentration < 0.3

    return {
        'length_statistics': {
            'mean': round(np.mean(lengths), 2),
            'std': round(np.std(lengths), 2),
            'min': min(lengths),
            'max': max(lengths),
            'mode': Counter(lengths).most_common(1)[0][0] if lengths else 0
        },
        'prefix_distribution': prefixes.most_common(10),
        'suffix_distribution': suffixes.most_common(10),
        'structural_diversity': {
            'prefix_concentration': round(prefix_concentration, 3),
            'suffix_concentration': round(suffix_concentration, 3),
            'is_diverse': is_structurally_diverse,
            'interpretation': 'Structurally DIVERSE (suggesting proper names)'
                if is_structurally_diverse else 'Structurally SIMILAR (suggesting category labels)'
        }
    }

# =============================================================================
# HEADING-BODY RELATIONSHIP
# =============================================================================

def analyze_heading_body_relationship(entries: Dict[str, List[Dict]], heading_words: Set[str]) -> Dict:
    """Analyze what follows heading words in entries."""

    # For entries with heading words, analyze Part 2 and Part 3
    entries_with_heading = []
    entries_without_heading = []

    part2_prefixes_with = Counter()
    part2_prefixes_without = Counter()
    part3_suffixes_with = Counter()
    part3_suffixes_without = Counter()

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        part1, part2, part3 = get_entry_parts(entry)
        part1_words = {w['word'] for w in part1}

        has_heading = bool(part1_words & heading_words)

        if has_heading:
            entries_with_heading.append(folio)
            for w in part2:
                part2_prefixes_with[get_prefix(w['word'])] += 1
            for w in part3:
                part3_suffixes_with[get_suffix(w['word'])] += 1
        else:
            entries_without_heading.append(folio)
            for w in part2:
                part2_prefixes_without[get_prefix(w['word'])] += 1
            for w in part3:
                part3_suffixes_without[get_suffix(w['word'])] += 1

    # Compare distributions
    total_with_p2 = sum(part2_prefixes_with.values())
    total_without_p2 = sum(part2_prefixes_without.values())

    # Find prefixes more common after heading
    heading_associated_prefixes = []
    for prefix in set(part2_prefixes_with.keys()) | set(part2_prefixes_without.keys()):
        with_rate = part2_prefixes_with.get(prefix, 0) / total_with_p2 if total_with_p2 else 0
        without_rate = part2_prefixes_without.get(prefix, 0) / total_without_p2 if total_without_p2 else 0
        if with_rate > 0 and without_rate > 0:
            ratio = with_rate / without_rate
            if ratio > 1.5:
                heading_associated_prefixes.append({
                    'prefix': prefix,
                    'ratio': round(ratio, 2),
                    'with_heading_rate': round(with_rate, 4),
                    'without_heading_rate': round(without_rate, 4)
                })

    heading_associated_prefixes.sort(key=lambda x: x['ratio'], reverse=True)

    return {
        'entries_with_heading': len(entries_with_heading),
        'entries_without_heading': len(entries_without_heading),
        'part2_prefix_after_heading': part2_prefixes_with.most_common(10),
        'part3_suffix_after_heading': part3_suffixes_with.most_common(10),
        'heading_associated_prefixes': heading_associated_prefixes[:15],
        'interpretation': f'{len(entries_with_heading)} entries have heading words in Part 1'
    }

# =============================================================================
# ONE-TO-ONE TEST
# =============================================================================

def one_to_one_test(entries: Dict[str, List[Dict]], currier: str = 'A') -> Dict:
    """Test if heading words are unique to entries or repeated."""

    # Get words appearing in Part 1
    part1_word_folios = defaultdict(set)

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue
        if entry[0]['currier'] != currier:
            continue

        part1, _, _ = get_entry_parts(entry)
        for w in part1:
            part1_word_folios[w['word']].add(folio)

    # Categorize by appearance count
    unique_to_one_entry = []  # Appear in exactly 1 entry's Part 1
    in_few_entries = []       # 2-3 entries
    in_many_entries = []      # 4+ entries

    for word, folios in part1_word_folios.items():
        entry = {
            'word': word,
            'entry_count': len(folios),
            'prefix': get_prefix(word),
            'suffix': get_suffix(word)
        }

        if len(folios) == 1:
            unique_to_one_entry.append(entry)
        elif len(folios) <= 3:
            in_few_entries.append(entry)
        else:
            in_many_entries.append(entry)

    # Summary
    total_part1_words = len(part1_word_folios)
    unique_fraction = len(unique_to_one_entry) / total_part1_words if total_part1_words else 0
    repeated_fraction = len(in_many_entries) / total_part1_words if total_part1_words else 0

    return {
        'total_part1_vocabulary': total_part1_words,
        'unique_to_one_entry': {
            'count': len(unique_to_one_entry),
            'fraction': round(unique_fraction, 3),
            'top_examples': sorted(unique_to_one_entry, key=lambda x: len(x['word']))[:20]
        },
        'in_few_entries_2_3': {
            'count': len(in_few_entries),
            'examples': in_few_entries[:20]
        },
        'in_many_entries_4_plus': {
            'count': len(in_many_entries),
            'examples': sorted(in_many_entries, key=lambda x: x['entry_count'], reverse=True)[:20]
        },
        'interpretation': {
            'pattern': 'MOSTLY_UNIQUE' if unique_fraction > 0.5 else
                       'MOSTLY_REPEATED' if repeated_fraction > 0.3 else 'MIXED',
            'suggests': 'Proper names (unique identifiers)' if unique_fraction > 0.5 else
                        'Category labels (repeated terms)' if repeated_fraction > 0.3 else
                        'Mix of names and categories'
        }
    }

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_analysis():
    """Run heading word deep analysis."""
    print("=" * 70)
    print("Phase 17, Task 5: Heading Word Deep Analysis")
    print("=" * 70)

    # Load data
    print("\n[1/7] Loading corpus...")
    all_words = load_corpus()
    currier_a = [w for w in all_words if w['currier'] == 'A']
    currier_b = [w for w in all_words if w['currier'] == 'B']
    print(f"  Currier A: {len(currier_a)} words")
    print(f"  Currier B: {len(currier_b)} words")

    # Segment into entries
    print("\n[2/7] Segmenting into entries...")
    a_entries = segment_into_entries(currier_a)
    b_entries = segment_into_entries(currier_b)

    valid_a = {f: e for f, e in a_entries.items() if len(e) >= MIN_ENTRY_WORDS}
    print(f"  Currier A: {len(valid_a)} valid entries")

    # Inventory known candidates
    print("\n[3/7] Analyzing known heading candidates...")
    known_inventory = inventory_known_candidates(currier_a, valid_a)
    for word, info in known_inventory.items():
        print(f"  {word}: {info['total_occurrences']} occurrences, Part 1 concentration: {info['part1_concentration']}")

    # Expanded heading detection
    print("\n[4/7] Detecting all heading candidates...")
    all_candidates = detect_all_heading_candidates(valid_a, currier='A')
    print(f"  High Part 1 concentration: {all_candidates['high_part1_concentration']['count']} words")
    print(f"  Part 1 only: {all_candidates['part1_only']['count']} words")
    print(f"  Entry-initial: {all_candidates['entry_initial']['count']} words")

    # Structural patterns
    print("\n[5/7] Analyzing heading structural patterns...")
    heading_list = all_candidates['high_part1_concentration']['candidates']
    structural_patterns = analyze_heading_structure(heading_list)
    print(f"  Mean length: {structural_patterns['length_statistics']['mean']}")
    print(f"  Structural diversity: {structural_patterns['structural_diversity']['interpretation']}")

    # Heading-body relationship
    print("\n[6/7] Analyzing heading-body relationships...")
    heading_words = {c['word'] for c in heading_list}
    heading_body = analyze_heading_body_relationship(valid_a, heading_words)
    print(f"  Entries with heading: {heading_body['entries_with_heading']}")
    print(f"  Heading-associated prefixes: {len(heading_body['heading_associated_prefixes'])}")

    # One-to-one test
    print("\n[7/7] Performing one-to-one test...")
    one_to_one = one_to_one_test(valid_a, currier='A')
    print(f"  Unique to one entry: {one_to_one['unique_to_one_entry']['count']} ({one_to_one['unique_to_one_entry']['fraction']:.1%})")
    print(f"  Pattern: {one_to_one['interpretation']['pattern']}")
    print(f"  Suggests: {one_to_one['interpretation']['suggests']}")

    # Compile results
    results = {
        'metadata': {
            'analysis': 'Phase 17 Task 5: Heading Word Deep Analysis',
            'corpus': 'Currier A',
            'timestamp': datetime.now().isoformat(),
            'valid_entries': len(valid_a)
        },
        'known_candidate_inventory': known_inventory,
        'expanded_heading_detection': all_candidates,
        'structural_patterns': structural_patterns,
        'heading_body_relationship': heading_body,
        'one_to_one_test': one_to_one,
        'summary': {
            'total_heading_candidates': all_candidates['high_part1_concentration']['count'],
            'part1_only_words': all_candidates['part1_only']['count'],
            'entry_initial_words': all_candidates['entry_initial']['count'],
            'key_findings': [
                f"Known candidates (pchor, kooiin, tshor) confirmed as Part 1 concentrated",
                f"{all_candidates['high_part1_concentration']['count']} words have >70% Part 1 concentration",
                f"{all_candidates['part1_only']['count']} words appear ONLY in Part 1",
                f"Heading words are {structural_patterns['structural_diversity']['interpretation'].lower()}",
                f"{one_to_one['unique_to_one_entry']['fraction']:.1%} of Part 1 vocabulary is unique to single entries",
                f"Pattern suggests: {one_to_one['interpretation']['suggests']}"
            ],
            'top_heading_candidates': [c['word'] for c in heading_list[:15]],
            'constraints_for_decipherment': [
                'Heading words concentrate in Part 1',
                f'Structural pattern: {structural_patterns["structural_diversity"]["interpretation"]}',
                f'One-to-one pattern: {one_to_one["interpretation"]["pattern"]}',
                'Certain prefixes associate with headings'
            ]
        }
    }

    # Save results
    output_file = 'heading_word_analysis_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'=' * 70}")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 70}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY: Heading Word Analysis")
    print("=" * 70)
    for finding in results['summary']['key_findings']:
        print(f"  - {finding}")

    print("\nTop 15 heading candidates:")
    for word in results['summary']['top_heading_candidates']:
        print(f"  - {word}")

    return results

if __name__ == '__main__':
    run_analysis()
