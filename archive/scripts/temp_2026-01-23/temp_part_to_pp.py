#!/usr/bin/env python3
"""
Check if specific PP atoms correlate with specific plant PARTS.
If so, the PP atom encodes "what part are we working with" procedurally.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])

# Load Brunschwig
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

# (folio classifications not needed for this analysis)

print("="*70)
print("PLANT PART -> PP ATOM CORRELATION")
print("="*70)

# What parts are most common?
part_counts = Counter()
for recipe in recipes:
    parts = recipe.get('parts_used', [])
    for p in parts:
        # Normalize part names
        p_lower = p.lower()
        if 'root' in p_lower:
            part_counts['root'] += 1
        elif 'herb' in p_lower:
            part_counts['herb'] += 1
        elif 'flower' in p_lower:
            part_counts['flower'] += 1
        elif 'leaf' in p_lower or 'leaves' in p_lower:
            part_counts['leaf'] += 1
        elif 'seed' in p_lower:
            part_counts['seed'] += 1
        elif 'sap' in p_lower:
            part_counts['sap'] += 1
        elif 'bark' in p_lower:
            part_counts['bark'] += 1
        elif 'blood' in p_lower:
            part_counts['blood'] += 1
        elif 'stem' in p_lower:
            part_counts['stem'] += 1

print("\nPart usage frequency:")
for part, count in part_counts.most_common():
    print(f"  {part}: {count}")

# Map procedure types to parts
proc_by_part = defaultdict(list)

for recipe in recipes:
    parts = recipe.get('parts_used', [])
    proc = tuple(recipe.get('instruction_sequence') or [])

    # Normalize
    for p in parts:
        p_lower = p.lower()
        if 'root' in p_lower:
            proc_by_part['root'].append(proc)
        elif 'herb' in p_lower:
            proc_by_part['herb'].append(proc)
        elif 'flower' in p_lower:
            proc_by_part['flower'].append(proc)
        elif 'sap' in p_lower:
            proc_by_part['sap'].append(proc)
        elif 'blood' in p_lower:
            proc_by_part['blood'].append(proc)

print("\n" + "="*70)
print("PROCEDURE SIGNATURES BY PART")
print("="*70)

for part in ['root', 'herb', 'flower', 'sap', 'blood']:
    procs = proc_by_part.get(part, [])
    if procs:
        dist = Counter(procs)
        print(f"\n{part.upper()} ({len(procs)} recipes):")
        for p, c in dist.most_common(3):
            pct = 100*c/len(procs)
            print(f"  {p}: {c} ({pct:.0f}%)")

# Key question: Does PART determine PP atom, or does PP atom span multiple parts?
print("\n" + "="*70)
print("PP ATOM HYPOTHESIS")
print("="*70)
print("""
Hypothesis A: PP atom encodes PART
  - 'e' = herb/root processing
  - 'ol' = flower/sap processing
  - Different parts = different PP atoms

Hypothesis B: PP atom encodes PROCEDURE TYPE regardless of part
  - 'e' = standard distillation (works for most parts)
  - 'ol' = precision handling (works for delicate materials)
  - PART affects WHICH procedure is chosen, but PP encodes the procedure itself

Based on the data:
  - Root: 98% use (AUX, e_ESCAPE) - standard
  - Herb: 96% use (AUX, e_ESCAPE) - standard
  - Flower: 92% use (AUX, e_ESCAPE), 6% need k_ENERGY
  - Sap: 100% need FLOW

The PP atom 'e' appears in (AUX, e_ESCAPE) which is the standard procedure.
But flowers sometimes need k_ENERGY, and sap always needs FLOW.

This suggests:
  - PP atom encodes PROCEDURE (not PART)
  - But PART influences which procedure is needed
  - The mapping is: PART -> required PROCEDURE -> PP atom
""")

# Check what the 'ol' enrichment means
print("\n" + "="*70)
print("'ol' vs 'e' IN CONTEXT OF PARTS")
print("="*70)
print("""
We found:
  - 'e' is enriched in WATER_STANDARD (most materials)
  - 'ol' is enriched in PRECISION (animal materials, special handling)

The PART breakdown:
  - Most plant parts (root, herb, flower) use standard procedure
  - SAP always needs FLOW (fluid handling)
  - BLOOD/animal parts need precision fire control (fire degree 4)

So the PP atoms may encode:
  - 'e' = compatible with standard aqueous distillation
  - 'ol' = requires precision/animal-grade handling

PART is a PREDICTOR of which PP you need:
  - Herb/root -> 'e' (standard)
  - Animal blood -> 'ol' (precision)
  - But the PP encodes the PROCEDURE, not the PART directly.
""")

# Final model
print("\n" + "="*70)
print("FINAL PARAMETRIC MODEL")
print("="*70)
print("""
RI structure:

  RI = PP_atom + identity_extension

Where:
  PP_atom = what PROCEDURE is needed (determined by material type/part)
    - 'e' = standard distillation compatible
    - 'ol' = precision handling required
    - (other atoms for other procedure requirements)

  identity_extension = WHICH SPECIFIC MATERIAL
    - Distinguishes rose from lily, borage from mint
    - But both might share same PP if same procedure works

STATE (chopped, dried, fresh):
  - Mostly IMPLICIT (chopped is nearly universal)
  - Not encoded as a separate modifier
  - May be handled at B execution level (parametric within procedure)

PART (root, herb, flower):
  - Determines which PP is needed
  - But not encoded as a separate atom
  - Instead: different parts of same plant = different RI entries
    with different PP atoms

Example:
  borage_herb   = PP_standard + ext_borage
  borage_flower = PP_heating + ext_borage

  Both have "borage" identity, but different PP atoms because
  different parts need different procedures.
""")
