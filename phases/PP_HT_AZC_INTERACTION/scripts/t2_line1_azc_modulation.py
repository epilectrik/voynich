"""
T2: Does AZC Modulation Affect Line-1 Specifically?

C794-C795 established that line-1 HT is a composite header:
- 68.3% PP (A-context declaration)
- 31.7% B-exclusive (folio ID)
- PP portion predicts best-match A at 15.8x random

Question: Does AZC mediation level affect this line-1 structure?

Hypotheses:
H1: High AZC-mediation folios have different line-1 PP/B-exclusive ratio
H2: Line-1 A-context prediction accuracy differs by AZC mediation level
H3: AZC provides an additional layer of context beyond A

Tests:
1. Line-1 HT composition by AZC tertile
2. A-context prediction accuracy by AZC tertile
3. Does including AZC improve prediction beyond A-only?
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

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

print("=" * 70)
print("T2: LINE-1 AZC MODULATION")
print("=" * 70)

# Collect vocabulary pools
azc_middles = set()
a_folio_pools = defaultdict(set)
all_a_middles = set()

for token in tx.azc():
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)

for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_folio_pools[token.folio].add(m.middle)
            all_a_middles.add(m.middle)

print(f"\nAZC unique MIDDLEs: {len(azc_middles)}")
print(f"A unique MIDDLEs: {len(all_a_middles)}")
print(f"A folios: {len(a_folio_pools)}")

# Collect B data
b_data = defaultdict(lambda: {
    'total_tokens': 0,
    'line1_ht_middles': [],
    'all_pp_middles': [],
    'middles': set(),
    'azc_mediated_middles': set(),
})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens
    m = morph.extract(w)
    mid = m.middle

    b_data[folio]['total_tokens'] += 1

    if mid:
        b_data[folio]['middles'].add(mid)
        if mid in azc_middles:
            b_data[folio]['azc_mediated_middles'].add(mid)

        if line == '1' and is_ht:
            b_data[folio]['line1_ht_middles'].append(mid)

        if mid in all_a_middles:
            b_data[folio]['all_pp_middles'].append(mid)

# Compute AZC mediation and best-match A
b_folios = sorted(b_data.keys())
a_folios = sorted(a_folio_pools.keys())

folio_metrics = []
for b_fol in b_folios:
    d = b_data[b_fol]
    total_middles = len(d['middles'])
    azc_med = len(d['azc_mediated_middles'])

    if total_middles == 0:
        continue

    azc_pct = 100 * azc_med / total_middles

    # Find best-match A folio
    b_pp = set(d['all_pp_middles'])
    if not b_pp:
        continue

    best_a = None
    best_cov = -1
    for a_fol in a_folios:
        cov = len(a_folio_pools[a_fol] & b_pp) / len(b_pp)
        if cov > best_cov:
            best_cov = cov
            best_a = a_fol

    folio_metrics.append({
        'folio': b_fol,
        'azc_pct': azc_pct,
        'best_a': best_a,
        'best_cov': best_cov,
        'line1_ht': d['line1_ht_middles'],
    })

print(f"\nB folios with data: {len(folio_metrics)}")

# Split by AZC tertile
sorted_by_azc = sorted(folio_metrics, key=lambda r: r['azc_pct'])
n = len(sorted_by_azc)
tertile_size = n // 3

low_azc = sorted_by_azc[:tertile_size]
med_azc = sorted_by_azc[tertile_size:2*tertile_size]
high_azc = sorted_by_azc[2*tertile_size:]

# ============================================================
# TEST 1: Line-1 PP fraction by AZC tertile
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: LINE-1 PP FRACTION BY AZC TERTILE")
print("=" * 70)

def compute_line1_pp_fraction(folio_list):
    """Compute fraction of line-1 HT MIDDLEs that are PP (in A)."""
    total_line1 = 0
    pp_line1 = 0
    for f in folio_list:
        for mid in f['line1_ht']:
            total_line1 += 1
            if mid in all_a_middles:
                pp_line1 += 1
    return pp_line1 / total_line1 if total_line1 > 0 else 0

low_pp_frac = compute_line1_pp_fraction(low_azc)
med_pp_frac = compute_line1_pp_fraction(med_azc)
high_pp_frac = compute_line1_pp_fraction(high_azc)

print(f"\nLow AZC tertile: Line-1 PP fraction = {100*low_pp_frac:.1f}%")
print(f"Medium AZC tertile: Line-1 PP fraction = {100*med_pp_frac:.1f}%")
print(f"High AZC tertile: Line-1 PP fraction = {100*high_pp_frac:.1f}%")

# Per-folio PP fractions for statistical test
def get_pp_fractions(folio_list):
    fracs = []
    for f in folio_list:
        if len(f['line1_ht']) > 0:
            pp_count = sum(1 for m in f['line1_ht'] if m in all_a_middles)
            fracs.append(pp_count / len(f['line1_ht']))
    return fracs

low_fracs = get_pp_fractions(low_azc)
med_fracs = get_pp_fractions(med_azc)
high_fracs = get_pp_fractions(high_azc)

kw_stat, kw_p = stats.kruskal(low_fracs, med_fracs, high_fracs)
print(f"\nKruskal-Wallis: H = {kw_stat:.2f}, p = {kw_p:.4f}")

# Mann-Whitney U for low vs high
mw_stat, mw_p = stats.mannwhitneyu(low_fracs, high_fracs, alternative='two-sided')
print(f"Mann-Whitney (low vs high): U = {mw_stat:.0f}, p = {mw_p:.4f}")

# ============================================================
# TEST 2: A-context prediction accuracy by AZC tertile
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: A-CONTEXT PREDICTION BY AZC TERTILE")
print("=" * 70)

def predict_a_from_line1(folio_list):
    """Use line-1 PP MIDDLEs to predict best-match A folio."""
    correct = 0
    total = 0

    for f in folio_list:
        line1_ht = set(f['line1_ht'])
        line1_pp = line1_ht & all_a_middles

        if len(line1_pp) < 2:
            continue

        true_best = f['best_a']

        # Predict: which A folio has highest overlap with line1_pp?
        best_overlap = -1
        predicted_a = None
        for a_fol in a_folios:
            overlap = len(line1_pp & a_folio_pools[a_fol])
            if overlap > best_overlap:
                best_overlap = overlap
                predicted_a = a_fol

        total += 1
        if predicted_a == true_best:
            correct += 1

    return correct, total

low_correct, low_total = predict_a_from_line1(low_azc)
med_correct, med_total = predict_a_from_line1(med_azc)
high_correct, high_total = predict_a_from_line1(high_azc)

random_baseline = 1 / len(a_folios)

print(f"\nLow AZC tertile: {low_correct}/{low_total} = {100*low_correct/low_total if low_total else 0:.1f}% (lift: {(low_correct/low_total)/random_baseline if low_total else 0:.1f}x)")
print(f"Medium AZC tertile: {med_correct}/{med_total} = {100*med_correct/med_total if med_total else 0:.1f}% (lift: {(med_correct/med_total)/random_baseline if med_total else 0:.1f}x)")
print(f"High AZC tertile: {high_correct}/{high_total} = {100*high_correct/high_total if high_total else 0:.1f}% (lift: {(high_correct/high_total)/random_baseline if high_total else 0:.1f}x)")
print(f"\nRandom baseline: {100*random_baseline:.2f}%")

# Chi-squared test for prediction accuracy difference
contingency = [[low_correct, low_total - low_correct],
               [high_correct, high_total - high_correct]]
chi2, chi_p, _, _ = stats.chi2_contingency(contingency)
print(f"\nChi-squared (low vs high accuracy): chi2 = {chi2:.2f}, p = {chi_p:.4f}")

# ============================================================
# TEST 3: Does AZC provide additional prediction beyond A?
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: AZC AS ADDITIONAL PREDICTOR")
print("=" * 70)

# Can we use AZC-mediated MIDDLEs in line-1 to improve prediction?
# Hypothesis: Line-1 MIDDLEs in both A AND AZC are more predictive

def predict_with_azc_overlap(folio_list):
    """Use line-1 MIDDLEs that are in BOTH A and AZC to predict."""
    correct = 0
    total = 0

    for f in folio_list:
        line1_ht = set(f['line1_ht'])
        # MIDDLEs in both A and AZC
        line1_both = line1_ht & all_a_middles & azc_middles

        if len(line1_both) < 2:
            continue

        true_best = f['best_a']

        best_overlap = -1
        predicted_a = None
        for a_fol in a_folios:
            overlap = len(line1_both & a_folio_pools[a_fol])
            if overlap > best_overlap:
                best_overlap = overlap
                predicted_a = a_fol

        total += 1
        if predicted_a == true_best:
            correct += 1

    return correct, total

both_correct, both_total = predict_with_azc_overlap(folio_metrics)
a_only_correct, a_only_total = predict_a_from_line1(folio_metrics)

print(f"\nA-only prediction: {a_only_correct}/{a_only_total} = {100*a_only_correct/a_only_total if a_only_total else 0:.1f}%")
print(f"A+AZC prediction: {both_correct}/{both_total} = {100*both_correct/both_total if both_total else 0:.1f}%")

if both_total > 0 and a_only_total > 0:
    a_only_acc = a_only_correct / a_only_total
    both_acc = both_correct / both_total
    print(f"\nDifference: {100*(both_acc - a_only_acc):+.1f} percentage points")

# ============================================================
# TEST 4: AZC-exclusive line-1 vocabulary
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: AZC-EXCLUSIVE LINE-1 VOCABULARY")
print("=" * 70)

# Are there line-1 MIDDLEs that are in AZC but NOT in A?
azc_only = azc_middles - all_a_middles
print(f"\nAZC-only MIDDLEs (in AZC, not in A): {len(azc_only)}")

azc_only_in_line1 = []
for f in folio_metrics:
    for mid in f['line1_ht']:
        if mid in azc_only:
            azc_only_in_line1.append(mid)

print(f"AZC-only MIDDLEs appearing in line-1 HT: {len(set(azc_only_in_line1))} types, {len(azc_only_in_line1)} tokens")

if azc_only_in_line1:
    azc_only_counter = Counter(azc_only_in_line1)
    print(f"\nMost common AZC-only line-1 MIDDLEs:")
    for mid, count in azc_only_counter.most_common(10):
        print(f"  '{mid}': {count}")

# Save results
output = {
    'line1_pp_fraction_by_tertile': {
        'low_azc': float(low_pp_frac),
        'med_azc': float(med_pp_frac),
        'high_azc': float(high_pp_frac),
        'kruskal_wallis_H': float(kw_stat),
        'kruskal_wallis_p': float(kw_p),
    },
    'a_context_prediction_by_tertile': {
        'low_azc': {'correct': low_correct, 'total': low_total},
        'med_azc': {'correct': med_correct, 'total': med_total},
        'high_azc': {'correct': high_correct, 'total': high_total},
        'chi2_low_vs_high': float(chi2),
        'chi2_p': float(chi_p),
    },
    'azc_additional_prediction': {
        'a_only': {'correct': a_only_correct, 'total': a_only_total},
        'a_plus_azc': {'correct': both_correct, 'total': both_total},
    },
    'azc_only_in_line1': {
        'types': len(set(azc_only_in_line1)),
        'tokens': len(azc_only_in_line1),
    },
}

output_path = PROJECT_ROOT / 'phases' / 'PP_HT_AZC_INTERACTION' / 'results' / 't2_line1_azc_modulation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

print(f"""
LINE-1 PP FRACTION:
  Low AZC: {100*low_pp_frac:.1f}%
  High AZC: {100*high_pp_frac:.1f}%
  Difference: {100*(high_pp_frac - low_pp_frac):+.1f}pp
  Kruskal-Wallis p = {kw_p:.4f} {'(SIGNIFICANT)' if kw_p < 0.05 else '(not significant)'}

A-CONTEXT PREDICTION:
  Low AZC: {100*low_correct/low_total if low_total else 0:.1f}% ({low_correct}/{low_total})
  High AZC: {100*high_correct/high_total if high_total else 0:.1f}% ({high_correct}/{high_total})
  Chi-squared p = {chi_p:.4f} {'(SIGNIFICANT)' if chi_p < 0.05 else '(not significant)'}

AZC MODULATION OF LINE-1:
  {'AZC mediation level DOES affect line-1 structure' if kw_p < 0.05 or chi_p < 0.05 else 'AZC mediation level does NOT significantly affect line-1 structure'}
""")
