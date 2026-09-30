"""PHASE_775 pre-lock calibration (controls only; nothing is computed on B's token order).

Design set: context-keyed ciphers in B's forms (true key K1 or K2; 1 or 2 spellings per unit and context) on segment 0
of six plaintexts plus Mesue segments 0-1; shuffled-plaintext twins; plain one-spelling word codes (no key); B-fitted
no-message generators (corpus-wide and section-fitted). EF groups = folio x line type (paragraph-first vs body line).

Usage: python prelock_calib775.py [workers] [set]   set = design (default) | cert
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


def design_specs():
    S = []
    base = [('LAT_rec', 0), ('NT_la', 0), ('NT_it', 0), ('ITA_dante', 0), ('LAT_sismel', 0), ('LAT_mesue', 0),
            ('LAT_mesue', 1)]
    for i, (pt, seg) in enumerate(base):
        S.append(('POS', 'key', pt, seg, 1, 1, 8100 + i))
        S.append(('POS', 'key', pt, seg, 2, 1, 8120 + i))
    for i, (pt, seg) in enumerate((('LAT_rec', 0), ('NT_la', 0), ('LAT_mesue', 0))):
        S.append(('POS', 'key', pt, seg, 1, 2, 8140 + i))
        S.append(('TWIN', 'key', pt, seg, 1, 1, 8150 + i))
        S.append(('TWIN', 'key', pt, seg, 2, 1, 8160 + i))
    for i, (pt, seg) in enumerate((('LAT_rec', 0), ('NT_la', 0))):
        S.append(('POS', 'CBB', pt, seg, 0, 1, 8170 + i))
    for gen, seeds in (('habit3', 6), ('habit3b', 6), ('habit3_sec', 4), ('habit3b_sec', 4), ('habit2', 3), ('M1', 3),
                       ('habit', 2)):
        for j in range(seeds):
            S.append(('NEG', gen, None, None, None, None, 8200 + 10 * j + len(gen)))
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
    kind, fam, pt, seg, key, hom, seed = spec
    t0 = time.time()
    sk = G.HR.b_skeleton()
    info = {}
    if kind in ('POS', 'TWIN'):
        words = G.plaintext_words(pt)
        stream = G.segment_stream(words, sk, seg)
        info['P5'] = G.plaintext_p5(stream, sk)
        if kind == 'TWIN':
            stream = G.twin_stream(stream, sk, seed + 1000)
        if fam == 'key':
            lines = GK.keyed_cipher(stream, sk, key, seed, homophones=hom)
        else:
            lines, _ = G.bform_codebook(words, sk, seed, stream)
    else:
        gens = {'habit3': G.HR.habit3_lines, 'habit3b': G.HR2.habit3b_lines, 'habit2': G.HR.habit2_lines,
                'habit': G.HR.habit_lines}
        if fam == 'M1':
            lines = G.m1_lines(sk, seed)
        elif fam.endswith('_sec'):
            lines = G.section_fitted(gens[fam[:-4]], sk, seed)
        else:
            lines = gens[fam](sk, seed)
    assert lines != sk['lines'], 'refusing to score B'
    res = K.run(lines, GK.ef_groups(sk), R=R, seed=seed)
    ntypes = len({w for ln in lines for w in ln if w is not None})
    name = '|'.join(str(x) for x in spec)
    return name, {'kind': kind, 'family': fam, 'plaintext': pt, 'segment': seg, 'true_key': key, 'homophones': hom,
                  'seed': seed, 'types': ntypes, **info, 'res': res, 'runtime_s': time.time() - t0}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    which = sys.argv[2] if len(sys.argv) > 2 else 'design'
    specs = design_specs() if which == 'design' else None
    T0 = time.time()
    out = {}
    fn = OUT / f'prelock_calib775_{which}.json'
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                print(f'FAILED {futs[f]}: {e!r}', flush=True)
                continue
            out[name] = r
            x = r['res']
            print(f'[{time.time() - T0:6.1f}s] {name:42s} | K0 dS {x["K0"]["dS"]:+.4f} | K1 dS {x["K1"]["dS"]:+.4f} '
                  f'G {x["K1"]["G"]:+.4f} p {x["K1"]["G_p"]:.3f} | K2 dS {x["K2"]["dS"]:+.4f} G {x["K2"]["G"]:+.4f} '
                  f'p {x["K2"]["G_p"]:.3f}', flush=True)
            json.dump(out, open(fn, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
