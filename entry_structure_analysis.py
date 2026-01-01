#!/usr/bin/env python3
"""
Entry Structure Analysis

Characterize the internal structure of detected entries:
1. Entry Length Analysis - distribution, variability
2. Entry Opening Patterns - which prefixes/words begin entries
3. Entry Closing Patterns - which prefixes/words end entries
4. Internal Structure - positional patterns within entries
5. Entry Type Classification - cluster entries by structural features

Uses folio boundaries as primary entry markers based on Task 1 findings.
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


def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    if len(word) >= 2:
        return word[-2:]
    return word


def segment_into_entries(words: List[Dict]) -> List[List[Dict]]:
    """
    Segment corpus into entries using folio boundaries.
    Each folio is treated as one entry (primary hypothesis from Task 1).
    """
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    # Convert to list of entries preserving folio order
    entries = []
    for folio in sorted(by_folio.keys()):
        entries.append(by_folio[folio])

    return entries


# ============================================================================
# ANALYSIS 1: ENTRY LENGTH ANALYSIS
# ============================================================================

def analyze_entry_lengths(entries: List[List[Dict]]) -> Dict:
    """Analyze distribution of entry lengths."""
    print("  Analyzing entry lengths...")

    lengths = [len(e) for e in entries if e]

    if not lengths:
        return {'error': 'No entries found'}

    mean_length = sum(lengths) / len(lengths)
    variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths)
    std_length = math.sqrt(variance)
    cv = std_length / mean_length if mean_length > 0 else 0  # Coefficient of variation

    # Quartiles
    sorted_lengths = sorted(lengths)
    n = len(sorted_lengths)
    q1 = sorted_lengths[n // 4]
    q2 = sorted_lengths[n // 2]  # median
    q3 = sorted_lengths[3 * n // 4]

    # Distribution buckets
    buckets = {
        '1-50': 0,
        '51-100': 0,
        '101-200': 0,
        '201-300': 0,
        '301-500': 0,
        '500+': 0
    }
    for l in lengths:
        if l <= 50:
            buckets['1-50'] += 1
        elif l <= 100:
            buckets['51-100'] += 1
        elif l <= 200:
            buckets['101-200'] += 1
        elif l <= 300:
            buckets['201-300'] += 1
        elif l <= 500:
            buckets['301-500'] += 1
        else:
            buckets['500+'] += 1

    return {
        'entry_count': len(lengths),
        'mean_length': round(mean_length, 2),
        'std_length': round(std_length, 2),
        'coefficient_of_variation': round(cv, 3),
        'min_length': min(lengths),
        'max_length': max(lengths),
        'q1': q1,
        'median': q2,
        'q3': q3,
        'length_distribution': buckets,
        'raw_lengths': sorted(lengths)[:100]  # Sample
    }


# ============================================================================
# ANALYSIS 2: ENTRY OPENING PATTERNS
# ============================================================================

def analyze_entry_openings(entries: List[List[Dict]]) -> Dict:
    """Analyze what prefixes/words begin entries."""
    print("  Analyzing entry opening patterns...")

    opening_words = Counter()
    opening_prefixes = Counter()
    opening_suffixes = Counter()
    first_n_words = defaultdict(list)  # First N words of each entry

    for entry in entries:
        if not entry:
            continue

        # First word
        first_word = entry[0]['word']
        opening_words[first_word] += 1
        opening_prefixes[get_prefix(first_word)] += 1
        opening_suffixes[get_suffix(first_word)] += 1

        # First 5 words
        first_five = [w['word'] for w in entry[:5]]
        first_n_words['first_5'].append(first_five)

    # Calculate which opening prefixes are enriched vs overall corpus
    all_words = [w for entry in entries for w in entry]
    all_prefixes = Counter(get_prefix(w['word']) for w in all_words)

    total_entries = len(entries)
    total_words = len(all_words)

    prefix_enrichment = []
    for prefix, opening_count in opening_prefixes.items():
        total_count = all_prefixes.get(prefix, 0)

        # Opening rate
        opening_rate = opening_count / total_entries if total_entries > 0 else 0
        # Overall rate
        overall_rate = total_count / total_words if total_words > 0 else 0
        # Enrichment
        enrichment = opening_rate / overall_rate if overall_rate > 0 else 0

        if opening_count >= 3:
            prefix_enrichment.append({
                'prefix': prefix,
                'opening_count': opening_count,
                'total_count': total_count,
                'enrichment': round(enrichment, 2)
            })

    prefix_enrichment.sort(key=lambda x: -x['enrichment'])

    # Top opening words
    top_opening_words = opening_words.most_common(30)

    # Candidate heading words (appear often at start, rarely elsewhere)
    heading_candidates = []
    for word, opening_count in opening_words.items():
        total_count = sum(1 for entry in entries for w in entry if w['word'] == word)
        if opening_count >= 3 and total_count >= 5:
            # What fraction of occurrences are at entry start?
            opening_fraction = opening_count / total_count
            if opening_fraction > 0.3:  # >30% of occurrences at start
                heading_candidates.append({
                    'word': word,
                    'opening_count': opening_count,
                    'total_count': total_count,
                    'opening_fraction': round(opening_fraction, 2)
                })

    heading_candidates.sort(key=lambda x: -x['opening_fraction'])

    return {
        'top_opening_words': top_opening_words,
        'top_opening_prefixes': opening_prefixes.most_common(20),
        'top_opening_suffixes': opening_suffixes.most_common(20),
        'prefix_enrichment': prefix_enrichment[:20],
        'heading_candidates': heading_candidates[:20],
        'sample_first_5': first_n_words['first_5'][:30]
    }


# ============================================================================
# ANALYSIS 3: ENTRY CLOSING PATTERNS
# ============================================================================

def analyze_entry_closings(entries: List[List[Dict]]) -> Dict:
    """Analyze what prefixes/words end entries."""
    print("  Analyzing entry closing patterns...")

    closing_words = Counter()
    closing_prefixes = Counter()
    closing_suffixes = Counter()
    last_n_words = defaultdict(list)

    for entry in entries:
        if not entry:
            continue

        # Last word
        last_word = entry[-1]['word']
        closing_words[last_word] += 1
        closing_prefixes[get_prefix(last_word)] += 1
        closing_suffixes[get_suffix(last_word)] += 1

        # Last 5 words
        last_five = [w['word'] for w in entry[-5:]]
        last_n_words['last_5'].append(last_five)

    # Calculate suffix enrichment at entry endings
    all_words = [w for entry in entries for w in entry]
    all_suffixes = Counter(get_suffix(w['word']) for w in all_words)

    total_entries = len(entries)
    total_words = len(all_words)

    suffix_enrichment = []
    for suffix, closing_count in closing_suffixes.items():
        total_count = all_suffixes.get(suffix, 0)

        closing_rate = closing_count / total_entries if total_entries > 0 else 0
        overall_rate = total_count / total_words if total_words > 0 else 0
        enrichment = closing_rate / overall_rate if overall_rate > 0 else 0

        if closing_count >= 3:
            suffix_enrichment.append({
                'suffix': suffix,
                'closing_count': closing_count,
                'total_count': total_count,
                'enrichment': round(enrichment, 2)
            })

    suffix_enrichment.sort(key=lambda x: -x['enrichment'])

    # Conclusion marker candidates
    conclusion_candidates = []
    for word, closing_count in closing_words.items():
        total_count = sum(1 for entry in entries for w in entry if w['word'] == word)
        if closing_count >= 3 and total_count >= 5:
            closing_fraction = closing_count / total_count
            if closing_fraction > 0.3:
                conclusion_candidates.append({
                    'word': word,
                    'closing_count': closing_count,
                    'total_count': total_count,
                    'closing_fraction': round(closing_fraction, 2)
                })

    conclusion_candidates.sort(key=lambda x: -x['closing_fraction'])

    return {
        'top_closing_words': closing_words.most_common(30),
        'top_closing_prefixes': closing_prefixes.most_common(20),
        'top_closing_suffixes': closing_suffixes.most_common(20),
        'suffix_enrichment': suffix_enrichment[:20],
        'conclusion_candidates': conclusion_candidates[:20],
        'sample_last_5': last_n_words['last_5'][:30]
    }


# ============================================================================
# ANALYSIS 4: INTERNAL STRUCTURE
# ============================================================================

def analyze_internal_structure(entries: List[List[Dict]]) -> Dict:
    """Analyze prefix distribution within entries."""
    print("  Analyzing internal structure...")

    # Normalize position: 0 = start, 1 = end
    prefix_positions = defaultdict(list)  # prefix -> list of normalized positions

    for entry in entries:
        n = len(entry)
        if n < 5:  # Skip very short entries
            continue

        for i, w in enumerate(entry):
            prefix = get_prefix(w['word'])
            normalized_pos = i / (n - 1) if n > 1 else 0
            prefix_positions[prefix].append(normalized_pos)

    # Calculate position statistics for each prefix
    prefix_position_stats = []
    for prefix, positions in prefix_positions.items():
        if len(positions) < 10:
            continue

        mean_pos = sum(positions) / len(positions)
        variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
        std_pos = math.sqrt(variance)

        # Categorize position tendency
        if mean_pos < 0.3:
            position_type = 'ENTRY_INITIAL'
        elif mean_pos > 0.7:
            position_type = 'ENTRY_FINAL'
        else:
            position_type = 'ENTRY_MEDIAL'

        # Is it concentrated or spread out?
        if std_pos < 0.25:
            spread = 'CONCENTRATED'
        else:
            spread = 'DISTRIBUTED'

        prefix_position_stats.append({
            'prefix': prefix,
            'count': len(positions),
            'mean_position': round(mean_pos, 3),
            'std_position': round(std_pos, 3),
            'position_type': position_type,
            'spread': spread
        })

    prefix_position_stats.sort(key=lambda x: x['mean_position'])

    # Identify position buckets
    initial_prefixes = [p for p in prefix_position_stats if p['position_type'] == 'ENTRY_INITIAL']
    final_prefixes = [p for p in prefix_position_stats if p['position_type'] == 'ENTRY_FINAL']
    medial_prefixes = [p for p in prefix_position_stats if p['position_type'] == 'ENTRY_MEDIAL']

    # Calculate entropy of prefix positions (are prefixes constrained or free?)
    def compute_position_entropy(positions: List[float], n_bins: int = 10) -> float:
        if not positions:
            return 0
        bins = [0] * n_bins
        for p in positions:
            bin_idx = min(int(p * n_bins), n_bins - 1)
            bins[bin_idx] += 1
        total = sum(bins)
        entropy = 0
        for count in bins:
            if count > 0:
                prob = count / total
                entropy -= prob * math.log2(prob)
        return entropy

    # Overall position entropy
    all_positions = []
    for positions in prefix_positions.values():
        all_positions.extend(positions)

    overall_entropy = compute_position_entropy(all_positions)
    max_entropy = math.log2(10)  # Maximum entropy for 10 bins

    return {
        'prefix_position_stats': prefix_position_stats[:50],
        'initial_prefixes': initial_prefixes[:15],
        'final_prefixes': final_prefixes[:15],
        'medial_prefixes': medial_prefixes[:15],
        'overall_position_entropy': round(overall_entropy, 3),
        'max_position_entropy': round(max_entropy, 3),
        'entropy_ratio': round(overall_entropy / max_entropy, 3) if max_entropy > 0 else 0
    }


# ============================================================================
# ANALYSIS 5: ENTRY TYPE CLASSIFICATION
# ============================================================================

def classify_entry_types(entries: List[List[Dict]]) -> Dict:
    """Cluster entries by structural features."""
    print("  Classifying entry types...")

    # Extract features for each entry
    entry_features = []

    for i, entry in enumerate(entries):
        if not entry:
            continue

        # Length
        length = len(entry)

        # Opening prefix
        opening_prefix = get_prefix(entry[0]['word'])

        # Closing suffix
        closing_suffix = get_suffix(entry[-1]['word'])

        # Prefix diversity
        prefixes = [get_prefix(w['word']) for w in entry]
        prefix_diversity = len(set(prefixes)) / len(prefixes) if prefixes else 0

        # Most common prefix
        prefix_counts = Counter(prefixes)
        dominant_prefix = prefix_counts.most_common(1)[0][0] if prefix_counts else ''
        dominant_fraction = prefix_counts.most_common(1)[0][1] / len(prefixes) if prefixes else 0

        entry_features.append({
            'entry_idx': i,
            'folio': entry[0]['folio'],
            'length': length,
            'opening_prefix': opening_prefix,
            'closing_suffix': closing_suffix,
            'prefix_diversity': round(prefix_diversity, 3),
            'dominant_prefix': dominant_prefix,
            'dominant_fraction': round(dominant_fraction, 3)
        })

    # Simple clustering based on length buckets and dominant features
    length_groups = {
        'SHORT': [],    # < 100 words
        'MEDIUM': [],   # 100-200 words
        'LONG': []      # > 200 words
    }

    for ef in entry_features:
        if ef['length'] < 100:
            length_groups['SHORT'].append(ef)
        elif ef['length'] < 200:
            length_groups['MEDIUM'].append(ef)
        else:
            length_groups['LONG'].append(ef)

    # Analyze characteristics of each group
    group_stats = {}
    for group_name, group_entries in length_groups.items():
        if not group_entries:
            continue

        opening_prefixes = Counter(e['opening_prefix'] for e in group_entries)
        closing_suffixes = Counter(e['closing_suffix'] for e in group_entries)
        dominant_prefixes = Counter(e['dominant_prefix'] for e in group_entries)

        mean_diversity = sum(e['prefix_diversity'] for e in group_entries) / len(group_entries)

        group_stats[group_name] = {
            'count': len(group_entries),
            'mean_diversity': round(mean_diversity, 3),
            'top_opening_prefixes': opening_prefixes.most_common(5),
            'top_closing_suffixes': closing_suffixes.most_common(5),
            'top_dominant_prefixes': dominant_prefixes.most_common(5)
        }

    # Identify potential entry "templates"
    # Common patterns in opening+closing
    opening_closing_pairs = Counter()
    for ef in entry_features:
        pair = (ef['opening_prefix'], ef['closing_suffix'])
        opening_closing_pairs[pair] += 1

    common_templates = opening_closing_pairs.most_common(20)

    return {
        'entry_count': len(entry_features),
        'length_groups': group_stats,
        'common_templates': common_templates,
        'sample_features': entry_features[:50]
    }


def analyze_section(words: List[Dict], section_name: str) -> Dict:
    """Run all analyses on a section."""
    print(f"\nAnalyzing {section_name} ({len(words)} words)...")

    entries = segment_into_entries(words)
    print(f"  Segmented into {len(entries)} entries (folios)")

    results = {
        'section': section_name,
        'word_count': len(words),
        'entry_count': len(entries)
    }

    results['length_analysis'] = analyze_entry_lengths(entries)
    results['opening_patterns'] = analyze_entry_openings(entries)
    results['closing_patterns'] = analyze_entry_closings(entries)
    results['internal_structure'] = analyze_internal_structure(entries)
    results['entry_types'] = classify_entry_types(entries)

    return results


def main():
    print("=" * 70)
    print("ENTRY STRUCTURE ANALYSIS")
    print("Characterizing internal structure of detected entries")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    all_words, by_currier = load_corpus()
    print(f"Total words: {len(all_words)}")
    print(f"Currier A: {len(by_currier['A'])} words")
    print(f"Currier B: {len(by_currier['B'])} words")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Entry structure characterization using folio-based segmentation'
    }

    # Analyze each section
    results['currier_a'] = analyze_section(by_currier['A'], 'Currier A')
    results['currier_b'] = analyze_section(by_currier['B'], 'Currier B')

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for section in ['currier_a', 'currier_b']:
        s = results[section]
        print(f"\n{section.upper()}:")
        print(f"  Entries: {s['entry_count']}")

        la = s['length_analysis']
        print(f"\n  Entry Length:")
        print(f"    Mean: {la['mean_length']} words")
        print(f"    Std: {la['std_length']} words")
        print(f"    CV: {la['coefficient_of_variation']}")
        print(f"    Range: {la['min_length']} - {la['max_length']}")

        op = s['opening_patterns']
        print(f"\n  Top Opening Prefixes:")
        for prefix, count in op['top_opening_prefixes'][:5]:
            print(f"    {prefix}: {count}")

        print(f"\n  Heading Candidates (>30% at entry start):")
        for h in op['heading_candidates'][:5]:
            print(f"    {h['word']}: {h['opening_count']}/{h['total_count']} ({h['opening_fraction']:.0%})")

        cp = s['closing_patterns']
        print(f"\n  Top Closing Suffixes:")
        for suffix, count in cp['top_closing_suffixes'][:5]:
            print(f"    {suffix}: {count}")

        istr = s['internal_structure']
        print(f"\n  Position Entropy Ratio: {istr['entropy_ratio']} (1.0 = uniform)")

        print(f"\n  Entry-Initial Prefixes:")
        for p in istr['initial_prefixes'][:3]:
            print(f"    {p['prefix']}: mean_pos={p['mean_position']}")

        print(f"\n  Entry-Final Prefixes:")
        for p in istr['final_prefixes'][:3]:
            print(f"    {p['prefix']}: mean_pos={p['mean_position']}")

    # Compare A vs B
    print("\n" + "=" * 70)
    print("CURRIER A vs B COMPARISON")
    print("=" * 70)

    a_mean = results['currier_a']['length_analysis']['mean_length']
    b_mean = results['currier_b']['length_analysis']['mean_length']
    a_cv = results['currier_a']['length_analysis']['coefficient_of_variation']
    b_cv = results['currier_b']['length_analysis']['coefficient_of_variation']

    print(f"\nEntry Length:")
    print(f"  A mean: {a_mean}, B mean: {b_mean}")
    print(f"  B entries are {b_mean/a_mean:.1f}x longer than A")

    print(f"\nEntry Regularity (lower CV = more regular):")
    print(f"  A CV: {a_cv}, B CV: {b_cv}")
    if a_cv < b_cv:
        print(f"  A entries are MORE REGULAR than B")
    else:
        print(f"  B entries are MORE REGULAR than A")

    # Check if opening/closing patterns differ
    a_top_open = results['currier_a']['opening_patterns']['top_opening_prefixes'][0][0]
    b_top_open = results['currier_b']['opening_patterns']['top_opening_prefixes'][0][0]

    print(f"\nTop Opening Prefix:")
    print(f"  A: {a_top_open}")
    print(f"  B: {b_top_open}")

    if a_top_open != b_top_open:
        print(f"  Different opening patterns - distinct entry types")

    # Save results
    with open('entry_structure_analysis_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to entry_structure_analysis_report.json")


if __name__ == '__main__':
    main()
