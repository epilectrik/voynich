"""
T3: CC Successor Analysis

What comes AFTER CC tokens?
Why is CC->FQ heavily forbidden (8 pairs)?
What does CC actually route to?
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
CC_GROUP_A = {10, 11}
CC_GROUP_B = {12, 17}
FQ_CLASSES = {9, 13, 14, 23}

print("="*70)
print("CC SUCCESSOR ANALYSIS")
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
# WHAT FOLLOWS CC CLASSES?
# ============================================================
print("\n" + "="*70)
print("SUCCESSOR ROLE BY CC CLASS")
print("="*70)

succ_role_by_cc = {cls: Counter() for cls in CC_CLASSES}
succ_class_by_cc = {cls: Counter() for cls in CC_CLASSES}
cc_line_final = {cls: 0 for cls in CC_CLASSES}
cc_total = {cls: 0 for cls in CC_CLASSES}

for key, tokens in lines_data.items():
    for i, tok in enumerate(tokens):
        if tok['class'] in CC_CLASSES:
            cc_cls = tok['class']
            cc_total[cc_cls] += 1

            if i == len(tokens) - 1:
                cc_line_final[cc_cls] += 1
                succ_role_by_cc[cc_cls]['LINE_END'] += 1
            else:
                succ = tokens[i+1]
                succ_role_by_cc[cc_cls][succ['role']] += 1
                if succ['class']:
                    succ_class_by_cc[cc_cls][succ['class']] += 1

for cls in CC_CLASSES:
    total = cc_total[cls]
    if total == 0:
        print(f"\nClass {cls}: No occurrences")
        continue

    print(f"\nClass {cls} (n={total}):")
    print(f"  Line-final: {cc_line_final[cls]} ({100*cc_line_final[cls]/total:.1f}%)")
    print(f"  Successor roles:")
    for role, count in succ_role_by_cc[cls].most_common():
        print(f"    {role}: {count} ({100*count/total:.1f}%)")

# ============================================================
# CC GROUP A vs GROUP B SUCCESSORS
# ============================================================
print("\n" + "="*70)
print("CC GROUP A (10,11) vs GROUP B (12,17) SUCCESSORS")
print("="*70)

group_a_succ = Counter()
group_b_succ = Counter()
group_a_total = 0
group_b_total = 0

for cls in CC_GROUP_A:
    group_a_succ.update(succ_role_by_cc[cls])
    group_a_total += cc_total[cls]

for cls in CC_GROUP_B:
    group_b_succ.update(succ_role_by_cc[cls])
    group_b_total += cc_total[cls]

print(f"\nGroup A (classes 10,11) - n={group_a_total}:")
for role, count in group_a_succ.most_common():
    print(f"  {role}: {count} ({100*count/group_a_total:.1f}%)")

print(f"\nGroup B (classes 12,17) - n={group_b_total}:")
if group_b_total > 0:
    for role, count in group_b_succ.most_common():
        print(f"  {role}: {count} ({100*count/group_b_total:.1f}%)")
else:
    print("  No occurrences")

# ============================================================
# CC -> FQ ANALYSIS (forbidden pair context)
# ============================================================
print("\n" + "="*70)
print("CC -> FQ TRANSITIONS (8 forbidden pairs)")
print("="*70)

# Forbidden CC->FQ: all combinations of CC(10,11,12,17) -> FQ(9,23)
# But from t2 data: (12,23), (12,9), (17,23), (17,9), (10,23), (10,9), (11,23), (11,9)
forbidden_cc_fq = {
    (10, 9), (10, 23), (11, 9), (11, 23),
    (12, 9), (12, 23), (17, 9), (17, 23)
}

cc_to_fq = defaultdict(Counter)
for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'CC' and tokens[i+1]['role'] == 'FQ':
            cc_cls = tokens[i]['class']
            fq_cls = tokens[i+1]['class']
            cc_to_fq[cc_cls][fq_cls] += 1

print("\nCC class -> FQ class transitions:")
for cc_cls in CC_CLASSES:
    if cc_cls not in cc_to_fq:
        print(f"  CC class {cc_cls}: No FQ transitions")
        continue
    print(f"  CC class {cc_cls}:")
    for fq_cls, count in cc_to_fq[cc_cls].most_common():
        forbidden = (cc_cls, fq_cls) in forbidden_cc_fq
        marker = " [FORBIDDEN]" if forbidden else ""
        print(f"    -> FQ class {fq_cls}: {count}{marker}")

# Total CC->FQ transitions
total_cc_fq = sum(sum(v.values()) for v in cc_to_fq.values())
forbidden_cc_fq_count = sum(
    cc_to_fq[cc][fq] for cc, fq in forbidden_cc_fq if cc in cc_to_fq
)
print(f"\nTotal CC->FQ transitions: {total_cc_fq}")
print(f"Of which forbidden: {forbidden_cc_fq_count}")

# ============================================================
# CC -> FL ANALYSIS (escape to FL?)
# ============================================================
print("\n" + "="*70)
print("CC -> FL TRANSITIONS")
print("="*70)

cc_to_fl = defaultdict(Counter)
cc_to_fl_state = defaultdict(Counter)

FL_STATES = {
    'EARLY': {'i', 'ii', 'in'},
    'MEDIAL': {'r', 'ar', 'al', 'l', 'ol'},
    'LATE': {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}
}

def get_fl_state(middle):
    if middle in FL_STATES['EARLY']:
        return 'EARLY'
    elif middle in FL_STATES['MEDIAL']:
        return 'MEDIAL'
    elif middle in FL_STATES['LATE']:
        return 'LATE'
    return 'OTHER'

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'CC' and tokens[i+1]['role'] == 'FL':
            cc_cls = tokens[i]['class']
            fl_middle = tokens[i+1]['middle']
            fl_state = get_fl_state(fl_middle)
            cc_to_fl[cc_cls][tokens[i+1]['class']] += 1
            cc_to_fl_state[cc_cls][fl_state] += 1

print("\nCC -> FL by CC class:")
for cc_cls in CC_CLASSES:
    if cc_cls not in cc_to_fl:
        print(f"  CC class {cc_cls}: No FL transitions")
        continue
    total = sum(cc_to_fl[cc_cls].values())
    print(f"  CC class {cc_cls}: {total} FL transitions")
    print(f"    FL states: {dict(cc_to_fl_state[cc_cls])}")

# ============================================================
# CC -> EN ANALYSIS
# ============================================================
print("\n" + "="*70)
print("CC -> EN TRANSITIONS")
print("="*70)

cc_to_en = defaultdict(Counter)
for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'CC' and tokens[i+1]['role'] == 'EN':
            cc_cls = tokens[i]['class']
            en_cls = tokens[i+1]['class']
            cc_to_en[cc_cls][en_cls] += 1

print("\nCC -> EN transitions:")
for cc_cls in CC_CLASSES:
    if cc_cls not in cc_to_en:
        print(f"  CC class {cc_cls}: No EN transitions")
        continue
    total = sum(cc_to_en[cc_cls].values())
    print(f"  CC class {cc_cls}: {total} EN transitions")
    print(f"    Top EN targets: {cc_to_en[cc_cls].most_common(5)}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# FQ restriction
if group_a_total > 0:
    fq_from_a = group_a_succ.get('FQ', 0)
    fq_pct_a = 100 * fq_from_a / group_a_total
    findings.append(f"GROUP_A_FQ_SUCCESSOR: {fq_pct_a:.1f}% of Group A -> FQ")

if group_b_total > 0:
    fq_from_b = group_b_succ.get('FQ', 0)
    fq_pct_b = 100 * fq_from_b / group_b_total
    findings.append(f"GROUP_B_FQ_SUCCESSOR: {fq_pct_b:.1f}% of Group B -> FQ")

# EN as dominant successor?
if group_a_total > 0:
    en_from_a = group_a_succ.get('EN', 0)
    if en_from_a > fq_from_a:
        findings.append(f"GROUP_A_EN_DOMINANT: EN ({en_from_a}) > FQ ({fq_from_a}) as successor")

# Line-final rates
if group_a_total > 0:
    line_final_a = sum(cc_line_final[c] for c in CC_GROUP_A)
    findings.append(f"GROUP_A_LINE_FINAL: {100*line_final_a/group_a_total:.1f}%")

if group_b_total > 0:
    line_final_b = sum(cc_line_final[c] for c in CC_GROUP_B)
    findings.append(f"GROUP_B_LINE_FINAL: {100*line_final_b/group_b_total:.1f}%")

# Forbidden CC->FQ compliance
if total_cc_fq > 0:
    compliance = 100 * (total_cc_fq - forbidden_cc_fq_count) / total_cc_fq
    if forbidden_cc_fq_count == 0:
        findings.append("CC_FQ_FORBIDDEN_COMPLIANT: Zero forbidden CC->FQ transitions observed")
    else:
        findings.append(f"CC_FQ_FORBIDDEN_VIOLATED: {forbidden_cc_fq_count}/{total_cc_fq} violate forbidden pairs")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Save results
results = {
    'succ_role_by_cc': {cls: dict(succ_role_by_cc[cls]) for cls in CC_CLASSES},
    'succ_class_by_cc': {cls: dict(succ_class_by_cc[cls].most_common(20)) for cls in CC_CLASSES},
    'group_a_successors': dict(group_a_succ),
    'group_b_successors': dict(group_b_succ),
    'cc_line_final': cc_line_final,
    'cc_total': cc_total,
    'cc_to_fq': {k: dict(v) for k, v in cc_to_fq.items()},
    'cc_to_fl': {k: dict(v) for k, v in cc_to_fl.items()},
    'cc_to_fl_state': {k: dict(v) for k, v in cc_to_fl_state.items()},
    'cc_to_en': {k: dict(v) for k, v in cc_to_en.items()},
    'forbidden_cc_fq_count': forbidden_cc_fq_count,
    'total_cc_fq': total_cc_fq,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CC_MECHANICS_DEEP_DIVE' / 'results' / 't3_cc_successor_analysis.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
