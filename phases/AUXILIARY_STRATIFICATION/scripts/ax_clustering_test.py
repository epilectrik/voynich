"""
Q3: AUXILIARY Clustering Test

Test whether AX classes form natural sub-groups using distributional features.
Compare distributional clusters to ICC's prefix-based families.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# Paths
BASE = Path('C:/git/voynich')
FEATURES_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_features.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

with open(FEATURES_FILE) as f:
    features = json.load(f)

with open(CENSUS_FILE) as f:
    census = json.load(f)

prefix_families = census['prefix_families']

# ============================================================
# BUILD FEATURE MATRIX
# ============================================================

# Select features for clustering
FEATURE_KEYS = [
    'mean_position', 'var_position', 'initial_rate', 'final_rate',
    'regime_entropy',
    'prefix_rate', 'suffix_rate', 'articulator_rate',
    'energy_adj_rate', 'left_en_rate', 'right_en_rate',
    'left_ax_rate', 'right_ax_rate',
]

# Add REGIME shares
REGIME_KEYS = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
# Add key section shares
SECTION_KEYS = ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']

class_ids = sorted(features.keys(), key=int)
n = len(class_ids)

# Build matrix
rows = []
for cls_id in class_ids:
    f = features[cls_id]
    row = [f[k] for k in FEATURE_KEYS]
    row += [f['regime_shares'].get(r, 0) for r in REGIME_KEYS]
    row += [f['section_shares'].get(s, 0) for s in SECTION_KEYS]
    rows.append(row)

X = np.array(rows)
feature_names = FEATURE_KEYS + [f'regime_{r}' for r in REGIME_KEYS] + [f'section_{s}' for s in SECTION_KEYS]

print("=" * 70)
print("Q3: AUXILIARY CLUSTERING TEST")
print("=" * 70)

print(f"\nFeature matrix: {X.shape[0]} classes x {X.shape[1]} features")
print(f"Features: {', '.join(feature_names)}")

# ============================================================
# NORMALIZE (Z-SCORE)
# ============================================================
means = X.mean(axis=0)
stds = X.std(axis=0)
# Avoid division by zero for constant features
stds[stds == 0] = 1
X_norm = (X - means) / stds

# ============================================================
# HIERARCHICAL CLUSTERING
# ============================================================
print("\n" + "-" * 70)
print("1. HIERARCHICAL CLUSTERING (Ward's method)")
print("-" * 70)

dist_matrix = pdist(X_norm, metric='euclidean')
Z = linkage(dist_matrix, method='ward')

# Try k=2,3,4,5 and compute silhouette
from scipy.spatial.distance import squareform

def silhouette_score(X, labels):
    """Simple silhouette score computation."""
    n = len(labels)
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        return -1

    dist = squareform(pdist(X, metric='euclidean'))
    scores = []
    for i in range(n):
        # a(i) = mean distance to same cluster
        same = [j for j in range(n) if labels[j] == labels[i] and j != i]
        if not same:
            scores.append(0)
            continue
        a_i = np.mean([dist[i][j] for j in same])

        # b(i) = min mean distance to other clusters
        b_i = float('inf')
        for label in unique_labels:
            if label == labels[i]:
                continue
            other = [j for j in range(n) if labels[j] == label]
            if other:
                b_i = min(b_i, np.mean([dist[i][j] for j in other]))

        scores.append((b_i - a_i) / max(a_i, b_i))

    return np.mean(scores)

print(f"\n{'k':>3} {'Silhouette':>11} {'Cluster sizes'}")
best_k = 2
best_sil = -1
cluster_results = {}

for k in range(2, 7):
    labels = fcluster(Z, t=k, criterion='maxclust')
    sil = silhouette_score(X_norm, labels)
    sizes = [sum(labels == i) for i in range(1, k+1)]
    print(f"{k:3d} {sil:11.3f} {sizes}")
    cluster_results[k] = {
        'labels': labels.tolist(),
        'silhouette': round(sil, 4),
        'sizes': sizes,
    }
    if sil > best_sil:
        best_sil = sil
        best_k = k

print(f"\nBest k: {best_k} (silhouette={best_sil:.3f})")

# ============================================================
# OPTIMAL CLUSTERING DETAILS
# ============================================================
print("\n" + "-" * 70)
print(f"2. OPTIMAL CLUSTERING (k={best_k})")
print("-" * 70)

best_labels = fcluster(Z, t=best_k, criterion='maxclust')

# Map class IDs to cluster labels
class_to_cluster = {}
for i, cls_id in enumerate(class_ids):
    class_to_cluster[int(cls_id)] = int(best_labels[i])

print(f"\n{'Cluster':>7} {'Classes'}")
for c in range(1, best_k + 1):
    members = [int(cls_id) for cls_id, cl in class_to_cluster.items() if cl == c]
    print(f"{c:7d} {sorted(members)}")

# ============================================================
# CLUSTER CHARACTERIZATION (per feature)
# ============================================================
print("\n" + "-" * 70)
print("3. CLUSTER FEATURE PROFILES")
print("-" * 70)

for c in range(1, best_k + 1):
    mask = best_labels == c
    cluster_X = X[mask]
    members = [int(cls_id) for i, cls_id in enumerate(class_ids) if best_labels[i] == c]

    print(f"\nCluster {c}: {sorted(members)}")
    print(f"  Classes: {len(members)}, Total tokens: {sum(features[str(cls)]['n_tokens'] for cls in members)}")

    for j, fname in enumerate(feature_names):
        if cluster_X.shape[0] > 0:
            mean_val = cluster_X[:, j].mean()
            global_mean = X[:, j].mean()
            if global_mean != 0:
                ratio = mean_val / global_mean
                if abs(ratio - 1.0) > 0.15:  # Only show distinctive features
                    direction = '+' if ratio > 1 else '-'
                    print(f"  {direction} {fname}: {mean_val:.3f} (vs global {global_mean:.3f}, {ratio:.2f}x)")

# ============================================================
# COMPARISON TO PREFIX FAMILIES
# ============================================================
print("\n" + "-" * 70)
print("4. PREFIX FAMILY vs DISTRIBUTIONAL CLUSTER COMPARISON")
print("-" * 70)

# Build prefix family membership
prefix_to_class = {}
for fam, classes in prefix_families.items():
    for cls in classes:
        prefix_to_class[cls] = fam

print(f"\n{'Class':>5} {'Cluster':>8} {'Prefix Family':>18} {'Match?'}")
for cls_id in class_ids:
    cls = int(cls_id)
    cluster = class_to_cluster[cls]
    pfam = prefix_to_class.get(cls, 'UNKNOWN')
    print(f"{cls:5d} {cluster:8d} {pfam:>18}")

# Agreement metric: do prefix families map cleanly to clusters?
from collections import Counter
family_cluster_overlap = {}
for fam, classes in prefix_families.items():
    cluster_counts = Counter(class_to_cluster.get(cls, -1) for cls in classes)
    dominant = cluster_counts.most_common(1)[0]
    purity = dominant[1] / len(classes) if classes else 0
    family_cluster_overlap[fam] = {
        'cluster_counts': dict(cluster_counts),
        'dominant_cluster': dominant[0],
        'purity': round(purity, 2),
    }
    print(f"\n{fam}: maps to cluster {dominant[0]} with purity {purity:.0%}")
    print(f"  {dict(cluster_counts)}")

# ============================================================
# ALSO TEST k=3 (positional grouping)
# ============================================================
print("\n" + "-" * 70)
print("5. k=3 CLUSTERING (positional hypothesis)")
print("-" * 70)

labels_3 = fcluster(Z, t=3, criterion='maxclust')
sil_3 = silhouette_score(X_norm, labels_3)

for c in range(1, 4):
    mask = labels_3 == c
    members = [int(cls_id) for i, cls_id in enumerate(class_ids) if labels_3[i] == c]
    cluster_X = X[mask]

    mean_pos = cluster_X[:, feature_names.index('mean_position')].mean()
    mean_init = cluster_X[:, feature_names.index('initial_rate')].mean()
    mean_final = cluster_X[:, feature_names.index('final_rate')].mean()
    mean_artic = cluster_X[:, feature_names.index('articulator_rate')].mean()

    pos_label = 'INITIAL' if mean_init > 0.2 else ('FINAL' if mean_final > 0.2 else 'MEDIAL')

    print(f"\nCluster {c} ({pos_label}): {sorted(members)}")
    print(f"  MeanPos={mean_pos:.3f}, Init={mean_init:.1%}, Final={mean_final:.1%}, Artic={mean_artic:.1%}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'feature_names': feature_names,
    'best_k': best_k,
    'best_silhouette': round(best_sil, 4),
    'all_k_results': {str(k): v for k, v in cluster_results.items()},
    'optimal_clustering': {
        'k': best_k,
        'class_to_cluster': {str(k): v for k, v in class_to_cluster.items()},
        'clusters': {
            str(c): sorted([int(cls_id) for cls_id, cl in class_to_cluster.items() if cl == c])
            for c in range(1, best_k + 1)
        }
    },
    'k3_clustering': {
        'silhouette': round(sil_3, 4),
        'class_to_cluster': {
            str(int(class_ids[i])): int(labels_3[i])
            for i in range(len(class_ids))
        }
    },
    'prefix_family_comparison': family_cluster_overlap,
}

with open(RESULTS / 'ax_clustering.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'ax_clustering.json'}")
