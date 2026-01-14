"""
2-Token Line Positional Split Test

Question: Do 2-token lines at folio-end differ from mid-folio 2-token lines?

Predictions:
- Mid-folio 2-token: Compressed normal entries
- End-folio 2-token: Scope-closing minimal bundles

Tests:
1. Vocabulary comparison
2. Morphological profile
3. Token rarity (MIDDLE distribution)
4. Prefix combinations
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"


def load_data():
    """Load A lines with position info."""
    lines = defaultdict(list)  # (folio, line_num) -> [tokens]
    folio_max = defaultdict(int)

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
            line_str = row.get('line_number', '0')

            try:
                line_num = int(line_str)
            except ValueError:
                line_num = int(''.join(c for c in line_str if c.isdigit()) or '0')

            lines[(folio, line_num)].append(token)
            folio_max[folio] = max(folio_max[folio], line_num)

    return lines, folio_max


def split_two_token_lines(lines, folio_max):
    """Split 2-token lines into end-folio vs mid-folio."""
    end_folio = []  # Last 2 lines of folio
    mid_folio = []  # Everything else

    for (folio, line_num), tokens in lines.items():
        if len(tokens) != 2:
            continue

        max_line = folio_max[folio]
        is_end = (max_line - line_num) <= 1  # Last 2 lines

        entry = {
            'folio': folio,
            'line_num': line_num,
            'tokens': tokens,
            'max_line': max_line,
            'normalized_pos': line_num / max_line if max_line > 0 else 0
        }

        if is_end:
            end_folio.append(entry)
        else:
            mid_folio.append(entry)

    return end_folio, mid_folio


def compare_vocabulary(end_folio, mid_folio, all_lines):
    """Compare vocabulary between end-folio and mid-folio 2-token lines."""
    print("="*70)
    print("TEST 1: VOCABULARY COMPARISON")
    print("="*70)

    end_tokens = [t for e in end_folio for t in e['tokens']]
    mid_tokens = [t for e in mid_folio for t in e['tokens']]
    all_3plus_tokens = [t for tokens in all_lines.values() if len(tokens) >= 3 for t in tokens]

    end_vocab = set(end_tokens)
    mid_vocab = set(mid_tokens)
    all_vocab = set(all_3plus_tokens)

    print(f"\nVocabulary sizes:")
    print(f"  End-folio 2-token: {len(end_vocab)} unique tokens")
    print(f"  Mid-folio 2-token: {len(mid_vocab)} unique tokens")
    print(f"  3+ token lines: {len(all_vocab)} unique tokens")

    # Overlap with 3+ vocabulary
    end_overlap = len(end_vocab & all_vocab) / len(end_vocab) if end_vocab else 0
    mid_overlap = len(mid_vocab & all_vocab) / len(mid_vocab) if mid_vocab else 0

    print(f"\nOverlap with 3+ vocabulary:")
    print(f"  End-folio: {end_overlap:.1%}")
    print(f"  Mid-folio: {mid_overlap:.1%}")

    # Overlap between end and mid
    end_mid_overlap = len(end_vocab & mid_vocab)
    print(f"\nOverlap between end and mid: {end_mid_overlap} tokens")

    # Exclusive tokens
    end_exclusive = end_vocab - mid_vocab - all_vocab
    mid_exclusive = mid_vocab - end_vocab - all_vocab

    print(f"\nExclusive tokens:")
    print(f"  End-folio only: {len(end_exclusive)}")
    print(f"  Mid-folio only: {len(mid_exclusive)}")

    if end_exclusive:
        print(f"    End examples: {list(end_exclusive)[:5]}")
    if mid_exclusive:
        print(f"    Mid examples: {list(mid_exclusive)[:5]}")

    return end_vocab, mid_vocab


def compare_morphology(end_folio, mid_folio):
    """Compare morphological profiles."""
    print("\n" + "="*70)
    print("TEST 2: MORPHOLOGICAL PROFILE")
    print("="*70)

    def get_prefix(token):
        return token[:2] if len(token) >= 2 else token

    def get_suffix(token):
        return token[-2:] if len(token) >= 2 else token

    end_prefixes = [get_prefix(t) for e in end_folio for t in e['tokens']]
    mid_prefixes = [get_prefix(t) for e in mid_folio for t in e['tokens']]

    end_prefix_counts = Counter(end_prefixes)
    mid_prefix_counts = Counter(mid_prefixes)

    end_total = sum(end_prefix_counts.values())
    mid_total = sum(mid_prefix_counts.values())

    print(f"\nPrefix distribution:")
    print(f"{'Prefix':<10} {'End-folio':<15} {'Mid-folio':<15} {'Difference':<12}")
    print("-"*55)

    all_prefixes = set(end_prefix_counts.keys()) | set(mid_prefix_counts.keys())
    diffs = []

    for prefix in all_prefixes:
        end_pct = end_prefix_counts.get(prefix, 0) / end_total if end_total else 0
        mid_pct = mid_prefix_counts.get(prefix, 0) / mid_total if mid_total else 0
        diff = end_pct - mid_pct
        diffs.append((prefix, end_pct, mid_pct, diff))

    # Show top divergent prefixes
    for prefix, end_pct, mid_pct, diff in sorted(diffs, key=lambda x: -abs(x[3]))[:10]:
        if end_pct > 0.02 or mid_pct > 0.02:
            print(f"{prefix:<10} {end_pct:>6.1%}          {mid_pct:>6.1%}          {diff:>+.1%}")

    return end_prefix_counts, mid_prefix_counts


def compare_token_structure(end_folio, mid_folio):
    """Compare token structure (length, complexity)."""
    print("\n" + "="*70)
    print("TEST 3: TOKEN STRUCTURE")
    print("="*70)

    end_lengths = [len(t) for e in end_folio for t in e['tokens']]
    mid_lengths = [len(t) for e in mid_folio for t in e['tokens']]

    print(f"\nToken length:")
    print(f"  End-folio: mean={np.mean(end_lengths):.1f}, median={np.median(end_lengths):.0f}")
    print(f"  Mid-folio: mean={np.mean(mid_lengths):.1f}, median={np.median(mid_lengths):.0f}")

    if end_lengths and mid_lengths:
        stat, p = stats.mannwhitneyu(end_lengths, mid_lengths, alternative='two-sided')
        print(f"  Mann-Whitney U p = {p:.4f}")
        print(f"  Interpretation: {'LENGTH DIFFERS' if p < 0.05 else 'SIMILAR LENGTH'}")

    # Check for common patterns
    print(f"\nToken pair patterns:")

    end_pairs = [tuple(sorted(e['tokens'])) for e in end_folio]
    mid_pairs = [tuple(sorted(e['tokens'])) for e in mid_folio]

    end_pair_counts = Counter(end_pairs)
    mid_pair_counts = Counter(mid_pairs)

    print(f"  Unique pairs in end-folio: {len(end_pair_counts)}")
    print(f"  Unique pairs in mid-folio: {len(mid_pair_counts)}")

    # Any repeated pairs?
    end_repeated = sum(1 for c in end_pair_counts.values() if c > 1)
    mid_repeated = sum(1 for c in mid_pair_counts.values() if c > 1)

    print(f"  Repeated pairs in end-folio: {end_repeated}")
    print(f"  Repeated pairs in mid-folio: {mid_repeated}")


def compare_internal_structure(end_folio, mid_folio):
    """Compare internal structure of 2-token pairs."""
    print("\n" + "="*70)
    print("TEST 4: INTERNAL PAIR STRUCTURE")
    print("="*70)

    def analyze_pair(tokens):
        """Analyze relationship between two tokens."""
        t1, t2 = tokens

        # Check prefix sharing
        p1 = t1[:2] if len(t1) >= 2 else t1
        p2 = t2[:2] if len(t2) >= 2 else t2
        same_prefix = p1 == p2

        # Check suffix sharing
        s1 = t1[-2:] if len(t1) >= 2 else t1
        s2 = t2[-2:] if len(t2) >= 2 else t2
        same_suffix = s1 == s2

        # Length similarity
        len_diff = abs(len(t1) - len(t2))

        return {
            'same_prefix': same_prefix,
            'same_suffix': same_suffix,
            'len_diff': len_diff
        }

    end_analysis = [analyze_pair(e['tokens']) for e in end_folio]
    mid_analysis = [analyze_pair(e['tokens']) for e in mid_folio]

    if end_analysis and mid_analysis:
        end_same_prefix = sum(1 for a in end_analysis if a['same_prefix']) / len(end_analysis)
        mid_same_prefix = sum(1 for a in mid_analysis if a['same_prefix']) / len(mid_analysis)

        end_same_suffix = sum(1 for a in end_analysis if a['same_suffix']) / len(end_analysis)
        mid_same_suffix = sum(1 for a in mid_analysis if a['same_suffix']) / len(mid_analysis)

        end_len_diff = np.mean([a['len_diff'] for a in end_analysis])
        mid_len_diff = np.mean([a['len_diff'] for a in mid_analysis])

        print(f"\nPair characteristics:")
        print(f"{'Metric':<25} {'End-folio':<15} {'Mid-folio':<15}")
        print("-"*55)
        print(f"{'Same prefix rate':<25} {end_same_prefix:>6.1%}          {mid_same_prefix:>6.1%}")
        print(f"{'Same suffix rate':<25} {end_same_suffix:>6.1%}          {mid_same_suffix:>6.1%}")
        print(f"{'Mean length difference':<25} {end_len_diff:>6.1f}          {mid_len_diff:>6.1f}")


def show_examples(end_folio, mid_folio):
    """Show example lines from each group."""
    print("\n" + "="*70)
    print("EXAMPLE LINES")
    print("="*70)

    print(f"\nEnd-folio 2-token lines ({len(end_folio)} total):")
    print(f"{'Folio':<10} {'Line':<6} {'Max':<6} {'Tokens':<40}")
    print("-"*65)
    for e in end_folio[:10]:
        tokens_str = " ".join(e['tokens'])
        print(f"{e['folio']:<10} {e['line_num']:<6} {e['max_line']:<6} {tokens_str:<40}")

    print(f"\nMid-folio 2-token lines ({len(mid_folio)} total):")
    print(f"{'Folio':<10} {'Line':<6} {'Max':<6} {'Tokens':<40}")
    print("-"*65)
    for e in mid_folio[:10]:
        tokens_str = " ".join(e['tokens'])
        print(f"{e['folio']:<10} {e['line_num']:<6} {e['max_line']:<6} {tokens_str:<40}")


def main():
    print("Loading data...")
    lines, folio_max = load_data()
    print(f"Loaded {len(lines)} A lines")

    # Split 2-token lines
    end_folio, mid_folio = split_two_token_lines(lines, folio_max)
    print(f"\n2-token lines: {len(end_folio)} end-folio, {len(mid_folio)} mid-folio")

    # Run comparisons
    compare_vocabulary(end_folio, mid_folio, lines)
    compare_morphology(end_folio, mid_folio)
    compare_token_structure(end_folio, mid_folio)
    compare_internal_structure(end_folio, mid_folio)
    show_examples(end_folio, mid_folio)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"""
Distribution:
  End-folio 2-token lines: {len(end_folio)} ({100*len(end_folio)/(len(end_folio)+len(mid_folio)):.1f}%)
  Mid-folio 2-token lines: {len(mid_folio)} ({100*len(mid_folio)/(len(end_folio)+len(mid_folio)):.1f}%)
""")

    if len(end_folio) > len(mid_folio) * 2:
        print("FINDING: 2-token lines are PREDOMINANTLY scope-closers")
        print("         Strong end-folio bias confirms structural closing role")
    elif len(end_folio) > len(mid_folio):
        print("FINDING: 2-token lines have MODERATE end-folio bias")
        print("         Dual role: minimal entries + scope-closing function")
    else:
        print("FINDING: 2-token lines are DISTRIBUTED throughout folios")
        print("         Primarily compressed normal entries")


if __name__ == '__main__':
    main()
