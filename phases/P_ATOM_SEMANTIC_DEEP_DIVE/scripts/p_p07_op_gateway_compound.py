#!/usr/bin/env python3
"""
P-P7: op gateway compound verification

Test op compound's dual identity: gateway position + TRANSITION category.

C1060 says op is 20/24 INITIAL in compound MIDDLEs (83%).
The gloss is "start" (o=arrange + p=pause).

Method:
1. Find all compound MIDDLEs (length >= 3) that START with "op"
2. Count: what fraction of op-containing compound MIDDLEs have op at INITIAL?
3. For all tokens with MIDDLE = "op" (standalone), classify category
4. For all tokens with MIDDLE starting with "op" (compound), classify category
5. Check folio coverage: how many distinct folios contain op tokens?
6. Compare to frequency-matched controls

Also: ep (e+p) for comparison -- does p+X preserve first atom's category?

Predictions:
- op at INITIAL position >= 75% in compound MIDDLEs
- op standalone majority category = TRANSITION
- op-initial compound majority category consistent
- op folio span >= 25 folios

Pass: INITIAL >= 75% AND TRANSITION is majority category for op standalone
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("P-P7: op gateway compound verification")
    print("=" * 75)

    # ---- PASS 1: Collect all MIDDLEs containing "op" ----
    # Categories:
    #   op_standalone: MIDDLE == "op"
    #   op_initial:    MIDDLE starts with "op" and len >= 3
    #   op_medial:     MIDDLE contains "op" not at start/end, len >= 4
    #   op_terminal:   MIDDLE ends with "op" and len >= 3

    op_standalone_cats = Counter()
    op_initial_cats = Counter()
    op_medial_cats = Counter()
    op_terminal_cats = Counter()
    op_other_cats = Counter()  # contains "op" somewhere

    op_standalone_folios = set()
    op_initial_folios = set()
    op_all_folios = set()

    # Track MIDDLEs for detail
    op_initial_middles = Counter()
    op_terminal_middles = Counter()

    # ep comparison
    ep_standalone_cats = Counter()
    ep_initial_cats = Counter()
    ep_standalone_total = 0
    ep_initial_total = 0
    ep_initial_middles = Counter()

    # Global baseline
    global_cats = Counter()
    global_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        mid = m.middle
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        global_cats[cat] += 1
        global_total += 1

        # op analysis
        if mid == 'op':
            op_standalone_cats[cat] += 1
            op_standalone_folios.add(token.folio)
            op_all_folios.add(token.folio)
        elif 'op' in mid and len(mid) >= 3:
            op_all_folios.add(token.folio)

            if mid[:2] == 'op':
                op_initial_cats[cat] += 1
                op_initial_folios.add(token.folio)
                op_initial_middles[mid] += 1
            elif mid[-2:] == 'op':
                op_terminal_cats[cat] += 1
                op_terminal_middles[mid] += 1
            else:
                op_medial_cats[cat] += 1

        # ep comparison
        if mid == 'ep':
            ep_standalone_cats[cat] += 1
            ep_standalone_total += 1
        elif 'ep' in mid and len(mid) >= 3 and mid[:2] == 'ep':
            ep_initial_cats[cat] += 1
            ep_initial_total += 1
            ep_initial_middles[mid] += 1

    op_standalone_total = sum(op_standalone_cats.values())
    op_initial_total = sum(op_initial_cats.values())
    op_terminal_total = sum(op_terminal_cats.values())
    op_medial_total = sum(op_medial_cats.values())

    # ---- TEST 1: op positional distribution in compounds ----
    print()
    print("-" * 75)
    print("TEST 1: op positional distribution in compound MIDDLEs")
    print("-" * 75)
    print()

    # Count unique compound MIDDLEs containing "op"
    op_containing_total = op_initial_total + op_terminal_total + op_medial_total
    op_initial_frac = op_initial_total / op_containing_total if op_containing_total > 0 else 0

    print(f"op in compound MIDDLEs (len >= 3):")
    print(f"  INITIAL (starts with 'op'): {op_initial_total} tokens ({op_initial_frac*100:.1f}%)")
    print(f"  TERMINAL (ends with 'op'):  {op_terminal_total} tokens")
    print(f"  MEDIAL (interior):          {op_medial_total} tokens")
    print(f"  Total compound op:          {op_containing_total}")
    print(f"  Standalone 'op':            {op_standalone_total}")
    print()
    print(f"  Prediction: INITIAL >= 75% -- {'PASS' if op_initial_frac >= 0.75 else 'FAIL'}")

    # ---- TEST 2: op standalone category ----
    print()
    print("-" * 75)
    print("TEST 2: op standalone category profile")
    print("-" * 75)
    print()

    print(f"op standalone (N={op_standalone_total}):")
    print(f"{'Category':<15} {'Count':>6} {'Frac%':>8} {'Global%':>9} {'Enrich':>8}")
    print("-" * 52)

    op_standalone_primary = None
    op_standalone_max = 0
    for cat in CATEGORIES:
        n = op_standalone_cats.get(cat, 0)
        frac = n / op_standalone_total if op_standalone_total > 0 else 0
        g_frac = global_cats[cat] / global_total if global_total > 0 else 0
        enrich = frac / g_frac if g_frac > 0 else 0
        marker = "  <-- primary" if n > op_standalone_max else ""
        if n > op_standalone_max:
            op_standalone_max = n
            op_standalone_primary = cat
        print(f"  {cat:<13} {n:>6} {frac*100:>7.1f}% {g_frac*100:>8.1f}% {enrich:>7.2f}x{marker}")

    print()
    print(f"  Majority category: {op_standalone_primary}")
    print(f"  Prediction: TRANSITION -- {'PASS' if op_standalone_primary == 'TRANSITION' else 'FAIL'}")

    # ---- TEST 3: op-initial compound category ----
    print()
    print("-" * 75)
    print("TEST 3: op-initial compound category profile")
    print("-" * 75)
    print()

    print(f"op-initial compounds (N={op_initial_total}):")
    print(f"{'Category':<15} {'Count':>6} {'Frac%':>8} {'Global%':>9} {'Enrich':>8}")
    print("-" * 52)

    op_initial_primary = None
    op_initial_max = 0
    for cat in CATEGORIES:
        n = op_initial_cats.get(cat, 0)
        frac = n / op_initial_total if op_initial_total > 0 else 0
        g_frac = global_cats[cat] / global_total if global_total > 0 else 0
        enrich = frac / g_frac if g_frac > 0 else 0
        if n > op_initial_max:
            op_initial_max = n
            op_initial_primary = cat
        print(f"  {cat:<13} {n:>6} {frac*100:>7.1f}% {g_frac*100:>8.1f}% {enrich:>7.2f}x")

    print()
    print(f"  Majority category: {op_initial_primary}")

    # Per-MIDDLE detail
    print()
    print(f"  op-initial compound MIDDLEs:")
    print(f"  {'MIDDLE':<15} {'Count':>6} {'Category':<15}")
    print("  " + "-" * 40)
    for mid, count in sorted(op_initial_middles.items(), key=lambda x: -x[1])[:15]:
        cat = cc.classify(mid)
        print(f"  {mid:<15} {count:>6} {cat}")

    # ---- TEST 4: Folio coverage ----
    print()
    print("-" * 75)
    print("TEST 4: Folio coverage")
    print("-" * 75)
    print()

    print(f"op standalone folios:   {len(op_standalone_folios)}")
    print(f"op initial folios:      {len(op_initial_folios)}")
    print(f"All op-containing:      {len(op_all_folios)}")
    print(f"  Prediction: >= 25 -- {'PASS' if len(op_all_folios) >= 25 else 'FAIL'}")

    # ---- TEST 5: ep comparison ----
    print()
    print("-" * 75)
    print("TEST 5: ep comparison (e+p compound)")
    print("-" * 75)
    print()

    ep_standalone_total = sum(ep_standalone_cats.values())
    ep_initial_total = sum(ep_initial_cats.values())

    print(f"ep standalone (N={ep_standalone_total}):")
    if ep_standalone_total > 0:
        ep_primary = ep_standalone_cats.most_common(1)[0][0]
        for cat in CATEGORIES:
            n = ep_standalone_cats.get(cat, 0)
            frac = n / ep_standalone_total if ep_standalone_total > 0 else 0
            if n > 0:
                print(f"  {cat:<15} {n:>5} ({frac*100:.1f}%)")
        print(f"  Majority: {ep_primary}")
    else:
        print("  (No standalone ep tokens)")

    print()
    print(f"ep-initial compounds (N={ep_initial_total}):")
    if ep_initial_total > 0:
        ep_init_primary = ep_initial_cats.most_common(1)[0][0]
        for cat in CATEGORIES:
            n = ep_initial_cats.get(cat, 0)
            frac = n / ep_initial_total if ep_initial_total > 0 else 0
            if n > 0:
                print(f"  {cat:<15} {n:>5} ({frac*100:.1f}%)")
        print(f"  Majority: {ep_init_primary}")

        print()
        print(f"  ep-initial MIDDLEs:")
        for mid, count in sorted(ep_initial_middles.items(), key=lambda x: -x[1])[:10]:
            cat = cc.classify(mid)
            print(f"    {mid:<15} {count:>5} {cat}")
    else:
        print("  (No ep-initial compound tokens)")

    print()
    print("  Category preservation analysis:")
    print("    op standalone -> TRANSITION;  ep standalone -> ?")
    print("    If p+X preserves first atom's category influence,")
    print("    then op compounds lean TRANSITION and ep compounds lean THERMAL/MARKING")

    # ---- TEST 6: Frequency-matched controls ----
    print()
    print("-" * 75)
    print("TEST 6: Frequency-matched controls")
    print("-" * 75)
    print()

    # Find 2-char MIDDLEs with similar standalone frequency to op
    all_2char_stats = {}
    middle_cat_counts = defaultdict(Counter)
    middle_totals = Counter()

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle:
            continue
        mid = m.middle
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue
        if len(mid) == 2:
            middle_cat_counts[mid][cat] += 1
            middle_totals[mid] += 1

    # Show 2-char MIDDLEs near op's frequency
    op_freq = middle_totals.get('op', 0)
    print(f"op standalone frequency: {op_freq}")
    print()

    candidates = sorted(middle_totals.items(), key=lambda x: abs(x[1] - op_freq))[:8]
    print(f"{'MIDDLE':<8} {'Count':>6} {'Primary':<15} {'2nd Cat':<15}")
    print("-" * 50)
    for mid, count in candidates:
        cats = middle_cat_counts[mid]
        top2 = cats.most_common(2)
        primary = top2[0][0] if top2 else 'N/A'
        second = top2[1][0] if len(top2) > 1 else 'N/A'
        marker = " <-- TARGET" if mid == 'op' else ""
        print(f"  {mid:<6} {count:>6} {primary:<15} {second:<15}{marker}")

    # ---- op-terminal MIDDLEs ----
    if op_terminal_total > 0:
        print()
        print("-" * 75)
        print("BONUS: op-terminal compound MIDDLEs")
        print("-" * 75)
        print()
        print(f"  {'MIDDLE':<15} {'Count':>6} {'Category':<15}")
        print("  " + "-" * 40)
        for mid, count in sorted(op_terminal_middles.items(), key=lambda x: -x[1])[:10]:
            cat = cc.classify(mid)
            print(f"  {mid:<15} {count:>6} {cat}")

    # ---- SUMMARY ----
    print()
    print("=" * 75)
    print("SUMMARY: P-P7 op gateway compound verification")
    print("=" * 75)
    print()

    p1 = op_initial_frac >= 0.75
    p2 = op_standalone_primary == 'TRANSITION'
    p3 = len(op_all_folios) >= 25

    # Category consistency check
    p4 = op_initial_primary == op_standalone_primary if op_initial_total > 0 else False

    results = [
        ("P1: op INITIAL in compounds >= 75%",
         p1,
         f"{op_initial_frac*100:.1f}% ({op_initial_total}/{op_containing_total})"),
        ("P2: op standalone majority = TRANSITION",
         p2,
         f"{op_standalone_primary}"),
        ("P3: op folio span >= 25",
         p3,
         f"{len(op_all_folios)} folios"),
        ("P4: op-initial compound majority matches standalone",
         p4,
         f"compound={op_initial_primary}, standalone={op_standalone_primary}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = p1 and p2
    print()
    print(f"  PRIMARY CRITERION (INITIAL >= 75% AND TRANSITION majority): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
