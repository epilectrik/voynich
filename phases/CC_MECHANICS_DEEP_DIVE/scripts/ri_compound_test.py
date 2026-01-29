"""
Quick test: Are RI compound MIDDLEs in the same way B compounds are?
Compare RI containment of PP atoms vs B MIDDLE containment of simpler MIDDLEs.
"""

import json
import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("RI vs B COMPOUND STRUCTURE COMPARISON")
print("="*70)

# ============================================================
# COLLECT ALL MIDDLES BY SYSTEM
# ============================================================

# Get all A MIDDLEs
a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_middles.add(m.middle)

# Get all B MIDDLEs
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

# PP = shared between A and B
pp_middles = a_middles & b_middles

# RI = A-exclusive
ri_middles = a_middles - b_middles

# B-exclusive
b_exclusive = b_middles - a_middles

print(f"\nMIDDLE inventory:")
print(f"  A total: {len(a_middles)}")
print(f"  B total: {len(b_middles)}")
print(f"  PP (shared): {len(pp_middles)}")
print(f"  RI (A-exclusive): {len(ri_middles)}")
print(f"  B-exclusive: {len(b_exclusive)}")

# ============================================================
# TEST: DO RI CONTAIN PP ATOMS?
# ============================================================
print("\n" + "="*70)
print("RI CONTAINMENT OF PP ATOMS")
print("="*70)

ri_contains_pp = 0
ri_pp_counts = []

for ri in ri_middles:
    contained = [pp for pp in pp_middles if pp in ri and pp != ri]
    if contained:
        ri_contains_pp += 1
        ri_pp_counts.append(len(contained))

ri_containment_rate = 100 * ri_contains_pp / len(ri_middles) if ri_middles else 0
print(f"\nRI containing PP atoms: {ri_contains_pp}/{len(ri_middles)} = {ri_containment_rate:.1f}%")
if ri_pp_counts:
    print(f"Mean PP atoms per RI: {sum(ri_pp_counts)/len(ri_pp_counts):.2f}")

# ============================================================
# TEST: DO B-EXCLUSIVE CONTAIN PP ATOMS?
# ============================================================
print("\n" + "="*70)
print("B-EXCLUSIVE CONTAINMENT OF PP ATOMS")
print("="*70)

b_contains_pp = 0
b_pp_counts = []

for bm in b_exclusive:
    contained = [pp for pp in pp_middles if pp in bm and pp != bm]
    if contained:
        b_contains_pp += 1
        b_pp_counts.append(len(contained))

b_containment_rate = 100 * b_contains_pp / len(b_exclusive) if b_exclusive else 0
print(f"\nB-exclusive containing PP atoms: {b_contains_pp}/{len(b_exclusive)} = {b_containment_rate:.1f}%")
if b_pp_counts:
    print(f"Mean PP atoms per B-exclusive: {sum(b_pp_counts)/len(b_pp_counts):.2f}")

# ============================================================
# TEST: DO B-EXCLUSIVE CONTAIN OTHER B MIDDLES?
# ============================================================
print("\n" + "="*70)
print("B-EXCLUSIVE CONTAINMENT OF ANY B MIDDLE")
print("="*70)

b_contains_b = 0
b_b_counts = []

for bm in b_exclusive:
    contained = [other for other in b_middles if other in bm and other != bm and len(other) > 1]
    if contained:
        b_contains_b += 1
        b_b_counts.append(len(contained))

b_b_rate = 100 * b_contains_b / len(b_exclusive) if b_exclusive else 0
print(f"\nB-exclusive containing other B MIDDLEs: {b_contains_b}/{len(b_exclusive)} = {b_b_rate:.1f}%")
if b_b_counts:
    print(f"Mean contained MIDDLEs per B-exclusive: {sum(b_b_counts)/len(b_b_counts):.2f}")

# ============================================================
# LENGTH COMPARISON
# ============================================================
print("\n" + "="*70)
print("LENGTH COMPARISON")
print("="*70)

pp_lens = [len(m) for m in pp_middles]
ri_lens = [len(m) for m in ri_middles]
b_excl_lens = [len(m) for m in b_exclusive]

print(f"\nMean MIDDLE length:")
print(f"  PP (shared): {sum(pp_lens)/len(pp_lens):.2f}")
print(f"  RI (A-exclusive): {sum(ri_lens)/len(ri_lens):.2f}")
print(f"  B-exclusive: {sum(b_excl_lens)/len(b_excl_lens):.2f}")

# ============================================================
# EXAMPLES
# ============================================================
print("\n" + "="*70)
print("EXAMPLES")
print("="*70)

print("\nSample RI with their PP atoms:")
ri_with_pp = [(ri, [pp for pp in pp_middles if pp in ri and pp != ri])
              for ri in sorted(ri_middles, key=len, reverse=True)[:10]]
for ri, pps in ri_with_pp:
    if pps:
        print(f"  '{ri}' contains: {pps[:5]}")

print("\nSample B-exclusive with their PP atoms:")
b_with_pp = [(bm, [pp for pp in pp_middles if pp in bm and pp != bm])
             for bm in sorted(b_exclusive, key=len, reverse=True)[:10]]
for bm, pps in b_with_pp:
    if pps:
        print(f"  '{bm}' contains: {pps[:5]}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

print(f"""
COMPOUND STRUCTURE COMPARISON:

  RI (A-exclusive):
    - {ri_containment_rate:.1f}% contain PP atoms
    - Mean length: {sum(ri_lens)/len(ri_lens):.2f}

  B-exclusive:
    - {b_containment_rate:.1f}% contain PP atoms
    - {b_b_rate:.1f}% contain any B MIDDLE
    - Mean length: {sum(b_excl_lens)/len(b_excl_lens):.2f}

  PP (shared primitives):
    - Mean length: {sum(pp_lens)/len(pp_lens):.2f}

CONCLUSION: {'SAME PATTERN - both RI and B-exclusive are compounds built from PP primitives'
             if ri_containment_rate > 80 and b_containment_rate > 80
             else 'DIFFERENT PATTERNS - need further analysis'}
""")
