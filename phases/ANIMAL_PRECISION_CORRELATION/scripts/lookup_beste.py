#!/usr/bin/env python3
"""Look up beste material details."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for m in data['materials']:
    name = m.get('name_normalized', '')
    if 'beste' in name.lower() or 'besser' in name.lower() or 'ish' in name.lower() or 'kyrsen' in name.lower():
        print("=" * 60)
        print(f"Name: {m.get('name_normalized')}")
        print(f"Original: {m.get('name_original')}")
        print(f"Class: {m.get('material_source')}")
        print(f"Fire degree: {m.get('fire_degree')}")
        print(f"Regime: {m.get('regime_assignment', {}).get('final_regime')}")
        print(f"Instructions: {m.get('instruction_sequence')}")
        if m.get('notes'):
            print(f"Notes: {m.get('notes')[:500]}")
        if m.get('recipe_text'):
            print(f"Recipe: {m.get('recipe_text')[:500]}")
        print()
