"""
Verbose Cipher Attack on Voynich Manuscript

Tests the hypothesis that Voynich words encode single letters of a
plaintext language (Latin, Italian, etc.) via a lookup table.

A verbose cipher maps each plaintext letter to one of several possible
ciphertext words. For example:
    'e' -> 'daiin', 'aiin', 'or'
    'a' -> 'chedy', 'shedy', 'ol'
    etc.

The attack:
1. Find candidate word->letter mappings based on frequency
2. Score each mapping by how well decoded text matches target language
3. Search for optimal mapping using hill climbing
"""

import sys
import random
import math
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


# Reference letter frequencies for candidate languages
# Source: Standard frequency tables
LATIN_FREQ = {
    'e': 0.116, 'i': 0.108, 'u': 0.082, 'a': 0.079, 't': 0.075,
    's': 0.073, 'n': 0.069, 'r': 0.063, 'o': 0.053, 'm': 0.045,
    'c': 0.040, 'l': 0.034, 'p': 0.031, 'd': 0.029, 'b': 0.016,
    'q': 0.015, 'g': 0.013, 'f': 0.010, 'h': 0.009, 'x': 0.006,
    'v': 0.005, 'y': 0.001, 'z': 0.001, 'k': 0.001
}

ITALIAN_FREQ = {
    'e': 0.118, 'a': 0.117, 'i': 0.112, 'o': 0.098, 'n': 0.069,
    't': 0.062, 'r': 0.064, 'l': 0.065, 's': 0.050, 'c': 0.045,
    'd': 0.037, 'u': 0.030, 'p': 0.031, 'm': 0.025, 'g': 0.016,
    'v': 0.021, 'h': 0.015, 'f': 0.011, 'b': 0.009, 'z': 0.007,
    'q': 0.005, 'k': 0.001, 'j': 0.001, 'w': 0.001, 'x': 0.001, 'y': 0.001
}

# Latin bigram frequencies (top ones)
LATIN_BIGRAMS = {
    'qu': 0.015, 'ue': 0.013, 'us': 0.012, 'um': 0.011, 'is': 0.011,
    'in': 0.010, 'er': 0.010, 'it': 0.009, 'es': 0.009, 'ti': 0.009,
    'nt': 0.008, 'te': 0.008, 'et': 0.008, 'st': 0.007, 'ut': 0.007,
    'at': 0.007, 'tu': 0.006, 're': 0.006, 'ar': 0.006, 'or': 0.006,
    'ra': 0.006, 'ta': 0.006, 'am': 0.005, 'em': 0.005, 'ae': 0.005
}


class VerboseCipherAttack:
    """Attack verbose cipher by frequency matching."""

    def __init__(self, voynich_words: List[str], target_lang: str = 'latin'):
        self.voynich_words = voynich_words
        self.target_lang = target_lang
        self.target_freq = LATIN_FREQ if target_lang == 'latin' else ITALIAN_FREQ

        # Voynich word frequencies
        self.word_freq = Counter(voynich_words)
        self.total_words = len(voynich_words)
        self.unique_words = list(self.word_freq.keys())

        # Normalize word frequencies
        self.word_prob = {w: c / self.total_words for w, c in self.word_freq.items()}

        # Sort words by frequency
        self.sorted_words = [w for w, c in self.word_freq.most_common()]

        # Get target letters sorted by frequency
        self.target_letters = sorted(self.target_freq.keys(),
                                    key=lambda x: -self.target_freq[x])

    def initial_mapping(self) -> Dict[str, str]:
        """
        Create initial word->letter mapping based on frequency matching.
        Most frequent Voynich word -> most frequent letter, etc.
        """
        mapping = {}

        # Map by frequency ranking
        for i, word in enumerate(self.sorted_words):
            if i < len(self.target_letters):
                letter = self.target_letters[i]
                mapping[word] = letter
            else:
                # Assign remaining words to common letters
                mapping[word] = 'e'  # default to most common

        return mapping

    def decode(self, mapping: Dict[str, str]) -> str:
        """Decode Voynich text using the given word->letter mapping."""
        decoded = []
        for word in self.voynich_words:
            letter = mapping.get(word, '?')
            decoded.append(letter)
        return ''.join(decoded)

    def score_mapping(self, mapping: Dict[str, str]) -> float:
        """
        Score a mapping by how well the decoded text matches target language.
        Uses bigram frequency matching.
        """
        decoded = self.decode(mapping)

        if len(decoded) < 2:
            return float('-inf')

        # Calculate bigram frequencies in decoded text
        bigrams = Counter(decoded[i:i+2] for i in range(len(decoded)-1))
        total_bigrams = sum(bigrams.values())

        # Score by correlation with target language bigrams
        score = 0
        for bigram, count in bigrams.items():
            observed_freq = count / total_bigrams
            expected_freq = LATIN_BIGRAMS.get(bigram, 0.0001)
            # Log likelihood
            if expected_freq > 0:
                score += count * math.log(expected_freq + 0.0001)

        return score

    def score_by_letter_freq(self, mapping: Dict[str, str]) -> float:
        """Score by how well letter frequencies match."""
        # Calculate implied letter frequencies from mapping
        letter_freq = defaultdict(float)
        for word, letter in mapping.items():
            letter_freq[letter] += self.word_prob.get(word, 0)

        # Compare to target frequencies (chi-squared-like score)
        score = 0
        for letter, expected in self.target_freq.items():
            observed = letter_freq.get(letter, 0)
            diff = expected - observed
            score -= diff * diff * 100

        return score

    def hill_climb(self, iterations: int = 10000) -> Tuple[Dict[str, str], float]:
        """
        Improve mapping using hill climbing with random swaps.
        """
        current = self.initial_mapping()
        current_score = self.score_mapping(current)

        best = current.copy()
        best_score = current_score

        top_words = self.sorted_words[:100]  # Focus on most frequent words

        for i in range(iterations):
            # Create neighbor by swapping two word mappings
            neighbor = current.copy()
            w1, w2 = random.sample(top_words, 2)
            neighbor[w1], neighbor[w2] = neighbor[w2], neighbor[w1]

            neighbor_score = self.score_mapping(neighbor)

            # Accept if better, or sometimes accept worse (simulated annealing)
            temperature = 1.0 - (i / iterations)
            if neighbor_score > current_score:
                current = neighbor
                current_score = neighbor_score

                if current_score > best_score:
                    best = current.copy()
                    best_score = current_score
            elif random.random() < temperature * 0.1:
                current = neighbor
                current_score = neighbor_score

            if i % 1000 == 0:
                print(f"  Iteration {i}: best_score = {best_score:.2f}")

        return best, best_score

    def analyze_mapping(self, mapping: Dict[str, str]) -> Dict:
        """Analyze a mapping to see if it makes sense."""
        decoded = self.decode(mapping)

        # Letter frequency in decoded text
        letter_freq = Counter(decoded)
        total = len(decoded)

        # Common patterns
        common_trigrams = Counter(decoded[i:i+3] for i in range(len(decoded)-2))

        # Check for common Latin words/patterns
        latin_markers = ['que', 'et', 'in', 'est', 'ad', 'ut', 'non', 'cum']
        found_markers = []
        for marker in latin_markers:
            if marker in decoded:
                count = decoded.count(marker)
                found_markers.append((marker, count))

        return {
            'decoded_sample': decoded[:500],
            'letter_freq': {k: v/total for k, v in letter_freq.most_common(10)},
            'top_trigrams': common_trigrams.most_common(10),
            'latin_markers': found_markers
        }


def find_word_pairs(corpus) -> List[Tuple[str, str, int]]:
    """
    Find common adjacent word pairs in Voynich text.
    If these map to common letter pairs, it's evidence for verbose cipher.
    """
    pair_counts = Counter()
    words = corpus.all_words

    for i in range(len(words) - 1):
        pair = (words[i], words[i+1])
        pair_counts[pair] += 1

    return pair_counts.most_common(30)


def test_simple_hypothesis():
    """
    Test simple verbose cipher hypothesis:
    Each unique Voynich word = one letter
    """
    print("=" * 80)
    print("VERBOSE CIPHER ANALYSIS")
    print("=" * 80)

    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    words = corpus.all_words

    print(f"\nCorpus statistics:")
    print(f"  Total words: {len(words):,}")
    print(f"  Unique words: {len(set(words)):,}")
    print(f"  If 1 word = 1 letter, plaintext would have {len(words):,} letters")

    # The key insight: 8000+ unique words is WAY too many for a simple cipher
    # But maybe word FAMILIES map to letters?

    print(f"\n" + "-" * 40)
    print("Testing: Most frequent Voynich word = 'e' (most common letter)")
    print("-" * 40)

    word_freq = Counter(words)
    top_20 = word_freq.most_common(20)

    print("\nTop 20 Voynich words vs expected letter frequencies:")
    print(f"{'Voynich Word':<15} {'Count':>8} {'%':>8} | {'Latin letter':>12} {'Expected %':>10}")
    print("-" * 60)

    latin_letters = list(LATIN_FREQ.keys())
    for i, (word, count) in enumerate(top_20):
        pct = 100 * count / len(words)
        letter = latin_letters[i] if i < len(latin_letters) else '?'
        expected = 100 * LATIN_FREQ.get(letter, 0)
        match = "~" if abs(pct - expected) < 2 else " "
        print(f"{word:<15} {count:>8,} {pct:>7.2f}% |{match}{letter:>12} {expected:>9.1f}%")

    # Key observation
    print("\n" + "=" * 80)
    print("OBSERVATION: Frequency distribution differs significantly from Latin")
    print("=" * 80)
    print("""
The most common Voynich word 'daiin' appears 2.3% of the time.
In Latin, 'e' should appear ~11.6% of the time.

Possible explanations:
1. Multiple Voynich words encode 'e' (verbose cipher with synonyms)
2. The plaintext is not Latin
3. The encoding is not a simple verbose cipher
""")

    # Test word pairs for common bigrams
    print("\n" + "=" * 80)
    print("WORD PAIR ANALYSIS (testing for bigram patterns)")
    print("=" * 80)

    pairs = find_word_pairs(corpus)
    print("\nMost common adjacent word pairs:")
    print("(If verbose cipher: these should map to common Latin bigrams like 'qu', 'et', 'in')")
    print(f"\n{'Word 1':<12} + {'Word 2':<12} = {'Count':>6}")
    print("-" * 35)
    for (w1, w2), count in pairs[:15]:
        print(f"{w1:<12} + {w2:<12} = {count:>6}")

    # Run optimization
    print("\n" + "=" * 80)
    print("ATTEMPTING OPTIMIZED MAPPING (hill climbing)")
    print("=" * 80)

    attack = VerboseCipherAttack(words, 'latin')
    print("\nSearching for best word->letter mapping...")
    best_mapping, best_score = attack.hill_climb(iterations=5000)

    print(f"\nBest score achieved: {best_score:.2f}")

    # Analyze best mapping
    analysis = attack.analyze_mapping(best_mapping)

    print(f"\nDecoded text sample (first 200 chars):")
    print("-" * 60)
    decoded = analysis['decoded_sample'][:200]
    # Format in groups of 50
    for i in range(0, len(decoded), 50):
        print(decoded[i:i+50])

    print(f"\nLetter frequencies in decoded text:")
    for letter, freq in analysis['letter_freq'].items():
        expected = LATIN_FREQ.get(letter, 0)
        print(f"  '{letter}': {freq*100:.1f}% (Latin expects: {expected*100:.1f}%)")

    if analysis['latin_markers']:
        print(f"\nPotential Latin words found:")
        for marker, count in analysis['latin_markers']:
            print(f"  '{marker}': {count} occurrences")

    # Show top mappings
    print(f"\nTop 20 word->letter mappings found:")
    for word, count in word_freq.most_common(20):
        letter = best_mapping.get(word, '?')
        print(f"  {word:<15} -> '{letter}'")


if __name__ == "__main__":
    test_simple_hypothesis()
