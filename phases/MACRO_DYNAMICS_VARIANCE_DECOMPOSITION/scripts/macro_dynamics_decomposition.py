#!/usr/bin/env python3
"""
Phase 340: MACRO_DYNAMICS_VARIANCE_DECOMPOSITION
=================================================
Decomposes macro-state transition dynamics into contributions from PREFIX
routing, bridge-backbone density, and their interaction — with controls for
REGIME, section, and line position.

Tests:
  T1: MIDDLE-conditioned PREFIX routing (genuine routing vs C662 tautology)
  T2: Positional null model (routing vs positional grammar)
  T3: REGIME-stratified PREFIX routing (C979 control)
  T4: Bridge density as folio-level archetype predictor
  T5: Combined folio-level variance decomposition
  T5b: Archetype-stratified models (non-linear residual investigation)
  T5c: Geometric bridge feature (bridge centroid PCA as predictor)
  T6: Residual characterization
  T7: Synthesis / verdict

Depends on: C1010 (6-state partition), C1012 (PREFIX selectivity),
            C1015 (transition matrix, T8 informative failure),
            C1016 (folio archetypes, bridge conduit),
            C1011 (geometric independence), C979 (REGIME modulation),
            C1003 (pairwise compositionality), C1004 (SUFFIX zero info)

Re-derivation guards:
  - T1 controls for MIDDLE identity (avoids re-deriving C661)
  - T3 runs within-REGIME (avoids re-deriving C979)
  - T1 reports AXM-eligible vs non-AXM-eligible separately (avoids C977 artifact)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

# Canonical 6-state partition (FROZEN, from C1010/Phase 328)
MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
N_STATES = len(STATE_ORDER)

MIN_TRANSITIONS = 50  # Minimum transitions for reliable matrix estimation

# Gatekeeper classes from C1007
GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}

# Hazard / escape token definitions (from SISTER analysis)
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_TOKENS = HAZARD_SOURCES | HAZARD_TARGETS

N_PERM = 1000  # Number of permutations for null models


# ── Data Loading ─────────────────────────────────────────────────────

def load_token_to_class():
    """Load token→class mapping from CLASS_COSURVIVAL_TEST."""
    path = Path(__file__).resolve().parents[2] / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    """Load folio→REGIME mapping from OPS2."""
    path = Path(__file__).resolve().parents[2] / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    """Load folio archetype labels from C1016 (Phase 339)."""
    path = Path(__file__).resolve().parents[2] / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    return data['t2_archetype_discovery']


def load_bridge_middles():
    """Load bridge MIDDLE set from BRIDGE_MIDDLE_SELECTION_MECHANISM."""
    path = Path(__file__).resolve().parents[2] / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path) as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])


def build_corpus_data(token_to_class):
    """Build enriched token-level corpus data for all tests.

    Returns:
        tokens: list of dicts with keys:
            word, folio, line, section, prefix, middle, suffix,
            cls (instruction class), state (macro-state),
            line_pos_quartile (1-4), is_bridge (bool)
        folio_sections: {folio: section}
    """
    tx = Transcript()
    morph = Morphology()
    bridge_set = load_bridge_middles()

    # First pass: collect per-line token counts for position quartiles
    line_token_counts = Counter()  # (folio, line) → count
    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        raw_tokens.append(token)
        line_token_counts[(token.folio, token.line)] += 1

    # Second pass: build enriched token list
    tokens = []
    folio_sections = {}
    line_position_counter = Counter()  # (folio, line) → position within line

    for token in raw_tokens:
        w = token.word.strip()
        if not w or '*' in w:
            continue

        cls = token_to_class.get(w)
        if cls is None:
            continue
        state = CLASS_TO_STATE.get(int(cls))
        if state is None:
            continue

        m = morph.extract(w)
        prefix = m.prefix if m.prefix else '__BARE__'
        middle = m.middle if m.middle else None
        suffix = m.suffix if m.suffix else None

        if middle is None:
            continue

        # Compute line position quartile
        key = (token.folio, token.line)
        line_position_counter[key] += 1
        pos_in_line = line_position_counter[key]
        total_in_line = line_token_counts[key]
        if total_in_line <= 1:
            quartile = 1
        else:
            frac = (pos_in_line - 1) / (total_in_line - 1)  # 0.0 to 1.0
            quartile = min(int(frac * 4) + 1, 4)

        tokens.append({
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'cls': int(cls),
            'state': state,
            'line_pos_quartile': quartile,
            'is_bridge': middle in bridge_set,
            'is_gatekeeper': int(cls) in GATEKEEPER_CLASSES,
            'is_hazard': w in HAZARD_TOKENS,
        })
        folio_sections[token.folio] = token.section

    print(f"  Corpus tokens loaded: {len(tokens)}")
    print(f"  Folios: {len(folio_sections)}")
    print(f"  Bridge MIDDLEs in corpus: {len(bridge_set)}")

    return tokens, folio_sections


def build_folio_matrices(tokens):
    """Build per-folio transition matrices from token-level data."""
    # Group by (folio, line), preserving order
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])

    folio_line_states = defaultdict(dict)
    for (folio, line), states in line_states.items():
        folio_line_states[folio][(folio, line)] = states

    results = {}
    for folio, line_dict in folio_line_states.items():
        trans_counts = np.zeros((N_STATES, N_STATES), dtype=int)
        state_counts = np.zeros(N_STATES, dtype=int)
        n_tokens = 0

        for (_, _), states in line_dict.items():
            for s in states:
                state_counts[STATE_IDX[s]] += 1
                n_tokens += 1
            for i in range(len(states) - 1):
                s_from = states[i]
                s_to = states[i + 1]
                trans_counts[STATE_IDX[s_from], STATE_IDX[s_to]] += 1

        n_transitions = trans_counts.sum()
        state_dist = state_counts / state_counts.sum() if state_counts.sum() > 0 else state_counts.astype(float)

        trans_prob = None
        if n_transitions >= MIN_TRANSITIONS:
            row_sums = trans_counts.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums == 0, 1, row_sums)
            trans_prob = trans_counts / row_sums

        results[folio] = {
            'trans_counts': trans_counts,
            'state_counts': state_counts,
            'n_transitions': int(n_transitions),
            'n_tokens': int(n_tokens),
            'trans_prob': trans_prob,
            'state_dist': state_dist,
        }

    return results


# ── T1: MIDDLE-Conditioned PREFIX Routing ────────────────────────────

def run_t1(tokens):
    """Test whether PREFIX predicts macro-state WITHIN the same MIDDLE.

    This is the critical test separating genuine routing from the C662 tautology.
    For each MIDDLE that appears with >=2 PREFIXes and spans >=2 macro-states,
    does PREFIX predict which state the token is in?

    Reports separately for AXM-eligible vs non-AXM-eligible MIDDLEs
    to avoid the C977 artifact (EN/AX transitionally indistinguishable).
    """
    print("\n" + "=" * 60)
    print("T1: MIDDLE-Conditioned PREFIX Routing")
    print("=" * 60)

    # Group tokens by MIDDLE
    middle_groups = defaultdict(list)
    for t in tokens:
        middle_groups[t['middle']].append(t)

    # Identify eligible MIDDLEs: >=2 distinct PREFIXes AND >=2 macro-states
    eligible = {}
    for mid, toks in middle_groups.items():
        prefixes = set(t['prefix'] for t in toks)
        states = set(t['state'] for t in toks)
        if len(prefixes) >= 2 and len(states) >= 2:
            eligible[mid] = toks

    print(f"\n  Total MIDDLEs: {len(middle_groups)}")
    print(f"  With >=2 PREFIXes and >=2 states: {len(eligible)}")

    if len(eligible) == 0:
        print("  No eligible MIDDLEs found. FAIL.")
        return {'pass': False, 'error': 'no_eligible_middles'}

    # For each eligible MIDDLE, compute:
    # H(State | MIDDLE=m) = entropy of state distribution for this MIDDLE
    # H(State | PREFIX, MIDDLE=m) = weighted average entropy over PREFIXes
    reduction_ratios = []
    per_middle_results = []

    # Track AXM vs non-AXM eligibility
    axm_only_reductions = []
    non_axm_reductions = []

    for mid, toks in sorted(eligible.items()):
        n = len(toks)
        state_counts = Counter(t['state'] for t in toks)
        state_probs = np.array([state_counts.get(s, 0) for s in STATE_ORDER]) / n

        # Marginal entropy H(State | MIDDLE=m)
        h_marginal = -sum(p * np.log2(p) for p in state_probs if p > 0)

        # Conditional entropy H(State | PREFIX, MIDDLE=m)
        prefix_groups = defaultdict(list)
        for t in toks:
            prefix_groups[t['prefix']].append(t['state'])

        h_conditional = 0
        for pfx, pfx_states in prefix_groups.items():
            pfx_n = len(pfx_states)
            pfx_counts = Counter(pfx_states)
            pfx_probs = np.array([pfx_counts.get(s, 0) for s in STATE_ORDER]) / pfx_n
            h_pfx = -sum(p * np.log2(p) for p in pfx_probs if p > 0)
            h_conditional += (pfx_n / n) * h_pfx

        reduction = (h_marginal - h_conditional) / h_marginal if h_marginal > 0 else 0

        # Classify: does this MIDDLE span non-AXM states?
        non_axm_states = {s for s in state_counts if s not in ('AXM', 'AXm')}
        has_non_axm = len(non_axm_states) >= 1 and any(
            s not in ('AXM', 'AXm') for s in state_counts if state_counts[s] >= 2
        )

        reduction_ratios.append(reduction)
        if has_non_axm:
            non_axm_reductions.append(reduction)
        else:
            axm_only_reductions.append(reduction)

        per_middle_results.append({
            'middle': mid,
            'n_tokens': n,
            'n_prefixes': len(prefix_groups),
            'states': dict(state_counts),
            'h_marginal': round(h_marginal, 4),
            'h_conditional': round(h_conditional, 4),
            'reduction': round(reduction, 4),
            'has_non_axm_spanning': has_non_axm,
        })

    mean_reduction = np.mean(reduction_ratios)
    print(f"\n  Mean entropy reduction (within-MIDDLE): {mean_reduction:.4f}")
    print(f"    AXM-only spanning ({len(axm_only_reductions)}): "
          f"mean={np.mean(axm_only_reductions):.4f}" if axm_only_reductions else "    AXM-only: none")
    print(f"    Non-AXM spanning ({len(non_axm_reductions)}): "
          f"mean={np.mean(non_axm_reductions):.4f}" if non_axm_reductions else "    Non-AXM: none")

    # Permutation test: shuffle PREFIX labels within each MIDDLE group
    null_reductions = []
    for _ in range(N_PERM):
        perm_ratios = []
        for mid, toks in eligible.items():
            n = len(toks)
            state_counts = Counter(t['state'] for t in toks)
            state_probs = np.array([state_counts.get(s, 0) for s in STATE_ORDER]) / n
            h_marginal = -sum(p * np.log2(p) for p in state_probs if p > 0)

            # Shuffle prefixes within this MIDDLE group
            shuffled_prefixes = [t['prefix'] for t in toks]
            np.random.shuffle(shuffled_prefixes)

            prefix_groups = defaultdict(list)
            for t, sp in zip(toks, shuffled_prefixes):
                prefix_groups[sp].append(t['state'])

            h_conditional = 0
            for pfx_states in prefix_groups.values():
                pfx_n = len(pfx_states)
                pfx_counts = Counter(pfx_states)
                pfx_probs = np.array([pfx_counts.get(s, 0) for s in STATE_ORDER]) / pfx_n
                h_pfx = -sum(p * np.log2(p) for p in pfx_probs if p > 0)
                h_conditional += (pfx_n / n) * h_pfx

            reduction = (h_marginal - h_conditional) / h_marginal if h_marginal > 0 else 0
            perm_ratios.append(reduction)
        null_reductions.append(np.mean(perm_ratios))

    null_reductions = np.array(null_reductions)
    z_score = (mean_reduction - null_reductions.mean()) / (null_reductions.std() + 1e-10)
    p_value = (null_reductions >= mean_reduction).mean()

    print(f"\n  Permutation test (within-MIDDLE PREFIX shuffle):")
    print(f"    Observed: {mean_reduction:.4f}")
    print(f"    Null: {null_reductions.mean():.4f} +/- {null_reductions.std():.4f}")
    print(f"    z = {z_score:.2f}, p = {p_value:.4f}")

    p1_pass = p_value < 0.05
    print(f"\n  P1: MIDDLE-conditioned PREFIX routing significant (p < 0.05)?")
    print(f"  Verdict: {'PASS' if p1_pass else 'FAIL'}")

    return {
        'n_eligible_middles': len(eligible),
        'n_total_middles': len(middle_groups),
        'mean_reduction': round(float(mean_reduction), 4),
        'mean_reduction_axm_only': round(float(np.mean(axm_only_reductions)), 4) if axm_only_reductions else None,
        'mean_reduction_non_axm': round(float(np.mean(non_axm_reductions)), 4) if non_axm_reductions else None,
        'n_axm_only': len(axm_only_reductions),
        'n_non_axm': len(non_axm_reductions),
        'null_mean': round(float(null_reductions.mean()), 4),
        'null_std': round(float(null_reductions.std()), 4),
        'z_score': round(float(z_score), 2),
        'p_value': round(float(p_value), 4),
        'per_middle': per_middle_results,
        'pass': p1_pass,
    }


# ── T2: Positional Null Model ───────────────────────────────────────

def run_t2(tokens, t1_result):
    """Shuffle PREFIX assignments within line-position quartiles.

    If T1's PREFIX routing effect survives positional shuffling, it is
    genuine morphological routing. If it collapses, the effect is
    positional grammar (C1001) masquerading as routing.
    """
    print("\n" + "=" * 60)
    print("T2: Positional Null Model (C1001 Control)")
    print("=" * 60)

    observed_reduction = t1_result['mean_reduction']
    print(f"  T1 observed reduction: {observed_reduction:.4f}")

    # Group tokens by MIDDLE (same eligibility as T1)
    middle_groups = defaultdict(list)
    for t in tokens:
        middle_groups[t['middle']].append(t)

    eligible = {}
    for mid, toks in middle_groups.items():
        prefixes = set(t['prefix'] for t in toks)
        states = set(t['state'] for t in toks)
        if len(prefixes) >= 2 and len(states) >= 2:
            eligible[mid] = toks

    # Positional null: shuffle PREFIX within line-position quartile
    # This preserves the PREFIX×position relationship while breaking PREFIX×MIDDLE
    positional_null_reductions = []

    # Pre-group tokens by quartile for efficient shuffling
    quartile_prefixes = defaultdict(list)  # quartile → list of (middle_idx, token_idx, prefix)
    for mid_idx, (mid, toks) in enumerate(sorted(eligible.items())):
        for tok_idx, t in enumerate(toks):
            quartile_prefixes[t['line_pos_quartile']].append((mid_idx, tok_idx, t['prefix']))

    for perm_i in range(N_PERM):
        # Build position-shuffled prefix assignment
        shuffled_assignments = {}  # (mid_idx, tok_idx) → shuffled_prefix
        for q, entries in quartile_prefixes.items():
            prefixes_in_q = [e[2] for e in entries]
            np.random.shuffle(prefixes_in_q)
            for (mid_idx, tok_idx, _), new_pfx in zip(entries, prefixes_in_q):
                shuffled_assignments[(mid_idx, tok_idx)] = new_pfx

        # Recompute entropy reduction with shuffled prefixes
        perm_ratios = []
        for mid_idx, (mid, toks) in enumerate(sorted(eligible.items())):
            n = len(toks)
            state_counts = Counter(t['state'] for t in toks)
            state_probs = np.array([state_counts.get(s, 0) for s in STATE_ORDER]) / n
            h_marginal = -sum(p * np.log2(p) for p in state_probs if p > 0)

            prefix_groups = defaultdict(list)
            for tok_idx, t in enumerate(toks):
                pfx = shuffled_assignments.get((mid_idx, tok_idx), t['prefix'])
                prefix_groups[pfx].append(t['state'])

            h_conditional = 0
            for pfx_states in prefix_groups.values():
                pfx_n = len(pfx_states)
                pfx_counts = Counter(pfx_states)
                pfx_probs = np.array([pfx_counts.get(s, 0) for s in STATE_ORDER]) / pfx_n
                h_pfx = -sum(p * np.log2(p) for p in pfx_probs if p > 0)
                h_conditional += (pfx_n / n) * h_pfx

            reduction = (h_marginal - h_conditional) / h_marginal if h_marginal > 0 else 0
            perm_ratios.append(reduction)

        positional_null_reductions.append(np.mean(perm_ratios))

    positional_null = np.array(positional_null_reductions)
    z_pos = (observed_reduction - positional_null.mean()) / (positional_null.std() + 1e-10)
    p_pos = (positional_null >= observed_reduction).mean()

    print(f"\n  Positional null (PREFIX shuffled within quartile):")
    print(f"    Observed: {observed_reduction:.4f}")
    print(f"    Null: {positional_null.mean():.4f} +/- {positional_null.std():.4f}")
    print(f"    z = {z_pos:.2f}, p = {p_pos:.4f}")

    # How much of T1's signal is positional?
    # T1 null was random shuffle; T2 null is position-preserving shuffle
    t1_null = t1_result['null_mean']
    positional_contribution = (positional_null.mean() - t1_null) / (observed_reduction - t1_null) if observed_reduction > t1_null else 0
    print(f"\n  Positional contribution to routing signal: {positional_contribution:.1%}")
    print(f"    (T1 random null: {t1_null:.4f}, T2 positional null: {positional_null.mean():.4f})")

    p2_pass = p_pos < 0.05
    print(f"\n  P2: PREFIX routing survives positional shuffling (p < 0.05)?")
    print(f"  Verdict: {'PASS' if p2_pass else 'FAIL'}")

    return {
        'observed_reduction': round(float(observed_reduction), 4),
        'positional_null_mean': round(float(positional_null.mean()), 4),
        'positional_null_std': round(float(positional_null.std()), 4),
        'z_score': round(float(z_pos), 2),
        'p_value': round(float(p_pos), 4),
        'positional_contribution': round(float(positional_contribution), 4),
        't1_random_null': t1_result['null_mean'],
        'pass': p2_pass,
    }


# ── T3: REGIME-Stratified PREFIX Routing ─────────────────────────────

def run_t3(tokens, regime_map):
    """Run T1-style analysis within each REGIME separately.

    C979 predicts transition weights are REGIME-dependent for 4/6 states.
    If PREFIX routing magnitude varies by REGIME, it interacts with REGIME
    modulation rather than being an independent mechanism.
    """
    print("\n" + "=" * 60)
    print("T3: REGIME-Stratified PREFIX Routing")
    print("=" * 60)

    # Assign REGIME to each token
    regime_tokens = defaultdict(list)
    for t in tokens:
        r = regime_map.get(t['folio'], 'UNKNOWN')
        if r != 'UNKNOWN':
            regime_tokens[r].append(t)

    print(f"  REGIMEs: {sorted(regime_tokens.keys())}")
    for r in sorted(regime_tokens.keys()):
        print(f"    REGIME_{r}: {len(regime_tokens[r])} tokens")

    per_regime_results = {}
    regime_reductions = []

    for regime in sorted(regime_tokens.keys()):
        rtoks = regime_tokens[regime]

        # Find eligible MIDDLEs within this REGIME
        middle_groups = defaultdict(list)
        for t in rtoks:
            middle_groups[t['middle']].append(t)

        eligible = {}
        for mid, toks in middle_groups.items():
            prefixes = set(t['prefix'] for t in toks)
            states = set(t['state'] for t in toks)
            if len(prefixes) >= 2 and len(states) >= 2:
                eligible[mid] = toks

        if not eligible:
            print(f"\n  REGIME_{regime}: no eligible MIDDLEs")
            per_regime_results[regime] = {'n_eligible': 0, 'mean_reduction': None}
            continue

        # Compute mean within-MIDDLE entropy reduction
        reductions = []
        for mid, toks in eligible.items():
            n = len(toks)
            state_counts = Counter(t['state'] for t in toks)
            state_probs = np.array([state_counts.get(s, 0) for s in STATE_ORDER]) / n
            h_marginal = -sum(p * np.log2(p) for p in state_probs if p > 0)

            prefix_groups = defaultdict(list)
            for t in toks:
                prefix_groups[t['prefix']].append(t['state'])

            h_conditional = 0
            for pfx_states in prefix_groups.values():
                pfx_n = len(pfx_states)
                pfx_counts = Counter(pfx_states)
                pfx_probs = np.array([pfx_counts.get(s, 0) for s in STATE_ORDER]) / pfx_n
                h_pfx = -sum(p * np.log2(p) for p in pfx_probs if p > 0)
                h_conditional += (pfx_n / n) * h_pfx

            reduction = (h_marginal - h_conditional) / h_marginal if h_marginal > 0 else 0
            reductions.append(reduction)

        mean_red = np.mean(reductions)
        regime_reductions.append(mean_red)

        print(f"\n  REGIME_{regime}: {len(eligible)} eligible MIDDLEs, "
              f"mean reduction = {mean_red:.4f}")

        per_regime_results[regime] = {
            'n_eligible': len(eligible),
            'n_tokens': len(rtoks),
            'mean_reduction': round(float(mean_red), 4),
        }

    # Test: is reduction REGIME-invariant?
    if len(regime_reductions) >= 3:
        # Compare max vs min reduction across REGIMEs
        max_red = max(r['mean_reduction'] for r in per_regime_results.values() if r['mean_reduction'] is not None)
        min_red = min(r['mean_reduction'] for r in per_regime_results.values() if r['mean_reduction'] is not None)
        range_ratio = max_red / min_red if min_red > 0 else float('inf')
        print(f"\n  REGIME range: {min_red:.4f} to {max_red:.4f} (ratio: {range_ratio:.2f})")
    else:
        range_ratio = None

    # P3: PREFIX routing varies by REGIME (ratio > 1.5)
    p3_pass = range_ratio is not None and range_ratio > 1.5
    print(f"\n  P3: PREFIX routing varies by REGIME (range ratio > 1.5)?")
    print(f"  Verdict: {'PASS' if p3_pass else 'FAIL'}")

    return {
        'per_regime': {str(k): v for k, v in per_regime_results.items()},
        'range_ratio': round(float(range_ratio), 4) if range_ratio is not None else None,
        'pass': p3_pass,
    }


# ── T4: Bridge Density as Archetype Predictor ───────────────────────

def run_t4(tokens, folio_matrices, regime_map, archetype_data):
    """Test whether bridge MIDDLE density predicts folio archetype class.

    Controls:
    - Partial correlation controlling for REGIME
    - Bridge/gatekeeper overlap check
    """
    print("\n" + "=" * 60)
    print("T4: Bridge Density as Folio-Level Archetype Predictor")
    print("=" * 60)

    archetype_labels = archetype_data.get('folio_labels', {})
    best_k = archetype_data['best_k']

    # Compute per-folio bridge density, hazard density, gatekeeper density
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    folio_features = {}
    for folio, ftoks in folio_token_groups.items():
        if folio not in archetype_labels:
            continue
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue

        n = len(ftoks)
        bridge_count = sum(1 for t in ftoks if t['is_bridge'])
        hazard_count = sum(1 for t in ftoks if t['is_hazard'])
        gatekeeper_count = sum(1 for t in ftoks if t['is_gatekeeper'])

        folio_features[folio] = {
            'bridge_density': bridge_count / n,
            'hazard_density': hazard_count / n,
            'gatekeeper_density': gatekeeper_count / n,
            'n_tokens': n,
            'archetype': archetype_labels[folio],
            'regime': regime_map.get(folio, 'UNKNOWN'),
            'axm_self': float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']]),
        }

    folios = sorted(folio_features.keys())
    n = len(folios)
    print(f"\n  Folios with bridge density and archetype: {n}")

    # Bridge/gatekeeper overlap check (C1007-C1009)
    bridge_set = load_bridge_middles()
    token_to_class = load_token_to_class()
    morph = Morphology()

    bridge_gatekeeper_overlap = set()
    bridge_non_gatekeeper = set()
    for mid in bridge_set:
        # Check if any token with this MIDDLE has a gatekeeper class
        found_gatekeeper = False
        for w, cls in token_to_class.items():
            m = morph.extract(w)
            if m.middle == mid and int(cls) in GATEKEEPER_CLASSES:
                found_gatekeeper = True
                bridge_gatekeeper_overlap.add(mid)
                break
        if not found_gatekeeper:
            bridge_non_gatekeeper.add(mid)

    print(f"\n  Bridge/gatekeeper overlap check:")
    print(f"    Bridge MIDDLEs: {len(bridge_set)}")
    print(f"    Bridge + gatekeeper: {len(bridge_gatekeeper_overlap)}")
    print(f"    Bridge - gatekeeper: {len(bridge_non_gatekeeper)}")
    overlap_frac = len(bridge_gatekeeper_overlap) / len(bridge_set) if bridge_set else 0
    print(f"    Overlap fraction: {overlap_frac:.3f}")

    # Compute arrays
    bridge_densities = np.array([folio_features[f]['bridge_density'] for f in folios])
    axm_selfs = np.array([folio_features[f]['axm_self'] for f in folios])
    hazard_densities = np.array([folio_features[f]['hazard_density'] for f in folios])
    gatekeeper_densities = np.array([folio_features[f]['gatekeeper_density'] for f in folios])
    archetypes = np.array([folio_features[f]['archetype'] for f in folios])
    regimes = np.array([folio_features[f]['regime'] for f in folios])

    # Check if bridge density is constant (expected: 85/87 B MIDDLEs are bridges)
    bridge_density_constant = bridge_densities.std() < 1e-6
    bridge_density_mean = float(bridge_densities.mean())

    if bridge_density_constant:
        print(f"\n  ** Bridge density is constant at {bridge_density_mean:.4f} across all folios **")
        print(f"  This is expected: 85/87 B MIDDLEs are bridges (appear in both A and B).")
        print(f"  Bridge contribution to dynamics operates at the GEOMETRIC level")
        print(f"  (manifold centroid positioning, C1016.T8: ARI=0.141 vs 0.037),")
        print(f"  not at the density level.")
        rho_bridge_axm, p_bridge_axm = None, None
        eta2_archetype, p_anova = None, None
        rho_partial, p_partial = None, None
    else:
        rho_bridge_axm, p_bridge_axm = stats.spearmanr(bridge_densities, axm_selfs)
        print(f"\n  Bridge density ~ AXM self: rho={rho_bridge_axm:.4f}, p={p_bridge_axm:.6f}")

        # ANOVA: bridge density by archetype
        archetype_groups = defaultdict(list)
        for f in folios:
            archetype_groups[folio_features[f]['archetype']].append(folio_features[f]['bridge_density'])
        if len(archetype_groups) >= 2:
            f_stat, p_anova = stats.f_oneway(*[archetype_groups[k] for k in sorted(archetype_groups.keys())])
            grand_mean = bridge_densities.mean()
            ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in archetype_groups.values())
            ss_total = sum((v - grand_mean) ** 2 for g in archetype_groups.values() for v in g)
            eta2_archetype = ss_between / ss_total if ss_total > 0 else 0
            print(f"  ANOVA bridge ~ archetype: F={f_stat:.2f}, p={p_anova:.6f}, eta2={eta2_archetype:.4f}")
        else:
            eta2_archetype, p_anova = None, None
        rho_partial, p_partial = None, None

    # Hazard and gatekeeper correlations (these do vary)
    rho_hazard_axm, p_hazard_axm = stats.spearmanr(hazard_densities, axm_selfs)
    rho_gatekeeper_axm, p_gatekeeper_axm = stats.spearmanr(gatekeeper_densities, axm_selfs)

    print(f"\n  Correlations with AXM self-transition:")
    print(f"    Hazard density:     rho={rho_hazard_axm:.4f}, p={p_hazard_axm:.6f}")
    print(f"    Gatekeeper density: rho={rho_gatekeeper_axm:.4f}, p={p_gatekeeper_axm:.6f}")

    # Hazard density vs archetype (the actually varying predictor)
    hazard_groups = defaultdict(list)
    for f in folios:
        hazard_groups[folio_features[f]['archetype']].append(folio_features[f]['hazard_density'])

    if len(hazard_groups) >= 2:
        f_haz, p_haz = stats.f_oneway(*[hazard_groups[k] for k in sorted(hazard_groups.keys())])
        grand_mean_h = hazard_densities.mean()
        ss_between_h = sum(len(g) * (np.mean(g) - grand_mean_h) ** 2 for g in hazard_groups.values())
        ss_total_h = sum((v - grand_mean_h) ** 2 for g in hazard_groups.values() for v in g)
        eta2_hazard = ss_between_h / ss_total_h if ss_total_h > 0 else 0
        print(f"\n  Hazard density ~ archetype: F={f_haz:.2f}, p={p_haz:.6f}, eta2={eta2_hazard:.4f}")
    else:
        f_haz, p_haz, eta2_hazard = None, None, None

    # P4 reframed: hazard density predicts archetype (since bridge density is constant)
    p4_pass = p_haz is not None and p_haz < 0.05
    print(f"\n  P4 (reframed): Hazard density differentiates archetypes (p < 0.05)?")
    print(f"  Verdict: {'PASS' if p4_pass else 'FAIL'}")

    return {
        'n_folios': n,
        'bridge_gatekeeper_overlap': len(bridge_gatekeeper_overlap),
        'bridge_non_gatekeeper': len(bridge_non_gatekeeper),
        'overlap_fraction': round(overlap_frac, 3),
        'bridge_density_constant': bridge_density_constant,
        'bridge_density_mean': round(bridge_density_mean, 4),
        'bridge_density_note': '85/87 B MIDDLEs are bridges; density is constant; bridge effect is geometric (C1016.T8)' if bridge_density_constant else None,
        'rho_hazard_axm': round(float(rho_hazard_axm), 4),
        'p_hazard_axm': round(float(p_hazard_axm), 6),
        'rho_gatekeeper_axm': round(float(rho_gatekeeper_axm), 4),
        'p_gatekeeper_axm': round(float(p_gatekeeper_axm), 6),
        'eta2_hazard_archetype': round(float(eta2_hazard), 4) if eta2_hazard is not None else None,
        'anova_p_hazard': round(float(p_haz), 6) if p_haz is not None else None,
        'folio_features': {f: {k: round(v, 4) if isinstance(v, float) else v
                               for k, v in folio_features[f].items()}
                          for f in folios},
        'pass': p4_pass,
    }


# ── T5: Combined Folio-Level Variance Decomposition ─────────────────

def run_t5(tokens, folio_matrices, regime_map, folio_sections, archetype_data):
    """Combined variance decomposition: PREFIX composition + bridge density +
    hazard density → AXM self-transition rate.

    Pre-registered: interaction term (PREFIX × bridge) should be weak (C1003).
    """
    print("\n" + "=" * 60)
    print("T5: Combined Folio-Level Variance Decomposition")
    print("=" * 60)

    archetype_labels = archetype_data.get('folio_labels', {})

    # Build per-folio feature vectors
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    rows = []
    for folio, ftoks in folio_token_groups.items():
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue
        if folio not in archetype_labels:
            continue

        n = len(ftoks)

        # PREFIX composition: entropy of PREFIX distribution
        prefix_counts = Counter(t['prefix'] for t in ftoks)
        prefix_total = sum(prefix_counts.values())
        prefix_probs = np.array(list(prefix_counts.values())) / prefix_total
        prefix_entropy = -sum(p * np.log2(p) for p in prefix_probs if p > 0)

        # Dominant PREFIX fraction
        dominant_prefix_frac = max(prefix_counts.values()) / prefix_total

        # Bridge density
        bridge_density = sum(1 for t in ftoks if t['is_bridge']) / n

        # Hazard density
        hazard_density = sum(1 for t in ftoks if t['is_hazard']) / n

        # Gatekeeper density
        gatekeeper_density = sum(1 for t in ftoks if t['is_gatekeeper']) / n

        # SUFFIX composition entropy
        suffix_counts = Counter(t['suffix'] for t in ftoks if t['suffix'] is not None)
        if suffix_counts:
            suffix_total = sum(suffix_counts.values())
            suffix_probs = np.array(list(suffix_counts.values())) / suffix_total
            suffix_entropy = -sum(p * np.log2(p) for p in suffix_probs if p > 0)
        else:
            suffix_entropy = 0

        # AXM self-transition (dependent variable)
        axm_self = float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']])

        rows.append({
            'folio': folio,
            'axm_self': axm_self,
            'prefix_entropy': prefix_entropy,
            'dominant_prefix_frac': dominant_prefix_frac,
            'bridge_density': bridge_density,
            'hazard_density': hazard_density,
            'gatekeeper_density': gatekeeper_density,
            'suffix_entropy': suffix_entropy,
            'regime': regime_map.get(folio, 'UNKNOWN'),
            'section': folio_sections.get(folio, 'UNKNOWN'),
            'archetype': archetype_labels[folio],
            'n_tokens': n,
        })

    n = len(rows)
    print(f"\n  Folios in model: {n}")

    # Build arrays
    y = np.array([r['axm_self'] for r in rows])
    prefix_entropy = np.array([r['prefix_entropy'] for r in rows])
    dominant_pfx = np.array([r['dominant_prefix_frac'] for r in rows])
    bridge_density = np.array([r['bridge_density'] for r in rows])
    hazard_density = np.array([r['hazard_density'] for r in rows])
    gatekeeper_density = np.array([r['gatekeeper_density'] for r in rows])
    suffix_entropy = np.array([r['suffix_entropy'] for r in rows])
    regimes = np.array([r['regime'] for r in rows])
    sections = np.array([r['section'] for r in rows])

    # Standardize predictors
    def standardize(x):
        return (x - x.mean()) / (x.std() + 1e-10)

    prefix_z = standardize(prefix_entropy)
    hazard_z = standardize(hazard_density)

    # REGIME dummies
    unique_regimes = sorted(set(regimes))
    regime_dummies = np.zeros((n, max(len(unique_regimes) - 1, 1)))
    for i, r in enumerate(regimes):
        r_idx = unique_regimes.index(r)
        if r_idx > 0 and regime_dummies.shape[1] >= r_idx:
            regime_dummies[i, r_idx - 1] = 1

    # Section dummies
    unique_sections = sorted(set(sections))
    section_dummies = np.zeros((n, max(len(unique_sections) - 1, 1)))
    for i, s in enumerate(sections):
        s_idx = unique_sections.index(s)
        if s_idx > 0 and section_dummies.shape[1] >= s_idx:
            section_dummies[i, s_idx - 1] = 1

    # --- Model 1: REGIME + section only (baseline) ---
    X_base = np.column_stack([np.ones(n), regime_dummies, section_dummies])
    beta_base = np.linalg.lstsq(X_base, y, rcond=None)[0]
    y_pred_base = X_base @ beta_base
    ss_res_base = np.sum((y - y_pred_base) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2_base = 1 - ss_res_base / ss_tot if ss_tot > 0 else 0

    print(f"\n  Model 1 (REGIME + section): R² = {r2_base:.4f}")

    # --- Model 2: REGIME + section + PREFIX entropy ---
    X_pfx = np.column_stack([X_base, prefix_z])
    beta_pfx = np.linalg.lstsq(X_pfx, y, rcond=None)[0]
    y_pred_pfx = X_pfx @ beta_pfx
    ss_res_pfx = np.sum((y - y_pred_pfx) ** 2)
    r2_pfx = 1 - ss_res_pfx / ss_tot if ss_tot > 0 else 0
    delta_r2_pfx = r2_pfx - r2_base

    print(f"  Model 2a (+ PREFIX entropy): R² = {r2_pfx:.4f}  (ΔR² = {delta_r2_pfx:.4f})")

    # --- Model 2b: REGIME + section + hazard density ---
    X_haz = np.column_stack([X_base, hazard_z])
    beta_haz = np.linalg.lstsq(X_haz, y, rcond=None)[0]
    y_pred_haz = X_haz @ beta_haz
    ss_res_haz = np.sum((y - y_pred_haz) ** 2)
    r2_haz = 1 - ss_res_haz / ss_tot if ss_tot > 0 else 0
    delta_r2_haz_alone = r2_haz - r2_base

    print(f"  Model 2b (+ hazard density): R² = {r2_haz:.4f}  (ΔR² = {delta_r2_haz_alone:.4f})")

    # --- Note on bridge density ---
    # Bridge density is constant (~1.0) because 85/87 B MIDDLEs are bridges.
    # Bridge contribution is geometric (C1016.T8), not densimetric.
    # Models use PREFIX entropy + hazard density as the varying predictors.
    bridge_constant = bridge_density.std() < 1e-6
    if bridge_constant:
        print(f"\n  Note: bridge density constant ({bridge_density.mean():.4f}), excluded from models.")
        print(f"  Bridge effect is geometric (C1016.T8), not a folio-level density variable.")

    # --- Model 3: REGIME + section + PREFIX + hazard (additive) ---
    X_add = np.column_stack([X_base, prefix_z, hazard_z])
    beta_add = np.linalg.lstsq(X_add, y, rcond=None)[0]
    y_pred_add = X_add @ beta_add
    ss_res_add = np.sum((y - y_pred_add) ** 2)
    r2_add = 1 - ss_res_add / ss_tot if ss_tot > 0 else 0
    delta_r2_add = r2_add - r2_base

    print(f"  Model 3 (+ PREFIX + hazard): R² = {r2_add:.4f}  (ΔR² = {delta_r2_add:.4f})")

    # --- Model 4: REGIME + section + PREFIX + hazard + interaction ---
    interaction = prefix_z * hazard_z
    X_int = np.column_stack([X_base, prefix_z, hazard_z, interaction])
    beta_int = np.linalg.lstsq(X_int, y, rcond=None)[0]
    y_pred_int = X_int @ beta_int
    ss_res_int = np.sum((y - y_pred_int) ** 2)
    r2_int = 1 - ss_res_int / ss_tot if ss_tot > 0 else 0
    delta_r2_interaction = r2_int - r2_add

    print(f"  Model 4 (+ interaction): R² = {r2_int:.4f}  (ΔR²_interaction = {delta_r2_interaction:.4f})")

    # --- Model 5: Full (+ gatekeeper density) ---
    gatekeeper_z = standardize(gatekeeper_density)
    X_full = np.column_stack([X_base, prefix_z, hazard_z, gatekeeper_z])
    beta_full = np.linalg.lstsq(X_full, y, rcond=None)[0]
    y_pred_full = X_full @ beta_full
    ss_res_full = np.sum((y - y_pred_full) ** 2)
    r2_full = 1 - ss_res_full / ss_tot if ss_tot > 0 else 0
    delta_r2_gatekeeper = r2_full - r2_add

    print(f"  Model 5 (+ gatekeeper): R² = {r2_full:.4f}  (ΔR²_gatekeeper = {delta_r2_gatekeeper:.4f})")

    # --- F-tests for incremental predictors ---
    def f_test_increment(ss_res_reduced, ss_res_full_model, df_extra, n_obs, k_full):
        """F-test for nested model comparison."""
        if ss_res_full_model <= 0 or df_extra <= 0:
            return 0, 1.0
        df_res = n_obs - k_full
        if df_res <= 0:
            return 0, 1.0
        f_stat = ((ss_res_reduced - ss_res_full_model) / df_extra) / (ss_res_full_model / df_res)
        p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
        return float(f_stat), float(p_val)

    k_base = X_base.shape[1]

    f_pfx, p_f_pfx = f_test_increment(ss_res_base, ss_res_pfx, 1, n, k_base + 1)
    f_haz_alone, p_f_haz_alone = f_test_increment(ss_res_base, ss_res_haz, 1, n, k_base + 1)
    f_add, p_f_add = f_test_increment(ss_res_base, ss_res_add, 2, n, k_base + 2)
    f_int, p_f_int = f_test_increment(ss_res_add, ss_res_int, 1, n, k_base + 3)
    f_gate, p_f_gate = f_test_increment(ss_res_add, ss_res_full, 1, n, k_base + 3)

    print(f"\n  F-tests (incremental):")
    print(f"    PREFIX entropy:    F={f_pfx:.2f}, p={p_f_pfx:.6f}")
    print(f"    Hazard density:    F={f_haz_alone:.2f}, p={p_f_haz_alone:.6f}")
    print(f"    PREFIX + hazard:   F={f_add:.2f}, p={p_f_add:.6f}")
    print(f"    Interaction:       F={f_int:.2f}, p={p_f_int:.6f}")
    print(f"    Gatekeeper:        F={f_gate:.2f}, p={p_f_gate:.6f}")

    # Residual from best model
    residual_frac = 1 - r2_full
    print(f"\n  Full model residual: {residual_frac:.4f}")

    # --- Within-section checks (C552 control) ---
    # Sections are single letters: B (bio/herbal), S (stars), H, C, T
    for sec_code, sec_name in [('B', 'Bio/Herbal'), ('S', 'Stars')]:
        sec_mask = np.array([s == sec_code for s in sections])
        if sec_mask.sum() >= 10:
            y_s = y[sec_mask]
            pe_s = standardize(prefix_entropy[sec_mask])
            hz_s = standardize(hazard_density[sec_mask])
            n_s = sec_mask.sum()

            X_s = np.column_stack([np.ones(n_s), pe_s, hz_s])
            beta_s = np.linalg.lstsq(X_s, y_s, rcond=None)[0]
            y_pred_s = X_s @ beta_s
            ss_res_s = np.sum((y_s - y_pred_s) ** 2)
            ss_tot_s = np.sum((y_s - y_s.mean()) ** 2)
            r2_sec = 1 - ss_res_s / ss_tot_s if ss_tot_s > 0 else 0
            print(f"\n  Within-{sec_name} check (n={n_s}): R² = {r2_sec:.4f}")
        else:
            print(f"\n  Within-{sec_name} check: insufficient data ({sec_mask.sum()} folios)")

    # Use the largest section for the return value
    bio_mask = np.array([s == 'B' for s in sections])
    if bio_mask.sum() >= 10:
        y_b = y[bio_mask]
        pe_b = standardize(prefix_entropy[bio_mask])
        hz_b = standardize(hazard_density[bio_mask])
        X_b = np.column_stack([np.ones(bio_mask.sum()), pe_b, hz_b])
        beta_b = np.linalg.lstsq(X_b, y_b, rcond=None)[0]
        r2_within_section = 1 - np.sum((y_b - X_b @ beta_b) ** 2) / np.sum((y_b - y_b.mean()) ** 2)
    else:
        r2_within_section = None

    # P5: interaction weak (ΔR² < 0.05)
    p5_pass = delta_r2_interaction < 0.05
    print(f"\n  P5: Interaction term weak (ΔR² < 0.05)? ΔR² = {delta_r2_interaction:.4f}")
    print(f"  Verdict: {'PASS (weak interaction, as C1003 predicts)' if p5_pass else 'FAIL'}")

    # P6: combined model > 40% of AXM self variance
    p6_pass = r2_full > 0.40
    print(f"\n  P6: Full model R² > 0.40? R² = {r2_full:.4f}")
    print(f"  Verdict: {'PASS' if p6_pass else 'FAIL'}")

    return {
        'n_folios': n,
        'bridge_density_constant': bridge_constant,
        'r2_base': round(float(r2_base), 4),
        'r2_prefix': round(float(r2_pfx), 4),
        'r2_hazard_alone': round(float(r2_haz), 4),
        'r2_additive': round(float(r2_add), 4),
        'r2_interaction': round(float(r2_int), 4),
        'r2_full': round(float(r2_full), 4),
        'delta_r2_prefix': round(float(delta_r2_pfx), 4),
        'delta_r2_hazard_alone': round(float(delta_r2_haz_alone), 4),
        'delta_r2_additive': round(float(delta_r2_add), 4),
        'delta_r2_interaction': round(float(delta_r2_interaction), 4),
        'delta_r2_gatekeeper': round(float(delta_r2_gatekeeper), 4),
        'residual_frac': round(float(residual_frac), 4),
        'f_prefix': round(float(f_pfx), 2),
        'p_prefix': round(float(p_f_pfx), 6),
        'f_hazard_alone': round(float(f_haz_alone), 2),
        'p_hazard_alone': round(float(p_f_haz_alone), 6),
        'f_additive': round(float(f_add), 2),
        'p_additive': round(float(p_f_add), 6),
        'f_interaction': round(float(f_int), 2),
        'p_interaction': round(float(p_f_int), 6),
        'f_gatekeeper': round(float(f_gate), 2),
        'p_gatekeeper': round(float(p_f_gate), 6),
        'r2_within_section': round(float(r2_within_section), 4) if r2_within_section is not None else None,
        'pass_p5_weak_interaction': p5_pass,
        'pass_p6_explained_variance': p6_pass,
    }


# ── T5b: Archetype-Stratified Analysis ───────────────────────────────

def run_t5b(tokens, folio_matrices, regime_map, folio_sections, archetype_data):
    """Run separate regression models within each archetype.

    The T5 residual is significantly structured by archetype (F=6.71, p<0.0001).
    This test asks: do PREFIX entropy and hazard density have different slopes
    within different archetypes? If so, the non-linear residual reflects
    archetype-specific routing patterns.
    """
    print("\n" + "=" * 60)
    print("T5b: Archetype-Stratified Models")
    print("=" * 60)

    archetype_labels = archetype_data.get('folio_labels', {})

    # Build per-folio data (same as T5)
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    rows = []
    for folio, ftoks in folio_token_groups.items():
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue
        if folio not in archetype_labels:
            continue

        n_f = len(ftoks)
        prefix_counts = Counter(t['prefix'] for t in ftoks)
        prefix_total = sum(prefix_counts.values())
        prefix_probs = np.array(list(prefix_counts.values())) / prefix_total
        prefix_entropy = -sum(p * np.log2(p) for p in prefix_probs if p > 0)

        hazard_density = sum(1 for t in ftoks if t['is_hazard']) / n_f
        axm_self = float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']])

        rows.append({
            'folio': folio,
            'archetype': archetype_labels[folio],
            'axm_self': axm_self,
            'prefix_entropy': prefix_entropy,
            'hazard_density': hazard_density,
        })

    def standardize(x):
        return (x - x.mean()) / (x.std() + 1e-10) if len(x) > 1 else x * 0

    per_archetype = {}
    unique_archetypes = sorted(set(r['archetype'] for r in rows))

    print(f"\n  Archetypes: {unique_archetypes}")

    for arch in unique_archetypes:
        arch_rows = [r for r in rows if r['archetype'] == arch]
        n_a = len(arch_rows)

        if n_a < 5:
            print(f"\n  Archetype {arch} (n={n_a}): too few folios")
            per_archetype[arch] = {'n': n_a, 'r2': None, 'note': 'insufficient data'}
            continue

        y_a = np.array([r['axm_self'] for r in arch_rows])
        pe_a = standardize(np.array([r['prefix_entropy'] for r in arch_rows]))
        hz_a = standardize(np.array([r['hazard_density'] for r in arch_rows]))

        X_a = np.column_stack([np.ones(n_a), pe_a, hz_a])
        beta_a = np.linalg.lstsq(X_a, y_a, rcond=None)[0]
        y_pred_a = X_a @ beta_a
        ss_res_a = np.sum((y_a - y_pred_a) ** 2)
        ss_tot_a = np.sum((y_a - y_a.mean()) ** 2)
        r2_a = 1 - ss_res_a / ss_tot_a if ss_tot_a > 1e-10 else 0

        # Coefficient interpretation
        beta_prefix = float(beta_a[1])
        beta_hazard = float(beta_a[2])

        print(f"\n  Archetype {arch} (n={n_a}): R²={r2_a:.4f}")
        print(f"    AXM self range: [{y_a.min():.3f}, {y_a.max():.3f}], mean={y_a.mean():.3f}")
        print(f"    β_PREFIX = {beta_prefix:.4f}, β_hazard = {beta_hazard:.4f}")

        per_archetype[arch] = {
            'n': n_a,
            'r2': round(float(r2_a), 4),
            'mean_axm_self': round(float(y_a.mean()), 4),
            'range_axm_self': [round(float(y_a.min()), 4), round(float(y_a.max()), 4)],
            'beta_prefix': round(float(beta_prefix), 4),
            'beta_hazard': round(float(beta_hazard), 4),
        }

    # Compare: do slopes differ across archetypes?
    betas_prefix = [v['beta_prefix'] for v in per_archetype.values() if v.get('r2') is not None]
    betas_hazard = [v['beta_hazard'] for v in per_archetype.values() if v.get('r2') is not None]
    r2s = [v['r2'] for v in per_archetype.values() if v.get('r2') is not None]

    if betas_prefix:
        prefix_range = max(betas_prefix) - min(betas_prefix)
        hazard_range = max(betas_hazard) - min(betas_hazard)
        mean_r2 = np.mean(r2s)

        print(f"\n  Cross-archetype slope variation:")
        print(f"    β_PREFIX range: {prefix_range:.4f} ({min(betas_prefix):.4f} to {max(betas_prefix):.4f})")
        print(f"    β_hazard range: {hazard_range:.4f} ({min(betas_hazard):.4f} to {max(betas_hazard):.4f})")
        print(f"    Mean within-archetype R²: {mean_r2:.4f}")

        # Slopes differ if range > 2× the mean absolute slope
        mean_abs_prefix = np.mean([abs(b) for b in betas_prefix])
        mean_abs_hazard = np.mean([abs(b) for b in betas_hazard])
        slopes_differ = (prefix_range > 2 * mean_abs_prefix) or (hazard_range > 2 * mean_abs_hazard)
        print(f"\n  Slopes qualitatively differ across archetypes: {'YES' if slopes_differ else 'NO'}")
    else:
        prefix_range, hazard_range, mean_r2, slopes_differ = None, None, None, False

    return {
        'per_archetype': {str(k): v for k, v in per_archetype.items()},
        'slopes_differ': slopes_differ,
        'mean_within_archetype_r2': round(float(mean_r2), 4) if mean_r2 is not None else None,
        'prefix_slope_range': round(float(prefix_range), 4) if prefix_range is not None else None,
        'hazard_slope_range': round(float(hazard_range), 4) if hazard_range is not None else None,
    }


# ── T5c: Geometric Bridge Feature ───────────────────────────────────

def run_t5c(tokens, folio_matrices, folio_sections, regime_map, archetype_data):
    """Test whether geometric bridge centroid position predicts AXM self-transition.

    Bridge density is constant (85/87 B MIDDLEs are bridges), but C1016.T8 showed
    bridge CENTROIDS in the 100D discrimination manifold cluster better than full
    centroids for archetype prediction. This test asks: does a scalar bridge
    geometric feature (first PC of bridge centroid) add to the variance decomposition?
    """
    print("\n" + "=" * 60)
    print("T5c: Geometric Bridge Feature")
    print("=" * 60)

    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    from sklearn.metrics import adjusted_rand_score

    archetype_labels = archetype_data.get('folio_labels', {})
    bridge_set = load_bridge_middles()

    # Load compatibility matrix and build spectral embedding (same as C1016.T7/T8)
    compat_path = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    if not compat_path.exists():
        print("  ERROR: Compatibility matrix not found. Skipping T5c.")
        return {'pass': False, 'error': 'compat_matrix_not_found'}

    M = np.load(compat_path)
    print(f"  Loaded compatibility matrix: {M.shape}")

    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}

    K_EMBED = 100
    eigenvalues, eigenvectors = np.linalg.eigh(M.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    evals = eigenvalues[:K_EMBED]
    evecs = eigenvectors[:, :K_EMBED]
    pos_evals = np.maximum(evals, 0)
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]
    print(f"  Embedding: {embedding.shape} ({K_EMBED}D)")

    # Build per-folio bridge centroid features
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    folio_bridge_centroids = {}
    folio_rows = []

    for folio, ftoks in folio_token_groups.items():
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue
        if folio not in archetype_labels:
            continue

        # Collect bridge MIDDLEs used in this folio that exist in manifold
        folio_bridge_mids = set()
        for t in ftoks:
            if t['is_bridge'] and t['middle'] in mid_to_idx:
                folio_bridge_mids.add(t['middle'])

        if not folio_bridge_mids:
            continue

        # Bridge centroid in manifold
        bridge_indices = [mid_to_idx[m] for m in folio_bridge_mids]
        bridge_centroid = embedding[bridge_indices].mean(axis=0)
        folio_bridge_centroids[folio] = bridge_centroid

        n_f = len(ftoks)
        prefix_counts = Counter(t['prefix'] for t in ftoks)
        prefix_total = sum(prefix_counts.values())
        prefix_probs = np.array(list(prefix_counts.values())) / prefix_total
        prefix_entropy = -sum(p * np.log2(p) for p in prefix_probs if p > 0)

        hazard_density = sum(1 for t in ftoks if t['is_hazard']) / n_f
        axm_self = float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']])

        folio_rows.append({
            'folio': folio,
            'axm_self': axm_self,
            'prefix_entropy': prefix_entropy,
            'hazard_density': hazard_density,
            'archetype': archetype_labels[folio],
            'regime': regime_map.get(folio, 'UNKNOWN'),
            'section': folio_sections.get(folio, 'UNKNOWN'),
        })

    folios_ordered = [r['folio'] for r in folio_rows]
    n = len(folios_ordered)
    print(f"  Folios with bridge centroids: {n}")

    if n < 20:
        print("  Too few folios. Skipping.")
        return {'pass': False, 'error': 'insufficient_data'}

    # Extract bridge centroid matrix and compute PCA
    X_centroids = np.array([folio_bridge_centroids[f] for f in folios_ordered])

    # PCA of bridge centroids: extract top components
    X_centered = X_centroids - X_centroids.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # First 3 PCs
    pc1 = X_centered @ Vt[0]
    pc2 = X_centered @ Vt[1]
    pc3 = X_centered @ Vt[2]
    var_explained = (S ** 2) / (S ** 2).sum()
    print(f"  Bridge centroid PCA: PC1={var_explained[0]:.1%}, PC2={var_explained[1]:.1%}, PC3={var_explained[2]:.1%}")

    # Also: centroid norm (distance from global mean)
    centroid_norms = np.linalg.norm(X_centered, axis=1)

    # Build dependent and predictor arrays
    y = np.array([r['axm_self'] for r in folio_rows])

    def standardize(x):
        return (x - x.mean()) / (x.std() + 1e-10)

    prefix_z = standardize(np.array([r['prefix_entropy'] for r in folio_rows]))
    hazard_z = standardize(np.array([r['hazard_density'] for r in folio_rows]))
    pc1_z = standardize(pc1)
    pc2_z = standardize(pc2)
    norm_z = standardize(centroid_norms)

    # Correlations: bridge geometric features vs AXM self
    rho_pc1, p_pc1 = stats.spearmanr(pc1, y)
    rho_pc2, p_pc2 = stats.spearmanr(pc2, y)
    rho_norm, p_norm = stats.spearmanr(centroid_norms, y)

    print(f"\n  Bridge geometric features vs AXM self-transition:")
    print(f"    PC1: rho={rho_pc1:.4f}, p={p_pc1:.6f}")
    print(f"    PC2: rho={rho_pc2:.4f}, p={p_pc2:.6f}")
    print(f"    Norm: rho={rho_norm:.4f}, p={p_norm:.6f}")

    # Build REGIME + section dummies (matching T5)
    regimes = [r['regime'] for r in folio_rows]
    sections = [r['section'] for r in folio_rows]
    unique_regimes = sorted(set(regimes))
    unique_sections = sorted(set(sections))

    regime_dummies = np.zeros((n, max(len(unique_regimes) - 1, 1)))
    for i, r_val in enumerate(regimes):
        r_idx = unique_regimes.index(r_val)
        if r_idx > 0 and regime_dummies.shape[1] >= r_idx:
            regime_dummies[i, r_idx - 1] = 1

    section_dummies = np.zeros((n, max(len(unique_sections) - 1, 1)))
    for i, s_val in enumerate(sections):
        s_idx = unique_sections.index(s_val)
        if s_idx > 0 and section_dummies.shape[1] >= s_idx:
            section_dummies[i, s_idx - 1] = 1

    # Model comparison: does bridge geometry add beyond PREFIX + hazard + controls?
    X_base_ctrl = np.column_stack([np.ones(n), regime_dummies, section_dummies, prefix_z, hazard_z])
    beta_ctrl = np.linalg.lstsq(X_base_ctrl, y, rcond=None)[0]
    ss_res_ctrl = np.sum((y - X_base_ctrl @ beta_ctrl) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2_ctrl = 1 - ss_res_ctrl / ss_tot

    # + bridge PC1
    X_geo1 = np.column_stack([X_base_ctrl, pc1_z])
    beta_geo1 = np.linalg.lstsq(X_geo1, y, rcond=None)[0]
    ss_res_geo1 = np.sum((y - X_geo1 @ beta_geo1) ** 2)
    r2_geo1 = 1 - ss_res_geo1 / ss_tot
    delta_r2_pc1 = r2_geo1 - r2_ctrl

    # + bridge PC1 + PC2
    X_geo2 = np.column_stack([X_base_ctrl, pc1_z, pc2_z])
    beta_geo2 = np.linalg.lstsq(X_geo2, y, rcond=None)[0]
    ss_res_geo2 = np.sum((y - X_geo2 @ beta_geo2) ** 2)
    r2_geo2 = 1 - ss_res_geo2 / ss_tot
    delta_r2_pc12 = r2_geo2 - r2_ctrl

    # + centroid norm
    X_norm = np.column_stack([X_base_ctrl, norm_z])
    beta_norm_model = np.linalg.lstsq(X_norm, y, rcond=None)[0]
    ss_res_norm = np.sum((y - X_norm @ beta_norm_model) ** 2)
    r2_norm = 1 - ss_res_norm / ss_tot
    delta_r2_norm = r2_norm - r2_ctrl

    # F-tests
    k_ctrl = X_base_ctrl.shape[1]

    def f_test(ss_red, ss_full_m, df_extra, n_obs, k_full_m):
        if ss_full_m <= 0 or df_extra <= 0:
            return 0, 1.0
        df_res = n_obs - k_full_m
        if df_res <= 0:
            return 0, 1.0
        f_stat = ((ss_red - ss_full_m) / df_extra) / (ss_full_m / df_res)
        p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
        return float(f_stat), float(p_val)

    f_pc1, p_f_pc1 = f_test(ss_res_ctrl, ss_res_geo1, 1, n, k_ctrl + 1)
    f_pc12, p_f_pc12 = f_test(ss_res_ctrl, ss_res_geo2, 2, n, k_ctrl + 2)
    f_norm_test, p_f_norm = f_test(ss_res_ctrl, ss_res_norm, 1, n, k_ctrl + 1)

    print(f"\n  Incremental R² from bridge geometry (beyond PREFIX + hazard + controls):")
    print(f"    Control model: R² = {r2_ctrl:.4f}")
    print(f"    + bridge PC1:  R² = {r2_geo1:.4f}  (ΔR² = {delta_r2_pc1:.4f}, F={f_pc1:.2f}, p={p_f_pc1:.6f})")
    print(f"    + bridge PC1+2: R² = {r2_geo2:.4f}  (ΔR² = {delta_r2_pc12:.4f}, F={f_pc12:.2f}, p={p_f_pc12:.6f})")
    print(f"    + centroid norm: R² = {r2_norm:.4f}  (ΔR² = {delta_r2_norm:.4f}, F={f_norm_test:.2f}, p={p_f_norm:.6f})")

    # Is bridge geometry load-bearing?
    geo_significant = p_f_pc1 < 0.05 or p_f_pc12 < 0.05 or p_f_norm < 0.05
    best_delta = max(delta_r2_pc1, delta_r2_pc12, delta_r2_norm)

    print(f"\n  Bridge geometry load-bearing: {'YES' if geo_significant else 'NO'} (best ΔR² = {best_delta:.4f})")

    return {
        'n_folios': n,
        'pca_variance_explained': [round(float(v), 4) for v in var_explained[:5]],
        'rho_pc1_axm': round(float(rho_pc1), 4),
        'p_pc1_axm': round(float(p_pc1), 6),
        'rho_pc2_axm': round(float(rho_pc2), 4),
        'p_pc2_axm': round(float(p_pc2), 6),
        'rho_norm_axm': round(float(rho_norm), 4),
        'p_norm_axm': round(float(p_norm), 6),
        'r2_control': round(float(r2_ctrl), 4),
        'r2_plus_pc1': round(float(r2_geo1), 4),
        'delta_r2_pc1': round(float(delta_r2_pc1), 4),
        'f_pc1': round(float(f_pc1), 2),
        'p_f_pc1': round(float(p_f_pc1), 6),
        'r2_plus_pc12': round(float(r2_geo2), 4),
        'delta_r2_pc12': round(float(delta_r2_pc12), 4),
        'f_pc12': round(float(f_pc12), 2),
        'p_f_pc12': round(float(p_f_pc12), 6),
        'r2_plus_norm': round(float(r2_norm), 4),
        'delta_r2_norm': round(float(delta_r2_norm), 4),
        'f_norm': round(float(f_norm_test), 2),
        'p_f_norm': round(float(p_f_norm), 6),
        'geo_significant': geo_significant,
        'best_delta_r2': round(float(best_delta), 4),
    }


# ── T6: Residual Characterization ───────────────────────────────────

def run_t6(tokens, folio_matrices, regime_map, folio_sections, archetype_data):
    """Characterize what the T5 residual correlates with.

    Tests: SUFFIX composition, HUB sub-role distribution, folio vocabulary
    properties. C1004 predicts SUFFIX should be uncorrelated (P7).
    """
    print("\n" + "=" * 60)
    print("T6: Residual Characterization")
    print("=" * 60)

    archetype_labels = archetype_data.get('folio_labels', {})

    # Rebuild T5's full model to get residuals
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    rows = []
    for folio, ftoks in folio_token_groups.items():
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue
        if folio not in archetype_labels:
            continue

        n_f = len(ftoks)
        prefix_counts = Counter(t['prefix'] for t in ftoks)
        prefix_total = sum(prefix_counts.values())
        prefix_probs = np.array(list(prefix_counts.values())) / prefix_total
        prefix_entropy = -sum(p * np.log2(p) for p in prefix_probs if p > 0)

        bridge_density = sum(1 for t in ftoks if t['is_bridge']) / n_f
        hazard_density = sum(1 for t in ftoks if t['is_hazard']) / n_f

        # SUFFIX composition entropy
        suffix_counts = Counter(t['suffix'] for t in ftoks if t['suffix'] is not None)
        if suffix_counts:
            suffix_total = sum(suffix_counts.values())
            suffix_probs_arr = np.array(list(suffix_counts.values())) / suffix_total
            suffix_entropy = -sum(p * np.log2(p) for p in suffix_probs_arr if p > 0)
        else:
            suffix_entropy = 0

        # HUB sub-role: fraction of tokens in gatekeeper classes
        gatekeeper_frac = sum(1 for t in ftoks if t['is_gatekeeper']) / n_f

        # Unique MIDDLE count (vocabulary diversity)
        unique_middles = len(set(t['middle'] for t in ftoks))
        middle_diversity = unique_middles / n_f

        # AXM self-transition
        axm_self = float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']])

        rows.append({
            'folio': folio,
            'axm_self': axm_self,
            'prefix_entropy': prefix_entropy,
            'bridge_density': bridge_density,
            'hazard_density': hazard_density,
            'suffix_entropy': suffix_entropy,
            'gatekeeper_frac': gatekeeper_frac,
            'middle_diversity': middle_diversity,
            'regime': regime_map.get(folio, 'UNKNOWN'),
            'section': folio_sections.get(folio, 'UNKNOWN'),
        })

    n = len(rows)
    y = np.array([r['axm_self'] for r in rows])

    def standardize(x):
        return (x - x.mean()) / (x.std() + 1e-10)

    prefix_z = standardize(np.array([r['prefix_entropy'] for r in rows]))
    hazard_z = standardize(np.array([r['hazard_density'] for r in rows]))

    # REGIME + section dummies
    regimes = [r['regime'] for r in rows]
    sections = [r['section'] for r in rows]
    unique_regimes = sorted(set(regimes))
    unique_sections = sorted(set(sections))

    regime_dummies = np.zeros((n, max(len(unique_regimes) - 1, 1)))
    for i, r in enumerate(regimes):
        r_idx = unique_regimes.index(r)
        if r_idx > 0 and regime_dummies.shape[1] >= r_idx:
            regime_dummies[i, r_idx - 1] = 1

    section_dummies = np.zeros((n, max(len(unique_sections) - 1, 1)))
    for i, s in enumerate(sections):
        s_idx = unique_sections.index(s)
        if s_idx > 0 and section_dummies.shape[1] >= s_idx:
            section_dummies[i, s_idx - 1] = 1

    # Full model from T5: REGIME + section + PREFIX + hazard + gatekeeper
    gatekeeper_z = standardize(np.array([r['gatekeeper_frac'] for r in rows]))
    X_full = np.column_stack([np.ones(n), regime_dummies, section_dummies,
                               prefix_z, hazard_z, gatekeeper_z])
    beta = np.linalg.lstsq(X_full, y, rcond=None)[0]
    residuals = y - X_full @ beta

    print(f"\n  Residual std: {residuals.std():.4f}")
    print(f"  Residual range: [{residuals.min():.4f}, {residuals.max():.4f}]")

    # Correlate residuals with candidate variables
    candidates = {
        'suffix_entropy': np.array([r['suffix_entropy'] for r in rows]),
        'gatekeeper_frac': np.array([r['gatekeeper_frac'] for r in rows]),
        'middle_diversity': np.array([r['middle_diversity'] for r in rows]),
    }

    print(f"\n  Residual correlations:")
    residual_correlations = {}
    for name, values in candidates.items():
        if values.std() < 1e-10:
            print(f"    {name}: constant, skipped")
            continue
        rho, p = stats.spearmanr(residuals, values)
        print(f"    {name}: rho={rho:.4f}, p={p:.6f}")
        residual_correlations[name] = {
            'rho': round(float(rho), 4),
            'p_value': round(float(p), 6),
        }

    # P7: SUFFIX entropy uncorrelated with residual (p > 0.05)
    suffix_result = residual_correlations.get('suffix_entropy', {})
    p7_pass = suffix_result.get('p_value', 1.0) > 0.05
    print(f"\n  P7: SUFFIX entropy uncorrelated with residual (p > 0.05)?")
    print(f"    p = {suffix_result.get('p_value', 'N/A')}")
    print(f"  Verdict: {'PASS (C1004 confirmed)' if p7_pass else 'FAIL'}")

    # Folio-identity test: is residual clustered by archetype?
    archetype_residuals = defaultdict(list)
    for i, r in enumerate(rows):
        arch = archetype_labels.get(r['folio'])
        if arch is not None:
            archetype_residuals[arch].append(residuals[i])

    if len(archetype_residuals) >= 2:
        f_arch, p_arch = stats.f_oneway(*[archetype_residuals[k] for k in sorted(archetype_residuals.keys())])
        print(f"\n  Residual ~ archetype: F={f_arch:.2f}, p={p_arch:.6f}")
        print(f"  (If significant: archetypes capture variance beyond the linear model)")
    else:
        f_arch, p_arch = None, None

    return {
        'n_folios': n,
        'residual_std': round(float(residuals.std()), 4),
        'residual_correlations': residual_correlations,
        'residual_vs_archetype_f': round(float(f_arch), 2) if f_arch is not None else None,
        'residual_vs_archetype_p': round(float(p_arch), 6) if p_arch is not None else None,
        'pass_p7_suffix_uncorrelated': p7_pass,
    }


# ── T7: Synthesis ────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5, t5b, t5c, t6):
    """Generate synthesis and verdict from all tests."""
    print("\n" + "=" * 60)
    print("T7: SYNTHESIS")
    print("=" * 60)

    predictions = {
        'P1_middle_conditioned_routing': {
            'description': 'MIDDLE-conditioned PREFIX routing significant (p<0.05)',
            'result': t1.get('pass', False),
            'value': f"z={t1.get('z_score', '?')}, p={t1.get('p_value', '?')}",
        },
        'P2_survives_positional': {
            'description': 'PREFIX routing survives positional shuffling (p<0.05)',
            'result': t2.get('pass', False),
            'value': f"z={t2.get('z_score', '?')}, p={t2.get('p_value', '?')}",
        },
        'P3_regime_variation': {
            'description': 'PREFIX routing varies by REGIME (range ratio > 1.5)',
            'result': t3.get('pass', False),
            'value': f"ratio={t3.get('range_ratio', '?')}",
        },
        'P4_hazard_differentiates': {
            'description': 'Hazard density differentiates archetypes (ANOVA p<0.05)',
            'result': t4.get('pass', False),
            'value': f"eta2={t4.get('eta2_hazard_archetype', '?')}, p={t4.get('anova_p_hazard', '?')}",
        },
        'P5_weak_interaction': {
            'description': 'PREFIX × bridge interaction weak (ΔR² < 0.05)',
            'result': t5.get('pass_p5_weak_interaction', False),
            'value': f"ΔR²={t5.get('delta_r2_interaction', '?')}",
        },
        'P6_explained_variance': {
            'description': 'Full model explains >40% of AXM self variance',
            'result': t5.get('pass_p6_explained_variance', False),
            'value': f"R²={t5.get('r2_full', '?')}",
        },
        'P7_suffix_uncorrelated': {
            'description': 'SUFFIX entropy uncorrelated with residual (p>0.05)',
            'result': t6.get('pass_p7_suffix_uncorrelated', False),
            'value': f"p={t6.get('residual_correlations', {}).get('suffix_entropy', {}).get('p_value', '?')}",
        },
    }

    n_pass = sum(1 for p in predictions.values() if p['result'])
    n_total = len(predictions)

    print(f"\n  Pre-registered predictions: {n_pass}/{n_total} PASS")
    for name, pred in predictions.items():
        status = "PASS" if pred['result'] else "FAIL"
        print(f"    {name}: {status} — {pred['value']}")

    # Overall verdict
    if n_pass >= 5:
        verdict = "DYNAMICS_DECOMPOSED"
        verdict_text = "Macro-state dynamics are jointly explained by PREFIX routing and hazard density, with weak interaction and no SUFFIX contribution. Bridge operates geometrically (C1016.T8), not densimetrically."
    elif n_pass >= 3:
        verdict = "PARTIAL_DECOMPOSITION"
        verdict_text = "Some variance decomposition achieved but key predictions failed."
    else:
        verdict = "DECOMPOSITION_FAILED"
        verdict_text = "Proposed variance decomposition does not hold."

    print(f"\n  Verdict: {verdict}")
    print(f"  {verdict_text}")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
        'verdict_text': verdict_text,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    start = time.time()

    print("Phase 340: MACRO_DYNAMICS_VARIANCE_DECOMPOSITION")
    print("=" * 60)
    print("\nLoading data...")

    token_to_class = load_token_to_class()
    regime_map = load_regime_assignments()
    archetype_data = load_folio_archetypes()

    print(f"  Token→class entries: {len(token_to_class)}")
    print(f"  REGIME assignments: {len(regime_map)}")
    print(f"  Archetypes: best_k={archetype_data['best_k']}, "
          f"folios={len(archetype_data.get('folio_labels', {}))}")

    tokens, folio_sections = build_corpus_data(token_to_class)
    folio_matrices = build_folio_matrices(tokens)

    sufficient = sum(1 for d in folio_matrices.values() if d['n_transitions'] >= MIN_TRANSITIONS)
    print(f"  Sufficient folios (>={MIN_TRANSITIONS} transitions): {sufficient}")

    # Run tests
    t1 = run_t1(tokens)
    t2 = run_t2(tokens, t1)
    t3 = run_t3(tokens, regime_map)
    t4 = run_t4(tokens, folio_matrices, regime_map, archetype_data)
    t5 = run_t5(tokens, folio_matrices, regime_map, folio_sections, archetype_data)
    t5b = run_t5b(tokens, folio_matrices, regime_map, folio_sections, archetype_data)
    t5c = run_t5c(tokens, folio_matrices, folio_sections, regime_map, archetype_data)
    t6 = run_t6(tokens, folio_matrices, regime_map, folio_sections, archetype_data)
    t7 = synthesize(t1, t2, t3, t4, t5, t5b, t5c, t6)

    # Save results
    results = {
        'phase_number': 340,
        'phase_name': 'MACRO_DYNAMICS_VARIANCE_DECOMPOSITION',
        'question': 'How much of macro-state dynamics is explained by PREFIX routing vs bridge density vs their interaction?',
        'n_tokens': len(tokens),
        't1_middle_conditioned_routing': t1,
        't2_positional_null': t2,
        't3_regime_stratified': t3,
        't4_bridge_archetype': {k: v for k, v in t4.items() if k != 'folio_features'},
        't4_folio_features': t4.get('folio_features', {}),
        't5_variance_decomposition': t5,
        't5b_archetype_stratified': t5b,
        't5c_geometric_bridge': t5c,
        't6_residual_characterization': t6,
        't7_synthesis': t7,
        'duration_seconds': round(time.time() - start, 1),
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'macro_dynamics_decomposition.json'
    # Remove non-serializable items from t1
    if 'per_middle' in results['t1_middle_conditioned_routing']:
        # Ensure all values are JSON-serializable
        for m in results['t1_middle_conditioned_routing']['per_middle']:
            pass  # Already using round() in construction

    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n\nResults saved to: {out_path}")
    print(f"Total time: {time.time() - start:.1f}s")

    return results


if __name__ == '__main__':
    main()
