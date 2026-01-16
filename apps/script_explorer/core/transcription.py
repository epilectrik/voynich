"""
Transcription Loader - Parses EVA transcription files.

Loads Voynich manuscript transcriptions in EVA (Extensible Voynich Alphabet) format
and provides access to text by folio and line.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TranscriptionLine:
    """A single line of transcription."""
    folio: str
    line_number: int
    text: str
    placements: Optional[List[str]] = None  # Per-token placement codes (C306)

    @property
    def full_id(self) -> str:
        return f"{self.folio}.{self.line_number}"

    @property
    def tokens(self) -> List[str]:
        """Get tokens from this line."""
        tokens = re.split(r'[.\s]+', self.text)
        return [t for t in tokens if t and t not in '=-']

    def get_placement(self, token_idx: int) -> str:
        """Get placement code for token at index. Returns 'UNKNOWN' if not available."""
        if self.placements and 0 <= token_idx < len(self.placements):
            return self.placements[token_idx] or 'UNKNOWN'
        return 'UNKNOWN'


@dataclass
class FolioTranscription:
    """Complete transcription for a single folio."""
    folio_id: str
    lines: List[TranscriptionLine]

    @property
    def full_text(self) -> str:
        """Get all text concatenated."""
        return ' '.join(line.text for line in self.lines)

    @property
    def tokens(self) -> List[str]:
        """Get all tokens (words) from folio."""
        text = self.full_text
        tokens = re.split(r'[.\s]+', text)
        return [t for t in tokens if t and t not in '=-']

    @property
    def token_count(self) -> int:
        """Number of tokens in this folio."""
        return len(self.tokens)

    @property
    def line_count(self) -> int:
        """Number of lines in this folio."""
        return len(self.lines)

    def get_line(self, line_num: int) -> Optional[TranscriptionLine]:
        """Get a specific line by number."""
        for line in self.lines:
            if line.line_number == line_num:
                return line
        return None


class TranscriptionLoader:
    """
    Loads and indexes EVA transcriptions.

    Format: <folio.line>text content-
    Example: <1r.1>fa19s.9,hae.ay.Akam.2oe.!oy9...
    """

    def __init__(self):
        self.folios: Dict[str, FolioTranscription] = {}
        self._line_pattern = re.compile(r'<(\d+[rv]\d*?)\.(\d+)>(.+)')

    def load_file(self, filepath: str) -> int:
        """
        Load transcription file.

        Args:
            filepath: Path to EVA transcription file

        Returns:
            Number of folios loaded
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Transcription file not found: {filepath}")

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        current_folio = None
        folio_lines: Dict[str, List[TranscriptionLine]] = {}

        for match in self._line_pattern.finditer(content):
            folio_id = match.group(1)
            line_num = int(match.group(2))
            text = match.group(3).strip()
            text = text.rstrip('-=')

            if folio_id not in folio_lines:
                folio_lines[folio_id] = []

            folio_lines[folio_id].append(TranscriptionLine(
                folio=folio_id,
                line_number=line_num,
                text=text
            ))

        for folio_id, lines in folio_lines.items():
            lines.sort(key=lambda x: x.line_number)
            self.folios[folio_id] = FolioTranscription(
                folio_id=folio_id,
                lines=lines
            )

        return len(self.folios)

    def load_interlinear(self, filepath: str) -> int:
        """
        Load interlinear transcription file (TSV format with EVA words).

        This format has proper EVA tokens like 'shey', 'daiin', 'qokaiin'
        which match the constraint model's forbidden pairs.

        Also extracts placement codes (column 10) per C306 - topological
        placement classes for AZC tokens.

        Args:
            filepath: Path to interlinear transcription file

        Returns:
            Number of folios loaded
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Interlinear file not found: {filepath}")

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        if not lines:
            return 0

        # Store (word, placement) pairs per folio/line
        folio_lines: Dict[str, Dict[int, List[Tuple[str, str]]]] = {}

        for line in lines[1:]:  # Skip header
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            word = parts[0].strip('"')
            folio = parts[2].strip('"').lower().lstrip('f')
            # Column 10 is placement (C306 topological class)
            placement = parts[10].strip('"') if len(parts) > 10 else ''
            transcriber = parts[12].strip('"') if len(parts) > 12 else 'H'
            try:
                line_num = int(parts[11].strip('"'))
            except ValueError:
                continue

            if transcriber != 'H':
                continue

            if not word or word in ('NA', '*', '-'):
                continue

            if folio not in folio_lines:
                folio_lines[folio] = {}
            if line_num not in folio_lines[folio]:
                folio_lines[folio][line_num] = []

            folio_lines[folio][line_num].append((word, placement))

        for folio_id, line_dict in folio_lines.items():
            lines_list = []
            for line_num in sorted(line_dict.keys()):
                word_placements = line_dict[line_num]
                words = [wp[0] for wp in word_placements]
                placements = [wp[1] for wp in word_placements]
                text = ' '.join(words)
                lines_list.append(TranscriptionLine(
                    folio=folio_id,
                    line_number=line_num,
                    text=text,
                    placements=placements
                ))

            self.folios[folio_id] = FolioTranscription(
                folio_id=folio_id,
                lines=lines_list
            )

        return len(self.folios)

    def get_folio(self, folio_id: str) -> Optional[FolioTranscription]:
        """Get transcription for a specific folio."""
        normalized = folio_id.lower().lstrip('f')
        return self.folios.get(normalized)

    def get_folio_ids(self) -> List[str]:
        """Get list of all folio IDs."""
        return sorted(self.folios.keys(), key=self._folio_sort_key)

    def _folio_sort_key(self, folio_id: str) -> Tuple[int, str]:
        """Sort key for folio IDs (numeric, then r/v)."""
        match = re.match(r'(\d+)([rv]\d*)', folio_id)
        if match:
            return (int(match.group(1)), match.group(2))
        return (0, folio_id)

    def search(self, pattern: str) -> List[Tuple[str, TranscriptionLine]]:
        """
        Search for pattern across all folios.

        Args:
            pattern: Regex pattern to search for

        Returns:
            List of (folio_id, line) tuples containing matches
        """
        regex = re.compile(pattern, re.IGNORECASE)
        results = []

        for folio_id, folio in self.folios.items():
            for line in folio.lines:
                if regex.search(line.text):
                    results.append((folio_id, line))

        return results

    @property
    def total_folios(self) -> int:
        """Total number of folios loaded."""
        return len(self.folios)

    @property
    def total_tokens(self) -> int:
        """Total number of tokens across all folios."""
        return sum(f.token_count for f in self.folios.values())
