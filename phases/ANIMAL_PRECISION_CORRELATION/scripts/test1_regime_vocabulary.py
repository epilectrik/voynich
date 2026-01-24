#!/usr/bin/env python3
"""
TEST 1: Is REGIME_4 PP vocabulary distinct?

If REGIME_4 has unique PP vocabulary, then recipes requiring fire degree 4
should connect to A entries containing that vocabulary.

Prediction: REGIME_4 should have some PP MIDDLEs that don't appear in other REGIMEs.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("TEST 1: Is REGIME_4 PP vocabulary distinct from other REGIMEs?")
print("=" * 70)
print()

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t')
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

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

# Get vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles  # PP tokens

print(f"Total PP (shared) MIDDLEs: {len(shared_middles)}")
print()

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

# Get vocabulary by REGIME
regime_vocab = {}
for regime_name in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4', 'REGIME_MIXED']:
    if regime_name in regime_data:
        folios = set(regime_data[regime_name])
        middles = set()
        for folio in folios:
            folio_tokens = df_b[df_b['folio'] == folio]
            middles.update(folio_tokens['middle'].dropna().unique())
        # Filter to PP only
        pp_middles = middles & shared_middles
        regime_vocab[regime_name] = pp_middles
        print(f"{regime_name}: {len(folios)} folios, {len(middles)} MIDDLEs, {len(pp_middles)} PP")

print()

# =============================================================================
# Test: REGIME_4-exclusive PP vocabulary
# =============================================================================
print("-" * 70)
print("REGIME_4-exclusive PP vocabulary")
print("-" * 70)
print()

# PP in REGIME_4 but not in other regimes
other_regimes = set()
for regime_name, vocab in regime_vocab.items():
    if regime_name != 'REGIME_4':
        other_regimes.update(vocab)

regime4_exclusive = regime_vocab.get('REGIME_4', set()) - other_regimes
regime4_shared = regime_vocab.get('REGIME_4', set()) & other_regimes

print(f"REGIME_4 PP vocabulary: {len(regime_vocab.get('REGIME_4', set()))}")
print(f"  Exclusive to REGIME_4: {len(regime4_exclusive)}")
print(f"  Shared with other REGIMEs: {len(regime4_shared)}")
print()

if regime4_exclusive:
    print(f"REGIME_4-exclusive PP MIDDLEs: {sorted(regime4_exclusive)[:20]}")
    if len(regime4_exclusive) > 20:
        print(f"  ... and {len(regime4_exclusive) - 20} more")
    print()

# =============================================================================
# Test: Each REGIME's exclusive vocabulary
# =============================================================================
print("-" * 70)
print("Exclusive PP vocabulary by REGIME")
print("-" * 70)
print()

for regime_name in sorted(regime_vocab.keys()):
    others = set()
    for other_name, other_vocab in regime_vocab.items():
        if other_name != regime_name:
            others.update(other_vocab)
    exclusive = regime_vocab[regime_name] - others
    print(f"{regime_name}: {len(exclusive)} exclusive PP MIDDLEs")
    if exclusive and len(exclusive) <= 10:
        print(f"  {sorted(exclusive)}")

print()

# =============================================================================
# Test: If we use REGIME_4-exclusive PP, which A entries match?
# =============================================================================
print("-" * 70)
print("A entries containing REGIME_4-exclusive PP")
print("-" * 70)
print()

if regime4_exclusive:
    # Build A entries
    a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
        lambda x: set(x.dropna())
    ).reset_index()
    a_entries.columns = ['folio', 'line', 'middles']

    # Count REGIME_4-exclusive PP overlap
    a_entries['r4_overlap'] = a_entries['middles'].apply(
        lambda x: len(x & regime4_exclusive) if x else 0
    )

    matching = a_entries[a_entries['r4_overlap'] > 0]
    print(f"A entries with any REGIME_4-exclusive PP: {len(matching)}")
    print(f"A entries with 2+ REGIME_4-exclusive PP: {len(a_entries[a_entries['r4_overlap'] >= 2])}")

    if len(matching) > 0:
        # Check if these A entries contain animal tokens
        animal_middles = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}

        animal_matches = 0
        for _, row in matching.iterrows():
            if row['middles'] & animal_middles:
                animal_matches += 1

        print(f"Of those, entries also containing animal RI tokens: {animal_matches}")

        if animal_matches > 0:
            print()
            print("*** A entries with BOTH REGIME_4-exclusive PP AND animal tokens ***")
            for _, row in matching[matching['middles'].apply(lambda x: bool(x & animal_middles))].head(10).iterrows():
                r4_tokens = row['middles'] & regime4_exclusive
                animal_tokens = row['middles'] & animal_middles
                print(f"  {row['folio']}:{row['line']}")
                print(f"    R4-exclusive: {r4_tokens}")
                print(f"    Animal: {animal_tokens}")
else:
    print("No REGIME_4-exclusive PP vocabulary found!")
    print("This means REGIME_4 shares ALL its PP vocabulary with other REGIMEs.")

print()

# =============================================================================
# VERDICT
# =============================================================================
print("=" * 70)
print("TEST 1 VERDICT")
print("=" * 70)
print()

exclusive_count = len(regime4_exclusive)
total_r4 = len(regime_vocab.get('REGIME_4', set()))

if exclusive_count == 0:
    print("RESULT: REGIME_4 has NO exclusive PP vocabulary!")
    print("All REGIME_4 PP MIDDLEs also appear in other REGIMEs.")
    print()
    print("IMPLICATION: Recipe fire degree CANNOT select A entries through PP alone.")
    print("REGIME is NOT discriminative at the vocabulary level.")
    print("This CONFIRMS why animal triangulation failed - all REGIMEs share PP space.")
elif exclusive_count < total_r4 * 0.1:
    print(f"RESULT: REGIME_4 has weak vocabulary distinctiveness ({exclusive_count}/{total_r4} = {exclusive_count/total_r4:.1%} exclusive)")
    print("Most REGIME_4 PP vocabulary overlaps with other REGIMEs.")
    print()
    print("IMPLICATION: Fire degree provides weak selection pressure.")
    print("Multi-dimensional conjunction may still help if other dimensions are more distinctive.")
else:
    print(f"RESULT: REGIME_4 has significant vocabulary distinctiveness ({exclusive_count}/{total_r4} = {exclusive_count/total_r4:.1%} exclusive)")
    print()
    print("IMPLICATION: Fire degree provides meaningful selection pressure.")
    print("Recipe triangulation via REGIME has discriminative power.")
