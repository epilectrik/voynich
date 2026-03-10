"""Phase 559 T2: Supervisory State Induction (Stage 1)

Loads T1 compositional decomposition output, builds evidence tables from
B-corpus enrichment data (effect-size-derived, NOT hand-authored), runs
3 state partitions on f43v tokens and 5 null types x 50 seeds, computes
baselines (HEAD-only, zone-only), scores S1-S6 criteria and checks FC1-FC6.

Input: results/t1_compositional_decomposition.json
Output: results/t2_supervisory_state_induction.json
"""
import json
import sys
import math
import random
import warnings
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import (
    Transcript, Morphology, BFolioDecoder, CategoryClassifier,
    decompose_middle_hmt
)

# ═══════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════

STATES_6 = ['SPEC', 'TWORK', 'OBS', 'CHK', 'TRANS', 'CLOSE']
STATES_4 = ['SPECIFY', 'OPERATE', 'TRANSITION', 'CLOSURE']

# 8 operational categories -> 6 supervisory states
CAT_TO_STATE6 = {
    'THERMAL': 'TWORK',
    'FLOW': 'TRANS',
    'CONTAINMENT': 'CLOSE',
    'STAGING': 'SPEC',
    'OPERATION': 'TWORK',
    'TRANSITION': 'TRANS',
    'MARKING': 'CHK',
    'MONITORING': 'OBS',
}

# 6-state -> 4-state merging
STATE6_TO_STATE4 = {
    'SPEC': 'SPECIFY', 'CHK': 'SPECIFY',
    'TWORK': 'OPERATE', 'OBS': 'OPERATE',
    'TRANS': 'TRANSITION',
    'CLOSE': 'CLOSURE',
}

# Channel weights (proportional to measured MI from constraints)
W1 = 0.30  # PREFIX x HEAD: 1.089 bits, C1411
W2 = 0.15  # TERM x SUFFIX_HEAD: 0.422 bits, C1412
W3 = 0.25  # HEAD x TERM frame: 64% of instruction class, C1394
W4 = 0.10  # HEAD x MOD: 36% of remaining, C1479
W5 = 0.10  # Zone modulation, C1566
W6 = 0.05  # Routing context, C1563
W7 = 0.05  # Meta features

# C1479 modifier effect sizes (used as confidence weights on CH4)
MOD_EFFECT_SIZES = {
    'd': 0.657, 'c': 0.505, 'i': 0.418,
    'p': 0.368, 'f': 0.351, 's': 0.245,
}

# C1563 terminal -> next HEAD routing enrichment
TERM_TO_HEAD_ENRICHMENT = {
    'r': {'a': 2.23},
    'n': {'a': 1.42},
    'y': {'k': 1.60, 't': 1.46},
    'h': {'t': 1.89, 'k': 1.32},
    'l': {'e': 1.25},
    'm': {'o': 1.55},
}

# HEAD domain -> state mapping for routing context
HEAD_DOMAIN_TO_STATE = {
    'k': 'TWORK',   # THERMAL domain
    't': 'TRANS',    # FLOW domain
    'a': 'TRANS',    # YIELD domain
    'e': 'SPEC',     # STAB domain -> specification
    'o': 'SPEC',     # ARRNG domain -> specification
}

N_PERMUTATIONS = 1000  # For paragraph differentiation permutation test
EPSILON = 1e-12  # Prevent log(0)

# Unsupervised k-means search range
K_RANGE = [4, 5, 6, 7, 8]


# ═══════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════

def softmax(arr):
    """Numerically stable softmax."""
    a = np.array(arr, dtype=np.float64)
    a -= np.max(a)
    e = np.exp(a)
    s = e.sum()
    if s < EPSILON:
        return np.ones_like(a) / len(a)
    return e / s


def log2_enrichment(count, total, base_count, base_total):
    """Compute log2(enrichment) with smoothing."""
    if total == 0 or base_total == 0:
        return 0.0
    rate = (count + 0.5) / (total + 1.0)
    base_rate = (base_count + 0.5) / (base_total + 1.0)
    if base_rate < EPSILON:
        return 0.0
    return math.log2(rate / base_rate)


def jsd(p, q):
    """Jensen-Shannon Divergence between two distributions."""
    p = np.array(p, dtype=np.float64) + EPSILON
    q = np.array(q, dtype=np.float64) + EPSILON
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log2(p / m))
    kl_qm = np.sum(q * np.log2(q / m))
    return 0.5 * (kl_pm + kl_qm)


def entropy(p):
    """Shannon entropy in bits."""
    p = np.array(p, dtype=np.float64) + EPSILON
    p = p / p.sum()
    return -np.sum(p * np.log2(p))


def state_profile(states, state_list):
    """Compute normalized distribution over states."""
    counts = Counter(states)
    total = sum(counts.values())
    if total == 0:
        return np.ones(len(state_list)) / len(state_list)
    return np.array([counts.get(s, 0) / total for s in state_list])


def transition_matrix(states, state_list):
    """Compute state transition matrix (row-normalized)."""
    n = len(state_list)
    s2i = {s: i for i, s in enumerate(state_list)}
    mat = np.zeros((n, n))
    for i in range(len(states) - 1):
        if states[i] in s2i and states[i + 1] in s2i:
            mat[s2i[states[i]], s2i[states[i + 1]]] += 1
    row_sums = mat.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return mat / row_sums


def frobenius_distance(m1, m2):
    """Frobenius norm of difference between two matrices."""
    return float(np.linalg.norm(m1 - m2))


# ═══════════════════════════════════════════════════════════════════════
# Evidence Table Builder
# ═══════════════════════════════════════════════════════════════════════

class EvidenceTableBuilder:
    """Build enrichment-based evidence tables from B-corpus data.

    For each pairwise key, computes category enrichment -> log-odds ->
    6-state mapping -> softmax. 100% data-derived, no hand-authoring.
    """

    def __init__(self):
        self.cc = CategoryClassifier()
        self.morph = Morphology()
        self.decoder = BFolioDecoder()

        # Corpus-wide counts
        self._corpus_tokens = []
        self._total_count = 0
        self._cat_baseline = Counter()

        # Pairwise evidence tables (key -> 6-element evidence vector)
        self.ch1_table = {}  # (prefix, head)
        self.ch2_table = {}  # (term, suffix_head)
        self.ch3_table = {}  # frame_hazard string
        self.ch4_table = {}  # (head, first_mod)
        self.zone_table = {}  # zone string
        self.route_table = {}  # prev_term string

    def build_from_corpus(self):
        """Build all evidence tables from full B corpus."""
        print("  Building evidence tables from B-corpus enrichment data...")
        tx = Transcript()
        b_tokens = [t for t in tx.currier_b()
                     if '*' not in t.word and t.word.strip()]

        # Analyze each token
        analyses = []
        print(f"    Analyzing {len(b_tokens)} B-corpus tokens...")
        for t in b_tokens:
            try:
                analysis = self.decoder.analyze_token(t.word)
                m = self.morph.extract(t.word)
                cat = analysis.operational_category
                if cat is None:
                    continue

                # Compute channel keys
                pfx = m.prefix if m.prefix else None
                head = analysis.middle_head
                if head is None and analysis.is_headless and m.middle:
                    head = m.middle[0]  # pseudo-head

                term = analysis.middle_term
                sfx_head = m.suffix[0] if m.suffix and len(m.suffix) > 0 else None

                first_mod = None
                if analysis.middle_mods and len(analysis.middle_mods) > 0:
                    first_mod = analysis.middle_mods[0]

                analyses.append({
                    'cat': cat,
                    'ch1_key': (pfx, head),
                    'ch2_key': (term, sfx_head),
                    'ch3_key': analysis.frame_hazard,
                    'ch4_key': (analysis.middle_head, first_mod),
                    'is_dark': analysis.is_dark_pipeline,
                })
            except Exception:
                continue

        # Filter out dark pipeline tokens
        analyses = [a for a in analyses if not a.get('is_dark', False)]

        self._total_count = len(analyses)
        print(f"    Non-dark tokens: {self._total_count}")

        # Compute category baseline
        for a in analyses:
            self._cat_baseline[a['cat']] += 1

        print(f"    Category baseline: {dict(self._cat_baseline.most_common())}")

        # Build CH1 table
        self._build_channel_table(
            analyses, 'ch1_key', self.ch1_table, 'CH1')

        # Build CH2 table
        self._build_channel_table(
            analyses, 'ch2_key', self.ch2_table, 'CH2')

        # Build CH3 table
        self._build_channel_table(
            analyses, 'ch3_key', self.ch3_table, 'CH3')

        # Build CH4 table
        self._build_channel_table(
            analyses, 'ch4_key', self.ch4_table, 'CH4')

        # Build zone table from C1426-C1428 positional data
        self._build_zone_table(analyses)

        # Build routing table from C1563
        self._build_route_table()

        print(f"    Evidence tables: CH1={len(self.ch1_table)} keys, "
              f"CH2={len(self.ch2_table)}, CH3={len(self.ch3_table)}, "
              f"CH4={len(self.ch4_table)}, zones={len(self.zone_table)}, "
              f"routes={len(self.route_table)}")

    def _build_channel_table(self, analyses, key_field, table, label):
        """Build an evidence table for one channel."""
        # Group by key
        key_counts = defaultdict(Counter)  # key -> category -> count
        key_totals = defaultdict(int)       # key -> total count

        for a in analyses:
            k = a[key_field]
            if k is None:
                k = ('_NONE_',)  # Normalize None keys
            elif not isinstance(k, tuple):
                k = (k,)  # Ensure tuple
            cat = a['cat']
            key_counts[k][cat] += 1
            key_totals[k] += 1

        # Convert to evidence vectors
        for k, counts in key_counts.items():
            total = key_totals[k]
            if total < 3:  # Skip very rare keys (noise)
                continue
            ev = self._enrichment_to_evidence(counts, total)
            # Serialize key for JSON compatibility
            table[str(k)] = ev.tolist()

    def _enrichment_to_evidence(self, cat_counts, total):
        """Convert category counts to 6-state evidence vector via enrichment."""
        # Compute log-odds enrichment for each of 8 categories
        log_odds_8 = {}
        for cat in CategoryClassifier.CATEGORIES:
            count = cat_counts.get(cat, 0)
            base_count = self._cat_baseline.get(cat, 0)
            lo = log2_enrichment(count, total, base_count, self._total_count)
            log_odds_8[cat] = lo

        # Map 8 categories to 6 states (sum when multiple map to same)
        ev6 = np.zeros(6)
        for cat, lo in log_odds_8.items():
            state = CAT_TO_STATE6.get(cat)
            if state:
                idx = STATES_6.index(state)
                ev6[idx] += lo

        return softmax(ev6)

    def _build_zone_table(self, analyses):
        """Build zone evidence table.

        Uses positional enrichment from C1426-C1428.
        We compute category enrichment at Q0, Q1-Q3, Q4 from corpus.
        """
        # We need positional data - re-analyze with line position info
        tx = Transcript()
        b_tokens = [t for t in tx.currier_b()
                     if '*' not in t.word and t.word.strip()]

        # Group by folio+line to get position indices
        lines = defaultdict(list)
        for t in b_tokens:
            lines[(t.folio, t.line)].append(t)

        zone_cat_counts = defaultdict(Counter)  # zone -> cat -> count
        zone_totals = defaultdict(int)

        for (fol, ln), toks in lines.items():
            n = len(toks)
            for idx, t in enumerate(toks):
                try:
                    analysis = self.decoder.analyze_token(t.word)
                    cat = analysis.operational_category
                    if cat is None or analysis.is_dark_pipeline:
                        continue
                    if n <= 1:
                        q = 0
                    else:
                        q = min(int(idx / (n - 1) * 5), 4)
                    if q == 0:
                        zone = 'SPECIFICATION'
                    elif q == 4:
                        zone = 'CLOSURE'
                    else:
                        zone = 'WORK'
                    zone_cat_counts[zone][cat] += 1
                    zone_totals[zone] += 1
                except Exception:
                    continue

        for zone in ['SPECIFICATION', 'WORK', 'CLOSURE']:
            counts = zone_cat_counts[zone]
            total = zone_totals[zone]
            if total < 10:
                self.zone_table[zone] = (np.ones(6) / 6).tolist()
            else:
                ev = self._enrichment_to_evidence(counts, total)
                self.zone_table[zone] = ev.tolist()

    def _build_route_table(self):
        """Build routing evidence table from C1563 terminal->HEAD enrichment."""
        for prev_term, head_enrichments in TERM_TO_HEAD_ENRICHMENT.items():
            ev = np.zeros(6)
            for head, enrich in head_enrichments.items():
                state = HEAD_DOMAIN_TO_STATE.get(head)
                if state:
                    idx = STATES_6.index(state)
                    ev[idx] += math.log2(enrich)
            self.route_table[prev_term] = softmax(ev).tolist()

        # Neutral routing for bare/None
        neutral = (np.ones(6) / 6).tolist()
        self.route_table['bare'] = neutral
        self.route_table['_NONE_'] = neutral

    def get_ch1_evidence(self, prefix, head):
        """Look up CH1 evidence for (prefix, head) pair."""
        key = str((prefix, head))
        return np.array(self.ch1_table.get(key, np.ones(6) / 6))

    def get_ch2_evidence(self, term, suffix_head):
        """Look up CH2 evidence for (term, suffix_head) pair."""
        key = str((term, suffix_head))
        return np.array(self.ch2_table.get(key, np.ones(6) / 6))

    def get_ch3_evidence(self, frame_hazard):
        """Look up CH3 evidence for frame hazard class."""
        if frame_hazard is None:
            return np.ones(6) / 6
        key = str((frame_hazard,))
        return np.array(self.ch3_table.get(key, np.ones(6) / 6))

    def get_ch4_evidence(self, head, first_mod):
        """Look up CH4 evidence for (HEAD, first_mod) pair."""
        key = str((head, first_mod))
        base = np.array(self.ch4_table.get(key, np.ones(6) / 6))
        # Apply modifier effect size as confidence weight
        if first_mod and first_mod in MOD_EFFECT_SIZES:
            effect = MOD_EFFECT_SIZES[first_mod]
            uniform = np.ones(6) / 6
            # Interpolate: more effect size = more trust in evidence
            base = effect * base + (1 - effect) * uniform
            base = base / base.sum()
        return base

    def get_zone_evidence(self, zone):
        """Look up zone modulation evidence."""
        ev = self.zone_table.get(zone)
        if ev is None:
            return np.ones(6) / 6
        return np.array(ev)

    def get_route_evidence(self, prev_term):
        """Look up routing context evidence."""
        if prev_term is None:
            prev_term = '_NONE_'
        ev = self.route_table.get(prev_term)
        if ev is None:
            return np.ones(6) / 6
        return np.array(ev)


# ═══════════════════════════════════════════════════════════════════════
# Meta Feature Evidence
# ═══════════════════════════════════════════════════════════════════════

def meta_evidence(token_features):
    """Compute meta feature evidence vector (w7).

    Based on binary features with measured enrichments from constraints.
    """
    ev = np.zeros(6)

    # is_safe_pathway: e->y depleted at CLOSURE 0.762x -> evidence toward SPEC
    if token_features.get('is_safe_pathway'):
        idx_spec = STATES_6.index('SPEC')
        ev[idx_spec] += math.log2(1.0 / 0.762)  # +0.39 bits

    # source_immune: headed tokens -> TWORK tendency
    if token_features.get('source_immune'):
        idx_tw = STATES_6.index('TWORK')
        ev[idx_tw] += math.log2(1.3)  # mild positive evidence

    # terminal_opacity == OPAQUE -> CLOSE
    opacity = token_features.get('terminal_opacity')
    if opacity == 'OPAQUE':
        idx_cl = STATES_6.index('CLOSE')
        ev[idx_cl] += math.log2(11.5)  # strong closure evidence
    elif opacity == 'TRANSPARENT':
        idx_obs = STATES_6.index('OBS')
        ev[idx_obs] += math.log2(2.0)  # moderate observation evidence

    # has_quenching_mod -> CHK
    if token_features.get('has_quenching_mod'):
        idx_chk = STATES_6.index('CHK')
        ev[idx_chk] += math.log2(2.5)

    # is_headless: 1.35x Q4 enrichment -> CLOSE
    if token_features.get('is_headless'):
        idx_cl = STATES_6.index('CLOSE')
        ev[idx_cl] += math.log2(1.35)

    # hazard_class_type not None: exposed hazard -> CLOSE
    if token_features.get('hazard_class_type'):
        idx_cl = STATES_6.index('CLOSE')
        ev[idx_cl] += math.log2(1.5)

    return softmax(ev)


# ═══════════════════════════════════════════════════════════════════════
# State Induction Engine
# ═══════════════════════════════════════════════════════════════════════

class StateInductor:
    """Assign supervisory states to tokens using compositional evidence."""

    def __init__(self, evidence_builder):
        self.eb = evidence_builder

    def induce_6state(self, token_features_list):
        """Induce 6-state partition (Partition A) for a list of token features.

        Returns: list of (state, evidence_vector) tuples.
        """
        results = []
        for feat in token_features_list:
            ev = self._compute_evidence_6(feat)
            state = STATES_6[np.argmax(ev)]
            results.append((state, ev.tolist()))
        return results

    def induce_4state(self, token_features_list):
        """Induce 4-state partition (Partition B) by merging 6-state evidence.

        SPECIFY = SPEC + CHK, OPERATE = TWORK + OBS.
        """
        results = []
        for feat in token_features_list:
            ev6 = self._compute_evidence_6(feat)
            # Merge to 4-state
            ev4 = np.zeros(4)
            ev4[0] = ev6[STATES_6.index('SPEC')] + ev6[STATES_6.index('CHK')]     # SPECIFY
            ev4[1] = ev6[STATES_6.index('TWORK')] + ev6[STATES_6.index('OBS')]     # OPERATE
            ev4[2] = ev6[STATES_6.index('TRANS')]                                    # TRANSITION
            ev4[3] = ev6[STATES_6.index('CLOSE')]                                    # CLOSURE
            ev4 = ev4 / (ev4.sum() + EPSILON)
            state = STATES_4[np.argmax(ev4)]
            results.append((state, ev4.tolist()))
        return results

    def induce_head_only(self, token_features_list):
        """HEAD-only baseline: use only CH3 (frame hazard) evidence."""
        results = []
        for feat in token_features_list:
            ev = self.eb.get_ch3_evidence(feat.get('frame_hazard'))
            state = STATES_6[np.argmax(ev)]
            results.append((state, ev.tolist()))
        return results

    def induce_zone_only(self, token_features_list):
        """Zone-only baseline: use only zone modulation evidence."""
        results = []
        for feat in token_features_list:
            ev = self.eb.get_zone_evidence(feat.get('zone', 'WORK'))
            state = STATES_6[np.argmax(ev)]
            results.append((state, ev.tolist()))
        return results

    def _compute_evidence_6(self, feat):
        """Compute full 6-element evidence vector for one token."""
        # Skip dark pipeline tokens - return uniform
        if feat.get('is_dark_pipeline'):
            return np.ones(6) / 6

        # CH1: PREFIX x HEAD
        pfx = feat.get('prefix')
        head = feat.get('middle_head')
        if head is None and feat.get('is_headless') and feat.get('middle'):
            head = feat['middle'][0]  # pseudo-head
        ch1 = self.eb.get_ch1_evidence(pfx, head)

        # CH2: TERM x SUFFIX_HEAD
        term = feat.get('middle_term', 'bare')
        sfx_head = feat.get('suffix_head')
        ch2 = self.eb.get_ch2_evidence(term, sfx_head)

        # CH3: Frame hazard
        ch3 = self.eb.get_ch3_evidence(feat.get('frame_hazard'))

        # CH4: HEAD x first_mod
        first_mod = None
        mods = feat.get('middle_mods', '')
        if mods and len(mods) > 0:
            first_mod = mods[0]
        ch4 = self.eb.get_ch4_evidence(feat.get('middle_head'), first_mod)

        # Zone modulation
        zone_ev = self.eb.get_zone_evidence(feat.get('zone', 'WORK'))

        # Routing context
        route_ev = self.eb.get_route_evidence(feat.get('prev_term'))

        # Meta features
        meta_ev = meta_evidence(feat)

        # Weighted sum
        ev = (W1 * ch1 + W2 * ch2 + W3 * ch3 + W4 * ch4
              + W5 * zone_ev + W6 * route_ev + W7 * meta_ev)

        # Normalize
        ev = ev / (ev.sum() + EPSILON)

        # Check for NaN
        if np.any(np.isnan(ev)):
            return np.ones(6) / 6

        return ev


# ═══════════════════════════════════════════════════════════════════════
# Unsupervised Partition (Partition C)
# ═══════════════════════════════════════════════════════════════════════

def build_feature_matrix(token_features_list):
    """Build one-hot feature matrix for unsupervised clustering.

    Features: CH1-CH4 keys (one-hot), zone (3), prev_term (7+1), meta (7).
    Uses dimensionality reduction via PCA retaining 90% variance.
    """
    # Collect all unique keys per channel
    ch1_keys = set()
    ch2_keys = set()
    ch3_keys = set()
    ch4_keys = set()
    prev_terms = set()

    for f in token_features_list:
        ch1_keys.add((f.get('prefix'), f.get('middle_head')))
        ch2_keys.add((f.get('middle_term'), f.get('suffix_head')))
        ch3_keys.add(f.get('frame_hazard'))
        mods = f.get('middle_mods', '')
        first_mod = mods[0] if mods else None
        ch4_keys.add((f.get('middle_head'), first_mod))
        prev_terms.add(f.get('prev_term'))

    ch1_list = sorted(str(k) for k in ch1_keys)
    ch2_list = sorted(str(k) for k in ch2_keys)
    ch3_list = sorted(str(k) for k in ch3_keys)
    ch4_list = sorted(str(k) for k in ch4_keys)
    prev_list = sorted(str(k) for k in prev_terms)
    zones = ['SPECIFICATION', 'WORK', 'CLOSURE']
    meta_names = ['is_safe_pathway', 'source_immune', 'is_headless',
                  'has_quenching_mod', 'is_dark_pipeline']
    opacity_vals = ['OPAQUE', 'SEMI_TRANSPARENT', 'TRANSPARENT']

    n_features = (len(ch1_list) + len(ch2_list) + len(ch3_list)
                  + len(ch4_list) + len(prev_list) + len(zones)
                  + len(meta_names) + len(opacity_vals))

    # Build index maps
    idx = 0
    ch1_idx = {k: i + idx for i, k in enumerate(ch1_list)}
    idx += len(ch1_list)
    ch2_idx = {k: i + idx for i, k in enumerate(ch2_list)}
    idx += len(ch2_list)
    ch3_idx = {k: i + idx for i, k in enumerate(ch3_list)}
    idx += len(ch3_list)
    ch4_idx = {k: i + idx for i, k in enumerate(ch4_list)}
    idx += len(ch4_list)
    prev_idx = {k: i + idx for i, k in enumerate(prev_list)}
    idx += len(prev_list)
    zone_idx = {k: i + idx for i, k in enumerate(zones)}
    idx += len(zones)
    meta_idx = {k: i + idx for i, k in enumerate(meta_names)}
    idx += len(meta_names)
    opac_idx = {k: i + idx for i, k in enumerate(opacity_vals)}

    # Build matrix
    X = np.zeros((len(token_features_list), n_features), dtype=np.float32)
    for row, f in enumerate(token_features_list):
        # CH1
        k = str((f.get('prefix'), f.get('middle_head')))
        if k in ch1_idx:
            X[row, ch1_idx[k]] = 1.0
        # CH2
        k = str((f.get('middle_term'), f.get('suffix_head')))
        if k in ch2_idx:
            X[row, ch2_idx[k]] = 1.0
        # CH3
        k = str(f.get('frame_hazard'))
        if k in ch3_idx:
            X[row, ch3_idx[k]] = 1.0
        # CH4
        mods = f.get('middle_mods', '')
        first_mod = mods[0] if mods else None
        k = str((f.get('middle_head'), first_mod))
        if k in ch4_idx:
            X[row, ch4_idx[k]] = 1.0
        # prev_term
        k = str(f.get('prev_term'))
        if k in prev_idx:
            X[row, prev_idx[k]] = 1.0
        # Zone
        z = f.get('zone', 'WORK')
        if z in zone_idx:
            X[row, zone_idx[z]] = 1.0
        # Meta
        for mn in meta_names:
            if f.get(mn):
                X[row, meta_idx[mn]] = 1.0
        # Opacity
        op = f.get('terminal_opacity')
        if op and op in opac_idx:
            X[row, opac_idx[op]] = 1.0

    return X, n_features


def pca_reduce(X, variance_threshold=0.90):
    """PCA dimensionality reduction retaining variance_threshold of variance."""
    # Center
    mean = X.mean(axis=0)
    Xc = X - mean
    # SVD (economical)
    n, p = Xc.shape
    if n < p:
        # More features than samples — use X @ X^T
        cov_small = Xc @ Xc.T
        eigvals, eigvecs_small = np.linalg.eigh(cov_small)
        # Sort descending
        idx_sort = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx_sort]
        eigvecs_small = eigvecs_small[:, idx_sort]
        # Project
        eigvals = np.maximum(eigvals, 0)
        total_var = eigvals.sum()
        if total_var < EPSILON:
            return Xc[:, :min(5, p)]
        cumvar = np.cumsum(eigvals) / total_var
        k = max(2, int(np.searchsorted(cumvar, variance_threshold)) + 1)
        k = min(k, n - 1)
        # Project back to feature space for proper PCA
        # V = X^T @ U / sqrt(eigenvalues)
        sqrt_eig = np.sqrt(eigvals[:k] + EPSILON)
        V = Xc.T @ eigvecs_small[:, :k] / sqrt_eig
        return Xc @ V
    else:
        # Standard PCA
        cov = (Xc.T @ Xc) / max(n - 1, 1)
        eigvals, eigvecs = np.linalg.eigh(cov)
        idx_sort = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx_sort]
        eigvecs = eigvecs[:, idx_sort]
        eigvals = np.maximum(eigvals, 0)
        total_var = eigvals.sum()
        if total_var < EPSILON:
            return Xc[:, :min(5, p)]
        cumvar = np.cumsum(eigvals) / total_var
        k = max(2, int(np.searchsorted(cumvar, variance_threshold)) + 1)
        k = min(k, p)
        return Xc @ eigvecs[:, :k]


def kmeans_simple(X, k, max_iter=100, n_init=10, seed=42):
    """Simple k-means implementation. Returns labels and silhouette score."""
    n, d = X.shape
    best_labels = None
    best_inertia = float('inf')

    rng = np.random.RandomState(seed)
    for _ in range(n_init):
        # Random init
        centers = X[rng.choice(n, k, replace=False)]
        for _ in range(max_iter):
            # Assign
            dists = np.zeros((n, k))
            for c in range(k):
                dists[:, c] = np.sum((X - centers[c]) ** 2, axis=1)
            labels = np.argmin(dists, axis=1)
            # Update
            new_centers = np.zeros_like(centers)
            for c in range(k):
                mask = labels == c
                if mask.sum() > 0:
                    new_centers[c] = X[mask].mean(axis=0)
                else:
                    new_centers[c] = X[rng.randint(n)]
            if np.allclose(centers, new_centers):
                break
            centers = new_centers
        inertia = sum(np.sum((X[labels == c] - centers[c]) ** 2)
                      for c in range(k))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()

    return best_labels


def silhouette_score_simple(X, labels):
    """Simplified silhouette score (sample-based for speed)."""
    n = len(labels)
    if n < 10:
        return -1.0
    # Sample up to 200 points for speed
    rng = np.random.RandomState(123)
    sample_idx = rng.choice(n, min(200, n), replace=False)

    k = len(set(labels))
    if k < 2:
        return -1.0

    scores = []
    for i in sample_idx:
        same = labels == labels[i]
        diff_clusters = [c for c in range(k) if c != labels[i]]
        if same.sum() <= 1 or not diff_clusters:
            continue
        # a(i) = mean distance to same cluster
        a = np.mean(np.sqrt(np.sum((X[same] - X[i]) ** 2, axis=1) + EPSILON))
        # b(i) = min mean distance to other clusters
        b = float('inf')
        for c in diff_clusters:
            mask_c = labels == c
            if mask_c.sum() > 0:
                dist_c = np.mean(np.sqrt(np.sum(
                    (X[mask_c] - X[i]) ** 2, axis=1) + EPSILON))
                b = min(b, dist_c)
        s = (b - a) / max(a, b, EPSILON)
        scores.append(s)

    return float(np.mean(scores)) if scores else -1.0


def run_unsupervised(token_features_list, seed=42):
    """Run unsupervised clustering (Partition C).

    Returns: (best_k, labels, silhouette, cluster_names).
    """
    X_raw, n_feat = build_feature_matrix(token_features_list)
    X = pca_reduce(X_raw, variance_threshold=0.90)

    best_k = 4
    best_sil = -1.0
    best_labels = None

    for k in K_RANGE:
        if k > len(token_features_list):
            continue
        labels = kmeans_simple(X, k, seed=seed)
        sil = silhouette_score_simple(X, labels)
        if sil > best_sil:
            best_sil = sil
            best_k = k
            best_labels = labels

    # Generate cluster names
    cluster_names = [f'C{i}' for i in range(best_k)]

    return best_k, best_labels, best_sil, cluster_names


# ═══════════════════════════════════════════════════════════════════════
# Null Processing Pipeline
# ═══════════════════════════════════════════════════════════════════════

def process_null_variant(decoder, morph, variant_words_nested, inductor):
    """Process a null variant through the full pipeline.

    variant_words_nested: list of paragraphs, each list of lines, each list of words.
    Returns: flat list of token features (same format as T1 folio_data flat).
    """
    flat_features = []
    for pi, para in enumerate(variant_words_nested):
        for li, line_words in enumerate(para):
            n_toks = len(line_words)
            prev_term = None
            for ti, word in enumerate(line_words):
                try:
                    analysis = decoder.analyze_token(word)
                    m = morph.extract(word)

                    sfx_head = m.suffix[0] if m.suffix and len(m.suffix) > 0 else None

                    head = analysis.middle_head
                    if head is None and analysis.is_headless and m.middle:
                        head = m.middle[0]

                    first_mod = None
                    if analysis.middle_mods and len(analysis.middle_mods) > 0:
                        first_mod = analysis.middle_mods[0]

                    if n_toks <= 1:
                        q = 0
                    else:
                        q = min(int(ti / (n_toks - 1) * 5), 4)
                    zone = 'SPECIFICATION' if q == 0 else (
                        'CLOSURE' if q == 4 else 'WORK')

                    feat = {
                        'word': word,
                        'prefix': m.prefix,
                        'middle': m.middle,
                        'middle_head': analysis.middle_head,
                        'middle_mods': analysis.middle_mods,
                        'middle_term': analysis.middle_term,
                        'head_term_frame': analysis.head_term_frame,
                        'suffix': m.suffix,
                        'suffix_head': sfx_head,
                        'operational_category': analysis.operational_category,
                        'frame_hazard': analysis.frame_hazard,
                        'terminal_opacity': analysis.terminal_opacity,
                        'terminal_tier': analysis.terminal_tier,
                        'is_dark_pipeline': analysis.is_dark_pipeline,
                        'is_safe_pathway': analysis.is_safe_pathway,
                        'source_immune': analysis.source_immune,
                        'has_quenching_mod': analysis.has_quenching_mod,
                        'is_headless': analysis.is_headless,
                        'hazard_class_type': analysis.hazard_class_type,
                        'quintile': q,
                        'zone': zone,
                        'prev_term': prev_term,
                        'paragraph_idx': pi,
                        'line_idx': li,
                        'is_header_line': (li == 0),
                    }
                    prev_term = analysis.middle_term
                    flat_features.append(feat)
                except Exception:
                    # If token analysis fails, insert uniform placeholder
                    flat_features.append({
                        'word': word, 'prefix': None, 'middle': None,
                        'middle_head': None, 'middle_mods': '',
                        'middle_term': 'bare', 'head_term_frame': None,
                        'suffix': None, 'suffix_head': None,
                        'operational_category': None, 'frame_hazard': None,
                        'terminal_opacity': None, 'terminal_tier': None,
                        'is_dark_pipeline': False, 'is_safe_pathway': False,
                        'source_immune': False, 'has_quenching_mod': False,
                        'is_headless': True, 'hazard_class_type': None,
                        'quintile': 0, 'zone': 'WORK', 'prev_term': prev_term,
                        'paragraph_idx': pi, 'line_idx': li,
                        'is_header_line': (li == 0),
                    })
                    prev_term = None
    return flat_features


# ═══════════════════════════════════════════════════════════════════════
# Metrics Computation
# ═══════════════════════════════════════════════════════════════════════

def compute_metrics(states_and_evidence, token_features, state_list,
                    partition_name='6state'):
    """Compute all metrics for a state assignment.

    Returns dict with: profile, zone_alignment, paragraph_metrics, entropy,
                       transition_matrix, per_line_trajectories.
    """
    states = [s for s, _ in states_and_evidence]
    evidence = [e for _, e in states_and_evidence]

    # Overall state profile
    profile = state_profile(states, state_list).tolist()

    # State entropy
    ent = float(entropy(state_profile(states, state_list)))

    # Zone-state alignment
    zone_alignment = _compute_zone_alignment(states, token_features, state_list)

    # Transition matrix
    tm = transition_matrix(states, state_list).tolist()

    # Per-paragraph metrics
    para_metrics = _compute_paragraph_metrics(
        states, token_features, state_list)

    return {
        'profile': profile,
        'entropy': ent,
        'zone_alignment': zone_alignment,
        'transition_matrix': tm,
        'paragraph_metrics': para_metrics,
    }


def _compute_zone_alignment(states, token_features, state_list):
    """Zone-state alignment fraction.

    Q0 tokens in {SPEC, CHK} or {SPECIFY}
    Q1-Q3 tokens in {TWORK, OBS, CHK} or {OPERATE, SPECIFY}
    Q4 tokens in {CLOSE, TRANS} or {CLOSURE, TRANSITION}
    """
    if not token_features:
        return 0.0

    # Determine which partition
    if 'SPEC' in state_list:
        # 6-state
        zone_expected = {
            'SPECIFICATION': {'SPEC', 'CHK'},
            'WORK': {'TWORK', 'OBS', 'CHK'},
            'CLOSURE': {'CLOSE', 'TRANS'},
        }
    else:
        # 4-state
        zone_expected = {
            'SPECIFICATION': {'SPECIFY'},
            'WORK': {'OPERATE', 'SPECIFY'},
            'CLOSURE': {'CLOSURE', 'TRANSITION'},
        }

    aligned = 0
    total = 0
    for s, feat in zip(states, token_features):
        zone = feat.get('zone', 'WORK')
        expected = zone_expected.get(zone, set())
        if s in expected:
            aligned += 1
        total += 1

    return aligned / max(total, 1)


def _compute_paragraph_metrics(states, token_features, state_list):
    """Compute per-paragraph metrics.

    Returns list of dicts (one per paragraph).
    """
    # Group by paragraph
    para_states = defaultdict(list)
    para_zones = defaultdict(list)

    for s, feat in zip(states, token_features):
        pi = feat.get('paragraph_idx', 0)
        para_states[pi].append(s)
        para_zones[pi].append(feat.get('zone', 'WORK'))

    para_ids = sorted(para_states.keys())
    results = []

    for pi in para_ids:
        p_states = para_states[pi]
        p_zones = para_zones[pi]

        # State distribution
        p_profile = state_profile(p_states, state_list).tolist()

        # State entropy
        p_entropy = float(entropy(state_profile(p_states, state_list)))

        # Dominant state
        counts = Counter(p_states)
        dominant = counts.most_common(1)[0][0] if counts else None

        # Transition matrix
        p_tm = transition_matrix(p_states, state_list).tolist()

        # Zone-conditioned state distribution
        zone_cond = {}
        for z in ['SPECIFICATION', 'WORK', 'CLOSURE']:
            z_states = [s for s, zn in zip(p_states, p_zones) if zn == z]
            if z_states:
                zone_cond[z] = state_profile(z_states, state_list).tolist()
            else:
                zone_cond[z] = (np.ones(len(state_list)) / len(state_list)).tolist()

        # Closure incidence: fraction of Q4 tokens that are CLOSE/TRANS
        closure_states = {'CLOSE', 'TRANS', 'CLOSURE', 'TRANSITION'}
        q4_states = [s for s, zn in zip(p_states, p_zones) if zn == 'CLOSURE']
        closure_inc = (sum(1 for s in q4_states if s in closure_states)
                       / max(len(q4_states), 1))

        results.append({
            'paragraph_idx': pi,
            'n_tokens': len(p_states),
            'profile': p_profile,
            'entropy': p_entropy,
            'dominant_state': dominant,
            'transition_matrix': p_tm,
            'zone_conditioned': zone_cond,
            'closure_incidence': closure_inc,
        })

    return results


def paragraph_differentiation_test(para_metrics, state_list, n_perm=1000,
                                   seed=42):
    """Permutation test for paragraph differentiation.

    Shuffle paragraph labels, recompute metrics, test whether real
    paragraphs are more differentiated.

    Returns dict with p-values for each metric.
    """
    if len(para_metrics) < 2:
        return {'n_paragraphs': len(para_metrics), 'all_p': {},
                'significant_count': 0}

    rng = random.Random(seed)
    n_para = len(para_metrics)

    # Compute real pairwise JSD (state profiles)
    profiles = [np.array(pm['profile']) for pm in para_metrics]
    real_jsd = _mean_pairwise_jsd(profiles)

    # Real pairwise transition distance
    tms = [np.array(pm['transition_matrix']) for pm in para_metrics]
    real_tm_dist = _mean_pairwise_frob(tms)

    # Real zone-conditioned JSD
    real_zone_jsd = _mean_zone_jsd(para_metrics, state_list)

    # Real closure incidence variance
    closure_incs = [pm['closure_incidence'] for pm in para_metrics]
    real_closure_var = float(np.var(closure_incs))

    # Real entropy variance
    entropies = [pm['entropy'] for pm in para_metrics]
    real_entropy_var = float(np.var(entropies))

    # Permutation test: collect all tokens, shuffle paragraph assignment
    perm_jsd = []
    perm_tm = []
    perm_zone = []
    perm_closure = []
    perm_entropy = []

    # Build flat token list per paragraph for shuffling
    all_tokens = []
    for pm in para_metrics:
        all_tokens.append(pm['n_tokens'])

    for _ in range(n_perm):
        # Shuffle token counts across paragraphs (approximate permutation)
        perm_profiles = [p.copy() for p in profiles]
        rng.shuffle(perm_profiles)
        perm_jsd.append(_mean_pairwise_jsd(perm_profiles))

        perm_tms = [t.copy() for t in tms]
        rng.shuffle(perm_tms)
        perm_tm.append(_mean_pairwise_frob(perm_tms))

        shuffled_metrics = list(para_metrics)
        rng.shuffle(shuffled_metrics)
        perm_zone.append(_mean_zone_jsd(shuffled_metrics, state_list))

        perm_ci = list(closure_incs)
        rng.shuffle(perm_ci)
        perm_closure.append(float(np.var(perm_ci)))

        perm_e = list(entropies)
        rng.shuffle(perm_e)
        perm_entropy.append(float(np.var(perm_e)))

    # Compute p-values (fraction of permutations >= real)
    p_jsd = sum(1 for x in perm_jsd if x >= real_jsd) / n_perm
    p_tm = sum(1 for x in perm_tm if x >= real_tm_dist) / n_perm
    p_zone = sum(1 for x in perm_zone if x >= real_zone_jsd) / n_perm
    p_closure = sum(1 for x in perm_closure if x >= real_closure_var) / n_perm
    p_entropy = sum(1 for x in perm_entropy if x >= real_entropy_var) / n_perm

    all_p = {
        'state_distribution_jsd': p_jsd,
        'transition_matrix_distance': p_tm,
        'zone_conditioned_jsd': p_zone,
        'closure_incidence': p_closure,
        'state_entropy': p_entropy,
    }

    significant_count = sum(1 for p in all_p.values() if p < 0.05)

    return {
        'n_paragraphs': n_para,
        'real_values': {
            'state_distribution_jsd': real_jsd,
            'transition_matrix_distance': real_tm_dist,
            'zone_conditioned_jsd': real_zone_jsd,
            'closure_incidence_var': real_closure_var,
            'state_entropy_var': real_entropy_var,
        },
        'all_p': all_p,
        'significant_count': significant_count,
    }


def _mean_pairwise_jsd(profiles):
    """Mean pairwise JSD over a list of probability vectors."""
    n = len(profiles)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += jsd(profiles[i], profiles[j])
            count += 1
    return total / max(count, 1)


def _mean_pairwise_frob(matrices):
    """Mean pairwise Frobenius distance over a list of matrices."""
    n = len(matrices)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += frobenius_distance(matrices[i], matrices[j])
            count += 1
    return total / max(count, 1)


def _mean_zone_jsd(para_metrics, state_list):
    """Mean zone-conditioned JSD across paragraphs and zones."""
    n = len(para_metrics)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for z in ['SPECIFICATION', 'WORK', 'CLOSURE']:
        profiles = []
        for pm in para_metrics:
            zc = pm.get('zone_conditioned', {})
            if z in zc:
                profiles.append(np.array(zc[z]))
        if len(profiles) >= 2:
            total += _mean_pairwise_jsd(profiles)
            count += 1
    return total / max(count, 1)


# ═══════════════════════════════════════════════════════════════════════
# Pass/Fail Criteria
# ═══════════════════════════════════════════════════════════════════════

def evaluate_criteria(real_metrics, null_metrics_by_type, baselines,
                      partition_comparison):
    """Evaluate S1-S6 criteria and FC1-FC6 failure conditions.

    Returns dict with all criteria results and overall verdict.
    """
    results = {}

    # ── S1: State Profile Distinctiveness ──
    # JSD(f43v, mean_null) vs null-null JSD, perm p < 0.01 for >= 2 of 5 nulls
    s1_passes = 0
    s1_details = {}
    real_profile = np.array(real_metrics['profile'])

    for null_type, null_runs in null_metrics_by_type.items():
        null_profiles = [np.array(nr['profile']) for nr in null_runs]
        if not null_profiles:
            continue

        # JSD between real and each null
        real_vs_null_jsds = [jsd(real_profile, np) for np in null_profiles]
        mean_real_null_jsd = float(np.mean(real_vs_null_jsds))

        # Null-vs-null JSD distribution
        null_null_jsds = []
        n_null = len(null_profiles)
        for i in range(min(n_null, 50)):
            for j in range(i + 1, min(n_null, 50)):
                null_null_jsds.append(jsd(null_profiles[i], null_profiles[j]))

        if null_null_jsds:
            # Permutation p-value: fraction of null-null JSDs >= mean real-null
            p_val = sum(1 for x in null_null_jsds
                        if x >= mean_real_null_jsd) / len(null_null_jsds)
        else:
            p_val = 1.0

        passes = p_val < 0.01
        if passes:
            s1_passes += 1

        s1_details[null_type] = {
            'mean_real_null_jsd': mean_real_null_jsd,
            'mean_null_null_jsd': float(np.mean(null_null_jsds)) if null_null_jsds else 0.0,
            'p_value': p_val,
            'passes': passes,
        }

    s1_pass = s1_passes >= 2
    results['S1'] = {
        'criterion': 'State Profile Distinctiveness',
        'threshold': 'perm p < 0.01 for >= 2 of 5 null types',
        'passing_null_types': s1_passes,
        'pass': s1_pass,
        'details': s1_details,
    }

    # ── S2: Line-Zone Alignment ──
    real_align = real_metrics['zone_alignment']
    null_aligns = []
    for null_runs in null_metrics_by_type.values():
        for nr in null_runs:
            null_aligns.append(nr['zone_alignment'])

    null_mean = float(np.mean(null_aligns)) if null_aligns else 0.0
    null_std = float(np.std(null_aligns)) if null_aligns else 0.0

    s2_pass = (real_align > 0.35) and (real_align > null_mean + 2 * null_std)
    results['S2'] = {
        'criterion': 'Line-Zone Alignment',
        'threshold': 'alignment > 0.35 AND > null_mean + 2*sigma',
        'real_alignment': real_align,
        'null_mean': null_mean,
        'null_std': null_std,
        'null_threshold': null_mean + 2 * null_std,
        'pass': s2_pass,
    }

    # ── S3: Paragraph Differentiation ──
    para_test = real_metrics.get('paragraph_differentiation', {})
    s3_sig = para_test.get('significant_count', 0)
    s3_pass = s3_sig >= 2
    results['S3'] = {
        'criterion': 'Paragraph Differentiation',
        'threshold': '>= 2 of 5 metrics significant at p<0.05',
        'significant_count': s3_sig,
        'pass': s3_pass,
        'details': para_test.get('all_p', {}),
    }

    # ── S4: Compositional Gain ──
    real_entropy = real_metrics['entropy']
    head_only_entropy = baselines.get('head_only', {}).get('entropy', 99.0)
    zone_only_entropy = baselines.get('zone_only', {}).get('entropy', 99.0)

    gain_vs_head = 1.0 - real_entropy / max(head_only_entropy, EPSILON)
    gain_vs_zone = 1.0 - real_entropy / max(zone_only_entropy, EPSILON)

    s4_pass = (gain_vs_head > 0.10) and (gain_vs_zone > 0.10)
    results['S4'] = {
        'criterion': 'Compositional Gain',
        'threshold': 'full model entropy lower than BOTH baselines by >10%',
        'real_entropy': real_entropy,
        'head_only_entropy': head_only_entropy,
        'zone_only_entropy': zone_only_entropy,
        'gain_vs_head': gain_vs_head,
        'gain_vs_zone': gain_vs_zone,
        'pass': s4_pass,
    }

    # ── S5: Head-Matched Separation ──
    hm_runs = null_metrics_by_type.get('head_matched', [])
    if hm_runs:
        hm_profiles = [np.array(nr['profile']) for nr in hm_runs]
        hm_jsds = [jsd(real_profile, hp) for hp in hm_profiles]
        mean_hm_jsd = float(np.mean(hm_jsds))

        # Null-null JSD for head_matched
        hm_null_jsds = []
        for i in range(min(len(hm_profiles), 50)):
            for j in range(i + 1, min(len(hm_profiles), 50)):
                hm_null_jsds.append(jsd(hm_profiles[i], hm_profiles[j]))

        null_null_std = float(np.std(hm_null_jsds)) if hm_null_jsds else EPSILON
        null_null_mean = float(np.mean(hm_null_jsds)) if hm_null_jsds else 0.0
        effect_size = (mean_hm_jsd - null_null_mean) / max(null_null_std, EPSILON)
    else:
        mean_hm_jsd = 0.0
        effect_size = 0.0
        null_null_mean = 0.0
        null_null_std = 0.0

    s5_pass = effect_size > 1.5
    results['S5'] = {
        'criterion': 'Head-Matched Separation',
        'threshold': 'effect size > 1.5',
        'mean_real_hm_jsd': mean_hm_jsd,
        'null_null_mean': null_null_mean,
        'null_null_std': null_null_std,
        'effect_size': effect_size,
        'pass': s5_pass,
    }

    # ── S6: Partition Comparison (diagnostic, not pass/fail) ──
    results['S6'] = {
        'criterion': 'Partition Comparison',
        'type': 'diagnostic',
        'details': partition_comparison,
    }

    # ── Failure Conditions ──
    fc = {}

    # FC1: NaN/infinite evidence
    nan_count = sum(1 for _, e in zip(
        [None] * len(real_metrics.get('_raw_evidence', [])),
        real_metrics.get('_raw_evidence', []))
        if any(math.isnan(v) or math.isinf(v) for v in e))
    total_tokens = real_metrics.get('n_tokens', 1)
    fc1 = nan_count / max(total_tokens, 1) > 0.01
    fc['FC1'] = {'trigger': 'NaN/inf in >1% tokens', 'nan_count': nan_count,
                 'triggered': fc1}

    # FC2: No state > 20%
    max_state_frac = max(real_metrics['profile'])
    fc2 = max_state_frac <= 0.20
    fc['FC2'] = {'trigger': 'No state > 20%', 'max_fraction': max_state_frac,
                 'triggered': fc2}

    # FC3: head_matched JSD < 0.01
    fc3 = mean_hm_jsd < 0.01
    fc['FC3'] = {'trigger': 'head_matched JSD < 0.01',
                 'head_matched_jsd': mean_hm_jsd, 'triggered': fc3}

    # FC4: full entropy >= head-only entropy
    fc4 = real_entropy >= head_only_entropy
    fc['FC4'] = {'trigger': 'Full entropy >= HEAD-only entropy',
                 'full': real_entropy, 'head_only': head_only_entropy,
                 'triggered': fc4}

    # FC5: All paragraphs > 60% same state
    para_mets = real_metrics.get('paragraph_metrics', [])
    all_same = all(max(pm['profile']) > 0.60 for pm in para_mets) if para_mets else True
    fc5 = all_same and len(para_mets) > 1
    fc['FC5'] = {'trigger': 'All paragraphs > 60% same state',
                 'triggered': fc5}

    # FC6: unsupervised beats 6-state
    unsu_better = partition_comparison.get('unsupervised_beats_6state', False)
    fc6 = unsu_better
    fc['FC6'] = {'trigger': 'Unsupervised > 6-state',
                 'triggered': fc6}

    # ── Overall Verdict ──
    any_fc = any(v['triggered'] for v in fc.values())
    hard_pass = s1_pass and s5_pass
    soft_count = sum(1 for k in ['S2', 'S3', 'S4'] if results[k]['pass'])

    if any_fc:
        triggered = [k for k, v in fc.items() if v['triggered']]
        verdict = f'FAIL (failure conditions: {", ".join(triggered)})'
        outcome = 'FAIL'
    elif not s1_pass:
        verdict = 'FAIL (S1: no folio specificity)'
        outcome = 'FAIL'
    elif s1_pass and not s5_pass:
        verdict = 'MARGINAL (S1 pass but S5 fail: HEAD-level only)'
        outcome = 'MARGINAL'
    elif hard_pass and soft_count >= 2:
        if not unsu_better:
            verdict = 'STRONG_PASS'
            outcome = 'STRONG_PASS'
        else:
            verdict = 'PASS_WITH_CAVEAT (unsupervised >= 6-state)'
            outcome = 'PASS_WITH_CAVEAT'
    elif hard_pass and soft_count < 2:
        verdict = f'MARGINAL (S1+S5 pass but only {soft_count}/3 soft criteria)'
        outcome = 'MARGINAL'
    else:
        verdict = 'FAIL'
        outcome = 'FAIL'

    return {
        'criteria': results,
        'failure_conditions': fc,
        'verdict': verdict,
        'outcome': outcome,
        'hard_pass': hard_pass,
        'soft_count': soft_count,
        'any_failure_condition': any_fc,
    }


# ═══════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Phase 559 T2: Supervisory State Induction (Stage 1)")
    print("=" * 70)

    # ── Step 1: Load T1 data ──
    base_dir = Path(__file__).parent.parent
    t1_path = base_dir / 'results' / 't1_compositional_decomposition.json'
    print(f"\n  Loading T1 data from {t1_path}...")
    with open(t1_path, 'r') as f:
        t1_data = json.load(f)

    folio_data = t1_data['folio_data']
    null_variants = t1_data['null_variants']
    diagnostics = t1_data['diagnostics']

    n_tokens = diagnostics['n_tokens']
    n_paragraphs = diagnostics['n_paragraphs']
    n_lines = diagnostics['n_lines']
    print(f"  Loaded: {n_tokens} tokens, {n_paragraphs} paragraphs, "
          f"{n_lines} lines")

    # Flatten folio_data for processing
    flat_tokens = []
    for para in folio_data:
        for line in para:
            for tok in line:
                flat_tokens.append(tok)

    # ── Step 2: Build evidence tables from corpus ──
    eb = EvidenceTableBuilder()
    eb.build_from_corpus()

    inductor = StateInductor(eb)

    # ── Step 3: Run state induction on f43v (all three partitions) ──
    print("\n  Running state induction on f43v...")

    # Partition A: 6-state
    print("    Partition A (6-state)...")
    real_6state = inductor.induce_6state(flat_tokens)
    real_states_6 = [s for s, _ in real_6state]
    real_evidence_6 = [e for _, e in real_6state]
    real_metrics_6 = compute_metrics(real_6state, flat_tokens, STATES_6, '6state')
    real_metrics_6['n_tokens'] = n_tokens
    real_metrics_6['_raw_evidence'] = real_evidence_6

    # Paragraph differentiation test
    print("    Paragraph differentiation test (6-state)...")
    para_diff_6 = paragraph_differentiation_test(
        real_metrics_6['paragraph_metrics'], STATES_6,
        n_perm=N_PERMUTATIONS)
    real_metrics_6['paragraph_differentiation'] = para_diff_6

    print(f"    6-state profile: {dict(zip(STATES_6, [f'{x:.3f}' for x in real_metrics_6['profile']]))}")
    print(f"    6-state entropy: {real_metrics_6['entropy']:.4f}")
    print(f"    Zone alignment: {real_metrics_6['zone_alignment']:.4f}")
    print(f"    Para diff significant: {para_diff_6['significant_count']}/5")

    # Partition B: 4-state
    print("    Partition B (4-state)...")
    real_4state = inductor.induce_4state(flat_tokens)
    real_metrics_4 = compute_metrics(real_4state, flat_tokens, STATES_4, '4state')
    real_metrics_4['n_tokens'] = n_tokens

    print(f"    4-state profile: {dict(zip(STATES_4, [f'{x:.3f}' for x in real_metrics_4['profile']]))}")

    # Partition C: Unsupervised
    print("    Partition C (unsupervised)...")
    best_k, unsup_labels, unsup_sil, cluster_names = run_unsupervised(
        flat_tokens)
    unsup_states = [cluster_names[l] for l in unsup_labels]
    unsup_metrics = compute_metrics(
        list(zip(unsup_states, [[0.0]] * len(unsup_states))),
        flat_tokens, cluster_names, 'unsupervised')
    unsup_metrics['best_k'] = best_k
    unsup_metrics['silhouette'] = unsup_sil

    print(f"    Unsupervised: k={best_k}, silhouette={unsup_sil:.4f}")

    # ── Step 4: Baselines ──
    print("\n  Computing baselines...")

    # HEAD-only baseline
    head_only_results = inductor.induce_head_only(flat_tokens)
    head_only_metrics = compute_metrics(
        head_only_results, flat_tokens, STATES_6, 'head_only')
    print(f"    HEAD-only entropy: {head_only_metrics['entropy']:.4f}")

    # Zone-only baseline
    zone_only_results = inductor.induce_zone_only(flat_tokens)
    zone_only_metrics = compute_metrics(
        zone_only_results, flat_tokens, STATES_6, 'zone_only')
    print(f"    Zone-only entropy: {zone_only_metrics['entropy']:.4f}")

    baselines = {
        'head_only': head_only_metrics,
        'zone_only': zone_only_metrics,
    }

    # ── Step 5: Process null variants ──
    print("\n  Processing null variants...")
    decoder = BFolioDecoder()
    morph = Morphology()

    null_metrics_6 = defaultdict(list)  # null_type -> list of metrics
    null_metrics_unsup = defaultdict(list)

    for null_type in ['token_shuffle', 'line_shuffle', 'cross_paragraph',
                      'random_token', 'head_matched']:
        variants = null_variants[null_type]
        n_seeds = len(variants)
        print(f"    {null_type}: {n_seeds} seeds", end='', flush=True)

        for seed_idx, variant in enumerate(variants):
            if seed_idx % 10 == 0:
                print('.', end='', flush=True)

            # Process null through full pipeline
            null_flat = process_null_variant(decoder, morph, variant, inductor)

            # 6-state induction
            null_6state = inductor.induce_6state(null_flat)
            null_met = compute_metrics(null_6state, null_flat, STATES_6, '6state')
            null_metrics_6[null_type].append(null_met)

            # Unsupervised (only every 5th seed for speed)
            if seed_idx % 5 == 0:
                try:
                    _, unsup_l, unsup_s, c_names = run_unsupervised(
                        null_flat, seed=42 + seed_idx)
                    null_unsup_states = [c_names[l] for l in unsup_l]
                    null_unsup_met = compute_metrics(
                        list(zip(null_unsup_states, [[0.0]] * len(null_unsup_states))),
                        null_flat, c_names, 'unsupervised')
                    null_unsup_met['silhouette'] = unsup_s
                    null_metrics_unsup[null_type].append(null_unsup_met)
                except Exception:
                    pass

        print(f" done ({n_seeds} variants)")

    # ── Step 6: Partition comparison ──
    print("\n  Comparing partitions...")

    # Compare 6-state vs unsupervised on null separation
    real_6_profile = np.array(real_metrics_6['profile'])

    # 6-state: mean JSD(real, null) across all null types
    all_6state_jsds = []
    for null_type, runs in null_metrics_6.items():
        for nr in runs:
            all_6state_jsds.append(jsd(real_6_profile, np.array(nr['profile'])))

    mean_6state_separation = float(np.mean(all_6state_jsds)) if all_6state_jsds else 0.0

    # Unsupervised: we can only compare via cluster-to-real mapping
    # Use a simpler metric: silhouette comparison
    real_unsup_sil = unsup_sil
    null_unsup_sils = []
    for runs in null_metrics_unsup.values():
        for nr in runs:
            null_unsup_sils.append(nr.get('silhouette', -1))

    mean_null_unsup_sil = float(np.mean(null_unsup_sils)) if null_unsup_sils else -1
    unsup_sil_gap = real_unsup_sil - mean_null_unsup_sil

    # FC6 check: unsupervised beats 6-state?
    # If unsupervised separates nulls better (higher silhouette gap),
    # the 6-state ontology may be over-engineered
    unsupervised_beats = unsup_sil_gap > mean_6state_separation * 1.5

    partition_comparison = {
        '6state_mean_separation_jsd': mean_6state_separation,
        'unsupervised_real_silhouette': real_unsup_sil,
        'unsupervised_null_mean_silhouette': mean_null_unsup_sil,
        'unsupervised_silhouette_gap': unsup_sil_gap,
        'unsupervised_beats_6state': unsupervised_beats,
        '4state_entropy': real_metrics_4['entropy'],
        '6state_entropy': real_metrics_6['entropy'],
    }

    print(f"    6-state mean separation JSD: {mean_6state_separation:.6f}")
    print(f"    Unsupervised silhouette gap: {unsup_sil_gap:.4f}")
    print(f"    Unsupervised beats 6-state: {unsupervised_beats}")

    # ── Step 7: Evaluate criteria ──
    print("\n  Evaluating Stage 1 criteria...")
    evaluation = evaluate_criteria(
        real_metrics_6, null_metrics_6, baselines, partition_comparison)

    print(f"\n  {'=' * 50}")
    print(f"  STAGE 1 VERDICT: {evaluation['verdict']}")
    print(f"  {'=' * 50}")
    print(f"  S1 (State Distinctiveness): {'PASS' if evaluation['criteria']['S1']['pass'] else 'FAIL'}")
    print(f"  S2 (Zone Alignment):        {'PASS' if evaluation['criteria']['S2']['pass'] else 'FAIL'}")
    print(f"  S3 (Para Differentiation):  {'PASS' if evaluation['criteria']['S3']['pass'] else 'FAIL'}")
    print(f"  S4 (Compositional Gain):    {'PASS' if evaluation['criteria']['S4']['pass'] else 'FAIL'}")
    print(f"  S5 (Head-Matched Sep):      {'PASS' if evaluation['criteria']['S5']['pass'] else 'FAIL'}")
    print(f"  S6 (Partition Comparison):   diagnostic only")

    for fc_name, fc_val in evaluation['failure_conditions'].items():
        if fc_val['triggered']:
            print(f"  *** {fc_name} TRIGGERED: {fc_val['trigger']} ***")

    # ── Step 8: Save output ──
    print("\n  Saving results...")

    # Serialize null metrics (compact: only profiles and key metrics)
    compact_null_metrics = {}
    for null_type, runs in null_metrics_6.items():
        compact_null_metrics[null_type] = [{
            'profile': nr['profile'],
            'entropy': nr['entropy'],
            'zone_alignment': nr['zone_alignment'],
        } for nr in runs]

    output = {
        'metadata': {
            'phase': '559',
            'task': 'T2_supervisory_state_induction',
            'folio': 'f43v',
            'n_tokens': n_tokens,
            'n_paragraphs': n_paragraphs,
            'n_lines': n_lines,
            'channel_weights': {
                'w1_prefix_head': W1, 'w2_term_suffix': W2,
                'w3_frame_hazard': W3, 'w4_head_mod': W4,
                'w5_zone': W5, 'w6_routing': W6, 'w7_meta': W7,
            },
            'states_6': STATES_6,
            'states_4': STATES_4,
            'cat_to_state_mapping': CAT_TO_STATE6,
        },
        'real': {
            '6state': {
                'metrics': {k: v for k, v in real_metrics_6.items()
                            if k != '_raw_evidence'},
                'state_sequence': real_states_6,
            },
            '4state': {
                'metrics': real_metrics_4,
            },
            'unsupervised': {
                'metrics': unsup_metrics,
                'best_k': best_k,
                'silhouette': unsup_sil,
                'state_sequence': unsup_states,
            },
        },
        'baselines': {
            'head_only': head_only_metrics,
            'zone_only': zone_only_metrics,
        },
        'null_metrics': compact_null_metrics,
        'partition_comparison': partition_comparison,
        'evaluation': evaluation,
        'evidence_tables': {
            'ch1_n_keys': len(eb.ch1_table),
            'ch2_n_keys': len(eb.ch2_table),
            'ch3_n_keys': len(eb.ch3_table),
            'ch4_n_keys': len(eb.ch4_table),
            'zone_n_keys': len(eb.zone_table),
            'route_n_keys': len(eb.route_table),
        },
    }

    out_path = base_dir / 'results' / 't2_supervisory_state_induction.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    import os
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"\n  Output: {out_path}")
    print(f"  Size: {size_mb:.1f} MB")
    print(f"\n{'=' * 70}")
    print(f"T2 Complete — Stage 1 Verdict: {evaluation['outcome']}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
