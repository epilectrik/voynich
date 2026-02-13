#!/usr/bin/env python3
"""
Phase 333: RECIPE_TRIANGULATION_V2
Tests whether A paragraph handling types predict B-side REGIME compatibility
through the PP filtering cascade, creating a three-way triangulation with
Brunschwig fire degree.

Tests:
  T2 (GATE): PP MIDDLE REGIME specificity
  T1: Handling-type REGIME profile discrimination
  T3: Size-controlled REGIME_4 enrichment
  T4: Brunschwig fire-degree concordance
  T5: Cross-handling-type REGIME gradient
  T6: Brunschwig procedural complexity alignment
"""

import json
import sys
import os
import numpy as np
from collections import Counter
from pathlib import Path
from scipy import stats

# Add project root
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology


def numpy_safe(obj):
    """JSON serializer for numpy types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def load_data():
    """Load all input data files."""
    data = {}

    # 1. REGIME mapping
    with open(ROOT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    data['folio_to_regime'] = {
        folio: info['regime']
        for folio, info in regime_data['regime_assignments'].items()
    }

    # 2. Paragraph profiles
    with open(ROOT / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'a_paragraph_profiles.json') as f:
        profiles_data = json.load(f)
    data['profiles'] = profiles_data['profiles']  # list of dicts

    # 3. Paragraph tokens
    with open(ROOT / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'a_paragraph_tokens.json') as f:
        data['paragraph_tokens'] = json.load(f)

    # 4. Handling type assignments
    with open(ROOT / 'phases' / 'MATERIAL_MAPPING_V2' / 'results' / 'all_categories_validation.json') as f:
        handling_data = json.load(f)
    # Build para_id -> handling_type mapping
    handling_map = {}
    for htype, entries in handling_data['handling_groups'].items():
        for entry in entries:
            handling_map[entry['para_id']] = htype
    data['handling_map'] = handling_map

    # 5. RI/PP MIDDLE classification
    with open(ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json') as f:
        mc = json.load(f)
    data['pp_middles'] = set(mc['a_shared_middles'])  # 404 PP MIDDLEs
    data['ri_middles'] = set(mc['a_exclusive_middles'])  # 609 RI MIDDLEs

    # 6. Brunschwig recipes
    with open(ROOT / 'data' / 'brunschwig_curated_v3.json', encoding='utf-8') as f:
        brun_data = json.load(f)
    data['recipes'] = brun_data['recipes']

    return data


def precompute_middle_regime_counts(data):
    """For each PP MIDDLE, count B token instances per REGIME."""
    tx = Transcript()
    morph = Morphology()
    pp_middles = data['pp_middles']
    folio_to_regime = data['folio_to_regime']

    middle_regime_counts = {}  # {middle: {REGIME_1: n, ...}}

    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue
        folio = token.folio
        if folio not in folio_to_regime:
            continue
        regime = folio_to_regime[folio]
        m = morph.extract(token.word)
        if m.middle and m.middle in pp_middles:
            if m.middle not in middle_regime_counts:
                middle_regime_counts[m.middle] = Counter()
            middle_regime_counts[m.middle][regime] += 1

    return middle_regime_counts


def extract_paragraph_pp_middles(data):
    """Extract set of PP MIDDLEs for each A paragraph."""
    morph = Morphology()
    pp_middles = data['pp_middles']
    paragraph_tokens = data['paragraph_tokens']

    para_pp = {}  # {para_id: set of PP MIDDLEs}
    for para_id, tokens in paragraph_tokens.items():
        pp_set = set()
        for tok in tokens:
            word = tok['word']
            if '*' in word or not word.strip():
                continue
            m = morph.extract(word)
            if m.middle and m.middle in pp_middles:
                pp_set.add(m.middle)
        para_pp[para_id] = pp_set

    return para_pp


def compute_regime_profile(pp_set, middle_regime_counts):
    """Compute token-weighted REGIME profile for a set of PP MIDDLEs."""
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    profile = Counter()
    for mid in pp_set:
        if mid in middle_regime_counts:
            profile += middle_regime_counts[mid]
    total = sum(profile.values())
    if total == 0:
        return None
    return {r: profile.get(r, 0) / total for r in regimes}


def entropy(profile):
    """Shannon entropy of a probability distribution (base e)."""
    vals = [v for v in profile.values() if v > 0]
    return -sum(v * np.log(v) for v in vals)


def run_t2_gate(middle_regime_counts, para_pp, handling_map):
    """T2 (GATE): PP MIDDLE REGIME specificity."""
    print("=== T2 (GATE): PP MIDDLE REGIME Specificity ===")
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    max_entropy = np.log(4)

    # Compute specificity for each PP MIDDLE that appears in B
    specificities = {}
    regime_profiles = {}
    for mid, counts in middle_regime_counts.items():
        total = sum(counts.values())
        if total == 0:
            continue
        profile = {r: counts.get(r, 0) / total for r in regimes}
        h = entropy(profile)
        spec = 1 - h / max_entropy
        specificities[mid] = spec
        regime_profiles[mid] = profile

    specs = list(specificities.values())
    median_spec = float(np.median(specs))
    high_spec_count = sum(1 for s in specs if s > 0.2)

    print(f"  PP MIDDLEs in B: {len(specificities)}")
    print(f"  Median specificity: {median_spec:.4f}")
    print(f"  MIDDLEs with spec > 0.2: {high_spec_count}")

    # Find REGIME_4-heavy MIDDLEs (peak at REGIME_4)
    r4_heavy = {mid for mid, prof in regime_profiles.items()
                if max(prof, key=prof.get) == 'REGIME_4'}

    # Check enrichment in PRECISION paragraphs
    precision_paras = [pid for pid, ht in handling_map.items() if ht == 'precision']
    careful_paras = [pid for pid, ht in handling_map.items() if ht == 'careful']

    precision_r4_count = sum(
        1 for pid in precision_paras
        for mid in para_pp.get(pid, set())
        if mid in r4_heavy
    )
    precision_total = sum(len(para_pp.get(pid, set()) & set(regime_profiles.keys()))
                          for pid in precision_paras)

    careful_r4_count = sum(
        1 for pid in careful_paras
        for mid in para_pp.get(pid, set())
        if mid in r4_heavy
    )
    careful_total = sum(len(para_pp.get(pid, set()) & set(regime_profiles.keys()))
                        for pid in careful_paras)

    # Fisher exact test: is R4-heavy proportion higher in PRECISION?
    table = [
        [precision_r4_count, precision_total - precision_r4_count],
        [careful_r4_count, careful_total - careful_r4_count]
    ]
    fisher_or, fisher_p = stats.fisher_exact(table, alternative='greater')

    prec_r4_rate = precision_r4_count / precision_total if precision_total > 0 else 0
    care_r4_rate = careful_r4_count / careful_total if careful_total > 0 else 0

    print(f"  REGIME_4-heavy MIDDLEs: {len(r4_heavy)}")
    print(f"  PRECISION R4-heavy rate: {prec_r4_rate:.3f} ({precision_r4_count}/{precision_total})")
    print(f"  CAREFUL R4-heavy rate: {care_r4_rate:.3f} ({careful_r4_count}/{careful_total})")
    print(f"  Fisher exact p: {fisher_p:.6f}, OR: {fisher_or:.3f}")

    # Gate evaluation
    gate_spec = median_spec > 0.05
    gate_count = high_spec_count >= 10
    gate_enrichment = fisher_p < 0.05

    if gate_spec and gate_count and gate_enrichment:
        verdict = "PASS"
    elif gate_spec and gate_count:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T2 verdict: {verdict}")

    return {
        'test': 'T2_GATE_REGIME_SPECIFICITY',
        'n_middles': len(specificities),
        'median_specificity': median_spec,
        'high_spec_count': high_spec_count,
        'r4_heavy_count': len(r4_heavy),
        'precision_r4_rate': prec_r4_rate,
        'careful_r4_rate': care_r4_rate,
        'fisher_p': fisher_p,
        'fisher_or': fisher_or,
        'predictions': {
            'median_spec_gt_0.05': gate_spec,
            'high_spec_gte_10': gate_count,
            'r4_enrichment_p_lt_0.05': gate_enrichment
        },
        'verdict': verdict
    }


def run_t1(para_pp, middle_regime_counts, handling_map):
    """T1: Handling-type REGIME profile discrimination."""
    print("\n=== T1: Handling-Type REGIME Profile Discrimination ===")
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    # Compute REGIME profile for each paragraph
    profiles_by_type = {}
    for para_id, pp_set in para_pp.items():
        ht = handling_map.get(para_id, 'unknown')
        if ht == 'unknown':
            continue
        profile = compute_regime_profile(pp_set, middle_regime_counts)
        if profile is None:
            continue
        profiles_by_type.setdefault(ht, []).append(profile)

    # Extract R4 weights per handling type
    r4_by_type = {}
    for ht, profiles in profiles_by_type.items():
        r4_weights = [p['REGIME_4'] for p in profiles]
        r4_by_type[ht] = r4_weights
        print(f"  {ht}: n={len(r4_weights)}, mean_R4={np.mean(r4_weights):.4f}, "
              f"std={np.std(r4_weights):.4f}")

    # Mean profiles per type
    mean_profiles = {}
    for ht, profiles in profiles_by_type.items():
        mean_p = {}
        for r in regimes:
            mean_p[r] = float(np.mean([p[r] for p in profiles]))
        mean_profiles[ht] = mean_p

    # Mann-Whitney: PRECISION vs CAREFUL on R4
    if 'precision' in r4_by_type and 'careful' in r4_by_type:
        prec_r4 = r4_by_type['precision']
        care_r4 = r4_by_type['careful']
        u_stat, mw_p = stats.mannwhitneyu(prec_r4, care_r4, alternative='greater')
        # Cohen's d
        pooled_std = np.sqrt((np.var(prec_r4) + np.var(care_r4)) / 2)
        d = (np.mean(prec_r4) - np.mean(care_r4)) / pooled_std if pooled_std > 0 else 0

        print(f"  PRECISION vs CAREFUL: U={u_stat:.1f}, p={mw_p:.6f}, Cohen's d={d:.3f}")
    else:
        mw_p = 1.0
        d = 0.0

    # Kruskal-Wallis across all types with n>1
    kw_groups = [v for k, v in r4_by_type.items() if len(v) > 1]
    if len(kw_groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*kw_groups)
        print(f"  Kruskal-Wallis: H={kw_stat:.3f}, p={kw_p:.6f}")
    else:
        kw_stat, kw_p = 0, 1.0

    pass_sig = mw_p < 0.05
    pass_effect = d > 0.5
    pass_direction = (np.mean(r4_by_type.get('precision', [0])) >
                      np.mean(r4_by_type.get('careful', [0])))

    if pass_sig and pass_effect:
        verdict = "PASS"
    elif pass_direction and not pass_sig:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T1 verdict: {verdict}")

    return {
        'test': 'T1_HANDLING_TYPE_DISCRIMINATION',
        'mean_profiles': mean_profiles,
        'r4_stats': {ht: {'n': len(vals), 'mean': float(np.mean(vals)),
                          'std': float(np.std(vals))}
                     for ht, vals in r4_by_type.items()},
        'precision_vs_careful': {
            'mann_whitney_p': mw_p,
            'cohens_d': d,
            'direction_correct': pass_direction
        },
        'kruskal_wallis': {'H': kw_stat, 'p': kw_p},
        'predictions': {
            'precision_gt_careful': pass_direction,
            'mann_whitney_p_lt_0.05': pass_sig,
            'cohens_d_gt_0.5': pass_effect
        },
        'verdict': verdict
    }


def run_t3(para_pp, middle_regime_counts, handling_map, all_pp_in_b, n_perms=1000):
    """T3: Size-controlled REGIME_4 enrichment.

    Uses label permutation: keeps each paragraph's PP set and REGIME profile
    fixed, shuffles handling-type labels. Tests whether PRECISION paragraphs'
    mean R4 is unusual compared to random label assignments.
    """
    print("\n=== T3: Size-Controlled REGIME_4 Enrichment (Label Permutation) ===")

    # Compute R4 weight for all non-unknown paragraphs
    all_r4 = []  # (para_id, handling_type, r4_weight)
    for para_id, pp_set in para_pp.items():
        ht = handling_map.get(para_id, 'unknown')
        if ht == 'unknown':
            continue
        pp_in_b = pp_set & all_pp_in_b
        if len(pp_in_b) == 0:
            continue
        profile = compute_regime_profile(pp_in_b, middle_regime_counts)
        if profile is None:
            continue
        all_r4.append((para_id, ht, profile['REGIME_4']))

    n_precision = sum(1 for _, ht, _ in all_r4 if ht == 'precision')
    r4_values = np.array([r4 for _, _, r4 in all_r4])
    labels = [ht for _, ht, _ in all_r4]

    # Observed: mean R4 of PRECISION paragraphs
    obs_prec_r4 = np.mean([r4 for _, ht, r4 in all_r4 if ht == 'precision'])
    obs_overall_r4 = np.mean(r4_values)

    print(f"  Total paragraphs: {len(all_r4)}, PRECISION: {n_precision}")
    print(f"  Observed PRECISION mean R4: {obs_prec_r4:.6f}")
    print(f"  Overall mean R4: {obs_overall_r4:.6f}")
    print(f"  Difference: {obs_prec_r4 - obs_overall_r4:.6f}")

    # Permutation test
    rng = np.random.RandomState(42)
    null_means = []
    for _ in range(n_perms):
        perm_idx = rng.permutation(len(r4_values))
        perm_prec_r4 = np.mean(r4_values[perm_idx[:n_precision]])
        null_means.append(perm_prec_r4)

    null_means = np.array(null_means)
    # Two-sided: how extreme is the observed PRECISION mean?
    perm_p = float(np.mean(np.abs(null_means - obs_overall_r4) >=
                           np.abs(obs_prec_r4 - obs_overall_r4)))
    # Directional: is PRECISION R4 higher than expected?
    perm_p_greater = float(np.mean(null_means >= obs_prec_r4))

    percentile = float(np.mean(null_means <= obs_prec_r4) * 100)

    print(f"  Permutation p (two-sided): {perm_p:.4f}")
    print(f"  Permutation p (greater): {perm_p_greater:.4f}")
    print(f"  PRECISION R4 percentile: {percentile:.1f}%")

    # Individual paragraph percentiles (vs all other paragraphs of same handling type excluded)
    para_percentiles = []
    for pid, ht, r4 in all_r4:
        if ht != 'precision':
            continue
        # What percentile is this paragraph among ALL paragraphs?
        pctl = float(np.mean(r4_values <= r4) * 100)
        para_percentiles.append({'para_id': pid, 'r4': r4, 'percentile': pctl})
        print(f"  {pid}: R4={r4:.4f}, percentile={pctl:.1f}% (among all)")

    above_60 = sum(1 for p in para_percentiles if p['percentile'] >= 60)

    pass_mean = percentile > 70
    pass_direction = obs_prec_r4 > obs_overall_r4

    if pass_mean and perm_p < 0.05:
        verdict = "PASS"
    elif percentile > 55:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T3 verdict: {verdict}")

    return {
        'test': 'T3_SIZE_CONTROLLED_R4_ENRICHMENT',
        'method': 'label_permutation',
        'n_total': len(all_r4),
        'n_precision': n_precision,
        'observed_precision_mean_r4': obs_prec_r4,
        'overall_mean_r4': obs_overall_r4,
        'difference': obs_prec_r4 - obs_overall_r4,
        'percentile': percentile,
        'perm_p_two_sided': perm_p,
        'perm_p_greater': perm_p_greater,
        'n_permutations': n_perms,
        'para_percentiles': para_percentiles,
        'above_60th_count': above_60,
        'predictions': {
            'percentile_gt_70': pass_mean,
            'direction_correct': pass_direction
        },
        'verdict': verdict
    }


def run_t4(mean_profiles):
    """T4: Brunschwig fire-degree concordance."""
    print("\n=== T4: Brunschwig Fire-Degree Concordance ===")

    # Mapping from BRSC:
    # degree 1 -> REGIME_2, degree 2 -> REGIME_1, degree 3 -> REGIME_3, degree 4 -> REGIME_4
    # Handling type -> Brunschwig analog:
    # GENTLE (flowers, degree 1) -> expect peak REGIME_2
    # CAREFUL (standard herbs, degree 2) -> expect peak REGIME_1
    # STANDARD (hot/dry herbs, degree 3) -> expect peak REGIME_3
    # PRECISION (animals/precision, degree 4) -> expect peak REGIME_4
    expected_peaks = {
        'gentle': 'REGIME_2',
        'careful': 'REGIME_1',
        'standard': 'REGIME_3',
        'precision': 'REGIME_4'
    }

    concordant = 0
    results = {}
    for ht, expected in expected_peaks.items():
        if ht not in mean_profiles:
            results[ht] = {'expected': expected, 'observed': 'N/A', 'concordant': False}
            continue
        profile = mean_profiles[ht]
        observed_peak = max(profile, key=profile.get)
        is_concordant = observed_peak == expected
        if is_concordant:
            concordant += 1
        results[ht] = {
            'expected': expected,
            'observed': observed_peak,
            'concordant': is_concordant,
            'profile': profile
        }
        print(f"  {ht}: expected={expected}, observed={observed_peak}, "
              f"{'MATCH' if is_concordant else 'MISS'}")

    # Binomial test: 1/4 base rate
    binom_result = stats.binomtest(concordant, len(expected_peaks), 0.25,
                                    alternative='greater')
    binom_p = float(binom_result.pvalue)

    print(f"  Concordant: {concordant}/{len(expected_peaks)}, binom p={binom_p:.4f}")

    if concordant >= 3:
        verdict = "PASS"
    elif concordant == 2 and results.get('precision', {}).get('concordant', False):
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T4 verdict: {verdict}")

    return {
        'test': 'T4_FIRE_DEGREE_CONCORDANCE',
        'expected_mapping': expected_peaks,
        'results': results,
        'concordant_count': concordant,
        'total': len(expected_peaks),
        'binom_p': binom_p,
        'predictions': {
            'concordant_gte_3': concordant >= 3,
            'precision_concordant': results.get('precision', {}).get('concordant', False)
        },
        'verdict': verdict
    }


def run_t5(r4_by_type):
    """T5: Cross-handling-type REGIME gradient."""
    print("\n=== T5: Cross-Handling-Type REGIME Gradient ===")

    # Test monotonic ordering: CAREFUL < STANDARD < PRECISION for R4 weight
    order = ['careful', 'standard', 'precision']
    means = {}
    groups = []
    for ht in order:
        if ht in r4_by_type and len(r4_by_type[ht]) > 0:
            means[ht] = float(np.mean(r4_by_type[ht]))
            groups.append(r4_by_type[ht])
            print(f"  {ht}: mean_R4={means[ht]:.4f}, n={len(r4_by_type[ht])}")

    # Check ordering
    ordered_means = [means.get(ht, None) for ht in order if ht in means]
    correct_order = all(ordered_means[i] < ordered_means[i + 1]
                        for i in range(len(ordered_means) - 1))
    print(f"  Ordering correct (CAREFUL < STANDARD < PRECISION): {correct_order}")

    # Jonckheere-Terpstra approximation via Spearman on group labels
    if len(groups) >= 2:
        all_vals = []
        all_labels = []
        for i, g in enumerate(groups):
            all_vals.extend(g)
            all_labels.extend([i] * len(g))
        jt_rho, jt_p = stats.spearmanr(all_labels, all_vals)
        print(f"  Spearman rho={jt_rho:.4f}, p={jt_p:.6f}")
    else:
        jt_rho, jt_p = 0, 1.0

    if correct_order and jt_p < 0.05:
        verdict = "PASS"
    elif correct_order:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T5 verdict: {verdict}")

    return {
        'test': 'T5_REGIME_GRADIENT',
        'means': means,
        'correct_order': correct_order,
        'spearman_rho': jt_rho,
        'spearman_p': jt_p,
        'predictions': {
            'order_correct': correct_order,
            'spearman_p_lt_0.05': jt_p < 0.05
        },
        'verdict': verdict
    }


def run_t6(recipes, para_pp, handling_map):
    """T6: Brunschwig procedural complexity alignment."""
    print("\n=== T6: Brunschwig Procedural Complexity Alignment ===")

    # Brunschwig: mean step count per material class
    class_steps = {}
    for recipe in recipes:
        mc = recipe.get('material_class', 'unknown')
        steps = len(recipe.get('procedural_steps') or [])
        class_steps.setdefault(mc, []).append(steps)

    print("  Brunschwig step counts by material class:")
    for mc, steps in sorted(class_steps.items()):
        print(f"    {mc}: mean={np.mean(steps):.1f}, n={len(steps)}")

    # Map material classes to handling types
    # herb/moderate_herb -> CAREFUL, hot_dry_herb/root -> STANDARD, animal -> PRECISION
    class_to_handling = {
        'herb': 'careful', 'moderate_herb': 'careful', 'fruit': 'careful',
        'hot_dry_herb': 'standard', 'root': 'standard',
        'animal': 'precision',
        'flower': 'gentle',
        'plant_parasite': 'standard'
    }

    # Aggregate Brunschwig steps by handling type
    brun_steps_by_ht = {}
    for mc, steps in class_steps.items():
        ht = class_to_handling.get(mc)
        if ht:
            brun_steps_by_ht.setdefault(ht, []).extend(steps)

    # Voynich PP pool size by handling type
    voynich_pp_by_ht = {}
    for pid, pp_set in para_pp.items():
        ht = handling_map.get(pid, 'unknown')
        if ht != 'unknown':
            voynich_pp_by_ht.setdefault(ht, []).append(len(pp_set))

    # Compare
    print("\n  Comparison:")
    ht_order = ['gentle', 'careful', 'standard', 'precision']
    brun_means = []
    voyn_means = []
    for ht in ht_order:
        b_steps = brun_steps_by_ht.get(ht, [])
        v_pp = voynich_pp_by_ht.get(ht, [])
        b_mean = float(np.mean(b_steps)) if b_steps else None
        v_mean = float(np.mean(v_pp)) if v_pp else None
        b_str = f"{b_mean:.1f}" if b_mean is not None else "N/A"
        v_str = f"{v_mean:.1f}" if v_mean is not None else "N/A"
        print(f"    {ht}: brun_steps={b_str} (n={len(b_steps)}), "
              f"voynich_pp={v_str} (n={len(v_pp)})")
        if b_mean is not None and v_mean is not None:
            brun_means.append(b_mean)
            voyn_means.append(v_mean)

    # Spearman correlation
    if len(brun_means) >= 3:
        rho, rho_p = stats.spearmanr(brun_means, voyn_means)
        print(f"  Spearman rho={rho:.4f}, p={rho_p:.4f}")
    else:
        rho, rho_p = 0, 1.0

    # Check direction: PRECISION has larger PP than CAREFUL?
    prec_pp = voynich_pp_by_ht.get('precision', [])
    care_pp = voynich_pp_by_ht.get('careful', [])
    direction_correct = (np.mean(prec_pp) > np.mean(care_pp)
                         if prec_pp and care_pp else False)

    if rho > 0.5 and len(brun_means) >= 3:
        verdict = "PASS"
    elif direction_correct:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  T6 verdict: {verdict}")

    return {
        'test': 'T6_PROCEDURAL_COMPLEXITY',
        'brunschwig_steps': {ht: {'mean': float(np.mean(v)), 'n': len(v)}
                             for ht, v in brun_steps_by_ht.items()},
        'voynich_pp_size': {ht: {'mean': float(np.mean(v)), 'n': len(v)}
                            for ht, v in voynich_pp_by_ht.items()},
        'correlation': {'rho': rho, 'p': rho_p, 'n_pairs': len(brun_means)},
        'direction_correct': direction_correct,
        'predictions': {
            'rho_gt_0.5': rho > 0.5,
            'precision_pp_gt_careful': direction_correct
        },
        'verdict': verdict
    }


def synthesize_verdict(results):
    """Determine overall verdict from test results."""
    t2 = results['T2']
    t1 = results['T1']
    t3 = results['T3']
    t4 = results['T4']
    t5 = results['T5']
    t6 = results['T6']

    pass_count = sum(1 for t in [t1, t3, t4, t5, t6] if t['verdict'] == 'PASS')

    if t2['verdict'] == 'FAIL':
        verdict = 'GATE_FAILURE'
        reason = 'PP MIDDLEs are REGIME-uniform; hypothesis mechanistically impossible'
    elif t3['verdict'] == 'PASS' and pass_count >= 3:
        verdict = 'TRIANGULATION_CONFIRMED'
        reason = f'Three-way convergence with size control ({pass_count}/5 non-gate tests PASS)'
    elif t1['verdict'] == 'PASS' and t4['verdict'] == 'PASS' and t3['verdict'] != 'PASS':
        verdict = 'SIGNAL_WITHOUT_SIZE_CONTROL'
        reason = 'Signal exists but may be size-mediated'
    elif t2['verdict'] == 'PASS' and t3['verdict'] == 'FAIL':
        verdict = 'INFORMATIVE_NULL'
        reason = 'MIDDLEs have REGIME specificity but handling types do not exploit it (C753 confirmed)'
    elif t2['verdict'] == 'PASS' and pass_count >= 1:
        verdict = 'WEAK_SIGNAL'
        reason = f'MIDDLE specificity exists but weak connection to handling types ({pass_count}/5 PASS)'
    else:
        verdict = 'NO_SIGNAL'
        reason = 'No significant triangulation detected'

    return {
        'verdict': verdict,
        'reason': reason,
        'test_verdicts': {
            'T2_GATE': t2['verdict'],
            'T1': t1['verdict'],
            'T3': t3['verdict'],
            'T4': t4['verdict'],
            'T5': t5['verdict'],
            'T6': t6['verdict']
        },
        'pass_count': pass_count
    }


def main():
    print("Phase 333: RECIPE_TRIANGULATION_V2")
    print("=" * 60)

    # Load data
    print("Loading data...")
    data = load_data()
    print(f"  Paragraphs: {len(data['profiles'])}")
    print(f"  Handling types: {Counter(data['handling_map'].values())}")
    print(f"  PP MIDDLEs: {len(data['pp_middles'])}")
    print(f"  B folios with REGIME: {len(data['folio_to_regime'])}")
    print(f"  Brunschwig recipes: {len(data['recipes'])}")

    # Pre-compute
    print("\nPre-computing MIDDLE->REGIME token counts...")
    middle_regime_counts = precompute_middle_regime_counts(data)
    print(f"  PP MIDDLEs found in B: {len(middle_regime_counts)}")

    print("Extracting paragraph PP MIDDLEs...")
    para_pp = extract_paragraph_pp_middles(data)
    pp_sizes = [len(v) for v in para_pp.values()]
    print(f"  Paragraphs with PP: {sum(1 for v in para_pp.values() if len(v) > 0)}/{len(para_pp)}")
    print(f"  Mean PP pool size: {np.mean(pp_sizes):.1f}")

    all_pp_in_b = set(middle_regime_counts.keys())

    # Run tests
    results = {}

    # T2 first (gate)
    results['T2'] = run_t2_gate(middle_regime_counts, para_pp, data['handling_map'])

    # T1
    t1_result = run_t1(para_pp, middle_regime_counts, data['handling_map'])
    results['T1'] = t1_result

    # T3
    results['T3'] = run_t3(para_pp, middle_regime_counts, data['handling_map'],
                           all_pp_in_b)

    # T4 (uses mean profiles from T1)
    results['T4'] = run_t4(t1_result['mean_profiles'])

    # T5 (uses R4 data from T1)
    r4_by_type = {}
    for para_id, pp_set in para_pp.items():
        ht = data['handling_map'].get(para_id, 'unknown')
        if ht == 'unknown':
            continue
        profile = compute_regime_profile(pp_set, middle_regime_counts)
        if profile:
            r4_by_type.setdefault(ht, []).append(profile['REGIME_4'])
    results['T5'] = run_t5(r4_by_type)

    # T6
    results['T6'] = run_t6(data['recipes'], para_pp, data['handling_map'])

    # Synthesis
    print("\n" + "=" * 60)
    synthesis = synthesize_verdict(results)
    print(f"\nOVERALL VERDICT: {synthesis['verdict']}")
    print(f"Reason: {synthesis['reason']}")
    print(f"Test results: {synthesis['test_verdicts']}")

    # Save
    output = {
        'phase': 'RECIPE_TRIANGULATION_V2',
        'phase_number': 333,
        'tests': results,
        'synthesis': synthesis,
        'metadata': {
            'n_paragraphs': len(data['profiles']),
            'n_pp_middles_total': len(data['pp_middles']),
            'n_pp_middles_in_b': len(middle_regime_counts),
            'n_b_folios': len(data['folio_to_regime']),
            'n_recipes': len(data['recipes']),
            'handling_counts': dict(Counter(data['handling_map'].values()))
        }
    }

    out_path = ROOT / 'phases' / 'RECIPE_TRIANGULATION_V2' / 'results' / 'recipe_triangulation.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=numpy_safe)

    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
