"""
Token System Classifier - Classifies tokens by their formal system.

Based on constraints:
- C240: Operational prefixes (ch, sh, ok, ot, da, qo, ol, ct) - 63%
- C347: Human Track prefixes (yk-, op-, yt-, sa-, etc.) - 11%
- C350: HT-B hybrids (HT prefix + B suffix) - 12.5%
- C407, C422: Infrastructure tokens (ar, al, ol, daiin) - ~5%
- C291-C295: Optional articulators - ~20% of A tokens

The ~37% of tokens outside C240 are fully characterized:
- Total characterized: ~100% (only ~0.6% true residue per C351-352)
"""
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.script_explorer.parsing.currier_a import CurrierAParseResult


class TokenSystem(Enum):
    """Primary token system classification."""
    OPERATIONAL = "OPERATIONAL"           # 63% - C240 prefixes
    HUMAN_TRACK = "HUMAN_TRACK"           # 11% - C347 disjoint prefix vocab
    HT_B_HYBRID = "HT_B_HYBRID"           # 12.5% - C350 HT prefix + B suffix
    INFRASTRUCTURE = "INFRASTRUCTURE"     # ~5% - C407, C422 punctuation/glue
    ARTICULATOR = "ARTICULATOR"           # Part of ~20% - C291-295 refinement
    UNCLASSIFIED = "UNCLASSIFIED"         # <1% true residue


# System colors for UI
SYSTEM_COLORS = {
    TokenSystem.OPERATIONAL: "#00cc88",     # Green - main system
    TokenSystem.HUMAN_TRACK: "#cc8800",     # Orange - HT layer
    TokenSystem.HT_B_HYBRID: "#cc6600",     # Dark orange - hybrid
    TokenSystem.INFRASTRUCTURE: "#8888aa",  # Gray-blue - glue
    TokenSystem.ARTICULATOR: "#aa88cc",     # Purple - refinement
    TokenSystem.UNCLASSIFIED: "#666666",    # Gray
}


class TokenSystemClassifier:
    """
    Classifies tokens by their formal system.

    The ~37% of tokens outside C240 prefix system are NOT unknown -
    they're fully characterized by the constraint system.
    """

    # C347: HT prefixes (disjoint from A/B operational prefixes)
    HT_PREFIXES = frozenset({
        'yk', 'op', 'yt', 'sa', 'so', 'pc', 'do', 'ta', 'od', 'am'
    })

    # C407, C422: Infrastructure tokens (punctuation/glue)
    # These are exact-match tokens that serve structural roles
    INFRASTRUCTURE_TOKENS = frozenset({
        'ar', 'al', 'ol', 'y', 'daiin', 'dar', 'dal', 'dy',
        'r', 'l', 'or', 'am', 'an', 'aiin', 's'
    })

    # B suffixes for HT-B hybrid detection (C350)
    B_SUFFIXES = frozenset({
        'edy', 'dy', 'ar', 'am', 'om', 'aiin', 'ain', 'an', 'in'
    })

    # Articulator patterns (C291-295)
    # These add optional refinement but contribute zero identity distinctions
    ARTICULATOR_PREFIXES = frozenset({
        'ykch', 'ytch', 'pch', 'kch', 'dch', 'rch', 'fch',
        'yksh', 'ytsh', 'ksh', 'dsh', 'rsh', 'fsh',
        'yko', 'yto', 'ko', 'do', 'ro', 'fo'
    })

    def classify(self, token: str, parse_result: Optional['CurrierAParseResult'] = None) -> TokenSystem:
        """
        Determine token's primary system classification.

        Args:
            token: The token text
            parse_result: Optional parsed result (if available, speeds up classification)

        Returns:
            TokenSystem enum value
        """
        # Check infrastructure first (exact match takes priority)
        if token in self.INFRASTRUCTURE_TOKENS:
            return TokenSystem.INFRASTRUCTURE

        # Check for valid C240 prefix (operational system)
        if parse_result is not None and parse_result.prefix is not None:
            return TokenSystem.OPERATIONAL

        # Check for HT prefix patterns
        ht_match = self._get_ht_prefix(token)
        if ht_match:
            # Check for B suffix (hybrid)
            if self._has_b_suffix(token, ht_match):
                return TokenSystem.HT_B_HYBRID
            return TokenSystem.HUMAN_TRACK

        # Check for articulator patterns
        if self._is_articulator(token):
            return TokenSystem.ARTICULATOR

        # Check single-char tokens (often infrastructure)
        if len(token) == 1:
            return TokenSystem.INFRASTRUCTURE

        return TokenSystem.UNCLASSIFIED

    def _get_ht_prefix(self, token: str) -> Optional[str]:
        """Check if token starts with an HT prefix. Returns prefix if found."""
        for prefix in self.HT_PREFIXES:
            if token.startswith(prefix):
                return prefix
        return None

    def _has_b_suffix(self, token: str, ht_prefix: str) -> bool:
        """Check if token has a B suffix after HT prefix."""
        remainder = token[len(ht_prefix):]
        for suffix in self.B_SUFFIXES:
            if remainder.endswith(suffix):
                return True
        return False

    def _is_articulator(self, token: str) -> bool:
        """Check if token matches articulator patterns (C291-295)."""
        for prefix in self.ARTICULATOR_PREFIXES:
            if token.startswith(prefix):
                return True
        return False

    def get_system_display(self, system: TokenSystem) -> str:
        """Get display text with constraint reference."""
        display_map = {
            TokenSystem.OPERATIONAL: "Operational (C240)",
            TokenSystem.HUMAN_TRACK: "Human Track (C347)",
            TokenSystem.HT_B_HYBRID: "HT-B Hybrid (C350)",
            TokenSystem.INFRASTRUCTURE: "Infrastructure (C407)",
            TokenSystem.ARTICULATOR: "Articulator (C291)",
            TokenSystem.UNCLASSIFIED: "Unclassified",
        }
        return display_map.get(system, "Unknown")

    def get_system_color(self, system: TokenSystem) -> str:
        """Get UI color for system."""
        return SYSTEM_COLORS.get(system, "#666666")
