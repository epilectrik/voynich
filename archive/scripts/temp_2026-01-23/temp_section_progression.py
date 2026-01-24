#!/usr/bin/env python3
"""
Do A records change systematically within singleton RI sections?

Check:
1. PP count progression (start vs middle vs end of section)
2. Boundary RI usage progression
3. PREFIX changes within sections
4. Record length changes
"""

import json
import sys
import pandas as pd
import numpy as np
from collections import defaultdict
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

# Classify RI
ri_counts = df_a[df_a['middle'].notna() & ~df_a['middle'].isin(pp_middles)]['middle'].value_counts()
singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)

# Sort folios
def folio_sort_key(f):
    import re
    match = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)

# Get folio-first tokens
df_a_sorted = df_a.sort_values(['folio', 'line_number', 'placement'])
folio_first = df_a_sorted.groupby('folio').first().reset_index()
folio_first['sort_key'] = folio_first['folio'].apply(folio_sort_key)
folio_first = folio_first.sort_values('sort_key')
folio_first['is_singleton_start'] = folio_first['middle'].isin(singleton_ri)

# Build sections (runs of folios after each singleton marker)
sections = []
current_section = None
folio_order = folio_first['folio'].tolist()

for folio in folio_order:
    is_start = folio_first[folio_first['folio'] == folio]['is_singleton_start'].iloc[0]
    if is_start:
        if current_section:
            sections.append(current_section)
        marker_token = folio_first[folio_first['folio'] == folio]['word'].iloc[0]
        current_section = {'marker': marker_token, 'folios': [folio]}
    elif current_section:
        current_section['folios'].append(folio)

if current_section:
    sections.append(current_section)

# Filter to sections with 3+ folios (enough to see progression)
multi_folio_sections = [s for s in sections if len(s['folios']) >= 3]

print("="*70)
print("SECTION PROGRESSION ANALYSIS")
print("="*70)

print(f"\nTotal sections: {len(sections)}")
print(f"Sections with 3+ folios: {len(multi_folio_sections)}")

# Build record-level data with section assignment
records = []
for section_idx, section in enumerate(sections):
    for folio_pos, folio in enumerate(section['folios']):
        folio_tokens = df_a[df_a['folio'] == folio]

        for (line,), line_tokens in folio_tokens.groupby(['line_number']):
            middles = set(line_tokens['middle'].dropna())
            prefixes = list(line_tokens['prefix'].dropna())

            pp_count = len(middles & pp_middles)
            singleton_count = len(middles & singleton_ri)
            boundary_count = len(middles & boundary_ri)

            records.append({
                'section_idx': section_idx,
                'section_marker': section['marker'],
                'section_length': len(section['folios']),
                'folio': folio,
                'folio_pos': folio_pos,  # 0 = first folio, 1 = second, etc.
                'rel_pos': folio_pos / (len(section['folios']) - 1) if len(section['folios']) > 1 else 0,
                'pp_count': pp_count,
                'singleton_count': singleton_count,
                'boundary_count': boundary_count,
                'total_tokens': len(line_tokens),
                'prefixes': prefixes
            })

records_df = pd.DataFrame(records)

# Analyze progression within multi-folio sections
print(f"\n" + "="*70)
print("PP COUNT PROGRESSION WITHIN SECTIONS")
print("="*70)

# Group records by relative position within section
records_df['pos_bin'] = pd.cut(records_df['rel_pos'], bins=[0, 0.33, 0.66, 1.0],
                               labels=['START', 'MIDDLE', 'END'], include_lowest=True)

multi_section_records = records_df[records_df['section_length'] >= 3]

print(f"\nMean PP count by position (sections with 3+ folios):")
pp_by_pos = multi_section_records.groupby('pos_bin')['pp_count'].mean()
for pos, mean_pp in pp_by_pos.items():
    n = len(multi_section_records[multi_section_records['pos_bin'] == pos])
    print(f"  {pos}: {mean_pp:.2f} (n={n})")

# Statistical test
from scipy import stats
start_pp = multi_section_records[multi_section_records['pos_bin'] == 'START']['pp_count']
end_pp = multi_section_records[multi_section_records['pos_bin'] == 'END']['pp_count']
if len(start_pp) > 5 and len(end_pp) > 5:
    t_stat, p_value = stats.ttest_ind(start_pp, end_pp)
    print(f"\n  START vs END t-test: t={t_stat:.2f}, p={p_value:.4f}")

# Boundary RI progression
print(f"\n" + "="*70)
print("BOUNDARY RI PROGRESSION WITHIN SECTIONS")
print("="*70)

print(f"\nMean boundary RI count by position:")
boundary_by_pos = multi_section_records.groupby('pos_bin')['boundary_count'].mean()
for pos, mean_b in boundary_by_pos.items():
    print(f"  {pos}: {mean_b:.2f}")

# Record length progression
print(f"\n" + "="*70)
print("RECORD LENGTH PROGRESSION")
print("="*70)

print(f"\nMean tokens per record by position:")
length_by_pos = multi_section_records.groupby('pos_bin')['total_tokens'].mean()
for pos, mean_len in length_by_pos.items():
    print(f"  {pos}: {mean_len:.2f}")

# PREFIX changes - do different prefixes dominate at different positions?
print(f"\n" + "="*70)
print("PREFIX DISTRIBUTION BY SECTION POSITION")
print("="*70)

for pos in ['START', 'MIDDLE', 'END']:
    pos_records = multi_section_records[multi_section_records['pos_bin'] == pos]
    all_prefixes = [p for prefixes in pos_records['prefixes'] for p in prefixes if p]
    prefix_counts = pd.Series(all_prefixes).value_counts()
    top_5 = prefix_counts.head(5)
    top_str = ', '.join(f"{p}:{c}" for p, c in top_5.items())
    print(f"\n{pos}: {top_str}")

# Look at specific long sections
print(f"\n" + "="*70)
print("DETAILED VIEW: LONGEST SECTIONS")
print("="*70)

long_sections = [s for s in sections if len(s['folios']) >= 4]
for section in long_sections[:5]:
    print(f"\n--- Section '{section['marker']}' ({len(section['folios'])} folios) ---")

    for i, folio in enumerate(section['folios']):
        folio_records = records_df[(records_df['section_marker'] == section['marker']) &
                                   (records_df['folio'] == folio)]
        mean_pp = folio_records['pp_count'].mean()
        mean_boundary = folio_records['boundary_count'].mean()
        n_records = len(folio_records)
        print(f"  {folio}: {n_records} records, PP={mean_pp:.1f}, boundary={mean_boundary:.2f}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

start_mean = pp_by_pos.get('START', 0)
end_mean = pp_by_pos.get('END', 0)

if abs(start_mean - end_mean) > 0.5:
    direction = "INCREASES" if end_mean > start_mean else "DECREASES"
    print(f"""
PP COUNT {direction} THROUGH SECTIONS.

START: {start_mean:.2f} PP per record
END: {end_mean:.2f} PP per record

This suggests sections have internal structure:
- Records change systematically as section progresses
- The singleton RI marker organizes coherent content
""")
else:
    print(f"""
NO CLEAR PROGRESSION DETECTED.

START: {start_mean:.2f} PP per record
END: {end_mean:.2f} PP per record

Records within sections show stable composition.
The singleton RI may mark boundaries without implying internal progression.
""")
