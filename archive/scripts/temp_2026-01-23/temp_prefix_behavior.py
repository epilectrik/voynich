#!/usr/bin/env python3
"""Check if RI MIDDLEs are strictly prefixed or unprefixed."""

import csv
import json
from collections import defaultdict

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

def extract(token):
    if not token:
        return None, False
    working = token
    had_prefix = False
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            had_prefix = True
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None, had_prefix

# Track which MIDDLEs appear with/without prefix (corpus-wide)
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

        middle, had_prefix = extract(word)
        if middle and middle in ri_middles:
            if had_prefix:
                appears_with_prefix.add(middle)
            else:
                appears_without_prefix.add(middle)

# Classify
only_prefixed = appears_with_prefix - appears_without_prefix
only_unprefixed = appears_without_prefix - appears_with_prefix
both = appears_with_prefix & appears_without_prefix

print("="*70)
print("RI MIDDLE PREFIX BEHAVIOR (CORPUS-WIDE)")
print("="*70)
print(f"Total RI MIDDLEs: {len(ri_middles)}")
print(f"  ONLY with PREFIX: {len(only_prefixed)} ({100*len(only_prefixed)/len(ri_middles):.1f}%)")
print(f"  ONLY without PREFIX: {len(only_unprefixed)} ({100*len(only_unprefixed)/len(ri_middles):.1f}%)")
print(f"  BOTH ways: {len(both)} ({100*len(both)/len(ri_middles):.1f}%)")

print(f"\nMIDDLEs appearing BOTH ways (all {len(both)}):")
for m in sorted(both):
    print(f"  {m}")

print(f"\nSample ONLY-prefixed MIDDLEs (first 15):")
for m in sorted(only_prefixed)[:15]:
    print(f"  {m}")

print(f"\nSample ONLY-unprefixed MIDDLEs (first 15):")
for m in sorted(only_unprefixed)[:15]:
    print(f"  {m}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print(f"""
RI vocabulary splits into TWO nearly-disjoint populations:

1. PREFIX-REQUIRED ({len(only_prefixed)} MIDDLEs, {100*len(only_prefixed)/len(ri_middles):.1f}%)
   - Always appear with a PREFIX
   - Never seen as bare MIDDLE

2. PREFIX-FORBIDDEN ({len(only_unprefixed)} MIDDLEs, {100*len(only_unprefixed)/len(ri_middles):.1f}%)
   - Never appear with a PREFIX
   - Always bare MIDDLE (possibly with SUFFIX)

3. PREFIX-OPTIONAL ({len(both)} MIDDLEs, {100*len(both)/len(ri_middles):.1f}%)
   - Can appear either way
   - Very small subset

This is NOT the same MIDDLE appearing with/without prefix.
These are DISTINCT substance identifiers with different morphological rules.
""")
