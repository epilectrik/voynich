#!/usr/bin/env python3
"""
Does processing state affect procedure, or just identity?

If processing affects PROCEDURE → encoded in PP
If processing is just IDENTIFICATION → encoded in RI extension
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

print("="*70)
print("DOES PROCESSING STATE AFFECT PROCEDURE?")
print("="*70)

# Find materials with variants (same base material, different preparations)
# Look for patterns like "X root" vs "X herb" vs "X flower"

base_materials = defaultdict(list)

for recipe in recipes:
    name = recipe.get('name_english', '')
    if not name:
        continue

    # Extract base material (crude heuristic)
    parts = name.lower().split()

    # Check for "X root", "X herb", "X flower" patterns
    for suffix in ['root', 'herb', 'flower', 'leaf', 'seed', 'bark', 'sap', 'blood', 'only']:
        if suffix in parts:
            # Base is everything before the suffix
            idx = parts.index(suffix)
            base = ' '.join(parts[:idx]) if idx > 0 else None
            if base:
                base_materials[base].append(recipe)
                break

print("\nMaterials with multiple part-based variants:")

for base, variants in sorted(base_materials.items(), key=lambda x: -len(x[1])):
    if len(variants) < 2:
        continue

    print(f"\n{base.upper()}:")
    for v in variants:
        name = v.get('name_english', '?')
        proc = v.get('instruction_sequence', [])
        fire = v.get('fire_degree', '?')
        parts = v.get('parts_used', [])
        print(f"  {name}")
        print(f"    Fire: {fire}, Parts: {parts}, Procedure: {proc}")

# Check if same base with different parts has same or different procedures
print("\n" + "="*70)
print("DO DIFFERENT PARTS OF SAME PLANT USE SAME PROCEDURE?")
print("="*70)

same_proc = 0
diff_proc = 0

for base, variants in base_materials.items():
    if len(variants) < 2:
        continue

    procs = [tuple(v.get('instruction_sequence') or []) for v in variants]
    unique_procs = set(procs)

    if len(unique_procs) == 1:
        same_proc += 1
    else:
        diff_proc += 1
        print(f"\n{base}: DIFFERENT procedures for different parts")
        for v in variants:
            name = v.get('name_english', '?')
            proc = v.get('instruction_sequence', [])
            print(f"  {name}: {proc}")

print(f"\n\nSummary:")
print(f"  Same procedure for all parts: {same_proc}")
print(f"  Different procedures for different parts: {diff_proc}")

# Now check fire degree
print("\n" + "="*70)
print("DO DIFFERENT PARTS HAVE SAME FIRE DEGREE?")
print("="*70)

same_fire = 0
diff_fire = 0

for base, variants in base_materials.items():
    if len(variants) < 2:
        continue

    fires = [v.get('fire_degree', 0) for v in variants]
    unique_fires = set(fires)

    if len(unique_fires) == 1:
        same_fire += 1
    else:
        diff_fire += 1
        print(f"\n{base}: DIFFERENT fire degrees for different parts")
        for v in variants:
            name = v.get('name_english', '?')
            fire = v.get('fire_degree', '?')
            print(f"  {name}: fire degree {fire}")

print(f"\n\nSummary:")
print(f"  Same fire degree for all parts: {same_fire}")
print(f"  Different fire degrees for different parts: {diff_fire}")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If different parts of SAME PLANT use:
  - SAME procedure → parts_used is RI (identification only)
  - DIFFERENT procedure → parts_used is PP (affects processing)

If different parts of SAME PLANT have:
  - SAME fire degree → preparation state doesn't affect heat tolerance
  - DIFFERENT fire degree → preparation state DOES affect processing
""")
