#!/usr/bin/env python3
"""PHASE_776 locked run (see ../PRE_REGISTRATION.md).

  python run776.py              verify the lock; class-pair MI of B under the routing-preserving null EF-K2 (1,000
                                permutations; v2 primary); the call; descriptives (lambda2 under EF-K2 and EF, lambda3,
                                lag-2, EFL, shuffle floor)
  python run776.py --checksums  write results/input_checksums.json (before the lock commit)
  python run776.py --dry        every code path on two DECOYS (an edge-only chain and a class chain)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(HERE))

ROOT = Path('C:/git/voynich')
LOCK = 'phase776-lock'
PHASE = 'phases/PHASE_776_EIGENSTRUCTURE_EF'
OUT = ROOT / PHASE / 'results'
R_B, SEED = 1000, 77600
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py',
          'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768.py', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768v2.py',
          'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py',
          'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/tu767.py',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
          'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py', 'phases/PHASE_774_VARIANT_MERGE/scripts/gen774.py',
          'phases/PHASE_775_BOUNDARY_KEY/scripts/gen775.py', 'phases/PHASE_775_BOUNDARY_KEY/scripts/key775.py',
          'phases/PHASE_764_HUMAN_GIBBERISH_CONTROL/scripts/g764.py',
          'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/syllabify.py')
LOCKED = ('PRE_REGISTRATION.md', 'results/thresholds776.json', 'results/prelock_calib776_design.json',
          'results/prelock_calib776_design2.json', 'results/prelock_cert776_v1.json', 'results/prelock_cert776.json',
          'results/input_checksums.json', 'scripts/eig776.py',
          'scripts/prelock_calib776.py', 'scripts/prelock_thresholds776.py', 'scripts/prelock_cert776.py',
          'scripts/run776.py', 'scripts/audit/audit776.py', 'scripts/audit/audit776_linehomog.py',
          'results/audit/audit776_plants.json', 'results/audit/audit776_linehomog.json')
DRY = '--dry' in sys.argv
LOGF = None


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
        r = subprocess.run(['git', 'cat-file', '-e', f'{LOCK}:{PHASE}/{p}'], cwd=ROOT)
        assert r.returncode == 0, f'{p} is not in the lock tag'
        r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/{p}'], cwd=ROOT)
        assert r.returncode == 0, f'{p} changed since the lock tag'
    r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/scripts'], cwd=ROOT)
    assert r.returncode == 0, 'scripts/ changed since the lock tag'
    r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--', f'{PHASE}/scripts'], cwd=ROOT,
                       capture_output=True, text=True)
    assert not r.stdout.strip(), f'untracked files under scripts/: {r.stdout.split()}'
    sums = json.loads((OUT / 'input_checksums.json').read_text())
    for p in INPUTS:
        assert sha256(p) == sums[p], f'input changed since the lock: {p}'


def call(D, p, th):
    """v2: MI under EF-K2."""
    if p <= 0.005 and D >= th['tau']:
        return 'BEYOND ROUTING'
    if p > 0.05 or D <= th['NEG']:
        return 'ROUTING-REDUCIBLE'
    return 'INDETERMINATE'


def shape_reading(d1, d2, eflk2_p):
    """Pre-declared wording rule on the MI excess (v3, lock-audit edit 2; restricts wording only)."""
    if d1 <= 0:
        return 'not applicable (no positive lag-1 excess)'
    if d2 < 0.5 * d1 and eflk2_p <= 0.05:
        return 'order-like (lag-2 excess < half of lag-1; within-line EFL-K2 MI significant)'
    if eflk2_p > 0.05 and d2 >= 0.75 * d1:
        return 'clustering-like (EFL-K2 MI not significant; lag-2 excess >= 0.75 x lag-1)'
    return 'unresolved'


def lambda2_rule(p):
    """Pre-registered rule for C2061/C2067 (lock-audit edit 1), on lambda2 under EF-K2 at alpha 0.05."""
    if p > 0.05:
        return ('lambda2 not shown beyond boundary rules: annotate C2061/C2067; their "sequence beyond boundary rules" '
                'reading moves to Tier 3 (the measurement against the 5-gram stands)')
    return 'lambda2 significant at 0.05: no demotion of C2061/C2067; record agreement/disagreement with the MI call'


def analyse(lines, sk, tag, X):
    TH = json.load(open(OUT / 'thresholds776.json', encoding='utf-8'))
    t0 = time.time()
    res = X.run(lines, X.GK.ef_groups(sk), R=R_B, seed=SEED)
    mi, mi2, l2, l3, g2, efl = (res['MI'], res['lag2_MI'], res['lambda2'], res['lambda3'], res['lag2_lambda2'],
                                res['EFL_lambda2'])
    eflk2 = res['EFLK2_MI']
    verdict = call(mi['D'], mi['p'], TH)
    log(f'[{tag}] {time.time() - t0:.0f}s | EF-K2 cells {res["EFK2_cells"]["n_cells"]}, movable '
        f'{res["EFK2_cells"]["frac_movable"]:.3f} | EF movable {res["EF_cells"]["frac_movable"]:.3f} | EFL movable '
        f'{res["EFL_cells"]["frac_movable"]:.3f} | EFL-K2 movable {res["EFLK2_cells"]["frac_movable"]:.3f}')
    log(f'[{tag}] PRIMARY class-pair MI under EF-K2: obs {mi["obs"]:.4f} bits, null {mi["null_mean"]:.4f} '
        f'(sd {mi["null_sd"]:.4f}), D {mi["D"]:+.4f}, z {mi["z"]:.1f}, p {mi["p"]:.4f}')
    log(f'[{tag}] CALL: {verdict}   [BEYOND ROUTING if p <= 0.005 and D >= {TH["tau"]:.4f}; ROUTING-REDUCIBLE if '
        f'p > 0.05 or D <= {TH["NEG"]:.4f}]')
    log(f'[{tag}] MI under plain EF (descriptive): null {res["EF_MI"]["null_mean"]:.4f}, D {res["EF_MI"]["D"]:+.4f}, '
        f'p {res["EF_MI"]["p"]:.4f}')
    log(f'[{tag}] lambda2 under EF-K2 (C2061 statistic, descriptive): obs {l2["obs"]:.4f}, null {l2["null_mean"]:.4f} '
        f'(sd {l2["null_sd"]:.4f}), D {l2["D"]:+.4f}, z {l2["z"]:.1f}, p {l2["p"]:.4f} | under plain EF: null '
        f'{res["EF_lambda2"]["null_mean"]:.4f}, D {res["EF_lambda2"]["D"]:+.4f}, p {res["EF_lambda2"]["p"]:.4f} | '
        f'shuffle floor {res["shuffle_floor"]["lambda2"]:.4f}')
    log(f'[{tag}] lambda3 under EF-K2 (descriptive): obs {l3["obs"]:.4f}, null {l3["null_mean"]:.4f}, D {l3["D"]:+.4f}, '
        f'p {l3["p"]:.4f} | floor {res["shuffle_floor"]["lambda3"]:.4f}')
    log(f'[{tag}] C2061/C2067 rule: {lambda2_rule(l2["p"])}')
    log(f'[{tag}] raw-adjacent 49-class MI (descriptive): D {res["raw49_MI"]["D"]:+.4f} p {res["raw49_MI"]["p"]:.4f}; '
        f'50-state MI with UN: D {res["raw50_MI"]["D"]:+.4f} p {res["raw50_MI"]["p"]:.4f}')
    log(f'[{tag}] lag-2 (descriptive): MI D {mi2["D"]:+.4f} p {mi2["p"]:.4f}; lambda2 D {g2["D"]:+.4f} p {g2["p"]:.4f}')
    log(f'[{tag}] within-line EFL-K2 MI (descriptive): null {eflk2["null_mean"]:.4f}, D {eflk2["D"]:+.4f}, p {eflk2["p"]:.4f}'
        f' | EFL lambda2: D {efl["D"]:+.4f}, p {efl["p"]:.4f}')
    log(f'[{tag}] shape (wording only): {shape_reading(mi["D"], mi2["D"], eflk2["p"])}')
    return {'tag': tag, 'res': res, 'call': verdict, 'shape': shape_reading(mi['D'], mi2['D'], eflk2['p']),
            'lambda2_rule': lambda2_rule(l2['p']), 'thresholds': TH, 'R': R_B, 'seed': SEED}


def main():
    global LOGF
    if '--checksums' in sys.argv:
        json.dump({p: sha256(p) for p in INPUTS}, open(OUT / 'input_checksums.json', 'w'), indent=1)
        print('wrote input_checksums.json')
        return
    if not DRY:
        verify_lock()
    import eig776 as X
    sk = X.HR.b_skeleton()
    if DRY:
        (OUT / 'dryrun').mkdir(exist_ok=True)
        LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
        decoys = {'DECOY_edge2': X.edge_only_lines(sk, 99961, k=2), 'DECOY_habit': X.HR.habit_lines(sk, 99962)}
        for tag, lines in decoys.items():
            assert lines != sk['lines']
            r = analyse(lines, sk, tag, X)
            json.dump(r, open(OUT / 'dryrun' / f'{tag}.json', 'w'), indent=1)
        return
    LOGF = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    import platform
    import numpy
    log(f'PHASE_776 locked run; lock {LOCK} verified; inputs verified; R = {R_B}; seed {SEED}')
    log(f'versions: python {platform.python_version()}, numpy {numpy.__version__}')
    r = analyse(sk['lines'], sk, 'B', X)
    json.dump(r, open(OUT / 'phase776_results.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
