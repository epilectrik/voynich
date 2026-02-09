#!/usr/bin/env python3
"""Check Brunschwig for solvent/wine/oil usage."""

import sys
import io
import json
from pathlib import Path

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(Path(__file__).parent.parent / 'data' / 'brunschwig_curated_v3.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

recipes = d.get('recipes', [])

# Check for wine/alcohol/solvent mentions
solvent_keywords = ['wine', 'wein', 'alcohol', 'aqua vitae', 'spirit', 'brantwein', 'öl', 'oil']
solvent_recipes = []
for r in recipes:
    text = str(r).lower()
    for kw in solvent_keywords:
        if kw in text:
            solvent_recipes.append((r, kw))
            break

print(f"Recipes with solvent/wine/oil keywords: {len(solvent_recipes)} / {len(recipes)}")
print()

for r, kw in solvent_recipes[:15]:
    print(f"{r.get('name_english','?')[:40]:<42} [matched: {kw}]")
    if 'procedural_steps' in r and r['procedural_steps']:
        steps = r['procedural_steps']
        if isinstance(steps, list):
            for s in steps[:2]:
                print(f"  -> {str(s)[:70]}")

print("\n" + "="*70)
print("METHOD DISTRIBUTION")
print("="*70)

from collections import Counter
methods = Counter(r.get('method', 'unknown') for r in recipes)
for m, c in methods.most_common():
    print(f"  {m}: {c}")

print("\n" + "="*70)
print("MATERIAL CLASS DISTRIBUTION")
print("="*70)

mat_classes = Counter(r.get('material_class', 'unknown') for r in recipes)
for m, c in mat_classes.most_common():
    print(f"  {m}: {c}")

# Look for non-water products
print("\n" + "="*70)
print("CHECKING FOR NON-WATER PRODUCTS")
print("="*70)

for r in recipes:
    steps = str(r.get('procedural_steps', '')).lower()
    name = r.get('name_english', '')

    # Oil extraction indicators
    if any(x in steps for x in ['oil', 'öl', 'fett', 'fat', 'resin', 'harz']):
        print(f"OIL/RESIN: {name[:50]}")
        print(f"  Steps: {steps[:100]}")
        print()
