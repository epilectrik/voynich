"""Analyze effect of different thresholds for universal/restricted."""
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

print('THRESHOLD ANALYSIS')
print('=' * 70)
print()

# For each potential threshold, calculate record distribution
for threshold in [2, 3, 4, 5, 8, 12, 29]:
    record_cats = {'no_restricted': 0, 'has_restricted': 0}
    compat_dist = Counter()

    for record in a_store.registry_entries:
        bundle = compute_record_bundle(record)
        # Restricted = spread 1 to (threshold-1)
        restricted = {m for m in bundle.middles
                      if 1 <= store.middle_folio_spread.get(m, 0) < threshold}

        if restricted:
            record_cats['has_restricted'] += 1
        else:
            record_cats['no_restricted'] += 1

        # Count compatible folios
        compatible = sum(1 for f, vocab in store.azc_folio_middles.items()
                         if not (restricted - vocab))
        if compatible == 0:
            compat_dist['0'] += 1
        elif compatible == 1:
            compat_dist['1'] += 1
        elif compatible == 2:
            compat_dist['2'] += 1
        else:
            compat_dist['3+'] += 1

    pct_no_restr = 100 * record_cats['no_restricted'] / len(a_store.registry_entries)
    print(f'Threshold {threshold} (universal >= {threshold}, restricted < {threshold}):')
    print(f'  Records with NO restricted: {record_cats["no_restricted"]} ({pct_no_restr:.1f}%)')
    print(f'  Compatible folio distribution: 0={compat_dist["0"]}, 1={compat_dist["1"]}, 2={compat_dist["2"]}, 3+={compat_dist["3+"]}')
    print()

# Also show what MIDDLEs are in each spread range
print()
print('MIDDLEs BY SPREAD RANGE (from AZC vocab)')
print('=' * 70)
spread_groups = {
    '1': [], '2': [], '3': [], '4-6': [], '7-12': [], '13+': []
}
for m, spread in store.middle_folio_spread.items():
    if spread == 1:
        spread_groups['1'].append(m)
    elif spread == 2:
        spread_groups['2'].append(m)
    elif spread == 3:
        spread_groups['3'].append(m)
    elif spread <= 6:
        spread_groups['4-6'].append(m)
    elif spread <= 12:
        spread_groups['7-12'].append(m)
    else:
        spread_groups['13+'].append(m)

for grp, middles in spread_groups.items():
    print(f'  Spread {grp}: {len(middles)} MIDDLEs')
    if len(middles) <= 10:
        print(f'    {sorted(middles)}')
    else:
        print(f'    Examples: {sorted(middles)[:8]}...')
