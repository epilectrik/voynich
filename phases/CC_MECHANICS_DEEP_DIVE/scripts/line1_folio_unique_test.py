"""
Verify the COMPOUND_MIDDLE_ARCHITECTURE finding:
- Line-1 HT has 21.7% folio-unique MIDDLEs vs 11.7% body
- Those folio-unique MIDDLEs are 84.8% compound

The "header" is the TOKEN ITSELF being unique to that folio.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

print("="*70)
print("LINE-1 FOLIO-UNIQUE COMPOUND TEST")
print("="*70)

# ============================================================
# COLLECT MIDDLES BY FOLIO AND LINE POSITION
# ============================================================

# Track which MIDDLEs appear in which folios
middle_to_folios = defaultdict(set)
line1_middles_by_folio = defaultdict(list)
body_middles_by_folio = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens

    middle_to_folios[m.middle].add(folio)

    if line == '1':
        line1_middles_by_folio[folio].append({
            'middle': m.middle,
            'is_ht': is_ht
        })
    else:
        body_middles_by_folio[folio].append({
            'middle': m.middle,
            'is_ht': is_ht
        })

# Identify folio-unique MIDDLEs
folio_unique_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) == 1}

print(f"\nTotal unique MIDDLEs: {len(middle_to_folios)}")
print(f"Folio-unique MIDDLEs: {len(folio_unique_middles)} ({100*len(folio_unique_middles)/len(middle_to_folios):.1f}%)")

# ============================================================
# GET CORE MIDDLES (for compound detection)
# ============================================================

# Core MIDDLEs = MIDDLEs that appear in 10+ folios (frequent, operational)
core_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) >= 10}
print(f"Core MIDDLEs (10+ folios): {len(core_middles)}")

# ============================================================
# ANALYZE LINE-1 HT vs BODY
# ============================================================
print("\n" + "="*70)
print("LINE-1 HT vs BODY COMPARISON")
print("="*70)

# Line-1 HT
line1_ht_middles = []
for folio, entries in line1_middles_by_folio.items():
    for e in entries:
        if e['is_ht']:
            line1_ht_middles.append(e['middle'])

line1_ht_unique = set(line1_ht_middles)
line1_ht_folio_unique = line1_ht_unique & folio_unique_middles
line1_ht_folio_unique_rate = len(line1_ht_folio_unique) / len(line1_ht_unique) * 100 if line1_ht_unique else 0

# Body (lines 2+)
body_middles = []
for folio, entries in body_middles_by_folio.items():
    for e in entries:
        body_middles.append(e['middle'])

body_unique = set(body_middles)
body_folio_unique = body_unique & folio_unique_middles
body_folio_unique_rate = len(body_folio_unique) / len(body_unique) * 100 if body_unique else 0

print(f"\nLine-1 HT MIDDLEs:")
print(f"  Unique types: {len(line1_ht_unique)}")
print(f"  Folio-unique: {len(line1_ht_folio_unique)} ({line1_ht_folio_unique_rate:.1f}%)")

print(f"\nBody MIDDLEs:")
print(f"  Unique types: {len(body_unique)}")
print(f"  Folio-unique: {len(body_folio_unique)} ({body_folio_unique_rate:.1f}%)")

print(f"\nDifference: {line1_ht_folio_unique_rate - body_folio_unique_rate:+.1f}pp")

# ============================================================
# CHECK IF FOLIO-UNIQUE MIDDLES ARE COMPOUND
# ============================================================
print("\n" + "="*70)
print("FOLIO-UNIQUE COMPOUND ANALYSIS")
print("="*70)

def is_compound(middle, core_set):
    """Check if MIDDLE contains any core MIDDLE as substring"""
    for core in core_set:
        if core in middle and core != middle:
            return True
    return False

# Line-1 HT folio-unique
line1_ht_fu_compound = sum(1 for m in line1_ht_folio_unique if is_compound(m, core_middles))
line1_ht_fu_compound_rate = 100 * line1_ht_fu_compound / len(line1_ht_folio_unique) if line1_ht_folio_unique else 0

# Body folio-unique
body_fu_compound = sum(1 for m in body_folio_unique if is_compound(m, core_middles))
body_fu_compound_rate = 100 * body_fu_compound / len(body_folio_unique) if body_folio_unique else 0

print(f"\nLine-1 HT folio-unique compound rate: {line1_ht_fu_compound_rate:.1f}%")
print(f"Body folio-unique compound rate: {body_fu_compound_rate:.1f}%")

# ============================================================
# EXAMPLES
# ============================================================
print("\n" + "="*70)
print("EXAMPLES: Line-1 HT Folio-Unique Compound MIDDLEs")
print("="*70)

examples = []
for mid in sorted(line1_ht_folio_unique, key=len, reverse=True)[:10]:
    cores = [c for c in core_middles if c in mid and c != mid]
    examples.append((mid, cores))

for mid, cores in examples:
    print(f"  '{mid}' contains cores: {cores[:5]}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

print(f"""
COMPOUND_MIDDLE_ARCHITECTURE Finding Verification:

Expected (from README):
  - Line-1 HT: 21.7% folio-unique
  - Body: 11.7% folio-unique
  - Folio-unique compound rate: 84.8%

Observed:
  - Line-1 HT: {line1_ht_folio_unique_rate:.1f}% folio-unique
  - Body: {body_folio_unique_rate:.1f}% folio-unique
  - Line-1 HT folio-unique compound rate: {line1_ht_fu_compound_rate:.1f}%
  - Body folio-unique compound rate: {body_fu_compound_rate:.1f}%

{'CONFIRMED: Line-1 HT tokens are identification tags (folio-unique compound forms)'
 if line1_ht_folio_unique_rate > body_folio_unique_rate and line1_ht_fu_compound_rate > 50
 else 'NEEDS INVESTIGATION'}
""")
