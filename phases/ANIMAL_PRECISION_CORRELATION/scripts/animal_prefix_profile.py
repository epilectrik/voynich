#!/usr/bin/env python3
"""
Check which animal A records have PP connecting to chicken-specific PREFIX profile.

Chicken profile: high qo (e_ESCAPE), high ok/ot (AUX), LOW da (no FLOW)
Other animals: scharlach/charlach/milch have FLOW (da) operations
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t')
df = df[df['transcriber'] == 'H']
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

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

df_b['middle'] = df_b['word'].apply(extract_middle)
df_b['prefix'] = df_b['word'].apply(extract_prefix)

# For each PP MIDDLE, compute its PREFIX distribution in B
# This tells us what operations use that MIDDLE

pp_middles = ['t', 'd', 'ckh', 'eod', 'fch', 'ch', 'l', 'k', 'ke', 'keo', 'i']

print("=" * 70)
print("PP MIDDLE -> PREFIX distribution in B")
print("=" * 70)
print()
print("Instruction mapping:")
print("  qo = e_ESCAPE (recovery)")
print("  ok/ot = AUX (auxiliary)")
print("  da = FLOW (direct action)")
print()

for middle in pp_middles:
    b_tokens = df_b[df_b['middle'] == middle]
    if len(b_tokens) == 0:
        print(f"{middle}: NOT IN B")
        continue

    prefix_counts = b_tokens['prefix'].value_counts()
    total = len(b_tokens)

    # Key ratios
    qo = prefix_counts.get('qo', 0)
    ok = prefix_counts.get('ok', 0)
    ot = prefix_counts.get('ot', 0)
    da = prefix_counts.get('da', 0)

    escape_ratio = qo / total
    aux_ratio = (ok + ot) / total
    flow_ratio = da / total

    chicken_score = escape_ratio + aux_ratio - flow_ratio  # Higher = more chicken-like

    print(f"{middle}: n={total}")
    print(f"  qo(ESCAPE)={qo} ({escape_ratio:.1%}), ok+ot(AUX)={ok+ot} ({aux_ratio:.1%}), da(FLOW)={da} ({flow_ratio:.1%})")
    print(f"  Chicken score (ESCAPE+AUX-FLOW): {chicken_score:.2f}")
    print()

# Now map each animal record by its unique PP's chicken score
print()
print("=" * 70)
print("ANIMAL RECORDS ranked by chicken-score of unique PP")
print("=" * 70)
print()

animal_unique_pp = {
    'teold': ['t'],
    'eyd': ['d', 'ckh', 'eod'],
    'chald': ['fch'],
    'eoschso': ['ch', 'l'],
}

for animal, unique_pp in animal_unique_pp.items():
    total_score = 0
    n_valid = 0
    for middle in unique_pp:
        b_tokens = df_b[df_b['middle'] == middle]
        if len(b_tokens) == 0:
            continue
        prefix_counts = b_tokens['prefix'].value_counts()
        total = len(b_tokens)
        qo = prefix_counts.get('qo', 0)
        ok = prefix_counts.get('ok', 0)
        ot = prefix_counts.get('ot', 0)
        da = prefix_counts.get('da', 0)
        score = (qo + ok + ot - da) / total
        total_score += score
        n_valid += 1

    avg_score = total_score / n_valid if n_valid > 0 else 0
    print(f"{animal}: avg chicken score = {avg_score:.2f} (from {unique_pp})")
