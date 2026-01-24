#!/usr/bin/env python3
"""
Explore Brunschwig instruction sequences.
"""

import json
from collections import Counter

with open('data/brunschwig_complete.json', encoding='utf-8') as f:
    data = json.load(f)
recipes = data['recipes']

# Check instruction_sequence field
print("=" * 60)
print("INSTRUCTION SEQUENCES")
print("=" * 60)

seq_counter = Counter()
for r in recipes:
    seq = r.get('instruction_sequence')
    if seq:
        seq_key = tuple(seq) if isinstance(seq, list) else seq
        seq_counter[seq_key] += 1

print(f"\nUnique instruction sequences: {len(seq_counter)}")
print("\nMost common sequences:")
for seq, cnt in seq_counter.most_common(15):
    print(f"  {cnt:3d}x: {list(seq) if isinstance(seq, tuple) else seq}")

# Show examples by material class
print("\n" + "=" * 60)
print("SEQUENCES BY MATERIAL CLASS")
print("=" * 60)

for cls in ['animal', 'animal_blood', 'herb', 'flower']:
    cls_recipes = [r for r in recipes if r.get('material_class') == cls]
    if cls_recipes:
        print(f"\n{cls.upper()} ({len(cls_recipes)} recipes):")
        for r in cls_recipes[:5]:
            seq = r.get('instruction_sequence', [])
            print(f"  {r['name_english']}: {seq}")

# Show fire degree vs sequence correlation
print("\n" + "=" * 60)
print("SEQUENCES BY FIRE DEGREE")
print("=" * 60)

for degree in [1, 2, 3, 4]:
    deg_recipes = [r for r in recipes if r.get('fire_degree') == degree]
    seq_counts = Counter()
    for r in deg_recipes:
        seq = r.get('instruction_sequence')
        if seq:
            seq_key = tuple(seq) if isinstance(seq, list) else seq
            seq_counts[seq_key] += 1
    print(f"\nFIRE DEGREE {degree} ({len(deg_recipes)} recipes):")
    for seq, cnt in seq_counts.most_common(5):
        print(f"  {cnt}x: {list(seq) if isinstance(seq, tuple) else seq}")
