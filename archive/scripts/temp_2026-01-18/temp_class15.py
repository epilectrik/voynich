"""Check Class 15 MIDDLEs and why it's pruned."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

# What MIDDLEs does Class 15 need?
cls15 = store.classes.get(15)
print(f'Class 15: {cls15.role}')
print(f'  MIDDLEs: {cls15.middles}')
print(f'  Effective MIDDLEs (non-empty): {[m for m in cls15.middles if m]}')
print()

# Which AZC folios contain these MIDDLEs?
effective = {m for m in cls15.middles if m}
print('AZC folios containing Class 15 MIDDLEs:')
for folio_id, vocab in store.azc_folio_middles.items():
    common = effective & vocab
    if common:
        print(f'  {folio_id}: has {sorted(common)}')

# Check zone legality for these MIDDLEs
print()
print('Zone legality for Class 15 MIDDLEs:')
from core.azc_projection import ALL_ZONES
for m in sorted(effective):
    legal = store.middle_zone_legality.get(m, ALL_ZONES)
    print(f'  "{m}": legal in {sorted(legal)}')
