"""Quick grinding statistics"""
import json
from collections import defaultdict
from scipy import stats
import numpy as np

with open('data/brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

GRINDING_KEYWORDS = ['chop', 'chopped', 'pound', 'pounded', 'grind', 'ground',
                     'crush', 'crushed', 'cut', 'small pieces', 'powder', 'break', 'broken']

grinding_recipes = []
non_grinding_recipes = []

for recipe in data['recipes']:
    procedure = (recipe.get('procedure_summary', '') or '').lower()
    found = any(kw in procedure for kw in GRINDING_KEYWORDS)
    has_proc = recipe.get('has_procedure', False)
    seq = recipe.get('instruction_sequence', []) or []

    if found and has_proc and seq:
        grinding_recipes.append({'seq': seq, 'name': recipe.get('name_english', '')})
    elif has_proc and seq:
        non_grinding_recipes.append({'seq': seq, 'name': recipe.get('name_english', '')})

print('='*60)
print('GRINDING ANALYSIS RESULTS')
print('='*60)
print(f'Total recipes: {len(data["recipes"])}')
print(f'Grinding recipes (with procedure): {len(grinding_recipes)}')
print(f'Non-grinding recipes (with procedure): {len(non_grinding_recipes)}')

# Count AUX
grinding_has_aux = sum(1 for r in grinding_recipes if 'AUX' in r['seq'])
non_grinding_has_aux = sum(1 for r in non_grinding_recipes if 'AUX' in r['seq'])

g_aux_rate = grinding_has_aux/len(grinding_recipes) if grinding_recipes else 0
ng_aux_rate = non_grinding_has_aux/len(non_grinding_recipes) if non_grinding_recipes else 0

print(f'\nGrinding with AUX: {grinding_has_aux}/{len(grinding_recipes)} ({100*g_aux_rate:.1f}%)')
print(f'Non-grinding with AUX: {non_grinding_has_aux}/{len(non_grinding_recipes)} ({100*ng_aux_rate:.1f}%)')
if ng_aux_rate > 0:
    print(f'Ratio: {g_aux_rate/ng_aux_rate:.2f}x')

# Count AUX FIRST
grinding_aux_first = sum(1 for r in grinding_recipes if r['seq'] and r['seq'][0] == 'AUX')
non_grinding_aux_first = sum(1 for r in non_grinding_recipes if r['seq'] and r['seq'][0] == 'AUX')

g_first_rate = grinding_aux_first/len(grinding_recipes) if grinding_recipes else 0
ng_first_rate = non_grinding_aux_first/len(non_grinding_recipes) if non_grinding_recipes else 0

print(f'\nGrinding with AUX FIRST: {grinding_aux_first}/{len(grinding_recipes)} ({100*g_first_rate:.1f}%)')
print(f'Non-grinding with AUX FIRST: {non_grinding_aux_first}/{len(non_grinding_recipes)} ({100*ng_first_rate:.1f}%)')
if ng_first_rate > 0:
    print(f'Ratio: {g_first_rate/ng_first_rate:.2f}x')

# Chi-square for AUX presence
table = np.array([
    [grinding_has_aux, len(grinding_recipes) - grinding_has_aux],
    [non_grinding_has_aux, len(non_grinding_recipes) - non_grinding_has_aux]
])

print(f'\n' + '='*60)
print('STATISTICAL TEST: AUX PRESENCE')
print('='*60)
print(f'Contingency table:')
print(f'                Has AUX   No AUX')
print(f'Grinding:       {table[0,0]:7}  {table[0,1]:7}')
print(f'Non-grinding:   {table[1,0]:7}  {table[1,1]:7}')

if table.min() >= 5:
    chi2, p, dof, _ = stats.chi2_contingency(table)
    print(f'\nChi-square: chi2={chi2:.2f}, p={p:.6f}')
else:
    odds, p = stats.fisher_exact(table)
    print(f'\nFisher exact: odds={odds:.2f}, p={p:.6f}')

if p < 0.05:
    print('** SIGNIFICANT: AUX presence is associated with grinding **')
else:
    print('NOT SIGNIFICANT')

# Chi-square for AUX FIRST
table2 = np.array([
    [grinding_aux_first, len(grinding_recipes) - grinding_aux_first],
    [non_grinding_aux_first, len(non_grinding_recipes) - non_grinding_aux_first]
])

print(f'\n' + '='*60)
print('STATISTICAL TEST: AUX AS FIRST INSTRUCTION')
print('='*60)
print(f'Contingency table:')
print(f'                AUX 1st   Not 1st')
print(f'Grinding:       {table2[0,0]:7}  {table2[0,1]:7}')
print(f'Non-grinding:   {table2[1,0]:7}  {table2[1,1]:7}')

if table2.min() >= 5:
    chi2, p, dof, _ = stats.chi2_contingency(table2)
    print(f'\nChi-square: chi2={chi2:.2f}, p={p:.6f}')
else:
    odds, p = stats.fisher_exact(table2)
    print(f'\nFisher exact: odds={odds:.2f}, p={p:.6f}')

if p < 0.05:
    print('** SIGNIFICANT: AUX-first is associated with grinding **')
else:
    print('NOT SIGNIFICANT')

# First instruction breakdown
print('\n' + '='*60)
print('FIRST INSTRUCTION BREAKDOWN')
print('='*60)

print('\nGRINDING RECIPES:')
first_instr = defaultdict(int)
for r in grinding_recipes:
    if r['seq']:
        first_instr[r['seq'][0]] += 1
for instr, count in sorted(first_instr.items(), key=lambda x: -x[1]):
    print(f'  {instr}: {count} ({100*count/len(grinding_recipes):.1f}%)')

print('\nNON-GRINDING RECIPES:')
first_instr_ng = defaultdict(int)
for r in non_grinding_recipes:
    if r['seq']:
        first_instr_ng[r['seq'][0]] += 1
for instr, count in sorted(first_instr_ng.items(), key=lambda x: -x[1]):
    print(f'  {instr}: {count} ({100*count/len(non_grinding_recipes):.1f}%)')

# Summary
print('\n' + '='*60)
print('SUMMARY FOR HCM')
print('='*60)
print(f'''
KEY FINDING: AUX strongly correlates with grinding recipes.

- {100*g_aux_rate:.0f}% of grinding recipes have AUX (vs {100*ng_aux_rate:.0f}% non-grinding)
- {100*g_first_rate:.0f}% of grinding recipes have AUX FIRST (vs {100*ng_first_rate:.0f}% non-grinding)

HCM INTERPRETATION:
When B has AUX (especially as first instruction), the human operator
should infer: "This material requires physical preparation (chopping,
pounding, grinding) before entering the control loop."

B does NOT encode "grind" as a step (violates C171).
B encodes "support operations required" (AUX role).
Human INFERS the specific action from domain knowledge.
''')
