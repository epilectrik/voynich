"""Test with REAL Currier A records."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import load_all_data
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability, ReachabilityStatus
import io
from contextlib import redirect_stdout
from collections import Counter

# IMPORTANT: Clear cache and force fresh load to pick up code changes
import core.data_loader as dl
dl._data_store = None

# Load data (showing diagnostics)
print("Loading data...")
store = load_all_data()
a_store = load_a_records()
print()

print(f'Loaded {a_store.total_records} Currier A records')
print(f'Registry entries (2+ tokens): {len(a_store.registry_entries)}')
print()

# Test a sample of real A records
print('='*80)
print('REAL A RECORD TEST')
print('='*80)
print()

# Get first 20 registry entries
records = a_store.registry_entries[:20]

for record in records:
    bundle = compute_record_bundle(record)
    projection = project_bundle(bundle)
    b_reach = compute_reachability(projection)

    status_counts = Counter(f.status for f in b_reach.folio_results.values())
    reachable = status_counts.get(ReachabilityStatus.REACHABLE, 0)
    conditional = status_counts.get(ReachabilityStatus.CONDITIONAL, 0)
    unreachable = status_counts.get(ReachabilityStatus.UNREACHABLE, 0)

    # Count compatible AZC folios using the CORRECT restricted-only logic
    # (matches the logic in reachability_engine.py)
    bundle_middles = bundle.middles
    restricted_middles = {
        m for m in bundle_middles
        if 1 <= store.middle_folio_spread.get(m, 0) <= 3
    }
    compatible = sum(1 for f, vocab in store.azc_folio_middles.items()
                     if not (restricted_middles - vocab))

    grammar_c = len(b_reach.grammar_by_zone['C'].reachable_classes)

    tokens_str = ' '.join(record.tokens[:3])
    if len(record.tokens) > 3:
        tokens_str += '...'

    print(f'{record.display_name:12} {len(record.tokens)} tokens  MIDDLEs: {len(bundle.middles):2}  '
          f'AZC: {compatible:2}  Gr: {grammar_c}/49  '
          f'B: {reachable}R/{conditional}C/{unreachable}U')
    print(f'             Tokens: {tokens_str}')
    print(f'             MIDDLEs: {sorted(bundle.middles)[:8]}{"..." if len(bundle.middles) > 8 else ""}')
    print()

# Summary
print('='*80)
print('SUMMARY')
print('='*80)

# Test all registry entries
total_reachable = 0
total_conditional = 0
total_unreachable = 0
compat_counts = []

for record in a_store.registry_entries:
    bundle = compute_record_bundle(record)
    projection = project_bundle(bundle)
    b_reach = compute_reachability(projection)

    status_counts = Counter(f.status for f in b_reach.folio_results.values())
    reachable = status_counts.get(ReachabilityStatus.REACHABLE, 0)
    conditional = status_counts.get(ReachabilityStatus.CONDITIONAL, 0)

    if reachable > 0:
        total_reachable += 1
    elif conditional > 0:
        total_conditional += 1
    else:
        total_unreachable += 1

    bundle_middles = bundle.middles
    restricted_middles = {
        m for m in bundle_middles
        if 1 <= store.middle_folio_spread.get(m, 0) <= 3
    }
    compatible = sum(1 for f, vocab in store.azc_folio_middles.items()
                     if not (restricted_middles - vocab))
    compat_counts.append(compatible)

print(f'Total A records tested: {len(a_store.registry_entries)}')
print(f'Records with any REACHABLE B: {total_reachable}')
print(f'Records with only CONDITIONAL B: {total_conditional}')
print(f'Records with all UNREACHABLE B: {total_unreachable}')
print()
print(f'Compatible AZC folios per record:')
print(f'  Min: {min(compat_counts)}, Max: {max(compat_counts)}, Avg: {sum(compat_counts)/len(compat_counts):.1f}')
print(f'  Records with 0 compatible: {compat_counts.count(0)}')
print(f'  Records with 1 compatible: {compat_counts.count(1)}')
print(f'  Records with 2 compatible: {compat_counts.count(2)}')
print(f'  Records with 3+ compatible: {sum(1 for c in compat_counts if c >= 3)}')
