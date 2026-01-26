"""
FOLIO NECESSITY ANALYSIS

Question: Are all 83 folios necessary, or could some be merged?
What makes a folio "necessary"?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("FOLIO NECESSITY ANALYSIS")
print("=" * 70)

# Build folio MIDDLE sets
folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            folio_middles[token.folio].add(m.middle)

folios = sorted(folio_middles.keys())
n_folios = len(folios)

# For each folio, compute: could its content be covered by other folios?
print(f"\nFOLIO REDUNDANCY ANALYSIS:")
print(f"Question: What % of each folio's MIDDLEs appear in other folios?")

folio_coverage = {}
for folio in folios:
    my_middles = folio_middles[folio]
    others_middles = set()
    for other in folios:
        if other != folio:
            others_middles.update(folio_middles[other])

    covered = my_middles & others_middles
    unique = my_middles - others_middles
    coverage = len(covered) / len(my_middles) if my_middles else 0
    folio_coverage[folio] = {
        'total': len(my_middles),
        'covered': len(covered),
        'unique': len(unique),
        'coverage': coverage
    }

# Distribution of coverage
coverage_vals = [v['coverage'] for v in folio_coverage.values()]
unique_counts = [v['unique'] for v in folio_coverage.values()]

print(f"\nCoverage by other folios:")
print(f"  Mean: {np.mean(coverage_vals)*100:.1f}%")
print(f"  Min: {np.min(coverage_vals)*100:.1f}%")
print(f"  Max: {np.max(coverage_vals)*100:.1f}%")

print(f"\nUnique MIDDLEs per folio:")
print(f"  Mean: {np.mean(unique_counts):.1f}")
print(f"  Min: {np.min(unique_counts)}")
print(f"  Max: {np.max(unique_counts)}")

# How many folios have 0 unique MIDDLEs?
zero_unique = sum(1 for v in folio_coverage.values() if v['unique'] == 0)
print(f"\nFolios with 0 unique MIDDLEs: {zero_unique}")

# If we removed each folio, how much vocabulary would be lost?
print("\n" + "=" * 70)
print("FOLIO ESSENTIALITY (what would be lost if removed)")
print("=" * 70)

folio_essential = {}
for folio in folios:
    lost = folio_coverage[folio]['unique']
    total_b_middles = len(set.union(*folio_middles.values()))
    essentiality = lost / total_b_middles if total_b_middles > 0 else 0
    folio_essential[folio] = {
        'lost_middles': lost,
        'essentiality': essentiality
    }

# Top 10 most essential folios
print(f"\nTop 10 most essential folios (most unique vocabulary):")
sorted_essential = sorted(folio_essential.items(), key=lambda x: -x[1]['lost_middles'])
for folio, data in sorted_essential[:10]:
    print(f"  {folio}: {data['lost_middles']} unique MIDDLEs")

# Bottom 10 (most redundant)
print(f"\nTop 10 most redundant folios (least unique vocabulary):")
for folio, data in sorted_essential[-10:]:
    print(f"  {folio}: {data['lost_middles']} unique MIDDLEs")

# Could any folios be merged without losing vocabulary?
print("\n" + "=" * 70)
print("PAIRWISE REDUNDANCY")
print("=" * 70)

# For each pair of folios, compute overlap
high_overlap_pairs = []
for i, f1 in enumerate(folios):
    for f2 in folios[i+1:]:
        m1, m2 = folio_middles[f1], folio_middles[f2]
        if m1 and m2:
            jaccard = len(m1 & m2) / len(m1 | m2)
            if jaccard > 0.5:
                high_overlap_pairs.append((f1, f2, jaccard, len(m1 & m2)))

print(f"\nFolio pairs with >50% Jaccard overlap: {len(high_overlap_pairs)}")
if high_overlap_pairs:
    high_overlap_pairs.sort(key=lambda x: -x[2])
    print("Top overlapping pairs:")
    for f1, f2, jac, shared in high_overlap_pairs[:10]:
        print(f"  {f1} - {f2}: {jac:.2f} Jaccard, {shared} shared MIDDLEs")

# The critical question: how many folios are truly necessary?
print("\n" + "=" * 70)
print("MINIMUM FOLIO SET")
print("=" * 70)

# Greedy set cover: minimum folios to cover all unique MIDDLEs
all_middles = set.union(*folio_middles.values())
remaining = all_middles.copy()
selected = []
available = {f: folio_middles[f].copy() for f in folios}

while remaining:
    # Find folio that covers most remaining MIDDLEs
    best_folio = max(available.keys(), key=lambda f: len(available[f] & remaining))
    best_coverage = available[best_folio] & remaining

    if not best_coverage:
        break

    selected.append((best_folio, len(best_coverage)))
    remaining -= best_coverage
    del available[best_folio]

print(f"\nGreedy set cover result:")
print(f"  Total MIDDLEs: {len(all_middles)}")
print(f"  Minimum folios needed: {len(selected)}")
print(f"  Actual folios: {n_folios}")
print(f"  Redundancy ratio: {n_folios / len(selected):.2f}x")

print(f"\nTop 15 folios by greedy coverage:")
for folio, coverage in selected[:15]:
    print(f"  {folio}: covers {coverage} MIDDLEs")

# Summary
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

print(f"""
KEY FINDINGS:

1. REDUNDANCY:
   - Mean coverage by other folios: {np.mean(coverage_vals)*100:.1f}%
   - Only {zero_unique} folios have ZERO unique MIDDLEs
   - Most folios contribute something unique

2. MINIMUM SET:
   - Greedy set cover needs {len(selected)} folios to cover all {len(all_middles)} MIDDLEs
   - Actual count is {n_folios} folios
   - Redundancy ratio: {n_folios / len(selected):.2f}x

3. WHY THE REDUNDANCY?
   - If {len(selected)} folios could cover vocabulary, why have {n_folios}?
   - Possible answers:
     a) Vocabulary coverage ≠ procedural coverage (different procedures share vocabulary)
     b) Each folio is a distinct PROCEDURE even if vocabulary overlaps
     c) The 19:1 A:B ratio requires this many procedures for material coverage
     d) REGIMEs require multiple procedures at each completeness tier

4. THE 83 NUMBER:
   - NOT determined by vocabulary coverage (only {len(selected)} needed)
   - LIKELY determined by procedural distinctiveness
   - Each folio is a unique recipe, even if some ingredients are shared
""")
