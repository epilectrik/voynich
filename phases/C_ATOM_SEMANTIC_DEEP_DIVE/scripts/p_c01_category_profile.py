#!/usr/bin/env python3
"""
P-C1: c-initial 8-category profile

Test whether c-initial MIDDLEs are enriched in MARKING category.
c = "adjust" maps to MARKING via CategoryClassifier. The {c,h} monitoring
cluster (C1207, r=+0.746) and c's MEDIAL slot position (C1209, mean 0.408)
suggest c acts as an adjustment/calibration marker.

Predictions:
  1. c-initial MARKING enrichment >= 1.3x
  2. c-initial THERMAL depletion <= 0.8x
  3. c ranked top 4 for MARKING among all initial atoms
  4. Per-section stability: MARKING enriched in >= 3/5 sections

Pass criterion: MARKING >= 1.3x AND THERMAL <= 0.8x (primary),
               3/4 sub-criteria total for full pass.
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


def chi2_1df_p(chi2_val):
    """Approximate p-value for chi-square with 1 df."""
    if chi2_val <= 0:
        return 1.0
    z = math.sqrt(chi2_val)
    return 2.0 * (1.0 - normal_cdf(z))


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Collect data: (initial_atom, category, section) tuples
    atom_cat_counts = defaultdict(lambda: defaultdict(int))  # atom -> cat -> count
    atom_totals = defaultdict(int)
    global_cat_counts = defaultdict(int)
    global_total = 0

    # Per-section tracking
    atom_section_cat = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    atom_section_totals = defaultdict(lambda: defaultdict(int))

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

        initial_atom = m.middle[0]
        section = token.section or 'UNK'

        atom_cat_counts[initial_atom][cat] += 1
        atom_totals[initial_atom] += 1
        global_cat_counts[cat] += 1
        global_total += 1

        atom_section_cat[initial_atom][section][cat] += 1
        atom_section_totals[initial_atom][section] += 1

    print("=" * 70)
    print("P-C1: c-initial MARKING category enrichment")
    print("=" * 70)
    print()

    # Global baselines
    global_marking_rate = global_cat_counts['MARKING'] / global_total if global_total > 0 else 0
    global_thermal_rate = global_cat_counts['THERMAL'] / global_total if global_total > 0 else 0
    print(f"Global baseline: MARKING = {global_cat_counts['MARKING']}/{global_total} "
          f"= {global_marking_rate:.4f} ({global_marking_rate*100:.2f}%)")
    print(f"Global baseline: THERMAL = {global_cat_counts['THERMAL']}/{global_total} "
          f"= {global_thermal_rate:.4f} ({global_thermal_rate*100:.2f}%)")
    print()

    # ---- TEST 1: Rank all initial atoms by MARKING fraction ----
    print("-" * 70)
    print("TEST 1: All initial atoms ranked by MARKING fraction")
    print("-" * 70)

    atom_marking = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 20:
            continue
        mark_n = atom_cat_counts[atom].get('MARKING', 0)
        frac = mark_n / n
        enrichment = frac / global_marking_rate if global_marking_rate > 0 else 0
        atom_marking.append((atom, frac, mark_n, n, enrichment))

    atom_marking.sort(key=lambda x: -x[1])

    print(f"{'Atom':<6} {'MARKING%':>10} {'Count':>8} {'Total':>8} {'Enrichment':>11}")
    print("-" * 50)
    c_rank = None
    c_frac = 0
    c_mark_n = 0
    c_total = 0
    c_enrichment = 0
    for rank, (atom, frac, mark_n, n, enrich) in enumerate(atom_marking, 1):
        marker = " <-- c-initial" if atom == 'c' else ""
        print(f"  {atom:<4} {frac*100:>9.2f}% {mark_n:>8} {n:>8} {enrich:>10.3f}x{marker}")
        if atom == 'c':
            c_rank = rank
            c_frac = frac
            c_mark_n = mark_n
            c_total = n
            c_enrichment = enrich

    print()
    if c_rank is not None:
        print(f"  c-initial rank: #{c_rank} of {len(atom_marking)} atoms")
    else:
        print("  WARNING: c-initial not found or too few tokens")

    # ---- TEST 2: Chi-square test for MARKING ----
    print()
    print("-" * 70)
    print("TEST 2: Chi-square -- c-initial MARKING vs global rate")
    print("-" * 70)

    p_val_marking = 1.0
    chi2_marking = 0.0
    if c_rank is not None and c_total > 0:
        a = c_mark_n
        b = c_total - c_mark_n
        c_other = global_cat_counts['MARKING'] - c_mark_n
        d = (global_total - c_total) - c_other
        total = a + b + c_other + d

        expected_a = (a + b) * (a + c_other) / total if total > 0 else 0
        expected_b = (a + b) * (b + d) / total if total > 0 else 0
        expected_c = (c_other + d) * (a + c_other) / total if total > 0 else 0
        expected_d = (c_other + d) * (b + d) / total if total > 0 else 0

        chi2_marking = 0
        for obs, exp in [(a, expected_a), (b, expected_b), (c_other, expected_c), (d, expected_d)]:
            if exp > 0:
                chi2_marking += (obs - exp) ** 2 / exp

        p_val_marking = chi2_1df_p(chi2_marking)

        print(f"  c-initial MARKING: {a}/{c_total} = {c_frac*100:.2f}%")
        print(f"  Global MARKING:    {global_cat_counts['MARKING']}/{global_total} = {global_marking_rate*100:.2f}%")
        print(f"  Enrichment: {c_enrichment:.3f}x")
        print(f"  Chi-square: {chi2_marking:.3f}, p = {p_val_marking:.6f}")
        if p_val_marking < 0.001:
            print(f"  Significance: p < 0.001 ***")
        elif p_val_marking < 0.01:
            print(f"  Significance: p < 0.01 **")
        elif p_val_marking < 0.05:
            print(f"  Significance: p < 0.05 *")
        else:
            print(f"  Significance: not significant")

    # ---- TEST 3: Full 8-category profile for c-initial ----
    print()
    print("-" * 70)
    print("TEST 3: Full 8-category profile for c-initial MIDDLEs")
    print("-" * 70)

    c_thermal_enrichment = 0.0
    if c_rank is not None and c_total > 0:
        print(f"{'Category':<15} {'c-initial%':>11} {'Global%':>9} {'Enrichment':>11} {'Count':>7}")
        print("-" * 55)
        for cat in CATEGORIES:
            c_cat_n = atom_cat_counts['c'].get(cat, 0)
            c_cat_frac = c_cat_n / c_total if c_total > 0 else 0
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = c_cat_frac / global_frac if global_frac > 0 else 0
            marker = ""
            if cat == 'MARKING':
                marker = "  <-- predicted enriched"
            elif cat == 'THERMAL':
                marker = "  <-- predicted depleted"
                c_thermal_enrichment = enrich
            print(f"  {cat:<13} {c_cat_frac*100:>10.2f}% {global_frac*100:>8.2f}% {enrich:>10.3f}x {c_cat_n:>7}{marker}")

    # ---- TEST 4: Per-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: c-initial MARKING enrichment per section")
    print("-" * 70)

    sections_tested = 0
    sections_enriched = 0

    for section in sorted(atom_section_totals.get('c', {}).keys()):
        c_sec_total = atom_section_totals['c'][section]
        c_sec_mark = atom_section_cat['c'][section].get('MARKING', 0)
        if c_sec_total < 10:
            continue

        # Section-level MARKING baseline
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_mark = sum(atom_section_cat[a][section].get('MARKING', 0) for a in atom_section_cat)
        sec_rate = sec_mark / sec_total if sec_total > 0 else 0

        c_rate = c_sec_mark / c_sec_total
        enrich = c_rate / sec_rate if sec_rate > 0 else 0

        sections_tested += 1
        if enrich >= 1.2:
            sections_enriched += 1

        status = "ENRICHED" if enrich >= 1.2 else "not enriched"
        print(f"  Section {section:>8}: c-initial {c_sec_mark}/{c_sec_total} = {c_rate*100:.1f}%, "
              f"section baseline {sec_rate*100:.1f}%, enrichment {enrich:.3f}x [{status}]")

    print()
    print(f"  Sections with MARKING enrichment >= 1.2x: {sections_enriched}/{sections_tested}")
    pass_section = sections_enriched >= 3

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-C1 c-initial MARKING category enrichment")
    print("=" * 70)

    pass_marking = c_enrichment >= 1.3 if c_rank is not None else False
    pass_thermal = c_thermal_enrichment <= 0.8 if c_rank is not None else False
    pass_rank = c_rank is not None and c_rank <= 4
    pass_chi2 = p_val_marking < 0.01 if c_rank is not None else False

    results = [
        ("MARKING enrichment >= 1.3x", pass_marking,
         f"{c_enrichment:.3f}x" if c_rank else "N/A"),
        ("THERMAL depletion <= 0.8x", pass_thermal,
         f"{c_thermal_enrichment:.3f}x" if c_rank else "N/A"),
        ("Ranked top 4 for MARKING", pass_rank,
         f"rank #{c_rank}" if c_rank else "N/A"),
        ("Section stability (>= 3 sections enriched)", pass_section,
         f"{sections_enriched}/{sections_tested}"),
    ]

    sub_pass_count = sum(1 for _, passed, _ in results if passed)
    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_marking and pass_thermal
    overall = primary and sub_pass_count >= 3
    print()
    print(f"  PRIMARY CRITERION (MARKING >= 1.3x AND THERMAL <= 0.8x): {'PASS' if primary else 'FAIL'}")
    print(f"  SUB-CRITERIA: {sub_pass_count}/4 passed (need >= 3)")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
