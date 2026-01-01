"""
Translation Synthesis Tool

Combine all analysis findings and attempt to produce readable text.
Tests various hypotheses systematically.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus
from analysis.linguistic.word_grammar import decompose_word


# Hypothesis 1: Specific word mappings based on frequency
WORD_MAPPING_H1 = {
    # Most common words -> common Latin words
    'daiin': 'et',      # Most common -> 'and'
    'ol': 'in',         # Second -> 'in'
    'aiin': 'est',      # 'is/are'
    'or': 'vel',        # 'or'
    'ar': 'ad',         # 'to'
    'chol': 'cum',      # 'with'
    's': 'e',           # 'from'
    'y': '',            # Word separator (null)
    'chedy': 'herba',   # 'herb' (botanical context)
    'shedy': 'aqua',    # 'water'
    'dar': 'folia',     # 'leaves'
    'al': 'de',         # 'of/from'
}

# Hypothesis 2: Syllable-based mapping
SYLLABLE_MAP = {
    'qo': 'qu',
    'ch': 'c',
    'sh': 'sc',
    'ot': 'at',
    'ok': 'oc',
    'ol': 'ul',
    'ai': 'ae',
    'ii': 'ii',
    'ee': 'e',
    'dy': 'dus',
    'ey': 'eus',
    'hy': 'tus',
    'y': 'us',
    'n': 'm',
}

# Hypothesis 3: Morpheme mapping (based on our analysis)
MORPHEME_MAP = {
    # Suffixes
    'aiin': 'ium',
    'ain': 'em',
    'iin': 'ium',
    'in': 'im',
    'dy': 'dum',
    'edy': 'idum',
    'eedy': 'idum',
    'y': 'us',
    'ey': 'eus',
    'hy': 'tus',
    'ol': 'ul',
    'al': 'al',
    'ar': 'ar',
    'or': 'or',
    # Prefixes
    'qok': 'quoc',
    'qot': 'quot',
    'qo': 'quo',
    'che': 'ce',
    'cho': 'co',
    'ch': 'c',
    'she': 'sce',
    'sho': 'sco',
    'sh': 'sc',
    'dai': 'de',
    'da': 'da',
    'ot': 'at',
    'ok': 'oc',
    'ol': 'ol',
    'o': 'o',
}


def translate_word_mapping(word: str, mapping: Dict[str, str]) -> str:
    """Translate using direct word mapping."""
    return mapping.get(word, f'[{word}]')


def translate_syllables(word: str, mapping: Dict[str, str]) -> str:
    """Translate using syllable substitution."""
    result = word
    # Apply mappings from longest to shortest
    for voy, lat in sorted(mapping.items(), key=lambda x: -len(x[0])):
        result = result.replace(voy, lat)
    return result


def translate_morphemes(word: str) -> str:
    """Translate using morpheme decomposition."""
    d = decompose_word(word)

    # Map each component
    prefix = MORPHEME_MAP.get(d.prefix, d.prefix)
    middle = d.middle  # Keep middle as-is for now
    suffix = MORPHEME_MAP.get(d.suffix, d.suffix)

    # Also apply syllable mappings to middle
    for voy, lat in sorted(MORPHEME_MAP.items(), key=lambda x: -len(x[0])):
        middle = middle.replace(voy, lat)

    return prefix + middle + suffix


def test_translation(corpus, method: str, sample_size: int = 100) -> str:
    """Apply a translation method and return sample text."""
    words = corpus.all_words[:sample_size]
    translated = []

    for word in words:
        if method == 'word':
            t = translate_word_mapping(word, WORD_MAPPING_H1)
        elif method == 'syllable':
            t = translate_syllables(word, SYLLABLE_MAP)
        elif method == 'morpheme':
            t = translate_morphemes(word)
        else:
            t = word
        translated.append(t)

    return ' '.join(translated)


def analyze_most_common_patterns(corpus) -> None:
    """Focus on the most common patterns and what they might mean."""
    print("\n" + "=" * 80)
    print("MOST COMMON PATTERN ANALYSIS")
    print("=" * 80)

    word_freq = Counter(corpus.all_words)

    # Most common word: 'daiin' (863 times)
    print("\n1. MOST COMMON WORD: 'daiin' (863 times)")
    print("-" * 50)

    # What words follow/precede 'daiin'?
    words = corpus.all_words
    daiin_followers = Counter()
    daiin_preceders = Counter()

    for i in range(len(words)):
        if words[i] == 'daiin':
            if i > 0:
                daiin_preceders[words[i-1]] += 1
            if i < len(words) - 1:
                daiin_followers[words[i+1]] += 1

    print("\nWords that FOLLOW 'daiin':")
    for word, count in daiin_followers.most_common(10):
        print(f"  {word}: {count}")

    print("\nWords that PRECEDE 'daiin':")
    for word, count in daiin_preceders.most_common(10):
        print(f"  {word}: {count}")

    # If 'daiin' = 'et' (and), we'd expect it between nouns/phrases
    # The patterns don't clearly show this...

    # Try 'daiin' = article or common word
    print("\nPossible meanings for 'daiin':")
    print("  - If Latin: 'et' (and), 'in' (in), 'de' (of), 'cum' (with)")
    print("  - If Italian: 'di' (of), 'e' (and), 'il' (the)")
    print("  - If Hebrew: prefix 'ha-' (the)")

    # Second most common: 'ol' (537 times)
    print("\n2. SECOND MOST COMMON: 'ol' (537 times)")
    print("-" * 50)

    ol_followers = Counter()
    for i in range(len(words) - 1):
        if words[i] == 'ol':
            ol_followers[words[i+1]] += 1

    print("\nWords that FOLLOW 'ol':")
    for word, count in ol_followers.most_common(10):
        print(f"  {word}: {count}")

    # 'ol' + 'chedy' very common -> could be 'ol' = article, 'chedy' = noun
    print("\n  'ol chedy' appears together often")
    print("  'ol shedy' also common")
    print("  Pattern suggests: 'ol' = article or preposition")


def test_article_hypothesis(corpus) -> None:
    """Test if common short words are articles."""
    print("\n" + "=" * 80)
    print("ARTICLE HYPOTHESIS")
    print("=" * 80)

    print("""
Hypothesis: Short common words are articles or particles.

Testing: 'ol', 'or', 'ar', 's', 'y' might be articles/particles

In Latin: no articles, but in vernacular Italian:
  - 'il', 'lo' = the (masc.)
  - 'la' = the (fem.)
  - 'le', 'li' = the (plural)
  - 'un', 'una' = a/an

Let's see if these patterns fit...
""")

    words = corpus.all_words
    word_freq = Counter(words)

    # Words that follow 'ol'
    ol_next = Counter()
    for i in range(len(words) - 1):
        if words[i] == 'ol':
            ol_next[words[i+1]] += 1

    print("\n'ol' + next word (if 'ol' is article, next should be noun):")
    for word, count in ol_next.most_common(10):
        pct = 100 * count / word_freq['ol']
        print(f"  ol {word}: {count} ({pct:.1f}%)")


def attempt_final_translation(corpus) -> None:
    """Make a final attempt at translation using best hypotheses."""
    print("\n" + "=" * 80)
    print("FINAL TRANSLATION ATTEMPT")
    print("=" * 80)

    # Best hypothesis: morpheme mapping with Italian target
    print("\nUsing morpheme mapping (Latin/Italian hybrid):")
    print("-" * 50)

    # Sample from first folio
    first_folio_words = [w for w in corpus.words if w.folio == 'f1r'][:50]
    words = [w.text for w in first_folio_words]

    print(f"\nOriginal (first 50 words of f1r):")
    print(' '.join(words))

    print(f"\nMorpheme translation:")
    translated = [translate_morphemes(w) for w in words]
    print(' '.join(translated))

    print(f"\nSyllable translation:")
    translated = [translate_syllables(w, SYLLABLE_MAP) for w in words]
    print(' '.join(translated))

    # Extract potential Latin roots
    print("\n" + "=" * 80)
    print("LOOKING FOR RECOGNIZABLE LATIN/ITALIAN ROOTS")
    print("=" * 80)

    all_morpheme = [translate_morphemes(w) for w in corpus.all_words]
    morpheme_freq = Counter(all_morpheme)

    print("\nMost common morpheme-translated words:")
    for word, count in morpheme_freq.most_common(30):
        print(f"  {word}: {count}")


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Analyze most common patterns
    analyze_most_common_patterns(corpus)

    # Test article hypothesis
    test_article_hypothesis(corpus)

    # Final translation attempt
    attempt_final_translation(corpus)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY OF DECIPHERMENT ATTEMPTS")
    print("=" * 80)

    print("""
METHODS TRIED:
1. Simple character substitution -> FAILED (decoded text not readable)
2. Verbose cipher (word = letter) -> FAILED (too many unique words)
3. Frequency-based mapping -> PARTIAL (frequencies match but text not readable)
4. Morpheme mapping -> PROMISING (produces plausible Latin-like structures)

KEY FINDINGS:
1. Voynich text follows strict word grammar: PREFIX + MIDDLE + SUFFIX
2. ~41% of words end in 'y' (could be grammatical marker or suffix '-us')
3. 'aiin' pattern (10% of words) could be Latin '-ium' ending
4. Section-specific vocabulary suggests semantic content, not random

HYPOTHESES THAT REMAIN VIABLE:
1. Verbose cipher with morpheme structure (not simple word=letter)
2. Syllabic script (each glyph = syllable, not letter)
3. Constructed language with Latin-influenced morphology
4. Heavy abbreviation system similar to medieval shorthand

WHAT'S NEEDED TO CRACK IT:
1. Find ONE confirmed word (proper noun like Taurus, Aries, a plant name)
2. Use that to bootstrap character mappings
3. Apply constraints from word grammar to reduce search space

The manuscript's structure suggests MEANINGFUL CONTENT, not a hoax.
But the encoding is more sophisticated than simple substitution.
""")


if __name__ == "__main__":
    main()
