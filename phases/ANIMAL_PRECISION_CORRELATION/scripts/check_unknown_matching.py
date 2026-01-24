#!/usr/bin/env python3
"""
Audit: Are we being careful with UNKNOWN steps in instruction matching?

Problem: If UNKNOWN means "we don't know what this is," how can we use it
to match against Voynich structures?

Check:
1. How many materials have UNKNOWN in their sequence?
2. What are we actually matching on for each material?
3. Are we using UNKNOWN as a positive signal (bad) or ignoring it (ok)?
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("AUDIT: UNKNOWN Steps in Instruction Matching")
print("=" * 70)
print()

# Check all REGIME_4 materials (the ones we're triangulating)
regime4_materials = []
for m in data['materials']:
    regime = m.get('regime_assignment', {})
    if regime.get('final_regime') == 'REGIME_4':
        regime4_materials.append({
            'name': m.get('name_normalized'),
            'class': m.get('material_source'),
            'instr': m.get('instruction_sequence', [])
        })

print(f"REGIME_4 materials: {len(regime4_materials)}")
print()

# Count UNKNOWN usage
has_unknown = []
no_unknown = []

for m in regime4_materials:
    if 'UNKNOWN' in m['instr']:
        has_unknown.append(m)
    else:
        no_unknown.append(m)

print(f"Materials WITH UNKNOWN in sequence: {len(has_unknown)}")
print(f"Materials WITHOUT UNKNOWN: {len(no_unknown)}")
print()

print("-" * 70)
print("Materials WITH UNKNOWN:")
print("-" * 70)
for m in has_unknown:
    seq = ' -> '.join(m['instr'])
    known_steps = [s for s in m['instr'] if s != 'UNKNOWN']
    print(f"  {m['name']} ({m['class']})")
    print(f"    Full sequence: {seq}")
    print(f"    KNOWN steps only: {known_steps}")
    print()

print("-" * 70)
print("Materials WITHOUT UNKNOWN (clean sequences):")
print("-" * 70)
for m in no_unknown:
    seq = ' -> '.join(m['instr']) if m['instr'] else '(no sequence)'
    print(f"  {m['name']} ({m['class']}): {seq}")
print()

# The key question: What are we ACTUALLY matching on?
print("=" * 70)
print("WHAT ARE WE ACTUALLY MATCHING ON?")
print("=" * 70)
print()

print("For each material, the KNOWN (non-UNKNOWN) discriminating features:")
print()

for m in regime4_materials:
    known = [s for s in m['instr'] if s != 'UNKNOWN']
    n_unknown = m['instr'].count('UNKNOWN')
    n_known = len(known)

    if n_known == 0 and n_unknown > 0:
        status = "DANGER: Only UNKNOWN steps - no real signal!"
    elif n_known == 0:
        status = "WARNING: No sequence at all"
    elif n_unknown > n_known:
        status = "WEAK: More UNKNOWN than known"
    else:
        status = "OK: Has discriminating features"

    print(f"{m['name']}: {status}")
    print(f"  Known: {known}")
    print(f"  Unknown count: {n_unknown}")
    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

all_known = []
for m in regime4_materials:
    known = [s for s in m['instr'] if s != 'UNKNOWN']
    all_known.extend(known)

print("Usable (KNOWN) instruction classes across REGIME_4:")
known_counts = Counter(all_known)
for cls, count in known_counts.most_common():
    print(f"  {cls}: {count}")

print()
print("CONCLUSION:")
print("  We should ONLY match on KNOWN instruction classes.")
print("  UNKNOWN should be treated as 'no information', not as a signal.")
print("  For materials with ONLY UNKNOWN steps, we cannot use instruction")
print("  sequence for discrimination - only regime and class priors.")
