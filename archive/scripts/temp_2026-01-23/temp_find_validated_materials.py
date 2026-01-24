#!/usr/bin/env python3
"""
Find validated material tokens in A records and get their PP profiles.
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)
token_to_middle = class_map['token_to_middle']

df['middle'] = df['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Identify PP MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
pp_middles = a_middles & b_middles

print("="*60)
print("FINDING VALIDATED MATERIAL TOKENS")
print("="*60)

# Search for known animal tokens in A records
animal_tokens = ['eoschso', 'eyd', 'ofy', 'tchyf', 'opcho', 'eoc', 'eso',
                 'olfcho', 'cthso', 'hdaoto', 'teold', 'chald', 'keolo']

for token in animal_tokens:
    matches = df_a[df_a['word'] == token]
    if len(matches) > 0:
        print(f"\n{token}:")
        for _, row in matches.iterrows():
            print(f"  {row['folio']}:{row['line']} - {row['word']}")

            # Get all tokens in that record
            record_tokens = df_a[(df_a['folio'] == row['folio']) & (df_a['line'] == row['line'])]
            all_tokens = list(record_tokens['word'])
            all_middles = set(record_tokens['middle'].dropna())
            pp = all_middles & pp_middles
            ri = all_middles - b_middles
            print(f"    Tokens: {all_tokens}")
            print(f"    PP MIDDLEs: {pp}")
            print(f"    RI MIDDLEs: {ri}")

# Also search by MIDDLE
print("\n" + "="*60)
print("SEARCHING BY MIDDLE (RI tokens)")
print("="*60)

# Get RI MIDDLEs with 100% animal prior
animal_ri_middles = ['eyd', 'tchyf', 'ofy', 'opcho', 'eoc', 'eso',
                     'olfcho', 'cthso', 'hdaoto']

for middle in animal_ri_middles:
    matches = df_a[df_a['middle'] == middle]
    if len(matches) > 0:
        print(f"\nMIDDLE '{middle}':")
        for _, row in matches.iterrows():
            record_tokens = df_a[(df_a['folio'] == row['folio']) & (df_a['line'] == row['line'])]
            all_middles = set(record_tokens['middle'].dropna())
            pp = all_middles & pp_middles
            ri = all_middles - b_middles
            print(f"  {row['folio']}:{row['line']} - PP={pp}")
