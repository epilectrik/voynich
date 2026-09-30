"""PHASE_774: derive the verdict thresholds from the pre-lock calibration (controls only) and check certification.

Rules (fixed before the thresholds were computed; see PRE_REGISTRATION.md):
  T arm (whole-word codes): statistic D5 = RPT5_TOK(obs) - mean RPT5_TOK(EF null).
    NEG_T  = max D5 over all no-message generators.
    POS_T  = min D5 over the design CBB positives.
    tau_T  = (NEG_T + POS_T) / 2.
  M arm (stem codes of repetitive text): statistic X5 = (RPT5_MID + 1) / (mean null + 1).
    NEG_M  = max X5 over all no-message generators.
    POS_M  = min X5 over the design HRCB-lem positives whose plaintext is a New Testament (the scope).
    tau_M  = sqrt(NEG_M * POS_M).
  Per arm: PRESENT if statistic >= tau and p <= 0.01; NONE if statistic <= NEG or p > 0.05; else INDETERMINATE.
Certification: every held-out positive in scope is PRESENT on its arm; no negative and no twin is PRESENT on either
arm. Writes results/thresholds774.json.
"""
import json
import math
from pathlib import Path

OUT = Path(__file__).parent.parent / 'results'
d = {}
for f in ('prelock_calib.json', 'prelock_calib2.json'):
    d.update(json.load(open(OUT / f, encoding='utf-8')))
vals = list(d.values())


def D5(v):
    x = v['reps']['TOK']['RPT5']
    return x['obs'] - x['null_mean'], x['p']


def X5(v):
    x = v['reps']['MID']['RPT5']
    return x['X'], x['p']


def call(stat, p, tau, neg):
    if stat >= tau and p <= 0.01:
        return 'PRESENT'
    if stat <= neg or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


neg = [v for v in vals if v['kind'] == 'NEG']
twin = [v for v in vals if v['kind'] == 'TWIN']
pos = [v for v in vals if v['kind'] == 'POS']
NEG_T = max(D5(v)[0] for v in neg)
POS_T = min(D5(v)[0] for v in pos if v['family'] == 'CBB' and v['group'].startswith('design'))
tau_T = (NEG_T + POS_T) / 2
NEG_M = max(X5(v)[0] for v in neg)
POS_M = min(X5(v)[0] for v in pos if v['family'] == 'HRCB-lem' and v['group'].startswith('design')
            and v['plaintext'].startswith('NT_'))
tau_M = math.sqrt(NEG_M * POS_M)
th = {'NEG_T': NEG_T, 'POS_T': POS_T, 'tau_T': tau_T, 'NEG_M': NEG_M, 'POS_M': POS_M, 'tau_M': tau_M,
      'n_negatives': len(neg), 'n_twins': len(twin), 'n_positives': len(pos)}
print(json.dumps(th, indent=1))

rows = []
for v in sorted(vals, key=lambda v: (v['kind'], v['family'], v['group'], str(v['plaintext']), v['seed'])):
    t = call(*D5(v), tau_T, NEG_T)
    m = call(*X5(v), tau_M, NEG_M)
    rows.append({'kind': v['kind'], 'group': v['group'], 'family': v['family'], 'plaintext': v['plaintext'],
                 'seed': v['seed'], 'D5': D5(v)[0], 'pT': D5(v)[1], 'T': t, 'X5': X5(v)[0], 'pM': X5(v)[1],
                 'M': m})
    print(f"{v['kind']:4s} {v['group']:8s} {v['family']:9s} {str(v['plaintext']):15s} {v['seed']:5d} | "
          f"T {t:13s} (D5 {D5(v)[0]:7.1f}) | M {m:13s} (X5 {X5(v)[0]:6.2f})")

cert = {
    'heldout_CBB_all_T_PRESENT': all(r['T'] == 'PRESENT' for r in rows
                                     if r['kind'] == 'POS' and r['group'] == 'heldout' and r['family'] == 'CBB'),
    'heldout_NT_stem_all_M_PRESENT': all(r['M'] == 'PRESENT' for r in rows
                                         if r['kind'] == 'POS' and r['group'] == 'heldout'
                                         and r['family'] == 'HRCB-lem' and r['plaintext'] in ('NT_de', 'NT_es',
                                                                                             'TUR_nt')),
    'no_negative_PRESENT': not any('PRESENT' in (r['T'], r['M']) for r in rows if r['kind'] == 'NEG'),
    'no_twin_PRESENT': not any('PRESENT' in (r['T'], r['M']) for r in rows if r['kind'] == 'TWIN'),
    'negatives_INDETERMINATE': sum('INDETERMINATE' in (r['T'], r['M']) for r in rows if r['kind'] == 'NEG'),
}
print(json.dumps(cert, indent=1))
json.dump({'thresholds': th, 'certification': cert, 'rows': rows}, open(OUT / 'thresholds774.json', 'w'),
          indent=1)
