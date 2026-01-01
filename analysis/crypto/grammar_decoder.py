"""
Grammar-Aware Page Decoder

Constraints:
1. One Voynich word = one Latin meaning (no duplicates)
2. Latin grammar patterns must be followed
3. Botanical context (it's a herbal manuscript)
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import json
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus


# Latin word categories
LATIN_WORDS = {
    # Nouns (botanical/medical)
    'nouns': {
        'herba': 'herb/plant',
        'radix': 'root',
        'folia': 'leaves',
        'flos': 'flower',
        'semen': 'seed',
        'aqua': 'water',
        'succus': 'juice',
        'cortex': 'bark',
        'oleum': 'oil',
        'sal': 'salt',
        'pulvis': 'powder',
        'natura': 'nature',
        'virtus': 'power/virtue',
        'morbus': 'disease',
        'dolor': 'pain',
        'febris': 'fever',
        'venenum': 'poison',
        'remedium': 'remedy',
        'medicina': 'medicine',
    },
    # Verbs
    'verbs': {
        'est': 'is',
        'sunt': 'are',
        'habet': 'has',
        'facit': 'makes',
        'curat': 'cures',
        'sanat': 'heals',
        'prodest': 'benefits',
        'nocet': 'harms',
        'crescit': 'grows',
        'nascitur': 'is born/grows',
    },
    # Prepositions
    'preps': {
        'in': 'in',
        'de': 'of/from',
        'cum': 'with',
        'ad': 'to/for',
        'per': 'through',
        'ex': 'out of',
        'pro': 'for',
        'sine': 'without',
        'contra': 'against',
        'ante': 'before',
        'post': 'after',
    },
    # Conjunctions
    'conj': {
        'et': 'and',
        'vel': 'or',
        'aut': 'or',
        'sed': 'but',
        'atque': 'and also',
        'neque': 'and not',
    },
    # Adjectives
    'adj': {
        'bonus': 'good',
        'malus': 'bad',
        'magnus': 'great',
        'parvus': 'small',
        'calidus': 'hot',
        'frigidus': 'cold',
        'siccus': 'dry',
        'humidus': 'wet',
        'albus': 'white',
        'niger': 'black',
        'viridis': 'green',
    },
    # Demonstratives/pronouns
    'pron': {
        'hic': 'this',
        'ille': 'that',
        'qui': 'which/who',
        'quid': 'what',
        'hoc': 'this (neuter)',
        'id': 'it',
        'eius': 'of it/his',
    },
    # Adverbs
    'adv': {
        'valde': 'very',
        'bene': 'well',
        'male': 'badly',
        'sic': 'thus',
        'ita': 'so',
        'non': 'not',
        'semper': 'always',
        'saepe': 'often',
    }
}

# Valid Latin patterns (simplified)
# Pattern: category sequence that makes grammatical sense
VALID_PATTERNS = [
    ('nouns', 'verbs'),           # herba est
    ('nouns', 'adj'),             # herba bona
    ('preps', 'nouns'),           # in aqua
    ('adj', 'nouns'),             # bona herba
    ('nouns', 'conj', 'nouns'),   # herba et radix
    ('verbs', 'adj'),             # est bonus
    ('verbs', 'preps'),           # est in
    ('pron', 'nouns'),            # hic herba
    ('pron', 'verbs'),            # hic est
    ('adv', 'verbs'),             # non est
    ('adv', 'adj'),               # valde bonus
    ('conj', 'nouns'),            # et herba
    ('conj', 'adj'),              # et bonus
]


class GrammarDecoder:
    def __init__(self, corpus, folio: str = 'f1r'):
        self.corpus = corpus
        self.folio = folio

        # Get page words
        self.words = [w.text for w in corpus.words if w.folio == folio]
        self.freq = Counter(self.words)
        self.unique = list(set(self.words))

        # Meanings: voynich -> (latin, category)
        self.meanings = {}

        # Reverse mapping for uniqueness
        self.used_latin = set()

        # Build all Latin words with categories
        self.latin_by_category = LATIN_WORDS
        self.latin_to_category = {}
        for cat, words in LATIN_WORDS.items():
            for word in words:
                self.latin_to_category[word] = cat

    def get_category(self, latin_word: str) -> Optional[str]:
        """Get grammatical category of a Latin word."""
        return self.latin_to_category.get(latin_word)

    def translate(self) -> List[Tuple[str, Optional[str]]]:
        """Translate page, returning (latin_word, category) pairs."""
        result = []
        for word in self.words:
            if word in self.meanings:
                latin, cat = self.meanings[word]
                result.append((latin, cat))
            else:
                result.append((f'[{word}]', None))
        return result

    def is_valid_sequence(self, cat1: Optional[str], cat2: Optional[str]) -> bool:
        """Check if two categories can appear adjacent."""
        if cat1 is None or cat2 is None:
            return True  # Unknown is always OK

        for pattern in VALID_PATTERNS:
            if len(pattern) >= 2:
                if pattern[0] == cat1 and pattern[1] == cat2:
                    return True
                # Also check reverse for some patterns
                if pattern[0] == cat2 and pattern[1] == cat1:
                    return True

        return False

    def grammar_score(self) -> float:
        """Score based on grammatical validity of adjacent pairs."""
        trans = self.translate()

        valid_pairs = 0
        total_pairs = 0

        for i in range(len(trans) - 1):
            word1, cat1 = trans[i]
            word2, cat2 = trans[i+1]

            # Skip if either is untranslated
            if cat1 is None or cat2 is None:
                continue

            total_pairs += 1
            if self.is_valid_sequence(cat1, cat2):
                valid_pairs += 1

        return valid_pairs / total_pairs if total_pairs > 0 else 0

    def coverage(self) -> float:
        """What percentage of words are translated?"""
        trans = self.translate()
        done = sum(1 for w, c in trans if c is not None)
        return done / len(trans)

    def combined_score(self) -> float:
        """Combined score: coverage + grammar."""
        cov = self.coverage()
        gram = self.grammar_score()
        return (cov * 0.4) + (gram * 0.6)

    def assign(self, voynich: str, latin: str) -> bool:
        """
        Assign a meaning. Returns False if Latin word already used.
        """
        if latin in self.used_latin:
            return False

        cat = self.get_category(latin)
        if cat is None:
            return False

        # Remove old assignment if exists
        if voynich in self.meanings:
            old_latin, _ = self.meanings[voynich]
            self.used_latin.discard(old_latin)

        self.meanings[voynich] = (latin, cat)
        self.used_latin.add(latin)
        return True

    def test_assign(self, voynich: str, latin: str) -> Tuple[float, float]:
        """Test an assignment, return (new_score, improvement)."""
        if latin in self.used_latin:
            return 0, -999

        cat = self.get_category(latin)
        if cat is None:
            return 0, -999

        old_score = self.combined_score()

        # Temporarily assign
        old_meaning = self.meanings.get(voynich)
        self.meanings[voynich] = (latin, cat)
        self.used_latin.add(latin)

        new_score = self.combined_score()

        # Restore
        del self.meanings[voynich]
        self.used_latin.discard(latin)
        if old_meaning:
            self.meanings[voynich] = old_meaning
            self.used_latin.add(old_meaning[0])

        return new_score, new_score - old_score

    def find_best_assignments(self, n: int = 5) -> List[Tuple[str, str, str, float]]:
        """
        Find best (voynich, latin, category, improvement) assignments.
        """
        candidates = []

        # Get untranslated words by frequency
        untranslated = [(w, c) for w, c in self.freq.most_common()
                        if w not in self.meanings]

        for voy, count in untranslated[:30]:
            for cat, words in self.latin_by_category.items():
                for latin in words:
                    if latin in self.used_latin:
                        continue

                    new_score, improvement = self.test_assign(voy, latin)
                    if improvement > 0:
                        candidates.append((voy, latin, cat, improvement, count))

        # Sort by improvement * frequency
        candidates.sort(key=lambda x: -(x[3] * x[4]))
        return [(v, l, c, i) for v, l, c, i, _ in candidates[:n]]

    def auto_decode(self, rounds: int = 30):
        """Automatically find and apply best assignments."""
        print(f"Auto-decoding {rounds} rounds...\n")

        for r in range(rounds):
            best = self.find_best_assignments(n=3)

            if not best:
                print(f"Round {r+1}: No more improvements found")
                break

            for voy, latin, cat, improvement in best:
                if self.assign(voy, latin):
                    count = self.freq[voy]
                    print(f"  {voy:<12} = {latin:<10} ({cat:<6}) +{improvement:.4f} [{count}x]")

            # Show progress every 5 rounds
            if (r + 1) % 5 == 0:
                print(f"\n  --- Round {r+1}: coverage={self.coverage()*100:.1f}%, grammar={self.grammar_score()*100:.1f}% ---\n")

    def show_translation(self):
        """Display the translated page."""
        trans = self.translate()

        print(f"\n{'='*70}")
        print(f"TRANSLATION - {self.folio}")
        print(f"Coverage: {self.coverage()*100:.1f}% | Grammar: {self.grammar_score()*100:.1f}%")
        print(f"{'='*70}\n")

        # Show with categories
        for i in range(0, len(trans), 6):
            chunk = trans[i:i+6]
            orig = self.words[i:i+6]

            # Original line
            print(' '.join(f"{o:<12}" for o in orig))

            # Translation with categories
            trans_line = []
            for latin, cat in chunk:
                if cat:
                    trans_line.append(f"{latin}({cat[:3]})")
                else:
                    trans_line.append(latin)
            print(' '.join(f"{t:<12}" for t in trans_line))
            print()

    def show_sentences(self):
        """Try to identify sentence-like structures."""
        trans = self.translate()

        print(f"\n{'='*70}")
        print("POTENTIAL SENTENCES")
        print(f"{'='*70}\n")

        # Find runs of translated words with valid grammar
        current_run = []
        current_orig = []

        for i, ((latin, cat), orig) in enumerate(zip(trans, self.words)):
            if cat is not None:
                current_run.append((latin, cat))
                current_orig.append(orig)
            else:
                if len(current_run) >= 3:
                    # Check grammar validity
                    valid = True
                    for j in range(len(current_run) - 1):
                        if not self.is_valid_sequence(current_run[j][1], current_run[j+1][1]):
                            valid = False
                            break

                    if valid:
                        orig_str = ' '.join(current_orig)
                        trans_str = ' '.join(w for w, c in current_run)
                        print(f"  {orig_str}")
                        print(f"  -> {trans_str}")
                        print()

                current_run = []
                current_orig = []


def main():
    print("Loading corpus...")
    data_dir = project_root / "data" / "transcriptions"
    corpus = load_corpus(str(data_dir))

    decoder = GrammarDecoder(corpus, folio='f1r')

    print(f"\n{'='*70}")
    print(f"GRAMMAR-AWARE DECODER - {decoder.folio}")
    print(f"{'='*70}")
    print(f"Words: {len(decoder.words)} | Unique: {len(decoder.unique)}")
    print(f"Latin vocabulary: {sum(len(w) for w in LATIN_WORDS.values())} words")

    # Show word frequencies
    print(f"\nTop words:")
    for word, count in decoder.freq.most_common(10):
        print(f"  {word:<15} {count}x")

    # Auto-decode
    print(f"\n{'='*70}")
    print("AUTO-DECODING")
    print(f"{'='*70}")

    decoder.auto_decode(rounds=40)

    # Show results
    print(f"\n{'='*70}")
    print("FINAL ASSIGNMENTS")
    print(f"{'='*70}")

    for voy, (latin, cat) in sorted(decoder.meanings.items(),
                                     key=lambda x: -decoder.freq[x[0]]):
        count = decoder.freq[voy]
        print(f"  {voy:<15} = {latin:<10} ({cat}) [{count}x]")

    # Show translation
    decoder.show_translation()

    # Show sentences
    decoder.show_sentences()

    # Save
    output = {
        'folio': decoder.folio,
        'meanings': {v: {'latin': l, 'category': c}
                    for v, (l, c) in decoder.meanings.items()},
        'coverage': decoder.coverage(),
        'grammar_score': decoder.grammar_score()
    }

    output_path = project_root / "results" / f"grammar_{decoder.folio}.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
