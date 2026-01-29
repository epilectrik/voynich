"""
T7: Role-Compound Correlation Analysis

Question: Does compound MIDDLE usage correlate with functional roles?
- CC (Core Control): Classes {10, 11, 12, 17}
- EN (Energy Operator): Classes {8, 31-37, 39, 41-49}
- FL (Flow Operator): Classes {7, 30, 38, 40}
- FQ (Frequent Operator): Classes {9, 13, 14, 23}
- AX (Auxiliary): Classes {1-6, 15, 16, 18-22, 24-29}

Does kernel operator involvement (k, h, e) correlate with base vs compound usage?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

tx = Transcript()
morph = Morphology()

# Load T6 results for class compound profiles
t6_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't6_class_compound_profile.json'
with open(t6_path, 'r', encoding='utf-8') as f:
    t6 = json.load(f)

class_profiles = {p['class']: p for p in t6['class_profiles']}

# Define role taxonomy from BCSC
ROLE_TAXONOMY = {
    'CC': {10, 11, 12, 17},  # Core Control
    'EN': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},  # Energy
    'FL': {7, 30, 38, 40},  # Flow
    'FQ': {9, 13, 14, 23},  # Frequent
    'AX': {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},  # Auxiliary
}

# Reverse mapping: class -> role
class_to_role = {}
for role, classes in ROLE_TAXONOMY.items():
    for cls in classes:
        class_to_role[cls] = role

print("="*70)
print("ROLE COMPOUND PROFILE")
print("="*70)

role_stats = {}

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    classes = ROLE_TAXONOMY[role]

    # Get all class profiles for this role
    role_profiles = [class_profiles[c] for c in classes if c in class_profiles]

    if not role_profiles:
        continue

    total_tokens = sum(p['total_tokens'] for p in role_profiles)
    total_compound = sum(p['compound_count'] for p in role_profiles)
    weighted_compound_rate = 100 * total_compound / total_tokens if total_tokens else 0

    # Also get simple average across classes
    avg_compound_rate = sum(p['compound_rate'] for p in role_profiles) / len(role_profiles)

    # Count base-only vs compound-heavy classes in this role
    base_only = sum(1 for p in role_profiles if p['compound_rate'] < 5)
    compound_heavy = sum(1 for p in role_profiles if p['compound_rate'] >= 85)

    role_stats[role] = {
        'classes': len(role_profiles),
        'total_tokens': total_tokens,
        'compound_tokens': total_compound,
        'weighted_compound_rate': weighted_compound_rate,
        'avg_compound_rate': avg_compound_rate,
        'base_only_classes': base_only,
        'compound_heavy_classes': compound_heavy
    }

    print(f"\n{role} ({len(role_profiles)} classes, {total_tokens} tokens):")
    print(f"  Weighted compound rate: {weighted_compound_rate:.1f}%")
    print(f"  Average compound rate: {avg_compound_rate:.1f}%")
    print(f"  Base-only classes: {base_only}")
    print(f"  Compound-heavy classes: {compound_heavy}")

# ============================================================
# DETAILED CLASS BREAKDOWN BY ROLE
# ============================================================
print("\n" + "="*70)
print("DETAILED CLASS BREAKDOWN BY ROLE")
print("="*70)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    classes = ROLE_TAXONOMY[role]
    role_profiles = [(c, class_profiles[c]) for c in sorted(classes) if c in class_profiles]

    print(f"\n{role}:")
    print(f"  {'Class':<8} {'Tokens':<8} {'Compound%':<12} {'Category'}")
    print(f"  {'-'*8} {'-'*8} {'-'*12} {'-'*15}")

    for cls, p in sorted(role_profiles, key=lambda x: x[1]['compound_rate']):
        if p['compound_rate'] < 5:
            cat = "BASE-ONLY"
        elif p['compound_rate'] < 30:
            cat = "LOW"
        elif p['compound_rate'] < 60:
            cat = "MEDIUM"
        elif p['compound_rate'] < 85:
            cat = "HIGH"
        else:
            cat = "COMPOUND-HEAVY"
        print(f"  {cls:<8} {p['total_tokens']:<8} {p['compound_rate']:<12.1f} {cat}")

# ============================================================
# KERNEL OPERATOR ANALYSIS
# ============================================================
print("\n" + "="*70)
print("KERNEL OPERATOR ANALYSIS")
print("="*70)

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)

token_to_class = ctm['token_to_class']

# Build MiddleAnalyzer
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer.get_core_middles()

# The kernel operators are k, h, e - these are MIDDLE-level concepts
# Check which MIDDLEs are associated with kernel behavior
# From BCSC: k=ENERGY_MODULATOR, h=PHASE_MANAGER, e=STABILITY_ANCHOR

# Let's check the MIDDLEs used by each role
role_middles = defaultdict(set)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or w not in token_to_class:
        continue

    cls = int(token_to_class[w])
    role = class_to_role.get(cls, 'UNKNOWN')

    m = morph.extract(w)
    if m.middle:
        role_middles[role].add(m.middle)

print("\nMIDDLEs by role:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    mids = role_middles[role]
    print(f"\n{role}: {len(mids)} unique MIDDLEs")
    print(f"  Samples: {sorted(mids, key=len)[:15]}")

    # Check for kernel-related MIDDLEs (those containing k, h, or e patterns)
    k_containing = [m for m in mids if 'k' in m]
    h_containing = [m for m in mids if 'h' in m]
    e_containing = [m for m in mids if 'e' in m]

    print(f"  k-containing: {len(k_containing)} ({sorted(k_containing)[:5]})")
    print(f"  h-containing: {len(h_containing)} ({sorted(h_containing)[:5]})")
    print(f"  e-containing: {len(e_containing)} ({sorted(e_containing)[:5]})")

# ============================================================
# CHECK: Do base-only classes use kernel MIDDLEs?
# ============================================================
print("\n" + "="*70)
print("BASE-ONLY CLASSES AND KERNEL MIDDLEs")
print("="*70)

base_only_classes = t6['categories']['base_only']
compound_heavy_classes = t6['categories']['compound_heavy']

base_middles = set()
compound_middles = set()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or w not in token_to_class:
        continue

    cls = int(token_to_class[w])
    m = morph.extract(w)
    if not m.middle:
        continue

    if cls in base_only_classes:
        base_middles.add(m.middle)
    elif cls in compound_heavy_classes:
        compound_middles.add(m.middle)

print(f"\nBase-only class MIDDLEs: {sorted(base_middles)}")
print(f"\nCompound-heavy class MIDDLEs: {sorted(compound_middles)}")

# Check kernel character presence
base_kernel = {'k': [], 'h': [], 'e': [], 'other': []}
for m in base_middles:
    if 'k' in m:
        base_kernel['k'].append(m)
    if 'h' in m:
        base_kernel['h'].append(m)
    if 'e' in m:
        base_kernel['e'].append(m)
    if 'k' not in m and 'h' not in m and 'e' not in m:
        base_kernel['other'].append(m)

print(f"\nBase-only MIDDLEs kernel content:")
print(f"  Contains 'k': {base_kernel['k']}")
print(f"  Contains 'h': {base_kernel['h']}")
print(f"  Contains 'e': {base_kernel['e']}")
print(f"  No kernel chars: {base_kernel['other']}")

# ============================================================
# ROLE-COMPOUND CORRELATION SUMMARY
# ============================================================
print("\n" + "="*70)
print("ROLE-COMPOUND CORRELATION SUMMARY")
print("="*70)

# Rank roles by compound rate
sorted_roles = sorted(role_stats.items(), key=lambda x: x[1]['weighted_compound_rate'])

print(f"\nRoles ranked by compound rate (low to high):")
for role, stats in sorted_roles:
    print(f"  {role}: {stats['weighted_compound_rate']:.1f}% compound ({stats['total_tokens']} tokens)")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

# Check if there's a clear pattern
role_rates = {role: stats['weighted_compound_rate'] for role, stats in role_stats.items()}
max_role = max(role_rates, key=role_rates.get)
min_role = min(role_rates, key=role_rates.get)
spread = role_rates[max_role] - role_rates[min_role]

findings = []

if spread > 20:
    findings.append(f"ROLE_DIFFERENTIATION: {spread:.1f}pp spread between {max_role} ({role_rates[max_role]:.1f}%) and {min_role} ({role_rates[min_role]:.1f}%)")

# Check for specific patterns
if role_rates.get('CC', 0) > 50:
    findings.append("CC_COMPOUND: Core Control is compound-heavy")
elif role_rates.get('CC', 100) < 20:
    findings.append("CC_BASE: Core Control uses base MIDDLEs")

if role_rates.get('EN', 0) > 50:
    findings.append("EN_COMPOUND: Energy Operators favor compound MIDDLEs")

if role_rates.get('FL', 100) < 20:
    findings.append("FL_BASE: Flow Operators use base MIDDLEs")

if findings:
    print("\nCompound usage CORRELATES with functional roles:")
    for f in findings:
        print(f"  - {f}")
    verdict = "ROLE_CORRELATED"
else:
    print("\nCompound usage does NOT strongly correlate with roles")
    verdict = "NOT_CORRELATED"

# Save results
results = {
    'role_stats': role_stats,
    'role_compound_rates': role_rates,
    'base_only_classes': base_only_classes,
    'compound_heavy_classes': compound_heavy_classes,
    'base_middles': list(base_middles),
    'compound_middles': list(compound_middles),
    'findings': findings,
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't7_role_compound_correlation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
