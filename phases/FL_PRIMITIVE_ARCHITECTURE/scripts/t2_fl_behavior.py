"""
T2: FL Behavioral Analysis

Now that we know FL's inventory, analyze what it DOES:
- What transitions does FL participate in?
- What's FL's relationship to hazards?
- How does FL's position in lines relate to its function?
- Is FL the "clock" or sequencing substrate?
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

# Role definitions from BCSC
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

print("="*70)
print("FL BEHAVIORAL ANALYSIS")
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
        role = 'UN'  # Unclassified

    lines_data[key].append({
        'word': w,
        'class': cls,
        'role': role,
        'folio': token.folio,
        'line': token.line
    })

print(f"Total lines: {len(lines_data)}")

# ============================================================
# TRANSITION ANALYSIS
# ============================================================
print("\n" + "="*70)
print("FL TRANSITION ANALYSIS")
print("="*70)

# Count role->role transitions
role_transitions = Counter()
fl_preceded_by = Counter()
fl_followed_by = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        curr_role = tokens[i]['role']
        next_role = tokens[i+1]['role']
        role_transitions[(curr_role, next_role)] += 1

        if next_role == 'FL':
            fl_preceded_by[curr_role] += 1
        if curr_role == 'FL':
            fl_followed_by[next_role] += 1

print("\nWhat precedes FL:")
total_pre = sum(fl_preceded_by.values())
for role, count in fl_preceded_by.most_common():
    pct = 100 * count / total_pre
    print(f"  {role} -> FL: {count:>4} ({pct:>5.1f}%)")

print("\nWhat follows FL:")
total_post = sum(fl_followed_by.values())
for role, count in fl_followed_by.most_common():
    pct = 100 * count / total_post
    print(f"  FL -> {role}: {count:>4} ({pct:>5.1f}%)")

# FL-FL chains
fl_fl = role_transitions[('FL', 'FL')]
print(f"\nFL -> FL (self-chaining): {fl_fl} ({100*fl_fl/total_post:.1f}%)")

# ============================================================
# POSITIONAL ANALYSIS
# ============================================================
print("\n" + "="*70)
print("FL POSITIONAL ANALYSIS")
print("="*70)

fl_positions = []
fl_line_lengths = []

for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['role'] == 'FL':
            # Normalized position (0 = start, 1 = end)
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            fl_positions.append(norm_pos)
            fl_line_lengths.append(line_len)

mean_pos = sum(fl_positions) / len(fl_positions) if fl_positions else 0
print(f"\nFL mean normalized position: {mean_pos:.3f}")
print(f"  (0 = line start, 1 = line end)")

# Position distribution
pos_buckets = {'initial': 0, 'early': 0, 'medial': 0, 'late': 0, 'final': 0}
for pos in fl_positions:
    if pos < 0.1:
        pos_buckets['initial'] += 1
    elif pos < 0.3:
        pos_buckets['early'] += 1
    elif pos < 0.7:
        pos_buckets['medial'] += 1
    elif pos < 0.9:
        pos_buckets['late'] += 1
    else:
        pos_buckets['final'] += 1

print("\nFL position distribution:")
for bucket, count in pos_buckets.items():
    pct = 100 * count / len(fl_positions)
    print(f"  {bucket:<8}: {count:>4} ({pct:>5.1f}%)")

# Line-initial and line-final rates
total_fl = len(fl_positions)
initial_rate = 100 * pos_buckets['initial'] / total_fl
final_rate = 100 * pos_buckets['final'] / total_fl
print(f"\nLine-initial rate: {initial_rate:.1f}%")
print(f"Line-final rate: {final_rate:.1f}%")

# ============================================================
# PER-CLASS POSITION
# ============================================================
print("\n" + "="*70)
print("PER-CLASS POSITIONAL PROFILE")
print("="*70)

class_positions = defaultdict(list)

for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['role'] == 'FL' and t['class']:
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            class_positions[t['class']].append(norm_pos)

for cls in sorted(FL_CLASSES):
    positions = class_positions[cls]
    if positions:
        mean = sum(positions) / len(positions)
        final_count = sum(1 for p in positions if p >= 0.9)
        final_rate = 100 * final_count / len(positions)
        print(f"Class {cls}: mean_pos={mean:.3f}, final_rate={final_rate:.1f}%, n={len(positions)}")

# ============================================================
# HAZARD RELATIONSHIP
# ============================================================
print("\n" + "="*70)
print("FL HAZARD RELATIONSHIP")
print("="*70)

# From BCSC: FL is hazard-SOURCE (initiates 4.5x more than receives)
# Check FL class hazard split: {7, 30} = hazard, {38, 40} = safe

hazard_classes = {7, 30}
safe_classes = {38, 40}

hazard_tokens = sum(1 for key, tokens in lines_data.items()
                    for t in tokens if t['class'] in hazard_classes)
safe_tokens = sum(1 for key, tokens in lines_data.items()
                  for t in tokens if t['class'] in safe_classes)

print(f"\nFL hazard/safe split:")
print(f"  Hazard classes {{7, 30}}: {hazard_tokens} tokens ({100*hazard_tokens/(hazard_tokens+safe_tokens):.1f}%)")
print(f"  Safe classes {{38, 40}}: {safe_tokens} tokens ({100*safe_tokens/(hazard_tokens+safe_tokens):.1f}%)")

# Position difference between hazard and safe
hazard_positions = [p for cls in hazard_classes for p in class_positions.get(cls, [])]
safe_positions = [p for cls in safe_classes for p in class_positions.get(cls, [])]

if hazard_positions and safe_positions:
    hazard_mean = sum(hazard_positions) / len(hazard_positions)
    safe_mean = sum(safe_positions) / len(safe_positions)
    print(f"\nPosition by hazard status:")
    print(f"  Hazard FL mean position: {hazard_mean:.3f}")
    print(f"  Safe FL mean position: {safe_mean:.3f}")
    print(f"  Difference: {safe_mean - hazard_mean:.3f} (safe is more final)")

# ============================================================
# FL IN CONTEXT: What surrounds FL?
# ============================================================
print("\n" + "="*70)
print("FL CONTEXT ANALYSIS")
print("="*70)

# What classes immediately surround FL?
before_fl_class = Counter()
after_fl_class = Counter()

for key, tokens in lines_data.items():
    for i, t in enumerate(tokens):
        if t['role'] == 'FL':
            if i > 0 and tokens[i-1]['class']:
                before_fl_class[tokens[i-1]['class']] += 1
            if i < len(tokens) - 1 and tokens[i+1]['class']:
                after_fl_class[tokens[i+1]['class']] += 1

print("\nClasses immediately BEFORE FL (top 10):")
for cls, count in before_fl_class.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    print(f"  Class {cls} ({role}): {count}")

print("\nClasses immediately AFTER FL (top 10):")
for cls, count in after_fl_class.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    print(f"  Class {cls} ({role}): {count}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

if mean_pos > 0.6:
    findings.append(f"FINAL_BIASED: FL mean position {mean_pos:.3f} (later in lines)")
elif mean_pos < 0.4:
    findings.append(f"INITIAL_BIASED: FL mean position {mean_pos:.3f} (earlier in lines)")
else:
    findings.append(f"MEDIAL: FL mean position {mean_pos:.3f}")

if final_rate > 20:
    findings.append(f"LINE_CLOSER: {final_rate:.1f}% of FL tokens are line-final")

if hazard_tokens > safe_tokens * 5:
    findings.append(f"HAZARD_DOMINANT: {100*hazard_tokens/(hazard_tokens+safe_tokens):.1f}% hazard classes")

# Check FL->FQ pattern (from BCSC: FQ-FL symbiosis)
fl_to_fq = fl_followed_by.get('FQ', 0)
fl_to_fq_rate = 100 * fl_to_fq / total_post if total_post else 0
if fl_to_fq_rate > 10:
    findings.append(f"FQ_FEEDER: FL -> FQ at {fl_to_fq_rate:.1f}%")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Save results
results = {
    'transitions': {
        'fl_preceded_by': dict(fl_preceded_by),
        'fl_followed_by': dict(fl_followed_by),
        'fl_fl_chains': fl_fl
    },
    'position': {
        'mean': mean_pos,
        'initial_rate': initial_rate,
        'final_rate': final_rate,
        'distribution': pos_buckets
    },
    'hazard_split': {
        'hazard_tokens': hazard_tokens,
        'safe_tokens': safe_tokens,
        'hazard_mean_pos': hazard_mean if hazard_positions else None,
        'safe_mean_pos': safe_mean if safe_positions else None
    },
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't2_fl_behavior.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
