#!/usr/bin/env python3
"""PHASE_778 locked run: rival-generator panel II, the table-and-grille method (see ../PRE_REGISTRATION.md).

  python run778.py --checksums   write results/input_checksums.json (before the lock commit)
  python run778.py --dry         every code path on 2 variants x 3 members + the evaluation logic (no verdict)
  python run778.py controls      positive-control certification (M1, G-EDGE; B + noise reference); B's D2-D6
  python run778.py panel         the declared variants (families x noise), N members each
  python run778.py verdict       outside tests, rerun rule, verdict (as published / steelman), PARTIAL, descriptives
Stages verify the lock first.
"""
from __future__ import annotations

import hashlib
import itertools
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
import fit778 as F  # noqa: E402

ROOT = Path('C:/git/voynich')
LOCK = 'phase778-lock'
PHASE = 'phases/PHASE_778_GRILLE_RIVAL_PANEL'
OUT = ROOT / PHASE / 'results'
P757 = 'phases/PHASE_757_NAIBBE_RIVAL_PANEL'
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          f'{P757}/scripts/naibbe_harness.py', f'{P757}/scripts/panel_stats.py', f'{P757}/results/noise_model.json',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
LOCKED = ('PRE_REGISTRATION.md', 'scripts/grille778.py', 'scripts/gates778.py', 'scripts/fit778.py', 'scripts/run778.py',
          'results/gates778.json', 'results/b_surface778.json', 'results/fit778.json', 'results/input_checksums.json')
NOISES = ['V0', 'V1']
N_MEMBERS, N_CTRL, N_REF = 1000, 1000, 50
RERUN_OFFSET = 5_000_000
DS = ['D2', 'D3', 'D4', 'D5', 'D6']
DESC = ['types', 'hapax_type_fraction', 'zipf_slope', 'mean_token_length', 'duplicate_lines', 'max_identical_run',
        'erun_class_same_lag1', 'max_qok_in_10_window']
BUILT_IN = {'M1': {'D5', 'D6'}, 'GEDGE': {'D2', 'D6'}}
CTRL_SEED = {'M1': 778_900_000, 'GEDGE': 778_910_000, 'BNOISE': 778_920_000}
WORKERS = 6
STEELMAN_ORDERS = {'chain'}            # beyond the published description (see PRE_REGISTRATION.md)
DRY = '--dry' in sys.argv
_W = {}
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


# ================================================================================================ variants
def variants():
    fit = json.load(open(OUT / 'fit778.json', encoding='utf-8'))['families']
    out = []
    for fam in F.FAMILIES:
        name = F.family_name(fam)
        best = fit[name]['best']
        for noise in NOISES:
            out.append({'name': f'{name}/{noise}', 'family': fam, 'cfg': best['cfg'], 'noise': noise,
                        'group': 'steelman' if fam['order'] in STEELMAN_ORDERS else 'published',
                        'fit_distance': best['distance']})
    return out


# ================================================================================================ workers
def _init():
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    import grille778 as X
    _W['X'] = X
    sk = X.skeleton()
    _W['sk'] = sk
    _W['inv'] = {p: X.inventory(sk, p) for p in F.PARSERS}
    _W['noise'] = X.H757.noise_model()
    _W['m1'] = X.H757.M1(sk['lines'])
    _W['ge'] = X.H757.GEdge(sk['lines'])
    _W['variants'] = variants() if (OUT / 'fit778.json').exists() else []


def _pack(st):
    return {'D': [st[d] for d in DS], 'desc': [st['desc'][k] for k in DESC], 'aux': st['aux']}


def member(args):
    vi, m, offset = args
    X, sk = _W['X'], _W['sk']
    v = _W['variants'][vi]
    seed = 778_000_000 + 10_000 * vi + m + offset
    rng = np.random.default_rng(seed)
    lines, info = X.generate(sk, _W['inv'][v['cfg']['parser']], {**v['family'], **v['cfg']}, rng)
    if v['noise'] == 'V1':
        lines = X.H757.apply_noise(lines, _W['noise'], rng)
    out = _pack(X.S.all_stats(lines, sk['folio'], rng))
    out.update({'vi': vi, 'member': m, 'offset': offset, 'empty_redraws': info['empty_redraws']})
    return out


def control_member(args):
    kind, m = args
    X, sk = _W['X'], _W['sk']
    rng = np.random.default_rng(CTRL_SEED[kind] + m)
    if kind == 'M1':
        c = _W['m1'].generate(sk['lines'], rng)
    elif kind == 'GEDGE':
        c = _W['ge'].generate(sk['lines'], rng)
    else:
        c = X.H757.apply_noise(sk['lines'], _W['noise'], rng)
    out = _pack(X.S.all_stats(c, sk['folio'], rng))
    out.update({'kind': kind, 'member': m})
    return out


# ================================================================================================ evaluation
def outside(b, vals, k):
    vals = np.asarray(vals, dtype=float)
    beyond = b < vals.min() or b > vals.max()
    sd = vals.std(ddof=1)
    if sd == 0:
        return bool(beyond)
    return bool(beyond and abs(b - vals.mean()) / sd > norm.ppf(1 - 0.005 / k))


def summ(vals, b=None):
    vals = np.asarray(vals, dtype=float)
    out = {'mean': float(vals.mean()), 'sd': float(vals.std(ddof=1)), 'min': float(vals.min()),
           'max': float(vals.max()), 'skew': float(skew(vals)) if vals.std() > 0 else 0.0}
    if b is not None and out['sd'] > 0:
        out['z_B'] = (b - out['mean']) / out['sd']
    return out


def evaluate(D, B, usable, nonbuiltin, k, vs):
    rows = []
    for vi, v in enumerate(vs):
        outs = [d for d in usable if outside(B[d], D[vi, :, DS.index(d)], k)]
        excl = len(outs) >= 2 and any(nonbuiltin[d] for d in outs)
        rows.append({'variant': v['name'], 'group': v['group'], 'outside': outs, 'n_out': len(outs),
                     'excludes': bool(excl), 'z': {d: summ(D[vi, :, DS.index(d)], B[d]).get('z_B') for d in usable},
                     'means': {d: float(np.mean(D[vi, :, DS.index(d)])) for d in usable}})
    return rows


# ================================================================================================ stages
def stage_controls():
    t0 = time.time()
    _init()
    X, sk = _W['X'], _W['sk']
    ref = X.H757.load_skeleton()
    assert ref['B'] == sk['lines'] and ref['folio'] == sk['folio'], 'skeleton differs from PHASE_757'
    b_stats = X.S.all_stats(sk['lines'], sk['folio'], np.random.default_rng(778))
    B = {d: float(b_stats[d]) for d in DS}
    log(f'B: ' + ', '.join(f'{d} {B[d]:.4f}' for d in DS))
    tasks = [('M1', m) for m in range(N_CTRL)] + [('GEDGE', m) for m in range(N_CTRL)] + \
            [('BNOISE', m) for m in range(N_REF)]
    res = {'M1': [], 'GEDGE': [], 'BNOISE': []}
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(control_member, tasks, chunksize=10)):
            res[r['kind']].append(r)
            if (i + 1) % 500 == 0:
                log(f'  controls {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)')
    k = len(DS)
    cert, usable = {}, []
    for j, d in enumerate(DS):
        certifiers = [c for c in ('M1', 'GEDGE') if not outside(B[d], [r['D'][j] for r in res[c]], k)]
        cert[d] = {'certifiers': certifiers, 'certified_by_non_builtin': any(d not in BUILT_IN[c] for c in certifiers),
                   **{c: summ([r['D'][j] for r in res[c]], B[d]) for c in res}}
        if certifiers:
            usable.append(d)
    out = {'B': B, 'usable': usable, 'k': len(usable), 'certification': cert, 'N_CTRL': N_CTRL,
           'B_desc': {k_: b_stats['desc'][k_] for k_ in DESC}, 'runtime_s': round(time.time() - t0, 1)}
    json.dump(out, open(OUT / 'controls_certification778.json', 'w', encoding='utf-8'), indent=1)
    np.savez_compressed(OUT / 'controls_raw778.npz', **{c: np.array([r['D'] for r in res[c]]) for c in res})
    log(f'certification: usable={usable} k={len(usable)}')
    for d in DS:
        log(f"  {d}: certifiers={cert[d]['certifiers']} non_builtin={cert[d]['certified_by_non_builtin']} "
            f"M1 z_B {cert[d]['M1'].get('z_B', float('nan')):+.1f} GEDGE z_B {cert[d]['GEDGE'].get('z_B', float('nan')):+.1f}")


def run_panel(offset, vis, n_members, tag):
    t0 = time.time()
    vs = variants()
    tasks = [(vi, m, offset) for vi in vis for m in range(n_members)]
    D = np.full((len(vs), n_members, len(DS)), np.nan)
    DE = np.full((len(vs), n_members, len(DESC)), np.nan)
    ER = np.full((len(vs), n_members), np.nan)
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(member, tasks, chunksize=10)):
            D[r['vi'], r['member']] = r['D']
            DE[r['vi'], r['member']] = r['desc']
            ER[r['vi'], r['member']] = r['empty_redraws']
            if (i + 1) % 2000 == 0:
                log(f'  panel {tag}: {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)')
                np.savez_compressed(OUT / f'panel_raw778_{tag}_interim.npz', D=D, DE=DE, ER=ER)
    np.savez_compressed(OUT / f'panel_raw778_{tag}.npz', D=D, DE=DE, ER=ER)
    log(f'panel {tag} done ({time.time() - t0:.0f}s)')


def stage_panel():
    run_panel(0, range(len(variants())), N_MEMBERS, 'offset0')


def stage_verdict():
    cc = json.load(open(OUT / 'controls_certification778.json', encoding='utf-8'))
    B, usable, k = cc['B'], cc['usable'], cc['k']
    nonbuiltin = {d: cc['certification'][d]['certified_by_non_builtin'] for d in DS}
    vs = variants()
    D0 = np.load(OUT / 'panel_raw778_offset0.npz')['D']
    rows = evaluate(D0, B, usable, nonbuiltin, k, vs)
    failing = [vi for vi, r in enumerate(rows) if not r['excludes']]
    log(f'first pass: {len(vs) - len(failing)}/{len(vs)} variants exclude; rerunning {len(failing)} with fresh seeds')
    rerun_rows = {}
    if failing:
        f = OUT / f'panel_raw778_offset{RERUN_OFFSET}.npz'
        if not f.exists():
            run_panel(RERUN_OFFSET, failing, N_MEMBERS, f'offset{RERUN_OFFSET}')
        D1 = np.load(f)['D']
        rr = evaluate(D1, B, usable, nonbuiltin, k, vs)
        rerun_rows = {vi: rr[vi] for vi in failing}
    final_fail = [vi for vi in failing if not rerun_rows[vi]['excludes']]
    groups = {}
    for grp in ('published', 'steelman'):
        idx = [vi for vi, v in enumerate(vs) if v['group'] == grp]
        ff = [vi for vi in final_fail if vi in idx]
        groups[grp] = {'n_variants': len(idx), 'not_excluding': [vs[vi]['name'] for vi in ff],
                       'verdict': ('NOT EXCLUDED' if (ff or k < 2) else 'EXCLUDED')}
    verdict = ('EXCLUDED' if (groups['published']['verdict'] == 'EXCLUDED' and
                              groups['steelman']['verdict'] == 'EXCLUDED') else 'NOT EXCLUDED')
    us2 = [d for d in usable if d != 'D2']
    rows2 = evaluate(D0, B, us2, nonbuiltin, max(len(us2), 1), vs) if us2 else []
    fail2 = [vs[vi]['name'] for vi, r in enumerate(rows2) if not r['excludes']]
    partial = {}
    for axis in ('order', 'd', 'pos', 'repeat'):
        partial[axis] = {}
        for val in sorted({str(v['family'][axis]) for v in vs}):
            idx = [vi for vi, v in enumerate(vs) if str(v['family'][axis]) == val]
            partial[axis][val] = {'excluding': sum(1 for vi in idx if vi not in final_fail), 'of': len(idx)}
    partial['noise'] = {n: {'excluding': sum(1 for vi, v in enumerate(vs) if v['noise'] == n and vi not in final_fail),
                            'of': sum(1 for v in vs if v['noise'] == n)} for n in NOISES}
    outside_counts = {d: sum(1 for r in rows if d in r['outside']) for d in usable}
    DE = np.load(OUT / 'panel_raw778_offset0.npz')['DE']
    desc = {vs[vi]['name']: dict(zip(DESC, np.nanmean(DE[vi], axis=0).tolist())) for vi in range(len(vs))}
    out = {'verdict': verdict, 'groups': groups, 'k': k, 'usable': usable, 'B': B, 'rows': rows,
           'rerun_rows': {vs[vi]['name']: r for vi, r in rerun_rows.items()},
           'final_not_excluding': [vs[vi]['name'] for vi in final_fail],
           'secondary_D2_removed': {'not_excluding': fail2, 'k': len(us2)}, 'partial': partial,
           'outside_counts': outside_counts, 'descriptives': desc, 'B_desc': cc['B_desc'],
           'fit_distance': {v['name']: v['fit_distance'] for v in vs}}
    json.dump(out, open(OUT / 'panel_verdict778.json', 'w', encoding='utf-8'), indent=1)
    log(f'VERDICT: {verdict} | published {groups["published"]["verdict"]} '
        f'({len(groups["published"]["not_excluding"])} not excluding of {groups["published"]["n_variants"]}); '
        f'steelman {groups["steelman"]["verdict"]} ({len(groups["steelman"]["not_excluding"])} of '
        f'{groups["steelman"]["n_variants"]}) | outside counts {outside_counts} | D2 removed: {len(fail2)} not excluding')
    for r in rows:
        log(f"  {r['variant']:34s} out={r['n_out']} {r['outside']} " +
            ' '.join(f"{d} {r['means'][d]:+.3f}(z{r['z'][d]:+.1f})" for d in usable))


def dry_run():
    global LOGF
    (OUT / 'dryrun').mkdir(exist_ok=True)
    LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
    _init()
    vs = _W['variants']
    if not vs:
        vs = [{'name': 'DRY/random/d5/reset/keep/V0', 'family': F.FAMILIES[0], 'cfg': F.configs()[0], 'noise': 'V0',
               'group': 'published', 'fit_distance': float('nan')},
              {'name': 'DRY/chain/d2/reset/keep/V1', 'family': F.FAMILIES[36], 'cfg': F.configs()[1], 'noise': 'V1',
               'group': 'steelman', 'fit_distance': float('nan')}]
        _W['variants'] = vs
    pick = [0, len(vs) - 1]
    X, sk = _W['X'], _W['sk']
    B = {d: float(v) for d, v in X.S.all_stats(sk['lines'], sk['folio'], np.random.default_rng(1)).items()
         if d in DS} if False else json.load(open(ROOT / P757 / 'results/controls_certification.json'))['B']
    D = np.full((len(vs), 3, len(DS)), np.nan)
    for vi in pick:
        for m in range(3):
            r = member((vi, m, 0))
            D[vi, m] = r['D']
            log(f"[dry] {vs[vi]['name']} m{m} " + ' '.join(f'{d} {x:+.3f}' for d, x in zip(DS, r['D'])) +
                f" empty_redraws {r['empty_redraws']}")
    rows = evaluate(D[pick], B, DS, {d: True for d in DS}, len(DS), [vs[i] for i in pick])
    for r in rows:
        log(f"[dry] evaluate {r['variant']}: outside {r['outside']} excludes {r['excludes']} (N=3, illustrative only)")
    c = control_member(('M1', 0))
    log('[dry] M1 member ' + ' '.join(f'{d} {x:+.3f}' for d, x in zip(DS, c['D'])))
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
    assert stage in ('controls', 'panel', 'verdict'), 'stage: controls | panel | verdict'
    verify_lock()
    LOGF = open(OUT / f'{stage}_log778.txt', 'a', encoding='utf-8')
    log(f'PHASE_778 {stage}; lock {LOCK} verified; inputs verified; {time.strftime("%Y-%m-%d %H:%M:%S")}')
    {'controls': stage_controls, 'panel': stage_panel, 'verdict': stage_verdict}[stage]()
    log('done')


if __name__ == '__main__':
    main()
