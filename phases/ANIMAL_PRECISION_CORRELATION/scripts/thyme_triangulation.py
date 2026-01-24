#!/usr/bin/env python3
"""
Triangulate quuendel (wild thyme) - a REGIME_4 herb via precision override.

Test hypothesis: Materials with specific procedures should yield converging
records with RI tokens, while generic materials (like rose) don't.

quuendel constraints:
- REGIME_4 (precision override)
- PP profile: da=0.4, qo=0.3, ol=0.2
- Instructions: RECOVERY -> UNKNOWN -> LINK
- Fire degree 2 (but elevated to REGIME_4 due to HIGH precision)
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t')
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
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_data = json.load(f)

# REGIME_4 folios (same as animals)
regime4_folios = set(regime_data.get('REGIME_4', []))

print("=" * 70)
print("QUUENDEL (Wild Thyme) TRIANGULATION")
print("=" * 70)
print()
print("Constraints from Brunschwig:")
print("  - REGIME_4 (precision override)")
print("  - PP profile: da=0.4, qo=0.3, ol=0.2")
print("  - Instructions: RECOVERY -> UNKNOWN -> LINK")
print()
print(f"REGIME_4 folios: {len(regime4_folios)}")
print()

# Build REGIME_4 PP vocabulary (same as for animals)
r4_b_middles = set()
for folio in regime4_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    r4_b_middles.update(folio_tokens['middle'].dropna().unique())

r4_pp = (r4_b_middles & shared) - infrastructure
print(f"REGIME_4 PP vocabulary: {len(r4_pp)} tokens")
print()

# Find A records converging on REGIME_4 PP
# Same method as chicken triangulation
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: list(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()

print("-" * 70)
print("Step 1: Find A records with 2+ REGIME_4 PP tokens")
print("-" * 70)
print()

converging_records = []
for _, row in a_records.iterrows():
    middles = set(row['middle']) - infrastructure
    pp_overlap = middles & r4_pp
    ri_tokens = middles - b_middles

    if len(pp_overlap) >= 2:  # At least 2 PP tokens in common with REGIME_4
        converging_records.append({
            'folio': row['folio'],
            'line': row['line_number'],
            'middles': middles,
            'pp_overlap': pp_overlap,
            'ri': ri_tokens,
            'n_pp': len(pp_overlap),
            'n_ri': len(ri_tokens)
        })

print(f"Records with 2+ REGIME_4 PP: {len(converging_records)}")
print()

# Show top converging records
print("-" * 70)
print("Step 2: Top converging records (sorted by PP count)")
print("-" * 70)
print()

converging_records.sort(key=lambda x: (-x['n_pp'], -x['n_ri']))
for r in converging_records[:15]:
    print(f"{r['folio']}:{r['line']}: {r['n_pp']} PP, {r['n_ri']} RI")
    print(f"  PP tokens: {sorted(r['pp_overlap'])[:8]}")
    if r['ri']:
        print(f"  RI tokens: {sorted(r['ri'])}")
    print()

# Load material class priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

class_lookup = {}
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    if posterior:
        class_lookup[middle] = posterior

print("-" * 70)
print("Step 3: Check RI tokens for 'herb' class priors")
print("-" * 70)
print()

# Collect all RI from converging records
all_ri = set()
for r in converging_records:
    all_ri.update(r['ri'])

# Check herb priors
herb_ri = []
for ri in all_ri:
    if ri in class_lookup:
        priors = class_lookup[ri]
        herb_prob = priors.get('herb', 0) + priors.get('hot_dry_herb', 0) + priors.get('moderate_herb', 0)
        if herb_prob > 0:
            herb_ri.append({
                'token': ri,
                'herb_prob': herb_prob,
                'all_priors': priors
            })

herb_ri.sort(key=lambda x: -x['herb_prob'])

print(f"RI tokens with herb-class priors: {len(herb_ri)}")
print()

for item in herb_ri[:15]:
    print(f"{item['token']}: P(herb)={item['herb_prob']:.2f}")
    # Show which converging records contain this token
    containing_records = [r for r in converging_records if item['token'] in r['ri']]
    if containing_records:
        locs = [r['folio'] + ':' + str(r['line']) for r in containing_records[:3]]
        print(f"  In records: {locs}")
    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

# Compare to chicken (for reference)
print("Comparison to chicken triangulation:")
print("  Chicken: Found eoschso with P(animal)=1.0 in f90r1")
print()

if herb_ri:
    best = herb_ri[0]
    print(f"Best herb candidate: {best['token']} with P(herb)={best['herb_prob']:.2f}")

    # Find which records
    containing = [r for r in converging_records if best['token'] in r['ri']]
    if containing:
        print(f"Found in {len(containing)} converging records")
        for r in containing[:3]:
            print(f"  {r['folio']}:{r['line']}: {r['n_pp']} PP, {r['n_ri']} RI")
else:
    print("No herb candidates found in converging RI")
    print()
    print("Checking if ANY non-infrastructure RI exists in converging records...")
    all_ri_count = sum(len(r['ri']) for r in converging_records)
    print(f"Total RI tokens across converging records: {all_ri_count}")
