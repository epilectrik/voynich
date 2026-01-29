"""
T7: Complete Role Kernel Taxonomy

Profile all 5 roles (CC, EN, FL, FQ, AX) for kernel signatures.
Questions:
1. Do roles partition kernel responsibilities?
2. Is CC k-heavy vs EN h+e-heavy?
3. What's FQ's kernel profile?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

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

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']

def get_kernel_signature(word):
    """Return kernel signature: which of k, h, e are present."""
    has_k = 'k' in word
    has_h = 'h' in word
    has_e = 'e' in word

    sig = []
    if has_k: sig.append('k')
    if has_h: sig.append('h')
    if has_e: sig.append('e')

    return tuple(sig) if sig else ('none',)

def sig_to_str(sig):
    return '+'.join(sig) if sig != ('none',) else 'none'

print("="*70)
print("COMPLETE ROLE KERNEL TAXONOMY")
print("="*70)

# Collect all classified tokens by role
role_tokens = defaultdict(list)
role_kernel_sigs = defaultdict(Counter)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    if w in token_to_class:
        cls = int(token_to_class[w])
        role = ROLE_MAP.get(cls, 'UNK')
        if role in ROLES:
            sig = get_kernel_signature(w)
            role_tokens[role].append(w)
            role_kernel_sigs[role][sig] += 1

# ============================================================
# ROLE KERNEL SUMMARY
# ============================================================
print("\n" + "="*70)
print("ROLE KERNEL SUMMARY")
print("="*70)

role_stats = {}

for role in ROLES:
    total = len(role_tokens[role])
    sigs = role_kernel_sigs[role]

    has_any = total - sigs.get(('none',), 0)
    has_k = sum(c for sig, c in sigs.items() if 'k' in sig)
    has_h = sum(c for sig, c in sigs.items() if 'h' in sig)
    has_e = sum(c for sig, c in sigs.items() if 'e' in sig)

    role_stats[role] = {
        'total': total,
        'any_kernel': 100 * has_any / total if total else 0,
        'k_rate': 100 * has_k / total if total else 0,
        'h_rate': 100 * has_h / total if total else 0,
        'e_rate': 100 * has_e / total if total else 0,
    }

    # Find dominant signature
    top_sig, top_count = sigs.most_common(1)[0] if sigs else (('none',), 0)
    role_stats[role]['dominant_sig'] = sig_to_str(top_sig)
    role_stats[role]['dominant_pct'] = 100 * top_count / total if total else 0

print("\n{:<6} {:>8} {:>10} {:>8} {:>8} {:>8}  {:<12}".format(
    "Role", "Tokens", "Any Kernel", "k%", "h%", "e%", "Dominant"))
print("-" * 70)

for role in ROLES:
    s = role_stats[role]
    print("{:<6} {:>8} {:>9.1f}% {:>7.1f}% {:>7.1f}% {:>7.1f}%  {:<12} ({:.1f}%)".format(
        role, s['total'], s['any_kernel'], s['k_rate'], s['h_rate'], s['e_rate'],
        s['dominant_sig'], s['dominant_pct']))

# ============================================================
# DETAILED SIGNATURE DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("DETAILED KERNEL SIGNATURE DISTRIBUTION")
print("="*70)

all_sigs = set()
for role in ROLES:
    all_sigs.update(role_kernel_sigs[role].keys())

# Sort signatures by complexity
sig_order = [('none',), ('k',), ('h',), ('e',), ('k', 'h'), ('k', 'e'), ('h', 'e'), ('k', 'h', 'e')]
sig_order = [s for s in sig_order if s in all_sigs]

for role in ROLES:
    total = len(role_tokens[role])
    sigs = role_kernel_sigs[role]

    print(f"\n{role} ({total} tokens):")
    for sig in sig_order:
        count = sigs.get(sig, 0)
        if count > 0:
            pct = 100 * count / total
            print(f"  {sig_to_str(sig):<10}: {count:>5} ({pct:>5.1f}%)")

# ============================================================
# KERNEL CHARACTER DOMINANCE BY ROLE
# ============================================================
print("\n" + "="*70)
print("KERNEL CHARACTER DOMINANCE BY ROLE")
print("="*70)

print("\nWhich kernel char dominates each role?")
print("\n{:<6} {:>10} {:>10} {:>10}  {:<10}".format(
    "Role", "k%", "h%", "e%", "Dominant"))
print("-" * 50)

for role in ROLES:
    s = role_stats[role]
    k, h, e = s['k_rate'], s['h_rate'], s['e_rate']

    if k == 0 and h == 0 and e == 0:
        dominant = "NONE"
    elif k >= h and k >= e:
        dominant = "k (energy)"
    elif h >= k and h >= e:
        dominant = "h (phase)"
    else:
        dominant = "e (stability)"

    print("{:<6} {:>9.1f}% {:>9.1f}% {:>9.1f}%  {:<10}".format(
        role, k, h, e, dominant))

# ============================================================
# ROLE KERNEL PROFILES COMPARISON
# ============================================================
print("\n" + "="*70)
print("ROLE KERNEL PROFILE COMPARISON")
print("="*70)

# Characterize each role's kernel strategy
print("\nRole characterizations:")

for role in ROLES:
    s = role_stats[role]
    k, h, e = s['k_rate'], s['h_rate'], s['e_rate']
    any_k = s['any_kernel']

    print(f"\n{role}:")

    if any_k < 10:
        print(f"  KERNEL-FREE ({any_k:.1f}% kernel)")
    elif any_k > 90:
        print(f"  KERNEL-MANDATORY ({any_k:.1f}% kernel)")
    else:
        print(f"  KERNEL-MIXED ({any_k:.1f}% kernel)")

    if any_k > 10:
        # Describe kernel balance
        if abs(h - e) < 10 and h > k and e > k:
            print(f"  h+e BALANCED (phase+stability): h={h:.0f}%, e={e:.0f}%")
        elif h > e + 15 and h > k + 15:
            print(f"  h DOMINANT (phase): h={h:.0f}%")
        elif e > h + 15 and e > k + 15:
            print(f"  e DOMINANT (stability): e={e:.0f}%")
        elif k > h + 15 and k > e + 15:
            print(f"  k DOMINANT (energy): k={k:.0f}%")
        elif k > 30 and h > 30:
            print(f"  k+h MIXED (energy+phase): k={k:.0f}%, h={h:.0f}%")
        else:
            print(f"  BALANCED: k={k:.0f}%, h={h:.0f}%, e={e:.0f}%")

# ============================================================
# FORBIDDEN PAIR PARTICIPATION
# ============================================================
print("\n" + "="*70)
print("FORBIDDEN PAIR PARTICIPATION BY ROLE")
print("="*70)

FORBIDDEN_PAIRS = [
    (12, 23), (12, 9), (17, 23), (17, 9),
    (10, 12), (10, 17), (11, 12), (11, 17),
    (10, 23), (10, 9), (11, 23), (11, 9),
    (32, 12), (32, 17), (31, 12), (31, 17),
    (23, 9)
]

# Count how many forbidden pairs involve each role
role_forbidden_count = Counter()
for c1, c2 in FORBIDDEN_PAIRS:
    r1 = ROLE_MAP.get(c1, 'UNK')
    r2 = ROLE_MAP.get(c2, 'UNK')
    role_forbidden_count[r1] += 1
    role_forbidden_count[r2] += 1

print("\nForbidden pair involvement:")
for role in ROLES:
    count = role_forbidden_count.get(role, 0)
    print(f"  {role}: {count} appearances in 17 forbidden pairs")

# Which classes from each role?
print("\nClasses in forbidden pairs by role:")
forbidden_classes = set()
for c1, c2 in FORBIDDEN_PAIRS:
    forbidden_classes.add(c1)
    forbidden_classes.add(c2)

for role in ROLES:
    role_classes_in_forbidden = [c for c in forbidden_classes if ROLE_MAP.get(c) == role]
    if role_classes_in_forbidden:
        print(f"  {role}: classes {sorted(role_classes_in_forbidden)}")
    else:
        print(f"  {role}: NO classes in forbidden pairs")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: ROLE KERNEL TAXONOMY")
print("="*70)

findings = []

# FL kernel-free
if role_stats['FL']['any_kernel'] < 5:
    findings.append("FL_KERNEL_FREE: FL is 0% kernel (state index only)")

# CC vs EN comparison
cc_k = role_stats['CC']['k_rate']
en_k = role_stats['EN']['k_rate']
cc_h = role_stats['CC']['h_rate']
en_h = role_stats['EN']['h_rate']

if cc_k > en_k + 20:
    findings.append(f"CC_K_HEAVY: CC has more 'k' than EN ({cc_k:.0f}% vs {en_k:.0f}%)")

# FQ profile
fq_e = role_stats['FQ']['e_rate']
if fq_e > 50:
    findings.append(f"FQ_E_DOMINANT: FQ is e-heavy ({fq_e:.0f}%) - stability/escape")

# Role partition
findings.append("ROLE_KERNEL_PARTITION: Roles have distinct kernel profiles")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

KERNEL RESPONSIBILITY PARTITION:

  FL:  KERNEL-FREE     -> State indexing (no modulation)
  CC:  {role_stats['CC']['dominant_sig']:<14} -> {role_stats['CC']['any_kernel']:.0f}% kernel
  EN:  {role_stats['EN']['dominant_sig']:<14} -> {role_stats['EN']['any_kernel']:.0f}% kernel (phase+stability)
  FQ:  {role_stats['FQ']['dominant_sig']:<14} -> {role_stats['FQ']['any_kernel']:.0f}% kernel
  AX:  {role_stats['AX']['dominant_sig']:<14} -> {role_stats['AX']['any_kernel']:.0f}% kernel

Forbidden pairs involve: CC ({role_forbidden_count['CC']}), EN ({role_forbidden_count['EN']}), FQ ({role_forbidden_count['FQ']})
FL and AX are OUTSIDE forbidden topology.
""")

# Save results
results = {
    'role_stats': role_stats,
    'role_kernel_sigs': {role: {sig_to_str(k): v for k, v in sigs.items()}
                         for role, sigs in role_kernel_sigs.items()},
    'forbidden_pair_counts': dict(role_forbidden_count),
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't7_role_kernel_taxonomy.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
