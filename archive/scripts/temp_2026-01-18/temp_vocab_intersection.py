"""Check what MIDDLE vocabularies look like after intersection."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

test_tokens = ['chedy', 'qokeedy', 'qokaiin', 'ol']

for token in test_tokens:
    bundle = compute_bundle(token)
    bundle_middles = bundle.middles

    # Find compatible folios
    compatible_folios = []
    for folio_id, folio_vocab in store.azc_folio_middles.items():
        if not bundle_middles or (bundle_middles <= folio_vocab):
            compatible_folios.append((folio_id, folio_vocab))

    # Intersect vocabularies
    effective_middles = None
    for folio_id, folio_vocab in compatible_folios:
        if effective_middles is None:
            effective_middles = folio_vocab.copy()
        else:
            effective_middles &= folio_vocab

    if effective_middles is None:
        effective_middles = set()

    print(f'{token} (MIDDLEs: {bundle_middles or "none"})')
    print(f'  Compatible folios: {len(compatible_folios)}')
    print(f'  Individual vocab sizes: {[len(v) for _, v in compatible_folios[:5]]}...')
    print(f'  Intersection size: {len(effective_middles)}')
    print(f'  Effective MIDDLEs: {sorted(effective_middles)}')
    print()
