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
from typing import Optional, Iterator, List, Set, Tuple
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
