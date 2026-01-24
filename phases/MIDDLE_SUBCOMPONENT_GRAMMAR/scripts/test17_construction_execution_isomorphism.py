#!/usr/bin/env python3
"""
Test 17: Construction-Execution Isomorphism

Tests whether character-level construction constraints within tokens are
isomorphic to class-level execution constraints between tokens.

Hypothesis: The same directional constraints govern both token construction
and program execution.

Method:
1. Build character-transition matrix from within-token sequences (construction)
2. Build class-transition matrix from between-token sequences (execution)
3. Map characters to their dominant class
4. Compare transition patterns - if isomorphic, correlation should be strong

Prediction: r > 0.7 if construction and execution constraints are unified
Null: r near 0 if constraints are independent
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'
CLASS_MAP_FILE = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

# Kernel primitives
KERNEL_PRIMITIVES = list('setdlohckr')


def load_class_map():
    """Load token-to-class mapping."""
    with open(CLASS_MAP_FILE, 'r') as f:
        data = json.load(f)
    return data.get('token_to_class', {})


def build_character_transition_matrix(tokens):
    """
    Build transition matrix from character sequences WITHIN tokens.
    This represents CONSTRUCTION constraints.
    """
    char_set = set()
    transitions = Counter()
    char_counts = Counter()

    for token in tokens:
        token = str(token).strip()
        if len(token) < 2:
            continue

        for char in token:
            char_set.add(char)
            char_counts[char] += 1

        for i in range(len(token) - 1):
            c1, c2 = token[i], token[i+1]
            transitions[(c1, c2)] += 1

    # Convert to matrix
    chars = sorted(char_set)
    n = len(chars)
    char_to_idx = {c: i for i, c in enumerate(chars)}

    matrix = np.zeros((n, n))
    for (c1, c2), count in transitions.items():
        if c1 in char_to_idx and c2 in char_to_idx:
            matrix[char_to_idx[c1], char_to_idx[c2]] = count

    # Normalize to transition probabilities
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    prob_matrix = matrix / row_sums

    return prob_matrix, chars, char_to_idx, transitions, char_counts


def build_class_transition_matrix(df, token_to_class):
    """
    Build transition matrix from class sequences BETWEEN tokens.
    This represents EXECUTION constraints.
    """
    class_set = set()
    transitions = Counter()
    class_counts = Counter()

    # Group by line to get sequences
    for (folio, line), group in df.groupby(['folio', 'line_number'], sort=False):
        tokens = group['word'].tolist()
        classes = [token_to_class.get(str(t).strip()) for t in tokens]
        classes = [c for c in classes if c is not None]

        for c in classes:
            class_set.add(c)
            class_counts[c] += 1

        for i in range(len(classes) - 1):
            transitions[(classes[i], classes[i+1])] += 1

    # Convert to matrix
    class_list = sorted(class_set)
    n = len(class_list)
    class_to_idx = {c: i for i, c in enumerate(class_list)}

    matrix = np.zeros((n, n))
    for (c1, c2), count in transitions.items():
        if c1 in class_to_idx and c2 in class_to_idx:
            matrix[class_to_idx[c1], class_to_idx[c2]] = count

    # Normalize to transition probabilities
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    prob_matrix = matrix / row_sums

    return prob_matrix, class_list, class_to_idx, transitions, class_counts


def compute_observed_expected_ratio(transitions, counts, total):
    """Compute observed/expected ratio for each transition."""
    ratios = {}
    total_count = sum(counts.values())

    for (a, b), obs in transitions.items():
        if counts[a] > 0 and counts[b] > 0:
            expected = (counts[a] / total_count) * (counts[b] / total_count) * total
            if expected > 0:
                ratios[(a, b)] = obs / expected

    return ratios


def map_chars_to_classes(token_to_class):
    """
    For single-character tokens, get their class assignment.
    For characters that aren't standalone tokens, use most common class
    of tokens starting with that character.
    """
    char_to_class = {}

    # Direct mapping for single-char tokens
    for token, cls in token_to_class.items():
        if len(token) == 1:
            char_to_class[token] = cls

    # For characters without direct mapping, use most common class of tokens starting with that char
    char_class_counts = defaultdict(Counter)
    for token, cls in token_to_class.items():
        if len(token) > 0:
            char_class_counts[token[0]][cls] += 1

    for char, class_counts in char_class_counts.items():
        if char not in char_to_class and class_counts:
            char_to_class[char] = class_counts.most_common(1)[0][0]

    return char_to_class


if __name__ == '__main__':
    print("=" * 70)
    print("TEST 17: CONSTRUCTION-EXECUTION ISOMORPHISM")
    print("=" * 70)

    # Load data
    token_to_class = load_class_map()
    print(f"\nLoaded class mapping: {len(token_to_class)} tokens → {len(set(token_to_class.values()))} classes")

    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]
    df_b = df[df['language'] == 'B'].copy()

    print(f"B tokens: {len(df_b)}")

    # Build construction matrix (within-token character transitions)
    print("\n=== CONSTRUCTION CONSTRAINTS (within-token) ===\n")

    tokens = df_b['word'].dropna().tolist()
    const_matrix, chars, char_to_idx, char_trans, char_counts = build_character_transition_matrix(tokens)

    total_char_trans = sum(char_trans.values())
    print(f"Characters: {len(chars)}")
    print(f"Total character transitions: {total_char_trans}")

    # Compute construction ratios for kernel primitives
    const_ratios = compute_observed_expected_ratio(char_trans, char_counts, total_char_trans)

    print("\nKernel primitive construction ratios (within-token):")
    kernel_pairs = [('h', 'k'), ('k', 'h'), ('e', 'k'), ('k', 'e'), ('h', 'e'), ('e', 'h')]
    for pair in kernel_pairs:
        ratio = const_ratios.get(pair, 0)
        status = "SUPPRESSED" if ratio < 0.5 else "ELEVATED" if ratio > 2 else "NORMAL"
        print(f"  {pair[0]}→{pair[1]}: {ratio:.3f} ({status})")

    # Build execution matrix (between-token class transitions)
    print("\n=== EXECUTION CONSTRAINTS (between-token) ===\n")

    exec_matrix, classes, class_to_idx, class_trans, class_counts = build_class_transition_matrix(df_b, token_to_class)

    total_class_trans = sum(class_trans.values())
    print(f"Classes: {len(classes)}")
    print(f"Total class transitions: {total_class_trans}")

    # Compute execution ratios
    exec_ratios = compute_observed_expected_ratio(class_trans, class_counts, total_class_trans)

    # Map characters to classes for comparison
    char_to_class = map_chars_to_classes(token_to_class)

    print("\nKernel primitive class assignments:")
    for char in KERNEL_PRIMITIVES:
        cls = char_to_class.get(char, 'N/A')
        print(f"  '{char}' → Class {cls}")

    # Compare construction vs execution ratios for mapped pairs
    print("\n=== ISOMORPHISM TEST ===\n")

    # For each character pair, get construction ratio
    # Map to class pair, get execution ratio
    # Compare

    construction_values = []
    execution_values = []
    pair_labels = []

    # Use all character pairs with sufficient data
    for (c1, c2), const_ratio in const_ratios.items():
        if char_trans[(c1, c2)] < 10:  # Minimum count
            continue

        cls1 = char_to_class.get(c1)
        cls2 = char_to_class.get(c2)

        if cls1 is None or cls2 is None:
            continue

        exec_ratio = exec_ratios.get((cls1, cls2))
        if exec_ratio is None:
            continue

        construction_values.append(const_ratio)
        execution_values.append(exec_ratio)
        pair_labels.append(f"{c1}→{c2}")

    print(f"Pairs with sufficient data: {len(construction_values)}")

    if len(construction_values) >= 10:
        # Compute correlation
        r, p = stats.pearsonr(construction_values, execution_values)
        rho, rho_p = stats.spearmanr(construction_values, execution_values)

        print(f"\nCorrelation (Pearson): r = {r:.4f}, p = {p:.6f}")
        print(f"Correlation (Spearman): rho = {rho:.4f}, p = {rho_p:.6f}")

        # Show extreme pairs
        print("\n=== EXTREME PAIRS (most suppressed in construction) ===")
        sorted_pairs = sorted(zip(construction_values, execution_values, pair_labels), key=lambda x: x[0])

        print(f"{'Pair':<10} {'Construction':<15} {'Execution':<15} {'Match?'}")
        print("-" * 50)
        for const, exec_val, label in sorted_pairs[:10]:
            match = "YES" if (const < 0.5 and exec_val < 1.5) or (const > 2 and exec_val > 0.7) else "NO"
            print(f"{label:<10} {const:<15.3f} {exec_val:<15.3f} {match}")

        print("\n=== EXTREME PAIRS (most elevated in construction) ===")
        print(f"{'Pair':<10} {'Construction':<15} {'Execution':<15} {'Match?'}")
        print("-" * 50)
        for const, exec_val, label in sorted_pairs[-10:]:
            match = "YES" if (const < 0.5 and exec_val < 1.5) or (const > 2 and exec_val > 0.7) else "NO"
            print(f"{label:<10} {const:<15.3f} {exec_val:<15.3f} {match}")

        # Focus on kernel primitives specifically
        print("\n=== KERNEL PRIMITIVE COMPARISON ===")
        print(f"{'Pair':<10} {'Construction':<15} {'Execution':<15} {'Const Status':<15} {'Exec Status'}")
        print("-" * 70)

        for pair in kernel_pairs:
            c1, c2 = pair
            const_ratio = const_ratios.get(pair, 0)

            cls1 = char_to_class.get(c1)
            cls2 = char_to_class.get(c2)
            exec_ratio = exec_ratios.get((cls1, cls2), 0) if cls1 and cls2 else 0

            const_status = "SUPPRESSED" if const_ratio < 0.5 else "ELEVATED" if const_ratio > 2 else "NORMAL"
            exec_status = "SUPPRESSED" if exec_ratio < 0.5 else "ELEVATED" if exec_ratio > 2 else "NORMAL"

            print(f"{c1}→{c2:<7} {const_ratio:<15.3f} {exec_ratio:<15.3f} {const_status:<15} {exec_status}")

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        print(f"\nPearson correlation: r = {r:.4f} (p = {p:.6f})")
        print(f"Spearman correlation: rho = {rho:.4f} (p = {rho_p:.6f})")

        # Count directional matches
        matches = 0
        for const, exec_val, _ in zip(construction_values, execution_values, pair_labels):
            # Both suppressed, both normal, or both elevated
            const_cat = "S" if const < 0.5 else "E" if const > 2 else "N"
            exec_cat = "S" if exec_val < 0.5 else "E" if exec_val > 2 else "N"
            if const_cat == exec_cat:
                matches += 1

        match_rate = matches / len(construction_values)
        print(f"Category match rate: {match_rate:.1%} ({matches}/{len(construction_values)})")

        # Verdict
        if r > 0.7 and p < 0.001:
            verdict = "STRONG ISOMORPHISM"
            tier = "Tier 2"
            explanation = "Construction and execution constraints are strongly correlated"
        elif r > 0.4 and p < 0.01:
            verdict = "MODERATE ISOMORPHISM"
            tier = "Tier 3"
            explanation = "Partial alignment between construction and execution constraints"
        elif r > 0.2 and p < 0.05:
            verdict = "WEAK ISOMORPHISM"
            tier = "Tier 4"
            explanation = "Some alignment, but not strong enough for structural claim"
        else:
            verdict = "NO ISOMORPHISM"
            tier = "Falsified"
            explanation = "Construction and execution constraints appear independent"

        print(f"\nVERDICT: {verdict}")
        print(f"TIER ASSESSMENT: {tier}")
        print(f"EXPLANATION: {explanation}")

        # Additional analysis: Are suppressed pairs in construction also rare in execution?
        print("\n=== SUPPRESSION COHERENCE TEST ===")

        const_suppressed = [(c, e, l) for c, e, l in zip(construction_values, execution_values, pair_labels) if c < 0.5]
        if const_suppressed:
            exec_of_suppressed = [e for c, e, l in const_suppressed]
            print(f"Pairs suppressed in construction (ratio < 0.5): {len(const_suppressed)}")
            print(f"Mean execution ratio for these pairs: {np.mean(exec_of_suppressed):.3f}")
            print(f"% also suppressed in execution: {100*sum(1 for e in exec_of_suppressed if e < 0.5)/len(exec_of_suppressed):.1f}%")

        const_elevated = [(c, e, l) for c, e, l in zip(construction_values, execution_values, pair_labels) if c > 2]
        if const_elevated:
            exec_of_elevated = [e for c, e, l in const_elevated]
            print(f"\nPairs elevated in construction (ratio > 2): {len(const_elevated)}")
            print(f"Mean execution ratio for these pairs: {np.mean(exec_of_elevated):.3f}")
            print(f"% also elevated in execution: {100*sum(1 for e in exec_of_elevated if e > 2)/len(exec_of_elevated):.1f}%")

        # Save results
        results = {
            'pearson_r': float(r),
            'pearson_p': float(p),
            'spearman_rho': float(rho),
            'spearman_p': float(rho_p),
            'n_pairs': len(construction_values),
            'category_match_rate': float(match_rate),
            'verdict': verdict,
            'tier': tier,
            'kernel_comparisons': {
                f"{c1}→{c2}": {
                    'construction': float(const_ratios.get((c1, c2), 0)),
                    'execution': float(exec_ratios.get((char_to_class.get(c1), char_to_class.get(c2)), 0))
                                 if char_to_class.get(c1) and char_to_class.get(c2) else None
                }
                for c1, c2 in kernel_pairs
            }
        }

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_DIR / 'construction_execution_isomorphism.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {RESULTS_DIR / 'construction_execution_isomorphism.json'}")

    else:
        print("Insufficient paired data for correlation analysis")
