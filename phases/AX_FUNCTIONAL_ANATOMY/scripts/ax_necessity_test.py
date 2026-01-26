"""
Script 5: AX Necessity Test

Determine whether AX is structurally necessary in every pipeline context,
or whether some A-record contexts can function with zero AX classes.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path('C:/git/voynich')
SURVIVORS = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(SURVIVORS) as f:
    surv_data = json.load(f)

# AX definitions
AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 14, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}

# Per-record analysis
records = surv_data['records']
ax_count_hist = defaultdict(int)
init_present_count = 0
med_present_count = 0
final_present_count = 0
all_present_count = 0

min_ax = float('inf')
max_ax = 0
min_ax_record = None
max_ax_record = None

# Track which AX classes are always present
ax_class_presence = {c: 0 for c in AX_CLASSES}

# Per-record details
record_details = []

for rec in records:
    surviving = set(rec['surviving_classes'])
    ax_surviving = surviving & AX_CLASSES
    ax_init = surviving & AX_INIT
    ax_med = surviving & AX_MED
    ax_final = surviving & AX_FINAL

    n_ax = len(ax_surviving)
    ax_count_hist[n_ax] += 1

    has_init = len(ax_init) > 0
    has_med = len(ax_med) > 0
    has_final = len(ax_final) > 0

    if has_init: init_present_count += 1
    if has_med: med_present_count += 1
    if has_final: final_present_count += 1
    if has_init and has_med and has_final: all_present_count += 1

    for c in ax_surviving:
        ax_class_presence[c] += 1

    if n_ax < min_ax:
        min_ax = n_ax
        min_ax_record = rec['a_record']
    if n_ax > max_ax:
        max_ax = n_ax
        max_ax_record = rec['a_record']

    record_details.append({
        'a_record': rec['a_record'],
        'total_classes': len(surviving),
        'ax_classes': n_ax,
        'has_init': has_init,
        'has_med': has_med,
        'has_final': has_final,
        'ax_init_classes': sorted(ax_init),
        'ax_med_classes': sorted(ax_med),
        'ax_final_classes': sorted(ax_final),
    })

n = len(records)

# AX class always-present analysis
always_present = [c for c, count in ax_class_presence.items() if count == n]
never_absent = sorted(always_present)

# Records with minimal AX
minimal_records = [r for r in record_details if r['ax_classes'] == min_ax]

# Records missing each subgroup
no_init_records = [r for r in record_details if not r['has_init']]
no_med_records = [r for r in record_details if not r['has_med']]
no_final_records = [r for r in record_details if not r['has_final']]

# Correlation: AX variety vs total vocab
total_classes = [r['total_classes'] for r in record_details]
ax_classes = [r['ax_classes'] for r in record_details]
mean_tc = sum(total_classes) / n
mean_ac = sum(ax_classes) / n
ss_xy = sum((x - mean_tc) * (y - mean_ac) for x, y in zip(total_classes, ax_classes))
ss_xx = sum((x - mean_tc) ** 2 for x in total_classes)
ss_yy = sum((y - mean_ac) ** 2 for y in ax_classes)
corr = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_xx > 0 and ss_yy > 0 else 0

# Print results
print("=== AX NECESSITY TEST ===")
print(f"\nTotal A records: {n}")
print(f"Minimum AX classes in any record: {min_ax} (record: {min_ax_record})")
print(f"Maximum AX classes in any record: {max_ax} (record: {max_ax_record})")
print(f"Records with ZERO AX classes: {ax_count_hist.get(0, 0)}")
print(f"Always-present AX classes: {never_absent}")

print(f"\n=== SUBGROUP PRESENCE ===")
print(f"AX_INIT present: {init_present_count}/{n} ({100*init_present_count/n:.1f}%)")
print(f"AX_MED present:  {med_present_count}/{n} ({100*med_present_count/n:.1f}%)")
print(f"AX_FINAL present: {final_present_count}/{n} ({100*final_present_count/n:.1f}%)")
print(f"ALL three present: {all_present_count}/{n} ({100*all_present_count/n:.1f}%)")

print(f"\n=== RECORDS WITHOUT SUBGROUPS ===")
print(f"Records missing AX_INIT: {len(no_init_records)}")
print(f"Records missing AX_MED: {len(no_med_records)}")
print(f"Records missing AX_FINAL: {len(no_final_records)}")

print(f"\n=== AX COUNT DISTRIBUTION ===")
for count in sorted(ax_count_hist):
    print(f"  {count:2d} AX classes: {ax_count_hist[count]:4d} records ({100*ax_count_hist[count]/n:.1f}%)")

print(f"\n=== PER-CLASS PRESENCE RATE ===")
for cls in sorted(AX_CLASSES):
    rate = ax_class_presence[cls] / n
    subgroup = 'INIT' if cls in AX_INIT else 'MED' if cls in AX_MED else 'FINAL'
    print(f"  Class {cls:2d} ({subgroup:5s}): {rate:.3f} ({ax_class_presence[cls]}/{n})")

print(f"\n=== CORRELATION ===")
print(f"AX variety vs total vocab: r = {corr:.4f}")

print(f"\n=== MINIMAL AX RECORDS (n={len(minimal_records)}) ===")
for r in minimal_records[:10]:  # Show first 10
    print(f"  {r['a_record']}: total={r['total_classes']}, ax={r['ax_classes']}, "
          f"init={r['has_init']}, med={r['has_med']}, final={r['has_final']}")

# Save results
results = {
    'minimum_ax_classes': min_ax,
    'maximum_ax_classes': max_ax,
    'min_ax_record': min_ax_record,
    'max_ax_record': max_ax_record,
    'always_present_ax_classes': never_absent,
    'zero_ax_records': ax_count_hist.get(0, 0),
    'subgroup_presence': {
        'AX_INIT': {
            'always_present': init_present_count == n,
            'presence_rate': round(init_present_count / n, 4),
            'records_present': init_present_count,
            'records_missing': len(no_init_records),
        },
        'AX_MED': {
            'always_present': med_present_count == n,
            'presence_rate': round(med_present_count / n, 4),
            'records_present': med_present_count,
            'records_missing': len(no_med_records),
        },
        'AX_FINAL': {
            'always_present': final_present_count == n,
            'presence_rate': round(final_present_count / n, 4),
            'records_present': final_present_count,
            'records_missing': len(no_final_records),
        },
        'all_three_present': {
            'count': all_present_count,
            'rate': round(all_present_count / n, 4),
        }
    },
    'ax_count_distribution': {str(k): v for k, v in sorted(ax_count_hist.items())},
    'per_class_presence': {
        str(cls): {
            'count': ax_class_presence[cls],
            'rate': round(ax_class_presence[cls] / n, 4),
            'subgroup': 'AX_INIT' if cls in AX_INIT else 'AX_MED' if cls in AX_MED else 'AX_FINAL'
        }
        for cls in sorted(AX_CLASSES)
    },
    'correlation_ax_vs_total': round(corr, 4),
    'minimal_records': minimal_records[:20],
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_necessity_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_necessity_test.json'}")
