"""
Iterative Meaning Assignment Decoder

Approach:
1. Assign initial meanings to words based on frequency/context
2. Translate text with current mappings
3. Score translations for coherence (do word pairs make sense?)
4. Keep good mappings, discard bad ones
5. Try new guesses for unassigned words
6. Iterate until meaning strengthens
"""

import sys
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

# Latin word frequencies and common words
LATIN_COMMON = {
    # Function words (most frequent)
    'et': 0.030,      # and
    'in': 0.025,      # in
    'est': 0.020,     # is
    'non': 0.015,     # not
    'ad': 0.012,      # to
    'cum': 0.012,     # with
    'de': 0.010,      # of/from
    'ut': 0.010,      # as/that
    'sed': 0.008,     # but
    'per': 0.008,     # through
    'ex': 0.007,      # out of
    'ab': 0.006,      # from
    'si': 0.006,      # if
    'aut': 0.005,     # or
    'vel': 0.005,     # or
    'quod': 0.005,    # which/that
    'hoc': 0.004,     # this
    'iam': 0.004,     # now/already
    'pro': 0.004,     # for
    'sub': 0.003,     # under

    # Botanical/medical terms (for herbal sections)
    'herba': 0.003,   # herb
    'aqua': 0.003,    # water
    'radix': 0.002,   # root
    'folia': 0.002,   # leaves
    'semen': 0.002,   # seed
    'flos': 0.002,    # flower
    'remedium': 0.001, # remedy
    'natura': 0.001,  # nature
}

# Valid Latin word pairs (for coherence scoring)
VALID_PAIRS = {
    ('et', 'in'), ('in', 'aqua'), ('de', 'herba'), ('cum', 'aqua'),
    ('est', 'herba'), ('non', 'est'), ('ad', 'remedium'), ('per', 'aqua'),
    ('herba', 'est'), ('aqua', 'est'), ('folia', 'et'), ('radix', 'et'),
    ('hoc', 'est'), ('si', 'est'), ('ut', 'est'), ('aut', 'in'),
    ('et', 'folia'), ('et', 'radix'), ('et', 'aqua'), ('et', 'herba'),
    ('de', 'natura'), ('in', 'natura'), ('cum', 'herba'), ('ex', 'aqua'),
}

# Words that can follow each other in Latin
LATIN_BIGRAM_PATTERNS = {
    'et': {'in', 'ad', 'de', 'cum', 'per', 'ex', 'herba', 'aqua', 'folia', 'radix', 'hoc', 'non'},
    'in': {'aqua', 'herba', 'natura', 'hoc', 'remedium'},
    'de': {'herba', 'aqua', 'natura', 'hoc', 'radix', 'folia'},
    'est': {'herba', 'aqua', 'in', 'ad', 'cum', 'non', 'et'},
    'cum': {'aqua', 'herba', 'hoc', 'radix'},
    'non': {'est', 'in', 'ad', 'hoc'},
    'herba': {'est', 'et', 'in', 'cum', 'hoc'},
    'aqua': {'est', 'et', 'in', 'cum'},
}


class IterativeDecoder:
    def __init__(self, corpus):
        self.corpus = corpus
        self.words = corpus.all_words
        self.word_freq = Counter(self.words)
        self.unique_words = list(self.word_freq.keys())

        # Current mappings: voynich_word -> latin_word
        self.mappings = {}

        # Confidence scores for each mapping (0-1)
        self.confidence = {}

        # History of scores for tracking progress
        self.score_history = []

        # Word context cache
        self.word_contexts = self._build_contexts()

    def _build_contexts(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build context windows for each word (prev_word, next_word)."""
        contexts = defaultdict(list)
        for i, word in enumerate(self.words):
            prev_word = self.words[i-1] if i > 0 else None
            next_word = self.words[i+1] if i < len(self.words)-1 else None
            contexts[word].append((prev_word, next_word))
        return contexts

    def initialize_mappings(self):
        """Create initial guesses based on frequency matching."""
        print("Initializing mappings based on frequency...")

        # Sort Voynich words by frequency
        voy_sorted = self.word_freq.most_common()

        # Sort Latin words by frequency
        lat_sorted = sorted(LATIN_COMMON.items(), key=lambda x: -x[1])

        # Initial frequency-based mapping for top words
        for i, (voy_word, voy_count) in enumerate(voy_sorted[:30]):
            if i < len(lat_sorted):
                lat_word = lat_sorted[i][0]
                self.mappings[voy_word] = lat_word
                self.confidence[voy_word] = 0.3  # Low initial confidence

        # Add section-specific guesses
        # 'chedy' and 'shedy' are 100% in botanical - likely plant terms
        self.mappings['chedy'] = 'herba'
        self.confidence['chedy'] = 0.7  # Higher confidence

        self.mappings['shedy'] = 'aqua'
        self.confidence['shedy'] = 0.6

        print(f"  Initialized {len(self.mappings)} mappings")

    def translate_text(self, words: List[str]) -> List[str]:
        """Translate a sequence of words using current mappings."""
        result = []
        for word in words:
            if word in self.mappings:
                result.append(self.mappings[word])
            else:
                result.append(f'[{word}]')
        return result

    def score_pair(self, word1: Optional[str], word2: Optional[str]) -> float:
        """Score how coherent a pair of translated words is."""
        if word1 is None or word2 is None:
            return 0.0

        # Check if it's a known valid pair
        if (word1, word2) in VALID_PAIRS:
            return 1.0

        # Check if word1 can be followed by word2
        if word1 in LATIN_BIGRAM_PATTERNS:
            if word2 in LATIN_BIGRAM_PATTERNS[word1]:
                return 0.8

        # Check reverse
        if word2 in LATIN_BIGRAM_PATTERNS:
            if word1 in LATIN_BIGRAM_PATTERNS.get(word2, set()):
                return 0.5

        # Both are untranslated
        if word1.startswith('[') and word2.startswith('['):
            return 0.1

        # One translated, one not
        if word1.startswith('[') or word2.startswith('['):
            return 0.2

        # Both translated but no known pattern
        return 0.3

    def score_mapping(self, voy_word: str, lat_word: str) -> float:
        """Score how well a mapping fits in all contexts."""
        contexts = self.word_contexts.get(voy_word, [])
        if not contexts:
            return 0.0

        total_score = 0.0

        for prev_voy, next_voy in contexts:
            # Translate neighbors
            prev_lat = self.mappings.get(prev_voy) if prev_voy else None
            next_lat = self.mappings.get(next_voy) if next_voy else None

            # Score pairs
            score_prev = self.score_pair(prev_lat, lat_word) if prev_lat else 0.2
            score_next = self.score_pair(lat_word, next_lat) if next_lat else 0.2

            total_score += (score_prev + score_next) / 2

        return total_score / len(contexts)

    def evaluate_all_mappings(self) -> Dict[str, float]:
        """Evaluate coherence scores for all current mappings."""
        scores = {}
        for voy_word, lat_word in self.mappings.items():
            scores[voy_word] = self.score_mapping(voy_word, lat_word)
        return scores

    def prune_bad_mappings(self, threshold: float = 0.25):
        """Remove mappings with low coherence scores."""
        scores = self.evaluate_all_mappings()

        to_remove = []
        for voy_word, score in scores.items():
            if score < threshold and self.confidence.get(voy_word, 0) < 0.5:
                to_remove.append(voy_word)

        for word in to_remove:
            del self.mappings[word]
            if word in self.confidence:
                del self.confidence[word]

        return len(to_remove)

    def try_new_mappings(self, n_attempts: int = 10):
        """Try new mappings for unmapped frequent words."""
        # Find frequent unmapped words
        unmapped = [w for w, c in self.word_freq.most_common(100)
                   if w not in self.mappings]

        # Latin words not yet used
        used_latin = set(self.mappings.values())
        available_latin = [w for w in LATIN_COMMON.keys() if w not in used_latin]

        if not unmapped or not available_latin:
            return 0

        new_mappings = 0

        for voy_word in unmapped[:n_attempts]:
            best_score = 0
            best_latin = None

            for lat_word in available_latin:
                # Temporarily add mapping
                self.mappings[voy_word] = lat_word
                score = self.score_mapping(voy_word, lat_word)
                del self.mappings[voy_word]

                if score > best_score:
                    best_score = score
                    best_latin = lat_word

            if best_latin and best_score > 0.3:
                self.mappings[voy_word] = best_latin
                self.confidence[voy_word] = best_score
                available_latin.remove(best_latin)
                new_mappings += 1

        return new_mappings

    def iterate(self, n_iterations: int = 20):
        """Run the iterative refinement process."""
        print(f"\nStarting iterative refinement ({n_iterations} iterations)...")

        for i in range(n_iterations):
            # Evaluate current state
            scores = self.evaluate_all_mappings()
            avg_score = sum(scores.values()) / len(scores) if scores else 0
            self.score_history.append(avg_score)

            # Prune bad mappings
            pruned = self.prune_bad_mappings()

            # Try new mappings
            added = self.try_new_mappings()

            # Update confidence based on scores
            for voy_word in self.mappings:
                if voy_word in scores:
                    # Increase confidence for good scores, decrease for bad
                    current_conf = self.confidence.get(voy_word, 0.3)
                    if scores[voy_word] > 0.5:
                        self.confidence[voy_word] = min(1.0, current_conf + 0.1)
                    elif scores[voy_word] < 0.3:
                        self.confidence[voy_word] = max(0.0, current_conf - 0.1)

            print(f"  Iteration {i+1}: avg_score={avg_score:.3f}, "
                  f"mappings={len(self.mappings)}, pruned={pruned}, added={added}")

    def get_best_mappings(self, min_confidence: float = 0.4) -> Dict[str, Tuple[str, float]]:
        """Get mappings above confidence threshold."""
        result = {}
        for voy_word, lat_word in self.mappings.items():
            conf = self.confidence.get(voy_word, 0)
            if conf >= min_confidence:
                result[voy_word] = (lat_word, conf)
        return result

    def translate_sample(self, n_words: int = 100) -> str:
        """Translate a sample of the text."""
        sample = self.words[:n_words]
        translated = self.translate_text(sample)
        return ' '.join(translated)

    def save_mappings(self, filepath: str):
        """Save current mappings to file."""
        data = {
            'mappings': self.mappings,
            'confidence': self.confidence,
            'score_history': self.score_history
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_mappings(self, filepath: str):
        """Load mappings from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.mappings = data['mappings']
        self.confidence = data['confidence']
        self.score_history = data.get('score_history', [])


def run_iterative_decoding():
    """Main function to run iterative decoding."""
    print("Loading Voynich corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))
    print(f"Loaded {len(corpus.words)} words\n")

    decoder = IterativeDecoder(corpus)

    print("=" * 70)
    print("ITERATIVE MEANING ASSIGNMENT")
    print("=" * 70)

    # Initialize
    decoder.initialize_mappings()

    # Show initial state
    print("\nInitial mappings:")
    for voy, lat in list(decoder.mappings.items())[:15]:
        conf = decoder.confidence.get(voy, 0)
        count = decoder.word_freq[voy]
        print(f"  {voy:<15} -> {lat:<12} (conf={conf:.2f}, count={count})")

    # Initial translation
    print("\nInitial translation (first 50 words):")
    print("-" * 60)
    print(decoder.translate_sample(50))

    # Run iterations
    decoder.iterate(n_iterations=30)

    # Show results
    print("\n" + "=" * 70)
    print("RESULTS AFTER ITERATION")
    print("=" * 70)

    best = decoder.get_best_mappings(min_confidence=0.4)
    print(f"\nHigh-confidence mappings ({len(best)} words):")
    print("-" * 50)

    # Sort by confidence
    sorted_mappings = sorted(best.items(), key=lambda x: -x[1][1])
    for voy, (lat, conf) in sorted_mappings[:25]:
        count = decoder.word_freq[voy]
        print(f"  {voy:<15} -> {lat:<12} conf={conf:.2f}  (appears {count}x)")

    # Final translation
    print("\nFinal translation (first 100 words):")
    print("-" * 60)
    translated = decoder.translate_sample(100)

    # Format nicely
    words = translated.split()
    line = []
    for word in words:
        line.append(word)
        if len(' '.join(line)) > 60:
            print(' '.join(line[:-1]))
            line = [word]
    if line:
        print(' '.join(line))

    # Score analysis
    print("\n" + "=" * 70)
    print("COHERENCE ANALYSIS")
    print("=" * 70)

    # Find best translated sequences
    print("\nMost coherent translated sequences:")

    words_list = corpus.all_words[:500]
    best_sequences = []

    for i in range(len(words_list) - 4):
        window = words_list[i:i+5]
        translated = decoder.translate_text(window)

        # Count how many are translated (not [bracketed])
        n_translated = sum(1 for w in translated if not w.startswith('['))

        if n_translated >= 3:
            # Score coherence
            score = 0
            for j in range(len(translated)-1):
                score += decoder.score_pair(translated[j], translated[j+1])
            score /= (len(translated) - 1)

            if score > 0.4:
                best_sequences.append((window, translated, score, n_translated))

    best_sequences.sort(key=lambda x: (-x[3], -x[2]))

    for window, translated, score, n_trans in best_sequences[:15]:
        print(f"  {' '.join(window)}")
        print(f"    -> {' '.join(translated)}")
        print(f"       (coherence={score:.2f}, {n_trans}/5 translated)")
        print()

    # Save mappings
    output_path = project_root / "results" / "learned_mappings.json"
    decoder.save_mappings(str(output_path))
    print(f"\nMappings saved to: {output_path}")

    return decoder


if __name__ == "__main__":
    decoder = run_iterative_decoding()
