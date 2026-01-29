"""
T5: Line Syntax Profile by REGIME

Question: Does the overall SETUP->WORK->CHECK->CLOSE pattern (C556) vary by REGIME?

Compute complete role position profiles for each REGIME and compare.
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

# Role definitions
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}
# AX = everything else classified

def get_role(tc):
    if tc in CC_CLASSES:
        return 'CC'
    elif tc in EN_CLASSES:
        return 'EN'
    elif tc in FL_CLASSES:
        return 'FL'
    elif tc in FQ_CLASSES:
        return 'FQ'
    elif tc:
        return 'AX'
    return None

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
    role = get_role(tc)

    line_tokens[key].append({
        'word': w,
        'role': role,
    })

# Compute role positions by REGIME
role_positions = defaultdict(lambda: defaultdict(list))  # role -> regime -> positions

for key, tokens in line_tokens.items():
    folio, line, regime = key
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['role']:
            continue

        pos = i / (n - 1) if n > 1 else 0.5
        role_positions[t['role']][regime].append(pos)

print("=" * 60)
print("T5: LINE SYNTAX PROFILE BY REGIME")
print("=" * 60)

results = {}

# Overall role positions by REGIME
print("\nROLE MEAN POSITIONS BY REGIME:")
print("-" * 60)
print(f"{'Role':<8} {'REGIME_1':>10} {'REGIME_2':>10} {'REGIME_3':>10} {'REGIME_4':>10}")
print("-" * 60)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    row = [role]
    regime_means = {}

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        positions = role_positions[role].get(regime, [])
        if len(positions) >= 20:
            mean = np.mean(positions)
            regime_means[regime] = mean
            row.append(f"{mean:.4f}")
        else:
            row.append("-")

    print(f"{row[0]:<8} {row[1]:>10} {row[2]:>10} {row[3]:>10} {row[4]:>10}")

    # Kruskal-Wallis
    groups = [role_positions[role].get(r, []) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
    groups = [g for g in groups if len(g) >= 20]

    if len(groups) >= 2:
        h_stat, p_val = stats.kruskal(*groups)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
        results[role] = {
            'regime_means': regime_means,
            'kruskal_h': float(h_stat),
            'kruskal_p': float(p_val),
            'significant': bool(p_val < 0.05),
        }

# Print significance summary
print("\n" + "=" * 60)
print("KRUSKAL-WALLIS SIGNIFICANCE (position varies by REGIME?):")
print("=" * 60)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    if role in results:
        r = results[role]
        sig = "***" if r['kruskal_p'] < 0.001 else "**" if r['kruskal_p'] < 0.01 else "*" if r['kruskal_p'] < 0.05 else "NS"
        verdict = "VARIES" if r['significant'] else "INVARIANT"
        print(f"  {role}: H={r['kruskal_h']:.2f}, p={r['kruskal_p']:.4f} {sig} -> {verdict}")

# Overall verdict
print("\n" + "=" * 60)
print("OVERALL VERDICT:")
print("=" * 60)

significant_roles = [r for r in results if results[r]['significant']]
if len(significant_roles) == 0:
    print("\n  LINE SYNTAX IS REGIME-INVARIANT")
    print("  No role shows significant position variation by REGIME.")
    print("  This CONFIRMS C124 (grammar universality).")
elif len(significant_roles) >= 3:
    print("\n  LINE SYNTAX VARIES BY REGIME")
    print(f"  {len(significant_roles)}/5 roles show significant variation:")
    for r in significant_roles:
        print(f"    - {r}")
else:
    print(f"\n  PARTIAL VARIATION")
    print(f"  {len(significant_roles)}/5 roles show significant variation:")
    for r in significant_roles:
        print(f"    - {r}")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't5_line_syntax_profile.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
