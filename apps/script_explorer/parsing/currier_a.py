"""
Currier A token parsing and validation.

Gate 1: C240 prefix legality (8 marker families + extended prefixes)
Gate 2: C267 morphological completeness (PREFIX + [MIDDLE] + SUFFIX)

IMPORTANT: This uses A-attested suffixes, NOT B-derived KNOWN_SUFFIXES.
Currier A suffixes are universal and permissive per CAS-MORPH.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

# =============================================================================
# CONSTANTS (Constraint-derived)
# =============================================================================

# C240: 8 validated marker families
MARKER_FAMILIES = {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}

# C349: Extended prefixes (C+C+h pattern)
EXTENDED_PREFIX_MAP = {
    'kch': 'ch', 'pch': 'ch', 'tch': 'ch', 'sch': 'sh',
    'dch': 'ch', 'rch': 'ch', 'fch': 'ch', 'lch': 'ch',
}

# A infrastructure minimal forms - atomic tokens valid in A context
# These are LINK/glue tokens that bypass the normal PREFIX+SUFFIX model
A_INFRASTRUCTURE_MINIMAL = {'ol', 'or', 'ar', 'al', 'am', 'an', 'l', 'r'}

# C269: Universal A suffixes (6+ prefix coverage, Currier A derived)
# NOTE: These are A-attested, NOT B-derived. See CAS-MORPH.
A_UNIVERSAL_SUFFIXES = {
    # C269: 7 universal suffixes (6+ prefix coverage)
    'ol', 'or', 'y', 'aiin', 'ar', 'chy', 'eeol',
    # Additional A-attested suffixes
    'ain', 'hy', 'al', 'am', 'an',
    'ey', 'dy', 'in',
}

# IMPORTANT: 'ol' is ALSO a prefix family (C240).
# When 'ol' appears at the end of a token with another valid prefix,
# it creates morphological ambiguity that must be flagged.
AMBIGUOUS_SUFFIX_PREFIXES = {'ol'}


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class AStatus(Enum):
    """Currier A token status after two-gate validation."""
    VALID_REGISTRY_ENTRY = auto()        # Prefix valid + has MIDDLE + valid SUFFIX
    VALID_MINIMAL = auto()               # Prefix valid + no MIDDLE + valid SUFFIX (includes chol, shol)
    UNDERSPECIFIED = auto()              # Valid prefix but no clear suffix pattern (chok, etc.)
    AMBIGUOUS_MORPHOLOGY = auto()        # Prefix valid but decomposition is ambiguous (kept for reference)
    PREFIX_VALID_MORPH_INCOMPLETE = auto()  # Prefix valid but no clear segmentation
    ILLEGAL_PREFIX = auto()              # No valid C240 prefix


@dataclass
class CurrierAParseResult:
    """Structured result from Currier A token parsing."""
    is_prefix_legal: bool       # Gate 1: C240 prefix check
    is_morph_complete: bool     # Gate 2: C267 structure check
    a_status: AStatus           # Combined status enum
    prefix: Optional[str]       # Detected prefix (2 or 3-char)
    middle: Optional[str]       # Middle component (may be '')
    suffix: Optional[str]       # Suffix component (may be ambiguous)
    reason: str                 # Human-readable explanation


# =============================================================================
# CORE PARSING FUNCTION
# =============================================================================

def parse_currier_a_token(token: str) -> CurrierAParseResult:
    """
    Full two-gate parsing for Currier A tokens.

    Gate 1: C240 prefix legality (8 families + extended prefixes)
    Gate 2: C267 morphological completeness (PREFIX + [MIDDLE] + SUFFIX)

    Uses A-attested suffixes (C269), NOT B-derived inventory.
    Flags ambiguous decompositions (e.g., when suffix is also a prefix).

    Special case: A infrastructure minimal forms (ol, ar, al, etc.) bypass
    normal two-gate validation as they are atomic LINK/glue tokens.
    """
    token_lower = token.lower()

    # === SPECIAL CASE: Infrastructure minimal forms ===
    # These are atomic A tokens that bypass the PREFIX+SUFFIX model
    if token_lower in A_INFRASTRUCTURE_MINIMAL:
        return CurrierAParseResult(
            is_prefix_legal=True,
            is_morph_complete=True,
            a_status=AStatus.VALID_MINIMAL,
            prefix=token_lower,  # Treat whole token as prefix
            middle=None,
            suffix=None,
            reason=f"Infrastructure minimal form (LINK/glue token)"
        )

    # === GATE 1: PREFIX LEGALITY (C240) ===
    detected_prefix = None
    prefix_family = None

    # Check extended prefixes first (C349: 3-char like kch, sch)
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

    # Gate 1 failure: No valid prefix
    if detected_prefix is None:
        return CurrierAParseResult(
            is_prefix_legal=False,
            is_morph_complete=False,
            a_status=AStatus.ILLEGAL_PREFIX,
            prefix=None,
            middle=None,
            suffix=None,
            reason=f"No valid C240 prefix (requires: {', '.join(sorted(MARKER_FAMILIES))})"
        )

    # === GATE 2: MORPHOLOGICAL COMPLETENESS (C267) ===
    remainder = token_lower[len(detected_prefix):]

    # Edge case: prefix-only token (no remainder)
    if not remainder:
        return CurrierAParseResult(
            is_prefix_legal=True,
            is_morph_complete=False,
            a_status=AStatus.PREFIX_VALID_MORPH_INCOMPLETE,
            prefix=detected_prefix,
            middle=None,
            suffix=None,
            reason=f"Prefix '{detected_prefix}' valid but token has no suffix (C267 requires SUFFIX)"
        )

    # Find valid suffix (longest match from end)
    detected_suffix = None
    for suffix_len in range(min(4, len(remainder)), 0, -1):
        candidate = remainder[-suffix_len:]
        if candidate in A_UNIVERSAL_SUFFIXES:
            detected_suffix = candidate
            break

    # No recognizable A suffix pattern - token is UNDERSPECIFIED (valid prefix, unclear suffix)
    # This is NOT invalid - it's a valid A token with underspecified morphology
    if detected_suffix is None:
        return CurrierAParseResult(
            is_prefix_legal=True,
            is_morph_complete=False,  # Morphology incomplete, but still valid A
            a_status=AStatus.UNDERSPECIFIED,
            prefix=detected_prefix,
            middle=remainder,
            suffix=None,
            reason=f"Underspecified: prefix '{detected_prefix}' valid, remainder '{remainder}' has no clear suffix"
        )

    # Handle suffix that is also a prefix family (e.g., 'ol')
    # These are still VALID - ambiguity doesn't mean invalid (CAS-MORPH)
    if detected_suffix in AMBIGUOUS_SUFFIX_PREFIXES:
        middle_end = len(remainder) - len(detected_suffix)
        detected_middle = remainder[:middle_end] if middle_end > 0 else ''

        # Determine status based on middle presence
        if detected_middle:
            status = AStatus.VALID_REGISTRY_ENTRY
            reason = f"Valid registry entry: {detected_prefix}-{detected_middle}-{detected_suffix} (note: suffix also functions as prefix)"
        else:
            status = AStatus.VALID_MINIMAL
            reason = f"Valid minimal form: {detected_prefix}-{detected_suffix} (note: suffix also functions as prefix)"

        return CurrierAParseResult(
            is_prefix_legal=True,
            is_morph_complete=True,  # Valid despite suffix/prefix overlap
            a_status=status,
            prefix=detected_prefix,
            middle=detected_middle if detected_middle else None,
            suffix=detected_suffix,
            reason=reason
        )

    # Extract middle (between prefix and suffix)
    middle_end = len(remainder) - len(detected_suffix)
    detected_middle = remainder[:middle_end] if middle_end > 0 else ''

    # Determine final status based on middle presence
    if detected_middle:
        status = AStatus.VALID_REGISTRY_ENTRY
        reason = f"Valid registry entry: {detected_prefix}-{detected_middle}-{detected_suffix}"
    else:
        status = AStatus.VALID_MINIMAL
        reason = f"Valid minimal form: {detected_prefix}-{detected_suffix}"

    return CurrierAParseResult(
        is_prefix_legal=True,
        is_morph_complete=True,
        a_status=status,
        prefix=detected_prefix,
        middle=detected_middle if detected_middle else None,
        suffix=detected_suffix,
        reason=reason
    )


# =============================================================================
# LEGACY WRAPPER (Backward Compatibility)
# =============================================================================

def validate_currier_a_token(token: str) -> Tuple[bool, str]:
    """
    Legacy wrapper for backward compatibility.
    Returns (is_valid, reason) where is_valid = prefix_legal AND morph_complete.
    """
    result = parse_currier_a_token(token)
    is_valid = result.is_prefix_legal and result.is_morph_complete
    return (is_valid, result.reason)
