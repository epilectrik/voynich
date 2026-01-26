"""
SIMPLE CHECK: Does every B folio have unique vocabulary?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict

tx = Transcript()
morph = Morphology()

# Build per-folio MIDDLE sets
folio_middles = defaultdict(set)

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            folio_middles[token.folio].add(m.middle)

folio_order = list(folio_middles.keys())

# Count how many folios each MIDDLE appears in
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

# For each folio, count MIDDLEs unique to that folio
print("=" * 70)
print("UNIQUE VOCABULARY PER FOLIO")
print("=" * 70)

folios_with_unique = 0
folios_without_unique = []

print(f"\n{'Folio':<10} {'Total MIDDLEs':<15} {'Unique MIDDLEs':<15} {'% Unique':<10}")
print("-" * 50)

for folio in folio_order:
    middles = folio_middles[folio]
    unique = [m for m in middles if middle_folio_count[m] == 1]

    pct = 100 * len(unique) / len(middles) if middles else 0

    if len(unique) > 0:
        folios_with_unique += 1
    else:
        folios_without_unique.append(folio)

    print(f"{folio:<10} {len(middles):<15} {len(unique):<15} {pct:.1f}%")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

print(f"\nFolios with at least 1 unique MIDDLE: {folios_with_unique}/{len(folio_order)} ({100*folios_with_unique/len(folio_order):.1f}%)")
print(f"Folios with NO unique MIDDLEs: {len(folios_without_unique)}")

if folios_without_unique:
    print(f"\nFolios without unique vocabulary:")
    for f in folios_without_unique:
        print(f"  {f}: {len(folio_middles[f])} total MIDDLEs (all shared with other folios)")
