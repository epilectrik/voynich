"""Check AZC folio compatibility counts."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

test_tokens = ['chedy', 'daiin', 'qokaiin', 'shedy', 'otaiin', 'chol', 'dain', 'qokeedy']

print('AZC Folio Compatibility Check')
print('='*70)
print()

for token in test_tokens:
    bundle = compute_bundle(token)
    bundle_middles = bundle.middles

    compatible = []
    for folio_id, folio_vocab in store.azc_folio_middles.items():
        if not bundle_middles or (bundle_middles <= folio_vocab):
            compatible.append(folio_id)

    print(f'{token} (MIDDLEs: {bundle_middles or "none"})')
    print(f'  Compatible AZC folios: {len(compatible)}')
    if compatible:
        print(f'  Folios: {compatible[:5]}{"..." if len(compatible) > 5 else ""}')
    print()

# Check what single MIDDLE 'e' tokens are compatible with
print('='*70)
print('Detailed check for MIDDLE "e":')
e_folios = []
for folio_id, folio_vocab in store.azc_folio_middles.items():
    if 'e' in folio_vocab:
        e_folios.append(folio_id)
print(f'Folios containing "e": {len(e_folios)} of {len(store.azc_folio_middles)}')
print(f'Folios: {e_folios}')
