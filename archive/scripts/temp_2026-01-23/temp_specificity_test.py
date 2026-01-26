#!/usr/bin/env python3
"""
Does RI encode SPECIFIC plants or just CATEGORIES?

If specific: ~1 RI per plant species
If categories: many plants share same RI
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

# Load Brunschwig
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

print("="*70)
print("SPECIFICITY TEST: PLANTS vs CATEGORIES")
print("="*70)

# Count unique materials in Brunschwig
unique_materials = set()
for recipe in recipes:
    name = recipe.get('name_english', '')
    if name:
        unique_materials.add(name.lower())

# Count by material class
class_counts = Counter(r.get('material_class', 'unknown') for r in recipes)

print(f"\nBrunschwig materials:")
print(f"  Total recipes: {len(recipes)}")
print(f"  Unique material names: {len(unique_materials)}")
print(f"\n  By class:")
for cls, count in class_counts.most_common():
    print(f"    {cls}: {count}")

print(f"\nVoynich vocabulary:")
print(f"  PP MIDDLEs (shared A+B): {len(pp_middles)}")
print(f"  RI MIDDLEs (A-only): {len(ri_middles)}")

# The key ratio
print(f"\nKey ratios:")
print(f"  RI MIDDLEs / Brunschwig materials: {len(ri_middles) / len(unique_materials):.2f}")
print(f"  PP MIDDLEs / Brunschwig materials: {len(pp_middles) / len(unique_materials):.2f}")

# What does this mean?
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if len(ri_middles) > len(unique_materials):
    print(f"""
RI count ({len(ri_middles)}) > Material count ({len(unique_materials)})

This suggests RI encodes MORE than just plant species:
  - Multiple RI per material (e.g., parts, preparations)
  - Or RI encodes at sub-species level
  - Or RI includes non-Brunschwig vocabulary
""")
elif len(ri_middles) < len(unique_materials) * 0.5:
    print(f"""
RI count ({len(ri_middles)}) << Material count ({len(unique_materials)})

This suggests RI encodes CATEGORIES, not specific plants:
  - Multiple materials share same RI
  - RI = category (bitter herbs, aromatic flowers, etc.)
""")
else:
    print(f"""
RI count ({len(ri_middles)}) ~ Material count ({len(unique_materials)})

This suggests RI encodes at approximately plant-species level:
  - Roughly 1:1 mapping possible
  - May be specific plants with some category grouping
""")

# Check if categories have distinct PP profiles
print("\n" + "="*70)
print("DO CATEGORIES SHARE PP ATOMS?")
print("="*70)

# Group Brunschwig by material class
class_to_fire = defaultdict(list)
for recipe in recipes:
    cls = recipe.get('material_class', 'unknown')
    fire = recipe.get('fire_degree', 2)
    class_to_fire[cls].append(fire)

print("\nFire degree by material class:")
for cls, fires in sorted(class_to_fire.items()):
    avg = sum(fires) / len(fires)
    unique = len(set(fires))
    print(f"  {cls}: avg fire={avg:.1f}, unique values={unique}")

# The animal class should have distinct fire degree (4)
print("""
If categories are encoded:
  - Animals (fire=4) should share PP 'ol' (precision)
  - Herbs (fire=2) should share PP 'e' (standard)
  - We found evidence for this earlier

But WITHIN a category (e.g., all fire=2 herbs):
  - Do they share SAME RI? (categories)
  - Or different RI? (specific plants)
""")

# Check RI diversity within Currier A
print("\n" + "="*70)
print("RI DIVERSITY WITHIN CURRIER A FOLIOS")
print("="*70)

import csv

# Load transcript
folio_ri = defaultdict(set)
folio_tokens = defaultdict(int)

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        folio = row.get('folio', '').strip()
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        folio_tokens[folio] += 1
        middle = extract_middle(word)
        if middle and middle in ri_middles:
            folio_ri[folio].add(middle)

print(f"\nCurrier A folios: {len(folio_ri)}")
print(f"\nRI diversity per folio (sample):")

for folio in sorted(folio_ri.keys())[:10]:
    ri_count = len(folio_ri[folio])
    token_count = folio_tokens[folio]
    print(f"  {folio}: {ri_count} unique RI from {token_count} tokens")

# Average RI per folio
avg_ri = sum(len(s) for s in folio_ri.values()) / len(folio_ri) if folio_ri else 0
print(f"\nAverage unique RI per folio: {avg_ri:.1f}")

# If RI = categories, expect low diversity per folio (few categories per page)
# If RI = specific plants, expect higher diversity (many plants per page)

print("""
If RI = categories:
  - Expect LOW RI diversity per folio (~3-5 categories)
  - Pages would be organized by category

If RI = specific plants:
  - Expect HIGHER RI diversity per folio (~10-20 species)
  - Pages contain multiple distinct materials
""")

# Check total unique RI actually used in A
total_ri_used = set()
for ri_set in folio_ri.values():
    total_ri_used.update(ri_set)

print(f"\nTotal unique RI used across all A folios: {len(total_ri_used)}")
print(f"RI defined: {len(ri_middles)}")
print(f"Coverage: {100*len(total_ri_used)/len(ri_middles):.1f}%")
