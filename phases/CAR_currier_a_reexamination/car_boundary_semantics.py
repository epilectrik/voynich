#!/usr/bin/env python
"""
CAR Phase: Boundary Marker Semantic Analysis

We know boundary markers don't delimit multi-line records.
But do they have MEANING? Do they connect records?

Questions:
1. Do records with the same terminator share vocabulary?
2. Do records with the same starter share vocabulary?
3. Are boundary markers prefix-specific?
4. Do boundary markers cluster (runs of same marker)?
5. Do specific terminators predict specific starters on next line?
6. Are there "families" of boundary markers?
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from itertools import combinations

from car_data_loader import CARDataLoader, PHASE_DIR

# Expanded boundary token sets (include variants)
STARTERS = {'tol', 'dchor', 'sor', 'qotol'}
TERMINATORS = {'dan', 'dam', 'sal', 'd', 'dy'}

# All boundary tokens
ALL_BOUNDARY = STARTERS | TERMINATORS


def test_1_shared_terminator_vocabulary():
    """
    Test 1: Do records ending with the same terminator share vocabulary?

    If terminators have semantic meaning, lines with the same terminator
    should have higher vocabulary overlap than lines with different terminators.
    """
    print("\n" + "=" * 70)
    print("Test 1: Shared Terminator -> Shared Vocabulary?")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Group lines by terminator
    lines_by_terminator = defaultdict(list)
    lines_without_terminator = []

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if not tokens:
            continue

        last_token = tokens[-1]
        middle_tokens = set(tokens[:-1]) if len(tokens) > 1 else set()

        if last_token in TERMINATORS:
            lines_by_terminator[last_token].append({
                'folio': folio,
                'line': line_num,
                'tokens': middle_tokens,
                'all_tokens': set(tokens)
            })
        else:
            lines_without_terminator.append({
                'folio': folio,
                'line': line_num,
                'tokens': middle_tokens,
                'all_tokens': set(tokens)
            })

    print(f"\nLines by terminator:")
    for term, lines in sorted(lines_by_terminator.items(), key=lambda x: -len(x[1])):
        print(f"  '{term}': {len(lines)} lines")
    print(f"  (no terminator): {len(lines_without_terminator)} lines")

    def mean_pairwise_jaccard(lines, max_pairs=500):
        """Calculate mean Jaccard for random sample of pairs."""
        if len(lines) < 2:
            return 0, 0

        pairs = list(combinations(range(len(lines)), 2))
        if len(pairs) > max_pairs:
            pairs = [pairs[i] for i in np.random.choice(len(pairs), max_pairs, replace=False)]

        jaccards = []
        for i, j in pairs:
            set1 = lines[i]['tokens']
            set2 = lines[j]['tokens']
            if set1 and set2:
                j_val = len(set1 & set2) / len(set1 | set2)
                jaccards.append(j_val)

        return np.mean(jaccards) if jaccards else 0, len(jaccards)

    # Within-terminator overlap
    print(f"\nWithin-terminator vocabulary overlap:")
    within_overlaps = []
    for term, lines in lines_by_terminator.items():
        if len(lines) >= 10:
            mean_j, n_pairs = mean_pairwise_jaccard(lines)
            within_overlaps.append(mean_j)
            print(f"  '{term}': {mean_j:.4f} (n_pairs={n_pairs})")

    mean_within = np.mean(within_overlaps) if within_overlaps else 0

    # Cross-terminator overlap (random pairs from different terminators)
    cross_pairs = []
    all_term_lines = [(term, line) for term, lines in lines_by_terminator.items() for line in lines]

    for _ in range(1000):
        i, j = np.random.choice(len(all_term_lines), 2, replace=False)
        term1, line1 = all_term_lines[i]
        term2, line2 = all_term_lines[j]
        if term1 != term2 and line1['tokens'] and line2['tokens']:
            j_val = len(line1['tokens'] & line2['tokens']) / len(line1['tokens'] | line2['tokens'])
            cross_pairs.append(j_val)

    mean_cross = np.mean(cross_pairs) if cross_pairs else 0

    print(f"\nCross-terminator overlap: {mean_cross:.4f}")
    print(f"Mean within-terminator: {mean_within:.4f}")

    ratio = mean_within / mean_cross if mean_cross > 0 else 0
    print(f"Ratio (within/cross): {ratio:.2f}x")

    # Statistical test
    if within_overlaps and cross_pairs:
        # Compare within-group to cross-group
        stat, p_value = stats.mannwhitneyu(within_overlaps, cross_pairs[:len(within_overlaps)], alternative='greater')
        print(f"\nMann-Whitney (within > cross): p = {p_value:.4f}")
    else:
        p_value = 1.0

    result = {
        'test': 'shared_terminator_vocabulary',
        'lines_by_terminator': {k: len(v) for k, v in lines_by_terminator.items()},
        'mean_within_overlap': mean_within,
        'mean_cross_overlap': mean_cross,
        'ratio': ratio,
        'p_value': p_value
    }

    if ratio > 1.2 and p_value < 0.05:
        result['verdict'] = 'TERMINATOR_SEMANTIC'
        print(f"\n-> VERDICT: TERMINATOR_SEMANTIC - Same terminator = related content")
    else:
        result['verdict'] = 'NO_SEMANTIC_LINK'
        print(f"\n-> VERDICT: NO_SEMANTIC_LINK - Terminators don't predict vocabulary")

    return result


def test_2_shared_starter_vocabulary():
    """
    Test 2: Do records starting with the same starter share vocabulary?
    """
    print("\n" + "=" * 70)
    print("Test 2: Shared Starter -> Shared Vocabulary?")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Group lines by starter
    lines_by_starter = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if not tokens:
            continue

        first_token = tokens[0]
        rest_tokens = set(tokens[1:]) if len(tokens) > 1 else set()

        if first_token in STARTERS:
            lines_by_starter[first_token].append({
                'folio': folio,
                'line': line_num,
                'tokens': rest_tokens,
                'all_tokens': set(tokens)
            })

    print(f"\nLines by starter:")
    for start, lines in sorted(lines_by_starter.items(), key=lambda x: -len(x[1])):
        print(f"  '{start}': {len(lines)} lines")

    def mean_pairwise_jaccard(lines, max_pairs=500):
        if len(lines) < 2:
            return 0, 0

        pairs = list(combinations(range(len(lines)), 2))
        if len(pairs) > max_pairs:
            pairs = [pairs[i] for i in np.random.choice(len(pairs), max_pairs, replace=False)]

        jaccards = []
        for i, j in pairs:
            set1 = lines[i]['tokens']
            set2 = lines[j]['tokens']
            if set1 and set2:
                j_val = len(set1 & set2) / len(set1 | set2)
                jaccards.append(j_val)

        return np.mean(jaccards) if jaccards else 0, len(jaccards)

    # Within-starter overlap
    print(f"\nWithin-starter vocabulary overlap:")
    within_overlaps = []
    for start, lines in lines_by_starter.items():
        if len(lines) >= 5:
            mean_j, n_pairs = mean_pairwise_jaccard(lines)
            within_overlaps.append(mean_j)
            print(f"  '{start}': {mean_j:.4f} (n_pairs={n_pairs})")

    mean_within = np.mean(within_overlaps) if within_overlaps else 0

    # Cross-starter overlap
    all_start_lines = [(start, line) for start, lines in lines_by_starter.items() for line in lines]
    cross_pairs = []

    if len(all_start_lines) >= 2:
        for _ in range(min(1000, len(all_start_lines) * 10)):
            i, j = np.random.choice(len(all_start_lines), 2, replace=False)
            start1, line1 = all_start_lines[i]
            start2, line2 = all_start_lines[j]
            if start1 != start2 and line1['tokens'] and line2['tokens']:
                j_val = len(line1['tokens'] & line2['tokens']) / len(line1['tokens'] | line2['tokens'])
                cross_pairs.append(j_val)

    mean_cross = np.mean(cross_pairs) if cross_pairs else 0

    print(f"\nCross-starter overlap: {mean_cross:.4f}")
    print(f"Mean within-starter: {mean_within:.4f}")

    ratio = mean_within / mean_cross if mean_cross > 0 else 0
    print(f"Ratio (within/cross): {ratio:.2f}x")

    result = {
        'test': 'shared_starter_vocabulary',
        'lines_by_starter': {k: len(v) for k, v in lines_by_starter.items()},
        'mean_within_overlap': mean_within,
        'mean_cross_overlap': mean_cross,
        'ratio': ratio
    }

    if ratio > 1.2:
        result['verdict'] = 'STARTER_SEMANTIC'
        print(f"\n-> VERDICT: STARTER_SEMANTIC - Same starter = related content")
    else:
        result['verdict'] = 'NO_SEMANTIC_LINK'
        print(f"\n-> VERDICT: NO_SEMANTIC_LINK - Starters don't predict vocabulary")

    return result


def test_3_boundary_prefix_association():
    """
    Test 3: Are boundary markers associated with specific PREFIX families?

    Maybe 'dan' is characteristic of ch-entries and 'dam' of sh-entries.
    """
    print("\n" + "=" * 70)
    print("Test 3: Boundary Marker <-> PREFIX Association")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Known prefixes
    PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

    # Count boundary markers by dominant prefix
    terminator_by_prefix = defaultdict(Counter)
    starter_by_prefix = defaultdict(Counter)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        # Determine dominant prefix
        prefix_counts = Counter()
        for tok in tokens:
            for pfx in PREFIXES:
                if tok.startswith(pfx):
                    prefix_counts[pfx] += 1
                    break

        if not prefix_counts:
            continue

        dominant_prefix = prefix_counts.most_common(1)[0][0]

        # Check boundary markers
        first_token = tokens[0]
        last_token = tokens[-1]

        if last_token in TERMINATORS:
            terminator_by_prefix[dominant_prefix][last_token] += 1

        if first_token in STARTERS:
            starter_by_prefix[dominant_prefix][first_token] += 1

    print(f"\nTerminators by dominant prefix:")
    for pfx in PREFIXES:
        if terminator_by_prefix[pfx]:
            total = sum(terminator_by_prefix[pfx].values())
            dist = ", ".join(f"{t}:{c}" for t, c in terminator_by_prefix[pfx].most_common(3))
            print(f"  {pfx}: {dist} (total={total})")

    print(f"\nStarters by dominant prefix:")
    for pfx in PREFIXES:
        if starter_by_prefix[pfx]:
            total = sum(starter_by_prefix[pfx].values())
            dist = ", ".join(f"{t}:{c}" for t, c in starter_by_prefix[pfx].most_common(3))
            print(f"  {pfx}: {dist} (total={total})")

    # Chi-square test for terminator-prefix independence
    # Build contingency table
    term_list = list(TERMINATORS)
    prefix_list = [p for p in PREFIXES if sum(terminator_by_prefix[p].values()) > 5]

    if len(prefix_list) >= 2 and len(term_list) >= 2:
        contingency = []
        for pfx in prefix_list:
            row = [terminator_by_prefix[pfx].get(t, 0) for t in term_list]
            contingency.append(row)

        contingency = np.array(contingency)
        # Remove columns with all zeros
        col_sums = contingency.sum(axis=0)
        valid_cols = col_sums > 0
        contingency = contingency[:, valid_cols]

        if contingency.shape[1] >= 2:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
            print(f"\nChi-square (terminator x prefix): chi2={chi2:.2f}, p={p_value:.4f}")
        else:
            chi2, p_value = 0, 1
    else:
        chi2, p_value = 0, 1

    result = {
        'test': 'boundary_prefix_association',
        'terminator_by_prefix': {k: dict(v) for k, v in terminator_by_prefix.items()},
        'starter_by_prefix': {k: dict(v) for k, v in starter_by_prefix.items()},
        'chi2': chi2,
        'p_value': p_value
    }

    if p_value < 0.05:
        result['verdict'] = 'PREFIX_ASSOCIATED'
        print(f"\n-> VERDICT: PREFIX_ASSOCIATED - Boundary markers vary by prefix family")
    else:
        result['verdict'] = 'PREFIX_INDEPENDENT'
        print(f"\n-> VERDICT: PREFIX_INDEPENDENT - Boundary markers don't depend on prefix")

    return result


def test_4_boundary_marker_runs():
    """
    Test 4: Do boundary markers cluster in runs?

    If 'dan' appears on line 5, is it more likely on lines 4 and 6?
    """
    print("\n" + "=" * 70)
    print("Test 4: Boundary Marker Clustering (Runs)")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build line sequences by folio
    folio_terminators = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if not tokens:
            continue

        last_token = tokens[-1]
        terminator = last_token if last_token in TERMINATORS else None

        folio_terminators[folio].append({
            'line': line_num,
            'terminator': terminator
        })

    for folio in folio_terminators:
        folio_terminators[folio].sort(key=lambda x: x['line'])

    # Count runs
    run_lengths = []
    current_run = 0
    current_term = None

    for folio, lines in folio_terminators.items():
        for line_info in lines:
            term = line_info['terminator']
            if term is not None:
                if term == current_term:
                    current_run += 1
                else:
                    if current_run > 0:
                        run_lengths.append(current_run)
                    current_run = 1
                    current_term = term
            else:
                if current_run > 0:
                    run_lengths.append(current_run)
                current_run = 0
                current_term = None

        # End of folio
        if current_run > 0:
            run_lengths.append(current_run)
        current_run = 0
        current_term = None

    if run_lengths:
        mean_run = np.mean(run_lengths)
        max_run = max(run_lengths)
        runs_gt_1 = sum(1 for r in run_lengths if r > 1)

        print(f"\nTerminator run statistics:")
        print(f"  Total runs: {len(run_lengths)}")
        print(f"  Mean run length: {mean_run:.2f}")
        print(f"  Max run length: {max_run}")
        print(f"  Runs > 1: {runs_gt_1} ({100*runs_gt_1/len(run_lengths):.1f}%)")

        # Compare to random baseline
        # Under random, expected run length for rare events is ~1
        # Calculate expected mean run length
        all_lines = sum(len(lines) for lines in folio_terminators.values())
        total_terms = sum(1 for folio, lines in folio_terminators.items()
                        for line in lines if line['terminator'] is not None)
        term_rate = total_terms / all_lines if all_lines > 0 else 0

        # Expected run length under independence: 1 / (1 - p) where p is continuation prob
        # For rare events, this is approximately 1
        expected_run = 1.0

        print(f"\nTerminator rate: {100*term_rate:.1f}%")
        print(f"Expected run length (random): ~{expected_run:.2f}")
        print(f"Observed/Expected ratio: {mean_run/expected_run:.2f}x")
    else:
        mean_run = 0
        runs_gt_1 = 0

    # Check adjacent line terminator matching
    same_term_adjacent = 0
    diff_term_adjacent = 0

    for folio, lines in folio_terminators.items():
        for i in range(len(lines) - 1):
            term1 = lines[i]['terminator']
            term2 = lines[i + 1]['terminator']

            if term1 is not None and term2 is not None:
                if term1 == term2:
                    same_term_adjacent += 1
                else:
                    diff_term_adjacent += 1

    total_adj = same_term_adjacent + diff_term_adjacent
    same_rate = same_term_adjacent / total_adj if total_adj > 0 else 0

    print(f"\nAdjacent terminator analysis:")
    print(f"  Same terminator: {same_term_adjacent} ({100*same_rate:.1f}%)")
    print(f"  Different terminator: {diff_term_adjacent}")

    # Expected under random: 1/n_terminators
    n_terms = len(TERMINATORS)
    expected_same = 1 / n_terms

    print(f"  Expected (random): {100*expected_same:.1f}%")
    print(f"  Ratio: {same_rate/expected_same:.2f}x")

    result = {
        'test': 'boundary_marker_runs',
        'mean_run_length': mean_run,
        'runs_gt_1_pct': runs_gt_1 / len(run_lengths) if run_lengths else 0,
        'same_term_adjacent': same_term_adjacent,
        'diff_term_adjacent': diff_term_adjacent,
        'same_rate': same_rate,
        'expected_same_rate': expected_same,
        'clustering_ratio': same_rate / expected_same if expected_same > 0 else 0
    }

    if result['clustering_ratio'] > 1.5:
        result['verdict'] = 'CLUSTERED'
        print(f"\n-> VERDICT: CLUSTERED - Same terminators cluster together")
    else:
        result['verdict'] = 'NOT_CLUSTERED'
        print(f"\n-> VERDICT: NOT_CLUSTERED - Terminators appear independently")

    return result


def test_5_terminator_starter_chains():
    """
    Test 5: Do specific terminators predict specific starters on the next line?

    If records are "linked", line ending with 'dan' might be followed by
    line starting with 'tol'.
    """
    print("\n" + "=" * 70)
    print("Test 5: Terminator -> Starter Chains")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Build line sequences
    folio_lines = defaultdict(list)

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if not tokens:
            continue

        folio_lines[folio].append({
            'line': line_num,
            'first': tokens[0],
            'last': tokens[-1]
        })

    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: x['line'])

    # Count terminator -> starter transitions
    transitions = Counter()
    terminator_totals = Counter()

    for folio, lines in folio_lines.items():
        for i in range(len(lines) - 1):
            term = lines[i]['last']
            start = lines[i + 1]['first']

            if term in TERMINATORS:
                terminator_totals[term] += 1
                if start in STARTERS:
                    transitions[(term, start)] += 1

    print(f"\nTerminator -> Starter transitions:")
    for (term, start), count in transitions.most_common(20):
        total = terminator_totals[term]
        rate = count / total if total > 0 else 0
        print(f"  {term} -> {start}: {count}/{total} ({100*rate:.1f}%)")

    # Is there any pattern?
    if transitions:
        # Calculate expected under independence
        total_trans = sum(transitions.values())
        term_dist = {t: terminator_totals[t] / sum(terminator_totals.values())
                    for t in terminator_totals}

        # Chi-square for independence
        observed = []
        expected = []

        for term in TERMINATORS:
            for start in STARTERS:
                obs = transitions.get((term, start), 0)
                # Expected = P(term) * P(start | any term) * total
                start_count = sum(transitions.get((t, start), 0) for t in TERMINATORS)
                exp = terminator_totals[term] * (start_count / sum(terminator_totals.values())) if terminator_totals else 0
                if exp > 0:
                    observed.append(obs)
                    expected.append(exp)

        if observed and expected:
            chi2 = sum((o - e)**2 / e for o, e in zip(observed, expected) if e > 0)
            dof = len(observed) - 1
            p_value = 1 - stats.chi2.cdf(chi2, dof) if dof > 0 else 1
            print(f"\nChi-square (term x start independence): chi2={chi2:.2f}, p={p_value:.4f}")
        else:
            chi2, p_value = 0, 1
    else:
        chi2, p_value = 0, 1
        print("\nNo terminator->starter transitions found")

    result = {
        'test': 'terminator_starter_chains',
        'transitions': {f"{k[0]}->{k[1]}": v for k, v in transitions.items()},
        'terminator_totals': dict(terminator_totals),
        'chi2': chi2,
        'p_value': p_value
    }

    if p_value < 0.05:
        result['verdict'] = 'CHAINS_EXIST'
        print(f"\n-> VERDICT: CHAINS_EXIST - Specific terminators predict specific starters")
    else:
        result['verdict'] = 'NO_CHAINS'
        print(f"\n-> VERDICT: NO_CHAINS - Terminators don't predict following starters")

    return result


def test_6_boundary_vocabulary_analysis():
    """
    Test 6: What ARE these boundary tokens? Analyze their properties.
    """
    print("\n" + "=" * 70)
    print("Test 6: Boundary Token Properties")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Analyze each boundary token
    all_tokens = [str(t).lower() for t in a_data['word']]
    token_counts = Counter(all_tokens)

    print(f"\nBoundary token frequencies:")
    print(f"\nTerminators:")
    for term in sorted(TERMINATORS):
        count = token_counts.get(term, 0)
        pct = 100 * count / len(all_tokens)
        print(f"  '{term}': {count} ({pct:.2f}%)")

    print(f"\nStarters:")
    for start in sorted(STARTERS):
        count = token_counts.get(start, 0)
        pct = 100 * count / len(all_tokens)
        print(f"  '{start}': {count} ({pct:.2f}%)")

    # Check prefix patterns
    print(f"\nBoundary token prefix analysis:")
    PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'd', 's', 't', 'q']

    for tok in sorted(ALL_BOUNDARY):
        for pfx in PREFIXES:
            if tok.startswith(pfx):
                print(f"  '{tok}' -> prefix '{pfx}'")
                break
        else:
            print(f"  '{tok}' -> no standard prefix")

    # Check if boundary tokens appear in non-boundary positions
    print(f"\nBoundary token position distribution:")

    boundary_positions = {tok: {'first': 0, 'last': 0, 'middle': 0} for tok in ALL_BOUNDARY}

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 1:
            continue

        for i, tok in enumerate(tokens):
            if tok in ALL_BOUNDARY:
                if i == 0:
                    boundary_positions[tok]['first'] += 1
                elif i == len(tokens) - 1:
                    boundary_positions[tok]['last'] += 1
                else:
                    boundary_positions[tok]['middle'] += 1

    for tok in sorted(ALL_BOUNDARY):
        pos = boundary_positions[tok]
        total = pos['first'] + pos['middle'] + pos['last']
        if total > 0:
            print(f"  '{tok}': first={pos['first']} ({100*pos['first']/total:.0f}%), "
                  f"middle={pos['middle']} ({100*pos['middle']/total:.0f}%), "
                  f"last={pos['last']} ({100*pos['last']/total:.0f}%)")

    result = {
        'test': 'boundary_vocabulary_analysis',
        'token_counts': {t: token_counts.get(t, 0) for t in ALL_BOUNDARY},
        'position_distribution': boundary_positions
    }

    # Check if any boundary tokens are strongly position-specific
    strong_positional = []
    for tok, pos in boundary_positions.items():
        total = pos['first'] + pos['middle'] + pos['last']
        if total >= 10:
            max_pos = max(pos.values())
            if max_pos / total > 0.7:
                strong_positional.append(tok)

    if strong_positional:
        result['verdict'] = 'POSITION_SPECIFIC'
        result['strong_positional'] = strong_positional
        print(f"\n-> VERDICT: POSITION_SPECIFIC - These tokens strongly prefer certain positions: {strong_positional}")
    else:
        result['verdict'] = 'POSITION_FLEXIBLE'
        print(f"\n-> VERDICT: POSITION_FLEXIBLE - Boundary tokens appear throughout lines")

    return result


def run_boundary_semantics():
    """Run all boundary marker semantic tests."""
    print("\n" + "=" * 80)
    print("CAR BOUNDARY MARKER SEMANTIC ANALYSIS")
    print("=" * 80)
    print("\nQuestion: Do boundary markers have meaning? Do they connect records?")

    results = {
        'phase': 'CAR-BS',
        'name': 'Boundary Marker Semantic Analysis',
        'tests': {}
    }

    results['tests']['test_1'] = test_1_shared_terminator_vocabulary()
    results['tests']['test_2'] = test_2_shared_starter_vocabulary()
    results['tests']['test_3'] = test_3_boundary_prefix_association()
    results['tests']['test_4'] = test_4_boundary_marker_runs()
    results['tests']['test_5'] = test_5_terminator_starter_chains()
    results['tests']['test_6'] = test_6_boundary_vocabulary_analysis()

    # Summary
    print("\n" + "=" * 80)
    print("BOUNDARY SEMANTICS SUMMARY")
    print("=" * 80)

    print("\nTest Results:")
    for test_id, test in results['tests'].items():
        print(f"  {test_id}: {test['verdict']}")

    # Count semantic vs non-semantic
    semantic_evidence = sum(1 for t in results['tests'].values()
                          if 'SEMANTIC' in t['verdict'] or 'ASSOCIATED' in t['verdict']
                          or 'CLUSTERED' in t['verdict'] or 'CHAINS' in t['verdict'])

    if semantic_evidence >= 3:
        overall = 'MARKERS_HAVE_MEANING'
        summary = 'Boundary markers carry semantic information'
    elif semantic_evidence >= 1:
        overall = 'PARTIAL_MEANING'
        summary = 'Some evidence for boundary marker semantics'
    else:
        overall = 'PURELY_STYLISTIC'
        summary = 'Boundary markers appear to be purely stylistic'

    results['overall_verdict'] = overall
    results['summary'] = summary
    results['semantic_evidence_count'] = semantic_evidence

    print(f"\n-> OVERALL VERDICT: {overall}")
    print(f"   {summary}")

    # Save results
    output_file = PHASE_DIR / 'car_boundary_semantics_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_boundary_semantics()
