#!/usr/bin/env python3
"""
Triangulate scharlach/charlach/milch (blood products).

KNOWN steps: e_ESCAPE, FLOW
- High qo (escape)
- High da (flow)
- NO AUX (unlike chicken)

This is different from chicken which has e_ESCAPE + AUX but NO FLOW.
"""

import json
import pandas as pd
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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
print("SCHARLACH/CHARLACH/MILCH TRIANGULATION (Blood Products)")
print("=" * 70)
print()
print("KNOWN steps: e_ESCAPE, FLOW")
print("Expected: HIGH qo (escape) + HIGH da (flow) + LOW aux")
print("Compare to chicken: HIGH qo + HIGH aux + LOW da")
print()

# Find REGIME_4 folios with HIGH qo AND HIGH da (scharlach signature)
print("-" * 70)
print("Step 1: Find REGIME_4 folios with escape+flow signature")
print("-" * 70)
print()

folio_profiles = []
for folio in regime4_folios:
    folio_b = df_b[df_b['folio'] == folio]
    prefixes = folio_b['prefix'].value_counts()
    total = len(folio_b)

    if total > 0:
        qo = prefixes.get('qo', 0) / total
        da = prefixes.get('da', 0) / total
        aux = (prefixes.get('ok', 0) + prefixes.get('ot', 0)) / total

        folio_profiles.append({
            'folio': folio,
            'qo': qo,
            'da': da,
            'aux': aux,
            'qo_plus_da': qo + da,
            'total': total
        })

# Scharlach signature: high qo + high da
folio_profiles.sort(key=lambda x: -x['qo_plus_da'])

print("REGIME_4 folios ranked by (qo + da) - scharlach signature:")
print(f"{'Folio':<12} {'qo%':<8} {'da%':<8} {'aux%':<8} {'qo+da%':<8}")
print("-" * 44)
for fp in folio_profiles[:10]:
    print(f"{fp['folio']:<12} {fp['qo']*100:<8.1f} {fp['da']*100:<8.1f} {fp['aux']*100:<8.1f} {fp['qo_plus_da']*100:<8.1f}")

# Select folios with scharlach-like profile (high qo AND high da)
scharlach_folios = [fp['folio'] for fp in folio_profiles
                   if fp['qo'] > 0.08 and fp['da'] > 0.05]

print()
print(f"Scharlach-signature folios (qo>8%, da>5%): {len(scharlach_folios)}")
print(f"  {scharlach_folios}")
print()

# Build PP vocabulary from scharlach folios
scharlach_pp = set()
for folio in scharlach_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    scharlach_pp.update(folio_tokens['middle'].dropna().unique())
scharlach_pp = (scharlach_pp & shared) - infrastructure

print(f"Scharlach-signature PP vocabulary: {len(scharlach_pp)} tokens")
print()

# Find converging A records
print("-" * 70)
print("Step 2: Find A records converging on scharlach PP")
print("-" * 70)
print()

a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: list(x.dropna()),
    'prefix': lambda x: list(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()

converging = []
for _, row in a_records.iterrows():
    middles = set(row['middle']) - infrastructure
    pp_overlap = middles & scharlach_pp
    ri = middles - b_middles

    prefixes = row['prefix']
    total = len(prefixes) if prefixes else 1
    qo_count = prefixes.count('qo') if prefixes else 0
    da_count = prefixes.count('da') if prefixes else 0
    aux_count = (prefixes.count('ok') + prefixes.count('ot')) if prefixes else 0

    if len(pp_overlap) >= 2:
        converging.append({
            'folio': row['folio'],
            'line': row['line_number'],
            'middles': middles,
            'pp_overlap': pp_overlap,
            'ri': ri,
            'n_pp': len(pp_overlap),
            'n_ri': len(ri),
            'qo': qo_count,
            'da': da_count,
            'aux': aux_count,
            'total': total
        })

# Sort by scharlach-like profile (high qo+da, low aux)
converging.sort(key=lambda x: (-(x['qo'] + x['da']), x['aux']))

print(f"Records with 2+ scharlach-signature PP: {len(converging)}")
print()

print("Top converging records (sorted by qo+da, low aux):")
for r in converging[:15]:
    print(f"{r['folio']}:{r['line']}: {r['n_pp']} PP, {r['n_ri']} RI (qo={r['qo']}, da={r['da']}, aux={r['aux']})")
    if r['ri']:
        print(f"  RI: {sorted(r['ri'])}")
print()

# Find animal RI with scharlach-like profile
print("-" * 70)
print("Step 3: Find animal RI in scharlach-converging records")
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
            # Check which records contain this RI
            containing = [r for r in converging if ri in r['ri']]
            # Scharlach-like: high qo+da, low aux
            scharlach_like = [r for r in containing
                            if (r['qo'] + r['da']) > r['aux'] and r['da'] > 0]

            animal_ri.append({
                'token': ri,
                'animal_prob': animal_prob,
                'n_records': len(containing),
                'n_scharlach_like': len(scharlach_like),
                'records': containing[:3]
            })

animal_ri.sort(key=lambda x: (-x['n_scharlach_like'], -x['animal_prob']))

print(f"Animal RI candidates: {len(animal_ri)}")
print()

# Exclude already identified tokens
identified = {'eoschso', 'ofy'}

for item in animal_ri[:15]:
    status = " <-- ALREADY IDENTIFIED" if item['token'] in identified else ""
    print(f"{item['token']}: P(animal)={item['animal_prob']:.2f}, {item['n_records']} records, {item['n_scharlach_like']} scharlach-like{status}")
    for r in item['records'][:2]:
        loc = r['folio'] + ':' + str(r['line'])
        print(f"  {loc}: qo={r['qo']}, da={r['da']}, aux={r['aux']}")
    print()

# Summary
print("=" * 70)
print("SCHARLACH CANDIDATES (not already identified)")
print("=" * 70)
print()

new_candidates = [item for item in animal_ri if item['token'] not in identified]
if new_candidates:
    best = new_candidates[0]
    print(f"Best scharlach candidate: {best['token']}")
    print(f"  P(animal) = {best['animal_prob']:.2f}")
    print(f"  Found in {best['n_records']} converging records")
    print(f"  {best['n_scharlach_like']} have scharlach-like profile (qo+da > aux, da > 0)")
else:
    print("No new animal candidates found")
