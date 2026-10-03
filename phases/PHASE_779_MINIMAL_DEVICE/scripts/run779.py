#!/usr/bin/env python3
"""PHASE_779 (v2) locked run (see ../PRE_REGISTRATION.md).

  python run779.py --checksums   write results/input_checksums.json (before the lock commit)
  python run779.py --dry         every code path on 2 members per variant (no B value read)
  python run779.py fidelity      PRE-LOCK: kappa grid on D2 alone (primary rung), memo variant's D6, depletion
                                 diagnostics; writes results/fidelity779.json (generated members; B's D2/D6 are
                                 the PHASE_757/778 values, already exposed)
  python run779.py plants        PRE-LOCK: plant grids on the primary rung (200 members per point) -> MDE80 per
                                 counted prediction; writes results/plants779.json (generated members only)
  python run779.py run           B's values and N members per variant (+ a second seed block for the discrete
                                 statistic); raw arrays
  python run779.py sens          descriptive sensitivity: the primary at kappa x 0.5 / x 2 and kappa_z x 0.5 / x 2
                                 (200 members each) against B's locked values; writes results/sens779.json
  python run779.py plantcheck    plant points around each pre-lock MDE80 rerun from their seeds (generated members
                                 only) and their fractions outside recomputed against the LOCKED primary ensemble
                                 (continuous N 1,000; P6z pooled N 2,000); writes results/plantcheck779.json
  python run779.py verdict       outside tests, three-way power rule, layer map (uses plantcheck779.json; folds
                                 sens779.json in if present)
Locked stages (run, sens, plantcheck, verdict) verify the lock first. `run` and `sens` write partial results
incrementally and resume from their seeds after a verified match of 5 regenerated members (HARNESS-FAIL otherwise).
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

ROOT = Path('C:/git/voynich')
LOCK = 'phase779-lock'
PHASE = 'phases/PHASE_779_MINIMAL_DEVICE'
OUT = ROOT / PHASE / 'results'
P757 = 'phases/PHASE_757_NAIBBE_RIVAL_PANEL'
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'scripts/voynich.py',
          f'{P757}/scripts/panel_stats.py', f'{P757}/scripts/naibbe_harness.py',
          'phases/PHASE_778_GRILLE_RIVAL_PANEL/scripts/grille778.py',
          'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
          'phases/LINE_CONTROL_BLOCK_GRAMMAR/results/02_mandatory_forbidden_bigrams.json')
LOCKED = ('PRE_REGISTRATION.md', 'scripts/mind779.py', 'scripts/run779.py', 'results/c957_bigrams.json',
          'results/fidelity779.json', 'results/plants779.json', 'results/input_checksums.json')
# variants: (name, rung, stock, replace, memo, header)
VARIANTS = [('R0L', 'R0', 'L', False, False, False), ('R1L', 'R1', 'L', False, False, False),
            ('R2aL', 'R2a', 'L', False, False, False), ('R2L', 'R2', 'L', False, False, False),
            ('R3L', 'R3', 'L', False, False, False), ('R2P', 'R2', 'P', False, False, False),
            ('R2Lmemo', 'R2', 'L', False, True, False), ('R2Lw', 'R2', 'L', True, False, False),
            ('R2L+H', 'R2', 'L', False, False, True)]
PRIMARY = 'R2L'
BASELINE = 'R0L'
LADDER = ['R0L', 'R1L', 'R2aL', 'R2L', 'R3L']
NO_COMPOSITION_READ = {'R2Lw'}          # composition statistics are not read on the depletion sensitivity
N_MEMBERS, N_PLANT, N_FID = 1000, 200, 200
SEED_RUN, SEED_RUN2, SEED_PLANT, SEED_FID = 779_000_000, 779_500_000, 779_200_000, 779_100_000
DS = ['D2', 'D3', 'D4', 'D5', 'D6']
PANEL_TESTED = ['D3', 'D4', 'D5']       # D2 (and D6 on memo) are fidelity statistics (audit edit 8)
WORKERS = 6
DRY = '--dry' in sys.argv
_W = {}
LOGF = None
B_KNOWN = {'D2': 0.2282, 'D6': 0.1718}  # PHASE_778 certification values (exposed), for the fidelity gate only


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


def kappa_locked():
    f = OUT / 'fidelity779.json'
    return json.load(open(f, encoding='utf-8'))['kappa_selected'] if f.exists() else 2.0


def _init(kappa=None, kz=None):
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
    _W['kappa'] = kappa_locked() if kappa is None else kappa
    _W['kz'] = M.KZ if kz is None else kz
    _W['T'] = M.spec_tables(_W['sk'], kappa=_W['kappa'], kz=_W['kz'])
    _W['c957'] = M.load_c957()
    pf = OUT / 'prohibit_tmp.json'
    _W['prohibit'] = {a: set(b) for a, b in json.load(open(pf, encoding='utf-8')).items()} if pf.exists() else None


SWEEPS = 10                             # Metropolis sweeps (init: the sequential sampler's output); mixing checked at 20


def gen_variant(name, rng, plant=None, lam=0.0, prohibit=None, sweeps=None, diag=False):
    """Without-replacement variants use the within-cell Metropolis sampler (the declared fallback after the sequential
    sampler failed the fidelity gate on D2 through depletion); R2Lw stays the sequential with-replacement sampler."""
    M, sk, T = _W['M'], _W['sk'], _W['T']
    v = next(x for x in VARIANTS if x[0] == name)
    _, rung, stock, rep, memo, header = v
    if rep:
        lines = M.generate(sk, T, rung, stock, True, memo, header, plant, lam, rng, prohibit)
        return (lines, {'acc': float('nan'), 'changed': float('nan')}) if diag else lines
    return M.generate_mh(sk, T, rung, stock, memo, header, plant, lam, rng, prohibit,
                         sweeps=SWEEPS if sweeps is None else sweeps, init='seq', diag=diag)


def member(args):
    """(variant name, member, seed base, plant, lam, keep_pairs[, block])"""
    name, m, seed, plant, lam, keep_pairs = args[:6]
    block = args[6] if len(args) > 6 else 0
    sweeps = args[7] if len(args) > 7 else None
    M, sk = _W['M'], _W['sk']
    rng = np.random.default_rng(seed + m)
    lines, mh = gen_variant(name, rng, plant, lam, _W.get('prohibit'), sweeps=sweeps, diag=True)
    st = M.S.all_stats(lines, sk['folio'], rng)
    pr, cpairs = M.predictions(lines, sk, _W['c957'], _W['T'], rng)
    fid = M.fidelity(lines, sk)
    out = {'name': name, 'member': m, 'block': block, 'D': [st[d] for d in DS], 'P': [pr[k] for k in M.COUNTED],
           'X': [pr[k] for k in M.DESCRIPTIVE], 'F': [fid[k] for k in ('mi_route2_raw', 'mi_edge_first_half_raw', 'mi_edge_second_half_raw')],
           'MH': [mh['acc'], mh['changed']]}
    if keep_pairs:
        out['pairs'] = (np.array([k[0] for k in cpairs], np.int16), np.array([k[1] for k in cpairs], np.int16),
                        np.array(list(cpairs.values()), np.int16))
    return out


def b_values():
    M, sk = _W['M'], _W['sk']
    rng = np.random.default_rng(779)
    st = M.S.all_stats(sk['lines'], sk['folio'], rng)
    pr, cpairs = M.predictions(sk['lines'], sk, _W['c957'], _W['T'], rng)
    fid = M.fidelity(sk['lines'], sk)
    return {'D': {d: float(st[d]) for d in DS}, 'P': {k: float(pr[k]) for k in M.COUNTED},
            'X': {k: (float(pr[k]) if isinstance(pr[k], float) else pr[k]) for k in M.DESCRIPTIVE}, 'F': fid}, cpairs


def zstar(k):
    return norm.ppf(1 - 0.005 / max(k, 1))


def outside(b, vals, k, discrete=False):
    vals = np.asarray(vals, float)
    vals = vals[~np.isnan(vals)]
    if discrete:
        return bool(b < vals.min() or b > vals.max())          # strictly beyond every member; ties inside
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
            'z_B': float((b - vals.mean()) / sd) if sd > 0 else float('nan'), 'rank_B': int((vals < b).sum())}


def pool_map(fn, tasks, init_kappa=None, chunksize=5, init_kz=None):
    with Pool(WORKERS, initializer=_init, initargs=(init_kappa, init_kz)) as pool:
        for r in pool.imap_unordered(fn, tasks, chunksize=chunksize):
            yield r


# ================================================================================================ pre-lock stages
def stage_fidelity():
    """kappa chosen on D2 alone; the primary rung must not be outside on D2 (B's D2 known); memo variant on D6."""
    t0 = time.time()
    res = {'kappa': {}, 'N': N_FID, 'sampler': 'MH', 'sweeps': SWEEPS}
    for kappa in _W['M'].KAPPA_GRID if 'M' in _W else (0.5, 2.0, 8.0):
        tasks = [(PRIMARY, m, SEED_FID + int(kappa * 1000), None, 0.0, False) for m in range(N_FID)]
        D = []; F = []; MH = []
        for r in pool_map(member, tasks, init_kappa=kappa):
            D.append(r['D']); F.append(r['F']); MH.append(r['MH'])
        D = np.array(D); F = np.array(F); MH = np.array(MH)
        d2 = summ(D[:, 0], B_KNOWN['D2'])
        res['kappa'][str(kappa)] = {'D2': d2, 'D2_outside': outside(B_KNOWN['D2'], D[:, 0], 5),
                                    'D6': summ(D[:, 4], B_KNOWN['D6']), 'fidelity_means': dict(zip(('mi_route2_raw', 'mi_edge_first_half_raw', 'mi_edge_second_half_raw'), F.mean(0).tolist())),
                                    'mh_acceptance': float(MH[:, 0].mean()), 'mh_changed': float(MH[:, 1].mean())}
        log(f"kappa {kappa}: D2 {d2['mean']:.4f} ± {d2['sd']:.4f} (B {B_KNOWN['D2']}, z {d2['z_B']:+.2f}, outside {res['kappa'][str(kappa)]['D2_outside']}); "
            f"halves {F[:, 1].mean():.4f}/{F[:, 2].mean():.4f}; MH acc {MH[:, 0].mean():.3f} changed {MH[:, 1].mean():.3f} ({time.time() - t0:.0f}s)")
    # selection on D2 alone: the kappa with the smallest |z_B| on D2
    best = min(res['kappa'], key=lambda k: abs(res['kappa'][k]['D2']['z_B']))
    res['kappa_selected'] = float(best)
    res['primary_D2_pass'] = not res['kappa'][best]['D2_outside']
    # mixing check: the primary at 2 x SWEEPS must agree with SWEEPS on D2 within one ensemble sd
    tasks = [(PRIMARY, m, SEED_FID + 90_000, None, 0.0, False, 0, 2 * SWEEPS) for m in range(N_FID)]
    D = np.array([r['D'] for r in pool_map(member, tasks, init_kappa=float(best))])
    d2b = summ(D[:, 0], B_KNOWN['D2'])
    res['mixing'] = {'sweeps_double': 2 * SWEEPS, 'D2': d2b, 'delta_mean': d2b['mean'] - res['kappa'][best]['D2']['mean'],
                     'pass': abs(d2b['mean'] - res['kappa'][best]['D2']['mean']) <= res['kappa'][best]['D2']['sd']}
    log(f"mixing: D2 at {2 * SWEEPS} sweeps {d2b['mean']:.4f} vs {res['kappa'][best]['D2']['mean']:.4f} at {SWEEPS} (sd {res['kappa'][best]['D2']['sd']:.4f}) pass {res['mixing']['pass']}")
    # memo variant and the no-replacement check at the selected kappa
    for name in ('R2Lmemo', 'R2Lw', 'R2P'):
        tasks = [(name, m, SEED_FID + 50_000, None, 0.0, False) for m in range(N_FID)]
        D = np.array([r['D'] for r in pool_map(member, tasks, init_kappa=float(best))])
        res[name] = {'D2': summ(D[:, 0], B_KNOWN['D2']), 'D6': summ(D[:, 4], B_KNOWN['D6']),
                     'D6_outside': outside(B_KNOWN['D6'], D[:, 4], 5), 'D2_outside': outside(B_KNOWN['D2'], D[:, 0], 5)}
        log(f"{name}: D2 {res[name]['D2']['mean']:.4f} (z {res[name]['D2']['z_B']:+.2f}) D6 {res[name]['D6']['mean']:.4f} (z {res[name]['D6']['z_B']:+.2f})")
    res['memo_D6_pass'] = not res['R2Lmemo']['D6_outside']
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(OUT / 'fidelity779.json', 'w', encoding='utf-8'), indent=1)
    log(f"fidelity: kappa {best} selected; primary D2 pass {res['primary_D2_pass']}; memo D6 pass {res['memo_D6_pass']}; mixing pass {res['mixing']['pass']}")


def _prohibit_cells(rng, m):
    """m random cells among common-token pairs with primary-ensemble expectation >= 3 (from fidelity-run members)."""
    exp = _W.get('pair_expect')
    if exp is None:
        return None
    cells = [(a, b) for (a, b), e in exp.items() if e >= 3]
    pick = rng.choice(len(cells), size=min(m, len(cells)), replace=False)
    common = _W['T']['common']
    pro = {}
    for i in pick:
        a, b = cells[i]
        pro.setdefault(common[a], set()).add(common[b])
    return pro


def stage_plants():
    """Plant grids on the primary rung: MDE80 per counted prediction (the smallest grid point at which >= 80% of
    members are outside the baseline primary ensemble on that statistic). Generated members only."""
    t0 = time.time()
    M = _W['M']
    kappa = kappa_locked()
    # baseline primary ensemble (N_PLANT) for the outside test, with pair counts for the P6 cell set
    tasks = [(PRIMARY, m, SEED_PLANT, None, 0.0, True) for m in range(N_PLANT)]
    base = list(pool_map(member, tasks, init_kappa=kappa))
    P0 = np.array([r['P'] for r in base])
    nC = len(_W['T']['common']) if 'T' in _W else None
    # ensemble pair expectation
    acc = Counter()
    for r in base:
        a, b, c = r['pairs']
        for i in range(len(a)):
            acc[(int(a[i]), int(b[i]))] += int(c[i])
    exp = {k: v / N_PLANT for k, v in acc.items()}
    cells = [k for k, e in exp.items() if e >= 3]
    zeros0 = []
    for r in base:
        a, b, c = r['pairs']
        present = set(zip(a.tolist(), b.tolist()))
        zeros0.append(sum(1 for k in cells if k not in present))
    res = {'kappa': kappa, 'N': N_PLANT, 'cells_expect_ge3': len(cells), 'baseline_zeros': summ(zeros0, 0.0),
           'plants': {}}
    json.dump({'cells': cells, 'expect': {f'{a},{b}': e for (a, b), e in exp.items() if e >= 3}},
              open(OUT / 'pair_cells779.json', 'w', encoding='utf-8'))
    _W['pair_expect'] = exp
    for key, (plant, grid) in M.PLANTS.items():
        res['plants'][key] = {'plant': plant, 'grid': list(grid), 'points': {}}
        j = M.COUNTED.index(key) if key in M.COUNTED else None
        mde = None
        for lam in grid:
            rng0 = np.random.default_rng(SEED_PLANT + 777)
            if plant == 'P6':
                pro = _prohibit_cells(rng0, int(lam))
                _W['prohibit'] = pro
            tasks = [(PRIMARY, m, SEED_PLANT + 10_000 * (list(M.PLANTS).index(key) + 1) + int(lam * 100), plant, float(lam), plant == 'P6')
                     for m in range(N_PLANT)]
            if plant == 'P6':
                # pool workers read the prohibit set from this file in _init (removed after the grid point)
                json.dump({a: sorted(b) for a, b in pro.items()}, open(OUT / 'prohibit_tmp.json', 'w'))
            vals = []
            for r in pool_map(member, tasks, init_kappa=kappa):
                if plant == 'P6':
                    a, b, c = r['pairs']
                    present = set(zip(a.tolist(), b.tolist()))
                    vals.append(sum(1 for k in cells if k not in present))
                else:
                    vals.append(r['P'][j])
            vals = np.array(vals, float)
            ref = np.array(zeros0, float) if plant == 'P6' else P0[:, j]
            frac_out = float(np.mean([outside(v, ref, 8, discrete=(plant == 'P6')) for v in vals]))
            res['plants'][key]['points'][str(lam)] = {'mean': float(np.nanmean(vals)), 'sd': float(np.nanstd(vals, ddof=1)),
                                                     'baseline_mean': float(np.nanmean(ref)), 'frac_outside': frac_out}
            log(f"plant {key} lam {lam}: mean {np.nanmean(vals):.4f} (baseline {np.nanmean(ref):.4f}) outside {frac_out:.2f} ({time.time() - t0:.0f}s)")
            if mde is None and frac_out >= 0.8:
                mde = {'lam': float(lam), 'effect': float(abs(np.nanmean(vals) - np.nanmean(ref)))}
            _W['prohibit'] = None
            if (OUT / 'prohibit_tmp.json').exists():
                (OUT / 'prohibit_tmp.json').unlink()
            res['plants'][key]['MDE80'] = mde
            json.dump(res, open(OUT / 'plants779_interim.json', 'w', encoding='utf-8'), indent=1)   # interim write per point
        res['plants'][key]['MDE80'] = mde
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(OUT / 'plants779.json', 'w', encoding='utf-8'), indent=1)
    log('plants done')


# ================================================================================================ locked stages
CHECKPOINT = 500                       # members between partial writes (edit 16)


def _partial_paths():
    return OUT / 'raw779_run_partial.npz', OUT / 'run779_partial_state.json'


def _save_partial(D, P, X, F, Z, done, names):
    npz, st = _partial_paths()
    tmp = OUT / 'raw779_run_partial.tmp.npz'
    np.savez_compressed(tmp, **{f'D_{n}': D[n] for n in names}, **{f'P_{n}': P[n] for n in names},
                        **{f'X_{n}': X[n] for n in names}, **{f'F_{n}': F[n] for n in names})
    os.replace(tmp, npz)
    tmp2 = OUT / 'run779_partial_state.tmp.json'
    json.dump({'done': sorted(list(x) for x in done), 'Z': {n: {f'{m},{b}': z for (m, b), z in Z[n].items()} for n in Z}},
              open(tmp2, 'w', encoding='utf-8'))
    os.replace(tmp2, st)


def _resume_check(D, P, X, Z, done_list, by_key, cellset, n_check=5):
    """Regenerate n_check already-written members from their seeds; every stored value must reproduce exactly."""
    rng = np.random.default_rng(779_777)
    pick = rng.choice(len(done_list), size=min(n_check, len(done_list)), replace=False)
    for i in pick:
        n, m, b = done_list[i]
        r = member(by_key[(n, m, b)])
        ok = True
        if b == 0:
            ok &= bool(np.allclose(D[n][m], r['D'], rtol=0, atol=0, equal_nan=True))
            ok &= bool(np.allclose(P[n][m], r['P'], rtol=0, atol=0, equal_nan=True))
            ok &= bool(np.allclose(X[n][m], r['X'], rtol=0, atol=0, equal_nan=True))
        if 'pairs' in r:
            a, bb, c = r['pairs']
            pres = set(zip(a.tolist(), bb.tolist()))
            ok &= Z[n][(m, b)] == sum(1 for k in cellset if k not in pres)
        log(f'  resume check {n} m{m} block{b}: {"ok" if ok else "MISMATCH"}')
        if not ok:
            raise RuntimeError('HARNESS-FAIL: a resumed member does not reproduce its stored values')


def stage_run():
    t0 = time.time()
    M = _W['M']
    names = [v[0] for v in VARIANTS]
    cells = json.load(open(OUT / 'pair_cells779.json', encoding='utf-8'))['cells']
    cellset = [tuple(c) for c in cells]
    npz, st = _partial_paths()
    resumed = npz.exists() and st.exists()
    if not resumed:
        B, bpairs = b_values()
        present = set(bpairs)
        B['P6z_pair_zeros'] = sum(1 for k in cellset if k not in present)
        json.dump(B, open(OUT / 'b_values779.json', 'w', encoding='utf-8'), indent=1)
        log('B: ' + ', '.join(f'{d} {B["D"][d]:.4f}' for d in DS))
        log('B counted: ' + ', '.join(f'{k.split("_")[0]} {v:.4f}' for k, v in B['P'].items()) + f' | P6z {B["P6z_pair_zeros"]}')
        log('B descriptive: ' + ', '.join(f'{k.split("_")[0] if k.startswith("P") else k} {v}' for k, v in B['X'].items()))
    tasks = [(n, m, SEED_RUN + 10_000 * i, None, 0.0, n in (PRIMARY, BASELINE), 0) for i, n in enumerate(names) for m in range(N_MEMBERS)]
    tasks += [(n, m, SEED_RUN2 + 10_000 * i, None, 0.0, True, 1) for i, n in enumerate(names) if n in (PRIMARY, BASELINE) for m in range(N_MEMBERS)]
    by_key = {(t[0], t[1], t[6]): t for t in tasks}
    D = {n: np.full((N_MEMBERS, len(DS)), np.nan) for n in names}
    P = {n: np.full((N_MEMBERS, len(M.COUNTED)), np.nan) for n in names}
    X = {n: np.full((N_MEMBERS, len(M.DESCRIPTIVE)), np.nan) for n in names}
    F = {n: np.full((N_MEMBERS, 3), np.nan) for n in names}
    Z = {n: {} for n in (PRIMARY, BASELINE)}          # pair zeros, two seed blocks
    done = set()
    if resumed:
        with np.load(npz) as raw:                      # closed before the next os.replace (Windows)
            for n in names:
                D[n], P[n], X[n], F[n] = (np.array(raw[f'D_{n}']), np.array(raw[f'P_{n}']),
                                          np.array(raw[f'X_{n}']), np.array(raw[f'F_{n}']))
        state = json.load(open(st, encoding='utf-8'))
        for n in state['Z']:
            Z[n] = {(int(k.split(',')[0]), int(k.split(',')[1])): z for k, z in state['Z'][n].items()}
        done = set(tuple(x) for x in state['done'])
        log(f'resuming: {len(done)}/{len(tasks)} members already written; verifying 5 from their seeds')
        _resume_check(D, P, X, Z, sorted(done), by_key, cellset)
        log('resume check passed')
    todo = [t for t in tasks if (t[0], t[1], t[6]) not in done]
    count = 0
    for r in pool_map(member, todo, init_kappa=kappa_locked()):
        n, m, block = r['name'], r['member'], r['block']
        if 'pairs' in r:
            a, b, c = r['pairs']
            pres = set(zip(a.tolist(), b.tolist()))
            Z[n][(m, block)] = sum(1 for k in cellset if k not in pres)
        if block == 0:
            D[n][m] = r['D']; P[n][m] = r['P']; X[n][m] = r['X']; F[n][m] = r['F']
        done.add((n, m, block))
        count += 1
        if count % CHECKPOINT == 0:
            _save_partial(D, P, X, F, Z, done, names)
            log(f'  run: {len(done)}/{len(tasks)} ({time.time() - t0:.0f}s)')
    np.savez_compressed(OUT / 'raw779_run.npz', **{f'D_{n}': D[n] for n in names}, **{f'P_{n}': P[n] for n in names},
                        **{f'X_{n}': X[n] for n in names}, **{f'F_{n}': F[n] for n in names})
    json.dump({n: {f'{m},{b}': z for (m, b), z in Z[n].items()} for n in Z}, open(OUT / 'pair_zeros779.json', 'w'))
    log(f'run done ({time.time() - t0:.0f}s; {len(done)} members)')


SEED_SENS = 779_300_000
N_SENS = 200


def stage_sens():
    """Descriptive sensitivity (pre-registration, Decision rules): the primary at kappa x 0.5 and x 2 and at kappa_z
    x 0.5 and x 2, N_SENS members each (own seed block SEED_SENS + 10,000 x setting + member), read against B's
    locked values. Not a verdict input. Writes a partial file per setting and resumes after a verified match."""
    t0 = time.time()
    M = _W['M']
    B = json.load(open(OUT / 'b_values779.json', encoding='utf-8'))
    kappa = kappa_locked()
    settings = [('kappa_x0.5', kappa * 0.5, M.KZ), ('kappa_x2', kappa * 2.0, M.KZ),
                ('kz_x0.5', kappa, M.KZ * 0.5), ('kz_x2', kappa, M.KZ * 2.0)]
    part = OUT / 'sens779_partial.json'
    res = json.load(open(part, encoding='utf-8')) if part.exists() else {'kappa_locked': kappa, 'kz': M.KZ, 'N': N_SENS, 'seed': SEED_SENS, 'settings': {}}
    kP = len(M.COUNTED) + 1
    for i, (name, ka, kz) in enumerate(settings):
        if name in res['settings']:
            sv = res['settings'][name]
            _init(ka, kz)
            rng = np.random.default_rng(779_778 + i)
            for m in rng.choice(N_SENS, size=5, replace=False):
                r = member((PRIMARY, int(m), SEED_SENS + 10_000 * i, None, 0.0, False))
                if not (np.allclose(sv['members']['D'][m], r['D'], rtol=0, atol=0, equal_nan=True) and
                        np.allclose(sv['members']['P'][m], r['P'], rtol=0, atol=0, equal_nan=True)):
                    raise RuntimeError(f'HARNESS-FAIL: resumed sens member {name} m{m} does not reproduce')
            _init()
            log(f'sens {name}: already done; 5 members re-verified')
            continue
        tasks = [(PRIMARY, m, SEED_SENS + 10_000 * i, None, 0.0, False) for m in range(N_SENS)]
        Dm = np.full((N_SENS, len(DS)), np.nan); Pm = np.full((N_SENS, len(M.COUNTED)), np.nan)
        for r in pool_map(member, tasks, init_kappa=ka, init_kz=kz):
            Dm[r['member']] = r['D']; Pm[r['member']] = r['P']
        dd = {d: dict(summ(Dm[:, j], B['D'][d]), outside=outside(B['D'][d], Dm[:, j], 5)) for j, d in enumerate(DS)}
        pp = {k: dict(summ(Pm[:, j], B['P'][k]), outside=outside(B['P'][k], Pm[:, j], kP)) for j, k in enumerate(M.COUNTED)}
        res['settings'][name] = {'kappa': ka, 'kz': kz, 'D': dd, 'P': pp, 'members': {'D': Dm.tolist(), 'P': Pm.tolist()}}
        tmp = OUT / 'sens779_partial.tmp.json'
        json.dump(res, open(tmp, 'w', encoding='utf-8'))
        os.replace(tmp, part)
        log(f"sens {name} (kappa {ka:g}, kz {kz:g}): " + ' '.join(f"{d} z{dd[d]['z_B']:+.1f}{'*' if dd[d]['outside'] else ''}" for d in DS)
            + ' | ' + ' '.join(f"{k.split('_')[0]} z{pp[k]['z_B']:+.1f}{'*' if pp[k]['outside'] else ''}" for k in M.COUNTED)
            + f" ({time.time() - t0:.0f}s)")
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(OUT / 'sens779.json', 'w', encoding='utf-8'), indent=1)
    log('sens done')


def strength_order(plant, lams):
    """Weakest plant first: larger kappa_p is weaker for P2; smaller lam / m is weaker otherwise."""
    return sorted(lams, key=lambda x: -x) if plant == 'P2' else sorted(lams)


def plant_seed(key, plant, lam, pts, plants_file):
    """The seed base a plant point was generated from: stage points follow the stage formula, extension points carry
    their seed in the file's extension record."""
    kidx = list(_W['M'].PLANTS).index(key)
    pk = next(k for k in pts if float(k) == float(lam))
    if pts[pk].get('source') == 'extension':
        return next(e['seed'] for e in plants_file.get('extensions', []) if e['key'] == key and float(e['lam']) == float(lam))
    return SEED_PLANT + 10_000 * (kidx + 1) + int(lam * 100)


def walk_mde80(order, fracs):
    """Pure walk rule on a weakest-first grid: start at the strongest point below 0.8 (or the weakest point), move up;
    MDE80 = the first point with >= 0.8 whose next stronger point (if any) also has >= 0.8. `fracs(lam)` is called
    lazily (reruns). Returns (mde_lam, last_fail_lam, visited)."""
    below = [lam for lam in order if fracs.known(lam) and fracs.known(lam) < 0.8]
    i = order.index(below[-1]) if below else 0
    last_fail = None
    visited = []
    while i < len(order):
        lam = order[i]
        f = fracs(lam); visited.append(lam)
        if f < 0.8:
            last_fail = lam; i += 1; continue
        if i + 1 < len(order):
            f2 = fracs(order[i + 1]); visited.append(order[i + 1])
            if f2 < 0.8:
                last_fail = order[i + 1]; i += 2; continue
        return lam, last_fail, visited
    return None, last_fail, visited


def stage_plantcheck():
    """Locked stage after `run` (edit 3): rerun the plant points around each plant's pre-lock MDE80 from their seeds
    (generated members only), store per-member values, and recompute each point's fraction outside against the
    LOCKED primary ensemble and criterion (continuous: R2L block 0, N 1,000, beyond [min, max] and |z| > z*; P6z:
    pooled R2L N 2,000, strictly beyond every member). Every rerun mean must reproduce the pre-lock table to four
    decimals, else the plant is flagged and its MDE80 void. Writes results/plantcheck779.json."""
    t0 = time.time()
    M = _W['M']
    kappa = kappa_locked()
    plants = json.load(open(OUT / 'plants779.json', encoding='utf-8'))
    raw = np.load(OUT / 'raw779_run.npz')
    Pprim = raw[f'P_{PRIMARY}']
    Zs = json.load(open(OUT / 'pair_zeros779.json', encoding='utf-8'))
    zprim = np.array(list(Zs[PRIMARY].values()), float)
    cells_f = json.load(open(OUT / 'pair_cells779.json', encoding='utf-8'))
    cells = [tuple(c) for c in cells_f['cells']]
    _W['pair_expect'] = {tuple(int(x) for x in k.split(',')): e for k, e in cells_f['expect'].items()}
    kP = len(M.COUNTED) + 1
    res = {'kappa': kappa, 'N_plant': N_PLANT, 'N_primary_continuous': int((~np.isnan(Pprim[:, 0])).sum()),
           'N_primary_P6z_pooled': int(len(zprim)), 'z_star': zstar(kP), 'plants': {}}
    for key, (plant, grid) in M.PLANTS.items():
        entry = plants['plants'][key]
        pts = entry['points']
        order = strength_order(plant, [float(x) for x in pts])
        j = M.COUNTED.index(key) if key in M.COUNTED else None
        ref = zprim if plant == 'P6' else Pprim[:, j]
        ref_mean = float(np.nanmean(ref))
        rerun = {}

        class Fr:
            def known(self, lam):
                pk = next(k for k in pts if float(k) == lam)
                return pts[pk]['frac_outside']

            def __call__(self, lam):
                pk = next(k for k in pts if float(k) == lam)
                if pk in rerun:
                    return rerun[pk]['frac_outside']
                seed = plant_seed(key, plant, lam, pts, plants)
                rng0 = np.random.default_rng(SEED_PLANT + 777)
                if plant == 'P6':
                    pro = _prohibit_cells(rng0, int(lam))
                    json.dump({a: sorted(b) for a, b in pro.items()}, open(OUT / 'prohibit_tmp.json', 'w'))
                tasks = [(PRIMARY, m, seed, plant, float(lam), plant == 'P6') for m in range(N_PLANT)]
                vals = np.full(N_PLANT, np.nan)
                for r in pool_map(member, tasks, init_kappa=kappa):
                    if plant == 'P6':
                        a, b, c = r['pairs']
                        present = set(zip(a.tolist(), b.tolist()))
                        vals[r['member']] = sum(1 for k in cells if k not in present)
                    else:
                        vals[r['member']] = r['P'][j]
                if (OUT / 'prohibit_tmp.json').exists():
                    (OUT / 'prohibit_tmp.json').unlink()
                frac = float(np.mean([outside(v, ref, kP, discrete=(plant == 'P6')) for v in vals]))
                mean = float(np.nanmean(vals))
                rerun[pk] = {'seed': seed, 'members': vals.tolist(), 'mean': mean, 'sd': float(np.nanstd(vals, ddof=1)),
                             'mean_prelock': pts[pk]['mean'], 'reproduces': bool(abs(mean - pts[pk]['mean']) < 6e-5),
                             'frac_outside_prelock': pts[pk]['frac_outside'], 'frac_outside': frac,
                             'effect': float(abs(mean - ref_mean))}
                log(f"  plantcheck {key} lam {lam:g}: mean {mean:.4f} (pre-lock {pts[pk]['mean']:.4f}, reproduces {rerun[pk]['reproduces']}); "
                    f"outside {frac:.2f} against N {len(ref)} (pre-lock {pts[pk]['frac_outside']:.2f}) ({time.time() - t0:.0f}s)")
                return frac

        fr = Fr()
        mde_lam, last_fail, visited = walk_mde80(order, fr)
        ok = all(rerun[k]['reproduces'] for k in rerun)
        mde = None
        if mde_lam is not None and ok:
            pk = next(k for k in pts if float(k) == mde_lam)
            mde = {'lam': float(mde_lam), 'effect': rerun[pk]['effect']}
        low = None
        if last_fail is not None:
            pk = next(k for k in pts if float(k) == last_fail)
            low = rerun[pk]['effect']
        res['plants'][key] = {'plant': plant, 'rerun': rerun, 'visited': visited, 'all_reproduce': ok,
                              'MDE80': mde, 'bracket': [low, mde['effect'] if mde else None],
                              'MDE80_prelock': entry['MDE80'], 'primary_mean_locked': ref_mean}
        log(f"plantcheck {key}: MDE80 {mde} (pre-lock {entry['MDE80']}); bracket {res['plants'][key]['bracket']}; reproduces {ok}")
        tmp = OUT / 'plantcheck779.tmp.json'
        json.dump(res, open(tmp, 'w', encoding='utf-8'))
        os.replace(tmp, OUT / 'plantcheck779.json')
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(OUT / 'plantcheck779.json', 'w', encoding='utf-8'), indent=1)
    log('plantcheck done')


def stage_verdict():
    M = _W['M']
    B = json.load(open(OUT / 'b_values779.json', encoding='utf-8'))
    raw = np.load(OUT / 'raw779_run.npz')
    Zs = json.load(open(OUT / 'pair_zeros779.json', encoding='utf-8'))
    plants = json.load(open(OUT / 'plants779.json', encoding='utf-8'))
    pc_f = OUT / 'plantcheck779.json'
    assert pc_f.exists(), 'plantcheck779.json missing: run `run779.py plantcheck` before the verdict'
    pcheck = json.load(open(pc_f, encoding='utf-8'))['plants']
    names = [v[0] for v in VARIANTS]
    counted = M.COUNTED + ['P6z_pair_zeros']
    kP = len(counted)
    rows = {}
    for n in names:
        D, P, X, F = raw[f'D_{n}'], raw[f'P_{n}'], raw[f'X_{n}'], raw[f'F_{n}']
        dd = {d: dict(summ(D[:, j], B['D'][d]), outside=outside(B['D'][d], D[:, j], 5)) for j, d in enumerate(DS)}
        pp = {}
        for j, k in enumerate(M.COUNTED):
            if n in NO_COMPOSITION_READ and k in ('P2_paragraph_prefix_jsd', 'P10_hapax_dispersion'):
                continue
            pp[k] = dict(summ(P[:, j], B['P'][k]), outside=outside(B['P'][k], P[:, j], kP))
        if n in Zs:
            zv = np.array(list(Zs[n].values()), float)
            pp['P6z_pair_zeros'] = dict(summ(zv, B['P6z_pair_zeros']), outside=outside(B['P6z_pair_zeros'], zv, kP, discrete=True), pooled_n=int(len(zv)))
        xx = {k: summ(X[:, j], B['X'][k]) for j, k in enumerate(M.DESCRIPTIVE)}
        ff = dict(zip(('mi_route2_raw', 'mi_edge_first_half_raw', 'mi_edge_second_half_raw'), np.nanmean(F, axis=0).tolist()))
        rows[n] = {'D': dd, 'P': pp, 'X': xx, 'F': ff,
                   'panel_pass': not any(dd[d]['outside'] for d in PANEL_TESTED),
                   'fidelity_D2_outside': dd['D2']['outside'], 'fidelity_D6_outside': dd['D6']['outside']}
    # three-way power rule on the primary, applied in order (edits 5, 6); MDE80 from the locked recomputation (edit 3)
    d2_failed = bool(rows[PRIMARY]['fidelity_D2_outside'])
    memo_marginal = bool(rows['R2Lmemo']['fidelity_D6_outside'])
    verdicts = {}
    for k in counted:
        b = B['P'][k] if k in B['P'] else B['P6z_pair_zeros']
        prim, base = rows[PRIMARY]['P'][k], rows[BASELINE]['P'][k]
        out_base = base['outside']; out_prim = prim['outside']
        pc = pcheck.get(k, {})
        mde = pc.get('MDE80')
        excess = b - base['mean']                      # signed; every plant moves its statistic upward
        if out_prim:
            v = 'NOT REPRODUCED'
        elif not out_base:
            v = 'NO EXCESS DETECTED OVER THE WITHIN-CELL SHUFFLE'
        elif mde is not None and excess > 0 and mde['effect'] <= abs(excess):
            v = 'REPRODUCED (powered)'
        else:
            v = 'REPRODUCED (unpowered)'
        sens = [n for n in ('R3L', 'R2Lw', 'R2Lmemo', 'R2P') if k in rows[n]['P'] and rows[n]['P'][k]['outside'] != out_prim]
        verdicts[k] = {'verdict': v, 'B': b, 'primary': prim, 'baseline': base, 'MDE80': mde, 'MDE80_bracket': pc.get('bracket'),
                       'MDE80_prelock': pc.get('MDE80_prelock'), 'plant_reproduces': pc.get('all_reproduce'),
                       'excess_over_baseline_signed': excess,
                       'mde_ratio': (mde['effect'] / abs(excess)) if (mde is not None and excess != 0) else None,
                       'sampler_sensitive': sens, 'D2_fidelity_failed_in_locked_run': d2_failed,
                       'partly_unblinded': k in ('P7_erun_lag1_agree', 'P8_qo_chsh_alternation')}
    ladder = [n for n in LADDER if rows[n]['panel_pass']]
    sens_f = OUT / 'sens779.json'
    sensitivity = json.load(open(sens_f, encoding='utf-8'))['settings'] if sens_f.exists() else None
    out = {'B': B, 'kappa': kappa_locked(), 'z_star_P': zstar(kP), 'rows': rows, 'verdicts': verdicts,
           'primary': PRIMARY, 'primary_panel_pass': rows[PRIMARY]['panel_pass'], 'MIN_D_descriptive': ladder[0] if ladder else None,
           'ladder_passing': ladder, 'sensitivity_descriptive': sensitivity,
           'R2Lmemo_fidelity_marginal': memo_marginal, 'D2_fidelity_failed_in_locked_run': d2_failed}
    json.dump(out, open(OUT / 'verdict779.json', 'w', encoding='utf-8'), indent=1)
    log(f"primary {PRIMARY}: panel (D3-D5) pass {rows[PRIMARY]['panel_pass']}; D2 fidelity outside {rows[PRIMARY]['fidelity_D2_outside']}; "
        f"MIN-D (descriptive) {out['MIN_D_descriptive']}")
    for n in names:
        r = rows[n]
        log(f"  {n:8s} " + ' '.join(f"{d} {r['D'][d]['mean']:+.3f}(z{r['D'][d]['z_B']:+.1f}{'*' if r['D'][d]['outside'] else ''})" for d in DS))
    for k, v in verdicts.items():
        log(f"  {k:34s} {v['verdict']:44s} B {v['B']:.4f} primary {v['primary']['mean']:.4f}±{v['primary']['sd']:.4f} z {v['primary']['z_B']:+.2f} rank {v['primary']['rank_B']} | base z {v['baseline']['z_B']:+.2f} excess {v['excess_over_baseline_signed']:+.4f} | MDE80 {v['MDE80']} ratio {v['mde_ratio']} | sens {v['sampler_sensitive']}")
    log(f"  R2Lmemo fidelity-marginal (D6 outside at N 1,000): {memo_marginal}; primary D2 fidelity failed: {d2_failed}")
    if sensitivity:
        for name, sv in sensitivity.items():
            log(f"  sensitivity {name:10s} " + ' '.join(f"{k.split('_')[0]} z{sv['P'][k]['z_B']:+.1f}{'*' if sv['P'][k]['outside'] else ''}" for k in M.COUNTED))


def dry_run():
    global LOGF
    (OUT / 'dryrun').mkdir(exist_ok=True)
    LOGF = open(OUT / 'dryrun' / 'dryrun_log.txt', 'w', encoding='utf-8')
    _init(2.0)
    M = _W['M']
    for v in VARIANTS:
        for m in range(2):
            r = member((v[0], m, 1, None, 0.0, v[0] == PRIMARY))
            log(f"[dry] {v[0]:8s} m{m} D " + ' '.join(f'{d} {x:+.3f}' for d, x in zip(DS, r['D'])) +
                ' | P ' + ' '.join(f"{k.split('_')[0]} {x:+.3f}" for k, x in zip(M.COUNTED, r['P'])) +
                ' | F ' + ' '.join(f'{x:.3f}' for x in r['F']) + f" | MH acc {r['MH'][0]:.2f} changed {r['MH'][1]:.2f}")
    for key, (plant, grid) in M.PLANTS.items():
        if plant == 'P6':
            continue
        r = member((PRIMARY, 0, 2, plant, float(grid[-1]), False))
        j = M.COUNTED.index(key)
        log(f"[dry] plant {plant} lam {grid[-1]}: {key.split('_')[0]} {r['P'][j]:+.4f}")
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
    assert stage in ('fidelity', 'plants', 'run', 'sens', 'plantcheck', 'verdict'), 'stage: fidelity | plants | run | sens | plantcheck | verdict'
    if stage in ('run', 'sens', 'plantcheck', 'verdict'):
        verify_lock()
    _init()
    LOGF = open(OUT / f'{stage}_log779.txt', 'a', encoding='utf-8')
    log(f'PHASE_779 {stage}; {"lock " + LOCK + " verified; " if stage in ("run", "sens", "plantcheck", "verdict") else ""}{time.strftime("%Y-%m-%d %H:%M:%S")}')
    {'fidelity': stage_fidelity, 'plants': stage_plants, 'run': stage_run, 'sens': stage_sens, 'plantcheck': stage_plantcheck,
     'verdict': stage_verdict}[stage]()
    log('done')


if __name__ == '__main__':
    main()
