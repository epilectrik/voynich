#!/usr/bin/env python3
"""
Identify frog (frosch) token.

Frog signature: UNKNOWN -> LINK
- Fire degree 4 (REGIME_4)
- Only 2 steps (simpler than chicken or thyme)
- No strong qo (unlike thyme's RECOVERY)
- No e_ESCAPE pattern (unlike chicken)
- LINK terminal

Discrimination from other REGIME_4 materials:
- vs chicken: No escape-heavy profile
- vs thyme: No qo-heavy profile
- vs other herbs: Should be animal class, not herb
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology
PREFIXES = ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
                'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
                'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
                'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']
    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or '_EMPTY_'
            return remainder or '_EMPTY_'
    return None

df_a['prefix'] = df_a['word'].apply(extract_prefix)
df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['prefix'] = df_b['word'].apply(extract_prefix)
df_b['middle'] = df_b['word'].apply(extract_middle)

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared = a_middles & b_middles
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_data = json.load(f)

regime4_folios = set(regime_data.get('REGIME_4', []))

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

class_lookup = {}
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    if posterior:
        class_lookup[middle] = posterior

print("=" * 70)
print("FROG (FROSCH) IDENTIFICATION")
print("=" * 70)
print()
print("Frog signature: UNKNOWN -> LINK")
print("  - REGIME_4 (fire degree 4)")
print("  - Simple 2-step sequence")
print("  - No qo-heavy profile (unlike thyme)")
print("  - No escape pattern (unlike chicken)")
print("  - Animal class")
print()

# Strategy: Find REGIME_4 records with animal RI that are NOT chicken/thyme-like
# Frog should have:
# - MODERATE qo (not high like thyme)
# - Animal class RI
# - Simpler structure

# Build REGIME_4 PP vocabulary
r4_pp = set()
for folio in regime4_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    r4_pp.update(folio_tokens['middle'].dropna().unique())
r4_pp = (r4_pp & shared) - infrastructure

print(f"REGIME_4 folios: {len(regime4_folios)}")
print(f"REGIME_4 PP vocabulary: {len(r4_pp)} tokens")
print()

# Find converging A records
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: list(x.dropna()),
    'prefix': lambda x: list(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()

converging = []
for _, row in a_records.iterrows():
    middles = set(row['middle']) - infrastructure
    pp_overlap = middles & r4_pp
    ri = middles - b_middles

    prefixes = row['prefix']
    total = len(prefixes) if prefixes else 1
    qo_count = prefixes.count('qo') if prefixes else 0
    da_count = prefixes.count('da') if prefixes else 0
    qo_ratio = qo_count / total

    if len(pp_overlap) >= 2:
        converging.append({
            'folio': row['folio'],
            'line': row['line_number'],
            'middles': middles,
            'pp_overlap': pp_overlap,
            'ri': ri,
            'n_pp': len(pp_overlap),
            'n_ri': len(ri),
            'qo_count': qo_count,
            'da_count': da_count,
            'qo_ratio': qo_ratio,
            'total': total
        })

print(f"Records with 2+ REGIME_4 PP: {len(converging)}")
print()

# Find animal RI tokens in converging records
print("-" * 70)
print("Step 1: Find animal RI in REGIME_4 converging records")
print("-" * 70)
print()

all_ri = set()
for r in converging:
    all_ri.update(r['ri'])

animal_ri = []
for ri in all_ri:
    if ri in class_lookup:
        priors = class_lookup[ri]
        animal_prob = priors.get('animal', 0)
        if animal_prob > 0.3:
            containing = [r for r in converging if ri in r['ri']]
            animal_ri.append({
                'token': ri,
                'animal_prob': animal_prob,
                'n_records': len(containing),
                'records': containing
            })

animal_ri.sort(key=lambda x: -x['animal_prob'])

print(f"Animal RI tokens (P(animal) > 0.3): {len(animal_ri)}")
print()

for item in animal_ri:
    print(f"{item['token']}: P(animal)={item['animal_prob']:.2f}, {item['n_records']} records")
    for r in item['records'][:3]:
        loc = r['folio'] + ':' + str(r['line'])
        print(f"  {loc}: qo={r['qo_count']}, da={r['da_count']}, total={r['total']}, qo_ratio={r['qo_ratio']:.2f}")
    print()

# Now discriminate frog from chicken
print("-" * 70)
print("Step 2: Discriminate frog from chicken")
print("-" * 70)
print()

# We already identified chicken as eoschso in f90r1
# Frog should be different - simpler pattern, different record

print("Known chicken: eoschso in f90r1")
print()

# Filter out eoschso and look for frog characteristics
# Frog: UNKNOWN -> LINK (simpler, 2 steps)
# Should have moderate, not extreme, PREFIX profile

print("Frog candidates (animal RI, not eoschso, moderate qo profile):")
print()

for item in animal_ri:
    if item['token'] == 'eoschso':
        print(f"  SKIP {item['token']} - already identified as chicken")
        continue

    # Look at the records this token appears in
    for r in item['records']:
        # Frog signature: not qo-heavy (unlike thyme), simpler
        # Moderate qo ratio (0.05-0.20) vs thyme's high qo
        if 0.05 <= r['qo_ratio'] <= 0.25:
            loc = r['folio'] + ':' + str(r['line'])
            print(f"  CANDIDATE: {item['token']} (P(animal)={item['animal_prob']:.2f})")
            print(f"    Location: {loc}")
            print(f"    PREFIX: qo={r['qo_count']}, da={r['da_count']}, total={r['total']}")
            print(f"    qo_ratio: {r['qo_ratio']:.2f} (moderate = frog-like)")
            print(f"    RI tokens: {sorted(r['ri'])}")
            print()

# Summary
print("=" * 70)
print("SUMMARY: REGIME_4 Animal Identifications")
print("=" * 70)
print()

# Group by token
print("All animal RI tokens found:")
for item in animal_ri:
    locs = [r['folio'] + ':' + str(r['line']) for r in item['records']]
    qo_ratios = [r['qo_ratio'] for r in item['records']]
    avg_qo = sum(qo_ratios) / len(qo_ratios) if qo_ratios else 0
    print(f"  {item['token']}: P={item['animal_prob']:.2f}, avg_qo_ratio={avg_qo:.2f}, locations={locs}")
