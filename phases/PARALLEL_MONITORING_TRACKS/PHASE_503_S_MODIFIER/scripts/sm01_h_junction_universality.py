#!/usr/bin/env python3
"""
SM-1: h-junction universality test

Question: Does adding 'sh' to ANY atom X always produce MONITORING?

For each Xsh compound MIDDLE (where X is a single atom: k, l, o, t, p, e, d, r, f),
compute the 8-category profile. If MONITORING is the primary (highest %) category
for >= 4/5 testable compounds, the h-junction is universal.

Testable (N >= 5): ksh(26), lsh(24), osh(13), tsh(9), psh(5)
Control: standalone sh(109)

Pass: >= 4/5 Xsh compounds have MONITORING as primary category.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Single atoms to test as X in Xsh
TEST_ATOMS = ['k', 'l', 'o', 't', 'p', 'e', 'd', 'r', 'f']
MIN_N = 5


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect category counts per MIDDLE
    middle_cats = defaultdict(lambda: defaultdict(int))
    middle_totals = defaultdict(int)

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

        middle_cats[m.middle][cat] += 1
        middle_totals[m.middle] += 1

    print("=" * 75)
    print("SM-1: h-junction universality -- Does Xsh always produce MONITORING?")
    print("=" * 75)
    print()

    # ---- Control: standalone sh ----
    print("-" * 75)
    print("CONTROL: standalone sh")
    print("-" * 75)
    print()

    sh_total = middle_totals.get('sh', 0)
    if sh_total > 0:
        print(f"  sh (N={sh_total}):")
        cats_sorted = sorted(middle_cats['sh'].items(), key=lambda x: -x[1])
        primary = cats_sorted[0][0]
        for cat in CATEGORIES:
            n = middle_cats['sh'].get(cat, 0)
            pct = n / sh_total * 100
            marker = " <-- PRIMARY" if cat == primary else ""
            print(f"    {cat:<15} {n:>5} ({pct:>5.1f}%){marker}")
        print(f"  Primary category: {primary}")
    else:
        print("  sh: NOT FOUND in corpus")
    print()

    # ---- Test Xsh compounds ----
    print("-" * 75)
    print("TEST: Xsh compound category profiles (N >= %d)" % MIN_N)
    print("-" * 75)
    print()

    tested = 0
    monitoring_primary = 0
    skipped = []
    results = []

    for atom in TEST_ATOMS:
        compound = atom + 'sh'
        total = middle_totals.get(compound, 0)

        if total < MIN_N:
            skipped.append((compound, total))
            continue

        tested += 1

        cats_sorted = sorted(middle_cats[compound].items(), key=lambda x: -x[1])
        primary = cats_sorted[0][0] if cats_sorted else 'N/A'
        is_mon = primary == 'MONITORING'

        if is_mon:
            monitoring_primary += 1

        verdict = "MONITORING PRIMARY" if is_mon else f"PRIMARY={primary}"
        results.append((compound, total, primary, is_mon))

        print(f"  {compound} (N={total}):  --> {verdict}")
        for cat in CATEGORIES:
            n = middle_cats[compound].get(cat, 0)
            pct = n / total * 100
            marker = " <-- PRIMARY" if cat == primary else ""
            print(f"    {cat:<15} {n:>5} ({pct:>5.1f}%){marker}")
        print()

    # ---- Skipped (insufficient data) ----
    if skipped:
        print("-" * 75)
        print("SKIPPED (N < %d)" % MIN_N)
        print("-" * 75)
        print()
        for compound, total in skipped:
            print(f"  {compound}: N={total}")
        print()

    # ---- Summary comparison table ----
    print("-" * 75)
    print("COMPARISON TABLE: Primary category for each Xsh")
    print("-" * 75)
    print()

    header = f"{'Compound':<12} {'N':>5} {'Primary':<15} {'MON%':>7} {'2nd Cat':<15} {'2nd%':>7} {'MON?':>6}"
    print(header)
    print("-" * len(header))

    # Include sh control
    if sh_total > 0:
        cs = sorted(middle_cats['sh'].items(), key=lambda x: -x[1])
        p1 = cs[0] if cs else ('N/A', 0)
        p2 = cs[1] if len(cs) > 1 else ('N/A', 0)
        mon_pct = middle_cats['sh'].get('MONITORING', 0) / sh_total * 100
        is_mon = p1[0] == 'MONITORING'
        print(f"  {'sh (ctrl)':<10} {sh_total:>5} {p1[0]:<15} {mon_pct:>6.1f}% {p2[0]:<15} {p2[1]/sh_total*100:>6.1f}% {'YES' if is_mon else 'NO':>6}")

    for compound, total, primary, is_mon in results:
        cs = sorted(middle_cats[compound].items(), key=lambda x: -x[1])
        p2 = cs[1] if len(cs) > 1 else ('N/A', 0)
        mon_pct = middle_cats[compound].get('MONITORING', 0) / total * 100
        print(f"  {compound:<10} {total:>5} {primary:<15} {mon_pct:>6.1f}% {p2[0]:<15} {p2[1]/total*100:>6.1f}% {'YES' if is_mon else 'NO':>6}")

    # ---- VERDICT ----
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    if tested == 0:
        print("  No Xsh compounds had N >= %d -- CANNOT EVALUATE" % MIN_N)
        overall = False
    else:
        threshold = min(4, tested)  # require 4/5 or all if fewer than 5 tested
        overall = monitoring_primary >= threshold
        print(f"  Tested: {tested} Xsh compounds with N >= {MIN_N}")
        print(f"  MONITORING as primary: {monitoring_primary}/{tested}")
        print(f"  Threshold: >= {threshold}/{tested}")
        print()
        print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
        if overall:
            print("  h-junction (Xsh) universally produces MONITORING regardless of X atom")
        else:
            print("  h-junction does NOT universally produce MONITORING")
            # Show which failed
            for compound, total, primary, is_mon in results:
                if not is_mon:
                    print(f"    EXCEPTION: {compound} -> {primary}")


if __name__ == '__main__':
    main()
