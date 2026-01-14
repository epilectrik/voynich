"""
Test: Intra-line token repetition in Currier A

Question: Do tokens repeat within single A lines in structured ways?
If yes: Could encode ratios (e.g., 3x token A, 1x token B = 3:1 ratio)
If no: Compounds are presence/absence only (1:1:1:1)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"


def load_a_lines():
    """Load all Currier A lines with their tokens."""
    a_lines = defaultdict(list)  # (folio, line_num) -> [tokens]

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            lang = row.get('language', '')
            if lang != 'A':
                continue

            folio = row['folio']
            line_num = row.get('line_number', '0')

            try:
                line_num = int(line_num)
            except:
                line_num = 0

            a_lines[(folio, line_num)].append(token)

    return a_lines


def analyze_intra_line_repetition(a_lines):
    """Analyze token repetition within single A lines."""
    print("="*70)
    print("INTRA-LINE TOKEN REPETITION ANALYSIS")
    print("="*70)

    # Statistics collectors
    lines_with_repetition = 0
    total_lines = 0
    repetition_counts = []  # max repetition count per line
    all_rep_patterns = []   # (token, count) for repeated tokens

    # Per-line analysis
    line_details = []

    for (folio, line_num), tokens in a_lines.items():
        if len(tokens) < 2:
            continue

        total_lines += 1
        token_counts = Counter(tokens)
        max_count = max(token_counts.values())

        if max_count > 1:
            lines_with_repetition += 1
            repetition_counts.append(max_count)

            # Record all repeated tokens
            for token, count in token_counts.items():
                if count > 1:
                    all_rep_patterns.append((token, count))

            # Store details for interesting cases
            if max_count >= 3:
                line_details.append({
                    'folio': folio,
                    'line': line_num,
                    'tokens': tokens,
                    'counts': dict(token_counts),
                    'max_rep': max_count
                })

    # Report basic stats
    print(f"\nTotal A lines (2+ tokens): {total_lines}")
    print(f"Lines with repetition: {lines_with_repetition} ({100*lines_with_repetition/total_lines:.1f}%)")

    if repetition_counts:
        print(f"\nMax repetition per line:")
        for rep in range(2, max(repetition_counts)+1):
            n = sum(1 for r in repetition_counts if r == rep)
            if n > 0:
                print(f"  {rep}x: {n} lines ({100*n/len(repetition_counts):.1f}% of repeating lines)")

    return lines_with_repetition, total_lines, repetition_counts, all_rep_patterns, line_details


def analyze_repetition_patterns(all_rep_patterns):
    """Analyze which tokens repeat and how."""
    print("\n" + "="*70)
    print("REPETITION PATTERN ANALYSIS")
    print("="*70)

    if not all_rep_patterns:
        print("No repetition patterns found.")
        return

    # Count by repetition level
    by_count = defaultdict(list)
    for token, count in all_rep_patterns:
        by_count[count].append(token)

    print(f"\nRepetition distribution:")
    for count in sorted(by_count.keys()):
        tokens = by_count[count]
        unique = len(set(tokens))
        print(f"  {count}x: {len(tokens)} occurrences, {unique} unique tokens")

    # Most commonly repeated tokens
    token_rep_freq = Counter(t for t, c in all_rep_patterns)
    print(f"\nMost frequently repeated tokens (top 20):")
    print(f"{'Token':<15} {'Times repeated':<15} {'Typical count'}")
    print("-"*45)

    for token, freq in token_rep_freq.most_common(20):
        counts = [c for t, c in all_rep_patterns if t == token]
        avg_count = np.mean(counts)
        print(f"{token:<15} {freq:<15} {avg_count:.1f}x")

    return token_rep_freq, by_count


def analyze_ratio_structure(line_details):
    """Look for ratio-like patterns in high-repetition lines."""
    print("\n" + "="*70)
    print("RATIO STRUCTURE ANALYSIS")
    print("="*70)

    if not line_details:
        print("No high-repetition lines found.")
        return

    # Look for lines with multiple different repetition counts
    # e.g., 3x of token A, 2x of token B, 1x of token C = potential 3:2:1 ratio

    ratio_candidates = []

    for detail in line_details:
        counts = detail['counts']
        unique_counts = set(counts.values())

        if len(unique_counts) > 1 and max(counts.values()) >= 2:
            # Multiple different counts = potential ratio encoding
            ratio_candidates.append(detail)

    print(f"\nLines with multiple different token counts: {len(ratio_candidates)}")

    if ratio_candidates:
        print(f"\nExample ratio-like patterns (first 15):")
        print("-"*70)

        for detail in ratio_candidates[:15]:
            counts = detail['counts']
            # Format as ratio string
            ratio_str = " : ".join(f"{t}({c})" for t, c in sorted(counts.items(), key=lambda x: -x[1]))
            print(f"{detail['folio']}:{detail['line']}: {ratio_str}")

    # Analyze ratio patterns
    print("\n" + "-"*70)
    print("RATIO PATTERN FREQUENCY")
    print("-"*70)

    ratio_signatures = []
    for detail in line_details:
        counts = sorted(detail['counts'].values(), reverse=True)
        ratio_signatures.append(tuple(counts))

    sig_freq = Counter(ratio_signatures)
    print(f"\nMost common repetition signatures:")
    for sig, freq in sig_freq.most_common(15):
        sig_str = ":".join(str(s) for s in sig)
        print(f"  {sig_str} ratio: {freq} lines")

    return ratio_candidates


def test_randomness(a_lines, repetition_counts):
    """Test if repetition is structured or random."""
    print("\n" + "="*70)
    print("RANDOMNESS TEST")
    print("="*70)

    # If repetition were random, we'd expect it to follow binomial distribution
    # based on vocabulary size and line length

    # Calculate expected repetition rate under random model
    all_tokens = []
    line_lengths = []
    for tokens in a_lines.values():
        if len(tokens) >= 2:
            all_tokens.extend(tokens)
            line_lengths.append(len(tokens))

    vocab_size = len(set(all_tokens))
    mean_line_length = np.mean(line_lengths)

    print(f"\nVocabulary size: {vocab_size}")
    print(f"Mean line length: {mean_line_length:.1f}")

    # Under random selection with replacement:
    # P(at least one repeat in line of length L) ≈ 1 - (V!/(V-L)!) / V^L
    # Simplified: birthday problem approximation

    # For each line length, calculate expected repetition probability
    expected_rep_rate = 0
    for length in line_lengths:
        # Birthday problem: P(collision) ≈ 1 - e^(-L(L-1)/(2V))
        p_collision = 1 - np.exp(-length * (length - 1) / (2 * vocab_size))
        expected_rep_rate += p_collision
    expected_rep_rate /= len(line_lengths)

    observed_rep_rate = len(repetition_counts) / len(line_lengths)

    print(f"\nExpected repetition rate (random model): {expected_rep_rate:.1%}")
    print(f"Observed repetition rate: {observed_rep_rate:.1%}")
    print(f"Ratio (observed/expected): {observed_rep_rate/expected_rep_rate:.2f}x")

    if observed_rep_rate > expected_rep_rate * 2:
        print("\n>> RESULT: Repetition is SIGNIFICANTLY HIGHER than random")
        print(">> This suggests STRUCTURED repetition (potential ratio encoding)")
    elif observed_rep_rate < expected_rep_rate * 0.5:
        print("\n>> RESULT: Repetition is SIGNIFICANTLY LOWER than random")
        print(">> This suggests AVOIDANCE of repetition")
    else:
        print("\n>> RESULT: Repetition is CONSISTENT with random")
        print(">> No evidence for structured ratio encoding")

    return expected_rep_rate, observed_rep_rate


def main():
    print("Loading Currier A lines...")
    a_lines = load_a_lines()
    print(f"Loaded {len(a_lines)} A lines")

    # Main analysis
    lines_with_rep, total, rep_counts, all_patterns, line_details = analyze_intra_line_repetition(a_lines)

    # Pattern analysis
    if all_patterns:
        analyze_repetition_patterns(all_patterns)

    # Ratio structure
    if line_details:
        analyze_ratio_structure(line_details)

    # Randomness test
    if rep_counts:
        test_randomness(a_lines, rep_counts)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if lines_with_rep > 0:
        rep_rate = 100 * lines_with_rep / total
        print(f"\n{rep_rate:.1f}% of A lines have intra-line repetition")

        if rep_rate > 20:
            print("\n>> VERDICT: Significant intra-line repetition exists")
            print(">> Ratio encoding is PLAUSIBLE")
        else:
            print("\n>> VERDICT: Limited intra-line repetition")
            print(">> Ratio encoding is UNLIKELY")


if __name__ == '__main__':
    main()
