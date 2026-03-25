"""
Phase 624: PARAGRAPH_STRUCTURAL_ISOMORPHISM -- Script 3: Section Analysis + Validation

Seven analyses that probe whether arc-signature templates are section-specific or
universal across the manuscript, validate header prediction, test short-paragraph
matching, and check template ordering against C1399 (null ordering).

Input files:
  - arc_signatures.json         (Script 1 output)
  - clustering_results.json     (Script 2 output)
  - grammar_temperature.json    (Phase 623 output)

Output: section_analysis.json
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

# Project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from phases.PARAGRAPH_STRUCTURAL_ISOMORPHISM.scripts.shared_624 import (
    ward_linkage,
    cut_dendrogram,
    silhouette_score,
    gap_statistic,
    adjusted_rand_index,
    nearest_centroid_classify,
    pca_reduce,
    z_normalize,
    cosine_similarity,
    kmeans,
    round_floats,
    euclidean_dist,
    RESULTS_DIR,
    RNG,
    N_PERM,
    ARC_FEATURE_NAMES,
    BIN_NAMES,
)

# ============================================================
# Statistical helpers
# ============================================================

def _rank(values):
    """Assign ranks to values (average rank for ties)."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and values[indexed[j + 1]] == values[indexed[j]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(x, y):
    """Spearman rank correlation as Pearson on ranks (average ties)."""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)
    n = len(x)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    sx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    sy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def normal_cdf(x):
    """Standard normal CDF using the error function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def chi2_p_value(chi2_stat, df):
    """
    Approximate p-value for chi-squared distribution.
    For large df, chi-squared ~ Normal(df, 2*df).
    """
    if df <= 0:
        return 1.0
    if chi2_stat <= 0:
        return 1.0
    z = (chi2_stat - df) / math.sqrt(2.0 * df)
    return 1.0 - normal_cdf(z)


def shannon_entropy(counts):
    """Shannon entropy in bits from a list/dict of counts."""
    total = sum(counts) if isinstance(counts, list) else sum(counts.values())
    if total <= 0:
        return 0.0
    probs = []
    items = counts if isinstance(counts, list) else counts.values()
    for c in items:
        if c > 0:
            p = c / total
            probs.append(p)
    return -sum(p * math.log2(p) for p in probs)


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 624, Script 3: Section Analysis + Validation")
    print("=" * 60)

    # ---- Load input files ----
    print("\n[LOAD] Reading input files...")

    arc_path = RESULTS_DIR / 'arc_signatures.json'
    cluster_path = RESULTS_DIR / 'clustering_results.json'
    grammar_temp_path = (
        _PROJECT_ROOT / 'phases' / 'LINE_LEVEL_SEQUENTIAL_ARCHITECTURE'
        / 'results' / 'grammar_temperature.json'
    )

    with open(arc_path) as f:
        arc_data = json.load(f)
    with open(cluster_path) as f:
        cluster_data = json.load(f)
    with open(grammar_temp_path) as f:
        grammar_temp_data = json.load(f)

    paragraphs = arc_data['paragraphs']
    short_paragraphs = arc_data.get('short_paragraphs', [])
    n_eligible = len(paragraphs)
    print(f"  Eligible paragraphs: {n_eligible}")
    print(f"  Short paragraphs: {len(short_paragraphs)}")

    # Build quick lookups
    par_id_to_idx = {p['par_id']: i for i, p in enumerate(paragraphs)}
    sections = [p['section'] for p in paragraphs]
    folios = [p['folio'] for p in paragraphs]

    # Extract vectors
    raw_vectors = [p['raw_vector'] for p in paragraphs]
    z_vectors = [p['z_normalized'] for p in paragraphs]
    residualized_vectors = [p['section_residualized'] for p in paragraphs]

    # ---- Parse clustering results ----
    # Pass A labels (raw clustering) -- may not be stored; reconstruct if needed
    pass_a = cluster_data.get('pass_a', cluster_data.get('passA', {}))
    pass_a_labels = pass_a.get('labels', [])
    pass_a_k = pass_a.get('optimal_k', 2)
    if not pass_a_labels:
        # Reconstruct Pass A labels by re-running Ward on z-normalized vectors
        print("  Pass A labels not in clustering results; reconstructing from z_vectors...")
        from shared_624 import ward_linkage, cut_dendrogram, pca_reduce
        raw_pca, *_ = pca_reduce(z_vectors, 0.90)
        raw_merges = ward_linkage(raw_pca)
        pass_a_labels = cut_dendrogram(raw_merges, n_eligible, pass_a_k)

    # Pass B labels (section-residualized clustering)
    pass_b = cluster_data.get('pass_b', cluster_data.get('passB', {}))
    pass_b_labels = pass_b.get('labels', [])
    pass_b_k = pass_b.get('optimal_k', pass_b.get('k', max(pass_b_labels) + 1 if pass_b_labels else 2))
    pass_b_centroids = pass_b.get('centroids', [])

    print(f"  Pass A: k={pass_a_k}, {len(pass_a_labels)} labels")
    print(f"  Pass B: k={pass_b_k}, {len(pass_b_labels)} labels")

    # ============================================================
    # 4a. Template x Section contingency
    # ============================================================
    print("\n[4a] Template x Section contingency...")

    section_set = sorted(set(sections))
    cluster_set = sorted(set(pass_a_labels))

    # Build contingency table
    contingency = defaultdict(lambda: defaultdict(int))
    for i in range(n_eligible):
        cl = pass_a_labels[i]
        sec = sections[i]
        contingency[cl][sec] += 1

    # Compute chi-squared
    row_totals = {}
    for cl in cluster_set:
        row_totals[cl] = sum(contingency[cl][sec] for sec in section_set)

    col_totals = {}
    for sec in section_set:
        col_totals[sec] = sum(contingency[cl][sec] for cl in cluster_set)

    grand_total = sum(row_totals.values())

    chi2 = 0.0
    for cl in cluster_set:
        for sec in section_set:
            observed = contingency[cl][sec]
            expected = (row_totals[cl] * col_totals[sec]) / grand_total if grand_total > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    # Cramer's V
    k_clusters = len(cluster_set)
    k_sections = len(section_set)
    min_dim = min(k_clusters, k_sections) - 1
    if min_dim > 0 and grand_total > 0:
        cramers_v = math.sqrt(chi2 / (grand_total * min_dim))
    else:
        cramers_v = 0.0

    # Per-section template frequency distributions
    per_section_distributions = {}
    for sec in section_set:
        dist = {}
        sec_total = col_totals[sec]
        for cl in cluster_set:
            frac = contingency[cl][sec] / sec_total if sec_total > 0 else 0.0
            dist[str(cl)] = frac
        per_section_distributions[sec] = dist

    # Contingency table for output
    contingency_table = {}
    for cl in cluster_set:
        contingency_table[str(cl)] = {sec: contingency[cl][sec] for sec in section_set}

    chi2_df = (k_clusters - 1) * (k_sections - 1)
    chi2_p = chi2_p_value(chi2, chi2_df)

    section_contingency = {
        'table': contingency_table,
        'chi_squared': chi2,
        'df': chi2_df,
        'p_value': chi2_p,
        'cramers_v': cramers_v,
        'per_section_distributions': per_section_distributions,
    }

    print(f"  Chi-squared: {chi2:.4f}, df={chi2_df}, p={chi2_p:.6f}")
    print(f"  Cramer's V: {cramers_v:.4f}")
    for sec in section_set:
        print(f"  Section {sec}: {col_totals[sec]} paragraphs, "
              f"dist = {per_section_distributions[sec]}")

    # ============================================================
    # 4b. Per-section independent clustering
    # ============================================================
    print("\n[4b] Per-section independent clustering...")

    SECTION_MIN = 30
    per_section_clustering = {}
    small_sections = {}

    # Group paragraphs by section
    section_indices = defaultdict(list)
    for i, sec in enumerate(sections):
        section_indices[sec].append(i)

    for sec in sorted(section_indices.keys()):
        indices = section_indices[sec]
        n_sec = len(indices)

        if n_sec < SECTION_MIN:
            # Small section: descriptive statistics only
            sec_vectors = [residualized_vectors[i] for i in indices]
            d = len(sec_vectors[0])
            mean_arc = [sum(v[j] for v in sec_vectors) / n_sec for j in range(d)]
            arc_variance = [
                sum((v[j] - mean_arc[j]) ** 2 for v in sec_vectors) / n_sec
                for j in range(d)
            ]
            small_sections[sec] = {
                'n_eligible': n_sec,
                'mean_arc': mean_arc,
                'arc_variance': arc_variance,
            }
            print(f"  Section {sec}: {n_sec} paragraphs (< {SECTION_MIN}, descriptive only)")
            continue

        print(f"  Section {sec}: {n_sec} paragraphs, clustering...")

        # Extract section's residualized vectors
        sec_vectors = [residualized_vectors[i] for i in indices]

        # PCA-reduce within section
        sec_z, sec_z_means, sec_z_stds = z_normalize(sec_vectors)
        sec_reduced, sec_eigvals, sec_eigvecs, sec_cumvar, sec_ncomp = \
            pca_reduce(sec_z, variance_threshold=0.90)

        if sec_ncomp == 0:
            print(f"    PCA returned 0 components, skipping")
            small_sections[sec] = {
                'n_eligible': n_sec,
                'note': 'PCA returned 0 components',
            }
            continue

        print(f"    PCA dims retained: {sec_ncomp}")

        # Ward linkage
        merges = ward_linkage(sec_reduced)

        # Silhouette for k=2..8
        k_range = list(range(2, min(9, n_sec)))
        sil_curve = {}
        for k in k_range:
            labels_k = cut_dendrogram(merges, n_sec, k)
            sil_k = silhouette_score(sec_reduced, labels_k)
            sil_curve[k] = sil_k

        # Gap statistic
        sec_rng = RNG  # shared RNG
        gap_result = gap_statistic(sec_reduced, k_range, n_ref=200, rng=sec_rng)
        gap_optimal_k = gap_result['optimal_k']

        # Pick optimal k: prefer gap, fallback to max silhouette
        if gap_optimal_k and gap_optimal_k in sil_curve:
            optimal_k = gap_optimal_k
        else:
            optimal_k = max(sil_curve, key=sil_curve.get) if sil_curve else 2

        sil_at_optimal = sil_curve.get(optimal_k, 0.0)
        print(f"    Optimal k: {optimal_k}, silhouette: {sil_at_optimal:.4f}")

        # Get reference labels at optimal k
        ref_labels = cut_dendrogram(merges, n_sec, optimal_k)

        # Bootstrap stability test: 100 replicates
        print(f"    Bootstrap stability (100 replicates)...")
        n_boot = 100
        boot_aris = []
        for b in range(n_boot):
            # Resample 80% of section paragraphs
            n_sample = max(2, int(0.8 * n_sec))
            sample_indices = sorted(RNG.sample(range(n_sec), n_sample))
            sample_vecs = [sec_reduced[i] for i in sample_indices]

            if len(sample_vecs) <= optimal_k:
                continue

            # Cluster sample
            sample_merges = ward_linkage(sample_vecs)
            sample_labels = cut_dendrogram(sample_merges, n_sample, optimal_k)

            # Build reference labels for sampled subset
            ref_subset = [ref_labels[i] for i in sample_indices]

            ari = adjusted_rand_index(ref_subset, sample_labels)
            boot_aris.append(ari)

        mean_ari = sum(boot_aris) / len(boot_aris) if boot_aris else 0.0
        stable = mean_ari >= 0.50

        print(f"    Bootstrap mean ARI: {mean_ari:.4f}, stable: {stable}")

        # Template diversity entropy
        label_counts = Counter(ref_labels)
        diversity_entropy = shannon_entropy(list(label_counts.values()))

        per_section_clustering[sec] = {
            'n_eligible': n_sec,
            'optimal_k': optimal_k,
            'silhouette': sil_at_optimal,
            'pca_dims': sec_ncomp,
            'bootstrap_mean_ari': mean_ari,
            'stable': stable,
            'diversity_entropy': diversity_entropy,
            'silhouette_curve': {str(k): v for k, v in sil_curve.items()},
            '_labels': ref_labels,  # keep for cross-section portability (not in output)
            '_reduced': sec_reduced,  # keep for cross-section portability
            '_z_means': sec_z_means,
            '_z_stds': sec_z_stds,
            '_eigvecs': sec_eigvecs,
            '_ncomp': sec_ncomp,
            '_indices': indices,
        }

    # ============================================================
    # Grammar temperature correlation (P5)
    # ============================================================
    print("\n[P5] Grammar temperature correlation...")

    # Find largest section
    largest_sec = max(section_indices.keys(), key=lambda s: len(section_indices[s]))
    print(f"  Largest section: {largest_sec} ({len(section_indices[largest_sec])} paragraphs)")

    # Grammar temperature per folio
    gt_per_folio = grammar_temp_data.get('per_folio', {})

    # Compute per-folio arc diversity (mean pairwise Euclidean) within largest section
    largest_indices = section_indices[largest_sec]
    folio_par_indices = defaultdict(list)
    for i in largest_indices:
        folio_par_indices[paragraphs[i]['folio']].append(i)

    folio_arc_diversity = {}
    for folio, par_idxs in folio_par_indices.items():
        if len(par_idxs) < 2:
            continue
        # Mean pairwise Euclidean distance on residualized vectors
        total_dist = 0.0
        n_pairs = 0
        for a in range(len(par_idxs)):
            for b in range(a + 1, len(par_idxs)):
                total_dist += euclidean_dist(
                    residualized_vectors[par_idxs[a]],
                    residualized_vectors[par_idxs[b]]
                )
                n_pairs += 1
        if n_pairs > 0:
            folio_arc_diversity[folio] = total_dist / n_pairs

    # Match with grammar temperature
    folio_diversity_list = []
    folio_temp_list = []
    for folio in sorted(folio_arc_diversity.keys()):
        if folio in gt_per_folio:
            folio_diversity_list.append(folio_arc_diversity[folio])
            folio_temp_list.append(gt_per_folio[folio]['T_composite'])

    n_folios_corr = len(folio_diversity_list)
    if n_folios_corr >= 3:
        rho = spearman_rho(folio_diversity_list, folio_temp_list)
        direction = 'positive' if rho > 0 else 'negative'
    else:
        rho = 0.0
        direction = 'insufficient data'

    grammar_temp_correlation = {
        'section': largest_sec,
        'n_folios': n_folios_corr,
        'spearman_rho': rho,
        'direction': direction,
        'note': 'low power',
    }

    print(f"  Folios with arc diversity + temperature: {n_folios_corr}")
    print(f"  Spearman rho: {rho:.4f} ({direction})")

    # ============================================================
    # 4c. Cross-section template portability
    # ============================================================
    print("\n[4c] Cross-section template portability...")

    training_sec = largest_sec
    cross_section_portability = {
        'training_section': training_sec,
        'training_k': None,
        'test_sections': {},
    }

    if training_sec in per_section_clustering:
        train_info = per_section_clustering[training_sec]
        train_k = train_info['optimal_k']
        train_labels = train_info['_labels']
        train_reduced = train_info['_reduced']
        train_z_means = train_info['_z_means']
        train_z_stds = train_info['_z_stds']
        train_eigvecs = train_info['_eigvecs']
        train_ncomp = train_info['_ncomp']
        train_indices = train_info['_indices']

        cross_section_portability['training_k'] = train_k

        # Compute training centroids in PCA space
        d_pca = len(train_reduced[0]) if train_reduced else 0
        train_centroids = {}
        for cl in sorted(set(train_labels)):
            members = [i for i in range(len(train_labels)) if train_labels[i] == cl]
            if members and d_pca > 0:
                centroid = [
                    sum(train_reduced[m][j] for m in members) / len(members)
                    for j in range(d_pca)
                ]
                train_centroids[cl] = centroid

        print(f"  Training section: {training_sec}, k={train_k}")

        # For each other section with enough data
        for sec in sorted(section_indices.keys()):
            if sec == training_sec:
                continue

            sec_idx = section_indices[sec]
            n_test = len(sec_idx)
            if n_test < 3:
                print(f"  Section {sec}: {n_test} paragraphs, skipping")
                continue

            # Project into training section's PCA space:
            # 1. Get their residualized vectors
            test_resid = [residualized_vectors[i] for i in sec_idx]

            # 2. Z-normalize using training section's means/stds
            d_full = len(test_resid[0])
            test_z = []
            for v in test_resid:
                test_z.append([
                    (v[j] - train_z_means[j]) / train_z_stds[j]
                    if train_z_stds[j] > 1e-10 else 0.0
                    for j in range(d_full)
                ])

            # 3. Apply training PCA transform
            test_projected = []
            for v in test_z:
                proj = []
                for c in range(train_ncomp):
                    val = sum(v[j] * train_eigvecs[c][j] for j in range(d_full))
                    proj.append(val)
                test_projected.append(proj)

            # 4. Assign to nearest centroid
            projected_labels = []
            for v in test_projected:
                best_cl = None
                best_d = float('inf')
                for cl, centroid in train_centroids.items():
                    d = euclidean_dist(v, centroid)
                    if d < best_d:
                        best_d = d
                        best_cl = cl
                projected_labels.append(best_cl)

            # 5. If this section has independent clustering, compute ARI
            result_entry = {'n_projected': n_test}

            if sec in per_section_clustering:
                independent_labels = per_section_clustering[sec]['_labels']
                ari = adjusted_rand_index(projected_labels, independent_labels)
                result_entry['ari_vs_independent'] = ari
                print(f"  Section {sec}: {n_test} projected, ARI vs independent: {ari:.4f}")
            else:
                result_entry['ari_vs_independent'] = None
                print(f"  Section {sec}: {n_test} projected, no independent clustering for ARI")

            cross_section_portability['test_sections'][sec] = result_entry
    else:
        print(f"  Training section {training_sec} has < {SECTION_MIN} paragraphs, skipping portability")

    # ============================================================
    # 4d. Anti-parallel boundary universality
    # ============================================================
    print("\n[4d] Anti-parallel boundary universality...")

    n_features = len(ARC_FEATURE_NAMES)  # 9
    passb_cluster_set = sorted(set(pass_b_labels))
    per_template_cosine = {}
    anti_parallel_count = 0
    threshold = -0.30

    for cl in passb_cluster_set:
        # Collect raw vectors for paragraphs in this template
        member_indices = [i for i in range(n_eligible) if pass_b_labels[i] == cl]
        if not member_indices:
            continue

        # Mean OPEN vector (first 9 dims) and mean CLOSE vector (last 9 dims)
        open_sum = [0.0] * n_features
        close_sum = [0.0] * n_features
        n_members = len(member_indices)

        for i in member_indices:
            vec = raw_vectors[i]
            for j in range(n_features):
                open_sum[j] += vec[j]
                close_sum[j] += vec[2 * n_features + j]

        mean_open = [s / n_members for s in open_sum]
        mean_close = [s / n_members for s in close_sum]

        cos = cosine_similarity(mean_open, mean_close)
        per_template_cosine[str(cl)] = cos
        if cos < threshold:
            anti_parallel_count += 1

    n_templates = len(passb_cluster_set)
    fraction_anti_parallel = anti_parallel_count / n_templates if n_templates > 0 else 0.0

    anti_parallel_universality = {
        'per_template_cosine': per_template_cosine,
        'fraction_anti_parallel': fraction_anti_parallel,
        'threshold': threshold,
    }

    print(f"  Templates: {n_templates}")
    for cl, cos in sorted(per_template_cosine.items()):
        flag = " <-- ANTI-PARALLEL" if cos < threshold else ""
        print(f"    Template {cl}: cosine = {cos:.4f}{flag}")
    print(f"  Fraction anti-parallel: {fraction_anti_parallel:.4f}")

    # ============================================================
    # 4e. Header atom validation (P8)
    # ============================================================
    print("\n[4e] Header atom validation (P8)...")

    # Extract header feature vectors for paragraphs that have them
    header_indices = []
    header_vectors = []
    header_gallows = []
    header_template_labels = []

    for i in range(n_eligible):
        hdr = paragraphs[i].get('header_features')
        if hdr is not None and hdr.get('vector') is not None:
            header_indices.append(i)
            header_vectors.append(hdr['vector'])
            header_gallows.append(hdr.get('gallows_type', 'none'))
            header_template_labels.append(pass_b_labels[i])

    n_header = len(header_indices)
    print(f"  Paragraphs with header features: {n_header}")

    k_templates = pass_b_k
    chance_level = 1.0 / k_templates if k_templates > 0 else 0.0

    # Full-header prediction: LOO nearest-centroid
    if n_header >= 5:
        loo_correct = 0
        for i in range(n_header):
            train_vecs = header_vectors[:i] + header_vectors[i+1:]
            train_labels = header_template_labels[:i] + header_template_labels[i+1:]
            test_vec = [header_vectors[i]]
            pred = nearest_centroid_classify(train_vecs, train_labels, test_vec)
            if pred[0] == header_template_labels[i]:
                loo_correct += 1

        full_header_accuracy = loo_correct / n_header

        # Permutation test (200 reps)
        print(f"    Full-header LOO accuracy: {full_header_accuracy:.4f} (chance: {chance_level:.4f})")
        print(f"    Running permutation test ({N_PERM} reps)...")
        null_accuracies = []
        for p_rep in range(N_PERM):
            shuffled_labels = list(header_template_labels)
            RNG.shuffle(shuffled_labels)

            null_correct = 0
            for i in range(n_header):
                train_vecs = header_vectors[:i] + header_vectors[i+1:]
                train_labels = shuffled_labels[:i] + shuffled_labels[i+1:]
                test_vec = [header_vectors[i]]
                pred = nearest_centroid_classify(train_vecs, train_labels, test_vec)
                if pred[0] == shuffled_labels[i]:
                    null_correct += 1
            null_accuracies.append(null_correct / n_header)

        full_header_p = sum(1 for a in null_accuracies if a >= full_header_accuracy) / N_PERM
        print(f"    Permutation p-value: {full_header_p:.4f}")

        # Gallows-only prediction: LOO
        gallows_correct = 0
        for i in range(n_header):
            test_gallows = header_gallows[i]
            # Find most common template among training paragraphs with same gallows type
            train_gallows = header_gallows[:i] + header_gallows[i+1:]
            train_labels = header_template_labels[:i] + header_template_labels[i+1:]

            # Count templates for this gallows type in training set
            matching = [train_labels[j] for j in range(len(train_labels))
                        if train_gallows[j] == test_gallows]
            if matching:
                most_common = Counter(matching).most_common(1)[0][0]
            else:
                # No matching gallows in training: predict most common overall
                most_common = Counter(train_labels).most_common(1)[0][0]

            if most_common == header_template_labels[i]:
                gallows_correct += 1

        gallows_only_accuracy = gallows_correct / n_header
        print(f"    Gallows-only LOO accuracy: {gallows_only_accuracy:.4f}")

    else:
        full_header_accuracy = 0.0
        gallows_only_accuracy = 0.0
        full_header_p = 1.0
        print(f"  Too few headers for validation (need >= 5, have {n_header})")

    header_validation = {
        'full_header_accuracy': full_header_accuracy,
        'gallows_only_accuracy': gallows_only_accuracy,
        'chance_level': chance_level,
        'full_header_p_value': full_header_p,
        'full_beats_chance': full_header_accuracy > chance_level,
        'full_beats_gallows': full_header_accuracy > gallows_only_accuracy,
        'n_headers': n_header,
    }

    # ============================================================
    # 4f. Short paragraph phase matching
    # ============================================================
    print("\n[4f] Short paragraph phase matching...")

    n_short = len(short_paragraphs)
    short_distribution = Counter()

    if n_short > 0 and pass_b_centroids:
        # Build 2-bin centroids from Pass B 27-dim centroids
        # Each centroid: [OPEN_9, INTERIOR_9, CLOSE_9]
        # 2-bin: BOUNDARY = mean(OPEN_9, CLOSE_9), INTERIOR = INTERIOR_9
        # -> 18-dim: [BOUNDARY_9, INTERIOR_9]
        two_bin_centroids = []
        for centroid in pass_b_centroids:
            open_9 = centroid[:n_features]
            interior_9 = centroid[n_features:2*n_features]
            close_9 = centroid[2*n_features:]
            boundary_9 = [(open_9[j] + close_9[j]) / 2.0 for j in range(n_features)]
            two_bin_centroid = boundary_9 + interior_9
            two_bin_centroids.append(two_bin_centroid)

        # Assign each short paragraph to nearest template centroid
        for sp in short_paragraphs:
            vec = sp['boundary_interior_vector']
            best_cl = 0
            best_d = float('inf')
            for cl_idx, centroid in enumerate(two_bin_centroids):
                d = euclidean_dist(vec, centroid)
                if d < best_d:
                    best_d = d
                    best_cl = cl_idx
            short_distribution[best_cl] += 1

        # Chi-squared test: uniform vs observed
        n_templates_b = len(two_bin_centroids)
        expected_uniform = n_short / n_templates_b if n_templates_b > 0 else 0.0
        chi2_short = 0.0
        for cl_idx in range(n_templates_b):
            observed = short_distribution.get(cl_idx, 0)
            if expected_uniform > 0:
                chi2_short += (observed - expected_uniform) ** 2 / expected_uniform

        df_short = n_templates_b - 1
        p_short = chi2_p_value(chi2_short, df_short)

        print(f"  Short paragraphs: {n_short}")
        print(f"  Distribution: {dict(short_distribution)}")
        print(f"  Chi-squared (vs uniform): {chi2_short:.4f}, df={df_short}, p={p_short:.4f}")

    else:
        chi2_short = 0.0
        p_short = 1.0
        print(f"  No short paragraphs or no centroids available")

    short_paragraph_matching = {
        'n_short': n_short,
        'distribution': {f"template_{k}": v for k, v in sorted(short_distribution.items())},
        'chi_squared': chi2_short,
        'uniform_p_value': p_short,
    }

    # ============================================================
    # 4g. Template ordering null (C1399 consistency, P9)
    # ============================================================
    print("\n[4g] Template ordering null (C1399)...")

    # Build per-folio template sequences using Pass B labels
    folio_sequences = defaultdict(list)
    # We need paragraphs in ordinal order within each folio
    folio_par_data = defaultdict(list)
    for i in range(n_eligible):
        folio_par_data[paragraphs[i]['folio']].append(
            (paragraphs[i]['ordinal'], pass_b_labels[i])
        )

    for folio in folio_par_data:
        # Sort by ordinal
        sorted_pars = sorted(folio_par_data[folio], key=lambda x: x[0])
        folio_sequences[folio] = [label for _, label in sorted_pars]

    # Build transition matrix from folios with >= 3 paragraphs
    transition_counts = defaultdict(int)
    n_transitions = 0
    template_marginals_from = Counter()
    template_marginals_to = Counter()

    for folio, seq in folio_sequences.items():
        if len(seq) < 3:
            continue
        for t in range(len(seq) - 1):
            fr = seq[t]
            to = seq[t + 1]
            key = f"{fr}->{to}"
            transition_counts[key] += 1
            template_marginals_from[fr] += 1
            template_marginals_to[to] += 1
            n_transitions += 1

    # Chi-squared: observed vs expected under independence
    all_from = sorted(set(template_marginals_from.keys()))
    all_to = sorted(set(template_marginals_to.keys()))

    chi2_order = 0.0
    df_cells = 0
    for fr in all_from:
        for to in all_to:
            observed = transition_counts.get(f"{fr}->{to}", 0)
            expected = (template_marginals_from[fr] * template_marginals_to[to]) / n_transitions \
                if n_transitions > 0 else 0.0
            if expected > 0:
                chi2_order += (observed - expected) ** 2 / expected
                df_cells += 1

    df_order = max(0, df_cells - len(all_from) - len(all_to) + 1)
    # More standard df for contingency: (rows-1)*(cols-1)
    df_order_standard = max(0, (len(all_from) - 1) * (len(all_to) - 1))
    # Use the standard formula
    df_order = df_order_standard

    p_order = chi2_p_value(chi2_order, df_order) if df_order > 0 else 1.0
    ordering_exists = p_order < 0.05

    template_ordering = {
        'transition_matrix': {k: v for k, v in sorted(transition_counts.items())},
        'chi_squared': chi2_order,
        'df': df_order,
        'p_value': p_order,
        'n_transitions': n_transitions,
        'ordering_exists': ordering_exists,
    }

    print(f"  Transitions: {n_transitions}")
    print(f"  Chi-squared: {chi2_order:.4f}, df={df_order}, p={p_order:.4f}")
    print(f"  Ordering exists: {ordering_exists}")
    if ordering_exists:
        print("  WARNING: Template ordering detected -- possible confound leakage")
    else:
        print("  Consistent with C1399 (no preferred sequence)")

    # ============================================================
    # Assemble output
    # ============================================================
    print("\n[OUTPUT] Assembling results...")

    # Clean per_section_clustering of internal keys
    clean_per_section = {}
    for sec, info in per_section_clustering.items():
        clean_per_section[sec] = {
            k: v for k, v in info.items() if not k.startswith('_')
        }

    output = {
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_eligible': n_eligible,
            'n_short': n_short,
            'pass_a_k': pass_a_k,
            'pass_b_k': pass_b_k,
        },
        'section_contingency': section_contingency,
        'per_section_clustering': clean_per_section,
        'SMALL_SECTIONS': small_sections,
        'grammar_temp_correlation': grammar_temp_correlation,
        'cross_section_portability': cross_section_portability,
        'anti_parallel_universality': anti_parallel_universality,
        'header_validation': header_validation,
        'short_paragraph_matching': short_paragraph_matching,
        'template_ordering': template_ordering,
    }

    output = round_floats(output)

    # Nest SMALL_SECTIONS under per_section_clustering in output
    output['per_section_clustering']['SMALL_SECTIONS'] = output.pop('SMALL_SECTIONS')

    out_path = RESULTS_DIR / 'section_analysis.json'
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  4a. Contingency: Cramer's V = {cramers_v:.4f}, chi2 p = {chi2_p:.6f}")
    for sec in sorted(per_section_clustering.keys()):
        info = per_section_clustering[sec]
        print(f"  4b. Section {sec}: k={info['optimal_k']}, "
              f"sil={info['silhouette']:.4f}, "
              f"stable={info.get('stable', 'N/A')}, "
              f"H_div={info['diversity_entropy']:.4f}")
    for sec in sorted(small_sections.keys()):
        print(f"  4b. Section {sec}: {small_sections[sec]['n_eligible']} paragraphs (small)")
    print(f"  P5. Grammar temp correlation: rho={rho:.4f} ({direction})")
    if training_sec in per_section_clustering:
        for sec, res in cross_section_portability['test_sections'].items():
            ari_val = res.get('ari_vs_independent')
            ari_str = f"{ari_val:.4f}" if ari_val is not None else "N/A"
            print(f"  4c. Portability {training_sec}->{sec}: ARI={ari_str}")
    print(f"  4d. Anti-parallel fraction: {fraction_anti_parallel:.4f}")
    print(f"  4e. Header: full={full_header_accuracy:.4f}, "
          f"gallows={gallows_only_accuracy:.4f}, "
          f"chance={chance_level:.4f}, p={full_header_p:.4f}")
    print(f"  4f. Short paragraphs: {n_short}, chi2 p={p_short:.4f}")
    print(f"  4g. Ordering: chi2={chi2_order:.4f}, p={p_order:.4f}, "
          f"exists={ordering_exists}")
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
