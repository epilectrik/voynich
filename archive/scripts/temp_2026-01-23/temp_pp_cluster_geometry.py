#!/usr/bin/env python3
"""
PP MIDDLE Clustering by Class Activation Profile

Question: Does the 86-PP × 49-CLASS activation matrix have low-rank structure?
Do PP MIDDLEs cluster into coherent groups based on which classes they activate?

Method:
1. Build binary matrix M[pp][class] = 1 if PP MIDDLE appears in any token of class
2. Cluster PP MIDDLEs by class activation vectors
3. Test significance vs random permutation
"""

import json
import sys
import numpy as np
from collections import defaultdict
from pathlib import Path
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Load class-token map
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
token_to_middle = class_map['token_to_middle']
class_to_tokens = class_map['class_to_tokens']

# Build MIDDLE → classes mapping
middle_to_classes = defaultdict(set)
for token, middle in token_to_middle.items():
    if middle:
        cls = token_to_class.get(token)
        if cls:
            middle_to_classes[middle].add(int(cls))

# Get all classes and PP MIDDLEs
all_classes = sorted(set(int(c) for c in class_to_tokens.keys()))
all_middles = sorted(middle_to_classes.keys())

print("="*70)
print("PP MIDDLE CLUSTERING BY CLASS ACTIVATION PROFILE")
print("="*70)
print(f"\nPP MIDDLEs: {len(all_middles)}")
print(f"Classes: {len(all_classes)}")

# Build binary activation matrix: rows=MIDDLEs, cols=classes
n_middles = len(all_middles)
n_classes = len(all_classes)
class_to_idx = {c: i for i, c in enumerate(all_classes)}

M = np.zeros((n_middles, n_classes), dtype=int)
for i, middle in enumerate(all_middles):
    for cls in middle_to_classes[middle]:
        M[i, class_to_idx[cls]] = 1

print(f"\nActivation matrix shape: {M.shape}")
print(f"Density: {M.sum() / M.size:.3f} ({M.sum()} / {M.size} cells active)")

# Basic statistics
row_sums = M.sum(axis=1)  # classes per MIDDLE
col_sums = M.sum(axis=0)  # MIDDLEs per class

print(f"\nClasses per MIDDLE: min={row_sums.min()}, max={row_sums.max()}, mean={row_sums.mean():.1f}")
print(f"MIDDLEs per class: min={col_sums.min()}, max={col_sums.max()}, mean={col_sums.mean():.1f}")

# Compute pairwise Jaccard distances between MIDDLEs
print("\n" + "="*70)
print("CLUSTERING ANALYSIS")
print("="*70)

# Jaccard distance = 1 - Jaccard similarity
def jaccard_distance(u, v):
    intersection = np.sum(u & v)
    union = np.sum(u | v)
    if union == 0:
        return 1.0
    return 1.0 - intersection / union

# Compute distance matrix
dist_matrix = squareform(pdist(M, metric=jaccard_distance))

print(f"\nPairwise Jaccard distances:")
print(f"  Min: {dist_matrix[dist_matrix > 0].min():.3f}")
print(f"  Max: {dist_matrix.max():.3f}")
print(f"  Mean: {dist_matrix[np.triu_indices(n_middles, 1)].mean():.3f}")

# Hierarchical clustering
print("\n--- Hierarchical Clustering (Ward linkage) ---")
# Use Euclidean for Ward (standard)
Z = linkage(M, method='ward')

# Try different cluster counts
print(f"\n{'k':>3} {'Silhouette':>12} {'Cluster sizes'}")
print("-" * 50)

best_k = 2
best_score = -1

for k in range(2, min(15, n_middles//3)):
    labels = fcluster(Z, k, criterion='maxclust')

    # Need at least 2 samples per cluster for silhouette
    cluster_sizes = [np.sum(labels == i) for i in range(1, k+1)]
    if min(cluster_sizes) < 2:
        continue

    score = silhouette_score(M, labels, metric='euclidean')
    sizes_str = ','.join(str(s) for s in sorted(cluster_sizes, reverse=True)[:5])
    if len(cluster_sizes) > 5:
        sizes_str += '...'

    print(f"{k:>3} {score:>12.3f} [{sizes_str}]")

    if score > best_score:
        best_score = score
        best_k = k

print(f"\nBest k={best_k} with silhouette={best_score:.3f}")

# Get best clustering
best_labels = fcluster(Z, best_k, criterion='maxclust')

# Analyze clusters
print("\n" + "="*70)
print(f"CLUSTER ANALYSIS (k={best_k})")
print("="*70)

for cluster_id in range(1, best_k + 1):
    cluster_mask = best_labels == cluster_id
    cluster_middles = [all_middles[i] for i in range(n_middles) if cluster_mask[i]]
    cluster_matrix = M[cluster_mask]

    # Which classes does this cluster primarily activate?
    class_activation = cluster_matrix.sum(axis=0)
    active_classes = [all_classes[j] for j in range(n_classes) if class_activation[j] > 0]

    # Mean classes per MIDDLE in this cluster
    mean_span = cluster_matrix.sum(axis=1).mean()

    print(f"\n--- Cluster {cluster_id} ({len(cluster_middles)} MIDDLEs) ---")
    print(f"  MIDDLEs: {', '.join(cluster_middles[:10])}{'...' if len(cluster_middles) > 10 else ''}")
    print(f"  Mean class span: {mean_span:.1f}")
    print(f"  Classes activated: {len(active_classes)} ({', '.join(map(str, sorted(active_classes)[:15]))}{'...' if len(active_classes) > 15 else ''})")

    # Class concentration - which classes are hit by >50% of cluster members?
    concentrated = [all_classes[j] for j in range(n_classes)
                   if class_activation[j] > len(cluster_middles) * 0.5]
    if concentrated:
        print(f"  Concentrated (>50%): classes {sorted(concentrated)}")

# Permutation test
print("\n" + "="*70)
print("PERMUTATION TEST")
print("="*70)

n_perms = 1000
perm_scores = []

for _ in range(n_perms):
    # Shuffle class assignments within each MIDDLE (preserve row sums)
    M_perm = np.zeros_like(M)
    for i in range(n_middles):
        n_active = M[i].sum()
        active_cols = np.random.choice(n_classes, size=n_active, replace=False)
        M_perm[i, active_cols] = 1

    Z_perm = linkage(M_perm, method='ward')
    labels_perm = fcluster(Z_perm, best_k, criterion='maxclust')

    cluster_sizes = [np.sum(labels_perm == i) for i in range(1, best_k+1)]
    if min(cluster_sizes) >= 2:
        score_perm = silhouette_score(M_perm, labels_perm, metric='euclidean')
        perm_scores.append(score_perm)

perm_scores = np.array(perm_scores)
p_value = (perm_scores >= best_score).sum() / len(perm_scores)

print(f"\nObserved silhouette: {best_score:.3f}")
print(f"Permutation mean: {perm_scores.mean():.3f} (std={perm_scores.std():.3f})")
print(f"Permutation max: {perm_scores.max():.3f}")
print(f"p-value: {p_value:.4f} ({(perm_scores >= best_score).sum()}/{len(perm_scores)} perms >= observed)")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if p_value < 0.05:
    print(f"""
SIGNIFICANT CLUSTERING DETECTED (p={p_value:.4f})

PP MIDDLEs show non-random structure in their class activation profiles.
The {best_k} clusters have silhouette={best_score:.3f}, significantly better
than random permutations (mean={perm_scores.mean():.3f}).

This suggests PP vocabulary has INTERNAL GEOMETRIC ORGANIZATION:
- Different PP subsets tune different regions of the 49-class grammar
- PP is not just "add more = more coverage" but has structured domains
""")
else:
    print(f"""
NO SIGNIFICANT CLUSTERING (p={p_value:.4f})

PP MIDDLEs do not show structure beyond what's expected by chance.
The observed silhouette={best_score:.3f} is within the null distribution
(mean={perm_scores.mean():.3f}).

This suggests PP class coverage is UNSTRUCTURED:
- PP count is the complete story (C506)
- No geometric organization to PP vocabulary
- Investigation CLOSED - PP is a capacity variable only
""")

# Save results
results = {
    'n_middles': n_middles,
    'n_classes': n_classes,
    'best_k': int(best_k),
    'best_silhouette': float(best_score),
    'perm_mean': float(perm_scores.mean()),
    'perm_std': float(perm_scores.std()),
    'p_value': float(p_value),
    'significant': p_value < 0.05,
    'clusters': {}
}

for cluster_id in range(1, best_k + 1):
    cluster_mask = best_labels == cluster_id
    cluster_middles = [all_middles[i] for i in range(n_middles) if cluster_mask[i]]
    cluster_matrix = M[cluster_mask]
    class_activation = cluster_matrix.sum(axis=0)
    active_classes = [all_classes[j] for j in range(n_classes) if class_activation[j] > 0]

    results['clusters'][cluster_id] = {
        'middles': cluster_middles,
        'n_middles': len(cluster_middles),
        'mean_span': float(cluster_matrix.sum(axis=1).mean()),
        'active_classes': active_classes
    }

with open('temp_pp_cluster_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to temp_pp_cluster_results.json")
