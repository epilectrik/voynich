#!/usr/bin/env python3
"""
T2: Dimensionality Convergence
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

The prior LATENT_AXES probe tested K=2..128 and AUC never plateaued.
This test extends to K=512 with finer granularity to find actual
convergence, and uses multiple dimensionality estimation methods.

Key questions:
- At what K does link-prediction AUC actually plateau?
- Do different methods (spectral, NMF, logistic) agree on K?
- Is there a sharp elbow or smooth saturation?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score
from sklearn.decomposition import TruncatedSVD, NMF

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_matrix():
    """Load compatibility matrix from T1."""
    mat_path = RESULTS_DIR / 't1_compat_matrix.npy'
    if mat_path.exists():
        return np.load(mat_path)
    raise FileNotFoundError(f"Run T1 first: {mat_path}")


def cross_validated_auc(M, K_values, n_folds=5, n_test=3000):
    """Cross-validated link prediction AUC at each K.

    Uses spectral embedding + dot-product scoring.
    Balanced positive/negative test sets.
    """
    n = M.shape[0]
    upper_tri = np.triu_indices(n, k=1)
    y_all = M[upper_tri].astype(np.float64)

    pos_indices = np.where(y_all == 1)[0]
    neg_indices = np.where(y_all == 0)[0]

    n_test_per_class = min(n_test, len(pos_indices) // n_folds, len(neg_indices) // n_folds)
    print(f"  Test set size per fold: {2 * n_test_per_class} (balanced)")

    results = {}
    for K in K_values:
        if K >= n:
            continue
        print(f"  K={K}...", end=" ")
        fold_aucs = []
        np.random.seed(42)

        for fold in range(n_folds):
            test_pos = np.random.choice(pos_indices, size=n_test_per_class, replace=False)
            test_neg = np.random.choice(neg_indices, size=n_test_per_class, replace=False)
            test_idx = np.concatenate([test_pos, test_neg])

            # Mask test edges
            M_train = M.copy()
            for idx in test_pos:
                i, j = upper_tri[0][idx], upper_tri[1][idx]
                M_train[i, j] = 0
                M_train[j, i] = 0

            # Spectral embedding
            svd = TruncatedSVD(n_components=K, random_state=42 + fold)
            embedding = svd.fit_transform(M_train.astype(np.float64))

            # Score test pairs
            test_i = upper_tri[0][test_idx]
            test_j = upper_tri[1][test_idx]
            scores = np.sum(embedding[test_i] * embedding[test_j], axis=1)
            y_test = y_all[test_idx]

            try:
                auc = roc_auc_score(y_test, scores)
                fold_aucs.append(auc)
            except Exception:
                pass

        if fold_aucs:
            mean_auc = np.mean(fold_aucs)
            std_auc = np.std(fold_aucs)
            results[K] = {'mean_auc': float(mean_auc), 'std_auc': float(std_auc)}
            print(f"AUC={mean_auc:.4f} +/- {std_auc:.4f}")
        else:
            results[K] = {'mean_auc': 0, 'std_auc': 0}
            print("FAILED")

    return results


def nmf_reconstruction(M, K_values):
    """NMF reconstruction error at each K.

    NMF is natural for binary matrices (non-negative factors).
    """
    print(f"\n  NMF reconstruction error...")
    M_float = M.astype(np.float64)
    results = {}

    for K in K_values:
        if K >= M.shape[0]:
            continue
        print(f"  K={K}...", end=" ")
        try:
            model = NMF(n_components=K, init='nndsvda', max_iter=300,
                        random_state=42, l1_ratio=0.0)
            W = model.fit_transform(M_float)
            H = model.components_
            recon = W @ H
            # Frobenius error relative to matrix norm
            error = np.linalg.norm(M_float - recon, 'fro')
            rel_error = error / np.linalg.norm(M_float, 'fro')
            results[K] = {
                'frobenius_error': float(error),
                'relative_error': float(rel_error),
                'n_iter': int(model.n_iter_),
            }
            print(f"rel_error={rel_error:.4f}")
        except Exception as e:
            print(f"ERROR: {e}")
            results[K] = {'frobenius_error': float('inf'), 'relative_error': 1.0, 'n_iter': 0}

    return results


def find_elbow(K_values, aucs):
    """Find elbow point using maximum curvature method."""
    if len(K_values) < 3:
        return K_values[0]

    # Normalize to [0,1] range
    x = np.array(K_values, dtype=float)
    y = np.array(aucs, dtype=float)
    x_norm = (x - x.min()) / (x.max() - x.min())
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-10)

    # Line from first to last point
    dx = x_norm[-1] - x_norm[0]
    dy = y_norm[-1] - y_norm[0]

    # Distance from each point to this line
    distances = np.abs(dy * x_norm - dx * y_norm + dx * y_norm[0] - dy * x_norm[0])
    distances /= np.sqrt(dx**2 + dy**2)

    elbow_idx = np.argmax(distances)
    return int(K_values[elbow_idx])


def diminishing_returns_analysis(cv_results):
    """Analyze where marginal AUC improvement becomes negligible."""
    sorted_k = sorted(cv_results.keys())
    aucs = [cv_results[k]['mean_auc'] for k in sorted_k]

    # Marginal improvement per doubling
    improvements = []
    for i in range(1, len(sorted_k)):
        delta = aucs[i] - aucs[i-1]
        improvements.append({
            'from_k': int(sorted_k[i-1]),
            'to_k': int(sorted_k[i]),
            'delta_auc': float(delta),
            'relative_improvement': float(delta / (1.0 - aucs[i-1] + 1e-10)),
        })

    # Find where improvement drops below 0.005 per step
    plateau_k = sorted_k[-1]
    for imp in improvements:
        if imp['delta_auc'] < 0.005:
            plateau_k = imp['from_k']
            break

    return {
        'improvements': improvements,
        'plateau_k': int(plateau_k),
    }


def run():
    print("=" * 70)
    print("T2: Dimensionality Convergence")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    M = load_matrix()
    n = M.shape[0]
    print(f"  Matrix size: {n}x{n}")

    # Extended K range
    K_values_cv = [4, 8, 16, 32, 48, 64, 96, 128, 192, 256, 384]
    K_values_cv = [k for k in K_values_cv if k < n - 1]

    K_values_nmf = [4, 8, 16, 32, 64, 128, 256]
    K_values_nmf = [k for k in K_values_nmf if k < n - 1]

    # Cross-validated AUC
    print("\n[1/3] Cross-validated link prediction AUC...")
    cv_results = cross_validated_auc(M, K_values_cv)

    # NMF reconstruction
    print("\n[2/3] NMF reconstruction error...")
    nmf_results = nmf_reconstruction(M, K_values_nmf)

    # Elbow and plateau analysis
    print("\n[3/3] Convergence analysis...")
    sorted_k = sorted(cv_results.keys())
    aucs = [cv_results[k]['mean_auc'] for k in sorted_k]

    elbow_k = find_elbow(sorted_k, aucs)
    print(f"  Elbow K (max curvature): {elbow_k}")

    dr_results = diminishing_returns_analysis(cv_results)
    print(f"  Plateau K (AUC improvement < 0.005): {dr_results['plateau_k']}")

    # NMF elbow
    nmf_sorted_k = sorted(nmf_results.keys())
    nmf_errors = [nmf_results[k]['relative_error'] for k in nmf_sorted_k]
    if len(nmf_sorted_k) >= 3:
        nmf_elbow = find_elbow(nmf_sorted_k, [-e for e in nmf_errors])
        print(f"  NMF elbow K: {nmf_elbow}")
    else:
        nmf_elbow = 0

    # Best AUC
    best_k = max(cv_results.keys(), key=lambda k: cv_results[k]['mean_auc'])
    best_auc = cv_results[best_k]['mean_auc']
    print(f"\n  Best AUC: {best_auc:.4f} at K={best_k}")

    # Is it still rising?
    last_two = sorted_k[-2:]
    if len(last_two) == 2:
        delta = cv_results[last_two[1]]['mean_auc'] - cv_results[last_two[0]]['mean_auc']
        still_rising = delta > 0.002
        print(f"  AUC delta at highest K: {delta:.4f} ({'STILL RISING' if still_rising else 'PLATEAUED'})")
    else:
        still_rising = False

    # Summary
    print(f"\n{'='*70}")
    print("CONVERGENCE SUMMARY")
    print(f"{'='*70}")

    if still_rising:
        verdict = "NOT_CONVERGED"
        explanation = f"AUC still rising at K={sorted_k[-1]}. True dimensionality exceeds test range."
    elif dr_results['plateau_k'] < sorted_k[-1]:
        verdict = "CONVERGED"
        explanation = f"AUC plateaus at K≈{dr_results['plateau_k']}. Marginal improvement negligible beyond."
    else:
        verdict = "SOFT_PLATEAU"
        explanation = f"AUC improvement slowing. Elbow at K={elbow_k}, approximate plateau at K={dr_results['plateau_k']}."

    print(f"  Verdict: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T2_dimensionality_convergence',
        'n_middles': n,
        'cross_validation': {str(k): v for k, v in cv_results.items()},
        'nmf_reconstruction': {str(k): v for k, v in nmf_results.items()},
        'convergence': {
            'elbow_k': elbow_k,
            'plateau_k': dr_results['plateau_k'],
            'best_k': int(best_k),
            'best_auc': float(best_auc),
            'still_rising': still_rising,
            'nmf_elbow_k': nmf_elbow,
        },
        'diminishing_returns': dr_results['improvements'],
        'verdict': verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't2_dimensionality_convergence.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't2_dimensionality_convergence.json'}")


if __name__ == '__main__':
    run()
