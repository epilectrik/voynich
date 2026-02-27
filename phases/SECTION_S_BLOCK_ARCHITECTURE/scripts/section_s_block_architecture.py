#!/usr/bin/env python3
"""
Phase 465: SECTION_S_BLOCK_ARCHITECTURE
========================================
Tests whether Section S (Stars/Recipe) blocks are parallel monitoring stations
rather than sequential processing stages.

Section S is anomalous: 12.4 blocks/folio, 1.17 paras/block, 49 tokens/block.
Hypothesis: blocks are independent, exchangeable monitoring snapshots.

6-test battery:
  S1: Within-folio block independence (MIDDLE Jaccard)
  S2: No block-position effect (ordinal correlation)
  S3: Gallows distribution uniformity (transition matrix)
  S4: Block-level profile homogeneity (category JSD)
  S5: REGIME homogeneity vs other sections (kernel distance)
  S6: lk distribution within Section S (ordinal + CV)
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
    normal_cdf, chi2_sf, jsd, cosine_sim, jaccard
)

# Reuse Phase 463 infrastructure
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import (
    precompute_gallows_data, chi2_test_matrix, GALLOWS_LIST, spearman_rho
)

# Reuse Phase 464 infrastructure
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_EXECUTION_CYCLE' / 'scripts'))
from block_execution_cycle import precompute_block_positions

from scripts.voynich import Morphology

N_PERM = 1_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
PREFIX_COMPARE = ['ch', 'sh', 'qo', 'lk']  # Prefixes to compare in S6


# ============================================================
# Phase 465 Pre-computation
# ============================================================

def precompute_block_metrics(folio_data):
    """Compute per-block MIDDLE sets, lk rates, and prefix counts."""
    print("Pre-computing per-block metrics...")
    morph = Morphology()

    for folio, fd in folio_data.items():
        paras = fd['all_paras']
        bi = fd['_block_indices']

        block_metrics = []
        for blk_idxs in bi:
            middle_set = set()
            prefix_counts = Counter()
            total_tokens = 0

            for pi in blk_idxs:
                p = paras[pi]
                for la in p.lines:
                    for tok in la.tokens:
                        total_tokens += 1
                        m = morph.extract(tok.word)
                        if m.middle:
                            middle_set.add(m.middle)
                        if m.prefix:
                            prefix_counts[m.prefix] += 1

            block_metrics.append({
                'middle_set': middle_set,
                'prefix_counts': prefix_counts,
                'total_tokens': total_tokens,
                'lk_rate': prefix_counts.get('lk', 0) / total_tokens if total_tokens > 0 else 0.0,
            })

        fd['_block_metrics'] = block_metrics

    # Report Section S stats
    s_blocks = 0
    s_tokens = 0
    for fd in folio_data.values():
        if fd['section'] == 'S':
            s_blocks += len(fd['_block_metrics'])
            s_tokens += sum(bm['total_tokens'] for bm in fd['_block_metrics'])
    print(f"  Section S: {s_blocks} blocks, {s_tokens} tokens")


# ============================================================
# S1: Within-Folio Block Independence
# ============================================================

def test_s1(folio_data):
    """S1: Cross-block MIDDLE Jaccard — S blocks more independent than non-S."""
    print("\n=== S1: Within-Folio Block Independence ===")

    s_jaccards = []
    non_s_jaccards = []

    for fd in folio_data.values():
        bi = fd['_block_indices']
        bm = fd['_block_metrics']
        is_s = fd['section'] == 'S'

        # Consecutive block pairs
        for b in range(len(bi) - 1):
            if not bi[b] or not bi[b + 1]:
                continue
            ms1 = bm[b]['middle_set']
            ms2 = bm[b + 1]['middle_set']
            if not ms1 or not ms2:
                continue
            j = jaccard(ms1, ms2)
            if is_s:
                s_jaccards.append(j)
            else:
                non_s_jaccards.append(j)

    if not s_jaccards or not non_s_jaccards:
        print("  Insufficient data")
        return {'test': 'S1: Within-Folio Block Independence', 'passed': False,
                'reason': 'insufficient data'}

    s_mean = sum(s_jaccards) / len(s_jaccards)
    ns_mean = sum(non_s_jaccards) / len(non_s_jaccards)
    U, z, p_mw = mann_whitney_u(s_jaccards, non_s_jaccards)

    print(f"  Section S cross-block MIDDLE Jaccard: {s_mean:.4f} (n={len(s_jaccards)})")
    print(f"  Non-S cross-block MIDDLE Jaccard: {ns_mean:.4f} (n={len(non_s_jaccards)})")
    print(f"  MW z={z:.2f} p={p_mw:.6f}")

    # Pass if S is significantly LOWER (more independent)
    passed = s_mean < ns_mean and p_mw < 0.01
    print(f"  PASS: {passed}")

    # Per-section breakdown
    section_means = defaultdict(list)
    for fd in folio_data.values():
        bi = fd['_block_indices']
        bm = fd['_block_metrics']
        sec = fd['section']
        for b in range(len(bi) - 1):
            if not bi[b] or not bi[b + 1]:
                continue
            ms1 = bm[b]['middle_set']
            ms2 = bm[b + 1]['middle_set']
            if ms1 and ms2:
                section_means[sec].append(jaccard(ms1, ms2))

    print("\n  Per-section cross-block Jaccard:")
    section_summary = {}
    for sec in sorted(section_means):
        vals = section_means[sec]
        m = sum(vals) / len(vals)
        section_summary[sec] = {'mean': round(m, 4), 'n': len(vals)}
        print(f"    {sec}: {m:.4f} (n={len(vals)})")

    return {
        'test': 'S1: Within-Folio Block Independence',
        'passed': passed,
        's_mean': round(s_mean, 4),
        'non_s_mean': round(ns_mean, 4),
        'n_s': len(s_jaccards),
        'n_non_s': len(non_s_jaccards),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'section_summary': section_summary,
    }


# ============================================================
# S2: No Block-Position Effect (Exchangeability)
# ============================================================

def test_s2(folio_data, rng):
    """S2: Block ordinal position does not predict any metric in Section S."""
    print("\n=== S2: No Block-Position Effect (Exchangeability) ===")

    # Collect per-block metrics with ordinal positions for S folios with 6+ blocks
    metric_names = ['kernel_k', 'kernel_h', 'kernel_e', 'lk_rate'] + list(CATEGORIES)
    block_data = []  # list of (folio, ordinal, metrics_dict)
    folio_blocks = []  # for permutation: list of (n_blocks, start_idx)

    for fd in folio_data.values():
        if fd['section'] != 'S':
            continue
        bi = fd['_block_indices']
        if len(bi) < 6:
            continue

        start_idx = len(block_data)
        for ordinal, blk_idxs in enumerate(bi):
            if not blk_idxs:
                continue
            # Aggregate metrics across paragraphs in block
            kf = fd['_kernel_fracs']
            cf = fd['_category_fracs']
            bm = fd['_block_metrics']

            k_vals = [kf[pi]['k'] for pi in blk_idxs]
            h_vals = [kf[pi]['h'] for pi in blk_idxs]
            e_vals = [kf[pi]['e'] for pi in blk_idxs]

            cat_vals = {cat: [cf[pi].get(cat, 0.0) for pi in blk_idxs] for cat in CATEGORIES}

            metrics = {
                'kernel_k': sum(k_vals) / len(k_vals),
                'kernel_h': sum(h_vals) / len(h_vals),
                'kernel_e': sum(e_vals) / len(e_vals),
                'lk_rate': bm[ordinal]['lk_rate'],
            }
            for cat in CATEGORIES:
                metrics[cat] = sum(cat_vals[cat]) / len(cat_vals[cat])

            norm_ordinal = ordinal / (len(bi) - 1) if len(bi) > 1 else 0.0
            block_data.append((fd['folio'], norm_ordinal, metrics))

        folio_blocks.append((len(bi), start_idx))

    if len(block_data) < 20:
        print("  Insufficient data")
        return {'test': 'S2: No Block-Position Effect', 'passed': False,
                'reason': 'insufficient data'}

    print(f"  {len(block_data)} blocks from {len(folio_blocks)} S folios with 6+ blocks")

    # Test each metric
    results = {}
    sig_count = 0
    ordinals = [bd[1] for bd in block_data]

    for name in metric_names:
        values = [bd[2][name] for bd in block_data]
        rho, p_rho = spearman_rho(ordinals, values)

        # Permutation test: shuffle ordinals within each folio
        null_rhos = []
        for _ in range(N_PERM):
            shuffled_ord = list(ordinals)
            for n_blks, start in folio_blocks:
                sub = shuffled_ord[start:start + n_blks]
                rng.shuffle(sub)
                shuffled_ord[start:start + n_blks] = sub
            sr, _ = spearman_rho(shuffled_ord, values)
            null_rhos.append(sr)

        if rho > 0:
            perm_p = permutation_p(rho, null_rhos, 'greater')
        else:
            perm_p = permutation_p(rho, null_rhos, 'less')

        is_sig = perm_p < 0.01
        if is_sig:
            sig_count += 1
        sig_str = "***" if perm_p < 0.001 else "**" if perm_p < 0.01 else "*" if perm_p < 0.05 else "ns"
        print(f"  {name:14s}: rho={rho:+.4f} perm_p={perm_p:.4f} {sig_str}")
        results[name] = {
            'rho': round(rho, 4),
            'perm_p': round(perm_p, 4),
            'sig': is_sig,
        }

    # Pass: NO significant correlations (parallel = exchangeable)
    passed = sig_count == 0
    print(f"\n  Significant ordinal correlations: {sig_count}/{len(metric_names)}")
    print(f"  PASS (exchangeable): {passed}")

    return {
        'test': 'S2: No Block-Position Effect',
        'passed': passed,
        'significant_count': sig_count,
        'total_metrics': len(metric_names),
        'n_blocks': len(block_data),
        'n_folios': len(folio_blocks),
        'metric_results': results,
    }


# ============================================================
# S3: Gallows Distribution Uniformity
# ============================================================

def test_s3(folio_data):
    """S3: Gallows types uniformly distributed across S blocks (no k/f/p->t pattern)."""
    print("\n=== S3: Gallows Distribution Uniformity ===")

    g_idx = {g: i for i, g in enumerate(GALLOWS_LIST)}

    # Section S transition matrix
    s_trans = [[0] * 4 for _ in range(4)]
    s_gallows_counts = Counter()

    # Non-S transition matrix
    ns_trans = [[0] * 4 for _ in range(4)]
    ns_gallows_counts = Counter()

    for fd in folio_data.values():
        bi = fd['_block_indices']
        gl = fd['_gallows']
        is_s = fd['section'] == 'S'
        trans = s_trans if is_s else ns_trans
        g_counts = s_gallows_counts if is_s else ns_gallows_counts

        # Build block-level gallows sequence
        block_gallows = []
        for blk_idxs in bi:
            # Use first paragraph's gallows (for single-para blocks, this IS the block)
            if blk_idxs and gl[blk_idxs[0]] is not None:
                block_gallows.append(gl[blk_idxs[0]])
                g_counts[gl[blk_idxs[0]]] += 1

        # Transitions between consecutive blocks
        for a in range(len(block_gallows) - 1):
            gi = g_idx[block_gallows[a]]
            gj = g_idx[block_gallows[a + 1]]
            trans[gi][gj] += 1

    # Chi-sq tests
    s_chi2, s_p, s_df = chi2_test_matrix(s_trans)
    ns_chi2, ns_p, ns_df = chi2_test_matrix(ns_trans)

    print("  Section S transition matrix:")
    print(f"  {'':>6s} {'->f':>6s} {'->k':>6s} {'->p':>6s} {'->t':>6s}")
    for i, g in enumerate(GALLOWS_LIST):
        row = s_trans[i]
        total_row = sum(row)
        pcts = [f"{100 * row[j] / total_row:.0f}%" if total_row > 0 else "  -" for j in range(4)]
        print(f"  {g:>4s}-> {pcts[0]:>6s} {pcts[1]:>6s} {pcts[2]:>6s} {pcts[3]:>6s}  (n={total_row})")
    print(f"  Chi-sq: {s_chi2:.2f}, df={s_df}, p={s_p:.6f}")

    print("\n  Non-S transition matrix:")
    print(f"  {'':>6s} {'->f':>6s} {'->k':>6s} {'->p':>6s} {'->t':>6s}")
    for i, g in enumerate(GALLOWS_LIST):
        row = ns_trans[i]
        total_row = sum(row)
        pcts = [f"{100 * row[j] / total_row:.0f}%" if total_row > 0 else "  -" for j in range(4)]
        print(f"  {g:>4s}-> {pcts[0]:>6s} {pcts[1]:>6s} {pcts[2]:>6s} {pcts[3]:>6s}  (n={total_row})")
    print(f"  Chi-sq: {ns_chi2:.2f}, df={ns_df}, p={ns_p:.6f}")

    # Gallows distribution comparison
    s_total = sum(s_gallows_counts.values())
    ns_total = sum(ns_gallows_counts.values())
    print("\n  Gallows distribution:")
    print(f"  {'':>6s} {'S':>8s} {'non-S':>8s}")
    dist_table = [[s_gallows_counts.get(g, 0) for g in GALLOWS_LIST],
                   [ns_gallows_counts.get(g, 0) for g in GALLOWS_LIST]]
    for i, g in enumerate(GALLOWS_LIST):
        s_pct = 100 * s_gallows_counts.get(g, 0) / s_total if s_total > 0 else 0
        ns_pct = 100 * ns_gallows_counts.get(g, 0) / ns_total if ns_total > 0 else 0
        print(f"  {g:>4s}: {s_pct:6.1f}% {ns_pct:6.1f}%")

    dist_chi2, dist_p, dist_df = chi2_test_matrix(dist_table)
    print(f"  Distribution chi-sq: {dist_chi2:.2f}, df={dist_df}, p={dist_p:.6f}")

    # Pass: S transition chi-sq NOT significant (uniform) while non-S IS significant
    passed = s_p > 0.05 and ns_p < 0.01
    print(f"\n  S transitions uniform (p>0.05): {s_p > 0.05}")
    print(f"  Non-S transitions structured (p<0.01): {ns_p < 0.01}")
    print(f"  PASS: {passed}")

    return {
        'test': 'S3: Gallows Distribution Uniformity',
        'passed': passed,
        's_transition_matrix': s_trans,
        'ns_transition_matrix': ns_trans,
        's_chi2': round(s_chi2, 3),
        's_p': round(s_p, 6),
        'ns_chi2': round(ns_chi2, 3),
        'ns_p': round(ns_p, 6),
        's_gallows_dist': dict(s_gallows_counts),
        'ns_gallows_dist': dict(ns_gallows_counts),
        'dist_chi2': round(dist_chi2, 3),
        'dist_p': round(dist_p, 6),
    }


# ============================================================
# S4: Block-Level Profile Homogeneity
# ============================================================

def test_s4(folio_data):
    """S4: S blocks within a folio more categorically similar than non-S blocks."""
    print("\n=== S4: Block-Level Profile Homogeneity ===")

    s_jsds = []
    non_s_jsds = []

    for fd in folio_data.values():
        bi = fd['_block_indices']
        cf = fd['_category_fracs']
        is_s = fd['section'] == 'S'

        if len(bi) < 2:
            continue

        # Compute mean category profile per block
        block_profiles = []
        for blk_idxs in bi:
            if not blk_idxs:
                continue
            cat_means = {}
            for cat in CATEGORIES:
                vals = [cf[pi].get(cat, 0.0) for pi in blk_idxs]
                cat_means[cat] = sum(vals) / len(vals)
            block_profiles.append([cat_means[cat] for cat in CATEGORIES])

        # Pairwise JSD between blocks within folio
        for a in range(len(block_profiles)):
            for b in range(a + 1, len(block_profiles)):
                if sum(block_profiles[a]) > 0 and sum(block_profiles[b]) > 0:
                    j = jsd(block_profiles[a], block_profiles[b])
                    if is_s:
                        s_jsds.append(j)
                    else:
                        non_s_jsds.append(j)

    if not s_jsds or not non_s_jsds:
        print("  Insufficient data")
        return {'test': 'S4: Block-Level Profile Homogeneity', 'passed': False,
                'reason': 'insufficient data'}

    s_mean = sum(s_jsds) / len(s_jsds)
    ns_mean = sum(non_s_jsds) / len(non_s_jsds)
    U, z, p_mw = mann_whitney_u(s_jsds, non_s_jsds)

    print(f"  Section S within-folio block JSD: {s_mean:.4f} (n={len(s_jsds)})")
    print(f"  Non-S within-folio block JSD: {ns_mean:.4f} (n={len(non_s_jsds)})")
    print(f"  MW z={z:.2f} p={p_mw:.6f}")

    # Per-section breakdown
    section_jsds = defaultdict(list)
    for fd in folio_data.values():
        bi = fd['_block_indices']
        cf = fd['_category_fracs']
        if len(bi) < 2:
            continue
        profiles = []
        for blk_idxs in bi:
            if not blk_idxs:
                continue
            cm = {cat: sum(cf[pi].get(cat, 0.0) for pi in blk_idxs) / len(blk_idxs)
                  for cat in CATEGORIES}
            profiles.append([cm[cat] for cat in CATEGORIES])
        for a in range(len(profiles)):
            for b in range(a + 1, len(profiles)):
                if sum(profiles[a]) > 0 and sum(profiles[b]) > 0:
                    section_jsds[fd['section']].append(jsd(profiles[a], profiles[b]))

    print("\n  Per-section within-folio block JSD:")
    section_summary = {}
    for sec in sorted(section_jsds):
        vals = section_jsds[sec]
        m = sum(vals) / len(vals)
        section_summary[sec] = {'mean': round(m, 4), 'n': len(vals)}
        print(f"    {sec}: {m:.4f} (n={len(vals)})")

    # Pass: S significantly LOWER (more homogeneous)
    passed = s_mean < ns_mean and p_mw < 0.01
    print(f"\n  PASS: {passed}")

    return {
        'test': 'S4: Block-Level Profile Homogeneity',
        'passed': passed,
        's_mean': round(s_mean, 4),
        'non_s_mean': round(ns_mean, 4),
        'n_s': len(s_jsds),
        'n_non_s': len(non_s_jsds),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'section_summary': section_summary,
    }


# ============================================================
# S5: REGIME Homogeneity vs Other Sections
# ============================================================

def test_s5(folio_data):
    """S5: Section S more REGIME-homogeneous (kernel distance) than other sections."""
    print("\n=== S5: REGIME Homogeneity vs Other Sections ===")

    # Compute within-folio between-block kernel distance per section
    section_dists = defaultdict(list)

    for fd in folio_data.values():
        bi = fd['_block_indices']
        kf = fd['_kernel_fracs']
        sec = fd['section']

        if len(bi) < 2:
            continue

        # Mean kernel profile per block
        block_profiles = []
        for blk_idxs in bi:
            if not blk_idxs:
                continue
            k_vals = [kf[pi]['k'] for pi in blk_idxs]
            h_vals = [kf[pi]['h'] for pi in blk_idxs]
            e_vals = [kf[pi]['e'] for pi in blk_idxs]
            block_profiles.append([
                sum(k_vals) / len(k_vals),
                sum(h_vals) / len(h_vals),
                sum(e_vals) / len(e_vals),
            ])

        # Pairwise kernel distance within folio
        for a in range(len(block_profiles)):
            for b in range(a + 1, len(block_profiles)):
                d = 1.0 - cosine_sim(block_profiles[a], block_profiles[b])
                section_dists[sec].append(d)

    # Report per section
    print("  Within-folio between-block kernel distance by section:")
    section_summary = {}
    for sec in sorted(section_dists):
        vals = section_dists[sec]
        m = sum(vals) / len(vals)
        section_summary[sec] = {'mean': round(m, 4), 'n': len(vals)}
        print(f"    {sec}: {m:.4f} (n={len(vals)})")

    # Compare S to each other section
    s_vals = section_dists.get('S', [])
    comparisons = {}
    sig_count = 0
    for sec in sorted(section_dists):
        if sec == 'S':
            continue
        other_vals = section_dists[sec]
        if len(other_vals) < 5:
            continue
        U, z, p = mann_whitney_u(s_vals, other_vals)
        is_sig = p < 0.01 and sum(s_vals) / len(s_vals) < sum(other_vals) / len(other_vals)
        if is_sig:
            sig_count += 1
        print(f"    S vs {sec}: MW z={z:.2f} p={p:.6f} {'***' if is_sig else 'ns'}")
        comparisons[sec] = {'mw_z': round(z, 3), 'mw_p': round(p, 6), 'sig': is_sig}

    # Pass: S significantly lower than >=2 other sections
    passed = sig_count >= 2
    print(f"\n  S significantly more homogeneous than {sig_count} sections")
    print(f"  PASS: {passed}")

    return {
        'test': 'S5: REGIME Homogeneity vs Other Sections',
        'passed': passed,
        'sig_count': sig_count,
        'section_summary': section_summary,
        'comparisons': comparisons,
    }


# ============================================================
# S6: lk Distribution Within Section S
# ============================================================

def test_s6(folio_data, rng):
    """S6: lk prefix uniformly distributed across block positions in Section S."""
    print("\n=== S6: lk Distribution Within Section S ===")

    # Collect lk rate per block with ordinal for S folios
    block_data = []  # (folio, norm_ordinal, lk_rate, prefix_rates)
    folio_blocks = []

    for fd in folio_data.values():
        if fd['section'] != 'S':
            continue
        bi = fd['_block_indices']
        bm = fd['_block_metrics']
        if len(bi) < 6:
            continue

        start_idx = len(block_data)
        for ordinal, blk_idxs in enumerate(bi):
            if not blk_idxs:
                continue
            metrics = bm[ordinal]
            total = metrics['total_tokens']
            prefix_rates = {}
            for pfx in PREFIX_COMPARE:
                prefix_rates[pfx] = metrics['prefix_counts'].get(pfx, 0) / total if total > 0 else 0.0
            norm_ord = ordinal / (len(bi) - 1) if len(bi) > 1 else 0.0
            block_data.append((fd['folio'], norm_ord, metrics['lk_rate'], prefix_rates))

        folio_blocks.append((len(bi), start_idx))

    if len(block_data) < 20:
        print("  Insufficient data")
        return {'test': 'S6: lk Distribution Within Section S', 'passed': False,
                'reason': 'insufficient data'}

    ordinals = [bd[1] for bd in block_data]
    lk_rates = [bd[2] for bd in block_data]

    # Spearman rho of lk rate vs ordinal
    rho, p_rho = spearman_rho(ordinals, lk_rates)

    # Permutation test
    null_rhos = []
    for _ in range(N_PERM):
        shuffled_ord = list(ordinals)
        for n_blks, start in folio_blocks:
            sub = shuffled_ord[start:start + n_blks]
            rng.shuffle(sub)
            shuffled_ord[start:start + n_blks] = sub
        sr, _ = spearman_rho(shuffled_ord, lk_rates)
        null_rhos.append(sr)

    if rho > 0:
        perm_p = permutation_p(rho, null_rhos, 'greater')
    else:
        perm_p = permutation_p(rho, null_rhos, 'less')

    print(f"  lk rate vs block ordinal: rho={rho:+.4f} perm_p={perm_p:.4f}")

    # CV of each prefix across blocks within S folios
    prefix_cvs = {}
    for pfx in PREFIX_COMPARE:
        all_rates = [bd[3][pfx] for bd in block_data]
        if all_rates:
            mean_r = sum(all_rates) / len(all_rates)
            if mean_r > 0:
                std_r = math.sqrt(sum((r - mean_r) ** 2 for r in all_rates) / len(all_rates))
                cv = std_r / mean_r
            else:
                cv = 0.0
            prefix_cvs[pfx] = round(cv, 4)
            print(f"  {pfx} rate: mean={mean_r:.4f} CV={cv:.4f}")

    # Per-folio CV of lk
    folio_cvs = []
    for fd in folio_data.values():
        if fd['section'] != 'S':
            continue
        bm = fd['_block_metrics']
        if len(bm) < 4:
            continue
        lk_vals = [m['lk_rate'] for m in bm]
        mean_lk = sum(lk_vals) / len(lk_vals)
        if mean_lk > 0:
            std_lk = math.sqrt(sum((v - mean_lk) ** 2 for v in lk_vals) / len(lk_vals))
            folio_cvs.append(std_lk / mean_lk)

    mean_folio_cv = sum(folio_cvs) / len(folio_cvs) if folio_cvs else 0.0
    print(f"\n  Mean within-folio lk CV: {mean_folio_cv:.4f} (n={len(folio_cvs)} folios)")

    # Pass: lk ordinal rho NOT significant (uniform across positions)
    rho_not_sig = perm_p > 0.05
    passed = rho_not_sig
    print(f"\n  lk ordinal correlation not significant (p>0.05): {rho_not_sig}")
    print(f"  PASS (uniform lk): {passed}")

    return {
        'test': 'S6: lk Distribution Within Section S',
        'passed': passed,
        'rho': round(rho, 4),
        'perm_p': round(perm_p, 4),
        'rho_significant': not rho_not_sig,
        'prefix_cvs': prefix_cvs,
        'mean_folio_lk_cv': round(mean_folio_cv, 4),
        'n_blocks': len(block_data),
        'n_folios': len(folio_blocks),
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 465: SECTION_S_BLOCK_ARCHITECTURE")
    print("=" * 80)

    rng = random.Random(SEED)

    folio_data = load_data()
    precompute_pairwise(folio_data)
    precompute_gallows_data(folio_data)
    precompute_block_positions(folio_data)
    precompute_block_metrics(folio_data)

    # Verify Section S folio count
    s_count = sum(1 for fd in folio_data.values() if fd['section'] == 'S')
    print(f"\nSection S folios: {s_count}")
    assert s_count >= 20, f"Expected ~23 S folios, got {s_count}"

    results = {}
    results['S1'] = test_s1(folio_data)
    results['S2'] = test_s2(folio_data, rng)
    results['S3'] = test_s3(folio_data)
    results['S4'] = test_s4(folio_data)
    results['S5'] = test_s5(folio_data)
    results['S6'] = test_s6(folio_data, rng)

    # Summary
    print(f"\n{'=' * 80}")
    total_passed = sum(1 for r in results.values() if r.get('passed'))
    print(f"SUMMARY: {total_passed}/6 tests passed")
    print()
    for k in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']:
        r = results[k]
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} -- {r.get('test', k)}")

    # Interpretation
    if total_passed >= 4:
        interpretation = "PARALLEL_STATIONS_CONFIRMED"
    elif total_passed >= 2:
        interpretation = "PARTIAL_PARALLEL"
    else:
        interpretation = "SEQUENTIAL_OR_MIXED"
    print(f"\n  Interpretation: {interpretation}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'SECTION_S_BLOCK_ARCHITECTURE',
        'phase_number': 465,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'section': 'S',
        'tests': results,
        'summary': {
            'tests_passed': total_passed,
            'tests_total': 6,
            'interpretation': interpretation,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'section_s_block_architecture.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
