"""
f75r dark pipeline referent analysis.

Ch19 recipe referents (things that need names):
  1. Aqua vitae (starting substance)
  2. Honey / honeycomb (material addition — possibly 1 item with wax)
  3. Wax (if separate)
  4. Water bath / balneum mariae (apparatus)
  5. Distillation vessel (alembic)
  6. Quintessence (product)
  = 4 to 6 distinct referents

f75r has 11 unique dark MIDDLEs. Does the count make sense?
Can we identify which ones name which referents?
"""

import sys, os, io, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
f75r = [t for t in all_b if t.folio == 'f75r']

def get_phase(line):
    lnum = int(line)
    if lnum <= 5: return 'ASSESS'
    elif lnum <= 6: return 'HEAT'
    elif lnum <= 12: return 'DISTILL'
    elif lnum <= 16: return 'REPEAT'
    elif lnum <= 22: return 'FERMENT'
    elif lnum <= 26: return 'RESTART'
    elif lnum <= 27: return 'QUALITY'
    elif lnum <= 31: return 'RE-DISTILL'
    else: return 'MAIN-LOOP'

# Build dark MIDDLE inventory on f75r
print("f75r DARK PIPELINE: REFERENT ANALYSIS")
print("=" * 100)

dark_appearances = defaultdict(list)
for t in f75r:
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        line_toks = [x for x in f75r if x.line == t.line]
        words = [x.word for x in line_toks]
        idx = next(i for i, x in enumerate(line_toks) if x.word == t.word)
        prev_w = words[idx-1] if idx > 0 else '(START)'
        next_w = words[idx+1] if idx < len(words)-1 else '(END)'
        has_dar = 'dar' in words or 'dal' in words
        dark_appearances[m.middle].append({
            'line': t.line, 'phase': get_phase(t.line),
            'word': t.word, 'prev': prev_w, 'next': next_w,
            'near_dar': has_dar,
        })

# Corpus stats per dark MIDDLE
mid_stats = {}
for mid in dark_appearances:
    n_folios = len(set(t.folio for t in all_b if morph.extract(t.word).middle == mid))
    n_tokens = sum(1 for t in all_b if morph.extract(t.word).middle == mid)
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    mid_stats[mid] = {'n_folios': n_folios, 'n_tokens': n_tokens, 'atoms': atoms}

print(f"\nUnique dark MIDDLEs on f75r: {len(dark_appearances)}")
print(f"Total dark tokens on f75r: {sum(len(v) for v in dark_appearances.values())}")
print(f"\nRecipe needs ~4-6 referent names. We have 11 unique dark MIDDLEs.")
print()

# Show each dark MIDDLE with context
for mid in sorted(dark_appearances, key=lambda m: -len(dark_appearances[m])):
    apps = dark_appearances[mid]
    stats = mid_stats[mid]
    sel = "SELECTIVE" if stats['n_folios'] < 15 else "COMMON"

    print(f"  {mid:>6s}  [{stats['atoms']:>30s}]  {len(apps)}x on f75r  "
          f"({stats['n_tokens']} tok / {stats['n_folios']} fol)  {sel}")
    for a in apps:
        dar_flag = " ** NEAR DAR **" if a['near_dar'] else ""
        print(f"    L{a['line']:>2s} [{a['phase']:10s}]  "
              f"...{a['prev']} > {a['word']} > {a['next']}...{dar_flag}")
    print()

# Double-dar lines
print("=" * 100)
print("DOUBLE-DAR LINES (L35-36): Dark MIDDLEs present?")
print("=" * 100)
for li in ['35', '36']:
    lt = [t for t in f75r if t.line == li]
    words = [t.word for t in lt]
    darks = [(t.word, morph.extract(t.word).middle) for t in lt
             if morph.extract(t.word).middle in dp_set]
    print(f"\n  L{li}: {' '.join(words)}")
    if darks:
        for w, mid in darks:
            print(f"    DARK: {w} (mid={mid}, {mid_stats.get(mid, {}).get('atoms', '?')})")
    else:
        print(f"    No dark MIDDLEs — all grammar tokens")

# Balneum shared
print("\n" + "=" * 100)
print("BALNEUM FOLIO SHARED DARK MIDDLEs")
print("=" * 100)
balneum = ['f75r', 'f84r', 'f108r']
folio_darks = {}
for f in balneum:
    folio_darks[f] = set()
    for t in all_b:
        if t.folio == f:
            m = morph.extract(t.word)
            if m.middle and m.middle in dp_set:
                folio_darks[f].add(m.middle)

for f in balneum:
    print(f"  {f}: {len(folio_darks[f])} dark MIDDLEs")

shared_all = folio_darks['f75r'] & folio_darks['f84r'] & folio_darks['f108r']
print(f"\n  All 3 share: {sorted(shared_all)}")
for mid in sorted(shared_all):
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    n_fol = len(set(t.folio for t in all_b if morph.extract(t.word).middle == mid))
    print(f"    {mid} ({atoms}) -- on {n_fol}/81 folios")

for pair in [('f75r','f84r'), ('f75r','f108r'), ('f84r','f108r')]:
    shared = folio_darks[pair[0]] & folio_darks[pair[1]] - shared_all
    if shared:
        print(f"\n  {pair[0]}+{pair[1]} share (not all 3): {sorted(shared)}")
        for mid in sorted(shared):
            atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
            n_fol = len(set(t.folio for t in all_b if morph.extract(t.word).middle == mid))
            sel = "<-- SELECTIVE" if n_fol < 15 else ""
            print(f"    {mid} ({atoms}) -- on {n_fol}/81 folios {sel}")

# Referent hypothesis
print("\n" + "=" * 100)
print("REFERENT HYPOTHESIS")
print("=" * 100)
print("""
  Recipe needs: aqua vitae, honey/wax (honeycomb?), water bath, vessel, product

  11 dark MIDDLEs > 4-6 referents means some MIDDLEs name the SAME thing
  in different contexts (different property being identified), OR some
  name conditions/states rather than materials.

  Grouping by context:

  APPEARS 2x (primary referents?):
    lch  (state.adjust.watch)     -- L2 (assess) + L16 (repeat end)
    ksh  (heat.sequence.watch)    -- L7 (distill) + L19 (ferment)
    eet  (cool.cool.transfer)     -- L35 (double-dar) + L37 (thermal block)

  APPEARS 1x, NEAR DAR/DAL (material-adjacent):
    epc  (cool.pause.adjust)      -- L17 (ferment start, has dal)

  APPEARS 1x, AT QUALITY/TRANSITION:
    eke  (cool.heat.cool)         -- L2 (assess)
    q    (?)                      -- L3 (assess)
    es   (cool.sequence)          -- L14 (repeat)
    lsh  (state.sequence.watch)   -- L27 (quality gate)
    ls   (state.sequence)         -- L32 (loop start)
    cth  (adjust.transfer.watch)  -- L33 (loop)
    lk   (state.heat)             -- L34 (pre-addition)
""")
