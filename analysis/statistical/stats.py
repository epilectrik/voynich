"""
Statistical Analysis Tools for the Voynich Manuscript

Implements frequency analysis, entropy calculations, and statistical
tests to characterize the manuscript's text properties.
"""

import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import VoynichCorpus, load_corpus


def log2(n: float) -> float:
    """Safe log base 2."""
    return math.log(n, 2) if n > 0 else 0


class FrequencyAnalyzer:
    """Analyze character and word frequencies."""

    def __init__(self, corpus: VoynichCorpus):
        self.corpus = corpus
        self._char_freq = None
        self._word_freq = None
        self._bigram_freq = None
        self._trigram_freq = None

    @property
    def char_freq(self) -> Counter:
        """Character frequency distribution."""
        if self._char_freq is None:
            self._char_freq = Counter(self.corpus.all_characters)
        return self._char_freq

    @property
    def word_freq(self) -> Counter:
        """Word frequency distribution."""
        if self._word_freq is None:
            self._word_freq = Counter(self.corpus.all_words)
        return self._word_freq

    @property
    def bigram_freq(self) -> Counter:
        """Character bigram frequency."""
        if self._bigram_freq is None:
            text = self.corpus.all_characters
            self._bigram_freq = Counter(text[i:i+2] for i in range(len(text)-1))
        return self._bigram_freq

    @property
    def trigram_freq(self) -> Counter:
        """Character trigram frequency."""
        if self._trigram_freq is None:
            text = self.corpus.all_characters
            self._trigram_freq = Counter(text[i:i+3] for i in range(len(text)-2))
        return self._trigram_freq

    def word_length_distribution(self) -> Dict[int, int]:
        """Distribution of word lengths."""
        return Counter(len(w) for w in self.corpus.all_words)

    def char_position_freq(self) -> Dict[str, Dict[str, int]]:
        """
        Character frequency by position in word.
        Returns dict mapping position ('first', 'middle', 'last') to char counts.
        """
        positions = {
            'first': Counter(),
            'middle': Counter(),
            'last': Counter(),
            'only': Counter()  # single-char words
        }

        for word in self.corpus.all_words:
            if len(word) == 1:
                positions['only'][word] += 1
            else:
                positions['first'][word[0]] += 1
                positions['last'][word[-1]] += 1
                for c in word[1:-1]:
                    positions['middle'][c] += 1

        return positions


class EntropyAnalyzer:
    """Calculate various entropy measures."""

    def __init__(self, corpus: VoynichCorpus):
        self.corpus = corpus
        self.freq = FrequencyAnalyzer(corpus)

    def shannon_entropy(self, counter: Counter) -> float:
        """Calculate Shannon entropy of a frequency distribution."""
        total = sum(counter.values())
        if total == 0:
            return 0
        probs = [count / total for count in counter.values()]
        return -sum(p * log2(p) for p in probs if p > 0)

    def char_entropy(self) -> float:
        """First-order character entropy (H1)."""
        return self.shannon_entropy(self.freq.char_freq)

    def word_entropy(self) -> float:
        """Word-level entropy."""
        return self.shannon_entropy(self.freq.word_freq)

    def conditional_char_entropy(self, order: int = 1) -> float:
        """
        Conditional character entropy H(X|context).
        For order=1 (bigrams), this is H2 - the second-order entropy.
        """
        text = self.corpus.all_characters
        if len(text) < order + 1:
            return 0

        # Count contexts and their following characters
        context_counts = defaultdict(Counter)
        for i in range(len(text) - order):
            context = text[i:i+order]
            next_char = text[i+order]
            context_counts[context][next_char] += 1

        # Calculate conditional entropy
        total = sum(sum(counts.values()) for counts in context_counts.values())
        entropy = 0

        for context, next_chars in context_counts.items():
            context_total = sum(next_chars.values())
            context_prob = context_total / total
            context_entropy = self.shannon_entropy(next_chars)
            entropy += context_prob * context_entropy

        return entropy

    def h2(self) -> float:
        """Second-order conditional entropy (the key Voynich metric)."""
        return self.conditional_char_entropy(order=1)


class ZipfAnalyzer:
    """Analyze Zipf's law compliance."""

    def __init__(self, corpus: VoynichCorpus):
        self.corpus = corpus
        self.freq = FrequencyAnalyzer(corpus)

    def word_rank_freq(self) -> List[Tuple[str, int, int]]:
        """Return words with their rank and frequency."""
        sorted_words = self.freq.word_freq.most_common()
        return [(word, rank+1, freq) for rank, (word, freq) in enumerate(sorted_words)]

    def zipf_coefficient(self) -> float:
        """
        Calculate Zipf coefficient (slope of log-log plot).
        Should be close to -1 for natural language.
        """
        ranked = self.word_rank_freq()
        if len(ranked) < 2:
            return 0

        # Linear regression on log-log scale
        n = min(len(ranked), 1000)  # Use top 1000 words
        log_ranks = [math.log(rank) for _, rank, _ in ranked[:n]]
        log_freqs = [math.log(freq) for _, _, freq in ranked[:n]]

        # Simple least squares
        mean_x = sum(log_ranks) / n
        mean_y = sum(log_freqs) / n

        numerator = sum((log_ranks[i] - mean_x) * (log_freqs[i] - mean_y) for i in range(n))
        denominator = sum((log_ranks[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            return 0

        return numerator / denominator


class WordStructureAnalyzer:
    """Analyze Voynich word structure patterns."""

    def __init__(self, corpus: VoynichCorpus):
        self.corpus = corpus

    def prefix_freq(self, max_len: int = 3) -> Dict[int, Counter]:
        """Frequency of word prefixes by length."""
        prefixes = {i: Counter() for i in range(1, max_len + 1)}
        for word in self.corpus.all_words:
            for i in range(1, min(len(word), max_len) + 1):
                prefixes[i][word[:i]] += 1
        return prefixes

    def suffix_freq(self, max_len: int = 3) -> Dict[int, Counter]:
        """Frequency of word suffixes by length."""
        suffixes = {i: Counter() for i in range(1, max_len + 1)}
        for word in self.corpus.all_words:
            for i in range(1, min(len(word), max_len) + 1):
                suffixes[i][word[-i:]] += 1
        return suffixes

    def first_char_distribution(self) -> Counter:
        """Distribution of first characters in words."""
        return Counter(w[0] for w in self.corpus.all_words if w)

    def last_char_distribution(self) -> Counter:
        """Distribution of last characters in words."""
        return Counter(w[-1] for w in self.corpus.all_words if w)

    def char_never_follows(self) -> Dict[str, set]:
        """
        For each character, find characters that never follow it.
        This reveals positional constraints in Voynichese.
        """
        text = self.corpus.all_characters
        all_chars = set(text)
        follows = defaultdict(set)

        for i in range(len(text) - 1):
            follows[text[i]].add(text[i+1])

        never_follows = {}
        for char in all_chars:
            never_follows[char] = all_chars - follows[char]

        return never_follows

    def word_patterns(self) -> Counter:
        """
        Analyze word structure patterns using character classes.
        Maps each word to a pattern like CVC (consonant-vowel-consonant).
        Uses simple heuristics for Voynichese.
        """
        # Common EVA "vowel-like" characters (appear in all positions)
        vowel_like = set('aeioy')
        # Common EVA "consonant-like" characters
        consonant_like = set('bcdfghklmnpqrstvxz')

        patterns = Counter()
        for word in self.corpus.all_words:
            pattern = ""
            for c in word:
                if c in vowel_like:
                    pattern += "V"
                elif c in consonant_like:
                    pattern += "C"
                else:
                    pattern += "X"  # unknown
            patterns[pattern] += 1

        return patterns


def analyze_corpus(corpus: VoynichCorpus) -> Dict:
    """Run comprehensive analysis on a corpus."""
    freq = FrequencyAnalyzer(corpus)
    entropy = EntropyAnalyzer(corpus)
    zipf = ZipfAnalyzer(corpus)
    structure = WordStructureAnalyzer(corpus)

    results = {
        'basic_stats': corpus.summary(),
        'char_entropy_h1': entropy.char_entropy(),
        'char_entropy_h2': entropy.h2(),
        'word_entropy': entropy.word_entropy(),
        'zipf_coefficient': zipf.zipf_coefficient(),
        'top_10_words': freq.word_freq.most_common(10),
        'top_10_chars': freq.char_freq.most_common(10),
        'word_length_dist': dict(freq.word_length_distribution().most_common(15)),
        'top_10_first_chars': structure.first_char_distribution().most_common(10),
        'top_10_last_chars': structure.last_char_distribution().most_common(10),
    }

    return results


def print_analysis(results: Dict) -> None:
    """Pretty print analysis results."""
    print("=" * 60)
    print("VOYNICH MANUSCRIPT STATISTICAL ANALYSIS")
    print("=" * 60)

    print("\n--- Basic Statistics ---")
    for key, value in results['basic_stats'].items():
        print(f"  {key}: {value}")

    print("\n--- Entropy Measures ---")
    print(f"  H1 (character entropy): {results['char_entropy_h1']:.4f} bits")
    print(f"  H2 (conditional entropy): {results['char_entropy_h2']:.4f} bits")
    print(f"  Word entropy: {results['word_entropy']:.4f} bits")
    print(f"  Note: Natural languages typically have H2 between 3-4")
    print(f"        Voynichese is known for H2 around 2 (highly predictable)")

    print("\n--- Zipf's Law ---")
    print(f"  Zipf coefficient: {results['zipf_coefficient']:.4f}")
    print(f"  Note: Natural language ~ -1.0")

    print("\n--- Top 10 Most Frequent Words ---")
    for word, count in results['top_10_words']:
        print(f"  {word}: {count}")

    print("\n--- Top 10 Most Frequent Characters ---")
    for char, count in results['top_10_chars']:
        print(f"  '{char}': {count}")

    print("\n--- Word Length Distribution ---")
    for length, count in sorted(results['word_length_dist'].items()):
        print(f"  Length {length}: {count}")

    print("\n--- First Character Distribution (Top 10) ---")
    for char, count in results['top_10_first_chars']:
        print(f"  '{char}': {count}")

    print("\n--- Last Character Distribution (Top 10) ---")
    for char, count in results['top_10_last_chars']:
        print(f"  '{char}': {count}")


if __name__ == "__main__":
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words from {len(corpus.folios)} folios\n")

    results = analyze_corpus(corpus)
    print_analysis(results)
