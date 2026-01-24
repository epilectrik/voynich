#!/usr/bin/env python3
"""
Can we specifically identify thyme (quuendel)?

Problem: Thyme shares REGIME_4 with:
- 9 animals (chicken, frog, blood, milk, etc.)
- 8 other precision-override herbs (nettle, clissen, wurg, etc.)

What distinguishes thyme from the others?
"""

import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load Brunschwig data
with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("REGIME_4 MATERIALS - What distinguishes thyme?")
print("=" * 70)
print()

# Find all REGIME_4 materials
regime4 = []
for m in data['materials']:
    regime = m.get('regime_assignment', {})
    if regime.get('final_regime') == 'REGIME_4':
        regime4.append({
            'name': m.get('name_normalized'),
            'class': m.get('material_source'),
            'fire': m.get('fire_degree'),
            'instr': m.get('instruction_sequence', []),
            'pp': regime.get('predicted_prefix_profile', {})
        })

# Group by instruction sequence
from collections import defaultdict
by_instr = defaultdict(list)
for m in regime4:
    key = ' -> '.join(m['instr']) if m['instr'] else 'NO_SEQUENCE'
    by_instr[key].append(m)

print("Grouped by INSTRUCTION SEQUENCE:")
print("-" * 70)
for seq, materials in sorted(by_instr.items()):
    names = [m['name'] for m in materials]
    classes = set(m['class'] for m in materials)
    print(f"{seq}")
    print(f"  Materials: {names}")
    print(f"  Classes: {classes}")
    print()

# Find thyme specifically
print("=" * 70)
print("THYME (quuendel/cuendel) SPECIFIC SIGNATURE")
print("=" * 70)
print()

for m in regime4:
    if 'uendel' in m['name']:
        print(f"{m['name']}:")
        print(f"  Class: {m['class']}")
        print(f"  Fire degree: {m['fire']}")
        print(f"  Instruction sequence: {m['instr']}")
        print(f"  PP profile: {m['pp']}")
        print()

# What other materials share thyme's instruction sequence?
thyme_seq = None
for m in regime4:
    if 'uendel' in m['name']:
        thyme_seq = ' -> '.join(m['instr'])
        break

if thyme_seq:
    print(f"Materials sharing thyme's sequence ({thyme_seq}):")
    for m in by_instr[thyme_seq]:
        print(f"  {m['name']} ({m['class']})")

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()
print("To identify THYME specifically, we need constraints that distinguish it from:")
print()

# Count what thyme competes with
thyme_competitors = by_instr.get(thyme_seq, []) if thyme_seq else []
print(f"  - {len(thyme_competitors)} materials with same instruction sequence")

same_regime = [m for m in regime4 if m['class'] != 'animal']
print(f"  - {len(same_regime)} non-animal REGIME_4 materials total")

all_regime4 = len(regime4)
print(f"  - {all_regime4} total REGIME_4 materials (including animals)")

print()
print("Current method narrows to: 'precision herb in REGIME_4'")
print("But CANNOT distinguish between the 9 precision-override herbs")
print()
print("Would need additional constraints:")
print("  - Folio section (if thyme appears in specific manuscript section)")
print("  - Co-occurrence patterns (what other tokens appear with thyme)")
print("  - Line position patterns")
print("  - Or external evidence (illustration identification)")
