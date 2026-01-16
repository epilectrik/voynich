"""
AZC Engine - Categorical Zone Logic.

Provides categorical legality zone information per AZC-ACT contract.
NO numeric physics - positions determine categorical state only.

Key contracts respected:
- C469: Categorical resolution principle (no parametric encoding)
- C442: Compatibility filtering (disallowed combinations never occur)
- C443: Positional escape gradient (categorical, not numeric)
- FAMILY_AGNOSTIC_MECHANISM: Same zones, different scaffolds
"""
import json
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


class ZoneCategory(Enum):
    """Categorical zone types per AZC-ACT."""
    INTERIOR = "INTERIOR"
    BOUNDARY = "BOUNDARY"


class EscapeClass(Enum):
    """Categorical escape classes per AZC-ACT monotonicity invariant."""
    HIGH = "HIGH"           # P zone - elevated escape permission
    MODERATE = "MODERATE"   # C zone - standard escape permission
    RESTRICTING = "RESTRICTING"  # R zone - decreasing through progression
    ZERO = "ZERO"           # S zone - no escape permitted


@dataclass
class ZoneInfo:
    """Complete zone information for display and logic."""
    zone: str               # C, P, R, S
    category: ZoneCategory  # INTERIOR or BOUNDARY
    escape_class: EscapeClass
    intervention: bool      # Whether intervention is permitted
    display: str            # Display label


@dataclass
class PipelineOutput:
    """What B receives from AZC (per AZC-B-ACT)."""
    legality_class: ZoneCategory
    intervention_permitted: bool
    zone_label: str


class AZCEngine:
    """
    AZC Engine - Categorical Zone Logic.

    Provides:
    - Zone category lookup (INTERIOR/BOUNDARY)
    - Escape class lookup (HIGH/MODERATE/RESTRICTING/ZERO)
    - Scaffold-aware position mapping
    - Pipeline output (what B receives)

    NO physics values (spring, damping, elasticity).
    """

    def __init__(self, family: str = 'zodiac'):
        self.family = family
        self._data_dir = Path(__file__).parent.parent / "data"
        self._load_data()

    def _load_data(self):
        """Load position and zone category data."""
        # Load positions (scaffold-specific)
        positions_path = self._data_dir / "positions.json"
        with open(positions_path, 'r') as f:
            all_positions = json.load(f)

        self._position_data = all_positions.get(self.family, all_positions['zodiac'])
        self.positions: List[str] = self._position_data.get('positions', [])
        self.phases: Dict[str, List[str]] = self._position_data.get('phases', {})
        self.phase_order: List[str] = self._position_data.get('phase_order', [])
        self.ring_radii: Dict[str, float] = self._position_data.get('ring_radii', {})
        self.colors: Dict[str, str] = self._position_data.get('colors', {})
        self.phase_display: Dict[str, str] = self._position_data.get('phase_display', {})
        self.scaffold = self._position_data.get('scaffold', {})

        # Load zone categories (family-agnostic)
        zones_path = self._data_dir / "zone_categories.json"
        with open(zones_path, 'r') as f:
            self._zone_data = json.load(f)

        self._zones = self._zone_data.get('zones', {})
        self._escape_classes = self._zone_data.get('escape_classes', {})
        self._section_to_family = all_positions.get('section_to_family', {})

    def set_family(self, family: str):
        """Switch to different family scaffold."""
        if family != self.family:
            self.family = family
            self._load_data()

    def is_ordered_scaffold(self) -> bool:
        """Check if current family uses ordered subscripts."""
        return self.scaffold.get('ordered', False)

    def get_zone_for_position(self, position: str) -> str:
        """
        Get abstract zone (C/P/R/S) for a position.

        Maps scaffold-specific positions (R1, R2, R3) to abstract zones (R).
        """
        for zone, positions in self.phases.items():
            if position in positions:
                return zone

        # Fallback by first character
        if position.startswith('C'):
            return 'C'
        elif position.startswith('P'):
            return 'P'
        elif position.startswith('R'):
            return 'R'
        elif position.startswith('S'):
            return 'S'
        return 'C'

    def get_zone_info(self, position: str) -> ZoneInfo:
        """Get complete zone information for a position."""
        zone = self.get_zone_for_position(position)
        zone_data = self._zones.get(zone, self._zones.get('C', {}))

        return ZoneInfo(
            zone=zone,
            category=ZoneCategory(zone_data.get('category', 'INTERIOR')),
            escape_class=EscapeClass(zone_data.get('escape_class', 'MODERATE')),
            intervention=zone_data.get('intervention', True),
            display=zone_data.get('display', zone)
        )

    def get_zone_category(self, position: str) -> ZoneCategory:
        """Get zone category (INTERIOR or BOUNDARY) for a position."""
        return self.get_zone_info(position).category

    def get_escape_class(self, position: str) -> EscapeClass:
        """Get escape class (HIGH/MODERATE/RESTRICTING/ZERO) for a position."""
        return self.get_zone_info(position).escape_class

    def is_intervention_permitted(self, position: str) -> bool:
        """Check if intervention is permitted at this position."""
        return self.get_zone_info(position).intervention

    def get_pipeline_output(self, position: str) -> PipelineOutput:
        """
        Get what B receives from this AZC position.

        Per AZC-B-ACT: B sees only legality class, not A content.
        """
        info = self.get_zone_info(position)
        return PipelineOutput(
            legality_class=info.category,
            intervention_permitted=info.intervention,
            zone_label=info.display
        )

    def get_radius(self, position: str) -> float:
        """Get normalized radius (0-1) for ring layout."""
        return self.ring_radii.get(position, 0.5)

    def get_color(self, position: str) -> str:
        """Get color for position's zone (hex string)."""
        zone = self.get_zone_for_position(position)
        return self.colors.get(zone, "#00aacc")

    def get_phase_display(self, zone: str) -> str:
        """Get display name for zone."""
        return self.phase_display.get(zone, zone)

    def get_phase_index(self, position: str) -> int:
        """Get depth index of position (0 = entry, higher = deeper)."""
        zone = self.get_zone_for_position(position)
        try:
            return self.phase_order.index(zone)
        except ValueError:
            return 0

    def get_monotonicity_rank(self, position: str) -> int:
        """
        Get monotonicity rank (1-4) for escape class.

        Per AZC-ACT monotonicity invariant: survivor options never increase.
        Lower rank = more escape permission.
        """
        escape_class = self.get_escape_class(position)
        ranks = {
            EscapeClass.HIGH: 1,
            EscapeClass.MODERATE: 2,
            EscapeClass.RESTRICTING: 3,
            EscapeClass.ZERO: 4
        }
        return ranks.get(escape_class, 2)

    def check_compatibility(self, token: str, position: str) -> bool:
        """
        Check if a token is compatible at a position.

        Per C442: Incompatible combinations simply don't occur.
        Returns True if compatible (token can appear at position).

        Note: Actual compatibility logic depends on MIDDLE analysis.
        This is a placeholder for token-position compatibility.
        """
        # Check if position exists in current scaffold
        if position not in self.positions and position not in self.phase_order:
            # Map to abstract zone
            zone = self.get_zone_for_position(position)
            if zone not in self.phase_order:
                return False

        return True

    def get_subscripts_for_zone(self, zone: str) -> Optional[List[str]]:
        """
        Get ordered subscripts for a zone (Zodiac only).

        Returns None for A/C family (no ordered subscripts).
        """
        if not self.is_ordered_scaffold():
            return None

        if zone == 'R':
            return self.scaffold.get('R_subscripts')
        elif zone == 'S':
            return self.scaffold.get('S_subscripts')
        return None
