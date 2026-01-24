#!/usr/bin/env python3
"""Quick stats on Brunschwig material classes and fire degrees."""

import json
from collections import Counter

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)
recipes = data['recipes']

# Count by material_class
classes = Counter(r.get('material_class') for r in recipes)
print('Material classes:')
for cls, cnt in classes.most_common():
    print(f'  {cls}: {cnt}')

# Count by fire_degree
fires = Counter(r.get('fire_degree') for r in recipes)
print('\nFire degrees:')
for fire, cnt in sorted(fires.items(), key=lambda x: (x[0] is None, x[0])):
    print(f'  {fire}: {cnt}')

# Material class by fire degree
print('\nMaterial class by fire degree:')
for fire in [1, 2, 3, 4]:
    recs = [r for r in recipes if r.get('fire_degree') == fire]
    cls_dist = Counter(r.get('material_class') for r in recs)
    print(f'  Fire {fire}: {dict(cls_dist)}')
