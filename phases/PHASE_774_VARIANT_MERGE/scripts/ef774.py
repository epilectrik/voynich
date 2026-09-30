"""PHASE_774 exact edge-frame null (EF) and repeat statistics.

EF: within each folio, tokens are permuted among positions that share a cell = (zone, edge signature of the token).
Zone is line-initial / medial / line-final (a one-token line counts as initial). The edge signature is the token's
first and last glyph units (and optionally its last two). Uncertain-token blockers stay fixed.

What EF preserves exactly: each folio's token multiset; the edge signature at every position, and so every
last-glyph -> first-glyph junction pair (C1212/C1563) in every line; line-initial and line-final signatures; line
lengths and blocker positions. What it destroys: which token (among those with the same edges, in the same folio and
zone) sits where, and with it any order carried by the token interiors (MIDDLEs).

Sampling is exact (independent uniform permutations within cells); there is no chain and nothing to converge.

Statistic RPT_n(rep): the number of windows of n consecutive certain tokens within one line whose rep-sequence occurs
at least twice in the corpus; RPTi_n: the same restricted to interior windows (no line-initial or line-final token);
RPTx_n: restricted to sequences that occur in two or more folios; DIST_n: the number of distinct repeated sequences.
"""
from __future__ import annotations

import re

import numpy as np

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')


def sig_fl(w):
    g = GLYPH_RE.findall(w)
    return (g[0], g[-1])


def sig_fl2(w):
    g = GLYPH_RE.findall(w)
    return (g[0], tuple(g[-2:]))


class Corpus:
    """Flat position arrays for one corpus in B's skeleton."""

    def __init__(self, lines, folios, sig=sig_fl, ns=(3, 4)):
        self.ns = ns
        vocab = sorted({w for ln in lines for w in ln if w is not None})
        self.vocab = vocab
        vid = {w: i for i, w in enumerate(vocab)}
        tok, line_of, fol_of, zone = [], [], [], []
        fid = {f: i for i, f in enumerate(dict.fromkeys(folios))}
        for li, (ln, f) in enumerate(zip(lines, folios)):
            L = len(ln)
            for p, w in enumerate(ln):
                tok.append(-1 if w is None else vid[w])
                line_of.append(li)
                fol_of.append(fid[f])
                zone.append(0 if p == 0 else (2 if p == L - 1 else 1))
        self.tok = np.array(tok, dtype=np.int64)
        self.line_of = np.array(line_of, dtype=np.int64)
        self.fol_of = np.array(fol_of, dtype=np.int64)
        self.zone = np.array(zone, dtype=np.int64)
        n = len(tok)
        # cells
        sig_id = {}
        vsig = np.array([sig_id.setdefault(sig(w), len(sig_id)) for w in vocab], dtype=np.int64)
        cell_key = {}
        cell = np.full(n, -1, dtype=np.int64)
        for p in range(n):
            if self.tok[p] >= 0:
                k = (int(self.fol_of[p]), int(self.zone[p]), int(vsig[self.tok[p]]))
                cell[p] = cell_key.setdefault(k, len(cell_key))
        self.cell = cell
        self.n_cells = len(cell_key)
        movable = cell >= 0
        self.mpos = np.flatnonzero(movable)
        self.P = self.mpos[np.argsort(cell[self.mpos], kind='stable')]
        cs = np.bincount(cell[self.mpos], minlength=len(cell_key))
        self.cell_sizes = cs
        self.frac_movable = float(cs[cs >= 2].sum() / max(1, movable.sum()))
        # windows
        blk = self.tok < 0
        self.win = {}
        self.interior = {}
        for nn in ns:
            st = np.arange(n - nn + 1)
            ok = self.line_of[st] == self.line_of[st + nn - 1]
            for k in range(nn):
                ok &= ~blk[st + k]
            self.win[nn] = st[ok]
            inter = np.ones(len(self.win[nn]), dtype=bool)
            for k in range(nn):
                inter &= self.zone[self.win[nn] + k] == 1       # no line-initial or line-final token in the window
            self.interior[nn] = inter

    def sample(self, rng):
        key = rng.random(len(self.mpos))
        Q = self.mpos[np.lexsort((key, self.cell[self.mpos]))]
        out = self.tok.copy()
        out[self.P] = self.tok[Q]
        return out

    def rep_array(self, fn):
        ids = {}
        return np.array([ids.setdefault(fn(w), len(ids)) for w in self.vocab], dtype=np.int64)


RARE_K = (20, 50)


def rare_masks(C, rep):
    """Per rep: for each K, a symbol-level mask 'not among the K most frequent symbols' (EF preserves every rep's
    marginal, so the masks are the same for the data and every null sample)."""
    sym = rep[C.tok[C.tok >= 0]]
    cnt = np.bincount(sym, minlength=int(rep.max()) + 1)
    order = np.argsort(-cnt, kind='stable')
    out = {}
    for K in RARE_K:
        m = np.ones(len(cnt), dtype=bool)
        m[order[:K]] = False
        out[K] = m
    return out


def repeat_counts(C, tok, rep, masks=None):
    """{stat name: value} for one token arrangement and one representation.
    RPTn: windows of n whose sequence occurs >= 2 times; RPTxn: ... in >= 2 folios; DISTn: distinct repeated
    sequences; RPTn_rK: repeated windows with >= 2 symbols outside the K most frequent."""
    sym = rep[np.where(tok >= 0, tok, 0)]
    S = int(rep.max()) + 1
    out = {}
    for nn in C.ns:
        w = C.win[nn]
        key = sym[w]
        for k in range(1, nn):                     # re-index after every step, so keys never overflow
            key = np.unique(key * S + sym[w + k], return_inverse=True)[1].ravel().astype(np.int64)
        _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        inv = inv.ravel()
        rep_occ = cnt[inv] >= 2
        fol = C.fol_of[w]
        pair = np.unique(inv * 4096 + fol)
        nfol = np.bincount(pair // 4096, minlength=len(cnt))
        cross = rep_occ & (nfol[inv] >= 2)
        out[f'RPT{nn}'] = int(rep_occ.sum())
        out[f'RPTi{nn}'] = int((rep_occ & C.interior[nn]).sum())
        out[f'RPTx{nn}'] = int(cross.sum())
        out[f'DIST{nn}'] = int((cnt >= 2).sum())
        if masks is not None:
            for K, m in masks.items():
                nr = np.zeros(len(w), dtype=np.int64)
                for k in range(nn):
                    nr += m[sym[w + k]]
                out[f'RPT{nn}_r{K}'] = int((rep_occ & (nr >= 2)).sum())
    return out


def ef_test(C, reps, R, seed):
    """reps: {name: vocab-id -> symbol-id array}. Returns per rep and statistic: obs, null mean/sd, X, z, p."""
    rng = np.random.default_rng(seed)
    masks = {k: rare_masks(C, r) for k, r in reps.items()}
    obs = {k: repeat_counts(C, C.tok, r, masks[k]) for k, r in reps.items()}
    null = {k: [] for k in reps}
    for _ in range(R):
        t = C.sample(rng)
        for k, r in reps.items():
            null[k].append(repeat_counts(C, t, r, masks[k]))
    res = {}
    for k in reps:
        res[k] = {}
        for nm, o in obs[k].items():
            v = np.array([s[nm] for s in null[k]], dtype=float)
            sd = float(v.std(ddof=1))
            res[k][nm] = {'obs': o, 'null_mean': float(v.mean()), 'null_sd': sd,
                          'X': (o + 1) / (float(v.mean()) + 1), 'z': (o - float(v.mean())) / max(sd, 1e-9),
                          'p': float((1 + (v >= o).sum()) / (1 + R))}
    return res
