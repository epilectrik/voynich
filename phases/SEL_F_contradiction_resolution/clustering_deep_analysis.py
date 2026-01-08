#!/usr/bin/env python3
"""
Deep analysis of clustering results.
- Why is Cluster 3 (f75-f84 area) so different?
- Is there a refinement gradient?
- What do the cluster compositions tell us?
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import mannwhitneyu, spearmanr

os.chdir('C:/git/voynich')

print("=" * 70)
print("CLUSTERING DEEP ANALYSIS")
print("=" * 70)

# Load data
with open('results/control_signatures.json', 'r') as f:
    signatures = json.load(f)

sigs = signatures.get('signatures', {})

with open('phases/SEL_F_contradiction_resolution/clustering_results.json', 'r') as f:
    clustering = json.load(f)

cluster_assignments = clustering['cluster_assignments']

# Load transcription
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Build vocabularies
folio_vocab = defaultdict(set)
a_vocab = set()

for t in all_tokens:
    word = t.get('word', '')
    if t.get('language', '') == 'B':
        folio = t.get('folio', '')
        if folio and word:
            folio_vocab[folio].add(word)
    elif t.get('language', '') == 'A':
        if word:
            a_vocab.add(word)

folios = sorted(cluster_assignments.keys())

# ==========================================================================
# CLUSTER PROFILE ANALYSIS
# ==========================================================================

print("\n" + "=" * 70)
print("CLUSTER PROFILE ANALYSIS")
print("=" * 70)

cluster_folios = defaultdict(list)
for f, c in cluster_assignments.items():
    cluster_folios[c].append(f)

for c in sorted(cluster_folios.keys()):
    members = sorted(cluster_folios[c], key=lambda x: folios.index(x))

    print(f"\nCLUSTER {c} ({len(members)} folios)")
    print("-" * 50)

    # Folio range
    positions = [folios.index(f) for f in members]
    print(f"  Position range: {min(positions)} - {max(positions)}")
    print(f"  Folios: {members[0]} to {members[-1]}")

    # Terminal state distribution
    terminal_states = Counter(sigs[f].get('terminal_state', 'unknown') for f in members)
    print(f"  Terminal states: {dict(terminal_states)}")

    # Kernel dominance
    kernel_dom = Counter(sigs[f].get('kernel_dominance', 'unknown') for f in members)
    print(f"  Kernel dominance: {dict(kernel_dom)}")

    # A-reference profile
    a_refs = [folio_vocab[f] & a_vocab for f in members]
    all_a_in_cluster = set.union(*a_refs) if a_refs else set()
    common_a = set.intersection(*a_refs) if a_refs else set()

    print(f"  Total A-refs used: {len(all_a_in_cluster)}")
    print(f"  Common to all: {len(common_a)}")
    if common_a:
        print(f"    {list(common_a)[:15]}")

    # Vocabulary size
    vocab_sizes = [len(folio_vocab[f]) for f in members]
    print(f"  Mean vocab size: {np.mean(vocab_sizes):.1f} (std {np.std(vocab_sizes):.1f})")

    # Stability metrics
    stabilities = [sigs[f].get('stability_score', 0) for f in members]
    print(f"  Mean stability: {np.mean(stabilities):.3f}")

# ==========================================================================
# CLUSTER 3 SPECIAL ANALYSIS (f75-f84 "completion zone")
# ==========================================================================

print("\n" + "=" * 70)
print("CLUSTER 3 SPECIAL ANALYSIS (High STATE-C Zone)")
print("=" * 70)

c3_members = sorted(cluster_folios[3], key=lambda x: folios.index(x))

print(f"\nCluster 3 members in order:")
for f in c3_members:
    ts = sigs[f].get('terminal_state', 'unknown')
    kd = sigs[f].get('kernel_dominance', '?')
    kcr = sigs[f].get('kernel_contact_ratio', 0)
    reset = sigs[f].get('reset_present', False)

    marker = ""
    if reset:
        marker = " <-- RESET"

    print(f"  {f}: {ts}, kernel={kd}, kcr={kcr:.3f}{marker}")

# What makes Cluster 3 special?
print("\nCluster 3 vs Others comparison:")

c3_folios = cluster_folios[3]
other_folios = [f for c, members in cluster_folios.items() if c != 3 for f in members]

# Terminal state ratio
c3_statec = sum(1 for f in c3_folios if sigs[f].get('terminal_state') == 'STATE-C') / len(c3_folios)
other_statec = sum(1 for f in other_folios if sigs[f].get('terminal_state') == 'STATE-C') / len(other_folios)
print(f"  STATE-C rate: Cluster 3 = {c3_statec:.1%}, Others = {other_statec:.1%}")

# Stability score
c3_stab = np.mean([sigs[f].get('stability_score', 0) for f in c3_folios])
other_stab = np.mean([sigs[f].get('stability_score', 0) for f in other_folios])
print(f"  Mean stability: Cluster 3 = {c3_stab:.3f}, Others = {other_stab:.3f}")

# Kernel contact ratio
c3_kcr = np.mean([sigs[f].get('kernel_contact_ratio', 0) for f in c3_folios])
other_kcr = np.mean([sigs[f].get('kernel_contact_ratio', 0) for f in other_folios])
print(f"  Mean kernel contact: Cluster 3 = {c3_kcr:.3f}, Others = {other_kcr:.3f}")

# A-reference overlap (within cluster)
def mean_pairwise_jaccard(folio_list):
    overlaps = []
    for i in range(len(folio_list)):
        for j in range(i+1, len(folio_list)):
            v1 = folio_vocab[folio_list[i]] & a_vocab
            v2 = folio_vocab[folio_list[j]] & a_vocab
            if len(v1 | v2) > 0:
                overlaps.append(len(v1 & v2) / len(v1 | v2))
    return np.mean(overlaps) if overlaps else 0

c3_a_overlap = mean_pairwise_jaccard(c3_folios)
# Sample from others for comparison
np.random.seed(42)
sampled_other = np.random.choice(other_folios, min(20, len(other_folios)), replace=False)
other_a_overlap = mean_pairwise_jaccard(list(sampled_other))
print(f"  A-reference coherence: Cluster 3 = {c3_a_overlap:.3f}, Others (sample) = {other_a_overlap:.3f}")

# ==========================================================================
# PHYSICAL CONTIGUITY CHECK
# ==========================================================================

print("\n" + "=" * 70)
print("PHYSICAL CONTIGUITY CHECK")
print("=" * 70)

for c in sorted(cluster_folios.keys()):
    members = sorted(cluster_folios[c], key=lambda x: folios.index(x))
    positions = [folios.index(f) for f in members]

    # Count gaps
    gaps = []
    for i in range(len(positions) - 1):
        gap = positions[i+1] - positions[i] - 1
        if gap > 0:
            gaps.append(gap)

    contiguous_runs = 1
    for i in range(len(positions) - 1):
        if positions[i+1] != positions[i] + 1:
            contiguous_runs += 1

    print(f"  Cluster {c}: {len(members)} folios in {contiguous_runs} contiguous runs")
    if gaps:
        print(f"    Gaps: {len(gaps)} (mean size {np.mean(gaps):.1f})")

# ==========================================================================
# GRADIENT HYPOTHESIS TEST
# ==========================================================================

print("\n" + "=" * 70)
print("GRADIENT HYPOTHESIS TEST")
print("=" * 70)

# Does folio position predict STATE-C probability?
# If there's a "refinement gradient", later folios might be more STATE-C

positions = list(range(len(folios)))
state_c_binary = [1 if sigs[folios[i]].get('terminal_state') == 'STATE-C' else 0 for i in positions]

rho, p = spearmanr(positions, state_c_binary)
print(f"\nFolio position vs STATE-C (Spearman):")
print(f"  rho = {rho:.4f}, p = {p:.4f}")

# Sliding window STATE-C rate
window_size = 10
window_rates = []
for i in range(len(folios) - window_size + 1):
    window = folios[i:i+window_size]
    rate = sum(1 for f in window if sigs[f].get('terminal_state') == 'STATE-C') / window_size
    window_rates.append(rate)

print(f"\nSliding window STATE-C rate ({window_size}-folio window):")
print(f"  Min: {min(window_rates):.1%} at position {window_rates.index(min(window_rates))}")
print(f"  Max: {max(window_rates):.1%} at position {window_rates.index(max(window_rates))}")

# Where are the high-STATE-C zones?
high_zones = []
for i, rate in enumerate(window_rates):
    if rate >= 0.8:
        high_zones.append((i, i + window_size - 1, rate))

print(f"\nHigh STATE-C zones (>=80%):")
for start, end, rate in high_zones:
    print(f"  Positions {start}-{end}: {rate:.0%}")
    print(f"    Folios: {folios[start]} to {folios[end]}")

# ==========================================================================
# ALTERNATIVE INTERPRETATION
# ==========================================================================

print("\n" + "=" * 70)
print("ALTERNATIVE INTERPRETATION")
print("=" * 70)

print("""
The clustering results suggest:

1. WEAK CLUSTERING (silhouette 0.0179):
   - Folios are NOT sharply separated into distinct material families
   - There's a CONTINUUM with some local coherence

2. CLUSTER 3 ANOMALY:
   - The f75-f84 region is highly coherent
   - 70% STATE-C (vs 52-58% elsewhere)
   - Highest A-reference overlap (0.294)
   - This may represent a "MASTER SECTION" or "REFINED VERSION"

3. A-REFERENCE SHARING (1.31x, p < 0.000001):
   - Real but not dramatic
   - Suggests MATERIAL OVERLAP between adjacent folios
   - NOT sharp family boundaries

4. STATE-C DISTRIBUTION:
   - NOT a cluster boundary marker
   - Clusters geographically contiguous (mostly)
   - May reflect MANUSCRIPT ORGANIZATION, not procedure types

REVISED HYPOTHESIS:
The manuscript may be organized by MATERIAL SOURCE (plant family, preparation type)
rather than PROCEDURE TYPE. Folios in Cluster 3 might represent:
- A refined/final version of procedures
- A specific material class with higher completion requirements
- A "master copy" section copied from earlier drafts
""")

# ==========================================================================
# QUANTITATIVE SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("QUANTITATIVE SUMMARY")
print("=" * 70)

print(f"""
CLUSTERING METRICS:
  Optimal clusters: 4
  Silhouette score: 0.0179 (VERY WEAK)
  Within-cluster Jaccard: 0.130
  Between-cluster Jaccard: 0.092
  Separation ratio: 1.41x

A-REFERENCE ANALYSIS:
  Within-cluster A-overlap: 0.2054
  Between-cluster A-overlap: 0.1571
  Enrichment: 1.31x
  Significance: p < 0.000001 (Mann-Whitney U)

STATE-C DISTRIBUTION:
  Cluster 1: 58.3%
  Cluster 2: 52.2%
  Cluster 3: 70.0% (ELEVATED)
  Cluster 4: 53.6%
  Overall: 57.8%

CLUSTER 3 PROFILE:
  Folios: f75r - f95r1 (20 folios)
  STATE-C rate: 70% (vs 54% others)
  A-reference coherence: 0.294 (highest)
  Vocabulary coherence: 89th percentile

VERDICT:
  TOPICAL CLUSTERING: PARTIAL SUPPORT
  - A-reference sharing IS significant
  - BUT cluster separation is very weak
  - Gradient/continuum model may fit better
  - Cluster 3 is anomalously coherent and complete
""")

print("\n" + "=" * 70)
print("DEEP ANALYSIS COMPLETE")
print("=" * 70)
