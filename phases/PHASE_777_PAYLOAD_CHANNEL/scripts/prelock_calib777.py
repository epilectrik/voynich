"""PHASE_777 pre-lock calibration (controls only; nothing is computed on B's token order).

Families, all laid into B's skeleton and scored on every channel under that channel's exact null:
  POS   Trithemius-style payload: plaintext letters carried by one channel (F1, F2, L1, L2 or GAL), filler drawn from
        B's tokens with that symbol, routing-aware (the junction rule kept as far as the payload allows).
  TWIN  the same with the letter stream shuffled within folio (no payload structure).
  NEG   no-payload generators fitted to B: edge chains, habit2/3/3b, M1, section-fitted.
Design set: seeds 7700+, letter offset 0 of each plaintext. Certification set: seeds 7900+, fresh plaintexts and the
second letter block (offset n).

Usage: python prelock_calib777.py [workers] [design|cert]
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
R = int(os.environ.get('R777', 300))
CH = ('F1', 'F2', 'L1', 'L2', 'GAL')


def specs(which):
    S = []
    if which == 'design':
        base, off = 7700, 0
        texts = ('LAT_rec', 'NT_la', 'LAT_mesue', 'ITA_dante', 'LAT_sismel')
        negs = (('edge2', 4), ('edge1', 3), ('habit3', 3), ('habit3b', 3), ('M1', 2), ('habit3b_sec', 2), ('habit2', 2))
        twins = (('F1', 'LAT_rec'), ('L1', 'NT_la'), ('GAL', 'LAT_mesue'), ('F2', 'ITA_dante'), ('L2', 'LAT_sismel'))
    elif which == 'cert':
        base, off = 7900, 1
        texts = ('NT_de', 'NT_es', 'NT_en', 'TUR_nt', 'LAT_rupescissa', 'LAT_mesue')
        negs = (('edge2', 4), ('edge1', 3), ('habit3', 3), ('habit3b', 3), ('M1', 2), ('habit3b_sec', 2), ('habit2', 2))
        twins = (('F1', 'NT_de'), ('L1', 'NT_es'), ('GAL', 'TUR_nt'), ('F2', 'NT_en'), ('L2', 'LAT_rupescissa'))
    else:                                            # cert2 (v2): arms F1/F2; fresh seeds, third letter block
        base, off = 8100, 2
        texts = ('NT_it', 'NT_la', 'LAT_sismel', 'LAT_mesue', 'LAT_rec', 'ITA_dante')
        negs = (('edge2', 4), ('edge1', 3), ('habit3', 3), ('habit3b', 3), ('M1', 2), ('habit3b_sec', 2), ('habit2', 2))
        twins = (('F1', 'NT_it'), ('F2', 'NT_la'), ('F1', 'LAT_mesue'), ('F2', 'LAT_rec'), ('L1', 'LAT_sismel'))
    i = 0
    pos_channels = ('F1', 'F2', 'L1') if which == 'cert2' else CH
    for pt in texts:
        for ch in pos_channels:
            S.append(('POS', ch, pt, off, base + i))
            i += 1
    for ch, pt in twins:
        S.append(('TWIN', ch, pt, off, base + 60 + i))
        i += 1
    for gen, k in negs:
        for j in range(k):
            S.append(('NEG', gen, None, None, base + 100 + 10 * j + len(gen)))
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
    kind, fam, pt, off, seed = spec
    t0 = time.time()
    sk = X.HR.b_skeleton()
    n = X.HR.n_certain(sk)
    info = {}
    if kind in ('POS', 'TWIN'):
        words = X.G.plaintext_words(pt)
        stream = X.letter_stream(words, n, offset=off * n)
        if kind == 'TWIN':
            stream = X.twin_letters(stream, sk, seed + 1000)
        lines, lmap = X.payload_lines(stream, sk, fam, seed, routing=True)
        info = {'payload_channel': fam, 'n_symbols_used': len(set(lmap.values())), 'letter_offset': off * n}
    else:
        gens = {'edge2': lambda s: X6.edge_only_lines(sk, s, k=2), 'edge1': lambda s: X6.edge_only_lines(sk, s, k=1),
                'habit2': lambda s: X.HR.habit2_lines(sk, s), 'habit3': lambda s: X.HR.habit3_lines(sk, s),
                'habit3b': lambda s: X.HR2.habit3b_lines(sk, s), 'M1': lambda s: X.G.m1_lines(sk, s),
                'habit3b_sec': lambda s: X.G.section_fitted(X.HR2.habit3b_lines, sk, s)}
        lines = gens[fam](seed)
    assert lines != sk['lines'], 'refusing to score B'
    res = X.run(lines, X.GK.ef_groups(sk), R=R, seed=seed)
    return '|'.join(str(x) for x in spec), {'kind': kind, 'family': fam, 'plaintext': pt, 'seed': seed, **info,
                                            'res': res, 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    which = sys.argv[2] if len(sys.argv) > 2 else 'design'
    T0 = time.time()
    out = {}
    fn = OUT / f'prelock_calib777_{which}.json'
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
            print(f'[{time.time() - T0:6.1f}s] {name:34s} | ' + ' | '.join(
                f'{ch} z7 {x[ch]["RPT7"]["z"]:6.1f} p {x[ch]["RPT7"]["p"]:.3f} z5 {x[ch]["RPT5"]["z"]:5.1f}' for ch in CH),
                flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
