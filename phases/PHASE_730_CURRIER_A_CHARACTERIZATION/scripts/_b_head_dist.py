import sys
sys.path.insert(0, 'C:/git/voynich')
from collections import Counter
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES
tx = Transcript(); morph = Morphology()
head = Counter(); term = Counter(); n = 0; action = 0
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    n += 1
    try:
        m = morph.extract(w); a = morph.atomize(w)
    except Exception:
        continue
    if (m.suffix or '') in ('dy', 'edy', 'eedy'):
        action += 1
    if hasattr(a, 'atoms'):
        for c, r, _ in a.atoms:
            if r == 'HEAD':
                head[c] += 1
            elif r == 'TERM':
                term[c] += 1
print('B tokens:', n, 'action-form:', f'{100*action/n:.1f}%')
print('B HEAD dist:')
for atom, ct in head.most_common():
    print(f'  {atom} ({ATOM_GLOSSES.get(atom, "?")}): {100*ct/sum(head.values()):.1f}%')
print('B TERM dist:')
for atom, ct in term.most_common(6):
    print(f'  {atom} ({ATOM_GLOSSES.get(atom, "?")}): {100*ct/sum(term.values()):.1f}%')
