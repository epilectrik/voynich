"""PHASE_777: per-channel verdict thresholds from the design calibration (controls only).
Writes results/thresholds777.json.

Rules (fixed before this script was run; see PRE_REGISTRATION.md):
  Confirmatory arms c in {F1, F2, L1, L2}; GAL is descriptive (its 9 symbols cannot carry a letter alphabet one
  letter per word without collapse, and in the design its Mesue payload control did not separate from the no-payload
  maximum: z7 2.3 against 2.6). Per arm: statistic z7 = (RPT7(corpus) - mean RPT7(null)) / sd(null) under the
  channel's exact null (EF-F for F1/F2, EF-L for L1/L2, EF-K2 for GAL); p from the same null.
  NEG_c = max z7 over every design control with no payload on channel c: the no-payload generators, the twins, and
          the payload controls whose payload is on ANOTHER channel.
  POS_c = min z7 over the design payload controls on channel c.
  tau_c = (NEG_c + POS_c) / 2.
  Call per channel: PRESENT if p <= 0.005 and z7 >= tau_c; NONE if p > 0.05 or z7 <= NEG_c; INDETERMINATE otherwise.
RPT5 and DIST are descriptive.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'results'
CH = ('F1', 'F2', 'L1', 'L2', 'GAL')
ARMS = ('F1', 'F2')                                 # v2: L1/L2 descriptive (v1 certification failed)
d = json.load(open(OUT / 'prelock_calib777_design.json', encoding='utf-8'))
th = {}
for c in CH:
    neg = [v['res'][c]['RPT7']['z'] for v in d.values()
           if v['kind'] in ('NEG', 'TWIN') or (v['kind'] == 'POS' and v['family'] != c)]
    pos = [v['res'][c]['RPT7']['z'] for v in d.values() if v['kind'] == 'POS' and v['family'] == c]
    th[c] = {'NEG': max(neg), 'POS': min(pos), 'tau': (max(neg) + min(pos)) / 2, 'n_neg': len(neg), 'n_pos': len(pos),
             'arm': c in ARMS}


def call(z, p, t):
    if p <= 0.005 and z >= t['tau']:
        return 'PRESENT'
    if p > 0.05 or z <= t['NEG']:
        return 'NONE'
    return 'INDETERMINATE'


print(json.dumps(th, indent=1))
for k, v in sorted(d.items(), key=lambda kv: (kv[1]['kind'], kv[1]['family'], str(kv[1]['plaintext']))):
    print(f"{v['kind']:4s} {v['family']:12s} {str(v['plaintext']):15s} | " + ' | '.join(
        f"{c} z {v['res'][c]['RPT7']['z']:6.1f} {call(v['res'][c]['RPT7']['z'], v['res'][c]['RPT7']['p'], th[c])[:4]}"
        for c in CH))
json.dump(th, open(OUT / 'thresholds777.json', 'w'), indent=1)
