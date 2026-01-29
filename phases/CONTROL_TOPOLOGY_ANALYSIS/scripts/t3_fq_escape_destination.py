"""
T3: FQ Escape Destination Analysis

FQ is phase-bypass escape (0% h).
Hazard FL drives 98% of FL->FQ.

Questions:
1. What happens AFTER FQ?
2. Where does escaped material go?
3. Does FQ lead back to FL, or somewhere else?
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

FQ_CLASSES = {9, 13, 14, 23}
FL_CLASSES = {7, 30, 38, 40}

# FL state categories
FL_EARLY = {'i', 'ii', 'in'}
FL_MEDIAL = {'r', 'ar', 'al', 'l', 'ol'}
FL_LATE = {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}

def get_fl_stage(middle):
    if middle in FL_EARLY:
        return 'EARLY'
    elif middle in FL_MEDIAL:
        return 'MEDIAL'
    elif middle in FL_LATE:
        return 'LATE'
    return 'OTHER'

print("="*70)
print("FQ ESCAPE DESTINATION ANALYSIS")
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
# WHAT FOLLOWS FQ?
# ============================================================
print("\n" + "="*70)
print("WHAT FOLLOWS FQ?")
print("="*70)

fq_followed_by = Counter()
fq_followed_by_class = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'FQ':
            next_role = tokens[i+1]['role']
            next_class = tokens[i+1]['class']
            fq_followed_by[next_role] += 1
            if next_class:
                fq_followed_by_class[next_class] += 1

total_fq_trans = sum(fq_followed_by.values())
print(f"\nTotal FQ transitions: {total_fq_trans}")
print("\nFQ -> Role distribution:")
for role, count in fq_followed_by.most_common():
    pct = 100 * count / total_fq_trans
    print(f"  FQ -> {role}: {count} ({pct:.1f}%)")

print("\nFQ -> Class (top 10):")
for cls, count in fq_followed_by_class.most_common(10):
    role = ROLE_MAP.get(cls, 'UNK')
    pct = 100 * count / total_fq_trans
    print(f"  FQ -> {cls} ({role}): {count} ({pct:.1f}%)")

# ============================================================
# FQ -> FL: WHICH FL STATE?
# ============================================================
print("\n" + "="*70)
print("FQ -> FL: DESTINATION STATE")
print("="*70)

fq_to_fl_state = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'FQ' and tokens[i+1]['role'] == 'FL':
            fl_mid = tokens[i+1]['middle']
            fl_stage = get_fl_stage(fl_mid)
            fq_to_fl_state[fl_stage] += 1

total_fq_fl = sum(fq_to_fl_state.values())
print(f"\nFQ -> FL transitions: {total_fq_fl}")
print("\nFQ -> FL by destination state:")
for stage, count in fq_to_fl_state.most_common():
    pct = 100 * count / total_fq_fl if total_fq_fl else 0
    print(f"  FQ -> FL[{stage}]: {count} ({pct:.1f}%)")

# ============================================================
# FL -> FQ -> ? SEQUENCES
# ============================================================
print("\n" + "="*70)
print("FL -> FQ -> ? SEQUENCES")
print("="*70)

fl_fq_then = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 2):
        if tokens[i]['role'] == 'FL' and tokens[i+1]['role'] == 'FQ':
            next_role = tokens[i+2]['role']
            fl_fq_then[next_role] += 1

total_fl_fq = sum(fl_fq_then.values())
print(f"\nFL -> FQ -> ? sequences: {total_fl_fq}")
print("\nAfter FL -> FQ, what comes next:")
for role, count in fl_fq_then.most_common():
    pct = 100 * count / total_fl_fq if total_fl_fq else 0
    print(f"  FL -> FQ -> {role}: {count} ({pct:.1f}%)")

# ============================================================
# FQ CHAIN LENGTH
# ============================================================
print("\n" + "="*70)
print("FQ CHAIN BEHAVIOR")
print("="*70)

# How often does FQ chain (FQ -> FQ)?
fq_chains = 0
fq_exits = 0

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'FQ':
            if tokens[i+1]['role'] == 'FQ':
                fq_chains += 1
            else:
                fq_exits += 1

total_fq_next = fq_chains + fq_exits
chain_rate = 100 * fq_chains / total_fq_next if total_fq_next else 0
print(f"\nFQ -> FQ (chaining): {fq_chains} ({chain_rate:.1f}%)")
print(f"FQ -> other (exiting): {fq_exits} ({100-chain_rate:.1f}%)")

# ============================================================
# FQ POSITIONAL PROFILE
# ============================================================
print("\n" + "="*70)
print("FQ POSITIONAL PROFILE")
print("="*70)

fq_positions = []
for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['role'] == 'FQ':
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            fq_positions.append(norm_pos)

fq_mean_pos = np.mean(fq_positions)
fq_std_pos = np.std(fq_positions)

# Line-final rate
fq_final = sum(1 for p in fq_positions if p >= 0.9)
fq_final_rate = 100 * fq_final / len(fq_positions)

print(f"\nFQ mean position: {fq_mean_pos:.3f} +/- {fq_std_pos:.3f}")
print(f"FQ line-final rate (pos >= 0.9): {fq_final_rate:.1f}%")

# Compare to other roles
fl_mean = 0.576  # from previous analysis
en_mean = 0.483
print(f"\nComparison:")
print(f"  FL mean: {fl_mean:.3f}")
print(f"  EN mean: {en_mean:.3f}")
print(f"  FQ mean: {fq_mean_pos:.3f}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# FQ -> FL rate
fq_to_fl_rate = 100 * fq_followed_by.get('FL', 0) / total_fq_trans if total_fq_trans else 0
if fq_to_fl_rate > 10:
    findings.append(f"FQ_RETURNS_FL: {fq_to_fl_rate:.1f}% of FQ leads back to FL")

# FQ -> FL destination state
if fq_to_fl_state:
    top_state, top_count = fq_to_fl_state.most_common(1)[0]
    top_pct = 100 * top_count / total_fq_fl if total_fq_fl else 0
    findings.append(f"FQ_FL_TARGET: FQ -> FL[{top_state}] at {top_pct:.1f}%")

# FQ chain rate
if chain_rate > 20:
    findings.append(f"FQ_CHAINS: FQ self-chains at {chain_rate:.1f}%")
elif chain_rate < 10:
    findings.append(f"FQ_EXITS_FAST: FQ rarely chains ({chain_rate:.1f}%)")

# FQ position
if fq_mean_pos > 0.6:
    findings.append(f"FQ_LATE_POSITION: FQ mean pos {fq_mean_pos:.3f} (later than FL/EN)")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

FQ ESCAPE DESTINATION:

After FQ, material goes to:
  - UN: {100*fq_followed_by.get('UN', 0)/total_fq_trans:.1f}%
  - EN: {100*fq_followed_by.get('EN', 0)/total_fq_trans:.1f}%
  - FL: {100*fq_followed_by.get('FL', 0)/total_fq_trans:.1f}%
  - FQ: {100*fq_followed_by.get('FQ', 0)/total_fq_trans:.1f}% (chaining)
  - AX: {100*fq_followed_by.get('AX', 0)/total_fq_trans:.1f}%
  - CC: {100*fq_followed_by.get('CC', 0)/total_fq_trans:.1f}%

When FQ returns to FL, destination state:
{dict(fq_to_fl_state)}

FQ is {'LINE-FINAL biased' if fq_final_rate > 20 else 'position-flexible'} ({fq_final_rate:.1f}% final)

ESCAPE MODEL:
  FL[hazard] -> FQ (phase-bypass) -> {'primarily ' + fq_followed_by.most_common(1)[0][0] if fq_followed_by else '?'}
""")

# Save results
results = {
    'fq_followed_by': dict(fq_followed_by),
    'fq_followed_by_class': dict(fq_followed_by_class),
    'fq_to_fl_state': dict(fq_to_fl_state),
    'fl_fq_then': dict(fl_fq_then),
    'fq_chain_rate': chain_rate,
    'fq_mean_position': float(fq_mean_pos),
    'fq_final_rate': fq_final_rate,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CONTROL_TOPOLOGY_ANALYSIS' / 'results' / 't3_fq_escape_destination.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
