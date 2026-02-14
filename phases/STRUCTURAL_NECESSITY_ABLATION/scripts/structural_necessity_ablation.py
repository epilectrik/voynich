#!/usr/bin/env python3
"""
Phase 346: STRUCTURAL_NECESSITY_ABLATION
=========================================
Counterfactual surgery on 4 key structural components to determine
which are load-bearing vs decorative for the 6-state macro-automaton.

Tests:
  T1:  Merge FL_HAZ + FL_SAFE into single FL state
  T2:  Reassign gatekeeper classes to AXM bulk
  T3a: Shuffle PREFIX within macro-state
  T3b: Shuffle PREFIX within position quintile
  T3c: Shuffle PREFIX globally
  T4:  Merge all 4 REGIMEs into one pool

Depends on: C1010, C1015, C978, C586, C1007, C109, C979
"""

import json
import sys
import copy
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

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

STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}

GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}

N_NULL = 100  # Null control permutations


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with class, state, prefix, middle, folio, line, position."""
    print("Loading data...")

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    # Load forbidden pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_pairs.add((t['source'], t['target']))
    print(f"  {len(forbidden_pairs)} forbidden MIDDLE pairs loaded")

    # Load REGIME assignments
    with open(PROJECT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json',
              encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_regime = {f: v['cluster_id'] for f, v in regime_data['assignments'].items()}

    morph = Morphology()

    tokens = []
    line_lengths = defaultdict(int)  # (folio, line) → count for position calc

    # First pass: count tokens per line for position quintiles
    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        if token.word not in token_to_class:
            continue
        line_lengths[(token.folio, token.line)] += 1

    # Second pass: build full token stream
    line_counters = defaultdict(int)
    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        cls = token_to_class.get(token.word)
        if cls is None:
            continue
        state = CLASS_TO_STATE.get(cls)
        if state is None:
            continue

        m = morph.extract(token.word)
        prefix = m.prefix if m else None
        middle = m.middle if m else token.word

        key = (token.folio, token.line)
        pos_in_line = line_counters[key]
        line_counters[key] += 1
        total_in_line = line_lengths[key]
        pos_frac = pos_in_line / max(total_in_line - 1, 1) if total_in_line > 1 else 0.5
        pos_quintile = min(int(pos_frac * 5), 4)  # 0-4

        tokens.append({
            'word': token.word,
            'cls': cls,
            'state': state,
            'prefix': prefix,
            'middle': middle,
            'folio': token.folio,
            'line': token.line,
            'pos_quintile': pos_quintile,
            'regime': folio_regime.get(token.folio, 'UNKNOWN'),
        })

    print(f"  {len(tokens)} classified tokens loaded")
    return tokens, forbidden_pairs


# ── Shared Ablation Engine ───────────────────────────────────────────

def compute_metrics(tokens, states=None):
    """Compute all metrics from a token stream.

    Args:
        tokens: list of token dicts with 'state' field
        states: ordered list of state labels (default: STATE_ORDER)
    Returns:
        dict of metrics
    """
    if states is None:
        states = STATE_ORDER
    n_states = len(states)
    s_idx = {s: i for i, s in enumerate(states)}

    # Build transition matrix
    trans = np.zeros((n_states, n_states))
    for i in range(len(tokens) - 1):
        # Only count within-line transitions
        if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
            continue
        s_from = tokens[i]['state']
        s_to = tokens[i+1]['state']
        if s_from in s_idx and s_to in s_idx:
            trans[s_idx[s_from], s_idx[s_to]] += 1

    # Normalize to row-stochastic
    row_sums = trans.sum(axis=1)
    trans_norm = np.zeros_like(trans)
    for i in range(n_states):
        if row_sums[i] > 0:
            trans_norm[i] = trans[i] / row_sums[i]

    # Spectral gap
    eigenvalues = np.sort(np.abs(np.linalg.eigvals(trans_norm)))[::-1]
    spectral_gap = 1.0 - eigenvalues[1] if len(eigenvalues) > 1 else 1.0

    # Stationary distribution (left eigenvector)
    try:
        evals, evecs = np.linalg.eig(trans_norm.T)
        idx = np.argmin(np.abs(evals - 1.0))
        stat = np.real(evecs[:, idx])
        stat = stat / stat.sum()
    except:
        stat = np.ones(n_states) / n_states

    # Forbidden transition count (MIDDLE-level, not state-level)
    forbidden_count = 0
    for i in range(len(tokens) - 1):
        if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
            continue
        pair = (tokens[i]['middle'], tokens[i+1]['middle'])
        if pair in _forbidden_pairs:
            forbidden_count += 1

    # AXM dwell statistics
    axm_label = 'AXM' if 'AXM' in s_idx else None
    dwell_lengths = []
    if axm_label:
        current_run = 0
        prev_folio_line = None
        for t in tokens:
            fl = (t['folio'], t['line'])
            if fl != prev_folio_line:
                if current_run > 0:
                    dwell_lengths.append(current_run)
                current_run = 0
                prev_folio_line = fl
            if t['state'] == axm_label:
                current_run += 1
            else:
                if current_run > 0:
                    dwell_lengths.append(current_run)
                current_run = 0
        if current_run > 0:
            dwell_lengths.append(current_run)

    mean_dwell = float(np.mean(dwell_lengths)) if dwell_lengths else 0
    median_dwell = float(np.median(dwell_lengths)) if dwell_lengths else 0

    # AXM exit entropy and destination vector
    if axm_label and axm_label in s_idx:
        axm_i = s_idx[axm_label]
        exit_row = trans[axm_i].copy()
        exit_row[axm_i] = 0  # Exclude self-transition
        exit_total = exit_row.sum()
        if exit_total > 0:
            exit_dist = exit_row / exit_total
            exit_entropy = float(scipy_entropy(exit_dist[exit_dist > 0], base=2))
        else:
            exit_dist = np.zeros(n_states)
            exit_entropy = 0.0
        exit_dest = {states[j]: float(exit_dist[j]) for j in range(n_states) if j != axm_i}
    else:
        exit_entropy = 0.0
        exit_dest = {}

    return {
        'spectral_gap': float(spectral_gap),
        'eigenvalues': [float(e) for e in eigenvalues[:3]],
        'stationary': {states[i]: float(stat[i]) for i in range(n_states)},
        'forbidden_count': forbidden_count,
        'mean_dwell': mean_dwell,
        'median_dwell': median_dwell,
        'n_dwell_runs': len(dwell_lengths),
        'exit_entropy': exit_entropy,
        'exit_destinations': exit_dest,
        'n_transitions': int(trans.sum()),
    }


# ── T1: Merge FL Split ──────────────────────────────────────────────

def ablation_t1_fl_merge(tokens):
    """Merge FL_HAZ and FL_SAFE into single FL state."""
    merged = []
    for t in tokens:
        t2 = t.copy()
        if t2['state'] in ('FL_HAZ', 'FL_SAFE'):
            t2['state'] = 'FL'
        merged.append(t2)
    return merged


def run_t1(tokens, baseline):
    """T1: Merge FL split."""
    print("\n" + "=" * 60)
    print("T1: Merge FL_HAZ + FL_SAFE → single FL")
    print("=" * 60)

    merged_tokens = ablation_t1_fl_merge(tokens)
    merged_states = ['AXM', 'AXm', 'FQ', 'CC', 'FL']
    metrics = compute_metrics(merged_tokens, states=merged_states)

    print(f"  Baseline spectral gap: {baseline['spectral_gap']:.4f}")
    print(f"  Merged spectral gap:   {metrics['spectral_gap']:.4f}")
    delta_pct = (metrics['spectral_gap'] - baseline['spectral_gap']) / baseline['spectral_gap'] * 100
    print(f"  Delta: {delta_pct:+.2f}%")

    # Null control: merge two random non-FL states
    null_gaps = []
    mergeable = [('AXm', 'CC'), ('AXm', 'FQ'), ('CC', 'FQ')]
    for _ in range(N_NULL):
        pair = mergeable[np.random.randint(len(mergeable))]
        merged_label = pair[0] + '+' + pair[1]
        null_tokens = []
        for t in tokens:
            t2 = t.copy()
            if t2['state'] in pair:
                t2['state'] = merged_label
            null_tokens.append(t2)
        null_states = [s for s in STATE_ORDER if s not in pair] + [merged_label]
        nm = compute_metrics(null_tokens, states=null_states)
        null_gaps.append(nm['spectral_gap'])

    null_mean = float(np.mean(null_gaps))
    null_std = float(np.std(null_gaps))
    z = (metrics['spectral_gap'] - null_mean) / max(null_std, 1e-10)

    print(f"  Null control: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"  z-score vs null: {z:.2f}")

    load_bearing = abs(delta_pct) > 20
    verdict = "LOAD_BEARING" if load_bearing else ("PARTIAL" if abs(delta_pct) > 5 else "DECORATIVE")
    print(f"  Verdict: {verdict}")

    return {
        'spectral_gap': metrics['spectral_gap'],
        'delta_pct': float(delta_pct),
        'forbidden_count': metrics['forbidden_count'],
        'forbidden_delta': metrics['forbidden_count'] - baseline['forbidden_count'],
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': float(z),
        'stationary': metrics['stationary'],
        'verdict': verdict,
    }


# ── T2: Reassign Gatekeepers ────────────────────────────────────────

def run_t2(tokens, baseline):
    """T2: Test whether gatekeepers cause or merely mark AXM exits."""
    print("\n" + "=" * 60)
    print("T2: Reassign Gatekeeper Classes to AXM Bulk")
    print("=" * 60)

    # Measure exit statistics WITH gatekeeper awareness
    # vs treating gatekeepers as generic AXM interior

    # Approach: measure what happens when we look at AXM exit tokens
    # Are gatekeeper classes disproportionately the LAST token before exit?

    # Compute exit-boundary class distribution (real)
    exit_classes_real = Counter()
    non_exit_classes_real = Counter()
    for i in range(len(tokens) - 1):
        if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
            continue
        if tokens[i]['state'] == 'AXM' and tokens[i+1]['state'] != 'AXM':
            exit_classes_real[tokens[i]['cls']] += 1
        elif tokens[i]['state'] == 'AXM' and tokens[i+1]['state'] == 'AXM':
            non_exit_classes_real[tokens[i]['cls']] += 1

    # Gatekeeper fraction at exits vs interior
    gk_at_exit = sum(exit_classes_real[c] for c in GATEKEEPER_CLASSES)
    total_exits = sum(exit_classes_real.values())
    gk_at_interior = sum(non_exit_classes_real[c] for c in GATEKEEPER_CLASSES)
    total_interior = sum(non_exit_classes_real.values())

    gk_exit_rate = gk_at_exit / max(total_exits, 1)
    gk_interior_rate = gk_at_interior / max(total_interior, 1)
    enrichment = gk_exit_rate / max(gk_interior_rate, 1e-10)

    print(f"  Gatekeeper exit rate: {gk_at_exit}/{total_exits} = {gk_exit_rate:.3f}")
    print(f"  Gatekeeper interior rate: {gk_at_interior}/{total_interior} = {gk_interior_rate:.3f}")
    print(f"  Exit enrichment: {enrichment:.2f}x")

    # Key test: Do exit DESTINATIONS differ when last-AXM is gatekeeper vs non-gatekeeper?
    gk_exit_dest = Counter()
    non_gk_exit_dest = Counter()
    for i in range(len(tokens) - 1):
        if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
            continue
        if tokens[i]['state'] == 'AXM' and tokens[i+1]['state'] != 'AXM':
            dest = tokens[i+1]['state']
            if tokens[i]['cls'] in GATEKEEPER_CLASSES:
                gk_exit_dest[dest] += 1
            else:
                non_gk_exit_dest[dest] += 1

    print(f"\n  Exit destinations when last-AXM is gatekeeper:")
    gk_total = sum(gk_exit_dest.values())
    non_gk_total = sum(non_gk_exit_dest.values())
    print(f"  {'State':<10} {'Gatekeeper':>10} {'Non-GK':>10} {'Delta':>8}")
    print(f"  {'-'*40}")

    gk_vec = []
    non_gk_vec = []
    for s in STATE_ORDER:
        if s == 'AXM':
            continue
        gk_frac = gk_exit_dest[s] / max(gk_total, 1)
        non_gk_frac = non_gk_exit_dest[s] / max(non_gk_total, 1)
        gk_vec.append(gk_frac)
        non_gk_vec.append(non_gk_frac)
        delta = gk_frac - non_gk_frac
        print(f"  {s:<10} {gk_frac:>9.3f}  {non_gk_frac:>9.3f}  {delta:>+7.3f}")

    # Jensen-Shannon divergence between gatekeeper and non-gatekeeper exit distributions
    gk_arr = np.array(gk_vec) + 1e-10
    non_gk_arr = np.array(non_gk_vec) + 1e-10
    gk_arr = gk_arr / gk_arr.sum()
    non_gk_arr = non_gk_arr / non_gk_arr.sum()
    m = 0.5 * (gk_arr + non_gk_arr)
    jsd = float(0.5 * scipy_entropy(gk_arr, m, base=2) + 0.5 * scipy_entropy(non_gk_arr, m, base=2))

    print(f"\n  Jensen-Shannon divergence: {jsd:.4f}")

    # Null control: pick 5 random AXM classes as "pseudo-gatekeepers"
    all_axm_classes = list(MACRO_STATE_PARTITION['AXM'] - GATEKEEPER_CLASSES)
    null_jsds = []
    for _ in range(N_NULL):
        pseudo_gk = set(np.random.choice(all_axm_classes, size=5, replace=False))
        p_gk_dest = Counter()
        p_non_gk_dest = Counter()
        for i in range(len(tokens) - 1):
            if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
                continue
            if tokens[i]['state'] == 'AXM' and tokens[i+1]['state'] != 'AXM':
                dest = tokens[i+1]['state']
                if tokens[i]['cls'] in pseudo_gk:
                    p_gk_dest[dest] += 1
                else:
                    p_non_gk_dest[dest] += 1
        p_gk_total = sum(p_gk_dest.values())
        p_non_gk_total = sum(p_non_gk_dest.values())
        if p_gk_total < 5 or p_non_gk_total < 5:
            continue
        pv1 = np.array([p_gk_dest[s] / p_gk_total for s in STATE_ORDER if s != 'AXM']) + 1e-10
        pv2 = np.array([p_non_gk_dest[s] / p_non_gk_total for s in STATE_ORDER if s != 'AXM']) + 1e-10
        pv1 /= pv1.sum()
        pv2 /= pv2.sum()
        pm = 0.5 * (pv1 + pv2)
        null_jsds.append(float(0.5 * scipy_entropy(pv1, pm, base=2) + 0.5 * scipy_entropy(pv2, pm, base=2)))

    null_mean = float(np.mean(null_jsds)) if null_jsds else 0
    null_std = float(np.std(null_jsds)) if null_jsds else 0
    z = (jsd - null_mean) / max(null_std, 1e-10)

    print(f"  Null JSD: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"  z-score: {z:.2f}")

    load_bearing = jsd > 0.05 or z > 2.0
    verdict = "LOAD_BEARING" if load_bearing else ("PARTIAL" if jsd > 0.02 or z > 1.5 else "DECORATIVE")
    print(f"  Verdict: {verdict}")

    return {
        'gk_exit_rate': float(gk_exit_rate),
        'gk_interior_rate': float(gk_interior_rate),
        'enrichment': float(enrichment),
        'gk_exits': gk_total,
        'non_gk_exits': non_gk_total,
        'gk_exit_destinations': {s: gk_exit_dest[s] / max(gk_total, 1) for s in STATE_ORDER if s != 'AXM'},
        'non_gk_exit_destinations': {s: non_gk_exit_dest[s] / max(non_gk_total, 1) for s in STATE_ORDER if s != 'AXM'},
        'jsd': jsd,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': float(z),
        'verdict': verdict,
    }


# ── T3: PREFIX Shuffle ───────────────────────────────────────────────

def build_prefix_state_distribution(tokens):
    """Build P(state | prefix) from the real data for state reassignment."""
    prefix_state_counts = defaultdict(Counter)
    for t in tokens:
        pfx = t['prefix'] if t['prefix'] else '(bare)'
        prefix_state_counts[pfx][t['state']] += 1

    # Convert to arrays for efficient sampling
    prefix_state_sampler = {}
    for pfx, counts in prefix_state_counts.items():
        states = list(counts.keys())
        probs = np.array([counts[s] for s in states], dtype=float)
        probs /= probs.sum()
        prefix_state_sampler[pfx] = (states, probs)

    return prefix_state_sampler


def shuffle_prefix(tokens, mode='global', prefix_state_sampler=None):
    """Shuffle PREFIX assignments and reassign state via P(state|new_prefix).

    After shuffling PREFIX, each token's state is resampled from the
    conditional distribution P(state | new_prefix), built from the original
    data. This properly tests whether PREFIX→state routing is load-bearing.

    Modes:
      'within_state': shuffle within same macro-state (state stays same by construction)
      'within_position': shuffle within same position quintile, reassign state
      'global': shuffle globally, reassign state
    """
    shuffled = [t.copy() for t in tokens]

    if mode == 'global':
        # Collect all prefixes, shuffle, reassign
        prefixes = [t['prefix'] for t in shuffled]
        np.random.shuffle(prefixes)
        for i, t in enumerate(shuffled):
            t['prefix'] = prefixes[i]
            # Reassign state based on new prefix
            if prefix_state_sampler:
                pfx_key = prefixes[i] if prefixes[i] else '(bare)'
                if pfx_key in prefix_state_sampler:
                    states, probs = prefix_state_sampler[pfx_key]
                    t['state'] = np.random.choice(states, p=probs)

    elif mode == 'within_state':
        # Group by macro-state, shuffle prefixes within each group
        # State reassignment is NOT applied here: shuffling within state
        # preserves the state by construction (all source prefixes come from
        # the same state pool). This tests within-state routing only.
        by_state = defaultdict(list)
        for i, t in enumerate(shuffled):
            by_state[t['state']].append(i)
        for state, indices in by_state.items():
            prefixes = [shuffled[i]['prefix'] for i in indices]
            np.random.shuffle(prefixes)
            for j, idx in enumerate(indices):
                shuffled[idx]['prefix'] = prefixes[j]

    elif mode == 'within_position':
        # Group by position quintile, shuffle within, reassign state
        by_pos = defaultdict(list)
        for i, t in enumerate(shuffled):
            by_pos[t['pos_quintile']].append(i)
        for pos, indices in by_pos.items():
            prefixes = [shuffled[i]['prefix'] for i in indices]
            np.random.shuffle(prefixes)
            for j, idx in enumerate(indices):
                shuffled[idx]['prefix'] = prefixes[j]
                # Reassign state based on new prefix
                if prefix_state_sampler:
                    pfx_key = prefixes[j] if prefixes[j] else '(bare)'
                    if pfx_key in prefix_state_sampler:
                        states, probs = prefix_state_sampler[pfx_key]
                        shuffled[idx]['state'] = np.random.choice(states, p=probs)

    return shuffled


def compute_prefix_entropy_reduction(tokens):
    """Compute PREFIX → macro-state entropy reduction (C1012 metric)."""
    # Marginal state distribution
    state_counts = Counter(t['state'] for t in tokens)
    total = sum(state_counts.values())
    marginal_probs = [state_counts.get(s, 0) / total for s in STATE_ORDER]
    h_marginal = scipy_entropy([p for p in marginal_probs if p > 0], base=2)

    # Conditional: H(state | prefix)
    by_prefix = defaultdict(Counter)
    for t in tokens:
        pfx = t['prefix'] or '(bare)'
        by_prefix[pfx][t['state']] += 1

    h_conditional = 0.0
    for pfx, counts in by_prefix.items():
        pfx_total = sum(counts.values())
        pfx_weight = pfx_total / total
        probs = [counts.get(s, 0) / pfx_total for s in STATE_ORDER]
        h_conditional += pfx_weight * scipy_entropy([p for p in probs if p > 0], base=2)

    reduction = (h_marginal - h_conditional) / max(h_marginal, 1e-10)
    return float(reduction), float(h_marginal), float(h_conditional)


def run_t3(tokens, baseline):
    """T3: PREFIX shuffle in 3 variants.

    After shuffling PREFIX, states are REASSIGNED via P(state|new_prefix)
    to properly test whether PREFIX→state routing is load-bearing.
    Without reassignment, spectral gap is tautologically invariant because
    state is determined by class (which doesn't change when PREFIX shuffles).
    """
    print("\n" + "=" * 60)
    print("T3: PREFIX Shuffle (3 variants, with state reassignment)")
    print("=" * 60)

    # Build prefix→state conditional distribution from real data
    prefix_state_sampler = build_prefix_state_distribution(tokens)
    print(f"  Prefix→state sampler: {len(prefix_state_sampler)} prefixes")

    # Baseline entropy reduction
    base_reduction, base_h_marginal, base_h_cond = compute_prefix_entropy_reduction(tokens)
    print(f"  Baseline PREFIX entropy reduction: {base_reduction:.3f} ({base_reduction*100:.1f}%)")

    results = {}
    n_runs = 20  # Average over multiple shuffles for stability

    for mode, label in [('within_state', 't3a'), ('within_position', 't3b'), ('global', 't3c')]:
        print(f"\n  --- {label}: shuffle PREFIX {mode} ---")

        gaps = []
        reductions = []
        forbidden_counts = []
        exit_entropies = []

        for _ in range(n_runs):
            shuffled = shuffle_prefix(tokens, mode=mode,
                                       prefix_state_sampler=prefix_state_sampler)
            m = compute_metrics(shuffled)
            gaps.append(m['spectral_gap'])
            forbidden_counts.append(m['forbidden_count'])
            exit_entropies.append(m['exit_entropy'])
            r, _, _ = compute_prefix_entropy_reduction(shuffled)
            reductions.append(r)

        mean_gap = float(np.mean(gaps))
        std_gap = float(np.std(gaps))
        mean_red = float(np.mean(reductions))
        mean_forb = float(np.mean(forbidden_counts))
        mean_exit_ent = float(np.mean(exit_entropies))

        gap_delta = (mean_gap - baseline['spectral_gap']) / baseline['spectral_gap'] * 100
        red_delta = (mean_red - base_reduction) / max(base_reduction, 1e-10) * 100

        # Non-random structure = 1 - spectral_gap (how far from fully-random mixing)
        # Baseline: 1 - 0.894 = 0.106 (10.6% non-random)
        # If shuffle INCREASES spectral gap, it DESTROYS non-random structure
        baseline_structure = 1.0 - baseline['spectral_gap']
        shuffled_structure = 1.0 - mean_gap
        structure_loss_pct = (baseline_structure - shuffled_structure) / max(baseline_structure, 1e-10) * 100

        print(f"  Spectral gap: {mean_gap:.4f} ± {std_gap:.4f} ({gap_delta:+.1f}%)")
        print(f"  Non-random structure: {shuffled_structure:.4f} (baseline: {baseline_structure:.4f})")
        print(f"  Structure loss: {structure_loss_pct:.1f}%")
        print(f"  Forbidden count: {mean_forb:.1f} (baseline: {baseline['forbidden_count']})")
        print(f"  Exit entropy: {mean_exit_ent:.3f} (baseline: {baseline['exit_entropy']:.3f})")

        # NOTE: Entropy reduction is tautological for T3b/T3c because
        # state was resampled from P(state|new_prefix) — measuring
        # P(state|prefix) back gives the same distribution.
        if label == 't3a':
            print(f"  Entropy reduction: {mean_red:.3f} ({red_delta:+.1f}%)")

        # Verdict based on structure loss (not raw spectral gap direction)
        # Structure loss > 50% = LOAD_BEARING, 20-50% = PARTIAL, <20% = DECORATIVE
        if label == 't3c':
            verdict = "LOAD_BEARING" if structure_loss_pct > 50 else ("PARTIAL" if structure_loss_pct > 20 else "DECORATIVE")
        elif label == 't3b':
            verdict = "LOAD_BEARING" if structure_loss_pct > 40 else ("PARTIAL" if structure_loss_pct > 15 else "DECORATIVE")
        else:  # t3a
            verdict = "LOAD_BEARING" if structure_loss_pct > 25 else ("PARTIAL" if structure_loss_pct > 10 else "DECORATIVE")

        print(f"  Verdict: {verdict}")

        results[label] = {
            'mode': mode,
            'spectral_gap': mean_gap,
            'spectral_gap_std': std_gap,
            'gap_delta_pct': float(gap_delta),
            'non_random_structure': float(shuffled_structure),
            'baseline_structure': float(baseline_structure),
            'structure_loss_pct': float(structure_loss_pct),
            'entropy_reduction': mean_red,
            'reduction_delta_pct': float(red_delta),
            'forbidden_count': mean_forb,
            'exit_entropy': mean_exit_ent,
            'n_runs': n_runs,
            'verdict': verdict,
        }

    # Summary: is hierarchy T3a > T3b > T3c?
    hierarchy = (results['t3a']['spectral_gap'] > results['t3b']['spectral_gap'] > results['t3c']['spectral_gap'])
    results['hierarchy_monotonic'] = hierarchy
    results['baseline_entropy_reduction'] = base_reduction

    return results


# ── T4: Merge REGIMEs ────────────────────────────────────────────────

def run_t4(tokens, baseline):
    """T4: Merge all 4 REGIMEs — test whether REGIME is decorative at macro level."""
    print("\n" + "=" * 60)
    print("T4: Merge All REGIMEs")
    print("=" * 60)

    # Compute per-REGIME transition matrices for comparison
    regimes = set(t['regime'] for t in tokens if t['regime'] != 'UNKNOWN')
    print(f"  REGIMEs found: {sorted(regimes)}")

    regime_gaps = {}
    for regime in sorted(regimes):
        regime_tokens = [t for t in tokens if t['regime'] == regime]
        if len(regime_tokens) < 100:
            continue
        rm = compute_metrics(regime_tokens)
        regime_gaps[regime] = rm['spectral_gap']
        print(f"  {regime}: n={len(regime_tokens)}, spectral_gap={rm['spectral_gap']:.4f}")

    # Pooled (all REGIMEs merged) = baseline
    # The question is: does pooling CHANGE anything?
    # Compare per-REGIME spectral gaps to pooled
    pooled_gap = baseline['spectral_gap']
    regime_gap_vals = list(regime_gaps.values())
    mean_regime_gap = float(np.mean(regime_gap_vals)) if regime_gap_vals else 0

    print(f"\n  Pooled spectral gap: {pooled_gap:.4f}")
    print(f"  Mean per-REGIME spectral gap: {mean_regime_gap:.4f}")
    gap_diff = abs(pooled_gap - mean_regime_gap)
    gap_diff_pct = gap_diff / pooled_gap * 100

    print(f"  Difference: {gap_diff:.4f} ({gap_diff_pct:.1f}%)")

    # Also compute JSD between per-REGIME transition matrices and pooled
    # Build pooled transition matrix
    pooled_trans = np.zeros((6, 6))
    for i in range(len(tokens) - 1):
        if tokens[i]['folio'] != tokens[i+1]['folio'] or tokens[i]['line'] != tokens[i+1]['line']:
            continue
        s_from = STATE_IDX.get(tokens[i]['state'])
        s_to = STATE_IDX.get(tokens[i+1]['state'])
        if s_from is not None and s_to is not None:
            pooled_trans[s_from, s_to] += 1

    pooled_flat = pooled_trans.flatten() + 1e-10
    pooled_flat = pooled_flat / pooled_flat.sum()

    regime_jsds = {}
    for regime in sorted(regimes):
        regime_tokens = [t for t in tokens if t['regime'] == regime]
        if len(regime_tokens) < 100:
            continue
        rt = np.zeros((6, 6))
        for i in range(len(regime_tokens) - 1):
            if regime_tokens[i]['folio'] != regime_tokens[i+1]['folio'] or regime_tokens[i]['line'] != regime_tokens[i+1]['line']:
                continue
            sf = STATE_IDX.get(regime_tokens[i]['state'])
            st = STATE_IDX.get(regime_tokens[i+1]['state'])
            if sf is not None and st is not None:
                rt[sf, st] += 1
        rt_flat = rt.flatten() + 1e-10
        rt_flat = rt_flat / rt_flat.sum()
        m = 0.5 * (pooled_flat + rt_flat)
        jsd = float(0.5 * scipy_entropy(pooled_flat, m, base=2) + 0.5 * scipy_entropy(rt_flat, m, base=2))
        regime_jsds[regime] = jsd
        print(f"  {regime} JSD from pooled: {jsd:.6f}")

    mean_jsd = float(np.mean(list(regime_jsds.values()))) if regime_jsds else 0

    verdict = "LOAD_BEARING" if gap_diff_pct > 5 else "DECORATIVE"
    print(f"  Mean JSD: {mean_jsd:.6f}")
    print(f"  Verdict: {verdict}")

    return {
        'pooled_spectral_gap': float(pooled_gap),
        'per_regime_spectral_gaps': regime_gaps,
        'mean_regime_spectral_gap': mean_regime_gap,
        'gap_diff_pct': float(gap_diff_pct),
        'per_regime_jsd': regime_jsds,
        'mean_jsd': mean_jsd,
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

# Global for forbidden pairs (used in compute_metrics)
_forbidden_pairs = set()


def main():
    global _forbidden_pairs

    print("=" * 60)
    print("Phase 346: STRUCTURAL_NECESSITY_ABLATION")
    print("=" * 60)

    tokens, forbidden_pairs = load_data()
    _forbidden_pairs = forbidden_pairs

    # Baseline
    print("\n--- Computing baseline metrics ---")
    baseline = compute_metrics(tokens)
    print(f"  Spectral gap: {baseline['spectral_gap']:.4f}")
    print(f"  Forbidden transitions: {baseline['forbidden_count']}")
    print(f"  AXM exit entropy: {baseline['exit_entropy']:.3f} bits")
    print(f"  AXM mean dwell: {baseline['mean_dwell']:.1f}")
    print(f"  Transitions: {baseline['n_transitions']}")

    results = {
        'metadata': {
            'phase': 346,
            'name': 'STRUCTURAL_NECESSITY_ABLATION',
            'total_tokens': len(tokens),
            'n_null_controls': N_NULL,
        },
        'baseline': baseline,
    }

    results['t1_fl_merge'] = run_t1(tokens, baseline)
    results['t2_gatekeeper'] = run_t2(tokens, baseline)
    results['t3_prefix_shuffle'] = run_t3(tokens, baseline)
    results['t4_regime_merge'] = run_t4(tokens, baseline)

    # Synthesis
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    verdicts = {
        'T1_fl_merge': results['t1_fl_merge']['verdict'],
        'T2_gatekeeper': results['t2_gatekeeper']['verdict'],
        'T3a_prefix_within_state': results['t3_prefix_shuffle']['t3a']['verdict'],
        'T3b_prefix_within_position': results['t3_prefix_shuffle']['t3b']['verdict'],
        'T3c_prefix_global': results['t3_prefix_shuffle']['t3c']['verdict'],
        'T4_regime_merge': results['t4_regime_merge']['verdict'],
    }

    for test, v in verdicts.items():
        print(f"  {test}: {v}")

    load_bearing = sum(1 for v in verdicts.values() if v == 'LOAD_BEARING')
    partial = sum(1 for v in verdicts.values() if v == 'PARTIAL')
    decorative = sum(1 for v in verdicts.values() if v == 'DECORATIVE')

    print(f"\n  LOAD_BEARING: {load_bearing}, PARTIAL: {partial}, DECORATIVE: {decorative}")

    # Determine hierarchy
    gaps = {
        'baseline': baseline['spectral_gap'],
        'T3a': results['t3_prefix_shuffle']['t3a']['spectral_gap'],
        'T3b': results['t3_prefix_shuffle']['t3b']['spectral_gap'],
        'T3c': results['t3_prefix_shuffle']['t3c']['spectral_gap'],
    }
    hierarchy = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  Spectral gap hierarchy: {' > '.join(f'{k}({v:.3f})' for k, v in hierarchy)}")

    results['synthesis'] = {
        'verdicts': verdicts,
        'load_bearing': load_bearing,
        'partial': partial,
        'decorative': decorative,
        'spectral_gap_hierarchy': {k: float(v) for k, v in gaps.items()},
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'structural_necessity_ablation.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {RESULTS_DIR / 'structural_necessity_ablation.json'}")


if __name__ == '__main__':
    main()
