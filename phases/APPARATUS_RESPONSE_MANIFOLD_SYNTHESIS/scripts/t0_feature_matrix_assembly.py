"""T0: Feature Matrix Assembly for Phase 580.

Build Space A (76x11 response surface) and Space B (76x4 realized performance).
Z-score standardize. Report correlation structure and effective redundancy.
"""
import json, os, math
import numpy as np

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))

SETUP_PATH = os.path.join(ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION',
                           'results', 't1_full_scale_setup.json')
ABLATION_PATH = os.path.join(ROOT, 'phases', 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES',
                              'results', 't1_mechanism_ablation.json')
LANDSCAPE_PATH = os.path.join(ROOT, 'phases', 'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP',
                               'results', 't4_landscape_model.json')

ABLATION_CHANNELS = [
    'NO_CROSS_COUPLING', 'NO_CLOSE_RECOVERY', 'NO_CONTAINMENT',
    'NO_TR_TO_Y', 'NO_Y_SENSITIVITY'
]

SPACE_A_NAMES = [
    'F1', 'F2', 'F3', 'F4_raw', 'F5',
    'abl_CROSS_COUPLING', 'abl_CLOSE_RECOVERY', 'abl_CONTAINMENT',
    'abl_TR_TO_Y', 'abl_Y_SENSITIVITY', 'mean_CTS'
]

SPACE_B_NAMES = ['DYE_advantage', 'CCS1', 'z_margin', 'PEF']

COMBINED_NAMES = SPACE_A_NAMES + SPACE_B_NAMES


def zscore(X):
    """Z-score standardize columns. Returns (standardized, means, stds)."""
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    sd[sd < 1e-12] = 1.0
    return (X - mu) / sd, mu.tolist(), sd.tolist()


def flag_high_corr(R, names, threshold=0.7):
    """Flag feature pairs with |r| > threshold."""
    flags = []
    p = R.shape[0]
    for i in range(p):
        for j in range(i + 1, p):
            if abs(R[i, j]) > threshold:
                flags.append({
                    'feature_1': names[i],
                    'feature_2': names[j],
                    'r': round(float(R[i, j]), 4)
                })
    return flags


def effective_rank_kaiser(R):
    """Kaiser criterion: count eigenvalues > 1/p of total variance."""
    eigenvalues = np.linalg.eigvalsh(R)[::-1]
    total = eigenvalues.sum()
    threshold = total / len(eigenvalues)
    count = int(sum(1 for e in eigenvalues if e > threshold))
    return count, eigenvalues.tolist()


def main():
    with open(SETUP_PATH) as f:
        setup = json.load(f)
    with open(ABLATION_PATH) as f:
        ablation = json.load(f)
    with open(LANDSCAPE_PATH) as f:
        landscape = json.load(f)

    eligible = setup['eligible_folios']
    configs = setup['folio_configs']
    per_folio_abl = ablation['per_folio']
    per_folio_land = landscape['per_folio_landscape']

    folios = sorted(eligible)
    n = len(folios)

    A_raw = np.zeros((n, 11))
    B_raw = np.zeros((n, 4))
    metadata = {}

    for i, f in enumerate(folios):
        cfg = configs[f]
        abl = per_folio_abl[f]
        land = per_folio_land[f]

        # Space A: apparatus properties
        A_raw[i, 0] = cfg['F1']
        A_raw[i, 1] = cfg['F2']
        A_raw[i, 2] = cfg['F3']
        A_raw[i, 3] = cfg['F4_raw']
        A_raw[i, 4] = cfg['F5']
        for j, ch in enumerate(ABLATION_CHANNELS):
            A_raw[i, 5 + j] = abl['ablations'][ch]['delta_m4f_dye']
        A_raw[i, 10] = land['mean_CTS']

        # Space B: behavioral outcomes
        B_raw[i, 0] = abl['baseline_m1_dye'] - abl['baseline_m4f_dye']  # DYE_advantage
        B_raw[i, 1] = abl['baseline_m4f_dye']  # CCS1 (forgivingness index)
        B_raw[i, 2] = land['z_margin']
        B_raw[i, 3] = land['positive_event_fraction']  # PEF

        profile = cfg['profile']
        family = 'A1' if 'A1' in profile else ('A2' if 'A2' in profile else 'A3')
        metadata[f] = {
            'profile': profile,
            'family': family,
            'section': cfg['section'],
            'landscape_class': land['classification'],
            'n_events': land['n_events']
        }

    # Z-score standardize
    A_std, A_mu, A_sd = zscore(A_raw)
    B_std, B_mu, B_sd = zscore(B_raw)

    C_raw = np.hstack([A_raw, B_raw])
    C_std, C_mu, C_sd = zscore(C_raw)

    # Correlation matrices
    R_A = np.corrcoef(A_std.T)
    R_B = np.corrcoef(B_std.T)
    R_C = np.corrcoef(C_std.T)

    high_corr_A = flag_high_corr(R_A, SPACE_A_NAMES)
    high_corr_B = flag_high_corr(R_B, SPACE_B_NAMES)

    eff_rank_A, evals_A = effective_rank_kaiser(R_A)
    eff_rank_B, evals_B = effective_rank_kaiser(R_B)

    result = {
        'metadata': {
            'phase': '580',
            'script': 't0_feature_matrix_assembly.py',
            'n_folios': n,
            'space_A_features': SPACE_A_NAMES,
            'space_B_features': SPACE_B_NAMES,
            'combined_features': COMBINED_NAMES
        },
        'folios': folios,
        'space_A': {
            'raw': A_raw.tolist(),
            'standardized': A_std.tolist(),
            'means': A_mu,
            'stds': A_sd,
            'correlation_matrix': R_A.tolist(),
            'high_correlations': high_corr_A,
            'effective_rank_kaiser': eff_rank_A,
            'eigenvalues': evals_A
        },
        'space_B': {
            'raw': B_raw.tolist(),
            'standardized': B_std.tolist(),
            'means': B_mu,
            'stds': B_sd,
            'correlation_matrix': R_B.tolist(),
            'high_correlations': high_corr_B,
            'effective_rank_kaiser': eff_rank_B,
            'eigenvalues': evals_B
        },
        'combined': {
            'raw': C_raw.tolist(),
            'standardized': C_std.tolist(),
            'means': C_mu,
            'stds': C_sd,
            'correlation_matrix': R_C.tolist()
        },
        'folio_metadata': metadata,
        'redundancy_report': {
            'space_A': {
                'n_features': 11,
                'effective_rank': eff_rank_A,
                'interpretation': f"{eff_rank_A} effective dimensions out of 11 features"
            },
            'space_B': {
                'n_features': 4,
                'effective_rank': eff_rank_B,
                'interpretation': f"{eff_rank_B} effective dimensions out of 4 features"
            }
        }
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"T0: Built feature matrices for {n} folios")
    print(f"  Space A: 11 features, effective rank = {eff_rank_A}")
    print(f"  Space B: 4 features, effective rank = {eff_rank_B}")
    print(f"  High correlations (|r|>0.7) in A: {len(high_corr_A)}")
    for hc in high_corr_A:
        print(f"    {hc['feature_1']} ~ {hc['feature_2']}: r={hc['r']}")
    print(f"  High correlations (|r|>0.7) in B: {len(high_corr_B)}")
    for hc in high_corr_B:
        print(f"    {hc['feature_1']} ~ {hc['feature_2']}: r={hc['r']}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
