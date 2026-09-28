#!/usr/bin/env python3
"""PHASE_755 — C2031/C2032 reconciliation. See ../PRE_REGISTRATION.md (locked, commit e588555).

Canonical C2031 method (paragraphs, e-depth class 0/1/2+, same-class rate at lag L minus the exact
within-paragraph shuffle expectation). Period-2 index D = excess(lag2) - excess(lag1).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology  # noqa: E402

OUT = ROOT / 'phases/PHASE_755_C2031_C2032_RECONCILIATION/results'
OUT.mkdir(parents=True, exist_ok=True)
SEED, NBOOT = 755, 2000
MATCHED_S = {"f103r", "f103v", "f106r", "f106v", "f107r", "f108r", "f108v", "f111r", "f112r", "f112v", "f113r",
             "f113v", "f114r", "f114v", "f115r", "f115v", "f116r"}
MATCHED_B = {"f75r", "f76r", "f76v", "f77r", "f77v", "f78v", "f79r", "f79v", "f80r", "f81v", "f82r", "f82v", "f83r",
             "f84r", "f84v"}
SECTION_B_ALL = {f"f{n}{rv}" for n in range(75, 87) for rv in ("r", "v")}
SECTION_S_ALL = {f"f{n}{rv}" for n in range(103, 117) for rv in ("r", "v")}
STRATA = [(3, 30), (30, 60), (60, 120), (120, 10_000)]

morph = Morphology()
cache = {}


def ecls(tok):
    if tok not in cache:
        try:
            e = morph.atomize(tok).e_depth
        except Exception:
            e = None
        cache[tok] = None if e is None else ('0' if e == 0 else '1' if e == 1 else '2')
    return cache[tok]


def paragraphs():
    tx = Transcript()
    out = defaultdict(list)
    cur = defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word or t.is_uncertain or t.language != 'B':
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        if t.par_initial and cur[t.folio]:
            out[t.folio].append(cur[t.folio])
            cur[t.folio] = []
        cur[t.folio].append(t.word.lower())
    for f, p in cur.items():
        if p:
            out[f].append(p)
    return out


def para_stats(p):
    """Per-paragraph contributions for lags 1 and 2: (pairs, observed same, expected same)."""
    cls = [ecls(w) for w in p]
    res = {}
    valid = [c for c in cls if c is not None]
    n = len(valid)
    cnt = Counter(valid)
    p_same = sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1)) if n > 1 else 0.0
    for lag in (1, 2):
        pairs = same = 0
        for i in range(len(cls) - lag):
            a, b = cls[i], cls[i + lag]
            if a is not None and b is not None:
                pairs += 1
                same += a == b
        res[lag] = (pairs, same, pairs * p_same)
    return res


def aggregate(stats):
    out = {}
    for lag in (1, 2):
        P = sum(s[lag][0] for s in stats)
        O = sum(s[lag][1] for s in stats)
        E = sum(s[lag][2] for s in stats)
        out[lag] = (O - E) / P if P else float('nan')
    return out


def D_of(stats):
    a = aggregate(stats)
    return a[2] - a[1], a[1], a[2]


def boot(stats, rng):
    n = len(stats)
    Ds = np.empty(NBOOT)
    for b in range(NBOOT):
        idx = rng.integers(0, n, n)
        Ds[b] = D_of([stats[i] for i in idx])[0]
    return Ds


def summarize(stats, rng):
    if len(stats) < 2:
        return {'n_paragraphs': len(stats)}
    D, e1, e2 = D_of(stats)
    Ds = boot(stats, rng)
    r21 = e2 / e1 if abs(e1) > 1e-9 else None
    return {'n_paragraphs': len(stats), 'excess_lag1': round(e1, 5), 'excess_lag2': round(e2, 5),
            'D': round(D, 5), 'D_ci95': [round(float(np.quantile(Ds, .025)), 5), round(float(np.quantile(Ds, .975)), 5)],
            'r21_for_reference': round(r21, 3) if r21 is not None else None, '_boot': Ds}


def main():
    rng = np.random.default_rng(SEED)
    fp = paragraphs()
    pops = {'Section_B_all': SECTION_B_ALL, 'matched_B': MATCHED_B, 'Section_S_all': SECTION_S_ALL,
            'matched_S': MATCHED_S, 'all_Currier_B': set(fp)}
    stats_by = {}
    for name, folios in pops.items():
        stats_by[name] = [(len(p), para_stats(p)) for f in sorted(folios) for p in fp.get(f, [])]
    results = {'pooled': {}, 'strata': {}}
    for name, lst in stats_by.items():
        results['pooled'][name] = summarize([s for _, s in lst], rng)
    for lo, hi in STRATA:
        key = f'{lo}-{hi - 1 if hi < 10_000 else "inf"}'
        results['strata'][key] = {}
        for name, lst in stats_by.items():
            sel = [s for L, s in lst if lo <= L < hi]
            results['strata'][key][name] = summarize(sel, rng) if len(sel) >= 2 else {'n_paragraphs': len(sel)}

    def diff(a, b):
        if '_boot' not in a or '_boot' not in b:
            return None
        d = a['_boot'] - b['_boot']
        return {'D_B_minus_D_S': round(a['D'] - b['D'], 5),
                'ci95': [round(float(np.quantile(d, .025)), 5), round(float(np.quantile(d, .975)), 5)]}

    comparisons = {'pooled': diff(results['pooled']['Section_B_all'], results['pooled']['Section_S_all'])}
    qualifying = []
    for key, grp in results['strata'].items():
        a, b = grp['Section_B_all'], grp['Section_S_all']
        comp = diff(a, b)
        comparisons[key] = comp
        if a.get('n_paragraphs', 0) >= 8 and b.get('n_paragraphs', 0) >= 8 and comp:
            qualifying.append((key, comp['ci95'][0] > 0))
    n_pos = sum(ok for _, ok in qualifying)
    pooled_ex0 = comparisons['pooled'] and comparisons['pooled']['ci95'][0] > 0
    if n_pos >= 2:
        verdict = 'SECTION EFFECT SURVIVES LENGTH CONTROL'
    elif pooled_ex0:
        verdict = 'LENGTH-CONFOUNDED'
    else:
        verdict = 'NO SECTION EFFECT'

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if k != '_boot'}
        return o

    out = {'phase': 'PHASE_755', 'pre_registration_commit': 'e588555', 'n_boot': NBOOT, 'seed': SEED,
           'results': strip(results), 'section_B_vs_S': comparisons,
           'qualifying_strata': [{'stratum': k, 'ci_excludes_0_positive': ok} for k, ok in qualifying],
           'verdict': verdict}
    json.dump(out, open(OUT / 'c2031_reconciliation.json', 'w', encoding='utf-8'), indent=1)

    print('POOLED')
    for name, r in out['results']['pooled'].items():
        print(f"  {name:<14} n={r['n_paragraphs']:4d}  lag1={r.get('excess_lag1')}  lag2={r.get('excess_lag2')}  "
              f"D={r.get('D')} CI={r.get('D_ci95')}  r21={r.get('r21_for_reference')}")
    for key, grp in out['results']['strata'].items():
        print(f'STRATUM {key}')
        for name in ('Section_B_all', 'matched_B', 'Section_S_all', 'matched_S', 'all_Currier_B'):
            r = grp[name]
            print(f"  {name:<14} n={r['n_paragraphs']:4d}  D={r.get('D')} CI={r.get('D_ci95')}  r21={r.get('r21_for_reference')}")
        print(f"  B-S: {comparisons[key]}")
    print(f"POOLED B-S: {comparisons['pooled']}")
    print(f"qualifying strata: {qualifying}")
    print(f"VERDICT (locked rules): {verdict}")


if __name__ == '__main__':
    main()
