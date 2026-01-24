"""
Deeper grinding analysis - what DOES distinguish grinding from non-grinding?

Finding: AUX is universal (100% of all recipes)
Question: Is there ANY structural difference?
"""
import json
from collections import defaultdict, Counter

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

    entry = {
        'seq': seq,
        'name': recipe.get('name_english', ''),
        'material_class': recipe.get('material_class', ''),
        'fire_degree': recipe.get('fire_degree', 0),
        'procedure': procedure
    }

    if found and has_proc and seq:
        grinding_recipes.append(entry)
    elif has_proc and seq:
        non_grinding_recipes.append(entry)

print('='*60)
print('DEEPER ANALYSIS: What distinguishes grinding recipes?')
print('='*60)

# 1. Sequence length comparison
print('\n1. SEQUENCE LENGTH')
print('-'*40)
grinding_lengths = [len(r['seq']) for r in grinding_recipes]
non_grinding_lengths = [len(r['seq']) for r in non_grinding_recipes]

g_avg = sum(grinding_lengths)/len(grinding_lengths) if grinding_lengths else 0
ng_avg = sum(non_grinding_lengths)/len(non_grinding_lengths) if non_grinding_lengths else 0

print(f'Grinding avg sequence length: {g_avg:.2f}')
print(f'Non-grinding avg sequence length: {ng_avg:.2f}')

# 2. Full sequence comparison
print('\n2. COMPLETE SEQUENCES')
print('-'*40)

grinding_seqs = Counter(' -> '.join(r['seq']) for r in grinding_recipes)
non_grinding_seqs = Counter(' -> '.join(r['seq']) for r in non_grinding_recipes)

print('\nMost common GRINDING sequences:')
for seq, count in grinding_seqs.most_common(10):
    print(f'  {seq}: {count} ({100*count/len(grinding_recipes):.1f}%)')

print('\nMost common NON-GRINDING sequences:')
for seq, count in non_grinding_seqs.most_common(10):
    print(f'  {seq}: {count} ({100*count/len(non_grinding_recipes):.1f}%)')

# 3. What instructions appear BESIDES AUX?
print('\n3. NON-AUX INSTRUCTIONS')
print('-'*40)

def get_non_aux(seq):
    return [s for s in seq if s != 'AUX']

grinding_non_aux = Counter()
for r in grinding_recipes:
    for instr in get_non_aux(r['seq']):
        grinding_non_aux[instr] += 1

non_grinding_non_aux = Counter()
for r in non_grinding_recipes:
    for instr in get_non_aux(r['seq']):
        non_grinding_non_aux[instr] += 1

print('\nNon-AUX instructions in GRINDING recipes:')
for instr, count in grinding_non_aux.most_common():
    print(f'  {instr}: {count} ({100*count/len(grinding_recipes):.1f}%)')

print('\nNon-AUX instructions in NON-GRINDING recipes:')
for instr, count in non_grinding_non_aux.most_common():
    print(f'  {instr}: {count} ({100*count/len(non_grinding_recipes):.1f}%)')

# 4. Material class comparison
print('\n4. MATERIAL CLASS COMPARISON')
print('-'*40)

grinding_classes = Counter(r['material_class'] for r in grinding_recipes)
non_grinding_classes = Counter(r['material_class'] for r in non_grinding_recipes)

print('\nGRINDING by material class:')
for cls, count in grinding_classes.most_common():
    print(f'  {cls}: {count} ({100*count/len(grinding_recipes):.1f}%)')

print('\nNON-GRINDING by material class:')
for cls, count in non_grinding_classes.most_common():
    print(f'  {cls}: {count} ({100*count/len(non_grinding_recipes):.1f}%)')

# 5. Fire degree comparison
print('\n5. FIRE DEGREE COMPARISON')
print('-'*40)

grinding_fire = Counter(r['fire_degree'] for r in grinding_recipes)
non_grinding_fire = Counter(r['fire_degree'] for r in non_grinding_recipes)

print('\nGRINDING by fire degree:')
for deg, count in sorted(grinding_fire.items()):
    print(f'  Fire {deg}: {count} ({100*count/len(grinding_recipes):.1f}%)')

print('\nNON-GRINDING by fire degree:')
for deg, count in sorted(non_grinding_fire.items()):
    print(f'  Fire {deg}: {count} ({100*count/len(non_grinding_recipes):.1f}%)')

# 6. What do non-grinding recipes do instead?
print('\n6. WHAT DO NON-GRINDING RECIPES DO?')
print('-'*40)
print('\nSample non-grinding procedures:')
for r in non_grinding_recipes[:10]:
    print(f'\n  {r["name"]}:')
    print(f'    Procedure: {r["procedure"][:80]}...')
    print(f'    Sequence: {r["seq"]}')

# 7. Key insight
print('\n' + '='*60)
print('KEY INSIGHT')
print('='*60)
print('''
AUX is UNIVERSAL in Brunschwig - every recipe starts with preparation.

The question "does B communicate grind?" may be wrong.

Better question: Does Brunschwig's instruction taxonomy even ENCODE
the grinding/non-grinding distinction?

Look at the sequences - they're almost identical.
The grinding vs non-grinding is in the GERMAN TEXT, not the sequence.

This suggests:
1. AUX = "preparation required" (universal in distillation)
2. The SPECIFIC prep (grind, wash, collect) is NOT encoded in sequence
3. The specific prep comes from MATERIAL KNOWLEDGE, not B structure

IMPLICATION FOR HCM:
B may NOT communicate "grind" at all.
B communicates "preparation phase exists."
The human knows from MATERIAL CLASS what that preparation involves.
''')
