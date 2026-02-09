#!/usr/bin/env python3
"""
Test 1: Cluster Validity Analysis

Questions:
1. Are 3 clusters optimal, or is the data continuous?
2. How stable are clusters under bootstrap resampling?
3. What is the silhouette score (cluster separation quality)?
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from scipy.cluster import hierarchy
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Role taxonomy
PREFIX_ROLES = {
    'ch': 'CORE', 'sh': 'CORE',
    'qo': 'ESCAPE', 'ok': 'AUXILIARY',
    'ol': 'LINK', 'or': 'LINK',
    'ct': 'CROSS-REF',
    'da': 'CLOSURE', 'do': 'CLOSURE',
    'kch': 'GALLOWS-CH', 'tch': 'GALLOWS-CH', 'pch': 'GALLOWS-CH',
    'fch': 'GALLOWS-CH', 'sch': 'GALLOWS-CH', 'dch': 'GALLOWS-CH',
    'po': 'INPUT', 'so': 'INPUT', 'to': 'INPUT', 'ko': 'INPUT',
}

def get_role(prefix):
    if prefix in PREFIX_ROLES:
        return PREFIX_ROLES[prefix]
    if prefix and len(prefix) >= 2 and prefix[-2:] == 'ch':
        return 'GALLOWS-CH'
    if prefix and prefix.endswith('o') and len(prefix) == 2:
        return 'INPUT'
    return 'UNCLASSIFIED'

print("="*70)
print("TEST 1: CLUSTER VALIDITY ANALYSIS")
print("="*70)

# Build A folio PP profiles for Section H
a_folio_data = defaultdict(lambda: {'role_counts': Counter(), 'total': 0})

current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word or token.section != 'H':
        continue

    if token.folio != current_folio:
        if current_para:
            # Extract PP from completed paragraph
            tokens = [t.word for t in current_para]
            if len(tokens) > 6:
                pp_tokens = tokens[3:-3]
            elif len(tokens) > 3:
                pp_tokens = tokens[3:]
            else:
                pp_tokens = []

            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        a_folio_data[current_folio]['total'] += 1
                except:
                    pass

        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            # New paragraph - process old one
            tokens = [t.word for t in current_para]
            if len(tokens) > 6:
                pp_tokens = tokens[3:-3]
            elif len(tokens) > 3:
                pp_tokens = tokens[3:]
            else:
                pp_tokens = []

            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        a_folio_data[current_folio]['total'] += 1
                except:
                    pass

            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

# Process final paragraph
if current_para:
    tokens = [t.word for t in current_para]
    if len(tokens) > 6:
        pp_tokens = tokens[3:-3]
    elif len(tokens) > 3:
        pp_tokens = tokens[3:]
    else:
        pp_tokens = []

    for tok in pp_tokens:
        try:
            m = morph.extract(tok)
            if m.prefix:
                role = get_role(m.prefix)
                a_folio_data[current_folio]['role_counts'][role] += 1
                a_folio_data[current_folio]['total'] += 1
        except:
            pass

# Filter to folios with sufficient data
roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']
folios = []
feature_matrix = []

for folio, data in a_folio_data.items():
    if data['total'] >= 20:
        folios.append(folio)
        vec = [data['role_counts'].get(r, 0) / data['total'] for r in roles]
        feature_matrix.append(vec)

X = np.array(feature_matrix)
print(f"\nFolios with sufficient PP data: {len(folios)}")
print(f"Feature dimensions: {X.shape[1]} (roles)")

# =========================================================================
# 1. Silhouette Analysis for k=2,3,4,5
# =========================================================================
print("\n" + "="*70)
print("1. SILHOUETTE ANALYSIS")
print("="*70)

silhouette_scores = {}

for k in [2, 3, 4, 5]:
    linkage = hierarchy.linkage(X, method='ward')
    clusters = hierarchy.fcluster(linkage, t=k, criterion='maxclust')

    score = silhouette_score(X, clusters)
    silhouette_scores[k] = score

    print(f"\nk={k}: Silhouette = {score:.3f}")

    # Per-cluster breakdown
    sample_scores = silhouette_samples(X, clusters)
    for c in range(1, k+1):
        mask = clusters == c
        cluster_score = sample_scores[mask].mean()
        print(f"  Cluster {c}: {cluster_score:.3f} (n={mask.sum()})")

best_k = max(silhouette_scores, key=silhouette_scores.get)
print(f"\nBest k by silhouette: {best_k} (score={silhouette_scores[best_k]:.3f})")

# Interpretation
if silhouette_scores[best_k] > 0.5:
    quality = "STRONG"
elif silhouette_scores[best_k] > 0.3:
    quality = "MODERATE"
elif silhouette_scores[best_k] > 0.2:
    quality = "WEAK"
else:
    quality = "POOR"

print(f"Cluster quality: {quality}")

# =========================================================================
# 2. Bootstrap Stability Analysis
# =========================================================================
print("\n" + "="*70)
print("2. BOOTSTRAP STABILITY ANALYSIS")
print("="*70)

n_bootstrap = 100
k = 3  # Use k=3 for main analysis

# Get reference clustering
linkage_ref = hierarchy.linkage(X, method='ward')
clusters_ref = hierarchy.fcluster(linkage_ref, t=k, criterion='maxclust')

# Bootstrap
stability_matrix = np.zeros((len(folios), len(folios)))

for b in range(n_bootstrap):
    # Resample with replacement
    indices = np.random.choice(len(folios), size=len(folios), replace=True)
    X_boot = X[indices]

    # Cluster
    linkage_boot = hierarchy.linkage(X_boot, method='ward')
    clusters_boot = hierarchy.fcluster(linkage_boot, t=k, criterion='maxclust')

    # Build co-clustering matrix for sampled points
    for i, idx_i in enumerate(indices):
        for j, idx_j in enumerate(indices):
            if clusters_boot[i] == clusters_boot[j]:
                stability_matrix[idx_i, idx_j] += 1

# Normalize
stability_matrix /= n_bootstrap

# Compute stability score (average within-cluster agreement)
within_cluster_stability = []
for c in range(1, k+1):
    mask = clusters_ref == c
    indices = np.where(mask)[0]
    if len(indices) > 1:
        pairs = [(i, j) for i in indices for j in indices if i < j]
        if pairs:
            scores = [stability_matrix[i, j] for i, j in pairs]
            within_cluster_stability.append(np.mean(scores))

overall_stability = np.mean(within_cluster_stability)
print(f"\nBootstrap stability (n={n_bootstrap}):")
print(f"  Overall within-cluster stability: {overall_stability:.3f}")

for c, stab in enumerate(within_cluster_stability, 1):
    print(f"  Cluster {c} stability: {stab:.3f}")

if overall_stability > 0.8:
    stability_verdict = "HIGHLY STABLE"
elif overall_stability > 0.6:
    stability_verdict = "MODERATELY STABLE"
else:
    stability_verdict = "UNSTABLE"

print(f"\nStability verdict: {stability_verdict}")

# =========================================================================
# 3. Gap Statistic
# =========================================================================
print("\n" + "="*70)
print("3. GAP STATISTIC")
print("="*70)

def compute_wss(X, clusters):
    """Within-cluster sum of squares."""
    wss = 0
    for c in np.unique(clusters):
        mask = clusters == c
        if mask.sum() > 0:
            center = X[mask].mean(axis=0)
            wss += ((X[mask] - center) ** 2).sum()
    return wss

n_ref = 50
gap_stats = {}

for k in [1, 2, 3, 4, 5]:
    # Observed WSS
    if k == 1:
        clusters_k = np.ones(len(folios))
    else:
        linkage_k = hierarchy.linkage(X, method='ward')
        clusters_k = hierarchy.fcluster(linkage_k, t=k, criterion='maxclust')

    wss_obs = compute_wss(X, clusters_k)

    # Reference WSS (uniform distribution)
    wss_ref = []
    for _ in range(n_ref):
        X_ref = np.random.uniform(X.min(axis=0), X.max(axis=0), size=X.shape)
        if k == 1:
            clusters_ref_k = np.ones(len(X_ref))
        else:
            linkage_ref_k = hierarchy.linkage(X_ref, method='ward')
            clusters_ref_k = hierarchy.fcluster(linkage_ref_k, t=k, criterion='maxclust')
        wss_ref.append(compute_wss(X_ref, clusters_ref_k))

    gap = np.mean(np.log(wss_ref)) - np.log(wss_obs)
    gap_std = np.std(np.log(wss_ref))

    gap_stats[k] = {'gap': gap, 'std': gap_std}
    print(f"k={k}: Gap = {gap:.3f} (+/- {gap_std:.3f})")

# Find optimal k using gap criterion
optimal_k_gap = 1
for k in range(1, 5):
    if gap_stats[k]['gap'] >= gap_stats[k+1]['gap'] - gap_stats[k+1]['std']:
        optimal_k_gap = k
        break

print(f"\nOptimal k by gap statistic: {optimal_k_gap}")

# =========================================================================
# 4. PCA Visualization Data
# =========================================================================
print("\n" + "="*70)
print("4. PCA PROJECTION")
print("="*70)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

print(f"\nVariance explained:")
print(f"  PC1: {pca.explained_variance_ratio_[0]:.1%}")
print(f"  PC2: {pca.explained_variance_ratio_[1]:.1%}")
print(f"  Total: {sum(pca.explained_variance_ratio_):.1%}")

# Get k=3 clusters for visualization
linkage_3 = hierarchy.linkage(X, method='ward')
clusters_3 = hierarchy.fcluster(linkage_3, t=3, criterion='maxclust')

# Compute cluster centroids in PCA space
print("\nCluster centroids (PCA space):")
for c in range(1, 4):
    mask = clusters_3 == c
    centroid = X_pca[mask].mean(axis=0)
    print(f"  Cluster {c}: PC1={centroid[0]:.3f}, PC2={centroid[1]:.3f}")

# =========================================================================
# 5. Feature Importance
# =========================================================================
print("\n" + "="*70)
print("5. FEATURE IMPORTANCE (PCA Loadings)")
print("="*70)

loadings = pca.components_
print(f"\n{'Role':<15} {'PC1 Loading':<15} {'PC2 Loading':<15}")
print("-"*45)

for i, role in enumerate(roles):
    print(f"{role:<15} {loadings[0, i]:>+.3f}{'':>10} {loadings[1, i]:>+.3f}")

# Identify most discriminating features
pc1_top = sorted(zip(roles, loadings[0]), key=lambda x: abs(x[1]), reverse=True)
print(f"\nTop PC1 discriminators: {', '.join(r for r, _ in pc1_top[:3])}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: CLUSTER VALIDITY")
print("="*70)

print(f"""
Silhouette Analysis:
  Best k: {best_k}
  Score: {silhouette_scores[best_k]:.3f} ({quality})

Bootstrap Stability:
  Overall: {overall_stability:.3f} ({stability_verdict})

Gap Statistic:
  Optimal k: {optimal_k_gap}

PCA Variance:
  2 components explain {sum(pca.explained_variance_ratio_):.1%}
""")

# Verdict
if silhouette_scores[3] > 0.25 and overall_stability > 0.6:
    verdict = "CONFIRMED"
    explanation = "3 clusters show meaningful separation and stability"
elif silhouette_scores[3] > 0.2:
    verdict = "SUPPORT"
    explanation = "Weak but detectable cluster structure"
else:
    verdict = "NOT SUPPORTED"
    explanation = "Data appears continuous, clusters may be artifacts"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'n_folios': len(folios),
    'silhouette_scores': silhouette_scores,
    'best_k_silhouette': best_k,
    'bootstrap_stability': overall_stability,
    'stability_verdict': stability_verdict,
    'gap_stats': {str(k): v for k, v in gap_stats.items()},
    'optimal_k_gap': optimal_k_gap,
    'pca_variance_explained': list(pca.explained_variance_ratio_),
    'verdict': verdict,
    'folios': folios,
    'clusters_k3': clusters_3.tolist(),
}

output_path = Path(__file__).parent.parent / 'results' / 'cluster_validity.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
