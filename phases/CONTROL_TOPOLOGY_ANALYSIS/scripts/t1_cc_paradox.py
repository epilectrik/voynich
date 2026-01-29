"""
T1: CC Paradox Analysis

CC is only 25% kernel BUT dominates forbidden pairs (20 appearances).
All 4 CC classes (10, 11, 12, 17) are in forbidden pairs.

Questions:
1. Why does a low-kernel role control hazard topology?
2. What distinguishes CC classes from each other?
3. Is CC's power about class transitions, not kernel content?
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

CC_CLASSES = [10, 11, 12, 17]

FORBIDDEN_PAIRS = [
    (12, 23), (12, 9), (17, 23), (17, 9),
    (10, 12), (10, 17), (11, 12), (11, 17),
    (10, 23), (10, 9), (11, 23), (11, 9),
    (32, 12), (32, 17), (31, 12), (31, 17),
    (23, 9)
]

def get_kernel_signature(word):
    has_k = 'k' in word
    has_h = 'h' in word
    has_e = 'e' in word
    sig = []
    if has_k: sig.append('k')
    if has_h: sig.append('h')
    if has_e: sig.append('e')
    return tuple(sig) if sig else ('none',)

print("="*70)
print("CC PARADOX ANALYSIS")
print("="*70)

# ============================================================
# CC CLASS PROFILES
# ============================================================
print("\n" + "="*70)
print("CC CLASS INDIVIDUAL PROFILES")
print("="*70)

# Collect CC tokens by class
cc_class_tokens = defaultdict(list)
cc_class_kernel = defaultdict(Counter)
cc_class_middles = defaultdict(Counter)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    if w in token_to_class:
        cls = int(token_to_class[w])
        if cls in CC_CLASSES:
            m = morph.extract(w)
            cc_class_tokens[cls].append(w)
            cc_class_kernel[cls][get_kernel_signature(w)] += 1
            if m.middle:
                cc_class_middles[cls][m.middle] += 1

print("\nCC class breakdown:")
for cls in CC_CLASSES:
    tokens = cc_class_tokens[cls]
    total = len(tokens)
    kernel_sigs = cc_class_kernel[cls]

    has_kernel = total - kernel_sigs.get(('none',), 0)
    kernel_rate = 100 * has_kernel / total if total else 0

    # Count forbidden pair involvement
    fp_count = sum(1 for p in FORBIDDEN_PAIRS if cls in p)

    print(f"\n  Class {cls}:")
    print(f"    Tokens: {total}")
    print(f"    Kernel rate: {kernel_rate:.1f}%")
    print(f"    Forbidden pairs: {fp_count}")
    print(f"    Top MIDDLEs: {cc_class_middles[cls].most_common(5)}")
    print(f"    Kernel sigs: {dict(kernel_sigs)}")

# ============================================================
# CC IN FORBIDDEN PAIRS - DIRECTIONALITY
# ============================================================
print("\n" + "="*70)
print("CC FORBIDDEN PAIR DIRECTIONALITY")
print("="*70)

# Analyze which CC classes are sources vs targets
cc_as_source = Counter()
cc_as_target = Counter()

for c1, c2 in FORBIDDEN_PAIRS:
    if c1 in CC_CLASSES:
        cc_as_source[c1] += 1
    if c2 in CC_CLASSES:
        cc_as_target[c2] += 1

print("\nCC classes as SOURCE (first in pair):")
for cls in CC_CLASSES:
    print(f"  Class {cls}: {cc_as_source.get(cls, 0)} times")

print("\nCC classes as TARGET (second in pair):")
for cls in CC_CLASSES:
    print(f"  Class {cls}: {cc_as_target.get(cls, 0)} times")

# ============================================================
# CC TRANSITION PARTNERS
# ============================================================
print("\n" + "="*70)
print("CC FORBIDDEN TRANSITION PARTNERS")
print("="*70)

# What classes are forbidden before/after CC?
forbidden_before_cc = Counter()  # X -> CC is forbidden
forbidden_after_cc = Counter()   # CC -> X is forbidden

for c1, c2 in FORBIDDEN_PAIRS:
    if c2 in CC_CLASSES:
        forbidden_before_cc[c1] += 1
    if c1 in CC_CLASSES:
        forbidden_after_cc[c2] += 1

print("\nClasses that CANNOT precede CC (X -> CC forbidden):")
for cls, count in forbidden_before_cc.most_common():
    role = ROLE_MAP.get(cls, 'UNK')
    print(f"  Class {cls} ({role}): {count} forbidden pairs")

print("\nClasses that CANNOT follow CC (CC -> X forbidden):")
for cls, count in forbidden_after_cc.most_common():
    role = ROLE_MAP.get(cls, 'UNK')
    print(f"  Class {cls} ({role}): {count} forbidden pairs")

# ============================================================
# CC POSITIONAL PROFILE
# ============================================================
print("\n" + "="*70)
print("CC POSITIONAL PROFILE")
print("="*70)

# Build line data
lines_data = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    if w in token_to_class:
        cls = int(token_to_class[w])
        role = ROLE_MAP.get(cls, 'UNK')
    else:
        cls = None
        role = 'UN'
    lines_data[key].append({'word': w, 'class': cls, 'role': role})

# CC position in lines
cc_positions = defaultdict(list)
for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['class'] in CC_CLASSES:
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            cc_positions[t['class']].append(norm_pos)

print("\nCC class mean positions:")
for cls in CC_CLASSES:
    positions = cc_positions[cls]
    if positions:
        mean_pos = sum(positions) / len(positions)
        print(f"  Class {cls}: mean pos {mean_pos:.3f} (n={len(positions)})")

# ============================================================
# CC ACTUAL TRANSITIONS (observed, not forbidden)
# ============================================================
print("\n" + "="*70)
print("CC ACTUAL TRANSITIONS (OBSERVED)")
print("="*70)

cc_preceded_by = Counter()
cc_followed_by = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens)):
        if tokens[i]['class'] in CC_CLASSES:
            if i > 0 and tokens[i-1]['class']:
                cc_preceded_by[(tokens[i-1]['class'], tokens[i]['class'])] += 1
            if i < len(tokens) - 1 and tokens[i+1]['class']:
                cc_followed_by[(tokens[i]['class'], tokens[i+1]['class'])] += 1

print("\nMost common X -> CC transitions:")
for (c1, c2), count in cc_preceded_by.most_common(10):
    r1 = ROLE_MAP.get(c1, 'UNK')
    is_forbidden = (c1, c2) in FORBIDDEN_PAIRS
    mark = " [FORBIDDEN!]" if is_forbidden else ""
    print(f"  {c1} ({r1}) -> {c2} (CC): {count}{mark}")

print("\nMost common CC -> X transitions:")
for (c1, c2), count in cc_followed_by.most_common(10):
    r2 = ROLE_MAP.get(c2, 'UNK')
    is_forbidden = (c1, c2) in FORBIDDEN_PAIRS
    mark = " [FORBIDDEN!]" if is_forbidden else ""
    print(f"  {c1} (CC) -> {c2} ({r2}): {count}{mark}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Kernel rate by class
kernel_rates = {}
for cls in CC_CLASSES:
    total = len(cc_class_tokens[cls])
    has_kernel = total - cc_class_kernel[cls].get(('none',), 0)
    kernel_rates[cls] = 100 * has_kernel / total if total else 0

high_kernel_cc = [cls for cls, rate in kernel_rates.items() if rate > 50]
low_kernel_cc = [cls for cls, rate in kernel_rates.items() if rate < 30]

if low_kernel_cc:
    findings.append(f"CC_LOW_KERNEL: Classes {low_kernel_cc} are <30% kernel")

# Source vs target asymmetry
total_source = sum(cc_as_source.values())
total_target = sum(cc_as_target.values())
if total_source > total_target * 2:
    findings.append(f"CC_SOURCE_HEAVY: CC is source {total_source}x vs target {total_target}x in forbidden pairs")
elif total_target > total_source * 2:
    findings.append(f"CC_TARGET_HEAVY: CC is target {total_target}x vs source {total_source}x in forbidden pairs")

# FQ as forbidden partner
fq_forbidden = forbidden_after_cc.get(9, 0) + forbidden_after_cc.get(23, 0)
if fq_forbidden >= 4:
    findings.append(f"CC_FQ_FORBIDDEN: CC -> FQ is heavily restricted ({fq_forbidden} pairs)")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

CC PARADOX RESOLUTION:

CC's 25% kernel rate masks class-level variation:
  Class 10: {kernel_rates.get(10, 0):.1f}% kernel
  Class 11: {kernel_rates.get(11, 0):.1f}% kernel
  Class 12: {kernel_rates.get(12, 0):.1f}% kernel
  Class 17: {kernel_rates.get(17, 0):.1f}% kernel

CC dominates forbidden pairs because:
  - CC is GATEKEEPER, not executor
  - Low kernel = CC doesn't transform, it CONTROLS transitions
  - Forbidden pairs prevent bad CC->X and X->CC sequences

CC operates on CLASS LOGIC, not kernel modulation.
""")

# Save results
results = {
    'cc_class_tokens': {cls: len(tokens) for cls, tokens in cc_class_tokens.items()},
    'cc_class_kernel_rates': kernel_rates,
    'cc_as_source': dict(cc_as_source),
    'cc_as_target': dict(cc_as_target),
    'forbidden_before_cc': dict(forbidden_before_cc),
    'forbidden_after_cc': dict(forbidden_after_cc),
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CONTROL_TOPOLOGY_ANALYSIS' / 'results' / 't1_cc_paradox.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
