#!/usr/bin/env python3
"""
Check: Do PREFIX-FORBIDDEN tokens use different SUFFIX patterns?

If PREFIX+SUFFIX have enriched pairings (like qo+ol, ch+y, d+or),
do PREFIX-FORBIDDEN tokens avoid the "paired" suffixes?
"""

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

# First classify MIDDLEs into prefix-required/forbidden
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
        prefix, middle, suffix = extract_full(word)
        if middle and middle in ri_middles:
            if prefix:
                appears_with_prefix.add(middle)
            else:
                appears_without_prefix.add(middle)

prefix_required = appears_with_prefix - appears_without_prefix
prefix_forbidden = appears_without_prefix - appears_with_prefix

# Now collect SUFFIX distributions for each population
prefixed_suffixes = Counter()    # Suffixes on PREFIX-REQUIRED tokens (when they have prefix)
unprefixed_suffixes = Counter()  # Suffixes on PREFIX-FORBIDDEN tokens

# Also track by specific prefix for comparison
prefix_to_suffix = {}  # prefix -> Counter of suffixes

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
        if middle and middle in ri_middles and suffix:
            if middle in prefix_required and prefix:
                prefixed_suffixes[suffix] += 1
                if prefix not in prefix_to_suffix:
                    prefix_to_suffix[prefix] = Counter()
                prefix_to_suffix[prefix][suffix] += 1
            elif middle in prefix_forbidden:
                unprefixed_suffixes[suffix] += 1

print("="*70)
print("SUFFIX DISTRIBUTION: PREFIX-REQUIRED vs PREFIX-FORBIDDEN")
print("="*70)

# Normalize to percentages
total_prefixed = sum(prefixed_suffixes.values())
total_unprefixed = sum(unprefixed_suffixes.values())

print(f"\nPREFIX-REQUIRED tokens with suffix: {total_prefixed}")
print(f"PREFIX-FORBIDDEN tokens with suffix: {total_unprefixed}")

# Top suffixes in each
print("\nTop 10 suffixes on PREFIX-REQUIRED:")
for suf, cnt in prefixed_suffixes.most_common(10):
    pct = 100 * cnt / total_prefixed
    print(f"  -{suf}: {cnt} ({pct:.1f}%)")

print("\nTop 10 suffixes on PREFIX-FORBIDDEN:")
for suf, cnt in unprefixed_suffixes.most_common(10):
    pct = 100 * cnt / total_unprefixed
    print(f"  -{suf}: {cnt} ({pct:.1f}%)")

# Compare specific suffixes
print("\n" + "="*70)
print("SUFFIX COMPARISON (% of each population)")
print("="*70)

all_suffixes = set(prefixed_suffixes.keys()) | set(unprefixed_suffixes.keys())
main_suffixes = ['y', 'dy', 'ol', 'or', 'ey', 'ar', 'al', 'hy', 'ly', 's']

print(f"\n{'Suffix':<10} {'PREFIX-REQ':>12} {'PREFIX-FORB':>12} {'Difference':>12}")
print("-" * 50)

for suf in main_suffixes:
    pct_req = 100 * prefixed_suffixes[suf] / total_prefixed if total_prefixed else 0
    pct_forb = 100 * unprefixed_suffixes[suf] / total_unprefixed if total_unprefixed else 0
    diff = pct_forb - pct_req
    diff_str = f"{diff:+.1f}%" if diff != 0 else "0"
    print(f"-{suf:<9} {pct_req:>10.1f}% {pct_forb:>10.1f}% {diff_str:>12}")

# Check for enriched pairings
print("\n" + "="*70)
print("ENRICHED PREFIX+SUFFIX PAIRINGS")
print("="*70)
print("\nFrom earlier analysis, these are the enriched combinations:")
print("  qo+ol (1.35x), ok+ol (1.30x), ok+ey (1.35x), ch+y (1.28x), d+or (1.39x)")

# What fraction of each suffix comes from its "paired" prefix?
paired_suffixes = {
    'ol': ['qo', 'ok'],
    'ey': ['ok'],
    'y': ['ch'],
    'or': ['d'],
}

print("\nDo PREFIX-FORBIDDEN tokens use 'paired' suffixes at lower rates?")
for suf, paired_prefs in paired_suffixes.items():
    forb_pct = 100 * unprefixed_suffixes[suf] / total_unprefixed if total_unprefixed else 0
    req_pct = 100 * prefixed_suffixes[suf] / total_prefixed if total_prefixed else 0
    print(f"\n  -{suf} (paired with {paired_prefs}):")
    print(f"    PREFIX-FORBIDDEN: {forb_pct:.1f}%")
    print(f"    PREFIX-REQUIRED: {req_pct:.1f}%")
    if forb_pct < req_pct:
        print(f"    --> LOWER in PREFIX-FORBIDDEN (as expected if pairing matters)")
    else:
        print(f"    --> HIGHER/EQUAL in PREFIX-FORBIDDEN")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
