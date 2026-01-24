#!/usr/bin/env python3
"""
Find Brunschwig materials with enough KNOWN instruction steps for triangulation.

Requirements for confident decoding:
1. Has instruction sequence (not empty)
2. Has 2+ KNOWN (non-UNKNOWN) steps
3. Ideally has unique combination of instruction classes
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("DECODABLE BRUNSCHWIG MATERIALS")
print("=" * 70)
print()
print("Criteria: 2+ KNOWN (non-UNKNOWN) instruction steps")
print()

# Analyze all materials
materials = []
for m in data['materials']:
    name = m.get('name_normalized', 'unknown')
    mat_class = m.get('material_source', 'unknown')
    fire = m.get('fire_degree')
    instr = m.get('instruction_sequence', [])
    regime = m.get('regime_assignment', {}).get('final_regime')

    known_steps = [s for s in instr if s != 'UNKNOWN']
    n_known = len(known_steps)
    n_unknown = instr.count('UNKNOWN')

    if n_known >= 2:
        materials.append({
            'name': name,
            'class': mat_class,
            'fire': fire,
            'regime': regime,
            'full_seq': instr,
            'known_steps': known_steps,
            'n_known': n_known,
            'n_unknown': n_unknown,
            'signature': tuple(sorted(set(known_steps)))  # Unique instruction types
        })

print(f"Materials with 2+ KNOWN steps: {len(materials)}")
print()

# Group by signature (unique instruction combination)
by_signature = defaultdict(list)
for m in materials:
    by_signature[m['signature']].append(m)

print("-" * 70)
print("GROUPED BY INSTRUCTION SIGNATURE (unique = best for discrimination)")
print("-" * 70)
print()

# Sort signatures by how unique they are (fewer materials = more discriminative)
for sig, mats in sorted(by_signature.items(), key=lambda x: len(x[1])):
    sig_str = ', '.join(sig)
    print(f"[{sig_str}]: {len(mats)} material(s)")
    for m in mats[:5]:
        status = "DONE" if m['name'] in ['ennen', 'quuendel', 'cuendel'] else ""
        print(f"  - {m['name']} ({m['class']}, {m['regime']}) {status}")
    if len(mats) > 5:
        print(f"  ... and {len(mats) - 5} more")
    print()

# Best candidates: unique signatures with 3+ KNOWN steps
print("=" * 70)
print("BEST CANDIDATES FOR TRIANGULATION")
print("=" * 70)
print()
print("Criteria: Unique or rare signature + 3+ KNOWN steps")
print()

best = []
for m in materials:
    sig_count = len(by_signature[m['signature']])
    if m['n_known'] >= 3 and sig_count <= 3:
        best.append({
            **m,
            'sig_count': sig_count,
            'discriminability': m['n_known'] / (sig_count + 1)  # Higher = better
        })

best.sort(key=lambda x: -x['discriminability'])

print(f"{'Material':<15} {'Class':<15} {'Regime':<10} {'KNOWN Steps':<30} {'Unique?':<8}")
print("-" * 85)

for m in best[:20]:
    known_str = ', '.join(m['known_steps'])[:28]
    unique = "YES" if m['sig_count'] == 1 else f"1/{m['sig_count']}"
    done = " (DONE)" if m['name'] in ['ennen', 'quuendel', 'cuendel'] else ""
    print(f"{m['name']:<15} {m['class']:<15} {m['regime']:<10} {known_str:<30} {unique:<8}{done}")

# Already identified
print()
print("-" * 70)
print("ALREADY IDENTIFIED:")
print("-" * 70)
identified = ['ennen', 'quuendel', 'cuendel', 'frosch']
for m in materials:
    if m['name'] in identified:
        print(f"  {m['name']}: {m['known_steps']}")

# Summary by regime
print()
print("-" * 70)
print("SUMMARY BY REGIME")
print("-" * 70)
regime_counts = Counter(m['regime'] for m in materials)
for regime, count in regime_counts.most_common():
    print(f"  {regime}: {count} decodable materials")

# Animals specifically
print()
print("-" * 70)
print("ANIMALS (all should be decodable)")
print("-" * 70)
animals = [m for m in materials if m['class'] == 'animal']
for m in animals:
    known_str = ', '.join(m['known_steps'])
    done = " <-- DONE" if m['name'] in identified else ""
    print(f"  {m['name']}: [{known_str}]{done}")

# Precision herbs
print()
print("-" * 70)
print("PRECISION HERBS (REGIME_4 override)")
print("-" * 70)
precision_herbs = [m for m in materials if m['class'] in ['herb', 'hot_flower'] and m['regime'] == 'REGIME_4']
for m in precision_herbs:
    known_str = ', '.join(m['known_steps'])
    done = " <-- DONE" if m['name'] in identified else ""
    print(f"  {m['name']}: [{known_str}]{done}")
