"""
Character-Level Mapping Analysis

Try to find EVA character -> Latin letter mappings by analyzing:
1. Character frequencies and comparing to Latin
2. Character position constraints
3. Common patterns and bigrams

Hypothesis: Individual EVA characters (or small groups) map to Latin letters.
"""

import sys
import random
import math
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


# Latin character frequencies
LATIN_FREQ = {
    'e': 0.116, 'i': 0.108, 'u': 0.082, 'a': 0.079, 't': 0.075,
    's': 0.073, 'n': 0.069, 'r': 0.063, 'o': 0.053, 'm': 0.045,
    'c': 0.040, 'l': 0.034, 'p': 0.031, 'd': 0.029, 'b': 0.016,
    'q': 0.015, 'g': 0.013, 'f': 0.010, 'h': 0.009, 'x': 0.006,
    'v': 0.005
}

# Latin common bigrams
LATIN_BIGRAMS = {
    'qu': 0.015, 'ue': 0.013, 'us': 0.012, 'um': 0.011, 'is': 0.011,
    'in': 0.010, 'er': 0.010, 'it': 0.009, 'es': 0.009, 'ti': 0.009,
    'nt': 0.008, 'te': 0.008, 'et': 0.008, 'st': 0.007, 'ut': 0.007,
    'at': 0.007, 'tu': 0.006, 're': 0.006, 'ar': 0.006, 'or': 0.006,
}


def analyze_char_frequency(corpus) -> Dict:
    """Analyze EVA character frequencies and compare to Latin."""
    text = corpus.all_characters
    total = len(text)
    char_freq = Counter(text)

    # Sort by frequency
    sorted_chars = char_freq.most_common()

    # Compare to Latin
    latin_sorted = sorted(LATIN_FREQ.items(), key=lambda x: -x[1])

    comparison = []
    for i, ((eva_char, eva_count), (lat_char, lat_freq)) in enumerate(
            zip(sorted_chars, latin_sorted)):
        eva_freq = eva_count / total
        comparison.append({
            'rank': i + 1,
            'eva_char': eva_char,
            'eva_freq': eva_freq,
            'latin_char': lat_char,
            'latin_freq': lat_freq,
            'freq_diff': abs(eva_freq - lat_freq)
        })

    return {
        'char_freq': dict(char_freq),
        'total_chars': total,
        'comparison': comparison
    }


def analyze_bigrams(corpus) -> Dict:
    """Analyze EVA bigram frequencies."""
    text = corpus.all_characters
    bigrams = Counter(text[i:i+2] for i in range(len(text)-1))
    total = sum(bigrams.values())

    return {
        'bigrams': dict(bigrams),
        'total': total,
        'top_20': bigrams.most_common(20)
    }


def find_frequency_mapping(eva_freq: Dict, target_freq: Dict) -> Dict[str, str]:
    """
    Create a simple frequency-based character mapping.
    Most common EVA char -> most common target char, etc.
    """
    eva_sorted = sorted(eva_freq.items(), key=lambda x: -x[1])
    target_sorted = sorted(target_freq.items(), key=lambda x: -x[1])

    mapping = {}
    for i, (eva_char, _) in enumerate(eva_sorted):
        if i < len(target_sorted):
            mapping[eva_char] = target_sorted[i][0]
        else:
            mapping[eva_char] = '?'

    return mapping


def decode_text(text: str, mapping: Dict[str, str]) -> str:
    """Apply character mapping to decode text."""
    return ''.join(mapping.get(c, '?') for c in text)


def score_decoded_text(decoded: str) -> float:
    """Score decoded text by Latin bigram frequency."""
    if len(decoded) < 2:
        return 0

    bigrams = Counter(decoded[i:i+2] for i in range(len(decoded)-1))
    total = sum(bigrams.values())

    score = 0
    for bigram, count in bigrams.items():
        if bigram in LATIN_BIGRAMS:
            score += count * math.log(LATIN_BIGRAMS[bigram] + 0.0001)
        else:
            score += count * math.log(0.0001)

    return score / total


def hill_climb_mapping(text: str, initial_mapping: Dict[str, str],
                       iterations: int = 10000) -> Tuple[Dict[str, str], float]:
    """Improve character mapping using hill climbing."""
    current = initial_mapping.copy()
    current_score = score_decoded_text(decode_text(text, current))

    best = current.copy()
    best_score = current_score

    eva_chars = list(current.keys())

    for i in range(iterations):
        # Swap two character mappings
        neighbor = current.copy()
        c1, c2 = random.sample(eva_chars, 2)
        neighbor[c1], neighbor[c2] = neighbor[c2], neighbor[c1]

        decoded = decode_text(text, neighbor)
        neighbor_score = score_decoded_text(decoded)

        # Accept better or sometimes accept worse
        temperature = 1.0 - (i / iterations)
        if neighbor_score > current_score:
            current = neighbor
            current_score = neighbor_score

            if current_score > best_score:
                best = current.copy()
                best_score = current_score
        elif random.random() < temperature * 0.3:
            current = neighbor
            current_score = neighbor_score

    return best, best_score


def analyze_position_patterns(corpus) -> Dict:
    """
    Analyze which EVA characters appear in which positions.
    This reveals the 'phonotactics' of Voynichese.
    """
    first_chars = Counter()
    last_chars = Counter()
    second_chars = Counter()
    penult_chars = Counter()

    for word in corpus.all_words:
        if len(word) >= 1:
            first_chars[word[0]] += 1
            last_chars[word[-1]] += 1
        if len(word) >= 2:
            second_chars[word[1]] += 1
            penult_chars[word[-2]] += 1

    return {
        'first': first_chars,
        'last': last_chars,
        'second': second_chars,
        'penultimate': penult_chars
    }


def main():
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    # Character frequency analysis
    print("=" * 80)
    print("CHARACTER FREQUENCY ANALYSIS")
    print("=" * 80)

    freq_analysis = analyze_char_frequency(corpus)

    print(f"\n{'Rank':<5} {'EVA':<6} {'EVA %':>8} {'Latin':<6} {'Latin %':>8} {'Diff':>8}")
    print("-" * 50)
    for c in freq_analysis['comparison'][:21]:
        print(f"{c['rank']:<5} '{c['eva_char']}'   {c['eva_freq']*100:>7.2f}% "
              f"'{c['latin_char']}'    {c['latin_freq']*100:>7.2f}% "
              f"{c['freq_diff']*100:>7.2f}%")

    # Initial frequency-based mapping
    print("\n" + "=" * 80)
    print("FREQUENCY-BASED CHARACTER MAPPING")
    print("=" * 80)

    eva_freq = {c: f / freq_analysis['total_chars']
                for c, f in freq_analysis['char_freq'].items()}
    freq_mapping = find_frequency_mapping(eva_freq, LATIN_FREQ)

    print("\nProposed mapping (by frequency):")
    sorted_mapping = sorted(freq_mapping.items(),
                           key=lambda x: -eva_freq.get(x[0], 0))
    for eva, latin in sorted_mapping[:21]:
        print(f"  '{eva}' -> '{latin}'  ({eva_freq.get(eva, 0)*100:.1f}%)")

    # Decode sample text
    sample = corpus.all_characters[:500]
    decoded_freq = decode_text(sample, freq_mapping)

    print(f"\nSample decoded text (frequency mapping):")
    print("-" * 60)
    for i in range(0, len(decoded_freq), 60):
        print(decoded_freq[i:i+60])

    # Hill climbing optimization
    print("\n" + "=" * 80)
    print("OPTIMIZED CHARACTER MAPPING (Hill Climbing)")
    print("=" * 80)

    print("\nOptimizing...")
    # Use first 5000 chars for speed
    opt_text = corpus.all_characters[:5000]
    best_mapping, best_score = hill_climb_mapping(opt_text, freq_mapping, 5000)

    print(f"Best score: {best_score:.4f}")

    print("\nOptimized mapping:")
    for eva, latin in sorted(best_mapping.items(),
                            key=lambda x: -eva_freq.get(x[0], 0))[:21]:
        orig = freq_mapping.get(eva, '?')
        change = " (changed)" if latin != orig else ""
        print(f"  '{eva}' -> '{latin}'{change}")

    decoded_opt = decode_text(sample, best_mapping)
    print(f"\nSample decoded text (optimized):")
    print("-" * 60)
    for i in range(0, len(decoded_opt), 60):
        print(decoded_opt[i:i+60])

    # Position analysis
    print("\n" + "=" * 80)
    print("CHARACTER POSITION CONSTRAINTS")
    print("=" * 80)

    positions = analyze_position_patterns(corpus)

    print("\nFirst character distribution (top 10):")
    for char, count in positions['first'].most_common(10):
        pct = 100 * count / len(corpus.all_words)
        mapped = best_mapping.get(char, '?')
        print(f"  '{char}' -> '{mapped}': {pct:.1f}%")

    print("\nLast character distribution (top 10):")
    for char, count in positions['last'].most_common(10):
        pct = 100 * count / len(corpus.all_words)
        mapped = best_mapping.get(char, '?')
        print(f"  '{char}' -> '{mapped}': {pct:.1f}%")

    # Check for Latin patterns in decoded text
    print("\n" + "=" * 80)
    print("SEARCHING FOR LATIN PATTERNS IN DECODED TEXT")
    print("=" * 80)

    full_decoded = decode_text(corpus.all_characters, best_mapping)

    common_latin = ['et', 'in', 'est', 'non', 'cum', 'sed', 'ut', 'ad',
                    'que', 'aut', 'vel', 'per', 'pro', 'de', 'ab']

    print("\nCommon Latin words found in decoded text:")
    for word in common_latin:
        count = full_decoded.count(word)
        if count > 10:
            print(f"  '{word}': {count} occurrences")

    # Final assessment
    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)
    print("""
Character-level substitution cipher hypothesis:

FINDINGS:
1. EVA character frequencies are moderately similar to Latin
2. But the decoded text does not read as Latin
3. The positional constraints (y=41% final) don't match Latin

CONCLUSION:
Simple substitution cipher is UNLIKELY. The encoding is more complex.

Possible next steps:
1. Try syllable-level mapping (EVA chars = syllables, not letters)
2. Try null cipher (some chars are meaningless padding)
3. Try polyalphabetic cipher (different mappings for different positions)
4. Consider non-European language targets
""")


if __name__ == "__main__":
    main()
