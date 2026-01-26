#!/usr/bin/env python3
"""
Investigate internal structure of PREFIX-FORBIDDEN RI MIDDLEs.

Questions:
1. Do they share sub-components (superstring compression)?
2. Are there recurring patterns/themes?
3. How do they compare to PREFIX-REQUIRED MIDDLEs?
4. Any parametric structure?
"""

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

def has_prefix(token):
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return True
    return False

# Classify MIDDLEs
appears_with_prefix = set()
appears_without_prefix = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        # For RI MIDDLEs, check the raw token
        for m in ri_middles:
            if m in word:
                if has_prefix(word):
                    appears_with_prefix.add(m)
                else:
                    appears_without_prefix.add(m)

prefix_required = appears_with_prefix - appears_without_prefix
prefix_forbidden = appears_without_prefix - appears_with_prefix

print("="*70)
print("PREFIX-FORBIDDEN RI MIDDLE STRUCTURE ANALYSIS")
print("="*70)
print(f"\nPREFIX-REQUIRED: {len(prefix_required)} MIDDLEs")
print(f"PREFIX-FORBIDDEN: {len(prefix_forbidden)} MIDDLEs")

# ============================================================
# 1. LENGTH DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("1. LENGTH DISTRIBUTION")
print("="*70)

req_lengths = Counter(len(m) for m in prefix_required)
forb_lengths = Counter(len(m) for m in prefix_forbidden)

print("\nPREFIX-REQUIRED length distribution:")
for length in sorted(req_lengths.keys()):
    pct = 100 * req_lengths[length] / len(prefix_required)
    bar = '#' * int(pct / 2)
    print(f"  len={length}: {req_lengths[length]:3d} ({pct:5.1f}%) {bar}")

print("\nPREFIX-FORBIDDEN length distribution:")
for length in sorted(forb_lengths.keys()):
    pct = 100 * forb_lengths[length] / len(prefix_forbidden)
    bar = '#' * int(pct / 2)
    print(f"  len={length}: {forb_lengths[length]:3d} ({pct:5.1f}%) {bar}")

avg_req = sum(len(m) for m in prefix_required) / len(prefix_required)
avg_forb = sum(len(m) for m in prefix_forbidden) / len(prefix_forbidden)
print(f"\nAverage length: REQ={avg_req:.2f}, FORB={avg_forb:.2f}")

# ============================================================
# 2. STARTING CHARACTER ANALYSIS
# ============================================================
print("\n" + "="*70)
print("2. STARTING CHARACTER")
print("="*70)

req_starts = Counter(m[0] for m in prefix_required if m)
forb_starts = Counter(m[0] for m in prefix_forbidden if m)

print("\nPREFIX-REQUIRED starting chars (top 10):")
for char, cnt in req_starts.most_common(10):
    pct = 100 * cnt / len(prefix_required)
    print(f"  '{char}': {cnt:3d} ({pct:5.1f}%)")

print("\nPREFIX-FORBIDDEN starting chars (top 10):")
for char, cnt in forb_starts.most_common(10):
    pct = 100 * cnt / len(prefix_forbidden)
    print(f"  '{char}': {cnt:3d} ({pct:5.1f}%)")

# ============================================================
# 3. ENDING CHARACTER ANALYSIS
# ============================================================
print("\n" + "="*70)
print("3. ENDING CHARACTER")
print("="*70)

req_ends = Counter(m[-1] for m in prefix_required if m)
forb_ends = Counter(m[-1] for m in prefix_forbidden if m)

print("\nPREFIX-REQUIRED ending chars (top 10):")
for char, cnt in req_ends.most_common(10):
    pct = 100 * cnt / len(prefix_required)
    print(f"  '{char}': {cnt:3d} ({pct:5.1f}%)")

print("\nPREFIX-FORBIDDEN ending chars (top 10):")
for char, cnt in forb_ends.most_common(10):
    pct = 100 * cnt / len(prefix_forbidden)
    print(f"  '{char}': {cnt:3d} ({pct:5.1f}%)")

# ============================================================
# 4. BIGRAM ANALYSIS (internal structure)
# ============================================================
print("\n" + "="*70)
print("4. INTERNAL BIGRAM STRUCTURE")
print("="*70)

def get_bigrams(s):
    return [s[i:i+2] for i in range(len(s)-1)]

req_bigrams = Counter()
forb_bigrams = Counter()

for m in prefix_required:
    req_bigrams.update(get_bigrams(m))
for m in prefix_forbidden:
    forb_bigrams.update(get_bigrams(m))

print("\nPREFIX-REQUIRED top bigrams:")
for bg, cnt in req_bigrams.most_common(15):
    print(f"  '{bg}': {cnt}")

print("\nPREFIX-FORBIDDEN top bigrams:")
for bg, cnt in forb_bigrams.most_common(15):
    print(f"  '{bg}': {cnt}")

# ============================================================
# 5. SHARED SUBSTRINGS (superstring compression)
# ============================================================
print("\n" + "="*70)
print("5. SHARED SUBSTRINGS (min length 2)")
print("="*70)

def get_substrings(s, min_len=2):
    subs = set()
    for i in range(len(s)):
        for j in range(i + min_len, len(s) + 1):
            subs.add(s[i:j])
    return subs

# Find common substrings in PREFIX-FORBIDDEN
forb_substrings = Counter()
for m in prefix_forbidden:
    for sub in get_substrings(m, min_len=2):
        if len(sub) <= len(m) - 1:  # Not the whole string
            forb_substrings[sub] += 1

# Filter to substrings appearing in multiple MIDDLEs
shared_subs = {s: c for s, c in forb_substrings.items() if c >= 3}

print(f"\nSubstrings appearing in 3+ PREFIX-FORBIDDEN MIDDLEs: {len(shared_subs)}")
print("\nTop 20 shared substrings:")
for sub, cnt in sorted(shared_subs.items(), key=lambda x: (-len(x[0]), -x[1]))[:20]:
    # Find example MIDDLEs containing this substring
    examples = [m for m in prefix_forbidden if sub in m][:3]
    print(f"  '{sub}' ({len(sub)} chars): {cnt} MIDDLEs - examples: {examples}")

# ============================================================
# 6. PATTERN FAMILIES (MIDDLEs sharing long substrings)
# ============================================================
print("\n" + "="*70)
print("6. PATTERN FAMILIES (share 3+ char substring)")
print("="*70)

# Group by shared 3+ char substrings
families = defaultdict(set)
for m in prefix_forbidden:
    for sub in get_substrings(m, min_len=3):
        if len(sub) <= len(m) - 1:
            families[sub].add(m)

# Filter to families with 3+ members
real_families = {k: v for k, v in families.items() if len(v) >= 3}

print(f"\nPattern families with 3+ members: {len(real_families)}")

# Show the largest families
sorted_families = sorted(real_families.items(), key=lambda x: -len(x[1]))
print("\nLargest families:")
for pattern, members in sorted_families[:15]:
    print(f"\n  Pattern '{pattern}':")
    for m in sorted(members)[:8]:
        print(f"    - {m}")
    if len(members) > 8:
        print(f"    ... and {len(members) - 8} more")

# ============================================================
# 7. COMPARE STRUCTURE: REQ vs FORB
# ============================================================
print("\n" + "="*70)
print("7. STRUCTURAL COMPARISON")
print("="*70)

# Unique bigrams
req_unique_bg = set(req_bigrams.keys()) - set(forb_bigrams.keys())
forb_unique_bg = set(forb_bigrams.keys()) - set(req_bigrams.keys())
shared_bg = set(req_bigrams.keys()) & set(forb_bigrams.keys())

print(f"\nBigram overlap:")
print(f"  Shared bigrams: {len(shared_bg)}")
print(f"  REQ-only bigrams: {len(req_unique_bg)}")
print(f"  FORB-only bigrams: {len(forb_unique_bg)}")

print(f"\nFORB-only bigrams (top 10):")
forb_only_sorted = sorted([(bg, forb_bigrams[bg]) for bg in forb_unique_bg], key=lambda x: -x[1])
for bg, cnt in forb_only_sorted[:10]:
    print(f"  '{bg}': {cnt}")

print(f"\nREQ-only bigrams (top 10):")
req_only_sorted = sorted([(bg, req_bigrams[bg]) for bg in req_unique_bg], key=lambda x: -x[1])
for bg, cnt in req_only_sorted[:10]:
    print(f"  '{bg}': {cnt}")

# ============================================================
# 8. CHECK FOR PARAMETRIC PATTERNS
# ============================================================
print("\n" + "="*70)
print("8. PARAMETRIC PATTERNS CHECK")
print("="*70)

# Look for systematic variation: same core with different endings
# Group by first N characters
prefix_groups = defaultdict(list)
for m in prefix_forbidden:
    if len(m) >= 3:
        prefix_groups[m[:3]].append(m)

# Find groups with multiple variants
variant_groups = {k: v for k, v in prefix_groups.items() if len(v) >= 3}

print(f"\nPrefix groups with 3+ variants (first 3 chars same):")
for prefix, variants in sorted(variant_groups.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"  '{prefix}...': {sorted(variants)}")

# Look for suffix variation
suffix_groups = defaultdict(list)
for m in prefix_forbidden:
    if len(m) >= 3:
        suffix_groups[m[-3:]].append(m)

variant_suffix_groups = {k: v for k, v in suffix_groups.items() if len(v) >= 3}

print(f"\nSuffix groups with 3+ variants (last 3 chars same):")
for suffix, variants in sorted(variant_suffix_groups.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"  '...{suffix}': {sorted(variants)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
