#!/usr/bin/env python3
"""PHASE_778 locked run: rival-generator panel II, the table-and-grille method (see ../PRE_REGISTRATION.md).

  python run778.py --checksums   write results/input_checksums.json (before the lock commit)
  python run778.py --dry         every code path on 2 variants x 3 members + the evaluation logic (no verdict)
  python run778.py controls      positive-control certification (M1, G-EDGE; B + noise reference); B's D2-D6
  python run778.py panel         the declared variants (families x noise), N members each
  python run778.py nearfit       C4: the PUBLISHED families' next-best fit configurations at N_NEAR members
  python run778.py verdict       outside tests, pooled rerun, tier verdicts, sensitivities, descriptives
Stages verify the lock first.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
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
          f'{P757}/results/controls_raw.npz', 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
LOCKED = ('PRE_REGISTRATION.md', 'scripts/grille778.py', 'scripts/gates778.py', 'scripts/fit778.py',
          'scripts/fit_extend778.py', 'scripts/prelock_controls778.py', 'scripts/run778.py', 'results/gates778.json', 'results/b_surface778.json',
          'results/fit778.json', 'results/prelock_controls778.json', 'results/input_checksums.json')
NOISES = ['V0', 'V1']
N_MEMBERS, N_CTRL, N_REF, N_NEAR = 1000, 1000, 50, 200
RERUN_OFFSET = 5_000_000
DS = ['D2', 'D3', 'D4', 'D5', 'D6']
DESC = ['types', 'hapax_type_fraction', 'zipf_slope', 'mean_token_length', 'duplicate_lines', 'max_identical_run',
        'erun_class_same_lag1', 'max_qok_in_10_window']
EXTRA = ['rpt5', 'whole_root_affixed', 'empty_redraws', 'repeat_redraws', 'junction_redraws']
BUILT_IN = {'M1': {'D5', 'D6'}, 'GEDGE': {'D2', 'D6'}}
CTRL_SEED = {'M1': 778_900_000, 'GEDGE': 778_910_000, 'BNOISE': 778_920_000}
WORKERS = 6
Z_BORDER = 4.0
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
    """One variant per (family, noise); the family's configuration is its fit group's selected configuration."""
    fit = json.load(open(OUT / 'fit778.json', encoding='utf-8'))
    out = []
    for fam in F.families():
        gname = F.group_name(fam)
        g = fit['groups'][gname]
        for noise in NOISES:
            out.append({'name': f"{F.family_name(fam)}/{noise}", 'family': fam, 'tier': fam['tier'], 'cfg': g['best']['cfg'],
                        'noise': noise, 'fit_distance': g['fresh']['distance'], 'band': g['fresh']['band']})
    return out


def counted_set(tier, usable, prelock):
    """Counted discriminators per tier: STEELMAN (exposed to B's junction table) drops D2."""
    ds = [d for d in usable if not (tier == 'STEELMAN' and d == 'D2')]
    return ds


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
    fitfn = OUT / 'fit778.json'
    _W['variants'] = variants() if (fitfn.exists() and json.load(open(fitfn, encoding='utf-8')).get('complete')) else []


def rpt5(lines):
    """Descriptive (C2091's statistic): within-line 5-token windows whose token sequence occurs >= 2 times."""
    c = Counter()
    for ln in lines:
        seg = []
        for w in ln + [None]:
            if w is None:
                for i in range(len(seg) - 4):
                    c[tuple(seg[i:i + 5])] += 1
                seg = []
            else:
                seg.append(w)
    return int(sum(n for n in c.values() if n >= 2))


def _pack(st, lines, info):
    return {'D': [st[d] for d in DS], 'desc': [st['desc'][k] for k in DESC], 'aux': st['aux'],
            'extra': [rpt5(lines), info.get('whole_root_affixed', 0), info.get('empty_redraws', 0),
                      info.get('repeat_redraws', 0), info.get('junction_redraws', 0)]}


def member(args):
    vi, m, offset, cfg_override = args
    X, sk = _W['X'], _W['sk']
    v = _W['variants'][vi]
    cfg = cfg_override or v['cfg']
    seed = 778_000_000 + 10_000 * vi + m + offset
    rng = np.random.default_rng(seed)
    fam = {k: v['family'][k] for k in ('order', 'd', 'pos', 'repeat', 'redraw')}
    lines, info = X.generate(sk, _W['inv'][cfg['parser']], {**fam, **cfg}, rng)
    if v['noise'] == 'V1':
        lines = X.H757.apply_noise(lines, _W['noise'], rng)
    out = _pack(X.S.all_stats(lines, sk['folio'], rng), lines, info)
    out.update({'vi': vi, 'member': m, 'offset': offset})
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
    out = _pack(X.S.all_stats(c, sk['folio'], rng), c, {})
    out.update({'kind': kind, 'member': m})
    return out


# ================================================================================================ evaluation
def zstar(k):
    return norm.ppf(1 - 0.005 / max(k, 1))


def outside(b, vals, k):
    vals = np.asarray(vals, dtype=float)
    vals = vals[~np.isnan(vals)]
    beyond = b < vals.min() or b > vals.max()
    sd = vals.std(ddof=1)
    if sd == 0:
        return bool(beyond)
    return bool(beyond and abs(b - vals.mean()) / sd > zstar(k))


def summ(vals, b=None):
    vals = np.asarray(vals, dtype=float)
    vals = vals[~np.isnan(vals)]
    out = {'mean': float(vals.mean()), 'sd': float(vals.std(ddof=1)), 'min': float(vals.min()),
           'max': float(vals.max()), 'skew': float(skew(vals)) if vals.std() > 0 else 0.0, 'n': int(len(vals))}
    if b is not None:
        out['z_B'] = (b - out['mean']) / out['sd'] if out['sd'] > 0 else float('inf') * np.sign(b - out['mean'])
        out['rank_B'] = int((vals < b).sum())             # members below B (0 = B below all; n = B above all)
    return out


def evaluate(D, B, usable, nonbuiltin, vs, merge_reset):
    """Per variant: outside set on its tier's counted discriminators; n_out with the D5/D6 merge for reset variants
    when the column-lock control says so; excludes if n_out >= 2 and an independently certified discriminator is
    outside; BORDERLINE if a counted outside discriminator has |z| < Z_BORDER."""
    rows = []
    for vi, v in enumerate(vs):
        ds = counted_set(v['tier'], usable, None)
        k = len(ds)
        outs = [d for d in ds if outside(B[d], D[vi, :, DS.index(d)], k)]
        n_out = len(outs)
        merged = bool(merge_reset and v['family']['pos'] == 'reset' and v['family']['d'] != 'RP'
                      and 'D5' in outs and 'D6' in outs)
        if merged:
            n_out -= 1
        excl = n_out >= 2 and any(nonbuiltin[d] for d in outs)
        st = {d: summ(D[vi, :, DS.index(d)], B[d]) for d in ds}
        border = bool(excl and any(abs(st[d]['z_B']) < Z_BORDER for d in outs))
        rows.append({'variant': v['name'], 'tier': v['tier'], 'band': v['band'], 'k': k, 'counted': ds, 'outside': outs,
                     'n_out': n_out, 'merged_d5_d6': merged, 'excludes': bool(excl), 'borderline': border,
                     'z': {d: st[d]['z_B'] for d in ds}, 'rank': {d: st[d]['rank_B'] for d in ds},
                     'means': {d: st[d]['mean'] for d in ds}, 'n': int(st[ds[0]]['n'])})
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
    log('B: ' + ', '.join(f'{d} {B[d]:.4f}' for d in DS))
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
           'B_desc': {k_: b_stats['desc'][k_] for k_ in DESC}, 'B_rpt5': rpt5(sk['lines']),
           'runtime_s': round(time.time() - t0, 1)}
    json.dump(out, open(OUT / 'controls_certification778.json', 'w', encoding='utf-8'), indent=1)
    np.savez_compressed(OUT / 'controls_raw778.npz', **{c: np.array([r['D'] for r in res[c]]) for c in res})
    log(f'certification: usable={usable} k={len(usable)}')
    for d in DS:
        log(f"  {d}: certifiers={cert[d]['certifiers']} non_builtin={cert[d]['certified_by_non_builtin']} "
            f"M1 z_B {cert[d]['M1']['z_B']:+.1f} GEDGE z_B {cert[d]['GEDGE']['z_B']:+.1f}")


def run_panel(offset, vis, n_members, tag, cfg_over=None):
    t0 = time.time()
    vs = variants()
    tasks = [(vi, m, offset, (cfg_over or {}).get(vi)) for vi in vis for m in range(n_members)]
    D = np.full((len(vs), n_members, len(DS)), np.nan)
    DE = np.full((len(vs), n_members, len(DESC)), np.nan)
    EX = np.full((len(vs), n_members, len(EXTRA)), np.nan)
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(member, tasks, chunksize=10)):
            D[r['vi'], r['member']] = r['D']
            DE[r['vi'], r['member']] = r['desc']
            EX[r['vi'], r['member']] = r['extra']
            if (i + 1) % 2000 == 0:
                log(f'  panel {tag}: {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)')
                np.savez_compressed(OUT / f'panel_raw778_{tag}_interim.npz', D=D, DE=DE, EX=EX)
    np.savez_compressed(OUT / f'panel_raw778_{tag}.npz', D=D, DE=DE, EX=EX)
    log(f'panel {tag} done ({time.time() - t0:.0f}s)')
    return D


def stage_panel():
    run_panel(0, range(len(variants())), N_MEMBERS, 'offset0')


def stage_nearfit():
    """C4: for each PUBLISHED family, the next two fit configurations (by distance) at N_NEAR members."""
    fit = json.load(open(OUT / 'fit778.json', encoding='utf-8'))
    vs = variants()
    for rank in (1, 2):
        over = {}
        for vi, v in enumerate(vs):
            if v['tier'] == 'PUBLISHED':
                top = fit['groups'][F.group_name(v['family'])]['top5']
                if rank < len(top):
                    over[vi] = top[rank]['cfg']
        run_panel(7_000_000 + rank * 100_000, list(over), N_NEAR, f'nearfit{rank}', over)


def tier_verdict(tier, rows, pooled):
    idx = [i for i, r in enumerate(rows) if r['tier'] == tier]
    counted = [i for i in idx if rows[i]['band'] in ('FITTED', 'PARTIAL')]
    fitted = [i for i in idx if rows[i]['band'] == 'FITTED']
    surv = [rows[i]['variant'] for i in counted if not pooled[i]['excludes']]
    if not counted:
        verdict = 'EXCLUDED ON SURFACE'
    elif surv:
        verdict = 'NOT EXCLUDED'
    elif not fitted:
        verdict = 'EXCLUDED (PARTIAL FITS ONLY)'
    else:
        verdict = 'EXCLUDED'
    border = [rows[i]['variant'] for i in counted if pooled[i]['excludes'] and pooled[i]['borderline']]
    return {'verdict': verdict, 'n_variants': len(idx), 'n_counted': len(counted), 'n_fitted': len(fitted),
            'not_excluding': surv, 'borderline': border,
            'unfitted_reported': [rows[i]['variant'] for i in idx if rows[i]['band'] == 'UNFITTED']}


def stage_verdict():
    cc = json.load(open(OUT / 'controls_certification778.json', encoding='utf-8'))
    pre = json.load(open(OUT / 'prelock_controls778.json', encoding='utf-8'))
    merge_reset = bool(pre['C3']['merge_d5_d6_reset'])
    B, usable = cc['B'], cc['usable']
    nonbuiltin = {d: cc['certification'][d]['certified_by_non_builtin'] for d in DS}
    vs = variants()
    raw0 = np.load(OUT / 'panel_raw778_offset0.npz')
    D0 = raw0['D']
    rows0 = evaluate(D0, B, usable, nonbuiltin, vs, merge_reset)
    failing = [vi for vi, r in enumerate(rows0) if not r['excludes']]
    log(f'first pass (N={N_MEMBERS}): {len(vs) - len(failing)}/{len(vs)} variants exclude; '
        f'rerunning {len(failing)} with fresh seeds for the pooled decision')
    D = D0
    rows1 = {}
    if failing:
        f = OUT / f'panel_raw778_offset{RERUN_OFFSET}.npz'
        if not f.exists():
            run_panel(RERUN_OFFSET, failing, N_MEMBERS, f'offset{RERUN_OFFSET}')
        D1 = np.load(f)['D']
        rows1 = {vi: r for vi, r in enumerate(evaluate(D1, B, usable, nonbuiltin, vs, merge_reset)) if vi in failing}
        D = np.concatenate([D0, D1], axis=1)                # pooled ensemble (NaN rows for variants not rerun)
    pooled = evaluate(D, B, usable, nonbuiltin, vs, merge_reset)
    tiers = {t: tier_verdict(t, pooled, pooled) for t in ('PUBLISHED', 'EXTENDED', 'STEELMAN')}
    # sensitivities
    sens = {}
    for drop in ('D2', 'D6'):
        us = [d for d in usable if d != drop]
        rr = evaluate(D, B, us, nonbuiltin, vs, merge_reset)
        sens[f'without_{drop}'] = {t: tier_verdict(t, rr, rr)['verdict'] for t in tiers}
    nomerge = evaluate(D, B, usable, nonbuiltin, vs, False)
    sens['no_d5_d6_merge'] = {t: tier_verdict(t, nomerge, nomerge)['verdict'] for t in tiers}
    partial = {}
    for axis in ('order', 'd', 'pos', 'repeat', 'redraw'):
        partial[axis] = {}
        for val in sorted({str(v['family'][axis]) for v in vs}):
            idx = [vi for vi, v in enumerate(vs) if str(v['family'][axis]) == val]
            partial[axis][val] = {'excluding': sum(1 for vi in idx if pooled[vi]['excludes']), 'of': len(idx)}
    partial['noise'] = {n: {'excluding': sum(1 for vi, v in enumerate(vs) if v['noise'] == n and pooled[vi]['excludes']),
                            'of': sum(1 for v in vs if v['noise'] == n)} for n in NOISES}
    outside_counts = {d: sum(1 for r in pooled if d in r['outside']) for d in usable}
    DE, EX = raw0['DE'], raw0['EX']
    desc = {vs[vi]['name']: {**dict(zip(DESC, np.nanmean(DE[vi], axis=0).tolist())),
                             **dict(zip(EXTRA, np.nanmean(EX[vi], axis=0).tolist()))} for vi in range(len(vs))}
    near = {}
    for rank in (1, 2):
        f = OUT / f'panel_raw778_nearfit{rank}.npz'
        if f.exists():
            Dn = np.load(f)['D']
            rn = evaluate(Dn, B, usable, nonbuiltin, vs, merge_reset)
            near[rank] = {vs[vi]['name']: {'excludes': r['excludes'], 'outside': r['outside']}
                          for vi, r in enumerate(rn) if not np.isnan(Dn[vi]).all()}
    unstable = sorted({name for rk in near.values() for name, r in rk.items() if not r['excludes']})
    out = {'tiers': tiers, 'usable': usable, 'B': B, 'merge_d5_d6_reset': merge_reset, 'z_star': {k: zstar(k) for k in (4, 5)},
           'rows_first_pass': rows0, 'rows_rerun': {vs[vi]['name']: r for vi, r in rows1.items()}, 'rows_pooled': pooled,
           'sensitivities': sens, 'partial': partial, 'outside_counts': outside_counts, 'descriptives': desc,
           'B_desc': cc['B_desc'], 'B_rpt5': cc['B_rpt5'], 'nearfit': near, 'unstable_to_fit': unstable,
           'fit': {v['name']: {'distance': v['fit_distance'], 'band': v['band']} for v in vs}}
    json.dump(out, open(OUT / 'panel_verdict778.json', 'w', encoding='utf-8'), indent=1)
    log('VERDICT per tier: ' + ' | '.join(f"{t} {tiers[t]['verdict']} (counted {tiers[t]['n_counted']}, fitted "
                                          f"{tiers[t]['n_fitted']}, not excluding {len(tiers[t]['not_excluding'])}, "
                                          f"borderline {len(tiers[t]['borderline'])})" for t in tiers))
    log(f'outside counts {outside_counts} | sensitivities {sens} | unstable-to-fit {unstable}')
    for r in pooled:
        log(f"  {r['variant']:52s} {r['band']:8s} out={r['n_out']} {r['outside']}{' merged' if r['merged_d5_d6'] else ''} "
            + ' '.join(f"{d} {r['means'][d]:+.3f}(z{r['z'][d]:+.1f},r{r['rank'][d]})" for d in r['counted'])
            + (' BORDERLINE' if r['borderline'] else ''))


def dry_run():
    global LOGF
    (OUT / 'dryrun').mkdir(exist_ok=True)
    LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
    _init()
    vs = _W['variants']
    if not vs:
        fams = F.families()
        c0, c1 = F.configs(True)[0], F.configs(False)[5]
        vs = [{'name': f"DRY/{F.family_name(fams[0])}/V0", 'family': fams[0], 'tier': fams[0]['tier'], 'cfg': c0,
               'noise': 'V0', 'fit_distance': float('nan'), 'band': 'PARTIAL'},
              {'name': f"DRY/{F.family_name(fams[-1])}/V1", 'family': fams[-1], 'tier': fams[-1]['tier'], 'cfg': c1,
               'noise': 'V1', 'fit_distance': float('nan'), 'band': 'PARTIAL'}]
        _W['variants'] = vs
    pick = [0, len(vs) - 1]
    B = json.load(open(ROOT / P757 / 'results/controls_certification.json'))['B']
    D = np.full((len(vs), 3, len(DS)), np.nan)
    for vi in pick:
        for m in range(3):
            r = member((vi, m, 0, None))
            D[vi, m] = r['D']
            log(f"[dry] {vs[vi]['name']} m{m} " + ' '.join(f'{d} {x:+.3f}' for d, x in zip(DS, r['D'])) +
                f" extra {dict(zip(EXTRA, r['extra']))}")
    rows = evaluate(D[pick], B, DS, {d: d in ('D3', 'D4') for d in DS}, [vs[i] for i in pick], True)
    for r in rows:
        log(f"[dry] evaluate {r['variant']}: counted {r['counted']} outside {r['outside']} n_out {r['n_out']} "
            f"merged {r['merged_d5_d6']} excludes {r['excludes']} borderline {r['borderline']} (N=3, illustrative only)")
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
    assert stage in ('controls', 'panel', 'nearfit', 'verdict'), 'stage: controls | panel | nearfit | verdict'
    verify_lock()
    LOGF = open(OUT / f'{stage}_log778.txt', 'a', encoding='utf-8')
    log(f'PHASE_778 {stage}; lock {LOCK} verified; inputs verified; {time.strftime("%Y-%m-%d %H:%M:%S")}')
    {'controls': stage_controls, 'panel': stage_panel, 'nearfit': stage_nearfit, 'verdict': stage_verdict}[stage]()
    log('done')


if __name__ == '__main__':
    main()
