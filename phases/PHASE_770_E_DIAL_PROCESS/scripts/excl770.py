#!/usr/bin/env python3
"""PHASE_770 Arm A, exclusion design (replaces v2's class-posterior classifier, whose gate failed: see
results/calib/bank/gate_H81_0.323_0.095_770_v2double.json).

For every model m in a plant bank (replicates accepted at the target S3c +- 0.03), the 8-vector
v = (S3far, V1, V2, V3, V4, D1, D2, D3) of a replicate or of B is scored by its squared Mahalanobis distance to model m
(mean and covariance from m's training replicates). p_m(v) = share of m's reference replicates at least as far
((1 + #) / (1 + n)). Model m is excluded at p_m <= ALPHA.
Class verdicts:
  STATIC EXCLUDED                 every static model excluded (and not every position-dependent one)
  POSITION-DEPENDENT EXCLUDED     every position-dependent model excluded (and not every static one)
  MODEL SET INADEQUATE            every pure model excluded
  UNRESOLVED                      otherwise (surviving models listed)
Replicates of each model are split in order: 40% training, 40% reference, 20% evaluation. The verdict-probability
table applies the rule to every model's evaluation replicates.

Usage: excl770.py BANK_TAG [ALPHA]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BANK = HERE.parent / 'results/calib/bank'
ALPHA = 0.01


def vec(bank, idx=None):
    V = np.column_stack([bank['S3far'], bank['F_raw']])
    return V if idx is None else V[idx]


class Excluder:
    def __init__(self, bank, info):
        self.classes = info['classes']
        models = np.asarray(bank['model'])
        self.models = [m for m in self.classes if (models == m).sum() >= 100]
        V = vec(bank)
        self.fit, self.ref, self.eval_idx = {}, {}, {}
        for m in self.models:
            idx = np.flatnonzero(models == m)
            n = len(idx)
            tr, rf, ev = idx[: int(0.4 * n)], idx[int(0.4 * n): int(0.8 * n)], idx[int(0.8 * n):]
            Z = V[tr]
            mu = Z.mean(0)
            S = np.cov(Z, rowvar=False)
            S = S + np.eye(len(mu)) * 1e-6 * np.trace(S) / len(mu)
            Si = np.linalg.inv(S)
            self.fit[m] = (mu, Si)
            self.ref[m] = np.sort(self._d2(m, V[rf]))
            self.eval_idx[m] = ev
        self.V = V

    def _d2(self, m, X):
        mu, Si = self.fit[m]
        D = X - mu
        return np.einsum('ij,jk,ik->i', D, Si, D)

    def pvals(self, X):
        """X (n, 8) -> {model: p (n,)}"""
        out = {}
        for m in self.models:
            d2 = self._d2(m, X)
            ref = self.ref[m]
            ge = len(ref) - np.searchsorted(ref, d2, side='left')
            out[m] = (1 + ge) / (1 + len(ref))
        return out

    def verdicts(self, X, alpha=ALPHA):
        P = self.pvals(X)
        S = [m for m in self.models if self.classes[m] == 'S']
        Pm = [m for m in self.models if self.classes[m] == 'P']
        allS = np.all([P[m] <= alpha for m in S], axis=0)
        allP = np.all([P[m] <= alpha for m in Pm], axis=0)
        v = np.full(len(X), 'UNRESOLVED', dtype=object)
        v[allS & ~allP] = 'STATIC EXCLUDED'
        v[allP & ~allS] = 'POSITION-DEPENDENT EXCLUDED'
        v[allS & allP] = 'MODEL SET INADEQUATE'
        return v, P


def main():
    tag = sys.argv[1]
    alpha = float(sys.argv[2]) if len(sys.argv) > 2 else ALPHA
    bank = dict(np.load(BANK / f'bank_{tag}.npz'))
    info = json.load(open(BANK / f'bank_{tag}.json'))
    ex = Excluder(bank, info)
    table, excl = {}, {}
    for t in ex.models:
        X = ex.V[ex.eval_idx[t]]
        v, P = ex.verdicts(X, alpha)
        table[t] = {k: float((v == k).mean()) for k in
                    ('STATIC EXCLUDED', 'POSITION-DEPENDENT EXCLUDED', 'MODEL SET INADEQUATE', 'UNRESOLVED')}
        table[t]['n_eval'] = int(len(X))
        excl[t] = {m: float((P[m] <= alpha).mean()) for m in ex.models}
    print(f'== {tag}  alpha {alpha}  verdict probabilities by true model (evaluation replicates)')
    print(f'{"true model":18s} {"cls":3s} {"STAT-EXCL":>9s} {"POS-EXCL":>9s} {"INADEQ":>7s} {"UNRES":>6s}  self-excl')
    for t in ex.models:
        r = table[t]
        print(f'{t:18s} {ex.classes[t]:3s} {r["STATIC EXCLUDED"]:9.3f} {r["POSITION-DEPENDENT EXCLUDED"]:9.3f} '
              f'{r["MODEL SET INADEQUATE"]:7.3f} {r["UNRESOLVED"]:6.3f}  {excl[t][t]:.3f}')
    json.dump({'tag': tag, 'alpha': alpha, 'verdict_probabilities': table, 'exclusion_rates': excl,
               'classes': {m: ex.classes[m] for m in ex.models}},
              open(BANK / f'excl_{tag}_a{alpha}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
