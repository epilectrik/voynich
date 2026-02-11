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
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Iterator, List, Set, Tuple, Dict
from collections import Counter, defaultdict

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
    prefix2: Optional[str] = None  # Secondary prefix (ch/sh after primary)

    @property
    def has_prefix(self) -> bool:
        return self.prefix is not None

    @property
    def has_prefix2(self) -> bool:
        return self.prefix2 is not None

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

        # Step 2.5: Check for secondary prefix (ch/sh embedded after primary)
        # Only ch and sh qualify — other strings after primary prefix are MIDDLEs
        SECONDARY_PREFIXES = ['sh', 'ch']
        prefix2 = None
        if prefix is not None:
            for sp in SECONDARY_PREFIXES:
                if remainder.startswith(sp) and len(remainder) > len(sp):
                    prefix2 = sp
                    remainder = remainder[len(sp):]
                    break

        # Step 3: Extract suffix from remainder
        middle, suffix = self._find_suffix(remainder)

        # Step 4: Avoid empty MIDDLE when possible (per C293/C267.a)
        # If prefix+suffix consumed everything, try alternative parses
        if middle == '':
            # Option A: Drop suffix, treat remainder as pure MIDDLE
            alt_a = MorphAnalysis(articulator, prefix, remainder, None, prefix2)

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

        return MorphAnalysis(articulator, prefix, middle, suffix, prefix2)

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

    def get_maximal_atoms(self, middle: str, use_core: bool = True) -> List[str]:
        """Get non-redundant atoms (remove substrings of longer atoms).

        Returns only maximal atoms — those not contained within any other
        returned atom. E.g., for MIDDLE 'odeey': returns ['eey', 'od']
        instead of ['eey', 'ee', 'ey', 'od'].
        """
        atoms = self.get_contained_atoms(middle, use_core)
        if len(atoms) <= 1:
            return atoms
        # atoms is sorted longest-first; keep only those not substrings of longer ones
        maximal = []
        for atom in atoms:
            if not any(atom in longer for longer in maximal):
                maximal.append(atom)
        return maximal

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
# B FOLIO DECODER
# ============================================================
# Consolidates structural knowledge for decoding Currier B folios.
# Based on constraints: C371-378, C510-522, C766-769, C884, C906-907,
#                      F-BRU-011, F-BRU-018-020

@dataclass
class BTokenAnalysis:
    """
    Complete analysis of a single Currier B token.

    Combines morphological decomposition with functional role classification
    and semantic markers from the constraint system.
    """
    word: str
    morph: MorphAnalysis

    # Role classification (Tier 0-2, from C371-378)
    prefix_role: Optional[str]   # EN_KERNEL, EN_QO, AX_SCAFFOLD, etc.
    suffix_role: Optional[str]   # KERN_HEAVY, LINK_ATTR, LINE_FINAL, etc.

    # MIDDLE analysis (F-BRU-011)
    middle_tier: Optional[str]   # PREP, THERMO, EXTENDED
    middle_meaning: Optional[str]  # Brunschwig-grounded description

    # FL state classification (C777, FL_SEMANTIC_INTERPRETATION)
    fl_stage: Optional[str]      # INITIAL, EARLY, MEDIAL, LATE, TERMINAL
    fl_meaning: Optional[str]    # State index description
    is_fl_role: bool             # True if FL-role token (pure FL vocab, no kernel/helper)

    # HT (Human Track) classification (C740, C747, C872)
    is_ht: bool                  # True if HT/UN token (compound identification/specification, C935)

    # Kernel content
    kernels: List[str]           # ['k'], ['h', 'e'], etc.

    # Material/output markers (C884, F-BRU-018-020)
    material_markers: List[str]  # ['ANIMAL'], ['ROOT'], []
    output_markers: List[str]    # ['OIL'], ['WATER'], []

    # Positional info
    is_line_initial: bool
    is_line_final: bool

    # Execution roles (C556 phases, C539 suffix roles)
    prefix_phase: Optional[str]      # SETUP, PREP, WORK, CLOSE (C556)
    suffix_terminal: Optional[str]   # TERMINAL, CHECKPOINT, CONNECTOR

    # MIDDLE semantic profile (MIDDLE_SEMANTIC_MAPPING phase)
    middle_kernel: Optional[str]     # K, H, E - kernel correlation
    middle_regime: Optional[str]     # PRECISION, HIGH_ENERGY, SETTLING
    middle_section: Optional[str]    # HERBAL, BIO, STARS

    def structural(self) -> str:
        """
        Tier 0-2 technical representation.

        Returns structural role codes for precise analysis.
        """
        parts = []
        if self.prefix_role:
            parts.append(self.prefix_role)
        if self.middle_tier:
            parts.append(self.middle_tier)
        if self.fl_stage:
            parts.append(f"FL:{self.fl_stage}")
        if self.suffix_role:
            parts.append(self.suffix_role)
        if self.kernels:
            parts.append(f"kern:{','.join(self.kernels)}")
        return ' + '.join(parts) if parts else '(unclassified)'

    def interpretive(self) -> str:
        """
        Auto-composed interpretive gloss.

        Priority:
        1. Whole-token gloss from TokenDictionary (manual, if set)
        2. Auto-composed: PREFIX_ACTION + MIDDLE_GLOSS + SUFFIX_GLOSS
        3. Structural fallback: [LANE] middle:kernel [-suffix PROPS]

        Auto-composition activates when MIDDLE has a learned or tier-based
        gloss. Otherwise falls back to structural format.
        """
        # 0. HT SPECIFICATION BUNDLE (C404/C405: non-executable, C935: atom decomposition)
        ht_bundle = self._ht_spec_bundle()
        if ht_bundle:
            return ht_bundle

        # MIDDLE signature for gloss discrimination (C506.b, C908)
        # Kernel is mandatory (primary discriminator), regime conditional.
        # Computed early so it applies to ALL gloss paths (manual + auto-compose).
        mid_sig = ''
        if self.middle_kernel:
            mid_sig = f"[{self.middle_kernel.lower()}]"
            # Regime is conditional: only append when needed to break collisions
            _regime_needed = (self.middle_regime
                              and hasattr(self, '_needs_regime')
                              and self.word in self._needs_regime)
            if _regime_needed:
                mid_sig += f":{self.middle_regime.lower()}"

        # 1. WHOLE-TOKEN LOOKUP (manual gloss takes priority)
        if hasattr(self, '_token_dict') and self._token_dict:
            gloss = self._token_dict.get_gloss(self.word)
            if gloss:
                # Expand *middle references to middle dictionary glosses
                if '*' in gloss and hasattr(self, '_middle_dict') and self._middle_dict:
                    import re
                    def replace_middle_ref(match):
                        mid_name = match.group(1)
                        mid_gloss = self._middle_dict.get_gloss(mid_name)
                        return mid_gloss if mid_gloss else f"[{mid_name}]"
                    gloss = re.sub(r'\*(\w+)', replace_middle_ref, gloss)
                # Inject MIDDLE signature for behavioral discrimination
                if mid_sig:
                    import re as _re
                    # Insert before suffix tags like " [thorough]" or trailing punct
                    m = _re.search(r'(\s+\[.+)$', gloss)
                    if m:
                        # Gloss has suffix tags: insert signature before them
                        pre = gloss[:m.start()].rstrip('.,;:! ')
                        trail_punct = gloss[len(gloss[:m.start()].rstrip('.,;:! ')):m.start()]
                        gloss = pre + mid_sig + trail_punct + m.group(1)
                    else:
                        # Simple gloss: insert before trailing punctuation
                        stripped = gloss.rstrip('.,;:! ')
                        trailing = gloss[len(stripped):]
                        gloss = stripped + mid_sig + trailing
                return gloss

        middle = self.morph.middle if self.morph else None
        prefix = self.morph.prefix if self.morph else None
        suffix = self.morph.suffix if self.morph else None

        # 2. AUTO-COMPOSED GLOSS (when MIDDLE meaning is known)
        mid_meaning = None
        if middle:
            # Dictionary gloss first (manually curated)
            if hasattr(self, '_middle_dict') and self._middle_dict:
                mid_meaning = self._middle_dict.get_gloss(middle)
            # Fall back to middle_tiers gloss (F-BRU tier-based)
            # Skip when prefix_role is PREP_TIER — middle_meaning was overridden
            # with the prep action, not the actual MIDDLE semantics
            # Skip "contains X" substring matches — compound decomposition is better
            if not mid_meaning and self.middle_meaning and self.prefix_role != 'PREP_TIER':
                if not str(self.middle_meaning).startswith('contains '):
                    mid_meaning = self.middle_meaning

            # Compound MIDDLE decomposition: atom_gloss (+extension_gloss)
            # Compound MIDDLEs = PP atom + parameter extensions (C872, C522)
            if not mid_meaning:
                mid_meaning = self._compose_compound_gloss(middle)

        if mid_meaning:
            # Compose: [PREFIX_ACTION] MIDDLE_MEANING[signature] [SUFFIX_GLOSS]
            composed = []

            # Prefix: use prep action if available, otherwise lane tag
            # For qo: suppress prefix verb in compose path. qo is the default
            # execution pathway (EN_QO, 17.6% of B tokens). The MIDDLE meaning
            # already carries the full operation — "heat-check" not "execute
            # heat-check". Other prefixes keep their verbs for contrast:
            # "test heat" (ch), "monitor heat" (sh), "store heat" (ol).
            prep_action = None
            if prefix and prefix != 'qo' and hasattr(self, '_prefix_actions'):
                prep_action = self._prefix_actions.get(prefix)

            # Secondary prefix action (ch/sh after primary prefix)
            prep2_action = None
            prefix2 = self.morph.prefix2 if self.morph else None
            if prefix2 and hasattr(self, '_prefix_actions'):
                prep2_action = self._prefix_actions.get(prefix2)

            if prep_action and prep2_action:
                composed.append(f"{prep_action}-{prep2_action}")
            elif prep_action:
                composed.append(prep_action)
            elif prep2_action:
                # qo suppressed but ch/sh still shows
                composed.append(prep2_action)
            elif prefix and prefix != 'qo':
                lane = self._get_prefix_lane(prefix)
                composed.append(f"[{lane}]")

            # Suffix-into-operation composition for k-MIDDLE:
            # Folds suffix semantics INTO the heat term so each k+suffix
            # renders as a distinct heat operation.
            # Criterion suffixes: k+edy B-enriched 2.08x, k+eey S-enriched
            # 1.25x, k+ey B-enriched 1.54x.
            # Gate suffixes: k+ain B-enriched 1.92x (inline check, self-chains),
            # k+aiin evenly distributed (quality gate, follows thorough ops).
            _K_SUFFIX_COMPOSE = {
                'edy':  'thorough heat',   # complete heat cycle (B 2.08x)
                'eey':  'prolonged heat',  # extended = sustained duration (S 1.25x)
                'ey':   'selective heat',  # selective = targeted application (B 1.54x)
                'ain':  'heat-check',      # inline progress check (B 1.92x, self-chains)
                'aiin': 'heat-verify',     # quality gate (even distribution, post-thorough)
            }
            suffix_consumed = False
            if middle == 'k' and suffix in _K_SUFFIX_COMPOSE:
                composed.append(_K_SUFFIX_COMPOSE[suffix] + mid_sig)
                suffix_consumed = True
            else:
                # When prefix verb present and MIDDLE gloss has colon,
                # use qualifier only: "test collect:gather" → "test gather"
                display_mid = mid_meaning
                has_verb = prep_action or prep2_action
                if has_verb and display_mid and ':' in display_mid:
                    display_mid = display_mid.split(':')[-1]
                composed.append(display_mid + mid_sig)

            # FL-role marking
            if self.is_fl_role:
                composed.append('(FL)')

            # Suffix: use interpretive gloss if available (skip if already composed)
            if not suffix_consumed and suffix and hasattr(self, '_suffix_gloss'):
                suf_gloss = self._suffix_gloss.get(suffix)
                if suf_gloss:
                    composed.append(suf_gloss)
                else:
                    composed.append(f"[-{suffix}]")
            return ' '.join(composed)

        # 3. STRUCTURAL FALLBACK (no MIDDLE meaning available)
        parts = []

        if prefix:
            # Use prep action verb when available, lane tag otherwise
            prep_action = None
            if hasattr(self, '_prefix_actions'):
                prep_action = self._prefix_actions.get(prefix)

            # Secondary prefix action (ch/sh after primary prefix)
            prep2_action = None
            prefix2 = self.morph.prefix2 if self.morph else None
            if prefix2 and hasattr(self, '_prefix_actions'):
                prep2_action = self._prefix_actions.get(prefix2)

            if prep_action and prep2_action:
                parts.append(f"{prep_action}-{prep2_action}")
            elif prep_action:
                parts.append(prep_action)
            elif prep2_action:
                parts.append(prep2_action)
            else:
                lane = self._get_prefix_lane(prefix)
                parts.append(f"[{lane}]")

        if middle:
            kernel_hint = ''
            if self.kernels:
                kernel_hint = ':' + ''.join(sorted(self.kernels))
            parts.append(f"{middle}{kernel_hint}")

        if self.is_fl_role:
            parts.append('(FL)')

        # Suffix structural properties (C375-378)
        suffix_props = {
            'dy': 'K+', 'edy': 'K+', 'ey': 'K+ IN', 'eey': 'K+',
            'hy': 'IN', 'ly': 'K+', 'ry': 'OUT', 'y': '',
            'r': 'L+ IN', 'l': 'L+', 'in': 'L+',
            'ar': 'L+ IN', 'or': 'L+ IN', 'al': 'L+ IN', 'ol': 'L+',
            'am': 'LF', 'om': 'LF', 'im': 'LF', 'oly': 'LF',
            'aiin': 'L+', 'ain': 'L+', 'iin': 'L+', 'oiin': 'L+',
            's': '', 'an': '',
        }
        if suffix:
            props = suffix_props.get(suffix, '')
            if props:
                parts.append(f"[-{suffix} {props}]")
            else:
                parts.append(f"[-{suffix}]")

        return ' '.join(parts) if parts else self.word

    def flow_gloss(self) -> dict:
        """Three-layer flow rendering: FL_STAGE + OPERATION + CONTROL_FLOW.

        Returns dict with keys:
            fl_stage: INITIAL/EARLY/MEDIAL/LATE/TERMINAL (only for FL-role tokens)
            fl_meaning: Tier 4 semantic description (only for FL-role tokens)
            operation: prefix_verb + middle_gloss (no suffix punctuation)
            flow: suffix control-flow label (CHECKPOINT, ITERATE, etc.)
            flow_type: GATE/LOOP/CHECK/HOLD/TERMINAL/CRITERION/SEQUENCE/MOVE
        """
        result = {
            'fl_stage': self.fl_stage if self.is_fl_role else None,
            'fl_meaning': self.fl_meaning if self.is_fl_role else None,
            'operation': '',
            'flow': '',
            'flow_type': '',
        }

        # HT SPECIFICATION BUNDLE (C404/C405: non-executable, C935: atom decomposition)
        ht_bundle = self._ht_spec_bundle()
        if ht_bundle:
            result['operation'] = ht_bundle
            return result

        # OPERATION layer: check token dictionary first (C936 composites)
        middle = self.morph.middle if self.morph else None
        prefix = self.morph.prefix if self.morph else None
        suffix = self.morph.suffix if self.morph else None

        if hasattr(self, '_token_dict') and self._token_dict:
            token_gloss = self._token_dict.get_gloss(self.word)
            if token_gloss:
                # Expand *middle references
                if '*' in token_gloss and hasattr(self, '_middle_dict') and self._middle_dict:
                    import re
                    def replace_middle_ref(match):
                        mid_name = match.group(1)
                        mid_gloss = self._middle_dict.get_gloss(mid_name)
                        return mid_gloss if mid_gloss else f"[{mid_name}]"
                    token_gloss = re.sub(r'\*(\w+)', replace_middle_ref, token_gloss)
                # Strip trailing punctuation for flow format
                op = token_gloss.rstrip('.,;')
                # Append compressed kernel signature for flow discrimination
                if self.middle_kernel:
                    flow_sig = self.middle_kernel.lower()
                    _regime_needed = (self.middle_regime
                                      and hasattr(self, '_needs_regime')
                                      and self.word in self._needs_regime)
                    if _regime_needed:
                        flow_sig += f":{self.middle_regime[:4].lower()}"
                    op += f" <{flow_sig}>"
                result['operation'] = op
                # Suffix flow still applies unless gloss already includes it
                if suffix and hasattr(self, '_suffix_flow'):
                    flow_entry = self._suffix_flow.get(suffix, {})
                    result['flow'] = flow_entry.get('value', '')
                    result['flow_type'] = flow_entry.get('flow_type', '')
                return result

        mid_meaning = None
        if middle and hasattr(self, '_middle_dict') and self._middle_dict:
            mid_meaning = self._middle_dict.get_gloss(middle)
        if not mid_meaning and self.middle_meaning and self.prefix_role != 'PREP_TIER':
            if not str(self.middle_meaning).startswith('contains '):
                mid_meaning = self.middle_meaning
        # Compound MIDDLE decomposition (same as interpretive())
        if not mid_meaning and middle:
            mid_meaning = self._compose_compound_gloss(middle)

        # For qo: suppress prefix verb (same as interpretive())
        prep_action = None
        if prefix and prefix != 'qo' and hasattr(self, '_prefix_actions'):
            prep_action = self._prefix_actions.get(prefix)

        # Suffix-into-operation composition for k-MIDDLE (same as interpretive())
        _K_SUFFIX_COMPOSE = {
            'edy':  'thorough heat',
            'eey':  'prolonged heat',
            'ey':   'selective heat',
            'ain':  'heat-check',
            'aiin': 'heat-verify',
        }
        suffix_consumed = False
        if middle == 'k' and suffix in _K_SUFFIX_COMPOSE:
            effective_mid = _K_SUFFIX_COMPOSE[suffix]
            suffix_consumed = True
        else:
            effective_mid = mid_meaning
            # Simplify colon-gloss when prefix verb present
            if prep_action and effective_mid and ':' in effective_mid:
                effective_mid = effective_mid.split(':')[-1]

        if prep_action and effective_mid:
            result['operation'] = f"{prep_action} {effective_mid}"
        elif prep_action:
            result['operation'] = prep_action
        elif prefix and effective_mid:
            lane = self._get_prefix_lane(prefix)
            result['operation'] = f"[{lane}] {effective_mid}"
        elif effective_mid:
            result['operation'] = effective_mid
        else:
            result['operation'] = self.word

        # Append compressed kernel signature for flow discrimination
        if self.middle_kernel:
            flow_sig = self.middle_kernel.lower()
            _regime_needed = (self.middle_regime
                              and hasattr(self, '_needs_regime')
                              and self.word in self._needs_regime)
            if _regime_needed:
                flow_sig += f":{self.middle_regime[:4].lower()}"
            result['operation'] += f" <{flow_sig}>"

        # FLOW layer: suffix control-flow semantics (skip if suffix was composed into operation)
        if not suffix_consumed and suffix and hasattr(self, '_suffix_flow'):
            flow_entry = self._suffix_flow.get(suffix, {})
            result['flow'] = flow_entry.get('value', '')
            result['flow_type'] = flow_entry.get('flow_type', '')

        return result

    def _decompose_compound(self, middle: str):
        """Decompose compound MIDDLE into (atom, pre_ext, suf_ext).

        Finds the longest core PP atom contained in the MIDDLE.
        Returns (atom, pre_ext, suf_ext) tuple or None.
        """
        if not hasattr(self, '_mid_analyzer') or not self._mid_analyzer:
            return None
        core = self._mid_analyzer._core_middles
        if not core or middle in core:
            return None  # Already a core atom, no decomposition needed

        best = None
        for atom in sorted(core, key=len, reverse=True):
            idx = middle.find(atom)
            if idx >= 0:
                pre = middle[:idx]
                post = middle[idx + len(atom):]
                ext_len = len(pre) + len(post)
                if ext_len <= 3 and (best is None or ext_len < best[3]):
                    best = (atom, pre, post, ext_len)

        if best:
            return (best[0], best[1], best[2])
        return None

    def _segment_multi_atom(self, middle: str):
        """Segment a MIDDLE into multiple atoms + extension characters using DP.

        Fallback for long MIDDLEs where single-atom decomposition fails
        (extension length > 3). Uses dynamic programming to find the
        optimal segmentation that maximizes atom coverage.

        Returns list of (segment, type, gloss) tuples where type is
        'ATOM' or 'EXT', or None if segmentation fails.
        """
        if not hasattr(self, '_mid_analyzer') or not self._mid_analyzer:
            return None
        if not hasattr(self, '_middle_dict') or not self._middle_dict:
            return None

        core = self._mid_analyzer._core_middles
        if not core or middle in core:
            return None

        # Build atom->gloss lookup (only atoms with glosses)
        atom_glosses = {}
        for name in core:
            g = self._middle_dict.get_gloss(name)
            if g:
                atom_glosses[name] = g

        if not atom_glosses:
            return None

        n = len(middle)
        INF = float('inf')
        # dp[i] = (min_cost, backtrack_info) for middle[:i]
        dp = [(INF, None)] * (n + 1)
        dp[0] = (0, None)

        for i in range(n):
            if dp[i][0] == INF:
                continue

            # Option 1: match a known atom starting at position i
            for atom_name, atom_gloss in atom_glosses.items():
                alen = len(atom_name)
                if i + alen <= n and middle[i:i + alen] == atom_name:
                    new_cost = dp[i][0]  # atoms are free (cost 0)
                    if new_cost < dp[i + alen][0]:
                        dp[i + alen] = (new_cost, ('ATOM', i, atom_name, atom_gloss))

            # Option 2: single char as extension
            ch = middle[i]
            ch_gloss = self._middle_dict.get_gloss(ch)
            ext_cost = 1 if ch_gloss else 10
            new_cost = dp[i][0] + ext_cost
            if new_cost < dp[i + 1][0]:
                dp[i + 1] = (new_cost, ('EXT', i, ch, ch_gloss or f'?{ch}'))

        if dp[n][0] == INF:
            return None

        # Backtrack
        segments = []
        pos = n
        while pos > 0:
            _, info = dp[pos]
            if info is None:
                break
            seg_type, start, value, gloss = info
            segments.append((value, seg_type, gloss))
            pos = start if seg_type == 'EXT' else start

        segments.reverse()

        # Only return if at least one atom was found
        if any(t == 'ATOM' for _, t, _ in segments):
            return segments
        return None

    def _compose_compound_gloss(self, middle: str):
        """Try to compose a gloss for a compound MIDDLE from atom + extension meanings.

        Uses PP atom gloss as the base operation, with extension character
        glosses as parameters. Compound MIDDLEs specify WHICH variant of an
        operation, not a different operation (C872, C522).

        For short compounds (ext <= 3), uses single-atom decomposition.
        For longer compounds, falls back to multi-atom DP segmentation.
        """
        decomp = self._decompose_compound(middle)
        if decomp:
            atom, pre_ext, suf_ext = decomp

            # Get atom gloss
            atom_gloss = None
            if hasattr(self, '_middle_dict') and self._middle_dict:
                atom_gloss = self._middle_dict.get_gloss(atom)
            if not atom_gloss:
                return None

            # Get extension glosses from single-char MIDDLE meanings
            ext_glosses = []
            for ch in pre_ext + suf_ext:
                if hasattr(self, '_middle_dict') and self._middle_dict:
                    g = self._middle_dict.get_gloss(ch)
                    if g:
                        ext_glosses.append(g)

            if ext_glosses:
                return f"{atom_gloss} (+{', '.join(ext_glosses)})"
            elif pre_ext or suf_ext:
                return f"{atom_gloss} (+{pre_ext}{suf_ext})"
            else:
                return atom_gloss

        # Fallback: multi-atom segmentation for long compounds
        segments = self._segment_multi_atom(middle)
        if not segments:
            return None

        atom_parts = []
        ext_parts = []
        for seg, stype, gloss in segments:
            if stype == 'ATOM':
                atom_parts.append(gloss)
            else:
                ext_parts.append(gloss)

        result = ', '.join(atom_parts)
        if ext_parts:
            result += f" (+{', '.join(ext_parts)})"
        return result

    def _ht_spec_bundle(self) -> Optional[str]:
        """Render HT token as posture gloss.

        HT tokens are NOT executable (C404/C405). Instead of pretending
        they carry semantic content, render as operator posture:
          - density (line-level HT proportion) -> vigilance: attend/hold
          - form (atom count) -> cognitive load: heavy/light

        HT Rendering Rule (FROZEN):
          1. Never rendered as actions
          2. Posture grammar: [mode-load] (attend/hold, heavy/light)
          3. No verbs, no arrows, no sequencing
          4. Suffix shown as raw morphology (form marker), never operational gloss

        Returns formatted posture string, or None if not an HT token.
        """
        if not self.is_ht:
            return None

        middle = self.morph.middle if self.morph else None
        suffix = self.morph.suffix if self.morph else None

        # Determine form from atom decomposition
        atoms = []
        if middle and hasattr(self, '_mid_analyzer') and self._mid_analyzer:
            atoms = self._mid_analyzer.get_maximal_atoms(middle)
        form = 'compound' if len(atoms) > 1 else 'simple'

        # Posture grammar (expert design):
        # density -> vigilance mode: high=attend, low=hold
        # form -> cognitive load: compound=heavy, simple=light
        density = getattr(self, '_ht_line_density', 'low')
        mode = 'attend' if density == 'high' else 'hold'
        load = 'heavy' if form == 'compound' else 'light'

        # Include atoms for discrimination (expert: "atom data after, not instead of")
        if atoms:
            atom_str = ' + '.join(atoms)
            spec = f"[{mode}-{load} {{{atom_str}}}]"
        elif middle:
            spec = f"[{mode}-{load} {{{middle}}}]"
        else:
            spec = f"[{mode}-{load}]"

        # Suffix as raw form marker (never operational gloss — C404/C405)
        if suffix:
            spec += f" [-{suffix}]"

        return spec

    @staticmethod
    def _get_prefix_lane(prefix: str) -> str:
        """Map prefix to execution lane for display."""
        lanes = {
            'qo': 'QO', 'ok': 'QO', 'ot': 'QO', 'o': 'QO',
            'ko': 'QO', 'to': 'QO', 'po': 'QO',
            'ch': 'CHSH', 'sh': 'CHSH', 'lsh': 'CHSH',
            'pch': 'PREP', 'tch': 'PREP', 'lch': 'PREP', 'dch': 'PREP',
            'fch': 'PREP', 'kch': 'PREP', 'rch': 'PREP', 'sch': 'PREP',
            'da': 'SETUP', 'sa': 'SETUP', 'so': 'SETUP',
            'al': 'CLOSE', 'ar': 'CLOSE', 'or': 'CLOSE', 'ol': 'CLOSE',
            'lk': 'LINK', 'lo': 'LINK',
            'yk': 'INIT', 'ka': 'MAINT', 'ta': 'XFER',
            'ct': 'CTRL', 'ck': 'CTRL',
            'ke': 'KE', 'te': 'TE',
        }
        return lanes.get(prefix, prefix.upper())


@dataclass
class BFolioAnalysis:
    """
    Complete analysis of a Currier B folio.

    Aggregates token-level analysis into folio-level interpretation
    including kernel balance, material category, and output type.
    """
    folio: str
    token_count: int
    tokens: List[BTokenAnalysis]

    # Aggregate distributions
    prefix_role_dist: Dict[str, int]
    suffix_role_dist: Dict[str, int]
    middle_tier_dist: Dict[str, int]
    kernel_dist: Dict[str, int]

    # Interpretations
    kernel_balance: str          # 'ESCAPE_DOMINANT', 'ENERGY_DOMINANT', etc.
    material_category: str       # 'ANIMAL', 'ROOT', 'DELICATE_PLANT'
    output_category: str         # 'WATER', 'OIL', 'PRECISION'

    # Classification rates
    prefix_classified_pct: float
    suffix_classified_pct: float
    middle_classified_pct: float


@dataclass
class BLineAnalysis:
    """
    Line-level analysis of a Currier B control block.

    Lines are boundary-constrained control blocks with free interior (C964).
    Boundaries (SETUP/CLOSE) are positionally constrained; the WORK zone
    interior is an unordered bag of operations (C961).
    """
    line_id: str
    tokens: List[BTokenAnalysis]
    token_count: int

    # Line structure (C357-358)
    has_init_marker: bool        # daiin, saiin at start
    has_final_marker: bool       # am, oly, dy at end
    init_token: Optional[str]    # The actual init token
    final_token: Optional[str]   # The actual final token

    # FL progression through line
    fl_stages: List[str]         # Sequence of FL stages
    fl_progression: str          # 'FORWARD', 'STATIC', 'MIXED'

    # Kernel inventory (C961: WORK zone is unordered, no within-line kernel ordering)
    kernel_sequence: List[str]   # Kernels encountered (order not meaningful per C961)

    # Role sequence
    role_sequence: List[str]     # Sequence of prefix roles

    # Line-level interpretation
    line_type: str               # 'INIT', 'PROCESS', 'TERMINAL', 'ESCAPE', 'HEADER'
    opener_role: Optional[str] = None     # C959: Role of opening token (determines line character)
    is_header: bool = False      # C747/C935: Line-1 HEADER (50% HT, operationally redundant)
    paragraph_zone: Optional[str] = None  # HEADER, SPECIFICATION, EXECUTION (C932, set by paragraph analysis)

    def structural(self) -> str:
        """Tier 0-2 technical line summary."""
        parts = []
        if self.has_init_marker:
            parts.append(f"INIT:{self.init_token}")
        if self.fl_stages:
            parts.append(f"FL:{self.fl_progression}")
        if self.kernel_sequence:
            parts.append(f"kern:[{','.join(self.kernel_sequence)}]")
        if self.has_final_marker:
            parts.append(f"FINAL:{self.final_token}")
        return ' | '.join(parts) if parts else '(no structure)'

    def interpretive(self) -> str:
        """Tier 3-4 human-readable line summary."""
        # C747/C935: Line-1 is HEADER (50% HT, operationally redundant)
        if self.is_header:
            return f"[HEADER] Identification/specification line - {self.token_count} tokens (HT compounds per C935)"

        parts = []

        # Line structure follows SETUP->WORK->CLOSE pattern (C556)
        setup_roles = {'CC_INIT', 'PREP_TIER', 'AX_SCAFFOLD'}
        work_roles = {'EN_KERNEL', 'EN_QO'}
        close_roles = {'AX_LATE', 'FL_FINAL'}

        has_setup = any(r in setup_roles for r in self.role_sequence[:2] if r)
        has_work = any(r in work_roles for r in self.role_sequence)
        has_close = any(r in close_roles for r in self.role_sequence[-2:] if r)

        # Opening
        if self.has_init_marker:
            if self.init_token and 'daiin' in self.init_token:
                parts.append("Begin procedure")
            else:
                parts.append("Start step")
        elif has_setup and 'PREP_TIER' in self.role_sequence[:2]:
            parts.append("Prepare material")

        # Main action based on line type
        type_gloss = {
            'INIT': 'setting up',
            'PROCESS': 'processing material',
            'TERMINAL': 'finishing step',
            'ESCAPE': 'handling exception',
            'MONITOR': 'checking progress',
        }
        if self.line_type in type_gloss:
            parts.append(type_gloss[self.line_type])

        # FL progression
        if self.fl_progression == 'FORWARD':
            parts.append('(progressing)')
        elif self.fl_progression == 'STATIC':
            parts.append('(steady state)')

        # Closing
        if self.has_final_marker:
            parts.append("-> done")

        return ' - '.join(parts) if parts else f"Line with {self.token_count} operations"

    def flow_render(self) -> str:
        """Render line as operations with control-flow labels and inline FL markers.

        Uses ' -> ' for boundary tokens (SETUP/CLOSE) to show sequential structure,
        and ' | ' for WORK zone tokens to reflect unordered interior (C961, C964).
        """
        if not self.tokens:
            return ''

        parts = []
        for tok in self.tokens:
            fg = tok.flow_gloss()
            s = fg['operation']
            if fg['fl_stage']:
                s += f" (FL:{fg['fl_stage']})"
            if fg['flow']:
                s += f" [{fg['flow']}]"
            parts.append((s, tok.prefix_phase))

        # Join with zone-aware separators
        if len(parts) <= 1:
            return parts[0][0] if parts else ''

        result = parts[0][0]
        for i in range(1, len(parts)):
            prev_phase = parts[i-1][1]
            curr_phase = parts[i][1]
            # Boundary-to-boundary or boundary-to-work: sequential arrow
            # Work-to-work: unordered pipe (C961)
            if prev_phase == 'WORK' and curr_phase == 'WORK':
                result += ' | ' + parts[i][0]
            else:
                result += ' -> ' + parts[i][0]
        return result


@dataclass
class BParagraphAnalysis:
    """
    Paragraph-level analysis of a Currier B operational unit.

    CRITICAL: Paragraphs are PARALLEL_PROGRAMS (C855), NOT sequential stages.
    Each paragraph is an independent mini-program. Do NOT assume sequential
    progression between paragraphs.

    Paragraph boundaries detected by gallows-initial lines (C827):
    k, t, p, f at line start indicate new operational unit.
    """
    paragraph_id: str               # P1, P2, P3...
    lines: List[BLineAnalysis]
    line_count: int
    token_count: int

    # Paragraph structure
    boundary_token: Optional[str]   # The gallows token that started this paragraph
    is_gallows_initial: bool        # Did paragraph start with gallows?

    # Aggregate from lines
    kernel_dist: Dict[str, int]
    role_dist: Dict[str, int]
    fl_distribution: Dict[str, int]  # INITIAL/EARLY/MEDIAL/LATE/TERMINAL counts

    # Line type composition
    init_lines: int                 # Lines with init markers
    process_lines: int              # Normal processing lines
    escape_lines: int               # Lines with backward FL
    terminal_lines: int             # Lines with terminal markers

    # Paragraph characterization
    kernel_balance: str             # ESCAPE_DOMINANT, ENERGY_DOMINANT, etc.
    dominant_role: Optional[str]    # Most common prefix role
    fl_trend: str                   # EARLY_HEAVY, LATE_HEAVY, DISTRIBUTED

    # Paragraph zones (C932: execution gradient)
    zone_distribution: Dict[str, int] = None  # {'HEADER': 1, 'SPECIFICATION': 3, 'EXECUTION': 5}

    # Spec→exec gradient (C933/C934)
    spec_ht_rate: float = 0.0       # HT fraction in SPECIFICATION zone
    exec_ht_rate: float = 0.0       # HT fraction in EXECUTION zone
    gradient_direction: str = 'FLAT' # SPEC_TO_EXEC or FLAT

    def structural(self) -> str:
        """Tier 0-2 technical paragraph summary."""
        parts = [f"{self.paragraph_id}"]
        if self.boundary_token:
            parts.append(f"({self.boundary_token})")
        parts.append(f": {self.line_count}L/{self.token_count}T")

        if self.kernel_dist:
            k_str = ','.join(f"{k}:{v}" for k, v in sorted(self.kernel_dist.items()))
            parts.append(f"kern=[{k_str}]")

        parts.append(f"type=[{self.kernel_balance}]")
        if self.dominant_role:
            parts.append(f"role={self.dominant_role}")

        if self.zone_distribution:
            zone_str = '/'.join(f"{z[0]}:{c}" for z, c in sorted(self.zone_distribution.items()))
            parts.append(f"zones=[{zone_str}]")

        return ' | '.join(parts)

    def interpretive(self) -> str:
        """Tier 3-4 human-readable paragraph summary."""
        parts = []

        # Kernel balance interpretation
        balance_gloss = {
            'ESCAPE_DOMINANT': "Waiting/settling phase",
            'ENERGY_DOMINANT': "Active heating phase",
            'HAZARD_HEAVY': "Careful monitoring phase",
            'BALANCED': "Mixed operations",
            'NO_KERNELS': "Control/setup phase",
        }
        parts.append(balance_gloss.get(self.kernel_balance, self.kernel_balance))

        # Line composition hint
        if self.escape_lines > self.line_count * 0.3:
            parts.append("with exception handling")
        if self.init_lines > 0:
            parts.append("with initialization")
        if self.terminal_lines > 0:
            parts.append("to completion")

        # FL trend
        fl_gloss = {
            'EARLY_HEAVY': "(early-stage focus)",
            'LATE_HEAVY': "(late-stage focus)",
            'TERMINAL_HEAVY': "(finishing)",
        }
        if self.fl_trend in fl_gloss:
            parts.append(fl_gloss[self.fl_trend])

        if self.gradient_direction == 'SPEC_TO_EXEC':
            parts.append("(spec->exec gradient)")

        return ' - '.join(parts) if parts else f"Paragraph with {self.line_count} steps"


class BFolioDecoder:
    """
    Decoder for Currier B folios using consolidated structural knowledge.

    Uses constraints: C371-378, C510-522, C766-769, C884, C906-907,
                     F-BRU-011, F-BRU-018-020

    Two output modes:
    - Structural (Tier 0-2): Technical constraint-based terminology
    - Interpretive (Tier 3-4): Brunschwig-grounded human-readable

    Example:
        decoder = BFolioDecoder()
        analysis = decoder.analyze_folio('f107r')
        print(analysis.kernel_balance)      # 'ESCAPE_DOMINANT'
        print(analysis.material_category)   # 'ANIMAL'
        print(decoder.decode_summary('f107r'))
    """

    # Maps are loaded from data/decoder_maps.json at init.
    # See that file for constraint citations per entry.
    DECODER_MAPS_PATH = PROJECT_ROOT / 'data' / 'decoder_maps.json'

    @classmethod
    def _load_maps(cls) -> dict:
        """Load decoder maps from external JSON file."""
        with open(cls.DECODER_MAPS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['maps']

    @staticmethod
    def _extract_simple(map_data: dict) -> dict:
        """Extract {key: value} from map entries."""
        return {k: v['value'] for k, v in map_data['entries'].items()}

    @staticmethod
    def _extract_tuple(map_data: dict) -> dict:
        """Extract {key: (category, gloss)} from map entries."""
        return {k: (v['category'], v['gloss']) for k, v in map_data['entries'].items()}

    def __init__(self):
        self.tx = Transcript()
        self.morph = Morphology()
        self.token_dict = TokenDictionary()
        self.middle_dict = MiddleDictionary()

        # MiddleAnalyzer for compound MIDDLE decomposition (C872, C522)
        self.mid_analyzer = MiddleAnalyzer()
        self.mid_analyzer.build_inventory('B')

        # Load maps from external JSON
        maps = self._load_maps()

        # Simple string-value maps
        self.PREFIX_PHASE = self._extract_simple(maps['prefix_phase'])
        self.PREFIX_ROLES = self._extract_simple(maps['prefix_roles'])
        self.SUFFIX_GLOSS = self._extract_simple(maps['suffix_gloss'])
        self.SUFFIX_TERMINAL = self._extract_simple(maps['suffix_terminal'])
        self.SUFFIX_ROLES = self._extract_simple(maps['suffix_roles'])
        self.PREFIX_ACTIONS = self._extract_simple(maps['prefix_actions'])
        self.BRUNSCHWIG_GLOSS = self._extract_simple(maps['brunschwig_gloss'])
        self.MIDDLE_KERNEL_PROFILE = self._extract_simple(maps['middle_kernel_profile'])
        self.MIDDLE_REGIME = self._extract_simple(maps['middle_regime'])
        self.MIDDLE_SECTION = self._extract_simple(maps['middle_section'])

        # Dict-value maps (suffix_flow: {key: {value, flow_type}})
        self.SUFFIX_FLOW = {k: v for k, v in maps['suffix_flow']['entries'].items()}

        # Tuple-value maps (category, gloss)
        self.MIDDLE_TIERS = self._extract_tuple(maps['middle_tiers'])
        self.FL_STAGE_MAP = self._extract_tuple(maps['fl_stage_map'])
        self.CC_TOKENS = self._extract_tuple(maps['cc_tokens'])

        # Simple list
        self.KERNEL_CHARS = maps['kernel_chars']['value']

        # Pre-sort substring-matching maps (longest first) for _get_*() methods
        self._middle_tiers_sorted = sorted(
            self.MIDDLE_TIERS.items(), key=lambda x: len(x[0]), reverse=True)
        self._middle_kernel_sorted = sorted(
            [(k, v) for k, v in self.MIDDLE_KERNEL_PROFILE.items() if v],
            key=lambda x: len(x[0]), reverse=True)
        self._middle_regime_sorted = sorted(
            self.MIDDLE_REGIME.items(), key=lambda x: len(x[0]), reverse=True)
        self._middle_section_sorted = sorted(
            self.MIDDLE_SECTION.items(), key=lambda x: len(x[0]), reverse=True)

        # Caches for expensive lookups
        self._cache_middle_tier = {}
        self._cache_middle_kernel = {}
        self._cache_middle_regime = {}
        self._cache_middle_section = {}

        # Pre-compute which tokens need regime for collision breaking.
        # Default: kernel-only gloss. Regime appended only when two tokens
        # with different regime would otherwise render the same gloss.
        # Initialize empty first (analyze_token refs this during build).
        self._needs_regime = set()
        self._needs_regime = self._build_regime_need_set()

    def _build_regime_need_set(self) -> set:
        """Pre-compute set of words that need regime suffix for disambiguation.

        Strategy:
        1. For each unique B token, compute its gloss with kernel only (no regime)
        2. Group tokens by that kernel-only gloss string
        3. For collision groups (2+ tokens → same gloss): check if members
           have different middle_regime values
        4. If regime would split the group, mark those words as needing regime

        Returns:
            Set of word strings that should display regime in their gloss.
        """
        needs_regime = set()
        # Collect unique words with kernel-only glosses
        # Use a lightweight approach: analyze each word, compute gloss parts
        seen = set()
        word_data = []  # (word, kernel_only_gloss, middle_regime)

        for token in self.tx.currier_b():
            w = token.word
            if '*' in w or not w.strip() or w in seen:
                continue
            seen.add(w)
            analysis = self.analyze_token(w)
            # Skip HT tokens (they use posture grammar, not kernel/regime)
            if analysis.is_ht:
                continue
            regime = analysis.middle_regime
            if not analysis.middle_kernel:
                continue  # No kernel = no regime question

            # Compute kernel-only gloss (suppress regime temporarily)
            saved_regime = analysis.middle_regime
            analysis.middle_regime = None
            gloss = analysis.interpretive()
            analysis.middle_regime = saved_regime

            word_data.append((w, gloss, regime))

        # Group by kernel-only gloss
        from collections import defaultdict
        gloss_groups = defaultdict(list)
        for w, gloss, regime in word_data:
            gloss_groups[gloss].append((w, regime))

        # Find collision groups where regime would help
        for gloss, members in gloss_groups.items():
            if len(members) < 2:
                continue
            regimes = set(r for _, r in members if r)
            if len(regimes) > 1:
                # Different regimes in this collision group — mark all for regime
                for w, _ in members:
                    needs_regime.add(w)

        return needs_regime

    def _get_prefix_role(self, prefix: Optional[str]) -> Optional[str]:
        """Get functional role for a prefix (C371-374)."""
        if prefix and prefix in self.PREFIX_ROLES:
            return self.PREFIX_ROLES[prefix]
        return None

    def _get_suffix_role(self, suffix: Optional[str]) -> Optional[str]:
        """Get functional role for a suffix (C375-378)."""
        if suffix and suffix in self.SUFFIX_ROLES:
            return self.SUFFIX_ROLES[suffix]
        return None

    def _get_middle_tier(self, middle: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Get tier and meaning for a MIDDLE (F-BRU-011)."""
        if not middle:
            return None, None
        if middle in self._cache_middle_tier:
            return self._cache_middle_tier[middle]

        # Direct match
        if middle in self.MIDDLE_TIERS:
            result = self.MIDDLE_TIERS[middle]
        else:
            # Check for contained patterns (pre-sorted longest first)
            result = (None, None)
            for mid, (tier, meaning) in self._middle_tiers_sorted:
                if mid in middle and len(mid) >= 2:
                    result = (tier, f"contains {mid}")
                    break

        self._cache_middle_tier[middle] = result
        return result

    def _get_kernels(self, middle: Optional[str]) -> List[str]:
        """Extract kernel characters from MIDDLE."""
        if not middle:
            return []
        return [k for k in self.KERNEL_CHARS if k in middle]

    def _get_material_markers(self, m: MorphAnalysis) -> List[str]:
        """Detect material category markers (C884, F-BRU-018)."""
        markers = []

        # Animal markers from suffix (C884)
        if m.suffix in ['ey', 'ol', 'eey', 'or']:
            markers.append('ANIMAL')

        # Root markers from MIDDLE (F-BRU-018)
        if m.middle and ('tch' in m.middle or 'pch' in m.middle):
            markers.append('ROOT')

        return markers

    def _get_output_markers(self, m: MorphAnalysis) -> List[str]:
        """Detect output category markers (F-BRU-020)."""
        markers = []

        # OIL markers from MIDDLE
        if m.middle and any(oil in m.middle for oil in ['kc', 'okch']):
            markers.append('OIL')

        # WATER markers from suffix
        if m.suffix in ['ly', 'al']:
            markers.append('WATER')

        return markers

    def _get_fl_stage(self, word: str, m: MorphAnalysis) -> Tuple[Optional[str], Optional[str]]:
        """
        Get FL state stage for a token (C777, FL_SEMANTIC_INTERPRETATION).

        FL state markers are standalone tokens or MIDDLEs that index
        material position in transformation process.

        Priority:
        1. Token dictionary (pre-computed, v6+)
        2. CC control token check
        3. FL_STAGE_MAP fallback
        """
        # 1. Check token dictionary first (pre-computed FL state)
        entry = self.token_dict.get(word)
        if entry and entry.get('fl_state'):
            return entry['fl_state'], entry.get('fl_meaning')

        # 2. Check if whole word is a CC control token
        if word in self.CC_TOKENS:
            role, meaning = self.CC_TOKENS[word]
            return f"CC_{role}", meaning

        # 3. Fall back to FL_STAGE_MAP computation
        middle = m.middle if m.middle else word

        if middle in self.FL_STAGE_MAP:
            return self.FL_STAGE_MAP[middle]

        # For tokens without prefix, check if the word itself is FL-like
        if not m.prefix and word in self.FL_STAGE_MAP:
            return self.FL_STAGE_MAP[word]

        return None, None

    def _get_middle_kernel(self, middle: Optional[str]) -> Optional[str]:
        """Get kernel profile for a MIDDLE (MIDDLE_SEMANTIC_MAPPING phase)."""
        if not middle:
            return None
        if middle in self._cache_middle_kernel:
            return self._cache_middle_kernel[middle]
        # Direct lookup
        if middle in self.MIDDLE_KERNEL_PROFILE:
            result = self.MIDDLE_KERNEL_PROFILE[middle]
        else:
            # Check for contained patterns (pre-sorted longest first, non-None only)
            result = None
            for mid, kernel in self._middle_kernel_sorted:
                if mid in middle and len(mid) >= 2:
                    result = kernel
                    break
        self._cache_middle_kernel[middle] = result
        return result

    def _get_middle_regime(self, middle: Optional[str]) -> Optional[str]:
        """Get execution regime for a MIDDLE (MIDDLE_SEMANTIC_MAPPING phase)."""
        if not middle:
            return None
        if middle in self._cache_middle_regime:
            return self._cache_middle_regime[middle]
        # Direct lookup
        if middle in self.MIDDLE_REGIME:
            result = self.MIDDLE_REGIME[middle]
        else:
            result = None
            for mid, regime in self._middle_regime_sorted:
                if mid in middle and len(mid) >= 2:
                    result = regime
                    break
        self._cache_middle_regime[middle] = result
        return result

    def _get_middle_section(self, middle: Optional[str]) -> Optional[str]:
        """Get section affinity for a MIDDLE (MIDDLE_SEMANTIC_MAPPING phase)."""
        if not middle:
            return None
        if middle in self._cache_middle_section:
            return self._cache_middle_section[middle]
        # Direct lookup
        if middle in self.MIDDLE_SECTION:
            result = self.MIDDLE_SECTION[middle]
        else:
            result = None
            for mid, section in self._middle_section_sorted:
                if mid in middle and len(mid) >= 2:
                    result = section
                    break
        self._cache_middle_section[middle] = result
        return result

    def analyze_token(self, word: str,
                      line_initial: bool = False,
                      line_final: bool = False) -> BTokenAnalysis:
        """
        Complete analysis of a single Currier B token.

        Args:
            word: The token string
            line_initial: Whether token is at line start
            line_final: Whether token is at line end

        Returns:
            BTokenAnalysis with all classifications
        """
        m = self.morph.extract(word)
        tier, meaning = self._get_middle_tier(m.middle)
        fl_stage, fl_meaning = self._get_fl_stage(word, m)

        # Get FL role and HT status from token dictionary
        entry = self.token_dict.get(word)
        is_fl_role = entry.get('is_fl_role', False) if entry else False

        # FL exclusion: known FQ/CC tokens that use FL-compatible characters
        # but are NOT FL (C583: aiin=FQ Class 9, C557: daiin=CC Class 10)
        FL_EXCLUDED = {'aiin', 'ain', 'oaiin'}
        if word in FL_EXCLUDED:
            is_fl_role = False
        # HT (Human Track) = UNKNOWN role in token dictionary (C740, C872)
        is_ht = entry.get('role', {}).get('primary') == 'UNKNOWN' if entry else False

        # Get prefix role
        prefix_role = self._get_prefix_role(m.prefix)

        # For PREP_TIER prefixes, use specific F-BRU-012 action instead of generic MIDDLE tier
        if prefix_role == 'PREP_TIER' and m.prefix in self.PREFIX_ACTIONS:
            meaning = self.PREFIX_ACTIONS[m.prefix]
            tier = 'PREP'

        analysis = BTokenAnalysis(
            word=word,
            morph=m,
            prefix_role=prefix_role,
            suffix_role=self._get_suffix_role(m.suffix),
            middle_tier=tier,
            middle_meaning=meaning,
            fl_stage=fl_stage,
            fl_meaning=fl_meaning,
            is_fl_role=is_fl_role,
            is_ht=is_ht,
            kernels=self._get_kernels(m.middle),
            material_markers=self._get_material_markers(m),
            output_markers=self._get_output_markers(m),
            is_line_initial=line_initial,
            is_line_final=line_final,
            prefix_phase=self.PREFIX_PHASE.get(m.prefix),
            suffix_terminal=self.SUFFIX_TERMINAL.get(m.suffix),
            middle_kernel=self._get_middle_kernel(m.middle),
            middle_regime=self._get_middle_regime(m.middle),
            middle_section=self._get_middle_section(m.middle),
        )
        # Pass references for whole-token, middle, suffix gloss, and prep action lookup
        analysis._token_dict = self.token_dict
        analysis._middle_dict = self.middle_dict
        analysis._suffix_gloss = self.SUFFIX_GLOSS
        analysis._suffix_flow = self.SUFFIX_FLOW
        analysis._prefix_actions = self.PREFIX_ACTIONS
        analysis._middle_tiers = self.MIDDLE_TIERS
        analysis._mid_analyzer = self.mid_analyzer
        analysis._needs_regime = self._needs_regime
        return analysis

    def _interpret_kernel_balance(self, kernel_dist: Dict[str, int]) -> str:
        """Interpret kernel distribution as process characterization."""
        total = sum(kernel_dist.values())
        if total == 0:
            return 'NO_KERNELS'

        k_pct = kernel_dist.get('k', 0) / total
        h_pct = kernel_dist.get('h', 0) / total
        e_pct = kernel_dist.get('e', 0) / total

        if e_pct > 0.45:
            return 'ESCAPE_DOMINANT'
        elif k_pct > 0.50:
            return 'ENERGY_DOMINANT'
        elif h_pct > 0.30:
            return 'HAZARD_HEAVY'
        else:
            return 'BALANCED'

    def _interpret_material_category(self, tokens: List[BTokenAnalysis]) -> str:
        """Interpret material category from token markers."""
        animal_count = sum(1 for t in tokens if 'ANIMAL' in t.material_markers)
        root_count = sum(1 for t in tokens if 'ROOT' in t.material_markers)
        total = len(tokens)

        # Threshold for detection (5% of tokens)
        if animal_count > total * 0.05:
            return 'ANIMAL'
        elif root_count > total * 0.03:
            return 'ROOT'
        else:
            return 'DELICATE_PLANT'  # Unmarked default (F-BRU-019)

    def _interpret_output_category(self, tokens: List[BTokenAnalysis]) -> str:
        """Interpret output category from token markers."""
        oil_count = sum(1 for t in tokens if 'OIL' in t.output_markers)
        water_count = sum(1 for t in tokens if 'WATER' in t.output_markers)
        total = len(tokens)

        if oil_count > total * 0.02:
            return 'OIL'
        elif water_count > total * 0.05:
            return 'WATER'
        else:
            return 'WATER'  # Default

    # === LINE-LEVEL MARKERS (C357-358) ===
    LINE_INIT_MARKERS = {'daiin', 'saiin', 'sain', 'dain'}  # 3-11x enriched at line start
    LINE_FINAL_MARKERS = {'am', 'oly', 'dy', 'om'}  # 4-31x enriched at line end

    # === PARAGRAPH DETECTION (C827) ===
    # Gallows characters mark paragraph boundaries when line-initial
    # These are the tall looped characters in EVA: k, t, p, f
    GALLOWS_CHARS = {'k', 't', 'p', 'f'}

    def _is_gallows_initial(self, word: str) -> bool:
        """Check if a word starts with a gallows character (k, t, p, f)."""
        if not word:
            return False
        return word[0] in self.GALLOWS_CHARS

    def analyze_line(self, line_tokens: List[BTokenAnalysis], line_id: str) -> BLineAnalysis:
        """
        Analyze a line as a control block (C357).

        Args:
            line_tokens: List of BTokenAnalysis for this line
            line_id: Line identifier

        Returns:
            BLineAnalysis with line-level interpretation
        """
        if not line_tokens:
            return BLineAnalysis(
                line_id=line_id, tokens=[], token_count=0,
                has_init_marker=False, has_final_marker=False,
                init_token=None, final_token=None,
                fl_stages=[], fl_progression='EMPTY',
                kernel_sequence=[],
                role_sequence=[], line_type='EMPTY',
                is_header=(line_id == '1')
            )

        # Check for init/final markers
        first_word = line_tokens[0].word if line_tokens else ''
        last_word = line_tokens[-1].word if line_tokens else ''

        has_init = first_word in self.LINE_INIT_MARKERS
        has_final = last_word in self.LINE_FINAL_MARKERS

        # Collect FL stages through line
        fl_stages = [t.fl_stage for t in line_tokens if t.fl_stage and not t.fl_stage.startswith('CC_')]

        # Determine FL progression
        if len(fl_stages) < 2:
            fl_progression = 'STATIC'
        else:
            stage_order = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'TERMINAL': 4}
            stage_nums = [stage_order.get(s, 2) for s in fl_stages]
            if all(stage_nums[i] <= stage_nums[i+1] for i in range(len(stage_nums)-1)):
                fl_progression = 'FORWARD'
            elif all(stage_nums[i] >= stage_nums[i+1] for i in range(len(stage_nums)-1)):
                fl_progression = 'BACKWARD'
            else:
                fl_progression = 'MIXED'

        # Collect kernel inventory (C961: order not meaningful within WORK zone)
        kernel_sequence = []
        for t in line_tokens:
            for k in t.kernels:
                if k not in kernel_sequence[-1:]:  # Avoid consecutive duplicates
                    kernel_sequence.append(k)

        # Collect role sequence
        role_sequence = [t.prefix_role for t in line_tokens if t.prefix_role]

        # C747/C935: Line-1 is HEADER (HT = operationally redundant compounds)
        is_header = (line_id == '1')

        # Determine line type
        if is_header:
            line_type = 'HEADER'
        elif has_init:
            line_type = 'INIT'
        elif has_final and any(s in ['TERMINAL', 'LATE'] for s in fl_stages):
            line_type = 'TERMINAL'
        elif 'FQ' in str(role_sequence):
            line_type = 'ESCAPE'
        elif 'AX_LATE' in role_sequence or 'EN_KERNEL' in role_sequence:
            line_type = 'MONITOR' if 'AX_LATE' in role_sequence else 'PROCESS'
        else:
            line_type = 'PROCESS'

        # C959: Opener role determines line character (not specific token)
        opener_role = line_tokens[0].prefix_role if line_tokens else None

        # Set HT density on HT tokens (for spec bundle rendering)
        # C747: header lines have ~50% HT; density=high when HT >= 40% of line
        ht_count = sum(1 for t in line_tokens if t.is_ht)
        if ht_count > 0:
            ht_density = 'high' if ht_count >= len(line_tokens) * 0.4 else 'low'
            for t in line_tokens:
                if t.is_ht:
                    t._ht_line_density = ht_density

        return BLineAnalysis(
            line_id=line_id,
            tokens=line_tokens,
            token_count=len(line_tokens),
            has_init_marker=has_init,
            has_final_marker=has_final,
            init_token=first_word if has_init else None,
            final_token=last_word if has_final else None,
            fl_stages=fl_stages,
            fl_progression=fl_progression,
            kernel_sequence=kernel_sequence,
            role_sequence=role_sequence,
            line_type=line_type,
            opener_role=opener_role,
            is_header=is_header,
        )

    def analyze_folio_lines(self, folio: str) -> List[BLineAnalysis]:
        """
        Analyze all lines in a folio as control blocks.

        Args:
            folio: Folio identifier

        Returns:
            List of BLineAnalysis, one per line
        """
        # Get folio tokens grouped by line
        folio_tokens = [t for t in self.tx.currier_b() if t.folio == folio]
        if not folio_tokens:
            return []

        # Group by line
        lines = defaultdict(list)
        for t in folio_tokens:
            analysis = self.analyze_token(t.word, t.line_initial, t.line_final)
            lines[t.line].append(analysis)

        # Analyze each line (sort numerically by line ID)
        def line_sort_key(item):
            line_id = item[0]
            try:
                return (0, int(line_id))
            except (ValueError, TypeError):
                return (1, str(line_id))
        return [self.analyze_line(tokens, line_id)
                for line_id, tokens in sorted(lines.items(), key=line_sort_key)]

    def _analyze_paragraph(self, lines: List[BLineAnalysis], para_id: str,
                           boundary_token: Optional[str]) -> BParagraphAnalysis:
        """
        Analyze a paragraph (operational unit) from its constituent lines.

        Args:
            lines: List of BLineAnalysis for this paragraph
            para_id: Paragraph identifier (P1, P2, etc.)
            boundary_token: The gallows token that started this paragraph (if any)

        Returns:
            BParagraphAnalysis with aggregate statistics
        """
        if not lines:
            return BParagraphAnalysis(
                paragraph_id=para_id, lines=[], line_count=0, token_count=0,
                boundary_token=None, is_gallows_initial=False,
                kernel_dist={}, role_dist={}, fl_distribution={},
                init_lines=0, process_lines=0, escape_lines=0, terminal_lines=0,
                kernel_balance='NO_KERNELS', dominant_role=None, fl_trend='DISTRIBUTED',
                zone_distribution={},
            )

        # Aggregate from lines
        token_count = sum(la.token_count for la in lines)
        kernel_dist = Counter()
        role_dist = Counter()
        fl_dist = Counter()

        for la in lines:
            for k in la.kernel_sequence:
                kernel_dist[k] += 1
            for r in la.role_sequence:
                role_dist[r] += 1
            for fl in la.fl_stages:
                fl_dist[fl] += 1

        # Line type counts
        init_lines = sum(1 for la in lines if la.line_type == 'INIT')
        process_lines = sum(1 for la in lines if la.line_type == 'PROCESS')
        escape_lines = sum(1 for la in lines if la.line_type == 'ESCAPE')
        terminal_lines = sum(1 for la in lines if la.line_type == 'TERMINAL')

        # Interpret kernel balance
        kernel_balance = self._interpret_kernel_balance(kernel_dist)

        # Find dominant role
        dominant_role = None
        if role_dist:
            dominant_role = max(role_dist.keys(), key=lambda r: role_dist[r])

        # Determine FL trend
        early_count = fl_dist.get('INITIAL', 0) + fl_dist.get('EARLY', 0)
        late_count = fl_dist.get('LATE', 0) + fl_dist.get('TERMINAL', 0)
        total_fl = sum(fl_dist.values())

        if total_fl == 0:
            fl_trend = 'DISTRIBUTED'
        elif fl_dist.get('TERMINAL', 0) > total_fl * 0.3:
            fl_trend = 'TERMINAL_HEAVY'
        elif late_count > total_fl * 0.5:
            fl_trend = 'LATE_HEAVY'
        elif early_count > total_fl * 0.5:
            fl_trend = 'EARLY_HEAVY'
        else:
            fl_trend = 'DISTRIBUTED'

        # C932: Paragraph zone assignment (HEADER / SPECIFICATION / EXECUTION)
        n = len(lines)
        zone_dist = Counter()
        for i, la in enumerate(lines):
            pos = i / max(n - 1, 1)
            if i == 0:
                la.paragraph_zone = 'HEADER'
            elif pos < 0.4:
                la.paragraph_zone = 'SPECIFICATION'
            else:
                la.paragraph_zone = 'EXECUTION'
            zone_dist[la.paragraph_zone] += 1

        # C933/C934: spec→exec vocabulary gradient (HT concentration as proxy)
        spec_tokens = [t for la in lines if la.paragraph_zone == 'SPECIFICATION'
                       for t in la.tokens]
        exec_tokens = [t for la in lines if la.paragraph_zone == 'EXECUTION'
                       for t in la.tokens]
        spec_ht = (sum(1 for t in spec_tokens if t.is_ht) / max(len(spec_tokens), 1))
        exec_ht = (sum(1 for t in exec_tokens if t.is_ht) / max(len(exec_tokens), 1))
        gradient = 'SPEC_TO_EXEC' if spec_ht > exec_ht else 'FLAT'

        return BParagraphAnalysis(
            paragraph_id=para_id,
            lines=lines,
            line_count=len(lines),
            token_count=token_count,
            boundary_token=boundary_token,
            is_gallows_initial=boundary_token is not None,
            kernel_dist=dict(kernel_dist),
            role_dist=dict(role_dist),
            fl_distribution=dict(fl_dist),
            init_lines=init_lines,
            process_lines=process_lines,
            escape_lines=escape_lines,
            terminal_lines=terminal_lines,
            kernel_balance=kernel_balance,
            dominant_role=dominant_role,
            fl_trend=fl_trend,
            zone_distribution=dict(zone_dist),
            spec_ht_rate=spec_ht,
            exec_ht_rate=exec_ht,
            gradient_direction=gradient,
        )

    def analyze_folio_paragraphs(self, folio: str) -> List[BParagraphAnalysis]:
        """
        Analyze all paragraphs in a folio as independent operational units.

        CRITICAL: Paragraphs are PARALLEL_PROGRAMS (C855), NOT sequential stages.
        Each paragraph is an independent mini-program. The analysis does NOT
        assume any progression between paragraphs.

        Paragraph boundaries detected by gallows-initial lines (C827).

        Args:
            folio: Folio identifier

        Returns:
            List of BParagraphAnalysis, one per paragraph
        """
        line_analyses = self.analyze_folio_lines(folio)
        if not line_analyses:
            return []

        # Group lines into paragraphs by gallows-initial heuristic
        paragraphs = []
        current_para_lines = []
        current_boundary = None
        para_count = 0

        for la in line_analyses:
            # Check if this line starts a new paragraph
            first_word = la.tokens[0].word if la.tokens else ''
            is_boundary = self._is_gallows_initial(first_word)

            if is_boundary and current_para_lines:
                # Save current paragraph and start new one
                para_count += 1
                para = self._analyze_paragraph(
                    current_para_lines,
                    f"P{para_count}",
                    current_boundary
                )
                paragraphs.append(para)
                current_para_lines = [la]
                current_boundary = first_word
            else:
                current_para_lines.append(la)
                if is_boundary and current_boundary is None:
                    current_boundary = first_word

        # Don't forget the last paragraph
        if current_para_lines:
            para_count += 1
            para = self._analyze_paragraph(
                current_para_lines,
                f"P{para_count}",
                current_boundary
            )
            paragraphs.append(para)

        return paragraphs

    def decode_folio_paragraphs(self, folio: str, mode: str = 'structural') -> str:
        """
        Generate paragraph-level decode of a folio.

        IMPORTANT: Paragraphs are INDEPENDENT operational units (C855).
        They do NOT represent sequential stages of a single procedure.

        Args:
            folio: Folio identifier
            mode: 'structural' or 'interpretive'

        Returns:
            Multi-line string with paragraph-level analysis
        """
        para_analyses = self.analyze_folio_paragraphs(folio)
        if not para_analyses:
            return f"No paragraphs found for folio {folio}"

        output = [f"{'=' * 60}"]
        output.append(f"FOLIO {folio}: {len(para_analyses)} paragraphs (PARALLEL_PROGRAMS)")
        output.append(f"NOTE: Paragraphs are INDEPENDENT units, not sequential stages (C855)")
        output.append(f"{'=' * 60}")

        for pa in para_analyses:
            output.append("")
            if mode == 'structural':
                output.append(f"--- {pa.structural()} ---")
                output.append(f"    Lines: {pa.line_count} | Tokens: {pa.token_count}")
                output.append(f"    Types: init={pa.init_lines}, process={pa.process_lines}, "
                            f"escape={pa.escape_lines}, terminal={pa.terminal_lines}")
                output.append(f"    FL trend: {pa.fl_trend}")
                if pa.gradient_direction == 'SPEC_TO_EXEC':
                    output.append(f"    Gradient: SPEC({pa.spec_ht_rate:.0%} HT) -> EXEC({pa.exec_ht_rate:.0%} HT)")

                # Show line summaries
                for la in pa.lines[:3]:  # First 3 lines
                    zone_tag = f"[{la.paragraph_zone}] " if la.paragraph_zone else ""
                    output.append(f"      L{la.line_id}: {zone_tag}{la.structural()}")
                if len(pa.lines) > 3:
                    output.append(f"      ... ({len(pa.lines) - 3} more lines)")
            else:
                output.append(f"--- {pa.paragraph_id}: {pa.interpretive()} ---")
                output.append(f"    ({pa.line_count} steps, {pa.token_count} operations)")

                # Show line interpretations
                for la in pa.lines[:3]:
                    output.append(f"      Step: {la.interpretive()}")
                if len(pa.lines) > 3:
                    output.append(f"      ... ({len(pa.lines) - 3} more steps)")

        return '\n'.join(output)

    def decode_folio_lines(self, folio: str, mode: str = 'structural') -> str:
        """
        Generate line-by-line decode of a folio.

        Args:
            folio: Folio identifier
            mode: 'structural' or 'interpretive'

        Returns:
            Multi-line string with line-level analysis
        """
        line_analyses = self.analyze_folio_lines(folio)
        if not line_analyses:
            return f"No lines found for folio {folio}"

        output = [f"{'=' * 60}"]
        output.append(f"FOLIO {folio}: {len(line_analyses)} lines")
        output.append(f"{'=' * 60}")

        for la in line_analyses:
            if mode == 'structural':
                output.append(f"\nLine {la.line_id} ({la.token_count} tokens): {la.structural()}")
                # Show first few tokens
                for t in la.tokens[:4]:
                    output.append(f"    {t.word:12} {t.structural()}")
            else:
                output.append(f"\nLine {la.line_id}: {la.interpretive()}")
                # Show token glosses
                for t in la.tokens[:4]:
                    output.append(f"    {t.word:12} -> {t.interpretive()}")

        return '\n'.join(output)

    def analyze_folio(self, folio: str) -> Optional[BFolioAnalysis]:
        """
        Complete analysis of a Currier B folio.

        Args:
            folio: Folio identifier (e.g., 'f107r')

        Returns:
            BFolioAnalysis with aggregate statistics and interpretations,
            or None if folio not found
        """
        # Get folio tokens
        folio_tokens = [t for t in self.tx.currier_b() if t.folio == folio]
        if not folio_tokens:
            return None

        # Analyze each token
        analyses = []
        lines = defaultdict(list)
        for t in folio_tokens:
            lines[t.line].append(t)

        for line_id, line_tokens in lines.items():
            for i, t in enumerate(line_tokens):
                analysis = self.analyze_token(
                    t.word,
                    line_initial=(i == 0),
                    line_final=(i == len(line_tokens) - 1)
                )
                analyses.append(analysis)

        # Aggregate distributions
        prefix_dist = Counter(a.prefix_role for a in analyses if a.prefix_role)
        suffix_dist = Counter(a.suffix_role for a in analyses if a.suffix_role)
        middle_dist = Counter(a.middle_tier for a in analyses if a.middle_tier)
        kernel_dist = Counter()
        for a in analyses:
            for k in a.kernels:
                kernel_dist[k] += 1

        total = len(analyses)

        return BFolioAnalysis(
            folio=folio,
            token_count=total,
            tokens=analyses,
            prefix_role_dist=dict(prefix_dist),
            suffix_role_dist=dict(suffix_dist),
            middle_tier_dist=dict(middle_dist),
            kernel_dist=dict(kernel_dist),
            kernel_balance=self._interpret_kernel_balance(kernel_dist),
            material_category=self._interpret_material_category(analyses),
            output_category=self._interpret_output_category(analyses),
            prefix_classified_pct=100 * sum(prefix_dist.values()) / total if total else 0,
            suffix_classified_pct=100 * sum(suffix_dist.values()) / total if total else 0,
            middle_classified_pct=100 * sum(middle_dist.values()) / total if total else 0,
        )

    def decode_summary(self, folio: str, mode: str = 'structural') -> str:
        """
        Generate human-readable summary of a folio.

        Args:
            folio: Folio identifier
            mode: 'structural' (Tier 0-2) or 'interpretive' (Tier 3-4)

        Returns:
            Multi-line summary string
        """
        analysis = self.analyze_folio(folio)
        if not analysis:
            return f"Folio {folio} not found in Currier B"

        lines = [f"{'=' * 60}"]
        lines.append(f"FOLIO {folio}: {analysis.token_count} tokens")
        lines.append(f"{'=' * 60}")

        if mode == 'structural':
            # Tier 0-2 technical output
            lines.append(f"\nPREFIX ROLES (C371-374):")
            lines.append(f"  Classified: {analysis.prefix_classified_pct:.1f}%")
            for role, count in sorted(analysis.prefix_role_dist.items(),
                                       key=lambda x: -x[1]):
                pct = 100 * count / analysis.token_count
                lines.append(f"  {role:12}: {count:4} ({pct:5.1f}%)")

            lines.append(f"\nSUFFIX ROLES (C375-378):")
            lines.append(f"  Classified: {analysis.suffix_classified_pct:.1f}%")
            for role, count in sorted(analysis.suffix_role_dist.items(),
                                       key=lambda x: -x[1]):
                pct = 100 * count / analysis.token_count
                lines.append(f"  {role:12}: {count:4} ({pct:5.1f}%)")

            lines.append(f"\nMIDDLE TIERS (F-BRU-011):")
            lines.append(f"  Classified: {analysis.middle_classified_pct:.1f}%")
            for tier, count in sorted(analysis.middle_tier_dist.items(),
                                       key=lambda x: -x[1]):
                pct = 100 * count / analysis.token_count
                lines.append(f"  {tier:12}: {count:4} ({pct:5.1f}%)")

            lines.append(f"\nKERNEL DISTRIBUTION:")
            kernel_total = sum(analysis.kernel_dist.values())
            for k in ['k', 'h', 'e']:
                if kernel_total > 0:
                    count = analysis.kernel_dist.get(k, 0)
                    pct = 100 * count / kernel_total
                    lines.append(f"  {k}: {count:4} ({pct:5.1f}%)")

            lines.append(f"\nINTERPRETATION:")
            lines.append(f"  Kernel balance: {analysis.kernel_balance}")
            lines.append(f"  Material: {analysis.material_category}")
            lines.append(f"  Output: {analysis.output_category}")

        else:
            # Tier 3-4 interpretive output
            lines.append(f"\nPROCESS CHARACTERIZATION:")

            # Kernel balance interpretation
            balance_gloss = {
                'ESCAPE_DOMINANT': "Mostly waiting for things to settle",
                'ENERGY_DOMINANT': "Active heating throughout",
                'HAZARD_HEAVY': "Careful monitoring required",
                'BALANCED': "Mixed heating and settling",
            }
            lines.append(f"  {balance_gloss.get(analysis.kernel_balance, analysis.kernel_balance)}")

            # Material interpretation
            material_gloss = {
                'ANIMAL': "Processing animal material (careful timing needed)",
                'ROOT': "Processing roots (mechanical preparation first)",
                'DELICATE_PLANT': "Processing delicate plant material (gentle handling)",
            }
            lines.append(f"  {material_gloss.get(analysis.material_category, analysis.material_category)}")

            # Output interpretation
            output_gloss = {
                'OIL': "Producing oil/resin extract",
                'WATER': "Producing water-based distillate",
            }
            lines.append(f"  {output_gloss.get(analysis.output_category, analysis.output_category)}")

            # Sample decoded lines
            lines.append(f"\nSAMPLE DECODED TOKENS:")
            for tok in analysis.tokens[:10]:
                interp = tok.interpretive()
                lines.append(f"  {tok.word:15} -> {interp}")

        return '\n'.join(lines)


# ============================================================
# TOKEN DICTIONARY
# ============================================================
class TokenDictionary:
    """
    Unified token lookup with persistent notes.

    Provides access to all 8,150 unique tokens in the H-track with:
    - Morphological decomposition (articulator, prefix, middle, suffix)
    - System membership (A, B, AZC)
    - Distribution statistics (counts, folios, sections)
    - Persistent notes for accumulated knowledge

    Usage:
        td = TokenDictionary()
        entry = td.get('daiin')
        print(td.lookup('chedy'))  # Quick summary
        td.add_note('daiin', 'High frequency in HERBAL_B')
        td.save()
    """

    DICT_PATH = PROJECT_ROOT / 'data' / 'token_dictionary.json'

    def __init__(self, path: Path = None):
        """Initialize dictionary with optional custom path."""
        self.path = path or self.DICT_PATH
        self._data = None

    def _load(self) -> dict:
        """Lazy load dictionary data."""
        if self._data is None:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        return self._data

    def get(self, token: str) -> Optional[dict]:
        """Get full entry for a token."""
        return self._load()['tokens'].get(token)

    def lookup(self, token: str) -> str:
        """Quick summary string for a token."""
        entry = self.get(token)
        if not entry:
            return f"{token}: not found"
        systems = '/'.join(entry['systems'])
        total = entry['distribution']['total']
        return f"{token}: {systems}, {total} occurrences"

    def add_note(self, token: str, note: str):
        """Add a timestamped note to a token."""
        data = self._load()
        if token in data['tokens']:
            data['tokens'][token]['notes'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'text': note
            })

    def save(self):
        """Persist changes to disk."""
        if self._data is not None:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)

    # --------------------------------------------------------
    # Gloss Management (Tier 3-4 Interpretive Content)
    # --------------------------------------------------------

    def get_gloss(self, token: str) -> Optional[str]:
        """Get Tier 3-4 interpretive gloss for a token."""
        entry = self.get(token)
        if entry:
            return entry.get('gloss')
        return None

    def set_gloss(self, token: str, gloss: str, save: bool = False):
        """
        Set gloss for a token, optionally persisting to disk.

        Args:
            token: The token word
            gloss: The interpretive gloss (human-readable meaning)
            save: If True, immediately persist to disk
        """
        data = self._load()
        if token in data['tokens']:
            data['tokens'][token]['gloss'] = gloss
            if save:
                self.save()

    def clear_gloss(self, token: str, save: bool = False):
        """Clear gloss for a token (set to None)."""
        data = self._load()
        if token in data['tokens']:
            data['tokens'][token]['gloss'] = None
            if save:
                self.save()

    def get_glossed_tokens(self) -> List[str]:
        """Get all tokens that have a gloss defined."""
        return [t for t, e in self._load()['tokens'].items()
                if e.get('gloss') is not None]

    def get_by_middle(self, middle: str) -> List[str]:
        """Get all tokens with a specific MIDDLE."""
        return [t for t, e in self._load()['tokens'].items()
                if e['morphology']['middle'] == middle]

    def get_by_system(self, system: str) -> List[str]:
        """Get all tokens in a system (A, B, or AZC)."""
        return [t for t, e in self._load()['tokens'].items()
                if system in e['systems']]

    def get_by_prefix(self, prefix: str) -> List[str]:
        """Get all tokens with a specific PREFIX."""
        return [t for t, e in self._load()['tokens'].items()
                if e['morphology']['prefix'] == prefix]

    def get_by_suffix(self, suffix: str) -> List[str]:
        """Get all tokens with a specific SUFFIX."""
        return [t for t, e in self._load()['tokens'].items()
                if e['morphology']['suffix'] == suffix]

    def stats(self) -> dict:
        """Get summary statistics."""
        data = self._load()
        tokens = data['tokens']
        azc_with_positions = len([t for t, e in tokens.items()
                                   if e.get('azc', {}).get('positions')])
        return {
            'total_tokens': len(tokens),
            'a_tokens': len([t for t, e in tokens.items() if 'A' in e['systems']]),
            'b_tokens': len([t for t, e in tokens.items() if 'B' in e['systems']]),
            'azc_tokens': len([t for t, e in tokens.items() if 'AZC' in e['systems']]),
            'label_tokens': len([t for t, e in tokens.items() if e['distribution']['is_label']]),
            'with_notes': len([t for t, e in tokens.items() if e['notes']]),
            'azc_with_positions': azc_with_positions,
        }

    # --------------------------------------------------------
    # AZC Position Management
    # --------------------------------------------------------

    def add_azc_position(self, token: str, folio: str, position: str):
        """
        Add an AZC diagram position for a token.

        Args:
            token: The token word
            folio: The folio where this position was observed (e.g., 'f57v')
            position: The placement code (e.g., 'C', 'R1', 'S2')
        """
        data = self._load()
        if token not in data['tokens']:
            return

        entry = data['tokens'][token]

        # Initialize azc structure if missing
        if 'azc' not in entry:
            entry['azc'] = {'positions': [], 'by_folio': {}}

        # Add to positions list (unique)
        if position not in entry['azc']['positions']:
            entry['azc']['positions'].append(position)
            entry['azc']['positions'].sort()

        # Add to by_folio mapping
        if folio not in entry['azc']['by_folio']:
            entry['azc']['by_folio'][folio] = []
        if position not in entry['azc']['by_folio'][folio]:
            entry['azc']['by_folio'][folio].append(position)
            entry['azc']['by_folio'][folio].sort()

    def get_azc_positions(self, token: str) -> Optional[dict]:
        """Get AZC position data for a token."""
        entry = self.get(token)
        if entry:
            return entry.get('azc')
        return None

    def get_by_azc_position(self, position: str) -> List[str]:
        """Get all tokens that appear at a specific AZC position."""
        return [t for t, e in self._load()['tokens'].items()
                if position in e.get('azc', {}).get('positions', [])]

    def get_azc_zone_tokens(self, zone: str) -> List[str]:
        """
        Get tokens by zone type (C, R, S, P).

        Matches position prefixes: 'R' matches R, R1, R2, R3, R4.
        """
        results = []
        for t, e in self._load()['tokens'].items():
            positions = e.get('azc', {}).get('positions', [])
            for pos in positions:
                if pos == zone or pos.startswith(zone):
                    results.append(t)
                    break
        return results

    # DA-family prefixes (infrastructure markers per C407)
    INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}

    @classmethod
    def generate(cls, output_path: Path = None, preserve_annotations: bool = True):
        """
        Generate token dictionary from transcript.

        Reads all H-track tokens and builds comprehensive dictionary
        with morphology, distribution statistics, and role classification.

        Args:
            output_path: Where to write. Defaults to DICT_PATH.
            preserve_annotations: If True (default), preserves manually curated
                fields (gloss, notes, fl_state, fl_meaning, is_fl_role, role.subrole)
                from the existing dictionary. Prevents accidental data loss during
                schema migrations or regeneration.
        """
        output_path = output_path or cls.DICT_PATH
        morph = Morphology()

        # Load existing annotations to preserve
        existing_annotations = {}
        if preserve_annotations and output_path.exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                for word, entry in existing.get('tokens', {}).items():
                    preserved = {}
                    if entry.get('gloss') is not None:
                        preserved['gloss'] = entry['gloss']
                    if entry.get('notes'):
                        preserved['notes'] = entry['notes']
                    if entry.get('fl_state') is not None:
                        preserved['fl_state'] = entry['fl_state']
                    if entry.get('fl_meaning') is not None:
                        preserved['fl_meaning'] = entry['fl_meaning']
                    if entry.get('is_fl_role') is not None:
                        preserved['is_fl_role'] = entry['is_fl_role']
                    if entry.get('role', {}).get('subrole') is not None:
                        preserved['subrole'] = entry['role']['subrole']
                    if preserved:
                        existing_annotations[word] = preserved
                print(f"Preserving annotations for {len(existing_annotations)} tokens")
            except (json.JSONDecodeError, KeyError):
                print("Warning: Could not read existing dictionary for annotation preservation")

        # Load MIDDLE classifications for role assignment
        ri_middles, pp_middles = load_middle_classes()

        # Collect all token data
        token_data = defaultdict(lambda: {
            'systems': set(),
            'a_count': 0,
            'b_count': 0,
            'azc_count': 0,
            'total': 0,
            'folios': set(),
            'sections': set(),
            'is_label': False,
            'locations': [],  # Track all occurrences as folio.line.position
            'azc_positions': set(),  # Unique AZC positions
            'azc_by_folio': defaultdict(set)  # Positions per folio
        })

        # Track position within each line for location IDs
        current_line_key = None
        position_in_line = 0

        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                # Filter to H transcriber
                transcriber = row.get('transcriber', '').strip().strip('"')
                if transcriber != 'H':
                    continue

                word = row.get('word', '').strip()
                if not word:
                    continue

                # Get metadata
                language = row.get('language', '').strip()
                folio = row.get('folio', '').strip()
                line = row.get('line_number', '').strip()
                placement = row.get('placement', '').strip()

                # Track position in line for location IDs
                line_key = (folio, line)
                if line_key != current_line_key:
                    current_line_key = line_key
                    position_in_line = 1
                else:
                    position_in_line += 1

                # Determine section from folio (simplified)
                if folio:
                    section = folio[0].upper() if folio[0].isalpha() else 'X'
                else:
                    section = 'X'

                # Track data
                td = token_data[word]
                td['total'] += 1

                if language == 'A':
                    td['systems'].add('A')
                    td['a_count'] += 1
                elif language == 'B':
                    td['systems'].add('B')
                    td['b_count'] += 1
                elif language == 'NA':
                    td['systems'].add('AZC')
                    td['azc_count'] += 1
                    # Track AZC diagram positions
                    if placement and not placement.startswith('L'):
                        td['azc_positions'].add(placement)
                        if folio:
                            td['azc_by_folio'][folio].add(placement)

                if folio:
                    td['folios'].add(folio)
                if section:
                    td['sections'].add(section)

                # Check if label
                if placement and placement.startswith('L'):
                    td['is_label'] = True

                # Add location ID (folio.line.position)
                if folio and line:
                    location_id = f"{folio}.{line}.{position_in_line}"
                    td['locations'].append(location_id)

        # Build final dictionary
        tokens = {}
        for word, data in token_data.items():
            # Extract morphology
            m = morph.extract(word)

            # Compute primary role based on MIDDLE classification
            primary_role = None
            middle = m.middle
            prefix = m.prefix

            # Check for INFRA first (DA-family with short MIDDLE)
            if prefix in cls.INFRA_PREFIXES and middle and len(middle) <= 3:
                primary_role = 'INFRA'
            elif middle in ri_middles:
                primary_role = 'RI'
            elif middle in pp_middles:
                primary_role = 'PP'
            else:
                primary_role = 'UNKNOWN'

            # Build azc position data
            azc_by_folio = {f: sorted(list(positions))
                           for f, positions in data['azc_by_folio'].items()}

            entry = {
                'morphology': {
                    'articulator': m.articulator,
                    'prefix': m.prefix,
                    'middle': m.middle,
                    'suffix': m.suffix
                },
                'systems': sorted(list(data['systems'])),
                'distribution': {
                    'total': data['total'],
                    'a_count': data['a_count'],
                    'b_count': data['b_count'],
                    'azc_count': data['azc_count'],
                    'folio_count': len(data['folios']),
                    'sections': sorted(list(data['sections'])),
                    'is_label': data['is_label']
                },
                'role': {
                    'primary': primary_role,
                    'subrole': None
                },
                'locations': data['locations'],
                'azc': {
                    'positions': sorted(list(data['azc_positions'])),
                    'by_folio': azc_by_folio
                },
                'notes': [],
                'gloss': None,
                'fl_state': None,
                'fl_meaning': None,
                'is_fl_role': False
            }

            # Restore preserved annotations
            if word in existing_annotations:
                ann = existing_annotations[word]
                if 'gloss' in ann:
                    entry['gloss'] = ann['gloss']
                if 'notes' in ann:
                    entry['notes'] = ann['notes']
                if 'fl_state' in ann:
                    entry['fl_state'] = ann['fl_state']
                if 'fl_meaning' in ann:
                    entry['fl_meaning'] = ann['fl_meaning']
                if 'is_fl_role' in ann:
                    entry['is_fl_role'] = ann['is_fl_role']
                if 'subrole' in ann:
                    entry['role']['subrole'] = ann['subrole']

            tokens[word] = entry

        # Count preserved annotations
        glossed = sum(1 for t in tokens.values() if t.get('gloss'))
        noted = sum(1 for t in tokens.values() if t.get('notes'))

        # Build final output
        output = {
            'meta': {
                'version': '6.0',
                'generated': datetime.now().strftime('%Y-%m-%d'),
                'token_count': len(tokens),
                'schema_notes': 'v3: locations[], role, notes. v4: azc{positions[], by_folio{}}. v5: gloss field (Tier 3-4). v6: fl_state, fl_meaning, is_fl_role (C770-C777).',
                'glossed': glossed,
                'annotated': noted
            },
            'tokens': tokens
        }

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"Generated token dictionary: {len(tokens)} tokens")
        if existing_annotations:
            print(f"Preserved: {glossed} glosses, {noted} annotated tokens")
        print(f"Saved to: {output_path}")

        return output


# ============================================================
# MIDDLE DICTIONARY
# ============================================================

class MiddleDictionary:
    """
    MIDDLE semantic tracking dictionary.

    MIDDLEs carry the core semantic content of tokens. This dictionary
    tracks all unique MIDDLEs with their kernel profiles, regime
    associations, and learned glosses.

    Usage:
        md = MiddleDictionary()
        entry = md.get('ypch')
        print(entry['kernel'])  # 'H'
        print(entry['gloss'])   # None (until we learn it)

        # Set a gloss
        md.set_gloss('od', 'output ready', save=True)
    """

    DEFAULT_PATH = PROJECT_ROOT / 'data' / 'middle_dictionary.json'

    def __init__(self, path: Optional[Path] = None):
        self._path = path or self.DEFAULT_PATH
        self._data: Optional[Dict] = None

    def _load(self) -> Dict:
        if self._data is None:
            if self._path.exists():
                with open(self._path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                self._data = {'meta': {'version': '1.0'}, 'middles': {}}
        return self._data

    def save(self):
        """Save dictionary to disk."""
        data = self._load()
        # Update glossed count
        glossed = sum(1 for m in data['middles'].values() if m.get('gloss'))
        data['meta']['glossed'] = glossed
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, middle: str) -> Optional[Dict]:
        """Get entry for a MIDDLE."""
        data = self._load()
        return data['middles'].get(middle)

    def get_gloss(self, middle: str) -> Optional[str]:
        """Get gloss for a MIDDLE."""
        entry = self.get(middle)
        return entry.get('gloss') if entry else None

    def get_kernel(self, middle: str) -> Optional[str]:
        """Get kernel type for a MIDDLE."""
        entry = self.get(middle)
        return entry.get('kernel') if entry else None

    def set_gloss(self, middle: str, gloss: str, save: bool = False):
        """Set gloss for a MIDDLE."""
        data = self._load()
        if middle in data['middles']:
            data['middles'][middle]['gloss'] = gloss
            if save:
                self.save()

    def get_glossed_middles(self) -> Dict[str, str]:
        """Get all MIDDLEs that have glosses."""
        data = self._load()
        return {m: e['gloss'] for m, e in data['middles'].items() if e.get('gloss')}

    def summary(self) -> Dict:
        """Get summary statistics."""
        data = self._load()
        middles = data['middles']
        return {
            'total': len(middles),
            'glossed': sum(1 for m in middles.values() if m.get('gloss')),
            'kernel_k': sum(1 for m in middles.values() if m.get('kernel') == 'K'),
            'kernel_h': sum(1 for m in middles.values() if m.get('kernel') == 'H'),
            'kernel_e': sum(1 for m in middles.values() if m.get('kernel') == 'E'),
        }


# ============================================================
# FOLIO NOTES
# ============================================================

class FolioNotes:
    """
    Persistent folio-level observations and notes.

    Stores structural observations about each folio that emerge
    during annotation - patterns, anomalies, questions to investigate.

    Usage:
        fn = FolioNotes()
        fn.add_note('f1r', 'High concentration of qo- escape tokens in lines 3-7')
        fn.save()
        notes = fn.get('f1r')
    """

    NOTES_PATH = PROJECT_ROOT / 'data' / 'folio_notes.json'

    def __init__(self, path: Path = None):
        """Initialize with optional custom path."""
        self.path = path or self.NOTES_PATH
        self._data = None

    def _load(self) -> dict:
        """Lazy load notes data."""
        if self._data is None:
            if self.path.exists():
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                self._data = {
                    'meta': {
                        'version': '1.0',
                        'generated': datetime.now().strftime('%Y-%m-%d'),
                        'description': 'Folio-level observations and notes'
                    },
                    'folios': {}
                }
        return self._data

    def get(self, folio: str) -> Optional[dict]:
        """Get all notes for a folio."""
        return self._load()['folios'].get(folio)

    def add_note(self, folio: str, note: str):
        """Add a timestamped note to a folio."""
        data = self._load()
        if folio not in data['folios']:
            data['folios'][folio] = {
                'notes': [],
                'first_annotated': datetime.now().strftime('%Y-%m-%d')
            }
        data['folios'][folio]['notes'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'text': note
        })

    def save(self):
        """Persist changes to disk."""
        if self._data is not None:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)

    def list_folios(self) -> List[str]:
        """Get list of folios with notes."""
        return list(self._load()['folios'].keys())

    def stats(self) -> dict:
        """Get summary statistics."""
        data = self._load()
        folios = data['folios']
        total_notes = sum(len(f['notes']) for f in folios.values())
        return {
            'folios_with_notes': len(folios),
            'total_notes': total_notes
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

    # Test BFolioDecoder
    print("\n" + "=" * 50)
    print("B Folio Decoder Test (f107r)")
    print("=" * 50)

    decoder = BFolioDecoder()
    analysis = decoder.analyze_folio('f107r')

    if analysis:
        print(f"\nFolio: {analysis.folio} ({analysis.token_count} tokens)")
        print(f"\nClassification rates:")
        print(f"  PREFIX: {analysis.prefix_classified_pct:.1f}%")
        print(f"  SUFFIX: {analysis.suffix_classified_pct:.1f}%")
        print(f"  MIDDLE tier: {analysis.middle_classified_pct:.1f}%")

        print(f"\nInterpretations:")
        print(f"  Kernel balance: {analysis.kernel_balance}")
        print(f"  Material: {analysis.material_category}")
        print(f"  Output: {analysis.output_category}")

        print(f"\nKernel distribution:")
        for k in ['k', 'h', 'e']:
            count = analysis.kernel_dist.get(k, 0)
            print(f"  {k}: {count}")

        # Test both output modes
        print("\nSample token analysis (structural mode):")
        for tok in analysis.tokens[:5]:
            print(f"  {tok.word:15} -> {tok.structural()}")

        print("\nSample token analysis (interpretive mode):")
        for tok in analysis.tokens[:5]:
            print(f"  {tok.word:15} -> {tok.interpretive()}")

        # Test line-level analysis
        print("\n" + "=" * 50)
        print("B Line-Level Analysis Test (f107r, first 3 lines)")
        print("=" * 50)

        lines = decoder.analyze_folio_lines('f107r')
        for la in lines[:3]:
            print(f"\nLine {la.line_id}: {la.interpretive()}")
            print(f"  Type: {la.line_type} | FL: {la.fl_progression} | Kernels: {la.kernel_sequence[:5]}")
            for t in la.tokens[:2]:
                print(f"    {t.word:12} -> {t.interpretive()}")
