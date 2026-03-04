#!/usr/bin/env python3
"""
P-O6: o-family compound categories match vessel predictions

Test whether specific o-containing compounds are classified into
the categories predicted by the "vessel" decomposition.

Targets (7 major compounds):
  ok  (vessel+heat)                -> predicted: CONTAINMENT
  ot  (vessel+transfer)            -> predicted: FLOW
  ol  (vessel+state)               -> predicted: STAGING
  eo  (cool+vessel)                -> predicted: FLOW or TRANSITION
  od  (vessel+mark)                -> predicted: MARKING
  eol (cool+vessel+state)          -> predicted: THERMAL
  opch (vessel+pause+adjust+watch) -> predicted: MONITORING

Pass criterion: >= 5/7 compounds match predicted category (exact or top-2).
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


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Prediction table: compound -> list of acceptable categories (exact or top-2 match)
    PREDICTIONS = {
        'ok':   ['CONTAINMENT'],
        'ot':   ['FLOW'],
        'ol':   ['STAGING'],
        'eo':   ['FLOW', 'TRANSITION'],
        'od':   ['MARKING'],
        'eol':  ['THERMAL'],
        'opch': ['MONITORING'],
    }

    # Negative controls: non-o compounds and what they should NOT map to vessel predictions
    CONTROLS = ['ke', 'hy', 'dy', 'ed', 'in']

    # ---- Collect MIDDLE category distributions ----
    # Build map: middle_string -> category counts
    target_middles = set(PREDICTIONS.keys()) | set(CONTROLS)
    middle_cat_counts = defaultdict(lambda: defaultdict(int))
    middle_totals = defaultdict(int)

    # Also collect global baseline
    global_cat_counts = defaultdict(int)
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

        global_cat_counts[cat] += 1
        global_total += 1

        if m.middle in target_middles:
            middle_cat_counts[m.middle][cat] += 1
            middle_totals[m.middle] += 1

    print("=" * 70)
    print("P-O6: o-family compound categories match vessel predictions")
    print("=" * 70)
    print()

    # Global baseline
    print(f"Global baseline (N={global_total}):")
    for cat in CATEGORIES:
        frac = global_cat_counts[cat] / global_total * 100 if global_total > 0 else 0
        print(f"  {cat:<15} {frac:>6.2f}%")
    print()

    # ---- TEST 1-4: Category profiles for each predicted compound ----
    print("-" * 70)
    print("TEST 1: Category profiles for o-family compounds")
    print("-" * 70)
    print()

    matches = 0
    total_tested = 0

    for compound in sorted(PREDICTIONS.keys()):
        predicted_cats = PREDICTIONS[compound]
        n = middle_totals[compound]

        print(f"  Compound: {compound} (N={n})")
        print(f"  Predicted: {' or '.join(predicted_cats)}")

        if n == 0:
            print(f"  WARNING: No tokens found with MIDDLE = '{compound}'")
            print()
            continue

        total_tested += 1

        # Sort categories by count for this compound
        cat_profile = []
        for cat in CATEGORIES:
            cnt = middle_cat_counts[compound].get(cat, 0)
            frac = cnt / n * 100
            global_frac = global_cat_counts[cat] / global_total * 100 if global_total > 0 else 0
            enrich = (cnt / n) / (global_cat_counts[cat] / global_total) if global_cat_counts[cat] > 0 and global_total > 0 else 0
            cat_profile.append((cat, cnt, frac, enrich))

        cat_profile.sort(key=lambda x: -x[1])

        print(f"  {'Category':<15} {'Count':>7} {'Frac%':>8} {'Enrichment':>11}")
        print(f"  {'-'*45}")
        for cat, cnt, frac, enrich in cat_profile:
            marker = ""
            if cat in predicted_cats:
                marker = " <-- PREDICTED"
            print(f"  {cat:<15} {cnt:>7} {frac:>7.1f}% {enrich:>10.3f}x{marker}")

        # Check match: does predicted category appear in top 2?
        top2_cats = [cat_profile[0][0]]
        if len(cat_profile) > 1:
            top2_cats.append(cat_profile[1][0])

        matched = any(pc in top2_cats for pc in predicted_cats)
        if matched:
            matches += 1
            print(f"  VERDICT: MATCH (predicted category in top 2)")
        else:
            print(f"  VERDICT: MISS (top 2 = {top2_cats[0]}, {top2_cats[1] if len(top2_cats) > 1 else 'N/A'})")

        print()

    # ---- TEST 5: Negative controls ----
    print("-" * 70)
    print("TEST 5: Negative controls (non-o compounds)")
    print("-" * 70)
    print()

    # Vessel predictions that non-o compounds should NOT preferentially match
    vessel_cats = set()
    for cats in PREDICTIONS.values():
        vessel_cats.update(cats)

    control_vessel_matches = 0
    controls_tested = 0

    for compound in CONTROLS:
        n = middle_totals[compound]

        print(f"  Control: {compound} (N={n})")

        if n == 0:
            print(f"  WARNING: No tokens found with MIDDLE = '{compound}'")
            print()
            continue

        controls_tested += 1

        cat_profile = []
        for cat in CATEGORIES:
            cnt = middle_cat_counts[compound].get(cat, 0)
            frac = cnt / n * 100
            cat_profile.append((cat, cnt, frac))

        cat_profile.sort(key=lambda x: -x[1])

        print(f"  {'Category':<15} {'Count':>7} {'Frac%':>8}")
        print(f"  {'-'*35}")
        for cat, cnt, frac in cat_profile[:4]:  # show top 4
            marker = " (vessel-cat)" if cat in vessel_cats else ""
            print(f"  {cat:<15} {cnt:>7} {frac:>7.1f}%{marker}")

        # Check: is top category a vessel category?
        top_cat = cat_profile[0][0] if cat_profile else None
        if top_cat in vessel_cats:
            control_vessel_matches += 1
            print(f"  NOTE: Top category IS a vessel category (expected for some controls)")
        else:
            print(f"  OK: Top category is not vessel-specific")

        print()

    # ---- Detailed scoring ----
    print("-" * 70)
    print("SCORING DETAIL")
    print("-" * 70)
    print()

    print(f"  Predicted compounds tested: {total_tested}/7")
    print(f"  Matches (predicted in top 2): {matches}/{total_tested}")
    print(f"  Match rate: {matches/total_tested*100:.1f}%" if total_tested > 0 else "  Match rate: N/A")
    print()
    print(f"  Controls tested: {controls_tested}/5")
    print(f"  Controls with vessel-cat as top: {control_vessel_matches}/{controls_tested}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O6 o-family compound category match")
    print("=" * 70)

    pass_primary = matches >= 5
    pass_rate = matches / total_tested >= 0.71 if total_tested > 0 else False  # 5/7

    results = [
        (f">= 5/{total_tested} compounds match predicted category", pass_primary,
         f"{matches}/{total_tested}"),
        (f"Match rate >= 71%", pass_rate,
         f"{matches/total_tested*100:.1f}%" if total_tested > 0 else "N/A"),
        (f"Controls: vessel-cat NOT dominant in majority",
         control_vessel_matches <= controls_tested // 2 if controls_tested > 0 else True,
         f"{control_vessel_matches}/{controls_tested} vessel-dominant"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    print()
    print(f"  PRIMARY CRITERION (>= 5/7 matches): {'PASS' if pass_primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if pass_primary else 'FAIL'}")


if __name__ == '__main__':
    main()
