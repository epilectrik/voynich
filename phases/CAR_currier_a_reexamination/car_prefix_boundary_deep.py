#!/usr/bin/env python
"""
CAR Phase: Deep PREFIX-Boundary Relationship Analysis

We found boundary markers vary by PREFIX family (p=0.003).
This script digs deeper into that relationship.

Questions:
1. What's the full PREFIX x first-token and PREFIX x last-token distribution?
2. Are boundary tokens morphologically related to prefixes?
3. Is there an entry "grammar" (start pattern -> middle -> end pattern)?
4. Do prefixes have characteristic entry structures?
5. What predicts the first/last token of an entry?
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

from car_data_loader import CARDataLoader, decompose_token, PHASE_DIR

# Known prefixes
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']


def analyze_token_morphology(token):
    """
    Decompose a token into morphological components.
    Returns dict with prefix, has_prefix, length, etc.
    """
    token = str(token).lower()

    result = {
        'token': token,
        'length': len(token),
        'prefix': None,
        'has_standard_prefix': False,
        'starts_with_d': token.startswith('d'),
        'starts_with_s': token.startswith('s'),
        'starts_with_t': token.startswith('t'),
        'starts_with_q': token.startswith('q'),
        'starts_with_o': token.startswith('o'),
        'starts_with_c': token.startswith('c'),
        'ends_with_y': token.endswith('y'),
        'ends_with_n': token.endswith('n'),
        'ends_with_m': token.endswith('m'),
        'ends_with_l': token.endswith('l'),
        'ends_with_r': token.endswith('r'),
    }

    for pfx in PREFIXES:
        if token.startswith(pfx):
            result['prefix'] = pfx
            result['has_standard_prefix'] = True
            break

    return result


def test_1_full_position_by_prefix():
    """
    Test 1: Complete first-token and last-token distribution by dominant PREFIX.
    """
    print("\n" + "=" * 70)
    print("Test 1: Full Position Distribution by PREFIX")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # Collect first/last tokens by dominant prefix
    first_by_prefix = defaultdict(Counter)
    last_by_prefix = defaultdict(Counter)
    entry_data = []

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
            dominant = 'none'
        else:
            dominant = prefix_counts.most_common(1)[0][0]

        first_tok = tokens[0]
        last_tok = tokens[-1]

        first_by_prefix[dominant][first_tok] += 1
        last_by_prefix[dominant][last_tok] += 1

        entry_data.append({
            'folio': folio,
            'line': line_num,
            'dominant_prefix': dominant,
            'first_token': first_tok,
            'last_token': last_tok,
            'n_tokens': len(tokens),
            'tokens': tokens
        })

    df = pd.DataFrame(entry_data)

    # Analyze first tokens by prefix
    print("\n" + "-" * 50)
    print("FIRST TOKEN by dominant PREFIX")
    print("-" * 50)

    for pfx in PREFIXES + ['none']:
        if pfx not in first_by_prefix:
            continue
        counter = first_by_prefix[pfx]
        total = sum(counter.values())
        if total < 10:
            continue

        print(f"\n{pfx.upper()}-dominant entries (n={total}):")
        print(f"  Top first tokens:")
        for tok, count in counter.most_common(10):
            pct = 100 * count / total
            morph = analyze_token_morphology(tok)
            pfx_info = f"[{morph['prefix']}]" if morph['prefix'] else "[no-pfx]"
            print(f"    {tok}: {count} ({pct:.1f}%) {pfx_info}")

    # Analyze last tokens by prefix
    print("\n" + "-" * 50)
    print("LAST TOKEN by dominant PREFIX")
    print("-" * 50)

    for pfx in PREFIXES + ['none']:
        if pfx not in last_by_prefix:
            continue
        counter = last_by_prefix[pfx]
        total = sum(counter.values())
        if total < 10:
            continue

        print(f"\n{pfx.upper()}-dominant entries (n={total}):")
        print(f"  Top last tokens:")
        for tok, count in counter.most_common(10):
            pct = 100 * count / total
            morph = analyze_token_morphology(tok)
            pfx_info = f"[{morph['prefix']}]" if morph['prefix'] else "[no-pfx]"
            print(f"    {tok}: {count} ({pct:.1f}%) {pfx_info}")

    return {
        'test': 'full_position_by_prefix',
        'n_entries': len(df),
        'first_by_prefix': {k: dict(v.most_common(20)) for k, v in first_by_prefix.items()},
        'last_by_prefix': {k: dict(v.most_common(20)) for k, v in last_by_prefix.items()}
    }


def test_2_first_token_prefix_match():
    """
    Test 2: Does the first token's prefix match the entry's dominant prefix?
    """
    print("\n" + "=" * 70)
    print("Test 2: First Token PREFIX Match")
    print("=" * 70)
    print("Question: Does the first token belong to the same PREFIX family as the entry?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    matches = 0
    mismatches = 0
    no_first_prefix = 0

    match_details = defaultdict(lambda: defaultdict(int))

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        # Dominant prefix
        prefix_counts = Counter()
        for tok in tokens:
            for pfx in PREFIXES:
                if tok.startswith(pfx):
                    prefix_counts[pfx] += 1
                    break

        if not prefix_counts:
            continue

        dominant = prefix_counts.most_common(1)[0][0]

        # First token prefix
        first_tok = tokens[0]
        first_prefix = None
        for pfx in PREFIXES:
            if first_tok.startswith(pfx):
                first_prefix = pfx
                break

        if first_prefix is None:
            no_first_prefix += 1
            match_details[dominant]['no_prefix'] += 1
        elif first_prefix == dominant:
            matches += 1
            match_details[dominant]['match'] += 1
        else:
            mismatches += 1
            match_details[dominant][f'mismatch_{first_prefix}'] += 1

    total = matches + mismatches + no_first_prefix
    print(f"\nFirst token PREFIX analysis:")
    print(f"  Matches dominant: {matches} ({100*matches/total:.1f}%)")
    print(f"  Mismatches: {mismatches} ({100*mismatches/total:.1f}%)")
    print(f"  No standard prefix: {no_first_prefix} ({100*no_first_prefix/total:.1f}%)")

    print(f"\nBy dominant PREFIX:")
    for pfx in PREFIXES:
        if pfx in match_details:
            details = match_details[pfx]
            total_pfx = sum(details.values())
            match_rate = details.get('match', 0) / total_pfx if total_pfx > 0 else 0
            no_pfx_rate = details.get('no_prefix', 0) / total_pfx if total_pfx > 0 else 0
            print(f"  {pfx}: match={100*match_rate:.1f}%, no-prefix={100*no_pfx_rate:.1f}% (n={total_pfx})")

    return {
        'test': 'first_token_prefix_match',
        'matches': matches,
        'mismatches': mismatches,
        'no_first_prefix': no_first_prefix,
        'match_rate': matches / total if total > 0 else 0,
        'details': {k: dict(v) for k, v in match_details.items()}
    }


def test_3_last_token_prefix_match():
    """
    Test 3: Does the last token's prefix match the entry's dominant prefix?
    """
    print("\n" + "=" * 70)
    print("Test 3: Last Token PREFIX Match")
    print("=" * 70)
    print("Question: Does the last token belong to the same PREFIX family as the entry?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    matches = 0
    mismatches = 0
    no_last_prefix = 0

    match_details = defaultdict(lambda: defaultdict(int))

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        # Dominant prefix
        prefix_counts = Counter()
        for tok in tokens:
            for pfx in PREFIXES:
                if tok.startswith(pfx):
                    prefix_counts[pfx] += 1
                    break

        if not prefix_counts:
            continue

        dominant = prefix_counts.most_common(1)[0][0]

        # Last token prefix
        last_tok = tokens[-1]
        last_prefix = None
        for pfx in PREFIXES:
            if last_tok.startswith(pfx):
                last_prefix = pfx
                break

        if last_prefix is None:
            no_last_prefix += 1
            match_details[dominant]['no_prefix'] += 1
        elif last_prefix == dominant:
            matches += 1
            match_details[dominant]['match'] += 1
        else:
            mismatches += 1
            match_details[dominant][f'mismatch_{last_prefix}'] += 1

    total = matches + mismatches + no_last_prefix
    print(f"\nLast token PREFIX analysis:")
    print(f"  Matches dominant: {matches} ({100*matches/total:.1f}%)")
    print(f"  Mismatches: {mismatches} ({100*mismatches/total:.1f}%)")
    print(f"  No standard prefix: {no_last_prefix} ({100*no_last_prefix/total:.1f}%)")

    print(f"\nBy dominant PREFIX:")
    for pfx in PREFIXES:
        if pfx in match_details:
            details = match_details[pfx]
            total_pfx = sum(details.values())
            match_rate = details.get('match', 0) / total_pfx if total_pfx > 0 else 0
            no_pfx_rate = details.get('no_prefix', 0) / total_pfx if total_pfx > 0 else 0
            print(f"  {pfx}: match={100*match_rate:.1f}%, no-prefix={100*no_pfx_rate:.1f}% (n={total_pfx})")

    # Compare to first token
    print(f"\nComparison: First token match rate was higher/lower than last token?")

    return {
        'test': 'last_token_prefix_match',
        'matches': matches,
        'mismatches': mismatches,
        'no_last_prefix': no_last_prefix,
        'match_rate': matches / total if total > 0 else 0,
        'details': {k: dict(v) for k, v in match_details.items()}
    }


def test_4_entry_structure_patterns():
    """
    Test 4: What's the typical structure of an entry?
    PREFIX composition from start to end.
    """
    print("\n" + "=" * 70)
    print("Test 4: Entry Structure Patterns")
    print("=" * 70)
    print("Question: How does PREFIX composition change from start to end of entry?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # For entries of different lengths, track prefix at each position
    position_prefix = defaultdict(lambda: defaultdict(Counter))

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        n = len(tokens)
        if n < 3:
            continue

        for i, tok in enumerate(tokens):
            # Normalized position (0=start, 1=end)
            if n <= 5:
                length_cat = 'short'
            elif n <= 10:
                length_cat = 'medium'
            else:
                length_cat = 'long'

            # Position category
            if i == 0:
                pos = 'first'
            elif i == n - 1:
                pos = 'last'
            elif i < n / 3:
                pos = 'early'
            elif i < 2 * n / 3:
                pos = 'middle'
            else:
                pos = 'late'

            # Token prefix
            tok_prefix = 'none'
            for pfx in PREFIXES:
                if tok.startswith(pfx):
                    tok_prefix = pfx
                    break

            position_prefix[length_cat][pos][tok_prefix] += 1

    print("\nPREFIX distribution by position in entry:")

    for length_cat in ['short', 'medium', 'long']:
        if length_cat not in position_prefix:
            continue
        print(f"\n{length_cat.upper()} entries:")

        for pos in ['first', 'early', 'middle', 'late', 'last']:
            if pos not in position_prefix[length_cat]:
                continue
            counter = position_prefix[length_cat][pos]
            total = sum(counter.values())
            if total < 10:
                continue

            # Top 4 prefixes
            top = counter.most_common(4)
            dist_str = ", ".join(f"{p}:{100*c/total:.0f}%" for p, c in top)
            print(f"  {pos:8s}: {dist_str} (n={total})")

    return {
        'test': 'entry_structure_patterns',
        'position_prefix': {k: {k2: dict(v2) for k2, v2 in v.items()}
                          for k, v in position_prefix.items()}
    }


def test_5_non_prefix_boundary_tokens():
    """
    Test 5: What are the non-prefix tokens that appear at boundaries?
    """
    print("\n" + "=" * 70)
    print("Test 5: Non-PREFIX Boundary Tokens Analysis")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    first_tokens_no_prefix = Counter()
    last_tokens_no_prefix = Counter()

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        first_tok = tokens[0]
        last_tok = tokens[-1]

        # Check if first has standard prefix
        has_first_prefix = any(first_tok.startswith(pfx) for pfx in PREFIXES)
        if not has_first_prefix:
            first_tokens_no_prefix[first_tok] += 1

        # Check if last has standard prefix
        has_last_prefix = any(last_tok.startswith(pfx) for pfx in PREFIXES)
        if not has_last_prefix:
            last_tokens_no_prefix[last_tok] += 1

    print(f"\nFirst tokens WITHOUT standard prefix:")
    print(f"Total unique: {len(first_tokens_no_prefix)}")
    print(f"Top 20:")
    for tok, count in first_tokens_no_prefix.most_common(20):
        morph = analyze_token_morphology(tok)
        features = []
        if morph['starts_with_d']: features.append('d-')
        if morph['starts_with_s']: features.append('s-')
        if morph['starts_with_t']: features.append('t-')
        if morph['starts_with_q']: features.append('q-')
        feature_str = "".join(features) if features else "other"
        print(f"  {tok}: {count} (starts: {feature_str})")

    print(f"\nLast tokens WITHOUT standard prefix:")
    print(f"Total unique: {len(last_tokens_no_prefix)}")
    print(f"Top 20:")
    for tok, count in last_tokens_no_prefix.most_common(20):
        morph = analyze_token_morphology(tok)
        features = []
        if morph['ends_with_y']: features.append('-y')
        if morph['ends_with_n']: features.append('-n')
        if morph['ends_with_m']: features.append('-m')
        if morph['ends_with_l']: features.append('-l')
        feature_str = "".join(features) if features else "other"
        print(f"  {tok}: {count} (ends: {feature_str})")

    # Analyze patterns
    print(f"\nNon-prefix first token patterns:")
    d_starts = sum(c for t, c in first_tokens_no_prefix.items() if t.startswith('d'))
    s_starts = sum(c for t, c in first_tokens_no_prefix.items() if t.startswith('s'))
    t_starts = sum(c for t, c in first_tokens_no_prefix.items() if t.startswith('t'))
    total_first = sum(first_tokens_no_prefix.values())
    print(f"  d-initial: {d_starts} ({100*d_starts/total_first:.1f}%)")
    print(f"  s-initial: {s_starts} ({100*s_starts/total_first:.1f}%)")
    print(f"  t-initial: {t_starts} ({100*t_starts/total_first:.1f}%)")

    print(f"\nNon-prefix last token patterns:")
    y_ends = sum(c for t, c in last_tokens_no_prefix.items() if t.endswith('y'))
    n_ends = sum(c for t, c in last_tokens_no_prefix.items() if t.endswith('n'))
    m_ends = sum(c for t, c in last_tokens_no_prefix.items() if t.endswith('m'))
    l_ends = sum(c for t, c in last_tokens_no_prefix.items() if t.endswith('l'))
    total_last = sum(last_tokens_no_prefix.values())
    print(f"  -y ending: {y_ends} ({100*y_ends/total_last:.1f}%)")
    print(f"  -n ending: {n_ends} ({100*n_ends/total_last:.1f}%)")
    print(f"  -m ending: {m_ends} ({100*m_ends/total_last:.1f}%)")
    print(f"  -l ending: {l_ends} ({100*l_ends/total_last:.1f}%)")

    return {
        'test': 'non_prefix_boundary_tokens',
        'first_tokens_no_prefix': dict(first_tokens_no_prefix.most_common(50)),
        'last_tokens_no_prefix': dict(last_tokens_no_prefix.most_common(50)),
        'd_initial_rate': d_starts / total_first if total_first > 0 else 0,
        'y_ending_rate': y_ends / total_last if total_last > 0 else 0
    }


def test_6_da_as_boundary_marker():
    """
    Test 6: Special analysis of DA-family tokens at boundaries.
    DA is known to be articulation punctuation (C422).
    """
    print("\n" + "=" * 70)
    print("Test 6: DA-Family at Boundaries")
    print("=" * 70)
    print("DA is articulation punctuation (C422). How does it behave at line boundaries?")

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()

    # DA-family tokens
    da_first = Counter()
    da_last = Counter()
    da_middle = Counter()

    non_da_first = 0
    non_da_last = 0

    for (folio, line_num), group in a_data.groupby(['folio', 'line_number']):
        tokens = [str(t).lower() for t in group['word'].values]
        if len(tokens) < 2:
            continue

        first_tok = tokens[0]
        last_tok = tokens[-1]

        if first_tok.startswith('da'):
            da_first[first_tok] += 1
        else:
            non_da_first += 1

        if last_tok.startswith('da'):
            da_last[last_tok] += 1
        else:
            non_da_last += 1

        for tok in tokens[1:-1]:
            if tok.startswith('da'):
                da_middle[tok] += 1

    total_da_first = sum(da_first.values())
    total_da_last = sum(da_last.values())
    total_da_middle = sum(da_middle.values())

    print(f"\nDA-family distribution:")
    print(f"  First position: {total_da_first} tokens")
    print(f"  Middle positions: {total_da_middle} tokens")
    print(f"  Last position: {total_da_last} tokens")

    total_entries = total_da_first + non_da_first
    print(f"\nDA at first position: {100*total_da_first/total_entries:.1f}%")
    print(f"DA at last position: {100*total_da_last/total_entries:.1f}%")

    print(f"\nTop DA tokens at FIRST position:")
    for tok, count in da_first.most_common(10):
        print(f"  {tok}: {count}")

    print(f"\nTop DA tokens at LAST position:")
    for tok, count in da_last.most_common(10):
        print(f"  {tok}: {count}")

    print(f"\nTop DA tokens at MIDDLE positions:")
    for tok, count in da_middle.most_common(10):
        print(f"  {tok}: {count}")

    # Is DA at last position characteristic?
    # Compare to baseline DA rate
    all_tokens = [str(t).lower() for t in a_data['word']]
    da_baseline = sum(1 for t in all_tokens if t.startswith('da')) / len(all_tokens)

    da_last_rate = total_da_last / total_entries
    da_first_rate = total_da_first / total_entries

    print(f"\nDA rates:")
    print(f"  Baseline (all positions): {100*da_baseline:.1f}%")
    print(f"  At first position: {100*da_first_rate:.1f}% ({da_first_rate/da_baseline:.2f}x)")
    print(f"  At last position: {100*da_last_rate:.1f}% ({da_last_rate/da_baseline:.2f}x)")

    return {
        'test': 'da_as_boundary_marker',
        'da_first': dict(da_first.most_common(20)),
        'da_last': dict(da_last.most_common(20)),
        'da_middle': dict(da_middle.most_common(20)),
        'da_baseline_rate': da_baseline,
        'da_first_rate': da_first_rate,
        'da_last_rate': da_last_rate
    }


def run_prefix_boundary_deep():
    """Run all PREFIX-boundary deep analysis tests."""
    print("\n" + "=" * 80)
    print("CAR PREFIX-BOUNDARY DEEP ANALYSIS")
    print("=" * 80)

    results = {
        'phase': 'CAR-PBD',
        'name': 'PREFIX-Boundary Deep Analysis',
        'tests': {}
    }

    results['tests']['test_1'] = test_1_full_position_by_prefix()
    results['tests']['test_2'] = test_2_first_token_prefix_match()
    results['tests']['test_3'] = test_3_last_token_prefix_match()
    results['tests']['test_4'] = test_4_entry_structure_patterns()
    results['tests']['test_5'] = test_5_non_prefix_boundary_tokens()
    results['tests']['test_6'] = test_6_da_as_boundary_marker()

    # Summary
    print("\n" + "=" * 80)
    print("PREFIX-BOUNDARY DEEP ANALYSIS SUMMARY")
    print("=" * 80)

    first_match = results['tests']['test_2']['match_rate']
    last_match = results['tests']['test_3']['match_rate']

    print(f"\nKey findings:")
    print(f"  First token matches dominant PREFIX: {100*first_match:.1f}%")
    print(f"  Last token matches dominant PREFIX: {100*last_match:.1f}%")

    da_first = results['tests']['test_6']['da_first_rate']
    da_last = results['tests']['test_6']['da_last_rate']
    da_base = results['tests']['test_6']['da_baseline_rate']

    print(f"\n  DA-family at first: {100*da_first:.1f}% (baseline {100*da_base:.1f}%)")
    print(f"  DA-family at last: {100*da_last:.1f}% (baseline {100*da_base:.1f}%)")

    if da_last > da_base * 1.5:
        print(f"\n  -> DA is ENRICHED at last position ({da_last/da_base:.1f}x)")
    if da_first < da_base * 0.5:
        print(f"  -> DA is DEPLETED at first position ({da_first/da_base:.1f}x)")

    # Save results
    output_file = PHASE_DIR / 'car_prefix_boundary_deep_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_prefix_boundary_deep()
