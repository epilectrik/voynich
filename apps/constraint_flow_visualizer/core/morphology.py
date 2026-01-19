"""
Morphology decomposition for Currier A tokens.

Extracts PREFIX, MIDDLE, and SUFFIX components per C267.
The MIDDLE is the primary discriminator for AZC legality (C441, C472).

Based on constraint-derived rules from CASC (Currier A Structural Contract).
"""

from dataclasses import dataclass
from typing import Optional, Set


# =============================================================================
# CONSTANTS (Constraint-derived from C240, C267, C269, C349)
# =============================================================================

# C240: 8 validated marker families
MARKER_FAMILIES: Set[str] = {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}

# C349: Extended prefixes (C+C+h pattern) map to base families
EXTENDED_PREFIX_MAP = {
    'kch': 'ch', 'pch': 'ch', 'tch': 'ch', 'sch': 'sh',
    'dch': 'ch', 'rch': 'ch', 'fch': 'ch', 'lch': 'ch',
}

# Infrastructure minimal forms - atomic tokens that bypass PREFIX+SUFFIX model
A_INFRASTRUCTURE_MINIMAL: Set[str] = {'ol', 'or', 'ar', 'al', 'am', 'an', 'l', 'r'}

# C291-C292: Articulator prefixes have ZERO discriminative capacity
# These are expressive refinements only, NOT discriminators
# Articulator MIDDLEs must NOT participate in AZC discrimination
ARTICULATOR_PREFIXES: Set[str] = {
    'kch', 'tch', 'dch', 'rch', 'pch', 'sch', 'fch', 'lch',  # C+C+h pattern
    'yk', 'yt',  # y+C pattern
}


def is_articulator(token: str) -> bool:
    """
    Check if a token has an articulator prefix.

    Per C291-C292: Articulators have zero unique identity distinctions.
    They are expressive refinement only, NOT discriminators.
    Articulator MIDDLEs must NOT participate in AZC discrimination.

    Args:
        token: The token to check

    Returns:
        True if the token starts with an articulator prefix
    """
    token_lower = token.lower().strip()
    for art_prefix in ARTICULATOR_PREFIXES:
        if token_lower.startswith(art_prefix):
            return True
    return False

# C269: Universal A suffixes (Currier A attested)
A_UNIVERSAL_SUFFIXES: Set[str] = {
    # C269: 7 universal suffixes (6+ prefix coverage)
    'ol', 'or', 'y', 'aiin', 'ar', 'chy', 'eeol',
    # Additional A-attested suffixes
    'ain', 'hy', 'al', 'am', 'an', 'ey', 'dy', 'in',
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MorphologyResult:
    """Result of token morphology decomposition."""
    token: str
    prefix: Optional[str]
    prefix_family: Optional[str]  # Base family (for extended prefixes)
    middle: Optional[str]
    suffix: Optional[str]
    is_valid: bool
    is_infrastructure: bool
    reason: str

    @property
    def has_middle(self) -> bool:
        """Check if token has a non-empty MIDDLE component."""
        return self.middle is not None and len(self.middle) > 0


# =============================================================================
# CORE DECOMPOSITION FUNCTION
# =============================================================================

def decompose_token(token: str) -> MorphologyResult:
    """
    Decompose a Currier A token into PREFIX, MIDDLE, SUFFIX.

    The MIDDLE component is the primary discriminator for AZC legality.
    Per C472, 77% of MIDDLEs appear in only 1 AZC folio.

    Args:
        token: The EVA token string to decompose

    Returns:
        MorphologyResult with decomposed components
    """
    token_lower = token.lower().strip()

    if not token_lower:
        return MorphologyResult(
            token=token,
            prefix=None,
            prefix_family=None,
            middle=None,
            suffix=None,
            is_valid=False,
            is_infrastructure=False,
            reason="Empty token"
        )

    # === SPECIAL CASE: Infrastructure minimal forms ===
    if token_lower in A_INFRASTRUCTURE_MINIMAL:
        return MorphologyResult(
            token=token,
            prefix=token_lower,
            prefix_family=token_lower,
            middle=None,
            suffix=None,
            is_valid=True,
            is_infrastructure=True,
            reason="Infrastructure minimal form (LINK/glue token)"
        )

    # === STEP 1: EXTRACT PREFIX ===
    detected_prefix = None
    prefix_family = None

    # Check extended prefixes first (3-char like kch, sch)
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            detected_prefix = prefix3
            prefix_family = EXTENDED_PREFIX_MAP[prefix3]

    # Check standard 2-char prefixes
    if detected_prefix is None and len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            detected_prefix = prefix2
            prefix_family = prefix2

    # No valid prefix found
    if detected_prefix is None:
        return MorphologyResult(
            token=token,
            prefix=None,
            prefix_family=None,
            middle=None,
            suffix=None,
            is_valid=False,
            is_infrastructure=False,
            reason=f"No valid C240 prefix"
        )

    # === STEP 2: EXTRACT SUFFIX ===
    remainder = token_lower[len(detected_prefix):]

    if not remainder:
        return MorphologyResult(
            token=token,
            prefix=detected_prefix,
            prefix_family=prefix_family,
            middle=None,
            suffix=None,
            is_valid=False,
            is_infrastructure=False,
            reason="No suffix after prefix"
        )

    # Find valid suffix (longest match from end)
    detected_suffix = None
    for suffix_len in range(min(4, len(remainder)), 0, -1):
        candidate = remainder[-suffix_len:]
        if candidate in A_UNIVERSAL_SUFFIXES:
            detected_suffix = candidate
            break

    # === STEP 3: EXTRACT MIDDLE ===
    if detected_suffix is None:
        # No clear suffix - treat entire remainder as ambiguous
        return MorphologyResult(
            token=token,
            prefix=detected_prefix,
            prefix_family=prefix_family,
            middle=remainder,  # Best guess: everything after prefix
            suffix=None,
            is_valid=True,  # Still valid for AZC purposes
            is_infrastructure=False,
            reason=f"Underspecified suffix; MIDDLE approximated as '{remainder}'"
        )

    # Extract middle (between prefix and suffix)
    middle_end = len(remainder) - len(detected_suffix)
    detected_middle = remainder[:middle_end] if middle_end > 0 else None

    return MorphologyResult(
        token=token,
        prefix=detected_prefix,
        prefix_family=prefix_family,
        middle=detected_middle,
        suffix=detected_suffix,
        is_valid=True,
        is_infrastructure=False,
        reason=f"Decomposed: {detected_prefix}-{detected_middle or ''}-{detected_suffix}"
    )


def get_middle(token: str) -> Optional[str]:
    """
    Quick extraction of MIDDLE component only.

    This is the primary discriminator for AZC legality projection.
    """
    result = decompose_token(token)
    return result.middle


def get_prefix_family(token: str) -> Optional[str]:
    """Get the base prefix family for a token."""
    result = decompose_token(token)
    return result.prefix_family


def is_valid_a_token(token: str) -> bool:
    """Check if a token is valid for Currier A analysis."""
    result = decompose_token(token)
    return result.is_valid


# =============================================================================
# BATCH OPERATIONS
# =============================================================================

def decompose_tokens(tokens: list) -> list:
    """Decompose multiple tokens at once."""
    return [decompose_token(t) for t in tokens]


def extract_middles(tokens: list) -> Set[str]:
    """Extract all unique MIDDLEs from a list of tokens."""
    middles = set()
    for token in tokens:
        result = decompose_token(token)
        if result.middle:
            middles.add(result.middle)
    return middles


if __name__ == "__main__":
    # Test decomposition
    test_tokens = [
        'chedy', 'qokaiin', 'daiin', 'shey', 'okaiin',
        'ol', 'ar',  # Infrastructure
        'chol', 'shol',  # Minimal forms
        'kchedy',  # Extended prefix
        'xyz',  # Invalid
    ]

    print("Morphology Decomposition Test")
    print("=" * 60)

    for token in test_tokens:
        result = decompose_token(token)
        if result.is_valid:
            print(f"\n{token}:")
            print(f"  PREFIX: {result.prefix} (family: {result.prefix_family})")
            print(f"  MIDDLE: {result.middle or '(none)'}")
            print(f"  SUFFIX: {result.suffix or '(none)'}")
            print(f"  Infrastructure: {result.is_infrastructure}")
        else:
            print(f"\n{token}: INVALID - {result.reason}")
