"""Check record f1r.12 which shows B folio differentiation."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability, ReachabilityStatus
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()
    a_store = load_a_records()

# Find f1r.12
record = None
for r in a_store.registry_entries:
    if r.display_name == 'f1r.12':
        record = r
        break

if not record:
    print('Record f1r.12 not found')
    exit()

bundle = compute_record_bundle(record)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

print('='*70)
print(f'Record: {record.display_name}')
print(f'Tokens: {" ".join(record.tokens)}')
print(f'Bundle MIDDLEs: {sorted(bundle.middles)}')
print('='*70)
print()

# Show compatible AZC folios
print('Compatible AZC folios:')
for folio_id, folio_vocab in store.azc_folio_middles.items():
    if bundle.middles <= folio_vocab:
        common = bundle.middles & folio_vocab
        print(f'  {folio_id}: vocab size={len(folio_vocab)}, contains all bundle MIDDLEs')

print()
print('Grammar by zone:')
for zone in ['C', 'P', 'R1', 'R2', 'R3', 'S']:
    gs = b_reach.grammar_by_zone.get(zone)
    if gs:
        print(f'  {zone}: {len(gs.reachable_classes)}/49 reachable')

print()
print('B Folio Results:')
reachable = [f for f in b_reach.folio_results.values() if f.status == ReachabilityStatus.REACHABLE]
conditional = [f for f in b_reach.folio_results.values() if f.status == ReachabilityStatus.CONDITIONAL]
unreachable = [f for f in b_reach.folio_results.values() if f.status == ReachabilityStatus.UNREACHABLE]

print(f'  REACHABLE: {len(reachable)}')
for f in reachable:
    print(f'    {f.folio}: requires {len(f.required_classes)} classes, all available')

print(f'\n  CONDITIONAL: {len(conditional)}')
for f in conditional[:5]:
    print(f'    {f.folio}: reachable in zones {f.reachable_zones}')
if len(conditional) > 5:
    print(f'    ...and {len(conditional)-5} more')

print(f'\n  UNREACHABLE: {len(unreachable)}')
for f in unreachable[:3]:
    print(f'    {f.folio}: missing classes {sorted(f.missing_classes)}')
