"""
24_b_only_excluding_ht.py

Re-run B-only vocabulary analysis EXCLUDING HT (gallows-initial) tokens.

HT tokens are paragraph-initial markers. They might have special vocabulary
that inflates the "B-only" count.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("B-ONLY VOCABULARY ANALYSIS (EXCLUDING HT)")
print("="*70)

tx = Transcript()
morph = Morphology()

GALLOWS = {'k', 't', 'p', 'f'}

def is_gallows_initial(word):
    """Check if word starts with a gallows letter."""
    if not word:
        return False
    return word[0] in GALLOWS

# =============================================================
# STEP 1: Build vocabulary sets (with and without HT)
# =============================================================
print("\nSTEP 1: Building vocabulary sets...")

# A vocabulary
a_middles_all = set()
a_middles_no_ht = set()
a_ht_middles = set()

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle:
            a_middles_all.add(m.middle)
            if is_gallows_initial(t.word):
                a_ht_middles.add(m.middle)
            else:
                a_middles_no_ht.add(m.middle)
    except:
        pass

# B vocabulary
b_middles_all = set()
b_middles_no_ht = set()
b_ht_middles = set()
b_middle_counts = Counter()
b_ht_counts = Counter()

for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle:
            b_middles_all.add(m.middle)
            b_middle_counts[m.middle] += 1
            if is_gallows_initial(t.word):
                b_ht_middles.add(m.middle)
                b_ht_counts[m.middle] += 1
            else:
                b_middles_no_ht.add(m.middle)
    except:
        pass

print(f"\nA MIDDLEs: {len(a_middles_all)} total, {len(a_middles_no_ht)} non-HT, {len(a_ht_middles)} HT")
print(f"B MIDDLEs: {len(b_middles_all)} total, {len(b_middles_no_ht)} non-HT, {len(b_ht_middles)} HT")

# =============================================================
# STEP 2: Compare with and without HT
# =============================================================
print("\n" + "="*70)
print("STEP 2: Vocabulary overlap comparison")
print("="*70)

# ALL tokens
b_only_all = b_middles_all - a_middles_all
shared_all = b_middles_all & a_middles_all

print(f"\nALL TOKENS:")
print(f"  Shared: {len(shared_all)} ({100*len(shared_all)/len(b_middles_all):.1f}% of B)")
print(f"  B-only: {len(b_only_all)} ({100*len(b_only_all)/len(b_middles_all):.1f}% of B)")

# Excluding HT from both
b_only_no_ht = b_middles_no_ht - a_middles_no_ht
shared_no_ht = b_middles_no_ht & a_middles_no_ht

print(f"\nEXCLUDING HT (non-gallows-initial only):")
print(f"  B non-HT MIDDLEs: {len(b_middles_no_ht)}")
print(f"  A non-HT MIDDLEs: {len(a_middles_no_ht)}")
print(f"  Shared: {len(shared_no_ht)} ({100*len(shared_no_ht)/len(b_middles_no_ht):.1f}% of B non-HT)")
print(f"  B-only: {len(b_only_no_ht)} ({100*len(b_only_no_ht)/len(b_middles_no_ht):.1f}% of B non-HT)")

# =============================================================
# STEP 3: Analyze HT-specific vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 3: HT-specific vocabulary analysis")
print("="*70)

# HT vocabulary unique to B
b_ht_only = b_ht_middles - a_middles_all  # HT middles not in ANY of A
b_ht_shared = b_ht_middles & a_middles_all

print(f"\nB HT vocabulary:")
print(f"  Total HT MIDDLEs in B: {len(b_ht_middles)}")
print(f"  Shared with A (any): {len(b_ht_shared)} ({100*len(b_ht_shared)/len(b_ht_middles):.1f}%)")
print(f"  B HT-only: {len(b_ht_only)} ({100*len(b_ht_only)/len(b_ht_middles):.1f}%)")

# What are the most common B HT-only MIDDLEs?
print(f"\nMost common B HT-only MIDDLEs:")
ht_only_counts = {m: b_ht_counts[m] for m in b_ht_only}
for mid, count in sorted(ht_only_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {mid}: {count}")

# =============================================================
# STEP 4: What about comparing just PP tokens?
# =============================================================
print("\n" + "="*70)
print("STEP 4: PP-only comparison (using B as PP reference)")
print("="*70)

# Get the PP MIDDLEs from B (standard set)
ri_middles, pp_middles = load_middle_classes()

# A PP vocabulary (non-HT)
a_pp_middles = set()
for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    if is_gallows_initial(t.word):
        continue  # Skip HT
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            a_pp_middles.add(m.middle)
    except:
        pass

# B PP vocabulary (non-HT)
b_pp_middles = set()
for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    if is_gallows_initial(t.word):
        continue  # Skip HT
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            b_pp_middles.add(m.middle)
    except:
        pass

shared_pp = b_pp_middles & a_pp_middles
b_only_pp = b_pp_middles - a_pp_middles

print(f"\nPP tokens only (non-HT):")
print(f"  A PP MIDDLEs: {len(a_pp_middles)}")
print(f"  B PP MIDDLEs: {len(b_pp_middles)}")
print(f"  Shared: {len(shared_pp)} ({100*len(shared_pp)/len(b_pp_middles):.1f}% of B PP)")
print(f"  B-only PP: {len(b_only_pp)} ({100*len(b_only_pp)/len(b_pp_middles):.1f}% of B PP)")

# =============================================================
# STEP 5: Token instance counts
# =============================================================
print("\n" + "="*70)
print("STEP 5: Token INSTANCE counts (not unique)")
print("="*70)

# Count actual token instances
a_instance_count = 0
a_ht_instance_count = 0
for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    a_instance_count += 1
    if is_gallows_initial(t.word):
        a_ht_instance_count += 1

b_instance_count = 0
b_ht_instance_count = 0
b_shared_instances = 0
b_only_instances = 0

for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    b_instance_count += 1
    if is_gallows_initial(t.word):
        b_ht_instance_count += 1
    try:
        m = morph.extract(t.word)
        if m.middle:
            if m.middle in a_middles_all:
                b_shared_instances += 1
            else:
                b_only_instances += 1
    except:
        pass

print(f"\nA tokens: {a_instance_count} total, {a_ht_instance_count} HT ({100*a_ht_instance_count/a_instance_count:.1f}%)")
print(f"B tokens: {b_instance_count} total, {b_ht_instance_count} HT ({100*b_ht_instance_count/b_instance_count:.1f}%)")

print(f"\nB token INSTANCES by vocabulary source:")
print(f"  Shared with A: {b_shared_instances} ({100*b_shared_instances/b_instance_count:.1f}%)")
print(f"  B-only: {b_only_instances} ({100*b_only_instances/b_instance_count:.1f}%)")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Does excluding HT tokens change the picture?

UNIQUE MIDDLE TYPES:
                        All tokens    Excluding HT
  B MIDDLEs             {len(b_middles_all):<6}        {len(b_middles_no_ht)}
  Shared with A         {len(shared_all)} ({100*len(shared_all)/len(b_middles_all):.1f}%)      {len(shared_no_ht)} ({100*len(shared_no_ht)/len(b_middles_no_ht):.1f}%)
  B-only                {len(b_only_all)} ({100*len(b_only_all)/len(b_middles_all):.1f}%)      {len(b_only_no_ht)} ({100*len(b_only_no_ht)/len(b_middles_no_ht):.1f}%)

PP TOKENS ONLY (non-HT):
  Shared PP: {len(shared_pp)}/{len(b_pp_middles)} ({100*len(shared_pp)/len(b_pp_middles):.1f}%)
  B-only PP: {len(b_only_pp)}/{len(b_pp_middles)} ({100*len(b_only_pp)/len(b_pp_middles):.1f}%)

TOKEN INSTANCES:
  B instances with shared MIDDLEs: {b_shared_instances}/{b_instance_count} ({100*b_shared_instances/b_instance_count:.1f}%)
  B instances with B-only MIDDLEs: {b_only_instances}/{b_instance_count} ({100*b_only_instances/b_instance_count:.1f}%)
""")

if 100*len(shared_no_ht)/len(b_middles_no_ht) > 50:
    print("CONCLUSION: Excluding HT significantly increases overlap.")
    print("HT tokens have specialized vocabulary that inflated B-only count.")
else:
    print("CONCLUSION: Even excluding HT, significant B-only vocabulary remains.")
    print("A and B have genuinely different vocabulary sets.")
