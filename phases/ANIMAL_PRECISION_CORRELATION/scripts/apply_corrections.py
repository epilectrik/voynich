#!/usr/bin/env python3
"""Apply instruction sequence corrections to the JSON database."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

# Load corrections
corrections_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'sequence_corrections.json'
with open(corrections_path, 'r', encoding='utf-8') as f:
    corrections_data = json.load(f)

# Convert to dict by ID
corrections = {c['id']: c['new_seq'] for c in corrections_data['corrections']}

# Manual corrections for cases the scanner missed
manual_corrections = {
    # #110: "40 days" is a procedural step, add LINK
    110: ['AUX', 'FLOW', 'LINK', 'e_ESCAPE'],
}

# Merge corrections
for id_, seq in manual_corrections.items():
    corrections[id_] = seq

# Load JSON database
json_path = PROJECT_ROOT / 'data' / 'brunschwig_complete.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Apply corrections
applied = []
for r in data['recipes']:
    if r['id'] in corrections:
        old_seq = r.get('instruction_sequence')
        new_seq = corrections[r['id']]
        r['instruction_sequence'] = new_seq
        applied.append({
            'id': r['id'],
            'name': r['name_german'],
            'old': old_seq,
            'new': new_seq
        })

# Save updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Applied {len(applied)} corrections to {json_path}")
print()
print("Corrections applied:")
for a in applied:
    print(f"  #{a['id']:3d} {a['name']:30s}: {a['old']} -> {a['new']}")

# Count unique sequences now
seq_counts = {}
for r in data['recipes']:
    seq = r.get('instruction_sequence')
    if seq:
        seq_tuple = tuple(seq)
        seq_counts[seq_tuple] = seq_counts.get(seq_tuple, 0) + 1

print()
print("=" * 60)
print("SEQUENCE DISTRIBUTION AFTER CORRECTIONS")
print("=" * 60)
for seq, count in sorted(seq_counts.items(), key=lambda x: -x[1]):
    print(f"  {list(seq)}: {count}")
