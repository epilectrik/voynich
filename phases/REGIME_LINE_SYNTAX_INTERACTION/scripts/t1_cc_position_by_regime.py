"""
T1: CC Position by REGIME

Question: Does daiin's initial-bias (27.1% per C819) vary by REGIME?

C545 shows REGIME_3 has 1.83x CC enrichment. Does this affect WHERE CC appears,
not just HOW MUCH CC appears?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load class map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

# Load REGIME mapping
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_map = json.load(f)

# Invert: folio -> REGIME
folio_to_regime = {}
for regime, folios in regime_map.items():
    for f in folios:
        folio_to_regime[f] = regime

CC_CLASSES = {10, 11, 12, 17}

# Collect line tokens with REGIME
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    regime = folio_to_regime.get(token.folio)
    if not regime:
        continue

    key = (token.folio, token.line, regime)
    tc = token_to_class.get(w)

    # CC classification
    cc_type = None
    if tc in CC_CLASSES:
        if w == 'daiin':
            cc_type = 'DAIIN'
        elif w == 'ol':
            cc_type = 'OL'
        elif tc == 17:
            cc_type = 'OL_DERIVED'

    line_tokens[key].append({
        'word': w,
        'cc_type': cc_type,
    })

# Compute position distributions by REGIME
position_data = defaultdict(lambda: defaultdict(list))  # cc_type -> regime -> positions
boundary_data = defaultdict(lambda: defaultdict(lambda: {'first': 0, 'middle': 0, 'last': 0, 'total': 0}))

for key, tokens in line_tokens.items():
    folio, line, regime = key
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['cc_type']:
            continue

        cc_type = t['cc_type']
        pos = i / (n - 1) if n > 1 else 0.5
        position_data[cc_type][regime].append(pos)

        # Boundary classification
        if i == 0:
            boundary_data[cc_type][regime]['first'] += 1
        elif i == n - 1:
            boundary_data[cc_type][regime]['last'] += 1
        else:
            boundary_data[cc_type][regime]['middle'] += 1
        boundary_data[cc_type][regime]['total'] += 1

print("=" * 60)
print("T1: CC POSITION BY REGIME")
print("=" * 60)

results = {}

for cc_type in ['DAIIN', 'OL', 'OL_DERIVED']:
    print(f"\n{'='*40}")
    print(f"{cc_type} MEAN POSITION BY REGIME:")
    print(f"{'='*40}")

    regime_means = {}
    regime_positions = position_data[cc_type]

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        positions = regime_positions.get(regime, [])
        if len(positions) >= 5:
            mean = np.mean(positions)
            std = np.std(positions)
            n = len(positions)
            regime_means[regime] = {'mean': mean, 'std': std, 'n': n}
            print(f"  {regime}: mean={mean:.4f}, std={std:.4f}, n={n}")

    # Kruskal-Wallis test across REGIMEs
    groups = [regime_positions.get(r, []) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
    groups = [g for g in groups if len(g) >= 5]

    if len(groups) >= 2:
        h_stat, p_val = stats.kruskal(*groups)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
        print(f"\n  Kruskal-Wallis: H={h_stat:.2f}, p={p_val:.4f} {sig}")

        results[cc_type] = {
            'regime_means': {k: {'mean': float(v['mean']), 'std': float(v['std']), 'n': v['n']}
                           for k, v in regime_means.items()},
            'kruskal_h': float(h_stat),
            'kruskal_p': float(p_val),
        }

    # Boundary analysis
    print(f"\n  BOUNDARY RATES BY REGIME:")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        bd = boundary_data[cc_type].get(regime, {'first': 0, 'middle': 0, 'last': 0, 'total': 0})
        if bd['total'] >= 5:
            first_rate = bd['first'] / bd['total']
            print(f"    {regime}: first={first_rate*100:.1f}% ({bd['first']}/{bd['total']})")

# Overall: does daiin initial-bias vary?
print("\n" + "=" * 60)
print("DAIIN INITIAL-BIAS BY REGIME:")
print("=" * 60)

daiin_first_rates = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    bd = boundary_data['DAIIN'].get(regime, {'first': 0, 'total': 0})
    if bd['total'] >= 5:
        rate = bd['first'] / bd['total']
        daiin_first_rates[regime] = (bd['first'], bd['total'], rate)
        print(f"  {regime}: {bd['first']}/{bd['total']} = {rate*100:.1f}%")

# Chi-squared test for initial rate variation
if len(daiin_first_rates) >= 2:
    observed = [v[0] for v in daiin_first_rates.values()]
    totals = [v[1] for v in daiin_first_rates.values()]
    overall_rate = sum(observed) / sum(totals)
    expected = [t * overall_rate for t in totals]

    chi2, p = stats.chisquare(observed, expected)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
    print(f"\n  Chi-squared (initial-bias variation): chi2={chi2:.2f}, p={p:.4f} {sig}")

    results['daiin_initial_chi2'] = float(chi2)
    results['daiin_initial_p'] = float(p)

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't1_cc_position_by_regime.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
