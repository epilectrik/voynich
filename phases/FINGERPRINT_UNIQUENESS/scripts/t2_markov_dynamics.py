#!/usr/bin/env python3
"""
T2: Markov Dynamics Null Model (F5, F6, F10)
FINGERPRINT_UNIQUENESS phase

Tests: Among random Markov chains on 49 states, how rare is:
  F5:  First-order Markov sufficiency (BIC 1st < BIC 2nd)
  F6:  1-token hazard gate (sharp KL drop at offset +2)
  F10: No cross-line memory (near-zero MI across line boundaries)

Three null ensembles:
  NULL-D: Density-matched Markov (transition matrices with observed sparsity)
  NULL-E: Uniform Markov (equal-probability transitions)
  NULL-F: Zipf-frequency Markov (rows weighted by Zipfian class frequencies)

Key note: The rare combination is F5 AND F6 AND F10 jointly.
First-order sufficiency alone may be common in sparse chains.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SAMPLES = 1000  # Each sample requires simulation + 2 BIC fits
RNG = np.random.default_rng(42)
GATE_KL_RATIO_THRESHOLD = 50  # KL(+1)/KL(+2) > this = "sharp gate"


# ============================================================
# DATA LOADING
# ============================================================

def load_class_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    all_classes = sorted(set(token_to_class.values()))
    return token_to_class, all_classes


def load_b_sequences():
    """Load Currier B as line-organized class sequences."""
    tx = Transcript()
    token_to_class, all_classes = load_class_map()
    n = len(all_classes)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}

    lines = []
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
                lines.append(current_seq)
            current_seq = []
            current_key = key
        current_seq.append(cls_to_idx[cls])

    if current_seq:
        lines.append(current_seq)

    return lines, all_classes, cls_to_idx


# ============================================================
# MARKOV MODEL FITTING
# ============================================================

def fit_first_order(sequences, n_states):
    """Fit first-order Markov model (vectorized). Returns (counts, ll, n_params, n_transitions)."""
    counts = np.zeros((n_states, n_states), dtype=float)
    for seq in sequences:
        if len(seq) < 2:
            continue
        s = np.array(seq)
        np.add.at(counts, (s[:-1], s[1:]), 1)

    alpha = 0.01
    smoothed = counts + alpha
    row_sums = smoothed.sum(axis=1, keepdims=True)
    probs = smoothed / np.where(row_sums > 0, row_sums, 1)

    ll = 0.0
    n_transitions = 0
    for seq in sequences:
        if len(seq) < 2:
            continue
        s = np.array(seq)
        ll += float(np.sum(np.log(probs[s[:-1], s[1:]])))
        n_transitions += len(seq) - 1

    active_rows = (counts.sum(axis=1) > 0).sum()
    n_params = active_rows * (n_states - 1)
    return counts, ll, n_params, n_transitions


def fit_second_order(sequences, n_states):
    """Fit second-order Markov model (vectorized). Returns (ll, n_params, n_transitions)."""
    counts = np.zeros((n_states, n_states, n_states), dtype=float)
    for seq in sequences:
        if len(seq) < 3:
            continue
        s = np.array(seq)
        np.add.at(counts, (s[:-2], s[1:-1], s[2:]), 1)

    alpha = 0.01
    smoothed = counts + alpha
    sums = smoothed.sum(axis=2, keepdims=True)
    probs = smoothed / np.where(sums > 0, sums, 1)

    ll = 0.0
    n_transitions = 0
    for seq in sequences:
        if len(seq) < 3:
            continue
        s = np.array(seq)
        ll += float(np.sum(np.log(probs[s[:-2], s[1:-1], s[2:]])))
        n_transitions += len(seq) - 2

    active_pairs = (counts.sum(axis=2) > 0).sum()
    n_params = active_pairs * (n_states - 1)
    return ll, n_params, n_transitions


def compute_bic_difference(sequences, n_states):
    """Compute BIC(1st) - BIC(2nd). Negative = 1st order preferred."""
    _, ll1, k1, n1 = fit_first_order(sequences, n_states)
    ll2, k2, n2 = fit_second_order(sequences, n_states)

    bic1 = -2 * ll1 + k1 * np.log(n1)
    bic2 = -2 * ll2 + k2 * np.log(n2)

    return bic1 - bic2, bic1, bic2  # Negative = 1st wins


# ============================================================
# HAZARD GATE ANALYSIS
# ============================================================

def compute_gate_kl_ratio(sequences, n_states, n_depleted_pairs=20):
    """After depleted transitions, measure KL divergence at offset +1 vs +2.

    Sharp gate: KL drops dramatically from +1 to +2.
    Returns KL(+1), KL(+2), and their ratio.
    """
    # Build transition matrix and find most depleted pairs
    counts = np.zeros((n_states, n_states), dtype=float)
    for seq in sequences:
        for i in range(len(seq) - 1):
            counts[seq[i]][seq[i + 1]] += 1

    row_sums = counts.sum(axis=1)
    grand = counts.sum()
    col_sums = counts.sum(axis=0)

    expected = np.outer(row_sums, col_sums) / grand if grand > 0 else np.zeros_like(counts)

    # Find depleted pairs (lowest obs/exp with enough expected)
    depleted = []
    for i in range(n_states):
        for j in range(n_states):
            if expected[i][j] >= 5:
                ratio = counts[i][j] / expected[i][j]
                depleted.append((ratio, i, j))
    depleted.sort()
    target_pairs = set((i, j) for _, i, j in depleted[:n_depleted_pairs])

    if not target_pairs:
        return 0.0, 0.0, 0.0

    # Get baseline distribution
    total = counts.sum()
    baseline = col_sums / total if total > 0 else np.ones(n_states) / n_states

    # After a depleted transition (i->j), measure distribution at offset +1 and +2
    offset1_counts = np.zeros(n_states)
    offset2_counts = np.zeros(n_states)

    for seq in sequences:
        for pos in range(len(seq) - 1):
            pair = (seq[pos], seq[pos + 1])
            if pair in target_pairs:
                if pos + 2 < len(seq):
                    offset1_counts[seq[pos + 2]] += 1
                if pos + 3 < len(seq):
                    offset2_counts[seq[pos + 3]] += 1

    # KL divergence
    def kl_div(p, q):
        p = p / p.sum() if p.sum() > 0 else np.ones_like(p) / len(p)
        q = np.clip(q, 1e-10, None)
        q = q / q.sum()
        return float(np.sum(p * np.log(p / q + 1e-15)))

    kl1 = kl_div(offset1_counts, baseline) if offset1_counts.sum() > 10 else 0.0
    kl2 = kl_div(offset2_counts, baseline) if offset2_counts.sum() > 10 else 0.0

    ratio = kl1 / kl2 if kl2 > 1e-6 else (float('inf') if kl1 > 0 else 0.0)

    return kl1, kl2, ratio


# ============================================================
# CROSS-LINE MI
# ============================================================

def compute_cross_line_mi(sequences, n_states):
    """Mutual information between last token of line N and first token of line N+1.

    C360/C966: Grammar is line-invariant, no cross-line memory.
    """
    joint = np.zeros((n_states, n_states), dtype=float)
    last_margin = np.zeros(n_states)
    first_margin = np.zeros(n_states)

    for i in range(len(sequences) - 1):
        if len(sequences[i]) == 0 or len(sequences[i + 1]) == 0:
            continue
        last = sequences[i][-1]
        first = sequences[i + 1][0]
        joint[last][first] += 1
        last_margin[last] += 1
        first_margin[first] += 1

    total = joint.sum()
    if total == 0:
        return 0.0

    mi = 0.0
    for a in range(n_states):
        for b in range(n_states):
            if joint[a][b] > 0:
                p_ab = joint[a][b] / total
                p_a = last_margin[a] / total
                p_b = first_margin[b] / total
                if p_a > 0 and p_b > 0:
                    mi += p_ab * np.log2(p_ab / (p_a * p_b))

    return float(mi)


# ============================================================
# COMPOSITE FINGERPRINT
# ============================================================

def compute_fingerprint(sequences, n_states):
    bic_diff, bic1, bic2 = compute_bic_difference(sequences, n_states)
    kl1, kl2, kl_ratio = compute_gate_kl_ratio(sequences, n_states)
    cross_mi = compute_cross_line_mi(sequences, n_states)

    return {
        'bic_diff': float(bic_diff),
        'bic1': float(bic1),
        'bic2': float(bic2),
        'first_order_wins': bool(bic_diff < 0),
        'kl_offset1': float(kl1),
        'kl_offset2': float(kl2),
        'kl_ratio': float(kl_ratio),
        'has_sharp_gate': bool(kl_ratio > GATE_KL_RATIO_THRESHOLD),
        'cross_line_mi': float(cross_mi),
    }


# ============================================================
# NULL GENERATORS: Simulate from random Markov chains
# ============================================================

def simulate_markov(trans_matrix, line_lengths, rng, n_states):
    """Simulate sequences from a Markov chain with line-boundary resets (vectorized)."""
    row_sums = trans_matrix.sum(axis=1)
    stationary = row_sums / row_sums.sum() if row_sums.sum() > 0 else np.ones(n_states) / n_states

    # Pre-compute cumulative probabilities for fast sampling
    cum_probs = np.cumsum(trans_matrix / np.where(row_sums[:, None] > 0,
                                                   row_sums[:, None], 1), axis=1)
    cum_stat = np.cumsum(stationary)

    max_len = max(line_lengths) if line_lengths else 0
    # Pre-generate all random numbers at once
    total_tokens = sum(line_lengths)
    all_randoms = rng.random(total_tokens)

    sequences = []
    r_idx = 0
    for length in line_lengths:
        if length == 0:
            sequences.append([])
            continue
        seq = np.empty(length, dtype=np.int32)
        seq[0] = np.searchsorted(cum_stat, all_randoms[r_idx])
        r_idx += 1
        for t in range(1, length):
            seq[t] = np.searchsorted(cum_probs[seq[t - 1]], all_randoms[r_idx])
            r_idx += 1
        # Clip to valid range
        np.clip(seq, 0, n_states - 1, out=seq)
        sequences.append(seq.tolist())
    return sequences


def make_density_matched_matrix(n_states, zero_frac, rng):
    """NULL-D: Random Markov matrix with matched zero-fraction per row."""
    mat = np.zeros((n_states, n_states))
    n_nonzero = max(1, int(round(n_states * (1 - zero_frac))))
    for i in range(n_states):
        cols = rng.choice(n_states, size=n_nonzero, replace=False)
        probs = rng.dirichlet(np.ones(n_nonzero))
        for c, j in enumerate(cols):
            mat[i][j] = probs[c]
    return mat


def make_uniform_matrix(n_states):
    """NULL-E: Uniform transition matrix."""
    return np.ones((n_states, n_states)) / n_states


def make_zipf_matrix(n_states, rng):
    """NULL-F: Zipf-frequency weighted matrix.
    Each row has probabilities proportional to Zipfian column weights.
    """
    # Zipf weights for columns
    ranks = np.arange(1, n_states + 1, dtype=float)
    zipf_weights = 1.0 / ranks
    zipf_weights /= zipf_weights.sum()

    mat = np.zeros((n_states, n_states))
    for i in range(n_states):
        # Add Dirichlet noise to Zipf base
        noise = rng.dirichlet(np.ones(n_states) * 0.5)
        probs = 0.7 * zipf_weights + 0.3 * noise
        probs /= probs.sum()
        mat[i] = probs
    return mat


# ============================================================
# MAIN
# ============================================================

def run():
    t_start = time.time()
    print("=" * 70)
    print("T2: Markov Dynamics Null Model (F5, F6, F10)")
    print("FINGERPRINT_UNIQUENESS phase")
    print("=" * 70)

    # 1. Load data
    print("\n[1/5] Loading data...")
    sequences, all_classes, cls_to_idx = load_b_sequences()
    n_states = len(all_classes)
    line_lengths = [len(s) for s in sequences]
    print(f"  States: {n_states}")
    print(f"  Lines: {len(sequences)}")
    print(f"  Mean line length: {np.mean(line_lengths):.1f}")
    print(f"  Total tokens: {sum(line_lengths)}")

    # Compute zero fraction for density-matched null
    counts1, _, _, _ = fit_first_order(sequences, n_states)
    zero_frac = float((counts1 == 0).sum()) / (n_states * n_states)
    print(f"  Transition matrix zero fraction: {zero_frac:.3f}")

    # 2. Observed fingerprint
    print("\n[2/5] Computing observed fingerprint...")
    obs = compute_fingerprint(sequences, n_states)

    print(f"  F5  - BIC difference: {obs['bic_diff']:.1f} "
          f"({'1st wins' if obs['first_order_wins'] else '2nd wins'})")
    print(f"  F6  - KL(+1)={obs['kl_offset1']:.4f}, KL(+2)={obs['kl_offset2']:.4f}, "
          f"ratio={obs['kl_ratio']:.1f}x")
    print(f"        Sharp gate: {obs['has_sharp_gate']}")
    print(f"  F10 - Cross-line MI: {obs['cross_line_mi']:.6f} bits")

    # 3-5. Null ensembles
    ensemble_results = {}
    generators = [
        ('NULL_D_density', lambda rng: make_density_matched_matrix(n_states, zero_frac, rng)),
        ('NULL_E_uniform', lambda rng: make_uniform_matrix(n_states)),
        ('NULL_F_zipf', lambda rng: make_zipf_matrix(n_states, rng)),
    ]

    for step, (label, mat_fn) in enumerate(generators, 3):
        print(f"\n[{step}/5] Running {label} ({N_SAMPLES} samples)...")
        t_ens = time.time()

        null_bic = np.zeros(N_SAMPLES)
        null_gate = np.zeros(N_SAMPLES, dtype=bool)
        null_mi = np.zeros(N_SAMPLES)
        null_kl_ratio = np.zeros(N_SAMPLES)

        for s in range(N_SAMPLES):
            mat = mat_fn(RNG)
            sim_seqs = simulate_markov(mat, line_lengths, RNG, n_states)
            fp = compute_fingerprint(sim_seqs, n_states)
            null_bic[s] = fp['bic_diff']
            null_gate[s] = fp['has_sharp_gate']
            null_mi[s] = fp['cross_line_mi']
            null_kl_ratio[s] = min(fp['kl_ratio'], 1000)  # Cap for stats

            if (s + 1) % 200 == 0:
                elapsed = time.time() - t_ens
                rate = (s + 1) / elapsed
                print(f"    {s + 1}/{N_SAMPLES} ({rate:.1f}/s, "
                      f"ETA {(N_SAMPLES - s - 1) / rate:.0f}s)")

        dt = time.time() - t_ens

        # P-values
        # F5: first-order wins = BIC diff < 0
        p_first_order = float(np.mean(null_bic < 0)) if obs['first_order_wins'] else float(
            np.mean(null_bic >= 0))
        # F6: sharp gate
        p_gate = float(np.mean(null_gate))
        # F10: low cross-line MI (MI <= observed)
        p_mi = float(np.mean(null_mi <= obs['cross_line_mi']))

        # Joint: first order wins AND sharp gate AND low MI
        if obs['first_order_wins']:
            joint_mask = (null_bic < 0) & null_gate & (null_mi <= obs['cross_line_mi'])
        else:
            joint_mask = np.zeros(N_SAMPLES, dtype=bool)
        p_joint = float(np.mean(joint_mask))

        ensemble_results[label] = {
            'p_first_order_wins': p_first_order,
            'p_sharp_gate': p_gate,
            'p_low_cross_mi': p_mi,
            'p_joint_F5_F6_F10': p_joint,
            'null_bic_mean': round(float(np.mean(null_bic)), 1),
            'null_bic_std': round(float(np.std(null_bic)), 1),
            'null_first_order_fraction': round(float(np.mean(null_bic < 0)), 4),
            'null_gate_fraction': round(float(np.mean(null_gate)), 4),
            'null_mi_mean': round(float(np.mean(null_mi)), 6),
            'null_mi_std': round(float(np.std(null_mi)), 6),
            'time_seconds': round(dt, 1),
        }

        print(f"  Completed in {dt:.1f}s")
        print(f"  P(1st order wins): {p_first_order:.4f} "
              f"[{np.mean(null_bic < 0):.1%} of nulls have 1st-order BIC win]")
        print(f"  P(sharp gate): {p_gate:.4f}")
        print(f"  P(MI <= {obs['cross_line_mi']:.6f}): {p_mi:.4f} "
              f"[null MI: {np.mean(null_mi):.6f}]")
        print(f"  P(joint F5 AND F6 AND F10): {p_joint:.6f}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nObserved fingerprint:")
    print(f"  F5  BIC diff:        {obs['bic_diff']:.1f} "
          f"({'1st wins' if obs['first_order_wins'] else '2nd wins'})")
    print(f"  F6  Gate KL ratio:   {obs['kl_ratio']:.1f}x "
          f"(sharp={obs['has_sharp_gate']})")
    print(f"  F10 Cross-line MI:   {obs['cross_line_mi']:.6f} bits")

    print(f"\nPer-ensemble joint p-values:")
    for label, res in ensemble_results.items():
        print(f"  {label}: {res['p_joint_F5_F6_F10']:.6f}")

    best_p = min(r['p_joint_F5_F6_F10'] for r in ensemble_results.values())
    worst_p = max(r['p_joint_F5_F6_F10'] for r in ensemble_results.values())

    if worst_p < 0.01:
        verdict = "RARE"
    elif worst_p < 0.05:
        verdict = "UNCOMMON"
    else:
        verdict = "NOT_RARE"
    print(f"\nT2 Verdict (worst-case p = {worst_p:.6f}): {verdict}")

    # Save
    results = {
        'test': 'T2_markov_dynamics',
        'properties': ['F5_first_order_sufficiency', 'F6_1_token_gate', 'F10_no_cross_line'],
        'observed': {
            'bic_diff': obs['bic_diff'],
            'bic1': obs['bic1'],
            'bic2': obs['bic2'],
            'first_order_wins': obs['first_order_wins'],
            'kl_offset1': obs['kl_offset1'],
            'kl_offset2': obs['kl_offset2'],
            'kl_ratio': min(obs['kl_ratio'], 1e6),
            'has_sharp_gate': obs['has_sharp_gate'],
            'cross_line_mi': obs['cross_line_mi'],
        },
        'ensembles': ensemble_results,
        'verdict': verdict,
        'best_joint_p': best_p,
        'worst_joint_p': worst_p,
        'n_samples': N_SAMPLES,
        'n_states': n_states,
        'n_lines': len(sequences),
        'mean_line_length': round(float(np.mean(line_lengths)), 1),
        'transition_zero_frac': round(zero_frac, 4),
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't2_dynamics.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Total time: {time.time() - t_start:.1f}s")

    return results


if __name__ == '__main__':
    run()
