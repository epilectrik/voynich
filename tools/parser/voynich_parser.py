"""
Voynich Manuscript Parser and Data Loader

Parses various transcription formats (EVA, interlinear) and provides
unified access to the manuscript text with metadata.
"""

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class VoynichWord:
    """Represents a single word from the Voynich Manuscript."""
    text: str
    folio: str
    section: str = ""
    quire: str = ""
    panel: str = ""
    language: str = ""  # Currier A or B
    hand: str = ""      # Scribal hand 1-5
    placement: str = ""
    line_number: int = 0
    transcriber: str = ""
    line_initial: bool = False
    line_final: bool = False
    par_initial: bool = False
    par_final: bool = False


@dataclass
class VoynichFolio:
    """Represents a single folio (page) of the manuscript."""
    folio_id: str
    words: List[VoynichWord] = field(default_factory=list)
    section: str = ""
    quire: str = ""
    language: str = ""
    hand: str = ""

    @property
    def text(self) -> str:
        """Return all words as space-separated text."""
        return " ".join(w.text for w in self.words)

    @property
    def word_count(self) -> int:
        return len(self.words)


class VoynichCorpus:
    """
    Main class for loading and accessing Voynich Manuscript data.
    """

    def __init__(self):
        self.words: List[VoynichWord] = []
        self.folios: Dict[str, VoynichFolio] = {}
        self.metadata: Dict = {}

    def load_interlinear(self, filepath: str) -> None:
        """Load the interlinear format transcription (tab-separated with metadata)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            # Track unique transcriptions per position
            seen_positions = set()

            for row in reader:
                # Skip if we've seen this exact position from this transcriber
                pos_key = (row['folio'], row['placement'], row['line_number'],
                          row.get('line_initial', ''), row['transcriber'])

                # Use only one transcriber per position (prefer 'H' = Herbal/main)
                if row['transcriber'] != 'H':
                    continue

                # Handle line numbers that may have letters (e.g., '11a')
                line_num_str = row.get('line_number', '0')
                try:
                    line_num = int(line_num_str)
                except ValueError:
                    # Extract numeric part if mixed
                    line_num = int(''.join(c for c in line_num_str if c.isdigit()) or '0')

                word = VoynichWord(
                    text=row['word'].strip('"'),
                    folio=row['folio'],
                    section=row.get('section', ''),
                    quire=row.get('quire', ''),
                    panel=row.get('panel', ''),
                    language=row.get('language', ''),
                    hand=row.get('hand', ''),
                    placement=row.get('placement', ''),
                    line_number=line_num,
                    transcriber=row.get('transcriber', ''),
                    line_initial=row.get('line_initial', '') == '1',
                    line_final=row.get('line_final', '') == '1',
                    par_initial=bool(row.get('par_initial')),
                    par_final=bool(row.get('par_final'))
                )

                self.words.append(word)

                # Add to folio
                if word.folio not in self.folios:
                    self.folios[word.folio] = VoynichFolio(
                        folio_id=word.folio,
                        section=word.section,
                        quire=word.quire,
                        language=word.language,
                        hand=word.hand
                    )
                self.folios[word.folio].words.append(word)

    def load_plain_text(self, filepath: str) -> None:
        """Load plain text transcription (one line per folio or continuous)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Split into words
        words = text.split()
        for i, word_text in enumerate(words):
            word = VoynichWord(
                text=word_text,
                folio="unknown",
                line_number=i
            )
            self.words.append(word)

    def load_annotated_wds(self, filepath: str) -> None:
        """Load the .wds format from deciphervoynich repo."""
        with open(filepath, 'r', encoding='utf-8') as f:
            current_folio = None
            line_num = 0

            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse folio header like <f1r P1 1 H>
                if line.startswith('<') and '>' in line:
                    header_match = re.match(r'<(\w+)\s+(\w+)\s+(\d+)\s+(\w+)>', line)
                    if header_match:
                        current_folio = header_match.group(1)
                        placement = header_match.group(2)
                        line_num = int(header_match.group(3))
                        transcriber = header_match.group(4)

                        if current_folio not in self.folios:
                            self.folios[current_folio] = VoynichFolio(folio_id=current_folio)

                    # Get words after the header
                    words_part = line.split('>')[-1].strip()
                    if words_part:
                        for word_text in words_part.split():
                            word = VoynichWord(
                                text=word_text,
                                folio=current_folio or "unknown",
                                placement=placement if header_match else "",
                                line_number=line_num,
                                transcriber=transcriber if header_match else ""
                            )
                            self.words.append(word)
                            if current_folio:
                                self.folios[current_folio].words.append(word)

    # Filtering methods
    def get_by_language(self, lang: str) -> List[VoynichWord]:
        """Get words from Currier language A or B."""
        return [w for w in self.words if w.language == lang]

    def get_by_hand(self, hand: str) -> List[VoynichWord]:
        """Get words by scribal hand (1-5)."""
        return [w for w in self.words if w.hand == hand]

    def get_by_section(self, section: str) -> List[VoynichWord]:
        """Get words by section type."""
        return [w for w in self.words if w.section == section]

    def get_by_folio(self, folio: str) -> List[VoynichWord]:
        """Get words from a specific folio."""
        return self.folios.get(folio, VoynichFolio(folio)).words

    @property
    def all_text(self) -> str:
        """Return all words as continuous text."""
        return " ".join(w.text for w in self.words)

    @property
    def all_words(self) -> List[str]:
        """Return list of all word strings."""
        return [w.text for w in self.words]

    @property
    def unique_words(self) -> set:
        """Return set of unique word types."""
        return set(self.all_words)

    @property
    def all_characters(self) -> str:
        """Return all characters (no spaces)."""
        return "".join(w.text for w in self.words)

    def summary(self) -> Dict:
        """Return summary statistics."""
        return {
            'total_words': len(self.words),
            'unique_words': len(self.unique_words),
            'total_characters': len(self.all_characters),
            'unique_characters': len(set(self.all_characters)),
            'num_folios': len(self.folios),
            'languages': list(set(w.language for w in self.words if w.language)),
            'hands': list(set(w.hand for w in self.words if w.hand)),
            'sections': list(set(w.section for w in self.words if w.section))
        }


def load_corpus(data_dir: str = "data/transcriptions") -> VoynichCorpus:
    """Convenience function to load the corpus from default location."""
    corpus = VoynichCorpus()

    data_path = Path(data_dir)

    # Try interlinear format first (richest metadata)
    interlinear = data_path / "interlinear_full_words.txt"
    if interlinear.exists():
        corpus.load_interlinear(str(interlinear))
        return corpus

    # Try annotated wds format
    wds_file = data_path / "voy.ann.wds"
    if wds_file.exists():
        corpus.load_annotated_wds(str(wds_file))
        return corpus

    # Fall back to plain text
    plain = data_path / "voynich_full_eva.txt"
    if plain.exists():
        corpus.load_plain_text(str(plain))

    return corpus


if __name__ == "__main__":
    # Test loading
    corpus = load_corpus()
    print("Corpus Summary:")
    for key, value in corpus.summary().items():
        print(f"  {key}: {value}")
