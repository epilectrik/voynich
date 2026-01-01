"""
Taurus Identification Attack

The Taurus folio (f71r) shows a clear bull image. If we can identify which
Voynich word represents "Taurus" (or bull-related terms), we have a foothold.

Known facts:
- f71r contains the Taurus zodiac diagram
- "Taurus" in Latin, "Toro" in Italian, "Tor/Stier" in German
- The word should appear on this folio, possibly multiple times
- It should NOT appear (or rarely) on other zodiac folios

Strategy:
1. Find words UNIQUE to f71r (appear there but nowhere else in zodiac)
2. Among those, find words that could phonetically match "Taurus"
3. Test if the character mapping generalizes to other proper nouns
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

# Known name forms to match against
TAURUS_FORMS = {
    'taurus': 'Latin nominative',
    'tauri': 'Latin genitive',
    'tauro': 'Latin dative/ablative',
    'taurum': 'Latin accusative',
    'toro': 'Italian/Spanish',
    'tor': 'abbreviated',
    'bull': 'English',
    'bos': 'Latin for ox/cow',
    'bovis': 'Latin genitive',
}

# Zodiac folios - we'll compare f71r (Taurus) against others
ZODIAC_FOLIOS = {
    'f70v': 'Pisces/Aries',
    'f71r': 'Taurus',
    'f71v': 'Gemini',
    'f72r': 'Cancer/Leo/Virgo',
    'f72v': 'Libra/Scorpio/Sagittarius',
    'f73r': 'Capricorn',
    'f73v': 'Aquarius',
}


def extract_folio_words(corpus, folio_prefix: str) -> List[str]:
    """Extract all words from folios matching the prefix."""
    words = []
    for word in corpus.words:
        if word.folio.startswith(folio_prefix):
            words.append(word.text)
    return words


def find_folio_unique_words(corpus) -> Dict[str, Set[str]]:
    """Find words that appear on only ONE zodiac folio."""
    folio_words = {}
    all_zodiac_words = set()

    for folio_prefix in ZODIAC_FOLIOS.keys():
        words = extract_folio_words(corpus, folio_prefix)
        folio_words[folio_prefix] = set(words)
        all_zodiac_words.update(words)

    # Find words unique to each folio
    unique_words = {}
    for folio, words in folio_words.items():
        other_words = set()
        for other_folio, other_word_set in folio_words.items():
            if other_folio != folio:
                other_words.update(other_word_set)
        unique_words[folio] = words - other_words

    return unique_words


def phonetic_similarity(voynich_word: str, target: str) -> float:
    """
    Score how well a Voynich word could phonetically match a target.
    Uses known/suspected sound mappings.
    """
    score = 0.0

    # Length similarity (Taurus has 6 letters)
    len_diff = abs(len(voynich_word) - len(target))
    if len_diff == 0:
        score += 0.3
    elif len_diff == 1:
        score += 0.2
    elif len_diff == 2:
        score += 0.1

    # Check for potential sound correspondences
    # 't' sound: Voynich 'ot', 't', 'ct' could represent 't'
    if target.startswith('t'):
        if voynich_word.startswith('ot') or voynich_word.startswith('t'):
            score += 0.25
        if voynich_word.startswith('ct'):
            score += 0.15

    # 'au' diphthong: could be 'o', 'a', 'ai' in Voynich
    if 'au' in target:
        if 'o' in voynich_word or 'a' in voynich_word or 'ai' in voynich_word:
            score += 0.15

    # 'r' sound: Voynich 'r' or 'ar' or 'or'
    if 'r' in target:
        if 'r' in voynich_word:
            score += 0.15

    # '-us' ending: Voynich '-y' is very common (41%)
    if target.endswith('us') and voynich_word.endswith('y'):
        score += 0.2

    # '-um' ending: also could be '-y' or '-m'
    if target.endswith('um') and (voynich_word.endswith('y') or voynich_word.endswith('m')):
        score += 0.15

    # '-o' ending (Italian): could be 'o' in Voynich
    if target.endswith('o') and voynich_word.endswith('o'):
        score += 0.2

    return score


def analyze_taurus_candidates(corpus) -> List[Tuple[str, float, str]]:
    """Find and rank Taurus candidates on f71r."""

    # Get words unique to f71r
    unique_words = find_folio_unique_words(corpus)
    f71r_unique = unique_words.get('f71r', set())

    # Get all words on f71r
    f71r_all = extract_folio_words(corpus, 'f71r')
    f71r_freq = Counter(f71r_all)

    candidates = []

    for word in f71r_unique:
        best_score = 0
        best_match = ''

        for target, desc in TAURUS_FORMS.items():
            score = phonetic_similarity(word, target)
            if score > best_score:
                best_score = score
                best_match = target

        # Boost score if word appears multiple times on f71r
        freq_boost = min(f71r_freq.get(word, 1) / 10.0, 0.3)
        final_score = best_score + freq_boost

        candidates.append((word, final_score, best_match))

    # Sort by score
    candidates.sort(key=lambda x: -x[1])

    return candidates


def test_character_mapping(voynich_word: str, latin_word: str) -> Dict[str, str]:
    """
    Given a proposed word pair, extract character mappings.
    This is speculative but helps build a mapping table.
    """
    mapping = {}

    # Try simple position-based alignment
    if len(voynich_word) == len(latin_word):
        for v, l in zip(voynich_word, latin_word):
            if v not in mapping:
                mapping[v] = l
    else:
        # Try to align based on known patterns
        # e.g., 'ot' might map to 't'
        pass

    return mapping


def search_for_patterns(corpus) -> None:
    """Search for words that might be zodiac names across all sections."""

    print("\n" + "=" * 80)
    print("SEARCHING FOR ZODIAC CONSTELLATION PATTERNS")
    print("=" * 80)

    # For each zodiac sign, find words on that folio that could match
    zodiac_latin = {
        'f70v': ['pisces', 'aries'],  # Pisces, then Aries
        'f71r': ['taurus'],
        'f71v': ['gemini'],
        'f72r': ['cancer', 'leo', 'virgo'],
        'f72v': ['libra', 'scorpius', 'sagittarius'],
        'f73r': ['capricornus'],
        'f73v': ['aquarius'],
    }

    for folio, signs in zodiac_latin.items():
        print(f"\n{folio} - Looking for: {', '.join(signs)}")
        print("-" * 50)

        folio_words = set(extract_folio_words(corpus, folio))

        for sign in signs:
            print(f"\n  {sign.upper()} (len={len(sign)}):")
            matches = []

            for word in folio_words:
                score = phonetic_similarity(word, sign)
                if score >= 0.3:
                    matches.append((word, score))

            matches.sort(key=lambda x: -x[1])

            if matches:
                for word, score in matches[:5]:
                    print(f"    {word:<15} score={score:.2f}")
            else:
                print("    No strong matches")


def analyze_word_beginnings(corpus) -> None:
    """Analyze if zodiac words share common beginnings."""

    print("\n" + "=" * 80)
    print("WORD BEGINNING ANALYSIS BY ZODIAC FOLIO")
    print("=" * 80)

    for folio in ZODIAC_FOLIOS.keys():
        words = extract_folio_words(corpus, folio)

        # Count 2-char beginnings
        beginnings = Counter()
        for word in words:
            if len(word) >= 2:
                beginnings[word[:2]] += 1

        print(f"\n{folio} ({ZODIAC_FOLIOS[folio]}):")
        print(f"  Total words: {len(words)}, Unique: {len(set(words))}")
        print(f"  Most common beginnings:")
        for begin, count in beginnings.most_common(5):
            pct = 100 * count / len(words)
            print(f"    '{begin}': {count} ({pct:.1f}%)")


def find_label_candidates(corpus) -> None:
    """
    Find short words that appear to be labels rather than running text.
    Labels are typically:
    - Short (2-6 characters)
    - Appear near illustrations
    - May have different statistical properties
    """
    print("\n" + "=" * 80)
    print("LABEL CANDIDATE ANALYSIS")
    print("=" * 80)

    for folio in ZODIAC_FOLIOS.keys():
        words = extract_folio_words(corpus, folio)

        # Filter for short words (potential labels)
        short_words = [w for w in words if 2 <= len(w) <= 6]
        short_freq = Counter(short_words)

        # Find words that appear few times (labels tend to be unique)
        rare_short = [(w, c) for w, c in short_freq.items() if c <= 3]

        print(f"\n{folio} ({ZODIAC_FOLIOS[folio]}):")
        print(f"  Short words (2-6 chars) appearing 1-3 times:")

        for word, count in sorted(rare_short, key=lambda x: -x[1])[:10]:
            print(f"    {word}: {count}")


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Primary analysis: Taurus candidates
    print("=" * 80)
    print("TAURUS IDENTIFICATION ON F71R")
    print("=" * 80)

    print("\nHypothesis: One word on f71r represents 'Taurus' or 'Toro' (bull)")
    print("Strategy: Find words UNIQUE to f71r that phonetically match")

    candidates = analyze_taurus_candidates(corpus)

    print(f"\nTop 20 Taurus candidates (unique to f71r):")
    print(f"{'Voynich Word':<15} {'Score':>8} {'Best Match':>12}")
    print("-" * 40)

    for word, score, match in candidates[:20]:
        print(f"{word:<15} {score:>8.2f} {match:>12}")

    # Additional analyses
    search_for_patterns(corpus)
    analyze_word_beginnings(corpus)
    find_label_candidates(corpus)

    # Final observations
    print("\n" + "=" * 80)
    print("OBSERVATIONS")
    print("=" * 80)
    print("""
KEY FINDINGS:

1. Words unique to f71r (Taurus folio) that score highest for 'taurus':
   - Look for words starting with 'ot' (could be 't' sound)
   - Look for words ending in 'y' (could be '-us' ending)

2. The pattern 'ot-' is very common in zodiac section (22% of words)
   - If 'ot' = 't', then 'otaiin' could be 't' + 'aiin'
   - 'aiin' might be '-aurus' or similar ending

3. CRITICAL TEST: If we identify 'taurus' on f71r:
   - The same word should NOT appear on other zodiac folios
   - The character mappings should work for 'aries', 'gemini', etc.

4. NEXT STEP: Manual inspection of f71r transcription needed
   - Look for word next to/under the bull illustration
   - That word is most likely to be 'Taurus' label
""")


if __name__ == "__main__":
    main()
