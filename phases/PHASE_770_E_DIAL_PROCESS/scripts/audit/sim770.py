"""Synthetic-only checks for the PHASE_770 draft audit (no Voynich data used).

Skeleton mimics B's gross structure: 81 pages, 13 reading-order chains with B's chain lengths + 12 singletons,
~30 lines per page, ~2.4 informative e-runs per line, Zipf frames with heterogeneous base logits, 4 strata.
Models of the folio component (logit scale): M1 constant, M1n constant with neighbour-correlated pages,
M3 restart walk, M6 cross-page stationary OU, TRENDPOS (quire trend x stratum-specific top/bottom offset).
Statistics: S3 (top-half A vs bottom-half B corr), S3far (Q1 vs Q4), quarter cross-half covariance matrix,
K (C1) with per-transition sign-flip null.
"""
import sys
import numpy as np

CHAINS = [2, 2, 4, 6, 2, 2, 2, 2, 2, 20, 2, 12, 11]
N_SINGLE = 12
K_SPLITS = 20


def skeleton(seed=1):
    rng = np.random.default_rng(seed)
    chain_of, pos_in_chain, stratum = [], [], []
    cid = 0
    for j, L in enumerate(CHAINS):
        s = 1 if L == 20 else (2 if L in (12, 11) else 0)
        for i in range(L):
            chain_of.append(cid); pos_in_chain.append(i); stratum.append(s)
        cid += 1
    for _ in range(N_SINGLE):
        chain_of.append(cid); pos_in_chain.append(0); stratum.append(3); cid += 1
    P = len(chain_of)
    nl = rng.integers(12, 49, P)
    op, ol = [], []
    for p in range(P):
        k = rng.poisson(2.4, nl[p])
        for l in range(nl[p]):
            op += [p] * k[l]; ol += [l] * k[l]
    op, ol = np.array(op), np.array(ol)
    n = len(op)
    KF = 1500
    w = 1 / np.arange(1, KF + 1) ** 1.1
    w /= w.sum()
    frame = rng.choice(KF, n, p=w)
    base = rng.normal(-0.7, 1.0, KF)
    strat = np.array(stratum)[op]
    cell = frame * 4 + strat
    # informative: cell spans >= 2 pages
    order = np.lexsort((op, cell))
    cs, ps = cell[order], op[order]
    first = np.r_[True, cs[1:] != cs[:-1]]
    newp = np.r_[True, (cs[1:] != cs[:-1]) | (ps[1:] != ps[:-1])]
    npages = np.add.reduceat(newp.astype(int), np.flatnonzero(first))
    cellpages = dict(zip(cs[first], npages))
    inf = np.array([cellpages[c] >= 2 for c in cell])
    rel = ol / nl[op]
    quarter = np.minimum(3, (4 * ol) // nl[op])
    half = (ol >= (nl[op] + 1) // 2).astype(int)
    trans = [(p, p + 1) for p in range(P - 1) if chain_of[p] == chain_of[p + 1]]
    return dict(P=P, nl=nl, op=op[inf], ol=ol[inf], frame=frame[inf], cell=cell[inf], base=base[frame[inf]],
                strat=strat[inf], pstrat=np.array(stratum), chain=np.array(chain_of), pos=np.array(pos_in_chain),
                quarter=quarter[inf], half=half[inf], rel=rel[inf], trans=trans)


def cell_means(y, cell):
    u, inv = np.unique(cell, return_inverse=True)
    s = np.bincount(inv, weights=y)
    c = np.bincount(inv)
    return (s / c)[inv]


def plant(S, model, amp, rng, rho=0.6, phi=0.97, g=0.0, c=0.0):
    P, nl = S['P'], S['nl']
    lev = {}  # (page, line) -> logit shift, built per page as arrays
    shift_page_line = [None] * P
    if model == 'M1':
        v = rng.normal(0, amp, P)
        for p in range(P):
            shift_page_line[p] = np.full(nl[p], v[p])
    elif model == 'M1n':  # constant per page, AR(1) across pages within chain
        v = np.zeros(P)
        for p in range(P):
            if S['pos'][p] == 0:
                v[p] = rng.normal(0, amp)
            else:
                v[p] = rho * v[p - 1] + np.sqrt(1 - rho ** 2) * rng.normal(0, amp)
            shift_page_line[p] = np.full(nl[p], v[p])
    elif model == 'M2b':  # constant, first and last 2 lines unexpressed
        v = rng.normal(0, amp, P)
        for p in range(P):
            a = np.full(nl[p], v[p]); a[:2] = 0; a[-2:] = 0
            shift_page_line[p] = a
    elif model == 'M3':  # restart walk from 0 each page
        for p in range(P):
            shift_page_line[p] = np.concatenate([[0.0], np.cumsum(rng.normal(0, amp, nl[p] - 1))])
    elif model == 'M5':  # page-specific slope from common start
        b = rng.normal(0, amp, P)
        for p in range(P):
            shift_page_line[p] = b[p] * np.arange(nl[p]) / nl[p]
    elif model == 'M6':  # stationary OU over lines, continuing across pages within chains (gap of 2 lines)
        x = 0.0
        for p in range(P):
            if S['pos'][p] == 0:
                x = rng.normal(0, amp)
            else:
                for _ in range(2):
                    x = phi * x + np.sqrt(1 - phi ** 2) * rng.normal(0, amp)
            a = np.empty(nl[p])
            for l in range(nl[p]):
                a[l] = x
                x = phi * x + np.sqrt(1 - phi ** 2) * rng.normal(0, amp)
            shift_page_line[p] = a
    elif model == 'MIX':  # half constant, half restart walk (variance split by amp)
        v = rng.normal(0, amp[0], P)
        for p in range(P):
            shift_page_line[p] = v[p] + np.concatenate([[0.0], np.cumsum(rng.normal(0, amp[1], nl[p] - 1))])
    elif model == 'TRENDPOS':  # static page levels that trend along each chain + stratum-specific top/bottom offset
        v = np.zeros(P)
        for p in range(P):
            v[p] = rng.normal(0, amp) + c * S['pos'][p]
        sgn = np.array([1.0, -1.0, 1.0, -1.0])
        for p in range(P):
            shift_page_line[p] = v[p] + g * sgn[S['pstrat'][p]] * (np.arange(nl[p]) / nl[p] - 0.5)
    elif model == 'POSGRAD':  # M1 + stratum-specific linear position gradient (opposite signs across strata)
        v = rng.normal(0, amp, P)
        sgn = np.array([1.0, -1.0, 1.0, -1.0])
        for p in range(P):
            shift_page_line[p] = v[p] + g * sgn[S['pstrat'][p]] * (np.arange(nl[p]) / nl[p] - 0.5)
    else:
        raise ValueError(model)
    sh = np.array([shift_page_line[p][l] for p, l in zip(S['op'], S['ol'])])
    lg = S['base'] + sh
    return (rng.random(len(lg)) < 1 / (1 + np.exp(-lg))).astype(float)


def splits(S, seed=7700, k=K_SPLITS):
    rng = np.random.default_rng(seed)
    nfr = S['frame'].max() + 1
    return [(rng.random(nfr) < 0.5)[S['frame']] for _ in range(k)]


def region_means(r, S, mask, P):
    s = np.bincount(S['op'][mask], weights=r[mask], minlength=P)
    n = np.bincount(S['op'][mask], minlength=P)
    return s, n


def corr_stat(r, S, SPL, reg, a, b, min_occ=5):
    P = S['P']
    vals = []
    for A in SPL:
        cs = []
        for g1, g2 in ((A, ~A), (~A, A)):
            s1, n1 = region_means(r, S, g1 & (reg == a), P)
            s2, n2 = region_means(r, S, g2 & (reg == b), P)
            ok = (n1 >= min_occ) & (n2 >= min_occ)
            if ok.sum() < 5:
                continue
            x, y = s1[ok] / n1[ok], s2[ok] / n2[ok]
            cs.append(np.corrcoef(x, y)[0, 1])
        if cs:
            vals.append(np.mean(cs))
    return float(np.mean(vals))


def quarter_cov(r, S, SPL, min_occ=3):
    P = S['P']
    C = np.zeros((4, 4))
    W = np.zeros((4, 4))
    for A in SPL:
        for g1, g2 in ((A, ~A), (~A, A)):
            m1 = [region_means(r, S, g1 & (S['quarter'] == q), P) for q in range(4)]
            m2 = [region_means(r, S, g2 & (S['quarter'] == q), P) for q in range(4)]
            for q in range(4):
                for q2 in range(4):
                    s1, n1 = m1[q]; s2, n2 = m2[q2]
                    ok = (n1 >= min_occ) & (n2 >= min_occ)
                    if ok.sum() < 5:
                        continue
                    x, y = s1[ok] / n1[ok], s2[ok] / n2[ok]
                    C[q, q2] += np.cov(x, y)[0, 1]; W[q, q2] += 1
    C = C / np.maximum(W, 1)
    return (C + C.T) / 2


def features(C):
    V = np.diag(C)
    d1 = np.mean([C[0, 1], C[1, 2], C[2, 3]])
    d2 = np.mean([C[0, 2], C[1, 3]])
    d3 = C[0, 3]
    return np.r_[V, d1, d2, d3]


def K_stat(r, S, SPL, center='stratum'):
    P = S['P']
    trans = S['trans']
    Ds = np.zeros(len(trans))
    for A in SPL:
        for g1, g2 in ((A, ~A), (~A, A)):
            sb1, nb1 = region_means(r, S, g1 & (S['quarter'] == 3), P)
            st1, nt1 = region_means(r, S, g1 & (S['quarter'] == 0), P)
            sb2, nb2 = region_means(r, S, g2 & (S['quarter'] == 3), P)
            st2, nt2 = region_means(r, S, g2 & (S['quarter'] == 0), P)
            mb1 = np.where(nb1 > 0, sb1 / np.maximum(nb1, 1), np.nan)
            mt1 = np.where(nt1 > 0, st1 / np.maximum(nt1, 1), np.nan)
            mb2 = np.where(nb2 > 0, sb2 / np.maximum(nb2, 1), np.nan)
            mt2 = np.where(nt2 > 0, st2 / np.maximum(nt2, 1), np.nan)
            for arr in (mb1, mt1, mb2, mt2):
                if center == 'stratum':
                    for s in range(4):
                        m = S['pstrat'] == s
                        arr[m] -= np.nanmean(arr[m])
                elif center == 'global':
                    arr -= np.nanmean(arr)
                elif center == 'chain':
                    for ch in np.unique(S['chain']):
                        m = S['chain'] == ch
                        arr[m] -= np.nanmean(arr[m])
                np.nan_to_num(arr, copy=False)
            for i, (t, u) in enumerate(trans):
                Ds[i] += mb1[t] * mt2[u] - mt1[t] * mb2[u]
    Ds /= (2 * len(SPL))
    return Ds


def signflip_p(Ds, rng, B=4000):
    k = Ds.sum()
    eps = rng.choice([-1.0, 1.0], size=(B, len(Ds)))
    null = eps @ Ds
    return (1 + (null >= k).sum()) / (1 + B), k


def residual(y, S):
    return y - cell_means(y, S['cell'])


if __name__ == '__main__' and sys.argv[1] == 'scale':
    what = sys.argv[1]
    S = skeleton()
    SPL = splits(S)
    print('occurrences', len(S['op']), 'pages', S['P'], 'transitions', len(S['trans']), flush=True)
    rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 11)
    if what == 'scale':
        # find amplitudes giving mean S3 ~ 0.32 for each model
        for model, grid in (('M1', [0.35, 0.45, 0.55]), ('M3', [0.08, 0.11, 0.14]), ('M6', [0.35, 0.45, 0.55]),
                            ('M5', [0.6, 0.8, 1.0]), ('M2b', [0.4, 0.5, 0.6])):
            for a in grid:
                s3, sf = [], []
                for _ in range(40):
                    y = plant(S, model, a, rng)
                    r = residual(y, S)
                    s3.append(corr_stat(r, S, SPL, S['half'], 0, 1))
                    sf.append(corr_stat(r, S, SPL, S['quarter'], 0, 3))
                print(model, a, 'S3 %.3f  S3far %.3f  ratio %.2f' % (np.mean(s3), np.mean(sf), np.mean(sf) / np.mean(s3)),
                      flush=True)


def run_c1(S, SPL, rng, R=200):
    conds = [('M6 power', 'M6', 0.7, {}), ('M1n rho0.6 size', 'M1n', 0.48, {'rho': 0.6}),
             ('M1n rho0.9 size', 'M1n', 0.48, {'rho': 0.9}), ('M3 size', 'M3', 0.19, {}),
             ('TRENDPOS size', 'TRENDPOS', 0.40, {'g': 0.8, 'c': 0.08})]
    for name, model, amp, kw in conds:
        res = {'stratum': [], 'global': [], 'chain': []}
        ks = []
        for _ in range(R):
            y = plant(S, model, amp, rng, **kw)
            r = residual(y, S)
            for cen in res:
                Ds = K_stat(r, S, SPL, center=cen)
                p, k = signflip_p(Ds, rng, B=2000)
                res[cen].append(p)
                if cen == 'stratum':
                    ks.append(k)
        out = '  '.join('%s a01 %.3f a05 %.3f' % (c, np.mean(np.array(v) <= 0.01), np.mean(np.array(v) <= 0.05))
                        for c, v in res.items())
        print('%-18s K mean %.5f sd %.5f | %s' % (name, np.mean(ks), np.std(ks), out), flush=True)


def run_a2(S, SPL, rng, R=300):
    models = [('M1', 'M1', 0.48, 'S'), ('M2b', 'M2b', 0.57, 'S'), ('M3', 'M3', 0.19, 'P'), ('M5', 'M5', 1.4, 'P'),
              ('M6', 'M6', 0.7, 'P'), ('MIX', 'MIX', (0.34, 0.13), 'X')]
    F = {}
    s3m = {}
    for name, model, amp, cls in models:
        fs, s3 = [], []
        for _ in range(R):
            y = plant(S, model, amp, rng)
            r = residual(y, S)
            fs.append(features(quarter_cov(r, S, SPL)))
            s3.append(corr_stat(r, S, SPL, S['half'], 0, 1))
        F[name] = np.array(fs)
        s3m[name] = np.mean(s3)
        print(name, 'mean S3 %.3f' % s3m[name], 'mean features', np.round(F[name].mean(0) * 1e3, 2),
              'sd', np.round(F[name].std(0) * 1e3, 2), flush=True)
    cls = {m[0]: m[3] for m in models}
    for norm in (False, True):
        def tf(X):
            if not norm:
                return X
            mv = X[:, :4].mean(1, keepdims=True)
            return np.hstack([X[:, :4] / mv, X[:, 4:] / mv])[:, 1:]   # drop one V (sums to 4)
        train = {m: tf(F[m][:R // 2]) for m in F if cls[m] != 'X'}
        par = {}
        for m, X in train.items():
            mu = X.mean(0)
            Cv = np.cov(X.T) + 1e-12 * np.eye(X.shape[1])
            par[m] = (mu, np.linalg.inv(Cv), np.linalg.slogdet(Cv)[1])
        def post(x):
            ll = {m: -0.5 * (x - mu) @ Pi @ (x - mu) - 0.5 * ld for m, (mu, Pi, ld) in par.items()}
            mx = max(ll.values())
            w = {m: np.exp(v - mx) for m, v in ll.items()}
            # equal class priors, uniform within class
            nS = sum(1 for m in w if cls[m] == 'S'); nP = sum(1 for m in w if cls[m] == 'P')
            pS = sum(v / nS for m, v in w.items() if cls[m] == 'S'); pP = sum(v / nP for m, v in w.items() if cls[m] == 'P')
            return pS / (pS + pP)
        print('--- classifier, normalised features' if norm else '--- classifier, raw features', flush=True)
        for m in F:
            X = tf(F[m][R // 2:])
            ps = np.array([post(x) for x in X])
            print('%-4s true %s: P(STATIC>=0.8) %.2f  P(POS>=0.8) %.2f  unresolved %.2f' %
                  (m, cls[m], np.mean(ps >= 0.8), np.mean(ps <= 0.2), np.mean((ps > 0.2) & (ps < 0.8))), flush=True)


def run_posgrad(S, SPL, rng, R=80):
    for g in (0.0, 0.6, 1.0):
        s3, sf = [], []
        for _ in range(R):
            y = plant(S, 'POSGRAD', 0.48, rng, g=g)
            r = residual(y, S)
            s3.append(corr_stat(r, S, SPL, S['half'], 0, 1))
            sf.append(corr_stat(r, S, SPL, S['quarter'], 0, 3))
        print('POSGRAD g %.1f  S3 %.3f  S3far %.3f  ratio %.2f' % (g, np.mean(s3), np.mean(sf), np.mean(sf) / np.mean(s3)),
              flush=True)


if __name__ == '__main__' and sys.argv[1] in ('c1', 'a2', 'posgrad'):
    S = skeleton()
    SPL = splits(S)
    rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 21)
    {'c1': run_c1, 'a2': run_a2, 'posgrad': run_posgrad}[sys.argv[1]](S, SPL, rng)


def plant_m4(S, amp, rng, phi):
    """Stationary AR(1) over lines, restarting each page from the stationary law (no folio intercept)."""
    P, nl = S['P'], S['nl']
    rows = []
    for p in range(P):
        a = np.empty(nl[p]); x = rng.normal(0, amp)
        for l in range(nl[p]):
            a[l] = x
            x = phi * x + np.sqrt(1 - phi ** 2) * rng.normal(0, amp)
        rows.append(a)
    sh = np.array([rows[p][l] for p, l in zip(S['op'], S['ol'])])
    lg = S['base'] + sh
    return (rng.random(len(lg)) < 1 / (1 + np.exp(-lg))).astype(float)


def K_general(r, S, SPL, bot_mask, top_mask):
    P = S['P']
    trans = S['trans']
    Ds = np.zeros(len(trans))
    for A in SPL:
        for g1, g2 in ((A, ~A), (~A, A)):
            arrs = []
            for g, m in ((g1, bot_mask), (g1, top_mask), (g2, bot_mask), (g2, top_mask)):
                s, n = region_means(r, S, g & m, P)
                a = np.where(n > 0, s / np.maximum(n, 1), np.nan)
                for st in range(4):
                    mm = S['pstrat'] == st
                    if np.isfinite(a[mm]).any():
                        a[mm] -= np.nanmean(a[mm])
                arrs.append(np.nan_to_num(a))
            mb1, mt1, mb2, mt2 = arrs
            for i, (t, u) in enumerate(trans):
                Ds[i] += mb1[t] * mt2[u] - mt1[t] * mb2[u]
    return Ds / (2 * len(SPL))


if __name__ == '__main__' and sys.argv[1] == 'm4':
    S = skeleton(); SPL = splits(S); rng = np.random.default_rng(31)
    for phi in (0.7, 0.9, 0.97):
        for amp in (0.5, 1.0, 2.0):
            s3, sf = [], []
            for _ in range(40):
                y = plant_m4(S, amp, rng, phi)
                r = residual(y, S)
                s3.append(corr_stat(r, S, SPL, S['half'], 0, 1))
                sf.append(corr_stat(r, S, SPL, S['quarter'], 0, 3))
            print('M4 phi %.2f amp %.1f  S3 %.3f  S3far %.3f' % (phi, amp, np.mean(s3), np.mean(sf)), flush=True)

if __name__ == '__main__' and sys.argv[1] == 'c1win':
    S = skeleton(); SPL = splits(S); rng = np.random.default_rng(41)
    nlo = S['nl'][S['op']]
    wins = {'quarters': (S['quarter'] == 3, S['quarter'] == 0),
            'thirds': (S['rel'] >= 2 / 3, S['rel'] < 1 / 3),
            'halves': (S['half'] == 1, S['half'] == 0),
            'last5/first5': (S['ol'] >= nlo - 5, S['ol'] < 5)}
    for name, model, amp, kw in (('M6 power', 'M6', 0.7, {}), ('M1n rho0.9 size', 'M1n', 0.48, {'rho': 0.9}),
                                 ('M3 size', 'M3', 0.19, {})):
        res = {w: [] for w in wins}
        for _ in range(200):
            y = plant(S, model, amp, rng, **kw)
            r = residual(y, S)
            for w, (bm, tm) in wins.items():
                Ds = K_general(r, S, SPL, bm, tm)
                res[w].append(signflip_p(Ds, rng, B=2000)[0])
        print('%-16s ' % name + '  '.join('%s a01 %.3f a05 %.3f' % (w, np.mean(np.array(v) <= 0.01),
                                                                   np.mean(np.array(v) <= 0.05))
                                          for w, v in res.items()), flush=True)


def add_paragraphs(S, seed=5):
    """Synthetic paragraphs: strata 1,2 (bio/recipe-like) ~5-line paragraphs; stratum 0 1-3 per page; 3 one."""
    rng = np.random.default_rng(seed)
    par_of_line = []
    for p in range(S['P']):
        L = S['nl'][p]; st = S['pstrat'][p]
        if st in (1, 2):
            cuts = []
            x = 0
            while x < L:
                cuts.append(x); x += 2 + rng.poisson(3)
        elif st == 0:
            k = rng.integers(1, 4); cuts = sorted(set([0] + list(rng.choice(np.arange(1, L), k - 1, replace=False)))) if k > 1 else [0]
        else:
            cuts = [0]
        lab = np.zeros(L, int)
        for i, c in enumerate(cuts):
            lab[c:] = i
        par_of_line.append(lab)
    S['par'] = np.array([par_of_line[p][l] for p, l in zip(S['op'], S['ol'])])
    return S


def a3_stat(r, S, SPL, rng, nperm=500, center='global'):
    op, ol, nl = S['op'], S['ol'], S['nl'][S['op']]
    keep = (ol >= 2) & (ol < nl - 2)
    rr = r.copy()
    dec = np.minimum(9, (10 * S['rel']).astype(int))
    if center == 'global':
        for d in range(10):
            m = keep & (dec == d)
            rr[m] -= rr[m].mean()
    elif center == 'stratum':
        for st in range(4):
            for d in range(10):
                m = keep & (dec == d) & (S['strat'] == st)
                if m.any():
                    rr[m] -= rr[m].mean()
    mats = []
    for p in range(S['P']):
        mp = keep & (op == p)
        pars = np.unique(S['par'][mp])
        if len(pars) < 3:
            continue
        k = len(pars)
        pidx = np.searchsorted(pars, S['par'][mp])
        M = np.zeros((k, k)); W = np.zeros((k, k))
        for A in SPL:
            a = A[mp]
            for g1, g2 in ((a, ~a), (~a, a)):
                s1 = np.bincount(pidx[g1], weights=rr[mp][g1], minlength=k); n1 = np.bincount(pidx[g1], minlength=k)
                s2 = np.bincount(pidx[g2], weights=rr[mp][g2], minlength=k); n2 = np.bincount(pidx[g2], minlength=k)
                m1 = np.where(n1 > 0, s1 / np.maximum(n1, 1), 0.0); m2 = np.where(n2 > 0, s2 / np.maximum(n2, 1), 0.0)
                v1 = (n1 > 0).astype(float); v2 = (n2 > 0).astype(float)
                M += np.outer(m1, m2); W += np.outer(v1, v2)
        M = (M + M.T) / 2; W = (W + W.T) / 2
        mats.append((M / np.maximum(W, 1), W > 0))
    def D(perms):
        adj_s = adj_n = far_s = far_n = 0.0
        for (M, V), pi in zip(mats, perms):
            k = len(M)
            Mp = M[np.ix_(pi, pi)]; Vp = V[np.ix_(pi, pi)]
            i, j = np.triu_indices(k, 1)
            adj = (j - i) == 1
            ok = Vp[i, j]
            adj_s += Mp[i, j][adj & ok].sum(); adj_n += (adj & ok).sum()
            far_s += Mp[i, j][~adj & ok].sum(); far_n += (~adj & ok).sum()
        return adj_s / max(adj_n, 1) - far_s / max(far_n, 1)
    obs = D([np.arange(len(M)) for M, _ in mats])
    null = np.array([D([rng.permutation(len(M)) for M, _ in mats]) for _ in range(nperm)])
    return (1 + (null >= obs).sum()) / (1 + nperm), len(mats)


if __name__ == '__main__' and sys.argv[1] == 'a3':
    S = add_paragraphs(skeleton()); SPL = splits(S, k=10); rng = np.random.default_rng(51)
    conds = [('M1 size', 'M1', 0.48, {}), ('M2b size', 'M2b', 0.57, {}), ('POSGRAD g1.0 size', 'POSGRAD', 0.48, {'g': 1.0}),
             ('M3 power', 'M3', 0.19, {}), ('M5 power', 'M5', 1.4, {}), ('M6 power', 'M6', 0.7, {})]
    for name, model, amp, kw in conds:
        pg, ps = [], []
        for _ in range(100):
            y = plant(S, model, amp, rng, **kw)
            r = residual(y, S)
            p1, nf = a3_stat(r, S, SPL, rng, center='global')
            p2, _ = a3_stat(r, S, SPL, rng, center='stratum')
            pg.append(p1); ps.append(p2)
        pg, ps = np.array(pg), np.array(ps)
        print('%-20s folios %d | global-centred a01 %.2f a05 %.2f | stratum-centred a01 %.2f a05 %.2f' %
              (name, nf, np.mean(pg <= 0.01), np.mean(pg <= 0.05), np.mean(ps <= 0.01), np.mean(ps <= 0.05)), flush=True)


def a3_stat2(r, S, SPL, rng, nperm=300, edge=2, equal_pars=False):
    """As a3_stat (global decile centring) with a switch for the page-edge exclusion."""
    op, ol, nl = S['op'], S['ol'], S['nl'][S['op']]
    keep = (ol >= edge) & (ol < nl - edge)
    rr = r.copy()
    dec = np.minimum(9, (10 * S['rel']).astype(int))
    for d in range(10):
        m = keep & (dec == d)
        if m.any():
            rr[m] -= rr[m].mean()
    mats = []
    for p in range(S['P']):
        mp = keep & (op == p)
        pars = np.unique(S['par'][mp])
        if len(pars) < 3:
            continue
        k = len(pars)
        pidx = np.searchsorted(pars, S['par'][mp])
        M = np.zeros((k, k)); W = np.zeros((k, k))
        for A in SPL:
            a = A[mp]
            for g1, g2 in ((a, ~a), (~a, a)):
                s1 = np.bincount(pidx[g1], weights=rr[mp][g1], minlength=k); n1 = np.bincount(pidx[g1], minlength=k)
                s2 = np.bincount(pidx[g2], weights=rr[mp][g2], minlength=k); n2 = np.bincount(pidx[g2], minlength=k)
                m1 = np.where(n1 > 0, s1 / np.maximum(n1, 1), 0.0); m2 = np.where(n2 > 0, s2 / np.maximum(n2, 1), 0.0)
                M += np.outer(m1, m2); W += np.outer((n1 > 0).astype(float), (n2 > 0).astype(float))
        M = (M + M.T) / 2; W = (W + W.T) / 2
        mats.append((M / np.maximum(W, 1), W > 0))
    def D(perms):
        a_s = a_n = f_s = f_n = 0.0
        for (M, V), pi in zip(mats, perms):
            k = len(M); Mp = M[np.ix_(pi, pi)]; Vp = V[np.ix_(pi, pi)]
            i, j = np.triu_indices(k, 1); adj = (j - i) == 1; ok = Vp[i, j]
            a_s += Mp[i, j][adj & ok].sum(); a_n += (adj & ok).sum()
            f_s += Mp[i, j][~adj & ok].sum(); f_n += (~adj & ok).sum()
        return a_s / max(a_n, 1) - f_s / max(f_n, 1)
    obs = D([np.arange(len(M)) for M, _ in mats])
    null = np.array([D([rng.permutation(len(M)) for M, _ in mats]) for _ in range(nperm)])
    return (1 + (null >= obs).sum()) / (1 + nperm)


if __name__ == '__main__' and sys.argv[1] == 'a3diag':
    S = add_paragraphs(skeleton()); SPL = splits(S, k=10); rng = np.random.default_rng(61)
    res = {0: [], 2: []}
    for _ in range(150):
        y = plant(S, 'M1', 0.48, rng)
        r = residual(y, S)
        for e in res:
            res[e].append(a3_stat2(r, S, SPL, rng, edge=e))
    for e, v in res.items():
        v = np.array(v)
        print('M1 size, edge exclusion %d lines: a01 %.3f a05 %.3f (n=%d)' % (e, np.mean(v <= 0.01), np.mean(v <= 0.05), len(v)),
              flush=True)


if __name__ == '__main__' and sys.argv[1] == 'c1chain':
    import itertools
    S = skeleton(); SPL = splits(S); rng = np.random.default_rng(71)
    tchain = np.array([S['chain'][t] for t, _ in S['trans']])
    chains = np.unique(tchain)
    signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(chains))))
    for name, model, amp, kw in (('M6 power', 'M6', 0.7, {}), ('M1n rho0.6 size', 'M1n', 0.48, {'rho': 0.6})):
        pt, pc = [], []
        for _ in range(200):
            y = plant(S, model, amp, rng, **kw)
            r = residual(y, S)
            Ds = K_stat(r, S, SPL, center='stratum')
            pt.append(signflip_p(Ds, rng, B=2000)[0])
            Kc = np.array([Ds[tchain == c].sum() for c in chains])
            null = signs @ Kc
            pc.append(np.mean(null >= Kc.sum()))
        pt, pc = np.array(pt), np.array(pc)
        print('%-16s per-transition flip a01 %.3f a05 %.3f | per-chain flip a01 %.3f a05 %.3f' %
              (name, np.mean(pt <= 0.01), np.mean(pt <= 0.05), np.mean(pc <= 0.01), np.mean(pc <= 0.05)), flush=True)


if __name__ == '__main__' and sys.argv[1] == 'm2bw':
    S = skeleton(); SPL = splits(S); rng = np.random.default_rng(81)
    for k, amp in ((2, 0.57), (4, 0.62), (6, 0.70), (8, 0.80)):
        s3, sf = [], []
        for _ in range(60):
            v = rng.normal(0, amp, S['P'])
            sh = v[S['op']].copy()
            nlo = S['nl'][S['op']]
            sh[(S['ol'] < k) | (S['ol'] >= nlo - k)] = 0.0
            lg = S['base'] + sh
            y = (rng.random(len(lg)) < 1 / (1 + np.exp(-lg))).astype(float)
            r = residual(y, S)
            s3.append(corr_stat(r, S, SPL, S['half'], 0, 1))
            sf.append(corr_stat(r, S, SPL, S['quarter'], 0, 3))
        s3, sf = np.array(s3), np.array(sf)
        print('static, first/last %d lines unexpressed, amp %.2f: S3 %.3f  S3far %.3f  ratio of means %.2f  P(S3far<=0.095) %.2f'
              % (k, amp, s3.mean(), sf.mean(), sf.mean() / s3.mean(), np.mean(sf <= 0.095)), flush=True)


if __name__ == '__main__' and sys.argv[1] == 'a3pow':
    which = sys.argv[2]
    table = {'M3': ('M3', 0.19, {}), 'M5': ('M5', 1.4, {}), 'M6': ('M6', 0.7, {}), 'MIX': ('MIX', (0.34, 0.13), {}),
             'POSGRAD': ('POSGRAD', 0.48, {'g': 1.0})}
    model, amp, kw = table[which]
    S = add_paragraphs(skeleton()); SPL = splits(S, k=10); rng = np.random.default_rng(hash(which) % 10000)
    ps = []
    for _ in range(80):
        y = plant(S, model, amp, rng, **kw)
        r = residual(y, S)
        ps.append(a3_stat2(r, S, SPL, rng, nperm=200, edge=2))
    ps = np.array(ps)
    print('A3 %-8s a01 %.3f a05 %.3f (n=%d, 200 perms)' % (which, np.mean(ps <= 0.01), np.mean(ps <= 0.05), len(ps)),
          flush=True)
