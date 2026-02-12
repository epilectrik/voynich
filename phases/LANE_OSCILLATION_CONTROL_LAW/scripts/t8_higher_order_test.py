#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8: Higher-Order Dependency Test

Tests whether EN lane sequences contain higher-order dependencies (2nd/3rd order
Markov) not captured by the first-order transition matrix from T1.

Method:
  - 2nd-order transition probabilities: P(lane_i | lane_{i-1}, lane_{i-2})
  - Conditional mutual information: I(lane_i; lane_{i-2} | lane_{i-1})
  - Run-length distribution vs geometric (memoryless) fit
  - Run-length hazard function (constant = memoryless)
  - Trigram frequency analysis vs first-order prediction

Criteria:
  - First-order sufficient: chi-sq p > 0.05 for all conditioning states,
    MI < 0.01 bits, run lengths fit geometric (p > 0.05), flat hazard function
  - Higher-order detected: document specific higher-order patterns
"""

import json
import math
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import chi2

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare (same pattern as T1)
# ============================================================
print("=" * 60)
print("T8: Higher-Order Dependency Test")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data with full annotations
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = token_to_class.get(w)
    m = morph.extract(w)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False

    lines[(token.folio, token.line)].append({
        'word': w,
        'class': cls,
        'en_subfamily': en_subfamily,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'section': token.section,
        'folio': token.folio,
    })

print(f"B lines: {len(lines)}")

# ============================================================
# SECTION 2: Build EN Sequences (MIN_EN = 4 for trigrams)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Build EN Sequences (MIN_EN = 4)")
print("=" * 60)

MIN_EN = 4  # Need at least 4 EN tokens for meaningful trigrams

en_line_data = []
for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue

        # Check if within 2 positions of hazard or CC
        near_haz = False
        near_cc = False
        for j in range(max(0, i - 2), min(len(toks), i + 3)):
            if j == i:
                continue
            if toks[j]['is_haz']:
                near_haz = True
            if toks[j]['is_cc']:
                near_cc = True

        en_positions.append({
            'pos': i,
            'lane': t['en_subfamily'],
            'near_haz': near_haz,
            'near_cc': near_cc,
        })

    if len(en_positions) >= MIN_EN:
        en_line_data.append({
            'folio': folio,
            'line': line_num,
            'section': toks[0]['section'],
            'en_positions': en_positions,
            'en_seq': [e['lane'] for e in en_positions],
        })

n_lines = len(en_line_data)
n_en = sum(len(d['en_seq']) for d in en_line_data)
print(f"Lines with >= {MIN_EN} EN tokens: {n_lines}")
print(f"Total EN tokens in sequences: {n_en}")

# Extract filtered lane sequences (excluding hazard/CC-adjacent)
filtered_seqs = []
for d in en_line_data:
    seq = d['en_positions']
    filt = [e['lane'] for e in seq if not e['near_haz'] and not e['near_cc']]
    if len(filt) >= MIN_EN:
        filtered_seqs.append(filt)

n_filtered_lines = len(filtered_seqs)
n_filtered_tokens = sum(len(s) for s in filtered_seqs)
print(f"Filtered lines with >= {MIN_EN} tokens: {n_filtered_lines}")
print(f"Filtered EN tokens: {n_filtered_tokens}")


# ============================================================
# SECTION 3: First-Order Baseline (from data, not T1 file)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: First-Order Baseline")
print("=" * 60)

# Count first-order transitions (bigrams)
bigram_counts = Counter()
unigram_counts = Counter()

for seq in filtered_seqs:
    for i, lane in enumerate(seq):
        unigram_counts[lane] += 1
        if i > 0:
            bigram_counts[(seq[i - 1], lane)] += 1

total_bigrams = sum(bigram_counts.values())
total_unigrams = sum(unigram_counts.values())

# First-order transition probabilities (MLE, no smoothing for tests)
p1 = {}
for prev in ['QO', 'CHSH']:
    row_total = sum(bigram_counts[(prev, nxt)] for nxt in ['QO', 'CHSH'])
    p1[prev] = {}
    for nxt in ['QO', 'CHSH']:
        p1[prev][nxt] = bigram_counts[(prev, nxt)] / row_total if row_total > 0 else 0.5

print(f"First-order transition probabilities (MLE):")
print(f"  P(QO|QO)   = {p1['QO']['QO']:.4f}   P(CHSH|QO)   = {p1['QO']['CHSH']:.4f}")
print(f"  P(QO|CHSH) = {p1['CHSH']['QO']:.4f}   P(CHSH|CHSH) = {p1['CHSH']['CHSH']:.4f}")
print(f"  Total bigrams: {total_bigrams}")


# ============================================================
# SECTION 4: 2nd-Order Transition Probabilities
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: 2nd-Order Transition Probabilities")
print("=" * 60)

# Count trigrams
trigram_counts = Counter()
for seq in filtered_seqs:
    for i in range(2, len(seq)):
        trigram_counts[(seq[i - 2], seq[i - 1], seq[i])] += 1

total_trigrams = sum(trigram_counts.values())
print(f"Total trigrams: {total_trigrams}")

# 2nd-order transition: P(lane_i | lane_{i-1}, lane_{i-2})
# Conditioning states: QQ, QC, CQ, CC
conditioning_labels = {
    ('QO', 'QO'): 'QQ',
    ('QO', 'CHSH'): 'QC',
    ('CHSH', 'QO'): 'CQ',
    ('CHSH', 'CHSH'): 'CC',
}

second_order = {}
second_order_chi2_tests = {}

print("\n2nd-order transition probabilities:")
for (prev2, prev1), label in conditioning_labels.items():
    # Count P(next | prev2, prev1)
    count_next_qo = trigram_counts[(prev2, prev1, 'QO')]
    count_next_chsh = trigram_counts[(prev2, prev1, 'CHSH')]
    total_cond = count_next_qo + count_next_chsh

    if total_cond > 0:
        p2_qo = count_next_qo / total_cond
        p2_chsh = count_next_chsh / total_cond
    else:
        p2_qo = 0.5
        p2_chsh = 0.5

    # First-order comparison: P(next | prev1) only
    p1_qo = p1[prev1]['QO']
    p1_chsh = p1[prev1]['CHSH']

    second_order[label] = {
        'conditioning_state': f"{prev2}->{prev1}",
        'count_total': int(total_cond),
        'count_next_QO': int(count_next_qo),
        'count_next_CHSH': int(count_next_chsh),
        'P_QO_given_context': float(p2_qo),
        'P_CHSH_given_context': float(p2_chsh),
        'P_QO_first_order': float(p1_qo),
        'P_CHSH_first_order': float(p1_chsh),
    }

    print(f"\n  Conditioning: {label} ({prev2}->{prev1}), n={total_cond}")
    print(f"    P(QO|{label})   = {p2_qo:.4f}  (1st-order: {p1_qo:.4f})")
    print(f"    P(CHSH|{label}) = {p2_chsh:.4f}  (1st-order: {p1_chsh:.4f})")

    # Chi-squared test: does knowing lane_{i-2} add info beyond lane_{i-1}?
    # Compare observed (count_next_qo, count_next_chsh) to expected under 1st-order
    if total_cond > 0:
        expected_qo = p1_qo * total_cond
        expected_chsh = p1_chsh * total_cond

        # Chi-squared statistic (df=1: 2 categories - 1)
        chi2_stat = 0
        if expected_qo > 0:
            chi2_stat += (count_next_qo - expected_qo) ** 2 / expected_qo
        if expected_chsh > 0:
            chi2_stat += (count_next_chsh - expected_chsh) ** 2 / expected_chsh

        p_value = float(1 - chi2.cdf(chi2_stat, df=1))

        second_order_chi2_tests[label] = {
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'df': 1,
            'significant': bool(p_value < 0.05),
            'expected_QO': float(expected_qo),
            'expected_CHSH': float(expected_chsh),
        }

        status = "SIGNIFICANT" if p_value < 0.05 else "not significant"
        print(f"    Chi-sq = {chi2_stat:.4f}, p = {p_value:.4f} ({status})")
    else:
        second_order_chi2_tests[label] = {
            'chi2_statistic': None,
            'p_value': None,
            'df': 1,
            'significant': False,
            'note': 'zero observations for this conditioning state',
        }
        print(f"    No observations for this conditioning state")


# ============================================================
# SECTION 5: Conditional Mutual Information
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Conditional Mutual Information")
print("=" * 60)

# I(lane_i; lane_{i-2} | lane_{i-1})
# = sum_{x,y,z} P(x,y,z) * log[ P(z|x,y) / P(z|y) ]
# where x=lane_{i-2}, y=lane_{i-1}, z=lane_i
#
# Using empirical probabilities from trigram counts.
# +1 smoothing for MI only to avoid log(0).

states = ['QO', 'CHSH']

# Smoothed counts for MI computation
smoothed_trigram_counts = Counter()
for x in states:
    for y in states:
        for z in states:
            smoothed_trigram_counts[(x, y, z)] = trigram_counts[(x, y, z)] + 1

smoothed_total = sum(smoothed_trigram_counts.values())

# P(x, y, z) from smoothed trigrams
p_xyz = {}
for x in states:
    for y in states:
        for z in states:
            p_xyz[(x, y, z)] = smoothed_trigram_counts[(x, y, z)] / smoothed_total

# P(y, z) = sum_x P(x, y, z)
p_yz = {}
for y in states:
    for z in states:
        p_yz[(y, z)] = sum(p_xyz[(x, y, z)] for x in states)

# P(x, y) = sum_z P(x, y, z)
p_xy = {}
for x in states:
    for y in states:
        p_xy[(x, y)] = sum(p_xyz[(x, y, z)] for z in states)

# P(y) = sum_z P(y, z)
p_y = {}
for y in states:
    p_y[y] = sum(p_yz[(y, z)] for z in states)

# CMI = sum P(x,y,z) * log[ P(z|x,y) * P(y) / (P(z|y) * P(y)) ]
#     = sum P(x,y,z) * log[ P(x,y,z) * P(y) / (P(x,y) * P(y,z)) ]
# (using the identity for conditional MI)
cmi_nats = 0.0
for x in states:
    for y in states:
        for z in states:
            pxyz = p_xyz[(x, y, z)]
            pxy = p_xy[(x, y)]
            pyz = p_yz[(y, z)]
            py = p_y[y]

            if pxyz > 0 and pxy > 0 and pyz > 0 and py > 0:
                cmi_nats += pxyz * math.log(pxyz * py / (pxy * pyz))

# Convert nats to bits
cmi_bits = cmi_nats / math.log(2)

print(f"Conditional Mutual Information I(lane_i; lane_{{i-2}} | lane_{{i-1}}):")
print(f"  CMI = {cmi_bits:.6f} bits")
print(f"  Threshold: < 0.01 bits for first-order sufficiency")
cmi_ok = cmi_bits < 0.01
print(f"  Result: {'PASS (near zero)' if cmi_ok else 'FAIL (significant higher-order info)'}")


# ============================================================
# SECTION 6: Run-Length Distribution vs Geometric
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Run-Length Distribution vs Geometric")
print("=" * 60)

# Extract run lengths from filtered sequences
run_lengths = {'QO': [], 'CHSH': []}

for seq in filtered_seqs:
    if not seq:
        continue
    current_lane = seq[0]
    current_run = 1
    for i in range(1, len(seq)):
        if seq[i] == current_lane:
            current_run += 1
        else:
            run_lengths[current_lane].append(current_run)
            current_lane = seq[i]
            current_run = 1
    # Last run in the sequence (right-censored: we include it but note this)
    run_lengths[current_lane].append(current_run)

run_length_results = {}
run_length_hazard = {}

for lane in ['QO', 'CHSH']:
    runs = run_lengths[lane]
    n_runs = len(runs)
    if n_runs == 0:
        continue

    # Self-transition probability from first-order model
    p_self = p1[lane][lane]
    # For geometric distribution: P(run=k) = p_self^(k-1) * (1-p_self)
    # Mean = 1 / (1-p_self)

    observed_mean = float(np.mean(runs))
    theoretical_mean = 1.0 / (1.0 - p_self) if p_self < 1.0 else float('inf')
    max_run = max(runs)

    print(f"\n  {lane} runs: n={n_runs}, max={max_run}")
    print(f"    Observed mean:    {observed_mean:.4f}")
    print(f"    Theoretical mean: {theoretical_mean:.4f} (geometric with p_self={p_self:.4f})")

    # Build observed histogram
    run_hist = Counter(runs)
    # Bin runs: 1, 2, 3, 4, 5+
    bins = list(range(1, 6))  # [1, 2, 3, 4, 5]
    observed = []
    expected = []

    for k in bins[:-1]:  # k=1,2,3,4
        observed.append(run_hist.get(k, 0))
        # P(run=k) = p_self^(k-1) * (1-p_self)
        expected.append(n_runs * (p_self ** (k - 1)) * (1 - p_self))

    # k=5+ (lumped tail)
    obs_5plus = sum(run_hist.get(k, 0) for k in range(5, max_run + 1))
    observed.append(obs_5plus)
    # P(run >= 5) = p_self^4
    expected.append(n_runs * (p_self ** 4))

    bin_labels = ['1', '2', '3', '4', '5+']

    print(f"    Run-length histogram:")
    print(f"      {'Bin':>5s}  {'Obs':>6s}  {'Exp':>8s}")
    for bl, o, e in zip(bin_labels, observed, expected):
        print(f"      {bl:>5s}  {o:>6d}  {e:>8.1f}")

    # Chi-squared goodness of fit
    # Pool bins with expected < 5 from the tail
    obs_pooled = list(observed)
    exp_pooled = list(expected)

    # Pool from tail until all expected >= 5
    while len(exp_pooled) > 2 and exp_pooled[-1] < 5:
        obs_pooled[-2] += obs_pooled[-1]
        exp_pooled[-2] += exp_pooled[-1]
        obs_pooled.pop()
        exp_pooled.pop()

    # Compute chi-squared
    chi2_stat = 0
    for o, e in zip(obs_pooled, exp_pooled):
        if e > 0:
            chi2_stat += (o - e) ** 2 / e

    # df = number of bins - 1 (parameter p_self estimated from data, so -1 more = bins-2)
    # But we use the MLE from bigrams (not from run lengths), so we don't subtract for parameter estimation
    df_run = len(obs_pooled) - 1
    p_value_run = float(1 - chi2.cdf(chi2_stat, df=df_run)) if df_run > 0 else 1.0

    status = "FITS GEOMETRIC" if p_value_run > 0.05 else "DEPARTS FROM GEOMETRIC"
    print(f"    Chi-sq goodness of fit: {chi2_stat:.4f}, df={df_run}, p={p_value_run:.4f} ({status})")

    # Hazard function: h(k) = n_runs_ending_at_k / n_runs_at_least_k
    # For geometric: h(k) = 1 - p_self (constant)
    hazard_data = []
    for k in range(1, max_run + 1):
        n_ending_at_k = run_hist.get(k, 0)
        n_at_least_k = sum(run_hist.get(j, 0) for j in range(k, max_run + 1))
        h_k = n_ending_at_k / n_at_least_k if n_at_least_k > 0 else 0
        hazard_data.append({
            'k': int(k),
            'n_ending_at_k': int(n_ending_at_k),
            'n_at_least_k': int(n_at_least_k),
            'hazard_rate': float(h_k),
            'theoretical_hazard': float(1 - p_self),
        })

    # Test hazard flatness: coefficient of variation of hazard rates where n_at_least_k >= 10
    reliable_hazards = [h['hazard_rate'] for h in hazard_data if h['n_at_least_k'] >= 10]
    if len(reliable_hazards) >= 2:
        hz_mean = float(np.mean(reliable_hazards))
        hz_std = float(np.std(reliable_hazards))
        hz_cv = hz_std / hz_mean if hz_mean > 0 else 0
        hazard_flat = hz_cv < 0.2  # CV < 0.2 is approximately flat
    else:
        hz_mean = float(np.mean(reliable_hazards)) if reliable_hazards else 0
        hz_std = 0
        hz_cv = 0
        hazard_flat = True  # Insufficient data to reject flatness

    print(f"    Hazard function (theoretical constant = {1 - p_self:.4f}):")
    for h in hazard_data:
        marker = " *" if h['n_at_least_k'] < 10 else ""
        print(f"      k={h['k']:2d}: h(k)={h['hazard_rate']:.4f} (n>={h['n_at_least_k']:4d}){marker}")
    print(f"    Hazard CV (reliable points): {hz_cv:.4f} ({'FLAT' if hazard_flat else 'NOT FLAT'})")

    run_length_results[lane] = {
        'n_runs': int(n_runs),
        'max_run': int(max_run),
        'observed_mean': float(observed_mean),
        'theoretical_mean': float(theoretical_mean),
        'p_self': float(p_self),
        'histogram': {bl: int(o) for bl, o in zip(bin_labels, observed)},
        'expected_histogram': {bl: float(e) for bl, e in zip(bin_labels, expected)},
        'chi2_goodness_of_fit': {
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value_run),
            'df': int(df_run),
            'n_bins_after_pooling': len(obs_pooled),
            'fits_geometric': bool(p_value_run > 0.05),
        },
        'hazard_function': {
            'data_points': hazard_data,
            'theoretical_constant': float(1 - p_self),
            'reliable_mean': float(hz_mean),
            'reliable_std': float(hz_std),
            'reliable_cv': float(hz_cv),
            'is_flat': bool(hazard_flat),
        },
    }
    run_length_hazard[lane] = hazard_data


# ============================================================
# SECTION 7: Trigram Frequency Analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Trigram Frequency Analysis")
print("=" * 60)

# All 8 possible trigrams
all_trigrams = []
for x in states:
    for y in states:
        for z in states:
            all_trigrams.append((x, y, z))

# Build short labels
def trigram_label(x, y, z):
    return ('Q' if x == 'QO' else 'C') + ('Q' if y == 'QO' else 'C') + ('Q' if z == 'QO' else 'C')

# Observed trigram counts (unsmoothed)
observed_trigrams = {}
for tri in all_trigrams:
    label = trigram_label(*tri)
    observed_trigrams[label] = trigram_counts[tri]

# Expected under first-order: P(trigram xyz) = P(x) * P(y|x) * P(z|y)
# where P(x) is the stationary distribution
# More directly: expected count = N_trigrams * P(x,y) * P(z|y) / sum...
# Actually: for a first-order chain, P(x,y,z) = P(x,y) * P(z|y)
# and P(x,y) = count(x,y) / total_bigrams
# So expected trigram count = total_trigrams * [bigram_count(x,y)/total_bigrams] * P(z|y)

expected_trigrams = {}
for tri in all_trigrams:
    x, y, z = tri
    label = trigram_label(x, y, z)
    # P(x,y) from bigrams
    p_xy_val = bigram_counts[(x, y)] / total_bigrams if total_bigrams > 0 else 0.25
    # P(z|y) from first-order
    p_z_given_y = p1[y][z]
    expected_trigrams[label] = total_trigrams * p_xy_val * p_z_given_y

print(f"Total trigrams: {total_trigrams}")
print(f"\n  {'Trigram':>8s}  {'Observed':>8s}  {'Expected':>8s}  {'O-E':>8s}  {'(O-E)^2/E':>10s}")
print(f"  {'-'*8:>8s}  {'-'*8:>8s}  {'-'*8:>8s}  {'-'*8:>8s}  {'-'*10:>10s}")

chi2_trigram_stat = 0
trigram_details = {}
for tri in all_trigrams:
    label = trigram_label(*tri)
    obs = observed_trigrams[label]
    exp = expected_trigrams[label]
    diff = obs - exp
    contrib = (diff ** 2) / exp if exp > 0 else 0
    chi2_trigram_stat += contrib
    trigram_details[label] = {
        'observed': int(obs),
        'expected': float(exp),
        'residual': float(diff),
        'chi2_contribution': float(contrib),
    }
    print(f"  {label:>8s}  {obs:>8d}  {exp:>8.1f}  {diff:>+8.1f}  {contrib:>10.4f}")

# df = 8 trigrams - 4 bigram parameters + 0 = 8 - 1 = 4
# Actually: 8 cells, we estimated 2 independent transition probabilities from bigrams
# (QO->QO, CHSH->QO; the others are complements), and 2 independent bigram marginals
# But the expected values are derived from first-order model which has 2 free params
# (the two transition probabilities, since row sums=1).
# Standard: df = (n_cells - 1) - n_estimated_params
# We have 8 cells, so df = 7 - 2 (two free transition params) = 5
# However, since we also condition on observed bigram counts (P(x,y)),
# the effective df is: 8 - 4 (one per bigram type) = 4
# Each bigram (x,y) contributes 1 df (split into z=QO vs z=CHSH), so df=4
df_trigram = 4
p_value_trigram = float(1 - chi2.cdf(chi2_trigram_stat, df=df_trigram))

status = "FITS FIRST-ORDER" if p_value_trigram > 0.05 else "DEPARTS FROM FIRST-ORDER"
print(f"\n  Trigram chi-sq: {chi2_trigram_stat:.4f}, df={df_trigram}, p={p_value_trigram:.4f} ({status})")


# ============================================================
# SECTION 8: Overall Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: Overall Verdict")
print("=" * 60)

# Collect all evidence
any_conditioning_significant = any(
    second_order_chi2_tests[label].get('significant', False)
    for label in second_order_chi2_tests
)

run_geometric_pass = all(
    run_length_results[lane]['chi2_goodness_of_fit']['fits_geometric']
    for lane in run_length_results
)

hazard_flat_pass = all(
    run_length_results[lane]['hazard_function']['is_flat']
    for lane in run_length_results
)

trigram_pass = p_value_trigram > 0.05

evidence_summary = {
    'conditioning_tests_all_nonsignificant': bool(not any_conditioning_significant),
    'cmi_below_threshold': bool(cmi_ok),
    'run_lengths_fit_geometric': bool(run_geometric_pass),
    'hazard_functions_flat': bool(hazard_flat_pass),
    'trigram_fit_first_order': bool(trigram_pass),
}

first_order_sufficient = all(evidence_summary.values())
verdict = 'FIRST_ORDER_SUFFICIENT' if first_order_sufficient else 'HIGHER_ORDER_DETECTED'

print(f"\nEvidence summary:")
for test, passed in evidence_summary.items():
    print(f"  {test}: {'PASS' if passed else 'FAIL'}")
print(f"\nVERDICT: {verdict}")

# Document specific higher-order patterns if detected
higher_order_patterns = []
if any_conditioning_significant:
    for label, test in second_order_chi2_tests.items():
        if test.get('significant', False):
            so = second_order[label]
            higher_order_patterns.append(
                f"Conditioning state {label}: P(QO|{label})={so['P_QO_given_context']:.4f} "
                f"vs P(QO|{label[-1]})={so['P_QO_first_order']:.4f} "
                f"(chi2={test['chi2_statistic']:.4f}, p={test['p_value']:.4f})"
            )
if not run_geometric_pass:
    for lane in run_length_results:
        rl = run_length_results[lane]
        if not rl['chi2_goodness_of_fit']['fits_geometric']:
            higher_order_patterns.append(
                f"{lane} run lengths depart from geometric "
                f"(chi2={rl['chi2_goodness_of_fit']['chi2_statistic']:.4f}, "
                f"p={rl['chi2_goodness_of_fit']['p_value']:.4f})"
            )
if not hazard_flat_pass:
    for lane in run_length_results:
        rl = run_length_results[lane]
        if not rl['hazard_function']['is_flat']:
            higher_order_patterns.append(
                f"{lane} hazard function not flat (CV={rl['hazard_function']['reliable_cv']:.4f})"
            )
if not trigram_pass:
    higher_order_patterns.append(
        f"Trigram frequencies depart from first-order prediction "
        f"(chi2={chi2_trigram_stat:.4f}, p={p_value_trigram:.4f})"
    )

if higher_order_patterns:
    print(f"\nHigher-order patterns detected:")
    for pattern in higher_order_patterns:
        print(f"  - {pattern}")


# ============================================================
# SECTION 9: Save Results
# ============================================================
print("\n" + "=" * 60)
print("SECTION 9: Save Results")
print("=" * 60)

results = {
    'test': 'T8_higher_order_dependency',
    'description': 'Test for higher-order (2nd/3rd order Markov) dependencies in EN lane sequences',
    'data_summary': {
        'min_en_per_line': int(MIN_EN),
        'n_lines': int(n_lines),
        'n_filtered_lines': int(n_filtered_lines),
        'n_en_tokens': int(n_en),
        'n_filtered_tokens': int(n_filtered_tokens),
        'n_bigrams': int(total_bigrams),
        'n_trigrams': int(total_trigrams),
    },
    'first_order_baseline': {
        'QO_to_QO': float(p1['QO']['QO']),
        'QO_to_CHSH': float(p1['QO']['CHSH']),
        'CHSH_to_QO': float(p1['CHSH']['QO']),
        'CHSH_to_CHSH': float(p1['CHSH']['CHSH']),
    },
    'second_order_transitions': second_order,
    'second_order_chi2_tests': second_order_chi2_tests,
    'conditional_mutual_information': {
        'cmi_bits': float(cmi_bits),
        'threshold': 0.01,
        'below_threshold': bool(cmi_ok),
    },
    'run_length_analysis': run_length_results,
    'trigram_analysis': {
        'total_trigrams': int(total_trigrams),
        'trigram_details': trigram_details,
        'chi2_goodness_of_fit': {
            'chi2_statistic': float(chi2_trigram_stat),
            'p_value': float(p_value_trigram),
            'df': int(df_trigram),
            'fits_first_order': bool(trigram_pass),
        },
    },
    'evidence_summary': evidence_summary,
    'higher_order_patterns': higher_order_patterns,
    'verdict': verdict,
}

out_path = RESULTS_DIR / 't8_higher_order.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")
print(f"\nT8 VERDICT: {verdict}")
