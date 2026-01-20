#!/usr/bin/env python3
"""Check material input types (material_source) in Brunschwig data."""

import json
from collections import Counter

with open('data/brunschwig_materials_master.json', encoding='utf-8') as f:
    brun = json.load(f)

# Count material sources
sources = Counter(m.get('material_source', 'UNK') for m in brun['materials'])
print('MATERIAL INPUT TYPES (material_source):')
print('=' * 50)
for src, count in sources.most_common():
    print(f'  {src}: {count}')

print()
print('=' * 50)
print('MATERIAL SOURCE -> PRODUCT TYPE')
print('=' * 50)

# Cross-tabulation
cross = {}
for m in brun['materials']:
    src = m.get('material_source', 'UNK')
    prod = m.get('predicted_product_type', 'UNK')
    if src not in cross:
        cross[src] = Counter()
    cross[src][prod] += 1

for src in sorted(cross.keys()):
    print(f'{src}:')
    for prod, count in cross[src].most_common():
        print(f'    {prod}: {count}')

print()
print('=' * 50)
print('PRODUCT TYPE -> MATERIAL SOURCES')
print('=' * 50)

# Reverse mapping
prod_to_src = {}
for m in brun['materials']:
    src = m.get('material_source', 'UNK')
    prod = m.get('predicted_product_type', 'UNK')
    if prod not in prod_to_src:
        prod_to_src[prod] = Counter()
    prod_to_src[prod][src] += 1

for prod in sorted(prod_to_src.keys()):
    total = sum(prod_to_src[prod].values())
    print(f'{prod} (n={total}):')
    for src, count in prod_to_src[prod].most_common():
        pct = 100 * count / total
        print(f'    {src}: {count} ({pct:.1f}%)')
