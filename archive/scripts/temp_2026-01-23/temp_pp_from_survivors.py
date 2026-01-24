#!/usr/bin/env python3
"""
Analyze PP/RI from a_record_survivors.json properly.
Find records containing animal-associated MIDDLEs and get their PP profiles.
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript for B MIDDLE extraction
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load A record survivors
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

# Get all unique MIDDLEs from A records
all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

print(f"Total unique MIDDLEs in A records: {len(all_a_middles)}")

# Need to get B MIDDLEs - let me check how the original script did it
# From the survivors data, we need to know which MIDDLEs appear in B

# Load class_token_map for B MIDDLEs
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

# class_to_middles tells us which MIDDLEs each B class has
class_to_middles = class_map['class_to_middles']

# Collect all MIDDLEs from B classes
b_middles_from_classes = set()
for cls, middles in class_to_middles.items():
    b_middles_from_classes.update(middles)

print(f"Unique MIDDLEs in B classes: {len(b_middles_from_classes)}")

# Now compute RI/PP
ri_middles = all_a_middles - b_middles_from_classes
pp_middles = all_a_middles & b_middles_from_classes

print(f"\nRI MIDDLEs (A-only): {len(ri_middles)}")
print(f"PP MIDDLEs (shared): {len(pp_middles)}")

# ============================================================
# Find animal-associated records
# ============================================================
print("\n" + "="*60)
print("ANIMAL-ASSOCIATED MIDDLES IN A RECORDS")
print("="*60)

# From reverse trace results, these MIDDLEs have high animal priors
animal_middles = ['eyd', 'tchyf', 'ofy', 'opcho', 'eoc', 'eso',
                  'olfcho', 'cthso', 'hdaoto', 'teold', 'eoschso']

# Find which records contain these
for m in animal_middles:
    matching_records = [rec for rec in records if m in rec['a_middles']]
    if matching_records:
        print(f"\n'{m}' found in {len(matching_records)} record(s):")
        for rec in matching_records[:3]:
            middles = set(rec['a_middles'])
            pp = middles & pp_middles
            ri = middles & ri_middles
            print(f"  {rec['a_record']}: PP={pp}, RI={ri}")

# ============================================================
# Show PP MIDDLE profiles for records with animal MIDDLEs
# ============================================================
print("\n" + "="*60)
print("PP PROFILES FOR ANIMAL RECORDS")
print("="*60)

# Find all records with any animal MIDDLE
animal_records = []
for rec in records:
    middles = set(rec['a_middles'])
    animal_in_record = middles & set(animal_middles)
    if animal_in_record:
        animal_records.append({
            'record': rec['a_record'],
            'animal_middles': animal_in_record,
            'pp_middles': middles & pp_middles,
            'ri_middles': middles & ri_middles,
            'survival': rec['surviving_class_count']
        })

print(f"\nTotal records with animal MIDDLEs: {len(animal_records)}")

for ar in animal_records:
    print(f"\n{ar['record']}:")
    print(f"  Animal RI: {ar['animal_middles']}")
    print(f"  PP: {ar['pp_middles']}")
    print(f"  Other RI: {ar['ri_middles'] - ar['animal_middles']}")
    print(f"  Classes surviving: {ar['survival']}")

# ============================================================
# Compare PP profiles
# ============================================================
print("\n" + "="*60)
print("COMMON PP MIDDLES IN ANIMAL RECORDS")
print("="*60)

if animal_records:
    # Aggregate PP across animal records
    pp_counter = Counter()
    for ar in animal_records:
        for pp in ar['pp_middles']:
            pp_counter[pp] += 1

    print(f"\nPP frequency in {len(animal_records)} animal records:")
    for pp, cnt in pp_counter.most_common(20):
        pct = 100 * cnt / len(animal_records)
        print(f"  '{pp}': {cnt} ({pct:.1f}%)")

# ============================================================
# Contrast with non-animal records
# ============================================================
print("\n" + "="*60)
print("CONTRAST: PP IN NON-ANIMAL RECORDS")
print("="*60)

non_animal_records = [rec for rec in records
                      if not (set(rec['a_middles']) & set(animal_middles))]

pp_counter_non = Counter()
for rec in non_animal_records:
    middles = set(rec['a_middles'])
    for pp in middles & pp_middles:
        pp_counter_non[pp] += 1

print(f"\nPP frequency in {len(non_animal_records)} non-animal records:")
for pp, cnt in pp_counter_non.most_common(20):
    pct = 100 * cnt / len(non_animal_records)
    print(f"  '{pp}': {cnt} ({pct:.1f}%)")

# ============================================================
# What PP distinguishes animal records?
# ============================================================
print("\n" + "="*60)
print("DIFFERENTIAL PP (ANIMAL vs NON-ANIMAL)")
print("="*60)

if animal_records and len(animal_records) > 0:
    print("\nPP more common in animal records:")
    for pp, cnt in pp_counter.most_common():
        animal_rate = cnt / len(animal_records)
        non_animal_cnt = pp_counter_non.get(pp, 0)
        non_animal_rate = non_animal_cnt / len(non_animal_records) if non_animal_records else 0

        if animal_rate > non_animal_rate * 1.5:  # 50% more common in animal
            print(f"  '{pp}': {animal_rate*100:.1f}% animal vs {non_animal_rate*100:.1f}% non-animal")
