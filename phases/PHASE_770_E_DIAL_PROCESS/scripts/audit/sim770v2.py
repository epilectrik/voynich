"""Synthetic-only checks for the PHASE_770 DRAFT v2 audit (no Voynich data).

Uses the v1 skeleton (sim770.skeleton + add_paragraphs: 81 pages, B-like chains, ~4,850 informative runs, 4 strata).
Questions:
  Q1  Can the v2 A2 gate pass when POSITION-DEPENDENT contains near-static variants (M4 rho 0.99, M8 segment 40)?
      Per-variant own-class / wrong-class rates at posterior >= 0.8, v2 priors (class 0.5, equal per model, equal per
      variant). Also R14 = latent corr of Q1 and Q4 means per page (ensemble), occurrence-weighted.
  Q2  Same, after conditioning on S3 and S3far near B-like values (S3 0.32 +- 0.05, S3far 0.095 +- 0.05).
  Q3  Stacking: P(primary >= 0.8 own class) vs P(primary and three near-duplicate analyses all >= 0.8 own class)
      (drop one page; cells split by a fixed line tercile; 5% of runs dropped at random). Optimistic analogues of the
      80-folio, fullness-tercile and H-F-consistent sensitivities.
Features: v2 sum-of-products quarter covariance, residuals centred within stratum x quarter; raw 7 features.
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad')
import sim770 as SIM  # noqa: E402

OUT = r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad\sim770v2_out.json'
R = int(sys.argv[1]) if len(sys.argv) > 1 else 1200

S = SIM.add_paragraphs(SIM.skeleton())
SPL = SIM.splits(S)
P, nl = S['P'], S['nl']
op, ol = S['op'], S['ol']
n_occ = len(op)
line_off = np.r_[0, np.cumsum(nl)[:-1]]
lidx = line_off[op] + ol
NL = int(nl.sum())
chain = S['chain']
pos = S['pos']
q4 = S['quarter']
strat = S['strat']
fq = op * 4 + q4

# analysis variants (fixed across replicates)
rng0 = np.random.default_rng(2024)
line_terc = rng0.integers(0, 3, NL)
_clen = np.bincount(chain)
drop_page = int(np.flatnonzero(chain == np.flatnonzero(_clen == 20)[0])[1])
ANALYSES = {
    'primary': (np.ones(n_occ, bool), S['cell']),
    'drop_page': (op != drop_page, S['cell']),
    'finer_cells': (np.ones(n_occ, bool), S['cell'] * 3 + line_terc[lidx]),
    'drop5': (rng0.random(n_occ) >= 0.05, S['cell']),
}


def lines_to_occ(arr_by_line):
    return arr_by_line[lidx]


def lat(model, a, rng, **kw):
    if model == 'M1':
        return rng.normal(0, a, P)[op]
    if model == 'M2b':
        k = kw['k']
        sh = rng.normal(0, a, P)[op].copy()
        nlo = nl[op]
        sh[(ol < k) | (ol >= nlo - k)] = 0.0
        return sh
    if model == 'M7':
        v = rng.normal(0, a / np.sqrt(2), P)
        u, inv = np.unique(op * 1000 + S['par'], return_inverse=True)
        return v[op] + rng.normal(0, a / np.sqrt(2), len(u))[inv]
    L = np.empty(NL)
    if model == 'M3':
        for p in range(P):
            L[line_off[p]:line_off[p] + nl[p]] = np.r_[0.0, np.cumsum(rng.normal(0, a, nl[p] - 1))]
        return L[lidx]
    if model == 'M4':
        phi = kw['phi']
        for p in range(P):
            x = rng.normal(0, a)
            e = rng.normal(0, a * np.sqrt(1 - phi ** 2), nl[p])
            seg = np.empty(nl[p])
            for i in range(nl[p]):
                seg[i] = x
                x = phi * x + e[i]
            L[line_off[p]:line_off[p] + nl[p]] = seg
        return L[lidx]
    if model == 'M6':
        phi = kw['phi']
        x = 0.0
        for p in range(P):
            if pos[p] == 0:
                x = rng.normal(0, a)
            else:
                for _ in range(2):
                    x = phi * x + np.sqrt(1 - phi ** 2) * rng.normal(0, a)
            seg = np.empty(nl[p])
            for i in range(nl[p]):
                seg[i] = x
                x = phi * x + np.sqrt(1 - phi ** 2) * rng.normal(0, a)
            L[line_off[p]:line_off[p] + nl[p]] = seg
        return L[lidx]
    if model == 'M8':
        m = kw['m']
        lev = 0.0
        for p in range(P):
            if pos[p] == 0:
                lev = rng.normal(0, a)
            ch = rng.random(nl[p]) < 1.0 / m
            seg = np.empty(nl[p])
            for i in range(nl[p]):
                if ch[i]:
                    lev = rng.normal(0, a)
                seg[i] = lev
            L[line_off[p]:line_off[p] + nl[p]] = seg
        return L[lidx]
    if model == 'MIX':
        s = kw['s']  # walk share of page-averaged variance
        mean_l = ol.mean()
        aw = a * np.sqrt(s / mean_l)
        ac = a * np.sqrt(1 - s)
        for p in range(P):
            L[line_off[p]:line_off[p] + nl[p]] = np.r_[0.0, np.cumsum(rng.normal(0, aw, nl[p] - 1))]
        return rng.normal(0, ac, P)[op] + L[lidx]
    raise ValueError(model)


def draw(sh, rng):
    lg = S['base'] + sh
    return (rng.random(n_occ) < 1 / (1 + np.exp(-lg))).astype(float)


def resid(y, mask, cell):
    r = np.zeros(n_occ)
    u, inv = np.unique(cell[mask], return_inverse=True)
    s = np.bincount(inv, weights=y[mask])
    c = np.bincount(inv)
    r[mask] = y[mask] - (s / c)[inv]
    return r


def centre_sq(r, mask):
    rr = r.copy()
    key = strat * 4 + q4
    k = key[mask]
    s = np.bincount(k, weights=rr[mask], minlength=16)
    c = np.bincount(k, minlength=16)
    rr[mask] -= (s / np.maximum(c, 1))[k]
    rr[~mask] = 0.0
    return rr


def feats_sop(r, mask):
    C = np.zeros((4, 4))
    for A in SPL:
        for g1, g2 in ((A, ~A), (~A, A)):
            m1, m2 = mask & g1, mask & g2
            SA = np.bincount(fq[m1], weights=r[m1], minlength=4 * P).reshape(P, 4)
            nA = np.bincount(fq[m1], minlength=4 * P).reshape(P, 4).astype(float)
            SB = np.bincount(fq[m2], weights=r[m2], minlength=4 * P).reshape(P, 4)
            nB = np.bincount(fq[m2], minlength=4 * P).reshape(P, 4).astype(float)
            C += (SA.T @ SB) / np.maximum(nA.T @ nB, 1)
    C /= 2 * len(SPL)
    C = (C + C.T) / 2
    V = np.diag(C)
    return np.r_[V, np.mean([C[0, 1], C[1, 2], C[2, 3]]), np.mean([C[0, 2], C[1, 3]]), C[0, 3]]


def s3_pair(r):
    return SIM.corr_stat(r, S, SPL, S['half'], 0, 1), SIM.corr_stat(r, S, SPL, S['quarter'], 0, 3)


def q14_latent(sh):
    s1 = np.bincount(op[q4 == 0], weights=sh[q4 == 0], minlength=P)
    n1 = np.bincount(op[q4 == 0], minlength=P)
    s4 = np.bincount(op[q4 == 3], weights=sh[q4 == 3], minlength=P)
    n4 = np.bincount(op[q4 == 3], minlength=P)
    return np.where(n1 > 0, s1 / np.maximum(n1, 1), np.nan), np.where(n4 > 0, s4 / np.maximum(n4, 1), np.nan)


VARIANTS = [  # name, model, kwargs, class, model-group
    ('M1', 'M1', {}, 'S', 'M1'),
    ('M2b4', 'M2b', {'k': 4}, 'S', 'M2b'),
    ('M7', 'M7', {}, 'S', 'M7'),
    ('M3', 'M3', {}, 'P', 'M3'),
    ('M4_95', 'M4', {'phi': 0.95}, 'P', 'M4'),
    ('M4_97', 'M4', {'phi': 0.97}, 'P', 'M4'),
    ('M4_99', 'M4', {'phi': 0.99}, 'P', 'M4'),
    ('M6_97', 'M6', {'phi': 0.97}, 'P', 'M6'),
    ('M8_10', 'M8', {'m': 10}, 'P', 'M8'),
    ('M8_20', 'M8', {'m': 20}, 'P', 'M8'),
    ('M8_40', 'M8', {'m': 40}, 'P', 'M8'),
    ('MIX25', 'MIX', {'s': 0.25}, 'X', 'MIX'),
    ('MIX50', 'MIX', {'s': 0.50}, 'X', 'MIX'),
    ('MIX75', 'MIX', {'s': 0.75}, 'X', 'MIX'),
]
GUESS = {'M1': 0.48, 'M2b': 0.62, 'M7': 0.55, 'M3': 0.19, 'M4': 0.7, 'M6': 0.7, 'M8': 0.7, 'MIX': 0.6}


def mean_s3(model, kw, a, rng, n=30):
    v = []
    for _ in range(n):
        y = draw(lat(model, a, rng, **kw), rng)
        v.append(SIM.corr_stat(resid(y, ANALYSES['primary'][0], S['cell']), S, SPL, S['half'], 0, 1))
    return float(np.mean(v))


def calibrate(model, kw, rng, target=0.32):
    a0 = GUESS[model]
    f0 = mean_s3(model, kw, a0, rng) - target
    a1 = a0 * (1.25 if f0 < 0 else 0.8)
    f1 = mean_s3(model, kw, a1, rng) - target
    for _ in range(4):
        if abs(f1) < 0.01 or f1 == f0:
            break
        a2 = max(0.02, a1 - f1 * (a1 - a0) / (f1 - f0))
        a0, f0 = a1, f1
        a1, f1 = a2, mean_s3(model, kw, a2, rng) - target
    return a1, f1 + target


if __name__ == '__main__':
    t0 = time.time()
    subset = sys.argv[2].split(',') if len(sys.argv) > 2 else [v[0] for v in VARIANTS]
    OUT = OUT.replace('.json', '_%s.json' % '_'.join(subset)) if len(sys.argv) > 2 else OUT
    rng = np.random.default_rng(770 + sum(ord(c) for c in ''.join(subset)))
    res = {'R': R, 'variants': {}}
    for name, model, kw, cls, grp in VARIANTS:
        if name not in subset:
            continue
        if len(sys.argv) > 3:
            grid = [float(x) for x in sys.argv[3].split(',')]
            vals = [mean_s3(model, kw, g, rng, n=60) for g in grid]
            print('grid', list(zip(grid, np.round(vals, 3))), flush=True)
            a = float(np.interp(0.32, vals, grid)) if vals[0] < 0.32 < vals[-1] else grid[int(np.argmin(np.abs(np.array(vals) - 0.32)))]
            s3m = mean_s3(model, kw, a, rng, n=60)
        else:
            a, s3m = calibrate(model, kw, rng)
        F = {k: [] for k in ANALYSES}
        s3, sfar, Q1, Q4 = [], [], [], []
        for _ in range(R):
            sh = lat(model, a, rng, **kw)
            y = draw(sh, rng)
            for k, (mask, cell) in ANALYSES.items():
                r = resid(y, mask, cell)
                if k == 'primary':
                    a3, af = s3_pair(r)
                    s3.append(a3); sfar.append(af)
                F[k].append(feats_sop(centre_sq(r, mask), mask).tolist())
            l1, l4 = q14_latent(sh)
            Q1.append(l1); Q4.append(l4)
        Q1, Q4 = np.array(Q1), np.array(Q4)
        w = np.bincount(op, minlength=P)
        cors = []
        ws = []
        for p in range(P):
            x, z = Q1[:, p], Q4[:, p]
            ok = np.isfinite(x) & np.isfinite(z)
            if ok.sum() > 10 and np.std(x[ok]) > 1e-9 and np.std(z[ok]) > 1e-9:
                cors.append(np.corrcoef(x[ok], z[ok])[0, 1]); ws.append(w[p])
        r14 = float(np.average(cors, weights=ws)) if cors else float('nan')
        res['variants'][name] = {'model': model, 'kw': kw, 'cls': cls, 'grp': grp, 'amp': a, 'cal_s3': s3m,
                                 'R14': r14, 's3': s3, 's3far': sfar, 'F': F}
        print('%-6s amp %.3f calS3 %.3f  meanS3 %.3f meanS3far %.3f  R14 %.2f  (%.0fs)' %
              (name, a, s3m, np.mean(s3), np.mean(sfar), r14, time.time() - t0), flush=True)
        with open(OUT, 'w') as fh:
            json.dump(res, fh)
    print('done %.0fs' % (time.time() - t0), flush=True)
