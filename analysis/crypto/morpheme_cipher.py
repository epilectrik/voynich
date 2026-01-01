"""
Morpheme-Based Cipher Analysis

Instead of character-by-character substitution, try mapping:
- Voynich SUFFIXES -> Latin ENDINGS (-us, -um, -is, etc.)
- Voynich PREFIXES -> Latin word beginnings
- Voynich MIDDLES -> Latin roots

This accounts for the strict Voynich word grammar.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import itertools

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus
from analysis.linguistic.word_grammar import decompose_word, KNOWN_PREFIXES, KNOWN_SUFFIXES


# Common Latin word endings (by frequency)
LATIN_ENDINGS = {
    'us': 0.12,   # nominative sing. masc. (2nd decl)
    'um': 0.10,   # accusative sing. (2nd decl)
    'is': 0.09,   # genitive sing., dat/abl plural
    'a': 0.08,    # nominative sing. fem. (1st decl)
    'ae': 0.07,   # genitive/dative sing. (1st decl)
    'i': 0.06,    # nominative plural (2nd decl)
    'am': 0.05,   # accusative sing. (1st decl)
    'as': 0.04,   # accusative plural (1st decl)
    'e': 0.04,    # ablative sing., vocative
    'em': 0.03,   # accusative sing. (3rd decl)
    'es': 0.03,   # nominative/accusative plural (3rd decl)
    'o': 0.03,    # ablative sing. (2nd decl)
    'orum': 0.02, # genitive plural (2nd decl)
    'arum': 0.02, # genitive plural (1st decl)
    'ibus': 0.02, # dative/ablative plural (3rd decl)
    'unt': 0.02,  # 3rd person plural present
    'it': 0.02,   # 3rd person singular present
    'tur': 0.01,  # passive verb ending
}

# Common Latin word beginnings
LATIN_BEGINNINGS = {
    'con': 0.05,  # prefix: with/together
    'in': 0.05,   # prefix: in/into
    'de': 0.04,   # prefix: down/from
    'ex': 0.03,   # prefix: out of
    'pro': 0.03,  # prefix: forward
    'ad': 0.03,   # prefix: to/toward
    'dis': 0.02,  # prefix: apart
    'per': 0.02,  # prefix: through
    'sub': 0.02,  # prefix: under
    'trans': 0.01, # prefix: across
    'qu': 0.04,   # common start (qui, quod, etc.)
    'et': 0.03,   # and (standalone)
}


def analyze_suffix_mapping(corpus) -> Dict:
    """
    Analyze if Voynich suffixes could map to Latin endings.
    Key question: Does 'y' (41% of endings) = Latin 'us' or 'um'?
    """
    # Get Voynich suffix frequencies
    suffix_counts = Counter()
    total_words = 0

    for word in corpus.all_words:
        d = decompose_word(word)
        if d.suffix:
            suffix_counts[d.suffix] += 1
        total_words += 1

    voy_suffix_freq = {s: c/total_words for s, c in suffix_counts.items()}

    # Compare to Latin endings
    results = {}

    print("\nVoynich suffix vs Latin ending frequency comparison:")
    print(f"{'Voy Suffix':<12} {'Voy %':>8} | {'Latin End':<10} {'Latin %':>8}")
    print("-" * 50)

    voy_sorted = sorted(voy_suffix_freq.items(), key=lambda x: -x[1])[:15]
    lat_sorted = sorted(LATIN_ENDINGS.items(), key=lambda x: -x[1])[:15]

    for (vs, vf), (le, lf) in zip(voy_sorted, lat_sorted):
        print(f"{vs:<12} {vf*100:>7.2f}% | {le:<10} {lf*100:>7.2f}%")
        results[vs] = le

    return results


def test_suffix_mapping(corpus, suffix_map: Dict[str, str]) -> str:
    """
    Apply suffix mapping and see if it produces Latin-like text.
    Replace Voynich suffixes with Latin endings.
    """
    decoded_words = []

    for word in corpus.all_words[:1000]:  # Sample
        d = decompose_word(word)

        # Keep prefix and middle, replace suffix
        latin_ending = suffix_map.get(d.suffix, d.suffix)
        decoded = d.prefix + d.middle + latin_ending

        decoded_words.append(decoded)

    return ' '.join(decoded_words)


def find_y_mapping(corpus) -> Dict:
    """
    'y' ends 41% of Voynich words. What Latin ending could it represent?

    Options:
    1. 'y' = 'us' (nominative masculine singular)
    2. 'y' = 'um' (accusative neuter singular)
    3. 'y' = 'is' (genitive singular)
    4. 'y' = word separator (not an ending at all)
    """
    results = {}

    # Get words ending in 'y'
    y_words = [w for w in corpus.all_words if w.endswith('y')]
    non_y_words = [w for w in corpus.all_words if not w.endswith('y')]

    print(f"\nWords ending in 'y': {len(y_words)} ({100*len(y_words)/len(corpus.all_words):.1f}%)")
    print(f"Words NOT ending in 'y': {len(non_y_words)}")

    # If 'y' = 'us', strip 'y' and add 'us'
    print("\n" + "=" * 60)
    print("HYPOTHESIS: Voynich 'y' = Latin 'us'")
    print("=" * 60)

    # Test on most common y-words
    y_freq = Counter(y_words)
    print("\nMost common y-words converted to -us:")
    for word, count in y_freq.most_common(20):
        without_y = word[:-1] if word.endswith('y') else word
        converted = without_y + 'us'
        print(f"  {word:<15} -> {converted:<15} ({count} occurrences)")

    # Check if -dy might be different from -y
    print("\n" + "=" * 60)
    print("ANALYZING -dy vs -y endings")
    print("=" * 60)

    dy_words = [w for w in corpus.all_words if w.endswith('dy')]
    edy_words = [w for w in corpus.all_words if w.endswith('edy')]

    print(f"\nWords ending in -dy: {len(dy_words)}")
    print(f"Words ending in -edy: {len(edy_words)}")

    print("\nMost common -dy words:")
    for word, count in Counter(dy_words).most_common(10):
        print(f"  {word}: {count}")

    print("\nMost common -edy words:")
    for word, count in Counter(edy_words).most_common(10):
        print(f"  {word}: {count}")

    return results


def test_word_boundary_hypothesis(corpus) -> None:
    """
    Test hypothesis: 'y' is a word separator, not part of the word.
    If true, 'chedy' = 'ched' + separator, 'shedy' = 'shed' + separator.
    """
    print("\n" + "=" * 60)
    print("HYPOTHESIS: 'y' is a WORD SEPARATOR")
    print("=" * 60)

    # Strip all trailing 'y' and analyze the remaining patterns
    stripped_words = []
    for word in corpus.all_words:
        if word.endswith('y'):
            stripped_words.append(word[:-1])
        else:
            stripped_words.append(word)

    stripped_freq = Counter(stripped_words)

    print("\nMost common words after stripping 'y':")
    for word, count in stripped_freq.most_common(20):
        print(f"  {word}: {count}")

    # Compare to Latin word frequency patterns
    # If these look more like Latin roots, the hypothesis gains support

    print("\nAfter stripping 'y', unique words:", len(set(stripped_words)))
    print("Before stripping, unique words:", len(set(corpus.all_words)))


def analyze_aiin_pattern(corpus) -> None:
    """
    'aiin' is one of the most common endings. What could it be?
    It appears in 'daiin', 'aiin', 'otaiin', 'qokaiin', etc.
    """
    print("\n" + "=" * 60)
    print("ANALYZING THE '-aiin' PATTERN")
    print("=" * 60)

    aiin_words = [w for w in corpus.all_words if 'aiin' in w]
    print(f"\nWords containing 'aiin': {len(aiin_words)}")

    aiin_freq = Counter(aiin_words)
    print("\nMost common 'aiin' words:")
    for word, count in aiin_freq.most_common(15):
        print(f"  {word}: {count}")

    # What if 'aiin' = Latin '-ium' (neuter noun ending)?
    print("\nHypothesis: 'aiin' = Latin '-ium' (neuter noun ending)")
    print("Examples: herbarium, remedium, mysterium")


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Suffix mapping analysis
    print("=" * 80)
    print("MORPHEME-BASED CIPHER ANALYSIS")
    print("=" * 80)

    suffix_map = analyze_suffix_mapping(corpus)

    # Analyze 'y' ending
    find_y_mapping(corpus)

    # Test word boundary hypothesis
    test_word_boundary_hypothesis(corpus)

    # Analyze 'aiin' pattern
    analyze_aiin_pattern(corpus)

    # Final synthesis
    print("\n" + "=" * 80)
    print("SYNTHESIS: PROPOSED MORPHEME MAPPINGS")
    print("=" * 80)

    print("""
Based on frequency analysis, here are tentative morpheme mappings:

VOYNICH SUFFIX    POSSIBLE LATIN       REASONING
---------------------------------------------------------
-y                -us / -um            Most common (41%), matches Latin nominative
-dy               -dum / -dus          Second most common (9%)
-aiin             -ium                 Common, looks like neuter noun ending
-in               -in / -em            Direct parallel
-ol               -ol- / -ul-          Could be root, not ending
-ar               -ar(e) / -er(e)      Verb infinitive marker?
-or               -or(is)              Could be 3rd decl noun
-al               -al(is)              Adjective ending

VOYNICH PREFIX    POSSIBLE LATIN       REASONING
---------------------------------------------------------
qo-               quo- / qu-           Matches Latin interrogative
ch-               c(h)- / ch-          Could be 'k' sound
sh-               s(c)- / sch-         Possibly 'sc' or 'sch'
ot-               ot- / at-            Could be Latin 'at' or 'aut'
da-               da- / de-            Latin preposition 'de'

These mappings need testing with actual text to see if they produce
readable Latin. The key test: apply mappings and check for known Latin words.
""")


if __name__ == "__main__":
    main()
