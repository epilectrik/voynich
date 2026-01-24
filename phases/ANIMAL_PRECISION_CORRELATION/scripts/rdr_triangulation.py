#!/usr/bin/env python3
"""
RDR Triangulation: Use multi-dimensional recipe constraints to find candidate B folios,
then trace back to A entries and check RI tokens.

Recipe: Hennen (Chicken)
Triangulation Vector:
  - regime: 4
  - material_class: animal
  - hazard_dominant: PHASE_ORDERING
  - zone_r: true (sound monitoring)
  - zone_p: true (sight monitoring)
  - escape_prediction: low
  - precision_level: high
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("RDR TRIANGULATION: Hennen (Chicken) Recipe")
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

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

# Get vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles  # PP tokens

print(f"A MIDDLEs: {len(a_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"Shared (PP tokens): {len(shared_middles)}")
print()

# =============================================================================
# STEP 1: Filter B folios by REGIME_4
# =============================================================================
print("-" * 70)
print("STEP 1: Filter by REGIME_4")
print("-" * 70)

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

# Get REGIME_4 folios
regime4_folios = set(regime_data['REGIME_4'])
print(f"REGIME_4 folios: {len(regime4_folios)}")
print(f"  {sorted(regime4_folios)[:10]}...")
print()

# =============================================================================
# STEP 2: Filter by zone affinity (R-zone enriched for sound monitoring)
# =============================================================================
print("-" * 70)
print("STEP 2: Filter by zone affinity")
print("-" * 70)

# Load zone data
zone_path = PROJECT_ROOT / 'results' / 'middle_zone_survival.json'
with open(zone_path, 'r') as f:
    zone_data = json.load(f)

# Get R-cluster MIDDLEs (sound-associated)
r_cluster_middles = set(zone_data['clustering']['clusters']['3']['example_middles'])
print(f"R-cluster example MIDDLEs: {r_cluster_middles}")

# For each REGIME_4 folio, count R-cluster MIDDLE presence
folio_r_scores = {}
for folio in regime4_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    folio_middles = set(folio_tokens['middle'].dropna().unique())
    r_count = len(folio_middles & r_cluster_middles)
    folio_r_scores[folio] = r_count

# Filter to folios with R-cluster presence
r_filtered = {f for f, c in folio_r_scores.items() if c >= 1}
print(f"REGIME_4 folios with R-cluster MIDDLEs: {len(r_filtered)}")
print()

# =============================================================================
# STEP 3: Combine filters
# =============================================================================
print("-" * 70)
print("STEP 3: Combine REGIME_4 + zone filters")
print("-" * 70)

# REGIME_4 already has low escape (0.52x average) by definition
# Use R-filtered if we have matches, otherwise all REGIME_4
if r_filtered:
    candidate_folios = r_filtered
    print(f"Using R-zone filtered REGIME_4 folios: {len(candidate_folios)}")
else:
    candidate_folios = regime4_folios
    print(f"No R-zone filter matches - using all REGIME_4: {len(candidate_folios)}")
print(f"\nCandidate B folios after triangulation: {len(candidate_folios)}")
print(f"  {sorted(candidate_folios)}")
print()

# =============================================================================
# STEP 4: Extract PP vocabulary from candidate folios
# =============================================================================
print("-" * 70)
print("STEP 4: Extract PP vocabulary from candidates")
print("-" * 70)

# Get all MIDDLEs from candidate folios
candidate_middles = set()
for folio in candidate_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    candidate_middles.update(folio_tokens['middle'].dropna().unique())

# Filter to shared (PP) MIDDLEs only
candidate_pp = candidate_middles & shared_middles

# Filter out infrastructure tokens (universal connectors)
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
discriminative_pp = candidate_pp - infrastructure

print(f"Total MIDDLEs in candidate folios: {len(candidate_middles)}")
print(f"Of which are PP (shared with A): {len(candidate_pp)}")
print(f"Discriminative PP (no infrastructure): {len(discriminative_pp)}")
print()

# =============================================================================
# STEP 5: Find A entries containing discriminative PP combinations
# =============================================================================
print("-" * 70)
print("STEP 5: Trace PP tokens to A entries")
print("-" * 70)

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Count discriminative PP overlap for each A entry
a_entries['pp_overlap'] = a_entries['middles'].apply(
    lambda x: len(x & discriminative_pp) if x else 0
)

# Filter to entries with multiple PP token overlap
min_overlap = 3
matching_entries = a_entries[a_entries['pp_overlap'] >= min_overlap].copy()
matching_entries = matching_entries.sort_values('pp_overlap', ascending=False)

print(f"A entries with >={min_overlap} discriminative PP tokens: {len(matching_entries)}")

if len(matching_entries) > 0:
    print("\nTop matching A entries:")
    for _, row in matching_entries.head(15).iterrows():
        overlap = row['middles'] & discriminative_pp
        print(f"  {row['folio']}:{row['line']} - PP overlap={row['pp_overlap']}")
        if row['pp_overlap'] >= 4:
            print(f"    Matching: {overlap}")

# =============================================================================
# STEP 6: Check RI tokens in matching A entries
# =============================================================================
print()
print("-" * 70)
print("STEP 6: Check RI tokens for animal class")
print("-" * 70)

if len(matching_entries) > 0:
    # Collect all MIDDLEs from matching entries
    matching_middles = set()
    for _, row in matching_entries.iterrows():
        matching_middles.update(row['middles'])

    # RI = in these A entries but NOT in B
    ri_middles = matching_middles - b_middles
    print(f"Total MIDDLEs in matching A entries: {len(matching_middles)}")
    print(f"Of which are RI (not in B): {len(ri_middles)}")

    # Load animal priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                     for item in priors_data['results']}

    # Check animal priors for RI tokens
    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_middles
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"\nRI MIDDLEs with P(animal) > 0: {len(ri_animal)}")

    if ri_animal:
        print("\n*** ANIMAL-ASSOCIATED RI TOKENS IN TRACED A ENTRIES ***")
        for m, p in sorted(ri_animal, key=lambda x: -x[1])[:15]:
            print(f"  {m}: P(animal) = {p:.2f}")

        # Count high-confidence animal tokens
        high_animal = [m for m, p in ri_animal if p >= 0.5]
        print(f"\nRI tokens with P(animal) >= 0.5: {len(high_animal)}")

        if high_animal:
            print("RESULT: Found animal-associated RI tokens in traced A entries!")
        else:
            print("RESULT: Animal signal present but weak (all P < 0.5)")
    else:
        print("RESULT: No animal-associated RI tokens found")
else:
    print("No matching A entries to check")

# =============================================================================
# SUMMARY
# =============================================================================
print()
print("=" * 70)
print("TRIANGULATION SUMMARY")
print("=" * 70)
print()
print("Recipe: Hennen (Chicken)")
print("Triangulation constraints:")
print("  - REGIME_4 (fire degree 4)")
print("  - R-zone affinity (sound monitoring)")
print("  - Low escape architecture")
print()
print(f"Pipeline:")
print(f"  83 B folios -> {len(regime4_folios)} REGIME_4 -> {len(candidate_folios)} after zone filter")
print(f"  {len(discriminative_pp)} discriminative PP tokens extracted")
print(f"  {len(matching_entries)} A entries with >={min_overlap} PP overlap")
if len(matching_entries) > 0:
    print(f"  {len(ri_middles)} RI tokens in those entries")
    print(f"  {len(ri_animal)} with animal priors > 0")
