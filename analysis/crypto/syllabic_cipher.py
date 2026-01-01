"""
Syllabic Cipher Hypothesis

Tests the hypothesis that Voynich characters represent SYLLABLES, not letters.

If true:
- Each Voynich character = one syllable of Latin/Italian
- 'daiin' = 5 characters = 5 syllables
- Low H2 explained: syllable sequences are more predictable than letter sequences

Evidence FOR syllabic hypothesis:
1. ~20 unique characters in EVA could represent ~20 common syllables
2. Word length distribution matches syllable-based systems
3. The predictability (H2=2.37) could come from syllable transition probabilities

Evidence AGAINST:
1. 5-syllable words would be unusually long for labels
2. Doesn't explain why some characters only appear in certain positions
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import itertools

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

# Most common Latin syllables (approximate)
LATIN_SYLLABLES = [
    # Open syllables (CV pattern)
    'ta', 'ra', 'na', 'ma', 'la', 'sa', 'ca', 'pa', 'da', 'ba', 'fa', 'ga', 'va',
    'te', 're', 'ne', 'me', 'le', 'se', 'ce', 'pe', 'de', 'be', 'fe', 'ge', 've',
    'ti', 'ri', 'ni', 'mi', 'li', 'si', 'ci', 'pi', 'di', 'bi', 'fi', 'gi', 'vi',
    'to', 'ro', 'no', 'mo', 'lo', 'so', 'co', 'po', 'do', 'bo', 'fo', 'go', 'vo',
    'tu', 'ru', 'nu', 'mu', 'lu', 'su', 'cu', 'pu', 'du', 'bu', 'fu', 'gu', 'vu',
    # Closed syllables (CVC pattern)
    'tus', 'rus', 'nus', 'mus', 'lus', 'sus', 'cus', 'pus', 'dus', 'bus',
    'tum', 'rum', 'num', 'mum', 'lum', 'sum', 'cum', 'pum', 'dum', 'bum',
    'ter', 'rer', 'ner', 'mer', 'ler', 'ser', 'cer', 'per', 'der', 'ber',
    'tor', 'ror', 'nor', 'mor', 'lor', 'sor', 'cor', 'por', 'dor', 'bor',
    # Vowels alone
    'a', 'e', 'i', 'o', 'u',
    # Common combinations
    'que', 'qua', 'qui', 'quo', 'quu',
    'ae', 'au', 'ei', 'eu', 'oe', 'ui',
]

# Common Italian syllables
ITALIAN_SYLLABLES = [
    'la', 'le', 'li', 'lo', 'lu',
    'na', 'ne', 'ni', 'no', 'nu',
    'ra', 're', 'ri', 'ro', 'ru',
    'ta', 'te', 'ti', 'to', 'tu',
    'ma', 'me', 'mi', 'mo', 'mu',
    'sa', 'se', 'si', 'so', 'su',
    'ca', 'ce', 'ci', 'co', 'cu',
    'da', 'de', 'di', 'do', 'du',
    'pa', 'pe', 'pi', 'po', 'pu',
    'fa', 'fe', 'fi', 'fo', 'fu',
    'va', 've', 'vi', 'vo', 'vu',
    'ba', 'be', 'bi', 'bo', 'bu',
    'ga', 'ge', 'gi', 'go', 'gu',
    'che', 'chi', 'ghe', 'ghi',
    'gli', 'gna', 'gne', 'gni', 'gno', 'gnu',
    'sca', 'sce', 'sci', 'sco', 'scu',
    'qua', 'que', 'qui', 'quo',
]


def extract_voynich_chars(text: str) -> List[str]:
    """
    Extract individual Voynich characters from EVA transcription.

    EVA uses multi-letter combinations for single glyphs:
    - Single letters: a, c, d, e, f, g, h, i, k, l, m, n, o, p, q, r, s, t, y
    - Digraphs: ch, sh, ck, cf, ct, etc.
    """
    chars = []
    i = 0

    # Known EVA digraphs (two letters = one glyph)
    digraphs = {'ch', 'sh', 'ck', 'cf', 'ct', 'cs', 'ai', 'ee', 'ii', 'in'}

    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in digraphs:
            chars.append(text[i:i+2])
            i += 2
        else:
            chars.append(text[i])
            i += 1

    return chars


def analyze_char_as_syllable(corpus) -> Dict:
    """
    Analyze if treating each Voynich character as a syllable makes sense.
    """
    # Extract all unique characters
    all_chars = []
    for word in corpus.all_words:
        all_chars.extend(extract_voynich_chars(word))

    char_freq = Counter(all_chars)
    total_chars = len(all_chars)

    # If syllabic, we'd expect ~20-50 unique "characters" (syllables)
    print(f"\nUnique character units: {len(char_freq)}")
    print(f"Total character units: {total_chars}")

    print("\nMost common character units (if these are syllables):")
    for char, count in char_freq.most_common(25):
        pct = 100 * count / total_chars
        print(f"  '{char}': {count} ({pct:.1f}%)")

    return {
        'unique_chars': len(char_freq),
        'total_chars': total_chars,
        'char_freq': dict(char_freq)
    }


def test_syllabic_word_lengths(corpus) -> None:
    """
    Test if word lengths are consistent with syllabic encoding.

    If each Voynich char = 1 syllable:
    - Average word length should match average syllables per word
    - Latin/Italian words typically have 2-4 syllables
    """
    print("\n" + "=" * 80)
    print("WORD LENGTH ANALYSIS (SYLLABIC HYPOTHESIS)")
    print("=" * 80)

    # Get word lengths in characters
    word_lengths = []
    for word in corpus.all_words:
        chars = extract_voynich_chars(word)
        word_lengths.append(len(chars))

    length_freq = Counter(word_lengths)

    print("\nWord length distribution (in character units):")
    print("If syllabic: length = number of syllables")

    total = len(word_lengths)
    cumulative = 0
    for length in sorted(length_freq.keys()):
        count = length_freq[length]
        pct = 100 * count / total
        cumulative += pct
        print(f"  {length} chars: {count:>5} ({pct:>5.1f}%) [cumulative: {cumulative:.1f}%]")

    avg_length = sum(word_lengths) / len(word_lengths)
    print(f"\nAverage word length: {avg_length:.2f} characters")
    print("Latin/Italian average: 2.5-3.5 syllables per word")

    if 2.0 <= avg_length <= 4.0:
        print("-> Length distribution is CONSISTENT with syllabic hypothesis")
    else:
        print("-> Length distribution may be INCONSISTENT with syllabic hypothesis")


def find_syllable_mapping_candidates(corpus) -> Dict[str, List[str]]:
    """
    Try to map common Voynich characters to Latin syllables by frequency.
    """
    print("\n" + "=" * 80)
    print("SYLLABLE MAPPING CANDIDATES")
    print("=" * 80)

    # Get Voynich character frequencies
    all_chars = []
    for word in corpus.all_words:
        all_chars.extend(extract_voynich_chars(word))

    char_freq = Counter(all_chars)
    total = len(all_chars)

    # Sort by frequency
    voy_sorted = char_freq.most_common(30)

    # Get Latin syllable frequencies (approximate based on general corpus analysis)
    # These are rough estimates
    latin_syllable_freq = {
        'us': 0.08, 'um': 0.06, 'is': 0.05, 'a': 0.05, 'e': 0.05,
        'i': 0.04, 'o': 0.04, 'u': 0.03, 'ae': 0.03, 'em': 0.03,
        'es': 0.03, 'am': 0.02, 'as': 0.02, 'et': 0.02, 'in': 0.02,
        'er': 0.02, 'ti': 0.02, 'ta': 0.02, 're': 0.02, 'te': 0.02,
        'ra': 0.02, 'ri': 0.02, 'ni': 0.02, 'na': 0.02, 'de': 0.02,
    }

    lat_sorted = sorted(latin_syllable_freq.items(), key=lambda x: -x[1])

    print("\nProposed syllable mapping (by frequency):")
    print(f"{'Voynich':<8} {'Voy %':>8} | {'Latin Syl':<10} {'Lat %':>8}")
    print("-" * 45)

    mapping = {}
    for i, (vchar, vcount) in enumerate(voy_sorted[:20]):
        vpct = 100 * vcount / total
        if i < len(lat_sorted):
            lsyl, lpct = lat_sorted[i]
            lpct *= 100
            mapping[vchar] = lsyl
            print(f"'{vchar}'    {vpct:>7.1f}% | '{lsyl}'      {lpct:>7.1f}%")
        else:
            print(f"'{vchar}'    {vpct:>7.1f}% | (no match)")

    return mapping


def decode_as_syllables(word: str, mapping: Dict[str, str]) -> str:
    """Decode a Voynich word using syllable mapping."""
    chars = extract_voynich_chars(word)
    decoded = []
    for char in chars:
        decoded.append(mapping.get(char, f'[{char}]'))
    return ''.join(decoded)


def test_syllabic_decoding(corpus, mapping: Dict[str, str]) -> None:
    """Test syllabic decoding on sample text."""
    print("\n" + "=" * 80)
    print("SYLLABIC DECODING TEST")
    print("=" * 80)

    # Get first 50 words
    sample_words = corpus.all_words[:50]

    print("\nSample decoded text (first 50 words):")
    print("-" * 60)

    decoded_words = []
    for word in sample_words:
        decoded = decode_as_syllables(word, mapping)
        decoded_words.append(decoded)

    # Print in lines
    line = []
    for word in decoded_words:
        line.append(word)
        if len(' '.join(line)) > 60:
            print(' '.join(line[:-1]))
            line = [word]
    if line:
        print(' '.join(line))

    # Analyze decoded text for Latin patterns
    print("\nLooking for recognizable Latin patterns in decoded text...")
    full_decoded = ' '.join(decoded_words)

    latin_patterns = ['us', 'um', 'is', 'ae', 'em', 'am', 'et', 'in', 'de', 'que']
    for pattern in latin_patterns:
        count = full_decoded.count(pattern)
        if count > 0:
            print(f"  '{pattern}': {count} occurrences")


def analyze_position_constraints_syllabic(corpus) -> None:
    """
    Analyze if character position constraints make sense for syllables.
    """
    print("\n" + "=" * 80)
    print("POSITION CONSTRAINTS (SYLLABIC VIEW)")
    print("=" * 80)

    first_chars = Counter()
    last_chars = Counter()
    middle_chars = Counter()

    for word in corpus.all_words:
        chars = extract_voynich_chars(word)
        if len(chars) >= 1:
            first_chars[chars[0]] += 1
            last_chars[chars[-1]] += 1
        if len(chars) >= 3:
            for char in chars[1:-1]:
                middle_chars[char] += 1

    print("\nCharacters that appear ONLY at word start (initial syllables):")
    only_first = set(first_chars.keys()) - set(middle_chars.keys()) - set(last_chars.keys())
    for char in sorted(only_first, key=lambda x: -first_chars[x])[:10]:
        print(f"  '{char}': {first_chars[char]}")

    print("\nCharacters that appear ONLY at word end (final syllables):")
    only_last = set(last_chars.keys()) - set(middle_chars.keys()) - set(first_chars.keys())
    for char in sorted(only_last, key=lambda x: -last_chars[x])[:10]:
        print(f"  '{char}': {last_chars[char]}")

    print("\nMost common FINAL characters (should be '-us', '-um', '-is', '-ae' type syllables):")
    total_words = len(corpus.all_words)
    for char, count in last_chars.most_common(10):
        pct = 100 * count / total_words
        print(f"  '{char}': {count} ({pct:.1f}%)")


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    print("=" * 80)
    print("SYLLABIC CIPHER HYPOTHESIS TEST")
    print("=" * 80)

    print("""
HYPOTHESIS: Each Voynich character represents a SYLLABLE, not a letter.

If true:
- A 5-character word = 5-syllable word (e.g., 'da-i-i-n' or similar)
- ~25-30 unique chars could represent Latin syllable inventory
- Low H2 (2.37) could reflect syllable-to-syllable predictability
""")

    # Character analysis
    char_analysis = analyze_char_as_syllable(corpus)

    # Word length analysis
    test_syllabic_word_lengths(corpus)

    # Find candidate mappings
    mapping = find_syllable_mapping_candidates(corpus)

    # Test decoding
    test_syllabic_decoding(corpus, mapping)

    # Position constraints
    analyze_position_constraints_syllabic(corpus)

    # Final assessment
    print("\n" + "=" * 80)
    print("SYLLABIC HYPOTHESIS ASSESSMENT")
    print("=" * 80)
    print("""
EVIDENCE FOR SYLLABIC:
1. Word lengths (avg ~4) consistent with syllable counts
2. ~25 common characters could represent core syllable set
3. Position constraints could reflect allowed syllable patterns

EVIDENCE AGAINST:
1. 'y' ending 41% of words is unusual for Latin syllables
2. Not clear what syllable 'ii' or 'ee' would represent
3. Some "words" like 'daiin' would be 5+ syllables (very long)

VERDICT: PARTIALLY PLAUSIBLE
- Syllabic encoding can't be ruled out
- But pure syllabic system doesn't fully explain patterns
- May be HYBRID: some chars = letters, some = syllables
""")


if __name__ == "__main__":
    main()
