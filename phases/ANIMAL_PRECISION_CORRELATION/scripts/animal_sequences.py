#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
d = json.load(open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', encoding='utf-8'))

animals = [m for m in d['materials'] if m.get('material_source') == 'animal']

print("Animal instruction sequences:")
print()
for a in animals:
    name = a['name_normalized']
    seq = a.get('instruction_sequence', [])
    print(f"{name}: {seq}")
