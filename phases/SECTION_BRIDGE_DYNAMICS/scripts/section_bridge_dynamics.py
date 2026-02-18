#!/usr/bin/env python3
"""Phase 391: SECTION_BRIDGE_DYNAMICS (6 predictions).

Tests whether per-folio bridge MIDDLE density mediates the relationship
between section identity and dynamical predictability/freedom.
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS = ROOT / "phases" / "SECTION_BRIDGE_DYNAMICS" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Sections with enough folios for within-section analysis
MAIN_SECTIONS = {'B', 'H', 'S'}


def round_floats(obj, decimals=4):
    """Recursively round floats in nested structures."""
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


def compute_bridge_density():
    """Compute per-folio bridge density from Currier B tokens.

    Returns dict {folio: bridge_density} and {folio: set(middles)}.
    """
    # Load bridge MIDDLEs
    bridge_path = ROOT / "phases" / "BRIDGE_MIDDLE_SELECTION_MECHANISM" / "results" / "bridge_selection.json"
    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f"Loaded {len(bridge_set)} bridge MIDDLEs")

    # Compute per-folio unique MIDDLE sets from Currier B
    tx = Transcript()
    morph = Morphology()
    folio_middles = defaultdict(set)

    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle:
            folio_middles[token.folio].add(m.middle)

    print(f"Computed MIDDLE sets for {len(folio_middles)} Currier B folios")

    # Compute bridge density per folio
    folio_bridge_density = {}
    for folio, mids in folio_middles.items():
        if mids:
            folio_bridge_density[folio] = len(mids & bridge_set) / len(mids)
        else:
            folio_bridge_density[folio] = 0.0

    return folio_bridge_density, dict(folio_middles), bridge_set


def load_axm_data():
    """Load per-folio AXM data from Phase 357 results."""
    axm_path = ROOT / "phases" / "AXM_RESIDUAL_DECOMPOSITION" / "results" / "axm_residual_decomposition.json"
    with open(axm_path) as f:
        data = json.load(f)
    folio_data = data['folio_data']
    print(f"Loaded AXM data for {len(folio_data)} folios")
    return folio_data


def merge_data(bridge_density, axm_data):
    """Merge bridge density with AXM data on folio key."""
    merged = {}
    for folio, axm_info in axm_data.items():
        if folio in bridge_density:
            entry = dict(axm_info)
            entry['bridge_density'] = bridge_density[folio]
            merged[folio] = entry
    print(f"Merged: {len(merged)} folios with both bridge density and AXM data")
    return merged


def get_bhs_folios(merged):
    """Return list of folios in B/H/S sections only."""
    return [f for f in merged if merged[f]['section'] in MAIN_SECTIONS]


def run_p1(merged, folios):
    """P1: REGIME bridge density effect after section control."""
    print("\n=== P1: REGIME-Bridge Density Section Control ===")

    bd = np.array([merged[f]['bridge_density'] for f in folios])
    regime_ord = np.array([int(merged[f]['regime'][-1]) for f in folios])
    sections = [merged[f]['section'] for f in folios]
    n = len(folios)

    # Raw correlation
    rho_raw, p_raw = sp_stats.spearmanr(bd, regime_ord)
    print(f"  Raw Spearman rho(bridge_density, REGIME): {rho_raw:.4f}, p={p_raw:.4f}")

    # Partial correlation controlling for section
    sec_map = {'B': 0, 'H': 1, 'S': 2}
    X_sec = np.zeros((n, 2))
    for i, f in enumerate(folios):
        s = sec_map[merged[f]['section']]
        if s == 1:
            X_sec[i, 0] = 1
        if s == 2:
            X_sec[i, 1] = 1

    X_aug = np.column_stack([np.ones(n), X_sec])

    # Residualize bridge density on section
    beta_bd = np.linalg.lstsq(X_aug, bd, rcond=None)[0]
    resid_bd = bd - X_aug @ beta_bd

    # Residualize REGIME on section
    beta_reg = np.linalg.lstsq(X_aug, regime_ord.astype(float), rcond=None)[0]
    resid_reg = regime_ord.astype(float) - X_aug @ beta_reg

    # Partial correlation
    partial_r, partial_p = sp_stats.pearsonr(resid_bd, resid_reg)
    print(f"  Partial r(bridge_density, REGIME | section): {partial_r:.4f}, p={partial_p:.4f}")

    # Also compute eta-squared (ANOVA-style) as categorical alternative
    regime_groups = defaultdict(list)
    for f in folios:
        regime_groups[merged[f]['regime']].append(merged[f]['bridge_density'])
    groups = [np.array(v) for v in regime_groups.values() if len(v) >= 2]
    if len(groups) >= 2:
        f_stat, f_p = sp_stats.f_oneway(*groups)
        # Eta-squared
        ss_between = sum(len(g) * (np.mean(g) - np.mean(bd)) ** 2 for g in groups)
        ss_total = np.sum((bd - np.mean(bd)) ** 2)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0
    else:
        f_stat, f_p, eta_sq = 0, 1.0, 0

    # Verdict
    if abs(partial_r) < 0.15 and partial_p > 0.05:
        verdict = "PASS"
    elif abs(partial_r) > 0.25 and partial_p < 0.01:
        verdict = "FAIL"
    else:
        verdict = "MARGINAL"

    print(f"  Verdict: {verdict}")

    return {
        'raw_spearman_rho': rho_raw,
        'raw_spearman_p': p_raw,
        'partial_r': partial_r,
        'partial_p': partial_p,
        'anova_F': f_stat,
        'anova_p': f_p,
        'eta_squared': eta_sq,
        'n': n,
        'verdict': verdict
    }


def run_p2(merged, folios):
    """P2: Bridge density anticorrelates with AXM residual magnitude."""
    print("\n=== P2: Bridge Density vs |C1017 Residual| ===")

    bd = np.array([merged[f]['bridge_density'] for f in folios])
    abs_resid = np.array([abs(merged[f]['c1017_residual']) for f in folios])
    sections = [merged[f]['section'] for f in folios]

    # Overall
    rho_all, p_all = sp_stats.spearmanr(bd, abs_resid)
    print(f"  Overall: rho={rho_all:.4f}, p={p_all:.4f}")

    # Per section
    per_section = {}
    for sec in ['B', 'H', 'S']:
        idx = [i for i, s in enumerate(sections) if s == sec]
        if len(idx) >= 5:
            rho_s, p_s = sp_stats.spearmanr(bd[idx], abs_resid[idx])
            per_section[sec] = {'rho': rho_s, 'p': p_s, 'n': len(idx)}
            print(f"  {sec}: rho={rho_s:.4f}, p={p_s:.4f}, n={len(idx)}")

    # Verdict
    if rho_all < -0.20:
        verdict = "PASS"
    elif rho_all > 0:
        verdict = "FAIL"
    else:
        verdict = "MARGINAL"

    print(f"  Verdict: {verdict}")

    return {
        'overall_rho': rho_all,
        'overall_p': p_all,
        'per_section': per_section,
        'n': len(folios),
        'verdict': verdict
    }


def run_p3(merged, folios):
    """P3: HERBAL has highest within-section AXM variance."""
    print("\n=== P3: Within-Section AXM Variance ===")

    section_axm = defaultdict(list)
    for f in folios:
        section_axm[merged[f]['section']].append(merged[f]['axm_self'])

    variances = {}
    for sec in ['B', 'H', 'S']:
        vals = np.array(section_axm[sec])
        var = np.var(vals, ddof=1)
        variances[sec] = var
        print(f"  {sec}: n={len(vals)}, mean={np.mean(vals):.4f}, var={var:.4f}, std={np.std(vals, ddof=1):.4f}")

    # Levene's test
    groups = [np.array(section_axm[s]) for s in ['B', 'H', 'S']]
    levene_stat, levene_p = sp_stats.levene(*groups)
    print(f"  Levene's test: W={levene_stat:.4f}, p={levene_p:.4f}")

    max_var_section = max(variances, key=variances.get)
    print(f"  Highest variance section: {max_var_section}")

    verdict = "PASS" if max_var_section == 'H' else "FAIL"
    print(f"  Verdict: {verdict}")

    return {
        'per_section_variance': variances,
        'per_section_mean': {s: float(np.mean(section_axm[s])) for s in ['B', 'H', 'S']},
        'per_section_n': {s: len(section_axm[s]) for s in ['B', 'H', 'S']},
        'highest_variance_section': max_var_section,
        'levene_stat': levene_stat,
        'levene_p': levene_p,
        'verdict': verdict
    }


def run_p4(merged, folios):
    """P4: Bridge density adds incremental R² beyond C1017 baseline."""
    print("\n=== P4: Incremental R² from Bridge Density ===")

    n = len(folios)
    y = np.array([merged[f]['axm_self'] for f in folios])

    # C1017 continuous predictors
    pe = np.array([merged[f]['prefix_entropy'] for f in folios])
    hd = np.array([merged[f]['hazard_density'] for f in folios])
    bpc1 = np.array([merged[f]['bridge_pc1'] for f in folios])
    bd = np.array([merged[f]['bridge_density'] for f in folios])

    # Section dummies (B=ref)
    sec_h = np.array([1.0 if merged[f]['section'] == 'H' else 0.0 for f in folios])
    sec_s = np.array([1.0 if merged[f]['section'] == 'S' else 0.0 for f in folios])

    # Regime dummies (REGIME_1=ref)
    reg2 = np.array([1.0 if merged[f]['regime'] == 'REGIME_2' else 0.0 for f in folios])
    reg3 = np.array([1.0 if merged[f]['regime'] == 'REGIME_3' else 0.0 for f in folios])
    reg4 = np.array([1.0 if merged[f]['regime'] == 'REGIME_4' else 0.0 for f in folios])

    # Baseline model
    X_base = np.column_stack([np.ones(n), pe, hd, bpc1, sec_h, sec_s, reg2, reg3, reg4])
    beta_base = np.linalg.lstsq(X_base, y, rcond=None)[0]
    y_pred_base = X_base @ beta_base
    ss_res_base = np.sum((y - y_pred_base) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2_base = 1 - ss_res_base / ss_tot

    # Extended model (+ bridge_density)
    X_ext = np.column_stack([X_base, bd])
    beta_ext = np.linalg.lstsq(X_ext, y, rcond=None)[0]
    y_pred_ext = X_ext @ beta_ext
    ss_res_ext = np.sum((y - y_pred_ext) ** 2)
    r2_ext = 1 - ss_res_ext / ss_tot

    delta_r2 = r2_ext - r2_base

    # F-test for added predictor
    df1 = 1
    df2 = n - X_ext.shape[1]
    if df2 > 0 and ss_res_ext > 0:
        f_stat = ((ss_res_base - ss_res_ext) / df1) / (ss_res_ext / df2)
        f_p = 1 - sp_stats.f.cdf(f_stat, df1, df2)
    else:
        f_stat, f_p = 0.0, 1.0

    # Bridge density coefficient in extended model
    bd_coeff = beta_ext[-1]

    # Collinearity diagnostic: bridge_density vs bridge_pc1
    bd_pc1_r, bd_pc1_p = sp_stats.pearsonr(bd, bpc1)

    print(f"  C1017 baseline R²: {r2_base:.4f}")
    print(f"  Extended R² (+bridge_density): {r2_ext:.4f}")
    print(f"  Delta R²: {delta_r2:.4f}")
    print(f"  F-test: F={f_stat:.4f}, p={f_p:.4f}")
    print(f"  Bridge density coeff: {bd_coeff:.4f}")
    print(f"  Collinearity: r(bridge_density, bridge_pc1) = {bd_pc1_r:.4f}")

    # Verdict
    if delta_r2 > 0.03:
        verdict = "PASS"
    elif delta_r2 < 0.01:
        verdict = "FAIL"
    else:
        verdict = "MARGINAL"

    print(f"  Verdict: {verdict}")

    return {
        'r2_baseline': r2_base,
        'r2_extended': r2_ext,
        'delta_r2': delta_r2,
        'f_stat': f_stat,
        'f_p': f_p,
        'bridge_density_coefficient': bd_coeff,
        'n_predictors_base': X_base.shape[1],
        'n_predictors_ext': X_ext.shape[1],
        'collinearity_bd_pc1_r': bd_pc1_r,
        'collinearity_bd_pc1_p': bd_pc1_p,
        'n': n,
        'verdict': verdict
    }


def run_p5(merged, folios):
    """P5: Bridge density improves BIO LOO R²."""
    print("\n=== P5: BIO LOO Cross-Validation ===")

    bio_folios = [f for f in folios if merged[f]['section'] == 'B']
    n = len(bio_folios)
    print(f"  BIO folios: {n}")

    y = np.array([merged[f]['axm_self'] for f in bio_folios])
    pe = np.array([merged[f]['prefix_entropy'] for f in bio_folios])
    hd = np.array([merged[f]['hazard_density'] for f in bio_folios])
    bpc1 = np.array([merged[f]['bridge_pc1'] for f in bio_folios])
    bd = np.array([merged[f]['bridge_density'] for f in bio_folios])

    # Check regime distribution within BIO
    regime_counts = defaultdict(int)
    for f in bio_folios:
        regime_counts[merged[f]['regime']] += 1
    print(f"  BIO regime distribution: {dict(regime_counts)}")

    # Build design matrices — no section dummies (within-section), include regime if varied
    regimes_present = [r for r, c in regime_counts.items() if c >= 2]

    # Baseline: continuous predictors only (within-section, regime may have too few per cell)
    X_base = np.column_stack([np.ones(n), pe, hd, bpc1])
    X_ext = np.column_stack([X_base, bd])

    def loo_r2(X, y):
        n = len(y)
        preds = np.zeros(n)
        for i in range(n):
            mask = np.arange(n) != i
            X_train, y_train = X[mask], y[mask]
            try:
                beta = np.linalg.lstsq(X_train, y_train, rcond=None)[0]
                preds[i] = X[i] @ beta
            except Exception:
                preds[i] = np.mean(y_train)
        ss_res = np.sum((y - preds) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    loo_base = loo_r2(X_base, y)
    loo_ext = loo_r2(X_ext, y)
    improvement = loo_ext - loo_base

    print(f"  LOO R² baseline: {loo_base:.4f}")
    print(f"  LOO R² extended: {loo_ext:.4f}")
    print(f"  Improvement: {improvement:.4f}")

    # Verdict
    if improvement > 0.05:
        verdict = "PASS"
    elif improvement <= 0:
        verdict = "FAIL"
    else:
        verdict = "MARGINAL"

    print(f"  Verdict: {verdict}")

    return {
        'n_bio_folios': n,
        'bio_regime_distribution': dict(regime_counts),
        'loo_r2_baseline': loo_base,
        'loo_r2_extended': loo_ext,
        'improvement': improvement,
        'n_predictors_base': X_base.shape[1],
        'n_predictors_ext': X_ext.shape[1],
        'verdict': verdict
    }


def run_p6(merged, folios):
    """P6: Bridge-freedom relationship is monotonic."""
    print("\n=== P6: Monotonicity Test ===")

    bd = np.array([merged[f]['bridge_density'] for f in folios])
    abs_resid = np.array([abs(merged[f]['c1017_residual']) for f in folios])
    n = len(folios)

    # Spearman and Pearson
    rho_spearman, p_spearman = sp_stats.spearmanr(bd, abs_resid)
    r_pearson, p_pearson = sp_stats.pearsonr(bd, abs_resid)

    print(f"  Spearman rho: {rho_spearman:.4f}, p={p_spearman:.4f}")
    print(f"  Pearson r: {r_pearson:.4f}, p={p_pearson:.4f}")

    # Same sign check
    same_sign = (rho_spearman * r_pearson) > 0 if (rho_spearman != 0 and r_pearson != 0) else True

    # Within 20% magnitude check
    max_mag = max(abs(rho_spearman), abs(r_pearson))
    if max_mag > 0:
        ratio = min(abs(rho_spearman), abs(r_pearson)) / max_mag
        within_20 = ratio >= 0.80
    else:
        ratio = 1.0
        within_20 = True

    print(f"  Same sign: {same_sign}, magnitude ratio: {ratio:.4f}, within 20%: {within_20}")

    # Quadratic test
    X_lin = np.column_stack([np.ones(n), bd])
    X_quad = np.column_stack([np.ones(n), bd, bd ** 2])

    beta_lin = np.linalg.lstsq(X_lin, abs_resid, rcond=None)[0]
    beta_quad = np.linalg.lstsq(X_quad, abs_resid, rcond=None)[0]

    ss_res_lin = np.sum((abs_resid - X_lin @ beta_lin) ** 2)
    ss_res_quad = np.sum((abs_resid - X_quad @ beta_quad) ** 2)

    df_num = 1
    df_den = n - 3
    if df_den > 0 and ss_res_quad > 0:
        f_quad = ((ss_res_lin - ss_res_quad) / df_num) / (ss_res_quad / df_den)
        p_quad = 1 - sp_stats.f.cdf(f_quad, df_num, df_den)
    else:
        f_quad, p_quad = 0.0, 1.0

    print(f"  Quadratic term: F={f_quad:.4f}, p={p_quad:.4f}")

    # Also test with axm_self directly (secondary)
    rho_axm, p_axm = sp_stats.spearmanr(bd, np.array([merged[f]['axm_self'] for f in folios]))
    print(f"  Secondary (bridge_density vs axm_self): rho={rho_axm:.4f}, p={p_axm:.4f}")

    # Verdict
    if p_quad < 0.05:
        verdict = "FAIL"
    elif same_sign and within_20:
        verdict = "PASS"
    else:
        verdict = "MARGINAL"

    print(f"  Verdict: {verdict}")

    return {
        'spearman_rho': rho_spearman,
        'spearman_p': p_spearman,
        'pearson_r': r_pearson,
        'pearson_p': p_pearson,
        'same_sign': same_sign,
        'magnitude_ratio': ratio,
        'within_20_pct': within_20,
        'quadratic_f_stat': f_quad,
        'quadratic_p': p_quad,
        'quadratic_coefficient': float(beta_quad[2]),
        'secondary_axm_rho': rho_axm,
        'secondary_axm_p': p_axm,
        'n': n,
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("Phase 391: SECTION_BRIDGE_DYNAMICS")
    print("=" * 70)

    # Step 1: Compute bridge density per folio
    print("\n--- Computing bridge density ---")
    bridge_density, folio_middles, bridge_set = compute_bridge_density()

    # Step 2: Load AXM data
    print("\n--- Loading AXM data ---")
    axm_data = load_axm_data()

    # Step 3: Merge
    print("\n--- Merging ---")
    merged = merge_data(bridge_density, axm_data)

    # Step 4: Filter to B/H/S
    folios_bhs = get_bhs_folios(merged)
    print(f"B/H/S folios: {len(folios_bhs)}")

    # Descriptive stats
    print("\n--- Bridge Density Stats (Currier B only) ---")
    section_bd = defaultdict(list)
    for f in folios_bhs:
        section_bd[merged[f]['section']].append(merged[f]['bridge_density'])

    bd_stats = {}
    for sec in sorted(section_bd.keys()):
        vals = section_bd[sec]
        stats = {
            'n': len(vals),
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals, ddof=1)),
            'min': float(min(vals)),
            'max': float(max(vals))
        }
        bd_stats[sec] = stats
        print(f"  {sec}: n={stats['n']}, mean={stats['mean']:.4f}, std={stats['std']:.4f}")

    all_bd = [merged[f]['bridge_density'] for f in folios_bhs]
    overall_stats = {
        'mean': float(np.mean(all_bd)),
        'std': float(np.std(all_bd, ddof=1)),
        'min': float(min(all_bd)),
        'max': float(max(all_bd))
    }

    # Regime x section contingency
    print("\n--- REGIME x Section Contingency ---")
    contingency = defaultdict(lambda: defaultdict(int))
    for f in folios_bhs:
        contingency[merged[f]['regime']][merged[f]['section']] += 1
    for regime in sorted(contingency.keys()):
        row = {s: contingency[regime][s] for s in ['B', 'H', 'S']}
        print(f"  {regime}: {dict(row)}")

    # Collinearity check
    bd_arr = np.array([merged[f]['bridge_density'] for f in folios_bhs])
    pc1_arr = np.array([merged[f]['bridge_pc1'] for f in folios_bhs])
    col_r, col_p = sp_stats.pearsonr(bd_arr, pc1_arr)
    print(f"\n--- Collinearity: r(bridge_density, bridge_pc1) = {col_r:.4f}, p={col_p:.4f} ---")

    # Run all 6 tests
    p1 = run_p1(merged, folios_bhs)
    p2 = run_p2(merged, folios_bhs)
    p3 = run_p3(merged, folios_bhs)
    p4 = run_p4(merged, folios_bhs)
    p5 = run_p5(merged, folios_bhs)
    p6 = run_p6(merged, folios_bhs)

    # Synthesis
    verdicts = {
        'P1_regime_section_control': p1['verdict'],
        'P2_bridge_residual_anticorrelation': p2['verdict'],
        'P3_herbal_highest_variance': p3['verdict'],
        'P4_incremental_r2': p4['verdict'],
        'P5_bio_loo_improvement': p5['verdict'],
        'P6_monotonic_relationship': p6['verdict']
    }

    all_verdicts = list(verdicts.values())
    n_pass = sum(1 for v in all_verdicts if v == 'PASS')
    n_fail = sum(1 for v in all_verdicts if v == 'FAIL')
    n_marginal = sum(1 for v in all_verdicts if v == 'MARGINAL')

    if n_pass >= 4:
        overall = "SECTION_MEDIATES"
        summary = ("Bridge density mediates the section-to-dynamics relationship. "
                    "Design freedom is vocabulary-compositional: sections with more "
                    "bridge vocabulary have more behavioral choices.")
    elif n_fail >= 4:
        overall = "SECTION_INDEPENDENT"
        summary = ("Section identity and bridge density act independently on AXM dynamics. "
                    "Design freedom has no vocabulary-compositional mechanism.")
    else:
        overall = "INCONCLUSIVE"
        summary = (f"Mixed results ({n_pass} PASS, {n_fail} FAIL, {n_marginal} MARGINAL). "
                    "No clear mediation or independence pattern.")

    print(f"\n{'=' * 70}")
    print(f"SYNTHESIS: {overall}")
    print(f"  {n_pass} PASS, {n_fail} FAIL, {n_marginal} MARGINAL")
    print(f"  {summary}")
    print(f"{'=' * 70}")

    # Build folio_data output (all merged folios, not just B/H/S)
    folio_output = {}
    for f in merged:
        folio_output[f] = {
            'bridge_density': merged[f]['bridge_density'],
            'axm_self': merged[f]['axm_self'],
            'section': merged[f]['section'],
            'regime': merged[f]['regime'],
            'c1017_residual': merged[f]['c1017_residual'],
            'n_unique_middles': len(folio_middles.get(f, set())),
            'n_bridge_middles': len(folio_middles.get(f, set()) & bridge_set)
        }

    results = round_floats({
        'phase': 391,
        'name': 'SECTION_BRIDGE_DYNAMICS',
        'test_count': 6,
        'n_folios_total': len(merged),
        'n_folios_bhs': len(folios_bhs),
        'sections_used': sorted(list(MAIN_SECTIONS)),
        'bridge_middles_count': len(bridge_set),
        'bridge_density_stats': {
            'per_section': bd_stats,
            'overall': overall_stats
        },
        'regime_section_contingency': {r: dict(s) for r, s in contingency.items()},
        'collinearity_bd_pc1': {'r': col_r, 'p': col_p},
        'verdicts': verdicts,
        'P1_data': p1,
        'P2_data': p2,
        'P3_data': p3,
        'P4_data': p4,
        'P5_data': p5,
        'P6_data': p6,
        'folio_data': folio_output,
        'synthesis': {
            'n_pass': n_pass,
            'n_fail': n_fail,
            'n_marginal': n_marginal,
            'overall': overall,
            'summary': summary
        }
    })

    out_path = RESULTS / "section_bridge_dynamics.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
