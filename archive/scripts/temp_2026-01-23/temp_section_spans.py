#!/usr/bin/env python3
"""
Test: Does folio-first singleton RI mark section boundaries?

If so:
- Singleton RI appears at START of a section
- Folios within section don't have new singleton RI at first position
- We'd see "runs" of folios under the same section marker
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

# Classify RI
ri_counts = df_a[df_a['middle'].notna() & ~df_a['middle'].isin(pp_middles)]['middle'].value_counts()
singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)

# Get folio-first tokens in order
df_a_sorted = df_a.sort_values(['folio', 'line_number', 'placement'])
folio_first = df_a_sorted.groupby('folio').first().reset_index()

# Sort folios in manuscript order (f1r, f1v, f2r, f2v, ...)
def folio_sort_key(f):
    import re
    match = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)

folio_first['sort_key'] = folio_first['folio'].apply(folio_sort_key)
folio_first = folio_first.sort_values('sort_key')

# Classify each folio-first token
folio_first['ri_type'] = folio_first['middle'].apply(
    lambda m: 'SINGLETON' if m in singleton_ri else
              ('BOUNDARY' if m in boundary_ri else
               ('PP' if m in pp_middles else 'OTHER'))
)

print("="*70)
print("FOLIO-FIRST TOKEN SEQUENCE ANALYSIS")
print("="*70)

# Show sequence with manuscript sections
print(f"\n--- FOLIO SEQUENCE WITH FIRST TOKEN TYPE ---")
print(f"{'Folio':>10} {'Section':>8} {'Type':>12} {'First Token':>20} {'MIDDLE':>15}")
print("-" * 75)

for _, row in folio_first.iterrows():
    section = df_a[df_a['folio'] == row['folio']]['section'].iloc[0] if len(df_a[df_a['folio'] == row['folio']]) > 0 else '?'
    word = str(row['word'])[:18] if pd.notna(row['word']) else '?'
    middle = str(row['middle'])[:13] if pd.notna(row['middle']) else '?'
    print(f"{row['folio']:>10} {section:>8} {row['ri_type']:>12} {word:>20} {middle:>15}")

# Analyze runs: consecutive folios with same ri_type
print(f"\n" + "="*70)
print("RUN ANALYSIS: CONSECUTIVE FOLIOS")
print("="*70)

# Find runs of non-singleton (potential "within section" folios)
runs = []
current_run = []
last_singleton_folio = None

for _, row in folio_first.iterrows():
    if row['ri_type'] == 'SINGLETON':
        if current_run:
            runs.append({
                'marker_folio': last_singleton_folio,
                'following_folios': current_run.copy(),
                'length': len(current_run)
            })
        current_run = []
        last_singleton_folio = row['folio']
    else:
        current_run.append(row['folio'])

# Don't forget the last run
if current_run:
    runs.append({
        'marker_folio': last_singleton_folio,
        'following_folios': current_run.copy(),
        'length': len(current_run)
    })

print(f"\n'Sections' (singleton RI followed by non-singleton folios):")
print(f"Total potential sections: {len(runs)}")

run_lengths = [r['length'] for r in runs]
if run_lengths:
    print(f"Folios following each singleton marker: min={min(run_lengths)}, max={max(run_lengths)}, mean={sum(run_lengths)/len(run_lengths):.1f}")

print(f"\n--- SECTION SPANS ---")
for r in runs[:20]:
    if r['marker_folio']:
        following = ', '.join(r['following_folios'][:5])
        if len(r['following_folios']) > 5:
            following += f"... (+{len(r['following_folios'])-5})"
        print(f"  {r['marker_folio']} → [{r['length']} folios]: {following}")

# Check if singleton markers align with manuscript sections
print(f"\n" + "="*70)
print("ALIGNMENT WITH MANUSCRIPT SECTIONS")
print("="*70)

# Get manuscript section for each folio
folio_to_section = df_a.groupby('folio')['section'].first().to_dict()
folio_first['ms_section'] = folio_first['folio'].map(folio_to_section)

# Do singleton RI tend to appear at section boundaries?
section_changes = []
prev_section = None
for _, row in folio_first.iterrows():
    if prev_section is not None and row['ms_section'] != prev_section:
        section_changes.append({
            'folio': row['folio'],
            'from': prev_section,
            'to': row['ms_section'],
            'ri_type': row['ri_type']
        })
    prev_section = row['ms_section']

print(f"\nManuscript section changes: {len(section_changes)}")
print(f"\n{'Folio':>10} {'From':>6} {'To':>6} {'First Token Type':>18}")
print("-" * 45)
for sc in section_changes:
    print(f"{sc['folio']:>10} {sc['from']:>6} {sc['to']:>6} {sc['ri_type']:>18}")

# Rate of singleton at section boundaries vs non-boundaries
singleton_at_boundary = sum(1 for sc in section_changes if sc['ri_type'] == 'SINGLETON')
singleton_at_nonboundary = (folio_first['ri_type'] == 'SINGLETON').sum() - singleton_at_boundary

print(f"\nSingleton RI at section boundaries: {singleton_at_boundary}/{len(section_changes)} ({100*singleton_at_boundary/len(section_changes):.1f}%)")
print(f"Singleton RI at non-boundaries: {singleton_at_nonboundary}/{len(folio_first)-len(section_changes)}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

boundary_rate = singleton_at_boundary / len(section_changes) if section_changes else 0
non_boundary_rate = singleton_at_nonboundary / (len(folio_first) - len(section_changes)) if (len(folio_first) - len(section_changes)) > 0 else 0

if boundary_rate > non_boundary_rate * 1.5:
    print(f"""
SINGLETON RI MARKS SECTION BOUNDARIES.

At section boundaries: {100*boundary_rate:.1f}% are singleton RI
At non-boundaries: {100*non_boundary_rate:.1f}% are singleton RI

The singleton RI folio-first tokens cluster at manuscript section transitions.
This supports the "chapter marker" hypothesis - new sections get new markers.
""")
else:
    print(f"""
SINGLETON RI DOES NOT SPECIFICALLY MARK SECTION BOUNDARIES.

At section boundaries: {100*boundary_rate:.1f}% are singleton RI
At non-boundaries: {100*non_boundary_rate:.1f}% are singleton RI

Singleton RI appears throughout, not specifically at section transitions.
It may mark finer-grained divisions (sub-chapters, topics, batches)
rather than the coarse manuscript sections (H, P, T, etc.).
""")
