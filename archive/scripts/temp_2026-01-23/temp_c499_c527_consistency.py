#!/usr/bin/env python3
"""
Consistency check: Do C499's P(animal)=1.00 MIDDLEs show C527's suffix pattern?

C499: Found 27 (later 18) RI MIDDLEs with P(animal)=1.00
C527: Animal-associated PP shows 0% -y/-dy, 78% -ey/-ol

If consistent: animal MIDDLEs should avoid -y/-dy, prefer -ey/-ol
If inconsistent: Need to investigate
"""

import json
import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load C499 results
with open(PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json', 'r') as f:
    c499_data = json.load(f)

# Get P(animal)=1.00 MIDDLEs
animal_middles = set()
herb_middles = set()
for result in c499_data['results']:
    top_class = result.get('top_class')
    top_prob = result.get('top_class_probability', 0)
    middle = result.get('middle')

    if top_class == 'animal' and top_prob >= 0.9:
        animal_middles.add(middle)
    elif top_class in ['herb', 'hot_dry_herb', 'cold_moist_flower'] and top_prob >= 0.7:
        herb_middles.add(middle)

print(f"C499 high-confidence animal MIDDLEs: {len(animal_middles)}")
print(f"C499 high-confidence herb MIDDLEs: {len(herb_middles)}")

# Extract suffix from tokens
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_suffix(token):
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            return s
    return None

# Collect tokens containing these MIDDLEs and their suffixes
animal_suffixes = Counter()
herb_suffixes = Counter()

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

        # Check if word contains any of the C499 MIDDLEs
        suffix = extract_suffix(word)
        if not suffix:
            continue

        for m in animal_middles:
            if m in word:
                animal_suffixes[suffix] += 1
                break

        for m in herb_middles:
            if m in word:
                herb_suffixes[suffix] += 1
                break

print("\n" + "="*60)
print("SUFFIX DISTRIBUTION FOR C499 MIDDLEs")
print("="*60)

animal_total = sum(animal_suffixes.values())
herb_total = sum(herb_suffixes.values())

print(f"\nAnimal MIDDLEs (P(animal)>=0.9): {animal_total} tokens with suffix")
print(f"Herb MIDDLEs (P(herb)>=0.7): {herb_total} tokens with suffix")

if animal_total > 0 and herb_total > 0:
    print(f"\n{'Suffix':<10} {'Animal':>10} {'Herb':>10} {'Animal %':>10} {'Herb %':>10}")
    print("-"*55)

    for suffix in ['y', 'dy', 'ey', 'ol', 'or', 'ar']:
        a_count = animal_suffixes[suffix]
        h_count = herb_suffixes[suffix]
        a_pct = 100 * a_count / animal_total if animal_total else 0
        h_pct = 100 * h_count / herb_total if herb_total else 0
        print(f"  -{suffix:<8} {a_count:>10} {h_count:>10} {a_pct:>9.1f}% {h_pct:>9.1f}%")

    # Group into LOW and HIGH fire
    animal_low = animal_suffixes['y'] + animal_suffixes['dy']
    animal_high = animal_suffixes['ey'] + animal_suffixes['ol']
    herb_low = herb_suffixes['y'] + herb_suffixes['dy']
    herb_high = herb_suffixes['ey'] + herb_suffixes['ol']

    print("\n" + "="*60)
    print("GROUPED COMPARISON (LOW fire vs HIGH fire)")
    print("="*60)
    print(f"\nC527 prediction:")
    print(f"  Animal should have: LOW ~0%, HIGH ~78%")
    print(f"  Herb should have:   LOW ~41%, HIGH ~27%")

    print(f"\nC499 MIDDLEs observed:")
    if animal_total > 0:
        print(f"  Animal (n={animal_total}): LOW={100*animal_low/animal_total:.1f}%, HIGH={100*animal_high/animal_total:.1f}%")
    if herb_total > 0:
        print(f"  Herb (n={herb_total}):   LOW={100*herb_low/herb_total:.1f}%, HIGH={100*herb_high/herb_total:.1f}%")

    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)
else:
    print("\nInsufficient data for comparison")
    print("Animal MIDDLEs from C499 may not have suffix tokens")

# Also show which MIDDLEs we're looking at
print("\n" + "="*60)
print("C499 ANIMAL MIDDLEs (P(animal)>=0.9)")
print("="*60)
print(sorted(animal_middles))

print("\n" + "="*60)
print("C499 HERB MIDDLEs (sample, P(herb)>=0.7)")
print("="*60)
print(sorted(list(herb_middles)[:20]))
