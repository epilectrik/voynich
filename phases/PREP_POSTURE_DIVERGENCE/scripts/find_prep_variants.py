"""Find materials with different prep states in Brunschwig data."""
import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

with open(PROJECT_ROOT / 'data' / 'brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group by base material name
materials_by_base = defaultdict(list)

for r in data['recipes']:
    name = r.get('name_english', '').lower()
    steps = r.get('procedural_steps') or []
    fire = r.get('fire_degree', 0)

    # Extract prep verbs from steps
    prep_verbs = []
    for step in steps:
        action = step.get('action', '')
        if action:
            prep_verbs.append(action)

    materials_by_base[name].append({
        'id': r['id'],
        'name_german': r.get('name_german', ''),
        'preps': prep_verbs,
        'fire_degree': fire,
        'material_source': r.get('material_source', ''),
    })

print('=' * 70)
print('MATERIALS WITH VARIED PREP PATTERNS')
print('=' * 70)

# Find materials where same base has different prep sequences
varied_materials = []
for name, entries in materials_by_base.items():
    if len(entries) > 1:
        all_preps = [tuple(e['preps']) for e in entries]
        unique_preps = set(all_preps)
        if len(unique_preps) > 1:
            varied_materials.append((name, entries, unique_preps))

print(f"\nFound {len(varied_materials)} materials with different prep patterns:\n")

for name, entries, unique_preps in sorted(varied_materials, key=lambda x: -len(x[1])):
    print(f"\n{name.upper()} ({len(entries)} entries, {len(unique_preps)} unique prep patterns):")
    for e in entries:
        prep_str = ' -> '.join(e['preps']) if e['preps'] else '[none]'
        print(f"  #{e['id']:3d} fire={e['fire_degree']} | {prep_str}")

# Also look for materials with complex prep sequences (multiple steps)
print("\n" + "=" * 70)
print("MATERIALS WITH MULTI-STEP PREP (potential prep state encoding)")
print("=" * 70)

multi_step = []
for name, entries in materials_by_base.items():
    for e in entries:
        if len(e['preps']) >= 3:
            multi_step.append((name, e))

print(f"\nFound {len(multi_step)} recipes with 3+ prep steps:\n")
for name, e in sorted(multi_step, key=lambda x: -len(x[1]['preps']))[:20]:
    prep_str = ' -> '.join(e['preps'])
    print(f"#{e['id']:3d} {name}: fire={e['fire_degree']} | {prep_str}")

# Look for explicit fresh/dried/chopped distinctions
print("\n" + "=" * 70)
print("EXPLICIT PREP STATE KEYWORDS IN NAMES")
print("=" * 70)

prep_keywords = ['fresh', 'dried', 'dry', 'chopped', 'ground', 'whole', 'crushed', 'powdered', 'juice', 'oil']
for kw in prep_keywords:
    matches = [name for name in materials_by_base.keys() if kw in name]
    if matches:
        print(f"\n'{kw}' in name: {matches}")
