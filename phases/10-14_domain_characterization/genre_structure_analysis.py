#!/usr/bin/env python3
"""
Genre Structure Analysis

Analyze structural patterns in Voynich text and compare to genre predictions.
NO SEMANTIC CLAIMS - purely structural pattern analysis.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any


# Genre prediction profiles (based on text structure, not content)
GENRE_PROFILES = {
    'MEDICAL_RECIPES': {
        'description': 'Medieval medical/pharmaceutical recipes',
        'procedure_length': (3, 7),        # Short procedures
        'repetition_rate': (0.15, 0.40),   # High repetition
        'position_entropy': (0.5, 2.0),    # Low entropy (stereotyped)
        'vocabulary_reuse': (3, 10),       # Moderate reuse
        'typical_pattern': 'Ingredient -> Process -> Application'
    },
    'NARRATIVE': {
        'description': 'Narrative prose text',
        'procedure_length': (10, 30),      # Variable, longer
        'repetition_rate': (0.01, 0.10),   # Low repetition
        'position_entropy': (2.5, 4.0),    # High entropy
        'vocabulary_reuse': (1, 3),        # Low reuse
        'typical_pattern': 'Variable ordering, few stereotypes'
    },
    'ASTRONOMICAL_TABLES': {
        'description': 'Astronomical/calendrical tables',
        'procedure_length': (1, 4),        # Very short entries
        'repetition_rate': (0.40, 0.80),   # Very high repetition
        'position_entropy': (0.1, 1.0),    # Very low entropy
        'vocabulary_reuse': (5, 20),       # High reuse
        'typical_pattern': 'Listing, enumeration, fixed format'
    },
    'LITURGICAL': {
        'description': 'Religious/liturgical formulae',
        'procedure_length': (5, 15),       # Medium length
        'repetition_rate': (0.30, 0.60),   # Very high repetition
        'position_entropy': (0.5, 1.5),    # Low entropy
        'vocabulary_reuse': (5, 15),       # High reuse
        'typical_pattern': 'Fixed formulaic phrases, invocations'
    }
}


def load_corpus() -> List[Dict]:
    """Load corpus with line-level structure."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []

    seen = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H (PRIMARY) transcriber track only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')
            par_initial = row.get('par_initial', '').strip().strip('"')
            par_final = row.get('par_final', '').strip().strip('"')

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
                    'is_par_initial': par_initial not in ('', 'NA'),
                    'is_par_final': par_final not in ('', 'NA')
                })

    return words


def split_by_currier(corpus: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Split corpus into Currier A and B."""
    currier_a = [w for w in corpus if w['currier'] == 'A']
    currier_b = [w for w in corpus if w['currier'] == 'B']
    return currier_a, currier_b


def extract_line_sequences(corpus: List[Dict]) -> List[List[str]]:
    """Extract word sequences by line (approximating procedures)."""
    # Group words by folio+line
    by_line = defaultdict(list)
    for w in corpus:
        key = (w['folio'], w['line'])
        by_line[key].append(w['word'])

    return list(by_line.values())


def extract_paragraph_sequences(corpus: List[Dict]) -> List[List[str]]:
    """Extract word sequences by paragraph."""
    # Use paragraph markers to split
    paragraphs = []
    current_para = []

    for w in corpus:
        if w['is_par_initial'] and current_para:
            paragraphs.append(current_para)
            current_para = []
        current_para.append(w['word'])

    if current_para:
        paragraphs.append(current_para)

    return paragraphs


def compute_sequence_length_stats(sequences: List[List[str]]) -> Dict:
    """Compute statistics on sequence lengths."""
    lengths = [len(seq) for seq in sequences if seq]

    if not lengths:
        return {'mean': 0, 'median': 0, 'std': 0, 'min': 0, 'max': 0}

    mean_len = sum(lengths) / len(lengths)
    sorted_lengths = sorted(lengths)
    median_len = sorted_lengths[len(lengths) // 2]

    variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
    std_len = math.sqrt(variance)

    return {
        'mean': round(mean_len, 2),
        'median': median_len,
        'std': round(std_len, 2),
        'min': min(lengths),
        'max': max(lengths),
        'count': len(lengths)
    }


def compute_repetition_rate(sequences: List[List[str]]) -> Dict:
    """Compute how often sequences (3-grams) repeat."""
    # Extract all 3-word sequences
    trigrams = []
    for seq in sequences:
        for i in range(len(seq) - 2):
            trigrams.append(tuple(seq[i:i+3]))

    if not trigrams:
        return {'total': 0, 'unique': 0, 'repeated': 0, 'rate': 0}

    trigram_counts = Counter(trigrams)
    repeated = sum(1 for t, c in trigram_counts.items() if c > 1)

    # Also compute exact duplicate rate
    total_trigrams = len(trigrams)
    unique_trigrams = len(trigram_counts)

    # Duplicate proportion: how many trigram instances are duplicates
    duplicate_instances = total_trigrams - unique_trigrams
    duplicate_rate = duplicate_instances / total_trigrams if total_trigrams > 0 else 0

    return {
        'total_trigrams': total_trigrams,
        'unique_trigrams': unique_trigrams,
        'repeated_patterns': repeated,
        'repetition_rate': round(repeated / len(trigram_counts), 3) if trigram_counts else 0,
        'duplicate_instance_rate': round(duplicate_rate, 3),
        'most_repeated': [
            {'pattern': ' '.join(t), 'count': c}
            for t, c in trigram_counts.most_common(10) if c > 1
        ]
    }


def compute_entropy(counts: Counter) -> float:
    """Compute Shannon entropy from frequency counts."""
    total = sum(counts.values())
    if total == 0:
        return 0

    entropy = 0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def compute_position_entropy(sequences: List[List[str]]) -> Dict:
    """Compute entropy of words by position (first, middle, last)."""
    first_words = Counter()
    middle_words = Counter()
    last_words = Counter()

    for seq in sequences:
        if len(seq) >= 1:
            first_words[seq[0]] += 1
        if len(seq) >= 2:
            last_words[seq[-1]] += 1
        if len(seq) >= 3:
            for w in seq[1:-1]:
                middle_words[w] += 1

    first_entropy = compute_entropy(first_words)
    middle_entropy = compute_entropy(middle_words)
    last_entropy = compute_entropy(last_words)

    return {
        'first_position_entropy': round(first_entropy, 2),
        'middle_position_entropy': round(middle_entropy, 2),
        'last_position_entropy': round(last_entropy, 2),
        'average_entropy': round((first_entropy + last_entropy) / 2, 2),
        'top_first_words': first_words.most_common(10),
        'top_last_words': last_words.most_common(10)
    }


def compute_vocabulary_reuse(corpus: List[Dict]) -> Dict:
    """Compute how many different contexts each word appears in."""
    word_contexts = defaultdict(set)

    for w in corpus:
        context = (w['folio'], w['line'])
        word_contexts[w['word']].add(context)

    context_counts = [len(contexts) for contexts in word_contexts.values()]

    if not context_counts:
        return {'mean_contexts': 0, 'max_contexts': 0}

    # Words appearing in multiple contexts
    multi_context = sum(1 for c in context_counts if c > 1)

    return {
        'unique_words': len(word_contexts),
        'words_in_multi_contexts': multi_context,
        'multi_context_rate': round(multi_context / len(word_contexts), 3),
        'mean_contexts_per_word': round(sum(context_counts) / len(context_counts), 2),
        'max_contexts': max(context_counts),
        'most_reused': sorted(
            [(w, len(c)) for w, c in word_contexts.items()],
            key=lambda x: -x[1]
        )[:10]
    }


def score_genre_fit(measured: Dict, profile: Dict) -> float:
    """Score how well measured features fit a genre profile."""
    score = 0
    max_score = 4  # 4 features

    # Procedure length fit
    mean_len = measured['sequence_stats']['mean']
    len_range = profile['procedure_length']
    if len_range[0] <= mean_len <= len_range[1]:
        score += 1
    elif len_range[0] - 2 <= mean_len <= len_range[1] + 2:
        score += 0.5

    # Repetition rate fit
    rep_rate = measured['repetition']['repetition_rate']
    rep_range = profile['repetition_rate']
    if rep_range[0] <= rep_rate <= rep_range[1]:
        score += 1
    elif rep_range[0] - 0.1 <= rep_rate <= rep_range[1] + 0.1:
        score += 0.5

    # Position entropy fit
    avg_entropy = measured['position_entropy']['average_entropy']
    entropy_range = profile['position_entropy']
    if entropy_range[0] <= avg_entropy <= entropy_range[1]:
        score += 1
    elif entropy_range[0] - 0.5 <= avg_entropy <= entropy_range[1] + 0.5:
        score += 0.5

    # Vocabulary reuse fit
    mean_reuse = measured['vocabulary_reuse']['mean_contexts_per_word']
    reuse_range = profile['vocabulary_reuse']
    if reuse_range[0] <= mean_reuse <= reuse_range[1]:
        score += 1
    elif reuse_range[0] - 1 <= mean_reuse <= reuse_range[1] + 1:
        score += 0.5

    return round(score / max_score * 100, 1)


def analyze_section(corpus: List[Dict], name: str) -> Dict:
    """Perform full structural analysis on a corpus section."""
    print(f"\nAnalyzing {name} ({len(corpus)} words)...")

    # Extract sequences
    line_sequences = extract_line_sequences(corpus)
    para_sequences = extract_paragraph_sequences(corpus)

    # Compute metrics using line sequences (more granular)
    seq_stats = compute_sequence_length_stats(line_sequences)
    repetition = compute_repetition_rate(line_sequences)
    position_entropy = compute_position_entropy(line_sequences)
    vocab_reuse = compute_vocabulary_reuse(corpus)

    measured = {
        'sequence_stats': seq_stats,
        'repetition': repetition,
        'position_entropy': position_entropy,
        'vocabulary_reuse': vocab_reuse
    }

    # Score against each genre
    genre_scores = {}
    for genre, profile in GENRE_PROFILES.items():
        genre_scores[genre] = score_genre_fit(measured, profile)

    # Find best fit
    best_genre = max(genre_scores, key=genre_scores.get)

    return {
        'name': name,
        'word_count': len(corpus),
        'line_count': len(line_sequences),
        'paragraph_count': len(para_sequences),
        'measured_features': measured,
        'genre_scores': genre_scores,
        'best_fit_genre': best_genre,
        'best_fit_score': genre_scores[best_genre]
    }


def main():
    print("=" * 70)
    print("GENRE STRUCTURE ANALYSIS")
    print("Compare structural patterns to genre predictions")
    print("NO SEMANTIC CLAIMS - purely structural pattern analysis")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    corpus = load_corpus()
    print(f"Total words: {len(corpus)}")

    # Split by Currier
    currier_a, currier_b = split_by_currier(corpus)
    print(f"Currier A: {len(currier_a)} words")
    print(f"Currier B: {len(currier_b)} words")

    # Analyze each section
    results = {}

    print("\n" + "=" * 50)
    print("CURRIER A ANALYSIS")
    print("=" * 50)
    results['currier_a'] = analyze_section(currier_a, 'Currier A')

    print("\n" + "=" * 50)
    print("CURRIER B ANALYSIS")
    print("=" * 50)
    results['currier_b'] = analyze_section(currier_b, 'Currier B')

    # Print results
    print("\n" + "=" * 70)
    print("MEASURED FEATURES")
    print("=" * 70)

    for section in ['currier_a', 'currier_b']:
        r = results[section]
        print(f"\n--- {r['name']} ---")
        print(f"  Sequence length (mean): {r['measured_features']['sequence_stats']['mean']}")
        print(f"  Repetition rate: {r['measured_features']['repetition']['repetition_rate']}")
        print(f"  Position entropy (avg): {r['measured_features']['position_entropy']['average_entropy']}")
        print(f"  Vocabulary reuse (mean): {r['measured_features']['vocabulary_reuse']['mean_contexts_per_word']}")

    print("\n" + "=" * 70)
    print("GENRE FIT SCORES")
    print("=" * 70)

    print(f"\n{'Genre':<25} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 55)
    for genre in GENRE_PROFILES:
        a_score = results['currier_a']['genre_scores'][genre]
        b_score = results['currier_b']['genre_scores'][genre]
        print(f"{genre:<25} {a_score:>14.1f}% {b_score:>14.1f}%")

    print("\n" + "=" * 70)
    print("BEST FIT")
    print("=" * 70)
    print(f"\nCurrier A best fit: {results['currier_a']['best_fit_genre']} ({results['currier_a']['best_fit_score']}%)")
    print(f"Currier B best fit: {results['currier_b']['best_fit_genre']} ({results['currier_b']['best_fit_score']}%)")

    # Add genre profile reference
    results['genre_profiles'] = GENRE_PROFILES
    results['timestamp'] = datetime.now().isoformat()
    results['methodology'] = 'Structural genre comparison - NO SEMANTIC CLAIMS'

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    a_best = results['currier_a']['best_fit_genre']
    b_best = results['currier_b']['best_fit_genre']
    a_score = results['currier_a']['best_fit_score']
    b_score = results['currier_b']['best_fit_score']

    if a_best == b_best:
        print(f"\nBoth sections best fit: {a_best}")
        print(f"This suggests unified genre despite vocabulary differences.")
    else:
        print(f"\nSections have different best-fit genres:")
        print(f"  Currier A -> {a_best} ({a_score}%)")
        print(f"  Currier B -> {b_best} ({b_score}%)")
        print(f"This supports treating them as structurally different text types.")

    # Add warnings about score quality
    if a_score < 50 and b_score < 50:
        print("\nWARNING: Both scores below 50% - neither genre is a strong fit.")
        print("The text may represent a genre not in our comparison set.")

    # Save results
    with open('genre_comparison_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to genre_comparison_report.json")


if __name__ == '__main__':
    main()
