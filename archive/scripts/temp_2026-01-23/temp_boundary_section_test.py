#!/usr/bin/env python3
"""
Test: Do boundary MIDDLEs (short, repeating RI) cluster in A sections
with low B representation?

Per C299, sections have different B mapping rates.
If boundary MIDDLEs cluster in low-B sections, their absence from B
is explained by section isolation, not functional difference.
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

# Get section info (from quire or section column if available)
# The 'section' column should have H, P, T, S, Z, C, A, R etc.
print("="*70)
print("CHECKING AVAILABLE SECTION INFORMATION")
print("="*70)

print(f"\nColumns available: {list(df.columns)}")

# Check what section-like columns exist
if 'section' in df.columns:
    print(f"\n'section' column values: {df['section'].unique()[:20]}")
elif 'quire' in df.columns:
    print(f"\n'quire' column values: {df['quire'].unique()[:20]}")

# Use quire as proxy for section grouping
# Map folios to their Currier language designation
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()
df_azc = df[df['language'].isna()].copy()

print(f"\nCurrier A tokens: {len(df_a)}")
print(f"Currier B tokens: {len(df_b)}")
print(f"AZC tokens: {len(df_azc)}")

# Extract MIDDLEs
df_a['middle'] = df_a['word'].apply(extract_middle)

# Identify RI tokens
df_ri = df_a[df_a['middle'].apply(lambda m: m is not None and m not in pp_middles)].copy()

# Classify RI MIDDLEs
ri_counts = df_ri['middle'].value_counts()
singleton_middles = set(ri_counts[ri_counts == 1].index)
repeating_middles = set(ri_counts[ri_counts > 1].index)

# Further classify: short repeaters (boundary) vs others
short_repeating = set(m for m in repeating_middles if len(m) <= 3)
long_repeating = set(m for m in repeating_middles if len(m) > 3)

print(f"\n" + "="*70)
print("RI MIDDLE CLASSIFICATION")
print("="*70)
print(f"Singleton (appear once): {len(singleton_middles)}")
print(f"Short repeating (len<=3, appear 2+): {len(short_repeating)}")
print(f"Long repeating (len>3, appear 2+): {len(long_repeating)}")

# Check folio distribution by Currier type
# Folios are predominantly A or B - let's see which folios the boundary MIDDLEs appear in

print(f"\n" + "="*70)
print("FOLIO ANALYSIS: WHERE DO BOUNDARY MIDDLEs APPEAR?")
print("="*70)

# Get folio-level Currier designation
# A folio is "A-dominant" if most of its tokens are Currier A
folio_language = df.groupby('folio')['language'].apply(
    lambda x: 'A' if (x == 'A').sum() > (x == 'B').sum() else ('B' if (x == 'B').sum() > 0 else 'AZC')
)

a_folios = set(folio_language[folio_language == 'A'].index)
b_folios = set(folio_language[folio_language == 'B'].index)
azc_folios = set(folio_language[folio_language == 'AZC'].index)

print(f"\nFolio classification:")
print(f"  A-dominant folios: {len(a_folios)}")
print(f"  B-dominant folios: {len(b_folios)}")
print(f"  AZC-only folios: {len(azc_folios)}")

# For each RI category, check which folio types they appear in
def analyze_folio_distribution(middles, label):
    tokens = df_ri[df_ri['middle'].isin(middles)]
    folios = tokens['folio'].unique()

    in_a_folios = sum(1 for f in folios if f in a_folios)
    in_b_folios = sum(1 for f in folios if f in b_folios)
    in_azc_folios = sum(1 for f in folios if f in azc_folios)

    # Token counts by folio type
    tokens_in_a = len(tokens[tokens['folio'].isin(a_folios)])
    tokens_in_b = len(tokens[tokens['folio'].isin(b_folios)])

    print(f"\n{label}:")
    print(f"  Unique MIDDLEs: {len(middles)}")
    print(f"  Appear in A-dominant folios: {in_a_folios} folios, {tokens_in_a} tokens")
    print(f"  Appear in B-dominant folios: {in_b_folios} folios, {tokens_in_b} tokens")
    print(f"  Ratio (B-folio tokens / total): {tokens_in_b / (tokens_in_a + tokens_in_b) * 100:.1f}%")

    return tokens_in_b / (tokens_in_a + tokens_in_b) if (tokens_in_a + tokens_in_b) > 0 else 0

singleton_b_ratio = analyze_folio_distribution(singleton_middles, "SINGLETON RI (true discriminators)")
short_rep_b_ratio = analyze_folio_distribution(short_repeating, "SHORT REPEATING RI (boundary)")
long_rep_b_ratio = analyze_folio_distribution(long_repeating, "LONG REPEATING RI")

# Now check: do PP MIDDLEs appear in the same distribution?
print(f"\n" + "="*70)
print("COMPARISON: PP vs RI FOLIO DISTRIBUTION")
print("="*70)

df_pp = df_a[df_a['middle'].isin(pp_middles)].copy()
pp_tokens_in_a = len(df_pp[df_pp['folio'].isin(a_folios)])
pp_tokens_in_b = len(df_pp[df_pp['folio'].isin(b_folios)])
pp_b_ratio = pp_tokens_in_b / (pp_tokens_in_a + pp_tokens_in_b) if (pp_tokens_in_a + pp_tokens_in_b) > 0 else 0

print(f"\nPP MIDDLEs (for comparison):")
print(f"  Tokens in A-dominant folios: {pp_tokens_in_a}")
print(f"  Tokens in B-dominant folios: {pp_tokens_in_b}")
print(f"  Ratio (B-folio tokens / total): {pp_b_ratio * 100:.1f}%")

# Deep dive: the specific boundary MIDDLEs
print(f"\n" + "="*70)
print("SPECIFIC BOUNDARY MIDDLEs: FOLIO BREAKDOWN")
print("="*70)

top_boundary = ['sh', 'ko', 'to', 'yd', 'p', 'ro', 'ls', 'ld', 'yk', 'da']

print(f"\n{'MIDDLE':>8} {'Total':>6} {'A-folios':>10} {'B-folios':>10} {'B-ratio':>10}")
print("-" * 50)

for middle in top_boundary:
    if middle in short_repeating:
        tokens = df_ri[df_ri['middle'] == middle]
        in_a = len(tokens[tokens['folio'].isin(a_folios)])
        in_b = len(tokens[tokens['folio'].isin(b_folios)])
        total = in_a + in_b
        b_ratio = in_b / total * 100 if total > 0 else 0
        print(f"{middle:>8} {total:>6} {in_a:>10} {in_b:>10} {b_ratio:>9.1f}%")

# Check: which specific B-folios have boundary MIDDLEs?
print(f"\n" + "="*70)
print("WHICH B-FOLIOS CONTAIN BOUNDARY MIDDLEs?")
print("="*70)

boundary_tokens = df_ri[df_ri['middle'].isin(short_repeating)]
boundary_in_b_folios = boundary_tokens[boundary_tokens['folio'].isin(b_folios)]

b_folio_boundary_counts = boundary_in_b_folios.groupby('folio').size().sort_values(ascending=False)
print(f"\nB-folios with boundary RI tokens:")
for folio, count in b_folio_boundary_counts.head(15).items():
    unique_middles = boundary_in_b_folios[boundary_in_b_folios['folio'] == folio]['middle'].nunique()
    print(f"  {folio}: {count} tokens, {unique_middles} unique boundary MIDDLEs")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if short_rep_b_ratio > singleton_b_ratio * 1.5:
    print(f"""
BOUNDARY MIDDLEs ARE ENRICHED IN B-FOLIOS.

Singleton RI (true discriminators): {singleton_b_ratio*100:.1f}% in B-folios
Short repeating RI (boundary): {short_rep_b_ratio*100:.1f}% in B-folios

The boundary MIDDLEs appear MORE in B-dominant folios than true RI.
This suggests they ARE functionally PP-like and their absence from B
may be a sampling artifact or positional restriction within B folios.
""")
elif abs(short_rep_b_ratio - singleton_b_ratio) < 0.1:
    print(f"""
NO SECTION CLUSTERING DETECTED.

Singleton RI: {singleton_b_ratio*100:.1f}% in B-folios
Boundary RI: {short_rep_b_ratio*100:.1f}% in B-folios

Both RI populations have similar folio distributions.
The boundary MIDDLEs' absence from B is NOT explained by section isolation.
They may be genuinely A-exclusive despite their PP-like structure.
""")
else:
    print(f"""
BOUNDARY MIDDLEs ARE CONCENTRATED IN A-FOLIOS.

Singleton RI: {singleton_b_ratio*100:.1f}% in B-folios
Boundary RI: {short_rep_b_ratio*100:.1f}% in B-folios

The boundary MIDDLEs appear LESS in B-folios than singleton RI.
This is unexpected and warrants further investigation.
""")
