"""
T4: FL Hazard Relationship Analysis

Deeper investigation of FL's role in the hazard system:
1. Does hazard FL trigger forbidden transitions?
2. What classes surround hazard FL vs safe FL?
3. FL -> FQ transition (16%) - escape route?
4. How does FL relate to the 17 forbidden pairs?
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

FL_CLASSES = {7, 30, 38, 40}
FL_HAZARD = {7, 30}
FL_SAFE = {38, 40}

# FQ classes for escape analysis
FQ_CLASSES = {9, 13, 14, 23}

# Load hazard topology from BCSC/existing data
# 17 forbidden transitions, 5 hazard failure classes
FORBIDDEN_PAIRS = [
    (12, 23), (12, 9), (17, 23), (17, 9),
    (10, 12), (10, 17), (11, 12), (11, 17),
    (10, 23), (10, 9), (11, 23), (11, 9),
    (32, 12), (32, 17), (31, 12), (31, 17),
    (23, 9)
]
FORBIDDEN_SET = set(FORBIDDEN_PAIRS)

print("="*70)
print("FL HAZARD RELATIONSHIP ANALYSIS")
print("="*70)

# Build per-line token sequences
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

    lines_data[key].append({
        'word': w,
        'class': cls,
        'role': role,
        'folio': token.folio,
        'line': token.line
    })

print(f"Total lines: {len(lines_data)}")

# ============================================================
# FL AND FORBIDDEN TRANSITIONS
# ============================================================
print("\n" + "="*70)
print("FL INVOLVEMENT IN FORBIDDEN TRANSITIONS")
print("="*70)

# Check if FL classes appear in forbidden pairs
fl_in_forbidden = []
for pair in FORBIDDEN_PAIRS:
    if pair[0] in FL_CLASSES or pair[1] in FL_CLASSES:
        fl_in_forbidden.append(pair)

print(f"\nForbidden pairs involving FL classes: {len(fl_in_forbidden)}")
for pair in fl_in_forbidden:
    c1_role = ROLE_MAP.get(pair[0], 'UNK')
    c2_role = ROLE_MAP.get(pair[1], 'UNK')
    print(f"  {pair[0]} ({c1_role}) -> {pair[1]} ({c2_role})")

if not fl_in_forbidden:
    print("  NONE - FL is not in any forbidden transition pair")

# ============================================================
# FL-ADJACENT CLASS ANALYSIS (HAZARD vs SAFE)
# ============================================================
print("\n" + "="*70)
print("CLASSES ADJACENT TO FL (HAZARD vs SAFE)")
print("="*70)

# Track what comes before/after hazard FL vs safe FL
before_hazard_fl = Counter()
after_hazard_fl = Counter()
before_safe_fl = Counter()
after_safe_fl = Counter()

for key, tokens in lines_data.items():
    for i, t in enumerate(tokens):
        if t['class'] in FL_HAZARD:
            if i > 0 and tokens[i-1]['class']:
                before_hazard_fl[tokens[i-1]['class']] += 1
            if i < len(tokens) - 1 and tokens[i+1]['class']:
                after_hazard_fl[tokens[i+1]['class']] += 1
        elif t['class'] in FL_SAFE:
            if i > 0 and tokens[i-1]['class']:
                before_safe_fl[tokens[i-1]['class']] += 1
            if i < len(tokens) - 1 and tokens[i+1]['class']:
                after_safe_fl[tokens[i+1]['class']] += 1

print("\nClasses BEFORE Hazard FL (top 10):")
total_before_h = sum(before_hazard_fl.values())
for cls, count in before_hazard_fl.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    pct = 100 * count / total_before_h if total_before_h else 0
    print(f"  Class {cls} ({role}): {count} ({pct:.1f}%)")

print("\nClasses AFTER Hazard FL (top 10):")
total_after_h = sum(after_hazard_fl.values())
for cls, count in after_hazard_fl.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    pct = 100 * count / total_after_h if total_after_h else 0
    print(f"  Class {cls} ({role}): {count} ({pct:.1f}%)")

print("\nClasses BEFORE Safe FL (top 10):")
total_before_s = sum(before_safe_fl.values())
for cls, count in before_safe_fl.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    pct = 100 * count / total_before_s if total_before_s else 0
    print(f"  Class {cls} ({role}): {count} ({pct:.1f}%)")

print("\nClasses AFTER Safe FL (top 10):")
total_after_s = sum(after_safe_fl.values())
for cls, count in after_safe_fl.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    pct = 100 * count / total_after_s if total_after_s else 0
    print(f"  Class {cls} ({role}): {count} ({pct:.1f}%)")

# ============================================================
# FL -> FQ TRANSITION ANALYSIS
# ============================================================
print("\n" + "="*70)
print("FL -> FQ TRANSITION ANALYSIS")
print("="*70)

# FL -> FQ is 16% - is this escape-related?
fl_to_fq_count = 0
fl_to_other_count = 0
fl_to_fq_by_fl_class = Counter()
fl_to_fq_target_class = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['class'] in FL_CLASSES:
            if tokens[i+1]['class'] in FQ_CLASSES:
                fl_to_fq_count += 1
                fl_to_fq_by_fl_class[tokens[i]['class']] += 1
                fl_to_fq_target_class[tokens[i+1]['class']] += 1
            elif tokens[i+1]['class']:
                fl_to_other_count += 1

total_fl_trans = fl_to_fq_count + fl_to_other_count
fl_fq_rate = 100 * fl_to_fq_count / total_fl_trans if total_fl_trans else 0

print(f"\nFL -> FQ transitions: {fl_to_fq_count} ({fl_fq_rate:.1f}%)")
print(f"FL -> other: {fl_to_other_count}")

print("\nFL -> FQ by FL class:")
for cls in sorted(FL_CLASSES):
    count = fl_to_fq_by_fl_class.get(cls, 0)
    status = "HAZARD" if cls in FL_HAZARD else "SAFE"
    print(f"  Class {cls} ({status}): {count}")

print("\nFL -> FQ by target FQ class:")
for cls in sorted(FQ_CLASSES):
    count = fl_to_fq_target_class.get(cls, 0)
    print(f"  Class {cls}: {count}")

# ============================================================
# HAZARD FL CLASS-PAIR ANALYSIS
# ============================================================
print("\n" + "="*70)
print("HAZARD FL CLASS-PAIR TRANSITIONS")
print("="*70)

# What class pairs involve hazard FL?
hazard_fl_pairs = Counter()
safe_fl_pairs = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        c1 = tokens[i]['class']
        c2 = tokens[i+1]['class']
        if c1 is None or c2 is None:
            continue

        if c1 in FL_HAZARD or c2 in FL_HAZARD:
            hazard_fl_pairs[(c1, c2)] += 1
        if c1 in FL_SAFE or c2 in FL_SAFE:
            safe_fl_pairs[(c1, c2)] += 1

print("\nMost common hazard FL transitions:")
for pair, count in hazard_fl_pairs.most_common(15):
    c1_role = ROLE_MAP.get(pair[0], 'UNK')
    c2_role = ROLE_MAP.get(pair[1], 'UNK')
    is_forbidden = pair in FORBIDDEN_SET
    forbidden_mark = " [FORBIDDEN]" if is_forbidden else ""
    print(f"  {pair[0]} ({c1_role}) -> {pair[1]} ({c2_role}): {count}{forbidden_mark}")

print("\nMost common safe FL transitions:")
for pair, count in safe_fl_pairs.most_common(15):
    c1_role = ROLE_MAP.get(pair[0], 'UNK')
    c2_role = ROLE_MAP.get(pair[1], 'UNK')
    is_forbidden = pair in FORBIDDEN_SET
    forbidden_mark = " [FORBIDDEN]" if is_forbidden else ""
    print(f"  {pair[0]} ({c1_role}) -> {pair[1]} ({c2_role}): {count}{forbidden_mark}")

# ============================================================
# FL ROLE IN RECOVERY SEQUENCES
# ============================================================
print("\n" + "="*70)
print("FL IN RECOVERY SEQUENCES")
print("="*70)

# Look for patterns: X -> FL -> Y where Y might be recovery
# Per C105, e is stability anchor for 54.7% of recovery paths

# Count what happens AFTER FL
post_fl_roles = Counter()
post_fl_has_kernel = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['class'] in FL_CLASSES:
            next_word = tokens[i+1]['word']
            next_role = tokens[i+1]['role']
            post_fl_roles[next_role] += 1

            # Check if next token has kernel char
            if next_word:
                has_k = 'k' in next_word
                has_h = 'h' in next_word
                has_e = 'e' in next_word
                if has_k or has_h or has_e:
                    post_fl_has_kernel['HAS_KERNEL'] += 1
                else:
                    post_fl_has_kernel['NO_KERNEL'] += 1

total_post = sum(post_fl_roles.values())
print("\nRole distribution AFTER FL:")
for role, count in post_fl_roles.most_common():
    pct = 100 * count / total_post if total_post else 0
    print(f"  {role}: {count} ({pct:.1f}%)")

total_kernel = sum(post_fl_has_kernel.values())
kernel_rate = 100 * post_fl_has_kernel.get('HAS_KERNEL', 0) / total_kernel if total_kernel else 0
print(f"\nPost-FL tokens with kernel chars: {kernel_rate:.1f}%")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# FL in forbidden pairs
if not fl_in_forbidden:
    findings.append("FL_OUTSIDE_FORBIDDEN: FL classes not in any of 17 forbidden pairs")

# FL -> FQ relationship
if fl_fq_rate > 10:
    # Check if hazard or safe FL drives FQ transition
    hazard_fq = sum(fl_to_fq_by_fl_class.get(c, 0) for c in FL_HAZARD)
    safe_fq = sum(fl_to_fq_by_fl_class.get(c, 0) for c in FL_SAFE)
    if hazard_fq > safe_fq * 2:
        findings.append(f"HAZARD_FL_FQ_DRIVER: Hazard FL drives {100*hazard_fq/(hazard_fq+safe_fq):.0f}% of FL->FQ")
    else:
        findings.append(f"FL_FQ_BALANCED: Both hazard and safe FL feed FQ ({hazard_fq} vs {safe_fq})")

# Post-FL kernel rate
if kernel_rate > 40:
    findings.append(f"POST_FL_KERNEL_ENRICHED: {kernel_rate:.1f}% of post-FL tokens have kernel chars")
elif kernel_rate < 20:
    findings.append(f"POST_FL_KERNEL_DEPLETED: Only {kernel_rate:.1f}% of post-FL tokens have kernel")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

FL HAZARD ANALYSIS SUMMARY:
- FL classes (7, 30, 38, 40) are NOT in any forbidden transition pair
- FL operates BELOW the hazard layer (hazard is class-class, not role-role)
- FL -> FQ rate: {fl_fq_rate:.1f}% (FQ = Frequency/escape role)
- Post-FL kernel rate: {kernel_rate:.1f}%

FL is primitive substrate that:
1. Doesn't trigger forbidden transitions directly
2. Feeds into FQ (escape routes) at {fl_fq_rate:.1f}% rate
3. Is followed by kernel-enriched tokens at {kernel_rate:.1f}% rate

FL provides material flow; hazard topology operates on class transitions AFTER FL.
""")

# Save results
results = {
    'fl_in_forbidden_pairs': len(fl_in_forbidden),
    'fl_to_fq_rate': fl_fq_rate,
    'fl_to_fq_by_class': dict(fl_to_fq_by_fl_class),
    'post_fl_roles': dict(post_fl_roles),
    'post_fl_kernel_rate': kernel_rate,
    'hazard_fl_top_pairs': [(list(p), c) for p, c in hazard_fl_pairs.most_common(10)],
    'safe_fl_top_pairs': [(list(p), c) for p, c in safe_fl_pairs.most_common(10)],
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't4_fl_hazard_relationship.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
