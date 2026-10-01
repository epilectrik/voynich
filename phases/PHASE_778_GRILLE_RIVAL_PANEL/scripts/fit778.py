"""PHASE_778 fit stage (surface statistics only; no panel statistic is computed).

For each declared FAMILY (row arrangement x vertical wandering x line rule x repeat rule) the fitted parameters
(parser, row construction, table scope, table size, draw exponent, number of tables, grille change rate, grille set)
are chosen to minimise the mean scaled distance between the generated corpora's surface statistics and B's:
types, hapax type fraction, Zipf slope, mean token length, adjacent- and distant-folio type-set Jaccard
(scales in grille778.SCALE). N_FIT members per configuration. Output: results/fit778.json (the panel's variant table).

Usage: python fit778.py [workers]
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
N_FIT = 3
SEED0 = 778_500_000

ORDERS = ['random', 'freq', 'length', 'chain']
DS = [2, 5, 'R']
POSS = ['reset', 'continue']
REPEATS = ['keep', 'avoid']
FAMILIES = [{'order': o, 'd': d, 'pos': p, 'repeat': r} for o, d, p, r in itertools.product(ORDERS, DS, POSS, REPEATS)]

PARSERS = ['morph', 'stolfi']
ROWS = ['indep', 'real']
SCOPES = {'all': [(40, 16), (120, 16), (250, 20), (500, 20)],
          'section': [(40, 16), (120, 16), (250, 20)],
          'folio': [(40, 8), (40, 16), (80, 16)]}
ALPHAS = [0.5, 1.0]
NTABS = [1, 3]
SGRS = [0.05, 0.3]
GRILLES = ['all', [(0, 0)]]


def configs():
    out = []
    for parser, rows, scope, alpha, n_tab, s_gr, gr in itertools.product(PARSERS, ROWS, SCOPES, ALPHAS, NTABS, SGRS,
                                                                            GRILLES):
        for R, G in SCOPES[scope]:
            out.append({'parser': parser, 'rows': rows, 'scope': scope, 'R': R, 'G': G, 'alpha': alpha,
                        'n_tab': n_tab, 's_gr': s_gr, 'grilles': gr})
    return out


def family_name(f):
    return f"{f['order']}/d{f['d']}/{f['pos']}/{f['repeat']}"


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


def fit_family(fi):
    import numpy as np
    X = _setup()
    if 'sk' not in _W:
        _W['sk'] = X.skeleton()
        _W['inv'] = {p: X.inventory(_W['sk'], p) for p in PARSERS}
        _W['b'] = X.b_surface(_W['sk'])
    sk, b = _W['sk'], _W['b']
    fam = FAMILIES[fi]
    t0 = time.time()
    rows = []
    for ci, cfg in enumerate(configs()):
        full = {**fam, **cfg}
        ss = []
        for m in range(N_FIT):
            rng = np.random.default_rng(SEED0 + 100_000 * fi + 10 * ci + m)
            lines, info = X.generate(sk, _W['inv'][cfg['parser']], full, rng)
            ss.append(X.surface(lines, sk['folio'], _W['inv'][cfg['parser']]['types']))
        mean = {k: float(np.mean([s[k] for s in ss])) for k in ss[0]}
        rows.append({'cfg': cfg, 'surface': mean, 'distance': X.distance(mean, b)})
    rows.sort(key=lambda r: r['distance'])
    return fi, {'family': fam, 'name': family_name(fam), 'best': rows[0], 'top5': rows[:5],
                'n_configs': len(rows), 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    OUT.mkdir(exist_ok=True)
    T0 = time.time()
    out = {}
    fn = OUT / 'fit778.json'
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fit_family, fi): fi for fi in range(len(FAMILIES))}
        for f in as_completed(futs):
            try:
                fi, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED family {futs[f]}: {e!r}', flush=True)
                continue
            out[r['name']] = r
            b = r['best']
            print(f"[{time.time() - T0:6.0f}s] {r['name']:28s} dist {b['distance']:.2f} "
                  f"{b['cfg']} {{{', '.join(f'{k} {v:.3f}' for k, v in b['surface'].items())}}} ({r['runtime_s']:.0f}s)",
                  flush=True)
            json.dump({'families': out, 'N_FIT': N_FIT, 'seed0': SEED0, 'n_configs': len(configs())},
                      open(fn, 'w', encoding='utf-8'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
