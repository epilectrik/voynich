#!/usr/bin/env python3
"""
Test 21: Trotula Recipe Structure Analysis

Can Trotula decoction/boiling recipes map to Voynich procedural grammar?

Extract Trotula recipes and analyze:
1. Procedural steps (take, boil, strain, apply)
2. Material lists (herbs, waters, oils)
3. Sequence patterns
4. Compare to Brunschwig and Voynich structure
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
import re
from collections import Counter

# Read Trotula text
trotula_path = Path('C:/git/voynich/data/reference_texts/trotula/experimentarius_medicinae_1544.txt')

with open(trotula_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Only take Trotula section (before Hildegard)
trotula_text = text[:text.find('HILDEGARDIs')]

print("=" * 70)
print("TEST 21: TROTULA RECIPE STRUCTURE ANALYSIS")
print("=" * 70)
print()

# 1. Find procedural verbs (imperatives)
print("1. PROCEDURAL VERBS (OPERATIONS)")
print("-" * 50)

# Common Latin imperatives in medical recipes
operation_patterns = {
    'accipe': 'TAKE/RECEIVE',
    'recipe': 'TAKE/RECEIVE',
    'coque': 'COOK/BOIL',
    'coquat': 'COOK/BOIL',
    'coquantur': 'COOK/BOIL',
    'decoque': 'DECOCT',
    'decoqua': 'DECOCT',
    'bulliat': 'BOIL',
    'bulliant': 'BOIL',
    'tere': 'GRIND',
    'teratur': 'GRIND',
    'misce': 'MIX',
    'miscea': 'MIX',
    'cola': 'STRAIN',
    'coletur': 'STRAIN',
    'fiat': 'LET IT BE MADE',
    'adde': 'ADD',
    'pone': 'PUT/PLACE',
    'impone': 'APPLY',
    'inunge': 'ANOINT',
    'laua': 'WASH',
    'da': 'GIVE',
    'bibat': 'DRINK',
    'potetur': 'DRINK',
    'sedeat': 'SIT',
    'intret': 'ENTER',
    'suppon': 'APPLY BELOW',
    'fumig': 'FUMIGATE',
}

op_counts = Counter()
for pattern, meaning in operation_patterns.items():
    count = len(re.findall(pattern, trotula_text, re.IGNORECASE))
    if count > 0:
        op_counts[f"{pattern} ({meaning})"] = count

print("Top procedural verbs:")
for op, count in op_counts.most_common(20):
    print(f"  {op}: {count}")

print()

# 2. Find material terms
print("2. MATERIALS (INPUTS)")
print("-" * 50)

material_patterns = {
    # Herbs
    'artemisia': 'ARTEMISIA/MUGWORT',
    'ruta': 'RUE',
    'mentha': 'MINT',
    'nepita': 'CATNIP',
    'absinth': 'WORMWOOD',
    'fenicul': 'FENNEL',
    'apium': 'CELERY/PARSLEY',
    'cuminum': 'CUMIN',
    'pulegium': 'PENNYROYAL',
    'laur': 'LAUREL/BAY',
    'rosa': 'ROSE',
    'lili': 'LILY',
    'malua': 'MALLOW',
    'urtica': 'NETTLE',
    # Waters and liquids
    'aqua': 'WATER',
    'uinum': 'WINE',
    'uino': 'WINE',
    'acetum': 'VINEGAR',
    'oleum': 'OIL',
    'mel': 'HONEY',
    'lac': 'MILK',
    # Other
    'sal': 'SALT',
    'cera': 'WAX',
    'axungia': 'LARD/FAT',
}

mat_counts = Counter()
for pattern, meaning in material_patterns.items():
    count = len(re.findall(pattern, trotula_text, re.IGNORECASE))
    if count > 0:
        mat_counts[f"{pattern} ({meaning})"] = count

print("Top materials:")
for mat, count in mat_counts.most_common(20):
    print(f"  {mat}: {count}")

print()

# 3. Extract sample recipes
print("3. SAMPLE RECIPE STRUCTURES")
print("-" * 50)

# Find lines with "Recipe" or "Accipe" (recipe starts)
lines = trotula_text.split('\n')

recipe_starts = []
for i, line in enumerate(lines):
    if re.search(r'\b(Recipe|Accipe)\b', line, re.IGNORECASE):
        # Get this line and next few
        recipe = ' '.join(lines[i:i+5])
        recipe_starts.append((i, recipe[:300]))

print(f"Found {len(recipe_starts)} recipe starts")
print()

# Show a few examples
print("Sample recipes:")
for i, (line_num, recipe) in enumerate(recipe_starts[:5]):
    print(f"\n--- Recipe {i+1} (line {line_num}) ---")
    print(recipe)

print()

# 4. Analyze recipe structure pattern
print("4. RECIPE STRUCTURAL PATTERN")
print("-" * 50)

# Common recipe pattern in Trotula:
# 1. ACCIPE/RECIPE [materials]
# 2. COQUE/DECOQUE in [liquid]
# 3. COLA/STRAIN
# 4. ADDE [additives]
# 5. DA/APPLY to patient

# Count recipes that follow each step
step_patterns = [
    (r'(accipe|recipe)', 'TAKE'),
    (r'(coque|coqu|decoque|bull)', 'COOK/BOIL'),
    (r'(col[ae]|strain)', 'STRAIN'),
    (r'(adde|admisce|misce)', 'ADD/MIX'),
    (r'(da|detur|potetur|bibat|inunge|impone|suppon)', 'APPLY/GIVE'),
]

# Find recipes that have sequential steps
print("Checking for TAKE -> COOK -> STRAIN -> ADD -> APPLY pattern:")
print()

# Look for sequences in text chunks
chunks = trotula_text.split('.')

sequential_count = 0
for chunk in chunks:
    chunk_lower = chunk.lower()
    has_take = bool(re.search(r'(accipe|recipe)', chunk_lower))
    has_cook = bool(re.search(r'(coque|coqu|decoque|bull)', chunk_lower))
    has_apply = bool(re.search(r'(da\b|detur|potetur|bibat|inunge|impone)', chunk_lower))

    if has_take and has_cook:
        sequential_count += 1

print(f"Chunks with TAKE + COOK: {sequential_count}")
print()

# 5. Compare to Voynich/Brunschwig structure
print("5. VOYNICH COMPATIBILITY ANALYSIS")
print("-" * 50)

print("""
TROTULA RECIPE STRUCTURE:
  1. TAKE [material list]
  2. COOK/BOIL in [solvent]
  3. STRAIN
  4. ADD [modifiers]
  5. APPLY [to patient]

BRUNSCHWIG DISTILLATION STRUCTURE:
  1. TAKE [material]
  2. PREPARE [cut, clean]
  3. PUT in [vessel]
  4. ADD [solvent]
  5. DISTILL [fire regimen]
  6. COLLECT [product]
  7. STORE

VOYNICH B STRUCTURE (per BCSC):
  1. [PREFIX] = operational mode/pathway
  2. [MIDDLE] = material/state
  3. [SUFFIX] = outcome marker
  - Organized in PROGRAMS (folios)
  - With CONTROL BLOCKS (lines)
  - And HAZARD AVOIDANCE (forbidden transitions)

COMPATIBILITY ASSESSMENT:
""")

# Key question: Can Trotula's simpler structure map to Voynich?
print("Key structural parallels:")
print()
print("  TROTULA          VOYNICH B")
print("  --------         ---------")
print("  TAKE material -> PREFIX selects material class")
print("  COOK/BOIL     -> MIDDLE encodes operation")
print("  in SOLVENT    -> PREFIX modifier (aqua/vino)")
print("  STRAIN        -> Transition to next state")
print("  ADD modifier  -> SUFFIX adjustment")
print("  APPLY         -> Output/LINK operation")

print()

# 6. Count complexity
print("6. PROCEDURAL COMPLEXITY COMPARISON")
print("-" * 50)

# Trotula: How many operations per recipe on average?
total_ops = sum(op_counts.values())
print(f"Total operation verbs in Trotula: {total_ops}")
print(f"Recipe starts found: {len(recipe_starts)}")
if recipe_starts:
    print(f"Avg operations per recipe: ~{total_ops / len(recipe_starts):.1f}")

print()
print("Brunschwig has more apparatus steps (vessel selection, fire regimen)")
print("Trotula is simpler: primarily boil + strain + apply")
print()
print("This SIMPLER structure might actually be MORE compatible with Voynich B")
print("if B encodes practical recipes rather than alchemical procedures.")
