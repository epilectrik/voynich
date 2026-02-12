#!/usr/bin/env python3
"""
T4: Synthetic Generation from Minimal Automaton
MINIMAL_STATE_AUTOMATON phase

Generate 1000 synthetic corpora from the 6-state automaton.
Compare against real Voynich B on key corpus-level statistics.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SAMPLES = 1000
RNG = np.random.default_rng(42)


def build_automaton(t1, t3):
    """Build 6-state automaton from T1 transition data and T3 partition."""
    all_classes = t1['classes']
    counts = np.array(t1['counts_49x49'], dtype=float)
    partition = t3['final_partition']  # list of lists of class IDs
    n_states = len(partition)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}

    # Map class → state
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # Build state-level transition matrix
    state_counts = np.zeros((n_states, n_states), dtype=float)
    for ci, c in enumerate(all_classes):
        for cj, d in enumerate(all_classes):
            si, sj = cls_to_state[c], cls_to_state[d]
            state_counts[si][sj] += counts[ci][cj]

    row_sums = state_counts.sum(axis=1, keepdims=True)
    state_probs = np.divide(state_counts, row_sums, where=row_sums > 0,
                            out=np.zeros_like(state_counts))

    # Build class emission probabilities within each state
    # P(class | state) proportional to class frequency
    emission = np.zeros((n_states, len(all_classes)))
    for ci, c in enumerate(all_classes):
        si = cls_to_state[c]
        emission[si][ci] = t1['class_details'][str(c)]['frequency']

    emission_sums = emission.sum(axis=1, keepdims=True)
    emission = np.divide(emission, emission_sums, where=emission_sums > 0,
                         out=np.zeros_like(emission))

    # Initial state distribution (from marginal frequencies)
    state_freqs = np.array([sum(t1['class_details'][str(c)]['frequency'] for c in group)
                            for group in partition], dtype=float)
    initial = state_freqs / state_freqs.sum()

    return state_probs, emission, initial, cls_to_state


def simulate_corpus(state_probs, emission, initial, line_lengths, all_classes, rng):
    """Generate one synthetic corpus from the automaton."""
    n_states = len(state_probs)
    n_classes = len(all_classes)
    cum_state = np.cumsum(state_probs, axis=1)
    cum_emit = np.cumsum(emission, axis=1)
    cum_init = np.cumsum(initial)

    lines = []
    for length in line_lengths:
        if length == 0:
            lines.append([])
            continue
        seq = []
        # Initial state
        state = np.searchsorted(cum_init, rng.random())
        state = min(state, n_states - 1)
        for _ in range(length):
            # Emit class from state
            cls_idx = np.searchsorted(cum_emit[state], rng.random())
            cls_idx = min(cls_idx, n_classes - 1)
            seq.append(all_classes[cls_idx])
            # Transition to next state
            state = np.searchsorted(cum_state[state], rng.random())
            state = min(state, n_states - 1)
        lines.append(seq)
    return lines


def compute_metrics(lines, all_classes, cls_to_idx):
    """Compute corpus-level metrics for comparison."""
    # Zipf: class frequency distribution
    class_freq = Counter()
    for seq in lines:
        for c in seq:
            class_freq[c] += 1
    freqs = sorted(class_freq.values(), reverse=True)
    if len(freqs) >= 2:
        log_ranks = np.log(np.arange(1, len(freqs) + 1))
        log_freqs = np.log(np.array(freqs, dtype=float))
        # Zipf exponent: slope of log-log fit
        if len(log_ranks) > 1:
            zipf_slope = float(np.polyfit(log_ranks, log_freqs, 1)[0])
        else:
            zipf_slope = 0.0
    else:
        zipf_slope = 0.0

    # Transition counts
    n = len(all_classes)
    counts = np.zeros((n, n), dtype=float)
    for seq in lines:
        for i in range(len(seq) - 1):
            a, b = cls_to_idx[seq[i]], cls_to_idx[seq[i + 1]]
            counts[a][b] += 1

    # Depleted pairs (obs/exp < 0.2, expected >= 5)
    row_sums = counts.sum(axis=1)
    col_sums = counts.sum(axis=0)
    total = counts.sum()
    expected = np.outer(row_sums, col_sums) / total if total > 0 else np.zeros_like(counts)

    n_depleted = 0
    n_asym = 0
    for i in range(n):
        for j in range(n):
            if expected[i][j] >= 5:
                ratio = counts[i][j] / expected[i][j]
                if ratio < 0.2:
                    n_depleted += 1
                    # Check reverse
                    if expected[j][i] >= 5:
                        rev_ratio = counts[j][i] / expected[j][i]
                        if rev_ratio >= 0.2:
                            n_asym += 1

    asymmetry = n_asym / n_depleted if n_depleted > 0 else 0.0

    # Cross-line MI
    n_cls = len(all_classes)
    joint = np.zeros((n_cls, n_cls), dtype=float)
    last_margin = np.zeros(n_cls)
    first_margin = np.zeros(n_cls)

    for i in range(len(lines) - 1):
        if len(lines[i]) == 0 or len(lines[i + 1]) == 0:
            continue
        last = cls_to_idx[lines[i][-1]]
        first = cls_to_idx[lines[i + 1][0]]
        joint[last][first] += 1
        last_margin[last] += 1
        first_margin[first] += 1

    total_j = joint.sum()
    cross_mi = 0.0
    if total_j > 0:
        for a in range(n_cls):
            for b in range(n_cls):
                if joint[a][b] > 0:
                    p_ab = joint[a][b] / total_j
                    p_a = last_margin[a] / total_j
                    p_b = first_margin[b] / total_j
                    if p_a > 0 and p_b > 0:
                        cross_mi += p_ab * np.log2(p_ab / (p_a * p_b))

    return {
        'zipf_slope': zipf_slope,
        'n_depleted': n_depleted,
        'asymmetry': asymmetry,
        'cross_line_mi': cross_mi,
        'n_active_classes': len(class_freq),
    }


def run():
    t_start = time.time()
    print("=" * 70)
    print("T4: Synthetic Generation from Minimal Automaton")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load data
    print("\n[1/4] Loading data...")
    with open(RESULTS_DIR / 't1_transition_data.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't3_merged_automaton.json') as f:
        t3 = json.load(f)

    all_classes = t1['classes']
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    line_lengths = t1['line_lengths']
    print(f"  {len(all_classes)} classes, {len(line_lengths)} lines")
    print(f"  Automaton: {t3['n_final_states']} states")

    # Build automaton
    print("\n[2/4] Building automaton...")
    state_probs, emission, initial, cls_to_state = build_automaton(t1, t3)
    print(f"  State transition matrix:")
    for si in range(len(state_probs)):
        row = " ".join(f"{state_probs[si][sj]:.3f}" for sj in range(len(state_probs)))
        print(f"    S{si}: [{row}]")

    # Compute real corpus metrics
    print("\n[3/4] Computing real corpus metrics...")
    tx = Transcript()
    real_lines = []
    current_key = None
    current_seq = []
    token_to_class = {}
    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    for t, c in ctm['token_to_class'].items():
        token_to_class[t] = int(c)

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

    real_metrics = compute_metrics(real_lines, all_classes, cls_to_idx)
    print(f"  Real corpus:")
    print(f"    Zipf slope: {real_metrics['zipf_slope']:.3f}")
    print(f"    Depleted pairs: {real_metrics['n_depleted']}")
    print(f"    Asymmetry: {real_metrics['asymmetry']:.3f}")
    print(f"    Cross-line MI: {real_metrics['cross_line_mi']:.4f} bits")
    print(f"    Active classes: {real_metrics['n_active_classes']}")

    # Generate synthetic corpora
    print(f"\n[4/4] Generating {N_SAMPLES} synthetic corpora...")
    t0 = time.time()
    syn_metrics = {k: [] for k in real_metrics.keys()}

    for s in range(N_SAMPLES):
        syn_lines = simulate_corpus(state_probs, emission, initial,
                                    line_lengths, all_classes, RNG)
        m = compute_metrics(syn_lines, all_classes, cls_to_idx)
        for k, v in m.items():
            syn_metrics[k].append(v)

        if (s + 1) % 200 == 0:
            elapsed = time.time() - t0
            rate = (s + 1) / elapsed
            print(f"    {s+1}/{N_SAMPLES} ({rate:.1f}/s)")

    dt = time.time() - t0
    print(f"  Generated {N_SAMPLES} corpora in {dt:.1f}s")

    # Compare
    print(f"\n{'='*70}")
    print(f"COMPARISON: Real vs Synthetic ({N_SAMPLES} samples)")
    print(f"{'='*70}")

    comparison = {}
    for metric, real_val in real_metrics.items():
        syn_arr = np.array(syn_metrics[metric])
        syn_mean = float(np.mean(syn_arr))
        syn_std = float(np.std(syn_arr))
        # Deviation in standard deviations
        z_score = (real_val - syn_mean) / syn_std if syn_std > 0 else 0.0
        # P-value (fraction of synthetics more extreme than real)
        if metric in ['n_depleted', 'asymmetry']:
            p = float(np.mean(syn_arr >= real_val))
        elif metric in ['cross_line_mi']:
            p = float(np.mean(syn_arr <= real_val))
        else:
            p = float(np.mean(np.abs(syn_arr - syn_mean) >= abs(real_val - syn_mean)))

        comparison[metric] = {
            'real': round(float(real_val), 4),
            'syn_mean': round(syn_mean, 4),
            'syn_std': round(syn_std, 4),
            'z_score': round(z_score, 2),
            'p_value': round(p, 4),
            'match': bool(abs(z_score) < 3),
        }
        status = "MATCH" if abs(z_score) < 3 else "MISMATCH"
        print(f"  {metric:>20}: real={real_val:>8.3f}  syn={syn_mean:>8.3f} +/- {syn_std:.3f}  "
              f"z={z_score:>+6.1f}  [{status}]")

    n_match = sum(1 for v in comparison.values() if v['match'])
    n_total = len(comparison)
    fidelity = n_match / n_total

    print(f"\n  Fidelity: {n_match}/{n_total} metrics match ({fidelity:.0%})")

    if fidelity >= 0.8:
        gen_verdict = "HIGH_FIDELITY"
    elif fidelity >= 0.5:
        gen_verdict = "PARTIAL_FIDELITY"
    else:
        gen_verdict = "LOW_FIDELITY"
    print(f"  Generation verdict: {gen_verdict}")

    # Save
    results = {
        'test': 'T4_synthetic_generation',
        'n_states': t3['n_final_states'],
        'n_samples': N_SAMPLES,
        'real_metrics': {k: round(float(v), 6) for k, v in real_metrics.items()},
        'comparison': comparison,
        'fidelity': round(fidelity, 4),
        'generation_verdict': gen_verdict,
        'state_transition_matrix': state_probs.tolist(),
        'initial_distribution': initial.tolist(),
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    with open(RESULTS_DIR / 't4_synthetic.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't4_synthetic.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
