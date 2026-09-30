#!/usr/bin/env python3
"""PHASE_771 lock audit, Arm L (lean-expert). Blind: label words are COUNTED per folio (and the folio's section read);
the unit after a label's 'o' is never computed. References come from paragraph text (P loci) and, for (4), from AZC
diagram text (non-P, non-L loci), never from labels.
"""
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

t0 = time.time()
PART = sys.argv[1] if len(sys.argv) > 1 else 'refs'
recs = Z.load()
lines = S.text_lines(recs)


def jsd(p, q):
    m = 0.5 * (p + q)
    kl = lambda a, b: float(np.sum(a * np.log2(a / b)))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def refs_weighted(lines_, type_weighted=False, min_units=None):
    cnt = {k: np.zeros(len(S.CATS)) for k in S.REFS}
    seen = {k: set() for k in S.REFS}
    for ln in lines_:
        for w in (w for s in ln['segs'] for w in s):
            if not Z.readable(w):
                continue
            u = Z.units(w)
            if min_units and len(u) < min_units:
                continue
            for key, ok, idx in (('init', True, 0), ('qo', w.startswith('qo') and len(u) > 2, 2),
                                 ('o', u[0] == 'o' and len(u) > 1, 1)):
                if not ok:
                    continue
                if type_weighted:
                    if w in seen[key]:
                        continue
                    seen[key].add(w)
                cnt[key][S.CIDX[S.cat(u[idx])]] += 1
    return cnt


comps = S.ref_matrix(S.references(lines))
if PART == 'refs':
    tok = refs_weighted(lines)
    typ = refs_weighted(lines, type_weighted=True)
    long3 = refs_weighted(lines, min_units=4)
    ct, cy, cl = S.ref_matrix(tok), S.ref_matrix(typ), S.ref_matrix(long3)
    print('(1) n token / type:', {k: (int(tok[k].sum()), int(typ[k].sum())) for k in S.REFS})
    for i, k in enumerate(S.REFS):
        print(f'    {k}: JSD(token, type) {jsd(ct[i], cy[i]):.3f}; JSD(token, words >=4 units) {jsd(ct[i], cl[i]):.3f}')
    print(f'    JSD(qo,o): token {jsd(ct[0], ct[1]):.3f}, type {jsd(cy[0], cy[1]):.3f}; '
          f'JSD(type qo, token o) {jsd(cy[0], ct[1]):.3f}; JSD(type o, token qo) {jsd(cy[1], ct[0]):.3f}')
    show = ['k', 't', 'l', 'r', 'd', 'e', 'pf', 'bench']
    for i, k in enumerate(S.REFS[:2]):
        print(f'    {k} token', {c: round(float(ct[i][S.CIDX[c]]), 3) for c in show})
        print(f'    {k} type ', {c: round(float(cy[i][S.CIDX[c]]), 3) for c in show})
    # where would a label sample that is TYPE-like but truly "ordinary o-words" land under token references?
    w_ty = S.em_weights(cy[1] * 10000, ct)
    w_long = S.em_weights(cl[1] * 10000, ct)
    print('    EM weights (qo, o, init) of the TYPE-weighted o-word distribution against the token references:',
          np.round(w_ty, 3), '; of o-words with >=4 units:', np.round(w_long, 3))
    # s2 references: line-initial words only
    li = S.references(lines, line_initial_only=True)
    c2 = S.ref_matrix(li)
    print('(2) s2 line-initial refs n:', {k: int(li[k].sum()) for k in S.REFS},
          f'JSD qo-o {jsd(c2[0], c2[1]):.3f}, qo-init {jsd(c2[0], c2[2]):.3f}, o-init {jsd(c2[1], c2[2]):.3f}',
          ' init mass on k/t/p-f:', round(float(c2[2][S.CIDX['k']] + c2[2][S.CIDX['t']] + c2[2][S.CIDX['pf']]), 3))
    print('    R_init (primary) mass on o + q:', round(float(comps[2][S.CIDX['o']] + comps[2][S.CIDX['q']]), 3))
    # AZC diagram text (non-P, non-L loci on pages without a language)
    azc = [{'folio': r['folio'], 'lang': 'NA', 'section': r['section'], 'segs': S.words_of(r)} for r in recs
           if r['lang'] == 'NA' and not r['kind'].startswith(('P', 'L'))]
    ca = S.references(azc)
    print('(4) AZC diagram-text refs n:', {k: int(ca[k].sum()) for k in S.REFS}, 'loci kinds:',
          dict(Counter(r['kind'][:1] for r in recs if r['lang'] == 'NA' and not r['kind'].startswith(('P', 'L')))))
    ma = S.ref_matrix(ca)
    print(f'    JSD(AZC o, P-text o) {jsd(ma[1], comps[1]):.3f}; JSD(AZC init, P init) {jsd(ma[2], comps[2]):.3f}')

# label folio counts and systems (counts only)
nfol, sysf = Counter(), {}
for r in recs:
    if not r['kind'].startswith('L'):
        continue
    for ws in S.words_of(r):
        for w in ws:
            if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                nfol[r['folio']] += 1
                sysf[r['folio']] = S.label_system(r['section'])
fols = sorted(nfol)
nf = np.array([nfol[f] for f in fols])
sysv = [sysf[f] for f in fols]
alpha = 19.8
rng = np.random.default_rng(99)


def sim_calls(wvec_per_folio, a, nsim, B=500):
    calls = Counter()
    for _ in range(nsim):
        mat = np.vstack([rng.multinomial(n, rng.dirichlet(a * (wv @ comps))) for n, wv in zip(nf, wvec_per_folio)])
        lo = np.quantile(S.boot_weights(mat.astype(float), comps, rng, B), 0.025, axis=0)
        calls[S.label_call(lo)] += 1
    return {k: round(v / nsim, 3) for k, v in calls.items()}


if PART == 'boundary':
    print('label folios', len(nf), 'words', nf.sum(), 'system shares',
          {s: int(sum(n for n, v in zip(nf, sysv) if v == s)) for s in set(sysv)})
    for name, wv in (('o 2/3 + qo 1/3', [1 / 3, 2 / 3, 0]), ('qo 2/3 + o 1/3', [2 / 3, 1 / 3, 0]),
                     ('o 2/3 + init 1/3', [0, 2 / 3, 1 / 3]), ('init 2/3 + o 1/3', [0, 1 / 3, 2 / 3])):
        for a in (alpha, alpha / 4):
            print(f'(5) truth {name} at alpha {a:.2f}:', sim_calls([np.array(wv)] * len(nf), a, 100), flush=True)
    print('elapsed', round(time.time() - t0, 1), 's')

if PART == 'hetero':
    E = np.eye(3)
    for name, m in (('astro=o, others=init', {'astro_zodiac_cosmo': E[1]}),
                    ('astro=o, others=qo', {'astro_zodiac_cosmo': E[1]}),
                    ('astro=init, others=o', {'astro_zodiac_cosmo': E[2]})):
        other = E[2] if 'others=init' in name else (E[0] if 'others=qo' in name else E[1])
        wv = [m.get(s, other) for s in sysv]
        for a in (alpha, alpha / 4):
            print(f'(6) heterogeneous truth {name}, alpha {a:.2f}:', sim_calls(wv, a, 100), flush=True)
    # fit-check size when labels cluster 4x more than text but the check uses alpha_text (as coded)
    for tname, ti in (('o', 1), ('qo', 0)):
        rej_coded, rej_matched = 0, 0
        for _ in range(60):
            mat = np.vstack([rng.multinomial(n, rng.dirichlet((alpha / 4) * comps[ti])) for n in nf]).astype(float)
            rej_coded += S.fit_check_p(mat, comps, alpha, nf, rng, 200) < 0.01
            rej_matched += S.fit_check_p(mat, comps, alpha / 4, nf, rng, 200) < 0.01
        print(f'(7) fit check size at 0.01, truth {tname}, data alpha/4: with alpha_text {rej_coded / 60:.3f}, '
              f'with alpha/4 {rej_matched / 60:.3f}', flush=True)
    print('elapsed', round(time.time() - t0, 1), 's')
