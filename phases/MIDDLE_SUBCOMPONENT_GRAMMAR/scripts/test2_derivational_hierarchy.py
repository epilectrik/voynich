#!/usr/bin/env python3
"""
Test 2: Derivational Hierarchy

Hypothesis: High-frequency MIDDLEs "seed" longer singletons productively.

Method:
1. For each repeater MIDDLE (freq > 1), count how many singletons contain it as:
   - Prefix (singleton starts with repeater)
   - Suffix (singleton ends with repeater)
   - Infix (singleton contains repeater internally)
2. Compute "productivity ratio" = actual derivations / expected derivations
3. Baseline (CRITICAL): Expected derivations based on character frequency

Pass criteria: Productivity ratio significantly > 1.0 for high-frequency MIDDLEs
"""

import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def expected_substring_count(substring, corpus, char_probs):
    """
    Estimate expected count of substring in corpus based on character probabilities.

    For each MIDDLE in corpus, compute P(contains substring) based on:
    - MIDDLE length
    - Substring length
    - Character probabilities (null model: random string)
    """
    k = len(substring)
    if k == 0:
        return 0

    # Probability of generating the substring at any position
    p_substring = 1.0
    for c in substring:
        p_substring *= char_probs.get(c, 0.001)

    total_expected = 0
    for middle in corpus:
        n = len(middle)
        if n < k:
            continue
        # Number of positions where substring could start
        positions = n - k + 1
        # Expected matches at each position (approximately)
        p_at_least_one = 1 - (1 - p_substring) ** positions
        total_expected += p_at_least_one

    return total_expected


def main():
    print("=" * 70)
    print("TEST 2: DERIVATIONAL HIERARCHY")
    print("=" * 70)
    print()

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Get Currier A MIDDLEs with frequency
    df_a = df[df['language'] == 'A']
    df_a = df_a.copy()
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_a = df_a[df_a['middle'].notna()]

    middle_counts = df_a['middle'].value_counts()

    # Classify into singletons and repeaters
    singletons = set(m for m, c in middle_counts.items() if c == 1)
    repeaters = set(m for m, c in middle_counts.items() if c > 1)

    print(f"Currier A MIDDLEs:")
    print(f"  Singletons (freq=1): {len(singletons)}")
    print(f"  Repeaters (freq>1): {len(repeaters)}")
    print()

    # Character probability distribution (from all MIDDLEs for null model)
    all_chars = ''.join(middle_counts.index)
    char_freq = Counter(all_chars)
    total_chars = sum(char_freq.values())
    char_probs = {c: f/total_chars for c, f in char_freq.items()}

    print(f"Character distribution (top 10):")
    for c, f in char_freq.most_common(10):
        print(f"  '{c}': {f} ({100*f/total_chars:.1f}%)")
    print()

    # ============================================================
    # PHASE 1: Count derivations for each repeater
    # ============================================================
    print("=" * 70)
    print("PHASE 1: DERIVATION COUNTS")
    print("=" * 70)
    print()

    derivational_analysis = {}

    for rep in repeaters:
        if len(rep) < 2:  # Skip single-char repeaters (too common)
            continue

        prefix_seeds = 0  # singletons starting with repeater
        suffix_seeds = 0  # singletons ending with repeater
        infix_seeds = 0   # singletons containing repeater internally

        for sing in singletons:
            if len(sing) <= len(rep):
                continue

            if sing.startswith(rep):
                prefix_seeds += 1
            elif sing.endswith(rep):
                suffix_seeds += 1
            elif rep in sing:
                infix_seeds += 1

        total_seeds = prefix_seeds + suffix_seeds + infix_seeds

        if total_seeds > 0:
            derivational_analysis[rep] = {
                'frequency': int(middle_counts[rep]),
                'length': len(rep),
                'prefix_seeds': prefix_seeds,
                'suffix_seeds': suffix_seeds,
                'infix_seeds': infix_seeds,
                'total_seeds': total_seeds
            }

    print(f"Repeaters that seed singletons: {len(derivational_analysis)}")
    print()

    # Show top by total seeds
    print("Top repeaters by singleton derivations:")
    top_by_seeds = sorted(derivational_analysis.items(), key=lambda x: -x[1]['total_seeds'])[:20]
    for rep, stats in top_by_seeds:
        print(f"  '{rep}' (freq={stats['frequency']}): {stats['total_seeds']} seeds "
              f"(pre={stats['prefix_seeds']}, suf={stats['suffix_seeds']}, inf={stats['infix_seeds']})")
    print()

    # ============================================================
    # PHASE 2: Compute expected derivations (baseline)
    # ============================================================
    print("=" * 70)
    print("PHASE 2: EXPECTED DERIVATIONS (NULL MODEL)")
    print("=" * 70)
    print()

    print("Computing expected substring counts based on character probabilities...")
    print("(This establishes baseline: how often would random strings contain each repeater?)")
    print()

    singleton_list = list(singletons)

    for rep, stats in derivational_analysis.items():
        expected = expected_substring_count(rep, singleton_list, char_probs)
        observed = stats['total_seeds']

        if expected > 0:
            productivity_ratio = observed / expected
        else:
            productivity_ratio = float('inf') if observed > 0 else 1.0

        derivational_analysis[rep]['expected'] = round(expected, 2)
        derivational_analysis[rep]['productivity_ratio'] = round(productivity_ratio, 2)

    # Show productivity ratios
    print("Top repeaters by productivity ratio (observed/expected):")
    top_by_ratio = sorted(
        [(r, s) for r, s in derivational_analysis.items() if s['expected'] > 0.5],
        key=lambda x: -x[1]['productivity_ratio']
    )[:20]
    for rep, stats in top_by_ratio:
        print(f"  '{rep}': ratio={stats['productivity_ratio']:.2f}x "
              f"(obs={stats['total_seeds']}, exp={stats['expected']:.1f})")
    print()

    # ============================================================
    # PHASE 3: Correlation analysis
    # ============================================================
    print("=" * 70)
    print("PHASE 3: FREQUENCY vs PRODUCTIVITY CORRELATION")
    print("=" * 70)
    print()

    # Filter to repeaters with meaningful expected values
    valid_repeaters = [(r, s) for r, s in derivational_analysis.items() if s['expected'] > 0.1]

    if len(valid_repeaters) >= 10:
        frequencies = [s['frequency'] for _, s in valid_repeaters]
        productivities = [s['productivity_ratio'] for _, s in valid_repeaters]
        total_seeds = [s['total_seeds'] for _, s in valid_repeaters]

        rho_freq_prod, p_freq_prod = sp_stats.spearmanr(frequencies, productivities)
        rho_freq_seeds, p_freq_seeds = sp_stats.spearmanr(frequencies, total_seeds)

        print(f"Repeaters analyzed: {len(valid_repeaters)}")
        print()
        print(f"Frequency vs Productivity ratio:")
        print(f"  Spearman rho = {rho_freq_prod:.3f}, p = {p_freq_prod:.4f}")
        print()
        print(f"Frequency vs Total seeds:")
        print(f"  Spearman rho = {rho_freq_seeds:.3f}, p = {p_freq_seeds:.4f}")
        print()

        # Binned analysis
        print("Productivity by frequency bin:")
        freq_bins = [(1, 5), (6, 10), (11, 20), (21, 50), (51, 1000)]
        for low, high in freq_bins:
            bin_repeaters = [(r, s) for r, s in valid_repeaters
                             if low <= s['frequency'] <= high and s['expected'] > 0.1]
            if bin_repeaters:
                mean_prod = np.mean([s['productivity_ratio'] for _, s in bin_repeaters])
                mean_seeds = np.mean([s['total_seeds'] for _, s in bin_repeaters])
                print(f"  Freq {low}-{high}: n={len(bin_repeaters)}, mean ratio={mean_prod:.2f}x, mean seeds={mean_seeds:.1f}")
    else:
        print("Insufficient data for correlation analysis")
        rho_freq_prod = 0
        p_freq_prod = 1

    # ============================================================
    # PHASE 4: STRATIFICATION BY SECTION
    # ============================================================
    print()
    print("=" * 70)
    print("PHASE 4: STRATIFICATION BY SECTION")
    print("=" * 70)
    print()

    section_results = {}
    for section in ['H', 'P', 'T']:
        section_df = df_a[df_a['section'] == section]
        section_counts = section_df['middle'].value_counts()

        section_singletons = set(m for m, c in section_counts.items() if c == 1)
        section_repeaters = set(m for m, c in section_counts.items() if c > 1)

        if len(section_singletons) < 20 or len(section_repeaters) < 10:
            continue

        # Count total derivation relationships
        total_derivations = 0
        for rep in section_repeaters:
            if len(rep) < 2:
                continue
            for sing in section_singletons:
                if len(sing) > len(rep) and rep in sing:
                    total_derivations += 1

        pct = 100 * total_derivations / len(section_singletons) if section_singletons else 0
        section_results[section] = {
            'singletons': len(section_singletons),
            'repeaters': len(section_repeaters),
            'derivation_relationships': total_derivations,
            'derivation_pct': round(pct, 1)
        }

        print(f"Section {section}:")
        print(f"  Singletons: {len(section_singletons)}")
        print(f"  Repeaters: {len(section_repeaters)}")
        print(f"  Derivation relationships: {total_derivations}")
        print(f"  Singletons derived from repeaters: {pct:.1f}%")
        print()

    # ============================================================
    # SUMMARY
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    # Compute overall statistics
    all_ratios = [s['productivity_ratio'] for s in derivational_analysis.values() if s['expected'] > 0.1]
    mean_ratio = np.mean(all_ratios) if all_ratios else 0
    median_ratio = np.median(all_ratios) if all_ratios else 0
    above_1 = sum(1 for r in all_ratios if r > 1.0)
    above_2 = sum(1 for r in all_ratios if r > 2.0)

    print(f"Productivity ratio statistics (for repeaters with expected > 0.1):")
    print(f"  N = {len(all_ratios)}")
    print(f"  Mean ratio: {mean_ratio:.2f}x")
    print(f"  Median ratio: {median_ratio:.2f}x")
    print(f"  Above 1.0 (productive): {above_1} ({100*above_1/len(all_ratios):.1f}%)")
    print(f"  Above 2.0 (highly productive): {above_2} ({100*above_2/len(all_ratios):.1f}%)")
    print()

    # Pass criterion
    passed = mean_ratio > 1.5 and median_ratio > 1.0

    results = {
        'singletons_count': len(singletons),
        'repeaters_count': len(repeaters),
        'derivational_repeaters': len(derivational_analysis),
        'productivity_stats': {
            'n_analyzed': len(all_ratios),
            'mean_ratio': round(mean_ratio, 2),
            'median_ratio': round(median_ratio, 2),
            'above_1': above_1,
            'above_2': above_2
        },
        'correlation': {
            'freq_vs_productivity_rho': round(rho_freq_prod, 3) if 'rho_freq_prod' in dir() else None,
            'freq_vs_productivity_p': round(p_freq_prod, 4) if 'p_freq_prod' in dir() else None
        },
        'stratification': section_results,
        'pass_criteria': {
            'mean_threshold': 1.5,
            'median_threshold': 1.0,
            'observed_mean': round(mean_ratio, 2),
            'observed_median': round(median_ratio, 2),
            'passed': bool(passed)
        }
    }

    print(f"PASS CRITERIA (mean > 1.5 AND median > 1.0): {'PASS' if passed else 'FAIL'}")
    print()

    if passed:
        print("INTERPRETATION:")
        print("High-frequency MIDDLEs DO seed longer singletons productively.")
        print("The derivation rate exceeds random baseline expectations.")
        print()
        print("Potential constraint C511:")
        print("  'High-frequency MIDDLEs seed longer singletons productively;")
        print(f"   mean productivity ratio = {mean_ratio:.2f}x above chance baseline.'")
    else:
        print("INTERPRETATION:")
        print("Derivation patterns are close to or below chance expectations.")
        print("The 'seeding' relationship may be coincidental.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_DIR / 'derivational_analysis.json', 'w') as f:
        json.dump(derivational_analysis, f, indent=2)

    # Save CSV for frequency vs productivity
    csv_data = []
    for rep, stats in derivational_analysis.items():
        csv_data.append({
            'repeater': rep,
            'frequency': stats['frequency'],
            'length': stats['length'],
            'total_seeds': stats['total_seeds'],
            'expected': stats.get('expected', 0),
            'productivity_ratio': stats.get('productivity_ratio', 0)
        })
    pd.DataFrame(csv_data).to_csv(RESULTS_DIR / 'productivity_by_frequency.csv', index=False)

    with open(RESULTS_DIR / 'test2_summary.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_DIR}")


if __name__ == '__main__':
    main()
