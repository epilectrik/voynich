#!/usr/bin/env python3
"""Check B frequency of singleton PP MIDDLEs."""

import json
from collections import Counter
import csv

PROJECT_ROOT = 'C:/git/voynich'
DATA_PATH = f'{PROJECT_ROOT}/data/transcriptions/interlinear_full_words.txt'

# Standard PREFIX list
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

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

def extract_middle(token):
    """Extract (prefix, middle, suffix) from token."""
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix

# Load A data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json') as f:
    a_tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])

# Count PP MIDDLE frequencies in A
pp_middle_counts_a = Counter()
for t in a_tokens:
    if t['middle'] not in ri_middles:
        pp_middle_counts_a[t['middle']] += 1

singleton_pp_middles = set(m for m, c in pp_middle_counts_a.items() if c == 1)
print(f"Singleton PP MIDDLEs in A: {len(singleton_pp_middles)}")

# Load B data and count MIDDLE frequencies
b_middle_counts = Counter()

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '') != 'H':
            continue
        if row.get('language', '') != 'B':
            continue

        word = row.get('word', '').strip().lower()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle:
            b_middle_counts[middle] += 1

print(f"Total B MIDDLEs: {len(b_middle_counts)}")
print(f"Total B tokens: {sum(b_middle_counts.values())}")
print()

# Check singleton PP MIDDLEs in B
print("=" * 60)
print("SINGLETON PP MIDDLES: A vs B FREQUENCY")
print("=" * 60)
print()

# Frequency in B for singleton PP MIDDLEs
b_freqs_of_singletons = []
for m in singleton_pp_middles:
    b_freq = b_middle_counts.get(m, 0)
    b_freqs_of_singletons.append((m, 1, b_freq))

# Sort by B frequency
b_freqs_of_singletons.sort(key=lambda x: -x[2])

# Summary stats
b_freqs = [x[2] for x in b_freqs_of_singletons]
print(f"B frequency of singleton PP MIDDLEs:")
print(f"  Mean: {sum(b_freqs)/len(b_freqs):.1f}")
print(f"  Median: {sorted(b_freqs)[len(b_freqs)//2]}")
print(f"  Min: {min(b_freqs)}")
print(f"  Max: {max(b_freqs)}")
print()

# Distribution
b_singleton = sum(1 for f in b_freqs if f == 1)
b_low = sum(1 for f in b_freqs if 2 <= f <= 5)
b_mid = sum(1 for f in b_freqs if 6 <= f <= 20)
b_high = sum(1 for f in b_freqs if f > 20)

print(f"B frequency distribution:")
print(f"  Singleton in B (freq=1): {b_singleton} ({100*b_singleton/len(b_freqs):.1f}%)")
print(f"  Low in B (2-5): {b_low} ({100*b_low/len(b_freqs):.1f}%)")
print(f"  Mid in B (6-20): {b_mid} ({100*b_mid/len(b_freqs):.1f}%)")
print(f"  High in B (>20): {b_high} ({100*b_high/len(b_freqs):.1f}%)")
print()

# Show examples
print("EXAMPLES: High B frequency (singleton in A, common in B):")
for m, a_freq, b_freq in b_freqs_of_singletons[:10]:
    print(f"  {m:<10} A={a_freq}, B={b_freq}")
print()

print("EXAMPLES: Also singleton in B (truly rare):")
truly_rare = [(m, a, b) for m, a, b in b_freqs_of_singletons if b == 1]
for m, a_freq, b_freq in truly_rare[:10]:
    print(f"  {m:<10} A={a_freq}, B={b_freq}")
print()

# Compare to high-frequency PP MIDDLEs
print("=" * 60)
print("COMPARISON: HIGH-FREQ PP MIDDLES IN B")
print("=" * 60)
print()

high_freq_pp = [m for m, c in pp_middle_counts_a.items() if c >= 50]
print(f"High-frequency PP MIDDLEs in A (>=50): {len(high_freq_pp)}")
for m in high_freq_pp[:10]:
    a_freq = pp_middle_counts_a[m]
    b_freq = b_middle_counts.get(m, 0)
    print(f"  {m:<10} A={a_freq}, B={b_freq}")
