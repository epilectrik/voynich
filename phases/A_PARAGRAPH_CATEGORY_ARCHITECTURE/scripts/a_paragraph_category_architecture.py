"""
Phase 468: A_PARAGRAPH_CATEGORY_ARCHITECTURE

Deep investigation of how the 8-category operational system organizes
Currier A paragraphs. Extends Phase 452's scattershot confirmation (C1263:
paragraphs specialize, d=12.5) into full architectural characterization.

Tests:
  A1: Paragraph dominant-category characterization
  A2: Category-based paragraph taxonomy
  A3: Within-paragraph category positional structure
  A4: Folio paragraph category organization

References: C1263, C850, C1039, C1040, C1041, C234, C240
"""

import json
import sys
import math
import time
import random
import functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Phase 452 (A data infrastructure)
sys.path.insert(0, str(ROOT / 'phases' / 'A_CATEGORY_SCATTERSHOT' / 'scripts'))
from a_category_scattershot import (
    load_all_data, build_category_map,
    GLOSS_TO_CATEGORY, ALL_CATEGORIES, ATOM_TO_CATEGORY
)

# Phase 462 (pure Python stats)
sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    jsd, mann_whitney_u, normal_cdf, normalize_profile, chi2_sf
)

# Phase 463 (Spearman rho)
sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "A_PARAGRAPH_CATEGORY_ARCHITECTURE" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42


# ================================================================
# PURE PYTHON ENTROPY (avoids numpy dependency)
# ================================================================
def entropy(counts):
    """Shannon entropy from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


# ================================================================
# PARAGRAPH BUILDER
# ================================================================
def build_a_paragraphs(a_tokens, mid_to_cat):
    """Build paragraph objects from A tokens using par_initial/par_final flags.

    Returns list of paragraph dicts, each with:
      folio, section, tokens, categories, cat_counts, cat_vector,
      n_categorized, dominant_cat, dominance_frac, pp_positions
    """
    paragraphs = []
    current = None

    for tok in a_tokens:
        if tok['par_initial']:
            # Close previous paragraph if open
            if current is not None:
                paragraphs.append(current)
            current = {
                'folio': tok['folio'],
                'section': tok['section'],
                'tokens': [],
            }
        if current is not None:
            current['tokens'].append(tok)
        if tok.get('par_final') and current is not None:
            paragraphs.append(current)
            current = None

    # Close any dangling paragraph
    if current is not None:
        paragraphs.append(current)

    # Enrich each paragraph with category data
    for para in paragraphs:
        # Collect categories of PP tokens in order
        pp_cats = []
        pp_positions = []  # (position_index, category) for positional analysis
        token_idx = 0
        for tok in para['tokens']:
            if tok['token_class'] == 'PP' and tok.get('category'):
                pp_cats.append(tok['category'])
                pp_positions.append((token_idx, tok['category']))
            token_idx += 1

        para['categories'] = pp_cats
        para['cat_counts'] = Counter(pp_cats)
        para['n_categorized'] = len(pp_cats)
        para['pp_positions'] = pp_positions

        # Category frequency vector (ALL_CATEGORIES order)
        total = len(pp_cats) if pp_cats else 1
        para['cat_vector'] = [para['cat_counts'].get(c, 0) / total
                              for c in ALL_CATEGORIES]

        # Dominant category
        if pp_cats:
            dom_cat, dom_count = para['cat_counts'].most_common(1)[0]
            para['dominant_cat'] = dom_cat
            para['dominance_frac'] = dom_count / len(pp_cats)
        else:
            para['dominant_cat'] = None
            para['dominance_frac'] = 0.0

    return paragraphs


# ================================================================
# TEST A1: Paragraph Dominant-Category Characterization
# ================================================================
def test_a1(paragraphs, rng):
    """How specialized are A paragraphs? What are the dominant categories?"""
    print("\n=== A1: Paragraph Dominant-Category Characterization ===")

    eligible = [p for p in paragraphs if p['n_categorized'] >= 3]
    print(f"  Eligible paragraphs (n_cat >= 3): {len(eligible)}")

    if len(eligible) < 10:
        return {'verdict': 'SKIP', 'reason': 'too few paragraphs'}

    # Observed statistics
    obs_dominance = [p['dominance_frac'] for p in eligible]
    obs_mean = sum(obs_dominance) / len(obs_dominance)
    obs_median = sorted(obs_dominance)[len(obs_dominance) // 2]

    # Distribution of dominant categories
    dom_dist = Counter(p['dominant_cat'] for p in eligible)
    dom_dist_pct = {cat: dom_dist.get(cat, 0) / len(eligible)
                    for cat in ALL_CATEGORIES}

    # Category frequency across all eligible paragraphs (baseline)
    all_cats = []
    for p in eligible:
        all_cats.extend(p['categories'])
    base_dist = Counter(all_cats)
    base_pct = {cat: base_dist.get(cat, 0) / len(all_cats) for cat in ALL_CATEGORIES}

    print(f"  Observed mean dominance: {obs_mean:.4f}")
    print(f"  Observed median dominance: {obs_median:.4f}")
    print(f"  Dominant category distribution:")
    for cat in ALL_CATEGORIES:
        print(f"    {cat}: {dom_dist.get(cat, 0)} ({dom_dist_pct[cat]:.1%})"
              f"  [base rate: {base_pct[cat]:.1%}]")

    # Null model: shuffle categories across paragraphs within section
    section_groups = defaultdict(list)
    for p in eligible:
        section_groups[p['section']].append(p)

    null_means = []
    for _ in range(N_PERM):
        perm_dominances = []
        for sec, sec_paras in section_groups.items():
            # Pool all categories in this section
            pool = []
            for p in sec_paras:
                pool.extend(p['categories'])
            rng.shuffle(pool)
            # Redistribute maintaining paragraph sizes
            idx = 0
            for p in sec_paras:
                n = p['n_categorized']
                chunk = pool[idx:idx + n]
                idx += n
                if chunk:
                    top_count = Counter(chunk).most_common(1)[0][1]
                    perm_dominances.append(top_count / len(chunk))
        null_means.append(sum(perm_dominances) / len(perm_dominances)
                          if perm_dominances else 0.0)

    p_val = sum(1 for nm in null_means if nm >= obs_mean) / N_PERM
    null_mean = sum(null_means) / len(null_means) if null_means else 0.0

    print(f"  Null mean dominance: {null_mean:.4f}")
    print(f"  Observed - Null: {obs_mean - null_mean:.4f}")
    print(f"  Permutation p: {p_val:.4f}")

    # Section stratification
    section_results = {}
    for sec in sorted(section_groups.keys()):
        sec_paras = section_groups[sec]
        sec_dom = [p['dominance_frac'] for p in sec_paras]
        sec_mean = sum(sec_dom) / len(sec_dom) if sec_dom else 0.0
        sec_dom_dist = Counter(p['dominant_cat'] for p in sec_paras)
        section_results[sec] = {
            'n_paragraphs': len(sec_paras),
            'mean_dominance': round(sec_mean, 4),
            'dominant_category_distribution': {
                cat: sec_dom_dist.get(cat, 0) for cat in ALL_CATEGORIES
            },
        }
        print(f"  Section {sec}: n={len(sec_paras)}, "
              f"mean_dom={sec_mean:.4f}")

    verdict = 'PASS' if p_val < 0.01 else 'FAIL'
    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_eligible': len(eligible),
        'observed_mean_dominance': round(obs_mean, 4),
        'observed_median_dominance': round(obs_median, 4),
        'null_mean_dominance': round(null_mean, 4),
        'excess_dominance': round(obs_mean - null_mean, 4),
        'perm_p': round(p_val, 4),
        'dominant_category_distribution': {
            cat: dom_dist.get(cat, 0) for cat in ALL_CATEGORIES
        },
        'dominant_category_pct': {
            cat: round(dom_dist_pct[cat], 4) for cat in ALL_CATEGORIES
        },
        'baseline_category_pct': {
            cat: round(base_pct[cat], 4) for cat in ALL_CATEGORIES
        },
        'section_breakdown': section_results,
    }


# ================================================================
# TEST A2: Category-Based Paragraph Taxonomy
# ================================================================
def test_a2(paragraphs, rng):
    """Do A paragraphs form distinct types based on category profiles?"""
    print("\n=== A2: Category-Based Paragraph Taxonomy ===")

    eligible = [p for p in paragraphs if p['n_categorized'] >= 3]
    print(f"  Eligible paragraphs: {len(eligible)}")

    if len(eligible) < 20:
        return {'verdict': 'SKIP', 'reason': 'too few paragraphs'}

    # Group by dominant category
    type_groups = defaultdict(list)
    for p in eligible:
        type_groups[p['dominant_cat']].append(p)

    n_types = len(type_groups)
    n_types_5plus = sum(1 for g in type_groups.values() if len(g) >= 5)
    print(f"  Observed types: {n_types} (with 5+ members: {n_types_5plus})")

    # Per-type profiles
    type_profiles = {}
    for cat in ALL_CATEGORIES:
        grp = type_groups.get(cat, [])
        if not grp:
            continue
        # Mean category vector
        mean_vec = [0.0] * len(ALL_CATEGORIES)
        for p in grp:
            for i, v in enumerate(p['cat_vector']):
                mean_vec[i] += v
        mean_vec = [v / len(grp) for v in mean_vec]

        # Top-2 secondary categories (excluding dominant)
        secondary = [(ALL_CATEGORIES[i], mean_vec[i])
                     for i in range(len(ALL_CATEGORIES))
                     if ALL_CATEGORIES[i] != cat]
        secondary.sort(key=lambda x: -x[1])
        top2_sec = secondary[:2]

        # Section distribution
        sec_dist = Counter(p['section'] for p in grp)

        type_profiles[cat] = {
            'count': len(grp),
            'mean_profile': {ALL_CATEGORIES[i]: round(mean_vec[i], 4)
                             for i in range(len(ALL_CATEGORIES))},
            'top2_secondary': [(s[0], round(s[1], 4)) for s in top2_sec],
            'section_distribution': dict(sec_dist),
        }
        print(f"  Type {cat}: n={len(grp)}, "
              f"sec={dict(sec_dist)}, "
              f"top2_sec={[s[0] for s in top2_sec]}")

    # Within-type vs between-type JSD
    within_jsds = []
    between_jsds = []
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            pi = eligible[i]['cat_vector']
            pj = eligible[j]['cat_vector']
            d = jsd(pi, pj)
            if eligible[i]['dominant_cat'] == eligible[j]['dominant_cat']:
                within_jsds.append(d)
            else:
                between_jsds.append(d)

    within_mean = sum(within_jsds) / len(within_jsds) if within_jsds else 0.0
    between_mean = sum(between_jsds) / len(between_jsds) if between_jsds else 0.0

    print(f"  Within-type JSD: mean={within_mean:.4f} (n={len(within_jsds)})")
    print(f"  Between-type JSD: mean={between_mean:.4f} (n={len(between_jsds)})")

    # Mann-Whitney test: within < between
    U, z, mw_p = mann_whitney_u(within_jsds, between_jsds)
    # We want within < between, so test if within ranks are lower
    # mann_whitney_u tests if x > y, but we want x < y, so invert
    # Actually, recompute: we want within_jsds < between_jsds
    # U measures how many within < between pairs, high U = within ranks higher
    # Use two-sided p from mann_whitney_u, then check direction
    direction = 'within < between' if within_mean < between_mean else 'within >= between'

    print(f"  MW U={U:.0f}, z={z:.2f}, p={mw_p:.6f}")
    print(f"  Direction: {direction}")

    # Null: shuffle dominant category assignments, recompute JSD distinctness
    dom_cats = [p['dominant_cat'] for p in eligible]
    null_diffs = []
    for _ in range(N_PERM):
        shuffled = dom_cats[:]
        rng.shuffle(shuffled)
        w_jsds = []
        b_jsds = []
        for i in range(len(eligible)):
            for j in range(i + 1, len(eligible)):
                d = jsd(eligible[i]['cat_vector'], eligible[j]['cat_vector'])
                if shuffled[i] == shuffled[j]:
                    w_jsds.append(d)
                else:
                    b_jsds.append(d)
        wm = sum(w_jsds) / len(w_jsds) if w_jsds else 0.0
        bm = sum(b_jsds) / len(b_jsds) if b_jsds else 0.0
        null_diffs.append(bm - wm)

    obs_diff = between_mean - within_mean
    perm_p = sum(1 for nd in null_diffs if nd >= obs_diff) / N_PERM
    null_diff_mean = sum(null_diffs) / len(null_diffs) if null_diffs else 0.0

    print(f"  Obs between-within gap: {obs_diff:.4f}")
    print(f"  Null mean gap: {null_diff_mean:.4f}")
    print(f"  Permutation p: {perm_p:.4f}")

    # Section stratification: compute within/between per section
    section_results = {}
    for sec in sorted(set(p['section'] for p in eligible)):
        sec_elig = [p for p in eligible if p['section'] == sec]
        if len(sec_elig) < 10:
            section_results[sec] = {'n': len(sec_elig), 'skipped': True}
            continue
        sw, sb = [], []
        for i in range(len(sec_elig)):
            for j in range(i + 1, len(sec_elig)):
                d = jsd(sec_elig[i]['cat_vector'], sec_elig[j]['cat_vector'])
                if sec_elig[i]['dominant_cat'] == sec_elig[j]['dominant_cat']:
                    sw.append(d)
                else:
                    sb.append(d)
        swm = sum(sw) / len(sw) if sw else 0.0
        sbm = sum(sb) / len(sb) if sb else 0.0
        section_results[sec] = {
            'n': len(sec_elig),
            'within_mean_jsd': round(swm, 4),
            'between_mean_jsd': round(sbm, 4),
            'gap': round(sbm - swm, 4),
            'n_types': len(set(p['dominant_cat'] for p in sec_elig)),
        }
        print(f"  Section {sec}: n={len(sec_elig)}, "
              f"w={swm:.4f}, b={sbm:.4f}, gap={sbm - swm:.4f}")

    pass_criteria = (mw_p < 0.01 and direction == 'within < between'
                     and n_types_5plus >= 4)
    verdict = 'PASS' if pass_criteria else 'FAIL'
    if mw_p < 0.01 and direction == 'within < between' and n_types_5plus < 4:
        verdict = 'WEAK'
    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_eligible': len(eligible),
        'n_types_observed': n_types,
        'n_types_5plus': n_types_5plus,
        'type_profiles': type_profiles,
        'within_type_mean_jsd': round(within_mean, 4),
        'between_type_mean_jsd': round(between_mean, 4),
        'jsd_gap': round(obs_diff, 4),
        'mw_U': round(U, 1),
        'mw_z': round(z, 3),
        'mw_p': round(mw_p, 6),
        'null_mean_gap': round(null_diff_mean, 4),
        'perm_p': round(perm_p, 4),
        'section_breakdown': section_results,
    }


# ================================================================
# TEST A3: Within-Paragraph Category Positional Structure
# ================================================================
def test_a3(paragraphs, rng):
    """Do categories have preferred positions within A paragraphs?"""
    print("\n=== A3: Within-Paragraph Category Positional Structure ===")

    eligible = [p for p in paragraphs if p['n_categorized'] >= 5]
    print(f"  Eligible paragraphs (n_cat >= 5): {len(eligible)}")

    if len(eligible) < 20:
        return {'verdict': 'SKIP', 'reason': 'too few paragraphs'}

    # Compute mean normalized position per category
    # Position = index among categorized PP tokens (0-based), normalized to [0,1]
    cat_positions = defaultdict(list)  # cat -> list of normalized positions
    for p in eligible:
        n = p['n_categorized']
        if n < 2:
            continue
        for idx, cat in enumerate(p['categories']):
            norm_pos = idx / (n - 1)  # 0.0 to 1.0
            cat_positions[cat].append(norm_pos)

    # Per-category statistics
    obs_mean_pos = {}
    obs_deviations = {}
    for cat in ALL_CATEGORIES:
        positions = cat_positions.get(cat, [])
        if len(positions) < 10:
            continue
        mean_pos = sum(positions) / len(positions)
        obs_mean_pos[cat] = mean_pos
        obs_deviations[cat] = abs(mean_pos - 0.5)

    print(f"  Category mean positions (0=start, 1=end):")
    for cat in ALL_CATEGORIES:
        if cat in obs_mean_pos:
            print(f"    {cat}: {obs_mean_pos[cat]:.4f} "
                  f"(dev={obs_deviations[cat]:.4f}, "
                  f"n={len(cat_positions[cat])})")

    # Permutation test: shuffle positions within each paragraph
    cat_null_means = defaultdict(list)  # cat -> list of N_PERM mean positions
    for _ in range(N_PERM):
        perm_positions = defaultdict(list)
        for p in eligible:
            n = p['n_categorized']
            if n < 2:
                continue
            cats = p['categories'][:]
            rng.shuffle(cats)
            for idx, cat in enumerate(cats):
                norm_pos = idx / (n - 1)
                perm_positions[cat].append(norm_pos)
        for cat in ALL_CATEGORIES:
            if cat in obs_mean_pos:
                pp = perm_positions.get(cat, [])
                if pp:
                    cat_null_means[cat].append(sum(pp) / len(pp))

    # P-values (two-sided)
    cat_p_values = {}
    for cat in obs_mean_pos:
        nulls = cat_null_means[cat]
        obs = obs_mean_pos[cat]
        # Two-sided: fraction of null means as or more extreme than observed
        p_high = sum(1 for n in nulls if n >= obs) / len(nulls)
        p_low = sum(1 for n in nulls if n <= obs) / len(nulls)
        cat_p_values[cat] = min(p_high, p_low) * 2  # two-sided
        cat_p_values[cat] = min(cat_p_values[cat], 1.0)

    print(f"  Permutation p-values (two-sided):")
    for cat in ALL_CATEGORIES:
        if cat in cat_p_values:
            sig = " ***" if cat_p_values[cat] < 0.01 and obs_deviations[cat] > 0.03 else ""
            print(f"    {cat}: p={cat_p_values[cat]:.4f}{sig}")

    # First-token and last-token category distributions
    first_cats = Counter()
    last_cats = Counter()
    for p in eligible:
        if p['categories']:
            first_cats[p['categories'][0]] += 1
            last_cats[p['categories'][-1]] += 1

    first_total = sum(first_cats.values())
    last_total = sum(last_cats.values())
    first_pct = {cat: first_cats.get(cat, 0) / first_total if first_total else 0
                 for cat in ALL_CATEGORIES}
    last_pct = {cat: last_cats.get(cat, 0) / last_total if last_total else 0
                for cat in ALL_CATEGORIES}

    print(f"  First-token category distribution:")
    for cat in ALL_CATEGORIES:
        if first_pct[cat] > 0.01:
            print(f"    {cat}: {first_pct[cat]:.1%}")
    print(f"  Last-token category distribution:")
    for cat in ALL_CATEGORIES:
        if last_pct[cat] > 0.01:
            print(f"    {cat}: {last_pct[cat]:.1%}")

    # Count categories passing threshold
    sig_cats = [cat for cat in obs_mean_pos
                if cat_p_values.get(cat, 1.0) < 0.01
                and obs_deviations.get(cat, 0.0) > 0.03]

    if len(sig_cats) >= 2:
        verdict = 'PASS_ORDERING'
    elif all(obs_deviations.get(cat, 0.0) <= 0.03 for cat in obs_mean_pos):
        verdict = 'PASS_NO_ORDERING'
    else:
        verdict = 'WEAK'

    print(f"  Significant categories (p<0.01, dev>0.03): {sig_cats}")
    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_eligible': len(eligible),
        'category_positions': {
            cat: {
                'mean_position': round(obs_mean_pos[cat], 4),
                'deviation_from_center': round(obs_deviations[cat], 4),
                'perm_p': round(cat_p_values[cat], 4),
                'n_tokens': len(cat_positions[cat]),
            }
            for cat in obs_mean_pos
        },
        'significant_categories': sig_cats,
        'first_token_distribution': {
            cat: round(first_pct[cat], 4) for cat in ALL_CATEGORIES
        },
        'last_token_distribution': {
            cat: round(last_pct[cat], 4) for cat in ALL_CATEGORIES
        },
    }


# ================================================================
# TEST A4: Folio Paragraph Category Organization
# ================================================================
def test_a4(paragraphs, rng):
    """Are paragraph category types organized within folios?"""
    print("\n=== A4: Folio Paragraph Category Organization ===")

    eligible = [p for p in paragraphs if p['n_categorized'] >= 3]

    # Group paragraphs by folio, preserving order
    folio_paras = defaultdict(list)
    for p in eligible:
        folio_paras[p['folio']].append(p)

    # Filter to folios with 3+ eligible paragraphs
    multi_folios = {f: ps for f, ps in folio_paras.items() if len(ps) >= 3}
    print(f"  Eligible paragraphs: {len(eligible)}")
    print(f"  Folios with 3+ eligible paragraphs: {len(multi_folios)}")

    if len(multi_folios) < 5:
        return {'verdict': 'SKIP', 'reason': 'too few multi-paragraph folios'}

    # Consecutive vs random-pair JSD
    consec_jsds = []
    random_jsds = []
    for f, ps in multi_folios.items():
        n = len(ps)
        # Consecutive pairs
        for i in range(n - 1):
            d = jsd(ps[i]['cat_vector'], ps[i + 1]['cat_vector'])
            consec_jsds.append(d)
        # Non-consecutive pairs
        for i in range(n):
            for j in range(i + 2, n):
                d = jsd(ps[i]['cat_vector'], ps[j]['cat_vector'])
                random_jsds.append(d)

    consec_mean = sum(consec_jsds) / len(consec_jsds) if consec_jsds else 0.0
    random_mean = sum(random_jsds) / len(random_jsds) if random_jsds else 0.0

    print(f"  Consecutive JSD: mean={consec_mean:.4f} (n={len(consec_jsds)})")
    print(f"  Non-consecutive JSD: mean={random_mean:.4f} (n={len(random_jsds)})")

    # MW test: consecutive vs non-consecutive
    U, z, mw_p = mann_whitney_u(consec_jsds, random_jsds)
    direction = ('consec < non-consec' if consec_mean < random_mean
                 else 'consec >= non-consec')
    print(f"  MW U={U:.0f}, z={z:.2f}, p={mw_p:.6f}")
    print(f"  Direction: {direction}")

    # Permutation test: shuffle paragraph order within each folio
    obs_diff = consec_mean - random_mean
    null_diffs = []
    for _ in range(N_PERM):
        perm_consec = []
        perm_random = []
        for f, ps in multi_folios.items():
            shuffled = ps[:]
            rng.shuffle(shuffled)
            n = len(shuffled)
            for i in range(n - 1):
                d = jsd(shuffled[i]['cat_vector'], shuffled[i + 1]['cat_vector'])
                perm_consec.append(d)
            for i in range(n):
                for j in range(i + 2, n):
                    d = jsd(shuffled[i]['cat_vector'], shuffled[j]['cat_vector'])
                    perm_random.append(d)
        pc = sum(perm_consec) / len(perm_consec) if perm_consec else 0.0
        pr = sum(perm_random) / len(perm_random) if perm_random else 0.0
        null_diffs.append(pc - pr)

    perm_p = sum(1 for nd in null_diffs if nd <= obs_diff) / N_PERM
    null_mean_diff = sum(null_diffs) / len(null_diffs) if null_diffs else 0.0

    print(f"  Obs consec-random gap: {obs_diff:.4f}")
    print(f"  Null mean gap: {null_mean_diff:.4f}")
    print(f"  Perm p (consec < random): {perm_p:.4f}")

    # Paragraph position vs entropy (Spearman rho)
    position_entropy_rhos = []
    for f, ps in multi_folios.items():
        positions = list(range(len(ps)))
        entropies = [entropy(p['cat_counts']) for p in ps]
        rho, rho_p = spearman_rho(positions, entropies)
        position_entropy_rhos.append(rho)

    median_rho = sorted(position_entropy_rhos)[len(position_entropy_rhos) // 2]
    mean_rho = (sum(position_entropy_rhos) / len(position_entropy_rhos)
                if position_entropy_rhos else 0.0)
    print(f"  Position vs entropy rho: mean={mean_rho:.4f}, median={median_rho:.4f}")

    # First-paragraph distinctness (a la C1332 block-0 marking enrichment)
    first_cats = Counter()
    rest_cats = Counter()
    for f, ps in multi_folios.items():
        for cat in ps[0]['categories']:
            first_cats[cat] += 1
        for p in ps[1:]:
            for cat in p['categories']:
                rest_cats[cat] += 1

    first_vec = normalize_profile(first_cats, ALL_CATEGORIES)
    rest_vec = normalize_profile(rest_cats, ALL_CATEGORIES)
    first_rest_jsd = jsd(first_vec, rest_vec)

    # Enrichment ratios
    enrichment = {}
    for i, cat in enumerate(ALL_CATEGORIES):
        if rest_vec[i] > 0:
            enrichment[cat] = round(first_vec[i] / rest_vec[i], 3)
        else:
            enrichment[cat] = 0.0 if first_vec[i] == 0 else float('inf')

    print(f"  First-paragraph vs rest JSD: {first_rest_jsd:.4f}")
    print(f"  First-paragraph enrichment ratios:")
    for cat in ALL_CATEGORIES:
        if enrichment[cat] != 0.0:
            marker = " ***" if enrichment[cat] > 1.5 or enrichment[cat] < 0.67 else ""
            print(f"    {cat}: {enrichment[cat]:.3f}x{marker}")

    # Section stratification
    section_results = {}
    for sec in sorted(set(p['section'] for p in eligible)):
        sec_folios = {f: ps for f, ps in multi_folios.items()
                      if ps[0]['section'] == sec}
        if len(sec_folios) < 3:
            section_results[sec] = {'n_folios': len(sec_folios), 'skipped': True}
            continue
        sc, sr = [], []
        for f, ps in sec_folios.items():
            for i in range(len(ps) - 1):
                sc.append(jsd(ps[i]['cat_vector'], ps[i + 1]['cat_vector']))
            for i in range(len(ps)):
                for j in range(i + 2, len(ps)):
                    sr.append(jsd(ps[i]['cat_vector'], ps[j]['cat_vector']))
        scm = sum(sc) / len(sc) if sc else 0.0
        srm = sum(sr) / len(sr) if sr else 0.0
        section_results[sec] = {
            'n_folios': len(sec_folios),
            'consec_mean_jsd': round(scm, 4),
            'random_mean_jsd': round(srm, 4),
            'gap': round(scm - srm, 4),
        }
        print(f"  Section {sec}: n_folios={len(sec_folios)}, "
              f"consec={scm:.4f}, random={srm:.4f}")

    verdict = 'PASS' if perm_p < 0.01 else 'FAIL'
    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_folios': len(multi_folios),
        'n_paragraphs': sum(len(ps) for ps in multi_folios.values()),
        'consec_mean_jsd': round(consec_mean, 4),
        'random_mean_jsd': round(random_mean, 4),
        'consec_random_gap': round(obs_diff, 4),
        'mw_U': round(U, 1),
        'mw_z': round(z, 3),
        'mw_p': round(mw_p, 6),
        'perm_p': round(perm_p, 4),
        'null_mean_gap': round(null_mean_diff, 4),
        'position_entropy_rho_mean': round(mean_rho, 4),
        'position_entropy_rho_median': round(median_rho, 4),
        'first_paragraph': {
            'first_rest_jsd': round(first_rest_jsd, 4),
            'enrichment_ratios': enrichment,
            'first_profile': {ALL_CATEGORIES[i]: round(first_vec[i], 4)
                              for i in range(len(ALL_CATEGORIES))},
            'rest_profile': {ALL_CATEGORIES[i]: round(rest_vec[i], 4)
                             for i in range(len(ALL_CATEGORIES))},
        },
        'section_breakdown': section_results,
    }


# ================================================================
# MAIN
# ================================================================
def main():
    rng = random.Random(SEED)
    t0 = time.time()

    print("Phase 468: A_PARAGRAPH_CATEGORY_ARCHITECTURE")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles, _, _ = load_all_data()

    # Build paragraphs
    print("\nBuilding paragraphs...")
    paragraphs = build_a_paragraphs(a_tokens, mid_to_cat)
    n3 = sum(1 for p in paragraphs if p['n_categorized'] >= 3)
    n5 = sum(1 for p in paragraphs if p['n_categorized'] >= 5)
    print(f"  Total paragraphs: {len(paragraphs)}")
    print(f"  With 3+ categorized PP: {n3}")
    print(f"  With 5+ categorized PP: {n5}")

    # Folio count
    folios = set(p['folio'] for p in paragraphs if p['n_categorized'] >= 3)
    print(f"  Folios represented: {len(folios)}")

    # Run tests
    results = {}
    results['A1'] = test_a1(paragraphs, rng)
    results['A2'] = test_a2(paragraphs, rng)
    results['A3'] = test_a3(paragraphs, rng)
    results['A4'] = test_a4(paragraphs, rng)

    # Summary
    dt = time.time() - t0
    results['meta'] = {
        'phase': 'A_PARAGRAPH_CATEGORY_ARCHITECTURE',
        'phase_number': 468,
        'total_paragraphs': len(paragraphs),
        'eligible_3plus': n3,
        'eligible_5plus': n5,
        'n_folios': len(folios),
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
    }

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for test_id in ['A1', 'A2', 'A3', 'A4']:
        v = results[test_id].get('verdict', 'N/A')
        print(f"  {test_id}: {v}")
    print(f"\nRuntime: {dt:.1f}s")

    # Save
    out_path = RESULTS_DIR / "a_paragraph_category_architecture.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
