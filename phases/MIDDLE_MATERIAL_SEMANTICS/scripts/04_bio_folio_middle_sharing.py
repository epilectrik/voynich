"""
04_bio_folio_middle_sharing.py

Test 4: BIO Section MIDDLE Sharing Network

Question: Do BIO folios cluster into sub-groups sharing rare tail vocabulary?

Method:
1. Load H-track Currier B tokens from BIO section (section='B')
2. Extract MIDDLEs using canonical Morphology
3. Identify RARE middles: those appearing in 2-15 folios corpus-wide
4. Build Jaccard similarity matrix for BIO folios based on shared rare middles
5. Hierarchical clustering (Ward's method) on (1 - Jaccard) distance
6. Evaluate silhouette scores for k=2,3,4,5
7. Correlate Jaccard similarity with kernel-profile similarity (cosine)
"""

import json
import sys
import warnings
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.cluster.hierarchy import ward, fcluster
from scipy.spatial.distance import squareform
from scipy.stats import pearsonr
from sklearn.metrics import silhouette_score

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# ============================================================
# STEP 1: Load data and extract MIDDLEs
# ============================================================
print("=" * 70)
print("BIO SECTION MIDDLE SHARING NETWORK")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Collect all B tokens (corpus-wide) to determine per-middle folio counts
# Pre-compute: folio sets per middle across entire Currier B
corpus_middle_folios = defaultdict(set)  # middle -> set of folios it appears in
bio_folio_tokens = defaultdict(list)     # folio -> list of (word, middle)
bio_folio_words = defaultdict(list)      # folio -> list of words (for kernel profile)

for token in tx.currier_b():
    if '*' in token.word:
        continue
    if token.is_label:
        continue
    if not token.word.strip():
        continue

    m = morph.extract(token.word)
    middle = m.middle
    if middle and middle != '_EMPTY_':
        corpus_middle_folios[middle].add(token.folio)

    # Collect BIO-specific data
    if token.section == 'B':
        if middle and middle != '_EMPTY_':
            bio_folio_tokens[token.folio].append((token.word, middle))
        bio_folio_words[token.folio].append(token.word)

bio_folios = sorted(bio_folio_tokens.keys())
n_bio = len(bio_folios)
print(f"\nBIO folios: {n_bio}")
print(f"BIO folios: {bio_folios}")

# ============================================================
# STEP 2: Identify RARE middles (2-15 folios corpus-wide)
# ============================================================
rare_middles = {m for m, folios in corpus_middle_folios.items()
                if 2 <= len(folios) <= 15}
print(f"\nTotal unique MIDDLEs in Currier B: {len(corpus_middle_folios)}")
print(f"Rare MIDDLEs (2-15 folios): {len(rare_middles)}")

# ============================================================
# STEP 3: Build per-folio rare-middle sets (pre-compute)
# ============================================================
folio_rare_sets = {}
for folio in bio_folios:
    middles_in_folio = {mid for _, mid in bio_folio_tokens[folio]}
    folio_rare_sets[folio] = middles_in_folio & rare_middles

total_rare_in_bio = set()
for s in folio_rare_sets.values():
    total_rare_in_bio |= s
n_rare_in_bio = len(total_rare_in_bio)
print(f"Rare MIDDLEs present in BIO section: {n_rare_in_bio}")

for folio in bio_folios[:5]:
    print(f"  {folio}: {len(folio_rare_sets[folio])} rare MIDDLEs")

# ============================================================
# STEP 4: Build Jaccard similarity matrix
# ============================================================
print(f"\nBuilding {n_bio}x{n_bio} Jaccard similarity matrix...")

jaccard_matrix = np.zeros((n_bio, n_bio))
for i in range(n_bio):
    for j in range(n_bio):
        si = folio_rare_sets[bio_folios[i]]
        sj = folio_rare_sets[bio_folios[j]]
        union = si | sj
        if len(union) == 0:
            jaccard_matrix[i, j] = 0.0
        else:
            jaccard_matrix[i, j] = len(si & sj) / len(union)

# Report summary statistics
upper_tri = jaccard_matrix[np.triu_indices(n_bio, k=1)]
print(f"Jaccard statistics (upper triangle):")
print(f"  Mean: {np.mean(upper_tri):.4f}")
print(f"  Median: {np.median(upper_tri):.4f}")
print(f"  Std: {np.std(upper_tri):.4f}")
print(f"  Min: {np.min(upper_tri):.4f}, Max: {np.max(upper_tri):.4f}")

# ============================================================
# STEP 5: Hierarchical clustering (Ward's method)
# ============================================================
print("\nPerforming hierarchical clustering (Ward's method)...")

# Convert Jaccard similarity to distance
distance_matrix = 1.0 - jaccard_matrix
np.fill_diagonal(distance_matrix, 0.0)  # Ensure diagonal is exactly 0

# Ward's method requires condensed distance matrix
condensed_dist = squareform(distance_matrix, checks=False)
linkage_matrix = ward(condensed_dist)

# ============================================================
# STEP 6: Evaluate silhouette scores for k=2,3,4,5
# ============================================================
print("\nEvaluating cluster counts (silhouette scores):")
silhouette_scores = {}

for k in [2, 3, 4, 5]:
    labels = fcluster(linkage_matrix, t=k, criterion='maxclust')
    # Need at least 2 clusters with members for silhouette
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        silhouette_scores[str(k)] = None
        print(f"  k={k}: Only 1 cluster formed, silhouette=N/A")
        continue
    score = silhouette_score(distance_matrix, labels, metric='precomputed')
    silhouette_scores[str(k)] = round(float(score), 4)
    print(f"  k={k}: silhouette={score:.4f}")

# Find best k
valid_scores = {k: v for k, v in silhouette_scores.items() if v is not None}
if valid_scores:
    best_k = int(max(valid_scores, key=lambda k: valid_scores[k]))
    best_silhouette = valid_scores[str(best_k)]
else:
    best_k = 2
    best_silhouette = None

print(f"\nBest k: {best_k} (silhouette={best_silhouette})")

# ============================================================
# STEP 7: Extract cluster details for best k
# ============================================================
best_labels = fcluster(linkage_matrix, t=best_k, criterion='maxclust')
folio_to_cluster = {bio_folios[i]: int(best_labels[i]) for i in range(n_bio)}

clusters = {}
for cluster_id in sorted(set(best_labels)):
    cluster_folios = [bio_folios[i] for i in range(n_bio) if best_labels[i] == cluster_id]

    # Shared rare middles: present in ALL folios of the cluster
    if len(cluster_folios) == 1:
        shared_rares = sorted(folio_rare_sets[cluster_folios[0]])
    else:
        shared_rares = folio_rare_sets[cluster_folios[0]].copy()
        for f in cluster_folios[1:]:
            shared_rares &= folio_rare_sets[f]
        shared_rares = sorted(shared_rares)

    # Within-cluster mean Jaccard
    indices = [i for i in range(n_bio) if best_labels[i] == cluster_id]
    if len(indices) > 1:
        within_pairs = []
        for ii in range(len(indices)):
            for jj in range(ii + 1, len(indices)):
                within_pairs.append(jaccard_matrix[indices[ii], indices[jj]])
        within_jaccard = float(np.mean(within_pairs))
    else:
        within_jaccard = 1.0  # Single folio cluster

    # Cluster label is 0-indexed for output
    cluster_key = str(cluster_id - 1)
    clusters[cluster_key] = {
        "folios": cluster_folios,
        "n_folios": len(cluster_folios),
        "shared_rare_middles": shared_rares,
        "n_shared_rare_middles": len(shared_rares),
        "within_jaccard": round(within_jaccard, 4)
    }

    print(f"\n  Cluster {cluster_key}: {cluster_folios}")
    print(f"    Shared rare MIDDLEs ({len(shared_rares)}): {shared_rares[:10]}{'...' if len(shared_rares) > 10 else ''}")
    print(f"    Within-cluster Jaccard: {within_jaccard:.4f}")

# Between-cluster mean Jaccard
between_pairs = []
for i in range(n_bio):
    for j in range(i + 1, n_bio):
        if best_labels[i] != best_labels[j]:
            between_pairs.append(jaccard_matrix[i, j])

if between_pairs:
    between_cluster_jaccard = float(np.mean(between_pairs))
else:
    between_cluster_jaccard = 0.0

print(f"\n  Between-cluster mean Jaccard: {between_cluster_jaccard:.4f}")

# ============================================================
# STEP 8: Kernel profile similarity vs Jaccard correlation
# ============================================================
print("\n" + "=" * 70)
print("KERNEL PROFILE vs JACCARD CORRELATION")
print("=" * 70)

# Build kernel profile per folio: fraction of k, h, e characters in all words
KERNELS = {'k', 'h', 'e'}
folio_kernel_profiles = {}

for folio in bio_folios:
    k_count = 0
    h_count = 0
    e_count = 0
    total_chars = 0
    for word in bio_folio_words[folio]:
        for c in word:
            if c in KERNELS:
                if c == 'k':
                    k_count += 1
                elif c == 'h':
                    h_count += 1
                elif c == 'e':
                    e_count += 1
            total_chars += 1

    if total_chars > 0:
        folio_kernel_profiles[folio] = np.array([
            k_count / total_chars,
            h_count / total_chars,
            e_count / total_chars
        ])
    else:
        folio_kernel_profiles[folio] = np.array([0.0, 0.0, 0.0])

# Compute cosine similarity matrix for kernel profiles
def cosine_sim(a, b):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

kernel_sim_matrix = np.zeros((n_bio, n_bio))
for i in range(n_bio):
    for j in range(n_bio):
        kernel_sim_matrix[i, j] = cosine_sim(
            folio_kernel_profiles[bio_folios[i]],
            folio_kernel_profiles[bio_folios[j]]
        )

# Correlate upper triangles: Jaccard vs kernel cosine similarity
jaccard_upper = jaccard_matrix[np.triu_indices(n_bio, k=1)]
kernel_upper = kernel_sim_matrix[np.triu_indices(n_bio, k=1)]

# Pearson correlation
if len(jaccard_upper) > 2 and np.std(jaccard_upper) > 0 and np.std(kernel_upper) > 0:
    r_val, p_val = pearsonr(jaccard_upper, kernel_upper)
else:
    r_val, p_val = 0.0, 1.0

print(f"\nPearson r (Jaccard vs kernel cosine): {r_val:.4f}")
print(f"p-value: {p_val:.6f}")
print(f"N pairs: {len(jaccard_upper)}")

# ============================================================
# STEP 9: Verdict
# ============================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

# Criteria for SUPPORTED:
# 1. Best silhouette >= 0.15 (meaningful clustering exists)
# 2. Within-cluster Jaccard > between-cluster Jaccard for all clusters
# 3. At least 2 clusters with shared rare middles

has_good_silhouette = best_silhouette is not None and best_silhouette >= 0.15

all_within_gt_between = all(
    clusters[str(c)]["within_jaccard"] > between_cluster_jaccard
    for c in range(best_k)
    if clusters[str(c)]["n_folios"] > 1
)

clusters_with_shared = sum(
    1 for c in range(best_k)
    if clusters[str(c)]["n_shared_rare_middles"] > 0
)

verdict_reasons = []
if has_good_silhouette:
    verdict_reasons.append(f"Silhouette {best_silhouette:.4f} >= 0.15")
else:
    verdict_reasons.append(f"Silhouette {best_silhouette} < 0.15")

if all_within_gt_between:
    verdict_reasons.append("All within-cluster Jaccard > between-cluster")
else:
    verdict_reasons.append("Some within-cluster Jaccard <= between-cluster")

if clusters_with_shared >= 2:
    verdict_reasons.append(f"{clusters_with_shared} clusters have shared rare MIDDLEs")
else:
    verdict_reasons.append(f"Only {clusters_with_shared} clusters have shared rare MIDDLEs")

verdict = "SUPPORTED" if (has_good_silhouette and all_within_gt_between) else "NOT_SUPPORTED"

notes = (
    f"BIO folios cluster into {best_k} groups by rare MIDDLE sharing "
    f"(silhouette={best_silhouette}). "
    f"{'Within-cluster sharing exceeds between-cluster sharing.' if all_within_gt_between else 'Within/between distinction is weak.'} "
    f"Jaccard-kernel correlation r={r_val:.4f} (p={p_val:.4f})."
)

print(f"\nVerdict: {verdict}")
for reason in verdict_reasons:
    print(f"  - {reason}")
print(f"\n{notes}")

# ============================================================
# STEP 10: Save results
# ============================================================
output = {
    "test": "BIO Section MIDDLE Sharing Network",
    "n_bio_folios": n_bio,
    "n_rare_middles_in_bio": n_rare_in_bio,
    "rare_middle_definition": "MIDDLEs appearing in 2-15 folios corpus-wide (Currier B)",
    "best_k": best_k,
    "silhouette_scores": silhouette_scores,
    "clusters": clusters,
    "between_cluster_jaccard": round(between_cluster_jaccard, 4),
    "jaccard_vs_kernel_similarity_r": round(float(r_val), 4),
    "jaccard_vs_kernel_similarity_p": round(float(p_val), 6),
    "verdict": verdict,
    "notes": notes
}

output_path = results_dir / "bio_folio_middle_sharing.json"
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
