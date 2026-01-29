"""
Line-1 HT and A-Folio Context

T1 showed line-1 HT MIDDLEs are 1.92x more likely in best-match A folio.
Let's understand this better:

1. Which line-1 HT MIDDLEs are driving the enrichment?
2. Are these the PP portion of line-1 HT (30.2% per C792)?
3. Can line-1 HT predict best-match A folio?
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
classified_tokens = set(ctm['token_to_class'].keys())

print("=" * 70)
print("LINE-1 HT AND A-FOLIO CONTEXT")
print("=" * 70)

# ============================================================
# COLLECT DATA
# ============================================================

# A folio pools
a_folio_pools = defaultdict(set)
all_a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_folio_pools[token.folio].add(m.middle)
            all_a_middles.add(m.middle)

# B data
b_data = defaultdict(lambda: {'line1_ht': [], 'all_pp': []})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens
    m = morph.extract(w)
    mid = m.middle

    if not mid:
        continue

    is_pp = mid in all_a_middles

    if line == '1' and is_ht:
        b_data[folio]['line1_ht'].append(mid)
    if is_pp:
        b_data[folio]['all_pp'].append(mid)

b_folios = sorted(b_data.keys())
a_folios = sorted(a_folio_pools.keys())

# Best-match A folio for each B
coverage = {}
for b_fol in b_folios:
    b_pp = set(b_data[b_fol]['all_pp'])
    if not b_pp:
        continue
    coverage[b_fol] = {}
    for a_fol in a_folios:
        a_pool = a_folio_pools[a_fol]
        cov = len(a_pool & b_pp) / len(b_pp)
        coverage[b_fol][a_fol] = cov

best_match = {}
for b_fol in coverage:
    best_a = max(coverage[b_fol], key=coverage[b_fol].get)
    best_match[b_fol] = best_a

# ============================================================
# T1: PARTITION LINE-1 HT INTO PP vs B-EXCLUSIVE
# ============================================================
print("\n" + "=" * 70)
print("T1: LINE-1 HT PARTITION (PP vs B-EXCLUSIVE)")
print("=" * 70)

line1_ht_pp = []  # Line-1 HT MIDDLEs that are PP
line1_ht_exclusive = []  # Line-1 HT MIDDLEs that are B-exclusive

for b_fol in b_folios:
    for mid in b_data[b_fol]['line1_ht']:
        if mid in all_a_middles:
            line1_ht_pp.append(mid)
        else:
            line1_ht_exclusive.append(mid)

print(f"\nLine-1 HT MIDDLEs:")
print(f"  PP (in A): {len(line1_ht_pp)} ({100*len(line1_ht_pp)/(len(line1_ht_pp)+len(line1_ht_exclusive)):.1f}%)")
print(f"  B-exclusive: {len(line1_ht_exclusive)} ({100*len(line1_ht_exclusive)/(len(line1_ht_pp)+len(line1_ht_exclusive)):.1f}%)")

# ============================================================
# T2: DO PP LINE-1 HT MIDDLES PREDICT BEST-MATCH?
# ============================================================
print("\n" + "=" * 70)
print("T2: PP LINE-1 HT PREDICTION OF BEST-MATCH")
print("=" * 70)

# For each B folio, use its PP line-1 HT MIDDLEs to predict A folio
# Prediction: which A folio has highest overlap with line-1 PP HT?

correct_predictions = 0
total_predictions = 0

rng = np.random.RandomState(42)

for b_fol in b_folios:
    line1_ht = set(b_data[b_fol]['line1_ht'])
    line1_pp_ht = line1_ht & all_a_middles  # Only PP portion

    if len(line1_pp_ht) < 2:  # Need at least 2 to predict
        continue

    if b_fol not in best_match:
        continue

    true_best = best_match[b_fol]

    # Predict: which A folio has highest overlap with line1_pp_ht?
    best_overlap = -1
    predicted_a = None
    for a_fol in a_folios:
        overlap = len(line1_pp_ht & a_folio_pools[a_fol])
        if overlap > best_overlap:
            best_overlap = overlap
            predicted_a = a_fol

    total_predictions += 1
    if predicted_a == true_best:
        correct_predictions += 1

print(f"\nPrediction using PP line-1 HT MIDDLEs:")
print(f"  Correct: {correct_predictions}/{total_predictions} ({100*correct_predictions/total_predictions:.1f}%)")
print(f"  Random baseline: {1/len(a_folios)*100:.2f}%")
print(f"  Lift: {(correct_predictions/total_predictions) / (1/len(a_folios)):.1f}x")

# ============================================================
# T3: WHAT ARE THE PREDICTIVE PP LINE-1 HT MIDDLES?
# ============================================================
print("\n" + "=" * 70)
print("T3: MOST PREDICTIVE PP LINE-1 HT MIDDLES")
print("=" * 70)

# Count PP line-1 HT by MIDDLE
pp_ht_counter = Counter(line1_ht_pp)

print(f"\nMost common PP line-1 HT MIDDLEs:")
for mid, count in pp_ht_counter.most_common(15):
    # How many A folios have this MIDDLE?
    n_a_folios = sum(1 for p in a_folio_pools.values() if mid in p)
    print(f"  '{mid}': {count} occ, in {n_a_folios}/114 A folios ({100*n_a_folios/114:.0f}%)")

# ============================================================
# T4: B-EXCLUSIVE LINE-1 HT - WHAT IS IT?
# ============================================================
print("\n" + "=" * 70)
print("T4: B-EXCLUSIVE LINE-1 HT VOCABULARY")
print("=" * 70)

exclusive_counter = Counter(line1_ht_exclusive)

print(f"\nMost common B-exclusive line-1 HT MIDDLEs:")
for mid, count in exclusive_counter.most_common(15):
    print(f"  '{mid}': {count} occurrences")

# Are these folio-unique?
mid_to_folios = defaultdict(set)
for b_fol in b_folios:
    for mid in b_data[b_fol]['line1_ht']:
        if mid not in all_a_middles:
            mid_to_folios[mid].add(b_fol)

folio_unique_exclusive = [m for m, f in mid_to_folios.items() if len(f) == 1]
print(f"\nFolio-unique B-exclusive line-1 HT: {len(folio_unique_exclusive)}/{len(set(line1_ht_exclusive))} ({100*len(folio_unique_exclusive)/len(set(line1_ht_exclusive)):.1f}%)")

# ============================================================
# T5: TWO-PART STRUCTURE?
# ============================================================
print("\n" + "=" * 70)
print("T5: LINE-1 HT TWO-PART STRUCTURE")
print("=" * 70)

# Hypothesis: Line-1 HT has two parts:
# 1. PP portion (39.6%) - carries A-folio context information
# 2. B-exclusive portion (60.4%) - folio-unique identifiers

print(f"""
LINE-1 HT STRUCTURE HYPOTHESIS:

PART 1: PP Component ({100*len(line1_ht_pp)/(len(line1_ht_pp)+len(line1_ht_exclusive)):.1f}%)
  - Uses vocabulary from A's PP pool
  - Enriched 1.92x in best-match A folio
  - Carries A-folio context information
  - Predicts best-match A at {100*correct_predictions/total_predictions:.1f}% (vs {1/len(a_folios)*100:.1f}% random)

PART 2: B-Exclusive Component ({100*len(line1_ht_exclusive)/(len(line1_ht_pp)+len(line1_ht_exclusive)):.1f}%)
  - Uses vocabulary NOT in any A folio
  - {100*len(folio_unique_exclusive)/len(set(line1_ht_exclusive)):.1f}% folio-unique
  - Serves as folio identifier
  - No A-folio context information

INTERPRETATION:
Line-1 is a COMPOSITE header with dual function:
1. Context declaration (PP portion) - "this program operates under A-folio X context"
2. Folio identification (B-exclusive portion) - "this is folio Y"
""")

# ============================================================
# T6: CORRELATION BETWEEN PP PORTION AND BODY PP
# ============================================================
print("\n" + "=" * 70)
print("T6: PP PORTION CORRELATION WITH BODY")
print("=" * 70)

# Does having more PP in line-1 predict more PP in body?
correlations = []
for b_fol in b_folios:
    line1_ht = b_data[b_fol]['line1_ht']
    if not line1_ht:
        continue

    line1_pp_count = sum(1 for m in line1_ht if m in all_a_middles)
    line1_pp_frac = line1_pp_count / len(line1_ht)

    body_pp = b_data[b_fol]['all_pp']
    # Compare to folio's overall PP density

    correlations.append((line1_pp_frac, len(set(body_pp))))

if correlations:
    from scipy.stats import spearmanr
    x = [c[0] for c in correlations]
    y = [c[1] for c in correlations]
    rho, pval = spearmanr(x, y)
    print(f"\nLine-1 PP fraction vs body PP vocabulary size:")
    print(f"  Spearman rho = {rho:.3f}, p = {pval:.4f}")
