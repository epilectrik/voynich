#!/usr/bin/env python3
"""
F-F1: f-initial 8-category profile
====================================
Test whether f-initial MIDDLEs are enriched in MARKING category.
f = "flag" maps to MARKING via CategoryClassifier. f is a rare atom
(215 total MIDDLE occurrences, 17 standalone tokens) with MARKING
classification alongside p and d.

Predictions:
  1. f-initial MARKING enrichment >= 1.3x
  2. f-initial THERMAL depletion <= 0.8x
  3. f ranked top 5 for MARKING among all initial atoms
  4. Per-section stability: MARKING enriched >= 1.2x in >= 2/4 sections

Pass criterion: MARKING >= 1.3x AND THERMAL <= 0.8x (primary),
               plus >= 3/4 sub-criteria total for full pass.

Controls: p-initial (MARKING), d-initial (MARKING), c-initial (MONITORING)
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


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
    print("F-F1: f-initial MARKING category enrichment")
    print("=" * 70)
    print()

    # Global baselines
    global_marking_rate = global_cat_counts['MARKING'] / global_total if global_total > 0 else 0
    global_thermal_rate = global_cat_counts['THERMAL'] / global_total if global_total > 0 else 0
    global_monitoring_rate = global_cat_counts['MONITORING'] / global_total if global_total > 0 else 0
    print("Global baseline: MARKING    = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['MARKING'], global_total, global_marking_rate, global_marking_rate * 100))
    print("Global baseline: THERMAL    = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['THERMAL'], global_total, global_thermal_rate, global_thermal_rate * 100))
    print("Global baseline: MONITORING = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['MONITORING'], global_total, global_monitoring_rate, global_monitoring_rate * 100))
    print()

    # ---- TEST 1: Rank all initial atoms by MARKING fraction ----
    print("-" * 70)
    print("TEST 1: All initial atoms ranked by MARKING fraction")
    print("-" * 70)

    atom_marking = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 10:  # lower threshold for rare atoms
            continue
        mark_n = atom_cat_counts[atom].get('MARKING', 0)
        frac = mark_n / n
        enrichment = frac / global_marking_rate if global_marking_rate > 0 else 0
        atom_marking.append((atom, frac, mark_n, n, enrichment))

    atom_marking.sort(key=lambda x: -x[1])

    print("%-6s %10s %8s %8s %11s" % ('Atom', 'MARKING%', 'Count', 'Total', 'Enrichment'))
    print("-" * 50)
    f_rank = None
    f_frac = 0
    f_mark_n = 0
    f_total = 0
    f_enrichment = 0
    for rank, (atom, frac, mark_n, n, enrich) in enumerate(atom_marking, 1):
        marker = " <-- f-initial" if atom == 'f' else ""
        if atom in ('p', 'd', 'c'):
            marker = " <-- %s (control)" % atom
        print("  %-4s %9.2f%% %8d %8d %10.3fx%s" % (atom, frac * 100, mark_n, n, enrich, marker))
        if atom == 'f':
            f_rank = rank
            f_frac = frac
            f_mark_n = mark_n
            f_total = n
            f_enrichment = enrich

    print()
    if f_rank is not None:
        print("  f-initial rank: #%d of %d atoms" % (f_rank, len(atom_marking)))
    else:
        print("  WARNING: f-initial not found or too few tokens")

    # ---- TEST 2: Chi-square test for MARKING ----
    print()
    print("-" * 70)
    print("TEST 2: Chi-square -- f-initial MARKING vs global rate")
    print("-" * 70)

    p_val_marking = 1.0
    chi2_marking = 0.0
    if f_rank is not None and f_total > 0:
        a = f_mark_n
        b = f_total - f_mark_n
        c_other = global_cat_counts['MARKING'] - f_mark_n
        d = (global_total - f_total) - c_other

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

        print("  f-initial MARKING: %d/%d = %.2f%%" % (a, f_total, f_frac * 100))
        print("  Global MARKING:    %d/%d = %.2f%%" % (global_cat_counts['MARKING'], global_total, global_marking_rate * 100))
        print("  Enrichment: %.3fx" % f_enrichment)
        print("  Chi-square: %.3f, p = %.6f" % (chi2_marking, p_val_marking))
        if p_val_marking < 0.001:
            print("  Significance: p < 0.001 ***")
        elif p_val_marking < 0.01:
            print("  Significance: p < 0.01 **")
        elif p_val_marking < 0.05:
            print("  Significance: p < 0.05 *")
        else:
            print("  Significance: not significant")

    # ---- TEST 3: Full 8-category profile for f-initial ----
    print()
    print("-" * 70)
    print("TEST 3: Full 8-category profile for f-initial MIDDLEs")
    print("-" * 70)

    f_thermal_enrichment = 0.0
    f_marking_frac = 0.0
    if f_rank is not None and f_total > 0:
        print("%-15s %11s %9s %11s %7s" % ('Category', 'f-initial%', 'Global%', 'Enrichment', 'Count'))
        print("-" * 55)
        for cat in CATEGORIES:
            f_cat_n = atom_cat_counts['f'].get(cat, 0)
            f_cat_frac = f_cat_n / f_total if f_total > 0 else 0
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = f_cat_frac / global_frac if global_frac > 0 else 0
            marker = ""
            if cat == 'MARKING':
                marker = "  <-- predicted enriched"
                f_marking_frac = f_cat_frac
            elif cat == 'THERMAL':
                marker = "  <-- predicted depleted"
                f_thermal_enrichment = enrich
            print("  %-13s %10.2f%% %8.2f%% %10.3fx %7d%s" % (cat, f_cat_frac * 100, global_frac * 100, enrich, f_cat_n, marker))

    # ---- TEST 4: Per-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: f-initial MARKING enrichment per section")
    print("-" * 70)

    sections_tested = 0
    sections_enriched = 0

    for section in sorted(atom_section_totals.get('f', {}).keys()):
        f_sec_total = atom_section_totals['f'][section]
        f_sec_mark = atom_section_cat['f'][section].get('MARKING', 0)
        if f_sec_total < 5:  # low threshold for rare atom
            continue

        # Section-level MARKING baseline
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_mark = sum(atom_section_cat[a][section].get('MARKING', 0) for a in atom_section_cat)
        sec_rate = sec_mark / sec_total if sec_total > 0 else 0

        f_rate = f_sec_mark / f_sec_total
        enrich = f_rate / sec_rate if sec_rate > 0 else 0

        sections_tested += 1
        if enrich >= 1.2:
            sections_enriched += 1

        status = "ENRICHED" if enrich >= 1.2 else "not enriched"
        print("  Section %8s: f-initial %d/%d = %.1f%%, "
              "section baseline %.1f%%, enrichment %.3fx [%s]" %
              (section, f_sec_mark, f_sec_total, f_rate * 100, sec_rate * 100, enrich, status))

    print()
    print("  Sections with MARKING enrichment >= 1.2x: %d/%d" % (sections_enriched, sections_tested))
    pass_section = sections_enriched >= 2

    # ---- CONTROLS: Compare to p-initial (MARKING), d-initial (MARKING), c-initial (MONITORING) ----
    print()
    print("-" * 70)
    print("CONTROLS: Reference atoms")
    print("-" * 70)

    control_atoms = [
        ('p', 'MARKING', 'flag/pause (MARKING)'),
        ('d', 'MARKING', 'seal (MARKING)'),
        ('c', 'MONITORING', 'adjust/calibrate (MONITORING)'),
    ]

    for ctrl_atom, expected_cat, label in control_atoms:
        ctrl_n = atom_totals.get(ctrl_atom, 0)
        if ctrl_n < 10:
            print("  %s-initial (%s): too few tokens (%d)" % (ctrl_atom, label, ctrl_n))
            continue
        ctrl_mark = atom_cat_counts[ctrl_atom].get('MARKING', 0)
        ctrl_mark_rate = ctrl_mark / ctrl_n
        ctrl_mark_enrich = ctrl_mark_rate / global_marking_rate if global_marking_rate > 0 else 0
        ctrl_exp_n = atom_cat_counts[ctrl_atom].get(expected_cat, 0)
        ctrl_exp_rate = ctrl_exp_n / ctrl_n
        global_exp_rate = global_cat_counts[expected_cat] / global_total if global_total > 0 else 0
        ctrl_exp_enrich = ctrl_exp_rate / global_exp_rate if global_exp_rate > 0 else 0

        print("  %s-initial (%s, N=%d):" % (ctrl_atom, label, ctrl_n))
        print("    MARKING: %.2f%% (%.3fx enrichment)" % (ctrl_mark_rate * 100, ctrl_mark_enrich))
        print("    %s: %.2f%% (%.3fx enrichment)" % (expected_cat, ctrl_exp_rate * 100, ctrl_exp_enrich))

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: F-F1 f-initial MARKING category enrichment")
    print("=" * 70)

    pass_marking = f_enrichment >= 1.3 if f_rank is not None else False
    pass_thermal = f_thermal_enrichment <= 0.8 if f_rank is not None else False
    pass_rank = f_rank is not None and f_rank <= 5
    pass_chi2 = p_val_marking < 0.01 if f_rank is not None else False

    results = [
        ("MARKING enrichment >= 1.3x", pass_marking,
         "%.3fx" % f_enrichment if f_rank else "N/A"),
        ("THERMAL depletion <= 0.8x", pass_thermal,
         "%.3fx" % f_thermal_enrichment if f_rank else "N/A"),
        ("Ranked top 5 for MARKING", pass_rank,
         "rank #%d" % f_rank if f_rank else "N/A"),
        ("Section stability (>= 2 sections enriched)", pass_section,
         "%d/%d" % (sections_enriched, sections_tested)),
    ]

    sub_pass_count = sum(1 for _, passed, _ in results if passed)
    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print("  [%s] %s: %s" % (status, desc, val))

    primary = pass_marking and pass_thermal
    overall = primary and sub_pass_count >= 3
    print()
    print("  PRIMARY CRITERION (MARKING >= 1.3x AND THERMAL <= 0.8x): %s" % ('PASS' if primary else 'FAIL'))
    print("  SUB-CRITERIA: %d/4 passed (need >= 3)" % sub_pass_count)
    print("  OVERALL VERDICT: %s" % ('PASS' if overall else 'FAIL'))


if __name__ == '__main__':
    main()
