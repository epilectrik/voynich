"""T1: Manifold Embedding via PCA for Phase 580.

PCA on Space A, Space B, and combined. Interpret major axes.
Report dimensionality diagnostics. Decide C1667.
"""
import json, os, math
import numpy as np

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')


def pca_analysis(X, feature_names, folios):
    """Run PCA on standardized matrix X (n x p). Return full diagnostics."""
    n, p = X.shape

    cov = np.cov(X.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    eigenvalues = np.maximum(eigenvalues, 0)

    total_var = eigenvalues.sum()
    if total_var < 1e-12:
        total_var = 1.0
    var_explained = (eigenvalues / total_var).tolist()
    cumulative = np.cumsum(eigenvalues / total_var).tolist()

    cum = np.cumsum(eigenvalues / total_var)
    pcs_70 = int(np.searchsorted(cum, 0.70)) + 1
    pcs_80 = int(np.searchsorted(cum, 0.80)) + 1
    pcs_90 = int(np.searchsorted(cum, 0.90)) + 1

    # Effective rank (participation ratio)
    eff_rank = float(total_var ** 2 / np.sum(eigenvalues ** 2))

    # Scree elbow: largest eigenvalue drop
    if p > 1:
        drops = [float(eigenvalues[i] - eigenvalues[i + 1]) for i in range(p - 1)]
        scree_elbow = int(np.argmax(drops)) + 1
    else:
        scree_elbow = 1

    # Loadings: top 5 features per PC
    n_pcs_report = min(p, max(3, pcs_80))
    loadings = {}
    for pc_idx in range(n_pcs_report):
        vec = eigenvectors[:, pc_idx]
        sorted_feats = sorted(range(p), key=lambda j: abs(vec[j]), reverse=True)
        top = [{'feature': feature_names[j], 'loading': round(float(vec[j]), 4)}
               for j in sorted_feats[:5]]
        loadings[f'PC{pc_idx + 1}'] = top

    # PC scores
    scores_matrix = X @ eigenvectors
    n_store = min(p, pcs_90 + 1)
    folio_scores = {}
    for i, f in enumerate(folios):
        folio_scores[f] = {f'PC{k + 1}': round(float(scores_matrix[i, k]), 6)
                           for k in range(n_store)}

    return {
        'n_features': p,
        'eigenvalues': eigenvalues.tolist(),
        'variance_explained': var_explained,
        'cumulative_variance': cumulative,
        'pcs_for_70pct': pcs_70,
        'pcs_for_80pct': pcs_80,
        'pcs_for_90pct': pcs_90,
        'effective_rank': round(eff_rank, 4),
        'scree_elbow': scree_elbow,
        'loadings': loadings,
        'folio_scores': folio_scores
    }


def main():
    with open(os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')) as f:
        t0 = json.load(f)

    folios = t0['folios']
    fnames = {
        'A': t0['metadata']['space_A_features'],
        'B': t0['metadata']['space_B_features'],
        'combined': t0['metadata']['combined_features']
    }
    matrices = {
        'A': np.array(t0['space_A']['standardized']),
        'B': np.array(t0['space_B']['standardized']),
        'combined': np.array(t0['combined']['standardized'])
    }

    results = {}
    for space_name in ['A', 'B', 'combined']:
        results[space_name] = pca_analysis(
            matrices[space_name], fnames[space_name], folios
        )

    # C1667 decision (Space A)
    eff_rank_A = results['A']['effective_rank']
    pcs_80_A = results['A']['pcs_for_80pct']

    if eff_rank_A <= 3.5 or pcs_80_A <= 3:
        verdict = 'MANIFOLD_LOW_DIM'
    elif eff_rank_A > 5.5 or pcs_80_A > 5:
        verdict = 'MANIFOLD_DIFFUSE'
    else:
        verdict = 'MANIFOLD_INTERMEDIATE'

    output = {
        'metadata': {
            'phase': '580',
            'script': 't1_manifold_embedding.py',
            'n_folios': len(folios)
        },
        'space_A': results['A'],
        'space_B': results['B'],
        'combined': results['combined'],
        'C1667': {
            'verdict': verdict,
            'effective_rank_A': round(eff_rank_A, 4),
            'pcs_for_80pct_A': pcs_80_A,
            'rationale': f"Space A effective rank = {eff_rank_A:.2f}, PCs for 80% = {pcs_80_A}"
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't1_manifold_embedding.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T1: Manifold embedding complete")
    for sn in ['A', 'B', 'combined']:
        r = results[sn]
        print(f"  Space {sn}: {r['n_features']} features, "
              f"eff_rank={r['effective_rank']:.2f}, PCs for 80%={r['pcs_for_80pct']}")
        for pc_name, tops in r['loadings'].items():
            top_str = ', '.join(f"{t['feature']}({t['loading']:+.3f})" for t in tops[:3])
            print(f"    {pc_name}: {top_str}")
    print(f"  C1667: {verdict} (eff_rank={eff_rank_A:.2f}, PCs_80={pcs_80_A})")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
