"""PHASE_775 pre-lock prototype (controls only; nothing is computed on B's token order).

Rank decoding under keys K0/K1/K2 with the EF null, on context-keyed ciphers of real plaintext in B's forms (message
present), their shuffled-plaintext twins, a plain one-spelling word code (no key), and B-fitted no-message generators.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
R = int(os.environ.get('R775', 200))


def specs():
    S = []
    for pt, seg in (('LAT_rec', 0), ('NT_la', 0), ('LAT_mesue', 7), ('ITA_dante', 0), ('LAT_mesue', 10)):
        S.append(('POS', 'keyK1', pt, seg, 1, 7751))
    S.append(('POS', 'keyK2', 'LAT_rec', 0, 1, 7752))
    S.append(('POS', 'keyK1', 'LAT_rec', 0, 2, 7753))          # 2 homophones per unit and context
    S.append(('POS', 'CBB', 'LAT_rec', 0, 1, 7754))            # plain word code, no key
    S.append(('TWIN', 'keyK1', 'LAT_rec', 0, 1, 7755))
    S.append(('TWIN', 'keyK1', 'NT_la', 0, 1, 7756))
    for gen, seeds in (('habit3', 2), ('habit3b', 2), ('habit3b_sec', 1), ('habit2', 1), ('M1', 1)):
        for j in range(seeds):
            S.append(('NEG', gen, None, None, None, 7760 + 10 * j + len(gen)))
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
    import gen775 as GK
    import key775 as K
    G = GK.G
    kind, fam, pt, seg, hom, seed = spec
    t0 = time.time()
    sk = G.HR.b_skeleton()
    if kind in ('POS', 'TWIN'):
        words = G.plaintext_words(pt)
        stream = G.segment_stream(words, sk, seg)
        if kind == 'TWIN':
            stream = G.twin_stream(stream, sk, seed + 1000)
        if fam.startswith('key'):
            lines = GK.keyed_cipher(stream, sk, int(fam[-1]), seed, homophones=hom)
        else:
            lines, _ = G.bform_codebook(words, sk, seed, stream)
    else:
        gen = {'habit3': G.HR.habit3_lines, 'habit3b': G.HR2.habit3b_lines, 'habit2': G.HR.habit2_lines,
               'M1': None, 'habit3b_sec': G.HR2.habit3b_lines}[fam]
        if fam == 'M1':
            lines = G.m1_lines(sk, seed)
        elif fam.endswith('_sec'):
            lines = G.section_fitted(gen, sk, seed)
        else:
            lines = gen(sk, seed)
    assert lines != sk['lines'], 'refusing to score B'
    res = K.run(lines, sk['folios'], R=R, seed=seed)
    ntypes = len({w for ln in lines for w in ln if w is not None})
    return '|'.join(str(x) for x in spec), {'spec': [str(x) for x in spec], 'types': ntypes, 'res': res,
                                            'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
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
            print(f'[{time.time() - T0:6.1f}s] {name:40s} types {r["types"]:5d} | ' + ' | '.join(
                f'{k} S {x[k]["S"]:.4f} null {x[k]["null_mean"]:.4f} dS {x[k]["dS"]:+.4f} z {x[k]["z"]:6.1f}'
                for k in ('K0', 'K1', 'K2')), flush=True)
            json.dump(out, open(OUT / 'prelock_proto775.json', 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
