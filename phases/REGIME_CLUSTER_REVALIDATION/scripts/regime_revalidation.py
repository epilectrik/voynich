#!/usr/bin/env python3
"""
Phase 590: REGIME_CLUSTER_REVALIDATION

Revalidates C179 (4-REGIME partition, silhouette 0.23) with expanded features,
multiple clustering methods, and rigorous controls including within-Herbal
substructure testing and functional validation.

Expected constraints: C1712-C1715
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / 'phases' / 'REGIME_CLUSTER_REVALIDATION' / 'results'

# Known HEAD atoms (first character of MIDDLE for kernel classification)
HEAD_ATOMS = {'k', 'h', 'e'}

# Known LINK pattern: bare 'l' MIDDLE (no prefix, no suffix)
# FQ tokens (high-frequency instruction classes)
FQ_TOKENS = {
    'daiin', 'ol', 'chedy', 'shedy', 'qokeedy', 'qokedy',
    'chey', 'shey', 'qokeey', 'okeedy', 'okeey',
}


def build_feature_matrix():
    """Build 22-feature matrix for all Currier B folios from transcript."""
    tx = Transcript()
    morph = Morphology()

    # Collect per-folio raw data
    folio_data = defaultdict(lambda: {
        'tokens': [],         # list of (word, morph_result)
        'lines': set(),       # distinct line numbers
        'line_tokens': defaultdict(list),  # line -> [tokens]
        'sections': [],       # section codes per token
    })

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        # Skip labels
        if token.placement and token.placement.startswith('L'):
            continue

        f = token.folio
        m = morph.extract(word)
        fd = folio_data[f]
        fd['tokens'].append((word, m))
        fd['lines'].add(token.line)
        fd['line_tokens'][token.line].append((word, m))
        if token.section:
            fd['sections'].append(token.section)

    # Build feature vectors
    feature_names = [
        # HEAD domain (3)
        'k_frac', 'e_frac', 'headless_frac',
        # PREFIX composition (6)
        'qo_frac', 'chsh_frac', 'bare_prefix_frac', 'da_frac', 'ok_frac', 'ot_frac',
        # Suffix/closure (4)
        'suffix_rate', 'y_suffix_rate', 'dy_suffix_rate', 'naked_rate',
        # Line structure (3)
        'mean_line_length', 'hapax_rate', 'log_token_count',
        # Dynamics (3)
        'link_rate', 'fq_rate', 'head_self_transition_rate',
        # Vocabulary (3)
        'vocab_richness', 'mean_middle_length', 'compound_rate',
    ]

    folios = []
    sections = {}  # folio -> majority section code
    X_rows = []

    for folio in sorted(folio_data.keys()):
        fd = folio_data[folio]
        n = len(fd['tokens'])
        if n < 30:
            continue

        folios.append(folio)

        # Determine section (majority vote from tokens)
        if fd['sections']:
            sec_counts = Counter(fd['sections'])
            sections[folio] = sec_counts.most_common(1)[0][0]
        else:
            sections[folio] = '?'

        # --- HEAD domain ---
        k_count = e_count = headless_count = 0
        middles_all = []
        for word, m in fd['tokens']:
            mid = m.middle or ''
            if mid:
                middles_all.append(mid)
                head = mid[0] if mid else ''
                if head == 'k':
                    k_count += 1
                elif head == 'e':
                    e_count += 1
                elif head not in HEAD_ATOMS:
                    headless_count += 1
            else:
                headless_count += 1

        k_frac = k_count / n
        e_frac = e_count / n
        headless_frac = headless_count / n

        # --- PREFIX composition ---
        qo_count = chsh_count = bare_prefix_count = da_count = ok_count = ot_count = 0
        for word, m in fd['tokens']:
            pfx = m.prefix or ''
            if not pfx:
                bare_prefix_count += 1
            elif pfx == 'qo':
                qo_count += 1
            elif pfx in ('ch', 'sh'):
                chsh_count += 1
            elif pfx == 'da':
                da_count += 1
            elif pfx == 'ok':
                ok_count += 1
            elif pfx in ('ot', 'ct'):
                ot_count += 1

        qo_frac = qo_count / n
        chsh_frac = chsh_count / n
        bare_prefix_frac = bare_prefix_count / n
        da_frac = da_count / n
        ok_frac = ok_count / n
        ot_frac = ot_count / n

        # --- Suffix/closure ---
        suffix_count = y_suffix_count = dy_suffix_count = naked_count = 0
        for word, m in fd['tokens']:
            sfx = m.suffix or ''
            pfx = m.prefix or ''
            mid = m.middle or ''
            if sfx:
                suffix_count += 1
                if sfx.endswith('y'):
                    y_suffix_count += 1
                if sfx == 'dy':
                    dy_suffix_count += 1
            if not pfx and not sfx and mid:
                naked_count += 1

        suffix_rate = suffix_count / n
        y_suffix_rate = y_suffix_count / n
        dy_suffix_rate = dy_suffix_count / n
        naked_rate = naked_count / n

        # --- Line structure ---
        n_lines = len(fd['lines'])
        mean_line_length = n / max(n_lines, 1)
        log_token_count = np.log(n)

        # Hapax rate: MIDDLEs appearing exactly once in this folio
        mid_counts = Counter(middles_all)
        hapax_count = sum(1 for c in mid_counts.values() if c == 1)
        hapax_rate = hapax_count / max(len(middles_all), 1)

        # --- Dynamics ---
        link_count = sum(1 for word, m in fd['tokens']
                         if (m.middle or '') == 'l' and not m.prefix and not m.suffix)
        link_rate = link_count / n

        fq_count = sum(1 for word, m in fd['tokens'] if word in FQ_TOKENS)
        fq_rate = fq_count / n

        # HEAD self-transition rate: consecutive tokens in same line with same HEAD
        total_pairs = 0
        same_head_pairs = 0
        for line, tokens in fd['line_tokens'].items():
            for i in range(len(tokens) - 1):
                mid_a = tokens[i][1].middle or ''
                mid_b = tokens[i + 1][1].middle or ''
                head_a = mid_a[0] if mid_a and mid_a[0] in HEAD_ATOMS else 'X'
                head_b = mid_b[0] if mid_b and mid_b[0] in HEAD_ATOMS else 'X'
                total_pairs += 1
                if head_a == head_b and head_a != 'X':
                    same_head_pairs += 1
        head_self_transition_rate = same_head_pairs / max(total_pairs, 1)

        # --- Vocabulary ---
        unique_middles = set(middles_all)
        vocab_richness = len(unique_middles) / max(n, 1)

        mid_lengths = [len(m) for m in middles_all if m]
        mean_middle_length = np.mean(mid_lengths) if mid_lengths else 0.0

        # Compound rate: MIDDLEs with 4+ characters (rough proxy for compound)
        compound_count = sum(1 for m in middles_all if len(m) >= 4)
        compound_rate = compound_count / max(len(middles_all), 1)

        # --- Build row ---
        row = [
            k_frac, e_frac, headless_frac,
            qo_frac, chsh_frac, bare_prefix_frac, da_frac, ok_frac, ot_frac,
            suffix_rate, y_suffix_rate, dy_suffix_rate, naked_rate,
            mean_line_length, hapax_rate, log_token_count,
            link_rate, fq_rate, head_self_transition_rate,
            vocab_richness, mean_middle_length, compound_rate,
        ]
        X_rows.append(row)

    X = np.array(X_rows)
    return X, folios, sections, feature_names


def gap_statistic(X, k_range, B=500, random_state=42):
    """Compute gap statistic (Tibshirani et al. 2001)."""
    from sklearn.cluster import KMeans

    rng = np.random.RandomState(random_state)
    n, d = X.shape

    # Reference: uniform distribution over bounding box of X
    x_min = X.min(axis=0)
    x_max = X.max(axis=0)

    def log_Wk(X_data, k):
        if k == 1:
            # W = sum of squared distances to centroid
            centroid = X_data.mean(axis=0)
            return np.log(np.sum((X_data - centroid) ** 2))
        km = KMeans(n_clusters=k, n_init=10, random_state=42, max_iter=300)
        km.fit(X_data)
        # W = sum of within-cluster sum of squares
        W = km.inertia_
        return np.log(max(W, 1e-10))

    gaps = []
    s_values = []

    for k in k_range:
        log_wk_obs = log_Wk(X, k)

        # Generate B reference datasets
        log_wk_refs = []
        for _ in range(B):
            X_ref = rng.uniform(x_min, x_max, size=(n, d))
            log_wk_refs.append(log_Wk(X_ref, k))

        log_wk_refs = np.array(log_wk_refs)
        gap = log_wk_refs.mean() - log_wk_obs
        sdk = np.std(log_wk_refs) * np.sqrt(1 + 1 / B)

        gaps.append(gap)
        s_values.append(sdk)

    # Tibshirani criterion: smallest k where Gap(k) >= Gap(k+1) - s(k+1)
    k_list = list(k_range)
    optimal_k = k_list[-1]  # default to last
    for i in range(len(k_list) - 1):
        if gaps[i] >= gaps[i + 1] - s_values[i + 1]:
            optimal_k = k_list[i]
            break

    return {
        'gaps': {k: round(g, 4) for k, g in zip(k_list, gaps)},
        's_values': {k: round(s, 4) for k, s in zip(k_list, s_values)},
        'optimal_k': optimal_k,
    }


def run_clustering_sweep(X, k_range, feature_names):
    """Run K-Means, Ward, GMM for each k. Return results dict."""
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.mixture import GaussianMixture
    from sklearn.metrics import (
        silhouette_score, calinski_harabasz_score, davies_bouldin_score
    )

    results = {}

    for method_name, ClusterClass in [
        ('kmeans', None), ('ward', None), ('gmm', None)
    ]:
        method_results = {}
        for k in k_range:
            if method_name == 'kmeans':
                model = KMeans(n_clusters=k, n_init=100, random_state=42, max_iter=300)
                labels = model.fit_predict(X)
            elif method_name == 'ward':
                model = AgglomerativeClustering(n_clusters=k, linkage='ward')
                labels = model.fit_predict(X)
            elif method_name == 'gmm':
                model = GaussianMixture(
                    n_components=k, covariance_type='diag',
                    n_init=10, max_iter=300, random_state=42,
                )
                labels = model.fit_predict(X)

            n_unique = len(set(labels))
            if n_unique < 2:
                sil = ch = db = float('nan')
            else:
                sil = silhouette_score(X, labels)
                ch = calinski_harabasz_score(X, labels)
                db = davies_bouldin_score(X, labels)

            entry = {
                'labels': labels.tolist(),
                'silhouette': round(sil, 4) if not np.isnan(sil) else None,
                'calinski_harabasz': round(ch, 1) if not np.isnan(ch) else None,
                'davies_bouldin': round(db, 4) if not np.isnan(db) else None,
                'sizes': np.bincount(labels).tolist(),
            }

            if method_name == 'gmm':
                entry['bic'] = round(float(model.bic(X)), 1)
                entry['aic'] = round(float(model.aic(X)), 1)

            method_results[k] = entry

        results[method_name] = method_results

    return results


def bootstrap_stability(X, k, n_bootstrap=200, random_state=42):
    """Bootstrap stability test: fraction of pairwise agreements."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.RandomState(random_state)
    n = X.shape[0]

    reference = KMeans(n_clusters=k, n_init=100, random_state=42, max_iter=300)
    ref_labels = reference.fit_predict(X)

    ari_scores = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        X_boot = X[idx]
        boot_model = KMeans(n_clusters=k, n_init=10, random_state=rng.randint(1e6), max_iter=300)
        boot_labels = boot_model.fit_predict(X_boot)

        # Compare on unique indices only
        unique_idx = list(set(idx))
        ref_sub = ref_labels[unique_idx]
        boot_sub = boot_labels[[list(idx).index(i) for i in unique_idx]]

        if len(set(ref_sub)) >= 2 and len(set(boot_sub)) >= 2:
            ari = adjusted_rand_score(ref_sub, boot_sub)
            ari_scores.append(ari)

    return {
        'mean_ari': round(np.mean(ari_scores), 4) if ari_scores else None,
        'std_ari': round(np.std(ari_scores), 4) if ari_scores else None,
        'n_valid': len(ari_scores),
    }


def within_herbal_test(X, folios, sections, k_range_inner):
    """PRIMARY H1c test: cluster within Herbal folios only."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    herbal_mask = [sections.get(f, '?') == 'H' for f in folios]
    herbal_idx = [i for i, m in enumerate(herbal_mask) if m]

    if len(herbal_idx) < 10:
        return {'error': f'Too few Herbal folios: {len(herbal_idx)}'}

    X_herbal = X[herbal_idx]
    # Re-standardize within Herbal
    scaler = StandardScaler()
    X_h_scaled = scaler.fit_transform(X_herbal)

    results = {}
    for k in k_range_inner:
        if k >= len(herbal_idx):
            continue
        km = KMeans(n_clusters=k, n_init=100, random_state=42, max_iter=300)
        labels = km.fit_predict(X_h_scaled)
        n_unique = len(set(labels))
        if n_unique < 2:
            sil = float('nan')
        else:
            sil = silhouette_score(X_h_scaled, labels)
        results[k] = {
            'silhouette': round(sil, 4) if not np.isnan(sil) else None,
            'sizes': np.bincount(labels).tolist(),
        }

    best_k = max(results, key=lambda k: results[k]['silhouette'] or -999)
    return {
        'n_herbal': len(herbal_idx),
        'herbal_folios': [folios[i] for i in herbal_idx],
        'results_by_k': results,
        'best_k': best_k,
        'best_silhouette': results[best_k]['silhouette'],
    }


def section_residualization_test(X, folios, sections, k_range):
    """SECONDARY H1c test: regress out section, cluster residuals."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    # Build section dummies
    unique_sections = sorted(set(sections[f] for f in folios if sections.get(f, '?') != '?'))
    if len(unique_sections) < 2:
        return {'error': 'Fewer than 2 sections'}

    n = X.shape[0]
    d_sec = len(unique_sections) - 1  # drop one for reference
    S = np.zeros((n, d_sec))
    for i, f in enumerate(folios):
        sec = sections.get(f, '?')
        for j, s in enumerate(unique_sections[1:]):  # skip first as reference
            if sec == s:
                S[i, j] = 1.0

    # OLS: X_residual = X - S @ (S^T S)^{-1} S^T X
    StS_inv = np.linalg.pinv(S.T @ S)
    projection = S @ StS_inv @ S.T
    X_resid = X - projection @ X

    # Re-standardize residuals
    scaler = StandardScaler()
    X_resid_scaled = scaler.fit_transform(X_resid)

    results = {}
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=100, random_state=42, max_iter=300)
        labels = km.fit_predict(X_resid_scaled)
        n_unique = len(set(labels))
        if n_unique < 2:
            sil = float('nan')
        else:
            sil = silhouette_score(X_resid_scaled, labels)
        results[k] = {
            'silhouette': round(sil, 4) if not np.isnan(sil) else None,
            'sizes': np.bincount(labels).tolist(),
        }

    best_k = max(results, key=lambda k: results[k]['silhouette'] or -999)
    return {
        'n_sections': len(unique_sections),
        'section_dummies': d_sec,
        'results_by_k': results,
        'best_k': best_k,
        'best_silhouette': results[best_k]['silhouette'],
    }


def random_null_test(X, k_range, n_perms=100, random_state=42):
    """Control C4: permute each column independently, compute silhouettes."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    rng = np.random.RandomState(random_state)
    n, d = X.shape

    null_sils = {k: [] for k in k_range}
    for _ in range(n_perms):
        X_perm = X.copy()
        for col in range(d):
            rng.shuffle(X_perm[:, col])

        for k in k_range:
            km = KMeans(n_clusters=k, n_init=10, random_state=rng.randint(1e6), max_iter=300)
            labels = km.fit_predict(X_perm)
            if len(set(labels)) >= 2:
                sil = silhouette_score(X_perm, labels)
                null_sils[k].append(sil)

    return {
        k: {
            'mean_sil': round(np.mean(v), 4) if v else None,
            'std_sil': round(np.std(v), 4) if v else None,
            'p95_sil': round(np.percentile(v, 95), 4) if v else None,
        }
        for k, v in null_sils.items()
    }


def functional_validation(X, folios, sections, feature_names):
    """Within-Herbal functional test: do REGIME subgroups predict dynamics?"""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    herbal_mask = [sections.get(f, '?') == 'H' for f in folios]
    herbal_idx = [i for i, m in enumerate(herbal_mask) if m]

    if len(herbal_idx) < 10:
        return {'error': 'Too few Herbal folios'}

    X_herbal = X[herbal_idx]
    scaler = StandardScaler()
    X_h_scaled = scaler.fit_transform(X_herbal)

    # Cluster Herbal folios into k=2,3,4
    results = {}
    for k in [2, 3, 4]:
        if k >= len(herbal_idx):
            continue
        km = KMeans(n_clusters=k, n_init=100, random_state=42, max_iter=300)
        labels = km.fit_predict(X_h_scaled)

        # Check if HEAD self-transition rate differs across clusters
        hst_idx = feature_names.index('head_self_transition_rate')
        hst_values = X_herbal[:, hst_idx]

        cluster_hst = {}
        for c in range(k):
            mask = labels == c
            vals = hst_values[mask]
            cluster_hst[c] = {
                'mean': round(float(vals.mean()), 4),
                'std': round(float(vals.std()), 4),
                'n': int(mask.sum()),
            }

        # One-way ANOVA F-test (manual)
        grand_mean = hst_values.mean()
        ss_between = sum(
            cluster_hst[c]['n'] * (cluster_hst[c]['mean'] - grand_mean) ** 2
            for c in range(k)
        )
        ss_within = sum(
            np.sum((hst_values[labels == c] - cluster_hst[c]['mean']) ** 2)
            for c in range(k)
        )
        df_between = k - 1
        df_within = len(herbal_idx) - k

        if df_within > 0 and ss_within > 0:
            f_stat = (ss_between / df_between) / (ss_within / df_within)
        else:
            f_stat = 0.0

        # Also check vocab_richness differentiation
        vr_idx = feature_names.index('vocab_richness')
        vr_values = X_herbal[:, vr_idx]
        cluster_vr = {}
        for c in range(k):
            mask = labels == c
            vals = vr_values[mask]
            cluster_vr[c] = {
                'mean': round(float(vals.mean()), 4),
                'std': round(float(vals.std()), 4),
                'n': int(mask.sum()),
            }

        results[k] = {
            'head_self_transition': {
                'cluster_means': cluster_hst,
                'f_statistic': round(f_stat, 3),
                'df_between': df_between,
                'df_within': df_within,
            },
            'vocab_richness': {
                'cluster_means': cluster_vr,
            },
        }

    return results


def reproduce_v2(folios):
    """Control C0: load existing v2 REGIME assignments for comparison."""
    v2_path = ROOT / 'data' / 'regime_folio_mapping.json'
    if not v2_path.exists():
        return {'error': 'v2 mapping not found'}

    with open(v2_path, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)

    v2_assignments = {}
    for folio in folios:
        if folio in v2_data.get('regime_assignments', {}):
            v2_assignments[folio] = v2_data['regime_assignments'][folio]['regime']

    return {
        'n_matched': len(v2_assignments),
        'assignments': v2_assignments,
        'v2_silhouette': v2_data['_metadata']['silhouette'],
        'v2_bic': v2_data['_metadata']['bic'],
        'v2_k': v2_data['_metadata']['n_clusters'],
    }


def main():
    print("=" * 70)
    print("PHASE 590: REGIME_CLUSTER_REVALIDATION")
    print("=" * 70)

    # ================================================================
    # 1. BUILD FEATURE MATRIX
    # ================================================================
    print("\n[1] Building feature matrix...")
    X_raw, folios, sections, feature_names = build_feature_matrix()
    n, d = X_raw.shape
    print(f"  Folios: {n}, Features: {d}")
    print(f"  Feature names: {feature_names}")

    # Section distribution
    sec_counts = Counter(sections[f] for f in folios)
    print(f"  Section distribution: {dict(sec_counts)}")

    # Feature summary (raw)
    print(f"\n  Feature summary (raw):")
    for j, feat in enumerate(feature_names):
        vals = X_raw[:, j]
        print(f"    {feat:30s}: mean={vals.mean():.4f}  std={vals.std():.4f}  "
              f"min={vals.min():.4f}  max={vals.max():.4f}")

    # ================================================================
    # 2. PCA REDUCTION
    # ================================================================
    print("\n[2] PCA reduction...")
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    pca = PCA(n_components=0.95, random_state=42)  # 95% variance
    X_pca = pca.fit_transform(X_scaled)
    n_pcs = X_pca.shape[1]
    cum_var = np.cumsum(pca.explained_variance_ratio_)

    print(f"  Components retained: {n_pcs} (95% variance threshold)")
    pca_info = {}
    for pc_i in range(n_pcs):
        var = pca.explained_variance_ratio_[pc_i]
        cum = cum_var[pc_i]
        loadings = pca.components_[pc_i]
        top_idx = np.argsort(np.abs(loadings))[::-1][:3]
        top_loadings = {feature_names[j]: round(float(loadings[j]), 3) for j in top_idx}
        print(f"    PC{pc_i+1}: {var:.3f} (cum: {cum:.3f}) — {top_loadings}")
        pca_info[f'PC{pc_i+1}'] = {
            'variance_explained': round(var, 4),
            'cumulative': round(cum, 4),
            'top_loadings': top_loadings,
        }

    # ================================================================
    # 3. CONTROL C0: REPRODUCE v2
    # ================================================================
    print("\n[3] Control C0: Reproduce v2 REGIME assignments...")
    v2_info = reproduce_v2(folios)
    print(f"  v2 matched folios: {v2_info.get('n_matched', 0)}")
    print(f"  v2 silhouette: {v2_info.get('v2_silhouette')}")
    print(f"  v2 k: {v2_info.get('v2_k')}")

    # ================================================================
    # 4. FULL CLUSTERING SWEEP
    # ================================================================
    print("\n[4] Clustering sweep (K-Means, Ward, GMM) k=2..8...")
    k_range = range(2, 9)
    sweep_results = run_clustering_sweep(X_pca, k_range, feature_names)

    # Print summary
    for method in ['kmeans', 'ward', 'gmm']:
        print(f"\n  {method.upper()}:")
        for k in k_range:
            r = sweep_results[method][k]
            bic_str = f"  BIC={r['bic']}" if 'bic' in r else ''
            print(f"    k={k}: sil={r['silhouette']}  CH={r['calinski_harabasz']}  "
                  f"DB={r['davies_bouldin']}{bic_str}  sizes={r['sizes']}")

    # ================================================================
    # 5. CONSENSUS K
    # ================================================================
    print("\n[5] Consensus k determination...")

    # Best k by silhouette for each method
    best_k_by_method = {}
    for method in ['kmeans', 'ward', 'gmm']:
        best_k = max(k_range, key=lambda k: sweep_results[method][k]['silhouette'] or -999)
        best_sil = sweep_results[method][best_k]['silhouette']
        best_k_by_method[method] = {'k': best_k, 'silhouette': best_sil}
        print(f"  {method}: best k={best_k} (sil={best_sil})")

    # Modal k across methods
    k_votes = [best_k_by_method[m]['k'] for m in ['kmeans', 'ward', 'gmm']]
    k_counter = Counter(k_votes)
    consensus_k = k_counter.most_common(1)[0][0]
    n_agree = k_counter.most_common(1)[0][1]
    print(f"  Consensus k: {consensus_k} ({n_agree}/3 methods agree)")

    # Mean silhouette at consensus k
    mean_sil_at_consensus = np.mean([
        sweep_results[m][consensus_k]['silhouette'] or 0
        for m in ['kmeans', 'ward', 'gmm']
    ])
    print(f"  Mean silhouette at k={consensus_k}: {mean_sil_at_consensus:.4f}")

    # ================================================================
    # 6. GAP STATISTIC
    # ================================================================
    print("\n[6] Gap statistic (B=500)...")
    gap_result = gap_statistic(X_pca, k_range=range(1, 9), B=500)
    print(f"  Gap optimal k: {gap_result['optimal_k']}")
    for k in range(1, 9):
        g = gap_result['gaps'].get(k, '?')
        s = gap_result['s_values'].get(k, '?')
        print(f"    k={k}: gap={g}  s={s}")

    # ================================================================
    # 7. WITHIN-HERBAL TEST (PRIMARY H1c)
    # ================================================================
    print("\n[7] Within-Herbal clustering (primary H1c test)...")
    herbal_result = within_herbal_test(X_scaled, folios, sections, range(2, 7))
    if 'error' not in herbal_result:
        print(f"  Herbal folios: {herbal_result['n_herbal']}")
        print(f"  Best k within Herbal: {herbal_result['best_k']} "
              f"(sil={herbal_result['best_silhouette']})")
        for k, r in herbal_result['results_by_k'].items():
            print(f"    k={k}: sil={r['silhouette']}  sizes={r['sizes']}")
    else:
        print(f"  ERROR: {herbal_result['error']}")

    # ================================================================
    # 8. SECTION RESIDUALIZATION (SECONDARY H1c)
    # ================================================================
    print("\n[8] Section residualization (secondary H1c test)...")
    resid_result = section_residualization_test(X_scaled, folios, sections, k_range)
    if 'error' not in resid_result:
        print(f"  Sections: {resid_result['n_sections']}, dummies: {resid_result['section_dummies']}")
        print(f"  Best k on residuals: {resid_result['best_k']} "
              f"(sil={resid_result['best_silhouette']})")
        for k in k_range:
            r = resid_result['results_by_k'][k]
            print(f"    k={k}: sil={r['silhouette']}  sizes={r['sizes']}")
    else:
        print(f"  ERROR: {resid_result['error']}")

    # ================================================================
    # 9. RANDOM NULL
    # ================================================================
    print("\n[9] Random null (100 permutations)...")
    null_result = random_null_test(X_pca, k_range, n_perms=100)
    for k in k_range:
        r = null_result[k]
        print(f"    k={k}: null_mean_sil={r['mean_sil']}  null_p95={r['p95_sil']}")

    # ================================================================
    # 10. BOOTSTRAP STABILITY
    # ================================================================
    print(f"\n[10] Bootstrap stability (200 resamples) at k={consensus_k}...")
    boot_result = bootstrap_stability(X_pca, consensus_k, n_bootstrap=200)
    print(f"  ARI: {boot_result['mean_ari']} ± {boot_result['std_ari']} "
          f"({boot_result['n_valid']} valid)")

    # Also test k=4 if consensus != 4
    boot_k4 = None
    if consensus_k != 4:
        print(f"  Also testing k=4 (original C179)...")
        boot_k4 = bootstrap_stability(X_pca, 4, n_bootstrap=200)
        print(f"  k=4 ARI: {boot_k4['mean_ari']} ± {boot_k4['std_ari']}")

    # ================================================================
    # 11. FUNCTIONAL VALIDATION
    # ================================================================
    print("\n[11] Functional validation (within-Herbal dynamics)...")
    func_result = functional_validation(X_raw, folios, sections, feature_names)
    for k, r in func_result.items():
        hst = r['head_self_transition']
        print(f"  k={k}: HST F-stat={hst['f_statistic']} "
              f"(df={hst['df_between']},{hst['df_within']})")
        for c, stats in hst['cluster_means'].items():
            print(f"    Cluster {c}: HST mean={stats['mean']}, n={stats['n']}")

    # ================================================================
    # 12. SECTION CROSS-TABULATION AT CONSENSUS K
    # ================================================================
    print(f"\n[12] Section cross-tabulation at k={consensus_k}...")

    # Get labels at consensus k from K-Means
    consensus_labels = np.array(sweep_results['kmeans'][consensus_k]['labels'])
    cross_tab = defaultdict(lambda: defaultdict(int))
    for i, f in enumerate(folios):
        sec = sections.get(f, '?')
        cluster = int(consensus_labels[i])
        cross_tab[cluster][sec] += 1

    all_secs = sorted(set(sections[f] for f in folios))
    header = f"{'Cluster':>10}" + ''.join(f"{s:>6}" for s in all_secs) + f"{'Total':>8}"
    print(f"  {header}")
    for c in sorted(cross_tab.keys()):
        row = f"  {'C' + str(c):>10}"
        total = 0
        for s in all_secs:
            count = cross_tab[c][s]
            total += count
            row += f"{count:>6}"
        row += f"{total:>8}"
        print(row)

    # ================================================================
    # 13. V2 COMPARISON
    # ================================================================
    print(f"\n[13] Comparison with v2 REGIME assignments...")
    if v2_info.get('assignments'):
        from sklearn.metrics import adjusted_rand_score
        v2_labels = []
        new_labels = []
        regime_to_int = {}
        for i, f in enumerate(folios):
            if f in v2_info['assignments']:
                regime = v2_info['assignments'][f]
                if regime not in regime_to_int:
                    regime_to_int[regime] = len(regime_to_int)
                v2_labels.append(regime_to_int[regime])
                new_labels.append(int(consensus_labels[i]))

        if len(set(v2_labels)) >= 2 and len(set(new_labels)) >= 2:
            ari = adjusted_rand_score(v2_labels, new_labels)
            print(f"  ARI(v2, new k={consensus_k}): {ari:.4f}")
        else:
            ari = None
            print(f"  Cannot compute ARI (insufficient cluster diversity)")
    else:
        ari = None

    # ================================================================
    # 14. DECISION LOGIC
    # ================================================================
    print("\n" + "=" * 70)
    print("DECISION LOGIC")
    print("=" * 70)

    gap_k = gap_result['optimal_k']
    all_sils = [
        sweep_results[m][consensus_k]['silhouette'] or 0
        for m in ['kmeans', 'ward', 'gmm']
    ]
    max_sil = max(all_sils)

    herbal_sil = herbal_result.get('best_silhouette', 0) or 0
    resid_sil = resid_result.get('best_silhouette', 0) or 0

    print(f"  Gap statistic optimal k: {gap_k}")
    print(f"  Consensus k: {consensus_k} ({n_agree}/3)")
    print(f"  Mean silhouette at consensus k: {mean_sil_at_consensus:.4f}")
    print(f"  Within-Herbal best silhouette: {herbal_sil}")
    print(f"  Section-residualized best silhouette: {resid_sil}")

    verdict = None
    if gap_k == 1:
        verdict = 'H0'
        verdict_text = f'CONTINUOUS — gap statistic selects k=1 (DECISIVE). C179 FALSIFIED.'
    elif max_sil < 0.15:
        verdict = 'H0'
        verdict_text = f'CONTINUOUS — all silhouettes < 0.15 (max={max_sil:.4f}). C179 FALSIFIED.'
    elif herbal_sil < 0.15 and resid_sil < 0.15:
        verdict = 'H1c'
        verdict_text = (f'SECTION ALIAS — within-Herbal sil={herbal_sil:.4f} < 0.15 AND '
                        f'residualized sil={resid_sil:.4f} < 0.15. REGIME = section alias.')
    elif consensus_k == 4 and mean_sil_at_consensus >= 0.20:
        verdict = 'H1a'
        verdict_text = (f'k=4 STRENGTHENED — consensus k=4, mean sil={mean_sil_at_consensus:.4f} >= 0.20. '
                        f'C179 validated.')
    elif consensus_k == 4 and mean_sil_at_consensus < 0.20:
        verdict = 'H1b'
        verdict_text = (f'k=4 WEAK — consensus k=4, mean sil={mean_sil_at_consensus:.4f} < 0.20. '
                        f'C179 retained with confidence note.')
    elif consensus_k != 4:
        verdict = 'H1d'
        verdict_text = (f'NEW K — consensus k={consensus_k} (not 4), '
                        f'mean sil={mean_sil_at_consensus:.4f}. C179 MODIFIED.')
    else:
        verdict = 'AMBIGUOUS'
        verdict_text = 'No clear verdict from decision logic.'

    print(f"\n  VERDICT: {verdict}")
    print(f"  {verdict_text}")

    # ================================================================
    # 15. SAVE RESULTS
    # ================================================================
    print("\n[15] Saving results...")

    # Clean up results for JSON serialization
    sweep_json = {}
    for method in ['kmeans', 'ward', 'gmm']:
        sweep_json[method] = {}
        for k in k_range:
            r = sweep_results[method][k].copy()
            r.pop('labels', None)  # Don't save full label arrays (save space)
            sweep_json[method][str(k)] = r

    output = {
        '_metadata': {
            'phase': 590,
            'title': 'REGIME_CLUSTER_REVALIDATION',
            'n_folios': n,
            'n_features': d,
            'n_pcs': n_pcs,
            'feature_names': feature_names,
        },
        'verdict': {
            'hypothesis': verdict,
            'text': verdict_text,
            'consensus_k': consensus_k,
            'n_methods_agree': n_agree,
            'mean_silhouette': round(mean_sil_at_consensus, 4),
        },
        'pca': pca_info,
        'clustering_sweep': sweep_json,
        'gap_statistic': gap_result,
        'best_k_by_method': {
            m: {'k': v['k'], 'silhouette': v['silhouette']}
            for m, v in best_k_by_method.items()
        },
        'within_herbal': herbal_result if 'error' not in herbal_result else {'error': herbal_result['error']},
        'section_residualized': resid_result if 'error' not in resid_result else {'error': resid_result['error']},
        'random_null': null_result,
        'bootstrap_stability': {
            f'k={consensus_k}': boot_result,
            **(({'k=4': boot_k4} if boot_k4 else {})),
        },
        'functional_validation': {str(k): v for k, v in func_result.items()},
        'v2_comparison': {
            'n_matched': v2_info.get('n_matched', 0),
            'v2_silhouette': v2_info.get('v2_silhouette'),
            'v2_k': v2_info.get('v2_k'),
            'ari_with_new': round(ari, 4) if ari is not None else None,
        },
        'section_distribution': dict(sec_counts),
        'section_cross_tab': {
            str(c): dict(cross_tab[c]) for c in sorted(cross_tab.keys())
        },
    }

    out_path = OUTPUT_DIR / 'regime_revalidation_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"  Saved: {out_path}")

    # ================================================================
    # SUMMARY
    # ================================================================
    print(f"\n{'=' * 70}")
    print(f"PHASE 590 COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Features: {d} ({n_pcs} PCs)")
    print(f"  Folios: {n}")
    print(f"  Consensus k: {consensus_k} ({n_agree}/3 methods)")
    print(f"  Mean silhouette: {mean_sil_at_consensus:.4f}")
    print(f"  Gap statistic k: {gap_k}")
    print(f"  Within-Herbal sil: {herbal_sil}")
    print(f"  Section-residualized sil: {resid_sil}")
    print(f"  Bootstrap ARI: {boot_result['mean_ari']}")
    print(f"  VERDICT: {verdict} — {verdict_text}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
