#!/usr/bin/env python3
"""
Triangulate beste/besser/ish/kyrsen (precision herbs with FLOW).

KNOWN steps: RECOVERY, LINK, FLOW
- High qo (recovery)
- High da (flow)
- Different from thyme which has RECOVERY, LINK but NO FLOW

This distinguishes beste from thyme: beste has FLOW (da), thyme doesn't.
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
print("BESTE/BESSER/ISH/KYRSEN TRIANGULATION (Precision Herbs with FLOW)")
print("=" * 70)
print()
print("KNOWN steps: RECOVERY, LINK, FLOW")
print("Expected: HIGH qo (recovery) + HIGH da (flow)")
print("Compare to thyme: HIGH qo + LOW da (no FLOW)")
print()

# Find REGIME_4 folios with HIGH qo AND HIGH da (beste signature)
# Different from thyme which has high qo but LOW da
print("-" * 70)
print("Step 1: Find REGIME_4 folios with recovery+flow signature")
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

        folio_profiles.append({
            'folio': folio,
            'qo': qo,
            'da': da,
            'qo_plus_da': qo + da,
            'total': total
        })

# Beste signature: high qo + high da (unlike thyme which is high qo, low da)
folio_profiles.sort(key=lambda x: -x['qo_plus_da'])

print("REGIME_4 folios ranked by (qo + da) - beste signature:")
print(f"{'Folio':<12} {'qo%':<8} {'da%':<8} {'qo+da%':<8}")
print("-" * 36)
for fp in folio_profiles[:10]:
    print(f"{fp['folio']:<12} {fp['qo']*100:<8.1f} {fp['da']*100:<8.1f} {fp['qo_plus_da']*100:<8.1f}")

# Beste signature: needs BOTH qo AND da (not just one or the other)
beste_folios = [fp['folio'] for fp in folio_profiles
               if fp['qo'] > 0.08 and fp['da'] > 0.05]

print()
print(f"Beste-signature folios (qo>8%, da>5%): {len(beste_folios)}")
print(f"  {beste_folios}")
print()

# Also identify thyme-like folios for comparison (high qo, LOW da)
thyme_folios = [fp['folio'] for fp in folio_profiles
               if fp['qo'] > 0.12 and fp['da'] < 0.06]
print(f"Thyme-signature folios (qo>12%, da<6%): {len(thyme_folios)}")
print(f"  {thyme_folios}")
print()

# Build PP vocabulary from beste folios
beste_pp = set()
for folio in beste_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    beste_pp.update(folio_tokens['middle'].dropna().unique())
beste_pp = (beste_pp & shared) - infrastructure

print(f"Beste-signature PP vocabulary: {len(beste_pp)} tokens")
print()

# Find converging A records
print("-" * 70)
print("Step 2: Find A records converging on beste PP with HIGH da")
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
    pp_overlap = middles & beste_pp
    ri = middles - b_middles

    prefixes = row['prefix']
    total = len(prefixes) if prefixes else 1
    qo_count = prefixes.count('qo') if prefixes else 0
    da_count = prefixes.count('da') if prefixes else 0

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
            'total': total
        })

# Sort by beste-like profile (high qo AND high da)
# This is the key difference from thyme (which has high qo, low da)
converging.sort(key=lambda x: (-(x['qo'] + x['da']), -x['da']))

print(f"Records with 2+ beste-signature PP: {len(converging)}")
print()

# Filter to records with BOTH qo AND da (beste signature)
beste_like = [r for r in converging if r['qo'] > 0 and r['da'] > 0]
print(f"Records with both qo AND da (beste-like): {len(beste_like)}")
print()

print("Top beste-like records (has both qo AND da):")
for r in beste_like[:15]:
    print(f"{r['folio']}:{r['line']}: {r['n_pp']} PP, {r['n_ri']} RI (qo={r['qo']}, da={r['da']})")
    if r['ri']:
        print(f"  RI: {sorted(r['ri'])}")
print()

# Find herb RI with beste-like profile
print("-" * 70)
print("Step 3: Find herb RI in beste-converging records")
print("-" * 70)
print()

all_ri = set()
for r in beste_like:  # Only from beste-like records
    all_ri.update(r['ri'])

herb_ri = []
for ri in all_ri:
    if ri in class_lookup:
        priors = class_lookup[ri]
        herb_prob = priors.get('herb', 0) + priors.get('hot_dry_herb', 0) + priors.get('moderate_herb', 0)
        if herb_prob > 0.3:
            # Check which records contain this RI
            containing = [r for r in beste_like if ri in r['ri']]

            herb_ri.append({
                'token': ri,
                'herb_prob': herb_prob,
                'n_records': len(containing),
                'records': containing[:3]
            })

herb_ri.sort(key=lambda x: (-x['n_records'], -x['herb_prob']))

print(f"Herb RI candidates in beste-like records: {len(herb_ri)}")
print()

# Exclude already identified tokens
identified = {'keolo'}  # thyme

for item in herb_ri[:15]:
    status = " <-- ALREADY IDENTIFIED (thyme)" if item['token'] in identified else ""
    print(f"{item['token']}: P(herb)={item['herb_prob']:.2f}, {item['n_records']} beste-like records{status}")
    for r in item['records'][:2]:
        loc = r['folio'] + ':' + str(r['line'])
        print(f"  {loc}: qo={r['qo']}, da={r['da']}")
    print()

# Summary
print("=" * 70)
print("BESTE CANDIDATES (not thyme)")
print("=" * 70)
print()

new_candidates = [item for item in herb_ri if item['token'] not in identified]
if new_candidates:
    best = new_candidates[0]
    print(f"Best beste candidate: {best['token']}")
    print(f"  P(herb) = {best['herb_prob']:.2f}")
    print(f"  Found in {best['n_records']} beste-like records (has both qo AND da)")
    print()
    print("Differentiation from thyme (keolo):")
    print("  - Thyme: qo=4, da=0 (RECOVERY, no FLOW)")
    print(f"  - Beste candidate: appears in records WITH da (has FLOW)")
else:
    print("No new herb candidates found in beste-like records")
