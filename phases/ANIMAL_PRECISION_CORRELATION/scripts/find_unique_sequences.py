#!/usr/bin/env python3
"""Find materials with unique instruction sequences for triangulation testing."""

import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count instruction sequence patterns
sequence_counts = Counter()
sequence_materials = {}

for r in data['recipes']:
    if not r.get('has_procedure'):
        continue
    seq = r.get('instruction_sequence') or []
    if not seq:
        continue

    # Convert to tuple for hashing
    seq_tuple = tuple(seq)
    sequence_counts[seq_tuple] += 1

    if seq_tuple not in sequence_materials:
        sequence_materials[seq_tuple] = []
    sequence_materials[seq_tuple].append({
        'id': r['id'],
        'name': r['name_german'],
        'english': r['name_english'],
        'class': r.get('material_class', 'unknown'),
        'fire_degree': r.get('fire_degree', 'unknown')
    })

print("=" * 70)
print("INSTRUCTION SEQUENCE ANALYSIS")
print("=" * 70)
print()

# Sort by frequency
sorted_seqs = sorted(sequence_counts.items(), key=lambda x: -x[1])

print("SEQUENCE FREQUENCY (most common first):")
print()
for seq, count in sorted_seqs[:10]:
    print(f"  {list(seq)}: {count} materials")

print()
print("=" * 70)
print("UNIQUE SEQUENCES (only 1-2 materials)")
print("=" * 70)
print()

unique_seqs = [(seq, count) for seq, count in sorted_seqs if count <= 2]

for seq, count in unique_seqs:
    materials = sequence_materials[seq]
    print(f"Sequence: {list(seq)}")
    print(f"  Count: {count}")
    for m in materials:
        print(f"  - #{m['id']} {m['name']} ({m['english']})")
        print(f"    Class: {m['class']}, Fire: {m['fire_degree']}")
    print()

print("=" * 70)
print("BEST TRIANGULATION CANDIDATES")
print("=" * 70)
print()
print("Looking for: unique sequence + distinctive steps + known class")
print()

# Score unique sequences
candidates = []
for seq, count in unique_seqs:
    materials = sequence_materials[seq]

    # Score based on:
    # - More steps = more discriminative
    # - Includes rare steps (FLOW, k_ENERGY, h_HAZARD, LINK)
    # - Known material class

    seq_list = list(seq)
    num_steps = len(seq_list)
    has_flow = 'FLOW' in seq_list
    has_energy = 'k_ENERGY' in seq_list
    has_hazard = 'h_HAZARD' in seq_list
    has_link = 'LINK' in seq_list
    has_recovery = 'RECOVERY' in seq_list

    # Skip if all UNKNOWN
    known_steps = [s for s in seq_list if s != 'UNKNOWN']
    if len(known_steps) < 2:
        continue

    score = num_steps + (has_flow * 2) + (has_energy * 2) + (has_hazard * 2) + (has_link * 2) + (has_recovery * 1)

    for m in materials:
        candidates.append({
            'sequence': seq_list,
            'material': m,
            'score': score,
            'distinctive': [s for s in ['FLOW', 'k_ENERGY', 'h_HAZARD', 'LINK', 'RECOVERY'] if s in seq_list]
        })

# Sort by score
candidates.sort(key=lambda x: -x['score'])

print("Top candidates (by sequence distinctiveness):")
print()
for c in candidates[:15]:
    m = c['material']
    print(f"#{m['id']:3d} {m['name']:25s} ({m['english']})")
    print(f"     Class: {m['class']}, Fire: {m['fire_degree']}")
    print(f"     Sequence: {c['sequence']}")
    print(f"     Distinctive steps: {c['distinctive'] if c['distinctive'] else 'none'}")
    print(f"     Score: {c['score']}")
    print()

# Also show sequences that differ from [AUX, e_ESCAPE]
print("=" * 70)
print("SEQUENCES DIFFERENT FROM GENERIC [AUX, e_ESCAPE]")
print("=" * 70)
print()

generic = ('AUX', 'e_ESCAPE')
different = [(seq, count) for seq, count in sorted_seqs if seq != generic]

for seq, count in different[:20]:
    materials = sequence_materials[seq]
    print(f"{list(seq)} - {count} material(s)")
    for m in materials[:3]:  # Show first 3
        print(f"  - {m['name']} ({m['english']}) [{m['class']}]")
    if len(materials) > 3:
        print(f"  ... and {len(materials)-3} more")
    print()
