#!/usr/bin/env python3
"""Check why 312 materials don't have procedures extracted."""

import json
import re
from pathlib import Path

# Load materials
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']

# Load OCR text
with open('sources/brunschwig_1500_text.txt', 'r', encoding='utf-8') as f:
    ocr_lines = f.readlines()

print("=" * 70)
print("COVERAGE ANALYSIS")
print("=" * 70)
print()

with_proc = [m for m in materials if m.get('procedural_steps')]
without_proc = [m for m in materials if not m.get('procedural_steps')]

print(f"Total materials: {len(materials)}")
print(f"With procedures: {len(with_proc)} ({100*len(with_proc)/len(materials):.1f}%)")
print(f"Without procedures: {len(without_proc)} ({100*len(without_proc)/len(materials):.1f}%)")
print()

# Check unique normalized names
unique_names = set(m['name_normalized'] for m in materials)
print(f"Unique normalized names: {len(unique_names)}")
print()

# Check if missing ones have entry text
print("Checking materials WITHOUT procedures...")
print()

# Pattern that indicates procedural content
proc_patterns = [
    r'di[sſ]tillier',
    r'brenn[eẽ]?',
    r'feuer',
    r'balneum',
    r'wa[sſ][sſ]erbad',
    r'be[sſ]te\s+te[iy]l',
]

has_distill_mention = 0
no_distill_mention = 0
short_entries = 0

for m in without_proc:
    line_num = m['source_reference']['line_start']

    # Get entry text (next 50 lines)
    if line_num < len(ocr_lines):
        entry_text = ' '.join(ocr_lines[line_num:min(line_num+50, len(ocr_lines))])
        entry_length = len(entry_text)

        # Check for procedural keywords
        has_proc_keywords = False
        for pattern in proc_patterns:
            if re.search(pattern, entry_text, re.IGNORECASE):
                has_proc_keywords = True
                break

        if has_proc_keywords:
            has_distill_mention += 1
        else:
            no_distill_mention += 1

        if entry_length < 200:
            short_entries += 1

print(f"Have distillation keywords but no extracted procedure: {has_distill_mention}")
print(f"No distillation keywords found: {no_distill_mention}")
print(f"Very short entries (<200 chars): {short_entries}")
print()

# Sample entries that SHOULD have procedures but don't
print("=" * 70)
print("SAMPLE: Entries WITH distillation keywords but NO procedure extracted")
print("=" * 70)
print()

count = 0
for m in without_proc:
    if count >= 5:
        break

    line_num = m['source_reference']['line_start']
    if line_num < len(ocr_lines):
        entry_text = ' '.join(ocr_lines[line_num:min(line_num+30, len(ocr_lines))])

        for pattern in proc_patterns:
            if re.search(pattern, entry_text, re.IGNORECASE):
                print(f"{m['recipe_id']}: {m['name_german']}")
                print(f"  Line {line_num}")
                print(f"  Text preview: {entry_text[:200]}...")
                print()
                count += 1
                break

# Check the reference guide count
print("=" * 70)
print("REFERENCE GUIDE COMPARISON")
print("=" * 70)
print()

# Count by category in reference
ref_categories = {
    'cold_moist_flower': 13,
    'hot_flower': 14,
    'leaf': 6,
    'fruit': 10,
    'moderate_herb': 11,
    'dangerous_herb': 4,
    'hot_dry_herb': 21,
    'moist_root': 4,
    'hot_dry_root': 6,
    'animal': 9
}

print("Expected from reference guide:")
total_ref = sum(ref_categories.values())
print(f"  Total documented materials: ~{total_ref}")
print()

print("Extracted by category:")
cat_counts = {}
for m in materials:
    cat = m['material_source']
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

for cat in sorted(cat_counts.keys()):
    ref = ref_categories.get(cat, '?')
    print(f"  {cat}: {cat_counts[cat]} extracted (reference: {ref})")

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()
print(f"We extracted {len(materials)} entries but ~{total_ref} were documented in reference.")
print(f"This means {len(materials) - total_ref} are duplicates/spelling variants.")
print()
print(f"Of the {len(with_proc)} with procedures, these represent the core recipes.")
print(f"The {has_distill_mention} missing procedures with distillation keywords")
print(f"could be recovered with improved extraction patterns.")
