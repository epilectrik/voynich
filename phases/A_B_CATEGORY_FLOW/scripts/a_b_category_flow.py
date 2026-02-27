"""
Phase 471: A_B_CATEGORY_FLOW

Tests whether A-side category structure propagates to B through the
vocabulary pipeline (bridge and dark channels), or whether B determines
its own category landscape independently.

Tests:
  T1: Category usage persistence across systems (same bridge MIDDLEs, A vs B)
  T2: Bridge delivery vs B consumption (reshaping test)
  T3: Section-level category flow through bridge
  T4: Dark pipeline category manifestation in B

References: C1136, C1264, C1272, C1274, C1279, C1287, C1288, C918,
            C1266, C1137, C1254, C1134, C1148, C1146
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

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# Phase 452: A/B data + bridge/dark
sys.path.insert(0, str(ROOT / 'phases' / 'A_CATEGORY_SCATTERSHOT' / 'scripts'))
from a_category_scattershot import (
    load_all_data, build_category_map, ALL_CATEGORIES
)

# Phase 462: stats
sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    jsd, normalize_profile, normal_cdf, chi2_sf, mann_whitney_u
)

# Phase 469: MI, chi2_independence
sys.path.insert(0, str(ROOT / 'phases' / 'SUFFIX_MODE_ASSIGNMENT' / 'scripts'))
from suffix_mode_assignment import (
    mutual_information, chi2_independence
)

# Phase 463: Spearman
sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "A_B_CATEGORY_FLOW" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42


# ================================================================
# DATA PREPARATION
# ================================================================

def precompute_middle_counts(a_tokens, b_tokens, mid_to_cat, target_set):
    """Pre-compute per-MIDDLE token counts in A and B for a target MIDDLE set.

    Returns:
        a_counts: dict {middle: count_in_A}
        b_counts: dict {middle: count_in_B}
        categorized_middles: set of MIDDLEs in target_set that have categories
    """
    a_counts = Counter()
    b_counts = Counter()

    for t in a_tokens:
        mid = t.get('middle')
        if mid and mid in target_set:
            a_counts[mid] += 1

    for t in b_tokens:
        mid = t.get('middle')
        if mid and mid in target_set:
            b_counts[mid] += 1

    categorized = {m for m in target_set if m in mid_to_cat}
    return dict(a_counts), dict(b_counts), categorized


def build_category_profile(middles, counts, mid_to_cat):
    """Build a frequency-weighted category profile from a set of MIDDLEs.

    Args:
        middles: iterable of MIDDLE strings
        counts: dict {middle: token_count}
        mid_to_cat: dict {middle: category}

    Returns:
        profile: list of 8 floats (ALL_CATEGORIES order), normalized
        raw_counts: Counter of category counts
    """
    raw = Counter()
    for mid in middles:
        cat = mid_to_cat.get(mid)
        if cat and mid in counts:
            raw[cat] += counts[mid]

    total = sum(raw.values())
    if total == 0:
        return [0.0] * len(ALL_CATEGORIES), raw

    profile = [raw.get(c, 0) / total for c in ALL_CATEGORIES]
    return profile, raw


# ================================================================
# TEST T1: Category Usage Persistence Across Systems
# ================================================================

def test_t1(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng):
    """Do bridge MIDDLEs show the same category usage profile in A vs B?"""
    print("\n=== T1: Category Usage Persistence Across Systems ===")

    a_counts, b_counts, cat_bridges = precompute_middle_counts(
        a_tokens, b_tokens, mid_to_cat, bridge_middles
    )
    print(f"  Bridge MIDDLEs with category: {len(cat_bridges)}")
    print(f"  Bridge MIDDLEs with A tokens: {sum(1 for m in cat_bridges if a_counts.get(m, 0) > 0)}")
    print(f"  Bridge MIDDLEs with B tokens: {sum(1 for m in cat_bridges if b_counts.get(m, 0) > 0)}")

    # Build A-side and B-side category usage profiles
    a_profile, a_raw = build_category_profile(cat_bridges, a_counts, mid_to_cat)
    b_profile, b_raw = build_category_profile(cat_bridges, b_counts, mid_to_cat)

    print(f"\n  A-side bridge usage profile:")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {a_profile[i]:.4f} ({a_raw.get(c, 0)} tokens)")
    print(f"\n  B-side bridge usage profile:")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {b_profile[i]:.4f} ({b_raw.get(c, 0)} tokens)")

    # JSD
    observed_jsd = jsd(a_profile, b_profile)
    print(f"\n  JSD(A_bridge, B_bridge): {observed_jsd:.6f}")

    # Spearman rho across 8 categories
    rho, rho_p = spearman_rho(a_profile, b_profile)
    print(f"  Spearman rho: {rho:.4f}, p={rho_p:.4f}")

    # Per-category enrichment ratios
    enrichment = {}
    for i, c in enumerate(ALL_CATEGORIES):
        if b_profile[i] > 0:
            ratio = a_profile[i] / b_profile[i]
        else:
            ratio = float('inf') if a_profile[i] > 0 else 1.0
        enrichment[c] = round(ratio, 3)
        if ratio > 1.5 or ratio < 0.67:
            print(f"  ** {c}: A/B ratio = {ratio:.3f} (significant shift)")

    # Permutation null: shuffle category assignments among bridge MIDDLEs
    cat_list = [mid_to_cat[m] for m in cat_bridges]
    null_jsds = []
    for _ in range(N_PERM):
        shuffled_cats = cat_list[:]
        rng.shuffle(shuffled_cats)
        perm_cat_map = dict(zip(cat_bridges, shuffled_cats))
        perm_a_profile, _ = build_category_profile(cat_bridges, a_counts, perm_cat_map)
        perm_b_profile, _ = build_category_profile(cat_bridges, b_counts, perm_cat_map)
        null_jsds.append(jsd(perm_a_profile, perm_b_profile))

    null_mean = sum(null_jsds) / len(null_jsds)
    n_le = sum(1 for nj in null_jsds if nj <= observed_jsd)
    perm_p = (n_le + 1) / (N_PERM + 1)
    print(f"  Null mean JSD: {null_mean:.6f}, Perm p (JSD <= observed): {perm_p:.4f}")

    # Verdict
    if rho > 0.70 and observed_jsd < 0.05:
        verdict = 'PERSISTENT'
    elif rho < 0.50 or observed_jsd > 0.10:
        n_shifted = sum(1 for r in enrichment.values() if r > 1.5 or r < 0.67)
        if n_shifted >= 2:
            verdict = 'SHIFTED'
        else:
            verdict = 'MIXED'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T1_category_persistence',
        'verdict': verdict,
        'n_bridge_with_cat': len(cat_bridges),
        'a_profile': {c: round(a_profile[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'b_profile': {c: round(b_profile[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'a_total_tokens': sum(a_raw.values()),
        'b_total_tokens': sum(b_raw.values()),
        'jsd': round(observed_jsd, 6),
        'spearman_rho': round(rho, 4),
        'spearman_p': round(rho_p, 4),
        'enrichment_ratios': enrichment,
        'null_mean_jsd': round(null_mean, 6),
        'perm_p': round(perm_p, 4),
    }


# ================================================================
# TEST T2: Bridge Delivery vs B Consumption
# ================================================================

def test_t2(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng):
    """Does B passively use what the bridge delivers, or actively reshape?"""
    print("\n=== T2: Bridge Delivery vs B Consumption ===")

    a_counts, b_counts, cat_bridges = precompute_middle_counts(
        a_tokens, b_tokens, mid_to_cat, bridge_middles
    )

    # Delivery profile: bridge MIDDLEs weighted by A-side frequency
    delivery, delivery_raw = build_category_profile(cat_bridges, a_counts, mid_to_cat)

    # Consumption profile: bridge MIDDLEs weighted by B-side frequency
    consumption, consumption_raw = build_category_profile(cat_bridges, b_counts, mid_to_cat)

    # B total profile: ALL B tokens with categories
    b_total_counts = Counter()
    for t in b_tokens:
        mid = t.get('middle')
        cat = mid_to_cat.get(mid) if mid else None
        if cat:
            b_total_counts[cat] += 1
    b_total_sum = sum(b_total_counts.values())
    b_total_profile = [b_total_counts.get(c, 0) / b_total_sum for c in ALL_CATEGORIES]

    print(f"  Delivery (A-weighted bridge):")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {delivery[i]:.4f}")
    print(f"  Consumption (B-weighted bridge):")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {consumption[i]:.4f}")
    print(f"  B total:")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {b_total_profile[i]:.4f}")

    # Three JSDs
    jsd_dc = jsd(delivery, consumption)
    jsd_dt = jsd(delivery, b_total_profile)
    jsd_ct = jsd(consumption, b_total_profile)
    print(f"\n  JSD(delivery, consumption): {jsd_dc:.6f}")
    print(f"  JSD(delivery, B_total): {jsd_dt:.6f}")
    print(f"  JSD(consumption, B_total): {jsd_ct:.6f}")

    # Spearman between delivery and consumption
    rho_dc, rho_dc_p = spearman_rho(delivery, consumption)
    print(f"  Spearman(delivery, consumption): {rho_dc:.4f}, p={rho_dc_p:.4f}")

    # Per-category amplification factor
    amplification = {}
    for i, c in enumerate(ALL_CATEGORIES):
        if delivery[i] > 0.001:
            amp = consumption[i] / delivery[i]
        else:
            amp = float('inf') if consumption[i] > 0.001 else 1.0
        amplification[c] = round(amp, 3)
        if amp > 1.5 or amp < 0.67:
            print(f"  ** {c}: B amplification = {amp:.3f}x")

    # Permutation null: shuffle A-side counts across bridge MIDDLEs
    bridge_list = list(cat_bridges)
    a_count_vals = [a_counts.get(m, 0) for m in bridge_list]
    null_jsds = []
    for _ in range(N_PERM):
        shuffled_a = a_count_vals[:]
        rng.shuffle(shuffled_a)
        perm_a_counts = dict(zip(bridge_list, shuffled_a))
        perm_delivery, _ = build_category_profile(cat_bridges, perm_a_counts, mid_to_cat)
        null_jsds.append(jsd(perm_delivery, consumption))

    null_mean = sum(null_jsds) / len(null_jsds)
    n_le = sum(1 for nj in null_jsds if nj <= jsd_dc)
    perm_p = (n_le + 1) / (N_PERM + 1)
    print(f"  Null mean JSD(delivery, consumption): {null_mean:.6f}, Perm p: {perm_p:.4f}")

    # Mode correlation: B folios with high vs low THERMAL delivery
    # Compute per-B-folio bridge THERMAL fraction
    b_folio_bridge_thermal = defaultdict(lambda: {'thermal': 0, 'total': 0})
    for t in b_tokens:
        mid = t.get('middle')
        if mid and mid in cat_bridges:
            cat = mid_to_cat.get(mid)
            if cat:
                b_folio_bridge_thermal[t['folio']]['total'] += 1
                if cat == 'THERMAL':
                    b_folio_bridge_thermal[t['folio']]['thermal'] += 1

    folio_thermal_fracs = {}
    for fol, d in b_folio_bridge_thermal.items():
        if d['total'] >= 10:
            folio_thermal_fracs[fol] = d['thermal'] / d['total']

    if len(folio_thermal_fracs) >= 8:
        sorted_folios = sorted(folio_thermal_fracs.items(), key=lambda x: x[1])
        n_q = len(sorted_folios) // 4
        low_folios = {f for f, _ in sorted_folios[:n_q]}
        high_folios = {f for f, _ in sorted_folios[-n_q:]}

        # Compute mode A fraction per folio (using suffix mode centroids)
        from suffix_mode_assignment import classify_suffix_mode, suffix_category
        folio_lines = defaultdict(lambda: defaultdict(list))
        for t in b_tokens:
            t_copy = dict(t)
            suf = t_copy.get('suffix', '') or ''
            t_copy['suffix_cat'] = suffix_category(suf)
            folio_lines[t_copy['folio']][t_copy['line']].append(t_copy)

        folio_mode_a_frac = {}
        for fol, lines in folio_lines.items():
            n_a = 0
            n_classified = 0
            for line_num, line_toks in lines.items():
                mode = classify_suffix_mode(line_toks)
                if mode is not None:
                    n_classified += 1
                    if mode == 'A':
                        n_a += 1
            if n_classified >= 5:
                folio_mode_a_frac[fol] = n_a / n_classified

        high_mode_a = [folio_mode_a_frac[f] for f in high_folios if f in folio_mode_a_frac]
        low_mode_a = [folio_mode_a_frac[f] for f in low_folios if f in folio_mode_a_frac]

        if high_mode_a and low_mode_a:
            mw_u, mw_z, mw_p = mann_whitney_u(high_mode_a, low_mode_a)
            mean_high = sum(high_mode_a) / len(high_mode_a)
            mean_low = sum(low_mode_a) / len(low_mode_a)
            print(f"\n  Mode correlation: high-THERMAL folios mode_A={mean_high:.3f} (n={len(high_mode_a)})")
            print(f"                    low-THERMAL folios mode_A={mean_low:.3f} (n={len(low_mode_a)})")
            print(f"                    Mann-Whitney Z={mw_z:.3f}, p={mw_p:.4f}")
            mode_result = {
                'high_thermal_mean_mode_a': round(mean_high, 4),
                'low_thermal_mean_mode_a': round(mean_low, 4),
                'n_high': len(high_mode_a),
                'n_low': len(low_mode_a),
                'mann_whitney_z': round(mw_z, 3),
                'mann_whitney_p': round(mw_p, 4),
            }
        else:
            mode_result = {'note': 'insufficient data'}
    else:
        mode_result = {'note': 'insufficient folios'}

    # Verdict
    n_amp_shifted = sum(1 for a in amplification.values()
                        if a > 1.5 or (a < 0.67 and a != float('inf')))
    if jsd_dc < 0.05 and rho_dc > 0.80:
        verdict = 'FLOW'
    elif jsd_dc > 0.05 and n_amp_shifted >= 2 and perm_p < 0.01:
        verdict = 'RESHAPING'
    elif jsd_dc > 0.05 and n_amp_shifted >= 2:
        verdict = 'MIXED'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T2_bridge_delivery_consumption',
        'verdict': verdict,
        'delivery_profile': {c: round(delivery[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'consumption_profile': {c: round(consumption[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'b_total_profile': {c: round(b_total_profile[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'jsd_delivery_consumption': round(jsd_dc, 6),
        'jsd_delivery_total': round(jsd_dt, 6),
        'jsd_consumption_total': round(jsd_ct, 6),
        'spearman_dc': round(rho_dc, 4),
        'spearman_dc_p': round(rho_dc_p, 4),
        'amplification': amplification,
        'null_mean_jsd': round(null_mean, 6),
        'perm_p': round(perm_p, 4),
        'mode_correlation': mode_result,
    }


# ================================================================
# TEST T3: Section-Level Category Flow Through Bridge
# ================================================================

def test_t3(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng):
    """Does A section identity create category differentiation in bridge usage?"""
    print("\n=== T3: Section-Level Category Flow Through Bridge ===")

    cat_bridges = {m for m in bridge_middles if m in mid_to_cat}

    # Per A-section bridge usage counts
    a_section_counts = defaultdict(Counter)  # section -> Counter({cat: count})
    for t in a_tokens:
        mid = t.get('middle')
        if mid and mid in cat_bridges:
            cat = mid_to_cat.get(mid)
            if cat:
                a_section_counts[t['section']][cat] += 1

    a_sections = sorted(a_section_counts.keys())
    print(f"  A sections with bridge tokens: {a_sections}")

    # Build per-section profiles
    a_section_profiles = {}
    for sec in a_sections:
        total = sum(a_section_counts[sec].values())
        profile = [a_section_counts[sec].get(c, 0) / total for c in ALL_CATEGORIES]
        a_section_profiles[sec] = profile
        print(f"  A-{sec}: n={total}")
        for i, c in enumerate(ALL_CATEGORIES):
            if profile[i] > 0.05:
                print(f"    {c}: {profile[i]:.4f}")

    # Chi-squared: A sections x categories
    chi2_val, chi2_p, chi2_n = chi2_independence(dict(a_section_counts))
    n_cats = len(ALL_CATEGORIES)
    n_secs = len(a_sections)
    min_dim = min(n_secs, n_cats) - 1
    v = math.sqrt(chi2_val / (chi2_n * min_dim)) if chi2_n * min_dim > 0 else 0.0
    print(f"\n  Chi2(A sections x categories): {chi2_val:.1f}, V={v:.4f}, p={chi2_p:.6f}")

    # Pairwise JSD between A sections
    pairwise_jsds = {}
    for i, s1 in enumerate(a_sections):
        for j, s2 in enumerate(a_sections):
            if j > i:
                d = jsd(a_section_profiles[s1], a_section_profiles[s2])
                pairwise_jsds[f"{s1}-{s2}"] = round(d, 6)
                print(f"  JSD(A-{s1}, A-{s2}): {d:.6f}")

    # Per B-section category profiles (all B tokens)
    b_section_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t.get('middle')
        cat = mid_to_cat.get(mid) if mid else None
        if cat:
            b_section_counts[t['section']][cat] += 1

    b_sections = sorted(b_section_counts.keys())
    b_section_profiles = {}
    for sec in b_sections:
        total = sum(b_section_counts[sec].values())
        profile = [b_section_counts[sec].get(c, 0) / total for c in ALL_CATEGORIES]
        b_section_profiles[sec] = profile

    # Cross-system correlation for shared sections
    shared_sections = sorted(set(a_sections) & set(b_sections))
    cross_correlations = {}
    for sec in shared_sections:
        r, r_p = spearman_rho(a_section_profiles[sec], b_section_profiles[sec])
        cross_correlations[sec] = {'rho': round(r, 4), 'p': round(r_p, 4)}
        print(f"  Cross-system rho (A-{sec} vs B-{sec}): {r:.4f}, p={r_p:.4f}")

    # Permutation null: shuffle A-section assignments of A tokens
    a_section_list = [t['section'] for t in a_tokens if t.get('middle') in cat_bridges
                      and mid_to_cat.get(t.get('middle'))]
    null_chi2s = []
    for _ in range(N_PERM):
        shuffled_secs = a_section_list[:]
        rng.shuffle(shuffled_secs)
        perm_counts = defaultdict(Counter)
        idx = 0
        for t in a_tokens:
            mid = t.get('middle')
            if mid and mid in cat_bridges:
                cat = mid_to_cat.get(mid)
                if cat:
                    perm_counts[shuffled_secs[idx]][cat] += 1
                    idx += 1
        perm_chi2, _, _ = chi2_independence(dict(perm_counts))
        null_chi2s.append(perm_chi2)

    null_mean_chi2 = sum(null_chi2s) / len(null_chi2s)
    n_ge = sum(1 for nc in null_chi2s if nc >= chi2_val)
    perm_p = (n_ge + 1) / (N_PERM + 1)
    print(f"  Null mean chi2: {null_mean_chi2:.1f}, Perm p: {perm_p:.4f}")

    # Verdict
    any_cross_sig = any(cc['p'] < 0.05 and cc['rho'] > 0.50
                        for cc in cross_correlations.values())
    if chi2_p < 0.01 and any_cross_sig and perm_p < 0.01:
        verdict = 'SECTION_FLOW'
    elif chi2_p > 0.10:
        verdict = 'SECTION_BLIND'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T3_section_flow',
        'verdict': verdict,
        'a_sections': a_sections,
        'chi2': round(chi2_val, 2),
        'cramers_v': round(v, 4),
        'chi2_p': chi2_p,
        'pairwise_jsds': pairwise_jsds,
        'cross_correlations': cross_correlations,
        'shared_sections': shared_sections,
        'null_mean_chi2': round(null_mean_chi2, 1),
        'perm_p': round(perm_p, 4),
        'a_section_profiles': {s: {c: round(p, 4) for c, p in zip(ALL_CATEGORIES, prof)}
                                for s, prof in a_section_profiles.items()},
    }


# ================================================================
# TEST T4: Dark Pipeline Category Manifestation in B
# ================================================================

def test_t4(a_tokens, b_tokens, dark_middles, mid_to_cat, bridge_middles, rng):
    """Does the dark pipeline carry A-organized categories into B?"""
    print("\n=== T4: Dark Pipeline Category Manifestation in B ===")

    a_counts, b_counts, cat_darks = precompute_middle_counts(
        a_tokens, b_tokens, mid_to_cat, dark_middles
    )
    print(f"  Dark MIDDLEs with category: {len(cat_darks)}")
    print(f"  Dark MIDDLEs with A tokens: {sum(1 for m in cat_darks if a_counts.get(m, 0) > 0)}")
    print(f"  Dark MIDDLEs with B tokens: {sum(1 for m in cat_darks if b_counts.get(m, 0) > 0)}")

    # A-side and B-side dark pipeline category profiles
    a_dark_profile, a_dark_raw = build_category_profile(cat_darks, a_counts, mid_to_cat)
    b_dark_profile, b_dark_raw = build_category_profile(cat_darks, b_counts, mid_to_cat)

    print(f"\n  A-side dark profile:")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {a_dark_profile[i]:.4f} ({a_dark_raw.get(c, 0)} tokens)")
    print(f"  B-side dark profile:")
    for i, c in enumerate(ALL_CATEGORIES):
        print(f"    {c}: {b_dark_profile[i]:.4f} ({b_dark_raw.get(c, 0)} tokens)")

    dark_jsd = jsd(a_dark_profile, b_dark_profile)
    dark_rho, dark_rho_p = spearman_rho(a_dark_profile, b_dark_profile)
    print(f"\n  JSD(A_dark, B_dark): {dark_jsd:.6f}")
    print(f"  Spearman rho: {dark_rho:.4f}, p={dark_rho_p:.4f}")

    # Per-B-section dark pipeline category profile
    b_sec_dark_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t.get('middle')
        if mid and mid in cat_darks:
            cat = mid_to_cat.get(mid)
            if cat:
                b_sec_dark_counts[t['section']][cat] += 1

    b_sections = sorted(b_sec_dark_counts.keys())
    print(f"\n  B sections with dark tokens: {b_sections}")

    # Chi-squared: B sections x dark categories
    if len(b_sections) >= 2:
        chi2_val, chi2_p, chi2_n = chi2_independence(dict(b_sec_dark_counts))
        min_dim = min(len(b_sections), len(ALL_CATEGORIES)) - 1
        v = math.sqrt(chi2_val / (chi2_n * min_dim)) if chi2_n * min_dim > 0 else 0.0
        print(f"  Chi2(B sections x dark cats): {chi2_val:.1f}, V={v:.4f}, p={chi2_p:.6f}")
    else:
        chi2_val, chi2_p, v = 0.0, 1.0, 0.0

    # Permutation null for section chi-squared
    b_dark_sec_list = []
    for t in b_tokens:
        mid = t.get('middle')
        if mid and mid in cat_darks and mid_to_cat.get(mid):
            b_dark_sec_list.append(t['section'])

    null_chi2s = []
    for _ in range(N_PERM):
        shuffled_secs = b_dark_sec_list[:]
        rng.shuffle(shuffled_secs)
        perm_counts = defaultdict(Counter)
        idx = 0
        for t in b_tokens:
            mid = t.get('middle')
            if mid and mid in cat_darks:
                cat = mid_to_cat.get(mid)
                if cat:
                    perm_counts[shuffled_secs[idx]][cat] += 1
                    idx += 1
        if len(perm_counts) >= 2:
            pc, _, _ = chi2_independence(dict(perm_counts))
            null_chi2s.append(pc)

    if null_chi2s:
        null_mean = sum(null_chi2s) / len(null_chi2s)
        n_ge = sum(1 for nc in null_chi2s if nc >= chi2_val)
        sec_perm_p = (n_ge + 1) / (N_PERM + 1)
    else:
        null_mean = 0.0
        sec_perm_p = 1.0
    print(f"  Section chi2 null mean: {null_mean:.1f}, perm p: {sec_perm_p:.4f}")

    # Correlate B-section dark category with B-section total (grammar) category
    b_sec_total_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t.get('middle')
        cat = mid_to_cat.get(mid) if mid else None
        if cat:
            b_sec_total_counts[t['section']][cat] += 1

    dark_grammar_corrs = {}
    for sec in b_sections:
        if sec not in b_sec_total_counts:
            continue
        dark_total = sum(b_sec_dark_counts[sec].values())
        gram_total = sum(b_sec_total_counts[sec].values())
        if dark_total < 10 or gram_total < 10:
            continue
        dark_prof = [b_sec_dark_counts[sec].get(c, 0) / dark_total for c in ALL_CATEGORIES]
        gram_prof = [b_sec_total_counts[sec].get(c, 0) / gram_total for c in ALL_CATEGORIES]
        r, r_p = spearman_rho(dark_prof, gram_prof)
        dark_grammar_corrs[sec] = {'rho': round(r, 4), 'p': round(r_p, 4)}
        print(f"  B-{sec}: dark-grammar rho={r:.4f}")

    # Bridge-dark cross-check per B section
    cat_bridges_set = {m for m in bridge_middles if m in mid_to_cat}
    b_sec_bridge_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t.get('middle')
        if mid and mid in cat_bridges_set:
            cat = mid_to_cat.get(mid)
            if cat:
                b_sec_bridge_counts[t['section']][cat] += 1

    bridge_dark_corrs = {}
    for sec in b_sections:
        if sec not in b_sec_bridge_counts:
            continue
        br_total = sum(b_sec_bridge_counts[sec].values())
        dk_total = sum(b_sec_dark_counts[sec].values())
        if br_total < 10 or dk_total < 10:
            continue
        br_prof = [b_sec_bridge_counts[sec].get(c, 0) / br_total for c in ALL_CATEGORIES]
        dk_prof = [b_sec_dark_counts[sec].get(c, 0) / dk_total for c in ALL_CATEGORIES]
        r, r_p = spearman_rho(br_prof, dk_prof)
        bridge_dark_corrs[sec] = {'rho': round(r, 4), 'p': round(r_p, 4)}
        print(f"  B-{sec}: bridge-dark rho={r:.4f}")

    # Overall bridge-dark category correlation (B-wide)
    _, b_bridge_counts_set, _ = precompute_middle_counts(
        a_tokens, b_tokens, mid_to_cat, bridge_middles
    )
    b_bridge_profile, _ = build_category_profile(cat_bridges_set, b_bridge_counts_set, mid_to_cat)
    bd_rho, bd_rho_p = spearman_rho(b_bridge_profile, b_dark_profile)
    print(f"\n  Overall bridge-dark category rho (B-wide): {bd_rho:.4f}, p={bd_rho_p:.4f}")

    # Verdict
    if dark_jsd < 0.05 and sec_perm_p < 0.01:
        verdict = 'PRESERVED'
    elif dark_jsd > 0.10:
        mean_dg_rho = (sum(d['rho'] for d in dark_grammar_corrs.values()) /
                       len(dark_grammar_corrs)) if dark_grammar_corrs else 0.0
        if mean_dg_rho < 0.30:
            verdict = 'INDEPENDENT'
        else:
            verdict = 'MIXED'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T4_dark_pipeline_categories',
        'verdict': verdict,
        'n_dark_with_cat': len(cat_darks),
        'a_dark_profile': {c: round(a_dark_profile[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'b_dark_profile': {c: round(b_dark_profile[i], 4) for i, c in enumerate(ALL_CATEGORIES)},
        'a_dark_tokens': sum(a_dark_raw.values()),
        'b_dark_tokens': sum(b_dark_raw.values()),
        'jsd_a_b_dark': round(dark_jsd, 6),
        'spearman_rho': round(dark_rho, 4),
        'spearman_p': round(dark_rho_p, 4),
        'section_chi2': round(chi2_val, 2),
        'section_v': round(v, 4),
        'section_chi2_p': chi2_p,
        'section_perm_p': round(sec_perm_p, 4),
        'dark_grammar_correlations': dark_grammar_corrs,
        'bridge_dark_correlations': bridge_dark_corrs,
        'overall_bridge_dark_rho': round(bd_rho, 4),
        'overall_bridge_dark_p': round(bd_rho_p, 4),
    }


# ================================================================
# MAIN
# ================================================================

def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("Phase 471: A_B_CATEGORY_FLOW")
    print("=" * 60)

    # Load data
    print("\nLoading data via Phase 452 load_all_data()...")
    a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles, \
        bridge_middles, dark_middles = load_all_data()

    # Run 4 tests
    results = {}
    results['T1'] = test_t1(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng)
    results['T2'] = test_t2(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng)
    results['T3'] = test_t3(a_tokens, b_tokens, bridge_middles, mid_to_cat, rng)
    results['T4'] = test_t4(a_tokens, b_tokens, dark_middles, mid_to_cat, bridge_middles, rng)

    # Summary
    dt = time.time() - t0
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = {}
    for key in ['T1', 'T2', 'T3', 'T4']:
        v = results[key]['verdict']
        verdicts[key] = v
        print(f"  {key}: {v}")

    results['meta'] = {
        'phase': 471,
        'name': 'A_B_CATEGORY_FLOW',
        'n_bridge': len(bridge_middles),
        'n_dark': len(dark_middles),
        'n_a_tokens': len(a_tokens),
        'n_b_tokens': len(b_tokens),
        'n_middles_with_category': len(mid_to_cat),
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
        'verdicts': verdicts,
    }

    # Save
    out_path = RESULTS_DIR / "a_b_category_flow.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")
    print(f"Runtime: {dt:.1f}s")


if __name__ == '__main__':
    main()
