#!/usr/bin/env python3
"""
Do A records contain both RI types, or one or the other?
"""

import json
import sys
import pandas as pd
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology
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
df_a['middle'] = df_a['word'].apply(extract_middle)

# Classify MIDDLEs
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
ri_counts = ri_tokens['middle'].value_counts()

singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)
long_repeat_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) > 3)

print("="*70)
print("RI TYPE CO-OCCURRENCE IN A RECORDS")
print("="*70)

print(f"\nRI classifications:")
print(f"  Singleton RI: {len(singleton_ri)} types")
print(f"  Boundary RI (short, repeating): {len(boundary_ri)} types")
print(f"  Long repeating RI: {len(long_repeat_ri)} types")

# Build record-level analysis
records = []
for (folio, line), group in df_a.groupby(['folio', 'line_number']):
    middles = set(group['middle'].dropna())

    has_pp = bool(middles & pp_middles)
    has_singleton = bool(middles & singleton_ri)
    has_boundary = bool(middles & boundary_ri)
    has_long_repeat = bool(middles & long_repeat_ri)

    pp_count = len(middles & pp_middles)
    singleton_count = len(middles & singleton_ri)
    boundary_count = len(middles & boundary_ri)

    records.append({
        'key': f"{folio}:{line}",
        'has_pp': has_pp,
        'has_singleton': has_singleton,
        'has_boundary': has_boundary,
        'has_long_repeat': has_long_repeat,
        'pp_count': pp_count,
        'singleton_count': singleton_count,
        'boundary_count': boundary_count,
        'total_middles': len(middles)
    })

records_df = pd.DataFrame(records)

print(f"\nTotal A records: {len(records_df)}")

# RI type combinations
print(f"\n" + "="*70)
print("RI TYPE COMBINATIONS IN RECORDS")
print("="*70)

# Create combination categories
def categorize(row):
    s = row['has_singleton']
    b = row['has_boundary']
    if s and b:
        return 'BOTH'
    elif s:
        return 'SINGLETON_ONLY'
    elif b:
        return 'BOUNDARY_ONLY'
    else:
        return 'NEITHER'

records_df['ri_combo'] = records_df.apply(categorize, axis=1)

combo_counts = records_df['ri_combo'].value_counts()
print(f"\n{'Combination':>20} {'Count':>8} {'%':>8}")
print("-" * 40)
for combo, count in combo_counts.items():
    pct = count / len(records_df) * 100
    print(f"{combo:>20} {count:>8} {pct:>7.1f}%")

# Cross-tabulation
print(f"\n" + "="*70)
print("CROSS-TABULATION: SINGLETON × BOUNDARY")
print("="*70)

crosstab = pd.crosstab(records_df['has_singleton'], records_df['has_boundary'],
                       margins=True, margins_name='Total')
crosstab.index = ['No Singleton', 'Has Singleton', 'Total']
crosstab.columns = ['No Boundary', 'Has Boundary', 'Total']
print(f"\n{crosstab}")

# Calculate expected values for independence test
total = len(records_df)
p_singleton = records_df['has_singleton'].mean()
p_boundary = records_df['has_boundary'].mean()
expected_both = total * p_singleton * p_boundary
actual_both = ((records_df['has_singleton']) & (records_df['has_boundary'])).sum()

print(f"\nIndependence test:")
print(f"  P(singleton) = {p_singleton:.3f}")
print(f"  P(boundary) = {p_boundary:.3f}")
print(f"  Expected BOTH (if independent) = {expected_both:.1f}")
print(f"  Actual BOTH = {actual_both}")
print(f"  Ratio (actual/expected) = {actual_both/expected_both:.2f}")

# Chi-square test
from scipy.stats import chi2_contingency
contingency = [[((~records_df['has_singleton']) & (~records_df['has_boundary'])).sum(),
                ((~records_df['has_singleton']) & (records_df['has_boundary'])).sum()],
               [((records_df['has_singleton']) & (~records_df['has_boundary'])).sum(),
                ((records_df['has_singleton']) & (records_df['has_boundary'])).sum()]]
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(f"  Chi-square = {chi2:.2f}, p = {p_value:.4f}")

# Detailed breakdown by PP presence
print(f"\n" + "="*70)
print("RI PATTERNS BY PP PRESENCE")
print("="*70)

for has_pp in [True, False]:
    subset = records_df[records_df['has_pp'] == has_pp]
    label = "WITH PP" if has_pp else "WITHOUT PP"
    print(f"\nRecords {label}: {len(subset)}")

    combo_sub = subset['ri_combo'].value_counts()
    for combo, count in combo_sub.items():
        pct = count / len(subset) * 100
        print(f"  {combo}: {count} ({pct:.1f}%)")

# Average counts
print(f"\n" + "="*70)
print("AVERAGE COUNTS PER RECORD")
print("="*70)

for combo in ['BOTH', 'SINGLETON_ONLY', 'BOUNDARY_ONLY', 'NEITHER']:
    subset = records_df[records_df['ri_combo'] == combo]
    if len(subset) > 0:
        print(f"\n{combo} records ({len(subset)}):")
        print(f"  Mean PP count: {subset['pp_count'].mean():.2f}")
        print(f"  Mean singleton count: {subset['singleton_count'].mean():.2f}")
        print(f"  Mean boundary count: {subset['boundary_count'].mean():.2f}")
        print(f"  Mean total MIDDLEs: {subset['total_middles'].mean():.2f}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if actual_both / expected_both > 1.2:
    print(f"""
POSITIVE ASSOCIATION: Singleton and boundary RI CLUSTER together.

Records with one type are MORE likely to have the other.
Ratio = {actual_both/expected_both:.2f}x expected (p={p_value:.4f})

This suggests:
- Complex A records use BOTH RI types
- Singleton (unique ID) + Boundary (type marker) = full entry
- They serve complementary functions
""")
elif actual_both / expected_both < 0.8:
    print(f"""
NEGATIVE ASSOCIATION: Singleton and boundary RI are MUTUALLY EXCLUSIVE.

Records with one type are LESS likely to have the other.
Ratio = {actual_both/expected_both:.2f}x expected (p={p_value:.4f})

This suggests:
- Two different TYPES of A records
- Type 1: Uses singleton RI (unique identifier entries)
- Type 2: Uses boundary RI (category marker entries)
""")
else:
    print(f"""
NO CLEAR PATTERN: Singleton and boundary RI are INDEPENDENT.

Ratio = {actual_both/expected_both:.2f}x expected (p={p_value:.4f})

The two RI types appear in records independently of each other.
No evidence of complementary or exclusive relationship.
""")
