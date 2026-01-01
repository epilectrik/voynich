"""
Voynich Translator

Uses dictionary.json to translate any folio.
Tracks coverage, suggests new entries, and updates dictionary.
"""

import sys
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

DICT_PATH = project_root / "dictionary.json"


class Translator:
    def __init__(self):
        self.dictionary = self.load_dictionary()
        self.corpus = None

    def load_dictionary(self) -> Dict:
        """Load the translation dictionary."""
        if DICT_PATH.exists():
            with open(DICT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0", "entries": {}}

    def save_dictionary(self):
        """Save the dictionary back to file."""
        self.dictionary["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(DICT_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, indent=2, ensure_ascii=False)
        print(f"Dictionary saved to {DICT_PATH}")

    def load_corpus(self):
        """Load the Voynich corpus."""
        if self.corpus is None:
            data_dir = project_root / "data" / "transcriptions"
            self.corpus = load_corpus(str(data_dir))
        return self.corpus

    def get_folio(self, folio: str) -> List[str]:
        """Get words from a specific folio."""
        corpus = self.load_corpus()
        return [w.text for w in corpus.words if w.folio == folio]

    def translate_word(self, word: str) -> Tuple[str, Optional[str], float]:
        """
        Translate a single word.
        Returns (translation, category, confidence)
        """
        entries = self.dictionary.get("entries", {})
        if word in entries:
            entry = entries[word]
            latin = entry.get("latin", "?")
            cat = entry.get("category")
            conf = entry.get("confidence", 0)
            return latin, cat, conf
        return f"[{word}]", None, 0

    def translate_folio(self, folio: str) -> List[Dict]:
        """Translate an entire folio."""
        words = self.get_folio(folio)
        result = []
        for word in words:
            latin, cat, conf = self.translate_word(word)
            result.append({
                "voynich": word,
                "latin": latin,
                "category": cat,
                "confidence": conf
            })
        return result

    def coverage(self, folio: str) -> Dict:
        """Calculate translation coverage for a folio."""
        translated = self.translate_folio(folio)
        total = len(translated)
        done = sum(1 for t in translated if t["category"] is not None)

        # By confidence level
        high_conf = sum(1 for t in translated if t["confidence"] >= 0.6)
        med_conf = sum(1 for t in translated if 0.3 <= t["confidence"] < 0.6)

        return {
            "total": total,
            "translated": done,
            "percentage": done / total * 100 if total > 0 else 0,
            "high_confidence": high_conf,
            "medium_confidence": med_conf
        }

    def show_translation(self, folio: str, show_confidence: bool = False):
        """Display translated folio."""
        translated = self.translate_folio(folio)
        cov = self.coverage(folio)

        print(f"\n{'='*70}")
        print(f"FOLIO {folio}")
        print(f"Coverage: {cov['translated']}/{cov['total']} ({cov['percentage']:.1f}%)")
        print(f"High confidence: {cov['high_confidence']} | Medium: {cov['medium_confidence']}")
        print(f"{'='*70}\n")

        # Print in chunks
        for i in range(0, len(translated), 6):
            chunk = translated[i:i+6]

            # Voynich line
            voy_line = ' '.join(f"{t['voynich']:<12}" for t in chunk)
            print(voy_line)

            # Latin line
            if show_confidence:
                lat_line = ' '.join(
                    f"{t['latin'][:10]:<10}{t['confidence']:.1f}" if t['category'] else f"{t['latin']:<12}"
                    for t in chunk
                )
            else:
                lat_line = ' '.join(f"{t['latin']:<12}" for t in chunk)
            print(lat_line)
            print()

    def suggest_entries(self, folio: str, n: int = 10) -> List[Tuple[str, int]]:
        """Suggest words that should be added to dictionary."""
        words = self.get_folio(folio)
        freq = Counter(words)
        entries = self.dictionary.get("entries", {})

        # Words not in dictionary, sorted by frequency
        missing = [(w, c) for w, c in freq.most_common() if w not in entries]
        return missing[:n]

    def add_entry(self, voynich: str, latin: str, english: str,
                  category: str, confidence: float = 0.5,
                  source: str = "", notes: str = ""):
        """Add a new entry to the dictionary."""
        if "entries" not in self.dictionary:
            self.dictionary["entries"] = {}

        self.dictionary["entries"][voynich] = {
            "latin": latin,
            "english": english,
            "category": category,
            "confidence": confidence,
            "source": source,
            "notes": notes
        }
        print(f"Added: {voynich} = {latin} ({english})")

    def update_entry(self, voynich: str, **kwargs):
        """Update an existing entry."""
        if voynich in self.dictionary.get("entries", {}):
            self.dictionary["entries"][voynich].update(kwargs)
            print(f"Updated: {voynich}")
        else:
            print(f"Entry not found: {voynich}")

    def remove_entry(self, voynich: str):
        """Remove an entry from the dictionary."""
        if voynich in self.dictionary.get("entries", {}):
            del self.dictionary["entries"][voynich]
            print(f"Removed: {voynich}")

    def show_dictionary(self, sort_by: str = "confidence"):
        """Display all dictionary entries."""
        entries = self.dictionary.get("entries", {})

        if sort_by == "confidence":
            sorted_entries = sorted(entries.items(),
                                   key=lambda x: -x[1].get("confidence", 0))
        else:
            sorted_entries = sorted(entries.items())

        print(f"\n{'='*70}")
        print(f"DICTIONARY ({len(entries)} entries)")
        print(f"{'='*70}\n")

        print(f"{'Voynich':<15} {'Latin':<12} {'English':<15} {'Cat':<6} {'Conf':<5} {'Source':<8}")
        print("-" * 70)

        for voy, entry in sorted_entries:
            latin = entry.get("latin", "?")[:12]
            english = entry.get("english", "?")[:15]
            cat = entry.get("category", "?")[:6]
            conf = entry.get("confidence", 0)
            source = entry.get("source", "")[:8]
            print(f"{voy:<15} {latin:<12} {english:<15} {cat:<6} {conf:<5.2f} {source:<8}")

    def find_patterns(self, folio: str) -> Dict:
        """Find repeated patterns in translation."""
        translated = self.translate_folio(folio)

        # Find sequences of translated words
        sequences = []
        current = []

        for t in translated:
            if t["category"]:
                current.append(t)
            else:
                if len(current) >= 2:
                    sequences.append(current)
                current = []

        if len(current) >= 2:
            sequences.append(current)

        return {
            "sequences": sequences,
            "count": len(sequences),
            "avg_length": sum(len(s) for s in sequences) / len(sequences) if sequences else 0
        }

    def test_on_folios(self, folios: List[str]):
        """Test dictionary coverage across multiple folios."""
        print(f"\n{'='*70}")
        print("COVERAGE ACROSS FOLIOS")
        print(f"{'='*70}\n")

        total_words = 0
        total_translated = 0

        for folio in folios:
            cov = self.coverage(folio)
            total_words += cov["total"]
            total_translated += cov["translated"]
            print(f"{folio}: {cov['translated']:>3}/{cov['total']:<3} ({cov['percentage']:>5.1f}%)")

        overall = total_translated / total_words * 100 if total_words > 0 else 0
        print(f"\nOverall: {total_translated}/{total_words} ({overall:.1f}%)")


def main():
    translator = Translator()

    print("="*70)
    print("VOYNICH TRANSLATOR")
    print("="*70)

    # Show current dictionary
    translator.show_dictionary()

    # Translate f1r
    translator.show_translation("f1r")

    # Suggest new entries
    print("\n" + "="*70)
    print("SUGGESTED ENTRIES (most frequent untranslated words)")
    print("="*70 + "\n")

    suggestions = translator.suggest_entries("f1r", n=15)
    for word, count in suggestions:
        print(f"  {word:<15} ({count}x)")

    # Test across first few folios
    folios = ["f1r", "f1v", "f2r", "f2v", "f3r"]
    translator.test_on_folios(folios)

    # Find translated sequences
    print("\n" + "="*70)
    print("TRANSLATED SEQUENCES (potential sentences)")
    print("="*70 + "\n")

    patterns = translator.find_patterns("f1r")
    for seq in patterns["sequences"][:10]:
        voy = ' '.join(t["voynich"] for t in seq)
        lat = ' '.join(t["latin"] for t in seq)
        print(f"  {voy}")
        print(f"  -> {lat}")
        print()

    # Save
    translator.save_dictionary()


if __name__ == "__main__":
    main()
