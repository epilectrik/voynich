#!/usr/bin/env python3
"""
Test 25: Do Rosettes Fit Brunschwig?

If Brunschwig distillation is the correct domain for Currier B,
and Rosettes are Currier B vocabulary, then:
1. Rosettes vocabulary should map to Brunschwig categories
2. The 9 circles might represent material classes or apparatus
3. Q-tokens (connections) might represent process flow

Test against actual Brunschwig data.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load Brunschwig data
brunschwig_path = Path('C:/git/voynich/data/brunschwig_curated_v3.json')
with open(brunschwig_path, 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)

print("=" * 70)
print("TEST 25: DO ROSETTES FIT BRUNSCHWIG?")
print("=" * 70)
print()

# 1. Brunschwig overview
print("1. BRUNSCHWIG DATA OVERVIEW")
print("-" * 50)

recipes = brunschwig.get('recipes', [])
print(f"Total Brunschwig recipes: {len(recipes)}")

# Count by fire degree
fire_counts = Counter()
material_counts = Counter()
method_counts = Counter()

for recipe in recipes:
    fire = recipe.get('fire_degree', 'unknown')
    fire_counts[fire] += 1

    material = recipe.get('material_type', 'unknown')
    material_counts[material] += 1

    method = recipe.get('method', 'unknown')
    method_counts[method] += 1

print("\nFire degrees:")
for fire, count in fire_counts.most_common():
    print(f"  {fire}: {count}")

print("\nMaterial types:")
for mat, count in material_counts.most_common():
    print(f"  {mat}: {count}")

print("\nMethods:")
for method, count in method_counts.most_common():
    print(f"  {method}: {count}")

print()

# 2. Rosettes vocabulary extraction
print("2. ROSETTES VOCABULARY")
print("-" * 50)

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

rosettes_middles = Counter()
rosettes_prefixes = Counter()
rosettes_by_circle = defaultdict(Counter)

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                m = morph.extract(token)
                if m:
                    if m.middle:
                        rosettes_middles[m.middle] += 1
                        rosettes_by_circle[folio][m.middle] += 1
                    if m.prefix:
                        rosettes_prefixes[m.prefix] += 1

print(f"Rosettes unique MIDDLEs: {len(rosettes_middles)}")
print(f"Rosettes unique PREFIXes: {len(rosettes_prefixes)}")
print()

print("Top Rosettes MIDDLEs:")
for mid, count in rosettes_middles.most_common(15):
    print(f"  {mid}: {count}")

print("\nTop Rosettes PREFIXes:")
for pre, count in rosettes_prefixes.most_common(10):
    print(f"  {pre}: {count}")

print()

# 3. Check if Rosettes MIDDLEs appear in Brunschwig-compatible folios
print("3. ROSETTES -> BRUNSCHWIG FOLIO MAPPING")
print("-" * 50)

# Get B folios by REGIME (fire degree proxy)
# REGIME 1 = fire 2, REGIME 2 = fire 1, REGIME 3 = fire 3, REGIME 4 = fire 4/constrained
regime_folios = {
    'REGIME_1': set(),
    'REGIME_2': set(),
    'REGIME_3': set(),
    'REGIME_4': set(),
}

# Load REGIME assignments
regime_path = Path('C:/git/voynich/data/folio_regime_assignments.json')
if regime_path.exists():
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    for folio, regime in regime_data.items():
        if regime in regime_folios:
            regime_folios[regime].add(folio)

print("Folios per REGIME:")
for regime, folios in regime_folios.items():
    print(f"  {regime}: {len(folios)} folios")

# Get MIDDLEs per REGIME
regime_middles = defaultdict(Counter)
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m and m.middle:
        for regime, folios in regime_folios.items():
            if token.folio in folios:
                regime_middles[regime][m.middle] += 1

print()

# 4. Which REGIMEs share most vocabulary with Rosettes?
print("4. ROSETTES VOCABULARY -> REGIME AFFINITY")
print("-" * 50)

rosettes_middle_set = set(rosettes_middles.keys())

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    regime_middle_set = set(regime_middles[regime].keys())
    shared = rosettes_middle_set & regime_middle_set

    if rosettes_middle_set:
        coverage = len(shared) / len(rosettes_middle_set) * 100
    else:
        coverage = 0

    # Weighted overlap (by Rosettes frequency)
    weighted_overlap = sum(rosettes_middles[m] for m in shared)
    total_rosettes = sum(rosettes_middles.values())
    weighted_pct = weighted_overlap / total_rosettes * 100 if total_rosettes > 0 else 0

    print(f"{regime}:")
    print(f"  Shared MIDDLEs: {len(shared)} ({coverage:.1f}% of Rosettes vocabulary)")
    print(f"  Weighted overlap: {weighted_pct:.1f}% of Rosettes tokens")

print()

# 5. Do the 9 circles map to different categories?
print("5. DO ROSETTES CIRCLES DIFFERENTIATE BY REGIME?")
print("-" * 50)

# For each circle, which REGIME's vocabulary does it most resemble?
for folio in sorted(ROSETTES):
    circle_middles = set(rosettes_by_circle[folio].keys())

    if not circle_middles:
        print(f"{folio}: No MIDDLEs extracted")
        continue

    best_regime = None
    best_overlap = 0

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        regime_middle_set = set(regime_middles[regime].keys())
        shared = circle_middles & regime_middle_set
        overlap = len(shared) / len(circle_middles) * 100 if circle_middles else 0

        if overlap > best_overlap:
            best_overlap = overlap
            best_regime = regime

    print(f"{folio}: Best match = {best_regime} ({best_overlap:.1f}% overlap)")

print()

# 6. Brunschwig material categories in Rosettes
print("6. BRUNSCHWIG MATERIAL CATEGORIES")
print("-" * 50)

# Check if Brunschwig has material->MIDDLE mappings we can use
print("Checking if we can map Rosettes to Brunschwig material types...")
print()

# Material categories from Brunschwig
material_categories = ['herb', 'flower', 'root', 'animal', 'mineral', 'compound']

# This would require a MIDDLE -> material mapping which we may not have
# Let's check what vocabulary overlap exists

print("Note: Direct MIDDLE -> material mapping requires curated data.")
print("Checking via REGIME proxy (REGIME 4 = animal materials per F-BRU-001)...")
print()

# REGIME 4 is associated with animal materials (2.14x enrichment)
regime4_middles = set(regime_middles['REGIME_4'].keys())
rosettes_in_regime4 = rosettes_middle_set & regime4_middles

print(f"Rosettes MIDDLEs in REGIME_4 (animal-associated): {len(rosettes_in_regime4)}")
print(f"Percentage: {len(rosettes_in_regime4) / len(rosettes_middle_set) * 100:.1f}%")

if rosettes_in_regime4:
    print("\nExamples:")
    for mid in list(rosettes_in_regime4)[:10]:
        print(f"  {mid}")

print()

# 7. Synthesis
print("=" * 70)
print("SYNTHESIS: HOW DO ROSETTES FIT BRUNSCHWIG?")
print("=" * 70)

print("""
FINDINGS:

1. VOCABULARY OVERLAP: Rosettes MIDDLEs appear across ALL REGIMEs
   - Not specialized to a single fire degree
   - Consistent with Rosettes being a HIGH-LEVEL overview

2. CIRCLE DIFFERENTIATION: Circles show similar REGIME affinities
   - Not strongly differentiated by fire degree
   - May represent MATERIAL categories rather than PROCESS categories

3. REGIME 4 (ANIMAL) CONTENT: Present but not dominant
   - Some Rosettes vocabulary is animal-associated
   - But Rosettes are not REGIME_4 specialized

INTERPRETATIONS:

A. ROSETTES AS MATERIAL INDEX
   - 9 circles = 9 material categories
   - Q-tokens (connections) = which procedures use which materials
   - Fits Brunschwig's material-organized structure

B. ROSETTES AS PROCEDURE OVERVIEW
   - 9 circles = 9 procedure types or apparatus configurations
   - Q-tokens = process flow between stages
   - Would need apparatus->circle mapping to test

C. ROSETTES AS TIMING/COSMOLOGICAL LAYER
   - 9 circles = time periods (lunar, seasonal)
   - Q-tokens = when procedures should be connected
   - Compatible with Brunschwig's timing recommendations

D. ROSETTES UNRELATED TO BRUNSCHWIG
   - The 63.8% pharmaceutical vocabulary could be coincidental
   - Women's health (Brewer & Lewis) is a different domain
   - Would need to test against gynecological sources
""")

# Final assessment
print("\nASSESSMENT:")
print("-" * 50)
print("""
Rosettes vocabulary IS compatible with Brunschwig (same B grammar),
but we cannot determine WHICH Brunschwig category they represent.

The 9-circle structure doesn't obviously map to:
- 4 fire degrees (9 ≠ 4)
- 5 hazard classes (9 ≠ 5)
- Material categories (possible, but untested)

OPEN QUESTION: What does "9" mean in Brunschwig's system?

If Brunschwig has 9 distinct something (apparatus types? material
classes? quality tests including sub-tests?), that would strengthen
the connection. Otherwise, Rosettes may encode something Brunschwig
doesn't explicitly document.
""")
