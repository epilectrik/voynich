"""
23_b_only_vocabulary.py

What B vocabulary is NEVER in A?

If A "constrains" B, uncovered vocabulary would be "illegal."
But B is self-contained and functional, so what's going on?

Questions:
1. How much B vocabulary is not in any A folio?
2. What does this vocabulary look like (morphologically)?
3. Is it a specific function (infrastructure, kernel, etc.)?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("B-ONLY VOCABULARY ANALYSIS")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# =============================================================
# STEP 1: Build vocabulary sets
# =============================================================
print("\nSTEP 1: Building vocabulary sets...")

# A vocabulary (MIDDLEs and full tokens)
a_middles = set()
a_tokens = set()
a_prefixes = Counter()

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    a_tokens.add(t.word)
    try:
        m = morph.extract(t.word)
        if m.middle:
            a_middles.add(m.middle)
        if m.prefix:
            a_prefixes[m.prefix] += 1
    except:
        pass

# B vocabulary (MIDDLEs and full tokens)
b_middles = set()
b_tokens = set()
b_middle_counts = Counter()
b_prefixes = Counter()

for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    b_tokens.add(t.word)
    try:
        m = morph.extract(t.word)
        if m.middle:
            b_middles.add(m.middle)
            b_middle_counts[m.middle] += 1
        if m.prefix:
            b_prefixes[m.prefix] += 1
    except:
        pass

print(f"A MIDDLEs: {len(a_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"A tokens: {len(a_tokens)}")
print(f"B tokens: {len(b_tokens)}")

# =============================================================
# STEP 2: Find B-only vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 2: B-only vocabulary")
print("="*70)

b_only_middles = b_middles - a_middles
shared_middles = b_middles & a_middles
a_only_middles = a_middles - b_middles

print(f"\nMIDDLE distribution:")
print(f"  Shared (in both A and B): {len(shared_middles)} ({100*len(shared_middles)/len(b_middles):.1f}% of B)")
print(f"  B-only (not in A): {len(b_only_middles)} ({100*len(b_only_middles)/len(b_middles):.1f}% of B)")
print(f"  A-only (not in B): {len(a_only_middles)} ({100*len(a_only_middles)/len(a_middles):.1f}% of A)")

# Token level
b_only_tokens = b_tokens - a_tokens
shared_tokens = b_tokens & a_tokens

print(f"\nFull token distribution:")
print(f"  Shared tokens: {len(shared_tokens)} ({100*len(shared_tokens)/len(b_tokens):.1f}% of B)")
print(f"  B-only tokens: {len(b_only_tokens)} ({100*len(b_only_tokens)/len(b_tokens):.1f}% of B)")

# =============================================================
# STEP 3: What are the B-only MIDDLEs?
# =============================================================
print("\n" + "="*70)
print("STEP 3: What are the B-only MIDDLEs?")
print("="*70)

# Count occurrences of B-only MIDDLEs
b_only_counts = {m: b_middle_counts[m] for m in b_only_middles}
sorted_b_only = sorted(b_only_counts.items(), key=lambda x: -x[1])

print(f"\nMost common B-only MIDDLEs:")
for mid, count in sorted_b_only[:20]:
    # Check if RI or PP
    token_class = "RI" if mid in ri_middles else "PP" if mid in pp_middles else "?"
    print(f"  {mid}: {count} occurrences ({token_class})")

# =============================================================
# STEP 4: Morphological analysis of B-only
# =============================================================
print("\n" + "="*70)
print("STEP 4: Morphological profile of B-only vocabulary")
print("="*70)

# Get tokens that use B-only MIDDLEs
b_only_tokens_list = []
for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle in b_only_middles:
            b_only_tokens_list.append((t.word, m))
    except:
        pass

# PREFIX distribution in B-only
b_only_prefix_counts = Counter()
for word, m in b_only_tokens_list:
    if m.prefix:
        b_only_prefix_counts[m.prefix] += 1

print(f"\nPREFIX distribution in B-only vocabulary:")
total_b_only = len(b_only_tokens_list)
for prefix, count in b_only_prefix_counts.most_common(10):
    pct = 100 * count / total_b_only
    # Compare to overall B
    b_pct = 100 * b_prefixes.get(prefix, 0) / sum(b_prefixes.values())
    print(f"  {prefix}: {pct:.1f}% (vs {b_pct:.1f}% in all B)")

# =============================================================
# STEP 5: Are B-only MIDDLEs concentrated or spread?
# =============================================================
print("\n" + "="*70)
print("STEP 5: B-only usage patterns")
print("="*70)

# How many B folios use B-only vocabulary?
b_only_by_folio = defaultdict(int)
for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle in b_only_middles:
            b_only_by_folio[t.folio] += 1
    except:
        pass

folios_with_b_only = len([f for f, c in b_only_by_folio.items() if c > 0])
total_b_folios = len(set(t.folio for t in tx.currier_b()))

print(f"\nFolios using B-only vocabulary: {folios_with_b_only}/{total_b_folios}")

# Distribution
print(f"\nB-only tokens per folio (top 10):")
sorted_folios = sorted(b_only_by_folio.items(), key=lambda x: -x[1])
for folio, count in sorted_folios[:10]:
    print(f"  {folio}: {count} B-only tokens")

# =============================================================
# STEP 6: Check if B-only are RI or PP
# =============================================================
print("\n" + "="*70)
print("STEP 6: Token class of B-only MIDDLEs")
print("="*70)

b_only_ri = b_only_middles & ri_middles
b_only_pp = b_only_middles & pp_middles
b_only_unknown = b_only_middles - ri_middles - pp_middles

print(f"\nB-only MIDDLEs by class:")
print(f"  RI (identity): {len(b_only_ri)} ({100*len(b_only_ri)/len(b_only_middles):.1f}%)")
print(f"  PP (procedure): {len(b_only_pp)} ({100*len(b_only_pp)/len(b_only_middles):.1f}%)")
print(f"  Unknown: {len(b_only_unknown)} ({100*len(b_only_unknown)/len(b_only_middles):.1f}%)")

if b_only_ri:
    print(f"\n  B-only RI MIDDLEs: {sorted(b_only_ri)[:10]}...")
if b_only_pp:
    print(f"\n  B-only PP MIDDLEs: {sorted(b_only_pp)[:10]}...")

# =============================================================
# STEP 7: Compare kernel content
# =============================================================
print("\n" + "="*70)
print("STEP 7: Kernel content comparison")
print("="*70)

def kernel_profile(middles):
    k_count = sum(1 for m in middles if 'k' in m)
    h_count = sum(1 for m in middles if 'h' in m)
    e_count = sum(1 for m in middles if 'e' in m)
    n = len(middles)
    return {
        'k': k_count / n if n > 0 else 0,
        'h': h_count / n if n > 0 else 0,
        'e': e_count / n if n > 0 else 0,
    }

shared_kernel = kernel_profile(shared_middles)
b_only_kernel = kernel_profile(b_only_middles)

print(f"\nKernel character rates:")
print(f"              Shared    B-only")
print(f"  k rate:     {shared_kernel['k']:.3f}     {b_only_kernel['k']:.3f}")
print(f"  h rate:     {shared_kernel['h']:.3f}     {b_only_kernel['h']:.3f}")
print(f"  e rate:     {shared_kernel['e']:.3f}     {b_only_kernel['e']:.3f}")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
B VOCABULARY NOT IN A:

1. MIDDLE level:
   - {len(b_only_middles)} B MIDDLEs ({100*len(b_only_middles)/len(b_middles):.1f}%) never appear in A
   - {len(shared_middles)} MIDDLEs ({100*len(shared_middles)/len(b_middles):.1f}%) are shared

2. Token level:
   - {len(b_only_tokens)} B tokens ({100*len(b_only_tokens)/len(b_tokens):.1f}%) never appear in A
   - Full tokens are more unique (PREFIX+MIDDLE+SUFFIX combinations)

3. Token class:
   - B-only RI: {len(b_only_ri)} ({100*len(b_only_ri)/len(b_only_middles):.1f}%)
   - B-only PP: {len(b_only_pp)} ({100*len(b_only_pp)/len(b_only_middles):.1f}%)

4. Distribution:
   - {folios_with_b_only}/{total_b_folios} B folios use B-only vocabulary
   - B-only vocabulary is {'widespread' if folios_with_b_only > 0.8 * total_b_folios else 'concentrated'}

INTERPRETATION:
""")

if len(b_only_middles) / len(b_middles) > 0.3:
    print("A significant portion of B vocabulary is B-specific.")
    print("This suggests A and B have OVERLAPPING but DISTINCT vocabularies.")
    print("A doesn't 'constrain' B - they're parallel systems with shared terms.")
else:
    print("Most B vocabulary appears in A.")
    print("The B-only vocabulary may be procedural infrastructure.")
