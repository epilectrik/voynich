"""Check which B folios don't need the missing classes."""
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

# Test with 'qokeedy'
token = 'qokeedy'
bundle = compute_bundle(token)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

reachable_classes = b_reach.grammar_by_zone["C"].reachable_classes
missing_from_grammar = set(range(1, 50)) - reachable_classes

print(f'Token: {token} (MIDDLEs: {bundle.middles})')
print(f'Reachable classes: {len(reachable_classes)}/49')
print(f'Missing from grammar: {sorted(missing_from_grammar)}')
print()

# For each missing class, count how many B folios need it
print('B folio requirements for missing classes:')
for cls_id in sorted(missing_from_grammar):
    count = sum(1 for classes in store.b_folio_class_footprints.values() if cls_id in classes)
    cls = store.classes.get(cls_id)
    role = cls.role if cls else '?'
    middles = cls.middles if cls else set()
    print(f'  Class {cls_id} ({role}): needed by {count}/82 B folios')
    print(f'    MIDDLEs: {middles}')

# Check for B folios that might NOT need these missing classes
print()
print('B folios that could potentially be REACHABLE:')
count_reachable = 0
for folio, required in store.b_folio_class_footprints.items():
    missing = required - reachable_classes
    if not missing:
        count_reachable += 1
        print(f'  {folio}: requires {len(required)} classes, all reachable!')
    elif len(missing) <= 2:
        print(f'  {folio}: only missing {len(missing)}: {sorted(missing)}')

print(f'\nTotal B folios with all classes reachable: {count_reachable}')
