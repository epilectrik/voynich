#!/usr/bin/env python3
"""
Check RI vs PP MIDDLE distribution within A records.

Hypothesis: A records contain both:
- RI MIDDLEs (identity - stays in A)
- PP MIDDLEs (properties - propagates to constrain B)

Questions:
1. What fraction of A records have RI MIDDLEs?
2. What fraction have PP MIDDLEs?
3. What fraction have BOTH?
4. What fraction have ONLY one type?
"""

import json
import pandas as pd
from collections import defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Filter to Currier A
df_a = df[df['language'] == 'A'].copy()
print(f"Currier A tokens: {len(df_a)}")

# Load the A MIDDLE stratification data
# We need to know which MIDDLEs are RI vs PP (AZC-Mediated vs B-Native)

# From C498.a, we know:
# - RI (Registry-Internal): 349 MIDDLEs, A-exclusive
# - AZC-Mediated: 154 MIDDLEs (go through AZC)
# - B-Native Overlap: 114 MIDDLEs (in A and B, not AZC)

# Let me load the actual classification if available
# Otherwise compute from first principles

# Load survivors data which has middle info
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

# Get all unique MIDDLEs from A records
all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

print(f"Unique MIDDLEs across all A records: {len(all_a_middles)}")

# We need to classify MIDDLEs as RI vs PP
# RI = appears in A but NOT in B
# PP = appears in both A and B

# Load B token data to identify which MIDDLEs appear in B
df_b = df[df['language'] == 'B'].copy()

# Load class token map for MIDDLE extraction
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']

# Get all MIDDLEs that appear in B
b_middles = set()
for token in df_b['word'].unique():
    if token in token_to_middle:
        m = token_to_middle[token]
        if m:  # Some are None (atomic)
            b_middles.add(m)

print(f"Unique MIDDLEs in Currier B: {len(b_middles)}")

# Classify A MIDDLEs
ri_middles = all_a_middles - b_middles  # In A but not B
pp_middles = all_a_middles & b_middles  # In both A and B

print(f"\nRI MIDDLEs (A-exclusive): {len(ri_middles)}")
print(f"PP MIDDLEs (shared with B): {len(pp_middles)}")

# Now analyze each A record
print("\n" + "="*60)
print("A RECORD COMPOSITION ANALYSIS")
print("="*60)

ri_only = 0
pp_only = 0
both = 0
neither = 0

ri_counts = []
pp_counts = []

for rec in records:
    middles = set(rec['a_middles'])

    has_ri = bool(middles & ri_middles)
    has_pp = bool(middles & pp_middles)

    ri_count = len(middles & ri_middles)
    pp_count = len(middles & pp_middles)

    ri_counts.append(ri_count)
    pp_counts.append(pp_count)

    if has_ri and has_pp:
        both += 1
    elif has_ri:
        ri_only += 1
    elif has_pp:
        pp_only += 1
    else:
        neither += 1

n = len(records)
print(f"\nTotal A records: {n}")
print(f"\nRecord composition:")
print(f"  BOTH RI and PP:  {both:4d} ({100*both/n:.1f}%)")
print(f"  RI only:         {ri_only:4d} ({100*ri_only/n:.1f}%)")
print(f"  PP only:         {pp_only:4d} ({100*pp_only/n:.1f}%)")
print(f"  Neither:         {neither:4d} ({100*neither/n:.1f}%)")

print(f"\nMean RI MIDDLEs per record: {sum(ri_counts)/n:.2f}")
print(f"Mean PP MIDDLEs per record: {sum(pp_counts)/n:.2f}")

# Distribution of counts
print(f"\nRI MIDDLE count distribution:")
from collections import Counter
ri_dist = Counter(ri_counts)
for count in sorted(ri_dist.keys())[:10]:
    pct = 100 * ri_dist[count] / n
    print(f"  {count} RI MIDDLEs: {ri_dist[count]:4d} records ({pct:.1f}%)")

print(f"\nPP MIDDLE count distribution:")
pp_dist = Counter(pp_counts)
for count in sorted(pp_dist.keys())[:10]:
    pct = 100 * pp_dist[count] / n
    print(f"  {count} PP MIDDLEs: {pp_dist[count]:4d} records ({pct:.1f}%)")

# ============================================================
# KEY TEST: Do PP MIDDLEs actually predict B class survival?
# ============================================================
print("\n" + "="*60)
print("KEY TEST: PP MIDDLEs -> B CLASS SURVIVAL")
print("="*60)

# For records with PP MIDDLEs, check if those MIDDLEs match surviving class requirements
print("\nIf PP = properties that propagate, then:")
print("  Records with more PP MIDDLEs should have more surviving B classes")

# Correlate PP count with surviving class count
import numpy as np
surviving_counts = [rec['surviving_class_count'] for rec in records]

corr = np.corrcoef(pp_counts, surviving_counts)[0,1]
print(f"\nCorrelation(PP_count, surviving_classes) = {corr:.3f}")

# Also check RI correlation (should be weaker if RI doesn't propagate)
corr_ri = np.corrcoef(ri_counts, surviving_counts)[0,1]
print(f"Correlation(RI_count, surviving_classes) = {corr_ri:.3f}")

# ============================================================
# EXAMPLE RECORDS
# ============================================================
print("\n" + "="*60)
print("EXAMPLE A RECORDS")
print("="*60)

# Show some records with both RI and PP
print("\nRecords with BOTH RI and PP (first 5):")
count = 0
for rec in records:
    middles = set(rec['a_middles'])
    ri = middles & ri_middles
    pp = middles & pp_middles
    if ri and pp:
        print(f"\n  {rec['a_record']}:")
        print(f"    RI MIDDLEs: {sorted(ri)[:5]}{'...' if len(ri) > 5 else ''}")
        print(f"    PP MIDDLEs: {sorted(pp)[:5]}{'...' if len(pp) > 5 else ''}")
        print(f"    Surviving classes: {rec['surviving_class_count']}")
        count += 1
        if count >= 5:
            break

# Show PP-only records
print("\nRecords with PP only (no RI) - first 5:")
count = 0
for rec in records:
    middles = set(rec['a_middles'])
    ri = middles & ri_middles
    pp = middles & pp_middles
    if pp and not ri:
        print(f"\n  {rec['a_record']}:")
        print(f"    PP MIDDLEs: {sorted(pp)[:5]}{'...' if len(pp) > 5 else ''}")
        print(f"    Surviving classes: {rec['surviving_class_count']}")
        count += 1
        if count >= 5:
            break

# Show RI-only records
print("\nRecords with RI only (no PP) - first 5:")
count = 0
for rec in records:
    middles = set(rec['a_middles'])
    ri = middles & ri_middles
    pp = middles & pp_middles
    if ri and not pp:
        print(f"\n  {rec['a_record']}:")
        print(f"    RI MIDDLEs: {sorted(ri)[:5]}{'...' if len(ri) > 5 else ''}")
        print(f"    Surviving classes: {rec['surviving_class_count']}")
        count += 1
        if count >= 5:
            break

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\nRI MIDDLEs (identity): {len(ri_middles)} types")
print(f"PP MIDDLEs (properties): {len(pp_middles)} types")
print(f"\nRecords with BOTH: {both} ({100*both/n:.1f}%)")
print(f"Records with PP only: {pp_only} ({100*pp_only/n:.1f}%)")
print(f"Records with RI only: {ri_only} ({100*ri_only/n:.1f}%)")
print(f"\nPP->survival correlation: {corr:.3f}")
print(f"RI->survival correlation: {corr_ri:.3f}")
