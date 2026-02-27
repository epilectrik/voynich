#!/usr/bin/env python3
"""
Phase 467: MULTIPLEXED_PROCEDURE_TEST
=======================================
Tests whether block architecture reflects multiplexed procedures: one fire
regime with multiple vessels/batches, where block 0 documents full operational
context and later blocks skip shared setup.

4-test battery:
  M1: Block-0-unique category enrichment (primary discriminator)
  M2: Block size gradient (multiplexing vs parallel operation)
  M3: Asymmetric vocabulary containment (later blocks subset of block 0)
  M4: Kernel stability across blocks (consistency check: same fire)
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
    permutation_p, jaccard, jsd, cosine_sim, mann_whitney_u,
    normalize_profile, normal_cdf, chi2_sf
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

# Phase 466 (drift aggregates)
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'BLOCK_VOCABULARY_DRIFT' / 'scripts'))
from block_vocabulary_drift import precompute_block_aggregates, median

from scripts.voynich import CategoryClassifier

N_PERM = 1_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'


# ============================================================
# Helpers
# ============================================================

def cramers_v(chi2, n, k):
    """Cramér's V from chi-squared, sample size, and min(rows, cols)."""
    if n == 0 or k <= 1:
        return 0.0
    return math.sqrt(chi2 / (n * (k - 1)))


def chi2_contingency(observed):
    """Chi-squared test on a contingency table (list of lists).
    Returns (chi2, p, df)."""
    rows = len(observed)
    cols = len(observed[0]) if observed else 0
    n = sum(sum(row) for row in observed)
    if n == 0:
        return 0.0, 1.0, 0

    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[r][c] for r in range(rows)) for c in range(cols)]

    chi2 = 0.0
    for r in range(rows):
        for c in range(cols):
            expected = row_sums[r] * col_sums[c] / n
            if expected > 0:
                chi2 += (observed[r][c] - expected) ** 2 / expected

    df = (rows - 1) * (cols - 1)
    p = chi2_sf(chi2, df) if df > 0 else 1.0
    return chi2, p, df


def section_stratify(folio_data, test_func, min_blocks=2):
    """Run test_func on each section separately. Returns dict of section results."""
    sections = defaultdict(dict)
    for folio, fd in folio_data.items():
        sec = fd['section']
        sections[sec][folio] = fd

    results = {}
    for sec in sorted(sections):
        sec_data = sections[sec]
        eligible = sum(1 for fd in sec_data.values()
                       if len(fd['_block_indices']) >= min_blocks)
        if eligible >= 3:
            results[sec] = test_func(sec_data)
        else:
            results[sec] = {'n_folios': eligible, 'skipped': True}
    return results


# ============================================================
# Phase 467 Pre-computation
# ============================================================

def precompute_multiplexing(folio_data):
    """Compute vocabulary partitions and containment metrics per folio.

    For each folio with 2+ blocks:
      - block0_unique: MIDDLEs in block 0 only
      - shared: MIDDLEs in block 0 AND at least one later block
      - later_unique: MIDDLEs in some later block but NOT block 0
      - forward/reverse containment pairs
    """
    print("Pre-computing multiplexing data...")
    cc = CategoryClassifier()

    eligible_2 = 0
    total_b0_unique = 0
    total_shared = 0
    total_later_unique = 0

    for folio, fd in folio_data.items():
        bm = fd['_block_metrics']
        bi = fd['_block_indices']

        if len(bi) < 2:
            fd['_mux_data'] = None
            continue

        block0_middles = bm[0]['middle_set']

        # Union of all later blocks' MIDDLEs
        later_middles = set()
        for i in range(1, len(bm)):
            later_middles |= bm[i]['middle_set']

        b0_unique = block0_middles - later_middles
        shared = block0_middles & later_middles
        later_unique = later_middles - block0_middles

        # Classify each pool by category
        def categorize_pool(middles):
            counts = Counter()
            for m in middles:
                cat = cc.classify(m)
                if cat:
                    counts[cat] += 1
            return counts

        b0_unique_cats = categorize_pool(b0_unique)
        shared_cats = categorize_pool(shared)
        later_unique_cats = categorize_pool(later_unique)

        # Forward/reverse containment for each later block
        containment_pairs = []
        for i in range(1, len(bm)):
            block_i_middles = bm[i]['middle_set']
            intersection = block0_middles & block_i_middles
            if block0_middles:
                forward = len(intersection) / len(block0_middles)
            else:
                forward = 0.0
            if block_i_middles:
                reverse = len(intersection) / len(block_i_middles)
            else:
                reverse = 0.0
            containment_pairs.append({
                'block_ordinal': i,
                'forward': forward,
                'reverse': reverse,
                'asymmetry': reverse - forward,
            })

        # Per-block category profile (for M4)
        block_cat_profiles = []
        for blk_idx, blk_middles_data in enumerate(bm):
            cats = Counter()
            for m in blk_middles_data['middle_set']:
                cat = cc.classify(m)
                if cat:
                    cats[cat] += 1
            total = sum(cats.values())
            profile = {c: cats.get(c, 0) / total if total > 0 else 0.0
                       for c in CATEGORIES}
            block_cat_profiles.append(profile)

        # Per-block PREFIX profile (for M4)
        block_pfx_profiles = []
        pfx_keys = sorted(set().union(*(set(bm[i]['prefix_counts'].keys())
                                         for i in range(len(bm)))))
        for blk_data in bm:
            total = sum(blk_data['prefix_counts'].values())
            profile = {k: blk_data['prefix_counts'].get(k, 0) / total
                       if total > 0 else 0.0 for k in pfx_keys}
            block_pfx_profiles.append(profile)

        fd['_mux_data'] = {
            'block0_unique': b0_unique,
            'shared': shared,
            'later_unique': later_unique,
            'b0_unique_cats': b0_unique_cats,
            'shared_cats': shared_cats,
            'later_unique_cats': later_unique_cats,
            'containment_pairs': containment_pairs,
            'block_cat_profiles': block_cat_profiles,
            'block_pfx_profiles': block_pfx_profiles,
            'pfx_keys': pfx_keys,
        }

        eligible_2 += 1
        total_b0_unique += len(b0_unique)
        total_shared += len(shared)
        total_later_unique += len(later_unique)

    print(f"  Eligible folios (2+ blocks): {eligible_2}")
    print(f"  Block-0-unique MIDDLEs: {total_b0_unique}")
    print(f"  Shared MIDDLEs: {total_shared}")
    print(f"  Later-unique MIDDLEs: {total_later_unique}")


# ============================================================
# M1: Block-0-Unique Category Enrichment
# ============================================================

def test_m1(folio_data, rng):
    """M1: Are MIDDLEs unique to block 0 categorically distinct from shared?"""
    print("\n--- M1: Block-0-Unique Category Enrichment ---")

    def run_m1(data):
        # Pool category counts across folios
        pooled_b0u = Counter()
        pooled_shared = Counter()
        pooled_later = Counter()
        n_folios = 0

        for fd in data.values():
            mux = fd.get('_mux_data')
            if not mux:
                continue
            pooled_b0u += mux['b0_unique_cats']
            pooled_shared += mux['shared_cats']
            pooled_later += mux['later_unique_cats']
            n_folios += 1

        # Build contingency table: 3 pools x 8 categories
        cats = CATEGORIES
        table = []
        for pool_counts in [pooled_b0u, pooled_shared, pooled_later]:
            row = [pool_counts.get(c, 0) for c in cats]
            table.append(row)

        chi2, p, df = chi2_contingency(table)
        n_total = sum(sum(row) for row in table)
        v = cramers_v(chi2, n_total, min(3, len(cats)))

        # Enrichment ratios: block0_unique vs shared
        b0u_total = sum(pooled_b0u.values())
        shared_total = sum(pooled_shared.values())
        later_total = sum(pooled_later.values())

        enrichment = {}
        for c in cats:
            b0u_frac = pooled_b0u.get(c, 0) / b0u_total if b0u_total > 0 else 0
            shared_frac = pooled_shared.get(c, 0) / shared_total if shared_total > 0 else 0
            later_frac = pooled_later.get(c, 0) / later_total if later_total > 0 else 0
            enrichment[c] = {
                'block0_unique_frac': round(b0u_frac, 4),
                'shared_frac': round(shared_frac, 4),
                'later_unique_frac': round(later_frac, 4),
                'b0u_vs_shared': round(b0u_frac / shared_frac, 3) if shared_frac > 0 else None,
            }

        # STAGING + CONTAINMENT enrichment in block0_unique
        setup_cats = ['STAGING', 'CONTAINMENT']
        b0u_setup = sum(pooled_b0u.get(c, 0) for c in setup_cats) / b0u_total if b0u_total > 0 else 0
        shared_setup = sum(pooled_shared.get(c, 0) for c in setup_cats) / shared_total if shared_total > 0 else 0

        return {
            'n_folios': n_folios,
            'chi2': round(chi2, 2),
            'p': round(p, 6),
            'df': df,
            'cramers_v': round(v, 4),
            'n_b0_unique': b0u_total,
            'n_shared': shared_total,
            'n_later_unique': later_total,
            'enrichment': enrichment,
            'setup_frac_b0u': round(b0u_setup, 4),
            'setup_frac_shared': round(shared_setup, 4),
            'setup_enrichment_ratio': round(b0u_setup / shared_setup, 3) if shared_setup > 0 else None,
        }

    # Overall
    overall = run_m1(folio_data)

    # Section stratification
    sec_results = section_stratify(folio_data, run_m1, min_blocks=2)

    # Pass criteria: chi-sq p<0.01, V>0.10, holds in 2+ sections
    sections_passing = 0
    for sec, sr in sec_results.items():
        if not sr.get('skipped') and sr.get('p', 1.0) < 0.01 and sr.get('cramers_v', 0) > 0.10:
            sections_passing += 1

    passed = (overall['p'] < 0.01 and overall['cramers_v'] > 0.10
              and sections_passing >= 2)

    status = 'PASS' if passed else 'FAIL'
    print(f"  Overall: chi2={overall['chi2']}, p={overall['p']:.6f}, V={overall['cramers_v']}")
    print(f"  Pool sizes: b0_unique={overall['n_b0_unique']}, shared={overall['n_shared']}, later_unique={overall['n_later_unique']}")
    print(f"  STAGING+CONTAINMENT: b0_unique={overall['setup_frac_b0u']:.3f}, shared={overall['setup_frac_shared']:.3f}, ratio={overall['setup_enrichment_ratio']}")
    print(f"  Sections passing (p<0.01, V>0.10): {sections_passing}")
    for c in CATEGORIES:
        e = overall['enrichment'][c]
        ratio = e['b0u_vs_shared']
        r_str = f"{ratio:.2f}x" if ratio is not None else "N/A"
        print(f"    {c:14s}: b0u={e['block0_unique_frac']:.3f}, shared={e['shared_frac']:.3f}, later={e['later_unique_frac']:.3f}, b0u/shared={r_str}")
    print(f"  Result: {status}")

    return {
        'test': 'M1: Block-0-Unique Category Enrichment',
        'tier': 'T2-3 (structural with interpretive)',
        'passed': passed,
        'overall': overall,
        'section_breakdown': sec_results,
        'sections_passing': sections_passing,
    }


# ============================================================
# M2: Block Size Gradient
# ============================================================

def test_m2(folio_data, rng):
    """M2: Do later blocks have fewer tokens and paragraphs?"""
    print("\n--- M2: Block Size Gradient ---")

    token_lists = []
    para_lists = []
    section_data = defaultdict(lambda: {'token_rhos': [], 'para_rhos': []})

    n_folios = 0
    n_blocks = 0

    for folio, fd in folio_data.items():
        bi = fd['_block_indices']
        bm = fd['_block_metrics']
        if len(bi) < 3:
            continue

        ordinals = list(range(len(bi)))
        token_counts = [bm[i]['total_tokens'] for i in range(len(bi))]
        para_counts = [len(bi[i]) for i in range(len(bi))]

        token_lists.append((ordinals, token_counts))
        para_lists.append((ordinals, para_counts))
        n_folios += 1
        n_blocks += len(bi)

        sec = fd['section']
        if len(set(token_counts)) > 1:
            rt, _ = spearman_rho(ordinals, token_counts)
            section_data[sec]['token_rhos'].append(rt)
        if len(set(para_counts)) > 1:
            rp, _ = spearman_rho(ordinals, para_counts)
            section_data[sec]['para_rhos'].append(rp)

    # Permutation tests for token counts
    observed_rhos_tok = []
    valid_tok = []
    for ordinals, values in token_lists:
        if len(set(values)) <= 1:
            continue
        rho, _ = spearman_rho(ordinals, values)
        observed_rhos_tok.append(rho)
        valid_tok.append((ordinals, values))

    tok_med = median(observed_rhos_tok) if observed_rhos_tok else 0.0

    null_medians_tok = []
    for _ in range(N_PERM):
        perm_rhos = []
        for ordinals, values in valid_tok:
            shuffled = list(values)
            rng.shuffle(shuffled)
            if len(set(shuffled)) <= 1:
                continue
            r, _ = spearman_rho(ordinals, shuffled)
            perm_rhos.append(r)
        if perm_rhos:
            null_medians_tok.append(median(perm_rhos))

    tok_p = permutation_p(tok_med, null_medians_tok, 'less') if null_medians_tok else 1.0

    # Same for paragraph counts
    observed_rhos_para = []
    valid_para = []
    for ordinals, values in para_lists:
        if len(set(values)) <= 1:
            continue
        rho, _ = spearman_rho(ordinals, values)
        observed_rhos_para.append(rho)
        valid_para.append((ordinals, values))

    para_med = median(observed_rhos_para) if observed_rhos_para else 0.0

    null_medians_para = []
    for _ in range(N_PERM):
        perm_rhos = []
        for ordinals, values in valid_para:
            shuffled = list(values)
            rng.shuffle(shuffled)
            if len(set(shuffled)) <= 1:
                continue
            r, _ = spearman_rho(ordinals, shuffled)
            perm_rhos.append(r)
        if perm_rhos:
            null_medians_para.append(median(perm_rhos))

    para_p = permutation_p(para_med, null_medians_para, 'less') if null_medians_para else 1.0

    tok_decreasing = tok_med < -0.15 and tok_p < 0.01
    para_decreasing = para_med < -0.15 and para_p < 0.01
    passed = tok_decreasing  # Primary criterion is token count

    def direction_counts(rhos):
        return {
            'negative': sum(1 for r in rhos if r < 0),
            'positive': sum(1 for r in rhos if r > 0),
            'zero': sum(1 for r in rhos if r == 0),
        }

    sec_breakdown = {}
    for sec in sorted(section_data):
        sd = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios': len(sd['token_rhos']),
            'median_token_rho': round(median(sd['token_rhos']), 4),
            'median_para_rho': round(median(sd['para_rhos']), 4) if sd['para_rhos'] else None,
        }

    # Mean token count by ordinal (first 6 positions)
    tok_by_ordinal = defaultdict(list)
    for ordinals, values in token_lists:
        for o, v in zip(ordinals, values):
            tok_by_ordinal[o].append(v)
    mean_tok_by_ordinal = {}
    for o in sorted(tok_by_ordinal):
        vals = tok_by_ordinal[o]
        mean_tok_by_ordinal[o] = round(sum(vals) / len(vals), 1)

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}, Blocks: {n_blocks}")
    print(f"  Token count: median_rho={tok_med:.4f}, perm_p={tok_p:.4f} ({'decreasing' if tok_decreasing else 'NOT decreasing'})")
    print(f"  Para count: median_rho={para_med:.4f}, perm_p={para_p:.4f} ({'decreasing' if para_decreasing else 'NOT decreasing'})")
    if mean_tok_by_ordinal:
        tok_str = ', '.join(f"B{k}={v:.0f}" for k, v in list(mean_tok_by_ordinal.items())[:6])
        print(f"  Mean tokens by ordinal: {tok_str}...")
    print(f"  Result: {status}")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_folios']}, tok_rho={sb['median_token_rho']}, para_rho={sb['median_para_rho']}")

    return {
        'test': 'M2: Block Size Gradient',
        'tier': 'T2 (structural)',
        'passed': passed,
        'n_folios': n_folios,
        'n_blocks_total': n_blocks,
        'token_count': {
            'median_rho': round(tok_med, 4),
            'mean_rho': round(sum(observed_rhos_tok) / len(observed_rhos_tok), 4) if observed_rhos_tok else 0.0,
            'perm_p': round(tok_p, 4),
            'n_folios': len(observed_rhos_tok),
            'direction_count': direction_counts(observed_rhos_tok),
        },
        'para_count': {
            'median_rho': round(para_med, 4),
            'mean_rho': round(sum(observed_rhos_para) / len(observed_rhos_para), 4) if observed_rhos_para else 0.0,
            'perm_p': round(para_p, 4),
            'n_folios': len(observed_rhos_para),
            'direction_count': direction_counts(observed_rhos_para),
        },
        'tok_decreasing': tok_decreasing,
        'para_decreasing': para_decreasing,
        'mean_tokens_by_ordinal': mean_tok_by_ordinal,
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# M3: Asymmetric Vocabulary Containment
# ============================================================

def test_m3(folio_data, rng):
    """M3: Are later blocks vocabulary-subsets of block 0?"""
    print("\n--- M3: Asymmetric Vocabulary Containment ---")

    all_asymmetries = []
    all_forwards = []
    all_reverses = []
    section_data = defaultdict(lambda: {'asymmetries': []})

    # By ordinal position
    asym_by_ordinal = defaultdict(list)

    n_folios = 0
    n_pairs = 0

    for folio, fd in folio_data.items():
        mux = fd.get('_mux_data')
        if not mux:
            continue

        pairs = mux['containment_pairs']
        if not pairs:
            continue

        n_folios += 1
        sec = fd['section']

        for cp in pairs:
            all_asymmetries.append(cp['asymmetry'])
            all_forwards.append(cp['forward'])
            all_reverses.append(cp['reverse'])
            section_data[sec]['asymmetries'].append(cp['asymmetry'])
            asym_by_ordinal[cp['block_ordinal']].append(cp['asymmetry'])
            n_pairs += 1

    if not all_asymmetries:
        print("  No eligible pairs found")
        return {'test': 'M3: Asymmetric Vocabulary Containment', 'passed': False,
                'reason': 'no data'}

    observed_mean_asym = sum(all_asymmetries) / len(all_asymmetries)
    mean_forward = sum(all_forwards) / len(all_forwards)
    mean_reverse = sum(all_reverses) / len(all_reverses)

    # Permutation test: shuffle which block is "block 0" within each folio
    null_means = []
    for _ in range(N_PERM):
        perm_asymmetries = []
        for folio, fd in folio_data.items():
            mux = fd.get('_mux_data')
            if not mux:
                continue
            bm = fd['_block_metrics']
            n_blocks = len(bm)
            if n_blocks < 2:
                continue

            # Randomly pick a "reference" block instead of block 0
            ref_idx = rng.randint(0, n_blocks - 1)
            ref_middles = bm[ref_idx]['middle_set']

            for i in range(n_blocks):
                if i == ref_idx:
                    continue
                other_middles = bm[i]['middle_set']
                intersection = ref_middles & other_middles
                fwd = len(intersection) / len(ref_middles) if ref_middles else 0.0
                rev = len(intersection) / len(other_middles) if other_middles else 0.0
                perm_asymmetries.append(rev - fwd)

        if perm_asymmetries:
            null_means.append(sum(perm_asymmetries) / len(perm_asymmetries))

    perm_p = permutation_p(observed_mean_asym, null_means, 'greater') if null_means else 1.0

    passed = observed_mean_asym > 0.10 and perm_p < 0.01

    # Section breakdown
    sec_breakdown = {}
    for sec in sorted(section_data):
        sd = section_data[sec]
        a = sd['asymmetries']
        sec_breakdown[sec] = {
            'n_pairs': len(a),
            'mean_asymmetry': round(sum(a) / len(a), 4) if a else 0.0,
            'median_asymmetry': round(median(a), 4),
        }

    # Asymmetry by ordinal
    mean_asym_by_ordinal = {}
    for o in sorted(asym_by_ordinal):
        vals = asym_by_ordinal[o]
        mean_asym_by_ordinal[o] = round(sum(vals) / len(vals), 4)

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}, Pairs: {n_pairs}")
    print(f"  Mean forward (b0 in bN): {mean_forward:.4f}")
    print(f"  Mean reverse (bN in b0): {mean_reverse:.4f}")
    print(f"  Mean asymmetry (rev - fwd): {observed_mean_asym:.4f}, perm_p={perm_p:.4f}")
    print(f"  Result: {status}")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_pairs']}, mean_asym={sb['mean_asymmetry']}")

    return {
        'test': 'M3: Asymmetric Vocabulary Containment',
        'tier': 'T2 (structural)',
        'passed': passed,
        'n_folios': n_folios,
        'n_pairs': n_pairs,
        'mean_forward': round(mean_forward, 4),
        'mean_reverse': round(mean_reverse, 4),
        'mean_asymmetry': round(observed_mean_asym, 4),
        'median_asymmetry': round(median(all_asymmetries), 4),
        'perm_p': round(perm_p, 4),
        'asymmetry_by_ordinal': mean_asym_by_ordinal,
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# M4: Kernel Stability Across Blocks (consistency check)
# ============================================================

def test_m4(folio_data, rng):
    """M4: Is kernel k/h/e the most stable dimension across blocks?"""
    print("\n--- M4: Kernel Stability Across Blocks ---")

    kernel_variances = []
    category_variances = []
    prefix_variances = []
    section_data = defaultdict(lambda: {'kern': [], 'cat': [], 'pfx': []})

    n_folios = 0

    for folio, fd in folio_data.items():
        mux = fd.get('_mux_data')
        if not mux:
            continue
        bi = fd['_block_indices']
        if len(bi) < 3:
            continue

        drift = fd.get('_drift_blocks', [])
        valid_drift = [b for b in drift if b is not None]
        if len(valid_drift) < 3:
            continue

        # Kernel: mean pairwise cosine distance between block kernel vectors
        kern_vecs = [[b['k_frac'], b['h_frac'], b['e_frac']] for b in valid_drift]
        kern_dists = []
        for i in range(len(kern_vecs)):
            for j in range(i + 1, len(kern_vecs)):
                d = 1.0 - cosine_sim(kern_vecs[i], kern_vecs[j])
                kern_dists.append(d)
        kern_var = sum(kern_dists) / len(kern_dists) if kern_dists else 0.0

        # Category: mean pairwise JSD between block category profiles
        cat_profiles = mux['block_cat_profiles']
        cat_dists = []
        for i in range(len(cat_profiles)):
            for j in range(i + 1, len(cat_profiles)):
                p = [cat_profiles[i].get(c, 0.0) for c in CATEGORIES]
                q = [cat_profiles[j].get(c, 0.0) for c in CATEGORIES]
                # Ensure they sum to something
                sp, sq = sum(p), sum(q)
                if sp > 0 and sq > 0:
                    p = [x / sp for x in p]
                    q = [x / sq for x in q]
                    cat_dists.append(jsd(p, q))
        cat_var = sum(cat_dists) / len(cat_dists) if cat_dists else 0.0

        # PREFIX: mean pairwise JSD between block PREFIX profiles
        pfx_profiles = mux['block_pfx_profiles']
        pfx_keys = mux['pfx_keys']
        pfx_dists = []
        for i in range(len(pfx_profiles)):
            for j in range(i + 1, len(pfx_profiles)):
                p = [pfx_profiles[i].get(k, 0.0) for k in pfx_keys]
                q = [pfx_profiles[j].get(k, 0.0) for k in pfx_keys]
                sp, sq = sum(p), sum(q)
                if sp > 0 and sq > 0:
                    p = [x / sp for x in p]
                    q = [x / sq for x in q]
                    pfx_dists.append(jsd(p, q))
        pfx_var = sum(pfx_dists) / len(pfx_dists) if pfx_dists else 0.0

        kernel_variances.append(kern_var)
        category_variances.append(cat_var)
        prefix_variances.append(pfx_var)

        sec = fd['section']
        section_data[sec]['kern'].append(kern_var)
        section_data[sec]['cat'].append(cat_var)
        section_data[sec]['pfx'].append(pfx_var)

        n_folios += 1

    if not kernel_variances:
        print("  No eligible folios")
        return {'test': 'M4: Kernel Stability', 'passed': False, 'reason': 'no data'}

    # Paired tests: kernel vs category, kernel vs PREFIX
    # Use paired differences and sign test
    kern_vs_cat = [k - c for k, c in zip(kernel_variances, category_variances)]
    kern_vs_pfx = [k - p for k, p in zip(kernel_variances, prefix_variances)]

    # Wilcoxon-like: just test if kernel < category and kernel < PREFIX
    kern_lt_cat = sum(1 for d in kern_vs_cat if d < 0)
    kern_lt_pfx = sum(1 for d in kern_vs_pfx if d < 0)

    n = len(kernel_variances)
    # MW test on paired differences
    kc_u, kc_z, kc_p = mann_whitney_u(kernel_variances, category_variances)
    kp_u, kp_z, kp_p = mann_whitney_u(kernel_variances, prefix_variances)

    # Kernel is most stable if it has lower variance than both
    kern_lt_cat_sig = median(kernel_variances) < median(category_variances) and kc_p < 0.01
    kern_lt_pfx_sig = median(kernel_variances) < median(prefix_variances) and kp_p < 0.01
    passed = kern_lt_cat_sig and kern_lt_pfx_sig

    sec_breakdown = {}
    for sec in sorted(section_data):
        sd = section_data[sec]
        sec_breakdown[sec] = {
            'n_folios': len(sd['kern']),
            'median_kernel': round(median(sd['kern']), 5),
            'median_category': round(median(sd['cat']), 5),
            'median_prefix': round(median(sd['pfx']), 5),
        }

    status = 'PASS' if passed else 'FAIL'
    print(f"  Folios: {n_folios}")
    print(f"  Median kernel distance: {median(kernel_variances):.5f}")
    print(f"  Median category JSD: {median(category_variances):.5f}")
    print(f"  Median PREFIX JSD: {median(prefix_variances):.5f}")
    print(f"  Kernel < Category: {kern_lt_cat}/{n} folios, MW p={kc_p:.4f}")
    print(f"  Kernel < PREFIX: {kern_lt_pfx}/{n} folios, MW p={kp_p:.4f}")
    print(f"  Result: {status}")
    for sec in sorted(sec_breakdown):
        sb = sec_breakdown[sec]
        print(f"    Section {sec}: n={sb['n_folios']}, kern={sb['median_kernel']:.5f}, cat={sb['median_category']:.5f}, pfx={sb['median_prefix']:.5f}")

    return {
        'test': 'M4: Kernel Stability Across Blocks',
        'tier': 'T2 (consistency check)',
        'passed': passed,
        'n_folios': n_folios,
        'median_kernel_distance': round(median(kernel_variances), 5),
        'median_category_jsd': round(median(category_variances), 5),
        'median_prefix_jsd': round(median(prefix_variances), 5),
        'kernel_vs_category': {
            'kern_lower_count': kern_lt_cat,
            'total': n,
            'mw_z': round(kc_z, 4),
            'mw_p': round(kc_p, 4),
        },
        'kernel_vs_prefix': {
            'kern_lower_count': kern_lt_pfx,
            'total': n,
            'mw_z': round(kp_z, 4),
            'mw_p': round(kp_p, 4),
        },
        'section_breakdown': sec_breakdown,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 467: MULTIPLEXED_PROCEDURE_TEST")
    print("Testing multiplexed procedure model for block architecture")
    print("=" * 80)

    rng = random.Random(SEED)

    # Full precompute pipeline (Phases 462-466)
    folio_data = load_data()
    precompute_pairwise(folio_data)
    precompute_gallows_data(folio_data)
    precompute_block_positions(folio_data)
    precompute_block_metrics(folio_data)
    precompute_block_aggregates(folio_data)

    # Phase 467 pre-computation
    precompute_multiplexing(folio_data)

    # Section summary
    sec_counts = defaultdict(lambda: {'f2': 0, 'f3': 0})
    for fd in folio_data.values():
        sec = fd['section']
        if len(fd['_block_indices']) >= 2:
            sec_counts[sec]['f2'] += 1
        if len(fd['_block_indices']) >= 3:
            sec_counts[sec]['f3'] += 1
    print("\nEligible folios by section:")
    for sec in sorted(sec_counts):
        sc = sec_counts[sec]
        print(f"  Section {sec}: {sc['f2']} (2+ blocks), {sc['f3']} (3+ blocks)")

    # Run tests
    results = {}
    results['M1'] = test_m1(folio_data, rng)
    results['M2'] = test_m2(folio_data, rng)
    results['M3'] = test_m3(folio_data, rng)
    results['M4'] = test_m4(folio_data, rng)

    # Summary
    passed = sum(1 for r in results.values() if r.get('passed'))
    total = len(results)

    # Determine interpretation
    m1_pass = results['M1'].get('passed', False)
    m2_pass = results['M2'].get('passed', False)
    m3_pass = results['M3'].get('passed', False)

    if m1_pass and (m2_pass or m3_pass):
        interpretation = "MULTIPLEXING_SUPPORTED"
    elif m1_pass:
        interpretation = "PARTIAL_BLOCK0_SPECIAL"
    elif m2_pass:
        interpretation = "SIZE_GRADIENT_ONLY"
    elif passed >= 1:
        interpretation = "WEAK_SIGNAL"
    else:
        interpretation = "NOT_SUPPORTED"

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    for k in ['M1', 'M2', 'M3', 'M4']:
        r = results[k]
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} -- {r.get('test', k)}")
    print(f"\n  Interpretation: {interpretation}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'MULTIPLEXED_PROCEDURE_TEST',
        'phase_number': 467,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'tests': results,
        'summary': {
            'tests_passed': passed,
            'tests_total': total,
            'interpretation': interpretation,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'multiplexed_procedure_test.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
