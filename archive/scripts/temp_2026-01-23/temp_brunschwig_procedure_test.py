#!/usr/bin/env python3
"""
Test: Does Brunschwig procedure type correlate with PP atoms?
Does material identity correlate with RI extensions?
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load Brunschwig
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

print("="*70)
print("BRUNSCHWIG PROCEDURE TYPE ANALYSIS")
print("="*70)

# Extract actual procedure types from instruction_sequence
procedure_patterns = defaultdict(list)

for recipe in recipes:
    instr_seq = recipe.get('instruction_sequence')
    if not instr_seq:
        continue

    # Create procedure signature
    proc_sig = tuple(instr_seq)
    procedure_patterns[proc_sig].append(recipe)

print(f"\nUnique procedure patterns: {len(procedure_patterns)}")

print("\nMost common procedure patterns:")
for proc, recs in sorted(procedure_patterns.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"  {proc}: {len(recs)} recipes")
    # Show example materials
    materials = [r.get('name_english', '?') for r in recs[:3]]
    print(f"    Examples: {', '.join(materials)}")

# Group by procedure complexity
print("\n" + "="*70)
print("PROCEDURE COMPLEXITY GROUPS")
print("="*70)

simple_procs = []  # 1-2 steps
medium_procs = []  # 3-4 steps
complex_procs = []  # 5+ steps

for recipe in recipes:
    instr_seq = recipe.get('instruction_sequence') or []
    if len(instr_seq) <= 2:
        simple_procs.append(recipe)
    elif len(instr_seq) <= 4:
        medium_procs.append(recipe)
    else:
        complex_procs.append(recipe)

print(f"\nSimple (1-2 steps): {len(simple_procs)} recipes")
print(f"Medium (3-4 steps): {len(medium_procs)} recipes")
print(f"Complex (5+ steps): {len(complex_procs)} recipes")

# What instructions appear in each?
def get_instr_dist(recipes):
    instrs = []
    for r in recipes:
        instrs.extend(r.get('instruction_sequence') or [])
    return Counter(instrs)

print("\nInstruction distribution by complexity:")

for name, group in [("Simple", simple_procs), ("Medium", medium_procs), ("Complex", complex_procs)]:
    if not group:
        continue
    dist = get_instr_dist(group)
    print(f"\n{name}:")
    for instr, count in dist.most_common(5):
        print(f"  {instr}: {count}")

# Key question: Do different procedure types have different material classes?
print("\n" + "="*70)
print("PROCEDURE TYPE vs MATERIAL CLASS")
print("="*70)

# Group by first instruction (main procedure type)
first_instr_groups = defaultdict(list)
for recipe in recipes:
    instr_seq = recipe.get('instruction_sequence') or []
    if instr_seq:
        first_instr_groups[instr_seq[0]].append(recipe)

print("\nMaterial class distribution by procedure type:")

for instr, recs in sorted(first_instr_groups.items(), key=lambda x: -len(x[1])):
    if len(recs) < 5:
        continue
    mc_dist = Counter(r.get('material_class', 'unknown') for r in recs)
    print(f"\n{instr} ({len(recs)} recipes):")
    for mc, count in mc_dist.most_common(5):
        print(f"  {mc}: {count}")

# The mapping insight
print("\n" + "="*70)
print("BRUNSCHWIG -> VOYNICH MAPPING HYPOTHESIS")
print("="*70)
print("""
If PP = procedure type and RI = material identity, then:

1. Brunschwig INSTRUCTION TYPE should map to PP atoms:
   - AUX (preparation) -> one set of PP
   - e_ESCAPE (collection) -> another set of PP
   - k_ENERGY (heating) -> another set of PP
   - LINK (monitoring) -> another set of PP

2. Brunschwig MATERIAL should map to RI extensions:
   - All roses share PP (same procedures)
   - Each rose variety has different RI extension

3. The PRODUCT TYPE mapping we already have:
   - WATER_STANDARD -> PP 'e' (standard processing)
   - PRECISION -> PP 'ol' (special handling)

   This works because product type IS a proxy for procedure type:
   - Standard water = standard procedures
   - Precision = special procedures

4. What we should test next:
   - Do materials with same Brunschwig procedure share PP?
   - Do materials with different names but same procedure differ only in RI?
""")

# Count materials that share procedures
print("\n" + "="*70)
print("MATERIALS SHARING PROCEDURES")
print("="*70)

# Find groups of different materials with identical procedures
proc_to_materials = defaultdict(list)
for recipe in recipes:
    instr_seq = recipe.get('instruction_sequence')
    if instr_seq:
        proc_to_materials[tuple(instr_seq)].append(recipe.get('name_english', '?'))

print("\nMaterials sharing identical procedure sequences:")
for proc, materials in sorted(proc_to_materials.items(), key=lambda x: -len(x[1])):
    if len(materials) >= 3:
        print(f"\n{proc}:")
        print(f"  Materials: {', '.join(materials[:10])}")
        if len(materials) > 10:
            print(f"  ... and {len(materials)-10} more")

print("\n" + "-"*70)
print("KEY INSIGHT:")
print("-"*70)
print("""
Many different materials share IDENTICAL procedures.
E.g., ('AUX', 'e_ESCAPE') is used for 127 different materials.

Under the PP/RI model:
- These 127 materials should share the SAME PP atoms (same procedures)
- But have DIFFERENT RI extensions (different identities)

This is testable:
- Map Brunschwig procedure groups to Voynich folios
- Check if PP is consistent within procedure group
- Check if RI varies within procedure group
""")
