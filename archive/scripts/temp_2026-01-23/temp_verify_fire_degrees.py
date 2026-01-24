#!/usr/bin/env python3
"""
Verify fire_degree values in brunschwig_curated_v2.json against source text.
"""

import json
import random

random.seed(42)

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']
print(f'Total recipes: {len(recipes)}')

# Check fire degree distribution
from collections import Counter
fire_dist = Counter(r.get('fire_degree') for r in recipes)
print(f'\nFire degree distribution:')
for fire, cnt in sorted(fire_dist.items(), key=lambda x: (x[0] is None, x[0])):
    print(f'  {fire}: {cnt}')

# Sample 30 random entries, spread across the dataset
sample = random.sample(recipes, 30)

# Show id, name, fire_degree, and source_lines for verification
print('\n' + '='*80)
print('SAMPLED ENTRIES FOR VERIFICATION')
print('='*80)

for r in sorted(sample, key=lambda x: x['id']):
    fire = r.get('fire_degree', 'NONE')
    lines = r.get('source_lines', {})
    start = lines.get('start', '?')
    end = lines.get('end', '?')
    print(f"\nID {r['id']:3d}: {r['name_english']}")
    print(f"  German: {r['name_german']}")
    print(f"  Fire degree: {fire}")
    print(f"  Source lines: {start}-{end}")
    print(f"  Material class: {r.get('material_class', '?')}")
