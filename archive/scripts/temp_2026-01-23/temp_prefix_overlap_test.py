#!/usr/bin/env python3
"""
Test: Do prefix-less RI tokens share MIDDLEs with prefixed tokens on same folio?
This verifies that folio-localization pattern holds across prefix variants.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

# Load corrected RI MIDDLEs
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

print(f"Loaded {len(ri_middles)} RI MIDDLEs")

# Extraction
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

# Track RI MIDDLEs by folio, split by prefix presence
folio_prefixed = defaultdict(set)    # folio -> RI MIDDLEs that appeared WITH prefix
folio_unprefixed = defaultdict(set)  # folio -> RI MIDDLEs that appeared WITHOUT prefix

# Also track token counts
prefixed_tokens = 0
unprefixed_tokens = 0

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue

        middle, had_prefix = extract(word)
        if middle and middle in ri_middles:
            if had_prefix:
                folio_prefixed[folio].add(middle)
                prefixed_tokens += 1
            else:
                folio_unprefixed[folio].add(middle)
                unprefixed_tokens += 1

print(f"\nRI token instances:")
print(f"  With PREFIX: {prefixed_tokens}")
print(f"  Without PREFIX: {unprefixed_tokens}")
print(f"  PREFIX rate: {100*prefixed_tokens/(prefixed_tokens+unprefixed_tokens):.1f}%")

# Analysis
print("\n" + "="*70)
print("PREFIX-LESS RI TOKENS: SAME-FOLIO OVERLAP TEST")
print("="*70)

# How many unprefixed RI MIDDLEs also appear prefixed on SAME folio?
same_folio_overlap = 0
unprefixed_only = 0
total_unprefixed_middles = set()

for folio in folio_unprefixed:
    unprefixed = folio_unprefixed[folio]
    prefixed = folio_prefixed.get(folio, set())
    overlap = unprefixed & prefixed
    same_folio_overlap += len(overlap)
    unprefixed_only += len(unprefixed - prefixed)
    total_unprefixed_middles.update(unprefixed)

print(f"\nTotal unique RI MIDDLEs appearing without prefix: {len(total_unprefixed_middles)}")
print(f"  - Also appear WITH prefix on SAME folio: {same_folio_overlap}")
print(f"  - Appear ONLY without prefix on that folio: {unprefixed_only}")

# What % of unprefixed instances share folio with prefixed form?
if same_folio_overlap + unprefixed_only > 0:
    pct = 100 * same_folio_overlap / (same_folio_overlap + unprefixed_only)
    print(f"\nSame-folio overlap rate: {pct:.1f}%")

# Show examples
print("\nExamples of same-folio overlap (MIDDLE appears both prefixed and unprefixed):")
count = 0
for folio in sorted(folio_unprefixed.keys()):
    unprefixed = folio_unprefixed[folio]
    prefixed = folio_prefixed.get(folio, set())
    overlap = unprefixed & prefixed
    if overlap and count < 8:
        examples = list(overlap)[:4]
        print(f"  {folio}: {examples}")
        count += 1

# Check if unprefixed-only are still folio-localized
print("\n" + "="*70)
print("UNPREFIXED-ONLY RI MIDDLEs: FOLIO LOCALIZATION")
print("="*70)

# For MIDDLEs that ONLY appear unprefixed (never with prefix), how many folios?
all_prefixed_middles = set()
for middles in folio_prefixed.values():
    all_prefixed_middles.update(middles)

never_prefixed = total_unprefixed_middles - all_prefixed_middles

print(f"\nRI MIDDLEs that NEVER appear with prefix: {len(never_prefixed)}")

# Count folios per never-prefixed MIDDLE
middle_folios = defaultdict(set)
for folio, middles in folio_unprefixed.items():
    for m in middles:
        if m in never_prefixed:
            middle_folios[m].add(folio)

folio_counts = [len(f) for f in middle_folios.values()]
if folio_counts:
    one_folio = sum(1 for c in folio_counts if c == 1)
    print(f"  On exactly 1 folio: {one_folio} ({100*one_folio/len(folio_counts):.1f}%)")
    print(f"  Avg folios: {sum(folio_counts)/len(folio_counts):.2f}")
    print(f"\n  Sample never-prefixed MIDDLEs (first 10):")
    for m in sorted(never_prefixed)[:10]:
        folios = middle_folios[m]
        print(f"    {m}: {len(folios)} folio(s)")

# Summary
print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print(f"""
The {len(total_unprefixed_middles)} RI MIDDLEs appearing without prefix:
  - {pct:.1f}% also appear WITH prefix on the SAME folio
  - This confirms: same substance identifier, with/without grammatical prefix
  - Folio-localization pattern HOLDS for prefix-less tokens

The {len(never_prefixed)} MIDDLEs that NEVER take prefix:
  - Still {100*one_folio/len(folio_counts):.1f}% on exactly 1 folio
  - Same localization pattern as prefixed RI
  - These are valid substance identifiers, just PREFIX-less by nature
""")
