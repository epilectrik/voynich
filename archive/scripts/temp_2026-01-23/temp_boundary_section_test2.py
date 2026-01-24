#!/usr/bin/env python3
"""
Test: Do boundary MIDDLEs cluster in MANUSCRIPT SECTIONS
with low B representation?

Sections: H (Herbal), P (Pharmaceutical), T (Text-only),
          S (Stars), Z (Zodiac), C (Cosmological), A (Astronomical), B (Balneological)
"""

import json
import sys
import pandas as pd
from collections import defaultdict, Counter
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

# Load full transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

print("="*70)
print("MANUSCRIPT SECTION ANALYSIS")
print("="*70)

# Section breakdown by Currier language
print("\nSection composition (Currier A vs B):")
print(f"{'Section':>10} {'Total':>8} {'A':>8} {'B':>8} {'AZC':>8} {'A%':>8} {'B%':>8}")
print("-" * 70)

section_stats = {}
for section in sorted(df['section'].unique()):
    sec_df = df[df['section'] == section]
    total = len(sec_df)
    a_count = len(sec_df[sec_df['language'] == 'A'])
    b_count = len(sec_df[sec_df['language'] == 'B'])
    azc_count = len(sec_df[sec_df['language'].isna()])
    a_pct = a_count / total * 100 if total > 0 else 0
    b_pct = b_count / total * 100 if total > 0 else 0
    print(f"{section:>10} {total:>8} {a_count:>8} {b_count:>8} {azc_count:>8} {a_pct:>7.1f}% {b_pct:>7.1f}%")
    section_stats[section] = {'total': total, 'a': a_count, 'b': b_count, 'a_pct': a_pct, 'b_pct': b_pct}

# Identify high-A sections (>50% A) and high-B sections (>50% B)
high_a_sections = [s for s, stats in section_stats.items() if stats['a_pct'] > 50]
high_b_sections = [s for s, stats in section_stats.items() if stats['b_pct'] > 50]
mixed_sections = [s for s in section_stats.keys() if s not in high_a_sections and s not in high_b_sections]

print(f"\nHigh-A sections (>50% Currier A): {high_a_sections}")
print(f"High-B sections (>50% Currier B): {high_b_sections}")
print(f"Mixed/AZC sections: {mixed_sections}")

# Now analyze RI distribution by section
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)
df_ri = df_a[df_a['middle'].apply(lambda m: m is not None and m not in pp_middles)].copy()

# Classify RI
ri_counts = df_ri['middle'].value_counts()
singleton_middles = set(ri_counts[ri_counts == 1].index)
repeating_middles = set(ri_counts[ri_counts > 1].index)
short_repeating = set(m for m in repeating_middles if len(m) <= 3)

print(f"\n" + "="*70)
print("RI DISTRIBUTION BY MANUSCRIPT SECTION")
print("="*70)

def analyze_section_dist(middles, label):
    tokens = df_ri[df_ri['middle'].isin(middles)]

    print(f"\n{label}:")
    print(f"  Total tokens: {len(tokens)}")

    section_counts = tokens.groupby('section').size()
    print(f"\n  {'Section':>10} {'Tokens':>8} {'%':>8} {'Section B%':>12}")
    print("  " + "-" * 45)

    for section in sorted(section_counts.index):
        count = section_counts[section]
        pct = count / len(tokens) * 100
        sec_b_pct = section_stats[section]['b_pct']
        print(f"  {section:>10} {count:>8} {pct:>7.1f}% {sec_b_pct:>11.1f}%")

    # Calculate weighted average B% for this RI category
    weighted_b = sum(section_counts.get(s, 0) * section_stats[s]['b_pct']
                     for s in section_stats.keys()) / len(tokens) if len(tokens) > 0 else 0
    print(f"\n  Weighted avg section B%: {weighted_b:.1f}%")
    return weighted_b

singleton_weighted_b = analyze_section_dist(singleton_middles, "SINGLETON RI (true discriminators)")
boundary_weighted_b = analyze_section_dist(short_repeating, "SHORT REPEATING RI (boundary)")

# Also check PP for comparison
df_pp = df_a[df_a['middle'].isin(pp_middles)]
print(f"\n" + "="*70)
print("PP MIDDLEs FOR COMPARISON")
print("="*70)
print(f"\nTotal PP tokens in A: {len(df_pp)}")
pp_section_counts = df_pp.groupby('section').size()
print(f"\n{'Section':>10} {'Tokens':>8} {'%':>8}")
print("-" * 30)
for section in sorted(pp_section_counts.index):
    count = pp_section_counts[section]
    pct = count / len(df_pp) * 100
    print(f"{section:>10} {count:>8} {pct:>7.1f}%")

# Deep dive: specific boundary MIDDLEs
print(f"\n" + "="*70)
print("SPECIFIC BOUNDARY MIDDLEs BY SECTION")
print("="*70)

top_boundary = ['sh', 'ko', 'to', 'yd', 'p', 'ro', 'ls']

for middle in top_boundary:
    if middle in short_repeating:
        tokens = df_ri[df_ri['middle'] == middle]
        section_dist = tokens.groupby('section').size()
        sections_str = ', '.join(f"{s}:{c}" for s, c in section_dist.items())
        print(f"  '{middle}' ({len(tokens)}x): {sections_str}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

diff = boundary_weighted_b - singleton_weighted_b
if abs(diff) < 5:
    print(f"""
NO SIGNIFICANT SECTION DIFFERENCE.

Singleton RI weighted section-B%: {singleton_weighted_b:.1f}%
Boundary RI weighted section-B%: {boundary_weighted_b:.1f}%
Difference: {diff:.1f}pp

Both RI populations appear in sections with similar B composition.
Section isolation does NOT explain the boundary MIDDLEs' absence from B.

The boundary MIDDLEs are genuinely A-exclusive despite their PP-like structure.
This suggests two possibilities:
1. They serve A-internal functions (registry organization, not execution)
2. They're PP-like in structure but functionally distinct (different role in A vs B)
""")
elif diff > 5:
    print(f"""
BOUNDARY MIDDLEs APPEAR IN HIGHER-B SECTIONS.

Singleton RI weighted section-B%: {singleton_weighted_b:.1f}%
Boundary RI weighted section-B%: {boundary_weighted_b:.1f}%
Difference: {diff:.1f}pp

Boundary MIDDLEs appear in sections with MORE B content.
Yet they still don't appear in B tokens within those sections.
This suggests they're position-restricted within folios (A-zone only).
""")
else:
    print(f"""
BOUNDARY MIDDLEs CONCENTRATED IN LOW-B SECTIONS.

Singleton RI weighted section-B%: {singleton_weighted_b:.1f}%
Boundary RI weighted section-B%: {boundary_weighted_b:.1f}%
Difference: {diff:.1f}pp

Boundary MIDDLEs appear in sections with LESS B content.
Their absence from B may partly reflect section isolation.
""")
