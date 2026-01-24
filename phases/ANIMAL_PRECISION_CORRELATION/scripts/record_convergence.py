#!/usr/bin/env python3
"""
Record-level PP convergence test.

Strategy:
1. Get PP vocabulary from recipe-constrained B folios
2. Find A RECORDS where multiple PP tokens converge
3. Extract RI tokens from those specific records
4. Check if different recipes converge to DIFFERENT records
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("RECORD-LEVEL PP CONVERGENCE")
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
shared_middles = a_middles & b_middles  # PP

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

regime1_folios = set(regime_data.get('REGIME_1', []))
regime4_folios = set(regime_data.get('REGIME_4', []))

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Build A records (folio:line)
a_records = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_records.columns = ['folio', 'line', 'middles']
a_records['record_id'] = a_records['folio'] + ':' + a_records['line'].astype(str)

print(f"Total A records: {len(a_records)}")
print()

# =============================================================================
# Get PP vocabulary by REGIME
# =============================================================================

def get_regime_pp(regime_folios):
    middles = set()
    for folio in regime_folios:
        folio_tokens = df_b[df_b['folio'] == folio]
        middles.update(folio_tokens['middle'].dropna().unique())
    return (middles & shared_middles) - infrastructure

regime1_pp = get_regime_pp(regime1_folios)
regime4_pp = get_regime_pp(regime4_folios)

# EXCLUSIVE PP = in one regime but not the other
regime1_exclusive = regime1_pp - regime4_pp
regime4_exclusive = regime4_pp - regime1_pp

print(f"REGIME_1 PP: {len(regime1_pp)} total, {len(regime1_exclusive)} exclusive")
print(f"REGIME_4 PP: {len(regime4_pp)} total, {len(regime4_exclusive)} exclusive")
print()

# =============================================================================
# Find A RECORDS with high PP convergence
# =============================================================================
print("-" * 70)
print("A RECORDS by PP convergence")
print("-" * 70)
print()

# Count convergence for each record
a_records['r1_count'] = a_records['middles'].apply(lambda x: len(x & regime1_pp))
a_records['r4_count'] = a_records['middles'].apply(lambda x: len(x & regime4_pp))
a_records['r1_excl'] = a_records['middles'].apply(lambda x: len(x & regime1_exclusive))
a_records['r4_excl'] = a_records['middles'].apply(lambda x: len(x & regime4_exclusive))

# Records with high convergence
min_convergence = 4

r1_high = a_records[a_records['r1_count'] >= min_convergence].copy()
r4_high = a_records[a_records['r4_count'] >= min_convergence].copy()

print(f"Records with {min_convergence}+ REGIME_1 PP: {len(r1_high)}")
print(f"Records with {min_convergence}+ REGIME_4 PP: {len(r4_high)}")
print()

# Records with EXCLUSIVE PP convergence
r1_excl_high = a_records[a_records['r1_excl'] >= 2]
r4_excl_high = a_records[a_records['r4_excl'] >= 2]

print(f"Records with 2+ REGIME_1-EXCLUSIVE PP: {len(r1_excl_high)}")
print(f"Records with 2+ REGIME_4-EXCLUSIVE PP: {len(r4_excl_high)}")
print()

# =============================================================================
# Key test: Do different regimes converge to DIFFERENT records?
# =============================================================================
print("-" * 70)
print("DISCRIMINATION TEST: Do regimes select different records?")
print("-" * 70)
print()

r1_records = set(r1_high['record_id'])
r4_records = set(r4_high['record_id'])

overlap = r1_records & r4_records
r1_only = r1_records - r4_records
r4_only = r4_records - r1_records

print(f"REGIME_1-converged records: {len(r1_records)}")
print(f"REGIME_4-converged records: {len(r4_records)}")
print(f"Overlap: {len(overlap)}")
print(f"REGIME_1 only: {len(r1_only)}")
print(f"REGIME_4 only: {len(r4_only)}")
print()

if len(r4_only) > 0 or len(r1_only) > 0:
    print("*** RECORDS DISCRIMINATE BY REGIME ***")
    print()

# =============================================================================
# Extract RI from regime-specific records
# =============================================================================
print("-" * 70)
print("RI TOKENS in regime-specific records")
print("-" * 70)
print()

def extract_ri(records_df):
    all_middles = set()
    for _, row in records_df.iterrows():
        all_middles.update(row['middles'])
    return all_middles - b_middles  # RI = not in B

# RI from REGIME_4-only records (should be animal candidates)
if len(r4_only) > 0:
    r4_only_df = a_records[a_records['record_id'].isin(r4_only)]
    r4_ri = extract_ri(r4_only_df)

    print(f"REGIME_4-only records: {len(r4_only_df)}")
    print(f"RI tokens in those records: {len(r4_ri)}")

    # Check against known animal tokens
    animal_middles = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}
    animal_in_r4 = r4_ri & animal_middles

    print(f"Known animal tokens found: {animal_in_r4}")
    print()

    if animal_in_r4:
        print("*** ANIMAL TOKENS IN REGIME_4-SPECIFIC RECORDS ***")
        for rec_id in sorted(r4_only)[:10]:
            rec = a_records[a_records['record_id'] == rec_id].iloc[0]
            rec_ri = rec['middles'] - b_middles
            rec_animal = rec_ri & animal_middles
            if rec_animal:
                print(f"  {rec_id}: RI={rec_ri}, ANIMAL={rec_animal}")

# RI from REGIME_1-only records (should be plant candidates)
if len(r1_only) > 0:
    r1_only_df = a_records[a_records['record_id'].isin(r1_only)]
    r1_ri = extract_ri(r1_only_df)

    print()
    print(f"REGIME_1-only records: {len(r1_only_df)}")
    print(f"RI tokens in those records: {len(r1_ri)}")

    # Check if these are different from animal tokens
    animal_in_r1 = r1_ri & animal_middles
    print(f"Known animal tokens found: {animal_in_r1}")

# =============================================================================
# Higher threshold test
# =============================================================================
print()
print("-" * 70)
print("HIGHER THRESHOLD TEST (5+ PP convergence)")
print("-" * 70)
print()

min_convergence = 5

r1_high5 = set(a_records[a_records['r1_count'] >= min_convergence]['record_id'])
r4_high5 = set(a_records[a_records['r4_count'] >= min_convergence]['record_id'])

overlap5 = r1_high5 & r4_high5
r1_only5 = r1_high5 - r4_high5
r4_only5 = r4_high5 - r1_high5

print(f"REGIME_1-converged (5+): {len(r1_high5)}")
print(f"REGIME_4-converged (5+): {len(r4_high5)}")
print(f"Overlap: {len(overlap5)}")
print(f"REGIME_1 only: {len(r1_only5)}")
print(f"REGIME_4 only: {len(r4_only5)}")

if r4_only5:
    print()
    print("REGIME_4-only records at 5+ threshold:")
    for rec_id in sorted(r4_only5)[:10]:
        rec = a_records[a_records['record_id'] == rec_id].iloc[0]
        rec_ri = rec['middles'] - b_middles
        rec_animal = rec_ri & animal_middles
        r4_matches = rec['middles'] & regime4_pp
        print(f"  {rec_id}: {len(r4_matches)} R4-PP, RI={rec_ri}")
        if rec_animal:
            print(f"    *** ANIMAL: {rec_animal} ***")

# =============================================================================
# VERDICT
# =============================================================================
print()
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

discrimination_ratio = len(r4_only) / len(r4_records) if r4_records else 0
print(f"Record discrimination: {len(r4_only)}/{len(r4_records)} = {discrimination_ratio:.1%} REGIME_4-only")

if discrimination_ratio > 0.3:
    print("RESULT: PP convergence DOES discriminate at record level!")
    print("Different regimes select different A records.")
elif discrimination_ratio > 0.1:
    print("RESULT: Partial discrimination at record level.")
    print("Some regime-specific records exist.")
else:
    print("RESULT: Poor discrimination at record level.")
    print("PP convergence does not select regime-specific records.")
