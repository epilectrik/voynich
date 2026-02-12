#!/usr/bin/env python3
"""
T6: Null Ensemble Benchmarking — Spectral Fingerprint Rarity Test
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Test whether the spectral profile of the MIDDLE incompatibility graph
is rare under matched null graph ensembles.

Two null models:
1. Configuration Model — preserves exact degree sequence
2. Erdős-Rényi — preserves only density

If the spectral shape is rare under both, it's a genuine structural
fingerprint. If it's generic for the degree distribution, the structure
is an artifact of hub heterogeneity.
"""

import sys
import json
import functools
import numpy as np
import networkx as nx
from pathlib import Path
from scipy.sparse.linalg import eigsh
from scipy.sparse import csr_matrix
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_TRIALS = 100


def load_real_graph():
    """Load compatibility matrix and compute real graph metrics."""
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')
    eigenvalues = np.load(RESULTS_DIR / 't1_eigenvalues.npy')
    return M, eigenvalues


def compute_graph_metrics(A, n_eig=50):
    """Compute spectral and graph metrics for an adjacency matrix.

    Returns dict of metrics. Uses sparse eigensolve for speed.
    """
    n = A.shape[0]
    metrics = {}

    # Eigenvalues (top n_eig)
    try:
        A_sparse = csr_matrix(A.astype(np.float64))
        k = min(n_eig, n - 2)
        eigs = eigsh(A_sparse, k=k, which='LM', return_eigenvectors=False)
        eigs = np.sort(eigs)[::-1]
    except Exception:
        # Fallback to dense
        eigs = np.linalg.eigvalsh(A.astype(np.float64))[::-1][:n_eig]

    metrics['lambda_1'] = float(eigs[0])
    metrics['lambda_2'] = float(eigs[1]) if len(eigs) > 1 else 0
    metrics['spectral_gap'] = float(eigs[0] / eigs[1]) if eigs[1] > 0 else float('inf')

    # Number of eigenvalues above threshold (T1 found 28 above random 2nd + 2σ)
    # Use threshold = 12.0 (approx random 2nd eig + 2σ from T1)
    threshold = 12.0
    metrics['n_eig_above_12'] = int((eigs > threshold).sum())

    # Effective rank from spectral entropy (using top eigenvalues)
    pos_eigs = eigs[eigs > 0]
    if len(pos_eigs) > 0:
        normed = pos_eigs / pos_eigs.sum()
        entropy = -np.sum(normed * np.log(normed))
        metrics['effective_rank_top50'] = float(np.exp(entropy))
    else:
        metrics['effective_rank_top50'] = 0

    # Clustering coefficient (via networkx)
    G = nx.from_numpy_array(A)
    metrics['clustering'] = float(nx.average_clustering(G))

    # Degree stats for sanity check
    degrees = np.array([d for _, d in G.degree()])
    metrics['mean_degree'] = float(degrees.mean())
    metrics['max_degree'] = int(degrees.max())
    metrics['n_edges'] = int(G.number_of_edges())

    return metrics


def generate_configuration_model(degree_seq, seed):
    """Generate a configuration model graph preserving degree sequence."""
    try:
        G = nx.configuration_model(degree_seq, seed=seed)
        G = nx.Graph(G)  # Remove parallel edges
        G.remove_edges_from(nx.selfloop_edges(G))  # Remove self-loops
        A = nx.to_numpy_array(G, dtype=np.int8)
        return A
    except Exception:
        return None


def generate_er_model(n, p, seed):
    """Generate Erdős-Rényi graph."""
    G = nx.erdos_renyi_graph(n, p, seed=seed)
    A = nx.to_numpy_array(G, dtype=np.int8)
    return A


def run():
    print("=" * 70)
    print("T6: Null Ensemble Benchmarking")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Load real graph
    print("\n[1/4] Loading real graph and computing metrics...")
    M, real_eigenvalues = load_real_graph()
    n = M.shape[0]

    real_metrics = compute_graph_metrics(M)
    print(f"  Real graph: {n} nodes, {real_metrics['n_edges']} edges")
    print(f"  λ₁ = {real_metrics['lambda_1']:.1f}")
    print(f"  λ₁/λ₂ = {real_metrics['spectral_gap']:.2f}")
    print(f"  n_eig > 12 = {real_metrics['n_eig_above_12']}")
    print(f"  Effective rank (top50) = {real_metrics['effective_rank_top50']:.1f}")
    print(f"  Clustering = {real_metrics['clustering']:.4f}")

    # Extract degree sequence
    G_real = nx.from_numpy_array(M)
    degree_seq = [d for _, d in G_real.degree()]
    density = 2 * real_metrics['n_edges'] / (n * (n - 1))
    print(f"  Density: {density:.4f}")

    # Configuration Model ensemble
    print(f"\n[2/4] Configuration Model ensemble ({N_TRIALS} trials)...")
    cm_metrics = {key: [] for key in ['lambda_1', 'spectral_gap', 'n_eig_above_12',
                                       'effective_rank_top50', 'clustering']}

    for trial in range(N_TRIALS):
        if trial % 10 == 0:
            print(f"  Trial {trial}...")
        A_null = generate_configuration_model(degree_seq, seed=42 + trial)
        if A_null is None:
            continue
        m = compute_graph_metrics(A_null)
        for key in cm_metrics:
            cm_metrics[key].append(m[key])

    print(f"  Completed {len(cm_metrics['lambda_1'])} trials")

    # ER ensemble
    print(f"\n[3/4] Erdős-Rényi ensemble ({N_TRIALS} trials)...")
    er_metrics = {key: [] for key in ['lambda_1', 'spectral_gap', 'n_eig_above_12',
                                       'effective_rank_top50', 'clustering']}

    for trial in range(N_TRIALS):
        if trial % 10 == 0:
            print(f"  Trial {trial}...")
        A_null = generate_er_model(n, density, seed=42 + trial)
        m = compute_graph_metrics(A_null)
        for key in er_metrics:
            er_metrics[key].append(m[key])

    print(f"  Completed {len(er_metrics['lambda_1'])} trials")

    # Comparison
    print(f"\n[4/4] Statistical comparison...")
    print(f"\n  {'Metric':<25} {'Real':>8} {'CM mean±std':>18} {'CM z':>8} {'CM pct':>8} {'ER mean±std':>18} {'ER z':>8}")
    print(f"  {'-'*110}")

    comparison = {}
    anomalous_cm = 0
    anomalous_er = 0

    for key in ['lambda_1', 'spectral_gap', 'n_eig_above_12', 'effective_rank_top50', 'clustering']:
        real_val = real_metrics[key]

        cm_vals = np.array(cm_metrics[key])
        cm_mean = cm_vals.mean()
        cm_std = cm_vals.std()
        cm_z = (real_val - cm_mean) / cm_std if cm_std > 0 else 0
        cm_pct = float(stats.percentileofscore(cm_vals, real_val))

        er_vals = np.array(er_metrics[key])
        er_mean = er_vals.mean()
        er_std = er_vals.std()
        er_z = (real_val - er_mean) / er_std if er_std > 0 else 0
        er_pct = float(stats.percentileofscore(er_vals, real_val))

        print(f"  {key:<25} {real_val:>8.2f} {cm_mean:>8.2f}±{cm_std:>6.2f} {cm_z:>8.2f} {cm_pct:>7.1f}% {er_mean:>8.2f}±{er_std:>6.2f} {er_z:>8.2f}")

        is_anomalous_cm = cm_pct > 95 or cm_pct < 5
        is_anomalous_er = er_pct > 95 or er_pct < 5
        if is_anomalous_cm:
            anomalous_cm += 1
        if is_anomalous_er:
            anomalous_er += 1

        comparison[key] = {
            'real': float(real_val),
            'cm_mean': float(cm_mean),
            'cm_std': float(cm_std),
            'cm_z': float(cm_z),
            'cm_percentile': float(cm_pct),
            'cm_anomalous': bool(is_anomalous_cm),
            'er_mean': float(er_mean),
            'er_std': float(er_std),
            'er_z': float(er_z),
            'er_percentile': float(er_pct),
            'er_anomalous': bool(is_anomalous_er),
        }

    # Verdict
    print(f"\n  Anomalous metrics under Configuration Model: {anomalous_cm}/5")
    print(f"  Anomalous metrics under Erdős-Rényi: {anomalous_er}/5")

    if anomalous_cm >= 4:
        verdict = "RARE"
        explanation = ("The spectral profile is anomalous even under degree-preserving "
                       "randomization. The structure goes beyond degree heterogeneity.")
    elif anomalous_cm >= 2:
        verdict = "PARTIALLY_RARE"
        explanation = ("Some spectral features are anomalous under degree-preserving "
                       "randomization. Partial structural fingerprint.")
    else:
        verdict = "NOT_RARE"
        explanation = ("The spectral profile is generic for graphs with this degree "
                       "distribution. Structure is an artifact of hub heterogeneity.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T6_null_ensemble',
        'n_trials': N_TRIALS,
        'n_nodes': n,
        'density': float(density),
        'real_metrics': {k: float(v) for k, v in real_metrics.items()},
        'comparison': comparison,
        'anomalous_cm': anomalous_cm,
        'anomalous_er': anomalous_er,
        'verdict': verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't6_null_ensemble.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't6_null_ensemble.json'}")


if __name__ == '__main__':
    run()
