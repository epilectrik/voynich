#!/usr/bin/env python3
"""Check nettle (nessel) as a non-animal REGIME_4 candidate."""

import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("SEARCHING FOR NETTLE (nessel) AND OTHER REGIME_4 NON-ANIMALS")
print("=" * 70)
print()

# Find all REGIME_4 materials
regime4_materials = []
for m in data['materials']:
    regime = m.get('regime_assignment', {})
    if regime.get('final_regime') == 'REGIME_4':
        regime4_materials.append({
            'name': m.get('name_normalized'),
            'class': m.get('material_source'),
            'fire': m.get('fire_degree'),
            'override': regime.get('override_reason'),
            'precision': regime.get('precision_requirement'),
            'pp_profile': regime.get('predicted_prefix_profile', {}),
            'instr': m.get('instruction_sequence', [])
        })

print(f"Total REGIME_4 materials: {len(regime4_materials)}")
print()

# Group by class
from collections import defaultdict
by_class = defaultdict(list)
for m in regime4_materials:
    by_class[m['class']].append(m)

for cls, materials in sorted(by_class.items()):
    print(f"{cls.upper()}: {len(materials)}")
    for m in materials:
        print(f"  {m['name']}: fire={m['fire']}, override={m['override']}")
        print(f"    Precision: {m['precision']}")
        print(f"    PP: {m['pp_profile']}")
        if m['instr']:
            print(f"    Instructions: {m['instr']}")
    print()

# Find non-animal REGIME_4
non_animal_r4 = [m for m in regime4_materials if m['class'] != 'animal']
print("=" * 70)
print(f"NON-ANIMAL REGIME_4 MATERIALS: {len(non_animal_r4)}")
print("=" * 70)
print()

for m in non_animal_r4:
    print(f"{m['name']} ({m['class']}):")
    print(f"  Fire degree: {m['fire']}")
    print(f"  Override reason: {m['override']}")
    print(f"  Precision requirement: {m['precision']}")
    print(f"  PP profile: {m['pp_profile']}")
    print(f"  Instructions: {m['instr']}")
    print()
