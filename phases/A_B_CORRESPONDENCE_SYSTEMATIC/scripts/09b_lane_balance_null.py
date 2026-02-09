"""
09b_lane_balance_null.py

Verify lane balance correlation with null model.
The 0.989-0.997 correlation seems too high - is it an artifact of best-match selection?
"""

import sys
import json
import random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("LANE BALANCE - NULL MODEL VERIFICATION")
print("="*70)

tx = Transcript()
morph = Morphology()

QO_LANE = {'qo'}
CHSH_LANE = {'ch', 'sh'}
GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter):
    by_folio_line = defaultdict(list)
    for t in tokens_iter:
        if t.word and '*' not in t.word:
            by_folio_line[(t.folio, t.line)].append(t)

    paragraphs = []
    current_para = {'tokens': [], 'folio': None}
    current_folio = None

    for (folio, line) in sorted(by_folio_line.keys()):
        tokens = by_folio_line[(folio, line)]
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'tokens': [], 'folio': folio}
            current_folio = folio
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs

def compute_lane_balance(tokens):
    qo_count = 0
    chsh_count = 0
    for t in tokens:
        word = t.word if hasattr(t, 'word') else t['word']
        try:
            m = morph.extract(word)
            if m.prefix in QO_LANE:
                qo_count += 1
            elif m.prefix in CHSH_LANE:
                chsh_count += 1
        except:
            pass
    total = qo_count + chsh_count
    return qo_count / total if total > 0 else 0.5

def correlation(x, y):
    n = len(x)
    if n == 0:
        return 0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = sum((xi - mx)**2 for xi in x) ** 0.5
    den_y = sum((yi - my)**2 for yi in y) ** 0.5
    return num / (den_x * den_y) if den_x * den_y > 0 else 0

# Build paragraphs
a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

# Compute lane balances
a_lanes = [compute_lane_balance(p['tokens']) for p in a_paras]
b_lanes = [compute_lane_balance(p['tokens']) for p in b_paras]

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# ACTUAL MATCHING (best lane match)
# =============================================================
print("\n" + "="*70)
print("ACTUAL BEST-MATCH")
print("="*70)

matched_b_lanes = []
for a_lane in a_lanes:
    best_b = min(b_lanes, key=lambda b: abs(a_lane - b))
    matched_b_lanes.append(best_b)

actual_corr = correlation(a_lanes, matched_b_lanes)
print(f"Actual correlation (A -> best-matching B): {actual_corr:.4f}")

# =============================================================
# NULL MODEL: Random matching
# =============================================================
print("\n" + "="*70)
print("NULL MODEL: RANDOM MATCHING")
print("="*70)

null_correlations = []
for _ in range(1000):
    random_b_lanes = [random.choice(b_lanes) for _ in a_lanes]
    null_corr = correlation(a_lanes, random_b_lanes)
    null_correlations.append(null_corr)

mean_null = sum(null_correlations) / len(null_correlations)
std_null = (sum((c - mean_null)**2 for c in null_correlations) / len(null_correlations)) ** 0.5

print(f"Null mean correlation: {mean_null:.4f}")
print(f"Null std: {std_null:.4f}")
print(f"Actual vs null: {(actual_corr - mean_null) / std_null:.1f} standard deviations")

# =============================================================
# NULL MODEL: Best-match on SHUFFLED labels
# =============================================================
print("\n" + "="*70)
print("NULL MODEL: BEST-MATCH ON SHUFFLED B")
print("="*70)

# What if we shuffle B lane labels?
shuffled_correlations = []
for _ in range(100):
    shuffled_b = b_lanes.copy()
    random.shuffle(shuffled_b)

    matched_shuffled = []
    for a_lane in a_lanes:
        best_b = min(shuffled_b, key=lambda b: abs(a_lane - b))
        matched_shuffled.append(best_b)

    shuffled_corr = correlation(a_lanes, matched_shuffled)
    shuffled_correlations.append(shuffled_corr)

mean_shuffled = sum(shuffled_correlations) / len(shuffled_correlations)
std_shuffled = (sum((c - mean_shuffled)**2 for c in shuffled_correlations) / len(shuffled_correlations)) ** 0.5

print(f"Shuffled best-match mean: {mean_shuffled:.4f}")
print(f"Shuffled std: {std_shuffled:.4f}")
print(f"Actual vs shuffled: {(actual_corr - mean_shuffled) / std_shuffled:.1f} std devs")

# =============================================================
# KEY TEST: Does matching preserve identity?
# =============================================================
print("\n" + "="*70)
print("KEY TEST: VOCABULARY OVERLAP WITH MATCHED B")
print("="*70)

# The real question: when we match A to B by lane balance,
# do we get vocabulary overlap?

ri_middles, pp_middles = load_middle_classes()

def get_pp_middles(para):
    pp = set()
    for t in para['tokens']:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                pp.add(m.middle)
        except:
            pass
    return pp

# For each A, get best lane-match B and compute PP overlap
lane_match_overlaps = []
random_match_overlaps = []

for i, a_para in enumerate(a_paras):
    a_pp = get_pp_middles(a_para)
    if not a_pp:
        continue

    a_lane = a_lanes[i]

    # Best lane match
    best_b_idx = min(range(len(b_paras)), key=lambda j: abs(a_lane - b_lanes[j]))
    best_b_pp = get_pp_middles(b_paras[best_b_idx])
    if best_b_pp:
        overlap = len(a_pp & best_b_pp) / len(best_b_pp)
        lane_match_overlaps.append(overlap)

    # Random B
    rand_b_idx = random.randint(0, len(b_paras) - 1)
    rand_b_pp = get_pp_middles(b_paras[rand_b_idx])
    if rand_b_pp:
        overlap = len(a_pp & rand_b_pp) / len(rand_b_pp)
        random_match_overlaps.append(overlap)

print(f"\nPP vocabulary overlap:")
print(f"  Lane-matched B: {sum(lane_match_overlaps)/len(lane_match_overlaps):.1%}")
print(f"  Random B: {sum(random_match_overlaps)/len(random_match_overlaps):.1%}")
print(f"  Lift: {(sum(lane_match_overlaps)/len(lane_match_overlaps)) / (sum(random_match_overlaps)/len(random_match_overlaps)):.2f}x")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Is the 0.989 lane correlation real or an artifact?

1. CORRELATION ANALYSIS:
   Actual (best-match): {actual_corr:.4f}
   Random match: {mean_null:.4f}
   Best-match shuffled: {mean_shuffled:.4f}

2. INTERPRETATION:
   - Best-match selection gives high correlation BY DESIGN
   - The question is: does it also give vocabulary overlap?

3. VOCABULARY OVERLAP TEST:
   Lane-matched: {sum(lane_match_overlaps)/len(lane_match_overlaps):.1%}
   Random: {sum(random_match_overlaps)/len(random_match_overlaps):.1%}
""")

lift = (sum(lane_match_overlaps)/len(lane_match_overlaps)) / (sum(random_match_overlaps)/len(random_match_overlaps))
if lift > 1.2:
    print(f"FINDING: Lane matching produces {lift:.2f}x better vocabulary overlap.")
    print("Lane balance IS a meaningful predictor of A-B correspondence.")
else:
    print(f"FINDING: Lane matching produces only {lift:.2f}x vocabulary overlap.")
    print("Lane balance is NOT a meaningful predictor - correlation is artifact.")
