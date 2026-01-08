#!/usr/bin/env python3
"""
AZC Axis Connectivity Tests - Batch 1

Tests for cross-axis dependencies in AZC labels:
- Test 1: Placement × Morphology Dependency
- Test 7: R1/R2/R3 Ordering
- Test 8: Forbidden Placement Combinations

Looking for: constraints, correlations, ordering relations, forbidden combinations
NOT looking for: interpretations, geometry, semantics
"""

import json
import os
from collections import Counter, defaultdict
import math

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC AXIS CONNECTIVITY TESTS - BATCH 1")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract tokens
azc_tokens = []
a_tokens = []
b_tokens = []

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        if lang == 'NA' or lang == '':
            azc_tokens.append(row)
        elif lang == 'A':
            a_tokens.append(row)
        elif lang == 'B':
            b_tokens.append(row)

# Get AZC-only vocabulary
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

print(f"\nLoaded {len(azc_only_tokens)} AZC-only tokens ({len(azc_only)} types)")

# =============================================================================
# MORPHOLOGICAL DECOMPOSITION
# =============================================================================

# Standard prefixes and suffixes
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt', 'kch', 'ko', 'op', 'oe', 'oa']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y', 'ey', 'eey', 'ol', 'al', 'or', 'ar', 'chy', 'shy', 'hy', 'eol', 'eal', 'am', 'an']

def decompose(word):
    """Decompose word into prefix, middle, suffix."""
    prefix = ''
    for p in sorted(PREFIXES, key=len, reverse=True):
        if word.startswith(p) and len(p) < len(word):
            prefix = p
            break

    suffix = ''
    remainder = word[len(prefix):] if prefix else word
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s) and len(s) <= len(remainder):
            suffix = s
            break

    if prefix and suffix and len(suffix) < len(word) - len(prefix):
        middle = word[len(prefix):-len(suffix)]
    elif prefix:
        middle = word[len(prefix):]
        suffix = ''
    elif suffix:
        middle = word[:-len(suffix)]
    else:
        middle = word

    return prefix or 'NONE', middle, suffix or 'NONE'

# Add morphology to tokens
for t in azc_only_tokens:
    prefix, middle, suffix = decompose(t['word'])
    t['prefix'] = prefix
    t['middle'] = middle
    t['middle_len'] = len(middle)
    t['suffix'] = suffix

# =============================================================================
# TEST 1: PLACEMENT × MORPHOLOGY DEPENDENCY
# =============================================================================

print("\n" + "=" * 70)
print("TEST 1: PLACEMENT × MORPHOLOGY DEPENDENCY")
print("=" * 70)

def chi_square_test(contingency):
    """Compute chi-square and Cramer's V from contingency table."""
    # Get row and column totals
    rows = list(contingency.keys())
    cols = set()
    for row_data in contingency.values():
        cols.update(row_data.keys())
    cols = list(cols)

    # Build matrix
    observed = []
    for row in rows:
        obs_row = [contingency[row].get(col, 0) for col in cols]
        observed.append(obs_row)

    # Calculate expected values and chi-square
    n = sum(sum(row) for row in observed)
    if n == 0:
        return 0, 0, 1.0

    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(len(rows))) for j in range(len(cols))]

    chi2 = 0
    for i, row in enumerate(rows):
        for j, col in enumerate(cols):
            expected = (row_totals[i] * col_totals[j]) / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    # Cramer's V
    k = min(len(rows), len(cols))
    if k > 1 and n > 0:
        cramers_v = math.sqrt(chi2 / (n * (k - 1)))
    else:
        cramers_v = 0

    # Degrees of freedom
    df = (len(rows) - 1) * (len(cols) - 1)

    return chi2, cramers_v, df

# Test 1a: Placement × PREFIX
print("\n--- Test 1a: Placement × PREFIX ---")

placement_prefix = defaultdict(Counter)
for t in azc_only_tokens:
    placement = t.get('placement', 'UNK')
    prefix = t['prefix']
    placement_prefix[placement][prefix] += 1

# Filter to significant placement codes
significant_placements = [p for p, counts in placement_prefix.items() if sum(counts.values()) >= 50]

contingency_prefix = {p: dict(placement_prefix[p]) for p in significant_placements}
chi2_prefix, v_prefix, df_prefix = chi_square_test(contingency_prefix)

print(f"Significant placement codes: {significant_placements}")
print(f"Chi-square: {chi2_prefix:.2f}")
print(f"Cramer's V: {v_prefix:.3f}")
print(f"Degrees of freedom: {df_prefix}")

if v_prefix < 0.1:
    print("Result: NO DEPENDENCY (V < 0.1)")
elif v_prefix < 0.2:
    print("Result: WEAK DEPENDENCY (0.1 <= V < 0.2)")
elif v_prefix < 0.3:
    print("Result: MODERATE DEPENDENCY (0.2 <= V < 0.3)")
else:
    print("Result: STRONG DEPENDENCY (V >= 0.3)")

# Show prefix distribution per placement
print("\nPrefix distribution by placement:")
for placement in sorted(significant_placements):
    counts = placement_prefix[placement]
    total = sum(counts.values())
    top3 = counts.most_common(3)
    top3_str = ", ".join(f"{p}:{c}" for p, c in top3)
    print(f"  {placement}: n={total}, top: {top3_str}")

# Test 1b: Placement × SUFFIX
print("\n--- Test 1b: Placement × SUFFIX ---")

placement_suffix = defaultdict(Counter)
for t in azc_only_tokens:
    placement = t.get('placement', 'UNK')
    suffix = t['suffix']
    placement_suffix[placement][suffix] += 1

contingency_suffix = {p: dict(placement_suffix[p]) for p in significant_placements}
chi2_suffix, v_suffix, df_suffix = chi_square_test(contingency_suffix)

print(f"Chi-square: {chi2_suffix:.2f}")
print(f"Cramer's V: {v_suffix:.3f}")

if v_suffix < 0.1:
    print("Result: NO DEPENDENCY (V < 0.1)")
elif v_suffix < 0.2:
    print("Result: WEAK DEPENDENCY (0.1 <= V < 0.2)")
elif v_suffix < 0.3:
    print("Result: MODERATE DEPENDENCY (0.2 <= V < 0.3)")
else:
    print("Result: STRONG DEPENDENCY (V >= 0.3)")

# Test 1c: Placement × MIDDLE LENGTH
print("\n--- Test 1c: Placement × MIDDLE LENGTH ---")

placement_midlen = defaultdict(list)
for t in azc_only_tokens:
    placement = t.get('placement', 'UNK')
    if placement in significant_placements:
        placement_midlen[placement].append(t['middle_len'])

print("Mean middle length by placement:")
for placement in sorted(significant_placements):
    lengths = placement_midlen[placement]
    if lengths:
        mean_len = sum(lengths) / len(lengths)
        print(f"  {placement}: mean={mean_len:.2f}, n={len(lengths)}")

# =============================================================================
# TEST 7: R1/R2/R3 ORDERING
# =============================================================================

print("\n" + "=" * 70)
print("TEST 7: R1/R2/R3 AND S1/S2 ORDERING")
print("=" * 70)

# Extract R-series and S-series placements
r_series = ['R', 'R1', 'R2', 'R3']
s_series = ['S', 'S1', 'S2']

def analyze_ordering(series_name, series_codes, tokens):
    """Analyze if numeric subscripts show ordering."""
    print(f"\n--- {series_name} Series Analysis ---")

    series_data = defaultdict(list)
    for t in tokens:
        placement = t.get('placement', '')
        if placement in series_codes:
            series_data[placement].append(t)

    if not series_data:
        print(f"No {series_name} series tokens found")
        return None

    metrics = {}
    for code in series_codes:
        if code in series_data:
            tokens_for_code = series_data[code]

            # Metric 1: Average word length
            avg_len = sum(len(t['word']) for t in tokens_for_code) / len(tokens_for_code)

            # Metric 2: Average middle length
            avg_mid = sum(t['middle_len'] for t in tokens_for_code) / len(tokens_for_code)

            # Metric 3: Repetition count (how many times each word appears)
            word_counts = Counter(t['word'] for t in tokens_for_code)
            avg_rep = sum(word_counts.values()) / len(word_counts) if word_counts else 0

            # Metric 4: Unique ratio (types/tokens)
            unique_ratio = len(word_counts) / len(tokens_for_code) if tokens_for_code else 0

            metrics[code] = {
                'n': len(tokens_for_code),
                'avg_word_len': avg_len,
                'avg_middle_len': avg_mid,
                'avg_repetition': avg_rep,
                'unique_ratio': unique_ratio
            }

            print(f"  {code}: n={len(tokens_for_code)}, "
                  f"word_len={avg_len:.2f}, middle_len={avg_mid:.2f}, "
                  f"rep={avg_rep:.2f}, unique={unique_ratio:.2f}")

    # Test for monotonic trends
    if len(metrics) >= 3:
        codes_ordered = [c for c in series_codes if c in metrics]

        # Check word length trend
        word_lens = [metrics[c]['avg_word_len'] for c in codes_ordered]
        mid_lens = [metrics[c]['avg_middle_len'] for c in codes_ordered]
        reps = [metrics[c]['avg_repetition'] for c in codes_ordered]

        def is_monotonic(values):
            if len(values) < 2:
                return False, "N/A"
            increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
            decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))
            if increasing:
                return True, "INCREASING"
            elif decreasing:
                return True, "DECREASING"
            return False, "NON-MONOTONIC"

        print(f"\n  Monotonicity tests:")
        mono_word, dir_word = is_monotonic(word_lens)
        mono_mid, dir_mid = is_monotonic(mid_lens)
        mono_rep, dir_rep = is_monotonic(reps)

        print(f"    Word length: {dir_word} ({word_lens})")
        print(f"    Middle length: {dir_mid} ({[f'{x:.2f}' for x in mid_lens]})")
        print(f"    Repetition: {dir_rep} ({[f'{x:.2f}' for x in reps]})")

        return {
            'codes': codes_ordered,
            'word_len_monotonic': mono_word,
            'middle_len_monotonic': mono_mid,
            'rep_monotonic': mono_rep
        }

    return None

r_result = analyze_ordering("R", r_series, azc_only_tokens)
s_result = analyze_ordering("S", s_series, azc_only_tokens)

# =============================================================================
# TEST 8: FORBIDDEN PLACEMENT COMBINATIONS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 8: FORBIDDEN PLACEMENT COMBINATIONS")
print("=" * 70)

# Build placement bigram transitions within lines
placement_bigrams = Counter()
placement_counts = Counter()

# Group tokens by folio and line
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# Count transitions
for key, tokens in by_line.items():
    # Sort by position if possible, otherwise use order in file
    for i in range(len(tokens) - 1):
        p1 = tokens[i].get('placement', 'UNK')
        p2 = tokens[i+1].get('placement', 'UNK')
        placement_bigrams[(p1, p2)] += 1
        placement_counts[p1] += 1

# Calculate expected vs observed
total_bigrams = sum(placement_bigrams.values())
total_unigrams = sum(placement_counts.values())

print(f"\nTotal placement bigrams: {total_bigrams}")
print(f"Unique bigram types: {len(placement_bigrams)}")

# Build expected transition matrix
all_placements = list(set(p for pair in placement_bigrams.keys() for p in pair))
expected_matrix = {}
for p1 in all_placements:
    for p2 in all_placements:
        # Expected under independence
        if total_unigrams > 0:
            expected = (placement_counts[p1] / total_unigrams) * (placement_counts[p2] / total_unigrams) * total_bigrams
        else:
            expected = 0
        expected_matrix[(p1, p2)] = expected

# Find forbidden (much lower than expected) and enriched (much higher than expected)
print("\n--- Forbidden Transitions (observed << expected) ---")
forbidden = []
for (p1, p2), expected in expected_matrix.items():
    observed = placement_bigrams.get((p1, p2), 0)
    if expected >= 5:  # Only consider if expected is substantial
        ratio = observed / expected if expected > 0 else 0
        if ratio < 0.2:  # Less than 20% of expected
            forbidden.append((p1, p2, observed, expected, ratio))

forbidden.sort(key=lambda x: x[4])  # Sort by ratio
print(f"Found {len(forbidden)} potentially forbidden transitions (ratio < 0.2)")
for p1, p2, obs, exp, ratio in forbidden[:15]:
    print(f"  {p1} -> {p2}: observed={obs}, expected={exp:.1f}, ratio={ratio:.2f}")

print("\n--- Enriched Transitions (observed >> expected) ---")
enriched = []
for (p1, p2), observed in placement_bigrams.items():
    expected = expected_matrix.get((p1, p2), 0)
    if expected >= 2:  # Only consider if expected is substantial
        ratio = observed / expected if expected > 0 else float('inf')
        if ratio > 3:  # More than 3x expected
            enriched.append((p1, p2, observed, expected, ratio))

enriched.sort(key=lambda x: -x[4])  # Sort by ratio descending
print(f"Found {len(enriched)} enriched transitions (ratio > 3)")
for p1, p2, obs, exp, ratio in enriched[:15]:
    print(f"  {p1} -> {p2}: observed={obs}, expected={exp:.1f}, ratio={ratio:.2f}")

# Self-transitions
print("\n--- Self-Transitions (same placement repeated) ---")
for p in sorted(all_placements):
    obs = placement_bigrams.get((p, p), 0)
    exp = expected_matrix.get((p, p), 0)
    if exp >= 2:
        ratio = obs / exp if exp > 0 else 0
        status = "ENRICHED" if ratio > 2 else ("DEPLETED" if ratio < 0.5 else "NORMAL")
        print(f"  {p} -> {p}: observed={obs}, expected={exp:.1f}, ratio={ratio:.2f} [{status}]")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("BATCH 1 SUMMARY")
print("=" * 70)

results = {
    'test1_placement_morphology': {
        'prefix_chi2': chi2_prefix,
        'prefix_cramers_v': v_prefix,
        'suffix_chi2': chi2_suffix,
        'suffix_cramers_v': v_suffix,
        'dependency_detected': v_prefix >= 0.1 or v_suffix >= 0.1
    },
    'test7_ordering': {
        'r_series': r_result,
        's_series': s_result,
        'ordering_detected': (r_result and any([r_result.get('word_len_monotonic'),
                                                 r_result.get('middle_len_monotonic'),
                                                 r_result.get('rep_monotonic')])) or
                            (s_result and any([s_result.get('word_len_monotonic'),
                                               s_result.get('middle_len_monotonic'),
                                               s_result.get('rep_monotonic')]))
    },
    'test8_forbidden': {
        'total_bigrams': total_bigrams,
        'unique_bigram_types': len(placement_bigrams),
        'forbidden_count': len(forbidden),
        'enriched_count': len(enriched),
        'forbidden_transitions': [(p1, p2, obs, exp, ratio) for p1, p2, obs, exp, ratio in forbidden[:10]],
        'enriched_transitions': [(p1, p2, obs, exp, ratio) for p1, p2, obs, exp, ratio in enriched[:10]]
    }
}

print(f"""
TEST 1 - Placement × Morphology:
  PREFIX dependency: Cramer's V = {v_prefix:.3f} {'[SIGNAL]' if v_prefix >= 0.1 else '[NO SIGNAL]'}
  SUFFIX dependency: Cramer's V = {v_suffix:.3f} {'[SIGNAL]' if v_suffix >= 0.1 else '[NO SIGNAL]'}

TEST 7 - R1/R2/R3 Ordering:
  R-series monotonic trends detected: {r_result is not None and any([r_result.get('word_len_monotonic'), r_result.get('middle_len_monotonic')])}
  S-series monotonic trends detected: {s_result is not None and any([s_result.get('word_len_monotonic'), s_result.get('middle_len_monotonic')])}

TEST 8 - Forbidden Combinations:
  Forbidden transitions (ratio < 0.2): {len(forbidden)}
  Enriched transitions (ratio > 3): {len(enriched)}
  Structure detected: {len(forbidden) >= 3 or len(enriched) >= 3}
""")

# Save results
with open('phases/AZC_AXIS_axis_connectivity/batch1_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("Results saved to: phases/AZC_AXIS_axis_connectivity/batch1_results.json")
print("\n" + "=" * 70)
print("BATCH 1 COMPLETE")
print("=" * 70)
