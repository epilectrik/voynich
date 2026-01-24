#!/usr/bin/env python3
"""
Verify C504: Does PP MIDDLE COUNT correlate with B class survival count?

C504 claims r=0.772 correlation between PP count and class survival.
"""

import json
import numpy as np
from scipy import stats

# Load A records survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json', encoding='utf-8') as f:
    survivors = json.load(f)

# Define PP MIDDLEs (shared between A and B)
# From the previous analysis: 283 shared MIDDLEs
# But we'll compute it more precisely by checking what's truly shared

# Load class map to get B MIDDLEs
import pandas as pd
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']

# Get B MIDDLEs
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

df_b = df[(df['language'] == 'B') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()
df_b['middle'] = df_b['word'].apply(extract_middle)
b_middles = set(df_b['middle'].dropna().unique())

print("=" * 70)
print("C504 VERIFICATION: PP COUNT vs B CLASS SURVIVAL")
print("=" * 70)
print(f"\nB MIDDLEs: {len(b_middles)}")

# For each A record, compute PP count (MIDDLEs shared with B) and class survival count
pp_counts = []
class_counts = []

for record_data in survivors['records']:
    a_middles = set(record_data['a_middles'])
    pp_count = len(a_middles & b_middles)  # MIDDLEs shared with B
    class_count = record_data['surviving_class_count']

    pp_counts.append(pp_count)
    class_counts.append(class_count)

pp_counts = np.array(pp_counts)
class_counts = np.array(class_counts)

# Compute correlation
r, p = stats.pearsonr(pp_counts, class_counts)

print(f"\nRecords analyzed: {len(pp_counts)}")
print(f"\nPP count range: {pp_counts.min()} - {pp_counts.max()}")
print(f"Class survival range: {class_counts.min()} - {class_counts.max()}")

print(f"\n{'=' * 50}")
print(f"CORRELATION: r = {r:.4f}, p = {p:.2e}")
print(f"{'=' * 50}")

if abs(r - 0.772) < 0.1:
    print(f"\n--> CONFIRMS C504: r ~ 0.772")
else:
    print(f"\n--> DIFFERS FROM C504 (claimed r=0.772)")

# Additional: Correlation with RI count (should be ~0)
ri_counts = []
for record_data in survivors['records']:
    a_middles = set(record_data['a_middles'])
    ri_count = len(a_middles - b_middles)  # MIDDLEs NOT shared with B (RI only)
    ri_counts.append(ri_count)

ri_counts = np.array(ri_counts)
r_ri, p_ri = stats.pearsonr(ri_counts, class_counts)

print(f"\nRI count (A-only MIDDLEs) vs class survival:")
print(f"  r = {r_ri:.4f}, p = {p_ri:.2e}")
print(f"  (Expected: ~0 per C504)")

# Breakdown by PP count buckets
print("\n" + "-" * 50)
print("CLASS SURVIVAL BY PP COUNT BUCKET")
print("-" * 50)

buckets = [(0, 2), (3, 5), (6, 8), (9, 11), (12, 15)]
for low, high in buckets:
    mask = (pp_counts >= low) & (pp_counts <= high)
    if mask.sum() > 0:
        mean_class = class_counts[mask].mean()
        std_class = class_counts[mask].std()
        n = mask.sum()
        print(f"  PP {low}-{high}: {mean_class:.1f} +/- {std_class:.1f} classes (n={n})")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"PP COUNT -> Class survival: r = {r:.3f} (C504 claimed r=0.772)")
print(f"RI COUNT -> Class survival: r = {r_ri:.3f} (C504 claimed ~0)")
