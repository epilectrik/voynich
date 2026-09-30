"""PHASE_776 v2: verdict thresholds from the v2 design calibration (controls only). Writes results/thresholds776.json.

v1 (lambda2 under EF) failed certification C1: an edge-only chain read SURVIVES, because EF fixes each slot's own
edges but not the routing of the next class by the preceding ending (C2082). v2 uses the routing-preserving null EF-K2
(cells also keyed by the slot's preceding-token last two glyph units) and, as the primary statistic, the class-pair
mutual information I(class_i; class_{i+1}) over bridged within-line pairs, which separates the families with far more
power than lambda2 under EF-K2.

Rules (fixed before this script was run; see PRE_REGISTRATION.md v2):
  D = MI(corpus) - mean MI(EF-K2 samples); p = (1 + #{null >= obs}) / (1 + R).
  NEG = max D over the EDGE family; POS = min D over the CLASS family; tau = (NEG + POS) / 2.
  Call: BEYOND ROUTING if p <= 0.005 and D >= tau; ROUTING-REDUCIBLE if p > 0.05 or D <= NEG; INDETERMINATE otherwise.
lambda2 under EF-K2 (C2061's statistic), lambda2 under plain EF, lambda3, lag-2, EFL and the shuffle floor are
descriptive.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'results'
d = json.load(open(OUT / 'prelock_calib776_design2.json', encoding='utf-8'))
edge = [v['res']['MI']['D'] for v in d.values() if v['kind'] == 'EDGE']
cls = [v['res']['MI']['D'] for v in d.values() if v['kind'] == 'CLASS']
th = {'statistic': 'MI under EF-K2', 'NEG': max(edge), 'POS': min(cls), 'tau': (max(edge) + min(cls)) / 2,
      'n_edge': len(edge), 'n_class': len(cls),
      'edge_p_min': min(v['res']['MI']['p'] for v in d.values() if v['kind'] == 'EDGE'),
      'class_p_max': max(v['res']['MI']['p'] for v in d.values() if v['kind'] == 'CLASS'),
      'lambda2_EFK2_class_p_le_005': sum(v['res']['lambda2']['p'] <= 0.005 for v in d.values() if v['kind'] == 'CLASS'),
      'lambda2_EFK2_edge_p_le_005': sum(v['res']['lambda2']['p'] <= 0.005 for v in d.values() if v['kind'] == 'EDGE')}


def call(D, p, th):
    if p <= 0.005 and D >= th['tau']:
        return 'BEYOND ROUTING'
    if p > 0.05 or D <= th['NEG']:
        return 'ROUTING-REDUCIBLE'
    return 'INDETERMINATE'


print(json.dumps(th, indent=1))
for k, v in sorted(d.items(), key=lambda kv: (kv[1]['kind'], kv[1]['family'], kv[1]['seed'])):
    x = v['res']['MI']
    l = v['res']['lambda2']
    print(f"{v['kind']:5s} {v['family']:12s} {v['seed']} | MI D {x['D']:+.4f} p {x['p']:.3f} -> {call(x['D'], x['p'], th):18s}"
          f" | l2 EF-K2 D {l['D']:+.4f} p {l['p']:.3f}")
json.dump(th, open(OUT / 'thresholds776.json', 'w'), indent=1)
