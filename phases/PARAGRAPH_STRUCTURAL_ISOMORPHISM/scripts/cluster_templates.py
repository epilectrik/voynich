"""
Phase 624: PARAGRAPH_STRUCTURAL_ISOMORPHISM -- Script 2: Template Clustering + Null Models

Clusters paragraph arc signatures to discover discrete structural templates,
tests against five null models, checks for section/regime/length confounds,
and compares with C853 paragraph profiles.

Input:  phases/PARAGRAPH_STRUCTURAL_ISOMORPHISM/results/arc_signatures.json
Output: phases/PARAGRAPH_STRUCTURAL_ISOMORPHISM/results/clustering_results.json
"""

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

# Import shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.PARAGRAPH_STRUCTURAL_ISOMORPHISM.scripts.shared_624 import (
    build_corpus,
    extract_arc_signature,
    _bin_features,
    ward_linkage,
    cut_dendrogram,
    silhouette_score,
    calinski_harabasz,
    gap_statistic,
    kmeans,
    adjusted_rand_index,
    cosine_similarity,
    z_normalize,
    pca_reduce,
    section_residualize,
    round_floats,
    RESULTS_DIR,
    RNG,
    N_PERM,
    ARC_FEATURE_NAMES,
    BIN_NAMES,
    MIN_BODY_LINES,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
K_RANGE = list(range(2, 13))  # k = 2..12


# ============================================================
# Statistical helpers
# ============================================================

def _chi_squared_contingency(table):
    """
    Chi-squared test on a contingency table (dict of dicts).

    Returns (chi2, dof, cramers_v, table_as_dict).
    """
    row_keys = sorted(table.keys())
    col_keys = sorted(set(c for row in table.values() for c in row.keys()))

    if not row_keys or not col_keys:
        return 0.0, 0, 0.0, {}

    n_rows = len(row_keys)
    n_cols = len(col_keys)

    # Build matrix
    obs = []
    for r in row_keys:
        row = []
        for c in col_keys:
            row.append(table[r].get(c, 0))
        obs.append(row)

    # Row and column totals
    row_totals = [sum(row) for row in obs]
    col_totals = [sum(obs[i][j] for i in range(n_rows)) for j in range(n_cols)]
    grand_total = sum(row_totals)

    if grand_total == 0:
        return 0.0, 0, 0.0, {}

    # Expected values and chi-squared
    chi2 = 0.0
    for i in range(n_rows):
        for j in range(n_cols):
            expected = row_totals[i] * col_totals[j] / grand_total
            if expected > 0:
                chi2 += (obs[i][j] - expected) ** 2 / expected

    dof = (n_rows - 1) * (n_cols - 1)
    min_dim = min(n_rows - 1, n_cols - 1)
    cramers_v = math.sqrt(chi2 / (grand_total * min_dim)) if min_dim > 0 and grand_total > 0 else 0.0

    # Table as dict for JSON
    table_out = {}
    for i, r in enumerate(row_keys):
        table_out[str(r)] = {str(col_keys[j]): obs[i][j] for j in range(n_cols)}

    return chi2, dof, cramers_v, table_out


def _build_contingency(labels_a, labels_b):
    """Build contingency table from two label vectors."""
    table = defaultdict(lambda: defaultdict(int))
    for a, b in zip(labels_a, labels_b):
        table[a][b] += 1
    return dict(table)


def _anova_f_test(values, labels):
    """
    One-way ANOVA F-test.

    Returns (F, significant_at_001).
    """
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)

    k = len(groups)
    n = len(values)
    if k < 2 or n <= k:
        return 0.0, False

    grand_mean = sum(values) / n

    # Between-group sum of squares
    ss_between = sum(len(g) * (sum(g) / len(g) - grand_mean) ** 2
                     for g in groups.values())

    # Within-group sum of squares
    ss_within = 0.0
    for g in groups.values():
        g_mean = sum(g) / len(g)
        ss_within += sum((v - g_mean) ** 2 for v in g)

    df_between = k - 1
    df_within = n - k

    if ss_within < 1e-12 or df_within <= 0:
        return 0.0, False

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_stat = ms_between / ms_within

    # Approximate p-value threshold: for F > 5 with typical dof, p < 0.01
    # More conservative: use a rough critical value table
    # For dof1=k-1, dof2=n-k, alpha=0.01: F_crit ~ 3.5 for moderate dof
    significant = f_stat > 4.0  # conservative approximation for p < 0.01

    return f_stat, significant


# ============================================================
# Null model helpers
# ============================================================

def _apply_real_transform(raw_vectors, z_means, z_stds, section_labels,
                          section_means, pca_eigenvectors, pca_n_components):
    """
    Apply the REAL data's z-normalization, section-residualization,
    and PCA projection to a set of vectors.

    Args:
        raw_vectors: list of 27-dim raw vectors
        z_means, z_stds: from real data z-normalization
        section_labels: section labels for each vector
        section_means: per-section mean vectors (in z-space)
        pca_eigenvectors: eigenvectors from real PCA
        pca_n_components: number of PCA components to keep

    Returns:
        PCA-projected vectors (list of lists)
    """
    d = len(z_means)
    n = len(raw_vectors)

    # Z-normalize using real parameters
    z_vecs = [[(raw_vectors[i][j] - z_means[j]) / z_stds[j]
               for j in range(d)] for i in range(n)]

    # Section-residualize using real section means
    residualized = []
    for i in range(n):
        s = section_labels[i]
        if s in section_means:
            mean_vec = section_means[s]
            residualized.append([z_vecs[i][j] - mean_vec[j] for j in range(d)])
        else:
            residualized.append(list(z_vecs[i]))

    # PCA-project using real eigenvectors
    # Center using the mean of the residualized data
    # (the real PCA was done on residualized data which was centered internally)
    # For null models projected into real space, we center with the
    # real residualized mean (which should be ~0 after section residualization)
    # but to be safe, use 0 as the center since residualized data is ~zero-mean
    projected = []
    nc = min(pca_n_components, len(pca_eigenvectors))
    for i in range(n):
        proj = []
        for c in range(nc):
            val = sum(residualized[i][j] * pca_eigenvectors[c][j] for j in range(d))
            proj.append(val)
        projected.append(proj)

    return projected


def _compute_bin_features_from_lines(body_lines):
    """
    Recompute 27-dim arc signature from a list of body line dicts.

    Splits into OPEN (first), INTERIOR (middle), CLOSE (last) bins
    and computes 9 features per bin.
    """
    if len(body_lines) < 3:
        return [0.0] * 27

    open_lines = [body_lines[0]]
    open_tokens = body_lines[0]['tokens']

    interior_lines = body_lines[1:-1]
    interior_tokens = []
    for line in interior_lines:
        interior_tokens.extend(line['tokens'])

    close_lines = [body_lines[-1]]
    close_tokens = body_lines[-1]['tokens']

    open_feats = _bin_features(open_tokens, open_lines)
    interior_feats = _bin_features(interior_tokens, interior_lines)
    close_feats = _bin_features(close_tokens, close_lines)

    return open_feats + interior_feats + close_feats


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 624, Script 2: Template Clustering + Null Models")
    print("=" * 58)

    # ================================================================
    # Phase 1: Load data
    # ================================================================
    print("\n[Phase 1] Loading arc signatures...")
    arc_path = RESULTS_DIR / 'arc_signatures.json'
    with open(arc_path) as f:
        arc_data = json.load(f)

    paragraphs = arc_data['paragraphs']
    n_par = len(paragraphs)
    print(f"  Loaded {n_par} paragraphs")

    # Extract vectors and metadata
    par_ids = [p['par_id'] for p in paragraphs]
    folios = [p['folio'] for p in paragraphs]
    sections = [p['section'] for p in paragraphs]
    regimes = [p['regime'] for p in paragraphs]
    n_body_lines_list = [p['n_body_lines'] for p in paragraphs]

    raw_vectors = [p['raw_vector'] for p in paragraphs]
    z_vectors = [p['z_normalized'] for p in paragraphs]
    resid_vectors = [p['section_residualized'] for p in paragraphs]
    pc_scores = arc_data['pca']['pc_scores']

    z_means = arc_data['z_means']
    z_stds = arc_data['z_stds']
    section_means = arc_data['section_means']
    pca_eigenvalues = arc_data['pca']['eigenvalues']
    pca_n_components = arc_data['pca']['n_components']

    # Recover PCA eigenvectors by re-running PCA on residualized vectors
    # (they weren't stored in arc_signatures.json)
    print("  Recovering PCA eigenvectors...")
    _, _, pca_eigenvectors, _, _ = pca_reduce(resid_vectors, variance_threshold=0.90)

    print(f"  Sections: {dict(Counter(sections))}")
    print(f"  Regimes: {dict(Counter(regimes))}")
    print(f"  PCA components: {pca_n_components}")

    # ================================================================
    # Phase 2: Pass A -- Raw (section-included) clustering
    # ================================================================
    print("\n[Phase 2] Pass A: Raw (section-included) clustering...")

    # PCA-reduce z-normalized vectors separately for Pass A
    print("  PCA on z-normalized (raw) vectors...")
    raw_pca_vecs, raw_eigvals, raw_eigvecs, raw_cumvar, raw_ncomp = \
        pca_reduce(z_vectors, variance_threshold=0.90)
    print(f"  Raw PCA components at 90%: {raw_ncomp}")

    # Ward linkage on raw PCA vectors
    print("  Ward linkage on raw PCA vectors...")
    raw_merges = ward_linkage(raw_pca_vecs)

    # Silhouette curve for k=2..12
    print("  Computing silhouette curve...")
    raw_sil_curve = {}
    for k in K_RANGE:
        labels = cut_dendrogram(raw_merges, n_par, k)
        sil = silhouette_score(raw_pca_vecs, labels)
        raw_sil_curve[k] = sil

    raw_best_sil_k = max(raw_sil_curve, key=raw_sil_curve.get)
    print(f"  Silhouette curve: {', '.join(f'k={k}:{s:.3f}' for k, s in raw_sil_curve.items())}")
    print(f"  Best silhouette k={raw_best_sil_k}: {raw_sil_curve[raw_best_sil_k]:.4f}")

    # Gap statistic for k=2..12
    print("  Computing gap statistic (200 references)...")
    raw_gap = gap_statistic(raw_pca_vecs, K_RANGE, n_ref=N_PERM, rng=random.Random(624))
    raw_gap_optimal = raw_gap['optimal_k']
    print(f"  Gap optimal k: {raw_gap_optimal}")

    # Use gap optimal k for Pass A
    raw_optimal_k = raw_gap_optimal
    raw_labels = cut_dendrogram(raw_merges, n_par, raw_optimal_k)

    # Chi-squared: cluster labels vs section labels
    print(f"  Chi-squared test at k={raw_optimal_k}...")
    contingency = _build_contingency(raw_labels, sections)
    chi2, dof, cramers_v, cont_table = _chi_squared_contingency(contingency)
    print(f"  Chi2={chi2:.2f}, dof={dof}, Cramer's V={cramers_v:.4f}")

    pass_a = {
        'silhouette_curve': {str(k): v for k, v in raw_sil_curve.items()},
        'gap_statistic': {
            'gaps': {str(k): v for k, v in raw_gap['gaps'].items()},
            'optimal_k': raw_gap_optimal,
        },
        'optimal_k': raw_optimal_k,
        'section_contingency': {
            'table': cont_table,
            'chi_squared': chi2,
            'cramers_v': cramers_v,
        },
    }

    # ================================================================
    # Phase 3: Pass B -- Section-residualized clustering (PRIMARY)
    # ================================================================
    print("\n[Phase 3] Pass B: Section-residualized clustering (PRIMARY)...")

    resid_pca_vecs = pc_scores  # Already PCA-reduced in Script 1

    # Ward linkage on residualized PCA vectors
    print("  Ward linkage on residualized PCA vectors...")
    resid_merges = ward_linkage(resid_pca_vecs)

    # Silhouette and Calinski-Harabasz curves
    print("  Computing silhouette and CH curves...")
    resid_sil_curve = {}
    resid_ch_curve = {}
    for k in K_RANGE:
        labels = cut_dendrogram(resid_merges, n_par, k)
        resid_sil_curve[k] = silhouette_score(resid_pca_vecs, labels)
        resid_ch_curve[k] = calinski_harabasz(resid_pca_vecs, labels)

    print(f"  Silhouette curve: {', '.join(f'k={k}:{s:.3f}' for k, s in resid_sil_curve.items())}")
    print(f"  CH curve: {', '.join(f'k={k}:{s:.1f}' for k, s in resid_ch_curve.items())}")

    # Gap statistic
    print("  Computing gap statistic (200 references)...")
    resid_gap = gap_statistic(resid_pca_vecs, K_RANGE, n_ref=N_PERM, rng=random.Random(625))
    resid_gap_optimal = resid_gap['optimal_k']
    print(f"  Gap optimal k: {resid_gap_optimal}")

    # Determine optimal k: prefer gap criterion, fallback to best silhouette
    resid_best_sil_k = max(resid_sil_curve, key=resid_sil_curve.get)
    resid_optimal_k = resid_gap_optimal
    print(f"  Best silhouette k={resid_best_sil_k}: {resid_sil_curve[resid_best_sil_k]:.4f}")
    print(f"  Using optimal k={resid_optimal_k}")

    # Ward labels at optimal k
    resid_ward_labels = cut_dendrogram(resid_merges, n_par, resid_optimal_k)
    resid_real_sil = silhouette_score(resid_pca_vecs, resid_ward_labels)
    print(f"  Real silhouette at k={resid_optimal_k}: {resid_real_sil:.4f}")

    # KMeans for robustness
    print("  KMeans for robustness check...")
    resid_km_labels = kmeans(resid_pca_vecs, resid_optimal_k, rng=random.Random(626))
    ward_km_ari = adjusted_rand_index(resid_ward_labels, resid_km_labels)
    print(f"  Ward-KMeans ARI: {ward_km_ari:.4f}")

    # Within-cluster and between-cluster cosine on ORIGINAL 27-dim residualized vectors
    print("  Computing within/between-cluster cosine similarity...")
    cluster_members = defaultdict(list)
    for i, l in enumerate(resid_ward_labels):
        cluster_members[l].append(i)

    within_cosines = []
    for cl, members in cluster_members.items():
        for i_idx in range(len(members)):
            for j_idx in range(i_idx + 1, len(members)):
                cs = cosine_similarity(resid_vectors[members[i_idx]],
                                       resid_vectors[members[j_idx]])
                within_cosines.append(cs)

    between_cosines = []
    cluster_ids = sorted(cluster_members.keys())
    for ci_idx in range(len(cluster_ids)):
        for cj_idx in range(ci_idx + 1, len(cluster_ids)):
            ci_members = cluster_members[cluster_ids[ci_idx]]
            cj_members = cluster_members[cluster_ids[cj_idx]]
            for mi in ci_members:
                for mj in cj_members:
                    cs = cosine_similarity(resid_vectors[mi], resid_vectors[mj])
                    between_cosines.append(cs)

    within_cos_mean = sum(within_cosines) / len(within_cosines) if within_cosines else 0.0
    between_cos_mean = sum(between_cosines) / len(between_cosines) if between_cosines else 0.0
    print(f"  Within-cluster cosine: {within_cos_mean:.4f}")
    print(f"  Between-cluster cosine: {between_cos_mean:.4f}")

    # Reconstruction R-squared on original 27-dim residualized vectors
    d = 27
    global_mean = [sum(resid_vectors[i][j] for i in range(n_par)) / n_par for j in range(d)]

    total_ss = sum(sum((resid_vectors[i][j] - global_mean[j]) ** 2
                       for j in range(d)) for i in range(n_par))

    centroids_27 = {}
    for cl, members in cluster_members.items():
        nc = len(members)
        centroids_27[cl] = [sum(resid_vectors[m][j] for m in members) / nc for j in range(d)]

    between_ss = sum(len(cluster_members[cl]) *
                     sum((centroids_27[cl][j] - global_mean[j]) ** 2 for j in range(d))
                     for cl in cluster_members)

    r_squared = between_ss / total_ss if total_ss > 1e-12 else 0.0
    print(f"  R-squared: {r_squared:.4f}")

    # Centroid PCA dimensionality
    centroid_list = [centroids_27[cl] for cl in sorted(centroids_27.keys())]
    if len(centroid_list) >= 2:
        _, cent_eigvals, _, cent_cumvar, _ = pca_reduce(centroid_list, variance_threshold=0.9999)
        centroid_pca_80 = 0
        total_cent_var = sum(cent_eigvals) if cent_eigvals else 1.0
        running_var = 0.0
        for idx, ev in enumerate(cent_eigvals):
            running_var += ev / total_cent_var if total_cent_var > 0 else 0
            if running_var >= 0.80:
                centroid_pca_80 = idx + 1
                break
        if centroid_pca_80 == 0:
            centroid_pca_80 = len(cent_eigvals)
    else:
        centroid_pca_80 = 1

    print(f"  Centroid PCA dims for 80%: {centroid_pca_80}")

    pass_b = {
        'silhouette_curve': {str(k): v for k, v in resid_sil_curve.items()},
        'calinski_harabasz_curve': {str(k): v for k, v in resid_ch_curve.items()},
        'gap_statistic': {
            'gaps': {str(k): v for k, v in resid_gap['gaps'].items()},
            'optimal_k': resid_gap_optimal,
        },
        'optimal_k': resid_optimal_k,
        'ward_kmeans_ari': ward_km_ari,
        'within_cluster_cosine': within_cos_mean,
        'between_cluster_cosine': between_cos_mean,
        'r_squared': r_squared,
        'centroid_pca_dims_for_80pct': centroid_pca_80,
        'labels': resid_ward_labels,
        'centroids': [centroids_27[cl] for cl in sorted(centroids_27.keys())],
    }

    # ================================================================
    # Phase 4: C853 comparison
    # ================================================================
    print("\n[Phase 4] C853 comparison...")

    c853_path = PROJECT_ROOT / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'b_paragraph_profiles.json'
    with open(c853_path) as f:
        c853_data = json.load(f)

    c853_profiles = c853_data['profiles']

    # Build C853 lookup: (folio, ordinal_0indexed) -> profile
    c853_by_folio = defaultdict(list)
    for p in c853_profiles:
        c853_by_folio[p['folio']].append(p)

    # Match paragraphs between arc_signatures and C853
    # arc_signatures: par_id = "folio_P{N}" where P{N} is 1-indexed paragraph ID
    # C853: sequential B_NNN, grouped by folio in order
    # Match by folio + ordinal position within folio
    matched_arc_indices = []
    matched_c853_profiles = []

    arc_by_folio = defaultdict(list)
    for idx, p in enumerate(paragraphs):
        arc_by_folio[p['folio']].append((idx, p['ordinal']))

    for folio in arc_by_folio:
        if folio not in c853_by_folio:
            continue
        c853_list = c853_by_folio[folio]
        for arc_idx, arc_ordinal in arc_by_folio[folio]:
            if arc_ordinal < len(c853_list):
                matched_arc_indices.append(arc_idx)
                matched_c853_profiles.append(c853_list[arc_ordinal])

    n_matched = len(matched_arc_indices)
    print(f"  Matched paragraphs: {n_matched}")

    if n_matched >= 10:
        # Extract C853 features: size, ht_delta, en_rate
        c853_features = []
        for prof in matched_c853_profiles:
            size = prof['size']['line_count']
            ht_delta = prof.get('ht_profile', {}).get('ht_delta', 0.0)
            if ht_delta is None:
                ht_profile = prof.get('ht_profile', {})
                body_rate = ht_profile.get('body_ht_rate', 0.0) or 0.0
                header_rate = ht_profile.get('line1_ht_rate', 0.0) or 0.0
                ht_delta = body_rate - header_rate
            en_rate = prof.get('role_profile', {}).get('en_rate', 0.0)
            if en_rate is None:
                en_rate = prof.get('initiation', {}).get('en_rate', 0.0) or 0.0
            c853_features.append([float(size), float(ht_delta or 0.0), float(en_rate or 0.0)])

        # Z-normalize C853 features
        c853_z, _, _ = z_normalize(c853_features)

        # KMeans k=5 on C853 features
        c853_labels = kmeans(c853_z, 5, rng=random.Random(853))

        # Get template labels for matched paragraphs
        matched_template_labels = [resid_ward_labels[i] for i in matched_arc_indices]

        c853_ari = adjusted_rand_index(matched_template_labels, c853_labels)
        print(f"  ARI(new templates, C853 k=5): {c853_ari:.4f}")
    else:
        c853_ari = 0.0
        print("  Too few matches for C853 comparison")

    c853_comparison = {
        'n_matched': n_matched,
        'ari': c853_ari,
    }

    # ================================================================
    # Phase 5: REGIME confound test
    # ================================================================
    print("\n[Phase 5] REGIME confound test...")

    regime_ari = adjusted_rand_index(resid_ward_labels, regimes)
    regime_contingency = _build_contingency(resid_ward_labels, regimes)
    regime_chi2, regime_dof, regime_cramers_v, regime_table = \
        _chi_squared_contingency(regime_contingency)

    is_regime_alias = regime_ari > 0.40
    print(f"  ARI(template, regime): {regime_ari:.4f}")
    print(f"  Chi2={regime_chi2:.2f}, Cramer's V={regime_cramers_v:.4f}")
    print(f"  Is regime alias: {is_regime_alias}")

    regime_confound = {
        'ari': regime_ari,
        'chi_squared': regime_chi2,
        'cramers_v': regime_cramers_v,
        'is_alias': is_regime_alias,
    }

    # ================================================================
    # Phase 6: Five null models (N_PERM=200 replicates each)
    # ================================================================
    print(f"\n[Phase 6] Null models ({N_PERM} replicates each)...")

    # Pre-compute section means in z-space for null transforms
    section_means_z = {}
    section_indices = defaultdict(list)
    for i, s in enumerate(sections):
        section_indices[s].append(i)
    for s, indices in section_indices.items():
        ns = len(indices)
        section_means_z[s] = [sum(z_vectors[idx][j] for idx in indices) / ns
                              for j in range(27)]

    def _null_cluster_silhouette(null_pca_vecs, k):
        """Cluster null data and return silhouette."""
        null_merges = ward_linkage(null_pca_vecs)
        null_labels = cut_dendrogram(null_merges, len(null_pca_vecs), k)
        return silhouette_score(null_pca_vecs, null_labels)

    # ---- N0: Bin permutation ----
    print("  N0: Bin permutation...")
    n0_sils = []
    for rep in range(N_PERM):
        if rep % 50 == 0:
            print(f"    Replicate {rep}/{N_PERM}...")
        rng_n0 = random.Random(RNG.random())

        # For each paragraph, randomly permute the 3 bins (chunks of 9)
        permuted_raw = []
        for i in range(n_par):
            vec = raw_vectors[i]
            bins = [vec[0:9], vec[9:18], vec[18:27]]
            rng_n0.shuffle(bins)
            permuted_raw.append(bins[0] + bins[1] + bins[2])

        # Apply real transform
        null_pca = _apply_real_transform(
            permuted_raw, z_means, z_stds, sections,
            section_means_z, pca_eigenvectors, pca_n_components
        )
        n0_sils.append(_null_cluster_silhouette(null_pca, resid_optimal_k))

    n0_mean = sum(n0_sils) / len(n0_sils)
    n0_std = math.sqrt(sum((s - n0_mean) ** 2 for s in n0_sils) / len(n0_sils))
    n0_ratio = n0_mean / resid_real_sil if resid_real_sil > 1e-6 else 0.0
    print(f"    N0 mean_sil={n0_mean:.4f}, std={n0_std:.4f}, ratio={n0_ratio:.4f}")

    # ---- Build corpus for N1 and N4 (line-level shuffles) ----
    print("  Building corpus for line-level null models...")
    corpus = build_corpus()

    # Build paragraph -> body lines mapping, matched by par_id
    par_body_lines = {}
    for folio in sorted(corpus.keys()):
        fdata = corpus[folio]
        for para in fdata['paragraphs']:
            pid = f"{folio}_{para['id']}"
            par_body_lines[pid] = para['body_lines']

    # Verify all arc_signatures paragraphs are found
    matched_corpus = 0
    for p in paragraphs:
        if p['par_id'] in par_body_lines:
            matched_corpus += 1
    print(f"  Corpus match: {matched_corpus}/{n_par} paragraphs")

    # Group paragraphs by section and folio for shuffles
    par_indices_by_section = defaultdict(list)
    par_indices_by_folio = defaultdict(list)
    for i, p in enumerate(paragraphs):
        par_indices_by_section[p['section']].append(i)
        par_indices_by_folio[p['folio']].append(i)

    # ---- N1: Cross-paragraph pool shuffle within section ----
    print("  N1: Cross-paragraph pool shuffle within section...")
    n1_sils = []
    for rep in range(N_PERM):
        if rep % 50 == 0:
            print(f"    Replicate {rep}/{N_PERM}...")
        rng_n1 = random.Random(RNG.random())

        # For each section, pool body lines and redistribute
        shuffled_raw_vectors = [None] * n_par

        for sec, indices in par_indices_by_section.items():
            # Pool all body lines from this section's paragraphs
            pool = []
            par_sizes = []
            for i in indices:
                pid = par_ids[i]
                body = par_body_lines.get(pid, [])
                pool.extend(body)
                par_sizes.append(len(body))

            # Shuffle the pool
            rng_n1.shuffle(pool)

            # Redistribute preserving paragraph sizes
            offset = 0
            for idx_in_section, i in enumerate(indices):
                size = par_sizes[idx_in_section]
                shuffled_body = pool[offset:offset + size]
                offset += size

                if len(shuffled_body) >= MIN_BODY_LINES:
                    vec = _compute_bin_features_from_lines(shuffled_body)
                else:
                    vec = raw_vectors[i]  # fallback
                shuffled_raw_vectors[i] = vec

        # Apply real transform
        null_pca = _apply_real_transform(
            shuffled_raw_vectors, z_means, z_stds, sections,
            section_means_z, pca_eigenvectors, pca_n_components
        )
        n1_sils.append(_null_cluster_silhouette(null_pca, resid_optimal_k))

    n1_mean = sum(n1_sils) / len(n1_sils)
    n1_std = math.sqrt(sum((s - n1_mean) ** 2 for s in n1_sils) / len(n1_sils))
    n1_ratio = n1_mean / resid_real_sil if resid_real_sil > 1e-6 else 0.0
    print(f"    N1 mean_sil={n1_mean:.4f}, std={n1_std:.4f}, ratio={n1_ratio:.4f}")

    # ---- N2: Folio mediation test ----
    print("  N2: Folio mediation test...")

    # Real statistic: per-section, compute folio x template chi-squared
    n2_real_chi2_total = 0.0
    n2_section_stats = {}
    for sec, indices in par_indices_by_section.items():
        if len(indices) < 5:
            continue
        sec_template_labels = [resid_ward_labels[i] for i in indices]
        sec_folio_labels = [folios[i] for i in indices]
        sec_contingency = _build_contingency(sec_template_labels, sec_folio_labels)
        sec_chi2, sec_dof, sec_cv, _ = _chi_squared_contingency(sec_contingency)
        n2_real_chi2_total += sec_chi2
        n2_section_stats[sec] = {'chi2': sec_chi2, 'dof': sec_dof, 'cramers_v': sec_cv}

    print(f"    Real total chi2 (across sections): {n2_real_chi2_total:.2f}")

    # Null: shuffle folio labels within section
    n2_null_chi2s = []
    for rep in range(N_PERM):
        if rep % 50 == 0:
            print(f"    Replicate {rep}/{N_PERM}...")
        rng_n2 = random.Random(RNG.random())

        null_chi2_total = 0.0
        for sec, indices in par_indices_by_section.items():
            if len(indices) < 5:
                continue
            sec_template_labels = [resid_ward_labels[i] for i in indices]
            sec_folio_labels = [folios[i] for i in indices]
            rng_n2.shuffle(sec_folio_labels)
            sec_contingency = _build_contingency(sec_template_labels, sec_folio_labels)
            sec_chi2, _, _, _ = _chi_squared_contingency(sec_contingency)
            null_chi2_total += sec_chi2

        n2_null_chi2s.append(null_chi2_total)

    n2_null_mean = sum(n2_null_chi2s) / len(n2_null_chi2s)
    n2_null_std = math.sqrt(sum((s - n2_null_mean) ** 2 for s in n2_null_chi2s) / len(n2_null_chi2s))
    n2_p_value = sum(1 for v in n2_null_chi2s if v >= n2_real_chi2_total) / len(n2_null_chi2s)
    print(f"    Null mean chi2={n2_null_mean:.2f}, std={n2_null_std:.2f}")
    print(f"    p-value={n2_p_value:.4f}")

    # ---- N3: Length-matched shuffle ----
    print("  N3: Length-matched shuffle...")
    n3_sils = []

    # Create length groups: paragraphs with n_body_lines within +/-1
    # Sort by length, then create overlapping groups
    sorted_by_length = sorted(range(n_par), key=lambda i: n_body_lines_list[i])

    for rep in range(N_PERM):
        if rep % 50 == 0:
            print(f"    Replicate {rep}/{N_PERM}...")
        rng_n3 = random.Random(RNG.random())

        # Group paragraphs by length (+/-1) and shuffle vectors within groups
        shuffled_raw = list(raw_vectors)  # copy

        # Create groups: for each unique length, group paragraphs with that length +/-1
        length_groups = defaultdict(list)
        for i in range(n_par):
            length_groups[n_body_lines_list[i]].append(i)

        # For each paragraph, find eligible swap partners (length within +/-1)
        # and do a random permutation within the group
        visited = set()
        for length_val in sorted(length_groups.keys()):
            # Collect all indices with this length or adjacent lengths
            group_indices = []
            for dl in [-1, 0, 1]:
                group_indices.extend(length_groups.get(length_val + dl, []))
            # Remove already-visited
            group_indices = [i for i in group_indices if i not in visited]
            if len(group_indices) < 2:
                visited.update(group_indices)
                continue

            # Shuffle the raw vectors among these indices
            group_vecs = [list(raw_vectors[i]) for i in group_indices]
            rng_n3.shuffle(group_vecs)
            for idx_in_group, i in enumerate(group_indices):
                shuffled_raw[i] = group_vecs[idx_in_group]
            visited.update(group_indices)

        # Apply real transform
        null_pca = _apply_real_transform(
            shuffled_raw, z_means, z_stds, sections,
            section_means_z, pca_eigenvectors, pca_n_components
        )
        n3_sils.append(_null_cluster_silhouette(null_pca, resid_optimal_k))

    n3_mean = sum(n3_sils) / len(n3_sils)
    n3_std = math.sqrt(sum((s - n3_mean) ** 2 for s in n3_sils) / len(n3_sils))
    n3_ratio = n3_mean / resid_real_sil if resid_real_sil > 1e-6 else 0.0
    print(f"    N3 mean_sil={n3_mean:.4f}, std={n3_std:.4f}, ratio={n3_ratio:.4f}")

    # ---- N4: Within-folio body-line shuffle ----
    print("  N4: Within-folio body-line shuffle...")
    n4_sils = []
    for rep in range(N_PERM):
        if rep % 50 == 0:
            print(f"    Replicate {rep}/{N_PERM}...")
        rng_n4 = random.Random(RNG.random())

        shuffled_raw_vectors = [None] * n_par

        for folio_name, indices in par_indices_by_folio.items():
            # Pool all body lines from this folio's eligible paragraphs
            pool = []
            par_sizes = []
            for i in indices:
                pid = par_ids[i]
                body = par_body_lines.get(pid, [])
                pool.extend(body)
                par_sizes.append(len(body))

            # Shuffle within folio
            rng_n4.shuffle(pool)

            # Redistribute
            offset = 0
            for idx_in_folio, i in enumerate(indices):
                size = par_sizes[idx_in_folio]
                shuffled_body = pool[offset:offset + size]
                offset += size

                if len(shuffled_body) >= MIN_BODY_LINES:
                    vec = _compute_bin_features_from_lines(shuffled_body)
                else:
                    vec = raw_vectors[i]
                shuffled_raw_vectors[i] = vec

        null_pca = _apply_real_transform(
            shuffled_raw_vectors, z_means, z_stds, sections,
            section_means_z, pca_eigenvectors, pca_n_components
        )
        n4_sils.append(_null_cluster_silhouette(null_pca, resid_optimal_k))

    n4_mean = sum(n4_sils) / len(n4_sils)
    n4_std = math.sqrt(sum((s - n4_mean) ** 2 for s in n4_sils) / len(n4_sils))
    n4_ratio = n4_mean / resid_real_sil if resid_real_sil > 1e-6 else 0.0
    print(f"    N4 mean_sil={n4_mean:.4f}, std={n4_std:.4f}, ratio={n4_ratio:.4f}")

    null_models = {
        'N0_bin_permutation': {'mean_sil': n0_mean, 'std_sil': n0_std, 'ratio': n0_ratio},
        'N1_pool_shuffle': {'mean_sil': n1_mean, 'std_sil': n1_std, 'ratio': n1_ratio},
        'N2_folio_mediation': {
            'real_chi2': n2_real_chi2_total,
            'null_mean_chi2': n2_null_mean,
            'null_std_chi2': n2_null_std,
            'p_value': n2_p_value,
        },
        'N3_length_matched': {'mean_sil': n3_mean, 'std_sil': n3_std, 'ratio': n3_ratio},
        'N4_within_folio': {'mean_sil': n4_mean, 'std_sil': n4_std, 'ratio': n4_ratio},
    }

    # ================================================================
    # Phase 7: Paragraph length confound
    # ================================================================
    print("\n[Phase 7] Paragraph length confound...")
    f_stat, f_sig = _anova_f_test(n_body_lines_list, resid_ward_labels)
    print(f"  ANOVA F={f_stat:.2f}, significant(p<0.01)={f_sig}")

    length_confound = {
        'f_statistic': f_stat,
        'significant': f_sig,
    }

    # ================================================================
    # Phase 8: Verdict logic
    # ================================================================
    print("\n[Phase 8] Verdict logic...")

    # Gap significance: check if gap at optimal_k > gap_se
    gap_val = resid_gap['gaps'].get(resid_optimal_k, 0)
    gap_se = resid_gap.get('gap_se', {}).get(resid_optimal_k, 0)
    gap_significant = gap_val > 1.96 * gap_se  # rough p<0.05

    print(f"  Residualized silhouette at optimal k: {resid_real_sil:.4f}")
    print(f"  Gap significant: {gap_significant} (gap={gap_val:.4f}, se={gap_se:.4f})")
    print(f"  N0 ratio: {n0_ratio:.4f}")
    print(f"  N1 ratio: {n1_ratio:.4f}")
    print(f"  Regime ARI: {regime_ari:.4f}")
    print(f"  Raw (Pass A) best sil: {raw_sil_curve[raw_best_sil_k]:.4f}")

    verdict = None

    # REGIME_ALIAS: residualized finds structure but regime ARI > 0.40
    if resid_real_sil > 0.15 and regime_ari > 0.40:
        verdict = 'REGIME_ALIAS'
    # SECTION_ONLY: raw finds structure but residualized does not
    elif raw_sil_curve[raw_best_sil_k] > 0.20 and resid_real_sil < 0.15:
        verdict = 'SECTION_ONLY'
    # LINE_POSITIONAL_ONLY: N1 preserves > 80% of structure
    elif resid_real_sil > 0.15 and n1_ratio > 0.80:
        verdict = 'LINE_POSITIONAL_ONLY'
    # DISCRETE_TEMPLATES: strong clustering signal
    elif resid_real_sil > 0.25 and gap_significant and n0_ratio < 0.50 and regime_ari < 0.40:
        verdict = 'DISCRETE_TEMPLATES'
    # WEAK_TEMPLATES: moderate signal
    elif 0.15 <= resid_real_sil <= 0.25:
        verdict = 'WEAK_TEMPLATES'
    # CONTINUOUS_MANIFOLD: no k gives decent silhouette
    elif resid_real_sil < 0.15:
        verdict = 'CONTINUOUS_MANIFOLD'
    # Fallback: if silhouette > 0.25 but gap not significant or N0 ratio high
    elif resid_real_sil > 0.25:
        verdict = 'WEAK_TEMPLATES'
    else:
        verdict = 'CONTINUOUS_MANIFOLD'

    print(f"\n  VERDICT: {verdict}")

    # ================================================================
    # Assemble output
    # ================================================================
    print("\nAssembling output JSON...")

    output = {
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_paragraphs': n_par,
            'n_perm': N_PERM,
        },
        'pass_a': pass_a,
        'pass_b': pass_b,
        'c853_comparison': c853_comparison,
        'regime_confound': regime_confound,
        'null_models': null_models,
        'length_confound': length_confound,
        'verdict': verdict,
    }

    output = round_floats(output)

    out_path = RESULTS_DIR / 'clustering_results.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 58)
    print("SUMMARY")
    print("=" * 58)
    print(f"  Paragraphs:                 {n_par}")
    print(f"  Pass A optimal k:           {raw_optimal_k}")
    print(f"  Pass A best sil:            {raw_sil_curve[raw_best_sil_k]:.4f}")
    print(f"  Pass A section Cramer's V:  {cramers_v:.4f}")
    print(f"  Pass B optimal k:           {resid_optimal_k}")
    print(f"  Pass B silhouette:          {resid_real_sil:.4f}")
    print(f"  Pass B R-squared:           {r_squared:.4f}")
    print(f"  Pass B Ward-KMeans ARI:     {ward_km_ari:.4f}")
    print(f"  C853 ARI:                   {c853_ari:.4f}")
    print(f"  Regime ARI:                 {regime_ari:.4f}")
    print(f"  Regime alias:               {is_regime_alias}")
    print(f"  N0 (bin perm) ratio:        {n0_ratio:.4f}")
    print(f"  N1 (pool shuffle) ratio:    {n1_ratio:.4f}")
    print(f"  N2 (folio med.) p-value:    {n2_p_value:.4f}")
    print(f"  N3 (length-match) ratio:    {n3_ratio:.4f}")
    print(f"  N4 (within-folio) ratio:    {n4_ratio:.4f}")
    print(f"  Length confound F:          {f_stat:.2f} (sig={f_sig})")
    print(f"  VERDICT:                    {verdict}")
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
