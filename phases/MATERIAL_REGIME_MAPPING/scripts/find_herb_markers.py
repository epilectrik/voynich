"""
FIND HERB-SPECIFIC PP MARKERS

Goal: Identify PP MIDDLEs enriched in herb records vs animal records.
This will help us distinguish the two classes more precisely.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("FINDING HERB-SPECIFIC PP MARKERS")
print("=" * 70)

# Build A record profiles
a_records = defaultdict(lambda: {
    'middles': [],
    'suffixes': [],
})

for token in tx.currier_a():
    record_id = f"{token.folio}:{token.line}"
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            a_records[record_id]['middles'].append(m.middle)
        if m.suffix:
            a_records[record_id]['suffixes'].append(m.suffix)

# Classify records by suffix pattern
ANIMAL_SUFFIXES = {'ey', 'ol'}
HERB_SUFFIXES = {'y', 'dy'}

animal_records = []
herb_records = []
neutral_records = []

for record_id, data in a_records.items():
    suffixes = data['suffixes']
    animal_count = sum(1 for s in suffixes if s in ANIMAL_SUFFIXES)
    herb_count = sum(1 for s in suffixes if s in HERB_SUFFIXES)

    if animal_count > herb_count and animal_count >= 2:
        animal_records.append(record_id)
    elif herb_count > animal_count and herb_count >= 2:
        herb_records.append(record_id)
    else:
        neutral_records.append(record_id)

print(f"\nRecord classification by suffix pattern:")
print(f"  Animal-signature: {len(animal_records)}")
print(f"  Herb-signature: {len(herb_records)}")
print(f"  Neutral: {len(neutral_records)}")

# Count PP MIDDLEs in each class
animal_middles = Counter()
herb_middles = Counter()
neutral_middles = Counter()

for record_id in animal_records:
    for m in a_records[record_id]['middles']:
        animal_middles[m] += 1

for record_id in herb_records:
    for m in a_records[record_id]['middles']:
        herb_middles[m] += 1

for record_id in neutral_records:
    for m in a_records[record_id]['middles']:
        neutral_middles[m] += 1

# Find enrichment
print("\n" + "=" * 70)
print("PP MIDDLE ENRICHMENT BY MATERIAL CLASS")
print("=" * 70)

# Normalize by record count
animal_norm = {m: c / len(animal_records) for m, c in animal_middles.items()}
herb_norm = {m: c / len(herb_records) for m, c in herb_middles.items()}
neutral_norm = {m: c / len(neutral_records) for m, c in neutral_middles.items()}

# Find animal-enriched MIDDLEs
all_middles = set(animal_middles.keys()) | set(herb_middles.keys())

animal_enriched = []
herb_enriched = []

for middle in all_middles:
    animal_rate = animal_norm.get(middle, 0.001)
    herb_rate = herb_norm.get(middle, 0.001)
    neutral_rate = neutral_norm.get(middle, 0.001)

    # Animal vs herb
    if animal_rate > 0 and herb_rate > 0:
        animal_vs_herb = animal_rate / herb_rate
        herb_vs_animal = herb_rate / animal_rate

        if animal_vs_herb > 2.0 and animal_middles[middle] >= 5:
            animal_enriched.append({
                'middle': middle,
                'animal_rate': animal_rate,
                'herb_rate': herb_rate,
                'enrichment': animal_vs_herb,
                'count': animal_middles[middle],
            })

        if herb_vs_animal > 2.0 and herb_middles[middle] >= 5:
            herb_enriched.append({
                'middle': middle,
                'animal_rate': animal_rate,
                'herb_rate': herb_rate,
                'enrichment': herb_vs_animal,
                'count': herb_middles[middle],
            })

# Sort by enrichment
animal_enriched.sort(key=lambda x: -x['enrichment'])
herb_enriched.sort(key=lambda x: -x['enrichment'])

print("\nANIMAL-ENRICHED PP MIDDLEs (>2x vs herb, min 5 occurrences):")
print(f"{'MIDDLE':<12} {'Enrichment':<12} {'Animal Rate':<15} {'Herb Rate':<15} {'Count'}")
print("-" * 65)
for m in animal_enriched[:15]:
    print(f"{m['middle']:<12} {m['enrichment']:.2f}x        {m['animal_rate']:.4f}          {m['herb_rate']:.4f}          {m['count']}")

print("\nHERB-ENRICHED PP MIDDLEs (>2x vs animal, min 5 occurrences):")
print(f"{'MIDDLE':<12} {'Enrichment':<12} {'Herb Rate':<15} {'Animal Rate':<15} {'Count'}")
print("-" * 65)
for m in herb_enriched[:15]:
    print(f"{m['middle']:<12} {m['enrichment']:.2f}x        {m['herb_rate']:.4f}          {m['animal_rate']:.4f}          {m['count']}")

# Check if herb has distinct PP markers
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nAnimal-enriched MIDDLEs found: {len(animal_enriched)}")
print(f"Herb-enriched MIDDLEs found: {len(herb_enriched)}")

if len(herb_enriched) > 0:
    print("\nTop herb-specific markers for improved classification:")
    for m in herb_enriched[:5]:
        print(f"  '{m['middle']}': {m['enrichment']:.1f}x herb-enriched")
else:
    print("\nNo strong herb-specific PP markers found.")
    print("This suggests herbs may NOT have a distinct PP profile from animals,")
    print("only a distinct SUFFIX profile.")

# Save results
results = {
    'animal_enriched': animal_enriched,
    'herb_enriched': herb_enriched,
    'record_counts': {
        'animal': len(animal_records),
        'herb': len(herb_records),
        'neutral': len(neutral_records),
    },
}

with open('phases/MATERIAL_REGIME_MAPPING/results/pp_marker_enrichment.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: phases/MATERIAL_REGIME_MAPPING/results/pp_marker_enrichment.json")
