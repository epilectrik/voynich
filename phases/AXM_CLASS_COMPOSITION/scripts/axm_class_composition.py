#!/usr/bin/env python3
"""
AXM_CLASS_COMPOSITION -- Phase 359
====================================
AXM contains 32 of 49 instruction classes. Two folios with the same AXM
self-transition rate could have completely different internal class profiles.
C1006 proved AXM runs are diverse class sequences (mean class run = 1.054).

This phase profiles per-folio AXM class composition, testing whether within-AXM
class structure explains the 57% irreducible AXM residual (C1035) and whether
C458's design asymmetry manifests at the class level.

Pre-registered hypotheses:
  P1: Between-folio AXM class profiles exceed multinomial sampling noise
  P2: Class profile PCs predict C1035 residual (LOO R2 > 0.10)
  P3: Hazard-adjacent class fractions have lower CV than non-hazard (C458)
  P4: PREFIX profile within AXM co-varies with class profile (mediation)
  P5: Class diversity correlates with AXM self-transition (|rho| > 0.25)
  P6: REGIME does not explain class profiles (eta2 < 0.30 on PC1-PC3)

Pipeline: S1-S9
  S1: Build per-folio AXM class composition vectors (72 x 32) + PREFIX dists
  S2: CLR transform + PCA via SVD
  S3: T1: Multinomial overdispersion test
  S4: T2: Predict C1035 residual from class PCs (OLS + LOO CV)
  S5: T3: C458 localization (hazard-adjacent vs non-hazard class CV)
  S6: T4: PREFIX mediation (PREFIX PCA vs class PCA correlation)
  S7: T5: Class diversity metrics vs AXM self-transition
  S8: T6: Variance decomposition (eta2 by REGIME, section, archetype)
  S9: Evaluate P1-P6

Depends on: C1035, C1036, C1010, C458, C1006, C1007, C1023
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# -- Constants --

# Canonical 6-state partition (C1010, Phase 358 canonical: class 45 in AXm)
AXM_CLASSES_SET = {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,
                   31,32,33,34,35,36,37,39,41,43,44,46,47,48,49}
AXM_CLASS_ORDER = sorted(AXM_CLASSES_SET)  # 32 classes
N_AXM = len(AXM_CLASS_ORDER)
AXM_IDX = {c: i for i, c in enumerate(AXM_CLASS_ORDER)}

GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}

HAZARD_SOURCE_MIDDLES = {'ar', 'dy', 'ey', 'l', 'ol', 'or'}
HAZARD_TARGET_MIDDLES = {'aiin', 'al', 'ee', 'o', 'r', 't'}
SAFETY_BUFFER_MIDDLES = {'eol', 'k', 'od'}
ALL_HAZARD_MIDDLES = HAZARD_SOURCE_MIDDLES | HAZARD_TARGET_MIDDLES

MIN_AXM_TOKENS = 30  # Minimum AXM tokens per folio for stable composition

CLR_PSEUDOCOUNT = 0.5


# -- Data Loading --

def load_token_to_class():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        return json.load(f)['token_to_class']


def load_c1035_data():
    path = PROJECT_ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
    with open(path) as f:
        return json.load(f)['folio_data']


def load_regime_assignments():
    path = PROJECT_ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = PROJECT_ROOT / 'phases' / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    return {k: int(v) for k, v in data['t2_archetype_discovery']['folio_labels'].items()}


# -- S1: Build Per-Folio AXM Class Composition --

def build_class_compositions(token_to_class):
    """Build per-folio AXM class composition vectors and PREFIX distributions.

    Returns:
        class_counts: {folio: np.array(32,)} raw counts per AXM class
        class_props: {folio: np.array(32,)} proportions
        prefix_counts: {folio: Counter} PREFIX distribution within AXM tokens
        folio_sections: {folio: section}
    """
    tx = Transcript()
    morph = Morphology()

    folio_axm_counts = defaultdict(lambda: np.zeros(N_AXM, dtype=int))
    folio_prefix_counts = defaultdict(Counter)
    folio_sections = {}
    n_unmapped = 0
    n_non_axm = 0

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        folio_sections[token.folio] = token.section

        cls = token_to_class.get(w)
        if cls is None:
            n_unmapped += 1
            continue
        cls = int(cls)

        if cls not in AXM_CLASSES_SET:
            n_non_axm += 1
            continue

        folio_axm_counts[token.folio][AXM_IDX[cls]] += 1

        # Extract PREFIX for AXM tokens
        m = morph.extract(w)
        prefix = m.prefix if m.prefix else 'NONE'
        folio_prefix_counts[token.folio][prefix] += 1

    # Filter folios with enough AXM tokens
    valid = {}
    excluded = 0
    for folio, counts in folio_axm_counts.items():
        total = counts.sum()
        if total >= MIN_AXM_TOKENS:
            valid[folio] = counts
        else:
            excluded += 1

    # Compute proportions
    class_props = {f: c / c.sum() for f, c in valid.items()}

    print(f"  {len(valid)} folios with >= {MIN_AXM_TOKENS} AXM tokens")
    print(f"  Excluded: {excluded} folios, {n_unmapped} unmapped tokens, {n_non_axm} non-AXM tokens")

    return valid, class_props, dict(folio_prefix_counts), folio_sections


def identify_hazard_adjacent_classes(token_to_class):
    """Identify AXM classes enriched in hazard MIDDLEs.

    Returns set of hazard-adjacent class IDs (union of gatekeepers + enriched).
    """
    morph = Morphology()

    class_hazard_counts = defaultdict(int)
    class_total_counts = defaultdict(int)

    for word, cls_str in token_to_class.items():
        cls = int(cls_str)
        if cls not in AXM_CLASSES_SET:
            continue

        m = morph.extract(word)
        mid = m.middle if m.middle else ''

        class_total_counts[cls] += 1
        if mid in ALL_HAZARD_MIDDLES:
            class_hazard_counts[cls] += 1

    # Flag classes with > 20% hazard-MIDDLE tokens
    enriched = set()
    class_hazard_fracs = {}
    for cls in AXM_CLASS_ORDER:
        total = class_total_counts.get(cls, 0)
        hazard = class_hazard_counts.get(cls, 0)
        frac = hazard / total if total > 0 else 0
        class_hazard_fracs[cls] = round(frac, 3)
        if frac > 0.20:
            enriched.add(cls)

    hazard_adjacent = GATEKEEPER_CLASSES | enriched
    hazard_adjacent = hazard_adjacent & AXM_CLASSES_SET  # Ensure only AXM classes

    return hazard_adjacent, class_hazard_fracs


# -- S2: CLR Transform + PCA --

def clr_transform(X, pseudocount=CLR_PSEUDOCOUNT):
    """Centered log-ratio transform for compositional data."""
    X_adj = X + pseudocount
    X_prop = X_adj / X_adj.sum(axis=1, keepdims=True)
    log_X = np.log(X_prop)
    geo_mean = log_X.mean(axis=1, keepdims=True)
    return log_X - geo_mean


def pca_numpy(X, n_components=None):
    """PCA via SVD. Returns scores, loadings, explained_variance_ratio."""
    X_centered = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    explained = (S ** 2) / (S ** 2).sum()

    if n_components is None:
        # Retain PCs with > 5% variance, up to cumulative 80%
        cumvar = np.cumsum(explained)
        n_components = max(1, np.searchsorted(cumvar, 0.80) + 1)
        # Also cap at PCs with > 5% individual variance
        sig_pcs = (explained > 0.05).sum()
        n_components = min(n_components, max(sig_pcs, 2))

    scores = U[:, :n_components] * S[:n_components]
    loadings = Vt[:n_components]
    return scores, loadings, explained, n_components


# -- S4: OLS + LOO CV --

def ols_fit(X, y):
    """OLS regression. Returns coefficients, R-squared."""
    # Add intercept
    n = X.shape[0]
    X_aug = np.column_stack([np.ones(n), X])
    beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    y_pred = X_aug @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, r2, y_pred


def loo_cv_r2(X, y):
    """Leave-one-out cross-validated R-squared."""
    n = X.shape[0]
    predictions = np.zeros(n)

    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train = X[mask]
        y_train = y[mask]

        X_aug = np.column_stack([np.ones(X_train.shape[0]), X_train])
        beta = np.linalg.lstsq(X_aug, y_train, rcond=None)[0]

        x_test = np.concatenate([[1], X[i]])
        predictions[i] = x_test @ beta

    ss_res = np.sum((y - predictions) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


# -- S8: Variance Decomposition --

def eta_squared(values, groups):
    """Compute eta-squared for one-way grouping."""
    grand_mean = np.mean(values)
    ss_total = np.sum((values - grand_mean) ** 2)
    if ss_total < 1e-15:
        return 0.0

    ss_between = 0
    for g in set(groups):
        mask = [i for i, gl in enumerate(groups) if gl == g]
        if mask:
            group_mean = np.mean([values[i] for i in mask])
            ss_between += len(mask) * (group_mean - grand_mean) ** 2

    return ss_between / ss_total


# -- Main --

def main():
    start = time.time()

    print("Phase 359: AXM_CLASS_COMPOSITION")
    print("=" * 70)

    # ---- Load data ----
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    c1035_data = load_c1035_data()
    regimes = load_regime_assignments()
    archetypes = load_folio_archetypes()

    # ---- S1: Build class compositions ----
    print("\n--- S1: BUILD PER-FOLIO AXM CLASS COMPOSITIONS ---")
    class_counts, class_props, prefix_counts, folio_sections = \
        build_class_compositions(token_to_class)

    # Intersect with C1035 folios (those with residual data)
    valid_folios = sorted(f for f in class_props if f in c1035_data)
    n = len(valid_folios)
    print(f"  {n} folios with both AXM composition and C1035 residual data")

    # Build matrices
    X_raw = np.array([class_props[f] for f in valid_folios])  # n x 32
    X_counts = np.array([class_counts[f] for f in valid_folios])
    axm_totals = X_counts.sum(axis=1)

    # Corpus-level proportions
    corpus_counts = X_counts.sum(axis=0)
    corpus_props = corpus_counts / corpus_counts.sum()

    print(f"\n  Corpus-level AXM class proportions (top 10):")
    top_classes = np.argsort(corpus_props)[::-1][:10]
    for idx in top_classes:
        cls = AXM_CLASS_ORDER[idx]
        print(f"    Class {cls:>3}: {corpus_props[idx]:.4f} ({corpus_counts[idx]} tokens)")

    # Zero-cell statistics
    n_zero = (X_counts == 0).sum()
    n_zero_per_folio = (X_counts == 0).sum(axis=1)
    active_per_folio = N_AXM - n_zero_per_folio
    print(f"\n  Zero cells: {n_zero}/{n * N_AXM} ({n_zero / (n * N_AXM) * 100:.1f}%)")
    print(f"  Active classes per folio: mean={active_per_folio.mean():.1f}, "
          f"min={active_per_folio.min()}, max={active_per_folio.max()}")

    # Identify hazard-adjacent classes
    hazard_adj, class_hazard_fracs = identify_hazard_adjacent_classes(token_to_class)
    hazard_adj_in_axm = hazard_adj & AXM_CLASSES_SET
    non_hazard_in_axm = AXM_CLASSES_SET - hazard_adj_in_axm
    print(f"\n  Hazard-adjacent AXM classes ({len(hazard_adj_in_axm)}): {sorted(hazard_adj_in_axm)}")
    print(f"  Non-hazard AXM classes ({len(non_hazard_in_axm)}): {sorted(non_hazard_in_axm)}")

    # ---- S2: CLR Transform + PCA ----
    print("\n--- S2: CLR TRANSFORM + PCA ---")

    X_clr = clr_transform(X_counts.astype(float))
    scores_clr, loadings_clr, explained_clr, k_clr = pca_numpy(X_clr)

    print(f"\n  CLR PCA: {k_clr} components retained")
    cumvar = np.cumsum(explained_clr)
    print(f"  Explained variance ratio:")
    for i in range(min(10, len(explained_clr))):
        marker = " *" if i < k_clr else ""
        print(f"    PC{i+1}: {explained_clr[i]:.4f} (cumulative: {cumvar[i]:.4f}){marker}")

    # Sensitivity: raw proportions PCA
    scores_raw, loadings_raw, explained_raw, k_raw = pca_numpy(X_raw)
    print(f"\n  Raw PCA: {k_raw} components retained, "
          f"top explained: {explained_raw[0]:.4f}")

    # Top loadings for PC1 (CLR)
    pc1_loadings = loadings_clr[0]
    top_pos = np.argsort(pc1_loadings)[::-1][:5]
    top_neg = np.argsort(pc1_loadings)[:5]
    print(f"\n  PC1 top positive loadings:")
    for idx in top_pos:
        print(f"    Class {AXM_CLASS_ORDER[idx]:>3}: {pc1_loadings[idx]:+.4f}")
    print(f"  PC1 top negative loadings:")
    for idx in top_neg:
        print(f"    Class {AXM_CLASS_ORDER[idx]:>3}: {pc1_loadings[idx]:+.4f}")

    # ---- S3: T1 -- Multinomial Overdispersion ----
    print("\n--- S3: T1 -- MULTINOMIAL OVERDISPERSION ---")

    overdispersion_ratios = []
    for j in range(N_AXM):
        p_j = corpus_props[j]
        if p_j < 0.001:
            continue  # Skip near-zero classes

        # Expected variance under multinomial: p(1-p)/n for each folio, averaged
        expected_vars = [p_j * (1 - p_j) / axm_totals[i] for i in range(n)]
        mean_expected_var = np.mean(expected_vars)

        # Observed variance of class fraction across folios
        observed_var = np.var(X_raw[:, j])

        ratio = observed_var / mean_expected_var if mean_expected_var > 0 else 0
        overdispersion_ratios.append((AXM_CLASS_ORDER[j], ratio))

    overdispersion_ratios.sort(key=lambda x: x[1], reverse=True)
    n_overdispersed = sum(1 for _, r in overdispersion_ratios if r > 2.0)
    n_tested = len(overdispersion_ratios)

    print(f"\n  {n_overdispersed}/{n_tested} classes with overdispersion ratio > 2.0")
    print(f"\n  Top 10 overdispersed:")
    print(f"  {'Class':>8} {'Ratio':>10}")
    for cls, ratio in overdispersion_ratios[:10]:
        print(f"  {cls:>8} {ratio:>10.2f}")
    print(f"\n  Bottom 5:")
    for cls, ratio in overdispersion_ratios[-5:]:
        print(f"  {cls:>8} {ratio:>10.2f}")

    # Aggregate chi-squared
    chi2_total = 0
    for i in range(n):
        ni = axm_totals[i]
        expected = corpus_props * ni
        observed = X_counts[i].astype(float)
        # Only include cells with expected > 0
        mask = expected > 0
        chi2_total += np.sum((observed[mask] - expected[mask]) ** 2 / expected[mask])

    df_total = n * (N_AXM - 1)
    chi2_p = 1.0 - stats.chi2.cdf(chi2_total, df_total) if df_total > 0 else 1.0

    print(f"\n  Aggregate chi-squared: {chi2_total:.1f} (df={df_total}, p={'<0.0001' if chi2_p < 0.0001 else f'{chi2_p:.6f}'})")

    # ---- S4: T2 -- Residual Prediction ----
    print("\n--- S4: T2 -- RESIDUAL PREDICTION ---")

    residuals = np.array([c1035_data[f]['c1017_residual'] for f in valid_folios])
    axm_self = np.array([c1035_data[f]['axm_self'] for f in valid_folios])

    print(f"\n  C1035 residual: mean={residuals.mean():.6f}, std={residuals.std():.4f}")

    # Test with different numbers of PCs
    print(f"\n  Residual prediction from class PCs (CLR):")
    print(f"  {'k PCs':>8} {'R2 train':>10} {'R2 LOO':>10}")
    best_loo_r2 = -999
    best_k = 0
    for k in [2, 3, 5, k_clr, min(10, k_clr + 3)]:
        k = min(k, scores_clr.shape[1])
        X_k = scores_clr[:, :k]
        _, r2_train, _ = ols_fit(X_k, residuals)
        r2_loo = loo_cv_r2(X_k, residuals)
        print(f"  {k:>8} {r2_train:>10.4f} {r2_loo:>10.4f}")
        if r2_loo > best_loo_r2:
            best_loo_r2 = r2_loo
            best_k = k

    print(f"\n  Best LOO R2: {best_loo_r2:.4f} at k={best_k}")

    # Also test: predict AXM self-transition directly
    print(f"\n  AXM self-transition prediction from class PCs:")
    print(f"  {'k PCs':>8} {'R2 train':>10} {'R2 LOO':>10}")
    for k in [2, 3, 5, k_clr]:
        k = min(k, scores_clr.shape[1])
        X_k = scores_clr[:, :k]
        _, r2_train, _ = ols_fit(X_k, axm_self)
        r2_loo = loo_cv_r2(X_k, axm_self)
        print(f"  {k:>8} {r2_train:>10.4f} {r2_loo:>10.4f}")

    # Incremental R-squared beyond C1017 baseline
    # Build C1017 predictor matrix from c1035_data
    regime_set = sorted(set(c1035_data[f]['regime'] for f in valid_folios))
    section_set = sorted(set(c1035_data[f]['section'] for f in valid_folios))

    X_baseline = []
    for f in valid_folios:
        d = c1035_data[f]
        row = []
        # REGIME dummies
        for r in regime_set[1:]:  # drop first for reference
            row.append(1.0 if d['regime'] == r else 0.0)
        # Section dummies
        for s in section_set[1:]:
            row.append(1.0 if d['section'] == s else 0.0)
        # Continuous predictors (standardize)
        row.extend([d['prefix_entropy'], d['hazard_density'], d['bridge_pc1']])
        X_baseline.append(row)
    X_baseline = np.array(X_baseline)
    # Standardize continuous columns
    for j in range(len(regime_set) - 1 + len(section_set) - 1, X_baseline.shape[1]):
        col = X_baseline[:, j]
        X_baseline[:, j] = (col - col.mean()) / (col.std() + 1e-10)

    _, r2_baseline, _ = ols_fit(X_baseline, axm_self)
    r2_loo_baseline = loo_cv_r2(X_baseline, axm_self)
    print(f"\n  C1017 baseline: R2={r2_baseline:.4f}, LOO={r2_loo_baseline:.4f}")

    # Combined: baseline + class PCs
    X_combined = np.column_stack([X_baseline, scores_clr[:, :best_k]])
    _, r2_combined, _ = ols_fit(X_combined, axm_self)
    r2_loo_combined = loo_cv_r2(X_combined, axm_self)
    incremental_r2 = r2_combined - r2_baseline
    incremental_loo = r2_loo_combined - r2_loo_baseline
    print(f"  Combined (baseline + {best_k} PCs): R2={r2_combined:.4f}, LOO={r2_loo_combined:.4f}")
    print(f"  Incremental R2: {incremental_r2:+.4f} (train), {incremental_loo:+.4f} (LOO)")

    # ---- S5: T3 -- C458 Localization ----
    print("\n--- S5: T3 -- C458 LOCALIZATION ---")

    hazard_indices = [AXM_IDX[c] for c in hazard_adj_in_axm if c in AXM_IDX]
    non_hazard_indices = [AXM_IDX[c] for c in non_hazard_in_axm if c in AXM_IDX]

    # Per-folio hazard-adjacent fraction (sum of hazard-adj class proportions)
    hazard_fracs = X_raw[:, hazard_indices].sum(axis=1)
    non_hazard_fracs = X_raw[:, non_hazard_indices].sum(axis=1)

    cv_hazard = hazard_fracs.std() / hazard_fracs.mean() if hazard_fracs.mean() > 0 else float('inf')
    cv_non_hazard = non_hazard_fracs.std() / non_hazard_fracs.mean() if non_hazard_fracs.mean() > 0 else float('inf')

    print(f"\n  Hazard-adjacent classes: {sorted(hazard_adj_in_axm)}")
    print(f"  Hazard fraction: mean={hazard_fracs.mean():.4f}, std={hazard_fracs.std():.4f}, CV={cv_hazard:.4f}")
    print(f"  Non-hazard fraction: mean={non_hazard_fracs.mean():.4f}, std={non_hazard_fracs.std():.4f}, CV={cv_non_hazard:.4f}")
    print(f"  CV difference: {cv_hazard - cv_non_hazard:+.4f}")

    # Per-class CV comparison
    hazard_cvs = []
    non_hazard_cvs = []
    print(f"\n  Per-class CV:")
    print(f"  {'Class':>8} {'Group':>12} {'Mean':>8} {'CV':>8}")
    for j in range(N_AXM):
        cls = AXM_CLASS_ORDER[j]
        vals = X_raw[:, j]
        mean_v = vals.mean()
        cv = vals.std() / mean_v if mean_v > 0.001 else None
        group = "HAZARD" if cls in hazard_adj_in_axm else "non-haz"
        if cv is not None:
            if cls in hazard_adj_in_axm:
                hazard_cvs.append(cv)
            else:
                non_hazard_cvs.append(cv)
    mean_cv_hazard = np.mean(hazard_cvs) if hazard_cvs else None
    mean_cv_non_hazard = np.mean(non_hazard_cvs) if non_hazard_cvs else None
    print(f"\n  Mean per-class CV (hazard-adj): {mean_cv_hazard:.4f}" if mean_cv_hazard else "  No hazard CVs")
    print(f"  Mean per-class CV (non-hazard): {mean_cv_non_hazard:.4f}" if mean_cv_non_hazard else "  No non-hazard CVs")
    if mean_cv_hazard is not None and mean_cv_non_hazard is not None:
        cv_diff_perclass = mean_cv_hazard - mean_cv_non_hazard
        print(f"  Per-class CV difference: {cv_diff_perclass:+.4f}")

    # ---- S6: T4 -- PREFIX Mediation ----
    print("\n--- S6: T4 -- PREFIX MEDIATION ---")

    # Build PREFIX distribution matrix
    all_prefixes = set()
    for f in valid_folios:
        all_prefixes.update(prefix_counts.get(f, {}).keys())
    prefix_order = sorted(all_prefixes)
    n_prefixes = len(prefix_order)
    prefix_idx = {p: i for i, p in enumerate(prefix_order)}

    X_prefix = np.zeros((n, n_prefixes))
    for i, f in enumerate(valid_folios):
        pc = prefix_counts.get(f, {})
        for p, count in pc.items():
            X_prefix[i, prefix_idx[p]] = count

    # Normalize to proportions
    row_sums = X_prefix.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    X_prefix_prop = X_prefix / row_sums

    # PCA on PREFIX proportions (CLR)
    X_prefix_clr = clr_transform(X_prefix)
    scores_prefix, _, explained_prefix, k_prefix = pca_numpy(X_prefix_clr)

    print(f"  {n_prefixes} unique PREFIXes in AXM tokens")
    print(f"  PREFIX PCA: {k_prefix} components retained")
    print(f"  Top explained: {explained_prefix[0]:.4f}, {explained_prefix[1]:.4f}")

    # Correlation: PREFIX PC1 vs class PC1
    rho_prefix_class, p_prefix_class = stats.spearmanr(
        scores_prefix[:, 0], scores_clr[:, 0])
    print(f"\n  PREFIX PC1 vs Class PC1: rho={rho_prefix_class:.4f} (p={p_prefix_class:.6f})")

    # Also test PC2
    if scores_prefix.shape[1] >= 2 and scores_clr.shape[1] >= 2:
        rho_p2_c2, p_p2_c2 = stats.spearmanr(scores_prefix[:, 1], scores_clr[:, 1])
        rho_p1_c2, p_p1_c2 = stats.spearmanr(scores_prefix[:, 0], scores_clr[:, 1])
        print(f"  PREFIX PC2 vs Class PC2: rho={rho_p2_c2:.4f} (p={p_p2_c2:.6f})")
        print(f"  PREFIX PC1 vs Class PC2: rho={rho_p1_c2:.4f} (p={p_p1_c2:.6f})")

    # ---- S7: T5 -- Class Diversity Metrics ----
    print("\n--- S7: T5 -- CLASS DIVERSITY METRICS ---")

    # Shannon entropy per folio
    entropies = []
    gini_simpsons = []
    effective_n_classes = []
    for i in range(n):
        props = X_raw[i]
        # Shannon entropy (base 2)
        nonzero = props[props > 0]
        H = -np.sum(nonzero * np.log2(nonzero))
        entropies.append(H)
        effective_n_classes.append(2 ** H)
        # Gini-Simpson
        gs = 1 - np.sum(props ** 2)
        gini_simpsons.append(gs)

    entropies = np.array(entropies)
    effective_n = np.array(effective_n_classes)
    gini_s = np.array(gini_simpsons)

    print(f"\n  Shannon entropy: mean={entropies.mean():.3f}, std={entropies.std():.3f}")
    print(f"  Effective classes: mean={effective_n.mean():.1f}, min={effective_n.min():.1f}, max={effective_n.max():.1f}")
    print(f"  Gini-Simpson: mean={gini_s.mean():.4f}")

    # Correlations with AXM self-transition and residual
    rho_ent_axm, p_ent_axm = stats.spearmanr(entropies, axm_self)
    rho_ent_res, p_ent_res = stats.spearmanr(entropies, residuals)
    rho_gs_axm, p_gs_axm = stats.spearmanr(gini_s, axm_self)

    print(f"\n  Entropy vs AXM self-transition: rho={rho_ent_axm:.4f} (p={p_ent_axm:.6f})")
    print(f"  Entropy vs C1035 residual:       rho={rho_ent_res:.4f} (p={p_ent_res:.6f})")
    print(f"  Gini-Simpson vs AXM self-trans:  rho={rho_gs_axm:.4f} (p={p_gs_axm:.6f})")

    # ---- S8: T6 -- Variance Decomposition ----
    print("\n--- S8: T6 -- VARIANCE DECOMPOSITION ---")

    regime_labels = [regimes.get(f, 'R0') for f in valid_folios]
    section_labels = [folio_sections.get(f, 'X') for f in valid_folios]
    archetype_labels = [str(archetypes.get(f, -1)) for f in valid_folios]

    print(f"\n  eta-squared on class composition PCs:")
    print(f"  {'':>6} {'REGIME':>10} {'Section':>10} {'Archetype':>10}")
    eta_results = {}
    for pc_idx in range(min(3, k_clr)):
        vals = scores_clr[:, pc_idx]
        e_reg = eta_squared(vals, regime_labels)
        e_sec = eta_squared(vals, section_labels)
        e_arch = eta_squared(vals, archetype_labels)
        label = f"PC{pc_idx+1}"
        print(f"  {label:>6} {e_reg:>10.4f} {e_sec:>10.4f} {e_arch:>10.4f}")
        eta_results[label] = {
            'eta2_regime': round(float(e_reg), 4),
            'eta2_section': round(float(e_sec), 4),
            'eta2_archetype': round(float(e_arch), 4),
        }

    # Also on entropy
    e_reg_ent = eta_squared(entropies, regime_labels)
    e_sec_ent = eta_squared(entropies, section_labels)
    print(f"  {'H':>6} {e_reg_ent:>10.4f} {e_sec_ent:>10.4f}")

    # ---- S9: Evaluate P1-P6 ----
    print(f"\n{'='*70}")
    print("  S9: HYPOTHESIS EVALUATION")
    print(f"{'='*70}")

    predictions = {}

    # P1: Overdispersion
    p1_pass = n_overdispersed >= n_tested * 0.5
    predictions['P1'] = {
        'description': 'AXM class profiles exceed multinomial sampling noise',
        'result': f'{n_overdispersed}/{n_tested} classes overdispersed (>2.0), chi2 p={"<0.0001" if chi2_p < 0.0001 else f"{chi2_p:.6f}"}',
        'n_overdispersed': n_overdispersed,
        'n_tested': n_tested,
        'chi2': round(float(chi2_total), 1),
        'pass': p1_pass,
    }

    # P2: Residual prediction
    p2_pass = best_loo_r2 > 0.10
    predictions['P2'] = {
        'description': 'Class profile PCs predict C1035 residual (LOO R2 > 0.10)',
        'result': f'Best LOO R2={best_loo_r2:.4f} at k={best_k}',
        'best_loo_r2': round(float(best_loo_r2), 4),
        'best_k': best_k,
        'incremental_r2': round(float(incremental_r2), 4),
        'incremental_loo': round(float(incremental_loo), 4),
        'pass': p2_pass,
    }

    # P3: C458 localization
    if mean_cv_hazard is not None and mean_cv_non_hazard is not None:
        p3_pass = mean_cv_hazard < mean_cv_non_hazard and (mean_cv_non_hazard - mean_cv_hazard) > 0.05
    else:
        p3_pass = False
    predictions['P3'] = {
        'description': 'Hazard-adjacent class CV < non-hazard class CV (C458 clamping)',
        'result': f'CV(hazard)={mean_cv_hazard:.4f}, CV(non-hazard)={mean_cv_non_hazard:.4f}, '
                  f'diff={mean_cv_hazard - mean_cv_non_hazard:+.4f}' if mean_cv_hazard and mean_cv_non_hazard else 'Insufficient data',
        'cv_hazard': round(float(mean_cv_hazard), 4) if mean_cv_hazard else None,
        'cv_non_hazard': round(float(mean_cv_non_hazard), 4) if mean_cv_non_hazard else None,
        'pass': p3_pass,
    }

    # P4: PREFIX mediation
    p4_pass = abs(rho_prefix_class) > 0.30 and p_prefix_class < 0.01
    predictions['P4'] = {
        'description': 'PREFIX PC1 co-varies with Class PC1 (|rho| > 0.30)',
        'result': f'rho={rho_prefix_class:.4f}, p={p_prefix_class:.6f}',
        'rho': round(float(rho_prefix_class), 4),
        'pass': p4_pass,
    }

    # P5: Diversity correlation
    p5_pass = abs(rho_ent_axm) > 0.25 and p_ent_axm < 0.01
    predictions['P5'] = {
        'description': 'Class diversity correlates with AXM self-transition (|rho| > 0.25)',
        'result': f'rho={rho_ent_axm:.4f}, p={p_ent_axm:.6f}',
        'rho': round(float(rho_ent_axm), 4),
        'pass': p5_pass,
    }

    # P6: REGIME independence
    pc1_eta = eta_results.get('PC1', {}).get('eta2_regime', 1.0)
    pc2_eta = eta_results.get('PC2', {}).get('eta2_regime', 1.0)
    pc3_eta = eta_results.get('PC3', {}).get('eta2_regime', 1.0)
    p6_pass = pc1_eta < 0.30 and pc2_eta < 0.30 and pc3_eta < 0.30
    predictions['P6'] = {
        'description': 'REGIME does not explain class profiles (eta2 < 0.30 on PC1-3)',
        'result': f'eta2: PC1={pc1_eta:.4f}, PC2={pc2_eta:.4f}, PC3={pc3_eta:.4f}',
        'pass': p6_pass,
    }

    # Print summary
    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    for pk, pv in sorted(predictions.items()):
        status = 'PASS' if pv['pass'] else 'FAIL'
        print(f"  {pk}: {pv['description']}")
        print(f"      {pv['result']} -> {status}")

    print(f"\n  VERDICT: {n_pass}/{n_total} PASS")

    if n_pass >= 5:
        verdict = 'AXM_CLASS_COMPOSITION_CONFIRMED'
    elif n_pass >= 3:
        verdict = 'AXM_CLASS_COMPOSITION_SUPPORTED'
    else:
        verdict = 'AXM_CLASS_COMPOSITION_NOT_FOUND'
    print(f"  {verdict}")

    # ---- Write results ----
    results = {
        'phase_name': 'AXM_CLASS_COMPOSITION',
        'phase_number': 359,
        'n_folios': n,
        'n_axm_classes': N_AXM,
        's1_class_profiles': {
            'corpus_proportions': {str(AXM_CLASS_ORDER[j]): round(float(corpus_props[j]), 6)
                                   for j in range(N_AXM)},
            'n_zero_cells': int(n_zero),
            'active_classes_per_folio': {
                'mean': round(float(active_per_folio.mean()), 1),
                'min': int(active_per_folio.min()),
                'max': int(active_per_folio.max()),
            },
            'hazard_adjacent_classes': sorted(hazard_adj_in_axm),
            'class_hazard_fracs': {str(k): v for k, v in class_hazard_fracs.items()},
        },
        's2_pca': {
            'n_components_clr': k_clr,
            'explained_variance_clr': [round(float(x), 4) for x in explained_clr[:10]],
            'cumulative_variance_clr': [round(float(x), 4) for x in cumvar[:10]],
            'n_components_raw': k_raw,
            'explained_variance_raw': [round(float(x), 4) for x in explained_raw[:10]],
        },
        's3_overdispersion': {
            'overdispersion_ratios': {str(c): round(float(r), 2) for c, r in overdispersion_ratios},
            'n_overdispersed': n_overdispersed,
            'n_tested': n_tested,
            'chi2_total': round(float(chi2_total), 1),
            'chi2_df': df_total,
            'chi2_p': chi2_p,
        },
        's4_residual_prediction': {
            'best_loo_r2': round(float(best_loo_r2), 4),
            'best_k': best_k,
            'r2_baseline': round(float(r2_baseline), 4),
            'r2_loo_baseline': round(float(r2_loo_baseline), 4),
            'r2_combined': round(float(r2_combined), 4),
            'r2_loo_combined': round(float(r2_loo_combined), 4),
            'incremental_r2': round(float(incremental_r2), 4),
            'incremental_loo': round(float(incremental_loo), 4),
        },
        's5_c458_localization': {
            'hazard_adjacent_classes': sorted(hazard_adj_in_axm),
            'cv_hazard_aggregate': round(float(cv_hazard), 4),
            'cv_non_hazard_aggregate': round(float(cv_non_hazard), 4),
            'mean_cv_hazard_perclass': round(float(mean_cv_hazard), 4) if mean_cv_hazard else None,
            'mean_cv_non_hazard_perclass': round(float(mean_cv_non_hazard), 4) if mean_cv_non_hazard else None,
        },
        's6_prefix_mediation': {
            'n_prefixes': n_prefixes,
            'prefix_pc1_vs_class_pc1_rho': round(float(rho_prefix_class), 4),
            'prefix_pc1_vs_class_pc1_p': round(float(p_prefix_class), 6),
        },
        's7_diversity': {
            'entropy_mean': round(float(entropies.mean()), 3),
            'entropy_std': round(float(entropies.std()), 3),
            'effective_classes_mean': round(float(effective_n.mean()), 1),
            'entropy_vs_axm_self_rho': round(float(rho_ent_axm), 4),
            'entropy_vs_axm_self_p': round(float(p_ent_axm), 6),
            'entropy_vs_residual_rho': round(float(rho_ent_res), 4),
            'entropy_vs_residual_p': round(float(p_ent_res), 6),
        },
        's8_variance_decomposition': eta_results,
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'axm_class_composition.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - start
    print(f"\nResults written to: {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
