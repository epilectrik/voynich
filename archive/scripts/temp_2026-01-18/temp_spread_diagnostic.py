"""Diagnostic script to check MIDDLE folio spread computation."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

# Force fresh load (not cached)
from core.data_loader import load_all_data

print('Loading data fresh (not cached)...')
store = load_all_data()

print()
print('=' * 60)
print('MIDDLE FOLIO SPREAD DIAGNOSTIC')
print('=' * 60)
print(f'Universal MIDDLEs count: {len(store.universal_middles)}')
print(f'Universal MIDDLEs: {sorted(store.universal_middles)}')
print()

# Show spread distribution
from collections import Counter
spread_dist = Counter(store.middle_folio_spread.values())
print('MIDDLE spread distribution (how many folios each MIDDLE appears in):')
for spread, count in sorted(spread_dist.items()):
    pct = 100 * count / len(store.middle_folio_spread) if store.middle_folio_spread else 0
    marker = ' <-- UNIVERSAL' if spread >= 4 else ''
    print(f'  {spread} folios: {count} MIDDLEs ({pct:.1f}%){marker}')

print()
print('=' * 60)
print('SAMPLE A RECORDS')
print('=' * 60)

from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle

a_store = load_a_records()
records = a_store.registry_entries[:10]

for record in records:
    bundle = compute_record_bundle(record)
    bundle_middles = bundle.middles

    # Classify bundle MIDDLEs
    # Restricted: 1-3 folios (can forbid)
    # Universal: 4+ folios (cannot forbid)
    # Unknown: 0 folios (cannot forbid - no information)
    restricted = {m for m in bundle_middles if 1 <= store.middle_folio_spread.get(m, 0) <= 3}
    universal = {m for m in bundle_middles if store.middle_folio_spread.get(m, 0) >= 4}
    unknown = {m for m in bundle_middles if store.middle_folio_spread.get(m, 0) == 0}

    # Find compatible folios
    compatible = []
    for folio_id, vocab in store.azc_folio_middles.items():
        missing = restricted - vocab
        if not missing:
            compatible.append(folio_id)

    print(f'{record.display_name}:')
    print(f'  All MIDDLEs: {sorted(bundle_middles)}')
    print(f'  Restricted: {sorted(restricted)} (spread 1-3, CAN forbid)')
    print(f'  Universal: {sorted(universal)} (spread 4+, cannot forbid)')
    print(f'  Unknown: {sorted(unknown)} (spread 0, cannot forbid)')
    print(f'  Compatible folios: {len(compatible)}')
    if not compatible and restricted:
        # Show why no folios match
        print(f'  NO MATCH - checking restricted MIDDLEs:')
        for m in restricted:
            spread = store.middle_folio_spread.get(m, 0)
            folios = [f for f, v in store.azc_folio_middles.items() if m in v]
            print(f'    {m}: spread={spread}, in folios={folios[:5]}{"..." if len(folios) > 5 else ""}')
    print()
