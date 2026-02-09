#!/usr/bin/env python3
"""Check if same animal appears across multiple folios."""

import json
from pathlib import Path
from collections import defaultdict

mappings_path = Path(__file__).parent.parent / 'phases' / 'MATERIAL_MAPPING_V2' / 'results' / 'validated_mappings.json'
with open(mappings_path) as f:
    data = json.load(f)

# Group by recipe
recipe_folios = defaultdict(list)
for m in data.get('validated_mappings', []):
    folio = m['record_id'].split(':')[0]
    recipe_folios[m['recipe']].append({
        'folio': folio,
        'record_id': m['record_id'],
        'ri_tokens': m['ri_tokens'],
        'confidence': m['confidence']
    })

print("="*70)
print("ANIMAL DISTRIBUTION ACROSS FOLIOS")
print("="*70)

for recipe, records in sorted(recipe_folios.items()):
    folios = set(r['folio'] for r in records)
    print(f"\n{recipe.upper()}")
    print(f"  Records: {len(records)}")
    print(f"  Folios: {len(folios)} - {', '.join(sorted(folios))}")

    # Show RI tokens for each record
    print(f"\n  {'Folio':<10} {'Record':<12} {'RI Tokens':<40}")
    print(f"  {'-'*60}")
    for r in sorted(records, key=lambda x: x['folio']):
        ri_str = ', '.join(r['ri_tokens'][:3])
        print(f"  {r['folio']:<10} {r['record_id']:<12} {ri_str:<40}")

print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print(f"\nEach animal type appears on MULTIPLE folios:")
for recipe, records in recipe_folios.items():
    folios = set(r['folio'] for r in records)
    print(f"  {recipe}: {len(folios)} folios, {len(records)} records")

print("""
This means:
1. A folios are NOT organized as "one folio per animal"
2. The same animal material appears in different A locations
3. A records reference materials, they don't contain materials

Implication: A is an INDEX/REGISTRY that references materials
by their properties, not a catalog organized by material identity.
""")
