"""Debug why B folios are unreachable."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability
import io
from contextlib import redirect_stdout

# Load data silently
with redirect_stdout(io.StringIO()):
    store = get_data_store()

# Test with a token that has rare MIDDLE
token = 'qokeedy'  # MIDDLE 'kee' - only 2 compatible folios
bundle = compute_bundle(token)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

print(f'Token: {token} (MIDDLEs: {bundle.middles})')
print()

# Show grammar
print('Grammar in zone C:')
print(f'  Reachable: {len(b_reach.grammar_by_zone["C"].reachable_classes)}')
print(f'  Classes: {sorted(b_reach.grammar_by_zone["C"].reachable_classes)}')
print()

# Check a few B folios
print('B Folio Analysis:')
for folio in list(store.b_folio_class_footprints.keys())[:5]:
    required = store.b_folio_class_footprints[folio]
    reachable = b_reach.grammar_by_zone["C"].reachable_classes
    missing = required - reachable

    print(f'\n{folio}:')
    print(f'  Required classes: {len(required)} - {sorted(required)[:10]}...')
    print(f'  Reachable: {len(reachable)}')
    print(f'  Missing: {len(missing)} - {sorted(missing)[:10]}...' if missing else '  Missing: 0')

# What classes are in most B folios?
print()
print('='*70)
print('Most common classes in B folios:')
from collections import Counter
class_counts = Counter()
for classes in store.b_folio_class_footprints.values():
    class_counts.update(classes)

for cls, count in class_counts.most_common(10):
    in_grammar = cls in b_reach.grammar_by_zone["C"].reachable_classes
    print(f'  Class {cls}: in {count}/82 B folios, in grammar: {in_grammar}')
