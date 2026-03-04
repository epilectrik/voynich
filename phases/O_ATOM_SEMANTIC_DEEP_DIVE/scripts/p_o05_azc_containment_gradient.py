#!/usr/bin/env python3
"""
P-O5: AZC enrichment gradient correlates with CONTAINMENT fraction

C1381 shows o-initial MIDDLEs have section gradient:
  AZC 22.4% > C 18.9% > H/T 13.3% > S 11.9% > B 9.2%
If o = "vessel", this gradient should correlate with CONTAINMENT category fraction.

Tests:
1. Compute o-initial MIDDLE fraction per section (B, C, H, S, T) plus AZC.
2. Compute CONTAINMENT category fraction per section.
3. Spearman correlation between o-initial rate and CONTAINMENT rate.
4. Test ALL 8 categories against the o-initial gradient.
5. Control: k-initial rate per section vs THERMAL fraction.

Pass criterion: rho(o-initial rate, CONTAINMENT rate) > +0.80 across sections.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


def normal_cdf(x):
    """Approximate CDF of standard normal using Abramowitz & Stegun."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p_const = 0.3275911
    sign = 1 if x >= 0 else -1
    x_abs = abs(x)
    t = 1.0 / (1.0 + p_const * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def spearman_rho(x_vals, y_vals):
    """Compute Spearman rank correlation and approximate p-value."""
    n = len(x_vals)
    if n < 3:
        return 0.0, 1.0

    def rank_values(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks

    x_ranks = rank_values(x_vals)
    y_ranks = rank_values(y_vals)

    mean_x = sum(x_ranks) / n
    mean_y = sum(y_ranks) / n

    cov = sum((x_ranks[i] - mean_x) * (y_ranks[i] - mean_y) for i in range(n))
    std_x = math.sqrt(sum((x_ranks[i] - mean_x) ** 2 for i in range(n)))
    std_y = math.sqrt(sum((y_ranks[i] - mean_y) ** 2 for i in range(n)))

    if std_x == 0 or std_y == 0:
        return 0.0, 1.0

    rho = cov / (std_x * std_y)

    # Approximate p-value using t-distribution approximation
    if abs(rho) >= 1.0:
        p_val = 0.0
    else:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho * rho))
        # Approximate with normal for small n
        p_val = 2.0 * (1.0 - normal_cdf(abs(t_stat)))

    return rho, p_val


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # ---- Collect Currier B data per section ----
    # section -> {total_middles, o_initial_count, k_initial_count, cat_counts}
    section_data = defaultdict(lambda: {
        'total': 0, 'o_count': 0, 'k_count': 0,
        'cat_counts': defaultdict(int),
        'o_cat_counts': defaultdict(int),
        'k_cat_counts': defaultdict(int),
    })

    # Pre-compute folio sections
    folio_sections = {}

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        folio = token.folio
        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa and fa.section else 'UNK'
            except Exception:
                folio_sections[folio] = 'UNK'
        section = folio_sections[folio]

        initial_atom = m.middle[0]

        sd = section_data[section]
        sd['total'] += 1
        sd['cat_counts'][cat] += 1

        if initial_atom == 'o':
            sd['o_count'] += 1
            sd['o_cat_counts'][cat] += 1
        if initial_atom == 'k':
            sd['k_count'] += 1
            sd['k_cat_counts'][cat] += 1

    # ---- Also collect AZC data ----
    # AZC tokens from full transcript (language=NA)
    azc_data = {'total': 0, 'o_count': 0, 'k_count': 0,
                'cat_counts': defaultdict(int)}

    for token in tx.azc():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        azc_data['total'] += 1
        initial_atom = m.middle[0]
        azc_data['cat_counts'][cat] += 1
        if initial_atom == 'o':
            azc_data['o_count'] += 1
        if initial_atom == 'k':
            azc_data['k_count'] += 1

    print("=" * 70)
    print("P-O5: AZC enrichment gradient correlates with CONTAINMENT fraction")
    print("=" * 70)
    print()

    # ---- TEST 1: o-initial MIDDLE fraction per section ----
    print("-" * 70)
    print("TEST 1: o-initial MIDDLE fraction per section")
    print("-" * 70)

    # Include AZC as a pseudo-section
    valid_sections = sorted([s for s in section_data if s != 'UNK' and section_data[s]['total'] >= 50])

    print(f"{'Section':<10} {'o-initial':>10} {'Total':>8} {'o-rate%':>9} {'k-initial':>10} {'k-rate%':>9}")
    print("-" * 60)

    # AZC row
    if azc_data['total'] >= 50:
        azc_o_rate = azc_data['o_count'] / azc_data['total'] * 100
        azc_k_rate = azc_data['k_count'] / azc_data['total'] * 100
        print(f"  {'AZC':<8} {azc_data['o_count']:>10} {azc_data['total']:>8} "
              f"{azc_o_rate:>8.2f}% {azc_data['k_count']:>10} {azc_k_rate:>8.2f}%")

    for section in valid_sections:
        sd = section_data[section]
        o_rate = sd['o_count'] / sd['total'] * 100
        k_rate = sd['k_count'] / sd['total'] * 100
        print(f"  {section:<8} {sd['o_count']:>10} {sd['total']:>8} "
              f"{o_rate:>8.2f}% {sd['k_count']:>10} {k_rate:>8.2f}%")

    # ---- TEST 2: CONTAINMENT category fraction per section ----
    print()
    print("-" * 70)
    print("TEST 2: CONTAINMENT category fraction per section")
    print("-" * 70)

    print(f"{'Section':<10} {'CONTAINMENT':>12} {'Total':>8} {'Rate%':>9}")
    print("-" * 45)

    if azc_data['total'] >= 50:
        azc_cont = azc_data['cat_counts'].get('CONTAINMENT', 0)
        azc_cont_rate = azc_cont / azc_data['total'] * 100
        print(f"  {'AZC':<8} {azc_cont:>12} {azc_data['total']:>8} {azc_cont_rate:>8.2f}%")

    for section in valid_sections:
        sd = section_data[section]
        cont = sd['cat_counts'].get('CONTAINMENT', 0)
        cont_rate = cont / sd['total'] * 100
        print(f"  {section:<8} {cont:>12} {sd['total']:>8} {cont_rate:>8.2f}%")

    # ---- TEST 3: Spearman correlation o-initial rate vs CONTAINMENT rate ----
    print()
    print("-" * 70)
    print("TEST 3: Spearman rho(o-initial rate, CONTAINMENT rate) across sections")
    print("-" * 70)

    # Build parallel arrays (include AZC if possible)
    o_rates = []
    containment_rates = []
    section_labels = []

    if azc_data['total'] >= 50:
        o_rates.append(azc_data['o_count'] / azc_data['total'])
        containment_rates.append(azc_data['cat_counts'].get('CONTAINMENT', 0) / azc_data['total'])
        section_labels.append('AZC')

    for section in valid_sections:
        sd = section_data[section]
        o_rates.append(sd['o_count'] / sd['total'])
        containment_rates.append(sd['cat_counts'].get('CONTAINMENT', 0) / sd['total'])
        section_labels.append(section)

    if len(o_rates) >= 3:
        rho_o_cont, p_o_cont = spearman_rho(o_rates, containment_rates)
        print(f"  N sections = {len(o_rates)}: {', '.join(section_labels)}")
        print(f"  rho(o-initial, CONTAINMENT) = {rho_o_cont:+.4f}, p = {p_o_cont:.6f}")
    else:
        rho_o_cont = 0.0
        p_o_cont = 1.0
        print("  WARNING: Too few sections for correlation")

    # ---- TEST 4: All 8 categories vs o-initial gradient ----
    print()
    print("-" * 70)
    print("TEST 4: All 8 categories correlated with o-initial gradient")
    print("-" * 70)

    print(f"{'Category':<15} {'Spearman rho':>13} {'p-value':>10} {'Direction':>10}")
    print("-" * 52)

    best_cat = None
    best_rho = -2.0

    for cat in CATEGORIES:
        cat_rates = []
        if azc_data['total'] >= 50:
            cat_rates.append(azc_data['cat_counts'].get(cat, 0) / azc_data['total'])
        for section in valid_sections:
            sd = section_data[section]
            cat_rates.append(sd['cat_counts'].get(cat, 0) / sd['total'])

        if len(cat_rates) >= 3 and len(cat_rates) == len(o_rates):
            rho_cat, p_cat = spearman_rho(o_rates, cat_rates)
            direction = "+" if rho_cat > 0 else "-"
            sig = ""
            if p_cat < 0.01:
                sig = " **"
            elif p_cat < 0.05:
                sig = " *"
            print(f"  {cat:<13} {rho_cat:>+12.4f} {p_cat:>10.6f} {direction:>10}{sig}")
            if rho_cat > best_rho:
                best_rho = rho_cat
                best_cat = cat

    print()
    if best_cat:
        print(f"  Best-tracking category: {best_cat} (rho = {best_rho:+.4f})")
        print(f"  CONTAINMENT rank among 8: see above")

    # ---- TEST 5: Control — k-initial rate vs THERMAL fraction ----
    print()
    print("-" * 70)
    print("TEST 5: Control — k-initial rate vs THERMAL fraction across sections")
    print("-" * 70)

    k_rates = []
    thermal_rates = []

    if azc_data['total'] >= 50:
        k_rates.append(azc_data['k_count'] / azc_data['total'])
        thermal_rates.append(azc_data['cat_counts'].get('THERMAL', 0) / azc_data['total'])

    for section in valid_sections:
        sd = section_data[section]
        k_rates.append(sd['k_count'] / sd['total'])
        thermal_rates.append(sd['cat_counts'].get('THERMAL', 0) / sd['total'])

    if len(k_rates) >= 3:
        rho_k_th, p_k_th = spearman_rho(k_rates, thermal_rates)
        print(f"  N sections = {len(k_rates)}")
        print(f"  rho(k-initial, THERMAL) = {rho_k_th:+.4f}, p = {p_k_th:.6f}")
    else:
        rho_k_th = 0.0
        p_k_th = 1.0
        print("  WARNING: Too few sections for correlation")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O5 AZC enrichment gradient vs CONTAINMENT fraction")
    print("=" * 70)

    pass_primary = rho_o_cont > 0.80
    pass_containment_best = best_cat == 'CONTAINMENT'
    pass_control = rho_k_th > 0.50

    results = [
        ("rho(o-initial, CONTAINMENT) > +0.80", pass_primary,
         f"rho = {rho_o_cont:+.4f}"),
        ("CONTAINMENT is best-tracking category", pass_containment_best,
         f"best = {best_cat} (rho = {best_rho:+.4f})" if best_cat else "N/A"),
        ("Control: rho(k-initial, THERMAL) > +0.50", pass_control,
         f"rho = {rho_k_th:+.4f}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    print()
    print(f"  PRIMARY CRITERION (rho > +0.80): {'PASS' if pass_primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if pass_primary else 'FAIL'}")


if __name__ == '__main__':
    main()
