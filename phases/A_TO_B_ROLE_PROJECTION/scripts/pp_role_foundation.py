#!/usr/bin/env python3
"""
pp_role_foundation.py - PP MIDDLE to B Role Mapping Foundation

Maps all 404 PP (pipeline-participating) MIDDLEs to B's 5-role, 49-class
instruction system. Computes AZC-Mediated vs B-Native split. Builds role
probability vectors. Tests role clustering.

Sections:
1. Load and validate input data
2. Build PP-to-role mapping
3. AZC-Mediated vs B-Native split
4. Role clustering test
5. Summary and save
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from math import log2

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


def mannwhitney_u(x, y):
    """Manual Mann-Whitney U test. Returns U, z, p (two-tailed, normal approx)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 0.0, 1.0

    # Pool and rank
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

    # Normal approximation
    mu = nx * ny / 2.0
    sigma = np.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return float(U), 0.0, 1.0
    z = (U - mu) / sigma
    # Two-tailed p from normal
    p = 2.0 * norm_sf(abs(z))
    return float(U), float(z), float(p)


def norm_sf(z):
    """Standard normal survival function (1 - CDF)."""
    # Abramowitz and Stegun approximation
    if z < 0:
        return 1.0 - norm_sf(-z)
    t = 1.0 / (1.0 + 0.2316419 * z)
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = d * np.exp(-z * z / 2.0) * (t * (0.319381530 +
        t * (-0.356563782 + t * (1.781477937 +
        t * (-1.821255978 + t * 1.330274429)))))
    return float(p)


def chi2_sf(x, df):
    """Chi-squared survival function."""
    if x <= 0 or df <= 0:
        return 1.0
    a = df / 2.0
    z = x / 2.0
    return 1.0 - regularized_gamma_p(a, z)


def regularized_gamma_p(a, x):
    """Regularized lower incomplete gamma function P(a, x)."""
    if x <= 0:
        return 0.0
    if x < a + 1:
        return gamma_series(a, x)
    else:
        return 1.0 - gamma_cf(a, x)


def gamma_series(a, x):
    """Series expansion for P(a, x)."""
    from math import lgamma, exp
    if x == 0:
        return 0.0
    ap = a
    s = 1.0 / a
    delta = s
    for n in range(1, 300):
        ap += 1
        delta *= x / ap
        s += delta
        if abs(delta) < abs(s) * 1e-12:
            break
    return s * exp(-x + a * np.log(x) - lgamma(a))


def gamma_cf(a, x):
    """Continued fraction for Q(a, x) = 1 - P(a, x)."""
    from math import lgamma, exp
    b = x + 1 - a
    c = 1e30
    d = 1.0 / b if b != 0 else 1e30
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return exp(-x + a * np.log(x) - lgamma(a)) * h


def compute_entropy(probs):
    """Shannon entropy of a probability distribution."""
    h = 0.0
    for p in probs:
        if p > 0:
            h -= p * log2(p)
    return h


def main():
    print("=" * 70)
    print("PP ROLE FOUNDATION")
    print("Phase: A_TO_B_ROLE_PROJECTION | Script 1 of 3")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / 'results'

    # ================================================================
    # SECTION 1: Load and Validate Input Data
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: Load and Validate Input Data")
    print("=" * 70)

    # Load PP MIDDLE list
    mc_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes_v2_backup.json'
    with open(mc_path, 'r', encoding='utf-8') as f:
        mc_data = json.load(f)
    pp_middles = set(mc_data['a_shared_middles'])
    ri_middles = set(mc_data['a_exclusive_middles'])
    print(f"\nPP MIDDLEs loaded: {len(pp_middles)}")
    print(f"RI MIDDLEs loaded: {len(ri_middles)}")

    # Load class_token_map
    ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)

    # Apply role corrections
    class_to_role = dict(ctm['class_to_role'])
    for cls_id, new_role in ROLE_CORRECTIONS.items():
        old_role = class_to_role.get(cls_id, 'UNKNOWN')
        class_to_role[cls_id] = new_role
        print(f"  Role correction: class {cls_id}: {old_role} -> {new_role} (per C560/C581)")

    # Count classes per role
    role_class_counts = Counter(class_to_role.values())
    print(f"\nClasses per role (after correction):")
    for role in ROLE_NAMES:
        short = ROLE_SHORT[role]
        print(f"  {short} ({role}): {role_class_counts[role]} classes")
    print(f"  Total: {sum(role_class_counts.values())} classes")

    # Build middle_to_classes by extracting MIDDLEs from B tokens using current parser
    # (class_to_middles was built with a different parser and only has 90 MIDDLEs)
    morph = Morphology()
    token_to_class = ctm['token_to_class']
    middle_to_classes = defaultdict(set)
    middle_to_tokens = defaultdict(set)

    for word, cls_val in token_to_class.items():
        m = morph.extract(word)
        if m.middle:
            middle_to_classes[m.middle].add(str(cls_val))
            middle_to_tokens[m.middle].add(word)

    print(f"\nUnique MIDDLEs in B class system (via current parser): {len(middle_to_classes)}")
    print(f"  (class_to_middles had only {len(set(m for mids in ctm['class_to_middles'].values() for m in mids))} unique MIDDLEs)")

    # ================================================================
    # SECTION 2: Build PP-to-Role Mapping
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: Build PP-to-Role Mapping")
    print("=" * 70)

    pp_role_map = {}
    matched = 0
    unmatched = 0
    unmatched_list = []

    for mid in sorted(pp_middles):
        classes = middle_to_classes.get(mid, set())
        if not classes:
            unmatched += 1
            unmatched_list.append(mid)
            pp_role_map[mid] = {
                'b_classes': [],
                'role_counts': {r: 0 for r in ROLE_NAMES},
                'role_vector': {r: 0.0 for r in ROLE_NAMES},
                'dominant_role': None,
                'n_classes': 0,
                'n_roles': 0,
                'role_entropy': 0.0,
            }
            continue

        matched += 1
        role_counts = Counter()
        for cls_id in classes:
            role = class_to_role.get(cls_id, 'UNKNOWN')
            if role != 'UNKNOWN':
                role_counts[role] += 1

        total_classes = sum(role_counts.values())
        role_vector = {r: role_counts.get(r, 0) / total_classes if total_classes > 0 else 0.0
                       for r in ROLE_NAMES}

        # Dominant role
        if role_counts:
            dominant = role_counts.most_common(1)[0][0]
        else:
            dominant = None

        n_roles = sum(1 for v in role_vector.values() if v > 0)
        entropy = compute_entropy([v for v in role_vector.values() if v > 0])

        pp_role_map[mid] = {
            'b_classes': sorted(classes),
            'role_counts': {r: role_counts.get(r, 0) for r in ROLE_NAMES},
            'role_vector': role_vector,
            'dominant_role': dominant,
            'n_classes': total_classes,
            'n_roles': n_roles,
            'role_entropy': entropy,
        }

    match_rate = matched / len(pp_middles) * 100
    print(f"\nPP MIDDLEs matched to B classes: {matched}/{len(pp_middles)} ({match_rate:.1f}%)")
    print(f"Unmatched: {unmatched}")
    if unmatched_list[:10]:
        print(f"  First 10 unmatched: {unmatched_list[:10]}")

    # Role distribution of matched PP
    dominant_counts = Counter()
    n_roles_dist = Counter()
    entropies = []
    for mid, data in pp_role_map.items():
        if data['dominant_role']:
            dominant_counts[data['dominant_role']] += 1
            n_roles_dist[data['n_roles']] += 1
            entropies.append(data['role_entropy'])

    print(f"\nDominant role distribution (matched PP):")
    for role in ROLE_NAMES:
        short = ROLE_SHORT[role]
        count = dominant_counts.get(role, 0)
        pct = count / matched * 100 if matched > 0 else 0
        print(f"  {short}: {count} ({pct:.1f}%)")

    print(f"\nMulti-role distribution:")
    for k in sorted(n_roles_dist.keys()):
        print(f"  {k} roles: {n_roles_dist[k]} PP MIDDLEs ({n_roles_dist[k]/matched*100:.1f}%)")

    multi_role_frac = sum(v for k, v in n_roles_dist.items() if k >= 2) / matched if matched > 0 else 0
    print(f"\nMulti-role fraction: {multi_role_frac:.3f}")
    print(f"Mean role entropy: {np.mean(entropies):.3f}")

    # ================================================================
    # SECTION 3: AZC-Mediated vs B-Native Split
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: AZC-Mediated vs B-Native Split")
    print("=" * 70)

    # Find PP MIDDLEs that appear in AZC tokens
    tx = Transcript()

    azc_middles = set()
    for token in tx.azc():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            azc_middles.add(m.middle)

    print(f"\nUnique MIDDLEs in AZC: {len(azc_middles)}")

    # Bifurcate PP
    azc_mediated = sorted([mid for mid in pp_middles if mid in azc_middles])
    b_native = sorted([mid for mid in pp_middles if mid not in azc_middles])

    print(f"AZC-Mediated PP: {len(azc_mediated)}")
    print(f"B-Native PP: {len(b_native)}")
    print(f"  [C498.a reference: expected ~235 AZC-Med, ~169 B-Native]")

    # Compare role vectors between populations
    def population_role_stats(middles, label):
        """Compute role statistics for a population of PP MIDDLEs."""
        role_vectors = []
        dom_counts = Counter()
        for mid in middles:
            data = pp_role_map.get(mid, {})
            if data.get('dominant_role'):
                dom_counts[data['dominant_role']] += 1
                role_vectors.append([data['role_vector'].get(r, 0.0) for r in ROLE_NAMES])

        if role_vectors:
            mean_vec = np.mean(role_vectors, axis=0)
        else:
            mean_vec = np.zeros(len(ROLE_NAMES))

        matched_n = sum(dom_counts.values())
        print(f"\n  {label} (n={len(middles)}, matched={matched_n}):")
        print(f"    Mean role vector:")
        for i, r in enumerate(ROLE_NAMES):
            print(f"      {ROLE_SHORT[r]}: {mean_vec[i]:.3f}")
        print(f"    Dominant role distribution:")
        for r in ROLE_NAMES:
            c = dom_counts.get(r, 0)
            pct = c / matched_n * 100 if matched_n > 0 else 0
            print(f"      {ROLE_SHORT[r]}: {c} ({pct:.1f}%)")

        return role_vectors, dom_counts

    azc_vectors, azc_dom = population_role_stats(azc_mediated, "AZC-Mediated")
    bn_vectors, bn_dom = population_role_stats(b_native, "B-Native")

    # Per-role Mann-Whitney U tests
    print(f"\n  Per-role Mann-Whitney U (AZC-Med vs B-Native):")
    role_mw_results = {}
    for i, role in enumerate(ROLE_NAMES):
        azc_vals = [v[i] for v in azc_vectors] if azc_vectors else []
        bn_vals = [v[i] for v in bn_vectors] if bn_vectors else []
        if len(azc_vals) >= 5 and len(bn_vals) >= 5:
            U, z, p = mannwhitney_u(azc_vals, bn_vals)
            sig = '*' if p < 0.05 else 'ns'
            azc_m = np.mean(azc_vals)
            bn_m = np.mean(bn_vals)
            print(f"    {ROLE_SHORT[role]}: AZC-Med={azc_m:.3f}, B-Native={bn_m:.3f}, U={U:.0f}, z={z:.2f}, p={p:.4f} {sig}")
            role_mw_results[role] = {'U': U, 'z': z, 'p': p, 'azc_mean': azc_m, 'bn_mean': bn_m,
                                     'significant': bool(p < 0.05)}
        else:
            print(f"    {ROLE_SHORT[role]}: insufficient data")
            role_mw_results[role] = {'insufficient': True}

    # Frequency confound control
    print(f"\n  Frequency confound control:")
    b_middle_freq = defaultdict(int)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word:
            continue
        m = morph.extract(word)
        if m.middle:
            b_middle_freq[m.middle] += 1

    azc_freqs = [b_middle_freq.get(mid, 0) for mid in azc_mediated]
    bn_freqs = [b_middle_freq.get(mid, 0) for mid in b_native]

    azc_med_freq = np.median(azc_freqs) if azc_freqs else 0
    bn_med_freq = np.median(bn_freqs) if bn_freqs else 0
    U_freq, z_freq, p_freq = mannwhitney_u(azc_freqs, bn_freqs)

    print(f"    AZC-Med B-frequency: median={azc_med_freq:.0f}, mean={np.mean(azc_freqs):.1f}")
    print(f"    B-Native B-frequency: median={bn_med_freq:.0f}, mean={np.mean(bn_freqs):.1f}")
    print(f"    Mann-Whitney: U={U_freq:.0f}, z={z_freq:.2f}, p={p_freq:.4f}")
    print(f"    Frequency confound: {'YES - must control' if p_freq < 0.05 else 'No significant difference'}")

    freq_confound = {
        'azc_med_median': float(azc_med_freq),
        'azc_med_mean': float(np.mean(azc_freqs)),
        'b_native_median': float(bn_med_freq),
        'b_native_mean': float(np.mean(bn_freqs)),
        'U': U_freq, 'z': z_freq, 'p': p_freq,
        'confounded': bool(p_freq < 0.05),
    }

    # ================================================================
    # SECTION 4: Role Clustering Test
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: Role Clustering Test")
    print("=" * 70)

    # Chi-squared goodness-of-fit: dominant_role distribution vs expected
    # Expected proportions from B role token shares
    role_token_counts = Counter()
    for token in tx.currier_b():
        word = token.word.strip()
        if not word:
            continue
        cls_val = ctm['token_to_class'].get(word)
        if cls_val is not None:
            role = class_to_role.get(str(cls_val), 'UNKNOWN')
            if role != 'UNKNOWN':
                role_token_counts[role] += 1

    total_role_tokens = sum(role_token_counts.values())
    expected_proportions = {r: role_token_counts.get(r, 0) / total_role_tokens
                           for r in ROLE_NAMES}

    print(f"\nB role token shares (expected proportions):")
    for r in ROLE_NAMES:
        print(f"  {ROLE_SHORT[r]}: {expected_proportions[r]:.3f} ({role_token_counts.get(r, 0)} tokens)")

    # Chi-squared test
    observed = [dominant_counts.get(r, 0) for r in ROLE_NAMES]
    expected = [expected_proportions[r] * matched for r in ROLE_NAMES]

    # Collapse small expected cells
    chi2 = 0.0
    valid_cells = 0
    for o, e in zip(observed, expected):
        if e > 0:
            chi2 += (o - e) ** 2 / e
            valid_cells += 1
    df = valid_cells - 1
    p_chi2 = chi2_sf(chi2, df) if df > 0 else 1.0

    print(f"\nChi-squared goodness-of-fit (dominant role vs B token shares):")
    print(f"  {'Role':<5} {'Obs':>6} {'Exp':>8}")
    for i, r in enumerate(ROLE_NAMES):
        print(f"  {ROLE_SHORT[r]:<5} {observed[i]:>6} {expected[i]:>8.1f}")
    print(f"  chi2={chi2:.2f}, df={df}, p={p_chi2:.4f}")
    print(f"  {'PP role distribution DIFFERS from B token shares' if p_chi2 < 0.05 else 'PP role distribution MATCHES B token shares'}")

    # Mean role entropy
    mean_entropy = float(np.mean(entropies)) if entropies else 0.0
    max_entropy = log2(5)  # 5 roles
    print(f"\nMean role entropy: {mean_entropy:.3f} (max={max_entropy:.3f})")
    print(f"Normalized entropy: {mean_entropy/max_entropy:.3f}")
    if mean_entropy < 0.5:
        entropy_interp = "LOW (role-specific)"
    elif mean_entropy < 1.5:
        entropy_interp = "MODERATE (partial role specificity)"
    else:
        entropy_interp = "HIGH (multi-role, weak specificity)"
    print(f"Interpretation: {entropy_interp}")

    # ================================================================
    # SECTION 5: Summary and Save
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    n_sig_roles = sum(1 for v in role_mw_results.values()
                      if isinstance(v, dict) and v.get('significant', False))

    print(f"\n  PP MIDDLEs: {len(pp_middles)} total, {matched} matched to B ({match_rate:.1f}%)")
    print(f"  AZC-Mediated: {len(azc_mediated)}, B-Native: {len(b_native)}")
    print(f"  Multi-role PP fraction: {multi_role_frac:.3f}")
    print(f"  Mean role entropy: {mean_entropy:.3f} ({entropy_interp})")
    print(f"  Dominant role chi2 vs B shares: p={p_chi2:.4f}")
    print(f"  AZC-Med vs B-Native role differences: {n_sig_roles}/5 roles significant")
    print(f"  Frequency confound: {'YES' if freq_confound['confounded'] else 'No'}")

    output = {
        'metadata': {
            'phase': 'A_TO_B_ROLE_PROJECTION',
            'script': 'pp_role_foundation.py',
            'description': 'PP MIDDLE to B role mapping foundation',
            'n_pp': len(pp_middles),
            'n_ri': len(ri_middles),
            'n_matched': matched,
            'n_unmatched': unmatched,
            'match_rate': match_rate,
            'role_correction': 'class_17: AUXILIARY->CORE_CONTROL per C560/C581',
        },
        'pp_role_map': pp_role_map,
        'role_distribution': {
            'dominant_counts': {r: dominant_counts.get(r, 0) for r in ROLE_NAMES},
            'n_roles_distribution': {str(k): v for k, v in sorted(n_roles_dist.items())},
            'multi_role_fraction': multi_role_frac,
            'mean_entropy': mean_entropy,
            'normalized_entropy': mean_entropy / max_entropy if max_entropy > 0 else 0,
            'entropy_interpretation': entropy_interp,
        },
        'azc_split': {
            'azc_mediated': azc_mediated,
            'b_native': b_native,
            'azc_med_count': len(azc_mediated),
            'b_native_count': len(b_native),
        },
        'population_comparison': {
            'per_role_mannwhitney': role_mw_results,
            'n_significant_roles': n_sig_roles,
            'frequency_confound': freq_confound,
        },
        'clustering_test': {
            'chi2_gof': {
                'chi2': chi2,
                'df': df,
                'p': p_chi2,
                'observed': {r: observed[i] for i, r in enumerate(ROLE_NAMES)},
                'expected': {r: round(expected[i], 1) for i, r in enumerate(ROLE_NAMES)},
                'verdict': 'DIFFERS' if p_chi2 < 0.05 else 'MATCHES',
            },
            'b_role_token_shares': {r: round(expected_proportions[r], 4) for r in ROLE_NAMES},
        },
        'b_middle_frequency': {mid: b_middle_freq.get(mid, 0) for mid in sorted(pp_middles)},
        'unmatched_pp': unmatched_list,
    }

    output_path = results_dir / 'pp_role_foundation.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nSaved: {output_path}")


if __name__ == '__main__':
    main()
