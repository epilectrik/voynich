"""Test single folio projection to see zone differentiation before aggregation."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle, ZONES, compute_zone_reachability
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

# Pick an AZC folio and examine zone differentiation
folio = 'f67r1'  # First AZC folio
token = 'chedy'
bundle = compute_bundle(token)

print(f'Token: {token} (MIDDLEs: {bundle.middles})')
print(f'Folio: {folio}')
print()

# Get folio vocabulary
folio_vocab = store.azc_folio_middles.get(folio, set())
print(f'Folio vocabulary ({len(folio_vocab)} MIDDLEs): {sorted(folio_vocab)[:20]}...')
print()

# Check zone differentiation for this folio
print('Zone-by-zone analysis:')
for zone in ZONES:
    zr = compute_zone_reachability(bundle, folio, zone, store)
    print(f'\nZone {zone}:')
    print(f'  Reachable classes: {len(zr.reachable_classes)}')
    print(f'  Pruned classes: {len(zr.pruned_classes)}')
    if zr.pruned_classes:
        print(f'  Pruned: {sorted(zr.pruned_classes)}')

# Let's trace what happens with class 30 (uses 'm')
print()
print('='*60)
print("Detailed trace for Class 30 (uses MIDDLE 'm'):")
cls30 = store.classes.get(30)
print(f"  Class 30 MIDDLEs: {cls30.middles}")

# Check if 'm' is in the folio vocabulary
m_in_vocab = 'm' in folio_vocab
print(f"  'm' in folio vocabulary: {m_in_vocab}")

# Check 'm' legality
m_legal_zones = store.middle_zone_legality.get('m', {'C', 'P', 'R', 'S'})
print(f"  'm' legal zones: {sorted(m_legal_zones)}")

# Trace through each zone
print()
print("  Per-zone 'm' status:")
for zone in ZONES:
    from core.azc_projection import _get_consolidated_zone, ALL_ZONES
    legality_zone = _get_consolidated_zone(zone)

    # Check if 'm' would be in effective_legal
    if m_in_vocab:
        legal = legality_zone in m_legal_zones
        print(f"    {zone} (lookup={legality_zone}): 'm' legal = {legal}")
    else:
        print(f"    {zone}: 'm' not in folio vocabulary")
