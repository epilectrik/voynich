#!/usr/bin/env python3
"""Phase 366: Section Residual Decomposition

Tests whether section x predictor interaction effects explain any of the
AXM self-transition residual that C1035 declared irreducible.

C1017 baseline: REGIME+section = 42% -> +PREFIX_entropy +hazard_density +bridge_PC1 = ~60%.
C1035: 6 additional additive predictors all fail. Residual declared design freedom (C458).
This phase tests INTERACTION effects: does section modulate the slopes of C1017 predictors?

Hypotheses:
  H1: Section x PREFIX_entropy interaction significant
  H2: Per-section LOO R² > global LOO R²
  H3: Section x hazard_density interaction (BIO > STARS_RECIPE)
  H4: Per-section bridge PC1 differs from global (cosine < 0.8)
  H5: Conservation — residual > 35% after all interactions

Depends on: C1017, C1035, C1042-C1046 (Phase 365 section parameterization)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = PROJECT / 'phases' / 'SECTION_RESIDUAL_DECOMPOSITION' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

VIABLE_SECTIONS = {'B', 'H', 'S'}


# ════════════════════════════════════════════════════════════════
# Regression helpers (from Phase 357)
# ════════════════════════════════════════════════════════════════

def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-10)


def ols_fit(X, y):
    """OLS regression. Returns beta, y_pred, ss_res, r2."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    """F-test for nested model comparison."""
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


def build_dummies(labels):
    """Build dummy variables from categorical labels (drop first alphabetically)."""
    unique = sorted(set(labels))
    if len(unique) <= 1:
        return np.zeros((len(labels), 0)), unique
    dummies = np.zeros((len(labels), len(unique) - 1))
    for i, label in enumerate(labels):
        idx = unique.index(label)
        if idx > 0:
            dummies[i, idx - 1] = 1
    return dummies, unique


def loo_cv_r2(X, y):
    """Leave-one-out cross-validated R²."""
    n = len(y)
    y_pred_loo = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train, y_train = X[mask], y[mask]
        X_test = X[i:i+1]
        beta = np.linalg.lstsq(X_train, y_train, rcond=None)[0]
        y_pred_loo[i] = float(X_test @ beta)
    ss_res = np.sum((y - y_pred_loo) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


def adjusted_r2(r2, n, k):
    """Adjusted R²."""
    if n - k - 1 <= 0:
        return r2
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)


def cooks_distance(X, y, beta, y_pred):
    """Compute Cook's distance for each observation."""
    n, p = X.shape
    residuals = y - y_pred
    H = X @ np.linalg.pinv(X.T @ X) @ X.T
    h = np.diag(H)
    mse = np.sum(residuals**2) / (n - p)
    if mse == 0:
        return np.zeros(n)
    return residuals**2 * h / (p * mse * (1 - h)**2 + 1e-10)


# ════════════════════════════════════════════════════════════════
# S1: Load data and replicate baseline
# ════════════════════════════════════════════════════════════════

def load_and_baseline():
    """Load 72-folio dataset, filter to 65 viable, replicate C1017 baseline."""
    print("S1: Loading data and replicating baseline...")

    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        data = json.load(f)

    folio_data = data['folio_data']

    # Build arrays for all 72 folios
    all_folios = sorted(folio_data.keys())
    print(f"  Total folios: {len(all_folios)}")

    # Filter to viable sections
    viable_folios = [f for f in all_folios if folio_data[f]['section'] in VIABLE_SECTIONS]
    print(f"  Viable folios (B+H+S): {len(viable_folios)}")

    # Extract arrays
    y = np.array([folio_data[f]['axm_self'] for f in viable_folios])
    regimes = [folio_data[f]['regime'] for f in viable_folios]
    sections = [folio_data[f]['section'] for f in viable_folios]
    prefix_ent = np.array([folio_data[f]['prefix_entropy'] for f in viable_folios])
    hazard_den = np.array([folio_data[f]['hazard_density'] for f in viable_folios])
    bridge_pc1 = np.array([folio_data[f]['bridge_pc1'] for f in viable_folios])

    n = len(y)

    # Standardize continuous predictors
    prefix_z = standardize(prefix_ent)
    hazard_z = standardize(hazard_den)
    bridge_z = standardize(bridge_pc1)

    # Build baseline design matrix: intercept + REGIME dummies + section dummies + 3 continuous
    regime_dummies, regime_levels = build_dummies(regimes)
    section_dummies, section_levels = build_dummies(sections)

    X_baseline = np.column_stack([
        np.ones(n),
        regime_dummies,
        section_dummies,
        prefix_z,
        hazard_z,
        bridge_z,
    ])

    beta, y_pred, ss_res, r2 = ols_fit(X_baseline, y)
    loo_r2 = loo_cv_r2(X_baseline, y)
    k = X_baseline.shape[1]
    adj_r2 = adjusted_r2(r2, n, k)

    print(f"  Baseline (65 folios): R²={r2:.4f}, adj_R²={adj_r2:.4f}, LOO_R²={loo_r2:.4f}")
    print(f"  Parameters: {k} (intercept + {regime_dummies.shape[1]} REGIME + {section_dummies.shape[1]} section + 3 continuous)")
    print(f"  REGIME levels: {regime_levels}")
    print(f"  Section levels: {section_levels}")

    # Section counts
    from collections import Counter
    sec_counts = Counter(sections)
    regime_sec = Counter(zip(sections, regimes))
    print(f"  Section counts: {dict(sec_counts)}")

    return {
        'viable_folios': viable_folios,
        'folio_data': folio_data,
        'y': y,
        'regimes': regimes,
        'sections': sections,
        'prefix_z': prefix_z,
        'hazard_z': hazard_z,
        'bridge_z': bridge_z,
        'prefix_raw': prefix_ent,
        'hazard_raw': hazard_den,
        'bridge_raw': bridge_pc1,
        'regime_dummies': regime_dummies,
        'regime_levels': regime_levels,
        'section_dummies': section_dummies,
        'section_levels': section_levels,
        'X_baseline': X_baseline,
        'baseline_r2': float(r2),
        'baseline_adj_r2': float(adj_r2),
        'baseline_loo_r2': float(loo_r2),
        'baseline_ss_res': float(ss_res),
        'baseline_k': k,
        'n': n,
    }


# ════════════════════════════════════════════════════════════════
# S2: Section interaction OLS tests (H1, H3)
# ════════════════════════════════════════════════════════════════

def test_interactions(data):
    """Test section x predictor interactions, one at a time."""
    print("\nS2: Section interaction tests...")

    y = data['y']
    X_base = data['X_baseline']
    ss_res_base = data['baseline_ss_res']
    k_base = data['baseline_k']
    n = data['n']
    sections = data['sections']
    section_levels = data['section_levels']  # ['B', 'H', 'S'] sorted

    predictors = {
        'prefix_entropy': data['prefix_z'],
        'hazard_density': data['hazard_z'],
        'bridge_pc1': data['bridge_z'],
    }

    # Section dummies for interaction (B=reference, so H and S dummies)
    sec_dummies = data['section_dummies']  # shape (n, 2) for H and S

    results = {}

    for pred_name, pred_z in predictors.items():
        # Interaction terms: section_H * pred, section_S * pred
        interactions = sec_dummies * pred_z[:, np.newaxis]  # (n, 2)

        X_ext = np.column_stack([X_base, interactions])
        k_ext = X_ext.shape[1]
        df_extra = k_ext - k_base

        beta_ext, y_pred_ext, ss_res_ext, r2_ext = ols_fit(X_ext, y)
        f_stat, p_val = f_test_increment(ss_res_base, ss_res_ext, df_extra, n, k_ext)
        delta_r2 = r2_ext - data['baseline_r2']
        loo_ext = loo_cv_r2(X_ext, y)

        # Extract per-section slopes
        # In X_ext, the pred_z main effect is at position (k_base - 3 + pred_idx)
        # where pred_idx is 0=prefix, 1=hazard, 2=bridge
        pred_idx = list(predictors.keys()).index(pred_name)
        main_effect_col = k_base - 3 + pred_idx  # position in X_base
        main_slope = beta_ext[main_effect_col]

        # Interaction coefficients are at positions k_base and k_base+1
        interaction_slopes = beta_ext[k_base:k_base + df_extra]

        # Per-section slopes: B = main_slope, H = main_slope + delta_H, S = main_slope + delta_S
        per_section_slopes = {section_levels[0]: float(main_slope)}
        for j in range(len(interaction_slopes)):
            sec_label = section_levels[j + 1]
            per_section_slopes[sec_label] = float(main_slope + interaction_slopes[j])

        # Cook's distance for influential folios
        cooks = cooks_distance(X_ext, y, beta_ext, y_pred_ext)
        max_cook = float(np.max(cooks))
        influential = int(np.sum(cooks > 4 / n))

        results[pred_name] = {
            'delta_r2': float(delta_r2),
            'f_stat': float(f_stat),
            'p_value': float(p_val),
            'r2_extended': float(r2_ext),
            'loo_r2_extended': float(loo_ext),
            'per_section_slopes': per_section_slopes,
            'interaction_deltas': {section_levels[j+1]: float(interaction_slopes[j])
                                   for j in range(len(interaction_slopes))},
            'max_cooks_d': max_cook,
            'influential_folios': influential,
        }

        sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
        print(f"  {pred_name}: dR²={delta_r2:.4f}, F={f_stat:.2f}, p={p_val:.4f}{sig}")
        print(f"    Slopes: {per_section_slopes}")
        print(f"    LOO R²: {loo_ext:.4f} (baseline: {data['baseline_loo_r2']:.4f})")

    # H1: PREFIX_entropy interaction
    h1_result = results['prefix_entropy']
    h1_slopes = h1_result['per_section_slopes']
    h1_deltas = h1_result['interaction_deltas']
    h1_max_delta = max(abs(v) for v in h1_deltas.values())
    h1_pass = bool(h1_result['p_value'] < 0.05 and h1_max_delta > 0.10)

    # H3: hazard_density interaction — BIO slope > STARS_RECIPE slope
    h3_result = results['hazard_density']
    h3_slopes = h3_result['per_section_slopes']
    h3_bio = h3_slopes.get('B', 0)
    h3_recipe = h3_slopes.get('S', 0)
    h3_pass = bool(h3_result['p_value'] < 0.05 and h3_bio < h3_recipe)
    # Note: negative slope means stronger negative effect. "Stronger" = more negative.
    # Re-interpret: "BIO shows stronger hazard-AXM relationship" means |slope_B| > |slope_S|
    h3_pass = bool(h3_result['p_value'] < 0.05 and abs(h3_bio) > abs(h3_recipe))

    print(f"\n  H1 (PREFIX x section): delta={h1_max_delta:.4f}, p={h1_result['p_value']:.4f} -> {'PASS' if h1_pass else 'FAIL'}")
    print(f"  H3 (hazard x section): |B|={abs(h3_bio):.4f} vs |S|={abs(h3_recipe):.4f}, p={h3_result['p_value']:.4f} -> {'PASS' if h3_pass else 'FAIL'}")

    return {
        's2_interactions': results,
        'h1_pass': bool(h1_pass),
        'h1': {
            'max_delta_slope': float(h1_max_delta),
            'p_value': float(h1_result['p_value']),
            'per_section_slopes': h1_slopes,
        },
        'h3_pass': bool(h3_pass),
        'h3': {
            'bio_slope': float(h3_bio),
            'recipe_slope': float(h3_recipe),
            'p_value': float(h3_result['p_value']),
            'per_section_slopes': h3_slopes,
        },
    }


# ════════════════════════════════════════════════════════════════
# S3: Per-section regression models (H2)
# ════════════════════════════════════════════════════════════════

def test_per_section_models(data):
    """Fit separate regressions per section, compute LOO CV, compare to global."""
    print("\nS3: Per-section regression models...")

    y = data['y']
    sections = data['sections']
    regimes = data['regimes']
    viable_folios = data['viable_folios']

    section_results = {}

    for sec in sorted(VIABLE_SECTIONS):
        mask = np.array([s == sec for s in sections])
        n_sec = mask.sum()

        y_sec = y[mask]
        regimes_sec = [r for r, m in zip(regimes, mask) if m]
        prefix_sec = data['prefix_raw'][mask]
        hazard_sec = data['hazard_raw'][mask]
        bridge_sec = data['bridge_raw'][mask]

        # Standardize within section
        prefix_z = standardize(prefix_sec)
        hazard_z = standardize(hazard_sec)
        bridge_z = standardize(bridge_sec)

        # Adapted REGIME encoding: drop levels with < 3 folios
        from collections import Counter
        reg_counts = Counter(regimes_sec)
        viable_regimes = [r for r, c in reg_counts.items() if c >= 3]

        if len(viable_regimes) <= 1:
            regime_dummies_sec = np.zeros((n_sec, 0))
            regime_info = f"no REGIME dummies (only {viable_regimes})"
        else:
            # Collapse rare regimes to 'OTHER'
            regimes_collapsed = []
            for r in regimes_sec:
                if r in viable_regimes:
                    regimes_collapsed.append(r)
                else:
                    regimes_collapsed.append('OTHER')
            regime_dummies_sec, _ = build_dummies(regimes_collapsed)
            regime_info = f"{regime_dummies_sec.shape[1]} REGIME dummies from {viable_regimes}"

        # Build per-section design matrix
        X_sec = np.column_stack([
            np.ones(n_sec),
            regime_dummies_sec,
            prefix_z,
            hazard_z,
            bridge_z,
        ])

        k_sec = X_sec.shape[1]
        if k_sec >= n_sec - 2:
            # Too many parameters — drop bridge_pc1
            X_sec = np.column_stack([
                np.ones(n_sec),
                regime_dummies_sec,
                prefix_z,
                hazard_z,
            ])
            k_sec = X_sec.shape[1]
            regime_info += " (bridge_pc1 dropped: insufficient df)"

        _, _, _, r2_sec = ols_fit(X_sec, y_sec)
        loo_sec = loo_cv_r2(X_sec, y_sec)
        adj_r2_sec = adjusted_r2(r2_sec, n_sec, k_sec)

        section_results[sec] = {
            'n': int(n_sec),
            'k': int(k_sec),
            'r2_train': float(r2_sec),
            'r2_adj': float(adj_r2_sec),
            'r2_loo': float(loo_sec),
            'gap': float(r2_sec - loo_sec),
            'regime_info': regime_info,
            'mean_axm': float(y_sec.mean()),
            'std_axm': float(y_sec.std()),
        }

        print(f"  {sec} (n={n_sec}): R²={r2_sec:.4f}, adj={adj_r2_sec:.4f}, LOO={loo_sec:.4f}, gap={r2_sec-loo_sec:.4f}")
        print(f"    {regime_info}")

    # H2: weighted mean per-section LOO > global LOO
    total_n = sum(section_results[s]['n'] for s in section_results)
    weighted_loo = sum(section_results[s]['r2_loo'] * section_results[s]['n'] / total_n
                       for s in section_results)
    global_loo = data['baseline_loo_r2']
    h2_pass = bool(weighted_loo > global_loo)

    print(f"\n  H2: weighted LOO={weighted_loo:.4f} vs global LOO={global_loo:.4f} -> {'PASS' if h2_pass else 'FAIL'}")

    return {
        's3_per_section': section_results,
        'h2_pass': bool(h2_pass),
        'h2': {
            'weighted_mean_loo': float(weighted_loo),
            'global_loo': float(global_loo),
            'delta': float(weighted_loo - global_loo),
        },
    }


# ════════════════════════════════════════════════════════════════
# S4: Bridge PC1 section-specific recomputation (H4)
# ════════════════════════════════════════════════════════════════

def test_bridge_geometry(data):
    """Recompute bridge PC1 per section, test cosine similarity."""
    print("\nS4: Bridge geometry section specificity...")

    # Load compatibility matrix and MIDDLE index
    compat_path = PROJECT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    if not compat_path.exists():
        print("  WARNING: Compatibility matrix not found. Skipping H4.")
        return {'h4_pass': False, 'h4': {'reason': 'compat_matrix_not_found'}}

    M = np.load(compat_path).astype(np.float64)

    # Reconstruct MIDDLE-to-index mapping from Currier A
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    print(f"  Compat matrix: {M.shape}, {len(all_middles)} MIDDLEs indexed")

    # Load bridge MIDDLE set
    with open(PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f"  Bridge MIDDLEs: {len(bridge_set)}")

    # Spectral embedding (100D)
    K_EMBED = 100
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    k = min(K_EMBED, len(eigenvalues))
    pos_evals = np.maximum(eigenvalues[:k], 0)
    scaling = np.sqrt(pos_evals)
    embedding = eigenvectors[:, :k] * scaling[np.newaxis, :]

    # Find which bridge MIDDLEs appear in each section
    section_middles = defaultdict(set)
    folio_middles = defaultdict(set)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            section_middles[token.section].add(m.middle)
            folio_middles[token.folio].add(m.middle)

    section_bridges = {}
    for sec in VIABLE_SECTIONS:
        section_bridges[sec] = section_middles[sec] & bridge_set
        print(f"  {sec}: {len(section_bridges[sec])}/{len(bridge_set)} bridge MIDDLEs present")

    # Per-folio bridge centroids (global embedding, all bridges)
    viable_folios = data['viable_folios']
    sections = data['sections']

    global_centroids = {}
    for folio in viable_folios:
        mids = folio_middles.get(folio, set()) & bridge_set
        if not mids:
            global_centroids[folio] = np.zeros(k)
            continue
        indices = [mid_to_idx[m] for m in mids if m in mid_to_idx]
        if not indices:
            global_centroids[folio] = np.zeros(k)
            continue
        global_centroids[folio] = embedding[indices].mean(axis=0)

    # Global PCA across all 65 folios
    X_global = np.array([global_centroids[f] for f in viable_folios])
    X_global_centered = X_global - X_global.mean(axis=0)
    _, _, Vt_global = np.linalg.svd(X_global_centered, full_matrices=False)
    global_pc1 = Vt_global[0]
    global_pc1_scores = X_global_centered @ global_pc1

    # Per-section PCA
    section_pc1s = {}
    section_pc1_scores = {}
    cosine_to_global = {}

    for sec in sorted(VIABLE_SECTIONS):
        sec_mask = np.array([s == sec for s in sections])
        sec_folios = [f for f, m in zip(viable_folios, sec_mask) if m]

        # Per-section centroids (using only that section's bridge MIDDLEs)
        sec_centroids = {}
        for folio in sec_folios:
            mids = folio_middles.get(folio, set()) & section_bridges[sec]
            if not mids:
                sec_centroids[folio] = np.zeros(k)
                continue
            indices = [mid_to_idx[m] for m in mids if m in mid_to_idx]
            sec_centroids[folio] = embedding[indices].mean(axis=0) if indices else np.zeros(k)

        X_sec = np.array([sec_centroids[f] for f in sec_folios])
        X_sec_centered = X_sec - X_sec.mean(axis=0)
        _, _, Vt_sec = np.linalg.svd(X_sec_centered, full_matrices=False)
        sec_pc1 = Vt_sec[0]
        section_pc1s[sec] = sec_pc1

        # Cosine similarity to global PC1
        cos_sim = abs(float(np.dot(sec_pc1, global_pc1) /
                            (np.linalg.norm(sec_pc1) * np.linalg.norm(global_pc1) + 1e-10)))
        cosine_to_global[sec] = cos_sim
        print(f"  {sec} PC1 cosine to global: {cos_sim:.4f}")

    # Pairwise cosines between sections
    pairwise = {}
    sec_list = sorted(VIABLE_SECTIONS)
    for i in range(len(sec_list)):
        for j in range(i+1, len(sec_list)):
            s1, s2 = sec_list[i], sec_list[j]
            cos = abs(float(np.dot(section_pc1s[s1], section_pc1s[s2]) /
                            (np.linalg.norm(section_pc1s[s1]) * np.linalg.norm(section_pc1s[s2]) + 1e-10)))
            pairwise[f"{s1}_{s2}"] = cos
            print(f"  {s1}-{s2} PC1 cosine: {cos:.4f}")

    # H4: any section PC1 cosine to global < 0.8
    min_cos = min(cosine_to_global.values())
    h4_pass = bool(min_cos < 0.8)

    # Substitution test: use per-section bridge_PC1 instead of global
    # Recompute per-section PC1 scores projected onto section-specific PC1
    new_bridge_scores = np.zeros(len(viable_folios))
    for i, (folio, sec) in enumerate(zip(viable_folios, sections)):
        centroid = global_centroids[folio]
        centroid_centered = centroid - X_global.mean(axis=0)
        new_bridge_scores[i] = float(centroid_centered @ section_pc1s[sec])

    new_bridge_z = standardize(new_bridge_scores)

    # Refit baseline with substituted bridge_PC1
    X_subst = np.column_stack([
        np.ones(data['n']),
        data['regime_dummies'],
        data['section_dummies'],
        data['prefix_z'],
        data['hazard_z'],
        new_bridge_z,
    ])
    _, _, _, r2_subst = ols_fit(X_subst, data['y'])
    loo_subst = loo_cv_r2(X_subst, data['y'])

    print(f"\n  Substituted bridge PC1: R²={r2_subst:.4f}, LOO={loo_subst:.4f} (baseline: R²={data['baseline_r2']:.4f}, LOO={data['baseline_loo_r2']:.4f})")
    print(f"  H4: min cosine={min_cos:.4f} -> {'PASS' if h4_pass else 'FAIL'}")

    return {
        'h4_pass': bool(h4_pass),
        'h4': {
            'cosine_to_global': {s: float(v) for s, v in cosine_to_global.items()},
            'pairwise_cosine': pairwise,
            'min_cosine': float(min_cos),
            'bridge_coverage': {s: len(section_bridges[s]) for s in sorted(VIABLE_SECTIONS)},
            'total_bridges': len(bridge_set),
            'substituted_r2': float(r2_subst),
            'substituted_loo_r2': float(loo_subst),
            'baseline_r2': float(data['baseline_r2']),
            'baseline_loo_r2': float(data['baseline_loo_r2']),
        },
    }


# ════════════════════════════════════════════════════════════════
# S5: Combined model + conservation test (H5)
# ════════════════════════════════════════════════════════════════

def test_conservation(data, interaction_results):
    """Build best combined model with significant interactions. Test H5."""
    print("\nS5: Combined model + conservation test...")

    y = data['y']
    X_base = data['X_baseline']
    n = data['n']
    sections = data['sections']

    # Identify significant interactions from S2
    significant = []
    predictors = {
        'prefix_entropy': data['prefix_z'],
        'hazard_density': data['hazard_z'],
        'bridge_pc1': data['bridge_z'],
    }
    sec_dummies = data['section_dummies']

    for pred_name in ['prefix_entropy', 'hazard_density', 'bridge_pc1']:
        info = interaction_results['s2_interactions'][pred_name]
        if info['p_value'] < 0.05:
            significant.append(pred_name)

    print(f"  Significant interactions (p<0.05): {significant if significant else 'none'}")

    if not significant:
        # No interactions pass — combined model = baseline
        loo_combined = data['baseline_loo_r2']
        r2_combined = data['baseline_r2']
        delta_loo = 0.0
        k_combined = data['baseline_k']
    else:
        # Build combined model with all significant interactions
        extra_cols = []
        for pred_name in significant:
            interactions = sec_dummies * predictors[pred_name][:, np.newaxis]
            extra_cols.append(interactions)

        X_combined = np.column_stack([X_base] + extra_cols)
        k_combined = X_combined.shape[1]

        _, _, _, r2_combined = ols_fit(X_combined, y)
        loo_combined = loo_cv_r2(X_combined, y)
        delta_loo = loo_combined - data['baseline_loo_r2']

    adj_r2_combined = adjusted_r2(r2_combined, n, k_combined)

    # H5: LOO R² < 0.65 (residual > 35%)
    h5_pass = bool(loo_combined < 0.65)

    print(f"  Combined: R²={r2_combined:.4f}, adj={adj_r2_combined:.4f}, LOO={loo_combined:.4f}")
    print(f"  Delta LOO vs baseline: {delta_loo:+.4f}")
    print(f"  H5 (conservation): LOO={loo_combined:.4f} < 0.65 -> {'PASS' if h5_pass else 'FAIL'}")

    return {
        'h5_pass': bool(h5_pass),
        'h5': {
            'significant_interactions': significant,
            'r2_combined': float(r2_combined),
            'adj_r2_combined': float(adj_r2_combined),
            'loo_combined': float(loo_combined),
            'delta_loo_vs_baseline': float(delta_loo),
            'k_combined': int(k_combined),
            'residual_fraction': float(1 - loo_combined),
        },
    }


# ════════════════════════════════════════════════════════════════
# S6: Synthesis and verdict
# ════════════════════════════════════════════════════════════════

def compute_verdict(results):
    """Evaluate H1-H5, compute global verdict."""
    h_pass = {f'H{i+1}': bool(results.get(f'h{i+1}_pass', False)) for i in range(5)}
    n_pass = sum(h_pass.values())

    delta_loo = results.get('h5', {}).get('delta_loo_vs_baseline', 0)
    h5_pass = results.get('h5_pass', True)

    if not h5_pass:
        verdict = 'SECTION_INTERACTIONS_SUBSTANTIALLY_DECOMPOSE'
    elif delta_loo > 0.05:
        verdict = 'SECTION_INTERACTIONS_MODESTLY_DECOMPOSE'
    else:
        verdict = 'SECTION_INTERACTIONS_CONFIRM_IRREDUCIBILITY'

    return {
        'verdict': verdict,
        'hypotheses': h_pass,
        'n_pass': n_pass,
        'delta_loo': float(delta_loo),
    }


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Phase 366: Section Residual Decomposition")
    print("=" * 60)

    # S1: Load and baseline
    data = load_and_baseline()

    results = {
        's1': {
            'n_total': 72,
            'n_viable': data['n'],
            'sections': dict(zip(*np.unique(data['sections'], return_counts=True))),
            'baseline_r2': data['baseline_r2'],
            'baseline_adj_r2': data['baseline_adj_r2'],
            'baseline_loo_r2': data['baseline_loo_r2'],
            'baseline_k': data['baseline_k'],
        },
    }

    # S2: Interaction tests (H1, H3)
    r_inter = test_interactions(data)
    results.update(r_inter)

    # S3: Per-section models (H2)
    r_sec = test_per_section_models(data)
    results.update(r_sec)

    # S4: Bridge geometry (H4)
    r_bridge = test_bridge_geometry(data)
    results.update(r_bridge)

    # S5: Combined model + conservation (H5)
    r_cons = test_conservation(data, r_inter)
    results.update(r_cons)

    # S6: Verdict
    verdict = compute_verdict(results)
    results['verdict'] = verdict

    print("\n" + "=" * 60)
    print(f"VERDICT: {verdict['verdict']}")
    print(f"Total: {verdict['n_pass']}/5 pass")
    for h, p in verdict['hypotheses'].items():
        print(f"  {h}: {'PASS' if p else 'FAIL'}")
    print(f"Delta LOO: {verdict['delta_loo']:+.4f}")
    print("=" * 60)

    # Save
    out_path = RESULTS_DIR / 'section_residual_decomposition.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
