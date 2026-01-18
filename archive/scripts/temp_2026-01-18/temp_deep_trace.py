"""Deep trace to understand why zone differentiation isn't happening."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.azc_projection import _get_consolidated_zone, ALL_ZONES
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

folio = 'f67r1'
folio_vocab = store.azc_folio_middles.get(folio, set())

# Build effective_legal_middles for each zone
print(f'Folio: {folio}')
print(f'Folio vocabulary: {len(folio_vocab)} MIDDLEs')
print()

zones_effective = {}
for zone in ['C', 'P', 'R', 'S']:
    effective = set()
    for middle in folio_vocab:
        legal_zones = store.middle_zone_legality.get(middle, ALL_ZONES)
        if zone in legal_zones:
            effective.add(middle)
    zones_effective[zone] = effective
    print(f'Zone {zone}: {len(effective)} effective MIDDLEs')

# Show differences between zones
print()
print('Zone differences:')
for z1, z2 in [('C', 'P'), ('P', 'R'), ('R', 'S')]:
    only_z1 = zones_effective[z1] - zones_effective[z2]
    only_z2 = zones_effective[z2] - zones_effective[z1]
    if only_z1:
        print(f'  {z1} has but {z2} lacks: {sorted(only_z1)}')
    if only_z2:
        print(f'  {z2} has but {z1} lacks: {sorted(only_z2)}')
    if not only_z1 and not only_z2:
        print(f'  {z1} and {z2}: identical')

# Now check classes with zone-restricted MIDDLEs
print()
print('='*60)
print('Classes using zone-restricted MIDDLEs (checking f67r1):')
print()

# MIDDLEs with partial legality
partial = {m: zones for m, zones in store.middle_zone_legality.items()
           if zones != {'C', 'P', 'R', 'S'}}

for class_id, cls in sorted(store.classes.items()):
    effective_middles = {m for m in cls.middles if m}
    if not effective_middles:
        continue  # Atomic class

    # Check if any class MIDDLEs are zone-restricted
    restricted_middles = effective_middles & set(partial.keys())
    if not restricted_middles:
        continue

    # Check class reachability by zone
    print(f'Class {class_id}: MIDDLEs = {sorted(effective_middles)}')
    for zone in ['C', 'P', 'R', 'S']:
        available = effective_middles & zones_effective[zone]
        reachable = len(available) > 0
        print(f'  Zone {zone}: available = {sorted(available)}, reachable = {reachable}')
    print()
