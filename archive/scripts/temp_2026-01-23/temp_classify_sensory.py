#!/usr/bin/env python3
"""
Classify Brunschwig recipes for sensory modality.

FINDING: Brunschwig's recipes use FIXED PROCEDURES (timing + fire degree)
rather than real-time sensory monitoring. Classification categories:

- NONE: No sensory input required in procedure
- INPUT_VISUAL: Material selection requires visual assessment (color, ripeness)
- INPUT_TACTILE: Material selection requires touch (temperature, texture)
- INPUT_OLFACTORY: Material selection requires smell

Note: Most recipes will be NONE because procedures are fixed.
Sensory descriptions in the TEXT (e.g., "the water is clear") are properties
of the output, not monitoring instructions for the operator.
"""

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load curated data
with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

# Classification rules based on manual review
def classify_sensory(recipe):
    """Classify a recipe's sensory requirements."""
    modalities = []

    # Check procedural steps
    steps = recipe.get('procedural_steps') or []
    step_texts = ' '.join([
        f"{s.get('german_text', '')} {s.get('notes', '')} {s.get('english_translation', '')}"
        for s in steps
    ]).lower()

    # Material class hints
    material = recipe.get('material_class', '').lower()
    name = recipe.get('name_german', '').lower()

    # INPUT_VISUAL indicators
    visual_indicators = [
        'schwartz farb',  # black colored
        'rot farb',       # red colored
        'gelb',           # yellow
        'weiss',          # white
        'weiß',           # white (ß)
        'grün',           # green
        'bleich',         # pale
        'zyttig',         # ripe
        'reiff',          # ripe
        'jung',           # young
        'alt',            # old (aged)
    ]

    for indicator in visual_indicators:
        if indicator in step_texts:
            if 'INPUT_VISUAL' not in modalities:
                modalities.append('INPUT_VISUAL')
            break

    # INPUT_TACTILE indicators (rare)
    tactile_indicators = [
        'weich',    # soft
        'hart',     # hard
        'warm',     # warm
        'kalt',     # cold
    ]

    for indicator in tactile_indicators:
        # Only if in procedural context, not in uses
        if indicator in step_texts and 'gefühl' in step_texts:
            if 'INPUT_TACTILE' not in modalities:
                modalities.append('INPUT_TACTILE')
            break

    # INPUT_OLFACTORY indicators (rare)
    olfactory_indicators = [
        'geruch',   # smell/odor
        'riech',    # smell (verb)
        'stinck',   # stink
        'duft',     # fragrance
    ]

    for indicator in olfactory_indicators:
        if indicator in step_texts:
            if 'INPUT_OLFACTORY' not in modalities:
                modalities.append('INPUT_OLFACTORY')
            break

    # If no modalities found, classify as NONE
    if not modalities:
        modalities = ['NONE']

    return modalities

# Classify all recipes
results = {}
modality_counts = {'NONE': 0, 'INPUT_VISUAL': 0, 'INPUT_TACTILE': 0, 'INPUT_OLFACTORY': 0}

for recipe in data['recipes']:
    rid = recipe['id']
    modalities = classify_sensory(recipe)
    results[rid] = modalities

    for m in modalities:
        modality_counts[m] += 1

    # Add to recipe
    recipe['sensory_modality'] = modalities

print("=== Sensory Classification Results ===\n")
print(f"Total recipes: {len(data['recipes'])}")
print("\nModality distribution:")
for m, count in sorted(modality_counts.items(), key=lambda x: -x[1]):
    pct = 100 * count / len(data['recipes'])
    print(f"  {m}: {count} ({pct:.1f}%)")

# Show recipes with non-NONE modalities
print("\n\n=== Recipes with sensory input requirements ===\n")
for recipe in data['recipes']:
    if recipe['sensory_modality'] != ['NONE']:
        print(f"{recipe['id']}. {recipe['name_german']} ({recipe['name_english']})")
        print(f"   Modalities: {recipe['sensory_modality']}")
        if recipe.get('procedural_steps'):
            for s in recipe['procedural_steps'][:2]:  # First 2 steps
                print(f"   Step {s['step']}: {s.get('german_text', '')[:60]}...")
        print()

# Update notes
data['notes'] = data.get('notes', '') + ' | Sensory modality classified (temp_classify_sensory.py)'

# Save updated data
output_path = 'data/brunschwig_curated_v3.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_path}")
