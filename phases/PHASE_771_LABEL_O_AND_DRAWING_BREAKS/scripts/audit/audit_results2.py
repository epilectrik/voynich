#!/usr/bin/env python3
"""PHASE_771 results-wording audit, part 2 (lean-expert, unblinded). Checks only, no verdicts.

(a) Arm E: folio-bootstrap CI of the difference in articulator rate, post-break minus continuation-line start
    (break folios and reference folios resampled independently, as in the pre-registered design).
(b) Arm L post hoc: length-standardised p/f and l shares of label o-words with and without the Rosettes foldout
    (fRos), with folio-bootstrap CIs; the fRos share of label o-words.
(c) Arm E post hoc (A): folio-bootstrap CIs of pre-break last-unit shares; position-matched interior expectations.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

sys.path.insert(0, str(Z.ROOT))
from scripts.voynich import Morphology  # noqa: E402

rng = np.random.default_rng(97712)
recs = Z.load()
lines = S.text_lines(recs)
morph = Morphology()
art = lambda wd: bool(morph.extract(wd).has_articulator)
words, breaks = S.edge_tables(lines)
B = 2000


def folio_arr(recs_, fn):
    by = defaultdict(lambda: [0, 0])
    for r in recs_:
        by[r['folio']][0] += fn(r)
        by[r['folio']][1] += 1
    return np.array(list(by.values()), dtype=float)


def boot_rates(arr):
    idx = rng.integers(0, len(arr), (B, len(arr)))
    s = arr[idx].sum(axis=1)
    return s[:, 0] / s[:, 1]


# (a)
for lang in ('A', 'B'):
    W = [x for x in words if x['lang'] == lang]
    Bk = [b for b in breaks if b['lang'] == lang]
    ci = [x for x in W if x['i_start'] == 0 and not x['par_first_line']]
    mid = [x for x in W if x['i_start'] > 0 and x['i_end'] > 0]
    rb = boot_rates(folio_arr(Bk, lambda r: art(r['post'])))
    rc = boot_rates(folio_arr(ci, lambda r: art(r['word'])))
    rm = boot_rates(folio_arr(mid, lambda r: art(r['word'])))
    d1, d2 = rb - rc, rb - rm
    print(f'(a) {lang} articulator post-break - cont-initial: 95% CI {np.percentile(d1, 2.5):+.3f}..'
          f'{np.percentile(d1, 97.5):+.3f}; share of replicates >= 0: {np.mean(d1 >= 0):.3f}; '
          f'post-break - interior: {np.percentile(d2, 2.5):+.3f}..{np.percentile(d2, 97.5):+.3f}')
    ratio = rb / rc
    print(f'    ratio post-break / cont-initial: 95% CI {np.percentile(ratio, 2.5):.2f}..{np.percentile(ratio, 97.5):.2f}')

# (b)
items = S.label_o_items(recs)
prof = Counter(it[-2] for it in items)
tot = sum(prof.values())
print(f'(b) fRos label o-words: {sum(1 for it in items if it[0] == "fRos")} of {len(items)}; '
      f'fRos p/f {sum(1 for it in items if it[0] == "fRos" and it[-1] == "pf")}')


def std_share(its, c):
    tab = defaultdict(Counter)
    for it in its:
        tab[it[-2]][it[-1]] += 1
    out = 0.0
    for L, wL in prof.items():
        n = sum(tab[L].values())
        if n:
            out += (wL / tot) * tab[L][c] / n
    return out


byf = defaultdict(list)
for it in items:
    byf[it[0]].append(it)
fol = list(byf)
for c in ('pf', 'l', 't'):
    full = std_share(items, c)
    nofr = std_share([it for it in items if it[0] != 'fRos'], c)
    bs = []
    for _ in range(B):
        pick = rng.integers(0, len(fol), len(fol))
        bs.append(std_share([it for j in pick for it in byf[fol[j]]], c))
    print(f'    labels standardised {c}: {full:.3f} (folio-boot 95% CI {np.percentile(bs, 2.5):.3f}..'
          f'{np.percentile(bs, 97.5):.3f}); without fRos {nofr:.3f}')

# (c)
W = [x for x in words if x['lang'] == 'A']
Bk = [b for b in breaks if b['lang'] == 'A']
fin = [x for x in W if x['i_end'] == 0 and not x['par_last_line']]
mid = [x for x in W if x['i_start'] > 0 and x['i_end'] > 0]
last = lambda wd: Z.units(wd)[-1]
pos = defaultdict(Counter)
for x in mid:
    pos[(x['section'], min(x['i_end'], 8))][last(x['word'])] += 1
for u in ('l', 'r', 'y', 's', 'd', 'iin', 'o', 'm'):
    rb = boot_rates(folio_arr(Bk, lambda r: last(r['pre']) == u))
    rf = boot_rates(folio_arr(fin, lambda r: last(r['word']) == u))
    ri = boot_rates(folio_arr(mid, lambda r: last(r['word']) == u))
    k = sum(last(b['pre']) == u for b in Bk)
    e = 0.0
    for b in Bk:
        cc = pos[(b['section'], min(b['pre_i_end'], 8))]
        e += cc[u] / sum(cc.values())
    pc = lambda r: f'{np.percentile(r, 2.5):.3f}..{np.percentile(r, 97.5):.3f}'
    print(f'(c) A last unit {u:>3}: pre-break {k}/512 CI {pc(rb)}; cont-final CI {pc(rf)}; interior CI {pc(ri)}; '
          f'position-matched interior expectation {e:.1f}')
