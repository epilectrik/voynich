#!/usr/bin/env python3
"""
Phase 1: DA Segment-Level RI/PP Composition Analysis

Question: Do DA-segmented blocks within A records show RI/PP stratification?
If segments have different RI/PP compositions, DA may be segmenting functional
units beyond just PREFIX family runs.

Method:
1. For each A line with DA tokens, split on DA
2. For each segment, compute RI count, PP count, RI ratio
3. Measure variance of RI ratio across segments within lines
4. Compare to null model (permuted RI/PP labels within folio)

Effect Size Threshold: Cohen's d > 0.5 for meaningful stratification
"""

import json
import numpy as np
from collections import defaultdict
from scipy import stats

# Load pre-classified token data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    middle_classes = json.load(f)

# Get RI middles set
ri_middles = set(middle_classes['a_exclusive_middles'])

print("=" * 70)
print("PHASE 1: DA SEGMENT RI/PP COMPOSITION ANALYSIS")
print("=" * 70)
print()

# Group tokens by line
lines = defaultdict(list)
for t in tokens:
    line_key = (t['folio'], t['line'])
    lines[line_key].append(t)

# Sort tokens within each line by their position (maintain order)
# Token order is preserved from the file, which is already in reading order

print(f"Total A lines: {len(lines)}")

# Analyze lines with DA tokens
lines_with_da = []
lines_without_da = []

for line_key, line_tokens in lines.items():
    has_da = any(t['prefix'] == 'da' for t in line_tokens)
    if has_da:
        lines_with_da.append((line_key, line_tokens))
    else:
        lines_without_da.append((line_key, line_tokens))

print(f"Lines with DA tokens: {len(lines_with_da)}")
print(f"Lines without DA tokens: {len(lines_without_da)}")
print()

def classify_token(t, ri_middles):
    """Classify token as RI or PP based on MIDDLE"""
    return 'RI' if t['middle'] in ri_middles else 'PP'

def split_on_da(line_tokens):
    """Split line tokens into segments on DA tokens.
    DA tokens themselves are excluded from segments."""
    segments = []
    current_segment = []

    for t in line_tokens:
        if t['prefix'] == 'da':
            if current_segment:
                segments.append(current_segment)
                current_segment = []
        else:
            current_segment.append(t)

    if current_segment:
        segments.append(current_segment)

    return segments

def compute_segment_stats(segments, ri_middles):
    """Compute RI/PP stats for each segment"""
    segment_stats = []
    for seg in segments:
        ri_count = sum(1 for t in seg if t['middle'] in ri_middles)
        pp_count = len(seg) - ri_count
        total = len(seg)
        ri_ratio = ri_count / total if total > 0 else 0
        segment_stats.append({
            'ri_count': ri_count,
            'pp_count': pp_count,
            'total': total,
            'ri_ratio': ri_ratio
        })
    return segment_stats

print("=" * 70)
print("SEGMENT-LEVEL RI/PP COMPOSITION")
print("=" * 70)
print()

# Analyze segment RI/PP composition for lines with DA
all_segment_ri_ratios = []
within_line_variances = []
segment_counts = []

for line_key, line_tokens in lines_with_da:
    segments = split_on_da(line_tokens)

    if len(segments) < 2:
        # Only one segment after removing DA - skip
        continue

    stats_list = compute_segment_stats(segments, ri_middles)

    # Collect RI ratios for segments with 2+ tokens (meaningful ratios)
    ri_ratios = [s['ri_ratio'] for s in stats_list if s['total'] >= 2]

    if len(ri_ratios) >= 2:
        all_segment_ri_ratios.extend(ri_ratios)
        within_line_variances.append(np.var(ri_ratios))
        segment_counts.append(len(ri_ratios))

print(f"Lines with 2+ segments (each >=2 tokens): {len(within_line_variances)}")
print(f"Total segments analyzed: {len(all_segment_ri_ratios)}")
print()

if len(all_segment_ri_ratios) > 0:
    print(f"Segment RI ratio distribution:")
    print(f"  Mean: {np.mean(all_segment_ri_ratios):.3f}")
    print(f"  Std:  {np.std(all_segment_ri_ratios):.3f}")
    print(f"  Min:  {np.min(all_segment_ri_ratios):.3f}")
    print(f"  Max:  {np.max(all_segment_ri_ratios):.3f}")
    print()

    # Histogram of RI ratios
    print("RI ratio distribution across segments:")
    bins = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0]
    hist, _ = np.histogram(all_segment_ri_ratios, bins=bins)
    for i in range(len(bins)-1):
        bar = '#' * int(hist[i] * 50 / max(hist)) if max(hist) > 0 else ''
        print(f"  {bins[i]:.2f}-{bins[i+1]:.2f}: {hist[i]:4d} {bar}")
    print()

    print(f"Mean within-line variance of RI ratio: {np.mean(within_line_variances):.6f}")
    print(f"Median within-line variance: {np.median(within_line_variances):.6f}")
    print()

print("=" * 70)
print("NULL MODEL: PERMUTED RI/PP LABELS")
print("=" * 70)
print()

# Null model: Permute RI/PP labels within each folio, re-segment, measure variance
n_permutations = 1000
null_variances = []

# Group tokens by folio for permutation
folio_tokens = defaultdict(list)
for t in tokens:
    folio_tokens[t['folio']].append(t)

np.random.seed(42)

for perm_idx in range(n_permutations):
    # Create permuted RI/PP labels for each folio
    permuted_ri_middles = {}
    for folio, ftoks in folio_tokens.items():
        # Get all middles in this folio
        folio_middles = [t['middle'] for t in ftoks]
        # Get original RI status
        ri_status = [m in ri_middles for m in folio_middles]
        # Permute
        np.random.shuffle(ri_status)
        # Create mapping
        for i, m in enumerate(folio_middles):
            if m not in permuted_ri_middles:
                permuted_ri_middles[m] = ri_status[i]

    # Compute variance under permuted labels
    perm_variances = []
    for line_key, line_tokens in lines_with_da:
        segments = split_on_da(line_tokens)

        if len(segments) < 2:
            continue

        ri_ratios = []
        for seg in segments:
            if len(seg) < 2:
                continue
            ri_count = sum(1 for t in seg if permuted_ri_middles.get(t['middle'], False))
            ri_ratio = ri_count / len(seg)
            ri_ratios.append(ri_ratio)

        if len(ri_ratios) >= 2:
            perm_variances.append(np.var(ri_ratios))

    if perm_variances:
        null_variances.append(np.mean(perm_variances))

null_variances = np.array(null_variances)
observed_mean_var = np.mean(within_line_variances)

print(f"Observed mean within-line variance: {observed_mean_var:.6f}")
print(f"Null model mean variance: {np.mean(null_variances):.6f}")
print(f"Null model std: {np.std(null_variances):.6f}")
print()

# P-value (one-sided: is observed variance higher than null?)
p_value = np.mean(null_variances >= observed_mean_var)
print(f"P-value (observed >= null): {p_value:.4f}")

# Effect size (Cohen's d)
if np.std(null_variances) > 0:
    cohens_d = (observed_mean_var - np.mean(null_variances)) / np.std(null_variances)
    print(f"Cohen's d: {cohens_d:.3f}")
else:
    cohens_d = 0
    print("Cohen's d: undefined (null std = 0)")

print()
if cohens_d > 0.5:
    print("RESULT: Meaningful stratification detected (Cohen's d > 0.5)")
    print("DA segments show RI/PP composition differences beyond random expectation.")
elif cohens_d > 0.2:
    print("RESULT: Small stratification effect (Cohen's d > 0.2)")
    print("DA segments show weak RI/PP composition differences.")
else:
    print("RESULT: No meaningful stratification (Cohen's d <= 0.2)")
    print("DA segment RI/PP composition is consistent with random assignment.")
print()

print("=" * 70)
print("SEGMENT POSITION ANALYSIS")
print("=" * 70)
print()

# Do first vs last segments have different RI/PP composition?
first_segment_ri_ratios = []
last_segment_ri_ratios = []
middle_segment_ri_ratios = []

for line_key, line_tokens in lines_with_da:
    segments = split_on_da(line_tokens)

    if len(segments) < 2:
        continue

    stats_list = compute_segment_stats(segments, ri_middles)

    # Filter to segments with 2+ tokens
    valid_stats = [(i, s) for i, s in enumerate(stats_list) if s['total'] >= 2]

    if len(valid_stats) >= 2:
        first_segment_ri_ratios.append(valid_stats[0][1]['ri_ratio'])
        last_segment_ri_ratios.append(valid_stats[-1][1]['ri_ratio'])

        for idx, s in valid_stats[1:-1]:  # Middle segments
            middle_segment_ri_ratios.append(s['ri_ratio'])

print(f"First segments (n={len(first_segment_ri_ratios)}): mean RI ratio = {np.mean(first_segment_ri_ratios):.3f}")
print(f"Last segments (n={len(last_segment_ri_ratios)}): mean RI ratio = {np.mean(last_segment_ri_ratios):.3f}")
if middle_segment_ri_ratios:
    print(f"Middle segments (n={len(middle_segment_ri_ratios)}): mean RI ratio = {np.mean(middle_segment_ri_ratios):.3f}")
print()

# Test: First vs Last segment RI ratio
if len(first_segment_ri_ratios) > 10 and len(last_segment_ri_ratios) > 10:
    t_stat, p_val = stats.ttest_rel(first_segment_ri_ratios, last_segment_ri_ratios)
    print(f"Paired t-test (first vs last): t={t_stat:.3f}, p={p_val:.4f}")

    # Effect size
    diff = np.array(first_segment_ri_ratios) - np.array(last_segment_ri_ratios)
    d_position = np.mean(diff) / np.std(diff) if np.std(diff) > 0 else 0
    print(f"Position effect size (Cohen's d): {d_position:.3f}")
    print()

    if p_val < 0.05:
        if np.mean(first_segment_ri_ratios) > np.mean(last_segment_ri_ratios):
            print("FINDING: RI tokens concentrated in FIRST segments")
        else:
            print("FINDING: RI tokens concentrated in LAST segments")
    else:
        print("FINDING: No significant positional preference for RI tokens")

print()
print("=" * 70)
print("PREFIX FAMILY x SEGMENT POSITION")
print("=" * 70)
print()

# Are certain PREFIX families more common in first vs last segments?
first_segment_prefixes = defaultdict(int)
last_segment_prefixes = defaultdict(int)

for line_key, line_tokens in lines_with_da:
    segments = split_on_da(line_tokens)

    if len(segments) < 2:
        continue

    # First segment
    for t in segments[0]:
        first_segment_prefixes[t['prefix']] += 1

    # Last segment
    for t in segments[-1]:
        last_segment_prefixes[t['prefix']] += 1

print("Top prefixes by segment position:")
print()
print(f"{'PREFIX':<8} {'First':>8} {'Last':>8} {'Ratio':>8}")
print("-" * 40)

all_prefixes = set(first_segment_prefixes.keys()) | set(last_segment_prefixes.keys())
sorted_prefixes = sorted(all_prefixes, key=lambda p: first_segment_prefixes[p] + last_segment_prefixes[p], reverse=True)

for prefix in sorted_prefixes[:12]:
    first = first_segment_prefixes[prefix]
    last = last_segment_prefixes[prefix]
    ratio = first / last if last > 0 else float('inf')
    print(f"{prefix:<8} {first:>8} {last:>8} {ratio:>8.2f}")

print()

# Save results
results = {
    'summary': {
        'total_lines': len(lines),
        'lines_with_da': len(lines_with_da),
        'lines_without_da': len(lines_without_da),
        'segments_analyzed': len(all_segment_ri_ratios),
        'lines_with_multi_segment': len(within_line_variances)
    },
    'segment_ri_composition': {
        'mean_ri_ratio': float(np.mean(all_segment_ri_ratios)) if all_segment_ri_ratios else None,
        'std_ri_ratio': float(np.std(all_segment_ri_ratios)) if all_segment_ri_ratios else None,
        'mean_within_line_variance': float(observed_mean_var) if within_line_variances else None
    },
    'null_model': {
        'n_permutations': n_permutations,
        'null_mean_variance': float(np.mean(null_variances)),
        'null_std_variance': float(np.std(null_variances)),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d)
    },
    'position_analysis': {
        'first_segment_mean_ri': float(np.mean(first_segment_ri_ratios)) if first_segment_ri_ratios else None,
        'last_segment_mean_ri': float(np.mean(last_segment_ri_ratios)) if last_segment_ri_ratios else None,
        'middle_segment_mean_ri': float(np.mean(middle_segment_ri_ratios)) if middle_segment_ri_ratios else None,
        'first_vs_last_n': len(first_segment_ri_ratios)
    },
    'interpretation': {
        'stratification_detected': bool(cohens_d > 0.5),
        'weak_stratification': bool(0.2 < cohens_d <= 0.5)
    }
}

with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_ri_pp_composition.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print()

if cohens_d > 0.5:
    print("DA SEGMENTS SHOW RI/PP STRATIFICATION")
    print("Segments have reliably different RI/PP compositions.")
    print("This is NEW structure beyond PREFIX alone (pre-check V=0.183).")
    print()
    print("RECOMMENDATION: Proceed to Phase 2 (within-segment positional distribution)")
elif cohens_d > 0.2:
    print("DA SEGMENTS SHOW WEAK RI/PP DIFFERENTIATION")
    print("There is a small but detectable effect.")
    print()
    print("RECOMMENDATION: Consider Phase 2 but effect may be marginal")
else:
    print("DA SEGMENTS DO NOT SHOW RI/PP STRATIFICATION")
    print("RI/PP composition is uniform across DA-segmented blocks.")
    print("DA articulation segments PREFIX families, not RI/PP tracks.")
    print()
    print("RECOMMENDATION: Phase 2 may not yield new insights")

print()
print("Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_ri_pp_composition.json")
