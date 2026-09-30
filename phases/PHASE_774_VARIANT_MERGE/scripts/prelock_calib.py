"""PHASE_774 pre-lock calibration (controls only; nothing is computed on B's token order).

Message-present controls in B's forms (B marginals only), their shuffled-plaintext twins, and no-message generators,
all laid into B's skeleton and scored under the exact edge-frame null (EF). Design plaintexts set thresholds;
held-out plaintexts certify them.

Usage: python prelock_calib.py [workers]    (writes results/prelock_calib.json and prelock_calib_log.txt)
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / 'results'
R = int(os.environ.get('R774', 300))
NS = (4, 5, 6)
REPS = ('TOK', 'MID', 'MIDn1')

# Plaintexts must be at least as long as B's 21,610 certain tokens (no cycling); the Antidotarium (17,292 words) is
# too short and is not used.
DESIGN = ('LAT_rec', 'LAT_sismel', 'NT_la', 'NT_it', 'NT_en')
HELDOUT = ('LAT_mesue', 'LAT_rupescissa', 'ITA_dante', 'NT_de', 'NT_es', 'TUR_nt')


def specs():
    S = []
    for i, pt in enumerate(DESIGN):
        S.append(('POS', 'design', 'CBB', pt, 7760 + i))
        S.append(('POS', 'design', 'HRCB-lem', pt, 7770 + i))
    S.append(('POS', 'design', 'CBB', 'LAT_rec', 7781))
    S.append(('POS', 'design', 'HRCB-lem', 'LAT_rec', 7782))
    S.append(('POS', 'design', 'HRCB-word', 'LAT_rec', 7783))
    S.append(('POS', 'design', 'HRCB-word', 'NT_la', 7784))
    S.append(('POS', 'design', 'CBB2', 'LAT_rec', 7785))
    S.append(('POS', 'design', 'CBB2', 'NT_la', 7786))
    for i, pt in enumerate(HELDOUT):
        S.append(('POS', 'heldout', 'CBB', pt, 7790 + i))
        S.append(('POS', 'heldout', 'HRCB-lem', pt, 7800 + i))
    for i, (fam, pt) in enumerate((('CBB', 'LAT_rec'), ('CBB', 'NT_la'), ('HRCB-lem', 'LAT_rec'),
                                   ('HRCB-lem', 'NT_la'), ('CBB', 'LAT_mesue'), ('HRCB-lem', 'ITA_dante'))):
        S.append(('TWIN', 'twin', fam, pt, 7810 + i))
    for gen, seeds in (('habit', 3), ('habit2', 3), ('habit3', 5), ('habit3b', 3), ('timmU', 3), ('M1', 2)):
        for j in range(seeds):
            S.append(('NEG', 'neg', gen, None, 7820 + 10 * j + len(gen)))
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
    import ef774 as E
    import gen774 as G
    import merge774 as M
    kind, group, fam, pt, seed = spec
    t0 = time.time()
    sk = G.HR.b_skeleton()
    units = None
    if kind in ('POS', 'TWIN'):
        words = G.plaintext_words(pt)
        stream = G.plain_stream(words, sk)
        if kind == 'TWIN':
            stream = G.twin_stream(stream, sk, seed + 1000)
        if fam == 'CBB':
            lines, units = G.bform_codebook(words, sk, seed, stream)
        elif fam == 'CBB2':
            lines, units = G.bform_codebook_k(words, sk, 2, seed, stream)
        elif fam == 'HRCB-lem':
            lines, units = G.bform_stem(words, sk, seed, 'rule', 'lemma', stream)
        elif fam == 'HRCB-word':
            lines, units = G.bform_stem(words, sk, seed, 'rule', 'word', stream)
        else:
            raise ValueError(fam)
    else:
        if fam == 'habit':
            lines = G.HR.habit_lines(sk, seed)
        elif fam == 'habit2':
            lines = G.HR.habit2_lines(sk, seed)
        elif fam == 'habit3':
            lines = G.HR.habit3_lines(sk, seed)
        elif fam == 'habit3b':
            lines = G.HR2.habit3b_lines(sk, seed)
        elif fam == 'timmU':
            lines = G.timm_unseeded(sk, seed)
        elif fam == 'M1':
            lines = G.m1_lines(sk, seed)
        else:
            raise ValueError(fam)
    C = E.Corpus(lines, sk['folios'], sig=E.sig_fl, ns=NS)
    reps = {k: C.rep_array(M.STATIC_MERGES[k]) for k in REPS}
    res = E.ef_test(C, reps, R, seed * 7 + 1)
    name = f'{kind}|{group}|{fam}|{pt}|{seed}'
    return name, {'kind': kind, 'group': group, 'family': fam, 'plaintext': pt, 'seed': seed,
                  'types': len(C.vocab), 'mid_types': int(len(set(reps['MID'].tolist()))),
                  'frac_movable': C.frac_movable, 'runtime_s': time.time() - t0, 'reps': res}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    log = open(OUT / 'prelock_calib_log.txt', 'w', encoding='utf-8')
    T0 = time.time()
    S = specs()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in S}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                msg = f'[{time.time() - T0:7.1f}s] FAILED {futs[f]}: {e!r}'
                print(msg, flush=True)
                log.write(msg + '\n')
                log.flush()
                continue
            out[name] = r
            x = r['reps']
            msg = (f'[{time.time() - T0:7.1f}s] {name}: ' + ' | '.join(
                f'{k}{nn} {x[k][f"RPT{nn}"]["obs"]}/{x[k][f"RPT{nn}"]["null_mean"]:.1f}'
                for k in ('TOK', 'MID') for nn in NS))
            print(msg, flush=True)
            log.write(msg + '\n')
            log.flush()
            json.dump(out, open(OUT / 'prelock_calib.json', 'w'), indent=1)
    log.write(f'done {len(out)}/{len(S)}\n')
    log.close()
    print('done', flush=True)


if __name__ == '__main__':
    main()
