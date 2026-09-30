#!/usr/bin/env python3
"""PHASE_777 locked run (see ../PRE_REGISTRATION.md).

  python run777.py              verify the lock; per-channel repeated 7-run excess on Currier B under each channel's
                                exact null (1,000 permutations); per-channel calls; descriptives
  python run777.py --checksums  write results/input_checksums.json (before the lock commit)
  python run777.py --dry        every code path on four DECOYS (an F1 payload of Latin NT letters, an edge chain, a
                                no-payload paragraph-palette plant at Dirichlet alpha 5, and a no-payload line-palette
                                plant at alpha 7)
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
sys.path.insert(0, str(HERE.parent.parent / 'PHASE_776_EIGENSTRUCTURE_EF' / 'scripts'))

ROOT = Path('C:/git/voynich')
LOCK = 'phase777-lock'
PHASE = 'phases/PHASE_777_PAYLOAD_CHANNEL'
OUT = ROOT / PHASE / 'results'
R_B, SEED = 1000, 77700
CH = ('F1', 'F2', 'L1', 'L2', 'GAL')
ARMS = ('F1', 'F2')                             # v2: L1, L2 and GAL are descriptive (see PRE_REGISTRATION.md)
LINE_PALETTE_PCT = 8.0                          # v3 gate: a PRESENT that passes EFq/EFpar is payload-level only if the
                                                # channel's line-entropy reduction is below this (line palettes that read
                                                # PRESENT gave >= 14%; payload decoys and controls -3.0..-0.3%)
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py',
          'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768.py', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768v2.py',
          'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py',
          'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/tu767.py', 'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/syllabify.py',
          'phases/PHASE_764_HUMAN_GIBBERISH_CONTROL/scripts/g764.py',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
          'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py', 'phases/PHASE_774_VARIANT_MERGE/scripts/gen774.py',
          'phases/PHASE_775_BOUNDARY_KEY/scripts/gen775.py', 'phases/PHASE_775_BOUNDARY_KEY/scripts/key775.py',
          'phases/PHASE_776_EIGENSTRUCTURE_EF/scripts/eig776.py')
LOCKED = ('PRE_REGISTRATION.md', 'results/thresholds777.json', 'results/prelock_calib777_design.json',
          'results/prelock_cert777_v1.json', 'results/prelock_cert777.json', 'results/input_checksums.json',
          'scripts/chan777.py',
          'scripts/prelock_calib777.py', 'scripts/prelock_thresholds777.py', 'scripts/prelock_cert777.py',
          'scripts/run777.py', 'scripts/audit/audit777.py', 'scripts/audit/audit777b.py',
          'scripts/audit/chaneff777.py', 'results/audit/audit777.json', 'results/audit/audit777b.json',
          'scripts/audit/confirm777.py', 'results/audit/confirm777.json')
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


def call(z, p, t):
    """v2 two-way call on the arms; 'NONE' vs 'NOT PRESENT (residual)' is descriptive only."""
    if p <= 0.005 and z >= t['tau']:
        return 'PRESENT'
    if p > 0.05 or z <= t['NEG']:
        return 'NONE'
    return 'NOT PRESENT (residual)'


def analyse(lines, sk, tag, X):
    TH = json.load(open(OUT / 'thresholds777.json', encoding='utf-8'))
    t0 = time.time()
    res = X.run(lines, X.GK.ef_groups(sk), R=R_B, seed=SEED, refined=X.par_groups(sk))
    calls = {c: call(res[c]['RPT7']['z'], res[c]['RPT7']['p'], TH[c]) for c in ARMS}
    comp = {c: X.composition_figures(lines, sk, c, SEED + 7) for c in ARMS}
    # interpretation gate (lock audit + confirmation pass): a PRESENT is payload-level only if it survives both refined
    # nulls AND the channel's line-entropy reduction is below LINE_PALETTE_PCT (line palettes pass EFq/EFpar)
    gate = {}
    for c in ARMS:
        q, pr = res[c]['EFq'], res[c]['EFpar']
        ok_q = q['z'] >= TH[c]['tau'] / 2 and q['p'] <= 0.005
        ok_p = pr['z'] >= TH[c]['tau'] / 2 and pr['p'] <= 0.005
        red = comp[c]['line_entropy_pct_reduction']
        if calls[c] != 'PRESENT':
            gate[c] = 'n/a'
        elif ok_q and ok_p and red < LINE_PALETTE_PCT:
            gate[c] = f'payload-level (survives EFq and EFpar; line-entropy reduction {red:.1f}% < {LINE_PALETTE_PCT:.0f}%)'
        elif ok_q and ok_p:
            gate[c] = (f'payload-level or line palette (line-entropy reduction {red:.1f}% >= {LINE_PALETTE_PCT:.0f}%; '
                       'not separable by EFq/EFpar)')
        else:
            gone = [nm for nm, ok in (('a line-position palette (removed by EFq)', ok_q),
                                      ('a paragraph palette (removed by EFpar)', ok_p)) if not ok]
            gate[c] = 'not payload-level: consistent with ' + ' and '.join(gone)
    desc = {c: call(res[c]['RPT7']['z'], res[c]['RPT7']['p'], TH[c]) for c in ('L1', 'L2', 'GAL')}
    log(f'[{tag}] {time.time() - t0:.0f}s')
    for c in CH:
        x, x5 = res[c]['RPT7'], res[c]['RPT5']
        log(f'[{tag}] {c:3s} [{res[c]["_null"]}, movable {res[c]["_cells"]["frac_movable"]:.3f}, {res[c]["_cells"]["symbols"]} symbols] '
            f'RPT7 {x["obs"]}/{x["null_mean"]:.1f} (sd {x["null_sd"]:.1f}) D {x["D"]:+.1f} z {x["z"]:.2f} p {x["p"]:.4f} '
            f'-> {(calls[c] if c in ARMS else desc[c] + " (descriptive)"):13s} [PRESENT z >= {TH[c]["tau"]:.2f}; '
            f'NONE z <= {TH[c]["NEG"]:.2f} or p > 0.05] | '
            f'RPT5 {x5["obs"]}/{x5["null_mean"]:.0f} z {x5["z"]:.2f} p {x5["p"]:.4f} | DIST7 {res[c]["DIST7"]["obs"]}/'
            f'{res[c]["DIST7"]["null_mean"]:.1f}')
        if c in ARMS:
            q, pr = res[c]['EFq'], res[c]['EFpar']
            log(f'[{tag}]     refined nulls: EFq z {q["z"]:.2f} p {q["p"]:.4f} (movable {q["frac_movable"]:.3f}); '
                f'EFpar z {pr["z"]:.2f} p {pr["p"]:.4f} (movable {pr["frac_movable"]:.3f}) -> gate: {gate[c]}')
    for c in ARMS:
        log(f'[{tag}]   composition (post-run descriptive) {c}: line-entropy reduction {comp[c]["line_entropy_pct_reduction"]:.1f}% '
            f'(z {comp[c]["line_entropy_z"]:.1f}); paragraph chi2/df {comp[c]["paragraph_chi2_df"]:.2f}')
    summary = ('summary: START-SYMBOL 7-RUN EXCESS on ' +
               ', '.join(f'{c} [gate: {gate[c]}]' for c in ARMS if calls[c] == 'PRESENT')
               if 'PRESENT' in calls.values() else 'summary: NO START-POSITION PAYLOAD (' +
               ', '.join(f'{c} {calls[c]}' for c in ARMS) + ')')
    log(f'[{tag}] {summary} | descriptive: ' + ', '.join(f'{c} {desc[c]}' for c in desc))
    return {'tag': tag, 'res': res, 'calls': calls, 'gate': gate, 'composition': comp, 'descriptive_calls': desc,
            'summary': summary, 'thresholds': TH, 'R': R_B, 'seed': SEED}


def main():
    global LOGF
    if '--checksums' in sys.argv:
        json.dump({p: sha256(p) for p in INPUTS}, open(OUT / 'input_checksums.json', 'w'), indent=1)
        print('wrote input_checksums.json')
        return
    if not DRY:
        verify_lock()
    import chan777 as X
    import eig776 as X6
    sk = X.HR.b_skeleton()
    if DRY:
        (OUT / 'dryrun').mkdir(exist_ok=True)
        LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
        words = X.G.plaintext_words('NT_la')
        n = X.HR.n_certain(sk)
        decoys = {'DECOY_F1_NTla': X.payload_lines(X.letter_stream(words, n, offset=2 * n), sk, 'F1', 99971)[0],
                  'DECOY_edge2': X6.edge_only_lines(sk, 99972, k=2),
                  'DECOY_PALPAR5_F1': X.palette_plant(sk, 'F1', 5.0, 99973, kind='PALPAR'),
                  'DECOY_PALLINE7_F1': X.palette_plant(sk, 'F1', 7.0, 9703, kind='PALLINE')}
        for tag, lines in decoys.items():
            assert lines != sk['lines']
            r = analyse(lines, sk, tag, X)
            json.dump(r, open(OUT / 'dryrun' / f'{tag}.json', 'w'), indent=1)
        return
    LOGF = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    import platform
    import numpy
    log(f'PHASE_777 locked run; lock {LOCK} verified; inputs verified; R = {R_B}; seed {SEED}')
    log(f'versions: python {platform.python_version()}, numpy {numpy.__version__}')
    r = analyse(sk['lines'], sk, 'B', X)
    json.dump(r, open(OUT / 'phase777_results.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
