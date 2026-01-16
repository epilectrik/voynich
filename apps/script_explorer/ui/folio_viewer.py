"""
Folio Viewer - Displays Voynich manuscript transcription with classification-based highlighting.

VISUAL DESIGN OVERHAUL (Jan 2026)
- Token backgrounds encode classification (LINK/A/B/HT) - toggleable view modes
- Morphology shown on-demand in detail panel (not inline)
- Click-to-select interaction
- All facts traceable to C-numbers
"""

from pathlib import Path
from typing import Optional, List, Dict, Tuple
from enum import Enum, auto
import re
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QStyleOption, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QMouseEvent, QPainter, QFontMetrics, QPalette

import sys
_app_dir = Path(__file__).parent.parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

try:
    from core.transcription import TranscriptionLoader, FolioTranscription
    from core.grammar import Grammar, OperatorRole
    from core.constraints import ConstraintLoader
    from parsing.currier_a import (
        parse_currier_a_token,
        validate_currier_a_token,
        CurrierAParseResult,
        AStatus,
        MARKER_FAMILIES,
        EXTENDED_PREFIX_MAP,
        A_UNIVERSAL_SUFFIXES,
        A_INFRASTRUCTURE_MINIMAL,
    )
except ImportError:
    from ..core.transcription import TranscriptionLoader, FolioTranscription
    from ..core.grammar import Grammar, OperatorRole
    from ..core.constraints import ConstraintLoader
    from ..parsing.currier_a import (
        parse_currier_a_token,
        validate_currier_a_token,
        CurrierAParseResult,
        AStatus,
        MARKER_FAMILIES,
        EXTENDED_PREFIX_MAP,
        A_UNIVERSAL_SUFFIXES,
        A_INFRASTRUCTURE_MINIMAL,
    )


# =============================================================================
# VIEW MODES - System-Aware Architecture
# =============================================================================

class ViewMode(Enum):
    """Token highlighting modes - system-aware to respect constraint boundaries.

    View modes are organized by which Currier system they apply to:
    - Global modes: Valid in all systems (shared type system per C383)
    - B modes: Valid only in Currier B (execution grammar)
    - A modes: Valid only in Currier A (categorical registry)
    - AZC modes: Valid only in AZC (diagram annotation)
    """
    # === Global modes (valid in all systems) ===
    PLAIN = auto()            # No highlighting
    MORPHOLOGY = auto()       # Prefix families (C267) - compositional structure
    KERNEL_AFFINITY = auto()  # Heavy/Light morphological pattern (C383) - NOT execution
    LINK_AFFINITY = auto()    # LINK attraction/avoidance pattern

    # === Currier B modes (execution grammar) ===
    B_INSTRUCTION = auto()    # 49-class grammar roles (C121)
    B_POSITION = auto()       # Line-initial/final positional grammar (C371)
    B_KERNEL_CONTACT = auto() # Kernel contact EXECUTION semantics (C372)
    B_EXECUTION = auto()      # Composite execution view (C357, C371, C372, C373)

    # === Currier A modes (categorical registry) ===
    A_MARKER = auto()         # 8 marker families (C235, C240)
    A_SISTER = auto()         # ch-sh, ok-ot equivalence classes (C408)
    A_ROLE = auto()           # Structure vs Data functional role (C267, C291)
    A_MULTIPLICITY = auto()   # Enumeration pattern (C250) - placeholder

    # === AZC modes (diagram annotation) ===
    AZC_PLACEMENT = auto()    # Topological placement classes (C306)
    AZC_LEGALITY = auto()     # Position legality constraints (C313) - placeholder


# Which modes are available per Currier system
SYSTEM_MODES = {
    'B': [
        ViewMode.PLAIN, ViewMode.MORPHOLOGY, ViewMode.KERNEL_AFFINITY, ViewMode.LINK_AFFINITY,
        ViewMode.B_INSTRUCTION, ViewMode.B_POSITION, ViewMode.B_KERNEL_CONTACT, ViewMode.B_EXECUTION
    ],
    'A': [
        ViewMode.PLAIN, ViewMode.MORPHOLOGY, ViewMode.KERNEL_AFFINITY, ViewMode.LINK_AFFINITY,
        ViewMode.A_MARKER, ViewMode.A_SISTER, ViewMode.A_ROLE
    ],
    'AZC': [
        ViewMode.PLAIN, ViewMode.MORPHOLOGY, ViewMode.KERNEL_AFFINITY, ViewMode.LINK_AFFINITY,
        ViewMode.AZC_PLACEMENT
    ],
}

# Default mode per system
SYSTEM_DEFAULT_MODE = {
    'B': ViewMode.B_INSTRUCTION,
    'A': ViewMode.A_MARKER,
    'AZC': ViewMode.AZC_PLACEMENT,
}

# Display labels with tooltips (label, tooltip)
VIEW_MODE_LABELS = {
    ViewMode.PLAIN: ("Plain", None),
    ViewMode.MORPHOLOGY: ("Morph", "Prefix family decomposition (C267)"),
    ViewMode.KERNEL_AFFINITY: ("Affinity", "Morphological kernel affinity — shared type system, not execution"),
    ViewMode.LINK_AFFINITY: ("LINK", "LINK operator attraction/avoidance pattern"),
    ViewMode.B_INSTRUCTION: ("Instr", "49-class instruction grammar (C121)"),
    ViewMode.B_POSITION: ("Position", "Line-initial/final positional grammar (C371)"),
    ViewMode.B_KERNEL_CONTACT: ("Contact", "Kernel contact execution semantics (C372)"),
    ViewMode.B_EXECUTION: ("Exec", "Composite execution inspector: kernel contact + position + LINK (C357, C371-373)"),
    ViewMode.A_MARKER: ("Marker", "8 validated marker families: ch/sh/ok/ot/da/qo/ol/ct (C240)"),
    ViewMode.A_SISTER: ("Sister", "ch-sh, ok-ot equivalence classes (C408)"),
    ViewMode.A_ROLE: ("Role", "Functional role: Structure vs Data (C267). Prefixes limited to validated families."),
    ViewMode.A_MULTIPLICITY: ("Multi", "Multiplicity enumeration pattern (C250)"),
    ViewMode.AZC_PLACEMENT: ("Place", "Topological placement classes (C306)"),
    ViewMode.AZC_LEGALITY: ("Legal", "Position legality constraints (C313)"),
}

# System banner text (title, subtitle)
SYSTEM_BANNERS = {
    'B': ("CURRIER B — Execution Grammar", "Sequential control grammar. Execution semantics active."),
    'A': ("CURRIER A — Registry Mode", "Non-sequential registry. 8 validated marker families (C240)."),
    'AZC': ("AZC — Diagram Annotation", "Diagram-anchored labeling. Positional legality only."),
}


# =============================================================================
# COLOR PALETTES (Per View Mode) - System-Aware
# =============================================================================

# --- GLOBAL MODE COLORS (valid in all systems) ---

# Morphology mode colors - prefix families (C267)
MORPHOLOGY_COLORS = {
    'ch': '#5A3A3A',  # Red family - ch-
    'sh': '#5A4A3A',  # Orange family - sh-
    'da': '#3A4A5A',  # Blue family - da-
    'sa': '#3A5A5A',  # Cyan family - sa-
    'qo': '#3A5A3A',  # Green family - qo- (escape)
    'ok': '#5A3A5A',  # Purple family - ok-
    'ot': '#4A3A5A',  # Violet family - ot-
    'ol': '#3A5A4A',  # Teal family - ol-
    'al': '#4A5A3A',  # Lime family - al-
    'ct': '#5A5A3A',  # Yellow family - ct-
    'other': '#4A4A4A',  # Gray - other prefixes
}

# Kernel AFFINITY mode colors (C383 - global type system, NOT execution)
KERNEL_AFFINITY_COLORS = {
    'heavy':   '#4A2828',  # Warm red - kernel-heavy morphology (ch-, sh-, ok-)
    'light':   '#28384A',  # Cool blue - kernel-light morphology (da-, sa-)
    'escape':  '#3A4A3A',  # Green - escape route morphology (qo-)
    'neutral': 'transparent',
}

# LINK affinity mode colors
LINK_AFFINITY_COLORS = {
    'attracted': '#3A5A6A',  # Teal - LINK-attracted (ol, al, da)
    'avoided':   '#5A3A3A',  # Red - LINK-avoided (qo)
    'neutral':   'transparent',
}

# --- CURRIER B MODE COLORS (execution grammar) ---

# B Instruction class mode colors (C121 - 49 classes grouped by role)
B_INSTRUCTION_COLORS = {
    'CORE_CONTROL':      '#4A3A5A',  # Deep purple - execution boundaries
    'ENERGY_OPERATOR':   '#5A3A3A',  # Deep red - energy modulation
    'FLOW_OPERATOR':     '#3A4A5A',  # Steel blue - flow control
    'HIGH_IMPACT':       '#5A4A3A',  # Bronze - major interventions
    'FREQUENT_OPERATOR': '#3A5A4A',  # Teal - common operations
    'AUXILIARY':         '#4A4A3A',  # Olive - support operations
    'LINK':              '#3A5A5A',  # Cyan - LINK behavior
    'MODIFIER':          '#4A3A4A',  # Mauve - parameter modifiers
    'TERMINAL':          '#5A3A4A',  # Plum - sequence terminators
    'UNKNOWN':           '#3A3A3A',  # Dark gray - unmapped tokens
}

# B Position mode colors (C371)
B_POSITION_COLORS = {
    'initial': '#4A5A3A',  # Green - line-initial enriched
    'final':   '#5A4A3A',  # Orange - line-final enriched
    'link':    '#3A5A6A',  # Teal - LINK tokens (shown for context)
    'neutral': 'transparent',
}

# B Kernel CONTACT mode colors (C372 - execution semantics, B-ONLY)
B_KERNEL_CONTACT_COLORS = {
    'heavy':   '#6A2828',  # Brighter red - intervention contact
    'light':   '#284A6A',  # Brighter blue - monitoring contact
    'escape':  '#3A6A3A',  # Brighter green - escape contact
    'neutral': 'transparent',
}

# B EXECUTION composite mode colors (C357, C371-373 - execution inspector)
# Uses higher saturation to signal "execution mode active"
B_EXECUTION_COLORS = {
    'heavy':   '#8A3030',  # Bright red - INTERVENTION phase (kernel-heavy)
    'light':   '#305A8A',  # Bright blue - MONITORING phase (kernel-light)
    'escape':  '#408A40',  # Bright green - ESCAPE route (qo-)
    'neutral': '#4A4A5A',  # Visible gray - unclassified (shows execution is analyzing)
}

# --- CURRIER A MODE COLORS (categorical registry) ---

# A Marker family mode colors (C235, C240 - 8 marker families)
A_MARKER_COLORS = {
    'ch': '#5A3A4A',  # Mauve - primary classifier
    'sh': '#5A4A4A',  # Gray-mauve - sister to ch
    'ok': '#3A4A5A',  # Steel blue - primary classifier
    'ot': '#3A5A5A',  # Teal - sister to ok
    'da': '#4A5A3A',  # Olive - infrastructure
    'qo': '#5A5A3A',  # Yellow-olive - bridging
    'ol': '#4A3A5A',  # Purple - bridging
    'ct': '#5A3A3A',  # Red - section H specialist
    'other': '#3A3A3A',  # Dark gray - other
}

# A Sister pair mode colors (C408)
A_SISTER_COLORS = {
    'pair1_ch': '#5A3A4A',  # ch-sh pair - one shade
    'pair1_sh': '#6A4A5A',  # ch-sh pair - sister shade
    'pair2_ok': '#3A4A5A',  # ok-ot pair - one shade
    'pair2_ot': '#4A5A6A',  # ok-ot pair - sister shade
    'other': '#4A4A4A',     # Not a sister pair
}

# A Role mode colors (C267, C291 - functional role classification)
A_ROLE_COLORS = {
    'ARTICULATED':    '#6A4A7A',  # Purple - has optional refinement prefix
    'INFRASTRUCTURE': '#2A5A6A',  # Deep teal - registry infrastructure token
    'REGISTRY_ENTRY': '#5A6A3A',  # Olive green - categorical entry with MIDDLE
    'MINIMAL':        '#5A5A4A',  # Muted gray - prefix + suffix, no middle
}

# Articulator prefixes (~20% of A tokens, C291)
ARTICULATORS = {'yk', 'yt', 'kch', 'ks', 'ko', 'yd', 'ysh', 'ych', 'yp'}

# Infrastructure tokens (registry glue) - from currier_a.md
A_INFRASTRUCTURE_TOKENS = {'daiin', 'dain', 'ol', 'or', 'ar', 'al', 'am', 'an', 'l', 'r'}

# --- AZC MODE COLORS (diagram annotation) ---

# AZC Placement class mode colors (C306)
AZC_PLACEMENT_COLORS = {
    'C': '#5A3A5A',   # Core - purple
    'P': '#3A5A5A',   # Peripheral - teal
    'R': '#5A5A3A',   # Ring - olive
    'S': '#3A3A5A',   # Surface - blue
    'B': '#5A3A3A',   # Base - red
    'T': '#3A5A3A',   # Top - green
    'L': '#4A4A5A',   # Left - gray-blue
    'M': '#5A4A4A',   # Middle - gray-red
    'N': '#4A5A4A',   # Node - gray-green
    'other': '#4A4A4A',  # Unknown placement
}

# --- LEGACY COLORS (for compatibility during transition) ---

# Classification mode colors (C089, C090, C105, C404-406) - used in B only
CLASSIFICATION_COLORS = {
    'link':        '#3A5A6A',  # Teal - structural boundary (C105)
    'a_enriched':  '#4A3A28',  # Warm brown - A-typical (C089)
    'b_enriched':  '#2A3A4A',  # Cool slate - B-typical (C090)
    'human_track': '#3A2A4A',  # Muted purple - non-operational (C404-406)
    'neutral':     'transparent',
}

# Legacy aliases (for backward compatibility)
KERNEL_COLORS = KERNEL_AFFINITY_COLORS
INSTRUCTION_COLORS = B_INSTRUCTION_COLORS
LEGALITY_COLORS = {
    'a_only':  '#6B8E9B',
    'b_only':  '#7B9B6B',
    'cross':   '#9B8B6B',
    'azc':     '#9B6B8E',
    'unknown': '#4A4A4A',
}

# Text colors
TEXT_COLORS = {
    'default':  '#E0D8C8',  # Warm parchment
    'selected': '#FFFFFF',  # White for selected token
}

# Classification state colors (for UNDERSPECIFIED, UNCERTAIN, and residual categories)
STATE_COLORS = {
    'A_UNDERSPECIFIED': '#4A4A3A',     # Muted grey-olive (valid prefix, unclear suffix)
    'UNCERTAIN': '#3A3A4A',            # Grey-blue (transcription uncertainty)
    # Residual categories (tokens failing A validation - typed, not single INVALID)
    'DAMAGED_OR_TRUNCATED': '#4A3A3A', # Muted red-brown (near-valid, truncated forms)
    'FORMED_NON_SYSTEM': '#3A3A4A',    # Grey-blue (well-formed but non-A)
    'INVALID_TRUE': '#2A2A2A',         # Dark grey (garbage, minimal visual weight)
}

# Selection state
SELECTION = {
    'ring_color': '#FFD080',  # Gold ring
    'glow_blur':  8,
}

# Chrome (UI elements)
CHROME = {
    'line_number': '#5C4A32',
    'separator':   '#3D3428',
    'background':  '#12100E',
    'line_bg':     '#1A1612',
}


# =============================================================================
# SYSTEM LEGALITY LOOKUP (Lazy-loaded)
# =============================================================================

# These sets are populated on first use from transcription data
_LEGALITY_CACHE = {
    'a_tokens': None,
    'b_tokens': None,
    'azc_tokens': None,
    'loaded': False
}


def _load_legality_data():
    """Load token legality data from transcription file."""
    if _LEGALITY_CACHE['loaded']:
        return

    import csv
    a_tokens = set()
    b_tokens = set()
    azc_tokens = set()

    paths = [
        Path(__file__).parent.parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
        Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt'),
    ]

    for path in paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        token = row.get('word', '').lower().strip('"')
                        lang = row.get('language', '')
                        if token and not token.startswith('*'):
                            if lang == 'A':
                                a_tokens.add(token)
                            elif lang == 'B':
                                b_tokens.add(token)
                            else:  # NA or other = AZC
                                azc_tokens.add(token)
                break
            except Exception:
                continue

    _LEGALITY_CACHE['a_tokens'] = a_tokens
    _LEGALITY_CACHE['b_tokens'] = b_tokens
    _LEGALITY_CACHE['azc_tokens'] = azc_tokens
    _LEGALITY_CACHE['loaded'] = True


def get_token_legality(token: str) -> str:
    """Get system legality for a token. Returns: 'a_only', 'b_only', 'cross', 'azc', 'unknown'."""
    _load_legality_data()

    token_lower = token.lower()
    in_a = token_lower in _LEGALITY_CACHE['a_tokens']
    in_b = token_lower in _LEGALITY_CACHE['b_tokens']
    in_azc = token_lower in _LEGALITY_CACHE['azc_tokens']

    if in_a and in_b:
        return 'cross'
    elif in_a:
        return 'a_only'
    elif in_b:
        return 'b_only'
    elif in_azc:
        return 'azc'
    else:
        return 'unknown'


# Grammar instance for instruction class lookup
_GRAMMAR_INSTANCE = None


def _get_grammar():
    """Get or create Grammar instance."""
    global _GRAMMAR_INSTANCE
    if _GRAMMAR_INSTANCE is None:
        _GRAMMAR_INSTANCE = Grammar()
    return _GRAMMAR_INSTANCE


def get_token_instruction_role(token: str) -> str:
    """Get instruction class role for a token. Returns role name or 'UNKNOWN'."""
    grammar = _get_grammar()
    instr_class = grammar.get_by_symbol(token)
    if instr_class:
        return instr_class.role.name
    return 'UNKNOWN'


def get_token_prefix_family(token: str) -> str:
    """Get prefix family for morphology mode. Returns prefix or 'other'."""
    token_lower = token.lower()
    if len(token_lower) >= 2:
        prefix = token_lower[:2]
        if prefix in MORPHOLOGY_COLORS:
            return prefix
    return 'other'


def get_kernel_affinity(token: str) -> str:
    """Get kernel AFFINITY (morphological pattern, NOT execution). Returns: 'heavy', 'light', 'escape', 'neutral'.

    This is a GLOBAL mode valid in all systems - it shows morphological kernel affinity
    from the shared type system (C383), NOT execution semantics.

    Extended prefixes (dch, tch, rch, etc.) inherit affinity from their base family.
    """
    token_lower = token.lower()

    # Check extended 3-char prefixes first (C349) - inherit from base family
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        # Extended prefixes map to their base family
        extended_to_base = {
            'kch': 'ch', 'pch': 'ch', 'tch': 'ch', 'sch': 'sh',
            'dch': 'ch', 'rch': 'ch', 'fch': 'ch', 'lch': 'ch',
        }
        if prefix3 in extended_to_base:
            base = extended_to_base[prefix3]
            # ch/sh are kernel-heavy
            if base in {'ch', 'sh'}:
                return 'heavy'

    prefix = token_lower[:2] if len(token_lower) >= 2 else ''

    # Escape morphology (qo-)
    if prefix == 'qo':
        return 'escape'
    # Kernel-heavy morphology (ch-, sh-, ok-, ot-)
    # NOTE: ct is NOT heavy - it's an isolate family (light)
    if prefix in {'ch', 'sh', 'ok', 'ot'}:
        return 'heavy'
    # Kernel-light morphology (da-, sa-, ct-, ol-)
    if prefix in {'da', 'sa', 'ct', 'ol'}:
        return 'light'

    return 'neutral'


def get_link_affinity(token: str) -> str:
    """Get LINK affinity pattern. Returns: 'attracted', 'avoided', 'neutral'.

    Based on C373 - LINK attraction/avoidance patterns.
    """
    token_lower = token.lower()

    # LINK-attracted tokens (C373)
    link_attracted = {'ol', 'al', 'or', 'ar', 'am', 'an', 'l', 'r', 'daiin', 'dal', 'sal'}
    if token_lower in link_attracted:
        return 'attracted'

    # Check for LINK-attracted prefixes
    if len(token_lower) >= 2:
        prefix = token_lower[:2]
        if prefix in {'ol', 'al', 'da', 'sa'}:
            return 'attracted'

    # LINK-avoided (qo- prefix)
    if token_lower.startswith('qo'):
        return 'avoided'

    return 'neutral'


def get_a_marker_family(token: str) -> Optional[str]:
    """Get A marker family for Currier A registry mode.

    Returns marker family (str) or None if token has no valid marker.
    Based on C235, C240 - exactly 8 categorical marker families in Currier A.
    C349 - Extended prefixes map to their base marker family.
    """
    token_lower = token.lower()

    # Check infrastructure minimal tokens first (ol, or, ar, al, am, an, l, r)
    # These are valid A tokens that map to 'ol' family (LINK infrastructure)
    if token_lower in A_INFRASTRUCTURE_MINIMAL:
        return 'ol'  # Map infrastructure tokens to ol family

    # Check extended prefixes first (C349) - explicit mapping
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            return EXTENDED_PREFIX_MAP[prefix3]

    # Check standard marker families (C240)
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            return prefix2

    return None  # Not valid Currier A


def get_a_sister_pair(token: str) -> str:
    """Get A sister pair classification. Returns: 'pair1_ch', 'pair1_sh', 'pair2_ok', 'pair2_ot', 'other'.

    Based on C408 - ch-sh and ok-ot are equivalence classes with J=0.23-0.24.
    """
    token_lower = token.lower()
    if len(token_lower) >= 2:
        prefix = token_lower[:2]
        if prefix == 'ch':
            return 'pair1_ch'
        elif prefix == 'sh':
            return 'pair1_sh'
        elif prefix == 'ok':
            return 'pair2_ok'
        elif prefix == 'ot':
            return 'pair2_ot'
    return 'other'


def detect_articulator(token: str) -> str:
    """Detect articulator prefix if present. Returns articulator or ''.

    Based on C291 - ~20% of A tokens have articulator prefixes.
    Articulators are optional refinement, 100% removable without identity loss.
    """
    token_lower = token.lower()
    # Check 3-char first (longest match wins)
    for art in ('kch', 'ysh', 'ych'):
        if token_lower.startswith(art):
            return art
    # Check 2-char
    for art in ('yk', 'yt', 'ks', 'ko', 'yd', 'yp'):
        if token_lower.startswith(art):
            return art
    return ''


def segment_word_4component(word: str) -> Tuple[str, str, str, str]:
    """Segment into (articulator, prefix, middle, suffix). C267 + C291.

    4-component morphology: [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
    - ARTICULATOR: Optional refinement (~20% of A tokens, C291)
    - PREFIX: 8 marker families (C240) or 7 extended clusters (C349)
    - MIDDLE: Type-specific data (optional)
    - SUFFIX: 7 universal forms (C269)
    """
    if not word:
        return ('', '', '', '')

    word_lower = word.lower()

    # Check extended prefixes FIRST (C349) - they take priority over articulators
    # This handles ambiguous cases like 'kch' which is both articulator and prefix
    articulator = ''
    prefix = ''
    if len(word_lower) >= 3 and word_lower[:3] in EXTENDED_PREFIXES:
        prefix = word[:3]
        remainder = word  # Keep full word, prefix is at start
    else:
        # No extended prefix - check for articulator
        articulator = detect_articulator(word)
        remainder = word[len(articulator):]
        remainder_lower = remainder.lower()

        # Then check for standard prefix (2-char, C240)
        if len(remainder_lower) >= 2 and remainder_lower[:2] in KNOWN_PREFIXES:
            prefix = remainder[:2]

    # Suffix (from end of remainder) - longest validated suffix match
    suffix = ''
    core_end = len(remainder)
    for suf_len in [4, 3, 2, 1]:
        if len(remainder) >= len(prefix) + suf_len:
            potential = remainder[-(suf_len):].lower()
            if potential in KNOWN_SUFFIXES:
                suffix = remainder[-(suf_len):]
                core_end = len(remainder) - suf_len
                break

    # Middle is what remains between prefix and suffix
    middle = remainder[len(prefix):core_end]

    return (articulator, prefix, middle, suffix)


def get_a_token_role(token: str) -> str:
    """Classify token functional role for A_ROLE view mode.

    Returns: 'ARTICULATED', 'INFRASTRUCTURE', 'REGISTRY_ENTRY', 'MINIMAL'.

    Based on C267 (compositional morphology) and C291 (articulators).
    Note: Currier A uses REGISTRY_ENTRY (not DATA) - categorical registry, not execution.
    """
    token_lower = token.lower()

    # INFRASTRUCTURE tokens (registry glue) - checked first
    if token_lower in A_INFRASTRUCTURE_TOKENS:
        return 'INFRASTRUCTURE'

    # Check for articulator
    articulator, prefix, middle, suffix = segment_word_4component(token)
    if articulator:
        return 'ARTICULATED'

    # MINIMAL (prefix + suffix, no middle) - frame only
    # Also includes very short suffix-like tokens
    if prefix and suffix and not middle:
        return 'MINIMAL'
    if len(token_lower) <= 2 and token_lower in KNOWN_SUFFIXES:
        return 'MINIMAL'

    # REGISTRY_ENTRY (has middle content - categorical payload)
    if middle:
        return 'REGISTRY_ENTRY'

    # Default: REGISTRY_ENTRY for categorized tokens
    return 'REGISTRY_ENTRY'


def get_azc_placement_group(placement: str) -> str:
    """Map specific placement (e.g., 'R2') to group (e.g., 'R').

    Based on C306 - topological placement classes in AZC.
    """
    if not placement:
        return 'other'
    # Strip numeric suffix
    base = placement.rstrip('0123456789')
    if base in AZC_PLACEMENT_COLORS:
        return base
    return 'other'


# =============================================================================
# MORPHOLOGICAL SEGMENTATION (For detail panel)
# =============================================================================

# NOTE: MARKER_FAMILIES and EXTENDED_PREFIX_MAP are imported from parsing.currier_a

# C349: Extended cluster prefixes (derived from EXTENDED_PREFIX_MAP for consistency)
EXTENDED_PREFIXES = set(EXTENDED_PREFIX_MAP.keys())

# Combined: All validated prefixes for parsing
# NOTE: Extended prefixes (3-char) must be checked before 2-char prefixes
KNOWN_PREFIXES = MARKER_FAMILIES  # 2-char only; extended handled separately

# Negative result: 'ck' is NOT a validated prefix family.
# Apparent ck- forms (95.9% are ckh-) resolve into ch-family variants.
# Do not add 'ck', 'kc', 'dc', 'fc', etc. without constraint validation.

KNOWN_SUFFIXES = {
    # C269: 7 universal suffixes (Currier A, 6+ prefix coverage)
    'ol', 'or', 'y', 'aiin', 'ar', 'chy', 'eeol',
    # C374: kernel-contact suffixes (Currier B)
    'edy', 'ey', 'dy', 'in',
    # LINK-related terminal forms
    'al', 'am', 'an',
    # Other validated atomic suffixes
    'ain', 'hy',
    # NOTE: Removed compounds (ry, ty, ny, ys, eey, eedy, etc.) - these are X+y, not atomic
}

# Kernel-heavy prefixes (C372: 100% kernel contact)
# NOTE: ct is NOT kernel-heavy - it's an isolate/registry family (light)
KERNEL_HEAVY_PREFIXES = {'ch', 'sh', 'ok', 'ot'}

# Kernel-light prefixes (C372: <5% kernel contact)
# Includes ct (isolate family) and infrastructure families
KERNEL_LIGHT_PREFIXES = {'da', 'sa', 'ct', 'ol'}

# Escape route prefix (C397)
ESCAPE_PREFIX = 'qo'

# Line-initial enriched prefixes (C371)
LINE_INITIAL_PREFIXES = {'so', 'po', 'to', 'ko'}

# Line-final enriched suffixes (C375)
LINE_FINAL_SUFFIXES = {'am', 'om', 'oly'}

# HT prefixes (C404-406)
HT_PREFIXES = {'yt', 'yp', 'yd', 'yf', 'yr', 'ys'}

# A-enriched tokens (C089) - simplified set, will be extended
A_ENRICHED_TOKENS = {
    'daiin', 'chedy', 'shedy', 'qokeey', 'qokedy', 'cheedy',
    'sheedy', 'qokeedy', 'cthy', 'shey', 'chey'
}

# B-enriched tokens (C090) - simplified set, will be extended
B_ENRICHED_TOKENS = {
    'ol', 'chol', 'sho', 'chor', 'shol', 'olor', 'ar', 'or',
    'dal', 'sal', 'lol', 'cho', 'she'
}

# LINK tokens (C105)
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'am', 'an', 'l', 'r'}


# NOTE: validate_currier_a_token and parse_currier_a_token are imported from parsing.currier_a


# =============================================================================
# RESIDUAL CLASSIFICATION (for tokens failing A validation)
# =============================================================================

def _is_garbage_pattern(token: str) -> bool:
    """Check if token is garbage (repetitive chars, impossible sequences).

    RULE-BASED: No token-specific lists.
    """
    token_lower = token.lower()
    # Excessive same-char repetition (3+ of same char)
    if any(c * 3 in token_lower for c in 'abcdefghijklmnopqrstuvwxyz'):
        return True
    # Single-char tokens not in any system
    if len(token_lower) == 1 and token_lower not in 'yfdr':
        return True
    return False


def _is_near_valid_a(token: str) -> bool:
    """Check if token is structurally close to valid A form.

    RULE-BASED ONLY - NO hard-coded token lists.

    Criteria:
    - Has valid A prefix but looks suffix-truncated
    - Missing final vowel/suffix pattern
    - Edit distance <= 1 from valid A structure
    """
    token_lower = token.lower()

    # Check if prepending a single char yields valid A prefix
    # This catches truncation like 'hol' (missing c/s) -> 'chol'/'shol'
    for prefix_char in ['c', 's', 'o', 'd', 'q']:
        test = prefix_char + token_lower
        if test[:2] in {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}:
            return True

    # Check for valid A prefix + truncated suffix pattern
    # e.g., 'cho' (missing -l/-y), 'sho' (missing -l/-y)
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}:
            remainder = token_lower[2:]
            # Very short remainder suggests truncation
            if len(remainder) <= 1:
                return True

    return False


def _is_voynich_wellformed(token: str) -> bool:
    """Check if token follows general Voynich EVA patterns.

    CONSERVATIVE: Err on false negatives, not false positives.
    This should NOT scoop up garbage or HT-like strings.
    """
    token_lower = token.lower()

    # Reject if contains uncertainty markers
    if '*' in token_lower:
        return False

    # Length bounds (typical Voynich tokens are 2-12 chars)
    if len(token_lower) < 2 or len(token_lower) > 12:
        return False

    # Reject repeated consonant clusters (rare/invalid in Voynich)
    if any(c * 2 in token_lower for c in 'bcdfghjklmnpqrstvwxz'):
        return False

    # Must contain at least one known Voynich vowel pattern
    vowel_patterns = {'ai', 'ee', 'ii', 'oi', 'ei'}
    has_vowel = any(v in token_lower for v in vowel_patterns) or \
                token_lower.endswith('y') or \
                'a' in token_lower or 'o' in token_lower

    if not has_vowel:
        return False

    # Passes conservative checks
    return True


def _classify_residual_token(token: str) -> str:
    """
    Classify tokens that failed A validation into residual categories.

    Returns: 'INVALID_TRUE', 'DAMAGED_OR_TRUNCATED', or 'FORMED_NON_SYSTEM'

    Key principle: Not belonging to a system != being invalid glyphs.
    C240 stays frozen - these are NOT promoted to A.
    """
    token_lower = token.lower()

    # INVALID_TRUE: garbage, lone glyphs not in any system
    if len(token) == 1 and token not in 'yfdr':  # Single non-HT char
        return 'INVALID_TRUE'
    if _is_garbage_pattern(token):
        return 'INVALID_TRUE'

    # DAMAGED_OR_TRUNCATED: close to valid A forms
    if _is_near_valid_a(token):
        return 'DAMAGED_OR_TRUNCATED'

    # FORMED_NON_SYSTEM: well-formed Voynich but non-A
    if _is_voynich_wellformed(token):
        return 'FORMED_NON_SYSTEM'

    # Default to INVALID_TRUE for anything else
    return 'INVALID_TRUE'


def _classify_clean_token(token: str, folio_system: str) -> str:
    """
    Classify a token (without uncertainty markers) into a primary system.
    Helper function for get_token_primary_system().

    Returns one of: 'A', 'A_UNDERSPECIFIED', 'B', 'AZC', 'HT', 'INVALID'
    """
    if not token:
        return 'INVALID'

    token_lower = token.lower()

    # HT carrier precedence: 'y' is a productive HT carrier morpheme
    if token_lower.startswith('y'):
        return 'HT'

    # Other HT single-char atoms (f, d, r) per C404-406
    if len(token) == 1 and token in 'fdr':
        return 'HT'

    # Non-y HT prefixes (future-proofing)
    if len(token) >= 2 and token_lower[:2] in HT_PREFIXES:
        return 'HT'

    # System-specific validation (for non-HT tokens)
    if folio_system == 'A':
        # Two-gate validation: C240 prefix legality + C267 morphology
        result = parse_currier_a_token(token)

        if not result.is_prefix_legal:
            return _classify_residual_token(token)

        # Valid prefix - determine A sub-state
        if result.a_status in (AStatus.VALID_REGISTRY_ENTRY, AStatus.VALID_MINIMAL):
            return 'A'
        elif result.a_status == AStatus.UNDERSPECIFIED:
            return 'A_UNDERSPECIFIED'
        elif result.a_status == AStatus.AMBIGUOUS_MORPHOLOGY:
            return 'A'  # Ambiguous but still valid
        else:
            # PREFIX_VALID_MORPH_INCOMPLETE - should not happen now, but fallback
            return 'A_UNDERSPECIFIED'

    elif folio_system == 'B':
        return 'B'

    elif folio_system == 'AZC':
        return 'AZC'

    return 'INVALID'


def get_token_primary_system(token: str, folio_system: str) -> str:
    """
    Determine the primary system for a token given folio context.

    Returns one of:
    - 'A', 'A_UNDERSPECIFIED' - Currier A tokens
    - 'B' - Currier B tokens
    - 'AZC' - AZC annotation tokens
    - 'HT' - Human Track tokens
    - 'INVALID' - Truly invalid (no valid prefix)
    - 'A-UNCERTAIN', 'B-UNCERTAIN', 'HT-UNCERTAIN', 'UNCERTAIN' - Contains transcription uncertainty

    Rules:
    - Tokens with '*' are classified as X-UNCERTAIN (orthogonal to system)
    - HT tokens (y-prefixed per C404-406) are HT regardless of folio
    - On A folios: valid prefix = valid A (may be UNDERSPECIFIED if no clear suffix)
    - On B folios: tokens are valid B (execution grammar context)
    - On AZC folios: tokens are valid AZC (diagram annotation context)
    """
    # Check for transcription uncertainty FIRST
    # Key principle: UNCERTAINTY != INVALIDITY
    if '*' in token:
        clean_token = token.replace('*', '')
        if not clean_token:
            return 'UNCERTAIN'

        # Try to classify the clean form
        base_system = _classify_clean_token(clean_token, folio_system)

        # Return X-UNCERTAIN (preserving base system info)
        if base_system == 'INVALID':
            return 'UNCERTAIN'  # Truly unclassifiable
        elif base_system.startswith('A'):
            return 'A-UNCERTAIN'
        elif base_system == 'B':
            return 'B-UNCERTAIN'
        elif base_system == 'HT':
            return 'HT-UNCERTAIN'
        elif base_system == 'AZC':
            return 'AZC-UNCERTAIN'
        else:
            return 'UNCERTAIN'

    # Normal classification (no uncertainty marker)
    return _classify_clean_token(token, folio_system)


def segment_word(word: str) -> Tuple[str, str, str]:
    """Segment word into (prefix, core, suffix). C267, C240, C349."""
    if not word:
        return ('', '', '')

    prefix = ''
    suffix = ''
    word_lower = word.lower()

    # Check extended prefixes (3-char, C349) before standard (2-char, C240)
    if len(word) >= 3 and word_lower[:3] in EXTENDED_PREFIXES:
        prefix = word[:3]
    elif len(word) >= 2 and word_lower[:2] in KNOWN_PREFIXES:
        prefix = word[:2]

    remainder = word[len(prefix):]
    for suf_len in [4, 3, 2, 1]:
        if len(remainder) >= suf_len and remainder[-suf_len:].lower() in KNOWN_SUFFIXES:
            suffix = remainder[-suf_len:]
            break

    core_end = len(word) - len(suffix) if suffix else len(word)
    core = word[len(prefix):core_end]

    return (prefix, core, suffix)


# =============================================================================
# TOKEN CLASSIFICATION
# =============================================================================

def get_token_classification(token: str) -> str:
    """Get classification for a token (Classification mode)."""
    token_lower = token.lower()

    # Check LINK first (highest priority for structural visibility)
    if token_lower in LINK_TOKENS:
        return 'link'

    # Check Human Track
    if len(token) == 1 and token in 'yfdr':
        return 'human_track'
    if len(token) >= 2 and token_lower[:2] in HT_PREFIXES:
        return 'human_track'

    # Check A/B enrichment
    if token_lower in A_ENRICHED_TOKENS:
        return 'a_enriched'
    if token_lower in B_ENRICHED_TOKENS:
        return 'b_enriched'

    return 'neutral'


def get_kernel_contact(token: str) -> str:
    """Get kernel contact classification (Kernel mode). C372, C397."""
    token_lower = token.lower()
    prefix = token_lower[:2] if len(token) >= 2 else ''

    if prefix == ESCAPE_PREFIX:
        return 'escape'
    if prefix in KERNEL_HEAVY_PREFIXES:
        return 'heavy'
    if prefix in KERNEL_LIGHT_PREFIXES:
        return 'light'

    return 'neutral'


def get_position_markers(token: str, is_first: bool, is_last: bool) -> Tuple[bool, bool]:
    """Check if token has line-initial or line-final enrichment. C371, C375."""
    token_lower = token.lower()
    prefix = token_lower[:2] if len(token) >= 2 else ''

    has_initial_marker = is_first and prefix in LINE_INITIAL_PREFIXES

    # Check suffix for line-final
    has_final_marker = False
    if is_last:
        for suffix in LINE_FINAL_SUFFIXES:
            if token_lower.endswith(suffix):
                has_final_marker = True
                break

    return (has_initial_marker, has_final_marker)


# =============================================================================
# CLICKABLE TOKEN LABEL
# =============================================================================

class ClickableLabel(QLabel):
    """Label that emits signal when clicked and doesn't clip glyph descenders.

    Standard QLabel clips content at widget boundaries, which cuts off descenders
    for custom fonts like Voynich EVA. This subclass overrides paintEvent to
    render text with proper vertical space.
    """
    clicked = pyqtSignal(str, int, int)  # token_text, line_num, tok_idx

    def __init__(self, text: str, line_num: int, tok_idx: int, parent=None):
        super().__init__(text, parent)
        self._token_text = text
        self._line_num = line_num
        self._tok_idx = tok_idx
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._token_text, self._line_num, self._tok_idx)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        """Custom paint that doesn't clip descenders."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background/border via stylesheet (this handles the styled appearance)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        # Draw the text centered vertically with room for descenders
        painter.setFont(self.font())

        # Get the text color from the stylesheet/palette
        painter.setPen(self.palette().color(QPalette.WindowText))

        # Calculate text rect - use full widget rect for centering
        text_rect = self.contentsRect()

        # Draw text vertically centered
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignHCenter, self.text())


# =============================================================================
# TRANSCRIPTION PANEL
# =============================================================================

class TranscriptionPanel(QFrame):
    """
    Panel displaying EVA transcription with classification-based highlighting.

    Emits token_selected signal when user clicks a token.
    """

    token_selected = pyqtSignal(str, int, int)  # token_text, line_num, tok_idx

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._transcription: Optional[FolioTranscription] = None
        self._view_mode = ViewMode.B_INSTRUCTION  # Default to B instruction mode
        self._selected_token: Optional[Tuple[int, int]] = None  # (line, idx)
        self._use_glyphs = False

        self._token_labels: Dict[Tuple[int, int], ClickableLabel] = {}
        self._token_texts: Dict[Tuple[int, int], str] = {}
        self._token_primary_systems: Dict[Tuple[int, int], str] = {}  # Cache per-token system
        self._scroll_area: Optional[QScrollArea] = None
        self._folio_system: str = 'B'  # Default to B; set by main_window

        # Core modules for tooltips
        self._grammar = Grammar()
        self._constraints = ConstraintLoader()

        # Enable keyboard focus for arrow key navigation
        self.setFocusPolicy(Qt.StrongFocus)

    def _setup_ui(self):
        """Set up the transcription display."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        header = QLabel("TRANSCRIPTION")
        header.setFont(QFont("Consolas", 10, QFont.Bold))
        header.setStyleSheet("color: #C9A227; padding: 5px;")
        layout.addWidget(header)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: {CHROME['background']}; border: 1px solid {CHROME['separator']}; }}
            QScrollBar:vertical {{ background-color: {CHROME['background']}; width: 12px; }}
            QScrollBar::handle:vertical {{ background-color: {CHROME['separator']}; border-radius: 4px; min-height: 20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.text_container = QWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        self.text_layout.setContentsMargins(10, 10, 10, 10)
        self.text_layout.setSpacing(2)
        self.text_layout.addStretch()

        self._scroll_area.setWidget(self.text_container)
        layout.addWidget(self._scroll_area)

        # Install event filter to intercept arrow keys before scroll area handles them
        self._scroll_area.installEventFilter(self)

        self.setStyleSheet(f"""
            QFrame {{ background-color: {CHROME['background']}; border: 2px solid {CHROME['separator']}; border-radius: 5px; }}
        """)

    def set_transcription(self, transcription: FolioTranscription):
        """Set the transcription to display."""
        self._transcription = transcription
        self._selected_token = None
        self._rebuild_display()

    def set_view_mode(self, mode: ViewMode):
        """Change the visualization mode."""
        self._view_mode = mode
        self._update_token_colors()

    def set_use_glyphs(self, use_glyphs: bool):
        """Toggle glyph display mode."""
        self._use_glyphs = use_glyphs
        self._rebuild_display()

    def set_folio_system(self, system: str):
        """Set the Currier system for the current folio (A, B, or AZC).

        This determines primary system classification for tokens.
        Must be called before set_transcription() or will use default 'B'.
        """
        self._folio_system = system
        # Rebuild if we already have content (system change affects coloring)
        if self._transcription:
            self._rebuild_display()

    def _rebuild_display(self):
        """Rebuild the transcription display."""
        self._token_labels.clear()
        self._token_texts.clear()
        self._token_primary_systems.clear()

        # Clear existing widgets
        while self.text_layout.count() > 1:
            item = self.text_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._transcription:
            return

        for line in self._transcription.lines:
            line_widget = self._create_line_widget(line)
            self.text_layout.insertWidget(self.text_layout.count() - 1, line_widget)

        self._update_token_colors()

    def _create_line_widget(self, line) -> QWidget:
        """Create a widget for a single transcription line."""
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)  # Minimal margins, height comes from labels
        layout.setSpacing(4)

        # Line number
        num_label = QLabel(f"{line.line_number:02d}")
        num_label.setFont(QFont("Consolas", 9))
        num_label.setStyleSheet(f"color: {CHROME['line_number']}; min-width: 25px;")
        layout.addWidget(num_label)

        sep = QLabel("|")
        sep.setStyleSheet(f"color: {CHROME['separator']};")
        layout.addWidget(sep)

        # Token container
        token_container = QWidget()
        token_layout = QHBoxLayout(token_container)
        token_layout.setContentsMargins(0, 0, 0, 0)
        token_layout.setSpacing(6)

        tokens = re.split(r'[.\s]+', line.text)
        tokens = [t for t in tokens if t]

        font = QFont("Voynich EVA", 20) if self._use_glyphs else QFont("Consolas", 11)

        for tok_idx, token_text in enumerate(tokens):
            is_first = (tok_idx == 0)
            is_last = (tok_idx == len(tokens) - 1)
            # Get placement from line data (C306 topological class)
            placement = line.get_placement(tok_idx) if hasattr(line, 'get_placement') else 'UNKNOWN'
            token_label = self._create_token_label(
                token_text, line.line_number, tok_idx, font, is_first, is_last, placement
            )
            token_layout.addWidget(token_label)

        token_layout.addStretch()
        layout.addWidget(token_container, stretch=1)

        widget.setStyleSheet(f"QFrame {{ background-color: {CHROME['line_bg']}; border: none; border-radius: 3px; }}")
        return widget

    def _create_token_label(self, token_text: str, line_num: int, tok_idx: int,
                            font: QFont, is_first: bool, is_last: bool,
                            placement: str = 'UNKNOWN') -> ClickableLabel:
        """Create a clickable token label."""
        label = ClickableLabel(token_text, line_num, tok_idx)
        label.setFont(font)
        label.clicked.connect(self._on_token_clicked)
        # Alignment handled in custom paintEvent - no setAlignment() needed

        # Calculate height based on font metrics to ensure descenders fit
        fm = QFontMetrics(font)
        needed_height = fm.height() + fm.descent() + 16  # height + extra descent room + padding
        label.setMinimumWidth(20)
        label.setMinimumHeight(needed_height)

        self._token_labels[(line_num, tok_idx)] = label
        self._token_texts[(line_num, tok_idx)] = token_text
        # Cache primary system for system-aware coloring
        self._token_primary_systems[(line_num, tok_idx)] = get_token_primary_system(
            token_text, self._folio_system
        )

        # Store position info for Position mode
        label.setProperty("is_first", is_first)
        label.setProperty("is_last", is_last)
        # Store placement info for AZC Placement mode (C306)
        label.setProperty("placement", placement)

        # No tooltips - all info goes to detail panel
        return label

    def _on_token_clicked(self, token_text: str, line_num: int, tok_idx: int):
        """Handle token click."""
        old_selection = self._selected_token
        self._selected_token = (line_num, tok_idx)

        # Update old selection appearance
        if old_selection and old_selection in self._token_labels:
            self._apply_token_style(old_selection, selected=False)

        # Update new selection appearance
        self._apply_token_style(self._selected_token, selected=True)

        # Grab focus for arrow key navigation
        self.setFocus()

        # Emit signal for external handlers
        self.token_selected.emit(token_text, line_num, tok_idx)

    def eventFilter(self, obj, event):
        """Intercept arrow keys from scroll area before it handles them for scrolling."""
        from PyQt5.QtCore import QEvent
        if obj == self._scroll_area and event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                # Only intercept if we have tokens and a selection
                if self._token_labels and self._selected_token is not None:
                    self.keyPressEvent(event)
                    return True  # Event handled, don't let scroll area process it
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """Handle arrow key navigation between tokens."""
        try:
            if not self._token_labels:
                return super().keyPressEvent(event)

            key = event.key()
            if key not in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                return super().keyPressEvent(event)

            # Accept the event to prevent scroll area from handling it
            event.accept()

            # Get sorted line numbers and tokens per line
            all_keys = sorted(self._token_labels.keys())
            if not all_keys:
                return

            lines = sorted(set(k[0] for k in all_keys))
            tokens_by_line = {ln: sorted(k[1] for k in all_keys if k[0] == ln) for ln in lines}

            # If no selection, start at first token
            if self._selected_token is None or self._selected_token not in self._token_labels:
                new_key = all_keys[0]
            else:
                line_num, tok_idx = self._selected_token
                line_tokens = tokens_by_line.get(line_num, [])
                line_idx = lines.index(line_num) if line_num in lines else 0

                if key == Qt.Key_Left:
                    # Previous token in same line
                    if tok_idx in line_tokens:
                        pos = line_tokens.index(tok_idx)
                        if pos > 0:
                            new_key = (line_num, line_tokens[pos - 1])
                        else:
                            new_key = self._selected_token  # Stay put
                    else:
                        new_key = self._selected_token

                elif key == Qt.Key_Right:
                    # Next token in same line
                    if tok_idx in line_tokens:
                        pos = line_tokens.index(tok_idx)
                        if pos < len(line_tokens) - 1:
                            new_key = (line_num, line_tokens[pos + 1])
                        else:
                            new_key = self._selected_token  # Stay put
                    else:
                        new_key = self._selected_token

                elif key == Qt.Key_Up:
                    # First token of previous line
                    if line_idx > 0:
                        prev_line = lines[line_idx - 1]
                        new_key = (prev_line, tokens_by_line[prev_line][0])
                    else:
                        new_key = self._selected_token  # Stay put

                elif key == Qt.Key_Down:
                    # First token of next line
                    if line_idx < len(lines) - 1:
                        next_line = lines[line_idx + 1]
                        new_key = (next_line, tokens_by_line[next_line][0])
                    else:
                        new_key = self._selected_token  # Stay put
                else:
                    new_key = self._selected_token

            # Select the new token
            if new_key and new_key in self._token_texts:
                token_text = self._token_texts[new_key]
                self._on_token_clicked(token_text, new_key[0], new_key[1])

                # Ensure selected token is visible in scroll area
                if new_key in self._token_labels and self._scroll_area:
                    label = self._token_labels[new_key]
                    if label and not label.isHidden():
                        self._scroll_area.ensureWidgetVisible(label, 50, 50)
        except Exception as e:
            import traceback
            print(f"Arrow key navigation error: {e}")
            traceback.print_exc()

    def _update_token_colors(self):
        """Update all token colors based on current view mode."""
        for key, label in self._token_labels.items():
            is_selected = (key == self._selected_token)
            self._apply_token_style(key, selected=is_selected)

    def _apply_token_style(self, key: Tuple[int, int], selected: bool = False):
        """Apply styling to a token based on view mode and selection state."""
        if key not in self._token_labels:
            return

        label = self._token_labels[key]
        token_text = self._token_texts.get(key, "")

        try:
            # Get background color based on view mode
            bg_color = self._get_background_color(token_text, label)

            # Check primary system for special styling
            primary_system = self._token_primary_systems.get(key, 'INVALID_TRUE')
            if not isinstance(primary_system, str):
                print(f"ERROR: primary_system is not string for {token_text}: {type(primary_system)} = {primary_system}")
                primary_system = 'INVALID_TRUE'
            is_ht = primary_system in ('HT', 'HT-UNCERTAIN')
            is_uncertain = 'UNCERTAIN' in primary_system
            # Text color
            text_color = TEXT_COLORS['selected'] if selected else TEXT_COLORS['default']

            # Build style - symmetric padding (custom paintEvent handles descenders)
            if bg_color == 'transparent':
                style = f"color: {text_color}; background: transparent; padding: 6px; border-radius: 3px;"
            else:
                style = f"color: {text_color}; background-color: {bg_color}; padding: 6px; border-radius: 3px;"

            # HT text styling: italic + dotted underline (orthogonal to grammar, per expert guidance)
            # HT = Human-Track: non-operational, non-executing tokens (C404-406)
            if is_ht:
                style += " font-style: italic; text-decoration: underline; text-decoration-style: dotted;"

            # UNCERTAIN tokens: reduced opacity (transcription uncertainty)
            # Key principle: UNCERTAINTY != INVALIDITY
            if is_uncertain:
                style += " opacity: 0.7;"
                label.setToolTip("Contains transcription uncertainty (*)")
            else:
                label.setToolTip("")  # Clear tooltip

            # Selection border - use background color when not selected to avoid layout shift
            # UNCERTAIN tokens get dotted border to indicate uncertainty
            if selected:
                style += f" border: 2px solid {SELECTION['ring_color']};"
            elif is_uncertain:
                style += f" border: 2px dotted #6A6A7A;"  # Dotted border for uncertainty
            else:
                # Match border to background so it's invisible but reserves space
                border_color = bg_color if bg_color != 'transparent' else CHROME['background']
                style += f" border: 2px solid {border_color};"

            label.setStyleSheet(style)
            label.setCursor(Qt.PointingHandCursor)  # Ensure cursor persists
        except Exception as e:
            print(f"ERROR styling token '{token_text}' at {key}: {e}")
            import traceback
            traceback.print_exc()

    def _get_background_color(self, token_text: str, label: ClickableLabel) -> str:
        """Get background color for token based on current view mode.

        SYSTEM-AWARE COLORING:
        - System-specific modes (A_*, B_*, AZC_*) only color tokens belonging to that system
        - Tokens not belonging to the mode's system get 'transparent'
        - Global modes (MORPHOLOGY, KERNEL_AFFINITY, LINK_AFFINITY) color all tokens
        - HT and INVALID tokens are transparent in system-specific modes
        """
        # Get cached primary system for this token
        token_key = (label._line_num, label._tok_idx)
        primary_system = self._token_primary_systems.get(token_key, 'INVALID')

        # Strip transcription uncertainty markers for marker lookups
        # Classification already handled * in get_token_primary_system()
        clean_token = token_text.replace('*', '')

        # === GLOBAL MODES (valid in all systems) ===
        if self._view_mode == ViewMode.PLAIN:
            return 'transparent'

        elif self._view_mode == ViewMode.MORPHOLOGY:
            prefix = get_token_prefix_family(clean_token)
            return MORPHOLOGY_COLORS.get(prefix, MORPHOLOGY_COLORS['other'])

        elif self._view_mode == ViewMode.KERNEL_AFFINITY:
            affinity = get_kernel_affinity(clean_token)
            return KERNEL_AFFINITY_COLORS.get(affinity, 'transparent')

        elif self._view_mode == ViewMode.LINK_AFFINITY:
            affinity = get_link_affinity(clean_token)
            return LINK_AFFINITY_COLORS.get(affinity, 'transparent')

        # === CURRIER B MODES (execution grammar) ===
        # Color tokens with primary_system in ('B', 'B-UNCERTAIN')
        # B-UNCERTAIN styling (opacity, dotted border) handled in _apply_token_style
        elif self._view_mode == ViewMode.B_INSTRUCTION:
            if not primary_system.startswith('B'):
                return 'transparent'
            role = get_token_instruction_role(clean_token)
            return B_INSTRUCTION_COLORS.get(role, B_INSTRUCTION_COLORS['UNKNOWN'])

        elif self._view_mode == ViewMode.B_POSITION:
            if not primary_system.startswith('B'):
                return 'transparent'
            # Check line position
            is_first = label.property("is_first")
            is_last = label.property("is_last")
            has_initial, has_final = get_position_markers(clean_token, is_first, is_last)

            if has_initial:
                return B_POSITION_COLORS['initial']
            elif has_final:
                return B_POSITION_COLORS['final']
            elif clean_token.lower() in LINK_TOKENS:
                return B_POSITION_COLORS['link']
            return 'transparent'

        elif self._view_mode == ViewMode.B_KERNEL_CONTACT:
            if not primary_system.startswith('B'):
                return 'transparent'
            contact = get_kernel_contact(clean_token)
            return B_KERNEL_CONTACT_COLORS.get(contact, 'transparent')

        elif self._view_mode == ViewMode.B_EXECUTION:
            # Composite execution view: kernel contact + position + LINK
            if not primary_system.startswith('B'):
                return 'transparent'
            # Primary color: kernel contact (execution's central axis)
            contact = get_kernel_contact(clean_token)
            return B_EXECUTION_COLORS.get(contact, 'transparent')

        # === CURRIER A MODES (categorical registry) ===
        # Color tokens with primary_system in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')
        # A_UNDERSPECIFIED gets muted color; A-UNCERTAIN styling handled in _apply_token_style
        # Residual categories (non-A) get their own distinct colors
        elif self._view_mode == ViewMode.A_MARKER:
            # Handle residual categories (tokens that failed A validation)
            if primary_system in ('DAMAGED_OR_TRUNCATED', 'FORMED_NON_SYSTEM', 'INVALID_TRUE'):
                return STATE_COLORS.get(primary_system, '#2A2A2A')
            if not primary_system.startswith('A'):
                return 'transparent'
            # A_UNDERSPECIFIED gets muted grey-olive
            if primary_system == 'A_UNDERSPECIFIED':
                return STATE_COLORS['A_UNDERSPECIFIED']
            marker = get_a_marker_family(clean_token)
            return A_MARKER_COLORS.get(marker, A_MARKER_COLORS['other'])

        elif self._view_mode == ViewMode.A_SISTER:
            # Handle residual categories (tokens that failed A validation)
            if primary_system in ('DAMAGED_OR_TRUNCATED', 'FORMED_NON_SYSTEM', 'INVALID_TRUE'):
                return STATE_COLORS.get(primary_system, '#2A2A2A')
            if not primary_system.startswith('A'):
                return 'transparent'
            if primary_system == 'A_UNDERSPECIFIED':
                return STATE_COLORS['A_UNDERSPECIFIED']
            sister = get_a_sister_pair(clean_token)
            return A_SISTER_COLORS.get(sister, A_SISTER_COLORS['other'])

        elif self._view_mode == ViewMode.A_ROLE:
            # Handle residual categories (tokens that failed A validation)
            if primary_system in ('DAMAGED_OR_TRUNCATED', 'FORMED_NON_SYSTEM', 'INVALID_TRUE'):
                return STATE_COLORS.get(primary_system, '#2A2A2A')
            if not primary_system.startswith('A'):
                return 'transparent'
            if primary_system == 'A_UNDERSPECIFIED':
                return STATE_COLORS['A_UNDERSPECIFIED']
            role = get_a_token_role(clean_token)
            return A_ROLE_COLORS.get(role, A_ROLE_COLORS['REGISTRY_ENTRY'])

        elif self._view_mode == ViewMode.A_MULTIPLICITY:
            # Handle residual categories (tokens that failed A validation)
            if primary_system in ('DAMAGED_OR_TRUNCATED', 'FORMED_NON_SYSTEM', 'INVALID_TRUE'):
                return STATE_COLORS.get(primary_system, '#2A2A2A')
            if not primary_system.startswith('A'):
                return 'transparent'
            if primary_system == 'A_UNDERSPECIFIED':
                return STATE_COLORS['A_UNDERSPECIFIED']
            return MORPHOLOGY_COLORS.get(get_token_prefix_family(clean_token), '#4A4A4A')

        # === AZC MODES (diagram annotation) ===
        # Color tokens with primary_system in ('AZC', 'AZC-UNCERTAIN')
        elif self._view_mode == ViewMode.AZC_PLACEMENT:
            if not primary_system.startswith('AZC'):
                return 'transparent'
            placement = label.property("placement") or ""
            group = get_azc_placement_group(placement)
            return AZC_PLACEMENT_COLORS.get(group, AZC_PLACEMENT_COLORS['other'])

        elif self._view_mode == ViewMode.AZC_LEGALITY:
            if not primary_system.startswith('AZC'):
                return 'transparent'
            return '#4A4A4A'

        return 'transparent'

    def get_selected_token(self) -> Optional[Tuple[str, int, int]]:
        """Get currently selected token info."""
        if self._selected_token and self._selected_token in self._token_texts:
            line, idx = self._selected_token
            return (self._token_texts[self._selected_token], line, idx)
        return None

    def get_unique_tokens(self) -> set:
        """Get deduplicated set of all surface token strings in current folio.
        Order is intentionally undefined - avoids false ordering signal."""
        return set(self._token_texts.values()) if self._token_texts else set()

    def get_token_placements(self) -> Dict[str, List[str]]:
        """Get placement codes for each unique token in current folio.

        Returns dict mapping token text → list of placements (may have duplicates
        if same token appears multiple times with same placement).

        This supports AZC placement binding (C306) in the export.
        """
        result: Dict[str, List[str]] = {}
        for key, token_text in self._token_texts.items():
            label = self._token_labels.get(key)
            if label:
                placement = label.property("placement") or 'UNKNOWN'
                if token_text not in result:
                    result[token_text] = []
                result[token_text].append(placement)
        return result


# =============================================================================
# FOLIO VIEWER
# =============================================================================

class FolioViewer(QWidget):
    """
    Complete folio viewer with transcription panel.

    Supports view mode switching and click-to-select interaction.
    """

    token_selected = pyqtSignal(str, int, int)  # Forwarded from TranscriptionPanel

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transcription_loader = TranscriptionLoader()
        self._current_folio_id = ""
        self._setup_ui()
        self._load_transcriptions()

    def _setup_ui(self):
        """Set up the folio viewer."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.transcription_panel = TranscriptionPanel()
        self.transcription_panel.token_selected.connect(self.token_selected.emit)
        layout.addWidget(self.transcription_panel)

        self.setStyleSheet(f"QWidget {{ background-color: {CHROME['background']}; }}")

    def _load_transcriptions(self):
        """Load transcription data."""
        paths = [
            Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt"),
            Path("./data/transcriptions/interlinear_full_words.txt"),
            Path(__file__).parent.parent.parent.parent / "data" / "transcriptions" / "interlinear_full_words.txt"
        ]

        for path in paths:
            if path.exists():
                self._transcription_loader.load_interlinear(str(path))
                break

    def load_folio(self, folio_id: str):
        """Load a folio for display."""
        self._current_folio_id = folio_id
        transcription = self._transcription_loader.get_folio(folio_id)
        if transcription:
            self.transcription_panel.set_transcription(transcription)

    def set_view_mode(self, mode: ViewMode):
        """Change the visualization mode."""
        self.transcription_panel.set_view_mode(mode)

    def set_use_glyphs(self, use_glyphs: bool):
        """Toggle glyph display mode."""
        self.transcription_panel.set_use_glyphs(use_glyphs)

    def set_folio_system(self, system: str):
        """Set the Currier system for the current folio (A, B, or AZC).

        Must be called BEFORE load_folio() for correct system-aware coloring.
        """
        self.transcription_panel.set_folio_system(system)

    def get_folio_ids(self) -> List[str]:
        """Get list of available folio IDs."""
        return self._transcription_loader.get_folio_ids()
