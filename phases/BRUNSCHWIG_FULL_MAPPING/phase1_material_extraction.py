#!/usr/bin/env python3
"""
PHASE 1: MATERIAL EXTRACTION

Extract all plant/material entries from Brunschwig OCR text into structured format.

Method:
1. Load reference guide for known material names
2. Search OCR text for "X wasser" patterns
3. Extract entry boundaries
4. Parse names, descriptions, and use counts
5. Output to JSON
"""

import re
import json
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Known material categories from reference guide
MATERIAL_CATEGORIES = {
    'cold_moist_flower': {
        'fire_degree': 1,
        'shelf_life': '2 years',
        'materials': [
            'Ibisch', 'Ochsenzung', 'Meyblumen', 'gilgen', 'Bappeln',
            'Burretsch', 'Bonen', 'violen', 'Holder', 'rosen', 'See blumen',
            'Klapper rosen', 'Magdot'
        ]
    },
    'hot_flower': {
        'fire_degree': 2,
        'shelf_life': '3 years',
        'materials': [
            'Camillen', 'Centaurien', 'nesseln', 'Dillen', 'Genserich',
            'Lauender', 'Rosmarin', 'Meygeronen', 'Salbey', 'Johans',
            'Linden', 'Pfirlich', 'Schlehen', 'wilgen'
        ]
    },
    'leaf': {
        'fire_degree': 2,
        'shelf_life': '3 years',
        'materials': [
            'loub', 'Ebhoy', 'Esche', 'Rebloub', 'Sevenboum', 'Tamariscus'
        ]
    },
    'fruit': {
        'fire_degree': 1,
        'shelf_life': '1 year',
        'materials': [
            'ber', 'Bonen', 'Ertber', 'erbeis', 'Pflumen', 'kirsen',
            'Mulber', 'Nuß', 'opfel', 'bieren'
        ]
    },
    'moderate_herb': {
        'fire_degree': 2,
        'shelf_life': '2 years',
        'materials': [
            'Ampffer', 'Burretsch', 'Brunellen', 'Brunnkressen', 'Cle',
            'Cabos', 'Fenchel', 'Garb', 'Gunsel', 'Latich', 'Peterling'
        ]
    },
    'dangerous_herb': {
        'fire_degree': 1,
        'shelf_life': '1-3 years',
        'materials': [
            'Alrunen', 'Bilsen', 'Burtzeln', 'Wuntscherling'
        ]
    },
    'hot_dry_herb': {
        'fire_degree': 3,
        'shelf_life': '3 years',
        'materials': [
            'Andorn', 'Alant', 'Agrimonien', 'Aron', 'Bibinell', 'Boley',
            'Basilien', 'Cardo', 'Gamander', 'Hopff', 'Isop', 'Lauendel',
            'Mellissen', 'Muntz', 'Orecht', 'Quendel', 'Ruten', 'Rosmarinen',
            'Sanickel'
        ]
    },
    'moist_root': {
        'fire_degree': 2,
        'shelf_life': '1 year',
        'materials': [
            'wurtzel', 'Rettich', 'Ruben', 'Walwurtz'
        ]
    },
    'hot_dry_root': {
        'fire_degree': 3,
        'shelf_life': '2 years',
        'materials': [
            'Alant wurtzel', 'Angelica', 'Bibinellen wurtzel', 'gilgen wurtzel',
            'Nessel wurtzel', 'Sparigen'
        ]
    },
    'animal': {
        'fire_degree': 4,
        'shelf_life': '1 year',
        'materials': [
            'blut', 'Eyer', 'Frosch', 'Hennen', 'Igels', 'Krebs',
            'milch', 'Honig', 'har'
        ]
    }
}

# Build search patterns from materials
def build_search_patterns():
    """Build regex patterns for finding material entries."""
    patterns = []

    # Pattern 1: "X wasser" or "X waszer" entries
    # Early modern German uses various spellings
    patterns.append(r'([A-Z][a-zäöüß]+(?:\s+[a-zäöüß]+)?)\s+wa[sſ][sſ]er')

    # Pattern 2: Entries starting with capital letter followed by description
    patterns.append(r'^([A-Z][a-zäöüßꝛꝛ]+)\s+wa[sſ][sſ]er\.')

    return patterns

# ============================================================
# LOAD OCR TEXT
# ============================================================

print("=" * 70)
print("PHASE 1: MATERIAL EXTRACTION")
print("=" * 70)
print()

# Load OCR text
ocr_path = Path('sources/brunschwig_1500_text.txt')
with open(ocr_path, 'r', encoding='utf-8') as f:
    ocr_lines = f.readlines()

print(f"Loaded {len(ocr_lines)} lines from OCR text")

# Focus on Part 2 (alphabetical encyclopedia) - lines ~3566-21000
PART2_START = 3566
PART2_END = 21000

part2_text = ''.join(ocr_lines[PART2_START:PART2_END])
part2_lines = ocr_lines[PART2_START:PART2_END]

print(f"Part 2 (alphabetical encyclopedia): lines {PART2_START}-{PART2_END}")
print()

# ============================================================
# EXTRACT MATERIAL ENTRIES
# ============================================================

print("=" * 70)
print("EXTRACTING MATERIAL ENTRIES")
print("=" * 70)
print()

# Pattern to find "X wasser" entries (handles OCR variations)
# The ſ character is common in OCR'd early modern German
water_pattern = re.compile(
    r'([A-Za-zäöüßꝛ]+)\s+wa[sſ][sſ]er[.\s]',
    re.IGNORECASE
)

# Find all potential water entries
entries_found = []
current_line_num = PART2_START

for i, line in enumerate(part2_lines):
    line_num = PART2_START + i
    matches = water_pattern.findall(line)

    for match in matches:
        # Clean up the match
        material_name = match.strip()

        # Skip very short matches (likely OCR artifacts)
        if len(material_name) < 3:
            continue

        # Skip common false positives
        if material_name.lower() in ['das', 'ein', 'dem', 'den', 'der', 'die', 'und', 'von']:
            continue

        entries_found.append({
            'raw_name': material_name,
            'line_number': line_num,
            'line_text': line.strip()[:100]
        })

print(f"Found {len(entries_found)} potential water entries")
print()

# ============================================================
# DEDUPLICATE AND CLASSIFY
# ============================================================

print("=" * 70)
print("DEDUPLICATING AND CLASSIFYING")
print("=" * 70)
print()

# Normalize names for deduplication
def normalize_name(name):
    """Normalize early modern German spelling."""
    name = name.lower()
    # Common OCR/spelling variations
    name = name.replace('ſ', 's')
    name = name.replace('ꝛ', 'r')
    name = name.replace('ů', 'u')
    name = name.replace('ü', 'u')
    name = name.replace('ö', 'o')
    name = name.replace('ä', 'a')
    name = name.replace('ß', 'ss')
    return name

# Group by normalized name, keep first occurrence
seen_normalized = {}
unique_entries = []

for entry in entries_found:
    norm = normalize_name(entry['raw_name'])
    if norm not in seen_normalized:
        seen_normalized[norm] = entry
        unique_entries.append(entry)

print(f"Unique materials after deduplication: {len(unique_entries)}")
print()

# Classify by category
def classify_material(name):
    """Classify material into category based on name patterns."""
    norm = normalize_name(name)

    for category, info in MATERIAL_CATEGORIES.items():
        for material in info['materials']:
            if normalize_name(material) in norm or norm in normalize_name(material):
                return {
                    'category': category,
                    'fire_degree': info['fire_degree'],
                    'shelf_life': info['shelf_life']
                }

    # Default classification based on name patterns
    if 'blut' in norm or 'eyer' in norm or 'milch' in norm:
        return {'category': 'animal', 'fire_degree': 4, 'shelf_life': '1 year'}
    elif 'wurtzel' in norm:
        return {'category': 'root', 'fire_degree': 2, 'shelf_life': '2 years'}
    elif 'blumen' in norm or 'blut' in norm:
        return {'category': 'flower', 'fire_degree': 1, 'shelf_life': '2 years'}
    elif 'loub' in norm:
        return {'category': 'leaf', 'fire_degree': 2, 'shelf_life': '3 years'}
    else:
        return {'category': 'herb', 'fire_degree': 2, 'shelf_life': '2 years'}

# Add classification to entries
for entry in unique_entries:
    classification = classify_material(entry['raw_name'])
    entry.update(classification)

# ============================================================
# BUILD MATERIALS DATABASE
# ============================================================

print("=" * 70)
print("BUILDING MATERIALS DATABASE")
print("=" * 70)
print()

# Map fire degree to REGIME and product type
DEGREE_TO_REGIME = {
    1: ('REGIME_2', 'WATER_GENTLE'),
    2: ('REGIME_1', 'WATER_STANDARD'),
    3: ('REGIME_3', 'OIL_RESIN'),
    4: ('REGIME_4', 'PRECISION')
}

materials_database = []

for i, entry in enumerate(unique_entries):
    regime, product_type = DEGREE_TO_REGIME.get(entry['fire_degree'], ('REGIME_1', 'WATER_STANDARD'))

    material = {
        'recipe_id': f'BRU-{i+1:03d}',
        'name_german': entry['raw_name'],
        'name_normalized': normalize_name(entry['raw_name']),
        'name_latin': '',  # To be filled in Phase 2
        'name_english': '',  # To be filled in Phase 2
        'material_source': entry['category'],
        'fire_degree': entry['fire_degree'],
        'shelf_life': entry['shelf_life'],
        'predicted_regime': regime,
        'predicted_product_type': product_type,
        'source_reference': {
            'line_start': entry['line_number'],
            'line_text_preview': entry['line_text']
        },
        'procedural_steps': [],  # To be filled in Phase 2
        'uses_count': 0,  # To be counted in Phase 2
        'extraction_status': 'PENDING'
    }

    materials_database.append(material)

# ============================================================
# STATISTICS
# ============================================================

print("Materials by category:")
category_counts = {}
for m in materials_database:
    cat = m['material_source']
    category_counts[cat] = category_counts.get(cat, 0) + 1

for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print()
print("Materials by fire degree:")
degree_counts = {}
for m in materials_database:
    deg = m['fire_degree']
    degree_counts[deg] = degree_counts.get(deg, 0) + 1

for deg in sorted(degree_counts.keys()):
    regime, product = DEGREE_TO_REGIME[deg]
    print(f"  Degree {deg} ({regime}/{product}): {degree_counts[deg]}")

print()
print("Materials by predicted product type:")
product_counts = {}
for m in materials_database:
    prod = m['predicted_product_type']
    product_counts[prod] = product_counts.get(prod, 0) + 1

for prod, count in sorted(product_counts.items(), key=lambda x: -x[1]):
    print(f"  {prod}: {count}")

# ============================================================
# SAVE DATABASE
# ============================================================

print()
print("=" * 70)
print("SAVING MATERIALS DATABASE")
print("=" * 70)
print()

output_path = Path('data/brunschwig_materials_master.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

output = {
    'phase': 'phase1_material_extraction',
    'source': 'sources/brunschwig_1500_text.txt',
    'extraction_range': {
        'start_line': PART2_START,
        'end_line': PART2_END
    },
    'summary': {
        'total_materials': len(materials_database),
        'by_category': category_counts,
        'by_fire_degree': degree_counts,
        'by_product_type': product_counts
    },
    'materials': materials_database
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved {len(materials_database)} materials to {output_path}")
print()

# Also save a simple list for quick reference
list_path = Path('data/brunschwig_materials_list.txt')
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# Brunschwig Materials Extracted from OCR\n")
    f.write(f"# Total: {len(materials_database)}\n\n")

    for m in materials_database:
        f.write(f"{m['recipe_id']}: {m['name_german']} (Degree {m['fire_degree']}, {m['predicted_product_type']})\n")

print(f"Saved materials list to {list_path}")

# ============================================================
# SAMPLE OUTPUT
# ============================================================

print()
print("=" * 70)
print("SAMPLE ENTRIES (first 10)")
print("=" * 70)
print()

for m in materials_database[:10]:
    print(f"{m['recipe_id']}: {m['name_german']}")
    print(f"  Category: {m['material_source']}, Degree: {m['fire_degree']}")
    print(f"  Predicted: {m['predicted_regime']} / {m['predicted_product_type']}")
    print(f"  Line {m['source_reference']['line_start']}: {m['source_reference']['line_text_preview'][:60]}...")
    print()
