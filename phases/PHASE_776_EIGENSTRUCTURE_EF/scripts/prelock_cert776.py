"""PHASE_776 v2 certification on fresh seeds (controls only), after thresholds776.json (v2: MI under EF-K2) was fixed.

v1 (lambda2 under EF; seeds 8900+) FAILED C1 and is kept in results/prelock_cert776_v1.json. v2 uses seeds 8600+.

Criteria (fixed here and in PRE_REGISTRATION.md v2 before this script was run):
  C1  no EDGE run (edge-only chains, k = 1 and k = 2; 10 runs) is BEYOND ROUTING, and at most 2 are INDETERMINATE;
  C2  at least 9 of the 10 CLASS runs (habit and M1) are BEYOND ROUTING, and none is ROUTING-REDUCIBLE.
MIXED runs (habit2/habit3/habit3b and section-fitted; 15 runs) are reported without a criterion: they carry partial
class structure beyond routing by construction.
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
        return 'BEYOND ROUTING'
    if p > 0.05 or D <= TH['NEG']:
        return 'ROUTING-REDUCIBLE'
    return 'INDETERMINATE'


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in PC.specs('cert2')}
        for f in as_completed(futs):
            name, r = f.result()
            x = r['res']['MI']
            r['call'] = call(x['D'], x['p'])
            out[name] = r
            l = r['res']['lambda2']
            print(f'[{time.time() - T0:6.1f}s] {name:24s} | MI D {x["D"]:+.4f} z {x["z"]:5.1f} p {x["p"]:.3f} -> '
                  f'{r["call"]:18s} | l2 EF-K2 D {l["D"]:+.4f} p {l["p"]:.3f} | EF l2 D {r["res"]["EF_lambda2"]["D"]:+.4f}',
                  flush=True)
    rows = list(out.values())
    edge = [r for r in rows if r['kind'] == 'EDGE']
    cls = [r for r in rows if r['kind'] == 'CLASS']
    crit = {
        'C1': (not any(r['call'] == 'BEYOND ROUTING' for r in edge)
               and sum(r['call'] == 'INDETERMINATE' for r in edge) <= 2),
        'C1_indeterminate': sum(r['call'] == 'INDETERMINATE' for r in edge),
        'C1_max_D': max(r['res']['MI']['D'] for r in edge),
        'C2': (sum(r['call'] == 'BEYOND ROUTING' for r in cls) >= 9
               and not any(r['call'] == 'ROUTING-REDUCIBLE' for r in cls)),
        'C2_beyond': f'{sum(r["call"] == "BEYOND ROUTING" for r in cls)}/{len(cls)}',
        'C2_min_D': min(r['res']['MI']['D'] for r in cls),
        'lambda2_EFK2_class_p_le_005': sum(r['res']['lambda2']['p'] <= 0.005 for r in cls),
        'lambda2_EFK2_edge_p_le_005': sum(r['res']['lambda2']['p'] <= 0.005 for r in edge),
        'mixed_calls': sorted((r['family'], r['seed'], r['call'], round(r['res']['MI']['D'], 4))
                              for r in rows if r['kind'] == 'MIXED'),
    }
    crit['PASS'] = crit['C1'] and crit['C2']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert776.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
