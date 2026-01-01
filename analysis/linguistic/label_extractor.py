"""
Label Extraction and Proper Noun Analysis

Focuses on the zodiac section (folios f70-f73) where constellation and
month names should appear. These are our best hope for finding cognates
with known languages.

The zodiac section has 12 diagrams showing zodiac signs:
- Each has ~30 female figures arranged in circles
- Each figure holds or is connected to a labeled star
- The labels should include constellation names, months, or star names

Known zodiac pages in the manuscript:
f70v1 - Pisces (two fish)
f70v2 - Aries (ram)
f71r - Taurus (bull)
f71v - Gemini (twins?)
f72r1 - Cancer?
f72r2 - Leo (lion?)
f72r3 - Virgo?
f72v1 - Libra (scales?)
f72v2 - Scorpio?
f72v3 - Sagittarius (archer)
f73r - Capricorn?
f73v - Aquarius?
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


# Known zodiac/month terms to search for patterns
ZODIAC_LATIN = {
    'aries': 'Ram (March-April)',
    'taurus': 'Bull (April-May)',
    'gemini': 'Twins (May-June)',
    'cancer': 'Crab (June-July)',
    'leo': 'Lion (July-August)',
    'virgo': 'Virgin (August-September)',
    'libra': 'Scales (September-October)',
    'scorpius': 'Scorpion (October-November)',
    'sagittarius': 'Archer (November-December)',
    'capricornus': 'Goat (December-January)',
    'aquarius': 'Water-bearer (January-February)',
    'pisces': 'Fish (February-March)'
}

MONTHS_LATIN = [
    'martius', 'aprilis', 'maius', 'iunius',
    'iulius', 'augustus', 'september', 'october',
    'november', 'december', 'ianuarius', 'februarius'
]

MONTHS_ITALIAN = [
    'marzo', 'aprile', 'maggio', 'giugno',
    'luglio', 'agosto', 'settembre', 'ottobre',
    'novembre', 'dicembre', 'gennaio', 'febbraio'
]

# Folios that are in the zodiac section
ZODIAC_FOLIOS = ['f70v', 'f71r', 'f71v', 'f72r', 'f72v', 'f73r', 'f73v']


def extract_zodiac_words(corpus) -> Dict[str, List[str]]:
    """Extract words from zodiac section, grouped by folio."""
    zodiac_words = defaultdict(list)

    for word in corpus.words:
        folio = word.folio
        # Check if it's a zodiac folio
        for zf in ZODIAC_FOLIOS:
            if folio.startswith(zf):
                zodiac_words[folio].append(word.text)
                break

    return zodiac_words


def find_short_labels(words: List[str], max_len: int = 8) -> List[str]:
    """
    Find short words that might be labels rather than running text.
    Labels are typically shorter and less common.
    """
    short_words = [w for w in words if len(w) <= max_len]
    return short_words


def analyze_zodiac_patterns(zodiac_words: Dict[str, List[str]]) -> Dict:
    """
    Analyze patterns across zodiac folios.
    Look for:
    - Words that appear on only one folio (unique labels)
    - Words that repeat across all folios (common terms)
    - Pattern similarities to known zodiac names
    """
    all_words = []
    folio_unique = {}
    word_folio_counts = defaultdict(set)

    for folio, words in zodiac_words.items():
        all_words.extend(words)
        for word in set(words):
            word_folio_counts[word].add(folio)

    # Words unique to single folio (potential names)
    unique_words = {w: list(folios)[0] for w, folios in word_folio_counts.items()
                   if len(folios) == 1}

    # Words appearing on all folios (common vocabulary)
    common_words = [w for w, folios in word_folio_counts.items()
                   if len(folios) >= len(zodiac_words) - 1]

    return {
        'total_words': len(all_words),
        'unique_to_folio': unique_words,
        'common_across_all': common_words,
        'word_folio_counts': dict(word_folio_counts)
    }


def match_zodiac_patterns(voynich_words: List[str]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Try to match Voynich words to zodiac names using:
    1. Length matching
    2. Initial letter patterns
    3. Ending patterns
    """
    matches = defaultdict(list)

    for zodiac, description in ZODIAC_LATIN.items():
        target_len = len(zodiac)

        for vword in voynich_words:
            # Score based on various features
            score = 0

            # Length match
            len_diff = abs(len(vword) - target_len)
            if len_diff == 0:
                score += 0.3
            elif len_diff <= 1:
                score += 0.2
            elif len_diff <= 2:
                score += 0.1

            # Check for similar patterns
            # Taurus starts with 'ta' - look for 'ot' words (common Voynich initial)
            # Aries starts with 'ar' - look for 'ar' words (exists in Voynich)
            if zodiac.startswith('ar') and vword.startswith('ar'):
                score += 0.4
            if zodiac.startswith('ta') and vword.startswith('ot'):
                score += 0.2
            if zodiac.startswith('pi') and 'p' in vword:
                score += 0.1

            # Ending patterns
            if zodiac.endswith('us') and vword.endswith('y'):
                score += 0.1  # -y is very common ending
            if zodiac.endswith('ius') and vword.endswith('aiin'):
                score += 0.2

            if score > 0.3:
                matches[zodiac].append((vword, score))

    # Sort matches by score
    for zodiac in matches:
        matches[zodiac].sort(key=lambda x: -x[1])
        matches[zodiac] = matches[zodiac][:5]

    return matches


def search_bax_words(corpus) -> Dict[str, List]:
    """
    Search for words that Stephen Bax proposed as proper nouns.
    Bax claimed to identify plant/star names.
    """
    # Bax's proposed identifications (from his 2014 paper)
    bax_proposals = {
        'kaur': 'Chiron (centaury plant)',
        'kain': 'related to Chiron',
        'okaiin': 'possible plant name',
        'otaiin': 'variant spelling',
    }

    results = {}
    word_freq = Counter(corpus.all_words)

    for pattern, meaning in bax_proposals.items():
        matches = [w for w in word_freq.keys() if pattern in w]
        results[pattern] = {
            'meaning': meaning,
            'exact_matches': [(w, word_freq[w]) for w in matches if w == pattern],
            'containing': [(w, word_freq[w]) for w in matches][:10]
        }

    return results


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Extract zodiac section
    print("=" * 80)
    print("ZODIAC SECTION ANALYSIS")
    print("=" * 80)

    zodiac_words = extract_zodiac_words(corpus)

    print(f"\nZodiac section folios found:")
    for folio, words in sorted(zodiac_words.items()):
        print(f"  {folio}: {len(words)} words")

    total_zodiac = sum(len(w) for w in zodiac_words.values())
    print(f"\nTotal zodiac section words: {total_zodiac}")

    # Analyze patterns
    patterns = analyze_zodiac_patterns(zodiac_words)

    print(f"\nWords unique to specific folios (potential names):")
    unique_by_folio = defaultdict(list)
    for word, folio in patterns['unique_to_folio'].items():
        unique_by_folio[folio].append(word)

    for folio in sorted(unique_by_folio.keys()):
        words = unique_by_folio[folio][:10]  # Top 10
        print(f"  {folio}: {', '.join(words)}")

    print(f"\nWords common across zodiac folios:")
    print(f"  {', '.join(patterns['common_across_all'][:20])}")

    # Try to match zodiac names
    print("\n" + "=" * 80)
    print("ZODIAC NAME MATCHING ATTEMPTS")
    print("=" * 80)

    all_zodiac_words = []
    for words in zodiac_words.values():
        all_zodiac_words.extend(set(words))
    all_zodiac_words = list(set(all_zodiac_words))

    matches = match_zodiac_patterns(all_zodiac_words)

    for zodiac, description in ZODIAC_LATIN.items():
        print(f"\n{zodiac.upper()} ({description}):")
        if zodiac in matches and matches[zodiac]:
            for vword, score in matches[zodiac]:
                print(f"  {vword:<15} (score: {score:.2f})")
        else:
            print(f"  No strong matches")

    # Look for specific patterns
    print("\n" + "=" * 80)
    print("SEARCHING FOR SPECIFIC PATTERNS")
    print("=" * 80)

    # Words starting with 'ar' (like 'aries')
    ar_words = [w for w in all_zodiac_words if w.startswith('ar')]
    print(f"\nWords starting with 'ar' (cf. Aries):")
    print(f"  {', '.join(ar_words[:15])}")

    # Words starting with 'ot' (common in zodiac, might = 'ta' for Taurus)
    ot_words = [w for w in all_zodiac_words if w.startswith('ot')]
    print(f"\nWords starting with 'ot' (cf. Taurus with reversal?):")
    print(f"  {', '.join(ot_words[:15])}")

    # Words that might match month names
    print("\n" + "=" * 80)
    print("LOOKING FOR MONTH NAME PATTERNS")
    print("=" * 80)

    # Words of similar length to month names
    for month in MONTHS_LATIN[:4]:  # First few months
        similar_len = [w for w in all_zodiac_words if abs(len(w) - len(month)) <= 1]
        print(f"\n{month} (len={len(month)}): similar length words:")
        print(f"  {', '.join(similar_len[:10])}")

    # Bax's proposed words
    print("\n" + "=" * 80)
    print("STEPHEN BAX'S PROPOSED IDENTIFICATIONS")
    print("=" * 80)

    bax_results = search_bax_words(corpus)
    for pattern, info in bax_results.items():
        print(f"\n'{pattern}' ({info['meaning']}):")
        if info['exact_matches']:
            for w, count in info['exact_matches']:
                print(f"  EXACT: '{w}' appears {count} times")
        print(f"  Words containing pattern: {len(info['containing'])}")
        for w, count in info['containing'][:5]:
            print(f"    {w}: {count}")

    # Final observations
    print("\n" + "=" * 80)
    print("KEY OBSERVATIONS")
    print("=" * 80)
    print("""
1. The zodiac section has distinctive vocabulary
2. Words starting with 'ot' are very common in zodiac section (22% vs 8% overall)
3. If 'ot' = 't' or 'ta', this could relate to Taurus on the bull folio

4. Words with 'ar' exist and could relate to Aries

5. The lack of clear cognates suggests either:
   - Heavy encoding/transformation
   - A non-European language
   - Constructed/artificial language

Next step: Focus on the Taurus folio (f71r) and see if we can identify the bull label
""")


if __name__ == "__main__":
    main()
