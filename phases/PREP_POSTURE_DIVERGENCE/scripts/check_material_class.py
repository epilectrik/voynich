"""Check material class distribution and correlation with verbs."""
import json
from collections import Counter

with open('phases/PREP_POSTURE_DIVERGENCE/results/recipe_verb_profiles.json', 'r') as f:
    data = json.load(f)
profiles = data['profiles']

# Material class distribution
mat_classes = Counter(p['material_class'] for p in profiles)
print('Material class distribution:')
for mc, count in mat_classes.most_common():
    print(f'  {mc}: {count} recipes ({100*count/len(profiles):.1f}%)')

# Material class by dominant verb
print('\nMaterial class by dominant verb:')
by_verb = {}
for p in profiles:
    verb = p['dominant_verb']
    mc = p['material_class']
    if verb not in by_verb:
        by_verb[verb] = Counter()
    by_verb[verb][mc] += 1

for verb in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'COLLECT', 'CRUSH', 'SELECT', 'BREAK']:
    mcs = by_verb.get(verb, Counter())
    if mcs:
        print(f'  {verb} (n={sum(mcs.values())}):')
        for mc, count in mcs.most_common(3):
            print(f'    {mc}: {count}')

# Dominant verb by material class
print('\nDominant verb by material class:')
by_class = {}
for p in profiles:
    mc = p['material_class']
    verb = p['dominant_verb']
    if mc not in by_class:
        by_class[mc] = Counter()
    by_class[mc][verb] += 1

for mc in ['herb', 'animal', 'root', 'flower', 'tree', 'mineral', 'fruit']:
    verbs = by_class.get(mc, Counter())
    if verbs:
        total = sum(verbs.values())
        print(f'  {mc} (n={total}):')
        for verb, count in verbs.most_common(3):
            print(f'    {verb}: {count} ({100*count/total:.1f}%)')
