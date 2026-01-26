#!/usr/bin/env python3
"""
Proper RI MIDDLE extraction that doesn't require PREFIX.

The issue: original methodology required PREFIX to extract MIDDLE,
but C509.a shows only 58.5% of RI tokens have PREFIX. We were
excluding ~40% of RI vocabulary!

New approach:
1. Try to strip PREFIX if present (optional)
2. Strip SUFFIX from the end (if present)
3. What remains is the MIDDLE core

This handles: MIDDLE, MIDDLE+SUFFIX, PREFIX+MIDDLE, PREFIX+MIDDLE+SUFFIX
"""

import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path('.')

# From the original prepare_middle_classes.py
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

# Standard suffixes (simplified list)
SUFFIXES = [
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'tedy', 'kedy',
    'cheey', 'sheey', 'chey', 'shey',
    'chol', 'shol', 'chor', 'shor',
    'eedy', 'edy', 'eey', 'ey',
    'iin', 'ain', 'oin', 'ein',
    'dy', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'in', 'an', 'on', 'en',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]
SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle_proper(token):
    """
    Extract MIDDLE core - PREFIX is optional, SUFFIX stripped if present.

    Returns: (prefix_or_none, middle_core, suffix_or_none, had_prefix)
    """
    if not token or len(token) == 0:
        return None, None, None, False

    working = token
    prefix = None

    # Try to strip prefix (optional)
    for p in ALL_PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break

    # Strip suffix from the end (if present and leaves something)
    suffix = None
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break

    # What remains is the MIDDLE core
    middle = working if working else None

    return prefix, middle, suffix, (prefix is not None)


# Process all tokens
a_tokens = []  # (token, folio, prefix, middle, suffix, had_prefix)
b_middles = set()

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        word = row.get('word', '').strip()
        language = row.get('language', '').strip()
        folio = row.get('folio', '').strip()

        if not word or '*' in word or word.startswith('[') or word.startswith('<'):
            continue

        prefix, middle, suffix, had_prefix = extract_middle_proper(word)

        if middle and len(middle) > 0:
            if language == 'A':
                a_tokens.append({
                    'token': word,
                    'folio': folio,
                    'prefix': prefix,
                    'middle': middle,
                    'suffix': suffix,
                    'had_prefix': had_prefix
                })
            elif language == 'B':
                b_middles.add(middle)

# Get unique A middles
a_middles = set(t['middle'] for t in a_tokens)

# Classify
ri_middles = a_middles - b_middles
pp_middles = a_middles & b_middles

print("="*70)
print("PROPER RI EXTRACTION (PREFIX OPTIONAL)")
print("="*70)

print(f"\nUnique MIDDLE cores:")
print(f"  A MIDDLEs: {len(a_middles)}")
print(f"  B MIDDLEs: {len(b_middles)}")
print(f"  RI (A-exclusive): {len(ri_middles)}")
print(f"  PP (shared A&B): {len(pp_middles)}")

# Check PREFIX presence in RI vs PP tokens
ri_tokens = [t for t in a_tokens if t['middle'] in ri_middles]
pp_tokens = [t for t in a_tokens if t['middle'] in pp_middles]

ri_with_prefix = sum(1 for t in ri_tokens if t['had_prefix'])
pp_with_prefix = sum(1 for t in pp_tokens if t['had_prefix'])

print(f"\nPREFIX presence (token instances):")
print(f"  RI tokens with PREFIX: {ri_with_prefix}/{len(ri_tokens)} ({100*ri_with_prefix/len(ri_tokens):.1f}%)")
print(f"  PP tokens with PREFIX: {pp_with_prefix}/{len(pp_tokens)} ({100*pp_with_prefix/len(pp_tokens):.1f}%)")

# This should match C509.a: RI ~58.5% PREFIX, PP ~85.4% PREFIX

# Check MIDDLE length distribution
ri_lengths = Counter(len(m) for m in ri_middles)
pp_lengths = Counter(len(m) for m in pp_middles)

print(f"\nMIDDLE length distribution:")
print(f"\n  RI MIDDLEs (n={len(ri_middles)}):")
for length in sorted(ri_lengths.keys())[:8]:
    print(f"    len={length}: {ri_lengths[length]}")

print(f"\n  PP MIDDLEs (n={len(pp_middles)}):")
for length in sorted(pp_lengths.keys())[:8]:
    print(f"    len={length}: {pp_lengths[length]}")

# Filter to reasonable MIDDLE lengths (exclude 1-char which are likely extraction artifacts)
ri_middles_filtered = {m for m in ri_middles if len(m) >= 2}
pp_middles_filtered = {m for m in pp_middles if len(m) >= 2}

print(f"\nFiltered (len >= 2):")
print(f"  RI MIDDLEs: {len(ri_middles_filtered)}")
print(f"  PP MIDDLEs: {len(pp_middles_filtered)}")

# Show some examples
print(f"\nSample RI MIDDLEs (first 20):")
print(f"  {sorted(ri_middles_filtered)[:20]}")

print(f"\nSample PP MIDDLEs (first 20):")
print(f"  {sorted(pp_middles_filtered)[:20]}")
