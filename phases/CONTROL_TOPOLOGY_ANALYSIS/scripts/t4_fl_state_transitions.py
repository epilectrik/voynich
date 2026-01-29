"""
T4: FL State Transition Grammar

FL indexes states with positional gradient.
Questions:
1. Are there forbidden FL state transitions?
2. Is FL[y] -> FL[i] (late->early) ever allowed?
3. What's the state machine?
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

FL_CLASSES = {7, 30, 38, 40}

# FL state categories with position order
FL_STATES = {
    'EARLY': {'i', 'ii', 'in'},
    'MEDIAL': {'r', 'ar', 'al', 'l', 'ol'},
    'LATE': {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}
}

STATE_ORDER = {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2, 'OTHER': -1}

def get_fl_stage(middle):
    if middle in FL_STATES['EARLY']:
        return 'EARLY'
    elif middle in FL_STATES['MEDIAL']:
        return 'MEDIAL'
    elif middle in FL_STATES['LATE']:
        return 'LATE'
    return 'OTHER'

print("="*70)
print("FL STATE TRANSITION GRAMMAR")
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
# FL -> FL DIRECT TRANSITIONS
# ============================================================
print("\n" + "="*70)
print("FL -> FL DIRECT STATE TRANSITIONS")
print("="*70)

fl_fl_state_trans = Counter()
fl_fl_middle_trans = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'FL' and tokens[i+1]['role'] == 'FL':
            s1 = get_fl_stage(tokens[i]['middle'])
            s2 = get_fl_stage(tokens[i+1]['middle'])
            fl_fl_state_trans[(s1, s2)] += 1

            m1 = tokens[i]['middle'] or '?'
            m2 = tokens[i+1]['middle'] or '?'
            fl_fl_middle_trans[(m1, m2)] += 1

total_fl_fl = sum(fl_fl_state_trans.values())
print(f"\nTotal FL -> FL transitions: {total_fl_fl}")

print("\nFL state -> FL state transitions:")
for (s1, s2), count in fl_fl_state_trans.most_common():
    pct = 100 * count / total_fl_fl if total_fl_fl else 0
    o1, o2 = STATE_ORDER.get(s1, -1), STATE_ORDER.get(s2, -1)
    if o1 < o2:
        direction = "FORWARD"
    elif o1 == o2:
        direction = "SAME"
    else:
        direction = "BACKWARD"
    print(f"  {s1} -> {s2}: {count} ({pct:.1f}%) [{direction}]")

# ============================================================
# TRANSITION DIRECTION ANALYSIS
# ============================================================
print("\n" + "="*70)
print("TRANSITION DIRECTION ANALYSIS")
print("="*70)

forward = 0
same = 0
backward = 0

for (s1, s2), count in fl_fl_state_trans.items():
    o1, o2 = STATE_ORDER.get(s1, -1), STATE_ORDER.get(s2, -1)
    if o1 < 0 or o2 < 0:
        continue
    if o1 < o2:
        forward += count
    elif o1 == o2:
        same += count
    else:
        backward += count

total_dir = forward + same + backward
print(f"\nDirection breakdown (excluding OTHER):")
print(f"  FORWARD (earlier -> later): {forward} ({100*forward/total_dir:.1f}%)")
print(f"  SAME (stay in stage): {same} ({100*same/total_dir:.1f}%)")
print(f"  BACKWARD (later -> earlier): {backward} ({100*backward/total_dir:.1f}%)")

# ============================================================
# FL ... FL TRANSITIONS (WITH INTERVENING TOKENS)
# ============================================================
print("\n" + "="*70)
print("FL ... FL TRANSITIONS (1-3 TOKENS BETWEEN)")
print("="*70)

# FL transitions with 1-3 tokens in between
fl_gap_trans = defaultdict(Counter)

for key, tokens in lines_data.items():
    fl_indices = [i for i, t in enumerate(tokens) if t['role'] == 'FL']

    for j in range(len(fl_indices) - 1):
        i1, i2 = fl_indices[j], fl_indices[j+1]
        gap = i2 - i1 - 1  # Tokens between

        if 1 <= gap <= 3:
            s1 = get_fl_stage(tokens[i1]['middle'])
            s2 = get_fl_stage(tokens[i2]['middle'])
            fl_gap_trans[gap][(s1, s2)] += 1

for gap in [1, 2, 3]:
    trans = fl_gap_trans[gap]
    total = sum(trans.values())
    if total > 0:
        print(f"\nFL ... ({gap} token gap) ... FL:")
        for (s1, s2), count in trans.most_common(5):
            pct = 100 * count / total
            o1, o2 = STATE_ORDER.get(s1, -1), STATE_ORDER.get(s2, -1)
            direction = "FWD" if o1 < o2 else "SAME" if o1 == o2 else "BACK"
            print(f"  {s1} -> {s2}: {count} ({pct:.1f}%) [{direction}]")

# ============================================================
# RARE/MISSING TRANSITIONS
# ============================================================
print("\n" + "="*70)
print("RARE OR MISSING FL STATE TRANSITIONS")
print("="*70)

# Expected transitions
expected = [
    ('EARLY', 'EARLY'), ('EARLY', 'MEDIAL'), ('EARLY', 'LATE'),
    ('MEDIAL', 'EARLY'), ('MEDIAL', 'MEDIAL'), ('MEDIAL', 'LATE'),
    ('LATE', 'EARLY'), ('LATE', 'MEDIAL'), ('LATE', 'LATE')
]

print("\nAll state transition counts:")
for s1, s2 in expected:
    count = fl_fl_state_trans.get((s1, s2), 0)
    o1, o2 = STATE_ORDER[s1], STATE_ORDER[s2]
    direction = "FWD" if o1 < o2 else "SAME" if o1 == o2 else "BACK"
    status = "RARE" if count < 3 else ""
    print(f"  {s1:6} -> {s2:6}: {count:3} [{direction}] {status}")

# ============================================================
# FL MIDDLE-LEVEL TRANSITIONS
# ============================================================
print("\n" + "="*70)
print("FL MIDDLE-LEVEL TRANSITIONS (TOP 15)")
print("="*70)

print("\nMost common FL MIDDLE -> FL MIDDLE:")
for (m1, m2), count in fl_fl_middle_trans.most_common(15):
    s1 = get_fl_stage(m1)
    s2 = get_fl_stage(m2)
    print(f"  '{m1}' ({s1}) -> '{m2}' ({s2}): {count}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Direction bias
if forward > backward * 2:
    findings.append(f"FORWARD_DOMINANT: {100*forward/total_dir:.0f}% forward vs {100*backward/total_dir:.0f}% backward")
elif backward > forward * 2:
    findings.append(f"BACKWARD_DOMINANT: {100*backward/total_dir:.0f}% backward vs {100*forward/total_dir:.0f}% forward")
else:
    findings.append(f"BIDIRECTIONAL: Forward {100*forward/total_dir:.0f}%, backward {100*backward/total_dir:.0f}%")

# Rare transitions
rare_trans = [(s1, s2) for s1, s2 in expected if fl_fl_state_trans.get((s1, s2), 0) < 3]
if rare_trans:
    findings.append(f"RARE_TRANSITIONS: {len(rare_trans)} state pairs have <3 occurrences")

# LATE -> EARLY specifically
late_early = fl_fl_state_trans.get(('LATE', 'EARLY'), 0)
if late_early == 0:
    findings.append("NO_LATE_EARLY: LATE -> EARLY never occurs (state reset forbidden?)")
elif late_early < 5:
    findings.append(f"RARE_LATE_EARLY: LATE -> EARLY only {late_early} times")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

FL STATE TRANSITION GRAMMAR:

Direct FL -> FL transitions:
  FORWARD (earlier->later): {100*forward/total_dir:.1f}%
  SAME (stay in stage): {100*same/total_dir:.1f}%
  BACKWARD (later->earlier): {100*backward/total_dir:.1f}%

{'FL state progression is FORWARD-BIASED' if forward > backward * 1.5 else 'FL allows BIDIRECTIONAL state movement'}

LATE -> EARLY: {late_early} occurrences ({'FORBIDDEN/RARE' if late_early < 3 else 'ALLOWED'})

State machine model:
  EARLY <-> MEDIAL <-> LATE
  {'(with forward bias)' if forward > backward else '(bidirectional)'}
  {'LATE -> EARLY is restricted' if late_early < 5 else ''}
""")

# Save results
results = {
    'fl_fl_state_trans': {f"{s1}->{s2}": c for (s1, s2), c in fl_fl_state_trans.items()},
    'direction_counts': {'forward': forward, 'same': same, 'backward': backward},
    'fl_gap_trans': {str(gap): {f"{s1}->{s2}": c for (s1, s2), c in trans.items()}
                     for gap, trans in fl_gap_trans.items()},
    'late_to_early': late_early,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CONTROL_TOPOLOGY_ANALYSIS' / 'results' / 't4_fl_state_transitions.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
