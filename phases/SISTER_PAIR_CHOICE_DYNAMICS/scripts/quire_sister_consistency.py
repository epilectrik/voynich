#!/usr/bin/env python3
"""
quire_sister_consistency.py - Quire-level clustering of ch_preference

Tests whether quire membership predicts folio-level ch_preference,
computes ICC(1,1) for quire clustering, and checks for quire-section
confound.

Sections:
1. Folio-to-quire mapping and per-folio ch_preference
2. Quire-level descriptive statistics
3. Kruskal-Wallis tests (quire vs section vs REGIME)
4. ICC(1,1) computation
5. Quire-section confound test
"""

import sys
import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict

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


def build_folio_quire_map():
    """Build folio -> quire mapping from raw transcript (H track, language=B)."""
    transcript_path = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    folio_quire = {}
    folio_section = {}

    with open(transcript_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            language = row.get('language', '').strip().strip('"')
            if transcriber != 'H' or language != 'B':
                continue
            folio = row.get('folio', '').strip().strip('"')
            quire = row.get('quire', '').strip().strip('"')
            section = row.get('section', '').strip().strip('"')
            if folio and quire:
                folio_quire[folio] = quire
            if folio and section:
                folio_section[folio] = section

    return folio_quire, folio_section


def compute_per_folio_ch_preference(min_tokens=5):
    """Compute per-folio ch_preference = ch / (ch + sh), minimum tokens filter."""
    tx = Transcript()
    morph = Morphology()

    folio_ch = defaultdict(int)
    folio_sh = defaultdict(int)

    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.prefix == 'ch':
            folio_ch[token.folio] += 1
        elif m.prefix == 'sh':
            folio_sh[token.folio] += 1

    results = {}
    for folio in set(list(folio_ch.keys()) + list(folio_sh.keys())):
        ch = folio_ch[folio]
        sh = folio_sh[folio]
        total = ch + sh
        if total >= min_tokens:
            results[folio] = {
                'ch': ch,
                'sh': sh,
                'total': total,
                'ch_preference': ch / total
            }

    return results


def kruskal_wallis(groups):
    """Manual Kruskal-Wallis test (no scipy dependency).

    groups: list of arrays of values
    Returns: H statistic, p-value (chi2 approximation), k, N
    """
    # Pool and rank all values
    all_vals = []
    group_ids = []
    for i, g in enumerate(groups):
        for v in g:
            all_vals.append(v)
            group_ids.append(i)

    N = len(all_vals)
    k = len(groups)
    if k < 2 or N < 3:
        return 0.0, 1.0, k, N

    # Rank (average ties)
    sorted_indices = np.argsort(all_vals)
    ranks = np.empty(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and all_vals[sorted_indices[j]] == all_vals[sorted_indices[i]]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-based
        for idx in range(i, j):
            ranks[sorted_indices[idx]] = avg_rank
        i = j

    # H statistic
    R_mean = (N + 1) / 2.0
    SS_between = 0.0
    for i, g in enumerate(groups):
        n_i = len(g)
        if n_i == 0:
            continue
        group_ranks = [ranks[idx] for idx, gid in enumerate(group_ids) if gid == i]
        R_bar_i = np.mean(group_ranks)
        SS_between += n_i * (R_bar_i - R_mean) ** 2

    H = (12.0 / (N * (N + 1))) * SS_between

    # Chi-squared approximation p-value
    from math import exp, lgamma
    df = k - 1
    p = chi2_sf(H, df)

    return float(H), float(p), k, N


def chi2_sf(x, df):
    """Survival function for chi-squared distribution (1 - CDF).
    Uses regularized incomplete gamma function approximation."""
    if x <= 0:
        return 1.0
    if df <= 0:
        return 0.0

    # Use series/continued fraction for regularized incomplete gamma
    a = df / 2.0
    z = x / 2.0
    return 1.0 - regularized_gamma_p(a, z)


def regularized_gamma_p(a, x):
    """Regularized lower incomplete gamma function P(a, x) = gamma(a, x) / Gamma(a).
    Uses series expansion for small x, continued fraction for large x."""
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0

    if x < a + 1:
        # Series expansion
        return gamma_series(a, x)
    else:
        # Continued fraction
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


def spearman_rank(x, y):
    """Spearman rank correlation."""
    from scipy.stats import rankdata
    # Manual rankdata to avoid scipy
    def rank_array(arr):
        arr = np.array(arr, dtype=float)
        sorted_idx = np.argsort(arr)
        ranks = np.empty_like(arr)
        i = 0
        n = len(arr)
        while i < n:
            j = i
            while j < n and arr[sorted_idx[j]] == arr[sorted_idx[i]]:
                j += 1
            avg_rank = (i + j + 1) / 2.0
            for k_idx in range(i, j):
                ranks[sorted_idx[k_idx]] = avg_rank
            i = j
        return ranks

    rx = rank_array(x)
    ry = rank_array(y)
    n = len(rx)
    d = rx - ry
    d_sq = np.sum(d ** 2)
    rho = 1 - (6 * d_sq) / (n * (n ** 2 - 1))
    # t-test for significance
    if abs(rho) >= 1.0:
        p = 0.0
    else:
        from math import sqrt
        t = rho * sqrt((n - 2) / (1 - rho ** 2))
        # Two-tailed p from t-distribution (df = n-2)
        p = t_distribution_sf(abs(t), n - 2) * 2
    return float(rho), float(p)


def t_distribution_sf(t, df):
    """Survival function for t-distribution using beta regularized function."""
    x = df / (df + t * t)
    return 0.5 * regularized_beta(x, df / 2.0, 0.5)


def regularized_beta(x, a, b):
    """Regularized incomplete beta function I_x(a,b) using continued fraction."""
    from math import lgamma, exp
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0

    lbeta = lgamma(a) + lgamma(b) - lgamma(a + b)
    front = exp(a * np.log(x) + b * np.log(1 - x) - lbeta) / a

    # Use Lentz's continued fraction
    if x < (a + 1) / (a + b + 2):
        return front * beta_cf(x, a, b)
    else:
        front2 = exp(a * np.log(x) + b * np.log(1 - x) - lbeta) / b
        return 1.0 - front2 * beta_cf(1 - x, b, a)


def beta_cf(x, a, b):
    """Continued fraction for incomplete beta."""
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d

    for m in range(1, 300):
        m2 = 2 * m
        # Even step
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c

        # Odd step
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < 1e-12:
            break

    return h


def chi2_test_contingency(observed):
    """Chi-squared test for independence on a contingency table.
    observed: 2D numpy array of counts.
    Returns: chi2, p, dof."""
    observed = np.array(observed, dtype=float)
    row_sums = observed.sum(axis=1)
    col_sums = observed.sum(axis=0)
    total = observed.sum()

    expected = np.outer(row_sums, col_sums) / total
    # Avoid division by zero
    mask = expected > 0
    chi2 = np.sum((observed[mask] - expected[mask]) ** 2 / expected[mask])
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    p = chi2_sf(chi2, dof)
    return float(chi2), float(p), int(dof)


def compute_eta_squared(H, k, N):
    """Eta-squared from Kruskal-Wallis H statistic."""
    if N <= k:
        return 0.0
    return (H - k + 1) / (N - k)


def compute_icc(groups):
    """Compute ICC(1,1) - one-way random effects intraclass correlation.

    groups: dict of {quire: [ch_preference values]}
    Returns: ICC value, MSB, MSW, k0 (adjusted group size)
    """
    # Filter to groups with >=2 members
    valid_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    if len(valid_groups) < 2:
        return None, None, None, None

    k = len(valid_groups)  # number of groups
    group_sizes = [len(v) for v in valid_groups.values()]
    N = sum(group_sizes)

    # Grand mean
    all_vals = []
    for v in valid_groups.values():
        all_vals.extend(v)
    grand_mean = np.mean(all_vals)

    # Between-group sum of squares
    SSB = sum(len(v) * (np.mean(v) - grand_mean) ** 2 for v in valid_groups.values())
    # Within-group sum of squares
    SSW = sum(sum((x - np.mean(v)) ** 2 for x in v) for v in valid_groups.values())

    dfB = k - 1
    dfW = N - k

    MSB = SSB / dfB if dfB > 0 else 0
    MSW = SSW / dfW if dfW > 0 else 0

    # Adjusted group size for unbalanced design
    sum_n = sum(group_sizes)
    sum_n2 = sum(n ** 2 for n in group_sizes)
    k0 = (sum_n - sum_n2 / sum_n) / (k - 1)

    # ICC(1,1)
    if MSB + (k0 - 1) * MSW == 0:
        icc = 0.0
    else:
        icc = (MSB - MSW) / (MSB + (k0 - 1) * MSW)

    return float(icc), float(MSB), float(MSW), float(k0)


def main():
    print("=" * 70)
    print("QUIRE SISTER CONSISTENCY")
    print("Phase: SISTER_PAIR_CHOICE_DYNAMICS | Script 2 of 3")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / 'results'

    # Load REGIME mapping
    regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_regime = {}
    for regime, folios in regime_data.items():
        for folio in folios:
            folio_regime[folio] = regime

    # ================================================================
    # SECTION 1: Folio-to-Quire Mapping and Per-Folio ch_preference
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: Folio-to-Quire Mapping and Per-Folio ch_preference")
    print("=" * 70)

    folio_quire, folio_section = build_folio_quire_map()
    ch_pref_data = compute_per_folio_ch_preference(min_tokens=5)

    # Filter to folios with both quire and ch_preference
    common_folios = sorted(set(ch_pref_data.keys()) & set(folio_quire.keys()))

    print(f"\nFolios with ch_preference (>=5 ch+sh): {len(ch_pref_data)}")
    print(f"Folios with quire mapping: {len(folio_quire)}")
    print(f"Folios with both: {len(common_folios)}")

    # Quire membership counts
    quire_folios = defaultdict(list)
    for f in common_folios:
        quire_folios[folio_quire[f]].append(f)

    print(f"\nQuire membership (B folios with ch_preference):")
    quire_summary = {}
    for q in sorted(quire_folios.keys()):
        print(f"  Quire {q}: {len(quire_folios[q])} folios")
        quire_summary[q] = len(quire_folios[q])

    # Section membership counts
    section_folios = defaultdict(list)
    for f in common_folios:
        if f in folio_section:
            section_folios[folio_section[f]].append(f)

    print(f"\nSection membership:")
    for s in sorted(section_folios.keys()):
        print(f"  Section {s}: {len(section_folios[s])} folios")

    # ================================================================
    # SECTION 2: Quire-Level Descriptive Statistics
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: Quire-Level Descriptive Statistics")
    print("=" * 70)

    quire_stats = {}
    print(f"\n{'Quire':<8} {'N':>3} {'Mean':>7} {'Std':>7} {'Min':>7} {'Max':>7}")
    print("-" * 45)

    for q in sorted(quire_folios.keys()):
        vals = [ch_pref_data[f]['ch_preference'] for f in quire_folios[q]]
        if len(vals) >= 2:
            stats = {
                'n': len(vals),
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals, ddof=1)),
                'min': float(np.min(vals)),
                'max': float(np.max(vals)),
                'folios': quire_folios[q]
            }
        else:
            stats = {
                'n': len(vals),
                'mean': float(np.mean(vals)),
                'std': 0.0,
                'min': float(vals[0]) if vals else 0.0,
                'max': float(vals[0]) if vals else 0.0,
                'folios': quire_folios[q]
            }
        quire_stats[q] = stats
        print(f"  {q:<6} {stats['n']:>3} {stats['mean']:>7.3f} {stats['std']:>7.3f} {stats['min']:>7.3f} {stats['max']:>7.3f}")

    # ================================================================
    # SECTION 3: Kruskal-Wallis Tests
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: Kruskal-Wallis Tests (quire vs section vs REGIME)")
    print("=" * 70)

    # 3a. Quire -> ch_preference (only quires with >=3 folios)
    quire_groups_3 = []
    quire_labels_3 = []
    for q in sorted(quire_folios.keys()):
        vals = [ch_pref_data[f]['ch_preference'] for f in quire_folios[q]]
        if len(vals) >= 3:
            quire_groups_3.append(vals)
            quire_labels_3.append(q)

    H_quire, p_quire, k_quire, N_quire = kruskal_wallis(quire_groups_3)
    eta_quire = compute_eta_squared(H_quire, k_quire, N_quire)

    print(f"\n3a. Quire -> ch_preference (quires with >=3 folios)")
    print(f"    Quires tested: {quire_labels_3}")
    print(f"    k={k_quire}, N={N_quire}")
    print(f"    H={H_quire:.3f}, p={p_quire:.4f}, eta_sq={eta_quire:.3f}")
    print(f"    Significant: {p_quire < 0.05}")

    # 3b. Section -> ch_preference
    section_groups = []
    section_labels = []
    for s in sorted(section_folios.keys()):
        vals = [ch_pref_data[f]['ch_preference'] for f in section_folios[s]]
        if len(vals) >= 3:
            section_groups.append(vals)
            section_labels.append(s)

    H_section, p_section, k_section, N_section = kruskal_wallis(section_groups)
    eta_section = compute_eta_squared(H_section, k_section, N_section)

    print(f"\n3b. Section -> ch_preference (sections with >=3 folios)")
    print(f"    Sections tested: {section_labels}")
    print(f"    k={k_section}, N={N_section}")
    print(f"    H={H_section:.3f}, p={p_section:.4f}, eta_sq={eta_section:.3f}")
    print(f"    Significant: {p_section < 0.05}")

    # 3c. REGIME -> ch_preference
    regime_groups = defaultdict(list)
    for f in common_folios:
        if f in folio_regime:
            regime_groups[folio_regime[f]].append(ch_pref_data[f]['ch_preference'])

    regime_groups_list = []
    regime_labels = []
    for r in sorted(regime_groups.keys()):
        if len(regime_groups[r]) >= 3:
            regime_groups_list.append(regime_groups[r])
            regime_labels.append(r)

    H_regime, p_regime, k_regime, N_regime = kruskal_wallis(regime_groups_list)
    eta_regime = compute_eta_squared(H_regime, k_regime, N_regime)

    print(f"\n3c. REGIME -> ch_preference")
    print(f"    REGIMEs tested: {regime_labels}")
    print(f"    k={k_regime}, N={N_regime}")
    print(f"    H={H_regime:.3f}, p={p_regime:.4f}, eta_sq={eta_regime:.3f}")
    print(f"    Significant: {p_regime < 0.05}")
    print(f"    [C604 reference: H=9.882, p=0.020]")

    # Comparison table
    print(f"\n--- Comparison ---")
    print(f"{'Predictor':<12} {'H':>8} {'p':>10} {'eta_sq':>8} {'Sig':>5}")
    print("-" * 48)
    print(f"{'Quire':<12} {H_quire:>8.3f} {p_quire:>10.4f} {eta_quire:>8.3f} {'*' if p_quire < 0.05 else 'ns':>5}")
    print(f"{'Section':<12} {H_section:>8.3f} {p_section:>10.4f} {eta_section:>8.3f} {'*' if p_section < 0.05 else 'ns':>5}")
    print(f"{'REGIME':<12} {H_regime:>8.3f} {p_regime:>10.4f} {eta_regime:>8.3f} {'*' if p_regime < 0.05 else 'ns':>5}")

    # ================================================================
    # SECTION 4: ICC(1,1) Computation
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: ICC(1,1) - Intraclass Correlation for Quire Clustering")
    print("=" * 70)

    # Build groups for ICC
    quire_icc_groups = {}
    for q in sorted(quire_folios.keys()):
        vals = [ch_pref_data[f]['ch_preference'] for f in quire_folios[q]]
        quire_icc_groups[q] = vals

    icc_val, MSB, MSW, k0 = compute_icc(quire_icc_groups)

    if icc_val is not None:
        if icc_val < 0.2:
            icc_interp = "POOR (<0.2)"
        elif icc_val < 0.5:
            icc_interp = "FAIR (0.2-0.5)"
        elif icc_val < 0.75:
            icc_interp = "GOOD (0.5-0.75)"
        else:
            icc_interp = "EXCELLENT (>0.75)"

        print(f"\n  ICC(1,1) = {icc_val:.3f}")
        print(f"  MSB (between-quire) = {MSB:.4f}")
        print(f"  MSW (within-quire)  = {MSW:.4f}")
        print(f"  k0 (adjusted group size) = {k0:.2f}")
        print(f"  Interpretation: {icc_interp}")
        print(f"  [C450 reference: quire effect on HT density eta_sq=0.150]")
    else:
        print("\n  ICC could not be computed (insufficient groups)")
        icc_interp = "INSUFFICIENT_DATA"

    # ================================================================
    # SECTION 5: Quire-Section Confound Test
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 5: Quire-Section Confound Test")
    print("=" * 70)

    # 5a. Build quire x section contingency table
    quire_set = sorted(set(folio_quire[f] for f in common_folios))
    section_set = sorted(set(folio_section.get(f, 'UNK') for f in common_folios))

    # Count folios per quire-section cell
    contingency = defaultdict(lambda: defaultdict(int))
    for f in common_folios:
        q = folio_quire[f]
        s = folio_section.get(f, 'UNK')
        contingency[q][s] += 1

    print(f"\nQuire x Section contingency table:")
    header = f"{'Quire':<8}" + "".join(f"{s:>6}" for s in section_set)
    print(f"  {header}")
    print("  " + "-" * (8 + 6 * len(section_set)))

    cont_matrix = []
    for q in quire_set:
        row = [contingency[q][s] for s in section_set]
        cont_matrix.append(row)
        row_str = f"  {q:<8}" + "".join(f"{v:>6}" for v in row)
        print(row_str)

    cont_array = np.array(cont_matrix)

    # Remove empty rows/columns for chi-squared
    row_mask = cont_array.sum(axis=1) > 0
    col_mask = cont_array.sum(axis=0) > 0
    cont_filtered = cont_array[row_mask][:, col_mask]

    if cont_filtered.shape[0] >= 2 and cont_filtered.shape[1] >= 2:
        chi2_qs, p_qs, dof_qs = chi2_test_contingency(cont_filtered)
        print(f"\n  Chi-squared test for quire-section independence:")
        print(f"    chi2={chi2_qs:.1f}, p={p_qs:.4f}, dof={dof_qs}")
        print(f"    {'CONFOUNDED (not independent)' if p_qs < 0.05 else 'Independent'}")

        # Cramers V
        n_obs = cont_filtered.sum()
        min_dim = min(cont_filtered.shape[0] - 1, cont_filtered.shape[1] - 1)
        cramers_v = np.sqrt(chi2_qs / (n_obs * min_dim)) if min_dim > 0 and n_obs > 0 else 0
        print(f"    Cramer's V = {cramers_v:.3f}")
    else:
        chi2_qs, p_qs, dof_qs = 0.0, 1.0, 0
        cramers_v = 0.0
        print("\n  Insufficient dimensions for chi-squared test")

    # 5b. For sections spanning multiple quires, test quire within section
    print(f"\n  Sections spanning multiple quires:")
    stratified_results = {}
    for s in sorted(section_folios.keys()):
        # Get unique quires in this section
        section_f = [f for f in section_folios[s] if f in folio_quire]
        quires_in_section = set(folio_quire[f] for f in section_f)
        if len(quires_in_section) >= 2:
            # Build quire groups within this section
            within_groups = defaultdict(list)
            for f in section_f:
                if f in ch_pref_data:
                    within_groups[folio_quire[f]].append(ch_pref_data[f]['ch_preference'])

            # Only test quires with >=2 folios in this section
            testable = {q: v for q, v in within_groups.items() if len(v) >= 2}
            if len(testable) >= 2:
                groups = [v for v in testable.values()]
                H_within, p_within, k_within, N_within = kruskal_wallis(groups)
                eta_within = compute_eta_squared(H_within, k_within, N_within)
                print(f"    Section {s}: quires={sorted(testable.keys())}, k={k_within}, N={N_within}")
                print(f"      H={H_within:.3f}, p={p_within:.4f}, eta_sq={eta_within:.3f}")
                print(f"      {'Quire significant WITHIN section' if p_within < 0.05 else 'Quire NOT significant within section'}")
                stratified_results[s] = {
                    'quires': sorted(testable.keys()),
                    'k': k_within,
                    'N': N_within,
                    'H': H_within,
                    'p': p_within,
                    'eta_sq': eta_within,
                    'significant': bool(p_within < 0.05)
                }
            else:
                print(f"    Section {s}: quires={sorted(quires_in_section)}, too few folios per quire for test")
        else:
            if len(section_folios[s]) >= 2:
                print(f"    Section {s}: only 1 quire ({list(quires_in_section)[0] if quires_in_section else 'none'})")

    # Verdict on quire independence
    has_independent_effect = any(r['significant'] for r in stratified_results.values())
    print(f"\n  Quire has independent effect after section control: {has_independent_effect}")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    quire_sig = p_quire < 0.05
    section_sig = p_section < 0.05
    regime_sig = p_regime < 0.05

    if quire_sig and has_independent_effect:
        quire_verdict = "QUIRE_PREDICTS_INDEPENDENTLY"
    elif quire_sig and not has_independent_effect:
        quire_verdict = "QUIRE_CONFOUNDED_WITH_SECTION"
    else:
        quire_verdict = "QUIRE_DOES_NOT_PREDICT"

    print(f"\n  Quire KW: H={H_quire:.3f}, p={p_quire:.4f} -> {'Sig' if quire_sig else 'Not sig'}")
    print(f"  Section KW: H={H_section:.3f}, p={p_section:.4f} -> {'Sig' if section_sig else 'Not sig'}")
    print(f"  REGIME KW: H={H_regime:.3f}, p={p_regime:.4f} -> {'Sig' if regime_sig else 'Not sig'}")
    print(f"  ICC(1,1): {icc_val:.3f} ({icc_interp})" if icc_val is not None else "  ICC(1,1): N/A")
    print(f"  Quire-section: {'CONFOUNDED' if p_qs < 0.05 else 'independent'} (chi2={chi2_qs:.1f})")
    print(f"  Quire independent of section: {has_independent_effect}")
    print(f"  Verdict: {quire_verdict}")

    # ================================================================
    # SAVE OUTPUT
    # ================================================================
    output = {
        'metadata': {
            'phase': 'SISTER_PAIR_CHOICE_DYNAMICS',
            'script': 'quire_sister_consistency.py',
            'description': 'Quire-level clustering of ch_preference',
            'min_tokens_per_folio': 5,
            'min_quire_size_kw': 3,
        },
        'folio_quire_map': {f: folio_quire[f] for f in common_folios},
        'quire_membership': quire_summary,
        'quire_stats': {q: {k: v for k, v in s.items() if k != 'folios'}
                        for q, s in quire_stats.items()},
        'kw_tests': {
            'quire': {
                'quires_tested': quire_labels_3,
                'k': k_quire,
                'N': N_quire,
                'H': H_quire,
                'p': p_quire,
                'eta_sq': eta_quire,
                'significant': bool(quire_sig),
            },
            'section': {
                'sections_tested': section_labels,
                'k': k_section,
                'N': N_section,
                'H': H_section,
                'p': p_section,
                'eta_sq': eta_section,
                'significant': bool(section_sig),
            },
            'regime': {
                'regimes_tested': regime_labels,
                'k': k_regime,
                'N': N_regime,
                'H': H_regime,
                'p': p_regime,
                'eta_sq': eta_regime,
                'significant': bool(regime_sig),
                'c604_reference': {'H': 9.882, 'p': 0.020},
            },
        },
        'icc': {
            'icc_1_1': icc_val,
            'MSB': MSB,
            'MSW': MSW,
            'k0': k0,
            'interpretation': icc_interp,
            'c450_reference_eta_sq': 0.150,
        },
        'quire_section_confound': {
            'chi2': chi2_qs,
            'p': p_qs,
            'dof': dof_qs,
            'cramers_v': cramers_v,
            'confounded': bool(p_qs < 0.05),
            'stratified_kw': stratified_results,
            'quire_independent_of_section': has_independent_effect,
        },
        'verdict': quire_verdict,
        'per_folio_ch_preference': {
            f: ch_pref_data[f] for f in common_folios
        },
    }

    output_path = results_dir / 'quire_sister_consistency.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nSaved: {output_path}")


if __name__ == '__main__':
    main()
