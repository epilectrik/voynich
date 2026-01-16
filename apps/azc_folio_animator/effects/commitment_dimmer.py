"""
Commitment Dimmer - Zone opacity based on categorical depth.

Per AZC-ACT monotonicity invariant:
"Survivor options never increase from earlier to later positions"

Deeper zones (R, S) are visually more committed (slightly different opacity).
No animation - static categorical differentiation.
"""
from typing import Dict, List
from PyQt5.QtCore import QObject


class CommitmentDimmer(QObject):
    """
    Provides opacity values for zones based on commitment depth.

    Deeper zones = more visually committed (subtle difference).
    No animation - values are static per zone.
    """

    # Static opacity multipliers per zone (categorical, not animated)
    ZONE_OPACITY = {
        'C': 1.0,    # Entry - full visibility
        'P': 0.95,   # Permissive - slight commitment
        'R': 0.85,   # Restricting - moderate commitment
        'S': 0.75    # Boundary - high commitment
    }

    def __init__(self, phase_order: List[str], parent=None):
        super().__init__(parent)
        self.phase_order = phase_order

    def get_alpha_multiplier(self, phase: str) -> float:
        """Get alpha multiplier for a zone (categorical, not animated)."""
        return self.ZONE_OPACITY.get(phase, 1.0)

    def reset(self):
        """No-op for compatibility. Values are static."""
        pass
