"""
ADJACENT PERIPHERAL SHARING

Do adjacent folios share more PERIPHERAL vocabulary than non-adjacent?
If so, that would suggest adjacent folios are "related recipes"
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import random

tx = Transcript()
morph = Morphology()

# Build per-folio MIDDLE sets
folio_middles = defaultdict(set)

for token in tx.currier_b():
    folio = token.folio
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            folio_middles[folio].add(m.middle)

folio_order = list(folio_middles.keys())
n_folios = len(folio_order)

# Count folio appearances
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

# Define core vs peripheral
core_threshold = n_folios // 2
core_set = set(m for m, count in middle_folio_count.items() if count >= core_threshold)
peripheral_set = set(m for m, count in middle_folio_count.items() if count < core_threshold)

print(f"Core MIDDLEs: {len(core_set)}")
print(f"Peripheral MIDDLEs: {len(peripheral_set)}")

def jaccard(set1, set2):
    if not set1 and not set2:
        return 1.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0

# Compute adjacent vs non-adjacent Jaccard for PERIPHERAL ONLY
print(f"\n{'='*70}")
print("PERIPHERAL VOCABULARY SHARING")
print(f"{'='*70}")

adjacent_peripheral_jaccard = []
nonadjacent_peripheral_jaccard = []

for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    p1 = folio_middles[f1] & peripheral_set
    p2 = folio_middles[f2] & peripheral_set
    adjacent_peripheral_jaccard.append(jaccard(p1, p2))

# Sample non-adjacent
random.seed(42)
for _ in range(len(adjacent_peripheral_jaccard)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        p1 = folio_middles[f1] & peripheral_set
        p2 = folio_middles[f2] & peripheral_set
        nonadjacent_peripheral_jaccard.append(jaccard(p1, p2))

print(f"\nPeripheral MIDDLE Jaccard:")
print(f"  Adjacent: {np.mean(adjacent_peripheral_jaccard):.3f} +/- {np.std(adjacent_peripheral_jaccard):.3f}")
print(f"  Non-adjacent: {np.mean(nonadjacent_peripheral_jaccard):.3f} +/- {np.std(nonadjacent_peripheral_jaccard):.3f}")
print(f"  Ratio: {np.mean(adjacent_peripheral_jaccard)/np.mean(nonadjacent_peripheral_jaccard):.2f}x")

# Compare to CORE
adjacent_core_jaccard = []
nonadjacent_core_jaccard = []

for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    c1 = folio_middles[f1] & core_set
    c2 = folio_middles[f2] & core_set
    adjacent_core_jaccard.append(jaccard(c1, c2))

random.seed(42)
for _ in range(len(adjacent_core_jaccard)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        c1 = folio_middles[f1] & core_set
        c2 = folio_middles[f2] & core_set
        nonadjacent_core_jaccard.append(jaccard(c1, c2))

print(f"\nCore MIDDLE Jaccard:")
print(f"  Adjacent: {np.mean(adjacent_core_jaccard):.3f}")
print(f"  Non-adjacent: {np.mean(nonadjacent_core_jaccard):.3f}")
print(f"  Ratio: {np.mean(adjacent_core_jaccard)/np.mean(nonadjacent_core_jaccard):.2f}x")

# Rare MIDDLEs (<=3 folios) - the most differentiating
rare_set = set(m for m, count in middle_folio_count.items() if count <= 3)

adjacent_rare_jaccard = []
nonadjacent_rare_jaccard = []

for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    r1 = folio_middles[f1] & rare_set
    r2 = folio_middles[f2] & rare_set
    adjacent_rare_jaccard.append(jaccard(r1, r2))

random.seed(42)
for _ in range(len(adjacent_rare_jaccard)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        r1 = folio_middles[f1] & rare_set
        r2 = folio_middles[f2] & rare_set
        nonadjacent_rare_jaccard.append(jaccard(r1, r2))

print(f"\nRare MIDDLE (<=3 folios) Jaccard:")
print(f"  Adjacent: {np.mean(adjacent_rare_jaccard):.3f}")
print(f"  Non-adjacent: {np.mean(nonadjacent_rare_jaccard):.3f}")
if np.mean(nonadjacent_rare_jaccard) > 0:
    print(f"  Ratio: {np.mean(adjacent_rare_jaccard)/np.mean(nonadjacent_rare_jaccard):.2f}x")

# Check if adjacent folios share UNIQUE MIDDLEs
unique_set = set(m for m, count in middle_folio_count.items() if count == 1)

print(f"\n{'='*70}")
print("UNIQUE MIDDLE SHARING (folios that share otherwise-unique MIDDLEs)")
print(f"{'='*70}")

# For MIDDLEs appearing in 2-3 folios, are those folios adjacent?
shared_rare = [m for m, count in middle_folio_count.items() if 2 <= count <= 3]
print(f"\nMIDDLEs appearing in exactly 2-3 folios: {len(shared_rare)}")

adjacent_sharing = 0
nonadjacent_sharing = 0

for m in shared_rare:
    folios_with_m = [f for f in folio_order if m in folio_middles[f]]
    # Check if any pair is adjacent
    positions = [folio_order.index(f) for f in folios_with_m]
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            if abs(positions[i] - positions[j]) == 1:
                adjacent_sharing += 1
            else:
                nonadjacent_sharing += 1

total_pairs = adjacent_sharing + nonadjacent_sharing
print(f"\nRare MIDDLE sharing pairs:")
print(f"  Adjacent pairs: {adjacent_sharing} ({100*adjacent_sharing/total_pairs:.1f}%)")
print(f"  Non-adjacent pairs: {nonadjacent_sharing} ({100*nonadjacent_sharing/total_pairs:.1f}%)")

# Expected by chance
n_adjacent_pairs = n_folios - 1
n_nonadjacent_pairs = n_folios * (n_folios - 1) // 2 - n_adjacent_pairs
expected_adjacent = 100 * n_adjacent_pairs / (n_adjacent_pairs + n_nonadjacent_pairs)
print(f"  Expected if random: {expected_adjacent:.1f}% adjacent")

if adjacent_sharing / total_pairs > expected_adjacent / 100:
    print(f"\n  => Adjacent folios share rare MIDDLEs MORE than expected!")
    print(f"     Enrichment: {(adjacent_sharing/total_pairs) / (expected_adjacent/100):.2f}x")
else:
    print(f"\n  => No special adjacent sharing of rare MIDDLEs")

print(f"\n{'='*70}")
print("INTERPRETATION")
print(f"{'='*70}")

print(f"""
Adjacent folio sharing ratios:
  Core vocabulary: {np.mean(adjacent_core_jaccard)/np.mean(nonadjacent_core_jaccard):.2f}x (expected: ~1.0x)
  Peripheral vocabulary: {np.mean(adjacent_peripheral_jaccard)/np.mean(nonadjacent_peripheral_jaccard):.2f}x
  Rare vocabulary: {np.mean(adjacent_rare_jaccard)/np.mean(nonadjacent_rare_jaccard):.2f}x (if any)

If adjacent folios share MORE peripheral/rare vocabulary:
=> Adjacent folios represent RELATED procedures (similar materials)
=> The manuscript has a thematic organization

If adjacent folios share only core vocabulary:
=> Adjacency is about control flow, not content
=> Folio order is curriculum-based, not thematic
""")
