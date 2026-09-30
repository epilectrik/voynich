"""PHASE_775 machinery: is B's word-boundary rule the key of a context-keyed cipher? (rank decoding)

Idea. Suppose each token is t_i = A_{c_i}(u_i): a hidden unit u_i written with an alphabet A_c chosen by a context c_i
that the reader can see, here the ending of the previous token (B's boundary coupling). Within one context the
alphabet is a relabelling, so the tokens seen after context c have the frequency profile of the hidden units. Replacing
every token by its frequency RANK among the tokens that follow the same context ("rank decoding") then maps equal
hidden units to equal symbols across contexts, and the hidden text's word order reappears as order among the ranks.
If the boundary rule is only a writing habit, rank decoding gains nothing.

Keys (the context c_i of token i):
  K0  none (one context): global frequency rank, the reference
  K1  the last glyph unit of the previous token
  K2  the last two glyph units of the previous token
Line-initial tokens and tokens after an uncertain-token blocker take the context '^'.

Statistic. S = plug-in mutual information (bits) between consecutive decoded symbols within a line; symbols are ranks
1..R_MAX-1 with every rank >= R_MAX pooled into one tail symbol. The decoder is re-estimated on every corpus it is
applied to (null samples included), so the null runs the same pipeline.

Null. The exact edge-frame permutation (EF, PHASE_774), here within folio x line type (paragraph-first line or body
line): tokens are permuted among positions that share group, zone, first glyph unit and last two glyph units. EF keeps
every position's K1 and K2 context exactly (the previous token's ending is part of its cell) and destroys which token
fills a context's slot, which is where a context-keyed cipher carries its message. dS = S(corpus) - mean S(EF samples).
Key gain G_K = dS_K - dS_K0: a context-keyed cipher gains from ranking within the key's contexts; a plain code, a
first-order habit process or a key mechanism with no message does not.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
R_MAX = 21                       # ranks 1..20 kept, 21+ pooled


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


E = _imp('ef774', 'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py')


def ending(w, k):
    g = GLYPH_RE.findall(w)
    return ''.join(g[-k:])


KEYS = {'K0': None, 'K1': 1, 'K2': 2}


class Decoder:
    """Per-corpus arrays for rank decoding under one key."""

    def __init__(self, C, key):
        self.C = C
        self.key = key
        k = KEYS[key]
        voc = C.vocab
        if k is None:
            end_id = np.zeros(len(voc), dtype=np.int64)
            self.n_ctx = 2
        else:
            ids = {}
            end_id = np.array([ids.setdefault(ending(w, k), len(ids)) for w in voc], dtype=np.int64)
            self.n_ctx = len(ids) + 1
        self.end_id = end_id + 1                   # context 0 = '^' (line start / after blocker)
        n = len(C.tok)
        self.same_line_prev = np.zeros(n, dtype=bool)
        self.same_line_prev[1:] = C.line_of[1:] == C.line_of[:-1]
        self.gcount = np.bincount(C.tok[C.tok >= 0], minlength=len(voc)).astype(np.int64)
        # pairs (i, i+1) inside a line
        self.pair = np.flatnonzero(self.same_line_prev[1:]) + 1          # index of the second member

    def contexts(self, tok):
        prev = np.roll(tok, 1)
        ctx = np.where(self.same_line_prev & (prev >= 0), self.end_id[np.where(prev >= 0, prev, 0)], 0)
        if KEYS[self.key] is None:
            ctx = np.zeros_like(ctx)
        return ctx

    def decode(self, tok):
        """Rank of each certain token within its context (1-based, pooled at R_MAX); -1 at blockers."""
        valid = tok >= 0
        ctx = self.contexts(tok)
        V = len(self.C.vocab)
        key = ctx[valid] * V + tok[valid]
        uk, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        uctx = uk // V
        utok = uk % V
        # rank within context: count desc, then global count desc, then token id
        order = np.lexsort((utok, -self.gcount[utok], -cnt, uctx))
        rank = np.empty(len(uk), dtype=np.int64)
        sc = uctx[order]
        start = np.r_[0, np.flatnonzero(np.diff(sc)) + 1]
        pos_in = np.arange(len(order)) - np.repeat(start, np.diff(np.r_[start, len(order)]))
        rank[order] = pos_in + 1
        r = np.full(len(tok), -1, dtype=np.int64)
        r[np.flatnonzero(valid)] = np.minimum(rank[inv.ravel()], R_MAX)
        return r

    def stat(self, tok):
        r = self.decode(tok)
        a, b = r[self.pair - 1], r[self.pair]
        ok = (a > 0) & (b > 0)
        a, b = a[ok], b[ok]
        K = R_MAX + 1
        joint = np.bincount(a * K + b, minlength=K * K).reshape(K, K).astype(float)
        n = joint.sum()
        pa, pb = joint.sum(1) / n, joint.sum(0) / n
        pj = joint / n
        nz = pj > 0
        return float((pj[nz] * np.log2(pj[nz] / np.outer(pa, pb)[nz])).sum())


def run(lines, groups, keys=('K0', 'K1', 'K2'), R=200, seed=0):
    """S and the EF null for each key, with G_K = dS_K - dS_K0 (the key gain) and its null distribution.
    groups: the EF permutation group of every line (folio x line type: paragraph-first line or body line).
    Every key is scored under the same EF samples: cells (group, zone, first glyph unit, last TWO glyph units), which
    keep the K1 and K2 contexts of every position exactly."""
    rng = np.random.default_rng(seed)
    C = E.Corpus(lines, groups, sig=E.sig_fl2, ns=(2,))
    Ds = {k: Decoder(C, k) for k in keys}
    obs = {k: D.stat(C.tok) for k, D in Ds.items()}
    null = {k: [] for k in keys}
    for _ in range(R):
        t = C.sample(rng)
        for k, D in Ds.items():
            null[k].append(D.stat(t))
    out = {}
    for k in keys:
        v = np.array(null[k])
        out[k] = {'S': obs[k], 'null_mean': float(v.mean()), 'null_sd': float(v.std(ddof=1)),
                  'dS': obs[k] - float(v.mean()), 'z': (obs[k] - float(v.mean())) / max(float(v.std(ddof=1)), 1e-12),
                  'p': float((1 + (v >= obs[k]).sum()) / (1 + R))}
    if 'K0' in keys:
        v0 = np.array(null['K0'])
        for k in keys:
            if k == 'K0':
                continue
            g_obs = obs[k] - obs['K0']                       # raw key gain in the corpus
            gv = np.array(null[k]) - v0                      # raw key gain in each null sample
            out[k]['G'] = g_obs - float(gv.mean())           # = dS_K - dS_K0
            out[k]['G_p'] = float((1 + (gv >= g_obs).sum()) / (1 + R))
    out['_cells'] = {'n_cells': C.n_cells, 'frac_movable': C.frac_movable}
    return out
