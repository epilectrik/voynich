"""
AZC Folio Model - Activatable folio objects for token-centric exploration.

Each AZC folio becomes an object that can be "activated" by a token query.
The registry holds all 20 folios and provides activation queries.

ARCHITECTURE (per C441, C472, C473):
- Activation is TOKEN-based (C441: "478 A-types appear in exactly 1 AZC folio")
- C472: MIDDLE is primary CARRIER of folio specificity (explains WHY tokens cluster)
- C473: PREFIX + MIDDLE + SUFFIX = compatibility signature (full token)
- MIDDLE matching provides "related tokens" view, not activation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import FolioLoader, FolioData, TokenData
from apps.script_explorer.parsing.currier_a import parse_currier_a_token


def _extract_middle(token_text: str) -> Optional[str]:
    """Extract MIDDLE from token using Currier A parser."""
    result = parse_currier_a_token(token_text)
    return result.middle


@dataclass
class AZCFolioModel:
    """
    Single AZC folio as an activatable object.

    Activation is TOKEN-based per C441: "478 A-types appear in exactly 1 AZC folio".
    MIDDLE vocabulary kept for "related tokens" view per C472.
    """
    folio_id: str
    family: str  # 'zodiac' or 'ac'
    token_vocabulary: Set[str] = field(default_factory=set)   # Full tokens (PRIMARY for activation)
    middle_vocabulary: Set[str] = field(default_factory=set)  # MIDDLEs (for related tokens view)
    token_positions: Dict[str, List[TokenData]] = field(default_factory=dict)
    middle_to_tokens: Dict[str, List[str]] = field(default_factory=dict)  # MIDDLE -> full tokens
    folio_data: Optional[FolioData] = None  # Keep reference for diagram building

    @classmethod
    def from_folio_data(cls, folio_data: FolioData) -> 'AZCFolioModel':
        """Create model from FolioData with token and MIDDLE vocabularies."""
        middle_vocab: Set[str] = set()
        token_vocab: Set[str] = set()
        positions: Dict[str, List[TokenData]] = {}
        middle_to_tokens: Dict[str, List[str]] = {}

        for token in folio_data.tokens:
            token_text = token.text
            token_vocab.add(token_text)

            # Track positions by full token
            if token_text not in positions:
                positions[token_text] = []
            positions[token_text].append(token)

            # Extract and track MIDDLE
            middle = _extract_middle(token_text)
            if middle:
                middle_vocab.add(middle)
                if middle not in middle_to_tokens:
                    middle_to_tokens[middle] = []
                if token_text not in middle_to_tokens[middle]:
                    middle_to_tokens[middle].append(token_text)

        return cls(
            folio_id=folio_data.folio_id,
            family=folio_data.family,
            middle_vocabulary=middle_vocab,
            token_vocabulary=token_vocab,
            token_positions=positions,
            middle_to_tokens=middle_to_tokens,
            folio_data=folio_data
        )

    def is_activated(self, token_text: str) -> bool:
        """
        Check if this folio is activated by token.

        Per C441: Activation is TOKEN-based ("478 A-types appear in exactly 1 AZC folio").
        Full token match determines folio membership.
        """
        return token_text in self.token_vocabulary

    def has_related_middle(self, token_text: str) -> bool:
        """
        Check if this folio has tokens with the same MIDDLE (related tokens view).

        Per C472: MIDDLE is primary carrier of folio specificity.
        This is for "related tokens" exploration, not activation.
        """
        middle = _extract_middle(token_text)
        if middle:
            return middle in self.middle_vocabulary
        return False

    def get_positions(self, token_text: str) -> List[TokenData]:
        """Get all positions where token appears in this folio."""
        return self.token_positions.get(token_text, [])

    def get_tokens_by_middle(self, token_text: str) -> List[str]:
        """Get all tokens in this folio that share the same MIDDLE."""
        middle = _extract_middle(token_text)
        if middle:
            return self.middle_to_tokens.get(middle, [])
        return [token_text] if token_text in self.token_vocabulary else []

    def get_positions_by_middle(self, token_text: str) -> List[TokenData]:
        """Get positions of all tokens sharing the same MIDDLE."""
        tokens = self.get_tokens_by_middle(token_text)
        positions = []
        for t in tokens:
            positions.extend(self.token_positions.get(t, []))
        return positions

    def get_token_count(self, token_text: str) -> int:
        """Get count of occurrences of this token."""
        return len(self.token_positions.get(token_text, []))


class AZCFolioRegistry:
    """
    Registry of all 20 AZC folios for activation queries.

    Provides efficient lookup of which folios contain a given token,
    enabling the token-centric exploration paradigm.
    """

    def __init__(self, folio_loader: FolioLoader):
        self.folios: Dict[str, AZCFolioModel] = {}
        self._folio_count_cache: Dict[str, int] = {}
        self._load_all(folio_loader)

    def _load_all(self, loader: FolioLoader):
        """Load all AZC folios into the registry."""
        for folio_id in loader.get_azc_folio_ids():
            folio_data = loader.get_folio(folio_id)
            if folio_data:
                self.folios[folio_id] = AZCFolioModel.from_folio_data(folio_data)

    def get_activated_folios(self, token_text: str) -> List[AZCFolioModel]:
        """Return all folios containing this token, sorted by folio ID."""
        activated = [f for f in self.folios.values() if f.is_activated(token_text)]
        return sorted(activated, key=lambda f: self._folio_sort_key(f.folio_id))

    def count_folios_for_token(self, token_text: str) -> int:
        """Count how many folios contain this token (cached)."""
        if token_text not in self._folio_count_cache:
            count = sum(1 for f in self.folios.values() if f.is_activated(token_text))
            self._folio_count_cache[token_text] = count
        return self._folio_count_cache[token_text]

    def get_all_folio_ids(self) -> List[str]:
        """Get all folio IDs in the registry."""
        return sorted(self.folios.keys(), key=self._folio_sort_key)

    def get_folio(self, folio_id: str) -> Optional[AZCFolioModel]:
        """Get a specific folio by ID."""
        return self.folios.get(folio_id)

    def _folio_sort_key(self, folio_id: str) -> tuple:
        """Sort key for folio IDs (numeric then suffix)."""
        import re
        match = re.match(r'(\d+)([rv]\d*)', folio_id)
        if match:
            return (int(match.group(1)), match.group(2))
        return (999, folio_id)

    @property
    def folio_count(self) -> int:
        """Total number of folios in registry."""
        return len(self.folios)

    @property
    def zodiac_count(self) -> int:
        """Number of Zodiac folios."""
        return sum(1 for f in self.folios.values() if f.family == 'zodiac')

    @property
    def ac_count(self) -> int:
        """Number of A/C folios."""
        return sum(1 for f in self.folios.values() if f.family == 'ac')
