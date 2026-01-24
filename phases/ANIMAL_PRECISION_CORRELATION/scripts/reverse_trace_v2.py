#!/usr/bin/env python3
"""
Strict Reverse Trace v2: Using simplified morphology extraction
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Simplified morphology - same as check script
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin', 'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry', 'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en', 'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

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

print("=" * 70)
print("STRICT REVERSE TRACE v2")
print("=" * 70)
print()

# Compute B MIDDLE frequencies and ranks
b_counts = df_b['middle'].value_counts()
b_rank = {m: r for r, m in enumerate(b_counts.index, 1)}
print(f"Total unique MIDDLEs in B: {len(b_counts)}")

# Identify shared MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles
print(f"Shared MIDDLEs (A and B): {len(shared_middles)}")

# Test multiple REGIME_4 candidates
candidates = ['f43v', 'f34r', 'f55r']

for candidate_folio in candidates:
    print()
    print("=" * 70)
    print(f"CANDIDATE: {candidate_folio}")
    print("=" * 70)

    folio_tokens = df_b[df_b['folio'] == candidate_folio]
    folio_middles = set(folio_tokens['middle'].dropna().unique())
    folio_shared = folio_middles & shared_middles

    print(f"Unique MIDDLEs: {len(folio_middles)}")
    print(f"Shared with A: {len(folio_shared)}")

    # Rare MIDDLEs (rank > 100)
    folio_rare = {m for m in folio_shared if b_rank.get(m, 9999) > 100}
    print(f"Rare MIDDLEs (rank>100): {len(folio_rare)}")
    print(f"  {sorted(folio_rare)}")

    # Build A entries
    a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
    a_entries.columns = ['folio', 'line', 'middles']

    # Count rare overlap
    a_entries['rare_overlap'] = a_entries['middles'].apply(lambda x: len(x & folio_rare) if x else 0)

    # Find entries with >=2 rare MIDDLEs
    strict = a_entries[a_entries['rare_overlap'] >= 2].sort_values('rare_overlap', ascending=False)
    print(f"\nA entries with >=2 rare MIDDLEs: {len(strict)}")

    if len(strict) > 0:
        print("\nTop candidates:")
        for _, row in strict.head(10).iterrows():
            overlap = row['middles'] & folio_rare
            print(f"  {row['folio']}:{row['line']} - rare_overlap={row['rare_overlap']}")
            print(f"    Matching: {overlap}")

        # Check RI MIDDLEs with animal priors
        cand_middles = set()
        for _, row in strict.iterrows():
            cand_middles.update(row['middles'])
        ri_cand = cand_middles - b_middles
        print(f"\nRI MIDDLEs in candidates: {len(ri_cand)}")

        # Load priors
        priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
        with open(priors_path, 'r') as f:
            priors_data = json.load(f)
        priors_lookup = {item['middle']: item.get('material_class_posterior', {}) for item in priors_data['results']}

        ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_cand if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]
        print(f"RI MIDDLEs with animal > 0: {len(ri_animal)}")
        for m, p in sorted(ri_animal, key=lambda x: -x[1])[:10]:
            print(f"  {m}: P(animal)={p:.2f}")
    else:
        print("No candidates found.")

    # Also try total overlap approach
    a_entries['total_overlap'] = a_entries['middles'].apply(lambda x: len(x & folio_shared) if x else 0)
    high = a_entries[a_entries['total_overlap'] >= 8].sort_values('total_overlap', ascending=False)
    print(f"\nA entries with >=8 total overlap: {len(high)}")
    if len(high) > 0:
        for _, row in high.head(5).iterrows():
            print(f"  {row['folio']}:{row['line']} - overlap={row['total_overlap']}/{len(folio_shared)}")
