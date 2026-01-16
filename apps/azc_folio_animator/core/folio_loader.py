"""
FolioLoader - Loads AZC folio data from interlinear corpus.

Wraps TranscriptionLoader and adds:
- Family detection (Zodiac vs A/C)
- Per-token placement extraction
- HT metrics for ambient weather
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Add parent to path for script_explorer imports
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from apps.script_explorer.core.transcription import TranscriptionLoader, FolioTranscription


@dataclass
class TokenData:
    """A single token with its placement and metadata."""
    text: str
    placement: str
    line_num: int
    position_in_line: int

    # Computed during placement
    phase: str = ""              # C, P, R, S
    is_control_operator: bool = False  # 1-token entries (C484)


@dataclass
class FolioData:
    """Complete data for a single folio."""
    folio_id: str
    family: str  # 'zodiac' or 'ac'
    section: str  # Z, A, C, H, S
    tokens: List[TokenData] = field(default_factory=list)
    lines: List[List[TokenData]] = field(default_factory=list)

    # HT metrics for ambient weather
    ht_density: float = 0.5
    ht_complexity: float = 0.5

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def line_count(self) -> int:
        return len(self.lines)

    def get_placement_distribution(self) -> Dict[str, int]:
        """Get count of tokens per placement."""
        dist = {}
        for token in self.tokens:
            p = token.placement
            dist[p] = dist.get(p, 0) + 1
        return dist

    def get_registry_entries(self) -> List[TokenData]:
        """Get tokens that are registry entries (not control operators)."""
        return [t for t in self.tokens if not t.is_control_operator]

    def get_control_operators(self) -> List[TokenData]:
        """Get tokens that are control operators (1-token entries per C484)."""
        return [t for t in self.tokens if t.is_control_operator]


class FolioLoader:
    """
    Loads folio data for AZC visualization.

    Combines:
    - TranscriptionLoader for corpus text
    - azc_folio_features.json for section/family metadata
    - Position data for placement mapping
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self._project_root = Path(__file__).parent.parent.parent.parent
        self._data_dir = data_dir or self._project_root / "data" / "transcriptions"
        self._results_dir = self._project_root / "results"

        self._loader: Optional[TranscriptionLoader] = None
        self._folio_features: Dict = {}
        self._position_data: Dict = {}
        self._loaded = False

    def load(self) -> bool:
        """Load all required data."""
        if self._loaded:
            return True

        # Load interlinear corpus
        self._loader = TranscriptionLoader()
        interlinear_path = self._data_dir / "interlinear_full_words.txt"
        if not interlinear_path.exists():
            raise FileNotFoundError(f"Interlinear corpus not found: {interlinear_path}")

        count = self._loader.load_interlinear(str(interlinear_path))
        if count == 0:
            raise ValueError("No folios loaded from interlinear corpus")

        # Load folio features for section/family info
        features_path = self._results_dir / "azc_folio_features.json"
        if features_path.exists():
            with open(features_path, 'r') as f:
                self._folio_features = json.load(f)

        # Load position data
        positions_path = Path(__file__).parent.parent / "data" / "positions.json"
        if positions_path.exists():
            with open(positions_path, 'r') as f:
                self._position_data = json.load(f)

        self._loaded = True
        return True

    def get_azc_folio_ids(self) -> List[str]:
        """Get list of AZC folios (sections A, Z, and C)."""
        if not self._loaded:
            self.load()

        azc_ids = []
        folios_data = self._folio_features.get('folios', {})

        for folio_id, data in folios_data.items():
            section = data.get('section', '')
            if section in ('A', 'Z', 'C'):
                azc_ids.append(folio_id)

        # Sort by folio number
        return sorted(azc_ids, key=self._folio_sort_key)

    def get_all_folio_ids(self) -> List[str]:
        """Get all loaded folio IDs."""
        if not self._loaded:
            self.load()
        return self._loader.get_folio_ids()

    def get_folio(self, folio_id: str) -> Optional[FolioData]:
        """Load complete data for a folio."""
        if not self._loaded:
            self.load()

        # Normalize folio ID
        normalized = folio_id.lower().lstrip('f')

        # Get transcription
        transcription = self._loader.get_folio(normalized)
        if not transcription:
            return None

        # Get section and family
        section, family = self._get_section_family(normalized)

        # Build token data
        tokens = []
        lines = []

        # C233: A = LINE_ATOMIC
        # The manuscript line is the atomic Currier A record.
        # Long lines are large constraint bundles by design - do NOT subdivide.
        # DA tokens and prefix changes are internal articulation, not boundaries.

        for line in transcription.lines:
            line_tokens = []

            # C484: Control operators are 1-token entries
            # They are meta-structural, not registry content
            is_single_token_line = len(line.tokens) == 1

            for idx, token_text in enumerate(line.tokens):
                placement = line.get_placement(idx)
                if placement in ('', 'UNKNOWN', 'NA'):
                    placement = 'UNK'

                token = TokenData(
                    text=token_text,
                    placement=placement,
                    line_num=line.line_number,
                    position_in_line=idx,
                    is_control_operator=is_single_token_line
                )

                # Set phase based on placement
                token.phase = self._get_phase(placement, family)

                tokens.append(token)
                line_tokens.append(token)

            # Each manuscript line = one atomic record (C233)
            if line_tokens:
                lines.append(line_tokens)

        # Get HT metrics
        ht_density, ht_complexity = self._get_ht_metrics(normalized)

        return FolioData(
            folio_id=normalized,
            family=family,
            section=section,
            tokens=tokens,
            lines=lines,
            ht_density=ht_density,
            ht_complexity=ht_complexity
        )

    def _get_section_family(self, folio_id: str) -> tuple:
        """Get section and family for a folio."""
        section = 'Z'  # Default to zodiac

        # Check folio features
        folios_data = self._folio_features.get('folios', {})
        if folio_id in folios_data:
            section = folios_data[folio_id].get('section', 'Z')

        # Map section to family
        section_map = self._position_data.get('section_to_family', {})
        family = section_map.get(section, 'zodiac')

        return section, family

    def _get_phase(self, placement: str, family: str) -> str:
        """
        Get categorical phase (C/P/R/S) for a placement.

        Per AZC-ACT: Only 4 zone types exist (C, P, R, S).
        Scaffold-specific positions (R1, R2, R3) map to abstract zones.
        """
        family_data = self._position_data.get(family, {})
        phases = family_data.get('phases', {})

        for phase, placements in phases.items():
            if placement in placements:
                return phase

        # Default mapping by first character (contract-compliant zones only)
        if placement.startswith('C'):
            return 'C'
        elif placement.startswith('P'):
            return 'P'
        elif placement.startswith('R'):
            return 'R'
        elif placement.startswith('S'):
            return 'S'

        return 'C'  # Default to entry zone

    def _get_ht_metrics(self, folio_id: str) -> tuple:
        """Get HT density and complexity for ambient weather effect."""
        folios_data = self._folio_features.get('folios', {})

        if folio_id not in folios_data:
            return 0.5, 0.5

        data = folios_data[folio_id]

        # Derive density from placement entropy (higher entropy = more complex)
        entropy = data.get('placement_entropy', 0.5)
        density = min(1.0, entropy / 2.0)  # Normalize

        # Derive complexity from TTR (type-token ratio)
        ttr = data.get('ttr', 0.3)
        complexity = min(1.0, ttr * 2.0)  # Higher TTR = more complex

        return density, complexity

    def _folio_sort_key(self, folio_id: str) -> tuple:
        """Sort key for folio IDs."""
        import re
        match = re.match(r'(\d+)([rv]\d*)', folio_id)
        if match:
            return (int(match.group(1)), match.group(2))
        return (999, folio_id)
