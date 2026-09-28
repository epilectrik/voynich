#!/usr/bin/env python3
"""PHASE_757 discriminators D2-D6 and descriptive statistics (definitions: ../PRE_REGISTRATION.md, commit a5506cb).

A corpus is a list of lines (lists of str tokens or None = blocker) plus a folio label per line.
"Shuffle" = uniform permutation of each line's certain tokens; blockers stay in place.
"""
from __future__ import annotations

import re

import numpy as np

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
N_SHUF_MI, N_SHUF_TRI, N_SHUF_GAIN = 20, 20, 3
D_ABS = 0.75
COMMON_MIN = 10


class Corpus:
    def __init__(self, lines, folios):
        toks, line_of, pos, seg, zone = [], [], [], [], []
        s = -1
        for li, ln in enumerate(lines):
            prev_none = True
            n = len(ln)
            for p, w in enumerate(ln):
                if w is None:
                    prev_none = True
                    continue
                if prev_none:
                    s += 1
                    prev_none = False
                toks.append(w)
                line_of.append(li)
                pos.append(p)
                seg.append(s)
                zone.append(0 if p == 0 else (2 if p == n - 1 else 1))
        self.vocab, ids = np.unique(np.array(toks, dtype=object).astype(str), return_inverse=True)
        self.ids = ids.astype(np.int64)
        self.V = len(self.vocab)
        self.line_of = np.array(line_of, dtype=np.int64)
        self.seg = np.array(seg, dtype=np.int64)
        self.zone = np.array(zone, dtype=np.int64)
        self.n = len(self.ids)
        self.adj = self.seg[:-1] == self.seg[1:]
        fol = {f: i for i, f in enumerate(sorted(set(folios)))}
        self.folio = np.array([fol[folios[li]] for li in line_of], dtype=np.int64)
        self.n_lines = len(lines)
        first_units = [GLYPH_RE.findall(w) for w in self.vocab]
        fu = sorted({g[0] for g in first_units})
        lu = sorted({g[-1] for g in first_units})
        self.first_u = np.array([fu.index(g[0]) for g in first_units], dtype=np.int64)
        self.last_u = np.array([lu.index(g[-1]) for g in first_units], dtype=np.int64)
        self.NFU, self.NLU = len(fu), len(lu)
        self.fold = self.line_of % 10
        cert_per_line = np.bincount(self.line_of, minlength=self.n_lines)
        self.d6_mask = cert_per_line[self.line_of] >= 3
        freq = np.bincount(self.ids, minlength=self.V)
        self.common = freq >= COMMON_MIN
        self.lines = lines

    def shuffle(self, rng):
        order = np.lexsort((rng.random(self.n), self.line_of))
        return self.ids[order]


def _mi(a, b, na, nb):
    j = np.bincount(a * nb + b, minlength=na * nb).astype(float).reshape(na, nb)
    n = j.sum()
    if n == 0:
        return 0.0
    p = j / n
    pa, pb = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (pa @ pb)[nz])).sum())


def edge_mi(C, ids):
    a = C.last_u[ids[:-1]][C.adj]
    b = C.first_u[ids[1:]][C.adj]
    return _mi(a, b, C.NLU, C.NFU)


def d2(C, rng):
    return edge_mi(C, C.ids) - np.mean([edge_mi(C, C.shuffle(rng)) for _ in range(N_SHUF_MI)])


def d3(C):
    O = int(((C.ids[:-1] == C.ids[1:]) & C.adj).sum())
    key = C.seg * C.V + C.ids
    _, cnt = np.unique(key, return_counts=True)
    seg_of_key = np.unique(key) // C.V
    seg_len = np.bincount(C.seg)
    X = float((cnt * (cnt - 1) / seg_len[seg_of_key]).sum())
    return float(np.log((O + 0.5) / (X + 0.5))), O, X


def tri_recur(C, ids):
    ok = C.adj[:-1] & C.adj[1:]
    k = np.flatnonzero(ok)
    if len(k) == 0:
        return 0
    V = np.int64(C.V)
    key = (ids[k] * V + ids[k + 1]) * V + ids[k + 2]
    pairs = np.unique(np.stack([key, C.folio[k]], axis=1), axis=0)
    _, nf = np.unique(pairs[:, 0], return_counts=True)
    return int((nf >= 3).sum())


def d4(C, rng):
    O = tri_recur(C, C.ids)
    S = float(np.mean([tri_recur(C, C.shuffle(rng)) for _ in range(N_SHUF_TRI)]))
    return float(np.log((O + 0.5) / (S + 0.5))), O, S


def _lookup(uk, uc, keys):
    i = np.searchsorted(uk, keys)
    i = np.minimum(i, len(uk) - 1)
    return np.where(uk[i] == keys, uc[i], 0)


def bigram_gain(C, ids):
    """Held-out gain (bits/token) of the token-bigram model over the edge-glyph-conditioned base model."""
    V = C.V
    START_V, UNK = V, V + 1
    W = V + 2
    prev = np.empty(C.n, dtype=np.int64)
    prev[0] = START_V
    prev[1:] = np.where(C.adj, ids[:-1], START_V)
    g = np.where(prev == START_V, C.NLU, C.last_u[np.minimum(prev, V - 1)])
    total_gain, total_n = 0.0, 0
    for f in range(10):
        tr = C.fold != f
        te = ~tr
        w_tr, w_te = ids[tr], ids[te]
        c = np.bincount(w_tr, minlength=V).astype(float)
        N = c.sum()
        n1 = float((c == 1).sum())
        known = c[w_te] > 0
        pu = np.where(known, (1 - n1 / N) * c[w_te] / N, n1 / N)
        wt = np.where(known, w_te, UNK)
        # base model on edge-glyph context
        gk_tr = g[tr] * W + w_tr
        uk, uc = np.unique(gk_tr, return_counts=True)
        cg = np.bincount(g[tr], minlength=C.NLU + 1).astype(float)
        Tg = np.bincount(uk // W, minlength=C.NLU + 1).astype(float)
        gte = g[te]
        cgw = _lookup(uk, uc, gte * W + wt).astype(float)
        cgt = cg[gte]
        with np.errstate(divide='ignore', invalid='ignore'):
            p0 = np.where(cgt > 0, np.maximum(cgw - D_ABS, 0) / cgt + D_ABS * Tg[gte] / cgt * pu, pu)
        # full model on previous-token context
        vk_tr = prev[tr] * W + w_tr
        vk, vc = np.unique(vk_tr, return_counts=True)
        cv = np.bincount(prev[tr], minlength=V + 1).astype(float)
        Tv = np.bincount(vk // W, minlength=V + 1).astype(float)
        vte = prev[te]
        cvw = _lookup(vk, vc, vte * W + wt).astype(float)
        cvt = cv[vte]
        with np.errstate(divide='ignore', invalid='ignore'):
            p1 = np.where(cvt > 0, np.maximum(cvw - D_ABS, 0) / cvt + D_ABS * Tv[vte] / cvt * p0, p0)
        total_gain += float((np.log2(p1) - np.log2(p0)).sum())
        total_n += int(te.sum())
    return total_gain / total_n


def d5(C, rng):
    real = bigram_gain(C, C.ids)
    sh = float(np.mean([bigram_gain(C, C.shuffle(rng)) for _ in range(N_SHUF_GAIN)]))
    return real - sh, real, sh


def zone_mi(C, ids):
    m = C.d6_mask & C.common[ids]
    if not m.any():
        return 0.0
    t = ids[m]
    _, t = np.unique(t, return_inverse=True)
    return _mi(t, C.zone[m], int(t.max()) + 1, 3)


def d6(C, rng):
    return zone_mi(C, C.ids) - np.mean([zone_mi(C, C.shuffle(rng)) for _ in range(N_SHUF_MI)])


def descriptives(C):
    freq = np.bincount(C.ids, minlength=C.V)
    fs = np.sort(freq)[::-1]
    r = np.arange(1, len(fs) + 1)
    top = min(len(fs), 1000)
    zipf = float(np.polyfit(np.log(r[:top]), np.log(fs[:top]), 1)[0])
    lines_str = [' '.join(w for w in ln if w is not None) for ln in C.lines]
    lines_str = [s for s in lines_str if s]
    dup_lines = len(lines_str) - len(set(lines_str))
    same = (C.ids[:-1] == C.ids[1:]) & C.adj
    run, max_run = 1, 1
    for s in same:
        run = run + 1 if s else 1
        max_run = max(max_run, run)
    erun = np.array([max((len(m) for m in re.findall(r'e+', w)), default=0) for w in C.vocab])
    ecls = np.minimum(erun, 2)[C.ids]
    lag1 = float(((ecls[:-1] == ecls[1:]) & C.adj).sum() / max(C.adj.sum(), 1))
    qok = np.array([w.startswith('qok') for w in C.vocab])[C.ids].astype(float)
    best = 0.0
    for f in np.unique(C.folio):
        q = qok[C.folio == f]
        if len(q) >= 10:
            best = max(best, float(np.convolve(q, np.ones(10), 'valid').max()))
    return {'types': int(C.V), 'hapax_type_fraction': float((freq == 1).sum() / C.V), 'zipf_slope': zipf,
            'mean_token_length': float(np.mean([len(w) for w in C.vocab[C.ids]])), 'duplicate_lines': dup_lines,
            'max_identical_run': int(max_run), 'erun_class_same_lag1': lag1, 'max_qok_in_10_window': best,
            'tokens': int(C.n)}


def all_stats(lines, folios, rng):
    C = Corpus(lines, folios)
    v2 = d2(C, rng)
    v3, O3, X3 = d3(C)
    v4, O4, S4 = d4(C, rng)
    v5, g_real, g_sh = d5(C, rng)
    v6 = d6(C, rng)
    out = {'D2': float(v2), 'D3': v3, 'D4': v4, 'D5': float(v5), 'D6': float(v6),
           'aux': {'edge_mi_raw': edge_mi(C, C.ids), 'D3_obs': O3, 'D3_exp': X3, 'D4_obs': O4, 'D4_shuf': S4,
                   'gain_real': g_real, 'gain_shuf': g_sh}}
    out['desc'] = descriptives(C)
    return out
