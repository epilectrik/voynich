#!/usr/bin/env python3
"""
Voynich Manuscript Analysis Library

Canonical interface for working with the transcript.
Use this in all analysis scripts to ensure consistent methodology.

Usage:
    from scripts.voynich import Transcript, Morphology

    # Load transcript
    tx = Transcript()
    for token in tx.currier_a():
        print(token.word, token.folio)

    # Morphological analysis
    morph = Morphology()
    prefix, middle, suffix = morph.extract(token.word)
"""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Iterator, List, Set, Tuple, Dict
from collections import Counter

# ============================================================
# PATHS
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# ============================================================
# CANONICAL MORPHOLOGY (from constraints)
# ============================================================

# C235: 8 core prefix markers (no gallows letters - p, t, k, f)
# Note: Gallows-initial sequences (cph, cfh, ckh, etc.) are PREFIX-FORBIDDEN
# MIDDLEs per C528, not missing prefixes. They correctly parse as prefixless.
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Extended prefixes (compound forms)
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
    'lk', 'yk', 'lsh',
    'ke', 'te', 'se', 'de', 'pe',
    'ko', 'to', 'so', 'do', 'po',
    'ka', 'ta', 'sa',
    'al', 'ar', 'or',
]

# C291: Articulators (optional, before prefix)
ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']

# All prefixes combined
ALL_PREFIXES = sorted(set(CORE_PREFIXES + EXTENDED_PREFIXES), key=len, reverse=True)

# Atomic suffix list (revised per expert analysis 2026-01-24)
# Previous compound suffixes (chol, shol, daiin, etc.) were over-specified
# and caused 52.9% empty-MIDDLE rate, violating C293/C267.a/C475/C511.
# Now using only atomic forms - consonant-initial compounds moved to MIDDLE.
SUFFIXES = [
    # -iin family (vowel-initial, atomic)
    'aiin', 'oiin', 'eiin', 'iin',
    'ain', 'oin', 'ein',
    # -Vy patterns (vowel + y)
    'eey', 'edy', 'ey',
    # -Vl/-Vr patterns (vowel + liquid)
    'eeol', 'eol', 'ool',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    # -Vn patterns (vowel + nasal)
    'in', 'an', 'on', 'en',
    # -Vm patterns (vowel + m)
    'am', 'om', 'em', 'im',
    # Two-char -Cy (consonant + y, where C is NOT ch/sh/k/t)
    'dy', 'hy', 'ly', 'ry',
    # Single char (true atomics)
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)


# ============================================================
# TOKEN DATA CLASS
# ============================================================
@dataclass
class Token:
    """A single token from the transcript."""
    word: str
    folio: str
    line: str
    language: str
    transcriber: str
    placement: str
    section: str
    line_initial: bool
    line_final: bool
    par_initial: bool
    par_final: bool

    @property
    def is_label(self) -> bool:
        """Check if token is a label (illustration annotation)."""
        return self.placement.startswith('L') if self.placement else False

    @property
    def is_uncertain(self) -> bool:
        """Check if token contains uncertain reading."""
        return '*' in self.word


# ============================================================
# TRANSCRIPT INTERFACE
# ============================================================
class Transcript:
    """Interface for reading the Voynich transcript."""

    def __init__(self, path: Path = DATA_PATH):
        self.path = path
        self._tokens: Optional[List[Token]] = None

    def _load(self) -> List[Token]:
        """Load all tokens from transcript."""
        if self._tokens is not None:
            return self._tokens

        tokens = []
        with open(self.path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                tokens.append(Token(
                    word=row.get('word', '').strip(),
                    folio=row.get('folio', '').strip(),
                    line=row.get('line_number', '').strip(),
                    language=row.get('language', '').strip(),
                    transcriber=row.get('transcriber', '').strip().strip('"'),
                    placement=row.get('placement', '').strip(),
                    section=row.get('section', '').strip(),
                    line_initial=row.get('line_initial', '').strip() == '1',
                    line_final=row.get('line_final', '').strip() == '1',
                    par_initial=row.get('par_initial', '').strip() == '1',
                    par_final=row.get('par_final', '').strip() == '1',
                ))
        self._tokens = tokens
        return tokens

    def all(self, h_only: bool = True) -> Iterator[Token]:
        """
        Iterate all tokens.

        Args:
            h_only: If True (default), filter to H transcriber only.
                    This is MANDATORY for most analyses per CLAUDE.md.
        """
        for token in self._load():
            if h_only and token.transcriber != 'H':
                continue
            yield token

    def currier_a(self, h_only: bool = True, exclude_labels: bool = True,
                  exclude_uncertain: bool = True) -> Iterator[Token]:
        """
        Iterate Currier A tokens.

        Args:
            h_only: Filter to H transcriber (default True)
            exclude_labels: Exclude label tokens (default True)
            exclude_uncertain: Exclude tokens with * (default True)
        """
        for token in self.all(h_only=h_only):
            if token.language != 'A':
                continue
            if exclude_labels and token.is_label:
                continue
            if exclude_uncertain and token.is_uncertain:
                continue
            if not token.word:
                continue
            yield token

    def currier_b(self, h_only: bool = True, exclude_labels: bool = True,
                  exclude_uncertain: bool = True) -> Iterator[Token]:
        """Iterate Currier B tokens."""
        for token in self.all(h_only=h_only):
            if token.language != 'B':
                continue
            if exclude_labels and token.is_label:
                continue
            if exclude_uncertain and token.is_uncertain:
                continue
            if not token.word:
                continue
            yield token

    def azc(self, h_only: bool = True) -> Iterator[Token]:
        """Iterate AZC tokens (language=NA)."""
        for token in self.all(h_only=h_only):
            if token.language != 'NA':
                continue
            if not token.word:
                continue
            yield token


# ============================================================
# MORPHOLOGY INTERFACE
# ============================================================
@dataclass
class MorphAnalysis:
    """Result of morphological analysis."""
    articulator: Optional[str]
    prefix: Optional[str]
    middle: Optional[str]
    suffix: Optional[str]

    @property
    def has_prefix(self) -> bool:
        return self.prefix is not None

    @property
    def has_articulator(self) -> bool:
        return self.articulator is not None

    @property
    def is_empty_middle(self) -> bool:
        return self.middle == '_EMPTY_'


class Morphology:
    """
    Morphological analysis following canonical methodology.

    Structure: [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]

    The articulator is optional and comes BEFORE the prefix (C291).
    """

    def __init__(self,
                 prefixes: List[str] = None,
                 suffixes: List[str] = None,
                 articulators: List[str] = None,
                 require_prefix: bool = False):
        """
        Initialize morphology analyzer.

        Args:
            prefixes: Custom prefix list (default: ALL_PREFIXES)
            suffixes: Custom suffix list (default: SUFFIXES)
            articulators: Custom articulator list (default: ARTICULATORS)
            require_prefix: If True, tokens without prefix return None middle
        """
        self.prefixes = sorted(prefixes or ALL_PREFIXES, key=len, reverse=True)
        self.suffixes = sorted(suffixes or SUFFIXES, key=len, reverse=True)
        self.articulators = articulators or ARTICULATORS
        self.require_prefix = require_prefix

    def _find_prefix(self, token: str) -> Tuple[Optional[str], str]:
        """Find prefix in token, return (prefix, remainder)."""
        for p in self.prefixes:
            if token.startswith(p) and len(token) > len(p):
                return p, token[len(p):]
        return None, token

    def _find_suffix(self, token: str) -> Tuple[str, Optional[str]]:
        """Find suffix in token, return (remainder, suffix)."""
        for s in self.suffixes:
            # Use >= to allow suffix matching when it equals remainder
            # This gives middle='_EMPTY_' for pure suffix tokens
            if token.endswith(s) and len(token) >= len(s):
                remainder = token[:-len(s)] if len(token) > len(s) else ''
                return remainder, s
        return token, None

    def extract(self, token: str) -> MorphAnalysis:
        """
        Extract morphological components from token.

        Returns MorphAnalysis with articulator, prefix, middle, suffix.

        Per C293/C267.a, MIDDLE is the primary discriminator and should not
        be empty when avoidable. If prefix+suffix would consume everything,
        we try alternative parses that preserve a non-empty MIDDLE.
        """
        if not token:
            return MorphAnalysis(None, None, None, None)

        articulator = None
        prefix = None

        # Step 1: Try to find prefix directly
        prefix, remainder = self._find_prefix(token)

        # Step 2: If no prefix, check for articulator + prefix
        if prefix is None:
            for art in self.articulators:
                if token.startswith(art) and len(token) > len(art):
                    after_art = token[len(art):]
                    maybe_prefix, maybe_remainder = self._find_prefix(after_art)
                    if maybe_prefix is not None:
                        articulator = art
                        prefix = maybe_prefix
                        remainder = maybe_remainder
                        break

        # If require_prefix and still no prefix, return None middle
        if self.require_prefix and prefix is None:
            return MorphAnalysis(None, None, None, None)

        # If no prefix found, remainder is the whole token
        if prefix is None:
            remainder = token

        # Step 3: Extract suffix from remainder
        middle, suffix = self._find_suffix(remainder)

        # Step 4: Avoid empty MIDDLE when possible (per C293/C267.a)
        # If prefix+suffix consumed everything, try alternative parses
        if middle == '':
            # Option A: Drop suffix, treat remainder as pure MIDDLE
            alt_a = MorphAnalysis(articulator, prefix, remainder, None)

            # Option B: Drop prefix, treat token as MIDDLE+suffix
            if prefix is not None:
                no_prefix_mid, no_prefix_suf = self._find_suffix(token)
                if no_prefix_mid:
                    alt_b = MorphAnalysis(articulator, None, no_prefix_mid, no_prefix_suf)
                else:
                    alt_b = MorphAnalysis(articulator, None, token, None)
            else:
                alt_b = None

            # Option C: Drop both, treat token as pure MIDDLE
            alt_c = MorphAnalysis(articulator, None, token, None)

            # Prefer: non-empty MIDDLE with most structure preserved
            # Priority: prefix+MIDDLE > MIDDLE+suffix > pure MIDDLE
            if prefix is not None and remainder:
                return alt_a  # Keep prefix, MIDDLE=remainder, no suffix
            elif alt_b and alt_b.middle and alt_b.middle != token:
                return alt_b  # No prefix, but have MIDDLE+suffix
            else:
                return alt_c  # Pure MIDDLE, no affixes

        return MorphAnalysis(articulator, prefix, middle, suffix)

    def extract_tuple(self, token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract and return (prefix, middle, suffix) tuple for compatibility."""
        result = self.extract(token)
        return result.prefix, result.middle, result.suffix


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================
def load_middle_classes() -> Tuple[Set[str], Set[str]]:
    """
    Load RI and PP middle classifications.

    Returns:
        (ri_middles, pp_middles) - Sets of A-exclusive and A-shared middles
    """
    import json
    path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
    with open(path) as f:
        data = json.load(f)
    return set(data['a_exclusive_middles']), set(data['a_shared_middles'])


# ============================================================
# TOKEN CLASSIFICATION
# ============================================================
class TokenClass:
    """Token classification constants."""
    RI = 'RI'              # Registry-Internal (A-exclusive MIDDLE)
    PP = 'PP'              # Pipeline-Participant (A+B shared MIDDLE)
    INFRA = 'INFRA'        # Infrastructure (DA-family per C407)
    UNKNOWN = 'UNKNOWN'    # MIDDLE not in classification data


@dataclass
class TokenAnalysis:
    """Complete analysis of a single token."""
    word: str
    morph: MorphAnalysis
    token_class: str

    @property
    def middle(self) -> Optional[str]:
        return self.morph.middle

    @property
    def prefix(self) -> Optional[str]:
        return self.morph.prefix

    @property
    def suffix(self) -> Optional[str]:
        return self.morph.suffix

    @property
    def articulator(self) -> Optional[str]:
        return self.morph.articulator

    @property
    def is_ri(self) -> bool:
        return self.token_class == TokenClass.RI

    @property
    def is_pp(self) -> bool:
        return self.token_class == TokenClass.PP

    @property
    def is_infra(self) -> bool:
        return self.token_class == TokenClass.INFRA


@dataclass
class RecordAnalysis:
    """Analysis of a complete record (line)."""
    folio: str
    line: str
    tokens: List[TokenAnalysis]

    @property
    def ri_count(self) -> int:
        return sum(1 for t in self.tokens if t.is_ri)

    @property
    def pp_count(self) -> int:
        return sum(1 for t in self.tokens if t.is_pp)

    @property
    def infra_count(self) -> int:
        return sum(1 for t in self.tokens if t.is_infra)

    @property
    def ri_tokens(self) -> List[TokenAnalysis]:
        return [t for t in self.tokens if t.is_ri]

    @property
    def pp_tokens(self) -> List[TokenAnalysis]:
        return [t for t in self.tokens if t.is_pp]

    @property
    def composition(self) -> str:
        """Classify record composition per C498."""
        has_ri = self.ri_count > 0
        has_pp = self.pp_count > 0
        if has_ri and has_pp:
            return 'MIXED'
        elif has_ri:
            return 'PURE_RI'
        elif has_pp:
            return 'PURE_PP'
        else:
            return 'UNKNOWN'


class RecordAnalyzer:
    """
    Analyze Currier A records with full morphological and class breakdown.

    Usage:
        analyzer = RecordAnalyzer()
        record = analyzer.analyze_record('f1r', '1')
        for token in record.tokens:
            print(f"{token.word}: {token.token_class} (MID={token.middle})")
    """

    # Infrastructure prefixes per C407 (DA-family)
    INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}

    def __init__(self):
        self.transcript = Transcript()
        self.morphology = Morphology()
        self.ri_middles, self.pp_middles = load_middle_classes()
        self._records_cache: Optional[dict] = None

    def _build_records_cache(self):
        """Build cache of records indexed by (folio, line)."""
        if self._records_cache is not None:
            return

        self._records_cache = {}
        for token in self.transcript.currier_a(exclude_uncertain=False):
            key = (token.folio, token.line)
            if key not in self._records_cache:
                self._records_cache[key] = []
            self._records_cache[key].append(token)

    def classify_token(self, word: str, morph: MorphAnalysis) -> str:
        """Classify a token based on its MIDDLE."""
        middle = morph.middle
        prefix = morph.prefix

        # Infrastructure check: DA-family prefixes with simple structure
        if prefix in self.INFRA_PREFIXES:
            # Pure DA-family tokens are infrastructure per C407
            if middle and len(middle) <= 3:
                return TokenClass.INFRA

        # Check MIDDLE classification
        if middle in self.ri_middles:
            return TokenClass.RI
        elif middle in self.pp_middles:
            return TokenClass.PP
        else:
            return TokenClass.UNKNOWN

    def analyze_token(self, word: str) -> TokenAnalysis:
        """Analyze a single token."""
        morph = self.morphology.extract(word)
        token_class = self.classify_token(word, morph)
        return TokenAnalysis(word, morph, token_class)

    def analyze_record(self, folio: str, line: str) -> Optional[RecordAnalysis]:
        """Analyze a complete record (line)."""
        self._build_records_cache()

        key = (folio, line)
        if key not in self._records_cache:
            return None

        tokens = []
        for t in self._records_cache[key]:
            if t.word and not t.is_uncertain:
                analysis = self.analyze_token(t.word)
                tokens.append(analysis)

        return RecordAnalysis(folio, line, tokens)

    def analyze_folio(self, folio: str) -> List[RecordAnalysis]:
        """Analyze all records in a folio."""
        self._build_records_cache()

        records = []
        for (f, line) in sorted(self._records_cache.keys()):
            if f == folio:
                record = self.analyze_record(f, line)
                if record:
                    records.append(record)
        return records

    def get_folios(self) -> List[str]:
        """Get list of all Currier A folios."""
        self._build_records_cache()
        return sorted(set(f for f, _ in self._records_cache.keys()))

    def iter_records(self) -> Iterator[RecordAnalysis]:
        """Iterate all Currier A records."""
        self._build_records_cache()
        for key in sorted(self._records_cache.keys()):
            record = self.analyze_record(key[0], key[1])
            if record:
                yield record


# ============================================================
# MIDDLE ANALYZER (Compound Detection & Folio-Spread Analysis)
# ============================================================
@dataclass
class MiddleStats:
    """Statistics for a single MIDDLE."""
    middle: str
    token_count: int
    folio_count: int
    folios: Set[str]

    @property
    def is_folio_unique(self) -> bool:
        """True if MIDDLE appears in exactly one folio."""
        return self.folio_count == 1

    @property
    def is_core(self) -> bool:
        """True if MIDDLE appears in 20+ folios (highly shared)."""
        return self.folio_count >= 20

    @property
    def is_common(self) -> bool:
        """True if MIDDLE appears in 5+ folios."""
        return self.folio_count >= 5


class MiddleAnalyzer:
    """
    Analyzer for MIDDLE compound structure and folio distribution.

    Provides methods to:
    - Track MIDDLE inventory and folio spread
    - Detect compound MIDDLEs (containing core MIDDLEs as substrings)
    - Classify MIDDLEs by uniqueness (folio-unique, common, core)
    - Analyze compositional structure

    Usage:
        analyzer = MiddleAnalyzer()
        analyzer.build_inventory()  # Scans all B tokens

        # Check if a MIDDLE is compound
        if analyzer.is_compound('opcheodai'):
            atoms = analyzer.get_contained_atoms('opcheodai')
            print(f"Contains: {atoms}")

        # Get folio-unique MIDDLEs
        unique = analyzer.get_folio_unique_middles()

        # Get statistics for a specific MIDDLE
        stats = analyzer.get_stats('od')
        print(f"'od' appears in {stats.folio_count} folios")

    The compound detection is based on findings from the COMPOUND_MIDDLE_ARCHITECTURE
    phase, which established that folio-unique MIDDLEs are built by combining
    core operational MIDDLEs (84.8% contain core MIDDLEs, +29.9pp above chance).
    """

    def __init__(self, min_atom_length: int = 2, core_threshold: int = 20,
                 common_threshold: int = 5):
        """
        Initialize MiddleAnalyzer.

        Args:
            min_atom_length: Minimum length for substring matching (default: 2)
            core_threshold: Folio count for "core" classification (default: 20)
            common_threshold: Folio count for "common" classification (default: 5)
        """
        self.min_atom_length = min_atom_length
        self.core_threshold = core_threshold
        self.common_threshold = common_threshold

        self._transcript = Transcript()
        self._morphology = Morphology()
        self._inventory: Optional[Dict[str, MiddleStats]] = None
        self._core_middles: Optional[Set[str]] = None
        self._common_middles: Optional[Set[str]] = None
        self._folio_unique_middles: Optional[Set[str]] = None

    def build_inventory(self, system: str = 'B') -> None:
        """
        Build MIDDLE inventory from transcript.

        Args:
            system: Which system to analyze ('A', 'B', 'all'). Default 'B'.
        """
        from collections import defaultdict

        middle_to_folios: Dict[str, Set[str]] = defaultdict(set)
        middle_counts: Counter = Counter()

        # Select token iterator based on system
        if system == 'A':
            tokens = self._transcript.currier_a()
        elif system == 'B':
            tokens = self._transcript.currier_b()
        elif system == 'all':
            tokens = self._transcript.all()
        else:
            raise ValueError(f"Unknown system: {system}. Use 'A', 'B', or 'all'.")

        for token in tokens:
            if not token.word or '*' in token.word:
                continue
            m = self._morphology.extract(token.word)
            if m.middle:
                middle_to_folios[m.middle].add(token.folio)
                middle_counts[m.middle] += 1

        # Build inventory
        self._inventory = {}
        for middle, folios in middle_to_folios.items():
            self._inventory[middle] = MiddleStats(
                middle=middle,
                token_count=middle_counts[middle],
                folio_count=len(folios),
                folios=folios
            )

        # Build classification sets
        self._core_middles = {
            mid for mid, stats in self._inventory.items()
            if stats.folio_count >= self.core_threshold
        }
        self._common_middles = {
            mid for mid, stats in self._inventory.items()
            if stats.folio_count >= self.common_threshold
        }
        self._folio_unique_middles = {
            mid for mid, stats in self._inventory.items()
            if stats.folio_count == 1
        }

    def _ensure_inventory(self) -> None:
        """Ensure inventory is built, build if not."""
        if self._inventory is None:
            self.build_inventory()

    def get_stats(self, middle: str) -> Optional[MiddleStats]:
        """
        Get statistics for a specific MIDDLE.

        Args:
            middle: The MIDDLE string to look up

        Returns:
            MiddleStats object or None if MIDDLE not in inventory
        """
        self._ensure_inventory()
        return self._inventory.get(middle)

    def is_compound(self, middle: str, use_core: bool = True) -> bool:
        """
        Check if a MIDDLE contains other MIDDLEs as substrings.

        Args:
            middle: The MIDDLE to check
            use_core: If True, check against core MIDDLEs only (default).
                      If False, check against common MIDDLEs.

        Returns:
            True if MIDDLE contains at least one atom from the reference set
        """
        self._ensure_inventory()
        reference_set = self._core_middles if use_core else self._common_middles

        for atom in reference_set:
            if (len(atom) >= self.min_atom_length and
                atom in middle and
                atom != middle):
                return True
        return False

    def get_contained_atoms(self, middle: str, use_core: bool = True) -> List[str]:
        """
        Get list of atomic MIDDLEs contained in a compound MIDDLE.

        Args:
            middle: The MIDDLE to analyze
            use_core: If True, use core MIDDLEs. If False, use common MIDDLEs.

        Returns:
            List of MIDDLEs from reference set that appear as substrings
        """
        self._ensure_inventory()
        reference_set = self._core_middles if use_core else self._common_middles

        found = []
        for atom in reference_set:
            if (len(atom) >= self.min_atom_length and
                atom in middle and
                atom != middle):
                found.append(atom)
        return sorted(found, key=len, reverse=True)

    def get_compound_rate(self, middles: List[str], use_core: bool = True) -> float:
        """
        Calculate compound rate for a list of MIDDLEs.

        Args:
            middles: List of MIDDLEs to analyze
            use_core: Reference set to use

        Returns:
            Fraction (0.0-1.0) of MIDDLEs that are compound
        """
        if not middles:
            return 0.0
        compound_count = sum(1 for m in middles if self.is_compound(m, use_core))
        return compound_count / len(middles)

    def get_core_middles(self) -> Set[str]:
        """Get set of core MIDDLEs (appear in 20+ folios)."""
        self._ensure_inventory()
        return self._core_middles.copy()

    def get_common_middles(self) -> Set[str]:
        """Get set of common MIDDLEs (appear in 5+ folios)."""
        self._ensure_inventory()
        return self._common_middles.copy()

    def get_folio_unique_middles(self) -> Set[str]:
        """Get set of folio-unique MIDDLEs (appear in exactly 1 folio)."""
        self._ensure_inventory()
        return self._folio_unique_middles.copy()

    def classify_middle(self, middle: str) -> str:
        """
        Classify a MIDDLE by its folio spread.

        Args:
            middle: The MIDDLE to classify

        Returns:
            'CORE' (20+ folios), 'COMMON' (5-19 folios),
            'RARE' (2-4 folios), 'FOLIO_UNIQUE' (1 folio),
            or 'UNKNOWN' if not in inventory
        """
        self._ensure_inventory()
        stats = self._inventory.get(middle)
        if stats is None:
            return 'UNKNOWN'
        if stats.folio_count >= self.core_threshold:
            return 'CORE'
        elif stats.folio_count >= self.common_threshold:
            return 'COMMON'
        elif stats.folio_count >= 2:
            return 'RARE'
        else:
            return 'FOLIO_UNIQUE'

    def analyze_token(self, word: str) -> dict:
        """
        Analyze a token's MIDDLE for compound structure.

        Args:
            word: The token to analyze

        Returns:
            Dict with middle, classification, is_compound, contained_atoms
        """
        self._ensure_inventory()
        m = self._morphology.extract(word)
        if not m.middle:
            return {
                'word': word,
                'middle': None,
                'classification': None,
                'is_compound': False,
                'contained_atoms': []
            }

        return {
            'word': word,
            'middle': m.middle,
            'classification': self.classify_middle(m.middle),
            'is_compound': self.is_compound(m.middle),
            'contained_atoms': self.get_contained_atoms(m.middle)
        }

    def summary(self) -> dict:
        """
        Get summary statistics of the MIDDLE inventory.

        Returns:
            Dict with counts and rates
        """
        self._ensure_inventory()
        total = len(self._inventory)
        return {
            'total_middles': total,
            'core_count': len(self._core_middles),
            'core_pct': 100 * len(self._core_middles) / total if total else 0,
            'common_count': len(self._common_middles),
            'common_pct': 100 * len(self._common_middles) / total if total else 0,
            'folio_unique_count': len(self._folio_unique_middles),
            'folio_unique_pct': 100 * len(self._folio_unique_middles) / total if total else 0,
        }


# ============================================================
# PP SEMANTIC ANALYZER
# ============================================================
# Based on FL_SEMANTIC_INTERPRETATION phase findings (2026-01-29)
# Assigns semantic roles to PP MIDDLEs based on character composition

@dataclass
class PPSemanticAnalysis:
    """Semantic analysis of a PP MIDDLE."""
    middle: str
    semantic_class: str      # STATE_INDEX, OPERATOR, MODIFIER, UNKNOWN
    subclass: Optional[str]  # For STATE_INDEX: stage; For OPERATOR: kernel type
    kernel_chars: List[str]  # Which kernel chars present (k, h, e)
    is_fl_vocabulary: bool   # True if this MIDDLE is in FL class vocabulary
    confidence: str          # HIGH, MEDIUM, LOW


class PPSemantics:
    """
    Semantic analyzer for PP (Pipeline-Participating) MIDDLEs.

    Based on FL_SEMANTIC_INTERPRETATION phase findings:
    - FL MIDDLEs use only 9 chars: a, d, i, l, m, n, o, r, y
    - FL MIDDLEs index material state in transformation process
    - Kernel chars (k, h, e) indicate operators, not state indices

    Classification:
    - STATE_INDEX: Kernel-free, FL-like vocabulary -> marks material states
    - OPERATOR: Contains kernel chars (k, h, e) -> marks transformations
    - MODIFIER: Contains helper chars (c, s, t, p, f, q, g) but no kernel

    Usage:
        sem = PPSemantics()
        result = sem.analyze('od')
        print(f"{result.middle}: {result.semantic_class} ({result.subclass})")

        # Batch analysis
        for mid, analysis in sem.analyze_vocabulary(pp_middles):
            print(f"{mid}: {analysis.semantic_class}")
    """

    # FL primitive character set (C770, C772)
    FL_CHARS = set('adilmnory')

    # Kernel characters (operators)
    KERNEL_CHARS = set('khe')

    # Helper/modifier characters
    HELPER_CHARS = set('cstpfqg')

    # FL MIDDLEs and their stages (from FL_SEMANTIC_INTERPRETATION phase)
    FL_STAGE_MAP = {
        'ii': 'INITIAL', 'i': 'INITIAL',
        'in': 'EARLY',
        'r': 'MEDIAL', 'ar': 'MEDIAL', 'al': 'MEDIAL', 'l': 'MEDIAL', 'ol': 'MEDIAL',
        'o': 'LATE', 'ly': 'LATE',
        'am': 'TERMINAL', 'n': 'TERMINAL', 'im': 'TERMINAL', 'm': 'TERMINAL',
        'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
    }

    # Extended stage inference for non-FL MIDDLEs based on character patterns
    CHAR_STAGE_HINTS = {
        'i': 'INITIAL',   # i-initial suggests input
        'y': 'TERMINAL',  # y-final suggests output
    }

    def __init__(self):
        self._fl_middles = set(self.FL_STAGE_MAP.keys())

    def _get_kernel_chars(self, middle: str) -> List[str]:
        """Extract kernel characters from MIDDLE."""
        return [c for c in 'khe' if c in middle]

    def _get_char_classes(self, middle: str) -> dict:
        """Classify characters in MIDDLE."""
        chars = set(middle)
        return {
            'has_kernel': bool(chars & self.KERNEL_CHARS),
            'has_helper': bool(chars & self.HELPER_CHARS),
            'fl_only': chars <= self.FL_CHARS,
            'kernel_chars': list(chars & self.KERNEL_CHARS),
            'helper_chars': list(chars & self.HELPER_CHARS),
        }

    def _infer_stage(self, middle: str) -> Optional[str]:
        """Infer process stage for FL-like MIDDLE."""
        # Direct FL lookup
        if middle in self.FL_STAGE_MAP:
            return self.FL_STAGE_MAP[middle]

        # Heuristic inference based on character patterns
        if middle.startswith('i') and 'y' not in middle:
            return 'INITIAL'
        elif middle.endswith('y'):
            return 'TERMINAL'
        elif middle.startswith('a') or middle.startswith('o'):
            return 'MEDIAL'

        return None

    def analyze(self, middle: str) -> PPSemanticAnalysis:
        """
        Analyze semantic role of a PP MIDDLE.

        Args:
            middle: The MIDDLE string to analyze

        Returns:
            PPSemanticAnalysis with classification and details
        """
        if not middle:
            return PPSemanticAnalysis(
                middle=middle,
                semantic_class='UNKNOWN',
                subclass=None,
                kernel_chars=[],
                is_fl_vocabulary=False,
                confidence='LOW'
            )

        char_info = self._get_char_classes(middle)
        is_fl = middle in self._fl_middles

        # Classification logic
        if char_info['has_kernel']:
            # OPERATOR: Contains kernel characters
            kernel_list = char_info['kernel_chars']
            # Subclass based on dominant kernel
            if 'k' in kernel_list:
                subclass = 'ENERGY'
            elif 'h' in kernel_list:
                subclass = 'PHASE'
            elif 'e' in kernel_list:
                subclass = 'STABILITY'
            else:
                subclass = 'MIXED'

            return PPSemanticAnalysis(
                middle=middle,
                semantic_class='OPERATOR',
                subclass=subclass,
                kernel_chars=kernel_list,
                is_fl_vocabulary=False,
                confidence='HIGH'
            )

        elif char_info['fl_only']:
            # STATE_INDEX: Uses only FL characters
            stage = self._infer_stage(middle)
            confidence = 'HIGH' if is_fl else 'MEDIUM'

            return PPSemanticAnalysis(
                middle=middle,
                semantic_class='STATE_INDEX',
                subclass=stage,
                kernel_chars=[],
                is_fl_vocabulary=is_fl,
                confidence=confidence
            )

        elif char_info['has_helper']:
            # MODIFIER: Has helper chars but no kernel
            helper_type = None
            if 'c' in middle or 's' in middle or 't' in middle:
                helper_type = 'CONTROL_MODIFIER'
            elif any(c in middle for c in 'pfqg'):
                helper_type = 'DOMAIN_MARKER'

            return PPSemanticAnalysis(
                middle=middle,
                semantic_class='MODIFIER',
                subclass=helper_type,
                kernel_chars=[],
                is_fl_vocabulary=False,
                confidence='MEDIUM'
            )

        else:
            # Shouldn't reach here, but handle gracefully
            return PPSemanticAnalysis(
                middle=middle,
                semantic_class='UNKNOWN',
                subclass=None,
                kernel_chars=[],
                is_fl_vocabulary=False,
                confidence='LOW'
            )

    def analyze_vocabulary(self, middles: List[str]) -> List[Tuple[str, PPSemanticAnalysis]]:
        """
        Analyze a list of PP MIDDLEs.

        Args:
            middles: List of MIDDLE strings

        Returns:
            List of (middle, PPSemanticAnalysis) tuples
        """
        return [(m, self.analyze(m)) for m in middles]

    def get_class_distribution(self, middles: List[str]) -> dict:
        """
        Get distribution of semantic classes in a vocabulary.

        Args:
            middles: List of MIDDLE strings

        Returns:
            Dict with counts per semantic class
        """
        results = self.analyze_vocabulary(middles)
        distribution = Counter(r.semantic_class for _, r in results)
        return dict(distribution)

    def filter_by_class(self, middles: List[str],
                        semantic_class: str) -> List[str]:
        """
        Filter MIDDLEs by semantic class.

        Args:
            middles: List of MIDDLE strings
            semantic_class: 'STATE_INDEX', 'OPERATOR', 'MODIFIER', or 'UNKNOWN'

        Returns:
            List of MIDDLEs matching the class
        """
        return [m for m, a in self.analyze_vocabulary(middles)
                if a.semantic_class == semantic_class]

    def get_operators_by_kernel(self, middles: List[str]) -> dict:
        """
        Group OPERATOR MIDDLEs by kernel type.

        Args:
            middles: List of MIDDLE strings

        Returns:
            Dict mapping kernel type to list of MIDDLEs
        """
        operators = {}
        for m, a in self.analyze_vocabulary(middles):
            if a.semantic_class == 'OPERATOR':
                key = a.subclass or 'UNKNOWN'
                if key not in operators:
                    operators[key] = []
                operators[key].append(m)
        return operators

    def get_state_indices_by_stage(self, middles: List[str]) -> dict:
        """
        Group STATE_INDEX MIDDLEs by process stage.

        Args:
            middles: List of MIDDLE strings

        Returns:
            Dict mapping stage to list of MIDDLEs
        """
        states = {}
        for m, a in self.analyze_vocabulary(middles):
            if a.semantic_class == 'STATE_INDEX':
                key = a.subclass or 'UNKNOWN'
                if key not in states:
                    states[key] = []
                states[key].append(m)
        return states

    def summary(self, middles: List[str]) -> dict:
        """
        Get comprehensive summary of PP vocabulary semantics.

        Args:
            middles: List of PP MIDDLEs

        Returns:
            Dict with distribution, breakdowns, and statistics
        """
        results = self.analyze_vocabulary(middles)

        class_dist = Counter(r.semantic_class for _, r in results)
        fl_count = sum(1 for _, r in results if r.is_fl_vocabulary)
        high_conf = sum(1 for _, r in results if r.confidence == 'HIGH')

        return {
            'total': len(middles),
            'class_distribution': dict(class_dist),
            'fl_vocabulary_count': fl_count,
            'high_confidence_count': high_conf,
            'operators_by_kernel': self.get_operators_by_kernel(middles),
            'states_by_stage': self.get_state_indices_by_stage(middles),
        }


# ============================================================
# QUICK VERIFICATION
# ============================================================
if __name__ == '__main__':
    # Quick test
    print("Voynich Library Test")
    print("=" * 50)

    tx = Transcript()
    morph = Morphology()

    # Count tokens
    a_count = sum(1 for _ in tx.currier_a())
    b_count = sum(1 for _ in tx.currier_b())
    print(f"Currier A tokens: {a_count}")
    print(f"Currier B tokens: {b_count}")

    # Test morphology
    test_tokens = ['chody', 'ydaraishy', 'dy', 'fachys', 'shol', 'qokeey']
    print(f"\nMorphology examples:")
    for t in test_tokens:
        m = morph.extract(t)
        print(f"  {t}: art={m.articulator}, pre={m.prefix}, mid={m.middle}, suf={m.suffix}")

    # Canonical counts verification
    print(f"\nCanonical count check (should match CLAUDE.md):")
    print(f"  Currier A: {a_count} (expected: 11,415)")
    print(f"  Currier B: {b_count} (expected: 23,243)")

    # Test RecordAnalyzer
    print("\n" + "=" * 50)
    print("Record Analyzer Test (f1r, first 3 lines)")
    print("=" * 50)

    analyzer = RecordAnalyzer()

    for line_num in ['1', '2', '3']:
        record = analyzer.analyze_record('f1r', line_num)
        if record:
            print(f"\nLine {line_num} [{record.composition}]: {record.ri_count} RI, {record.pp_count} PP, {record.infra_count} INFRA")
            print("-" * 50)
            for t in record.tokens:
                class_tag = f"[{t.token_class:7}]"
                morph_str = f"PRE={t.prefix or '-':5} MID={t.middle or '-':10} SUF={t.suffix or '-'}"
                print(f"  {t.word:15} {class_tag} {morph_str}")

    # Test MiddleAnalyzer
    print("\n" + "=" * 50)
    print("Middle Analyzer Test (Currier B)")
    print("=" * 50)

    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    summary = mid_analyzer.summary()
    print(f"\nInventory summary:")
    print(f"  Total MIDDLEs: {summary['total_middles']}")
    print(f"  Core (20+ folios): {summary['core_count']} ({summary['core_pct']:.1f}%)")
    print(f"  Folio-unique: {summary['folio_unique_count']} ({summary['folio_unique_pct']:.1f}%)")

    # Test compound detection
    print(f"\nCompound analysis examples:")
    test_middles = ['od', 'aiin', 'odaiin', 'cheod', 'oteey']
    for mid in test_middles:
        stats = mid_analyzer.get_stats(mid)
        if stats:
            is_cmp = mid_analyzer.is_compound(mid)
            atoms = mid_analyzer.get_contained_atoms(mid)
            cls = mid_analyzer.classify_middle(mid)
            print(f"  '{mid}': {cls}, compound={is_cmp}, atoms={atoms}")

    # Test PPSemantics
    print("\n" + "=" * 50)
    print("PP Semantics Test")
    print("=" * 50)

    sem = PPSemantics()

    # Test individual MIDDLEs
    test_pp = ['od', 'al', 'ar', 'y', 'in', 'k', 'e', 'ey', 'ckh', 'aiin', 'or', 't', 'ct']
    print("\nSemantic analysis examples:")
    for mid in test_pp:
        a = sem.analyze(mid)
        fl_tag = "[FL]" if a.is_fl_vocabulary else ""
        kernel_str = f"kernel={a.kernel_chars}" if a.kernel_chars else ""
        print(f"  {mid:10} -> {a.semantic_class:12} ({a.subclass or '-':15}) {fl_tag} {kernel_str}")

    # Test vocabulary summary
    print("\nVocabulary summary (sample PP MIDDLEs):")
    sample_pp = ['od', 'al', 'ar', 'y', 'in', 'k', 'e', 'ey', 'ckh', 'aiin', 'or', 't', 'ct',
                 'ol', 'r', 'dy', 'm', 'eol', 'ch', 'ok', 'ek', 'he', 'ke']
    summary = sem.summary(sample_pp)
    print(f"  Total: {summary['total']}")
    print(f"  Class distribution: {summary['class_distribution']}")
    print(f"  FL vocabulary: {summary['fl_vocabulary_count']}")
    print(f"  High confidence: {summary['high_confidence_count']}")
