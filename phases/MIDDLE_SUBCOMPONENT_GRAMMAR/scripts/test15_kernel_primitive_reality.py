#!/usr/bin/env python3
"""
Test 15: Kernel Primitive Reality Check

Hypotheses:
H0 (Artifacts): Kernel primitives appear important because they're compression hinges.
H1 (Real): Kernel primitives are fundamental operators with distinct behavioral roles.

Tests:
A - Frequency Deflation: Do kernel primitives still dominate after removing compression inflation?
B - Transition Specificity: Are forbidden transitions explainable by frequency alone?
C - Role Substitution: Can kernel primitives substitute for each other?
D - Hinge Exclusivity: Are kernel primitives special as hinges?
E - Non-Compressed Contexts: Do primitives show distinct behavior without compression?
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import random

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Kernel primitives from C085
KERNEL_PRIMITIVES = set('setdlohckr')
CORE_KERNEL = set('khe')  # C089: core within core

# Known forbidden transitions from C109 (subset - the specific pairs)
# These are transitions that should NOT occur in valid B execution
FORBIDDEN_PAIRS = [
    ('h', 'k'),  # PHASE_ORDERING class
    ('k', 'h'),
    ('e', 'k'),
    ('s', 'h'),
    ('d', 'k'),
    ('t', 'h'),
    ('l', 'k'),
    ('c', 'h'),
    ('o', 'k'),
    ('r', 'h'),
]

# Morphology extraction
PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lsh',
            'ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'lk', 'yk',
            'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po',
            'sa', 'ka', 'ta', 'al', 'ar', 'or', 'o', 'd', 's', 'y', 'l', 'r', 'q', 'k', 't', 'p', 'f']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token).strip()
    if not token:
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


def get_pp_vocabulary(df_a, df_b):
    """Get PP (shared) vocabulary."""
    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    return a_middles & b_middles


def find_overlaps_in_token(token, vocab):
    """Find overlapping sub-components and return coverage map."""
    vocab_list = sorted([v for v in vocab if len(v) > 1 and v in token], key=len, reverse=True)
    coverage = [[] for _ in range(len(token))]  # List of sub-components covering each position

    for v in vocab_list:
        start = 0
        while True:
            pos = token.find(v, start)
            if pos == -1:
                break
            for i in range(pos, pos + len(v)):
                if i < len(token):
                    coverage[i].append(v)
            start = pos + 1

    return coverage


def test_a_frequency_deflation(df_b, pp_vocab):
    """Test A: Do kernel primitives still dominate after deflation?"""
    print("\n=== TEST A: Frequency Deflation ===\n")

    # Raw character frequency (with compression inflation)
    raw_counts = Counter()
    for token in df_b['word'].dropna():
        for char in str(token):
            raw_counts[char] += 1

    # Deflated frequency (count each position once)
    deflated_counts = Counter()
    for token in df_b['word'].dropna():
        token = str(token)
        # Just count each character once per position
        for char in token:
            deflated_counts[char] += 1

    # Actually, raw and deflated are the same if we're just counting characters
    # The inflation comes from sub-component counting, not character counting
    # Let me reframe: compare character frequency to sub-component participation

    # Sub-component participation (how often char appears in ANY sub-component match)
    subcomp_counts = Counter()
    for token in df_b['word'].dropna():
        token = str(token)
        middle = extract_middle(token)
        if not middle:
            continue
        coverage = find_overlaps_in_token(middle, pp_vocab)
        for i, char in enumerate(middle):
            if coverage[i]:  # This position is covered by sub-components
                subcomp_counts[char] += len(coverage[i])  # Count per sub-component

    # Compare rankings
    raw_top10 = [c for c, _ in raw_counts.most_common(10)]
    deflated_top10 = [c for c, _ in deflated_counts.most_common(10)]
    subcomp_top10 = [c for c, _ in subcomp_counts.most_common(10)]

    print("Raw character frequency (top 10):")
    for i, (char, count) in enumerate(raw_counts.most_common(10)):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  {i+1}. '{char}'{kernel_mark}: {count}")

    print("\nSub-component participation (top 10):")
    for i, (char, count) in enumerate(subcomp_counts.most_common(10)):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  {i+1}. '{char}'{kernel_mark}: {count}")

    # Check if kernel primitives dominate both
    raw_kernel_in_top10 = sum(1 for c in raw_top10 if c in KERNEL_PRIMITIVES)
    subcomp_kernel_in_top10 = sum(1 for c in subcomp_top10 if c in KERNEL_PRIMITIVES)

    print(f"\nKernel primitives in raw top-10: {raw_kernel_in_top10}/10")
    print(f"Kernel primitives in subcomp top-10: {subcomp_kernel_in_top10}/10")

    # Inflation ratio: how much does sub-component counting inflate kernel primitive counts?
    inflation_ratios = {}
    for char in KERNEL_PRIMITIVES:
        if raw_counts[char] > 0 and subcomp_counts[char] > 0:
            inflation_ratios[char] = subcomp_counts[char] / raw_counts[char]

    non_kernel_inflation = []
    for char in raw_counts:
        if char not in KERNEL_PRIMITIVES and raw_counts[char] > 100:
            if subcomp_counts[char] > 0:
                non_kernel_inflation.append(subcomp_counts[char] / raw_counts[char])

    print(f"\nInflation ratios (subcomp/raw):")
    print(f"  Kernel primitives: {np.mean(list(inflation_ratios.values())):.2f}x mean")
    print(f"  Non-kernel chars: {np.mean(non_kernel_inflation):.2f}x mean")

    # Verdict
    if raw_kernel_in_top10 >= 7:
        verdict = "PASS (H1)"
        reason = "Kernel primitives dominate raw frequency, not just sub-component inflation"
    else:
        verdict = "FAIL (H0)"
        reason = "Kernel primitive dominance may be inflation artifact"

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {reason}")

    return {
        'verdict': verdict,
        'raw_kernel_in_top10': raw_kernel_in_top10,
        'subcomp_kernel_in_top10': subcomp_kernel_in_top10,
        'kernel_inflation_mean': float(np.mean(list(inflation_ratios.values()))) if inflation_ratios else 0,
        'non_kernel_inflation_mean': float(np.mean(non_kernel_inflation)) if non_kernel_inflation else 0
    }


def test_b_transition_specificity(df_b):
    """Test B: Are forbidden transitions explainable by frequency alone?"""
    print("\n=== TEST B: Transition Specificity ===\n")

    # Count all bigram transitions in B
    bigram_counts = Counter()
    char_counts = Counter()

    for token in df_b['word'].dropna():
        token = str(token)
        for char in token:
            char_counts[char] += 1
        for i in range(len(token) - 1):
            bigram_counts[(token[i], token[i+1])] += 1

    total_bigrams = sum(bigram_counts.values())
    total_chars = sum(char_counts.values())

    # Expected frequency of each bigram under independence
    expected_freq = {}
    for (c1, c2), count in bigram_counts.items():
        p1 = char_counts[c1] / total_chars
        p2 = char_counts[c2] / total_chars
        expected_freq[(c1, c2)] = p1 * p2 * total_bigrams

    # Check forbidden pairs
    print("Forbidden transition analysis:")
    print(f"{'Pair':<10} {'Observed':<12} {'Expected':<12} {'Ratio':<10} {'Status'}")
    print("-" * 55)

    forbidden_ratios = []
    for pair in FORBIDDEN_PAIRS:
        observed = bigram_counts.get(pair, 0)
        expected = expected_freq.get(pair, 0)
        ratio = observed / expected if expected > 0 else 0
        forbidden_ratios.append(ratio)
        status = "SUPPRESSED" if ratio < 0.5 else "NORMAL"
        print(f"{pair[0]}→{pair[1]:<7} {observed:<12} {expected:<12.1f} {ratio:<10.2f} {status}")

    # Compare to random pairs
    all_pairs = list(bigram_counts.keys())
    random_ratios = []
    for pair in random.sample(all_pairs, min(100, len(all_pairs))):
        observed = bigram_counts[pair]
        expected = expected_freq.get(pair, 0)
        if expected > 0:
            random_ratios.append(observed / expected)

    print(f"\nMean ratio for forbidden pairs: {np.mean(forbidden_ratios):.3f}")
    print(f"Mean ratio for random pairs: {np.mean(random_ratios):.3f}")

    # Permutation test
    n_permutations = 1000
    observed_mean_ratio = np.mean(forbidden_ratios)
    more_extreme = 0

    all_ratios = []
    for pair in bigram_counts:
        expected = expected_freq.get(pair, 0)
        if expected > 0:
            all_ratios.append(bigram_counts[pair] / expected)

    for _ in range(n_permutations):
        sample = random.sample(all_ratios, len(FORBIDDEN_PAIRS))
        if np.mean(sample) <= observed_mean_ratio:
            more_extreme += 1

    p_value = more_extreme / n_permutations

    print(f"\nPermutation test p-value: {p_value:.4f}")

    # Verdict
    if p_value < 0.01:
        verdict = "PASS (H1)"
        reason = "Forbidden transitions are MORE suppressed than frequency predicts"
    else:
        verdict = "FAIL (H0)"
        reason = "Forbidden transitions consistent with frequency-based sampling"

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {reason}")

    return {
        'verdict': verdict,
        'forbidden_mean_ratio': float(np.mean(forbidden_ratios)),
        'random_mean_ratio': float(np.mean(random_ratios)),
        'p_value': p_value
    }


def test_c_role_substitution(df_b):
    """Test C: Can kernel primitives substitute for each other?"""
    print("\n=== TEST C: Role Substitution ===\n")

    # Count forbidden transition violations in original corpus
    def count_violations(tokens):
        violations = 0
        for token in tokens:
            token = str(token)
            for i in range(len(token) - 1):
                if (token[i], token[i+1]) in FORBIDDEN_PAIRS:
                    violations += 1
        return violations

    original_tokens = list(df_b['word'].dropna())
    original_violations = count_violations(original_tokens)

    print(f"Original corpus violations: {original_violations}")

    # Test substitutions
    substitution_tests = [
        ('k', 'h'),  # Replace k with h
        ('h', 'k'),  # Replace h with k
        ('e', 'k'),  # Replace e with k
        ('k', 'e'),  # Replace k with e
    ]

    results = []
    for old, new in substitution_tests:
        substituted = [str(t).replace(old, new) for t in original_tokens]
        new_violations = count_violations(substituted)
        change = new_violations - original_violations
        results.append({
            'substitution': f'{old}→{new}',
            'new_violations': new_violations,
            'change': change
        })
        print(f"  {old}→{new}: {new_violations} violations (change: {change:+d})")

    # Also check if substitution changes token distribution
    print("\nToken identity changes:")
    for old, new in substitution_tests[:2]:
        substituted = [str(t).replace(old, new) for t in original_tokens]
        original_unique = len(set(original_tokens))
        substituted_unique = len(set(substituted))
        overlap = len(set(original_tokens) & set(substituted))
        print(f"  {old}→{new}: {original_unique} → {substituted_unique} unique tokens, {overlap} unchanged")

    # Verdict
    avg_change = np.mean([r['change'] for r in results])
    if avg_change > 100:
        verdict = "PASS (H1)"
        reason = f"Substitution breaks grammar (avg {avg_change:+.0f} new violations)"
    elif avg_change < -100:
        verdict = "UNCLEAR"
        reason = f"Substitution reduces violations - unexpected"
    else:
        verdict = "FAIL (H0)"
        reason = f"Grammar tolerates substitution (avg {avg_change:+.0f} violations)"

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {reason}")

    return {
        'verdict': verdict,
        'original_violations': original_violations,
        'substitution_results': results,
        'avg_change': float(avg_change)
    }


def test_d_hinge_exclusivity(df_a, pp_vocab):
    """Test D: Are kernel primitives special as hinges?"""
    print("\n=== TEST D: Hinge Exclusivity ===\n")

    # Count hinge occurrences for each character
    hinge_counts = Counter()
    total_positions = Counter()

    for _, row in df_a.iterrows():
        middle = row.get('middle')
        if pd.isna(middle) or not middle:
            continue
        middle = str(middle)

        coverage = find_overlaps_in_token(middle, pp_vocab)

        for i, char in enumerate(middle):
            total_positions[char] += 1
            if len(coverage[i]) > 1:  # Position covered by multiple sub-components = hinge
                hinge_counts[char] += 1

    # Calculate hinge rate for each character
    hinge_rates = {}
    for char in total_positions:
        if total_positions[char] >= 100:  # Minimum sample
            hinge_rates[char] = hinge_counts[char] / total_positions[char]

    # Compare kernel vs non-kernel
    kernel_rates = [hinge_rates[c] for c in KERNEL_PRIMITIVES if c in hinge_rates]
    non_kernel_rates = [r for c, r in hinge_rates.items() if c not in KERNEL_PRIMITIVES]

    print("Hinge rates by character type:")
    print(f"  Kernel primitives: {np.mean(kernel_rates):.1%} (n={len(kernel_rates)})")
    print(f"  Non-kernel chars: {np.mean(non_kernel_rates):.1%} (n={len(non_kernel_rates)})")

    print("\nTop 10 hinge characters:")
    sorted_rates = sorted(hinge_rates.items(), key=lambda x: x[1], reverse=True)
    for i, (char, rate) in enumerate(sorted_rates[:10]):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  {i+1}. '{char}'{kernel_mark}: {rate:.1%}")

    # Statistical test
    if kernel_rates and non_kernel_rates:
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(kernel_rates, non_kernel_rates)
        print(f"\nt-test: t={t_stat:.2f}, p={p_value:.4f}")
    else:
        p_value = 1.0

    # Verdict
    kernel_mean = np.mean(kernel_rates) if kernel_rates else 0
    non_kernel_mean = np.mean(non_kernel_rates) if non_kernel_rates else 0

    if abs(kernel_mean - non_kernel_mean) < 0.1:
        verdict = "PASS (H1)"
        reason = "Kernel primitives are hinges at similar rate to others - not just hinge status"
    else:
        verdict = "PASS (H0)" if kernel_mean > non_kernel_mean else "UNCLEAR"
        reason = f"Kernel primitives are {kernel_mean/non_kernel_mean:.1f}x more likely to be hinges"

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {reason}")

    return {
        'verdict': verdict,
        'kernel_hinge_rate': float(kernel_mean),
        'non_kernel_hinge_rate': float(non_kernel_mean),
        'p_value': float(p_value) if p_value else 1.0
    }


def test_e_non_compressed_contexts(df_b):
    """Test E: Do primitives show distinct behavior without compression?"""
    print("\n=== TEST E: Non-Compressed Contexts ===\n")

    # Find single-character tokens and first/last positions
    # These are positions where overlap can't inflate counts

    # Single-char tokens
    single_char_tokens = []
    for token in df_b['word'].dropna():
        if len(str(token)) == 1:
            single_char_tokens.append(str(token))

    single_char_counts = Counter(single_char_tokens)
    print(f"Single-character tokens: {len(single_char_tokens)}")
    for char, count in single_char_counts.most_common(10):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  '{char}'{kernel_mark}: {count}")

    # First and last character distributions
    first_chars = Counter()
    last_chars = Counter()
    for token in df_b['word'].dropna():
        token = str(token)
        if token:
            first_chars[token[0]] += 1
            last_chars[token[-1]] += 1

    print("\nFirst character distribution (top 10):")
    for char, count in first_chars.most_common(10):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  '{char}'{kernel_mark}: {count}")

    print("\nLast character distribution (top 10):")
    for char, count in last_chars.most_common(10):
        kernel_mark = "*" if char in KERNEL_PRIMITIVES else " "
        print(f"  '{char}'{kernel_mark}: {count}")

    # Check if k, h, e show different positional preferences (role differentiation)
    core_positions = {}
    for char in CORE_KERNEL:
        first_rate = first_chars[char] / sum(first_chars.values())
        last_rate = last_chars[char] / sum(last_chars.values())
        core_positions[char] = {
            'first_rate': first_rate,
            'last_rate': last_rate,
            'ratio': first_rate / last_rate if last_rate > 0 else float('inf')
        }

    print("\nCore kernel (k, h, e) positional differentiation:")
    for char, pos in core_positions.items():
        print(f"  '{char}': first={pos['first_rate']:.1%}, last={pos['last_rate']:.1%}, ratio={pos['ratio']:.2f}")

    # Check if they have different ratios (role differentiation)
    ratios = [pos['ratio'] for pos in core_positions.values()]
    ratio_variance = np.var(ratios)

    print(f"\nCore kernel ratio variance: {ratio_variance:.4f}")

    # Verdict
    if ratio_variance > 0.5:
        verdict = "PASS (H1)"
        reason = "k, h, e show distinct positional preferences even in non-compressed positions"
    else:
        verdict = "FAIL (H0)"
        reason = "k, h, e show similar positional behavior"

    print(f"\nVerdict: {verdict}")
    print(f"Reason: {reason}")

    return {
        'verdict': verdict,
        'single_char_count': len(single_char_tokens),
        'core_positions': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in core_positions.items()},
        'ratio_variance': float(ratio_variance)
    }


if __name__ == '__main__':
    print("=" * 60)
    print("TEST 15: KERNEL PRIMITIVE REALITY CHECK")
    print("=" * 60)

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    # Split populations
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()

    # Extract MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_b['middle'] = df_b['word'].apply(extract_middle)

    # Get PP vocabulary
    pp_vocab = get_pp_vocabulary(df_a, df_b)
    pp_vocab = set(p for p in pp_vocab if len(p) > 1)

    print(f"\nData loaded: {len(df_a)} A tokens, {len(df_b)} B tokens")
    print(f"PP vocabulary: {len(pp_vocab)} items")

    # Run all tests
    results = {}

    results['test_a'] = test_a_frequency_deflation(df_b, pp_vocab)
    results['test_b'] = test_b_transition_specificity(df_b)
    results['test_c'] = test_c_role_substitution(df_b)
    results['test_d'] = test_d_hinge_exclusivity(df_a, pp_vocab)
    results['test_e'] = test_e_non_compressed_contexts(df_b)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = {
        'A': results['test_a']['verdict'],
        'B': results['test_b']['verdict'],
        'C': results['test_c']['verdict'],
        'D': results['test_d']['verdict'],
        'E': results['test_e']['verdict'],
    }

    print(f"\n{'Test':<10} {'Verdict':<20} {'Supports'}")
    print("-" * 45)
    for test, verdict in verdicts.items():
        supports = "H1 (Real)" if "H1" in verdict else ("H0 (Artifact)" if "H0" in verdict else "Unclear")
        print(f"{test:<10} {verdict:<20} {supports}")

    h1_count = sum(1 for v in verdicts.values() if "H1" in v)
    h0_count = sum(1 for v in verdicts.values() if "H0" in v)

    print(f"\nH1 (Real) wins: {h1_count}/5")
    print(f"H0 (Artifact) wins: {h0_count}/5")

    if h1_count >= 4:
        final_verdict = "KERNEL PRIMITIVES ARE REAL"
        explanation = "Multiple independent tests confirm primitives have structural roles beyond compression"
    elif h0_count >= 4:
        final_verdict = "KERNEL PRIMITIVES MAY BE ARTIFACTS"
        explanation = "Evidence suggests primitive importance is compression-derived"
    else:
        final_verdict = "MIXED EVIDENCE"
        explanation = "Some tests support real roles, others consistent with artifacts"

    print(f"\n{'=' * 60}")
    print(f"FINAL VERDICT: {final_verdict}")
    print(f"{'=' * 60}")
    print(f"\n{explanation}")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'kernel_primitive_reality.json', 'w') as f:
        json.dump({
            'tests': results,
            'verdicts': verdicts,
            'h1_count': h1_count,
            'h0_count': h0_count,
            'final_verdict': final_verdict
        }, f, indent=2)

    print(f"\nResults saved to {RESULTS_DIR / 'kernel_primitive_reality.json'}")
