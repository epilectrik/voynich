#!/usr/bin/env python3
"""PHASE_769 pre-lock calibration worker (CONTROLS ONLY; synthetic y or control texts, never B's real run lengths by
folio). Usage: python prelock769_worker.py CONDITION  ->  results/calib/CONDITION.json

Conditions: SHARED_<s> (joint H + ZL, with S3-int/S3-cons/S3-k subsets), SHARED_K_<s>, WORDSPEC_<s>, LOCAL_<phi>,
DRIFT_<s>, COPY_<c>, SHARED_PARA_<s>, NEG_TEXT, KAPPA_MINIMS. 200 replicates, 1,000 permutations, 50 splits.
"""
from __future__ import annotations

import os

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'PHASE_768_HIDDEN_REPEATS/scripts'))
import ed769 as E  # noqa: E402
import ed769b as B  # noqa: E402

OUT = E.ROOT / 'phases/PHASE_769_E_DIAL_SETTING/results/calib'
OUT.mkdir(parents=True, exist_ok=True)
NREP, NPERM = 200, 1000
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def setup():
    recs = E.load_b_h()
    amap, leg = B.hf_alignment()
    O = B.add_structure(B.occurrences2(recs, 'e', amap))
    X = B.folio_covariates(recs, O, leg)
    return recs, amap, leg, O, X


def main(cond):
    recs, amap, leg, O, X = setup()
    import zlib
    rng = np.random.default_rng(zlib.crc32(cond.encode()))
    res = {'condition': cond, 'n_rep': NREP, 'n_perm': NPERM, 'reps': []}
    if cond == 'KAPPA_MINIMS':
        H, F = B.track_lines('H'), B.track_lines('F')
        conf = np.zeros((2, 2), int)
        import difflib
        import re
        for key, h in H.items():
            f = F.get(key)
            if f is None:
                continue
            sm = difflib.SequenceMatcher(None, h, f, autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
                    for a, b in zip(h[i1:i2], f[j1:j2]):
                        if '*' in a or '*' in b:
                            continue
                        ra, fa = E.i_runs(a)
                        rb, fb = E.i_runs(b)
                        if fa != fb or len(ra) != len(rb):
                            continue
                        for x, z in zip(ra, rb):
                            conf[int(x >= 2), int(z >= 2)] += 1
        n = conf.sum()
        po = np.trace(conf) / n
        pe = (conf.sum(0) * conf.sum(1)).sum() / n ** 2
        res.update({'confusion_[H1|H2+][F1|F2+]': conf.tolist(), 'kappa': float((po - pe) / (1 - pe)), 'n': int(n)})
        log('minim kappa H-F:', res['kappa'], conf.tolist())
        json.dump(res, open(OUT / f'{cond}.json', 'w'), indent=1)
        return
    if cond == 'NEG_TEXT':
        import hr768 as HR
        import hr768v2 as V
        sk = HR.b_skeleton()
        flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
        n = len(recs)
        streams = {'NAIBBE_P-REC': HR.naibbe_stream('P-REC', 769001, n)[0], 'TIMM': flat(HR.timm_lines(sk, 769201))}
        for s in (769101, 769102, 769103):
            streams[f'HABIT3B_{s}'] = flat(V.habit3b_lines(sk, s))
        res['controls'] = {}
        for name, stream in streams.items():
            rc = E.pour_tokens(recs, stream)
            Oc = B.add_structure(B.occurrences2(rc, 'e', None))
            Xc = B.folio_covariates(rc, Oc, leg)
            r = B.Battery(Oc, Xc).evaluate(Oc['y'], nperm=2000, seed=769600)
            res['controls'][name] = r
            log(name, {k: round(v, 3) for k, v in r.items() if k.startswith('p_') or k in ('S3c', 'n_occ')})
            json.dump(res, open(OUT / f'{cond}.json', 'w'), indent=1, default=float)
        return
    kind, val = cond.rsplit('_', 1)
    val = float(val)
    bat = B.Battery(O, X)
    extra = {}
    if kind == 'SHARED':
        recs_z = E.load_b_zl()
        Oz = B.add_structure(B.occurrences2(recs_z, 'e', None))
        Xz = B.folio_covariates(recs_z, Oz, leg)
        batz = B.Battery(Oz, Xz, paragraph=False)
        extra['int'] = B.Battery(O, X, subset=~O['final'], paragraph=False)
        extra['cons'] = B.Battery(O, X, subset=O['cons'], paragraph=False)
        extra['k'] = B.Battery(O, X, subset=O['after_k'], paragraph=False)
        res['zl_informative'] = int(Oz['informative'].sum())
    if kind == 'SHARED_K':
        extra['k'] = B.Battery(O, X, subset=O['after_k'], paragraph=False)
    for rep in range(NREP):
        if kind == 'SHARED':
            d = {f: v for f, v in zip(O['folio_names'], rng.normal(0, val, len(O['folio_names'])))}
            dz = np.array([d.get(f, rng.normal(0, val)) for f in Oz['folio_names']])
            y = B.draw(B.base_logit(O) + np.array([d[f] for f in O['folio_names']])[O['folio']], rng)
            yz = B.draw(B.base_logit(Oz) + dz[Oz['folio']], rng)
        else:
            mode = {'SHARED_K': 'SHARED_K', 'WORDSPEC': 'WORDSPEC', 'LOCAL': 'LOCAL', 'DRIFT': 'DRIFT', 'COPY': 'COPY',
                    'SHARED_PARA': 'SHARED_PARA'}[kind]
            y = B.plant(O, mode, val, rng)
        row = {'H': bat.evaluate(y, nperm=NPERM, seed=770000 + rep)}
        if kind == 'SHARED':
            row['ZL'] = batz.evaluate(yz, nperm=NPERM, seed=771000 + rep, stats=('S3c',))
        for k, bb in extra.items():
            row[k] = bb.evaluate(y, nperm=NPERM, seed=772000 + rep, stats=('S3c',))
        if kind in ('SHARED_PARA', 'SHARED', 'LOCAL'):
            row['H_S3P_within'] = bat.evaluate(y, nperm=NPERM, seed=773000 + rep, stats=('S3P',),
                                               within_folio_para=True)
        res['reps'].append(row)
        if (rep + 1) % 20 == 0:
            ps = np.array([r['H']['p_S3c'] for r in res['reps']])
            log(f'{cond}: {rep + 1} reps, power S3c(.01) {np.mean(ps <= 0.01):.2f} (.05) {np.mean(ps <= 0.05):.2f}')
            json.dump(res, open(OUT / f'{cond}.json', 'w'), indent=1, default=float)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / f'{cond}.json', 'w'), indent=1, default=float)
    log('done')


if __name__ == '__main__':
    main(sys.argv[1])
