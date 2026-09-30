"""PHASE_770 descriptive statistics for the run (pre-registered as descriptive; no verdict rests on them):
A1 per-folio parts (per-stratum matrices, effective folio count, leave-one-folio-out range), A4 edge checks, A5 residual
variogram, C2 page-pair similarity and face statistics, the Arm B crowding probe, and the Currier A loader for D0.
All functions take residual matrices (n_inf x B) so the same code gives B's values and plant envelopes.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cal770 as C  # noqa: E402

E, B, X = C.E, C.B, C.X


# ------------------------------------------------------------------------------------------------ A1
def quarter_cov_parts(St, R):
    """Per-folio numerator (F x 4 x 4 x B) and denominator (F x 4 x 4) of the A1 estimator, summed over halvings and
    symmetrised; C = sum_f num / sum_f den for any folio subset."""
    Rc = C.group_center(R, St.sq_group)
    Bn = R.shape[1]
    num = np.zeros((St.nf, 4, 4, Bn))
    den = np.zeros((St.nf, 4, 4))
    for MA, MB, nA, nB in zip(St.QA, St.QB, St.nA, St.nB):
        SA = (MA @ Rc).reshape(St.nf, 4, Bn)
        SB = (MB @ Rc).reshape(St.nf, 4, Bn)
        num += np.einsum('fqb,fpb->fqpb', SA, SB)
        den += np.einsum('fq,fp->fqp', nA, nB)
    num = (num + num.transpose(0, 2, 1, 3)) / 2
    den = (den + den.transpose(0, 2, 1)) / 2
    return num, den


def a1_descriptives(St, R0):
    """B's A1 matrix, per-stratum matrices, effective number of folios, leave-one-folio-out range of the features."""
    num, den = quarter_cov_parts(St, R0)
    C_all = num.sum(0)[..., 0] / den.sum(0)
    out = {'C': C_all.tolist()}
    w = den.sum(axis=(1, 2))
    out['effective_folios'] = float(w.sum() ** 2 / (w ** 2).sum())
    st = St.A.page_stratum
    out['per_stratum'] = {}
    for s, name in enumerate(St.A.stratum_names):
        idx = np.flatnonzero(st == s)
        if len(idx) >= 5 and den[idx].sum() > 0:
            Cs = num[idx].sum(0)[..., 0] / np.where(den[idx].sum(0) > 0, den[idx].sum(0), np.nan)
            out['per_stratum']['/'.join(name)] = {'n_folios': int(len(idx)), 'C': Cs.tolist()}
    feats = []
    tot_n, tot_d = num.sum(0)[..., 0], den.sum(0)
    for f in range(St.nf):
        Cf = (tot_n - num[f, ..., 0]) / (tot_d - den[f])
        feats.append(C.Stats.features(Cf[None])[0])
    feats = np.array(feats)
    out['LOFO_feature_range'] = {'min': feats.min(0).tolist(), 'max': feats.max(0).tolist()}
    return out


# ------------------------------------------------------------------------------------------------ A4
def edge_versions(A):
    """Occurrence masks for the A4 edge checks."""
    O = A.O
    L = np.array([A.O['folio_nlines'].get(f, 0) if isinstance(A.O['folio_nlines'], dict) else 0 for f in O['folio']])
    li = O['line_idx']
    edge = np.minimum(li, L - 1 - li)
    return {'all': np.ones(len(li), bool), 'no_par_edges': ~(O['par_first'] | O['par_last']),
            'no_page_edge_2': edge >= 2, 'no_page_edge_4': edge >= 4}


def s3_centred(A_sub):
    """S3c and S3far on an analysis set with residuals centred within stratum x quarter."""
    St = C.Stats(A_sub)
    y = A_sub.O['y'][St.m]
    R = (y - E.cell_means(y, St.cell))[:, None]
    Rc = C.group_center(R, St.sq_group)
    return float(St.S3c(Rc)[0]), float(St.S3far(Rc)[0])


# ------------------------------------------------------------------------------------------------ A5
SEP_BINS = [(1, 1), (2, 2), (3, 4), (5, 8), (9, 16), (17, 32)]


class Variogram:
    """Cross-frame covariance of line residual sums against absolute line separation within pages (sum-of-products
    ratio over halvings), split by page-length stratum (< 20, >= 20 lines) and same / different paragraph; plus the
    same across reading-order page turns (separation = lines to the end of page p + line index on page p+1 + 1)."""

    def __init__(self, St, k=20, seed=7750):
        A, O = St.A, St.A.O
        m = St.m
        self.occ_line = A.occ_line[m]
        self.nL = len(A.line_keys)
        tok = O['token'][m]
        rng = np.random.default_rng(seed)
        self.halves = [(rng.random(O['n_tokens']) < 0.5)[tok] for _ in range(k)]
        n = len(self.occ_line)
        self.mats = []
        for h in self.halves:
            for mask in (h, ~h):
                idx = np.flatnonzero(mask)
                M = sp.csr_matrix((np.ones(len(idx)), (self.occ_line[idx], idx)), shape=(self.nL, n))
                self.mats.append((M, np.asarray(M.sum(1)).ravel()))
        # line pairs within pages
        page, line, L, par = A.L_page, A.L_line, A.L_len, A.L_par
        I, J, cls = [], [], []
        for p in range(len(A.pages)):
            idx = np.flatnonzero(page == p)
            for a_ in range(len(idx)):
                for b_ in range(a_ + 1, len(idx)):
                    i, j = idx[a_], idx[b_]
                    d = line[j] - line[i]
                    for bi, (lo, hi) in enumerate(SEP_BINS):
                        if lo <= d <= hi:
                            I.append(i)
                            J.append(j)
                            cls.append((bi, int(L[i] >= 20), int(par[i] == par[j])))
                            break
        # pairs across reading-order transitions
        pid = {p_: i for i, p_ in enumerate(A.pages)}
        for a, b, _ in A.trans:
            if a not in pid or b not in pid:
                continue
            ia = np.flatnonzero(page == pid[a])
            ib = np.flatnonzero(page == pid[b])
            for i in ia:
                for j in ib:
                    d = (L[i] - 1 - line[i]) + line[j] + 1
                    for bi, (lo, hi) in enumerate(SEP_BINS):
                        if lo <= d <= hi:
                            I.append(i)
                            J.append(j)
                            cls.append((bi, 2, 0))           # stratum code 2: across a page turn
                            break
        self.I, self.J = np.array(I), np.array(J)
        self.cls = cls
        self.keys = sorted(set(cls))

    def __call__(self, R):
        """R (n_inf x B) residuals -> {class key: covariance (B,)}."""
        Bn = R.shape[1]
        num = {k_: np.zeros(Bn) for k_ in self.keys}
        den = {k_: 0.0 for k_ in self.keys}
        cls_idx = defaultdict(list)
        for t, c_ in enumerate(self.cls):
            cls_idx[c_].append(t)
        cls_idx = {k_: np.array(v) for k_, v in cls_idx.items()}
        for t in range(0, len(self.mats), 2):
            (MA, nA), (MB, nB) = self.mats[t], self.mats[t + 1]
            SA, SB = MA @ R, MB @ R
            for k_, ix in cls_idx.items():
                i, j = self.I[ix], self.J[ix]
                num[k_] += (SA[i] * SB[j] + SB[i] * SA[j]).sum(0)
                den[k_] += float((nA[i] * nB[j] + nB[i] * nA[j]).sum())
        return {k_: num[k_] / max(den[k_], 1e-12) for k_ in self.keys}


# ------------------------------------------------------------------------------------------------ C2
def page_positions(A):
    """Original position of each page in its quire (missing leaves counted): 2 x (leaf - first leaf of the quire) +
    (verso); foldout panels share their side's position."""
    pv = E.zl_page_vars()
    first = {}
    for p, v in pv.items():
        m = re.match(r'f(\d+)[rv]', p)
        if m and v.get('Q'):
            first[v['Q']] = min(first.get(v['Q'], 10 ** 6), int(m.group(1)))
    pos, quire = [], []
    for p in A.pages:
        m = re.match(r'f(\d+)([rv])', p)
        q = pv.get(p, {}).get('Q')
        quire.append(q)
        pos.append(2 * (int(m.group(1)) - first.get(q, int(m.group(1)))) + (m.group(2) == 'v'))
    return np.array(pos), np.array(quire, dtype=object)


def page_similarity(St, R, k_pairs):
    """Whole-page cross-frame similarity for page pairs (P x 2): mean over halvings of (m^A_a m^B_b + m^B_a m^A_b)/2,
    page means centred within stratum."""
    A = St.A
    st = A.page_stratum
    acc = np.zeros((len(k_pairs), R.shape[1]))
    for h in St.halves:
        vals = []
        for mask in (h, ~h):
            idx = np.flatnonzero(mask)
            M = sp.csr_matrix((np.ones(len(idx)), (St.fu[idx], idx)), shape=(St.nf, len(St.fu)))
            cnt = np.asarray(M.sum(1)).ravel()
            mean = np.where(cnt[:, None] > 0, (M @ R) / np.maximum(cnt, 1)[:, None], np.nan)
            for s in np.unique(st):
                rows = st == s
                if np.isfinite(mean[rows]).any():
                    mean[rows] -= np.nanmean(mean[rows], axis=0)
            vals.append(np.nan_to_num(mean))
        mA, mB = vals
        a, b = k_pairs[:, 0], k_pairs[:, 1]
        acc += (mA[a] * mB[b] + mB[a] * mA[b]) / 2
    return acc / len(St.halves)


def c2_pairs(St):
    """Same-quire page pairs with type labels: leaf pair, opening, sheet face, cross-face (same bifolium, different
    face, not a leaf pair), and the Gregory's-rule same-side indicator; reading distance on original positions."""
    A = St.A
    pos, quire = page_positions(A)
    pid = {p: i for i, p in enumerate(A.pages)}
    faces = {tuple(sorted(x)) for x in St.FACES.tolist()}
    leafpair, opening = set(), set()
    for a, b, kind in A.trans:
        if a in pid and b in pid:
            (leafpair if kind == 'leaf_turn' else opening).add(tuple(sorted((pid[a], pid[b]))))
    pv = E.zl_page_vars()
    bif_of = {}
    for i, p in enumerate(A.pages):
        v = pv.get(p, {})
        if v.get('Q') and v.get('B'):
            bif_of[i] = (v['Q'], v['B'])
    rows = []
    for i in range(len(A.pages)):
        for j in range(i + 1, len(A.pages)):
            if quire[i] is None or quire[i] != quire[j]:
                continue
            key = (i, j)
            same_bif = bif_of.get(i) is not None and bif_of.get(i) == bif_of.get(j)
            ptype = ('leaf' if key in leafpair else 'opening' if key in opening else 'face' if key in faces
                     else 'crossface' if same_bif else 'other')
            side_i = ((pos[i] + 1) // 2) % 2
            side_j = ((pos[j] + 1) // 2) % 2
            rows.append((i, j, abs(int(pos[i]) - int(pos[j])), ptype, int(side_i == side_j)))
    return rows


def c2_summary(St, R0, nperm=2000, seed=7751):
    """Mean similarity by pair type; face pairs against same-quire 'other' pairs at the same reading distance, with a
    permutation p (page labels permuted within quire); same-side (Gregory) contrast among 'other' pairs."""
    rows = c2_pairs(St)
    P = np.array([(r[0], r[1]) for r in rows])
    sim = page_similarity(St, R0, P)[:, 0]
    dist = np.array([r[2] for r in rows])
    ptype = np.array([r[3] for r in rows], dtype=object)
    same = np.array([r[4] for r in rows])
    out = {'by_type': {t: {'n': int((ptype == t).sum()), 'mean': float(sim[ptype == t].mean())}
                       for t in ('leaf', 'opening', 'face', 'crossface', 'other') if (ptype == t).any()}}

    def face_vs_matched(s):
        diffs, ws = [], []
        for d in np.unique(dist[ptype == 'face']):
            f = s[(ptype == 'face') & (dist == d)]
            o = s[(ptype == 'other') & (dist == d)]
            if len(f) and len(o):
                diffs.append(f.mean() - o.mean())
                ws.append(len(f))
        return float(np.average(diffs, weights=ws)) if diffs else float('nan')

    obs = face_vs_matched(sim)
    oth = ptype == 'other'
    obs_side = float(sim[oth & (same == 1)].mean() - sim[oth & (same == 0)].mean())
    # permutation: page labels within quire
    pos, quire = page_positions(St.A)
    rng = np.random.default_rng(seed)
    null_f, null_s = [], []
    Rq = {}
    for q in set(quire.tolist()):
        Rq[q] = np.flatnonzero(quire == q)
    for _ in range(nperm):
        perm = np.arange(len(quire))
        for q, idx in Rq.items():
            perm[idx] = rng.permutation(idx)
        s_p = page_similarity_cached(St, R0, P, perm)
        null_f.append(face_vs_matched(s_p))
        null_s.append(float(s_p[oth & (same == 1)].mean() - s_p[oth & (same == 0)].mean()))
    null_f, null_s = np.array(null_f), np.array(null_s)
    out['face_minus_matched'] = obs
    out['face_minus_matched_p_two_sided'] = float((1 + (np.abs(null_f - np.nanmean(null_f)) >=
                                                       abs(obs - np.nanmean(null_f))).sum()) / (1 + nperm))
    out['same_side_minus_other'] = obs_side
    out['same_side_p_two_sided'] = float((1 + (np.abs(null_s - null_s.mean()) >= abs(obs_side - null_s.mean())).sum())
                                         / (1 + nperm))
    return out


_SIM_CACHE = {}


def page_similarity_cached(St, R0, P, perm):
    """Similarity of permuted page pairs, from a cached full page x page similarity matrix."""
    key = id(R0)
    if key not in _SIM_CACHE:
        n = St.nf
        allp = np.array([(i, j) for i in range(n) for j in range(n)])
        S = page_similarity(St, R0, allp)[:, 0].reshape(n, n)
        _SIM_CACHE.clear()
        _SIM_CACHE[key] = S
    S = _SIM_CACHE[key]
    return S[perm[P[:, 0]], perm[P[:, 1]]]


# ------------------------------------------------------------------------------------------------ Arm B crowding probe
def crowding_probe(A, nperm=2000, seed=7752):
    """Within folio and within-line position quintile: the dial residual against line fullness (collapsed units /
    page median). Statistic: sum over informative occurrences of r_i x (fullness_i - mean fullness in its folio x pos5
    group); null: y permuted within cell x folio."""
    O = A.O
    m = O['informative']
    y = O['y'][m]
    cell = O['cell'][m]
    f = O['folio'][m]
    g = f * 5 + O['pos5'][m]
    full = O['fullness'][m]
    _, gi = np.unique(g, return_inverse=True)
    gi = gi.ravel()
    fc = full - np.bincount(gi, weights=full)[gi] / np.bincount(gi)[gi]
    cm = E.cell_means(y, cell)
    obs = float(((y - cm) * fc).sum())
    _, cf = np.unique(np.stack([cell, f], 1), axis=0, return_inverse=True)
    cf = cf.ravel()
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(0, nperm, 250):
        Yp = B.perm_batch(y, cf, 250, rng)
        null.append(((Yp - cm[None, :]) * fc[None, :]).sum(1))
    null = np.concatenate(null)
    return {'stat': obs, 'null_mean': float(null.mean()), 'null_sd': float(null.std()),
            'p_two_sided': float((1 + (np.abs(null - null.mean()) >= abs(obs - null.mean())).sum()) / (1 + nperm))}


# ------------------------------------------------------------------------------------------------ D0
def load_a_h():
    """Currier A, H track, P placement, uncertain tokens dropped (same record format as ed769.load_b_h)."""
    from scripts.voynich import Transcript
    pv = E.zl_page_vars()
    rows = []
    for t in Transcript().currier_a(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if w:
            rows.append((w, t.folio, t.line, t.par_initial, t.section, '*' in w))
    return E._assemble(rows, pv)
