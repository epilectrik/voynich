#!/usr/bin/env python3
"""
MATERIAL_LOCUS_SEARCH Phase - Test 1: Folio MIDDLE Vocabulary Profile Clustering

Question: Do folio-level MIDDLE profiles cluster into material-like categories
beyond section/regime?

Method:
1. Build MIDDLE frequency vectors per Currier B folio (common MIDDLEs in 20+ folios).
2. Compute pairwise cosine similarity and Jaccard similarity.
3. Hierarchical clustering (Ward linkage) at k=4,5,6.
4. Test cluster-section and cluster-regime correspondence (ARI, NMI).
5. Identify cross-section cluster members.
6. Null model: 10,000 permutations for ARI/NMI p-values.

Pass: ARI > 0.15, NMI > 0.10, permutation p < 0.01.
Fail: ARI < 0.05 (clusters just mirror section).

References: C909 (section MIDDLE vocabularies), C910 (regime MIDDLE clustering).
"""

import sys
import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology

# ============================================================
# 1. LOAD DATA
# ============================================================
print("Loading transcript and extracting MIDDLEs for Currier B...")
tx = Transcript()
morph = Morphology()

# Collect per-folio data
folio_middle_counts = defaultdict(Counter)  # folio -> Counter of MIDDLEs
folio_sections = {}                          # folio -> section
folio_token_counts = Counter()               # folio -> total token count

for token in tx.currier_b():
    folio = token.folio
    section = token.section
    m = morph.extract(token.word)
    middle = m.middle

    if middle and middle != '_EMPTY_':
        folio_middle_counts[folio][middle] += 1
        folio_token_counts[folio] += 1
        if folio not in folio_sections:
            folio_sections[folio] = section

folios = sorted(folio_middle_counts.keys())
n_folios = len(folios)
print(f"  Found {n_folios} Currier B folios with MIDDLE data")

# ============================================================
# 2. LOAD REGIME MAPPING
# ============================================================
regime_path = Path('C:/git/voynich/phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json')
with open(regime_path) as f:
    regime_data = json.load(f)

folio_regimes = {}
for regime, folio_list in regime_data.items():
    for folio in folio_list:
        folio_regimes[folio] = regime

# Count coverage
regime_covered = sum(1 for f in folios if f in folio_regimes)
print(f"  Regime mapping covers {regime_covered}/{n_folios} folios")

# ============================================================
# 3. BUILD COMMON MIDDLE SET (appearing in 20+ folios)
# ============================================================
middle_folio_presence = defaultdict(set)  # middle -> set of folios
for folio, counts in folio_middle_counts.items():
    for mid in counts:
        middle_folio_presence[mid].add(folio)

common_middles = sorted([mid for mid, fset in middle_folio_presence.items()
                         if len(fset) >= 20])
n_middles = len(common_middles)
print(f"  Common MIDDLEs (in 20+ folios): {n_middles}")

if n_middles < 5:
    print("ERROR: Too few common MIDDLEs for clustering. Aborting.")
    sys.exit(1)

# Create MIDDLE index for vector construction
middle_idx = {mid: i for i, mid in enumerate(common_middles)}

# ============================================================
# 4. BUILD FREQUENCY VECTORS (proportions)
# ============================================================
print("Building folio MIDDLE frequency vectors...")
# Matrix: folios x middles
freq_matrix = np.zeros((n_folios, n_middles))

for i, folio in enumerate(folios):
    counts = folio_middle_counts[folio]
    total = sum(counts[mid] for mid in common_middles)
    if total > 0:
        for mid in common_middles:
            freq_matrix[i, middle_idx[mid]] = counts[mid] / total

# ============================================================
# 5. COMPUTE PAIRWISE SIMILARITIES
# ============================================================
print("Computing pairwise similarities...")

# Cosine similarity
from numpy.linalg import norm

norms = norm(freq_matrix, axis=1, keepdims=True)
norms[norms == 0] = 1.0  # avoid division by zero
normed = freq_matrix / norms
cosine_sim = normed @ normed.T

# Jaccard similarity (binary: present/absent at threshold > 0)
binary_matrix = (freq_matrix > 0).astype(float)
# Jaccard = intersection / union
intersection = binary_matrix @ binary_matrix.T
row_sums = binary_matrix.sum(axis=1)
union = row_sums[:, None] + row_sums[None, :] - intersection
union[union == 0] = 1.0  # avoid division by zero
jaccard_sim = intersection / union

# Summary stats
cosine_triu = cosine_sim[np.triu_indices(n_folios, k=1)]
jaccard_triu = jaccard_sim[np.triu_indices(n_folios, k=1)]
print(f"  Cosine similarity: mean={cosine_triu.mean():.3f}, "
      f"std={cosine_triu.std():.3f}, range=[{cosine_triu.min():.3f}, {cosine_triu.max():.3f}]")
print(f"  Jaccard similarity: mean={jaccard_triu.mean():.3f}, "
      f"std={jaccard_triu.std():.3f}, range=[{jaccard_triu.min():.3f}, {jaccard_triu.max():.3f}]")

# ============================================================
# 6. HIERARCHICAL CLUSTERING (Ward linkage) at k=4,5,6
# ============================================================
print("Running hierarchical clustering...")
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# Use cosine distance for clustering
cosine_dist = pdist(freq_matrix, metric='cosine')
# Replace NaN with max distance (for zero vectors)
cosine_dist = np.nan_to_num(cosine_dist, nan=1.0)

linkage_matrix = linkage(cosine_dist, method='ward')

# ============================================================
# 7. COMPUTE ARI AND NMI FOR SECTION AND REGIME
# ============================================================
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Build section and regime label arrays
section_labels = [folio_sections.get(f, 'UNKNOWN') for f in folios]
regime_labels = [folio_regimes.get(f, 'UNKNOWN') for f in folios]

# Encode labels as integers
unique_sections = sorted(set(section_labels))
unique_regimes = sorted(set(regime_labels))
section_ints = np.array([unique_sections.index(s) for s in section_labels])
regime_ints = np.array([unique_regimes.index(r) for r in regime_labels])

print(f"\n  Sections: {dict(Counter(section_labels))}")
print(f"  Regimes: {dict(Counter(regime_labels))}")

results_per_k = {}

for k in [4, 5, 6]:
    cluster_labels = fcluster(linkage_matrix, t=k, criterion='maxclust')

    # ARI and NMI vs section
    ari_section = adjusted_rand_score(section_ints, cluster_labels)
    nmi_section = normalized_mutual_info_score(section_ints, cluster_labels)

    # ARI and NMI vs regime
    ari_regime = adjusted_rand_score(regime_ints, cluster_labels)
    nmi_regime = normalized_mutual_info_score(regime_ints, cluster_labels)

    # Cluster composition
    cluster_composition = {}
    for c in range(1, k + 1):
        members = [folios[i] for i in range(n_folios) if cluster_labels[i] == c]
        sections_in = [section_labels[i] for i in range(n_folios) if cluster_labels[i] == c]
        regimes_in = [regime_labels[i] for i in range(n_folios) if cluster_labels[i] == c]
        cluster_composition[f"cluster_{c}"] = {
            "size": len(members),
            "folios": members,
            "section_distribution": dict(Counter(sections_in)),
            "regime_distribution": dict(Counter(regimes_in)),
        }

    # Identify cross-section folios: folios in clusters where they are minority section
    cross_section_folios = []
    for c in range(1, k + 1):
        members_idx = [i for i in range(n_folios) if cluster_labels[i] == c]
        if not members_idx:
            continue
        sections_in = [section_labels[i] for i in members_idx]
        section_counts = Counter(sections_in)
        majority_section = section_counts.most_common(1)[0][0]
        for i in members_idx:
            if section_labels[i] != majority_section:
                cross_section_folios.append({
                    "folio": folios[i],
                    "folio_section": section_labels[i],
                    "cluster": int(c),
                    "cluster_majority_section": majority_section,
                    "cluster_majority_fraction": section_counts[majority_section] / len(members_idx),
                })

    results_per_k[k] = {
        "k": k,
        "ari_section": round(ari_section, 4),
        "nmi_section": round(nmi_section, 4),
        "ari_regime": round(ari_regime, 4),
        "nmi_regime": round(nmi_regime, 4),
        "cluster_composition": cluster_composition,
        "cross_section_folios": cross_section_folios,
        "n_cross_section": len(cross_section_folios),
    }

    print(f"\n  k={k}: ARI_section={ari_section:.4f}, NMI_section={nmi_section:.4f}, "
          f"ARI_regime={ari_regime:.4f}, NMI_regime={nmi_regime:.4f}, "
          f"cross-section={len(cross_section_folios)}")

# ============================================================
# 8. PERMUTATION NULL MODEL (10,000 shuffles)
# ============================================================
print("\nRunning permutation test (10,000 shuffles)...")
n_permutations = 10000
rng = np.random.RandomState(42)

# Use k=5 as primary test (midpoint)
primary_k = 5
primary_clusters = fcluster(linkage_matrix, t=primary_k, criterion='maxclust')
observed_ari_section = adjusted_rand_score(section_ints, primary_clusters)
observed_nmi_section = normalized_mutual_info_score(section_ints, primary_clusters)
observed_ari_regime = adjusted_rand_score(regime_ints, primary_clusters)
observed_nmi_regime = normalized_mutual_info_score(regime_ints, primary_clusters)

null_ari_section = np.zeros(n_permutations)
null_nmi_section = np.zeros(n_permutations)
null_ari_regime = np.zeros(n_permutations)
null_nmi_regime = np.zeros(n_permutations)

for perm in range(n_permutations):
    shuffled_section = rng.permutation(section_ints)
    shuffled_regime = rng.permutation(regime_ints)

    null_ari_section[perm] = adjusted_rand_score(shuffled_section, primary_clusters)
    null_nmi_section[perm] = normalized_mutual_info_score(shuffled_section, primary_clusters)
    null_ari_regime[perm] = adjusted_rand_score(shuffled_regime, primary_clusters)
    null_nmi_regime[perm] = normalized_mutual_info_score(shuffled_regime, primary_clusters)

# p-values: fraction of null >= observed
p_ari_section = (np.sum(null_ari_section >= observed_ari_section) + 1) / (n_permutations + 1)
p_nmi_section = (np.sum(null_nmi_section >= observed_nmi_section) + 1) / (n_permutations + 1)
p_ari_regime = (np.sum(null_ari_regime >= observed_ari_regime) + 1) / (n_permutations + 1)
p_nmi_regime = (np.sum(null_nmi_regime >= observed_nmi_regime) + 1) / (n_permutations + 1)

print(f"  Section ARI: observed={observed_ari_section:.4f}, "
      f"null_mean={null_ari_section.mean():.4f}, p={p_ari_section:.4f}")
print(f"  Section NMI: observed={observed_nmi_section:.4f}, "
      f"null_mean={null_nmi_section.mean():.4f}, p={p_nmi_section:.4f}")
print(f"  Regime ARI:  observed={observed_ari_regime:.4f}, "
      f"null_mean={null_ari_regime.mean():.4f}, p={p_ari_regime:.4f}")
print(f"  Regime NMI:  observed={observed_nmi_regime:.4f}, "
      f"null_mean={null_nmi_regime.mean():.4f}, p={p_nmi_regime:.4f}")

# ============================================================
# 9. BEYOND-SECTION ANALYSIS
# ============================================================
# Do clusters explain variance BEYOND section?
# Re-cluster residuals after removing section means
print("\nComputing residual clustering (section-corrected)...")

# Compute section-mean frequency vectors
section_means = {}
for s in unique_sections:
    s_indices = [i for i, sl in enumerate(section_labels) if sl == s]
    if s_indices:
        section_means[s] = freq_matrix[s_indices].mean(axis=0)

# Compute residuals
residual_matrix = np.zeros_like(freq_matrix)
for i, folio in enumerate(folios):
    s = section_labels[i]
    if s in section_means:
        residual_matrix[i] = freq_matrix[i] - section_means[s]

# Re-cluster residuals
residual_dist = pdist(residual_matrix, metric='cosine')
residual_dist = np.nan_to_num(residual_dist, nan=1.0)
residual_linkage = linkage(residual_dist, method='ward')

residual_results = {}
for k in [4, 5, 6]:
    res_clusters = fcluster(residual_linkage, t=k, criterion='maxclust')
    ari_section = adjusted_rand_score(section_ints, res_clusters)
    nmi_section = normalized_mutual_info_score(section_ints, res_clusters)
    ari_regime = adjusted_rand_score(regime_ints, res_clusters)
    nmi_regime = normalized_mutual_info_score(regime_ints, res_clusters)

    residual_results[k] = {
        "k": k,
        "ari_section": round(ari_section, 4),
        "nmi_section": round(nmi_section, 4),
        "ari_regime": round(ari_regime, 4),
        "nmi_regime": round(nmi_regime, 4),
    }
    print(f"  Residual k={k}: ARI_section={ari_section:.4f}, NMI_section={nmi_section:.4f}, "
          f"ARI_regime={ari_regime:.4f}, NMI_regime={nmi_regime:.4f}")

# ============================================================
# 10. TOP DISCRIMINATING MIDDLEs PER CLUSTER
# ============================================================
print("\nIdentifying discriminating MIDDLEs per cluster (k=5)...")
k5_clusters = fcluster(linkage_matrix, t=5, criterion='maxclust')
cluster_discriminators = {}

global_mean = freq_matrix.mean(axis=0)

for c in range(1, 6):
    c_indices = [i for i in range(n_folios) if k5_clusters[i] == c]
    if not c_indices:
        continue
    cluster_mean = freq_matrix[c_indices].mean(axis=0)
    # Enrichment ratio: cluster_mean / global_mean
    enrichment = np.zeros(n_middles)
    for j in range(n_middles):
        if global_mean[j] > 0:
            enrichment[j] = cluster_mean[j] / global_mean[j]

    # Top 8 enriched MIDDLEs
    top_indices = np.argsort(enrichment)[::-1][:8]
    top_middles = []
    for idx in top_indices:
        if enrichment[idx] > 1.0:  # only include actually enriched
            top_middles.append({
                "middle": common_middles[idx],
                "enrichment_ratio": round(float(enrichment[idx]), 2),
                "cluster_proportion": round(float(cluster_mean[idx]), 4),
                "global_proportion": round(float(global_mean[idx]), 4),
            })

    cluster_discriminators[f"cluster_{c}"] = top_middles

# ============================================================
# 11. VERDICT
# ============================================================
# Use k=5 as primary judgment
primary = results_per_k[5]
ari_s = primary['ari_section']
nmi_s = primary['nmi_section']

# Pass criteria: ARI > 0.15, NMI > 0.10, p < 0.01
# Fail criteria: ARI < 0.05
if ari_s > 0.15 and nmi_s > 0.10 and p_ari_section < 0.01:
    verdict = "PASS"
    verdict_detail = (f"Clusters significantly correspond to section (ARI={ari_s:.4f} > 0.15, "
                      f"NMI={nmi_s:.4f} > 0.10, p={p_ari_section:.4f} < 0.01)")
elif ari_s < 0.05:
    verdict = "FAIL"
    verdict_detail = f"Clusters do not meaningfully correspond to structure (ARI={ari_s:.4f} < 0.05)"
else:
    # Intermediate: check if residual clustering reveals beyond-section signal
    res_k5 = residual_results[5]
    if res_k5['ari_regime'] > 0.10 or res_k5['nmi_regime'] > 0.08:
        verdict = "PARTIAL_PASS"
        verdict_detail = (f"Section ARI={ari_s:.4f} (below 0.15 threshold), but residual "
                          f"clustering captures regime signal (residual ARI_regime="
                          f"{res_k5['ari_regime']:.4f}, NMI_regime={res_k5['nmi_regime']:.4f})")
    else:
        verdict = "INCONCLUSIVE"
        verdict_detail = (f"Section ARI={ari_s:.4f}, NMI={nmi_s:.4f} - between pass and fail "
                          f"thresholds, no clear beyond-section signal")

print(f"\nVERDICT: {verdict}")
print(f"  {verdict_detail}")

# ============================================================
# 12. ASSEMBLE OUTPUT
# ============================================================
output = {
    "test": "folio_vocabulary_clustering",
    "phase": "MATERIAL_LOCUS_SEARCH",
    "question": "Do folio-level MIDDLE profiles cluster into material-like categories beyond section/regime?",
    "method": {
        "description": "Hierarchical clustering of folio MIDDLE frequency vectors",
        "scope": "Currier B",
        "n_folios": n_folios,
        "n_common_middles": n_middles,
        "common_middle_threshold": "20+ folios",
        "common_middles": common_middles,
        "distance_metric": "cosine",
        "linkage_method": "ward",
        "k_values_tested": [4, 5, 6],
        "n_permutations": n_permutations,
        "primary_k": primary_k,
    },
    "similarity_summary": {
        "cosine": {
            "mean": round(float(cosine_triu.mean()), 4),
            "std": round(float(cosine_triu.std()), 4),
            "min": round(float(cosine_triu.min()), 4),
            "max": round(float(cosine_triu.max()), 4),
        },
        "jaccard": {
            "mean": round(float(jaccard_triu.mean()), 4),
            "std": round(float(jaccard_triu.std()), 4),
            "min": round(float(jaccard_triu.min()), 4),
            "max": round(float(jaccard_triu.max()), 4),
        },
    },
    "clustering_results": {str(k): v for k, v in results_per_k.items()},
    "permutation_test": {
        "primary_k": primary_k,
        "n_permutations": n_permutations,
        "section": {
            "observed_ari": round(float(observed_ari_section), 4),
            "null_mean_ari": round(float(null_ari_section.mean()), 4),
            "null_std_ari": round(float(null_ari_section.std()), 4),
            "p_value_ari": round(float(p_ari_section), 4),
            "observed_nmi": round(float(observed_nmi_section), 4),
            "null_mean_nmi": round(float(null_nmi_section.mean()), 4),
            "null_std_nmi": round(float(null_nmi_section.std()), 4),
            "p_value_nmi": round(float(p_nmi_section), 4),
        },
        "regime": {
            "observed_ari": round(float(observed_ari_regime), 4),
            "null_mean_ari": round(float(null_ari_regime.mean()), 4),
            "null_std_ari": round(float(null_ari_regime.std()), 4),
            "p_value_ari": round(float(p_ari_regime), 4),
            "observed_nmi": round(float(observed_nmi_regime), 4),
            "null_mean_nmi": round(float(null_nmi_regime.mean()), 4),
            "null_std_nmi": round(float(null_nmi_regime.std()), 4),
            "p_value_nmi": round(float(p_nmi_regime), 4),
        },
    },
    "residual_clustering": {
        "description": "Clustering after removing section-mean MIDDLE profiles",
        "results": {str(k): v for k, v in residual_results.items()},
    },
    "cluster_discriminators": {
        "description": "Top enriched MIDDLEs per cluster at k=5",
        "clusters": cluster_discriminators,
    },
    "folio_metadata": {
        f: {
            "section": section_labels[i],
            "regime": regime_labels[i],
            "n_tokens": int(folio_token_counts[f]),
            "cluster_k5": int(k5_clusters[i]),
        }
        for i, f in enumerate(folios)
    },
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "pass_criteria": "ARI > 0.15, NMI > 0.10, permutation p < 0.01",
    "fail_criteria": "ARI < 0.05 (clusters mirror section only)",
    "references": ["C909 (section MIDDLE vocabularies)", "C910 (regime MIDDLE clustering)"],
}

# ============================================================
# 13. WRITE OUTPUT
# ============================================================
output_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/folio_vocabulary_clustering.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {output_path}")
print("Done.")
