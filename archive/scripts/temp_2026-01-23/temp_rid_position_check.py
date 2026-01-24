#!/usr/bin/env python3
"""
Where do RI-D (singleton) tokens actually appear?
Check if they're really concentrated at folio-first or spread throughout.
"""

import json
import pandas as pd
from pathlib import Path

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
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
ri_counts = ri_tokens['middle'].value_counts()

singleton_ri = set(m for m, c in ri_counts.items() if c == 1)  # RI-D
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)  # RI-B

print("="*70)
print("RI-D POSITION ANALYSIS")
print("="*70)

print(f"\nTotal Currier A folios: {df_a['folio'].nunique()}")
print(f"Total RI-D types (singleton MIDDLEs): {len(singleton_ri)}")
print(f"Total RI-B types (short repeaters): {len(boundary_ri)}")

# Get folio-first tokens
df_a_sorted = df_a.sort_values(['folio', 'line_number', 'placement'])
folio_first = df_a_sorted.groupby('folio').first().reset_index()

# How many folio-first tokens are RI-D?
folio_first_rid = folio_first[folio_first['middle'].isin(singleton_ri)]
print(f"\nFolio-first tokens that are RI-D: {len(folio_first_rid)} / {len(folio_first)} ({100*len(folio_first_rid)/len(folio_first):.1f}%)")

# Since each RI-D appears exactly once, and some appear at folio-first...
# How many RI-D tokens are NOT folio-first?
rid_at_folio_first = len(folio_first_rid)
rid_not_at_folio_first = len(singleton_ri) - rid_at_folio_first

print(f"\nRI-D breakdown:")
print(f"  At folio-first position: {rid_at_folio_first} ({100*rid_at_folio_first/len(singleton_ri):.1f}%)")
print(f"  NOT at folio-first: {rid_not_at_folio_first} ({100*rid_not_at_folio_first/len(singleton_ri):.1f}%)")

# Where do the non-folio-first RI-D appear?
print(f"\n" + "="*70)
print("WHERE DO NON-FOLIO-FIRST RI-D TOKENS APPEAR?")
print("="*70)

# Get line-first tokens
line_first = df_a_sorted.groupby(['folio', 'line_number']).first().reset_index()
line_first_rid = line_first[line_first['middle'].isin(singleton_ri)]

# Exclude folio-first (which is also line-first for line 1)
line_first_not_folio_first = line_first_rid[~line_first_rid['folio'].isin(folio_first_rid['folio']) |
                                             (line_first_rid['line_number'] != line_first_rid.groupby('folio')['line_number'].transform('min'))]

# Actually let's be more precise - check if each RI-D token is at position 1 of a line
df_a['is_line_first'] = df_a.groupby(['folio', 'line_number']).cumcount() == 0
df_a['is_folio_first'] = df_a.groupby('folio').cumcount() == 0

rid_tokens = df_a[df_a['middle'].isin(singleton_ri)]

print(f"\nAll RI-D token positions:")
print(f"  Folio-first (first token of folio): {rid_tokens['is_folio_first'].sum()}")
print(f"  Line-first but NOT folio-first: {(rid_tokens['is_line_first'] & ~rid_tokens['is_folio_first']).sum()}")
print(f"  Mid-line (not first in line): {(~rid_tokens['is_line_first']).sum()}")

# What's the position distribution?
rid_tokens_with_pos = rid_tokens.copy()
rid_tokens_with_pos['line_position'] = rid_tokens_with_pos.groupby(['folio', 'line_number']).cumcount() + 1

print(f"\nRI-D position within line:")
pos_dist = rid_tokens_with_pos['line_position'].value_counts().sort_index()
for pos, count in pos_dist.head(10).items():
    pct = 100 * count / len(rid_tokens_with_pos)
    print(f"  Position {pos}: {count} ({pct:.1f}%)")

# Compare to overall position distribution
df_a['line_position'] = df_a.groupby(['folio', 'line_number']).cumcount() + 1
overall_pos1_rate = (df_a['line_position'] == 1).mean()
rid_pos1_rate = (rid_tokens_with_pos['line_position'] == 1).mean()

print(f"\nPosition 1 (line-first) rates:")
print(f"  Overall A tokens: {100*overall_pos1_rate:.1f}%")
print(f"  RI-D tokens: {100*rid_pos1_rate:.1f}%")
print(f"  Enrichment: {rid_pos1_rate/overall_pos1_rate:.2f}x")

# Summary interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

folio_first_pct = 100 * rid_at_folio_first / len(singleton_ri)
if folio_first_pct < 10:
    print(f"""
CORRECTION NEEDED: RI-D is NOT primarily a folio-first phenomenon.

Only {folio_first_pct:.1f}% of RI-D tokens appear at folio-first position.
The remaining {100-folio_first_pct:.1f}% appear throughout Currier A records.

The 4.2x "enrichment" at folio-first means:
- RI-D is MORE LIKELY at folio-first than elsewhere
- But most RI-D still appears mid-record, not at folio boundaries

RI-D tokens are unique discriminators distributed throughout A,
with a statistical preference for boundary positions (folio-first, line-first).
""")
else:
    print(f"""
RI-D shows strong folio-first concentration: {folio_first_pct:.1f}%
""")
