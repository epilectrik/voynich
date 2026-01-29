"""
T3: FL as Primitive Substrate

FL uses only 9 characters: a, d, i, l, m, n, o, r, y
FL excludes kernel chars: k, h, e (and c, s, t)

Question: Is FL the "substrate" that other roles modify?
- Do other roles ADD kernel chars to FL-like bases?
- Is FL's character set the "ground state"?
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

# FL character set (from T1)
FL_CHARS = set('adilmnory')
KERNEL_CHARS = set('khe')
EXCLUDED_CHARS = set('cehkst')  # Chars FL doesn't use

print("="*70)
print("FL PRIMITIVE SUBSTRATE ANALYSIS")
print("="*70)

print(f"\nFL characters: {sorted(FL_CHARS)}")
print(f"Kernel characters (k, h, e): {sorted(KERNEL_CHARS)}")
print(f"FL-excluded characters: {sorted(EXCLUDED_CHARS)}")

# Collect MIDDLEs by role
role_middles = defaultdict(set)
role_tokens = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or w not in token_to_class:
        continue

    cls = int(token_to_class[w])
    role = ROLE_MAP.get(cls, 'UNK')
    m = morph.extract(w)

    if m.middle:
        role_middles[role].add(m.middle)
        role_tokens[role].append({
            'word': w,
            'middle': m.middle,
            'class': cls
        })

# ============================================================
# CHARACTER USAGE BY ROLE
# ============================================================
print("\n" + "="*70)
print("CHARACTER USAGE BY ROLE")
print("="*70)

role_char_usage = {}

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    chars = set()
    for mid in role_middles[role]:
        chars.update(mid)
    role_char_usage[role] = chars

    has_kernel = chars & KERNEL_CHARS
    fl_compatible = chars <= FL_CHARS

    print(f"\n{role}:")
    print(f"  Characters: {sorted(chars)}")
    print(f"  Count: {len(chars)}")
    print(f"  Has kernel chars: {sorted(has_kernel) if has_kernel else 'NO'}")
    print(f"  FL-compatible (subset of FL chars): {fl_compatible}")

# ============================================================
# FL-COMPATIBLE MIDDLEs IN OTHER ROLES
# ============================================================
print("\n" + "="*70)
print("FL-COMPATIBLE MIDDLEs IN OTHER ROLES")
print("="*70)

print("\nMIDDLEs that use ONLY FL characters (no k, h, e, c, s, t):")

for role in ['CC', 'EN', 'FQ', 'AX']:
    fl_compat_middles = []
    for mid in role_middles[role]:
        mid_chars = set(mid)
        if mid_chars <= FL_CHARS:
            fl_compat_middles.append(mid)

    compat_rate = 100 * len(fl_compat_middles) / len(role_middles[role]) if role_middles[role] else 0
    print(f"\n{role}: {len(fl_compat_middles)}/{len(role_middles[role])} MIDDLEs are FL-compatible ({compat_rate:.1f}%)")
    if fl_compat_middles:
        print(f"  FL-compatible: {sorted(fl_compat_middles)[:15]}{'...' if len(fl_compat_middles) > 15 else ''}")

# ============================================================
# KERNEL CHARACTER DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("KERNEL CHARACTER DISTRIBUTION IN MIDDLEs")
print("="*70)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    k_middles = [m for m in role_middles[role] if 'k' in m]
    h_middles = [m for m in role_middles[role] if 'h' in m]
    e_middles = [m for m in role_middles[role] if 'e' in m]
    any_kernel = [m for m in role_middles[role] if any(c in m for c in 'khe')]

    total = len(role_middles[role])
    print(f"\n{role} ({total} MIDDLEs):")
    print(f"  k-containing: {len(k_middles)} ({100*len(k_middles)/total:.1f}%)")
    print(f"  h-containing: {len(h_middles)} ({100*len(h_middles)/total:.1f}%)")
    print(f"  e-containing: {len(e_middles)} ({100*len(e_middles)/total:.1f}%)")
    print(f"  Any kernel: {len(any_kernel)} ({100*len(any_kernel)/total:.1f}%)")

# ============================================================
# FL AS BASE, OTHERS AS MODIFICATION
# ============================================================
print("\n" + "="*70)
print("FL AS SUBSTRATE HYPOTHESIS")
print("="*70)

# Check if other role MIDDLEs can be decomposed into FL chars + kernel chars
fl_base_plus_kernel = defaultdict(list)

for role in ['CC', 'EN', 'FQ', 'AX']:
    for mid in role_middles[role]:
        mid_chars = set(mid)
        fl_part = mid_chars & FL_CHARS
        kernel_part = mid_chars & KERNEL_CHARS
        other_part = mid_chars - FL_CHARS - KERNEL_CHARS

        if kernel_part and fl_part and not other_part:
            # This MIDDLE = FL chars + kernel chars only
            fl_base_plus_kernel[role].append({
                'middle': mid,
                'fl_chars': sorted(fl_part),
                'kernel_chars': sorted(kernel_part)
            })

print("\nMIDDLEs that are FL_CHARS + KERNEL_CHARS only (no c, s, t):")
for role in ['CC', 'EN', 'FQ', 'AX']:
    matches = fl_base_plus_kernel[role]
    total = len(role_middles[role])
    print(f"\n{role}: {len(matches)}/{total} ({100*len(matches)/total:.1f}%)")
    for m in matches[:10]:
        print(f"    '{m['middle']}' = FL{m['fl_chars']} + K{m['kernel_chars']}")

# ============================================================
# 'c', 's', 't' ANALYSIS
# ============================================================
print("\n" + "="*70)
print("c, s, t DISTRIBUTION (FL-excluded, non-kernel)")
print("="*70)

for char in ['c', 's', 't']:
    print(f"\n'{char}' in MIDDLEs by role:")
    for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
        char_middles = [m for m in role_middles[role] if char in m]
        total = len(role_middles[role])
        if char_middles:
            print(f"  {role}: {len(char_middles)}/{total} ({100*len(char_middles)/total:.1f}%)")
            print(f"    Examples: {char_middles[:5]}")
        else:
            print(f"  {role}: 0/{total} (0%)")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

# Calculate FL-compatibility across all non-FL roles
all_other_middles = set()
fl_compatible_middles = set()
for role in ['CC', 'EN', 'FQ', 'AX']:
    all_other_middles.update(role_middles[role])
    for mid in role_middles[role]:
        if set(mid) <= FL_CHARS:
            fl_compatible_middles.add(mid)

overall_fl_compat = 100 * len(fl_compatible_middles) / len(all_other_middles) if all_other_middles else 0

findings = []

# FL exclusivity
if len(role_char_usage['FL'] & KERNEL_CHARS) == 0:
    findings.append("FL_KERNEL_FREE: FL uses 0 kernel characters")

# Other roles use kernel
en_kernel_rate = len([m for m in role_middles['EN'] if any(c in m for c in 'khe')]) / len(role_middles['EN']) * 100
if en_kernel_rate > 30:
    findings.append(f"EN_KERNEL_RICH: EN MIDDLEs are {en_kernel_rate:.1f}% kernel-containing")

# FL-compatible rate in others
if overall_fl_compat < 30:
    findings.append(f"FL_SUBSTRATE_PARTIAL: Only {overall_fl_compat:.1f}% of non-FL MIDDLEs are FL-compatible")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""
SUBSTRATE ANALYSIS:
- FL uses 9 characters: {sorted(FL_CHARS)}
- FL excludes kernel (k, h, e) AND helpers (c, s, t)
- EN is kernel-rich ({en_kernel_rate:.1f}% kernel-containing)
- {overall_fl_compat:.1f}% of non-FL MIDDLEs use only FL characters

FL provides the primitive flow substrate. Other roles add:
- Kernel characters (k, h, e) for energy/phase/stability
- Helper characters (c, s, t) for additional modulation
""")

# Save results
results = {
    'fl_chars': sorted(FL_CHARS),
    'kernel_chars': sorted(KERNEL_CHARS),
    'role_char_usage': {r: sorted(c) for r, c in role_char_usage.items()},
    'fl_compatible_rate': overall_fl_compat,
    'en_kernel_rate': en_kernel_rate,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't3_fl_primitive_substrate.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
