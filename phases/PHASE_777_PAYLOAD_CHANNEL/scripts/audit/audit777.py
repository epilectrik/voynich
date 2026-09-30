"""PHASE_777 lean-expert lock audit (controls only; nothing is computed on B's token order).

Families (all laid into B's skeleton, filler drawn from B's routing pools exactly as chan777.payload_lines does):
  PAYBASE   the design payload construction (reproduction check)
  PAYNULL   the same letters, plus null words at B's tail-symbol mass (words whose channel symbol is one of the
            symbols the frequency-rank map leaves unused; letters not consumed) -> reproduces B's channel marginal
  PAYSUB    each letter's symbol replaced with probability r by a draw from B's channel marginal (misreadings,
            homophones); letters consumed
  PALPAR    no payload: channel symbols i.i.d. within each paragraph from a paragraph palette Dirichlet(a * m)
  PALLINE   no payload: the same with one palette per line
  PALPOS    no payload: one palette per line-position quintile (shared by the whole corpus)
Each run is scored on F1 and F2 under EF-F with B's groups (folio x line type) and, as a candidate descriptive, with
paragraph-keyed groups (paragraph x line type).

Usage: python audit777.py [workers]
Exposure: B's channel marginals and (preceding ending, symbol) pools (declared in the pre-registration), B's layout
(paragraph starts, line lengths). No repeat count, EF sample or order statistic on B.
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCR = HERE.parent
OUT = SCR.parent / 'results' / 'audit'
R = int(os.environ.get('R777A', 200))


def _setup():
    os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(SCR))
    import chan777 as X
    return X


def paragraphs(sk, X):
    lt = X.GK.b_line_types(sk)
    pid, cur, last_f = [], -1, None
    for f, t in zip(sk['folios'], lt):
        if t == 'H' or f != last_f:
            cur += 1
        pid.append(cur)
        last_f = f
    return pid, lt


def par_groups(sk, X):
    pid, lt = paragraphs(sk, X)
    return [f'{f}|P{p}|{t}' for f, p, t in zip(sk['folios'], pid, lt)]


def symbol_lines(symstream, sk, channel, seed, X):
    """chan777.payload_lines' filler construction with the channel symbols given directly (None = skip slot)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    P = X.b_pools(sk)
    cache = {}

    def draw(key, counter):
        if key not in cache:
            ks = list(counter)
            p = np.array([counter[k] for k in ks], dtype=float)
            cache[key] = (ks, np.cumsum(p / p.sum()))
        ks, cum = cache[key]
        return ks[min(int(np.searchsorted(cum, rng.random())), len(ks) - 1)]
    out, it = [], iter(symstream)
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            s = next(it)
            ctx = ('^',) if prev is None else tuple(X.units(prev)[-2:])
            pool = P['by_ctx'][channel].get((ctx, s))
            t = draw((ctx, s), pool) if pool and sum(pool.values()) >= 3 else draw(('S', s), P['by_sym'][channel][s])
            cur.append(t)
            prev = t
        out.append(cur)
    return out


def marginal(sk, X, ch):
    P = X.b_pools(sk)
    return Counter({s: sum(c.values()) for s, c in P['by_sym'][ch].items()})


def build(spec, X):
    import numpy as np
    kind, ch, par, seed = spec
    sk = X.HR.b_skeleton()
    n = X.HR.n_certain(sk)
    rng = np.random.default_rng(seed + 55)
    m = marginal(sk, X, ch)
    syms = sorted(m, key=lambda s: (-m[s], str(s)))
    mv = np.array([m[s] for s in syms], dtype=float)
    mv /= mv.sum()
    info = {}
    if kind.startswith('PAY'):
        text, extra = par
        words = X.G.plaintext_words(text)
        stream = X.letter_stream(words, n, offset=0)
        _, lmap = X.payload_lines(stream, sk, ch, seed)          # the design map (deterministic given the stream)
        used = set(lmap.values())
        tail = [s for s in syms if s not in used]
        tmass = float(sum(m[s] for s in tail) / sum(m.values()))
        info = {'text': text, 'tail_symbols': len(tail), 'tail_mass': tmass, 'used_symbols': len(used)}
        if kind == 'PAYBASE':
            lines, _ = X.payload_lines(stream, sk, ch, seed)
            return lines, info
        if kind == 'PAYNULL':
            tw = np.array([m[s] for s in tail], dtype=float)
            tw /= tw.sum()
            it = iter(stream)
            sym = []
            for _ in range(n):
                if rng.random() < tmass:
                    sym.append(tail[int(rng.choice(len(tail), p=tw))])
                else:
                    sym.append(lmap[next(it)])
            info['null_rate'] = tmass
            return symbol_lines(sym, sk, ch, seed, X), info
        if kind == 'PAYSUB':
            r = extra
            sym = [syms[int(rng.choice(len(syms), p=mv))] if rng.random() < r else lmap[L] for L in stream]
            info['sub_rate'] = r
            return symbol_lines(sym, sk, ch, seed, X), info
    # palette plants (no payload)
    a = par
    pid, lt = paragraphs(sk, X)
    slot_unit = []
    for li, ln in enumerate(sk['lines']):
        L = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                continue
            if kind == 'PALPAR':
                slot_unit.append(pid[li])
            elif kind == 'PALLINE':
                slot_unit.append(li)
            elif kind == 'PALPOS':
                slot_unit.append(min(4, int(5 * p / max(L, 1))))
    pal = {}
    sym = []
    for u in slot_unit:
        if u not in pal:
            pal[u] = rng.dirichlet(a * mv + 1e-9)
        sym.append(syms[int(rng.choice(len(syms), p=pal[u]))])
    # dispersion: per folio, paragraphs x top-6 symbols chi2/df (descriptive heterogeneity measure)
    fol = [f for ln, f in zip(sk['lines'], sk['folios']) for w in ln if w is not None]
    pslot = [pid[li] for li, ln in enumerate(sk['lines']) for w in ln if w is not None]
    top = set(syms[:6])
    tab = defaultdict(Counter)
    for f, p, s in zip(fol, pslot, sym):
        tab[(f, p)][s if s in top else 'other'] += 1
    byf = defaultdict(list)
    for (f, p), c in tab.items():
        byf[f].append(c)
    chi, df = 0.0, 0
    cats = sorted(top, key=str) + ['other']
    for f, rows in byf.items():
        if len(rows) < 2:
            continue
        M = np.array([[r[c] for c in cats] for r in rows], dtype=float)
        rs, cs, T = M.sum(1, keepdims=True), M.sum(0, keepdims=True), M.sum()
        E = rs @ cs / T
        ok = E > 0
        chi += float((((M - E) ** 2)[ok] / E[ok]).sum())
        df += (M.shape[0] - 1) * (int((cs > 0).sum()) - 1)
    info = {'alpha': a, 'par_dispersion_chi2_df': chi / max(df, 1)}
    return symbol_lines(sym, sk, ch, seed, X), info


def run_one(spec):
    X = _setup()
    t0 = time.time()
    sk = X.HR.b_skeleton()
    lines, info = build(spec, X)
    assert lines != sk['lines'], 'refusing to score B'
    res = {}
    for gname, groups in (('EF', X.GK.ef_groups(sk)), ('EFpar', par_groups(sk, X))):
        r = X.run(lines, groups, R=R, seed=spec[3] + 7, channels=('F1', 'F2'))
        res[gname] = {c: {'z7': r[c]['RPT7']['z'], 'p7': r[c]['RPT7']['p'], 'obs7': r[c]['RPT7']['obs'],
                          'null7': r[c]['RPT7']['null_mean'], 'z5': r[c]['RPT5']['z'],
                          'movable': r[c]['_cells']['frac_movable']} for c in ('F1', 'F2')}
    return '|'.join(str(x) for x in spec), {'spec': [str(x) for x in spec], **info, 'res': res,
                                            'runtime_s': time.time() - t0}


def specs():
    S, seed = [], 9900
    for ch in ('F1', 'F2'):
        for text in ('LAT_mesue', 'NT_la'):
            S.append(('PAYBASE', ch, (text, None), seed)); seed += 1
            S.append(('PAYNULL', ch, (text, None), seed)); seed += 1
            for r in (0.05, 0.10):
                S.append(('PAYSUB', ch, (text, r), seed)); seed += 1
        for a in (50.0, 15.0, 5.0):
            S.append(('PALPAR', ch, a, seed)); seed += 1
        for a in (30.0, 10.0):
            S.append(('PALLINE', ch, a, seed)); seed += 1
        for a in (20.0, 5.0):
            S.append(('PALPOS', ch, a, seed)); seed += 1
    return S


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    X = _setup()
    sk = X.HR.b_skeleton()
    out = {}
    # marginal facts (declared exposure): tail mass left unused by the frequency-rank map
    fn = OUT / 'audit777.json'
    T0 = time.time()
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
            extra = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()
                     if k not in ('res', 'spec', 'runtime_s')}
            print(f'[{time.time() - T0:6.0f}s] {name:40s} ' + ' | '.join(
                f'{g}:{c} z7 {x[g][c]["z7"]:6.1f} p {x[g][c]["p7"]:.3f} mv {x[g][c]["movable"]:.2f}'
                for g in ('EF', 'EFpar') for c in ('F1', 'F2')) + f' {extra}', flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
