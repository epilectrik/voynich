#!/usr/bin/env python3
"""
Verify RI MIDDLE counts - where do 349 vs 173 vs 176 come from?
"""

import json
import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load the middle_classes.json
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)

ri_defined = set(data['a_exclusive_middles'])
pp_defined = set(data['a_shared_middles'])

print("="*60)
print("FROM middle_classes.json:")
print("="*60)
print(f"  RI (a_exclusive_middles): {len(ri_defined)}")
print(f"  PP (a_shared_middles): {len(pp_defined)}")

# Now extract MIDDLEs from actual transcript and see what appears
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    """Extract MIDDLE by stripping PREFIX and SUFFIX."""
    if not token:
        return None

    # Strip prefix
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break

    # Strip suffix
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break

    return token if token else None

def extract_middle_no_suffix(token):
    """Extract just PREFIX-stripped (what C499 did)."""
    if not token:
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# Collect MIDDLEs from Currier A
a_middles_full = Counter()  # PREFIX-stripped only (MIDDLE+SUFFIX)
a_middles_core = Counter()  # Full extraction (MIDDLE only)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        middle_full = extract_middle_no_suffix(word)
        middle_core = extract_middle(word)

        if middle_full and len(middle_full) > 0:
            a_middles_full[middle_full] += 1
        if middle_core and len(middle_core) > 0:
            a_middles_core[middle_core] += 1

print(f"\n" + "="*60)
print("FROM ACTUAL TRANSCRIPT (Currier A, H-track):")
print("="*60)
print(f"  Unique MIDDLE+SUFFIX (PREFIX-stripped): {len(a_middles_full)}")
print(f"  Unique MIDDLE cores (full extraction): {len(a_middles_core)}")

# Cross-reference with RI defined
ri_found_full = set(a_middles_full.keys()) & ri_defined
ri_found_core = set(a_middles_core.keys()) & ri_defined

print(f"\n" + "="*60)
print("CROSS-REFERENCE WITH middle_classes.json:")
print("="*60)
print(f"  RI defined that appear in A (MIDDLE+SUFFIX match): {len(ri_found_full)}")
print(f"  RI defined that appear in A (MIDDLE core match): {len(ri_found_core)}")

# What about the 176 number?
# Maybe it's the number of RI that appear ONLY in A (truly A-exclusive from transcript)

# Collect B MIDDLEs
b_middles_full = set()
b_middles_core = set()

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'B':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        middle_full = extract_middle_no_suffix(word)
        middle_core = extract_middle(word)

        if middle_full:
            b_middles_full.add(middle_full)
        if middle_core:
            b_middles_core.add(middle_core)

# Compute A-exclusive from transcript
a_exclusive_full = set(a_middles_full.keys()) - b_middles_full
a_exclusive_core = set(a_middles_core.keys()) - b_middles_core

print(f"\n" + "="*60)
print("DERIVED FROM TRANSCRIPT (A-exclusive = in A, not in B):")
print("="*60)
print(f"  A-exclusive MIDDLE+SUFFIX: {len(a_exclusive_full)}")
print(f"  A-exclusive MIDDLE cores: {len(a_exclusive_core)}")

# Show what's in middle_classes.json that doesn't match
print(f"\n" + "="*60)
print("SAMPLES OF RI DEFINED:")
print("="*60)
print(f"First 20: {sorted(ri_defined)[:20]}")

print(f"\n" + "="*60)
print("SAMPLES OF A-EXCLUSIVE FROM TRANSCRIPT:")
print("="*60)
print(f"First 20: {sorted(a_exclusive_core)[:20]}")
