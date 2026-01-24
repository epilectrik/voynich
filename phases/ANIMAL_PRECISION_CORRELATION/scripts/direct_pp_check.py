#!/usr/bin/env python3
"""
Direct PP overlap check for flower vs animal lines.
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

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

b_middles = set(df_b['middle'].dropna().unique())
a_middles = set(df_a['middle'].dropna().unique())
shared = a_middles & b_middles

# Load regime
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Get PP for different regimes
regime1_folios = set(regime_data.get('REGIME_1', []))
regime4_folios = set(regime_data.get('REGIME_4', []))

def get_regime_pp(folios):
    middles = set()
    for folio in folios:
        folio_tokens = df_b[df_b['folio'] == folio]
        middles.update(folio_tokens['middle'].dropna().unique())
    return (middles & shared) - infrastructure

r1_pp = get_regime_pp(regime1_folios)
r4_pp = get_regime_pp(regime4_folios)

print("=" * 70)
print("DIRECT PP COMPARISON: Flower vs Animal lines")
print("=" * 70)
print()

# Check specific lines
lines_to_check = [
    ('FLOWER', 'okaro', 'f89v2', 3, 'REGIME_1'),
    ('FLOWER', 'ockho', 'f3v', 11, 'REGIME_1'),
    ('FLOWER', 'ysho', 'f44r', 5, 'REGIME_1'),
    ('ANIMAL', 'eoschso', 'f90r1', 6, 'REGIME_4'),
    ('ANIMAL', 'eyd', 'f89r2', 1, 'REGIME_4'),
    ('ANIMAL', 'chald', 'f23r', 4, 'REGIME_4'),
]

print(f"REGIME_1 PP vocabulary: {len(r1_pp)} tokens")
print(f"REGIME_4 PP vocabulary: {len(r4_pp)} tokens")
print()

for material_type, token, folio, line, expected_regime in lines_to_check:
    line_df = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == str(line))]
    line_middles = set(line_df['middle'].dropna().unique()) - infrastructure
    line_ri = line_middles - b_middles
    line_pp = line_middles & shared

    # PP overlap with each regime
    r1_overlap = line_pp & r1_pp
    r4_overlap = line_pp & r4_pp

    print(f"{material_type}: {token} in {folio}:{line}")
    print(f"  Total MIDDLEs: {len(line_middles)}")
    print(f"  PP tokens: {len(line_pp)}")
    print(f"  RI tokens: {len(line_ri)}")
    print(f"  REGIME_1 PP overlap: {len(r1_overlap)}")
    print(f"  REGIME_4 PP overlap: {len(r4_overlap)}")
    print(f"  PP tokens: {sorted(line_pp)[:10]}")
    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

flower_pp_counts = []
animal_pp_counts = []

for material_type, token, folio, line, expected_regime in lines_to_check:
    line_df = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == str(line))]
    line_middles = set(line_df['middle'].dropna().unique()) - infrastructure
    line_pp = line_middles & shared

    if material_type == 'FLOWER':
        flower_pp_counts.append(len(line_pp))
    else:
        animal_pp_counts.append(len(line_pp))

print(f"FLOWER lines avg PP: {sum(flower_pp_counts)/len(flower_pp_counts):.1f}")
print(f"ANIMAL lines avg PP: {sum(animal_pp_counts)/len(animal_pp_counts):.1f}")
