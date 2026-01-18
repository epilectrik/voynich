"""Test B tab - debug remaining missing classes."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import get_data_store
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle, ZONES
from core.reachability_engine import compute_reachability

# Load data
print('Loading data...')
store = get_data_store()
print()

# Test with one token
token = 'chedy'
bundle = compute_bundle(token)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

# Show grammar state
reachable = b_reach.grammar_by_zone['C'].reachable_classes
pruned = b_reach.grammar_by_zone['C'].pruned_classes
print(f'Grammar in zone C:')
print(f'  Reachable ({len(reachable)}): {sorted(reachable)}')
print(f'  Pruned ({len(pruned)}): {sorted(pruned)}')
print()

# Check what MIDDLEs the pruned classes need
print('=== Pruned Classes and Their MIDDLEs ===')
for class_id in sorted(pruned):
    cls = store.classes.get(class_id)
    if cls:
        effective_middles = {m for m in cls.middles if m}
        print(f'Class {class_id} ({cls.role}): effective MIDDLEs = {sorted(effective_middles)}')

# Check B folio requirements
print()
print('=== B Folio Requirements Analysis ===')
for folio, classes in list(store.b_folio_class_footprints.items())[:3]:
    required = set(classes)
    missing = required - reachable
    print(f'{folio}: requires {len(required)} classes, missing {len(missing)}: {sorted(missing)}')
