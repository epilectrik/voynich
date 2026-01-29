"""
T1: AZC Role Coverage by Folio

Question: Do separate AZC folios cover different token roles?

Method:
1. For each AZC folio (diagram text only, exclude P-placement)
2. Classify each token by role using class_token_map
3. Compute role distribution per folio
4. Test for differentiation: do some folios specialize in certain roles?

Roles from class_token_map:
- KERNEL (k, h, e operators)
- LINK (monitoring/waiting)
- CORE_CONTROL (daiin, ol, etc)
- AUXILIARY (less critical)
- UN (unclassified, outside 49-class grammar)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

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
class_to_role = ctm.get('class_to_role', {})

# Define role categories based on class names
def get_role(token):
    """Map token to role category."""
    if token not in token_to_class:
        return 'UN'

    cls = token_to_class[token]

    # KERNEL classes
    if cls in ['k', 'h', 'e']:
        return 'KERNEL'

    # LINK class
    if cls == 'LINK':
        return 'LINK'

    # Check class_to_role if available
    if cls in class_to_role:
        return class_to_role[cls]

    # Default to OPERATIONAL for classified tokens
    return 'OPERATIONAL'

# Define which folios are Zodiac family vs A/C family
ZODIAC_FOLIOS = {
    'f72v3', 'f72v2', 'f72v1', 'f72r3', 'f72r2', 'f72r1',
    'f71v', 'f71r', 'f70v2', 'f70v1', 'f73v', 'f73r', 'f57v'
}

# Collect AZC tokens by folio
folio_tokens = defaultdict(list)
folio_placements = defaultdict(set)

print("Collecting AZC tokens...")

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    # Skip P-placement (Currier A text)
    placement = getattr(token, 'placement', '')
    if placement.startswith('P'):
        continue

    folio = token.folio
    folio_tokens[folio].append(w)
    folio_placements[folio].add(placement)

print(f"Found {len(folio_tokens)} AZC folios with diagram text")

# Analyze role distribution per folio
results = {
    'folio_stats': {},
    'summary': {},
}

all_roles = ['KERNEL', 'LINK', 'OPERATIONAL', 'UN']
role_by_folio = {}

for folio in sorted(folio_tokens.keys()):
    tokens = folio_tokens[folio]

    # Count roles
    role_counts = Counter(get_role(t) for t in tokens)
    total = sum(role_counts.values())

    role_pct = {r: 100.0 * role_counts.get(r, 0) / total for r in all_roles}

    # Determine family
    family = 'Zodiac' if folio in ZODIAC_FOLIOS else 'A/C'

    results['folio_stats'][folio] = {
        'total_tokens': total,
        'family': family,
        'role_counts': dict(role_counts),
        'role_pct': role_pct,
        'placements': sorted(folio_placements[folio]),
    }

    role_by_folio[folio] = role_pct

    print(f"{folio:8} ({family:6}): {total:4} tokens | "
          f"KERNEL {role_pct['KERNEL']:5.1f}% | "
          f"LINK {role_pct['LINK']:5.1f}% | "
          f"OP {role_pct['OPERATIONAL']:5.1f}% | "
          f"UN {role_pct['UN']:5.1f}%")

# Aggregate by family
zodiac_tokens = []
ac_tokens = []

for folio, tokens in folio_tokens.items():
    if folio in ZODIAC_FOLIOS:
        zodiac_tokens.extend(tokens)
    else:
        ac_tokens.extend(tokens)

zodiac_roles = Counter(get_role(t) for t in zodiac_tokens)
ac_roles = Counter(get_role(t) for t in ac_tokens)

zodiac_total = sum(zodiac_roles.values())
ac_total = sum(ac_roles.values())

print("\n" + "="*60)
print("FAMILY SUMMARY")
print("="*60)

print(f"\nZodiac family ({len([f for f in folio_tokens if f in ZODIAC_FOLIOS])} folios, {zodiac_total} tokens):")
for role in all_roles:
    pct = 100.0 * zodiac_roles.get(role, 0) / zodiac_total
    print(f"  {role:12}: {zodiac_roles.get(role, 0):4} ({pct:5.1f}%)")

print(f"\nA/C family ({len([f for f in folio_tokens if f not in ZODIAC_FOLIOS])} folios, {ac_total} tokens):")
for role in all_roles:
    pct = 100.0 * ac_roles.get(role, 0) / ac_total
    print(f"  {role:12}: {ac_roles.get(role, 0):4} ({pct:5.1f}%)")

# Test for differentiation: chi-squared on family role profiles
from scipy import stats

# Build contingency table: families x roles (only roles with counts > 0)
non_zero_roles = [r for r in all_roles if zodiac_roles.get(r, 0) > 0 or ac_roles.get(r, 0) > 0]
observed = [
    [zodiac_roles.get(r, 0) for r in non_zero_roles],
    [ac_roles.get(r, 0) for r in non_zero_roles],
]

if len(non_zero_roles) >= 2 and min(sum(row) for row in observed) > 0:
    chi2, p_val, dof, expected = stats.chi2_contingency(observed)
    print(f"\nFamily differentiation test (roles: {non_zero_roles}):")
    print(f"  Chi-squared: {chi2:.2f}, df={dof}, p={p_val:.4f}")
else:
    chi2, p_val, dof = 0, 1.0, 0
    print(f"\nFamily differentiation test: insufficient variance (only roles: {non_zero_roles})")

# Test for folio-level differentiation within each family
print("\n" + "="*60)
print("FOLIO-LEVEL DIFFERENTIATION")
print("="*60)

# Compute variance of role percentages across folios
import numpy as np

zodiac_role_pcts = {r: [] for r in all_roles}
ac_role_pcts = {r: [] for r in all_roles}

for folio, role_pct in role_by_folio.items():
    target = zodiac_role_pcts if folio in ZODIAC_FOLIOS else ac_role_pcts
    for role in all_roles:
        target[role].append(role_pct[role])

print("\nZodiac family role variance (std dev of %):")
for role in all_roles:
    if zodiac_role_pcts[role]:
        std = np.std(zodiac_role_pcts[role])
        mean = np.mean(zodiac_role_pcts[role])
        print(f"  {role:12}: mean={mean:5.1f}%, std={std:5.1f}%")

print("\nA/C family role variance (std dev of %):")
for role in all_roles:
    if ac_role_pcts[role]:
        std = np.std(ac_role_pcts[role])
        mean = np.mean(ac_role_pcts[role])
        print(f"  {role:12}: mean={mean:5.1f}%, std={std:5.1f}%")

# Find extreme folios
print("\n" + "="*60)
print("EXTREME FOLIOS (highest/lowest per role)")
print("="*60)

for role in all_roles:
    sorted_folios = sorted(role_by_folio.items(), key=lambda x: x[1][role])
    lowest = sorted_folios[:3]
    highest = sorted_folios[-3:][::-1]

    print(f"\n{role}:")
    print(f"  Highest: {', '.join([f'{f}({p[role]:.1f}%)' for f,p in highest])}")
    print(f"  Lowest:  {', '.join([f'{f}({p[role]:.1f}%)' for f,p in lowest])}")

# Summary
results['summary'] = {
    'total_folios': len(folio_tokens),
    'zodiac_folios': len([f for f in folio_tokens if f in ZODIAC_FOLIOS]),
    'ac_folios': len([f for f in folio_tokens if f not in ZODIAC_FOLIOS]),
    'zodiac_tokens': zodiac_total,
    'ac_tokens': ac_total,
    'family_chi2': chi2,
    'family_chi2_p': p_val,
    'zodiac_role_means': {r: float(np.mean(zodiac_role_pcts[r])) if zodiac_role_pcts[r] else 0 for r in all_roles},
    'ac_role_means': {r: float(np.mean(ac_role_pcts[r])) if ac_role_pcts[r] else 0 for r in all_roles},
}

# Save results
out_path = Path(__file__).parent.parent / 'results' / 't1_role_coverage.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if p_val < 0.01:
    verdict = "FAMILY_DIFFERENTIATED"
    print(f"Zodiac and A/C families have DIFFERENT role profiles (p={p_val:.4f})")
else:
    verdict = "FAMILY_UNIFORM"
    print(f"Zodiac and A/C families have SIMILAR role profiles (p={p_val:.4f})")

results['verdict'] = verdict

# Update saved results
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)
