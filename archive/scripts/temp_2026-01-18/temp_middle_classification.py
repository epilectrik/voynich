"""Analyze A record MIDDLE classification."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from core.data_loader import load_all_data
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from collections import Counter

# Force fresh load
import core.data_loader as dl
dl._data_store = None

store = load_all_data()
a_store = load_a_records()

# Analyze MIDDLE classification across all A records
all_middles_seen = set()
middle_category = Counter()  # unknown, restricted, universal

for record in a_store.registry_entries:
    bundle = compute_record_bundle(record)
    for m in bundle.middles:
        all_middles_seen.add(m)
        spread = store.middle_folio_spread.get(m, 0)
        if spread == 0:
            middle_category['unknown'] += 1
        elif spread <= 3:
            middle_category['restricted'] += 1
        else:
            middle_category['universal'] += 1

print('MIDDLE CLASSIFICATION IN A RECORDS')
print('=' * 60)
print(f'Total MIDDLE occurrences: {sum(middle_category.values())}')
print(f'Unique MIDDLEs seen: {len(all_middles_seen)}')
print()
print('Occurrences by category:')
total = sum(middle_category.values())
for cat, count in middle_category.most_common():
    print(f'  {cat}: {count} ({100*count/total:.1f}%)')

print()
print('UNIQUE MIDDLEs by category:')
unique_cats = {'unknown': set(), 'restricted': set(), 'universal': set()}
for m in all_middles_seen:
    spread = store.middle_folio_spread.get(m, 0)
    if spread == 0:
        unique_cats['unknown'].add(m)
    elif spread <= 3:
        unique_cats['restricted'].add(m)
    else:
        unique_cats['universal'].add(m)

for cat, middles in unique_cats.items():
    print(f'  {cat}: {len(middles)} unique MIDDLEs')
    if len(middles) <= 20:
        print(f'    {sorted(middles)}')
    else:
        print(f'    Examples: {sorted(middles)[:15]}...')

# Check record-level classification
print()
print('RECORD-LEVEL ANALYSIS')
print('=' * 60)
record_cats = Counter()
for record in a_store.registry_entries:
    bundle = compute_record_bundle(record)
    restricted = {m for m in bundle.middles if 1 <= store.middle_folio_spread.get(m, 0) <= 3}
    if len(restricted) == 0:
        record_cats['no_restricted'] += 1
    elif len(restricted) == 1:
        record_cats['1_restricted'] += 1
    elif len(restricted) == 2:
        record_cats['2_restricted'] += 1
    else:
        record_cats['3+_restricted'] += 1

print('Records by restricted MIDDLE count:')
total = sum(record_cats.values())
for cat, count in sorted(record_cats.items()):
    print(f'  {cat}: {count} ({100*count/total:.1f}%)')
