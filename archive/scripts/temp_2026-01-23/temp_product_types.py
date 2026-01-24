#!/usr/bin/env python3
"""Explore product types for PP profiling."""

import json
from collections import Counter

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    d = json.load(f)

recipes = d['recipes']

print("MATERIAL CLASSES IN BRUNSCHWIG:")
print("-" * 50)
classes = Counter(r.get('material_class') for r in recipes)
for cls, cnt in classes.most_common():
    print(f"  {cls}: {cnt}")

print("\n\nFIRE DEGREE + MATERIAL CLASS COMBINATIONS:")
print("-" * 50)
combos = Counter((r.get('material_class'), r.get('fire_degree')) for r in recipes)
for (cls, fire), cnt in combos.most_common(30):
    print(f"  {cls} + fire={fire}: {cnt}")

print("\n\nMETHOD CATEGORIES:")
print("-" * 50)
methods = Counter(r.get('method', 'none') for r in recipes)
for method, cnt in methods.most_common(15):
    print(f"  {method[:50]}: {cnt}")
