"""PHASE_776: verdict thresholds from the design calibration (controls only). Writes results/thresholds776.json.

Rules (fixed before this script was run; see PRE_REGISTRATION.md):
  Primary statistic: lambda2 of the 49x49 class-transition operator under the header-aware EF null
  (D = lambda2(corpus) - mean lambda2(EF); p = (1 + #{null >= obs}) / (1 + R)).
  NEG = max D over the EDGE family (edge-only chains, k = 1 and k = 2).
  POS = min D over the CLASS family (class-chain generators habit and M1).
  tau = (NEG + POS) / 2.
  Call: SURVIVES EDGES if p <= 0.005 and D >= tau; EDGE-REDUCIBLE if p > 0.05; INDETERMINATE otherwise.
lambda3, the lag-2 lambda2, the within-line EF (EFL) and the shuffle floor are descriptive only.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'results'
d = json.load(open(OUT / 'prelock_calib776_design.json', encoding='utf-8'))
edge = [v['res']['lambda2']['D'] for v in d.values() if v['kind'] == 'EDGE']
cls = [v['res']['lambda2']['D'] for v in d.values() if v['kind'] == 'CLASS']
th = {'NEG': max(edge), 'POS': min(cls), 'tau': (max(edge) + min(cls)) / 2, 'n_edge': len(edge), 'n_class': len(cls),
      'edge_p_min': min(v['res']['lambda2']['p'] for v in d.values() if v['kind'] == 'EDGE'),
      'class_p_max': max(v['res']['lambda2']['p'] for v in d.values() if v['kind'] == 'CLASS')}


def call(D, p, th):
    if p <= 0.005 and D >= th['tau']:
        return 'SURVIVES EDGES'
    if p > 0.05:
        return 'EDGE-REDUCIBLE'
    return 'INDETERMINATE'


print(json.dumps(th, indent=1))
for k, v in sorted(d.items(), key=lambda kv: (kv[1]['kind'], kv[1]['family'], kv[1]['seed'])):
    x = v['res']['lambda2']
    print(f"{v['kind']:5s} {v['family']:12s} {v['seed']} | D {x['D']:+.4f} p {x['p']:.3f} -> {call(x['D'], x['p'], th)}")
json.dump(th, open(OUT / 'thresholds776.json', 'w'), indent=1)
