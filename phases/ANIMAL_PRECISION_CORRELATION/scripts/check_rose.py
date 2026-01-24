#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

d = json.load(open('C:/git/voynich/data/brunschwig_materials_master.json', encoding='utf-8'))

for m in d['materials']:
    if m['name_normalized'] in ['rosen', 'rose']:
        print(f"=== {m['name_normalized']} ===")
        for k, v in m.items():
            print(f"  {k}: {str(v).encode('ascii', 'replace').decode()}")
        print()

# Also check how many materials have empty instruction sequences
empty_seq = [m['name_normalized'] for m in d['materials'] if not m.get('instruction_sequence')]
has_seq = [m['name_normalized'] for m in d['materials'] if m.get('instruction_sequence')]

print(f"\nMaterials WITH instruction sequences ({len(has_seq)}):")
print(f"  {has_seq[:20]}...")

print(f"\nMaterials WITHOUT instruction sequences ({len(empty_seq)}):")
print(f"  {empty_seq[:20]}...")
