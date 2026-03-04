#!/usr/bin/env python3
"""
P-O8: ok/ot sister pair MIDDLE-level category and macro-state profiles

C936 establishes ok as vessel domain selector at PREFIX level. Test whether
ok and ot as MIDDLE compounds also show vessel-related profiles.

Tests:
1. Category profile of ok-MIDDLE tokens.
2. Category profile of ot-MIDDLE tokens.
3. Macro-state distributions for ok-MIDDLE and ot-MIDDLE.
4. Chi-square: ok vs ot category profiles differ significantly.
5. Also compute ol-MIDDLE and or-MIDDLE for o-family comparison.
6. Consistency: ok-as-MIDDLE vs ok-as-PREFIX category profiles.

Pass criterion: ok-MIDDLE CONTAINMENT+OPERATION >= 50%;
               ot-MIDDLE FLOW+TRANSITION >= 40%;
               chi-square p < 0.01.
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


def chi2_p_value(chi2_val, df):
    """Approximate p-value for chi-square using Wilson-Hilferty normal approx."""
    if chi2_val <= 0 or df <= 0:
        return 1.0
    # Wilson-Hilferty approximation
    z = ((chi2_val / df) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
    return 1.0 - normal_cdf(z)


def chi_square_test(counts_a, counts_b, categories):
    """Chi-square test comparing two category distributions."""
    n_a = sum(counts_a.get(c, 0) for c in categories)
    n_b = sum(counts_b.get(c, 0) for c in categories)
    n_total = n_a + n_b

    if n_total == 0 or n_a == 0 or n_b == 0:
        return 0.0, 1.0, 0

    chi2 = 0.0
    df = 0
    for cat in categories:
        o_a = counts_a.get(cat, 0)
        o_b = counts_b.get(cat, 0)
        row_total = o_a + o_b
        if row_total == 0:
            continue
        e_a = row_total * n_a / n_total
        e_b = row_total * n_b / n_total
        if e_a > 0:
            chi2 += (o_a - e_a) ** 2 / e_a
        if e_b > 0:
            chi2 += (o_b - e_b) ** 2 / e_b
        df += 1

    df = max(df - 1, 1)  # degrees of freedom = categories_used - 1
    p_val = chi2_p_value(chi2, df)
    return chi2, p_val, df


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    MACRO_STATES = ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']

    # Target MIDDLEs for o-family analysis
    TARGET_MIDDLES = ['ok', 'ot', 'ol', 'or']

    # ---- Collect data ----
    # middle_as_MIDDLE -> {cat_counts, macro_counts, total}
    middle_data = defaultdict(lambda: {
        'cat_counts': defaultdict(int),
        'macro_counts': defaultdict(int),
        'total': 0,
    })

    # prefix_as_PREFIX -> {cat_counts (of the MIDDLE), total}
    prefix_data = defaultdict(lambda: {
        'cat_counts': defaultdict(int),
        'total': 0,
    })

    # Global baseline
    global_cat_counts = defaultdict(int)
    global_macro_counts = defaultdict(int)
    global_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        # Macro-state
        ta = decoder.analyze_token(w)
        macro = ta.macro_state if ta and ta.macro_state else None

        global_cat_counts[cat] += 1
        if macro:
            global_macro_counts[macro] += 1
        global_total += 1

        # Track MIDDLE-level data for target MIDDLEs
        if m.middle in TARGET_MIDDLES:
            md = middle_data[m.middle]
            md['cat_counts'][cat] += 1
            if macro:
                md['macro_counts'][macro] += 1
            md['total'] += 1

        # Track PREFIX-level data for ok and ot as PREFIXes
        if m.prefix in ('ok', 'ot', 'ol', 'or'):
            pd = prefix_data[m.prefix]
            pd['cat_counts'][cat] += 1
            pd['total'] += 1

    print("=" * 70)
    print("P-O8: ok/ot sister pair MIDDLE-level profiles")
    print("=" * 70)
    print()
    print(f"Global baseline: N = {global_total}")
    print()

    # ---- Helper function to print category profile ----
    def print_cat_profile(label, cat_counts, total, highlight_cats=None):
        print(f"  {label} (N={total}):")
        if total == 0:
            print(f"    WARNING: No tokens found")
            return
        print(f"  {'Category':<15} {'Count':>7} {'Frac%':>8} {'Enrichment':>11}")
        print(f"  {'-'*45}")
        for cat in CATEGORIES:
            cnt = cat_counts.get(cat, 0)
            frac = cnt / total * 100
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = (cnt / total) / global_frac if global_frac > 0 else 0
            marker = ""
            if highlight_cats and cat in highlight_cats:
                marker = " <--"
            print(f"  {cat:<15} {cnt:>7} {frac:>7.1f}% {enrich:>10.3f}x{marker}")
        print()

    # ---- Helper function to print macro-state profile ----
    def print_macro_profile(label, macro_counts, total):
        macro_total = sum(macro_counts.values())
        print(f"  {label} macro-states (N_classified={macro_total}):")
        if macro_total == 0:
            print(f"    WARNING: No classified tokens")
            return
        print(f"  {'State':<10} {'Count':>7} {'Frac%':>8}")
        print(f"  {'-'*28}")
        for state in MACRO_STATES:
            cnt = macro_counts.get(state, 0)
            frac = cnt / macro_total * 100 if macro_total > 0 else 0
            print(f"  {state:<10} {cnt:>7} {frac:>7.1f}%")
        print()

    # ---- TEST 1: ok-MIDDLE category profile ----
    print("-" * 70)
    print("TEST 1: ok as MIDDLE — category profile")
    print("-" * 70)
    print_cat_profile("ok-MIDDLE", middle_data['ok']['cat_counts'],
                      middle_data['ok']['total'],
                      highlight_cats=['CONTAINMENT', 'OPERATION'])

    # ---- TEST 2: ot-MIDDLE category profile ----
    print("-" * 70)
    print("TEST 2: ot as MIDDLE — category profile")
    print("-" * 70)
    print_cat_profile("ot-MIDDLE", middle_data['ot']['cat_counts'],
                      middle_data['ot']['total'],
                      highlight_cats=['FLOW', 'TRANSITION'])

    # ---- TEST 3: Macro-state distributions ----
    print("-" * 70)
    print("TEST 3: Macro-state distributions for ok-MIDDLE and ot-MIDDLE")
    print("-" * 70)
    print_macro_profile("ok-MIDDLE", middle_data['ok']['macro_counts'],
                        middle_data['ok']['total'])
    print_macro_profile("ot-MIDDLE", middle_data['ot']['macro_counts'],
                        middle_data['ot']['total'])

    # ---- TEST 4: Chi-square ok vs ot category profiles ----
    print("-" * 70)
    print("TEST 4: Chi-square — ok-MIDDLE vs ot-MIDDLE category profiles")
    print("-" * 70)

    chi2_ok_ot, p_ok_ot, df_ok_ot = chi_square_test(
        middle_data['ok']['cat_counts'],
        middle_data['ot']['cat_counts'],
        CATEGORIES
    )

    print(f"  Chi-square = {chi2_ok_ot:.3f}, df = {df_ok_ot}, p = {p_ok_ot:.6f}")
    if p_ok_ot < 0.001:
        print(f"  Significance: p < 0.001 ***")
    elif p_ok_ot < 0.01:
        print(f"  Significance: p < 0.01 **")
    elif p_ok_ot < 0.05:
        print(f"  Significance: p < 0.05 *")
    else:
        print(f"  Significance: not significant")
    print()

    # ---- TEST 5: ol-MIDDLE and or-MIDDLE profiles for o-family comparison ----
    print("-" * 70)
    print("TEST 5: Additional o-family — ol and or as MIDDLEs")
    print("-" * 70)
    print_cat_profile("ol-MIDDLE", middle_data['ol']['cat_counts'],
                      middle_data['ol']['total'],
                      highlight_cats=['STAGING'])
    print_cat_profile("or-MIDDLE", middle_data['or']['cat_counts'],
                      middle_data['or']['total'])

    # ---- TEST 6: Consistency — ok-as-MIDDLE vs ok-as-PREFIX ----
    print("-" * 70)
    print("TEST 6: Consistency — ok as MIDDLE vs ok as PREFIX")
    print("-" * 70)

    print_cat_profile("ok-as-PREFIX (classifying their MIDDLEs)",
                      prefix_data['ok']['cat_counts'],
                      prefix_data['ok']['total'])
    print_cat_profile("ok-as-MIDDLE",
                      middle_data['ok']['cat_counts'],
                      middle_data['ok']['total'])

    # Compute cosine similarity between the two profiles
    ok_mid_vec = [middle_data['ok']['cat_counts'].get(c, 0) for c in CATEGORIES]
    ok_pfx_vec = [prefix_data['ok']['cat_counts'].get(c, 0) for c in CATEGORIES]

    dot = sum(a * b for a, b in zip(ok_mid_vec, ok_pfx_vec))
    mag_a = math.sqrt(sum(a * a for a in ok_mid_vec))
    mag_b = math.sqrt(sum(b * b for b in ok_pfx_vec))
    cosine = dot / (mag_a * mag_b) if mag_a > 0 and mag_b > 0 else 0

    print(f"  Cosine similarity (ok-MIDDLE vs ok-PREFIX): {cosine:.4f}")
    print()

    # Also show ot comparison
    print_cat_profile("ot-as-PREFIX (classifying their MIDDLEs)",
                      prefix_data['ot']['cat_counts'],
                      prefix_data['ot']['total'])

    ot_mid_vec = [middle_data['ot']['cat_counts'].get(c, 0) for c in CATEGORIES]
    ot_pfx_vec = [prefix_data['ot']['cat_counts'].get(c, 0) for c in CATEGORIES]

    dot_ot = sum(a * b for a, b in zip(ot_mid_vec, ot_pfx_vec))
    mag_ot_a = math.sqrt(sum(a * a for a in ot_mid_vec))
    mag_ot_b = math.sqrt(sum(b * b for b in ot_pfx_vec))
    cosine_ot = dot_ot / (mag_ot_a * mag_ot_b) if mag_ot_a > 0 and mag_ot_b > 0 else 0

    print(f"  Cosine similarity (ot-MIDDLE vs ot-PREFIX): {cosine_ot:.4f}")
    print()

    # ---- SUMMARY ----
    print("=" * 70)
    print("SUMMARY: P-O8 ok/ot MIDDLE-level profiles")
    print("=" * 70)

    # ok-MIDDLE CONTAINMENT + OPERATION >= 50%
    ok_total = middle_data['ok']['total']
    ok_cont_op = 0
    if ok_total > 0:
        ok_cont = middle_data['ok']['cat_counts'].get('CONTAINMENT', 0)
        ok_op = middle_data['ok']['cat_counts'].get('OPERATION', 0)
        ok_cont_op = (ok_cont + ok_op) / ok_total * 100

    # ot-MIDDLE FLOW + TRANSITION >= 40%
    ot_total = middle_data['ot']['total']
    ot_flow_trans = 0
    if ot_total > 0:
        ot_flow = middle_data['ot']['cat_counts'].get('FLOW', 0)
        ot_trans = middle_data['ot']['cat_counts'].get('TRANSITION', 0)
        ot_flow_trans = (ot_flow + ot_trans) / ot_total * 100

    pass_ok = ok_cont_op >= 50
    pass_ot = ot_flow_trans >= 40
    pass_chi2 = p_ok_ot < 0.01
    pass_consistency = cosine >= 0.70

    results = [
        ("ok-MIDDLE CONTAINMENT+OPERATION >= 50%", pass_ok,
         f"{ok_cont_op:.1f}%"),
        ("ot-MIDDLE FLOW+TRANSITION >= 40%", pass_ot,
         f"{ot_flow_trans:.1f}%"),
        ("Chi-square ok vs ot: p < 0.01", pass_chi2,
         f"chi2={chi2_ok_ot:.2f}, p={p_ok_ot:.6f}"),
        ("ok MIDDLE/PREFIX consistency (cosine >= 0.70)", pass_consistency,
         f"cosine = {cosine:.4f}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_ok and pass_ot and pass_chi2
    print()
    print(f"  PRIMARY CRITERION (ok>=50% AND ot>=40% AND chi2 p<0.01): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
