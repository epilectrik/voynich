#!/usr/bin/env python3
"""
Phase 2: Within-Segment RI Positional Distribution

Question: Do RI tokens prefer specific positions within DA segments?
Phase 1 found weak segment-level stratification. This tests whether RI tokens
cluster at segment boundaries (opener/closer) vs segment interiors.

Method:
1. For each DA segment with 3+ tokens, identify token positions
2. Classify positions: OPENER (first), CLOSER (last), INTERIOR (middle)
3. Compute RI rate by position class
4. Compare to null model (random RI placement within segments)

This extends C498-CHAR-A-CLOSURE (line-level) to segment-level.
"""

import json
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

# Load pre-classified token data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    middle_classes = json.load(f)

# Get RI middles set
ri_middles = set(middle_classes['a_exclusive_middles'])

print("=" * 70)
print("PHASE 2: WITHIN-SEGMENT RI POSITIONAL DISTRIBUTION")
print("=" * 70)
print()

# Group tokens by line
lines = defaultdict(list)
for t in tokens:
    line_key = (t['folio'], t['line'])
    lines[line_key].append(t)

def split_on_da(line_tokens):
    """Split line tokens into segments on DA tokens."""
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

# Collect position data
opener_ri = 0
opener_pp = 0
closer_ri = 0
closer_pp = 0
interior_ri = 0
interior_pp = 0

# Also track normalized positions for continuous analysis
ri_normalized_positions = []
pp_normalized_positions = []

# Track by segment length
position_by_length = defaultdict(lambda: {'opener_ri': 0, 'opener_pp': 0,
                                           'closer_ri': 0, 'closer_pp': 0,
                                           'interior_ri': 0, 'interior_pp': 0})

segments_analyzed = 0
total_tokens_in_segments = 0

for line_key, line_tokens in lines.items():
    segments = split_on_da(line_tokens)

    for seg in segments:
        seg_len = len(seg)

        if seg_len < 3:
            # Need at least 3 tokens to have opener, interior, closer
            continue

        segments_analyzed += 1
        total_tokens_in_segments += seg_len

        for i, t in enumerate(seg):
            is_ri = t['middle'] in ri_middles

            # Normalized position (0.0 = start, 1.0 = end)
            norm_pos = i / (seg_len - 1) if seg_len > 1 else 0.5

            if is_ri:
                ri_normalized_positions.append(norm_pos)
            else:
                pp_normalized_positions.append(norm_pos)

            # Categorical position
            if i == 0:
                # Opener
                if is_ri:
                    opener_ri += 1
                    position_by_length[seg_len]['opener_ri'] += 1
                else:
                    opener_pp += 1
                    position_by_length[seg_len]['opener_pp'] += 1
            elif i == seg_len - 1:
                # Closer
                if is_ri:
                    closer_ri += 1
                    position_by_length[seg_len]['closer_ri'] += 1
                else:
                    closer_pp += 1
                    position_by_length[seg_len]['closer_pp'] += 1
            else:
                # Interior
                if is_ri:
                    interior_ri += 1
                    position_by_length[seg_len]['interior_ri'] += 1
                else:
                    interior_pp += 1
                    position_by_length[seg_len]['interior_pp'] += 1

print(f"Segments analyzed (3+ tokens): {segments_analyzed}")
print(f"Total tokens in segments: {total_tokens_in_segments}")
print()

print("=" * 70)
print("RI RATE BY POSITION CLASS")
print("=" * 70)
print()

opener_total = opener_ri + opener_pp
closer_total = closer_ri + closer_pp
interior_total = interior_ri + interior_pp

opener_ri_rate = opener_ri / opener_total if opener_total > 0 else 0
closer_ri_rate = closer_ri / closer_total if closer_total > 0 else 0
interior_ri_rate = interior_ri / interior_total if interior_total > 0 else 0

print(f"{'Position':<12} {'RI':>8} {'PP':>8} {'Total':>8} {'RI Rate':>10}")
print("-" * 50)
print(f"{'OPENER':<12} {opener_ri:>8} {opener_pp:>8} {opener_total:>8} {100*opener_ri_rate:>9.2f}%")
print(f"{'INTERIOR':<12} {interior_ri:>8} {interior_pp:>8} {interior_total:>8} {100*interior_ri_rate:>9.2f}%")
print(f"{'CLOSER':<12} {closer_ri:>8} {closer_pp:>8} {closer_total:>8} {100*closer_ri_rate:>9.2f}%")
print("-" * 50)

total_ri = opener_ri + interior_ri + closer_ri
total_pp = opener_pp + interior_pp + closer_pp
total = total_ri + total_pp
overall_ri_rate = total_ri / total if total > 0 else 0

print(f"{'OVERALL':<12} {total_ri:>8} {total_pp:>8} {total:>8} {100*overall_ri_rate:>9.2f}%")
print()

# Chi-square test: Position x RI/PP
observed = np.array([
    [opener_ri, opener_pp],
    [interior_ri, interior_pp],
    [closer_ri, closer_pp]
])

chi2, p_value, dof, expected = stats.chi2_contingency(observed)

print(f"Chi-square test (Position x RI/PP):")
print(f"  chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.4e}")
print(f"  degrees of freedom = {dof}")
print()

# Cramer's V
n = observed.sum()
min_dim = min(observed.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"  Cramer's V = {cramers_v:.4f}")
if cramers_v > 0.1:
    print(f"  -> MODERATE association")
elif cramers_v > 0.05:
    print(f"  -> WEAK association")
else:
    print(f"  -> NEGLIGIBLE association")
print()

print("=" * 70)
print("NORMALIZED POSITION DISTRIBUTION")
print("=" * 70)
print()

ri_positions = np.array(ri_normalized_positions)
pp_positions = np.array(pp_normalized_positions)

print(f"RI tokens (n={len(ri_positions)}):")
print(f"  Mean position: {np.mean(ri_positions):.3f}")
print(f"  Std: {np.std(ri_positions):.3f}")
print(f"  Median: {np.median(ri_positions):.3f}")
print()

print(f"PP tokens (n={len(pp_positions)}):")
print(f"  Mean position: {np.mean(pp_positions):.3f}")
print(f"  Std: {np.std(pp_positions):.3f}")
print(f"  Median: {np.median(pp_positions):.3f}")
print()

# Mann-Whitney U test (non-parametric)
if len(ri_positions) > 0 and len(pp_positions) > 0:
    u_stat, u_pval = stats.mannwhitneyu(ri_positions, pp_positions, alternative='two-sided')
    print(f"Mann-Whitney U test (RI vs PP positions):")
    print(f"  U = {u_stat:.0f}")
    print(f"  p-value = {u_pval:.4e}")
    print()

    # Effect size (rank-biserial correlation)
    n1, n2 = len(ri_positions), len(pp_positions)
    r_rb = 1 - (2 * u_stat) / (n1 * n2)
    print(f"  Rank-biserial correlation: {r_rb:.4f}")
    if abs(r_rb) > 0.3:
        print(f"  -> LARGE effect")
    elif abs(r_rb) > 0.1:
        print(f"  -> MEDIUM effect")
    else:
        print(f"  -> SMALL effect")
print()

# Position histogram
print("Position distribution (bins of 0.2):")
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
ri_hist, _ = np.histogram(ri_positions, bins=bins)
pp_hist, _ = np.histogram(pp_positions, bins=bins)

print()
print(f"{'Bin':<12} {'RI Count':>10} {'RI %':>8} {'PP Count':>10} {'PP %':>8} {'RI Rate':>10}")
print("-" * 70)
for i in range(len(bins)-1):
    ri_pct = 100 * ri_hist[i] / len(ri_positions) if len(ri_positions) > 0 else 0
    pp_pct = 100 * pp_hist[i] / len(pp_positions) if len(pp_positions) > 0 else 0
    bin_total = ri_hist[i] + pp_hist[i]
    ri_rate = 100 * ri_hist[i] / bin_total if bin_total > 0 else 0
    print(f"{bins[i]:.1f}-{bins[i+1]:.1f}       {ri_hist[i]:>10} {ri_pct:>7.1f}% {pp_hist[i]:>10} {pp_pct:>7.1f}% {ri_rate:>9.1f}%")
print()

print("=" * 70)
print("BOUNDARY VS INTERIOR ANALYSIS")
print("=" * 70)
print()

# Combine opener + closer as "boundary" position
boundary_ri = opener_ri + closer_ri
boundary_pp = opener_pp + closer_pp
boundary_total = boundary_ri + boundary_pp
boundary_ri_rate = boundary_ri / boundary_total if boundary_total > 0 else 0

print(f"BOUNDARY (opener + closer): {boundary_ri}/{boundary_total} = {100*boundary_ri_rate:.2f}% RI")
print(f"INTERIOR: {interior_ri}/{interior_total} = {100*interior_ri_rate:.2f}% RI")
print()

# 2x2 chi-square: Boundary/Interior x RI/PP
observed_2x2 = np.array([
    [boundary_ri, boundary_pp],
    [interior_ri, interior_pp]
])

chi2_2x2, p_2x2, dof_2x2, expected_2x2 = stats.chi2_contingency(observed_2x2)

print(f"Chi-square test (Boundary vs Interior):")
print(f"  chi2 = {chi2_2x2:.2f}")
print(f"  p-value = {p_2x2:.4e}")
print()

# Odds ratio
if interior_pp > 0 and boundary_pp > 0 and interior_ri > 0:
    odds_ratio = (boundary_ri / boundary_pp) / (interior_ri / interior_pp)
    print(f"Odds ratio (boundary vs interior for RI): {odds_ratio:.2f}")
    if odds_ratio > 1:
        print(f"  -> RI tokens {odds_ratio:.1f}x more likely at boundaries")
    else:
        print(f"  -> RI tokens {1/odds_ratio:.1f}x more likely in interior")
else:
    odds_ratio = None
    print("Odds ratio: undefined (zero counts)")
print()

print("=" * 70)
print("OPENER VS CLOSER ASYMMETRY")
print("=" * 70)
print()

print(f"OPENER: {opener_ri}/{opener_total} = {100*opener_ri_rate:.2f}% RI")
print(f"CLOSER: {closer_ri}/{closer_total} = {100*closer_ri_rate:.2f}% RI")
print()

if opener_ri_rate > closer_ri_rate:
    ratio = opener_ri_rate / closer_ri_rate if closer_ri_rate > 0 else float('inf')
    print(f"RI prefers OPENER position ({ratio:.2f}x)")
elif closer_ri_rate > opener_ri_rate:
    ratio = closer_ri_rate / opener_ri_rate if opener_ri_rate > 0 else float('inf')
    print(f"RI prefers CLOSER position ({ratio:.2f}x)")
else:
    print("RI equally distributed between opener and closer")
print()

# Test opener vs closer
if opener_total > 0 and closer_total > 0:
    # Fisher exact test for opener vs closer
    observed_oc = np.array([
        [opener_ri, opener_pp],
        [closer_ri, closer_pp]
    ])
    _, p_oc = stats.fisher_exact(observed_oc)
    print(f"Fisher exact test (opener vs closer): p = {p_oc:.4f}")
    if p_oc < 0.05:
        print("  -> SIGNIFICANT difference between opener and closer")
    else:
        print("  -> No significant opener/closer asymmetry")
print()

print("=" * 70)
print("COMPARISON TO LINE-LEVEL (C498-CHAR-A-CLOSURE)")
print("=" * 70)
print()

# From C498-CHAR-A-CLOSURE: RI closers show 29.5% line-final vs 16.8% random
# Here we test if segment-level shows similar pattern

print("Line-level finding (C498-CHAR-A-CLOSURE):")
print("  RI tokens: 29.5% line-final vs 16.8% expected")
print("  Ratio: 1.76x preference for line-final")
print()

segment_closer_ratio = closer_ri_rate / overall_ri_rate if overall_ri_rate > 0 else 0
segment_opener_ratio = opener_ri_rate / overall_ri_rate if overall_ri_rate > 0 else 0

print("Segment-level finding (this analysis):")
print(f"  RI rate at CLOSER: {100*closer_ri_rate:.2f}% vs {100*overall_ri_rate:.2f}% overall")
print(f"  Ratio: {segment_closer_ratio:.2f}x")
print()
print(f"  RI rate at OPENER: {100*opener_ri_rate:.2f}% vs {100*overall_ri_rate:.2f}% overall")
print(f"  Ratio: {segment_opener_ratio:.2f}x")
print()

if segment_closer_ratio > 1.3:
    print("FINDING: Segment-level closer preference CONFIRMS line-level pattern")
elif segment_opener_ratio > 1.3:
    print("FINDING: Segment-level shows OPENER preference (different from line-level)")
else:
    print("FINDING: No strong positional preference within segments")

print()

# Save results
results = {
    'summary': {
        'segments_analyzed': segments_analyzed,
        'total_tokens': total_tokens_in_segments,
        'total_ri': total_ri,
        'total_pp': total_pp
    },
    'position_counts': {
        'opener': {'ri': opener_ri, 'pp': opener_pp, 'ri_rate': opener_ri_rate},
        'interior': {'ri': interior_ri, 'pp': interior_pp, 'ri_rate': interior_ri_rate},
        'closer': {'ri': closer_ri, 'pp': closer_pp, 'ri_rate': closer_ri_rate}
    },
    'chi_square_3way': {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v)
    },
    'normalized_position': {
        'ri_mean': float(np.mean(ri_positions)) if len(ri_positions) > 0 else None,
        'pp_mean': float(np.mean(pp_positions)) if len(pp_positions) > 0 else None,
        'mann_whitney_p': float(u_pval) if len(ri_positions) > 0 else None,
        'rank_biserial': float(r_rb) if len(ri_positions) > 0 else None
    },
    'boundary_vs_interior': {
        'boundary_ri_rate': float(boundary_ri_rate),
        'interior_ri_rate': float(interior_ri_rate),
        'chi2': float(chi2_2x2),
        'p_value': float(p_2x2),
        'odds_ratio': float(odds_ratio) if odds_ratio else None
    },
    'opener_vs_closer': {
        'opener_ri_rate': float(opener_ri_rate),
        'closer_ri_rate': float(closer_ri_rate),
        'closer_to_overall_ratio': float(segment_closer_ratio),
        'opener_to_overall_ratio': float(segment_opener_ratio)
    }
}

with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_ri_position.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print()

if cramers_v > 0.1 or abs(r_rb) > 0.1:
    print("RI TOKENS SHOW POSITIONAL PREFERENCE WITHIN SEGMENTS")
    if closer_ri_rate > opener_ri_rate and closer_ri_rate > interior_ri_rate:
        print("  -> CLOSER preference (consistent with line-level finding)")
    elif opener_ri_rate > closer_ri_rate and opener_ri_rate > interior_ri_rate:
        print("  -> OPENER preference (segment-initial marking)")
    elif interior_ri_rate > opener_ri_rate and interior_ri_rate > closer_ri_rate:
        print("  -> INTERIOR preference (embedded within segments)")
else:
    print("NO STRONG POSITIONAL PREFERENCE WITHIN SEGMENTS")
    print("RI tokens are distributed uniformly across segment positions.")
print()

print("Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_ri_position.json")
