"""PHASE_776 machinery: does the class-transition eigenstructure (C2061/C2067) survive the edge-fixing null?

Statistic (as in PHASE_733, the C2061 pipeline): map every certain token to its class (CLASS_COSURVIVAL_TEST map, 49
classes); within each line drop unmapped tokens and join their neighbours (the BRIDGE convention); count adjacent class
pairs into a 49x49 matrix; row-normalise; lambda2 and lambda3 = the second and third largest eigenvalue magnitudes.

Null: the header-aware exact edge-frame permutation (EF; PHASE_774/775): tokens permuted within folio x line type among
positions that share zone, first glyph unit and last two glyph units. EF keeps every boundary junction and every
position's edges, and destroys which token (and so which class) sits in a slot among same-edge tokens.

Excess: D_k = lambda_k(corpus) - mean lambda_k(EF samples), k = 2, 3; p = (1 + #{null >= obs}) / (1 + R).
Reference floors reported for continuity with C2061: the within-line class shuffle.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
N_CLS = 49


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


E = _imp('ef774', 'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py')
GK = _imp('gen775', 'phases/PHASE_775_BOUNDARY_KEY/scripts/gen775.py')
G = GK.G
HR = G.HR
HR2 = G.HR2

_CM = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8'))
TOKEN_CLASS = {t: int(c) for t, c in _CM['token_to_class'].items()}     # classes 1..49


class Spectrum:
    """Per-corpus arrays; lambda2/lambda3 for any token arrangement of the same Corpus."""

    def __init__(self, C):
        self.C = C
        self.cls = np.array([TOKEN_CLASS.get(w, 0) for w in C.vocab], dtype=np.int64)   # 0 = unmapped
        n = len(C.tok)
        self.line_of = C.line_of

    def lambdas(self, tok, k_max=3, lag=1):
        """lag 1: adjacent classified tokens (bridged); lag 2: classified tokens two apart in the bridged sequence."""
        cl = np.where(tok >= 0, self.cls[np.where(tok >= 0, tok, 0)], 0)
        keep = cl > 0
        # bridge: consecutive classified tokens within a line, unmapped tokens dropped
        idx = np.flatnonzero(keep)
        a, b = idx[:-lag], idx[lag:]
        same = self.line_of[a] == self.line_of[b]
        a, b = a[same], b[same]
        counts = np.zeros((N_CLS, N_CLS))
        np.add.at(counts, (cl[a] - 1, cl[b] - 1), 1)
        rs = counts.sum(1, keepdims=True)
        P = np.divide(counts, rs, where=rs > 0, out=np.zeros_like(counts))
        ev = np.sort(np.abs(np.linalg.eigvals(P)))[::-1]
        return tuple(float(x) for x in ev[1:k_max])

    def shuffle_floor(self, rng, n=30):
        """Within-line shuffle of the classified tokens (the C2061 floor)."""
        out = []
        tok = self.C.tok
        for _ in range(n):
            t = tok.copy()
            for li in np.unique(self.line_of):
                pos = np.flatnonzero((self.line_of == li) & (t >= 0))
                t[pos] = t[rng.permutation(pos)]
            out.append(self.lambdas(t))
        return np.array(out)


def _summ(obs, v, R):
    return {'obs': float(obs), 'null_mean': float(v.mean()), 'null_sd': float(v.std(ddof=1)),
            'D': float(obs - v.mean()), 'z': float((obs - v.mean()) / max(float(v.std(ddof=1)), 1e-12)),
            'p': float((1 + (v >= obs).sum()) / (1 + R))}


def run(lines, groups, R=200, seed=0, floor=True, efl=True):
    """Primary: EF within `groups` (folio x line type), cells = zone x first glyph x last two glyph units.
    Descriptives: lambda3; lag-2 lambda2 on the same samples; EFL = the same permutation within LINE (edges and line
    composition both fixed; low movable mass, exact); the within-line class shuffle floor (C2061's floor)."""
    rng = np.random.default_rng(seed)
    C = E.Corpus(lines, groups, sig=E.sig_fl2, ns=(2,))
    S = Spectrum(C)
    obs = S.lambdas(C.tok)
    obs2 = S.lambdas(C.tok, lag=2)
    null, null2 = [], []
    for _ in range(R):
        t = C.sample(rng)
        null.append(S.lambdas(t))
        null2.append(S.lambdas(t, lag=2))
    null, null2 = np.array(null), np.array(null2)
    out = {'lambda2': _summ(obs[0], null[:, 0], R), 'lambda3': _summ(obs[1], null[:, 1], R),
           'lag2_lambda2': _summ(obs2[0], null2[:, 0], R)}
    if efl:
        line_groups = list(range(len(lines)))
        CL = E.Corpus(lines, line_groups, sig=E.sig_fl, ns=(2,))     # first + last glyph: every junction kept
        SL = Spectrum(CL)
        nl = np.array([SL.lambdas(CL.sample(rng)) for _ in range(R)])
        out['EFL_lambda2'] = _summ(obs[0], nl[:, 0], R)
        out['EFL_cells'] = {'n_cells': CL.n_cells, 'frac_movable': CL.frac_movable}
    if floor:
        fl = S.shuffle_floor(rng)
        out['shuffle_floor'] = {'lambda2': float(fl[:, 0].mean()), 'lambda3': float(fl[:, 1].mean())}
    out['_cells'] = {'n_cells': C.n_cells, 'frac_movable': C.frac_movable}
    return out


# ------------------------------------------------------------------------------------------------ edge-only generator
def edge_only_lines(sk, seed, k=2):
    """A first-order EDGE chain with no class structure beyond edges: each token is drawn from B's tokens that follow
    the same (previous token's last k glyph units, zone) in B; line starts from B's line-initial tokens. Exposure: B's
    adjacent pairs keyed by ending and zone (the same class as the habit generators)."""
    from collections import Counter, defaultdict
    rng = np.random.default_rng(seed)
    pool = defaultdict(Counter)
    for ln in sk['lines']:
        prev = None
        L = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                prev = None
                continue
            z = 0 if p == 0 else (2 if p == L - 1 else 1)
            key = ('^', z) if prev is None else (GK.K.ending(prev, k), z)
            pool[key][w] += 1
            prev = w
    zone_pool = defaultdict(Counter)
    for (c, z), cnt in pool.items():
        zone_pool[z].update(cnt)
    cache = {}

    def draw(key, counter):
        if key not in cache:
            keys = list(counter)
            p = np.array([counter[x] for x in keys], dtype=float)
            cache[key] = (keys, np.cumsum(p / p.sum()))
        keys, cum = cache[key]
        return keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]
    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        L = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                cur.append(None)
                prev = None
                continue
            z = 0 if p == 0 else (2 if p == L - 1 else 1)
            key = ('^', z) if prev is None else (GK.K.ending(prev, k), z)
            src = pool.get(key)
            t = draw(key, src) if src and sum(src.values()) >= 5 else draw(('Z', z), zone_pool[z])
            cur.append(t)
            prev = t
        out.append(cur)
    return out
