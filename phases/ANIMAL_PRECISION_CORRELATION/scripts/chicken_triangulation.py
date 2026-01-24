#!/usr/bin/env python3
"""
Refined Triangulation: Pinpoint CHICKEN specifically

Chicken (ennen) has unique instruction sequence:
  e_ESCAPE -> AUX -> UNKNOWN -> e_ESCAPE

Pattern features:
1. Bookended by e_ESCAPE (recovery operations)
2. AUX in the middle (auxiliary operations)
3. 4 steps total

We need to find B folios that match this operational profile.
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("REFINED TRIANGULATION: Pinpointing CHICKEN")
print("=" * 70)
print()
print("Chicken instruction pattern: [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE]")
print("Key features: e_ESCAPE bookends, AUX present, 4 operations")
print()

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
regime4_folios = set(regime_data['REGIME_4'])

print(f"REGIME_4 folios: {len(regime4_folios)}")
print()

# =============================================================================
# STEP 1: Characterize B folios by operational profile
# =============================================================================
print("-" * 70)
print("STEP 1: Characterize B folios by PREFIX profile")
print("-" * 70)
print()

# Chicken pattern uses:
# - e_ESCAPE: typically qo prefix (escape/recovery)
# - AUX: typically ok/ot prefix (auxiliary operations)
# - Bookended pattern suggests recovery-heavy procedure

# For each REGIME_4 folio, compute PREFIX distribution
folio_profiles = {}
for folio in regime4_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())

    # Compute ratios for key prefixes
    qo_ratio = prefix_counts.get('qo', 0) / total if total > 0 else 0
    ok_ratio = prefix_counts.get('ok', 0) / total if total > 0 else 0
    ot_ratio = prefix_counts.get('ot', 0) / total if total > 0 else 0
    da_ratio = prefix_counts.get('da', 0) / total if total > 0 else 0

    # e_ESCAPE bookend pattern = high qo (recovery)
    # AUX presence = ok/ot
    recovery_score = qo_ratio
    aux_score = ok_ratio + ot_ratio

    folio_profiles[folio] = {
        'qo_ratio': qo_ratio,
        'ok_ratio': ok_ratio,
        'ot_ratio': ot_ratio,
        'da_ratio': da_ratio,
        'recovery_score': recovery_score,
        'aux_score': aux_score,
        'combined': recovery_score + aux_score,
        'total_tokens': total
    }

# Sort by combined recovery+aux score (chicken pattern)
sorted_folios = sorted(folio_profiles.items(), key=lambda x: -x[1]['combined'])

print("REGIME_4 folios ranked by chicken-like pattern (qo + ok/ot):")
print()
for folio, profile in sorted_folios[:10]:
    print(f"  {folio}: qo={profile['qo_ratio']:.2%}, ok={profile['ok_ratio']:.2%}, "
          f"ot={profile['ot_ratio']:.2%}, combined={profile['combined']:.2%}")

# =============================================================================
# STEP 2: Filter to folios with chicken-like profile
# =============================================================================
print()
print("-" * 70)
print("STEP 2: Filter to chicken-like operational profile")
print("-" * 70)
print()

# Chicken criteria:
# 1. Above-average qo (recovery bookends)
# 2. Presence of ok/ot (AUX operations)

avg_qo = sum(p['qo_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_aux = sum(p['aux_score'] for p in folio_profiles.values()) / len(folio_profiles)

print(f"Average qo ratio in REGIME_4: {avg_qo:.2%}")
print(f"Average aux (ok+ot) ratio: {avg_aux:.2%}")
print()

# Filter to above-average on both dimensions
chicken_folios = set()
for folio, profile in folio_profiles.items():
    if profile['qo_ratio'] >= avg_qo and profile['aux_score'] >= avg_aux:
        chicken_folios.add(folio)

print(f"Folios matching chicken profile (above avg qo AND aux): {len(chicken_folios)}")
print(f"  {sorted(chicken_folios)}")
print()

# If too many, be more strict
if len(chicken_folios) > 10:
    # Top quartile on combined score
    threshold = sorted([p['combined'] for p in folio_profiles.values()], reverse=True)[len(folio_profiles)//4]
    chicken_folios = {f for f, p in folio_profiles.items() if p['combined'] >= threshold}
    print(f"Refined to top quartile: {len(chicken_folios)} folios")
    print(f"  {sorted(chicken_folios)}")
    print()

# =============================================================================
# STEP 3: Extract PP vocabulary from chicken-like folios
# =============================================================================
print("-" * 70)
print("STEP 3: Extract discriminative PP vocabulary")
print("-" * 70)
print()

# Get MIDDLEs from chicken-like folios
chicken_middles = set()
for folio in chicken_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    chicken_middles.update(folio_tokens['middle'].dropna().unique())

# Get MIDDLEs from OTHER REGIME_4 folios (non-chicken)
other_folios = regime4_folios - chicken_folios
other_middles = set()
for folio in other_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    other_middles.update(folio_tokens['middle'].dropna().unique())

# Chicken-enriched = in chicken folios but rare/absent in others
chicken_enriched = chicken_middles - other_middles
chicken_shared = chicken_middles & other_middles

# PP tokens from chicken-enriched
chicken_pp = chicken_enriched & shared_middles

# Also get PP that are shared but filter out infrastructure
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
discriminative_pp = (chicken_middles & shared_middles) - infrastructure

print(f"MIDDLEs in chicken-like folios: {len(chicken_middles)}")
print(f"MIDDLEs ONLY in chicken folios (not in other REGIME_4): {len(chicken_enriched)}")
print(f"Of those, PP tokens: {len(chicken_pp)}")
print(f"Discriminative PP (no infrastructure): {len(discriminative_pp)}")
print()

if chicken_pp:
    print(f"Chicken-exclusive PP tokens: {chicken_pp}")
    print()

# =============================================================================
# STEP 4: Trace to A entries
# =============================================================================
print("-" * 70)
print("STEP 4: Trace to A entries using chicken-specific vocabulary")
print("-" * 70)
print()

# Build A entries
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Use chicken-exclusive PP if we have them, otherwise discriminative
trace_vocab = chicken_pp if len(chicken_pp) >= 3 else discriminative_pp

a_entries['pp_overlap'] = a_entries['middles'].apply(
    lambda x: len(x & trace_vocab) if x else 0
)

# Use stricter threshold since we're looking for specific match
min_overlap = 2 if len(chicken_pp) >= 3 else 3
matching_entries = a_entries[a_entries['pp_overlap'] >= min_overlap].copy()
matching_entries = matching_entries.sort_values('pp_overlap', ascending=False)

print(f"Using vocabulary: {'chicken-exclusive PP' if len(chicken_pp) >= 3 else 'discriminative PP'}")
print(f"A entries with >={min_overlap} overlap: {len(matching_entries)}")
print()

if len(matching_entries) > 0:
    print("Top matching A entries:")
    for _, row in matching_entries.head(10).iterrows():
        overlap = row['middles'] & trace_vocab
        print(f"  {row['folio']}:{row['line']} - overlap={row['pp_overlap']}: {overlap}")

# =============================================================================
# STEP 5: Check RI tokens for animal class
# =============================================================================
print()
print("-" * 70)
print("STEP 5: Check RI tokens in matched A entries")
print("-" * 70)
print()

if len(matching_entries) > 0:
    # Collect MIDDLEs from matching entries
    matching_middles = set()
    for _, row in matching_entries.iterrows():
        matching_middles.update(row['middles'])

    # RI = not in B
    ri_middles = matching_middles - b_middles
    print(f"Total MIDDLEs in matching entries: {len(matching_middles)}")
    print(f"RI tokens (not in B): {len(ri_middles)}")

    # Load animal priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                     for item in priors_data['results']}

    # Check animal priors
    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_middles
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"RI tokens with P(animal) > 0: {len(ri_animal)}")
    print()

    if ri_animal:
        print("*** CHICKEN-SPECIFIC ANIMAL TOKENS ***")
        for m, p in sorted(ri_animal, key=lambda x: -x[1]):
            print(f"  {m}: P(animal) = {p:.2f}")

        high_animal = [m for m, p in ri_animal if p >= 0.5]
        print(f"\nHigh-confidence (P>=0.5): {len(high_animal)}")

        if high_animal:
            print(f"\n*** CANDIDATE CHICKEN TOKENS: {high_animal} ***")

# =============================================================================
# STEP 6: Cross-reference with known animal token locations
# =============================================================================
print()
print("-" * 70)
print("STEP 6: Cross-reference with folio-exclusive animal tokens")
print("-" * 70)
print()

# The folio-exclusive animal tokens we found earlier
folio_exclusive = {
    'chald': 'f23r',
    'hyd': 'f19r',
    'olfcho': 'f89r2',
    'eoschso': 'f90r1',
    'hdaoto': 'f100r',
    'cthso': 'f100r',
    'eyd': 'f89r2',
    'teold': 'f100r',
    'olar': 'f89r2'
}

# Check which of these appear in our matched A entries
if len(matching_entries) > 0:
    matched_folios = set(matching_entries['folio'].unique())

    print("Matched A folios:", sorted(matched_folios))
    print()

    # Check overlap with exclusive animal token folios
    for token, token_folio in folio_exclusive.items():
        if token_folio in matched_folios:
            print(f"  MATCH: '{token}' is in {token_folio} - which we traced to!")

    # Show which animal tokens are in our matched entries
    matched_animal = set()
    for _, row in matching_entries.iterrows():
        for token in folio_exclusive.keys():
            if token in row['middles']:
                matched_animal.add(token)

    if matched_animal:
        print(f"\n*** ANIMAL TOKENS IN TRACED ENTRIES: {matched_animal} ***")
        print()
        print("If chicken has unique operational profile (qo+aux bookends),")
        print("then these tokens are CHICKEN candidates!")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print(f"Chicken operational pattern: e_ESCAPE -> AUX -> e_ESCAPE")
print(f"Mapped to: high qo (recovery) + high ok/ot (auxiliary)")
print(f"REGIME_4 folios with this profile: {len(chicken_folios)}")
print(f"A entries traced: {len(matching_entries)}")
