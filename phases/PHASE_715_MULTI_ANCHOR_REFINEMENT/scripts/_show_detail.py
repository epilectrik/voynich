import json
from pathlib import Path
p = Path("C:/git/voynich/phases/PHASE_715_MULTI_ANCHOR_REFINEMENT/results/multi_anchor_results.json")
d = json.loads(p.read_text())
for name, r in d['results_by_anchor'].items():
    if 'error' in r:
        continue
    print(f'\n=== {name} ===')
    print(f'  N events: {r["n_events"]}, baseline: {r["baseline_target_rate"]:.4f}')
    print(f'  Multi-lag:', end='')
    for lag in sorted(r['multi_lag'].keys(), key=lambda x: int(x)):
        d2 = r['multi_lag'][lag]
        print(f'  lag+{lag}={d2["rate"]:.4f}', end='')
    print()
    for lag_int in [1, 2, 3, 4]:
        if lag_int in r['per_lag_null']:
            pln = r['per_lag_null'][lag_int]
            mark = 'PASS' if pln['passes'] else 'fail'
            print(f'    Null lag+{lag_int}: obs={pln["observed"]:.4f}  null_mean={pln["null_mean"]:.4f}  p99={pln["null_p99"]:.4f}  p_emp={pln["p_emp"]:.4f}  {mark}')
