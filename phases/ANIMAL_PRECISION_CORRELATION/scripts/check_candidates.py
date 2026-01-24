#!/usr/bin/env python3
"""Check details of unique sequence candidates."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find specific materials
targets = [164, 94, 62]  # White rose, Honey, Nettle

for r in data['recipes']:
    if r['id'] in targets:
        print("=" * 70)
        print(f"#{r['id']} {r['name_german']} ({r['name_english']})")
        print("=" * 70)
        print()
        print(f"Material class: {r.get('material_class')}")
        print(f"Fire degree: {r.get('fire_degree')}")
        print(f"Has procedure: {r.get('has_procedure')}")
        print(f"Instruction sequence: {r.get('instruction_sequence')}")
        print()
        print("Procedure summary:")
        print(r.get('procedure_summary', 'N/A'))
        print()
        print(f"Use count: {r.get('use_count', 0)}")
        print(f"Key uses: {r.get('key_uses', [])[:5]}")
        print()
