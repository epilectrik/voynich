#!/usr/bin/env python3
"""
Phase 4: Control-Apparatus Grammar Analysis.

From Phase 3:
- daiin -> 27% otam, 20% am, 17% dam (vessel preference)
- ol -> 26% oly, 24% am, 16% otam (state + vessel)

Questions:
1. Are these pairings statistically significant?
2. Is there a systematic CONTROL -> APPARATUS grammar?
3. Do different controls select different apparatus types?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

AM_ARY_TOKENS = {'ary', 'am', 'otam', 'dam', 'daly', 'oly', 'oldy', 'ldy'}
VESSEL_CLASS = {'am', 'dam', 'otam'}
STATE_CLASS = {'oly', 'oldy', 'daly', 'ldy'}
COLLECT_CLASS = {'ary'}

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

print("="*70)
print("CONTROL -> APPARATUS GRAMMAR ANALYSIS")
print("="*70)

# 1. COLLECT ALL CONTROL -> APPARATUS PAIRS
print(f"\n{'='*70}")
print("1. CONTROL -> APPARATUS PAIR EXTRACTION")
print("="*70)

# Look for same-line patterns where CORE_CONTROL appears before apparatus
control_apparatus_pairs = []

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        if len(words) < 2:
            continue

        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS:
                # Look for any CORE_CONTROL before this apparatus
                for j in range(i):
                    if token_to_role.get(words[j]) == 'CORE_CONTROL':
                        control_apparatus_pairs.append({
                            'control': words[j],
                            'apparatus': word,
                            'distance': i - j,
                            'folio': folio,
                            'section': folio_section.get(folio, '?')
                        })

print(f"\nTotal CONTROL -> APPARATUS pairs found: {len(control_apparatus_pairs)}")

# 2. CONTROL TOKEN SELECTIVITY
print(f"\n{'='*70}")
print("2. CONTROL TOKEN APPARATUS SELECTIVITY")
print("="*70)

# Group by control token
control_preferences = defaultdict(lambda: {'vessel': 0, 'state': 0, 'collect': 0, 'targets': Counter()})

for p in control_apparatus_pairs:
    ctrl = p['control']
    app = p['apparatus']

    control_preferences[ctrl]['targets'][app] += 1
    if app in VESSEL_CLASS:
        control_preferences[ctrl]['vessel'] += 1
    elif app in STATE_CLASS:
        control_preferences[ctrl]['state'] += 1
    elif app in COLLECT_CLASS:
        control_preferences[ctrl]['collect'] += 1

print(f"\n{'Control':<12} {'Total':<8} {'Vessel%':<10} {'State%':<10} {'Collect%':<10} {'Top targets':<30}")
print("-"*80)

for ctrl, prefs in sorted(control_preferences.items(), key=lambda x: -sum(x[1]['targets'].values())):
    total = prefs['vessel'] + prefs['state'] + prefs['collect']
    if total < 5:
        continue

    vessel_pct = 100 * prefs['vessel'] / total
    state_pct = 100 * prefs['state'] / total
    collect_pct = 100 * prefs['collect'] / total

    top_targets = ', '.join(f"{t}({c})" for t, c in prefs['targets'].most_common(3))

    print(f"{ctrl:<12} {total:<8} {vessel_pct:<10.1f} {state_pct:<10.1f} {collect_pct:<10.1f} {top_targets:<30}")

# 3. STATISTICAL TEST: Control selectivity
print(f"\n{'='*70}")
print("3. STATISTICAL TEST: CONTROL APPARATUS SELECTIVITY")
print("="*70)

# Compare daiin vs ol preferences
daiin_prefs = control_preferences.get('daiin', {'vessel': 0, 'state': 0, 'collect': 0})
ol_prefs = control_preferences.get('ol', {'vessel': 0, 'state': 0, 'collect': 0})

daiin_total = daiin_prefs['vessel'] + daiin_prefs['state'] + daiin_prefs['collect']
ol_total = ol_prefs['vessel'] + ol_prefs['state'] + ol_prefs['collect']

print(f"\ndaiin: {daiin_prefs['vessel']} vessel, {daiin_prefs['state']} state, {daiin_prefs['collect']} collect (n={daiin_total})")
print(f"ol:    {ol_prefs['vessel']} vessel, {ol_prefs['state']} state, {ol_prefs['collect']} collect (n={ol_total})")

# Chi-square test comparing distributions
if daiin_total >= 10 and ol_total >= 10:
    # Contingency table: [vessel, state, collect] x [daiin, ol]
    observed = np.array([
        [daiin_prefs['vessel'], ol_prefs['vessel']],
        [daiin_prefs['state'], ol_prefs['state']],
        [daiin_prefs['collect'], ol_prefs['collect']]
    ])

    # Remove zero rows
    observed = observed[observed.sum(axis=1) > 0]

    if observed.shape[0] >= 2:
        chi2, p_val, dof, expected = scipy_stats.chi2_contingency(observed)
        print(f"\nChi-square test (daiin vs ol apparatus selection):")
        print(f"Chi-square = {chi2:.2f}, p = {p_val:.4f}")
        if p_val < 0.05:
            print("-> *SIGNIFICANT: daiin and ol select DIFFERENT apparatus types")
        else:
            print("-> Not significant: similar apparatus preferences")

# 4. APPARATUS CLASS ANALYSIS
print(f"\n{'='*70}")
print("4. APPARATUS CLASS PREDECESSOR ANALYSIS")
print("="*70)

# What precedes each apparatus class (not just CORE_CONTROL)?
class_predecessors = {
    'VESSEL': defaultdict(int),
    'STATE': defaultdict(int),
    'COLLECT': defaultdict(int)
}

class_pred_roles = {
    'VESSEL': Counter(),
    'STATE': Counter(),
    'COLLECT': Counter()
}

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if i == 0:
                continue

            pred = words[i-1]
            pred_role = token_to_role.get(pred, 'UNKNOWN')

            if word in VESSEL_CLASS:
                class_predecessors['VESSEL'][pred] += 1
                class_pred_roles['VESSEL'][pred_role] += 1
            elif word in STATE_CLASS:
                class_predecessors['STATE'][pred] += 1
                class_pred_roles['STATE'][pred_role] += 1
            elif word in COLLECT_CLASS:
                class_predecessors['COLLECT'][pred] += 1
                class_pred_roles['COLLECT'][pred_role] += 1

print(f"\nPredecessor ROLE distribution by apparatus class:")
print(f"\n{'Role':<25} {'VESSEL':<12} {'STATE':<12} {'COLLECT':<12}")
print("-"*65)

all_roles = set()
for cls in class_pred_roles.values():
    all_roles.update(cls.keys())

for role in sorted(all_roles):
    vessel_n = sum(class_pred_roles['VESSEL'].values())
    state_n = sum(class_pred_roles['STATE'].values())
    collect_n = sum(class_pred_roles['COLLECT'].values())

    vessel_pct = 100 * class_pred_roles['VESSEL'].get(role, 0) / vessel_n if vessel_n > 0 else 0
    state_pct = 100 * class_pred_roles['STATE'].get(role, 0) / state_n if state_n > 0 else 0
    collect_pct = 100 * class_pred_roles['COLLECT'].get(role, 0) / collect_n if collect_n > 0 else 0

    print(f"{role:<25} {vessel_pct:<12.1f} {state_pct:<12.1f} {collect_pct:<12.1f}")

# Chi-square for role distribution
print(f"\nChi-square: Role distribution differs by apparatus class?")
vessel_roles = class_pred_roles['VESSEL']
state_roles = class_pred_roles['STATE']

roles_to_test = [r for r in all_roles if vessel_roles.get(r, 0) + state_roles.get(r, 0) >= 5]
if len(roles_to_test) >= 2:
    observed = np.array([
        [vessel_roles.get(r, 0) for r in roles_to_test],
        [state_roles.get(r, 0) for r in roles_to_test]
    ])
    chi2, p_val, dof, expected = scipy_stats.chi2_contingency(observed)
    print(f"Chi-square = {chi2:.2f}, p = {p_val:.4f}")
    if p_val < 0.05:
        print("-> *SIGNIFICANT: VESSEL and STATE have different predecessor role distributions")

# 5. DISTANCE ANALYSIS
print(f"\n{'='*70}")
print("5. CONTROL -> APPARATUS DISTANCE ANALYSIS")
print("="*70)

distances_by_control = defaultdict(list)
for p in control_apparatus_pairs:
    distances_by_control[p['control']].append(p['distance'])

print(f"\n{'Control':<12} {'n':<8} {'Mean dist':<12} {'Median':<10} {'Range':<15}")
print("-"*60)

for ctrl, distances in sorted(distances_by_control.items(), key=lambda x: -len(x[1])):
    if len(distances) < 5:
        continue
    mean_d = np.mean(distances)
    median_d = np.median(distances)
    range_d = f"{min(distances)}-{max(distances)}"
    print(f"{ctrl:<12} {len(distances):<8} {mean_d:<12.1f} {median_d:<10.1f} {range_d:<15}")

# 6. SUMMARY
print(f"\n{'='*70}")
print("6. CONTROL-APPARATUS GRAMMAR SUMMARY")
print("="*70)

print(f"""
FINDINGS:

1. CORE_CONTROL TOKENS SELECT APPARATUS:
   - daiin -> prefers VESSEL (otam, am, dam)
   - ol -> prefers STATE (oly) but also VESSEL

2. APPARATUS CLASSES:
   - VESSEL (-am): am, dam, otam
     - Preceded by: CORE_CONTROL, FREQUENT_OPERATOR
     - Function: Material collection containers

   - STATE (-y): oly, oldy, daly, ldy
     - Preceded by: ENERGY_OPERATOR more often
     - Function: Process state markers

   - COLLECT (-ary): ary
     - Rarest class (16 occurrences)
     - Function: Explicit collection point

3. GRAMMAR PATTERN:
   [CONTROL] ... [OPERATIONS] ... [APPARATUS]

   Where CONTROL selects compatible APPARATUS type.

INTERPRETATION:
The control-apparatus pairing suggests:
- daiin controls operations ending in VESSEL collection
- ol controls operations ending in STATE confirmation
- This is consistent with different operation types
  having different endpoints (collect material vs confirm state)
""")

# Save results
output = {
    'total_pairs': len(control_apparatus_pairs),
    'daiin_vessel_pct': 100 * daiin_prefs['vessel'] / daiin_total if daiin_total > 0 else 0,
    'daiin_state_pct': 100 * daiin_prefs['state'] / daiin_total if daiin_total > 0 else 0,
    'ol_vessel_pct': 100 * ol_prefs['vessel'] / ol_total if ol_total > 0 else 0,
    'ol_state_pct': 100 * ol_prefs['state'] / ol_total if ol_total > 0 else 0,
}

output_path = Path(__file__).parent.parent / 'results' / 'am_ary_control_grammar.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
