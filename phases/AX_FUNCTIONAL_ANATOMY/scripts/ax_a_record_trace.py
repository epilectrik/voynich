"""
Script 2: AX A-Record Trace

Trace AX MIDDLEs backward through the pipeline to Currier A records.
Determine how many A records carry AX-relevant vocabulary and whether
AX participation is required or optional.
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
INVENTORY = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results/ax_middle_inventory.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(SURVIVORS) as f:
    surv_data = json.load(f)

with open(INVENTORY) as f:
    inv_data = json.load(f)

# Get AX PP MIDDLEs from inventory
ax_pp_middles = set(inv_data['pipeline_breakdown']['PP']['middles'])
ax_all_middles = set(inv_data['per_middle'].keys())

# Also get operational role middles for comparison
all_role_middles = inv_data['all_role_middles']
en_middles = set(all_role_middles.get('EN', {}).get('middles', []))
cc_middles = set(all_role_middles.get('CC', {}).get('middles', []))
fl_middles = set(all_role_middles.get('FL', {}).get('middles', []))
fq_middles = set(all_role_middles.get('FQ', {}).get('middles', []))
operational_middles = en_middles | cc_middles | fl_middles | fq_middles

print(f"AX PP MIDDLEs to trace: {len(ax_pp_middles)}")
print(f"AX total MIDDLEs: {len(ax_all_middles)}")

# Per-record analysis
records = surv_data['records']
ax_mid_counts = []
total_mid_counts = []
ax_coverage = []
records_with_ax = 0
records_without_ax = 0

# Per-MIDDLE: how many A records contain it
middle_a_record_count = defaultdict(int)

# Track per-record details
record_details = []

for rec in records:
    a_middles = set(rec['a_middles'])
    total_mids = len(a_middles)

    # AX PP MIDDLEs present in this A record
    ax_present = a_middles & ax_pp_middles
    ax_count = len(ax_present)

    # Operational middles present
    op_present = a_middles & operational_middles
    op_count = len(op_present)

    ax_mid_counts.append(ax_count)
    total_mid_counts.append(total_mids)

    if ax_count > 0:
        records_with_ax += 1
    else:
        records_without_ax += 1

    # Track per-MIDDLE presence
    for mid in ax_present:
        middle_a_record_count[mid] += 1

    record_details.append({
        'a_record': rec['a_record'],
        'total_middles': total_mids,
        'ax_pp_middles': ax_count,
        'operational_middles': op_count,
        'ax_middles_present': sorted(ax_present),
    })

n = len(records)

# Correlation: AX MIDDLE count vs total MIDDLE count
mean_ax = sum(ax_mid_counts) / n
mean_total = sum(total_mid_counts) / n
ss_xy = sum((x - mean_total) * (y - mean_ax) for x, y in zip(total_mid_counts, ax_mid_counts))
ss_xx = sum((x - mean_total) ** 2 for x in total_mid_counts)
ss_yy = sum((y - mean_ax) ** 2 for y in ax_mid_counts)
corr_mid = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_xx > 0 and ss_yy > 0 else 0

# Distribution histogram
ax_hist = defaultdict(int)
for c in ax_mid_counts:
    ax_hist[c] += 1

# Zero-AX analysis
zero_ax_records = [r for r in record_details if r['ax_pp_middles'] == 0]
# Do these records have operational middles?
zero_ax_with_op = [r for r in zero_ax_records if r['operational_middles'] > 0]

# Per-MIDDLE spread
per_middle_spread = {}
for mid in sorted(ax_pp_middles):
    count = middle_a_record_count.get(mid, 0)
    rate = count / n
    per_middle_spread[mid] = {
        'a_record_count': count,
        'presence_rate': round(rate, 4),
    }

# Top and bottom coverage MIDDLEs
sorted_by_count = sorted(per_middle_spread.items(), key=lambda x: -x[1]['a_record_count'])
top_10 = sorted_by_count[:10]
bottom_10 = sorted_by_count[-10:]

# AX-only middles in A records
ax_only_list = inv_data['cross_role_summary']['ax_only_list']
ax_only_in_a = [m for m in ax_only_list if middle_a_record_count.get(m, 0) > 0]

# Print results
print(f"\n=== AX A-RECORD TRACE ===")
print(f"Total A records: {n}")
print(f"Records with at least 1 AX PP MIDDLE: {records_with_ax} ({100*records_with_ax/n:.1f}%)")
print(f"Records with ZERO AX PP MIDDLEs: {records_without_ax} ({100*records_without_ax/n:.1f}%)")
print(f"  Of those, {len(zero_ax_with_op)} have operational MIDDLEs")

print(f"\n=== AX MIDDLE COUNT PER RECORD ===")
print(f"Mean: {mean_ax:.1f}")
print(f"Median: {sorted(ax_mid_counts)[n//2]}")
print(f"Min: {min(ax_mid_counts)}")
print(f"Max: {max(ax_mid_counts)}")

print(f"\n=== DISTRIBUTION ===")
for count in sorted(ax_hist):
    pct = 100 * ax_hist[count] / n
    bar = '#' * int(pct)
    print(f"  {count:2d} AX MIDDLEs: {ax_hist[count]:4d} records ({pct:5.1f}%) {bar}")

print(f"\n=== CORRELATION ===")
print(f"AX MIDDLE count vs total MIDDLE count: r = {corr_mid:.4f}")

print(f"\n=== TOP 10 AX PP MIDDLEs (most widespread in A) ===")
for mid, info in top_10:
    print(f"  {mid:12s}: {info['a_record_count']:4d} records ({info['presence_rate']:.3f})")

print(f"\n=== BOTTOM 10 AX PP MIDDLEs (least widespread in A) ===")
for mid, info in bottom_10:
    print(f"  {mid:12s}: {info['a_record_count']:4d} records ({info['presence_rate']:.3f})")

print(f"\n=== AX-ONLY MIDDLEs in A records ===")
print(f"AX-only MIDDLEs that appear in A: {len(ax_only_in_a)}/{len(ax_only_list)}")
for m in ax_only_in_a:
    print(f"  {m:12s}: {middle_a_record_count[m]} records")

print(f"\n=== ZERO-AX RECORDS (first 10) ===")
for r in zero_ax_records[:10]:
    print(f"  {r['a_record']}: total_middles={r['total_middles']}, op_middles={r['operational_middles']}")

# Save results
results = {
    'total_a_records': n,
    'records_with_ax_middles': records_with_ax,
    'records_without_ax_middles': records_without_ax,
    'ax_coverage_rate': round(records_with_ax / n, 4),
    'zero_ax_with_operational': len(zero_ax_with_op),
    'ax_middles_per_record': {
        'mean': round(mean_ax, 2),
        'median': sorted(ax_mid_counts)[n // 2],
        'min': min(ax_mid_counts),
        'max': max(ax_mid_counts),
        'histogram': {str(k): v for k, v in sorted(ax_hist.items())},
    },
    'correlation_ax_vs_total_middles': round(corr_mid, 4),
    'per_middle_a_record_count': per_middle_spread,
    'ax_only_middles_in_a': {
        'count': len(ax_only_in_a),
        'total_ax_only': len(ax_only_list),
        'middles': ax_only_in_a,
    },
    'zero_ax_records': [{
        'a_record': r['a_record'],
        'total_middles': r['total_middles'],
        'operational_middles': r['operational_middles'],
    } for r in zero_ax_records[:50]],
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_a_record_trace.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_a_record_trace.json'}")
