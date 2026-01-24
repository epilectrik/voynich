#!/usr/bin/env python3
"""List animal candidates for reverse triangulation."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all fire degree 4 (animal) entries with procedures
animals = [r for r in data['recipes'] if r.get('fire_degree') == 4 and r.get('has_procedure')]

print('=== ANIMAL WATERS WITH PROCEDURES (Fire Degree 4) ===\n')
for r in animals:
    seq = r.get('instruction_sequence') or []
    known = [s for s in seq if s != 'UNKNOWN']
    unk_rate = (len(seq) - len(known)) / len(seq) if seq else 1.0

    print(f'#{r["id"]:3d} {r["name_german"]:20s} ({r["name_english"]})')
    print(f'     Sequence: {seq}')
    print(f'     Known steps: {len(known)}/{len(seq)} (unknown rate: {unk_rate:.0%})')
    print(f'     Summary: {r.get("procedure_summary", "")[:80]}...')
    print()

# Identify best candidates (low unknown rate, distinctive sequences)
print('\n=== BEST TRIANGULATION CANDIDATES ===')
print('(Low unknown rate + distinctive instruction patterns)\n')

scored = []
for r in animals:
    seq = r.get('instruction_sequence') or []
    known = [s for s in seq if s != 'UNKNOWN']
    if not seq:
        continue
    unk_rate = (len(seq) - len(known)) / len(seq)

    # Score: more known steps = better, unique patterns = better
    score = len(known) - (unk_rate * 5)

    # Bonus for distinctive patterns
    if 'FLOW' in known:
        score += 1  # FLOW is less common
    if 'k_ENERGY' in known:
        score += 1  # Energy step is distinctive
    if 'h_HAZARD' in known:
        score += 1  # Hazard is distinctive

    scored.append((score, r, known, unk_rate))

scored.sort(reverse=True)

for score, r, known, unk_rate in scored[:6]:
    print(f'#{r["id"]:3d} {r["name_german"]:20s} - Score: {score:.1f}')
    print(f'     Known sequence: {known}')
    print(f'     Unknown rate: {unk_rate:.0%}')
    validated = '✓ VALIDATED' if r["name_german"] == 'Hennen' else ''
    print(f'     {validated}')
    print()
