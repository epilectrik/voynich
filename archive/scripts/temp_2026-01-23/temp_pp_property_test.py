#!/usr/bin/env python3
"""
Enhanced Reverse Brunschwig Test: PP -> Properties

Hypothesis: PP MIDDLEs encode material properties.
Test: A records sharing rare PP MIDDLEs should map to Brunschwig
materials with similar properties (fire_degree, material_class, etc.)

Method:
1. Load PP MIDDLEs and their A record distributions
2. For each rare PP MIDDLE, find which B folios heavily use it
3. Map those B folios to REGIME (fire_degree proxy)
4. Check if PP MIDDLEs cluster by property dimension
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class mapping for MIDDLE extraction
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)
token_to_middle = class_map['token_to_middle']

# Extract MIDDLEs
def get_middle(token):
    if pd.isna(token):
        return None
    return token_to_middle.get(token, None)

df['middle'] = df['word'].apply(get_middle)

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Identify PP MIDDLEs (appear in both A and B)
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
pp_middles = a_middles & b_middles
ri_middles = a_middles - b_middles

print(f"PP MIDDLEs (shared A&B): {len(pp_middles)}")
print(f"RI MIDDLEs (A-only): {len(ri_middles)}")

# ============================================================
# STEP 1: PP MIDDLE frequency in B (by folio)
# ============================================================
print("\n" + "="*60)
print("STEP 1: PP MIDDLE FREQUENCY IN B")
print("="*60)

# Count PP frequency in B
b_middle_counts = Counter(df_b['middle'].dropna())
pp_freq_in_b = {m: b_middle_counts.get(m, 0) for m in pp_middles}

# Sort by frequency
pp_by_freq = sorted(pp_freq_in_b.items(), key=lambda x: -x[1])
print("\nMost common PP MIDDLEs in B:")
for m, cnt in pp_by_freq[:15]:
    print(f"  '{m}': {cnt}")

print("\nRarest PP MIDDLEs in B (non-zero):")
rare_pp = [(m, cnt) for m, cnt in pp_by_freq if cnt > 0][-15:]
for m, cnt in rare_pp:
    print(f"  '{m}': {cnt}")

# ============================================================
# STEP 2: Which B folios use which PP MIDDLEs?
# ============================================================
print("\n" + "="*60)
print("STEP 2: PP MIDDLE -> B FOLIO MAPPING")
print("="*60)

# For each PP MIDDLE, find which B folios have it
pp_to_folios = defaultdict(set)
for _, row in df_b.iterrows():
    m = row['middle']
    if m in pp_middles:
        pp_to_folios[m].add(row['folio'])

# Load REGIME mapping
try:
    with open('phases/ANIMAL_PRECISION_CORRELATION/results/regime_folio_mapping.json') as f:
        regime_map = json.load(f)
    # Invert: folio -> regime
    folio_to_regime = {}
    for regime, folios in regime_map.items():
        for f in folios:
            folio_to_regime[f] = int(regime.replace('REGIME_', ''))
except:
    regime_map = None
    folio_to_regime = {}
    print("Warning: No regime mapping found")

# For rare PP MIDDLEs, check their REGIME distribution
print("\nRare PP MIDDLEs and their REGIME distribution:")
for m, cnt in rare_pp[:10]:
    folios = pp_to_folios[m]
    regimes = [folio_to_regime.get(f) for f in folios if f in folio_to_regime]
    regime_dist = Counter(regimes)
    print(f"  '{m}' ({cnt} in B): folios={len(folios)}, regimes={dict(regime_dist)}")

# ============================================================
# STEP 3: Cluster PP by REGIME affinity
# ============================================================
print("\n" + "="*60)
print("STEP 3: PP MIDDLEs BY PRIMARY REGIME")
print("="*60)

# For each PP MIDDLE, compute its primary regime
pp_primary_regime = {}
for m in pp_middles:
    if m in pp_to_folios:
        folios = pp_to_folios[m]
        regimes = [folio_to_regime.get(f) for f in folios if f in folio_to_regime]
        if regimes:
            # Most common regime
            most_common = Counter(regimes).most_common(1)[0][0]
            pp_primary_regime[m] = most_common

# Group PP by primary regime
regime_to_pp = defaultdict(list)
for m, regime in pp_primary_regime.items():
    regime_to_pp[regime].append(m)

for regime in sorted(regime_to_pp.keys()):
    middles = regime_to_pp[regime]
    print(f"\nREGIME_{regime} preferred PP MIDDLEs ({len(middles)}):")
    # Show top ones by frequency
    sorted_m = sorted(middles, key=lambda x: pp_freq_in_b.get(x, 0), reverse=True)
    for m in sorted_m[:10]:
        print(f"  '{m}' ({pp_freq_in_b.get(m, 0)} in B)")

# ============================================================
# STEP 4: Check if PP MIDDLEs correlate with instruction sequence
# ============================================================
print("\n" + "="*60)
print("STEP 4: PP -> INSTRUCTION SEQUENCE CORRELATION")
print("="*60)

# Load Brunschwig data
with open('data/brunschwig_complete.json', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

# Create property groups
fire_to_materials = defaultdict(list)
seq_to_materials = defaultdict(list)
class_to_materials = defaultdict(list)

for r in recipes:
    fire = r.get('fire_degree')
    seq = tuple(r.get('instruction_sequence') or [])
    mat_class = r.get('material_class')
    name = r['name_english']

    if fire:
        fire_to_materials[fire].append(name)
    if seq:
        seq_to_materials[seq].append(name)
    if mat_class:
        class_to_materials[mat_class].append(name)

# Show the specialized sequences and their materials
print("\nSpecialized instruction sequences:")
for seq, materials in seq_to_materials.items():
    if seq != ('AUX', 'e_ESCAPE') and len(materials) > 0:
        print(f"  {list(seq)}: {materials[:5]}")

# ============================================================
# STEP 5: The test - do A records with same rare PP share properties?
# ============================================================
print("\n" + "="*60)
print("STEP 5: A RECORDS BY RARE PP CLUSTER")
print("="*60)

# Build A record -> PP set mapping
a_records = df_a.groupby(['folio', 'line'])['middle'].apply(
    lambda x: set(x.dropna()) & pp_middles
).reset_index()
a_records.columns = ['folio', 'line', 'pp_set']
a_records['record'] = a_records['folio'] + ':' + a_records['line'].astype(str)

# Filter to records with at least 2 PP
a_records = a_records[a_records['pp_set'].apply(len) >= 2]

print(f"\nA records with 2+ PP MIDDLEs: {len(a_records)}")

# Find A records that share rare PP MIDDLEs
rare_pp_set = set(m for m, cnt in rare_pp)

# For each rare PP, find A records containing it
rare_pp_records = defaultdict(list)
for _, row in a_records.iterrows():
    for m in row['pp_set'] & rare_pp_set:
        rare_pp_records[m].append(row['record'])

print("\nRare PP MIDDLEs and their A records:")
for m in list(rare_pp_set)[:10]:
    records = rare_pp_records[m]
    if records:
        print(f"  '{m}': {len(records)} A records ({records[:3]}...)")

# ============================================================
# STEP 6: Map rare PP to Brunschwig properties
# ============================================================
print("\n" + "="*60)
print("STEP 6: RARE PP -> PROPERTY INFERENCE")
print("="*60)

# For each rare PP, determine which REGIME it prefers
# Then map that REGIME to Brunschwig fire_degree
print("\nRare PP -> REGIME -> fire_degree -> material property:")
for m, cnt in rare_pp[:10]:
    if m in pp_primary_regime:
        regime = pp_primary_regime[m]
        # Regime 4 = fire_degree 4 = animals
        # Regime 2 = fire_degree 2 = most herbs
        # etc.
        materials_at_fire = fire_to_materials.get(regime, [])
        print(f"\n  '{m}' (B count={cnt}):")
        print(f"    Primary REGIME: {regime}")
        print(f"    Fire {regime} materials ({len(materials_at_fire)}): {materials_at_fire[:5]}")
