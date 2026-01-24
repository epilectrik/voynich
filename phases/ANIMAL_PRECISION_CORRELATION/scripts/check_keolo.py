#!/usr/bin/env python3
"""Check keolo as thyme candidate."""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

print("=" * 70)
print("KEOLO ANALYSIS - Thyme candidate")
print("=" * 70)
print()

# Find all occurrences of keolo
# Need to check which words contain 'keolo' as a middle
PREFIXES = ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh', 'ct', 'pch', 'tch', 'kch', 'dch',
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

df['middle'] = df['word'].apply(extract_middle)

# Find keolo
keolo_df = df[df['middle'] == 'keolo']
print(f"Total occurrences of keolo: {len(keolo_df)}")
print()

print("Occurrences:")
for _, row in keolo_df.iterrows():
    print(f"  {row['folio']}:{row['line_number']} - {row['word']} (lang={row['language']})")
print()

# Check the record f99v:7 in detail
print("-" * 70)
print("RECORD f99v:7 (where keolo appears)")
print("-" * 70)
print()

record = df[(df['folio'] == 'f99v') & (df['line_number'] == '7')]
print(f"Total tokens: {len(record)}")
print()

# Show by language
for lang in ['A', 'B']:
    lang_df = record[record['language'] == lang]
    if len(lang_df) > 0:
        print(f"Language {lang}: {len(lang_df)} tokens")
        words = list(lang_df['word'])
        print(f"  Words: {words}")
        print()

# PREFIX profile of the A side
a_record = record[record['language'] == 'A']

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

a_record = a_record.copy()
a_record['prefix'] = a_record['word'].apply(extract_prefix)
prefix_counts = a_record['prefix'].value_counts()

print("PREFIX profile of f99v:7 (A side):")
for p in ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh']:
    count = prefix_counts.get(p, 0)
    print(f"  {p}: {count}")
print()

# Also check 'ho' for comparison
print("=" * 70)
print("HO ANALYSIS - Alternative thyme candidate")
print("=" * 70)
print()

ho_df = df[df['middle'] == 'ho']
print(f"Total occurrences of 'ho': {len(ho_df)}")
print()

# Group by language
ho_by_lang = ho_df.groupby('language').size()
print("By language:")
print(ho_by_lang)
print()

# Check A occurrences
ho_a = ho_df[ho_df['language'] == 'A']
print(f"A occurrences: {len(ho_a)}")
if len(ho_a) > 0:
    for _, row in ho_a.head(10).iterrows():
        print(f"  {row['folio']}:{row['line_number']} - {row['word']}")
