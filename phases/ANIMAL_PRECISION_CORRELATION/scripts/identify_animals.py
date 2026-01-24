#!/usr/bin/env python3
"""
Can we identify specific animals from the RI tokens?

The 7 tokens with P(animal) = 1.00:
- chald, hyd, olfcho, eoschso, hdaoto, cthso, eyd

Questions:
1. Where do these tokens appear in A?
2. Do they cluster together (same A records)?
3. What PREFIX/SUFFIX patterns do they have?
4. Can we infer distinct animal identities?
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_morphology(token):
    if pd.isna(token): return None, None, None
    token = str(token)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None, None, None
    remainder = token[len(prefix):]
    suffix = None
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            break
    middle = remainder[:-len(suffix)] if suffix else remainder
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix

df_a['prefix'], df_a['middle'], df_a['suffix'] = zip(*df_a['word'].apply(extract_morphology))

print("=" * 70)
print("ANIMAL IDENTIFICATION ANALYSIS")
print("=" * 70)
print()

# The 7 definitive animal tokens (P(animal) = 1.00)
animal_tokens = ['chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd']

# Also include strong candidates (P(animal) >= 0.5)
strong_animal = ['teold', 'olar', 'hod']

all_animal = animal_tokens + strong_animal

print(f"Definitive animal tokens (P=1.00): {animal_tokens}")
print(f"Strong animal tokens (P>=0.50): {strong_animal}")
print()

# =============================================================================
# ANALYSIS 1: Where do these tokens appear?
# =============================================================================
print("-" * 70)
print("ANALYSIS 1: Location of animal-associated MIDDLEs")
print("-" * 70)
print()

token_locations = {}
for token in all_animal:
    matches = df_a[df_a['middle'] == token]
    if len(matches) > 0:
        locations = matches[['folio', 'line_number', 'word', 'prefix', 'suffix']].values.tolist()
        token_locations[token] = locations
        print(f"{token} (n={len(matches)}):")
        for loc in locations[:5]:  # Show first 5
            print(f"  {loc[0]}:{loc[1]} - '{loc[2]}' (prefix={loc[3]}, suffix={loc[4]})")
        if len(locations) > 5:
            print(f"  ... and {len(locations)-5} more")
        print()

# =============================================================================
# ANALYSIS 2: Co-occurrence clustering
# =============================================================================
print("-" * 70)
print("ANALYSIS 2: Co-occurrence (do animal tokens appear together?)")
print("-" * 70)
print()

# Build A entries with animal tokens
a_entries = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()
a_entries.columns = ['folio', 'line', 'middles', 'words']

# Find entries containing animal tokens
animal_set = set(all_animal)
a_entries['animal_count'] = a_entries['middles'].apply(lambda x: len(x & animal_set))
a_entries['animal_tokens'] = a_entries['middles'].apply(lambda x: x & animal_set)

animal_entries = a_entries[a_entries['animal_count'] > 0].copy()
animal_entries = animal_entries.sort_values('animal_count', ascending=False)

print(f"A entries containing animal tokens: {len(animal_entries)}")
print()

# Check for co-occurrence
multi_animal = animal_entries[animal_entries['animal_count'] >= 2]
print(f"Entries with 2+ animal tokens: {len(multi_animal)}")

if len(multi_animal) > 0:
    print("\n*** POTENTIAL ANIMAL RECORDS (multiple tokens) ***")
    for _, row in multi_animal.iterrows():
        print(f"  {row['folio']}:{row['line']} - {row['animal_tokens']}")
        # Show the full words
        for word in row['words']:
            if pd.notna(word):
                p, m, s = extract_morphology(word)
                if m in animal_set:
                    print(f"    '{word}' = {p} + {m} + {s}")
print()

# =============================================================================
# ANALYSIS 3: PREFIX patterns (what operations apply to animals?)
# =============================================================================
print("-" * 70)
print("ANALYSIS 3: PREFIX patterns for animal tokens")
print("-" * 70)
print()

prefix_counts = defaultdict(lambda: defaultdict(int))
for token in all_animal:
    matches = df_a[df_a['middle'] == token]
    for _, row in matches.iterrows():
        if pd.notna(row['prefix']):
            prefix_counts[token][row['prefix']] += 1

print("PREFIX distribution by animal token:")
for token in all_animal:
    if token in prefix_counts:
        prefixes = dict(prefix_counts[token])
        print(f"  {token}: {prefixes}")

# Aggregate
all_prefixes = defaultdict(int)
for token in all_animal:
    for p, c in prefix_counts[token].items():
        all_prefixes[p] += c

print(f"\nAggregate PREFIX distribution for animal tokens:")
for p, c in sorted(all_prefixes.items(), key=lambda x: -x[1]):
    print(f"  {p}: {c}")

# =============================================================================
# ANALYSIS 4: Folio clustering
# =============================================================================
print()
print("-" * 70)
print("ANALYSIS 4: Which A folios contain animal tokens?")
print("-" * 70)
print()

folio_animal = defaultdict(set)
for _, row in animal_entries.iterrows():
    folio_animal[row['folio']].update(row['animal_tokens'])

print("A folios with animal tokens:")
for folio, tokens in sorted(folio_animal.items(), key=lambda x: -len(x[1])):
    print(f"  {folio}: {tokens}")

# =============================================================================
# ANALYSIS 5: Can we infer distinct animals?
# =============================================================================
print()
print("-" * 70)
print("ANALYSIS 5: Distinct animal inference")
print("-" * 70)
print()

# Check if tokens cluster by folio (suggesting distinct records)
token_folios = defaultdict(set)
for token in all_animal:
    matches = df_a[df_a['middle'] == token]
    for folio in matches['folio'].unique():
        token_folios[token].add(folio)

print("Folio spread by token:")
for token in all_animal:
    folios = token_folios.get(token, set())
    print(f"  {token}: {len(folios)} folios - {sorted(folios)}")

# Check for exclusive tokens (appear in only 1 folio = likely specific identity)
exclusive = {t: f for t, f in token_folios.items() if len(f) == 1}
print(f"\nFolio-exclusive tokens: {len(exclusive)}")
for t, f in exclusive.items():
    print(f"  {t} -> only in {f}")

# =============================================================================
# SUMMARY
# =============================================================================
print()
print("=" * 70)
print("SUMMARY: Can we name the animals?")
print("=" * 70)
print()

print("""
CONSTRAINT: C171 (closed-loop control) says the grammar encodes operational
behavior, not material identity. We cannot definitively say "token X = chicken".

HOWEVER, we can observe:
""")

print(f"1. {len(animal_entries)} A entries contain animal-associated tokens")
print(f"2. {len(multi_animal)} entries have 2+ animal tokens (potential records)")
print(f"3. {len(exclusive)} tokens are folio-exclusive (specific identities?)")
print()

if len(exclusive) > 0:
    print("FOLIO-EXCLUSIVE TOKENS (strongest identity candidates):")
    for token, folios in exclusive.items():
        folio = list(folios)[0]
        print(f"  '{token}' appears ONLY in {folio}")
        # Check Brunschwig animal count
    print()
    print("Brunschwig lists 9 animal materials.")
    print(f"We found {len(exclusive)} folio-exclusive animal tokens.")
    print("These MAY represent distinct animal identities, but we cannot prove")
    print("which token corresponds to which animal.")
