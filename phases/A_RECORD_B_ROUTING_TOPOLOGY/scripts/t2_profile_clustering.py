"""
T2: A-Record Profile Clustering (H1)

Question: Do A-records cluster by B-viability profile?

Method:
1. Load profile vectors from T1
2. Compute pairwise Jaccard similarity
3. Hierarchical clustering
4. Evaluate cluster quality (silhouette score)
5. Test if clusters align with known structure (folio, section)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_score, adjusted_rand_score

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("T2: A-RECORD PROFILE CLUSTERING")
print("=" * 70)

# Load profile vectors
data_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't1_profile_vectors.json'
with open(data_path) as f:
    data = json.load(f)

b_folios = data['b_folios']
profiles = data['profiles']
a_record_pp = data['a_record_pp']

print(f"\nLoaded {len(profiles)} A-record profiles over {len(b_folios)} B-folios")

# Convert to matrix
record_keys = list(profiles.keys())
profile_matrix = np.array([profiles[k] for k in record_keys], dtype=np.float32)

print(f"Profile matrix shape: {profile_matrix.shape}")

# Filter out zero-viability and universal records (no signal)
viability_sizes = profile_matrix.sum(axis=1)
valid_mask = (viability_sizes > 0) & (viability_sizes < len(b_folios))
valid_indices = np.where(valid_mask)[0]

print(f"Valid records (non-zero, non-universal): {len(valid_indices)}")

if len(valid_indices) < 50:
    print("ERROR: Too few valid records for clustering")
    sys.exit(1)

valid_keys = [record_keys[i] for i in valid_indices]
valid_matrix = profile_matrix[valid_indices]

# Compute Jaccard distance
print("\nComputing Jaccard distances...")

def jaccard_distance(u, v):
    """1 - Jaccard similarity"""
    intersection = np.sum(u & v)
    union = np.sum(u | v)
    if union == 0:
        return 1.0
    return 1.0 - (intersection / union)

# Use pdist with custom metric
distances = pdist(valid_matrix.astype(bool), metric='jaccard')
dist_matrix = squareform(distances)

print(f"Distance matrix: {dist_matrix.shape}")
print(f"Mean Jaccard distance: {np.mean(distances):.3f}")

# Hierarchical clustering
print("\nHierarchical clustering...")
Z = linkage(distances, method='average')

# Try different k values
results = {'k_values': {}}
best_k = 2
best_silhouette = -1

for k in [2, 3, 4, 5, 6, 8, 10]:
    labels = fcluster(Z, k, criterion='maxclust')

    # Silhouette score
    if len(set(labels)) > 1:
        sil = silhouette_score(dist_matrix, labels, metric='precomputed')
    else:
        sil = -1

    cluster_sizes = Counter(labels)

    results['k_values'][k] = {
        'silhouette': float(sil),
        'cluster_sizes': {int(k): int(v) for k, v in cluster_sizes.items()},
    }

    print(f"  k={k}: silhouette={sil:.3f}, sizes={dict(cluster_sizes)}")

    if sil > best_silhouette:
        best_silhouette = sil
        best_k = k

print(f"\nBest k={best_k} with silhouette={best_silhouette:.3f}")

# Get best clustering
best_labels = fcluster(Z, best_k, criterion='maxclust')

# Analyze cluster characteristics
print("\n" + "=" * 70)
print("CLUSTER ANALYSIS:")
print("=" * 70)

cluster_profiles = defaultdict(list)
for i, label in enumerate(best_labels):
    cluster_profiles[label].append(valid_keys[i])

for label in sorted(cluster_profiles.keys()):
    members = cluster_profiles[label]
    n = len(members)

    # Mean viability size
    sizes = [sum(profiles[k]) for k in members]
    mean_size = np.mean(sizes)

    # Mean PP count
    pp_counts = [len(a_record_pp[k]) for k in members]
    mean_pp = np.mean(pp_counts)

    # Source folio distribution
    source_folios = [k.split('_')[0] for k in members]
    top_folios = Counter(source_folios).most_common(3)

    print(f"\nCluster {label}: {n} records")
    print(f"  Mean viability: {mean_size:.1f} B-folios")
    print(f"  Mean PP count: {mean_pp:.1f}")
    print(f"  Top source folios: {top_folios}")

# Test cluster differentiation
print("\n" + "=" * 70)
print("CLUSTER DIFFERENTIATION TEST:")
print("=" * 70)

# Within-cluster vs between-cluster Jaccard
within_dists = []
between_dists = []

for i in range(len(valid_indices)):
    for j in range(i + 1, len(valid_indices)):
        d = dist_matrix[i, j]
        if best_labels[i] == best_labels[j]:
            within_dists.append(d)
        else:
            between_dists.append(d)

mean_within = np.mean(within_dists)
mean_between = np.mean(between_dists)
ratio = mean_between / mean_within if mean_within > 0 else 0

print(f"\nMean within-cluster distance: {mean_within:.3f}")
print(f"Mean between-cluster distance: {mean_between:.3f}")
print(f"Ratio (between/within): {ratio:.2f}x")

# Statistical test
stat, p_val = stats.mannwhitneyu(within_dists, between_dists, alternative='less')
sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
print(f"Mann-Whitney U: p={p_val:.4f} {sig}")

if ratio > 1.5 and p_val < 0.05:
    verdict = "CLUSTERS ARE SHARP (H2 SUPPORTED)"
else:
    verdict = "CLUSTERS ARE FUZZY (H2 NOT SUPPORTED)"

print(f"\n{verdict}")

results['best_k'] = best_k
results['best_silhouette'] = float(best_silhouette)
results['within_cluster_distance'] = float(mean_within)
results['between_cluster_distance'] = float(mean_between)
results['distance_ratio'] = float(ratio)
results['mannwhitney_p'] = float(p_val)
results['verdict'] = verdict

# Save
out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't2_clustering.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
