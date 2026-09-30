"""PHASE_774 pre-lock calibration, part 2 (controls only): more no-message seeds (the strongest local-rule
generators, habit3 and habit3b, at 10 seeds each) and more seeds of the weakest design positives (Latin recipes), to
see the spread that thresholds must survive. Writes results/prelock_calib2.json.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import prelock_calib as PC  # noqa: E402

OUT = HERE.parent / 'results'


def specs():
    S = []
    for gen, seeds in (('habit3', 10), ('habit3b', 10), ('habit2', 5), ('habit', 3), ('M1', 3), ('timmU', 3)):
        for j in range(seeds):
            S.append(('NEG', 'neg2', gen, None, 8820 + 10 * j + len(gen)))
    for j in range(3):
        S.append(('POS', 'design2', 'CBB', 'LAT_rec', 8900 + j))
        S.append(('POS', 'design2', 'HRCB-lem', 'LAT_rec', 8910 + j))
    return S


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    log = open(OUT / 'prelock_calib2_log.txt', 'w', encoding='utf-8')
    T0 = time.time()
    S = specs()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in S}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                msg = f'[{time.time() - T0:7.1f}s] FAILED {futs[f]}: {e!r}'
                print(msg, flush=True)
                log.write(msg + '\n')
                continue
            out[name] = r
            x = r['reps']
            msg = (f'[{time.time() - T0:7.1f}s] {name}: ' + ' | '.join(
                f'{k}{nn} {x[k][f"RPT{nn}"]["obs"]}/{x[k][f"RPT{nn}"]["null_mean"]:.1f}'
                for k in ('TOK', 'MID') for nn in PC.NS))
            print(msg, flush=True)
            log.write(msg + '\n')
            log.flush()
            json.dump(out, open(OUT / 'prelock_calib2.json', 'w'), indent=1)
    log.write(f'done {len(out)}/{len(S)}\n')
    log.close()
    print('done', flush=True)


if __name__ == '__main__':
    main()
