"""
FOLIO UNIQUE VOCABULARY

Does each B folio contribute unique MIDDLEs that appear nowhere else?
If so, that would explain why 83 folios are needed.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("FOLIO UNIQUE VOCABULARY ANALYSIS")
print("Does each folio contribute unique content?")
print("=" * 70)

# Build per-folio MIDDLE sets
folio_middles = defaultdict(set)
folio_tokens = defaultdict(set)
all_middles = Counter()

for token in tx.currier_b():
    folio = token.folio
    word = token.word
    if word:
        m = morph.extract(word)
        folio_tokens[folio].add(word)
        if m.middle:
            folio_middles[folio].add(m.middle)
            all_middles[m.middle] += 1

folio_order = list(folio_middles.keys())
print(f"B folios: {len(folio_order)}")
print(f"Total unique MIDDLEs: {len(all_middles)}")

# For each folio, compute:
# 1. How many MIDDLEs are UNIQUE to this folio (appear in no other folio)?
# 2. How many MIDDLEs are RARE (appear in <=3 folios)?
# 3. What fraction of its vocabulary is shared with all other folios?

print("\n" + "=" * 70)
print("UNIQUE MIDDLEs PER FOLIO")
print("=" * 70)

# Count which folios each MIDDLE appears in
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

# Classify MIDDLEs
unique_middles = set(m for m, count in middle_folio_count.items() if count == 1)
rare_middles = set(m for m, count in middle_folio_count.items() if count <= 3)
common_middles = set(m for m, count in middle_folio_count.items() if count >= 70)

print(f"\nMIDDLE distribution:")
print(f"  Unique to 1 folio: {len(unique_middles)} ({100*len(unique_middles)/len(all_middles):.1f}%)")
print(f"  Rare (<=3 folios): {len(rare_middles)} ({100*len(rare_middles)/len(all_middles):.1f}%)")
print(f"  Common (>=70 folios): {len(common_middles)} ({100*len(common_middles)/len(all_middles):.1f}%)")

# Per-folio unique counts
folio_unique_counts = []
folio_rare_counts = []
for folio in folio_order:
    middles = folio_middles[folio]
    n_unique = len(middles & unique_middles)
    n_rare = len(middles & rare_middles)
    folio_unique_counts.append(n_unique)
    folio_rare_counts.append(n_rare)

print(f"\nFolios with unique MIDDLEs:")
print(f"  Mean unique per folio: {np.mean(folio_unique_counts):.1f}")
print(f"  Folios with 0 unique: {sum(1 for c in folio_unique_counts if c == 0)}")
print(f"  Folios with 5+ unique: {sum(1 for c in folio_unique_counts if c >= 5)}")

# Which folios have the most unique MIDDLEs?
print("\nTop 10 folios by unique MIDDLE count:")
for folio, n_unique in sorted(zip(folio_order, folio_unique_counts), key=lambda x: -x[1])[:10]:
    n_total = len(folio_middles[folio])
    print(f"  {folio}: {n_unique} unique / {n_total} total MIDDLEs ({100*n_unique/n_total:.1f}%)")

# ANALYSIS: Do unique MIDDLEs carry significant token volume?
print("\n" + "=" * 70)
print("UNIQUE MIDDLE TOKEN VOLUME")
print("=" * 70)

# For each folio, what fraction of its tokens use unique MIDDLEs?
folio_unique_token_frac = []
for folio in folio_order:
    tokens = folio_tokens[folio]
    unique_token_count = 0
    for word in tokens:
        m = morph.extract(word)
        if m.middle in unique_middles:
            unique_token_count += 1
    frac = unique_token_count / len(tokens) if tokens else 0
    folio_unique_token_frac.append(frac)

print(f"\nFraction of tokens using unique MIDDLEs:")
print(f"  Mean: {100*np.mean(folio_unique_token_frac):.2f}%")
print(f"  Max: {100*np.max(folio_unique_token_frac):.2f}%")

# ANALYSIS: Vocabulary OVERLAP between folios
print("\n" + "=" * 70)
print("VOCABULARY OVERLAP STRUCTURE")
print("=" * 70)

# How much overlap is there between folios?
# Compute pairwise Jaccard
jaccard_matrix = []
for i, f1 in enumerate(folio_order):
    row = []
    for j, f2 in enumerate(folio_order):
        if i == j:
            row.append(1.0)
        else:
            m1, m2 = folio_middles[f1], folio_middles[f2]
            inter = len(m1 & m2)
            union = len(m1 | m2)
            row.append(inter / union if union > 0 else 0)
    jaccard_matrix.append(row)

jaccard_matrix = np.array(jaccard_matrix)
mean_jaccard = np.mean(jaccard_matrix[np.triu_indices(len(folio_order), k=1)])
print(f"\nMean pairwise Jaccard similarity: {mean_jaccard:.3f}")

# What fraction of each folio's vocabulary is SHARED with at least one other folio?
shared_fracs = []
for folio in folio_order:
    middles = folio_middles[folio]
    shared = len([m for m in middles if middle_folio_count[m] > 1])
    shared_fracs.append(shared / len(middles) if middles else 0)

print(f"Fraction of vocabulary shared with at least one other folio:")
print(f"  Mean: {100*np.mean(shared_fracs):.1f}%")
print(f"  Min: {100*np.min(shared_fracs):.1f}%")

# ANALYSIS: CORE vs PERIPHERAL vocabulary
print("\n" + "=" * 70)
print("CORE vs PERIPHERAL VOCABULARY")
print("=" * 70)

# Core = MIDDLEs that appear in majority of folios
core_threshold = len(folio_order) // 2  # 41 folios
core_middles = set(m for m, count in middle_folio_count.items() if count >= core_threshold)
peripheral_middles = set(m for m, count in middle_folio_count.items() if count < core_threshold)

print(f"\nCore MIDDLEs (in >={core_threshold} folios): {len(core_middles)}")
print(f"Peripheral MIDDLEs (in <{core_threshold} folios): {len(peripheral_middles)}")

# What fraction of each folio uses core vocabulary?
folio_core_frac = []
for folio in folio_order:
    middles = folio_middles[folio]
    core_count = len(middles & core_middles)
    folio_core_frac.append(core_count / len(middles) if middles else 0)

print(f"\nCore vocabulary fraction per folio:")
print(f"  Mean: {100*np.mean(folio_core_frac):.1f}%")
print(f"  Range: {100*np.min(folio_core_frac):.1f}% - {100*np.max(folio_core_frac):.1f}%")

# HYPOTHESIS: Each folio = core + unique combination
print("\n" + "=" * 70)
print("HYPOTHESIS: FOLIO = CORE + UNIQUE PERIPHERY")
print("=" * 70)

print("""
If each B folio is:
  [SHARED CORE] + [UNIQUE PERIPHERAL MIDDLEs]

Then the 83 folios exist because each represents a unique COMBINATION
of the core operations with folio-specific details.

This is consistent with:
- 83 distinct "recipes" or "procedures"
- Each sharing common control operations (core)
- Each with specific materials/parameters (peripheral)
""")

# Test: Is peripheral vocabulary what differentiates folios?
peripheral_per_folio = []
for folio in folio_order:
    middles = folio_middles[folio]
    periph_count = len(middles & peripheral_middles)
    peripheral_per_folio.append(periph_count)

print(f"\nPeripheral MIDDLEs per folio:")
print(f"  Mean: {np.mean(peripheral_per_folio):.1f}")
print(f"  Std: {np.std(peripheral_per_folio):.1f}")
print(f"  Range: {np.min(peripheral_per_folio)} - {np.max(peripheral_per_folio)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
1. UNIQUE MIDDLEs: {len(unique_middles)} MIDDLEs appear in only 1 folio ({100*len(unique_middles)/len(all_middles):.1f}%)

2. CORE MIDDLEs: {len(core_middles)} MIDDLEs appear in >50% of folios
   - These carry the shared grammar/operations

3. PERIPHERAL MIDDLEs: {len(peripheral_middles)} MIDDLEs appear in <50% of folios
   - These differentiate folios

4. OVERLAP STRUCTURE:
   - Mean Jaccard: {mean_jaccard:.3f}
   - Mean shared vocabulary: {100*np.mean(shared_fracs):.1f}%
   - Mean core fraction: {100*np.mean(folio_core_frac):.1f}%

INTERPRETATION:
Each folio shares ~{100*np.mean(folio_core_frac):.0f}% core vocabulary with others,
but has ~{np.mean(peripheral_per_folio):.0f} peripheral MIDDLEs that localize it.

83 folios may represent 83 distinct "parameter sets" over a shared control grammar.
""")
