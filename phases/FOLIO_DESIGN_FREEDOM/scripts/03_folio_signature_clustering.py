"""
Script 3: Folio Signature Clustering
Question: Do folios with similar design choices form interpretable groups?

Uses section-residualized atom vectors, runs Ward clustering,
compares to REGIME/apparatus, identifies extreme pairs.
"""

import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.stats import spearmanr, entropy
from sklearn.metrics import silhouette_score, adjusted_rand_score

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

RESULTS = Path(__file__).resolve().parent.parent / 'results'

# === Load Data ===

feature_df = pd.read_csv(RESULTS / '01_folio_atom_features.csv', index_col=0)
residual_df = pd.read_csv(RESULTS / '01_folio_atom_features_residualized.csv', index_col=0)

with open(RESULTS / '01_freedom_space_pca.json') as f:
    pca_results = json.load(f)

sections = pd.Series(pca_results['sections'])
numeric_cols = residual_df.columns.tolist()

print(f"Loaded {len(feature_df)} folios, {len(numeric_cols)} residualized features")

# === Pairwise Distance Matrix ===

from sklearn.preprocessing import StandardScaler

X = residual_df[numeric_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = np.nan_to_num(X_scaled, nan=0.0)

# Use Jensen-Shannon divergence on normalized features where possible,
# Euclidean on residualized+scaled features for clustering
dist_matrix = pdist(X_scaled, metric='euclidean')
dist_sq = squareform(dist_matrix)

print(f"Distance matrix shape: {dist_sq.shape}")
print(f"Mean distance: {dist_matrix.mean():.3f}, std: {dist_matrix.std():.3f}")

# === Ward Clustering with Silhouette Scan ===

Z = linkage(dist_matrix, method='ward')

print(f"\n=== Silhouette Scan (k=2..8) ===")
sil_scores = {}
for k in range(2, 9):
    labels = fcluster(Z, t=k, criterion='maxclust')
    sil = silhouette_score(X_scaled, labels, metric='euclidean')
    sil_scores[k] = sil
    print(f"  k={k}: silhouette={sil:.3f}")

best_k = max(sil_scores, key=sil_scores.get)
best_sil = sil_scores[best_k]
print(f"\nBest k={best_k} (silhouette={best_sil:.3f})")

# Is this a genuine cluster structure or gradient?
# Compare to section-stratified null
from sklearn.utils import shuffle as sk_shuffle

null_sils = []
for _ in range(200):
    # Shuffle residualized features independently per column
    X_null = X_scaled.copy()
    for col_idx in range(X_null.shape[1]):
        np.random.shuffle(X_null[:, col_idx])
    null_dist = pdist(X_null, metric='euclidean')
    null_Z = linkage(null_dist, method='ward')
    null_labels = fcluster(null_Z, t=best_k, criterion='maxclust')
    null_sil = silhouette_score(X_null, null_labels, metric='euclidean')
    null_sils.append(null_sil)

null_mean = np.mean(null_sils)
null_p95 = np.percentile(null_sils, 95)
print(f"\nNull baseline (k={best_k}): mean={null_mean:.3f}, p95={null_p95:.3f}")
print(f"Real silhouette: {best_sil:.3f}")
print(f"Verdict: {'ABOVE_NULL' if best_sil > null_p95 else 'WITHIN_NULL'}")

# === Compare Clusters to REGIME ===

best_labels = fcluster(Z, t=best_k, criterion='maxclust')
folio_labels = dict(zip(feature_df.index, best_labels))

try:
    regime_path = Path(__file__).resolve().parents[3] / 'results' / 'regime_assignments.json'
    if regime_path.exists():
        with open(regime_path) as f:
            regime_data = json.load(f)
        common = [f for f in feature_df.index if f in regime_data]
        if len(common) > 20:
            cluster_labels = [folio_labels[f] for f in common]
            regime_labels = [regime_data[f] for f in common]
            ari = adjusted_rand_score(regime_labels, cluster_labels)
            print(f"\n=== REGIME Alignment (n={len(common)}) ===")
            print(f"  ARI with REGIME: {ari:.3f}")
            print(f"  (0=random, 1=identical)")
except Exception as e:
    print(f"\nREGIME comparison skipped: {e}")

# ARI with section (should be ~0 since we residualized)
section_labels = [sections[f] for f in feature_df.index]
ari_section = adjusted_rand_score(section_labels, best_labels)
print(f"\n  ARI with section: {ari_section:.3f} (should be ~0)")

# === Extreme Pairs Within Each Section ===

print(f"\n=== Most Different Folio Pairs Within Sections ===")

extreme_pairs = {}
for sec in sorted(set(section_labels)):
    sec_folios = [f for f in feature_df.index if sections[f] == sec]
    if len(sec_folios) < 3:
        continue

    sec_indices = [list(feature_df.index).index(f) for f in sec_folios]
    sec_dist = dist_sq[np.ix_(sec_indices, sec_indices)]

    # Find max distance pair
    max_i, max_j = np.unravel_index(sec_dist.argmax(), sec_dist.shape)
    f1, f2 = sec_folios[max_i], sec_folios[max_j]
    max_dist = sec_dist[max_i, max_j]

    # Which features diverge most?
    diff = residual_df.loc[f1, numeric_cols] - residual_df.loc[f2, numeric_cols]
    top_diff = diff.abs().nlargest(5)

    extreme_pairs[sec] = {
        'folio_1': f1,
        'folio_2': f2,
        'distance': float(max_dist),
        'mean_within_section_dist': float(sec_dist[sec_dist > 0].mean()),
        'top_divergent_features': {k: float(diff[k]) for k in top_diff.index},
    }

    print(f"\n  {sec}: {f1} vs {f2} (dist={max_dist:.3f}, mean={sec_dist[sec_dist > 0].mean():.3f})")
    print(f"    Top divergent features:")
    for feat, val in extreme_pairs[sec]['top_divergent_features'].items():
        v1 = feature_df.loc[f1, feat]
        v2 = feature_df.loc[f2, feat]
        print(f"      {feat}: {v1:.4f} vs {v2:.4f} (delta={val:+.4f})")

# === Cluster Characterization ===

print(f"\n=== Cluster Profiles (k={best_k}) ===")
cluster_profiles = {}
for k in range(1, best_k + 1):
    cluster_folios = [f for f, lbl in folio_labels.items() if lbl == k]
    cluster_sections = [sections[f] for f in cluster_folios]
    sec_counts = pd.Series(cluster_sections).value_counts().to_dict()

    # Mean residualized features for this cluster
    cluster_means = residual_df.loc[cluster_folios].mean()
    top_pos = cluster_means.nlargest(3)
    top_neg = cluster_means.nsmallest(3)

    cluster_profiles[k] = {
        'n': len(cluster_folios),
        'sections': sec_counts,
        'top_positive': {feat: float(val) for feat, val in top_pos.items()},
        'top_negative': {feat: float(val) for feat, val in top_neg.items()},
    }

    print(f"\n  Cluster {k} (n={len(cluster_folios)}): sections={sec_counts}")
    print(f"    Enriched: {', '.join(f'{k}={v:.3f}' for k, v in top_pos.items())}")
    print(f"    Depleted: {', '.join(f'{k}={v:.3f}' for k, v in top_neg.items())}")

# === Save Results ===

results = {
    'n_folios': len(feature_df),
    'silhouette_scan': {str(k): float(v) for k, v in sil_scores.items()},
    'best_k': int(best_k),
    'best_silhouette': float(best_sil),
    'null_mean': float(null_mean),
    'null_p95': float(null_p95),
    'verdict': 'ABOVE_NULL' if best_sil > null_p95 else 'WITHIN_NULL',
    'ari_section': float(ari_section),
    'folio_cluster_labels': {f: int(lbl) for f, lbl in folio_labels.items()},
    'cluster_profiles': cluster_profiles,
    'extreme_pairs': extreme_pairs,
}

with open(RESULTS / '03_clustering.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / '03_clustering.json'}")
print("Done.")
