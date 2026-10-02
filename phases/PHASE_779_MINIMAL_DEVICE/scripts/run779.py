#!/usr/bin/env python3
"""PHASE_779 locked run (see ../PRE_REGISTRATION.md).

  python run779.py --checksums   write results/input_checksums.json (before the lock commit)
  python run779.py --dry         every code path on 3 members per variant and the evaluation logic (no B values read)
  python run779.py run           B's values (D2-D6 and the predictions) and N members per variant
  python run779.py verdict       inside/outside per variant and statistic; MIN-D; layer map
Stages verify the lock first.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm, skew

HERE = Path(__file__).resolve().parent
os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(HERE))

ROOT = Path('C:/git/voynich')
LOCK = 'phase779-lock'
PHASE = 'phases/PHASE_779_MINIMAL_DEVICE'
OUT = ROOT / PHASE / 'results'
P757 = 'phases/PHASE_757_NAIBBE_RIVAL_PANEL'
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          f'{P757}/scripts/panel_stats.py', f'{P757}/scripts/naibbe_harness.py',
          'phases/PHASE_778_GRILLE_RIVAL_PANEL/scripts/grille778.py',
          'phases/LINE_CONTROL_BLOCK_GRAMMAR/results/02_mandatory_forbidden_bigrams.json')
LOCKED = ('PRE_REGISTRATION.md', 'scripts/mind779.py', 'scripts/run779.py', 'results/c957_bigrams.json',
          'results/input_checksums.json')
VARIANTS = [('R0', False, None), ('R1', False, None), ('R2a', False, None), ('R2', False, None), ('R2', True, None),
            ('R3', False, None), ('R3', True, None), ('R2', False, 'H')]
LADDER = ['R0', 'R1', 'R2a', 'R2', 'R3']            # rungs in order of added rules (without replacement)
N_MEMBERS = 1000
SEED0 = 779_000_000
DS = ['D2', 'D3', 'D4', 'D5', 'D6']
WORKERS = 6
DRY = '--dry' in sys.argv
_W = {}
LOGF = None


def vname(v):
    rung, rep, plant = v
    return rung + ('w' if rep else '') + ('+H' if plant else '')


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(msg, flush=True)
    if LOGF is not None:
        LOGF.write(msg + '\n')
        LOGF.flush()


def sha256(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def verify_lock():
    r = subprocess.run(['git', 'rev-parse', '--verify', LOCK], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, f'lock tag {LOCK} not found'
    for p in LOCKED:
        assert subprocess.run(['git', 'cat-file', '-e', f'{LOCK}:{PHASE}/{p}'], cwd=ROOT).returncode == 0, \
            f'{p} is not in the lock tag'
        assert subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/{p}'], cwd=ROOT).returncode == 0, \
            f'{p} changed since the lock tag'
    assert subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/scripts'], cwd=ROOT).returncode == 0, \
        'scripts/ changed since the lock tag'
    r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--', f'{PHASE}/scripts'], cwd=ROOT,
                       capture_output=True, text=True)
    assert not r.stdout.strip(), f'untracked files under scripts/: {r.stdout.split()}'
    sums = json.loads((OUT / 'input_checksums.json').read_text())
    for p in INPUTS:
        assert sha256(p) == sums[p], f'input changed since the lock: {p}'


def _init():
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    import mind779 as M
    _W['M'] = M
    _W['sk'] = M.skeleton()
    _W['T'] = M.spec_tables(_W['sk'])
    _W['c957'] = M.load_c957()


def member(args):
    vi, m = args
    M, sk, T = _W['M'], _W['sk'], _W['T']
    rung, rep, plant = VARIANTS[vi]
    rng = np.random.default_rng(SEED0 + 10_000 * vi + m)
    lines = M.generate(sk, T, rung, rep, plant, rng)
    st = M.S.all_stats(lines, sk['folio'], rng)
    pr = M.predictions(lines, sk, _W['c957'], rng)
    return {'vi': vi, 'member': m, 'D': [st[d] for d in DS], 'P': [pr[k] for k in M.PRED_KEYS],
            'X': [pr[k] for k in M.EXTRA_KEYS]}


def b_values():
    M, sk = _W['M'], _W['sk']
    rng = np.random.default_rng(779)
    st = M.S.all_stats(sk['lines'], sk['folio'], rng)
    pr = M.predictions(sk['lines'], sk, _W['c957'], rng)
    return {'D': {d: float(st[d]) for d in DS}, 'P': {k: float(pr[k]) for k in M.PRED_KEYS},
            'X': {k: pr[k] for k in M.EXTRA_KEYS}}


def zstar(k):
    return norm.ppf(1 - 0.005 / max(k, 1))


def outside(b, vals, k):
    vals = np.asarray(vals, float)
    vals = vals[~np.isnan(vals)]
    beyond = b < vals.min() or b > vals.max()
    sd = vals.std(ddof=1)
    if sd == 0:
        return bool(beyond)
    return bool(beyond and abs(b - vals.mean()) / sd > zstar(k))


def summ(vals, b):
    vals = np.asarray(vals, float)
    vals = vals[~np.isnan(vals)]
    sd = vals.std(ddof=1)
    return {'mean': float(vals.mean()), 'sd': float(sd), 'min': float(vals.min()), 'max': float(vals.max()),
            'skew': float(skew(vals)) if sd > 0 else 0.0, 'n': int(len(vals)),
            'z_B': float((b - vals.mean()) / sd) if sd > 0 else float('inf') * float(np.sign(b - vals.mean()) or 1.0),
            'rank_B': int((vals < b).sum())}


def stage_run(n_members=N_MEMBERS, tag='run'):
    t0 = time.time()
    _init()
    B = b_values()
    json.dump(B, open(OUT / f'b_values779_{tag}.json', 'w', encoding='utf-8'), indent=1)
    log('B: ' + ', '.join(f'{d} {B["D"][d]:.4f}' for d in DS))
    log('B predictions: ' + ', '.join(f'{k} {v:.4f}' for k, v in B['P'].items()) + ' | ' +
        ', '.join(f'{k} {v}' for k, v in B['X'].items()))
    M = _W['M']
    tasks = [(vi, m) for vi in range(len(VARIANTS)) for m in range(n_members)]
    D = np.full((len(VARIANTS), n_members, len(DS)), np.nan)
    P = np.full((len(VARIANTS), n_members, len(M.PRED_KEYS)), np.nan)
    X = np.full((len(VARIANTS), n_members, len(M.EXTRA_KEYS)), np.nan)
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(member, tasks, chunksize=5)):
            D[r['vi'], r['member']] = r['D']
            P[r['vi'], r['member']] = r['P']
            X[r['vi'], r['member']] = r['X']
            if (i + 1) % 500 == 0:
                log(f'  {tag}: {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)')
                np.savez_compressed(OUT / f'raw779_{tag}_interim.npz', D=D, P=P, X=X)
    np.savez_compressed(OUT / f'raw779_{tag}.npz', D=D, P=P, X=X)
    log(f'{tag} done ({time.time() - t0:.0f}s)')


def stage_verdict(tag='run'):
    _init()
    M = _W['M']
    B = json.load(open(OUT / f'b_values779_{tag}.json', encoding='utf-8'))
    raw = np.load(OUT / f'raw779_{tag}.npz')
    D, P, X = raw['D'], raw['P'], raw['X']
    kD, kP = len(DS), len(M.PRED_KEYS)
    rows = {}
    for vi, v in enumerate(VARIANTS):
        name = vname(v)
        dd = {d: dict(summ(D[vi, :, j], B['D'][d]), outside=outside(B['D'][d], D[vi, :, j], kD)) for j, d in enumerate(DS)}
        pp = {k: dict(summ(P[vi, :, j], B['P'][k]), outside=outside(B['P'][k], P[vi, :, j], kP)) for j, k in enumerate(M.PRED_KEYS)}
        xx = {k: summ(X[vi, :, j], B['X'][k]) for j, k in enumerate(M.EXTRA_KEYS)}
        rows[name] = {'variant': v, 'D': dd, 'P': pp, 'X': xx, 'n_outside_D': sum(x['outside'] for x in dd.values()),
                      'passes_panel': not any(x['outside'] for x in dd.values()),
                      'reproduced': [k for k, x in pp.items() if not x['outside']],
                      'not_reproduced': [k for k, x in pp.items() if x['outside']]}
    ladder = [r for r in LADDER if rows[r]['passes_panel']]
    mind = ladder[0] if ladder else None
    fewest = min(LADDER, key=lambda r: rows[r]['n_outside_D'])
    out = {'B': B, 'z_star': {'D': zstar(kD), 'P': zstar(kP)}, 'N': int(D.shape[1]), 'rows': rows,
           'MIN_D': mind, 'ladder_passing': ladder, 'fewest_outside_rung': fewest,
           'layer_map': {name: {'reproduced': r['reproduced'], 'not_reproduced': r['not_reproduced']} for name, r in rows.items()}}
    json.dump(out, open(OUT / f'verdict779_{tag}.json', 'w', encoding='utf-8'), indent=1)
    log(f"MIN-D: {mind} (passing rungs {ladder}; fewest outside {fewest})")
    for name, r in rows.items():
        log(f"  {name:5s} panel " + ' '.join(f"{d} {r['D'][d]['mean']:+.3f}(z{r['D'][d]['z_B']:+.1f}{'*' if r['D'][d]['outside'] else ''})" for d in DS)
            + f"  outside {r['n_outside_D']}")
        log(f"        pred " + ' '.join(f"{k.split('_')[0]} {r['P'][k]['mean']:+.3f}(z{r['P'][k]['z_B']:+.1f}{'*' if r['P'][k]['outside'] else ''})" for k in M.PRED_KEYS))
    log('B predictions: ' + ', '.join(f"{k.split('_')[0]} {v:.3f}" for k, v in B['P'].items()))


def dry_run():
    global LOGF
    (OUT / 'dryrun').mkdir(exist_ok=True)
    LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
    _init()
    M = _W['M']
    for vi, v in enumerate(VARIANTS):
        for m in range(2):
            r = member((vi, m))
            log(f"[dry] {vname(v):5s} m{m} D " + ' '.join(f'{d} {x:+.3f}' for d, x in zip(DS, r['D'])) +
                ' | P ' + ' '.join(f"{k.split('_')[0]} {x:+.3f}" for k, x in zip(M.PRED_KEYS, r['P'])) +
                ' | X ' + ' '.join(f"{k.split('_')[1]} {x}" for k, x in zip(M.EXTRA_KEYS, r['X'])))
    # evaluation logic on a fake B (the dry run reads no B value): the first member of R0 plays B
    fake = {'D': dict(zip(DS, member((0, 0))['D'])), 'P': dict(zip(M.PRED_KEYS, member((0, 0))['P']))}
    vals = np.array([member((3, m))['D'] for m in range(3)])
    log('[dry] outside logic on 3 R2 members vs a fake B: ' + str({d: outside(fake['D'][d], vals[:, j], 5) for j, d in enumerate(DS)}))
    log('[dry] done')


def main():
    global LOGF
    if '--checksums' in sys.argv:
        json.dump({p: sha256(p) for p in INPUTS}, open(OUT / 'input_checksums.json', 'w'), indent=1)
        print('wrote input_checksums.json')
        return
    if DRY:
        dry_run()
        return
    stage = next((a for a in sys.argv[1:] if not a.startswith('-')), None)
    assert stage in ('run', 'verdict'), 'stage: run | verdict'
    verify_lock()
    LOGF = open(OUT / f'{stage}_log779.txt', 'a', encoding='utf-8')
    log(f'PHASE_779 {stage}; lock {LOCK} verified; inputs verified; {time.strftime("%Y-%m-%d %H:%M:%S")}')
    {'run': stage_run, 'verdict': stage_verdict}[stage]()
    log('done')


if __name__ == '__main__':
    main()
