"""
Grinding/Preparation Analysis for Human Communication Model validation

Goal: Find Brunschwig recipes with explicit grinding/pounding/crushing steps
and identify common B structural patterns that might communicate "grind"
"""

import json
import re
from collections import defaultdict

# Load complete Brunschwig database
with open('data/brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Keywords for grinding/pounding/crushing in Middle High German AND English
GRINDING_KEYWORDS_GERMAN = [
    'gehackt', 'hacken', 'hack',      # chopped
    'gestossen', 'stossen', 'stoß',   # pounded
    'gerieben', 'reiben', 'rib',      # ground/rubbed
    'zerkleinert', 'klein',           # made small
    'zerstoßen', 'zerstossen',        # crushed
    'pulver', 'puluerisier',          # powdered
    'gemalen', 'malen',               # ground (mill)
    'zerbrochen', 'brechen',          # broken
    'zerschnitten', 'schneiden',      # cut up
    'cleinen stücklin',               # small pieces
    'cleinen stückle',                # small pieces variant
]

GRINDING_KEYWORDS_ENGLISH = [
    'chop', 'chopped', 'chopping',
    'pound', 'pounded', 'pounding',
    'grind', 'ground', 'grinding',
    'crush', 'crushed', 'crushing',
    'cut', 'cutting',
    'small pieces',
    'powder', 'powdered',
    'mash', 'mashed',
    'break', 'broken',
]

# Track recipes with grinding
grinding_recipes = []
non_grinding_recipes = []

for recipe in data['recipes']:
    recipe_id = recipe['id']
    name = recipe.get('name_english', recipe.get('name_german', f'Recipe {recipe_id}'))

    # Check procedure_summary for grinding keywords
    procedure = (recipe.get('procedure_summary', '') or '').lower()

    # Find grinding keywords
    found_keywords = []
    for kw in GRINDING_KEYWORDS_ENGLISH:
        if kw in procedure:
            found_keywords.append(kw)

    has_procedure = recipe.get('has_procedure', False)
    instruction_seq = recipe.get('instruction_sequence', []) or []

    if found_keywords and has_procedure and instruction_seq:
        grinding_recipes.append({
            'id': recipe_id,
            'name': name,
            'keywords': list(set(found_keywords)),  # dedupe
            'sequence': instruction_seq,
            'material_class': recipe.get('material_class', ''),
            'fire_degree': recipe.get('fire_degree', 0),
            'procedure': procedure,
        })
    elif has_procedure and instruction_seq:
        non_grinding_recipes.append({
            'id': recipe_id,
            'name': name,
            'sequence': instruction_seq,
            'material_class': recipe.get('material_class', ''),
            'fire_degree': recipe.get('fire_degree', 0),
            'procedure': procedure,
        })

print("=" * 70)
print("GRINDING/PREPARATION ANALYSIS (COMPLETE DATABASE)")
print("=" * 70)

print(f"\nTotal recipes in database: {len(data['recipes'])}")
print(f"Recipes WITH grinding keywords and procedure: {len(grinding_recipes)}")
print(f"Recipes WITHOUT grinding (but have procedure): {len(non_grinding_recipes)}")

print("\n" + "=" * 70)
print("RECIPES WITH GRINDING/CHOPPING/POUNDING")
print("=" * 70)

# Analyze instruction sequences for grinding recipes
grinding_sequences = defaultdict(list)
grinding_first_instructions = defaultdict(int)
grinding_has_aux = 0

for r in grinding_recipes:
    print(f"\n#{r['id']}: {r['name']}")
    print(f"  Keywords: {r['keywords']}")
    print(f"  Sequence: {r['sequence']}")
    print(f"  Material: {r['material_class']}, Fire: {r['fire_degree']}")
    print(f"  Procedure: {r['procedure'][:100]}...")

    # Track sequences
    seq_str = ' -> '.join(r['sequence']) if r['sequence'] else 'EMPTY'
    grinding_sequences[seq_str].append(r['name'])

    # Track first instruction
    if r['sequence']:
        grinding_first_instructions[r['sequence'][0]] += 1

    # Track AUX presence
    if 'AUX' in r['sequence']:
        grinding_has_aux += 1

print("\n" + "=" * 70)
print("PATTERN ANALYSIS: GRINDING RECIPES")
print("=" * 70)

print("\nInstruction sequences in grinding recipes:")
for seq, recipes in sorted(grinding_sequences.items(), key=lambda x: -len(x[1])):
    print(f"  {seq}: {len(recipes)} recipes")
    for name in recipes[:5]:
        print(f"    - {name}")
    if len(recipes) > 5:
        print(f"    ... and {len(recipes)-5} more")

print("\nFirst instruction in grinding recipes:")
for instr, count in sorted(grinding_first_instructions.items(), key=lambda x: -x[1]):
    pct = 100*count/len(grinding_recipes) if grinding_recipes else 0
    print(f"  {instr}: {count} recipes ({pct:.1f}%)")

print("\n" + "=" * 70)
print("COMPARISON: NON-GRINDING RECIPES")
print("=" * 70)

non_grinding_first = defaultdict(int)
non_grinding_has_aux = 0

for r in non_grinding_recipes:
    if r['sequence']:
        non_grinding_first[r['sequence'][0]] += 1
    if 'AUX' in r['sequence']:
        non_grinding_has_aux += 1

print("\nFirst instruction in NON-grinding recipes:")
for instr, count in sorted(non_grinding_first.items(), key=lambda x: -x[1]):
    pct = 100*count/len(non_grinding_recipes) if non_grinding_recipes else 0
    print(f"  {instr}: {count} recipes ({pct:.1f}%)")

print("\n" + "=" * 70)
print("KEY FINDING: Does AUX correlate with grinding?")
print("=" * 70)

grinding_aux_rate = grinding_has_aux / len(grinding_recipes) if grinding_recipes else 0
non_grinding_aux_rate = non_grinding_has_aux / len(non_grinding_recipes) if non_grinding_recipes else 0

print(f"\nGrinding recipes with AUX: {grinding_has_aux}/{len(grinding_recipes)} ({100*grinding_aux_rate:.1f}%)")
print(f"Non-grinding recipes with AUX: {non_grinding_has_aux}/{len(non_grinding_recipes)} ({100*non_grinding_aux_rate:.1f}%)")

if non_grinding_aux_rate > 0:
    ratio = grinding_aux_rate / non_grinding_aux_rate
    print(f"\nRatio: Grinding recipes are {ratio:.2f}x more likely to have AUX")

    # Chi-square test
    from scipy import stats
    import numpy as np

    # Contingency table: [grinding, non-grinding] x [has_aux, no_aux]
    table = np.array([
        [grinding_has_aux, len(grinding_recipes) - grinding_has_aux],
        [non_grinding_has_aux, len(non_grinding_recipes) - non_grinding_has_aux]
    ])
    print(f"\nContingency table:")
    print(f"                  Has AUX   No AUX")
    print(f"  Grinding:       {table[0,0]:7}  {table[0,1]:7}")
    print(f"  Non-grinding:   {table[1,0]:7}  {table[1,1]:7}")

    # Only run chi-square if we have enough data
    if table.min() >= 5:
        chi2, p, dof, expected = stats.chi2_contingency(table)
        print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.4f}, dof={dof}")
        if p < 0.05:
            print("  SIGNIFICANT: AUX is significantly associated with grinding")
        else:
            print("  NOT SIGNIFICANT: Association is not statistically significant")
    else:
        # Use Fisher's exact test for small samples
        odds_ratio, p = stats.fisher_exact(table)
        print(f"\nFisher's exact test: odds_ratio={odds_ratio:.2f}, p={p:.4f}")
        if p < 0.05:
            print("  SIGNIFICANT: AUX is significantly associated with grinding")
        else:
            print("  NOT SIGNIFICANT: Association is not statistically significant")

print("\n" + "=" * 70)
print("DOES AUX APPEAR FIRST IN GRINDING RECIPES?")
print("=" * 70)

grinding_aux_first = sum(1 for r in grinding_recipes if r['sequence'] and r['sequence'][0] == 'AUX')
non_grinding_aux_first = sum(1 for r in non_grinding_recipes if r['sequence'] and r['sequence'][0] == 'AUX')

print(f"\nGrinding recipes with AUX FIRST: {grinding_aux_first}/{len(grinding_recipes)} ({100*grinding_aux_first/len(grinding_recipes) if grinding_recipes else 0:.1f}%)")
print(f"Non-grinding recipes with AUX FIRST: {non_grinding_aux_first}/{len(non_grinding_recipes)} ({100*non_grinding_aux_first/len(non_grinding_recipes) if non_grinding_recipes else 0:.1f}%)")

if grinding_aux_first > 0 and len(non_grinding_recipes) > 0:
    g_rate = grinding_aux_first / len(grinding_recipes)
    n_rate = non_grinding_aux_first / len(non_grinding_recipes)
    if n_rate > 0:
        print(f"Ratio: Grinding recipes are {g_rate/n_rate:.2f}x more likely to have AUX FIRST")

print("\n" + "=" * 70)
print("MATERIAL CLASS BREAKDOWN")
print("=" * 70)

grinding_by_class = defaultdict(int)
for r in grinding_recipes:
    grinding_by_class[r['material_class']] += 1

print("\nGrinding recipes by material class:")
for cls, count in sorted(grinding_by_class.items(), key=lambda x: -x[1]):
    print(f"  {cls}: {count} recipes")

print("\n" + "=" * 70)
print("HCM HYPOTHESIS SUMMARY")
print("=" * 70)
print("""
HYPOTHESIS: B communicates "grinding/physical prep needed" through AUX

Mechanism:
1. B encodes "support operations required" (AUX role)
2. AUX appears disproportionately in grinding recipes
3. Human operator infers: "AUX heavy profile = material needs physical prep"

This does NOT violate C171 because:
- B doesn't encode "grind" as a discrete step
- B encodes an operational profile (high support requirement)
- Human INFERS the specific prep action from domain knowledge
""")
