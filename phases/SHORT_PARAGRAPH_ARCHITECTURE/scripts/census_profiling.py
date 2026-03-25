"""
Phase 625, Script 1: Census and Feature Profiling of Short Paragraphs.

Performs stratum census (HEADER_ONLY / MINIMAL / SHORT / LONG), gallows
profiling, header atom analysis, C1398 zone classification, and three-level
11-feature comparison across strata.

Output: phases/SHORT_PARAGRAPH_ARCHITECTURE/results/census_profiling.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from phases.SHORT_PARAGRAPH_ARCHITECTURE.scripts.shared_625 import (
    build_corpus, assign_stratum, get_all_tokens, extract_paragraph_features,
    extract_gallows_info, extract_header_features, classify_paragraph_zone,
    STRATA, STRATUM_ORDER, FEATURE_NAMES, CATEGORIES, RESULTS_DIR,
    round_floats, chi_squared_contingency, mann_whitney_u, kruskal_wallis,
    cohens_d, section_residualize_values, identify_golden_folios,
    euclidean_dist,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Zone name mapping from numeric cluster IDs to descriptive names (C1398)
ZONE_NAMES = {
    '0': 'THERMAL_QO',
    '1': 'CONTAINMENT_SEALING',
    '2': 'OPERATION_ITERATION',
    '3': 'MONITORING_PHASE',
}

# The 8 category keys used in zone centroids
ZONE_CATS = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
             'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']


# ============================================================
# Helpers
# ============================================================

def _mean(vals):
    """Mean of a list, returning 0.0 if empty."""
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals):
    """Population standard deviation of a list."""
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))


def _median(vals):
    """Median of a list."""
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def _compute_8cat_profile(paragraph):
    """
    Compute the 8-category fraction profile for a paragraph.
    Returns dict: category_name -> fraction.
    """
    tokens = get_all_tokens(paragraph)
    cat_counts = Counter()
    for t in tokens:
        cat = t.get('category', 'UNKNOWN')
        if cat in CATEGORIES:
            cat_counts[cat] += 1
    total = sum(cat_counts.values())
    if total == 0:
        return {c: 0.0 for c in ZONE_CATS}
    return {c: cat_counts.get(c, 0) / total for c in ZONE_CATS}


def _load_zone_centroids():
    """Load C1398 zone centroids from Phase 510 results."""
    path = PROJECT_ROOT / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json'
    with open(path) as f:
        data = json.load(f)
    raw = data['T1_clustering']['centroids']
    centroids = {}
    for zone_id_str, cent_dict in raw.items():
        zone_name = ZONE_NAMES.get(zone_id_str, f'ZONE_{zone_id_str}')
        # Extract only the 8 category keys
        centroids[zone_name] = {c: cent_dict.get(c, 0.0) for c in ZONE_CATS}
    return centroids


# ============================================================
# T1: Census by stratum and section
# ============================================================

def run_t1(corpus, all_paragraphs):
    """Census cross-tabulation: stratum x section, golden folios, consecutive run analysis."""
    print("\n=== T1: Census by Stratum and Section ===")

    # Assign strata
    strata_map = {}  # (folio, par_id) -> stratum
    for par in all_paragraphs:
        stratum = assign_stratum(par)
        strata_map[(par['folio'], par['id'])] = stratum

    # Count by stratum
    stratum_counts = Counter()
    for par in all_paragraphs:
        stratum_counts[strata_map[(par['folio'], par['id'])]] += 1

    print(f"  Total paragraphs: {len(all_paragraphs)}")
    for s in STRATUM_ORDER:
        print(f"    {s}: {stratum_counts.get(s, 0)}")

    # Cross-tabulate stratum x section
    cross_tab = defaultdict(lambda: defaultdict(int))
    for par in all_paragraphs:
        stratum = strata_map[(par['folio'], par['id'])]
        section = par['section']
        cross_tab[stratum][section] += 1

    # Build dict-of-dicts for chi_squared_contingency
    sections_present = sorted({par['section'] for par in all_paragraphs})
    cross_dict = {}
    for s in STRATUM_ORDER:
        cross_dict[s] = {}
        for sec in sections_present:
            cross_dict[s][sec] = cross_tab[s].get(sec, 0)

    print("\n  Cross-tabulation (stratum x section):")
    header = f"  {'':18s}" + ''.join(f'{sec:>8s}' for sec in sections_present)
    print(header)
    for s in STRATUM_ORDER:
        vals = ''.join(f'{cross_dict[s].get(sec, 0):8d}' for sec in sections_present)
        print(f"  {s:18s}{vals}")

    # Chi-squared test
    chi_result = chi_squared_contingency(cross_dict)
    print(f"\n  Chi-squared: {chi_result['chi2']:.2f}, df={chi_result['df']}, "
          f"p={chi_result['p']:.6f}, Cramer's V={chi_result['V']:.4f}")

    # Golden folios
    golden = identify_golden_folios(all_paragraphs, strata_map)
    print(f"\n  Golden folios (SHORT-or-below + LONG in same section): {len(golden)}")
    if golden:
        print(f"    Examples: {golden[:10]}")

    # HEADER_ONLY consecutive run census
    print("\n  HEADER_ONLY consecutive run census:")
    folios_with_runs = 0
    max_run_global = 0
    total_runs = 0

    for folio, fdata in corpus.items():
        paragraphs = fdata['paragraphs']
        run_len = 0
        folio_has_run = False
        for par in paragraphs:
            stratum = assign_stratum(par)
            if stratum == 'HEADER_ONLY':
                run_len += 1
                if run_len >= 2:
                    if not folio_has_run:
                        folio_has_run = True
            else:
                if run_len >= 2:
                    total_runs += 1
                    max_run_global = max(max_run_global, run_len)
                run_len = 0
        # Check trailing run
        if run_len >= 2:
            total_runs += 1
            max_run_global = max(max_run_global, run_len)
        if folio_has_run:
            folios_with_runs += 1

    print(f"    Folios with consecutive HEADER_ONLY runs: {folios_with_runs}")
    print(f"    Max consecutive run length: {max_run_global}")
    print(f"    Total runs of 2+: {total_runs}")

    return {
        'stratum_counts': {s: stratum_counts.get(s, 0) for s in STRATUM_ORDER},
        'section_x_stratum': {s: dict(cross_dict[s]) for s in STRATUM_ORDER},
        'chi2': chi_result['chi2'],
        'V': chi_result['V'],
        'p': chi_result['p'],
        'df': chi_result['df'],
        'golden_folios': golden,
        'golden_folio_count': len(golden),
        'header_only_consecutive_runs': {
            'folios_with_runs': folios_with_runs,
            'max_run': max_run_global,
            'total_runs': total_runs,
        },
    }


# ============================================================
# T2: Gallows profile by stratum
# ============================================================

def run_t2(all_paragraphs):
    """Gallows type distribution by stratum; opener fraction; within-Recipe version."""
    print("\n=== T2: Gallows Profile by Stratum ===")

    # Build contingency: gallows_type x stratum
    cross_tab = defaultdict(lambda: defaultdict(int))
    gallows_types_seen = set()

    for par in all_paragraphs:
        stratum = assign_stratum(par)
        ginfo = extract_gallows_info(par)
        gtype = ginfo['gallows_type']
        cross_tab[gtype][stratum] += 1
        gallows_types_seen.add(gtype)

    gallows_order = sorted(gallows_types_seen)

    # Print table
    print(f"\n  {'':8s}" + ''.join(f'{s:>16s}' for s in STRATUM_ORDER))
    for gt in gallows_order:
        vals = ''.join(f'{cross_tab[gt].get(s, 0):16d}' for s in STRATUM_ORDER)
        print(f"  {gt:8s}{vals}")

    # Chi-squared
    cross_dict = {}
    for gt in gallows_order:
        cross_dict[gt] = {s: cross_tab[gt].get(s, 0) for s in STRATUM_ORDER}
    chi_result = chi_squared_contingency(cross_dict)
    print(f"\n  Chi-squared: {chi_result['chi2']:.2f}, df={chi_result['df']}, "
          f"p={chi_result['p']:.6f}, Cramer's V={chi_result['V']:.4f}")

    # k+f opener fraction per stratum
    print("\n  Opener fraction (k+f) by stratum:")
    opener_fracs = {}
    for s in STRATUM_ORDER:
        total = sum(cross_tab[gt].get(s, 0) for gt in gallows_order)
        kf = cross_tab.get('k', {}).get(s, 0) + cross_tab.get('f', {}).get(s, 0)
        frac = kf / total if total > 0 else 0.0
        opener_fracs[s] = frac
        print(f"    {s}: {frac:.4f}  ({kf}/{total})")

    # Within-Recipe (section='S' only)
    print("\n  Within-Recipe (section=S only):")
    s_pars = [p for p in all_paragraphs if p['section'] == 'S']
    s_cross_tab = defaultdict(lambda: defaultdict(int))
    s_types = set()
    for par in s_pars:
        stratum = assign_stratum(par)
        ginfo = extract_gallows_info(par)
        gtype = ginfo['gallows_type']
        s_cross_tab[gtype][stratum] += 1
        s_types.add(gtype)

    s_types_order = sorted(s_types)
    s_cross_dict = {}
    for gt in s_types_order:
        s_cross_dict[gt] = {s: s_cross_tab[gt].get(s, 0) for s in STRATUM_ORDER}

    s_chi = chi_squared_contingency(s_cross_dict)
    print(f"    n={len(s_pars)}, Chi-squared: {s_chi['chi2']:.2f}, "
          f"df={s_chi['df']}, p={s_chi['p']:.6f}, V={s_chi['V']:.4f}")

    return {
        'gallows_x_stratum': {gt: dict(cross_tab[gt]) for gt in gallows_order},
        'chi2': chi_result['chi2'],
        'V': chi_result['V'],
        'p': chi_result['p'],
        'df': chi_result['df'],
        'opener_fraction_by_stratum': opener_fracs,
        'within_recipe': {
            'n': len(s_pars),
            'chi2': s_chi['chi2'],
            'V': s_chi['V'],
            'p': s_chi['p'],
            'df': s_chi['df'],
        },
    }


# ============================================================
# T3: HEADER_ONLY atom profile
# ============================================================

def run_t3(all_paragraphs):
    """Compare header atom composition between HEADER_ONLY and multi-line paragraphs."""
    print("\n=== T3: HEADER_ONLY Atom Profile ===")

    header_only_vecs = []
    multiline_vecs = []

    for par in all_paragraphs:
        stratum = assign_stratum(par)
        hf_result = extract_header_features(par)
        if hf_result is None or hf_result[0] is None:
            continue
        vec, meta = hf_result
        if stratum == 'HEADER_ONLY':
            header_only_vecs.append(vec)
        else:
            multiline_vecs.append(vec)

    print(f"  HEADER_ONLY paragraphs with header features: {len(header_only_vecs)}")
    print(f"  Multi-line paragraphs with header features: {len(multiline_vecs)}")

    # Feature names for the 7-dim header vector
    atom_names = ['k_frac', 'h_frac', 'e_frac', 'o_frac', 'a_frac', 'ht_rate', 'n_tokens']
    # We compare only the first 5 (atom fractions)
    atom_indices = list(range(5))

    comparisons = {}
    enriched = []
    depleted = []

    for idx in atom_indices:
        name = atom_names[idx]
        ho_vals = [v[idx] for v in header_only_vecs]
        ml_vals = [v[idx] for v in multiline_vecs]

        ho_mean = _mean(ho_vals)
        ml_mean = _mean(ml_vals)

        if len(ho_vals) >= 5 and len(ml_vals) >= 5:
            mw = mann_whitney_u(ho_vals, ml_vals)
            d = cohens_d(ho_vals, ml_vals)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(ho_vals), 'n_b': len(ml_vals)}
            d = 0.0

        comparisons[name] = {
            'header_only_mean': ho_mean,
            'multiline_mean': ml_mean,
            'U': mw['U'],
            'z': mw['z'],
            'p': mw['p'],
            'cohens_d': d,
        }

        direction = 'enriched' if ho_mean > ml_mean else 'depleted'
        sig = '*' if mw['p'] < 0.05 else ''
        print(f"  {name:10s}: HO={ho_mean:.4f} vs ML={ml_mean:.4f}, "
              f"d={d:+.3f}, p={mw['p']:.4f}{sig}  ({direction})")

        if mw['p'] < 0.05:
            if ho_mean > ml_mean:
                enriched.append(name)
            else:
                depleted.append(name)

    # Also report ht_rate and n_tokens
    for idx in [5, 6]:
        name = atom_names[idx]
        ho_vals = [v[idx] for v in header_only_vecs]
        ml_vals = [v[idx] for v in multiline_vecs]

        ho_mean = _mean(ho_vals)
        ml_mean = _mean(ml_vals)

        if len(ho_vals) >= 5 and len(ml_vals) >= 5:
            mw = mann_whitney_u(ho_vals, ml_vals)
            d = cohens_d(ho_vals, ml_vals)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(ho_vals), 'n_b': len(ml_vals)}
            d = 0.0

        comparisons[name] = {
            'header_only_mean': ho_mean,
            'multiline_mean': ml_mean,
            'U': mw['U'],
            'z': mw['z'],
            'p': mw['p'],
            'cohens_d': d,
        }
        sig = '*' if mw['p'] < 0.05 else ''
        print(f"  {name:10s}: HO={ho_mean:.4f} vs ML={ml_mean:.4f}, "
              f"d={d:+.3f}, p={mw['p']:.4f}{sig}")

    print(f"\n  Enriched in HEADER_ONLY: {enriched or 'none'}")
    print(f"  Depleted in HEADER_ONLY: {depleted or 'none'}")

    return {
        'n_header_only': len(header_only_vecs),
        'n_multiline': len(multiline_vecs),
        'comparisons': comparisons,
        'enriched_in_header_only': enriched,
        'depleted_in_header_only': depleted,
    }


# ============================================================
# T4: MINIMAL zone classification (C1398)
# ============================================================

def run_t4(all_paragraphs):
    """Assign paragraphs to nearest C1398 zone centroid; compare zone distributions."""
    print("\n=== T4: Zone Classification (C1398) ===")

    zone_centroids = _load_zone_centroids()
    zone_names = sorted(zone_centroids.keys())
    print(f"  Loaded {len(zone_centroids)} zone centroids: {zone_names}")

    # Classify each paragraph
    zone_by_stratum = defaultdict(lambda: Counter())
    for par in all_paragraphs:
        stratum = assign_stratum(par)
        if stratum not in ('MINIMAL', 'SHORT', 'LONG'):
            # Skip HEADER_ONLY for zone classification (too few tokens)
            continue
        cat_profile = _compute_8cat_profile(par)
        zone = classify_paragraph_zone(cat_profile, zone_centroids)
        zone_by_stratum[stratum][zone] += 1

    # Build contingency table: zone x stratum (MINIMAL, SHORT, LONG)
    target_strata = ['MINIMAL', 'SHORT', 'LONG']
    cross_dict = {}
    for z in zone_names:
        cross_dict[z] = {s: zone_by_stratum[s].get(z, 0) for s in target_strata}

    # Print distribution
    print(f"\n  {'':28s}" + ''.join(f'{s:>12s}' for s in target_strata))
    for z in zone_names:
        vals = ''.join(f'{cross_dict[z].get(s, 0):12d}' for s in target_strata)
        print(f"  {z:28s}{vals}")

    # Per-stratum zone proportions
    per_stratum_dist = {}
    for s in target_strata:
        total = sum(zone_by_stratum[s].values())
        dist = {}
        for z in zone_names:
            c = zone_by_stratum[s].get(z, 0)
            dist[z] = c / total if total > 0 else 0.0
        per_stratum_dist[s] = dist
        print(f"\n  {s} proportions:")
        for z in zone_names:
            print(f"    {z}: {dist[z]:.4f}")

    # Chi-squared
    chi_result = chi_squared_contingency(cross_dict)
    print(f"\n  Chi-squared: {chi_result['chi2']:.2f}, df={chi_result['df']}, "
          f"p={chi_result['p']:.6f}, V={chi_result['V']:.4f}")

    # Section-controlled: within-Recipe version
    print("\n  Within-Recipe (section=S only):")
    s_zone_by_stratum = defaultdict(lambda: Counter())
    for par in all_paragraphs:
        if par['section'] != 'S':
            continue
        stratum = assign_stratum(par)
        if stratum not in target_strata:
            continue
        cat_profile = _compute_8cat_profile(par)
        zone = classify_paragraph_zone(cat_profile, zone_centroids)
        s_zone_by_stratum[stratum][zone] += 1

    s_cross_dict = {}
    for z in zone_names:
        s_cross_dict[z] = {s: s_zone_by_stratum[s].get(z, 0) for s in target_strata}
    s_chi = chi_squared_contingency(s_cross_dict)
    s_n = sum(sum(s_zone_by_stratum[s].values()) for s in target_strata)
    print(f"    n={s_n}, Chi-squared: {s_chi['chi2']:.2f}, "
          f"df={s_chi['df']}, p={s_chi['p']:.6f}, V={s_chi['V']:.4f}")

    return {
        'zone_x_stratum': {z: dict(v) for z, v in cross_dict.items()},
        'per_stratum_distribution': per_stratum_dist,
        'chi2': chi_result['chi2'],
        'V': chi_result['V'],
        'p': chi_result['p'],
        'df': chi_result['df'],
        'within_recipe': {
            'n': s_n,
            'chi2': s_chi['chi2'],
            'V': s_chi['V'],
            'p': s_chi['p'],
            'df': s_chi['df'],
        },
    }


# ============================================================
# T5: 11-feature profiles by stratum (THREE-LEVEL protocol)
# ============================================================

def run_t5(all_paragraphs):
    """Three-level feature comparison: pooled, section-residualized, within-Recipe."""
    print("\n=== T5: 11-Feature Profiles by Stratum (Three-Level Protocol) ===")

    # Extract features per paragraph
    par_features = []  # list of (stratum, section, folio, par_id, feat_dict)
    for par in all_paragraphs:
        stratum = assign_stratum(par)
        feats = extract_paragraph_features(par)
        par_features.append({
            'stratum': stratum,
            'section': par['section'],
            'folio': par['folio'],
            'par_id': par['id'],
            'features': feats,
        })

    # Group by stratum
    by_stratum = defaultdict(list)
    for pf in par_features:
        by_stratum[pf['stratum']].append(pf)

    # Compute per-stratum descriptive stats
    print("\n  Per-stratum descriptive statistics:")
    by_stratum_stats = {}
    for s in STRATUM_ORDER:
        pars = by_stratum.get(s, [])
        stats = {}
        for fname in FEATURE_NAMES:
            vals = [p['features'][fname] for p in pars]
            stats[fname] = {
                'mean': _mean(vals),
                'sd': _std(vals),
                'median': _median(vals),
                'n': len(vals),
            }
        by_stratum_stats[s] = stats

    # Print summary table
    print(f"\n  {'Feature':20s}", end='')
    for s in STRATUM_ORDER:
        print(f"  {s:>14s}", end='')
    print()
    for fname in FEATURE_NAMES:
        print(f"  {fname:20s}", end='')
        for s in STRATUM_ORDER:
            st = by_stratum_stats[s].get(fname, {})
            m = st.get('mean', 0.0)
            print(f"  {m:14.4f}", end='')
        print()

    # ---- Level 1: Pooled ----
    print("\n  --- Level 1: Pooled ---")
    pooled_kw = {}
    pooled_short_vs_long = {}

    for fname in FEATURE_NAMES:
        groups = []
        for s in STRATUM_ORDER:
            vals = [p['features'][fname] for p in by_stratum.get(s, [])]
            groups.append(vals)

        # Kruskal-Wallis across all 4 strata
        kw = kruskal_wallis(groups)
        pooled_kw[fname] = {'H': kw['H'], 'df': kw['df'], 'p': kw['p']}

        # SHORT vs LONG pairwise
        short_vals = [p['features'][fname] for p in by_stratum.get('SHORT', [])]
        long_vals = [p['features'][fname] for p in by_stratum.get('LONG', [])]
        if len(short_vals) >= 5 and len(long_vals) >= 5:
            mw = mann_whitney_u(short_vals, long_vals)
            d = cohens_d(short_vals, long_vals)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(short_vals), 'n_b': len(long_vals)}
            d = 0.0

        pooled_short_vs_long[fname] = {
            'U': mw['U'], 'z': mw['z'], 'p': mw['p'],
            'cohens_d': d,
            'n_short': len(short_vals), 'n_long': len(long_vals),
        }

        sig_kw = '*' if kw['p'] < 0.05 else ' '
        sig_mw = '*' if mw['p'] < 0.05 else ' '
        print(f"    {fname:20s}  KW p={kw['p']:.4f}{sig_kw}  "
              f"S-vs-L d={d:+.3f} p={mw['p']:.4f}{sig_mw}")

    pooled_invariant = sum(1 for f in FEATURE_NAMES if pooled_kw[f]['p'] > 0.05)
    print(f"\n  Pooled invariant features (KW p>0.05): {pooled_invariant}/{len(FEATURE_NAMES)}")

    # ---- Level 2: Section-residualized ----
    print("\n  --- Level 2: Section-Residualized ---")
    resid_kw = {}
    resid_short_vs_long = {}

    for fname in FEATURE_NAMES:
        all_vals = [p['features'][fname] for p in par_features]
        all_sections = [p['section'] for p in par_features]
        all_strata = [p['stratum'] for p in par_features]

        resid_vals = section_residualize_values(all_vals, all_sections)

        # Build groups by stratum from residualized values
        groups_resid = defaultdict(list)
        for rv, s in zip(resid_vals, all_strata):
            groups_resid[s].append(rv)

        kw_groups = [groups_resid.get(s, []) for s in STRATUM_ORDER]
        kw = kruskal_wallis(kw_groups)
        resid_kw[fname] = {'H': kw['H'], 'df': kw['df'], 'p': kw['p']}

        short_r = groups_resid.get('SHORT', [])
        long_r = groups_resid.get('LONG', [])
        if len(short_r) >= 5 and len(long_r) >= 5:
            mw = mann_whitney_u(short_r, long_r)
            d = cohens_d(short_r, long_r)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(short_r), 'n_b': len(long_r)}
            d = 0.0

        resid_short_vs_long[fname] = {
            'U': mw['U'], 'z': mw['z'], 'p': mw['p'], 'cohens_d': d,
        }

        sig_kw = '*' if kw['p'] < 0.05 else ' '
        sig_mw = '*' if mw['p'] < 0.05 else ' '
        print(f"    {fname:20s}  KW p={kw['p']:.4f}{sig_kw}  "
              f"S-vs-L d={d:+.3f} p={mw['p']:.4f}{sig_mw}")

    resid_invariant = sum(1 for f in FEATURE_NAMES if resid_kw[f]['p'] > 0.05)
    print(f"\n  Section-residualized invariant features: {resid_invariant}/{len(FEATURE_NAMES)}")

    # ---- Level 3: Within-Recipe (section=S only) ----
    print("\n  --- Level 3: Within-Recipe (section=S only) ---")
    recipe_kw = {}
    recipe_short_vs_long = {}

    recipe_pars = [p for p in par_features if p['section'] == 'S']
    recipe_by_stratum = defaultdict(list)
    for p in recipe_pars:
        recipe_by_stratum[p['stratum']].append(p)

    n_recipe = len(recipe_pars)
    print(f"    Recipe paragraphs: {n_recipe}")

    for fname in FEATURE_NAMES:
        groups = [
            [p['features'][fname] for p in recipe_by_stratum.get(s, [])]
            for s in STRATUM_ORDER
        ]
        non_empty = [g for g in groups if len(g) > 0]
        if len(non_empty) >= 2:
            kw = kruskal_wallis(groups)
        else:
            kw = {'H': 0.0, 'df': 0, 'p': 1.0}
        recipe_kw[fname] = {'H': kw['H'], 'df': kw['df'], 'p': kw['p']}

        short_r = [p['features'][fname] for p in recipe_by_stratum.get('SHORT', [])]
        long_r = [p['features'][fname] for p in recipe_by_stratum.get('LONG', [])]
        if len(short_r) >= 5 and len(long_r) >= 5:
            mw = mann_whitney_u(short_r, long_r)
            d = cohens_d(short_r, long_r)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(short_r), 'n_b': len(long_r)}
            d = 0.0

        recipe_short_vs_long[fname] = {
            'U': mw['U'], 'z': mw['z'], 'p': mw['p'], 'cohens_d': d,
        }

        sig_kw = '*' if kw['p'] < 0.05 else ' '
        sig_mw = '*' if mw['p'] < 0.05 else ' '
        print(f"    {fname:20s}  KW p={kw['p']:.4f}{sig_kw}  "
              f"S-vs-L d={d:+.3f} p={mw['p']:.4f}{sig_mw}")

    recipe_invariant = sum(1 for f in FEATURE_NAMES if recipe_kw[f]['p'] > 0.05)
    print(f"\n  Within-Recipe invariant features: {recipe_invariant}/{len(FEATURE_NAMES)}")

    # ---- Golden folio test ----
    print("\n  --- Golden Folio Test ---")
    strata_map = {}
    for pf in par_features:
        strata_map[(pf['folio'], pf['par_id'])] = pf['stratum']

    golden = identify_golden_folios(
        [{'folio': p['folio'], 'section': p['section'], 'id': p['par_id']}
         for p in par_features],
        strata_map,
    )
    golden_set = set(golden)

    golden_short = [p for p in par_features
                    if p['folio'] in golden_set and p['stratum'] == 'SHORT']
    golden_long = [p for p in par_features
                   if p['folio'] in golden_set and p['stratum'] == 'LONG']

    print(f"    Golden SHORT: {len(golden_short)}, Golden LONG: {len(golden_long)}")

    golden_results = {}
    for fname in FEATURE_NAMES:
        gs = [p['features'][fname] for p in golden_short]
        gl = [p['features'][fname] for p in golden_long]
        if len(gs) >= 5 and len(gl) >= 5:
            mw = mann_whitney_u(gs, gl)
            d = cohens_d(gs, gl)
        else:
            mw = {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': len(gs), 'n_b': len(gl)}
            d = 0.0

        golden_results[fname] = {
            'U': mw['U'], 'z': mw['z'], 'p': mw['p'], 'cohens_d': d,
        }
        sig = '*' if mw['p'] < 0.05 else ' '
        print(f"    {fname:20s}  d={d:+.3f}  p={mw['p']:.4f}{sig}")

    golden_invariant = sum(1 for f in FEATURE_NAMES
                           if golden_results[f]['p'] > 0.05)
    print(f"\n  Golden folio invariant features: {golden_invariant}/{len(FEATURE_NAMES)}")

    return {
        'by_stratum': by_stratum_stats,
        'pooled_kw': pooled_kw,
        'pooled_short_vs_long': pooled_short_vs_long,
        'section_residualized': {
            'kw': resid_kw,
            'short_vs_long': resid_short_vs_long,
        },
        'within_recipe': {
            'n': n_recipe,
            'kw': recipe_kw,
            'short_vs_long': recipe_short_vs_long,
        },
        'golden_folio': {
            'n_golden_folios': len(golden),
            'n_golden_short': len(golden_short),
            'n_golden_long': len(golden_long),
            'comparisons': golden_results,
        },
        'invariant_counts': {
            'pooled': pooled_invariant,
            'section_resid': resid_invariant,
            'within_recipe': recipe_invariant,
            'golden_folio': golden_invariant,
        },
    }


# ============================================================
# SYNTHESIS
# ============================================================

def print_synthesis(t1, t2, t3, t4, t5):
    """Print a summary of key findings."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: Census Profiling of Short Paragraphs")
    print("=" * 70)

    total = sum(t1['stratum_counts'].values())
    long_n = t1['stratum_counts'].get('LONG', 0)
    short_n = t1['stratum_counts'].get('SHORT', 0)
    min_n = t1['stratum_counts'].get('MINIMAL', 0)
    ho_n = t1['stratum_counts'].get('HEADER_ONLY', 0)
    non_long = total - long_n
    pct_non_long = non_long / total * 100 if total > 0 else 0

    print(f"\n  1. CENSUS: {total} paragraphs total")
    print(f"     HEADER_ONLY={ho_n}, MINIMAL={min_n}, SHORT={short_n}, LONG={long_n}")
    print(f"     Non-LONG: {non_long} ({pct_non_long:.1f}%)")
    print(f"     Section x stratum association: V={t1['V']:.3f}, p={t1['p']:.6f}")
    print(f"     Golden folios: {t1['golden_folio_count']}")
    ho_runs = t1['header_only_consecutive_runs']
    print(f"     HEADER_ONLY consecutive runs: {ho_runs['total_runs']} runs "
          f"across {ho_runs['folios_with_runs']} folios, max={ho_runs['max_run']}")

    print(f"\n  2. GALLOWS: association with stratum V={t2['V']:.3f}, p={t2['p']:.6f}")
    print(f"     Opener (k+f) fractions: ", end='')
    for s in STRATUM_ORDER:
        print(f"{s}={t2['opener_fraction_by_stratum'].get(s, 0):.3f}  ", end='')
    print()
    wr = t2['within_recipe']
    print(f"     Within-Recipe: V={wr['V']:.3f}, p={wr['p']:.6f}")

    print(f"\n  3. HEADER_ONLY ATOMS:")
    enr = t3.get('enriched_in_header_only', [])
    dep = t3.get('depleted_in_header_only', [])
    print(f"     Enriched: {enr if enr else 'none'}")
    print(f"     Depleted: {dep if dep else 'none'}")

    print(f"\n  4. ZONE CLASSIFICATION (C1398):")
    print(f"     Association: V={t4['V']:.3f}, p={t4['p']:.6f}")
    wr4 = t4['within_recipe']
    print(f"     Within-Recipe: V={wr4['V']:.3f}, p={wr4['p']:.6f}")

    inv = t5['invariant_counts']
    n_feat = len(FEATURE_NAMES)
    print(f"\n  5. FEATURE PROFILES ({n_feat} features):")
    print(f"     Invariant across strata (KW p>0.05):")
    print(f"       Pooled:               {inv['pooled']}/{n_feat}")
    print(f"       Section-residualized:  {inv['section_resid']}/{n_feat}")
    print(f"       Within-Recipe:         {inv['within_recipe']}/{n_feat}")
    print(f"       Golden-folio S-vs-L:   {inv.get('golden_folio', '?')}/{n_feat}")

    # Identify features that are consistently significant
    sig_pooled = [f for f in FEATURE_NAMES
                  if t5['pooled_short_vs_long'][f]['p'] < 0.05]
    sig_resid = [f for f in FEATURE_NAMES
                 if t5['section_residualized']['short_vs_long'][f]['p'] < 0.05]
    sig_recipe = [f for f in FEATURE_NAMES
                  if t5['within_recipe']['short_vs_long'][f]['p'] < 0.05]

    # Features significant at all 3 levels
    robust_sig = sorted(set(sig_pooled) & set(sig_resid) & set(sig_recipe))
    if robust_sig:
        print(f"\n     Features significant at ALL 3 levels (SHORT vs LONG):")
        for f in robust_sig:
            d_p = t5['pooled_short_vs_long'][f]['cohens_d']
            d_r = t5['section_residualized']['short_vs_long'][f]['cohens_d']
            d_w = t5['within_recipe']['short_vs_long'][f]['cohens_d']
            print(f"       {f}: d_pooled={d_p:+.3f}, d_resid={d_r:+.3f}, d_recipe={d_w:+.3f}")
    else:
        print(f"\n     No features significant at all 3 levels.")

    # Features invariant at all 3 levels
    inv_pooled = {f for f in FEATURE_NAMES if t5['pooled_kw'][f]['p'] > 0.05}
    inv_resid = {f for f in FEATURE_NAMES if t5['section_residualized']['kw'][f]['p'] > 0.05}
    inv_recipe = {f for f in FEATURE_NAMES if t5['within_recipe']['kw'][f]['p'] > 0.05}
    robust_inv = sorted(inv_pooled & inv_resid & inv_recipe)
    if robust_inv:
        print(f"\n     Features invariant at ALL 3 levels:")
        for f in robust_inv:
            print(f"       {f}")

    print()


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 625, Script 1: Census and Feature Profiling")
    print("=" * 60)

    # Build corpus
    print("\nBuilding corpus...")
    corpus = build_corpus()
    n_folios = len(corpus)
    print(f"  {n_folios} folios loaded")

    # Flatten paragraphs with folio/section metadata
    all_paragraphs = []
    for folio, fdata in sorted(corpus.items()):
        for par in fdata['paragraphs']:
            par_with_meta = dict(par)
            par_with_meta['folio'] = folio
            par_with_meta['section'] = fdata['section']
            par_with_meta['regime'] = fdata['regime']
            all_paragraphs.append(par_with_meta)

    n_paragraphs = len(all_paragraphs)
    print(f"  {n_paragraphs} total paragraphs")

    # Run analyses
    t1_result = run_t1(corpus, all_paragraphs)
    t2_result = run_t2(all_paragraphs)
    t3_result = run_t3(all_paragraphs)
    t4_result = run_t4(all_paragraphs)
    t5_result = run_t5(all_paragraphs)

    # Print synthesis
    print_synthesis(t1_result, t2_result, t3_result, t4_result, t5_result)

    # Assemble output
    result = {
        'metadata': {
            'phase': 625,
            'script': 1,
            'timestamp': datetime.now().isoformat(),
            'n_paragraphs': n_paragraphs,
            'n_folios': n_folios,
            'feature_names': FEATURE_NAMES,
            'strata': {k: list(v) for k, v in STRATA.items()},
        },
        'T1_census': t1_result,
        'T2_gallows': t2_result,
        'T3_header_only_atoms': t3_result,
        'T4_zone_classification': t4_result,
        'T5_feature_profiles': t5_result,
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'census_profiling.json'
    result = round_floats(result)
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print("Done.")


if __name__ == '__main__':
    main()
