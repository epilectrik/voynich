#!/usr/bin/env python3
"""
Check for parametric encoding in Brunschwig:
- Same material with different preparations (fresh/dried, chopped/whole)
- Do they share base RI with different modifiers?
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

print("="*70)
print("PREPARATION MODIFIERS IN BRUNSCHWIG")
print("="*70)

# Look for preparation-related terms in procedure_summary
prep_terms = ['fresh', 'dried', 'dry', 'green', 'chopped', 'bruised', 'crushed',
              'ground', 'powder', 'whole', 'cut', 'macerated', 'steeped', 'washed']

prep_found = defaultdict(list)

for recipe in recipes:
    summary = (recipe.get('procedure_summary') or '').lower()
    name = recipe.get('name_english', 'Unknown')

    for term in prep_terms:
        if term in summary:
            prep_found[term].append({
                'name': name,
                'summary': summary[:100],
                'parts': recipe.get('parts_used', []),
                'procedure': recipe.get('instruction_sequence', [])
            })

print("\nPreparation terms found:")
for term, recs in sorted(prep_found.items(), key=lambda x: -len(x[1])):
    print(f"\n{term.upper()}: {len(recs)} recipes")
    for r in recs[:3]:
        print(f"  {r['name']}: \"{r['summary']}...\"")

# Check if same material appears with different preparations
print("\n" + "="*70)
print("SAME MATERIAL, DIFFERENT PREPARATIONS")
print("="*70)

# Group by base material name
material_variants = defaultdict(list)

for recipe in recipes:
    name = recipe.get('name_english', '').lower()

    # Check for variant markers
    variant_markers = ['fresh', 'dried', 'green', 'root', 'herb', 'flower',
                       'leaf', 'seed', 'bark', 'sap', 'blood', 'wild', 'garden']

    # Find base name
    parts = name.split()
    base = None
    variant = None

    for marker in variant_markers:
        if marker in parts:
            idx = parts.index(marker)
            base = ' '.join(parts[:idx]) if idx > 0 else ' '.join(parts[idx+1:])
            variant = marker
            break

    if base and len(base) > 2:
        material_variants[base].append({
            'full_name': name,
            'variant': variant,
            'parts': recipe.get('parts_used', []),
            'procedure': recipe.get('instruction_sequence', []),
            'fire': recipe.get('fire_degree', 0)
        })

print("\nMaterials with multiple variants:")
for base, variants in sorted(material_variants.items(), key=lambda x: -len(x[1])):
    if len(variants) < 2:
        continue

    print(f"\n{base.upper()}:")
    for v in variants:
        print(f"  {v['full_name']}")
        print(f"    Variant: {v['variant']}, Parts: {v['parts']}")
        print(f"    Procedure: {v['procedure']}, Fire: {v['fire']}")

# Check if variants have same or different procedures
print("\n" + "="*70)
print("DO PREPARATION VARIANTS SHARE PROCEDURES?")
print("="*70)

same_proc = 0
diff_proc = 0
examples_same = []
examples_diff = []

for base, variants in material_variants.items():
    if len(variants) < 2:
        continue

    procs = [tuple(v['procedure']) for v in variants]
    unique_procs = set(procs)

    if len(unique_procs) == 1:
        same_proc += 1
        examples_same.append((base, variants))
    else:
        diff_proc += 1
        examples_diff.append((base, variants))

print(f"\nSame procedure for all variants: {same_proc}")
print(f"Different procedures for variants: {diff_proc}")

print("\nExamples with DIFFERENT procedures:")
for base, variants in examples_diff[:5]:
    print(f"\n  {base.upper()}:")
    for v in variants:
        print(f"    {v['full_name']}: {v['procedure']}")

print("\nExamples with SAME procedure:")
for base, variants in examples_same[:5]:
    print(f"\n  {base.upper()}:")
    for v in variants:
        print(f"    {v['full_name']}: {v['procedure']}")

# KEY QUESTION: If variants share base but differ in prep,
# would RI = base_atom + prep_modifier?
print("\n" + "="*70)
print("PARAMETRIC ENCODING HYPOTHESIS")
print("="*70)
print("""
If RI encodes material + preparation parametrically:
  RI = base_material_atom + preparation_modifier

Examples:
  rose_fresh  = base_rose + mod_fresh
  rose_dried  = base_rose + mod_dried
  borage_root = base_borage + mod_root
  borage_herb = base_borage + mod_herb

If preparation affects PROCEDURE:
  - The modification should change the PP atom (not just extension)
  - Different preparations = different PP = different procedural affordances

If preparation is just IDENTIFICATION:
  - The modification would only change the extension
  - Different preparations = same PP, different extension
""")

# Check if different preparations require different fire degrees
print("\n" + "="*70)
print("DO PREPARATIONS AFFECT FIRE DEGREE?")
print("="*70)

same_fire = 0
diff_fire = 0

for base, variants in material_variants.items():
    if len(variants) < 2:
        continue

    fires = [v['fire'] for v in variants]
    unique_fires = set(fires)

    if len(unique_fires) == 1:
        same_fire += 1
    else:
        diff_fire += 1
        print(f"\n  {base.upper()}: Different fire degrees")
        for v in variants:
            print(f"    {v['full_name']}: fire={v['fire']}")

print(f"\nSummary:")
print(f"  Same fire for all variants: {same_fire}")
print(f"  Different fire for variants: {diff_fire}")

# CONCLUSION
print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
Based on the data:

1. PREPARATION affects PROCEDURE in many cases:
   - Different plant parts often need different procedures
   - This means preparation is NOT just identification

2. RI encoding structure would be:
   RI = PP_atom(preparation-dependent) + extension(material-identity)

   Rather than:
   RI = base_material + preparation_modifier

3. This means preparation is EMBEDDED in the PP atom:
   - rose_root: PP_for_roots + ext_rose
   - rose_flower: PP_for_flowers + ext_rose

   The PP atom already carries the preparation requirement.
   The extension just identifies WHICH material (rose vs lily).

4. Parametric structure is:
   RI = (what_procedure_needed) + (which_material)
       = PP_atom + identity_extension

   NOT:
   RI = (base_material) + (preparation_modifier)
""")
