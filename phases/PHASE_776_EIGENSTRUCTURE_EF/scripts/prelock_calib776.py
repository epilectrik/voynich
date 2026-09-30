"""PHASE_776 pre-lock calibration (controls only; nothing is computed on B's token order).

Reference families under the header-aware EF null:
  EDGE   first-order edge-only chains fitted to B (ending -> next token, by zone), k = 1 and k = 2 glyph units: class
         structure only as far as edges carry it. Expected D ~ 0.
  CLASS  class-chain generators fitted to B: habit (class bigram Markov, PHASE_768) and M1 (PHASE_757): class structure
         by construction beyond what edges carry. Expected D > 0.
  MIXED  habit2 / habit3 / habit3b (token-level and (class, last glyph) contexts) and their section-fitted forms.
Design set = seeds 8800+; certification set (fresh seeds) = 8900+.

Usage: python prelock_calib776.py [workers] [design|cert]
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
R = int(os.environ.get('R776', 300))


def specs(which):
    base = {'design': 8800, 'cert': 8900, 'design2': 8700, 'cert2': 8600}[which]
    S = []
    for j in range(6 if which.startswith('design') else 5):
        S.append(('EDGE', 'edge2', base + j))
        S.append(('EDGE', 'edge1', base + 10 + j))
        S.append(('CLASS', 'habit', base + 20 + j))
        S.append(('CLASS', 'M1', base + 30 + j))
    for j in range(4 if which.startswith('design') else 3):
        S.append(('MIXED', 'habit2', base + 40 + j))
        S.append(('MIXED', 'habit3', base + 50 + j))
        S.append(('MIXED', 'habit3b', base + 60 + j))
        S.append(('MIXED', 'habit3_sec', base + 70 + j))
        S.append(('MIXED', 'habit3b_sec', base + 80 + j))
    return S


def run_one(spec):
    os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(HERE))
    import eig776 as X
    kind, fam, seed = spec
    t0 = time.time()
    sk = X.HR.b_skeleton()
    G = X.G
    if fam == 'edge2':
        lines = X.edge_only_lines(sk, seed, k=2)
    elif fam == 'edge1':
        lines = X.edge_only_lines(sk, seed, k=1)
    elif fam == 'habit':
        lines = X.HR.habit_lines(sk, seed)
    elif fam == 'M1':
        lines = G.m1_lines(sk, seed)
    elif fam == 'habit2':
        lines = X.HR.habit2_lines(sk, seed)
    elif fam == 'habit3':
        lines = X.HR.habit3_lines(sk, seed)
    elif fam == 'habit3b':
        lines = X.HR2.habit3b_lines(sk, seed)
    elif fam == 'habit3_sec':
        lines = G.section_fitted(X.HR.habit3_lines, sk, seed)
    elif fam == 'habit3b_sec':
        lines = G.section_fitted(X.HR2.habit3b_lines, sk, seed)
    else:
        raise ValueError(fam)
    assert lines != sk['lines'], 'refusing to score B'
    res = X.run(lines, X.GK.ef_groups(sk), R=R, seed=seed)
    return '|'.join(str(x) for x in spec), {'kind': kind, 'family': fam, 'seed': seed, 'res': res,
                                            'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    which = sys.argv[2] if len(sys.argv) > 2 else 'design'
    T0 = time.time()
    out = {}
    fn = OUT / f'prelock_calib776_{which}.json'
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs(which)}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED {futs[f]}: {e!r}', flush=True)
                continue
            out[name] = r
            x = r['res']
            print(f'[{time.time() - T0:6.1f}s] {name:24s} | EFK2 l2 {x["lambda2"]["obs"]:.4f} null {x["lambda2"]["null_mean"]:.4f} '
                  f'D {x["lambda2"]["D"]:+.4f} z {x["lambda2"]["z"]:5.1f} p {x["lambda2"]["p"]:.3f} mov {x["EFK2_cells"]["frac_movable"]:.2f} | '
                  f'MI D {x["MI"]["D"]:+.4f} z {x["MI"]["z"]:5.1f} p {x["MI"]["p"]:.3f} | EF l2 D {x["EF_lambda2"]["D"]:+.4f} '
                  f'p {x["EF_lambda2"]["p"]:.3f} EF MI D {x["EF_MI"]["D"]:+.4f} p {x["EF_MI"]["p"]:.3f} | '
                  f'lag2 D {x["lag2_lambda2"]["D"]:+.4f} | EFL D {x["EFL_lambda2"]["D"]:+.4f} p {x["EFL_lambda2"]["p"]:.3f} | '
                  f'floor {x["shuffle_floor"]["lambda2"]:.4f}', flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
