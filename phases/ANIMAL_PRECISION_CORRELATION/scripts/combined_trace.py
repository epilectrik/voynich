#!/usr/bin/env python3
"""
Combined Trace: B folio vocabulary + AZC zone affinity

Approach:
1. Get f43v's MIDDLEs
2. Check which of those have S-zone affinity
3. Find A entries containing S-zone-compatible MIDDLEs from f43v
4. Check those entries for animal-associated RIs
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load zone data
with open(PROJECT_ROOT / 'results' / 'middle_zone_survival.json', 'r') as f:
    zone_data = json.load(f)

s_cluster_middles = set(zone_data['clustering']['clusters']['1']['example_middles'])

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

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared = a_middles & b_middles

print("=" * 70)
print("COMBINED TRACE: B folio + AZC zone affinity")
print("=" * 70)
print()

# Get f43v vocabulary
candidate = 'f43v'
f_tokens = df_b[df_b['folio'] == candidate]
f_middles = set(f_tokens['middle'].dropna().unique())
f_shared = f_middles & shared

print(f"B folio: {candidate}")
print(f"Total MIDDLEs: {len(f_middles)}")
print(f"Shared with A: {len(f_shared)}")

# Which of f43v's MIDDLEs are S-cluster?
f_s_middles = f_shared & s_cluster_middles
print(f"S-cluster MIDDLEs in {candidate}: {f_s_middles}")

# If few/none, expand to check broader zone affinity
print()
print("Checking zone affinity for all f43v MIDDLEs...")
print()

# We don't have full MIDDLE->zone mapping, but we can check overlap with each cluster
p_cluster = set(zone_data['clustering']['clusters']['2']['example_middles'])
r_cluster = set(zone_data['clustering']['clusters']['3']['example_middles'])

f_p = f_shared & p_cluster
f_r = f_shared & r_cluster
f_s = f_shared & s_cluster_middles

print(f"  P-cluster (intervention): {f_p}")
print(f"  R-cluster (restriction): {f_r}")
print(f"  S-cluster (boundary): {f_s}")

print()
print("-" * 70)
print("ALTERNATIVE: Trace via specific B folio vocabulary (no zone filter)")
print("-" * 70)
print()

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Count overlap with f43v's shared MIDDLEs
a_entries['b_overlap'] = a_entries['middles'].apply(lambda x: len(x & f_shared) if x else 0)

# Also count S-cluster overlap
a_entries['s_overlap'] = a_entries['middles'].apply(lambda x: len(x & s_cluster_middles) if x else 0)

# Combined score: B overlap + S-zone bonus
a_entries['combined'] = a_entries['b_overlap'] + a_entries['s_overlap'] * 2

# Sort by combined
top = a_entries.sort_values('combined', ascending=False).head(20)
print(f"Top 20 A entries by combined score (B_overlap + 2*S_cluster):")
print()

for _, row in top.iterrows():
    b_match = row['middles'] & f_shared
    s_match = row['middles'] & s_cluster_middles
    print(f"  {row['folio']}:{row['line']} - combined={row['combined']} "
          f"(B={row['b_overlap']}, S={row['s_overlap']})")
    if row['combined'] >= 6:
        print(f"    B-overlap: {b_match}")
        print(f"    S-cluster: {s_match}")

# Take top candidates and check RIs
print()
print("-" * 70)
print("RI CHECK for top combined candidates")
print("-" * 70)
print()

top_entries = a_entries[a_entries['combined'] >= 5]
print(f"A entries with combined >= 5: {len(top_entries)}")

if len(top_entries) > 0:
    top_middles = set()
    for _, row in top_entries.iterrows():
        top_middles.update(row['middles'])

    ri_top = top_middles - b_middles
    print(f"RI MIDDLEs in top candidates: {len(ri_top)}")

    # Check priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {}) for item in priors_data['results']}

    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_top
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"RI MIDDLEs with animal > 0: {len(ri_animal)}")
    if ri_animal:
        for m, p in sorted(ri_animal, key=lambda x: -x[1])[:10]:
            print(f"  {m}: P(animal)={p:.2f}")
else:
    print("No candidates meet threshold.")

# Final check: does f43v itself contain any MIDDLEs from the animal-associated priors?
print()
print("-" * 70)
print("DIRECT CHECK: Animal-prior MIDDLEs in f43v")
print("-" * 70)
print()

# Get all MIDDLEs with animal > 0.5
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

animal_middles = {item['middle'] for item in priors_data['results']
                  if item.get('material_class_posterior', {}).get('animal', 0) > 0.5}

f43v_animal = f_middles & animal_middles
print(f"MIDDLEs with P(animal) > 0.5 in corpus: {len(animal_middles)}")
print(f"Of those appearing in f43v: {len(f43v_animal)}")
if f43v_animal:
    print(f"  {f43v_animal}")
else:
    print("  None - f43v doesn't directly contain high-animal MIDDLEs")
    print("  (This is expected - animal-associated MIDDLEs are mostly RI)")
