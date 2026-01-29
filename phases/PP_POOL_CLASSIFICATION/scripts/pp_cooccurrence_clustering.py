#!/usr/bin/env python3
"""
PP_POOL_CLASSIFICATION Phase — Script 1: PP Co-Occurrence Clustering

Tests 1-4: Build A-record PP co-occurrence matrix, discover pools via
hierarchical clustering, test attribute alignment, control for section.

Constraints produced: C656 (network topology), C657 (pool census),
C658 (attribute alignment)
"""

import json
import sys
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.stats import chi2_contingency, fisher_exact, entropy as sp_entropy
from sklearn.metrics import silhouette_score, normalized_mutual_info_score, adjusted_rand_score

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
MIN_RECORDS = 3       # minimum A records for inclusion in clustering
MAX_K = 20            # maximum clusters to test
SIL_THRESHOLD = 0.25  # silhouette acceptance threshold


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, set):
            return sorted(list(obj))
        return super().default(obj)


# ---------------------------------------------------------------------------
# Section 1: Load & Prepare
# ---------------------------------------------------------------------------
print("=" * 70)
print("PP CO-OCCURRENCE CLUSTERING")
print("=" * 70)

# Load PP set (404)
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])
print(f"PP MIDDLEs loaded: {len(pp_set)}")

# Load AZC-Med / B-Native split
with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])
pp_role_map = role_data['pp_role_map']
print(f"AZC-Med: {len(azc_med_set)}, B-Native: {len(b_native_set)}")

# Load material class
with open(PROJECT_ROOT / 'phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    pp_class_data = json.load(f)
pp_classification = pp_class_data['pp_classification']

# Load lane discrimination data
with open(PROJECT_ROOT / 'phases/LANE_CHANGE_HOLD_ANALYSIS/results/lane_pp_discrimination.json') as f:
    lane_disc_data = json.load(f)
disc_results = lane_disc_data['discrimination_test']['all_results']

# Load EN-exclusive data
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_data = json.load(f)

# Lane prediction (C649 initial character rule)
def lane_prediction(middle):
    if not middle:
        return 'neutral'
    c = middle[0]
    if c in ('k', 't', 'p'):
        return 'QO'
    elif c in ('e', 'o'):
        return 'CHSH'
    return 'neutral'

# Build A-record PP sets
tx = Transcript()
morph = Morphology()

record_pp_sets = {}    # (folio, line) -> set of PP MIDDLEs
record_sections = {}   # (folio, line) -> section

for token in tx.currier_a():
    key = (token.folio, token.line)
    m = morph.extract(token.word)
    if m.middle and m.middle in pp_set:
        record_pp_sets.setdefault(key, set()).add(m.middle)
    if key not in record_sections:
        record_sections[key] = token.section

# Build PP -> record index
pp_records = defaultdict(set)
for (folio, line), middles in record_pp_sets.items():
    for mid in middles:
        pp_records[mid].add((folio, line))

n_records_total = len(record_pp_sets)
print(f"A records with PP: {n_records_total}")
print(f"PP MIDDLEs appearing in A records: {len(pp_records)}")

# Record frequency distribution
pp_record_counts = {mid: len(recs) for mid, recs in pp_records.items()}

# Filter: PP MIDDLEs with >= MIN_RECORDS A records
filtered_pp = sorted([mid for mid, cnt in pp_record_counts.items() if cnt >= MIN_RECORDS])
excluded_pp = sorted([mid for mid in pp_set if mid not in pp_records or pp_record_counts.get(mid, 0) < MIN_RECORDS])
print(f"Filtered PP (>={MIN_RECORDS} records): {len(filtered_pp)}")
print(f"Excluded PP: {len(excluded_pp)}")

# Attribute lookup functions
def get_material_class(mid):
    if mid in pp_classification:
        return pp_classification[mid].get('material_class', 'UNKNOWN')
    return 'UNKNOWN'

def get_pathway(mid):
    if mid in azc_med_set:
        return 'AZC-Med'
    elif mid in b_native_set:
        return 'B-Native'
    return 'UNKNOWN'

# Section lookup for records
def get_record_section(key):
    return record_sections.get(key, 'UNKNOWN')


# ---------------------------------------------------------------------------
# Section 2: Test 1 — PP Co-Occurrence Matrix
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 1: PP Co-Occurrence Matrix")
print("=" * 70)

n = len(filtered_pp)
mid_to_idx = {mid: i for i, mid in enumerate(filtered_pp)}

# Build Jaccard similarity matrix
jaccard_matrix = np.zeros((n, n))
cooccur_count = np.zeros((n, n), dtype=int)

# Pre-compute record sets for filtered PP
pp_record_sets = {mid: pp_records[mid] for mid in filtered_pp}

for i in range(n):
    mid_i = filtered_pp[i]
    recs_i = pp_record_sets[mid_i]
    for j in range(i + 1, n):
        mid_j = filtered_pp[j]
        recs_j = pp_record_sets[mid_j]
        intersection = len(recs_i & recs_j)
        union = len(recs_i | recs_j)
        cooccur_count[i, j] = intersection
        cooccur_count[j, i] = intersection
        if union > 0:
            jac = intersection / union
            jaccard_matrix[i, j] = jac
            jaccard_matrix[j, i] = jac

# Diagonal = 1 (self-similarity)
np.fill_diagonal(jaccard_matrix, 1.0)

# Matrix statistics
upper_tri = jaccard_matrix[np.triu_indices(n, k=1)]
n_pairs = len(upper_tri)
n_zero = int(np.sum(upper_tri == 0))
n_nonzero = n_pairs - n_zero
sparsity = n_zero / n_pairs if n_pairs > 0 else 1.0

print(f"Matrix size: {n}x{n}")
print(f"Total pairs: {n_pairs}")
print(f"Zero-Jaccard pairs: {n_zero} ({sparsity:.1%})")
print(f"Non-zero pairs: {n_nonzero} ({1-sparsity:.1%})")

if n_nonzero > 0:
    nonzero_vals = upper_tri[upper_tri > 0]
    print(f"Non-zero Jaccard: mean={np.mean(nonzero_vals):.4f}, "
          f"median={np.median(nonzero_vals):.4f}, max={np.max(nonzero_vals):.4f}")
else:
    nonzero_vals = np.array([])
    print("WARNING: All pairs have zero Jaccard!")

# Component analysis (connected components from co-occurrence)
# Use BFS on adjacency where Jaccard > 0
visited = set()
components = []
for start in range(n):
    if start in visited:
        continue
    component = []
    queue = [start]
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        component.append(filtered_pp[node])
        for neighbor in range(n):
            if neighbor not in visited and jaccard_matrix[node, neighbor] > 0:
                queue.append(neighbor)
    components.append(component)

components.sort(key=len, reverse=True)
print(f"Connected components: {len(components)}")
print(f"Largest component: {len(components[0])} PP MIDDLEs")
if len(components) > 1:
    print(f"Isolated PP (component size=1): {sum(1 for c in components if len(c) == 1)}")

# Degree distribution (number of non-zero co-occurrence partners)
degrees = np.sum(jaccard_matrix > 0, axis=1) - 1  # subtract self
degree_stats = {
    'mean': float(np.mean(degrees)),
    'median': float(np.median(degrees)),
    'max': int(np.max(degrees)),
    'min': int(np.min(degrees)),
    'n_isolated': int(np.sum(degrees == 0))
}
print(f"Degree stats: mean={degree_stats['mean']:.1f}, median={degree_stats['median']:.0f}, "
      f"max={degree_stats['max']}, isolated={degree_stats['n_isolated']}")

cooccurrence_results = {
    'n_filtered': n,
    'n_excluded': len(excluded_pp),
    'excluded_pp': excluded_pp[:20],  # sample
    'n_records_total': n_records_total,
    'stats': {
        'n_pairs': n_pairs,
        'n_zero_jaccard': n_zero,
        'n_nonzero_jaccard': n_nonzero,
        'sparsity': sparsity,
        'nonzero_mean': float(np.mean(nonzero_vals)) if len(nonzero_vals) > 0 else None,
        'nonzero_median': float(np.median(nonzero_vals)) if len(nonzero_vals) > 0 else None,
        'nonzero_max': float(np.max(nonzero_vals)) if len(nonzero_vals) > 0 else None,
    },
    'component_analysis': {
        'n_components': len(components),
        'largest_component_size': len(components[0]),
        'component_sizes': [len(c) for c in components[:20]],
        'n_isolated': sum(1 for c in components if len(c) == 1),
    },
    'degree_stats': degree_stats,
    'record_count_stats': {
        'mean': float(np.mean(list(pp_record_counts.values()))),
        'median': float(np.median(list(pp_record_counts.values()))),
        'max': int(max(pp_record_counts.values())),
        'min': int(min(pp_record_counts.values())),
    }
}


# ---------------------------------------------------------------------------
# Section 3: Test 2 — Hierarchical Clustering
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 2: Hierarchical Clustering")
print("=" * 70)

# Distance matrix = 1 - Jaccard
distance_matrix = 1.0 - jaccard_matrix
np.fill_diagonal(distance_matrix, 0.0)

# Condensed form for scipy
condensed = squareform(distance_matrix)

# Multiple linkage methods
linkage_methods = ['average', 'complete', 'ward']
clustering_results = {}

for method in linkage_methods:
    print(f"\n--- Linkage: {method} ---")
    try:
        if method == 'ward':
            # Ward requires Euclidean distances; use distance matrix directly
            Z = linkage(condensed, method='ward')
        else:
            Z = linkage(condensed, method=method)
    except Exception as e:
        print(f"  FAILED: {e}")
        clustering_results[method] = {'error': str(e)}
        continue

    sil_scores = {}
    for k in range(2, min(MAX_K + 1, n)):
        labels = fcluster(Z, t=k, criterion='maxclust')
        # Check we actually got k clusters
        n_actual = len(set(labels))
        if n_actual < 2:
            continue
        try:
            sil = silhouette_score(distance_matrix, labels, metric='precomputed')
            sil_scores[k] = float(sil)
        except Exception:
            pass

    if sil_scores:
        # Find highest k with silhouette >= threshold
        qualifying = {k: s for k, s in sil_scores.items() if s >= SIL_THRESHOLD}
        if qualifying:
            optimal_k = max(qualifying.keys())
            optimal_sil = qualifying[optimal_k]
        else:
            # Fallback: best silhouette regardless of threshold
            optimal_k = max(sil_scores, key=sil_scores.get)
            optimal_sil = sil_scores[optimal_k]

        print(f"  Silhouette scores: {', '.join(f'k={k}: {s:.3f}' for k, s in sorted(sil_scores.items())[:10])}")
        print(f"  Qualifying (>={SIL_THRESHOLD}): {len(qualifying) if qualifying else 0}")
        print(f"  Selected k={optimal_k} (sil={optimal_sil:.4f})")

        # Get cluster assignments at optimal k
        labels_opt = fcluster(Z, t=optimal_k, criterion='maxclust')
        cluster_sizes = Counter(labels_opt)

        # Within-cluster and between-cluster distances
        within_dists = []
        between_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                d = distance_matrix[i, j]
                if labels_opt[i] == labels_opt[j]:
                    within_dists.append(d)
                else:
                    between_dists.append(d)

        clustering_results[method] = {
            'silhouette_scores': sil_scores,
            'optimal_k': optimal_k,
            'optimal_silhouette': optimal_sil,
            'meets_threshold': optimal_sil >= SIL_THRESHOLD,
            'cluster_sizes': {int(k): int(v) for k, v in sorted(cluster_sizes.items())},
            'cluster_assignments': {filtered_pp[i]: int(labels_opt[i]) for i in range(n)},
            'within_cluster_mean_dist': float(np.mean(within_dists)) if within_dists else None,
            'between_cluster_mean_dist': float(np.mean(between_dists)) if between_dists else None,
        }
        print(f"  Cluster sizes: {dict(sorted(cluster_sizes.items()))}")
        print(f"  Within mean dist: {np.mean(within_dists):.4f}" if within_dists else "  Within: N/A")
        print(f"  Between mean dist: {np.mean(between_dists):.4f}" if between_dists else "  Between: N/A")
    else:
        print("  No valid silhouette scores computed")
        clustering_results[method] = {'error': 'no_valid_silhouette'}

# Select primary result (UPGMA = average linkage)
primary_method = 'average'
primary_result = clustering_results.get(primary_method, {})

# Also compute baselines: k=4 (material class) and k=2 (pathway)
print("\n--- Baseline comparisons ---")
baselines = {}
for baseline_k, baseline_name in [(4, 'material_class'), (2, 'pathway')]:
    try:
        Z_avg = linkage(condensed, method='average')
        labels_bl = fcluster(Z_avg, t=baseline_k, criterion='maxclust')
        sil_bl = silhouette_score(distance_matrix, labels_bl, metric='precomputed')
        baselines[baseline_name] = {
            'k': baseline_k,
            'silhouette': float(sil_bl),
            'cluster_sizes': {int(k): int(v) for k, v in Counter(labels_bl).items()},
        }
        print(f"  {baseline_name} (k={baseline_k}): sil={sil_bl:.4f}")
    except Exception as e:
        baselines[baseline_name] = {'error': str(e)}

hierarchical_results = {
    'primary_method': primary_method,
    'linkage_results': clustering_results,
    'baselines': baselines,
}


# ---------------------------------------------------------------------------
# Section 4: Test 3 — Attribute Alignment
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 3: Attribute Alignment")
print("=" * 70)

# Use primary clustering assignments
if 'cluster_assignments' not in primary_result:
    print("WARNING: No primary clustering available, skipping attribute alignment")
    alignment_results = {'error': 'no_primary_clustering'}
else:
    assignments = primary_result['cluster_assignments']
    optimal_k = primary_result['optimal_k']

    # Collect attributes per PP MIDDLE
    pool_labels = []
    material_labels = []
    pathway_labels = []
    lane_labels = []
    existing_cluster_labels = []

    for mid in filtered_pp:
        pool_labels.append(assignments[mid])
        material_labels.append(get_material_class(mid))
        pathway_labels.append(get_pathway(mid))
        lane_labels.append(lane_prediction(mid))
        # Existing cluster from pp_classification
        existing = pp_classification.get(mid, {}).get('cluster')
        existing_cluster_labels.append(existing if existing is not None else -1)

    pool_arr = np.array(pool_labels)
    mat_arr = np.array(material_labels)
    path_arr = np.array(pathway_labels)
    lane_arr = np.array(lane_labels)
    exist_arr = np.array(existing_cluster_labels)

    def safe_chi2(table):
        """Chi-squared with Fisher's exact fallback for small expected counts."""
        table = np.array(table)
        if table.shape == (2, 2):
            if np.any(table < 5):
                _, p = fisher_exact(table)
                return {'test': 'fisher_exact', 'p': float(p), 'chi2': None, 'cramers_v': None}
        try:
            chi2, p, dof, expected = chi2_contingency(table)
            # Cramér's V
            n_obs = table.sum()
            min_dim = min(table.shape) - 1
            cramers_v = math.sqrt(chi2 / (n_obs * min_dim)) if min_dim > 0 and n_obs > 0 else 0.0
            return {
                'test': 'chi2',
                'chi2': float(chi2),
                'p': float(p),
                'dof': int(dof),
                'cramers_v': float(cramers_v),
                'min_expected': float(expected.min()),
            }
        except Exception as e:
            return {'test': 'error', 'error': str(e)}

    def build_contingency(labels_a, labels_b):
        """Build contingency table from two label arrays."""
        cats_a = sorted(set(labels_a))
        cats_b = sorted(set(labels_b), key=str)
        table = np.zeros((len(cats_a), len(cats_b)), dtype=int)
        for la, lb in zip(labels_a, labels_b):
            i = cats_a.index(la)
            j = list(cats_b).index(lb)
            table[i, j] += 1
        return table, cats_a, cats_b

    alignment_results = {}

    # 3a: Pool × Material Class
    print("\n--- Pool × Material Class ---")
    table_mat, pools, mats = build_contingency(pool_labels, material_labels)
    chi2_mat = safe_chi2(table_mat)
    nmi_mat = float(normalized_mutual_info_score(pool_labels, material_labels))
    print(f"  Chi2 test: {chi2_mat}")
    print(f"  NMI (pool, material): {nmi_mat:.4f}")
    print(f"  Table:\n  {mats}")
    for i, p in enumerate(pools):
        print(f"    Pool {p}: {list(table_mat[i])}")

    alignment_results['material_class'] = {
        'chi2_test': chi2_mat,
        'nmi': nmi_mat,
        'table': table_mat.tolist(),
        'row_labels': [int(x) for x in pools],
        'col_labels': list(mats),
        'per_pool': {
            int(pools[i]): {mats[j]: int(table_mat[i, j]) for j in range(len(mats))}
            for i in range(len(pools))
        },
        'redundant': nmi_mat > 0.8,
    }

    # 3b: Pool × Pathway
    print("\n--- Pool × Pathway ---")
    table_path, pools_p, paths = build_contingency(pool_labels, pathway_labels)
    chi2_path = safe_chi2(table_path)
    nmi_path = float(normalized_mutual_info_score(pool_labels, pathway_labels))
    print(f"  Chi2 test: {chi2_path}")
    print(f"  NMI (pool, pathway): {nmi_path:.4f}")

    alignment_results['pathway'] = {
        'chi2_test': chi2_path,
        'nmi': nmi_path,
        'table': table_path.tolist(),
        'row_labels': [int(x) for x in pools_p],
        'col_labels': list(paths),
        'per_pool': {
            int(pools_p[i]): {paths[j]: int(table_path[i, j]) for j in range(len(paths))}
            for i in range(len(pools_p))
        },
    }

    # 3c: Pool × Lane Character
    print("\n--- Pool × Lane Character ---")
    table_lane, pools_l, lanes = build_contingency(pool_labels, lane_labels)
    chi2_lane = safe_chi2(table_lane)
    nmi_lane = float(normalized_mutual_info_score(pool_labels, lane_labels))
    print(f"  Chi2 test: {chi2_lane}")
    print(f"  NMI (pool, lane): {nmi_lane:.4f}")

    alignment_results['lane_character'] = {
        'chi2_test': chi2_lane,
        'nmi': nmi_lane,
        'table': table_lane.tolist(),
        'row_labels': [int(x) for x in pools_l],
        'col_labels': list(lanes),
    }

    # 3d: Homogeneity - within-pool material entropy
    print("\n--- Homogeneity Analysis ---")
    overall_mat_counts = Counter(material_labels)
    overall_mat_dist = np.array([overall_mat_counts[m] for m in sorted(overall_mat_counts)])
    overall_mat_entropy = float(sp_entropy(overall_mat_dist / overall_mat_dist.sum(), base=2))

    pool_entropies = {}
    for p in sorted(set(pool_labels)):
        pool_mats = [mat_arr[i] for i in range(n) if pool_arr[i] == p]
        pool_counts = Counter(pool_mats)
        dist = np.array([pool_counts.get(m, 0) for m in sorted(overall_mat_counts)])
        pool_ent = float(sp_entropy(dist / dist.sum(), base=2)) if dist.sum() > 0 else 0.0
        pool_entropies[int(p)] = pool_ent

    mean_pool_entropy = float(np.mean(list(pool_entropies.values())))
    entropy_reduction = overall_mat_entropy - mean_pool_entropy

    print(f"  Overall material entropy: {overall_mat_entropy:.4f} bits")
    print(f"  Mean within-pool entropy: {mean_pool_entropy:.4f} bits")
    print(f"  Entropy reduction: {entropy_reduction:.4f} bits ({entropy_reduction/overall_mat_entropy:.1%})")

    alignment_results['homogeneity'] = {
        'overall_material_entropy': overall_mat_entropy,
        'mean_pool_entropy': mean_pool_entropy,
        'entropy_reduction': entropy_reduction,
        'entropy_reduction_pct': entropy_reduction / overall_mat_entropy if overall_mat_entropy > 0 else 0,
        'per_pool_entropy': pool_entropies,
    }

    # 3e: Compare to existing pp_classification cluster field
    print("\n--- Comparison to Existing Clusters ---")
    # Filter to PP with non-null existing cluster
    valid_exist = [(pool_labels[i], existing_cluster_labels[i])
                   for i in range(n) if existing_cluster_labels[i] != -1]
    if len(valid_exist) >= 10:
        exist_pool = [x[0] for x in valid_exist]
        exist_old = [x[1] for x in valid_exist]
        ari_existing = float(adjusted_rand_score(exist_pool, exist_old))
        print(f"  ARI (new pools, existing clusters): {ari_existing:.4f} (n={len(valid_exist)})")
        alignment_results['vs_existing_clusters'] = {
            'ari': ari_existing,
            'n_comparable': len(valid_exist),
        }
    else:
        print(f"  Insufficient overlap with existing clusters ({len(valid_exist)} PP)")
        alignment_results['vs_existing_clusters'] = {
            'ari': None,
            'n_comparable': len(valid_exist),
            'note': 'insufficient_overlap',
        }

    # Summary NMI table
    print(f"\n--- NMI Summary ---")
    nmi_scores = {
        'material_class': nmi_mat,
        'pathway': nmi_path,
        'lane_character': nmi_lane,
    }
    for axis, score in nmi_scores.items():
        tag = " *** REDUNDANT" if score > 0.8 else (" (strong)" if score > 0.5 else "")
        print(f"  {axis}: NMI = {score:.4f}{tag}")

    alignment_results['nmi_summary'] = nmi_scores


# ---------------------------------------------------------------------------
# Section 5: Test 4 — Section-Controlled Analysis
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 4: Section-Controlled Analysis")
print("=" * 70)

section_control_results = {}

if 'cluster_assignments' in primary_result:
    assignments = primary_result['cluster_assignments']

    # 4a: Section distribution per pool
    pool_section_dist = defaultdict(Counter)
    for mid in filtered_pp:
        pool = assignments[mid]
        # Get all records for this PP and their sections
        for rec in pp_records[mid]:
            sec = get_record_section(rec)
            pool_section_dist[pool][sec] += 1

    print("\nSection distribution per pool:")
    for pool in sorted(pool_section_dist):
        total = sum(pool_section_dist[pool].values())
        dist_str = ', '.join(f"{s}={c} ({c/total:.0%})" for s, c in sorted(pool_section_dist[pool].items()))
        print(f"  Pool {pool}: {dist_str}")

    section_control_results['section_per_pool'] = {
        int(p): dict(pool_section_dist[p]) for p in pool_section_dist
    }

    # 4b: Within-Herbal analysis
    # Find PP MIDDLEs with >= MIN_RECORDS Herbal records
    herbal_pp_records = defaultdict(set)
    for mid in filtered_pp:
        for rec in pp_records[mid]:
            if get_record_section(rec) == 'H':
                herbal_pp_records[mid].add(rec)

    herbal_filtered = sorted([mid for mid, recs in herbal_pp_records.items()
                              if len(recs) >= MIN_RECORDS])
    print(f"\nWithin-Herbal: {len(herbal_filtered)} PP with >={MIN_RECORDS} Herbal records")

    if len(herbal_filtered) >= 30:
        # Build Herbal-only Jaccard matrix
        n_h = len(herbal_filtered)
        herbal_mid_to_idx = {mid: i for i, mid in enumerate(herbal_filtered)}
        herbal_jaccard = np.zeros((n_h, n_h))

        for i in range(n_h):
            recs_i = herbal_pp_records[herbal_filtered[i]]
            for j in range(i + 1, n_h):
                recs_j = herbal_pp_records[herbal_filtered[j]]
                inter = len(recs_i & recs_j)
                union = len(recs_i | recs_j)
                if union > 0:
                    jac = inter / union
                    herbal_jaccard[i, j] = jac
                    herbal_jaccard[j, i] = jac
        np.fill_diagonal(herbal_jaccard, 1.0)

        herbal_dist = 1.0 - herbal_jaccard
        np.fill_diagonal(herbal_dist, 0.0)
        herbal_condensed = squareform(herbal_dist)

        # Cluster within Herbal
        Z_h = linkage(herbal_condensed, method='average')
        herbal_sil_scores = {}
        for k in range(2, min(MAX_K + 1, n_h)):
            labels_h = fcluster(Z_h, t=k, criterion='maxclust')
            n_actual = len(set(labels_h))
            if n_actual < 2:
                continue
            try:
                sil_h = silhouette_score(herbal_dist, labels_h, metric='precomputed')
                herbal_sil_scores[k] = float(sil_h)
            except Exception:
                pass

        if herbal_sil_scores:
            herbal_qualifying = {k: s for k, s in herbal_sil_scores.items() if s >= SIL_THRESHOLD}
            if herbal_qualifying:
                herbal_opt_k = max(herbal_qualifying.keys())
                herbal_opt_sil = herbal_qualifying[herbal_opt_k]
            else:
                herbal_opt_k = max(herbal_sil_scores, key=herbal_sil_scores.get)
                herbal_opt_sil = herbal_sil_scores[herbal_opt_k]

            herbal_labels = fcluster(Z_h, t=herbal_opt_k, criterion='maxclust')
            herbal_assignments = {herbal_filtered[i]: int(herbal_labels[i]) for i in range(n_h)}
            herbal_cluster_sizes = Counter(herbal_labels)

            print(f"  Herbal optimal k={herbal_opt_k} (sil={herbal_opt_sil:.4f})")
            print(f"  Meets threshold: {herbal_opt_sil >= SIL_THRESHOLD}")
            print(f"  Cluster sizes: {dict(sorted(herbal_cluster_sizes.items()))}")

            # Consistency: compare full-data pool to Herbal-only pool for shared PP
            overlap_pp = [mid for mid in herbal_filtered if mid in assignments]
            if overlap_pp:
                full_labels = [assignments[mid] for mid in overlap_pp]
                herbal_labels_overlap = [herbal_assignments[mid] for mid in overlap_pp]
                consistency_ari = float(adjusted_rand_score(full_labels, herbal_labels_overlap))
                print(f"  Consistency ARI (full vs herbal-only): {consistency_ari:.4f} (n={len(overlap_pp)})")
            else:
                consistency_ari = None

            section_control_results['within_herbal'] = {
                'n_pp': n_h,
                'optimal_k': herbal_opt_k,
                'optimal_silhouette': herbal_opt_sil,
                'meets_threshold': herbal_opt_sil >= SIL_THRESHOLD,
                'silhouette_scores': herbal_sil_scores,
                'cluster_sizes': {int(k): int(v) for k, v in herbal_cluster_sizes.items()},
                'consistency_ari': consistency_ari,
                'n_overlap': len(overlap_pp) if overlap_pp else 0,
                'cluster_assignments': herbal_assignments,
            }
        else:
            print("  No valid Herbal silhouette scores")
            section_control_results['within_herbal'] = {'error': 'no_valid_silhouette'}
    else:
        print(f"  GUARD: Only {len(herbal_filtered)} Herbal PP (< 30), descriptive only")
        section_control_results['within_herbal'] = {
            'guard': True,
            'n_pp': len(herbal_filtered),
            'note': 'insufficient_herbal_pp'
        }

    # 4c: Section NMI - do pools predict section membership?
    # For each PP, compute dominant section (most records in which section)
    pp_dominant_section = {}
    for mid in filtered_pp:
        sec_counts = Counter()
        for rec in pp_records[mid]:
            sec_counts[get_record_section(rec)] += 1
        pp_dominant_section[mid] = sec_counts.most_common(1)[0][0]

    section_labels = [pp_dominant_section[mid] for mid in filtered_pp]
    nmi_section = float(normalized_mutual_info_score(pool_labels, section_labels))
    print(f"\n  NMI (pool, dominant section): {nmi_section:.4f}")
    section_control_results['nmi_with_section'] = nmi_section
    section_control_results['section_driven'] = nmi_section > 0.8


# ---------------------------------------------------------------------------
# Section 6: Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY SCORECARD")
print("=" * 70)

# Determine verdict
if 'cluster_assignments' in primary_result:
    opt_k = primary_result['optimal_k']
    opt_sil = primary_result['optimal_silhouette']
    meets = primary_result['meets_threshold']

    if meets:
        if alignment_results.get('material_class', {}).get('nmi', 0) > 0.8:
            verdict = 'MATERIAL_REDUNDANT'
        elif section_control_results.get('section_driven', False):
            verdict = 'SECTION_DRIVEN'
        else:
            verdict = 'POOLS_FOUND'
    else:
        verdict = 'CONTINUOUS'

    print(f"Optimal k: {opt_k}")
    print(f"Silhouette: {opt_sil:.4f} (threshold: {SIL_THRESHOLD})")
    print(f"Meets threshold: {meets}")
    print(f"Material NMI: {alignment_results.get('material_class', {}).get('nmi', 'N/A')}")
    print(f"Pathway NMI: {alignment_results.get('pathway', {}).get('nmi', 'N/A')}")
    print(f"Lane NMI: {alignment_results.get('lane_character', {}).get('nmi', 'N/A')}")
    print(f"Section NMI: {section_control_results.get('nmi_with_section', 'N/A')}")
    herbal_info = section_control_results.get('within_herbal', {})
    if 'optimal_k' in herbal_info:
        print(f"Within-Herbal k: {herbal_info['optimal_k']} (sil={herbal_info['optimal_silhouette']:.4f})")
    print(f"\nVERDICT: {verdict}")
else:
    verdict = 'ERROR'
    print("No clustering produced")

# Save results
output = {
    'metadata': {
        'phase': 'PP_POOL_CLASSIFICATION',
        'script': 'pp_cooccurrence_clustering.py',
        'n_pp_total': len(pp_set),
        'n_filtered': len(filtered_pp),
        'n_excluded': len(excluded_pp),
        'min_records': MIN_RECORDS,
        'max_k': MAX_K,
        'silhouette_threshold': SIL_THRESHOLD,
    },
    'cooccurrence_matrix': cooccurrence_results,
    'hierarchical_clustering': hierarchical_results,
    'attribute_alignment': alignment_results if isinstance(alignment_results, dict) else {},
    'section_control': section_control_results,
    'verdict': verdict,
}

with open(RESULTS_DIR / 'pp_cooccurrence_clustering.json', 'w') as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_DIR / 'pp_cooccurrence_clustering.json'}")
