#!/usr/bin/env python3
"""
When a localized RI appears on 1-2 folios, is it:
1. IDENTICAL each time (same full word)?
2. VARIANT (same MIDDLE but different PREFIX/SUFFIX)?
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_parts(token):
    """Extract prefix, middle, suffix from token."""
    if not token or not isinstance(token, str):
        return None, None, None

    original = token
    prefix = None
    suffix = None

    # Extract prefix
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    # Extract suffix
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    middle = token if token else None
    return prefix, middle, suffix

# Collect all words with localized RI
ri_to_words = defaultdict(list)
ri_to_folios = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        folio = row.get('folio', '').strip()
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if middle and middle in ri_middles:
            ri_to_words[middle].append({
                'word': word,
                'prefix': prefix,
                'suffix': suffix,
                'folio': folio
            })
            ri_to_folios[middle].add(folio)

# Focus on localized RI (1-2 folios)
localized_ri = [ri for ri, folios in ri_to_folios.items() if len(folios) <= 2]

print("="*70)
print("LOCALIZED RI: IDENTICAL OR VARIANT?")
print("="*70)

identical_count = 0
variant_count = 0
examples_identical = []
examples_variant = []

for ri in localized_ri:
    words = ri_to_words[ri]
    if len(words) < 2:
        continue  # Need at least 2 occurrences to compare

    unique_words = set(w['word'] for w in words)
    unique_prefixes = set(w['prefix'] for w in words)
    unique_suffixes = set(w['suffix'] for w in words)

    if len(unique_words) == 1:
        identical_count += 1
        if len(examples_identical) < 10:
            examples_identical.append({
                'ri': ri,
                'word': list(unique_words)[0],
                'count': len(words),
                'folios': list(ri_to_folios[ri])
            })
    else:
        variant_count += 1
        if len(examples_variant) < 15:
            examples_variant.append({
                'ri': ri,
                'words': list(unique_words),
                'prefixes': list(unique_prefixes),
                'suffixes': list(unique_suffixes),
                'count': len(words),
                'folios': list(ri_to_folios[ri])
            })

print(f"\nLocalized RI with 2+ occurrences: {identical_count + variant_count}")
print(f"  IDENTICAL (same word each time): {identical_count} ({100*identical_count/(identical_count+variant_count):.0f}%)")
print(f"  VARIANT (different words, same MIDDLE): {variant_count} ({100*variant_count/(identical_count+variant_count):.0f}%)")

print("\n" + "="*70)
print("EXAMPLES: IDENTICAL RI")
print("="*70)

for ex in examples_identical:
    print(f"\n  RI '{ex['ri']}' on {ex['folios']}:")
    print(f"    Always appears as: {ex['word']} ({ex['count']} times)")

print("\n" + "="*70)
print("EXAMPLES: VARIANT RI")
print("="*70)

for ex in examples_variant:
    print(f"\n  RI '{ex['ri']}' on {ex['folios']}:")
    print(f"    Appears as: {ex['words']}")
    print(f"    Prefixes used: {ex['prefixes']}")
    print(f"    Suffixes used: {ex['suffixes']}")

# Analyze the variation patterns
print("\n" + "="*70)
print("VARIATION ANALYSIS")
print("="*70)

# For variants, what changes: prefix, suffix, or both?
prefix_only = 0
suffix_only = 0
both_change = 0

for ri in localized_ri:
    words = ri_to_words[ri]
    if len(words) < 2:
        continue

    unique_words = set(w['word'] for w in words)
    if len(unique_words) == 1:
        continue

    unique_prefixes = set(w['prefix'] for w in words)
    unique_suffixes = set(w['suffix'] for w in words)

    prefix_varies = len(unique_prefixes) > 1
    suffix_varies = len(unique_suffixes) > 1

    if prefix_varies and suffix_varies:
        both_change += 1
    elif prefix_varies:
        prefix_only += 1
    elif suffix_varies:
        suffix_only += 1

print(f"\nAmong variant RI:")
print(f"  Only PREFIX changes: {prefix_only}")
print(f"  Only SUFFIX changes: {suffix_only}")
print(f"  BOTH change: {both_change}")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If localized RI appear with VARIANTS (same MIDDLE, different PREFIX/SUFFIX):
  - The MIDDLE identifies the material (constant)
  - PREFIX/SUFFIX encode something else (variable)
    - PREFIX might encode: position, quantity, grammatical role
    - SUFFIX might encode: state, inflection, modification

This would be like:
  - "the rose" vs "a rose" vs "roses" (same base, different grammar)
  - Or: "rose root" vs "rose flower" (same plant, different part)

If localized RI appear IDENTICALLY:
  - The whole word is a fixed identifier
  - No grammatical variation
  - More like a label or code
""")
