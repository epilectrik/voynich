#!/usr/bin/env python3
"""
Phase 328: MACRO_AUTOMATON_NECESSITY

Tests whether k=6 is the minimal invariant-preserving macro abstraction
of the Voynich control grammar.

T1: k-Sweep Fidelity + Constraint Retention (k=3..12)
T2: Information-Theoretic Model Selection (AIC/BIC)
T3: Constraint Violation Accounting (k<6)
T4: Upward Split Analysis (k=7,8 with 5 alternative partitions)
T5: Independent Spectral Clustering (k=3..12)
T6: Synthesis and Verdict
"""

import sys
import json
import time
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.spatial.distance import jensenshannon
from scipy.cluster.vq import kmeans2

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SYNTHETIC = 200
RNG = np.random.default_rng(42)

# Structural constants
ROLE_FAMILIES = {
    'CC': {10, 11, 12},
    'FQ': {9, 13, 14, 23},
    'FL_HAZ': {7, 30},
    'FL_SAFE': {38, 40},
}
GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}


# =============================================================================
# SECTION 0: Data Loading & Pre-computation
# =============================================================================

def load_all_data():
    """Load and pre-compute all shared data structures. O(n) total."""
    print("[0/6] Loading data...")

    with open(PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON/results/t1_transition_data.json') as f:
        t1 = json.load(f)
    with open(PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON/results/t3_merged_automaton.json') as f:
        t3 = json.load(f)

    all_classes = t1['classes']
    n_cls = len(all_classes)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    counts_49 = np.array(t1['counts_49x49'], dtype=float)
    class_details = t1['class_details']
    class_freq = {int(c): d['frequency'] for c, d in class_details.items()}
    class_to_role = {int(c): d['role'] for c, d in class_details.items()}
    line_lengths = t1['line_lengths']
    merge_log = t3['merge_log']
    n_transitions = t1['n_transitions']

    # Row-normalized probability matrix
    row_sums = counts_49.sum(axis=1, keepdims=True)
    probs_49 = np.divide(counts_49, row_sums, where=row_sums > 0,
                         out=np.zeros_like(counts_49))

    # Expected counts for depleted pair detection
    rs = counts_49.sum(axis=1)
    cs = counts_49.sum(axis=0)
    total = counts_49.sum()
    expected = np.outer(rs, cs) / total if total > 0 else np.zeros_like(counts_49)

    # Depleted pairs: obs/exp < 0.2, expected >= 5
    depleted_pairs = set()
    for i in range(n_cls):
        for j in range(n_cls):
            if expected[i][j] >= 5:
                ratio = counts_49[i][j] / expected[i][j]
                if ratio < 0.2:
                    depleted_pairs.add((all_classes[i], all_classes[j]))
    print(f"  {len(depleted_pairs)} depleted class-pairs")

    # JSD distance matrix (49x49, computed ONCE)
    jsd_matrix = np.zeros((n_cls, n_cls))
    for i in range(n_cls):
        for j in range(i + 1, n_cls):
            d = jensenshannon(probs_49[i] + 1e-15, probs_49[j] + 1e-15)
            jsd_matrix[i][j] = d
            jsd_matrix[j][i] = d

    # Load real corpus as class sequences (one pass)
    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    tx = Transcript()
    real_lines = []
    current_key = None
    current_seq = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        key = (token.folio, token.line)
        if key != current_key:
            if current_seq:
                real_lines.append(current_seq)
            current_seq = []
            current_key = key
        current_seq.append(cls)
    if current_seq:
        real_lines.append(current_seq)

    # EN/AX class sets
    en_classes = {c for c in all_classes if class_to_role[c] == 'EN'}
    ax_classes = {c for c in all_classes if class_to_role[c] == 'AX'}

    print(f"  {n_cls} classes, {len(real_lines)} lines, {n_transitions} transitions")
    print(f"  {len(depleted_pairs)} depleted pairs, {len(en_classes)} EN, {len(ax_classes)} AX")

    return {
        'all_classes': all_classes,
        'n_cls': n_cls,
        'cls_to_idx': cls_to_idx,
        'counts_49': counts_49,
        'probs_49': probs_49,
        'expected': expected,
        'class_freq': class_freq,
        'class_to_role': class_to_role,
        'line_lengths': line_lengths,
        'merge_log': merge_log,
        'n_transitions': n_transitions,
        'depleted_pairs': depleted_pairs,
        'jsd_matrix': jsd_matrix,
        'real_lines': real_lines,
        'token_to_class': token_to_class,
        'en_classes': en_classes,
        'ax_classes': ax_classes,
    }


# =============================================================================
# SECTION 1: Shared Helper Functions
# =============================================================================

def reconstruct_partition(merge_log, target_k, n_cls=49, all_classes=None):
    """Reconstruct partition at a given k from the merge log.

    Returns list of sets, each set containing class IDs.
    For k >= 6, reverses merge log to the appropriate step.
    """
    # Start with singletons
    groups = {c: frozenset([c]) for c in all_classes}
    # class -> group_id mapping
    cls_to_group = {c: c for c in all_classes}
    current_k = n_cls

    for step in merge_log:
        if current_k <= target_k:
            break
        merged_lists = step['merged']
        # Find the two groups being merged
        group_a = frozenset()
        for c in merged_lists[0]:
            group_a = group_a | groups[cls_to_group[c]]
        group_b = frozenset()
        for c in merged_lists[1]:
            group_b = group_b | groups[cls_to_group[c]]
        # Create new merged group
        new_group = group_a | group_b
        # Pick a representative ID
        rep = min(new_group)
        groups[rep] = new_group
        for c in new_group:
            cls_to_group[c] = rep
        # Remove old group entries
        for c in new_group:
            if c != rep and c in groups:
                del groups[c]
        current_k -= 1

    return [set(g) for g in groups.values()]


def force_merge_below_6(partition_6, counts_49, all_classes, cls_to_idx, target_k):
    """Force merges below k=6, picking lowest-JSD pairs (constraint-violating).

    Returns (partition, merge_history) where merge_history records each forced merge.
    """
    partition = [set(g) for g in partition_6]
    history = []

    while len(partition) > target_k:
        # Compute JSD between all pairs
        best_jsd = float('inf')
        best_pair = None
        n = len(partition)
        for i in range(n):
            for j in range(i + 1, n):
                # Aggregate count rows for each group
                row_i = np.zeros(len(all_classes))
                for c in partition[i]:
                    row_i += counts_49[cls_to_idx[c]]
                row_j = np.zeros(len(all_classes))
                for c in partition[j]:
                    row_j += counts_49[cls_to_idx[c]]
                # Normalize
                pi = row_i / max(row_i.sum(), 1e-15)
                pj = row_j / max(row_j.sum(), 1e-15)
                d = jensenshannon(pi + 1e-15, pj + 1e-15)
                if d < best_jsd:
                    best_jsd = d
                    best_pair = (i, j)

        i, j = best_pair
        # Check what constraints are violated
        violations = check_merge_violations(partition[i], partition[j], all_classes,
                                            cls_to_idx, counts_49)
        history.append({
            'merged': [sorted(partition[i]), sorted(partition[j])],
            'jsd': round(float(best_jsd), 6),
            'violations': violations,
            'states_after': len(partition) - 1,
        })
        # Merge
        new_group = partition[i] | partition[j]
        partition = [g for idx, g in enumerate(partition) if idx not in (i, j)]
        partition.append(new_group)

    return partition, history


def check_merge_violations(group_a, group_b, all_classes, cls_to_idx, counts_49):
    """Check what structural constraints a merge would violate."""
    violations = []
    combined = group_a | group_b

    # Role violations
    roles_a = {get_fine_role(c) for c in group_a}
    roles_b = {get_fine_role(c) for c in group_b}

    # Check CC purity
    cc = ROLE_FAMILIES['CC']
    if (group_a & cc) and (group_b - cc):
        violations.append('ROLE: CC mixed with non-CC')
    if (group_b & cc) and (group_a - cc):
        violations.append('ROLE: CC mixed with non-CC')

    # Check FQ purity
    fq = ROLE_FAMILIES['FQ']
    if (group_a & fq) and (group_b - fq):
        violations.append('ROLE: FQ mixed with non-FQ')
    if (group_b & fq) and (group_a - fq):
        violations.append('ROLE: FQ mixed with non-FQ')

    # Check FL_HAZ / FL_SAFE separation
    fl_haz = ROLE_FAMILIES['FL_HAZ']
    fl_safe = ROLE_FAMILIES['FL_SAFE']
    if (combined & fl_haz) and (combined & fl_safe):
        violations.append('ROLE: FL_HAZ mixed with FL_SAFE')

    # Check FL mixed with EN/AX
    fl_all = fl_haz | fl_safe
    enax = set(c for c in all_classes if c not in cc and c not in fq and c not in fl_all)
    if (combined & fl_all) and (combined & enax):
        violations.append('ROLE: FL mixed with EN/AX')

    # Depletion violations
    # Check if any known depleted pair (from binding constraints) would be merged
    binding_depleted = [
        (24, 30), (11, 14), (13, 5), (9, 33),
        (13, 40), (11, 36), (5, 34), (33, 38),
    ]
    for a, b in binding_depleted:
        if a in combined and b in combined:
            if not (a in group_a and b in group_a) and not (a in group_b and b in group_b):
                violations.append(f'DEPLETION: ({a},{b}) merged')

    return violations


def get_fine_role(cls_id):
    """Get fine-grained role (FL_HAZ, FL_SAFE, CC, FQ, EN, AX)."""
    for role, classes in ROLE_FAMILIES.items():
        if cls_id in classes:
            return role
    # Not in special roles: EN or AX
    # EN: class 8, and classes 31-49 minus FL
    en_set = ({8} | set(range(31, 50))) - ROLE_FAMILIES['FL_HAZ'] - ROLE_FAMILIES['FL_SAFE']
    if cls_id in en_set:
        return 'EN'
    return 'AX'


def build_state_automaton(partition, counts_49, class_freq, all_classes, cls_to_idx):
    """Build k-state automaton from a partition.

    Returns (state_probs, emission, initial, cls_to_state).
    Pre-computes CDFs for efficient sampling.
    """
    n_states = len(partition)
    n_cls = len(all_classes)

    # Map class -> state
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # State-level transition counts
    state_counts = np.zeros((n_states, n_states))
    for ci, c in enumerate(all_classes):
        for cj, d in enumerate(all_classes):
            si, sj = cls_to_state[c], cls_to_state[d]
            state_counts[si][sj] += counts_49[ci][cj]

    row_sums = state_counts.sum(axis=1, keepdims=True)
    state_probs = np.divide(state_counts, row_sums, where=row_sums > 0,
                            out=np.zeros_like(state_counts))

    # Emission: P(class | state)
    emission = np.zeros((n_states, n_cls))
    for ci, c in enumerate(all_classes):
        si = cls_to_state[c]
        emission[si][ci] = class_freq.get(c, 0)
    em_sums = emission.sum(axis=1, keepdims=True)
    emission = np.divide(emission, em_sums, where=em_sums > 0,
                         out=np.zeros_like(emission))

    # Initial state distribution
    state_freqs = np.array([sum(class_freq.get(c, 0) for c in group)
                            for group in partition], dtype=float)
    initial = state_freqs / max(state_freqs.sum(), 1e-15)

    return state_probs, emission, initial, cls_to_state


def simulate_corpus(state_probs, emission, initial, line_lengths, all_classes, rng):
    """Generate one synthetic corpus. O(n_tokens) with pre-computed CDFs."""
    n_states = len(state_probs)
    n_classes = len(all_classes)
    # Pre-compute CDFs (O(k^2 + k*n_cls))
    cum_state = np.cumsum(state_probs, axis=1)
    cum_emit = np.cumsum(emission, axis=1)
    cum_init = np.cumsum(initial)

    lines = []
    for length in line_lengths:
        if length == 0:
            lines.append([])
            continue
        seq = []
        state = min(np.searchsorted(cum_init, rng.random()), n_states - 1)
        for _ in range(length):
            cls_idx = min(np.searchsorted(cum_emit[state], rng.random()), n_classes - 1)
            seq.append(all_classes[cls_idx])
            state = min(np.searchsorted(cum_state[state], rng.random()), n_states - 1)
        lines.append(seq)
    return lines


def compute_fidelity_metrics(lines, all_classes, cls_to_idx):
    """Compute 5 corpus-level fidelity metrics. O(n_tokens + n_cls^2)."""
    n_cls = len(all_classes)

    # Class frequencies
    class_freq = Counter()
    for seq in lines:
        for c in seq:
            class_freq[c] += 1

    # Zipf slope
    freqs = sorted(class_freq.values(), reverse=True)
    if len(freqs) >= 2:
        log_ranks = np.log(np.arange(1, len(freqs) + 1))
        log_freqs = np.log(np.array(freqs, dtype=float))
        zipf_slope = float(np.polyfit(log_ranks, log_freqs, 1)[0])
    else:
        zipf_slope = 0.0

    # Transition counts
    counts = np.zeros((n_cls, n_cls))
    for seq in lines:
        for i in range(len(seq) - 1):
            a, b = cls_to_idx[seq[i]], cls_to_idx[seq[i + 1]]
            counts[a][b] += 1

    # Depleted pairs
    rs = counts.sum(axis=1)
    cs = counts.sum(axis=0)
    total = counts.sum()
    exp = np.outer(rs, cs) / total if total > 0 else np.zeros_like(counts)

    n_depleted = 0
    n_asym = 0
    for i in range(n_cls):
        for j in range(n_cls):
            if exp[i][j] >= 5:
                ratio = counts[i][j] / exp[i][j]
                if ratio < 0.2:
                    n_depleted += 1
                    if exp[j][i] >= 5:
                        rev = counts[j][i] / exp[j][i]
                        if rev >= 0.2:
                            n_asym += 1
    asymmetry = n_asym / n_depleted if n_depleted > 0 else 0.0

    # Cross-line MI
    joint = np.zeros((n_cls, n_cls))
    last_m = np.zeros(n_cls)
    first_m = np.zeros(n_cls)
    for i in range(len(lines) - 1):
        if len(lines[i]) == 0 or len(lines[i + 1]) == 0:
            continue
        last = cls_to_idx[lines[i][-1]]
        first = cls_to_idx[lines[i + 1][0]]
        joint[last][first] += 1
        last_m[last] += 1
        first_m[first] += 1
    total_j = joint.sum()
    cross_mi = 0.0
    if total_j > 0:
        for a in range(n_cls):
            for b in range(n_cls):
                if joint[a][b] > 0:
                    p_ab = joint[a][b] / total_j
                    p_a = last_m[a] / total_j
                    p_b = first_m[b] / total_j
                    if p_a > 0 and p_b > 0:
                        cross_mi += p_ab * np.log2(p_ab / (p_a * p_b))

    return {
        'zipf_slope': round(zipf_slope, 4),
        'n_depleted': n_depleted,
        'asymmetry': round(asymmetry, 4),
        'cross_line_mi': round(cross_mi, 4),
        'n_active_classes': len(class_freq),
    }


def compute_spectral_gap(state_probs):
    """Compute spectral gap of transition matrix. O(k^3)."""
    eigvals = np.abs(np.linalg.eigvals(state_probs))
    eigvals_sorted = sorted(eigvals, reverse=True)
    if len(eigvals_sorted) >= 2:
        return round(float(eigvals_sorted[0] - eigvals_sorted[1]), 6)
    return 0.0


def compute_constraint_retention(partition, all_classes, depleted_pairs, cls_to_idx):
    """Score how well a partition preserves structural invariants.

    Returns dict with retention metrics.
    """
    # Map class -> state index
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # 1. Depleted pair localization: how many depleted pairs are cross-state?
    cross_state = 0
    within_state = 0
    for a, b in depleted_pairs:
        if a in cls_to_state and b in cls_to_state:
            if cls_to_state[a] != cls_to_state[b]:
                cross_state += 1
            else:
                within_state += 1
    total_dep = cross_state + within_state
    dep_cross_frac = cross_state / total_dep if total_dep > 0 else 0.0

    # 2. FL_HAZ / FL_SAFE separation
    fl_haz_states = {cls_to_state[c] for c in ROLE_FAMILIES['FL_HAZ'] if c in cls_to_state}
    fl_safe_states = {cls_to_state[c] for c in ROLE_FAMILIES['FL_SAFE'] if c in cls_to_state}
    fl_separated = len(fl_haz_states & fl_safe_states) == 0

    # 3. EN/AX indistinguishability: no state should be EN-only or AX-only
    # (among states that contain EN or AX classes)
    en_set = {c for c in all_classes if get_fine_role(c) == 'EN'}
    ax_set = {c for c in all_classes if get_fine_role(c) == 'AX'}
    enax_violation = False
    for group in partition:
        has_en = bool(group & en_set)
        has_ax = bool(group & ax_set)
        # If a state has EN but not AX (or vice versa), and it has > 2 classes
        # (small states might naturally be one type)
        if len(group) > 2:
            if has_en and not has_ax:
                enax_violation = True
            if has_ax and not has_en:
                enax_violation = True

    # 4. Role purity: fraction of states that are role-pure
    # (all classes share the same fine role)
    n_pure = 0
    for group in partition:
        roles = {get_fine_role(c) for c in group}
        # EN and AX mixing is OK (C977)
        roles_simplified = set()
        for r in roles:
            if r in ('EN', 'AX'):
                roles_simplified.add('ENAX')
            else:
                roles_simplified.add(r)
        if len(roles_simplified) == 1:
            n_pure += 1
    role_purity = n_pure / len(partition) if partition else 0.0

    return {
        'depleted_cross_state': cross_state,
        'depleted_within_state': within_state,
        'depleted_cross_fraction': round(dep_cross_frac, 4),
        'fl_separated': fl_separated,
        'enax_violation': enax_violation,
        'role_purity': round(role_purity, 4),
    }


def compute_log_likelihood(partition, counts_49, all_classes, cls_to_idx, class_freq):
    """Compute log-likelihood of observed transitions under k-state HMM.

    For each observed class pair (i,j):
      P(class_j | class_i) = P(state_j | state_i) * P(class_j | state_j)

    LL = sum_{i,j} counts[i,j] * log(P(state_j|state_i) * P(class_j|state_j))

    This correctly models the state-compression: more states give better LL
    because emission distributions become more concentrated.
    """
    n_states = len(partition)
    n_cls = len(all_classes)
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # Build state transition counts
    state_counts = np.zeros((n_states, n_states))
    for ci, c in enumerate(all_classes):
        for cj, d in enumerate(all_classes):
            si, sj = cls_to_state[c], cls_to_state[d]
            state_counts[si][sj] += counts_49[ci][cj]

    row_sums = state_counts.sum(axis=1, keepdims=True)
    state_probs = np.divide(state_counts, row_sums, where=row_sums > 0,
                            out=np.zeros_like(state_counts))

    # Build emission probabilities P(class | state)
    emission = np.zeros((n_states, n_cls))
    for ci, c in enumerate(all_classes):
        si = cls_to_state[c]
        emission[si][ci] = class_freq.get(c, 0)
    em_sums = emission.sum(axis=1, keepdims=True)
    emission = np.divide(emission, em_sums, where=em_sums > 0,
                         out=np.zeros_like(emission))

    # LL = sum counts[i,j] * log(P(s_j|s_i) * P(class_j|s_j))
    ll = 0.0
    for ci, c in enumerate(all_classes):
        si = cls_to_state[c]
        for cj, d in enumerate(all_classes):
            if counts_49[ci][cj] > 0:
                sj = cls_to_state[d]
                p_trans = state_probs[si][sj]
                p_emit = emission[sj][cj]
                p = p_trans * p_emit
                if p > 0:
                    ll += counts_49[ci][cj] * np.log(p)
                else:
                    ll += counts_49[ci][cj] * np.log(1e-15)

    return float(ll)


def run_fidelity_comparison(partition, data, real_metrics, n_synthetic=N_SYNTHETIC):
    """Run synthetic generation at a given partition and compare to real.

    Returns comparison dict with z-scores and match flags.
    """
    state_probs, emission, initial, _ = build_state_automaton(
        partition, data['counts_49'], data['class_freq'],
        data['all_classes'], data['cls_to_idx'])

    syn_metrics = {k: [] for k in real_metrics.keys()}
    for _ in range(n_synthetic):
        syn_lines = simulate_corpus(state_probs, emission, initial,
                                    data['line_lengths'], data['all_classes'], RNG)
        m = compute_fidelity_metrics(syn_lines, data['all_classes'], data['cls_to_idx'])
        for k, v in m.items():
            syn_metrics[k].append(v)

    comparison = {}
    for metric, real_val in real_metrics.items():
        syn_arr = np.array(syn_metrics[metric])
        syn_mean = float(np.mean(syn_arr))
        syn_std = float(np.std(syn_arr))
        z = (real_val - syn_mean) / syn_std if syn_std > 0 else 0.0
        comparison[metric] = {
            'real': round(float(real_val), 4),
            'syn_mean': round(syn_mean, 4),
            'syn_std': round(syn_std, 4),
            'z_score': round(z, 2),
            'match': bool(abs(z) < 3),
        }

    n_match = sum(1 for v in comparison.values() if v['match'])
    fidelity = n_match / len(comparison)
    return comparison, round(fidelity, 4)


# =============================================================================
# T1: k-Sweep Fidelity + Constraint Retention
# =============================================================================

def run_t1(data, real_metrics):
    """k-sweep from k=3 to k=12 with fidelity and constraint retention."""
    print("\n" + "=" * 70)
    print("T1: k-Sweep Fidelity + Constraint Retention (k=3..12)")
    print("=" * 70)

    all_classes = data['all_classes']
    counts_49 = data['counts_49']
    cls_to_idx = data['cls_to_idx']
    merge_log = data['merge_log']
    depleted_pairs = data['depleted_pairs']

    # Get canonical 6-state partition
    partition_6 = reconstruct_partition(merge_log, 6, len(all_classes), all_classes)

    results = {}
    for k in range(3, 13):
        print(f"\n  k={k}...")

        if k >= 6:
            partition = reconstruct_partition(merge_log, k, len(all_classes), all_classes)
        else:
            partition, forced_history = force_merge_below_6(
                partition_6, counts_49, all_classes, cls_to_idx, k)

        # State automaton
        state_probs, _, _, _ = build_state_automaton(
            partition, counts_49, data['class_freq'], all_classes, cls_to_idx)

        # Spectral gap
        gap = compute_spectral_gap(state_probs)

        # Constraint retention
        retention = compute_constraint_retention(partition, all_classes, depleted_pairs, cls_to_idx)

        # Fidelity (synthetic comparison)
        comparison, fidelity = run_fidelity_comparison(partition, data, real_metrics)

        # Log-likelihood for AIC/BIC
        ll = compute_log_likelihood(partition, counts_49, all_classes, cls_to_idx, data['class_freq'])
        # Params: k*(k-1) transition + (n_cls - k) emission = k^2 - 2k + n_cls
        params = k * (k - 1) + (data['n_cls'] - k)
        n_trans = data['n_transitions']
        aic = 2 * params - 2 * ll
        bic = params * np.log(n_trans) - 2 * ll

        depletion_z = comparison.get('n_depleted', {}).get('z_score', None)

        print(f"    States: {len(partition)}, Spectral gap: {gap:.4f}")
        print(f"    Fidelity: {fidelity:.2f}, Depletion z: {depletion_z}")
        print(f"    Constraint retention: dep_cross={retention['depleted_cross_fraction']:.3f}, "
              f"fl_sep={retention['fl_separated']}, role_pure={retention['role_purity']:.3f}")
        print(f"    AIC: {aic:.1f}, BIC: {bic:.1f}")

        entry = {
            'k': k,
            'partition': [sorted(g) for g in partition],
            'spectral_gap': gap,
            'retention': retention,
            'fidelity': fidelity,
            'comparison': comparison,
            'log_likelihood': round(ll, 2),
            'aic': round(aic, 2),
            'bic': round(bic, 2),
            'params': params,
        }
        if k < 6:
            entry['forced_merges'] = forced_history

        results[str(k)] = entry

    return results


# =============================================================================
# T2: Information-Theoretic Model Selection (extracted from T1 data)
# =============================================================================

def run_t2(t1_results):
    """Extract and analyze AIC/BIC curves from T1 results."""
    print("\n" + "=" * 70)
    print("T2: Information-Theoretic Model Selection (AIC/BIC)")
    print("=" * 70)

    aic_vals = {}
    bic_vals = {}
    ll_vals = {}
    for k_str, entry in sorted(t1_results.items(), key=lambda x: int(x[0])):
        k = int(k_str)
        aic_vals[k] = entry['aic']
        bic_vals[k] = entry['bic']
        ll_vals[k] = entry['log_likelihood']

    # Find minima
    aic_min_k = min(aic_vals, key=aic_vals.get)
    bic_min_k = min(bic_vals, key=bic_vals.get)

    print(f"\n  AIC minimum at k={aic_min_k} ({aic_vals[aic_min_k]:.1f})")
    print(f"  BIC minimum at k={bic_min_k} ({bic_vals[bic_min_k]:.1f})")
    print(f"\n  AIC curve:")
    for k in sorted(aic_vals):
        marker = " <-- MIN" if k == aic_min_k else ""
        print(f"    k={k:>2}: AIC={aic_vals[k]:>12.1f}  BIC={bic_vals[k]:>12.1f}  "
              f"LL={ll_vals[k]:>12.1f}{marker}")

    # Check AIC plateau (is the difference between k=6 and neighbors < 5%?)
    if 6 in aic_vals and 7 in aic_vals:
        aic_6_7_diff = abs(aic_vals[6] - aic_vals[7]) / abs(aic_vals[6]) * 100
    else:
        aic_6_7_diff = None

    return {
        'aic_values': {str(k): round(v, 2) for k, v in aic_vals.items()},
        'bic_values': {str(k): round(v, 2) for k, v in bic_vals.items()},
        'aic_minimum_k': aic_min_k,
        'bic_minimum_k': bic_min_k,
        'aic_6_7_pct_diff': round(aic_6_7_diff, 2) if aic_6_7_diff is not None else None,
        'caution': 'Models are induced by hard merges; interpret directionally',
    }


# =============================================================================
# T3: Constraint Violation Accounting (k<6)
# =============================================================================

def run_t3(t1_results):
    """Analyze which invariants break at k<6."""
    print("\n" + "=" * 70)
    print("T3: Constraint Violation Accounting (k<6)")
    print("=" * 70)

    violations_by_k = {}
    for k in [5, 4, 3]:
        k_str = str(k)
        if k_str not in t1_results:
            continue
        entry = t1_results[k_str]
        forced = entry.get('forced_merges', [])
        retention = entry['retention']

        all_violations = []
        for fm in forced:
            all_violations.extend(fm['violations'])

        # Categorize
        role_v = [v for v in all_violations if v.startswith('ROLE')]
        dep_v = [v for v in all_violations if v.startswith('DEPLETION')]

        # Which invariant breaks first?
        first_violations = forced[0]['violations'] if forced else []

        print(f"\n  k={k}: {len(all_violations)} total violations")
        print(f"    ROLE: {len(role_v)}, DEPLETION: {len(dep_v)}")
        print(f"    First merge violations: {first_violations}")
        print(f"    FL separated: {retention['fl_separated']}")
        print(f"    EN/AX violation: {retention['enax_violation']}")
        print(f"    Role purity: {retention['role_purity']:.3f}")

        violations_by_k[k_str] = {
            'total_violations': len(all_violations),
            'role_violations': len(role_v),
            'depletion_violations': len(dep_v),
            'all_violations': all_violations,
            'first_merge_violations': first_violations,
            'retention': retention,
        }

    return violations_by_k


# =============================================================================
# T4: Upward Split Analysis (k=7, k=8)
# =============================================================================

def run_t4(data, real_metrics):
    """Test 5 alternative 7-state partitions."""
    print("\n" + "=" * 70)
    print("T4: Upward Split Analysis (5 alternative 7-state partitions)")
    print("=" * 70)

    all_classes = data['all_classes']
    counts_49 = data['counts_49']
    cls_to_idx = data['cls_to_idx']
    merge_log = data['merge_log']
    depleted_pairs = data['depleted_pairs']
    jsd_matrix = data['jsd_matrix']

    # Get canonical 6-state partition
    partition_6 = reconstruct_partition(merge_log, 6, len(all_classes), all_classes)

    # Identify AXM group (the one with 32 classes)
    axm_group = None
    axm_idx = None
    other_groups = []
    for i, g in enumerate(partition_6):
        if len(g) > 20:  # AXM has 32 classes
            axm_group = g
            axm_idx = i
        else:
            other_groups.append(g)

    if axm_group is None:
        print("  ERROR: Could not identify AXM group")
        return {}

    axm_classes = sorted(axm_group)
    axm_indices = [cls_to_idx[c] for c in axm_classes]
    print(f"  AXM group: {len(axm_group)} classes")

    splits = {}

    # 1. JSD-greedy: undo last merge (split FL_SAFE into {38} and {40})
    print("\n  [1] JSD-greedy split (undo step 43: FL_SAFE -> {38},{40})...")
    partition_jsd = reconstruct_partition(merge_log, 7, len(all_classes), all_classes)
    splits['jsd_greedy'] = evaluate_split(partition_jsd, data, real_metrics, depleted_pairs)

    # 2. AXM spectral split: spectral bisection of AXM
    print("  [2] AXM spectral bisection...")
    axm_sub_jsd = jsd_matrix[np.ix_(axm_indices, axm_indices)]
    # Convert JSD distance to affinity
    sigma = np.median(axm_sub_jsd[axm_sub_jsd > 0]) if np.any(axm_sub_jsd > 0) else 1.0
    affinity = np.exp(-axm_sub_jsd ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(affinity, 0)
    # Normalized Laplacian
    D = np.diag(affinity.sum(axis=1))
    D_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(affinity.sum(axis=1), 1e-15)))
    L = np.eye(len(axm_classes)) - D_inv_sqrt @ affinity @ D_inv_sqrt
    eigvals, eigvecs = np.linalg.eigh(L)
    # Use Fiedler vector (2nd smallest eigenvalue)
    fiedler = eigvecs[:, 1]
    group_a_axm = {axm_classes[i] for i in range(len(axm_classes)) if fiedler[i] <= 0}
    group_b_axm = {axm_classes[i] for i in range(len(axm_classes)) if fiedler[i] > 0}
    partition_spectral = other_groups + [group_a_axm, group_b_axm]
    splits['axm_spectral'] = evaluate_split(partition_spectral, data, real_metrics, depleted_pairs)
    splits['axm_spectral']['split_sizes'] = [len(group_a_axm), len(group_b_axm)]

    # 3. Gatekeeper split: separate {15,20,21,22,25} from AXM
    print("  [3] Gatekeeper split ({15,20,21,22,25} from AXM)...")
    gk_in_axm = GATEKEEPER_CLASSES & axm_group
    rest_axm = axm_group - gk_in_axm
    if gk_in_axm and rest_axm:
        partition_gk = other_groups + [gk_in_axm, rest_axm]
        splits['gatekeeper'] = evaluate_split(partition_gk, data, real_metrics, depleted_pairs)
        splits['gatekeeper']['split_sizes'] = [len(gk_in_axm), len(rest_axm)]
    else:
        print("    Gatekeeper classes not fully in AXM, skipping")

    # 4. Affordance-motivated split: STABILITY_CRITICAL-enriched classes
    print("  [4] Affordance-motivated split (STABILITY_CRITICAL enrichment)...")
    try:
        with open(PROJECT_ROOT / 'data/middle_affordance_table.json') as f:
            aff_table = json.load(f)
        # Build MIDDLE -> bin mapping (table is dict with 'middles' key)
        mid_to_bin = {}
        middles_data = aff_table.get('middles', aff_table)
        for mid_name, mid_info in middles_data.items():
            mid_to_bin[mid_name] = mid_info.get('affordance_bin', -1)

        # For each AXM class, compute fraction of tokens with STABILITY_CRITICAL MIDDLEs
        morph = Morphology()
        stab_frac = {}
        # Pre-build: class -> token list
        class_to_tokens = defaultdict(list)
        for t, c in data['token_to_class'].items():
            if c in axm_group:
                class_to_tokens[c].append(t)

        for c in axm_classes:
            tokens = class_to_tokens.get(c, [])
            if not tokens:
                stab_frac[c] = 0.0
                continue
            n_stab = 0
            for t in tokens:
                m = morph.extract(t)
                if m and m.middle:
                    b = mid_to_bin.get(m.middle, -1)
                    if b == 8:  # STABILITY_CRITICAL
                        n_stab += 1
            stab_frac[c] = n_stab / len(tokens)

        # Split: top half by stab_frac vs bottom half
        median_frac = np.median(list(stab_frac.values()))
        stab_high = {c for c in axm_classes if stab_frac[c] > median_frac}
        stab_low = axm_group - stab_high
        if stab_high and stab_low:
            partition_aff = other_groups + [stab_high, stab_low]
            splits['affordance'] = evaluate_split(partition_aff, data, real_metrics, depleted_pairs)
            splits['affordance']['split_sizes'] = [len(stab_high), len(stab_low)]
            splits['affordance']['median_stab_frac'] = round(float(median_frac), 4)
        else:
            print("    Could not split by affordance (all same side)")
    except Exception as e:
        print(f"    Affordance split failed: {e}")

    # 5. Entropy-maximizing split: maximize internal transition KL divergence
    print("  [5] Entropy-maximizing split (max internal KL divergence)...")
    # Use same spectral approach but with transition-based affinity
    # Extract AXM internal transition submatrix
    axm_counts_sub = counts_49[np.ix_(axm_indices, axm_indices)]
    rs = axm_counts_sub.sum(axis=1, keepdims=True)
    axm_probs_sub = np.divide(axm_counts_sub, rs, where=rs > 0,
                               out=np.zeros_like(axm_counts_sub, dtype=float))
    # Average row profile
    avg_profile = axm_probs_sub.mean(axis=0)
    # KL divergence of each class from average (measures "distinctiveness")
    kl_divs = np.zeros(len(axm_classes))
    for i in range(len(axm_classes)):
        p = axm_probs_sub[i] + 1e-15
        q = avg_profile + 1e-15
        kl_divs[i] = float(np.sum(p * np.log(p / q)))
    # Split at median KL: high-KL classes vs low-KL classes
    median_kl = np.median(kl_divs)
    kl_high = {axm_classes[i] for i in range(len(axm_classes)) if kl_divs[i] > median_kl}
    kl_low = axm_group - kl_high
    if kl_high and kl_low:
        partition_kl = other_groups + [kl_high, kl_low]
        splits['entropy_max'] = evaluate_split(partition_kl, data, real_metrics, depleted_pairs)
        splits['entropy_max']['split_sizes'] = [len(kl_high), len(kl_low)]
    else:
        print("    Could not split by KL (all same side)")

    # Summary
    print(f"\n  Summary of 7-state alternatives:")
    for name, result in splits.items():
        print(f"    {name:>20}: fidelity={result['fidelity']:.2f}, "
              f"gap={result['spectral_gap']:.4f}, "
              f"depl_z={result['comparison'].get('n_depleted', {}).get('z_score', '?')}")

    return splits


def evaluate_split(partition, data, real_metrics, depleted_pairs):
    """Evaluate a partition: fidelity, spectral gap, constraint retention, AIC/BIC."""
    all_classes = data['all_classes']
    counts_49 = data['counts_49']
    cls_to_idx = data['cls_to_idx']

    state_probs, _, _, _ = build_state_automaton(
        partition, counts_49, data['class_freq'], all_classes, cls_to_idx)
    gap = compute_spectral_gap(state_probs)
    retention = compute_constraint_retention(partition, all_classes, depleted_pairs, cls_to_idx)
    comparison, fidelity = run_fidelity_comparison(partition, data, real_metrics)

    ll = compute_log_likelihood(partition, counts_49, all_classes, cls_to_idx, data['class_freq'])
    k = len(partition)
    params = k * (k - 1) + (data['n_cls'] - k)
    n_trans = data['n_transitions']
    aic = 2 * params - 2 * ll
    bic = params * np.log(n_trans) - 2 * ll

    return {
        'k': k,
        'partition': [sorted(g) for g in partition],
        'spectral_gap': gap,
        'retention': retention,
        'fidelity': fidelity,
        'comparison': comparison,
        'log_likelihood': round(ll, 2),
        'aic': round(aic, 2),
        'bic': round(bic, 2),
    }


# =============================================================================
# T5: Independent Spectral Clustering (k=3..12)
# =============================================================================

def run_t5(data, real_metrics):
    """Spectral clustering directly on 49x49, independent of merge log."""
    print("\n" + "=" * 70)
    print("T5: Independent Spectral Clustering (k=3..12)")
    print("=" * 70)

    all_classes = data['all_classes']
    n_cls = data['n_cls']
    counts_49 = data['counts_49']
    cls_to_idx = data['cls_to_idx']
    jsd_matrix = data['jsd_matrix']
    depleted_pairs = data['depleted_pairs']

    # Build affinity matrix from JSD distances (computed ONCE)
    sigma = np.median(jsd_matrix[jsd_matrix > 0]) if np.any(jsd_matrix > 0) else 1.0
    affinity = np.exp(-jsd_matrix ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(affinity, 0)

    # Normalized Laplacian (computed ONCE)
    d_vec = affinity.sum(axis=1)
    d_inv_sqrt = 1.0 / np.sqrt(np.maximum(d_vec, 1e-15))
    L_norm = np.eye(n_cls) - np.outer(d_inv_sqrt, d_inv_sqrt) * affinity

    # Eigendecomposition (ONCE)
    eigvals, eigvecs = np.linalg.eigh(L_norm)

    results = {}
    for k in range(3, 13):
        print(f"\n  k={k}...")

        # Take first k eigenvectors
        V = eigvecs[:, :k].copy()
        # Normalize rows
        norms = np.linalg.norm(V, axis=1, keepdims=True)
        V = np.divide(V, norms, where=norms > 0, out=np.zeros_like(V))

        # K-means (best of 10 runs)
        best_labels = None
        best_inertia = float('inf')
        for trial in range(10):
            try:
                _, labels = kmeans2(V, k, minit='++', seed=42 + trial)
                # Compute inertia
                centroids = np.array([V[labels == i].mean(axis=0) for i in range(k)])
                inertia = sum(np.sum((V[labels == i] - centroids[i]) ** 2)
                              for i in range(k))
                if inertia < best_inertia:
                    best_inertia = inertia
                    best_labels = labels
            except Exception:
                continue

        if best_labels is None:
            print(f"    k-means failed at k={k}")
            continue

        # Convert labels to partition
        partition = []
        for si in range(k):
            group = {all_classes[i] for i in range(n_cls) if best_labels[i] == si}
            if group:
                partition.append(group)

        # Evaluate
        state_probs, _, _, _ = build_state_automaton(
            partition, counts_49, data['class_freq'], all_classes, cls_to_idx)
        gap = compute_spectral_gap(state_probs)
        retention = compute_constraint_retention(partition, all_classes, depleted_pairs, cls_to_idx)

        ll = compute_log_likelihood(partition, counts_49, all_classes, cls_to_idx, data['class_freq'])
        params = len(partition) * (len(partition) - 1) + (data['n_cls'] - len(partition))
        n_trans = data['n_transitions']
        aic = 2 * params - 2 * ll
        bic = params * np.log(n_trans) - 2 * ll

        # Compare partition to agglomerative (ARI)
        # Simple overlap metric: fraction of class pairs that agree
        agglom_partition = reconstruct_partition(
            data['merge_log'], min(k, len(data['merge_log']) + 6),
            n_cls, all_classes)
        ari = compute_ari(partition, agglom_partition, all_classes)

        print(f"    Actual states: {len(partition)}, Gap: {gap:.4f}, "
              f"ARI vs agglom: {ari:.3f}")
        print(f"    Retention: dep_cross={retention['depleted_cross_fraction']:.3f}, "
              f"fl_sep={retention['fl_separated']}, purity={retention['role_purity']:.3f}")
        print(f"    AIC: {aic:.1f}, BIC: {bic:.1f}")

        results[str(k)] = {
            'k': k,
            'actual_states': len(partition),
            'partition': [sorted(g) for g in partition],
            'spectral_gap': gap,
            'retention': retention,
            'log_likelihood': round(ll, 2),
            'aic': round(aic, 2),
            'bic': round(bic, 2),
            'ari_vs_agglomerative': round(ari, 4),
        }

    return results


def compute_ari(partition_a, partition_b, all_classes):
    """Compute Adjusted Rand Index between two partitions."""
    # Build label arrays
    label_a = {}
    for si, group in enumerate(partition_a):
        for c in group:
            label_a[c] = si
    label_b = {}
    for si, group in enumerate(partition_b):
        for c in group:
            label_b[c] = si

    # Contingency table
    n_a = len(partition_a)
    n_b = len(partition_b)
    contingency = np.zeros((n_a, n_b), dtype=int)
    for c in all_classes:
        if c in label_a and c in label_b:
            contingency[label_a[c]][label_b[c]] += 1

    # ARI computation
    n = contingency.sum()
    if n <= 1:
        return 0.0

    sum_comb_c = sum(math.comb(int(nij), 2) for nij in contingency.flatten())
    sum_comb_a = sum(math.comb(int(ai), 2) for ai in contingency.sum(axis=1))
    sum_comb_b = sum(math.comb(int(bj), 2) for bj in contingency.sum(axis=0))
    comb_n = math.comb(int(n), 2)

    expected = sum_comb_a * sum_comb_b / comb_n if comb_n > 0 else 0
    max_idx = (sum_comb_a + sum_comb_b) / 2
    denom = max_idx - expected
    if abs(denom) < 1e-15:
        return 1.0 if abs(sum_comb_c - expected) < 1e-15 else 0.0
    return float((sum_comb_c - expected) / denom)


# =============================================================================
# T6: Synthesis and Verdict
# =============================================================================

def run_t6(t1_results, t2_results, t3_results, t4_results, t5_results):
    """Synthesize all results into a structured verdict."""
    print("\n" + "=" * 70)
    print("T6: Synthesis and Verdict")
    print("=" * 70)

    # 1. Is 6 the constrained minimum? (from T3)
    k5_violations = t3_results.get('5', {}).get('total_violations', 0)
    k4_violations = t3_results.get('4', {}).get('total_violations', 0)
    k3_violations = t3_results.get('3', {}).get('total_violations', 0)
    constrained_minimum = k5_violations > 0  # Every k<6 breaks constraints

    # 2. Is 6 the IT optimum? (from T2)
    aic_min = t2_results['aic_minimum_k']
    bic_min = t2_results['bic_minimum_k']
    it_optimum_aic = aic_min == 6
    it_optimum_bic = bic_min == 6

    # 3. Does k>6 close the depletion gap? (from T1)
    dep_z_6 = t1_results.get('6', {}).get('comparison', {}).get('n_depleted', {}).get('z_score', None)
    dep_z_7 = t1_results.get('7', {}).get('comparison', {}).get('n_depleted', {}).get('z_score', None)
    dep_z_8 = t1_results.get('8', {}).get('comparison', {}).get('n_depleted', {}).get('z_score', None)

    depletion_closed_at_7 = dep_z_7 is not None and abs(dep_z_7) < 3
    depletion_closed_at_8 = dep_z_8 is not None and abs(dep_z_8) < 3

    # 4. Do alternative 7-state partitions help? (from T4)
    best_alt_fidelity = 0.0
    best_alt_name = None
    for name, result in t4_results.items():
        if result['fidelity'] > best_alt_fidelity:
            best_alt_fidelity = result['fidelity']
            best_alt_name = name

    # 5. Does independent clustering converge to 6? (from T5)
    spectral_6 = t5_results.get('6', {})
    spectral_ari = spectral_6.get('ari_vs_agglomerative', 0.0)
    spectral_retention = spectral_6.get('retention', {})
    independent_convergence = spectral_ari > 0.7

    # Determine verdict
    if constrained_minimum and (it_optimum_bic or aic_min <= 7):
        if not depletion_closed_at_7 and not depletion_closed_at_8:
            verdict = "STRUCTURALLY_FORCED"
            explanation = ("6 is minimal under constraints, BIC-optimal or near-optimal, "
                           "and upward refinement does not close the depletion gap")
        else:
            verdict = "SUFFICIENT_BUT_REFINABLE"
            explanation = ("6 is minimal under constraints, but k=7 or k=8 closes "
                           "the depletion gap — depletion is NOT purely class-level")
    elif not constrained_minimum:
        verdict = "ERROR_CONSTRAINTS_INSUFFICIENT"
        explanation = "k<6 does not break constraints — constraint set is incomplete"
    else:
        verdict = "COMPRESSION_SLIGHTLY_UNDERFIT"
        explanation = f"AIC prefers k={aic_min}, suggesting macro compression loses structure"

    print(f"\n  Constrained minimum at 6: {constrained_minimum}")
    print(f"  AIC minimum: k={aic_min}, BIC minimum: k={bic_min}")
    print(f"  Depletion z at k=6: {dep_z_6}, k=7: {dep_z_7}, k=8: {dep_z_8}")
    print(f"  Depletion closed at k=7: {depletion_closed_at_7}, k=8: {depletion_closed_at_8}")
    print(f"  Best alt 7-state: {best_alt_name} (fidelity={best_alt_fidelity:.2f})")
    print(f"  Spectral k=6 ARI: {spectral_ari:.3f}")
    print(f"  Independent convergence: {independent_convergence}")
    print(f"\n  *** VERDICT: {verdict} ***")
    print(f"  {explanation}")

    return {
        'constrained_minimum': constrained_minimum,
        'k5_violations': k5_violations,
        'k4_violations': k4_violations,
        'k3_violations': k3_violations,
        'aic_minimum_k': aic_min,
        'bic_minimum_k': bic_min,
        'it_optimum_aic': it_optimum_aic,
        'it_optimum_bic': it_optimum_bic,
        'depletion_z_6': dep_z_6,
        'depletion_z_7': dep_z_7,
        'depletion_z_8': dep_z_8,
        'depletion_closed_at_7': depletion_closed_at_7,
        'depletion_closed_at_8': depletion_closed_at_8,
        'best_alt_7state': best_alt_name,
        'best_alt_7state_fidelity': best_alt_fidelity,
        'spectral_k6_ari': spectral_ari,
        'independent_convergence': independent_convergence,
        'verdict': verdict,
        'explanation': explanation,
    }


# =============================================================================
# Main
# =============================================================================

def run():
    t_start = time.time()
    print("=" * 70)
    print("Phase 328: MACRO_AUTOMATON_NECESSITY")
    print("Is k=6 the minimal invariant-preserving macro abstraction?")
    print("=" * 70)

    # Load all shared data (ONCE)
    data = load_all_data()

    # Compute real corpus metrics (ONCE)
    print("\n[0b] Computing real corpus metrics...")
    real_metrics = compute_fidelity_metrics(data['real_lines'], data['all_classes'],
                                           data['cls_to_idx'])
    print(f"  Real metrics: {real_metrics}")

    # T1: k-sweep
    t1_results = run_t1(data, real_metrics)

    # T2: AIC/BIC (extracted from T1)
    t2_results = run_t2(t1_results)

    # T3: Constraint violations
    t3_results = run_t3(t1_results)

    # T4: Upward splits
    t4_results = run_t4(data, real_metrics)

    # T5: Independent spectral clustering
    t5_results = run_t5(data, real_metrics)

    # T6: Synthesis
    t6_results = run_t6(t1_results, t2_results, t3_results, t4_results, t5_results)

    # Save all results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        'phase': 'MACRO_AUTOMATON_NECESSITY',
        'phase_number': 328,
        'question': 'Is k=6 the minimal invariant-preserving macro abstraction?',
        'n_synthetic_per_k': N_SYNTHETIC,
        'real_metrics': real_metrics,
        't1_ksweep': t1_results,
        't2_information_criteria': t2_results,
        't3_constraint_violations': t3_results,
        't4_upward_splits': t4_results,
        't5_spectral_clustering': t5_results,
        't6_synthesis': t6_results,
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    with open(RESULTS_DIR / 'automaton_necessity.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 'automaton_necessity.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
