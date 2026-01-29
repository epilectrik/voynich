#!/usr/bin/env python3
"""
population_profiles.py - AZC-Med vs B-Native Execution Profiles & EN Sub-Family Prediction

Maps AZC-Mediated and B-Native PP populations to B-side behavioral profiles
(role distribution, hazard participation, REGIME, suffix patterns) and tests
whether EN sub-family membership is predictable from A record composition.

Sections:
1. Load dependencies
2. AZC-Med vs B-Native role & hazard profiles
3. REGIME profile by population
4. Suffix pattern by population
5. EN sub-family prediction from A records
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from math import lgamma, log2

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Role correction per BCSC v1.4 (C560/C581)
ROLE_CORRECTIONS = {'17': 'CORE_CONTROL'}
ROLE_NAMES = ['AUXILIARY', 'CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR']
ROLE_SHORT = {'AUXILIARY': 'AX', 'CORE_CONTROL': 'CC', 'ENERGY_OPERATOR': 'EN',
              'FLOW_OPERATOR': 'FL', 'FREQUENT_OPERATOR': 'FQ'}


# --- Statistical Functions ---

def mannwhitney_u(x, y):
    """Manual Mann-Whitney U test. Returns U, z, p (two-tailed, normal approx)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 0.0, 1.0
    combined = np.concatenate([x, y])
    n = nx + ny
    sorted_idx = np.argsort(combined)
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and combined[sorted_idx[j]] == combined[sorted_idx[i]]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[sorted_idx[k]] = avg_rank
        i = j
    R1 = np.sum(ranks[:nx])
    U1 = R1 - nx * (nx + 1) / 2.0
    U2 = nx * ny - U1
    U = min(U1, U2)
    mu = nx * ny / 2.0
    sigma = np.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return float(U), 0.0, 1.0
    z = (U - mu) / sigma
    p = 2.0 * norm_sf(abs(z))
    return float(U), float(z), float(p)


def norm_sf(z):
    """Standard normal survival function."""
    if z < 0:
        return 1.0 - norm_sf(-z)
    t = 1.0 / (1.0 + 0.2316419 * z)
    d = 0.3989422804014327
    p = d * np.exp(-z * z / 2.0) * (t * (0.319381530 +
        t * (-0.356563782 + t * (1.781477937 +
        t * (-1.821255978 + t * 1.330274429)))))
    return float(p)


def fisher_exact_2x2(a, b, c, d):
    """Fisher's exact test for 2x2 table [[a,b],[c,d]]. Returns odds_ratio, p (two-tailed)."""
    n = a + b + c + d
    if n == 0:
        return 0.0, 1.0

    def lf(x):
        return lgamma(x + 1)

    def table_prob(a, b, c, d):
        return np.exp(lf(a+b) + lf(c+d) + lf(a+c) + lf(b+d) - lf(n) - lf(a) - lf(b) - lf(c) - lf(d))

    p_obs = table_prob(a, b, c, d)

    row1 = a + b
    col1 = a + c
    min_a = max(0, row1 + col1 - n)
    max_a = min(row1, col1)

    p_val = 0.0
    for ai in range(min_a, max_a + 1):
        bi = row1 - ai
        ci = col1 - ai
        di = n - ai - bi - ci
        if bi < 0 or ci < 0 or di < 0:
            continue
        p_i = table_prob(ai, bi, ci, di)
        if p_i <= p_obs + 1e-12:
            p_val += p_i

    p_val = min(p_val, 1.0)

    if b * c == 0:
        odds = float('inf') if a * d > 0 else 0.0
    else:
        odds = (a * d) / (b * c)

    return odds, p_val


def spearman_rho(x, y):
    """Spearman rank correlation. Returns rho, p."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def rank_data(arr):
        sorted_idx = np.argsort(arr)
        ranks = np.empty(n, dtype=float)
        i = 0
        while i < n:
            j = i
            while j < n and arr[sorted_idx[j]] == arr[sorted_idx[i]]:
                j += 1
            avg = (i + j + 1) / 2.0
            for k in range(i, j):
                ranks[sorted_idx[k]] = avg
            i = j
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)
    d = rx - ry
    d2 = np.sum(d * d)
    rho = 1.0 - 6.0 * d2 / (n * (n * n - 1))

    if abs(rho) >= 1.0:
        return float(rho), 0.0
    t_stat = rho * np.sqrt((n - 2) / (1 - rho * rho))
    p = 2.0 * norm_sf(abs(t_stat))
    return float(rho), float(p)


def main():
    print("=" * 70)
    print("POPULATION PROFILES")
    print("Phase: A_TO_B_ROLE_PROJECTION | Script 2 of 3")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / 'results'

    # ================================================================
    # SECTION 1: Load Dependencies
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: Load Dependencies")
    print("=" * 70)

    # Load Script 1 results
    s1_path = results_dir / 'pp_role_foundation.json'
    with open(s1_path, 'r', encoding='utf-8') as f:
        s1 = json.load(f)
    pp_role_map = s1['pp_role_map']
    b_freq = s1['b_middle_frequency']

    azc_med = s1['azc_split']['azc_mediated']
    b_native = s1['azc_split']['b_native']
    print(f"PP role map: {len(pp_role_map)} MIDDLEs")
    print(f"AZC-Mediated: {len(azc_med)}, B-Native: {len(b_native)}")

    matched_azc = [m for m in azc_med if pp_role_map.get(m, {}).get('dominant_role') is not None]
    matched_bn = [m for m in b_native if pp_role_map.get(m, {}).get('dominant_role') is not None]
    print(f"Matched AZC-Med: {len(matched_azc)}, Matched B-Native: {len(matched_bn)}")
    print(f"WARNING: B-Native matched count ({len(matched_bn)}) is very small")

    # Load EN census
    en_path = PROJECT_ROOT / 'phases' / 'EN_ANATOMY' / 'results' / 'en_census.json'
    with open(en_path, 'r', encoding='utf-8') as f:
        en_census = json.load(f)
    qo_classes = set(str(c) for c in en_census['prefix_families']['QO'])
    chsh_classes = set(str(c) for c in en_census['prefix_families']['CH_SH'])
    print(f"EN QO classes: {sorted(qo_classes)}")
    print(f"EN CH_SH classes: {sorted(chsh_classes)}")

    # Load REGIME mapping
    regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_mapping = json.load(f)
    folio_to_regime = {}
    for regime, folios in regime_mapping.items():
        for fol in folios:
            folio_to_regime[fol] = regime
    print(f"REGIME mapping: {len(folio_to_regime)} folios")

    # Load PP classification
    ppc_path = PROJECT_ROOT / 'phases' / 'PP_CLASSIFICATION' / 'results' / 'pp_classification.json'
    with open(ppc_path, 'r', encoding='utf-8') as f:
        ppc_data = json.load(f)
    pp_material = {}
    for mid, info in ppc_data.get('pp_classification', {}).items():
        pp_material[mid] = info.get('material_class', 'UNKNOWN')
    print(f"PP material classifications: {len(pp_material)}")

    # Load class_token_map for FL class identification
    ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    class_to_role = dict(ctm['class_to_role'])
    for cls_id, new_role in ROLE_CORRECTIONS.items():
        class_to_role[cls_id] = new_role

    fl_classes = set(c for c, r in class_to_role.items() if r == 'FLOW_OPERATOR')
    print(f"FL (FLOW_OPERATOR) classes: {sorted(fl_classes)}")

    # Load PP/RI MIDDLE lists
    mc_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes_v2_backup.json'
    with open(mc_path, 'r', encoding='utf-8') as f:
        mc_data = json.load(f)
    pp_middles = set(mc_data['a_shared_middles'])
    ri_middles = set(mc_data['a_exclusive_middles'])

    # Initialize transcript and morphology
    tx = Transcript()
    morph = Morphology()

    # ================================================================
    # SECTION 2: AZC-Med vs B-Native Role & Hazard Profiles
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: AZC-Med vs B-Native Role & Hazard Profiles")
    print("=" * 70)

    # 2a: Fisher's exact test for each role x population (matched PP only)
    print("\n--- Per-Role Fisher's Exact (matched PP) ---")
    fisher_results = {}

    for role in ROLE_NAMES:
        short = ROLE_SHORT[role]
        azc_yes = sum(1 for m in matched_azc if pp_role_map[m]['dominant_role'] == role)
        azc_no = len(matched_azc) - azc_yes
        bn_yes = sum(1 for m in matched_bn if pp_role_map[m]['dominant_role'] == role)
        bn_no = len(matched_bn) - bn_yes

        odds, p = fisher_exact_2x2(azc_yes, azc_no, bn_yes, bn_no)

        fisher_results[role] = {
            'azc_med_count': azc_yes,
            'azc_med_total': len(matched_azc),
            'azc_med_rate': azc_yes / len(matched_azc) if matched_azc else 0.0,
            'b_native_count': bn_yes,
            'b_native_total': len(matched_bn),
            'b_native_rate': bn_yes / len(matched_bn) if matched_bn else 0.0,
            'odds_ratio': odds if odds != float('inf') else 'Inf',
            'p_fisher': p,
            'significant': p < 0.05,
        }
        sig = "*" if p < 0.05 else ""
        azc_pct = azc_yes / len(matched_azc) * 100 if matched_azc else 0
        bn_pct = bn_yes / len(matched_bn) * 100 if matched_bn else 0
        print(f"  {short}: AZC-Med {azc_yes}/{len(matched_azc)} ({azc_pct:.1f}%) vs "
              f"B-Native {bn_yes}/{len(matched_bn)} ({bn_pct:.1f}%) p={p:.4f} {sig}")

    # 2b: Hazard (FL) participation
    print("\n--- FL (Hazard-Adjacent) Participation ---")
    azc_fl = sum(1 for m in matched_azc
                 if any(c in fl_classes for c in pp_role_map[m].get('b_classes', [])))
    bn_fl = sum(1 for m in matched_bn
                if any(c in fl_classes for c in pp_role_map[m].get('b_classes', [])))

    fl_odds, fl_p = fisher_exact_2x2(
        azc_fl, len(matched_azc) - azc_fl,
        bn_fl, len(matched_bn) - bn_fl)

    hazard_results = {
        'fl_classes': sorted(fl_classes),
        'azc_med_fl_count': azc_fl,
        'azc_med_fl_rate': azc_fl / len(matched_azc) if matched_azc else 0.0,
        'b_native_fl_count': bn_fl,
        'b_native_fl_rate': bn_fl / len(matched_bn) if matched_bn else 0.0,
        'odds_ratio': fl_odds if fl_odds != float('inf') else 'Inf',
        'p_fisher': fl_p,
        'significant': fl_p < 0.05,
    }

    azc_fl_pct = azc_fl / len(matched_azc) * 100 if matched_azc else 0
    bn_fl_pct = bn_fl / len(matched_bn) * 100 if matched_bn else 0
    print(f"  AZC-Med FL participation: {azc_fl}/{len(matched_azc)} ({azc_fl_pct:.1f}%)")
    print(f"  B-Native FL participation: {bn_fl}/{len(matched_bn)} ({bn_fl_pct:.1f}%)")
    print(f"  Fisher's p={fl_p:.4f}")

    # 2c: Role purity (single-role vs multi-role)
    print("\n--- Role Purity ---")
    azc_single = sum(1 for m in matched_azc if pp_role_map[m]['n_roles'] == 1)
    azc_multi = len(matched_azc) - azc_single
    bn_single = sum(1 for m in matched_bn if pp_role_map[m]['n_roles'] == 1)
    bn_multi = len(matched_bn) - bn_single

    purity_odds, purity_p = fisher_exact_2x2(azc_single, azc_multi, bn_single, bn_multi)

    purity_results = {
        'azc_med_single': azc_single,
        'azc_med_multi': azc_multi,
        'azc_med_purity': azc_single / len(matched_azc) if matched_azc else 0.0,
        'b_native_single': bn_single,
        'b_native_multi': bn_multi,
        'b_native_purity': bn_single / len(matched_bn) if matched_bn else 0.0,
        'odds_ratio': purity_odds if purity_odds != float('inf') else 'Inf',
        'p_fisher': purity_p,
        'significant': purity_p < 0.05,
    }

    azc_pur = azc_single / len(matched_azc) * 100 if matched_azc else 0
    bn_pur = bn_single / len(matched_bn) * 100 if matched_bn else 0
    print(f"  AZC-Med single-role: {azc_single}/{len(matched_azc)} ({azc_pur:.1f}%)")
    print(f"  B-Native single-role: {bn_single}/{len(matched_bn)} ({bn_pur:.1f}%)")
    print(f"  Fisher's p={purity_p:.4f}")

    # ================================================================
    # SECTION 3: REGIME Profile by Population
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: REGIME Profile by Population")
    print("=" * 70)

    # Single-pass over B tokens: build middle_to_regime_counts and suffix info
    middle_regime_counts = defaultdict(Counter)
    middle_suffix_counts = defaultdict(Counter)
    middle_suffix_total = defaultdict(int)
    middle_suffix_bare = defaultdict(int)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        folio = token.folio
        regime = folio_to_regime.get(folio)
        m = morph.extract(word)
        if not m.middle:
            continue
        mid = m.middle

        if mid in pp_middles:
            if regime:
                middle_regime_counts[mid][regime] += 1
            suffix = m.suffix if m.suffix else 'BARE'
            middle_suffix_counts[mid][suffix] += 1
            middle_suffix_total[mid] += 1
            if suffix == 'BARE':
                middle_suffix_bare[mid] += 1

    print(f"\nPP MIDDLEs with B-side REGIME data: {len(middle_regime_counts)}")
    print(f"PP MIDDLEs with B-side suffix data: {len(middle_suffix_counts)}")

    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    # Per-MIDDLE REGIME distribution vectors
    regime_vectors_azc = []
    regime_mids_azc = []
    regime_vectors_bn = []
    regime_mids_bn = []

    for mid in azc_med:
        if mid in middle_regime_counts:
            counts = middle_regime_counts[mid]
            total = sum(counts.values())
            vec = [counts.get(r, 0) / total for r in regimes]
            regime_vectors_azc.append(vec)
            regime_mids_azc.append(mid)

    for mid in b_native:
        if mid in middle_regime_counts:
            counts = middle_regime_counts[mid]
            total = sum(counts.values())
            vec = [counts.get(r, 0) / total for r in regimes]
            regime_vectors_bn.append(vec)
            regime_mids_bn.append(mid)

    print(f"AZC-Med with REGIME data: {len(regime_vectors_azc)}")
    print(f"B-Native with REGIME data: {len(regime_vectors_bn)}")

    # Compare per-REGIME (Mann-Whitney)
    regime_comparison = {}
    for i, regime in enumerate(regimes):
        azc_vals = [v[i] for v in regime_vectors_azc]
        bn_vals = [v[i] for v in regime_vectors_bn]

        if len(azc_vals) >= 2 and len(bn_vals) >= 2:
            U, z, p = mannwhitney_u(azc_vals, bn_vals)
            regime_comparison[regime] = {
                'azc_mean': float(np.mean(azc_vals)),
                'bn_mean': float(np.mean(bn_vals)),
                'azc_n': len(azc_vals),
                'bn_n': len(bn_vals),
                'U': U, 'z': z, 'p': p,
                'significant': p < 0.05,
            }
            sig = "*" if p < 0.05 else ""
            print(f"  {regime}: AZC={np.mean(azc_vals):.3f} (n={len(azc_vals)}) "
                  f"vs BN={np.mean(bn_vals):.3f} (n={len(bn_vals)}) p={p:.4f} {sig}")
        else:
            regime_comparison[regime] = {
                'azc_mean': float(np.mean(azc_vals)) if azc_vals else None,
                'bn_mean': float(np.mean(bn_vals)) if bn_vals else None,
                'verdict': 'INSUFFICIENT_DATA',
            }
            print(f"  {regime}: insufficient data")

    # REGIME centroid summary
    if regime_vectors_azc and regime_vectors_bn:
        azc_centroid = np.mean(regime_vectors_azc, axis=0)
        bn_centroid = np.mean(regime_vectors_bn, axis=0)
        print(f"\n  AZC-Med REGIME centroid: [{', '.join(f'{v:.3f}' for v in azc_centroid)}]")
        print(f"  B-Native REGIME centroid: [{', '.join(f'{v:.3f}' for v in bn_centroid)}]")
        regime_comparison['centroids'] = {
            'azc_med': azc_centroid.tolist(),
            'b_native': bn_centroid.tolist(),
        }

    # ================================================================
    # SECTION 4: Suffix Pattern by Population
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: Suffix Pattern by Population")
    print("=" * 70)

    azc_suffix_diversity = []
    azc_bare_rates = []
    bn_suffix_diversity = []
    bn_bare_rates = []

    for mid in azc_med:
        if mid in middle_suffix_counts:
            n_suffixes = len(middle_suffix_counts[mid])
            azc_suffix_diversity.append(n_suffixes)
            total = middle_suffix_total[mid]
            bare = middle_suffix_bare.get(mid, 0)
            azc_bare_rates.append(bare / total if total > 0 else 0.0)

    for mid in b_native:
        if mid in middle_suffix_counts:
            n_suffixes = len(middle_suffix_counts[mid])
            bn_suffix_diversity.append(n_suffixes)
            total = middle_suffix_total[mid]
            bare = middle_suffix_bare.get(mid, 0)
            bn_bare_rates.append(bare / total if total > 0 else 0.0)

    print(f"\nAZC-Med with suffix data: {len(azc_suffix_diversity)}")
    print(f"B-Native with suffix data: {len(bn_suffix_diversity)}")

    suffix_results = {}

    if len(azc_suffix_diversity) >= 2 and len(bn_suffix_diversity) >= 2:
        U_div, z_div, p_div = mannwhitney_u(azc_suffix_diversity, bn_suffix_diversity)
        suffix_results['diversity'] = {
            'azc_mean': float(np.mean(azc_suffix_diversity)),
            'azc_median': float(np.median(azc_suffix_diversity)),
            'bn_mean': float(np.mean(bn_suffix_diversity)),
            'bn_median': float(np.median(bn_suffix_diversity)),
            'U': U_div, 'z': z_div, 'p': p_div,
            'significant': p_div < 0.05,
        }
        sig = "*" if p_div < 0.05 else ""
        print(f"  Suffix diversity: AZC mean={np.mean(azc_suffix_diversity):.2f} "
              f"vs BN mean={np.mean(bn_suffix_diversity):.2f} p={p_div:.4f} {sig}")

        U_bare, z_bare, p_bare = mannwhitney_u(azc_bare_rates, bn_bare_rates)
        suffix_results['bare_rate'] = {
            'azc_mean': float(np.mean(azc_bare_rates)),
            'bn_mean': float(np.mean(bn_bare_rates)),
            'U': U_bare, 'z': z_bare, 'p': p_bare,
            'significant': p_bare < 0.05,
        }
        sig = "*" if p_bare < 0.05 else ""
        print(f"  Bare rate: AZC mean={np.mean(azc_bare_rates):.3f} "
              f"vs BN mean={np.mean(bn_bare_rates):.3f} p={p_bare:.4f} {sig}")

        # Frequency-controlled comparison: partial out B-side frequency
        # For both populations, check if suffix differences survive after
        # controlling for B-side token count
        azc_freqs = [b_freq.get(mid, 0) for mid in azc_med if mid in middle_suffix_counts]
        bn_freqs = [b_freq.get(mid, 0) for mid in b_native if mid in middle_suffix_counts]

        if len(azc_freqs) >= 3 and len(bn_freqs) >= 3:
            # Spearman: frequency vs suffix diversity (within AZC-Med)
            all_mids_with_suffix = [m for m in azc_med if m in middle_suffix_counts] + \
                                   [m for m in b_native if m in middle_suffix_counts]
            all_freqs = [b_freq.get(m, 0) for m in all_mids_with_suffix]
            all_divs = [len(middle_suffix_counts[m]) for m in all_mids_with_suffix]
            rho_fd, p_fd = spearman_rho(all_freqs, all_divs)
            suffix_results['freq_diversity_correlation'] = {
                'rho': rho_fd, 'p': p_fd,
                'interpretation': 'Frequency confounds diversity' if rho_fd > 0.5 and p_fd < 0.05
                    else 'Diversity partially independent of frequency',
            }
            print(f"  Freq-diversity correlation: rho={rho_fd:.3f} p={p_fd:.4f}")
            print(f"    -> {suffix_results['freq_diversity_correlation']['interpretation']}")
    else:
        suffix_results['verdict'] = 'INSUFFICIENT_DATA'
        print("  Insufficient data for suffix comparison")

    # ================================================================
    # SECTION 5: EN Sub-Family Prediction from A Records
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 5: EN Sub-Family Prediction from A Records")
    print("=" * 70)

    # 5a: Classify PP MIDDLEs by EN sub-family
    pp_en_class = {}
    for mid, data in pp_role_map.items():
        if data.get('dominant_role') is None:
            continue
        b_classes = set(data.get('b_classes', []))
        qo_count = len(b_classes & qo_classes)
        chsh_count = len(b_classes & chsh_classes)
        en_total = qo_count + chsh_count

        if en_total == 0:
            continue

        qo_score = qo_count / en_total
        chsh_score = chsh_count / en_total

        if qo_score > 0.6:
            subfamily = 'QO'
        elif chsh_score > 0.6:
            subfamily = 'CHSH'
        else:
            subfamily = 'MIXED_EN'

        pp_en_class[mid] = {
            'qo_count': qo_count,
            'chsh_count': chsh_count,
            'en_total': en_total,
            'qo_score': qo_score,
            'subfamily': subfamily,
        }

    subfamily_counts = Counter(v['subfamily'] for v in pp_en_class.values())
    print(f"\nPP MIDDLEs with EN class membership: {len(pp_en_class)}")
    for sf, count in sorted(subfamily_counts.items()):
        print(f"  {sf}: {count}")

    # 5b: Build A-record profiles
    a_records = defaultdict(list)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if not m.middle:
            continue
        mid = m.middle
        key = (token.folio, token.line)
        a_records[key].append({
            'word': word,
            'middle': mid,
            'is_pp': mid in pp_middles,
            'is_ri': mid in ri_middles,
            'prefix': m.prefix,
            'suffix': m.suffix,
        })

    print(f"\nA records loaded: {len(a_records)}")

    # For each record with PP MIDDLEs that have EN class info, compute QO fraction
    record_profiles = []
    for (folio, line), tokens in sorted(a_records.items()):
        pp_with_en = [t for t in tokens if t['is_pp'] and t['middle'] in pp_en_class]
        if len(pp_with_en) < 1:
            continue

        qo_scores = [pp_en_class[t['middle']]['qo_score'] for t in pp_with_en]
        mean_qo = float(np.mean(qo_scores))

        n_total = len(tokens)
        n_pp = sum(1 for t in tokens if t['is_pp'])
        n_ri = sum(1 for t in tokens if t['is_ri'])
        n_en_pp = len(pp_with_en)

        # Material composition
        mat_counts = Counter()
        for t in tokens:
            if t['is_pp'] and t['middle'] in pp_material:
                mat_counts[pp_material[t['middle']]] += 1

        # Prefix composition
        prefixes = [t['prefix'] for t in tokens if t['prefix']]
        qo_prefix_count = sum(1 for p in prefixes if p == 'qo')
        chsh_prefix_count = sum(1 for p in prefixes if p in ('ch', 'sh'))
        total_prefix = qo_prefix_count + chsh_prefix_count
        prefix_qo_frac = qo_prefix_count / total_prefix if total_prefix > 0 else None

        if mean_qo > 0.6:
            record_type = 'QO_DOMINANT'
        elif mean_qo < 0.4:
            record_type = 'CHSH_DOMINANT'
        else:
            record_type = 'MIXED'

        record_profiles.append({
            'folio': folio,
            'line': line,
            'mean_qo_score': mean_qo,
            'record_type': record_type,
            'n_total': n_total,
            'n_pp': n_pp,
            'n_ri': n_ri,
            'n_en_pp': n_en_pp,
            'material_counts': dict(mat_counts),
            'qo_prefix_count': qo_prefix_count,
            'chsh_prefix_count': chsh_prefix_count,
            'prefix_qo_frac': prefix_qo_frac,
        })

    print(f"\nRecords with EN-classified PP: {len(record_profiles)}")
    type_counts = Counter(r['record_type'] for r in record_profiles)
    for rt, count in sorted(type_counts.items()):
        print(f"  {rt}: {count}")

    # 5c: Compare QO-dominant vs CHSH-dominant records
    qo_records = [r for r in record_profiles if r['record_type'] == 'QO_DOMINANT']
    chsh_records = [r for r in record_profiles if r['record_type'] == 'CHSH_DOMINANT']

    print(f"\nQO-dominant records: {len(qo_records)}")
    print(f"CHSH-dominant records: {len(chsh_records)}")

    en_prediction = {}

    if len(qo_records) >= 5 and len(chsh_records) >= 5:
        # Record size
        qo_sizes = [r['n_total'] for r in qo_records]
        chsh_sizes = [r['n_total'] for r in chsh_records]
        U_size, z_size, p_size = mannwhitney_u(qo_sizes, chsh_sizes)

        en_prediction['record_size'] = {
            'qo_mean': float(np.mean(qo_sizes)),
            'qo_median': float(np.median(qo_sizes)),
            'chsh_mean': float(np.mean(chsh_sizes)),
            'chsh_median': float(np.median(chsh_sizes)),
            'U': U_size, 'z': z_size, 'p': p_size,
            'significant': p_size < 0.05,
        }
        sig = "*" if p_size < 0.05 else ""
        print(f"\n  Record size: QO={np.mean(qo_sizes):.1f} vs CHSH={np.mean(chsh_sizes):.1f} p={p_size:.4f} {sig}")

        # RI count
        qo_ri = [r['n_ri'] for r in qo_records]
        chsh_ri = [r['n_ri'] for r in chsh_records]
        U_ri, z_ri, p_ri = mannwhitney_u(qo_ri, chsh_ri)

        en_prediction['ri_count'] = {
            'qo_mean': float(np.mean(qo_ri)),
            'chsh_mean': float(np.mean(chsh_ri)),
            'U': U_ri, 'z': z_ri, 'p': p_ri,
            'significant': p_ri < 0.05,
        }
        sig = "*" if p_ri < 0.05 else ""
        print(f"  RI count: QO={np.mean(qo_ri):.1f} vs CHSH={np.mean(chsh_ri):.1f} p={p_ri:.4f} {sig}")

        # PP count
        qo_pp = [r['n_pp'] for r in qo_records]
        chsh_pp = [r['n_pp'] for r in chsh_records]
        U_pp, z_pp, p_pp = mannwhitney_u(qo_pp, chsh_pp)

        en_prediction['pp_count'] = {
            'qo_mean': float(np.mean(qo_pp)),
            'chsh_mean': float(np.mean(chsh_pp)),
            'U': U_pp, 'z': z_pp, 'p': p_pp,
            'significant': p_pp < 0.05,
        }
        sig = "*" if p_pp < 0.05 else ""
        print(f"  PP count: QO={np.mean(qo_pp):.1f} vs CHSH={np.mean(chsh_pp):.1f} p={p_pp:.4f} {sig}")

        # PREFIX test: does EN sub-family signal go beyond PREFIX?
        valid_records = [r for r in record_profiles if r['prefix_qo_frac'] is not None]
        if len(valid_records) >= 10:
            prefix_fracs = [r['prefix_qo_frac'] for r in valid_records]
            en_scores = [r['mean_qo_score'] for r in valid_records]
            rho, p_rho = spearman_rho(prefix_fracs, en_scores)

            en_prediction['prefix_correlation'] = {
                'rho': rho,
                'p': p_rho,
                'n': len(valid_records),
                'interpretation': ('PREFIX captures most EN signal' if rho > 0.7
                    else 'EN signal partially independent of PREFIX' if rho > 0.3
                    else 'EN signal largely independent of PREFIX'),
            }
            print(f"  PREFIX vs EN score: rho={rho:.3f} p={p_rho:.4f} (n={len(valid_records)})")
            print(f"    -> {en_prediction['prefix_correlation']['interpretation']}")

            # Residual test: after controlling for prefix, does EN score still predict record type?
            # Split valid_records by prefix_qo_frac into high/low prefix groups
            median_prefix = float(np.median(prefix_fracs))
            high_prefix = [r for r in valid_records if r['prefix_qo_frac'] > median_prefix]
            low_prefix = [r for r in valid_records if r['prefix_qo_frac'] <= median_prefix]

            en_prediction['prefix_stratified'] = {}
            for label, subset in [('high_qo_prefix', high_prefix), ('low_qo_prefix', low_prefix)]:
                if len(subset) >= 10:
                    sub_en = [r['mean_qo_score'] for r in subset]
                    sub_sizes = [r['n_total'] for r in subset]
                    rho_s, p_s = spearman_rho(sub_en, sub_sizes)
                    en_prediction['prefix_stratified'][label] = {
                        'n': len(subset),
                        'mean_qo_score': float(np.mean(sub_en)),
                        'en_vs_size_rho': rho_s,
                        'en_vs_size_p': p_s,
                    }
                    print(f"    {label}: n={len(subset)}, mean_qo={np.mean(sub_en):.3f}")

        # Material class by EN sub-family
        qo_materials = Counter()
        chsh_materials = Counter()
        for r in qo_records:
            for mat, count in r['material_counts'].items():
                if mat != 'NEUTRAL':
                    qo_materials[mat] += count
        for r in chsh_records:
            for mat, count in r['material_counts'].items():
                if mat != 'NEUTRAL':
                    chsh_materials[mat] += count

        en_prediction['material'] = {
            'qo_materials': dict(qo_materials),
            'chsh_materials': dict(chsh_materials),
        }

        qo_total = sum(qo_materials.values())
        chsh_total = sum(chsh_materials.values())
        if qo_total > 0 and chsh_total > 0:
            qo_animal = qo_materials.get('ANIMAL', 0) / qo_total
            chsh_animal = chsh_materials.get('ANIMAL', 0) / chsh_total
            en_prediction['material']['qo_animal_rate'] = qo_animal
            en_prediction['material']['chsh_animal_rate'] = chsh_animal

            # Fisher's exact for animal enrichment
            a_val = qo_materials.get('ANIMAL', 0)
            b_val = qo_total - a_val
            c_val = chsh_materials.get('ANIMAL', 0)
            d_val = chsh_total - c_val
            mat_odds, mat_p = fisher_exact_2x2(a_val, b_val, c_val, d_val)
            en_prediction['material']['animal_fisher_p'] = mat_p
            en_prediction['material']['animal_fisher_sig'] = mat_p < 0.05
            sig = "*" if mat_p < 0.05 else ""
            print(f"  Material ANIMAL rate: QO={qo_animal:.3f} vs CHSH={chsh_animal:.3f} "
                  f"Fisher p={mat_p:.4f} {sig}")
        else:
            print("  Insufficient non-neutral material data")
    else:
        en_prediction['verdict'] = 'INSUFFICIENT_DATA'
        print(f"\n  Insufficient data: QO={len(qo_records)}, CHSH={len(chsh_records)} (need >=5 each)")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    n_sig_fisher = sum(1 for v in fisher_results.values() if v.get('significant'))
    n_sig_regime = sum(1 for v in regime_comparison.values()
                       if isinstance(v, dict) and v.get('significant'))

    # Determine overall population verdict
    if n_sig_fisher >= 2:
        pop_verdict = 'POPULATIONS_DIFFER'
    elif n_sig_fisher == 1:
        pop_verdict = 'WEAK_DIFFERENCE'
    else:
        pop_verdict = 'NO_DIFFERENCE'

    summary = {
        'match_limitation': (f"Only {len(matched_azc) + len(matched_bn)}/"
                             f"{len(azc_med) + len(b_native)} PP MIDDLEs matched to B classes (22%)"),
        'b_native_warning': (f"B-Native has only {len(matched_bn)} matched MIDDLEs - "
                             f"all tests severely underpowered"),
        'population_verdict': pop_verdict,
        'n_sig_role_tests': f"{n_sig_fisher}/5",
        'n_sig_regime_tests': f"{n_sig_regime}/4",
        'hazard_fl_significant': hazard_results.get('significant', False),
        'purity_significant': purity_results.get('significant', False),
        'en_subfamily_records': len(record_profiles),
        'en_subfamily_verdict': en_prediction.get('prefix_correlation', {}).get('interpretation', 'NOT_TESTED'),
    }

    for k, v in summary.items():
        print(f"  {k}: {v}")

    results = {
        'metadata': {
            'phase': 'A_TO_B_ROLE_PROJECTION',
            'script': 'population_profiles.py',
            'description': 'AZC-Med vs B-Native execution profiles and EN sub-family prediction',
            'n_matched_azc': len(matched_azc),
            'n_matched_bn': len(matched_bn),
            'n_azc_med_total': len(azc_med),
            'n_b_native_total': len(b_native),
        },
        'fisher_role_tests': fisher_results,
        'hazard_participation': hazard_results,
        'role_purity': purity_results,
        'regime_comparison': regime_comparison,
        'suffix_comparison': suffix_results,
        'en_subfamily_classification': {
            'n_pp_with_en': len(pp_en_class),
            'subfamily_counts': dict(subfamily_counts),
            'pp_en_details': pp_en_class,
        },
        'en_prediction': en_prediction,
        'a_record_profiles': {
            'n_records': len(record_profiles),
            'type_distribution': dict(type_counts),
            'records': record_profiles,
        },
        'summary': summary,
    }

    out_path = results_dir / 'population_profiles.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")

    print("\n" + "=" * 70)
    print("Script 2 complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
