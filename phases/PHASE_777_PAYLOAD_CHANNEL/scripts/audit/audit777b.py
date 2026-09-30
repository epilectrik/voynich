"""PHASE_777 lock audit, part 2 (controls only): do refined EF-F nulls remove structural no-payload plants while
keeping payload power?

Nulls (all exact; cells keyed so every key is invariant under within-cell permutation):
  EF      chan777 EF-F: (folio x line type, zone, own last two units, preceding last two units)
  EFq     EF plus the line-position quintile of the slot
  EFpar   EF with groups = paragraph x line type
  EFparq  both
Plants: audit777 families PAYBASE, PALPAR, PALLINE, PALPOS (F1 unless stated). Also a descriptive line-homogeneity
measure for each plant: mean within-line entropy of the channel symbols relative to a within-folio shuffle (percent
reduction; the registered B anchor C1214 is 3.8% at atom level, z -7.0).
Usage: python audit777b.py [workers]
"""
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit777 as A  # noqa: E402

OUT = A.OUT
R = A.R


def build_null_q(lines, groups, X):
    """EF-F with the line-position quintile added to the cell key (quintile is a layout property: invariant)."""
    E = X.E
    C = E.Corpus(lines, groups, sig=E.sig_fl2, ns=(2,))
    n = len(C.tok)
    last2 = [tuple(X.units(w)[-2:]) for w in C.vocab]
    pos, L = [], []
    for ln in lines:
        for p in range(len(ln)):
            pos.append(p)
            L.append(len(ln))
    keys = [None] * n
    for p in range(n):
        t = C.tok[p]
        if t < 0:
            continue
        prev = ('^',) if (p == 0 or C.line_of[p - 1] != C.line_of[p] or C.tok[p - 1] < 0) else last2[C.tok[p - 1]]
        q = min(4, int(5 * pos[p] / max(L[p], 1)))
        keys[p] = (int(C.fol_of[p]), int(C.zone[p]), q, last2[t], prev)
    return X._reset_cells(C, keys)


def score(lines, C, X, ch, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    K = X.Channel(C, X.CHANNELS[ch])
    obs = K.counts(C.tok)
    null = [K.counts(C.sample(rng)) for _ in range(R)]
    s = X._summ(obs['RPT7'], [x['RPT7'] for x in null], R)
    return {'z7': s['z'], 'p7': s['p'], 'obs7': s['obs'], 'null7': s['null_mean'], 'movable': C.frac_movable}


def line_entropy_reduction(lines, sk, X, ch, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    fn = X.CHANNELS[ch]

    def mean_H(ls):
        hs = []
        for ln in ls:
            s = [fn(w) for w in ln if w is not None]
            if len(s) < 4:
                continue
            c = np.array(list(Counter(s).values()), dtype=float)
            p = c / c.sum()
            hs.append(float(-(p * np.log2(p)).sum()))
        return float(np.mean(hs))
    h = mean_H(lines)
    by = {}
    for i, f in enumerate(sk['folios']):
        by.setdefault(f, []).append(i)
    hs = []
    for _ in range(20):
        sh = [list(ln) for ln in lines]
        for f, idx in by.items():
            toks = [w for i in idx for w in lines[i] if w is not None]
            rng.shuffle(toks)
            it = iter(toks)
            for i in idx:
                sh[i] = [None if w is None else next(it) for w in lines[i]]
        hs.append(mean_H(sh))
    hn = float(np.mean(hs))
    return {'H_line': h, 'H_line_shuffled': hn, 'pct_reduction': 100 * (hn - h) / hn, 'z': (h - hn) / max(float(np.std(hs, ddof=1)), 1e-9)}


def run_one(spec):
    X = A._setup()
    t0 = time.time()
    sk = X.HR.b_skeleton()
    kind, ch = spec[0], spec[1]
    lines, info = A.build(spec, X)
    assert lines != sk['lines'], 'refusing to score B'
    g_ef, g_par = X.GK.ef_groups(sk), A.par_groups(sk, X)
    res = {'EF': score(lines, X.build_null(lines, g_ef, 'EF-F'), X, ch, spec[3] + 11),
           'EFq': score(lines, build_null_q(lines, g_ef, X), X, ch, spec[3] + 12),
           'EFpar': score(lines, X.build_null(lines, g_par, 'EF-F'), X, ch, spec[3] + 13),
           'EFparq': score(lines, build_null_q(lines, g_par, X), X, ch, spec[3] + 14)}
    info['line_homog'] = line_entropy_reduction(lines, sk, X, ch, spec[3] + 15)
    return '|'.join(str(x) for x in spec), {**info, 'res': res, 'runtime_s': time.time() - t0}


def specs():
    S = [('PAYBASE', 'F1', ('LAT_mesue', None), 9800), ('PAYBASE', 'F2', ('LAT_mesue', None), 9801),
         ('PAYBASE', 'F1', ('NT_la', None), 9802), ('PAYBASE', 'F2', ('LAT_rec', None), 9803)]
    seed = 9810
    for kind, alphas in (('PALPAR', (5.0, 10.0)), ('PALLINE', (10.0, 20.0, 50.0)), ('PALPOS', (5.0, 10.0))):
        for a in alphas:
            S.append((kind, 'F1', a, seed)); seed += 1
    S.append(('PALPAR', 'F2', 5.0, seed)); seed += 1
    S.append(('PALPOS', 'F2', 5.0, seed)); seed += 1
    return S


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    A._setup()
    out, T0 = {}, time.time()
    fn = OUT / 'audit777b.json'
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs()}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED {futs[f]}: {e!r}', flush=True)
                continue
            out[name] = r
            x = r['res']
            lh = r['line_homog']
            print(f'[{time.time() - T0:5.0f}s] {name:34s} ' + ' | '.join(
                f'{g} z7 {x[g]["z7"]:6.1f} p {x[g]["p7"]:.3f} mv {x[g]["movable"]:.2f}' for g in x)
                + f" | lineH red {lh['pct_reduction']:.1f}% z {lh['z']:.1f}"
                + (f" | par disp {r['par_dispersion_chi2_df']:.2f}" if 'par_dispersion_chi2_df' in r else ''), flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
