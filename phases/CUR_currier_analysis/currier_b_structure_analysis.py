#!/usr/bin/env python3
"""
Phase 17, Task 2: Currier B Structure Comparison

This script applies the same three-part structure analysis to Currier B
and compares results with Currier A to characterize structural differences.

Output: currier_b_structure_report.json
"""

import csv
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
import numpy as np
from scipy import stats

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

MIN_ENTRY_WORDS = 9

# =============================================================================
# DATA LOADING (same as Task 1)
# =============================================================================

def load_corpus() -> List[Dict]:
    """Load the Voynich transcription corpus."""
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

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def compute_prefix_distribution(words: List[Dict]) -> Dict[str, float]:
    if not words:
        return {}
    prefixes = [get_prefix(w['word']) for w in words]
    counts = Counter(prefixes)
    total = len(prefixes)
    return {p: c / total for p, c in counts.items()}

def jensen_shannon_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    all_keys = set(p.keys()) | set(q.keys())
    if not all_keys:
        return 0.0
    p_vec = np.array([p.get(k, 0) for k in all_keys])
    q_vec = np.array([q.get(k, 0) for k in all_keys])
    eps = 1e-10
    p_vec = p_vec + eps
    q_vec = q_vec + eps
    p_vec = p_vec / p_vec.sum()
    q_vec = q_vec / q_vec.sum()
    m = 0.5 * (p_vec + q_vec)
    return 0.5 * (stats.entropy(p_vec, m) + stats.entropy(q_vec, m))

def test_n_part_structure(entries: Dict[str, List[Dict]], n_parts: int) -> Dict:
    """Test if entries show n-part structure."""

    part_prefix_counts = {i: Counter() for i in range(1, n_parts + 1)}
    part_totals = {i: 0 for i in range(1, n_parts + 1)}
    overall_prefix_counts = Counter()
    overall_total = 0

    analyzed_entries = 0

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        analyzed_entries += 1
        n = len(entry)
        part_size = n // n_parts

        for part_num in range(1, n_parts + 1):
            start = (part_num - 1) * part_size
            end = part_num * part_size if part_num < n_parts else n
            part_words = entry[start:end]

            for w in part_words:
                prefix = get_prefix(w['word'])
                part_prefix_counts[part_num][prefix] += 1
                part_totals[part_num] += 1
                overall_prefix_counts[prefix] += 1
                overall_total += 1

    # Calculate enrichment
    enriched_counts = {i: 0 for i in range(1, n_parts + 1)}
    max_enrichments = {i: 0 for i in range(1, n_parts + 1)}

    for prefix in overall_prefix_counts:
        if overall_prefix_counts[prefix] < 5:
            continue
        overall_rate = overall_prefix_counts[prefix] / overall_total

        for part in range(1, n_parts + 1):
            if part_totals[part] > 0:
                part_rate = part_prefix_counts[part][prefix] / part_totals[part]
                enrichment = part_rate / overall_rate if overall_rate > 0 else 0
                if enrichment > 2.0:
                    enriched_counts[part] += 1
                if enrichment > max_enrichments[part]:
                    max_enrichments[part] = enrichment

    # Compute position entropy
    position_entropy = {}
    for part in range(1, n_parts + 1):
        if part_totals[part] > 0:
            counts = list(part_prefix_counts[part].values())
            total = sum(counts)
            entropy = sum(-c/total * math.log2(c/total) for c in counts if c > 0)
            position_entropy[part] = round(entropy, 3)

    return {
        'n_parts': n_parts,
        'analyzed_entries': analyzed_entries,
        'enriched_prefixes_per_part': enriched_counts,
        'total_enriched': sum(enriched_counts.values()),
        'max_enrichment_per_part': {k: round(v, 3) for k, v in max_enrichments.items()},
        'position_entropy': position_entropy,
        'part_totals': part_totals
    }

def analyze_position_distribution(entries: Dict[str, List[Dict]]) -> Dict:
    """Analyze prefix distribution by normalized position (0.0-1.0)."""

    # Divide into 10 position bins
    n_bins = 10
    bin_prefix_counts = {i: Counter() for i in range(n_bins)}
    bin_totals = {i: 0 for i in range(n_bins)}

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        n = len(entry)
        for i, w in enumerate(entry):
            pos = i / n  # Normalized position
            bin_idx = min(int(pos * n_bins), n_bins - 1)
            prefix = get_prefix(w['word'])
            bin_prefix_counts[bin_idx][prefix] += 1
            bin_totals[bin_idx] += 1

    # Find opening vs closing vocabulary
    opening_dist = compute_prefix_distribution_from_counter(bin_prefix_counts[0])
    closing_dist = compute_prefix_distribution_from_counter(bin_prefix_counts[n_bins - 1])

    # Calculate divergence between opening and closing
    opening_closing_divergence = jensen_shannon_divergence(opening_dist, closing_dist)

    # Find position-specific prefixes
    opening_prefixes = []
    closing_prefixes = []

    overall = Counter()
    for bc in bin_prefix_counts.values():
        overall.update(bc)
    overall_total = sum(overall.values())

    for prefix, count in overall.items():
        if count < 10:
            continue
        overall_rate = count / overall_total

        # Opening rate (first 20%)
        opening_count = bin_prefix_counts[0].get(prefix, 0) + bin_prefix_counts[1].get(prefix, 0)
        opening_total = bin_totals[0] + bin_totals[1]
        opening_rate = opening_count / opening_total if opening_total > 0 else 0
        opening_enrichment = opening_rate / overall_rate if overall_rate > 0 else 0

        # Closing rate (last 20%)
        closing_count = bin_prefix_counts[n_bins-1].get(prefix, 0) + bin_prefix_counts[n_bins-2].get(prefix, 0)
        closing_total = bin_totals[n_bins-1] + bin_totals[n_bins-2]
        closing_rate = closing_count / closing_total if closing_total > 0 else 0
        closing_enrichment = closing_rate / overall_rate if overall_rate > 0 else 0

        if opening_enrichment > 1.5:
            opening_prefixes.append({'prefix': prefix, 'enrichment': round(opening_enrichment, 3)})
        if closing_enrichment > 1.5:
            closing_prefixes.append({'prefix': prefix, 'enrichment': round(closing_enrichment, 3)})

    opening_prefixes.sort(key=lambda x: x['enrichment'], reverse=True)
    closing_prefixes.sort(key=lambda x: x['enrichment'], reverse=True)

    return {
        'opening_closing_divergence': round(opening_closing_divergence, 4),
        'opening_prefixes': opening_prefixes[:15],
        'closing_prefixes': closing_prefixes[:15],
        'interpretation': 'HIGH divergence (distinct opening/closing)'
            if opening_closing_divergence > 0.1 else 'LOW divergence (continuous)',
        'bin_totals': bin_totals
    }

def compute_prefix_distribution_from_counter(counter: Counter) -> Dict[str, float]:
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counter.items()}

def compare_a_vs_b(a_entries: Dict, b_entries: Dict) -> Dict:
    """Create comparison matrix between Currier A and B."""

    # Test multiple part structures for both
    a_tests = {}
    b_tests = {}

    for n_parts in [2, 3, 4]:
        a_tests[n_parts] = test_n_part_structure(a_entries, n_parts)
        b_tests[n_parts] = test_n_part_structure(b_entries, n_parts)

    # Get position analysis
    a_pos = analyze_position_distribution(a_entries)
    b_pos = analyze_position_distribution(b_entries)

    # Determine best structure for each
    best_a = max(a_tests.keys(), key=lambda k: a_tests[k]['total_enriched'])
    best_b = max(b_tests.keys(), key=lambda k: b_tests[k]['total_enriched'])

    # Entry statistics
    a_lengths = [len(e) for e in a_entries.values() if len(e) >= MIN_ENTRY_WORDS]
    b_lengths = [len(e) for e in b_entries.values() if len(e) >= MIN_ENTRY_WORDS]

    return {
        'currier_a': {
            'entry_count': len(a_lengths),
            'mean_length': round(np.mean(a_lengths), 1),
            'std_length': round(np.std(a_lengths), 1),
            'cv_length': round(np.std(a_lengths) / np.mean(a_lengths), 3),
            'best_part_structure': best_a,
            'enriched_prefixes_at_best': a_tests[best_a]['total_enriched'],
            'opening_closing_divergence': a_pos['opening_closing_divergence'],
            'opening_prefix_count': len(a_pos['opening_prefixes']),
            'closing_prefix_count': len(a_pos['closing_prefixes'])
        },
        'currier_b': {
            'entry_count': len(b_lengths),
            'mean_length': round(np.mean(b_lengths), 1),
            'std_length': round(np.std(b_lengths), 1),
            'cv_length': round(np.std(b_lengths) / np.mean(b_lengths), 3),
            'best_part_structure': best_b,
            'enriched_prefixes_at_best': b_tests[best_b]['total_enriched'],
            'opening_closing_divergence': b_pos['opening_closing_divergence'],
            'opening_prefix_count': len(b_pos['opening_prefixes']),
            'closing_prefix_count': len(b_pos['closing_prefixes'])
        },
        'comparison': {
            'b_to_a_length_ratio': round(np.mean(b_lengths) / np.mean(a_lengths), 2),
            'structure_difference': 'SAME' if best_a == best_b else f'A={best_a}-part, B={best_b}-part',
            'b_more_continuous': b_pos['opening_closing_divergence'] < a_pos['opening_closing_divergence'],
            'heading_vocabulary_comparison': {
                'a_opening_prefixes': len(a_pos['opening_prefixes']),
                'b_opening_prefixes': len(b_pos['opening_prefixes']),
                'a_has_more_distinct_openings': len(a_pos['opening_prefixes']) > len(b_pos['opening_prefixes'])
            }
        }
    }

def analyze_vocabulary_overlap_by_position(a_entries: Dict, b_entries: Dict) -> Dict:
    """Compare vocabulary at different positions between A and B."""

    # Extract vocabulary from first 20%, middle, and last 20%
    def get_position_vocabulary(entries: Dict) -> Dict[str, Set[str]]:
        vocab = {'opening': set(), 'middle': set(), 'closing': set()}

        for folio, entry in entries.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue

            n = len(entry)
            opening_end = n // 5
            closing_start = 4 * n // 5

            for i, w in enumerate(entry):
                word = w['word']
                if i < opening_end:
                    vocab['opening'].add(word)
                elif i >= closing_start:
                    vocab['closing'].add(word)
                else:
                    vocab['middle'].add(word)

        return vocab

    a_vocab = get_position_vocabulary(a_entries)
    b_vocab = get_position_vocabulary(b_entries)

    # Calculate overlaps
    position_overlaps = {}
    for pos in ['opening', 'middle', 'closing']:
        shared = a_vocab[pos] & b_vocab[pos]
        only_a = a_vocab[pos] - b_vocab[pos]
        only_b = b_vocab[pos] - a_vocab[pos]

        position_overlaps[pos] = {
            'shared_count': len(shared),
            'only_a_count': len(only_a),
            'only_b_count': len(only_b),
            'jaccard': round(len(shared) / len(a_vocab[pos] | b_vocab[pos]), 3)
                if (a_vocab[pos] | b_vocab[pos]) else 0,
            'shared_examples': list(shared)[:20]
        }

    return position_overlaps

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_analysis():
    """Run Currier B structure analysis and comparison with A."""
    print("=" * 70)
    print("Phase 17, Task 2: Currier B Structure Comparison")
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
    valid_b = {f: e for f, e in b_entries.items() if len(e) >= MIN_ENTRY_WORDS}
    print(f"  Currier A: {len(valid_a)} valid entries")
    print(f"  Currier B: {len(valid_b)} valid entries")

    # Test different part structures for B
    print("\n[3/7] Testing part structures for Currier B...")
    b_structure_tests = {}
    for n_parts in [2, 3, 4]:
        result = test_n_part_structure(valid_b, n_parts)
        b_structure_tests[f'{n_parts}_part'] = result
        print(f"  {n_parts}-part: {result['total_enriched']} enriched prefixes")

    # Position distribution analysis for B
    print("\n[4/7] Analyzing position distribution for Currier B...")
    b_position = analyze_position_distribution(valid_b)
    print(f"  Opening-closing divergence: {b_position['opening_closing_divergence']:.4f}")
    print(f"  Opening prefixes: {len(b_position['opening_prefixes'])}")
    print(f"  Closing prefixes: {len(b_position['closing_prefixes'])}")

    # A vs B comparison
    print("\n[5/7] Comparing Currier A vs B...")
    comparison = compare_a_vs_b(valid_a, valid_b)
    print(f"  A best structure: {comparison['currier_a']['best_part_structure']}-part")
    print(f"  B best structure: {comparison['currier_b']['best_part_structure']}-part")
    print(f"  B/A length ratio: {comparison['comparison']['b_to_a_length_ratio']}x")

    # Vocabulary overlap by position
    print("\n[6/7] Analyzing vocabulary overlap by position...")
    vocab_overlap = analyze_vocabulary_overlap_by_position(valid_a, valid_b)
    print(f"  Opening vocabulary Jaccard: {vocab_overlap['opening']['jaccard']}")
    print(f"  Middle vocabulary Jaccard: {vocab_overlap['middle']['jaccard']}")
    print(f"  Closing vocabulary Jaccard: {vocab_overlap['closing']['jaccard']}")

    # Determine B structure type
    print("\n[7/7] Determining Currier B structure type...")

    # Compare 3-part enrichment counts
    b_3part_enriched = b_structure_tests['3_part']['total_enriched']
    b_2part_enriched = b_structure_tests['2_part']['total_enriched']

    if b_3part_enriched >= 6:
        structure_type = 'THREE_PART'
        structure_clarity = 'CLEAR'
    elif b_2part_enriched >= 4:
        structure_type = 'TWO_PART'
        structure_clarity = 'MODERATE'
    elif b_position['opening_closing_divergence'] > 0.1:
        structure_type = 'OPENING_CLOSING'
        structure_clarity = 'WEAK'
    else:
        structure_type = 'CONTINUOUS'
        structure_clarity = 'NO_CLEAR_STRUCTURE'

    print(f"  Structure type: {structure_type}")
    print(f"  Structure clarity: {structure_clarity}")

    # Compile results
    results = {
        'metadata': {
            'analysis': 'Phase 17 Task 2: Currier B Structure Comparison',
            'timestamp': datetime.now().isoformat(),
            'currier_a_entries': len(valid_a),
            'currier_b_entries': len(valid_b)
        },
        'currier_b_structure_tests': b_structure_tests,
        'currier_b_position_analysis': b_position,
        'a_vs_b_comparison': comparison,
        'vocabulary_overlap_by_position': vocab_overlap,
        'currier_b_structure_determination': {
            'structure_type': structure_type,
            'structure_clarity': structure_clarity,
            'evidence': {
                '3_part_enriched': b_3part_enriched,
                '2_part_enriched': b_2part_enriched,
                'opening_closing_divergence': b_position['opening_closing_divergence']
            },
            'interpretation': f'Currier B shows {structure_type} structure with {structure_clarity} evidence'
        },
        'summary': {
            'key_findings': [
                f"Currier B has {len(valid_b)} entries averaging {comparison['currier_b']['mean_length']} words",
                f"B entries are {comparison['comparison']['b_to_a_length_ratio']}x longer than A",
                f"B structure type: {structure_type} ({structure_clarity})",
                f"B has {len(b_position['opening_prefixes'])} opening-specific prefixes vs A's {comparison['currier_a']['opening_prefix_count']}",
                f"Opening vocabulary Jaccard (A-B): {vocab_overlap['opening']['jaccard']}",
                f"Middle vocabulary Jaccard (A-B): {vocab_overlap['middle']['jaccard']}",
                f"B is {'MORE' if comparison['comparison']['b_more_continuous'] else 'LESS'} continuous than A"
            ],
            'structural_differences': {
                'A_has_clearer_3_part': comparison['currier_a']['enriched_prefixes_at_best'] > comparison['currier_b']['enriched_prefixes_at_best'],
                'A_has_more_distinct_openings': comparison['comparison']['heading_vocabulary_comparison']['a_has_more_distinct_openings'],
                'entries_are_different_length': comparison['comparison']['b_to_a_length_ratio'] > 1.5
            },
            'constraints_for_decipherment': [
                'Currier B has different structure than A',
                f'B structure is {structure_type}',
                f'B entries are {comparison["comparison"]["b_to_a_length_ratio"]}x longer',
                'A and B share vocabulary but distribution differs by position'
            ]
        }
    }

    # Save results
    output_file = 'currier_b_structure_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'=' * 70}")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 70}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY: Currier B Structure Analysis")
    print("=" * 70)
    for finding in results['summary']['key_findings']:
        print(f"  - {finding}")

    return results

if __name__ == '__main__':
    run_analysis()
