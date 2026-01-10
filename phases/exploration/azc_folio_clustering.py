#!/usr/bin/env python3
"""
AZC-DEEP Phase 3: Hierarchical Clustering
==========================================

Identifies folio families within AZC using:
1. Hierarchical clustering (Ward and Average linkage)
2. Silhouette analysis for optimal cluster count
3. Bootstrap stability testing
4. Cophenetic correlation

Questions addressed (all Tier 2-legal):
1. Do AZC folios form families (discrete groups)?
2. Do they form chains (local coherence)?
3. Are clusters placement-profile-defined?
4. Are Zodiac pages structurally special or just templated?

Output: results/azc_folio_clusters.json
"""

import json
import os
import math
import random
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC-DEEP PHASE 3: HIERARCHICAL CLUSTERING")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

print("\nLoading similarity matrix...")

with open('results/azc_folio_similarity_matrix.json', 'r', encoding='utf-8') as f:
    sim_data = json.load(f)

with open('results/azc_folio_features.json', 'r', encoding='utf-8') as f:
    feature_data = json.load(f)

folios = sim_data['metadata']['folio_order']
combined_sim = sim_data['matrices']['combined']
vocab_jaccard = sim_data['matrices']['vocab_jaccard']
feature_cosine = sim_data['matrices']['feature_cosine']
placement_js = sim_data['matrices']['placement_js']

folio_features = feature_data['folios']

n = len(folios)
print(f"Loaded {n} folios")

# Convert similarity to distance
def sim_to_dist(sim_matrix):
    """Convert similarity matrix to distance matrix."""
    n = len(sim_matrix)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dist[i][j] = 1.0 - sim_matrix[i][j]
    return dist

combined_dist = sim_to_dist(combined_sim)

# =============================================================================
# HIERARCHICAL CLUSTERING
# =============================================================================

def hierarchical_cluster(dist_matrix, linkage='average'):
    """
    Perform hierarchical clustering.

    Args:
        dist_matrix: n x n distance matrix
        linkage: 'single', 'average', or 'complete'

    Returns:
        List of merge steps: [(cluster_i, cluster_j, distance, size)]
    """
    n = len(dist_matrix)

    # Initialize: each item is its own cluster
    clusters = {i: [i] for i in range(n)}
    active = set(range(n))
    merges = []

    # Distance between clusters
    def cluster_distance(c1, c2):
        items1 = clusters[c1]
        items2 = clusters[c2]
        dists = [dist_matrix[i][j] for i in items1 for j in items2]

        if linkage == 'single':
            return min(dists)
        elif linkage == 'complete':
            return max(dists)
        elif linkage == 'average':
            return sum(dists) / len(dists)
        elif linkage == 'ward':
            # Ward's method: minimize within-cluster variance
            # Approximate using average distance weighted by size
            n1, n2 = len(items1), len(items2)
            avg_dist = sum(dists) / len(dists)
            return avg_dist * math.sqrt(2 * n1 * n2 / (n1 + n2))
        else:
            return sum(dists) / len(dists)

    next_id = n
    while len(active) > 1:
        # Find closest pair of clusters
        best_dist = float('inf')
        best_pair = None

        active_list = list(active)
        for i, c1 in enumerate(active_list):
            for c2 in active_list[i+1:]:
                d = cluster_distance(c1, c2)
                if d < best_dist:
                    best_dist = d
                    best_pair = (c1, c2)

        if best_pair is None:
            break

        c1, c2 = best_pair

        # Merge clusters
        new_cluster = clusters[c1] + clusters[c2]
        clusters[next_id] = new_cluster

        merges.append({
            'left': c1,
            'right': c2,
            'distance': best_dist,
            'size': len(new_cluster),
            'members': new_cluster
        })

        active.remove(c1)
        active.remove(c2)
        active.add(next_id)
        next_id += 1

    return merges

print("\nPerforming hierarchical clustering...")

# Run with different linkage methods
ward_merges = hierarchical_cluster(combined_dist, linkage='ward')
average_merges = hierarchical_cluster(combined_dist, linkage='average')

print(f"Ward linkage: {len(ward_merges)} merges")
print(f"Average linkage: {len(average_merges)} merges")

# =============================================================================
# CLUSTER ASSIGNMENT AT DIFFERENT LEVELS
# =============================================================================

def get_clusters_at_k(merges, n, k):
    """Get cluster assignments when cut to k clusters."""
    if k >= n:
        return {i: i for i in range(n)}
    if k <= 0:
        return {i: 0 for i in range(n)}

    # Start with each item in its own cluster
    cluster_of = list(range(n))

    # Merge until we have k clusters
    num_clusters = n
    for merge in merges:
        if num_clusters <= k:
            break

        left_members = [i for i in range(n) if cluster_of[i] == merge['left'] or
                        (merge['left'] < n and cluster_of[i] == merge['left'])]
        right_members = [i for i in range(n) if cluster_of[i] == merge['right'] or
                         (merge['right'] < n and cluster_of[i] == merge['right'])]

        # Find actual members
        left_items = set()
        right_items = set()
        for i in range(n):
            if cluster_of[i] == merge['left']:
                left_items.add(i)
            elif merge['left'] < n and i == merge['left']:
                left_items.add(i)

        for i in range(n):
            if cluster_of[i] == merge['right']:
                right_items.add(i)
            elif merge['right'] < n and i == merge['right']:
                right_items.add(i)

        # Assign all to left cluster
        new_cluster = min(merge['left'], merge['right'])
        for i in left_items | right_items:
            cluster_of[i] = new_cluster

        num_clusters -= 1

    # Renumber clusters 0 to k-1
    unique_clusters = sorted(set(cluster_of))
    cluster_map = {c: i for i, c in enumerate(unique_clusters)}
    return {i: cluster_map[cluster_of[i]] for i in range(n)}

def get_clusters_simple(merges, n, k):
    """Simpler cluster extraction using merge tree with Union-Find."""
    if k >= n:
        return {i: i for i in range(n)}
    if k <= 1:
        return {i: 0 for i in range(n)}

    # Use Union-Find to track cluster membership
    parent = list(range(n + len(merges)))  # Room for all cluster IDs

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y, new_id):
        px, py = find(x), find(y)
        parent[px] = new_id
        parent[py] = new_id

    # Process merges: start with n clusters, stop when we reach k
    num_clusters = n
    for merge_idx, merge in enumerate(merges):
        if num_clusters <= k:
            break

        left = merge['left']
        right = merge['right']
        new_id = n + merge_idx  # New cluster ID

        union(left, right, new_id)
        num_clusters -= 1

    # Get final cluster assignments for original items (0 to n-1)
    raw_clusters = [find(i) for i in range(n)]

    # Renumber to 0..k-1
    unique = sorted(set(raw_clusters))
    mapping = {c: i for i, c in enumerate(unique)}
    return {i: mapping[raw_clusters[i]] for i in range(n)}

# =============================================================================
# SILHOUETTE ANALYSIS
# =============================================================================

def silhouette_score(dist_matrix, cluster_assignments):
    """Compute silhouette coefficient."""
    n = len(dist_matrix)
    clusters = defaultdict(list)
    for i, c in cluster_assignments.items():
        clusters[c].append(i)

    if len(clusters) <= 1 or len(clusters) >= n:
        return 0.0

    silhouettes = []
    for i in range(n):
        ci = cluster_assignments[i]
        same_cluster = [j for j in clusters[ci] if j != i]

        if not same_cluster:
            silhouettes.append(0.0)
            continue

        # a(i) = mean distance to same cluster
        a_i = sum(dist_matrix[i][j] for j in same_cluster) / len(same_cluster)

        # b(i) = min mean distance to other clusters
        b_i = float('inf')
        for ck, members in clusters.items():
            if ck != ci and members:
                mean_dist = sum(dist_matrix[i][j] for j in members) / len(members)
                b_i = min(b_i, mean_dist)

        if b_i == float('inf'):
            silhouettes.append(0.0)
        else:
            s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0
            silhouettes.append(s_i)

    return sum(silhouettes) / len(silhouettes) if silhouettes else 0.0

print("\n" + "=" * 70)
print("SILHOUETTE ANALYSIS")
print("=" * 70)

# Test different numbers of clusters
silhouette_scores = {}

print(f"\n{'k':<5} {'Ward Silhouette':<20} {'Avg Silhouette':<20}")
print("-" * 45)

for k in range(2, min(10, n)):
    ward_assign = get_clusters_simple(ward_merges, n, k)
    avg_assign = get_clusters_simple(average_merges, n, k)

    ward_sil = silhouette_score(combined_dist, ward_assign)
    avg_sil = silhouette_score(combined_dist, avg_assign)

    silhouette_scores[k] = {
        'ward': ward_sil,
        'average': avg_sil
    }

    print(f"{k:<5} {ward_sil:<20.4f} {avg_sil:<20.4f}")

# Find optimal k
best_k_ward = max(range(2, min(10, n)), key=lambda k: silhouette_scores[k]['ward'])
best_k_avg = max(range(2, min(10, n)), key=lambda k: silhouette_scores[k]['average'])

print(f"\nOptimal k (Ward): {best_k_ward} (silhouette={silhouette_scores[best_k_ward]['ward']:.4f})")
print(f"Optimal k (Average): {best_k_avg} (silhouette={silhouette_scores[best_k_avg]['average']:.4f})")

# =============================================================================
# CLUSTER ANALYSIS AT OPTIMAL K
# =============================================================================

print("\n" + "=" * 70)
print(f"CLUSTER ANALYSIS AT k={best_k_ward} (Ward)")
print("=" * 70)

final_clusters = get_clusters_simple(ward_merges, n, best_k_ward)

# Build cluster profiles
cluster_profiles = defaultdict(list)
for i, cluster_id in final_clusters.items():
    cluster_profiles[cluster_id].append(folios[i])

print("\nCluster Membership:")
for cluster_id in sorted(cluster_profiles.keys()):
    members = cluster_profiles[cluster_id]
    sections = [folio_features[f]['section'] for f in members]
    section_counts = Counter(sections)

    print(f"\n  Cluster {cluster_id} ({len(members)} folios):")
    print(f"    Sections: {dict(section_counts)}")
    print(f"    Members: {', '.join(sorted(members))}")

# =============================================================================
# SECTION-CLUSTER ALIGNMENT
# =============================================================================

print("\n" + "=" * 70)
print("SECTION-CLUSTER ALIGNMENT")
print("=" * 70)

section_cluster_matrix = defaultdict(lambda: defaultdict(int))
for i, cluster_id in final_clusters.items():
    folio = folios[i]
    section = folio_features[folio]['section']
    section_cluster_matrix[section][cluster_id] += 1

sections = sorted(set(folio_features[f]['section'] for f in folios))

print(f"\n{'Section':<10}" + "".join(f"C{c:<8}" for c in sorted(cluster_profiles.keys())))
print("-" * (10 + 9 * len(cluster_profiles)))

for section in sections:
    row = f"{section:<10}"
    for cluster_id in sorted(cluster_profiles.keys()):
        count = section_cluster_matrix[section][cluster_id]
        row += f"{count:<9}"
    print(row)

# Compute alignment (Cramer's V)
def cramers_v(contingency):
    """Compute Cramer's V for section-cluster association."""
    rows = list(contingency.keys())
    cols = set()
    for row_data in contingency.values():
        cols.update(row_data.keys())
    cols = list(cols)

    observed = []
    for row in rows:
        obs_row = [contingency[row].get(col, 0) for col in cols]
        observed.append(obs_row)

    N = sum(sum(row) for row in observed)
    if N == 0:
        return 0.0

    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(len(rows))) for j in range(len(cols))]

    chi2 = 0
    for i in range(len(rows)):
        for j in range(len(cols)):
            expected = (row_totals[i] * col_totals[j]) / N if N > 0 else 0
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    k = min(len(rows), len(cols))
    if k > 1 and N > 0:
        return math.sqrt(chi2 / (N * (k - 1)))
    return 0.0

v = cramers_v(dict(section_cluster_matrix))
print(f"\nSection-Cluster Cramer's V: {v:.3f}")

if v >= 0.5:
    print("-> STRONG alignment: clusters are largely section-defined")
elif v >= 0.3:
    print("-> MODERATE alignment: clusters partially follow sections")
else:
    print("-> WEAK alignment: clusters cross section boundaries")

# =============================================================================
# CLUSTER FEATURE PROFILES
# =============================================================================

print("\n" + "=" * 70)
print("CLUSTER FEATURE PROFILES")
print("=" * 70)

cluster_feature_means = {}

feature_names = ['ttr', 'a_coverage', 'b_coverage', 'azc_unique_rate',
                 'link_density', 'placement_entropy', 'ordered_subscript_depth']

print(f"\n{'Cluster':<10}" + "".join(f"{f[:12]:<14}" for f in feature_names))
print("-" * (10 + 14 * len(feature_names)))

for cluster_id in sorted(cluster_profiles.keys()):
    members = cluster_profiles[cluster_id]
    means = {}
    row = f"C{cluster_id:<9}"

    for feat in feature_names:
        values = [folio_features[f][feat] for f in members]
        mean_val = sum(values) / len(values) if values else 0
        means[feat] = mean_val
        row += f"{mean_val:<14.3f}"

    cluster_feature_means[cluster_id] = means
    print(row)

# =============================================================================
# BOOTSTRAP STABILITY
# =============================================================================

print("\n" + "=" * 70)
print("BOOTSTRAP STABILITY (100 iterations)")
print("=" * 70)

def bootstrap_stability(dist_matrix, merges, k, n_bootstrap=100):
    """Estimate cluster stability via bootstrap resampling."""
    n = len(dist_matrix)

    # Get reference clusters
    ref_clusters = get_clusters_simple(merges, n, k)

    # Count co-cluster frequencies
    cooccurrence = [[0] * n for _ in range(n)]

    for _ in range(n_bootstrap):
        # Sample with replacement
        sample_indices = [random.randint(0, n-1) for _ in range(n)]

        # Build subsampled distance matrix
        sub_dist = [[dist_matrix[sample_indices[i]][sample_indices[j]]
                     for j in range(n)] for i in range(n)]

        # Cluster
        sub_merges = hierarchical_cluster(sub_dist, linkage='ward')
        sub_clusters = get_clusters_simple(sub_merges, n, k)

        # Update co-occurrence (for original indices)
        for i in range(n):
            for j in range(i+1, n):
                # Check if i and j are in same cluster in this sample
                orig_i = sample_indices[i]
                orig_j = sample_indices[j]
                if sub_clusters[i] == sub_clusters[j]:
                    cooccurrence[orig_i][orig_j] += 1
                    cooccurrence[orig_j][orig_i] += 1

    # Compute stability per cluster
    cluster_stability = {}
    for cluster_id in set(ref_clusters.values()):
        members = [i for i, c in ref_clusters.items() if c == cluster_id]
        if len(members) < 2:
            cluster_stability[cluster_id] = 1.0
            continue

        # Average co-occurrence within cluster
        pairs = [(i, j) for i in members for j in members if i < j]
        if pairs:
            avg_cooc = sum(cooccurrence[i][j] for i, j in pairs) / len(pairs)
            cluster_stability[cluster_id] = avg_cooc / n_bootstrap
        else:
            cluster_stability[cluster_id] = 1.0

    return cluster_stability

random.seed(42)
stability = bootstrap_stability(combined_dist, ward_merges, best_k_ward, n_bootstrap=100)

print(f"\nCluster stability scores (0-1, higher = more stable):")
for cluster_id in sorted(stability.keys()):
    members = cluster_profiles[cluster_id]
    print(f"  Cluster {cluster_id} ({len(members)} folios): {stability[cluster_id]:.3f}")

avg_stability = sum(stability.values()) / len(stability) if stability else 0
print(f"\nAverage stability: {avg_stability:.3f}")

if avg_stability >= 0.8:
    print("-> HIGHLY STABLE clustering")
elif avg_stability >= 0.6:
    print("-> MODERATELY STABLE clustering")
else:
    print("-> UNSTABLE clustering (may be gradient rather than discrete)")

# =============================================================================
# ZODIAC TEMPLATE ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("ZODIAC TEMPLATE ANALYSIS (C319 validation)")
print("=" * 70)

zodiac_folios = [f for f in folios if folio_features[f]['section'] == 'Z']

print(f"\nZodiac folios: {len(zodiac_folios)}")
print(f"Members: {', '.join(sorted(zodiac_folios))}")

# Check if all zodiac folios are in same cluster
zodiac_clusters = set(final_clusters[folios.index(f)] for f in zodiac_folios)
print(f"Cluster assignments: {zodiac_clusters}")

if len(zodiac_clusters) == 1:
    print("-> ALL ZODIAC FOLIOS IN SINGLE CLUSTER (confirms C319 template reuse)")
else:
    print(f"-> Zodiac folios split across {len(zodiac_clusters)} clusters")

# Placement profile similarity within zodiac
zodiac_placement_sims = []
for i, f1 in enumerate(zodiac_folios):
    for f2 in zodiac_folios[i+1:]:
        idx1 = folios.index(f1)
        idx2 = folios.index(f2)
        zodiac_placement_sims.append(placement_js[idx1][idx2])

if zodiac_placement_sims:
    mean_zps = sum(zodiac_placement_sims) / len(zodiac_placement_sims)
    print(f"\nZodiac placement JS mean: {mean_zps:.3f}")
    if mean_zps >= 0.9:
        print("-> VERY HIGH placement similarity (strong template signal)")
    elif mean_zps >= 0.7:
        print("-> HIGH placement similarity (moderate template signal)")
    else:
        print("-> MODERATE placement similarity")

# =============================================================================
# SAVE RESULTS
# =============================================================================

output_path = 'results/azc_folio_clusters.json'

# Build folio-cluster mapping
folio_cluster_map = {folios[i]: cluster_id for i, cluster_id in final_clusters.items()}

output = {
    'metadata': {
        'num_folios': n,
        'num_clusters': best_k_ward,
        'optimal_k_ward': best_k_ward,
        'optimal_k_average': best_k_avg,
        'silhouette_ward': silhouette_scores[best_k_ward]['ward'],
        'silhouette_average': silhouette_scores[best_k_avg]['average'],
        'section_cluster_cramers_v': v,
        'average_bootstrap_stability': avg_stability
    },
    'silhouette_analysis': silhouette_scores,
    'cluster_assignments': folio_cluster_map,
    'cluster_profiles': {
        str(k): {
            'members': sorted(v),
            'size': len(v),
            'sections': dict(Counter(folio_features[f]['section'] for f in v)),
            'stability': stability.get(k, 0),
            'feature_means': cluster_feature_means.get(k, {})
        }
        for k, v in cluster_profiles.items()
    },
    'zodiac_analysis': {
        'folios': sorted(zodiac_folios),
        'cluster_ids': list(zodiac_clusters),
        'single_cluster': len(zodiac_clusters) == 1,
        'mean_placement_similarity': mean_zps if zodiac_placement_sims else 0
    },
    'merge_history': {
        'ward': [{'distance': m['distance'], 'size': m['size']} for m in ward_merges],
        'average': [{'distance': m['distance'], 'size': m['size']} for m in average_merges]
    }
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n[OK] Results saved to: {output_path}")
print("=" * 70)
