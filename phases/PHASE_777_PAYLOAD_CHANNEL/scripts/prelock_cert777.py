"""PHASE_777 certification on fresh seeds, fresh plaintexts and the second letter block (controls only), after
thresholds777.json was fixed.

Criteria (fixed here and in PRE_REGISTRATION.md before this script was run):
  C1  no no-payload run (19 generators, 5 twins) is PRESENT on any ARM (F1, F2, L1, L2); at most 2 INDETERMINATE
      arm calls in all;
  C2  no payload control is PRESENT on an arm other than its payload channel (cross-channel leakage);
  C3  of the 24 arm payload controls (6 plaintexts x 4 arms), at least 22 are PRESENT on their own arm and none is
      NONE.
  GAL is descriptive: its payload controls run and are reported, with no criterion.
PASS = C1 and C2 and C3. A FAIL means redesign (no re-tuning on these seeds). Writes results/prelock_cert777.json.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import prelock_calib777 as PC  # noqa: E402

TH = json.load(open(OUT / 'thresholds777.json', encoding='utf-8'))
CH = PC.CH
ARMS = ('F1', 'F2', 'L1', 'L2')


def call(z, p, c):
    t = TH[c]
    if p <= 0.005 and z >= t['tau']:
        return 'PRESENT'
    if p > 0.05 or z <= t['NEG']:
        return 'NONE'
    return 'INDETERMINATE'


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in PC.specs('cert')}
        for f in as_completed(futs):
            name, r = f.result()
            r['calls'] = {c: call(r['res'][c]['RPT7']['z'], r['res'][c]['RPT7']['p'], c) for c in CH}
            out[name] = r
            print(f'[{time.time() - T0:6.1f}s] {name:34s} | ' + ' | '.join(
                f'{c} z {r["res"][c]["RPT7"]["z"]:6.1f} {r["calls"][c][:4]}' for c in CH), flush=True)
    rows = list(out.values())
    nopay = [r for r in rows if r['kind'] in ('NEG', 'TWIN')]
    pos = [r for r in rows if r['kind'] == 'POS' and r['family'] in ARMS]
    crit = {
        'C1': (not any(r['calls'][c] == 'PRESENT' for r in nopay for c in ARMS)
               and sum(r['calls'][c] == 'INDETERMINATE' for r in nopay for c in ARMS) <= 2),
        'C1_indeterminate': sum(r['calls'][c] == 'INDETERMINATE' for r in nopay for c in ARMS),
        'C2': not any(r['calls'][c] == 'PRESENT' for r in rows if r['kind'] == 'POS' for c in ARMS if c != r['family']),
        'C3': (sum(r['calls'][r['family']] == 'PRESENT' for r in pos) >= 22
               and not any(r['calls'][r['family']] == 'NONE' for r in pos)),
        'C3_present': f"{sum(r['calls'][r['family']] == 'PRESENT' for r in pos)}/{len(pos)}",
        'C3_misses': sorted((r['family'], r['plaintext'], r['calls'][r['family']], round(r['res'][r['family']]['RPT7']['z'], 1))
                            for r in pos if r['calls'][r['family']] != 'PRESENT'),
        'GAL_descriptive': sorted((r['plaintext'], r['calls']['GAL'], round(r['res']['GAL']['RPT7']['z'], 1))
                                  for r in rows if r['kind'] == 'POS' and r['family'] == 'GAL'),
        'nopay_max_z7': {c: max(r['res'][c]['RPT7']['z'] for r in nopay) for c in CH},
    }
    crit['PASS'] = crit['C1'] and crit['C2'] and crit['C3']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert777.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
