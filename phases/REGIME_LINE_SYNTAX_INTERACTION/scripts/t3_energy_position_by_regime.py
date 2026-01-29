"""
T3: ENERGY Position by REGIME

Question: Does ENERGY medial concentration (C556) shift by REGIME?

C556 shows ENERGY concentrates medially (positions 3-6). Does this
shift earlier or later depending on REGIME?
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

# EN classes per C573
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}

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

    # Lane classification
    m = morph.extract(w)
    prefix = m.prefix or ''
    if prefix == 'qo':
        lane = 'QO'
    elif prefix in {'ch', 'sh'}:
        lane = 'CHSH'
    else:
        lane = 'OTHER'

    line_tokens[key].append({
        'word': w,
        'is_en': tc in EN_CLASSES,
        'lane': lane,
    })

# Compute EN position by REGIME
en_positions = defaultdict(list)
en_qo_positions = defaultdict(list)
en_chsh_positions = defaultdict(list)

for key, tokens in line_tokens.items():
    folio, line, regime = key
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_en']:
            continue

        pos = i / (n - 1) if n > 1 else 0.5
        en_positions[regime].append(pos)

        if t['lane'] == 'QO':
            en_qo_positions[regime].append(pos)
        elif t['lane'] == 'CHSH':
            en_chsh_positions[regime].append(pos)

print("=" * 60)
print("T3: ENERGY POSITION BY REGIME")
print("=" * 60)

results = {}

print("\nEN (ALL) MEAN POSITION BY REGIME:")
print("-" * 40)

regime_means = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    positions = en_positions.get(regime, [])
    if len(positions) >= 50:
        mean = np.mean(positions)
        std = np.std(positions)
        n = len(positions)
        regime_means[regime] = {'mean': mean, 'std': std, 'n': n}
        print(f"  {regime}: mean={mean:.4f}, std={std:.4f}, n={n}")

# Kruskal-Wallis
groups = [en_positions.get(r, []) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
groups = [g for g in groups if len(g) >= 50]

if len(groups) >= 2:
    h_stat, p_val = stats.kruskal(*groups)
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
    print(f"\n  Kruskal-Wallis: H={h_stat:.2f}, p={p_val:.4f} {sig}")

    results['en_overall'] = {
        'regime_means': {k: {'mean': float(v['mean']), 'std': float(v['std']), 'n': v['n']}
                        for k, v in regime_means.items()},
        'kruskal_h': float(h_stat),
        'kruskal_p': float(p_val),
    }

# By lane
print("\n" + "=" * 60)
print("EN BY LANE AND REGIME:")
print("=" * 60)

for label, pos_data in [('EN_QO', en_qo_positions), ('EN_CHSH', en_chsh_positions)]:
    print(f"\n{label}:")
    lane_means = {}
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        positions = pos_data.get(regime, [])
        if len(positions) >= 20:
            mean = np.mean(positions)
            n = len(positions)
            lane_means[regime] = mean
            print(f"  {regime}: mean={mean:.4f}, n={n}")

    # Test across regimes
    groups = [pos_data.get(r, []) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
    groups = [g for g in groups if len(g) >= 20]
    if len(groups) >= 2:
        h_stat, p_val = stats.kruskal(*groups)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
        print(f"  Kruskal-Wallis: H={h_stat:.2f}, p={p_val:.4f} {sig}")

        results[label.lower()] = {
            'kruskal_h': float(h_stat),
            'kruskal_p': float(p_val),
        }

# Effect size: compare extreme REGIMEs
print("\n" + "=" * 60)
print("EFFECT SIZE ANALYSIS:")
print("=" * 60)

if 'REGIME_1' in regime_means and 'REGIME_3' in regime_means:
    r1_mean = regime_means['REGIME_1']['mean']
    r3_mean = regime_means['REGIME_3']['mean']
    delta = r3_mean - r1_mean
    print(f"\nREGIME_3 - REGIME_1 = {delta:+.4f}")
    print(f"  (positive = REGIME_3 has later EN, negative = earlier)")

    # Mann-Whitney for these two
    stat, p = stats.mannwhitneyu(en_positions['REGIME_1'], en_positions['REGIME_3'], alternative='two-sided')
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
    print(f"  Mann-Whitney: U={stat:.0f}, p={p:.4f} {sig}")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't3_energy_position_by_regime.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
