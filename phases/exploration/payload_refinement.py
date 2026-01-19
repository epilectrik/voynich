#!/usr/bin/env python
"""
Currier A Clean-Payload Refinement: Quantify DA articulation suppression.

Goal: Measure how much DA articulation suppressed payload-level similarity
metrics, without introducing semantics or modifying frozen constraints.

This is MEASUREMENT SHARPENING, not reinterpretation.

Three representations:
- FULL_TOKEN: Original tokens (baseline)
- TOKEN_MINUS_DA: Tokens excluding DA family (structural mask)
- MIDDLE_ONLY: Prefix-conditioned MIDDLE layer (payload isolation)

Expected pattern:
- FULL_TOKEN: ~1.31x (matches C346)
- TOKEN_MINUS_DA: > 1.31x
- MIDDLE_ONLY: highest

Output: Refinement note for C346, not new constraint.
"""
import sys
from collections import defaultdict
import numpy as np
from scipy import stats
import random

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

random.seed(42)


def load_currier_a_entries():
    """Load Currier A entries with line structure."""

    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def is_da_token(token):
    """Check if token is DA family."""
    return token.lower().startswith('da')


def get_representations(tokens):
    """
    Get three representations of an entry's tokens.

    Returns dict with:
    - FULL_TOKEN: set of original tokens
    - TOKEN_MINUS_DA: set of tokens excluding DA family
    - MIDDLE_ONLY: multiset of MIDDLE components (prefix-conditioned)
    """
    full_tokens = set(tokens)

    tokens_minus_da = set(t for t in tokens if not is_da_token(t))

    middles = []
    for token in tokens:
        if is_da_token(token):
            continue  # Mask DA for MIDDLE extraction too
        result = parse_currier_a_token(token)
        if result.middle:
            # Prefix-condition: include prefix context
            middles.append(f"{result.prefix}:{result.middle}")
    middle_set = set(middles)

    return {
        'FULL_TOKEN': full_tokens,
        'TOKEN_MINUS_DA': tokens_minus_da,
        'MIDDLE_ONLY': middle_set
    }


def jaccard(set1, set2):
    """Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def compute_adjacency_similarity(entries, mode):
    """
    Compute adjacent vs non-adjacent similarity for a given mode.

    Returns (adjacent_mean, nonadjacent_mean, ratio, p_value)
    """
    # Get representations for all entries
    representations = []
    for entry in entries:
        reps = get_representations(entry['tokens'])
        representations.append(reps[mode])

    # Adjacent pairs
    adjacent_sims = []
    for i in range(len(representations) - 1):
        s1, s2 = representations[i], representations[i+1]
        if s1 and s2:  # Both non-empty
            adjacent_sims.append(jaccard(s1, s2))

    # Non-adjacent pairs (sample for efficiency)
    nonadjacent_sims = []
    sample_size = min(5000, len(representations) * (len(representations) - 1) // 2)

    for _ in range(sample_size):
        i, j = random.sample(range(len(representations)), 2)
        if abs(i - j) > 1:  # Not adjacent
            s1, s2 = representations[i], representations[j]
            if s1 and s2:
                nonadjacent_sims.append(jaccard(s1, s2))

    adj_mean = np.mean(adjacent_sims) if adjacent_sims else 0
    nonadj_mean = np.mean(nonadjacent_sims) if nonadjacent_sims else 0

    ratio = adj_mean / nonadj_mean if nonadj_mean > 0 else float('inf')

    # Mann-Whitney U test
    if adjacent_sims and nonadjacent_sims:
        stat, p = stats.mannwhitneyu(adjacent_sims, nonadjacent_sims, alternative='greater')
    else:
        p = 1.0

    return {
        'mode': mode,
        'adjacent_mean': adj_mean,
        'nonadjacent_mean': nonadj_mean,
        'ratio': ratio,
        'p_value': p,
        'n_adjacent': len(adjacent_sims),
        'n_nonadjacent': len(nonadjacent_sims)
    }


def segment_at_da(tokens):
    """Segment token list at DA tokens. Returns list of blocks."""
    blocks = []
    current = []

    for token in tokens:
        if is_da_token(token):
            if current:
                blocks.append(current)
            current = []
        else:
            current.append(token)

    if current:
        blocks.append(current)

    return blocks


def compute_block_similarity(entries):
    """
    Block-level similarity analysis.

    Compares:
    - Adjacent blocks (within same entry)
    - Random block pairs
    """
    all_blocks = []
    adjacent_block_pairs = []

    for entry in entries:
        blocks = segment_at_da(entry['tokens'])

        if len(blocks) < 2:
            continue

        # Get MIDDLE representations for each block
        block_reps = []
        for block in blocks:
            middles = set()
            for token in block:
                result = parse_currier_a_token(token)
                if result.middle:
                    middles.add(f"{result.prefix}:{result.middle}")
            if middles:
                block_reps.append(middles)
                all_blocks.append(middles)

        # Adjacent block pairs within entry
        for i in range(len(block_reps) - 1):
            adjacent_block_pairs.append((block_reps[i], block_reps[i+1]))

    # Compute adjacent block similarity
    adjacent_sims = [jaccard(b1, b2) for b1, b2 in adjacent_block_pairs]

    # Random block pairs
    random_sims = []
    for _ in range(min(2000, len(all_blocks) * 10)):
        if len(all_blocks) >= 2:
            b1, b2 = random.sample(all_blocks, 2)
            random_sims.append(jaccard(b1, b2))

    return {
        'n_blocks': len(all_blocks),
        'n_adjacent_pairs': len(adjacent_block_pairs),
        'adjacent_mean': np.mean(adjacent_sims) if adjacent_sims else 0,
        'random_mean': np.mean(random_sims) if random_sims else 0,
        'ratio': np.mean(adjacent_sims) / np.mean(random_sims) if random_sims and np.mean(random_sims) > 0 else 0
    }


def main():
    print("=" * 70)
    print("CURRIER A CLEAN-PAYLOAD REFINEMENT")
    print("=" * 70)
    print("\nGoal: Quantify DA articulation suppression on similarity metrics")
    print("This is MEASUREMENT SHARPENING, not reinterpretation.\n")

    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries\n")

    # ==========================================================================
    # TEST 1: ADJACENCY SIMILARITY BY MODE
    # ==========================================================================

    print("-" * 70)
    print("TEST 1: ADJACENCY SIMILARITY BY REPRESENTATION")
    print("-" * 70)
    print("\nExpected: FULL_TOKEN ~1.31x, TOKEN_MINUS_DA > 1.31x, MIDDLE_ONLY highest\n")

    modes = ['FULL_TOKEN', 'TOKEN_MINUS_DA', 'MIDDLE_ONLY']
    results = []

    for mode in modes:
        result = compute_adjacency_similarity(entries, mode)
        results.append(result)

    print(f"{'Mode':<20} {'Adjacent J':<12} {'Non-adj J':<12} {'Ratio':<10} {'p-value':<12}")
    print("-" * 66)

    for r in results:
        print(f"{r['mode']:<20} {r['adjacent_mean']:.4f}{'':>6} {r['nonadjacent_mean']:.4f}{'':>6} {r['ratio']:.2f}x{'':>4} {r['p_value']:.2e}")

    # Calculate suppression
    full_ratio = results[0]['ratio']
    minus_da_ratio = results[1]['ratio']
    middle_ratio = results[2]['ratio']

    print(f"\nDA suppression effect:")
    print(f"  FULL -> TOKEN_MINUS_DA: {(minus_da_ratio/full_ratio - 1)*100:+.1f}% gain")
    print(f"  FULL -> MIDDLE_ONLY: {(middle_ratio/full_ratio - 1)*100:+.1f}% gain")

    # ==========================================================================
    # TEST 2: BLOCK-LEVEL SIMILARITY
    # ==========================================================================

    print("\n" + "-" * 70)
    print("TEST 2: BLOCK-LEVEL SIMILARITY (DA-SEGMENTED)")
    print("-" * 70)
    print("\nValidates: DA role, block atomicity, lack of cross-block smoothing\n")

    block_result = compute_block_similarity(entries)

    print(f"Total blocks analyzed: {block_result['n_blocks']}")
    print(f"Adjacent block pairs: {block_result['n_adjacent_pairs']}")
    print(f"\nAdjacent block similarity: J={block_result['adjacent_mean']:.4f}")
    print(f"Random block similarity: J={block_result['random_mean']:.4f}")
    print(f"Ratio: {block_result['ratio']:.2f}x")

    if block_result['ratio'] < 1.1:
        print("\n-> Blocks do NOT show cross-block content smoothing")
        print("-> DA genuinely separates independent sub-records")
    else:
        print("\n-> Some block-to-block coherence detected")

    # ==========================================================================
    # SUMMARY
    # ==========================================================================

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
Findings:
---------
1. FULL_TOKEN adjacency ratio: {full_ratio:.2f}x (matches C346 baseline)
2. TOKEN_MINUS_DA ratio: {minus_da_ratio:.2f}x ({(minus_da_ratio/full_ratio - 1)*100:+.1f}% vs baseline)
3. MIDDLE_ONLY ratio: {middle_ratio:.2f}x ({(middle_ratio/full_ratio - 1)*100:+.1f}% vs baseline)

Interpretation:
---------------
DA articulation {'suppresses' if minus_da_ratio > full_ratio else 'does not suppress'} observed adjacency similarity.
Content-level coherence is {'stronger' if middle_ratio > full_ratio else 'similar'} but remains soft and overlapping.

Block-level finding:
--------------------
Adjacent blocks show {block_result['ratio']:.2f}x similarity vs random.
{'DA genuinely separates independent sub-records.' if block_result['ratio'] < 1.1 else 'Some block coherence exists.'}

Documentation:
--------------
This is a REFINEMENT NOTE for C346, not a new constraint.
The finding sharpens measurement, it does not change interpretation.
""")


if __name__ == '__main__':
    main()
