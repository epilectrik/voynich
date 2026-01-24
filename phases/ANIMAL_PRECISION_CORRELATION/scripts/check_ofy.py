#!/usr/bin/env python3
"""Check ofy as frog candidate."""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

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

print("=" * 70)
print("OFY - Frog Candidate Analysis")
print("=" * 70)
print()

ofy = df[df['middle'] == 'ofy']
print(f"Total occurrences: {len(ofy)}")
print()

print("All occurrences:")
for _, row in ofy.iterrows():
    print(f"  {row['folio']}:{row['line_number']} - {row['word']} (lang={row['language']})")
print()

# Check the records where ofy appears
print("-" * 70)
print("Records containing ofy:")
print("-" * 70)

for folio, line in [('f21r', '4'), ('f8r', '14')]:
    record = df[(df['folio'] == folio) & (df['line_number'] == line) & (df['language'] == 'A')]
    if len(record) > 0:
        print(f"\n{folio}:{line}")
        print(f"  Words: {list(record['word'])}")
        print(f"  Total: {len(record)} tokens")
