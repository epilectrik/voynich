"""T4: Accent as Machine Fit for Phase 580.

Can folio accent be reinterpreted as manifold position?
Canonical correlation, partial correlation, incremental R-squared.
Forgiving-edge distance test with Phase 579 stubborn folios. Decide C1670.
"""
import json, os, math
import numpy as np

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))

ACCENT_PATH = os.path.join(ROOT, 'phases', 'FOLIO_ACCENT_VECTOR',
                            'results', 'folio_accent_vector.json')

STRUCTURAL_ENDPOINT = ['f39v', 'f55v', 'f86v5', 'f95r2']
PARAMETER_ACHIEVABLE = ['f40r', 'f50v', 'f85r2', 'f86v6']
STUBBORN_FOLIOS = STRUCTURAL_ENDPOINT + PARAMETER_ACHIEVABLE

FAMILIES = ['A1', 'A2', 'A3']


def spearman_rank(x, y):
    """Pure-Python Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            mean_rank = (i + j) / 2.0 + 1.0
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = mean_rank
            i = j + 1
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx) ** 2 for i in range(n))
    den_y = sum((ry[i] - mean_ry) ** 2 for i in range(n))
    den = math.sqrt(den_x * den_y)
    if den < 1e-12:
        return 0.0
    return num / den


def r_squared(y, X_pred):
    """OLS R-squared."""
    n = len(y)
    X_aug = np.column_stack([np.ones(n), X_pred])
    try:
        beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    except Exception:
        return 0.0
    y_hat = X_aug @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    if ss_tot < 1e-12:
        return 0.0
    return float(1 - ss_res / ss_tot)


def matrix_sqrt_inv(M):
    """Compute M^{-1/2} via eigendecomposition."""
    evals, evecs = np.linalg.eigh(M)
    evals = np.maximum(evals, 1e-12)
    return evecs @ np.diag(1.0 / np.sqrt(evals)) @ evecs.T


def residualize(Y, X_control):
    """Regress Y on X_control, return residuals."""
    XtX = X_control.T @ X_control
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ X_control.T @ Y
    return Y - X_control @ beta


def main():
    with open(os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_manifold_embedding.json')) as f:
        t1 = json.load(f)
    with open(ACCENT_PATH) as f:
        accent_data = json.load(f)

    folios = t0['folios']
    meta = t0['folio_metadata']

    # Common folios (accent has 72 of 76)
    accent_scores = accent_data['T1_pca']['folio_scores']
    common_folios = [f for f in folios if f in accent_scores]
    missing = [f for f in folios if f not in accent_scores]
    n_common = len(common_folios)

    # Accent matrix (n_common x 3)
    accent_pcs = np.array([
        [accent_scores[f]['PC1'], accent_scores[f]['PC2'], accent_scores[f]['PC3']]
        for f in common_folios
    ])

    # Manifold-A PC matrix
    space_A = t1['space_A']
    pcs_80_A = space_A['pcs_for_80pct']
    pc_names_A = [f'PC{k + 1}' for k in range(pcs_80_A)]
    manifold_scores = space_A['folio_scores']
    X_A = np.array([[manifold_scores[f][pc] for pc in pc_names_A]
                     for f in common_folios])

    # 1. Spearman correlations: all accent-vs-manifold PC pairs
    spearman_matrix = {}
    for a_idx in range(3):
        for m_idx in range(pcs_80_A):
            rho = spearman_rank(accent_pcs[:, a_idx].tolist(),
                                X_A[:, m_idx].tolist())
            spearman_matrix[f'accent_PC{a_idx+1}_vs_manifold_PC{m_idx+1}'] = round(rho, 4)

    # 2. Canonical correlation via SVD
    def standardize_cols(M):
        mu = M.mean(axis=0)
        sd = M.std(axis=0, ddof=1)
        sd[sd < 1e-12] = 1.0
        return (M - mu) / sd

    accent_std = standardize_cols(accent_pcs)
    manifold_std = standardize_cols(X_A)

    R_xx = accent_std.T @ accent_std / (n_common - 1)
    R_yy = manifold_std.T @ manifold_std / (n_common - 1)
    C_cross = accent_std.T @ manifold_std / (n_common - 1)

    R_xx_inv_sqrt = matrix_sqrt_inv(R_xx)
    R_yy_inv_sqrt = matrix_sqrt_inv(R_yy)

    T_cca = R_xx_inv_sqrt @ C_cross @ R_yy_inv_sqrt
    _, s, _ = np.linalg.svd(T_cca, full_matrices=False)
    canonical_corrs = np.clip(s, 0, 1).tolist()

    # 3. Partial correlation controlling for family
    family_labels = [meta[f]['family'] for f in common_folios]
    dummies = np.zeros((n_common, 2))
    for i, fl in enumerate(family_labels):
        if fl == 'A1':
            dummies[i, 0] = 1
        elif fl == 'A2':
            dummies[i, 1] = 1

    accent_resid = residualize(accent_pcs, dummies)
    manifold_resid = residualize(X_A, dummies)

    partial_corrs = {}
    for a_idx in range(3):
        for m_idx in range(pcs_80_A):
            rho = spearman_rank(accent_resid[:, a_idx].tolist(),
                                manifold_resid[:, m_idx].tolist())
            partial_corrs[f'accent_PC{a_idx+1}_vs_manifold_PC{m_idx+1}'] = round(rho, 4)

    # 4. Incremental R-squared
    B_raw = np.array(t0['space_B']['raw'])
    folio_idx_map = {f: i for i, f in enumerate(folios)}
    B_names = t0['metadata']['space_B_features']
    ccs1_idx = B_names.index('CCS1')
    dye_idx = B_names.index('DYE_advantage')

    ccs1_common = np.array([B_raw[folio_idx_map[f], ccs1_idx] for f in common_folios])
    dye_common = np.array([B_raw[folio_idx_map[f], dye_idx] for f in common_folios])

    r2_ccs1_family = r_squared(ccs1_common, dummies)
    r2_dye_family = r_squared(dye_common, dummies)

    X_full = np.column_stack([dummies, X_A])
    r2_ccs1_full = r_squared(ccs1_common, X_full)
    r2_dye_full = r_squared(dye_common, X_full)

    incr_r2_ccs1 = r2_ccs1_full - r2_ccs1_family
    incr_r2_dye = r2_dye_full - r2_dye_family

    # 5. Within-A2 analysis
    a2_idx = [i for i, f in enumerate(common_folios) if meta[f]['family'] == 'A2']
    if len(a2_idx) >= 5:
        ccs1_a2 = ccs1_common[a2_idx]
        X_A_a2 = X_A[a2_idx]
        within_a2_corrs = {}
        for k in range(pcs_80_A):
            rho = spearman_rank(ccs1_a2.tolist(), X_A_a2[:, k].tolist())
            within_a2_corrs[f'manifold_PC{k+1}_vs_CCS1'] = round(rho, 4)
        r2_a2 = r_squared(ccs1_a2, X_A_a2)
    else:
        within_a2_corrs = {}
        r2_a2 = 0.0

    # 6. Forgiving-edge distance test
    # FR centroid in Space A (using all 76 folios)
    all_A_scores = np.array([
        [manifold_scores[f][pc] for pc in pc_names_A] for f in folios
    ])
    fr_idx = [i for i, f in enumerate(folios)
              if meta[f]['landscape_class'] == 'FORGIVING_RECIRCULATOR']
    fr_centroid = all_A_scores[fr_idx].mean(axis=0) if fr_idx else np.zeros(pcs_80_A)

    # Accent PCs vs FR distance (common folios only)
    fr_dists_common = []
    for f in common_folios:
        i_all = folios.index(f)
        d = float(np.linalg.norm(all_A_scores[i_all] - fr_centroid))
        fr_dists_common.append(d)

    fr_dist_corrs = {}
    for a_idx in range(3):
        rho = spearman_rank(accent_pcs[:, a_idx].tolist(), fr_dists_common)
        fr_dist_corrs[f'accent_PC{a_idx+1}_vs_FR_dist'] = round(rho, 4)

    # Stubborn folio analysis
    stubborn_analysis = {}
    for f in STUBBORN_FOLIOS:
        if f not in folios:
            continue
        i_all = folios.index(f)
        endpoint_class = 'STRUCTURAL_ENDPOINT' if f in STRUCTURAL_ENDPOINT else 'PARAMETER_ACHIEVABLE'
        scores_dict = {pc: round(float(all_A_scores[i_all, k]), 4)
                       for k, pc in enumerate(pc_names_A)}
        fr_dist = float(np.linalg.norm(all_A_scores[i_all] - fr_centroid))
        stubborn_analysis[f] = {
            'endpoint_class': endpoint_class,
            'manifold_scores': scores_dict,
            'fr_distance': round(fr_dist, 4)
        }

    # Point-biserial: manifold PCs vs endpoint class
    se_folios = [f for f in STRUCTURAL_ENDPOINT if f in folios]
    pa_folios = [f for f in PARAMETER_ACHIEVABLE if f in folios]
    point_biserial = {}
    if len(se_folios) >= 2 and len(pa_folios) >= 2:
        stub_order = se_folios + pa_folios
        stub_labels = [0.0] * len(se_folios) + [1.0] * len(pa_folios)
        for k in range(pcs_80_A):
            stub_scores = [float(all_A_scores[folios.index(f), k]) for f in stub_order]
            rho = spearman_rank(stub_scores, stub_labels)
            point_biserial[f'manifold_PC{k+1}'] = round(rho, 4)

    # C1670 decision
    canonical_r1 = canonical_corrs[0] if canonical_corrs else 0
    max_incr_r2 = max(incr_r2_ccs1, incr_r2_dye)
    max_partial = max(abs(v) for v in partial_corrs.values()) if partial_corrs else 0

    if canonical_r1 > 0.50 and max_incr_r2 > 0.15:
        verdict = 'ACCENT_IS_MANIFOLD_POSITION'
    elif canonical_r1 > 0.30 or max_incr_r2 > 0.10 or max_partial > 0.25:
        verdict = 'ACCENT_PARTIALLY_CAPTURED'
    else:
        verdict = 'ACCENT_INDEPENDENT'

    output = {
        'metadata': {
            'phase': '580',
            'script': 't4_accent_machine_fit.py',
            'n_common_folios': n_common,
            'missing_accent': missing
        },
        'spearman_accent_vs_manifold': spearman_matrix,
        'canonical_correlations': [round(c, 4) for c in canonical_corrs],
        'partial_correlations_family_controlled': partial_corrs,
        'incremental_r_squared': {
            'CCS1': {
                'family_only': round(r2_ccs1_family, 4),
                'family_plus_manifold': round(r2_ccs1_full, 4),
                'incremental': round(incr_r2_ccs1, 4)
            },
            'DYE_advantage': {
                'family_only': round(r2_dye_family, 4),
                'family_plus_manifold': round(r2_dye_full, 4),
                'incremental': round(incr_r2_dye, 4)
            }
        },
        'within_A2': {
            'n_a2': len(a2_idx),
            'correlations': within_a2_corrs,
            'r_squared': round(r2_a2, 4)
        },
        'forgiving_edge_distance': {
            'n_FR_folios': len(fr_idx),
            'accent_vs_FR_distance': fr_dist_corrs,
            'stubborn_folios': stubborn_analysis,
            'point_biserial_SE_vs_PA': point_biserial
        },
        'C1670': {
            'verdict': verdict,
            'canonical_r1': round(canonical_r1, 4),
            'max_incremental_r2': round(max_incr_r2, 4),
            'max_partial_corr': round(max_partial, 4),
            'rationale': (f"Canonical r1={canonical_r1:.3f}, "
                          f"max incr R²={max_incr_r2:.3f}, "
                          f"max partial r={max_partial:.3f}")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't4_accent_machine_fit.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T4: Accent-machine-fit analysis complete")
    print(f"  Common folios: {n_common} (missing: {missing})")
    print(f"  Canonical correlations: {[round(c, 3) for c in canonical_corrs]}")
    print(f"  Incremental R² CCS1: {incr_r2_ccs1:.4f}, DYE: {incr_r2_dye:.4f}")
    print(f"  Within-A2 R²: {r2_a2:.4f} (n={len(a2_idx)})")
    print(f"  Top Spearman pairs:")
    for k, v in sorted(spearman_matrix.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
        print(f"    {k}: {v}")
    print(f"  FR distance correlations: {fr_dist_corrs}")
    print(f"  Point-biserial (stubborn): {point_biserial}")
    print(f"  C1670: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
