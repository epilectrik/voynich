"""PHASE_777 pre-lock prototype (controls only; nothing is computed on B's token order).

Payload controls: Latin / NT letters carried by F1 or L1 with routing-aware filler; their within-folio letter twins;
no-payload generators (edge chains, habit3, habit3b, M1, section-fitted). All channels scored under their nulls.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
R = int(os.environ.get('R777', 200))


def specs():
    S = []
    for pt in ('LAT_rec', 'NT_la', 'LAT_mesue', 'ITA_dante'):
        S.append(('POS', 'F1', pt, 7771))
        S.append(('POS', 'L1', pt, 7772))
    S.append(('POS', 'F1noroute', 'LAT_rec', 7773))
    S.append(('TWIN', 'F1', 'LAT_rec', 7774))
    S.append(('TWIN', 'L1', 'NT_la', 7775))
    for gen, seeds in (('edge2', 3), ('edge1', 2), ('habit3', 2), ('habit3b', 2), ('M1', 1), ('habit3b_sec', 2)):
        for j in range(seeds):
            S.append(('NEG', gen, None, 7780 + 10 * j + len(gen)))
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
    sys.path.insert(0, str(HERE.parent.parent / 'PHASE_776_EIGENSTRUCTURE_EF' / 'scripts'))
    import chan777 as X
    import eig776 as X6
    kind, fam, pt, seed = spec
    t0 = time.time()
    sk = X.HR.b_skeleton()
    n = X.HR.n_certain(sk)
    info = {}
    if kind in ('POS', 'TWIN'):
        words = X.G.plaintext_words(pt)
        stream = X.letter_stream(words, n)
        if kind == 'TWIN':
            stream = X.twin_letters(stream, sk, seed + 1000)
        ch = 'F1' if fam.startswith('F1') else 'L1'
        lines, lmap = X.payload_lines(stream, sk, ch, seed, routing=(fam != 'F1noroute'))
        info['payload_channel'] = ch
        info['n_symbols_used'] = len(set(lmap.values()))
    else:
        gens = {'edge2': lambda s: X6.edge_only_lines(sk, s, k=2), 'edge1': lambda s: X6.edge_only_lines(sk, s, k=1),
                'habit3': lambda s: X.HR.habit3_lines(sk, s), 'habit3b': lambda s: X.HR2.habit3b_lines(sk, s),
                'M1': lambda s: X.G.m1_lines(sk, s),
                'habit3b_sec': lambda s: X.G.section_fitted(X.HR2.habit3b_lines, sk, s)}
        lines = gens[fam](seed)
    assert lines != sk['lines'], 'refusing to score B'
    res = X.run(lines, X.GK.ef_groups(sk), R=R, seed=seed)
    return '|'.join(str(x) for x in spec), {'kind': kind, 'family': fam, 'plaintext': pt, 'seed': seed, **info,
                                            'res': res, 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    T0 = time.time()
    out = {}
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
            print(f'[{time.time() - T0:6.1f}s] {name:30s} | ' + ' | '.join(
                f'{ch} 5:{x[ch]["RPT5"]["obs"]}/{x[ch]["RPT5"]["null_mean"]:.0f} z{x[ch]["RPT5"]["z"]:5.1f} '
                f'7:{x[ch]["RPT7"]["obs"]}/{x[ch]["RPT7"]["null_mean"]:.0f} z{x[ch]["RPT7"]["z"]:5.1f}'
                for ch in ('F1', 'L1', 'F2', 'L2', 'GAL')), flush=True)
            json.dump(out, open(OUT / 'prelock_proto777.json', 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
