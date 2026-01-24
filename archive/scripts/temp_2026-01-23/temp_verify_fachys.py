#!/usr/bin/env python3
"""Verify 'fachys' is singleton RI-D"""

import pandas as pd
from pathlib import Path

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A']

# Count occurrences of 'fachys'
fachys_count = (df_a['word'] == 'fachys').sum()
print(f"'fachys' appears {fachys_count} time(s) in Currier A")

# Where does it appear?
fachys_rows = df_a[df_a['word'] == 'fachys'][['folio', 'line_number', 'placement']]
print(fachys_rows.to_string())

# Check a few other section markers
markers = ['fachys', 'kodalchy', 'tydlo', 'fochof', 'polyshy']
print("\n--- Section marker frequencies ---")
for m in markers:
    count = (df_a['word'] == m).sum()
    print(f"  '{m}': {count}")

# Check a few boundary RI (should repeat)
boundary_examples = ['sh', 'ko', 'och', 'cfh', 'tsh']
print("\n--- Boundary RI frequencies ---")

# Need to extract MIDDLEs first
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None

df_a['middle'] = df_a['word'].apply(extract_middle)

# Check middle frequencies for boundary examples
middle_counts = df_a['middle'].value_counts()
for m in boundary_examples:
    count = middle_counts.get(m, 0)
    print(f"  MIDDLE '{m}': {count}")
