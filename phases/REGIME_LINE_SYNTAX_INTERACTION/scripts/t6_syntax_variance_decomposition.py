"""
T6: Syntax Variance Decomposition

Question: How much variance in role positions is explained by REGIME vs other factors?

This is the key synthesis: if REGIME explains substantial variance, line syntax
is REGIME-dependent. If it explains little, line syntax is universal.
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

# Collect all position observations with REGIME
observations = []

line_data = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    regime = folio_to_regime.get(token.folio)
    if not regime:
        continue

    key = (token.folio, token.line)
    tc = token_to_class.get(w)
    role = get_role(tc)

    line_data[key].append({
        'word': w,
        'role': role,
        'regime': regime,
        'folio': token.folio,
    })

for key, tokens in line_data.items():
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['role']:
            continue

        pos = i / (n - 1) if n > 1 else 0.5
        observations.append({
            'position': pos,
            'role': t['role'],
            'regime': t['regime'],
            'folio': t['folio'],
        })

print("=" * 60)
print("T6: SYNTAX VARIANCE DECOMPOSITION")
print("=" * 60)

print(f"\nTotal observations: {len(observations)}")

results = {}

# Compute variance explained by REGIME for each role
print("\n" + "-" * 60)
print("VARIANCE EXPLAINED BY REGIME (eta-squared):")
print("-" * 60)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    role_obs = [o for o in observations if o['role'] == role]
    if len(role_obs) < 100:
        continue

    # Group by REGIME
    regime_groups = defaultdict(list)
    for o in role_obs:
        regime_groups[o['regime']].append(o['position'])

    # Need at least 2 groups with sufficient data
    valid_groups = {k: v for k, v in regime_groups.items() if len(v) >= 20}
    if len(valid_groups) < 2:
        continue

    # ANOVA (or Kruskal-Wallis)
    groups = list(valid_groups.values())
    f_stat, p_val = stats.f_oneway(*groups)

    # Eta-squared (variance explained)
    all_positions = [o['position'] for o in role_obs]
    ss_total = np.var(all_positions) * len(all_positions)

    grand_mean = np.mean(all_positions)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)

    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"

    results[role] = {
        'n': len(role_obs),
        'f_stat': float(f_stat),
        'p_val': float(p_val),
        'eta_squared': float(eta_squared),
        'significant': bool(p_val < 0.05),
    }

    print(f"  {role}: F={f_stat:.2f}, p={p_val:.4f} {sig}, eta^2={eta_squared:.4f} ({eta_squared*100:.2f}%)")

# Compare to C815 (phase position variance = 1.5%)
print("\n" + "=" * 60)
print("COMPARISON TO C815 (PHASE POSITION VARIANCE):")
print("=" * 60)

c815_eta = 0.015  # From C815
regime_etas = [r['eta_squared'] for r in results.values() if 'eta_squared' in r]
mean_regime_eta = np.mean(regime_etas) if regime_etas else 0

print(f"\n  C815 (PHASE explains position): eta^2 = {c815_eta:.4f} ({c815_eta*100:.2f}%)")
print(f"  REGIME explains position: mean eta^2 = {mean_regime_eta:.4f} ({mean_regime_eta*100:.2f}%)")

if mean_regime_eta < c815_eta:
    print(f"\n  REGIME explains LESS variance than PHASE itself.")
    print(f"  -> Line syntax is PHASE-driven, not REGIME-driven.")
else:
    print(f"\n  REGIME explains MORE variance than PHASE itself.")
    print(f"  -> REGIME modulates line syntax beyond phase membership.")

# Overall verdict
print("\n" + "=" * 60)
print("OVERALL VERDICT:")
print("=" * 60)

any_significant = any(r.get('significant', False) for r in results.values())
max_eta = max((r.get('eta_squared', 0) for r in results.values()), default=0)

if not any_significant:
    print("\n  LINE SYNTAX IS REGIME-INVARIANT (STRONG)")
    print("  No role shows significant REGIME effect.")
    print("  REGIME encodes execution requirements, not syntax structure.")
elif max_eta < 0.01:
    print("\n  LINE SYNTAX IS REGIME-INVARIANT (WEAK EFFECTS)")
    print(f"  Some significance but max eta^2 = {max_eta:.4f} (<1%)")
    print("  Effects exist but are trivially small.")
elif max_eta < 0.05:
    print("\n  LINE SYNTAX SHOWS MINOR REGIME EFFECTS")
    print(f"  Max eta^2 = {max_eta:.4f} ({max_eta*100:.1f}%)")
    print("  REGIME has detectable but small influence on syntax.")
else:
    print("\n  LINE SYNTAX IS REGIME-DEPENDENT")
    print(f"  Max eta^2 = {max_eta:.4f} ({max_eta*100:.1f}%)")
    print("  REGIME substantially modulates line syntax.")

results['summary'] = {
    'any_significant': bool(any_significant),
    'max_eta_squared': float(max_eta),
    'mean_eta_squared': float(mean_regime_eta),
    'c815_eta_squared': c815_eta,
}

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't6_variance_decomposition.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
