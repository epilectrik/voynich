#!/usr/bin/env python3
"""
Detail the PP tokens linking animal A records to chicken B folios.

Question: Does the specific PP vocabulary distinguish which animal is which?
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

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

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Chicken folios
chicken_folios = ['f40v', 'f41v', 'f85r1', 'f94v', 'f95v1']

# Get PP for each chicken folio
chicken_pp = {}
for folio in chicken_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    folio_middles = set(folio_tokens['middle'].dropna().unique())
    chicken_pp[folio] = (folio_middles & shared_middles) - infrastructure

# Animal records we found
animal_records = [
    ('f100r:3', 'teold'),
    ('f89r2:1', 'eyd'),
    ('f23r:4', 'chald'),
    ('f90r1:6', 'eoschso'),
]

# Also add the other animal record locations
more_records = [
    ('f89r2:4', 'olfcho,olar'),
    ('f100r:3', 'teold'),  # duplicate
    ('f19r:1', 'hyd'),  # check this
]

print("=" * 70)
print("ANIMAL RECORD PP DETAIL")
print("=" * 70)
print()

# Build A records
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()
a_records.columns = ['folio', 'line', 'middles', 'words']

for rec_id, animal_token in animal_records:
    folio, line = rec_id.split(':')
    rec = a_records[(a_records['folio'] == folio) & (a_records['line'].astype(str) == line)]

    if len(rec) == 0:
        print(f"{rec_id}: NOT FOUND")
        continue

    rec = rec.iloc[0]
    print(f"RECORD: {rec_id}")
    print(f"  Animal token: {animal_token}")
    print(f"  All MIDDLEs: {rec['middles']}")
    print(f"  Words: {rec['words']}")
    print()

    # PP overlap with each chicken folio
    print("  PP overlap by chicken folio:")
    for cf in chicken_folios:
        overlap = rec['middles'] & chicken_pp[cf]
        if overlap:
            print(f"    {cf}: {overlap}")

    # RI tokens (not in B)
    ri = rec['middles'] - b_middles
    print(f"  RI tokens: {ri}")
    print()
    print("-" * 50)
    print()

# Check if PP patterns differ
print()
print("=" * 70)
print("PP PATTERN COMPARISON")
print("=" * 70)
print()

# For each animal record, get full PP pattern
patterns = {}
for rec_id, animal_token in animal_records:
    folio, line = rec_id.split(':')
    rec = a_records[(a_records['folio'] == folio) & (a_records['line'].astype(str) == line)]
    if len(rec) == 0:
        continue
    rec = rec.iloc[0]

    pattern = {}
    for cf in chicken_folios:
        overlap = rec['middles'] & chicken_pp[cf]
        pattern[cf] = overlap

    patterns[rec_id] = pattern

# Show unique PP for each
print("Unique PP tokens (in this record's chicken connection but not others):")
print()

for rec_id, pattern in patterns.items():
    all_pp_this = set()
    for v in pattern.values():
        all_pp_this.update(v)

    all_pp_others = set()
    for other_id, other_pattern in patterns.items():
        if other_id != rec_id:
            for v in other_pattern.values():
                all_pp_others.update(v)

    unique_pp = all_pp_this - all_pp_others
    animal = [t for r, t in animal_records if r == rec_id][0]

    print(f"{rec_id} ({animal}):")
    print(f"  Total PP: {all_pp_this}")
    print(f"  Unique PP: {unique_pp}")
    print()
