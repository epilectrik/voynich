#!/usr/bin/env python3
import json

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    d = json.load(f)

r = [x for x in d['recipes'] if x['id'] == 177][0]
print(f"ID 177: {r['name_german']}")
print(f"English: {r.get('name_english')}")
print(f"Fire degree: {r.get('fire_degree')}")
print(f"Method: {r.get('method')}")
print(f"Material class: {r.get('material_class')}")
print(f"Source lines: {r.get('source_lines')}")

# Also check ID 232 (white lily - fire=1) and 233 (white lily root - fire=3)
for rid in [232, 233]:
    r = [x for x in d['recipes'] if x['id'] == rid][0]
    print(f"\nID {rid}: {r.get('name_english')}")
    print(f"  Fire degree: {r.get('fire_degree')}")
    print(f"  Material class: {r.get('material_class')}")
    print(f"  Source lines: {r.get('source_lines')}")
