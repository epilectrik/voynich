#!/usr/bin/env python3
"""
Currier A/B Separation Analysis

Formal separation of Voynich manuscript into Currier A and B sections
with comprehensive comparison statistics.

NO SEMANTIC CLAIMS - purely structural analysis.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any


def load_corpus() -> List[Dict[str, str]]:
    """Load and deduplicate transcription data."""
    words = []
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        seen = set()

        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            # Extract and clean fields
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')
            section = row.get('section', '').strip().strip('"')
            hand = row.get('hand', '').strip().strip('"')

            # Skip empty words or special markers
            if not word or word.startswith('*') or len(word) < 2:
                continue

            # Deduplicate by word+folio+line (take first transcriber)
            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'currier': currier,
                    'section': section,
                    'hand': hand,
                    'line': line_num
                })

    return words


def split_by_currier(corpus: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Split corpus into Currier A, B, and uncertain."""
    currier_a = [w for w in corpus if w['currier'] == 'A']
    currier_b = [w for w in corpus if w['currier'] == 'B']
    uncertain = [w for w in corpus if w['currier'] not in ('A', 'B')]
    return currier_a, currier_b, uncertain


def basic_statistics(words: List[Dict]) -> Dict[str, Any]:
    """Compute basic statistics for a word list."""
    word_texts = [w['word'] for w in words]
    folios = set(w['folio'] for w in words)

    unique_words = set(word_texts)
    word_lengths = [len(w) for w in word_texts]

    return {
        'total_words': len(word_texts),
        'unique_words': len(unique_words),
        'folio_count': len(folios),
        'avg_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
        'median_word_length': sorted(word_lengths)[len(word_lengths)//2] if word_lengths else 0,
        'words_ending_in_y': sum(1 for w in word_texts if w.endswith('y')),
        'y_ending_percentage': sum(1 for w in word_texts if w.endswith('y')) / len(word_texts) * 100 if word_texts else 0
    }


def vocabulary_overlap(a_words: List[Dict], b_words: List[Dict]) -> Dict[str, Any]:
    """Analyze vocabulary overlap between A and B."""
    vocab_a = set(w['word'] for w in a_words)
    vocab_b = set(w['word'] for w in b_words)

    shared = vocab_a & vocab_b
    only_a = vocab_a - vocab_b
    only_b = vocab_b - vocab_a
    all_unique = vocab_a | vocab_b

    return {
        'shared_vocabulary': len(shared),
        'only_in_a': len(only_a),
        'only_in_b': len(only_b),
        'total_unique': len(all_unique),
        'overlap_percentage': len(shared) / len(all_unique) * 100 if all_unique else 0,
        'a_unique_percentage': len(only_a) / len(vocab_a) * 100 if vocab_a else 0,
        'b_unique_percentage': len(only_b) / len(vocab_b) * 100 if vocab_b else 0,
        'sample_shared': sorted(shared)[:20],
        'sample_only_a': sorted(only_a)[:20],
        'sample_only_b': sorted(only_b)[:20]
    }


def extract_affixes(word: str) -> Tuple[str, str]:
    """Extract first 2 and last 2 characters as prefix/suffix."""
    if len(word) < 2:
        return word, word
    prefix = word[:2]
    suffix = word[-2:]
    return prefix, suffix


def affix_distribution(words: List[Dict]) -> Tuple[Counter, Counter]:
    """Get prefix and suffix frequency distributions."""
    prefixes = Counter()
    suffixes = Counter()

    for w in words:
        word = w['word']
        if len(word) >= 2:
            prefixes[word[:2]] += 1
            suffixes[word[-2:]] += 1

    return prefixes, suffixes


def compute_enrichment(a_dist: Counter, b_dist: Counter) -> List[Dict[str, Any]]:
    """Compute enrichment ratios for items between A and B."""
    a_total = sum(a_dist.values())
    b_total = sum(b_dist.values())

    all_items = set(a_dist.keys()) | set(b_dist.keys())
    enrichments = []

    for item in all_items:
        a_count = a_dist.get(item, 0)
        b_count = b_dist.get(item, 0)

        # Compute rates
        a_rate = a_count / a_total if a_total > 0 else 0
        b_rate = b_count / b_total if b_total > 0 else 0

        # Compute enrichment (with smoothing to avoid division by zero)
        if b_rate > 0 and a_rate > 0:
            a_over_b = a_rate / b_rate
            b_over_a = b_rate / a_rate
        elif a_rate > 0:
            a_over_b = float('inf')
            b_over_a = 0
        elif b_rate > 0:
            a_over_b = 0
            b_over_a = float('inf')
        else:
            a_over_b = 1
            b_over_a = 1

        enrichments.append({
            'item': item,
            'a_count': a_count,
            'b_count': b_count,
            'a_rate': round(a_rate * 100, 3),
            'b_rate': round(b_rate * 100, 3),
            'a_over_b': round(a_over_b, 2) if a_over_b != float('inf') else 'inf',
            'b_over_a': round(b_over_a, 2) if b_over_a != float('inf') else 'inf'
        })

    return sorted(enrichments, key=lambda x: x['a_count'] + x['b_count'], reverse=True)


def chi_square_test(a_dist: Counter, b_dist: Counter) -> Dict[str, float]:
    """Perform chi-square test for distribution difference."""
    all_items = list(set(a_dist.keys()) | set(b_dist.keys()))

    a_total = sum(a_dist.values())
    b_total = sum(b_dist.values())
    grand_total = a_total + b_total

    if grand_total == 0:
        return {'chi_square': 0, 'degrees_of_freedom': 0, 'significant': False}

    chi_sq = 0
    for item in all_items:
        a_obs = a_dist.get(item, 0)
        b_obs = b_dist.get(item, 0)
        row_total = a_obs + b_obs

        a_exp = (row_total * a_total) / grand_total if grand_total > 0 else 0
        b_exp = (row_total * b_total) / grand_total if grand_total > 0 else 0

        if a_exp > 0:
            chi_sq += ((a_obs - a_exp) ** 2) / a_exp
        if b_exp > 0:
            chi_sq += ((b_obs - b_exp) ** 2) / b_exp

    df = len(all_items) - 1

    # Critical values for chi-square at p=0.05
    # For large df, approximate critical value
    critical = df + 2 * math.sqrt(2 * df) if df > 100 else df * 1.5

    return {
        'chi_square': round(chi_sq, 2),
        'degrees_of_freedom': df,
        'significant_at_p05': chi_sq > critical
    }


# Known morpheme patterns from previous analysis (for compositional testing)
KNOWN_PREFIXES = ['qo', 'ch', 'sh', 'da', 'ot', 'ok', 'ol', 'al', 'ar', 'ct', 'so', 'or', 'yk', 'yt', 'lk', 'sa', 'cth']
KNOWN_SUFFIXES = ['y', 'dy', 'ey', 'aiin', 'ain', 'iin', 'in', 'hy', 'ky', 'ar', 'or', 'an']


def test_compositional_structure(words: List[Dict]) -> Dict[str, Any]:
    """Test if PREFIX + MIDDLE + SUFFIX structure holds."""
    results = {
        'total_tested': 0,
        'has_known_prefix': 0,
        'has_known_suffix': 0,
        'has_both': 0,
        'prefix_rate': 0,
        'suffix_rate': 0,
        'both_rate': 0
    }

    for w in words:
        word = w['word']
        if len(word) < 3:
            continue

        results['total_tested'] += 1

        # Check prefix (first 2-3 chars)
        has_prefix = any(word.startswith(p) for p in KNOWN_PREFIXES)

        # Check suffix (last 1-4 chars)
        has_suffix = any(word.endswith(s) for s in KNOWN_SUFFIXES)

        if has_prefix:
            results['has_known_prefix'] += 1
        if has_suffix:
            results['has_known_suffix'] += 1
        if has_prefix and has_suffix:
            results['has_both'] += 1

    if results['total_tested'] > 0:
        results['prefix_rate'] = round(results['has_known_prefix'] / results['total_tested'] * 100, 1)
        results['suffix_rate'] = round(results['has_known_suffix'] / results['total_tested'] * 100, 1)
        results['both_rate'] = round(results['has_both'] / results['total_tested'] * 100, 1)

    return results


def extract_trigram_sequences(words: List[Dict]) -> List[Tuple[str, str, str]]:
    """Extract 3-word sequences within same folio/line context."""
    # Group words by folio and line
    by_context = defaultdict(list)
    for w in words:
        key = (w['folio'], w['line'])
        by_context[key].append(w['word'])

    trigrams = []
    for context, word_list in by_context.items():
        for i in range(len(word_list) - 2):
            trigrams.append((word_list[i], word_list[i+1], word_list[i+2]))

    return trigrams


def analyze_trigram_patterns(trigrams: List[Tuple[str, str, str]]) -> Dict[str, Any]:
    """Analyze 3-word sequence patterns."""
    trigram_counts = Counter(trigrams)

    # Find repeated patterns
    repeated = {t: c for t, c in trigram_counts.items() if c > 1}

    # Analyze position-specific vocabulary
    first_words = Counter(t[0] for t in trigrams)
    middle_words = Counter(t[1] for t in trigrams)
    last_words = Counter(t[2] for t in trigrams)

    return {
        'total_trigrams': len(trigrams),
        'unique_trigrams': len(trigram_counts),
        'repeated_trigrams': len(repeated),
        'repetition_rate': round(len(repeated) / len(trigram_counts) * 100, 1) if trigram_counts else 0,
        'most_common': [{'trigram': ' '.join(t), 'count': c} for t, c in trigram_counts.most_common(10)],
        'top_first_words': first_words.most_common(10),
        'top_middle_words': middle_words.most_common(10),
        'top_last_words': last_words.most_common(10)
    }


def generate_recommendation(a_stats: Dict, b_stats: Dict, overlap: Dict,
                           prefix_chi: Dict, suffix_chi: Dict,
                           a_comp: Dict, b_comp: Dict) -> Dict[str, Any]:
    """Generate recommendation on ONE vs TWO systems."""

    evidence_for_separation = []
    evidence_against_separation = []

    # 1. Vocabulary overlap
    if overlap['overlap_percentage'] < 50:
        evidence_for_separation.append(
            f"Low vocabulary overlap ({overlap['overlap_percentage']:.1f}%) suggests distinct lexicons"
        )
    else:
        evidence_against_separation.append(
            f"High vocabulary overlap ({overlap['overlap_percentage']:.1f}%) suggests shared vocabulary"
        )

    # 2. Statistical difference in affixes
    if prefix_chi['significant_at_p05']:
        evidence_for_separation.append(
            f"Prefix distributions significantly different (chi-sq={prefix_chi['chi_square']})"
        )
    else:
        evidence_against_separation.append(
            "Prefix distributions not significantly different"
        )

    if suffix_chi['significant_at_p05']:
        evidence_for_separation.append(
            f"Suffix distributions significantly different (chi-sq={suffix_chi['chi_square']})"
        )
    else:
        evidence_against_separation.append(
            "Suffix distributions not significantly different"
        )

    # 3. Compositional structure
    a_both = a_comp['both_rate']
    b_both = b_comp['both_rate']
    diff = abs(a_both - b_both)

    if diff > 10:
        evidence_for_separation.append(
            f"Compositional success differs: A={a_both}%, B={b_both}% ({diff:.1f}pp difference)"
        )
    else:
        evidence_against_separation.append(
            f"Similar compositional success: A={a_both}%, B={b_both}%"
        )

    # 4. Word length
    len_diff = abs(a_stats['avg_word_length'] - b_stats['avg_word_length'])
    if len_diff > 0.5:
        evidence_for_separation.append(
            f"Word length differs: A={a_stats['avg_word_length']:.2f}, B={b_stats['avg_word_length']:.2f}"
        )
    else:
        evidence_against_separation.append(
            f"Similar word lengths: A={a_stats['avg_word_length']:.2f}, B={b_stats['avg_word_length']:.2f}"
        )

    # 5. Y-ending rate
    y_diff = abs(a_stats['y_ending_percentage'] - b_stats['y_ending_percentage'])
    if y_diff > 5:
        evidence_for_separation.append(
            f"Y-ending rate differs: A={a_stats['y_ending_percentage']:.1f}%, B={b_stats['y_ending_percentage']:.1f}%"
        )
    else:
        evidence_against_separation.append(
            f"Similar Y-ending rates: A={a_stats['y_ending_percentage']:.1f}%, B={b_stats['y_ending_percentage']:.1f}%"
        )

    # Generate verdict
    for_count = len(evidence_for_separation)
    against_count = len(evidence_against_separation)

    if for_count >= 4:
        verdict = "TWO_SYSTEMS"
        confidence = "HIGH"
        explanation = "Strong evidence for distinct systems: different vocabulary, affixes, and structure"
    elif for_count >= 3:
        verdict = "TWO_SYSTEMS"
        confidence = "MEDIUM"
        explanation = "Moderate evidence for distinct systems: several structural differences"
    elif against_count >= 4:
        verdict = "ONE_SYSTEM"
        confidence = "HIGH"
        explanation = "Strong evidence for unified system: similar vocabulary, affixes, and structure"
    elif against_count >= 3:
        verdict = "ONE_SYSTEM"
        confidence = "MEDIUM"
        explanation = "Moderate evidence for unified system: mostly similar patterns"
    else:
        verdict = "INCONCLUSIVE"
        confidence = "LOW"
        explanation = "Mixed evidence: some differences, some similarities"

    return {
        'verdict': verdict,
        'confidence': confidence,
        'explanation': explanation,
        'evidence_for_separation': evidence_for_separation,
        'evidence_against_separation': evidence_against_separation,
        'score_for': for_count,
        'score_against': against_count
    }


def main():
    print("=" * 70)
    print("CURRIER A/B SEPARATION ANALYSIS")
    print("Formal separation with comprehensive statistics")
    print("NO SEMANTIC CLAIMS - structural analysis only")
    print("=" * 70)
    print()

    # Load and split corpus
    print("Loading corpus...")
    corpus = load_corpus()
    print(f"Total words loaded: {len(corpus)}")

    currier_a, currier_b, uncertain = split_by_currier(corpus)
    print(f"Currier A: {len(currier_a)} words")
    print(f"Currier B: {len(currier_b)} words")
    print(f"Uncertain: {len(uncertain)} words")
    print()

    # Basic statistics
    print("Computing basic statistics...")
    a_stats = basic_statistics(currier_a)
    b_stats = basic_statistics(currier_b)

    print("\n--- BASIC STATISTICS ---")
    print(f"{'Metric':<25} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 55)
    print(f"{'Total words':<25} {a_stats['total_words']:>15,} {b_stats['total_words']:>15,}")
    print(f"{'Unique words':<25} {a_stats['unique_words']:>15,} {b_stats['unique_words']:>15,}")
    print(f"{'Folio count':<25} {a_stats['folio_count']:>15} {b_stats['folio_count']:>15}")
    print(f"{'Avg word length':<25} {a_stats['avg_word_length']:>15.2f} {b_stats['avg_word_length']:>15.2f}")
    print(f"{'Y-ending %':<25} {a_stats['y_ending_percentage']:>14.1f}% {b_stats['y_ending_percentage']:>14.1f}%")
    print()

    # Vocabulary overlap
    print("Analyzing vocabulary overlap...")
    overlap = vocabulary_overlap(currier_a, currier_b)

    print("\n--- VOCABULARY OVERLAP ---")
    print(f"Shared vocabulary: {overlap['shared_vocabulary']} words")
    print(f"Only in A: {overlap['only_in_a']} words ({overlap['a_unique_percentage']:.1f}% of A)")
    print(f"Only in B: {overlap['only_in_b']} words ({overlap['b_unique_percentage']:.1f}% of B)")
    print(f"Overlap: {overlap['overlap_percentage']:.1f}%")
    print()

    # Prefix/suffix analysis
    print("Analyzing prefix distributions...")
    a_prefixes, a_suffixes = affix_distribution(currier_a)
    b_prefixes, b_suffixes = affix_distribution(currier_b)

    prefix_enrichment = compute_enrichment(a_prefixes, b_prefixes)
    suffix_enrichment = compute_enrichment(a_suffixes, b_suffixes)

    prefix_chi = chi_square_test(a_prefixes, b_prefixes)
    suffix_chi = chi_square_test(a_suffixes, b_suffixes)

    print("\n--- PREFIX ANALYSIS ---")
    print(f"Chi-square: {prefix_chi['chi_square']} (df={prefix_chi['degrees_of_freedom']})")
    print(f"Significant difference: {prefix_chi['significant_at_p05']}")
    print("\nTop prefixes enriched in A (A/B ratio):")
    a_enriched = [p for p in prefix_enrichment if p['a_count'] >= 50 and
                  (isinstance(p['a_over_b'], (int, float)) and p['a_over_b'] >= 1.5)]
    for p in a_enriched[:5]:
        print(f"  {p['item']}: {p['a_count']} in A, {p['b_count']} in B, ratio {p['a_over_b']}x")

    print("\nTop prefixes enriched in B (B/A ratio):")
    b_enriched = [p for p in prefix_enrichment if p['b_count'] >= 50 and
                  (isinstance(p['b_over_a'], (int, float)) and p['b_over_a'] >= 1.5)]
    for p in b_enriched[:5]:
        print(f"  {p['item']}: {p['a_count']} in A, {p['b_count']} in B, ratio {p['b_over_a']}x")
    print()

    print("\n--- SUFFIX ANALYSIS ---")
    print(f"Chi-square: {suffix_chi['chi_square']} (df={suffix_chi['degrees_of_freedom']})")
    print(f"Significant difference: {suffix_chi['significant_at_p05']}")
    print()

    # Compositional structure test
    print("Testing compositional structure...")
    a_comp = test_compositional_structure(currier_a)
    b_comp = test_compositional_structure(currier_b)

    print("\n--- COMPOSITIONAL STRUCTURE ---")
    print(f"{'Metric':<30} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 60)
    print(f"{'Words with known prefix':<30} {a_comp['prefix_rate']:>14.1f}% {b_comp['prefix_rate']:>14.1f}%")
    print(f"{'Words with known suffix':<30} {a_comp['suffix_rate']:>14.1f}% {b_comp['suffix_rate']:>14.1f}%")
    print(f"{'Words with both':<30} {a_comp['both_rate']:>14.1f}% {b_comp['both_rate']:>14.1f}%")
    print()

    # Trigram pattern analysis
    print("Analyzing sequence patterns...")
    a_trigrams = extract_trigram_sequences(currier_a)
    b_trigrams = extract_trigram_sequences(currier_b)

    a_patterns = analyze_trigram_patterns(a_trigrams)
    b_patterns = analyze_trigram_patterns(b_trigrams)

    print("\n--- SEQUENCE PATTERNS ---")
    print(f"{'Metric':<30} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 60)
    print(f"{'Total 3-word sequences':<30} {a_patterns['total_trigrams']:>15,} {b_patterns['total_trigrams']:>15,}")
    print(f"{'Unique sequences':<30} {a_patterns['unique_trigrams']:>15,} {b_patterns['unique_trigrams']:>15,}")
    print(f"{'Repeated sequences':<30} {a_patterns['repeated_trigrams']:>15,} {b_patterns['repeated_trigrams']:>15,}")
    print(f"{'Repetition rate':<30} {a_patterns['repetition_rate']:>14.1f}% {b_patterns['repetition_rate']:>14.1f}%")
    print()

    # Generate recommendation
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    recommendation = generate_recommendation(
        a_stats, b_stats, overlap,
        prefix_chi, suffix_chi,
        a_comp, b_comp
    )

    print(f"\nVERDICT: {recommendation['verdict']}")
    print(f"CONFIDENCE: {recommendation['confidence']}")
    print(f"\nExplanation: {recommendation['explanation']}")

    print(f"\nEvidence FOR separation ({recommendation['score_for']} points):")
    for e in recommendation['evidence_for_separation']:
        print(f"  + {e}")

    print(f"\nEvidence AGAINST separation ({recommendation['score_against']} points):")
    for e in recommendation['evidence_against_separation']:
        print(f"  - {e}")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Formal Currier A/B separation - NO SEMANTIC CLAIMS',
        'summary': {
            'currier_a_words': len(currier_a),
            'currier_b_words': len(currier_b),
            'uncertain_words': len(uncertain)
        },
        'basic_statistics': {
            'currier_a': a_stats,
            'currier_b': b_stats
        },
        'vocabulary_overlap': overlap,
        'prefix_analysis': {
            'chi_square_test': prefix_chi,
            'top_20_enrichment': prefix_enrichment[:20]
        },
        'suffix_analysis': {
            'chi_square_test': suffix_chi,
            'top_20_enrichment': suffix_enrichment[:20]
        },
        'compositional_structure': {
            'currier_a': a_comp,
            'currier_b': b_comp
        },
        'sequence_patterns': {
            'currier_a': a_patterns,
            'currier_b': b_patterns
        },
        'recommendation': recommendation
    }

    with open('currier_ab_separation_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to currier_ab_separation_report.json")


if __name__ == '__main__':
    main()
