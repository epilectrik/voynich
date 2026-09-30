#!/usr/bin/env python3
"""PHASE_770 Arm A classifier v3 (after the lean-expert v2 check; v2's class-label gate failed, see
results/calib/bank/gate_H81_0.323_0.095_770_v2double.json).

Classes by the latent position contrast D14 (stored in the bank JSON):
  S  static              D14 <= 0.15        (in the class prior and the gate)
  P  position-dependent  D14 >= 0.50        (in the class prior and the gate)
  I  intermediate        in between         (fit check and verdict tables only)
  X  mixtures                               (gated by their own D14 class; intermediate-D14 mixtures not gated)
Per model: a joint Gaussian of (S3c, S3far, features) fitted to its training replicates (first 40% in bank order);
reference replicates (next 40%) give the fit-check percentile; evaluation replicates (last 20%) give the gate and the
verdict tables. For an observation o = (S3c_o, S3far_o, f_o):
  known_m  = density of S3far_o given S3c_o                       (the already-known part)
  new_m    = density of f_o given S3c_o and S3far_o               (the new part)
  posterior over S and P models: prior (1/2 per class, equal per base model, equal per variant) x known x new
  BF_new   = [sum over S of w_m new_m] / [sum over P of w_m new_m], w_m the within-class prior weights
  fit check: the conditional Mahalanobis distance of f_o to the best-fitting model among S, P and I (by known x new)
             is at most that model's 99th percentile over its reference replicates
Verdict: STATIC-DOMINANT if P(S) >= POST_THR (0.9), BF_new >= BF_THR (10) and the fit check passes;
POSITION-DEPENDENT-DOMINANT if P(S) <= 0.1, BF_new <= 1/10 and the fit check passes; otherwise UNRESOLVED
(thresholds calibrated on controls before lock, thr770.py). Every verdict carries its bound
("position-dependent models with D14 >= 0.5 disfavoured" / "static models with D14 <= 0.15 disfavoured").
Gate map: grid S3c {0.28 ... 0.36} x S3far {0.03 ... 0.15}; evaluation replicates within +-0.03 of both; each S/P model
with n >= 30 reaches its own class in >= 70% and the wrong class in <= 5%; a mixture whose own D14 falls in a class
reaches the other class in <= 15%; mixtures with intermediate D14 are not gated (same rule as intermediate models).

Usage: clf770.py BANK_TAG      (writes clf_<tag>.json: gate map for both feature versions, verdict tables)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BANK = HERE.parent / 'results/calib/bank'
GRID_S3C = [0.28, 0.30, 0.32, 0.34, 0.36]
POST_THR, BF_THR = 0.9, 10.0      # calibrated on controls before lock (thr770.py; v3 draft had 0.8 and 3)
GRID_S3F = [0.03, 0.06, 0.09, 0.12, 0.15]
WIN = 0.03


def base_name(m):
    return m.split(':')[0]


class CondGauss:
    """Joint Gaussian of (S3c, S3far, features) with the two conditionals used by the classifier."""

    def __init__(self, Z):
        mu = Z.mean(0)
        S = np.cov(Z, rowvar=False)
        S = S + np.eye(len(mu)) * 1e-9 * np.trace(S)
        self.mu, self.S = mu, S
        # S3far | S3c
        self.b_far = S[1, 0] / S[0, 0]
        self.v_far = S[1, 1] - S[1, 0] ** 2 / S[0, 0]
        # features | S3c, S3far
        g, r = [0, 1], list(range(2, len(mu)))
        Sgg, Srg, Srr = S[np.ix_(g, g)], S[np.ix_(r, g)], S[np.ix_(r, r)]
        self.Bf = Srg @ np.linalg.inv(Sgg)
        Sc = Srr - self.Bf @ Srg.T
        self.Sci = np.linalg.inv(Sc)
        self.logdet = np.linalg.slogdet(Sc)[1]
        self.k = len(r)

    def known_logpdf(self, a, b):
        m = self.mu[1] + self.b_far * (a - self.mu[0])
        return -0.5 * ((b - m) ** 2 / self.v_far + np.log(2 * np.pi * self.v_far))

    def new_d2(self, a, b, F):
        m = self.mu[2:] + (np.column_stack([a - self.mu[0], b - self.mu[1]]) @ self.Bf.T)
        D = F - m
        return np.einsum('ij,jk,ik->i', D, self.Sci, D)

    def new_logpdf(self, a, b, F):
        return -0.5 * (self.new_d2(a, b, F) + self.logdet + self.k * np.log(2 * np.pi))


class Classifier:
    def __init__(self, bank, info, version='raw'):
        self.classes = info['classes']
        self.d14 = info['D14']
        self.version = version
        models = np.asarray(bank['model'])
        F = bank['F_raw'] if version == 'raw' else bank['F_free']
        self.Z = np.column_stack([bank['S3c'], bank['S3far'], F])
        self.models = [m for m in self.classes if self.classes[m] in ('S', 'P', 'I') and (models == m).sum() >= 200]
        self.split = {}
        self.fit, self.ref99 = {}, {}
        for m in self.classes:
            idx = np.flatnonzero(models == m)
            n = len(idx)
            self.split[m] = (idx[: int(0.4 * n)], idx[int(0.4 * n): int(0.8 * n)], idx[int(0.8 * n):])
        for m in self.models:
            tr, rf, _ = self.split[m]
            g = CondGauss(self.Z[tr])
            self.fit[m] = g
            Zr = self.Z[rf]
            self.ref99[m] = float(np.quantile(g.new_d2(Zr[:, 0], Zr[:, 1], Zr[:, 2:]), 0.99))
        # priors over S and P models
        self.prior = {}
        for cls in ('S', 'P'):
            ms = [m for m in self.models if self.classes[m] == cls]
            bases = sorted({base_name(m) for m in ms})
            for m in ms:
                nvar = sum(1 for x in ms if base_name(x) == base_name(m))
                self.prior[m] = 0.5 / len(bases) / nvar

    def score(self, Zo):
        a, b, F = Zo[:, 0], Zo[:, 1], Zo[:, 2:]
        known = {m: self.fit[m].known_logpdf(a, b) for m in self.models}
        new = {m: self.fit[m].new_logpdf(a, b, F) for m in self.models}
        SP = [m for m in self.models if m in self.prior]
        L = np.stack([np.log(self.prior[m]) + known[m] + new[m] for m in SP], axis=1)
        W = np.exp(L - L.max(1, keepdims=True))
        W /= W.sum(1, keepdims=True)
        isS = np.array([self.classes[m] == 'S' for m in SP])
        pS = W[:, isS].sum(1)
        # new-part Bayes factor with within-class prior weights
        def cls_new(cls):
            ms = [m for m in SP if self.classes[m] == cls]
            w = np.array([self.prior[m] for m in ms])
            w = w / w.sum()
            Ln = np.stack([new[m] for m in ms], axis=1) + np.log(w)[None]
            mx = Ln.max(1)
            return mx + np.log(np.exp(Ln - mx[:, None]).sum(1))
        lbf = cls_new('S') - cls_new('P')
        # fit check against the best-fitting model among S, P and I
        Lall = np.stack([known[m] + new[m] for m in self.models], axis=1)
        best = np.argmax(Lall, 1)
        d2 = np.stack([self.fit[m].new_d2(a, b, F) for m in self.models], axis=1)
        fit_ok = np.array([d2[i, j] <= self.ref99[self.models[j]] for i, j in enumerate(best)])
        return {'pS': pS, 'log_bf_new': lbf, 'fit_ok': fit_ok, 'best': [self.models[j] for j in best]}

    def verdict(self, Zo):
        s = self.score(Zo)
        v = np.full(len(Zo), 'UNRESOLVED', dtype=object)
        v[(s['pS'] >= POST_THR) & (s['log_bf_new'] >= np.log(BF_THR)) & s['fit_ok']] = 'STATIC-DOMINANT'
        v[(s['pS'] <= 1 - POST_THR) & (s['log_bf_new'] <= -np.log(BF_THR)) & s['fit_ok']] = 'POSITION-DEPENDENT-DOMINANT'
        return v, s


def gate_map(clf, models_arr):
    out = {}
    for c3 in GRID_S3C:
        for cf in GRID_S3F:
            key = f'{c3:.2f}/{cf:.2f}'
            rows, ok_all = {}, True
            for m, cls in clf.classes.items():
                if cls not in ('S', 'P', 'X', 'I'):
                    continue
                ev = clf.split[m][2]
                Zev = clf.Z[ev]
                sel = (np.abs(Zev[:, 0] - c3) <= WIN) & (np.abs(Zev[:, 1] - cf) <= WIN)
                n = int(sel.sum())
                if n < 30:
                    rows[m] = {'n': n}
                    continue
                v, _ = clf.verdict(Zev[sel])
                fS = float((v == 'STATIC-DOMINANT').mean())
                fP = float((v == 'POSITION-DEPENDENT-DOMINANT').mean())
                r = {'n': n, 'static': fS, 'position': fP}
                if cls == 'S':
                    r['pass'] = fS >= 0.70 and fP <= 0.05
                elif cls == 'P':
                    r['pass'] = fP >= 0.70 and fS <= 0.05
                elif cls == 'X' and clf.d14[m] <= 0.15:        # mixtures gated by their own D14 class
                    r['pass'] = fP <= 0.15
                elif cls == 'X' and clf.d14[m] >= 0.5:
                    r['pass'] = fS <= 0.15
                if 'pass' in r and not r['pass']:
                    ok_all = False
                rows[m] = r
            n_eval = sum(1 for m, r in rows.items() if 'pass' in r and clf.classes[m] in ('S', 'P'))
            out[key] = {'gate_pass': ok_all and n_eval > 0, 'n_models_evaluated': n_eval, 'rows': rows}
    return out


def main():
    tag = sys.argv[1]
    bank = dict(np.load(BANK / f'bank_{tag}.npz'))
    info = json.load(open(BANK / f'bank_{tag}.json'))
    res = {'tag': tag, 'classes': info['classes'], 'D14': info['D14']}
    for version in ('raw', 'free'):
        clf = Classifier(bank, info, version)
        gm = gate_map(clf, bank['model'])
        res[version] = {'gate_map': gm}
        print(f'== {tag} [{version}] gate map (S3c / S3far: pass, models evaluated)')
        for key, g in gm.items():
            fails = [f"{m}({r.get('static', 0):.2f}/{r.get('position', 0):.2f})" for m, r in g['rows'].items()
                     if 'pass' in r and not r['pass']]
            print(f'   {key}: {"PASS" if g["gate_pass"] else "fail"}  n_eval {g["n_models_evaluated"]:2d}  '
                  f'{"" if g["gate_pass"] else "failing: " + ", ".join(fails)}')
    # verdict-probability table at points near B's likely values, all models (raw features)
    clf = Classifier(bank, info, 'raw')
    res['verdict_probabilities_raw'] = {}
    for c3, cf in ((0.30, 0.09), (0.32, 0.09), (0.32, 0.12), (0.34, 0.09)):
        tab = {}
        for m in clf.classes:
            ev = clf.split[m][2]
            Zev = clf.Z[ev]
            sel = (np.abs(Zev[:, 0] - c3) <= WIN) & (np.abs(Zev[:, 1] - cf) <= WIN)
            if sel.sum() < 30:
                tab[m] = {'n': int(sel.sum())}
                continue
            v, s = clf.verdict(Zev[sel])
            tab[m] = {'n': int(sel.sum()), 'D14': clf.d14[m], 'class': clf.classes[m],
                      'STATIC': float((v == 'STATIC-DOMINANT').mean()),
                      'POSITION': float((v == 'POSITION-DEPENDENT-DOMINANT').mean()),
                      'UNRESOLVED': float((v == 'UNRESOLVED').mean()), 'fit_fail': float((~s['fit_ok']).mean())}
        res['verdict_probabilities_raw'][f'{c3:.2f}/{cf:.2f}'] = tab
    json.dump(res, open(BANK / f'clf_{tag}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
