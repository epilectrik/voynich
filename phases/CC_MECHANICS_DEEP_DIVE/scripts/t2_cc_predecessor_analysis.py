"""
T2: CC Predecessor Analysis

What comes BEFORE CC tokens?
Is there a pattern in what precedes classes 10,11 vs 17?
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
CC_GROUP_A = {10, 11}  # 0% kernel, source-only
CC_GROUP_B = {12, 17}  # High kernel, target

print("="*70)
print("CC PREDECESSOR ANALYSIS")
print("="*70)

# Build line data
lines_data = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    m = morph.extract(w)

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
        'middle': m.middle
    })

# ============================================================
# WHAT PRECEDES CC CLASSES?
# ============================================================
print("\n" + "="*70)
print("PREDECESSOR ROLE BY CC CLASS")
print("="*70)

pred_role_by_cc = {cls: Counter() for cls in CC_CLASSES}
pred_class_by_cc = {cls: Counter() for cls in CC_CLASSES}
cc_line_initial = {cls: 0 for cls in CC_CLASSES}
cc_total = {cls: 0 for cls in CC_CLASSES}

for key, tokens in lines_data.items():
    for i, tok in enumerate(tokens):
        if tok['class'] in CC_CLASSES:
            cc_cls = tok['class']
            cc_total[cc_cls] += 1

            if i == 0:
                cc_line_initial[cc_cls] += 1
                pred_role_by_cc[cc_cls]['LINE_START'] += 1
            else:
                pred = tokens[i-1]
                pred_role_by_cc[cc_cls][pred['role']] += 1
                if pred['class']:
                    pred_class_by_cc[cc_cls][pred['class']] += 1

for cls in CC_CLASSES:
    total = cc_total[cls]
    if total == 0:
        print(f"\nClass {cls}: No occurrences")
        continue

    print(f"\nClass {cls} (n={total}):")
    print(f"  Line-initial: {cc_line_initial[cls]} ({100*cc_line_initial[cls]/total:.1f}%)")
    print(f"  Predecessor roles:")
    for role, count in pred_role_by_cc[cls].most_common():
        print(f"    {role}: {count} ({100*count/total:.1f}%)")

# ============================================================
# CC GROUP A vs GROUP B PREDECESSORS
# ============================================================
print("\n" + "="*70)
print("CC GROUP A (10,11) vs GROUP B (12,17) PREDECESSORS")
print("="*70)

group_a_pred = Counter()
group_b_pred = Counter()
group_a_total = 0
group_b_total = 0

for cls in CC_GROUP_A:
    group_a_pred.update(pred_role_by_cc[cls])
    group_a_total += cc_total[cls]

for cls in CC_GROUP_B:
    group_b_pred.update(pred_role_by_cc[cls])
    group_b_total += cc_total[cls]

print(f"\nGroup A (classes 10,11) - n={group_a_total}:")
for role, count in group_a_pred.most_common():
    print(f"  {role}: {count} ({100*count/group_a_total:.1f}%)")

print(f"\nGroup B (classes 12,17) - n={group_b_total}:")
if group_b_total > 0:
    for role, count in group_b_pred.most_common():
        print(f"  {role}: {count} ({100*count/group_b_total:.1f}%)")
else:
    print("  No occurrences")

# ============================================================
# SPECIFIC PREDECESSOR CLASSES
# ============================================================
print("\n" + "="*70)
print("SPECIFIC PREDECESSOR CLASSES (TOP 10)")
print("="*70)

for cls in CC_CLASSES:
    if not pred_class_by_cc[cls]:
        continue
    print(f"\nClass {cls} preceded by:")
    for pred_cls, count in pred_class_by_cc[cls].most_common(10):
        pred_role = ROLE_MAP.get(pred_cls, 'UNK')
        print(f"  Class {pred_cls} ({pred_role}): {count}")

# ============================================================
# EN -> CC ANALYSIS (forbidden pair context)
# ============================================================
print("\n" + "="*70)
print("EN -> CC TRANSITIONS (forbidden pair context)")
print("="*70)

# EN classes that have forbidden -> CC: 31, 32
# They're forbidden to go to 12, 17 (Group B)

en_to_cc = defaultdict(Counter)
for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'EN' and tokens[i+1]['role'] == 'CC':
            en_cls = tokens[i]['class']
            cc_cls = tokens[i+1]['class']
            en_to_cc[en_cls][cc_cls] += 1

print("\nEN class -> CC class transitions:")
for en_cls in sorted(en_to_cc.keys()):
    print(f"  EN class {en_cls}:")
    for cc_cls, count in en_to_cc[en_cls].most_common():
        forbidden = (en_cls in {31, 32} and cc_cls in {12, 17})
        marker = " [FORBIDDEN]" if forbidden else ""
        print(f"    -> CC class {cc_cls}: {count}{marker}")

# ============================================================
# CC -> CC ANALYSIS (internal transitions)
# ============================================================
print("\n" + "="*70)
print("CC -> CC TRANSITIONS (internal)")
print("="*70)

cc_to_cc = defaultdict(Counter)
for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'CC' and tokens[i+1]['role'] == 'CC':
            cc1 = tokens[i]['class']
            cc2 = tokens[i+1]['class']
            cc_to_cc[cc1][cc2] += 1

# Forbidden CC->CC: 10->12, 10->17, 11->12, 11->17
forbidden_cc_cc = {(10, 12), (10, 17), (11, 12), (11, 17)}

print("\nCC class -> CC class transitions:")
for cc1 in sorted(cc_to_cc.keys()):
    print(f"  CC class {cc1}:")
    for cc2, count in cc_to_cc[cc1].most_common():
        forbidden = (cc1, cc2) in forbidden_cc_cc
        marker = " [FORBIDDEN]" if forbidden else ""
        print(f"    -> CC class {cc2}: {count}{marker}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Group A predecessor pattern
if group_a_total > 0:
    en_to_a = group_a_pred.get('EN', 0)
    en_pct_a = 100 * en_to_a / group_a_total
    findings.append(f"GROUP_A_EN_PREDECESSOR: {en_pct_a:.1f}% of Group A (10,11) preceded by EN")

# Group B predecessor pattern
if group_b_total > 0:
    en_to_b = group_b_pred.get('EN', 0)
    en_pct_b = 100 * en_to_b / group_b_total
    findings.append(f"GROUP_B_EN_PREDECESSOR: {en_pct_b:.1f}% of Group B (12,17) preceded by EN")

# Line-initial rates
if group_a_total > 0:
    line_init_a = sum(cc_line_initial[c] for c in CC_GROUP_A)
    findings.append(f"GROUP_A_LINE_INITIAL: {100*line_init_a/group_a_total:.1f}%")

if group_b_total > 0:
    line_init_b = sum(cc_line_initial[c] for c in CC_GROUP_B)
    findings.append(f"GROUP_B_LINE_INITIAL: {100*line_init_b/group_b_total:.1f}%")

# Forbidden transition violations
total_forbidden = sum(cc_to_cc[c1][c2] for c1, c2 in forbidden_cc_cc)
if total_forbidden == 0:
    findings.append("NO_FORBIDDEN_CC_CC: All CC->CC forbidden pairs show 0 transitions")
else:
    findings.append(f"FORBIDDEN_CC_CC_OBSERVED: {total_forbidden} transitions violate CC->CC forbidden pairs")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Save results
results = {
    'pred_role_by_cc': {cls: dict(pred_role_by_cc[cls]) for cls in CC_CLASSES},
    'pred_class_by_cc': {cls: dict(pred_class_by_cc[cls].most_common(20)) for cls in CC_CLASSES},
    'group_a_predecessors': dict(group_a_pred),
    'group_b_predecessors': dict(group_b_pred),
    'cc_line_initial': cc_line_initial,
    'cc_total': cc_total,
    'en_to_cc': {k: dict(v) for k, v in en_to_cc.items()},
    'cc_to_cc': {k: dict(v) for k, v in cc_to_cc.items()},
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CC_MECHANICS_DEEP_DIVE' / 'results' / 't2_cc_predecessor_analysis.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
