#!/usr/bin/env python3
"""
Test 17: Q-Token Classification

Are the Rosettes Q-tokens PP (Procedural Primitives)?
What instruction classes do they belong to?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter
from scripts.voynich import Morphology, RecordAnalyzer

# The Q tokens from the Rosettes
Q_TOKENS = [
    'or', 'or', 'or',
    'dar', 'dar', 'dar',
    'shol', 'shol',
    'chol', 'chol',
    'tchdy', 'tchdy',
    'tshdcsey', 'dalkshdy', 'shocfhy', 'saiin', 'airody', 'chedaly',
    'dcheody', 'skeeody', 'qokshey', 'chodain', 'ykched', 'raraldy',
    'dsheody', 'qokchey', 'dal', 'odaiin', 'sar', 'pchedaiin',
    'dchedy', 'qokchdy', 'qopchol', 'sheody', 'rolkam', 'dchey',
    'otain', 'olkechy', 'qokam', 'kchdy', 'aiin', 'dy', 'lshodair',
    'ykcho', 'chody', 'ykeeody', 'qochey', 'chcthey', 'lkar', 'ary',
    'dshedy', 'kshey', 'shdy', 'ralkchedy', 'ytchol', 'qoty', 'okshy',
    'tam', 'ytchdy', 'alor'
]

morph = Morphology()
analyzer = RecordAnalyzer()

print("=" * 70)
print("TEST 17: Q-TOKEN CLASSIFICATION")
print("=" * 70)
print()

# 1. Morphological breakdown
print("1. MORPHOLOGICAL BREAKDOWN")
print("-" * 50)

unique_q = set(Q_TOKENS)
print(f"{'Token':<15} {'PREFIX':<8} {'MIDDLE':<12} {'SUFFIX':<8} {'ARTIC':<6}")
print("-" * 49)

prefix_counts = Counter()
middle_counts = Counter()
suffix_counts = Counter()
artic_counts = Counter()

for token in sorted(unique_q):
    m = morph.extract(token)
    prefix = m.prefix if m.prefix else '-'
    middle = m.middle if m.middle else '-'
    suffix = m.suffix if m.suffix else '-'
    artic = m.articulator if m.articulator else '-'

    prefix_counts[prefix] += 1
    middle_counts[middle] += 1
    suffix_counts[suffix] += 1
    artic_counts[artic] += 1

    print(f"{token:<15} {prefix:<8} {middle:<12} {suffix:<8} {artic:<6}")

print()

# 2. PREFIX distribution
print("2. PREFIX DISTRIBUTION")
print("-" * 50)

for prefix, count in prefix_counts.most_common():
    pct = count / len(unique_q) * 100
    print(f"  {prefix:<8}: {count:>3} ({pct:.1f}%)")

print()

# 3. Check against instruction classes
print("3. INSTRUCTION CLASS ANALYSIS")
print("-" * 50)

# Get the 49 instruction classes from BCSC
# Classes are defined by PREFIX + MIDDLE combinations
# Let me extract MIDDLEs and check their roles

print("\nMIDDLE distribution:")
for middle, count in middle_counts.most_common(15):
    pct = count / len(unique_q) * 100
    print(f"  {middle:<12}: {count:>3} ({pct:.1f}%)")

print()

# 4. Check for kernel characters (k, h, e)
print("4. KERNEL CHARACTER ANALYSIS")
print("-" * 50)

has_k = []
has_h = []
has_e = []
has_none = []

for token in unique_q:
    has_kernel = False
    if 'k' in token:
        has_k.append(token)
        has_kernel = True
    if 'h' in token:
        has_h.append(token)
        has_kernel = True
    if 'e' in token:
        has_e.append(token)
        has_kernel = True
    if not has_kernel:
        has_none.append(token)

print(f"Tokens with 'k': {len(has_k)} ({len(has_k)/len(unique_q)*100:.1f}%)")
print(f"Tokens with 'h': {len(has_h)} ({len(has_h)/len(unique_q)*100:.1f}%)")
print(f"Tokens with 'e': {len(has_e)} ({len(has_e)/len(unique_q)*100:.1f}%)")
print(f"Tokens with NO kernel: {len(has_none)} ({len(has_none)/len(unique_q)*100:.1f}%)")

if has_none:
    print(f"\nNo-kernel tokens: {sorted(has_none)}")

print()

# 5. RI vs PP classification attempt
print("5. RI vs PP CLASSIFICATION")
print("-" * 50)

# RI tokens typically: first-line, specific prefixes, linking function
# PP tokens: procedural primitives, execution instructions

# Check for RI-associated patterns
ri_prefixes = {'s', 'ot', 'ok', 'op'}  # Common RI prefixes
pp_prefixes = {'ch', 'sh', 'qo', 'da'}  # Common PP prefixes

ri_like = []
pp_like = []
unknown = []

for token in unique_q:
    m = morph.extract(token)
    prefix = m.prefix if m.prefix else ''

    # Simple heuristic based on prefix
    if prefix in ri_prefixes or (prefix == '' and token.startswith(('s', 'ot', 'ok'))):
        ri_like.append(token)
    elif prefix in pp_prefixes or prefix.startswith(('ch', 'sh', 'qo', 'da')):
        pp_like.append(token)
    else:
        unknown.append(token)

print(f"RI-like tokens (s, ot, ok, op prefixes): {len(ri_like)}")
if ri_like:
    print(f"  {sorted(ri_like)}")

print(f"\nPP-like tokens (ch, sh, qo, da prefixes): {len(pp_like)}")
if pp_like:
    print(f"  {sorted(pp_like)}")

print(f"\nUncategorized: {len(unknown)}")
if unknown:
    print(f"  {sorted(unknown)}")

print()

# 6. Suffix analysis (functional markers)
print("6. SUFFIX ANALYSIS (FUNCTIONAL MARKERS)")
print("-" * 50)

for suffix, count in suffix_counts.most_common():
    pct = count / len(unique_q) * 100
    print(f"  {suffix:<8}: {count:>3} ({pct:.1f}%)")

print()

# 7. Summary
print("=" * 70)
print("CLASSIFICATION SUMMARY")
print("=" * 70)

# Count by broad category
no_prefix = prefix_counts.get('-', 0)
with_prefix = len(unique_q) - no_prefix

print(f"""
Q-TOKEN STRUCTURAL PROFILE:

1. Morphological completeness:
   - With PREFIX: {with_prefix} ({with_prefix/len(unique_q)*100:.1f}%)
   - No PREFIX (bare): {no_prefix} ({no_prefix/len(unique_q)*100:.1f}%)

2. Top PREFIXes:
   - qo-: {prefix_counts.get('qo', 0)} tokens (PP-associated)
   - ch-: {prefix_counts.get('ch', 0)} tokens (PP-associated)
   - sh-: {prefix_counts.get('sh', 0)} tokens (PP-associated)
   - da-: {prefix_counts.get('da', 0)} tokens (PP-associated)
   - ot-: {prefix_counts.get('ot', 0)} tokens (mixed)

3. Kernel content:
   - Contains 'e': {len(has_e)} tokens ({len(has_e)/len(unique_q)*100:.1f}%)
   - Contains 'h': {len(has_h)} tokens ({len(has_h)/len(unique_q)*100:.1f}%)
   - Contains 'k': {len(has_k)} tokens ({len(has_k)/len(unique_q)*100:.1f}%)

4. Classification estimate:
   - RI-like: {len(ri_like)} tokens ({len(ri_like)/len(unique_q)*100:.1f}%)
   - PP-like: {len(pp_like)} tokens ({len(pp_like)/len(unique_q)*100:.1f}%)
""")

if len(pp_like) > len(ri_like):
    print("CONCLUSION: Q-tokens are predominantly PP (Procedural Primitives)")
    print("These are execution instructions, not registry/linking tokens.")
elif len(ri_like) > len(pp_like):
    print("CONCLUSION: Q-tokens are predominantly RI (Registry Items)")
    print("These function as references/links, not execution instructions.")
else:
    print("CONCLUSION: Q-tokens show mixed RI/PP characteristics.")
