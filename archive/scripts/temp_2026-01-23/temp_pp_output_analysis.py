#!/usr/bin/env python3
"""Detailed analysis of what PP atoms correlate with in Brunschwig."""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load data
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

# What does each product type actually mean in Brunschwig?
print("="*70)
print("BRUNSCHWIG PRODUCT TYPE DEFINITIONS")
print("="*70)

product_type_info = {
    'WATER_GENTLE': {
        'fire_degree': 1,
        'description': 'Balneum marie (water bath), gentlest heat',
        'output': 'Delicate waters from sensitive materials',
        'examples': []
    },
    'WATER_STANDARD': {
        'fire_degree': 2,
        'description': 'Standard alembic distillation',
        'output': 'Most herbal waters',
        'examples': []
    },
    'OIL_RESIN': {
        'fire_degree': 3,
        'description': 'Higher heat, oil extraction',
        'output': 'Oils, resins, aromatic compounds',
        'examples': []
    },
    'PRECISION': {
        'fire_degree': 4,
        'description': 'Highest precision, animal materials',
        'output': 'Animal products, dangerous materials, precision work',
        'examples': []
    }
}

# Categorize recipes
for recipe in recipes:
    fd = recipe.get('fire_degree', 2)
    mc = recipe.get('material_class', 'herb')
    name = recipe.get('name_english', 'Unknown')

    if fd == 4 or mc == 'animal':
        ptype = 'PRECISION'
    elif fd == 3:
        ptype = 'OIL_RESIN'
    elif fd == 1:
        ptype = 'WATER_GENTLE'
    else:
        ptype = 'WATER_STANDARD'

    product_type_info[ptype]['examples'].append({
        'name': name,
        'material_class': mc,
        'fire_degree': fd,
        'has_procedure': recipe.get('has_procedure', False),
        'key_uses': (recipe.get('key_uses') or [])[:3]
    })

for ptype, info in product_type_info.items():
    print(f"\n{ptype}:")
    print(f"  Fire degree: {info['fire_degree']}")
    print(f"  Description: {info['description']}")
    print(f"  Output: {info['output']}")
    print(f"  Recipe count: {len(info['examples'])}")

    # Show material class distribution
    mc_dist = Counter(e['material_class'] for e in info['examples'])
    print(f"  Material classes: {dict(mc_dist.most_common(5))}")

    # Show example recipes
    print(f"  Examples:")
    for ex in info['examples'][:5]:
        print(f"    - {ex['name']} ({ex['material_class']}): {ex['key_uses']}")

# Now show what makes each type DISTINCT in terms of Brunschwig properties
print("\n" + "="*70)
print("WHAT DISTINGUISHES EACH TYPE IN BRUNSCHWIG")
print("="*70)

for ptype, info in product_type_info.items():
    examples = info['examples']
    if not examples:
        continue

    print(f"\n{ptype} ({len(examples)} recipes):")

    # Material class breakdown
    mc_dist = Counter(e['material_class'] for e in examples)
    print(f"  Material classes: {dict(mc_dist)}")

    # Has procedure rate
    has_proc = sum(1 for e in examples if e['has_procedure'])
    print(f"  Has procedure: {has_proc}/{len(examples)} ({100*has_proc/len(examples):.0f}%)")

    # Common uses
    all_uses = []
    for e in examples:
        all_uses.extend(e['key_uses'])
    use_dist = Counter(all_uses)
    print(f"  Common uses: {dict(use_dist.most_common(5))}")

# Key insight
print("\n" + "="*70)
print("KEY INSIGHT")
print("="*70)
print("""
The product types differ primarily in:

1. WATER_GENTLE (fire=1): Sensitive materials requiring gentle heat
   - Delicate flowers, easily damaged compounds
   - Output: Subtle aromatic waters

2. WATER_STANDARD (fire=2): The workhorse category
   - Most herbs, standard materials
   - Output: Standard herbal waters

3. OIL_RESIN (fire=3): High-heat extraction
   - Resinous materials, woody plants
   - Output: Oils, essential compounds, concentrated preparations

4. PRECISION (fire=4 or animal): Special handling
   - Animal materials (require different chemistry)
   - Dangerous/toxic materials (require precise control)
   - Output: Specialized preparations

So when Test 3 found:
- 'e' enriched in WATER_STANDARD
- 'ol' enriched in PRECISION

This suggests:
- 'e' may encode compatibility with standard aqueous processing
- 'ol' may encode compatibility with precision/special handling
""")
