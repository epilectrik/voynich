"""Check fire degree distribution across verb profiles."""
import json
from collections import Counter

with open('phases/PREP_POSTURE_DIVERGENCE/results/recipe_verb_profiles.json', 'r') as f:
    data = json.load(f)
profiles = data['profiles']

# Fire degree distribution
fire_degrees = Counter(p['fire_degree'] for p in profiles)
print('Fire degree distribution:')
for fd, count in sorted(fire_degrees.items()):
    print(f'  Degree {fd}: {count} recipes ({100*count/len(profiles):.1f}%)')

# Fire degree by dominant verb
print('\nFire degree by dominant verb:')
by_verb = {}
for p in profiles:
    verb = p['dominant_verb']
    fd = p['fire_degree']
    if verb not in by_verb:
        by_verb[verb] = []
    by_verb[verb].append(fd)

for verb in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'COLLECT', 'CRUSH', 'WASH', 'BREAK']:
    fds = by_verb.get(verb, [])
    if fds:
        avg = sum(fds) / len(fds)
        dist = Counter(fds)
        print(f'  {verb} (n={len(fds)}): avg={avg:.2f}, dist={dict(dist)}')
