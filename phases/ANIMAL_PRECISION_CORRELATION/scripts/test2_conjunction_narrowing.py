#!/usr/bin/env python3
"""
TEST 2: Does multi-dimensional conjunction actually narrow candidates?

Test if combining multiple recipe dimensions provides tighter selection
than any single dimension alone.

Dimensions to test:
1. REGIME (fire degree)
2. Zone affinity (R-cluster for sound)
3. PREFIX profile (qo for escape, ok/ot for aux)
4. PP vocabulary overlap
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("TEST 2: Multi-dimensional conjunction narrowing")
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

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)
df_b['prefix'] = df_b['word'].apply(extract_prefix)

# Get vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

# All B folios
all_b_folios = set(df_b['folio'].unique())
print(f"Total B folios: {len(all_b_folios)}")
print()

# =============================================================================
# Define Dimensions
# =============================================================================

# Dimension 1: REGIME_4 (fire degree 4)
regime4_folios = set(regime_data['REGIME_4'])

# Dimension 2: High qo PREFIX (escape/recovery)
folio_qo = {}
for folio in all_b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    folio_qo[folio] = prefix_counts.get('qo', 0) / total if total > 0 else 0

avg_qo = sum(folio_qo.values()) / len(folio_qo)
high_qo_folios = {f for f, r in folio_qo.items() if r >= avg_qo}

# Dimension 3: High ok/ot PREFIX (auxiliary)
folio_aux = {}
for folio in all_b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    ok = prefix_counts.get('ok', 0) / total if total > 0 else 0
    ot = prefix_counts.get('ot', 0) / total if total > 0 else 0
    folio_aux[folio] = ok + ot

avg_aux = sum(folio_aux.values()) / len(folio_aux)
high_aux_folios = {f for f, r in folio_aux.items() if r >= avg_aux}

# Dimension 4: Low da PREFIX (low direct action - for precision procedures)
folio_da = {}
for folio in all_b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    folio_da[folio] = prefix_counts.get('da', 0) / total if total > 0 else 0

avg_da = sum(folio_da.values()) / len(folio_da)
low_da_folios = {f for f, r in folio_da.items() if r <= avg_da}

print("Dimension thresholds:")
print(f"  REGIME_4: {len(regime4_folios)} folios")
print(f"  High qo (>={avg_qo:.2%}): {len(high_qo_folios)} folios")
print(f"  High aux (>={avg_aux:.2%}): {len(high_aux_folios)} folios")
print(f"  Low da (<={avg_da:.2%}): {len(low_da_folios)} folios")
print()

# =============================================================================
# Test Single Dimensions
# =============================================================================
print("-" * 70)
print("Single dimension narrowing")
print("-" * 70)
print()

single_results = {
    'REGIME_4': len(regime4_folios),
    'High qo': len(high_qo_folios),
    'High aux': len(high_aux_folios),
    'Low da': len(low_da_folios)
}

for dim, count in single_results.items():
    pct = count / len(all_b_folios) * 100
    print(f"{dim}: {count} folios ({pct:.1f}%)")

print()

# =============================================================================
# Test Pairwise Conjunctions
# =============================================================================
print("-" * 70)
print("Pairwise conjunction narrowing")
print("-" * 70)
print()

pairs = [
    ('REGIME_4', 'High qo', regime4_folios & high_qo_folios),
    ('REGIME_4', 'High aux', regime4_folios & high_aux_folios),
    ('REGIME_4', 'Low da', regime4_folios & low_da_folios),
    ('High qo', 'High aux', high_qo_folios & high_aux_folios),
    ('High qo', 'Low da', high_qo_folios & low_da_folios),
    ('High aux', 'Low da', high_aux_folios & low_da_folios),
]

for d1, d2, result in pairs:
    n1 = single_results[d1]
    n2 = single_results[d2]
    expected = (n1 / len(all_b_folios)) * (n2 / len(all_b_folios)) * len(all_b_folios)
    actual = len(result)
    ratio = actual / expected if expected > 0 else float('inf')
    print(f"{d1} AND {d2}: {actual} folios (expected={expected:.1f}, ratio={ratio:.2f})")

print()

# =============================================================================
# Test Triple Conjunctions
# =============================================================================
print("-" * 70)
print("Triple conjunction narrowing")
print("-" * 70)
print()

triples = [
    ('REGIME_4', 'High qo', 'High aux', regime4_folios & high_qo_folios & high_aux_folios),
    ('REGIME_4', 'High qo', 'Low da', regime4_folios & high_qo_folios & low_da_folios),
    ('REGIME_4', 'High aux', 'Low da', regime4_folios & high_aux_folios & low_da_folios),
    ('High qo', 'High aux', 'Low da', high_qo_folios & high_aux_folios & low_da_folios),
]

for d1, d2, d3, result in triples:
    actual = len(result)
    pct = actual / len(all_b_folios) * 100
    print(f"{d1} AND {d2} AND {d3}: {actual} folios ({pct:.1f}%)")
    if actual > 0 and actual <= 10:
        print(f"  {sorted(result)}")

print()

# =============================================================================
# Test Quadruple Conjunction (full chicken profile)
# =============================================================================
print("-" * 70)
print("Full conjunction (all 4 dimensions)")
print("-" * 70)
print()

full_conj = regime4_folios & high_qo_folios & high_aux_folios & low_da_folios
print(f"REGIME_4 AND High qo AND High aux AND Low da: {len(full_conj)} folios")
if full_conj:
    print(f"  {sorted(full_conj)}")

# For those folios, extract PP vocabulary
if full_conj:
    print()
    print("PP vocabulary from fully-matched folios:")
    conj_middles = set()
    for folio in full_conj:
        folio_tokens = df_b[df_b['folio'] == folio]
        conj_middles.update(folio_tokens['middle'].dropna().unique())
    conj_pp = conj_middles & shared_middles
    print(f"  {len(conj_pp)} PP MIDDLEs")

print()

# =============================================================================
# Compare: Does conjunction narrow more than chance?
# =============================================================================
print("-" * 70)
print("Narrowing efficiency analysis")
print("-" * 70)
print()

# Expected under independence
p_r4 = len(regime4_folios) / len(all_b_folios)
p_qo = len(high_qo_folios) / len(all_b_folios)
p_aux = len(high_aux_folios) / len(all_b_folios)
p_da = len(low_da_folios) / len(all_b_folios)

expected_4d = p_r4 * p_qo * p_aux * p_da * len(all_b_folios)
actual_4d = len(full_conj)

print(f"4D conjunction:")
print(f"  Expected (independent): {expected_4d:.1f} folios")
print(f"  Actual: {actual_4d} folios")
if expected_4d > 0:
    print(f"  Ratio: {actual_4d/expected_4d:.2f}x")

print()

# =============================================================================
# Key test: Do conjunction folios connect to animal A entries?
# =============================================================================
print("-" * 70)
print("Animal A entry connection test")
print("-" * 70)
print()

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Animal tokens
animal_middles = {'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'eyd', 'teold', 'olar', 'hod'}
animal_entries = a_entries[a_entries['middles'].apply(lambda x: bool(x & animal_middles))]

print(f"A entries with animal tokens: {len(animal_entries)}")
print()

# For each folio set, check PP overlap with animal entries
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

def get_folio_pp(folios):
    middles = set()
    for folio in folios:
        folio_tokens = df_b[df_b['folio'] == folio]
        middles.update(folio_tokens['middle'].dropna().unique())
    return (middles & shared_middles) - infrastructure

def count_overlap(entry_middles, pp_vocab):
    return len(entry_middles & pp_vocab)

# Get animal entry MIDDLEs
animal_middles_in_entries = set()
for _, row in animal_entries.iterrows():
    animal_middles_in_entries.update(row['middles'])

# Test different B folio sets
print("PP overlap with animal A entries:")
print()

tests = [
    ('All B folios', all_b_folios),
    ('REGIME_4 only', regime4_folios),
    ('High qo only', high_qo_folios),
    ('REGIME_4 AND High qo', regime4_folios & high_qo_folios),
    ('REGIME_4 AND High qo AND High aux', regime4_folios & high_qo_folios & high_aux_folios),
    ('Full 4D conjunction', full_conj) if full_conj else ('Full 4D conjunction', set()),
]

for name, folios in tests:
    if not folios:
        print(f"  {name}: (empty set)")
        continue
    pp_vocab = get_folio_pp(folios)
    overlap = len(animal_middles_in_entries & pp_vocab)
    exclusive = pp_vocab - animal_middles_in_entries
    print(f"  {name}: {len(pp_vocab)} PP, {overlap} overlap with animal entries")
    print(f"    Not in animal entries: {len(exclusive)}")

print()

# =============================================================================
# VERDICT
# =============================================================================
print("=" * 70)
print("TEST 2 VERDICT")
print("=" * 70)
print()

# Check if conjunction provides meaningful narrowing
if actual_4d == 0:
    print("RESULT: Full 4D conjunction is EMPTY!")
    print("The dimensions are not jointly satisfiable.")
    print("This suggests dimensions are anti-correlated or too strict.")
elif actual_4d > expected_4d * 0.5:
    print(f"RESULT: Conjunction narrows minimally ({actual_4d} actual vs {expected_4d:.1f} expected)")
    print("Dimensions provide ADDITIVE narrowing (independent), not synergistic.")
    print()
    print("IMPLICATION: Multi-dimensional triangulation is just filtering,")
    print("not leveraging structural correlations in the grammar.")
else:
    print(f"RESULT: Conjunction narrows significantly ({actual_4d} actual vs {expected_4d:.1f} expected)")
    print("Dimensions are CORRELATED - conjunction is synergistic.")
    print()
    print("IMPLICATION: Multi-dimensional triangulation exploits structural relationships.")
