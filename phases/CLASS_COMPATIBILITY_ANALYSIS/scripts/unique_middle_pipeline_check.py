"""
UNIQUE MIDDLE PIPELINE CHECK

Are unique B MIDDLEs:
1. In the A→B pipeline (PP MIDDLEs) - can be activated by A records
2. B-exclusive - exist only in B, never in A

If B-exclusive, they're always "active" (no AZC filtering)
If PP, they require A record activation
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("UNIQUE MIDDLE PIPELINE CHECK")
print("Are unique B MIDDLEs in the A->B pipeline?")
print("=" * 70)

# Build B folio MIDDLEs
b_folio_middles = defaultdict(set)
b_all_middles = set()

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
            b_all_middles.add(m.middle)

# Build A MIDDLEs (PP vocabulary)
a_middles = set()
for token in tx.currier_a():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            a_middles.add(m.middle)

print(f"\nB unique MIDDLEs: {len(b_all_middles)}")
print(f"A MIDDLEs: {len(a_middles)}")

# PP MIDDLEs = intersection (in both A and B)
pp_middles = a_middles & b_all_middles
b_exclusive = b_all_middles - a_middles

print(f"\nPP MIDDLEs (in both A and B): {len(pp_middles)}")
print(f"B-exclusive MIDDLEs (only in B): {len(b_exclusive)}")

# Identify unique B MIDDLEs (appear in only 1 B folio)
middle_folio_count = defaultdict(int)
for folio, middles in b_folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

unique_b_middles = {m for m, count in middle_folio_count.items() if count == 1}
print(f"\nUnique B MIDDLEs (in only 1 folio): {len(unique_b_middles)}")

# Of unique B MIDDLEs, how many are PP vs B-exclusive?
unique_pp = unique_b_middles & pp_middles
unique_b_exclusive = unique_b_middles & b_exclusive

print(f"\n--- UNIQUE B MIDDLE CLASSIFICATION ---")
print(f"  PP (in A, can be AZC-filtered): {len(unique_pp)} ({100*len(unique_pp)/len(unique_b_middles):.1f}%)")
print(f"  B-exclusive (not in A, always active): {len(unique_b_exclusive)} ({100*len(unique_b_exclusive)/len(unique_b_middles):.1f}%)")

# Per-folio breakdown
print(f"\n{'='*70}")
print("PER-FOLIO UNIQUE MIDDLE BREAKDOWN")
print(f"{'='*70}")

print(f"\n{'Folio':<10} {'Unique':<10} {'PP':<10} {'B-Excl':<10} {'%PP':<10}")
print("-" * 50)

folio_stats = []
for folio in sorted(b_folio_middles.keys()):
    middles = b_folio_middles[folio]
    unique = [m for m in middles if middle_folio_count[m] == 1]
    unique_in_pp = [m for m in unique if m in pp_middles]
    unique_in_bex = [m for m in unique if m in b_exclusive]

    pct_pp = 100 * len(unique_in_pp) / len(unique) if unique else 0

    folio_stats.append({
        'folio': folio,
        'unique': len(unique),
        'pp': len(unique_in_pp),
        'bex': len(unique_in_bex),
        'pct_pp': pct_pp
    })

    print(f"{folio:<10} {len(unique):<10} {len(unique_in_pp):<10} {len(unique_in_bex):<10} {pct_pp:.0f}%")

# Summary statistics
pp_counts = [s['pp'] for s in folio_stats]
bex_counts = [s['bex'] for s in folio_stats]

import numpy as np
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

print(f"""
UNIQUE B MIDDLEs breakdown:
  - In A->B pipeline (PP): {len(unique_pp)} ({100*len(unique_pp)/len(unique_b_middles):.1f}%)
    => These require A record activation, subject to AZC filtering

  - B-exclusive: {len(unique_b_exclusive)} ({100*len(unique_b_exclusive)/len(unique_b_middles):.1f}%)
    => These exist only in B, always "active" (no A/AZC dependency)

Per folio:
  - Mean PP unique: {np.mean(pp_counts):.1f}
  - Mean B-exclusive unique: {np.mean(bex_counts):.1f}
""")

# Check what B-exclusive MIDDLEs look like
print(f"\n{'='*70}")
print("B-EXCLUSIVE UNIQUE MIDDLEs (sample)")
print(f"{'='*70}")

# Sample some
sample_bex = list(unique_b_exclusive)[:20]
print(f"\nSample of {len(sample_bex)} B-exclusive unique MIDDLEs:")
for m in sample_bex:
    # Find which folio it's in
    folio = [f for f, middles in b_folio_middles.items() if m in middles][0]
    print(f"  '{m}' (len={len(m)}) in {folio}")

# Length comparison
pp_lengths = [len(m) for m in unique_pp]
bex_lengths = [len(m) for m in unique_b_exclusive]

print(f"\n{'='*70}")
print("LENGTH COMPARISON")
print(f"{'='*70}")
print(f"PP unique MIDDLEs: mean length = {np.mean(pp_lengths):.2f}")
print(f"B-exclusive unique MIDDLEs: mean length = {np.mean(bex_lengths):.2f}")

print(f"\n{'='*70}")
print("INTERPRETATION")
print(f"{'='*70}")

if len(unique_b_exclusive) > len(unique_pp):
    print(f"""
MAJORITY B-EXCLUSIVE:

{100*len(unique_b_exclusive)/len(unique_b_middles):.0f}% of unique B MIDDLEs are B-exclusive.
These are NOT in the A->B pipeline - they exist only in B.

This means:
- They are ALWAYS available (no AZC filtering)
- They don't require A record activation
- They are part of B's internal grammar, not A-derived content

The unique vocabulary per folio is primarily B-internal,
not A-sourced material that could be filtered.
""")
else:
    print(f"""
MAJORITY PP (A-derived):

{100*len(unique_pp)/len(unique_b_middles):.0f}% of unique B MIDDLEs are in the A->B pipeline.
These require A record activation and are subject to AZC filtering.

This means:
- Their activation depends on which A record is used
- AZC position determines their legality
- They may not always be "active" in execution
""")
