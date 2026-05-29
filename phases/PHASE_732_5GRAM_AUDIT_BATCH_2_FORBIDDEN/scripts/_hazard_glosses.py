"""Do the 5 hazard classes' physical interpretations cohere with the atom glosses
of their constituent tokens?

For each forbidden transition in each class, show the atom gloss of source and target,
then assess whether the class's claimed physical failure mode is consistent with what
the atoms actually say.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Morphology

morph = Morphology()

CLASSES = {
    'ENERGY_OVERSHOOT': ('Too much heat too fast / scorching', [('he','t')]),
    'PHASE_ORDERING': ('Wrong sequence of phase changes / vapor lock', [
        ('shey','aiin'),('shey','al'),('shey','c'),('dy','aiin'),('dy','chey'),
        ('chey','chedy'),('chey','shedy')]),
    'RATE_MISMATCH': ('Flow rates incompatible / flooding', [('ar','dal')]),
    'COMPOSITION_JUMP': ('Skipping purification stages / contamination', [
        ('chedy','ee'),('c','ee'),('shedy','aiin'),('shedy','o')]),
    'CONTAINMENT_TIMING': ('Improper vessel state / overflow', [
        ('chol','r'),('l','chol'),('or','dal'),('he','or')]),
}

def gloss(tok):
    try:
        a = morph.atomize(tok)
        g = getattr(a, 'gloss', None)
        atoms = getattr(a, 'atoms', None)
        atom_str = '.'.join(f'{c}:{role}:{m}' for c, role, m in atoms) if atoms else 'n/a'
        return g, atom_str
    except Exception as e:
        return f'ERR({e})', 'n/a'

for cls, (interp, pairs) in CLASSES.items():
    print(f'\n{"="*80}')
    print(f'{cls}  --  claimed: "{interp}"')
    print('='*80)
    for src, tgt in pairs:
        sg, sa = gloss(src)
        tg, ta = gloss(tgt)
        print(f'  {src:>7} -> {tgt:<7}')
        print(f'    src {src:>7}: gloss="{sg}"  atoms=[{sa}]')
        print(f'    tgt {tgt:>7}: gloss="{tg}"  atoms=[{ta}]')
