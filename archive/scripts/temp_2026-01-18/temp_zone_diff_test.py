"""Test zone differentiation after default legality fix."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle, ZONES
from core.reachability_engine import compute_reachability
import io
from contextlib import redirect_stdout
from collections import Counter

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

# Check the zone legality data
print('=== Zone Legality Analysis ===')
print(f'MIDDLEs with explicit zone restrictions: {len(store.middle_zone_legality)}')
partial = {m: zones for m, zones in store.middle_zone_legality.items()
           if zones != {'C', 'P', 'R', 'S'}}
print(f'MIDDLEs with partial legality: {len(partial)}')
print()
print('Partial legality details:')
for m, zones in sorted(partial.items()):
    print(f'  "{m}": legal in {sorted(zones)}')

# Check if any classes use these zone-restricted MIDDLEs
print()
print('=== Classes using zone-restricted MIDDLEs ===')
for class_id, cls in store.classes.items():
    effective_middles = {m for m in cls.middles if m}
    restricted = effective_middles & set(partial.keys())
    if restricted:
        print(f'  Class {class_id}: uses {sorted(restricted)}')

# Test with 'chedy'
print()
print('='*60)
token = 'chedy'
bundle = compute_bundle(token)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

print(f'Token: {token} (MIDDLEs: {bundle.middles})')
print()
print('Grammar by zone:')
for zone in ['C', 'P', 'R1', 'R2', 'R3', 'S']:
    gs = b_reach.grammar_by_zone.get(zone)
    if gs:
        print(f'  {zone}: {len(gs.reachable_classes)} reachable, {len(gs.pruned_classes)} pruned')
        if gs.pruned_classes:
            print(f'      Pruned: {sorted(gs.pruned_classes)}')

print()
print('B Folio Reachability:')
status_counts = Counter(f.status.value for f in b_reach.folio_results.values())
for status, count in sorted(status_counts.items()):
    print(f'  {status}: {count}')
