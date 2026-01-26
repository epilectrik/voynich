#!/usr/bin/env python3
"""Check SUFFIX behavior of PREFIX-FORBIDDEN RI tokens."""

import csv
import json
from collections import Counter

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_full(token):
    if not token:
        return None, None, None
    working = token
    prefix = None
    suffix = None
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break
    return prefix, working if working else None, suffix

# Track which MIDDLEs appear with/without prefix
appears_with_prefix = set()
appears_without_prefix = set()

# Track suffix behavior by prefix status
prefixed_tokens = {'with_suffix': 0, 'without_suffix': 0}
unprefixed_tokens = {'with_suffix': 0, 'without_suffix': 0}

prefixed_suffix_types = Counter()
unprefixed_suffix_types = Counter()

# Also track by MIDDLE class
middle_suffix_behavior = {}  # middle -> {'prefixed': has_suffix_list, 'unprefixed': has_suffix_list}

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

        prefix, middle, suffix = extract_full(word)
        if middle and middle in ri_middles:
            if prefix:
                appears_with_prefix.add(middle)
                if suffix:
                    prefixed_tokens['with_suffix'] += 1
                    prefixed_suffix_types[suffix] += 1
                else:
                    prefixed_tokens['without_suffix'] += 1
            else:
                appears_without_prefix.add(middle)
                if suffix:
                    unprefixed_tokens['with_suffix'] += 1
                    unprefixed_suffix_types[suffix] += 1
                else:
                    unprefixed_tokens['without_suffix'] += 1

# Classify
prefix_required = appears_with_prefix - appears_without_prefix
prefix_forbidden = appears_without_prefix - appears_with_prefix

print("="*70)
print("SUFFIX BEHAVIOR BY PREFIX STATUS")
print("="*70)

# Prefixed tokens
total_prefixed = prefixed_tokens['with_suffix'] + prefixed_tokens['without_suffix']
print(f"\nPREFIXED RI tokens ({total_prefixed} total):")
print(f"  With SUFFIX: {prefixed_tokens['with_suffix']} ({100*prefixed_tokens['with_suffix']/total_prefixed:.1f}%)")
print(f"  Bare (no SUFFIX): {prefixed_tokens['without_suffix']} ({100*prefixed_tokens['without_suffix']/total_prefixed:.1f}%)")

# Unprefixed tokens
total_unprefixed = unprefixed_tokens['with_suffix'] + unprefixed_tokens['without_suffix']
print(f"\nUNPREFIXED RI tokens ({total_unprefixed} total):")
print(f"  With SUFFIX: {unprefixed_tokens['with_suffix']} ({100*unprefixed_tokens['with_suffix']/total_unprefixed:.1f}%)")
print(f"  Bare MIDDLE only: {unprefixed_tokens['without_suffix']} ({100*unprefixed_tokens['without_suffix']/total_unprefixed:.1f}%)")

print("\n" + "="*70)
print("TOP SUFFIXES BY PREFIX STATUS")
print("="*70)

print("\nOn PREFIXED RI tokens:")
for suf, cnt in prefixed_suffix_types.most_common(10):
    print(f"  -{suf}: {cnt}")

print("\nOn UNPREFIXED RI tokens:")
for suf, cnt in unprefixed_suffix_types.most_common(10):
    print(f"  -{suf}: {cnt}")

# Compare suffix repertoires
print("\n" + "="*70)
print("SUFFIX REPERTOIRE COMPARISON")
print("="*70)

prefixed_suffs = set(prefixed_suffix_types.keys())
unprefixed_suffs = set(unprefixed_suffix_types.keys())

shared = prefixed_suffs & unprefixed_suffs
prefixed_only = prefixed_suffs - unprefixed_suffs
unprefixed_only = unprefixed_suffs - prefixed_suffs

print(f"\nSuffixes used in BOTH: {len(shared)}")
print(f"  {sorted(shared)[:15]}...")
print(f"\nSuffixes ONLY on prefixed: {len(prefixed_only)}")
print(f"  {sorted(prefixed_only)}")
print(f"\nSuffixes ONLY on unprefixed: {len(unprefixed_only)}")
print(f"  {sorted(unprefixed_only)}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print(f"""
PREFIX-FORBIDDEN tokens:
  - {100*unprefixed_tokens['with_suffix']/total_unprefixed:.1f}% have SUFFIX
  - {100*unprefixed_tokens['without_suffix']/total_unprefixed:.1f}% are bare MIDDLE only

Compare to PREFIXED tokens:
  - {100*prefixed_tokens['with_suffix']/total_prefixed:.1f}% have SUFFIX
  - {100*prefixed_tokens['without_suffix']/total_prefixed:.1f}% have no SUFFIX
""")
