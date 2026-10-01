"""PHASE_778 fit-grid extension (surface statistics only; declared before the lock).

The base fit (fit778.py) left every group short on hapax share and type count: a table-and-grille device re-reads its
cells, so its vocabulary is poorer than B's. To give the device its best shot at B's composition, the grid is extended
toward richer tables: a larger per-folio table, (R, G) = (250, 20) at scope = folio, and a flatter draw
exponent alpha = 0.25 at every scope and size. Only the new configurations are evaluated (same N_FIT, distinct seeds);
a group's selected configuration is replaced when a new one has a lower distance, and the replacement is re-evaluated
on 10 fresh seeds. The record keeps the base selection alongside. No order statistic is involved.

Usage: python fit_extend778.py [workers]
"""
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import fit778 as F  # noqa: E402

EXT_FOLIO_SIZES = [(250, 20)]
EXT_ALPHA = 0.25
CI_OFFSET = 20_000


def ext_configs(restricted):
    base = {json.dumps(c, sort_keys=True) for c in F.configs(restricted)}
    out = []
    for parser, rows, n_tab, s_gr, gr in itertools.product(F.PARSERS, F.ROWS, F.NTABS, F.SGRS, F.GRILLES):
        if restricted and (rows != 'indep' or gr != 'distinct'):
            continue
        for R, G in EXT_FOLIO_SIZES:
            for alpha in F.ALPHAS + [EXT_ALPHA]:
                out.append({'parser': parser, 'rows': rows, 'scope': 'folio', 'R': R, 'G': G, 'alpha': alpha,
                            'n_tab': n_tab, 's_gr': s_gr, 'grilles': gr})
        for scope, sizes in F.SCOPES.items():
            for R, G in sizes:
                out.append({'parser': parser, 'rows': rows, 'scope': scope, 'R': R, 'G': G, 'alpha': EXT_ALPHA,
                            'n_tab': n_tab, 's_gr': s_gr, 'grilles': gr})
    return [c for c in out if json.dumps(c, sort_keys=True) not in base]


def extend_group(gi):
    W = F._world()
    X = W['X']
    g = F.groups()[gi]
    walk = {k: g[k] for k in ('d', 'pos', 'repeat', 'redraw')}
    t0 = time.time()
    rows = []
    for ci, cfg in enumerate(ext_configs(g['restricted'])):
        mean, dist = F.eval_cfg(gi, ci, cfg, walk, [F.SEED0 + 100_000 * gi + 10 * (CI_OFFSET + ci) + m
                                                     for m in range(F.N_FIT)])
        rows.append({'cfg': cfg, 'surface': mean, 'distance': dist})
    rows.sort(key=lambda r: r['distance'])
    best = rows[0]
    fresh_mean, fresh_dist = F.eval_cfg(gi, 0, best['cfg'], walk, [F.SEED_FRESH + 1000 * gi + 500 + m
                                                                   for m in range(F.N_FRESH)])
    dev = X.deviations(fresh_mean, W['b'])
    tot = sum(dev.values())
    return gi, {'name': F.group_name(g), 'best': best,
                'fresh': {'surface': fresh_mean, 'distance': fresh_dist, 'band': X.band(fresh_dist), 'deviations': dev,
                          'dominant': max(dev, key=dev.get), 'dominant_share': max(dev.values()) / tot if tot else 0.0},
                'top5': rows[:5], 'n_configs': len(rows), 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    fn = OUT / 'fit778.json'
    fit = json.load(open(fn, encoding='utf-8'))
    assert fit.get('complete'), 'base fit must be complete'
    T0 = time.time()
    gs = F.groups()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(extend_group, gi): gi for gi in range(len(gs))}
        for f in as_completed(futs):
            try:
                gi, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED group {futs[f]}: {e!r}', flush=True)
                continue
            grp = fit['groups'][r['name']]
            grp.setdefault('base', {'best': grp['best'], 'fresh': grp['fresh'], 'top5': grp['top5']})
            replaced = r['best']['distance'] < grp['base']['best']['distance']
            grp['extension'] = {'best': r['best'], 'fresh': r['fresh'], 'top5': r['top5'], 'n_configs': r['n_configs'],
                                'replaced_base': replaced}
            if replaced:
                grp['best'], grp['fresh'] = r['best'], r['fresh']
                merged = sorted(grp['base']['top5'] + r['top5'], key=lambda x: x['distance'])[:5]
                grp['top5'] = merged
            fr = grp['fresh']
            print(f"[{time.time() - T0:6.0f}s] {r['name']:40s} ext dist {r['best']['distance']:.2f} "
                  f"({'replaces' if replaced else 'keeps'} base {grp['base']['best']['distance']:.2f}) -> fresh {fr['distance']:.2f} "
                  f"{fr['band']:8s} dominant {fr['dominant']} {fr['dominant_share']:.2f} {grp['best']['cfg']} ({r['runtime_s']:.0f}s)",
                  flush=True)
            fit['extension'] = {'folio_sizes': EXT_FOLIO_SIZES, 'alpha': EXT_ALPHA, 'ci_offset': CI_OFFSET,
                                'n_configs_full': len(ext_configs(False)), 'n_configs_restricted': len(ext_configs(True)),
                                'groups_done': sum(1 for g_ in fit['groups'].values() if 'extension' in g_)}
            json.dump(fit, open(fn, 'w', encoding='utf-8'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
