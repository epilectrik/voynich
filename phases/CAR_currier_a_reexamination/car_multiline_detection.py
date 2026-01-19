#!/usr/bin/env python
"""
CAR Phase: Multi-Line Record Detection

Tests whether some Currier A records span multiple lines.

If LINE = RECORD is absolute, boundary markers are stylistic.
If multi-line records exist, boundary markers serve structural function.

Tests:
1. Missing boundary marker patterns
2. Adjacent line correlation when markers missing
3. Continuation signal detection
4. MI recalculation for marker-based groupings
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from itertools import combinations

from car_data_loader import CARDataLoader, PHASE_DIR

# CAR-identified boundary tokens (from previous analysis)
STARTERS = {'tol', 'dchor', 'sor', 'qotol'}
TERMINATORS = {'dan', 'dam', 'sal', 'd', 'dy'}


def get_line_boundary_status(tokens):
    """
    Classify a line by its boundary marker status.

    Returns: (has_starter, has_terminator)
    """
    if not tokens:
        return False, False

    tokens_lower = [str(t).lower() for t in tokens]

    # Check first token for starter
    has_starter = tokens_lower[0] in STARTERS

    # Check last token for terminator
    has_terminator = tokens_lower[-1] in TERMINATORS

    return has_starter, has_terminator


def test_1_missing_marker_patterns():
    """
    Test 1: Do lines without terminators precede lines without starters?

    If multi-line records exist:
    - Line without terminator = record continues
    - Line without starter = record continuation
    - These should co-occur at adjacent positions
    """
    print("\n" + "=" * 70)
    print("Test 1: Missing Marker Co-occurrence")
    print("=" * 70)
    print("Hypothesis: Lines without terminators precede lines without starters")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build line sequence by folio
    folio_lines = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = list(group['word'].values)
        has_starter, has_terminator = get_line_boundary_status(tokens)
        folio_lines[folio].append({
            'line_num': line_num,
            'tokens': tokens,
            'has_starter': has_starter,
            'has_terminator': has_terminator
        })

    # Sort lines within each folio
    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: x['line_num'])

    # Count patterns
    total_adjacent_pairs = 0
    no_term_then_no_start = 0  # Potential continuation
    no_term_then_has_start = 0
    has_term_then_no_start = 0
    has_term_then_has_start = 0

    # Track specific cases
    potential_continuations = []

    for folio, lines in folio_lines.items():
        for i in range(len(lines) - 1):
            line1 = lines[i]
            line2 = lines[i + 1]

            total_adjacent_pairs += 1

            if not line1['has_terminator'] and not line2['has_starter']:
                no_term_then_no_start += 1
                potential_continuations.append({
                    'folio': folio,
                    'line1': line1['line_num'],
                    'line2': line2['line_num'],
                    'tokens1': line1['tokens'][-3:] if len(line1['tokens']) >= 3 else line1['tokens'],
                    'tokens2': line2['tokens'][:3] if len(line2['tokens']) >= 3 else line2['tokens']
                })
            elif not line1['has_terminator'] and line2['has_starter']:
                no_term_then_has_start += 1
            elif line1['has_terminator'] and not line2['has_starter']:
                has_term_then_no_start += 1
            else:
                has_term_then_has_start += 1

    print(f"\nTotal adjacent line pairs: {total_adjacent_pairs}")
    print(f"\nTransition matrix:")
    print(f"                          Next line:")
    print(f"                    No starter    Has starter")
    print(f"  Prev line:")
    print(f"    No terminator     {no_term_then_no_start:4d}           {no_term_then_has_start:4d}")
    print(f"    Has terminator    {has_term_then_no_start:4d}           {has_term_then_has_start:4d}")

    # Calculate rates
    lines_without_term = no_term_then_no_start + no_term_then_has_start
    lines_with_term = has_term_then_no_start + has_term_then_has_start

    no_start_rate_after_no_term = no_term_then_no_start / lines_without_term if lines_without_term > 0 else 0
    no_start_rate_after_has_term = has_term_then_no_start / lines_with_term if lines_with_term > 0 else 0

    print(f"\nRate of 'no starter' after 'no terminator': {100*no_start_rate_after_no_term:.1f}%")
    print(f"Rate of 'no starter' after 'has terminator': {100*no_start_rate_after_has_term:.1f}%")

    # Chi-square test for independence
    contingency = [
        [no_term_then_no_start, no_term_then_has_start],
        [has_term_then_no_start, has_term_then_has_start]
    ]

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    print(f"\nChi-square test for independence:")
    print(f"  Chi2 = {chi2:.2f}, p = {p_value:.4f}")

    # If multi-line records exist, no_term_then_no_start should be enriched
    enrichment = no_start_rate_after_no_term / no_start_rate_after_has_term if no_start_rate_after_has_term > 0 else float('inf')

    print(f"\nEnrichment (no-start after no-term vs after has-term): {enrichment:.2f}x")

    # Show examples of potential continuations
    print(f"\nPotential continuation pairs (first 10):")
    for pc in potential_continuations[:10]:
        print(f"  {pc['folio']} L{pc['line1']}->{pc['line2']}: ...{pc['tokens1']} | {pc['tokens2']}...")

    result = {
        'test': 'missing_marker_cooccurrence',
        'total_pairs': total_adjacent_pairs,
        'no_term_no_start': no_term_then_no_start,
        'no_term_has_start': no_term_then_has_start,
        'has_term_no_start': has_term_then_no_start,
        'has_term_has_start': has_term_then_has_start,
        'no_start_rate_after_no_term': no_start_rate_after_no_term,
        'no_start_rate_after_has_term': no_start_rate_after_has_term,
        'enrichment': enrichment,
        'chi2': chi2,
        'p_value': p_value,
        'n_potential_continuations': len(potential_continuations)
    }

    if p_value < 0.05 and enrichment > 1.5:
        result['verdict'] = 'CONTINUATION_SIGNAL'
        print(f"\n-> VERDICT: CONTINUATION_SIGNAL")
        print(f"   Missing markers co-occur more than expected")
    else:
        result['verdict'] = 'NO_SIGNAL'
        print(f"\n-> VERDICT: NO_SIGNAL")
        print(f"   Missing markers are independent")

    return result


def test_2_vocabulary_overlap_by_markers():
    """
    Test 2: Do adjacent lines share more vocabulary when markers are missing?

    If multi-line records exist, lines that are part of the same record
    should have higher vocabulary overlap.
    """
    print("\n" + "=" * 70)
    print("Test 2: Vocabulary Overlap by Marker Status")
    print("=" * 70)
    print("Hypothesis: Higher overlap when boundary markers are missing")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build line data
    folio_lines = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        has_starter, has_terminator = get_line_boundary_status(tokens)
        folio_lines[folio].append({
            'line_num': line_num,
            'tokens': set(tokens),
            'has_starter': has_starter,
            'has_terminator': has_terminator
        })

    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: x['line_num'])

    def jaccard(set1, set2):
        if not set1 or not set2:
            return 0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0

    # Calculate overlap for different marker configurations
    overlap_no_term_no_start = []  # Potential multi-line
    overlap_has_term_has_start = []  # Clear single-line
    overlap_other = []  # Mixed

    for folio, lines in folio_lines.items():
        for i in range(len(lines) - 1):
            line1 = lines[i]
            line2 = lines[i + 1]

            j = jaccard(line1['tokens'], line2['tokens'])

            if not line1['has_terminator'] and not line2['has_starter']:
                overlap_no_term_no_start.append(j)
            elif line1['has_terminator'] and line2['has_starter']:
                overlap_has_term_has_start.append(j)
            else:
                overlap_other.append(j)

    mean_potential = np.mean(overlap_no_term_no_start) if overlap_no_term_no_start else 0
    mean_clear = np.mean(overlap_has_term_has_start) if overlap_has_term_has_start else 0
    mean_other = np.mean(overlap_other) if overlap_other else 0

    print(f"\nMean Jaccard overlap:")
    print(f"  Potential multi-line (no-term -> no-start): {mean_potential:.4f} (n={len(overlap_no_term_no_start)})")
    print(f"  Clear single-line (has-term -> has-start): {mean_clear:.4f} (n={len(overlap_has_term_has_start)})")
    print(f"  Other configurations: {mean_other:.4f} (n={len(overlap_other)})")

    # Statistical test
    if len(overlap_no_term_no_start) >= 5 and len(overlap_has_term_has_start) >= 5:
        stat, p_value = stats.mannwhitneyu(
            overlap_no_term_no_start,
            overlap_has_term_has_start,
            alternative='greater'
        )
        print(f"\nMann-Whitney U test (potential > clear):")
        print(f"  U = {stat:.1f}, p = {p_value:.4f}")
    else:
        p_value = 1.0
        print("\nInsufficient samples for statistical test")

    ratio = mean_potential / mean_clear if mean_clear > 0 else float('inf')
    print(f"\nOverlap ratio (potential / clear): {ratio:.2f}x")

    result = {
        'test': 'vocabulary_overlap',
        'mean_potential_multiline': mean_potential,
        'n_potential': len(overlap_no_term_no_start),
        'mean_clear_singleline': mean_clear,
        'n_clear': len(overlap_has_term_has_start),
        'mean_other': mean_other,
        'n_other': len(overlap_other),
        'overlap_ratio': ratio,
        'p_value': p_value
    }

    if p_value < 0.05 and ratio > 1.2:
        result['verdict'] = 'HIGHER_OVERLAP'
        print(f"\n-> VERDICT: HIGHER_OVERLAP")
        print(f"   Potential multi-line pairs have significantly higher vocabulary overlap")
    else:
        result['verdict'] = 'NO_DIFFERENCE'
        print(f"\n-> VERDICT: NO_DIFFERENCE")
        print(f"   Vocabulary overlap is similar regardless of markers")

    return result


def test_3_marker_absence_rates():
    """
    Test 3: What fraction of lines are missing boundary markers?

    If LINE = RECORD is absolute, we'd expect random variation.
    If multi-line records exist, we'd expect systematic patterns.
    """
    print("\n" + "=" * 70)
    print("Test 3: Boundary Marker Absence Rates")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Classify all lines
    line_classifications = []

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = list(group['word'].values)
        has_starter, has_terminator = get_line_boundary_status(tokens)

        line_classifications.append({
            'folio': folio,
            'line_num': line_num,
            'n_tokens': len(tokens),
            'has_starter': has_starter,
            'has_terminator': has_terminator
        })

    df = pd.DataFrame(line_classifications)

    total_lines = len(df)
    has_both = len(df[(df['has_starter']) & (df['has_terminator'])])
    has_starter_only = len(df[(df['has_starter']) & (~df['has_terminator'])])
    has_terminator_only = len(df[(~df['has_starter']) & (df['has_terminator'])])
    has_neither = len(df[(~df['has_starter']) & (~df['has_terminator'])])

    print(f"\nLine classification:")
    print(f"  Total lines: {total_lines}")
    print(f"  Has both markers: {has_both} ({100*has_both/total_lines:.1f}%)")
    print(f"  Has starter only: {has_starter_only} ({100*has_starter_only/total_lines:.1f}%)")
    print(f"  Has terminator only: {has_terminator_only} ({100*has_terminator_only/total_lines:.1f}%)")
    print(f"  Has neither: {has_neither} ({100*has_neither/total_lines:.1f}%)")

    # If markers are independent, we can calculate expected
    starter_rate = (has_both + has_starter_only) / total_lines
    terminator_rate = (has_both + has_terminator_only) / total_lines

    expected_both = starter_rate * terminator_rate * total_lines
    expected_neither = (1 - starter_rate) * (1 - terminator_rate) * total_lines

    print(f"\nMarker rates:")
    print(f"  Starter rate: {100*starter_rate:.1f}%")
    print(f"  Terminator rate: {100*terminator_rate:.1f}%")
    print(f"\nExpected under independence:")
    print(f"  Both: {expected_both:.1f} (observed: {has_both})")
    print(f"  Neither: {expected_neither:.1f} (observed: {has_neither})")

    # Chi-square test for independence of markers
    contingency = [
        [has_both, has_starter_only],
        [has_terminator_only, has_neither]
    ]
    chi2, p_value, _, _ = stats.chi2_contingency(contingency)

    print(f"\nChi-square test (starter-terminator independence):")
    print(f"  Chi2 = {chi2:.2f}, p = {p_value:.4f}")

    # Check by line length
    print(f"\nMarker rates by line length:")
    for length_cat, (min_len, max_len) in [('short', (1, 3)), ('medium', (4, 7)), ('long', (8, 100))]:
        subset = df[(df['n_tokens'] >= min_len) & (df['n_tokens'] <= max_len)]
        if len(subset) > 0:
            s_rate = subset['has_starter'].mean()
            t_rate = subset['has_terminator'].mean()
            print(f"  {length_cat} ({min_len}-{max_len} tokens, n={len(subset)}): starter={100*s_rate:.1f}%, terminator={100*t_rate:.1f}%")

    result = {
        'test': 'marker_absence_rates',
        'total_lines': total_lines,
        'has_both': has_both,
        'has_starter_only': has_starter_only,
        'has_terminator_only': has_terminator_only,
        'has_neither': has_neither,
        'starter_rate': starter_rate,
        'terminator_rate': terminator_rate,
        'chi2': chi2,
        'p_value': p_value
    }

    if p_value < 0.05:
        result['verdict'] = 'MARKERS_DEPENDENT'
        print(f"\n-> VERDICT: MARKERS_DEPENDENT")
        print(f"   Starter and terminator presence are NOT independent")
    else:
        result['verdict'] = 'MARKERS_INDEPENDENT'
        print(f"\n-> VERDICT: MARKERS_INDEPENDENT")
        print(f"   Markers appear independently (stylistic)")

    return result


def test_4_recalculate_mi_for_groupings():
    """
    Test 4: Recalculate MI treating potential multi-line as single records.

    Original MI=0 was calculated line-by-line.
    If we group lines that might be continuations, does MI increase?
    """
    print("\n" + "=" * 70)
    print("Test 4: MI Recalculation with Groupings")
    print("=" * 70)
    print("Question: Does MI increase if we group potential multi-line records?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build lines with marker status
    folio_lines = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        has_starter, has_terminator = get_line_boundary_status(tokens)
        folio_lines[folio].append({
            'line_num': line_num,
            'tokens': tokens,
            'has_starter': has_starter,
            'has_terminator': has_terminator
        })

    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: x['line_num'])

    # Create two versions of "records":
    # Version A: Each line is a record (original)
    # Version B: Merge lines where terminator missing + next line starter missing

    records_original = []
    records_merged = []

    for folio, lines in folio_lines.items():
        # Original: each line is a record
        for line in lines:
            records_original.append(line['tokens'])

        # Merged: combine potential continuations
        i = 0
        while i < len(lines):
            current_record = list(lines[i]['tokens'])

            # Check if this line continues
            while (i < len(lines) - 1 and
                   not lines[i]['has_terminator'] and
                   not lines[i + 1]['has_starter']):
                i += 1
                current_record.extend(lines[i]['tokens'])

            records_merged.append(current_record)
            i += 1

    print(f"\nRecord counts:")
    print(f"  Original (line = record): {len(records_original)}")
    print(f"  Merged (potential multi-line): {len(records_merged)}")
    print(f"  Reduction: {len(records_original) - len(records_merged)} records merged")

    # Calculate vocabulary overlap between adjacent records
    def calc_adjacent_overlap(records):
        overlaps = []
        for i in range(len(records) - 1):
            set1 = set(records[i])
            set2 = set(records[i + 1])
            if set1 and set2:
                j = len(set1 & set2) / len(set1 | set2)
                overlaps.append(j)
        return overlaps

    overlap_original = calc_adjacent_overlap(records_original)
    overlap_merged = calc_adjacent_overlap(records_merged)

    mean_original = np.mean(overlap_original) if overlap_original else 0
    mean_merged = np.mean(overlap_merged) if overlap_merged else 0

    print(f"\nAdjacent record vocabulary overlap (proxy for MI):")
    print(f"  Original: {mean_original:.4f}")
    print(f"  Merged: {mean_merged:.4f}")

    if mean_original > 0:
        change = (mean_merged - mean_original) / mean_original * 100
        print(f"  Change: {change:+.1f}%")

    # If merging reduces overlap, it means we correctly grouped related lines
    # If merging increases or doesn't change overlap, lines were independent

    result = {
        'test': 'mi_recalculation',
        'n_records_original': len(records_original),
        'n_records_merged': len(records_merged),
        'n_merged': len(records_original) - len(records_merged),
        'mean_overlap_original': mean_original,
        'mean_overlap_merged': mean_merged
    }

    if mean_merged < mean_original * 0.9:  # 10% reduction
        result['verdict'] = 'GROUPING_REDUCES_OVERLAP'
        result['interpretation'] = 'Merging potential continuations reduces inter-record overlap'
        print(f"\n-> VERDICT: GROUPING_REDUCES_OVERLAP")
        print(f"   Suggests merged lines WERE related")
    elif mean_merged > mean_original * 1.1:
        result['verdict'] = 'GROUPING_INCREASES_OVERLAP'
        result['interpretation'] = 'Merging increases overlap (unexpected)'
        print(f"\n-> VERDICT: GROUPING_INCREASES_OVERLAP")
    else:
        result['verdict'] = 'NO_CHANGE'
        result['interpretation'] = 'Merging does not affect overlap - lines were independent'
        print(f"\n-> VERDICT: NO_CHANGE")
        print(f"   Lines appear to be independent records")

    return result


def test_5_folio_boundary_behavior():
    """
    Test 5: Do boundary markers behave differently at folio edges?

    If multi-line records exist but can't cross folios,
    we'd expect high terminator rate at folio-final and
    high starter rate at folio-initial.
    """
    print("\n" + "=" * 70)
    print("Test 5: Folio Boundary Behavior")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build lines by folio
    folio_lines = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = list(group['word'].values)
        has_starter, has_terminator = get_line_boundary_status(tokens)
        folio_lines[folio].append({
            'line_num': line_num,
            'has_starter': has_starter,
            'has_terminator': has_terminator
        })

    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: x['line_num'])

    # Check first and last lines of each folio
    folio_first_starter = 0
    folio_first_total = 0
    folio_last_terminator = 0
    folio_last_total = 0
    middle_starter = 0
    middle_terminator = 0
    middle_total = 0

    for folio, lines in folio_lines.items():
        if len(lines) < 3:
            continue

        # First line
        folio_first_total += 1
        if lines[0]['has_starter']:
            folio_first_starter += 1

        # Last line
        folio_last_total += 1
        if lines[-1]['has_terminator']:
            folio_last_terminator += 1

        # Middle lines
        for line in lines[1:-1]:
            middle_total += 1
            if line['has_starter']:
                middle_starter += 1
            if line['has_terminator']:
                middle_terminator += 1

    first_starter_rate = folio_first_starter / folio_first_total if folio_first_total > 0 else 0
    last_term_rate = folio_last_terminator / folio_last_total if folio_last_total > 0 else 0
    middle_starter_rate = middle_starter / middle_total if middle_total > 0 else 0
    middle_term_rate = middle_terminator / middle_total if middle_total > 0 else 0

    print(f"\nFolio-first lines (n={folio_first_total}):")
    print(f"  Starter rate: {100*first_starter_rate:.1f}%")
    print(f"  vs middle lines: {100*middle_starter_rate:.1f}%")
    print(f"  Enrichment: {first_starter_rate/middle_starter_rate:.2f}x" if middle_starter_rate > 0 else "  (no baseline)")

    print(f"\nFolio-last lines (n={folio_last_total}):")
    print(f"  Terminator rate: {100*last_term_rate:.1f}%")
    print(f"  vs middle lines: {100*middle_term_rate:.1f}%")
    print(f"  Enrichment: {last_term_rate/middle_term_rate:.2f}x" if middle_term_rate > 0 else "  (no baseline)")

    result = {
        'test': 'folio_boundary_behavior',
        'folio_first_starter_rate': first_starter_rate,
        'folio_last_terminator_rate': last_term_rate,
        'middle_starter_rate': middle_starter_rate,
        'middle_terminator_rate': middle_term_rate,
        'first_enrichment': first_starter_rate / middle_starter_rate if middle_starter_rate > 0 else 0,
        'last_enrichment': last_term_rate / middle_term_rate if middle_term_rate > 0 else 0
    }

    first_enrich = result['first_enrichment']
    last_enrich = result['last_enrichment']

    if first_enrich > 1.5 and last_enrich > 1.5:
        result['verdict'] = 'FOLIO_BOUNDARY_ENRICHED'
        print(f"\n-> VERDICT: FOLIO_BOUNDARY_ENRICHED")
        print(f"   Records respect folio boundaries")
    else:
        result['verdict'] = 'NO_FOLIO_EFFECT'
        print(f"\n-> VERDICT: NO_FOLIO_EFFECT")
        print(f"   Markers not specially enriched at folio edges")

    return result


def run_multiline_detection():
    """Run all multi-line record detection tests."""
    print("\n" + "=" * 80)
    print("CAR MULTI-LINE RECORD DETECTION")
    print("=" * 80)
    print("\nQuestion: Do some Currier A records span multiple lines?")
    print("If yes: boundary markers serve structural function")
    print("If no: boundary markers are stylistic convention")

    results = {
        'phase': 'CAR-ML',
        'name': 'Multi-Line Record Detection',
        'tests': {}
    }

    results['tests']['test_1'] = test_1_missing_marker_patterns()
    results['tests']['test_2'] = test_2_vocabulary_overlap_by_markers()
    results['tests']['test_3'] = test_3_marker_absence_rates()
    results['tests']['test_4'] = test_4_recalculate_mi_for_groupings()
    results['tests']['test_5'] = test_5_folio_boundary_behavior()

    # Summary
    print("\n" + "=" * 80)
    print("MULTI-LINE DETECTION SUMMARY")
    print("=" * 80)

    print("\nTest Results:")
    for test_id, test in results['tests'].items():
        print(f"  {test_id}: {test['verdict']}")

    # Overall interpretation
    continuation_evidence = 0
    independence_evidence = 0

    if results['tests']['test_1']['verdict'] == 'CONTINUATION_SIGNAL':
        continuation_evidence += 1
    else:
        independence_evidence += 1

    if results['tests']['test_2']['verdict'] == 'HIGHER_OVERLAP':
        continuation_evidence += 1
    else:
        independence_evidence += 1

    if results['tests']['test_3']['verdict'] == 'MARKERS_DEPENDENT':
        continuation_evidence += 1
    else:
        independence_evidence += 1

    if results['tests']['test_4']['verdict'] == 'GROUPING_REDUCES_OVERLAP':
        continuation_evidence += 1
    else:
        independence_evidence += 1

    print(f"\nEvidence for multi-line records: {continuation_evidence}/4")
    print(f"Evidence for line independence: {independence_evidence}/4")

    if continuation_evidence >= 3:
        overall = 'MULTI_LINE_LIKELY'
        summary = 'Multiple tests suggest some records span lines'
    elif independence_evidence >= 3:
        overall = 'LINE_EQUALS_RECORD'
        summary = 'Lines appear to be independent records; markers are stylistic'
    else:
        overall = 'INCONCLUSIVE'
        summary = 'Mixed evidence; further investigation needed'

    results['overall_verdict'] = overall
    results['summary'] = summary
    results['continuation_evidence'] = continuation_evidence
    results['independence_evidence'] = independence_evidence

    print(f"\n-> OVERALL VERDICT: {overall}")
    print(f"   {summary}")

    # Save results
    output_file = PHASE_DIR / 'car_multiline_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_multiline_detection()
