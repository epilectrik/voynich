#!/usr/bin/env python3
"""
CORRECT extraction with proper articulator handling.

Structure: [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]

Articulator is OPTIONAL and comes BEFORE prefix.
We should strip articulator first, THEN find prefix.
"""

import csv
from collections import Counter

# Known articulators (single chars that can precede prefix)
# From C291: yk-, yt-, kch- etc.
ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']

# Standard PREFIX list
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

def find_prefix(token):
    """Find prefix in token, returns (prefix, remainder) or (None, token)."""
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return p, token[len(p):]
    return None, token

def extract_correct(token):
    """
    Extract with correct articulator handling.

    1. Try to find prefix directly
    2. If not found, check if starts with articulator + prefix
    3. Strip suffix from remainder to get MIDDLE
    """
    if not token:
        return None, None, None, None

    articulator = None
    prefix = None

    # First try: find prefix directly
    prefix, remainder = find_prefix(token)

    # If no prefix found, check for articulator + prefix
    if prefix is None:
        for art in ARTICULATORS:
            if token.startswith(art) and len(token) > len(art):
                # Try to find prefix after articulator
                after_art = token[len(art):]
                maybe_prefix, maybe_remainder = find_prefix(after_art)
                if maybe_prefix is not None:
                    articulator = art
                    prefix = maybe_prefix
                    remainder = maybe_remainder
                    break

    # If still no prefix, token is truly prefix-less
    if prefix is None:
        remainder = token

    # Strip suffix
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    middle = remainder if remainder else None

    return articulator, prefix, middle, suffix


# ============================================================
# TEST ON CURRIER A
# ============================================================

results = {
    'has_prefix': 0,
    'has_art_prefix': 0,  # Has articulator + prefix
    'no_prefix': 0,
}

a_middles = Counter()
b_middles = Counter()

examples = {
    'has_prefix': [],
    'has_art_prefix': [],
    'no_prefix': [],
}

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        word = row.get('word', '').strip()
        lang = row.get('language', '').strip()
        if not word or '*' in word:
            continue

        art, prefix, middle, suffix = extract_correct(word)

        if middle:
            if lang == 'A':
                a_middles[middle] += 1

                if art and prefix:
                    results['has_art_prefix'] += 1
                    if len(examples['has_art_prefix']) < 10:
                        examples['has_art_prefix'].append((word, art, prefix, middle, suffix))
                elif prefix:
                    results['has_prefix'] += 1
                    if len(examples['has_prefix']) < 10:
                        examples['has_prefix'].append((word, art, prefix, middle, suffix))
                else:
                    results['no_prefix'] += 1
                    if len(examples['no_prefix']) < 10:
                        examples['no_prefix'].append((word, art, prefix, middle, suffix))

            elif lang == 'B':
                b_middles[middle] += 1

print("="*70)
print("CORRECT EXTRACTION WITH ARTICULATOR HANDLING")
print("="*70)

total_a = results['has_prefix'] + results['has_art_prefix'] + results['no_prefix']
print(f"\nCurrier A token breakdown:")
print(f"  Has PREFIX directly: {results['has_prefix']} ({100*results['has_prefix']/total_a:.1f}%)")
print(f"  Has ARTICULATOR + PREFIX: {results['has_art_prefix']} ({100*results['has_art_prefix']/total_a:.1f}%)")
print(f"  Truly prefix-less: {results['no_prefix']} ({100*results['no_prefix']/total_a:.1f}%)")

print(f"\nExamples - Has PREFIX directly:")
for word, art, prefix, middle, suffix in examples['has_prefix'][:5]:
    print(f"  {word} -> prefix={prefix}, middle={middle}, suffix={suffix}")

print(f"\nExamples - Has ARTICULATOR + PREFIX:")
for word, art, prefix, middle, suffix in examples['has_art_prefix'][:5]:
    print(f"  {word} -> art={art}, prefix={prefix}, middle={middle}, suffix={suffix}")

print(f"\nExamples - Truly prefix-less:")
for word, art, prefix, middle, suffix in examples['no_prefix'][:10]:
    print(f"  {word} -> middle={middle}, suffix={suffix}")

# ============================================================
# MIDDLE CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("MIDDLE CLASSIFICATION (CORRECT)")
print("="*70)

a_types = set(a_middles.keys())
b_types = set(b_middles.keys())

ri = a_types - b_types  # A-exclusive
pp = a_types & b_types  # Shared

print(f"\nUnique MIDDLE types:")
print(f"  Currier A: {len(a_types)}")
print(f"  Currier B: {len(b_types)}")
print(f"  RI (A-exclusive): {len(ri)}")
print(f"  PP (A-shared): {len(pp)}")

# By length
from collections import defaultdict
ri_by_len = defaultdict(set)
pp_by_len = defaultdict(set)
for m in ri:
    ri_by_len[len(m)].add(m)
for m in pp:
    pp_by_len[len(m)].add(m)

print(f"\n{'Length':<8} {'RI':<10} {'PP':<10}")
print("-" * 30)
for length in sorted(set(ri_by_len.keys()) | set(pp_by_len.keys())):
    print(f"{length:<8} {len(ri_by_len[length]):<10} {len(pp_by_len[length]):<10}")

# ============================================================
# COMPARE TO PREVIOUS
# ============================================================
print("\n" + "="*70)
print("COMPARISON TO PREVIOUS EXTRACTIONS")
print("="*70)

import json
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    v2_data = json.load(f)
v2_ri = set(v2_data['a_exclusive_middles'])
v2_pp = set(v2_data['a_shared_middles'])

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v1_backup.json') as f:
    v1_data = json.load(f)
v1_ri = set(v1_data['a_exclusive_middles'])
v1_pp = set(v1_data['a_shared_middles'])

print(f"\nv1 (PREFIX required, no articulator handling):")
print(f"  RI: {len(v1_ri)}, PP: {len(v1_pp)}")

print(f"\nv2 (PREFIX optional, no articulator handling):")
print(f"  RI: {len(v2_ri)}, PP: {len(v2_pp)}")

print(f"\nv3 CORRECT (articulator stripped, then PREFIX found):")
print(f"  RI: {len(ri)}, PP: {len(pp)}")

print(f"\nTruly prefix-less tokens: {results['no_prefix']} ({100*results['no_prefix']/total_a:.1f}%)")
