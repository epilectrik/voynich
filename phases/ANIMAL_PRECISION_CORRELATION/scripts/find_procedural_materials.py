#!/usr/bin/env python3
"""
Find non-animal materials with specific procedures in Brunschwig.
Test hypothesis: Only materials with unique procedures get specific tokens.
"""

import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

# Load Brunschwig data
with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find materials with actual procedures (non-empty instruction_sequence)
materials_with_procedures = []

for material in data.get('materials', []):
    name = material.get('name_normalized', 'unknown')
    status = material.get('extraction_status', '')
    instr = material.get('instruction_sequence', [])
    mat_class = material.get('material_source', 'unknown')
    fire_degree = material.get('fire_degree')

    # PP profile is nested under regime_assignment
    regime = material.get('regime_assignment', {})
    pp_profile = regime.get('predicted_prefix_profile', {})
    predicted_regime = regime.get('final_regime')

    if instr and len(instr) > 0:
        materials_with_procedures.append({
            'name': name,
            'class': mat_class,
            'status': status,
            'n_steps': len(instr),
            'fire_degree': fire_degree,
            'predicted_regime': predicted_regime,
            'pp_profile': pp_profile,
            'steps': instr[:3]  # First 3 steps
        })

print('=' * 70)
print('MATERIALS WITH ACTUAL PROCEDURES (instruction_sequence not empty)')
print('=' * 70)
print()

# Group by class
by_class = defaultdict(list)
for m in materials_with_procedures:
    by_class[m['class']].append(m)

for cls in sorted(by_class.keys()):
    print(f'{cls.upper()}: {len(by_class[cls])} materials')
    for m in by_class[cls][:3]:  # First 3 per class
        print(f'  - {m["name"]}: {m["n_steps"]} steps, fire={m["fire_degree"]}, regime={m["predicted_regime"]}')
        if m['pp_profile']:
            top_pp = sorted(m['pp_profile'].items(), key=lambda x: -x[1])[:3]
            print(f'    PP profile: {dict(top_pp)}')
    if len(by_class[cls]) > 3:
        print(f'  ... and {len(by_class[cls]) - 3} more')
    print()

# Focus on non-animal materials with unique procedures
print('=' * 70)
print('BEST CANDIDATES FOR TRIANGULATION TEST')
print('=' * 70)
print()
print('Looking for: non-animal, specific procedure, fire_degree=4 (high precision)')
print()

# First, show fire_degree distribution
print('Fire degree distribution among procedural materials:')
fire_dist = defaultdict(list)
for m in materials_with_procedures:
    fire_dist[m['fire_degree']].append(m)

for fd in sorted(fire_dist.keys()):
    print(f'  Fire degree {fd}: {len(fire_dist[fd])} materials')
print()

# Best candidates: fire_degree 4 (REGIME_4 = high precision)
# These are the materials most likely to have unique tokens (like animals)
print('=' * 70)
print('FIRE DEGREE 4 MATERIALS (REGIME_4 - High Precision)')
print('=' * 70)
print()

fire4_materials = fire_dist.get(4, [])
for m in fire4_materials:
    print(f'{m["name"]} ({m["class"]}):')
    print(f'  Regime: {m["predicted_regime"]}')
    print(f'  Steps: {m["n_steps"]}')
    print(f'  PP profile: {m["pp_profile"]}')
    print(f'  Instruction sequence: {m["steps"]}')
    print()

# Also check for uniquely long procedures
print('=' * 70)
print('MATERIALS WITH LONGEST PROCEDURES (5+ steps)')
print('=' * 70)
print()

long_procedures = [m for m in materials_with_procedures if m['n_steps'] >= 5]
long_procedures.sort(key=lambda x: -x['n_steps'])

for m in long_procedures[:10]:
    print(f'{m["name"]} ({m["class"]}): {m["n_steps"]} steps')
    print(f'  Fire: {m["fire_degree"]}, Regime: {m["predicted_regime"]}')
    print(f'  PP profile: {m["pp_profile"]}')
    print()
