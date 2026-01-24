#!/usr/bin/env python3
"""Check late entries with balneum for fire degree verification."""

import json

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

print("ENTRIES WITH BALNEUM (ID > 100):")
print("-" * 60)
for r in data['recipes']:
    if r['id'] > 100 and r.get('method') and 'balneum' in r.get('method', '').lower():
        print(f"ID {r['id']}: fire={r.get('fire_degree')}, method={r.get('method')[:40]}, lines={r.get('source_lines')}")

print("\n\nENTRIES WITH PER ALEMBICUM (ID > 150):")
print("-" * 60)
for r in data['recipes']:
    if r['id'] > 150 and r.get('method') and 'alembic' in r.get('method', '').lower():
        print(f"ID {r['id']}: fire={r.get('fire_degree')}, method={r.get('method')[:40]}, lines={r.get('source_lines')}")

print("\n\nFIRE DEGREE 1 ENTRIES (ID > 150) - should be gentle methods:")
print("-" * 60)
for r in data['recipes']:
    if r['id'] > 150 and r.get('fire_degree') == 1:
        print(f"ID {r['id']}: {r.get('name_english', '')[:30]}, method={r.get('method', 'none')[:30]}, material={r.get('material_class')}")
