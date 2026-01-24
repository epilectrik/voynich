#!/usr/bin/env python3
"""
Find tokens by MIDDLE component.
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
print("SEARCHING FOR RI MIDDLES IN A RECORDS")
print("="*60)

# The validated identifications mention these as RI MIDDLEs
target_middles = ['eoschso', 'eyd', 'ofy', 'tchyf', 'opcho', 'eoc', 'eso',
                  'keolo', 'teold', 'chald']

for middle in target_middles:
    matches = df_a[df_a['middle'] == middle]
    if len(matches) > 0:
        print(f"\nMIDDLE '{middle}' found in A:")
        for _, row in matches.iterrows():
            record_tokens = df_a[(df_a['folio'] == row['folio']) & (df_a['line'] == row['line'])]
            all_middles = set(record_tokens['middle'].dropna())
            pp = all_middles & pp_middles
            ri = all_middles - b_middles
            print(f"  {row['folio']}:{row['line']}")
            print(f"    Token: {row['word']}")
            print(f"    PP in record: {pp}")
            print(f"    RI in record: {ri}")

# Also check which middles are RI (A-exclusive)
print("\n" + "="*60)
print("ALL A-EXCLUSIVE MIDDLES (RI)")
print("="*60)

ri_middles = a_middles - b_middles
print(f"Total RI MIDDLEs: {len(ri_middles)}")
print(f"RI MIDDLEs: {sorted(ri_middles)}")

# Check if eoschso, keolo are actually RI
print("\n\nVerifying target MIDDLEs:")
for m in target_middles:
    in_a = m in a_middles
    in_b = m in b_middles
    is_ri = m in ri_middles
    print(f"  {m}: in_A={in_a}, in_B={in_b}, is_RI={is_ri}")
