#!/usr/bin/env python3
"""
Currier A Deep Dive

Intensive analysis of Currier A as potentially more tractable reference material:
1. Entry Detection in A Only - are boundaries clearer in A?
2. Entry Regularity - how regular are A entries?
3. Label/Heading Detection - candidate heading words
4. Comparison to Herbal Structure - three-part structure?
5. Illustration Alignment - do entries correlate with folios/pages?

Currier A is predominantly herbal sections with illustrations.
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
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
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


def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    if len(word) >= 2:
        return word[-2:]
    return word


def segment_into_entries(words: List[Dict]) -> List[List[Dict]]:
    """Segment corpus into entries using folio boundaries."""
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    entries = []
    for folio in sorted(by_folio.keys()):
        entries.append(by_folio[folio])

    return entries


# ============================================================================
# ANALYSIS 1: ENTRY DETECTION IN A ONLY
# ============================================================================

def analyze_entry_detection(words: List[Dict]) -> Dict:
    """
    Apply boundary detection methods to Currier A alone.
    Are boundaries clearer in A than in full corpus?
    """
    print("  Analyzing entry detection in Currier A...")

    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    folios = list(sorted(by_folio.keys()))
    entries = [by_folio[f] for f in folios]

    # Calculate vocabulary overlap between adjacent folios
    folio_overlaps = []
    for i in range(len(folios) - 1):
        vocab1 = set(w['word'] for w in by_folio[folios[i]])
        vocab2 = set(w['word'] for w in by_folio[folios[i + 1]])

        intersection = len(vocab1 & vocab2)
        union = len(vocab1 | vocab2)
        overlap = intersection / union if union > 0 else 0

        folio_overlaps.append({
            'folio_pair': (folios[i], folios[i + 1]),
            'overlap': round(overlap, 3)
        })

    overlaps = [fo['overlap'] for fo in folio_overlaps]
    mean_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
    variance = sum((o - mean_overlap) ** 2 for o in overlaps) / len(overlaps) if overlaps else 0
    std_overlap = math.sqrt(variance)

    # Identify sharp boundaries (low overlap)
    sharp_boundaries = [fo for fo in folio_overlaps if fo['overlap'] < mean_overlap - std_overlap]

    # Identify continuous sections (high overlap)
    continuous_sections = [fo for fo in folio_overlaps if fo['overlap'] > mean_overlap + std_overlap]

    return {
        'folio_count': len(folios),
        'entry_count': len(entries),
        'mean_adjacent_overlap': round(mean_overlap, 3),
        'std_adjacent_overlap': round(std_overlap, 3),
        'sharp_boundary_count': len(sharp_boundaries),
        'continuous_section_count': len(continuous_sections),
        'sharp_boundaries': sharp_boundaries[:20],
        'continuous_sections': continuous_sections[:10],
        'all_overlaps': folio_overlaps[:50]
    }


# ============================================================================
# ANALYSIS 2: ENTRY REGULARITY
# ============================================================================

def analyze_entry_regularity(words: List[Dict]) -> Dict:
    """
    How regular are A entries in length and structure?
    """
    print("  Analyzing entry regularity...")

    entries = segment_into_entries(words)

    # Length regularity
    lengths = [len(e) for e in entries if e]
    mean_length = sum(lengths) / len(lengths) if lengths else 0
    variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths) if lengths else 0
    std_length = math.sqrt(variance)
    cv = std_length / mean_length if mean_length > 0 else 0

    # Structural regularity - do entries follow similar patterns?
    # Compare first-line prefix distribution
    first_line_prefixes = []
    for entry in entries:
        # Get first line
        first_line = entry[0]['line'] if entry else None
        first_line_words = [w for w in entry if w['line'] == first_line]
        first_line_prefixes.append(tuple(get_prefix(w['word']) for w in first_line_words[:5]))

    # How many unique first-line patterns?
    unique_patterns = len(set(first_line_prefixes))
    pattern_reuse = 1 - (unique_patterns / len(first_line_prefixes)) if first_line_prefixes else 0

    # Most common first-line patterns
    first_line_pattern_counts = Counter(first_line_prefixes)
    top_patterns = first_line_pattern_counts.most_common(20)

    # Line count regularity
    line_counts = []
    for entry in entries:
        lines = set(w['line'] for w in entry)
        line_counts.append(len(lines))

    mean_lines = sum(line_counts) / len(line_counts) if line_counts else 0
    lines_variance = sum((l - mean_lines) ** 2 for l in line_counts) / len(line_counts) if line_counts else 0
    lines_cv = math.sqrt(lines_variance) / mean_lines if mean_lines > 0 else 0

    return {
        'length_regularity': {
            'mean_length': round(mean_length, 2),
            'std_length': round(std_length, 2),
            'cv': round(cv, 3),
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0
        },
        'line_count_regularity': {
            'mean_lines': round(mean_lines, 2),
            'cv': round(lines_cv, 3)
        },
        'structural_regularity': {
            'unique_first_line_patterns': unique_patterns,
            'total_entries': len(first_line_prefixes),
            'pattern_reuse_rate': round(pattern_reuse, 3)
        },
        'top_first_line_patterns': top_patterns
    }


# ============================================================================
# ANALYSIS 3: LABEL/HEADING DETECTION
# ============================================================================

def detect_labels_and_headings(words: List[Dict]) -> Dict:
    """
    Identify candidate heading words in Currier A.
    Criteria: appear at entry beginnings, short, distinct from body vocabulary.
    """
    print("  Detecting candidate labels and headings...")

    entries = segment_into_entries(words)

    # Entry-initial words (first word of each entry)
    initial_words = Counter()
    first_line_words = Counter()  # Words in first line

    # Body words (not in first line)
    body_words = Counter()

    for entry in entries:
        if not entry:
            continue

        # First word
        initial_words[entry[0]['word']] += 1

        # First line
        first_line = entry[0]['line']
        first_line_ws = [w for w in entry if w['line'] == first_line]
        for w in first_line_ws:
            first_line_words[w['word']] += 1

        # Body
        for w in entry:
            if w['line'] != first_line:
                body_words[w['word']] += 1

    # Calculate heading characteristics
    heading_candidates = []

    for word, initial_count in initial_words.items():
        if initial_count < 2:
            continue

        first_line_count = first_line_words.get(word, 0)
        body_count = body_words.get(word, 0)
        total_count = first_line_count + body_count

        # Heading-like characteristics
        word_length = len(word)
        initial_fraction = initial_count / len(entries)
        first_line_fraction = first_line_count / total_count if total_count > 0 else 0
        body_fraction = body_count / total_count if total_count > 0 else 0

        # Score: short words that appear mostly at entry starts
        heading_score = 0

        # Short words (3-5 chars) are more label-like
        if 3 <= word_length <= 5:
            heading_score += 2
        elif word_length <= 7:
            heading_score += 1

        # High initial fraction
        if initial_fraction > 0.05:  # >5% of entries start with this word
            heading_score += 3
        elif initial_fraction > 0.02:
            heading_score += 1

        # High first-line concentration
        if first_line_fraction > 0.7:
            heading_score += 2
        elif first_line_fraction > 0.5:
            heading_score += 1

        # Low body appearance
        if body_fraction < 0.3:
            heading_score += 1

        heading_candidates.append({
            'word': word,
            'length': word_length,
            'initial_count': initial_count,
            'first_line_count': first_line_count,
            'body_count': body_count,
            'initial_fraction': round(initial_fraction, 3),
            'first_line_fraction': round(first_line_fraction, 3),
            'heading_score': heading_score
        })

    # Sort by heading score
    heading_candidates.sort(key=lambda x: -x['heading_score'])

    # Top candidates
    top_20 = heading_candidates[:20]

    # Identify distinct heading vocabulary
    heading_vocab = [h['word'] for h in top_20 if h['heading_score'] >= 3]

    return {
        'total_entries': len(entries),
        'unique_initial_words': len(initial_words),
        'heading_candidates': top_20,
        'high_confidence_headings': heading_vocab,
        'heading_vocabulary_size': len(heading_vocab)
    }


# ============================================================================
# ANALYSIS 4: COMPARISON TO HERBAL STRUCTURE
# ============================================================================

def compare_to_herbal_structure(words: List[Dict]) -> Dict:
    """
    Do A entries show three-part structure like traditional herbals?
    (name -> properties -> uses)
    """
    print("  Comparing to herbal structure...")

    entries = segment_into_entries(words)

    # Analyze position of different prefix types within entries
    # Hypothesis: different prefixes dominate different parts

    prefix_by_third = {'first': Counter(), 'middle': Counter(), 'last': Counter()}

    for entry in entries:
        n = len(entry)
        if n < 9:  # Need at least 9 words for meaningful thirds
            continue

        third_size = n // 3

        # First third
        for w in entry[:third_size]:
            prefix_by_third['first'][get_prefix(w['word'])] += 1

        # Middle third
        for w in entry[third_size:2*third_size]:
            prefix_by_third['middle'][get_prefix(w['word'])] += 1

        # Last third
        for w in entry[2*third_size:]:
            prefix_by_third['last'][get_prefix(w['word'])] += 1

    # Calculate relative enrichment in each third
    third_enrichment = {}

    total_first = sum(prefix_by_third['first'].values())
    total_middle = sum(prefix_by_third['middle'].values())
    total_last = sum(prefix_by_third['last'].values())

    all_prefixes = (set(prefix_by_third['first'].keys()) |
                   set(prefix_by_third['middle'].keys()) |
                   set(prefix_by_third['last'].keys()))

    for prefix in all_prefixes:
        first_rate = prefix_by_third['first'][prefix] / total_first if total_first > 0 else 0
        middle_rate = prefix_by_third['middle'][prefix] / total_middle if total_middle > 0 else 0
        last_rate = prefix_by_third['last'][prefix] / total_last if total_last > 0 else 0

        # Find dominant third
        rates = {'first': first_rate, 'middle': middle_rate, 'last': last_rate}
        max_rate = max(rates.values())
        min_rate = min(rates.values())

        # Only include if there's meaningful variation
        count = (prefix_by_third['first'][prefix] +
                prefix_by_third['middle'][prefix] +
                prefix_by_third['last'][prefix])

        if count >= 30 and max_rate > min_rate * 1.3:
            dominant = max(rates, key=rates.get)
            third_enrichment[prefix] = {
                'first_rate': round(first_rate * 100, 2),
                'middle_rate': round(middle_rate * 100, 2),
                'last_rate': round(last_rate * 100, 2),
                'dominant_third': dominant,
                'count': count
            }

    # Group by dominant third
    first_prefixes = {p: d for p, d in third_enrichment.items() if d['dominant_third'] == 'first'}
    middle_prefixes = {p: d for p, d in third_enrichment.items() if d['dominant_third'] == 'middle'}
    last_prefixes = {p: d for p, d in third_enrichment.items() if d['dominant_third'] == 'last'}

    # Is there a three-part structure?
    has_three_parts = len(first_prefixes) >= 2 and len(middle_prefixes) >= 2 and len(last_prefixes) >= 2

    return {
        'entries_analyzed': len([e for e in entries if len(e) >= 9]),
        'first_third_prefixes': first_prefixes,
        'middle_third_prefixes': middle_prefixes,
        'last_third_prefixes': last_prefixes,
        'three_part_structure_detected': has_three_parts,
        'interpretation': (
            'POSSIBLE three-part structure: different prefixes dominate each third'
            if has_three_parts else
            'NO clear three-part structure detected'
        )
    }


# ============================================================================
# ANALYSIS 5: ILLUSTRATION ALIGNMENT
# ============================================================================

def analyze_illustration_alignment(words: List[Dict]) -> Dict:
    """
    Do entry boundaries correlate with illustration boundaries?
    In Voynich herbals, each folio typically has one plant illustration.
    """
    print("  Analyzing illustration alignment...")

    entries = segment_into_entries(words)

    # Group folios by type based on folio naming convention
    # Voynich folios: f1r, f1v, f2r, f2v... (r=recto, v=verso)
    # Herbal folios are typically in ranges like f1-f66

    folios = [entry[0]['folio'] if entry else '' for entry in entries]

    # Analyze folio patterns
    folio_lengths = [len(entry) for entry in entries]

    # In herbals, each page (folio) should be one entry
    # If entries = folios, that's perfect alignment

    # Check if multiple entries per folio (would suggest sub-entries)
    from collections import Counter
    folio_counts = Counter(folios)
    multi_entry_folios = [f for f, c in folio_counts.items() if c > 1]

    # Calculate page-level statistics
    # Assumption: one illustration per folio in herbal section

    # Group by folio base (without r/v suffix)
    def get_folio_base(folio):
        # Remove r/v suffix if present
        if folio.endswith('r') or folio.endswith('v'):
            return folio[:-1]
        return folio

    folio_bases = Counter(get_folio_base(f) for f in folios)

    # Most common pattern
    entries_per_page = Counter(folio_bases.values())

    # Word count distribution by folio
    folio_word_counts = defaultdict(int)
    for entry in entries:
        if entry:
            folio_word_counts[entry[0]['folio']] += len(entry)

    # Analyze regularity of folio word counts
    counts = list(folio_word_counts.values())
    mean_count = sum(counts) / len(counts) if counts else 0
    variance = sum((c - mean_count) ** 2 for c in counts) / len(counts) if counts else 0
    cv = math.sqrt(variance) / mean_count if mean_count > 0 else 0

    return {
        'total_entries': len(entries),
        'unique_folios': len(set(folios)),
        'entries_equal_folios': len(entries) == len(set(folios)),
        'multi_entry_folios': multi_entry_folios[:10],
        'entries_per_page_distribution': dict(entries_per_page),
        'mean_words_per_folio': round(mean_count, 2),
        'folio_word_count_cv': round(cv, 3),
        'interpretation': (
            'ONE-TO-ONE alignment: each folio is one entry (consistent with one plant per page)'
            if len(entries) == len(set(folios)) else
            f'MIXED alignment: {len(entries)} entries across {len(set(folios))} folios'
        ),
        'herbal_consistency': (
            'HIGH' if cv < 0.5 else
            'MEDIUM' if cv < 0.7 else
            'LOW'
        )
    }


def main():
    print("=" * 70)
    print("CURRIER A DEEP DIVE")
    print("Intensive analysis of Currier A as reference material")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    all_words, by_currier = load_corpus()
    currier_a = by_currier['A']
    print(f"Currier A: {len(currier_a)} words")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Currier A deep dive analysis',
        'word_count': len(currier_a)
    }

    # Run analyses
    print("\nRunning analyses...")
    results['entry_detection'] = analyze_entry_detection(currier_a)
    results['entry_regularity'] = analyze_entry_regularity(currier_a)
    results['label_detection'] = detect_labels_and_headings(currier_a)
    results['herbal_structure'] = compare_to_herbal_structure(currier_a)
    results['illustration_alignment'] = analyze_illustration_alignment(currier_a)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    ed = results['entry_detection']
    print(f"\n1. ENTRY DETECTION:")
    print(f"   Folio count: {ed['folio_count']}")
    print(f"   Mean adjacent overlap: {ed['mean_adjacent_overlap']}")
    print(f"   Sharp boundaries: {ed['sharp_boundary_count']}")

    er = results['entry_regularity']
    print(f"\n2. ENTRY REGULARITY:")
    print(f"   Mean length: {er['length_regularity']['mean_length']} words")
    print(f"   CV (lower = more regular): {er['length_regularity']['cv']}")
    print(f"   Mean lines per entry: {er['line_count_regularity']['mean_lines']}")

    ld = results['label_detection']
    print(f"\n3. LABEL/HEADING DETECTION:")
    print(f"   High-confidence headings: {len(ld['high_confidence_headings'])}")
    if ld['heading_candidates'][:5]:
        print("   Top candidates:")
        for h in ld['heading_candidates'][:5]:
            print(f"      {h['word']}: score={h['heading_score']}, "
                  f"initial={h['initial_count']}, "
                  f"first_line_frac={h['first_line_fraction']}")

    hs = results['herbal_structure']
    print(f"\n4. HERBAL STRUCTURE:")
    print(f"   Three-part structure: {hs['three_part_structure_detected']}")
    print(f"   First-third prefixes: {list(hs['first_third_prefixes'].keys())[:5]}")
    print(f"   Middle-third prefixes: {list(hs['middle_third_prefixes'].keys())[:5]}")
    print(f"   Last-third prefixes: {list(hs['last_third_prefixes'].keys())[:5]}")

    ia = results['illustration_alignment']
    print(f"\n5. ILLUSTRATION ALIGNMENT:")
    print(f"   Entries: {ia['total_entries']}, Folios: {ia['unique_folios']}")
    print(f"   One-to-one: {ia['entries_equal_folios']}")
    print(f"   Herbal consistency: {ia['herbal_consistency']}")

    # Overall assessment
    print("\n" + "=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)

    # Calculate tractability score
    tractability_score = 0
    tractability_notes = []

    # Entry regularity
    if er['length_regularity']['cv'] < 0.6:
        tractability_score += 2
        tractability_notes.append("Good length regularity (CV < 0.6)")
    else:
        tractability_notes.append("Variable entry lengths")

    # Heading candidates
    if len(ld['high_confidence_headings']) >= 5:
        tractability_score += 2
        tractability_notes.append(f"{len(ld['high_confidence_headings'])} candidate headings found")
    elif len(ld['high_confidence_headings']) >= 2:
        tractability_score += 1
        tractability_notes.append(f"{len(ld['high_confidence_headings'])} candidate headings found")

    # Three-part structure
    if hs['three_part_structure_detected']:
        tractability_score += 2
        tractability_notes.append("Three-part structure detected")
    else:
        tractability_notes.append("No clear three-part structure")

    # Illustration alignment
    if ia['entries_equal_folios']:
        tractability_score += 2
        tractability_notes.append("One-to-one folio alignment")
    else:
        tractability_score += 1
        tractability_notes.append("Partial folio alignment")

    # Adjacent folio overlap (low is good - distinct entries)
    if ed['mean_adjacent_overlap'] < 0.15:
        tractability_score += 1
        tractability_notes.append("Low inter-folio vocabulary overlap")

    print(f"\nTractability Score: {tractability_score}/9")
    print("\nAssessment notes:")
    for note in tractability_notes:
        print(f"  - {note}")

    if tractability_score >= 7:
        verdict = "HIGH tractability - Currier A shows regular, herbal-like structure"
    elif tractability_score >= 4:
        verdict = "MEDIUM tractability - Currier A shows some structure but with variability"
    else:
        verdict = "LOW tractability - Currier A structure is irregular"

    print(f"\nVerdict: {verdict}")

    results['overall'] = {
        'tractability_score': tractability_score,
        'max_score': 9,
        'notes': tractability_notes,
        'verdict': verdict
    }

    # Save results
    with open('currier_a_deep_dive_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to currier_a_deep_dive_report.json")


if __name__ == '__main__':
    main()
