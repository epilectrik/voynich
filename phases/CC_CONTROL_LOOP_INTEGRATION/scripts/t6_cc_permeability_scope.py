"""
T6: CC Permeability Scope

Question: Is the 34% forbidden pair violation rate (C789) CC-specific or generalizable?

C789 established that forbidden pairs are "disfavored (~65% compliance), not absolute."
This was measured on all B transitions. Test if CC transitions show different permeability.

Method:
1. Load forbidden transition pairs
2. Compute violation rate for CC->X transitions specifically
3. Compare to baseline violation rate
4. Test if CC is more/less permeable than other roles
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load class map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

# Load forbidden transitions from C109
# Format: list of (from_class, to_class) pairs
# The 17 forbidden transitions per C109
FORBIDDEN_TRANSITIONS = {
    (8, 31), (8, 32), (8, 33), (8, 34),  # Class 8 -> 31-34
    (31, 8), (32, 8), (33, 8), (34, 8),  # Reverse
    (35, 36), (36, 35),  # 35 <-> 36
    (37, 38), (38, 37),  # 37 <-> 38
    (39, 40), (40, 39),  # 39 <-> 40
    (41, 42), (42, 41),  # 41 <-> 42
    (43, 44),            # 43 -> 44 (directional)
}

CC_CLASSES = {10, 11, 12, 17}
FL_CLASSES = {7, 30, 38, 40}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}  # 18 EN classes per C573
FQ_CLASSES = {9, 13, 14, 23}

def get_role(tc):
    """Get role from class"""
    if tc in CC_CLASSES:
        return 'CC'
    elif tc in FL_CLASSES:
        return 'FL'
    elif tc in EN_CLASSES:
        return 'EN'
    elif tc in FQ_CLASSES:
        return 'FQ'
    elif tc:
        return 'AX'
    return None

# Collect transitions
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    tc = token_to_class.get(w)
    line_tokens[key].append({
        'word': w,
        'class': tc,
        'role': get_role(tc),
    })

# Count transitions and violations by source role
role_transitions = defaultdict(lambda: {'total': 0, 'forbidden': 0, 'forbidden_pairs': Counter()})
all_transitions = {'total': 0, 'forbidden': 0}

for key, tokens in line_tokens.items():
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_t = tokens[i + 1]

        if curr['class'] is None or next_t['class'] is None:
            continue

        pair = (curr['class'], next_t['class'])
        is_forbidden = pair in FORBIDDEN_TRANSITIONS

        all_transitions['total'] += 1
        if is_forbidden:
            all_transitions['forbidden'] += 1

        if curr['role']:
            role_transitions[curr['role']]['total'] += 1
            if is_forbidden:
                role_transitions[curr['role']]['forbidden'] += 1
                role_transitions[curr['role']]['forbidden_pairs'][pair] += 1

print("=" * 60)
print("T6: CC PERMEABILITY SCOPE")
print("=" * 60)

# Baseline violation rate
baseline_rate = all_transitions['forbidden'] / all_transitions['total'] if all_transitions['total'] > 0 else 0
print(f"\nBASELINE (all classified transitions):")
print(f"  Total: {all_transitions['total']}")
print(f"  Forbidden: {all_transitions['forbidden']}")
print(f"  Violation rate: {baseline_rate*100:.2f}%")

results = {
    'baseline': {
        'total': all_transitions['total'],
        'forbidden': all_transitions['forbidden'],
        'rate': float(baseline_rate),
    },
    'by_role': {},
}

print(f"\n{'Role':<10} {'Total':>8} {'Forbidden':>10} {'Rate':>8} {'vs Base':>10}")
print("-" * 50)

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    data = role_transitions[role]
    total = data['total']
    forbidden = data['forbidden']

    if total == 0:
        continue

    rate = forbidden / total
    ratio = rate / baseline_rate if baseline_rate > 0 else 0

    results['by_role'][role] = {
        'total': total,
        'forbidden': forbidden,
        'rate': float(rate),
        'ratio': float(ratio),
    }

    print(f"{role:<10} {total:>8} {forbidden:>10} {rate*100:>7.2f}% {ratio:>9.2f}x")

# Statistical test: is CC different from baseline?
print("\n" + "=" * 60)
print("STATISTICAL TESTS:")
print("=" * 60)

for role in ['CC', 'EN', 'FL', 'FQ']:
    data = role_transitions[role]
    total = data['total']
    forbidden = data['forbidden']

    if total < 10:
        continue

    # Binomial test against baseline rate
    result = stats.binomtest(forbidden, total, baseline_rate, alternative='two-sided')
    p_val = result.pvalue
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"

    rate = forbidden / total
    direction = "HIGHER" if rate > baseline_rate else "LOWER" if rate < baseline_rate else "SAME"

    print(f"\n{role} vs baseline:")
    print(f"  Observed: {forbidden}/{total} ({rate*100:.2f}%)")
    print(f"  Expected: {total * baseline_rate:.1f} ({baseline_rate*100:.2f}%)")
    print(f"  Direction: {direction}")
    print(f"  p = {p_val:.4f} {sig}")

# CC subtype analysis
print("\n" + "=" * 60)
print("CC SUBTYPE ANALYSIS:")
print("=" * 60)

cc_subtype_transitions = defaultdict(lambda: {'total': 0, 'forbidden': 0})
for key, tokens in line_tokens.items():
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_t = tokens[i + 1]

        if curr['class'] is None or next_t['class'] is None:
            continue

        # Classify CC subtype
        if curr['class'] == 10:  # daiin
            subtype = 'DAIIN'
        elif curr['class'] == 11:  # ol
            subtype = 'OL'
        elif curr['class'] == 17:  # ol-derived
            subtype = 'OL_DERIVED'
        else:
            continue

        pair = (curr['class'], next_t['class'])
        is_forbidden = pair in FORBIDDEN_TRANSITIONS

        cc_subtype_transitions[subtype]['total'] += 1
        if is_forbidden:
            cc_subtype_transitions[subtype]['forbidden'] += 1

for subtype in ['DAIIN', 'OL', 'OL_DERIVED']:
    data = cc_subtype_transitions[subtype]
    total = data['total']
    forbidden = data['forbidden']
    if total > 0:
        rate = forbidden / total
        print(f"\n{subtype}:")
        print(f"  Transitions: {total}")
        print(f"  Forbidden: {forbidden} ({rate*100:.2f}%)")

# Interpretation
print("\n" + "=" * 60)
print("INTERPRETATION:")
print("=" * 60)

cc_data = role_transitions['CC']
if cc_data['total'] > 0:
    cc_rate = cc_data['forbidden'] / cc_data['total']
    if cc_rate < baseline_rate * 0.5:
        verdict = "CC is LESS PERMEABLE than baseline (stricter control)"
    elif cc_rate > baseline_rate * 1.5:
        verdict = "CC is MORE PERMEABLE than baseline (looser control)"
    else:
        verdict = "CC permeability is SIMILAR to baseline"
    print(f"\n{verdict}")
    print(f"  CC rate: {cc_rate*100:.2f}%")
    print(f"  Baseline: {baseline_rate*100:.2f}%")
    print(f"  Ratio: {cc_rate/baseline_rate:.2f}x")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'CC_CONTROL_LOOP_INTEGRATION' / 'results' / 't6_permeability_scope.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
