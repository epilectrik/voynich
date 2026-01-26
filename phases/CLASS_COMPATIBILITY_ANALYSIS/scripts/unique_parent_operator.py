"""
UNIQUE MIDDLE PARENT OPERATOR ANALYSIS

Hypothesis: Unique MIDDLEs are PARAMETRIC INSTANCES of core MIDDLEs.
- Core MIDDLEs = abstract operators (generic "filter", "heat")
- Unique MIDDLEs = specific instances ("filter-through-silk")

Test: Do unique MIDDLEs cluster around their "parent" core MIDDLEs?
If yes: Unique vocabulary is INSTANTIATION of abstract operators
If no: Unique vocabulary is independent content
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("UNIQUE MIDDLE PARENT OPERATOR ANALYSIS")
print("=" * 70)

# Build B folio MIDDLEs
b_folio_middles = defaultdict(set)
b_middle_counts = Counter()

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
            b_middle_counts[m.middle] += 1

# Identify core MIDDLEs (appear in >50% of folios)
middle_folio_count = defaultdict(int)
for folio, middles in b_folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

total_folios = len(b_folio_middles)
core_threshold = total_folios * 0.5
core_middles = {m for m, count in middle_folio_count.items() if count >= core_threshold}
unique_middles = {m for m, count in middle_folio_count.items() if count == 1}

print(f"\nCore MIDDLEs (>50% folios): {len(core_middles)}")
print(f"Unique MIDDLEs (1 folio): {len(unique_middles)}")

# For each unique MIDDLE, find which core MIDDLEs it contains
def find_parent_cores(unique_middle, cores):
    """Find all core MIDDLEs that are substrings of this unique MIDDLE."""
    parents = []
    for core in cores:
        if core in unique_middle and core != unique_middle:
            parents.append(core)
    return parents

unique_parents = {}
for um in unique_middles:
    parents = find_parent_cores(um, core_middles)
    if parents:
        # Keep the longest parent (most specific)
        longest = max(parents, key=len)
        unique_parents[um] = longest

print(f"\nUnique MIDDLEs with core parent: {len(unique_parents)} ({100*len(unique_parents)/len(unique_middles):.1f}%)")

# Parent distribution
parent_counts = Counter(unique_parents.values())
print(f"\nCore MIDDLEs serving as parents: {len(parent_counts)}")

print(f"\nTop 15 parent cores (by # of unique children):")
for core, count in parent_counts.most_common(15):
    print(f"  '{core}' (len={len(core)}): {count} unique children")

# Now the key test: Do folios cluster by parent operator?
# If unique MIDDLEs are instantiations, a folio should have many
# unique MIDDLEs sharing the SAME parent (using same abstract operator)

print("\n" + "=" * 70)
print("FOLIO PARENT CLUSTERING")
print("=" * 70)

folio_parent_profiles = {}
for folio, middles in b_folio_middles.items():
    # Get unique MIDDLEs in this folio
    folio_unique = [m for m in middles if m in unique_middles]
    # Get their parents
    parents = [unique_parents.get(m) for m in folio_unique if m in unique_parents]
    folio_parent_profiles[folio] = Counter(parents)

# Measure parent concentration per folio
# If instantiation hypothesis is true: few parents, many children each
# If independent content: many parents, few children each

concentration_scores = []
for folio, parent_counts in folio_parent_profiles.items():
    if parent_counts:
        total = sum(parent_counts.values())
        unique_parents_count = len(parent_counts)
        # Concentration = 1 - (diversity / max_diversity)
        # High concentration = few parents with many children
        concentration = 1 - (unique_parents_count / total) if total > 1 else 0
        concentration_scores.append((folio, concentration, total, unique_parents_count))

concentration_scores.sort(key=lambda x: -x[1])

print(f"\nFolio parent concentration (top 10):")
print(f"{'Folio':<10} {'Conc':<8} {'#Unique':<10} {'#Parents':<10}")
print("-" * 40)
for folio, conc, total, n_parents in concentration_scores[:10]:
    print(f"{folio:<10} {conc:.3f}    {total:<10} {n_parents:<10}")

mean_conc = np.mean([c[1] for c in concentration_scores])
print(f"\nMean concentration: {mean_conc:.3f}")

# Compare to random baseline
# If unique MIDDLEs were randomly assigned to parents, what would concentration be?
import random
random.seed(42)

# Shuffle parent assignments
all_unique_with_parents = list(unique_parents.keys())
random_concentration = []
for _ in range(100):
    random.shuffle(all_unique_with_parents)
    idx = 0
    for folio, middles in b_folio_middles.items():
        folio_unique = [m for m in middles if m in unique_middles]
        n = len([m for m in folio_unique if m in unique_parents])
        if n > 0:
            fake_parents = [unique_parents[all_unique_with_parents[i % len(all_unique_with_parents)]]
                          for i in range(idx, idx + n)]
            idx += n
            parent_dist = Counter(fake_parents)
            total = sum(parent_dist.values())
            unique_p = len(parent_dist)
            conc = 1 - (unique_p / total) if total > 1 else 0
            random_concentration.append(conc)

random_mean = np.mean(random_concentration)
print(f"Random baseline concentration: {random_mean:.3f}")
print(f"Ratio (actual/random): {mean_conc/random_mean:.2f}x")

# Now check: do adjacent folios use similar parent operators?
print("\n" + "=" * 70)
print("ADJACENT FOLIO PARENT SIMILARITY")
print("=" * 70)

folio_order = list(b_folio_middles.keys())

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

adjacent_similarity = []
for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    parents1 = set(folio_parent_profiles[f1].keys()) - {None}
    parents2 = set(folio_parent_profiles[f2].keys()) - {None}
    if parents1 and parents2:
        sim = jaccard(parents1, parents2)
        adjacent_similarity.append((f1, f2, sim))

# Non-adjacent comparison
nonadj_similarity = []
for _ in range(len(adjacent_similarity)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        parents1 = set(folio_parent_profiles[f1].keys()) - {None}
        parents2 = set(folio_parent_profiles[f2].keys()) - {None}
        if parents1 and parents2:
            nonadj_similarity.append(jaccard(parents1, parents2))

adj_mean = np.mean([s[2] for s in adjacent_similarity])
nonadj_mean = np.mean(nonadj_similarity) if nonadj_similarity else 0

print(f"\nParent operator overlap (Jaccard):")
print(f"  Adjacent folios: {adj_mean:.3f}")
print(f"  Non-adjacent: {nonadj_mean:.3f}")
if nonadj_mean > 0:
    print(f"  Ratio: {adj_mean/nonadj_mean:.2f}x")

# Sample adjacent pairs
print(f"\nSample adjacent pairs:")
for f1, f2, sim in adjacent_similarity[:5]:
    p1 = set(folio_parent_profiles[f1].keys()) - {None}
    p2 = set(folio_parent_profiles[f2].keys()) - {None}
    shared = p1 & p2
    print(f"  {f1} - {f2}: sim={sim:.2f}")
    print(f"    Shared parents: {sorted(shared)[:5]}...")

# Summary
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if mean_conc > random_mean * 1.1:
    print(f"""
PARENT CLUSTERING DETECTED:

Unique MIDDLEs within a folio cluster around specific parent operators
more than expected by chance ({mean_conc:.3f} vs {random_mean:.3f} random).

This supports the INSTANTIATION hypothesis:
- Each folio uses a FEW abstract operators (core MIDDLEs)
- But instantiates them in MANY specific ways (unique MIDDLEs)

The unique vocabulary is NOT random content - it's parametric
elaboration of the shared control vocabulary.
""")
else:
    print(f"""
NO PARENT CLUSTERING:

Unique MIDDLEs are distributed across parents roughly randomly.
The containment relationship may be coincidental string overlap,
not semantic instantiation.
""")

if adj_mean > nonadj_mean * 1.1:
    print(f"""
ADJACENT FOLIOS USE SIMILAR PARENT OPERATORS:

Adjacent folios share parent operators at {adj_mean/nonadj_mean:.2f}x the rate
of non-adjacent folios.

This means adjacent folios are VARIATIONS:
- Same abstract operations (parent cores)
- Different specific instantiations (unique children)

Like two recipes for similar dishes - same cooking verbs,
different specific ingredients.
""")
else:
    print(f"""
NO PREFERENTIAL PARENT SHARING between adjacent folios.
""")

# Final architectural interpretation
print("\n" + "=" * 70)
print("ARCHITECTURAL SPECULATION")
print("=" * 70)

print(f"""
TWO-LAYER MODEL:

1. CONTROL LAYER (AZC-filtered):
   - Core MIDDLEs = abstract operators
   - AZC determines: "Is FILTER legal here? Is HEAT legal here?"
   - These are the control primitives, ~79% of tokens

2. PROCEDURE LAYER (B-exclusive):
   - Unique MIDDLEs = parametric instantiations
   - "If FILTER is legal, WHICH filtration method?"
   - Each folio's unique vocabulary defines its specific procedure
   - These are always available (no AZC filtering needed)

WHY AZC MATTERS EVEN THOUGH FOLIOS ARE UNIQUE:

AZC doesn't decide WHICH folio/procedure runs.
AZC decides WHICH OPERATIONS ARE LEGAL within any procedure.

The same folio could execute differently depending on AZC state:
- High escape: more operations available, aggressive intervention
- Constrained: fewer operations available, conservative approach

Each folio is a unique procedure, but it's a CONDITIONAL procedure -
its execution path depends on what the AZC makes legal.
""")
