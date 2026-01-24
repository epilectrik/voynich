#!/usr/bin/env python3
"""
Investigate why flower entries are sparse while animal entries are rich.

Compare record structure across material classes.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("RECORD STRUCTURE ANALYSIS: Animal vs Flower")
print("=" * 70)
print()

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

b_middles = set(df[df['language'] == 'B']['word'].apply(extract_middle).dropna().unique())

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

# Build class lookup
class_lookup = {}
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    if posterior:
        best_class = max(posterior.items(), key=lambda x: x[1])
        class_lookup[middle] = {
            'best_class': best_class[0],
            'best_prob': best_class[1],
            'all_classes': posterior
        }

# Build A records
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: list(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()
a_records.columns = ['folio', 'line', 'middles', 'words']

# Infrastructure tokens to exclude from counts
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_', None}

# =============================================================================
# Analyze record structure by material class
# =============================================================================
print("-" * 70)
print("Step 1: Record size by material class")
print("-" * 70)
print()

class_record_stats = defaultdict(list)

for _, row in a_records.iterrows():
    middles = [m for m in row['middles'] if m not in infrastructure]
    record_size = len(middles)

    # Find material class tokens in this record
    for middle in middles:
        if middle in class_lookup:
            cls = class_lookup[middle]['best_class']
            prob = class_lookup[middle]['best_prob']
            # Only count if probability is meaningful
            if prob > 0.1:
                class_record_stats[cls].append({
                    'record': f"{row['folio']}:{row['line']}",
                    'token': middle,
                    'prob': prob,
                    'record_size': record_size,
                    'other_middles': [m for m in middles if m != middle]
                })

# Summarize by class
print(f"{'Class':<25} {'Tokens':<8} {'Avg Size':<10} {'Min':<6} {'Max':<6}")
print("-" * 60)

class_summaries = {}
for cls in sorted(class_record_stats.keys()):
    records = class_record_stats[cls]
    sizes = [r['record_size'] for r in records]
    avg_size = sum(sizes) / len(sizes)
    class_summaries[cls] = {
        'count': len(records),
        'avg_size': avg_size,
        'min_size': min(sizes),
        'max_size': max(sizes)
    }
    print(f"{cls:<25} {len(records):<8} {avg_size:<10.1f} {min(sizes):<6} {max(sizes):<6}")

# =============================================================================
# Deep dive: Animal vs Flower
# =============================================================================
print()
print("-" * 70)
print("Step 2: Animal vs cold_moist_flower detailed comparison")
print("-" * 70)
print()

# Animal records
animal_records = class_record_stats.get('animal', [])
flower_records = class_record_stats.get('cold_moist_flower', [])

print(f"ANIMAL records: {len(animal_records)}")
if animal_records:
    print("Sample records:")
    for r in sorted(animal_records, key=lambda x: -x['record_size'])[:5]:
        print(f"  {r['record']}: {r['token']} (P={r['prob']:.2f})")
        print(f"    Size: {r['record_size']}, Others: {r['other_middles'][:5]}...")

print()
print(f"COLD_MOIST_FLOWER records: {len(flower_records)}")
if flower_records:
    print("Sample records:")
    for r in sorted(flower_records, key=lambda x: -x['record_size'])[:5]:
        print(f"  {r['record']}: {r['token']} (P={r['prob']:.2f})")
        print(f"    Size: {r['record_size']}, Others: {r['other_middles'][:5]}...")

# =============================================================================
# Check if sparse records are a pattern for certain folios
# =============================================================================
print()
print("-" * 70)
print("Step 3: Folio patterns - where are sparse vs rich records?")
print("-" * 70)
print()

# Compute average record size per folio
folio_sizes = defaultdict(list)
for _, row in a_records.iterrows():
    middles = [m for m in row['middles'] if m not in infrastructure]
    folio_sizes[row['folio']].append(len(middles))

folio_avg = {f: sum(s)/len(s) for f, s in folio_sizes.items()}

# Where are animal tokens?
animal_folios = set(r['record'].split(':')[0] for r in animal_records)
flower_folios = set(r['record'].split(':')[0] for r in flower_records)

print(f"Animal tokens appear in {len(animal_folios)} folios")
print(f"Flower tokens appear in {len(flower_folios)} folios")
print()

# Average folio size for animal vs flower folios
animal_folio_avg = [folio_avg[f] for f in animal_folios if f in folio_avg]
flower_folio_avg = [folio_avg[f] for f in flower_folios if f in folio_avg]

if animal_folio_avg:
    print(f"Animal folios avg record size: {sum(animal_folio_avg)/len(animal_folio_avg):.1f}")
if flower_folio_avg:
    print(f"Flower folios avg record size: {sum(flower_folio_avg)/len(flower_folio_avg):.1f}")

# =============================================================================
# Check record type distribution (1-token vs multi-token)
# =============================================================================
print()
print("-" * 70)
print("Step 4: Record type distribution")
print("-" * 70)
print()

# Categorize records by size
def categorize_size(size):
    if size <= 1:
        return "1-token"
    elif size <= 3:
        return "2-3 tokens"
    elif size <= 6:
        return "4-6 tokens"
    else:
        return "7+ tokens"

animal_size_dist = defaultdict(int)
flower_size_dist = defaultdict(int)

for r in animal_records:
    cat = categorize_size(r['record_size'])
    animal_size_dist[cat] += 1

for r in flower_records:
    cat = categorize_size(r['record_size'])
    flower_size_dist[cat] += 1

print("Animal record size distribution:")
for cat in ["1-token", "2-3 tokens", "4-6 tokens", "7+ tokens"]:
    count = animal_size_dist.get(cat, 0)
    pct = count / len(animal_records) * 100 if animal_records else 0
    print(f"  {cat}: {count} ({pct:.0f}%)")

print()
print("Flower record size distribution:")
for cat in ["1-token", "2-3 tokens", "4-6 tokens", "7+ tokens"]:
    count = flower_size_dist.get(cat, 0)
    pct = count / len(flower_records) * 100 if flower_records else 0
    print(f"  {cat}: {count} ({pct:.0f}%)")

# =============================================================================
# Check if flowers are in labels vs text
# =============================================================================
print()
print("-" * 70)
print("Step 5: Check placement type (labels vs text)")
print("-" * 70)
print()

# Get placement info for tokens
df_a_full = df[df['language'] == 'A'].copy()
df_a_full['middle'] = df_a_full['word'].apply(extract_middle)

# Check placement for animal vs flower tokens
animal_tokens = set(r['token'] for r in animal_records)
flower_tokens_set = set(r['token'] for r in flower_records)

animal_placements = df_a_full[df_a_full['middle'].isin(animal_tokens)]['placement'].value_counts()
flower_placements = df_a_full[df_a_full['middle'].isin(flower_tokens_set)]['placement'].value_counts()

print("Animal token placements:")
for p, c in animal_placements.head(10).items():
    print(f"  {p}: {c}")

print()
print("Flower token placements:")
for p, c in flower_placements.head(10).items():
    print(f"  {p}: {c}")

# =============================================================================
# VERDICT
# =============================================================================
print()
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

if animal_records and flower_records:
    animal_avg = sum(r['record_size'] for r in animal_records) / len(animal_records)
    flower_avg = sum(r['record_size'] for r in flower_records) / len(flower_records)

    print(f"Average record size:")
    print(f"  Animal: {animal_avg:.1f} MIDDLEs")
    print(f"  Flower: {flower_avg:.1f} MIDDLEs")
    print()

    if flower_avg < animal_avg * 0.5:
        print("CONFIRMED: Flower records are structurally sparse compared to animal records.")
        print()
        print("Possible explanations:")
        print("  1. Different entry types in Currier A (single-item vs compound entries)")
        print("  2. Flowers may be LABELS, animals may be TEXT entries")
        print("  3. Different semantic density (flowers = simple, animals = complex processing)")
        print("  4. Registry organization differs by material class")
