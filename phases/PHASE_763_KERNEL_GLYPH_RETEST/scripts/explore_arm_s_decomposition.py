#!/usr/bin/env python3
"""PHASE_763 — POST-HOC EXPLORATION (not pre-registered, not verdict-bearing).

Question: what carries the Arm S signal (glyph content of token t -> class of t+1, beyond the first glyph of t, above
N5)? Per-unit, e (z 10.1), bench (7.6) and the non-kernel d (8.9) are strong; k (1.8) is not. If the signal is the
token's ending or the class succession, it should vanish when the conditioning set includes the ending or the class
of t.

Conditioning sets (target always C(t+1), 49 classes + UN):
  F      first glyph unit of t                      (the Arm S primary, reproduced here)
  F+L1   first + last glyph unit of t
  F+L2   first + last two glyph units of t
  CLS    class of t (UN tokens: UN x first glyph unit)
Null: N5 (glyph edges, beta 2), 2 chains x 300 draws at thin 16 (the Arm S H thin). Miller-Madow CMI.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path('C:/git/voynich')
os.environ['NUMBA_CACHE_DIR'] = str(ROOT / 'phases/PHASE_763_KERNEL_GLYPH_RETEST/scripts/__pycache__/numba')
import numpy as np  # noqa: E402

spec = importlib.util.spec_from_file_location('n5', ROOT / 'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py')
N5 = importlib.util.module_from_spec(spec)
sys.modules['n5'] = N5
spec.loader.exec_module(N5)

OUT = ROOT / 'phases/PHASE_763_KERNEL_GLYPH_RETEST/results'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
S1 = {'ch': 'B', 'sh': 'B'}
UNITS = ['e', 'B', 'k', 'd', 'a', 't', 'o', 'y', 'l', 's', 'p']
CTM = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8'))
T2C = {w: int(c) for w, c in CTM['token_to_class'].items()}


def ent(c, N):
    c = c[c > 0]
    p = c / N
    return float(-(p * np.log(p)).sum() + (len(c) - 1) / (2.0 * N))


def cmi(strat, y, x, nS, nY):
    N = float(len(strat))
    sx = strat * 2 + x
    return (ent(np.bincount(sx, minlength=nS * 2).astype(float), N)
            + ent(np.bincount(strat * nY + y, minlength=nS * nY).astype(float), N)
            - ent(np.bincount(sx * nY + y, minlength=nS * 2 * nY).astype(float), N)
            - ent(np.bincount(strat, minlength=nS).astype(float), N)) / np.log(2)


def main():
    lines, secs, keys = N5.load_primary()
    D = N5.Data(lines, secs, 'GLYPH')
    V = D.vocab
    raw = [GLYPH_RE.findall(w) for w in V]
    enc = {}

    def eid(key, v):
        d = enc.setdefault(key, {})
        return d.setdefault(v, len(d))
    Fr = np.array([eid('F', r[0]) for r in raw])
    L1 = np.array([eid('L1', r[-1]) for r in raw])
    L2 = np.array([eid('L2', tuple(r[-2:])) for r in raw])
    Cl = np.array([T2C.get(w, 0) for w in V])
    CLS = np.array([c if c > 0 else 50 + Fr[i] for i, c in enumerate(Cl)])
    su = [[S1.get(g, g) for g in r] for r in raw]
    X = np.array([[1 if u in set(s) else 0 for u in UNITS] for s in su])
    cert = np.array([sum(w is not None for w in ln) for ln in lines])
    idx = np.flatnonzero(D.valid_edge & (cert[D.line_of] >= 5))
    nF, nL1, nL2 = len(enc['F']), len(enc['L1']), len(enc['L2'])
    strata = {'F': (lambda a: Fr[a], nF), 'F+L1': (lambda a: Fr[a] * nL1 + L1[a], nF * nL1),
              'F+L2': (lambda a: Fr[a] * nL2 + L2[a], nF * nL2), 'CLS': (lambda a: CLS[a], 50 + nF)}

    def stats(tok):
        a, b = tok[idx], tok[idx + 1]
        y = Cl[b]
        out = {}
        for k, (f, nS) in strata.items():
            s = f(a)
            xa = X[a]
            out[k] = [cmi(s, y, xa[:, j], nS, 50) for j in range(len(UNITS))]
        return out

    draws = {k: [] for k in strata}
    for ci, (seed, start) in enumerate(((76370, 'real'), (76371, 'N1'))):
        tok = D.tok0.copy()
        N5.nb_seed(seed)
        if start == 'N1':
            N5.nb_shuffle_medial(tok, D.mov_pos, D.mov_start, D.mov_cnt)
        C = np.zeros_like(D.R)
        N5.nb_counts(tok, D.valid_edge, D.line_of, D.sec_line, D.last_u, D.first_u, D.NF, C)
        L1c = np.array([int(np.abs(C - D.R).sum())], dtype=np.int64)
        args = (D.n_prop, D.cumw, D.mov_pos, D.mov_start, D.mov_cnt, D.valid_edge, D.sec_line, D.last_u, D.first_u, D.NF)
        au = 1000 if start == 'N1' else 0
        N5.nb_sweeps(tok, C, D.R, L1c, 2000, 2.0, au, 0, *args)
        sw = 2000
        for _ in range(300):
            N5.nb_sweeps(tok, C, D.R, L1c, 16, 2.0, au, sw, *args)
            sw += 16
            st = stats(tok)
            for k in strata:
                draws[k].append(st[k])
        print('chain', ci, 'done', flush=True)
    real = stats(D.tok0)
    res = {'note': 'POST-HOC EXPLORATION, not pre-registered, not verdict-bearing', 'units': UNITS, 'z': {},
           'excess_bits': {}}
    for k in strata:
        arr = np.array(draws[k])
        mu, sd = arr.mean(0), arr.std(0)
        z = (np.array(real[k]) - mu) / sd
        res['z'][k] = dict(zip(UNITS, np.round(z, 2).tolist()))
        res['excess_bits'][k] = dict(zip(UNITS, np.round(np.array(real[k]) - mu, 5).tolist()))
        print(k, res['z'][k], flush=True)
    json.dump(res, open(OUT / 'explore_arm_s_decomposition.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
