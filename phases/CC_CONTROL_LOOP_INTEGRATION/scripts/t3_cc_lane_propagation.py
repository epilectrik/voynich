"""
T3: CC Lane Propagation

Question: Does lane assignment at CC propagate through the control loop?

Method:
1. Per C600: daiin -> EN_CHSH, ol-derived -> EN_QO
2. Track lane of tokens following CC through the line
3. Test if initial CC lane assignment persists downstream
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

CC_CLASSES = {10, 11, 12, 17}

def get_lane(word):
    """Determine lane from PREFIX"""
    m = morph.extract(word)
    prefix = m.prefix or ''
    if prefix == 'qo':
        return 'QO'
    elif prefix in {'ch', 'sh'}:
        return 'CHSH'
    else:
        return 'OTHER'

def get_cc_type(word, tc):
    """Classify CC subtype"""
    if tc not in CC_CLASSES:
        return None
    if word == 'daiin':
        return 'DAIIN'
    elif word == 'ol':
        return 'OL'
    elif tc == 17:
        return 'OL_DERIVED'
    return None

# Collect tokens by line
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
        'cc_type': get_cc_type(w, tc),
        'lane': get_lane(w),
    })

# Analyze lane propagation after CC
# For each CC token, track lanes of subsequent tokens in same line
propagation = defaultdict(lambda: defaultdict(Counter))

for key, tokens in line_tokens.items():
    for i, t in enumerate(tokens):
        if t['cc_type'] is None:
            continue

        cc_type = t['cc_type']

        # Track lanes of subsequent tokens
        for offset, succ in enumerate(tokens[i+1:], start=1):
            lane = succ['lane']
            if lane in ['QO', 'CHSH']:  # Only count lane-assigned tokens
                propagation[cc_type][offset][lane] += 1

print("=" * 60)
print("T3: CC LANE PROPAGATION")
print("=" * 60)

# Per C600: daiin -> CHSH, ol-derived -> QO
# Test if this holds at various offsets

results = {}
for cc_type in ['DAIIN', 'OL', 'OL_DERIVED']:
    print(f"\n{'-'*40}")
    print(f"{cc_type} LANE PROPAGATION:")
    print(f"{'-'*40}")

    results[cc_type] = {}

    for offset in [1, 2, 3, 5, 10]:
        counts = propagation[cc_type].get(offset, Counter())
        total = counts['QO'] + counts['CHSH']
        if total < 10:
            continue

        qo_rate = counts['QO'] / total if total > 0 else 0
        chsh_rate = counts['CHSH'] / total if total > 0 else 0

        # Chi-squared against 50/50 baseline
        expected = total / 2
        if expected > 0:
            chi2 = ((counts['QO'] - expected)**2 + (counts['CHSH'] - expected)**2) / expected
            p_val = 1 - stats.chi2.cdf(chi2, df=1)
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"
        else:
            chi2, p_val, sig = 0, 1, "NS"

        dominant = 'QO' if qo_rate > chsh_rate else 'CHSH'

        results[cc_type][f'offset_{offset}'] = {
            'qo': counts['QO'],
            'chsh': counts['CHSH'],
            'total': total,
            'qo_rate': float(qo_rate),
            'chsh_rate': float(chsh_rate),
            'dominant': dominant,
            'chi2': float(chi2),
            'p': float(p_val),
        }

        print(f"  Offset +{offset}: QO={counts['QO']} ({qo_rate*100:.1f}%), CHSH={counts['CHSH']} ({chsh_rate*100:.1f}%), dominant={dominant} {sig}")

# Test C600 predictions
print("\n" + "=" * 60)
print("C600 PREDICTION TEST:")
print("=" * 60)
print("  C600 claims: daiin -> EN_CHSH, ol-derived -> EN_QO")

# DAIIN immediate successor (offset=1)
daiin_1 = propagation['DAIIN'].get(1, Counter())
daiin_total = daiin_1['QO'] + daiin_1['CHSH']
if daiin_total > 0:
    daiin_chsh_rate = daiin_1['CHSH'] / daiin_total
    print(f"\n  DAIIN +1: CHSH rate = {daiin_chsh_rate*100:.1f}% (C600 predicts CHSH-biased)")
    print(f"    Verdict: {'CONFIRMED' if daiin_chsh_rate > 0.5 else 'NOT CONFIRMED'}")

# OL_DERIVED immediate successor
old_1 = propagation['OL_DERIVED'].get(1, Counter())
old_total = old_1['QO'] + old_1['CHSH']
if old_total > 0:
    old_qo_rate = old_1['QO'] / old_total
    print(f"\n  OL_DERIVED +1: QO rate = {old_qo_rate*100:.1f}% (C600 predicts QO-biased)")
    print(f"    Verdict: {'CONFIRMED' if old_qo_rate > 0.5 else 'NOT CONFIRMED'}")

# Test decay: does lane bias persist?
print("\n" + "-" * 40)
print("LANE BIAS DECAY:")
print("-" * 40)

for cc_type, expected_lane in [('DAIIN', 'CHSH'), ('OL_DERIVED', 'QO')]:
    print(f"\n  {cc_type} (expected: {expected_lane}):")
    for offset in [1, 2, 3, 5, 10]:
        counts = propagation[cc_type].get(offset, Counter())
        total = counts['QO'] + counts['CHSH']
        if total < 10:
            continue
        expected_rate = counts[expected_lane] / total if total > 0 else 0
        print(f"    +{offset}: {expected_lane} rate = {expected_rate*100:.1f}% (n={total})")

# Save results
out_path = PROJECT_ROOT / 'phases' / 'CC_CONTROL_LOOP_INTEGRATION' / 'results' / 't3_lane_propagation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
