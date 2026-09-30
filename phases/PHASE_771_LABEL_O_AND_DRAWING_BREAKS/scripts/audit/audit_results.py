#!/usr/bin/env python3
"""PHASE_771 results-wording audit (lean-expert, after the locked run; unblinded). Checks only, no verdicts.

Arm L: (1) reproduce the primary expected counts; (2) folio-cluster bootstrap of the fitted-mixture residuals
(weights refitted per replicate); (3) folio concentration of the p/f, t, l, k label counts.
Arm E: (4) reproduce the descriptive rates; (5) folio-cluster bootstrap intervals for them; (6) position-matched
mid-line expectations; (7) the bare-aiin post-break cases and their pre-break neighbours (cut-word check).
"""
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

sys.path.insert(0, str(Z.ROOT))
from scripts.voynich import Morphology  # noqa: E402

t0 = time.time()
rng = np.random.default_rng(97711)
recs = Z.load()
lines = S.text_lines(recs)

# ---------------- Arm L ----------------
items = S.label_o_items(recs)
cnt = S.references_by_length(lines)
comps = S.comps_grouped(cnt)
folios, C = S.grouped_counts(items)
fit = S.grouped_fit(C, comps)
w = np.asarray(fit[0] if isinstance(fit, tuple) else fit, dtype=float)
print('(1) grouped_fit returned', type(fit), 'weights', np.round(w, 4))


def expected(Cm, wv):
    n_g = Cm.sum(axis=(0, 2))                       # per group totals
    mix = np.einsum('k,gkc->gc', wv, comps)         # G x cats
    return (n_g[:, None] * mix).sum(axis=0)


obs = C.sum(axis=(0, 1))
exp = expected(C, w)
print('    obs  ', dict(zip(S.CATS, obs.astype(int))))
print('    exp  ', dict(zip(S.CATS, np.round(exp, 1))))
res = obs - exp
KEY = ['l', 'k', 't', 'pf', 'r', 'e', 's']
B = 1000
boot = np.zeros((B, len(S.CATS)))
F = C.shape[0]
for b in range(B):
    idx = rng.integers(0, F, F)
    Cb = C[idx]
    fb = S.grouped_fit(Cb, comps)
    wb = np.asarray(fb[0] if isinstance(fb, tuple) else fb, dtype=float)
    boot[b] = Cb.sum(axis=(0, 1)) - expected(Cb, wb)
print(f'(2) residual (obs - exp, weights refitted), folio bootstrap B={B} ({time.time() - t0:.0f} s):')
for c in KEY:
    i = S.CIDX[c]
    lo, hi = np.percentile(boot[:, i], [2.5, 97.5])
    print(f'    {c:>3}: {res[i]:+6.1f}  95% CI {lo:+6.1f} .. {hi:+6.1f}')

# (3) folio concentration
per_f = defaultdict(Counter)
sysf = {}
for it in items:
    per_f[it[0]][it[-1]] += 1
    sysf[it[0]] = S.label_system(it[2])
for c in ('pf', 't', 'l', 'k'):
    tot = sum(v[c] for v in per_f.values())
    top = sorted(((v[c], f) for f, v in per_f.items()), reverse=True)[:4]
    nf = sum(1 for v in per_f.values() if v[c] > 0)
    print(f'(3) {c}: {tot} label words on {nf} folios; top: {[(f, n, sysf[f]) for n, f in top]}; '
          f'top-folio share {top[0][0] / tot:.2f}, top-3 share {sum(n for n, _ in top[:3]) / tot:.2f}')
# leave-one-folio-out residual range for pf, t, l
for c in ('pf', 't', 'l'):
    i = S.CIDX[c]
    vals = []
    for j in range(F):
        keep = np.ones(F, bool)
        keep[j] = False
        Cj = C[keep]
        fj = S.grouped_fit(Cj, comps)
        wj = np.asarray(fj[0] if isinstance(fj, tuple) else fj, dtype=float)
        vals.append((Cj.sum(axis=(0, 1)) - expected(Cj, wj))[i])
    print(f'    leave-one-folio-out residual {c}: {min(vals):+.1f} .. {max(vals):+.1f}')

# ---------------- Arm E ----------------
morph = Morphology()
art = lambda wd: bool(morph.extract(wd).has_articulator)
words, breaks = S.edge_tables(lines)
print(f'(4) words {len(words)}, breaks {len(breaks)}  ({time.time() - t0:.0f} s)')


def ends_m(wd):
    return Z.units(wd)[-1] == 'm'


def ends_m_any(wd):
    return Z.units(wd)[-1].endswith('m')


def boot_rate(recs_, fn, B=2000):
    """Folio-cluster bootstrap 95% CI of a rate (records carry 'folio')."""
    by = defaultdict(lambda: [0, 0])
    for r in recs_:
        v = fn(r)
        by[r['folio']][0] += v
        by[r['folio']][1] += 1
    arr = np.array(list(by.values()), dtype=float)
    k = len(arr)
    idx = rng.integers(0, k, (B, k))
    s = arr[idx].sum(axis=1)
    rates = s[:, 0] / s[:, 1]
    return arr[:, 0].sum(), arr[:, 1].sum(), np.percentile(rates, [2.5, 97.5])


for lang in ('A', 'B'):
    W = [x for x in words if x['lang'] == lang]
    Bk = [b for b in breaks if b['lang'] == lang]
    cont_ini = [x for x in W if x['i_start'] == 0 and not x['par_first_line']]
    cont_fin = [x for x in W if x['i_end'] == 0 and not x['par_last_line']]
    mid = [x for x in W if x['i_start'] > 0 and x['i_end'] > 0]
    print(f'--- {lang}: cont-initial {len(cont_ini)}, cont-final {len(cont_fin)}, interior {len(mid)}, breaks {len(Bk)}')
    for name, grp, fn in (('articulator post-break', Bk, lambda r: art(r['post'])),
                          ('articulator cont-initial', cont_ini, lambda r: art(r['word'])),
                          ('articulator interior', mid, lambda r: art(r['word'])),
                          ('-m (unit m) pre-break', Bk, lambda r: ends_m(r['pre'])),
                          ('-m (unit m) cont-final', cont_fin, lambda r: ends_m(r['word'])),
                          ('-m (unit m) interior', mid, lambda r: ends_m(r['word'])),
                          ('-m (any m unit) pre-break', Bk, lambda r: ends_m_any(r['pre'])),
                          ('-m (any m unit) cont-final', cont_fin, lambda r: ends_m_any(r['word'])),
                          ('-m (any m unit) interior', mid, lambda r: ends_m_any(r['word']))):
        k, n, ci = boot_rate(grp, fn)
        print(f'    {name:28s} {int(k):4d}/{int(n):5d} = {k / n:.4f}  folio-boot 95% CI {ci[0]:.4f}..{ci[1]:.4f}')
    # (6) position-matched interior expectations (same section, index from the relevant edge, capped at 8)
    art_rate = defaultdict(lambda: [0, 0])
    m_rate = defaultdict(lambda: [0, 0])
    for x in mid:
        ks = (x['section'], min(x['i_start'], 8))
        art_rate[ks][0] += art(x['word'])
        art_rate[ks][1] += 1
        ke = (x['section'], min(x['i_end'], 8))
        m_rate[ke][0] += ends_m(x['word'])
        m_rate[ke][1] += 1
    ea = em = 0.0
    miss = 0
    for b in Bk:
        a = art_rate.get((b['section'], min(b['post_i_start'], 8)))
        m = m_rate.get((b['section'], min(b['pre_i_end'], 8)))
        if a and a[1] >= 10:
            ea += a[0] / a[1]
        else:
            miss += 1
        if m and m[1] >= 10:
            em += m[0] / m[1]
    print(f'(6) position-matched interior expectation: articulated post-break {ea:.1f} '
          f'(obs {sum(art(b["post"]) for b in Bk)}), -m pre-break {em:.1f} (obs {sum(ends_m(b["pre"]) for b in Bk)}); '
          f'unmatched {miss}')
    # (7) bare aiin after breaks and -m before breaks
    joined = Counter(x['word'] for x in W)
    for b in Bk:
        if b['post'] == 'aiin':
            print(f'(7) {b["folio"]}: pre "{b["pre"]}" <-> post "aiin"; joined "{b["pre"] + "aiin"}" attested '
                  f'{joined.get(b["pre"] + "aiin", 0)}x in unbroken lines; post_i_start {b["post_i_start"]}')
    print(f'    pre-break -m words: {[b["pre"] for b in Bk if ends_m(b["pre"])]}')
print(f'done {time.time() - t0:.0f} s')
