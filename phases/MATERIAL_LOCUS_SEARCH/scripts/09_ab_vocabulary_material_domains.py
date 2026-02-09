#!/usr/bin/env python3
"""
MATERIAL_LOCUS_SEARCH Phase - Test 9: A Folio Vocabulary Overlap by Material Domain

Question: Do A folios specialize in covering specific B sections?

Method:
1. Extract MIDDLE vocabulary per A folio.
2. Extract combined MIDDLE vocabulary per B section (B, H, S, T, C, P).
3. Compute Jaccard similarity of each A folio's MIDDLE set against each B section's
   MIDDLE set -> 'reach vector' per A folio.
4. Cluster A folios by reach vectors (hierarchical, Ward linkage, k=3-5).
5. Test whether A folio clusters correspond to B-section reach specialization (ARI).
6. Null model: permute A folio labels and re-cluster (1000 permutations).
7. Supplementary: for each A folio, which B section has highest reach? Is there
   systematic specialization?

Pass: ARI > 0.10, A folios specialize in specific B sections.
Fail: A folios cover all B sections uniformly (generic pool, per C846).

References: C846 (A/B paragraph pool relationship).
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
print("Loading transcript and extracting MIDDLEs...")
tx = Transcript()
morph = Morphology()

# -- Currier A: per-folio MIDDLE sets --
a_folio_middles = defaultdict(set)  # folio -> set of MIDDLEs
a_folio_token_counts = Counter()

for token in tx.currier_a():
    m = morph.extract(token.word)
    middle = m.middle
    if middle and middle != '_EMPTY_':
        a_folio_middles[token.folio].add(middle)
        a_folio_token_counts[token.folio] += 1

a_folios = sorted(a_folio_middles.keys())
n_a_folios = len(a_folios)
print(f"  Currier A folios with MIDDLE data: {n_a_folios}")

# -- Currier B: per-section MIDDLE sets --
b_section_middles = defaultdict(set)  # section -> set of MIDDLEs
b_section_token_counts = Counter()
b_folio_sections = defaultdict(set)   # track which folios are in which sections

for token in tx.currier_b():
    section = token.section
    m = morph.extract(token.word)
    middle = m.middle
    if middle and middle != '_EMPTY_':
        b_section_middles[section].add(middle)
        b_section_token_counts[section] += 1
        b_folio_sections[section].add(token.folio)

b_sections = sorted(b_section_middles.keys())
print(f"  Currier B sections with MIDDLE data: {b_sections}")
for s in b_sections:
    print(f"    Section {s}: {len(b_section_middles[s])} unique MIDDLEs, "
          f"{b_section_token_counts[s]} tokens, {len(b_folio_sections[s])} folios")

if len(b_sections) < 2:
    print("ERROR: Too few B sections for meaningful analysis. Aborting.")
    sys.exit(1)

# ============================================================
# 2. COMPUTE REACH VECTORS (Jaccard similarity per A folio vs each B section)
# ============================================================
print("\nComputing reach vectors (Jaccard of A folio MIDDLEs vs B section MIDDLEs)...")

n_b_sections = len(b_sections)
reach_matrix = np.zeros((n_a_folios, n_b_sections))

for i, folio in enumerate(a_folios):
    a_set = a_folio_middles[folio]
    for j, section in enumerate(b_sections):
        b_set = b_section_middles[section]
        intersection = len(a_set & b_set)
        union = len(a_set | b_set)
        if union > 0:
            reach_matrix[i, j] = intersection / union
        else:
            reach_matrix[i, j] = 0.0

# Summary statistics for reach vectors
print(f"\nReach matrix shape: {reach_matrix.shape}")
print("Per-section reach statistics:")
for j, section in enumerate(b_sections):
    col = reach_matrix[:, j]
    print(f"  Section {section}: mean={col.mean():.4f}, std={col.std():.4f}, "
          f"min={col.min():.4f}, max={col.max():.4f}")

# ============================================================
# 3. IDENTIFY DOMINANT B SECTION PER A FOLIO
# ============================================================
print("\nIdentifying dominant B section per A folio...")

folio_dominant_section = {}
folio_reach_profiles = {}

for i, folio in enumerate(a_folios):
    reach_vec = reach_matrix[i, :]
    dominant_idx = np.argmax(reach_vec)
    dominant_section = b_sections[dominant_idx]
    folio_dominant_section[folio] = dominant_section
    folio_reach_profiles[folio] = {
        b_sections[j]: round(float(reach_vec[j]), 4) for j in range(n_b_sections)
    }

dominant_counts = Counter(folio_dominant_section.values())
print(f"  Dominant B section distribution: {dict(dominant_counts)}")

# Compute specialization index per folio: max_reach / mean_reach
# High = specialized, ~1 = uniform
specialization_indices = []
for i, folio in enumerate(a_folios):
    reach_vec = reach_matrix[i, :]
    mean_r = reach_vec.mean()
    max_r = reach_vec.max()
    spec_idx = max_r / mean_r if mean_r > 0 else 0.0
    specialization_indices.append(spec_idx)

specialization_indices = np.array(specialization_indices)
print(f"  Specialization index (max/mean): mean={specialization_indices.mean():.3f}, "
      f"std={specialization_indices.std():.3f}, "
      f"range=[{specialization_indices.min():.3f}, {specialization_indices.max():.3f}]")
print(f"  (1.0 = perfectly uniform, higher = more specialized)")

# ============================================================
# 4. HIERARCHICAL CLUSTERING OF A FOLIOS BY REACH VECTORS
# ============================================================
print("\nRunning hierarchical clustering on reach vectors...")
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# Filter out A folios with very few tokens (< 10) to avoid noise
MIN_TOKENS = 10
valid_mask = np.array([a_folio_token_counts[f] >= MIN_TOKENS for f in a_folios])
valid_folios = [f for f, v in zip(a_folios, valid_mask) if v]
valid_reach = reach_matrix[valid_mask]
n_valid = len(valid_folios)

print(f"  Folios with >= {MIN_TOKENS} tokens: {n_valid}/{n_a_folios}")

if n_valid < 6:
    print("ERROR: Too few valid A folios for clustering. Aborting.")
    sys.exit(1)

# Euclidean distance on reach vectors (they are already low-dimensional)
reach_dist = pdist(valid_reach, metric='euclidean')

linkage_matrix = linkage(reach_dist, method='ward')

# ============================================================
# 5. CLUSTER AT k=3,4,5 AND EVALUATE
# ============================================================
from sklearn.metrics import adjusted_rand_score, silhouette_score

# Build dominant-section labels for valid folios
valid_dominant = [folio_dominant_section[f] for f in valid_folios]
valid_dominant_ints = np.array([b_sections.index(d) if d in b_sections else -1
                                 for d in valid_dominant])

results_per_k = {}
best_ari = -1
best_k = 3

for k in [3, 4, 5]:
    cluster_labels = fcluster(linkage_matrix, t=k, criterion='maxclust')

    # Silhouette score
    if k < n_valid:
        sil = silhouette_score(valid_reach, cluster_labels, metric='euclidean')
    else:
        sil = 0.0

    # ARI: cluster assignment vs dominant-section assignment
    ari_dominant = adjusted_rand_score(valid_dominant_ints, cluster_labels)

    # Cluster composition
    cluster_composition = {}
    for c in range(1, k + 1):
        members = [valid_folios[i] for i in range(n_valid) if cluster_labels[i] == c]
        dominants_in = [valid_dominant[i] for i in range(n_valid) if cluster_labels[i] == c]

        # Compute mean reach vector for cluster
        c_indices = [i for i in range(n_valid) if cluster_labels[i] == c]
        if c_indices:
            mean_reach = valid_reach[c_indices].mean(axis=0)
            reach_profile = {b_sections[j]: round(float(mean_reach[j]), 4)
                             for j in range(n_b_sections)}
        else:
            reach_profile = {}

        cluster_composition[f"cluster_{c}"] = {
            "size": len(members),
            "folios": members,
            "dominant_section_distribution": dict(Counter(dominants_in)),
            "mean_reach_profile": reach_profile,
        }

    results_per_k[k] = {
        "k": k,
        "ari_vs_dominant_section": round(ari_dominant, 4),
        "silhouette": round(sil, 4),
        "cluster_composition": cluster_composition,
    }

    if ari_dominant > best_ari:
        best_ari = ari_dominant
        best_k = k

    print(f"  k={k}: ARI_dominant={ari_dominant:.4f}, silhouette={sil:.4f}")

# ============================================================
# 6. PERMUTATION NULL MODEL (1000 permutations)
# ============================================================
print("\nRunning permutation test (1000 shuffles)...")
n_permutations = 1000
rng = np.random.RandomState(42)

# Use best_k for primary test
primary_k = best_k
primary_clusters = fcluster(linkage_matrix, t=primary_k, criterion='maxclust')
observed_ari = adjusted_rand_score(valid_dominant_ints, primary_clusters)

null_ari = np.zeros(n_permutations)
for perm in range(n_permutations):
    shuffled_labels = rng.permutation(valid_dominant_ints)
    null_ari[perm] = adjusted_rand_score(shuffled_labels, primary_clusters)

p_value_ari = (np.sum(null_ari >= observed_ari) + 1) / (n_permutations + 1)

print(f"  Primary k={primary_k}: observed ARI={observed_ari:.4f}, "
      f"null_mean={null_ari.mean():.4f}, null_std={null_ari.std():.4f}, "
      f"p={p_value_ari:.4f}")

# ============================================================
# 7. REACH ENTROPY ANALYSIS
# ============================================================
# For each A folio, compute entropy of its reach vector
# Low entropy = specialized, high entropy = uniform
print("\nComputing reach entropy per A folio...")

def reach_entropy(vec):
    """Shannon entropy of normalized reach vector."""
    total = vec.sum()
    if total == 0:
        return 0.0
    p = vec / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))

max_entropy = np.log2(n_b_sections)  # uniform distribution entropy
folio_entropies = {}
for i, folio in enumerate(a_folios):
    h = reach_entropy(reach_matrix[i])
    folio_entropies[folio] = round(h, 4)

entropy_vals = np.array(list(folio_entropies.values()))
print(f"  Reach entropy: mean={entropy_vals.mean():.3f}, std={entropy_vals.std():.3f}, "
      f"range=[{entropy_vals.min():.3f}, {entropy_vals.max():.3f}]")
print(f"  Max possible entropy (uniform): {max_entropy:.3f}")
print(f"  Mean/max ratio: {entropy_vals.mean() / max_entropy:.3f} "
      f"(1.0 = perfectly uniform)")

# ============================================================
# 8. PAIRWISE A-FOLIO REACH SIMILARITY
# ============================================================
print("\nComputing pairwise A-folio reach similarity...")
# Are A folios diverse in their reach patterns or all similar?
from numpy.linalg import norm

# Cosine similarity of reach vectors
norms = norm(reach_matrix, axis=1, keepdims=True)
norms[norms == 0] = 1.0
normed = reach_matrix / norms
cosine_sim = normed @ normed.T
triu_indices = np.triu_indices(n_a_folios, k=1)
cosine_triu = cosine_sim[triu_indices]

print(f"  Pairwise cosine similarity of reach vectors:")
print(f"    mean={cosine_triu.mean():.4f}, std={cosine_triu.std():.4f}, "
      f"range=[{cosine_triu.min():.4f}, {cosine_triu.max():.4f}]")
print(f"  (High mean + low std = all A folios reach B sections similarly = generic)")

# ============================================================
# 9. REACH CONCENTRATION TEST
# ============================================================
# For each B section, do specific A folios have significantly higher reach?
print("\nReach concentration test per B section...")
section_reach_spread = {}
for j, section in enumerate(b_sections):
    col = reach_matrix[:, j]
    # Coefficient of variation
    cv = col.std() / col.mean() if col.mean() > 0 else 0.0
    # Top 5 A folios for this section
    top5_idx = np.argsort(col)[::-1][:5]
    top5 = [(a_folios[idx], round(float(col[idx]), 4)) for idx in top5_idx]

    section_reach_spread[section] = {
        "mean_reach": round(float(col.mean()), 4),
        "std_reach": round(float(col.std()), 4),
        "cv": round(float(cv), 4),
        "top_5_a_folios": [{"folio": f, "jaccard": j_val} for f, j_val in top5],
    }
    print(f"  Section {section}: mean={col.mean():.4f}, std={col.std():.4f}, "
          f"CV={cv:.3f}")

# ============================================================
# 10. VERDICT
# ============================================================
# Primary metric: ARI of clustering vs dominant section
# Secondary: entropy ratio, pairwise similarity spread

ari_primary = results_per_k[best_k]['ari_vs_dominant_section']
entropy_ratio = float(entropy_vals.mean() / max_entropy)
cosine_mean = float(cosine_triu.mean())
cosine_std = float(cosine_triu.std())

print(f"\n{'='*60}")
print(f"PRIMARY METRICS:")
print(f"  Best k={best_k}, ARI vs dominant section = {ari_primary:.4f}")
print(f"  Permutation p-value = {p_value_ari:.4f}")
print(f"  Entropy ratio (mean/max) = {entropy_ratio:.3f}")
print(f"  Pairwise reach similarity: mean={cosine_mean:.4f}, std={cosine_std:.4f}")

# Decision logic
if ari_primary > 0.10 and p_value_ari < 0.05:
    verdict = "PASS"
    verdict_detail = (
        f"A folios specialize in specific B sections. "
        f"ARI={ari_primary:.4f} > 0.10 (p={p_value_ari:.4f}). "
        f"Reach entropy ratio={entropy_ratio:.3f} indicates "
        f"{'moderate' if entropy_ratio < 0.85 else 'high'} B-section differentiation."
    )
elif ari_primary < 0.05 and entropy_ratio > 0.90 and cosine_std < 0.05:
    verdict = "FAIL"
    verdict_detail = (
        f"A folios cover all B sections uniformly (generic pool). "
        f"ARI={ari_primary:.4f} < 0.05, entropy ratio={entropy_ratio:.3f} near 1.0, "
        f"pairwise reach similarity std={cosine_std:.4f} very low. "
        f"Consistent with C846 (shared vocabulary pool)."
    )
elif entropy_ratio > 0.90 and cosine_mean > 0.95:
    verdict = "FAIL"
    verdict_detail = (
        f"A folios reach B sections nearly uniformly. "
        f"ARI={ari_primary:.4f}, entropy ratio={entropy_ratio:.3f} near 1.0, "
        f"pairwise cosine mean={cosine_mean:.4f} very high (all reach vectors similar). "
        f"No B-section specialization detected."
    )
else:
    verdict = "PARTIAL"
    verdict_detail = (
        f"Intermediate result: some differentiation but below specialization threshold. "
        f"ARI={ari_primary:.4f}, entropy ratio={entropy_ratio:.3f}, "
        f"p={p_value_ari:.4f}. "
        f"A folios show mild preferences but not strong specialization."
    )

print(f"\nVERDICT: {verdict}")
print(f"  {verdict_detail}")

# ============================================================
# 11. ASSEMBLE OUTPUT
# ============================================================
output = {
    "test": "ab_vocabulary_material_domains",
    "phase": "MATERIAL_LOCUS_SEARCH",
    "question": "Do A folios specialize in covering specific B sections?",
    "method": {
        "description": "Jaccard similarity of A folio MIDDLE vocabulary against each B section vocabulary, then cluster A folios by reach vectors",
        "scope": "Currier A folios vs Currier B sections",
        "n_a_folios": n_a_folios,
        "n_a_folios_valid": n_valid,
        "min_token_threshold": MIN_TOKENS,
        "b_sections": b_sections,
        "b_section_vocabulary_sizes": {s: len(b_section_middles[s]) for s in b_sections},
        "b_section_token_counts": {s: int(b_section_token_counts[s]) for s in b_sections},
        "b_section_folio_counts": {s: len(b_folio_sections[s]) for s in b_sections},
        "distance_metric": "euclidean (on reach vectors)",
        "linkage_method": "ward",
        "k_values_tested": [3, 4, 5],
        "primary_k": primary_k,
        "n_permutations": n_permutations,
    },
    "reach_summary": {
        "per_section": {
            section: {
                "mean": round(float(reach_matrix[:, j].mean()), 4),
                "std": round(float(reach_matrix[:, j].std()), 4),
                "min": round(float(reach_matrix[:, j].min()), 4),
                "max": round(float(reach_matrix[:, j].max()), 4),
            }
            for j, section in enumerate(b_sections)
        },
        "pairwise_reach_cosine": {
            "mean": round(float(cosine_mean), 4),
            "std": round(float(cosine_std), 4),
            "min": round(float(cosine_triu.min()), 4),
            "max": round(float(cosine_triu.max()), 4),
        },
    },
    "dominant_section_analysis": {
        "distribution": dict(dominant_counts),
        "per_folio": {
            folio: {
                "dominant_section": folio_dominant_section[folio],
                "reach_profile": folio_reach_profiles[folio],
                "n_tokens": int(a_folio_token_counts[folio]),
                "entropy": folio_entropies[folio],
                "specialization_index": round(float(specialization_indices[i]), 3),
            }
            for i, folio in enumerate(a_folios)
        },
    },
    "entropy_analysis": {
        "max_possible_entropy": round(float(max_entropy), 4),
        "mean_entropy": round(float(entropy_vals.mean()), 4),
        "std_entropy": round(float(entropy_vals.std()), 4),
        "entropy_ratio": round(entropy_ratio, 4),
        "interpretation": (
            "uniform" if entropy_ratio > 0.90 else
            "mild_preference" if entropy_ratio > 0.75 else
            "specialized"
        ),
    },
    "clustering_results": {str(k): v for k, v in results_per_k.items()},
    "permutation_test": {
        "primary_k": primary_k,
        "n_permutations": n_permutations,
        "observed_ari": round(float(observed_ari), 4),
        "null_mean_ari": round(float(null_ari.mean()), 4),
        "null_std_ari": round(float(null_ari.std()), 4),
        "p_value_ari": round(float(p_value_ari), 4),
    },
    "section_reach_spread": section_reach_spread,
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "pass_criteria": "ARI > 0.10, p < 0.05; A folios specialize in specific B sections",
    "fail_criteria": "A folios cover all B sections uniformly (generic pool, C846)",
    "references": ["C846 (A/B paragraph pool relationship)"],
}

# ============================================================
# 12. WRITE OUTPUT
# ============================================================
output_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/ab_vocabulary_material_domains.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {output_path}")
print("Done.")
