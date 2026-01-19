import json

with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']

# Unique names with procedures
with_proc = [m for m in materials if m.get('procedural_steps')]
unique_with_proc = set(m['name_normalized'] for m in with_proc)

print('Unique materials WITH procedures:', len(unique_with_proc))
print()
print('Coverage by category (with procedures):')

cat_with = {}
for m in with_proc:
    cat = m['material_source']
    cat_with[cat] = cat_with.get(cat, 0) + 1

for cat, count in sorted(cat_with.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {count}')

# Reference expected
ref = {'cold_moist_flower': 13, 'hot_flower': 14, 'leaf': 6, 'fruit': 10,
       'moderate_herb': 11, 'dangerous_herb': 4, 'hot_dry_herb': 21,
       'moist_root': 4, 'hot_dry_root': 6, 'animal': 9}

print()
print('Reference guide expected ~', sum(ref.values()), 'materials')
print('We have procedures for', len(unique_with_proc), 'unique names')
