"""Find related materials that might show prep state variation."""
import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

with open(PROJECT_ROOT / 'data' / 'brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']

# Define material families (base materials with variants)
material_families = {
    'borage': ['borage'],
    'nettle': ['nettle', 'nessel'],
    'rose': ['rose', 'rosa'],
    'birch': ['birch'],
    'mint': ['mint'],
    'sage': ['sage', 'salvia'],
    'chicken': ['chicken', 'hen', 'capon', 'hennen'],
    'lavender': ['lavender'],
    'fennel': ['fennel'],
    'wormwood': ['wormwood', 'absinth'],
    'elder': ['elder'],
    'plantain': ['plantain'],
    'mugwort': ['mugwort', 'beifuss'],
    'celandine': ['celandine', 'chelidon'],
}

print("=" * 70)
print("MATERIAL FAMILY ANALYSIS")
print("=" * 70)

for family_name, keywords in material_families.items():
    matches = []
    for r in recipes:
        name_en = (r.get('name_english') or '').lower()
        name_de = (r.get('name_german') or '').lower()

        if any(kw in name_en or kw in name_de for kw in keywords):
            steps = r.get('procedural_steps') or []
            preps = [s.get('action', '') for s in steps if s.get('action')]
            matches.append({
                'id': r['id'],
                'name_en': r.get('name_english', ''),
                'name_de': r.get('name_german', ''),
                'fire': r.get('fire_degree', 0),
                'preps': preps,
                'material_source': r.get('material_source', ''),
            })

    if len(matches) >= 2:
        print(f"\n{'='*70}")
        print(f"FAMILY: {family_name.upper()} ({len(matches)} variants)")
        print("=" * 70)
        for m in matches:
            prep_str = ' -> '.join(m['preps']) if m['preps'] else '[no steps]'
            print(f"\n#{m['id']:3d} {m['name_en']}")
            print(f"     German: {m['name_de']}")
            print(f"     Source: {m['material_source']}, Fire: {m['fire']}")
            print(f"     Preps: {prep_str}")

# Special focus: look for herb vs flower vs root variants
print("\n" + "=" * 70)
print("PART-BASED VARIANTS (herb/leaf/flower/root/seed)")
print("=" * 70)

part_keywords = ['herb', 'leaf', 'flower', 'root', 'seed', 'bark', 'fruit', 'berry', 'juice', 'kraut', 'blatt', 'blume', 'wurzel', 'samen']

# Group by base name minus part
base_to_parts = defaultdict(list)
for r in recipes:
    name = (r.get('name_english') or '').lower()
    for part in part_keywords:
        if part in name:
            # Try to extract base name
            base = name.replace(part, '').strip()
            base = base.replace('  ', ' ').strip()
            if len(base) > 2:
                steps = r.get('procedural_steps') or []
                preps = [s.get('action', '') for s in steps if s.get('action')]
                base_to_parts[base].append({
                    'id': r['id'],
                    'name': r.get('name_english', ''),
                    'part': part,
                    'fire': r.get('fire_degree', 0),
                    'preps': preps,
                })
            break

# Show bases with multiple parts
for base, parts in sorted(base_to_parts.items(), key=lambda x: -len(x[1])):
    if len(parts) >= 2:
        print(f"\n{base.upper()}:")
        for p in parts:
            prep_str = ' -> '.join(p['preps']) if p['preps'] else '[no steps]'
            print(f"  #{p['id']:3d} {p['name']} (fire={p['fire']})")
            print(f"       {prep_str}")
