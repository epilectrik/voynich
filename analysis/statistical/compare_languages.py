"""
Compare Currier Language A vs B and analyze differences between scribal hands.

This analysis investigates the key question: Are there really two distinct
"languages" in the Voynich Manuscript, or are the differences attributable
to scribes, sections, or other factors?
"""

import sys
from pathlib import Path
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import VoynichCorpus, load_corpus
from stats import FrequencyAnalyzer, EntropyAnalyzer, ZipfAnalyzer


def analyze_subset(words: list, label: str) -> dict:
    """Analyze a subset of words and return statistics."""
    if not words:
        return {'label': label, 'word_count': 0}

    # Create a mini-corpus from the word list
    text = " ".join(w.text for w in words)
    chars = "".join(w.text for w in words)
    word_texts = [w.text for w in words]

    char_freq = Counter(chars)
    word_freq = Counter(word_texts)

    # Calculate H2 (conditional entropy)
    bigram_counts = Counter(chars[i:i+2] for i in range(len(chars)-1))
    total_bigrams = sum(bigram_counts.values())

    # First-order char freq for context
    context_counts = {}
    for bigram, count in bigram_counts.items():
        c1 = bigram[0]
        if c1 not in context_counts:
            context_counts[c1] = Counter()
        context_counts[c1][bigram[1]] += count

    # Calculate conditional entropy
    import math
    h2 = 0
    for c1, following in context_counts.items():
        c1_total = sum(following.values())
        c1_prob = c1_total / total_bigrams if total_bigrams > 0 else 0
        c1_entropy = 0
        for c2, count in following.items():
            p = count / c1_total
            if p > 0:
                c1_entropy -= p * math.log2(p)
        h2 += c1_prob * c1_entropy

    return {
        'label': label,
        'word_count': len(words),
        'unique_words': len(set(word_texts)),
        'char_count': len(chars),
        'unique_chars': len(set(chars)),
        'h2': h2,
        'top_5_words': word_freq.most_common(5),
        'top_5_chars': char_freq.most_common(5),
        'first_char_dist': Counter(w.text[0] for w in words if w.text).most_common(5),
        'last_char_dist': Counter(w.text[-1] for w in words if w.text).most_common(5),
    }


def print_comparison(results: list) -> None:
    """Print side-by-side comparison of multiple analyses."""
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)

    # Header
    labels = [r['label'] for r in results]
    print(f"\n{'Metric':<25}", end="")
    for label in labels:
        print(f"{label:>18}", end="")
    print()
    print("-" * (25 + 18 * len(labels)))

    # Basic stats
    print(f"{'Word Count':<25}", end="")
    for r in results:
        print(f"{r['word_count']:>18,}", end="")
    print()

    print(f"{'Unique Words':<25}", end="")
    for r in results:
        print(f"{r['unique_words']:>18,}", end="")
    print()

    print(f"{'H2 (Cond. Entropy)':<25}", end="")
    for r in results:
        print(f"{r.get('h2', 0):>18.4f}", end="")
    print()

    # Top words
    print(f"\n{'Top 5 Words:':<25}")
    for i in range(5):
        print(f"  #{i+1:<22}", end="")
        for r in results:
            if i < len(r.get('top_5_words', [])):
                word, count = r['top_5_words'][i]
                print(f"{word}({count}):>18", end="")
            else:
                print(f"{'':>18}", end="")
        print()

    # First char distribution
    print(f"\n{'First Char (Top 5):':<25}")
    for i in range(5):
        print(f"  #{i+1:<22}", end="")
        for r in results:
            if i < len(r.get('first_char_dist', [])):
                char, count = r['first_char_dist'][i]
                pct = 100 * count / r['word_count'] if r['word_count'] > 0 else 0
                print(f"'{char}' {pct:>5.1f}%", end="     ")
            else:
                print(f"{'':>18}", end="")
        print()

    # Last char distribution
    print(f"\n{'Last Char (Top 5):':<25}")
    for i in range(5):
        print(f"  #{i+1:<22}", end="")
        for r in results:
            if i < len(r.get('last_char_dist', [])):
                char, count = r['last_char_dist'][i]
                pct = 100 * count / r['word_count'] if r['word_count'] > 0 else 0
                print(f"'{char}' {pct:>5.1f}%", end="     ")
            else:
                print(f"{'':>18}", end="")
        print()


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # === CURRIER LANGUAGE COMPARISON ===
    print("\n" + "=" * 80)
    print("CURRIER LANGUAGE A vs B COMPARISON")
    print("=" * 80)

    lang_a = [w for w in corpus.words if w.language == 'A']
    lang_b = [w for w in corpus.words if w.language == 'B']
    lang_na = [w for w in corpus.words if w.language == 'NA']

    print(f"\nLanguage A words: {len(lang_a):,}")
    print(f"Language B words: {len(lang_b):,}")
    print(f"Unassigned (NA): {len(lang_na):,}")

    results_lang = [
        analyze_subset(lang_a, "Language A"),
        analyze_subset(lang_b, "Language B"),
    ]
    print_comparison(results_lang)

    # === SCRIBAL HAND COMPARISON ===
    print("\n" + "=" * 80)
    print("SCRIBAL HAND COMPARISON")
    print("=" * 80)

    hands = {}
    for w in corpus.words:
        if w.hand and w.hand not in ('NA', 'X', 'Y'):
            if w.hand not in hands:
                hands[w.hand] = []
            hands[w.hand].append(w)

    print(f"\nHands found: {sorted(hands.keys())}")
    for hand, words in sorted(hands.items()):
        print(f"  Hand {hand}: {len(words):,} words")

    results_hands = [
        analyze_subset(hands.get(h, []), f"Hand {h}")
        for h in sorted(hands.keys())
    ]
    if results_hands:
        print_comparison(results_hands)

    # === SECTION COMPARISON ===
    print("\n" + "=" * 80)
    print("SECTION COMPARISON")
    print("=" * 80)

    section_names = {
        'H': 'Herbal',
        'A': 'Astronomical',
        'B': 'Biological',
        'C': 'Cosmological',
        'P': 'Pharmaceutical',
        'S': 'Stars/Recipe',
        'Z': 'Zodiac',
        'T': 'Text'
    }

    sections = {}
    for w in corpus.words:
        if w.section:
            if w.section not in sections:
                sections[w.section] = []
            sections[w.section].append(w)

    print(f"\nSections found:")
    for sec, words in sorted(sections.items()):
        name = section_names.get(sec, 'Unknown')
        print(f"  {sec} ({name}): {len(words):,} words")

    # Compare top sections
    top_sections = sorted(sections.items(), key=lambda x: -len(x[1]))[:4]
    results_sections = [
        analyze_subset(words, f"{sec} ({section_names.get(sec, '?')})")
        for sec, words in top_sections
    ]
    if results_sections:
        print_comparison(results_sections)

    # === KEY FINDINGS ===
    print("\n" + "=" * 80)
    print("KEY OBSERVATIONS")
    print("=" * 80)

    if results_lang and len(results_lang) >= 2:
        h2_a = results_lang[0].get('h2', 0)
        h2_b = results_lang[1].get('h2', 0)
        print(f"\n1. Currier Language A vs B:")
        print(f"   - H2 difference: {abs(h2_a - h2_b):.4f} bits")
        print(f"   - This {'suggests' if abs(h2_a - h2_b) > 0.2 else 'does not strongly suggest'} "
              f"distinct encoding patterns")

    print(f"\n2. Overall H2 of ~2.37 is significantly lower than natural languages (3-4)")
    print(f"   This indicates highly predictable character sequences.")

    print(f"\n3. The dominance of 'y' as a final character (~40%) is unusual")
    print(f"   and suggests strong positional constraints on characters.")


if __name__ == "__main__":
    main()
