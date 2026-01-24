#!/usr/bin/env python3
"""
Verify: If MIDDLE is unique (RI-D), is the whole TOKEN also unique?
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('.')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
    if not token.strip():
        return None, None, None
    prefix = None
    suffix = None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            prefix = p
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break
    middle = remainder if remainder else None
    return prefix, middle, suffix

# Load PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load A tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

# Extract morphology
morph = df_a['word'].apply(extract_morphology)
df_a['prefix'] = morph.apply(lambda x: x[0])
df_a['middle'] = morph.apply(lambda x: x[1])
df_a['suffix'] = morph.apply(lambda x: x[2])

# Get RI MIDDLEs (A-exclusive)
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
middle_counts = ri_tokens['middle'].value_counts()
singleton_middles = set(m for m, c in middle_counts.items() if c == 1)

print("="*70)
print("RI-D TOKEN vs MIDDLE UNIQUENESS")
print("="*70)

print(f"\nTotal singleton MIDDLEs (RI-D): {len(singleton_middles)}")

# For each singleton MIDDLE, how many different TOKENS contain it?
singleton_tokens = df_a[df_a['middle'].isin(singleton_middles)]

# Group by MIDDLE and count unique tokens
middle_to_tokens = singleton_tokens.groupby('middle')['word'].apply(lambda x: list(x.unique())).to_dict()

# Check if any singleton MIDDLE appears in multiple token forms
multi_token_middles = {m: tokens for m, tokens in middle_to_tokens.items() if len(tokens) > 1}

print(f"Singleton MIDDLEs that appear in multiple TOKEN forms: {len(multi_token_middles)}")

if multi_token_middles:
    print("\nExamples of singleton MIDDLEs with multiple token forms:")
    for m, tokens in list(multi_token_middles.items())[:10]:
        print(f"  MIDDLE '{m}': {tokens}")
else:
    print("\nAll singleton MIDDLEs appear in exactly ONE token form.")
    print("RI-D MIDDLE uniqueness = TOKEN uniqueness")

# Let's also check: are the TOKENS themselves unique?
singleton_token_words = singleton_tokens['word'].tolist()
token_counts = Counter(singleton_token_words)
repeated_tokens = {t: c for t, c in token_counts.items() if c > 1}

print(f"\n" + "="*70)
print("TOKEN-LEVEL UNIQUENESS")
print("="*70)

print(f"\nTotal tokens with singleton MIDDLEs: {len(singleton_token_words)}")
print(f"Unique token types: {len(set(singleton_token_words))}")
print(f"Tokens that repeat (same word appears twice): {len(repeated_tokens)}")

if repeated_tokens:
    print("\nTokens that appear more than once (but have singleton MIDDLE?):")
    for t, c in list(repeated_tokens.items())[:10]:
        # Get the MIDDLE for this token
        m = df_a[df_a['word'] == t]['middle'].iloc[0]
        print(f"  '{t}' (MIDDLE='{m}'): appears {c} times")
        # This would be strange - how can a singleton MIDDLE's token appear twice?

# Show some examples of RI-D tokens
print(f"\n" + "="*70)
print("SAMPLE RI-D TOKENS (first 20)")
print("="*70)

sample = singleton_tokens.head(20)[['word', 'prefix', 'middle', 'suffix', 'folio']].drop_duplicates()
print(f"\n{'Token':<20} {'PREFIX':<8} {'MIDDLE':<15} {'SUFFIX':<8} {'Folio':<10}")
print("-" * 65)
for _, row in sample.iterrows():
    p = row['prefix'] if row['prefix'] else '-'
    m = row['middle'] if row['middle'] else '-'
    s = row['suffix'] if row['suffix'] else '-'
    print(f"{row['word']:<20} {p:<8} {m:<15} {s:<8} {row['folio']:<10}")

# Check fachys specifically
print(f"\n" + "="*70)
print("'FACHYS' BREAKDOWN")
print("="*70)
fachys_morph = extract_morphology('fachys')
print(f"\nToken: 'fachys'")
print(f"  PREFIX: {fachys_morph[0]}")
print(f"  MIDDLE: {fachys_morph[1]}")
print(f"  SUFFIX: {fachys_morph[2]}")

fachys_middle = fachys_morph[1]
if fachys_middle in singleton_middles:
    print(f"\n  MIDDLE '{fachys_middle}' is RI-D (singleton)")
else:
    print(f"\n  MIDDLE '{fachys_middle}' is NOT a singleton")
