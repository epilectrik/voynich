#!/usr/bin/env python3
"""
DIRECTION E: MIXED-MARKER ENTRY ANALYSIS

Bounded analysis of the 35.9% of Currier A entries that mix multiple marker classes.

BACKGROUND (from CAS-SCAN):
- 64.1% of A entries = block entries with ONE marker class (exclusive)
- 35.9% of A entries = mixed entries with 2-8 marker classes

QUESTIONS:
- What distinguishes mixed from exclusive entries?
- Are they cross-references? Compound entries? Fallback syntax?
- Do they map to specific B folios or sections?

Tests:
E-1: Mixed entry marker count distribution
E-2: Marker co-occurrence patterns
E-3: Section distribution of mixed entries
E-4: Structural/positional differences

STOP CONDITIONS:
- No pattern beyond random -> noise
- Fully predicted by section -> already known
- Max 2 Tier 2 constraints
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, fisher_exact
import itertools

os.chdir('C:/git/voynich')

print("=" * 70)
print("DIRECTION E: MIXED-MARKER ENTRY ANALYSIS")
print("Bounded analysis of multi-marker entries in Currier A")
print("=" * 70)

# ==========================================================================
# LOAD DATA
# ==========================================================================

print("\nLoading data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Currier A only
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
print(f"Currier A tokens: {len(a_tokens)}")

# ==========================================================================
# DEFINE MARKER CLASSIFICATION
# ==========================================================================

# 8 marker prefixes from CAS analysis
MARKERS = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def get_marker_class(word):
    """Determine which marker class(es) a word belongs to."""
    if not word:
        return set()

    markers = set()
    for m in MARKERS:
        if word.startswith(m):
            markers.add(m.upper())
            break  # Only one prefix per word

    return markers

def classify_line(tokens):
    """Classify a line by its marker composition."""
    markers_found = set()
    for t in tokens:
        word = t.get('word', '')
        markers = get_marker_class(word)
        markers_found.update(markers)

    return markers_found

# ==========================================================================
# BUILD LINE-LEVEL ENTRIES
# ==========================================================================

print("\nBuilding line-level entries...")

# Group tokens by folio and line
line_entries = defaultdict(list)
for t in a_tokens:
    folio = t.get('folio', '')
    line = t.get('line_number', '')  # Use line_number field
    section = t.get('section', '')
    key = (folio, line)
    line_entries[key].append({
        'word': t.get('word', ''),
        'section': section
    })

# Classify each line
line_classifications = {}
for key, tokens in line_entries.items():
    markers = classify_line(tokens)
    section = tokens[0]['section'] if tokens else ''

    line_classifications[key] = {
        'markers': markers,
        'marker_count': len(markers),
        'section': section,
        'token_count': len(tokens),
        'tokens': [t['word'] for t in tokens]
    }

# Separate exclusive (1 marker) vs mixed (2+ markers)
exclusive_lines = {k: v for k, v in line_classifications.items() if v['marker_count'] == 1}
mixed_lines = {k: v for k, v in line_classifications.items() if v['marker_count'] >= 2}
no_marker_lines = {k: v for k, v in line_classifications.items() if v['marker_count'] == 0}

total_lines = len(line_classifications)
print(f"\nLine classification:")
print(f"  Total lines: {total_lines}")
print(f"  Exclusive (1 marker): {len(exclusive_lines)} ({100*len(exclusive_lines)/total_lines:.1f}%)")
print(f"  Mixed (2+ markers): {len(mixed_lines)} ({100*len(mixed_lines)/total_lines:.1f}%)")
print(f"  No markers: {len(no_marker_lines)} ({100*len(no_marker_lines)/total_lines:.1f}%)")

# ==========================================================================
# E-1: MIXED ENTRY MARKER COUNT DISTRIBUTION
# ==========================================================================

print("\n" + "=" * 70)
print("E-1: MIXED ENTRY MARKER COUNT DISTRIBUTION")
print("Question: How many markers per mixed entry?")
print("=" * 70)

# Count distribution for mixed entries
marker_count_dist = Counter(v['marker_count'] for v in mixed_lines.values())

print(f"\nMarker count distribution in mixed entries:")
for count in sorted(marker_count_dist.keys()):
    n = marker_count_dist[count]
    pct = 100 * n / len(mixed_lines)
    print(f"  {count} markers: {n} entries ({pct:.1f}%)")

# Statistics
counts = [v['marker_count'] for v in mixed_lines.values()]
mean_markers = np.mean(counts)
std_markers = np.std(counts)
max_markers = max(counts) if counts else 0

print(f"\nStatistics:")
print(f"  Mean markers per mixed entry: {mean_markers:.2f}")
print(f"  Std: {std_markers:.2f}")
print(f"  Max: {max_markers}")

# ==========================================================================
# E-2: MARKER CO-OCCURRENCE PATTERNS
# ==========================================================================

print("\n" + "=" * 70)
print("E-2: MARKER CO-OCCURRENCE PATTERNS")
print("Question: Which markers appear together in mixed entries?")
print("=" * 70)

# Build co-occurrence matrix
cooccur = defaultdict(int)
marker_solo = Counter()

for v in mixed_lines.values():
    markers = v['markers']
    # Count pairs
    for m1, m2 in itertools.combinations(sorted(markers), 2):
        cooccur[(m1, m2)] += 1
    # Count solo appearances
    for m in markers:
        marker_solo[m] += 1

print(f"\nMarker frequency in mixed entries:")
for m, c in marker_solo.most_common():
    pct = 100 * c / len(mixed_lines)
    print(f"  {m}: {c} ({pct:.1f}%)")

print(f"\nTop marker pairs in mixed entries:")
for pair, count in sorted(cooccur.items(), key=lambda x: -x[1])[:15]:
    pct = 100 * count / len(mixed_lines)
    print(f"  {pair[0]}+{pair[1]}: {count} ({pct:.1f}%)")

# Test for non-random co-occurrence
# Expected under independence: P(A and B) = P(A) * P(B)
print(f"\nCo-occurrence enrichment analysis:")
print(f"{'Pair':<12} {'Observed':<10} {'Expected':<10} {'Ratio':<10} {'Status'}")
print("-" * 55)

pair_analysis = []
for pair, observed in sorted(cooccur.items(), key=lambda x: -x[1])[:10]:
    m1, m2 = pair
    p1 = marker_solo[m1] / len(mixed_lines)
    p2 = marker_solo[m2] / len(mixed_lines)
    expected = p1 * p2 * len(mixed_lines)
    ratio = observed / expected if expected > 0 else 0

    if ratio > 1.5:
        status = "ENRICHED"
    elif ratio < 0.5:
        status = "AVOIDED"
    else:
        status = "NORMAL"

    pair_analysis.append({
        'pair': pair,
        'observed': observed,
        'expected': expected,
        'ratio': ratio,
        'status': status
    })

    print(f"{m1}+{m2}       {observed:<10} {expected:<10.1f} {ratio:<10.2f} {status}")

# Count enriched/avoided
enriched_pairs = [p for p in pair_analysis if p['status'] == 'ENRICHED']
avoided_pairs = [p for p in pair_analysis if p['status'] == 'AVOIDED']

print(f"\nEnriched pairs (>1.5x): {len(enriched_pairs)}")
print(f"Avoided pairs (<0.5x): {len(avoided_pairs)}")

# ==========================================================================
# E-3: SECTION DISTRIBUTION OF MIXED ENTRIES
# ==========================================================================

print("\n" + "=" * 70)
print("E-3: SECTION DISTRIBUTION")
print("Question: Do mixed entries cluster in certain sections?")
print("=" * 70)

# Section distribution
exclusive_sections = Counter(v['section'] for v in exclusive_lines.values())
mixed_sections = Counter(v['section'] for v in mixed_lines.values())

print(f"\nSection distribution comparison:")
print(f"{'Section':<10} {'Exclusive':<15} {'Mixed':<15} {'Mixed Rate':<15}")
print("-" * 55)

section_data = []
all_sections = set(exclusive_sections.keys()) | set(mixed_sections.keys())
for section in sorted(all_sections):
    exc = exclusive_sections.get(section, 0)
    mix = mixed_sections.get(section, 0)
    total = exc + mix
    rate = 100 * mix / total if total > 0 else 0

    section_data.append({
        'section': section,
        'exclusive': exc,
        'mixed': mix,
        'rate': rate
    })

    print(f"{section:<10} {exc:<15} {mix:<15} {rate:.1f}%")

# Chi-square test for section independence
observed_matrix = []
sections_list = sorted(all_sections)
for sec in sections_list:
    if sec:  # Skip empty
        observed_matrix.append([
            exclusive_sections.get(sec, 0),
            mixed_sections.get(sec, 0)
        ])

if len(observed_matrix) > 1:
    observed_matrix = np.array(observed_matrix)
    if observed_matrix.sum() > 0:
        chi2, p, dof, expected = chi2_contingency(observed_matrix)
        print(f"\nChi-square test (section vs entry type):")
        print(f"  Chi2 = {chi2:.2f}, dof = {dof}, p = {p:.6f}")

        if p < 0.05:
            print("  RESULT: Mixed entry rate is SECTION-DEPENDENT")
            e3_verdict = "SECTION_DEPENDENT"
        else:
            print("  RESULT: Mixed entry rate is SECTION-INDEPENDENT")
            e3_verdict = "SECTION_INDEPENDENT"

# ==========================================================================
# E-4: STRUCTURAL/POSITIONAL DIFFERENCES
# ==========================================================================

print("\n" + "=" * 70)
print("E-4: STRUCTURAL DIFFERENCES")
print("Question: Do mixed entries differ structurally from exclusive entries?")
print("=" * 70)

# Token count comparison
exc_token_counts = [v['token_count'] for v in exclusive_lines.values()]
mix_token_counts = [v['token_count'] for v in mixed_lines.values()]

print(f"\nToken count per line:")
print(f"  Exclusive: mean={np.mean(exc_token_counts):.1f}, std={np.std(exc_token_counts):.1f}")
print(f"  Mixed: mean={np.mean(mix_token_counts):.1f}, std={np.std(mix_token_counts):.1f}")

# Mann-Whitney test
from scipy.stats import mannwhitneyu
if exc_token_counts and mix_token_counts:
    stat, p = mannwhitneyu(exc_token_counts, mix_token_counts, alternative='two-sided')
    print(f"  Mann-Whitney p = {p:.6f}")
    if p < 0.05:
        if np.mean(exc_token_counts) < np.mean(mix_token_counts):
            print("  RESULT: Mixed entries are LONGER")
            length_verdict = "MIXED_LONGER"
        else:
            print("  RESULT: Exclusive entries are LONGER")
            length_verdict = "EXCLUSIVE_LONGER"
    else:
        print("  RESULT: No significant length difference")
        length_verdict = "NO_DIFFERENCE"

# Check if mixed entries have special position (first/last lines of folio)
# Get line numbers
def parse_line_number(line_str):
    try:
        return int(line_str)
    except:
        return -1

exc_line_nums = [parse_line_number(k[1]) for k in exclusive_lines.keys()]
mix_line_nums = [parse_line_number(k[1]) for k in mixed_lines.keys()]

exc_line_nums = [n for n in exc_line_nums if n > 0]
mix_line_nums = [n for n in mix_line_nums if n > 0]

print(f"\nLine position in folio:")
print(f"  Exclusive: mean={np.mean(exc_line_nums):.1f}, median={np.median(exc_line_nums):.1f}")
print(f"  Mixed: mean={np.mean(mix_line_nums):.1f}, median={np.median(mix_line_nums):.1f}")

if exc_line_nums and mix_line_nums:
    stat, p = mannwhitneyu(exc_line_nums, mix_line_nums, alternative='two-sided')
    print(f"  Mann-Whitney p = {p:.6f}")
    if p < 0.05:
        print("  RESULT: Position difference detected")
        position_verdict = "POSITION_DIFFERS"
    else:
        print("  RESULT: No significant position difference")
        position_verdict = "NO_DIFFERENCE"

# Check vocabulary overlap with B
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
b_vocab = set(t.get('word', '') for t in b_tokens)

def get_b_overlap(tokens):
    """Calculate fraction of tokens that appear in B vocabulary."""
    words = [t for t in tokens if t]
    if not words:
        return 0
    in_b = sum(1 for w in words if w in b_vocab)
    return in_b / len(words)

exc_b_overlap = [get_b_overlap(v['tokens']) for v in exclusive_lines.values()]
mix_b_overlap = [get_b_overlap(v['tokens']) for v in mixed_lines.values()]

print(f"\nB-vocabulary overlap:")
print(f"  Exclusive: mean={100*np.mean(exc_b_overlap):.1f}%")
print(f"  Mixed: mean={100*np.mean(mix_b_overlap):.1f}%")

if exc_b_overlap and mix_b_overlap:
    stat, p = mannwhitneyu(exc_b_overlap, mix_b_overlap, alternative='two-sided')
    print(f"  Mann-Whitney p = {p:.6f}")
    if p < 0.05:
        if np.mean(exc_b_overlap) < np.mean(mix_b_overlap):
            print("  RESULT: Mixed entries have MORE B-vocabulary")
            b_overlap_verdict = "MIXED_MORE_B"
        else:
            print("  RESULT: Exclusive entries have MORE B-vocabulary")
            b_overlap_verdict = "EXCLUSIVE_MORE_B"
    else:
        print("  RESULT: No significant B-vocabulary difference")
        b_overlap_verdict = "NO_DIFFERENCE"

# ==========================================================================
# E-5: MARKER DOMINANCE IN MIXED ENTRIES
# ==========================================================================

print("\n" + "=" * 70)
print("E-5: MARKER DOMINANCE PATTERNS")
print("Question: In mixed entries, is one marker dominant or are they balanced?")
print("=" * 70)

# For each mixed entry, count tokens per marker
dominance_ratios = []
for v in mixed_lines.values():
    tokens = v['tokens']
    marker_counts = Counter()
    for word in tokens:
        markers = get_marker_class(word)
        for m in markers:
            marker_counts[m] += 1

    if len(marker_counts) >= 2 and sum(marker_counts.values()) > 0:
        # Dominance ratio = max / total
        total = sum(marker_counts.values())
        if total > 0:
            max_count = max(marker_counts.values())
            dominance = max_count / total
            dominance_ratios.append(dominance)

print(f"\nDominance ratio (max marker / total marked tokens):")
print(f"  Mean: {np.mean(dominance_ratios):.2f}")
print(f"  Std: {np.std(dominance_ratios):.2f}")
print(f"  Min: {min(dominance_ratios):.2f}")
print(f"  Max: {max(dominance_ratios):.2f}")

# Distribution
dom_bins = [(0, 0.5), (0.5, 0.67), (0.67, 0.8), (0.8, 0.9), (0.9, 1.0)]
print(f"\nDominance distribution:")
for low, high in dom_bins:
    count = sum(1 for d in dominance_ratios if low <= d < high)
    pct = 100 * count / len(dominance_ratios) if dominance_ratios else 0
    if high == 1.0:
        count = sum(1 for d in dominance_ratios if low <= d <= high)
    print(f"  {low:.0%}-{high:.0%}: {count} ({pct:.1f}%)")

if np.mean(dominance_ratios) > 0.7:
    dom_verdict = "ONE_DOMINANT"
    print(f"\nVERDICT: Mixed entries typically have ONE DOMINANT marker ({np.mean(dominance_ratios):.0%})")
else:
    dom_verdict = "BALANCED"
    print(f"\nVERDICT: Mixed entries have BALANCED marker distribution")

# ==========================================================================
# SUMMARY AND VERDICT
# ==========================================================================

print("\n" + "=" * 70)
print("DIRECTION E: SUMMARY AND VERDICT")
print("=" * 70)

results = {
    'e1_marker_distribution': {
        'mean_markers': mean_markers,
        'std_markers': std_markers,
        'max_markers': max_markers,
        'count_distribution': dict(marker_count_dist)
    },
    'e2_cooccurrence': {
        'enriched_pairs': len(enriched_pairs),
        'avoided_pairs': len(avoided_pairs),
        'top_pairs': [(p['pair'], p['ratio']) for p in pair_analysis[:5]]
    },
    'e3_section': {
        'verdict': e3_verdict,
        'section_rates': {s['section']: s['rate'] for s in section_data}
    },
    'e4_structural': {
        'length_verdict': length_verdict,
        'exc_mean_length': np.mean(exc_token_counts),
        'mix_mean_length': np.mean(mix_token_counts),
        'b_overlap_verdict': b_overlap_verdict,
        'exc_b_overlap': np.mean(exc_b_overlap),
        'mix_b_overlap': np.mean(mix_b_overlap)
    },
    'e5_dominance': {
        'mean_dominance': np.mean(dominance_ratios),
        'verdict': dom_verdict
    }
}

# Determine overall findings
findings = []

if len(enriched_pairs) > 0 or len(avoided_pairs) > 0:
    findings.append(f"E-2: {len(enriched_pairs)} enriched pairs, {len(avoided_pairs)} avoided pairs - CO-OCCURRENCE NOT RANDOM")

if e3_verdict == "SECTION_DEPENDENT":
    findings.append("E-3: Mixed entry rate is SECTION-DEPENDENT")

if length_verdict != "NO_DIFFERENCE":
    findings.append(f"E-4: Length difference: {length_verdict}")

if b_overlap_verdict != "NO_DIFFERENCE":
    findings.append(f"E-4: B-overlap difference: {b_overlap_verdict}")

if dom_verdict == "ONE_DOMINANT":
    findings.append(f"E-5: Mixed entries have ONE DOMINANT marker ({np.mean(dominance_ratios):.0%} dominance)")

print(f"\nFINDINGS:")
if findings:
    for f in findings:
        print(f"  - {f}")
else:
    print("  - No significant patterns detected")

# Hard stop evaluation
print(f"\nHARD STOP EVALUATION:")

patterns_found = len(findings) > 0
already_known = e3_verdict == "SECTION_DEPENDENT" and len(findings) == 1

if not patterns_found:
    print("  STOP 1: No patterns -> TRIGGERED (noise)")
    overall_verdict = "NO_PATTERN"
elif already_known:
    print("  STOP 2: Only section dependence -> TRIGGERED (already known)")
    overall_verdict = "SECTION_ONLY"
else:
    print("  STOP 1: Patterns found -> NOT triggered")
    print("  STOP 2: New findings -> NOT triggered")
    overall_verdict = "NEW_STRUCTURE"

print(f"\nOVERALL VERDICT: {overall_verdict}")

# Proposed constraints
constraints = []
if overall_verdict == "NEW_STRUCTURE":
    if dom_verdict == "ONE_DOMINANT":
        constraints.append(f"Mixed entries have ONE DOMINANT marker ({np.mean(dominance_ratios):.0%} mean dominance); mixing is asymmetric, not balanced")

    if len(enriched_pairs) > 0:
        top_enriched = [p['pair'] for p in pair_analysis if p['status'] == 'ENRICHED'][:3]
        constraints.append(f"Marker co-occurrence is non-random; enriched pairs: {top_enriched}")

print(f"\nPROPOSED CONSTRAINTS ({len(constraints)}):")
for c in constraints:
    print(f"  - {c}")

print("\n" + "=" * 70)
print("DIRECTION E: CLOSED")
print("Mixed-marker entry investigation is now COMPLETE.")
print("=" * 70)

# Save results
os.makedirs('phases/MIXED_marker_entry_analysis', exist_ok=True)
with open('phases/MIXED_marker_entry_analysis/mixed_entry_results.json', 'w') as f:
    # Convert tuples to strings for JSON
    results_json = json.loads(json.dumps(results, default=str))
    json.dump(results_json, f, indent=2)

print("\nResults saved to phases/MIXED_marker_entry_analysis/mixed_entry_results.json")
