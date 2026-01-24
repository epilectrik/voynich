#!/usr/bin/env python3
"""
Rose Water Triangulation

Using predicted PREFIX profile from Brunschwig:
- fire_degree: 1
- predicted_regime: REGIME_2 (WATER_GENTLE)
- predicted_prefix_profile: ol=0.4, da=0.3, qo=0.15

Rose profile (opposite of chicken):
- High ol (stable/structural)
- Moderate da (direct action)
- Low qo (minimal escape/recovery)
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("ROSE WATER TRIANGULATION")
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

# Vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

all_b_folios = set(df_b['folio'].unique())

# =============================================================================
# Step 1: Rose profile constraints
# =============================================================================
print("-" * 70)
print("Step 1: Rose profile constraints")
print("-" * 70)
print()

print("Rose predicted profile:")
print("  REGIME: REGIME_1 or REGIME_2 (fire degree 1)")
print("  PREFIX: high ol (40%), moderate da (30%), low qo (15%)")
print()

# Get REGIME_1 and REGIME_2 folios
regime1_folios = set(regime_data.get('REGIME_1', []))
regime2_folios = set(regime_data.get('REGIME_2', []))
rose_regime_folios = regime1_folios | regime2_folios

print(f"REGIME_1 folios: {len(regime1_folios)}")
print(f"REGIME_2 folios: {len(regime2_folios)}")
print(f"Combined: {len(rose_regime_folios)}")
print()

# =============================================================================
# Step 2: Compute PREFIX profiles for all B folios
# =============================================================================
print("-" * 70)
print("Step 2: PREFIX profile filtering")
print("-" * 70)
print()

folio_profiles = {}
for folio in all_b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    if total > 0:
        folio_profiles[folio] = {
            'ol': prefix_counts.get('ol', 0) / total,
            'da': prefix_counts.get('da', 0) / total,
            'qo': prefix_counts.get('qo', 0) / total,
            'ok': prefix_counts.get('ok', 0) / total,
            'ot': prefix_counts.get('ot', 0) / total,
        }

# Compute averages
avg_ol = sum(p['ol'] for p in folio_profiles.values()) / len(folio_profiles)
avg_da = sum(p['da'] for p in folio_profiles.values()) / len(folio_profiles)
avg_qo = sum(p['qo'] for p in folio_profiles.values()) / len(folio_profiles)

print(f"Average PREFIX ratios:")
print(f"  ol: {avg_ol:.1%}")
print(f"  da: {avg_da:.1%}")
print(f"  qo: {avg_qo:.1%}")
print()

# Rose profile: high ol, moderate+ da, low qo
high_ol_folios = {f for f, p in folio_profiles.items() if p['ol'] >= avg_ol}
high_da_folios = {f for f, p in folio_profiles.items() if p['da'] >= avg_da}
low_qo_folios = {f for f, p in folio_profiles.items() if p['qo'] <= avg_qo}

print(f"High ol (>={avg_ol:.1%}): {len(high_ol_folios)} folios")
print(f"High da (>={avg_da:.1%}): {len(high_da_folios)} folios")
print(f"Low qo (<={avg_qo:.1%}): {len(low_qo_folios)} folios")
print()

# =============================================================================
# Step 3: Multi-dimensional conjunction
# =============================================================================
print("-" * 70)
print("Step 3: Multi-dimensional conjunction")
print("-" * 70)
print()

# Rose conjunction: REGIME_1/2 + high ol + high da + low qo
rose_conj_2d = rose_regime_folios & high_ol_folios
rose_conj_3d = rose_conj_2d & low_qo_folios
rose_conj_4d = rose_conj_3d & high_da_folios

print(f"REGIME_1/2: {len(rose_regime_folios)} folios")
print(f"REGIME + high ol: {len(rose_conj_2d)} folios")
print(f"REGIME + high ol + low qo: {len(rose_conj_3d)} folios")
print(f"REGIME + high ol + low qo + high da: {len(rose_conj_4d)} folios")

if rose_conj_4d:
    print(f"  Rose candidate folios: {sorted(rose_conj_4d)}")
print()

# Use 3D conjunction if 4D is too narrow
rose_folios = rose_conj_3d if len(rose_conj_4d) < 3 else rose_conj_4d
print(f"Using {len(rose_folios)} folios for PP extraction")
print()

# =============================================================================
# Step 4: Extract PP vocabulary
# =============================================================================
print("-" * 70)
print("Step 4: Extract PP vocabulary")
print("-" * 70)
print()

infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

rose_middles = set()
for folio in rose_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    rose_middles.update(folio_tokens['middle'].dropna().unique())

rose_pp = (rose_middles & shared_middles) - infrastructure
print(f"Rose PP vocabulary: {len(rose_pp)} tokens")
print()

# =============================================================================
# Step 5: Find A RECORDS with PP convergence
# =============================================================================
print("-" * 70)
print("Step 5: A RECORD convergence")
print("-" * 70)
print()

# Build A records
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()
a_records.columns = ['folio', 'line', 'middles', 'words']
a_records['record_id'] = a_records['folio'] + ':' + a_records['line'].astype(str)

# Count PP convergence
a_records['rose_pp_count'] = a_records['middles'].apply(lambda x: len(x & rose_pp))

# Get records with 3+ PP convergence
high_conv = a_records[a_records['rose_pp_count'] >= 3].copy()
high_conv = high_conv.sort_values('rose_pp_count', ascending=False)

print(f"A records with 3+ rose PP: {len(high_conv)}")
print()

# =============================================================================
# Step 6: Extract RI and check plant priors
# =============================================================================
print("-" * 70)
print("Step 6: Extract RI tokens with plant priors")
print("-" * 70)
print()

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                 for item in priors_data['results']}

# Extract RI from high-convergence records
all_ri = set()
ri_with_plant = []

for _, row in high_conv.iterrows():
    ri = row['middles'] - b_middles
    all_ri.update(ri)

    for token in ri:
        if token in priors_lookup:
            plant_prob = priors_lookup[token].get('plant', 0)
            if plant_prob > 0:
                ri_with_plant.append((token, plant_prob, row['record_id']))

print(f"Total RI tokens in converging records: {len(all_ri)}")
print(f"RI tokens with P(plant) > 0: {len(set(t for t,_,_ in ri_with_plant))}")
print()

# Show plant candidates
if ri_with_plant:
    # Deduplicate and sort by probability
    plant_tokens = {}
    for token, prob, record in ri_with_plant:
        if token not in plant_tokens or prob > plant_tokens[token][0]:
            plant_tokens[token] = (prob, record)

    print("Plant-associated RI tokens:")
    for token, (prob, record) in sorted(plant_tokens.items(), key=lambda x: -x[1][0])[:15]:
        print(f"  {token}: P(plant) = {prob:.2f} (in {record})")

# =============================================================================
# Step 7: Check unique PP patterns
# =============================================================================
print()
print("-" * 70)
print("Step 7: Top converging records with RI")
print("-" * 70)
print()

# Show top records
for _, row in high_conv.head(10).iterrows():
    ri = row['middles'] - b_middles
    pp_overlap = row['middles'] & rose_pp

    # Check for plant RI
    plant_ri = {t for t in ri if t in priors_lookup and priors_lookup[t].get('plant', 0) > 0}

    print(f"{row['record_id']}: {row['rose_pp_count']} PP")
    print(f"  PP: {sorted(pp_overlap)[:8]}...")
    print(f"  RI: {ri}")
    if plant_ri:
        print(f"  *** PLANT RI: {plant_ri} ***")
    print()

# =============================================================================
# Step 8: Compare with chicken results
# =============================================================================
print("-" * 70)
print("Step 8: Compare with chicken triangulation")
print("-" * 70)
print()

# Chicken folios from previous analysis
chicken_folios = {'f40v', 'f41v', 'f85r1', 'f94v', 'f95v1'}
animal_ri = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}

# Check overlap
folio_overlap = rose_folios & chicken_folios
print(f"Rose folios: {len(rose_folios)}")
print(f"Chicken folios: {len(chicken_folios)}")
print(f"Overlap: {len(folio_overlap)}")
if folio_overlap:
    print(f"  {folio_overlap}")
print()

# Check if rose records contain animal RI
rose_records = set(high_conv['record_id'])
animal_in_rose = 0
for _, row in high_conv.iterrows():
    ri = row['middles'] - b_middles
    if ri & animal_ri:
        animal_in_rose += 1

print(f"Rose-converging records containing animal RI: {animal_in_rose}")
print()

# =============================================================================
# VERDICT
# =============================================================================
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

if ri_with_plant:
    best_plant = max(plant_tokens.items(), key=lambda x: x[1][0])
    print(f"Best rose candidate: {best_plant[0]} (P(plant) = {best_plant[1][0]:.2f})")
    print(f"  Found in record: {best_plant[1][1]}")
else:
    print("No plant-associated RI tokens found in converging records.")
    print("May need to adjust constraints or check if rose is in the corpus.")
