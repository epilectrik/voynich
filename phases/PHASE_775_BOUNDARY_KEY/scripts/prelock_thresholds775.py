"""PHASE_775: verdict thresholds from the design calibration (controls only). Writes results/thresholds775.json.

Rules (fixed before this script was run; see PRE_REGISTRATION.md):
  Statistic per arm K in {K1, K2}: the key gain G_K = dS_K - dS_K0, with p_G = share of EF samples whose raw key gain is
  at least the corpus's.
  NEG_K = max G_K over every design control without a keyed message: no-message generators, shuffled-plaintext twins
          and plain one-spelling word codes.
  Scope: plaintext segments whose word-order index O >= O_S = 0.04.
  POS_K = min G_K over design context-keyed ciphers with true key K, one spelling per unit and context, and O >= O_S.
  tau_K = (NEG_K + POS_K) / 2.
  Call per arm: PRESENT if G_K >= tau_K and p_G <= 0.005; NONE if G_K <= NEG_K or p_G > 0.05; else INDETERMINATE.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'results'
O_S = 0.04
d = json.load(open(OUT / 'prelock_calib775_design.json', encoding='utf-8'))
O = json.load(open(OUT / 'prelock_order775_design.json', encoding='utf-8'))
th = {'O_S': O_S}
for K in ('K1', 'K2'):
    k = int(K[1])
    neg = [v['res'][K]['G'] for v in d.values()
           if v['kind'] in ('NEG', 'TWIN') or (v['kind'] == 'POS' and v['family'] == 'CBB')]
    pos = [v['res'][K]['G'] for v in d.values()
           if v['kind'] == 'POS' and v['family'] == 'key' and v['true_key'] == k and v['homophones'] == 1
           and O[f"{v['plaintext']}|{v['segment']}"] >= O_S]
    th[f'NEG_{K}'] = max(neg)
    th[f'POS_{K}'] = min(pos)
    th[f'tau_{K}'] = (max(neg) + min(pos)) / 2
    th[f'n_neg_{K}'] = len(neg)
    th[f'n_pos_{K}'] = len(pos)
print(json.dumps(th, indent=1))
json.dump(th, open(OUT / 'thresholds775.json', 'w'), indent=1)
