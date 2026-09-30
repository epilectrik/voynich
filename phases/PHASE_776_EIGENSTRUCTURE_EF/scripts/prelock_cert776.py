"""PHASE_776 certification on fresh seeds (controls only), after thresholds776.json was fixed.

Criteria (fixed here and in PRE_REGISTRATION.md before this script was run):
  C1  no EDGE run (edge-only chains, k = 1 and k = 2; 10 runs) is SURVIVES EDGES, and at most 2 are INDETERMINATE;
  C2  at least 8 of the 10 CLASS runs (habit and M1) are SURVIVES EDGES, and none is EDGE-REDUCIBLE.
MIXED runs (habit2/habit3/habit3b and section-fitted; 15 runs) are reported without a criterion: they carry partial
class structure beyond edges by construction.
PASS = C1 and C2. A FAIL means redesign (no re-tuning on these seeds). Writes results/prelock_cert776.json.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import prelock_calib776 as PC  # noqa: E402

TH = json.load(open(OUT / 'thresholds776.json', encoding='utf-8'))


def call(D, p):
    if p <= 0.005 and D >= TH['tau']:
        return 'SURVIVES EDGES'
    if p > 0.05:
        return 'EDGE-REDUCIBLE'
    return 'INDETERMINATE'


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in PC.specs('cert')}
        for f in as_completed(futs):
            name, r = f.result()
            x = r['res']['lambda2']
            r['call'] = call(x['D'], x['p'])
            out[name] = r
            print(f'[{time.time() - T0:6.1f}s] {name:24s} | D {x["D"]:+.4f} p {x["p"]:.3f} -> {r["call"]:15s} | '
                  f'lag2 D {r["res"]["lag2_lambda2"]["D"]:+.4f} | EFL D {r["res"]["EFL_lambda2"]["D"]:+.4f} '
                  f'p {r["res"]["EFL_lambda2"]["p"]:.3f}', flush=True)
    rows = list(out.values())
    edge = [r for r in rows if r['kind'] == 'EDGE']
    cls = [r for r in rows if r['kind'] == 'CLASS']
    crit = {
        'C1': (not any(r['call'] == 'SURVIVES EDGES' for r in edge)
               and sum(r['call'] == 'INDETERMINATE' for r in edge) <= 2),
        'C1_indeterminate': sum(r['call'] == 'INDETERMINATE' for r in edge),
        'C1_max_D': max(r['res']['lambda2']['D'] for r in edge),
        'C2': (sum(r['call'] == 'SURVIVES EDGES' for r in cls) >= 8
               and not any(r['call'] == 'EDGE-REDUCIBLE' for r in cls)),
        'C2_survives': f'{sum(r["call"] == "SURVIVES EDGES" for r in cls)}/{len(cls)}',
        'C2_min_D': min(r['res']['lambda2']['D'] for r in cls),
        'mixed_calls': sorted((r['family'], r['seed'], r['call'], round(r['res']['lambda2']['D'], 4))
                              for r in rows if r['kind'] == 'MIXED'),
    }
    crit['PASS'] = crit['C1'] and crit['C2']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert776.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
