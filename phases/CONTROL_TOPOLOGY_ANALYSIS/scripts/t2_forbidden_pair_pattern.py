"""
T2: Forbidden Pair Pattern Analysis

17 forbidden pairs involve specific class combinations.
Questions:
1. What makes these specific transitions illegal?
2. Is there a structural pattern (role->role, kernel->kernel)?
3. What's the logic of hazard topology?
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

# Role definitions
ROLE_MAP = {}
for cls in [10, 11, 12, 17]:
    ROLE_MAP[cls] = 'CC'
for cls in [8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
    ROLE_MAP[cls] = 'EN'
for cls in [7, 30, 38, 40]:
    ROLE_MAP[cls] = 'FL'
for cls in [9, 13, 14, 23]:
    ROLE_MAP[cls] = 'FQ'
for cls in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
    ROLE_MAP[cls] = 'AX'

FORBIDDEN_PAIRS = [
    (12, 23), (12, 9), (17, 23), (17, 9),
    (10, 12), (10, 17), (11, 12), (11, 17),
    (10, 23), (10, 9), (11, 23), (11, 9),
    (32, 12), (32, 17), (31, 12), (31, 17),
    (23, 9)
]

print("="*70)
print("FORBIDDEN PAIR PATTERN ANALYSIS")
print("="*70)

# ============================================================
# ROLE-LEVEL PATTERN
# ============================================================
print("\n" + "="*70)
print("FORBIDDEN PAIRS BY ROLE")
print("="*70)

role_pairs = Counter()
for c1, c2 in FORBIDDEN_PAIRS:
    r1 = ROLE_MAP.get(c1, 'UNK')
    r2 = ROLE_MAP.get(c2, 'UNK')
    role_pairs[(r1, r2)] += 1

print("\nRole -> Role forbidden transitions:")
for (r1, r2), count in role_pairs.most_common():
    print(f"  {r1} -> {r2}: {count} pairs")

# ============================================================
# CLASS PARTICIPATION
# ============================================================
print("\n" + "="*70)
print("CLASS PARTICIPATION IN FORBIDDEN PAIRS")
print("="*70)

class_participation = Counter()
for c1, c2 in FORBIDDEN_PAIRS:
    class_participation[c1] += 1
    class_participation[c2] += 1

print("\nClasses by forbidden pair involvement:")
for cls, count in class_participation.most_common():
    role = ROLE_MAP.get(cls, 'UNK')
    print(f"  Class {cls} ({role}): {count} appearances")

# ============================================================
# FORBIDDEN PAIR STRUCTURE
# ============================================================
print("\n" + "="*70)
print("FORBIDDEN PAIR STRUCTURE")
print("="*70)

# Group forbidden pairs by pattern
cc_to_cc = [(c1, c2) for c1, c2 in FORBIDDEN_PAIRS
            if ROLE_MAP.get(c1) == 'CC' and ROLE_MAP.get(c2) == 'CC']
cc_to_fq = [(c1, c2) for c1, c2 in FORBIDDEN_PAIRS
            if ROLE_MAP.get(c1) == 'CC' and ROLE_MAP.get(c2) == 'FQ']
en_to_cc = [(c1, c2) for c1, c2 in FORBIDDEN_PAIRS
            if ROLE_MAP.get(c1) == 'EN' and ROLE_MAP.get(c2) == 'CC']
fq_to_fq = [(c1, c2) for c1, c2 in FORBIDDEN_PAIRS
            if ROLE_MAP.get(c1) == 'FQ' and ROLE_MAP.get(c2) == 'FQ']

print(f"\nCC -> CC: {len(cc_to_cc)} pairs")
for p in cc_to_cc:
    print(f"  {p[0]} -> {p[1]}")

print(f"\nCC -> FQ: {len(cc_to_fq)} pairs")
for p in cc_to_fq:
    print(f"  {p[0]} -> {p[1]}")

print(f"\nEN -> CC: {len(en_to_cc)} pairs")
for p in en_to_cc:
    print(f"  {p[0]} -> {p[1]}")

print(f"\nFQ -> FQ: {len(fq_to_fq)} pairs")
for p in fq_to_fq:
    print(f"  {p[0]} -> {p[1]}")

# ============================================================
# CC SUBCLASS ANALYSIS
# ============================================================
print("\n" + "="*70)
print("CC SUBCLASS FORBIDDEN PATTERNS")
print("="*70)

# Classes 10, 11 vs 12, 17 patterns
cc_group_a = {10, 11}  # These are sources
cc_group_b = {12, 17}  # These are targets

print("\nCC classes 10, 11 (Group A) forbidden patterns:")
for c1, c2 in FORBIDDEN_PAIRS:
    if c1 in cc_group_a:
        r2 = ROLE_MAP.get(c2, 'UNK')
        print(f"  {c1} -> {c2} ({r2})")

print("\nCC classes 12, 17 (Group B) forbidden patterns:")
for c1, c2 in FORBIDDEN_PAIRS:
    if c1 in cc_group_b:
        r2 = ROLE_MAP.get(c2, 'UNK')
        print(f"  {c1} -> {c2} ({r2})")

# Check if Group A -> Group B is forbidden
a_to_b = [(c1, c2) for c1, c2 in FORBIDDEN_PAIRS
          if c1 in cc_group_a and c2 in cc_group_b]
print(f"\nGroup A (10,11) -> Group B (12,17): {len(a_to_b)} forbidden pairs")

# ============================================================
# FQ SUBCLASS ANALYSIS
# ============================================================
print("\n" + "="*70)
print("FQ SUBCLASS FORBIDDEN PATTERNS")
print("="*70)

fq_classes = {9, 13, 14, 23}
print(f"\nFQ classes in forbidden pairs: {[c for c in fq_classes if c in class_participation]}")

for cls in fq_classes:
    if cls in class_participation:
        as_source = sum(1 for c1, c2 in FORBIDDEN_PAIRS if c1 == cls)
        as_target = sum(1 for c1, c2 in FORBIDDEN_PAIRS if c2 == cls)
        print(f"  Class {cls}: source={as_source}, target={as_target}")

# ============================================================
# SYMMETRY ANALYSIS
# ============================================================
print("\n" + "="*70)
print("FORBIDDEN PAIR SYMMETRY")
print("="*70)

# Check if (a,b) forbidden implies (b,a) forbidden
symmetric = 0
asymmetric = 0
for c1, c2 in FORBIDDEN_PAIRS:
    if (c2, c1) in FORBIDDEN_PAIRS:
        symmetric += 1
    else:
        asymmetric += 1

# Divide by 2 for symmetric (counted twice)
print(f"\nSymmetric pairs (both directions forbidden): {symmetric // 2}")
print(f"Asymmetric pairs (one direction only): {asymmetric}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Role patterns
if role_pairs[('CC', 'CC')] >= 4:
    findings.append(f"CC_INTERNAL_HAZARD: {role_pairs[('CC', 'CC')]} CC->CC forbidden pairs")

if role_pairs[('CC', 'FQ')] >= 4:
    findings.append(f"CC_FQ_GATING: {role_pairs[('CC', 'FQ')]} CC->FQ forbidden pairs")

if role_pairs[('EN', 'CC')] >= 4:
    findings.append(f"EN_CC_RESTRICTED: {role_pairs[('EN', 'CC')]} EN->CC forbidden pairs")

# Asymmetry
if asymmetric > symmetric:
    findings.append(f"DIRECTIONAL_HAZARDS: {asymmetric} asymmetric vs {symmetric//2} symmetric")

# FL/AX absence
fl_ax_count = sum(1 for c1, c2 in FORBIDDEN_PAIRS
                  if ROLE_MAP.get(c1) in ['FL', 'AX'] or ROLE_MAP.get(c2) in ['FL', 'AX'])
if fl_ax_count == 0:
    findings.append("FL_AX_EXEMPT: FL and AX never appear in forbidden pairs")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

FORBIDDEN PAIR PATTERN:

The 17 forbidden pairs have clear structure:
  - CC -> CC: {role_pairs[('CC', 'CC')]} pairs (internal CC conflicts)
  - CC -> FQ: {role_pairs[('CC', 'FQ')]} pairs (CC cannot trigger FQ directly)
  - EN -> CC: {role_pairs[('EN', 'CC')]} pairs (EN cannot enter CC directly)
  - FQ -> FQ: {role_pairs[('FQ', 'FQ')]} pairs (FQ internal conflict)

CC subgroups:
  - Classes 10, 11: SOURCE in {len([p for p in FORBIDDEN_PAIRS if p[0] in cc_group_a])} pairs
  - Classes 12, 17: TARGET in {len([p for p in FORBIDDEN_PAIRS if p[1] in cc_group_b])} pairs

The pattern suggests:
  - CC has internal hierarchy (10,11 vs 12,17)
  - CC gates FQ access (CC -> FQ forbidden)
  - EN must not directly invoke CC
  - FL and AX are EXEMPT from hazard topology
""")

# Save results
results = {
    'role_pairs': {f"{r1}->{r2}": c for (r1, r2), c in role_pairs.items()},
    'class_participation': dict(class_participation),
    'cc_to_cc': cc_to_cc,
    'cc_to_fq': cc_to_fq,
    'en_to_cc': en_to_cc,
    'fq_to_fq': fq_to_fq,
    'symmetric_count': symmetric // 2,
    'asymmetric_count': asymmetric,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CONTROL_TOPOLOGY_ANALYSIS' / 'results' / 't2_forbidden_pair_pattern.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
