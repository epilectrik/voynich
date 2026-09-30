"""Analyse sim770v2 outputs (synthetic only). Gate rates under the v2 class rule and under an R14-based rule; stacking."""
import glob
import json

import numpy as np

SP = r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad'
V = {}
for f in glob.glob(SP + r'\sim770v2_out_*.json'):
    V.update(json.load(open(f))['variants'])
names = [n for n in ['M1', 'M2b4', 'M7', 'M3', 'M4_95', 'M4_97', 'M4_99', 'M6_97', 'M8_10', 'M8_20', 'M8_40',
                     'MIX25', 'MIX50', 'MIX75'] if n in V]
print('variants:', names)
for n in names:
    v = V[n]
    print('%-6s cls %s amp %.3f  S3 %.3f  S3far %.3f  ratio %.2f  R14 %.2f' %
          (n, v['cls'], v['amp'], np.mean(v['s3']), np.mean(v['s3far']), np.mean(v['s3far']) / np.mean(v['s3']),
           v['R14']))


def fit(X):
    mu = X.mean(0)
    C = np.cov(X.T) + 1e-10 * np.eye(X.shape[1])
    return mu, np.linalg.inv(C), np.linalg.slogdet(C)[1]


def loglik(x, par):
    mu, Pi, ld = par
    d = x - mu
    return -0.5 * np.einsum('ij,jk,ik->i', d, Pi, d) - 0.5 * ld


def priors(cls_of, grp_of, members):
    pr = {}
    for c in ('S', 'P'):
        mem = [m for m in members if cls_of[m] == c]
        groups = sorted(set(grp_of[m] for m in mem))
        for m in mem:
            ng = len(groups)
            nv = sum(1 for x in mem if grp_of[x] == grp_of[m])
            pr[m] = 0.5 / ng / nv
    return pr


def classify(members, cls_of, grp_of, train, test_sets):
    pr = priors(cls_of, grp_of, members)
    pars = {m: fit(train[m]) for m in members}
    out = {}
    for n, X in test_sets.items():
        ll = np.array([loglik(X, pars[m]) + np.log(pr[m]) for m in members])  # (M, n)
        mx = ll.max(0)
        w = np.exp(ll - mx)
        pS = w[[cls_of[m] == 'S' for m in members]].sum(0) / w.sum(0)
        out[n] = pS
    return out


def split_idx(n, sel=None):
    idx = np.arange(n) if sel is None else np.flatnonzero(sel)
    h = len(idx) // 2
    return idx[:h], idx[h:]


def gate_report(label, members, cls_of, grp_of, analysis='primary', cond=None):
    train, test = {}, {}
    for n in names:
        F = np.array(V[n]['F'][analysis])
        sel = None
        if cond is not None:
            s3 = np.array(V[n]['s3']); sf = np.array(V[n]['s3far'])
            sel = (np.abs(s3 - cond[0]) <= cond[2]) & (np.abs(sf - cond[1]) <= cond[2])
        tr, te = split_idx(len(F), sel)
        train[n], test[n] = F[tr], F[te]
    if any(len(train[m]) < 30 for m in members):
        print(label, 'too few accepted:', {m: len(train[m]) for m in members})
    post = classify(members, cls_of, grp_of, train, test)
    print('---', label, '| n_test', {n: len(test[n]) for n in names})
    for n in names:
        pS = post[n]
        own = V[n]['cls']
        role = 'in prior' if n in members else 'probe'
        if own == 'S' and n in members:
            print('  %-6s S %-8s own(S>=.8) %.2f  wrong(P>=.8) %.2f  unres %.2f' %
                  (n, role, np.mean(pS >= 0.8), np.mean(pS <= 0.2), np.mean((pS > 0.2) & (pS < 0.8))))
        elif own == 'P' and n in members:
            print('  %-6s P %-8s own(P>=.8) %.2f  wrong(S>=.8) %.2f  unres %.2f' %
                  (n, role, np.mean(pS <= 0.2), np.mean(pS >= 0.8), np.mean((pS > 0.2) & (pS < 0.8))))
        else:
            print('  %-6s %s %-8s S>=.8 %.2f  P>=.8 %.2f  unres %.2f' %
                  (n, own, role, np.mean(pS >= 0.8), np.mean(pS <= 0.2), np.mean((pS > 0.2) & (pS < 0.8))))
    return post


V['M8_10']['cls'] = 'D'  # degenerate: needed an 18-logit level SD to approach S3 0.32
D14 = {'M1': 0.00, 'M2b4': 0.11, 'M7': 0.29, 'M3': 0.74, 'M4_95': 0.66, 'M4_97': 0.48, 'M4_99': 0.20, 'M6_97': 0.48,
       'M8_10': 0.87, 'M8_20': 0.65, 'M8_40': 0.44, 'MIX25': 0.17, 'MIX50': 0.35, 'MIX75': 0.54}
cls_v2 = {n: V[n]['cls'] for n in names}
grp = {n: V[n]['grp'] for n in names}
mem_v2 = [n for n in names if cls_v2[n] in 'SP']
gate_report('v2 classes, unconditioned', mem_v2, cls_v2, grp)
gate_report('v2 classes, conditioned on S3 0.32 and S3far 0.095 (+-0.05)', mem_v2, cls_v2, grp, cond=(0.32, 0.095, 0.05))

# D14 rule: S if D14 <= 0.15, P if D14 >= 0.5, else intermediate (probe only); mixtures stay probes
cls_r = {}
for n in names:
    d = D14[n]
    cls_r[n] = V[n]['cls'] if V[n]['cls'] in 'XD' else ('S' if d <= 0.15 else ('P' if d >= 0.5 else 'I'))
print('D14 classes:', cls_r)
mem_r = [n for n in names if cls_r[n] in 'SP']
for n in names:
    V[n]['cls_orig'] = V[n]['cls']
    V[n]['cls'] = cls_r[n] if cls_r[n] in 'SP' else V[n]['cls']
gate_report('D14 classes (0.15 / 0.5), unconditioned', mem_r, cls_r, grp)
gate_report('D14 classes, conditioned', mem_r, cls_r, grp, cond=(0.32, 0.095, 0.05))

# stacking under the R14 rule and under v2
for label, mem, cmap in (('v2', mem_v2, cls_v2), ('D14', mem_r, cls_r)):
    for n in names:
        V[n]['cls'] = cmap[n] if cmap[n] in 'SP' else V[n]['cls_orig']
    posts = {}
    for an in ('primary', 'drop_page', 'finer_cells', 'drop5'):
        train, test = {}, {}
        for n in names:
            F = np.array(V[n]['F'][an])
            tr, te = split_idx(len(F))
            train[n], test[n] = F[tr], F[te]
        posts[an] = classify(mem, cmap, grp, train, test)
    print('--- stacking (%s classes, unconditioned): own-class >= 0.8 in primary vs in all four analyses' % label)
    for n in mem:
        c = cmap[n]
        ok = {an: (posts[an][n] >= 0.8) if c == 'S' else (posts[an][n] <= 0.2) for an in posts}
        opp = {an: (posts[an][n] <= 0.2) if c == 'S' else (posts[an][n] >= 0.8) for an in posts}
        allok = np.all([ok[a] for a in ok], axis=0)
        noflip = ok['primary'] & ~np.any([opp[a] for a in opp], axis=0)
        pri = ok['primary']
        print('  %-6s %s primary %.2f | all four %.2f | primary & no flip %.2f | P(all|primary) %.2f' %
              (n, c, pri.mean(), allok.mean(), noflip.mean(), allok.sum() / max(pri.sum(), 1)))
