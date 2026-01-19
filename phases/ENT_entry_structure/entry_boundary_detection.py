#!/usr/bin/env python3
"""
Entry Boundary Detection

Detect where entries begin and end in the Voynich Manuscript using
multiple independent methods, then find consensus boundaries.

REVISED APPROACH: Since Voynich has extremely high vocabulary diversity,
we focus on:
1. FOLIO boundaries as primary entry markers (herbals = 1 plant/page)
2. First-line vocabulary distinctiveness
3. Prefix concentration at folio/paragraph beginnings
4. Cross-folio vocabulary patterns
5. Line-initial word markers

Success criterion: Consensus across 3+ methods
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set, Any


# Known prefixes from previous analysis
KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'qok', 'che', 'sho', 'dai', 'ota', 'oke'
]


def load_corpus() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Load corpus with line-level structure."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    all_words = []
    by_currier = {'A': [], 'B': []}

    seen = set()
    word_idx = 0

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

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                entry = {
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'idx': word_idx
                }
                all_words.append(entry)
                if currier in by_currier:
                    by_currier[currier].append(entry)
                word_idx += 1

    return all_words, by_currier


def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    if len(word) >= 2:
        return word[:2]
    return word


def compute_entropy(items: List) -> float:
    """Compute Shannon entropy in bits."""
    if not items:
        return 0
    counts = Counter(items)
    total = len(items)
    entropy = 0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def vocabulary_overlap(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard overlap between two vocabulary sets."""
    if not set1 or not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0


def chi_square_divergence(dist1: Counter, dist2: Counter) -> float:
    """Calculate chi-square-like divergence between two distributions."""
    all_keys = set(dist1.keys()) | set(dist2.keys())
    if not all_keys:
        return 0

    total1 = sum(dist1.values()) + 1e-10
    total2 = sum(dist2.values()) + 1e-10

    chi_sq = 0
    for key in all_keys:
        p1 = dist1.get(key, 0) / total1
        p2 = dist2.get(key, 0) / total2
        expected = (p1 + p2) / 2
        if expected > 0:
            chi_sq += (p1 - p2) ** 2 / expected

    return chi_sq


# ============================================================================
# METHOD 1: FOLIO-BASED ENTRY DETECTION
# ============================================================================

def detect_folio_entries(words: List[Dict]) -> Dict:
    """
    Treat each folio as a potential entry boundary.
    For herbals, entries typically correspond to folios (1 plant per page).
    """
    print("  Method 1: Folio-Based Entry Detection...")

    # Group words by folio
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    folios = list(by_folio.keys())
    folio_boundaries = []

    # Track folio statistics
    folio_stats = []
    for folio in folios:
        folio_words = by_folio[folio]
        first_word_idx = folio_words[0]['idx'] if folio_words else 0
        folio_boundaries.append(first_word_idx)

        folio_stats.append({
            'folio': folio,
            'word_count': len(folio_words),
            'first_word': folio_words[0]['word'] if folio_words else '',
            'unique_words': len(set(w['word'] for w in folio_words)),
            'start_idx': first_word_idx
        })

    # Calculate folio lengths
    folio_lengths = [s['word_count'] for s in folio_stats]
    mean_folio_length = sum(folio_lengths) / len(folio_lengths) if folio_lengths else 0
    if folio_lengths:
        variance = sum((l - mean_folio_length) ** 2 for l in folio_lengths) / len(folio_lengths)
        std_folio_length = math.sqrt(variance)
    else:
        std_folio_length = 0

    return {
        'boundaries': folio_boundaries,
        'boundary_count': len(folio_boundaries),
        'folio_count': len(folios),
        'folio_stats': folio_stats[:50],  # Sample
        'mean_folio_length': round(mean_folio_length, 2),
        'std_folio_length': round(std_folio_length, 2),
        'folio_length_distribution': dict(Counter(folio_lengths).most_common(20))
    }


# ============================================================================
# METHOD 2: CROSS-FOLIO VOCABULARY DISTINCTIVENESS
# ============================================================================

def detect_cross_folio_vocabulary(words: List[Dict]) -> Dict:
    """
    Measure how distinct each folio's vocabulary is from its neighbors.
    High distinctiveness suggests a new entry/topic.
    """
    print("  Method 2: Cross-Folio Vocabulary Distinctiveness...")

    # Group words by folio
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    folios = list(by_folio.keys())
    folio_vocabs = {f: set(w['word'] for w in by_folio[f]) for f in folios}

    # Calculate distinctiveness for each folio
    distinctiveness_scores = []
    high_distinctiveness_boundaries = []

    for i, folio in enumerate(folios):
        current_vocab = folio_vocabs[folio]

        # Compare to previous folio
        if i > 0:
            prev_vocab = folio_vocabs[folios[i-1]]
            prev_overlap = vocabulary_overlap(current_vocab, prev_vocab)
        else:
            prev_overlap = 0

        # Compare to next folio
        if i < len(folios) - 1:
            next_vocab = folio_vocabs[folios[i+1]]
            next_overlap = vocabulary_overlap(current_vocab, next_vocab)
        else:
            next_overlap = 0

        # Distinctiveness = low overlap with neighbors
        distinctiveness = 1 - (prev_overlap + next_overlap) / 2

        first_word_idx = by_folio[folio][0]['idx'] if by_folio[folio] else 0

        distinctiveness_scores.append({
            'folio': folio,
            'distinctiveness': round(distinctiveness, 3),
            'prev_overlap': round(prev_overlap, 3),
            'next_overlap': round(next_overlap, 3),
            'start_idx': first_word_idx
        })

    # Calculate mean and std
    scores = [d['distinctiveness'] for d in distinctiveness_scores]
    mean_distinctiveness = sum(scores) / len(scores) if scores else 0
    if scores:
        variance = sum((s - mean_distinctiveness) ** 2 for s in scores) / len(scores)
        std_distinctiveness = math.sqrt(variance)
    else:
        std_distinctiveness = 0

    # High distinctiveness suggests entry boundary
    boundaries = []
    for d in distinctiveness_scores:
        if d['distinctiveness'] > mean_distinctiveness + std_distinctiveness:
            boundaries.append(d['start_idx'])
            high_distinctiveness_boundaries.append(d)

    return {
        'boundaries': boundaries,
        'boundary_count': len(boundaries),
        'mean_distinctiveness': round(mean_distinctiveness, 3),
        'std_distinctiveness': round(std_distinctiveness, 3),
        'high_distinctiveness_folios': high_distinctiveness_boundaries[:30],
        'all_scores': distinctiveness_scores[:50]
    }


# ============================================================================
# METHOD 3: FIRST-LINE PREFIX PATTERNS
# ============================================================================

def detect_first_line_patterns(words: List[Dict]) -> Dict:
    """
    Analyze prefix patterns in first lines of folios vs rest.
    Entry-initial lines may have distinct prefix distributions.
    """
    print("  Method 3: First-Line Prefix Patterns...")

    # Group by folio and line
    by_folio = defaultdict(lambda: defaultdict(list))
    for w in words:
        by_folio[w['folio']][w['line']].append(w)

    first_line_prefixes = Counter()
    other_line_prefixes = Counter()
    first_line_boundaries = []

    for folio, lines in by_folio.items():
        sorted_lines = sorted(lines.keys())

        for i, line in enumerate(sorted_lines):
            line_words = lines[line]

            # Get prefixes
            for w in line_words:
                prefix = get_prefix(w['word'])
                if i == 0:  # First line of folio
                    first_line_prefixes[prefix] += 1
                else:
                    other_line_prefixes[prefix] += 1

            # Mark first line boundaries
            if i == 0 and line_words:
                first_line_boundaries.append(line_words[0]['idx'])

    # Calculate prefix enrichment in first lines
    total_first = sum(first_line_prefixes.values())
    total_other = sum(other_line_prefixes.values())

    enriched_prefixes = []
    for prefix in set(first_line_prefixes.keys()) | set(other_line_prefixes.keys()):
        first_rate = first_line_prefixes[prefix] / total_first if total_first > 0 else 0
        other_rate = other_line_prefixes[prefix] / total_other if total_other > 0 else 0

        if other_rate > 0:
            enrichment = first_rate / other_rate
        else:
            enrichment = first_rate * 10 if first_rate > 0 else 0

        if first_line_prefixes[prefix] >= 3:  # Minimum count
            enriched_prefixes.append({
                'prefix': prefix,
                'first_line_count': first_line_prefixes[prefix],
                'other_count': other_line_prefixes[prefix],
                'enrichment': round(enrichment, 2)
            })

    # Sort by enrichment
    enriched_prefixes.sort(key=lambda x: -x['enrichment'])

    # Top entry-initial prefixes
    entry_initial_prefixes = [p for p in enriched_prefixes if p['enrichment'] > 1.5]

    return {
        'boundaries': first_line_boundaries,
        'boundary_count': len(first_line_boundaries),
        'entry_initial_prefixes': entry_initial_prefixes[:20],
        'all_prefix_analysis': enriched_prefixes[:30],
        'total_first_line_words': total_first,
        'total_other_words': total_other
    }


# ============================================================================
# METHOD 4: LINE/PARAGRAPH ALIGNMENT
# ============================================================================

def detect_line_boundaries(words: List[Dict]) -> Dict:
    """
    Detect natural boundaries at line and folio starts.
    These are physical structure boundaries in the manuscript.
    """
    print("  Method 4: Line/Paragraph Alignment...")

    line_starts = []
    folio_starts = []

    prev_folio = None
    prev_line = None

    for i, w in enumerate(words):
        folio = w['folio']
        line = w['line']

        # New folio
        if folio != prev_folio:
            folio_starts.append(i)
            line_starts.append(i)  # Folio start is also line start
        # New line (same folio)
        elif line != prev_line:
            line_starts.append(i)

        prev_folio = folio
        prev_line = line

    # Calculate line lengths
    line_lengths = []
    for j in range(len(line_starts) - 1):
        length = line_starts[j+1] - line_starts[j]
        line_lengths.append(length)

    if line_lengths:
        mean_line_length = sum(line_lengths) / len(line_lengths)
        variance = sum((l - mean_line_length) ** 2 for l in line_lengths) / len(line_lengths)
        std_line_length = math.sqrt(variance)
    else:
        mean_line_length, std_line_length = 0, 0

    return {
        'line_boundaries': line_starts,
        'folio_boundaries': folio_starts,
        'line_boundary_count': len(line_starts),
        'folio_boundary_count': len(folio_starts),
        'mean_line_length': round(mean_line_length, 2),
        'std_line_length': round(std_line_length, 2),
        'line_length_distribution': dict(Counter(line_lengths).most_common(20))
    }


# ============================================================================
# METHOD 5: SENTENCE-INITIAL WORD PATTERNS
# ============================================================================

def detect_initial_word_patterns(words: List[Dict]) -> Dict:
    """
    Identify words that appear disproportionately at line beginnings.
    These may be entry-initial markers.
    """
    print("  Method 5: Sentence-Initial Word Patterns...")

    # Track which words appear at line starts
    line_initial_words = Counter()
    all_words_count = Counter()

    prev_folio = None
    prev_line = None

    for w in words:
        word = w['word']
        folio = w['folio']
        line = w['line']

        all_words_count[word] += 1

        # Is this at line start?
        if folio != prev_folio or line != prev_line:
            line_initial_words[word] += 1

        prev_folio = folio
        prev_line = line

    # Calculate enrichment ratio for each word
    total_words = sum(all_words_count.values())
    total_line_starts = sum(line_initial_words.values())

    enrichment = {}
    for word, initial_count in line_initial_words.items():
        total_count = all_words_count[word]

        # Expected rate if random
        expected_rate = total_count / total_words
        # Actual rate at line starts
        actual_rate = initial_count / total_line_starts if total_line_starts > 0 else 0

        # Enrichment ratio
        ratio = actual_rate / expected_rate if expected_rate > 0 else 0

        # Only include words with sufficient counts
        if total_count >= 5 and initial_count >= 2:
            enrichment[word] = {
                'initial_count': initial_count,
                'total_count': total_count,
                'enrichment': round(ratio, 2)
            }

    # Sort by enrichment
    sorted_enrichment = sorted(enrichment.items(), key=lambda x: -x[1]['enrichment'])

    # Get top candidates
    top_initial_markers = sorted_enrichment[:30]

    # Calculate which positions these markers appear at
    marker_positions = []
    marker_words = set(w for w, _ in top_initial_markers[:10])

    for i, w in enumerate(words):
        if w['word'] in marker_words:
            marker_positions.append(i)

    return {
        'top_initial_markers': top_initial_markers,
        'marker_positions': marker_positions[:500],
        'total_line_starts': total_line_starts,
        'unique_initial_words': len(line_initial_words),
        'high_enrichment_count': sum(1 for w, d in enrichment.items() if d['enrichment'] > 2.0)
    }


# ============================================================================
# CONSENSUS ANALYSIS
# ============================================================================

def find_consensus_boundaries(method_results: Dict,
                              words: List[Dict],
                              proximity_threshold: int = 5) -> Dict:
    """
    Find boundaries where multiple methods agree.
    Boundaries within proximity_threshold positions are considered the same.
    """
    print("  Finding consensus boundaries...")

    # Collect all boundaries from each method
    all_method_boundaries = {
        'folio_entries': set(method_results['folio_entries'].get('boundaries', [])),
        'cross_folio_vocab': set(method_results['cross_folio_vocab'].get('boundaries', [])),
        'first_line_patterns': set(method_results['first_line_patterns'].get('boundaries', [])),
        'line_boundary': set(method_results['line_boundary'].get('line_boundaries', [])),
        'initial_marker': set(method_results['initial_markers'].get('marker_positions', []))
    }

    # For each position, count how many methods flagged nearby
    n = len(words)
    position_votes = defaultdict(set)

    for method, boundaries in all_method_boundaries.items():
        for b in boundaries:
            # Count votes for nearby positions
            for offset in range(-proximity_threshold, proximity_threshold + 1):
                pos = b + offset
                if 0 <= pos < n:
                    position_votes[pos].add(method)

    # Find positions with multiple method agreement
    consensus_3plus = []
    consensus_4plus = []
    consensus_all = []

    for pos, methods in sorted(position_votes.items()):
        if len(methods) >= 3:
            consensus_3plus.append((pos, list(methods)))
        if len(methods) >= 4:
            consensus_4plus.append((pos, list(methods)))
        if len(methods) == 5:
            consensus_all.append((pos, list(methods)))

    # Merge nearby consensus points
    def merge_nearby(positions: List[Tuple], threshold: int = 10):
        if not positions:
            return []

        merged = []
        current_cluster = [positions[0]]

        for pos, methods in positions[1:]:
            if pos - current_cluster[-1][0] <= threshold:
                current_cluster.append((pos, methods))
            else:
                # Finish current cluster - take middle position
                mid_idx = len(current_cluster) // 2
                merged.append(current_cluster[mid_idx])
                current_cluster = [(pos, methods)]

        # Don't forget last cluster
        if current_cluster:
            mid_idx = len(current_cluster) // 2
            merged.append(current_cluster[mid_idx])

        return merged

    merged_3plus = merge_nearby(consensus_3plus)
    merged_4plus = merge_nearby(consensus_4plus)

    # Calculate entry statistics
    if merged_3plus:
        positions_3plus = [p for p, _ in merged_3plus]
        entry_lengths = [positions_3plus[i+1] - positions_3plus[i]
                        for i in range(len(positions_3plus)-1)]

        if entry_lengths:
            mean_entry_length = sum(entry_lengths) / len(entry_lengths)
            variance = sum((l - mean_entry_length) ** 2 for l in entry_lengths) / len(entry_lengths)
            std_entry_length = math.sqrt(variance)
        else:
            mean_entry_length, std_entry_length = 0, 0
    else:
        entry_lengths = []
        mean_entry_length, std_entry_length = 0, 0

    # Calculate inter-method agreement
    method_pairs = [
        ('folio_entries', 'cross_folio_vocab'),
        ('folio_entries', 'first_line_patterns'),
        ('folio_entries', 'line_boundary'),
        ('first_line_patterns', 'initial_marker')
    ]

    pair_agreements = {}
    for m1, m2 in method_pairs:
        b1 = all_method_boundaries[m1]
        b2 = all_method_boundaries[m2]

        # Count how many in b1 have a match within threshold in b2
        matches = 0
        for pos1 in b1:
            for pos2 in b2:
                if abs(pos1 - pos2) <= proximity_threshold:
                    matches += 1
                    break

        agreement_rate = matches / len(b1) if b1 else 0
        pair_agreements[f'{m1}_vs_{m2}'] = round(agreement_rate, 3)

    return {
        'consensus_3plus': merged_3plus[:200],
        'consensus_4plus': merged_4plus[:100],
        'consensus_3plus_count': len(merged_3plus),
        'consensus_4plus_count': len(merged_4plus),
        'estimated_entries': len(merged_3plus) + 1 if merged_3plus else 0,
        'entry_lengths': entry_lengths[:100] if entry_lengths else [],
        'mean_entry_length': round(mean_entry_length, 2),
        'std_entry_length': round(std_entry_length, 2),
        'method_pair_agreements': pair_agreements,
        'method_boundary_counts': {m: len(b) for m, b in all_method_boundaries.items()}
    }


def analyze_corpus_section(words: List[Dict], section_name: str) -> Dict:
    """Run all detection methods on a corpus section."""
    print(f"\nAnalyzing {section_name} ({len(words)} words)...")

    results = {
        'section': section_name,
        'word_count': len(words)
    }

    # Run each method
    results['folio_entries'] = detect_folio_entries(words)
    results['cross_folio_vocab'] = detect_cross_folio_vocabulary(words)
    results['first_line_patterns'] = detect_first_line_patterns(words)
    results['line_boundary'] = detect_line_boundaries(words)
    results['initial_markers'] = detect_initial_word_patterns(words)

    # Find consensus
    results['consensus'] = find_consensus_boundaries(results, words)

    return results


def main():
    print("=" * 70)
    print("ENTRY BOUNDARY DETECTION")
    print("Multi-method detection of entry boundaries in Voynich text")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    all_words, by_currier = load_corpus()
    print(f"Total words: {len(all_words)}")
    print(f"Currier A: {len(by_currier['A'])} words")
    print(f"Currier B: {len(by_currier['B'])} words")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Multi-method entry boundary detection with consensus analysis',
        'methods': [
            'folio_entries',
            'cross_folio_vocab',
            'first_line_patterns',
            'line_boundary',
            'initial_markers'
        ]
    }

    # Analyze each section
    results['currier_a'] = analyze_corpus_section(by_currier['A'], 'Currier A')
    results['currier_b'] = analyze_corpus_section(by_currier['B'], 'Currier B')

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for section in ['currier_a', 'currier_b']:
        s = results[section]
        c = s['consensus']
        print(f"\n{section.upper()}:")
        print(f"  Word count: {s['word_count']}")
        print(f"  Estimated entries (3+ method consensus): {c['estimated_entries']}")
        print(f"  High-confidence boundaries (4+ methods): {c['consensus_4plus_count']}")
        print(f"  Mean entry length: {c['mean_entry_length']} words")
        print(f"  Std entry length: {c['std_entry_length']} words")

        print(f"\n  Method boundary counts:")
        for method, count in c['method_boundary_counts'].items():
            print(f"    {method}: {count}")

        print(f"\n  Method pair agreements:")
        for pair, agreement in c['method_pair_agreements'].items():
            print(f"    {pair}: {agreement:.1%}")

    # Compare A vs B
    print("\n" + "=" * 70)
    print("CURRIER A vs B COMPARISON")
    print("=" * 70)

    a_entries = results['currier_a']['consensus']['estimated_entries']
    b_entries = results['currier_b']['consensus']['estimated_entries']
    a_length = results['currier_a']['consensus']['mean_entry_length']
    b_length = results['currier_b']['consensus']['mean_entry_length']

    print(f"\nEntry counts:")
    print(f"  Currier A: ~{a_entries} entries")
    print(f"  Currier B: ~{b_entries} entries")

    print(f"\nMean entry length:")
    print(f"  Currier A: {a_length} words")
    print(f"  Currier B: {b_length} words")

    if a_length > 0 and b_length > 0:
        length_ratio = b_length / a_length
        print(f"\n  B entries are {length_ratio:.2f}x longer than A entries")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if a_entries > 0 and b_entries > 0:
        if a_length < b_length * 0.7:
            print("\nCurrier A has SHORTER entries than B - consistent with")
            print("labeled/captioned content (herbal descriptions) vs")
            print("longer expository entries (encyclopedia-like).")
        elif a_length > b_length * 1.3:
            print("\nCurrier A has LONGER entries than B - unexpected pattern")
            print("that warrants further investigation.")
        else:
            print("\nCurrier A and B have SIMILAR entry lengths.")

    # Check if boundaries could be detected
    if a_entries == 0 or b_entries == 0:
        print("\nWARNING: Could not detect entry boundaries in one or both sections.")
        print("This may indicate:")
        print("  - Text is not structured as discrete entries")
        print("  - Boundaries are not detectable with current methods")
        print("  - More sensitive detection parameters needed")

    # Save results
    with open('entry_boundary_detection_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to entry_boundary_detection_report.json")


if __name__ == '__main__':
    main()
