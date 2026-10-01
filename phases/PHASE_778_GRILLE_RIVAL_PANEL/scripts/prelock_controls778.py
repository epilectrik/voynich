"""PHASE_778 pre-lock controls (generated corpora and PHASE_757's control ensembles only; nothing is computed on
Currier B's token order). Required by the lean-expert design audit; results go into PRE_REGISTRATION.md.

C1  Self-consistency (false-exclusion rate): for the best-fit variant of each tier plus four randomly chosen declared
    variants, an ensemble of N1 members and H held-out members of the same variant; each held-out member is tested with
    the panel's outside/exclusion rule against its own ensemble. Pass: at most 2% of held-out members excluded overall.
C2  Surface-band sanity: the nine-statistic distance of 10 M1 and 10 G-EDGE members; both must be FITTED (<= 1.0).
C3  Column-lock control: tokens drawn i.i.d. from the fitted PUBLISHED table's column-set vocabulary at each token's
    column set (reset line rule; no walk, no memory); D5 and D6 over 20 corpora. If the control's mean D5 lies above
    the 99th percentile of PHASE_757's M1 ensemble, D5 and D6 are merged into one count for pos = reset variants.
C5  Steelman plant check: CHAIN rows and JUNCTION REDRAW at their most favourable settings (d = 0, pos = continue,
    same-height grille) must reach at least 50% of PHASE_757's G-EDGE mean D2 (reference G-EDGE, not B).

Usage: python prelock_controls778.py [workers]
"""
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import run778 as R  # noqa: E402
import fit778 as F  # noqa: E402

N1, H = 500, 50
SEED_C1 = 778_700_000
N_C3, N_C5 = 20, 5
P757 = R.ROOT / R.P757 / 'results'


def _init():
    R._init()


def c1_member(args):
    vi, m = args
    return R.member((vi, m, SEED_C1, None))


def columnlock_member(args):
    cfg, seed = args
    X, sk = R._W['X'], R._W['sk']
    inv = R._W['inv'][cfg['parser']]
    rng = np.random.default_rng(seed)
    full = {**X.DEFAULT, **cfg, 'order': 'random'}
    grilles = X.GRILLE_SETS[full['grilles']]
    scope = full['scope']
    unit_of = (lambda li: 'all') if scope == 'all' else (lambda li: sk['section'][li]) if scope == 'section' \
        else (lambda li: sk['folio'][li])
    tables, out = {}, []
    for li, ln in enumerate(sk['lines']):
        u = unit_of(li)
        if u not in tables:
            tables[u] = [X.build_table(inv, full, rng) for _ in range(full['n_tab'])]
        tab = tables[u][int(rng.integers(full['n_tab']))]
        new, k = [], 0
        for w in ln:
            if w is None:
                new.append(None)
                continue
            g = k % full['G']
            word = ''
            for _ in range(10):
                word = tab.word(int(rng.integers(full['R'])), g, grilles[int(rng.integers(len(grilles)))])
                if word:
                    break
            new.append(word or 'o')
            k += 1
        out.append(new)
    st = X.S.all_stats(out, sk['folio'], rng)
    return [st[d] for d in R.DS]


def plant_member(args):
    kind, seed = args
    X, sk = R._W['X'], R._W['sk']
    inv = R._W['inv']['morph']
    rng = np.random.default_rng(seed)
    cfg = {'order': 'chain' if kind == 'chain' else 'random', 'redraw': kind == 'redraw', 'd': 0, 'pos': 'continue',
           'grilles': 'same', 'rows': 'indep', 'R': 40, 'G': 16, 'alpha': 1.0, 'n_tab': 1, 's_gr': 0.0}
    lines, info = X.generate(sk, inv, cfg, rng)
    st = X.S.all_stats(lines, sk['folio'], rng)
    return [st[d] for d in R.DS]


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    t0 = time.time()
    R._init()
    X, sk = R._W['X'], R._W['sk']
    vs = R._W['variants']
    assert vs, 'fit778.json must be complete'
    fit = json.load(open(OUT / 'fit778.json', encoding='utf-8'))
    cc757 = json.load(open(P757 / 'controls_certification.json', encoding='utf-8'))
    raw757 = np.load(P757 / 'controls_raw.npz')
    nonbuiltin = {d: cc757['certification'][d]['certified_by_non_builtin'] for d in R.DS}
    res = {}
    # ---------------------------------------------------------------- C2
    b = X.load_b(sk)
    rows = []
    for kind, gen in (('M1', R._W['m1']), ('GEDGE', R._W['ge'])):
        for m in range(10):
            rng = np.random.default_rng(778_800_000 + m)
            c = gen.generate(sk['lines'], rng)
            s = X.surface(c, sk['folio'], b)
            dev = X.deviations(s, b)
            rows.append({'kind': kind, 'member': m, 'distance': X.distance(s, b), 'band': X.band(X.distance(s, b)),
                         'deviations': dev})
    res['C2'] = {'rows': rows, 'pass': all(r['band'] == 'FITTED' for r in rows),
                 'mean_distance': {k: float(np.mean([r['distance'] for r in rows if r['kind'] == k])) for k in ('M1', 'GEDGE')}}
    print(f"C2: pass={res['C2']['pass']} mean distance {res['C2']['mean_distance']}", flush=True)
    # ---------------------------------------------------------------- C3
    pub = [v for v in vs if v['tier'] == 'PUBLISHED']
    cfg3 = min(pub, key=lambda v: v['fit_distance'])['cfg']
    with Pool(workers, initializer=_init) as pool:
        D3 = np.array(pool.map(columnlock_member, [(cfg3, 778_810_000 + i) for i in range(N_C3)]))
    m1_d5 = raw757['M1'][:, R.DS.index('D5')]
    p99 = float(np.percentile(m1_d5, 99))
    res['C3'] = {'cfg': cfg3, 'mean': dict(zip(R.DS, D3.mean(0).tolist())), 'sd': dict(zip(R.DS, D3.std(0, ddof=1).tolist())),
                 'M1_D5_p99': p99, 'merge_d5_d6_reset': bool(D3[:, R.DS.index('D5')].mean() > p99)}
    print(f"C3: column-lock D5 {res['C3']['mean']['D5']:.3f} D6 {res['C3']['mean']['D6']:.3f}; M1 D5 p99 {p99:.3f}; "
          f"merge={res['C3']['merge_d5_d6_reset']}", flush=True)
    # ---------------------------------------------------------------- C5
    with Pool(workers, initializer=_init) as pool:
        D5c = np.array(pool.map(plant_member, [('chain', 778_820_000 + i) for i in range(N_C5)]))
        D5r = np.array(pool.map(plant_member, [('redraw', 778_830_000 + i) for i in range(N_C5)]))
    ge_d2 = float(cc757['certification']['D2']['GEDGE']['mean'])
    res['C5'] = {'GEDGE_mean_D2': ge_d2, 'threshold': 0.5 * ge_d2,
                 'chain': {'mean': dict(zip(R.DS, D5c.mean(0).tolist())), 'pass': bool(D5c[:, 0].mean() >= 0.5 * ge_d2)},
                 'redraw': {'mean': dict(zip(R.DS, D5r.mean(0).tolist())), 'pass': bool(D5r[:, 0].mean() >= 0.5 * ge_d2)}}
    print(f"C5: chain D2 {D5c[:, 0].mean():.3f} redraw D2 {D5r[:, 0].mean():.3f} vs threshold {0.5 * ge_d2:.3f}", flush=True)
    # ---------------------------------------------------------------- C1
    picks = []
    for tier in ('PUBLISHED', 'EXTENDED', 'STEELMAN'):
        cand = [vi for vi, v in enumerate(vs) if v['tier'] == tier and v['noise'] == 'V0']
        picks.append(min(cand, key=lambda vi: vs[vi]['fit_distance']))
    rng = np.random.default_rng(778_701)
    rest = [vi for vi in range(len(vs)) if vi not in picks]
    picks += [int(x) for x in rng.choice(rest, size=4, replace=False)]
    merge = res['C3']['merge_d5_d6_reset']
    c1 = {}
    tot_ex = tot = 0
    for vi in picks:
        with Pool(workers, initializer=_init) as pool:
            D = np.array([r['D'] for r in pool.imap(c1_member, [(vi, m) for m in range(N1 + H)], chunksize=10)])
        ens, held = D[:N1], D[N1:]
        v = vs[vi]
        ds = R.counted_set(v['tier'], R.DS, None)
        k = len(ds)
        n_ex = 0
        per = []
        for h in held:
            outs = [d for d in ds if R.outside(h[R.DS.index(d)], ens[:, R.DS.index(d)], k)]
            n_out = len(outs) - (1 if (merge and v['family']['pos'] == 'reset' and v['family']['d'] != 'RP'
                                       and 'D5' in outs and 'D6' in outs) else 0)
            ex = n_out >= 2 and any(nonbuiltin[d] for d in outs)
            n_ex += ex
            per.append(outs)
        c1[v['name']] = {'tier': v['tier'], 'N1': N1, 'H': H, 'excluded': int(n_ex), 'rate': n_ex / H,
                         'outside_counts': {d: sum(1 for o in per if d in o) for d in ds}}
        tot_ex += n_ex
        tot += H
        print(f"C1: {v['name']:50s} held-out excluded {n_ex}/{H} ({time.time() - t0:.0f}s)", flush=True)
    res['C1'] = {'variants': c1, 'excluded': tot_ex, 'of': tot, 'rate': tot_ex / tot, 'pass': tot_ex / tot <= 0.02}
    res['pass'] = bool(res['C1']['pass'] and res['C2']['pass'] and res['C5']['chain']['pass'] and res['C5']['redraw']['pass'])
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(OUT / 'prelock_controls778.json', 'w', encoding='utf-8'), indent=1)
    print(f"ALL: pass={res['pass']} C1 rate {res['C1']['rate']:.3f} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == '__main__':
    main()
