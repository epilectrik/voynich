"""Test if different A entries produce different B folio reachability."""
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

# Test different A entries (tokens with different MIDDLEs)
test_tokens = ['chedy', 'daiin', 'qokaiin', 'shedy', 'otaiin', 'chol', 'dain']

print('='*70)
print('A Entry Differentiation Test')
print('='*70)
print()

results = {}
for token in test_tokens:
    bundle = compute_bundle(token)
    projection = project_bundle(bundle)
    b_reach = compute_reachability(projection)

    # Count B folio statuses
    status_counts = Counter(f.status for f in b_reach.folio_results.values())
    reachable = status_counts.get(ReachabilityStatus.REACHABLE, 0)
    conditional = status_counts.get(ReachabilityStatus.CONDITIONAL, 0)
    unreachable = status_counts.get(ReachabilityStatus.UNREACHABLE, 0)

    results[token] = {
        'middles': bundle.middles,
        'reachable': reachable,
        'conditional': conditional,
        'unreachable': unreachable,
        'grammar_c': len(b_reach.grammar_by_zone['C'].reachable_classes),
        'grammar_s': len(b_reach.grammar_by_zone['S'].reachable_classes)
    }

    print(f'{token} (MIDDLEs: {bundle.middles or "none"})')
    print(f'  Grammar: C={results[token]["grammar_c"]}/49, S={results[token]["grammar_s"]}/49')
    print(f'  B Folios: {reachable} REACHABLE, {conditional} CONDITIONAL, {unreachable} UNREACHABLE')
    print()

# Summary
print('='*70)
print('Summary: Differentiation Analysis')
print('='*70)

# Check if any tokens produce different results
unique_patterns = set()
for token, r in results.items():
    pattern = (r['reachable'], r['conditional'], r['unreachable'])
    unique_patterns.add(pattern)

print(f'Unique B folio reachability patterns: {len(unique_patterns)}')
if len(unique_patterns) == 1:
    print('WARNING: All A entries produce identical B reachability!')
else:
    print('SUCCESS: Different A entries produce different B reachability')
