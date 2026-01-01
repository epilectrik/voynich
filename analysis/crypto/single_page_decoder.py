"""
Single Page Iterative Decoder

Start with ONE page, build strong meanings, then expand.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


class SinglePageDecoder:
    def __init__(self, corpus, folio: str = 'f1r'):
        self.corpus = corpus
        self.target_folio = folio

        # Extract words from target folio
        self.page_words = [w.text for w in corpus.words if w.folio == folio]
        self.page_sequence = self.page_words.copy()

        # Word stats for this page
        self.word_freq = Counter(self.page_words)
        self.unique_words = list(self.word_freq.keys())

        # Meanings and confidence
        self.meanings = {}
        self.confidence = {}

        # Build adjacency (what words appear next to each other)
        self.left_neighbors = defaultdict(Counter)
        self.right_neighbors = defaultdict(Counter)
        self._build_neighbors()

    def _build_neighbors(self):
        """Track which words appear next to which."""
        for i, word in enumerate(self.page_sequence):
            if i > 0:
                self.left_neighbors[word][self.page_sequence[i-1]] += 1
            if i < len(self.page_sequence) - 1:
                self.right_neighbors[word][self.page_sequence[i+1]] += 1

    def show_page_stats(self):
        """Display statistics about the target page."""
        print(f"\n{'='*60}")
        print(f"PAGE: {self.target_folio}")
        print(f"{'='*60}")
        print(f"Total words: {len(self.page_words)}")
        print(f"Unique words: {len(self.unique_words)}")
        print(f"\nWord frequency:")
        for word, count in self.word_freq.most_common(15):
            print(f"  {word:<15} {count:>3}x")

        print(f"\nFull text:")
        print('-' * 60)
        # Print in lines of ~10 words
        for i in range(0, len(self.page_sequence), 10):
            print(' '.join(self.page_sequence[i:i+10]))

    def show_word_context(self, word: str):
        """Show all contexts where a word appears."""
        print(f"\nContexts for '{word}':")
        for i, w in enumerate(self.page_sequence):
            if w == word:
                start = max(0, i-2)
                end = min(len(self.page_sequence), i+3)
                context = self.page_sequence[start:end]
                # Mark the target word
                marked = [f"[{x}]" if x == word else x for x in context]
                print(f"  {' '.join(marked)}")

    def assign_meaning(self, voynich_word: str, meaning: str, conf: float = 0.5):
        """Manually assign a meaning to a word."""
        self.meanings[voynich_word] = meaning
        self.confidence[voynich_word] = conf
        print(f"  Assigned: {voynich_word} = '{meaning}' (conf={conf})")

    def translate_page(self) -> List[str]:
        """Translate the page with current meanings."""
        result = []
        for word in self.page_sequence:
            if word in self.meanings:
                result.append(self.meanings[word])
            else:
                result.append(f'[{word}]')
        return result

    def show_translation(self):
        """Display current translation."""
        translated = self.translate_page()

        n_done = sum(1 for t in translated if not t.startswith('['))
        pct = 100 * n_done / len(translated)

        print(f"\nTranslation ({n_done}/{len(translated)} = {pct:.0f}% complete):")
        print('-' * 60)

        for i in range(0, len(translated), 10):
            line = translated[i:i+10]
            print(' '.join(line))

    def coherence_score(self) -> float:
        """
        Score how coherent the current translation is.
        Higher = more words translated, more consistent patterns.
        """
        translated = self.translate_page()

        # Coverage score
        n_translated = sum(1 for t in translated if not t.startswith('['))
        coverage = n_translated / len(translated)

        # Consistency score: same voynich word -> same meaning
        # (This should always be 1.0 with our approach, but check)
        consistency = 1.0

        # Pattern score: do translated words form reasonable sequences?
        # For now, just count how many adjacent pairs are both translated
        adjacent_pairs = 0
        for i in range(len(translated) - 1):
            if not translated[i].startswith('[') and not translated[i+1].startswith('['):
                adjacent_pairs += 1

        pattern_score = adjacent_pairs / (len(translated) - 1) if len(translated) > 1 else 0

        return (coverage * 0.5) + (pattern_score * 0.5)

    def suggest_next_word(self) -> List[Tuple[str, int, str]]:
        """Suggest which word to assign meaning to next."""
        suggestions = []

        for word in self.unique_words:
            if word in self.meanings:
                continue

            count = self.word_freq[word]

            # Check how many of its neighbors are already translated
            translated_neighbors = 0
            total_neighbors = 0

            for neighbor, n_count in self.left_neighbors[word].items():
                total_neighbors += n_count
                if neighbor in self.meanings:
                    translated_neighbors += n_count

            for neighbor, n_count in self.right_neighbors[word].items():
                total_neighbors += n_count
                if neighbor in self.meanings:
                    translated_neighbors += n_count

            # Priority: frequent words with translated neighbors
            neighbor_ratio = translated_neighbors / total_neighbors if total_neighbors > 0 else 0
            priority = count * (1 + neighbor_ratio)

            suggestions.append((word, count, f"{translated_neighbors}/{total_neighbors} neighbors done"))

        suggestions.sort(key=lambda x: -x[1])  # Sort by frequency
        return suggestions[:10]

    def interactive_assign(self):
        """Interactive mode for assigning meanings."""
        print("\n" + "="*60)
        print("INTERACTIVE MEANING ASSIGNMENT")
        print("="*60)
        print("Commands:")
        print("  <word> = <meaning>  : Assign meaning")
        print("  show <word>         : Show word contexts")
        print("  status              : Show current translation")
        print("  suggest             : Suggest next word to assign")
        print("  score               : Show coherence score")
        print("  done                : Exit interactive mode")
        print("="*60)

        while True:
            try:
                cmd = input("\n> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            if cmd == 'done':
                break
            elif cmd == 'status':
                self.show_translation()
            elif cmd == 'suggest':
                suggestions = self.suggest_next_word()
                print("\nSuggested words to assign next:")
                for word, count, info in suggestions:
                    print(f"  {word:<15} ({count}x, {info})")
            elif cmd == 'score':
                score = self.coherence_score()
                print(f"\nCoherence score: {score:.3f}")
            elif cmd.startswith('show '):
                word = cmd[5:].strip()
                self.show_word_context(word)
            elif '=' in cmd:
                parts = cmd.split('=')
                if len(parts) == 2:
                    word = parts[0].strip()
                    meaning = parts[1].strip()
                    if word in self.unique_words:
                        self.assign_meaning(word, meaning, 0.5)
                    else:
                        print(f"  Word '{word}' not found on this page")
            else:
                print(f"  Unknown command: {cmd}")


def main():
    print("Loading corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))

    # Start with f1r
    decoder = SinglePageDecoder(corpus, folio='f1r')
    decoder.show_page_stats()

    # Bootstrap with some initial guesses based on our analysis
    print("\n" + "="*60)
    print("INITIAL ASSIGNMENTS (based on previous analysis)")
    print("="*60)

    # Most frequent word on page is likely a function word
    top_word = decoder.word_freq.most_common(1)[0][0]

    # Show contexts for top words to help decide meanings
    print("\nTop words and their contexts:")
    for word, count in decoder.word_freq.most_common(5):
        print(f"\n'{word}' ({count}x):")
        decoder.show_word_context(word)

    # Make initial assignments based on frequency pattern
    print("\n" + "="*60)
    print("BOOTSTRAP ASSIGNMENTS")
    print("="*60)

    # Frequency-based initial guesses
    freq_order = [w for w, c in decoder.word_freq.most_common()]

    # Common Latin function words in order of frequency
    latin_guesses = ['et', 'in', 'de', 'est', 'cum', 'ad', 'non', 'per']

    for i, word in enumerate(freq_order[:min(len(latin_guesses), 8)]):
        decoder.assign_meaning(word, latin_guesses[i], conf=0.3)

    # Show result
    decoder.show_translation()

    print(f"\nCoherence score: {decoder.coherence_score():.3f}")

    # Save state
    output = {
        'folio': decoder.target_folio,
        'meanings': decoder.meanings,
        'confidence': decoder.confidence,
        'page_text': decoder.page_sequence
    }

    output_path = project_root / "results" / f"page_{decoder.target_folio}_meanings.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")

    # Offer interactive mode
    print("\n" + "="*60)
    print("Enter 'interactive' to manually assign meanings, or 'quit' to exit")
    print("="*60)


if __name__ == "__main__":
    main()
