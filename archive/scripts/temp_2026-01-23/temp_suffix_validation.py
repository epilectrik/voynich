#!/usr/bin/env python3
"""
Validate suffix-fire correlation finding:
1. Sample size check - are animal PP counts adequate?
2. Length confounding - is suffix pattern an artifact of MIDDLE length?
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

PROJECT_ROOT = Path('.')

with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

# Animal-associated PP from C505
animal_pp = {'te', 'ho', 'ke'}

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

# Collect detailed data
tokens_data = []

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
            is_animal = middle in animal_pp
            tokens_data.append({
                'word': word,
                'middle': middle,
                'suffix': suffix,
                'middle_len': len(middle),
                'is_animal': is_animal
            })

print("="*60)
print("1. SAMPLE SIZE CHECK")
print("="*60)

animal_tokens = [t for t in tokens_data if t['is_animal']]
herb_tokens = [t for t in tokens_data if not t['is_animal']]

print(f"\nAnimal PP tokens with suffix: {len(animal_tokens)}")
print(f"Herb PP tokens with suffix: {len(herb_tokens)}")

# Break down by PP atom
animal_by_pp = Counter(t['middle'] for t in animal_tokens)
print(f"\nAnimal PP breakdown:")
for pp, count in animal_by_pp.most_common():
    print(f"  {pp}: {count} tokens")

# Suffix distribution with counts
animal_suffix = Counter(t['suffix'] for t in animal_tokens)
herb_suffix = Counter(t['suffix'] for t in herb_tokens)

print(f"\nSuffix counts (Animal vs Herb):")
print(f"{'Suffix':<8} {'Animal':>10} {'Herb':>10}")
print("-"*30)
for suffix in ['y', 'dy', 'ey', 'ol', 'or', 'ar', 'al', 'am']:
    print(f"  -{suffix:<6} {animal_suffix[suffix]:>10} {herb_suffix[suffix]:>10}")

# Chi-square test for the main finding
print("\n" + "="*60)
print("STATISTICAL TEST: Animal vs Herb suffix distribution")
print("="*60)

# Group into -y/-dy (low fire) vs -ey/-ol (high fire)
animal_low = animal_suffix['y'] + animal_suffix['dy']
animal_high = animal_suffix['ey'] + animal_suffix['ol']
herb_low = herb_suffix['y'] + herb_suffix['dy']
herb_high = herb_suffix['ey'] + herb_suffix['ol']

print(f"\nGrouped counts:")
print(f"  Animal: LOW(-y,-dy)={animal_low}, HIGH(-ey,-ol)={animal_high}")
print(f"  Herb:   LOW(-y,-dy)={herb_low}, HIGH(-ey,-ol)={herb_high}")

# 2x2 contingency table
contingency = [[animal_low, animal_high], [herb_low, herb_high]]
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test:")
print(f"  chi2 = {chi2:.2f}, p = {p:.2e}, dof = {dof}")
print(f"  Expected: {expected}")

if p < 0.001:
    print("  Result: HIGHLY SIGNIFICANT")
elif p < 0.05:
    print("  Result: SIGNIFICANT")
else:
    print("  Result: NOT SIGNIFICANT")

print("\n" + "="*60)
print("2. LENGTH CONFOUNDING CHECK")
print("="*60)

# Check if animal PP MIDDLEs have different lengths
animal_lengths = [t['middle_len'] for t in animal_tokens]
herb_lengths = [t['middle_len'] for t in herb_tokens]

print(f"\nMIDDLE length distribution:")
print(f"  Animal PP: mean={sum(animal_lengths)/len(animal_lengths):.2f}, median={sorted(animal_lengths)[len(animal_lengths)//2]}")
print(f"  Herb PP:   mean={sum(herb_lengths)/len(herb_lengths):.2f}, median={sorted(herb_lengths)[len(herb_lengths)//2]}")

# Length distribution
animal_len_dist = Counter(animal_lengths)
herb_len_dist = Counter(herb_lengths)
print(f"\n  Animal length counts: {dict(sorted(animal_len_dist.items()))}")
print(f"  Herb length counts: {dict(sorted(herb_len_dist.items()))}")

# Check suffix distribution BY LENGTH (controlling for length)
print("\n" + "="*60)
print("SUFFIX DISTRIBUTION BY MIDDLE LENGTH (controlling for length)")
print("="*60)

length_suffix = defaultdict(lambda: {'animal': Counter(), 'herb': Counter()})
for t in tokens_data:
    group = 'animal' if t['is_animal'] else 'herb'
    length_suffix[t['middle_len']][group][t['suffix']] += 1

print("\nFor each MIDDLE length, compare animal vs herb suffix pattern:")
for length in sorted(length_suffix.keys()):
    animal_s = length_suffix[length]['animal']
    herb_s = length_suffix[length]['herb']
    animal_total = sum(animal_s.values())
    herb_total = sum(herb_s.values())

    if animal_total >= 10 and herb_total >= 50:
        print(f"\n  Length {length}:")
        print(f"    Animal (n={animal_total}): -y={animal_s['y']}, -dy={animal_s['dy']}, -ey={animal_s['ey']}, -ol={animal_s['ol']}")
        print(f"    Herb (n={herb_total}): -y={herb_s['y']}, -dy={herb_s['dy']}, -ey={herb_s['ey']}, -ol={herb_s['ol']}")

        # Calculate LOW vs HIGH percentages
        if animal_total > 0:
            animal_low_pct = 100 * (animal_s['y'] + animal_s['dy']) / animal_total
            animal_high_pct = 100 * (animal_s['ey'] + animal_s['ol']) / animal_total
        else:
            animal_low_pct = animal_high_pct = 0

        herb_low_pct = 100 * (herb_s['y'] + herb_s['dy']) / herb_total
        herb_high_pct = 100 * (herb_s['ey'] + herb_s['ol']) / herb_total

        print(f"    Animal: LOW={animal_low_pct:.0f}%, HIGH={animal_high_pct:.0f}%")
        print(f"    Herb:   LOW={herb_low_pct:.0f}%, HIGH={herb_high_pct:.0f}%")

# Also check: does suffix correlate with length independent of animal/herb?
print("\n" + "="*60)
print("SUFFIX BY LENGTH (all PP, ignoring animal/herb)")
print("="*60)

all_length_suffix = defaultdict(Counter)
for t in tokens_data:
    all_length_suffix[t['middle_len']][t['suffix']] += 1

print(f"\n{'Length':<8} {'n':>6} {'-y':>8} {'-dy':>8} {'-ey':>8} {'-ol':>8}")
print("-"*50)
for length in sorted(all_length_suffix.keys()):
    suffixes = all_length_suffix[length]
    total = sum(suffixes.values())
    if total >= 50:
        y_pct = 100 * suffixes['y'] / total
        dy_pct = 100 * suffixes['dy'] / total
        ey_pct = 100 * suffixes['ey'] / total
        ol_pct = 100 * suffixes['ol'] / total
        print(f"  {length:<6} {total:>6} {y_pct:>7.1f}% {dy_pct:>7.1f}% {ey_pct:>7.1f}% {ol_pct:>7.1f}%")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
