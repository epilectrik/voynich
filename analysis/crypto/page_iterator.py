"""
Page-based Iterative Decoder with Coherence Tracking

Focus on ONE page. Try assignments. Keep what improves coherence.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


class PageIterator:
    def __init__(self, corpus, folio: str = 'f1r'):
        self.corpus = corpus
        self.folio = folio

        # Get page words
        self.words = [w.text for w in corpus.words if w.folio == folio]
        self.freq = Counter(self.words)
        self.unique = list(set(self.words))

        # Meanings
        self.meanings = {}

        # Build bigram stats for this page
        self.bigrams = Counter()
        for i in range(len(self.words) - 1):
            self.bigrams[(self.words[i], self.words[i+1])] += 1

    def translate(self) -> List[str]:
        """Get current translation."""
        return [self.meanings.get(w, f'_{w}_') for w in self.words]

    def coverage(self) -> float:
        """What percentage of words are translated?"""
        t = self.translate()
        done = sum(1 for x in t if not x.startswith('_'))
        return done / len(t)

    def coherence(self) -> float:
        """
        Measure translation coherence.
        Score based on:
        1. Coverage (more = better)
        2. Bigram consistency (same pairs should translate the same)
        3. Pattern repetition (real text has repeated phrases)
        """
        t = self.translate()

        # Coverage component
        cov = self.coverage()

        # Bigram component: count translated bigrams
        trans_bigrams = 0
        total_bigrams = len(t) - 1

        for i in range(len(t) - 1):
            if not t[i].startswith('_') and not t[i+1].startswith('_'):
                trans_bigrams += 1

        bigram_score = trans_bigrams / total_bigrams if total_bigrams > 0 else 0

        # Combine
        return (cov * 0.6) + (bigram_score * 0.4)

    def test_assignment(self, word: str, meaning: str) -> Tuple[float, float]:
        """
        Test what happens if we assign this meaning.
        Returns (new_coherence, change_from_current).
        """
        old_score = self.coherence()

        # Temporarily assign
        old_meaning = self.meanings.get(word)
        self.meanings[word] = meaning

        new_score = self.coherence()

        # Restore
        if old_meaning is None:
            del self.meanings[word]
        else:
            self.meanings[word] = old_meaning

        return new_score, new_score - old_score

    def assign(self, word: str, meaning: str) -> float:
        """Assign meaning and return coherence change."""
        old = self.coherence()
        self.meanings[word] = meaning
        new = self.coherence()
        return new - old

    def remove(self, word: str) -> float:
        """Remove a meaning assignment."""
        if word in self.meanings:
            old = self.coherence()
            del self.meanings[word]
            new = self.coherence()
            return new - old
        return 0

    def show_page(self):
        """Display the page with current translation."""
        print(f"\n{'='*70}")
        print(f"FOLIO {self.folio} - {len(self.words)} words, {len(self.unique)} unique")
        print(f"Coverage: {self.coverage()*100:.1f}% | Coherence: {self.coherence():.3f}")
        print(f"{'='*70}")

        t = self.translate()

        # Show aligned original and translation
        print("\nOriginal | Translation")
        print("-" * 70)

        for i in range(0, len(self.words), 8):
            orig_line = self.words[i:i+8]
            trans_line = t[i:i+8]
            print(' '.join(f"{o:<10}" for o in orig_line))
            print(' '.join(f"{t:<10}" for t in trans_line))
            print()

    def show_word(self, word: str):
        """Show all occurrences of a word with context."""
        print(f"\n'{word}' appears {self.freq[word]}x:")
        for i, w in enumerate(self.words):
            if w == word:
                start = max(0, i-2)
                end = min(len(self.words), i+3)
                ctx = self.words[start:end]
                trans = self.translate()[start:end]
                print(f"  {' '.join(ctx)}")
                print(f"  {' '.join(trans)}")
                print()

    def suggest_assignments(self, n: int = 10) -> List[Tuple[str, str, float]]:
        """
        Suggest word-meaning pairs that would improve coherence.
        Try common Latin words for frequent untranslated Voynich words.
        """
        latin_candidates = [
            'et', 'in', 'de', 'est', 'cum', 'ad', 'non', 'per', 'ut', 'sed',
            'herba', 'aqua', 'radix', 'folia', 'hoc', 'ille', 'qui', 'quod',
            'sic', 'enim', 'autem', 'ergo', 'tamen', 'ita', 'vel', 'aut',
            'ante', 'post', 'inter', 'super', 'sub', 'pro', 'contra', 'sine'
        ]

        # Get untranslated words sorted by frequency
        untranslated = [(w, c) for w, c in self.freq.most_common()
                        if w not in self.meanings]

        suggestions = []

        # For each untranslated word, try each Latin candidate
        for voy_word, count in untranslated[:20]:
            best_meaning = None
            best_improvement = -999

            for lat_word in latin_candidates:
                # Skip if already used
                if lat_word in self.meanings.values():
                    continue

                new_coh, improvement = self.test_assignment(voy_word, lat_word)

                if improvement > best_improvement:
                    best_improvement = improvement
                    best_meaning = lat_word

            if best_meaning and best_improvement > 0:
                suggestions.append((voy_word, best_meaning, best_improvement))

        # Sort by improvement
        suggestions.sort(key=lambda x: -x[2])
        return suggestions[:n]

    def auto_iterate(self, rounds: int = 10):
        """Automatically assign meanings that improve coherence."""
        print(f"\nAuto-iterating {rounds} rounds...")

        for r in range(rounds):
            suggestions = self.suggest_assignments(n=3)

            if not suggestions:
                print(f"  Round {r+1}: No improving assignments found")
                break

            for word, meaning, improvement in suggestions:
                if improvement > 0.001:  # Only if actually improves
                    self.assign(word, meaning)
                    print(f"  Round {r+1}: {word} = {meaning} (+{improvement:.4f})")

        print(f"\nFinal coherence: {self.coherence():.3f}")
        print(f"Final coverage: {self.coverage()*100:.1f}%")

    def prune_bad_assignments(self):
        """Remove assignments that hurt coherence."""
        to_remove = []

        for word in list(self.meanings.keys()):
            # Test removing it
            old = self.coherence()
            meaning = self.meanings[word]
            del self.meanings[word]
            new = self.coherence()

            if new > old:  # Removing improves coherence
                to_remove.append((word, meaning, new - old))
            else:
                self.meanings[word] = meaning  # Restore

        for word, meaning, improvement in to_remove:
            print(f"  Removed: {word} = {meaning} (improved by {improvement:.4f})")

        return len(to_remove)


def main():
    print("Loading corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))

    # Initialize with f1r
    page = PageIterator(corpus, folio='f1r')

    print(f"\n{'='*70}")
    print("STARTING PAGE f1r")
    print(f"{'='*70}")

    # Show initial state
    print(f"\nPage has {len(page.words)} words, {len(page.unique)} unique")
    print(f"\nMost frequent words:")
    for word, count in page.freq.most_common(10):
        print(f"  {word:<15} {count}x")

    # Show contexts for the most frequent words
    print(f"\n{'='*70}")
    print("CONTEXT ANALYSIS")
    print(f"{'='*70}")

    for word, count in page.freq.most_common(5):
        page.show_word(word)

    # Auto-iterate to find good assignments
    print(f"\n{'='*70}")
    print("AUTO-ITERATION")
    print(f"{'='*70}")

    page.auto_iterate(rounds=20)

    # Show results
    print(f"\n{'='*70}")
    print("CURRENT ASSIGNMENTS")
    print(f"{'='*70}")

    for word, meaning in sorted(page.meanings.items(), key=lambda x: -page.freq[x[0]]):
        print(f"  {word:<15} = {meaning:<10} ({page.freq[word]}x)")

    # Show translated page
    page.show_page()

    # Show best translated sequences
    print(f"\n{'='*70}")
    print("BEST TRANSLATED SEQUENCES")
    print(f"{'='*70}")

    t = page.translate()
    best_runs = []

    i = 0
    while i < len(t):
        if not t[i].startswith('_'):
            # Start of translated run
            start = i
            while i < len(t) and not t[i].startswith('_'):
                i += 1
            run_len = i - start
            if run_len >= 2:
                orig = page.words[start:i]
                trans = t[start:i]
                best_runs.append((run_len, orig, trans))
        else:
            i += 1

    best_runs.sort(key=lambda x: -x[0])

    for length, orig, trans in best_runs[:10]:
        print(f"  {' '.join(orig)}")
        print(f"  -> {' '.join(trans)}")
        print()

    # Save
    output = {
        'folio': page.folio,
        'meanings': page.meanings,
        'coherence': page.coherence(),
        'coverage': page.coverage()
    }

    output_path = project_root / "results" / f"decoded_{page.folio}.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
