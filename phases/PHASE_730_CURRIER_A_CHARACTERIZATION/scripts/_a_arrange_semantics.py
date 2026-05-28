"""What does o-HEAD 'arrange/stage' dominance in Currier A mean?

The project glosses o-HEAD as 'arrange' (C1195) / 'staging' (GUIDE B-grammar).
A is 44% o-HEAD vs B's 16%. This tests what the arrangement dominance tracks.

Tests:
1. Section distribution: does o-HEAD concentrate in H (herbal/plants), P (pharma), or T (text)?
   If 'arrange'=botanical structure, H should be highest.
   If 'arrange'=staging/organization, could be uniform or pharma-concentrated.
2. Reconcile with C1266 section atom profiles (H closure/monitoring, P stability/energy, T iteration/energy)
3. Within-section o-HEAD variation: per-folio, does o-HEAD rate correlate with anything measurable?
4. o-HEAD vs other HEADs: what MIDDLEs are o-HEAD in A? Are they distinct from B's o-HEAD MIDDLEs?
"""
import sys
from collections import defaultdict, Counter

import numpy as np

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript(); morph = Morphology()

# Section mapping — A folios are in H/P/T. Use the transcript's section info.
# Collect per-token: folio, section, HEAD atom
folio_section = {}
section_head = defaultdict(Counter)
section_total = Counter()
folio_head = defaultdict(Counter)
folio_total = Counter()

for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    # Section: use placement/illustration info. The transcript has section codes.
    sec = getattr(t, 'section', None) or getattr(t, 'illustration_type', None) or '?'
    folio_section[t.folio] = sec
    try:
        a = morph.atomize(w)
    except Exception:
        continue
    head = None
    if hasattr(a, 'atoms'):
        for c, r, _ in a.atoms:
            if r == 'HEAD':
                head = c
                break
    section_total[sec] += 1
    folio_total[t.folio] += 1
    if head:
        section_head[sec][head] += 1
        folio_head[t.folio][head] += 1

print('Sections found:', dict(section_total))
print()

# o-HEAD rate by section
print('=== o-HEAD (arrange/stage) rate by section ===')
for sec in sorted(section_total.keys()):
    o_rate = section_head[sec].get('o', 0) / section_total[sec] if section_total[sec] else 0
    e_rate = section_head[sec].get('e', 0) / section_total[sec] if section_total[sec] else 0
    k_rate = section_head[sec].get('k', 0) / section_total[sec] if section_total[sec] else 0
    a_rate = section_head[sec].get('a', 0) / section_total[sec] if section_total[sec] else 0
    print(f'  Section {sec}: o={o_rate:.1%} e={e_rate:.1%} k={k_rate:.1%} a={a_rate:.1%} (n={section_total[sec]})')

# Per-folio o-HEAD distribution
print('\n=== Per-folio o-HEAD rate distribution ===')
o_rates = []
for f in folio_total:
    if folio_total[f] >= 20:
        o_rates.append(folio_head[f].get('o', 0) / folio_total[f])
o_rates = np.array(o_rates)
print(f'  Folios (>=20 tokens): {len(o_rates)}')
print(f'  o-HEAD rate: mean={o_rates.mean():.1%}, sd={o_rates.std():.1%}, range=[{o_rates.min():.1%}, {o_rates.max():.1%}]')

# Highest and lowest o-HEAD folios
folio_o = [(f, folio_head[f].get('o', 0) / folio_total[f]) for f in folio_total if folio_total[f] >= 20]
folio_o.sort(key=lambda x: -x[1])
print(f'\n  Highest o-HEAD folios: {[(f, f"{r:.0%}") for f, r in folio_o[:8]]}')
print(f'  Lowest o-HEAD folios:  {[(f, f"{r:.0%}") for f, r in folio_o[-8:]]}')

# What MIDDLEs carry o-HEAD in A?
print('\n=== Top o-HEAD MIDDLEs in Currier A ===')
o_middles = Counter()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        m = morph.extract(w)
        a = morph.atomize(w)
    except Exception:
        continue
    if not m.middle: continue
    head = None
    if hasattr(a, 'atoms'):
        for c, r, _ in a.atoms:
            if r == 'HEAD':
                head = c
                break
    if head == 'o':
        o_middles[m.middle] += 1
print(f'  Distinct o-HEAD MIDDLEs: {len(o_middles)}')
for mid, ct in o_middles.most_common(20):
    print(f'    {mid}: {ct}')
