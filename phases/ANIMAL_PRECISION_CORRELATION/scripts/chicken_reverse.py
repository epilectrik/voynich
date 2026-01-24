#!/usr/bin/env python3
"""
Reverse approach: Start from A folios with animal tokens,
check which B folios their PP vocabulary connects to.

Known animal token clusters:
- f89r2: olfcho, eyd, olar (3 tokens)
- f100r: hdaoto, cthso, teold (3 tokens)
- f23r: chald (1 token)
- f19r: hyd (1 token)
- f90r1: eoschso (1 token)

Question: Which B folios do these A folios connect to?
And do those B folios match chicken's operational pattern?
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("REVERSE TRIANGULATION: A folios -> B folios")
print("=" * 70)
print()

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
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

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)
df_b['prefix'] = df_b['word'].apply(extract_prefix)

# Get B vocabulary by folio
b_folio_vocab = {}
for folio in df_b['folio'].unique():
    b_folio_vocab[folio] = set(df_b[df_b['folio'] == folio]['middle'].dropna().unique())

# Get shared (PP) vocabulary
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

# Animal token A folios
animal_a_folios = {
    'f89r2': ['olfcho', 'eyd', 'olar'],
    'f100r': ['hdaoto', 'cthso', 'teold'],
    'f23r': ['chald'],
    'f19r': ['hyd'],
    'f90r1': ['eoschso']
}

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)
regime4_folios = set(regime_data['REGIME_4'])

# Chicken-like B folios (from previous analysis)
chicken_b_folios = {'f40v', 'f41v', 'f85r1', 'f94v', 'f95v1'}

print("Animal token A folios and their tokens:")
for a_folio, tokens in animal_a_folios.items():
    print(f"  {a_folio}: {tokens}")
print()

print(f"Chicken-like B folios (high qo + aux): {chicken_b_folios}")
print()

# =============================================================================
# For each animal A folio, find which B folios share PP vocabulary
# =============================================================================
print("-" * 70)
print("STEP 1: A folio -> B folio vocabulary connections")
print("-" * 70)
print()

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

for a_folio, animal_tokens in animal_a_folios.items():
    print(f"A folio: {a_folio} (animal tokens: {animal_tokens})")

    # Get PP vocabulary from this A folio
    a_folio_tokens = df_a[df_a['folio'] == a_folio]
    a_folio_middles = set(a_folio_tokens['middle'].dropna().unique())
    a_pp = (a_folio_middles & shared_middles) - infrastructure

    print(f"  PP vocabulary in {a_folio}: {len(a_pp)} tokens")

    # Find B folios with most overlap
    b_overlaps = []
    for b_folio, b_vocab in b_folio_vocab.items():
        overlap = len(a_pp & b_vocab)
        if overlap > 0:
            b_overlaps.append((b_folio, overlap, a_pp & b_vocab))

    b_overlaps.sort(key=lambda x: -x[1])

    # Show top B folio connections
    print(f"  Top B folio connections:")
    for b_folio, overlap, tokens in b_overlaps[:5]:
        regime_mark = "*R4*" if b_folio in regime4_folios else ""
        chicken_mark = "**CHICKEN**" if b_folio in chicken_b_folios else ""
        print(f"    {b_folio}: {overlap} PP overlap {regime_mark} {chicken_mark}")

    # Check if any chicken-like folios are in top connections
    top_b = [x[0] for x in b_overlaps[:10]]
    chicken_matches = set(top_b) & chicken_b_folios
    if chicken_matches:
        print(f"  >>> CHICKEN-LIKE FOLIOS IN TOP 10: {chicken_matches}")

    print()

# =============================================================================
# STEP 2: Which A folio best connects to chicken-like B folios?
# =============================================================================
print("-" * 70)
print("STEP 2: Which animal A folio best connects to chicken B pattern?")
print("-" * 70)
print()

# For each animal A folio, count overlap with chicken-like B folios
a_chicken_scores = {}
for a_folio, animal_tokens in animal_a_folios.items():
    a_folio_tokens = df_a[df_a['folio'] == a_folio]
    a_folio_middles = set(a_folio_tokens['middle'].dropna().unique())
    a_pp = (a_folio_middles & shared_middles) - infrastructure

    # Count overlap with chicken B folios
    chicken_overlap = 0
    for b_folio in chicken_b_folios:
        chicken_overlap += len(a_pp & b_folio_vocab.get(b_folio, set()))

    # Count overlap with OTHER REGIME_4 folios
    other_overlap = 0
    for b_folio in regime4_folios - chicken_b_folios:
        other_overlap += len(a_pp & b_folio_vocab.get(b_folio, set()))

    # Ratio = chicken / other (higher = more chicken-specific)
    ratio = chicken_overlap / other_overlap if other_overlap > 0 else float('inf')

    a_chicken_scores[a_folio] = {
        'animal_tokens': animal_tokens,
        'chicken_overlap': chicken_overlap,
        'other_overlap': other_overlap,
        'ratio': ratio
    }

print("Animal A folios ranked by chicken-specificity (overlap ratio):")
print()
for a_folio, scores in sorted(a_chicken_scores.items(), key=lambda x: -x[1]['ratio']):
    print(f"  {a_folio}: chicken={scores['chicken_overlap']}, other={scores['other_overlap']}, "
          f"ratio={scores['ratio']:.2f}")
    print(f"    Animal tokens: {scores['animal_tokens']}")

# Find the best match
best_match = max(a_chicken_scores.items(), key=lambda x: x[1]['ratio'])
print()
print("=" * 70)
print(f"BEST CHICKEN CANDIDATE: {best_match[0]}")
print(f"Animal tokens: {best_match[1]['animal_tokens']}")
print("=" * 70)
print()

# =============================================================================
# STEP 3: Validate with instruction sequence comparison
# =============================================================================
print("-" * 70)
print("STEP 3: Validate - does this A folio's vocabulary match chicken pattern?")
print("-" * 70)
print()

best_a_folio = best_match[0]
best_tokens = best_match[1]['animal_tokens']

# Get the specific entry containing the animal tokens
a_entries = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()

animal_entries = a_entries[
    (a_entries['folio'] == best_a_folio) &
    (a_entries['middle'].apply(lambda x: any(t in x for t in best_tokens)))
]

print(f"A entries in {best_a_folio} containing animal tokens:")
for _, row in animal_entries.iterrows():
    print(f"  {row['folio']}:{row['line_number']}")
    print(f"    MIDDLEs: {row['middle']}")
    animal_in_entry = [t for t in best_tokens if t in row['middle']]
    print(f"    Animal tokens: {animal_in_entry}")

print()
print("CONCLUSION:")
print(f"If chicken has the unique pattern [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE],")
print(f"and that maps to high qo+aux B folios,")
print(f"then the animal tokens in {best_a_folio} are CHICKEN candidates:")
print(f"  {best_tokens}")
