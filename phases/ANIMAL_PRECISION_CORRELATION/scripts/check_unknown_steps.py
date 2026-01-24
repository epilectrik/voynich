#!/usr/bin/env python3
"""
Why do we have UNKNOWN instruction steps in Brunschwig?
Check what actual text is being classified as UNKNOWN.
"""

import json
import sys
from pathlib import Path
from collections import Counter

# Handle Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("UNKNOWN INSTRUCTION STEPS IN BRUNSCHWIG")
print("=" * 70)
print()

# Collect all UNKNOWN steps
unknown_steps = []
all_steps = []

for material in data['materials']:
    name = material.get('name_normalized', 'unknown')
    steps = material.get('procedural_steps', [])

    for step in steps:
        instr_class = step.get('instruction_class', '')
        step_text = step.get('brunschwig_text', '')[:100]  # First 100 chars
        step_type = step.get('step_type', '')

        all_steps.append(instr_class)

        if instr_class == 'UNKNOWN':
            unknown_steps.append({
                'material': name,
                'step_type': step_type,
                'text': step_text
            })

# Summary
print(f"Total steps extracted: {len(all_steps)}")
print()

# Count by class
class_counts = Counter(all_steps)
print("Instruction class distribution:")
for cls, count in class_counts.most_common():
    pct = count / len(all_steps) * 100
    print(f"  {cls}: {count} ({pct:.1f}%)")

print()
print("-" * 70)
print(f"UNKNOWN steps: {len(unknown_steps)} ({len(unknown_steps)/len(all_steps)*100:.1f}%)")
print("-" * 70)
print()

# Show sample UNKNOWN steps
print("Sample UNKNOWN steps (what text failed to classify?):")
print()

for step in unknown_steps[:15]:
    print(f"Material: {step['material']}")
    print(f"Step type: {step['step_type']}")
    print(f"Text: {step['text']}...")
    print()

# Check if UNKNOWN correlates with step_type
print("-" * 70)
print("UNKNOWN by step_type:")
print("-" * 70)
step_type_counts = Counter(s['step_type'] for s in unknown_steps)
for st, count in step_type_counts.most_common():
    print(f"  {st}: {count}")
