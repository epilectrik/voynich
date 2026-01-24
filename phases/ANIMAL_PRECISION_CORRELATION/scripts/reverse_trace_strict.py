#!/usr/bin/env python3
"""
Strict Reverse Trace: Following expert methodology

1. Extract RARE MIDDLEs from candidate B folio (freq rank > 100)
2. Find A entries with >=3 rare MIDDLE co-occurrences
3. Filter to S-zone affinity (REGIME_4 appropriate)
4. Expected result: 0-10 highly specific A entries
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)
SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin', 'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy', 'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey', 'chol', 'shol', 'kol', 'tol', 'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
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
    # Sort suffixes by length (longest first) to match correctly
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    middle = remainder[:-len(suffix)] if suffix else remainder
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix

df_a['prefix'], df_a['middle'], df_a['suffix'] = zip(*df_a['word'].apply(extract_morphology))
df_b['prefix'], df_b['middle'], df_b['suffix'] = zip(*df_b['word'].apply(extract_morphology))

print("=" * 70)
print("STRICT REVERSE TRACE (Expert Methodology)")
print("=" * 70)
print()

# Step 1: Compute global MIDDLE frequencies in B
b_middle_counts = df_b['middle'].value_counts()
total_b_middles = len(b_middle_counts)
print(f"Total unique MIDDLEs in B: {total_b_middles}")

# Create frequency rank
b_middle_rank = {middle: rank for rank, middle in enumerate(b_middle_counts.index, 1)}

# Step 2: Extract MIDDLEs from candidate B folio
candidate_folio = 'f43v'
print(f"\nCandidate B folio: {candidate_folio}")

folio_tokens = df_b[df_b['folio'] == candidate_folio]
folio_middles = set(folio_tokens['middle'].dropna().unique())
print(f"Unique MIDDLEs in {candidate_folio}: {len(folio_middles)}")

# Identify shared MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles
folio_shared = folio_middles & shared_middles

print(f"Shared MIDDLEs (in both A and B): {len(folio_shared)}")

# Step 3: Identify RARE MIDDLEs (freq rank > 100)
rare_threshold = 100
folio_rare = {m for m in folio_shared if b_middle_rank.get(m, 9999) > rare_threshold}
print(f"\nRare MIDDLEs (rank > {rare_threshold}): {len(folio_rare)}")
print(f"Rare MIDDLEs: {sorted(folio_rare)}")

# Show their ranks
print("\nRare MIDDLE ranks:")
for m in sorted(folio_rare, key=lambda x: b_middle_rank.get(x, 9999)):
    rank = b_middle_rank.get(m, 'N/A')
    count = b_middle_counts.get(m, 0)
    print(f"  {m}: rank={rank}, count={count}")

# Step 4: Find A entries with >=3 rare MIDDLE co-occurrences
print()
print("-" * 70)
print("FINDING A ENTRIES WITH 3+ RARE MIDDLE CO-OCCURRENCES")
print("-" * 70)
print()

a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

def count_rare_overlap(entry_middles, rare_set):
    if not entry_middles:
        return 0
    return len(entry_middles & rare_set)

a_entries['rare_overlap'] = a_entries['middles'].apply(lambda x: count_rare_overlap(x, folio_rare))

# Filter to entries with >=3 rare MIDDLEs
strict_threshold = 3
strict_candidates = a_entries[a_entries['rare_overlap'] >= strict_threshold].copy()
strict_candidates = strict_candidates.sort_values('rare_overlap', ascending=False)

print(f"A entries with >= {strict_threshold} rare MIDDLE co-occurrences: {len(strict_candidates)}")
print()

if len(strict_candidates) == 0:
    print("No entries found with strict threshold.")
    print("Trying threshold of 2...")
    strict_threshold = 2
    strict_candidates = a_entries[a_entries['rare_overlap'] >= strict_threshold].copy()
    strict_candidates = strict_candidates.sort_values('rare_overlap', ascending=False)
    print(f"A entries with >= {strict_threshold} rare MIDDLEs: {len(strict_candidates)}")

if len(strict_candidates) > 0:
    print("\nCandidate A entries:")
    for _, row in strict_candidates.head(20).iterrows():
        overlap_middles = row['middles'] & folio_rare
        print(f"  {row['folio']}:{row['line']} - rare_overlap={row['rare_overlap']}")
        print(f"    Overlapping rare MIDDLEs: {overlap_middles}")

# Step 5: Check for RI MIDDLEs with animal priors in strict candidates
print()
print("-" * 70)
print("CHECKING RI MIDDLEs IN STRICT CANDIDATES")
print("-" * 70)
print()

# Load material-class priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {}) for item in priors_data['results']}

# Collect all MIDDLEs from strict candidates
if len(strict_candidates) > 0:
    candidate_middles = set()
    for _, row in strict_candidates.iterrows():
        candidate_middles.update(row['middles'])

    # RI = in A but not in B
    ri_in_candidates = candidate_middles - b_middles
    print(f"Total MIDDLEs in strict candidates: {len(candidate_middles)}")
    print(f"Of which are RI (not in B): {len(ri_in_candidates)}")

    # Check animal priors
    ri_with_animal = []
    for middle in ri_in_candidates:
        if middle in priors_lookup:
            animal_p = priors_lookup[middle].get('animal', 0)
            if animal_p > 0:
                ri_with_animal.append((middle, animal_p))

    print(f"RI MIDDLEs with animal > 0: {len(ri_with_animal)}")
    print()

    if ri_with_animal:
        print("Animal-associated RI MIDDLEs in strict candidates:")
        for middle, prob in sorted(ri_with_animal, key=lambda x: -x[1]):
            print(f"  {middle}: P(animal)={prob:.2f}")
else:
    ri_in_candidates = set()
    ri_with_animal = []

# Step 6: Also try 50%+ overlap approach
print()
print("-" * 70)
print("ALTERNATIVE: 50%+ TOTAL OVERLAP APPROACH")
print("-" * 70)
print()

total_overlap_threshold = len(folio_shared) // 2  # 50% of shared MIDDLEs
print(f"Requiring >= {total_overlap_threshold} MIDDLEs overlap (50% of {len(folio_shared)})")

def count_total_overlap(entry_middles, target_set):
    if not entry_middles:
        return 0
    return len(entry_middles & target_set)

a_entries['total_overlap'] = a_entries['middles'].apply(lambda x: count_total_overlap(x, folio_shared))
high_overlap = a_entries[a_entries['total_overlap'] >= total_overlap_threshold].copy()
high_overlap = high_overlap.sort_values('total_overlap', ascending=False)

print(f"A entries with >= {total_overlap_threshold} total MIDDLEs overlap: {len(high_overlap)}")

if len(high_overlap) > 0:
    print("\nHigh-overlap A entries:")
    for _, row in high_overlap.head(10).iterrows():
        print(f"  {row['folio']}:{row['line']} - overlap={row['total_overlap']}/{len(folio_shared)}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

print(f"Candidate B folio: {candidate_folio} (REGIME_4, precision profile)")
print(f"Shared MIDDLEs: {len(folio_shared)}")
print(f"Rare MIDDLEs (rank>{rare_threshold}): {len(folio_rare)}")
print()
print(f"Strict approach (>=3 rare co-occur): {len(strict_candidates)} A entries")
print(f"50% overlap approach: {len(high_overlap)} A entries")
print()

if len(strict_candidates) <= 10 and len(strict_candidates) > 0:
    print("GOOD: Strict approach yields specific candidates (<=10)")
    print("These entries are highly constrained matches.")
elif len(strict_candidates) == 0:
    print("NOTE: No entries meet strict threshold.")
    print("Either f43v doesn't have enough rare MIDDLEs,")
    print("or there's no strong A-entry match for this folio.")
else:
    print("WARNING: Still too many candidates.")
    print("May need additional filtering (zone affinity, PREFIX compatibility).")

# Save results
results = {
    'candidate_folio': candidate_folio,
    'folio_shared_middles': len(folio_shared),
    'folio_rare_middles': len(folio_rare),
    'rare_middles_list': list(folio_rare),
    'strict_candidates': [
        {'folio': row['folio'], 'line': str(row['line']), 'rare_overlap': int(row['rare_overlap'])}
        for _, row in strict_candidates.iterrows()
    ],
    'high_overlap_candidates': [
        {'folio': row['folio'], 'line': str(row['line']), 'total_overlap': int(row['total_overlap'])}
        for _, row in high_overlap.iterrows()
    ],
    'ri_with_animal': ri_with_animal
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'reverse_trace_strict.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to {output_path}")
