#!/usr/bin/env python3
"""PHASE_770 Arm A classifier, gate and verdict-probability table (controls only).

Input: a plant bank (bank770.py) for one analysis set and target. Accepted replicates of each pure model are split in
half (train / held-out, alternating). A multivariate normal is fitted to each model's training features. For any
feature vector, the classifier computes, per model m:
    log posterior_m = log prior_m + log known_m + log N(features; mu_m, Sigma_m)
  prior: 1/2 per class, split equally among the class's models and equally among a model's variants;
  known_m: P(S3far in window | S3c in window) under model m (the already-known part, from the bank counts);
  the MVN term is the new part (features given S3c and S3far, since the bank conditions on both).
Verdict on a feature vector:
  fit check: squared Mahalanobis distance to the best-fitting model <= that model's 99th percentile (training);
             otherwise UNRESOLVED (model set inadequate)
  class posterior >= 0.8 -> STATIC-DOMINANT / POSITION-DEPENDENT-DOMINANT, else UNRESOLVED
  confirmatory only if the new part alone (equal priors, no known part) favours the same class (posterior > 0.5).
Gate (held-out): each pure model reaches its own class in >= 70% and the wrong class in <= 5%; each 50/50 mixture
reaches either class in <= 25%.

Usage: gate770.py BANK_TAG [raw|free]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BANK = HERE.parent / 'results/calib/bank'


def base_name(model):
    return model.split(':')[0] if not model.startswith('MIX') else model


class Classifier:
    def __init__(self, bank, info, version='raw'):
        self.classes = info['classes']
        F = bank['F_raw'] if version == 'raw' else bank['F_free']
        models = bank['model']
        self.models = [m for m in self.classes if self.classes[m] in ('S', 'P') and (models == m).sum() >= 20]
        # priors: 1/2 per class, equal per base model, equal per variant
        prior = {}
        for cls in ('S', 'P'):
            ms = [m for m in self.models if self.classes[m] == cls]
            bases = sorted({base_name(m) for m in ms})
            for m in ms:
                nvar = sum(1 for x in ms if base_name(x) == base_name(m))
                prior[m] = 0.5 / len(bases) / nvar
        self.log_prior = {m: np.log(prior[m]) for m in self.models}
        self.log_known = {m: np.log(max(info['counts'][m]['known_part'] or 1e-12, 1e-12)) for m in self.models}
        self.fit, self.train_idx, self.test_idx = {}, {}, {}
        for m in self.classes:
            idx = np.flatnonzero(models == m)
            self.train_idx[m], self.test_idx[m] = idx[0::2], idx[1::2]
        for m in self.models:
            Z = F[self.train_idx[m]]
            mu = Z.mean(0)
            S = np.cov(Z, rowvar=False)
            S = S + np.eye(len(mu)) * 1e-6 * np.trace(S) / len(mu)
            Si = np.linalg.inv(S)
            _, logdet = np.linalg.slogdet(S)
            d2 = np.einsum('ij,jk,ik->i', Z - mu, Si, Z - mu)
            self.fit[m] = (mu, Si, logdet, float(np.quantile(d2, 0.99)))
        self.F = F

    def score(self, f):
        """f: (n, 7) -> dict with log-likelihoods per model, class posteriors (full and new-part-only), fit check."""
        ll, d2 = {}, {}
        for m in self.models:
            mu, Si, logdet, _ = self.fit[m]
            diff = f - mu
            d2[m] = np.einsum('ij,jk,ik->i', diff, Si, diff)
            ll[m] = -0.5 * (d2[m] + logdet + len(mu) * np.log(2 * np.pi))
        M = self.models
        L_full = np.stack([ll[m] + self.log_prior[m] + self.log_known[m] for m in M], axis=1)
        L_new = np.stack([ll[m] + np.log(1 / len(M)) for m in M], axis=1)
        out = {}
        for key, L in (('full', L_full), ('new', L_new)):
            W = np.exp(L - L.max(axis=1, keepdims=True))
            W /= W.sum(axis=1, keepdims=True)
            isS = np.array([self.classes[m] == 'S' for m in M])
            out[f'post_S_{key}'] = W[:, isS].sum(axis=1)
        best = np.argmax(np.stack([ll[m] for m in M], axis=1), axis=1)
        out['fit_ok'] = np.array([d2[M[b]][i] <= self.fit[M[b]][3] for i, b in enumerate(best)])
        out['best'] = [M[b] for b in best]
        return out

    def verdict(self, f):
        s = self.score(f)
        pS, pSn, ok = s['post_S_full'], s['post_S_new'], s['fit_ok']
        v = np.full(len(pS), 'UNRESOLVED', dtype=object)
        v[(pS >= 0.8) & (pSn > 0.5) & ok] = 'STATIC-DOMINANT'
        v[(pS <= 0.2) & (pSn < 0.5) & ok] = 'POSITION-DEPENDENT-DOMINANT'
        return v, s


def gate(tag, version):
    bank = dict(np.load(BANK / f'bank_{tag}.npz'))
    info = json.load(open(BANK / f'bank_{tag}.json'))
    clf = Classifier(bank, info, version)
    table, rows = {}, {}
    for m, cls in info['classes'].items():
        idx = clf.test_idx[m] if m in clf.models else np.flatnonzero(bank['model'] == m)
        if cls == 'X':
            idx = np.flatnonzero(bank['model'] == m)
        if len(idx) == 0:
            continue
        v, s = clf.verdict(bank[f'F_{version}'][idx])
        n = len(v)
        frac = {k: float((v == k).mean()) for k in ('STATIC-DOMINANT', 'POSITION-DEPENDENT-DOMINANT', 'UNRESOLVED')}
        frac['fit_fail'] = float((~s['fit_ok']).mean())
        frac['n'] = n
        table[m] = frac
        own = {'S': 'STATIC-DOMINANT', 'P': 'POSITION-DEPENDENT-DOMINANT'}.get(cls)
        wrong = {'S': 'POSITION-DEPENDENT-DOMINANT', 'P': 'STATIC-DOMINANT'}.get(cls)
        if cls in ('S', 'P'):
            rows[m] = {'own': frac[own], 'wrong': frac[wrong], 'pass': frac[own] >= 0.70 and frac[wrong] <= 0.05}
        elif m.endswith('/0.5'):
            either = frac['STATIC-DOMINANT'] + frac['POSITION-DEPENDENT-DOMINANT']
            rows[m] = {'either': either, 'pass': either <= 0.25}
    passed = all(r['pass'] for r in rows.values())
    return {'tag': tag, 'version': version, 'gate_pass': passed, 'gate_rows': rows, 'verdict_probabilities': table,
            'models_fitted': clf.models}


def main():
    tag = sys.argv[1]
    versions = sys.argv[2:] or ['raw', 'free']
    out = {}
    for ver in versions:
        g = gate(tag, ver)
        out[ver] = g
        print(f'== {tag} [{ver}] gate {"PASS" if g["gate_pass"] else "FAIL"}')
        for m, r in g['gate_rows'].items():
            print(f'   {m:18s} ' + '  '.join(f'{k} {v:.2f}' if isinstance(v, float) else f'{k} {v}' for k, v in r.items()))
    json.dump(out, open(BANK / f'gate_{tag}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
