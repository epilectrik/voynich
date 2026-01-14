"""
Minimum Record Size Analysis

Question: What is the minimum size for actual registry entries?
- 1 token: Registry control operators (C484)
- 2 tokens: Unknown - structural or genuine entries?
- 3+ tokens: Normal registry entries

Tests:
1. Distribution of line lengths
2. 2-token line characteristics vs 1-token and 3+ token
3. AZC presence by line length
4. Vocabulary overlap analysis
5. Positional patterns
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"


def load_data():
    """Load A lines with full metadata."""
    lines = defaultdict(list)  # (folio, line_num) -> [tokens]
    folio_has_azc = defaultdict(bool)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            lang = row.get('language', '')
            line_str = row.get('line_number', '0')

            try:
                line_num = int(line_str)
            except ValueError:
                line_num = int(''.join(c for c in line_str if c.isdigit()) or '0')

            if lang == 'A':
                lines[(folio, line_num)].append(token)
            elif lang == 'NA':  # AZC
                folio_has_azc[folio] = True

    return lines, folio_has_azc


def analyze_length_distribution(lines):
    """Test 1: Distribution of line lengths."""
    print("="*70)
    print("TEST 1: LINE LENGTH DISTRIBUTION")
    print("="*70)

    lengths = [len(tokens) for tokens in lines.values()]
    length_counts = Counter(lengths)

    print(f"\nLine length distribution:")
    print(f"{'Length':<10} {'Count':<10} {'Percent':<10} {'Cumulative':<10}")
    print("-"*45)

    cumulative = 0
    for length in sorted(length_counts.keys()):
        count = length_counts[length]
        pct = 100 * count / len(lengths)
        cumulative += pct
        print(f"{length:<10} {count:<10} {pct:.1f}%      {cumulative:.1f}%")
        if length > 15:
            break

    print(f"\nTotal lines: {len(lengths)}")
    print(f"Mean length: {np.mean(lengths):.1f}")
    print(f"Median length: {np.median(lengths):.0f}")

    return length_counts


def analyze_by_length_class(lines, folio_has_azc):
    """Test 2: Compare characteristics by length class."""
    print("\n" + "="*70)
    print("TEST 2: CHARACTERISTICS BY LENGTH CLASS")
    print("="*70)

    # Group lines by length
    by_length = defaultdict(list)
    for (folio, line_num), tokens in lines.items():
        by_length[len(tokens)].append({
            'folio': folio,
            'line_num': line_num,
            'tokens': tokens,
            'has_azc': folio_has_azc.get(folio, False)
        })

    print(f"\n{'Length':<8} {'Count':<8} {'In AZC folio':<15} {'AZC rate':<12}")
    print("-"*50)

    for length in sorted(by_length.keys())[:10]:
        entries = by_length[length]
        in_azc = sum(1 for e in entries if e['has_azc'])
        azc_rate = in_azc / len(entries) if entries else 0
        print(f"{length:<8} {len(entries):<8} {in_azc:<15} {azc_rate:.1%}")

    return by_length


def analyze_vocabulary_overlap(lines):
    """Test 3: Vocabulary overlap between length classes."""
    print("\n" + "="*70)
    print("TEST 3: VOCABULARY OVERLAP")
    print("="*70)

    # Collect vocabulary by length class
    vocab_1 = set()  # single-token
    vocab_2 = set()  # 2-token
    vocab_3plus = set()  # 3+ token

    for (folio, line_num), tokens in lines.items():
        if len(tokens) == 1:
            vocab_1.update(tokens)
        elif len(tokens) == 2:
            vocab_2.update(tokens)
        else:
            vocab_3plus.update(tokens)

    print(f"\nVocabulary sizes:")
    print(f"  1-token lines: {len(vocab_1)} unique tokens")
    print(f"  2-token lines: {len(vocab_2)} unique tokens")
    print(f"  3+-token lines: {len(vocab_3plus)} unique tokens")

    # Overlap analysis
    overlap_1_2 = vocab_1 & vocab_2
    overlap_1_3 = vocab_1 & vocab_3plus
    overlap_2_3 = vocab_2 & vocab_3plus

    print(f"\nOverlap:")
    print(f"  1-token & 2-token: {len(overlap_1_2)} ({100*len(overlap_1_2)/len(vocab_1) if vocab_1 else 0:.1f}% of 1-token vocab)")
    print(f"  1-token & 3+-token: {len(overlap_1_3)} ({100*len(overlap_1_3)/len(vocab_1) if vocab_1 else 0:.1f}% of 1-token vocab)")
    print(f"  2-token & 3+-token: {len(overlap_2_3)} ({100*len(overlap_2_3)/len(vocab_2) if vocab_2 else 0:.1f}% of 2-token vocab)")

    # Tokens exclusive to 2-token lines
    exclusive_2 = vocab_2 - vocab_1 - vocab_3plus
    print(f"\n  Tokens ONLY in 2-token lines: {len(exclusive_2)} ({100*len(exclusive_2)/len(vocab_2) if vocab_2 else 0:.1f}%)")

    if exclusive_2:
        print(f"  Examples: {list(exclusive_2)[:10]}")

    return vocab_1, vocab_2, vocab_3plus


def analyze_morphology(lines):
    """Test 4: Morphological profile by length class."""
    print("\n" + "="*70)
    print("TEST 4: MORPHOLOGICAL PROFILE BY LENGTH")
    print("="*70)

    def get_prefix(token):
        return token[:2] if len(token) >= 2 else token

    # Collect prefixes by length class
    prefixes_by_length = defaultdict(list)

    for (folio, line_num), tokens in lines.items():
        length = len(tokens)
        if length <= 5:  # Focus on small lengths
            for token in tokens:
                prefixes_by_length[length].append(get_prefix(token))

    # Compare prefix distributions
    print(f"\nTop prefixes by line length:")

    for length in [1, 2, 3, 4, 5]:
        if length not in prefixes_by_length:
            continue
        prefixes = prefixes_by_length[length]
        counts = Counter(prefixes)
        total = sum(counts.values())

        top_5 = counts.most_common(5)
        top_str = ", ".join(f"{p}:{100*c/total:.0f}%" for p, c in top_5)
        print(f"  Length {length}: {top_str}")

    # Check if 2-token lines have different morphology
    if 1 in prefixes_by_length and 2 in prefixes_by_length:
        prefix_1 = Counter(prefixes_by_length[1])
        prefix_2 = Counter(prefixes_by_length[2])

        # Normalize
        total_1 = sum(prefix_1.values())
        total_2 = sum(prefix_2.values())

        # Find divergent prefixes
        all_prefixes = set(prefix_1.keys()) | set(prefix_2.keys())
        divergences = []

        for p in all_prefixes:
            rate_1 = prefix_1.get(p, 0) / total_1 if total_1 else 0
            rate_2 = prefix_2.get(p, 0) / total_2 if total_2 else 0
            diff = abs(rate_1 - rate_2)
            if diff > 0.05:
                divergences.append((p, rate_1, rate_2, diff))

        if divergences:
            print(f"\nDivergent prefixes (1-token vs 2-token):")
            for p, r1, r2, diff in sorted(divergences, key=lambda x: -x[3])[:5]:
                print(f"  {p}: {r1:.1%} (1-token) vs {r2:.1%} (2-token)")


def analyze_positional_patterns(lines):
    """Test 5: Positional patterns by length."""
    print("\n" + "="*70)
    print("TEST 5: POSITIONAL PATTERNS")
    print("="*70)

    # Get max line per folio
    folio_max = defaultdict(int)
    for (folio, line_num), tokens in lines.items():
        folio_max[folio] = max(folio_max[folio], line_num)

    # Normalized positions by length
    positions_by_length = defaultdict(list)

    for (folio, line_num), tokens in lines.items():
        length = len(tokens)
        max_line = folio_max[folio]
        if max_line > 0:
            norm_pos = line_num / max_line
            positions_by_length[length].append(norm_pos)

    print(f"\nNormalized position by length:")
    print(f"{'Length':<10} {'Mean pos':<12} {'At start':<12} {'At end':<12}")
    print("-"*50)

    for length in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        if length not in positions_by_length:
            continue
        positions = positions_by_length[length]
        mean_pos = np.mean(positions)
        at_start = sum(1 for p in positions if p < 0.1) / len(positions)
        at_end = sum(1 for p in positions if p > 0.9) / len(positions)
        print(f"{length:<10} {mean_pos:.3f}        {at_start:.1%}         {at_end:.1%}")

    # Statistical test: 2-token vs 3+-token positions
    if 2 in positions_by_length and 3 in positions_by_length:
        pos_2 = positions_by_length[2]
        pos_3plus = []
        for length in range(3, max(positions_by_length.keys()) + 1):
            pos_3plus.extend(positions_by_length.get(length, []))

        if pos_2 and pos_3plus:
            stat, p = stats.mannwhitneyu(pos_2, pos_3plus, alternative='two-sided')
            print(f"\n2-token vs 3+-token position test: p = {p:.4f}")
            print(f"Interpretation: {'POSITIONALLY DISTINCT' if p < 0.05 else 'SIMILAR POSITIONS'}")


def detailed_2token_analysis(lines, folio_has_azc):
    """Detailed analysis of 2-token lines."""
    print("\n" + "="*70)
    print("DETAILED 2-TOKEN LINE ANALYSIS")
    print("="*70)

    two_token_lines = []
    for (folio, line_num), tokens in lines.items():
        if len(tokens) == 2:
            two_token_lines.append({
                'folio': folio,
                'line_num': line_num,
                'tokens': tokens,
                'has_azc': folio_has_azc.get(folio, False)
            })

    print(f"\nTotal 2-token lines: {len(two_token_lines)}")

    # In AZC vs non-AZC folios
    in_azc = sum(1 for e in two_token_lines if e['has_azc'])
    print(f"In AZC folios: {in_azc} ({100*in_azc/len(two_token_lines):.1f}%)")
    print(f"In pure-A folios: {len(two_token_lines) - in_azc} ({100*(len(two_token_lines)-in_azc)/len(two_token_lines):.1f}%)")

    # Show some examples
    print(f"\nExample 2-token lines:")
    print(f"{'Folio':<10} {'Line':<6} {'Tokens':<40} {'AZC?':<6}")
    print("-"*65)

    for entry in two_token_lines[:15]:
        tokens_str = " ".join(entry['tokens'])
        azc_str = "YES" if entry['has_azc'] else "NO"
        print(f"{entry['folio']:<10} {entry['line_num']:<6} {tokens_str:<40} {azc_str:<6}")

    return two_token_lines


def main():
    print("Loading data...")
    lines, folio_has_azc = load_data()
    print(f"Loaded {len(lines)} A lines")

    # Run analyses
    length_counts = analyze_length_distribution(lines)
    by_length = analyze_by_length_class(lines, folio_has_azc)
    vocab_1, vocab_2, vocab_3plus = analyze_vocabulary_overlap(lines)
    analyze_morphology(lines)
    analyze_positional_patterns(lines)
    two_token = detailed_2token_analysis(lines, folio_has_azc)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: MINIMUM RECORD SIZE")
    print("="*70)

    n_1 = length_counts.get(1, 0)
    n_2 = length_counts.get(2, 0)
    n_3 = length_counts.get(3, 0)

    # Check if 2-token lines behave like control operators or entries
    two_token_in_azc = sum(1 for e in two_token if e['has_azc'])
    two_token_azc_rate = two_token_in_azc / len(two_token) if two_token else 0

    # Compare to 3+ token AZC rate
    three_plus = [e for (f, l), tokens in lines.items() for e in [{'has_azc': folio_has_azc.get(f, False)}] if len(tokens) >= 3]
    three_plus_azc_rate = sum(1 for e in three_plus if e['has_azc']) / len(three_plus) if three_plus else 0

    vocab_2_overlap_3 = len(vocab_2 & vocab_3plus) / len(vocab_2) if vocab_2 else 0
    vocab_1_overlap_3 = len(vocab_1 & vocab_3plus) / len(vocab_1) if vocab_1 else 0

    print(f"""
Length Distribution:
  1-token: {n_1} ({100*n_1/len(lines):.1f}%) - CONTROL OPERATORS (C484)
  2-token: {n_2} ({100*n_2/len(lines):.1f}%)
  3-token: {n_3} ({100*n_3/len(lines):.1f}%)

2-Token Line Characteristics:
  AZC folio rate: {two_token_azc_rate:.1%} (vs {three_plus_azc_rate:.1%} for 3+)
  Vocabulary overlap with 3+: {vocab_2_overlap_3:.1%} (vs {vocab_1_overlap_3:.1%} for 1-token)
""")

    if two_token_azc_rate > 0.5 and vocab_2_overlap_3 > 0.8:
        print("VERDICT: 2-token lines are NORMAL REGISTRY ENTRIES (small batches)")
        print("         Minimum record size = 2 tokens")
    elif two_token_azc_rate < 0.2 and vocab_2_overlap_3 < 0.5:
        print("VERDICT: 2-token lines are STRUCTURALLY DISTINCT (like 1-token)")
        print("         Minimum record size = 3 tokens")
    else:
        print("VERDICT: 2-token lines show MIXED characteristics")
        print("         Further investigation needed")


if __name__ == '__main__':
    main()
