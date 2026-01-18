"""Test three-set model projection."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle, ZONES

# Load data
print('Loading data...')
store = get_data_store()
print(f'  {len(store.classes)} instruction classes')
print(f'  {len(store.azc_folios)} AZC folios')
print(f'  {len(store.azc_folio_middles)} AZC folio vocabularies')
print()

# Test with different A entries
test_tokens = ['chedy', 'qokaiin', 'shey', 'ol', 'daiin']

for token in test_tokens:
    bundle = compute_bundle(token)
    summary = project_bundle(bundle)

    print(f'{token} (MIDDLEs: {bundle.middles or "none"}):')

    # Show first 3 folios with zone progression
    for folio, result in list(summary.results.items())[:3]:
        reachable_by_zone = [
            len(result.reachability_by_zone[z].reachable_classes)
            for z in ZONES
        ]
        print(f'  {folio}: {reachable_by_zone}')
    print()

# Test differentiation: same folio, different A entries
print('=== Differentiation Test ===')
folio = 'f67r1'
for token in test_tokens:
    bundle = compute_bundle(token)
    summary = project_bundle(bundle)
    result = summary.results.get(folio)
    if result:
        counts = [len(result.reachability_by_zone[z].reachable_classes) for z in ZONES]
        print(f'{token} -> {folio}: C={counts[0]} P={counts[1]} R1={counts[2]} R2={counts[3]} R3={counts[4]} S={counts[5]}')
