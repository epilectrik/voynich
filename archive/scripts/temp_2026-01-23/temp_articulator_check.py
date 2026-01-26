#!/usr/bin/env python3
"""
Check articulator patterns and their impact on PREFIX-FORBIDDEN classification.

The ARTICULATOR layer (C291-C294) includes forms like yk-, yt-, kch-, etc.
These are OPTIONAL, section-concentrated, and purely expressive.

Our current PREFIX list may be incomplete, causing ARTICULATOR+PREFIX
combinations to be misclassified as PREFIX-FORBIDDEN.
"""

import csv
import json
from collections import Counter, defaultdict

# Current PREFIX list (from our scripts)
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
                     'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                     'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']

CURRENT_PREFIXES = CORE_PREFIXES + EXTENDED_PREFIXES
CURRENT_PREFIXES = sorted(set(CURRENT_PREFIXES), key=len, reverse=True)

# Known articulators from C291
KNOWN_ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']

# Load RI middles
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

def has_prefix(token, prefix_list):
    for p in prefix_list:
        if token.startswith(p) and len(token) > len(p):
            return p
    return None

# Collect all Currier A tokens
all_tokens = []
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
        all_tokens.append(word)

print("="*70)
print("ARTICULATOR PATTERN ANALYSIS")
print("="*70)
print(f"\nTotal Currier A tokens: {len(all_tokens)}")

# ============================================================
# 1. FIND TOKENS THAT START WITH ARTICULATOR + CORE PREFIX
# ============================================================
print("\n" + "="*70)
print("1. ARTICULATOR + CORE PREFIX PATTERNS")
print("="*70)

articulator_patterns = Counter()
articulator_examples = defaultdict(list)

for token in all_tokens:
    # Check if starts with articulator + core prefix
    for art in KNOWN_ARTICULATORS:
        if token.startswith(art) and len(token) > len(art):
            rest = token[len(art):]
            for core in CORE_PREFIXES:
                if rest.startswith(core):
                    pattern = art + core
                    articulator_patterns[pattern] += 1
                    if len(articulator_examples[pattern]) < 5:
                        articulator_examples[pattern].append(token)
                    break

print(f"\nArticulator+CorePrefix patterns found:")
for pattern, cnt in sorted(articulator_patterns.items(), key=lambda x: -x[1]):
    if cnt >= 5:
        examples = articulator_examples[pattern][:3]
        print(f"  {pattern}: {cnt} tokens - e.g., {examples}")

# ============================================================
# 2. CHECK Y- SPECIFICALLY
# ============================================================
print("\n" + "="*70)
print("2. Y- ARTICULATOR PATTERNS")
print("="*70)

y_patterns = Counter()
y_examples = defaultdict(list)

for token in all_tokens:
    if token.startswith('y') and len(token) > 1:
        rest = token[1:]
        # Check for any known prefix after y
        found = False
        for p in CURRENT_PREFIXES:
            if rest.startswith(p):
                pattern = 'y' + p
                y_patterns[pattern] += 1
                if len(y_examples[pattern]) < 5:
                    y_examples[pattern].append(token)
                found = True
                break
        if not found:
            y_patterns['y+???'] += 1
            if len(y_examples['y+???']) < 10:
                y_examples['y+???'].append(token)

print(f"\nY- followed by known prefix:")
for pattern, cnt in sorted(y_patterns.items(), key=lambda x: -x[1]):
    if cnt >= 3 and pattern != 'y+???':
        examples = y_examples[pattern][:3]
        print(f"  {pattern}: {cnt} tokens - e.g., {examples}")

print(f"\nY- NOT followed by known prefix: {y_patterns.get('y+???', 0)}")
print(f"  Examples: {y_examples.get('y+???', [])[:10]}")

# ============================================================
# 3. BUILD EXTENDED PREFIX LIST WITH ARTICULATORS
# ============================================================
print("\n" + "="*70)
print("3. PROPOSED EXTENDED PREFIX LIST")
print("="*70)

# Articulator + core prefix combinations that appear 10+ times
significant_art_prefixes = []
for pattern, cnt in articulator_patterns.items():
    if cnt >= 10:
        significant_art_prefixes.append(pattern)

# Y-prefix combinations that appear 10+ times
for pattern, cnt in y_patterns.items():
    if cnt >= 10 and pattern != 'y+???':
        if pattern not in significant_art_prefixes:
            significant_art_prefixes.append(pattern)

print(f"\nSignificant articulator+prefix combinations (10+ tokens):")
for p in sorted(significant_art_prefixes):
    total = articulator_patterns.get(p, 0) + y_patterns.get(p, 0)
    print(f"  {p}: {total}")

# ============================================================
# 4. RECLASSIFY WITH EXTENDED PREFIX LIST
# ============================================================
print("\n" + "="*70)
print("4. RECLASSIFICATION IMPACT")
print("="*70)

# Create extended prefix list
EXTENDED_PREFIX_LIST = CURRENT_PREFIXES + significant_art_prefixes
EXTENDED_PREFIX_LIST = sorted(set(EXTENDED_PREFIX_LIST), key=len, reverse=True)

# Count how many previously PREFIX-FORBIDDEN now have prefix
old_no_prefix = 0
new_has_prefix = 0
still_no_prefix = 0

for token in all_tokens:
    old_prefix = has_prefix(token, CURRENT_PREFIXES)
    new_prefix = has_prefix(token, EXTENDED_PREFIX_LIST)

    if old_prefix is None:
        old_no_prefix += 1
        if new_prefix is not None:
            new_has_prefix += 1
        else:
            still_no_prefix += 1

print(f"\nTokens without prefix (old list): {old_no_prefix}")
print(f"Now have prefix (extended list): {new_has_prefix}")
print(f"Still without prefix: {still_no_prefix}")
print(f"Reclassification rate: {100*new_has_prefix/old_no_prefix:.1f}%")

# ============================================================
# 5. IMPACT ON RI MIDDLE CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("5. IMPACT ON RI MIDDLE CLASSIFICATION")
print("="*70)

# Re-classify RI MIDDLEs with extended prefix list
old_appears_with_prefix = set()
old_appears_without_prefix = set()
new_appears_with_prefix = set()
new_appears_without_prefix = set()

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token, prefix_list):
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

for token in all_tokens:
    old_prefix = has_prefix(token, CURRENT_PREFIXES)
    new_prefix = has_prefix(token, EXTENDED_PREFIX_LIST)

    old_middle = extract_middle(token, CURRENT_PREFIXES)
    new_middle = extract_middle(token, EXTENDED_PREFIX_LIST)

    if old_middle and old_middle in ri_middles:
        if old_prefix:
            old_appears_with_prefix.add(old_middle)
        else:
            old_appears_without_prefix.add(old_middle)

    if new_middle and new_middle in ri_middles:
        if new_prefix:
            new_appears_with_prefix.add(new_middle)
        else:
            new_appears_without_prefix.add(new_middle)

old_prefix_required = old_appears_with_prefix - old_appears_without_prefix
old_prefix_forbidden = old_appears_without_prefix - old_appears_with_prefix

new_prefix_required = new_appears_with_prefix - new_appears_without_prefix
new_prefix_forbidden = new_appears_without_prefix - new_appears_with_prefix

print(f"\nOLD classification (current prefix list):")
print(f"  PREFIX-REQUIRED: {len(old_prefix_required)}")
print(f"  PREFIX-FORBIDDEN: {len(old_prefix_forbidden)}")

print(f"\nNEW classification (extended prefix list):")
print(f"  PREFIX-REQUIRED: {len(new_prefix_required)}")
print(f"  PREFIX-FORBIDDEN: {len(new_prefix_forbidden)}")

print(f"\nChange:")
print(f"  PREFIX-REQUIRED: {len(old_prefix_required)} -> {len(new_prefix_required)} ({len(new_prefix_required) - len(old_prefix_required):+d})")
print(f"  PREFIX-FORBIDDEN: {len(old_prefix_forbidden)} -> {len(new_prefix_forbidden)} ({len(new_prefix_forbidden) - len(old_prefix_forbidden):+d})")

# ============================================================
# 6. WHAT'S STILL PREFIX-FORBIDDEN?
# ============================================================
print("\n" + "="*70)
print("6. REMAINING PREFIX-FORBIDDEN MIDDLEs")
print("="*70)

remaining = new_prefix_forbidden
print(f"\n{len(remaining)} MIDDLEs still PREFIX-FORBIDDEN after articulator extension")

# Check their starting characters
remaining_starts = Counter(m[0] for m in remaining if m)
print(f"\nStarting characters:")
for char, cnt in remaining_starts.most_common(10):
    pct = 100 * cnt / len(remaining)
    print(f"  '{char}': {cnt} ({pct:.1f}%)")

# Show some examples
print(f"\nExample remaining PREFIX-FORBIDDEN MIDDLEs:")
for m in sorted(remaining)[:20]:
    print(f"  {m}")
