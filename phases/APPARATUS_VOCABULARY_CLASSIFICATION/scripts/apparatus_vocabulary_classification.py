"""
Phase 445: APPARATUS_VOCABULARY_CLASSIFICATION
================================================
Tests whether Currier B folios can be classified by apparatus type
based on vocabulary signatures, beyond what REGIME and section explain.

Hypothesis: Different apparatus types (alembic, balneum marie, retort,
decoction pot) require different control vocabularies. If apparatus type
is encoded, vocabulary clusters should emerge AFTER controlling for REGIME
and section.

Tests:
  T1:  REGIME-Residual PCA (primary discovery)
  T2:  Within-REGIME Vocabulary Clustering
  T3:  t/ok/ee Triangle Discrimination
  T4:  ke/ek Ratio as Apparatus Discriminator
  T5:  Archetype-Vocabulary Cross-Validation (C1016)

Constraints referenced:
  C663 (501 effective PREFIX-MIDDLE pairs), C1016 (6 archetypes, ARI=0.065),
  C1153 (~40% design freedom), C1226 (ke/ek conditioning),
  C980 (free variation envelope), C179 (4 REGIMEs), C911 (PREFIX selectivity),
  C171 (semantic ceiling)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
np.random.seed(42)

RESULTS_DIR = ROOT / "phases" / "APPARATUS_VOCABULARY_CLASSIFICATION" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REGIME_PATH = ROOT / "data" / "regime_folio_mapping.json"
ARCHETYPE_PATH = (ROOT / "phases" / "FOLIO_MACRO_AUTOMATON_DECOMPOSITION"
                  / "results" / "folio_macro_decomposition.json")

MIN_FOLIO_TOKENS = 50
N_PERM = 1000
CLUSTER_RANGE = range(2, 7)       # k=2..6 for T1
WITHIN_CLUSTER_RANGE = range(2, 6) # k=2..5 for T2


# ============================================================
# DATA LOADING
# ============================================================

def load_regime_map():
    """Load folio -> REGIME mapping from regime_folio_mapping.json."""
    with open(REGIME_PATH, encoding='utf-8') as f:
        raw = json.load(f)
    assignments = raw.get('regime_assignments', raw)
    return {k: v.get('regime', 'UNK') if isinstance(v, dict) else v
            for k, v in assignments.items()}


def load_archetype_labels():
    """Load C1016 archetype labels per folio."""
    with open(ARCHETYPE_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return data['t2_archetype_discovery']['folio_labels']


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_folio_data():
    """
    Single pass through Currier B: build per-folio PREFIX-MIDDLE counters
    and derived apparatus-relevant features.

    Returns:
        folio_pm_counts: {folio: Counter of (prefix, middle) tuples}
        folio_sections:  {folio: section_string}
        folio_token_counts: {folio: int}
        folio_derived: {folio: dict of t_rate, ok_rate, ee_rate, ke_count, ek_count, ke_ek_ratio}
    """
    tx = Transcript()
    morph = Morphology()

    folio_pm_counts = defaultdict(Counter)
    folio_sections = {}
    folio_token_counts = Counter()

    # Raw accumulators for derived features
    folio_t_count = Counter()
    folio_ok_count = Counter()
    folio_ee_count = Counter()
    folio_ke_count = Counter()
    folio_ek_count = Counter()

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        folio = token.folio
        folio_token_counts[folio] += 1
        folio_sections[folio] = token.section

        m = morph.extract(w)
        mid = m.middle or '_EMPTY_'
        pfx = m.prefix or 'NONE'

        folio_pm_counts[folio][(pfx, mid)] += 1

        # Derived features
        if mid == 't':
            folio_t_count[folio] += 1
        if pfx == 'ok':
            folio_ok_count[folio] += 1
        if mid and 'ee' in mid:
            folio_ee_count[folio] += 1
        if pfx == 'ke':
            folio_ke_count[folio] += 1
        if w.startswith('ek'):
            folio_ek_count[folio] += 1

    # Compute derived features
    folio_derived = {}
    for f in folio_token_counts:
        total = folio_token_counts[f]
        ke = folio_ke_count[f]
        ek = folio_ek_count[f]
        folio_derived[f] = {
            't_rate': folio_t_count[f] / total if total > 0 else 0,
            'ok_rate': folio_ok_count[f] / total if total > 0 else 0,
            'ee_family_rate': folio_ee_count[f] / total if total > 0 else 0,
            'ke_count': ke,
            'ek_count': ek,
            'ke_ek_ratio': ke / (ke + ek) if (ke + ek) > 0 else None,
        }

    return dict(folio_pm_counts), folio_sections, dict(folio_token_counts), folio_derived


def build_feature_matrix(folio_pm_counts, folio_list):
    """Build N_folio x D matrix from per-folio PM counters.

    Returns:
        X: raw count matrix (N x D)
        pm_pairs: sorted list of (prefix, middle) tuples (column order)
    """
    # Collect all observed PM pairs
    all_pairs = set()
    for counts in folio_pm_counts.values():
        all_pairs.update(counts.keys())
    pm_pairs = sorted(all_pairs)
    pair_to_idx = {p: i for i, p in enumerate(pm_pairs)}

    X = np.zeros((len(folio_list), len(pm_pairs)), dtype=np.float64)
    for i, f in enumerate(folio_list):
        for pair, count in folio_pm_counts[f].items():
            if pair in pair_to_idx:
                X[i, pair_to_idx[pair]] = count
    return X, pm_pairs


def hellinger_transform(X):
    """Hellinger transform: sqrt of relative frequencies.

    Robust for sparse count data. Euclidean distance on Hellinger-transformed
    data equals Hellinger distance (proper metric for distributions).
    """
    row_sums = X.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    return np.sqrt(X / row_sums)


# ============================================================
# T1: REGIME-RESIDUAL PCA
# ============================================================

def residualize_by_regime(X, folio_list, regime_map):
    """Subtract REGIME centroid from each folio vector."""
    regime_groups = defaultdict(list)
    for i, f in enumerate(folio_list):
        regime_groups[regime_map.get(f, 'UNK')].append(i)

    centroids = {}
    for r, indices in regime_groups.items():
        centroids[r] = X[indices].mean(axis=0)

    X_res = np.zeros_like(X)
    for i, f in enumerate(folio_list):
        r = regime_map.get(f, 'UNK')
        X_res[i] = X[i] - centroids[r]
    return X_res


def residualize_by_regression(X, folio_list, regime_map, folio_sections):
    """OLS residualization: regress X on REGIME + section dummies."""
    regimes = sorted(set(regime_map.get(f, 'UNK') for f in folio_list))
    sections = sorted(set(folio_sections.get(f, '?') for f in folio_list))

    # Build dummy matrix (drop first category for each as reference)
    n = len(folio_list)
    n_regime_dummies = max(len(regimes) - 1, 0)
    n_section_dummies = max(len(sections) - 1, 0)
    n_cols = 1 + n_regime_dummies + n_section_dummies  # intercept + dummies

    D = np.zeros((n, n_cols))
    D[:, 0] = 1  # intercept
    for i, f in enumerate(folio_list):
        r = regime_map.get(f, 'UNK')
        idx = regimes.index(r) - 1  # skip reference category
        if idx >= 0:
            D[i, 1 + idx] = 1
        s = folio_sections.get(f, '?')
        idx_s = sections.index(s) - 1
        if idx_s >= 0:
            D[i, 1 + n_regime_dummies + idx_s] = 1

    # OLS: X_hat = D @ (D'D)^-1 D' @ X, residuals = X - X_hat
    beta, _, _, _ = np.linalg.lstsq(D, X, rcond=None)
    X_hat = D @ beta
    return X - X_hat


def run_t1(X_hell, folio_list, regime_map, folio_sections):
    """T1: REGIME-Residual PCA — discover structure beyond REGIME."""
    print("\n" + "=" * 60)
    print("T1: REGIME-RESIDUAL PCA")
    print("=" * 60)

    # Method 1: centroid subtraction
    X_res = residualize_by_regime(X_hell, folio_list, regime_map)

    n_comp = min(10, len(folio_list) - 1, X_res.shape[1])
    pca = PCA(n_components=n_comp, random_state=42)
    scores = pca.fit_transform(X_res)
    var_exp = pca.explained_variance_ratio_.tolist()
    cum_4pc = sum(var_exp[:4])

    print(f"  Variance explained (first 10 PCs): {[f'{v:.4f}' for v in var_exp]}")
    print(f"  Cumulative 4-PC: {cum_4pc:.4f}")

    # Cluster on first 4 PCs
    scores_4 = scores[:, :4]
    best_k, best_sil = 2, -1
    sil_by_k = {}
    for k in CLUSTER_RANGE:
        if k >= len(folio_list):
            break
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(scores_4)
        sil = silhouette_score(scores_4, km.labels_)
        sil_by_k[k] = round(sil, 4)
        if sil > best_sil:
            best_sil = sil
            best_k = k

    # Get cluster labels at best k
    km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(scores_4)
    cluster_labels = {folio_list[i]: int(km_best.labels_[i]) for i in range(len(folio_list))}

    print(f"  Best k={best_k}, silhouette={best_sil:.4f}")
    print(f"  Silhouettes: {sil_by_k}")

    # Method 2: OLS regression sensitivity check
    X_res_ols = residualize_by_regression(X_hell, folio_list, regime_map, folio_sections)
    pca_ols = PCA(n_components=n_comp, random_state=42)
    pca_ols.fit(X_res_ols)
    cum_4pc_ols = sum(pca_ols.explained_variance_ratio_[:4].tolist())
    print(f"  OLS sensitivity: cumulative 4-PC = {cum_4pc_ols:.4f}")

    # Pass condition
    passed = cum_4pc > 0.30 and best_sil > 0.15
    print(f"  PASS: {passed} (cum_4pc>0.30={cum_4pc>0.30}, sil>0.15={best_sil>0.15})")

    # Store PC scores for T4
    folio_pc_scores = {folio_list[i]: scores[i, :4].tolist() for i in range(len(folio_list))}

    return {
        'variance_explained_pcs': [round(v, 6) for v in var_exp],
        'cumulative_4pc': round(cum_4pc, 4),
        'best_k': best_k,
        'best_silhouette': round(best_sil, 4),
        'silhouette_by_k': sil_by_k,
        'folio_cluster_labels': cluster_labels,
        'folio_pc_scores': folio_pc_scores,
        'sensitivity_ols_cumulative_4pc': round(cum_4pc_ols, 4),
        'pass': passed,
    }


# ============================================================
# T2: WITHIN-REGIME VOCABULARY CLUSTERING
# ============================================================

def run_t2(X_hell, folio_list, regime_map, pm_pairs):
    """T2: cluster folios within each REGIME separately."""
    print("\n" + "=" * 60)
    print("T2: WITHIN-REGIME VOCABULARY CLUSTERING")
    print("=" * 60)

    regime_groups = defaultdict(list)
    for i, f in enumerate(folio_list):
        regime_groups[regime_map.get(f, 'UNK')].append(i)

    regime_results = {}
    n_passing = 0

    for regime in sorted(regime_groups.keys()):
        indices = regime_groups[regime]
        n = len(indices)
        if n < 6:
            print(f"  {regime}: {n} folios — SKIP (need >=6)")
            regime_results[regime] = {'n_folios': n, 'skipped': True}
            continue

        X_sub = X_hell[indices]
        scaler = StandardScaler()
        X_std = scaler.fit_transform(X_sub)

        best_k, best_sil = 2, -1
        sils = {}
        for k in WITHIN_CLUSTER_RANGE:
            if k >= n:
                break
            km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_std)
            sil = silhouette_score(X_std, km.labels_)
            sils[k] = round(sil, 4)
            if sil > best_sil:
                best_sil = sil
                best_k = k

        # Get best clustering
        km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(X_std)
        sub_folios = [folio_list[i] for i in indices]
        labels = {sub_folios[j]: int(km_best.labels_[j]) for j in range(n)}

        # Signature features: top 5 by centroid difference (for k=2 case, or biggest spread)
        signatures = []
        centroids_raw = np.zeros((best_k, X_sub.shape[1]))
        for c in range(best_k):
            mask = km_best.labels_ == c
            if mask.sum() > 0:
                centroids_raw[c] = X_sub[mask].mean(axis=0)

        if best_k == 2:
            diff = centroids_raw[0] - centroids_raw[1]
            top_indices = np.argsort(np.abs(diff))[-10:][::-1]
            for idx in top_indices:
                pfx, mid = pm_pairs[idx]
                signatures.append({
                    'pair': f"{pfx}+{mid}",
                    'diff': round(float(diff[idx]), 6),
                    'c0_mean': round(float(centroids_raw[0, idx]), 6),
                    'c1_mean': round(float(centroids_raw[1, idx]), 6),
                })
        else:
            # For k>2, find features with highest variance across centroids
            var_across = centroids_raw.var(axis=0)
            top_indices = np.argsort(var_across)[-10:][::-1]
            for idx in top_indices:
                pfx, mid = pm_pairs[idx]
                signatures.append({
                    'pair': f"{pfx}+{mid}",
                    'variance': round(float(var_across[idx]), 6),
                })

        passed_regime = best_sil > 0.15
        if passed_regime:
            n_passing += 1

        cluster_sizes = Counter(km_best.labels_.tolist())

        print(f"  {regime}: {n} folios, best_k={best_k}, sil={best_sil:.4f} "
              f"{'PASS' if passed_regime else 'FAIL'}")
        print(f"    Cluster sizes: {dict(cluster_sizes)}")
        if signatures:
            print(f"    Top signatures: {', '.join(s['pair'] for s in signatures[:5])}")

        regime_results[regime] = {
            'n_folios': n,
            'best_k': best_k,
            'best_silhouette': round(best_sil, 4),
            'silhouettes_by_k': sils,
            'cluster_labels': labels,
            'cluster_sizes': {str(k): v for k, v in cluster_sizes.items()},
            'signature_features': signatures,
            'pass': passed_regime,
        }

    passed = n_passing >= 2
    print(f"\n  REGIMEs passing: {n_passing}/4")
    print(f"  T2 PASS: {passed}")

    return {
        'regime_results': regime_results,
        'n_regimes_passing': n_passing,
        'pass': passed,
    }


# ============================================================
# T3: t/ok/ee TRIANGLE DISCRIMINATION
# ============================================================

def run_t3(folio_derived, folio_list, regime_map):
    """T3: test whether t/ok/ee rates form apparatus-discriminating clusters."""
    print("\n" + "=" * 60)
    print("T3: t/ok/ee TRIANGLE DISCRIMINATION")
    print("=" * 60)

    n = len(folio_list)
    triangle = np.zeros((n, 3))
    for i, f in enumerate(folio_list):
        d = folio_derived[f]
        triangle[i] = [d['t_rate'], d['ok_rate'], d['ee_family_rate']]

    # Residualize against REGIME centroids in 3D
    regime_groups = defaultdict(list)
    for i, f in enumerate(folio_list):
        regime_groups[regime_map.get(f, 'UNK')].append(i)

    centroids_3d = {}
    for r, indices in regime_groups.items():
        centroids_3d[r] = triangle[indices].mean(axis=0)

    residuals_3d = np.zeros_like(triangle)
    for i, f in enumerate(folio_list):
        r = regime_map.get(f, 'UNK')
        residuals_3d[i] = triangle[i] - centroids_3d[r]

    # Full 3D: best k, silhouette
    best_k_3d, best_sil_3d = 2, -1
    for k in range(2, 5):
        if k >= n:
            break
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(residuals_3d)
        sil = silhouette_score(residuals_3d, km.labels_)
        if sil > best_sil_3d:
            best_sil_3d = sil
            best_k_3d = k

    # Permutation test on full 3D
    real_sil = best_sil_3d
    n_exceed = 0
    for _ in range(N_PERM):
        # Shuffle REGIME assignments
        shuffled_regime = list(regime_map.get(f, 'UNK') for f in folio_list)
        np.random.shuffle(shuffled_regime)
        # Recompute centroids and residuals
        shuf_groups = defaultdict(list)
        for i, r in enumerate(shuffled_regime):
            shuf_groups[r].append(i)
        shuf_centroids = {}
        for r, indices in shuf_groups.items():
            shuf_centroids[r] = triangle[indices].mean(axis=0)
        shuf_res = np.zeros_like(triangle)
        for i in range(n):
            shuf_res[i] = triangle[i] - shuf_centroids[shuffled_regime[i]]
        km = KMeans(n_clusters=best_k_3d, n_init=5, random_state=42).fit(shuf_res)
        shuf_sil = silhouette_score(shuf_res, km.labels_)
        if shuf_sil >= real_sil:
            n_exceed += 1

    p_3d = (n_exceed + 1) / (N_PERM + 1)
    print(f"  Full 3D: k={best_k_3d}, sil={best_sil_3d:.4f}, perm_p={p_3d:.4f}")

    # Pairwise projections
    dim_names = ['t_rate', 'ok_rate', 'ee_family_rate']
    pairs = [(0, 1), (0, 2), (1, 2)]
    pair_names = ['t_vs_ok', 't_vs_ee', 'ok_vs_ee']
    pairwise_results = {}
    n_sig = 0

    for (d1, d2), name in zip(pairs, pair_names):
        res_2d = residuals_3d[:, [d1, d2]]

        # Best k for this pair
        best_sil_pw = -1
        best_k_pw = 2
        for k in range(2, 5):
            if k >= n:
                break
            km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(res_2d)
            s = silhouette_score(res_2d, km.labels_)
            if s > best_sil_pw:
                best_sil_pw = s
                best_k_pw = k

        # Permutation test
        n_exc_pw = 0
        for _ in range(N_PERM):
            shuffled_regime = list(regime_map.get(f, 'UNK') for f in folio_list)
            np.random.shuffle(shuffled_regime)
            shuf_groups = defaultdict(list)
            for i, r in enumerate(shuffled_regime):
                shuf_groups[r].append(i)
            shuf_centroids = {}
            for r, indices in shuf_groups.items():
                shuf_centroids[r] = triangle[indices].mean(axis=0)
            shuf_res = np.zeros_like(triangle)
            for i in range(n):
                shuf_res[i] = triangle[i] - shuf_centroids[shuffled_regime[i]]
            shuf_2d = shuf_res[:, [d1, d2]]
            km = KMeans(n_clusters=best_k_pw, n_init=5, random_state=42).fit(shuf_2d)
            shuf_sil = silhouette_score(shuf_2d, km.labels_)
            if shuf_sil >= best_sil_pw:
                n_exc_pw += 1

        p_pw = (n_exc_pw + 1) / (N_PERM + 1)
        sig = p_pw < 0.01
        if sig:
            n_sig += 1
        pairwise_results[name] = {
            'dim1': dim_names[d1],
            'dim2': dim_names[d2],
            'best_k': best_k_pw,
            'silhouette': round(best_sil_pw, 4),
            'permutation_p': round(p_pw, 4),
            'significant': sig,
        }
        print(f"  {name}: k={best_k_pw}, sil={best_sil_pw:.4f}, p={p_pw:.4f} "
              f"{'SIG' if sig else 'NS'}")

    # Correlation matrix of the three features
    corr_t_ok = sp_stats.spearmanr(triangle[:, 0], triangle[:, 1])
    corr_t_ee = sp_stats.spearmanr(triangle[:, 0], triangle[:, 2])
    corr_ok_ee = sp_stats.spearmanr(triangle[:, 1], triangle[:, 2])

    print(f"\n  Raw correlations (before residualization):")
    print(f"    t-ok:  rho={corr_t_ok.statistic:.3f}, p={corr_t_ok.pvalue:.4f}")
    print(f"    t-ee:  rho={corr_t_ee.statistic:.3f}, p={corr_t_ee.pvalue:.4f}")
    print(f"    ok-ee: rho={corr_ok_ee.statistic:.3f}, p={corr_ok_ee.pvalue:.4f}")

    passed = n_sig >= 2
    print(f"\n  Significant pairwise projections: {n_sig}/3")
    print(f"  T3 PASS: {passed}")

    return {
        'full_3d_best_k': best_k_3d,
        'full_3d_silhouette': round(best_sil_3d, 4),
        'full_3d_permutation_p': round(p_3d, 4),
        'pairwise_results': pairwise_results,
        'n_significant_pairs': n_sig,
        'correlations': {
            't_vs_ok': {'rho': round(corr_t_ok.statistic, 4), 'p': round(corr_t_ok.pvalue, 4)},
            't_vs_ee': {'rho': round(corr_t_ee.statistic, 4), 'p': round(corr_t_ee.pvalue, 4)},
            'ok_vs_ee': {'rho': round(corr_ok_ee.statistic, 4), 'p': round(corr_ok_ee.pvalue, 4)},
        },
        'pass': passed,
    }


# ============================================================
# T4: ke/ek RATIO AS APPARATUS DISCRIMINATOR
# ============================================================

def run_t4(folio_derived, folio_list, regime_map, folio_sections, t1_results):
    """T4: partial correlation of ke/ek ratio with T1 PCs after REGIME+section control."""
    print("\n" + "=" * 60)
    print("T4: ke/ek RATIO AS APPARATUS DISCRIMINATOR")
    print("=" * 60)

    # Filter to folios with enough ke+ek tokens
    MIN_KE_EK = 5
    valid_folios = []
    ke_ek_vals = []
    pc_scores = []
    for f in folio_list:
        d = folio_derived[f]
        if d['ke_ek_ratio'] is not None and (d['ke_count'] + d['ek_count']) >= MIN_KE_EK:
            if f in t1_results['folio_pc_scores']:
                valid_folios.append(f)
                ke_ek_vals.append(d['ke_ek_ratio'])
                pc_scores.append(t1_results['folio_pc_scores'][f])

    n = len(valid_folios)
    print(f"  Folios with ke+ek >= {MIN_KE_EK}: {n}")

    if n < 10:
        print("  TOO FEW FOLIOS — T4 INCONCLUSIVE")
        return {
            'n_folios_with_ke_ek': n,
            'partial_correlations': {},
            'any_significant': False,
            'pass': False,
            'note': 'insufficient data',
        }

    Y = np.array(ke_ek_vals)
    PC = np.array(pc_scores)  # (n, 4)

    # Build REGIME+section dummy matrix
    regimes = sorted(set(regime_map.get(f, 'UNK') for f in valid_folios))
    sections = sorted(set(folio_sections.get(f, '?') for f in valid_folios))
    n_r = max(len(regimes) - 1, 0)
    n_s = max(len(sections) - 1, 0)
    n_cols = 1 + n_r + n_s

    D = np.zeros((n, n_cols))
    D[:, 0] = 1
    for i, f in enumerate(valid_folios):
        r = regime_map.get(f, 'UNK')
        r_idx = regimes.index(r) - 1
        if r_idx >= 0:
            D[i, 1 + r_idx] = 1
        s = folio_sections.get(f, '?')
        s_idx = sections.index(s) - 1
        if s_idx >= 0:
            D[i, 1 + n_r + s_idx] = 1

    # Residualize Y on dummies
    beta_y, _, _, _ = np.linalg.lstsq(D, Y, rcond=None)
    Y_res = Y - D @ beta_y

    # Residualize each PC on dummies and compute partial correlation
    partial_corrs = {}
    any_sig = False
    for pc_idx in range(min(4, PC.shape[1])):
        pc_col = PC[:, pc_idx]
        beta_pc, _, _, _ = np.linalg.lstsq(D, pc_col, rcond=None)
        pc_res = pc_col - D @ beta_pc

        r, p = sp_stats.pearsonr(Y_res, pc_res)
        sig = p < 0.01
        if sig:
            any_sig = True
        partial_corrs[f'PC{pc_idx+1}'] = {
            'r': round(float(r), 4),
            'p_value': round(float(p), 6),
            'significant': sig,
        }
        print(f"  PC{pc_idx+1}: partial r={r:.4f}, p={p:.6f} {'SIG' if sig else 'NS'}")

    passed = any_sig
    print(f"\n  T4 PASS: {passed}")

    return {
        'n_folios_with_ke_ek': n,
        'min_ke_ek_threshold': MIN_KE_EK,
        'partial_correlations': partial_corrs,
        'any_significant': any_sig,
        'pass': passed,
    }


# ============================================================
# T5: ARCHETYPE-VOCABULARY CROSS-VALIDATION
# ============================================================

def run_t5(t2_results, archetype_labels, folio_list, regime_map):
    """T5: ARI between vocabulary clusters (from T2) and C1016 archetypes."""
    print("\n" + "=" * 60)
    print("T5: ARCHETYPE-VOCABULARY CROSS-VALIDATION")
    print("=" * 60)

    # Build global vocab cluster label per folio from T2 results
    # Combine REGIME + within-REGIME cluster into a global label
    vocab_labels = {}
    label_counter = 0
    regime_label_maps = {}

    for regime, rr in t2_results['regime_results'].items():
        if rr.get('skipped'):
            # Assign single cluster for skipped REGIMEs
            regime_label_maps[regime] = {}
            for f in rr.get('cluster_labels', {}):
                vocab_labels[f] = label_counter
            label_counter += 1
            continue
        for f, cl in rr.get('cluster_labels', {}).items():
            global_key = f"{regime}_c{cl}"
            if global_key not in regime_label_maps:
                regime_label_maps[global_key] = label_counter
                label_counter += 1
            vocab_labels[f] = regime_label_maps[global_key]

    # Intersect with archetypes
    common = [f for f in folio_list if f in vocab_labels and f in archetype_labels]
    n_common = len(common)
    print(f"  Folios with both vocab cluster and archetype: {n_common}")

    if n_common < 10:
        print("  TOO FEW FOLIOS — T5 INCONCLUSIVE")
        return {
            'n_common_folios': n_common,
            'ari_vocab_vs_archetype': 0,
            'pass': False,
            'note': 'insufficient overlap',
        }

    v_labels = [vocab_labels[f] for f in common]
    a_labels = [archetype_labels[f] for f in common]
    # archetype_labels might be int or str
    a_labels = [int(x) for x in a_labels]

    ari = adjusted_rand_score(v_labels, a_labels)
    print(f"  ARI (vocab vs archetype): {ari:.4f}")
    print(f"  Reference ARI (REGIME vs archetype, C1016): 0.065")

    # Permutation test
    n_exceed = 0
    for _ in range(N_PERM):
        shuf_v = list(v_labels)
        np.random.shuffle(shuf_v)
        shuf_ari = adjusted_rand_score(shuf_v, a_labels)
        if shuf_ari >= ari:
            n_exceed += 1
    p_val = (n_exceed + 1) / (N_PERM + 1)
    print(f"  Permutation p={p_val:.4f}")

    passed = ari > 0.10
    print(f"  T5 PASS: {passed} (ARI>0.10={ari>0.10})")

    return {
        'n_common_folios': n_common,
        'n_vocab_clusters': label_counter,
        'n_archetypes': len(set(a_labels)),
        'ari_vocab_vs_archetype': round(ari, 4),
        'ari_reference_regime_vs_archetype': 0.065,
        'permutation_p': round(p_val, 4),
        'pass': passed,
    }


# ============================================================
# SYNTHESIS
# ============================================================

def synthesize(t1, t2, t3, t4, t5):
    """Combine all test results into a verdict."""
    tests = {'T1': t1, 'T2': t2, 'T3': t3, 'T4': t4, 'T5': t5}
    n_pass = sum(1 for t in tests.values() if t.get('pass'))
    n_total = len(tests)

    if n_pass >= 5:
        verdict = 'APPARATUS_VOCABULARY_CONFIRMED'
    elif n_pass >= 3:
        verdict = 'APPARATUS_VOCABULARY_SUPPORTED'
    else:
        verdict = 'APPARATUS_VOCABULARY_NOT_SUPPORTED'

    summary = {}
    for name, t in tests.items():
        summary[name] = {'pass': t.get('pass', False)}

    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    for name, s in summary.items():
        print(f"  {name}: {'PASS' if s['pass'] else 'FAIL'}")
    print(f"\n  Tests passing: {n_pass}/{n_total}")
    print(f"  VERDICT: {verdict}")

    return {
        'test_summary': summary,
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    start = time.time()
    print("Phase 445: APPARATUS_VOCABULARY_CLASSIFICATION")
    print("=" * 60)

    # 1. Load external data
    regime_map = load_regime_map()
    archetype_labels = load_archetype_labels()
    print(f"REGIME map: {len(regime_map)} folios")
    print(f"Archetype labels: {len(archetype_labels)} folios")

    # 2. Extract features
    folio_pm_counts, folio_sections, folio_token_counts, folio_derived = extract_folio_data()
    print(f"Extracted: {len(folio_pm_counts)} folios")

    # 3. Filter to valid folios
    folio_list = sorted(f for f in folio_pm_counts
                        if folio_token_counts.get(f, 0) >= MIN_FOLIO_TOKENS
                        and f in regime_map)
    print(f"Folios after MIN_FOLIO_TOKENS={MIN_FOLIO_TOKENS} filter: {len(folio_list)}")

    # 4. Build and transform feature matrix
    X_raw, pm_pairs = build_feature_matrix(folio_pm_counts, folio_list)
    X_hell = hellinger_transform(X_raw)
    print(f"Feature matrix: {X_hell.shape[0]} folios x {X_hell.shape[1]} PM pairs")

    # Show regime distribution
    regime_dist = Counter(regime_map.get(f, '?') for f in folio_list)
    print(f"REGIME distribution: {dict(sorted(regime_dist.items()))}")

    # Show derived feature stats
    t_rates = [folio_derived[f]['t_rate'] for f in folio_list]
    ok_rates = [folio_derived[f]['ok_rate'] for f in folio_list]
    ee_rates = [folio_derived[f]['ee_family_rate'] for f in folio_list]
    print(f"t_rate:  mean={np.mean(t_rates):.4f}, std={np.std(t_rates):.4f}")
    print(f"ok_rate: mean={np.mean(ok_rates):.4f}, std={np.std(ok_rates):.4f}")
    print(f"ee_rate: mean={np.mean(ee_rates):.4f}, std={np.std(ee_rates):.4f}")

    # 5. Run tests
    t1 = run_t1(X_hell, folio_list, regime_map, folio_sections)
    t2 = run_t2(X_hell, folio_list, regime_map, pm_pairs)
    t3 = run_t3(folio_derived, folio_list, regime_map)
    t4 = run_t4(folio_derived, folio_list, regime_map, folio_sections, t1)
    t5 = run_t5(t2, archetype_labels, folio_list, regime_map)
    synthesis = synthesize(t1, t2, t3, t4, t5)

    # 6. Save results
    results = {
        '_metadata': {
            'phase': 'APPARATUS_VOCABULARY_CLASSIFICATION',
            'phase_number': 445,
            'n_folios': len(folio_list),
            'n_pm_pairs': len(pm_pairs),
            'min_folio_tokens': MIN_FOLIO_TOKENS,
            'normalization': 'hellinger',
            'n_permutations': N_PERM,
            'depends_on': ['C663', 'C1016', 'C1153', 'C1226'],
        },
        't1_regime_residual_pca': t1,
        't2_within_regime_clustering': t2,
        't3_triangle_discrimination': t3,
        't4_ke_ek_apparatus_discriminator': t4,
        't5_archetype_cross_validation': t5,
        'synthesis': synthesis,
    }

    output_path = RESULTS_DIR / 'apparatus_vocabulary_classification.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - start
    print(f"\nResults saved to {output_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
