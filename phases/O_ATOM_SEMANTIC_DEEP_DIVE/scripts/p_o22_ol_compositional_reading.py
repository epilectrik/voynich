#!/usr/bin/env python3
"""
P-O22: ol = LINK operator compositional reading (arrange + state)

C874 establishes ol as the LINK operator (monitoring/intervention boundary).
If o = "ordnen" (arrange) and l = "state/condition", then ol = "arrange the state"
= preparation for state transition. This predicts:

1. ol should be enriched in STAGING and/or TRANSITION (preparing state changes)
2. ol should have HIGHER STAGING+TRANSITION fraction than ok, ot, or (other o-compounds)
3. ol should lean STAGING while kl (heat+state) leans THERMAL
4. ol should appear mid-line or late (linking prior work to next phase)
5. ol at paragraph-internal positions (boundary between body sections)

Pass criterion: ol STAGING+TRANSITION >= 25% AND ol highest ST+TR among o-compounds
               AND ol STAGING enrichment > al (major l-compound)
Note: kl and el have only 2-3 tokens — comparison uses al (521 tokens) as
the meaningful l-compound control. If l itself drives STAGING, all l-compounds
should be equal; if o contributes, ol should be HIGHER than al.
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


def get_category_profile(cat_counts, total):
    """Return dict of category -> fraction."""
    if total == 0:
        return {}
    return {cat: cnt / total for cat, cnt in cat_counts.items()}


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Target MIDDLEs: ol, ok, ot, or (o-compounds), kl, el, al (l-compounds)
    TARGET_MIDDLES = ['ol', 'ok', 'ot', 'or', 'kl', 'el', 'al']

    # Collect category profiles for each target MIDDLE
    middle_cat_counts = defaultdict(lambda: defaultdict(int))
    middle_totals = defaultdict(int)
    global_cat_counts = defaultdict(int)
    global_total = 0

    # Position data for ol
    ol_positions = []  # normalized [0, 1] within line
    ol_line_positions = {'initial': 0, 'medial': 0, 'final': 0}
    ol_par_positions = {'par_initial': 0, 'par_interior': 0, 'par_final': 0}

    # Track line lengths for normalization
    line_token_counts = defaultdict(int)
    line_token_positions = defaultdict(list)  # line_key -> [(pos, middle)]

    # First pass: count tokens per line
    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        line_key = (token.folio, token.line)
        line_token_counts[line_key] += 1

    # Second pass: collect data
    line_pos_counters = defaultdict(int)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        mid = m.middle
        cat = cc.classify(mid)

        line_key = (token.folio, token.line)
        pos_idx = line_pos_counters[line_key]
        line_pos_counters[line_key] += 1
        line_len = line_token_counts[line_key]

        if cat is not None:
            global_cat_counts[cat] += 1
            global_total += 1

            if mid in TARGET_MIDDLES:
                middle_cat_counts[mid][cat] += 1
                middle_totals[mid] += 1

        # Position tracking for ol
        if mid == 'ol':
            if line_len > 1:
                norm_pos = pos_idx / (line_len - 1)
            else:
                norm_pos = 0.5
            ol_positions.append(norm_pos)

            if token.line_initial:
                ol_line_positions['initial'] += 1
            elif token.line_final:
                ol_line_positions['final'] += 1
            else:
                ol_line_positions['medial'] += 1

            if token.par_initial:
                ol_par_positions['par_initial'] += 1
            elif token.par_final:
                ol_par_positions['par_final'] += 1
            else:
                ol_par_positions['par_interior'] += 1

    print("=" * 70)
    print("P-O22: ol compositional reading — arrange + state (ordnen)")
    print("=" * 70)
    print()

    # Global baselines
    print(f"Global classified tokens: {global_total}")
    print(f"Global baselines:")
    for cat in CATEGORIES:
        frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
        print(f"  {cat:<15} {frac*100:>6.2f}%")
    print()

    global_staging_rate = global_cat_counts['STAGING'] / global_total if global_total > 0 else 0
    global_transition_rate = global_cat_counts['TRANSITION'] / global_total if global_total > 0 else 0
    global_thermal_rate = global_cat_counts['THERMAL'] / global_total if global_total > 0 else 0
    global_st_rate = global_staging_rate + global_transition_rate

    # ---- TEST 1: ol full category profile ----
    print("-" * 70)
    print("TEST 1: ol (LINK operator) category profile")
    print("-" * 70)
    print()

    ol_total = middle_totals['ol']
    ol_staging_frac = 0.0
    ol_transition_frac = 0.0
    ol_thermal_frac = 0.0
    ol_st_frac = 0.0

    if ol_total > 0:
        print(f"  ol total classified tokens: {ol_total}")
        print()
        print(f"  {'Category':<15} {'ol fraction':>12} {'Global':>9} {'Enrichment':>11} {'Count':>7}")
        print(f"  {'-'*58}")
        for cat in CATEGORIES:
            ol_n = middle_cat_counts['ol'].get(cat, 0)
            ol_frac = ol_n / ol_total
            g_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = ol_frac / g_frac if g_frac > 0 else 0
            marker = ""
            if cat == 'STAGING':
                marker = " <-- PREDICTED ENRICHED"
                ol_staging_frac = ol_frac
            elif cat == 'TRANSITION':
                marker = " <-- PREDICTED ENRICHED"
                ol_transition_frac = ol_frac
            elif cat == 'THERMAL':
                ol_thermal_frac = ol_frac
            print(f"  {cat:<13} {ol_frac*100:>11.2f}% {g_frac*100:>8.2f}% {enrich:>10.3f}x {ol_n:>7}{marker}")

        ol_st_frac = ol_staging_frac + ol_transition_frac
        print()
        print(f"  ol STAGING + TRANSITION combined: {ol_st_frac*100:.2f}%")
        ol_staging_enrich = ol_staging_frac / global_staging_rate if global_staging_rate > 0 else 0
        print(f"  ol STAGING enrichment: {ol_staging_enrich:.3f}x")
    else:
        print("  WARNING: ol has no classified tokens")

    # ---- TEST 2: Compare ol to other o-compounds (ok, ot, or) ----
    print()
    print("-" * 70)
    print("TEST 2: ol vs other o-compounds (STAGING+TRANSITION fraction)")
    print("-" * 70)
    print()

    o_compounds = ['ol', 'ok', 'ot', 'or']
    o_compound_st = {}

    print(f"  {'MIDDLE':<8} {'STAGING%':>10} {'TRANSIT%':>10} {'ST+TR%':>10} {'THERMAL%':>10} {'Total':>7}")
    print(f"  {'-'*58}")

    for mid in o_compounds:
        total = middle_totals[mid]
        if total == 0:
            print(f"  {mid:<8} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {0:>7}")
            continue
        stg = middle_cat_counts[mid].get('STAGING', 0) / total
        trn = middle_cat_counts[mid].get('TRANSITION', 0) / total
        thm = middle_cat_counts[mid].get('THERMAL', 0) / total
        st_combined = stg + trn
        o_compound_st[mid] = st_combined
        marker = " <-- LINK" if mid == 'ol' else ""
        print(f"  {mid:<8} {stg*100:>9.2f}% {trn*100:>9.2f}% {st_combined*100:>9.2f}% {thm*100:>9.2f}% {total:>7}{marker}")

    ol_st_highest = True
    for mid in ['ok', 'ot', 'or']:
        if mid in o_compound_st and o_compound_st.get('ol', 0) <= o_compound_st[mid]:
            ol_st_highest = False

    print()
    print(f"  ol has highest STAGING+TRANSITION among o-compounds: {'YES' if ol_st_highest else 'NO'}")

    # ---- TEST 3: Compare ol to kl, el, al (l-compounds) ----
    print()
    print("-" * 70)
    print("TEST 3: ol vs other l-compounds (STAGING vs THERMAL distinction)")
    print("-" * 70)
    print()

    l_compounds = ['ol', 'kl', 'el', 'al']

    print(f"  {'MIDDLE':<8} {'STAGING%':>10} {'THERMAL%':>10} {'STAGING enrich':>15} {'Total':>7}")
    print(f"  {'-'*55}")

    l_compound_staging_enrich = {}
    for mid in l_compounds:
        total = middle_totals[mid]
        if total == 0:
            print(f"  {mid:<8} {'N/A':>10} {'N/A':>10} {'N/A':>15} {0:>7}")
            continue
        stg = middle_cat_counts[mid].get('STAGING', 0) / total
        thm = middle_cat_counts[mid].get('THERMAL', 0) / total
        stg_enrich = stg / global_staging_rate if global_staging_rate > 0 else 0
        l_compound_staging_enrich[mid] = stg_enrich
        marker = ""
        if mid == 'ol':
            marker = " <-- PREDICTED STAGING"
        elif mid == 'kl':
            marker = " <-- PREDICTED THERMAL"
        print(f"  {mid:<8} {stg*100:>9.2f}% {thm*100:>9.2f}% {stg_enrich:>14.3f}x {total:>7}{marker}")

    ol_more_staging_than_kl = l_compound_staging_enrich.get('ol', 0) > l_compound_staging_enrich.get('kl', 0)
    ol_more_staging_than_el = l_compound_staging_enrich.get('ol', 0) > l_compound_staging_enrich.get('el', 0)
    ol_more_staging_than_al = l_compound_staging_enrich.get('ol', 0) > l_compound_staging_enrich.get('al', 0)
    print()
    print(f"  ol STAGING enrichment > kl: {'YES' if ol_more_staging_than_kl else 'NO'} (N={middle_totals.get('kl', 0)} — may be too small)")
    print(f"  ol STAGING enrichment > el: {'YES' if ol_more_staging_than_el else 'NO'} (N={middle_totals.get('el', 0)} — may be too small)")
    print(f"  ol STAGING enrichment > al: {'YES' if ol_more_staging_than_al else 'NO'} (N={middle_totals.get('al', 0)} — primary l-compound control)")

    # ---- TEST 4: ol positional profile ----
    print()
    print("-" * 70)
    print("TEST 4: ol line-position profile")
    print("-" * 70)
    print()

    ol_pos_total = ol_line_positions['initial'] + ol_line_positions['medial'] + ol_line_positions['final']
    if ol_pos_total > 0:
        for pos_type in ['initial', 'medial', 'final']:
            n = ol_line_positions[pos_type]
            frac = n / ol_pos_total
            print(f"  {pos_type:<10}: {n:>6} ({frac*100:.1f}%)")

        # Mean normalized position
        if ol_positions:
            mean_pos = sum(ol_positions) / len(ol_positions)
            print(f"\n  Mean normalized position: {mean_pos:.3f}")
            print(f"  (0.0 = line start, 1.0 = line end)")
            print(f"  Prediction: mid-line or late (> 0.40)")
        else:
            mean_pos = 0.5

    print()
    print(f"  Paragraph position:")
    par_total = sum(ol_par_positions.values())
    if par_total > 0:
        for pos_type in ['par_initial', 'par_interior', 'par_final']:
            n = ol_par_positions[pos_type]
            frac = n / par_total
            print(f"  {pos_type:<15}: {n:>6} ({frac*100:.1f}%)")

    # ---- TEST 5: Chi-square — ol STAGING enrichment significance ----
    print()
    print("-" * 70)
    print("TEST 5: Chi-square — ol STAGING enrichment vs global")
    print("-" * 70)
    print()

    chi2_p = 1.0
    if ol_total > 0 and global_total > 0:
        ol_stg_n = middle_cat_counts['ol'].get('STAGING', 0)
        a = ol_stg_n
        b = ol_total - ol_stg_n
        c = global_cat_counts['STAGING'] - ol_stg_n
        d = (global_total - ol_total) - c
        total_table = a + b + c + d

        if total_table > 0:
            exp_a = (a + b) * (a + c) / total_table
            exp_b = (a + b) * (b + d) / total_table
            exp_c = (c + d) * (a + c) / total_table
            exp_d = (c + d) * (b + d) / total_table

            chi2 = 0
            for obs, exp in [(a, exp_a), (b, exp_b), (c, exp_c), (d, exp_d)]:
                if exp > 0:
                    chi2 += (obs - exp) ** 2 / exp

            chi2_p = chi2_1df_p(chi2)

            print(f"  ol STAGING: {a}/{ol_total} = {ol_staging_frac*100:.2f}%")
            print(f"  Global STAGING: {global_cat_counts['STAGING']}/{global_total} = {global_staging_rate*100:.2f}%")
            print(f"  Chi-square: {chi2:.3f}, p = {chi2_p:.6f}")
            if chi2_p < 0.001:
                print(f"  Significance: p < 0.001 ***")
            elif chi2_p < 0.01:
                print(f"  Significance: p < 0.01 **")
            elif chi2_p < 0.05:
                print(f"  Significance: p < 0.05 *")
            else:
                print(f"  Significance: not significant")

    # ---- TEST 6: Full profile comparison across all target MIDDLEs ----
    print()
    print("-" * 70)
    print("TEST 6: Full profile comparison — all target MIDDLEs")
    print("-" * 70)
    print()

    all_targets = ['ol', 'ok', 'ot', 'or', 'kl', 'el', 'al']
    header = f"  {'MIDDLE':<8}"
    for cat in CATEGORIES:
        header += f" {cc.abbrev(cat):>5}"
    header += f" {'Total':>7}"
    print(header)
    print(f"  {'-'*(8 + 6*len(CATEGORIES) + 8)}")

    for mid in all_targets:
        total = middle_totals[mid]
        if total == 0:
            continue
        row = f"  {mid:<8}"
        for cat in CATEGORIES:
            n = middle_cat_counts[mid].get(cat, 0)
            frac = n / total * 100
            row += f" {frac:>4.1f}%"
        row += f" {total:>7}"
        if mid == 'ol':
            row += " <-- LINK"
        print(row)

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O22 ol compositional reading (ordnen + state)")
    print("=" * 70)

    pass_st_frac = ol_st_frac >= 0.25
    pass_ol_highest_o = ol_st_highest
    pass_staging_gt_al = ol_more_staging_than_al
    pass_chi2 = chi2_p < 0.05
    mean_pos_val = sum(ol_positions) / len(ol_positions) if ol_positions else 0.5
    pass_position = mean_pos_val >= 0.40
    # Note: kl (N=2) and el (N=3) are too small for meaningful comparison.
    # al (N=521) is the real l-compound control — it shows whether ol's STAGING
    # enrichment comes from the 'o' atom or purely from 'l'.
    pass_interior = ol_par_positions['par_interior'] / par_total > 0.90 if par_total > 0 else False

    results = [
        ("ol STAGING+TRANSITION >= 25%", pass_st_frac,
         f"{ol_st_frac*100:.2f}%"),
        ("ol highest ST+TR among o-compounds", pass_ol_highest_o,
         f"ol={o_compound_st.get('ol', 0)*100:.1f}% vs others"),
        ("ol STAGING enrichment > al (l-compound control)", pass_staging_gt_al,
         f"ol={l_compound_staging_enrich.get('ol', 0):.3f}x vs al={l_compound_staging_enrich.get('al', 0):.3f}x"),
        ("STAGING chi-square p < 0.05", pass_chi2,
         f"p = {chi2_p:.6f}"),
        ("Mean position >= 0.40 (mid-late)", pass_position,
         f"pos = {mean_pos_val:.3f}"),
        ("Paragraph-interior > 90%", pass_interior,
         f"{ol_par_positions['par_interior']}/{par_total} = {ol_par_positions['par_interior']/par_total*100:.1f}%" if par_total > 0 else "N/A"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_st_frac and pass_ol_highest_o and pass_staging_gt_al
    print()
    print(f"  PRIMARY CRITERION (ST+TR>=25% AND highest o-compound AND > al): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
