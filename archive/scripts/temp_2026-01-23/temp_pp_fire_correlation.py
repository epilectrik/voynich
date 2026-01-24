#!/usr/bin/env python3
"""
Test: Do differential PP MIDDLEs correlate with fire degree?

Hypothesis:
- 'ke', 'ho', 'te', 'eod' are more common in animal records
- Animals require fire degree 4 in Brunschwig
- Therefore these PP might encode "high heat tolerance"

Test method:
- Look at which B folios have high concentrations of these PP
- Check if those folios correlate with REGIME_4
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class_token_map for MIDDLE extraction
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']
df['middle'] = df['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

df_b = df[df['language'] == 'B'].copy()

print("="*60)
print("TESTING: PP MIDDLES -> FIRE DEGREE CORRELATION")
print("="*60)

# Animal-associated PP MIDDLEs from previous analysis
animal_pp = ['ke', 'ho', 'te', 'eod', 'eo', 'keo', 'cph', 'ol']

# Universal PP (high in both animal and non-animal)
universal_pp = ['o', 'e', 'i', 'a', 'r', 'l']

# Check where these PP appear in B (by folio)
print("\n--- ANIMAL-ASSOCIATED PP: FOLIO DISTRIBUTION ---")

for pp in animal_pp:
    pp_tokens = df_b[df_b['middle'] == pp]
    if len(pp_tokens) > 0:
        folios = pp_tokens['folio'].value_counts()
        total = len(pp_tokens)
        print(f"\n'{pp}' ({total} tokens in B):")
        print(f"  Top folios: {dict(folios.head(8))}")

# Load REGIME mapping if available
try:
    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/regime_folio_mapping.json') as f:
        regime_map = json.load(f)
    has_regime = True
except:
    # Try alternate location
    try:
        with open('data/regime_folio_mapping.json') as f:
            regime_map = json.load(f)
        has_regime = True
    except:
        has_regime = False
        print("\nNo REGIME mapping found, checking Brunschwig fire degrees instead")

# ============================================================
# Approach 2: Check directly from Brunschwig data
# ============================================================
print("\n" + "="*60)
print("BRUNSCHWIG FIRE DEGREE -> EXPECTED PP")
print("="*60)

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    brunschwig = json.load(f)

recipes = brunschwig['recipes']

# Group by fire degree
fire_groups = defaultdict(list)
for r in recipes:
    fire = r.get('fire_degree')
    if fire:
        fire_groups[fire].append(r)

print("\nFire degree distribution:")
for fire in sorted(fire_groups.keys()):
    recs = fire_groups[fire]
    classes = Counter(r.get('material_class') for r in recs)
    print(f"\n  FIRE {fire} ({len(recs)} recipes):")
    print(f"    Classes: {dict(classes.most_common(5))}")
    # Check for CHOP/POUND requirements
    has_chop = sum(1 for r in recs if any(
        s.get('action') == 'CHOP' for s in (r.get('procedural_steps') or [])
    ))
    has_pound = sum(1 for r in recs if any(
        s.get('action') == 'POUND' for s in (r.get('procedural_steps') or [])
    ))
    print(f"    CHOP: {has_chop} ({100*has_chop/len(recs):.0f}%), POUND: {has_pound} ({100*has_pound/len(recs):.0f}%)")

# ============================================================
# What properties distinguish fire degrees?
# ============================================================
print("\n" + "="*60)
print("PROPERTIES BY FIRE DEGREE")
print("="*60)

print("\nIf PP encodes fire degree, expect:")
print("  Fire 1: flowers, fruits (gentle)")
print("  Fire 2: most herbs (standard)")
print("  Fire 3: tougher herbs (moderate)")
print("  Fire 4: animals (strong heat)")

# Check action profiles by fire degree
for fire in [1, 2, 3, 4]:
    recs = fire_groups.get(fire, [])
    if recs:
        action_counter = Counter()
        for r in recs:
            steps = r.get('procedural_steps') or []
            for s in steps:
                action_counter[s.get('action')] += 1
        print(f"\n  Fire {fire} actions: {dict(action_counter.most_common(5))}")

# ============================================================
# Hypothesis mapping
# ============================================================
print("\n" + "="*60)
print("HYPOTHESIS: PP MIDDLE -> BRUNSCHWIG PROPERTY")
print("="*60)

print("""
Based on animal vs non-animal differential:

PP MIDDLE | Animal vs Non | Possible Brunschwig Property
----------|---------------|------------------------------
'ke'      | 31% vs 6%     | High fire (animals fire=4)
'ho'      | 23% vs 3%     | Organic/complex material
'te'      | 15% vs 1%     | Special prep (PLUCK/BUTCHER)
'eod'     | 15% vs 2%     | Extended processing
'eo'      | 23% vs 9%     | Moderate-high complexity
'keo'     | 8% vs 1%      | Very high fire + complexity
'cph'     | 8% vs 3%      | Hard material (POUND?)
'ol'      | 15% vs 5%     | Liquid extraction (COLLECT?)

Universal PP (similar in both):
'o'       | 77% vs 60%    | Base distillation
'e'       | 62% vs 34%    | Standard processing
'i'       | 31% vs 39%    | Common herb property
'a'       | 23% vs 27%    | Standard
'l'       | 23% vs 18%    | Fluid handling
""")

# ============================================================
# Cross-validation: Do herbal records with CHOP have different PP?
# ============================================================
print("\n" + "="*60)
print("CROSS-VALIDATION: CHOP-REQUIRING MATERIALS")
print("="*60)

# Get materials requiring CHOP
chop_materials = [r['name_english'] for r in recipes if any(
    s.get('action') == 'CHOP' for s in (r.get('procedural_steps') or [])
)]
no_chop_materials = [r['name_english'] for r in recipes if
    r.get('procedural_steps') and not any(
        s.get('action') == 'CHOP' for s in r['procedural_steps']
    )
]

print(f"\nCHOP required: {len(chop_materials)} materials")
print(f"No CHOP: {len(no_chop_materials)} materials")

# If we had material->token mappings, we could check PP
# For now, note the expectation
print("""
Expectation: If PP encodes preparation type:
- Materials needing CHOP should share certain PP MIDDLEs
- Materials needing POUND should share different PP MIDDLEs
- Animals (PLUCK/BUTCHER) should share 'ke', 'ho', 'te' etc.

This could explain why animal records have distinct PP signatures.
""")
