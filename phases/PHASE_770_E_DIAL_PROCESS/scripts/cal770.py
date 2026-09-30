"""PHASE_770 calibration machinery (controls only): the analysis set, latent-field plant generators over the lines of the
analysis set, and the statistics of Arms 0, A and C, vectorised over replicate columns.

Nothing here computes a statistic of B's observed outcomes by folio, position or page turn; the run script does that
after the lock. Plants keep B's cell-level base rates (PHASE_769 base_logit) and replace the outcome.
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
import ed770 as X  # noqa: E402

E, B = X.E, X.B
K_SPLITS = 50
DRY_FAKE_CONS = False       # set by run_b770.py --dry only


# ------------------------------------------------------------------------------------------------ analysis set
def transitions_and_chains(pages, pv, exclude=(('f40v', 'f41r'),)):
    """Usable reading-order transitions between consecutive B pages (leaf turn r->v of one leaf; opening v->r of
    consecutive leaves; no foldout panels; listed exclusions) and the maximal chains they form."""
    info = []
    for p in pages:
        m = re.match(r'f(\d+)([rv])(\d*)$', p)
        info.append((p, int(m.group(1)), m.group(2), m.group(3) or None, pv.get(p, {}).get('Q')))
    trans = []
    for a, b in zip(info, info[1:]):
        if a[3] or b[3] or (a[0], b[0]) in exclude:
            continue
        if a[1] == b[1] and a[2] == 'r' and b[2] == 'v':
            trans.append((a[0], b[0], 'leaf_turn'))
        elif a[2] == 'v' and b[2] == 'r' and b[1] == a[1] + 1:
            trans.append((a[0], b[0], 'opening'))
    nxt = {a: b for a, b, _ in trans}
    has_prev = {b for _, b, _ in trans}
    chains = []
    for p in pages:
        if p in has_prev:
            continue
        c = [p]
        while c[-1] in nxt:
            c.append(nxt[c[-1]])
        chains.append(c)
    return trans, chains


class Analysis:
    """The analysis set for one dial. set81: PHASE_770 set (f76r included); otherwise PHASE_769's 80 folios.
    f115r_hand: hand assigned to f115r (None keeps the blank ZL value, as in PHASE_769)."""

    def __init__(self, dial='E', set81=True, f115r_hand='3', cell_extra=(), recs=None, amap_leg=None, zl=False,
                 subset=None, pair_dials=None):
        self.dial = dial
        if amap_leg is None:
            H = X.track_lines_plus('H') if set81 else B.track_lines('H')
            F = X.track_lines_plus('F') if set81 else B.track_lines('F')
            amap_leg = X.alignment(H, F)
        self.amap, self.leg = amap_leg
        if recs is None:
            if zl:
                h_pages = set(r[1] for r in (X.load_b_h_plus() if set81 else E.load_b_h()))
                recs = [r for r in E.load_b_zl() if r[1] in h_pages]      # same pages as the H analysis set
            else:
                recs = X.load_b_h_plus() if set81 else E.load_b_h()
            if f115r_hand:
                recs = X.fix_hands(recs, {'f115r': f115r_hand})
        self.recs = recs
        amapZ = None
        if subset in ('consZ', 'cons3') and not zl:
            H = X.track_lines_plus('H') if set81 else B.track_lines('H')
            Z = X.zl_lines()
            amapZ = X.alignment(H, Z, key_map=X.zl_content_map(H, Z))[0]
        O = X.occurrences(recs, dial, None if zl else self.amap, cell_extra=cell_extra, pair_dials=pair_dials,
                          amapZ=amapZ)
        if subset is not None and DRY_FAKE_CONS:         # dry run only: consistency flags are meaningless on poured text
            O = subset_O(O, np.random.default_rng(7799).random(len(O['y'])) < 0.85)
        elif subset == 'cons3':                          # read alike by H, F and ZL
            O = subset_O(O, O['cons'] & O['consZ'])
        elif subset is not None:
            O = subset_O(O, O[subset])
        self.O = O
        self.Xcov = B.folio_covariates(recs, O, self.leg)
        pv = E.zl_page_vars()
        self.pages = list(O['folio_names'])
        self.trans, self.chains = transitions_and_chains(list(dict.fromkeys(r[1] for r in recs)), pv)
        # page strata (section / hand)
        st = {}
        for r in recs:
            st.setdefault(r[1], (r[7], r[8]))
        self.page_stratum_key = [st[p] for p in self.pages]
        keys = {k: i for i, k in enumerate(dict.fromkeys(self.page_stratum_key))}
        self.page_stratum = np.array([keys[k] for k in self.page_stratum_key])
        self.stratum_names = list(keys)
        self._line_table()

    # ------------------------------------------------------------------ line table
    def _line_table(self):
        S = X.page_structure(self.recs)
        fid = {f: i for i, f in enumerate(self.pages)}
        keys = [k for k in S if k[0] in fid]
        keys.sort(key=lambda k: (fid[k[0]], S[k]['line']))
        self.line_keys = keys
        lid = {k: i for i, k in enumerate(keys)}
        self.L_page = np.array([fid[k[0]] for k in keys])
        self.L_line = np.array([S[k]['line'] for k in keys])
        self.L_len = np.array([S[k]['L'] for k in keys])
        self.L_par_first = np.array([S[k]['par_first'] for k in keys])
        self.L_par_last = np.array([S[k]['par_last'] for k in keys])
        self.L_par_idx = np.array([S[k]['par_idx'] for k in keys])
        self.L_npar = np.array([S[k]['n_par'] for k in keys])
        self.L_edge = np.minimum(self.L_line, self.L_len - 1 - self.L_line)
        # paragraph unit per line (global paragraph id from recs)
        par_of = {}
        for r in self.recs:
            par_of.setdefault(r[2], r[5])
        pu = {p: i for i, p in enumerate(dict.fromkeys(par_of[k] for k in keys))}
        self.L_par = np.array([pu[par_of[k]] for k in keys])
        # writing sequence along chains (pages not in any chain form their own chain)
        chain_of, pos_in_chain = {}, {}
        for c, pages in enumerate(self.chains):
            for j, p in enumerate(pages):
                chain_of[p], pos_in_chain[p] = c, j
        nxt = len(self.chains)
        for p in self.pages:
            if p not in chain_of:
                chain_of[p], pos_in_chain[p] = nxt, 0
                nxt += 1
        self.n_chains = nxt
        self.L_chain = np.array([chain_of[k[0]] for k in keys])
        order = sorted(range(len(keys)), key=lambda i: (self.L_chain[i], pos_in_chain[keys[i][0]], self.L_line[i]))
        self.L_seq = np.empty(len(keys), dtype=int)
        pos = defaultdict(int)
        for i in order:
            c = self.L_chain[i]
            self.L_seq[i] = pos[c]
            pos[c] += 1
        self.chain_len = np.array([pos[c] for c in range(self.n_chains)])
        self.occ_line = np.array([lid[k] for k in self.O['line_keys']])

    # ------------------------------------------------------------------ base logit
    def base_logit(self):
        p = np.clip(E.cell_means(self.O['y'], self.O['cell']), 0.01, 0.99)
        return np.log(p / (1 - p))


def subset_O(O, mask):
    """Restrict an occurrence set to a mask; cells re-indexed and 'informative' recomputed within the subset (folio
    indexing kept)."""
    n = len(O['y'])
    mask = np.asarray(mask, dtype=bool)
    out = {}
    for k, v in O.items():
        if isinstance(v, np.ndarray) and v.shape[:1] == (n,):
            out[k] = v[mask]
        elif isinstance(v, list) and len(v) == n and k not in ('folio_names', 'token_str', 'jkey_str'):
            out[k] = [x for x, keep in zip(v, mask) if keep]
        else:
            out[k] = v
    _, out['cell'] = np.unique(out['cell'], return_inverse=True)
    out['cell'] = out['cell'].ravel()
    cf = defaultdict(set)
    for c, f in zip(out['cell'], out['folio']):
        cf[c].add(f)
    out['informative'] = np.array([len(cf[c]) >= 2 for c in out['cell']])
    return out


def cell_means_batch(Y, cell):
    """Per-occurrence cell means for each column of Y (n x B)."""
    n = len(cell)
    G = sp.csr_matrix((np.ones(n), (cell, np.arange(n))), shape=(cell.max() + 1, n))
    cnt = np.asarray(G.sum(axis=1)).ravel()
    return (G @ Y / np.maximum(cnt, 1)[:, None])[cell]


def group_center(R, groups):
    """Subtract the group mean (per column) from each row of R (n x B)."""
    n = len(groups)
    _, g = np.unique(groups, return_inverse=True)
    g = g.ravel()
    G = sp.csr_matrix((np.ones(n), (g, np.arange(n))), shape=(g.max() + 1, n))
    cnt = np.asarray(G.sum(axis=1)).ravel()
    return R - (G @ R / np.maximum(cnt, 1)[:, None])[g]


# ------------------------------------------------------------------------------------------------ plants
class Plants:
    """Latent fields over the analysis set's lines (n_lines x B), mapped to occurrences. Each model's field is
    normalised to unit SD over the informative occurrences, column by column, then scaled."""

    def __init__(self, A: Analysis, background=True):
        """background: add the within-folio context (preceding two collapsed units) and line-fullness effects, estimated
        on the analysis set's own outcomes with folio fixed effects, to every plant's logit (lean-expert v2 check)."""
        self.A = A
        self.lg = A.base_logit()
        self.m = A.O['informative']
        self.bg = None
        if background:
            ctx = within_folio_effect(A, 'prev')[1]
            lay = within_folio_effect(A, 'full3')[1]
            self.bg = ctx + lay
            self.lg = self.lg + self.bg
        A_ = A
        self.nL = len(A_.line_keys)
        self.nP = len(A_.pages)
        # line index arrays grouped by page, paragraph and chain (for loops over position)
        self.page_lines = [np.flatnonzero(A_.L_page == p) for p in range(self.nP)]
        self.max_len = int(A_.L_len.max())
        # position-major arrays: for each page, lines sorted by line index (already sorted in the table)

    def _to_occ(self, Z):
        return Z[self.A.occ_line]

    def _normalise(self, Zocc):
        sd = Zocc[self.m].std(axis=0)
        return Zocc / np.where(sd > 0, sd, 1)

    # --- fields (n_lines x B)
    def f_page_const(self, rng, B_):
        return rng.normal(0, 1, (self.nP, B_))[self.A.L_page]

    def f_par_const(self, rng, B_):
        return rng.normal(0, 1, (self.A.L_par.max() + 1, B_))[self.A.L_par]

    def f_restart_walk(self, rng, B_, unit):
        """Random walk over lines restarting at 0 at the first line of each unit (page or paragraph)."""
        A = self.A
        eps = rng.normal(0, 1, (self.nL, B_))
        u = A.L_page if unit == 'page' else A.L_par
        first = np.r_[True, u[1:] != u[:-1]]
        eps[first] = 0.0
        cs = np.cumsum(eps, axis=0)
        start_idx = np.maximum.accumulate(np.where(first, np.arange(self.nL), 0))
        return cs - cs[start_idx]

    def f_ar1_page(self, rng, B_, rho):
        A = self.A
        Z = np.empty((self.nL, B_))
        first = np.r_[True, A.L_page[1:] != A.L_page[:-1]]
        z = rng.normal(0, 1, B_)
        s = np.sqrt(1 - rho ** 2)
        for i in range(self.nL):
            if first[i]:
                z = rng.normal(0, 1, B_)
            else:
                z = rho * z + s * rng.normal(0, 1, B_)
            Z[i] = z
        return Z

    def f_trend(self, rng, B_):
        A = self.A
        beta = rng.normal(0, 1, (self.nP, B_))[A.L_page]
        frac = (A.L_line / np.maximum(A.L_len - 1, 1))[:, None]
        return beta * frac

    def _seq_order(self):
        A = self.A
        return np.lexsort((A.L_seq, A.L_chain))

    def f_ar1_chain(self, rng, B_, rho):
        A = self.A
        order = self._seq_order()
        Z = np.empty((self.nL, B_))
        s = np.sqrt(1 - rho ** 2)
        prev_chain = -1
        z = None
        for i in order:
            if A.L_chain[i] != prev_chain:
                z = rng.normal(0, 1, B_)
                prev_chain = A.L_chain[i]
            else:
                z = rho * z + s * rng.normal(0, 1, B_)
            Z[i] = z
        return Z

    def face_order(self):
        """Page order for writing on flat sheets before folding (advisor v2 check): within each quire, bifolia from the
        outermost inward; on each bifolium the outer face (B-v left, A-r right) then the inner face (A-v left, B-r
        right), where A is the lower-numbered leaf. Pages without a conjoint (singletons, foldouts) follow in reading
        order. Returns {page: rank}."""
        A = self.A
        pv = E.zl_page_vars()
        bif = defaultdict(set)
        for p, v in pv.items():
            m = re.match(r'f(\d+)[rv]', p)
            if m and v.get('Q') and v.get('B'):
                bif[(v['Q'], v['B'])].add(int(m.group(1)))
        key = {}
        for i, p in enumerate(A.pages):
            v = pv.get(p, {})
            m = re.match(r'f(\d+)([rv])(\d*)$', p)
            leaves = sorted(bif.get((v.get('Q'), v.get('B')), []))
            if len(leaves) == 2 and not m.group(3):
                lo, hi = leaves
                n, side = int(m.group(1)), m.group(2)
                slot = {(hi, 'v'): 0, (lo, 'r'): 1, (lo, 'v'): 2, (hi, 'r'): 3}[(n, side)]
                key[p] = (v.get('Q'), int(v.get('B')), slot, 0)
            else:
                key[p] = (v.get('Q'), 99, 0, i)
        order = sorted(A.pages, key=lambda p: key[p])
        return {p: r for r, p in enumerate(order)}

    def f_ar1_face(self, rng, B_, rho):
        """AR(1) over lines continuing across pages in flat-sheet face order within each quire (stationary start per
        quire)."""
        A = self.A
        rank = self.face_order()
        pv = E.zl_page_vars()
        quire = np.array([pv.get(A.pages[p], {}).get('Q') for p in A.L_page])
        page_rank = np.array([rank[A.pages[p]] for p in A.L_page])
        order = np.lexsort((A.L_line, page_rank))
        Z = np.empty((self.nL, B_))
        s = np.sqrt(1 - rho ** 2)
        prev_q, z = None, None
        for i in order:
            if quire[i] != prev_q:
                z = rng.normal(0, 1, B_)
                prev_q = quire[i]
            else:
                z = rho * z + s * rng.normal(0, 1, B_)
            Z[i] = z
        return Z

    def f_changepoint(self, rng, B_, mean_seg):
        A = self.A
        order = self._seq_order()
        Z = np.empty((self.nL, B_))
        prev_chain = -1
        z = None
        p = 1.0 / mean_seg
        for i in order:
            if A.L_chain[i] != prev_chain:
                z = rng.normal(0, 1, B_)
                prev_chain = A.L_chain[i]
            else:
                jump = rng.random(B_) < p
                z = np.where(jump, rng.normal(0, 1, B_), z)
            Z[i] = z
        return Z

    def f_page_ar(self, rng, B_, rho):
        """Constant per page, correlated along reading-order chains: AR(1) over pages within a chain (stationary)."""
        A = self.A
        chain_pages = defaultdict(list)
        for i, p in enumerate(A.pages):
            chain_pages[A.L_chain[self.page_lines[i][0]]].append(i)
        U = np.empty((self.nP, B_))
        s = np.sqrt(1 - rho ** 2)
        for c, pages in chain_pages.items():
            pages = sorted(pages, key=lambda i: A.L_seq[self.page_lines[i][0]])
            z = rng.normal(0, 1, B_)
            for j, i in enumerate(pages):
                if j > 0:
                    z = rho * z + s * rng.normal(0, 1, B_)
                U[i] = z
        return U[A.L_page]

    def f_parchment(self, rng, B_):
        """Gregory's rule: within a quire, the pages in reading order run H F F H H F F H ... (random start per quire);
        latent = side sign x a quire-level amplitude, plus an independent page constant (half the variance each)."""
        A = self.A
        pv = E.zl_page_vars()
        quire_pages = defaultdict(list)
        for i, p in enumerate(A.pages):
            quire_pages[pv.get(p, {}).get('Q')].append(i)
        side = np.zeros(self.nP)
        for q, pages in quire_pages.items():
            # page order in the quire from the ZL $P letter (reading order within the quire)
            pages = sorted(pages, key=lambda i: pv.get(A.pages[i], {}).get('P', ''))
            start = rng.integers(2)
            for i in pages:
                k = ord(pv.get(A.pages[i], {}).get('P', 'A')) - ord('A')          # page position in the quire
                side[i] = 1.0 if ((k + 1) // 2 + start) % 2 == 0 else -1.0
        amp = rng.normal(0, 1, (1, B_))
        U = np.sqrt(0.5) * side[:, None] * np.abs(amp) + np.sqrt(0.5) * rng.normal(0, 1, (self.nP, B_))
        return U[A.L_page]

    def f_quire_trend(self, rng, B_):
        """A trend across the pages of each quire plus a stratum-specific top/bottom offset (no continuity)."""
        A = self.A
        pv = E.zl_page_vars()
        qpos = np.array([ord(pv.get(p, {}).get('P', 'A')) - ord('A') for p in A.pages], dtype=float)
        quire = [pv.get(p, {}).get('Q') for p in A.pages]
        slope = {q: rng.normal(0, 1, B_) for q in set(quire)}
        U = np.stack([slope[quire[i]] * (qpos[i] / 20.0) for i in range(self.nP)])
        st = A.page_stratum[A.L_page]
        off = rng.normal(0, 1, (st.max() + 1, B_))
        frac = (A.L_line / np.maximum(A.L_len - 1, 1) - 0.5)[:, None]
        return U[A.L_page] + off[st] * frac

    # --- models -> occurrence-level latent (n_occ x B), unit SD over informative occurrences
    def latent(self, model, rng, B_):
        A = self.A
        name, _, arg = model.partition(':')
        if name == 'M1':
            Z = self.f_page_const(rng, B_)
        elif name == 'PAGEAR':
            Z = self.f_page_ar(rng, B_, float(arg))
        elif name == 'PARCH':
            Z = self.f_parchment(rng, B_)
        elif name == 'QTREND':
            Z = self.f_quire_trend(rng, B_)
        elif name == 'M6M2B':
            Z = self.f_ar1_chain(rng, B_, 0.97) * (A.L_edge >= int(arg))[:, None]
        elif name == 'M6FACE':
            Z = self.f_ar1_face(rng, B_, float(arg))
        elif name == 'M2a':
            Z = self.f_page_const(rng, B_) * (~(A.L_par_first | A.L_par_last))[:, None]
        elif name == 'M2b':
            Z = self.f_page_const(rng, B_) * (A.L_edge >= int(arg))[:, None]
        elif name == 'M2c':
            Z = self.f_page_const(rng, B_) * ((A.L_par_idx > 0) & (A.L_par_idx < A.L_npar - 1))[:, None]
        elif name == 'M7':
            Z = np.sqrt(0.5) * self.f_page_const(rng, B_) + np.sqrt(0.5) * self.f_par_const(rng, B_)
        elif name == 'M3':
            Z = self.f_restart_walk(rng, B_, 'page')
        elif name == 'M4':
            Z = self.f_ar1_page(rng, B_, float(arg))
        elif name == 'M5':
            Z = self.f_trend(rng, B_)
        elif name == 'M6':
            Z = self.f_ar1_chain(rng, B_, float(arg))
        elif name == 'M8':
            Z = self.f_changepoint(rng, B_, float(arg))
        elif name == 'M9':
            Z = self.f_restart_walk(rng, B_, 'par')
        elif name == 'MIX':
            base, w = arg.split('/')
            w = float(w)
            z1 = self._normalise(self._to_occ(self.f_page_const(rng, B_)))
            z2 = self._normalise(self.latent(base, rng, B_))
            return self._normalise(np.sqrt(1 - w) * z1 + np.sqrt(w) * z2)
        else:
            raise ValueError(model)
        return self._normalise(self._to_occ(Z))

    def draw(self, model, scales, rng, extra_logit=None):
        """y (n_occ x B) for the model at the given per-column scales (B,). extra_logit: an occurrence-level (n_occ,)
        or (n_occ x B) term added to the logit (CONTEXT, LAYOUT)."""
        B_ = len(scales)
        if model == 'NONE':
            lg = np.repeat(self.lg[:, None], B_, axis=1)
        else:
            lg = self.lg[:, None] + self.latent(model, rng, B_) * scales[None, :]
        if extra_logit is not None:
            lg = lg + (extra_logit[:, None] if extra_logit.ndim == 1 else extra_logit)
        return (rng.random(lg.shape) < 1 / (1 + np.exp(-lg))).astype(float)


def within_folio_effect(A: Analysis, attr, y=None, min_n=30, iters=25):
    """Additive effect of a categorical occurrence attribute on the outcome, with cell means removed and folio fixed
    effects (backfitting on the linear-probability scale), so no folio component leaks into the effect (lean-expert v2
    check). Returns (effect on the probability scale per occurrence, effect on the logit scale centred within cell per
    occurrence, {category: effect}). Categories with < min_n occurrences get 0."""
    O = A.O
    y = O['y'] if y is None else y
    r = y - E.cell_means(y, O['cell'])
    vals = np.array(O[attr]) if isinstance(O[attr], list) else O[attr]
    keys, k = np.unique(vals, return_inverse=True)
    k = k.ravel()
    f = O['folio']
    nk = np.bincount(k, minlength=len(keys)).astype(float)
    nf = np.bincount(f).astype(float)
    b = np.zeros(len(keys))
    for _ in range(iters):
        a = np.bincount(f, weights=r - b[k], minlength=len(nf)) / np.maximum(nf, 1)
        b = np.bincount(k, weights=r - a[f], minlength=len(keys)) / np.maximum(nk, 1)
    b = np.where(nk >= min_n, b, 0.0)
    b = b - (b * nk).sum() / nk.sum()
    eff_p = b[k]
    pbar = float(y.mean())
    eff_l = eff_p / (pbar * (1 - pbar))
    return eff_p, eff_l - E.cell_means(eff_l, O['cell']), {str(kk): float(v) for kk, v in zip(keys, b)}


def d14(A: Analysis, P, model, rng, B_=200):
    """Latent position contrast D14 = E(u1 - u4)^2 / E(u1^2 + u4^2), u_q = mean latent over a page's informative
    occurrences in quarter q (lean-expert v2 check; computed from the latent field alone, no outcomes)."""
    Z = P.latent(model, rng, B_)
    m = A.O['informative']
    f, q = A.O['folio'][m], A.O['quarter'][m]
    Z = Z[m]
    u = {}
    for qq in (0, 3):
        sel = q == qq
        s = np.zeros((len(A.pages), B_))
        np.add.at(s, f[sel], Z[sel])
        n = np.bincount(f[sel], minlength=len(A.pages))
        u[qq] = (s / np.maximum(n, 1)[:, None], n > 0)
    ok = u[0][1] & u[3][1]
    u1, u4 = u[0][0][ok], u[3][0][ok]
    return float(((u1 - u4) ** 2).sum() / (u1 ** 2 + u4 ** 2).sum())


def pooled_effect(A: Analysis, attr):
    """Pooled (all folios) effect of an occurrence attribute on the outcome within cells, on the logit scale, centred
    within cell: returns the occurrence-level term delta(attr_i) - cell mean of delta. Uses B's outcome pooled over all
    folios (no folio, position or page-turn information)."""
    O = A.O
    y = O['y']
    r = y - E.cell_means(y, O['cell'])
    vals = O[attr] if not isinstance(O[attr], list) else np.array(O[attr])
    keys, inv = np.unique(vals, return_inverse=True)
    inv = inv.ravel()
    s = np.bincount(inv, weights=r)
    n = np.bincount(inv)
    pbar = y.mean()
    d = (s / np.maximum(n, 1)) / (pbar * (1 - pbar))
    d = np.where(n >= 30, d, 0.0)                    # rare contexts: no effect
    t = d[inv]
    return t - E.cell_means(t, O['cell']), dict(zip([str(k) for k in keys], d.tolist()))


# ------------------------------------------------------------------------------------------------ statistics
class Stats:
    """Arm 0 / A / C statistics for one analysis set, restricted to informative occurrences."""

    def __init__(self, A: Analysis, k=K_SPLITS, seed=7700):
        self.A = A
        O = A.O
        m = O['informative']
        self.m = m
        self.cell = O['cell'][m]
        self.fu = O['folio'][m]
        self.nf = len(A.pages)
        self.X = A.Xcov
        tok = O['token'][m]
        self.S3c = B.Coherence(self.fu, O['half'][m], tok, O['n_tokens'], self.nf, k=k, X=self.X)
        self.S3far = B.Coherence(self.fu, O['quart'][m], tok, O['n_tokens'], self.nf, k=k, X=self.X)
        self.quarter = O['quarter'][m]
        self.stratum = A.page_stratum[self.fu]
        self.sq_group = self.stratum * 4 + self.quarter
        # halvings of the split key (the dial frame)
        rng = np.random.default_rng(seed)
        self.halves = [(rng.random(O['n_tokens']) < 0.5)[tok] for _ in range(k)]
        self._quarter_cov_setup()
        self._page_turn_setup()

    def residuals(self, Y):
        Ym = Y[self.m]
        return Ym - cell_means_batch(Ym, self.cell)

    # --- A1: quarter covariance (sum-of-products ratio), stratum x quarter centred
    def _quarter_cov_setup(self):
        n = len(self.fu)
        row = self.fu * 4 + self.quarter
        self.QA, self.QB, self.nA, self.nB = [], [], [], []
        for h in self.halves:
            for mask in (h, ~h):
                idx = np.flatnonzero(mask)
                M = sp.csr_matrix((np.ones(len(idx)), (row[idx], idx)), shape=(self.nf * 4, n))
                (self.QA if mask is h else self.QB).append(M)
            self.nA.append(np.bincount(row[h], minlength=self.nf * 4).reshape(self.nf, 4).astype(float))
            self.nB.append(np.bincount(row[~h], minlength=self.nf * 4).reshape(self.nf, 4).astype(float))

    def quarter_cov(self, R):
        """R: (n_inf x B) residuals -> C (B x 4 x 4)."""
        Rc = group_center(R, self.sq_group)
        Bn = R.shape[1]
        num = np.zeros((Bn, 4, 4))
        den = np.zeros((4, 4))
        for MA, MB, nA, nB in zip(self.QA, self.QB, self.nA, self.nB):
            SA = (MA @ Rc).reshape(self.nf, 4, Bn)
            SB = (MB @ Rc).reshape(self.nf, 4, Bn)
            num += np.einsum('fqb,fpb->bqp', SA, SB)
            den += nA.T @ nB
        C = num / den[None]
        return (C + C.transpose(0, 2, 1)) / 2

    @staticmethod
    def features(C, scale_free=False):
        V = np.stack([C[:, q, q] for q in range(4)], axis=1)
        D = []
        for d in (1, 2, 3):
            D.append(np.mean([C[:, q, q + d] for q in range(4 - d)], axis=0))
        F = np.concatenate([V, np.stack(D, axis=1)], axis=1)
        if scale_free:                                   # six features (V1-V3, D1-D3) / mean(V1-V4); not singular
            mv = V.mean(axis=1, keepdims=True)
            F = np.concatenate([V[:, :3], np.stack(D, axis=1)], axis=1) / np.where(np.abs(mv) > 0, mv, 1)
        return F

    # --- C1: page-turn continuity
    def _page_turn_setup(self):
        A = self.A
        pid = {p: i for i, p in enumerate(A.pages)}
        self.T = np.array([(pid[a], pid[b]) for a, b, _ in A.trans if a in pid and b in pid])
        self.T_kind = np.array([k for a, b, k in A.trans if a in pid and b in pid])
        chain_of = {}
        for c, pages in enumerate(A.chains):
            for p in pages:
                chain_of[p] = c
        self.T_chain = np.array([chain_of[A.pages[a]] for a, _ in self.T])
        pv = E.zl_page_vars()
        self.T_quire = np.array([pv.get(A.pages[a], {}).get('Q') for a, _ in self.T])
        # quire half of each transition (by the ZL page position $P of its first page within the quire)
        qn = defaultdict(int)
        for pg, v in pv.items():
            if v.get('Q') and v.get('P'):
                qn[v['Q']] = max(qn[v['Q']], ord(v['P']) - ord('A') + 1)
        self.T_half = np.array([int((ord(pv.get(A.pages[a], {}).get('P', 'A')) - ord('A')) >= qn[pv.get(A.pages[a], {}).get('Q')] / 2)
                                for a, _ in self.T])
        # sheet faces (both pages in the analysis set; left page first): outer B-v | A-r, inner A-v | B-r, A the
        # lower-numbered leaf of the bifolium; the reading-adjacent inner face (an opening) is left to C1
        bif = defaultdict(set)
        for pg, v in pv.items():
            m = re.match(r'f(\d+)[rv]', pg)
            if m and v.get('Q') and v.get('B'):
                bif[(v['Q'], v['B'])].add(int(m.group(1)))
        faces, fkind = [], []
        for (qq, bb), leaves in sorted(bif.items()):
            if len(leaves) != 2:
                continue
            lo, hi = sorted(leaves)
            for kind, (l, r) in (('outer', (f'f{hi}v', f'f{lo}r')), ('inner', (f'f{lo}v', f'f{hi}r'))):
                if l in pid and r in pid and not (kind == 'inner' and hi == lo + 1):
                    faces.append((pid[l], pid[r]))
                    fkind.append(kind)
        self.FACES = np.array(faces, dtype=int).reshape(-1, 2)
        self.F_kind = np.array(fkind)
        n = len(self.fu)
        top, bot = self.quarter == 0, self.quarter == 3
        self.PT = []
        for h in self.halves:
            mats = []
            for mask in (h, ~h):
                for reg in (top, bot):
                    idx = np.flatnonzero(mask & reg)
                    M = sp.csr_matrix((np.ones(len(idx)), (self.fu[idx], idx)), shape=(self.nf, n))
                    cnt = np.asarray(M.sum(axis=1)).ravel()
                    mats.append((M, cnt))
            self.PT.append(mats)            # [A-top, A-bot, B-top, B-bot]

    def page_turn_terms(self, R, pairs=None):
        """Per-pair terms d = b_first * top_second - top_first * b_second (pairs x B; default: the reading-order
        transitions), averaged over halvings and the A/B swap; top and bottom means centred within stratum (pages
        with no occurrences in a region contribute 0 after centring)."""
        pairs = self.T if pairs is None else pairs
        Bn = R.shape[1]
        acc = np.zeros((len(pairs), Bn))
        st = self.A.page_stratum
        for mats in self.PT:
            vals = []
            for M, cnt in mats:
                S = M @ R
                mean = np.where(cnt[:, None] > 0, S / np.maximum(cnt, 1)[:, None], np.nan)
                # centre within stratum over pages with data
                for s in np.unique(st):
                    rows = st == s
                    mu = np.nanmean(mean[rows], axis=0) if np.isfinite(mean[rows]).any() else 0.0
                    mean[rows] = mean[rows] - mu
                vals.append(np.nan_to_num(mean))
            At, Ab, Bt, Bb = vals
            a, b = pairs[:, 0], pairs[:, 1]
            acc += (Ab[a] * Bt[b] - At[a] * Bb[b]) + (Bb[a] * At[b] - Bt[a] * Ab[b])
        return acc / (2 * len(self.PT))

    def page_turn_test(self, R, nflip=2000, seed=7701, by='transition', subset=None):
        d = self.page_turn_terms(R)
        if subset is not None:
            d = d[subset]
        K = d.sum(axis=0)
        rng = np.random.default_rng(seed)
        if by == 'transition':
            S = rng.choice([-1.0, 1.0], size=(nflip, d.shape[0]))
            null = S @ d
        else:
            ch = self.T_chain if subset is None else self.T_chain[subset]
            u, inv = np.unique(ch, return_inverse=True)
            dc = np.zeros((len(u), d.shape[1]))
            np.add.at(dc, inv.ravel(), d)
            S = rng.choice([-1.0, 1.0], size=(nflip, len(u)))
            null = S @ dc
        p = (1 + (null >= K[None, :]).sum(axis=0)) / (1 + nflip)
        return K, p


# ------------------------------------------------------------------------------------------------ A3: paragraph order
class ParaOrder:
    """D = mean cross-frame product of paragraph body means for adjacent paragraphs minus that for paragraphs >= 2
    apart (pair weight: the smaller half-count; halves with < 2 occurrences dropped; folios with >= 3 usable
    paragraphs). Body lines only; first and last 2 lines of each page excluded; residuals centred within stratum x
    position decile. Null: paragraph order permuted within folio."""

    def __init__(self, St: Stats, nperm=2000, seed=7702):
        A, O = St.A, St.A.O
        m = St.m
        body = ~(O['par_first'][m] | O['par_last'][m] | O['page_edge'][m])
        self.body = body
        dec = np.minimum(9, (O['relpos'][m] * 10).astype(int))
        self.group = (St.stratum * 10 + dec)[body]
        self.par = O['par'][m][body]
        self.fu = St.fu[body]
        self.halves = [h[body] for h in St.halves]
        # paragraph order within folio
        pidx = O['par_idx'][m][body]
        self.par_pos = {}
        for p, f, j in zip(self.par, self.fu, pidx):
            self.par_pos[p] = (f, j)
        self.nperm, self.seed = nperm, seed

    def stat_and_p(self, R):
        """R: (n_inf x B). Returns D (B,), p (B,) one-sided (D > 0)."""
        Rb = group_center(R[self.body], self.group)
        pars = np.unique(self.par)
        pid = {p: i for i, p in enumerate(pars)}
        pi = np.array([pid[p] for p in self.par])
        nP, Bn = len(pars), R.shape[1]
        SWP = defaultdict(lambda: np.zeros(Bn))
        SW = defaultdict(float)
        for h in self.halves:
            for mA in (h, ~h):
                mB = ~mA
                sA = np.zeros((nP, Bn))
                np.add.at(sA, pi[mA], Rb[mA])
                sB = np.zeros((nP, Bn))
                np.add.at(sB, pi[mB], Rb[mB])
                nA = np.bincount(pi[mA], minlength=nP)
                nB = np.bincount(pi[mB], minlength=nP)
                mA_ = sA / np.maximum(nA, 1)[:, None]
                mB_ = sB / np.maximum(nB, 1)[:, None]
                by_f = defaultdict(list)
                for p in pars:
                    by_f[self.par_pos[p][0]].append(pid[p])
                for f, ids in by_f.items():
                    for i in ids:
                        if nA[i] < 2:
                            continue
                        for j in ids:
                            if i == j or nB[j] < 2:
                                continue
                            w = min(nA[i], nB[j])
                            SWP[(i, j)] += w * mA_[i] * mB_[j]
                            SW[(i, j)] += w
        # per folio pair arrays
        by_f = defaultdict(list)
        for (i, j) in SW:
            by_f[self.par_pos[pars[i]][0]].append((i, j))
        rng = np.random.default_rng(self.seed)
        obs_num = {'adj': np.zeros(Bn), 'far': np.zeros(Bn)}
        obs_den = {'adj': 0.0, 'far': 0.0}
        null_num = {'adj': np.zeros((self.nperm, Bn)), 'far': np.zeros((self.nperm, Bn))}
        null_den = {'adj': np.zeros(self.nperm), 'far': np.zeros(self.nperm)}
        for f, pairs in by_f.items():
            ids = sorted({i for i, _ in pairs} | {j for _, j in pairs})
            if len(ids) < 3:
                continue
            pos = np.array([self.par_pos[pars[i]][1] for i in ids])
            loc = {i: k for k, i in enumerate(ids)}
            I = np.array([loc[i] for i, _ in pairs])
            J = np.array([loc[j] for _, j in pairs])
            P = np.stack([SWP[pr] for pr in pairs])            # (npairs x B)
            W = np.array([SW[pr] for pr in pairs])
            gap = np.abs(pos[I] - pos[J])
            for key, sel in (('adj', gap == 1), ('far', gap >= 2)):
                obs_num[key] += P[sel].sum(axis=0)
                obs_den[key] += W[sel].sum()
            perms = np.argsort(rng.random((self.nperm, len(ids))), axis=1)   # new position of each paragraph
            g = np.abs(perms[:, I] - perms[:, J])
            for key, sel in (('adj', g == 1), ('far', g >= 2)):
                null_num[key] += sel.astype(float) @ P
                null_den[key] += sel.astype(float) @ W
        D = obs_num['adj'] / max(obs_den['adj'], 1e-12) - obs_num['far'] / max(obs_den['far'], 1e-12)
        Dn = null_num['adj'] / np.maximum(null_den['adj'], 1e-12)[:, None] - \
            null_num['far'] / np.maximum(null_den['far'], 1e-12)[:, None]
        p = (1 + (Dn >= D[None, :]).sum(axis=0)) / (1 + self.nperm)
        return D, p
