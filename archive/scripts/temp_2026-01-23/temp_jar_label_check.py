#!/usr/bin/env python3
"""Check if jar labels specifically appear in Currier A."""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_text = df[~df['placement'].str.startswith('L', na=False)]

a_tokens = set(df_text[df_text['language'] == 'A']['word'].dropna().unique())
b_tokens = set(df_text[df_text['language'] == 'B']['word'].dropna().unique())
pp_tokens = a_tokens & b_tokens
ri_tokens = a_tokens - b_tokens

# Load jar labels specifically
pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
jar_labels = set()

for json_file in pharma_dir.glob('*_mapping.json'):
    with open(json_file) as f:
        data = json.load(f)

    if 'groups' in data:
        for group in data['groups']:
            jar = group.get('jar')
            if jar and isinstance(jar, str):
                jar_labels.add(jar)

print('JAR LABELS (container identifiers):')
print(f'Total unique jar labels: {len(jar_labels)}')
print(f'Jar labels: {sorted(jar_labels)}')

print()
jars_in_a = jar_labels & a_tokens
jars_in_pp = jar_labels & pp_tokens
jars_in_ri = jar_labels & ri_tokens
jars_in_b_only = jar_labels & (b_tokens - a_tokens)
jars_not_in_text = jar_labels - a_tokens - b_tokens

print(f'In Currier A: {len(jars_in_a)}')
if jars_in_a:
    print(f'  Tokens: {sorted(jars_in_a)}')
print(f'  - As PP: {len(jars_in_pp)}')
if jars_in_pp:
    print(f'    Tokens: {sorted(jars_in_pp)}')
print(f'  - As RI: {len(jars_in_ri)}')
if jars_in_ri:
    print(f'    Tokens: {sorted(jars_in_ri)}')
print(f'In B only: {len(jars_in_b_only)}')
if jars_in_b_only:
    print(f'  Tokens: {sorted(jars_in_b_only)}')
print(f'NOT in text at all: {len(jars_not_in_text)}')
if jars_not_in_text:
    print(f'  Tokens: {sorted(jars_not_in_text)}')

# Summary
print()
print('SUMMARY:')
print(f'  Jar labels in running text: {len(jars_in_a)}/{len(jar_labels)} = {100*len(jars_in_a)/len(jar_labels):.1f}%')
print(f'  Jar labels NOT in running text: {len(jars_not_in_text)}/{len(jar_labels)} = {100*len(jars_not_in_text)/len(jar_labels):.1f}%')

# Check AZC and Currier B
print()
print('=' * 50)
print('CHECKING AZC AND CURRIER B')
print('=' * 50)

# AZC tokens (language = NA, which means AZC sections)
azc_tokens = set(df_text[df_text['language'].isna() | (df_text['language'] == 'NA')]['word'].dropna().unique())
# Also check the placement-based AZC (R, C, S prefixes)
df_azc_placement = df[df['placement'].str.match(r'^[RCS]', na=False)]
azc_tokens_placement = set(df_azc_placement['word'].dropna().unique())
azc_tokens = azc_tokens | azc_tokens_placement

print(f'AZC vocabulary size: {len(azc_tokens)}')

jars_in_azc = jar_labels & azc_tokens
print(f'Jar labels in AZC: {len(jars_in_azc)}')
if jars_in_azc:
    print(f'  Tokens: {sorted(jars_in_azc)}')

# Currier B specifically
print(f'Currier B vocabulary size: {len(b_tokens)}')

jars_in_b = jar_labels & b_tokens
print(f'Jar labels in Currier B: {len(jars_in_b)}')
if jars_in_b:
    print(f'  Tokens: {sorted(jars_in_b)}')

# Check all systems
all_text_tokens = a_tokens | b_tokens | azc_tokens
jars_anywhere = jar_labels & all_text_tokens
jars_nowhere = jar_labels - all_text_tokens

print()
print('FINAL SUMMARY:')
print(f'  Jar labels found ANYWHERE in text: {len(jars_anywhere)}/{len(jar_labels)}')
if jars_anywhere:
    print(f'    Tokens: {sorted(jars_anywhere)}')
print(f'  Jar labels found NOWHERE in text: {len(jars_nowhere)}/{len(jar_labels)}')
if jars_nowhere:
    print(f'    Tokens: {sorted(jars_nowhere)}')
