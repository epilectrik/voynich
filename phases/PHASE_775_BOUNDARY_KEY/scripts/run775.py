#!/usr/bin/env python3
"""PHASE_775 locked run (see ../PRE_REGISTRATION.md).

  python run775.py              verify the lock; key gain G_K1 and G_K2 on Currier B under the header-aware EF null
                                (1,000 permutations); per-arm calls; descriptives
  python run775.py --checksums  write results/input_checksums.json (before the lock commit)
  python run775.py --dry        every code path on two DECOYS (a K1-keyed cipher of NT_la segment 5 and a habit3 run)
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
import gen775 as GK  # noqa: E402
import key775 as K  # noqa: E402

ROOT = Path('C:/git/voynich')
LOCK = 'phase775-lock'
PHASE = 'phases/PHASE_775_BOUNDARY_KEY'
OUT = ROOT / PHASE / 'results'
R_B, SEED = 1000, 77500
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py',
          'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768.py', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768v2.py',
          'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py',
          'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/tu767.py',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
          'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py', 'phases/PHASE_774_VARIANT_MERGE/scripts/gen774.py',
          'phases/PHASE_774_VARIANT_MERGE/scripts/merge774.py')
LOCKED = ('PRE_REGISTRATION.md', 'results/thresholds775.json', 'results/prelock_calib775_design.json',
          'results/prelock_order775_design.json', 'results/prelock_cert775.json', 'results/input_checksums.json',
          'scripts/key775.py', 'scripts/gen775.py', 'scripts/run775.py', 'scripts/prelock_calib775.py',
          'scripts/prelock_thresholds775.py', 'scripts/prelock_cert775.py', 'scripts/prelock_order775.py')
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


def call(G, p, Kn, TH):
    if G >= TH[f'tau_{Kn}'] and p <= 0.005:
        return 'PRESENT'
    if G <= TH[f'NEG_{Kn}'] or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def analyse(lines, sk, tag):
    TH = json.load(open(OUT / 'thresholds775.json', encoding='utf-8'))
    t0 = time.time()
    res = K.run(lines, GK.ef_groups(sk), R=R_B, seed=SEED)
    calls = {Kn: call(res[Kn]['G'], res[Kn]['G_p'], Kn, TH) for Kn in ('K1', 'K2')}
    log(f'[{tag}] {time.time() - t0:.0f}s | EF cells {res["_cells"]["n_cells"]}, movable '
        f'{res["_cells"]["frac_movable"]:.3f}')
    for Kn in ('K0', 'K1', 'K2'):
        x = res[Kn]
        log(f'[{tag}] {Kn}: S {x["S"]:.5f}, EF null {x["null_mean"]:.5f} (sd {x["null_sd"]:.5f}), dS {x["dS"]:+.5f}, '
            f'z {x["z"]:.1f}, p {x["p"]:.4f}')
    for Kn in ('K1', 'K2'):
        x = res[Kn]
        log(f'[{tag}] ARM {Kn}: key gain G {x["G"]:+.5f}, p_G {x["G_p"]:.4f} -> {calls[Kn]}   '
            f'[PRESENT >= {TH["tau_" + Kn]:.5f} with p <= 0.005; NONE <= {TH["NEG_" + Kn]:.5f} or p > 0.05]')
    summary = ('summary: key gain PRESENT (' + ' and '.join(k for k in ('K1', 'K2') if calls[k] == 'PRESENT') + ')'
               if 'PRESENT' in calls.values() else f'summary: K1 {calls["K1"]}, K2 {calls["K2"]}')
    log(f'[{tag}] {summary}')
    return {'tag': tag, 'res': res, 'calls': calls, 'summary': summary, 'thresholds': TH, 'R': R_B, 'seed': SEED}


def main():
    global LOGF
    if '--checksums' in sys.argv:
        json.dump({p: sha256(p) for p in INPUTS}, open(OUT / 'input_checksums.json', 'w'), indent=1)
        print('wrote input_checksums.json')
        return
    sk = GK.G.HR.b_skeleton()
    if DRY:
        (OUT / 'dryrun').mkdir(exist_ok=True)
        LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
        words = GK.G.plaintext_words('NT_la')
        decoys = {'DECOY_keyK1_NTla5': GK.keyed_cipher(GK.G.segment_stream(words, sk, 5), sk, 1, 99951),
                  'DECOY_habit3': GK.G.HR.habit3_lines(sk, 99952)}
        for tag, lines in decoys.items():
            assert lines != sk['lines']
            r = analyse(lines, sk, tag)
            json.dump(r, open(OUT / 'dryrun' / f'{tag}.json', 'w'), indent=1)
        return
    verify_lock()
    LOGF = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    import platform
    import numpy
    log(f'PHASE_775 locked run; lock {LOCK} verified; inputs verified; R = {R_B}; seed {SEED}')
    log(f'versions: python {platform.python_version()}, numpy {numpy.__version__}')
    r = analyse(sk['lines'], sk, 'B')
    json.dump(r, open(OUT / 'phase775_results.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
