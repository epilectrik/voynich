#!/usr/bin/env python3
"""
T2: Spectral Analysis — Effective Dimensionality
MINIMAL_STATE_AUTOMATON phase

Eigendecomposition of 49x49 transition matrix. NMF at varying ranks.
Determines effective state count from spectral structure.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from sklearn.decomposition import NMF

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def run():
    t_start = time.time()
    print("=" * 70)
    print("T2: Spectral Analysis — Effective Dimensionality")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load T1 data
    print("\n[1/4] Loading transition data...")
    with open(RESULTS_DIR / 't1_transition_data.json') as f:
        t1 = json.load(f)

    P = np.array(t1['probs_49x49'])
    counts = np.array(t1['counts_49x49'])
    n = len(t1['classes'])
    print(f"  {n}x{n} transition matrix loaded")

    # Eigendecomposition
    print("\n[2/4] Eigendecomposition...")
    eigvals, eigvecs = np.linalg.eig(P)

    # Sort by magnitude (descending)
    idx_sorted = np.argsort(-np.abs(eigvals))
    eigvals_sorted = eigvals[idx_sorted]
    magnitudes = np.abs(eigvals_sorted)

    print(f"  Top 15 eigenvalue magnitudes:")
    for i in range(min(15, n)):
        cumulative = np.sum(magnitudes[:i + 1]) / np.sum(magnitudes)
        print(f"    λ_{i+1:>2}: |{magnitudes[i]:.4f}|  (complex: {eigvals_sorted[i].imag:.4f}i)  "
              f"cumulative: {cumulative:.3f}")

    # Spectral gap analysis
    gaps = magnitudes[:-1] - magnitudes[1:]
    max_gap_idx = np.argmax(gaps[1:]) + 1  # Skip λ₁=1 gap
    print(f"\n  Largest spectral gap (after λ₁): between λ_{max_gap_idx+1} and λ_{max_gap_idx+2}")
    print(f"    Gap size: {gaps[max_gap_idx]:.4f}")
    print(f"    Suggests ~{max_gap_idx + 1} effective states")

    # Effective rank at various thresholds
    thresholds = [0.1, 0.05, 0.01, 0.005]
    print(f"\n  Effective rank at different thresholds:")
    effective_ranks = {}
    for thresh in thresholds:
        rank = int(np.sum(magnitudes > thresh))
        effective_ranks[str(thresh)] = rank
        print(f"    |λ| > {thresh}: rank = {rank}")

    # Cumulative energy at key state counts
    print(f"\n  Cumulative spectral energy:")
    energy_total = np.sum(magnitudes)
    for k in [3, 5, 7, 8, 10, 12, 15, 20]:
        if k <= n:
            energy_k = np.sum(magnitudes[:k]) / energy_total
            print(f"    k={k:>2}: {energy_k:.3f}")

    # NMF analysis
    print("\n[3/4] NMF reconstruction error analysis...")
    # Use count matrix (non-negative) for NMF
    counts_norm = counts.astype(float)
    row_sums = counts_norm.sum(axis=1, keepdims=True)
    counts_norm = np.divide(counts_norm, row_sums, where=row_sums > 0,
                            out=np.zeros_like(counts_norm))

    nmf_errors = {}
    for k in range(2, 16):
        model = NMF(n_components=k, max_iter=500, random_state=42)
        W = model.fit_transform(counts_norm)
        H = model.components_
        recon = W @ H
        error = float(np.linalg.norm(counts_norm - recon, 'fro'))
        rel_error = error / float(np.linalg.norm(counts_norm, 'fro'))
        nmf_errors[k] = {'absolute': round(error, 4), 'relative': round(rel_error, 4)}
        print(f"    k={k:>2}: relative error = {rel_error:.4f}")

    # Find NMF elbow (largest decrease in error)
    ks = sorted(nmf_errors.keys())
    error_deltas = []
    for i in range(1, len(ks)):
        delta = nmf_errors[ks[i - 1]]['relative'] - nmf_errors[ks[i]]['relative']
        error_deltas.append((ks[i], delta))
    error_deltas.sort(key=lambda x: -x[1])
    nmf_elbow = error_deltas[0][0]
    print(f"\n  NMF elbow at k={nmf_elbow} (biggest error reduction from k={nmf_elbow-1})")

    # Role-level comparison
    print("\n[4/4] Role-level (5x5) spectral comparison...")
    P_role = np.array(t1['role_probs_5x5'])
    eigvals_role = np.linalg.eigvals(P_role)
    mags_role = sorted(np.abs(eigvals_role), reverse=True)
    print(f"  Role eigenvalues: {', '.join(f'{m:.4f}' for m in mags_role)}")
    print(f"  Role effective rank (>0.01): {sum(1 for m in mags_role if m > 0.01)}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  49x49 eigenspectrum:")
    print(f"    Spectral gap suggests: ~{max_gap_idx + 1} effective states")
    print(f"    Effective rank (>0.01): {effective_ranks['0.01']}")
    print(f"    NMF elbow: k={nmf_elbow}")
    print(f"\n  5x5 role matrix: {sum(1 for m in mags_role if m > 0.01)} effective states")
    print(f"\n  Roles capture {'much' if effective_ranks['0.01'] <= 8 else 'some'} of the structure")

    # Save
    results = {
        'test': 'T2_spectral_analysis',
        'eigenvalues': [{'magnitude': round(float(magnitudes[i]), 6),
                         'real': round(float(eigvals_sorted[i].real), 6),
                         'imag': round(float(eigvals_sorted[i].imag), 6)}
                        for i in range(n)],
        'spectral_gap': {
            'position': int(max_gap_idx + 1),
            'gap_size': round(float(gaps[max_gap_idx]), 6),
            'suggested_states': int(max_gap_idx + 1),
        },
        'effective_rank': effective_ranks,
        'nmf_errors': {str(k): v for k, v in nmf_errors.items()},
        'nmf_elbow': nmf_elbow,
        'role_eigenvalues': [round(float(m), 6) for m in mags_role],
        'role_effective_rank': sum(1 for m in mags_role if m > 0.01),
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    with open(RESULTS_DIR / 't2_spectral.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't2_spectral.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
