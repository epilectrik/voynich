#!/usr/bin/env python3
"""
Phase AAZ: A-AZC Coordination Stress Test

Purpose: Test whether Currier A assets behave as persistent managed entities
whose existence is independent of AZC-encoded action-legality windows.

Tests:
- AAZ-1: Availability vs Legality Decoupling (suppression test)
- AAZ-2: Section x Placement-Type Affinity
- AAZ-3: Multiplicity Persistence Under Legality Constraints

Framing: Stewardship vs Opportunism, NOT seasonal availability.
"""

import os
import json
import random
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

os.chdir('C:/git/voynich')

print("=" * 70)
print("Phase AAZ: A-AZC Coordination Stress Test")
print("Testing: Stewardship vs Opportunism Structure")
print("=" * 70)

# =============================================================================
# DATA LOADING
# =============================================================================

def is_clean_token(token):
    """Filter out damaged/artifact tokens."""
    return '*' not in token and token.isalpha() and len(token) >= 2

# Load all tokens
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip() != 'H':
            continue
        if is_clean_token(row.get('word', '')):
            all_tokens.append(row)

# Separate by language
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]

# Build vocabularies
a_vocab = set(t['word'] for t in a_tokens)
b_vocab = set(t['word'] for t in b_tokens)
azc_vocab = set(t['word'] for t in azc_tokens)

# Shared vocabulary (A tokens that appear in AZC)
a_in_azc = a_vocab & azc_vocab
azc_only = azc_vocab - a_vocab - b_vocab

print(f"\nData loaded:")
print(f"  Currier A tokens: {len(a_tokens):,} ({len(a_vocab):,} types)")
print(f"  Currier B tokens: {len(b_tokens):,} ({len(b_vocab):,} types)")
print(f"  AZC tokens: {len(azc_tokens):,} ({len(azc_vocab):,} types)")
print(f"  A-vocab in AZC: {len(a_in_azc):,} types (shared vocabulary)")
print(f"  AZC-only: {len(azc_only):,} types")

# =============================================================================
# BUILD A-VOCABULARY METADATA
# =============================================================================

# Section affinity for A tokens
a_section_counts = defaultdict(lambda: defaultdict(int))
for t in a_tokens:
    word = t['word']
    section = t.get('section', 'UNK')
    a_section_counts[word][section] += 1

# Determine primary section for each A-vocab token
def get_primary_section(word):
    """Get the section where this word appears most in Currier A."""
    if word not in a_section_counts:
        return None
    counts = a_section_counts[word]
    if not counts:
        return None
    return max(counts, key=counts.get)

a_primary_section = {w: get_primary_section(w) for w in a_vocab}

# =============================================================================
# BUILD AZC PLACEMENT DATA
# =============================================================================

# Get placement for each AZC token
azc_by_placement = defaultdict(list)
azc_token_placements = defaultdict(set)

for t in azc_tokens:
    word = t['word']
    placement = t.get('placement', 'UNK')
    if placement and placement != 'UNK':
        azc_by_placement[placement].append(word)
        azc_token_placements[word].add(placement)

placements = sorted(azc_by_placement.keys())
print(f"\nAZC placements: {len(placements)}")
print(f"  {placements}")

# =============================================================================
# TEST AAZ-1: AVAILABILITY VS LEGALITY DECOUPLING
# =============================================================================

print("\n" + "=" * 70)
print("TEST AAZ-1: AVAILABILITY VS LEGALITY DECOUPLING")
print("Question: Are A-vocab tokens SUPPRESSED when AZC forbids procedures?")
print("=" * 70)

# For each A-vocab token that appears in AZC, count which placements it appears in
a_placement_coverage = {}
for word in a_in_azc:
    if word in azc_token_placements:
        a_placement_coverage[word] = len(azc_token_placements[word])

if a_placement_coverage:
    # Compare to AZC-only tokens
    azc_only_coverage = {}
    for word in azc_only:
        if word in azc_token_placements:
            azc_only_coverage[word] = len(azc_token_placements[word])

    a_mean_coverage = np.mean(list(a_placement_coverage.values()))
    azc_only_mean = np.mean(list(azc_only_coverage.values())) if azc_only_coverage else 0

    print(f"\nPlacement coverage comparison:")
    print(f"  A-vocab tokens in AZC: {len(a_placement_coverage)} types")
    print(f"  Mean placements per A-vocab token: {a_mean_coverage:.2f}")
    print(f"  AZC-only tokens: {len(azc_only_coverage)} types")
    print(f"  Mean placements per AZC-only token: {azc_only_mean:.2f}")

    if azc_only_coverage and a_placement_coverage:
        # Mann-Whitney U test
        u_stat, p_value = stats.mannwhitneyu(
            list(a_placement_coverage.values()),
            list(azc_only_coverage.values()),
            alternative='two-sided'
        )
        print(f"\n  Mann-Whitney U test: U={u_stat:.0f}, p={p_value:.4f}")

        if p_value < 0.05:
            direction = "MORE" if a_mean_coverage > azc_only_mean else "LESS"
            print(f"  SIGNIFICANT: A-vocab has {direction} placement coverage")
        else:
            print(f"  NOT significant: Similar coverage")

    # Suppression test: Do A-vocab tokens avoid certain placements?
    print(f"\nPlacement distribution for A-vocab tokens:")
    a_by_placement = defaultdict(int)
    for word in a_in_azc:
        for p in azc_token_placements.get(word, []):
            a_by_placement[p] += 1

    azc_only_by_placement = defaultdict(int)
    for word in azc_only:
        for p in azc_token_placements.get(word, []):
            azc_only_by_placement[p] += 1

    print(f"\n{'Placement':<12} {'A-vocab':<10} {'AZC-only':<10} {'Ratio':<10}")
    print("-" * 45)

    suppression_ratios = {}
    for p in sorted(set(a_by_placement.keys()) | set(azc_only_by_placement.keys())):
        a_count = a_by_placement[p]
        azc_count = azc_only_by_placement[p]
        if azc_count > 0:
            ratio = a_count / azc_count
            suppression_ratios[p] = ratio
            print(f"{p:<12} {a_count:<10} {azc_count:<10} {ratio:<10.2f}")

    # Check for suppression pattern
    if suppression_ratios:
        mean_ratio = np.mean(list(suppression_ratios.values()))
        low_ratio_placements = [p for p, r in suppression_ratios.items() if r < mean_ratio * 0.5]
        high_ratio_placements = [p for p, r in suppression_ratios.items() if r > mean_ratio * 2]

        print(f"\n  Mean ratio: {mean_ratio:.2f}")
        print(f"  Suppressed placements (ratio < 0.5x mean): {low_ratio_placements}")
        print(f"  Enriched placements (ratio > 2x mean): {high_ratio_placements}")

# Verdict
print("\nAAZ-1 INTERPRETATION:")
if a_placement_coverage:
    if p_value < 0.05:
        if a_mean_coverage > azc_only_mean:
            verdict_1 = "A_BROADER"
            print("  A-vocab tokens appear in MORE placements than AZC-only")
            print("  -> Assets PERSIST across legality windows (STEWARDSHIP)")
        else:
            verdict_1 = "A_RESTRICTED"
            print("  A-vocab tokens appear in FEWER placements than AZC-only")
            print("  -> Assets SUPPRESSED by legality (OPPORTUNISTIC)")
    else:
        verdict_1 = "NO_SUPPRESSION"
        print("  No significant difference in placement coverage")
        print("  -> Assets exist INDEPENDENTLY of legality (STEWARDSHIP)")
else:
    verdict_1 = "INSUFFICIENT_DATA"
    print("  Insufficient shared vocabulary to test")

# =============================================================================
# TEST AAZ-2: SECTION x PLACEMENT-TYPE AFFINITY
# =============================================================================

print("\n" + "=" * 70)
print("TEST AAZ-2: SECTION x PLACEMENT-TYPE AFFINITY")
print("Question: Do A sections associate with AZC placement TYPES?")
print("=" * 70)

# For A-vocab tokens in AZC, check if their A-section correlates with AZC placement
section_placement_matrix = defaultdict(lambda: defaultdict(int))

for word in a_in_azc:
    section = a_primary_section.get(word)
    if section and section in ['H', 'P', 'T']:
        for p in azc_token_placements.get(word, []):
            section_placement_matrix[section][p] += 1

print(f"\nSection x Placement contingency:")
sections = sorted(section_placement_matrix.keys())
placements_found = sorted(set(p for s in section_placement_matrix.values() for p in s.keys()))

if sections and placements_found:
    # Print matrix
    print(f"\n{'Section':<10}", end='')
    for p in placements_found[:10]:  # Limit columns
        print(f"{p:<8}", end='')
    print()
    print("-" * (10 + 8 * min(10, len(placements_found))))

    contingency = []
    for s in sections:
        row = [section_placement_matrix[s][p] for p in placements_found]
        contingency.append(row)
        print(f"{s:<10}", end='')
        for v in row[:10]:
            print(f"{v:<8}", end='')
        print()

    # Chi-square test
    contingency_array = np.array(contingency)
    # Filter to columns with data
    col_sums = contingency_array.sum(axis=0)
    valid_cols = col_sums > 5
    if valid_cols.sum() >= 2 and len(sections) >= 2:
        filtered = contingency_array[:, valid_cols]
        chi2, p_value, dof, expected = stats.chi2_contingency(filtered)

        # Cramer's V
        n = filtered.sum()
        min_dim = min(filtered.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0

        print(f"\nChi-square test: chi2={chi2:.2f}, p={p_value:.4f}, dof={dof}")
        print(f"Cramer's V: {cramers_v:.3f}")

        if p_value < 0.05:
            print(f"SIGNIFICANT: Sections have different placement profiles")
        else:
            print(f"NOT significant: Sections have similar placement profiles")

        verdict_2 = "SIGNIFICANT" if p_value < 0.05 else "NOT_SIGNIFICANT"
        cramers_v_2 = cramers_v
    else:
        print("\nInsufficient data for chi-square test")
        verdict_2 = "INSUFFICIENT_DATA"
        cramers_v_2 = None
else:
    print("\nNo section x placement data to analyze")
    verdict_2 = "NO_DATA"
    cramers_v_2 = None

print("\nAAZ-2 INTERPRETATION:")
if verdict_2 == "SIGNIFICANT":
    print(f"  Sections show DISTINCT placement profiles (V={cramers_v_2:.3f})")
    print("  -> A-sections coordinate with AZC zoning")
elif verdict_2 == "NOT_SIGNIFICANT":
    print("  Sections show SIMILAR placement profiles")
    print("  -> A registry is globally applicable (no spatial coordination)")
else:
    print("  Insufficient data to determine")

# =============================================================================
# TEST AAZ-3: MULTIPLICITY PERSISTENCE UNDER LEGALITY CONSTRAINTS
# =============================================================================

print("\n" + "=" * 70)
print("TEST AAZ-3: MULTIPLICITY PERSISTENCE")
print("Question: Does A repetition count change under AZC constraint?")
print("=" * 70)

# Load multiplicity data from CAS-MULT results
try:
    with open('phases/CAS_currier_a_schema/cas_deep_track1_results.json', 'r') as f:
        mult_data = json.load(f)

    # Get repetition counts by token
    # We need to compute this from raw data
    print("\nAnalyzing multiplicity for shared vocabulary...")

    # Count A-token repetition within entries (simplified approach)
    # Group A tokens by folio+line (entry proxy)
    a_by_entry = defaultdict(list)
    for t in a_tokens:
        key = (t.get('folio', ''), t.get('line_number', ''))
        a_by_entry[key].append(t['word'])

    # For each shared token, compute its typical repetition context
    token_rep_context = defaultdict(list)
    for entry_tokens in a_by_entry.values():
        # Count runs of identical tokens
        if len(entry_tokens) < 2:
            continue
        counts = Counter(entry_tokens)
        for word, count in counts.items():
            if word in a_in_azc:
                token_rep_context[word].append(count)

    # Classify tokens by their typical multiplicity
    high_mult_tokens = set()  # Typically appear 2+ times per entry
    low_mult_tokens = set()   # Typically appear 1 time per entry

    for word, reps in token_rep_context.items():
        mean_rep = np.mean(reps) if reps else 1
        if mean_rep >= 1.5:
            high_mult_tokens.add(word)
        else:
            low_mult_tokens.add(word)

    print(f"\n  High-multiplicity A-tokens (mean rep >= 1.5): {len(high_mult_tokens)}")
    print(f"  Low-multiplicity A-tokens (mean rep < 1.5): {len(low_mult_tokens)}")

    # Compare AZC placement coverage for high vs low multiplicity
    if high_mult_tokens and low_mult_tokens:
        high_mult_coverage = [len(azc_token_placements.get(w, set()))
                             for w in high_mult_tokens if w in azc_token_placements]
        low_mult_coverage = [len(azc_token_placements.get(w, set()))
                            for w in low_mult_tokens if w in azc_token_placements]

        if high_mult_coverage and low_mult_coverage:
            high_mean = np.mean(high_mult_coverage)
            low_mean = np.mean(low_mult_coverage)

            print(f"\n  High-mult mean AZC coverage: {high_mean:.2f} placements")
            print(f"  Low-mult mean AZC coverage: {low_mean:.2f} placements")

            u_stat, p_value = stats.mannwhitneyu(
                high_mult_coverage, low_mult_coverage,
                alternative='two-sided'
            )
            print(f"\n  Mann-Whitney U test: U={u_stat:.0f}, p={p_value:.4f}")

            if p_value < 0.05:
                direction = "BROADER" if high_mean > low_mean else "NARROWER"
                print(f"  SIGNIFICANT: High-mult tokens have {direction} AZC coverage")
                verdict_3 = "SIGNIFICANT"
            else:
                print(f"  NOT significant: Similar coverage regardless of multiplicity")
                verdict_3 = "NOT_SIGNIFICANT"
        else:
            print("\n  Insufficient tokens with AZC placements")
            verdict_3 = "INSUFFICIENT_DATA"
    else:
        print("\n  Could not classify tokens by multiplicity")
        verdict_3 = "NO_DATA"

except Exception as e:
    print(f"\nError loading multiplicity data: {e}")
    verdict_3 = "ERROR"

print("\nAAZ-3 INTERPRETATION:")
if verdict_3 == "SIGNIFICANT":
    print("  Multiplicity affects AZC presence")
    print("  -> Assets are legality-gated (OPPORTUNISTIC)")
elif verdict_3 == "NOT_SIGNIFICANT":
    print("  Multiplicity does NOT affect AZC presence")
    print("  -> Assets PERSIST regardless of repetition context (STEWARDSHIP)")
else:
    print("  Unable to determine")

# =============================================================================
# SYNTHESIS
# =============================================================================

print("\n" + "=" * 70)
print("SYNTHESIS: AAZ PHASE RESULTS")
print("=" * 70)

results = {
    'AAZ-1': {
        'test': 'Availability vs Legality Decoupling',
        'verdict': verdict_1,
        'shared_vocab_size': len(a_in_azc),
        'a_mean_coverage': float(a_mean_coverage) if 'a_mean_coverage' in dir() else None,
        'azc_only_mean': float(azc_only_mean) if 'azc_only_mean' in dir() else None,
    },
    'AAZ-2': {
        'test': 'Section x Placement Affinity',
        'verdict': verdict_2,
        'cramers_v': float(cramers_v_2) if cramers_v_2 else None,
    },
    'AAZ-3': {
        'test': 'Multiplicity Persistence',
        'verdict': verdict_3,
    }
}

# Determine overall interpretation
stewardship_signals = 0
opportunism_signals = 0

if verdict_1 in ['A_BROADER', 'NO_SUPPRESSION']:
    stewardship_signals += 1
elif verdict_1 == 'A_RESTRICTED':
    opportunism_signals += 1

if verdict_2 == 'NOT_SIGNIFICANT':
    stewardship_signals += 1
elif verdict_2 == 'SIGNIFICANT':
    # Could go either way - spatial coordination exists
    pass

if verdict_3 == 'NOT_SIGNIFICANT':
    stewardship_signals += 1
elif verdict_3 == 'SIGNIFICANT':
    opportunism_signals += 1

print(f"\nStewardship signals: {stewardship_signals}")
print(f"Opportunism signals: {opportunism_signals}")

if stewardship_signals > opportunism_signals:
    overall = "STEWARDSHIP_FAVORED"
    print(f"\nOVERALL: Evidence favors MANAGED/STEWARDED system")
    print("  Assets exist independently of action-legality windows")
elif opportunism_signals > stewardship_signals:
    overall = "OPPORTUNISM_FAVORED"
    print(f"\nOVERALL: Evidence favors OPPORTUNISTIC/CONSUMPTIVE system")
    print("  Assets appear mainly when actions are permitted")
else:
    overall = "NEUTRAL"
    print(f"\nOVERALL: NEUTRAL - no clear pattern")

results['overall'] = {
    'stewardship_signals': stewardship_signals,
    'opportunism_signals': opportunism_signals,
    'verdict': overall
}

# Save results
with open('phases/AAZ_a_azc_coordination/aaz_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to phases/AAZ_a_azc_coordination/aaz_results.json")

# =============================================================================
# STOP CONDITION CHECK
# =============================================================================

print("\n" + "=" * 70)
print("STOP CONDITION CHECK")
print("=" * 70)

close_conditions = []

# Check for minimal integration
if len(a_in_azc) < len(a_vocab) * 0.05:
    close_conditions.append("A-AZC overlap < 5% (minimal integration)")

# Check for all-null results
null_count = sum(1 for v in [verdict_1, verdict_2, verdict_3]
                 if v in ['INSUFFICIENT_DATA', 'NO_DATA', 'ERROR'])
if null_count >= 2:
    close_conditions.append(">=2 tests returned no usable data")

if close_conditions:
    print("\nCLOSE CONDITIONS MET:")
    for c in close_conditions:
        print(f"  - {c}")
    print("\nRECOMMENDATION: Phase should CLOSE without new constraints")
else:
    print("\nNo close conditions met. Phase may yield constraints.")
