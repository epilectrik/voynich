"""Test a wider range of tokens to find B matches."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability, ReachabilityStatus
import io
from contextlib import redirect_stdout
from collections import Counter

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

# First, find AZC folios with 'k' and 't' (needed for classes 36, 48)
print('AZC folios with key MIDDLEs:')
for middle in ['k', 't', 'ke', 'd']:
    folios_with = [f for f, vocab in store.azc_folio_middles.items() if middle in vocab]
    print(f'  "{middle}": {len(folios_with)} folios - {folios_with[:5]}...')
print()

# Now test tokens that have these MIDDLEs
test_tokens = [
    'qokeedy',  # kee
    'daiin',    # i
    'chedy',    # e
    'shedy',    # e
    'ol',       # (none)
    'dar',      # (none)
    'chey',     # (none)
    'qokaiin',  # k
    'dain',     # (none)
    'chol',     # (none)
    'otedy',    # e
    'okedy',    # k
    'dedy',     # e
    'tedy',     # e
]

print('='*70)
print('Token Test Results')
print('='*70)

for token in test_tokens:
    bundle = compute_bundle(token)
    projection = project_bundle(bundle)
    b_reach = compute_reachability(projection)

    status_counts = Counter(f.status for f in b_reach.folio_results.values())
    reachable = status_counts.get(ReachabilityStatus.REACHABLE, 0)
    conditional = status_counts.get(ReachabilityStatus.CONDITIONAL, 0)
    unreachable = status_counts.get(ReachabilityStatus.UNREACHABLE, 0)

    # Count compatible AZC folios
    bundle_middles = bundle.middles
    compatible = sum(1 for f, vocab in store.azc_folio_middles.items()
                     if not bundle_middles or bundle_middles <= vocab)

    grammar_c = len(b_reach.grammar_by_zone['C'].reachable_classes)

    print(f'{token:12} MIDDLEs: {str(bundle_middles or "none"):8} '
          f'AZC: {compatible:2} '
          f'Grammar: {grammar_c}/49 '
          f'B: {reachable}R/{conditional}C/{unreachable}U')
