#!/usr/bin/env python3
"""
Reverse Trace Test: Can we trace from B folio back to A entries?

Approach:
1. Pick B folio candidate (f43v - low recovery, high escape = Kuetreck candidate)
2. Extract all MIDDLEs used in that folio
3. Find A entries with high overlap on those MIDDLEs
4. Extract RI MIDDLEs from high-overlap A entries
5. Check material-class priors of those RIs
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Split by Currier language
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology parsing (same as before)
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

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
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
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix

# Parse morphology for both A and B
df_a['prefix'], df_a['middle'], df_a['suffix'] = zip(*df_a['word'].apply(extract_morphology))
df_b['prefix'], df_b['middle'], df_b['suffix'] = zip(*df_b['word'].apply(extract_morphology))

print("=" * 70)
print("REVERSE TRACE TEST: B FOLIO -> A ENTRIES")
print("=" * 70)
print()

# Step 1: Extract MIDDLEs from candidate B folio
candidate_folio = 'f43v'
print(f"Candidate B folio: {candidate_folio}")
print("(Selected because: low recovery=2, high near_miss=33, timing-critical profile)")
print()

folio_tokens = df_b[df_b['folio'] == candidate_folio]
folio_middles = set(folio_tokens['middle'].dropna().unique())
print(f"Unique MIDDLEs in {candidate_folio}: {len(folio_middles)}")
print(f"Sample: {list(folio_middles)[:15]}...")
print()

# Step 2: Identify shared vs B-exclusive MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

folio_shared = folio_middles & shared_middles
folio_b_exclusive = folio_middles - shared_middles

print(f"Shared MIDDLEs (appear in both A and B): {len(folio_shared)}")
print(f"B-exclusive MIDDLEs (only in B): {len(folio_b_exclusive)}")
print()

# Step 3: Find A entries (lines) with high overlap on the shared MIDDLEs
print("-" * 70)
print("FINDING A ENTRIES WITH HIGH MIDDLE OVERLAP")
print("-" * 70)
print()

# Group A by folio+line_number to get "entries"
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Calculate overlap with candidate folio's shared MIDDLEs
def calc_overlap(entry_middles, target_middles):
    if not entry_middles or not target_middles:
        return 0, 0
    intersection = entry_middles & target_middles
    return len(intersection), len(intersection) / len(target_middles)

a_entries['overlap_count'], a_entries['overlap_ratio'] = zip(*a_entries['middles'].apply(
    lambda x: calc_overlap(x, folio_shared)
))

# Sort by overlap
a_entries_sorted = a_entries.sort_values('overlap_count', ascending=False)

print(f"Target: {len(folio_shared)} shared MIDDLEs from {candidate_folio}")
print()
print("Top 20 A entries by MIDDLE overlap:")
print()

for i, row in a_entries_sorted.head(20).iterrows():
    print(f"  {row['folio']}:{row['line']} - overlap={row['overlap_count']}/{len(folio_shared)} "
          f"({row['overlap_ratio']*100:.1f}%) - entry has {len(row['middles'])} MIDDLEs")

# Step 4: For high-overlap entries, extract their RI MIDDLEs
print()
print("-" * 70)
print("EXTRACTING RI MIDDLEs FROM HIGH-OVERLAP A ENTRIES")
print("-" * 70)
print()

# Get entries with overlap >= 3
high_overlap_entries = a_entries_sorted[a_entries_sorted['overlap_count'] >= 3]
print(f"A entries with overlap >= 3: {len(high_overlap_entries)}")

# Collect all MIDDLEs from high-overlap entries
high_overlap_middles = set()
for _, row in high_overlap_entries.iterrows():
    high_overlap_middles.update(row['middles'])

# RI MIDDLEs = those in A but not in B
ri_middles_in_candidates = high_overlap_middles - b_middles
print(f"Total unique MIDDLEs in high-overlap entries: {len(high_overlap_middles)}")
print(f"Of which are RI (not in B): {len(ri_middles_in_candidates)}")
print()

# Step 5: Check material-class priors for those RI MIDDLEs
print("-" * 70)
print("CHECKING MATERIAL-CLASS PRIORS FOR CANDIDATE RI MIDDLEs")
print("-" * 70)
print()

# Load material-class priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

# Build lookup
priors_lookup = {}
for item in priors_data['results']:
    priors_lookup[item['middle']] = item.get('material_class_posterior', {})

# Check which RI MIDDLEs have priors
ri_with_priors = []
ri_with_animal = []

for middle in ri_middles_in_candidates:
    if middle in priors_lookup:
        priors = priors_lookup[middle]
        ri_with_priors.append((middle, priors))
        if priors.get('animal', 0) > 0:
            ri_with_animal.append((middle, priors))

print(f"RI MIDDLEs with material-class priors: {len(ri_with_priors)}")
print(f"RI MIDDLEs with animal > 0: {len(ri_with_animal)}")
print()

if ri_with_animal:
    print("RI MIDDLEs with animal probability:")
    for middle, priors in sorted(ri_with_animal, key=lambda x: x[1].get('animal', 0), reverse=True):
        animal_p = priors.get('animal', 0)
        print(f"  {middle}: P(animal)={animal_p:.2f}")
else:
    print("No RI MIDDLEs with animal probability found in high-overlap entries.")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

if ri_with_animal:
    print(f"POSITIVE SIGNAL: Found {len(ri_with_animal)} RI MIDDLEs with animal priors")
    print("in A entries that share vocabulary with our candidate B folio.")
    print()
    print("This suggests a possible trace from:")
    print(f"  {candidate_folio} (B, REGIME_4, precision) -> A entries with animal-associated RIs")
else:
    print("NO SIGNAL: The high-overlap A entries don't contain RI MIDDLEs with animal priors.")
    print()
    print("Possible explanations:")
    print("1. The candidate folio doesn't execute animal distillation")
    print("2. The overlap threshold is too low to find the right entries")
    print("3. C384 is stricter than we thought - no statistical trace possible")

# Save results
results = {
    'candidate_folio': candidate_folio,
    'folio_unique_middles': len(folio_middles),
    'folio_shared_middles': len(folio_shared),
    'folio_b_exclusive_middles': len(folio_b_exclusive),
    'high_overlap_entry_count': len(high_overlap_entries),
    'ri_middles_in_candidates': len(ri_middles_in_candidates),
    'ri_with_priors': len(ri_with_priors),
    'ri_with_animal': [(m, p) for m, p in ri_with_animal],
    'top_overlap_entries': [
        {'folio': row['folio'], 'line': str(row['line']),
         'overlap': int(row['overlap_count']), 'ratio': float(row['overlap_ratio'])}
        for _, row in a_entries_sorted.head(20).iterrows()
    ]
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'reverse_trace_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to {output_path}")
