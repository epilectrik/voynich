#!/usr/bin/env python3
"""
A-Internal Stratification: Run all 8 tests

Tests whether A-exclusive MIDDLEs (349, never in B) behave differently
from A/B-shared MIDDLEs (268) within Currier A.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
MIDDLE_CLASSES_PATH = RESULTS_DIR / 'middle_classes.json'
TOKEN_DATA_PATH = RESULTS_DIR / 'token_data.json'
ENTRY_DATA_PATH = RESULTS_DIR / 'entry_data.json'
OUTPUT_PATH = RESULTS_DIR / 'stratification_tests.json'


def load_data():
    """Load prepared data files."""
    with open(MIDDLE_CLASSES_PATH) as f:
        middle_classes = json.load(f)
    with open(TOKEN_DATA_PATH) as f:
        tokens = json.load(f)
    with open(ENTRY_DATA_PATH) as f:
        entries = json.load(f)
    return middle_classes, tokens, entries


def cramers_v(confusion_matrix):
    """Calculate Cramér's V for a confusion matrix."""
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = np.sum(confusion_matrix)
    min_dim = min(np.array(confusion_matrix).shape) - 1
    if min_dim == 0 or n == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


def test_1_positional_distribution(tokens, middle_classes):
    """Test: Do A-exclusive MIDDLEs appear preferentially as openers/closers/interior?"""
    print("\n" + "=" * 70)
    print("TEST 1: POSITIONAL DISTRIBUTION")
    print("=" * 70)

    a_exclusive = set(middle_classes['a_exclusive_middles'])

    # Group tokens by entry
    entries = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line'])
        entries[key].append(t)

    # Classify positions
    position_counts = {'exclusive': Counter(), 'shared': Counter()}

    for key, entry_tokens in entries.items():
        n = len(entry_tokens)
        for i, t in enumerate(entry_tokens):
            cls = 'exclusive' if t['middle'] in a_exclusive else 'shared'
            if i == 0:
                pos = 'OPENER'
            elif i == n - 1:
                pos = 'CLOSER'
            else:
                pos = 'INTERIOR'
            position_counts[cls][pos] += 1

    print("\nPosition counts:")
    for cls in ['exclusive', 'shared']:
        total = sum(position_counts[cls].values())
        print(f"  {cls.upper()}:")
        for pos in ['OPENER', 'INTERIOR', 'CLOSER']:
            count = position_counts[cls].get(pos, 0)
            pct = 100 * count / total if total > 0 else 0
            print(f"    {pos}: {count} ({pct:.1f}%)")

    # Chi-square test
    matrix = [
        [position_counts['exclusive'].get(p, 0) for p in ['OPENER', 'INTERIOR', 'CLOSER']],
        [position_counts['shared'].get(p, 0) for p in ['OPENER', 'INTERIOR', 'CLOSER']]
    ]

    # Handle sparse matrix
    if min(sum(matrix[0]), sum(matrix[1])) < 5:
        print("\n  WARNING: Sparse data, chi-square may be unreliable")

    chi2, p_value, dof, expected = stats.chi2_contingency(matrix)
    v = cramers_v(matrix)

    print(f"\n  Chi-square: {chi2:.2f}, p={p_value:.6f}")
    print(f"  Cramér's V: {v:.3f}")
    print(f"  Effect: {'SIGNIFICANT' if p_value < 0.00625 and v > 0.1 else 'NOT SIGNIFICANT'}")

    return {
        'position_counts': {k: dict(v) for k, v in position_counts.items()},
        'chi2': chi2,
        'p_value': p_value,
        'cramers_v': v,
        'significant': p_value < 0.00625 and v > 0.1
    }


def test_2_section_distribution(tokens, middle_classes):
    """Test: Do A-exclusive MIDDLEs concentrate in specific sections?"""
    print("\n" + "=" * 70)
    print("TEST 2: SECTION DISTRIBUTION (by folio number)")
    print("=" * 70)

    import re

    a_exclusive = set(middle_classes['a_exclusive_middles'])

    def get_section(folio):
        """Categorize folio into section based on number."""
        match = re.search(r'f(\d+)', folio.lower())
        if match:
            num = int(match.group(1))
            if num <= 57:
                return 'herbal_a'
            elif num >= 87 and num <= 102:
                return 'herbal_c'
            elif num >= 103:
                return 'text'
        return 'other'

    section_counts = {'exclusive': Counter(), 'shared': Counter()}

    for t in tokens:
        cls = 'exclusive' if t['middle'] in a_exclusive else 'shared'
        section = get_section(t['folio'])
        section_counts[cls][section] += 1

    print("\nSection counts:")
    all_sections = sorted(set(section_counts['exclusive'].keys()) | set(section_counts['shared'].keys()))
    for cls in ['exclusive', 'shared']:
        total = sum(section_counts[cls].values())
        print(f"  {cls.upper()}: {total} total")
        for section in all_sections:
            count = section_counts[cls].get(section, 0)
            pct = 100 * count / total if total > 0 else 0
            print(f"    {section}: {count} ({pct:.1f}%)")

    # Chi-square for sections with sufficient counts
    sections_to_use = [s for s in all_sections
                       if section_counts['exclusive'].get(s, 0) + section_counts['shared'].get(s, 0) >= 5]

    if len(sections_to_use) < 2:
        print("\n  WARNING: Not enough sections with data for chi-square test")
        return {'insufficient_sections': True, 'section_counts': {k: dict(v) for k, v in section_counts.items()}}

    matrix = [
        [section_counts['exclusive'].get(s, 0) for s in sections_to_use],
        [section_counts['shared'].get(s, 0) for s in sections_to_use]
    ]

    # Check for zero rows/columns
    if min(sum(matrix[0]), sum(matrix[1])) == 0:
        print("\n  WARNING: One class has zero counts, cannot run chi-square")
        return {'insufficient_data': True, 'section_counts': {k: dict(v) for k, v in section_counts.items()}}

    chi2, p_value, dof, expected = stats.chi2_contingency(matrix)
    v = cramers_v(matrix)

    print(f"\n  Chi-square: {chi2:.2f}, p={p_value:.6f}")
    print(f"  Cramér's V: {v:.3f}")
    print(f"  Effect: {'SIGNIFICANT' if p_value < 0.00625 and v > 0.1 else 'NOT SIGNIFICANT'}")

    return {
        'section_counts': {k: dict(v) for k, v in section_counts.items()},
        'chi2': chi2,
        'p_value': p_value,
        'cramers_v': v,
        'significant': p_value < 0.00625 and v > 0.1
    }


def test_3_folio_clustering(tokens, middle_classes):
    """Test: Do A-exclusive MIDDLEs cluster in specific folios?"""
    print("\n" + "=" * 70)
    print("TEST 3: FOLIO CLUSTERING")
    print("=" * 70)

    a_exclusive = set(middle_classes['a_exclusive_middles'])
    freqs = middle_classes['middle_frequencies']

    # Calculate folio spread for each MIDDLE
    middle_folios = defaultdict(set)
    for t in tokens:
        middle_folios[t['middle']].add(t['folio'])

    exclusive_spreads = []
    shared_spreads = []

    for middle, folios in middle_folios.items():
        spread = len(folios)
        if middle in a_exclusive:
            exclusive_spreads.append(spread)
        else:
            shared_spreads.append(spread)

    print(f"\nFolio spread (number of folios each MIDDLE appears in):")
    print(f"  A-exclusive: mean={np.mean(exclusive_spreads):.2f}, median={np.median(exclusive_spreads):.1f}, n={len(exclusive_spreads)}")
    print(f"  A/B-shared:  mean={np.mean(shared_spreads):.2f}, median={np.median(shared_spreads):.1f}, n={len(shared_spreads)}")

    # KS test
    ks_stat, p_value = stats.ks_2samp(exclusive_spreads, shared_spreads)

    print(f"\n  KS statistic: {ks_stat:.3f}, p={p_value:.6f}")
    print(f"  Effect: {'SIGNIFICANT' if p_value < 0.00625 and ks_stat > 0.1 else 'NOT SIGNIFICANT'}")

    return {
        'exclusive_spread': {'mean': np.mean(exclusive_spreads), 'median': np.median(exclusive_spreads), 'n': len(exclusive_spreads)},
        'shared_spread': {'mean': np.mean(shared_spreads), 'median': np.median(shared_spreads), 'n': len(shared_spreads)},
        'ks_stat': ks_stat,
        'p_value': p_value,
        'significant': p_value < 0.00625 and ks_stat > 0.1
    }


def test_4_adjacency_patterns(entries, middle_classes):
    """Test: Do entries with A-exclusive MIDDLEs cluster differently?"""
    print("\n" + "=" * 70)
    print("TEST 4: ADJACENCY PATTERNS")
    print("=" * 70)

    # Sort entries by folio and line for adjacency analysis
    sorted_entries = sorted(entries, key=lambda e: (e['folio'], e['line']))

    # Find runs of same composition
    composition_counts = Counter(e['composition'] for e in sorted_entries)
    print(f"\nEntry composition distribution:")
    for comp, count in composition_counts.most_common():
        print(f"  {comp}: {count} ({100*count/len(sorted_entries):.1f}%)")

    # Check if PURE_EXCLUSIVE entries are clustered or dispersed
    exclusive_positions = []
    for i, e in enumerate(sorted_entries):
        if e['composition'] == 'PURE_EXCLUSIVE':
            exclusive_positions.append(i)

    if len(exclusive_positions) < 2:
        print("\n  Too few PURE_EXCLUSIVE entries for adjacency analysis")
        return {'insufficient_data': True}

    # Calculate gaps between exclusive entries
    gaps = [exclusive_positions[i+1] - exclusive_positions[i] for i in range(len(exclusive_positions)-1)]
    mean_gap = np.mean(gaps)
    median_gap = np.median(gaps)

    # Expected gap if random
    n_total = len(sorted_entries)
    n_excl = len(exclusive_positions)
    expected_gap = n_total / n_excl

    print(f"\n  PURE_EXCLUSIVE entries: {n_excl}")
    print(f"  Mean gap between them: {mean_gap:.1f}")
    print(f"  Expected gap (if random): {expected_gap:.1f}")
    print(f"  Ratio (actual/expected): {mean_gap/expected_gap:.2f}")

    # Test if gaps are smaller than expected (clustering)
    # Use one-sample t-test against expected
    t_stat, p_value = stats.ttest_1samp(gaps, expected_gap)

    # Effect size: ratio of actual to expected gap
    effect = mean_gap / expected_gap

    print(f"\n  t-statistic: {t_stat:.2f}, p={p_value:.6f}")
    print(f"  Clustering: {'YES (gaps smaller than random)' if mean_gap < expected_gap and p_value < 0.00625 else 'NO'}")

    return {
        'n_exclusive_entries': n_excl,
        'mean_gap': mean_gap,
        'expected_gap': expected_gap,
        'gap_ratio': effect,
        't_stat': t_stat,
        'p_value': p_value,
        'clustered': mean_gap < expected_gap and p_value < 0.00625
    }


def test_5_morphological_profile(tokens, middle_classes):
    """Test: Do A-exclusive MIDDLEs have different PREFIX/SUFFIX distributions?"""
    print("\n" + "=" * 70)
    print("TEST 5: MORPHOLOGICAL PROFILE")
    print("=" * 70)

    a_exclusive = set(middle_classes['a_exclusive_middles'])

    # PREFIX distribution
    prefix_counts = {'exclusive': Counter(), 'shared': Counter()}
    suffix_counts = {'exclusive': Counter(), 'shared': Counter()}

    for t in tokens:
        cls = 'exclusive' if t['middle'] in a_exclusive else 'shared'
        prefix_counts[cls][t['prefix']] += 1
        suffix_counts[cls][t['suffix'] if t['suffix'] else '_NONE_'] += 1

    print("\nPREFIX distribution:")
    all_prefixes = sorted(set(prefix_counts['exclusive'].keys()) | set(prefix_counts['shared'].keys()))
    for prefix in all_prefixes[:10]:  # Top 10
        excl = prefix_counts['exclusive'].get(prefix, 0)
        shared = prefix_counts['shared'].get(prefix, 0)
        excl_total = sum(prefix_counts['exclusive'].values())
        shared_total = sum(prefix_counts['shared'].values())
        excl_pct = 100 * excl / excl_total if excl_total > 0 else 0
        shared_pct = 100 * shared / shared_total if shared_total > 0 else 0
        print(f"  {prefix:6s}: exclusive={excl_pct:5.1f}%  shared={shared_pct:5.1f}%")

    # Chi-square for PREFIX
    prefixes_to_use = [p for p in all_prefixes if prefix_counts['exclusive'].get(p, 0) + prefix_counts['shared'].get(p, 0) >= 10]
    matrix = [
        [prefix_counts['exclusive'].get(p, 0) for p in prefixes_to_use],
        [prefix_counts['shared'].get(p, 0) for p in prefixes_to_use]
    ]

    chi2, p_value, dof, expected = stats.chi2_contingency(matrix)
    v = cramers_v(matrix)

    print(f"\n  PREFIX Chi-square: {chi2:.2f}, p={p_value:.6f}")
    print(f"  PREFIX Cramér's V: {v:.3f}")

    # SUFFIX distribution (top suffixes)
    print("\nSUFFIX distribution (top 10):")
    all_suffixes = sorted(set(suffix_counts['exclusive'].keys()) | set(suffix_counts['shared'].keys()),
                          key=lambda s: -(suffix_counts['exclusive'].get(s, 0) + suffix_counts['shared'].get(s, 0)))
    for suffix in all_suffixes[:10]:
        excl = suffix_counts['exclusive'].get(suffix, 0)
        shared = suffix_counts['shared'].get(suffix, 0)
        excl_total = sum(suffix_counts['exclusive'].values())
        shared_total = sum(suffix_counts['shared'].values())
        excl_pct = 100 * excl / excl_total if excl_total > 0 else 0
        shared_pct = 100 * shared / shared_total if shared_total > 0 else 0
        print(f"  {suffix:10s}: exclusive={excl_pct:5.1f}%  shared={shared_pct:5.1f}%")

    # Chi-square for SUFFIX
    suffixes_to_use = [s for s in all_suffixes if suffix_counts['exclusive'].get(s, 0) + suffix_counts['shared'].get(s, 0) >= 10]
    matrix_suffix = [
        [suffix_counts['exclusive'].get(s, 0) for s in suffixes_to_use],
        [suffix_counts['shared'].get(s, 0) for s in suffixes_to_use]
    ]

    chi2_suffix, p_suffix, _, _ = stats.chi2_contingency(matrix_suffix)
    v_suffix = cramers_v(matrix_suffix)

    print(f"\n  SUFFIX Chi-square: {chi2_suffix:.2f}, p={p_suffix:.6f}")
    print(f"  SUFFIX Cramér's V: {v_suffix:.3f}")

    significant = (p_value < 0.00625 and v > 0.1) or (p_suffix < 0.00625 and v_suffix > 0.1)
    print(f"  Effect: {'SIGNIFICANT' if significant else 'NOT SIGNIFICANT'}")

    return {
        'prefix_counts': {k: dict(v) for k, v in prefix_counts.items()},
        'suffix_counts': {k: dict(v) for k, v in suffix_counts.items()},
        'prefix_chi2': chi2,
        'prefix_p_value': p_value,
        'prefix_cramers_v': v,
        'suffix_chi2': chi2_suffix,
        'suffix_p_value': p_suffix,
        'suffix_cramers_v': v_suffix,
        'significant': significant
    }


def test_6_azc_presence(middle_classes):
    """Test: Do A-exclusive MIDDLEs appear in AZC at all?"""
    print("\n" + "=" * 70)
    print("TEST 6: AZC PRESENCE")
    print("=" * 70)

    a_exclusive = set(middle_classes['a_exclusive_middles'])
    a_shared = set(middle_classes['a_shared_middles'])
    azc_middles = set(middle_classes.get('azc_middles', []))

    # The prep script shows 0 AZC - need to check why
    # For now, report what we have

    excl_in_azc = a_exclusive & azc_middles
    shared_in_azc = a_shared & azc_middles

    print(f"\n  AZC MIDDLEs detected: {len(azc_middles)}")
    print(f"  A-exclusive in AZC: {len(excl_in_azc)} / {len(a_exclusive)} ({100*len(excl_in_azc)/len(a_exclusive):.1f}%)")
    print(f"  A/B-shared in AZC: {len(shared_in_azc)} / {len(a_shared)} ({100*len(shared_in_azc)/len(a_shared):.1f}%)")

    if len(azc_middles) == 0:
        print("\n  WARNING: No AZC data loaded. AZC folio detection needs review.")
        print("  This test is INCONCLUSIVE pending data fix.")
        return {'inconclusive': True, 'reason': 'No AZC data loaded'}

    # Fisher's exact test
    table = [
        [len(excl_in_azc), len(a_exclusive) - len(excl_in_azc)],
        [len(shared_in_azc), len(a_shared) - len(shared_in_azc)]
    ]
    odds_ratio, p_value = stats.fisher_exact(table)

    print(f"\n  Fisher's exact: odds ratio={odds_ratio:.2f}, p={p_value:.6f}")

    return {
        'exclusive_in_azc': len(excl_in_azc),
        'shared_in_azc': len(shared_in_azc),
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'significant': p_value < 0.00625
    }


def test_7_entry_composition(entries, middle_classes):
    """Test: Are A entries typically pure or mixed?"""
    print("\n" + "=" * 70)
    print("TEST 7: ENTRY COMPOSITION")
    print("=" * 70)

    comp_counts = Counter(e['composition'] for e in entries)
    total = len(entries)

    print(f"\nEntry composition:")
    for comp in ['PURE_EXCLUSIVE', 'MIXED', 'PURE_SHARED']:
        count = comp_counts.get(comp, 0)
        print(f"  {comp}: {count} ({100*count/total:.1f}%)")

    # Test against random expectation
    # Under independence, P(pure_exclusive) = p_excl^n, P(pure_shared) = p_shared^n
    # where p_excl = proportion of exclusive tokens, n = entry length

    # Simpler: if random, we'd expect MIXED to dominate
    # The fact that there are NO MIXED entries is itself the finding

    observed_mixed = comp_counts.get('MIXED', 0)
    observed_pure = comp_counts.get('PURE_EXCLUSIVE', 0) + comp_counts.get('PURE_SHARED', 0)

    # Calculate expected mixed under independence
    # Use the entry-level token proportions
    all_exclusive_tokens = sum(e['n_exclusive'] for e in entries)
    all_shared_tokens = sum(e['n_shared'] for e in entries)
    total_tokens = all_exclusive_tokens + all_shared_tokens

    p_excl = all_exclusive_tokens / total_tokens if total_tokens > 0 else 0
    p_shared = all_shared_tokens / total_tokens if total_tokens > 0 else 0

    # For each entry, probability of being pure = p_excl^n + p_shared^n
    # probability of being mixed = 1 - p_excl^n - p_shared^n
    expected_pure = 0
    expected_mixed = 0
    for e in entries:
        n = e['n_tokens']
        p_pure = (p_excl ** n) + (p_shared ** n)
        expected_pure += p_pure
        expected_mixed += (1 - p_pure)

    print(f"\n  Token-level: {100*p_excl:.1f}% exclusive, {100*p_shared:.1f}% shared")
    print(f"\n  Observed: {observed_pure} pure, {observed_mixed} mixed")
    print(f"  Expected (if random): {expected_pure:.0f} pure, {expected_mixed:.0f} mixed")

    # Chi-square test
    observed = [observed_pure, observed_mixed]
    expected = [expected_pure, expected_mixed]

    if expected_mixed > 0:
        chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
    else:
        chi2 = float('inf')
        p_value = 0.0

    print(f"\n  Chi-square: {chi2:.2f}, p={p_value:.6f}")
    print(f"  Effect: {'SIGNIFICANT - entries are NOT randomly mixed' if p_value < 0.00625 else 'NOT SIGNIFICANT'}")

    return {
        'composition_counts': dict(comp_counts),
        'observed_pure': observed_pure,
        'observed_mixed': observed_mixed,
        'expected_pure': expected_pure,
        'expected_mixed': expected_mixed,
        'chi2': chi2,
        'p_value': p_value,
        'significant': p_value < 0.00625
    }


def test_8_frequency_control(tokens, middle_classes):
    """Test: Are observed differences explained by frequency effects?"""
    print("\n" + "=" * 70)
    print("TEST 8: FREQUENCY CONTROL")
    print("=" * 70)

    a_exclusive = set(middle_classes['a_exclusive_middles'])
    freqs = middle_classes['middle_frequencies']

    # Frequency distribution by class
    excl_freqs = [freqs[m] for m in a_exclusive if m in freqs]
    shared_freqs = [freqs[m] for m in middle_classes['a_shared_middles'] if m in freqs]

    print(f"\nFrequency distribution:")
    print(f"  A-exclusive: mean={np.mean(excl_freqs):.1f}, median={np.median(excl_freqs):.0f}, max={max(excl_freqs)}")
    print(f"  A/B-shared:  mean={np.mean(shared_freqs):.1f}, median={np.median(shared_freqs):.0f}, max={max(shared_freqs)}")

    # Mann-Whitney U test (non-parametric)
    u_stat, p_value = stats.mannwhitneyu(excl_freqs, shared_freqs, alternative='two-sided')

    print(f"\n  Mann-Whitney U: {u_stat:.0f}, p={p_value:.6f}")

    # Effect size: rank-biserial correlation
    n1, n2 = len(excl_freqs), len(shared_freqs)
    r = 1 - (2 * u_stat) / (n1 * n2)

    print(f"  Rank-biserial correlation: {r:.3f}")
    print(f"  A-exclusive tokens are {'SIGNIFICANTLY LOWER FREQUENCY' if p_value < 0.00625 else 'NOT significantly different in frequency'}")

    # Frequency bins for controlled analysis
    all_middles = list(a_exclusive) + list(middle_classes['a_shared_middles'])
    all_freqs_list = [freqs.get(m, 0) for m in all_middles]

    # Create quintile bins
    percentiles = [0, 20, 40, 60, 80, 100]
    bins = np.percentile(all_freqs_list, percentiles)
    bins = list(set(bins))  # Remove duplicates
    bins.sort()

    print(f"\n  Frequency quintile bins: {bins}")

    # Count class membership per bin
    bin_counts = defaultdict(lambda: {'exclusive': 0, 'shared': 0})
    for m in a_exclusive:
        f = freqs.get(m, 0)
        for i in range(len(bins) - 1):
            if bins[i] <= f < bins[i + 1] or (i == len(bins) - 2 and f == bins[i + 1]):
                bin_counts[i]['exclusive'] += 1
                break

    for m in middle_classes['a_shared_middles']:
        f = freqs.get(m, 0)
        for i in range(len(bins) - 1):
            if bins[i] <= f < bins[i + 1] or (i == len(bins) - 2 and f == bins[i + 1]):
                bin_counts[i]['shared'] += 1
                break

    print(f"\n  Class distribution across frequency bins:")
    for i in sorted(bin_counts.keys()):
        excl = bin_counts[i]['exclusive']
        shared = bin_counts[i]['shared']
        total = excl + shared
        print(f"    Bin {i} ({bins[i]:.0f}-{bins[i+1]:.0f}): exclusive={excl} ({100*excl/total:.0f}%), shared={shared} ({100*shared/total:.0f}%)")

    return {
        'exclusive_freq_stats': {'mean': np.mean(excl_freqs), 'median': np.median(excl_freqs), 'max': max(excl_freqs)},
        'shared_freq_stats': {'mean': np.mean(shared_freqs), 'median': np.median(shared_freqs), 'max': max(shared_freqs)},
        'mann_whitney_u': u_stat,
        'p_value': p_value,
        'rank_biserial': r,
        'significant_frequency_difference': p_value < 0.00625,
        'bin_counts': {str(k): v for k, v in bin_counts.items()}
    }


def main():
    print("=" * 70)
    print("A-INTERNAL STRATIFICATION: ALL TESTS")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    middle_classes, tokens, entries = load_data()
    print(f"  {len(tokens)} tokens")
    print(f"  {len(entries)} entries")
    print(f"  {len(middle_classes['a_exclusive_middles'])} A-exclusive MIDDLEs")
    print(f"  {len(middle_classes['a_shared_middles'])} A/B-shared MIDDLEs")

    results = {}

    # Run all tests
    results['test_1_position'] = test_1_positional_distribution(tokens, middle_classes)
    results['test_2_section'] = test_2_section_distribution(tokens, middle_classes)
    results['test_3_folio'] = test_3_folio_clustering(tokens, middle_classes)
    results['test_4_adjacency'] = test_4_adjacency_patterns(entries, middle_classes)
    results['test_5_morphology'] = test_5_morphological_profile(tokens, middle_classes)
    results['test_6_azc'] = test_6_azc_presence(middle_classes)
    results['test_7_composition'] = test_7_entry_composition(entries, middle_classes)
    results['test_8_frequency'] = test_8_frequency_control(tokens, middle_classes)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    significant_count = 0
    print("\n  Test results:")
    for test_name, test_results in results.items():
        if 'inconclusive' in test_results:
            status = 'INCONCLUSIVE'
        elif 'insufficient_data' in test_results:
            status = 'INSUFFICIENT DATA'
        elif test_results.get('significant', False) or test_results.get('clustered', False):
            status = 'SIGNIFICANT'
            significant_count += 1
        else:
            status = 'NOT SIGNIFICANT'
        print(f"    {test_name}: {status}")

    print(f"\n  Significant effects: {significant_count}/8")

    if significant_count >= 5:
        verdict = "CONFIRMED - A has internal functional stratification"
    elif significant_count >= 2:
        verdict = "PARTIAL - Some stratification detected (Tier 3)"
    else:
        verdict = "NULL - A is internally homogeneous"

    print(f"\n  VERDICT: {verdict}")

    results['summary'] = {
        'significant_count': significant_count,
        'verdict': verdict
    }

    # Save results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_PATH}")

    return results


if __name__ == '__main__':
    main()
