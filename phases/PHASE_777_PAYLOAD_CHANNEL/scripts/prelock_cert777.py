"""PHASE_777 v2 certification (controls only), after thresholds777.json was fixed and the v1 certification FAILED
(v1: results/prelock_cert777_v1.json -- 4 INDETERMINATE no-payload arm calls against a limit of 2, and end-of-word
payloads leaking PRESENT into the other end-of-word arm).

v2 (no threshold changed): confirmatory arms F1 and F2 only, each called two ways -- PAYLOAD PRESENT (p <= 0.005 and
z7 >= tau) or NOT PRESENT (otherwise; with the descriptive flag "residual above the design no-payload maximum" when
z7 > NEG and p <= 0.05). L1, L2 and GAL are descriptive. Fresh seeds (8100+), fresh texts, the third letter block.

Criteria (fixed here and in PRE_REGISTRATION.md v2 before this script was run):
  C1  no no-payload run (19 generators, 5 twins) is PAYLOAD PRESENT on F1 or F2;
  C2  no payload control is PAYLOAD PRESENT on the other F arm (F1 payload on F2, or F2 payload on F1);
  C3  of the 12 F-arm payload controls (6 plaintexts x F1/F2), at least 11 are PAYLOAD PRESENT on their own arm.
  L1 payload controls (6) and all L1/L2/GAL values are reported without a criterion.
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
ARMS = ('F1', 'F2')


def call(z, p, c):
    """v2 two-way call; the third label is descriptive only."""
    t = TH[c]
    if p <= 0.005 and z >= t['tau']:
        return 'PRESENT'
    if p > 0.05 or z <= t['NEG']:
        return 'NONE'
    return 'NOT PRESENT (residual)'


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in PC.specs('cert2')}
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
        'C1': not any(r['calls'][c] == 'PRESENT' for r in nopay for c in ARMS),
        'C1_residual_flags': sum(r['calls'][c] == 'NOT PRESENT (residual)' for r in nopay for c in ARMS),
        'C2': not any(r['calls'][c] == 'PRESENT' for r in rows if r['kind'] == 'POS' for c in ARMS if c != r['family']),
        'C3': sum(r['calls'][r['family']] == 'PRESENT' for r in pos) >= 11,
        'C3_present': f"{sum(r['calls'][r['family']] == 'PRESENT' for r in pos)}/{len(pos)}",
        'C3_misses': sorted((r['family'], r['plaintext'], r['calls'][r['family']], round(r['res'][r['family']]['RPT7']['z'], 1))
                            for r in pos if r['calls'][r['family']] != 'PRESENT'),
        'L1_payload_descriptive': sorted((r['plaintext'], r['calls']['L1'], round(r['res']['L1']['RPT7']['z'], 1),
                                          'L2 z', round(r['res']['L2']['RPT7']['z'], 1))
                                         for r in rows if r['kind'] == 'POS' and r['family'] == 'L1'),
        'nopay_max_z7': {c: max(r['res'][c]['RPT7']['z'] for r in nopay) for c in CH},
    }
    crit['PASS'] = crit['C1'] and crit['C2'] and crit['C3']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert777.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
