"""How do we read Currier A? — atom-gloss decode of A records as state-descriptions.

Given the state-vs-action finding: A catalogs items in STATE form (bare,
l-terminal), B deploys same items in ACTION form (dy-sealed). So reading an
A record = reading state-descriptions in atom-gloss terms.

This script:
1. Shows the state-form (A) vs action-form (B) gloss for the dramatic-split MIDDLEs
2. Decodes sample A folio records into atom-glosses
3. Characterizes what kind of content emerges (honest, not narrative-building)
"""
import sys
from collections import defaultdict, Counter

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

print('Atom glosses (C1195):')
for atom, gloss in ATOM_GLOSSES.items():
    print(f'  {atom} = {gloss}')

# ===== Part 1: state-form vs action-form for split MIDDLEs =====
print('\n' + '=' * 60)
print('PART 1: Same MIDDLE, state-form (A) vs action-form (B)')
print('=' * 60)

split_middles = ['ke', 'te', 'tee', 'pche', 'tche', 'opche']
print('\nThese MIDDLEs appear bare in A (state) but dy-sealed in B (action):')
for mid in split_middles:
    # atomize the bare middle (A state form) vs the dy form (B action form)
    a_form = morph.atomize(mid) if len(mid) >= 1 else None
    b_form = morph.atomize(mid + 'dy')
    a_gloss = a_form.gloss if a_form and hasattr(a_form, 'gloss') else '?'
    b_gloss = b_form.gloss if hasattr(b_form, 'gloss') else '?'
    print(f'\n  {mid}:')
    print(f'    A state-form  "{mid}"   -> atoms {a_form.atoms if a_form else "?"}')
    print(f'    B action-form "{mid}dy" -> atoms {b_form.atoms}')

# ===== Part 2: decode sample A folios =====
print('\n' + '=' * 60)
print('PART 2: A folio records decoded as state-descriptions')
print('=' * 60)

# Get A folios by line
folio_lines = defaultdict(lambda: defaultdict(list))
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        ln = int(t.line)
    except (ValueError, TypeError):
        ln = 0
    folio_lines[t.folio][ln].append(w)

# Pick representative folios from each section
# Section H (herbal): f1r-ish; Section P (pharma): f88-ish; Section T (text): f58-ish
sample_folios = ['f1r', 'f3v', 'f88r']

def gloss_token(w):
    """Render a token's atom-gloss with state/action annotation."""
    try:
        a = morph.atomize(w)
        m = morph.extract(w)
    except Exception:
        return f'{w}[?]'
    suffix = m.suffix or ''
    # State vs action marker
    is_action = suffix in ('dy', 'edy', 'eedy')
    marker = '[ACTION]' if is_action else '[state]'
    gloss = a.gloss if hasattr(a, 'gloss') else '?'
    return f'{w} = {gloss} {marker}'

for folio in sample_folios:
    if folio not in folio_lines:
        print(f'\n{folio}: no data')
        continue
    print(f'\n--- {folio} ---')
    for ln in sorted(folio_lines[folio].keys())[:6]:
        words = folio_lines[folio][ln]
        print(f'  L{ln}: {" ".join(words)}')
        for w in words:
            print(f'      {gloss_token(w)}')

# ===== Part 3: characterize A content distribution =====
print('\n' + '=' * 60)
print('PART 3: What kind of content is in A? (aggregate characterization)')
print('=' * 60)

# Count state vs action tokens across all A
a_state = 0
a_action = 0
a_total = 0
# Head-atom distribution (operational domain)
head_dist = Counter()
term_dist = Counter()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    a_total += 1
    try:
        m = morph.extract(w)
        a = morph.atomize(w)
    except Exception:
        continue
    suffix = m.suffix or ''
    if suffix in ('dy', 'edy', 'eedy'):
        a_action += 1
    else:
        a_state += 1
    if hasattr(a, 'atoms'):
        for char, role, _ in a.atoms:
            if role == 'HEAD':
                head_dist[char] += 1
            elif role == 'TERM':
                term_dist[char] += 1

print(f'\nA tokens: {a_total}')
print(f'  State-form (bare/non-dy): {a_state} ({100*a_state/a_total:.1f}%)')
print(f'  Action-form (dy-sealed):  {a_action} ({100*a_action/a_total:.1f}%)')
print(f'\nHEAD-atom distribution (operational domain of each entry):')
for atom, count in head_dist.most_common():
    g = ATOM_GLOSSES.get(atom, '?')
    print(f'  {atom} ({g}): {count} ({100*count/sum(head_dist.values()):.1f}%)')
print(f'\nTERM-atom distribution (exit/state condition):')
for atom, count in term_dist.most_common(10):
    g = ATOM_GLOSSES.get(atom, '?')
    print(f'  {atom} ({g}): {count} ({100*count/sum(term_dist.values()):.1f}%)')
