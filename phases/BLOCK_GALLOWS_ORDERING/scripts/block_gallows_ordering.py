#!/usr/bin/env python3
"""
Phase 463: BLOCK_GALLOWS_ORDERING
=================================
Tests whether gallows letters encode paragraph operator roles within visual
text blocks, and whether blocks have internal ordered execution structure.

Two converging angles:
  1. Gallows as role markers: does gallows letter predict paragraph profile?
  2. Block-internal ordering: do paragraphs follow a sequence within blocks?

5-test battery:
  T1: Gallows-category association
  T2: Gallows-kernel association
  T3: Gallows ordering within blocks
  T4: Within-block position gradient
  T5: Block position in folio
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
    normal_cdf, chi2_sf, para_ht_density
)

N_PERM = 1_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
GALLOWS_LIST = sorted(GALLOWS)  # ['f', 'k', 'p', 't']
KERNEL_KEYS = ['k', 'h', 'e']


# ============================================================
# Additional statistical utilities
# ============================================================

def spearman_rho(x, y):
    """Spearman rank correlation coefficient."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    rx = _ranks(x)
    ry = _ranks(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rho = 1.0 - 6.0 * d2 / (n * (n * n - 1))
    # t-approximation for p-value
    if abs(rho) >= 1.0:
        return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho * rho))
    # Use normal approximation for large n
    p = 2.0 * normal_cdf(-abs(t_stat) / math.sqrt(1 + t_stat * t_stat / n))
    return rho, p


def _ranks(vals):
    """Assign ranks with tie handling (average rank)."""
    indexed = sorted(enumerate(vals), key=lambda t: t[1])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def chi2_test_matrix(observed_matrix):
    """Chi-squared test of independence for a 2D matrix.
    Returns (chi2, p, df)."""
    rows = len(observed_matrix)
    cols = len(observed_matrix[0]) if rows > 0 else 0
    row_totals = [sum(row) for row in observed_matrix]
    col_totals = [sum(observed_matrix[r][c] for r in range(rows)) for c in range(cols)]
    total = sum(row_totals)
    if total == 0:
        return 0.0, 1.0, 0
    chi2 = 0.0
    for r in range(rows):
        for c in range(cols):
            expected = row_totals[r] * col_totals[c] / total
            if expected > 0:
                chi2 += (observed_matrix[r][c] - expected) ** 2 / expected
    df = (rows - 1) * (cols - 1)
    if df <= 0:
        return chi2, 1.0, df
    p = chi2_sf(chi2, df)
    return chi2, p, df


# ============================================================
# Pre-computation for Phase 463
# ============================================================

def precompute_gallows_data(folio_data):
    """Extract per-paragraph gallows letter, kernel fractions, and category fractions.
    Stores results in folio_data entries."""
    print("Pre-computing gallows data...")

    for folio, fd in folio_data.items():
        paras = fd['all_paras']
        n = len(paras)

        gallows_letters = []  # gallows letter or None per paragraph
        kernel_fracs = []     # [k_frac, h_frac, e_frac] per paragraph
        category_fracs = []   # {cat: frac} per paragraph

        for p in paras:
            # Gallows letter
            gl = None
            if p.is_gallows_initial and p.boundary_token:
                first_char = p.boundary_token[0].lower()
                if first_char in GALLOWS:
                    gl = first_char
            gallows_letters.append(gl)

            # Kernel fractions
            kd = p.kernel_dist if p.kernel_dist else {}
            kt = sum(kd.values())
            if kt > 0:
                kernel_fracs.append({
                    'k': kd.get('k', 0) / kt,
                    'h': kd.get('h', 0) / kt,
                    'e': kd.get('e', 0) / kt,
                })
            else:
                kernel_fracs.append({'k': 0.0, 'h': 0.0, 'e': 0.0})

            # Category fractions
            cp = p.category_profile if p.category_profile else {}
            ct = sum(cp.values())
            if ct > 0:
                category_fracs.append({cat: cp.get(cat, 0) / ct for cat in CATEGORIES})
            else:
                category_fracs.append({cat: 0.0 for cat in CATEGORIES})

        fd['_gallows'] = gallows_letters
        fd['_kernel_fracs'] = kernel_fracs
        fd['_category_fracs'] = category_fracs

    # Report gallows distribution
    counts = Counter()
    for fd in folio_data.values():
        for gl in fd['_gallows']:
            if gl:
                counts[gl] += 1
    total_gl = sum(counts.values())
    print(f"  Gallows-initial paragraphs: {total_gl}")
    for g in GALLOWS_LIST:
        pct = 100 * counts[g] / total_gl if total_gl > 0 else 0
        print(f"    {g}: {counts[g]} ({pct:.1f}%)")


# ============================================================
# Test functions
# ============================================================

def test_t1(folio_data, rng):
    """T1: Gallows-Category Association."""
    print("\n=== T1: Gallows-Category Association ===")

    # Collect category fractions grouped by gallows letter
    gallows_cat = {g: {cat: [] for cat in CATEGORIES} for g in GALLOWS_LIST}

    for fd in folio_data.values():
        for i, p in enumerate(fd['all_paras']):
            gl = fd['_gallows'][i]
            if gl is None:
                continue
            cf = fd['_category_fracs'][i]
            for cat in CATEGORIES:
                gallows_cat[gl][cat].append(cf[cat])

    # KW test per category across gallows types
    kw_results = {}
    sig_count = 0
    for cat in CATEGORIES:
        groups = [gallows_cat[g][cat] for g in GALLOWS_LIST if gallows_cat[g][cat]]
        if len(groups) < 2:
            continue
        H, p = kruskal_wallis(groups)
        is_sig = p < 0.01
        if is_sig:
            sig_count += 1
        means = {g: round(sum(gallows_cat[g][cat]) / len(gallows_cat[g][cat]), 4)
                 if gallows_cat[g][cat] else 0.0 for g in GALLOWS_LIST}
        kw_results[cat] = {'H': round(H, 3), 'p': round(p, 6), 'sig': is_sig, 'means': means}
        sig_str = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  {cat:14s}: H={H:7.2f} p={p:.6f} {sig_str}  "
              f"f={means['f']:.3f} k={means['k']:.3f} p={means['p']:.3f} t={means['t']:.3f}")

    # Section-stratified check
    print("\n  Section-stratified significant categories:")
    section_confirmation = {}
    sections = defaultdict(list)
    for fd in folio_data.values():
        sections[fd['section']].append(fd)

    for cat in CATEGORIES:
        if not kw_results.get(cat, {}).get('sig'):
            continue
        confirmed_sections = []
        for sec in sorted(sections):
            sec_gallows_cat = {g: [] for g in GALLOWS_LIST}
            for fd in sections[sec]:
                for i, p in enumerate(fd['all_paras']):
                    gl = fd['_gallows'][i]
                    if gl is None:
                        continue
                    sec_gallows_cat[gl].append(fd['_category_fracs'][i][cat])
            groups = [sec_gallows_cat[g] for g in GALLOWS_LIST if sec_gallows_cat[g]]
            if len(groups) >= 2:
                H, p = kruskal_wallis(groups)
                if p < 0.05:
                    confirmed_sections.append(sec)
        section_confirmation[cat] = confirmed_sections
        if confirmed_sections:
            print(f"    {cat}: confirmed in {', '.join(confirmed_sections)}")

    # Count categories significant in >= 2 sections
    cats_multi_section = sum(1 for v in section_confirmation.values() if len(v) >= 2)
    passed = sig_count >= 3 and cats_multi_section >= 1
    print(f"\n  Significant categories (global): {sig_count}/8")
    print(f"  Categories confirmed in >=2 sections: {cats_multi_section}")
    print(f"  PASS: {passed}")

    # Sample sizes
    n_per_gallows = {g: len(gallows_cat[g][CATEGORIES[0]]) for g in GALLOWS_LIST}

    return {
        'test': 'T1: Gallows-Category Association',
        'tier': 'T2 (structural)',
        'passed': passed,
        'significant_categories': sig_count,
        'multi_section_categories': cats_multi_section,
        'n_per_gallows': n_per_gallows,
        'kw_results': kw_results,
        'section_confirmation': section_confirmation,
    }


def test_t2(folio_data, rng):
    """T2: Gallows-Kernel Association."""
    print("\n=== T2: Gallows-Kernel Association ===")

    gallows_kern = {g: {kk: [] for kk in KERNEL_KEYS} for g in GALLOWS_LIST}

    for fd in folio_data.values():
        for i, p in enumerate(fd['all_paras']):
            gl = fd['_gallows'][i]
            if gl is None:
                continue
            kf = fd['_kernel_fracs'][i]
            for kk in KERNEL_KEYS:
                gallows_kern[gl][kk].append(kf[kk])

    kw_results = {}
    sig_count = 0
    for kk in KERNEL_KEYS:
        groups = [gallows_kern[g][kk] for g in GALLOWS_LIST if gallows_kern[g][kk]]
        if len(groups) < 2:
            continue
        H, p = kruskal_wallis(groups)
        is_sig = p < 0.01
        if is_sig:
            sig_count += 1
        means = {g: round(sum(gallows_kern[g][kk]) / len(gallows_kern[g][kk]), 4)
                 if gallows_kern[g][kk] else 0.0 for g in GALLOWS_LIST}
        kw_results[kk] = {'H': round(H, 3), 'p': round(p, 6), 'sig': is_sig, 'means': means}
        sig_str = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  kernel-{kk}: H={H:7.2f} p={p:.6f} {sig_str}  "
              f"f={means['f']:.3f} k={means['k']:.3f} p={means['p']:.3f} t={means['t']:.3f}")

    # Section-stratified
    print("\n  Section-stratified:")
    sections = defaultdict(list)
    for fd in folio_data.values():
        sections[fd['section']].append(fd)

    section_results = {}
    for kk in KERNEL_KEYS:
        confirmed = []
        for sec in sorted(sections):
            sec_gallows_kern = {g: [] for g in GALLOWS_LIST}
            for fd in sections[sec]:
                for i, p in enumerate(fd['all_paras']):
                    gl = fd['_gallows'][i]
                    if gl is None:
                        continue
                    sec_gallows_kern[gl].append(fd['_kernel_fracs'][i][kk])
            groups = [sec_gallows_kern[g] for g in GALLOWS_LIST if sec_gallows_kern[g]]
            if len(groups) >= 2:
                H, p = kruskal_wallis(groups)
                if p < 0.05:
                    confirmed.append(sec)
        section_results[kk] = confirmed
        if confirmed:
            print(f"    kernel-{kk}: confirmed in {', '.join(confirmed)}")

    kerns_multi_section = sum(1 for v in section_results.values() if len(v) >= 2)
    passed = sig_count >= 1 and kerns_multi_section >= 1
    print(f"\n  Significant kernel fractions (global): {sig_count}/3")
    print(f"  Kernel fractions confirmed in >=2 sections: {kerns_multi_section}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T2: Gallows-Kernel Association',
        'tier': 'T2 (structural)',
        'passed': passed,
        'significant_kernels': sig_count,
        'multi_section_kernels': kerns_multi_section,
        'kw_results': kw_results,
        'section_results': section_results,
    }


def test_t3(folio_data, rng):
    """T3: Gallows Ordering Within Blocks."""
    print("\n=== T3: Gallows Ordering Within Blocks ===")

    # Collect gallows positions within blocks
    gallows_positions = {g: [] for g in GALLOWS_LIST}  # normalized [0,1] positions
    transition_counts = [[0] * 4 for _ in range(4)]  # 4x4 transition matrix
    g_idx = {g: i for i, g in enumerate(GALLOWS_LIST)}

    total_blocks = 0
    total_transitions = 0

    for fd in folio_data.values():
        bi = fd['_block_indices']
        gl = fd['_gallows']

        for blk_idxs in bi:
            # Get gallows sequence for this block
            block_gallows = []
            for pos, pi in enumerate(blk_idxs):
                if gl[pi] is not None:
                    block_gallows.append((pos, gl[pi]))

            if len(block_gallows) < 2:
                continue
            total_blocks += 1

            # Normalized positions
            max_pos = len(blk_idxs) - 1
            for pos, g in block_gallows:
                norm_pos = pos / max_pos if max_pos > 0 else 0.0
                gallows_positions[g].append(norm_pos)

            # Transitions (consecutive gallows-initial paragraphs)
            for a in range(len(block_gallows) - 1):
                gi = g_idx[block_gallows[a][1]]
                gj = g_idx[block_gallows[a + 1][1]]
                transition_counts[gi][gj] += 1
                total_transitions += 1

    # Mean position per gallows
    print(f"  Blocks with 2+ gallows-initial paragraphs: {total_blocks}")
    print(f"  Total within-block transitions: {total_transitions}")
    mean_positions = {}
    for g in GALLOWS_LIST:
        if gallows_positions[g]:
            mp = sum(gallows_positions[g]) / len(gallows_positions[g])
            mean_positions[g] = round(mp, 4)
            print(f"  {g}: mean position = {mp:.4f} (n={len(gallows_positions[g])})")
        else:
            mean_positions[g] = None

    # Test: k/f mean position < p/t mean position
    opener_pos = gallows_positions['k'] + gallows_positions['f']
    mode_pos = gallows_positions['p'] + gallows_positions['t']

    if opener_pos and mode_pos:
        opener_mean = sum(opener_pos) / len(opener_pos)
        mode_mean = sum(mode_pos) / len(mode_pos)
        U, z, p_mw = mann_whitney_u(mode_pos, opener_pos)  # mode > opener?
        print(f"\n  Opener (k/f) mean: {opener_mean:.4f} (n={len(opener_pos)})")
        print(f"  Mode (p/t) mean: {mode_mean:.4f} (n={len(mode_pos)})")
        print(f"  MW z={z:.2f} p={p_mw:.6f}")
    else:
        opener_mean, mode_mean, z, p_mw = 0, 0, 0, 1.0

    # Permutation test on opener vs mode position
    observed_diff = mode_mean - opener_mean
    null_diffs = []
    for _ in range(N_PERM):
        all_pos = opener_pos + mode_pos
        rng.shuffle(all_pos)
        fake_opener = all_pos[:len(opener_pos)]
        fake_mode = all_pos[len(opener_pos):]
        if fake_opener and fake_mode:
            null_diffs.append(sum(fake_mode) / len(fake_mode) -
                              sum(fake_opener) / len(fake_opener))
    perm_p_pos = permutation_p(observed_diff, null_diffs, 'greater')
    print(f"  Position permutation p: {perm_p_pos:.4f}")

    # Transition matrix chi-squared
    chi2, p_trans, df = chi2_test_matrix(transition_counts)
    print(f"\n  Transition matrix chi-sq: {chi2:.2f}, df={df}, p={p_trans:.6f}")
    print("  Transition matrix:")
    print(f"  {'':>6s} {'->f':>6s} {'->k':>6s} {'->p':>6s} {'->t':>6s}")
    for i, g in enumerate(GALLOWS_LIST):
        row = transition_counts[i]
        total_row = sum(row)
        pcts = [f"{100*row[j]/total_row:.0f}%" if total_row > 0 else "  -" for j in range(4)]
        print(f"  {g:>4s}-> {pcts[0]:>6s} {pcts[1]:>6s} {pcts[2]:>6s} {pcts[3]:>6s}  (n={total_row})")

    passed = (perm_p_pos < 0.01 and observed_diff > 0) or p_trans < 0.01
    print(f"\n  PASS: {passed}")

    return {
        'test': 'T3: Gallows Ordering Within Blocks',
        'tier': 'T2 (structural)',
        'passed': passed,
        'total_blocks_tested': total_blocks,
        'total_transitions': total_transitions,
        'mean_positions': mean_positions,
        'opener_mean': round(opener_mean, 4),
        'mode_mean': round(mode_mean, 4),
        'position_diff': round(observed_diff, 4),
        'position_mw_z': round(z, 3),
        'position_mw_p': round(p_mw, 6),
        'position_perm_p': round(perm_p_pos, 4),
        'transition_chi2': round(chi2, 3),
        'transition_p': round(p_trans, 6),
        'transition_df': df,
        'transition_matrix': transition_counts,
    }


def test_t4(folio_data, rng):
    """T4: Within-Block Position Gradient."""
    print("\n=== T4: Within-Block Position Gradient ===")

    # Collect (normalized_position, metric_value) pairs across all blocks
    metrics = {
        'THERMAL': [],
        'MONITORING': [],
        'MARKING': [],
        'OPERATION': [],
        'kernel_k': [],
        'kernel_e': [],
    }

    for fd in folio_data.values():
        bi = fd['_block_indices']
        cf = fd['_category_fracs']
        kf = fd['_kernel_fracs']

        for blk_idxs in bi:
            if len(blk_idxs) < 3:
                continue
            max_pos = len(blk_idxs) - 1
            for rank, pi in enumerate(blk_idxs):
                norm_pos = rank / max_pos
                metrics['THERMAL'].append((norm_pos, cf[pi]['THERMAL']))
                metrics['MONITORING'].append((norm_pos, cf[pi].get('MONITORING', 0.0)))
                metrics['MARKING'].append((norm_pos, cf[pi].get('MARKING', 0.0)))
                metrics['OPERATION'].append((norm_pos, cf[pi].get('OPERATION', 0.0)))
                metrics['kernel_k'].append((norm_pos, kf[pi]['k']))
                metrics['kernel_e'].append((norm_pos, kf[pi]['e']))

    results = {}
    sig_count = 0
    for name, pairs in metrics.items():
        if len(pairs) < 10:
            continue
        x = [p[0] for p in pairs]
        y = [p[1] for p in pairs]
        rho, p_val = spearman_rho(x, y)

        # Permutation test: shuffle positions within blocks
        null_rhos = []
        # Reconstruct block-level data for permutation
        block_data = []
        for fd in folio_data.values():
            for blk_idxs in fd['_block_indices']:
                if len(blk_idxs) < 3:
                    continue
                if name.startswith('kernel_'):
                    kk = name.split('_')[1]
                    vals = [fd['_kernel_fracs'][pi][kk] for pi in blk_idxs]
                else:
                    vals = [fd['_category_fracs'][pi].get(name, 0.0) for pi in blk_idxs]
                block_data.append(vals)

        for _ in range(N_PERM):
            shuf_x, shuf_y = [], []
            for vals in block_data:
                n = len(vals)
                max_p = n - 1
                shuffled = list(vals)
                rng.shuffle(shuffled)
                for rank, v in enumerate(shuffled):
                    shuf_x.append(rank / max_p)
                    shuf_y.append(v)
            if len(shuf_x) >= 10:
                sr, _ = spearman_rho(shuf_x, shuf_y)
                null_rhos.append(sr)

        # Two-sided: test if |rho| is extreme
        if rho > 0:
            perm_p = permutation_p(rho, null_rhos, 'greater')
        else:
            perm_p = permutation_p(rho, null_rhos, 'less')

        is_sig = perm_p < 0.01
        if is_sig:
            sig_count += 1
        sig_str = "***" if perm_p < 0.001 else "**" if perm_p < 0.01 else "*" if perm_p < 0.05 else "ns"
        print(f"  {name:14s}: rho={rho:+.4f} perm_p={perm_p:.4f} {sig_str} (n={len(pairs)})")
        results[name] = {
            'rho': round(rho, 4),
            'perm_p': round(perm_p, 4),
            'n': len(pairs),
            'sig': is_sig,
        }

    # Section-stratified for significant metrics
    sections = defaultdict(list)
    for fd in folio_data.values():
        sections[fd['section']].append(fd)

    section_confirmation = {}
    for name in results:
        if not results[name]['sig']:
            continue
        confirmed = []
        for sec in sorted(sections):
            pairs = []
            for fd in sections[sec]:
                for blk_idxs in fd['_block_indices']:
                    if len(blk_idxs) < 3:
                        continue
                    max_pos = len(blk_idxs) - 1
                    for rank, pi in enumerate(blk_idxs):
                        norm_pos = rank / max_pos
                        if name.startswith('kernel_'):
                            kk = name.split('_')[1]
                            val = fd['_kernel_fracs'][pi][kk]
                        else:
                            val = fd['_category_fracs'][pi].get(name, 0.0)
                        pairs.append((norm_pos, val))
            if len(pairs) >= 10:
                x = [p[0] for p in pairs]
                y = [p[1] for p in pairs]
                rho, _ = spearman_rho(x, y)
                # Check same direction as global
                global_dir = results[name]['rho'] > 0
                sec_dir = rho > 0
                if global_dir == sec_dir and abs(rho) > 0.05:
                    confirmed.append(sec)
        section_confirmation[name] = confirmed
        if confirmed:
            print(f"    {name}: same direction in {', '.join(confirmed)}")

    metrics_multi_section = sum(1 for v in section_confirmation.values() if len(v) >= 2)
    passed = sig_count >= 1 and metrics_multi_section >= 1
    print(f"\n  Significant gradients: {sig_count}/6")
    print(f"  Confirmed in >=2 sections: {metrics_multi_section}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T4: Within-Block Position Gradient',
        'tier': 'T2 (structural)',
        'passed': passed,
        'significant_gradients': sig_count,
        'multi_section_gradients': metrics_multi_section,
        'gradient_results': results,
        'section_confirmation': section_confirmation,
    }


def test_t5(folio_data, rng):
    """T5: Block Position in Folio."""
    print("\n=== T5: Block Position in Folio ===")

    first_block = {'kernel_k': [], 'kernel_e': [], 'kernel_h': [],
                   'ht_density': [], 'n_gallows': {g: 0 for g in GALLOWS_LIST}}
    last_block = {'kernel_k': [], 'kernel_e': [], 'kernel_h': [],
                  'ht_density': [], 'n_gallows': {g: 0 for g in GALLOWS_LIST}}

    # Also collect per-category for first vs last
    for cat in CATEGORIES:
        first_block[cat] = []
        last_block[cat] = []

    for fd in folio_data.values():
        bi = fd['_block_indices']
        if len(bi) < 2:
            continue

        for target, blk_idx in [('first', 0), ('last', -1)]:
            bucket = first_block if target == 'first' else last_block
            blk = bi[blk_idx]
            if not blk:
                continue

            # Aggregate metrics across paragraphs in this block
            k_fracs, h_fracs, e_fracs = [], [], []
            cat_fracs = {cat: [] for cat in CATEGORIES}
            ht_vals = []

            for pi in blk:
                kf = fd['_kernel_fracs'][pi]
                k_fracs.append(kf['k'])
                h_fracs.append(kf['h'])
                e_fracs.append(kf['e'])
                cf = fd['_category_fracs'][pi]
                for cat in CATEGORIES:
                    cat_fracs[cat].append(cf[cat])
                ht_vals.append(para_ht_density(fd['all_paras'][pi]))

                # Gallows count
                gl = fd['_gallows'][pi]
                if gl:
                    bucket['n_gallows'][gl] += 1

            if k_fracs:
                bucket['kernel_k'].append(sum(k_fracs) / len(k_fracs))
                bucket['kernel_h'].append(sum(h_fracs) / len(h_fracs))
                bucket['kernel_e'].append(sum(e_fracs) / len(e_fracs))
            if ht_vals:
                bucket['ht_density'].append(sum(ht_vals) / len(ht_vals))
            for cat in CATEGORIES:
                if cat_fracs[cat]:
                    bucket[cat].append(sum(cat_fracs[cat]) / len(cat_fracs[cat]))

    # Compare first vs last for each metric
    results = {}
    sig_count = 0
    test_metrics = ['kernel_k', 'kernel_h', 'kernel_e', 'ht_density'] + list(CATEGORIES)

    for metric in test_metrics:
        fvals = first_block[metric]
        lvals = last_block[metric]
        if len(fvals) < 5 or len(lvals) < 5:
            continue
        f_mean = sum(fvals) / len(fvals)
        l_mean = sum(lvals) / len(lvals)
        U, z, p = mann_whitney_u(fvals, lvals)
        is_sig = p < 0.01
        if is_sig:
            sig_count += 1
        sig_str = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  {metric:14s}: first={f_mean:.4f} last={l_mean:.4f} "
              f"z={z:.2f} p={p:.6f} {sig_str}")
        results[metric] = {
            'first_mean': round(f_mean, 4),
            'last_mean': round(l_mean, 4),
            'mw_z': round(z, 3),
            'mw_p': round(p, 6),
            'sig': is_sig,
        }

    # Gallows distribution: first vs last block
    print("\n  Gallows distribution:")
    print(f"  {'':>8s} {'first':>8s} {'last':>8s}")
    first_total = sum(first_block['n_gallows'].values())
    last_total = sum(last_block['n_gallows'].values())
    for g in GALLOWS_LIST:
        fc = first_block['n_gallows'][g]
        lc = last_block['n_gallows'][g]
        fp = 100 * fc / first_total if first_total > 0 else 0
        lp = 100 * lc / last_total if last_total > 0 else 0
        print(f"  {g:>6s}: {fp:6.1f}% {lp:6.1f}%")

    # k/f fraction in first vs last
    kf_first = (first_block['n_gallows']['k'] + first_block['n_gallows']['f'])
    kf_last = (last_block['n_gallows']['k'] + last_block['n_gallows']['f'])
    kf_first_pct = 100 * kf_first / first_total if first_total > 0 else 0
    kf_last_pct = 100 * kf_last / last_total if last_total > 0 else 0
    print(f"\n  k/f (opener) fraction: first={kf_first_pct:.1f}% last={kf_last_pct:.1f}%")

    passed = sig_count >= 1
    print(f"\n  Significant first-vs-last differences: {sig_count}/{len(results)}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T5: Block Position in Folio',
        'tier': 'T2 (structural)',
        'passed': passed,
        'significant_metrics': sig_count,
        'metric_results': results,
        'gallows_first': dict(first_block['n_gallows']),
        'gallows_last': dict(last_block['n_gallows']),
        'kf_first_pct': round(kf_first_pct, 1),
        'kf_last_pct': round(kf_last_pct, 1),
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 463: BLOCK_GALLOWS_ORDERING")
    print("=" * 80)

    rng = random.Random(SEED)

    # Load data (reuse Phase 462 pipeline)
    folio_data = load_data()
    precompute_pairwise(folio_data)  # Phase 462 pre-computation
    precompute_gallows_data(folio_data)  # Phase 463 pre-computation

    results = {}
    results['T1'] = test_t1(folio_data, rng)
    results['T2'] = test_t2(folio_data, rng)
    results['T3'] = test_t3(folio_data, rng)
    results['T4'] = test_t4(folio_data, rng)
    results['T5'] = test_t5(folio_data, rng)

    # Summary
    passed = sum(1 for r in results.values() if r.get('passed'))
    total = len(results)

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    for k, r in results.items():
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} -- {r.get('test', k)}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'BLOCK_GALLOWS_ORDERING',
        'phase_number': 463,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'tests': results,
        'summary': {
            'tests_passed': passed,
            'tests_total': total,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'block_gallows_ordering.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
