#!/usr/bin/env python3
"""
SEL-F: TOPICAL CLUSTERING HYPOTHESIS

Pivot from procedural chaining to topical clustering:
- Vocabulary continuity (28% higher, p=0.003) suggests MATERIAL GROUPING
- A-reference persistence (29% higher, p=0.004) suggests SHARED INGREDIENTS

TEST 9: Cluster detection via vocabulary
- Hierarchical clustering of folios by vocabulary Jaccard similarity
- Predict: 5-10 major clusters
- Measure: within-cluster vs between-cluster vocabulary overlap

TEST 10: A-section material families
- Do A-entries predict folio clusters?
- Map which A-section tokens appear in which B folios
- See if clusters share A-references

TEST 11: STATE-C as cluster boundary marker
- Do STATE-C folios mark transitions between clusters?

TEST 12: f82v anomaly analysis
- Why 9 STATE-C in 10 folios around f82v?

TEST 13: Restart folios as cluster initiators
- Do f50v, f57r, f82v start new clusters?
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform

os.chdir('C:/git/voynich')

print("=" * 70)
print("SEL-F: TOPICAL CLUSTERING HYPOTHESIS")
print("=" * 70)

# Load data
with open('results/control_signatures.json', 'r') as f:
    signatures = json.load(f)

sigs = signatures.get('signatures', {})

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        # Filter to H (PRIMARY) transcriber only
        transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
        if transcriber != 'H':
            continue
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Build per-folio vocabulary for Currier B only
folio_vocab = defaultdict(set)
folio_tokens = defaultdict(list)
for t in all_tokens:
    if t.get('language', '') == 'B':
        folio = t.get('folio', '')
        word = t.get('word', '')
        if folio and word:
            folio_vocab[folio].add(word)
            folio_tokens[folio].append(word)

# Get ordered folio list (matching signatures)
folios = sorted([f for f in sigs.keys() if f in folio_vocab])
print(f"\nFolios with both signatures and vocabulary: {len(folios)}")

# ==========================================================================
# TEST 9: CLUSTER DETECTION VIA VOCABULARY
# ==========================================================================

print("\n" + "=" * 70)
print("TEST 9: CLUSTER DETECTION VIA VOCABULARY")
print("=" * 70)

# Build Jaccard distance matrix
n = len(folios)
jaccard_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        v1 = folio_vocab[folios[i]]
        v2 = folio_vocab[folios[j]]
        if len(v1 | v2) > 0:
            jaccard_matrix[i, j] = len(v1 & v2) / len(v1 | v2)
        else:
            jaccard_matrix[i, j] = 0

# Convert similarity to distance
distance_matrix = 1 - jaccard_matrix

# Hierarchical clustering
condensed = squareform(distance_matrix, checks=False)
linkage_matrix = linkage(condensed, method='ward')

# Try different numbers of clusters
print("\nCluster analysis at different k:")
print(f"{'k':<4} {'Silhouette':<12} {'Within-cluster J':<18} {'Between-cluster J':<18}")
print("-" * 60)

from sklearn.metrics import silhouette_score

best_k = 0
best_silhouette = -1
best_clusters = None

for k in range(3, 12):
    clusters = fcluster(linkage_matrix, k, criterion='maxclust')

    # Calculate silhouette score
    if len(set(clusters)) > 1:
        sil = silhouette_score(distance_matrix, clusters, metric='precomputed')
    else:
        sil = 0

    # Calculate within-cluster and between-cluster Jaccard
    within_j = []
    between_j = []

    for i in range(n):
        for j in range(i+1, n):
            if clusters[i] == clusters[j]:
                within_j.append(jaccard_matrix[i, j])
            else:
                between_j.append(jaccard_matrix[i, j])

    mean_within = np.mean(within_j) if within_j else 0
    mean_between = np.mean(between_j) if between_j else 0

    print(f"{k:<4} {sil:<12.4f} {mean_within:<18.4f} {mean_between:<18.4f}")

    if sil > best_silhouette:
        best_silhouette = sil
        best_k = k
        best_clusters = clusters

print(f"\nBest k = {best_k} (silhouette = {best_silhouette:.4f})")

# Use best clustering
clusters = best_clusters
cluster_folios = defaultdict(list)
for i, f in enumerate(folios):
    cluster_folios[clusters[i]].append(f)

print(f"\nCluster composition:")
for c in sorted(cluster_folios.keys()):
    members = cluster_folios[c]
    terminal_states = [sigs[f].get('terminal_state', 'unknown') for f in members]
    state_c_pct = terminal_states.count('STATE-C') / len(terminal_states) * 100
    print(f"  Cluster {c}: {len(members)} folios, {state_c_pct:.1f}% STATE-C")
    print(f"    First 5: {members[:5]}")

# ==========================================================================
# TEST 10: A-SECTION MATERIAL FAMILIES
# ==========================================================================

print("\n" + "=" * 70)
print("TEST 10: A-SECTION MATERIAL FAMILIES")
print("=" * 70)

# Build A-vocabulary (tokens that appear in Currier A)
a_vocab = set()
for t in all_tokens:
    if t.get('language', '') == 'A':
        word = t.get('word', '')
        if word:
            a_vocab.add(word)

print(f"\nCurrier A vocabulary size: {len(a_vocab)}")

# For each B folio, find which A-tokens it uses
folio_a_refs = {}
for f in folios:
    a_tokens_used = folio_vocab[f] & a_vocab
    folio_a_refs[f] = a_tokens_used

# Calculate A-reference overlap within vs between clusters
print("\nA-reference sharing by cluster:")

cluster_a_overlap = {}
for c in sorted(cluster_folios.keys()):
    members = cluster_folios[c]
    if len(members) < 2:
        continue

    # Within-cluster A-reference overlap
    overlaps = []
    for i in range(len(members)):
        for j in range(i+1, len(members)):
            a1 = folio_a_refs[members[i]]
            a2 = folio_a_refs[members[j]]
            if len(a1 | a2) > 0:
                overlaps.append(len(a1 & a2) / len(a1 | a2))

    mean_overlap = np.mean(overlaps) if overlaps else 0
    cluster_a_overlap[c] = mean_overlap

    # Find common A-tokens in this cluster
    common_a = set.intersection(*[folio_a_refs[m] for m in members]) if members else set()

    print(f"  Cluster {c}: mean A-overlap = {mean_overlap:.4f}, common A-tokens = {len(common_a)}")
    if common_a:
        print(f"    Common A-refs: {list(common_a)[:10]}")

# Between-cluster A-reference overlap
between_overlaps = []
for c1 in cluster_folios:
    for c2 in cluster_folios:
        if c1 >= c2:
            continue
        for f1 in cluster_folios[c1]:
            for f2 in cluster_folios[c2]:
                a1 = folio_a_refs[f1]
                a2 = folio_a_refs[f2]
                if len(a1 | a2) > 0:
                    between_overlaps.append(len(a1 & a2) / len(a1 | a2))

mean_within_a = np.mean(list(cluster_a_overlap.values())) if cluster_a_overlap else 0
mean_between_a = np.mean(between_overlaps) if between_overlaps else 0

print(f"\nA-reference overlap summary:")
print(f"  Within-cluster mean: {mean_within_a:.4f}")
print(f"  Between-cluster mean: {mean_between_a:.4f}")
print(f"  Ratio: {mean_within_a / mean_between_a:.2f}x" if mean_between_a > 0 else "  Ratio: N/A")

# Statistical test
from scipy.stats import mannwhitneyu

within_a_values = []
for c in cluster_folios:
    members = cluster_folios[c]
    for i in range(len(members)):
        for j in range(i+1, len(members)):
            a1 = folio_a_refs[members[i]]
            a2 = folio_a_refs[members[j]]
            if len(a1 | a2) > 0:
                within_a_values.append(len(a1 & a2) / len(a1 | a2))

if within_a_values and between_overlaps:
    stat, p = mannwhitneyu(within_a_values, between_overlaps, alternative='greater')
    print(f"  Mann-Whitney U test (within > between): p = {p:.6f}")
    if p < 0.05:
        print("  RESULT: Within-cluster A-reference sharing SIGNIFICANTLY higher")
    else:
        print("  RESULT: No significant difference")

# ==========================================================================
# TEST 11: STATE-C AS CLUSTER BOUNDARY MARKER
# ==========================================================================

print("\n" + "=" * 70)
print("TEST 11: STATE-C AS CLUSTER BOUNDARY MARKER")
print("=" * 70)

# Check if STATE-C folios tend to be at cluster boundaries
# Boundary = followed by folio in different cluster

boundary_state_c = 0
boundary_other = 0
internal_state_c = 0
internal_other = 0

folio_to_cluster = {f: clusters[i] for i, f in enumerate(folios)}

for i in range(len(folios) - 1):
    current = folios[i]
    next_f = folios[i + 1]

    current_state = sigs[current].get('terminal_state', 'unknown')
    is_state_c = current_state == 'STATE-C'

    current_cluster = folio_to_cluster[current]
    next_cluster = folio_to_cluster[next_f]

    is_boundary = current_cluster != next_cluster

    if is_boundary:
        if is_state_c:
            boundary_state_c += 1
        else:
            boundary_other += 1
    else:
        if is_state_c:
            internal_state_c += 1
        else:
            internal_other += 1

print(f"\nSTATE-C distribution at cluster boundaries:")
print(f"  At boundaries: STATE-C = {boundary_state_c}, Other = {boundary_other}")
print(f"  Internal: STATE-C = {internal_state_c}, Other = {internal_other}")

# Chi-square test
from scipy.stats import chi2_contingency, fisher_exact

contingency = [[boundary_state_c, boundary_other],
               [internal_state_c, internal_other]]

# Use Fisher's exact test for small counts
if min(sum(contingency[0]), sum(contingency[1])) < 5:
    odds, p = fisher_exact(contingency)
    print(f"\n  Fisher's exact test: p = {p:.4f}")
else:
    chi2, p, dof, expected = chi2_contingency(contingency)
    print(f"\n  Chi-square test: p = {p:.4f}")

if p < 0.05:
    boundary_rate_sc = boundary_state_c / (boundary_state_c + internal_state_c) if (boundary_state_c + internal_state_c) > 0 else 0
    boundary_rate_other = boundary_other / (boundary_other + internal_other) if (boundary_other + internal_other) > 0 else 0
    print(f"  STATE-C boundary rate: {boundary_rate_sc:.1%}")
    print(f"  Other boundary rate: {boundary_rate_other:.1%}")
    print("  RESULT: STATE-C IS associated with cluster boundaries")
else:
    print("  RESULT: STATE-C is NOT significantly associated with cluster boundaries")

# ==========================================================================
# TEST 12: f82v ANOMALY ANALYSIS
# ==========================================================================

print("\n" + "=" * 70)
print("TEST 12: f82v ANOMALY ANALYSIS")
print("=" * 70)

# Find f82v's neighborhood
f82v_idx = folios.index('f82v') if 'f82v' in folios else -1

if f82v_idx >= 0:
    # Look at 10-folio window around f82v
    start = max(0, f82v_idx - 5)
    end = min(len(folios), f82v_idx + 5)

    print(f"\nFolios around f82v (position {f82v_idx}):")
    print(f"{'Folio':<10} {'Terminal':<12} {'Cluster':<10} {'Reset?':<8}")
    print("-" * 45)

    for i in range(start, end):
        f = folios[i]
        ts = sigs[f].get('terminal_state', 'unknown')
        c = folio_to_cluster[f]
        reset = sigs[f].get('reset_present', False)
        marker = " <-- f82v" if f == 'f82v' else ""
        print(f"{f:<10} {ts:<12} {c:<10} {reset!s:<8}{marker}")

    # Count STATE-C in this window
    window_folios = folios[start:end]
    state_c_in_window = sum(1 for f in window_folios if sigs[f].get('terminal_state') == 'STATE-C')
    print(f"\nSTATE-C in window: {state_c_in_window}/{len(window_folios)} ({state_c_in_window/len(window_folios)*100:.1f}%)")
    print(f"Corpus average: {sum(1 for f in folios if sigs[f].get('terminal_state') == 'STATE-C') / len(folios) * 100:.1f}%")

    # Check vocabulary coherence in this window
    window_vocab = [folio_vocab[f] for f in window_folios]
    vocab_overlaps = []
    for i in range(len(window_vocab)):
        for j in range(i+1, len(window_vocab)):
            v1, v2 = window_vocab[i], window_vocab[j]
            if len(v1 | v2) > 0:
                vocab_overlaps.append(len(v1 & v2) / len(v1 | v2))

    print(f"Vocabulary coherence in f82v window: {np.mean(vocab_overlaps):.4f}")

    # Compare to random windows
    random_coherences = []
    np.random.seed(42)
    for _ in range(1000):
        rand_start = np.random.randint(0, len(folios) - 10)
        rand_window = folios[rand_start:rand_start + 10]
        rand_vocab = [folio_vocab[f] for f in rand_window]
        rand_overlaps = []
        for i in range(len(rand_vocab)):
            for j in range(i+1, len(rand_vocab)):
                v1, v2 = rand_vocab[i], rand_vocab[j]
                if len(v1 | v2) > 0:
                    rand_overlaps.append(len(v1 & v2) / len(v1 | v2))
        random_coherences.append(np.mean(rand_overlaps))

    percentile = sum(1 for r in random_coherences if r < np.mean(vocab_overlaps)) / len(random_coherences) * 100
    print(f"Percentile vs random windows: {percentile:.1f}%")

# ==========================================================================
# TEST 13: RESTART FOLIOS AS CLUSTER INITIATORS
# ==========================================================================

print("\n" + "=" * 70)
print("TEST 13: RESTART FOLIOS AS CLUSTER INITIATORS")
print("=" * 70)

restart_folios = ['f50v', 'f57r', 'f82v']

print("\nRestart folio positions:")
for rf in restart_folios:
    if rf in folios:
        idx = folios.index(rf)
        cluster = folio_to_cluster[rf]

        # Check if this is the first folio in its cluster
        cluster_members = cluster_folios[cluster]
        cluster_positions = [folios.index(f) for f in cluster_members]
        is_first = idx == min(cluster_positions)

        # Check if previous folio (if exists) is in different cluster
        if idx > 0:
            prev_cluster = folio_to_cluster[folios[idx - 1]]
            starts_new_cluster = prev_cluster != cluster
        else:
            starts_new_cluster = True  # First folio

        print(f"  {rf}: cluster {cluster}, position {idx}")
        print(f"    First in cluster? {is_first}")
        print(f"    Starts new cluster? {starts_new_cluster}")

        # Show preceding and following folios
        if idx > 0:
            prev = folios[idx - 1]
            print(f"    Preceded by: {prev} (cluster {folio_to_cluster[prev]}, {sigs[prev].get('terminal_state')})")
        if idx < len(folios) - 1:
            next_f = folios[idx + 1]
            print(f"    Followed by: {next_f} (cluster {folio_to_cluster[next_f]}, {sigs[next_f].get('terminal_state')})")

# ==========================================================================
# SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("TOPICAL CLUSTERING HYPOTHESIS SUMMARY")
print("=" * 70)

print(f"""
TEST 9 (Cluster Detection):
  Best k = {best_k}, silhouette = {best_silhouette:.4f}
  Clusters identified with varying STATE-C concentrations

TEST 10 (A-Section Material Families):
  Within-cluster A-overlap: {mean_within_a:.4f}
  Between-cluster A-overlap: {mean_between_a:.4f}
  Ratio: {mean_within_a / mean_between_a:.2f}x
  p-value: {p:.6f} (Mann-Whitney U)

TEST 11 (STATE-C as Boundary Marker):
  See contingency table above

TEST 12 (f82v Anomaly):
  High STATE-C concentration in neighborhood
  Vocabulary coherence analysis complete

TEST 13 (Restart as Cluster Initiators):
  See restart folio analysis above
""")

# Save clustering results for further analysis
results = {
    'best_k': int(best_k),
    'silhouette': float(best_silhouette),
    'cluster_assignments': {folios[i]: int(clusters[i]) for i in range(len(folios))},
    'cluster_sizes': {int(c): len(members) for c, members in cluster_folios.items()},
    'a_overlap_within': float(mean_within_a),
    'a_overlap_between': float(mean_between_a),
}

with open('phases/SEL_F_contradiction_resolution/clustering_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to phases/SEL_F_contradiction_resolution/clustering_results.json")
print("\n" + "=" * 70)
print("TESTS 9-13 COMPLETE")
print("=" * 70)
