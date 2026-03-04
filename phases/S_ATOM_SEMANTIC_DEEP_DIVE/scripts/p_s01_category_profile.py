#!/usr/bin/env python3
"""
S-S1: s-initial 8-category profile

Test whether s-initial MIDDLEs are enriched in STAGING category.
s = "sequence" maps to STAGING via CategoryClassifier. Late-MEDIAL slot
position (mean 0.640, C1209), weakest positive carryover (z=+2.47, C1208),
and s->h junction enrichment 8.1x (C1216) suggest s acts as a
sequencing/staging element.

Predictions:
  1. s-initial STAGING enrichment >= 1.3x (lower threshold due to smaller N)
  2. s-initial THERMAL depletion <= 0.8x
  3. s ranked top 5 for STAGING among all initial atoms
  4. Per-section stability: STAGING enriched >= 1.2x in >= 2/4 sections

Pass criterion: STAGING >= 1.3x AND THERMAL <= 0.8x (primary),
               plus >= 3/4 sub-criteria total for full pass.

Controls: o-initial (STAGING), k-initial (THERMAL), c-initial (MONITORING)

ALSO: report whether MONITORING > STAGING for s-initial (H1 vs H2 discriminant)
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
    print("S-S1: s-initial STAGING category enrichment")
    print("=" * 70)
    print()

    # Global baselines
    global_staging_rate = global_cat_counts['STAGING'] / global_total if global_total > 0 else 0
    global_thermal_rate = global_cat_counts['THERMAL'] / global_total if global_total > 0 else 0
    global_monitoring_rate = global_cat_counts['MONITORING'] / global_total if global_total > 0 else 0
    print("Global baseline: STAGING    = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['STAGING'], global_total, global_staging_rate, global_staging_rate * 100))
    print("Global baseline: THERMAL    = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['THERMAL'], global_total, global_thermal_rate, global_thermal_rate * 100))
    print("Global baseline: MONITORING = %d/%d = %.4f (%.2f%%)" %
          (global_cat_counts['MONITORING'], global_total, global_monitoring_rate, global_monitoring_rate * 100))
    print()

    # ---- TEST 1: Rank all initial atoms by STAGING fraction ----
    print("-" * 70)
    print("TEST 1: All initial atoms ranked by STAGING fraction")
    print("-" * 70)

    atom_staging = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 20:
            continue
        stag_n = atom_cat_counts[atom].get('STAGING', 0)
        frac = stag_n / n
        enrichment = frac / global_staging_rate if global_staging_rate > 0 else 0
        atom_staging.append((atom, frac, stag_n, n, enrichment))

    atom_staging.sort(key=lambda x: -x[1])

    print("%-6s %10s %8s %8s %11s" % ('Atom', 'STAGING%', 'Count', 'Total', 'Enrichment'))
    print("-" * 50)
    s_rank = None
    s_frac = 0
    s_stag_n = 0
    s_total = 0
    s_enrichment = 0
    for rank, (atom, frac, stag_n, n, enrich) in enumerate(atom_staging, 1):
        marker = " <-- s-initial" if atom == 's' else ""
        print("  %-4s %9.2f%% %8d %8d %10.3fx%s" % (atom, frac * 100, stag_n, n, enrich, marker))
        if atom == 's':
            s_rank = rank
            s_frac = frac
            s_stag_n = stag_n
            s_total = n
            s_enrichment = enrich

    print()
    if s_rank is not None:
        print("  s-initial rank: #%d of %d atoms" % (s_rank, len(atom_staging)))
    else:
        print("  WARNING: s-initial not found or too few tokens")

    # ---- TEST 2: Chi-square test for STAGING ----
    print()
    print("-" * 70)
    print("TEST 2: Chi-square -- s-initial STAGING vs global rate")
    print("-" * 70)

    p_val_staging = 1.0
    chi2_staging = 0.0
    if s_rank is not None and s_total > 0:
        a = s_stag_n
        b = s_total - s_stag_n
        c_other = global_cat_counts['STAGING'] - s_stag_n
        d = (global_total - s_total) - c_other

        total = a + b + c_other + d
        expected_a = (a + b) * (a + c_other) / total if total > 0 else 0
        expected_b = (a + b) * (b + d) / total if total > 0 else 0
        expected_c = (c_other + d) * (a + c_other) / total if total > 0 else 0
        expected_d = (c_other + d) * (b + d) / total if total > 0 else 0

        chi2_staging = 0
        for obs, exp in [(a, expected_a), (b, expected_b), (c_other, expected_c), (d, expected_d)]:
            if exp > 0:
                chi2_staging += (obs - exp) ** 2 / exp

        p_val_staging = chi2_1df_p(chi2_staging)

        print("  s-initial STAGING: %d/%d = %.2f%%" % (a, s_total, s_frac * 100))
        print("  Global STAGING:    %d/%d = %.2f%%" % (global_cat_counts['STAGING'], global_total, global_staging_rate * 100))
        print("  Enrichment: %.3fx" % s_enrichment)
        print("  Chi-square: %.3f, p = %.6f" % (chi2_staging, p_val_staging))
        if p_val_staging < 0.001:
            print("  Significance: p < 0.001 ***")
        elif p_val_staging < 0.01:
            print("  Significance: p < 0.01 **")
        elif p_val_staging < 0.05:
            print("  Significance: p < 0.05 *")
        else:
            print("  Significance: not significant")

    # ---- TEST 3: Full 8-category profile for s-initial ----
    print()
    print("-" * 70)
    print("TEST 3: Full 8-category profile for s-initial MIDDLEs")
    print("-" * 70)

    s_thermal_enrichment = 0.0
    s_monitoring_frac = 0.0
    s_staging_frac = 0.0
    if s_rank is not None and s_total > 0:
        print("%-15s %11s %9s %11s %7s" % ('Category', 's-initial%', 'Global%', 'Enrichment', 'Count'))
        print("-" * 55)
        for cat in CATEGORIES:
            s_cat_n = atom_cat_counts['s'].get(cat, 0)
            s_cat_frac = s_cat_n / s_total if s_total > 0 else 0
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = s_cat_frac / global_frac if global_frac > 0 else 0
            marker = ""
            if cat == 'STAGING':
                marker = "  <-- predicted enriched"
                s_staging_frac = s_cat_frac
            elif cat == 'THERMAL':
                marker = "  <-- predicted depleted"
                s_thermal_enrichment = enrich
            elif cat == 'MONITORING':
                marker = "  <-- H1 vs H2 discriminant"
                s_monitoring_frac = s_cat_frac
            print("  %-13s %10.2f%% %8.2f%% %10.3fx %7d%s" % (cat, s_cat_frac * 100, global_frac * 100, enrich, s_cat_n, marker))

        # Key H1 vs H2 discriminant
        print()
        print("  --- H1 vs H2 DISCRIMINANT ---")
        print("  H1 ('sequence' -> STAGING): s-initial STAGING = %.2f%%" % (s_staging_frac * 100))
        print("  H2 ('sift' -> MONITORING):  s-initial MONITORING = %.2f%%" % (s_monitoring_frac * 100))
        if s_monitoring_frac > s_staging_frac:
            print("  --> MONITORING > STAGING: favors H2 ('sift/sort')")
        else:
            print("  --> STAGING >= MONITORING: favors H1 ('sequence')")

    # ---- TEST 4: Per-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: s-initial STAGING enrichment per section")
    print("-" * 70)

    sections_tested = 0
    sections_enriched = 0

    for section in sorted(atom_section_totals.get('s', {}).keys()):
        s_sec_total = atom_section_totals['s'][section]
        s_sec_stag = atom_section_cat['s'][section].get('STAGING', 0)
        if s_sec_total < 10:
            continue

        # Section-level STAGING baseline
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_stag = sum(atom_section_cat[a][section].get('STAGING', 0) for a in atom_section_cat)
        sec_rate = sec_stag / sec_total if sec_total > 0 else 0

        s_rate = s_sec_stag / s_sec_total
        enrich = s_rate / sec_rate if sec_rate > 0 else 0

        sections_tested += 1
        if enrich >= 1.2:
            sections_enriched += 1

        status = "ENRICHED" if enrich >= 1.2 else "not enriched"
        print("  Section %8s: s-initial %d/%d = %.1f%%, "
              "section baseline %.1f%%, enrichment %.3fx [%s]" %
              (section, s_sec_stag, s_sec_total, s_rate * 100, sec_rate * 100, enrich, status))

    print()
    print("  Sections with STAGING enrichment >= 1.2x: %d/%d" % (sections_enriched, sections_tested))
    pass_section = sections_enriched >= 2  # lower threshold for s (2/4 instead of 3/5)

    # ---- CONTROLS: Compare to o-initial (STAGING), k-initial (THERMAL), c-initial (MONITORING) ----
    print()
    print("-" * 70)
    print("CONTROLS: Reference atoms")
    print("-" * 70)

    control_atoms = [
        ('o', 'STAGING', 'arrange/vessel'),
        ('k', 'THERMAL', 'energy driver'),
        ('c', 'MONITORING', 'adjust/calibrate'),
    ]

    for ctrl_atom, expected_cat, label in control_atoms:
        ctrl_n = atom_totals.get(ctrl_atom, 0)
        if ctrl_n < 20:
            print("  %s-initial (%s): too few tokens (%d)" % (ctrl_atom, label, ctrl_n))
            continue
        ctrl_stag = atom_cat_counts[ctrl_atom].get('STAGING', 0)
        ctrl_stag_rate = ctrl_stag / ctrl_n
        ctrl_stag_enrich = ctrl_stag_rate / global_staging_rate if global_staging_rate > 0 else 0
        ctrl_exp_n = atom_cat_counts[ctrl_atom].get(expected_cat, 0)
        ctrl_exp_rate = ctrl_exp_n / ctrl_n
        global_exp_rate = global_cat_counts[expected_cat] / global_total if global_total > 0 else 0
        ctrl_exp_enrich = ctrl_exp_rate / global_exp_rate if global_exp_rate > 0 else 0

        print("  %s-initial (%s, N=%d):" % (ctrl_atom, label, ctrl_n))
        print("    STAGING: %.2f%% (%.3fx enrichment)" % (ctrl_stag_rate * 100, ctrl_stag_enrich))
        print("    %s: %.2f%% (%.3fx enrichment)" % (expected_cat, ctrl_exp_rate * 100, ctrl_exp_enrich))

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: S-S1 s-initial STAGING category enrichment")
    print("=" * 70)

    pass_staging = s_enrichment >= 1.3 if s_rank is not None else False
    pass_thermal = s_thermal_enrichment <= 0.8 if s_rank is not None else False
    pass_rank = s_rank is not None and s_rank <= 5
    pass_chi2 = p_val_staging < 0.01 if s_rank is not None else False

    results = [
        ("STAGING enrichment >= 1.3x", pass_staging,
         "%.3fx" % s_enrichment if s_rank else "N/A"),
        ("THERMAL depletion <= 0.8x", pass_thermal,
         "%.3fx" % s_thermal_enrichment if s_rank else "N/A"),
        ("Ranked top 5 for STAGING", pass_rank,
         "rank #%d" % s_rank if s_rank else "N/A"),
        ("Section stability (>= 2 sections enriched)", pass_section,
         "%d/%d" % (sections_enriched, sections_tested)),
    ]

    sub_pass_count = sum(1 for _, passed, _ in results if passed)
    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print("  [%s] %s: %s" % (status, desc, val))

    primary = pass_staging and pass_thermal
    overall = primary and sub_pass_count >= 3
    print()
    print("  PRIMARY CRITERION (STAGING >= 1.3x AND THERMAL <= 0.8x): %s" % ('PASS' if primary else 'FAIL'))
    print("  SUB-CRITERIA: %d/4 passed (need >= 3)" % sub_pass_count)
    print("  OVERALL VERDICT: %s" % ('PASS' if overall else 'FAIL'))

    # H1 vs H2 summary
    print()
    if s_monitoring_frac > s_staging_frac:
        print("  H1/H2 NOTE: MONITORING (%.1f%%) > STAGING (%.1f%%) -- favors H2 'sift'" %
              (s_monitoring_frac * 100, s_staging_frac * 100))
    else:
        print("  H1/H2 NOTE: STAGING (%.1f%%) >= MONITORING (%.1f%%) -- favors H1 'sequence'" %
              (s_staging_frac * 100, s_monitoring_frac * 100))


if __name__ == '__main__':
    main()
