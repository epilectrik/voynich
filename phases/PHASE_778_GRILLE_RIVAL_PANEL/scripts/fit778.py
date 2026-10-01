"""PHASE_778 fit stage (surface statistics only; no panel statistic is computed).

FIT GROUPS. The surface statistics depend on the walk (d, pos, repeat, redraw) but not on the row arrangement
(order): the walk visits the same cells whatever is written in them, and over a corpus its row distribution is
uniform. So one fit per (d, pos, repeat, redraw) group is shared by the random / freq / length / chain families of that
group (the panel's descriptives verify this per variant). Each fit chooses, from the declared grid, the configuration
minimising the mean scaled distance between generated corpora (N_FIT members) and B on nine composition statistics
(grille778.SCALE); the selected configuration is then re-evaluated on 10 fresh seeds (winner's curse).

TIER ELIGIBILITY. PUBLISHED fits are restricted to rows = indep and grilles = distinct (holes at three different
heights), as Hyde & Rugg describe; EXTENDED / STEELMAN fits use the full grid.

Output: results/fit778.json (the panel's variant table).  Usage: python fit778.py [workers]
"""
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
N_FIT = 2
N_FRESH = 10
SEED0 = 778_500_000
SEED_FRESH = 778_600_000

PARSERS = ['morph', 'stolfi']
ROWS = ['indep', 'real']
SCOPES = {'all': [(40, 16), (120, 16), (500, 20)],
          'section': [(40, 16), (120, 16), (250, 20)],
          'folio': [(40, 8), (40, 16), (80, 16)]}
ALPHAS = [0.5, 1.0]
NTABS = [1, 3]
SGRS = [0.05, 0.3, 'word']
GRILLES = ['distinct', 'all', 'same']

# walk axes
D_POS = [(2, 'reset'), (2, 'continue'), (5, 'reset'), (5, 'continue'), ('R', 'reset'), ('R', 'continue'),
         ('RP', 'continue')]
REPEATS = ['keep', 'avoid']


def groups():
    """Fit groups: (d, pos, repeat, redraw, restricted)."""
    out = []
    for (d, pos), rep in itertools.product(D_POS, REPEATS):
        out.append({'d': d, 'pos': pos, 'repeat': rep, 'redraw': False, 'restricted': False})
        if d in (2, 5) and pos == 'reset':
            out.append({'d': d, 'pos': pos, 'repeat': rep, 'redraw': False, 'restricted': True})   # PUBLISHED
    for d, pos in D_POS:
        out.append({'d': d, 'pos': pos, 'repeat': 'keep', 'redraw': True, 'restricted': False})      # STEELMAN
    return out


def group_name(g):
    return f"d{g['d']}/{g['pos']}/{g['repeat']}/{'redraw' if g['redraw'] else 'noredraw'}/{'restricted' if g['restricted'] else 'full'}"


def families():
    """Families = variants before noise: (tier, order, group)."""
    out = []
    for g in groups():
        if g['restricted']:
            out.append({'tier': 'PUBLISHED', 'order': 'random', **g})
        elif g['redraw']:
            out.append({'tier': 'STEELMAN', 'order': 'random', **g})
            if g['d'] != 'RP':
                out.append({'tier': 'STEELMAN', 'order': 'chain', **g})
        else:
            for order in ('random', 'freq', 'length'):
                out.append({'tier': 'EXTENDED', 'order': order, **g})
            if g['d'] != 'RP' and g['repeat'] == 'keep':
                out.append({'tier': 'STEELMAN', 'order': 'chain', **g})
    return out


def family_name(f):
    return f"{f['tier']}/{f['order']}/{group_name(f)}"


def configs(restricted):
    out = []
    for parser, rows, scope, alpha, n_tab, s_gr, gr in itertools.product(
            PARSERS, ROWS, SCOPES, ALPHAS, NTABS, SGRS, GRILLES):
        if restricted and (rows != 'indep' or gr != 'distinct'):
            continue
        for R, G in SCOPES[scope]:
            out.append({'parser': parser, 'rows': rows, 'scope': scope, 'R': R, 'G': G, 'alpha': alpha,
                        'n_tab': n_tab, 's_gr': s_gr, 'grilles': gr})
    return out


def _setup():
    os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(HERE))
    import grille778 as X
    return X


_W = {}


def _world():
    X = _setup()
    if 'sk' not in _W:
        _W['X'] = X
        _W['sk'] = X.skeleton()
        _W['inv'] = {p: X.inventory(_W['sk'], p) for p in PARSERS}
        _W['b'] = X.load_b(_W['sk'])
    return _W


def eval_cfg(gi, ci, cfg, walk, seeds):
    import numpy as np
    W = _world()
    X, sk, b = W['X'], W['sk'], W['b']
    ss = []
    for s in seeds:
        rng = np.random.default_rng(s)
        lines, info = X.generate(sk, W['inv'][cfg['parser']], {'order': 'random', **walk, **cfg}, rng)
        ss.append(X.surface(lines, sk['folio'], b, W['inv'][cfg['parser']]['types']))
    mean = {k: float(np.mean([s[k] for s in ss])) for k in ss[0]}
    return mean, X.distance(mean, b)


def fit_group(gi):
    W = _world()
    X = W['X']
    g = groups()[gi]
    walk = {k: g[k] for k in ('d', 'pos', 'repeat', 'redraw')}
    t0 = time.time()
    rows = []
    for ci, cfg in enumerate(configs(g['restricted'])):
        mean, dist = eval_cfg(gi, ci, cfg, walk, [SEED0 + 100_000 * gi + 10 * ci + m for m in range(N_FIT)])
        rows.append({'cfg': cfg, 'surface': mean, 'distance': dist})
    rows.sort(key=lambda r: r['distance'])
    best = rows[0]
    fresh_mean, fresh_dist = eval_cfg(gi, 0, best['cfg'], walk, [SEED_FRESH + 1000 * gi + m for m in range(N_FRESH)])
    dev = X.deviations(fresh_mean, W['b'])
    tot = sum(dev.values())
    return gi, {'group': g, 'name': group_name(g), 'best': best, 'fresh': {'surface': fresh_mean, 'distance': fresh_dist,
                'band': X.band(fresh_dist), 'deviations': dev,
                'dominant': max(dev, key=dev.get), 'dominant_share': max(dev.values()) / tot if tot else 0.0},
                'top5': rows[:5], 'n_configs': len(rows), 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    OUT.mkdir(exist_ok=True)
    T0 = time.time()
    out = {}
    fn = OUT / 'fit778.json'
    gs = groups()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fit_group, gi): gi for gi in range(len(gs))}
        for f in as_completed(futs):
            try:
                gi, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED group {futs[f]}: {e!r}', flush=True)
                continue
            out[r['name']] = r
            fr = r['fresh']
            print(f"[{time.time() - T0:6.0f}s] {r['name']:40s} dist {r['best']['distance']:.2f} fresh {fr['distance']:.2f} "
                  f"{fr['band']:8s} dominant {fr['dominant']} {fr['dominant_share']:.2f} {r['best']['cfg']} ({r['runtime_s']:.0f}s)",
                  flush=True)
            json.dump({'groups': out, 'families': [{'name': family_name(f), **f} for f in families()],
                       'N_FIT': N_FIT, 'N_FRESH': N_FRESH, 'seed0': SEED0, 'seed_fresh': SEED_FRESH,
                       'n_configs_full': len(configs(False)), 'n_configs_restricted': len(configs(True)),
                       'complete': len(out) == len(gs)},
                      open(fn, 'w', encoding='utf-8'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
