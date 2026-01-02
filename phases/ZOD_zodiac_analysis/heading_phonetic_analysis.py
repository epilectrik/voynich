#!/usr/bin/env python3
"""
Phase 18, Task 5: Heading Word Phonetic Structure Analysis

Analyzes heading words for internal phonetic regularities WITHOUT attempting
to match external plant names. This is structural analysis only.

Focus areas:
- Length distribution
- Character frequency (headings vs body)
- Compositional analysis (PREFIX + MIDDLE + SUFFIX)
- Spelling consistency
- Cross-entry patterns

CRITICAL: NO external plant name matching. Internal analysis only.

Output: heading_phonetic_analysis_report.json
"""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'pa', 'py', 'ky', 'ty', 'fa', 'fs', 'ks'
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
    """Load the full corpus."""
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

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier
                })

    return words


def segment_by_folio(corpus: List[Dict], currier: str) -> Dict[str, List[Dict]]:
    """Segment corpus by folio for given Currier language."""
    entries = defaultdict(list)
    for w in corpus:
        if w['currier'] == currier:
            entries[w['folio']].append(w)

    return {f: e for f, e in entries.items() if len(e) >= MIN_ENTRY_WORDS}


# =============================================================================
# AFFIX EXTRACTION
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


def decompose_word(word: str) -> Dict:
    """Decompose word into PREFIX + MIDDLE + SUFFIX."""
    prefix = get_prefix(word)
    suffix = get_suffix(word)

    # Get middle portion
    prefix_len = len(prefix) if prefix in KNOWN_PREFIXES else 2
    suffix_len = len(suffix) if suffix in KNOWN_SUFFIXES else 2

    if len(word) > prefix_len + suffix_len:
        middle = word[prefix_len:-suffix_len]
    else:
        middle = ''

    return {
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'follows_grammar': (
            prefix in KNOWN_PREFIXES and
            suffix in KNOWN_SUFFIXES
        )
    }


# =============================================================================
# HEADING EXTRACTION
# =============================================================================

def extract_heading_words(entries: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
    """
    Extract heading words (first word of each entry) and categorize.

    Returns mapping of folio -> heading word
    """
    headings = {}
    for folio, entry in entries.items():
        if entry:
            headings[folio] = entry[0]['word']
    return headings


def get_body_words(entries: Dict[str, List[Dict]]) -> List[str]:
    """Extract all non-heading words (body text)."""
    body = []
    for folio, entry in entries.items():
        if len(entry) > 1:
            body.extend([w['word'] for w in entry[1:]])
    return body


# =============================================================================
# STRUCTURAL PATTERNS ANALYSIS
# =============================================================================

def analyze_length_distribution(headings: List[str], body_words: List[str]) -> Dict:
    """Analyze length distribution of headings vs body words."""
    heading_lengths = [len(h) for h in headings]
    body_lengths = [len(w) for w in body_words]

    return {
        'headings': {
            'mean': round(np.mean(heading_lengths), 2),
            'std': round(np.std(heading_lengths), 2),
            'min': min(heading_lengths),
            'max': max(heading_lengths),
            'median': round(np.median(heading_lengths), 2),
            'mode': Counter(heading_lengths).most_common(1)[0][0]
        },
        'body': {
            'mean': round(np.mean(body_lengths), 2),
            'std': round(np.std(body_lengths), 2),
            'min': min(body_lengths),
            'max': max(body_lengths),
            'median': round(np.median(body_lengths), 2),
            'mode': Counter(body_lengths).most_common(1)[0][0]
        },
        'comparison': {
            'heading_longer': round(np.mean(heading_lengths), 2) > round(np.mean(body_lengths), 2),
            'length_difference': round(np.mean(heading_lengths) - np.mean(body_lengths), 2)
        }
    }


def analyze_character_frequency(headings: List[str], body_words: List[str]) -> Dict:
    """Compare character frequency between headings and body words."""
    heading_chars = Counter(''.join(headings))
    body_chars = Counter(''.join(body_words))

    # Normalize
    heading_total = sum(heading_chars.values())
    body_total = sum(body_chars.values())

    heading_freq = {c: count/heading_total for c, count in heading_chars.items()}
    body_freq = {c: count/body_total for c, count in body_chars.items()}

    # Find characters enriched in headings
    all_chars = set(heading_chars.keys()) | set(body_chars.keys())

    enriched_in_headings = []
    enriched_in_body = []

    for c in all_chars:
        h_freq = heading_freq.get(c, 0)
        b_freq = body_freq.get(c, 0)

        if b_freq > 0:
            ratio = h_freq / b_freq
        elif h_freq > 0:
            ratio = float('inf')
        else:
            ratio = 1.0

        if ratio > 1.5 and h_freq > 0.01:
            enriched_in_headings.append({
                'char': c,
                'heading_freq': round(h_freq, 4),
                'body_freq': round(b_freq, 4),
                'ratio': round(ratio, 2) if ratio != float('inf') else 'inf'
            })
        elif ratio < 0.67 and b_freq > 0.01:
            enriched_in_body.append({
                'char': c,
                'heading_freq': round(h_freq, 4),
                'body_freq': round(b_freq, 4),
                'ratio': round(ratio, 2)
            })

    return {
        'heading_char_counts': dict(heading_chars.most_common(20)),
        'body_char_counts': dict(body_chars.most_common(20)),
        'enriched_in_headings': sorted(enriched_in_headings,
                                        key=lambda x: x['ratio'] if x['ratio'] != 'inf' else 999,
                                        reverse=True)[:10],
        'enriched_in_body': sorted(enriched_in_body,
                                   key=lambda x: x['ratio'])[:10]
    }


# =============================================================================
# COMPOSITIONAL ANALYSIS
# =============================================================================

def analyze_heading_composition(headings: List[str], body_words: List[str]) -> Dict:
    """Analyze PREFIX + MIDDLE + SUFFIX composition of headings vs body."""
    heading_decomp = [decompose_word(h) for h in headings]
    body_decomp = [decompose_word(w) for w in body_words[:5000]]  # Sample

    # Prefix distribution
    heading_prefixes = Counter(d['prefix'] for d in heading_decomp)
    body_prefixes = Counter(d['prefix'] for d in body_decomp)

    # Suffix distribution
    heading_suffixes = Counter(d['suffix'] for d in heading_decomp)
    body_suffixes = Counter(d['suffix'] for d in body_decomp)

    # Grammar compliance
    heading_follows_grammar = sum(1 for d in heading_decomp if d['follows_grammar'])
    body_follows_grammar = sum(1 for d in body_decomp if d['follows_grammar'])

    # Find heading-specific affixes
    heading_only_prefixes = set(heading_prefixes.keys()) - set(body_prefixes.keys())
    heading_only_suffixes = set(heading_suffixes.keys()) - set(body_suffixes.keys())

    # Enriched prefixes in headings
    heading_total = len(heading_decomp)
    body_total = len(body_decomp)

    prefix_enrichment = []
    for prefix in set(heading_prefixes.keys()) | set(body_prefixes.keys()):
        h_rate = heading_prefixes.get(prefix, 0) / heading_total if heading_total else 0
        b_rate = body_prefixes.get(prefix, 0) / body_total if body_total else 0

        if b_rate > 0:
            ratio = h_rate / b_rate
        elif h_rate > 0:
            ratio = float('inf')
        else:
            ratio = 1.0

        if ratio > 1.5 and heading_prefixes.get(prefix, 0) >= 2:
            prefix_enrichment.append({
                'prefix': prefix,
                'heading_count': heading_prefixes.get(prefix, 0),
                'heading_rate': round(h_rate, 4),
                'body_rate': round(b_rate, 4),
                'enrichment_ratio': round(ratio, 2) if ratio != float('inf') else 'inf'
            })

    return {
        'prefix_distribution': {
            'headings': dict(heading_prefixes.most_common(15)),
            'body': dict(body_prefixes.most_common(15))
        },
        'suffix_distribution': {
            'headings': dict(heading_suffixes.most_common(15)),
            'body': dict(body_suffixes.most_common(15))
        },
        'grammar_compliance': {
            'headings_following_grammar': heading_follows_grammar,
            'headings_total': len(heading_decomp),
            'headings_rate': round(heading_follows_grammar / len(heading_decomp), 3) if heading_decomp else 0,
            'body_following_grammar': body_follows_grammar,
            'body_total': len(body_decomp),
            'body_rate': round(body_follows_grammar / len(body_decomp), 3) if body_decomp else 0
        },
        'heading_only_affixes': {
            'prefixes': list(heading_only_prefixes)[:10],
            'suffixes': list(heading_only_suffixes)[:10]
        },
        'prefix_enrichment_in_headings': sorted(
            prefix_enrichment,
            key=lambda x: x['enrichment_ratio'] if x['enrichment_ratio'] != 'inf' else 999,
            reverse=True
        )[:10]
    }


# =============================================================================
# SPELLING CONSISTENCY
# =============================================================================

def analyze_spelling_consistency(entries: Dict[str, List[Dict]]) -> Dict:
    """
    Analyze spelling consistency of headings across the corpus.

    If the same heading appears in multiple entries, are they spelled identically?
    """
    headings = extract_heading_words(entries)
    heading_list = list(headings.values())

    # Find repeated headings
    heading_counts = Counter(heading_list)
    repeated = {h: c for h, c in heading_counts.items() if c > 1}

    # Find near-duplicates (edit distance 1)
    near_duplicates = []

    def edit_distance_1(w1, w2):
        """Check if words differ by exactly one character."""
        if abs(len(w1) - len(w2)) > 1:
            return False

        if len(w1) == len(w2):
            # Substitution
            diffs = sum(1 for a, b in zip(w1, w2) if a != b)
            return diffs == 1
        else:
            # Insertion/deletion
            longer, shorter = (w1, w2) if len(w1) > len(w2) else (w2, w1)
            i = j = 0
            diffs = 0
            while i < len(longer) and j < len(shorter):
                if longer[i] != shorter[j]:
                    diffs += 1
                    i += 1
                else:
                    i += 1
                    j += 1
            return diffs <= 1

    unique_headings = list(set(heading_list))
    for i, h1 in enumerate(unique_headings):
        for h2 in unique_headings[i+1:]:
            if edit_distance_1(h1, h2):
                near_duplicates.append({
                    'word1': h1,
                    'word2': h2,
                    'count1': heading_counts[h1],
                    'count2': heading_counts[h2]
                })

    return {
        'unique_headings': len(set(heading_list)),
        'total_entries': len(heading_list),
        'repeated_headings': repeated,
        'repeated_count': len(repeated),
        'uniqueness_rate': round(len(set(heading_list)) / len(heading_list), 3) if heading_list else 0,
        'near_duplicates_edit_distance_1': near_duplicates[:20],
        'interpretation': (
            'HIGH_CONSISTENCY' if len(near_duplicates) < 5 else
            'MODERATE_VARIATION' if len(near_duplicates) < 15 else
            'HIGH_VARIATION'
        )
    }


# =============================================================================
# CROSS-ENTRY PATTERNS
# =============================================================================

def analyze_cross_entry_patterns(entries: Dict[str, List[Dict]]) -> Dict:
    """
    Analyze if entries with similar headings have similar vocabulary.

    This tests for taxonomic/organizational encoding.
    """
    headings = extract_heading_words(entries)

    # Group entries by heading prefix
    by_prefix = defaultdict(list)
    for folio, heading in headings.items():
        prefix = get_prefix(heading)
        by_prefix[prefix].append(folio)

    # For prefixes with 2+ entries, compare vocabulary
    prefix_vocab_similarity = {}

    for prefix, folios in by_prefix.items():
        if len(folios) < 2:
            continue

        # Get vocabulary for each entry
        vocabs = []
        for folio in folios:
            vocab = set(w['word'] for w in entries[folio])
            vocabs.append(vocab)

        # Compute pairwise Jaccard similarity
        similarities = []
        for i in range(len(vocabs)):
            for j in range(i+1, len(vocabs)):
                intersection = len(vocabs[i] & vocabs[j])
                union = len(vocabs[i] | vocabs[j])
                if union > 0:
                    similarities.append(intersection / union)

        if similarities:
            prefix_vocab_similarity[prefix] = {
                'n_entries': len(folios),
                'mean_jaccard': round(np.mean(similarities), 4),
                'max_jaccard': round(max(similarities), 4),
                'folios': folios[:5]
            }

    # Sort by vocabulary similarity
    sorted_prefixes = sorted(
        prefix_vocab_similarity.items(),
        key=lambda x: x[1]['mean_jaccard'],
        reverse=True
    )

    return {
        'prefixes_with_multiple_entries': len(prefix_vocab_similarity),
        'high_similarity_prefixes': [
            {'prefix': p, **data}
            for p, data in sorted_prefixes[:10]
            if data['mean_jaccard'] > 0.15
        ],
        'low_similarity_prefixes': [
            {'prefix': p, **data}
            for p, data in sorted_prefixes[-10:]
            if data['mean_jaccard'] < 0.1
        ],
        'interpretation': (
            'Some heading prefixes show taxonomic clustering (similar vocabulary)'
            if any(d['mean_jaccard'] > 0.2 for _, d in sorted_prefixes) else
            'No strong taxonomic clustering detected'
        )
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 18, Task 5: Heading Phonetic Structure Analysis")
    print("=" * 70)
    print("\nNOTE: Internal analysis only. NO external plant name matching.")

    # Load corpus
    print("\n[1/7] Loading corpus...")
    corpus = load_corpus()

    print("\n[2/7] Segmenting into entries...")
    a_entries = segment_by_folio(corpus, 'A')
    print(f"  Currier A: {len(a_entries)} entries")

    # Extract headings and body
    print("\n[3/7] Extracting headings and body words...")
    headings = extract_heading_words(a_entries)
    heading_list = list(headings.values())
    body_words = get_body_words(a_entries)
    print(f"  Headings: {len(heading_list)}")
    print(f"  Body words: {len(body_words)}")

    # Length analysis
    print("\n[4/7] Analyzing length distribution...")
    length_analysis = analyze_length_distribution(heading_list, body_words)

    # Character frequency
    print("\n[5/7] Analyzing character frequency...")
    char_analysis = analyze_character_frequency(heading_list, body_words)

    # Compositional analysis
    print("\n[6/7] Analyzing composition (PREFIX + MIDDLE + SUFFIX)...")
    composition_analysis = analyze_heading_composition(heading_list, body_words)

    # Spelling consistency
    print("\n[7/7] Analyzing spelling consistency and cross-entry patterns...")
    spelling_analysis = analyze_spelling_consistency(a_entries)
    cross_entry_analysis = analyze_cross_entry_patterns(a_entries)

    # Compile results
    results = {
        'metadata': {
            'title': 'Heading Word Phonetic Structure Analysis',
            'phase': 'Phase 18, Task 5',
            'date': datetime.now().isoformat(),
            'purpose': 'Internal structural analysis of heading words (NO external matching)',
            'n_entries_analyzed': len(a_entries),
            'n_headings': len(heading_list),
            'n_body_words': len(body_words)
        },

        'length_distribution': length_analysis,
        'character_frequency': char_analysis,
        'compositional_analysis': composition_analysis,
        'spelling_consistency': spelling_analysis,
        'cross_entry_patterns': cross_entry_analysis,

        'key_findings': {
            'heading_mean_length': length_analysis['headings']['mean'],
            'body_mean_length': length_analysis['body']['mean'],
            'headings_longer_than_body': length_analysis['comparison']['heading_longer'],
            'heading_grammar_compliance': composition_analysis['grammar_compliance']['headings_rate'],
            'body_grammar_compliance': composition_analysis['grammar_compliance']['body_rate'],
            'spelling_uniqueness': spelling_analysis['uniqueness_rate'],
            'near_duplicate_count': len(spelling_analysis['near_duplicates_edit_distance_1']),
            'taxonomic_clustering': cross_entry_analysis['interpretation']
        },

        'constraints': [
            f"Headings average {length_analysis['headings']['mean']} chars (body: {length_analysis['body']['mean']})",
            f"Heading grammar compliance: {composition_analysis['grammar_compliance']['headings_rate']*100:.1f}%",
            f"Heading uniqueness: {spelling_analysis['uniqueness_rate']*100:.1f}% unique",
            f"Spelling variation: {spelling_analysis['interpretation']}",
            cross_entry_analysis['interpretation']
        ]
    }

    # Convert numpy types for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(i) for i in obj]
        return obj

    results = convert_for_json(results)

    # Save
    with open('heading_phonetic_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nLength Distribution:")
    print(f"  Headings: mean={length_analysis['headings']['mean']}, "
          f"range={length_analysis['headings']['min']}-{length_analysis['headings']['max']}")
    print(f"  Body: mean={length_analysis['body']['mean']}, "
          f"range={length_analysis['body']['min']}-{length_analysis['body']['max']}")
    print(f"  Headings are {'LONGER' if length_analysis['comparison']['heading_longer'] else 'SHORTER'} than body")

    print(f"\nGrammar Compliance (PREFIX + MIDDLE + SUFFIX):")
    print(f"  Headings: {composition_analysis['grammar_compliance']['headings_rate']*100:.1f}%")
    print(f"  Body: {composition_analysis['grammar_compliance']['body_rate']*100:.1f}%")

    print(f"\nTop Prefixes in Headings:")
    for prefix, count in list(composition_analysis['prefix_distribution']['headings'].items())[:5]:
        print(f"  {prefix}: {count}")

    print(f"\nSpelling Consistency:")
    print(f"  Unique headings: {spelling_analysis['uniqueness_rate']*100:.1f}%")
    print(f"  Near-duplicates (edit distance 1): {len(spelling_analysis['near_duplicates_edit_distance_1'])}")

    print(f"\nCross-Entry Patterns:")
    print(f"  {cross_entry_analysis['interpretation']}")

    print(f"\nSaved to: heading_phonetic_analysis_report.json")

    return results


if __name__ == '__main__':
    main()
