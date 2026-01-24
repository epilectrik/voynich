#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze recipes 201-225 for sensory monitoring instructions.

Sensory categories:
- SIGHT: color changes, clarity, visual cues ("bis es klar wird", "farb")
- SMELL: odor assessment ("geruch", "riech")
- SOUND: bubbling, boiling sounds ("sieden", "wallen")
- TOUCH: temperature, texture ("warm", "kalt", "weich")
- TASTE: flavor testing ("schmeck", "prob")
- NONE: No sensory monitoring required

Conservative approach: Only mark a modality if there's an EXPLICIT instruction
requiring sensory assessment during the procedure.
"""

import json
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Load recipes
with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load German source text
with open('sources/brunschwig_1500_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

recipes = [r for r in data['recipes'] if 201 <= r['id'] <= 225]

# Recipe line ranges (from extraction)
recipe_ranges = {
    201: (18768, 18776),  # sloe blossom water - no procedure
    202: (18779, 18801),  # barberry water
    203: (18803, 18943),  # spikenard water
    204: (18946, 18986),  # savin water
    205: (18989, 19027),  # mustard herb water
    206: (19033, 19120),  # pellitory-of-the-wall water
    207: (19131, 19217),  # asparagus water
    208: (19229, 19254),  # spindle tree water
    209: (19260, 19297),  # caper spurge water
    210: (19304, 19353),  # oregano water
    211: (19356, 19410),  # tormentil water - no procedure
    212: (19412, 19426),  # dodder water - no procedure
    213: (19429, 19459),  # grape marc water
    214: (19462, 19516),  # tamarisk water
    215: (19525, 19784),  # wormwood water
    216: (19787, 19869),  # comfrey water
    217: (19879, 19947),  # willow leaf water
    218: (19949, 19979),  # willow blossom water - no procedure
    219: (19996, 20054),  # hemlock water
    220: (20057, 20152),  # bindweed water
    221: (20186, 20270),  # chicory water
    222: (20273, 20305),  # chicory flower water
    223: (20308, 20368),  # mullein water
    224: (20390, 20535),  # knotgrass water
    225: (20538, 20601),  # solomon's seal water
}

print("=" * 80)
print("SENSORY MONITORING ANALYSIS - Recipes 201-225")
print("=" * 80)

results = {}

for recipe in recipes:
    rid = recipe['id']
    name = recipe.get('name_english', 'N/A')
    has_proc = recipe.get('has_procedure', False)

    start, end = recipe_ranges.get(rid, (0, 0))
    german_text = ''.join(lines[start-1:end]) if start > 0 else ""

    print(f"\n--- Recipe {rid}: {name} ---")
    print(f"Has procedure: {has_proc}")

    if recipe.get('procedural_steps'):
        print("Procedural steps:")
        for step in recipe['procedural_steps']:
            action = step['action']
            german = step.get('german_text', 'N/A')
            print(f"  {step['step']}. {action}: {german}")

    sensory_found = []

    # SIGHT keywords (color, clarity) - for procedural assessment
    sight_keywords = ['farb', 'clar', 'klar', 'heiter', 'trieb', 'luter', 'rot', 'bleich', 'siehst']

    # SMELL keywords
    smell_keywords = ['geruch', 'riech']

    # SOUND keywords (boiling, bubbling)
    sound_keywords = ['sieden', 'sied', 'wallen', 'brodeln']

    # TOUCH keywords (temperature, texture) - for procedural assessment
    touch_keywords = ['warm', 'weich', 'hart']

    # TASTE keywords
    taste_keywords = ['schmeck', 'kost', 'prob']

    german_lower = german_text.lower()

    # Check each category
    for kw in sight_keywords:
        if kw.lower() in german_lower:
            if 'SIGHT' not in sensory_found:
                sensory_found.append('SIGHT')
            print(f"  Found sight keyword: {kw}")
            break

    for kw in smell_keywords:
        if kw.lower() in german_lower:
            if 'SMELL' not in sensory_found:
                sensory_found.append('SMELL')
            print(f"  Found smell keyword: {kw}")
            break

    for kw in sound_keywords:
        if kw.lower() in german_lower:
            if 'SOUND' not in sensory_found:
                sensory_found.append('SOUND')
            print(f"  Found sound keyword: {kw}")
            break

    for kw in touch_keywords:
        if kw.lower() in german_lower:
            if 'TOUCH' not in sensory_found:
                sensory_found.append('TOUCH')
            print(f"  Found touch keyword: {kw}")
            break

    for kw in taste_keywords:
        if kw.lower() in german_lower:
            if 'TASTE' not in sensory_found:
                sensory_found.append('TASTE')
            print(f"  Found taste keyword: {kw}")
            break

    if not sensory_found:
        sensory_found = ['NONE']

    results[str(rid)] = sensory_found
    print(f"  => Sensory categories: {sensory_found}")

print("\n" + "=" * 80)
print("FINAL JSON OUTPUT")
print("=" * 80)
print(json.dumps(results, indent=2))
