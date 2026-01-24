#!/usr/bin/env python3
"""
AZC Zone Trace: Use zone affinity to filter A entries

Approach:
1. REGIME_4 has 54.7% S-zone affinity
2. Identify S-cluster MIDDLEs (boundary-surviving)
3. Find A entries containing S-cluster MIDDLEs
4. Check if those entries have animal-associated RIs
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load zone survival data
with open(PROJECT_ROOT / 'results' / 'middle_zone_survival.json', 'r') as f:
    zone_data = json.load(f)

print("=" * 70)
print("AZC ZONE TRACE")
print("=" * 70)
print()

# Get S-cluster MIDDLEs
s_cluster = zone_data['clustering']['clusters']['1']
print(f"S-cluster (boundary-surviving): n={s_cluster['size']}")
print(f"Mean S-zone affinity: {s_cluster['mean_profile']['S']:.1%}")
print(f"Example MIDDLEs: {s_cluster['example_middles']}")

# Check if full mapping exists
if 'middle_to_cluster' in zone_data:
    middle_to_cluster = zone_data['middle_to_cluster']
    s_middles = [m for m, c in middle_to_cluster.items() if c == 1]
    print(f"\nFull S-cluster MIDDLEs: {len(s_middles)}")
    print(f"  {s_middles}")
else:
    print("\nNo full middle_to_cluster mapping in data.")
    s_middles = s_cluster['example_middles']
    print(f"Using example MIDDLEs only: {len(s_middles)}")

print()
print("-" * 70)
print("TRACE: S-cluster MIDDLEs -> A entries -> RI priors")
print("-" * 70)
print()

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Simplified morphology
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

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Find A entries containing S-cluster MIDDLEs
s_middle_set = set(s_middles)
a_entries['s_cluster_count'] = a_entries['middles'].apply(lambda x: len(x & s_middle_set) if x else 0)

# Filter to entries with >=2 S-cluster MIDDLEs
s_filtered = a_entries[a_entries['s_cluster_count'] >= 2].sort_values('s_cluster_count', ascending=False)
print(f"A entries with >=2 S-cluster MIDDLEs: {len(s_filtered)}")

if len(s_filtered) > 0:
    print("\nTop S-cluster-enriched A entries:")
    for _, row in s_filtered.head(15).iterrows():
        s_overlap = row['middles'] & s_middle_set
        print(f"  {row['folio']}:{row['line']} - S-cluster={row['s_cluster_count']}")
        print(f"    Matching: {s_overlap}")

    # Collect all MIDDLEs from S-filtered entries
    s_entry_middles = set()
    for _, row in s_filtered.iterrows():
        s_entry_middles.update(row['middles'])

    # RI MIDDLEs = those not in B
    b_middles = set(df_b['middle'].dropna().unique())
    ri_middles = s_entry_middles - b_middles
    print(f"\nRI MIDDLEs in S-enriched A entries: {len(ri_middles)}")

    # Check animal priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {}) for item in priors_data['results']}

    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_middles
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"RI MIDDLEs with animal > 0: {len(ri_animal)}")
    if ri_animal:
        print("\nAnimal-associated RI MIDDLEs in S-cluster-enriched A entries:")
        for m, p in sorted(ri_animal, key=lambda x: -x[1])[:15]:
            print(f"  {m}: P(animal)={p:.2f}")
else:
    print("No A entries found with >=2 S-cluster MIDDLEs.")
    print("S-cluster MIDDLEs may be too specialized for A entry matching.")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()
print("""
The AZC zone trace filters A entries by S-zone affinity, which should be
more relevant for REGIME_4 (precision procedures).

If S-enriched A entries show elevated animal-associated RIs compared to
the baseline, this supports a causal pathway:

  Animal material -> A entry (with S-cluster MIDDLEs) -> AZC S-zone legal
  -> REGIME_4 B folio execution

This doesn't prove 1:1 matching, but shows category-level coherence.
""")
