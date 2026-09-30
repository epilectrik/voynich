#!/usr/bin/env python3
"""PHASE_774 locked run (see ../PRE_REGISTRATION.md).

  python run774.py              verify the lock; the two pre-registered arms on Currier B under the exact edge-frame
                                null (EF, 1,000 permutations); per-arm calls (v3: T confirmatory,
                                M one-sided); pre-specified descriptives
  python run774.py --checksums  write results/input_checksums.json (before the lock commit)
  python run774.py --dry        every code path on two DECOY corpora (a whole-word code of Mesue and a no-message
                                generator) instead of B; writes results/dryrun/
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(HERE))
import ef774 as E  # noqa: E402
import gen774 as G  # noqa: E402
import merge774 as M  # noqa: E402

ROOT = Path('C:/git/voynich')
LOCK = 'phase774-lock'
PHASE = 'phases/PHASE_774_VARIANT_MERGE'
OUT = ROOT / PHASE / 'results'
R_B, SEED = 1000, 77400
NS = (3, 4, 5, 6)
REPS = ('TOK', 'MID', 'MIDn1')
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py',
          'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768.py', 'phases/PHASE_768_HIDDEN_REPEATS/scripts/hr768v2.py',
          'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py',
          'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/tu767.py',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
LOCKED = ('PRE_REGISTRATION.md', 'results/thresholds774.json', 'results/prelock_cert.json',
          'results/prelock_recert.json', 'results/input_checksums.json', 'scripts/ef774.py', 'scripts/merge774.py',
          'scripts/gen774.py', 'scripts/run774.py', 'scripts/prelock_thresholds.py', 'scripts/prelock_cert.py',
          'scripts/prelock_recert.py', 'scripts/audit/audit_stress.py', 'results/audit/audit_stress.json',
          'results/prelock_recovery.json', 'scripts/prelock_recovery.py')
CAL_RANGES = {'TOK5_null_no_message_102_runs': (0.0, 0.13), 'MID5_null_B_like_corpus_wide': (14.6, 27.2),
              'MID5_null_section_fitted': (31.4, 44.7)}
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


def call_T(d5, p, th):
    """T arm (v2, lock-audit E3): half-integer boundaries on the excess count."""
    if d5 >= th['tau_T'] and p <= 0.01:
        return 'PRESENT'
    if d5 < th['NONE_T_lt'] or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def call_M(x5, p, th):
    """M arm (v3, one-sided): PRESENT is registrable; anything else is 'not PRESENT' (descriptive, no exclusion
    claim). The v2 three-way label is kept as a descriptive field (label_M_v2)."""
    if x5 >= th['tau_M'] and p <= 0.01:
        return 'PRESENT'
    return 'not PRESENT'


def label_M_v2(x5, p, th):
    """Descriptive position of X5 against the no-message ceiling; never a NONE claim (v3.1, E2)."""
    if x5 >= th['tau_M'] and p <= 0.01:
        return 'PRESENT'
    if x5 <= th['NEG_M'] or p > 0.05:
        return 'at or below the no-message ceiling (descriptive)'
    return 'between the ceiling and the PRESENT bar (descriptive)'


def repeated_list(lines, folios, fn, n):
    """Every sequence of n consecutive certain tokens (within a line) whose representation occurs >= 2 times."""
    occ = defaultdict(list)
    for ln, f in zip(lines, folios):
        for i in range(len(ln) - n + 1):
            w = ln[i:i + n]
            if any(x is None for x in w):
                continue
            occ[tuple(fn(x) for x in w)].append((f, ' '.join(w)))
    out = []
    for k, v in occ.items():
        if len(v) >= 2:
            out.append({'rep': ' '.join(k), 'count': len(v), 'folios': sorted({f for f, _ in v}),
                        'tokens': [t for _, t in v]})
    return sorted(out, key=lambda r: (-r['count'], r['rep']))


def analyse(lines, folios, tag):
    TH = json.load(open(OUT / 'thresholds774.json', encoding='utf-8'))['thresholds']
    t0 = time.time()
    C = E.Corpus(lines, folios, sig=E.sig_fl, ns=NS)
    reps = {k: C.rep_array(M.STATIC_MERGES[k]) for k in REPS}
    res = E.ef_test(C, reps, R_B, SEED)
    t5, m5 = res['TOK']['RPT5'], res['MID']['RPT5']
    D5 = t5['obs'] - t5['null_mean']
    T = call_T(D5, t5['p'], TH)
    Mv = call_M(m5['X'], m5['p'], TH)
    # the per-arm calls are the result (E5); this summary line is not a separate verdict
    if 'PRESENT' in (T, Mv):
        verdict = 'summary: PHRASE REPEATS PRESENT (' + ' and '.join(a for a, v in (('T', T), ('M', Mv))
                                                                     if v == 'PRESENT') + ')'
    else:
        verdict = f'summary: T {T}, M {Mv}'
    log(f'[{tag}] {time.time() - t0:.0f}s | tokens {int((C.tok >= 0).sum())}, types {len(C.vocab)}, '
        f'cells {C.n_cells}, movable {C.frac_movable:.3f}')
    log(f'[{tag}] T arm (TOK, n = 5): obs {t5["obs"]}, null mean {t5["null_mean"]:.2f} (sd {t5["null_sd"]:.2f}), '
        f'D5 {D5:.2f}, p {t5["p"]:.4f} -> {T}   [PRESENT >= {TH["tau_T"]:.1f}, NONE < {TH["NONE_T_lt"]:.1f}]')
    log(f'[{tag}] M arm (MID, n = 5): obs {m5["obs"]}, null mean {m5["null_mean"]:.2f} (sd {m5["null_sd"]:.2f}), '
        f'X5 {m5["X"]:.3f}, p {m5["p"]:.4f} -> {Mv}   [PRESENT >= {TH["tau_M"]:.2f}; descriptive v2 range: '
        f'{label_M_v2(m5["X"], m5["p"], TH)}]')
    log(f'[{tag}] T CALL: {T} | M CALL: {Mv} | {verdict}')
    nm = {'TOK5_null_mean': t5['null_mean'], 'MID5_null_mean': m5['null_mean'], 'calibration_ranges': CAL_RANGES}
    log(f'[{tag}] null means (O1): TOK5 {t5["null_mean"]:.2f} (no-message runs 0-0.13); MID5 '
        f'{m5["null_mean"]:.2f} (B-like no-message 14.6-27.2, section-fitted 31.4-44.7; M-arm PRESENT power assumes '
        f'<= ~27)')
    # descriptives (pre-specified; no verdict)
    desc = {}
    for k in REPS:
        for nn in NS:
            for st in (f'RPT{nn}', f'RPTi{nn}', f'RPTx{nn}', f'DIST{nn}', f'RPT{nn}_r20', f'RPT{nn}_r50'):
                x = res[k][st]
                desc[f'{k}_{st}'] = {'obs': x['obs'], 'null_mean': round(x['null_mean'], 3), 'X': round(x['X'], 3),
                                     'D': round(x['obs'] - x['null_mean'], 3), 'p': x['p']}
    for k in REPS:
        log(f'[{tag}]   {k:6s} ' + ' | '.join(
            f'n{nn} {res[k][f"RPT{nn}"]["obs"]}/{res[k][f"RPT{nn}"]["null_mean"]:.1f} X {res[k][f"RPT{nn}"]["X"]:.2f}'
            f' p {res[k][f"RPT{nn}"]["p"]:.3f}' for nn in NS))
    C2 = E.Corpus(lines, folios, sig=E.sig_fl2, ns=(5,))
    reps2 = {k: C2.rep_array(M.STATIC_MERGES[k]) for k in ('TOK', 'MID')}
    r2 = E.ef_test(C2, reps2, R_B, SEED + 1)
    desc['EF_fl2'] = {'TOK_D5': r2['TOK']['RPT5']['obs'] - r2['TOK']['RPT5']['null_mean'],
                      'TOK_p': r2['TOK']['RPT5']['p'], 'MID_X5': r2['MID']['RPT5']['X'],
                      'MID_p': r2['MID']['RPT5']['p'], 'cells': C2.n_cells, 'movable': C2.frac_movable}
    log(f'[{tag}]   EF with last-two-glyph edges: TOK D5 {desc["EF_fl2"]["TOK_D5"]:.2f} '
        f'(p {desc["EF_fl2"]["TOK_p"]:.4f}); MID X5 {desc["EF_fl2"]["MID_X5"]:.3f} (p {desc["EF_fl2"]["MID_p"]:.4f})')
    lists = {'TOK5': repeated_list(lines, folios, M.STATIC_MERGES['TOK'], 5),
             'MID5': repeated_list(lines, folios, M.STATIC_MERGES['MID'], 5)}
    log(f'[{tag}]   repeated 5-grams: TOK {len(lists["TOK5"])} distinct, MID {len(lists["MID5"])} distinct')
    for r in lists['TOK5'][:15]:
        log(f'[{tag}]     TOK  x{r["count"]} {r["rep"]}  {r["folios"]}')
    for r in lists['MID5'][:15]:
        log(f'[{tag}]     MID  x{r["count"]} {r["rep"]}  {r["folios"]}  e.g. {r["tokens"][:2]}')
    for k in ('TOK', 'MID'):
        x = res[k]['RPTi5']
        log(f'[{tag}]   interior-only (O2) {k} n5: {x["obs"]}/{x["null_mean"]:.2f} X {x["X"]:.2f} '
            f'D {x["obs"] - x["null_mean"]:.2f} p {x["p"]:.3f}')
    return {'tag': tag, 'null_means': nm,
            'T': {'obs': t5['obs'], 'null_mean': t5['null_mean'], 'null_sd': t5['null_sd'], 'D5': D5,
                              'p': t5['p'], 'call': T},
            'M': {'obs': m5['obs'], 'null_mean': m5['null_mean'], 'null_sd': m5['null_sd'], 'X5': m5['X'],
                  'p': m5['p'], 'call': Mv, 'v2_range_descriptive': label_M_v2(m5['X'], m5['p'], TH)},
            'verdict': verdict, 'thresholds': TH, 'descriptives': desc, 'repeated_5grams': lists,
            'tokens': int((C.tok >= 0).sum()), 'types': len(C.vocab), 'cells': C.n_cells,
            'frac_movable': C.frac_movable, 'R': R_B, 'seed': SEED}


def main():
    global LOGF
    if '--checksums' in sys.argv:
        json.dump({p: sha256(p) for p in INPUTS}, open(OUT / 'input_checksums.json', 'w'), indent=1)
        print('wrote input_checksums.json')
        return
    sk = G.HR.b_skeleton()
    if DRY:
        (OUT / 'dryrun').mkdir(exist_ok=True)
        LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
        words = G.plaintext_words('LAT_mesue')
        decoys = {'DECOY_CBB_mesue': G.bform_codebook(words, sk, 99901, G.plain_stream(words, sk))[0],
                  'DECOY_habit3': G.HR.habit3_lines(sk, 99902)}
        for tag, lines in decoys.items():
            r = analyse(lines, sk['folios'], tag)
            json.dump(r, open(OUT / 'dryrun' / f'{tag}.json', 'w'), indent=1)
        return
    verify_lock()
    LOGF = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    import platform
    import numba
    import numpy
    log(f'PHASE_774 locked run; lock {LOCK} verified; inputs verified; R = {R_B}; seed {SEED}')
    log(f'versions: python {platform.python_version()}, numpy {numpy.__version__}, numba {numba.__version__}')
    r = analyse(sk['lines'], sk['folios'], 'B')
    json.dump(r, open(OUT / 'phase774_results.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
