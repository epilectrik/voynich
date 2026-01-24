#!/usr/bin/env python3
"""
Rose Water Triangulation v2

Using cold_moist_flower class (rose's actual classification)
"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("ROSE WATER TRIANGULATION v2 (cold_moist_flower class)")
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

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

# Vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

# Load regime and priors
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                 for item in priors_data['results']}

# Known flower tokens (P(cold_moist_flower) > 0)
flower_tokens = {item['middle'] for item in priors_data['results']
                 if item.get('material_class_posterior', {}).get('cold_moist_flower', 0) > 0}

print(f"Known cold_moist_flower tokens: {len(flower_tokens)}")
print(f"Top 10: {sorted([(t, priors_lookup[t].get('cold_moist_flower',0)) for t in list(flower_tokens)[:20]], key=lambda x:-x[1])[:10]}")
print()

# =============================================================================
# Use relaxed constraints since 4D was empty
# =============================================================================
print("-" * 70)
print("Step 1: REGIME-based selection (relaxed)")
print("-" * 70)
print()

# Just use REGIME_1/2 without strict PREFIX filtering
regime1_folios = set(regime_data.get('REGIME_1', []))
regime2_folios = set(regime_data.get('REGIME_2', []))
rose_regime_folios = regime1_folios | regime2_folios

print(f"REGIME_1/2 folios: {len(rose_regime_folios)}")

# Extract PP from these folios
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
rose_middles = set()
for folio in rose_regime_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    rose_middles.update(folio_tokens['middle'].dropna().unique())

rose_pp = (rose_middles & shared_middles) - infrastructure
print(f"Rose REGIME PP vocabulary: {len(rose_pp)} tokens")
print()

# =============================================================================
# Find A records with PP convergence
# =============================================================================
print("-" * 70)
print("Step 2: A RECORD convergence")
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

# Get records with 3+ PP
high_conv = a_records[a_records['rose_pp_count'] >= 3].copy()
high_conv = high_conv.sort_values('rose_pp_count', ascending=False)

print(f"A records with 3+ rose PP: {len(high_conv)}")
print()

# =============================================================================
# Check for flower RI tokens
# =============================================================================
print("-" * 70)
print("Step 3: Check for cold_moist_flower RI")
print("-" * 70)
print()

# Check ALL RI in converging records
flower_ri_found = []
for _, row in high_conv.iterrows():
    ri = row['middles'] - b_middles
    for token in ri:
        if token in flower_tokens:
            prob = priors_lookup[token].get('cold_moist_flower', 0)
            flower_ri_found.append((token, prob, row['record_id']))

print(f"Flower RI tokens found in converging records: {len(flower_ri_found)}")

if flower_ri_found:
    # Deduplicate
    unique_flowers = {}
    for token, prob, record in flower_ri_found:
        if token not in unique_flowers or prob > unique_flowers[token][0]:
            unique_flowers[token] = (prob, record)

    print()
    print("Flower candidates:")
    for token, (prob, record) in sorted(unique_flowers.items(), key=lambda x: -x[1][0]):
        print(f"  {token}: P(cold_moist_flower) = {prob:.2f} (in {record})")

# =============================================================================
# Also check: which flower tokens are RI (not in B)?
# =============================================================================
print()
print("-" * 70)
print("Step 4: Which flower tokens are RI?")
print("-" * 70)
print()

flower_ri = flower_tokens - b_middles
flower_pp = flower_tokens & b_middles

print(f"Flower tokens that are RI (not in B): {len(flower_ri)}")
print(f"Flower tokens that are PP (in both): {len(flower_pp)}")
print()

if flower_ri:
    print("Flower RI tokens:")
    for t in sorted(flower_ri, key=lambda x: -priors_lookup.get(x,{}).get('cold_moist_flower',0)):
        prob = priors_lookup.get(t, {}).get('cold_moist_flower', 0)
        # Check which A folios contain this token
        a_with_token = df_a[df_a['middle'] == t]['folio'].unique()
        print(f"  {t}: P={prob:.2f}, in A folios: {list(a_with_token)[:5]}")

# =============================================================================
# Final: Records with flower RI that converge to rose profile
# =============================================================================
print()
print("-" * 70)
print("Step 5: FINAL - Records with flower RI + rose PP convergence")
print("-" * 70)
print()

# For each A record, check if it has flower RI AND rose PP convergence
final_candidates = []
for _, row in a_records.iterrows():
    ri = row['middles'] - b_middles
    flower_in_ri = ri & flower_ri
    pp_count = row['rose_pp_count']

    if flower_in_ri and pp_count >= 2:
        final_candidates.append({
            'record_id': row['record_id'],
            'flower_ri': flower_in_ri,
            'pp_count': pp_count,
            'all_ri': ri
        })

print(f"Records with flower RI AND 2+ rose PP: {len(final_candidates)}")
print()

if final_candidates:
    # Sort by PP count
    final_candidates.sort(key=lambda x: -x['pp_count'])

    print("Rose candidates:")
    for c in final_candidates[:10]:
        flower_probs = {t: priors_lookup.get(t,{}).get('cold_moist_flower',0) for t in c['flower_ri']}
        print(f"  {c['record_id']}: {c['pp_count']} PP")
        print(f"    Flower RI: {c['flower_ri']}")
        print(f"    Priors: {flower_probs}")
        print()

# =============================================================================
# VERDICT
# =============================================================================
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

if final_candidates:
    best = final_candidates[0]
    best_token = max(best['flower_ri'], key=lambda t: priors_lookup.get(t,{}).get('cold_moist_flower',0))
    best_prob = priors_lookup.get(best_token,{}).get('cold_moist_flower',0)
    print(f"Best rose candidate: {best_token}")
    print(f"  P(cold_moist_flower) = {best_prob:.2f}")
    print(f"  Found in record: {best['record_id']}")
    print(f"  PP convergence: {best['pp_count']}")
else:
    print("No flower RI tokens found in rose-converging records.")
    print()
    print("This could mean:")
    print("  1. Rose-class tokens don't follow the same PP convergence pattern")
    print("  2. Rose materials are encoded differently than animals")
    print("  3. The flower priors need refinement")
