#!/usr/bin/env python3
"""
What product types does Brunschwig describe?
"""

import json
from collections import Counter
from pathlib import Path

with open('data/brunschwig_curated_v3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("BRUNSCHWIG RECIPE STRUCTURE")
print("="*60)

# Check method field
methods = Counter()
for recipe in data['recipes']:
    if recipe.get('method'):
        methods[recipe['method']] += 1

print('\nDistillation methods mentioned:')
for m, c in methods.most_common():
    print(f'  {m}: {c}')

# Check action taxonomy
print("\nAction taxonomy defined:")
for action, desc in data.get('action_taxonomy', {}).items():
    print(f"  {action}: {desc}")

# Look at actual procedural steps
print("\n" + "="*60)
print("PROCEDURAL ACTIONS USED")
print("="*60)

actions = Counter()
for recipe in data['recipes']:
    steps = recipe.get('procedural_steps') or []
    for step in steps:
        actions[step.get('action', 'UNKNOWN')] += 1

print("\nAction frequency:")
for action, count in actions.most_common():
    print(f"  {action}: {count}")

# Read the actual source text to find product types
print("\n" + "="*60)
print("SEARCHING SOURCE TEXT FOR PRODUCT TYPES")
print("="*60)

with open('sources/brunschwig_1500_text.txt', 'r', encoding='utf-8') as f:
    text = f.read().lower()

# Common medieval product terms
product_terms = [
    'wasser', 'water',  # water
    'oel', 'oil', 'oleum',  # oil
    'pulver', 'powder',  # powder
    'syrup', 'sirup',  # syrup
    'salb', 'salve', 'ointment',  # ointment
    'essent', 'essence', 'quintessent',  # essence
    'tinctur', 'tincture',  # tincture
    'spirit', 'geist',  # spirit
    'balsam',  # balsam
    'extract',  # extract
]

print("\nProduct type mentions in source text:")
for term in product_terms:
    count = text.count(term)
    if count > 0:
        print(f"  '{term}': {count} occurrences")

# Check if there are different output forms per recipe
print("\n" + "="*60)
print("SAMPLE RECIPES - WHAT IS THE OUTPUT?")
print("="*60)

for recipe in data['recipes'][:10]:
    name = recipe.get('name_english', recipe.get('name_german'))
    method = recipe.get('method', 'unspecified')
    steps = recipe.get('procedural_steps') or []
    final_action = steps[-1]['action'] if steps else 'none'
    print(f"\n{name}:")
    print(f"  Method: {method}")
    print(f"  Final action: {final_action}")
    if steps:
        print(f"  Last step: {steps[-1].get('english_translation', '')[:60]}...")
