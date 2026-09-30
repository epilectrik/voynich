#!/usr/bin/env python3
"""PHASE_771 lock audit, Arm E (lean-expert). Blind: break records keep POSITIONS only (the readability test is the
same boolean the design uses); no glyph of a break-adjacent word is stored, printed or scored. Synthetic "break words"
are drawn from unbroken lines only.

Checks: (1) '<->' neighbour classes (separator vs letter) in cleaned P text; (2) paragraph-start / paragraph-end
shares of the line-edge reference and of break lines; (3) hand composition of breaks vs reference lines;
(4) expected I under realistic synthetic alternatives with the design as written; (5) quick power of a corrected
design (paragraph-initial starts / paragraph-final ends removed from the edge class).
"""
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

t0 = time.time()
recs = Z.load()

# (1) neighbour classes of '<->' in cleaned paragraph text
nb = Counter()
for raw in open(Z.ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
    if not m or not m.group(4).startswith('P'):
        continue
    t = Z.clean(m.group(5))
    t = re.sub(r'<(?!->)[^>]*>', '', t)
    for mm in re.finditer(re.escape('<->'), t):
        a = t[mm.start() - 1] if mm.start() > 0 else '^'
        b = t[mm.end()] if mm.end() < len(t) else '$'
        cls = lambda c: 'sep' if c in '.,' else ('letter' if c.isalpha() else ('edge' if c in '^$' else 'other'))
        nb[(cls(a), cls(b))] += 1
print('(1) <-> neighbour classes (before, after):', dict(nb))

# tables with paragraph flags and hand; breaks WITHOUT word strings
lines = [{'folio': r['folio'], 'lang': r['lang'], 'section': r['section'], 'hand': r['hand'],
          'ps': r['par_start'], 'pe': r['par_end'], 'segs': S.words_of(r)} for r in recs if r['kind'].startswith('P')]
words, breaks = [], []
for ln in lines:
    if ln['lang'] not in ('A', 'B'):
        continue
    segs = ln['segs']
    flat = [w for s in segs for w in s]
    n = len(flat)
    if len(segs) == 1:
        if n < 3:
            continue
        for i, w in enumerate(flat):
            if Z.readable(w):
                u = Z.units(w)
                words.append({'folio': ln['folio'], 'lang': ln['lang'], 'section': ln['section'], 'hand': ln['hand'],
                              'ps': ln['ps'], 'pe': ln['pe'], 'i_start': i, 'i_end': n - 1 - i,
                              'first': u[0], 'last': u[-1]})
        continue
    before = 0
    for j in range(len(segs) - 1):
        before += len(segs[j])
        left, right = segs[j], segs[j + 1]
        if not left or not right or not (Z.readable(left[-1]) and Z.readable(right[0])):
            continue
        breaks.append({'folio': ln['folio'], 'lang': ln['lang'], 'section': ln['section'], 'hand': ln['hand'],
                       'ps': ln['ps'], 'pe': ln['pe'], 'post_i_start': before, 'post_is_last': before == n - 1,
                       'pre_i_end': n - before, 'pre_is_first': before - 1 == 0,
                       'n_breaks_line': len(segs) - 1, 'n_line': n})
del lines

# (2) paragraph-edge shares
for lang in ('A', 'B'):
    W = [w for w in words if w['lang'] == lang]
    ini = [w for w in W if w['i_start'] == 0]
    fin = [w for w in W if w['i_end'] == 0]
    Bk = [b for b in breaks if b['lang'] == lang]
    print(f'(2) {lang}: line-initial ref words {len(ini)}, from paragraph-initial lines {sum(w["ps"] for w in ini)}; '
          f'line-final ref words {len(fin)}, from paragraph-final lines {sum(w["pe"] for w in fin)}; '
          f'breaks {len(Bk)}, on paragraph-first lines {sum(b["ps"] for b in Bk)}, on paragraph-last lines '
          f'{sum(b["pe"] for b in Bk)}')

# (3) hand composition
for lang in ('A', 'B'):
    hb = Counter((b['section'], b['hand']) for b in breaks if b['lang'] == lang)
    hr = Counter((w['section'], w['hand']) for w in words if w['lang'] == lang and w['i_start'] == 0)
    print(f'(3) {lang} breaks by (section, hand):', dict(sorted(hb.items())))
    print(f'    {lang} ref lines by (section, hand):', dict(sorted(hr.items())))


# (4) expected I under synthetic alternatives, design as written
def pools(W, side):
    ukey = 'first' if side == 'start' else 'last'
    flag = 'ps' if side == 'start' else 'pe'
    P = defaultdict(list)
    for w in W:
        k, is_edge = S._word_keys(w, side)
        u = w[ukey]
        if is_edge:
            typ = 'par_edge' if w[flag] else 'cont_edge'
            for key in ((typ, w['folio']), (typ, w['section']), (typ,), ('all_edge', w['folio']),
                        ('all_edge', w['section']), ('all_edge',)):
                P[key].append(u)
        else:
            for key in (('mid', w['folio']) + k, ('mid', w['section']) + k, ('mid',) + k, ('midany', w['section'])):
                P[key].append(u)
        P[('anypos', w['section'])].append(u)
    return P


def draw(b, side, kind, P, rng):
    if kind in ('par_edge', 'cont_edge', 'all_edge'):
        cands = ((kind, b['folio']), (kind, b['section']), (kind,))
    elif kind == 'mid':
        k = S.break_key(b, side)
        cands = (('mid', b['folio']) + k, ('mid', b['section']) + k, ('mid',) + k, ('midany', b['section']))
    else:
        cands = ((kind, b['section']),)
    for c in cands:
        pool = P.get(c, [])
        if len(pool) >= 3:
            return pool[rng.integers(len(pool))]
    raise RuntimeError(kind)


rng = np.random.default_rng(4242)
for lang in ('A', 'B'):
    W = [w for w in words if w['lang'] == lang]
    for side in ('start', 'end'):
        arm = S.EdgeArm(W, breaks, lang, side, seed=771)
        P = pools(W, side)
        out = {}
        for kind in ('all_edge', 'cont_edge', 'par_edge', 'mid', 'midany', 'anypos'):
            rr = [arm.evaluate([draw(b, side, kind, P, rng) for b in arm.breaks], B=20, rng=rng) for _ in range(15)]
            out[kind] = round(float(np.mean([x['I'] for x in rr])), 3)
        gap = [round(x['edge'] - x['mid'], 3) for x in rr[0]['directions']]
        print(f'(4) {lang} {side} design-as-written mean I by synthetic source:', out, 'edge-mid gap', gap)
print('elapsed', round(time.time() - t0, 1), 's')

# (5) corrected design: paragraph-initial line starts (start side) / paragraph-final line ends (end side) removed from
# the edge class and from M_init / M_final; E-seg draws from continuation-line edges; quick power (40 sims, B=300)
NS, BB = 40, 300
for lang in ('A', 'B'):
    W = [w for w in words if w['lang'] == lang]
    for side in ('start', 'end'):
        flag = 'ps' if side == 'start' else 'pe'
        edge_pos = (lambda w: w['i_start'] == 0) if side == 'start' else (lambda w: w['i_end'] == 0)
        Wc = [w for w in W if not (edge_pos(w) and w[flag])]
        arm = S.EdgeArm(Wc, breaks, lang, side, seed=771)
        P = pools(W, side)
        res = {}
        for truth, kind, target in (('seg', 'cont_edge', 'E-seg'), ('line', 'mid', 'E-line')):
            calls, Is = Counter(), []
            for _ in range(NS):
                r = arm.evaluate([draw(b, side, kind, P, rng) for b in arm.breaks], B=BB, rng=rng)
                calls[r['call']] += 1
                Is.append(r['I'])
            res[truth] = {'correct': round(calls[target] / NS, 3), 'I_mean': round(float(np.mean(Is)), 3)}
        gap = [round(x['edge'] - x['mid'], 3) for x in r['directions']]
        print(f'(5) {lang} {side} corrected design: {res}; edge-mid gap per direction {gap}')
print('elapsed', round(time.time() - t0, 1), 's')
