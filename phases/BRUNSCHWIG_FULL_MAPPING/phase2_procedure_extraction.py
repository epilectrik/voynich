#!/usr/bin/env python3
"""
PHASE 2: PROCEDURAL SKELETON EXTRACTION

For each material, extract the distillation procedure as a step sequence.

Method:
1. Load materials database from Phase 1
2. For each material, find its entry in the OCR text
3. Extract the distillation instructions section
4. Parse into discrete procedural steps
5. Count uses (A, B, C, etc.)
"""

import re
import json
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Patterns for finding procedural content
DISTILLATION_PATTERNS = [
    # "Das beste teyl und zyt syner distillierung/brennung ist..."
    r'[Dd]as\s+be[sſ]te\s+te[iy]l.*?(?:di[sſ]tillier|brenn)',
    # "gebrannt/gedistilliert im end des..."
    r'ge(?:bꝛant|diſtilliert|brennt)\s+(?:im|in)\s+',
    # "distilliere/brenne..."
    r'(?:di[sſ]tillier|brenn)[eẽ]?\s+',
]

# Patterns for uses (A, B, C, etc.)
USE_PATTERN = re.compile(r'[A-Z]\s+[A-Z][a-zäöüßꝛſ]+\s+wa[sſ][sſ]er')

# Step type keywords
STEP_KEYWORDS = {
    'PREPARATION': ['hack', 'schneid', 'stoß', 'zerklein', 'wasch', 'sammel', 'nimm'],
    'HEATING': ['setz', 'thu', 'leg', 'balneum', 'feuer', 'warm', 'hitz', 'koch', 'sied'],
    'MONITORING': ['wart', 'schau', 'sieh', 'acht', 'farb', 'riech'],
    'COLLECTION': ['nimm ab', 'fang', 'sammel', 'behalt', 'gieß'],
    'RECOVERY': ['wenn', 'so', 'aber', 'vermeide', 'hüt'],
}

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 2: PROCEDURAL SKELETON EXTRACTION")
print("=" * 70)
print()

# Load materials database
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials from Phase 1")

# Load OCR text
with open('sources/brunschwig_1500_text.txt', 'r', encoding='utf-8') as f:
    ocr_lines = f.readlines()

print(f"Loaded {len(ocr_lines)} lines from OCR text")
print()

# ============================================================
# EXTRACT ENTRY BOUNDARIES
# ============================================================

print("=" * 70)
print("EXTRACTING ENTRY BOUNDARIES")
print("=" * 70)
print()

def find_entry_end(start_line, lines, max_lines=200):
    """Find where the current entry ends (next entry starts)."""
    water_pattern = re.compile(r'^[A-Z][a-zäöüßꝛſ]+\s+wa[sſ][sſ]er[.\s]')

    for i in range(1, min(max_lines, len(lines) - start_line)):
        line = lines[start_line + i]
        if water_pattern.match(line.strip()):
            return start_line + i - 1

    return start_line + max_lines

def extract_entry_text(start_line, lines):
    """Extract the full text of an entry."""
    end_line = find_entry_end(start_line, lines)
    entry_lines = lines[start_line:end_line + 1]
    return ' '.join(line.strip() for line in entry_lines)

# ============================================================
# EXTRACT PROCEDURAL STEPS
# ============================================================

def classify_step(text):
    """Classify a step based on keywords."""
    text_lower = text.lower()

    for step_type, keywords in STEP_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return step_type

    return 'OTHER'

def extract_procedures(entry_text):
    """Extract procedural steps from entry text."""
    procedures = []

    # Look for distillation instruction section
    # Pattern: "Das beste teyl..." or similar
    distill_match = None
    for pattern in DISTILLATION_PATTERNS:
        match = re.search(pattern, entry_text, re.IGNORECASE)
        if match:
            distill_match = match
            break

    if distill_match:
        # Extract the section after the match
        start_pos = distill_match.start()
        # Find the end (next use marker or end of relevant section)
        section = entry_text[start_pos:start_pos + 500]

        # Split into potential steps
        # Steps often separated by periods or "und"
        step_parts = re.split(r'[.]\s*(?=[A-Z])|(?:\s+und\s+)', section)

        for i, part in enumerate(step_parts[:10]):  # Limit to 10 steps
            part = part.strip()
            if len(part) > 10:  # Skip very short fragments
                step_type = classify_step(part)
                procedures.append({
                    'step_number': i + 1,
                    'brunschwig_text': part[:200],  # Truncate long text
                    'step_type': step_type,
                    'instruction_class': '',  # To be filled in Phase 3
                    'hazard_exposure': 'NONE',
                    'intervention_required': False,
                    'recovery_permitted': True
                })

    return procedures

def count_uses(entry_text):
    """Count the number of uses (A, B, C, etc.) in the entry."""
    # Pattern: letter followed by material name + "wasser"
    uses = re.findall(r'[A-P]\s+[A-Z]', entry_text)
    return len(set(uses))

# ============================================================
# PROCESS ALL MATERIALS
# ============================================================

print("=" * 70)
print("PROCESSING MATERIALS")
print("=" * 70)
print()

processed_count = 0
procedure_count = 0

for i, material in enumerate(materials):
    start_line = material['source_reference']['line_start']

    # Skip if line is out of range
    if start_line >= len(ocr_lines):
        continue

    # Extract entry text
    entry_text = extract_entry_text(start_line, ocr_lines)

    # Extract procedures
    procedures = extract_procedures(entry_text)

    # Count uses
    uses_count = count_uses(entry_text)

    # Update material
    material['procedural_steps'] = procedures
    material['uses_count'] = uses_count
    material['entry_text_length'] = len(entry_text)

    if procedures:
        material['extraction_status'] = 'EXTRACTED'
        processed_count += 1
        procedure_count += len(procedures)
    else:
        material['extraction_status'] = 'NO_PROCEDURE_FOUND'

    # Progress indicator
    if (i + 1) % 100 == 0:
        print(f"Processed {i + 1}/{len(materials)} materials...")

print()
print(f"Materials with procedures extracted: {processed_count}/{len(materials)}")
print(f"Total procedural steps extracted: {procedure_count}")
print()

# ============================================================
# STATISTICS
# ============================================================

print("=" * 70)
print("EXTRACTION STATISTICS")
print("=" * 70)
print()

# Steps per material distribution
steps_dist = {}
for m in materials:
    n = len(m['procedural_steps'])
    steps_dist[n] = steps_dist.get(n, 0) + 1

print("Procedural steps per material:")
for n in sorted(steps_dist.keys()):
    print(f"  {n} steps: {steps_dist[n]} materials")

print()

# Uses distribution
uses_dist = {}
for m in materials:
    u = m['uses_count']
    bucket = '0' if u == 0 else '1-5' if u <= 5 else '6-10' if u <= 10 else '11+'
    uses_dist[bucket] = uses_dist.get(bucket, 0) + 1

print("Uses per material:")
for bucket in ['0', '1-5', '6-10', '11+']:
    print(f"  {bucket}: {uses_dist.get(bucket, 0)} materials")

print()

# Step types distribution
step_types = {}
for m in materials:
    for step in m['procedural_steps']:
        st = step['step_type']
        step_types[st] = step_types.get(st, 0) + 1

print("Step types extracted:")
for st, count in sorted(step_types.items(), key=lambda x: -x[1]):
    print(f"  {st}: {count}")

# ============================================================
# SAVE UPDATED DATABASE
# ============================================================

print()
print("=" * 70)
print("SAVING UPDATED DATABASE")
print("=" * 70)
print()

# Update summary
data['summary']['materials_with_procedures'] = processed_count
data['summary']['total_steps_extracted'] = procedure_count
data['summary']['step_types'] = step_types

# Save
output_path = Path('data/brunschwig_materials_master.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated database saved to {output_path}")

# ============================================================
# SAMPLE OUTPUT
# ============================================================

print()
print("=" * 70)
print("SAMPLE ENTRIES WITH PROCEDURES")
print("=" * 70)
print()

# Find materials with good procedure extraction
good_samples = [m for m in materials if len(m['procedural_steps']) >= 3][:5]

for m in good_samples:
    print(f"{m['recipe_id']}: {m['name_german']}")
    print(f"  Product type: {m['predicted_product_type']}")
    print(f"  Uses: {m['uses_count']}")
    print(f"  Steps: {len(m['procedural_steps'])}")
    for step in m['procedural_steps'][:3]:
        text_preview = step['brunschwig_text'][:60].replace('\n', ' ')
        print(f"    {step['step_number']}. [{step['step_type']}] {text_preview}...")
    print()
