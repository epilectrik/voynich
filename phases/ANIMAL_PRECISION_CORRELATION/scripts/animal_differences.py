#!/usr/bin/env python3
"""Check what distinguishes different animal recipes"""
import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
d = json.load(open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', encoding='utf-8'))

animals = [m for m in d['materials'] if m.get('material_source') == 'animal']

print("=" * 70)
print("ANIMAL RECIPE DIFFERENCES")
print("=" * 70)
print()

for a in animals:
    name = a['name_normalized']
    steps = a.get('procedural_steps', [])
    uses = a.get('uses_count', 0)
    seq = a.get('instruction_sequence', [])
    text_len = a.get('entry_text_length', 0)

    print(f"{name}:")
    print(f"  Steps: {len(steps)}")
    print(f"  Uses: {uses}")
    print(f"  Instruction sequence: {seq}")
    print(f"  Text length: {text_len}")

    # Look at actual step content
    if steps:
        for s in steps[:2]:
            txt = s.get('brunschwig_text', '')[:60]
            # Remove non-ASCII for printing
            txt = txt.encode('ascii', 'replace').decode('ascii')
            iclass = s.get('instruction_class', 'UNK')
            hazard = s.get('hazard_exposure', 'NONE')
            print(f"    Step: {iclass}/{hazard} - '{txt}...'")
    print()
