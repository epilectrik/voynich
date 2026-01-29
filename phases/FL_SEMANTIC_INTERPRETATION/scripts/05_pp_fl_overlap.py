"""
05_pp_fl_overlap.py

Check if PP MIDDLEs in Currier A share structure with FL MIDDLEs in Currier B.
Can we apply FL semantic framework to PP tokens?
"""
import sys
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class map for FL identification
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
FL_CLASSES = {7, 30, 38, 40}

# Get FL MIDDLEs from B
tx = Transcript()
morph = Morphology()

fl_middles = set()
fl_middle_counts = Counter()
for t in tx.currier_b():
    cls = token_to_class.get(t.word)
    if cls in FL_CLASSES:
        m = morph.extract(t.word)
        if m and m.middle:
            fl_middles.add(m.middle)
            fl_middle_counts[m.middle] += 1

print("=" * 60)
print("FL MIDDLEs in Currier B")
print("=" * 60)
print(f"FL MIDDLEs: {sorted(fl_middles)}")
print(f"Count: {len(fl_middles)}")

# Get all MIDDLEs from A and B
a_middles = set()
a_middle_counts = Counter()
b_middles = set()

for t in tx.currier_a():
    m = morph.extract(t.word)
    if m and m.middle:
        a_middles.add(m.middle)
        a_middle_counts[m.middle] += 1

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

pp_middles = a_middles & b_middles  # Shared = PP
ri_middles = a_middles - b_middles  # A-only = RI

print(f"\n" + "=" * 60)
print("MIDDLE Inventory")
print("=" * 60)
print(f"A MIDDLEs: {len(a_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"PP MIDDLEs (A & B): {len(pp_middles)}")
print(f"RI MIDDLEs (A-only): {len(ri_middles)}")

# Check overlap between FL and PP
fl_in_pp = fl_middles & pp_middles
fl_not_pp = fl_middles - pp_middles

print(f"\n" + "=" * 60)
print("FL-PP Overlap")
print("=" * 60)
print(f"FL MIDDLEs that are PP: {len(fl_in_pp)}/{len(fl_middles)} = {len(fl_in_pp)/len(fl_middles)*100:.1f}%")
print(f"FL MIDDLEs in PP: {sorted(fl_in_pp)}")
print(f"FL MIDDLEs NOT in PP: {sorted(fl_not_pp) if fl_not_pp else 'NONE'}")

# What PP MIDDLEs are NOT FL?
pp_not_fl = pp_middles - fl_middles
print(f"\nPP MIDDLEs that are NOT FL: {len(pp_not_fl)}")

# Check: do PP MIDDLEs contain kernel characters?
print(f"\n" + "=" * 60)
print("PP MIDDLEs: Kernel Character Analysis")
print("=" * 60)

kernel_chars = set('khe')
pp_with_kernel = set()
pp_without_kernel = set()

for mid in pp_middles:
    if any(c in mid for c in kernel_chars):
        pp_with_kernel.add(mid)
    else:
        pp_without_kernel.add(mid)

print(f"PP with kernel (k/h/e): {len(pp_with_kernel)} ({len(pp_with_kernel)/len(pp_middles)*100:.1f}%)")
print(f"PP without kernel: {len(pp_without_kernel)} ({len(pp_without_kernel)/len(pp_middles)*100:.1f}%)")

# FL is kernel-free, so kernel-free PP might have FL-like semantics
print(f"\nKernel-free PP that are FL: {len(fl_in_pp)}")
print(f"Kernel-free PP that are NOT FL: {len(pp_without_kernel - fl_middles)}")

# Show some examples
print(f"\n" + "=" * 60)
print("Kernel-Free PP MIDDLEs (FL-like substrate)")
print("=" * 60)
kernel_free_pp = sorted(pp_without_kernel, key=lambda x: -a_middle_counts.get(x, 0))
for mid in kernel_free_pp[:30]:
    is_fl = "FL" if mid in fl_middles else "  "
    a_count = a_middle_counts.get(mid, 0)
    print(f"  {mid:10} [{is_fl}]  A-count: {a_count}")

# Show PP MIDDLEs with kernel (non-FL)
print(f"\n" + "=" * 60)
print("PP MIDDLEs WITH Kernel (EN-like operators)")
print("=" * 60)
kernel_pp = sorted(pp_with_kernel, key=lambda x: -a_middle_counts.get(x, 0))
for mid in kernel_pp[:30]:
    a_count = a_middle_counts.get(mid, 0)
    kernels = [c for c in 'khe' if c in mid]
    print(f"  {mid:10} [{','.join(kernels)}]  A-count: {a_count}")

# Summary
print(f"\n" + "=" * 60)
print("SEMANTIC ASSIGNMENT POTENTIAL")
print("=" * 60)
print(f"""
Based on the analysis:

1. FL MIDDLEs are 100% kernel-free (by definition, C770)
2. All {len(fl_in_pp)} FL MIDDLEs appear in PP vocabulary
3. PP has {len(pp_without_kernel)} kernel-free MIDDLEs (potential FL-like)
4. PP has {len(pp_with_kernel)} kernel-containing MIDDLEs (potential EN-like)

POTENTIAL SEMANTIC ASSIGNMENTS:

A) Kernel-free PP MIDDLEs -> STATE INDICES (like FL)
   - Could mark material/process states in A registry
   - {len(fl_in_pp)} directly map to B's FL states
   - Additional {len(pp_without_kernel - fl_middles)} may have similar function

B) Kernel-containing PP MIDDLEs -> OPERATORS (like EN)
   - Could mark transformations/operations in A registry
   - k = energy-related operations
   - h = phase-related operations
   - e = stability-related operations

CAVEAT: A records are REGISTRY ENTRIES, not execution sequences.
The semantics may be:
  - FL-like PP = "what states are relevant to this entry"
  - EN-like PP = "what operations are relevant to this entry"

This is speculative (Tier 3) but structurally motivated.
""")
