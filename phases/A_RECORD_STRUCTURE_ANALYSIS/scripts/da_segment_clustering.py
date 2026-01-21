#!/usr/bin/env python3
"""
Phase 3: Segment-Type Clustering by RI/PP Profile

Question: Can DA segments be classified into distinct types based on RI/PP composition?
Phase 1 found weak stratification, Phase 2 found hierarchical closure.
This tests whether segments cluster into meaningful types.

Method:
1. Extract segment features: RI ratio, length, dominant PREFIX, position in line
2. Classify segments into RI-profile types (PP-pure, RI-sparse, RI-rich)
3. Test if types correlate with: segment position, PREFIX family, folio
4. Determine if segment types have structural meaning beyond random
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
print("PHASE 3: SEGMENT-TYPE CLUSTERING BY RI/PP PROFILE")
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

# Extract all segments with metadata
all_segments = []

for line_key, line_tokens in lines.items():
    folio, line_num = line_key
    segments = split_on_da(line_tokens)
    n_segments = len(segments)

    for seg_idx, seg in enumerate(segments):
        if len(seg) < 2:
            continue

        # Compute features
        ri_count = sum(1 for t in seg if t['middle'] in ri_middles)
        pp_count = len(seg) - ri_count
        ri_ratio = ri_count / len(seg)

        # Dominant PREFIX
        prefix_counts = Counter(t['prefix'] for t in seg)
        dominant_prefix = prefix_counts.most_common(1)[0][0]
        prefix_diversity = len(prefix_counts)

        # Position in line
        if n_segments == 1:
            position = 'only'
        elif seg_idx == 0:
            position = 'first'
        elif seg_idx == n_segments - 1:
            position = 'last'
        else:
            position = 'middle'

        # Normalized position
        norm_position = seg_idx / (n_segments - 1) if n_segments > 1 else 0.5

        all_segments.append({
            'folio': folio,
            'line': line_num,
            'seg_idx': seg_idx,
            'n_segments_in_line': n_segments,
            'position': position,
            'norm_position': norm_position,
            'length': len(seg),
            'ri_count': ri_count,
            'pp_count': pp_count,
            'ri_ratio': ri_ratio,
            'dominant_prefix': dominant_prefix,
            'prefix_diversity': prefix_diversity,
            'tokens': seg
        })

print(f"Total segments analyzed: {len(all_segments)}")
print()

# Classify segments by RI profile
def classify_ri_profile(ri_ratio):
    """Classify segment by RI content."""
    if ri_ratio == 0:
        return 'PP_PURE'
    elif ri_ratio < 0.1:
        return 'RI_SPARSE'
    elif ri_ratio < 0.3:
        return 'RI_MODERATE'
    else:
        return 'RI_RICH'

for seg in all_segments:
    seg['ri_profile'] = classify_ri_profile(seg['ri_ratio'])

# Profile distribution
profile_counts = Counter(seg['ri_profile'] for seg in all_segments)

print("=" * 70)
print("SEGMENT RI PROFILE DISTRIBUTION")
print("=" * 70)
print()

print(f"{'Profile':<15} {'Count':>8} {'Pct':>8}")
print("-" * 35)
for profile in ['PP_PURE', 'RI_SPARSE', 'RI_MODERATE', 'RI_RICH']:
    count = profile_counts[profile]
    pct = 100 * count / len(all_segments)
    print(f"{profile:<15} {count:>8} {pct:>7.1f}%")
print("-" * 35)
print(f"{'TOTAL':<15} {len(all_segments):>8}")
print()

print("=" * 70)
print("PROFILE x SEGMENT POSITION")
print("=" * 70)
print()

# Cross-tab: Profile x Position
position_profile = defaultdict(Counter)
for seg in all_segments:
    position_profile[seg['position']][seg['ri_profile']] += 1

print(f"{'Position':<10} {'PP_PURE':>10} {'RI_SPARSE':>10} {'RI_MOD':>10} {'RI_RICH':>10} {'Total':>8}")
print("-" * 70)

for position in ['first', 'middle', 'last', 'only']:
    counts = position_profile[position]
    total = sum(counts.values())
    if total == 0:
        continue
    print(f"{position:<10} {counts['PP_PURE']:>10} {counts['RI_SPARSE']:>10} "
          f"{counts['RI_MODERATE']:>10} {counts['RI_RICH']:>10} {total:>8}")
print()

# Chi-square test: Position x Profile
positions_to_test = ['first', 'middle', 'last']
profiles_to_test = ['PP_PURE', 'RI_SPARSE', 'RI_MODERATE', 'RI_RICH']

observed_pos = []
for pos in positions_to_test:
    row = [position_profile[pos][prof] for prof in profiles_to_test]
    observed_pos.append(row)

observed_pos = np.array(observed_pos)
# Remove columns with all zeros
col_sums = observed_pos.sum(axis=0)
valid_cols = col_sums > 0
observed_pos = observed_pos[:, valid_cols]

if observed_pos.shape[1] > 1:
    chi2_pos, p_pos, dof_pos, expected_pos = stats.chi2_contingency(observed_pos)
    print(f"Chi-square (Position x Profile): chi2={chi2_pos:.2f}, p={p_pos:.4f}")
    cramers_v_pos = np.sqrt(chi2_pos / (observed_pos.sum() * (min(observed_pos.shape) - 1)))
    print(f"Cramer's V: {cramers_v_pos:.4f}")
    print()

    if p_pos < 0.05:
        print("FINDING: Segment position predicts RI profile")
    else:
        print("FINDING: Segment position does NOT predict RI profile")
    print()
else:
    print("Insufficient data for position x profile chi-square")
    print()

print("=" * 70)
print("PROFILE x DOMINANT PREFIX")
print("=" * 70)
print()

# Which prefixes dominate which profile types?
prefix_profile = defaultdict(Counter)
for seg in all_segments:
    prefix_profile[seg['dominant_prefix']][seg['ri_profile']] += 1

# Top prefixes by total segments
prefix_totals = {p: sum(counts.values()) for p, counts in prefix_profile.items()}
top_prefixes = sorted(prefix_totals.keys(), key=lambda p: prefix_totals[p], reverse=True)[:10]

print(f"{'PREFIX':<8} {'PP_PURE':>10} {'RI_SPARSE':>10} {'RI_MOD':>10} {'RI_RICH':>10} {'RI Rate':>10}")
print("-" * 70)

for prefix in top_prefixes:
    counts = prefix_profile[prefix]
    total = sum(counts.values())
    # Compute weighted RI rate for this prefix's segments
    prefix_segs = [s for s in all_segments if s['dominant_prefix'] == prefix]
    mean_ri_ratio = np.mean([s['ri_ratio'] for s in prefix_segs])

    print(f"{prefix:<8} {counts['PP_PURE']:>10} {counts['RI_SPARSE']:>10} "
          f"{counts['RI_MODERATE']:>10} {counts['RI_RICH']:>10} {100*mean_ri_ratio:>9.1f}%")
print()

# Chi-square: Prefix x Profile (top 5 prefixes)
top5_prefixes = top_prefixes[:5]
observed_pfx = []
for pfx in top5_prefixes:
    row = [prefix_profile[pfx][prof] for prof in profiles_to_test]
    observed_pfx.append(row)

observed_pfx = np.array(observed_pfx)
col_sums_pfx = observed_pfx.sum(axis=0)
valid_cols_pfx = col_sums_pfx > 0
observed_pfx = observed_pfx[:, valid_cols_pfx]

if observed_pfx.shape[1] > 1:
    chi2_pfx, p_pfx, dof_pfx, expected_pfx = stats.chi2_contingency(observed_pfx)
    print(f"Chi-square (Top 5 Prefix x Profile): chi2={chi2_pfx:.2f}, p={p_pfx:.4e}")
    cramers_v_pfx = np.sqrt(chi2_pfx / (observed_pfx.sum() * (min(observed_pfx.shape) - 1)))
    print(f"Cramer's V: {cramers_v_pfx:.4f}")
    print()

    if cramers_v_pfx > 0.1:
        print("FINDING: PREFIX strongly predicts segment RI profile")
    elif p_pfx < 0.05:
        print("FINDING: PREFIX weakly predicts segment RI profile")
    else:
        print("FINDING: PREFIX does NOT predict segment RI profile")
    print()

print("=" * 70)
print("RI-RICH SEGMENT ANALYSIS")
print("=" * 70)
print()

# Focus on RI-RICH segments (>30% RI)
ri_rich_segs = [s for s in all_segments if s['ri_profile'] == 'RI_RICH']
print(f"RI-RICH segments (>30% RI): {len(ri_rich_segs)}")
print()

if ri_rich_segs:
    # Position distribution
    rich_positions = Counter(s['position'] for s in ri_rich_segs)
    print("Position distribution of RI-RICH segments:")
    for pos in ['first', 'middle', 'last', 'only']:
        if rich_positions[pos] > 0:
            pct = 100 * rich_positions[pos] / len(ri_rich_segs)
            print(f"  {pos}: {rich_positions[pos]} ({pct:.1f}%)")
    print()

    # Dominant prefix distribution
    rich_prefixes = Counter(s['dominant_prefix'] for s in ri_rich_segs)
    print("Dominant PREFIX in RI-RICH segments:")
    for prefix, count in rich_prefixes.most_common(8):
        pct = 100 * count / len(ri_rich_segs)
        print(f"  {prefix}: {count} ({pct:.1f}%)")
    print()

    # Length distribution
    rich_lengths = [s['length'] for s in ri_rich_segs]
    print(f"Length of RI-RICH segments: mean={np.mean(rich_lengths):.1f}, "
          f"median={np.median(rich_lengths):.0f}, range={min(rich_lengths)}-{max(rich_lengths)}")
    print()

    # Folio concentration
    rich_folios = Counter(s['folio'] for s in ri_rich_segs)
    print(f"RI-RICH segments appear in {len(rich_folios)} folios")
    print("Top folios:")
    for folio, count in rich_folios.most_common(5):
        print(f"  {folio}: {count}")
    print()

print("=" * 70)
print("SEGMENT LENGTH x RI PROFILE")
print("=" * 70)
print()

# Do longer segments have different RI profiles?
length_buckets = {
    'short (2-4)': lambda s: 2 <= s['length'] <= 4,
    'medium (5-8)': lambda s: 5 <= s['length'] <= 8,
    'long (9+)': lambda s: s['length'] >= 9
}

print(f"{'Length':<15} {'Mean RI%':>10} {'PP_PURE':>10} {'RI_RICH':>10} {'Count':>8}")
print("-" * 60)

for bucket_name, bucket_filter in length_buckets.items():
    bucket_segs = [s for s in all_segments if bucket_filter(s)]
    if not bucket_segs:
        continue

    mean_ri = np.mean([s['ri_ratio'] for s in bucket_segs])
    pp_pure_pct = 100 * sum(1 for s in bucket_segs if s['ri_profile'] == 'PP_PURE') / len(bucket_segs)
    ri_rich_pct = 100 * sum(1 for s in bucket_segs if s['ri_profile'] == 'RI_RICH') / len(bucket_segs)

    print(f"{bucket_name:<15} {100*mean_ri:>9.1f}% {pp_pure_pct:>9.1f}% {ri_rich_pct:>9.1f}% {len(bucket_segs):>8}")

print()

# Correlation: Length vs RI ratio
lengths = np.array([s['length'] for s in all_segments])
ri_ratios = np.array([s['ri_ratio'] for s in all_segments])

corr, p_corr = stats.pearsonr(lengths, ri_ratios)
print(f"Correlation (length vs RI ratio): r={corr:.4f}, p={p_corr:.4e}")
if p_corr < 0.05:
    if corr > 0:
        print("  -> Longer segments have MORE RI tokens")
    else:
        print("  -> Longer segments have FEWER RI tokens")
else:
    print("  -> No significant correlation")
print()

print("=" * 70)
print("SEGMENT TYPING COHERENCE")
print("=" * 70)
print()

# Key question: Are RI-RICH segments structurally distinct or just random variation?
# Test: Compare RI-RICH to random sample of same lengths

if ri_rich_segs:
    # Get length distribution of RI-RICH
    rich_length_dist = Counter(s['length'] for s in ri_rich_segs)

    # Sample PP_PURE segments with matching lengths
    pp_pure_segs = [s for s in all_segments if s['ri_profile'] == 'PP_PURE']

    # For each RI-RICH segment, what's the probability of that RI count by chance?
    # Given segment length L and overall RI rate r, P(RI >= k) follows binomial

    overall_ri_rate = sum(s['ri_count'] for s in all_segments) / sum(s['length'] for s in all_segments)
    print(f"Overall RI token rate: {100*overall_ri_rate:.2f}%")
    print()

    # For each RI-RICH segment, compute binomial p-value
    significant_segs = 0
    for seg in ri_rich_segs:
        # P(X >= ri_count) where X ~ Binomial(length, overall_ri_rate)
        p_val = 1 - stats.binom.cdf(seg['ri_count'] - 1, seg['length'], overall_ri_rate)
        if p_val < 0.05:
            significant_segs += 1

    print(f"RI-RICH segments with p<0.05 (binomial): {significant_segs}/{len(ri_rich_segs)} "
          f"({100*significant_segs/len(ri_rich_segs):.1f}%)")

    # Expected by chance at p<0.05: 5%
    expected_by_chance = 0.05 * len(ri_rich_segs)
    ratio = significant_segs / expected_by_chance if expected_by_chance > 0 else 0
    print(f"Expected by chance: {expected_by_chance:.1f}")
    print(f"Ratio observed/expected: {ratio:.1f}x")
    print()

    if ratio > 2:
        print("FINDING: RI-RICH segments are significantly more common than expected by chance")
        print("These segments represent a distinct structural type, not random fluctuation.")
    else:
        print("FINDING: RI-RICH segments could arise from random binomial fluctuation")
        print("No evidence for a distinct segment type.")

print()

print("=" * 70)
print("PREFIX COHERENCE IN RI-RICH SEGMENTS")
print("=" * 70)
print()

# Are RI-RICH segments more PREFIX-coherent than average?
if ri_rich_segs:
    rich_diversity = [s['prefix_diversity'] for s in ri_rich_segs]
    other_segs = [s for s in all_segments if s['ri_profile'] != 'RI_RICH']
    other_diversity = [s['prefix_diversity'] for s in other_segs]

    print(f"PREFIX diversity in RI-RICH segments: mean={np.mean(rich_diversity):.2f}")
    print(f"PREFIX diversity in other segments: mean={np.mean(other_diversity):.2f}")

    t_div, p_div = stats.mannwhitneyu(rich_diversity, other_diversity, alternative='two-sided')
    print(f"Mann-Whitney U: p={p_div:.4f}")

    if p_div < 0.05:
        if np.mean(rich_diversity) < np.mean(other_diversity):
            print("  -> RI-RICH segments are MORE PREFIX-coherent")
        else:
            print("  -> RI-RICH segments are LESS PREFIX-coherent")
    else:
        print("  -> No difference in PREFIX coherence")
    print()

# Save results
results = {
    'summary': {
        'total_segments': len(all_segments),
        'profile_distribution': dict(profile_counts)
    },
    'position_x_profile': {
        'chi2': float(chi2_pos) if 'chi2_pos' in dir() else None,
        'p_value': float(p_pos) if 'p_pos' in dir() else None,
        'cramers_v': float(cramers_v_pos) if 'cramers_v_pos' in dir() else None
    },
    'prefix_x_profile': {
        'chi2': float(chi2_pfx) if 'chi2_pfx' in dir() else None,
        'p_value': float(p_pfx) if 'p_pfx' in dir() else None,
        'cramers_v': float(cramers_v_pfx) if 'cramers_v_pfx' in dir() else None
    },
    'ri_rich_analysis': {
        'count': len(ri_rich_segs),
        'position_distribution': dict(rich_positions) if ri_rich_segs else None,
        'top_prefixes': dict(rich_prefixes.most_common(5)) if ri_rich_segs else None,
        'significant_by_binomial': significant_segs if ri_rich_segs else None,
        'ratio_observed_expected': float(ratio) if ri_rich_segs and 'ratio' in dir() else None
    },
    'length_correlation': {
        'pearson_r': float(corr),
        'p_value': float(p_corr)
    }
}

with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_clustering.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print()

# Summarize key findings
findings = []

if 'cramers_v_pfx' in dir() and cramers_v_pfx > 0.1:
    findings.append("PREFIX strongly predicts segment RI profile (V > 0.1)")
elif 'p_pfx' in dir() and p_pfx < 0.05:
    findings.append("PREFIX weakly predicts segment RI profile")

if 'p_pos' in dir() and p_pos < 0.05:
    findings.append("Segment position predicts RI profile")

if ri_rich_segs and 'ratio' in dir() and ratio > 2:
    findings.append("RI-RICH segments are structurally distinct (not random)")

if corr < -0.1 and p_corr < 0.05:
    findings.append("Shorter segments have higher RI rates")
elif corr > 0.1 and p_corr < 0.05:
    findings.append("Longer segments have higher RI rates")

if findings:
    print("KEY FINDINGS:")
    for f in findings:
        print(f"  - {f}")
else:
    print("No strong segment typing effects detected.")
    print("RI/PP distribution across segments appears uniform.")

print()
print("Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/da_segment_clustering.json")
