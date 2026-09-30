"""PHASE_776 lean-expert lock audit: controls-only plants (nothing is computed on B's token order).

Plants (B supplies only the declared exposure: adjacent pairs keyed by ending and zone, line-quintile unigrams, and
per-folio token counts = composition):
  habit           reference class chain (PHASE_768 habit)
  habit_folio     class-bigram chain fitted to B, emission P(token | class, folio): B-like folio concentration
                  (does C2 transfer to B's folio marginals?)
  edge2_folio     edge2 chain reweighted by folio unigram ratio (exact null under EF-K2; checks null behaviour)
  edge2_pos       edge2 chain reweighted by B's line-quintile unigram ratio ^ beta (within-line positional composition,
                  no class transitions beyond routing)
  edge2_line      edge2 chain with a latent per-line mode tilting a random half of the classes (line clustering)
  edge3, edgeFL2  edge chains keyed by the previous token's last 3 glyph units, or its first unit + last 2
  edge2_un        edge2 chain where after an unmapped token the next is unmapped with extra probability pi
Extra nulls/statistics per plant (R each): EFL-K2 MI (within line, cells keyed by preceding ending), EF-K2Q MI (EF-K2
cells also keyed by line quintile), raw-adjacent 49-class MI (no bridging) and 50-state MI (UN as a state) under EF-K2,
and the number of bridged pairs (obs vs null).
Usage: python audit776.py [workers<=4]
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCR = HERE.parent
OUT = SCR.parent / 'results' / 'audit'
R = int(os.environ.get('R776A', 300))
SCRATCH = os.environ.get('AUDIT_NUMBA', str(Path(os.environ.get('TEMP', '.')) / 'numba776audit'))


def specs():
    S = [('habit', 1.0, 9100), ('habit', 1.0, 9101),
         ('habit_folio', 1.0, 9110), ('habit_folio', 1.0, 9111), ('habit_folio', 1.0, 9112),
         ('edge2_folio', 1.0, 9120), ('edge2_folio', 1.0, 9121),
         ('edge2_pos', 1.0, 9130), ('edge2_pos', 1.0, 9131), ('edge2_pos', 2.0, 9132),
         ('edge2_line', 0.3, 9140), ('edge2_line', 0.3, 9141), ('edge2_line', 0.6, 9142),
         ('edge3', 1.0, 9150), ('edge3', 1.0, 9151), ('edgeFL2', 1.0, 9160), ('edgeFL2', 1.0, 9161),
         ('edge2_un', 0.3, 9170), ('edge2_un', 0.3, 9171)]
    return S


def _setup():
    os.environ['NUMBA_CACHE_DIR'] = SCRATCH
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(SCR))
    import eig776 as X
    return X


def quint(p, L):
    return min(4, int(5 * p / max(L, 1)))


def make_lines(X, sk, fam, par, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    E = X.E
    ending = X.GK.K.ending
    vocab = sorted({w for ln in sk['lines'] for w in ln if w is not None})
    vid = {w: i for i, w in enumerate(vocab)}
    cls = np.array([X.TOKEN_CLASS.get(w, 0) for w in vocab])
    glob = np.zeros(len(vocab))
    folc = defaultdict(lambda: np.zeros(len(vocab)))
    qc = np.zeros((5, len(vocab)))
    for ln, f in zip(sk['lines'], sk['folios']):
        L = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                continue
            glob[vid[w]] += 1
            folc[f][vid[w]] += 1
            qc[quint(p, L), vid[w]] += 1
    folios = sk['folios']

    if fam == 'habit':
        return X.HR.habit_lines(sk, seed)
    if fam == 'habit_folio':
        init, trans = Counter(), defaultdict(Counter)
        emitF, emitG = defaultdict(Counter), defaultdict(Counter)
        for ln, f in zip(sk['lines'], folios):
            prev = None
            for w in ln:
                if w is None:
                    prev = None
                    continue
                c = X.TOKEN_CLASS.get(w, 0)
                emitF[(f, c)][w] += 1
                emitG[c][w] += 1
                if prev is None:
                    init[c] += 1
                else:
                    trans[prev][c] += 1
                prev = c

        def draw(counter):
            keys = list(counter)
            pr = np.array([counter[k] for k in keys], dtype=float)
            return keys[int(rng.choice(len(keys), p=pr / pr.sum()))]
        out = []
        for ln, f in zip(sk['lines'], folios):
            prev, cur = None, []
            for w in ln:
                if w is None:
                    cur.append(None)
                    prev = None
                    continue
                c = draw(init if prev is None or not trans[prev] else trans[prev])
                src = emitF.get((f, c))
                cur.append(draw(src if src else emitG[c]))
                prev = c
            out.append(cur)
        return out

    # edge-chain family with a multiplicative weight modifier
    if fam in ('edge2_folio', 'edge2_pos', 'edge2_line', 'edge2_un'):
        keyfn = lambda w: ending(w, 2)  # noqa: E731
    elif fam == 'edge3':
        keyfn = lambda w: ending(w, 3)  # noqa: E731
    elif fam == 'edgeFL2':
        keyfn = lambda w: E.GLYPH_RE.findall(w)[0] + '|' + ending(w, 2)  # noqa: E731
    else:
        raise ValueError(fam)
    pool = defaultdict(Counter)
    for ln in sk['lines']:
        prev = None
        L = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                prev = None
                continue
            z = 0 if p == 0 else (2 if p == L - 1 else 1)
            key = ('^', z) if prev is None else (keyfn(prev), z)
            pool[key][vid[w]] += 1
            prev = w
    zpool = defaultdict(Counter)
    for (c, z), cnt in pool.items():
        zpool[z].update(cnt)
    arr = {}

    def arrays(key, counter):
        if key not in arr:
            ids = np.array(list(counter), dtype=np.int64)
            arr[key] = (ids, np.array([counter[i] for i in ids], dtype=float))
        return arr[key]
    gl = np.maximum(glob, 1)
    qf = [((qc[q] + 0.5) / (qc[q].sum() + 0.5 * len(vocab))) / ((glob + 0.5) / (glob.sum() + 0.5 * len(vocab)))
          for q in range(5)]
    part = rng.permutation(np.arange(1, 50))[:24]
    h = np.where(np.isin(cls, part), 1.0, np.where(cls > 0, -1.0, 0.0))
    out = []
    for li, ln in enumerate(sk['lines']):
        f = folios[li]
        L = len(ln)
        s = 1.0 if rng.random() < 0.5 else -1.0
        prev, cur = None, []
        for p, w in enumerate(ln):
            if w is None:
                cur.append(None)
                prev = None
                continue
            z = 0 if p == 0 else (2 if p == L - 1 else 1)
            key = ('^', z) if prev is None else (keyfn(prev), z)
            src = pool.get(key)
            ids, wt = arrays(key, src) if src and sum(src.values()) >= 5 else arrays(('Z', z), zpool[z])
            if fam == 'edge2_folio':
                m = wt * folc[f][ids] / gl[ids]
                if m.sum() <= 0:
                    ids, wt = arrays(('Z', z), zpool[z])
                    m = wt * folc[f][ids] / gl[ids]
                if m.sum() <= 0:
                    ids = np.flatnonzero(folc[f] > 0)
                    m = folc[f][ids]
            elif fam == 'edge2_pos':
                m = wt * qf[quint(p, L)][ids] ** par
            elif fam == 'edge2_line':
                m = wt * np.exp(par * s * h[ids])
            elif fam == 'edge2_un':
                m = wt
                if prev is not None and cls[vid[prev]] == 0 and rng.random() < par:
                    u = cls[ids] == 0
                    if u.any():
                        m = wt * u
            else:
                m = wt
            cum = np.cumsum(m)
            t = vocab[ids[min(int(np.searchsorted(cum, rng.random() * cum[-1])), len(ids) - 1)]]
            cur.append(t)
            prev = t
        out.append(cur)
    return out


def refine(C, extra):
    import numpy as np
    cell_key = {}
    cell = np.full(len(C.tok), -1, dtype=np.int64)
    for p in range(len(C.tok)):
        if C.tok[p] >= 0:
            cell[p] = cell_key.setdefault((int(C.cell[p]), int(extra[p])), len(cell_key))
    C.cell = cell
    C.n_cells = len(cell_key)
    C.mpos = np.flatnonzero(cell >= 0)
    C.P = C.mpos[np.argsort(cell[C.mpos], kind='stable')]
    cs = np.bincount(cell[C.mpos], minlength=len(cell_key))
    C.frac_movable = float(cs[cs >= 2].sum() / max(1, len(C.mpos)))
    return C


def raw_mi(S, tok, states50):
    import numpy as np
    cl = np.where(tok >= 0, S.cls[np.where(tok >= 0, tok, 0)], -1)
    a = np.arange(len(tok) - 1)
    ok = (S.line_of[a] == S.line_of[a + 1]) & (cl[a] >= 0) & (cl[a + 1] >= 0)
    if not states50:
        ok &= (cl[a] > 0) & (cl[a + 1] > 0)
    x, y = cl[a[ok]], cl[a[ok] + 1]
    c = np.zeros((50, 50))
    np.add.at(c, (x, y), 1)
    n = c.sum()
    pj = c / n
    pa, pb = pj.sum(1, keepdims=True), pj.sum(0, keepdims=True)
    nz = pj > 0
    return float((pj[nz] * np.log2(pj[nz] / (pa @ pb)[nz])).sum())


def summ(obs, v, Rr):
    import numpy as np
    v = np.asarray(v, dtype=float)
    sd = float(v.std(ddof=1))
    return {'obs': float(obs), 'null_mean': float(v.mean()), 'D': float(obs - v.mean()),
            'z': float((obs - v.mean()) / max(sd, 1e-12)), 'p': float((1 + (v >= obs).sum()) / (1 + Rr))}


def run_one(spec):
    X = _setup()
    import numpy as np
    fam, par, seed = spec
    t0 = time.time()
    sk = X.HR.b_skeleton()
    lines = make_lines(X, sk, fam, par, seed)
    assert lines != sk['lines'], 'refusing to score B'
    groups = X.GK.ef_groups(sk)
    res = X.run(lines, groups, R=R, seed=seed, floor=False, efl=True)
    TH = json.load(open(SCR.parent / 'results' / 'thresholds776.json', encoding='utf-8'))
    mi = res['MI']
    call = ('BEYOND ROUTING' if (mi['p'] <= 0.005 and mi['D'] >= TH['tau']) else
            ('ROUTING-REDUCIBLE' if (mi['p'] > 0.05 or mi['D'] <= TH['NEG']) else 'INDETERMINATE'))
    d1, d2, ep = mi['D'], res['lag2_MI']['D'], res['EFL_lambda2']['p']
    shape = ('n/a' if d1 <= 0 else ('order-like' if (d2 < 0.5 * d1 and ep <= 0.05) else
                                    ('clustering-like' if d2 >= d1 else 'unresolved')))
    rng = np.random.default_rng(seed + 7)
    extra = {}
    # EFL-K2: within line, cells keyed by zone, first unit, last two units, preceding ending
    CL = X.refine_by_context(X.E.Corpus(lines, list(range(len(lines))), sig=X.E.sig_fl2, ns=(2,)), k=2)
    SL = X.Spectrum(CL)
    extra['EFLK2_MI'] = summ(SL.mi(CL.tok), [SL.mi(CL.sample(rng)) for _ in range(R)], R)
    extra['EFLK2_movable'] = CL.frac_movable
    # EF-K2Q: EF-K2 cells also keyed by line quintile
    CK = X.refine_by_context(X.E.Corpus(lines, groups, sig=X.E.sig_fl2, ns=(2,)), k=2)
    pos = np.zeros(len(CK.tok), dtype=np.int64)
    i = 0
    for ln in lines:
        L = len(ln)
        for p in range(L):
            pos[i] = quint(p, L)
            i += 1
    CQ = refine(X.refine_by_context(X.E.Corpus(lines, groups, sig=X.E.sig_fl2, ns=(2,)), k=2), pos)
    SQ = X.Spectrum(CQ)
    extra['EFK2Q_MI'] = summ(SQ.mi(CQ.tok), [SQ.mi(CQ.sample(rng)) for _ in range(R)], R)
    extra['EFK2Q_movable'] = CQ.frac_movable
    # raw-adjacent (no bridging) 49-class MI and 50-state MI under EF-K2; number of bridged pairs
    SK = X.Spectrum(CK)
    o49, o50, onp = raw_mi(SK, CK.tok, False), raw_mi(SK, CK.tok, True), SK.counts(CK.tok).sum()
    n49, n50, npair = [], [], []
    for _ in range(R):
        t = CK.sample(rng)
        n49.append(raw_mi(SK, t, False))
        n50.append(raw_mi(SK, t, True))
        npair.append(SK.counts(t).sum())
    extra['EFK2_raw49_MI'] = summ(o49, n49, R)
    extra['EFK2_raw50_MI'] = summ(o50, n50, R)
    extra['n_bridged_pairs'] = {'obs': float(onp), 'null_mean': float(np.mean(npair)), 'null_sd': float(np.std(npair))}
    return '|'.join(str(x) for x in spec), {'family': fam, 'par': par, 'seed': seed, 'call': call, 'shape': shape,
                                            'res': res, 'extra': extra, 'runtime_s': time.time() - t0}


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    OUT.mkdir(parents=True, exist_ok=True)
    fn = OUT / 'audit776_plants.json'
    out = {}
    T0 = time.time()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['NUMBA_CACHE_DIR'] = SCRATCH
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs()}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED {futs[f]}: {e!r}', flush=True)
                continue
            out[name] = r
            x, e = r['res'], r['extra']
            print(f"[{time.time() - T0:6.0f}s] {name:22s} MI D {x['MI']['D']:+.4f} z {x['MI']['z']:5.1f} p {x['MI']['p']:.3f} "
                  f"-> {r['call']:17s} shape {r['shape']:15s} | lag2 {x['lag2_MI']['D']:+.4f} | EF MI D {x['EF_MI']['D']:+.4f} | "
                  f"l2 D {x['lambda2']['D']:+.4f} p {x['lambda2']['p']:.3f} | EFL l2 p {x['EFL_lambda2']['p']:.3f} | "
                  f"EFLK2 D {e['EFLK2_MI']['D']:+.4f} p {e['EFLK2_MI']['p']:.3f} mov {e['EFLK2_movable']:.2f} | "
                  f"EFK2Q D {e['EFK2Q_MI']['D']:+.4f} p {e['EFK2Q_MI']['p']:.3f} mov {e['EFK2Q_movable']:.2f} | "
                  f"raw49 D {e['EFK2_raw49_MI']['D']:+.4f} p {e['EFK2_raw49_MI']['p']:.3f} | raw50 D "
                  f"{e['EFK2_raw50_MI']['D']:+.4f} p {e['EFK2_raw50_MI']['p']:.3f} | pairs {e['n_bridged_pairs']['obs']:.0f} "
                  f"vs {e['n_bridged_pairs']['null_mean']:.0f}+-{e['n_bridged_pairs']['null_sd']:.0f}", flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
