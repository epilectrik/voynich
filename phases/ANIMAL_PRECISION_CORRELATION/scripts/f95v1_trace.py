#!/usr/bin/env python3
"""
Trace from f95v1 (chicken-specific B folio from 4D conjunction) to A records.

f95v1 was the ONLY folio matching:
- REGIME_4
- High qo (escape)
- High aux (ok/ot)
- Low da

This is our best chicken candidate. What A records does its PP converge to?
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("F95V1 TRACE: Chicken-specific B folio -> A records")
print("=" * 70)
print()

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t')
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or '_EMPTY_'
            return remainder or '_EMPTY_'
    return None

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

# Vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# =============================================================================
# Get f95v1 PP vocabulary
# =============================================================================
print("-" * 70)
print("Step 1: f95v1 PP vocabulary")
print("-" * 70)
print()

f95v1_tokens = df_b[df_b['folio'] == 'f95v1']
f95v1_middles = set(f95v1_tokens['middle'].dropna().unique())
f95v1_pp = (f95v1_middles & shared_middles) - infrastructure

print(f"f95v1 total MIDDLEs: {len(f95v1_middles)}")
print(f"f95v1 PP (discriminative): {len(f95v1_pp)}")
print(f"PP tokens: {sorted(f95v1_pp)}")
print()

# =============================================================================
# Build A records and count f95v1 PP convergence
# =============================================================================
print("-" * 70)
print("Step 2: A records with f95v1 PP convergence")
print("-" * 70)
print()

a_records = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_records.columns = ['folio', 'line', 'middles']
a_records['record_id'] = a_records['folio'] + ':' + a_records['line'].astype(str)

a_records['f95v1_overlap'] = a_records['middles'].apply(lambda x: len(x & f95v1_pp))

# Sort by overlap
a_records_sorted = a_records.sort_values('f95v1_overlap', ascending=False)

# Show top converging records
print("Top A records by f95v1 PP convergence:")
print()
for _, row in a_records_sorted.head(20).iterrows():
    if row['f95v1_overlap'] >= 2:
        overlap_tokens = row['middles'] & f95v1_pp
        ri_tokens = row['middles'] - b_middles
        print(f"{row['record_id']}: {row['f95v1_overlap']} PP overlap")
        print(f"  PP matches: {overlap_tokens}")
        print(f"  RI tokens: {ri_tokens}")
        print()

# =============================================================================
# Check animal tokens in converging records
# =============================================================================
print("-" * 70)
print("Step 3: Animal tokens in f95v1-converging records")
print("-" * 70)
print()

animal_middles = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}

# Records with 3+ f95v1 PP overlap
high_convergence = a_records[a_records['f95v1_overlap'] >= 3]

print(f"Records with 3+ f95v1 PP: {len(high_convergence)}")

# Check for animal tokens
for _, row in high_convergence.iterrows():
    ri_tokens = row['middles'] - b_middles
    animal_in_record = ri_tokens & animal_middles
    if animal_in_record:
        print(f"  {row['record_id']}: ANIMAL RI = {animal_in_record}")

# Also check 2+ overlap
print()
mid_convergence = a_records[(a_records['f95v1_overlap'] >= 2) & (a_records['f95v1_overlap'] < 3)]
print(f"Records with 2 f95v1 PP: {len(mid_convergence)}")

for _, row in mid_convergence.iterrows():
    ri_tokens = row['middles'] - b_middles
    animal_in_record = ri_tokens & animal_middles
    if animal_in_record:
        print(f"  {row['record_id']}: ANIMAL RI = {animal_in_record}")

# =============================================================================
# Compare: What A records do OTHER chicken-adjacent folios converge to?
# =============================================================================
print()
print("-" * 70)
print("Step 4: Compare with other chicken-candidate folios")
print("-" * 70)
print()

# From chicken_triangulation.py, the chicken-like folios were:
# f40v, f41v, f85r1, f94v, f95v1 (high qo + aux in REGIME_4)
chicken_folios = ['f40v', 'f41v', 'f85r1', 'f94v', 'f95v1']

for folio in chicken_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    folio_middles = set(folio_tokens['middle'].dropna().unique())
    folio_pp = (folio_middles & shared_middles) - infrastructure

    # Count A records with 3+ overlap
    a_records[f'{folio}_overlap'] = a_records['middles'].apply(lambda x: len(x & folio_pp))
    high_conv = a_records[a_records[f'{folio}_overlap'] >= 3]

    # Check for animal tokens
    animal_records = []
    for _, row in high_conv.iterrows():
        ri = row['middles'] - b_middles
        if ri & animal_middles:
            animal_records.append((row['record_id'], ri & animal_middles))

    print(f"{folio}: {len(folio_pp)} PP, {len(high_conv)} records at 3+, {len(animal_records)} with animal RI")
    if animal_records:
        for rec_id, animals in animal_records[:3]:
            print(f"    {rec_id}: {animals}")

# =============================================================================
# Final: Intersection of chicken folio convergence
# =============================================================================
print()
print("-" * 70)
print("Step 5: Records converging to MULTIPLE chicken folios")
print("-" * 70)
print()

# Records with 2+ overlap to at least 3 of the 5 chicken folios
a_records['chicken_folio_count'] = sum(
    (a_records[f'{f}_overlap'] >= 2).astype(int) for f in chicken_folios
)

multi_chicken = a_records[a_records['chicken_folio_count'] >= 3]
print(f"Records converging to 3+ chicken folios (at 2+ PP each): {len(multi_chicken)}")

for _, row in multi_chicken.iterrows():
    ri = row['middles'] - b_middles
    animal = ri & animal_middles
    which_folios = [f for f in chicken_folios if row[f'{f}_overlap'] >= 2]
    print(f"  {row['record_id']}: converges to {which_folios}")
    print(f"    RI: {ri}")
    if animal:
        print(f"    *** ANIMAL: {animal} ***")
