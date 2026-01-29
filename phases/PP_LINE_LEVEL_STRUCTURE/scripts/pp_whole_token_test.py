"""
PP_LINE_LEVEL_STRUCTURE - Script 3: Whole-Token Co-occurrence (T9)

Tests whether whole PP tokens (not just MIDDLEs) show co-occurrence
structure within Currier A lines beyond what MIDDLE-level incompatibility
predicts.

Phase: PP_LINE_LEVEL_STRUCTURE
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_PERM = 1000
rng = np.random.RandomState(42)


def load_data():
    """Pre-compute per-folio, per-line PP token data."""
    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    # Per-line: whole tokens (word) and their MIDDLEs
    folio_line_pp_words = {}    # folio -> [[word1, word2, ...], ...]
    folio_line_pp_mids = {}     # folio -> [[mid1, mid2, ...], ...]

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        line_words = []
        line_mids = []
        for rec in records:
            words = []
            mids = []
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    words.append(t.word)
                    mids.append(t.middle)
            line_words.append(words)
            line_mids.append(mids)
        folio_line_pp_words[fol] = line_words
        folio_line_pp_mids[fol] = line_mids

    return folios, folio_line_pp_words, folio_line_pp_mids


def count_pairs(folio_line_data):
    """Count unique co-occurring pairs and variance from per-folio line data."""
    pair_counts = defaultdict(int)
    total_pairs = 0
    lines_used = 0

    for fol, line_list in folio_line_data.items():
        for items in line_list:
            if len(items) < 2:
                continue
            lines_used += 1
            item_set = set(items)
            for a, b in combinations(sorted(item_set), 2):
                pair_counts[(a, b)] += 1
                total_pairs += 1

    unique = len(pair_counts)
    counts = list(pair_counts.values())
    variance = float(np.var(counts)) if counts else 0.0
    return pair_counts, unique, variance, total_pairs, lines_used


def shuffle_within_folio(folio_line_data, rng):
    """Shuffle items within each folio, preserving line lengths."""
    shuffled = {}
    for fol, line_list in folio_line_data.items():
        all_items = []
        lengths = []
        for items in line_list:
            all_items.extend(items)
            lengths.append(len(items))
        rng.shuffle(all_items)
        new_lines = []
        idx = 0
        for length in lengths:
            new_lines.append(all_items[idx:idx + length])
            idx += length
        shuffled[fol] = new_lines
    return shuffled


def shuffle_words_preserving_middles(folio_line_pp_words, folio_line_pp_mids, rng):
    """Shuffle whole tokens across lines BUT constrained to preserve
    MIDDLE-level line assignment. Within each line, replace each token
    with another token sharing the same MIDDLE from the folio pool.

    This tests: given the same MIDDLE assignment to lines, does the
    specific token variant matter?
    """
    shuffled = {}
    for fol in folio_line_pp_words:
        line_words = folio_line_pp_words[fol]
        line_mids = folio_line_pp_mids[fol]

        # Build pool: MIDDLE -> list of all tokens with that MIDDLE in this folio
        mid_to_tokens = defaultdict(list)
        for words, mids in zip(line_words, line_mids):
            for w, m in zip(words, mids):
                mid_to_tokens[m].append(w)

        # For each MIDDLE, shuffle its token pool
        mid_pools = {}
        for m, tokens in mid_to_tokens.items():
            pool = list(tokens)
            rng.shuffle(pool)
            mid_pools[m] = iter(pool)

        # Reassign: each position gets a token with the same MIDDLE
        new_lines = []
        for mids in line_mids:
            new_line = []
            for m in mids:
                new_line.append(next(mid_pools[m]))
            new_lines.append(new_line)
        shuffled[fol] = new_lines

    return shuffled


def main():
    print("PP_LINE_LEVEL_STRUCTURE - Script 3: Whole-Token Co-occurrence")
    print("=" * 60)

    print("\nLoading data...")
    folios, folio_line_pp_words, folio_line_pp_mids = load_data()

    # Summary
    all_words = set()
    all_mids = set()
    total_tokens = 0
    for fol in folios:
        for words, mids in zip(folio_line_pp_words[fol], folio_line_pp_mids[fol]):
            all_words.update(words)
            all_mids.update(mids)
            total_tokens += len(words)

    print(f"Folios: {len(folios)}")
    print(f"Total PP token occurrences: {total_tokens}")
    print(f"Unique PP whole tokens (word forms): {len(all_words)}")
    print(f"Unique PP MIDDLEs: {len(all_mids)}")
    print(f"Token/MIDDLE ratio: {len(all_words) / len(all_mids):.2f}x")

    results = {}

    # ================================================================
    # T9a: Whole-token co-occurrence vs free shuffle
    # ================================================================
    print("\n=== T9a: Whole-Token Co-occurrence (free shuffle) ===")

    obs_pairs_w, obs_unique_w, obs_var_w, obs_total_w, lines_used = count_pairs(folio_line_pp_words)
    print(f"Lines with 2+ PP tokens: {lines_used}")
    print(f"Total within-line word pairs: {obs_total_w}")
    print(f"Observed unique word pairs: {obs_unique_w}")
    print(f"Observed word pair variance: {obs_var_w:.4f}")

    # For comparison: MIDDLE-level stats
    obs_pairs_m, obs_unique_m, obs_var_m, obs_total_m, _ = count_pairs(folio_line_pp_mids)
    print(f"\nMIDDLE-level unique pairs: {obs_unique_m}")
    print(f"Word-level unique pairs: {obs_unique_w}")
    print(f"Expansion factor: {obs_unique_w / obs_unique_m:.2f}x")

    # Free shuffle null (same as T1 but at word level)
    null_unique_w = []
    null_var_w = []
    for i in range(N_PERM):
        shuffled = shuffle_within_folio(folio_line_pp_words, rng)
        _, u, v, _, _ = count_pairs(shuffled)
        null_unique_w.append(u)
        null_var_w.append(v)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_unique_w = np.array(null_unique_w)
    null_var_w = np.array(null_var_w)

    p_unique_lower = float(np.mean(null_unique_w <= obs_unique_w))
    p_unique_upper = float(np.mean(null_unique_w >= obs_unique_w))
    p_var = float(np.mean(null_var_w >= obs_var_w))

    print(f"\nObserved unique word pairs: {obs_unique_w}")
    print(f"Null unique: {np.mean(null_unique_w):.1f} +/- {np.std(null_unique_w):.1f}")
    print(f"p_unique_lower (fewer): {p_unique_lower:.4f}")
    print(f"p_unique_upper (more): {p_unique_upper:.4f}")
    print(f"Observed variance: {obs_var_w:.4f}")
    print(f"Null variance: {np.mean(null_var_w):.4f} +/- {np.std(null_var_w):.4f}")
    print(f"p_variance: {p_var:.4f}")

    t9a_pass = p_unique_lower < 0.01 or p_unique_upper < 0.01 or p_var < 0.01

    results['T9a_whole_token_free_shuffle'] = {
        'test': 'T9a_whole_token_free_shuffle',
        'unique_word_types': len(all_words),
        'unique_middle_types': len(all_mids),
        'expansion_factor': len(all_words) / len(all_mids),
        'lines_with_2plus': lines_used,
        'total_word_pairs': obs_total_w,
        'observed_unique_word_pairs': obs_unique_w,
        'observed_unique_middle_pairs': obs_unique_m,
        'observed_word_variance': obs_var_w,
        'null_unique_mean': float(np.mean(null_unique_w)),
        'null_unique_std': float(np.std(null_unique_w)),
        'null_variance_mean': float(np.mean(null_var_w)),
        'null_variance_std': float(np.std(null_var_w)),
        'p_unique_lower': p_unique_lower,
        'p_unique_upper': p_unique_upper,
        'p_variance': p_var,
        'PASS': t9a_pass,
        'verdict': 'PASS' if t9a_pass else 'FAIL'
    }

    print(f"T9a verdict: {'PASS' if t9a_pass else 'FAIL'}")

    # ================================================================
    # T9b: Whole-token structure BEYOND middle-level assignment
    # ================================================================
    print("\n=== T9b: Whole-Token Structure Beyond MIDDLE Assignment ===")
    print("(Shuffle token variants within same MIDDLE, preserving MIDDLE-line assignment)")

    # This test holds MIDDLE assignment to lines fixed,
    # and shuffles which specific token variant fills each MIDDLE slot.
    # If PASS: the specific token variant (PREFIX+SUFFIX choice) matters
    # If FAIL: only the MIDDLE identity matters, variant is irrelevant

    null_unique_variant = []
    null_var_variant = []

    for i in range(N_PERM):
        shuffled = shuffle_words_preserving_middles(
            folio_line_pp_words, folio_line_pp_mids, rng)
        _, u, v, _, _ = count_pairs(shuffled)
        null_unique_variant.append(u)
        null_var_variant.append(v)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_unique_variant = np.array(null_unique_variant)
    null_var_variant = np.array(null_var_variant)

    p_unique_v_lower = float(np.mean(null_unique_variant <= obs_unique_w))
    p_unique_v_upper = float(np.mean(null_unique_variant >= obs_unique_w))
    p_var_v = float(np.mean(null_var_variant >= obs_var_w))

    print(f"\nObserved unique word pairs: {obs_unique_w}")
    print(f"Variant-null unique: {np.mean(null_unique_variant):.1f} +/- {np.std(null_unique_variant):.1f}")
    print(f"p_unique_lower (fewer): {p_unique_v_lower:.4f}")
    print(f"p_unique_upper (more): {p_unique_v_upper:.4f}")
    print(f"Observed variance: {obs_var_w:.4f}")
    print(f"Variant-null variance: {np.mean(null_var_variant):.4f} +/- {np.std(null_var_variant):.4f}")
    print(f"p_variance: {p_var_v:.4f}")

    t9b_pass = p_unique_v_lower < 0.01 or p_unique_v_upper < 0.01 or p_var_v < 0.01

    results['T9b_whole_token_variant_shuffle'] = {
        'test': 'T9b_whole_token_variant_shuffle',
        'observed_unique_word_pairs': obs_unique_w,
        'observed_word_variance': obs_var_w,
        'variant_null_unique_mean': float(np.mean(null_unique_variant)),
        'variant_null_unique_std': float(np.std(null_unique_variant)),
        'variant_null_variance_mean': float(np.mean(null_var_variant)),
        'variant_null_variance_std': float(np.std(null_var_variant)),
        'p_unique_lower': p_unique_v_lower,
        'p_unique_upper': p_unique_v_upper,
        'p_variance': p_var_v,
        'PASS': t9b_pass,
        'verdict': 'PASS' if t9b_pass else 'FAIL'
    }

    print(f"T9b verdict: {'PASS' if t9b_pass else 'FAIL'}")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  T9a (free shuffle, word level): {results['T9a_whole_token_free_shuffle']['verdict']}")
    print(f"  T9b (variant shuffle, MIDDLE-preserving): {results['T9b_whole_token_variant_shuffle']['verdict']}")

    if t9a_pass and not t9b_pass:
        print("\n  --> Word-level structure exists but is fully explained by MIDDLE assignment.")
        print("      Specific token variant (PREFIX+SUFFIX) adds no structure.")
    elif t9a_pass and t9b_pass:
        print("\n  --> Word-level structure exists BEYOND MIDDLE assignment.")
        print("      Specific token variants are structured within lines.")
    elif not t9a_pass:
        print("\n  --> No word-level co-occurrence structure at all.")

    # Save
    output_path = RESULTS_DIR / 'pp_whole_token_tests.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
