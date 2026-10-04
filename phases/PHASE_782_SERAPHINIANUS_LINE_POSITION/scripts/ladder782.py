#!/usr/bin/env python3
"""PHASE_782 plant ladder (confirmation pass S1), on within-line-shuffled CS only: how often each label fires when the
Codex carries a line-position dependence of a given size. Plants in zones I and F (core782.plant_edges, B-tilted,
non-fragment forms), p chosen per target median excess by bisection; 50 replicates per rung; the two-condition rules
of the pre-registration (the opposite-label variants, which can only downgrade a label, are not applied here).

  PHASE782_L=30 python ladder782.py      -> results/ladder782_L30.json (replicates: ladder782_L30.jsonl)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core782 as C  # noqa: E402
import calib782 as K  # noqa: E402

TARGETS = (0.01, 0.02, 0.04, 0.08, 0.15)
N_REP = 50
RES = C.PH / 'results'
TAG = f'_L{K.CFG_L}'
W = {}


def _init(Bc, Bh, I, F):
    K._init()
    W.update({'Bc': Bc, 'Bh': Bh, 'I': I, 'F': F})


def task(args):
    target, p, rep = args
    rng = K.stable_rng(f'ladder-{target}', rep)
    cs = C.load_cs(rng=rng)                                    # within-line shuffled (pre-lock guard)
    pl = C.plant_edges(cs, p, W['I'], W['F'], rng)
    raw = K.CSET(pl, rng).excess(K.R_PERM, rng)
    two = K.CSET(pl, rng, first_n=2).excess(K.R_PERM, rng)
    gd = K.CSET(C.guard(pl, W['frag'] if 'frag' in W else K.W['frag']), rng).excess(K.R_PERM, rng)
    nra = C.auc_block(W['Bh'], raw, rng, B=K.B_BOOT)
    nrb = C.auc_block(W['Bh'], two, rng, B=K.B_BOOT)
    ra = C.auc_block(W['Bc'], raw, rng, B=K.B_BOOT)
    rb = C.auc_block(W['Bc'], gd, rng, B=K.B_BOOT)
    return {'target': target, 'p': p, 'rep': rep, 'raw_median': float(np.median(raw)),
            'label': C.label([nra, nrb], [ra, rb]), 'NR_a_lo': nra['lo'], 'NR_b_lo': nrb['lo'],
            'R_a_hi': ra['hi'], 'R_b_hi': rb['hi']}


def p_for(target, I, F):
    def med(p, n=6):
        vals = []
        for r in range(n):
            rr = K.stable_rng(f'ladp-{target}-{p:.5f}', r)
            cs = C.load_cs(rng=rr)
            vals.append(np.median(K.CSET(C.plant_edges(cs, p, I, F, rr), rr).excess(200, rr)))
        return float(np.median(vals))
    lo, hi = 0.0, 1.0
    for _ in range(9):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if med(mid) < target else (lo, mid)
    return hi


def main():
    from multiprocessing import Pool
    t0 = time.time()
    K._init()
    rng = K.stable_rng('B-clean')
    Bc = K.CSET(K.W['B'], rng).excess(K.R_PERM, rng)
    Bh = K.b_realisations('heavy')
    tI, tF, _ = K.tilts()
    I, F = K.tilted(tI, 1.0), K.tilted(tF, 1.0)
    ps = {t: p_for(t, I, F) for t in TARGETS}
    print('plant p per target', ps, flush=True)
    tasks = [(t, ps[t], r) for t in TARGETS for r in range(N_REP)]
    rows = []
    with Pool(int(os.environ.get('PHASE782_WORKERS', K.WORKERS)), initializer=_init, initargs=(Bc, Bh, I, F)) as pool, \
            open(RES / f'ladder782{TAG}.jsonl', 'w', encoding='utf-8') as fh:
        for r in pool.imap_unordered(task, tasks, chunksize=2):
            fh.write(json.dumps(r) + '\n')
            fh.flush()
            rows.append(r)
    out = {'L': K.CFG_L, 'B_clean_median': float(np.median(Bc)), 'B_heavy_median': float(np.median(np.concatenate(Bh))),
           'rungs': {}}
    for t in TARGETS:
        rr = [x for x in rows if x['target'] == t]
        labs = [x['label'] for x in rr]
        out['rungs'][str(t)] = {'p': ps[t], 'n': len(rr), 'planted_median': float(np.median([x['raw_median'] for x in rr])),
                                'NOT_REACHED': labs.count('NOT REACHED') / len(rr),
                                'REACHED': labs.count('REACHED') / len(rr),
                                'UNRESOLVED': labs.count('UNRESOLVED') / len(rr)}
    out['runtime_s'] = round(time.time() - t0, 1)
    json.dump(out, open(RES / f'ladder782{TAG}.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(out, indent=1), flush=True)


if __name__ == '__main__':
    main()
