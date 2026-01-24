#!/usr/bin/env python3
"""
Connect Brunschwig action profiles to PP MIDDLE signatures.

Strategy:
1. Start from validated identifications (chicken=eoschso, thyme=keolo)
2. Get their PP MIDDLE profiles
3. Check if their action profiles predict their PP signature
4. Extend to other materials
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)
token_to_middle = class_map['token_to_middle']

df['middle'] = df['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Identify PP MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
pp_middles = a_middles & b_middles

print("="*60)
print("VALIDATED MATERIAL PP PROFILES")
print("="*60)

# Known identifications from triangulation
# chicken (eoschso) at f90r1:6
# thyme (keolo) at f99v:7

# Get the A record content for validated materials
def get_record_pp(folio, line):
    record_tokens = df_a[(df_a['folio'] == folio) & (df_a['line'] == line)]
    middles = set(record_tokens['middle'].dropna())
    pp_in_record = middles & pp_middles
    ri_in_record = middles - b_middles
    return {
        'all_middles': middles,
        'pp': pp_in_record,
        'ri': ri_in_record,
        'tokens': list(record_tokens['word'])
    }

print("\n--- CHICKEN (eoschso) at f90r1:6 ---")
chicken = get_record_pp('f90r1', 6)
print(f"Tokens: {chicken['tokens']}")
print(f"PP MIDDLEs: {chicken['pp']}")
print(f"RI MIDDLEs: {chicken['ri']}")

print("\n--- THYME (keolo) at f99v:7 ---")
thyme = get_record_pp('f99v', 7)
print(f"Tokens: {thyme['tokens']}")
print(f"PP MIDDLEs: {thyme['pp']}")
print(f"RI MIDDLEs: {thyme['ri']}")

# Load Brunschwig data
with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    brunschwig = json.load(f)
recipes = brunschwig['recipes']

# Find chicken and thyme in Brunschwig
def find_recipe(name_contains):
    for r in recipes:
        if name_contains.lower() in r['name_english'].lower():
            return r
    return None

print("\n" + "="*60)
print("BRUNSCHWIG PROFILES FOR VALIDATED MATERIALS")
print("="*60)

chicken_recipe = find_recipe('chicken') or find_recipe('hen')
thyme_recipe = find_recipe('thyme') or find_recipe('quendel')

if chicken_recipe:
    print(f"\nCHICKEN: {chicken_recipe['name_english']}")
    print(f"  Fire degree: {chicken_recipe.get('fire_degree')}")
    print(f"  Material class: {chicken_recipe.get('material_class')}")
    steps = chicken_recipe.get('procedural_steps') or []
    actions = [s.get('action') for s in steps]
    print(f"  Actions: {actions}")
    print(f"  Parts used: {chicken_recipe.get('parts_used')}")

if thyme_recipe:
    print(f"\nTHYME: {thyme_recipe['name_english']}")
    print(f"  Fire degree: {thyme_recipe.get('fire_degree')}")
    print(f"  Material class: {thyme_recipe.get('material_class')}")
    steps = thyme_recipe.get('procedural_steps') or []
    actions = [s.get('action') for s in steps]
    print(f"  Actions: {actions}")
    print(f"  Parts used: {thyme_recipe.get('parts_used')}")

# ============================================================
# Now the KEY TEST: Do similar action profiles share PP?
# ============================================================
print("\n" + "="*60)
print("KEY TEST: ACTION PROFILE -> PP CORRELATION")
print("="*60)

# Group recipes by action profile
recipe_by_profile = defaultdict(list)
for r in recipes:
    steps = r.get('procedural_steps') or []
    actions = frozenset(s.get('action') for s in steps) if steps else frozenset()
    recipe_by_profile[actions].append(r)

# For each profile, list the materials
# We'll then need to find their A records and check PP overlap

print("\nAction profiles and their materials:")
for profile, recs in sorted(recipe_by_profile.items(), key=lambda x: -len(x[1]))[:10]:
    if len(profile) > 0:
        names = [r['name_english'] for r in recs[:8]]
        print(f"\n  {set(profile)}:")
        print(f"    {names}")

# ============================================================
# Check what PP MIDDLEs appear with PLUCK (animal-specific)
# ============================================================
print("\n" + "="*60)
print("PLUCK-REQUIRING MATERIALS AND THEIR PROPERTIES")
print("="*60)

pluck_recipes = [r for r in recipes if any(
    s.get('action') == 'PLUCK' for s in (r.get('procedural_steps') or [])
)]

for r in pluck_recipes:
    print(f"\n{r['name_english']}:")
    print(f"  Fire: {r.get('fire_degree')}")
    print(f"  Class: {r.get('material_class')}")
    steps = r.get('procedural_steps') or []
    actions = [s.get('action') for s in steps]
    print(f"  Actions: {actions}")

# ============================================================
# Hypothesis: Rare PP MIDDLEs encode rare procedures
# ============================================================
print("\n" + "="*60)
print("HYPOTHESIS: RARE PP = RARE PROCEDURES")
print("="*60)

# Get rare PP frequency in B
b_middle_counts = Counter(df_b['middle'].dropna())
pp_freq = {m: b_middle_counts.get(m, 0) for m in pp_middles}
rare_pp = [m for m, cnt in pp_freq.items() if 0 < cnt < 20]

print(f"\nRare PP MIDDLEs (1-19 occurrences in B): {len(rare_pp)}")
for m in sorted(rare_pp, key=lambda x: pp_freq[x]):
    print(f"  '{m}': {pp_freq[m]}")

# Map rare PP to B folios
print("\n\nRare PP -> B folio distribution:")
for m in sorted(rare_pp, key=lambda x: pp_freq[x])[:10]:
    folios = df_b[df_b['middle'] == m]['folio'].unique()
    print(f"  '{m}' ({pp_freq[m]}): {list(folios)[:5]}")

# ============================================================
# The reverse direction: B folio characteristics
# ============================================================
print("\n" + "="*60)
print("B FOLIO CHARACTERISTICS")
print("="*60)

# Which folios have animals? (known: f95v1, f85r1, f94v for chicken-like)
# Let's check if rare PP concentrate in these folios

animal_folios = ['f95v1', 'f85r1', 'f94v', 'f40v', 'f41v']  # From methodology doc

print(f"\nAnimal-associated B folios: {animal_folios}")

for folio in animal_folios:
    folio_df = df_b[df_b['folio'] == folio]
    folio_middles = set(folio_df['middle'].dropna())
    folio_pp = folio_middles & pp_middles
    folio_rare_pp = folio_pp & set(rare_pp)
    print(f"\n  {folio}:")
    print(f"    Total PP: {len(folio_pp)}")
    print(f"    Rare PP: {folio_rare_pp}")

# ============================================================
# Direct comparison: chicken PP vs thyme PP
# ============================================================
print("\n" + "="*60)
print("PP SIGNATURE COMPARISON")
print("="*60)

print(f"\nChicken PP: {chicken['pp']}")
print(f"Thyme PP: {thyme['pp']}")
print(f"Overlap: {chicken['pp'] & thyme['pp']}")
print(f"Chicken unique: {chicken['pp'] - thyme['pp']}")
print(f"Thyme unique: {thyme['pp'] - chicken['pp']}")

# What do these PP MIDDLEs mean in terms of B behavior?
print("\n\nPP MIDDLE -> B behavior (PREFIX distribution):")

def get_prefix_profile(middle):
    b_tokens = df_b[df_b['middle'] == middle]
    if len(b_tokens) == 0:
        return None
    prefix_counts = b_tokens['word'].apply(
        lambda x: x[:2] if pd.notna(x) and len(x) >= 2 else 'NA'
    ).value_counts()
    return dict(prefix_counts.head(5))

for m in chicken['pp']:
    profile = get_prefix_profile(m)
    if profile:
        print(f"  '{m}': {profile}")
