#!/usr/bin/env python3
"""
Enhanced Reverse Brunschwig Test using curated v2 data.

Key insight: brunschwig_curated_v2.json has discrete procedural actions:
GATHER, STRIP, BREAK, BORE, CHOP, POUND, PLUCK, WASH, DISTILL, COLLECT, STEEP

Question: Do materials with similar procedural steps share PP MIDDLEs?
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load curated Brunschwig data
with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    brunschwig = json.load(f)

recipes = brunschwig['recipes']
action_taxonomy = brunschwig['action_taxonomy']

print("="*60)
print("BRUNSCHWIG CURATED V2 - PROCEDURAL ANALYSIS")
print("="*60)

print(f"\nTotal recipes: {len(recipes)}")
print(f"\nAction taxonomy:")
for action, desc in action_taxonomy.items():
    print(f"  {action}: {desc}")

# Count action frequencies
action_counts = Counter()
recipes_with_procedures = 0
for r in recipes:
    steps = r.get('procedural_steps') or []
    if steps:
        recipes_with_procedures += 1
        for step in steps:
            action_counts[step.get('action', 'UNKNOWN')] += 1

print(f"\nRecipes with procedures: {recipes_with_procedures}/{len(recipes)}")
print(f"\nAction frequencies:")
for action, cnt in action_counts.most_common():
    print(f"  {action}: {cnt}")

# ============================================================
# Group recipes by action PROFILE (set of actions used)
# ============================================================
print("\n" + "="*60)
print("RECIPES BY ACTION PROFILE")
print("="*60)

recipe_profiles = defaultdict(list)
for r in recipes:
    steps = r.get('procedural_steps') or []
    if steps:
        actions = frozenset(step.get('action') for step in steps)
        recipe_profiles[actions].append(r)

print(f"\nUnique action profiles: {len(recipe_profiles)}")
print("\nProfiles with 2+ recipes:")
for profile, recs in sorted(recipe_profiles.items(), key=lambda x: -len(x[1])):
    if len(recs) >= 2:
        names = [r['name_english'] for r in recs[:5]]
        fire_degrees = [r.get('fire_degree') for r in recs]
        mat_classes = Counter(r.get('material_class') for r in recs)
        print(f"\n  {set(profile)} ({len(recs)} recipes):")
        print(f"    Fire degrees: {Counter(fire_degrees)}")
        print(f"    Material classes: {dict(mat_classes.most_common(3))}")
        print(f"    Examples: {names}")

# ============================================================
# Specific action combinations
# ============================================================
print("\n" + "="*60)
print("SPECIFIC ACTION ANALYSIS")
print("="*60)

# Which recipes require CHOP?
chop_recipes = [r for r in recipes if any(
    s.get('action') == 'CHOP' for s in (r.get('procedural_steps') or [])
)]
print(f"\nRecipes requiring CHOP ({len(chop_recipes)}):")
for r in chop_recipes[:8]:
    print(f"  {r['name_english']} (fire={r.get('fire_degree')}, class={r.get('material_class')})")

# Which recipes require POUND?
pound_recipes = [r for r in recipes if any(
    s.get('action') == 'POUND' for s in (r.get('procedural_steps') or [])
)]
print(f"\nRecipes requiring POUND ({len(pound_recipes)}):")
for r in pound_recipes[:8]:
    print(f"  {r['name_english']} (fire={r.get('fire_degree')}, class={r.get('material_class')})")

# Which have WASH step?
wash_recipes = [r for r in recipes if any(
    s.get('action') == 'WASH' for s in (r.get('procedural_steps') or [])
)]
print(f"\nRecipes requiring WASH ({len(wash_recipes)}):")
for r in wash_recipes:
    print(f"  {r['name_english']} (fire={r.get('fire_degree')}, class={r.get('material_class')})")

# Which have PLUCK step? (animal specific)
pluck_recipes = [r for r in recipes if any(
    s.get('action') == 'PLUCK' for s in (r.get('procedural_steps') or [])
)]
print(f"\nRecipes requiring PLUCK ({len(pluck_recipes)}):")
for r in pluck_recipes:
    print(f"  {r['name_english']} (fire={r.get('fire_degree')}, class={r.get('material_class')})")

# ============================================================
# Parts used analysis
# ============================================================
print("\n" + "="*60)
print("PARTS USED ANALYSIS")
print("="*60)

parts_counter = Counter()
for r in recipes:
    parts = r.get('parts_used') or []
    for part in parts:
        # Normalize part names
        part_lower = part.lower()
        if 'root' in part_lower:
            parts_counter['ROOT'] += 1
        elif 'leaf' in part_lower or 'leaves' in part_lower:
            parts_counter['LEAF'] += 1
        elif 'flower' in part_lower:
            parts_counter['FLOWER'] += 1
        elif 'seed' in part_lower:
            parts_counter['SEED'] += 1
        elif 'stem' in part_lower or 'stalk' in part_lower:
            parts_counter['STEM'] += 1
        elif 'berry' in part_lower or 'berries' in part_lower:
            parts_counter['BERRY'] += 1
        elif 'bark' in part_lower:
            parts_counter['BARK'] += 1
        elif 'sap' in part_lower or 'juice' in part_lower:
            parts_counter['SAP/JUICE'] += 1
        elif 'herb' in part_lower or 'krut' in part_lower:
            parts_counter['WHOLE_HERB'] += 1
        else:
            parts_counter['OTHER'] += 1

print("\nPlant parts frequency:")
for part, cnt in parts_counter.most_common():
    print(f"  {part}: {cnt}")

# ============================================================
# Property dimensions that could map to PP
# ============================================================
print("\n" + "="*60)
print("POTENTIAL PP PROPERTY DIMENSIONS")
print("="*60)

print("""
Based on Brunschwig analysis, materials differ in:

1. FIRE DEGREE (1-4)
   - 1: Gentle (fruits, delicate flowers)
   - 2: Standard (most herbs)
   - 3: Moderate-hot (some herbs)
   - 4: Strong (animals, tough materials)

2. PREPARATION REQUIRED
   - None (soft materials, direct distill)
   - CHOP (fibrous herbs)
   - POUND (hard materials like roots)
   - STRIP (separating parts)

3. PARTS USED
   - Whole herb
   - Root only
   - Flower only
   - Combination (root + herb)

4. SPECIAL HANDLING
   - WASH required (dirty/contaminated)
   - PLUCK required (animals with feathers)
   - BORE required (sap extraction)

5. MATERIAL SOURCE
   - Herb
   - Flower
   - Animal
   - Tree product
   - Mineral

If PP encodes these dimensions, we'd expect:
- ~5-8 coarse categories
- High overlap (most materials share some properties)
- Rare PP for specialized handling
""")

# ============================================================
# How many unique property combinations exist?
# ============================================================
print("\n" + "="*60)
print("PROPERTY COMBINATION SPACE")
print("="*60)

property_combos = Counter()
for r in recipes:
    fire = r.get('fire_degree', 0)
    mat_class = r.get('material_class', 'unknown')

    steps = r.get('procedural_steps') or []
    actions = frozenset(s.get('action') for s in steps) if steps else frozenset()

    has_chop = 'CHOP' in actions
    has_pound = 'POUND' in actions
    has_wash = 'WASH' in actions

    parts = r.get('parts_used') or []
    has_root = any('root' in p.lower() for p in parts)
    has_flower = any('flower' in p.lower() for p in parts)

    combo = (fire, has_chop, has_pound, has_root)
    property_combos[combo] += 1

print(f"Unique (fire, chop, pound, root) combos: {len(property_combos)}")
print("\nMost common combos:")
for combo, cnt in property_combos.most_common(15):
    fire, chop, pound, root = combo
    print(f"  fire={fire}, chop={chop}, pound={pound}, root={root}: {cnt} recipes")
