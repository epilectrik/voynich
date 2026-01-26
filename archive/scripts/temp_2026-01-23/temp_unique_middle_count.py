#!/usr/bin/env python3
"""
Check unique MIDDLE counts - why do we still have 600+ if MIDDLEs are short?

If 65% of tokens have single-letter MIDDLEs, and there are only ~20 letters,
shouldn't there be far fewer unique MIDDLE types?
"""

import csv
from collections import Counter, defaultdict

# Extended prefix list with articulators
ARTICULATOR_PREFIXES = ['ych', 'ysh', 'yda', 'yok', 'yke', 'yte', 'yto', 'yta', 'yko', 'yka', 'ytch', 'ykch', 'ypch']
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
                     'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                     'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']

ALL_PREFIXES = ARTICULATOR_PREFIXES + CORE_PREFIXES + EXTENDED_PREFIXES
ALL_PREFIXES = sorted(set(ALL_PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token, prefix_list):
    if not token:
        return None
    working = token
    for p in prefix_list:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None

# Collect all MIDDLEs
a_middles = Counter()
b_middles = Counter()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        word = row.get('word', '').strip()
        lang = row.get('language', '').strip()
        if not word or '*' in word:
            continue

        middle = extract_middle(word, ALL_PREFIXES)
        if middle:
            if lang == 'A':
                a_middles[middle] += 1
            elif lang == 'B':
                b_middles[middle] += 1

print("="*70)
print("UNIQUE MIDDLE COUNT ANALYSIS")
print("="*70)

# Unique types
a_types = set(a_middles.keys())
b_types = set(b_middles.keys())
a_only = a_types - b_types  # RI
a_shared = a_types & b_types  # PP

print(f"\nCurrier A unique MIDDLE types: {len(a_types)}")
print(f"Currier B unique MIDDLE types: {len(b_types)}")
print(f"A-exclusive (RI): {len(a_only)}")
print(f"A-shared (PP): {len(a_shared)}")

# ============================================================
# BY LENGTH
# ============================================================
print("\n" + "="*70)
print("UNIQUE MIDDLE TYPES BY LENGTH")
print("="*70)

a_by_len = defaultdict(set)
for m in a_types:
    a_by_len[len(m)].add(m)

ri_by_len = defaultdict(set)
for m in a_only:
    ri_by_len[len(m)].add(m)

pp_by_len = defaultdict(set)
for m in a_shared:
    pp_by_len[len(m)].add(m)

print(f"\n{'Length':<8} {'A types':<12} {'RI':<12} {'PP':<12}")
print("-" * 50)
for length in sorted(a_by_len.keys()):
    a_cnt = len(a_by_len[length])
    ri_cnt = len(ri_by_len[length])
    pp_cnt = len(pp_by_len[length])
    print(f"{length:<8} {a_cnt:<12} {ri_cnt:<12} {pp_cnt:<12}")

# ============================================================
# SINGLE LETTER MIDDLES
# ============================================================
print("\n" + "="*70)
print("SINGLE-LETTER MIDDLES IN DETAIL")
print("="*70)

single_a = a_by_len[1]
single_ri = ri_by_len[1]
single_pp = pp_by_len[1]

print(f"\nSingle-letter MIDDLEs in A: {len(single_a)}")
print(f"  Types: {sorted(single_a)}")
print(f"\nSingle-letter RI: {len(single_ri)}")
print(f"  Types: {sorted(single_ri)}")
print(f"\nSingle-letter PP: {len(single_pp)}")
print(f"  Types: {sorted(single_pp)}")

# ============================================================
# TOKEN DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("TOKEN COUNT BY MIDDLE LENGTH (A only)")
print("="*70)

tokens_by_len = defaultdict(int)
for m, cnt in a_middles.items():
    tokens_by_len[len(m)] += cnt

total_a_tokens = sum(a_middles.values())
print(f"\nTotal A tokens with MIDDLE: {total_a_tokens}")
print(f"\n{'Length':<8} {'Tokens':<12} {'%':<10} {'Unique types':<15}")
print("-" * 50)
for length in sorted(tokens_by_len.keys()):
    tok_cnt = tokens_by_len[length]
    pct = 100 * tok_cnt / total_a_tokens
    type_cnt = len(a_by_len[length])
    print(f"{length:<8} {tok_cnt:<12} {pct:>6.1f}%    {type_cnt:<15}")

# ============================================================
# THE KEY QUESTION: Where do the 600 RI come from?
# ============================================================
print("\n" + "="*70)
print("WHERE DO 600 RI MIDDLES COME FROM?")
print("="*70)

print(f"""
Single-letter RI: {len(single_ri)}
Multi-letter RI: {len(a_only) - len(single_ri)}
Total RI: {len(a_only)}

The majority of RI MIDDLEs are multi-letter strings that:
1. Appear in A but not in B
2. Are extracted after stripping prefix and suffix
""")

# Show some examples of multi-letter RI
multi_ri = [m for m in a_only if len(m) > 1]
print(f"\nExample multi-letter RI MIDDLEs (first 30):")
for m in sorted(multi_ri)[:30]:
    cnt = a_middles[m]
    print(f"  '{m}' ({cnt} tokens)")

# ============================================================
# COMPARE TO OLD EXTRACTION
# ============================================================
print("\n" + "="*70)
print("COMPARISON TO ORIGINAL middle_classes.json")
print("="*70)

import json
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    old_data = json.load(f)

old_ri = set(old_data['a_exclusive_middles'])
old_pp = set(old_data['a_shared_middles'])

print(f"\nOld extraction:")
print(f"  RI: {len(old_ri)}")
print(f"  PP: {len(old_pp)}")

print(f"\nNew extraction:")
print(f"  RI: {len(a_only)}")
print(f"  PP: {len(a_shared)}")

# What's the overlap?
ri_still_ri = old_ri & a_only
ri_now_pp = old_ri & a_shared
ri_gone = old_ri - a_only - a_shared

print(f"\nOld RI MIDDLEs:")
print(f"  Still RI: {len(ri_still_ri)}")
print(f"  Now PP: {len(ri_now_pp)}")
print(f"  Gone (not extracted): {len(ri_gone)}")

# New RI that weren't in old
new_ri = a_only - old_ri - old_pp
print(f"\nNew RI not in old extraction: {len(new_ri)}")
if new_ri:
    print(f"  Examples: {sorted(new_ri)[:15]}")
