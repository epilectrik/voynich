#!/usr/bin/env python3
"""
T1: Definitive Incompatibility Matrix & Eigenspectrum
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Build the complete MIDDLE incompatibility matrix from Currier A line-level
co-occurrence (C475 basis). Compute the full eigenspectrum and compare to
random matrix theory (Marchenko-Pastur) to establish a noise floor.

Key questions:
- How many eigenvalues exceed the random matrix noise floor?
- Is the eigenvalue spectrum truly flat, or does it have structure?
- What is the matrix rank at various numerical thresholds?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def build_incompatibility_matrix():
    """Build binary compatibility matrix from Currier A line-level co-occurrence."""
    tx = Transcript()
    morph = Morphology()

    # Collect MIDDLEs per line (Currier A only, H-track, labels excluded)
    line_middles = defaultdict(set)
    all_middles_set = set()

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            key = (token.folio, token.line)
            line_middles[key].add(m.middle)
            all_middles_set.add(m.middle)

    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    n = len(all_middles)

    print(f"  Unique MIDDLEs: {n}")
    print(f"  Lines with MIDDLEs: {len(line_middles)}")

    # Build binary compatibility matrix (1 = co-occurred, 0 = never co-occurred)
    compat = np.zeros((n, n), dtype=np.int8)
    np.fill_diagonal(compat, 1)

    for key, middles in line_middles.items():
        mid_list = [m for m in middles if m in mid_to_idx]
        for i in range(len(mid_list)):
            for j in range(i + 1, len(mid_list)):
                a, b = mid_to_idx[mid_list[i]], mid_to_idx[mid_list[j]]
                compat[a, b] = 1
                compat[b, a] = 1

    n_pairs = n * (n - 1) // 2
    n_compat = (compat.sum() - n) // 2  # exclude diagonal
    n_incompat = n_pairs - n_compat
    pct_incompat = 100 * n_incompat / n_pairs

    print(f"  Total pairs: {n_pairs}")
    print(f"  Compatible: {n_compat} ({100 * n_compat / n_pairs:.1f}%)")
    print(f"  Incompatible: {n_incompat} ({pct_incompat:.1f}%)")

    # Degree distribution
    degrees = compat.sum(axis=1) - 1  # exclude self
    print(f"  Degree range: {degrees.min()} - {degrees.max()}")
    print(f"  Mean degree: {degrees.mean():.1f}")
    print(f"  Median degree: {np.median(degrees):.0f}")

    # Identify known hubs
    known_hubs = ['a', 'o', 'e', 'ee', 'eo']
    hub_degrees = {h: int(degrees[mid_to_idx[h]]) for h in known_hubs if h in mid_to_idx}
    print(f"  Hub degrees: {hub_degrees}")

    return compat, all_middles, mid_to_idx, degrees


def full_eigenspectrum(compat):
    """Compute full eigendecomposition of compatibility matrix."""
    n = compat.shape[0]
    print(f"\n  Computing full eigendecomposition ({n}x{n})...")

    # Use float64 for numerical stability
    M = compat.astype(np.float64)

    # Symmetric matrix -> use eigh
    eigenvalues, eigenvectors = np.linalg.eigh(M)

    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    print(f"  Top 10 eigenvalues: {eigenvalues[:10].round(2)}")
    print(f"  Sum of eigenvalues: {eigenvalues.sum():.1f} (should = trace = {n})")

    # Positive eigenvalues
    n_positive = (eigenvalues > 0).sum()
    n_negative = (eigenvalues < 0).sum()
    print(f"  Positive eigenvalues: {n_positive}")
    print(f"  Negative eigenvalues: {n_negative}")

    return eigenvalues, eigenvectors


def marchenko_pastur_comparison(eigenvalues, compat):
    """Compare eigenvalue distribution to Marchenko-Pastur (random matrix theory).

    For a random binary matrix with density p, the bulk eigenvalue distribution
    follows a shifted/scaled MP law. Eigenvalues exceeding the MP upper bound
    represent genuine structure.
    """
    n = compat.shape[0]
    p = (compat.sum() - n) / (n * (n - 1))  # density (compatibility rate)

    print(f"\n  Matrix density (compatibility rate): {p:.4f}")

    # For Erdos-Renyi random graph with edge probability p:
    # Expected largest eigenvalue ≈ np + sqrt(np(1-p))
    # Bulk eigenvalues concentrate in [-2*sqrt(np(1-p)), 2*sqrt(np(1-p))] around 0
    # (after centering by removing the mean)

    mean_degree = p * (n - 1)
    std_degree = np.sqrt(p * (1 - p) * (n - 1))

    # MP upper bound for centered adjacency matrix
    # λ_bulk_max ≈ 2 * sqrt(np(1-p))
    mp_upper = 2 * np.sqrt(n * p * (1 - p))

    # The leading eigenvalue of a random graph with density p is ≈ np
    # (mean degree), then the next eigenvalues are O(sqrt(n))
    expected_leading = n * p
    print(f"  Expected leading eigenvalue (random): {expected_leading:.1f}")
    print(f"  Actual leading eigenvalue: {eigenvalues[0]:.1f}")
    print(f"  MP bulk upper bound (centered): {mp_upper:.1f}")

    # Center the matrix and check
    centered_eigs = eigenvalues - p  # rough centering
    n_above_mp = (eigenvalues > expected_leading + mp_upper).sum()

    # More precise: use permutation test
    # Generate random binary matrices with same density, compute top eigenvalues
    print(f"\n  Running permutation test (100 random matrices)...")
    random_max_eigs = []
    np.random.seed(42)
    for trial in range(100):
        # Random symmetric binary matrix with same density
        R = np.random.random((n, n)) < p
        R = np.triu(R, k=1)
        R = R + R.T
        np.fill_diagonal(R, 1)
        R = R.astype(np.float64)
        # Only compute top few eigenvalues for speed
        from scipy.sparse.linalg import eigsh
        from scipy.sparse import csr_matrix
        try:
            top_eigs = eigsh(csr_matrix(R), k=10, which='LM', return_eigenvectors=False)
            random_max_eigs.append(sorted(top_eigs, reverse=True))
        except Exception:
            continue

    if random_max_eigs:
        random_max_eigs = np.array(random_max_eigs)
        random_mean_top10 = random_max_eigs.mean(axis=0)
        random_std_top10 = random_max_eigs.std(axis=0)
        print(f"  Random matrix top eigenvalue: {random_mean_top10[0]:.1f} +/- {random_std_top10[0]:.1f}")

        # Count how many real eigenvalues exceed the 99th percentile of random
        random_99th = np.percentile(random_max_eigs[:, 0], 99)
        n_significant = (eigenvalues > random_99th).sum()
        print(f"  Random 99th percentile (top eig): {random_99th:.1f}")
        print(f"  Real eigenvalues above random 99th: {n_significant}")

        # Find where real eigenvalues cross below random mean second eigenvalue
        random_2nd_mean = random_mean_top10[1] if len(random_mean_top10) > 1 else 0
        n_above_random_2nd = (eigenvalues > random_2nd_mean + 2 * random_std_top10[1]).sum()
        print(f"  Random 2nd eigenvalue mean: {random_2nd_mean:.1f}")
        print(f"  Real eigenvalues above random 2nd + 2σ: {n_above_random_2nd}")
    else:
        random_mean_top10 = []
        n_significant = 0
        n_above_random_2nd = 0

    return {
        'density': float(p),
        'expected_leading_random': float(expected_leading),
        'actual_leading': float(eigenvalues[0]),
        'mp_bulk_upper': float(mp_upper),
        'n_above_random_99th': int(n_significant),
        'random_mean_top10': [float(x) for x in random_mean_top10[:10]] if len(random_mean_top10) > 0 else [],
    }


def rank_analysis(eigenvalues):
    """Analyze effective rank at various thresholds."""
    thresholds = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
    ranks = {}
    for t in thresholds:
        rank = (np.abs(eigenvalues) > t).sum()
        ranks[str(t)] = int(rank)
        print(f"  Rank at threshold {t}: {rank}")

    # Effective rank (exponential of spectral entropy)
    pos_eigs = eigenvalues[eigenvalues > 0]
    normed = pos_eigs / pos_eigs.sum()
    spectral_entropy = -np.sum(normed * np.log(normed))
    effective_rank = np.exp(spectral_entropy)
    print(f"  Spectral entropy: {spectral_entropy:.3f}")
    print(f"  Effective rank (exp(entropy)): {effective_rank:.1f}")

    return {
        'ranks_by_threshold': ranks,
        'spectral_entropy': float(spectral_entropy),
        'effective_rank': float(effective_rank),
    }


def eigenvalue_decay_profile(eigenvalues):
    """Characterize the eigenvalue decay: flat, exponential, power law?"""
    pos_eigs = eigenvalues[eigenvalues > 0]
    n = len(pos_eigs)

    # Cumulative variance
    total = pos_eigs.sum()
    cumvar = np.cumsum(pos_eigs) / total

    # Find K for various variance thresholds
    thresholds = [0.5, 0.8, 0.9, 0.95, 0.99]
    k_for_threshold = {}
    for t in thresholds:
        k = np.searchsorted(cumvar, t) + 1
        k_for_threshold[str(t)] = int(k)
        print(f"  K for {100*t:.0f}% variance: {k}")

    # Check flatness: ratio of consecutive eigenvalues
    ratios = pos_eigs[:-1] / pos_eigs[1:]
    mean_ratio = ratios[:50].mean()
    std_ratio = ratios[:50].std()
    print(f"  Mean consecutive ratio (top 50): {mean_ratio:.4f} +/- {std_ratio:.4f}")

    # Is it flat (ratio ≈ 1) or decaying (ratio > 1)?
    if mean_ratio < 1.05:
        profile = "FLAT"
    elif mean_ratio < 1.2:
        profile = "SLOW_DECAY"
    else:
        profile = "RAPID_DECAY"
    print(f"  Decay profile: {profile}")

    # Spectral gap between 1st and 2nd eigenvalue
    gap_1_2 = float(pos_eigs[0] - pos_eigs[1])
    ratio_1_2 = float(pos_eigs[0] / pos_eigs[1])
    print(f"  Gap λ1-λ2: {gap_1_2:.2f}")
    print(f"  Ratio λ1/λ2: {ratio_1_2:.2f}")

    return {
        'n_positive': int(n),
        'k_for_variance': k_for_threshold,
        'mean_consecutive_ratio_top50': float(mean_ratio),
        'std_consecutive_ratio_top50': float(std_ratio),
        'decay_profile': profile,
        'gap_1_2': gap_1_2,
        'ratio_1_2': ratio_1_2,
        'top_20_eigenvalues': [float(x) for x in pos_eigs[:20]],
        'eigenvalues_at_positions': {
            str(k): float(pos_eigs[k-1]) if k <= n else 0
            for k in [1, 5, 10, 25, 50, 100, 150, 200, 300, 500]
            if k <= n
        },
    }


def participation_ratio(eigenvectors, eigenvalues):
    """Compute participation ratio of top eigenvectors.

    PR = 1 / sum(v_i^4)  for normalized eigenvector v.
    PR=1 means localized on one component.
    PR=N means uniformly distributed.
    Low PR means the eigenvector picks out a small subspace.
    """
    n = eigenvectors.shape[0]
    n_check = min(200, eigenvectors.shape[1])

    prs = []
    for k in range(n_check):
        v = eigenvectors[:, k]
        v2 = v ** 2
        pr = 1.0 / np.sum(v2 ** 2)
        prs.append(float(pr))

    prs = np.array(prs)
    print(f"\n  Participation ratios (top {n_check} eigenvectors):")
    print(f"  Mean PR: {prs.mean():.1f} (max possible: {n})")
    print(f"  PR range: {prs.min():.1f} - {prs.max():.1f}")
    print(f"  PR for top 5: {prs[:5].round(1)}")

    # How many eigenvectors are delocalized (PR > n/4)?
    n_delocalized = (prs > n / 4).sum()
    n_localized = (prs < n / 10).sum()
    print(f"  Delocalized (PR > n/4): {n_delocalized}")
    print(f"  Localized (PR < n/10): {n_localized}")

    return {
        'mean_pr': float(prs.mean()),
        'max_possible': n,
        'pr_top_20': [float(x) for x in prs[:20]],
        'n_delocalized': int(n_delocalized),
        'n_localized': int(n_localized),
    }


def run():
    print("=" * 70)
    print("T1: Definitive Incompatibility Matrix & Eigenspectrum")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Build matrix
    print("\n[1/5] Building incompatibility matrix from Currier A...")
    compat, all_middles, mid_to_idx, degrees = build_incompatibility_matrix()

    # Full eigenspectrum
    print("\n[2/5] Full eigendecomposition...")
    eigenvalues, eigenvectors = full_eigenspectrum(compat)

    # Random matrix comparison
    print("\n[3/5] Marchenko-Pastur comparison...")
    mp_results = marchenko_pastur_comparison(eigenvalues, compat)

    # Rank analysis
    print("\n[4/5] Rank analysis...")
    rank_results = rank_analysis(eigenvalues)

    # Eigenvalue decay profile
    print("\n[5/5] Eigenvalue decay profile...")
    decay_results = eigenvalue_decay_profile(eigenvalues)

    # Participation ratio
    pr_results = participation_ratio(eigenvectors, eigenvalues)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    n = compat.shape[0]
    n_pairs = n * (n - 1) // 2
    n_compat = (compat.sum() - n) // 2
    print(f"  MIDDLEs: {n}")
    print(f"  Compatible pairs: {n_compat} / {n_pairs} ({100*n_compat/n_pairs:.1f}%)")
    print(f"  Leading eigenvalue: {eigenvalues[0]:.1f}")
    print(f"  Eigenvalues above random 99th: {mp_results['n_above_random_99th']}")
    print(f"  Effective rank: {rank_results['effective_rank']:.1f}")
    print(f"  Decay profile: {decay_results['decay_profile']}")
    print(f"  K for 90% variance: {decay_results['k_for_variance'].get('0.9', '?')}")

    # Save
    results = {
        'test': 'T1_definitive_matrix',
        'n_middles': n,
        'n_pairs': n_pairs,
        'n_compatible': int(n_compat),
        'pct_compatible': round(100 * n_compat / n_pairs, 1),
        'degree_stats': {
            'min': int(degrees.min()),
            'max': int(degrees.max()),
            'mean': round(float(degrees.mean()), 1),
            'median': round(float(np.median(degrees)), 1),
        },
        'eigenspectrum': {
            'leading': float(eigenvalues[0]),
            'n_positive': int((eigenvalues > 0).sum()),
            'n_negative': int((eigenvalues < 0).sum()),
        },
        'marchenko_pastur': mp_results,
        'rank': rank_results,
        'decay': decay_results,
        'participation_ratio': pr_results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't1_definitive_matrix.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't1_definitive_matrix.json'}")

    # Also save the raw eigenvalues for T2
    np.save(RESULTS_DIR / 't1_eigenvalues.npy', eigenvalues)
    np.save(RESULTS_DIR / 't1_compat_matrix.npy', compat)
    print(f"Saved eigenvalues and matrix for downstream tests")


if __name__ == '__main__':
    run()
