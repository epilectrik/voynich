#!/usr/bin/env python3
"""
A-Internal Stratification: Incompatibility Test

Question: Are A-exclusive MIDDLEs systematically incompatible with A/B-shared MIDDLEs
under the C475 incompatibility lattice?

If yes: Zero-mixing is explained by the existing incompatibility structure
If no: Zero-mixing requires a new explanation (functional stratification)
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np
from scipy import stats

RESULTS_DIR = Path(__file__).parent.parent / 'results'
MIDDLE_CLASSES_PATH = RESULTS_DIR / 'middle_classes.json'
TOKEN_DATA_PATH = RESULTS_DIR / 'token_data.json'
ENTRY_DATA_PATH = RESULTS_DIR / 'entry_data.json'


def load_data():
    """Load prepared data files."""
    with open(MIDDLE_CLASSES_PATH) as f:
        middle_classes = json.load(f)
    with open(TOKEN_DATA_PATH) as f:
        tokens = json.load(f)
    with open(ENTRY_DATA_PATH) as f:
        entries = json.load(f)
    return middle_classes, tokens, entries


def build_cooccurrence_matrix(entries):
    """
    Build MIDDLE co-occurrence matrix from entries.

    Two MIDDLEs "co-occur" if they appear in the same entry.
    This defines compatibility: if two MIDDLEs never co-occur, they may be incompatible.
    """
    # Get all MIDDLEs
    all_middles = set()
    for entry in entries:
        for token in entry['tokens']:
            all_middles.add(token['middle'])

    middle_list = sorted(all_middles)
    middle_to_idx = {m: i for i, m in enumerate(middle_list)}
    n = len(middle_list)

    # Build co-occurrence counts
    cooccur = np.zeros((n, n), dtype=int)

    for entry in entries:
        entry_middles = list(set(token['middle'] for token in entry['tokens']))
        for i, m1 in enumerate(entry_middles):
            for m2 in entry_middles[i:]:
                idx1, idx2 = middle_to_idx[m1], middle_to_idx[m2]
                cooccur[idx1, idx2] += 1
                if idx1 != idx2:
                    cooccur[idx2, idx1] += 1

    return cooccur, middle_list, middle_to_idx


def main():
    print("=" * 70)
    print("INCOMPATIBILITY TEST")
    print("=" * 70)
    print()
    print("Question: Are A-exclusive MIDDLEs systematically incompatible with")
    print("A/B-shared MIDDLEs, explaining the zero-mixing finding?")
    print()

    # Load data
    print("Loading data...")
    middle_classes, tokens, entries = load_data()

    a_exclusive = set(middle_classes['a_exclusive_middles'])
    a_shared = set(middle_classes['a_shared_middles'])

    print(f"  A-exclusive MIDDLEs: {len(a_exclusive)}")
    print(f"  A/B-shared MIDDLEs: {len(a_shared)}")
    print()

    # Build co-occurrence matrix
    print("Building co-occurrence matrix...")
    cooccur, middle_list, middle_to_idx = build_cooccurrence_matrix(entries)

    # Analyze co-occurrence patterns
    print()
    print("=" * 70)
    print("CO-OCCURRENCE ANALYSIS")
    print("=" * 70)

    # 1. Within-class co-occurrence (exclusive-exclusive, shared-shared)
    # 2. Cross-class co-occurrence (exclusive-shared)

    excl_excl_pairs = 0
    excl_excl_cooccur = 0
    shared_shared_pairs = 0
    shared_shared_cooccur = 0
    cross_pairs = 0
    cross_cooccur = 0

    excl_indices = [middle_to_idx[m] for m in a_exclusive if m in middle_to_idx]
    shared_indices = [middle_to_idx[m] for m in a_shared if m in middle_to_idx]

    # Exclusive-Exclusive pairs
    for i, idx1 in enumerate(excl_indices):
        for idx2 in excl_indices[i+1:]:
            excl_excl_pairs += 1
            if cooccur[idx1, idx2] > 0:
                excl_excl_cooccur += 1

    # Shared-Shared pairs
    for i, idx1 in enumerate(shared_indices):
        for idx2 in shared_indices[i+1:]:
            shared_shared_pairs += 1
            if cooccur[idx1, idx2] > 0:
                shared_shared_cooccur += 1

    # Cross-class pairs (exclusive-shared)
    for idx1 in excl_indices:
        for idx2 in shared_indices:
            cross_pairs += 1
            if cooccur[idx1, idx2] > 0:
                cross_cooccur += 1

    print()
    print("Pair co-occurrence rates:")
    print()

    excl_excl_rate = excl_excl_cooccur / excl_excl_pairs if excl_excl_pairs > 0 else 0
    shared_shared_rate = shared_shared_cooccur / shared_shared_pairs if shared_shared_pairs > 0 else 0
    cross_rate = cross_cooccur / cross_pairs if cross_pairs > 0 else 0

    print(f"  Exclusive-Exclusive: {excl_excl_cooccur:,} / {excl_excl_pairs:,} pairs co-occur ({100*excl_excl_rate:.2f}%)")
    print(f"  Shared-Shared:       {shared_shared_cooccur:,} / {shared_shared_pairs:,} pairs co-occur ({100*shared_shared_rate:.2f}%)")
    print(f"  Cross-class:         {cross_cooccur:,} / {cross_pairs:,} pairs co-occur ({100*cross_rate:.2f}%)")

    # Key question: Is cross-class co-occurrence rate LOWER than expected?
    print()
    print("=" * 70)
    print("STATISTICAL TEST: Is cross-class incompatibility elevated?")
    print("=" * 70)

    # Compare cross-class rate to within-class rates
    # If cross-class << within-class, incompatibility explains zero mixing

    # Baseline: average of within-class rates
    baseline_rate = (excl_excl_rate + shared_shared_rate) / 2

    print(f"\n  Within-class average compatibility: {100*baseline_rate:.2f}%")
    print(f"  Cross-class compatibility:          {100*cross_rate:.2f}%")
    print(f"  Ratio (cross / baseline):           {cross_rate/baseline_rate:.3f}" if baseline_rate > 0 else "  Ratio: undefined")

    # Fisher's exact test: is cross-class rate significantly different?
    # Compare: cross vs pooled within-class
    within_cooccur = excl_excl_cooccur + shared_shared_cooccur
    within_pairs = excl_excl_pairs + shared_shared_pairs
    within_no_cooccur = within_pairs - within_cooccur
    cross_no_cooccur = cross_pairs - cross_cooccur

    table = [
        [cross_cooccur, cross_no_cooccur],
        [within_cooccur, within_no_cooccur]
    ]

    odds_ratio, p_value = stats.fisher_exact(table)

    print(f"\n  Fisher's exact test:")
    print(f"    Odds ratio: {odds_ratio:.3f}")
    print(f"    p-value: {p_value:.6f}")

    # Interpretation
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if cross_rate == 0:
        print("""
FINDING: Cross-class co-occurrence is ZERO.

A-exclusive and A/B-shared MIDDLEs NEVER appear together in the same entry.
This is COMPLETE INCOMPATIBILITY between the two classes.

The zero-mixing finding is FULLY EXPLAINED by incompatibility structure.
No additional "functional stratification" hypothesis is needed beyond C475.
""")
        verdict = "COMPLETE_INCOMPATIBILITY"
    elif cross_rate < baseline_rate * 0.5 and p_value < 0.001:
        print(f"""
FINDING: Cross-class co-occurrence is SIGNIFICANTLY LOWER than within-class.

Cross-class compatibility: {100*cross_rate:.2f}%
Within-class average:      {100*baseline_rate:.2f}%
Ratio: {cross_rate/baseline_rate:.3f}

A-exclusive and A/B-shared MIDDLEs show ELEVATED INCOMPATIBILITY.
This partially explains zero-mixing, but the effect is stronger than
expected from incompatibility alone.

INTERPRETATION: Both incompatibility structure AND functional stratification
contribute to the zero-mixing pattern.
""")
        verdict = "ELEVATED_INCOMPATIBILITY"
    elif p_value < 0.05:
        print(f"""
FINDING: Cross-class co-occurrence is somewhat different from within-class.

Cross-class compatibility: {100*cross_rate:.2f}%
Within-class average:      {100*baseline_rate:.2f}%

The difference is statistically significant but not dramatically so.
Incompatibility structure provides partial explanation for zero-mixing.
""")
        verdict = "PARTIAL_INCOMPATIBILITY"
    else:
        print(f"""
FINDING: Cross-class co-occurrence is NOT significantly different from within-class.

Cross-class compatibility: {100*cross_rate:.2f}%
Within-class average:      {100*baseline_rate:.2f}%

Incompatibility structure does NOT explain the zero-mixing pattern.
The functional stratification hypothesis stands as primary explanation.
""")
        verdict = "NO_SPECIAL_INCOMPATIBILITY"

    # Additional analysis: What about the specific pairs that DO co-occur?
    print()
    print("=" * 70)
    print("DETAILED CROSS-CLASS ANALYSIS")
    print("=" * 70)

    if cross_cooccur > 0:
        print(f"\n{cross_cooccur} cross-class pairs co-occur. Examining them...")

        # Find the actual co-occurring pairs
        cross_pairs_list = []
        for idx1 in excl_indices:
            for idx2 in shared_indices:
                if cooccur[idx1, idx2] > 0:
                    m1, m2 = middle_list[idx1], middle_list[idx2]
                    cross_pairs_list.append((m1, m2, cooccur[idx1, idx2]))

        cross_pairs_list.sort(key=lambda x: -x[2])

        print("\nTop cross-class co-occurrences:")
        for m1, m2, count in cross_pairs_list[:20]:
            print(f"  {m1} + {m2}: {count} entries")
    else:
        print("\nNo cross-class co-occurrences found.")
        print("A-exclusive and A/B-shared MIDDLEs are COMPLETELY PARTITIONED.")

    # Save results
    results = {
        'excl_excl_pairs': excl_excl_pairs,
        'excl_excl_cooccur': excl_excl_cooccur,
        'excl_excl_rate': excl_excl_rate,
        'shared_shared_pairs': shared_shared_pairs,
        'shared_shared_cooccur': shared_shared_cooccur,
        'shared_shared_rate': shared_shared_rate,
        'cross_pairs': cross_pairs,
        'cross_cooccur': cross_cooccur,
        'cross_rate': cross_rate,
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'verdict': verdict
    }

    output_path = RESULTS_DIR / 'incompatibility_test.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return results


if __name__ == '__main__':
    main()
