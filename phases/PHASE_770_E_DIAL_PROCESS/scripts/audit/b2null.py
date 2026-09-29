"""Synthetic check of the Arm B (B2) null. Two dials E and Y on the same 81 pages, disjoint occurrence sets,
each with its OWN independent folio component (true shared correlation = 0). Statistic X = mean over splits and
swaps of corr across folios (E top half vs Y bottom half). Compare:
  null I : E and Y permuted independently within their own cells (the draft)
  null P : pairing null - Y's per-folio vectors relabelled by one folio permutation within stratum (all splits).
Also the power at a shared latent correlation of 0.7."""
import sys
import numpy as np
import scipy.sparse as sp

sys.path.insert(0, r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad')
import sim770 as SIM

K = 20
MIN_OCC = 5


def second_dial(S_e, seed, rate=2.0):
    rng = np.random.default_rng(seed)
    P, nl = S_e['P'], S_e['nl']
    op, ol = [], []
    for p in range(P):
        k = rng.poisson(rate, nl[p])
        for l in range(nl[p]):
            op += [p] * k[l]; ol += [l] * k[l]
    op, ol = np.array(op), np.array(ol)
    KF = 1200
    w = 1 / np.arange(1, KF + 1) ** 1.1; w /= w.sum()
    frame = rng.choice(KF, len(op), p=w)
    base = rng.normal(-0.7, 1.0, KF)
    strat = S_e['pstrat'][op]
    cell = frame * 4 + strat
    pages_per_cell = {}
    for c, p in zip(cell, op):
        pages_per_cell.setdefault(c, set()).add(p)
    inf = np.array([len(pages_per_cell[c]) >= 2 for c in cell])
    half = (ol >= (nl[op] + 1) // 2).astype(int)
    return dict(P=P, op=op[inf], ol=ol[inf], frame=frame[inf], cell=cell[inf], base=base[frame[inf]],
                half=half[inf], pstrat=S_e['pstrat'])


def draw(S, shift_page, rng):
    lg = S['base'] + shift_page[S['op']]
    return (rng.random(len(lg)) < 1 / (1 + np.exp(-lg))).astype(float)


def agg_mats(S, rng_seed, region, use_half_bit):
    """For each split: sparse (P x n) aggregation matrix over occurrences whose frame is in the chosen half and
    whose page-half == region."""
    rng = np.random.default_rng(rng_seed)
    nfr = S['frame'].max() + 1
    out = []
    for _ in range(K):
        A = (rng.random(nfr) < 0.5)[S['frame']]
        sel = (A if use_half_bit else ~A)
        mats = []
        for reg in (0, 1):
            m = sel & (S['half'] == reg)
            idx = np.flatnonzero(m)
            M = sp.csr_matrix((np.ones(len(idx)), (S['op'][idx], idx)), shape=(S['P'], len(S['op'])))
            mats.append((M, np.asarray(M.sum(1)).ravel()))
        out.append(mats)
    return out


def X_from(SE_R, SY_R, ME, MY, relabel=None):
    """SE_R, SY_R: residual matrices (n x B). Returns X per column."""
    vals = []
    for s in range(K):
        for ra, rb in ((0, 1), (1, 0)):
            ME_s, nE = ME[s][ra]
            MY_s, nY = MY[s][rb]
            e = (ME_s @ SE_R); y = (MY_s @ SY_R)
            if relabel is not None:
                y = y[relabel]; nYr = nY[relabel]
            else:
                nYr = nY
            ok = (nE >= MIN_OCC) & (nYr >= MIN_OCC)
            e = e[ok] / nE[ok][:, None]; y = y[ok] / nYr[ok][:, None]
            e = e - e.mean(0); y = y - y.mean(0)
            den = np.sqrt((e * e).sum(0) * (y * y).sum(0))
            vals.append((e * y).sum(0) / np.where(den > 0, den, 1))
    return np.mean(vals, axis=0)


def perm_within(y, cell, B, rng):
    n = len(y)
    stable = np.argsort(cell, kind='stable')
    keys = rng.random((B, n)) + cell[None, :] * 2.0
    rnd = np.argsort(keys, axis=1)
    out = np.empty((B, n))
    out[:, stable] = y[rnd]
    return out.T


def strat_perm(pstrat, rng):
    idx = np.arange(len(pstrat))
    out = idx.copy()
    for s in np.unique(pstrat):
        m = np.flatnonzero(pstrat == s)
        out[m] = rng.permutation(m)
    return out


if __name__ == '__main__':
    rho = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    SE = SIM.skeleton()
    SY = second_dial(SE, seed=99)
    ME = agg_mats(SE, 1, None, True)
    MY = agg_mats(SY, 2, None, False)
    rng = np.random.default_rng(int(1000 * rho) + 7)
    amp = 0.48
    pI, pP, xs = [], [], []
    for rep in range(R):
        z1 = rng.normal(0, 1, SE['P']); z2 = rng.normal(0, 1, SE['P'])
        uE = amp * z1
        uY = amp * (rho * z1 + np.sqrt(1 - rho ** 2) * z2)
        yE, yY = draw(SE, uE, rng), draw(SY, uY, rng)
        cE, cY = SIM.cell_means(yE, SE['cell']), SIM.cell_means(yY, SY['cell'])
        rE, rY = (yE - cE)[:, None], (yY - cY)[:, None]
        x = X_from(rE, rY, ME, MY)[0]
        xs.append(x)
        # null I: independent within-cell permutations
        B = 300
        nE = perm_within(yE, SE['cell'], B, rng) - cE[:, None]
        nY = perm_within(yY, SY['cell'], B, rng) - cY[:, None]
        nullI = X_from(nE, nY, ME, MY)
        pI.append((1 + (np.abs(nullI) >= abs(x)).sum()) / (1 + B))
        # null P: pairing null, relabel Y folios within stratum
        nullP = np.array([X_from(rE, rY, ME, MY, relabel=strat_perm(SE['pstrat'], rng))[0] for _ in range(B)])
        pP.append((1 + (np.abs(nullP) >= abs(x)).sum()) / (1 + B))
        if (rep + 1) % 25 == 0:
            print('rep', rep + 1, flush=True)
    pI, pP = np.array(pI), np.array(pP)
    print('rho %.2f  mean X %.3f sd %.3f | null I (draft) two-sided a01 %.3f a05 %.3f | null P (pairing) a01 %.3f a05 %.3f'
          % (rho, np.mean(xs), np.std(xs), np.mean(pI <= 0.01), np.mean(pI <= 0.05), np.mean(pP <= 0.01),
             np.mean(pP <= 0.05)), flush=True)
