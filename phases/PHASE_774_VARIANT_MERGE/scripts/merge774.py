"""PHASE_774 shared machinery: spelling-variant merges and their recovery of hidden units (controls first).

A merge maps each token to a symbol. It is meant to put interchangeable spellings of one hidden unit together,
so that the hidden unit sequence (and any repeated phrases in it) becomes visible.

Merges:
  TOK      the token itself
  MID      canonical MIDDLE (scripts/voynich.py Morphology; the token itself when there is none)
  MIDn1    MID with e-runs and i-runs collapsed
  MIDn2    MIDn1 plus sh -> ch, benched gallows -> ckh, t/p/f -> k (PHASE_772 N2 collapse, applied to the MIDDLE)
  BRn      distributional (exchange / Brown) clustering of the token stream into n classes, fitted per text; tokens
           below the count floor keep their own symbol
  ORACLE   the hidden unit (controls only)
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

import numpy as np
from numba import njit

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
_MORPH = None


def _morph():
    global _MORPH
    if _MORPH is None:
        import sys
        sys.path.insert(0, 'C:/git/voynich')
        from scripts.voynich import Morphology
        _MORPH = Morphology()
    return _MORPH


def middle(w):
    try:
        m = _morph().extract(w).middle
    except Exception:
        m = None
    return m if m else w


def n1(s):
    return re.sub(r'i+', 'i', re.sub(r'e+', 'e', s))


def n2(s):
    s = n1(s)
    s = s.replace('sh', 'ch')
    s = re.sub(r'c[tpf]h', 'ckh', s)
    return re.sub(r'[tpf]', 'k', s)


STATIC_MERGES = {
    'TOK': lambda w: w,
    'MID': middle,
    'MIDn1': lambda w: n1(middle(w)),
    'MIDn2': lambda w: n2(middle(w)),
}


# ------------------------------------------------------------------------------------------------ exchange clustering
@njit(cache=True)
def _f(x):
    return x * math.log(x) if x > 0 else 0.0


@njit(cache=True)
def _exchange(K, a, out_ptr, out_idx, out_cnt, in_ptr, in_idx, in_cnt, self_cnt, outdeg, indeg, order, max_iter,
              min_move_frac):
    V = a.shape[0]
    N = np.zeros((K, K), dtype=np.int64)
    NL = np.zeros(K, dtype=np.int64)
    NR = np.zeros(K, dtype=np.int64)
    for w in range(V):
        for j in range(out_ptr[w], out_ptr[w + 1]):
            N[a[w], a[out_idx[j]]] += out_cnt[j]
        N[a[w], a[w]] += self_cnt[w]
        NL[a[w]] += outdeg[w]
        NR[a[w]] += indeg[w]
    r = np.zeros(K, dtype=np.int64)
    l = np.zeros(K, dtype=np.int64)
    rs = np.empty(K, dtype=np.int64)
    ls = np.empty(K, dtype=np.int64)
    delta = np.empty(K, dtype=np.float64)
    n_iter = 0
    for it in range(max_iter):
        n_iter += 1
        moves = 0
        for oi in range(V):
            w = order[oi]
            c0 = a[w]
            nr = 0
            for j in range(out_ptr[w], out_ptr[w + 1]):
                d = a[out_idx[j]]
                if r[d] == 0:
                    rs[nr] = d
                    nr += 1
                r[d] += out_cnt[j]
            nl = 0
            for j in range(in_ptr[w], in_ptr[w + 1]):
                c = a[in_idx[j]]
                if l[c] == 0:
                    ls[nl] = c
                    nl += 1
                l[c] += in_cnt[j]
            s = self_cnt[w]
            # remove w from c0
            for q in range(nr):
                N[c0, rs[q]] -= r[rs[q]]
            for q in range(nl):
                N[ls[q], c0] -= l[ls[q]]
            N[c0, c0] -= s
            NL[c0] -= outdeg[w]
            NR[c0] -= indeg[w]
            # evaluate every cluster
            best, bestk = -1e300, c0
            for k in range(K):
                dlt = 0.0
                for q in range(nr):
                    d = rs[q]
                    if d != k:
                        dlt += _f(N[k, d] + r[d]) - _f(N[k, d])
                for q in range(nl):
                    c = ls[q]
                    if c != k:
                        dlt += _f(N[c, k] + l[c]) - _f(N[c, k])
                dlt += _f(N[k, k] + r[k] + l[k] + s) - _f(N[k, k])
                dlt -= _f(NL[k] + outdeg[w]) - _f(NL[k])
                dlt -= _f(NR[k] + indeg[w]) - _f(NR[k])
                delta[k] = dlt
                if dlt > best + 1e-9:
                    best, bestk = dlt, k
            if delta[c0] >= best - 1e-9:
                bestk = c0
            if bestk != c0:
                moves += 1
            k = bestk
            for q in range(nr):
                N[k, rs[q]] += r[rs[q]]
            for q in range(nl):
                N[ls[q], k] += l[ls[q]]
            N[k, k] += s
            NL[k] += outdeg[w]
            NR[k] += indeg[w]
            a[w] = k
            for q in range(nr):
                r[rs[q]] = 0
            for q in range(nl):
                l[ls[q]] = 0
        if moves <= min_move_frac * V:
            break
    obj = 0.0
    for c in range(K):
        for d in range(K):
            obj += _f(N[c, d])
        obj -= _f(NL[c]) + _f(NR[c])
    return n_iter, obj


def brown_classes(lines, K, minc=3, max_iter=40, min_move_frac=0.001, seed=0):
    """Exchange clustering of token types (count >= minc) on within-line bigrams. Returns {type: class id}; rarer
    types are absent (callers give them their own symbol)."""
    cnt = Counter(w for ln in lines for w in ln if w is not None)
    types = sorted((w for w, c in cnt.items() if c >= minc), key=lambda w: (-cnt[w], w))
    tid = {w: i for i, w in enumerate(types)}
    V = len(types)
    outs, ins = defaultdict(Counter), defaultdict(Counter)
    self_cnt = np.zeros(V, dtype=np.int64)
    outdeg = np.zeros(V, dtype=np.int64)
    indeg = np.zeros(V, dtype=np.int64)
    for ln in lines:
        for x, y in zip(ln, ln[1:]):
            if x is None or y is None:
                continue
            i, j = tid.get(x, -1), tid.get(y, -1)
            if i < 0 or j < 0:
                continue
            outdeg[i] += 1
            indeg[j] += 1
            if i == j:
                self_cnt[i] += 1
            else:
                outs[i][j] += 1
                ins[j][i] += 1

    def csr(d):
        ptr = np.zeros(V + 1, dtype=np.int64)
        idx, c = [], []
        for w in range(V):
            items = sorted(d[w].items())
            ptr[w + 1] = ptr[w] + len(items)
            idx.extend(k for k, _ in items)
            c.extend(v for _, v in items)
        return ptr, np.array(idx, dtype=np.int64), np.array(c, dtype=np.int64)
    op, oi, oc = csr(outs)
    ip, ii, ic = csr(ins)
    K = min(K, V)
    a = (np.arange(V) % K).astype(np.int64)               # frequency-sorted round robin
    rng = np.random.default_rng(seed)
    order = np.arange(V, dtype=np.int64)
    if seed:
        rng.shuffle(order)
    n_iter, obj = _exchange(K, a, op, oi, oc, ip, ii, ic, self_cnt, outdeg, indeg, order, max_iter, min_move_frac)
    return {w: int(a[i]) for w, i in tid.items()}, {'types_clustered': V, 'iterations': int(n_iter),
                                                    'objective': float(obj)}


def brown_merge(lines, K, minc=3, seed=0):
    cls, info = brown_classes(lines, K, minc=minc, seed=seed)
    return (lambda w: f'#{cls[w]}' if w in cls else w), info


# ------------------------------------------------------------------------------------------------ recovery metrics
def recovery(tokens, units, fn):
    """Information a merge keeps about the hidden unit, and the spelling noise it leaves.
    tokens, units: aligned lists (certain tokens only). Returns bits and per-position collision rates:
      I      I(M; U)
      H_U    H(U)
      H_MgU  H(M | U)    (spelling variation the merge did not remove)
      k1     P(M_i = M_j | U_i = U_j)   (a true unit repeat stays a visible repeat)
      k0     P(M_i = M_j | U_i != U_j)  (chance collision)
    """
    m = [fn(t) for t in tokens]
    n = len(m)
    cu = Counter(units)
    cm = Counter(m)
    cj = Counter(zip(m, units))

    def H(c):
        return -sum(v / n * math.log2(v / n) for v in c.values())
    Hu, Hm, Hj = H(cu), H(cm), H(cj)
    same_u = sum(v * v for v in cu.values())
    same_m = sum(v * v for v in cm.values())
    same_both = sum(v * v for v in cj.values())
    k1 = same_both / same_u
    k0 = (same_m - same_both) / (n * n - same_u)
    return {'I': Hu + Hm - Hj, 'H_U': Hu, 'H_M': Hm, 'H_MgU': Hj - Hu, 'k1': k1, 'k0': k0, 'types': len(cm)}
