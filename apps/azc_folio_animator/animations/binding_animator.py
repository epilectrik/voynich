"""
Binding Animator - Instant Token Placement.

Per AZC-ACT transformations.content_invariants:
- "No movement of tokens"
- "No selection"
- "No branching"

Tokens appear INSTANTLY at their zone positions.
No physics simulation (spring, damping, velocity).
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from PyQt5.QtCore import QPointF, QObject, pyqtSignal

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import TokenData
from apps.azc_folio_animator.core.azc_engine import AZCEngine, ZoneCategory


@dataclass
class PlacementState:
    """State of a token after instant placement."""
    token: TokenData
    position: QPointF
    zone: str                    # C, P, R, S
    category: ZoneCategory       # INTERIOR or BOUNDARY
    is_placed: bool = True


class BindingAnimator(QObject):
    """
    Instant placement coordinator.

    Per contract: tokens don't "travel" - they appear at zones.
    This class tracks placements for UI rendering.

    Signals:
        token_placed(TokenData, QPointF, str): Token placed at position in zone
        bundle_complete(int): Bundle finished with N tokens placed
    """

    token_placed = pyqtSignal(object, QPointF, str)
    bundle_complete = pyqtSignal(int)

    def __init__(self, engine: AZCEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        # Placed tokens by zone
        self._placements: Dict[str, List[PlacementState]] = {
            'C': [], 'P': [], 'R': [], 'S': []
        }
        self._all_placements: List[PlacementState] = []

    def place_token(self, token: TokenData, position: QPointF) -> PlacementState:
        """
        Place a token instantly at a position.

        No animation - token appears immediately.
        """
        zone = self.engine.get_zone_for_position(token.placement)
        category = self.engine.get_zone_category(token.placement)

        state = PlacementState(
            token=token,
            position=position,
            zone=zone,
            category=category,
            is_placed=True
        )

        self._placements[zone].append(state)
        self._all_placements.append(state)

        self.token_placed.emit(token, position, zone)
        return state

    def place_bundle(self, tokens: List[TokenData],
                     positions: List[QPointF]) -> List[PlacementState]:
        """
        Place an entire bundle of tokens instantly.

        All tokens appear at once - no animation.
        """
        self.clear()

        states = []
        for token, pos in zip(tokens, positions):
            state = self.place_token(token, pos)
            states.append(state)

        self.bundle_complete.emit(len(states))
        return states

    def get_placements_by_zone(self, zone: str) -> List[PlacementState]:
        """Get all tokens placed in a zone."""
        return self._placements.get(zone, [])

    def get_all_placements(self) -> List[PlacementState]:
        """Get all placed tokens."""
        return self._all_placements

    def get_zone_counts(self) -> Dict[str, int]:
        """Get count of tokens in each zone."""
        return {zone: len(tokens) for zone, tokens in self._placements.items()}

    def get_interior_count(self) -> int:
        """Get count of tokens in INTERIOR zones (C, P, R)."""
        return (len(self._placements['C']) +
                len(self._placements['P']) +
                len(self._placements['R']))

    def get_boundary_count(self) -> int:
        """Get count of tokens in BOUNDARY zone (S)."""
        return len(self._placements['S'])

    def clear(self):
        """Clear all placements."""
        self._placements = {'C': [], 'P': [], 'R': [], 'S': []}
        self._all_placements.clear()
