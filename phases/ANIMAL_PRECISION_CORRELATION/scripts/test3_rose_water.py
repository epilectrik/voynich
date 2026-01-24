#!/usr/bin/env python3
"""
TEST 3: Rose water triangulation (control)

Rose water (rosen/rose) should be:
- Plant-based (not animal)
- First or second degree fire (REGIME_1 or REGIME_2)
- Different instruction patterns than animal recipes

This tests if a different recipe connects to different A entries.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("TEST 3: Rose water triangulation (control)")
print("=" * 70)
print()

# =============================================================================
# Step 1: Extract rose water characteristics from Brunschwig
# =============================================================================
print("-" * 70)
print("Step 1: Rose water characteristics")
print("-" * 70)
print()

d = json.load(open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', encoding='utf-8'))

rose_materials = [m for m in d['materials'] if m['name_normalized'] in ['rosen', 'rose']]

for m in rose_materials:
    name = m['name_normalized']
    fire = m.get('fire_degree')
    source = m.get('material_source')
    seq = m.get('instruction_sequence', [])
    steps = len(m.get('procedural_steps', []))
    print(f"{name}:")
    print(f"  Fire degree: {fire}")
    print(f"  Source: {source}")
    print(f"  Instruction sequence: {seq}")
    print(f"  Steps: {steps}")
    print()

# Get representative rose material
rose = rose_materials[0] if rose_materials else None

if not rose:
    print("ERROR: No rose water material found!")
    exit(1)

rose_fire_degree = rose.get('fire_degree')
rose_source = rose.get('material_source')
rose_seq = rose.get('instruction_sequence', [])

print(f"Using: {rose['name_normalized']}")
print(f"Fire degree: {rose_fire_degree} -> REGIME_{rose_fire_degree}")
print(f"Source: {rose_source}")
print()

# =============================================================================
# Step 2: Load transcript and regime data
# =============================================================================
print("-" * 70)
print("Step 2: Load data")
print("-" * 70)
print()

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

# Get vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

all_b_folios = set(df_b['folio'].unique())
print(f"Total B folios: {len(all_b_folios)}")
print()

# =============================================================================
# Step 3: Apply rose water constraints
# =============================================================================
print("-" * 70)
print("Step 3: Apply rose water constraints")
print("-" * 70)
print()

# Constraint 1: Fire degree -> REGIME
regime_key = f'REGIME_{rose_fire_degree}'
if regime_key in regime_data:
    rose_regime_folios = set(regime_data[regime_key])
else:
    # Try to find any regime containing this fire degree
    rose_regime_folios = set()
    for key in ['REGIME_1', 'REGIME_2', 'REGIME_MIXED']:
        if key in regime_data:
            rose_regime_folios.update(regime_data[key])

print(f"Constraint 1: {regime_key} -> {len(rose_regime_folios)} folios")

# Constraint 2: Plant source -> look for different PREFIX profile than animals
# Plants typically don't have the escape-heavy profile that animals do
# Check for lower qo (less escape/recovery needed for plant extraction)
folio_qo = {}
for folio in all_b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    folio_qo[folio] = prefix_counts.get('qo', 0) / total if total > 0 else 0

avg_qo = sum(folio_qo.values()) / len(folio_qo)
# Plants: LOW qo (opposite of animals)
low_qo_folios = {f for f, r in folio_qo.items() if r <= avg_qo}

print(f"Constraint 2: Low qo (<={avg_qo:.2%}) -> {len(low_qo_folios)} folios")

# Constraint 3: Check instruction sequence
# Rose has different sequence than animals
# Look for folios matching that operational profile
print(f"Rose instruction sequence: {rose_seq}")

# =============================================================================
# Step 4: Apply conjunction
# =============================================================================
print()
print("-" * 70)
print("Step 4: Apply conjunction")
print("-" * 70)
print()

# Just use REGIME for now (to compare with animal test)
rose_candidates = rose_regime_folios

# Add low qo constraint
rose_candidates_with_qo = rose_candidates & low_qo_folios

print(f"REGIME alone: {len(rose_candidates)} folios")
print(f"REGIME + Low qo: {len(rose_candidates_with_qo)} folios")

# =============================================================================
# Step 5: Extract PP vocabulary from candidates
# =============================================================================
print()
print("-" * 70)
print("Step 5: Extract PP vocabulary")
print("-" * 70)
print()

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

def get_folio_pp(folios):
    middles = set()
    for folio in folios:
        folio_tokens = df_b[df_b['folio'] == folio]
        middles.update(folio_tokens['middle'].dropna().unique())
    return (middles & shared_middles) - infrastructure

rose_pp = get_folio_pp(rose_candidates)
rose_pp_constrained = get_folio_pp(rose_candidates_with_qo)

print(f"REGIME-only PP: {len(rose_pp)} tokens")
print(f"REGIME+qo PP: {len(rose_pp_constrained)} tokens")

# =============================================================================
# Step 6: Trace to A entries
# =============================================================================
print()
print("-" * 70)
print("Step 6: Trace to A entries")
print("-" * 70)
print()

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Count PP overlap
a_entries['rose_overlap'] = a_entries['middles'].apply(
    lambda x: len(x & rose_pp) if x else 0
)

min_overlap = 3
rose_matches = a_entries[a_entries['rose_overlap'] >= min_overlap]
rose_matches = rose_matches.sort_values('rose_overlap', ascending=False)

print(f"A entries with >={min_overlap} rose PP tokens: {len(rose_matches)}")

if len(rose_matches) > 0:
    print()
    print("Top matching A entries:")
    for _, row in rose_matches.head(10).iterrows():
        overlap = row['middles'] & rose_pp
        print(f"  {row['folio']}:{row['line']} - {row['rose_overlap']} PP: {sorted(overlap)[:5]}...")

# =============================================================================
# Step 7: Check RI tokens in matched entries
# =============================================================================
print()
print("-" * 70)
print("Step 7: Check RI tokens for plant class")
print("-" * 70)
print()

if len(rose_matches) > 0:
    matching_middles = set()
    for _, row in rose_matches.iterrows():
        matching_middles.update(row['middles'])

    ri_middles = matching_middles - b_middles
    print(f"Total MIDDLEs in matching A entries: {len(matching_middles)}")
    print(f"Of which are RI (not in B): {len(ri_middles)}")

    # Load priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                     for item in priors_data['results']}

    # Check plant priors
    ri_plant = [(m, priors_lookup[m].get('plant', 0)) for m in ri_middles
                if m in priors_lookup and priors_lookup[m].get('plant', 0) > 0]
    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_middles
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"RI tokens with P(plant) > 0: {len(ri_plant)}")
    print(f"RI tokens with P(animal) > 0: {len(ri_animal)}")
    print()

    if ri_plant:
        print("Plant-associated RI tokens:")
        for m, p in sorted(ri_plant, key=lambda x: -x[1])[:10]:
            print(f"  {m}: P(plant) = {p:.2f}")

# =============================================================================
# Step 8: Compare with animal triangulation
# =============================================================================
print()
print("-" * 70)
print("Step 8: Compare rose vs animal triangulation")
print("-" * 70)
print()

# Animal tokens
animal_middles = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}

# Check if rose-matched A entries contain animal tokens
rose_animal_overlap = 0
for _, row in rose_matches.iterrows():
    if row['middles'] & animal_middles:
        rose_animal_overlap += 1

print(f"Rose-matched A entries: {len(rose_matches)}")
print(f"Of those, also containing animal tokens: {rose_animal_overlap}")

# Get REGIME_4 (animal) matched A entries for comparison
regime4_folios = set(regime_data.get('REGIME_4', []))
regime4_pp = get_folio_pp(regime4_folios)

a_entries['animal_overlap'] = a_entries['middles'].apply(
    lambda x: len(x & regime4_pp) if x else 0
)
animal_matches = a_entries[a_entries['animal_overlap'] >= min_overlap]

print(f"Animal-REGIME_4 matched A entries: {len(animal_matches)}")

# Overlap between rose and animal matches
rose_folios = set(rose_matches['folio'].unique())
animal_folios = set(animal_matches['folio'].unique())
overlap_folios = rose_folios & animal_folios

print(f"A folios in rose matches: {len(rose_folios)}")
print(f"A folios in animal matches: {len(animal_folios)}")
print(f"Overlap: {len(overlap_folios)}")

if overlap_folios:
    print(f"  Shared folios: {sorted(overlap_folios)}")

# =============================================================================
# VERDICT
# =============================================================================
print()
print("=" * 70)
print("TEST 3 VERDICT")
print("=" * 70)
print()

print(f"Rose water: Fire degree {rose_fire_degree}, {rose_source}")
print(f"Animals: Fire degree 4, animal source")
print()

# Key question: Do rose and animal map to DIFFERENT A entries?
if overlap_folios:
    pct_overlap = len(overlap_folios) / max(len(rose_folios), len(animal_folios)) * 100
    print(f"A folio overlap: {len(overlap_folios)} ({pct_overlap:.1f}%)")
    if pct_overlap > 50:
        print("RESULT: Rose and animal triangulations overlap SIGNIFICANTLY!")
        print("This suggests PP vocabulary is NOT discriminative by recipe.")
    else:
        print("RESULT: Rose and animal triangulations have SOME overlap.")
        print("PP provides partial discrimination.")
else:
    print("RESULT: Rose and animal triangulations are DISJOINT!")
    print("This suggests PP vocabulary IS discriminative by recipe type.")
