#!/usr/bin/env python3
"""
Investigate the label vs text distinction for material classes.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("LABEL vs TEXT ANALYSIS")
print("=" * 70)
print()

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

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

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

class_lookup = {}
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    if posterior:
        best = max(posterior.items(), key=lambda x: x[1])
        class_lookup[middle] = {'class': best[0], 'prob': best[1]}

# =============================================================================
# What's in labels?
# =============================================================================
print("-" * 70)
print("Step 1: What's in Currier A labels?")
print("-" * 70)
print()

# Label placements start with 'L'
labels_df = df_a[df_a['placement'].str.startswith('L', na=False)]
text_df = df_a[df_a['placement'].str.startswith('P', na=False)]

print(f"Total A tokens in LABELS: {len(labels_df)}")
print(f"Total A tokens in TEXT: {len(text_df)}")
print()

# Unique MIDDLEs in labels vs text
label_middles = set(labels_df['middle'].dropna().unique())
text_middles = set(text_df['middle'].dropna().unique())

print(f"Unique MIDDLEs in labels: {len(label_middles)}")
print(f"Unique MIDDLEs in text: {len(text_middles)}")
print(f"Label-only MIDDLEs: {len(label_middles - text_middles)}")
print(f"Text-only MIDDLEs: {len(text_middles - label_middles)}")
print()

# =============================================================================
# Material classes in labels vs text
# =============================================================================
print("-" * 70)
print("Step 2: Material classes in labels vs text")
print("-" * 70)
print()

# Count by class
label_classes = defaultdict(int)
text_classes = defaultdict(int)

for middle in label_middles:
    if middle in class_lookup and class_lookup[middle]['prob'] > 0.1:
        label_classes[class_lookup[middle]['class']] += 1

for middle in text_middles:
    if middle in class_lookup and class_lookup[middle]['prob'] > 0.1:
        text_classes[class_lookup[middle]['class']] += 1

print("Classes in LABELS:")
for cls, count in sorted(label_classes.items(), key=lambda x: -x[1]):
    print(f"  {cls}: {count}")

print()
print("Classes in TEXT:")
for cls, count in sorted(text_classes.items(), key=lambda x: -x[1]):
    print(f"  {cls}: {count}")

# =============================================================================
# The specific flower tokens
# =============================================================================
print()
print("-" * 70)
print("Step 3: Where are the top flower tokens?")
print("-" * 70)
print()

top_flowers = ['okaro', 'ockho', 'ysho', 'ota', 'aram']

for token in top_flowers:
    token_df = df_a[df_a['middle'] == token]
    if len(token_df) == 0:
        print(f"{token}: NOT FOUND")
        continue

    placements = token_df['placement'].value_counts()
    folios = token_df['folio'].unique()

    print(f"{token}:")
    print(f"  Folios: {list(folios)}")
    print(f"  Placements: {dict(placements)}")

    # What kind of folios are these?
    for folio in folios:
        folio_df = df_a[df_a['folio'] == folio]
        label_count = len(folio_df[folio_df['placement'].str.startswith('L', na=False)])
        text_count = len(folio_df[folio_df['placement'].str.startswith('P', na=False)])
        print(f"    {folio}: {label_count} label tokens, {text_count} text tokens")
    print()

# =============================================================================
# Contrast with animal tokens
# =============================================================================
print("-" * 70)
print("Step 4: Where are the top animal tokens?")
print("-" * 70)
print()

top_animals = ['eoschso', 'eyd', 'chald', 'teold', 'olfcho', 'hdaoto', 'cthso']

for token in top_animals:
    token_df = df_a[df_a['middle'] == token]
    if len(token_df) == 0:
        print(f"{token}: NOT FOUND")
        continue

    placements = token_df['placement'].value_counts()
    folios = token_df['folio'].unique()

    print(f"{token}:")
    print(f"  Folios: {list(folios)}")
    print(f"  Placements: {dict(placements)}")
    print()

# =============================================================================
# Check what botanical (herbal) folios look like
# =============================================================================
print("-" * 70)
print("Step 5: Herbal folio structure")
print("-" * 70)
print()

# Known herbal section folios (pharmaceutical/botanical)
# These typically have illustrations with plant labels
herbal_folios = ['f1r', 'f1v', 'f2r', 'f2v', 'f3r', 'f3v', 'f4r', 'f4v', 'f5r', 'f5v']

for folio in herbal_folios:
    folio_df = df_a[df_a['folio'] == folio]
    if len(folio_df) == 0:
        continue

    label_df = folio_df[folio_df['placement'].str.startswith('L', na=False)]
    text_df = folio_df[folio_df['placement'].str.startswith('P', na=False)]

    label_middles = set(label_df['middle'].dropna().unique())
    text_middles = set(text_df['middle'].dropna().unique())

    # Check for flower/herb tokens
    flower_in_labels = [m for m in label_middles if m in class_lookup and 'flower' in class_lookup[m]['class']]
    herb_in_labels = [m for m in label_middles if m in class_lookup and 'herb' in class_lookup[m]['class']]

    print(f"{folio}: {len(label_df)} label tokens, {len(text_df)} text tokens")
    if flower_in_labels:
        print(f"  Flower in labels: {flower_in_labels}")
    if herb_in_labels:
        print(f"  Herb in labels: {herb_in_labels}")

# =============================================================================
# VERDICT
# =============================================================================
print()
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

label_flower = sum(1 for m in label_middles if m in class_lookup and 'flower' in class_lookup[m]['class'])
text_flower = sum(1 for m in text_middles if m in class_lookup and 'flower' in class_lookup[m]['class'])
label_animal = sum(1 for m in label_middles if m in class_lookup and class_lookup[m]['class'] == 'animal')
text_animal = sum(1 for m in text_middles if m in class_lookup and class_lookup[m]['class'] == 'animal')

print(f"Flower tokens: {label_flower} in labels, {text_flower} in text")
print(f"Animal tokens: {label_animal} in labels, {text_animal} in text")
print()

if label_flower > text_flower:
    print("FINDING: Flower tokens are preferentially in LABELS")
    print("This explains sparse records - labels are single-item annotations")
elif label_animal < text_animal:
    print("FINDING: Animal tokens are preferentially in TEXT")
    print("This explains rich records - text entries have multi-token structure")
