"""
Test 2: Paragraph Kernel x MIDDLE Tier Interaction

Question: Do paragraph kernel types (HIGH_K, HIGH_H, BALANCED) use different MIDDLE tiers?

From C893:
- HIGH_K paragraphs = recovery procedures (2x FQ rate)
- HIGH_H paragraphs = active distillation
- BALANCED = general procedures

Hypothesis:
- HIGH_K (recovery) should use more EARLY prep MIDDLEs (re-preparation after failure)
- HIGH_H (active distillation) should use more MID thermodynamic MIDDLEs
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import re
import re

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Define tiers
EARLY_MIDDLES = {'ksh', 'lch', 'tch', 'pch', 'te'}
MID_MIDDLES = {'k', 't', 'e'}
LATE_MIDDLES = {'ke', 'kch'}

# Group tokens by folio-line (use line as paragraph proxy)
# Lines starting with same digit are often in same paragraph
by_para = defaultdict(list)
for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix and m.prefix in HT_PREFIXES:
        continue
    # Use line number as paragraph proxy (group consecutive lines)
    try:
        line_num = int(re.match(r'(\d+)', str(t.line)).group(1)) if re.match(r'(\d+)', str(t.line)) else 0
    except:
        line_num = 0
    # Group into 5-line paragraphs
    para_num = line_num // 5
    para_key = (t.folio, para_num)
    by_para[para_key].append(t)

# Classify paragraphs by kernel profile
def get_kernel_type(tokens):
    k_count = 0
    h_count = 0
    for t in tokens:
        m = morph.extract(t.word)
        if not m.middle:
            continue
        if m.middle == 'k' or m.middle.startswith('k'):
            k_count += 1
        if 'h' in t.word or m.middle == 'h':
            h_count += 1

    total = k_count + h_count
    if total < 5:
        return None

    k_ratio = k_count / total
    if k_ratio > 0.6:
        return 'HIGH_K'
    elif k_ratio < 0.4:
        return 'HIGH_H'
    else:
        return 'BALANCED'

# Analyze tier distribution by kernel type
tier_by_kernel = defaultdict(lambda: {'early': 0, 'mid': 0, 'late': 0, 'total': 0})

for para_key, tokens in by_para.items():
    kernel_type = get_kernel_type(tokens)
    if kernel_type is None:
        continue

    for t in tokens:
        m = morph.extract(t.word)
        if not m.middle:
            continue

        tier_by_kernel[kernel_type]['total'] += 1
        if m.middle in EARLY_MIDDLES:
            tier_by_kernel[kernel_type]['early'] += 1
        elif m.middle in MID_MIDDLES:
            tier_by_kernel[kernel_type]['mid'] += 1
        elif m.middle in LATE_MIDDLES:
            tier_by_kernel[kernel_type]['late'] += 1

print("=" * 70)
print("TEST 2: PARAGRAPH KERNEL x MIDDLE TIER INTERACTION")
print("=" * 70)
print()
print("Question: Do HIGH_K, HIGH_H, and BALANCED paragraphs use different MIDDLE tiers?")
print()

print("TIER DISTRIBUTION BY PARAGRAPH KERNEL TYPE:")
print("-" * 70)
print(f"{'Kernel Type':<12} {'N':<8} {'EARLY %':<12} {'MID %':<12} {'LATE %':<12}")
print("-" * 70)

results_table = []
for ktype in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    data = tier_by_kernel[ktype]
    n = data['total']
    if n == 0:
        continue
    early_pct = data['early'] / n * 100
    mid_pct = data['mid'] / n * 100
    late_pct = data['late'] / n * 100

    print(f"{ktype:<12} {n:<8} {early_pct:<12.1f} {mid_pct:<12.1f} {late_pct:<12.1f}")
    results_table.append({
        'kernel_type': ktype,
        'n': n,
        'early_pct': early_pct,
        'mid_pct': mid_pct,
        'late_pct': late_pct
    })

print()

# Chi-square test
from scipy import stats
import numpy as np

# Build contingency table
observed = []
for ktype in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    data = tier_by_kernel[ktype]
    if data['total'] > 0:
        observed.append([data['early'], data['mid'], data['late']])

if len(observed) >= 2:
    observed = np.array(observed)
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    print("CHI-SQUARE TEST (Kernel Type x MIDDLE Tier):")
    print("-" * 50)
    print(f"  Chi-square: {chi2:.2f}")
    print(f"  df: {dof}")
    print(f"  p-value: {p_value:.6f}")
    print()

    # Effect size (Cramer's V)
    n_total = observed.sum()
    min_dim = min(observed.shape) - 1
    cramers_v = np.sqrt(chi2 / (n_total * min_dim))
    print(f"  Cramer's V: {cramers_v:.3f}")
    print()
else:
    chi2, p_value, cramers_v = None, None, None

# Key comparisons
print("KEY COMPARISONS:")
print("-" * 50)

if len(results_table) >= 2:
    high_k = next((r for r in results_table if r['kernel_type'] == 'HIGH_K'), None)
    high_h = next((r for r in results_table if r['kernel_type'] == 'HIGH_H'), None)

    if high_k and high_h:
        early_diff = high_k['early_pct'] - high_h['early_pct']
        mid_diff = high_k['mid_pct'] - high_h['mid_pct']
        print(f"  HIGH_K vs HIGH_H:")
        print(f"    EARLY tier: {'+' if early_diff > 0 else ''}{early_diff:.1f}% (HIGH_K {'more' if early_diff > 0 else 'less'} prep)")
        print(f"    MID tier:   {'+' if mid_diff > 0 else ''}{mid_diff:.1f}% (HIGH_K {'more' if mid_diff > 0 else 'less'} thermo)")

print()

# Verdict
if p_value and p_value < 0.05 and cramers_v and cramers_v > 0.1:
    verdict = "CONFIRMED"
elif p_value and p_value < 0.1:
    verdict = "SUPPORT"
else:
    verdict = "NOT SUPPORTED"

print("=" * 70)
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict in ["CONFIRMED", "SUPPORT"]:
    print("\nInterpretation: Paragraph kernel type predicts MIDDLE tier usage.")
    print("HIGH_K (recovery) and HIGH_H (active distillation) show different")
    print("MIDDLE distributions, consistent with different procedural phases.")

# Output JSON
output = {
    "test": "Paragraph Kernel x MIDDLE Tier Interaction",
    "question": "Do paragraph kernel types use different MIDDLE tiers?",
    "results": results_table,
    "statistics": {
        "chi_square": chi2,
        "p_value": p_value,
        "cramers_v": cramers_v
    },
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/paragraph_kernel_middle_tier.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/paragraph_kernel_middle_tier.json")
