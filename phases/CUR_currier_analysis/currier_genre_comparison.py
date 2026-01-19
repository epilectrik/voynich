#!/usr/bin/env python3
"""
Currier A/B Genre Comparison

Separate genre diagnostics for Currier A and B to test whether
pooled analysis masks fundamental genre differences.

HYPOTHESIS:
- Currier A: More formulaic (labels, tables, captions)
- Currier B: More narrative (explanatory prose)
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any


def load_corpus() -> Tuple[List[Dict], List[Dict]]:
    """Load corpus and split by Currier classification."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    currier_a = []
    currier_b = []

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

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                entry = {
                    'word': word,
                    'folio': folio,
                    'line': line_num
                }
                if currier == 'A':
                    currier_a.append(entry)
                elif currier == 'B':
                    currier_b.append(entry)

    return currier_a, currier_b


def extract_sequences(corpus: List[Dict]) -> List[List[str]]:
    """Extract word sequences by line."""
    by_line = defaultdict(list)
    for w in corpus:
        key = (w['folio'], w['line'])
        by_line[key].append(w['word'])
    return list(by_line.values())


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


# ============================================================================
# 1. SEQUENCE LENGTH DISTRIBUTION
# ============================================================================

def analyze_sequence_lengths(sequences: List[List[str]]) -> Dict:
    """Compute sequence length statistics."""
    lengths = [len(seq) for seq in sequences if seq]

    if not lengths:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0}

    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    std = math.sqrt(variance)
    sorted_lengths = sorted(lengths)
    median = sorted_lengths[len(lengths) // 2]

    return {
        'count': len(lengths),
        'mean': round(mean, 2),
        'std': round(std, 2),
        'min': min(lengths),
        'max': max(lengths),
        'median': median,
        'distribution': dict(Counter(lengths).most_common(10))
    }


# ============================================================================
# 2. REPETITION ANALYSIS
# ============================================================================

def extract_ngrams(sequences: List[List[str]], n: int) -> List[Tuple]:
    """Extract n-grams from sequences."""
    ngrams = []
    for seq in sequences:
        for i in range(len(seq) - n + 1):
            ngrams.append(tuple(seq[i:i+n]))
    return ngrams


def analyze_repetition(sequences: List[List[str]]) -> Dict:
    """Analyze repetition rates for 2-grams, 3-grams, 4-grams."""
    results = {}

    for n in [2, 3, 4]:
        ngrams = extract_ngrams(sequences, n)
        if not ngrams:
            results[f'{n}gram'] = {'total': 0, 'unique': 0, 'repeated': 0, 'rate': 0}
            continue

        counts = Counter(ngrams)
        repeated = sum(1 for c in counts.values() if c > 1)

        # Duplicate instance rate (how many tokens are duplicates)
        total = len(ngrams)
        unique = len(counts)
        duplicate_rate = (total - unique) / total if total > 0 else 0

        results[f'{n}gram'] = {
            'total': total,
            'unique': unique,
            'repeated_patterns': repeated,
            'repetition_rate': round(repeated / len(counts), 4) if counts else 0,
            'duplicate_instance_rate': round(duplicate_rate, 4),
            'most_repeated': [
                {'pattern': ' '.join(t), 'count': c}
                for t, c in counts.most_common(5) if c > 1
            ]
        }

    # Near-duplicate detection (simplified - just count patterns with 2+ occurrences)
    # Full O(n^2) comparison is too slow for large corpora
    results['near_duplicates'] = 'skipped_for_performance'

    return results


# ============================================================================
# 3. POSITIONAL ENTROPY
# ============================================================================

def analyze_positional_entropy(sequences: List[List[str]]) -> Dict:
    """Compute entropy of words by position."""
    first_words = []
    last_words = []
    all_words = []

    for seq in sequences:
        if len(seq) >= 1:
            first_words.append(seq[0])
            all_words.extend(seq)
        if len(seq) >= 2:
            last_words.append(seq[-1])

    # Also analyze prefix positions (first 2 chars of words)
    first_prefixes = [w[:2] if len(w) >= 2 else w for w in first_words]
    last_prefixes = [w[:2] if len(w) >= 2 else w for w in last_words]
    all_prefixes = [w[:2] if len(w) >= 2 else w for w in all_words]

    # And suffix positions (last 2 chars)
    first_suffixes = [w[-2:] if len(w) >= 2 else w for w in first_words]
    last_suffixes = [w[-2:] if len(w) >= 2 else w for w in last_words]
    all_suffixes = [w[-2:] if len(w) >= 2 else w for w in all_words]

    return {
        'word_entropy': {
            'first_position': round(compute_entropy(first_words), 2),
            'last_position': round(compute_entropy(last_words), 2),
            'overall': round(compute_entropy(all_words), 2)
        },
        'prefix_entropy': {
            'first_position': round(compute_entropy(first_prefixes), 2),
            'last_position': round(compute_entropy(last_prefixes), 2),
            'overall': round(compute_entropy(all_prefixes), 2)
        },
        'suffix_entropy': {
            'first_position': round(compute_entropy(first_suffixes), 2),
            'last_position': round(compute_entropy(last_suffixes), 2),
            'overall': round(compute_entropy(all_suffixes), 2)
        },
        'top_first_words': Counter(first_words).most_common(10),
        'top_last_words': Counter(last_words).most_common(10)
    }


# ============================================================================
# 4. VOCABULARY CONCENTRATION
# ============================================================================

def analyze_vocabulary_concentration(corpus: List[Dict]) -> Dict:
    """Analyze vocabulary concentration (Zipf's law)."""
    words = [w['word'] for w in corpus]
    counts = Counter(words)
    total = len(words)
    unique = len(counts)

    # Sort by frequency (descending)
    sorted_counts = sorted(counts.values(), reverse=True)

    # Find how many words account for 50% and 90% of tokens
    cumsum = 0
    words_for_50 = 0
    words_for_90 = 0

    for i, count in enumerate(sorted_counts):
        cumsum += count
        if words_for_50 == 0 and cumsum >= total * 0.5:
            words_for_50 = i + 1
        if words_for_90 == 0 and cumsum >= total * 0.9:
            words_for_90 = i + 1
            break

    # Zipf's law fit (log-log regression)
    # Zipf: frequency ~ 1/rank
    # log(freq) = -alpha * log(rank) + c
    # We compute correlation between log(rank) and log(freq)

    ranks = list(range(1, len(sorted_counts) + 1))
    log_ranks = [math.log(r) for r in ranks]
    log_freqs = [math.log(f) if f > 0 else 0 for f in sorted_counts]

    # Compute Pearson correlation
    n = len(ranks)
    mean_lr = sum(log_ranks) / n
    mean_lf = sum(log_freqs) / n

    num = sum((log_ranks[i] - mean_lr) * (log_freqs[i] - mean_lf) for i in range(n))
    den_lr = math.sqrt(sum((log_ranks[i] - mean_lr) ** 2 for i in range(n)))
    den_lf = math.sqrt(sum((log_freqs[i] - mean_lf) ** 2 for i in range(n)))

    if den_lr > 0 and den_lf > 0:
        zipf_correlation = num / (den_lr * den_lf)
    else:
        zipf_correlation = 0

    # Estimate Zipf exponent (should be ~-1 for natural language)
    if den_lr > 0:
        zipf_exponent = num / (den_lr ** 2)
    else:
        zipf_exponent = 0

    return {
        'total_tokens': total,
        'unique_words': unique,
        'type_token_ratio': round(unique / total, 4) if total > 0 else 0,
        'words_for_50_pct': words_for_50,
        'words_for_90_pct': words_for_90,
        'concentration_50': round(words_for_50 / unique, 4) if unique > 0 else 0,
        'concentration_90': round(words_for_90 / unique, 4) if unique > 0 else 0,
        'zipf_correlation': round(zipf_correlation, 4),
        'zipf_exponent': round(zipf_exponent, 4)
    }


# ============================================================================
# 5. GENRE PROFILE SCORING
# ============================================================================

GENRE_PROFILES = {
    'MEDICAL_RECIPES': {
        'sequence_length': (3, 7),
        'repetition_rate': (0.15, 0.40),
        'position_entropy': (0.5, 2.0),
        'concentration_50': (0.01, 0.05)
    },
    'NARRATIVE': {
        'sequence_length': (10, 30),
        'repetition_rate': (0.01, 0.10),
        'position_entropy': (2.5, 4.0),
        'concentration_50': (0.01, 0.03)
    },
    'ASTRONOMICAL_TABLES': {
        'sequence_length': (1, 4),
        'repetition_rate': (0.40, 0.80),
        'position_entropy': (0.1, 1.0),
        'concentration_50': (0.005, 0.02)
    },
    'LITURGICAL': {
        'sequence_length': (5, 15),
        'repetition_rate': (0.30, 0.60),
        'position_entropy': (0.5, 1.5),
        'concentration_50': (0.02, 0.06)
    },
    'LABELS_CAPTIONS': {
        'sequence_length': (1, 5),
        'repetition_rate': (0.05, 0.25),
        'position_entropy': (1.0, 3.0),
        'concentration_50': (0.02, 0.08)
    }
}


def score_genre_fit(metrics: Dict, profile: Dict) -> float:
    """Score how well metrics fit a genre profile (0-100)."""
    score = 0
    max_score = 4

    # Sequence length
    seq_len = metrics['sequence_length']['mean']
    if profile['sequence_length'][0] <= seq_len <= profile['sequence_length'][1]:
        score += 1
    elif profile['sequence_length'][0] - 2 <= seq_len <= profile['sequence_length'][1] + 2:
        score += 0.5

    # Repetition rate (use 3gram)
    rep_rate = metrics['repetition']['3gram']['repetition_rate']
    if profile['repetition_rate'][0] <= rep_rate <= profile['repetition_rate'][1]:
        score += 1
    elif profile['repetition_rate'][0] - 0.1 <= rep_rate <= profile['repetition_rate'][1] + 0.1:
        score += 0.5

    # Position entropy (use first position word entropy)
    entropy = metrics['positional_entropy']['word_entropy']['first_position']
    if profile['position_entropy'][0] <= entropy <= profile['position_entropy'][1]:
        score += 1
    elif profile['position_entropy'][0] - 0.5 <= entropy <= profile['position_entropy'][1] + 0.5:
        score += 0.5

    # Vocabulary concentration
    conc = metrics['vocabulary']['concentration_50']
    if profile['concentration_50'][0] <= conc <= profile['concentration_50'][1]:
        score += 1
    elif profile['concentration_50'][0] - 0.01 <= conc <= profile['concentration_50'][1] + 0.01:
        score += 0.5

    return round(score / max_score * 100, 1)


def analyze_corpus(corpus: List[Dict], name: str) -> Dict:
    """Run full analysis on a corpus."""
    print(f"\nAnalyzing {name} ({len(corpus)} words)...")

    sequences = extract_sequences(corpus)

    metrics = {
        'name': name,
        'word_count': len(corpus),
        'sequence_count': len(sequences),
        'sequence_length': analyze_sequence_lengths(sequences),
        'repetition': analyze_repetition(sequences),
        'positional_entropy': analyze_positional_entropy(sequences),
        'vocabulary': analyze_vocabulary_concentration(corpus)
    }

    # Score against genre profiles
    genre_scores = {}
    for genre, profile in GENRE_PROFILES.items():
        genre_scores[genre] = score_genre_fit(metrics, profile)

    metrics['genre_scores'] = genre_scores
    metrics['best_fit_genre'] = max(genre_scores, key=genre_scores.get)
    metrics['best_fit_score'] = genre_scores[metrics['best_fit_genre']]

    return metrics


def compare_corpora(a_metrics: Dict, b_metrics: Dict) -> Dict:
    """Compare metrics between Currier A and B."""
    comparisons = {}

    # Sequence length comparison
    a_len = a_metrics['sequence_length']['mean']
    b_len = b_metrics['sequence_length']['mean']
    comparisons['sequence_length'] = {
        'a': a_len,
        'b': b_len,
        'difference': round(b_len - a_len, 2),
        'a_shorter': a_len < b_len
    }

    # Repetition comparison
    a_rep = a_metrics['repetition']['3gram']['repetition_rate']
    b_rep = b_metrics['repetition']['3gram']['repetition_rate']
    comparisons['repetition_rate'] = {
        'a': a_rep,
        'b': b_rep,
        'difference': round(b_rep - a_rep, 4),
        'a_more_repetitive': a_rep > b_rep
    }

    # Entropy comparison
    a_ent = a_metrics['positional_entropy']['word_entropy']['first_position']
    b_ent = b_metrics['positional_entropy']['word_entropy']['first_position']
    comparisons['position_entropy'] = {
        'a': a_ent,
        'b': b_ent,
        'difference': round(b_ent - a_ent, 2),
        'a_lower_entropy': a_ent < b_ent
    }

    # Vocabulary concentration comparison
    a_conc = a_metrics['vocabulary']['concentration_50']
    b_conc = b_metrics['vocabulary']['concentration_50']
    comparisons['vocabulary_concentration'] = {
        'a': a_conc,
        'b': b_conc,
        'difference': round(b_conc - a_conc, 4),
        'a_more_concentrated': a_conc > b_conc
    }

    # Genre comparison
    comparisons['genre_fit'] = {
        'a_best': a_metrics['best_fit_genre'],
        'a_score': a_metrics['best_fit_score'],
        'b_best': b_metrics['best_fit_genre'],
        'b_score': b_metrics['best_fit_score'],
        'same_genre': a_metrics['best_fit_genre'] == b_metrics['best_fit_genre']
    }

    # Hypothesis test: Is A more formulaic than B?
    formulaic_evidence = 0
    if comparisons['sequence_length']['a_shorter']:
        formulaic_evidence += 1
    if comparisons['repetition_rate']['a_more_repetitive']:
        formulaic_evidence += 1
    if comparisons['position_entropy']['a_lower_entropy']:
        formulaic_evidence += 1
    if comparisons['vocabulary_concentration']['a_more_concentrated']:
        formulaic_evidence += 1

    if formulaic_evidence >= 3:
        verdict = 'CONFIRMED'
        explanation = f'Currier A shows {formulaic_evidence}/4 formulaic characteristics'
    elif formulaic_evidence >= 2:
        verdict = 'PARTIAL'
        explanation = f'Currier A shows {formulaic_evidence}/4 formulaic characteristics'
    else:
        verdict = 'REJECTED'
        explanation = f'Currier A shows only {formulaic_evidence}/4 formulaic characteristics'

    comparisons['hypothesis_test'] = {
        'hypothesis': 'Currier A is more formulaic than Currier B',
        'evidence_count': formulaic_evidence,
        'verdict': verdict,
        'explanation': explanation
    }

    return comparisons


def main():
    print("=" * 70)
    print("CURRIER A/B GENRE COMPARISON")
    print("Separate genre diagnostics for each corpus")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    currier_a, currier_b = load_corpus()
    print(f"Currier A: {len(currier_a)} words")
    print(f"Currier B: {len(currier_b)} words")

    # Analyze each corpus
    a_metrics = analyze_corpus(currier_a, 'Currier A')
    b_metrics = analyze_corpus(currier_b, 'Currier B')

    # Compare
    comparisons = compare_corpora(a_metrics, b_metrics)

    # Print results
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    print(f"\n{'Metric':<30} {'Currier A':>15} {'Currier B':>15} {'Diff':>10}")
    print("-" * 70)

    print(f"{'Sequence length (mean)':<30} {a_metrics['sequence_length']['mean']:>15.2f} {b_metrics['sequence_length']['mean']:>15.2f} {comparisons['sequence_length']['difference']:>10.2f}")
    print(f"{'Repetition rate (3gram)':<30} {a_metrics['repetition']['3gram']['repetition_rate']:>15.4f} {b_metrics['repetition']['3gram']['repetition_rate']:>15.4f} {comparisons['repetition_rate']['difference']:>10.4f}")
    print(f"{'Position entropy (first)':<30} {a_metrics['positional_entropy']['word_entropy']['first_position']:>15.2f} {b_metrics['positional_entropy']['word_entropy']['first_position']:>15.2f} {comparisons['position_entropy']['difference']:>10.2f}")
    print(f"{'Vocab concentration (50%)':<30} {a_metrics['vocabulary']['concentration_50']:>15.4f} {b_metrics['vocabulary']['concentration_50']:>15.4f} {comparisons['vocabulary_concentration']['difference']:>10.4f}")

    print("\n" + "=" * 70)
    print("GENRE FIT SCORES")
    print("=" * 70)

    print(f"\n{'Genre':<25} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 55)
    for genre in GENRE_PROFILES:
        a_score = a_metrics['genre_scores'].get(genre, 0)
        b_score = b_metrics['genre_scores'].get(genre, 0)
        print(f"{genre:<25} {a_score:>14.1f}% {b_score:>14.1f}%")

    print("\n" + "=" * 70)
    print("HYPOTHESIS TEST")
    print("=" * 70)

    hyp = comparisons['hypothesis_test']
    print(f"\nHypothesis: {hyp['hypothesis']}")
    print(f"Evidence: {hyp['evidence_count']}/4 characteristics confirmed")
    print(f"Verdict: {hyp['verdict']}")
    print(f"Explanation: {hyp['explanation']}")

    print("\n" + "=" * 70)
    print("BEST FIT GENRES")
    print("=" * 70)
    print(f"\nCurrier A: {a_metrics['best_fit_genre']} ({a_metrics['best_fit_score']}%)")
    print(f"Currier B: {b_metrics['best_fit_genre']} ({b_metrics['best_fit_score']}%)")

    if comparisons['genre_fit']['same_genre']:
        print("\nBoth corpora best fit the SAME genre.")
    else:
        print("\nCorpora best fit DIFFERENT genres.")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Separate genre diagnostics for Currier A vs B',
        'currier_a': a_metrics,
        'currier_b': b_metrics,
        'comparison': comparisons,
        'genre_profiles': GENRE_PROFILES
    }

    with open('currier_genre_comparison_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to currier_genre_comparison_report.json")


if __name__ == '__main__':
    main()
