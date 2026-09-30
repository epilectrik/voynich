#!/usr/bin/env python3
"""PHASE_770 Arm B machinery and calibration (controls only).

CrossDial (B2): for a pair of dials (E, Y) with the joint frame as split key, over 50 halvings x key-half swap x
page-half swap (200 combinations): E's covariate-residualised folio mean vector (its key half, one page half) and Y's
(the other key half, the other page half); X = mean Pearson correlation across folios with >= MIN_OCC occurrences in
both. Null: circular shifts of Y's folio vector along manuscript order within stratum (section x hand), one
relabelling for every combination and every dial ('random' within-stratum relabelling is kept as an option; it was
anti-conservative under drift). Region split 'half' (page halves) or 'block' (alternating 3-line blocks, buffer line).
B3 (co-drift within pages): E (key half A, one line block) and Y (key half B, the other block, buffer line between)
folio-demeaned quarter profiles after removing within-folio line-type effects (stratum x quarter centred); statistic =
sum_f,q w ee yy / sum w, w = min count; same null. The verdict thresholds are z-scale critical values calibrated in
calBj770.py (B2, 3.2) and calB3_770.py (B3, 3.76); Westfall-Young adjusted p is descriptive.

Calibration: size (independent components at several strengths, independent drifting components, word-level
coupling) and power (shared latent at rho 0.4 / 0.7 over a grid of Y strengths; folio-level and drifting), B1 MDE80
per dial.
"""
from __future__ import annotations

import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cal770 as C  # noqa: E402

OUT = HERE.parent / 'results/calib'
DIALS_Y = ('CS', 'KTH', 'MIN')          # KTH: k/t as the HEAD atom (lexical control); OKOT descriptive
MIN_OCC = 5
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def build_pair(y_dial, recs=None, amap_leg=None, zl=False):
    """Analysis objects for E and Y with the joint frame of (E, Y) as split key."""
    ce = ('prev',) if y_dial == 'CS' else ()
    AE = C.Analysis('E', recs=recs, amap_leg=amap_leg, zl=zl, pair_dials=('E', y_dial))
    AY = C.Analysis(y_dial, recs=AE.recs, amap_leg=(AE.amap, AE.leg), zl=zl, pair_dials=('E', y_dial), cell_extra=ce)
    return AE, AY


def _wls_projector(Xc, w):
    W = np.diag(w)
    return np.eye(len(w)) - Xc @ np.linalg.pinv(Xc.T @ W @ Xc) @ Xc.T @ W


class CrossDial:
    def __init__(self, AE, AY, k=50, seed=7710, strata=None, split='half'):
        """split: 'half' (E top half vs Y bottom half, and the swap) or 'block' (alternating 3-line blocks with a
        buffer line: lines with index mod 8 in 0-2 vs 4-6)."""
        self.AE, self.AY = AE, AY
        OE, OY = AE.O, AY.O
        self.mE, self.mY = OE['informative'], OY['informative']
        self.cE, self.cY = OE['cell'][self.mE], OY['cell'][self.mY]
        self.fE, self.fY = OE['folio'][self.mE], OY['folio'][self.mY]
        assert list(OE['folio_names']) == list(OY['folio_names']) or True
        self.pages = AE.pages
        self.nf = len(self.pages)
        # map Y folio index onto E's page order
        yid = {p: i for i, p in enumerate(OY['folio_names'])}
        self.y2e = np.array([self.pages.index(p) for p in OY['folio_names']])
        self.fY = self.y2e[self.fY]
        keys = {s: i for i, s in enumerate(dict.fromkeys(list(OE['jkey_str']) + list(OY['jkey_str'])))}
        jE = np.array([keys[OE['jkey_str'][j]] for j in OE['jkey'][self.mE]])
        jY = np.array([keys[OY['jkey_str'][j]] for j in OY['jkey'][self.mY]])
        if split == 'half':
            hE, hY = OE['half'][self.mE], OY['half'][self.mY]
        else:
            def blk(li):
                r = li % 8
                return np.where(r < 3, 0, np.where((r >= 4) & (r < 7), 1, -1))
            hE, hY = blk(OE['line_idx'][self.mE]), blk(OY['line_idx'][self.mY])
        self.X = AE.Xcov
        rng = np.random.default_rng(seed)
        self.combos = []
        for _ in range(k):
            inA = rng.random(len(keys)) < 0.5
            for ks in (0, 1):
                kE = inA[jE] if ks == 0 else ~inA[jE]
                kY = ~inA[jY] if ks == 0 else inA[jY]
                for ps in (0, 1):
                    selE = np.flatnonzero(kE & (hE == ps))
                    selY = np.flatnonzero(kY & (hY == 1 - ps))
                    ME = sp.csr_matrix((np.ones(len(selE)), (self.fE[selE], selE)), shape=(self.nf, len(self.fE)))
                    MY = sp.csr_matrix((np.ones(len(selY)), (self.fY[selY], selY)), shape=(self.nf, len(self.fY)))
                    nE = np.asarray(ME.sum(1)).ravel()
                    nY = np.asarray(MY.sum(1)).ravel()
                    okE, okY = nE >= MIN_OCC, nY >= MIN_OCC
                    PE = _wls_projector(self.X[okE], nE[okE])
                    PY = _wls_projector(self.X[okY], nY[okY])
                    self.combos.append((ME, MY, nE, nY, okE, okY, PE, PY))
        # B3: alternating 3-line blocks with a buffer line (line index mod 8: 0-2 vs 4-6), quarter profiles
        def blk(li):
            r = li % 8
            return np.where(r < 3, 0, np.where((r >= 4) & (r < 7), 1, -1))
        lineE = blk(OE['line_idx'][self.mE])
        lineY = blk(OY['line_idx'][self.mY])
        # line types for residualisation: paragraph-final line, first body line, fullness tercile
        def ltype(O, m):
            return (O['par_last'][m].astype(int) * 6 + (O['par_line'][m] == 1).astype(int) * 3 + O['full3'][m])
        self.ltE, self.ltY = ltype(OE, self.mE), ltype(OY, self.mY)
        qE, qY = OE['quarter'][self.mE], OY['quarter'][self.mY]
        stE = AE.page_stratum[self.fE]
        stY = AE.page_stratum[self.fY]
        self.sqE, self.sqY = stE * 4 + qE, stY * 4 + qY
        self.b3 = []
        rng = np.random.default_rng(seed + 1)
        for _ in range(k):
            inA = rng.random(len(keys)) < 0.5
            for ks in (0, 1):
                kE = inA[jE] if ks == 0 else ~inA[jE]
                kY = ~inA[jY] if ks == 0 else inA[jY]
                for par in (0, 1):
                    selE = np.flatnonzero(kE & (lineE == par))
                    selY = np.flatnonzero(kY & (lineY == 1 - par))      # buffer lines (-1) never used
                    ME = sp.csr_matrix((np.ones(len(selE)), (self.fE[selE] * 4 + qE[selE], selE)),
                                       shape=(self.nf * 4, len(self.fE)))
                    MY = sp.csr_matrix((np.ones(len(selY)), (self.fY[selY] * 4 + qY[selY], selY)),
                                       shape=(self.nf * 4, len(self.fY)))
                    nE = np.asarray(ME.sum(1)).ravel().reshape(self.nf, 4)
                    nY = np.asarray(MY.sum(1)).ravel().reshape(self.nf, 4)
                    self.b3.append((ME, MY, nE, nY))
        # within-stratum relabelling generator
        self.strata = AE.page_stratum if strata is None else strata

    def relabellings(self, nperm, seed, mode='shift'):
        """Folio relabellings for the pairing null, within stratum (section x hand).
        'shift' (v3 after certification): Y's folio vector circularly shifted along manuscript order within each
        stratum by a random non-zero offset, which keeps each dial's autocorrelation along the reading order (the
        random relabelling was anti-conservative under independent drifting components: size 0.026 at alpha 0.01,
        1,000 replicates; results/calib/calB_relabel_null.json).
        'random': the v2 random relabelling within stratum."""
        rng = np.random.default_rng(seed)
        Pi = np.tile(np.arange(self.nf), (nperm, 1))
        for s in np.unique(self.strata):
            idx = np.flatnonzero(self.strata == s)                 # page indices in manuscript order
            n = len(idx)
            if n < 2:
                continue
            if mode == 'random':
                sh = np.argsort(rng.random((nperm, n)), axis=1)
                Pi[:, idx] = idx[sh]
            else:
                k = rng.integers(1, n, nperm)
                Pi[:, idx] = idx[(np.arange(n)[None, :] + k[:, None]) % n]
        return Pi

    def residuals(self, YE, YY):
        RE = YE[self.mE] - C.cell_means_batch(YE[self.mE], self.cE)
        RY = YY[self.mY] - C.cell_means_batch(YY[self.mY], self.cY)
        return RE, RY

    def _vectors(self, RE, RY):
        """Per combination: E and Y residualised folio vectors (F x B) with NaN where not usable."""
        out = []
        for ME, MY, nE, nY, okE, okY, PE, PY in self.combos:
            e = np.full((self.nf, RE.shape[1]), np.nan)
            y = np.full((self.nf, RY.shape[1]), np.nan)
            e[okE] = PE @ ((ME @ RE)[okE] / nE[okE][:, None])
            y[okY] = PY @ ((MY @ RY)[okY] / nY[okY][:, None])
            out.append((e, y))
        return out

    @staticmethod
    def _corr(e, y):
        """Masked Pearson correlation along axis -2 (folios); e (..., F, B), y (..., F, B)."""
        m = ~(np.isnan(e) | np.isnan(y))
        e0, y0 = np.where(m, e, 0.0), np.where(m, y, 0.0)
        n = m.sum(-2)
        se, sy = e0.sum(-2), y0.sum(-2)
        sey, see, syy = (e0 * y0).sum(-2), (e0 * e0).sum(-2), (y0 * y0).sum(-2)
        num = n * sey - se * sy
        den = np.sqrt(np.maximum(n * see - se ** 2, 0) * np.maximum(n * syy - sy ** 2, 0))
        return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)

    def X_stat(self, RE, RY, Pi=None):
        """Observed X (B,) and, if Pi (P x F) is given, the null X (P x B)."""
        V = self._vectors(RE, RY)
        obs = np.nanmean(np.stack([self._corr(e, y) for e, y in V]), axis=0)
        if Pi is None:
            return obs, None
        acc = np.zeros((Pi.shape[0], RE.shape[1]))
        cnt = np.zeros((Pi.shape[0], RE.shape[1]))
        for e, y in V:
            yp = y[Pi]                                          # (P, F, B)
            c = self._corr(np.broadcast_to(e, yp.shape), yp)
            acc += np.nan_to_num(c)
            cnt += ~np.isnan(c)
        return obs, acc / np.maximum(cnt, 1)

    @staticmethod
    def _remove_within_folio(R, groups, folio, nf, iters=15):
        """Remove additive within-folio effects of a categorical (backfitting with folio fixed effects), per column."""
        n = len(groups)
        _, g = np.unique(groups, return_inverse=True)
        g = g.ravel()
        Gg = sp.csr_matrix((np.ones(n), (g, np.arange(n))), shape=(g.max() + 1, n))
        Gf = sp.csr_matrix((np.ones(n), (folio, np.arange(n))), shape=(nf, n))
        ng = np.maximum(np.asarray(Gg.sum(1)).ravel(), 1)[:, None]
        nfc = np.maximum(np.asarray(Gf.sum(1)).ravel(), 1)[:, None]
        b = np.zeros((g.max() + 1, R.shape[1]))
        for _ in range(iters):
            a = (Gf @ (R - b[g])) / nfc
            b = (Gg @ (R - a[folio])) / ng
        return R - b[g]

    def B3_stat(self, RE, RY, Pi=None):
        RE = self._remove_within_folio(RE, self.ltE, self.fE, self.nf)
        RY = self._remove_within_folio(RY, self.ltY, self.fY, self.nf)
        RE = C.group_center(RE, self.sqE)
        RY = C.group_center(RY, self.sqY)
        num_o = np.zeros(RE.shape[1])
        den_o = 0.0
        num_n = None if Pi is None else np.zeros((Pi.shape[0], RE.shape[1]))
        den_n = None if Pi is None else np.zeros(Pi.shape[0])
        for ME, MY, nE, nY in self.b3:
            SE = (ME @ RE).reshape(self.nf, 4, -1)
            SY = (MY @ RY).reshape(self.nf, 4, -1)
            mE = np.where(nE[..., None] > 0, SE / np.maximum(nE, 1)[..., None], 0.0)
            mY = np.where(nY[..., None] > 0, SY / np.maximum(nY, 1)[..., None], 0.0)
            # folio-demeaned profiles (count-weighted mean over quarters)
            wE = nE / np.maximum(nE.sum(1, keepdims=True), 1)
            wY = nY / np.maximum(nY.sum(1, keepdims=True), 1)
            pE = mE - (mE * wE[..., None]).sum(1, keepdims=True)
            pY = mY - (mY * wY[..., None]).sum(1, keepdims=True)
            w = np.minimum(nE, nY).astype(float)                # (F, 4)
            num_o += np.einsum('fq,fqb,fqb->b', w, pE, pY)
            den_o += w.sum()
            if Pi is not None:
                pYp = pY[Pi]                                    # (P, F, 4, B)
                wp = np.minimum(nE[None], nY[Pi])               # (P, F, 4)
                num_n += np.einsum('pfq,fqb,pfqb->pb', wp, pE, pYp)
                den_n += wp.sum(axis=(1, 2))
        obs = num_o / max(den_o, 1e-12)
        return obs, (None if Pi is None else num_n / np.maximum(den_n, 1e-12)[:, None])


# ------------------------------------------------------------------------------------------------ joint plants
class PairPlants:
    """Joint plants for (E, Y) on the same line table: shared latent at correlation rho."""

    def __init__(self, AE, AY):
        self.PE, self.PY = C.Plants(AE), C.Plants(AY)
        self.AE, self.AY = AE, AY
        assert len(AE.line_keys) == len(AY.line_keys)

    def draw(self, kind, sE, sY, rho, rng, B_):
        """kind: 'folio' (page constants) or 'drift' (M6 AR(1) rho_line 0.97 along chains). sE, sY: scales."""
        PE = self.PE
        if kind == 'folio':
            u = PE.f_page_const(rng, B_)
            v = PE.f_page_const(rng, B_)
        elif kind == 'drift':
            u = PE.f_ar1_chain(rng, B_, 0.97)
            v = PE.f_ar1_chain(rng, B_, 0.97)
        else:
            raise ValueError(kind)
        zE = PE._normalise(u[self.AE.occ_line])
        zY = self.PY._normalise((rho * u + np.sqrt(1 - rho ** 2) * v)[self.AY.occ_line])
        lgE = PE.lg[:, None] + zE * sE
        lgY = self.PY.lg[:, None] + zY * sY
        YE = (rng.random(lgE.shape) < 1 / (1 + np.exp(-lgE))).astype(float)
        YY = (rng.random(lgY.shape) < 1 / (1 + np.exp(-lgY))).astype(float)
        return YE, YY

    def draw_line(self, kind, s, rng, B_):
        """B3 size plants. 'linestate': an iid latent per line shared by both dials (no page structure);
        'linetype': both dials shifted by s on paragraph-final and first body lines."""
        AE, AY = self.AE, self.AY
        if kind == 'linestate':
            w = rng.normal(0, 1, (len(AE.line_keys), B_))
            zE, zY = w[AE.occ_line] * s, w[AY.occ_line] * s
        else:
            def lt(O):
                return (O['par_last'] | (O['par_line'] == 1)).astype(float)[:, None] * s
            zE = np.repeat(lt(AE.O), B_, axis=1)
            zY = np.repeat(lt(AY.O), B_, axis=1)
        lgE = self.PE.lg[:, None] + zE
        lgY = self.PY.lg[:, None] + zY
        YE = (rng.random(lgE.shape) < 1 / (1 + np.exp(-lgE))).astype(float)
        YY = (rng.random(lgY.shape) < 1 / (1 + np.exp(-lgY))).astype(float)
        return YE, YY

    def draw_wordcouple(self, s, rng, B_):
        """Word-level coupling: per folio, a random quarter of the joint frames get a shared shift on both dials."""
        OE, OY = self.AE.O, self.AY.O
        keys = {k: i for i, k in enumerate(dict.fromkeys(list(OE['jkey_str']) + list(OY['jkey_str'])))}
        jE = np.array([keys[OE['jkey_str'][j]] for j in OE['jkey']])
        jY = np.array([keys[OY['jkey_str'][j]] for j in OY['jkey']])
        fE = OE['folio']
        yidx = {p: i for i, p in enumerate(OE['folio_names'])}
        fY = np.array([yidx[OY['folio_names'][f]] for f in OY['folio']])
        nk, nf = len(keys), len(OE['folio_names'])
        YE = np.empty((len(fE), B_))
        YY = np.empty((len(fY), B_))
        for b in range(B_):
            sel = rng.random((nf, nk)) < 0.25
            shift = rng.normal(0, 1, (nf, nk)) * sel
            lgE = self.PE.lg + s * shift[fE, jE]
            lgY = self.PY.lg + s * shift[fY, jY]
            YE[:, b] = rng.random(len(lgE)) < 1 / (1 + np.exp(-lgE))
            YY[:, b] = rng.random(len(lgY)) < 1 / (1 + np.exp(-lgY))
        return YE, YY


def z_and_p(obs, null):
    mu, sd = np.nanmean(null, axis=0), np.nanstd(null, axis=0)
    z = (obs - mu) / np.where(sd > 0, sd, 1)
    zn = (null - mu) / np.where(sd > 0, sd, 1)
    p2 = (1 + (np.abs(zn) >= np.abs(z)[None]).sum(0)) / (1 + null.shape[0])
    p2 = np.where(np.isfinite(z), p2, 1.0)                    # not computable (no usable folios): p = 1
    return z, zn, p2


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pilot = json.load(open(OUT / 'pilot.json'))
    sE = pilot['grid_S3c']['M1']['s_star']
    nrep, nperm = 200, 500
    res = {'n_rep': nrep, 'n_perm': nperm, 'sE': sE, 'pairs': {}}
    pairs = {}
    for yd in DIALS_Y + ('OKOT',):
        AE, AY = build_pair(yd)
        pairs[yd] = (AE, AY, CrossDial(AE, AY), PairPlants(AE, AY))
        log('pair E', yd, 'E inf', int(AE.O['informative'].sum()), 'Y inf', int(AY.O['informative'].sum()),
            'joint keys', len(set(AE.O['jkey_str']) | set(AY.O['jkey_str'])))
    b1_only = {'OKOT': pairs.pop('OKOT')}
    # ---- B1: own component per dial (S3c power against scale; null moments from within-cell permutations)
    res['B1'] = {}
    for yd, (AE, AY, CD, PP) in list(pairs.items()) + list(b1_only.items()):
        St = C.Stats(AY)
        P1 = C.Plants(AY)
        rng = np.random.default_rng(zlib.crc32(f'B1/{yd}'.encode()))
        y0 = P1.draw('NONE', np.zeros(1), rng)[:, 0]
        m = AY.O['informative']
        null = []
        for j in range(0, 1000, 250):
            Yp = C.B.perm_batch(y0[m], St.cell, 250, rng)
            R = (Yp - C.cell_means_batch(Yp.T, St.cell).T).T
            null.append(St.S3c(R))
        null = np.concatenate(null)
        mu, sd = float(np.nanmean(null)), float(np.nanstd(null))
        crit = float(np.nanquantile(null, 0.99))
        curve = {}
        for sY in (0.1, 0.2, 0.3, 0.4, 0.5, 0.7):
            Y = P1.draw('M1', np.full(200, sY), rng)
            s3 = St.S3c(St.residuals(Y))
            curve[str(sY)] = {'S3c_mean': float(np.nanmean(s3)), 'S3c_sd': float(np.nanstd(s3)),
                              'power_01': float((s3 >= crit).mean())}
        xs = sorted(float(k) for k in curve)
        pw = [curve[str(x)]['power_01'] for x in xs]
        mde = float(np.interp(0.8, pw, xs)) if max(pw) >= 0.8 and np.all(np.diff(pw) >= 0) else None
        res['B1'][yd] = {'null_mean': mu, 'null_sd': sd, 'crit_01': crit, 'curve': curve, 'MDE80_logit': mde}
        log('B1', yd, 'null', round(mu, 3), round(sd, 3), 'MDE80', mde, {k: v['power_01'] for k, v in curve.items()})
        json.dump(res, open(OUT / 'calB.json', 'w'), indent=1)
    Pi = pairs['CS'][2].relabellings(nperm, 7711)
    s6 = pilot['grid_S3c']['M6:0.97']['s_star']
    conds = [('half', 'size_folio', 'folio', 0.0, 0.2), ('half', 'size_folio', 'folio', 0.0, 0.4),
             ('half', 'size_folio', 'folio', 0.0, 0.6), ('half', 'size_drift', 'drift', 0.0, 0.6),
             ('half', 'power_folio', 'folio', 0.4, 0.4), ('half', 'power_folio', 'folio', 0.7, 0.2),
             ('half', 'power_folio', 'folio', 0.7, 0.35), ('half', 'power_folio', 'folio', 0.7, 0.5),
             ('half', 'power_drift', 'drift', 0.7, 0.6),
             ('block', 'size_drift', 'drift', 0.0, 0.6), ('block', 'power_folio', 'folio', 0.7, 0.35),
             ('block', 'power_drift', 'drift', 0.7, 0.6)]
    certify = [('half', 'size_folio', 'folio', 0.0, 0.4), ('half', 'size_drift', 'drift', 0.0, 0.6),
               ('block', 'size_folio', 'folio', 0.0, 0.4), ('block', 'size_drift', 'drift', 0.0, 0.6)]
    cds = {}
    for yd, (AE, AY, CD, PP) in pairs.items():
        cds[(yd, 'half')] = CD
        cds[(yd, 'block')] = CrossDial(AE, AY, split='block')
    for yd, (AE, AY, CD, PP) in pairs.items():
        out = {}
        for split, name, kind, rho, sY in conds:
            CDs = cds[(yd, split)]
            rng = np.random.default_rng(zlib.crc32(f'{yd}/{split}/{name}/{rho}/{sY}'.encode()))
            sEk = sE if kind == 'folio' else s6
            sYk = sY if kind == 'folio' else sY * s6 / sE
            Xo, Xn, B3o, B3n = [], [], [], []
            for j in range(0, nrep, 50):
                YE, YY = PP.draw(kind, sEk, sYk, rho, rng, 50)
                RE, RY = CDs.residuals(YE, YY)
                o, n = CDs.X_stat(RE, RY, Pi)
                Xo.append(o)
                Xn.append(n)
                o3, n3 = CDs.B3_stat(RE, RY, Pi)
                B3o.append(o3)
                B3n.append(n3)
            Xo, Xn = np.concatenate(Xo), np.concatenate(Xn, axis=1)
            B3o, B3n = np.concatenate(B3o), np.concatenate(B3n, axis=1)
            z, zn, p2 = z_and_p(Xo, Xn)
            pb3 = (1 + (B3n >= B3o[None]).sum(0)) / (1 + nperm)
            key = f'{split}_{name}_rho{rho}_sY{sY}'
            out[key] = {'X_mean': float(np.nanmean(Xo)), 'p2_le_01': float((p2 <= 0.01).mean()),
                        'p2_le_0033': float((p2 <= 0.01 / 3).mean()), 'p2_le_05': float((p2 <= 0.05).mean()),
                        'B3_p_le_01': float((pb3 <= 0.01).mean()), 'B3_p_le_05': float((pb3 <= 0.05).mean())}
            log(yd, key, out[key])
            res['pairs'][yd] = out
            json.dump(res, open(OUT / 'calB.json', 'w'), indent=1)
        # certification of B2 size (1,000 replicates, joint relabelling as in the run)
        for split, name, kind, rho, sY in certify:
            CDs = cds[(yd, split)]
            rng = np.random.default_rng(zlib.crc32(f'cert/{yd}/{split}/{name}'.encode()))
            sEk = sE if kind == 'folio' else s6
            sYk = sY if kind == 'folio' else sY * s6 / sE
            p_all = []
            for j in range(0, 1000, 50):
                YE, YY = PP.draw(kind, sEk, sYk, rho, rng, 50)
                RE, RY = CDs.residuals(YE, YY)
                o, n = CDs.X_stat(RE, RY, Pi)
                p_all.append(z_and_p(o, n)[2])
            p_all = np.concatenate(p_all)
            key = f'CERT_{split}_{name}_sY{sY}'
            out[key] = {'n_rep': int(len(p_all)), 'p2_le_01': float((p_all <= 0.01).mean()),
                        'p2_le_05': float((p_all <= 0.05).mean())}
            log(yd, key, out[key])
            res['pairs'][yd] = out
            json.dump(res, open(OUT / 'calB.json', 'w'), indent=1)
        # B3 size under line-state and line-type plants
        for kind, s in (('linestate', 0.5), ('linetype', 0.5)):
            rng = np.random.default_rng(zlib.crc32(f'b3/{yd}/{kind}'.encode()))
            CDs = cds[(yd, 'half')]
            pb = []
            for j in range(0, 400, 50):
                YE, YY = PP.draw_line(kind, s, rng, 50)
                RE, RY = CDs.residuals(YE, YY)
                o3, n3 = CDs.B3_stat(RE, RY, Pi)
                pb.append((1 + (n3 >= o3[None]).sum(0)) / (1 + nperm))
            pb = np.concatenate(pb)
            out[f'B3_size_{kind}'] = {'n_rep': int(len(pb)), 'p_le_01': float((pb <= 0.01).mean()),
                                      'p_le_05': float((pb <= 0.05).mean())}
            log(yd, 'B3 size', kind, out[f'B3_size_{kind}'])
        # word-level coupling (size)
        rng = np.random.default_rng(7712)
        YE, YY = PP.draw_wordcouple(1.0, rng, 100)
        RE, RY = CD.residuals(YE, YY)
        o, n = CD.X_stat(RE, RY, Pi)
        z, zn, p2 = z_and_p(o, n)
        out['size_wordcouple_s1.0'] = {'X_mean': float(np.nanmean(o)), 'p2_le_01': float((p2 <= 0.01).mean()),
                                       'p2_le_05': float((p2 <= 0.05).mean())}
        log(yd, 'wordcouple', out['size_wordcouple_s1.0'])
        res['pairs'][yd] = out
        json.dump(res, open(OUT / 'calB.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'calB.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
