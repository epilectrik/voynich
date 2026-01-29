"""
T2: A-AZC Folio Affinity

Question: Do certain A folios preferentially route through certain AZC folios?

Method:
1. Build vocabulary overlap matrix: A folios x AZC folios
2. Compute Jaccard similarity for each A-AZC pair
3. Look for clustering: do groups of A folios share affinity with specific AZC folios?
4. Test: is overlap structured (clusters) or uniform (all A work with all AZC)?

Key question from user: "Do the bulk of compatible A folios work with a few AZC main
folios and then maybe additional currier A records and azc folios are more related?"
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Collect A folio vocabularies (MIDDLEs)
print("Collecting A folio vocabularies...")
a_folio_middles = defaultdict(set)

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if m.middle:
        a_folio_middles[token.folio].add(m.middle)

print(f"Found {len(a_folio_middles)} A folios")

# Collect AZC folio vocabularies (diagram text only, exclude P-placement)
print("Collecting AZC folio vocabularies...")
azc_folio_middles = defaultdict(set)

# Define Zodiac family for labeling
ZODIAC_FOLIOS = {
    'f72v3', 'f72v2', 'f72v1', 'f72r3', 'f72r2', 'f72r1',
    'f71v', 'f71r', 'f70v2', 'f70v1', 'f73v', 'f73r', 'f57v'
}

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    # Skip P-placement (Currier A text)
    placement = getattr(token, 'placement', '')
    if placement.startswith('P'):
        continue

    m = morph.extract(w)
    if m.middle:
        azc_folio_middles[token.folio].add(m.middle)

print(f"Found {len(azc_folio_middles)} AZC folios with diagram text")

# Build overlap matrix
a_folios = sorted(a_folio_middles.keys())
azc_folios = sorted(azc_folio_middles.keys())

print(f"\nBuilding {len(a_folios)} x {len(azc_folios)} overlap matrix...")

overlap_matrix = np.zeros((len(a_folios), len(azc_folios)))
jaccard_matrix = np.zeros((len(a_folios), len(azc_folios)))

for i, a_f in enumerate(a_folios):
    a_vocab = a_folio_middles[a_f]
    for j, azc_f in enumerate(azc_folios):
        azc_vocab = azc_folio_middles[azc_f]

        intersection = len(a_vocab & azc_vocab)
        union = len(a_vocab | azc_vocab)

        overlap_matrix[i, j] = intersection
        jaccard_matrix[i, j] = intersection / union if union > 0 else 0

# Analyze affinity patterns
print("\n" + "="*60)
print("A-AZC AFFINITY ANALYSIS")
print("="*60)

# Per-AZC folio: how many A folios have >0 overlap?
print("\nAZC folio coverage (A folios with >0 MIDDLE overlap):")
azc_coverage = {}
for j, azc_f in enumerate(azc_folios):
    a_count = np.sum(overlap_matrix[:, j] > 0)
    pct = 100.0 * a_count / len(a_folios)
    family = 'Z' if azc_f in ZODIAC_FOLIOS else 'AC'
    azc_coverage[azc_f] = {'a_count': int(a_count), 'pct': pct, 'family': family}
    print(f"  {azc_f:8} ({family:2}): {a_count:3} A folios ({pct:5.1f}%)")

# Per-A folio: how many AZC folios have overlap?
print("\nA folio spread (AZC folios with >0 MIDDLE overlap):")
a_spread = {}
for i, a_f in enumerate(a_folios):
    azc_count = np.sum(overlap_matrix[i, :] > 0)
    pct = 100.0 * azc_count / len(azc_folios)
    a_spread[a_f] = {'azc_count': int(azc_count), 'pct': pct}

# Show distribution
spread_counts = [v['azc_count'] for v in a_spread.values()]
print(f"  Mean AZC overlap per A folio: {np.mean(spread_counts):.1f}")
print(f"  Median: {np.median(spread_counts):.0f}")
print(f"  Range: {min(spread_counts)} - {max(spread_counts)}")

# Top 10 most connected A folios
top_a = sorted(a_spread.items(), key=lambda x: x[1]['azc_count'], reverse=True)[:10]
print("\nTop 10 most AZC-connected A folios:")
for a_f, info in top_a:
    print(f"  {a_f:8}: overlaps with {info['azc_count']} AZC folios ({info['pct']:.1f}%)")

# Test: is there clustering in the A-AZC affinity?
print("\n" + "="*60)
print("CLUSTERING ANALYSIS")
print("="*60)

# Cluster A folios by their AZC affinity profiles
# Use Jaccard profiles as features
print("\nClustering A folios by AZC affinity profile...")

# Need at least 2 samples
if len(a_folios) > 2 and jaccard_matrix.shape[1] > 0:
    # Hierarchical clustering on A folios
    Z = linkage(jaccard_matrix, method='ward')

    # Cut at different heights to see if clusters emerge
    for k in [2, 3, 5]:
        clusters = fcluster(Z, k, criterion='maxclust')
        cluster_sizes = [np.sum(clusters == c) for c in range(1, k+1)]
        print(f"  k={k} clusters: sizes = {sorted(cluster_sizes, reverse=True)}")

    # Test uniformity: if AZC folios are interchangeable, Jaccard variance should be low
    mean_jaccards = np.mean(jaccard_matrix, axis=0)  # Per AZC folio
    jaccard_var = np.var(mean_jaccards)
    print(f"\nAZC folio Jaccard variance: {jaccard_var:.6f}")
    print(f"Mean Jaccard per AZC folio: {np.mean(mean_jaccards):.4f} (std={np.std(mean_jaccards):.4f})")

# Compare Zodiac vs A/C family affinity
print("\n" + "="*60)
print("ZODIAC vs A/C FAMILY AFFINITY")
print("="*60)

zodiac_idx = [j for j, f in enumerate(azc_folios) if f in ZODIAC_FOLIOS]
ac_idx = [j for j, f in enumerate(azc_folios) if f not in ZODIAC_FOLIOS]

zodiac_jaccards = jaccard_matrix[:, zodiac_idx].flatten()
ac_jaccards = jaccard_matrix[:, ac_idx].flatten()

print(f"Zodiac family mean Jaccard with A: {np.mean(zodiac_jaccards):.4f} (std={np.std(zodiac_jaccards):.4f})")
print(f"A/C family mean Jaccard with A:    {np.mean(ac_jaccards):.4f} (std={np.std(ac_jaccards):.4f})")

# Statistical test
t_stat, t_p = stats.ttest_ind(zodiac_jaccards, ac_jaccards)
print(f"t-test: t={t_stat:.3f}, p={t_p:.4f}")

# Test user hypothesis: do a few AZC folios serve most A folios?
print("\n" + "="*60)
print("HUB AZC FOLIO ANALYSIS")
print("="*60)

# Sort AZC folios by A coverage
sorted_azc = sorted(azc_coverage.items(), key=lambda x: x[1]['a_count'], reverse=True)

print("\nCumulative A coverage by AZC folios (in order of coverage):")
covered_a = set()
for i, (azc_f, info) in enumerate(sorted_azc):
    # Find which A folios this AZC covers
    j = azc_folios.index(azc_f)
    newly_covered = {a_folios[k] for k in range(len(a_folios)) if overlap_matrix[k, j] > 0}
    covered_a.update(newly_covered)
    cum_pct = 100.0 * len(covered_a) / len(a_folios)

    if i < 10 or i == len(sorted_azc) - 1:
        family = 'Z' if azc_f in ZODIAC_FOLIOS else 'AC'
        print(f"  +{azc_f:8} ({family:2}): cumulative {len(covered_a)} A folios ({cum_pct:.1f}%)")

# Save results
results = {
    'a_folio_count': len(a_folios),
    'azc_folio_count': len(azc_folios),
    'azc_coverage': azc_coverage,
    'a_spread_summary': {
        'mean': float(np.mean(spread_counts)),
        'median': float(np.median(spread_counts)),
        'min': int(min(spread_counts)),
        'max': int(max(spread_counts)),
    },
    'zodiac_mean_jaccard': float(np.mean(zodiac_jaccards)),
    'ac_mean_jaccard': float(np.mean(ac_jaccards)),
    'family_ttest_p': float(t_p),
    'jaccard_variance': float(jaccard_var) if 'jaccard_var' in dir() else None,
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if t_p < 0.01:
    verdict = "FAMILY_DIFFERENTIATED"
    print(f"Zodiac and A/C families have DIFFERENT A-affinity profiles (p={t_p:.4f})")
elif jaccard_var and jaccard_var < 0.001:
    verdict = "UNIFORMLY_DISTRIBUTED"
    print("AZC folios are nearly interchangeable in A-affinity")
else:
    verdict = "WEAKLY_DIFFERENTIATED"
    print(f"Weak differentiation detected (p={t_p:.4f})")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't2_a_azc_affinity.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")
