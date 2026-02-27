#!/usr/bin/env python3
"""
Phase 480: FOLIO ACCENT VECTOR ANALYSIS
========================================
Extracts per-folio accent vectors from Phase 479 z-scores, runs PCA,
and tests whether the accent structure is archetype-dominated or captures
genuinely new folio-level structure.

Gating test: accent PC1 vs archetype correlation.
  r > 0.7 → accent IS archetype structure (minimal further testing)
  r < 0.5 → accent captures new structure (full test battery)

Tests:
  T1: PCA extraction (variance explained, loadings)
  T2: Gating test (accent PC1 vs archetype Spearman)
  T3: Category composition correlation (controlling for kernel)
  T4: Within-quire accent ordering
  T5: Archetype 1 individual profiling
  T6: BIO accent after REGIME control

Depends on: C1366, C1016, C1048, C1294, C638
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, mannwhitneyu, f_oneway, pearsonr
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Constants ────────────────────────────────────────────────────────

# The 11 systematic gap features from C1366 (mean|z| > 1.5)
GAP_FEATURES = [
    'class_entropy', 'class_concentration', 'axm_fraction', 'fq_fraction',
    'axm_self_transition', 'mean_run_length', 'bigram_entropy',
    'suffix_rate', 'mean_word_length', 'e_fraction', 'category_entropy',
]

CATEGORIES = ('THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING')


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def folio_sort_key(folio_id):
    """Sort key for physical folio ordering."""
    import re
    m = re.match(r'f(\d+)([rv]?)(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0 if m.group(2) == 'r' else 1
        sub = int(m.group(3)) if m.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load Phase 479 results and external metadata."""
    print("Loading data...")

    # Phase 479 results
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        gap_data = json.load(f)

    per_folio = gap_data['per_folio']
    folios = sorted(per_folio.keys())
    print(f"  {len(folios)} folios from Phase 479")

    # Quire assignments
    with open(PROJECT / 'results' / 'unified_folio_profiles.json', encoding='utf-8') as f:
        profiles = json.load(f)
    folio_quire = {}
    for folio_id, profile in profiles.items():
        if isinstance(profile, dict) and 'quire' in profile:
            folio_quire[folio_id] = profile['quire']

    # AXM folio data (for paragraph count, etc.)
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    axm_folio_data = axm_data['folio_data']

    return {
        'per_folio': per_folio,
        'folios': folios,
        'folio_quire': folio_quire,
        'axm_folio_data': axm_folio_data,
    }


def compute_category_fractions(folios_set):
    """Compute per-folio 8-category fractions from transcript."""
    print("  Computing category fractions...")
    morph = Morphology()
    cc = CategoryClassifier()

    # Single-pass token loading
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    folio_cat_counts = defaultdict(lambda: Counter())
    folio_token_counts = Counter()

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        if token_to_class.get(token.word) is None:
            continue
        if token.folio not in folios_set:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        folio_token_counts[token.folio] += 1
        if cat:
            folio_cat_counts[token.folio][cat] += 1

    # Convert to fractions
    folio_cat_fractions = {}
    for folio in folios_set:
        total = sum(folio_cat_counts[folio].values())
        if total > 0:
            folio_cat_fractions[folio] = {
                cat: folio_cat_counts[folio].get(cat, 0) / total
                for cat in CATEGORIES
            }
        else:
            folio_cat_fractions[folio] = {cat: 0.0 for cat in CATEGORIES}

    return folio_cat_fractions


# ── Test Functions ───────────────────────────────────────────────────

def test1_pca(folios, per_folio):
    """T1: PCA extraction on 11 gap features."""
    print("\n=== T1: PCA Extraction ===")

    # Build 72 x 11 z-score matrix
    z_matrix = np.zeros((len(folios), len(GAP_FEATURES)))
    for i, folio in enumerate(folios):
        z_scores = per_folio[folio]['z_scores']
        for j, feat in enumerate(GAP_FEATURES):
            z_matrix[i, j] = z_scores[feat]

    # Standardize
    scaler = StandardScaler()
    z_std = scaler.fit_transform(z_matrix)

    # PCA
    pca = PCA(n_components=min(5, len(GAP_FEATURES)))
    pcs = pca.fit_transform(z_std)

    # Results
    var_explained = pca.explained_variance_ratio_
    cum_var = np.cumsum(var_explained)
    loadings = pca.components_  # n_components x n_features

    print(f"  Variance explained: PC1={var_explained[0]:.3f}, PC2={var_explained[1]:.3f}, "
          f"PC3={var_explained[2]:.3f}")
    print(f"  Cumulative: PC1={cum_var[0]:.3f}, PC1-2={cum_var[1]:.3f}, PC1-3={cum_var[2]:.3f}")

    # Top loadings per PC
    for pc_idx in range(3):
        sorted_loadings = sorted(enumerate(loadings[pc_idx]),
                                 key=lambda x: abs(x[1]), reverse=True)
        top3 = [(GAP_FEATURES[idx], val) for idx, val in sorted_loadings[:3]]
        print(f"  PC{pc_idx+1} top loadings: {', '.join(f'{f}={v:.3f}' for f, v in top3)}")

    # Per-folio PC scores
    folio_pcs = {folio: {f'PC{k+1}': float(pcs[i, k]) for k in range(3)}
                 for i, folio in enumerate(folios)}

    result = {
        'variance_explained': [float(v) for v in var_explained[:5]],
        'cumulative_variance': [float(v) for v in cum_var[:5]],
        'loadings': {
            f'PC{k+1}': {GAP_FEATURES[j]: float(loadings[k, j])
                         for j in range(len(GAP_FEATURES))}
            for k in range(3)
        },
        'folio_scores': folio_pcs,
    }

    return result, pcs


def test2_gating(folios, per_folio, pcs):
    """T2: Gating test — accent PC1 vs archetype."""
    print("\n=== T2: GATING TEST — Accent PC1 vs Archetype ===")

    pc1 = pcs[:, 0]
    archetypes = []
    valid_idx = []
    for i, folio in enumerate(folios):
        arch = per_folio[folio].get('archetype')
        if arch is not None:
            archetypes.append(arch)
            valid_idx.append(i)

    pc1_valid = pc1[valid_idx]
    arch_arr = np.array(archetypes)

    # Spearman correlation
    rho, p = spearmanr(pc1_valid, arch_arr)
    print(f"  PC1 vs archetype: rho={rho:.3f}, p={p:.4f}")

    # Also test PC2
    pc2_valid = pcs[valid_idx, 1]
    rho2, p2 = spearmanr(pc2_valid, arch_arr)
    print(f"  PC2 vs archetype: rho={rho2:.3f}, p={p2:.4f}")

    # Composite anomaly vs archetype
    composites = [per_folio[folios[i]]['composite_anomaly'] for i in valid_idx]
    rho_comp, p_comp = spearmanr(composites, arch_arr)
    print(f"  Composite anomaly vs archetype: rho={rho_comp:.3f}, p={p_comp:.4f}")

    # ANOVA: composite anomaly by archetype
    arch_groups = defaultdict(list)
    for i, arch in zip(valid_idx, archetypes):
        arch_groups[arch].append(per_folio[folios[i]]['composite_anomaly'])

    groups = [arch_groups[k] for k in sorted(arch_groups.keys())]
    if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
        f_stat, anova_p = f_oneway(*groups)
        # Eta-squared
        grand_mean = np.mean([c for g in groups for c in g])
        ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
        ss_total = sum((c - grand_mean) ** 2 for g in groups for c in g)
        eta_sq = ss_between / max(ss_total, 1e-10)
        print(f"  ANOVA: F={f_stat:.2f}, p={anova_p:.4f}, eta-sq={eta_sq:.3f}")
    else:
        f_stat, anova_p, eta_sq = None, None, None

    # Gating decision
    abs_rho = abs(rho)
    if abs_rho > 0.7:
        gate = 'ARCHETYPE_DOMINATED'
        print(f"  GATE: {gate} (|rho|={abs_rho:.3f} > 0.7)")
    elif abs_rho < 0.5:
        gate = 'NEW_STRUCTURE'
        print(f"  GATE: {gate} (|rho|={abs_rho:.3f} < 0.5)")
    else:
        gate = 'MIXED'
        print(f"  GATE: {gate} (0.5 <= |rho|={abs_rho:.3f} <= 0.7)")

    return {
        'pc1_vs_archetype_rho': float(rho),
        'pc1_vs_archetype_p': float(p),
        'pc2_vs_archetype_rho': float(rho2),
        'pc2_vs_archetype_p': float(p2),
        'composite_vs_archetype_rho': float(rho_comp),
        'composite_vs_archetype_p': float(p_comp),
        'anova_F': float(f_stat) if f_stat is not None else None,
        'anova_p': float(anova_p) if anova_p is not None else None,
        'anova_eta_sq': float(eta_sq) if eta_sq is not None else None,
        'gate_decision': gate,
    }


def test3_category(folios, per_folio, pcs, folio_cat_fractions):
    """T3: Category composition vs accent (controlling for kernel)."""
    print("\n=== T3: Category Composition vs Accent ===")

    pc1 = pcs[:, 0]
    composites = np.array([per_folio[f]['composite_anomaly'] for f in folios])

    # Per-folio kernel fractions from Phase 479 real_features
    k_fracs = np.array([per_folio[f]['real_features']['k_fraction'] for f in folios])
    h_fracs = np.array([per_folio[f]['real_features']['h_fraction'] for f in folios])
    e_fracs = np.array([per_folio[f]['real_features']['e_fraction'] for f in folios])

    results = {}
    print(f"  {'Category':15s} {'rho_PC1':>8s} {'p_PC1':>8s} {'rho_comp':>8s} {'p_comp':>8s}")

    for cat in CATEGORIES:
        cat_vals = np.array([folio_cat_fractions[f].get(cat, 0) for f in folios])

        # Raw correlation with PC1
        rho_pc1, p_pc1 = spearmanr(cat_vals, pc1)

        # Raw correlation with composite anomaly
        rho_comp, p_comp = spearmanr(cat_vals, composites)

        # Partial correlation controlling for kernel (k + e fractions)
        # Use residuals from OLS regression on kernel
        from numpy.linalg import lstsq
        X_kernel = np.column_stack([k_fracs, e_fracs, np.ones(len(folios))])
        # Residualize cat_vals
        beta_cat, _, _, _ = lstsq(X_kernel, cat_vals, rcond=None)
        cat_resid = cat_vals - X_kernel @ beta_cat
        # Residualize PC1
        beta_pc1, _, _, _ = lstsq(X_kernel, pc1, rcond=None)
        pc1_resid = pc1 - X_kernel @ beta_pc1

        if np.std(cat_resid) > 1e-10 and np.std(pc1_resid) > 1e-10:
            rho_partial, p_partial = spearmanr(cat_resid, pc1_resid)
        else:
            rho_partial, p_partial = 0.0, 1.0

        print(f"  {cat:15s} {rho_pc1:8.3f} {p_pc1:8.4f} {rho_comp:8.3f} {p_comp:8.4f}  "
              f"(partial: rho={rho_partial:.3f}, p={p_partial:.4f})")

        results[cat] = {
            'rho_pc1': float(rho_pc1),
            'p_pc1': float(p_pc1),
            'rho_composite': float(rho_comp),
            'p_composite': float(p_comp),
            'rho_partial_kernel': float(rho_partial),
            'p_partial_kernel': float(p_partial),
        }

    # Any category significant after kernel control?
    sig_after_kernel = [cat for cat, r in results.items()
                        if abs(r['rho_partial_kernel']) > 0.3 and r['p_partial_kernel'] < 0.05]
    print(f"\n  Categories significant after kernel control: {sig_after_kernel if sig_after_kernel else 'NONE'}")

    return {
        'category_correlations': results,
        'significant_after_kernel': sig_after_kernel,
    }


def test4_quire_ordering(folios, per_folio, folio_quire):
    """T4: Within-quire accent ordering."""
    print("\n=== T4: Within-Quire Accent Ordering ===")

    # Group folios by quire
    quire_folios = defaultdict(list)
    for folio in folios:
        quire = folio_quire.get(folio)
        if quire:
            quire_folios[quire].append(folio)

    # Sort within quire by physical position
    for quire in quire_folios:
        quire_folios[quire].sort(key=folio_sort_key)

    # For quires with 3+ folios, compute within-quire correlation
    quire_results = {}
    rhos = []
    for quire, qfolios in sorted(quire_folios.items()):
        if len(qfolios) < 3:
            continue
        positions = list(range(len(qfolios)))
        composites = [per_folio[f]['composite_anomaly'] for f in qfolios]
        rho, p = spearmanr(positions, composites)
        quire_results[quire] = {
            'n_folios': len(qfolios),
            'rho': float(rho),
            'p': float(p),
            'folios': qfolios,
        }
        rhos.append(rho)
        print(f"  Quire {quire}: n={len(qfolios)}, rho={rho:.3f}, p={p:.3f}")

    if rhos:
        mean_rho = float(np.mean(rhos))
        mean_abs_rho = float(np.mean([abs(r) for r in rhos]))
        print(f"  Mean within-quire rho: {mean_rho:.3f} (mean|rho|={mean_abs_rho:.3f})")
    else:
        mean_rho = None
        mean_abs_rho = None

    return {
        'quire_results': quire_results,
        'mean_rho': mean_rho,
        'mean_abs_rho': mean_abs_rho,
        'n_quires_tested': len(quire_results),
    }


def test5_archetype1(folios, per_folio):
    """T5: Archetype 1 individual profiling."""
    print("\n=== T5: Archetype 1 Individual Profiling ===")

    arch1_folios = [f for f in folios if per_folio[f].get('archetype') == 1]
    print(f"  {len(arch1_folios)} archetype 1 folios")

    if not arch1_folios:
        return {'n_folios': 0}

    # Per-folio z-score profiles on gap features
    profiles = {}
    feature_z_matrix = []
    for folio in arch1_folios:
        z = per_folio[folio]['z_scores']
        profile = {feat: z[feat] for feat in GAP_FEATURES}
        profiles[folio] = {
            'z_scores': profile,
            'composite': per_folio[folio]['composite_anomaly'],
            'section': per_folio[folio].get('section', 'UNK'),
            'regime': per_folio[folio].get('regime', 'UNK'),
            'top_feature': max(GAP_FEATURES, key=lambda f: abs(z[f])),
        }
        feature_z_matrix.append([z[f] for f in GAP_FEATURES])

    feature_z_matrix = np.array(feature_z_matrix)

    # Which features drive the anomaly?
    feature_mean_abs_z = {GAP_FEATURES[j]: float(np.mean(np.abs(feature_z_matrix[:, j])))
                          for j in range(len(GAP_FEATURES))}
    sorted_features = sorted(feature_mean_abs_z.items(), key=lambda x: x[1], reverse=True)

    print(f"  Top driving features:")
    for feat, maz in sorted_features[:5]:
        print(f"    {feat:25s}  mean|z|={maz:.3f}")

    # Homogeneity: do all folios agree on direction?
    feature_sign_agreement = {}
    for j, feat in enumerate(GAP_FEATURES):
        vals = feature_z_matrix[:, j]
        n_pos = np.sum(vals > 0)
        n_neg = np.sum(vals < 0)
        agreement = max(n_pos, n_neg) / len(vals)
        feature_sign_agreement[feat] = float(agreement)

    mean_agreement = float(np.mean(list(feature_sign_agreement.values())))
    print(f"  Mean sign agreement: {mean_agreement:.2f} (1.0 = all same direction)")

    # Section/REGIME composition
    sections = Counter(per_folio[f].get('section', 'UNK') for f in arch1_folios)
    regimes = Counter(per_folio[f].get('regime', 'UNK') for f in arch1_folios)
    print(f"  Sections: {dict(sections)}")
    print(f"  REGIMEs: {dict(regimes)}")

    return {
        'n_folios': len(arch1_folios),
        'profiles': profiles,
        'feature_mean_abs_z': dict(sorted_features),
        'feature_sign_agreement': feature_sign_agreement,
        'mean_sign_agreement': mean_agreement,
        'section_composition': dict(sections),
        'regime_composition': dict(regimes),
    }


def test6_bio_regime_control(folios, per_folio):
    """T6: BIO accent after REGIME control."""
    print("\n=== T6: BIO Accent After REGIME Control ===")

    # Filter to REGIME_1 only
    r1_folios = [f for f in folios
                 if per_folio[f].get('regime') in ('REGIME_1', '1', 1)]
    print(f"  REGIME_1 folios: {len(r1_folios)}")

    bio_r1 = [f for f in r1_folios if per_folio[f].get('section') == 'B']
    non_bio_r1 = [f for f in r1_folios if per_folio[f].get('section') != 'B']
    print(f"  BIO in R1: {len(bio_r1)}, non-BIO in R1: {len(non_bio_r1)}")

    if not bio_r1 or not non_bio_r1:
        print("  Insufficient data for comparison")
        return {'bio_n': len(bio_r1), 'non_bio_n': len(non_bio_r1),
                'test_possible': False}

    bio_composites = [per_folio[f]['composite_anomaly'] for f in bio_r1]
    non_bio_composites = [per_folio[f]['composite_anomaly'] for f in non_bio_r1]

    bio_mean = float(np.mean(bio_composites))
    non_bio_mean = float(np.mean(non_bio_composites))

    # Mann-Whitney
    u_stat, mw_p = mannwhitneyu(bio_composites, non_bio_composites, alternative='greater')

    bio_still_higher = bio_mean > non_bio_mean
    print(f"  BIO mean anomaly: {bio_mean:.3f}")
    print(f"  Non-BIO mean anomaly: {non_bio_mean:.3f}")
    print(f"  MW U={u_stat:.1f}, p={mw_p:.4f}")
    print(f"  BIO still higher within R1: {bio_still_higher}")

    interpretation = ("BIO accent is section-intrinsic (persists after REGIME control)"
                      if bio_still_higher and mw_p < 0.05
                      else "BIO accent is REGIME-mediated or non-significant within R1")
    print(f"  Interpretation: {interpretation}")

    return {
        'bio_n': len(bio_r1),
        'non_bio_n': len(non_bio_r1),
        'bio_mean_anomaly': bio_mean,
        'non_bio_mean_anomaly': non_bio_mean,
        'mw_U': float(u_stat),
        'mw_p': float(mw_p),
        'bio_still_higher': bio_still_higher,
        'significant': mw_p < 0.05,
        'interpretation': interpretation,
        'test_possible': True,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()
    folios = data['folios']
    per_folio = data['per_folio']

    # T1: PCA
    t1_result, pcs = test1_pca(folios, per_folio)

    # T2: Gating test
    t2_result = test2_gating(folios, per_folio, pcs)
    gate = t2_result['gate_decision']

    # Compute category fractions for T3
    folio_cat_fractions = compute_category_fractions(set(folios))

    # T3: Category composition
    t3_result = test3_category(folios, per_folio, pcs, folio_cat_fractions)

    # T4: Within-quire ordering
    t4_result = test4_quire_ordering(folios, per_folio, data['folio_quire'])

    # T5: Archetype 1 profiling
    t5_result = test5_archetype1(folios, per_folio)

    # T6: BIO REGIME control
    t6_result = test6_bio_regime_control(folios, per_folio)

    # ── Verdict ──────────────────────────────────────────────────
    print(f"\n{'='*60}")

    verdict_parts = []

    # PCA structure
    verdict_parts.append(f"PC1 explains {t1_result['variance_explained'][0]*100:.1f}% of accent variance")

    # Gating
    rho = abs(t2_result['pc1_vs_archetype_rho'])
    verdict_parts.append(f"Accent-archetype |rho|={rho:.3f} → {gate}")

    # Category
    sig_cats = t3_result['significant_after_kernel']
    if sig_cats:
        verdict_parts.append(f"Categories beyond kernel: {', '.join(sig_cats)}")
    else:
        verdict_parts.append("No category signal beyond kernel")

    # Quire
    if t4_result['mean_abs_rho'] is not None:
        verdict_parts.append(f"Within-quire ordering: mean|rho|={t4_result['mean_abs_rho']:.3f}")
    else:
        verdict_parts.append("No quires with 3+ folios")

    # BIO
    if t6_result.get('test_possible'):
        if t6_result['significant']:
            verdict_parts.append("BIO accent is section-intrinsic")
        else:
            verdict_parts.append("BIO accent is REGIME-mediated")

    verdict = "; ".join(verdict_parts)
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save results
    results = {
        'metadata': {
            'phase': 480,
            'name': 'FOLIO_ACCENT_VECTOR',
            'n_folios': len(folios),
            'n_gap_features': len(GAP_FEATURES),
            'gap_features': GAP_FEATURES,
            'elapsed_seconds': elapsed,
        },
        'T1_pca': t1_result,
        'T2_gating': t2_result,
        'T3_category': t3_result,
        'T4_quire': t4_result,
        'T5_archetype1': t5_result,
        'T6_bio_regime': t6_result,
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'folio_accent_vector.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
