#!/usr/bin/env python3
"""
Explore Brunschwig recipe properties for PP correlation research.
"""

import json
from collections import Counter

with open('data/brunschwig_complete.json', encoding='utf-8') as f:
    data = json.load(f)
recipes = data['recipes']
print(f'Total recipes: {len(recipes)}')
print()

# Check what fields exist
if recipes:
    print('Fields in first recipe:', list(recipes[0].keys()))
    print()

# Count by material_class
classes = Counter(r.get('material_class', 'UNKNOWN') for r in recipes)
print('By material_class:')
for cls, cnt in classes.most_common():
    print(f'  {cls}: {cnt}')
print()

# Count by fire_degree
degrees = Counter(r.get('fire_degree') for r in recipes)
print('By fire_degree:')
for deg, cnt in sorted(degrees.items(), key=lambda x: (x[0] is None, x[0])):
    print(f'  {deg}: {cnt}')
print()

# Count by has_procedure
has_proc = Counter(r.get('has_procedure', False) for r in recipes)
print('By has_procedure:', dict(has_proc))
print()

# What action types exist?
actions = Counter()
for r in recipes:
    steps = r.get('procedural_steps') or []
    for step in steps:
        actions[step.get('action', 'UNKNOWN')] += 1

print('Action types in procedures:')
for action, cnt in actions.most_common():
    print(f'  {action}: {cnt}')

# Show a few animals with procedures
print("\n" + "="*60)
print("ANIMALS WITH PROCEDURES")
print("="*60)
animals = [r for r in recipes if r.get('material_class') == 'animal' and r.get('has_procedure')]
for a in animals[:5]:
    print(f"\n{a['name_english']} (fire={a.get('fire_degree')}):")
    steps = a.get('procedural_steps') or []
    for step in steps:
        print(f"  {step['step']}. {step['action']}: {step.get('english_translation', '')[:60]}")

# Show fire_degree distribution by material_class
print("\n" + "="*60)
print("FIRE DEGREE BY MATERIAL CLASS")
print("="*60)
for cls in ['herb', 'animal', 'mineral', 'flower', 'tree', 'fruit']:
    cls_recipes = [r for r in recipes if r.get('material_class') == cls]
    if cls_recipes:
        degrees = [r.get('fire_degree') for r in cls_recipes if r.get('fire_degree')]
        if degrees:
            print(f"{cls}: min={min(degrees)}, max={max(degrees)}, avg={sum(degrees)/len(degrees):.1f}")
