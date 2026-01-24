#!/usr/bin/env python3
"""Quick check: how many rare MIDDLEs do different REGIME_4 folios have?"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B']

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin', 'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry', 'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en', 'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

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

df_b['middle'] = df_b['word'].apply(extract_middle)
b_counts = df_b['middle'].value_counts()
b_rank = {m: r for r, m in enumerate(b_counts.index, 1)}

print("REGIME_4 folios - rare MIDDLE counts:")
print()
regime4_folios = ['f43v', 'f39v', 'f55r', 'f34r', 'f46v', 'f50r', 'f34v', 'f94r']
for folio in regime4_folios:
    f_middles = set(df_b[df_b['folio'] == folio]['middle'].dropna().unique())
    rare_50 = [m for m in f_middles if b_rank.get(m, 9999) > 50]
    rare_100 = [m for m in f_middles if b_rank.get(m, 9999) > 100]
    print(f'{folio}: total={len(f_middles)}, rank>50={len(rare_50)}, rank>100={len(rare_100)}')
    if rare_100:
        print(f'  rank>100: {rare_100}')
