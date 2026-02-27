#!/usr/bin/env python3
"""
Phase 464: BLOCK_EXECUTION_CYCLE
=================================
Tests whether visual text blocks form complete execution cycles:
initiation (k/f/p) -> continuation (t) -> [termination] -> reinitiation.

Building on Phases 462-463:
- C1317: 91.5% multi-block, 485 blocks
- C1318: Within-block PREFIX complementarity
- C1321: Gallows ordering (k/f/p early, t late)
- C1322: Gallows encode WHEN, not WHAT

8-test battery in 3 groups:
  A1: Gallows restart confirmation
  A2: Kernel initiation reset
  A3: Cross-block PREFIX discontinuity
  A4: Cross-block category discontinuity
  B1: Block-final -am enrichment
  B2: Block-final suffix mode
  B3: Block-final category profile
  C1: Block-level REGIME homogeneity
"""

import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Reuse Phase 462 infrastructure
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    load_data, precompute_pairwise, GALLOWS, CATEGORIES, SEED,
    mann_whitney_u, kruskal_wallis, permutation_p, normalize_profile,
    normal_cdf, chi2_sf, jsd, cosine_sim
)

# Reuse Phase 463 infrastructure
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import (
    precompute_gallows_data, chi2_test_matrix, GALLOWS_LIST
)

from scripts.voynich import Morphology

N_PERM = 1_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'


# ============================================================
# Additional statistical utilities
# ============================================================

def fisher_exact_2x2(table, alternative='greater'):
    """Fisher exact test for a 2x2 contingency table.
    table = [[a, b], [c, d]]
    Uses log-factorials to avoid overflow.
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d

    max_val = n + 1
    log_fact = [0.0] * (max_val + 1)
    for i in range(2, max_val + 1):
        log_fact[i] = log_fact[i - 1] + math.log(i)

    r1 = a + b
    r2 = c + d
    c1 = a + c
    c2 = b + d

    def log_hyper(x):
        y = r1 - x
        z = c1 - x
        w = r2 - z
        if y < 0 or z < 0 or w < 0:
            return float('-inf')
        return (log_fact[r1] + log_fact[r2] + log_fact[c1] + log_fact[c2]
                - log_fact[x] - log_fact[y] - log_fact[z] - log_fact[w] - log_fact[n])

    observed_lp = log_hyper(a)

    if alternative == 'greater':
        max_x = min(r1, c1)
        p_val = sum(math.exp(log_hyper(x)) for x in range(a, max_x + 1)
                    if log_hyper(x) > float('-inf'))
    elif alternative == 'less':
        p_val = sum(math.exp(log_hyper(x)) for x in range(0, a + 1)
                    if log_hyper(x) > float('-inf'))
    else:
        max_x = min(r1, c1)
        p_val = sum(math.exp(lp) for lp in (log_hyper(x) for x in range(0, max_x + 1))
                    if lp > float('-inf') and lp <= observed_lp + 1e-10)

    return min(p_val, 1.0)


# ============================================================
# Phase 464 Pre-computation
# ============================================================

def precompute_block_positions(folio_data):
    """Compute block position labels and cross-block transition pairs."""
    print("Pre-computing block positions...")
    total_transitions = 0
    total_sole = 0
    position_counts = Counter()

    for folio, fd in folio_data.items():
        bi = fd['_block_indices']
        n = fd['_n']

        positions = [None] * n
        for blk_idxs in bi:
            if len(blk_idxs) == 0:
                continue
            if len(blk_idxs) == 1:
                positions[blk_idxs[0]] = 'SOLE'
                total_sole += 1
            else:
                positions[blk_idxs[0]] = 'INITIAL'
                for idx in blk_idxs[1:-1]:
                    positions[idx] = 'INTERNAL'
                positions[blk_idxs[-1]] = 'FINAL'

        cross_pairs = []
        for b in range(len(bi) - 1):
            if bi[b] and bi[b + 1]:
                final_idx = bi[b][-1]
                initial_idx = bi[b + 1][0]
                cross_pairs.append((final_idx, initial_idx))
                total_transitions += 1

        for p in positions:
            if p:
                position_counts[p] += 1

        fd['_block_positions'] = positions
        fd['_cross_block_pairs'] = cross_pairs

    print(f"  Cross-block transitions: {total_transitions}")
    print(f"  Sole-paragraph blocks: {total_sole}")
    for pos in ['INITIAL', 'INTERNAL', 'FINAL', 'SOLE']:
        print(f"  {pos}: {position_counts[pos]}")


# ============================================================
# Test A1: Gallows Restart Confirmation
# ============================================================

def test_a1(folio_data):
    """A1: Gallows at block boundaries -- final=t-enriched, initial=k/f/p-enriched."""
    print("\n=== A1: Gallows Restart Confirmation ===")

    final_gallows = Counter()
    initial_gallows = Counter()

    for fd in folio_data.values():
        gl = fd['_gallows']
        for final_idx, initial_idx in fd['_cross_block_pairs']:
            if gl[final_idx]:
                final_gallows[gl[final_idx]] += 1
            if gl[initial_idx]:
                initial_gallows[gl[initial_idx]] += 1

    # 2x4 contingency: [FINAL, INITIAL] x [f, k, p, t]
    table = [[final_gallows.get(g, 0) for g in GALLOWS_LIST],
             [initial_gallows.get(g, 0) for g in GALLOWS_LIST]]

    chi2, p, df = chi2_test_matrix(table)

    print("  Gallows distribution at block boundaries:")
    print(f"  {'':>10s} {'f':>6s} {'k':>6s} {'p':>6s} {'t':>6s} {'total':>6s}")
    for label, row in [('FINAL', table[0]), ('INITIAL', table[1])]:
        total_row = sum(row)
        pcts = [f"{100 * v / total_row:.1f}%" if total_row > 0 else "-" for v in row]
        print(f"  {label:>10s} {pcts[0]:>6s} {pcts[1]:>6s} {pcts[2]:>6s} {pcts[3]:>6s} n={total_row}")

    final_total = sum(final_gallows.values())
    initial_total = sum(initial_gallows.values())
    t_final_pct = 100 * final_gallows.get('t', 0) / final_total if final_total > 0 else 0
    t_initial_pct = 100 * initial_gallows.get('t', 0) / initial_total if initial_total > 0 else 0
    kfp_final_pct = 100 * sum(final_gallows.get(g, 0) for g in ['k', 'f', 'p']) / final_total if final_total > 0 else 0
    kfp_initial_pct = 100 * sum(initial_gallows.get(g, 0) for g in ['k', 'f', 'p']) / initial_total if initial_total > 0 else 0

    print(f"\n  t at FINAL: {t_final_pct:.1f}% vs INITIAL: {t_initial_pct:.1f}%")
    print(f"  k/f/p at INITIAL: {kfp_initial_pct:.1f}% vs FINAL: {kfp_final_pct:.1f}%")
    print(f"  Chi-sq: {chi2:.2f}, df={df}, p={p:.6f}")

    passed = p < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'A1: Gallows Restart Confirmation',
        'passed': passed,
        'contingency_table': table,
        'final_gallows': dict(final_gallows),
        'initial_gallows': dict(initial_gallows),
        't_final_pct': round(t_final_pct, 1),
        't_initial_pct': round(t_initial_pct, 1),
        'kfp_initial_pct': round(kfp_initial_pct, 1),
        'kfp_final_pct': round(kfp_final_pct, 1),
        'chi2': round(chi2, 3),
        'p': round(p, 6),
        'df': df,
    }


# ============================================================
# Test A2: Kernel Initiation Reset
# ============================================================

def test_a2(folio_data):
    """A2: Block-initial paragraphs show stronger e->k->h initiation ordering."""
    print("\n=== A2: Kernel Initiation Reset ===")

    initial_scores = []
    internal_scores = []

    for fd in folio_data.values():
        paras = fd['all_paras']
        positions = fd['_block_positions']

        for i, p in enumerate(paras):
            pos = positions[i]
            if pos is None or pos == 'SOLE':
                continue

            # Collect kernel positions within paragraph
            e_positions = []
            k_positions = []
            h_positions = []
            token_idx = 0
            for la in p.lines:
                for t in la.tokens:
                    for kern in t.kernels:
                        if kern == 'e':
                            e_positions.append(token_idx)
                        elif kern == 'k':
                            k_positions.append(token_idx)
                        elif kern == 'h':
                            h_positions.append(token_idx)
                    token_idx += 1

            # Concordance: proportion of (e,k) pairs where e < k
            ek_concordant = 0
            ek_total = 0
            for ep in e_positions:
                for kp in k_positions:
                    ek_total += 1
                    if ep < kp:
                        ek_concordant += 1

            kh_concordant = 0
            kh_total = 0
            for kp in k_positions:
                for hp in h_positions:
                    kh_total += 1
                    if kp < hp:
                        kh_concordant += 1

            scores = []
            if ek_total > 0:
                scores.append(ek_concordant / ek_total)
            if kh_total > 0:
                scores.append(kh_concordant / kh_total)

            if not scores:
                continue

            avg_score = sum(scores) / len(scores)

            if pos == 'INITIAL':
                initial_scores.append(avg_score)
            elif pos in ('INTERNAL', 'FINAL'):
                internal_scores.append(avg_score)

    if not initial_scores or not internal_scores:
        print("  Insufficient data")
        return {'test': 'A2: Kernel Initiation Reset', 'passed': False,
                'reason': 'insufficient data'}

    init_mean = sum(initial_scores) / len(initial_scores)
    int_mean = sum(internal_scores) / len(internal_scores)
    U, z, p_mw = mann_whitney_u(initial_scores, internal_scores)

    print(f"  Block-initial e->k->h concordance: {init_mean:.4f} (n={len(initial_scores)})")
    print(f"  Block-internal concordance: {int_mean:.4f} (n={len(internal_scores)})")
    print(f"  MW z={z:.2f} p={p_mw:.6f}")

    passed = init_mean > int_mean and p_mw < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'A2: Kernel Initiation Reset',
        'passed': passed,
        'initial_mean': round(init_mean, 4),
        'internal_mean': round(int_mean, 4),
        'n_initial': len(initial_scores),
        'n_internal': len(internal_scores),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
    }


# ============================================================
# Test A3: Cross-Block PREFIX Discontinuity
# ============================================================

def test_a3(folio_data, rng):
    """A3: PREFIX JSD across block boundaries > within-block paragraph boundaries."""
    print("\n=== A3: Cross-Block PREFIX Discontinuity ===")

    morph = Morphology()

    # Collect all prefixes
    all_prefixes = set()
    for fd in folio_data.values():
        for p in fd['all_paras']:
            for la in p.lines:
                for tok in la.tokens:
                    m = morph.extract(tok.word)
                    if m.prefix:
                        all_prefixes.add(m.prefix)
    prefix_keys = sorted(all_prefixes)

    def line_prefix_vec(line_analysis):
        counts = Counter()
        for tok in line_analysis.tokens:
            m = morph.extract(tok.word)
            if m.prefix:
                counts[m.prefix] += 1
        return normalize_profile(counts, prefix_keys)

    cross_block_jsds = []
    within_block_jsds = []

    for fd in folio_data.values():
        paras = fd['all_paras']
        bi = fd['_block_indices']

        # Cross-block: last line of final para -> first line of next initial para
        for final_idx, initial_idx in fd['_cross_block_pairs']:
            final_para = paras[final_idx]
            initial_para = paras[initial_idx]
            if not final_para.lines or not initial_para.lines:
                continue
            v1 = line_prefix_vec(final_para.lines[-1])
            v2 = line_prefix_vec(initial_para.lines[0])
            if sum(v1) > 0 and sum(v2) > 0:
                cross_block_jsds.append(jsd(v1, v2))

        # Within-block: adjacent paragraph boundaries
        for blk_idxs in bi:
            if len(blk_idxs) < 2:
                continue
            for a in range(len(blk_idxs) - 1):
                pa = paras[blk_idxs[a]]
                pb = paras[blk_idxs[a + 1]]
                if not pa.lines or not pb.lines:
                    continue
                v1 = line_prefix_vec(pa.lines[-1])
                v2 = line_prefix_vec(pb.lines[0])
                if sum(v1) > 0 and sum(v2) > 0:
                    within_block_jsds.append(jsd(v1, v2))

    if not cross_block_jsds or not within_block_jsds:
        print("  Insufficient data")
        return {'test': 'A3: Cross-Block PREFIX Discontinuity', 'passed': False,
                'reason': 'insufficient data'}

    cross_mean = sum(cross_block_jsds) / len(cross_block_jsds)
    within_mean = sum(within_block_jsds) / len(within_block_jsds)
    U, z, p_mw = mann_whitney_u(cross_block_jsds, within_block_jsds)

    # Permutation: shuffle boundary type labels
    observed_diff = cross_mean - within_mean
    all_jsds = cross_block_jsds + within_block_jsds
    n_cross = len(cross_block_jsds)
    null_diffs = []
    for _ in range(N_PERM):
        rng.shuffle(all_jsds)
        fake_cross = all_jsds[:n_cross]
        fake_within = all_jsds[n_cross:]
        if fake_cross and fake_within:
            null_diffs.append(sum(fake_cross) / len(fake_cross) -
                              sum(fake_within) / len(fake_within))
    perm_p = permutation_p(observed_diff, null_diffs, 'greater')

    print(f"  Cross-block PREFIX JSD: {cross_mean:.4f} (n={len(cross_block_jsds)})")
    print(f"  Within-block PREFIX JSD: {within_mean:.4f} (n={len(within_block_jsds)})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.6f}")
    print(f"  Permutation p: {perm_p:.4f}")

    passed = cross_mean > within_mean and p_mw < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'A3: Cross-Block PREFIX Discontinuity',
        'passed': passed,
        'cross_mean': round(cross_mean, 4),
        'within_mean': round(within_mean, 4),
        'diff': round(observed_diff, 4),
        'n_cross': len(cross_block_jsds),
        'n_within': len(within_block_jsds),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
    }


# ============================================================
# Test A4: Cross-Block Category Discontinuity
# ============================================================

def test_a4(folio_data, rng):
    """A4: Category JSD across block boundaries > within-block paragraph boundaries."""
    print("\n=== A4: Cross-Block Category Discontinuity ===")

    cross_block_jsds = []
    within_block_jsds = []

    for fd in folio_data.values():
        paras = fd['all_paras']
        bi = fd['_block_indices']
        cf = fd['_category_fracs']

        def cat_vec(para_idx):
            return [cf[para_idx].get(cat, 0.0) for cat in CATEGORIES]

        # Cross-block boundaries
        for final_idx, initial_idx in fd['_cross_block_pairs']:
            v1 = cat_vec(final_idx)
            v2 = cat_vec(initial_idx)
            if sum(v1) > 0 and sum(v2) > 0:
                cross_block_jsds.append(jsd(v1, v2))

        # Within-block adjacent paragraph boundaries
        for blk_idxs in bi:
            if len(blk_idxs) < 2:
                continue
            for a in range(len(blk_idxs) - 1):
                v1 = cat_vec(blk_idxs[a])
                v2 = cat_vec(blk_idxs[a + 1])
                if sum(v1) > 0 and sum(v2) > 0:
                    within_block_jsds.append(jsd(v1, v2))

    if not cross_block_jsds or not within_block_jsds:
        print("  Insufficient data")
        return {'test': 'A4: Cross-Block Category Discontinuity', 'passed': False,
                'reason': 'insufficient data'}

    cross_mean = sum(cross_block_jsds) / len(cross_block_jsds)
    within_mean = sum(within_block_jsds) / len(within_block_jsds)
    U, z, p_mw = mann_whitney_u(cross_block_jsds, within_block_jsds)

    # Permutation
    observed_diff = cross_mean - within_mean
    all_jsds = cross_block_jsds + within_block_jsds
    n_cross = len(cross_block_jsds)
    null_diffs = []
    for _ in range(N_PERM):
        rng.shuffle(all_jsds)
        fake_cross = all_jsds[:n_cross]
        fake_within = all_jsds[n_cross:]
        if fake_cross and fake_within:
            null_diffs.append(sum(fake_cross) / len(fake_cross) -
                              sum(fake_within) / len(fake_within))
    perm_p = permutation_p(observed_diff, null_diffs, 'greater')

    print(f"  Cross-block category JSD: {cross_mean:.4f} (n={len(cross_block_jsds)})")
    print(f"  Within-block category JSD: {within_mean:.4f} (n={len(within_block_jsds)})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.6f}")
    print(f"  Permutation p: {perm_p:.4f}")

    passed = cross_mean > within_mean and p_mw < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'A4: Cross-Block Category Discontinuity',
        'passed': passed,
        'cross_mean': round(cross_mean, 4),
        'within_mean': round(within_mean, 4),
        'diff': round(observed_diff, 4),
        'n_cross': len(cross_block_jsds),
        'n_within': len(within_block_jsds),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
    }


# ============================================================
# Test B1: Block-Final -am Enrichment
# ============================================================

def test_b1(folio_data):
    """B1: Block-final paragraphs show higher -am rate than block-internal."""
    print("\n=== B1: Block-Final -am Enrichment ===")

    final_am = 0
    final_total = 0
    internal_am = 0
    internal_total = 0

    for fd in folio_data.values():
        paras = fd['all_paras']
        positions = fd['_block_positions']

        for i, p in enumerate(paras):
            pos = positions[i]
            if pos is None or pos == 'SOLE':
                continue

            is_am = p.termination_type == 'AM_SHUTDOWN'

            if pos == 'FINAL':
                final_total += 1
                if is_am:
                    final_am += 1
            elif pos in ('INTERNAL', 'INITIAL'):
                internal_total += 1
                if is_am:
                    internal_am += 1

    if final_total == 0 or internal_total == 0:
        print("  Insufficient data")
        return {'test': 'B1: Block-Final -am Enrichment', 'passed': False,
                'reason': 'insufficient data'}

    final_rate = final_am / final_total
    internal_rate = internal_am / internal_total

    # Fisher exact test
    table = [[final_am, final_total - final_am],
             [internal_am, internal_total - internal_am]]
    fisher_p = fisher_exact_2x2(table, alternative='greater')

    # Chi-squared for comparison
    chi2, chi2_p, df = chi2_test_matrix(table)

    enrich = final_rate / internal_rate if internal_rate > 0 else float('inf')

    print(f"  Block-final -am rate: {final_am}/{final_total} = {final_rate:.4f}")
    print(f"  Block-internal -am rate: {internal_am}/{internal_total} = {internal_rate:.4f}")
    print(f"  Enrichment ratio: {enrich:.2f}x")
    print(f"  Fisher exact p: {fisher_p:.6f}")
    print(f"  Chi-sq: {chi2:.2f}, p={chi2_p:.6f}")

    passed = final_rate > internal_rate and fisher_p < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'B1: Block-Final -am Enrichment',
        'passed': passed,
        'final_am': final_am,
        'final_total': final_total,
        'final_rate': round(final_rate, 4),
        'internal_am': internal_am,
        'internal_total': internal_total,
        'internal_rate': round(internal_rate, 4),
        'enrichment_ratio': round(enrich, 3) if internal_rate > 0 else None,
        'fisher_p': round(fisher_p, 6),
        'chi2': round(chi2, 3),
        'chi2_p': round(chi2_p, 6),
    }


# ============================================================
# Test B2: Block-Final Suffix Mode
# ============================================================

def test_b2(folio_data):
    """B2: Block-final paragraphs show different final suffix mode than block-internal."""
    print("\n=== B2: Block-Final Suffix Mode ===")

    final_modes = Counter()
    internal_modes = Counter()

    for fd in folio_data.values():
        paras = fd['all_paras']
        positions = fd['_block_positions']

        for i, p in enumerate(paras):
            pos = positions[i]
            if pos is None or pos == 'SOLE':
                continue

            if not p.suffix_mode_sequence:
                continue
            last_mode = p.suffix_mode_sequence[-1]
            if last_mode not in ('A', 'B'):
                continue

            if pos == 'FINAL':
                final_modes[last_mode] += 1
            elif pos in ('INTERNAL', 'INITIAL'):
                internal_modes[last_mode] += 1

    if not final_modes or not internal_modes:
        print("  Insufficient data")
        return {'test': 'B2: Block-Final Suffix Mode', 'passed': False,
                'reason': 'insufficient data'}

    table = [[final_modes.get('A', 0), final_modes.get('B', 0)],
             [internal_modes.get('A', 0), internal_modes.get('B', 0)]]

    chi2, p, df = chi2_test_matrix(table)

    final_total = sum(final_modes.values())
    internal_total = sum(internal_modes.values())
    final_b_pct = 100 * final_modes.get('B', 0) / final_total if final_total > 0 else 0
    internal_b_pct = 100 * internal_modes.get('B', 0) / internal_total if internal_total > 0 else 0

    print(f"  Block-final: Mode A={final_modes.get('A', 0)}, Mode B={final_modes.get('B', 0)} "
          f"(B rate: {final_b_pct:.1f}%)")
    print(f"  Block-internal: Mode A={internal_modes.get('A', 0)}, Mode B={internal_modes.get('B', 0)} "
          f"(B rate: {internal_b_pct:.1f}%)")
    print(f"  Chi-sq: {chi2:.2f}, df={df}, p={p:.6f}")

    passed = p < 0.01
    print(f"  PASS: {passed}")

    return {
        'test': 'B2: Block-Final Suffix Mode',
        'passed': passed,
        'final_modes': dict(final_modes),
        'internal_modes': dict(internal_modes),
        'final_b_pct': round(final_b_pct, 1),
        'internal_b_pct': round(internal_b_pct, 1),
        'chi2': round(chi2, 3),
        'p': round(p, 6),
        'df': df,
    }


# ============================================================
# Test B3: Block-Final Category Profile
# ============================================================

def test_b3(folio_data):
    """B3: Block-final paragraph tails show different category profile than block-internal tails."""
    print("\n=== B3: Block-Final Category Profile ===")

    final_cat = {cat: [] for cat in CATEGORIES}
    internal_cat = {cat: [] for cat in CATEGORIES}

    for fd in folio_data.values():
        paras = fd['all_paras']
        positions = fd['_block_positions']

        for i, p in enumerate(paras):
            pos = positions[i]
            if pos is None or pos == 'SOLE':
                continue
            if len(p.lines) < 2:
                continue

            # Tail = last 2 lines
            n_tail = min(2, len(p.lines))
            tail_lines = p.lines[-n_tail:]

            tail_cats = Counter()
            for la in tail_lines:
                if la.category_profile:
                    for cat, cnt in la.category_profile.items():
                        tail_cats[cat] += cnt

            total = sum(tail_cats.values())
            if total == 0:
                continue

            target = final_cat if pos == 'FINAL' else internal_cat
            for cat in CATEGORIES:
                target[cat].append(tail_cats.get(cat, 0) / total)

    results = {}
    sig_count = 0
    for cat in CATEGORIES:
        fvals = final_cat[cat]
        ivals = internal_cat[cat]
        if len(fvals) < 5 or len(ivals) < 5:
            continue
        f_mean = sum(fvals) / len(fvals)
        i_mean = sum(ivals) / len(ivals)
        U, z, p = mann_whitney_u(fvals, ivals)
        is_sig = p < 0.01
        if is_sig:
            sig_count += 1
        sig_str = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  {cat:14s}: final={f_mean:.4f} internal={i_mean:.4f} "
              f"z={z:.2f} p={p:.6f} {sig_str}")
        results[cat] = {
            'final_mean': round(f_mean, 4),
            'internal_mean': round(i_mean, 4),
            'mw_z': round(z, 3),
            'mw_p': round(p, 6),
            'sig': is_sig,
        }

    passed = sig_count >= 1
    n_final = len(final_cat[CATEGORIES[0]]) if final_cat[CATEGORIES[0]] else 0
    n_internal = len(internal_cat[CATEGORIES[0]]) if internal_cat[CATEGORIES[0]] else 0
    print(f"\n  Significant categories: {sig_count}/8")
    print(f"  n_final={n_final}, n_internal={n_internal}")
    print(f"  PASS: {passed}")

    return {
        'test': 'B3: Block-Final Category Profile',
        'passed': passed,
        'significant_categories': sig_count,
        'n_final': n_final,
        'n_internal': n_internal,
        'category_results': results,
    }


# ============================================================
# Test C1: Block-Level REGIME Homogeneity
# ============================================================

def test_c1(folio_data, rng):
    """C1: Are blocks within the same folio REGIME-homogeneous?"""
    print("\n=== C1: Block-Level REGIME Homogeneity ===")

    # Compute mean kernel profile per block
    folio_block_profiles = {}
    for folio, fd in folio_data.items():
        bi = fd['_block_indices']
        kf = fd['_kernel_fracs']

        profiles = []
        for blk_idxs in bi:
            if not blk_idxs:
                continue
            k_vals = [kf[pi]['k'] for pi in blk_idxs]
            h_vals = [kf[pi]['h'] for pi in blk_idxs]
            e_vals = [kf[pi]['e'] for pi in blk_idxs]
            profiles.append([
                sum(k_vals) / len(k_vals),
                sum(h_vals) / len(h_vals),
                sum(e_vals) / len(e_vals),
            ])

        if len(profiles) >= 2:
            folio_block_profiles[folio] = profiles

    if len(folio_block_profiles) < 5:
        print("  Insufficient data")
        return {'test': 'C1: Block-Level REGIME Homogeneity', 'passed': None,
                'reason': 'insufficient data'}

    # Flatten: all block profiles with integer folio labels
    all_profiles = []
    folio_labels = []  # integer labels for fast comparison
    folio_sizes = []
    folio_names = sorted(folio_block_profiles.keys())
    for fi, folio in enumerate(folio_names):
        profs = folio_block_profiles[folio]
        folio_sizes.append(len(profs))
        for prof in profs:
            all_profiles.append(prof)
            folio_labels.append(fi)

    N = len(all_profiles)
    print(f"  {N} blocks from {len(folio_names)} folios")

    # Pre-compute pairwise distance matrix (upper triangle)
    pair_i = []
    pair_j = []
    pair_d = []
    for i in range(N):
        for j in range(i + 1, N):
            d = 1.0 - cosine_sim(all_profiles[i], all_profiles[j])
            pair_i.append(i)
            pair_j.append(j)
            pair_d.append(d)

    n_pairs = len(pair_i)
    print(f"  {n_pairs} block pairs pre-computed")

    def compute_within_between_means(labels):
        w_sum, w_cnt = 0.0, 0
        b_sum, b_cnt = 0.0, 0
        for p in range(n_pairs):
            d = pair_d[p]
            if labels[pair_i[p]] == labels[pair_j[p]]:
                w_sum += d
                w_cnt += 1
            else:
                b_sum += d
                b_cnt += 1
        w_mean = w_sum / w_cnt if w_cnt > 0 else 0.0
        b_mean = b_sum / b_cnt if b_cnt > 0 else 0.0
        return w_mean, b_mean, w_cnt, b_cnt

    # Observed
    within_mean, between_mean, n_within, n_between = compute_within_between_means(folio_labels)
    observed_diff = within_mean - between_mean

    U, z, p_mw = mann_whitney_u(
        [pair_d[p] for p in range(n_pairs) if folio_labels[pair_i[p]] == folio_labels[pair_j[p]]],
        [pair_d[p] for p in range(n_pairs) if folio_labels[pair_i[p]] != folio_labels[pair_j[p]]]
    )

    # Permutation: shuffle folio labels
    null_diffs = []
    for _ in range(N_PERM):
        shuffled = list(folio_labels)
        rng.shuffle(shuffled)
        w_m, b_m, _, _ = compute_within_between_means(shuffled)
        null_diffs.append(w_m - b_m)

    perm_p = permutation_p(observed_diff, null_diffs, 'less')  # within < between = homogeneous

    is_homogeneous = within_mean < between_mean and perm_p < 0.01

    print(f"  Within-folio between-block distance: {within_mean:.4f} (n={n_within})")
    print(f"  Between-folio distance: {between_mean:.4f} (n={n_between})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.6f}")
    print(f"  Permutation p (homogeneity): {perm_p:.4f}")

    interpretation = "REGIME-HOMOGENEOUS" if is_homogeneous else "REGIME-HETEROGENEOUS"
    print(f"  Interpretation: {interpretation}")
    print(f"  (Both outcomes informative -- this is descriptive)")

    return {
        'test': 'C1: Block-Level REGIME Homogeneity',
        'passed': is_homogeneous,
        'within_folio_mean': round(within_mean, 4),
        'between_folio_mean': round(between_mean, 4),
        'diff': round(observed_diff, 4),
        'n_within': n_within,
        'n_between': n_between,
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
        'interpretation': interpretation,
        'n_folios': len(folio_block_profiles),
        'n_blocks': N,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 464: BLOCK_EXECUTION_CYCLE")
    print("=" * 80)

    rng = random.Random(SEED)

    folio_data = load_data()
    precompute_pairwise(folio_data)
    precompute_gallows_data(folio_data)
    precompute_block_positions(folio_data)

    results = {}

    # Group A: Cross-Block Transitions
    results['A1'] = test_a1(folio_data)
    results['A2'] = test_a2(folio_data)
    results['A3'] = test_a3(folio_data, rng)
    results['A4'] = test_a4(folio_data, rng)

    # Group B: Block-Final Signatures
    results['B1'] = test_b1(folio_data)
    results['B2'] = test_b2(folio_data)
    results['B3'] = test_b3(folio_data)

    # Group C: Architectural Completeness
    results['C1'] = test_c1(folio_data, rng)

    # Summary
    print(f"\n{'=' * 80}")
    passed_a = sum(1 for k in ['A1', 'A2', 'A3', 'A4'] if results[k].get('passed'))
    passed_b = sum(1 for k in ['B1', 'B2', 'B3'] if results[k].get('passed'))
    c1_result = results['C1'].get('interpretation', '?')
    total_passed = passed_a + passed_b + (1 if results['C1'].get('passed') else 0)

    print(f"SUMMARY: {total_passed}/8 tests passed")
    print(f"  Group A (Cross-Block Transitions): {passed_a}/4")
    print(f"  Group B (Block-Final Signatures): {passed_b}/3")
    print(f"  Group C (Architectural): {c1_result}")
    print()
    for k in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'C1']:
        r = results[k]
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} -- {r.get('test', k)}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'BLOCK_EXECUTION_CYCLE',
        'phase_number': 464,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'tests': results,
        'summary': {
            'tests_passed': total_passed,
            'tests_total': 8,
            'group_a_passed': passed_a,
            'group_b_passed': passed_b,
            'group_c_result': c1_result,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'block_execution_cycle.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
