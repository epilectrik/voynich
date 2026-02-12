#!/usr/bin/env python3
"""
T9: Independent Feature Model
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Can an AND-style independent binary feature model reproduce the
observed graph statistics?

Model: Each of N=972 nodes gets K binary features (each 1 with prob p).
Two nodes are "compatible" if they share >= T features set to 1.

Sweep K to find the dimensionality that simultaneously matches:
- Density ≈ 2.2%
- Clustering ≈ 0.873
- λ₁ ≈ 82
- n_eig > 12 ≈ 18
- Effective rank (top 50) ≈ 27.7
"""

import sys
import json
import functools
import numpy as np
import networkx as nx
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from scipy.stats import binom

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'

N = 972  # Number of nodes (matching real graph)

# Target statistics from real graph
TARGET = {
    'density': 0.0217,
    'clustering': 0.8732,
    'lambda_1': 81.98,
    'n_eig_above_12': 18,
    'effective_rank_top50': 27.72,
}

K_VALUES = [20, 40, 60, 80, 100, 120, 150, 200]


def theoretical_density(K, p, T):
    """Compute expected density for the AND-model analytically.

    P(compatible) = P(|shared 1s| >= T)

    If node i has features drawn Bernoulli(p), then for a pair (i,j):
    P(both have feature k = 1) = p^2
    Number of shared 1s ~ Binomial(K, p^2)
    P(compatible) = P(Binom(K, p^2) >= T)
    """
    p_shared = p * p
    prob = 1 - binom.cdf(T - 1, K, p_shared)
    return float(prob)


def find_threshold_for_density(K, p, target_density, tol=0.005):
    """Binary search for T that gives target density."""
    # T=0 means everything compatible, T=K means almost nothing
    best_T = None
    best_diff = float('inf')

    for T in range(0, K + 1):
        d = theoretical_density(K, p, T)
        diff = abs(d - target_density)
        if diff < best_diff:
            best_diff = diff
            best_T = T
        if d < target_density * 0.1:
            break  # No point going further

    return best_T, theoretical_density(K, p, best_T)


def find_p_and_T(K, target_density, tol=0.005):
    """Find (p, T) that gives target density for given K.

    Strategy: sweep p from 0.1 to 0.9, for each find best T.
    """
    best_config = None
    best_diff = float('inf')

    for p_int in range(10, 95, 5):
        p = p_int / 100.0
        T, achieved_density = find_threshold_for_density(K, p, target_density)
        diff = abs(achieved_density - target_density)
        if diff < best_diff:
            best_diff = diff
            best_config = (p, T, achieved_density)

    # Refine p around best
    if best_config:
        p_coarse = best_config[0]
        for p_int in range(max(5, int(p_coarse * 100) - 10),
                           min(99, int(p_coarse * 100) + 10)):
            p = p_int / 100.0
            T, achieved_density = find_threshold_for_density(K, p, target_density)
            diff = abs(achieved_density - target_density)
            if diff < best_diff:
                best_diff = diff
                best_config = (p, T, achieved_density)

    return best_config


def generate_and_measure(K, p, T, seed=42):
    """Generate an AND-model graph and compute all metrics."""
    np.random.seed(seed)

    # Generate binary feature vectors
    features = (np.random.random((N, K)) < p).astype(np.int8)

    # Compute compatibility matrix via shared features
    # shared[i,j] = features[i] AND features[j] summed over K
    # Use matrix multiplication: shared = features @ features.T
    shared = features.astype(np.int32) @ features.astype(np.int32).T

    # Compatible if shared >= T
    A = (shared >= T).astype(np.int8)
    np.fill_diagonal(A, 0)  # No self-loops for graph metrics

    # Density
    n_edges = A.sum() // 2
    n_pairs = N * (N - 1) // 2
    density = n_edges / n_pairs

    # Clustering coefficient
    G = nx.from_numpy_array(A)
    clustering = nx.average_clustering(G)

    # Eigenvalues (top 50)
    np.fill_diagonal(A, 1)  # Restore diagonal for eigenvalue computation
    try:
        A_sparse = csr_matrix(A.astype(np.float64))
        eigs = eigsh(A_sparse, k=50, which='LM', return_eigenvectors=False)
        eigs = np.sort(eigs)[::-1]
    except Exception:
        eigs = np.linalg.eigvalsh(A.astype(np.float64))[::-1][:50]

    lambda_1 = float(eigs[0])
    n_eig_above_12 = int((eigs > 12).sum())

    # Effective rank (top 50)
    pos_eigs = eigs[eigs > 0]
    if len(pos_eigs) > 0:
        normed = pos_eigs / pos_eigs.sum()
        entropy = -np.sum(normed * np.log(normed))
        eff_rank = float(np.exp(entropy))
    else:
        eff_rank = 0

    # Degree distribution
    np.fill_diagonal(A, 0)
    degrees = A.sum(axis=1)

    return {
        'density': float(density),
        'clustering': float(clustering),
        'lambda_1': float(lambda_1),
        'n_eig_above_12': int(n_eig_above_12),
        'effective_rank_top50': float(eff_rank),
        'mean_degree': float(degrees.mean()),
        'max_degree': int(degrees.max()),
        'n_edges': int(n_edges),
    }


def score_match(metrics):
    """Score how well synthetic metrics match targets. Lower is better."""
    score = 0
    # Relative errors, weighted by importance
    weights = {
        'density': 2.0,      # Must match closely
        'clustering': 5.0,    # The key discriminator
        'lambda_1': 1.0,
        'n_eig_above_12': 1.0,
        'effective_rank_top50': 1.0,
    }
    for key, weight in weights.items():
        if TARGET[key] != 0:
            rel_error = abs(metrics[key] - TARGET[key]) / abs(TARGET[key])
        else:
            rel_error = abs(metrics[key])
        score += weight * rel_error
    return score


def run():
    print("=" * 70)
    print("T9: Independent Feature Model")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    print(f"\n  Target statistics:")
    for key, val in TARGET.items():
        print(f"    {key}: {val}")

    all_results = {}
    best_overall = None
    best_overall_score = float('inf')

    for K in K_VALUES:
        print(f"\n{'='*50}")
        print(f"  K = {K}")

        # Find (p, T) for target density
        config = find_p_and_T(K, TARGET['density'])
        if config is None:
            print(f"    Could not find density match")
            continue

        p, T, theoretical_d = config
        print(f"    Best config: p={p:.2f}, T={T}, theoretical density={theoretical_d:.4f}")

        # Generate and measure (multiple seeds)
        seed_results = []
        for seed in range(42, 52):
            m = generate_and_measure(K, p, T, seed=seed)
            seed_results.append(m)

        # Average metrics
        avg_metrics = {}
        for key in seed_results[0]:
            vals = [r[key] for r in seed_results]
            avg_metrics[key] = float(np.mean(vals))
            avg_metrics[f'{key}_std'] = float(np.std(vals))

        # Score
        match_score = score_match(avg_metrics)

        print(f"    Achieved density: {avg_metrics['density']:.4f} (target: {TARGET['density']:.4f})")
        print(f"    Clustering: {avg_metrics['clustering']:.4f} (target: {TARGET['clustering']:.4f})")
        print(f"    λ₁: {avg_metrics['lambda_1']:.1f} (target: {TARGET['lambda_1']:.1f})")
        print(f"    n_eig > 12: {avg_metrics['n_eig_above_12']:.1f} (target: {TARGET['n_eig_above_12']})")
        print(f"    Eff. rank: {avg_metrics['effective_rank_top50']:.1f} (target: {TARGET['effective_rank_top50']:.1f})")
        print(f"    Match score: {match_score:.4f}")

        all_results[K] = {
            'K': K,
            'p': float(p),
            'T': int(T),
            'theoretical_density': float(theoretical_d),
            'metrics': avg_metrics,
            'match_score': float(match_score),
        }

        if match_score < best_overall_score:
            best_overall_score = match_score
            best_overall = K

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    print(f"\n  {'K':>5} {'p':>5} {'T':>4} {'density':>10} {'cluster':>10} {'λ₁':>8} {'n_eig':>7} {'eff_rk':>8} {'score':>8}")
    print(f"  {'-'*75}")
    print(f"  {'REAL':>5} {'':>5} {'':>4} {TARGET['density']:>10.4f} {TARGET['clustering']:>10.4f} {TARGET['lambda_1']:>8.1f} {TARGET['n_eig_above_12']:>7} {TARGET['effective_rank_top50']:>8.1f} {'':>8}")
    print(f"  {'-'*75}")

    for K in K_VALUES:
        if K in all_results:
            r = all_results[K]
            m = r['metrics']
            print(f"  {K:>5} {r['p']:>5.2f} {r['T']:>4} {m['density']:>10.4f} {m['clustering']:>10.4f} {m['lambda_1']:>8.1f} {m['n_eig_above_12']:>7.0f} {m['effective_rank_top50']:>8.1f} {r['match_score']:>8.3f}")

    print(f"\n  Best K: {best_overall} (score: {best_overall_score:.4f})")

    # Assess whether the model works
    if best_overall is not None:
        best_metrics = all_results[best_overall]['metrics']
        cluster_error = abs(best_metrics['clustering'] - TARGET['clustering']) / TARGET['clustering']

        if cluster_error < 0.10:
            model_verdict = "REPRODUCED"
            explanation = (f"K={best_overall} independent binary features reproduce the observed "
                           f"graph statistics including clustering ({best_metrics['clustering']:.3f} "
                           f"vs target {TARGET['clustering']:.3f}).")
        elif cluster_error < 0.25:
            model_verdict = "APPROXIMATE"
            explanation = (f"K={best_overall} gives approximate match. Clustering "
                           f"({best_metrics['clustering']:.3f}) within 25% of target "
                           f"({TARGET['clustering']:.3f}) but not exact.")
        else:
            model_verdict = "INSUFFICIENT"
            explanation = ("No K value reproduces the observed clustering coefficient. "
                           "The constraint structure is more complex than independent binary features.")
    else:
        model_verdict = "FAILED"
        explanation = "Could not find any matching configuration."

    print(f"\n  Model verdict: {model_verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T9_independent_feature_model',
        'n_nodes': N,
        'target': TARGET,
        'k_values_tested': K_VALUES,
        'results_by_k': {str(k): v for k, v in all_results.items()},
        'best_k': best_overall,
        'best_score': float(best_overall_score),
        'model_verdict': model_verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't9_independent_feature_model.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't9_independent_feature_model.json'}")


if __name__ == '__main__':
    run()
