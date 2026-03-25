#!/usr/bin/env python3
"""
Phase 626 Script 1: PP Jaccard Clustering

Lightweight clustering of 111 A folios by PP MIDDLE Jaccard distance.
Confirms cluster structure exists in the validated feature space (C1706, C1709)
before the bridge decomposition in Script 2.

Tests:
  T1: PP MIDDLE Jaccard distance matrix + hierarchical clustering + permutation null
  T2: Section confound test (H vs P)
  T3: Restricted-PP enrichment by cluster (C1707)
  T4: Cluster characterization (8-category profiles, PREFIX, RI, material overlay)
  T5: RI sharing within vs between clusters
"""

import sys, json, functools, warnings, time, math, random
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore')

from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from scipy import stats

from scripts.voynich import Transcript, Morphology, CategoryClassifier, load_middle_classes
from phases.A_TO_B_BRIDGE_DECOMPOSITION.scripts.shared_626 import (
    PROJECT_ROOT, RESULTS_DIR, N_PERM, RNG,
    CATEGORIES, MATERIAL_CLASSES,
    load_pp_classification, load_a_record_profiles,
    group_records_by_folio, compute_folio_pp_set_from_profiles,
    compute_folio_ri_set, get_a_folio_section,
    jaccard_similarity, jsd, cosine_sim, cohens_d, round_floats,
)

t0 = time.time()

print("=" * 70)
print("Phase 626 Script 1: PP Jaccard Clustering")
print("=" * 70)

# ============================================================
# STAGE 0: Data Loading
# ============================================================

tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
ri_middles, pp_middles = load_middle_classes()
pp_class = load_pp_classification()
records = load_a_record_profiles()
bridge_set_path = (PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' /
                   'results' / 'bridge_selection.json')
with open(bridge_set_path) as f:
    bdata = json.load(f)
bridge_set = set(bdata['t5_structural_profile']['bridge_middles'])

dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
with open(dark_path) as f:
    ddata = json.load(f)
dark_set = set(ddata['middles'])

folio_records = group_records_by_folio(records)
a_folios = sorted(folio_records.keys())
n_folios = len(a_folios)
print(f"\n  A folios: {n_folios}")

# ============================================================
# STAGE 1: Per-folio PP MIDDLE sets
# ============================================================

print("\n[T1] Computing PP MIDDLE Jaccard distance matrix...")

folio_pp_sets = {}
folio_sections = {}
for folio in a_folios:
    folio_pp_sets[folio] = compute_folio_pp_set_from_profiles(folio_records[folio])
    folio_sections[folio] = get_a_folio_section(folio)

pp_sizes = [len(folio_pp_sets[f]) for f in a_folios]
print(f"  PP set sizes: mean={np.mean(pp_sizes):.1f}, median={np.median(pp_sizes):.0f}, "
      f"range=[{min(pp_sizes)}, {max(pp_sizes)}]")

# Compute Jaccard distance matrix
dist_matrix = np.zeros((n_folios, n_folios))
for i in range(n_folios):
    for j in range(i + 1, n_folios):
        jacc = jaccard_similarity(folio_pp_sets[a_folios[i]], folio_pp_sets[a_folios[j]])
        dist = 1.0 - jacc
        dist_matrix[i, j] = dist
        dist_matrix[j, i] = dist

# Flatten for clustering
dist_flat = squareform(dist_matrix)

print(f"  Mean Jaccard distance: {np.mean(dist_flat):.4f}")
print(f"  Distance range: [{np.min(dist_flat):.4f}, {np.max(dist_flat):.4f}]")

# Hierarchical clustering
Z = linkage(dist_flat, method='ward')

# Silhouette analysis for k=2..8
from sklearn.metrics import silhouette_score

silhouette_results = {}
for k in range(2, 9):
    labels = fcluster(Z, k, criterion='maxclust')
    sil = silhouette_score(dist_matrix, labels, metric='precomputed')
    silhouette_results[k] = float(sil)
    print(f"  k={k}: silhouette={sil:.4f}")

best_k = max(silhouette_results, key=silhouette_results.get)
best_sil = silhouette_results[best_k]
print(f"  Best k={best_k}, silhouette={best_sil:.4f}")

# Permutation null: shuffle PP MIDDLEs across folios preserving sizes
print(f"\n  Running permutation null ({N_PERM} reps)...")
all_pp_pool = []
for f in a_folios:
    all_pp_pool.extend(list(folio_pp_sets[f]))
all_pp_unique = list(set(all_pp_pool))

null_silhouettes = []
rng = random.Random(626)
for rep in range(min(N_PERM, 500)):
    # Shuffle: randomly assign PP MIDDLEs to folios preserving sizes
    shuffled_pool = all_pp_unique[:]
    rng.shuffle(shuffled_pool)
    null_sets = {}
    idx = 0
    for f in a_folios:
        size = len(folio_pp_sets[f])
        # Sample 'size' MIDDLEs from pool (with replacement to handle size > pool)
        null_sets[f] = set(rng.choices(all_pp_unique, k=size))

    null_dist = np.zeros((n_folios, n_folios))
    for i in range(n_folios):
        for j in range(i + 1, n_folios):
            jacc = jaccard_similarity(null_sets[a_folios[i]], null_sets[a_folios[j]])
            null_dist[i, j] = 1.0 - jacc
            null_dist[j, i] = 1.0 - jacc

    null_flat = squareform(null_dist)
    null_Z = linkage(null_flat, method='ward')
    null_labels = fcluster(null_Z, best_k, criterion='maxclust')
    null_sil = silhouette_score(null_dist, null_labels, metric='precomputed')
    null_silhouettes.append(null_sil)

null_p95 = float(np.percentile(null_silhouettes, 95))
null_mean = float(np.mean(null_silhouettes))
exceeds_null = best_sil > null_p95
print(f"  Null silhouette: mean={null_mean:.4f}, p95={null_p95:.4f}")
print(f"  Observed ({best_sil:.4f}) exceeds p95: {exceeds_null}")

# Final cluster labels
final_labels = fcluster(Z, best_k, criterion='maxclust')
folio_cluster = {a_folios[i]: int(final_labels[i]) for i in range(n_folios)}

cluster_sizes = Counter(final_labels)
print(f"\n  Cluster sizes: {dict(sorted(cluster_sizes.items()))}")

# ============================================================
# T2: Section confound test
# ============================================================

print("\n[T2] Section confound test...")

# Chi-squared: cluster x section
section_counts = defaultdict(lambda: defaultdict(int))
for f in a_folios:
    section_counts[folio_cluster[f]][folio_sections[f]] += 1

# Build contingency table
sections = sorted(set(folio_sections.values()))
clusters = sorted(set(final_labels))
contingency = np.zeros((len(clusters), len(sections)), dtype=int)
for i, c in enumerate(clusters):
    for j, s in enumerate(sections):
        contingency[i, j] = section_counts[c][s]

chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency)
n_total = contingency.sum()
cramers_v = float(np.sqrt(chi2 / (n_total * (min(contingency.shape) - 1)))) if n_total > 0 else 0.0

print(f"  Chi-squared: {chi2:.2f}, p={p_chi2:.6f}")
print(f"  Cramer's V: {cramers_v:.4f}")
print(f"  Section distribution per cluster:")
for c in clusters:
    h_count = section_counts[c]['H']
    p_count = section_counts[c]['P']
    print(f"    Cluster {c}: H={h_count}, P={p_count}")

# Within-H clustering
h_folios = [f for f in a_folios if folio_sections[f] == 'H']
h_indices = [a_folios.index(f) for f in h_folios]
n_h = len(h_folios)
print(f"\n  Within-H analysis (n={n_h})...")

if n_h > 10:
    h_dist = np.zeros((n_h, n_h))
    for i in range(n_h):
        for j in range(i + 1, n_h):
            jacc = jaccard_similarity(folio_pp_sets[h_folios[i]], folio_pp_sets[h_folios[j]])
            h_dist[i, j] = 1.0 - jacc
            h_dist[j, i] = 1.0 - jacc

    h_flat = squareform(h_dist)
    h_Z = linkage(h_flat, method='ward')

    h_sil_results = {}
    for k in range(2, min(9, n_h)):
        h_labels = fcluster(h_Z, k, criterion='maxclust')
        h_sil = silhouette_score(h_dist, h_labels, metric='precomputed')
        h_sil_results[k] = float(h_sil)

    h_best_k = max(h_sil_results, key=h_sil_results.get)
    h_best_sil = h_sil_results[h_best_k]
    print(f"  Within-H best k={h_best_k}, silhouette={h_best_sil:.4f}")
    within_h_persists = h_best_sil > 0.10
else:
    h_sil_results = {}
    h_best_k = 0
    h_best_sil = 0.0
    within_h_persists = False

# ============================================================
# T3: Restricted-PP enrichment by cluster
# ============================================================

print("\n[T3] Restricted-PP enrichment...")

# Count how many folios each PP MIDDLE appears on
pp_folio_counts = Counter()
for f in a_folios:
    for mid in folio_pp_sets[f]:
        pp_folio_counts[mid] += 1

restricted_pps = {mid for mid, count in pp_folio_counts.items() if count <= 2}
print(f"  Restricted PPs (<=2 folios): {len(restricted_pps)} / {len(pp_folio_counts)}")

# Per-cluster restricted-PP density
cluster_restricted_density = {}
cluster_restricted_values = defaultdict(list)
for c in clusters:
    c_folios = [f for f in a_folios if folio_cluster[f] == c]
    densities = []
    for f in c_folios:
        pp_set = folio_pp_sets[f]
        if len(pp_set) > 0:
            density = len(pp_set & restricted_pps) / len(pp_set)
        else:
            density = 0.0
        densities.append(density)
        cluster_restricted_values[c].append(density)
    cluster_restricted_density[c] = float(np.mean(densities)) if densities else 0.0
    print(f"  Cluster {c}: restricted density = {cluster_restricted_density[c]:.4f} (n={len(c_folios)})")

# KW test
if len(clusters) >= 2:
    kw_groups = [cluster_restricted_values[c] for c in clusters if len(cluster_restricted_values[c]) > 0]
    if len(kw_groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*kw_groups)
    else:
        kw_stat, kw_p = 0.0, 1.0
else:
    kw_stat, kw_p = 0.0, 1.0
print(f"  KW test: H={kw_stat:.4f}, p={kw_p:.6f}")

# ============================================================
# T4: Cluster characterization (DESCRIPTORS)
# ============================================================

print("\n[T4] Cluster characterization...")

# Category profiles per cluster
print("  Computing category profiles per cluster...")
cluster_cat_profiles = {}
for c in clusters:
    c_folios = [f for f in a_folios if folio_cluster[f] == c]
    cat_counts = Counter()
    total = 0
    for f in c_folios:
        for rec in folio_records[f]:
            for tok in rec.get('pp_tokens', []):
                m = morph.extract(tok)
                if m.middle:
                    cat = cc.classify(m.middle)
                    if cat in CATEGORIES:
                        cat_counts[cat] += 1
                        total += 1
    if total > 0:
        profile = {cat: cat_counts[cat] / total for cat in CATEGORIES}
    else:
        profile = {cat: 0.0 for cat in CATEGORIES}
    cluster_cat_profiles[c] = profile

for c in clusters:
    top_cats = sorted(cluster_cat_profiles[c].items(), key=lambda x: -x[1])[:3]
    top_str = ", ".join(f"{cat}={frac:.3f}" for cat, frac in top_cats)
    print(f"  Cluster {c}: {top_str}")

# PREFIX profiles per cluster
print("  Computing PREFIX profiles per cluster...")
prefix_families = ['qo', 'ch_sh', 'ok_ot', 'da', 'ol_or']
cluster_prefix_profiles = {}
cluster_prefix_values = {pf: defaultdict(list) for pf in prefix_families}

for c in clusters:
    c_folios = [f for f in a_folios if folio_cluster[f] == c]
    prefix_sums = {pf: 0.0 for pf in prefix_families}
    n_recs = 0
    for f in c_folios:
        for rec in folio_records[f]:
            npp = rec.get('normalized_prefix_profile', {})
            if npp:
                for pf in prefix_families:
                    prefix_sums[pf] += npp.get(pf, 0.0)
                n_recs += 1
    if n_recs > 0:
        cluster_prefix_profiles[c] = {pf: prefix_sums[pf] / n_recs for pf in prefix_families}
    else:
        cluster_prefix_profiles[c] = {pf: 0.0 for pf in prefix_families}

    # Collect per-folio values for KW test
    for f in c_folios:
        f_prefix = {pf: 0.0 for pf in prefix_families}
        f_n = 0
        for rec in folio_records[f]:
            npp = rec.get('normalized_prefix_profile', {})
            if npp:
                for pf in prefix_families:
                    f_prefix[pf] += npp.get(pf, 0.0)
                f_n += 1
        if f_n > 0:
            for pf in prefix_families:
                cluster_prefix_values[pf][c].append(f_prefix[pf] / f_n)

# KW test per prefix family
prefix_kw = {}
for pf in prefix_families:
    groups = [cluster_prefix_values[pf][c] for c in clusters if len(cluster_prefix_values[pf][c]) > 0]
    if len(groups) >= 2:
        h_stat, p_val = stats.kruskal(*groups)
        prefix_kw[pf] = {'H': float(h_stat), 'p': float(p_val)}
    else:
        prefix_kw[pf] = {'H': 0.0, 'p': 1.0}
    print(f"  PREFIX {pf}: H={prefix_kw[pf]['H']:.2f}, p={prefix_kw[pf]['p']:.6f}")

# RI diversity per cluster
cluster_ri_stats = {}
for c in clusters:
    c_folios = [f for f in a_folios if folio_cluster[f] == c]
    ri_counts = []
    for f in c_folios:
        ri_set = compute_folio_ri_set(folio_records[f])
        ri_counts.append(len(ri_set))
    cluster_ri_stats[c] = {'mean': float(np.mean(ri_counts)), 'median': float(np.median(ri_counts))}
    print(f"  Cluster {c} RI diversity: mean={cluster_ri_stats[c]['mean']:.1f}")

# Material overlay per cluster (Tier 3)
cluster_material_profiles = {}
for c in clusters:
    c_folios = [f for f in a_folios if folio_cluster[f] == c]
    mat_counts = Counter()
    total = 0
    for f in c_folios:
        for rec in folio_records[f]:
            for tok in rec.get('pp_tokens', []):
                m = morph.extract(tok)
                if m.middle and m.middle in pp_class:
                    mat_counts[pp_class[m.middle]['material_class']] += 1
                    total += 1
    if total > 0:
        profile = {mc: mat_counts[mc] / total for mc in MATERIAL_CLASSES}
    else:
        profile = {mc: 0.0 for mc in MATERIAL_CLASSES}
    cluster_material_profiles[c] = profile

# ============================================================
# T5: RI sharing within vs between clusters
# ============================================================

print("\n[T5] RI sharing within vs between clusters...")

folio_ri_sets = {}
for f in a_folios:
    folio_ri_sets[f] = compute_folio_ri_set(folio_records[f])

# Compute within-cluster and between-cluster RI Jaccard
within_jaccards = []
between_jaccards = []

for i in range(n_folios):
    for j in range(i + 1, n_folios):
        fi, fj = a_folios[i], a_folios[j]
        jacc = jaccard_similarity(folio_ri_sets[fi], folio_ri_sets[fj])
        if folio_cluster[fi] == folio_cluster[fj]:
            within_jaccards.append(jacc)
        else:
            between_jaccards.append(jacc)

within_mean = float(np.mean(within_jaccards)) if within_jaccards else 0.0
between_mean = float(np.mean(between_jaccards)) if between_jaccards else 0.0
ri_ratio = within_mean / between_mean if between_mean > 0 else 0.0

print(f"  Within-cluster RI Jaccard: {within_mean:.6f} (n={len(within_jaccards)})")
print(f"  Between-cluster RI Jaccard: {between_mean:.6f} (n={len(between_jaccards)})")
print(f"  Ratio: {ri_ratio:.4f}")

# Permutation test
print(f"  Running permutation test ({min(N_PERM, 500)} reps)...")
null_ratios = []
rng2 = random.Random(6260)
for _ in range(min(N_PERM, 500)):
    shuffled_labels = list(final_labels)
    rng2.shuffle(shuffled_labels)
    null_cluster = {a_folios[i]: shuffled_labels[i] for i in range(n_folios)}

    null_within = []
    null_between = []
    for i in range(n_folios):
        for j in range(i + 1, n_folios):
            fi, fj = a_folios[i], a_folios[j]
            jacc = jaccard_similarity(folio_ri_sets[fi], folio_ri_sets[fj])
            if null_cluster[fi] == null_cluster[fj]:
                null_within.append(jacc)
            else:
                null_between.append(jacc)

    nw_mean = np.mean(null_within) if null_within else 0.0
    nb_mean = np.mean(null_between) if null_between else 0.0
    null_ratios.append(nw_mean / nb_mean if nb_mean > 0 else 0.0)

perm_p = float(np.mean([1 if nr >= ri_ratio else 0 for nr in null_ratios]))
print(f"  Permutation p: {perm_p:.4f}")

# ============================================================
# OUTPUT
# ============================================================

elapsed = time.time() - t0
print(f"\n  Total time: {elapsed:.1f}s")

output = {
    'metadata': {
        'phase': 626,
        'script': 1,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'n_folios': n_folios,
        'n_pp_middles': len(pp_folio_counts),
        'elapsed_s': round(elapsed, 1),
    },
    'T1_pp_clustering': {
        'mean_jaccard_distance': float(np.mean(dist_flat)),
        'distance_range': [float(np.min(dist_flat)), float(np.max(dist_flat))],
        'silhouette_by_k': {str(k): round(v, 6) for k, v in silhouette_results.items()},
        'best_k': best_k,
        'best_silhouette': round(best_sil, 6),
        'null_silhouette_mean': round(null_mean, 6),
        'null_silhouette_p95': round(null_p95, 6),
        'exceeds_null_p95': exceeds_null,
        'cluster_sizes': {str(c): int(n) for c, n in sorted(cluster_sizes.items())},
        'folio_cluster': {f: int(c) for f, c in sorted(folio_cluster.items())},
    },
    'T2_section_confound': {
        'chi2': round(chi2, 4),
        'p': round(p_chi2, 6),
        'cramers_v': round(cramers_v, 4),
        'section_per_cluster': {str(c): dict(section_counts[c]) for c in clusters},
        'within_h': {
            'n_folios': n_h,
            'silhouette_by_k': {str(k): round(v, 6) for k, v in h_sil_results.items()},
            'best_k': h_best_k,
            'best_silhouette': round(h_best_sil, 6),
            'persists': within_h_persists,
        },
    },
    'T3_restricted_pp': {
        'n_restricted': len(restricted_pps),
        'n_total_pp': len(pp_folio_counts),
        'density_by_cluster': {str(c): round(v, 6) for c, v in cluster_restricted_density.items()},
        'kw_H': round(kw_stat, 4),
        'kw_p': round(kw_p, 6),
    },
    'T4_characterization': {
        'category_profiles': {str(c): round_floats(p) for c, p in cluster_cat_profiles.items()},
        'prefix_profiles': {str(c): round_floats(p) for c, p in cluster_prefix_profiles.items()},
        'prefix_kw': round_floats(prefix_kw),
        'ri_diversity': round_floats(cluster_ri_stats),
        'material_overlay': {str(c): round_floats(p) for c, p in cluster_material_profiles.items()},
    },
    'T5_ri_sharing': {
        'within_mean': round(within_mean, 6),
        'between_mean': round(between_mean, 6),
        'ratio': round(ri_ratio, 4),
        'n_within': len(within_jaccards),
        'n_between': len(between_jaccards),
        'permutation_p': round(perm_p, 4),
    },
}

def sanitize_for_json(obj):
    """Recursively convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, dict):
        return {str(k) if not isinstance(k, str) else k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(x) for x in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
with open(RESULTS_DIR / 'pp_clustering.json', 'w') as f:
    json.dump(sanitize_for_json(output), f, indent=2)

print(f"\n  Output: {RESULTS_DIR / 'pp_clustering.json'}")
print("  DONE")
