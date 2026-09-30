#!/usr/bin/env python3
"""PHASE_772 lock audit (lean-expert): STRUCTURAL counts only.

Prints locus-type sequence per zodiac page, clock presence, ring counter as zod772 assigns it, word counts,
readability and edit-site applicability. Never prints a label form and never computes any duplicate /
recurrence statistic (R, W, D_w, D_a) on the real labels.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zod772 as Z  # noqa: E402

seq = defaultdict(list)          # folio -> list of (type, has_clock, ring_at_time, nwords, readable)
cur, ring = None, 0
excl = Counter()
multiword = Counter()
alt = Counter()
types_seen = Counter()
for raw in open(Z.ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f\w+)>', raw)
    if m and not re.match(r'^<f\w+\.', raw):
        cur, ring = (m.group(1) if m.group(1) in Z.SIGN else None), 0
        continue
    if cur is None:
        continue
    m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
    if not m or m.group(1) != cur:
        if raw.startswith('<' + cur + '.') if cur else False:
            types_seen[('UNPARSED', cur)] += 1
        continue
    kind, body = m.group(4), m.group(5)
    types_seen[kind] += 1
    clock = re.match(r'<!(\d\d):(\d\d)>', body)
    if kind[0] in 'CR':
        ring += 1
        seq[cur].append((kind, clock is not None, ring, None, None))
        continue
    if not kind.startswith('L'):
        seq[cur].append((kind, clock is not None, ring, None, None))
        continue
    cb = Z.clean(body)
    words = [w for w in re.split(r'[.,]', cb) if w]
    form = ''.join(re.split(r'[.,]', cb))
    readable = bool(form) and bool(re.fullmatch(r'[a-z]+', form))
    if re.search(r'\[[^\]]*:', body):
        alt[Z.SIGN[cur]] += 1
    if clock is not None and not readable:
        excl[Z.SIGN[cur]] += 1
    if clock is not None and readable and len(words) >= 2:
        multiword[Z.SIGN[cur]] += 1
    seq[cur].append((kind, clock is not None, ring, len(words), readable))

print('locus types on zodiac pages:', dict(types_seen))
for f in Z.SIGN:
    s = seq.get(f, [])
    compact = []
    for kind, ck, rg, nw, rd in s:
        if kind.startswith('L'):
            compact.append(f"L{'' if ck else '(noclk)'}{'' if rd in (True, None) else '(X)'}")
        else:
            compact.append(f'[{kind}{"+clk" if ck else ""}->r{rg}]')
    # run-length compress
    out, prev, n = [], None, 0
    for c in compact:
        if c == prev:
            n += 1
        else:
            if prev is not None:
                out.append(f'{prev}x{n}' if n > 1 else prev)
            prev, n = c, 1
    if prev is not None:
        out.append(f'{prev}x{n}' if n > 1 else prev)
    print(f'{f:6s} {Z.SIGN[f]:11s}', ' '.join(out))
print('excluded unreadable labels with clock, by sign:', dict(excl), 'total', sum(excl.values()))
print('readable labels with 2+ words, by sign:', dict(multiword), 'total', sum(multiword.values()))
print('labels with alternative readings [a:b], by sign:', dict(alt), 'total', sum(alt.values()))

labels = Z.load_labels()
print('n labels', len(labels))
per_page = Counter((r['folio'], r['ring']) for r in labels)
print('labels per (page, ring):', dict(sorted(per_page.items())))
# clock ties within a ring
ties = 0
for (f, g), n in per_page.items():
    cl = [r['clock'] for r in labels if r['folio'] == f and r['ring'] == g]
    ties += len(cl) - len(set(cl))
print('clock ties within (page, ring):', ties)
# glyph-unit lengths (structural)
L = Counter(len(Z.GLYPH_RE.findall(Z.n1(r['form']))) for r in labels)
print('N1 glyph-unit length distribution:', dict(sorted(L.items())))
# edit-site applicability per form (structural, per-form, no cross-label comparison)
app = Counter()
for r in labels:
    w = r['form']
    app['e_run'] += bool(re.search('e', w))
    app['i_run'] += bool(re.search('i', w))
    app['ch_sh'] += ('ch' in w or 'sh' in w)
    app['gallows'] += bool(re.search('[ktpf]', w))
    app['oyq_initial'] += w[0] in 'oyq'
    app['end_applicable'] += any(w.endswith(a) for a in ('dy', 'ey', 'y', 'l', 'r', 'm'))
print('edit-site applicability (count of 290 forms):', dict(app))
