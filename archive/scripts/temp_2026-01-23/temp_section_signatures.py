#!/usr/bin/env python3
"""
What makes each section different?
Characterize sections by their PP composition, PREFIX usage, and boundary RI.
"""

import json
import sys
import pandas as pd
import numpy as np
from collections import Counter
from pathlib import Path
from scipy.spatial.distance import cosine

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
    if not token.strip():
        return None, None, None
    prefix = None
    suffix = None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            prefix = p
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break
    middle = remainder if remainder else None
    return prefix, middle, suffix

# Load PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load A tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

# Extract morphology
morph = df_a['word'].apply(extract_morphology)
df_a['prefix'] = morph.apply(lambda x: x[0])
df_a['middle'] = morph.apply(lambda x: x[1])
df_a['suffix'] = morph.apply(lambda x: x[2])

# Classify RI
ri_counts = df_a[df_a['middle'].notna() & ~df_a['middle'].isin(pp_middles)]['middle'].value_counts()
singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
boundary_ri = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)

# Sort folios
def folio_sort_key(f):
    import re
    match = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)

# Get folio-first tokens and build sections
df_a_sorted = df_a.sort_values(['folio', 'line_number', 'placement'])
folio_first = df_a_sorted.groupby('folio').first().reset_index()
folio_first['sort_key'] = folio_first['folio'].apply(folio_sort_key)
folio_first = folio_first.sort_values('sort_key')
folio_first['is_singleton_start'] = folio_first['middle'].isin(singleton_ri)

# Build sections
sections = []
current_section = None
folio_order = folio_first['folio'].tolist()

for folio in folio_order:
    row = folio_first[folio_first['folio'] == folio].iloc[0]
    is_start = row['is_singleton_start']
    if is_start:
        if current_section:
            sections.append(current_section)
        current_section = {
            'marker': row['word'],
            'marker_middle': row['middle'],
            'folios': [folio]
        }
    elif current_section:
        current_section['folios'].append(folio)

if current_section:
    sections.append(current_section)

# Characterize each section
print("="*70)
print("SECTION CHARACTERIZATION")
print("="*70)

section_profiles = []

for section in sections:
    # Get all tokens in this section
    section_tokens = df_a[df_a['folio'].isin(section['folios'])]

    # PP profile
    pp_tokens = section_tokens[section_tokens['middle'].isin(pp_middles)]
    pp_counts = Counter(pp_tokens['middle'])
    top_pp = pp_counts.most_common(5)

    # PREFIX profile
    prefix_counts = Counter(section_tokens['prefix'].dropna())
    top_prefix = prefix_counts.most_common(5)

    # SUFFIX profile
    suffix_counts = Counter(section_tokens['suffix'].dropna())
    top_suffix = suffix_counts.most_common(3)

    # Boundary RI used
    boundary_tokens = section_tokens[section_tokens['middle'].isin(boundary_ri)]
    boundary_counts = Counter(boundary_tokens['middle'])
    top_boundary = boundary_counts.most_common(5)

    # Metrics
    total_tokens = len(section_tokens)
    unique_pp = len(set(pp_tokens['middle']))
    pp_density = len(pp_tokens) / total_tokens if total_tokens > 0 else 0

    section_profiles.append({
        'marker': section['marker'],
        'folios': len(section['folios']),
        'tokens': total_tokens,
        'pp_density': pp_density,
        'unique_pp': unique_pp,
        'top_pp': top_pp,
        'top_prefix': top_prefix,
        'top_suffix': top_suffix,
        'top_boundary': top_boundary,
        'pp_vector': dict(pp_counts),
        'prefix_vector': dict(prefix_counts)
    })

# Show section profiles
print(f"\nTotal sections: {len(section_profiles)}")

# Filter to sections with enough data
substantial = [s for s in section_profiles if s['tokens'] >= 30]
print(f"Sections with 30+ tokens: {len(substantial)}")

print(f"\n" + "="*70)
print("SECTION SIGNATURES (30+ tokens)")
print("="*70)

for s in substantial:
    print(f"\n--- '{s['marker']}' ({s['folios']} folios, {s['tokens']} tokens) ---")

    pp_str = ', '.join(f"{m}:{c}" for m, c in s['top_pp'][:5])
    prefix_str = ', '.join(f"{p}:{c}" for p, c in s['top_prefix'][:5])
    boundary_str = ', '.join(f"{m}:{c}" for m, c in s['top_boundary'][:4]) if s['top_boundary'] else "(none)"

    print(f"  PP density: {s['pp_density']:.1%}, unique PP: {s['unique_pp']}")
    print(f"  Top PP: {pp_str}")
    print(f"  Top PREFIX: {prefix_str}")
    print(f"  Top BOUNDARY: {boundary_str}")

# Find sections with distinctive characteristics
print(f"\n" + "="*70)
print("DISTINCTIVE SECTIONS")
print("="*70)

# Highest/lowest PP density
by_density = sorted(substantial, key=lambda x: x['pp_density'])
print(f"\nLOWEST PP density:")
for s in by_density[:3]:
    print(f"  '{s['marker']}': {s['pp_density']:.1%}")

print(f"\nHIGHEST PP density:")
for s in by_density[-3:]:
    print(f"  '{s['marker']}': {s['pp_density']:.1%}")

# Sections dominated by specific PP
print(f"\n" + "="*70)
print("PP SPECIALIZATION")
print("="*70)

# For each major PP MIDDLE, which sections use it most?
all_pp = Counter()
for s in substantial:
    all_pp.update(s['pp_vector'])

top_global_pp = [pp for pp, _ in all_pp.most_common(10)]

for pp in top_global_pp[:6]:
    # Find sections where this PP is dominant
    pp_users = [(s['marker'], s['pp_vector'].get(pp, 0), s['tokens'])
                for s in substantial]
    pp_users = [(m, c, t, c/t if t > 0 else 0) for m, c, t in pp_users]
    pp_users.sort(key=lambda x: -x[3])  # Sort by rate

    print(f"\nPP '{pp}' - highest usage sections:")
    for marker, count, tokens, rate in pp_users[:3]:
        print(f"  '{marker}': {count}/{tokens} ({rate:.1%})")

# PREFIX specialization
print(f"\n" + "="*70)
print("PREFIX SPECIALIZATION")
print("="*70)

for prefix in ['qo', 'da', 'ch', 'sh', 'ok']:
    prefix_users = [(s['marker'], s['prefix_vector'].get(prefix, 0), s['tokens'])
                    for s in substantial]
    prefix_users = [(m, c, t, c/t if t > 0 else 0) for m, c, t in prefix_users]
    prefix_users.sort(key=lambda x: -x[3])

    print(f"\nPREFIX '{prefix}' - highest usage sections:")
    for marker, count, tokens, rate in prefix_users[:3]:
        print(f"  '{marker}': {count}/{tokens} ({rate:.1%})")

# Section similarity matrix
print(f"\n" + "="*70)
print("SECTION SIMILARITY (PP composition)")
print("="*70)

# Build PP vectors for substantial sections
all_pp_types = list(all_pp.keys())
vectors = {}
for s in substantial:
    vec = [s['pp_vector'].get(pp, 0) for pp in all_pp_types]
    total = sum(vec)
    if total > 0:
        vec = [v/total for v in vec]  # Normalize
    vectors[s['marker']] = vec

# Find most similar and most different pairs
similarities = []
markers = list(vectors.keys())
for i in range(len(markers)):
    for j in range(i+1, len(markers)):
        v1, v2 = vectors[markers[i]], vectors[markers[j]]
        if sum(v1) > 0 and sum(v2) > 0:
            sim = 1 - cosine(v1, v2)
            similarities.append((markers[i], markers[j], sim))

similarities.sort(key=lambda x: -x[2])

print(f"\nMost SIMILAR sections (by PP composition):")
for m1, m2, sim in similarities[:5]:
    print(f"  '{m1}' ~ '{m2}': {sim:.3f}")

print(f"\nMost DIFFERENT sections:")
for m1, m2, sim in similarities[-5:]:
    print(f"  '{m1}' ≠ '{m2}': {sim:.3f}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check if sections cluster or are all unique
mean_sim = np.mean([s[2] for s in similarities])
std_sim = np.std([s[2] for s in similarities])

print(f"\nPP composition similarity across sections:")
print(f"  Mean: {mean_sim:.3f}")
print(f"  Std: {std_sim:.3f}")
print(f"  Range: {similarities[-1][2]:.3f} to {similarities[0][2]:.3f}")

if std_sim > 0.15:
    print(f"""
SECTIONS HAVE DISTINCTIVE PP SIGNATURES.

High variance in section similarity suggests each section
has a characteristic PP composition - not just random variation.

This supports the idea that singleton RI marks topically
distinct content (different materials, processes, or subjects).
""")
else:
    print(f"""
SECTIONS HAVE SIMILAR PP PROFILES.

Low variance suggests sections use similar PP vocabulary.
Sections may differ in other ways (specific items, not PP composition).
""")
