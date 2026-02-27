#!/usr/bin/env python3
"""
Phase 466: BLOCK_VOCABULARY_DRIFT
==================================
Tests whether consecutive blocks on a folio show directional vocabulary drift
consistent with an iterative refinement model.

C1326 found adjacent blocks are MORE categorically similar (JSD 0.071) than
paragraphs within a block (JSD 0.136). This rules out "sequential stages" and
"parallel stations". Hypothesis: iterative refinement -- each block re-runs a
similar procedure with slightly adjusted parameters, converging toward a target.

4-test battery:
  D1: Atom Profile Shift (k->e drift across blocks)
  D2: Vocabulary Convergence (narrowing MIDDLE sets)
  D3: Suffix Mode Shift (Mode A decreasing, Mode B increasing)
  D4: FL Stage Progression (material state advances across blocks)
"""

import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Phase 462 (foundation)
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    load_data, precompute_pairwise, GALLOWS, CATEGORIES, SEED,
    permutation_p, jaccard, normal_cdf
)

# Phase 463 (gallows + kernel fracs)
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import precompute_gallows_data, spearman_rho

# Phase 464 (block positions)
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_EXECUTION_CYCLE' / 'scripts'))
from block_execution_cycle import precompute_block_positions

# Phase 465 (block metrics)
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'SECTION_S_BLOCK_ARCHITECTURE' / 'scripts'))
from section_s_block_architecture import precompute_block_metrics

from scripts.voynich import Morphology

N_PERM = 1_000
MIN_BLOCKS = 3
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

# FL stage numeric mapping (C777)
FL_STAGE_INDEX = {
    'INITIAL': 0.0,
    'EARLY': 1.0,
    'MEDIAL': 2.0,
    'LATE': 3.0,
    'FINAL': 4.0,
    'TERMINAL': 5.0,
}


# ============================================================
# Helpers
# ============================================================

def median(values):
    """Compute median of a list of floats."""
    if not values:
        return 0.0
    sv = sorted(values)
    n = len(sv)
    if n % 2 == 0:
        return (sv[n // 2 - 1] + sv[n // 2]) / 2.0
    return sv[n // 2]


def permutation_test_ordinal_rho(folio_metric_lists, rng, n_perm=N_PERM,
                                  alternative='greater'):
    """Permutation test for ordinal Spearman rho pooled across folios.

    folio_metric_lists: list of (ordinals: list[int], values: list[float])
    alternative: 'greater' tests median rho > 0, 'less' tests median rho < 0
    Returns: (observed_median_rho, perm_p, all_rhos, null_medians)
    """
    # Compute observed rhos per folio
    observed_rhos = []
    valid_lists = []
    for ordinals, values in folio_metric_lists:
        if len(ordinals) < MIN_BLOCKS:
            continue
        # Check for constant values (rho undefined)
        if len(set(values)) <= 1:
            continue
        rho, _ = spearman_rho(ordinals, values)
        observed_rhos.append(rho)
        valid_lists.append((ordinals, values))

    if not observed_rhos:
        return 0.0, 1.0, [], []

    observed_median = median(observed_rhos)

    # Permutation null
    null_medians = []
    for _ in range(n_perm):
        perm_rhos = []
        for ordinals, values in valid_lists:
            shuffled = list(values)
            rng.shuffle(shuffled)
            # Check constant after shuffle (same data, still constant)
            if len(set(shuffled)) <= 1:
                continue
            rho, _ = spearman_rho(ordinals, shuffled)
            perm_rhos.append(rho)
        if perm_rhos:
            null_medians.append(median(perm_rhos))

    if not null_medians:
        return observed_median, 1.0, observed_rhos, []

    perm_p = permutation_p(observed_median, null_medians, alternative)
    return observed_median, perm_p, observed_rhos, null_medians


# ============================================================
# Phase 466 Pre-computation
# ============================================================

def precompute_block_aggregates(folio_data):
    """Aggregate per-block drift metrics for folios with 3+ blocks.

    Stores:
        fd['_drift_blocks']: List[dict] per block with k/h/e fracs,
            middle_count, mode_a_frac, fl_index, token_count
        fd['_drift_eligible']: bool (True if 3+ blocks)
    """
    print("Pre-computing block-level drift aggregates...")

    eligible_count = 0
    total_blocks = 0

    for folio, fd in folio_data.items():
        bi = fd['_block_indices']
        paras = fd['all_paras']
        kf = fd['_kernel_fracs']
        bm = fd['_block_metrics']

        if len(bi) < MIN_BLOCKS:
            fd['_drift_eligible'] = False
            fd['_drift_blocks'] = []
            continue

        fd['_drift_eligible'] = True
        eligible_count += 1
        drift_blocks = []

        for ordinal, blk_idxs in enumerate(bi):
            if not blk_idxs:
                drift_blocks.append(None)
                continue

            # (a) Token-weighted kernel fractions
            block_tokens = 0
            wk, wh, we = 0.0, 0.0, 0.0
            for pi in blk_idxs:
                tc = paras[pi].token_count
                block_tokens += tc
                wk += kf[pi]['k'] * tc
                wh += kf[pi]['h'] * tc
                we += kf[pi]['e'] * tc

            k_frac = wk / block_tokens if block_tokens > 0 else 0.0
            h_frac = wh / block_tokens if block_tokens > 0 else 0.0
            e_frac = we / block_tokens if block_tokens > 0 else 0.0

            # (b) MIDDLE vocabulary from _block_metrics
            middle_count = len(bm[ordinal]['middle_set'])

            # (c) Suffix mode A fraction
            all_modes = []
            for pi in blk_idxs:
                all_modes.extend(paras[pi].suffix_mode_sequence)
            if all_modes:
                count_a = sum(1 for m in all_modes if m == 'A')
                mode_a_frac = count_a / len(all_modes)
            else:
                mode_a_frac = None

            # (d) FL state index — iterate actual tokens
            fl_values = []
            for pi in blk_idxs:
                p = paras[pi]
                for la in p.lines:
                    for tok in la.tokens:
                        if tok.fl_stage and tok.fl_stage in FL_STAGE_INDEX:
                            fl_values.append(FL_STAGE_INDEX[tok.fl_stage])
            fl_index = sum(fl_values) / len(fl_values) if fl_values else None

            drift_blocks.append({
                'k_frac': k_frac,
                'h_frac': h_frac,
                'e_frac': e_frac,
                'middle_count': middle_count,
                'mode_a_frac': mode_a_frac,
                'fl_index': fl_index,
                'fl_token_count': len(fl_values),
                'token_count': block_tokens,
            })

            total_blocks += 1

        fd['_drift_blocks'] = drift_blocks

    print(f"  Eligible folios (>={MIN_BLOCKS} blocks): {eligible_count}")
    print(f"  Total blocks in eligible folios: {total_blocks}")


# ============================================================
# D1: Atom Profile Shift
# ============================================================

def test_d1(folio_data, rng):
    """D1: Kernel fraction drift across block ordinals.

    Test whether k-fraction decreases and e-fraction increases with
    block ordinal (iterative refinement: setup -> precision).
    """
    print("\n--- D1: Atom Profile Shift ---")

    # Collect per-folio ordinal-metric pairs for k, h, e
    k_lists = []
    h_lists = []
    e_lists = []
    section_data = defaultdict(lambda: {'k_rhos': [], 'e_rhos': [], 'h_rhos': []})

    n_folios = 0
    n_blocks = 0

    for folio, fd in folio_data.items():
        if not fd.get('_drift_eligible'):
            continue
        blocks = [b for b in fd['_drift_blocks'] if b is not None]
        if len(blocks) < MIN_BLOCKS:
            continue

        ordinals = list(range(len(blocks)))
        k_vals = [b['k_frac'] for b in blocks]
        h_vals = [b['h_frac'] for b in blocks]
        e_vals = [b['e_frac'] for b in blocks]

        k_lists.append((ordinals, k_vals))
        h_lists.append((ordinals, h_vals))
        e_lists.append((ordinals, e_vals))

        sec = fd['section']
        # Compute per-folio rho for section breakdown
        if len(set(k_vals)) > 1:
            rk, _ = spearman_rho(ordinals, k_vals)
            section_data[sec]['k_rhos'].append(rk)
        if len(set(h_vals)) > 1:
            rh, _ = spearman_rho(ordinals, h_vals)
            section_data[sec]['h_rhos'].append(rh)
        if len(set(e_vals)) > 1:
            re_, _ = spearman_rho(ordinals, e_vals)
            section_data[sec]['e_rhos'].append(re_)

        n_folios += 1
        n_blocks += len(blocks)

    # Permutation tests
    k_med, k_p, k_rhos, _ = permutation_test_ordinal_rho(k_lists, rng,
                                                           alternative='less')
    h_med, h_p, h_rhos, _ = permutation_test_ordinal_rho(h_lists, rng,
                                                           alternative='less')
    e_med, e_p, e_rhos, _ = permutation_test_ordinal_rho(e_lists, rng,
                                                           alternative='greater')

    k_decreasing = k_med < 0 and k_p < 0.01
    e_increasing = e_med > 0 and e_p < 0.01
    passed = k_decreasing and e_increasing

    # Direction counts
    def direction_counts(rhos):
        neg = sum(1 for r in rhos if r < 0)
        pos = sum(1 for r in rhos if r > 0)
        zero = sum(1 for r in rhos if r == 0)
        return {'negative': neg, 'positive': pos, 'zero': zero}

    # Section breakdown
    sec_breakdown = {}
    for sec in sorted(section_data):
        sd = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios': len(sd['k_rhos']),
            'median_k_rho': round(median(sd['k_rhos']), 4),
            'median_e_rho': round(median(sd['e_rhos']), 4),
            'median_h_rho': round(median(sd['h_rhos']), 4),
        }

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}, Blocks: {n_blocks}")
    print(f"  k: median_rho={k_med:.4f}, perm_p={k_p:.4f} ({'decreasing' if k_decreasing else 'NOT decreasing'})")
    print(f"  h: median_rho={h_med:.4f}, perm_p={h_p:.4f}")
    print(f"  e: median_rho={e_med:.4f}, perm_p={e_p:.4f} ({'increasing' if e_increasing else 'NOT increasing'})")
    print(f"  Result: {status}")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_folios']}, k_rho={sb['median_k_rho']}, e_rho={sb['median_e_rho']}")

    return {
        'test': 'D1: Atom Profile Shift',
        'tier': 'T2 (structural)',
        'passed': passed,
        'n_folios': n_folios,
        'n_blocks_total': n_blocks,
        'kernel_results': {
            'k': {
                'median_rho': round(k_med, 4),
                'mean_rho': round(sum(k_rhos) / len(k_rhos), 4) if k_rhos else 0.0,
                'perm_p': round(k_p, 4),
                'n_folios': len(k_rhos),
                'direction_count': direction_counts(k_rhos),
            },
            'h': {
                'median_rho': round(h_med, 4),
                'mean_rho': round(sum(h_rhos) / len(h_rhos), 4) if h_rhos else 0.0,
                'perm_p': round(h_p, 4),
                'n_folios': len(h_rhos),
                'direction_count': direction_counts(h_rhos),
            },
            'e': {
                'median_rho': round(e_med, 4),
                'mean_rho': round(sum(e_rhos) / len(e_rhos), 4) if e_rhos else 0.0,
                'perm_p': round(e_p, 4),
                'n_folios': len(e_rhos),
                'direction_count': direction_counts(e_rhos),
            },
        },
        'k_decreasing': k_decreasing,
        'e_increasing': e_increasing,
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# D2: Vocabulary Convergence
# ============================================================

def test_d2(folio_data, rng):
    """D2: Vocabulary narrowing across block ordinals.

    Sub-test (a): MIDDLE vocabulary size decreases with block ordinal
    Sub-test (b): Consecutive block Jaccard increases with position (convergence)
    Sub-test (c): Cumulative coverage of block 0's MIDDLEs (informational)
    """
    print("\n--- D2: Vocabulary Convergence ---")

    vocab_lists = []  # (ordinals, middle_counts) per folio
    jaccard_lists = []  # (pair_positions, jaccard_values) per folio — need 4+ blocks
    coverage_by_ordinal = defaultdict(list)  # ordinal -> list of coverage fracs
    section_data = defaultdict(lambda: {'vocab_rhos': [], 'jaccard_rhos': []})

    n_folios_vocab = 0
    n_folios_jaccard = 0

    for folio, fd in folio_data.items():
        if not fd.get('_drift_eligible'):
            continue
        blocks = fd['_drift_blocks']
        bm = fd['_block_metrics']
        valid = [(i, b) for i, b in enumerate(blocks) if b is not None]
        if len(valid) < MIN_BLOCKS:
            continue

        ordinals = [i for i, _ in valid]
        mcounts = [b['middle_count'] for _, b in valid]
        vocab_lists.append((ordinals, mcounts))
        n_folios_vocab += 1

        sec = fd['section']
        if len(set(mcounts)) > 1:
            rv, _ = spearman_rho(ordinals, mcounts)
            section_data[sec]['vocab_rhos'].append(rv)

        # Sub-test (b): Jaccard between consecutive pairs — need 4+ blocks for 3+ pairs
        if len(valid) >= 4:
            pair_positions = []
            pair_jaccards = []
            for idx in range(len(valid) - 1):
                i1, _ = valid[idx]
                i2, _ = valid[idx + 1]
                ms1 = bm[i1]['middle_set']
                ms2 = bm[i2]['middle_set']
                j = jaccard(ms1, ms2)
                pair_positions.append(idx + 0.5)
                pair_jaccards.append(j)
            if len(set(pair_jaccards)) > 1:
                jaccard_lists.append((pair_positions, pair_jaccards))
                rj, _ = spearman_rho(pair_positions, pair_jaccards)
                section_data[sec]['jaccard_rhos'].append(rj)
                n_folios_jaccard += 1

        # Sub-test (c): Cumulative coverage of block 0's MIDDLEs
        if valid:
            base_set = bm[valid[0][0]]['middle_set']
            if base_set:
                for ordinal_idx, (bi_idx, _) in enumerate(valid):
                    later_set = bm[bi_idx]['middle_set']
                    cov = len(base_set & later_set) / len(base_set)
                    coverage_by_ordinal[ordinal_idx].append(cov)

    # Permutation tests
    vocab_med, vocab_p, vocab_rhos, _ = permutation_test_ordinal_rho(
        vocab_lists, rng, alternative='less')

    if jaccard_lists:
        jacc_med, jacc_p, jacc_rhos, _ = permutation_test_ordinal_rho(
            jaccard_lists, rng, alternative='greater')
    else:
        jacc_med, jacc_p, jacc_rhos = 0.0, 1.0, []

    vocab_decreasing = vocab_med < 0 and vocab_p < 0.01
    jaccard_increasing = jacc_med > 0 and jacc_p < 0.01
    passed = vocab_decreasing or jaccard_increasing

    # Mean coverage by ordinal
    mean_coverages = {}
    for ordinal in sorted(coverage_by_ordinal):
        vals = coverage_by_ordinal[ordinal]
        mean_coverages[ordinal] = round(sum(vals) / len(vals), 4)

    # Section breakdown
    sec_breakdown = {}
    for sec in sorted(section_data):
        sd = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios_vocab': len(sd['vocab_rhos']),
            'median_vocab_rho': round(median(sd['vocab_rhos']), 4),
            'n_folios_jaccard': len(sd['jaccard_rhos']),
            'median_jaccard_rho': round(median(sd['jaccard_rhos']), 4) if sd['jaccard_rhos'] else None,
        }

    def direction_counts(rhos):
        return {
            'negative': sum(1 for r in rhos if r < 0),
            'positive': sum(1 for r in rhos if r > 0),
            'zero': sum(1 for r in rhos if r == 0),
        }

    status = 'PASS' if passed else 'FAIL'
    print(f"  Vocab size: n_folios={n_folios_vocab}, median_rho={vocab_med:.4f}, perm_p={vocab_p:.4f} ({'narrowing' if vocab_decreasing else 'NOT narrowing'})")
    print(f"  Jaccard trend: n_folios={n_folios_jaccard}, median_rho={jacc_med:.4f}, perm_p={jacc_p:.4f} ({'converging' if jaccard_increasing else 'NOT converging'})")
    if mean_coverages:
        cov_str = ', '.join(f"B{k}={v:.3f}" for k, v in list(mean_coverages.items())[:6])
        print(f"  Coverage of B0 MIDDLEs: {cov_str}...")
    print(f"  Result: {status}")

    return {
        'test': 'D2: Vocabulary Convergence',
        'tier': 'T2 (structural)',
        'passed': passed,
        'vocab_size_test': {
            'median_rho': round(vocab_med, 4),
            'mean_rho': round(sum(vocab_rhos) / len(vocab_rhos), 4) if vocab_rhos else 0.0,
            'perm_p': round(vocab_p, 4),
            'n_folios': n_folios_vocab,
            'direction_count': direction_counts(vocab_rhos),
        },
        'jaccard_trend_test': {
            'median_rho': round(jacc_med, 4),
            'mean_rho': round(sum(jacc_rhos) / len(jacc_rhos), 4) if jacc_rhos else 0.0,
            'perm_p': round(jacc_p, 4),
            'n_folios': n_folios_jaccard,
            'direction_count': direction_counts(jacc_rhos) if jacc_rhos else {},
        },
        'cumulative_coverage': {
            'mean_coverages_by_ordinal': mean_coverages,
        },
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# D3: Suffix Mode Shift
# ============================================================

def test_d3(folio_data, rng):
    """D3: Mode A fraction decreases with block ordinal.

    Early blocks should be specification-heavy (Mode A), later blocks
    execution-heavy (Mode B).
    """
    print("\n--- D3: Suffix Mode Shift ---")

    mode_lists = []
    section_data = defaultdict(list)

    n_folios = 0
    n_blocks = 0

    for folio, fd in folio_data.items():
        if not fd.get('_drift_eligible'):
            continue
        blocks = fd['_drift_blocks']
        # Filter to blocks with valid mode_a_frac
        valid = [(i, b) for i, b in enumerate(blocks)
                 if b is not None and b['mode_a_frac'] is not None]
        if len(valid) < MIN_BLOCKS:
            continue

        ordinals = [i for i, _ in valid]
        mode_a_vals = [b['mode_a_frac'] for _, b in valid]

        if len(set(mode_a_vals)) <= 1:
            continue

        mode_lists.append((ordinals, mode_a_vals))
        n_folios += 1
        n_blocks += len(valid)

        rho, _ = spearman_rho(ordinals, mode_a_vals)
        section_data[fd['section']].append(rho)

    # Permutation test
    obs_med, perm_p, all_rhos, _ = permutation_test_ordinal_rho(
        mode_lists, rng, alternative='less')

    passed = obs_med < 0 and perm_p < 0.01

    def direction_counts(rhos):
        return {
            'negative': sum(1 for r in rhos if r < 0),
            'positive': sum(1 for r in rhos if r > 0),
            'zero': sum(1 for r in rhos if r == 0),
        }

    sec_breakdown = {}
    for sec in sorted(section_data):
        rhos = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios': len(rhos),
            'median_rho': round(median(rhos), 4),
            'mean_rho': round(sum(rhos) / len(rhos), 4) if rhos else 0.0,
        }

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}, Blocks: {n_blocks}")
    print(f"  median_rho={obs_med:.4f}, perm_p={perm_p:.4f}")
    print(f"  Mode A {'decreasing' if passed else 'NOT decreasing'}")
    print(f"  Result: {status}")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_folios']}, median_rho={sb['median_rho']}")

    return {
        'test': 'D3: Suffix Mode Shift',
        'tier': 'T2-3 (structural with interpretive)',
        'passed': passed,
        'median_rho': round(obs_med, 4),
        'mean_rho': round(sum(all_rhos) / len(all_rhos), 4) if all_rhos else 0.0,
        'perm_p': round(perm_p, 4),
        'n_folios': n_folios,
        'n_blocks_total': n_blocks,
        'direction_count': direction_counts(all_rhos),
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# D4: FL Stage Progression
# ============================================================

def test_d4(folio_data, rng):
    """D4: Mean FL state index increases with block ordinal.

    Later blocks should describe materials at later transformation stages
    (INITIAL=0 -> TERMINAL=5).
    """
    print("\n--- D4: FL Stage Progression ---")

    fl_lists = []
    section_data = defaultdict(list)

    n_folios = 0
    n_blocks = 0
    blocks_no_fl = 0

    for folio, fd in folio_data.items():
        if not fd.get('_drift_eligible'):
            continue
        blocks = fd['_drift_blocks']
        # Filter to blocks with valid fl_index
        valid = [(i, b) for i, b in enumerate(blocks)
                 if b is not None and b['fl_index'] is not None]
        if len(valid) < MIN_BLOCKS:
            continue

        ordinals = [i for i, _ in valid]
        fl_vals = [b['fl_index'] for _, b in valid]

        if len(set(fl_vals)) <= 1:
            continue

        fl_lists.append((ordinals, fl_vals))
        n_folios += 1
        n_blocks += len(valid)

        rho, _ = spearman_rho(ordinals, fl_vals)
        section_data[fd['section']].append(rho)

        # Count blocks without FL data in this folio
        blocks_no_fl += sum(1 for b in blocks
                           if b is not None and b['fl_index'] is None)

    # Permutation test
    obs_med, perm_p, all_rhos, _ = permutation_test_ordinal_rho(
        fl_lists, rng, alternative='greater')

    passed = obs_med > 0 and perm_p < 0.01

    def direction_counts(rhos):
        return {
            'negative': sum(1 for r in rhos if r < 0),
            'positive': sum(1 for r in rhos if r > 0),
            'zero': sum(1 for r in rhos if r == 0),
        }

    # Mean FL index by ordinal position (across all folios)
    fl_by_ordinal = defaultdict(list)
    for folio, fd in folio_data.items():
        if not fd.get('_drift_eligible'):
            continue
        for i, b in enumerate(fd['_drift_blocks']):
            if b is not None and b['fl_index'] is not None:
                fl_by_ordinal[i].append(b['fl_index'])
    mean_fl_by_ordinal = {}
    for ordinal in sorted(fl_by_ordinal):
        vals = fl_by_ordinal[ordinal]
        if vals:
            mean_fl_by_ordinal[ordinal] = round(sum(vals) / len(vals), 4)

    sec_breakdown = {}
    for sec in sorted(section_data):
        rhos = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios': len(rhos),
            'median_rho': round(median(rhos), 4),
            'mean_rho': round(sum(rhos) / len(rhos), 4) if rhos else 0.0,
        }

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}, Blocks with FL: {n_blocks}, Blocks without FL: {blocks_no_fl}")
    print(f"  median_rho={obs_med:.4f}, perm_p={perm_p:.4f}")
    print(f"  FL stage {'advancing' if passed else 'NOT advancing'}")
    print(f"  Result: {status}")
    if mean_fl_by_ordinal:
        fl_str = ', '.join(f"B{k}={v:.3f}" for k, v in list(mean_fl_by_ordinal.items())[:6])
        print(f"  Mean FL by ordinal: {fl_str}...")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_folios']}, median_rho={sb['median_rho']}")

    return {
        'test': 'D4: FL Stage Progression',
        'tier': 'T2-3 (structural with interpretive)',
        'passed': passed,
        'median_rho': round(obs_med, 4),
        'mean_rho': round(sum(all_rhos) / len(all_rhos), 4) if all_rhos else 0.0,
        'perm_p': round(perm_p, 4),
        'n_folios': n_folios,
        'n_blocks_total': n_blocks,
        'blocks_without_fl': blocks_no_fl,
        'direction_count': direction_counts(all_rhos),
        'mean_fl_by_ordinal': mean_fl_by_ordinal,
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 466: BLOCK_VOCABULARY_DRIFT")
    print("Testing iterative refinement model for block architecture")
    print("=" * 80)

    rng = random.Random(SEED)

    # Full precompute pipeline (Phases 462-465)
    folio_data = load_data()
    precompute_pairwise(folio_data)
    precompute_gallows_data(folio_data)
    precompute_block_positions(folio_data)
    precompute_block_metrics(folio_data)

    # Phase 466 aggregation
    precompute_block_aggregates(folio_data)

    # Report
    eligible = sum(1 for fd in folio_data.values() if fd.get('_drift_eligible'))
    total_blocks = sum(len([b for b in fd['_drift_blocks'] if b is not None])
                       for fd in folio_data.values() if fd.get('_drift_eligible'))
    print(f"\nEligible folios (>={MIN_BLOCKS} blocks): {eligible}")
    print(f"Total blocks in eligible folios: {total_blocks}")

    # Section summary
    sec_counts = defaultdict(lambda: {'folios': 0, 'blocks': 0})
    for fd in folio_data.values():
        if fd.get('_drift_eligible'):
            sec = fd['section']
            sec_counts[sec]['folios'] += 1
            sec_counts[sec]['blocks'] += len([b for b in fd['_drift_blocks']
                                              if b is not None])
    for sec in sorted(sec_counts):
        sc = sec_counts[sec]
        print(f"  Section {sec}: {sc['folios']} folios, {sc['blocks']} blocks")

    # Run tests
    results = {}
    results['D1'] = test_d1(folio_data, rng)
    results['D2'] = test_d2(folio_data, rng)
    results['D3'] = test_d3(folio_data, rng)
    results['D4'] = test_d4(folio_data, rng)

    # Summary
    passed = sum(1 for r in results.values() if r.get('passed'))
    total = len(results)

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    for k in ['D1', 'D2', 'D3', 'D4']:
        r = results[k]
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} -- {r.get('test', k)}")

    if passed >= 3:
        interpretation = "ITERATIVE_REFINEMENT_CONFIRMED"
    elif passed >= 2:
        interpretation = "PARTIAL_REFINEMENT"
    elif passed == 1:
        interpretation = "WEAK_SIGNAL"
    else:
        interpretation = "NO_REFINEMENT_DETECTED"
    print(f"\n  Interpretation: {interpretation}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'BLOCK_VOCABULARY_DRIFT',
        'phase_number': 466,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'min_blocks': MIN_BLOCKS,
        'tests': results,
        'summary': {
            'tests_passed': passed,
            'tests_total': total,
            'eligible_folios': eligible,
            'total_blocks': total_blocks,
            'interpretation': interpretation,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'block_vocabulary_drift.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
