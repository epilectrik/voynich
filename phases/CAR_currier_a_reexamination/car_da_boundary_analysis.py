#!/usr/bin/env python
"""
CAR Phase: DA-Boundary Token Relationship Analysis

Tests the hypothesis that CAR "boundary markers" are actually internal structure
markers related to DA-segmented sub-records, not line delimiters.

Questions:
1. Do "terminators" appear immediately before DA tokens within lines?
2. Do "starters" appear immediately after DA tokens within lines?
3. Are these tokens characteristic of first/last sub-records?

If true: LINE = RECORD remains solid, boundary tokens mark internal structure.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

from car_data_loader import CARDataLoader, PHASE_DIR

# CAR-identified boundary tokens
STARTERS = {'tol', 'dchor', 'sor', 'qotol'}
TERMINATORS = {'dan', 'dam', 'sal', 'd', 'dy'}

# DA-family tokens (C422)
DA_TOKENS = {'da', 'daiin', 'dain', 'dal', 'dam', 'dan', 'dar', 'daiiin', 'daim'}


def is_da_family(token):
    """Check if token is DA-family (starts with 'da' or is in known set)."""
    token = str(token).lower()
    return token.startswith('da') or token in DA_TOKENS


def test_1_terminator_da_adjacency():
    """
    Test 1: Do terminators appear immediately BEFORE DA tokens?

    If terminators mark the end of sub-records, they should appear
    right before DA (which separates sub-records).
    """
    print("\n" + "=" * 70)
    print("Test 1: Terminator-DA Adjacency")
    print("=" * 70)
    print("Hypothesis: Terminators appear before DA tokens (end of sub-records)")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Group by line
    terminator_before_da = 0
    terminator_not_before_da = 0
    da_preceded_by_terminator = 0
    da_not_preceded_by_terminator = 0

    # Track what precedes DA
    da_predecessors = Counter()

    for (folio, line), group in a_data.groupby(['folio', 'line_number']):
        tokens = list(group['word'].values)
        if len(tokens) < 2:
            continue

        for i in range(len(tokens) - 1):
            curr = str(tokens[i]).lower()
            next_tok = str(tokens[i + 1]).lower()

            # Is current a terminator?
            if curr in TERMINATORS:
                if is_da_family(next_tok):
                    terminator_before_da += 1
                else:
                    terminator_not_before_da += 1

            # Is next a DA token?
            if is_da_family(next_tok):
                da_predecessors[curr] += 1
                if curr in TERMINATORS:
                    da_preceded_by_terminator += 1
                else:
                    da_not_preceded_by_terminator += 1

    total_terminators = terminator_before_da + terminator_not_before_da
    total_da = da_preceded_by_terminator + da_not_preceded_by_terminator

    term_da_rate = terminator_before_da / total_terminators if total_terminators > 0 else 0
    da_term_rate = da_preceded_by_terminator / total_da if total_da > 0 else 0

    print(f"\nTerminator occurrences (non-final position): {total_terminators}")
    print(f"  Before DA: {terminator_before_da} ({100*term_da_rate:.1f}%)")
    print(f"  Not before DA: {terminator_not_before_da} ({100*(1-term_da_rate):.1f}%)")

    print(f"\nDA occurrences (non-initial position): {total_da}")
    print(f"  Preceded by terminator: {da_preceded_by_terminator} ({100*da_term_rate:.1f}%)")
    print(f"  Not preceded by terminator: {da_not_preceded_by_terminator} ({100*(1-da_term_rate):.1f}%)")

    print(f"\nTop 10 tokens that precede DA:")
    for tok, count in da_predecessors.most_common(10):
        marker = " <-- TERMINATOR" if tok in TERMINATORS else ""
        print(f"  {tok}: {count}{marker}")

    # Baseline: what fraction of ALL tokens are terminators?
    all_tokens = [str(t).lower() for t in a_data['word']]
    terminator_baseline = sum(1 for t in all_tokens if t in TERMINATORS) / len(all_tokens)

    enrichment = da_term_rate / terminator_baseline if terminator_baseline > 0 else 0

    print(f"\nBaseline terminator rate in corpus: {100*terminator_baseline:.2f}%")
    print(f"Terminator rate before DA: {100*da_term_rate:.1f}%")
    print(f"Enrichment: {enrichment:.2f}x")

    result = {
        'test': 'terminator_da_adjacency',
        'total_terminators_nonfinal': total_terminators,
        'terminators_before_da': terminator_before_da,
        'terminator_before_da_rate': term_da_rate,
        'total_da_noninitial': total_da,
        'da_preceded_by_terminator': da_preceded_by_terminator,
        'da_preceded_rate': da_term_rate,
        'baseline_terminator_rate': terminator_baseline,
        'enrichment': enrichment,
        'top_da_predecessors': dict(da_predecessors.most_common(20))
    }

    if enrichment > 2.0:
        result['verdict'] = 'STRONG_ASSOCIATION'
        print(f"\n-> VERDICT: STRONG_ASSOCIATION (terminators enriched {enrichment:.1f}x before DA)")
    elif enrichment > 1.5:
        result['verdict'] = 'MODERATE_ASSOCIATION'
        print(f"\n-> VERDICT: MODERATE_ASSOCIATION")
    else:
        result['verdict'] = 'WEAK_OR_NO_ASSOCIATION'
        print(f"\n-> VERDICT: WEAK_OR_NO_ASSOCIATION")

    return result


def test_2_starter_da_adjacency():
    """
    Test 2: Do starters appear immediately AFTER DA tokens?

    If starters mark the beginning of sub-records, they should appear
    right after DA (which separates sub-records).
    """
    print("\n" + "=" * 70)
    print("Test 2: Starter-DA Adjacency")
    print("=" * 70)
    print("Hypothesis: Starters appear after DA tokens (start of sub-records)")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    starter_after_da = 0
    starter_not_after_da = 0
    da_followed_by_starter = 0
    da_not_followed_by_starter = 0

    # Track what follows DA
    da_successors = Counter()

    for (folio, line), group in a_data.groupby(['folio', 'line_number']):
        tokens = list(group['word'].values)
        if len(tokens) < 2:
            continue

        for i in range(len(tokens) - 1):
            curr = str(tokens[i]).lower()
            next_tok = str(tokens[i + 1]).lower()

            # Is next a starter?
            if next_tok in STARTERS:
                if is_da_family(curr):
                    starter_after_da += 1
                else:
                    starter_not_after_da += 1

            # Is current a DA token?
            if is_da_family(curr):
                da_successors[next_tok] += 1
                if next_tok in STARTERS:
                    da_followed_by_starter += 1
                else:
                    da_not_followed_by_starter += 1

    total_starters = starter_after_da + starter_not_after_da
    total_da = da_followed_by_starter + da_not_followed_by_starter

    start_da_rate = starter_after_da / total_starters if total_starters > 0 else 0
    da_start_rate = da_followed_by_starter / total_da if total_da > 0 else 0

    print(f"\nStarter occurrences (non-initial position): {total_starters}")
    print(f"  After DA: {starter_after_da} ({100*start_da_rate:.1f}%)")
    print(f"  Not after DA: {starter_not_after_da} ({100*(1-start_da_rate):.1f}%)")

    print(f"\nDA occurrences (non-final position): {total_da}")
    print(f"  Followed by starter: {da_followed_by_starter} ({100*da_start_rate:.1f}%)")
    print(f"  Not followed by starter: {da_not_followed_by_starter} ({100*(1-da_start_rate):.1f}%)")

    print(f"\nTop 10 tokens that follow DA:")
    for tok, count in da_successors.most_common(10):
        marker = " <-- STARTER" if tok in STARTERS else ""
        print(f"  {tok}: {count}{marker}")

    # Baseline
    all_tokens = [str(t).lower() for t in a_data['word']]
    starter_baseline = sum(1 for t in all_tokens if t in STARTERS) / len(all_tokens)

    enrichment = da_start_rate / starter_baseline if starter_baseline > 0 else 0

    print(f"\nBaseline starter rate in corpus: {100*starter_baseline:.2f}%")
    print(f"Starter rate after DA: {100*da_start_rate:.1f}%")
    print(f"Enrichment: {enrichment:.2f}x")

    result = {
        'test': 'starter_da_adjacency',
        'total_starters_noninitial': total_starters,
        'starters_after_da': starter_after_da,
        'starter_after_da_rate': start_da_rate,
        'total_da_nonfinal': total_da,
        'da_followed_by_starter': da_followed_by_starter,
        'da_followed_rate': da_start_rate,
        'baseline_starter_rate': starter_baseline,
        'enrichment': enrichment,
        'top_da_successors': dict(da_successors.most_common(20))
    }

    if enrichment > 2.0:
        result['verdict'] = 'STRONG_ASSOCIATION'
        print(f"\n-> VERDICT: STRONG_ASSOCIATION (starters enriched {enrichment:.1f}x after DA)")
    elif enrichment > 1.5:
        result['verdict'] = 'MODERATE_ASSOCIATION'
        print(f"\n-> VERDICT: MODERATE_ASSOCIATION")
    else:
        result['verdict'] = 'WEAK_OR_NO_ASSOCIATION'
        print(f"\n-> VERDICT: WEAK_OR_NO_ASSOCIATION")

    return result


def test_3_subrecord_position_vocabulary():
    """
    Test 3: Are starters/terminators characteristic of first/last DA-segments?

    Segment each multi-DA line into DA-delimited blocks.
    Check if starters appear in FIRST block and terminators in LAST block.
    """
    print("\n" + "=" * 70)
    print("Test 3: Sub-Record Position Vocabulary")
    print("=" * 70)
    print("Hypothesis: Starters in first block, terminators in last block")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    first_block_tokens = []
    middle_block_tokens = []
    last_block_tokens = []
    only_block_tokens = []  # Lines with no DA (single block)

    for (folio, line), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        # Find DA positions
        da_positions = [i for i, t in enumerate(tokens) if is_da_family(t)]

        if len(da_positions) == 0:
            # No DA - entire line is one block
            only_block_tokens.extend(tokens)
            continue

        # Segment by DA
        blocks = []
        start = 0
        for da_pos in da_positions:
            if da_pos > start:
                blocks.append(tokens[start:da_pos])
            start = da_pos + 1
        if start < len(tokens):
            blocks.append(tokens[start:])

        # Filter empty blocks
        blocks = [b for b in blocks if b]

        if len(blocks) == 1:
            only_block_tokens.extend(blocks[0])
        elif len(blocks) >= 2:
            first_block_tokens.extend(blocks[0])
            last_block_tokens.extend(blocks[-1])
            for block in blocks[1:-1]:
                middle_block_tokens.extend(block)

    # Count starters/terminators in each position
    def count_boundary_tokens(token_list, boundary_set):
        if not token_list:
            return 0, 0
        count = sum(1 for t in token_list if t in boundary_set)
        return count, len(token_list)

    starter_first, n_first = count_boundary_tokens(first_block_tokens, STARTERS)
    starter_middle, n_middle = count_boundary_tokens(middle_block_tokens, STARTERS)
    starter_last, n_last = count_boundary_tokens(last_block_tokens, STARTERS)
    starter_only, n_only = count_boundary_tokens(only_block_tokens, STARTERS)

    term_first, _ = count_boundary_tokens(first_block_tokens, TERMINATORS)
    term_middle, _ = count_boundary_tokens(middle_block_tokens, TERMINATORS)
    term_last, _ = count_boundary_tokens(last_block_tokens, TERMINATORS)
    term_only, _ = count_boundary_tokens(only_block_tokens, TERMINATORS)

    print(f"\nBlock statistics:")
    print(f"  First blocks: {n_first} tokens")
    print(f"  Middle blocks: {n_middle} tokens")
    print(f"  Last blocks: {n_last} tokens")
    print(f"  Only blocks (no DA): {n_only} tokens")

    print(f"\nStarter distribution:")
    print(f"  First block: {starter_first}/{n_first} = {100*starter_first/n_first:.2f}%" if n_first > 0 else "  First block: N/A")
    print(f"  Middle blocks: {starter_middle}/{n_middle} = {100*starter_middle/n_middle:.2f}%" if n_middle > 0 else "  Middle blocks: N/A")
    print(f"  Last block: {starter_last}/{n_last} = {100*starter_last/n_last:.2f}%" if n_last > 0 else "  Last block: N/A")
    print(f"  Only block: {starter_only}/{n_only} = {100*starter_only/n_only:.2f}%" if n_only > 0 else "  Only block: N/A")

    print(f"\nTerminator distribution:")
    print(f"  First block: {term_first}/{n_first} = {100*term_first/n_first:.2f}%" if n_first > 0 else "  First block: N/A")
    print(f"  Middle blocks: {term_middle}/{n_middle} = {100*term_middle/n_middle:.2f}%" if n_middle > 0 else "  Middle blocks: N/A")
    print(f"  Last block: {term_last}/{n_last} = {100*term_last/n_last:.2f}%" if n_last > 0 else "  Last block: N/A")
    print(f"  Only block: {term_only}/{n_only} = {100*term_only/n_only:.2f}%" if n_only > 0 else "  Only block: N/A")

    # Calculate enrichment ratios
    starter_rate_first = starter_first / n_first if n_first > 0 else 0
    starter_rate_last = starter_last / n_last if n_last > 0 else 0
    term_rate_first = term_first / n_first if n_first > 0 else 0
    term_rate_last = term_last / n_last if n_last > 0 else 0

    # Expected: starters enriched in FIRST, terminators enriched in LAST
    starter_first_vs_last = starter_rate_first / starter_rate_last if starter_rate_last > 0 else float('inf')
    term_last_vs_first = term_rate_last / term_rate_first if term_rate_first > 0 else float('inf')

    print(f"\nEnrichment ratios:")
    print(f"  Starters in FIRST vs LAST: {starter_first_vs_last:.2f}x")
    print(f"  Terminators in LAST vs FIRST: {term_last_vs_first:.2f}x")

    # Chi-square test for starter position preference
    if n_first > 0 and n_last > 0:
        contingency_starter = [
            [starter_first, n_first - starter_first],
            [starter_last, n_last - starter_last]
        ]
        chi2_starter, p_starter, _, _ = stats.chi2_contingency(contingency_starter)

        contingency_term = [
            [term_first, n_first - term_first],
            [term_last, n_last - term_last]
        ]
        chi2_term, p_term, _, _ = stats.chi2_contingency(contingency_term)

        print(f"\nChi-square tests:")
        print(f"  Starters (first vs last): chi2={chi2_starter:.2f}, p={p_starter:.4f}")
        print(f"  Terminators (first vs last): chi2={chi2_term:.2f}, p={p_term:.4f}")
    else:
        chi2_starter, p_starter = 0, 1
        chi2_term, p_term = 0, 1

    result = {
        'test': 'subrecord_position_vocabulary',
        'n_first_block': n_first,
        'n_middle_block': n_middle,
        'n_last_block': n_last,
        'n_only_block': n_only,
        'starter_first': starter_first,
        'starter_last': starter_last,
        'starter_first_vs_last_ratio': starter_first_vs_last,
        'term_first': term_first,
        'term_last': term_last,
        'term_last_vs_first_ratio': term_last_vs_first,
        'chi2_starter': chi2_starter,
        'p_starter': p_starter,
        'chi2_term': chi2_term,
        'p_term': p_term
    }

    # Verdict
    starter_hypothesis = starter_first_vs_last > 1.5 and p_starter < 0.05
    term_hypothesis = term_last_vs_first > 1.5 and p_term < 0.05

    if starter_hypothesis and term_hypothesis:
        result['verdict'] = 'BOTH_CONFIRMED'
        print(f"\n-> VERDICT: BOTH_CONFIRMED - Starters prefer FIRST, terminators prefer LAST")
    elif starter_hypothesis:
        result['verdict'] = 'STARTER_ONLY'
        print(f"\n-> VERDICT: STARTER_ONLY - Only starter hypothesis confirmed")
    elif term_hypothesis:
        result['verdict'] = 'TERMINATOR_ONLY'
        print(f"\n-> VERDICT: TERMINATOR_ONLY - Only terminator hypothesis confirmed")
    else:
        result['verdict'] = 'NEITHER_CONFIRMED'
        print(f"\n-> VERDICT: NEITHER_CONFIRMED - No position preference found")

    return result


def test_4_line_position_vs_da_position():
    """
    Test 4: Compare line-boundary enrichment vs DA-boundary enrichment.

    Key question: Are "boundary markers" really about LINE position,
    or are they about DA-segment position?
    """
    print("\n" + "=" * 70)
    print("Test 4: Line Position vs DA Position")
    print("=" * 70)
    print("Question: Is boundary enrichment about lines or DA-segments?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Track positions
    line_initial = Counter()
    line_final = Counter()
    line_middle = Counter()

    da_adjacent_before = Counter()  # Token immediately before DA
    da_adjacent_after = Counter()   # Token immediately after DA
    da_non_adjacent = Counter()     # Tokens not adjacent to DA

    for (folio, line), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 1:
            continue

        # Line positions
        line_initial[tokens[0]] += 1
        if len(tokens) > 1:
            line_final[tokens[-1]] += 1
        for t in tokens[1:-1]:
            line_middle[t] += 1

        # DA adjacency
        da_positions = set(i for i, t in enumerate(tokens) if is_da_family(t))

        for i, t in enumerate(tokens):
            if is_da_family(t):
                continue  # Skip DA tokens themselves

            if (i + 1) in da_positions:  # Token before DA
                da_adjacent_before[t] += 1
            elif (i - 1) in da_positions:  # Token after DA
                da_adjacent_after[t] += 1
            else:
                da_non_adjacent[t] += 1

    # Calculate enrichment for starters and terminators
    total_initial = sum(line_initial.values())
    total_final = sum(line_final.values())
    total_middle = sum(line_middle.values())
    total_before_da = sum(da_adjacent_before.values())
    total_after_da = sum(da_adjacent_after.values())
    total_non_adj = sum(da_non_adjacent.values())

    print(f"\nPosition counts:")
    print(f"  Line-initial: {total_initial}")
    print(f"  Line-final: {total_final}")
    print(f"  Line-middle: {total_middle}")
    print(f"  Before DA: {total_before_da}")
    print(f"  After DA: {total_after_da}")
    print(f"  Not DA-adjacent: {total_non_adj}")

    # Starter enrichment comparison
    starter_line_initial = sum(line_initial[t] for t in STARTERS)
    starter_before_da = sum(da_adjacent_before[t] for t in STARTERS)
    starter_after_da = sum(da_adjacent_after[t] for t in STARTERS)

    starter_line_rate = starter_line_initial / total_initial if total_initial > 0 else 0
    starter_before_rate = starter_before_da / total_before_da if total_before_da > 0 else 0
    starter_after_rate = starter_after_da / total_after_da if total_after_da > 0 else 0

    print(f"\nStarter enrichment:")
    print(f"  Line-initial: {100*starter_line_rate:.2f}%")
    print(f"  Before DA: {100*starter_before_rate:.2f}%")
    print(f"  After DA: {100*starter_after_rate:.2f}%")

    # Terminator enrichment comparison
    term_line_final = sum(line_final[t] for t in TERMINATORS)
    term_before_da = sum(da_adjacent_before[t] for t in TERMINATORS)
    term_after_da = sum(da_adjacent_after[t] for t in TERMINATORS)

    term_line_rate = term_line_final / total_final if total_final > 0 else 0
    term_before_rate = term_before_da / total_before_da if total_before_da > 0 else 0
    term_after_rate = term_after_da / total_after_da if total_after_da > 0 else 0

    print(f"\nTerminator enrichment:")
    print(f"  Line-final: {100*term_line_rate:.2f}%")
    print(f"  Before DA: {100*term_before_rate:.2f}%")
    print(f"  After DA: {100*term_after_rate:.2f}%")

    # Which is stronger?
    # If DA-based > line-based, then boundary markers are about DA structure
    starter_line_vs_da = starter_line_rate / starter_after_rate if starter_after_rate > 0 else float('inf')
    term_line_vs_da = term_line_rate / term_before_rate if term_before_rate > 0 else float('inf')

    print(f"\nLine-based vs DA-based enrichment:")
    print(f"  Starters: line-initial / after-DA = {starter_line_vs_da:.2f}x")
    print(f"  Terminators: line-final / before-DA = {term_line_vs_da:.2f}x")

    result = {
        'test': 'line_vs_da_position',
        'starter_line_initial_rate': starter_line_rate,
        'starter_before_da_rate': starter_before_rate,
        'starter_after_da_rate': starter_after_rate,
        'term_line_final_rate': term_line_rate,
        'term_before_da_rate': term_before_rate,
        'term_after_da_rate': term_after_rate,
        'starter_line_vs_da_ratio': starter_line_vs_da,
        'term_line_vs_da_ratio': term_line_vs_da
    }

    # Interpretation
    if starter_line_vs_da > 2 and term_line_vs_da > 2:
        result['verdict'] = 'LINE_BOUNDARY_PRIMARY'
        result['interpretation'] = 'Boundary enrichment is primarily about line position, not DA structure'
    elif starter_line_vs_da < 0.5 and term_line_vs_da < 0.5:
        result['verdict'] = 'DA_BOUNDARY_PRIMARY'
        result['interpretation'] = 'Boundary enrichment is primarily about DA structure, not line position'
    else:
        result['verdict'] = 'MIXED'
        result['interpretation'] = 'Both line position and DA structure contribute to boundary patterns'

    print(f"\n-> VERDICT: {result['verdict']}")
    print(f"   {result['interpretation']}")

    return result


def run_da_boundary_analysis():
    """Run all DA-boundary relationship tests."""
    print("\n" + "=" * 80)
    print("CAR DA-BOUNDARY TOKEN RELATIONSHIP ANALYSIS")
    print("=" * 80)
    print("\nHypothesis: CAR boundary markers are internal structure markers")
    print("related to DA-segmented sub-records, not line delimiters.")
    print(f"\nStarters being tested: {STARTERS}")
    print(f"Terminators being tested: {TERMINATORS}")

    results = {
        'phase': 'CAR-DA',
        'name': 'DA-Boundary Token Relationship',
        'starters': list(STARTERS),
        'terminators': list(TERMINATORS),
        'tests': {}
    }

    results['tests']['test_1'] = test_1_terminator_da_adjacency()
    results['tests']['test_2'] = test_2_starter_da_adjacency()
    results['tests']['test_3'] = test_3_subrecord_position_vocabulary()
    results['tests']['test_4'] = test_4_line_position_vs_da_position()

    # Summary
    print("\n" + "=" * 80)
    print("DA-BOUNDARY ANALYSIS SUMMARY")
    print("=" * 80)

    print("\nTest Results:")
    for test_id, test in results['tests'].items():
        print(f"  {test_id}: {test['verdict']}")

    # Overall interpretation
    verdicts = [t['verdict'] for t in results['tests'].values()]

    da_evidence = sum(1 for v in verdicts if 'DA' in v or 'ASSOCIATION' in v)
    line_evidence = sum(1 for v in verdicts if 'LINE' in v)

    if results['tests']['test_4']['verdict'] == 'LINE_BOUNDARY_PRIMARY':
        overall = 'LINE_MARKERS'
        summary = 'Boundary tokens mark LINE positions, not DA structure'
    elif results['tests']['test_4']['verdict'] == 'DA_BOUNDARY_PRIMARY':
        overall = 'DA_MARKERS'
        summary = 'Boundary tokens mark DA-segment positions, LINE = RECORD confirmed'
    else:
        overall = 'DUAL_FUNCTION'
        summary = 'Boundary tokens serve both line and DA-segment marking functions'

    results['overall_verdict'] = overall
    results['summary'] = summary

    print(f"\n-> OVERALL VERDICT: {overall}")
    print(f"   {summary}")

    # Implications for LINE = RECORD
    print("\n" + "-" * 40)
    print("IMPLICATIONS FOR LINE = RECORD:")
    print("-" * 40)
    if overall == 'LINE_MARKERS':
        print("The boundary tokens DO mark line boundaries.")
        print("This could mean:")
        print("  1. Lines need explicit marking (LINE != RECORD?)")
        print("  2. Or: stylistic convention with no structural function")
    elif overall == 'DA_MARKERS':
        print("The boundary tokens mark DA-segment structure, not lines.")
        print("LINE = RECORD remains valid.")
        print("Boundary tokens = internal structure of compound entries.")
    else:
        print("Boundary tokens serve multiple functions.")
        print("Further investigation needed.")

    # Save results
    output_file = PHASE_DIR / 'car_da_boundary_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_da_boundary_analysis()
