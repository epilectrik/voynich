"""
P-C9: Section gradient — c tracks MARKING/MONITORING across sections

Tests whether c-initial MIDDLE rate correlates with MARKING or MONITORING
category rates across B sections and AZC.

Predictions:
- rho(c-initial rate, MARKING or MONITORING rate) >= +0.50
- THERMAL |rho| <= 0.40 (c doesn't track thermal, that's k)
- Control: k-initial vs THERMAL should be strong positive

Based on:
- {c,h} monitoring cluster r=+0.746 (C1207)
- c→h obligatory junction 100% (C1216)
- CategoryClassifier maps c → MARKING
- H-kernel affinity 0.483 (C1251)
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']


def spearman_rho(x, y):
    n = len(x)
    if n < 4:
        return 0.0, 1.0

    def normal_cdf(z):
        if z < -8: return 0.0
        if z > 8: return 1.0
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        p_c = 0.3275911
        sign = 1 if z >= 0 else -1
        z_abs = abs(z)
        t = 1.0 / (1.0 + p_c * z_abs)
        val = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2.0)
        return 0.5 * (1.0 + sign * val)

    def rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0, 1.0
    rho = num / (den_x * den_y)
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-15))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


def main():
    print("=" * 70)
    print("P-C9: Section gradient - c tracks MARKING/MONITORING")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()

    # --- Collect per-section data from Currier B ---
    section_data = defaultdict(lambda: {
        'total': 0, 'c_initial': 0, 'k_initial': 0, 'h_initial': 0,
        'cats': defaultdict(int)
    })

    folio_sections = {}

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        folio = token.folio
        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa.section else 'UNKNOWN'
            except Exception:
                folio_sections[folio] = 'UNKNOWN'

        section = folio_sections[folio]
        m = morph.extract(w)
        if not m or not m.middle:
            continue

        mid = m.middle
        cat = cc.classify(mid)

        section_data[section]['total'] += 1
        if cat in CATEGORIES:
            section_data[section]['cats'][cat] += 1

        # Check initial atom of MIDDLE
        if len(mid) > 0:
            first_char = mid[0]
            if first_char == 'c':
                section_data[section]['c_initial'] += 1
            if first_char == 'k':
                section_data[section]['k_initial'] += 1
            if first_char == 'h':
                section_data[section]['h_initial'] += 1

    # --- Also include AZC ---
    azc_data = {'total': 0, 'c_initial': 0, 'k_initial': 0, 'h_initial': 0, 'cats': defaultdict(int)}
    for token in tx.azc():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        mid = m.middle
        cat = cc.classify(mid)
        azc_data['total'] += 1
        if cat in CATEGORIES:
            azc_data['cats'][cat] += 1
        if len(mid) > 0:
            if mid[0] == 'c':
                azc_data['c_initial'] += 1
            if mid[0] == 'k':
                azc_data['k_initial'] += 1
            if mid[0] == 'h':
                azc_data['h_initial'] += 1

    section_data['AZC'] = azc_data

    # --- Build vectors ---
    sections = sorted([s for s in section_data if section_data[s]['total'] >= 50])

    print(f"\nSections with >= 50 tokens: {len(sections)}")
    print(f"Sections: {sections}\n")

    # Section breakdown table
    print("-" * 100)
    print(f"{'Section':<15} {'Total':>7} {'c-init%':>8} {'k-init%':>8} {'h-init%':>8}", end="")
    for cat in CATEGORIES:
        print(f" {cat[:5]:>6}", end="")
    print()
    print("-" * 100)

    for sec in sections:
        d = section_data[sec]
        total = d['total']
        c_rate = d['c_initial'] / total * 100 if total > 0 else 0
        k_rate = d['k_initial'] / total * 100 if total > 0 else 0
        h_rate = d['h_initial'] / total * 100 if total > 0 else 0
        print(f"{sec:<15} {total:>7} {c_rate:>7.2f}% {k_rate:>7.2f}% {h_rate:>7.2f}%", end="")
        for cat in CATEGORIES:
            cat_rate = d['cats'][cat] / total * 100 if total > 0 else 0
            print(f" {cat_rate:>5.1f}%", end="")
        print()

    print("-" * 100)

    # --- Compute correlations ---
    c_rates = []
    k_rates = []
    h_rates = []
    cat_rates = {cat: [] for cat in CATEGORIES}

    for sec in sections:
        d = section_data[sec]
        total = d['total']
        c_rates.append(d['c_initial'] / total if total > 0 else 0)
        k_rates.append(d['k_initial'] / total if total > 0 else 0)
        h_rates.append(d['h_initial'] / total if total > 0 else 0)
        for cat in CATEGORIES:
            cat_rates[cat].append(d['cats'][cat] / total if total > 0 else 0)

    print("\n" + "=" * 70)
    print("CORRELATIONS: c-initial rate vs category rates")
    print("=" * 70)
    print(f"{'Category':<15} {'rho':>8} {'p-value':>10} {'Verdict':>10}")
    print("-" * 50)

    best_cat = None
    best_rho = -2.0
    c_thermal_rho = None

    for cat in CATEGORIES:
        rho, p = spearman_rho(c_rates, cat_rates[cat])
        verdict = ""
        if cat in ('MARKING', 'MONITORING') and rho >= 0.50:
            verdict = "TARGET"
        elif cat == 'THERMAL' and abs(rho) > 0.40:
            verdict = "WARN"
        print(f"{cat:<15} {rho:>+8.3f} {p:>10.4f} {verdict:>10}")
        if cat == 'THERMAL':
            c_thermal_rho = rho
        if rho > best_rho:
            best_rho = rho
            best_cat = cat

    print(f"\nBest tracker for c: {best_cat} (rho={best_rho:+.3f})")

    # --- Control: k-initial vs THERMAL ---
    print("\n" + "=" * 70)
    print("CONTROL: k-initial rate vs THERMAL rate")
    print("=" * 70)
    rho_k_thermal, p_k_thermal = spearman_rho(k_rates, cat_rates['THERMAL'])
    print(f"rho(k-initial, THERMAL) = {rho_k_thermal:+.3f}, p = {p_k_thermal:.4f}")

    # --- Validation: h-initial vs MONITORING ---
    print("\n" + "=" * 70)
    print("VALIDATION: h-initial rate vs MONITORING rate")
    print("=" * 70)
    rho_h_mon, p_h_mon = spearman_rho(h_rates, cat_rates['MONITORING'])
    print(f"rho(h-initial, MONITORING) = {rho_h_mon:+.3f}, p = {p_h_mon:.4f}")

    # Also h vs all categories
    print(f"\n{'Category':<15} {'rho(h)':>8} {'p':>10}")
    print("-" * 40)
    for cat in CATEGORIES:
        rho, p = spearman_rho(h_rates, cat_rates[cat])
        print(f"{cat:<15} {rho:>+8.3f} {p:>10.4f}")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # P1: c tracks MARKING or MONITORING with rho >= +0.50
    marking_rho, _ = spearman_rho(c_rates, cat_rates['MARKING'])
    monitoring_rho, _ = spearman_rho(c_rates, cat_rates['MONITORING'])
    best_tracker_rho = max(marking_rho, monitoring_rho)
    best_tracker_name = 'MARKING' if marking_rho >= monitoring_rho else 'MONITORING'
    p1 = best_tracker_rho >= 0.50
    print(f"P1: c best-tracker is {best_tracker_name} (rho={best_tracker_rho:+.3f}) >= +0.50: {'PASS' if p1 else 'FAIL'}")

    # P2: THERMAL |rho| <= 0.40
    p2 = abs(c_thermal_rho) <= 0.40
    print(f"P2: c vs THERMAL |rho|={abs(c_thermal_rho):.3f} <= 0.40: {'PASS' if p2 else 'FAIL'}")

    # P3: k-initial vs THERMAL positive and strong
    p3 = rho_k_thermal >= 0.40
    print(f"P3: k-initial vs THERMAL rho={rho_k_thermal:+.3f} >= +0.40 (control): {'PASS' if p3 else 'FAIL'}")

    overall = p1 and p2
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    print(f"  c tracks {best_tracker_name} with rho={best_tracker_rho:+.3f}")
    if overall:
        print("  c-atom section gradient confirms MARKING/MONITORING alignment")
    else:
        print("  c-atom section gradient does NOT confirm MARKING/MONITORING alignment")


if __name__ == '__main__':
    main()
