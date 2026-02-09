#!/usr/bin/env python3
"""Quick Rosettes-B section overlap check"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from collections import defaultdict
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Get all tokens
all_tokens = tx._load()

# Get Rosettes MIDDLEs
rosettes_middles = set()
for token in all_tokens:
    if token.folio in ROSETTES and token.transcriber == 'H':
        m = morph.extract(token.word)
        if m and m.middle:
            rosettes_middles.add(m.middle)

# Get B folios MIDDLEs by section (excluding Rosettes)
section_middles = defaultdict(set)
for token in tx.currier_b():
    if token.folio not in ROSETTES:
        m = morph.extract(token.word)
        if m and m.middle:
            section_middles[token.section].add(m.middle)

print("ROSETTES -> B SECTION VOCABULARY OVERLAP")
print("=" * 50)
print(f"Rosettes unique MIDDLEs: {len(rosettes_middles)}")
print()

# By section
print("Overlap by B section:")
results = []
for section in sorted(section_middles.keys()):
    sect_mids = section_middles[section]
    shared_sect = rosettes_middles & sect_mids
    pct = len(shared_sect) / len(rosettes_middles) * 100 if rosettes_middles else 0
    results.append((section, len(shared_sect), pct, len(sect_mids)))

# Sort by overlap
results.sort(key=lambda x: -x[2])
for section, shared, pct, total in results:
    print(f"  {section}: {shared} shared ({pct:.1f}%) [section has {total} MIDDLEs]")

print()

# Check what 9 could mean in Brunschwig
print("WHAT DOES '9' MEAN IN BRUNSCHWIG?")
print("-" * 50)
print("""
Brunschwig's system includes:
- 4 fire degrees (1-4)
- 5 quality tests
- ~20 apparatus types (alembic, balneum marie, etc.)
- ~10 material categories (herb, flower, root, animal...)

NONE of these = 9.

Possible interpretations:
- 9 = 4 fire + 5 quality (composite?)
- 9 = planetary association (9 celestial spheres in medieval cosmology)
- 9 = NOT a Brunschwig number (different system)
""")

# Compare to actual Brunschwig fire mapping
print()
print("BRUNSCHWIG FIRE DEGREE -> REGIME MAPPING:")
print("-" * 50)

# From F-BRU-001 and BRSC
fire_regime = {
    'Fire 1 (gentle/slow)': 'REGIME_2',
    'Fire 2 (medium)': 'REGIME_1',
    'Fire 3 (intense)': 'REGIME_3',
    'Fire 4 (constrained)': 'REGIME_4 (animal materials)',
}

for fire, regime in fire_regime.items():
    print(f"  {fire} -> {regime}")

print()
print("ROSETTES = 9 circles, but Brunschwig has 4 fire degrees")
print("This is a MISMATCH unless circles encode something else.")
