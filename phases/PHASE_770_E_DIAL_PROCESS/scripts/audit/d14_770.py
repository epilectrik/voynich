"""Latent-only (no outcomes, synthetic skeleton): per-model R14 (corr of page Q1 and Q4 latent means) and
D14 = E[(u1-u4)^2] / E[u1^2 + u4^2] (position contrast; 0 for a constant or symmetric-edge setting), per page over
replicates, occurrence-weighted. Adds M5 (page trend from a common start) and M9 (walk restarting per paragraph)."""
import sys

import numpy as np

sys.argv = ['x', '4']
sys.path.insert(0, r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad')
import sim770v2 as V  # noqa: E402

P, nl, op, ol, lidx, NL, line_off = V.P, V.nl, V.op, V.ol, V.lidx, V.NL, V.line_off


def lat_extra(model, rng):
    L = np.empty(NL)
    if model == 'M5':
        b = rng.normal(0, 1, P)
        for p in range(P):
            L[line_off[p]:line_off[p] + nl[p]] = b[p] * np.arange(nl[p]) / nl[p]
        return L[lidx]
    if model == 'M9':
        sh = np.zeros(len(op))
        par = V.S['par']
        for p in range(P):
            m = op == p
            for k in np.unique(par[m]):
                mm = m & (par == k)
                ls = np.unique(ol[mm])
                w = np.r_[0.0, np.cumsum(rng.normal(0, 1, len(ls) - 1))]
                sh[mm] = w[np.searchsorted(ls, ol[mm])]
        return sh
    raise ValueError


rng = np.random.default_rng(14)
w = np.bincount(op, minlength=P)
rows = [(n, m, kw) for n, m, kw, c, g in V.VARIANTS] + [('M5', 'M5', None), ('M9', 'M9', None)]
for name, model, kw in rows:
    Q1, Q4 = [], []
    for _ in range(400):
        sh = lat_extra(model, rng) if kw is None else V.lat(model, 1.0, rng, **kw)
        a, b = V.q14_latent(sh)
        Q1.append(a); Q4.append(b)
    Q1, Q4 = np.array(Q1), np.array(Q4)
    rs, ds, ws = [], [], []
    for p in range(P):
        x, z = Q1[:, p], Q4[:, p]
        ok = np.isfinite(x) & np.isfinite(z)
        den = np.mean(x[ok] ** 2 + z[ok] ** 2)
        if ok.sum() < 50 or den < 1e-12:
            continue
        ds.append(np.mean((x[ok] - z[ok]) ** 2) / den)
        rs.append(np.corrcoef(x[ok], z[ok])[0, 1] if np.std(x[ok]) > 1e-9 and np.std(z[ok]) > 1e-9 else np.nan)
        ws.append(w[p])
    rs, ds, ws = np.array(rs), np.array(ds), np.array(ws)
    okr = np.isfinite(rs)
    print('%-6s R14 %.2f  D14 %.2f  (pages %d)' % (name, np.average(rs[okr], weights=ws[okr]), np.average(ds, weights=ws),
                                                   len(ds)), flush=True)
