#!/usr/bin/env python3
"""
Does SUFFIX correlate with FIRE DEGREE?

If suffix encodes water quality/fraction:
- Higher fire degree = different suffix pattern
- Gentle fire (1-2) vs strong fire (3-4) might produce different outputs
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load Brunschwig fire degrees
with open(PROJECT_ROOT / 'data' / 'brunschwig_curated_v3.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)

# Build material -> fire degree mapping
material_fire_degree = {}
for recipe in brunschwig['recipes']:
    name = recipe.get('name_english', '').lower()
    german = recipe.get('name_german', '').lower()
    fire = recipe.get('fire_degree')
    if fire:
        material_fire_degree[name] = fire
        material_fire_degree[german] = fire

print(f"Materials with fire degree: {len(material_fire_degree)}")
print(f"Fire degree distribution: {Counter(material_fire_degree.values())}")

# Load PP profiles that might correlate with fire degree
# We established earlier that PP encodes procedural compatibility
# Let's check if certain PP atoms correlate with fire degree

with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_parts(token):
    if not token:
        return None, None, None
    prefix = None
    suffix = None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break
    return prefix, token if token else None, suffix

# Check if we have fire degree annotations in our folio data
# Or we can use the PP profiles we established correlate with material classes

# Actually, let's check a simpler thing:
# Do certain suffixes correlate with certain PREFIX patterns that we know
# correlate with processing intensity?

# From earlier work, we know:
# - ch/sh = sister pairs, ch = precision mode
# - qo = escape routes
# - ct = registry reference
# - ok/ot = sister pairs

# Let's check suffix distribution by PREFIX to see if there's a "processing intensity" gradient

print("\n" + "="*60)
print("SUFFIX DISTRIBUTION BY PREFIX (proxy for processing intensity)")
print("="*60)

prefix_suffix = defaultdict(Counter)
suffix_total = Counter()

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if prefix and suffix:
            prefix_suffix[prefix][suffix] += 1
            suffix_total[suffix] += 1

# Group prefixes by hypothesized intensity
low_intensity = ['ch', 'sh']  # Precision, careful
medium_intensity = ['qo', 'ok', 'ot']  # Standard, escape
high_intensity = ['ct', 'd', 'o', 's']  # Registry, direct

print("\nSuffix distribution by intensity group:")

for group_name, prefixes in [('LOW (ch,sh)', low_intensity),
                              ('MED (qo,ok,ot)', medium_intensity),
                              ('HIGH (ct,d,o,s)', high_intensity)]:
    group_suffixes = Counter()
    for p in prefixes:
        group_suffixes.update(prefix_suffix[p])

    total = sum(group_suffixes.values())
    if total < 100:
        continue

    print(f"\n{group_name} (n={total}):")
    for suffix in ['y', 'dy', 'ol', 'or', 'ey', 'ar', 'al', 'am']:
        pct = 100 * group_suffixes[suffix] / total
        print(f"  -{suffix}: {pct:>5.1f}%")

# Now let's try to correlate with actual fire degree data
# We need to find Currier A folios that might correspond to specific Brunschwig materials

print("\n" + "="*60)
print("DIRECT FIRE DEGREE CORRELATION (via folio classification)")
print("="*60)

# Load folio classifications if they exist
folio_class_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'folio_classifications.json'
if folio_class_path.exists():
    with open(folio_class_path, 'r') as f:
        folio_classes = json.load(f)
    print(f"Loaded folio classifications: {len(folio_classes)} folios")
else:
    print("No folio classifications found")
    folio_classes = {}

# Alternative: use the material class from PP profiles
# We established that certain PP atoms correlate with material classes
# Animal materials tend to use higher fire degrees

# Check if certain PP atoms (that correlate with animal/mineral) have different suffix patterns
print("\n" + "="*60)
print("PP ATOMS BY SUFFIX (looking for fire degree proxy)")
print("="*60)

# From C505: 'te' 16.1x, 'ho' 8.6x, 'ke' 5.1x enriched in animal records
animal_pp = {'te', 'ho', 'ke'}
# Standard herbs would be other PP atoms

pp_suffix = defaultdict(Counter)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if middle and middle in pp_middles and suffix:
            pp_suffix[middle][suffix] += 1

# Compare animal-associated PP vs others
animal_suffixes = Counter()
herb_suffixes = Counter()

for pp, suffixes in pp_suffix.items():
    if pp in animal_pp:
        animal_suffixes.update(suffixes)
    else:
        herb_suffixes.update(suffixes)

animal_total = sum(animal_suffixes.values())
herb_total = sum(herb_suffixes.values())

print(f"\nAnimal-associated PP (te, ho, ke): {animal_total} tokens with suffix")
print(f"Other PP (herbs): {herb_total} tokens with suffix")

if animal_total > 50 and herb_total > 50:
    print(f"\n{'Suffix':<10} {'Animal %':>12} {'Herb %':>12} {'Diff':>10}")
    print("-"*45)

    for suffix in ['y', 'dy', 'ol', 'or', 'ey', 'ar', 'al', 'am']:
        animal_pct = 100 * animal_suffixes[suffix] / animal_total
        herb_pct = 100 * herb_suffixes[suffix] / herb_total
        diff = animal_pct - herb_pct
        marker = "***" if abs(diff) > 5 else ""
        print(f"  -{suffix:<8} {animal_pct:>11.1f}% {herb_pct:>11.1f}% {diff:>+9.1f}% {marker}")

print("\n" + "="*60)
print("INTERPRETATION")
print("="*60)
print("""
Fire degree in Brunschwig:
  1 = lukewarm (balneum mariae)
  2 = noticeably warm
  3 = almost seething
  4 = boiling/destructive

If suffix = water quality/fraction:
  - Low fire (1-2) should produce gentler waters
  - High fire (3-4) should produce stronger extracts/oils

Animal materials often need higher fire degrees.
If animal-PP has different suffix pattern, suffix may encode fire intensity.
""")
