#!/usr/bin/env python3
"""
Check if RI has two categories (long vs short) and if they behave differently.
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

print("="*70)
print("RI LENGTH DISTRIBUTION")
print("="*70)

# Group RI by length
ri_by_length = defaultdict(list)
for ri in ri_middles:
    ri_by_length[len(ri)].append(ri)

print("\nRI by length:")
for length in sorted(ri_by_length.keys()):
    items = ri_by_length[length]
    print(f"  Length {length}: {len(items)} items")
    if len(items) <= 10:
        print(f"    {items}")
    else:
        print(f"    Examples: {items[:5]}...")

# Check if short RI overlap with PP
print("\n" + "="*70)
print("DO SHORT RI OVERLAP WITH PP?")
print("="*70)

short_ri = [ri for ri in ri_middles if len(ri) <= 3]
long_ri = [ri for ri in ri_middles if len(ri) > 3]

print(f"\nShort RI (<=3 chars): {len(short_ri)}")
print(f"Long RI (>3 chars): {len(long_ri)}")

# Check if short RI are substrings of PP or vice versa
short_in_pp = [ri for ri in short_ri if ri in pp_middles]
print(f"\nShort RI that are ALSO in PP (should be 0): {len(short_in_pp)}")
if short_in_pp:
    print(f"  {short_in_pp}")

# Check if short RI are PP atoms
print("\nShort RI examples:")
for ri in sorted(short_ri)[:20]:
    print(f"  {ri}")

# Now check folio distribution by length
print("\n" + "="*70)
print("FOLIO DISTRIBUTION BY RI LENGTH")
print("="*70)

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

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

        middle = extract_middle(word)
        if middle and middle in ri_middles:
            ri_to_folios[middle].add(folio)

# Compare short vs long RI folio distribution
short_folio_counts = [len(ri_to_folios.get(ri, set())) for ri in short_ri if ri in ri_to_folios]
long_folio_counts = [len(ri_to_folios.get(ri, set())) for ri in long_ri if ri in ri_to_folios]

import statistics

if short_folio_counts:
    print(f"\nShort RI (<=3 chars):")
    print(f"  Mean folios: {statistics.mean(short_folio_counts):.1f}")
    print(f"  Median folios: {statistics.median(short_folio_counts)}")
    print(f"  Max folios: {max(short_folio_counts)}")

if long_folio_counts:
    print(f"\nLong RI (>3 chars):")
    print(f"  Mean folios: {statistics.mean(long_folio_counts):.1f}")
    print(f"  Median folios: {statistics.median(long_folio_counts)}")
    print(f"  Max folios: {max(long_folio_counts)}")

# Show the most distributed short RI
print("\n" + "="*70)
print("MOST DISTRIBUTED SHORT RI")
print("="*70)

short_distributed = [(ri, len(ri_to_folios.get(ri, set())))
                     for ri in short_ri if ri in ri_to_folios]
short_distributed.sort(key=lambda x: -x[1])

print("\nShort RI appearing on most folios:")
for ri, count in short_distributed[:15]:
    print(f"  {ri}: {count} folios")

# Show the most distributed long RI
print("\n" + "="*70)
print("MOST DISTRIBUTED LONG RI")
print("="*70)

long_distributed = [(ri, len(ri_to_folios.get(ri, set())))
                    for ri in long_ri if ri in ri_to_folios]
long_distributed.sort(key=lambda x: -x[1])

print("\nLong RI appearing on most folios:")
for ri, count in long_distributed[:15]:
    print(f"  {ri}: {count} folios")

# Check if there's a bimodal distribution
print("\n" + "="*70)
print("IS THERE A BIMODAL DISTRIBUTION?")
print("="*70)

all_folio_counts = [len(folios) for folios in ri_to_folios.values()]
folio_count_dist = Counter(all_folio_counts)

print("\nFolio count distribution:")
for count in sorted(folio_count_dist.keys())[:15]:
    freq = folio_count_dist[count]
    bar = '*' * min(freq, 50)
    print(f"  {count:2d} folios: {freq:3d} RI {bar}")

# Check the high-distribution outliers
print("\n" + "="*70)
print("HIGH-DISTRIBUTION OUTLIERS (10+ folios)")
print("="*70)

outliers = [(ri, len(folios)) for ri, folios in ri_to_folios.items() if len(folios) >= 10]
outliers.sort(key=lambda x: -x[1])

print(f"\nRI appearing on 10+ folios: {len(outliers)}")
for ri, count in outliers:
    length = len(ri)
    print(f"  {ri} (len={length}): {count} folios")
