#!/usr/bin/env python3
"""
Identify thyme token using instruction sequence discrimination.

Thyme (quuendel) unique signature:
- REGIME_4 (precision override)
- Instruction: RECOVERY -> UNKNOWN -> LINK
- This means: HIGH qo (recovery/escape), LOW da (no FLOW), LINK terminal

Other REGIME_4 herbs:
- beste/besser/ish/kyrsen: RECOVERY -> LINK -> FLOW (has da!)
- clissen/wurg/nessel: UNKNOWN -> LINK -> RECOVERY (qo at end, not start)

Discrimination: Find records with HIGH qo, LOW da within REGIME_4 context.
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

print("=" * 70)
print("THYME IDENTIFICATION")
print("=" * 70)
print()
print("Thyme signature: RECOVERY -> UNKNOWN -> LINK")
print("  = HIGH qo (recovery), LOW da (no flow), LINK terminal")
print()
print(f"REGIME_4 folios: {len(regime4_folios)}")
print()

# Analyze PREFIX distribution in REGIME_4 B folios
print("-" * 70)
print("Step 1: PREFIX distribution in REGIME_4 B folios")
print("-" * 70)
print()

r4_b = df_b[df_b['folio'].isin(regime4_folios)]
r4_prefix_counts = r4_b['prefix'].value_counts()

print("PREFIX distribution in REGIME_4:")
for prefix in ['qo', 'da', 'ok', 'ot', 'ol', 'ch', 'sh']:
    count = r4_prefix_counts.get(prefix, 0)
    total = len(r4_b)
    pct = count / total * 100 if total > 0 else 0
    print(f"  {prefix}: {count} ({pct:.1f}%)")

print()

# Calculate qo/da ratio per folio
print("-" * 70)
print("Step 2: qo/da ratio by folio (thyme = HIGH qo, LOW da)")
print("-" * 70)
print()

folio_ratios = []
for folio in regime4_folios:
    folio_b = df_b[df_b['folio'] == folio]
    prefixes = folio_b['prefix'].value_counts()
    qo_count = prefixes.get('qo', 0)
    da_count = prefixes.get('da', 0)
    total = len(folio_b)

    if total > 0:
        qo_ratio = qo_count / total
        da_ratio = da_count / total
        folio_ratios.append({
            'folio': folio,
            'qo_count': qo_count,
            'da_count': da_count,
            'qo_ratio': qo_ratio,
            'da_ratio': da_ratio,
            'qo_minus_da': qo_ratio - da_ratio,  # Thyme should have high qo - da
            'total': total
        })

# Sort by qo/da differential (thyme = high qo, low da)
folio_ratios.sort(key=lambda x: -x['qo_minus_da'])

print("Folios ranked by (qo - da) ratio (thyme signature = positive):")
print(f"{'Folio':<12} {'qo%':<8} {'da%':<8} {'qo-da':<8} {'Total':<8}")
print("-" * 44)
for fr in folio_ratios[:10]:
    print(f"{fr['folio']:<12} {fr['qo_ratio']*100:<8.1f} {fr['da_ratio']*100:<8.1f} {fr['qo_minus_da']*100:<8.1f} {fr['total']:<8}")

print()

# Identify candidate folios (high qo, low da)
thyme_candidate_folios = [fr['folio'] for fr in folio_ratios
                          if fr['qo_ratio'] > 0.15 and fr['da_ratio'] < 0.15]

print(f"Thyme candidate folios (qo > 15%, da < 15%): {len(thyme_candidate_folios)}")
if thyme_candidate_folios:
    print(f"  {thyme_candidate_folios}")
print()

# Build PP vocabulary from thyme candidate folios
print("-" * 70)
print("Step 3: Find A records converging on thyme-signature folios")
print("-" * 70)
print()

if not thyme_candidate_folios:
    # Relax criteria
    thyme_candidate_folios = [fr['folio'] for fr in folio_ratios[:5]]
    print(f"(Relaxed: using top 5 folios by qo-da ratio)")
    print(f"  {thyme_candidate_folios}")
    print()

# Build PP from thyme candidate folios
thyme_pp = set()
for folio in thyme_candidate_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    thyme_pp.update(folio_tokens['middle'].dropna().unique())

thyme_pp = (thyme_pp & shared) - infrastructure
print(f"Thyme-signature PP vocabulary: {len(thyme_pp)} tokens")
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
    pp_overlap = middles & thyme_pp
    ri = middles - b_middles

    # Also check PREFIX profile in the A record
    prefixes = row['prefix']
    qo_in_record = prefixes.count('qo') if prefixes else 0
    da_in_record = prefixes.count('da') if prefixes else 0

    if len(pp_overlap) >= 2:
        converging.append({
            'folio': row['folio'],
            'line': row['line_number'],
            'middles': middles,
            'pp_overlap': pp_overlap,
            'ri': ri,
            'n_pp': len(pp_overlap),
            'n_ri': len(ri),
            'qo_count': qo_in_record,
            'da_count': da_in_record
        })

# Sort by PP count, then by qo-da differential
converging.sort(key=lambda x: (-x['n_pp'], x['da_count'] - x['qo_count']))

print(f"Records with 2+ thyme-signature PP: {len(converging)}")
print()

print("-" * 70)
print("Step 4: Top converging records (thyme candidates)")
print("-" * 70)
print()

for r in converging[:15]:
    print(f"{r['folio']}:{r['line']}: {r['n_pp']} PP, {r['n_ri']} RI (qo={r['qo_count']}, da={r['da_count']})")
    if r['ri']:
        print(f"  RI tokens: {sorted(r['ri'])}")
    print()

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

# Find herb RI in converging records
print("-" * 70)
print("Step 5: Herb RI tokens in thyme-converging records")
print("-" * 70)
print()

all_ri = set()
for r in converging:
    all_ri.update(r['ri'])

herb_ri = []
for ri in all_ri:
    if ri in class_lookup:
        priors = class_lookup[ri]
        herb_prob = priors.get('herb', 0) + priors.get('hot_dry_herb', 0) + priors.get('moderate_herb', 0)
        if herb_prob > 0.3:
            # Find which records contain this RI
            containing = [r for r in converging if ri in r['ri']]
            # Check if those records have thyme-like PREFIX profile (more qo than da)
            thyme_like = [r for r in containing if r['qo_count'] >= r['da_count']]

            herb_ri.append({
                'token': ri,
                'herb_prob': herb_prob,
                'n_records': len(containing),
                'n_thyme_like': len(thyme_like),
                'records': containing[:3]
            })

herb_ri.sort(key=lambda x: (-x['n_thyme_like'], -x['herb_prob']))

print(f"Herb RI candidates: {len(herb_ri)}")
print()

for item in herb_ri[:10]:
    print(f"{item['token']}: P(herb)={item['herb_prob']:.2f}, {item['n_records']} records, {item['n_thyme_like']} thyme-like")
    for r in item['records'][:2]:
        loc = r['folio'] + ':' + str(r['line'])
        print(f"  {loc}: qo={r['qo_count']}, da={r['da_count']}")
    print()

print("=" * 70)
print("THYME TOKEN CANDIDATES")
print("=" * 70)
print()

if herb_ri:
    best = herb_ri[0]
    print(f"Best thyme candidate: {best['token']}")
    print(f"  P(herb) = {best['herb_prob']:.2f}")
    print(f"  Found in {best['n_records']} converging records")
    print(f"  {best['n_thyme_like']} have thyme-like PREFIX profile (qo >= da)")
else:
    print("No strong thyme candidates found")
