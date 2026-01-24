#!/usr/bin/env python3
"""Find animal-based recipes."""

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

# Find animal-based recipes (non-plant)
animal_classes = ['bird', 'animal', 'insect', 'reptile', 'mollusk', 'animal_product', 'bodily_fluid']
animals = [r for r in data['recipes'] if r.get('material_class') in animal_classes]

print(f'Animal-based recipes: {len(animals)}')
for r in animals:
    print(f"  {r['id']}. {r['name_german']} ({r.get('material_class')}) - lines {r['source_lines']['start']}-{r['source_lines']['end']}")
    if r.get('procedural_steps'):
        for s in r['procedural_steps']:
            print(f"      {s['step']}. {s['action']}: {s.get('german_text', '')}")

# Also look at all material classes
print('\n=== Material class distribution ===')
from collections import Counter
classes = Counter(r.get('material_class') for r in data['recipes'])
for cls, count in classes.most_common():
    print(f"  {cls}: {count}")
