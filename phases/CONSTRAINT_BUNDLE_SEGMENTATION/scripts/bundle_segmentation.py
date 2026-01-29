"""
CONSTRAINT_BUNDLE_SEGMENTATION - Shared Module

Provides:
  - Bundle dataclass: A maximal run of consecutive PP-pure A lines
  - segment_all_folios(): Segment all A folios into bundles
  - B inventory and C502.a filtering infrastructure
  - Role taxonomy and class mappings

Algorithm:
  For each A folio (sorted lines):
    Classify each line: PP-pure (ri_count == 0) or RI-bearing (ri_count > 0)
    Bundle = maximal run of consecutive PP-pure lines
    RI-bearing lines are boundary markers (not in bundles)
"""

import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, FrozenSet, Optional
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer, RecordAnalysis

# ── Role taxonomy (C560/C581: class 17 = CC) ──
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

ROLE_TO_CLASSES = {}
for c, r in CLASS_TO_ROLE.items():
    ROLE_TO_CLASSES.setdefault(r, set()).add(c)

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']


@dataclass
class Bundle:
    """A maximal run of consecutive PP-pure A lines within a folio."""
    folio: str
    lines: List[RecordAnalysis]      # PP-pure lines in this bundle
    size: int = 0                     # len(lines)
    pp_middles: Set[str] = field(default_factory=set)
    pp_prefixes: Set[str] = field(default_factory=set)
    pp_suffixes: Set[str] = field(default_factory=set)
    legal_b_tokens: Set[str] = field(default_factory=set)
    legal_b_classes: FrozenSet[int] = field(default_factory=frozenset)
    n_classes: int = 0
    line_numbers: List[str] = field(default_factory=list)


def _build_b_inventory(tx: Transcript, morph: Morphology):
    """Build B token inventory with morphology. Returns (b_tokens, b_by_middle, b_by_prefix, b_by_suffix, b_middles_set, b_prefixes_set, b_suffixes_set)."""
    b_tokens = {}       # token_str -> (prefix, middle, suffix)
    b_by_middle = defaultdict(set)
    b_by_prefix = defaultdict(set)
    b_by_suffix = defaultdict(set)

    for token in tx.currier_b():
        w = token.word
        if w in b_tokens:
            continue
        m = morph.extract(w)
        if m.middle:
            b_tokens[w] = (m.prefix, m.middle, m.suffix)
            b_by_middle[m.middle].add(w)
            if m.prefix:
                b_by_prefix[m.prefix].add(w)
            if m.suffix:
                b_by_suffix[m.suffix].add(w)

    b_middles_set = set(b_by_middle.keys())
    b_prefixes_set = set(b_by_prefix.keys())
    b_suffixes_set = set(b_by_suffix.keys())

    return b_tokens, b_by_middle, b_by_prefix, b_by_suffix, b_middles_set, b_prefixes_set, b_suffixes_set


def _filter_b_tokens(pp_middles, pp_prefixes, pp_suffixes, b_tokens, b_middles_set, b_prefixes_set, b_suffixes_set):
    """Apply C502.a full morphological filtering. Returns set of legal B tokens."""
    # Intersect with B vocabulary
    active_middles = pp_middles & b_middles_set
    active_prefixes = pp_prefixes & b_prefixes_set
    active_suffixes = pp_suffixes & b_suffixes_set

    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in active_middles:
            pref_ok = (pref is None or pref in active_prefixes)
            suf_ok = (suf is None or suf in active_suffixes)
            if pref_ok and suf_ok:
                legal.add(tok)
    return legal


def segment_all_folios(verbose=True):
    """
    Segment all Currier A folios into bundles.

    Returns:
        (bundles, ri_bearing_lines, metadata, shared_data)

        bundles: List[Bundle] - all bundles across all folios
        ri_bearing_lines: List[RecordAnalysis] - all RI-bearing lines
        metadata: dict - segmentation statistics
        shared_data: dict - shared infrastructure for downstream scripts:
            tx, morph, analyzer,
            b_tokens, b_token_class, b_middles_set, b_prefixes_set, b_suffixes_set,
            token_to_class
    """
    tx = Transcript()
    morph = Morphology()
    analyzer = RecordAnalyzer()

    if verbose:
        print("Building B token inventory...")
    b_tokens, b_by_middle, b_by_prefix, b_by_suffix, b_middles_set, b_prefixes_set, b_suffixes_set = _build_b_inventory(tx, morph)

    # Load class map for B token -> class
    with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    b_token_class = {tok: int(cls) for tok, cls in token_to_class.items() if tok in b_tokens}

    if verbose:
        print(f"  B token types: {len(b_tokens)}, B MIDDLEs: {len(b_middles_set)}")

    # Segment all folios
    if verbose:
        print("Segmenting A folios into bundles...")

    folios = analyzer.get_folios()
    all_bundles = []
    all_ri_lines = []
    folio_stats = {}

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        if not records:
            continue

        # Classify each line
        pp_pure_lines = []  # (record, is_pp_pure)
        for rec in records:
            is_pp_pure = (rec.ri_count == 0)
            pp_pure_lines.append((rec, is_pp_pure))

        # Segment into bundles: maximal runs of PP-pure lines
        current_run = []
        n_ri_lines = 0
        folio_bundles = []

        for rec, is_pp_pure in pp_pure_lines:
            if is_pp_pure:
                current_run.append(rec)
            else:
                # RI-bearing line: close current bundle if any
                if current_run:
                    folio_bundles.append(current_run)
                    current_run = []
                all_ri_lines.append(rec)
                n_ri_lines += 1

        # Close final run
        if current_run:
            folio_bundles.append(current_run)

        # Build Bundle objects with B filtering
        for run_lines in folio_bundles:
            # Pool PP morphology across all lines
            pp_middles = set()
            pp_prefixes = set()
            pp_suffixes = set()

            for rec in run_lines:
                for t in rec.tokens:
                    if t.is_pp:
                        if t.middle:
                            pp_middles.add(t.middle)
                        if t.prefix:
                            pp_prefixes.add(t.prefix)
                        if t.suffix:
                            pp_suffixes.add(t.suffix)

            # Apply C502.a filtering
            legal = _filter_b_tokens(
                pp_middles, pp_prefixes, pp_suffixes,
                b_tokens, b_middles_set, b_prefixes_set, b_suffixes_set
            )
            legal_classes = frozenset(b_token_class[t] for t in legal if t in b_token_class)

            bundle = Bundle(
                folio=fol,
                lines=run_lines,
                size=len(run_lines),
                pp_middles=pp_middles,
                pp_prefixes=pp_prefixes,
                pp_suffixes=pp_suffixes,
                legal_b_tokens=legal,
                legal_b_classes=legal_classes,
                n_classes=len(legal_classes),
                line_numbers=[r.line for r in run_lines],
            )
            all_bundles.append(bundle)

        folio_stats[fol] = {
            'n_lines': len(records),
            'n_pp_pure': len(records) - n_ri_lines,
            'n_ri_bearing': n_ri_lines,
            'n_bundles': len(folio_bundles),
        }

    metadata = {
        'total_folios': len(folios),
        'total_bundles': len(all_bundles),
        'total_ri_lines': len(all_ri_lines),
        'total_pp_pure_lines': sum(b.size for b in all_bundles),
        'total_lines': sum(s['n_lines'] for s in folio_stats.values()),
        'folio_stats': folio_stats,
    }

    if verbose:
        print(f"  Folios: {metadata['total_folios']}")
        print(f"  Total lines: {metadata['total_lines']}")
        print(f"  PP-pure lines: {metadata['total_pp_pure_lines']}")
        print(f"  RI-bearing lines: {metadata['total_ri_lines']}")
        print(f"  Bundles: {metadata['total_bundles']}")
        sizes = [b.size for b in all_bundles]
        if sizes:
            print(f"  Bundle sizes: min={min(sizes)}, max={max(sizes)}, mean={sum(sizes)/len(sizes):.2f}")

    shared_data = {
        'tx': tx,
        'morph': morph,
        'analyzer': analyzer,
        'b_tokens': b_tokens,
        'b_token_class': b_token_class,
        'b_middles_set': b_middles_set,
        'b_prefixes_set': b_prefixes_set,
        'b_suffixes_set': b_suffixes_set,
        'token_to_class': token_to_class,
        'filter_b_tokens': _filter_b_tokens,
    }

    return all_bundles, all_ri_lines, metadata, shared_data
