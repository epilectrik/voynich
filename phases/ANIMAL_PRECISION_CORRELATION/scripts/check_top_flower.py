#!/usr/bin/env python3
"""Check the highest-prior flower tokens directly"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t')
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

# Load regime
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

regime1_folios = set(regime_data.get('REGIME_1', []))
regime2_folios = set(regime_data.get('REGIME_2', []))
rose_regime_folios = regime1_folios | regime2_folios

# Rose PP from REGIME_1/2
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
rose_middles = set()
for folio in rose_regime_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    rose_middles.update(folio_tokens['middle'].dropna().unique())
rose_pp = (rose_middles & shared_middles) - infrastructure

# High-prior flower tokens
top_flowers = {
    'okaro': (0.52, 'f89v2'),
    'ockho': (0.52, 'f3v'),
    'ysho': (0.52, 'f44r'),
    'ota': (0.52, 'unknown'),
    'aram': (0.35, 'f99v'),
}

print("=" * 70)
print("TOP FLOWER TOKENS - Direct Analysis")
print("=" * 70)
print()

for token, (prob, expected_folio) in top_flowers.items():
    print(f"=== {token} (P={prob:.2f}) ===")

    # Find in A
    a_with = df_a[df_a['middle'] == token]
    if len(a_with) == 0:
        print(f"  NOT FOUND in Currier A")
        print()
        continue

    folios = a_with['folio'].unique()
    print(f"  Found in A folios: {list(folios)}")

    # For each occurrence, check record-level PP
    for folio in folios:
        folio_a = a_with[a_with['folio'] == folio]
        for line in folio_a['line_number'].unique():
            record_a = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == line)]
            record_middles = set(record_a['middle'].dropna().unique())

            # PP overlap
            pp_overlap = record_middles & rose_pp
            all_ri = record_middles - b_middles

            print(f"  Record {folio}:{line}:")
            print(f"    All MIDDLEs: {record_middles}")
            print(f"    Rose PP overlap: {len(pp_overlap)} tokens")
            if pp_overlap:
                print(f"    PP tokens: {pp_overlap}")
            print(f"    RI tokens: {all_ri}")
    print()

# Compare with chicken tokens
print("=" * 70)
print("COMPARISON: Chicken tokens (for reference)")
print("=" * 70)
print()

chicken_tokens = {
    'eoschso': (1.00, 'f90r1'),  # Our identified chicken
}

for token, (prob, expected_folio) in chicken_tokens.items():
    a_with = df_a[df_a['middle'] == token]
    if len(a_with) == 0:
        print(f"{token}: NOT FOUND")
        continue

    folios = a_with['folio'].unique()
    print(f"{token} (P(animal)={prob:.2f}):")
    print(f"  In A folios: {list(folios)}")

    for folio in folios:
        folio_a = a_with[a_with['folio'] == folio]
        for line in folio_a['line_number'].unique():
            record_a = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == line)]
            record_middles = set(record_a['middle'].dropna().unique())
            pp_overlap = record_middles & rose_pp
            print(f"  {folio}:{line} - {len(pp_overlap)} rose PP overlap")
