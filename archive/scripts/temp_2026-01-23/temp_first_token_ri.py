#!/usr/bin/env python3
"""
Is singleton RI the same as the "unique first token" pattern?
Check if singleton RI concentrates at folio-initial or line-initial positions.
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
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
ri_counts = ri_tokens['middle'].value_counts()
singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)

print("="*70)
print("FIRST TOKEN / SINGLETON RI RELATIONSHIP")
print("="*70)

# Identify folio-initial tokens (first token of each folio)
df_a_sorted = df_a.sort_values(['folio', 'line_number', 'placement'])
folio_first_tokens = df_a_sorted.groupby('folio').first().reset_index()

print(f"\nTotal folios with A content: {len(folio_first_tokens)}")
print(f"Total A tokens: {len(df_a)}")

# Check MIDDLE type of folio-first tokens
folio_first_tokens['ri_type'] = folio_first_tokens['middle'].apply(
    lambda m: 'SINGLETON' if m in singleton_ri else
              ('BOUNDARY' if m in boundary_ri else
               ('PP' if m in pp_middles else 'OTHER'))
)

print(f"\n--- FOLIO-FIRST TOKEN MIDDLE TYPE ---")
type_counts = folio_first_tokens['ri_type'].value_counts()
for t, c in type_counts.items():
    pct = c / len(folio_first_tokens) * 100
    print(f"  {t}: {c} ({pct:.1f}%)")

# Compare to overall distribution
df_a['ri_type'] = df_a['middle'].apply(
    lambda m: 'SINGLETON' if m in singleton_ri else
              ('BOUNDARY' if m in boundary_ri else
               ('PP' if m in pp_middles else 'OTHER'))
)

print(f"\n--- OVERALL A TOKEN MIDDLE TYPE (for comparison) ---")
overall_counts = df_a['ri_type'].value_counts()
for t, c in overall_counts.items():
    pct = c / len(df_a) * 100
    print(f"  {t}: {c} ({pct:.1f}%)")

# Enrichment calculation
singleton_folio_first = (folio_first_tokens['ri_type'] == 'SINGLETON').mean() * 100
singleton_overall = (df_a['ri_type'] == 'SINGLETON').mean() * 100
enrichment = singleton_folio_first / singleton_overall if singleton_overall > 0 else 0

print(f"\n--- SINGLETON RI ENRICHMENT AT FOLIO-FIRST ---")
print(f"  Folio-first singleton rate: {singleton_folio_first:.1f}%")
print(f"  Overall singleton rate: {singleton_overall:.1f}%")
print(f"  Enrichment: {enrichment:.2f}x")

# Now check LINE-first tokens
line_first_tokens = df_a_sorted.groupby(['folio', 'line_number']).first().reset_index()

print(f"\n--- LINE-FIRST TOKEN MIDDLE TYPE ---")
line_first_tokens['ri_type'] = line_first_tokens['middle'].apply(
    lambda m: 'SINGLETON' if m in singleton_ri else
              ('BOUNDARY' if m in boundary_ri else
               ('PP' if m in pp_middles else 'OTHER'))
)

line_first_counts = line_first_tokens['ri_type'].value_counts()
for t, c in line_first_counts.items():
    pct = c / len(line_first_tokens) * 100
    print(f"  {t}: {c} ({pct:.1f}%)")

# Check uniqueness of folio-first tokens (the original pattern)
print(f"\n" + "="*70)
print("UNIQUENESS OF FOLIO-FIRST TOKENS")
print("="*70)

folio_first_words = folio_first_tokens['word'].tolist()
word_counts_in_a = df_a['word'].value_counts()

unique_first_tokens = sum(1 for w in folio_first_words if word_counts_in_a.get(w, 0) == 1)
print(f"\nFolio-first tokens that are UNIQUE (appear only once in all A): {unique_first_tokens}/{len(folio_first_words)} ({100*unique_first_tokens/len(folio_first_words):.1f}%)")

# What about overall token uniqueness?
total_unique = (word_counts_in_a == 1).sum()
print(f"Overall unique tokens in A: {total_unique}/{len(word_counts_in_a)} types ({100*total_unique/len(word_counts_in_a):.1f}% of vocabulary)")

# Are folio-first tokens more unique than expected?
overall_singleton_token_rate = total_unique / len(df_a)  # probability a random token is unique
print(f"\nExpected unique folio-first tokens (if random): {overall_singleton_token_rate * len(folio_first_words):.1f}")
print(f"Actual unique folio-first tokens: {unique_first_tokens}")
print(f"Enrichment: {unique_first_tokens / (overall_singleton_token_rate * len(folio_first_words)):.2f}x")

# Check if singleton RI specifically concentrates at folio-first
print(f"\n" + "="*70)
print("SINGLETON RI AT FOLIO-FIRST POSITION")
print("="*70)

singleton_at_folio_first = folio_first_tokens[folio_first_tokens['ri_type'] == 'SINGLETON']
print(f"\nFolio-first tokens with singleton RI: {len(singleton_at_folio_first)}")

# What % of ALL singleton RI tokens are folio-first?
all_singleton_tokens = df_a[df_a['ri_type'] == 'SINGLETON']
singleton_is_folio_first = all_singleton_tokens['word'].isin(folio_first_tokens['word'])
print(f"\nTotal singleton RI tokens: {len(all_singleton_tokens)}")
print(f"Singleton RI tokens that ARE folio-first: {singleton_is_folio_first.sum()} ({100*singleton_is_folio_first.mean():.1f}%)")

# Check specific examples
print(f"\n--- EXAMPLES OF FOLIO-FIRST SINGLETON RI ---")
for _, row in singleton_at_folio_first.head(15).iterrows():
    print(f"  {row['folio']}: '{row['word']}' (MIDDLE='{row['middle']}')")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if singleton_folio_first > singleton_overall * 2:
    print(f"""
YES - SINGLETON RI IS THE "UNIQUE FIRST TOKEN" PATTERN.

Singleton RI at folio-first: {singleton_folio_first:.1f}%
Singleton RI overall: {singleton_overall:.1f}%
Enrichment: {enrichment:.2f}x

The previously discovered "unique first token" pattern IS the singleton RI.
Folio-initial position is where unique identifiers concentrate.

This suggests folio-first tokens serve as:
- Folio identifiers / titles
- Batch/lot markers for the folio's content
- Index entries for navigation
""")
elif singleton_folio_first > singleton_overall * 1.3:
    print(f"""
PARTIAL OVERLAP - Singleton RI is ENRICHED at folio-first but not exclusive.

Singleton RI at folio-first: {singleton_folio_first:.1f}%
Singleton RI overall: {singleton_overall:.1f}%
Enrichment: {enrichment:.2f}x

Folio-first tokens are more likely to be singleton RI, but singleton RI
also appears throughout folios. The "unique first token" pattern is
a subset of the broader singleton RI phenomenon.
""")
else:
    print(f"""
NO - Singleton RI is NOT concentrated at folio-first.

Singleton RI at folio-first: {singleton_folio_first:.1f}%
Singleton RI overall: {singleton_overall:.1f}%
Enrichment: {enrichment:.2f}x

The "unique first token" pattern (if it exists) is separate from
the singleton RI phenomenon we discovered.
""")
