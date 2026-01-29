"""
T2: FL Position by REGIME

Question: Does FL's final-bias (C562, C586) vary by REGIME?

FL is the escape/recovery layer. Does its positional behavior change
based on REGIME (execution requirements)?
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

folio_to_regime = {}
for regime, folios in regime_map.items():
    for f in folios:
        folio_to_regime[f] = regime

FL_CLASSES = {7, 30, 38, 40}

# Collect line tokens
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

    is_fl = tc in FL_CLASSES

    line_tokens[key].append({
        'word': w,
        'is_fl': is_fl,
        'fl_class': tc if is_fl else None,
    })

# Compute FL position by REGIME
fl_positions = defaultdict(list)
fl_boundary = defaultdict(lambda: {'first': 0, 'middle': 0, 'last': 0, 'total': 0})

# Also track by FL subtype (hazard vs safe per C586)
fl_hazard_positions = defaultdict(list)  # Classes 7, 30
fl_safe_positions = defaultdict(list)    # Classes 38, 40

for key, tokens in line_tokens.items():
    folio, line, regime = key
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_fl']:
            continue

        pos = i / (n - 1) if n > 1 else 0.5
        fl_positions[regime].append(pos)

        # Subtype
        if t['fl_class'] in {7, 30}:
            fl_hazard_positions[regime].append(pos)
        else:
            fl_safe_positions[regime].append(pos)

        # Boundary
        if i == 0:
            fl_boundary[regime]['first'] += 1
        elif i == n - 1:
            fl_boundary[regime]['last'] += 1
        else:
            fl_boundary[regime]['middle'] += 1
        fl_boundary[regime]['total'] += 1

print("=" * 60)
print("T2: FL POSITION BY REGIME")
print("=" * 60)

results = {}

print("\nFL MEAN POSITION BY REGIME:")
print("-" * 40)

regime_means = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    positions = fl_positions.get(regime, [])
    if len(positions) >= 10:
        mean = np.mean(positions)
        std = np.std(positions)
        n = len(positions)
        regime_means[regime] = {'mean': mean, 'std': std, 'n': n}
        print(f"  {regime}: mean={mean:.4f}, std={std:.4f}, n={n}")

# Kruskal-Wallis
groups = [fl_positions.get(r, []) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
groups = [g for g in groups if len(g) >= 10]

if len(groups) >= 2:
    h_stat, p_val = stats.kruskal(*groups)
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
    print(f"\n  Kruskal-Wallis: H={h_stat:.2f}, p={p_val:.4f} {sig}")

    results['fl_overall'] = {
        'regime_means': {k: {'mean': float(v['mean']), 'std': float(v['std']), 'n': v['n']}
                        for k, v in regime_means.items()},
        'kruskal_h': float(h_stat),
        'kruskal_p': float(p_val),
    }

# Final-bias by REGIME
print("\nFL FINAL-BIAS BY REGIME:")
print("-" * 40)

fl_final_rates = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    bd = fl_boundary.get(regime, {'last': 0, 'total': 0})
    if bd['total'] >= 10:
        rate = bd['last'] / bd['total']
        fl_final_rates[regime] = (bd['last'], bd['total'], rate)
        print(f"  {regime}: {bd['last']}/{bd['total']} = {rate*100:.1f}% final")

# Chi-squared for final rate variation
if len(fl_final_rates) >= 2:
    observed = [v[0] for v in fl_final_rates.values()]
    totals = [v[1] for v in fl_final_rates.values()]
    overall_rate = sum(observed) / sum(totals)
    expected = [t * overall_rate for t in totals]

    chi2, p = stats.chisquare(observed, expected)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
    print(f"\n  Chi-squared (final-bias variation): chi2={chi2:.2f}, p={p:.4f} {sig}")

    results['fl_final_chi2'] = float(chi2)
    results['fl_final_p'] = float(p)

# FL subtypes by REGIME
print("\n" + "=" * 60)
print("FL SUBTYPES BY REGIME:")
print("=" * 60)

for label, pos_data in [('FL_HAZARD (7,30)', fl_hazard_positions), ('FL_SAFE (38,40)', fl_safe_positions)]:
    print(f"\n{label}:")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        positions = pos_data.get(regime, [])
        if len(positions) >= 5:
            mean = np.mean(positions)
            print(f"  {regime}: mean={mean:.4f}, n={len(positions)}")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't2_fl_position_by_regime.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
