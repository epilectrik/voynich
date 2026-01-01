"""
Positional Character Constraint Analyzer for Voynich Manuscript

Analyzes which characters can appear in which positions within words,
revealing the strict positional rules that characterize Voynichese.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


def analyze_position_constraints(corpus):
    """Analyze character constraints by position in word."""

    # Position categories
    positions = {
        'first': Counter(),
        'second': Counter(),
        'middle': Counter(),  # not first, second, penultimate, or last
        'penultimate': Counter(),
        'last': Counter(),
    }

    # Track which positions each character appears in
    char_positions = defaultdict(set)

    for word in corpus.all_words:
        if len(word) >= 1:
            positions['first'][word[0]] += 1
            positions['last'][word[-1]] += 1
            char_positions[word[0]].add('first')
            char_positions[word[-1]].add('last')

        if len(word) >= 2:
            positions['second'][word[1]] += 1
            positions['penultimate'][word[-2]] += 1
            char_positions[word[1]].add('second')
            char_positions[word[-2]].add('penultimate')

        if len(word) >= 5:
            for c in word[2:-2]:
                positions['middle'][c] += 1
                char_positions[c].add('middle')

    return positions, char_positions


def analyze_bigram_constraints(corpus):
    """Find which character pairs never occur."""
    all_chars = set(corpus.all_characters)
    observed_bigrams = set()

    for word in corpus.all_words:
        for i in range(len(word) - 1):
            observed_bigrams.add((word[i], word[i+1]))

    # Theoretical possible bigrams
    possible = set()
    for c1 in all_chars:
        for c2 in all_chars:
            possible.add((c1, c2))

    never_occur = possible - observed_bigrams

    return observed_bigrams, never_occur, all_chars


def analyze_word_beginnings_endings(corpus):
    """Analyze common word beginnings and endings."""
    prefix_2 = Counter(w[:2] for w in corpus.all_words if len(w) >= 2)
    prefix_3 = Counter(w[:3] for w in corpus.all_words if len(w) >= 3)
    suffix_2 = Counter(w[-2:] for w in corpus.all_words if len(w) >= 2)
    suffix_3 = Counter(w[-3:] for w in corpus.all_words if len(w) >= 3)

    return prefix_2, prefix_3, suffix_2, suffix_3


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words with {len(set(corpus.all_characters))} unique characters\n")

    all_chars = sorted(set(corpus.all_characters))
    print(f"Character set: {''.join(all_chars)}\n")

    # === POSITION ANALYSIS ===
    print("=" * 80)
    print("POSITIONAL CHARACTER DISTRIBUTION")
    print("=" * 80)

    positions, char_positions = analyze_position_constraints(corpus)

    for pos_name, counter in positions.items():
        total = sum(counter.values())
        print(f"\n{pos_name.upper()} position (n={total:,}):")
        for char, count in counter.most_common(10):
            pct = 100 * count / total
            bar = "#" * int(pct / 2)
            print(f"  '{char}': {count:>6,} ({pct:>5.1f}%) {bar}")

    # === CHARACTER RESTRICTIONS ===
    print("\n" + "=" * 80)
    print("CHARACTER POSITION RESTRICTIONS")
    print("=" * 80)
    print("\nCharacters that NEVER appear in certain positions:")

    all_positions = {'first', 'second', 'middle', 'penultimate', 'last'}

    for char in sorted(all_chars):
        positions_present = char_positions[char]
        positions_absent = all_positions - positions_present
        if positions_absent:
            print(f"  '{char}' never appears: {', '.join(sorted(positions_absent))}")

    # === BIGRAM CONSTRAINTS ===
    print("\n" + "=" * 80)
    print("BIGRAM (CHARACTER PAIR) CONSTRAINTS")
    print("=" * 80)

    observed, never, all_c = analyze_bigram_constraints(corpus)

    print(f"\nPossible bigrams: {len(all_c) * len(all_c)}")
    print(f"Observed bigrams: {len(observed)}")
    print(f"Never-occurring bigrams: {len(never)}")
    print(f"Observed percentage: {100 * len(observed) / (len(all_c) * len(all_c)):.1f}%")

    # Characters that never follow specific characters
    print("\n--- Characters that NEVER follow 'a': ---")
    never_after_a = [c2 for (c1, c2) in never if c1 == 'a']
    print(f"  {''.join(sorted(never_after_a)) if never_after_a else 'None - all characters can follow a'}")

    print("\n--- Characters that NEVER follow 'o': ---")
    never_after_o = [c2 for (c1, c2) in never if c1 == 'o']
    print(f"  {''.join(sorted(never_after_o)) if never_after_o else 'None - all characters can follow o'}")

    print("\n--- Characters that NEVER follow 'y': ---")
    never_after_y = [c2 for (c1, c2) in never if c1 == 'y']
    print(f"  {''.join(sorted(never_after_y)) if never_after_y else 'None'}")

    # Characters that never precede others
    print("\n--- Characters that NEVER precede 'y': ---")
    never_before_y = [c1 for (c1, c2) in never if c2 == 'y']
    print(f"  {''.join(sorted(never_before_y)) if never_before_y else 'None - all characters can precede y'}")

    # === COMMON PATTERNS ===
    print("\n" + "=" * 80)
    print("COMMON WORD PATTERNS")
    print("=" * 80)

    prefix_2, prefix_3, suffix_2, suffix_3 = analyze_word_beginnings_endings(corpus)

    print("\nTop 15 two-character prefixes:")
    for prefix, count in prefix_2.most_common(15):
        print(f"  {prefix}: {count:>5,}")

    print("\nTop 15 three-character prefixes:")
    for prefix, count in prefix_3.most_common(15):
        print(f"  {prefix}: {count:>5,}")

    print("\nTop 15 two-character suffixes:")
    for suffix, count in suffix_2.most_common(15):
        print(f"  {suffix}: {count:>5,}")

    print("\nTop 15 three-character suffixes:")
    for suffix, count in suffix_3.most_common(15):
        print(f"  {suffix}: {count:>5,}")

    # === KEY INSIGHTS ===
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    # Calculate what percentage of words end with common suffixes
    common_suffixes = ['y', 'dy', 'edy', 'aiin', 'ain', 'in']
    print("\nCoverage of common suffixes:")
    total_words = len(corpus.all_words)
    for suf in common_suffixes:
        count = sum(1 for w in corpus.all_words if w.endswith(suf))
        print(f"  Words ending in '{suf}': {count:>6,} ({100*count/total_words:.1f}%)")

    # Common prefixes coverage
    common_prefixes = ['qo', 'ch', 'sh', 'ol', 'da', 'ot']
    print("\nCoverage of common prefixes:")
    for pre in common_prefixes:
        count = sum(1 for w in corpus.all_words if w.startswith(pre))
        print(f"  Words starting with '{pre}': {count:>6,} ({100*count/total_words:.1f}%)")

    print("\n" + "=" * 80)
    print("VOYNICH WORD STRUCTURE HYPOTHESIS")
    print("=" * 80)
    print("""
Based on the analysis, Voynich words appear to follow a pattern:

    [INITIAL GLYPH] + [MIDFIX] + [SUFFIX]

Where:
- INITIAL GLYPHS: Limited set (q-, ch-, sh-, d-, o-, s-, etc.)
- MIDFIX: Optional elaboration (ol, eo, ai, ok, etc.)
- SUFFIX: Highly constrained (-y, -dy, -aiin, -in, -ar, -or, etc.)

This tripartite structure explains:
1. The low H2 (predictable sequences)
2. The strict positional constraints
3. The apparent morphological regularity

The question remains: Is this an encoding scheme or a constructed language?
""")


if __name__ == "__main__":
    main()
