"""
P-C14: c Injects MONITORING into Compounds
============================================
Test whether adding c to a base atom consistently increases MONITORING fraction.

Method:
1. For each base atom X that appears in both c+X and non-c+X contexts:
   - Collect all c+X tokens, compute MONITORING fraction
   - Collect all non-c first-atom + X tokens, compute MONITORING fraction
   - Compare: does c+X have higher MONITORING than average-first+X?
2. Aggregate across all X: does c systematically inject MONITORING?
3. Same analysis for MARKING.

Pass: MONITORING injection in >= 3/4 bases AND mean injection >= 10pp
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

    # Collect: for each (first_atom, second_atom) pair, count categories
    # pair_data[(first, second)] = Counter of categories
    pair_data = defaultdict(Counter)
    # Also track standalone second atoms
    standalone_data = defaultdict(Counter)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        if len(mid) == 1:
            standalone_data[mid][cat] += 1
        elif len(mid) >= 2:
            first = mid[0]
            second = mid[1]
            pair_data[(first, second)][cat] += 1

    # Find base atoms X where both c+X and at least one non-c+X exist with N>=5
    c_bases = set()
    for (first, second), counts in pair_data.items():
        if first == 'c' and sum(counts.values()) >= 5:
            c_bases.add(second)

    # For each base X, gather c+X data and non-c+X aggregate
    print("=" * 80)
    print("P-C14: c Injects MONITORING into Compounds")
    print("=" * 80)

    # --- MONITORING Analysis ---
    print("\n--- MONITORING Injection Analysis ---")
    print(f"{'Base X':<8} {'c+X Mon%':<12} {'c+X N':<8} {'non-c+X Mon%':<15} {'non-c+X N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    monitoring_injections = 0
    monitoring_bases_tested = 0
    monitoring_deltas = []

    for base in sorted(c_bases):
        # c+X data
        c_counts = pair_data.get(('c', base), Counter())
        c_total = sum(c_counts.values())
        if c_total < 5:
            continue

        c_mon = c_counts.get('MONITORING', 0) / c_total

        # non-c+X aggregate (all first atoms except c)
        non_c_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'c':
                non_c_counts += counts

        # Also include standalone X
        if base in standalone_data:
            non_c_counts += standalone_data[base]

        non_c_total = sum(non_c_counts.values())
        if non_c_total < 5:
            continue

        non_c_mon = non_c_counts.get('MONITORING', 0) / non_c_total
        delta = c_mon - non_c_mon
        injected = delta > 0

        monitoring_bases_tested += 1
        monitoring_deltas.append(delta)
        if injected:
            monitoring_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {c_mon:<12.1%} {c_total:<8} {non_c_mon:<15.1%} {non_c_total:<10} {delta:<+10.1%} {marker}")

    mean_mon_delta = sum(monitoring_deltas) / len(monitoring_deltas) if monitoring_deltas else 0

    print(f"\nMONITORING injection: {monitoring_injections}/{monitoring_bases_tested} bases")
    print(f"Mean MONITORING delta: {mean_mon_delta:+.1%}")

    # --- MARKING Analysis ---
    print("\n--- MARKING Injection Analysis ---")
    print(f"{'Base X':<8} {'c+X Mrk%':<12} {'c+X N':<8} {'non-c+X Mrk%':<15} {'non-c+X N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    marking_injections = 0
    marking_bases_tested = 0
    marking_deltas = []

    for base in sorted(c_bases):
        c_counts = pair_data.get(('c', base), Counter())
        c_total = sum(c_counts.values())
        if c_total < 5:
            continue

        c_mrk = c_counts.get('MARKING', 0) / c_total

        non_c_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'c':
                non_c_counts += counts
        if base in standalone_data:
            non_c_counts += standalone_data[base]

        non_c_total = sum(non_c_counts.values())
        if non_c_total < 5:
            continue

        non_c_mrk = non_c_counts.get('MARKING', 0) / non_c_total
        delta = c_mrk - non_c_mrk
        injected = delta > 0

        marking_bases_tested += 1
        marking_deltas.append(delta)
        if injected:
            marking_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {c_mrk:<12.1%} {c_total:<8} {non_c_mrk:<15.1%} {non_c_total:<10} {delta:<+10.1%} {marker}")

    mean_mrk_delta = sum(marking_deltas) / len(marking_deltas) if marking_deltas else 0

    print(f"\nMARKING injection: {marking_injections}/{marking_bases_tested} bases")
    print(f"Mean MARKING delta: {mean_mrk_delta:+.1%}")

    # --- Combined MONITORING + MARKING ---
    print("\n--- Combined MONITORING + MARKING Injection ---")
    print(f"{'Base X':<8} {'c+X M+M%':<12} {'c+X N':<8} {'non-c M+M%':<15} {'non-c N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    combined_injections = 0
    combined_bases_tested = 0
    combined_deltas = []

    for base in sorted(c_bases):
        c_counts = pair_data.get(('c', base), Counter())
        c_total = sum(c_counts.values())
        if c_total < 5:
            continue

        c_mm = (c_counts.get('MONITORING', 0) + c_counts.get('MARKING', 0)) / c_total

        non_c_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'c':
                non_c_counts += counts
        if base in standalone_data:
            non_c_counts += standalone_data[base]

        non_c_total = sum(non_c_counts.values())
        if non_c_total < 5:
            continue

        non_c_mm = (non_c_counts.get('MONITORING', 0) + non_c_counts.get('MARKING', 0)) / non_c_total
        delta = c_mm - non_c_mm
        injected = delta > 0

        combined_bases_tested += 1
        combined_deltas.append(delta)
        if injected:
            combined_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {c_mm:<12.1%} {c_total:<8} {non_c_mm:<15.1%} {non_c_total:<10} {delta:<+10.1%} {marker}")

    mean_comb_delta = sum(combined_deltas) / len(combined_deltas) if combined_deltas else 0

    print(f"\nCombined injection: {combined_injections}/{combined_bases_tested} bases")
    print(f"Mean combined delta: {mean_comb_delta:+.1%}")

    # --- Full category profile comparison ---
    print("\n--- Full Category Profile: c+X vs non-c+X ---")
    for base in sorted(c_bases):
        c_counts = pair_data.get(('c', base), Counter())
        c_total = sum(c_counts.values())
        if c_total < 5:
            continue

        non_c_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'c':
                non_c_counts += counts
        if base in standalone_data:
            non_c_counts += standalone_data[base]
        non_c_total = sum(non_c_counts.values())
        if non_c_total < 5:
            continue

        print(f"\n  Base atom: {base}")
        print(f"  {'Category':<15} {'c+{0} (N={1})':<20} {'non-c+{0} (N={2})':<20}".format(
            base, c_total, non_c_total))
        for cat in CATEGORIES:
            c_frac = c_counts.get(cat, 0) / c_total
            nc_frac = non_c_counts.get(cat, 0) / non_c_total
            delta = c_frac - nc_frac
            flag = " ***" if abs(delta) > 0.10 else ""
            print(f"  {cat:<15} {c_frac:<20.1%} {nc_frac:<20.1%} {delta:+.1%}{flag}")

    # --- Verdicts ---
    print("\n" + "=" * 80)
    print("VERDICTS")
    print("=" * 80)

    mon_frac = monitoring_injections / monitoring_bases_tested if monitoring_bases_tested > 0 else 0
    v1 = monitoring_bases_tested >= 4 and mon_frac >= 0.75
    print(f"\n[{'PASS' if v1 else 'FAIL'}] MONITORING injection in >= 3/4 bases: "
          f"{monitoring_injections}/{monitoring_bases_tested} = {mon_frac:.1%}")

    v2 = mean_mon_delta >= 0.10
    print(f"[{'PASS' if v2 else 'FAIL'}] Mean MONITORING injection >= 10pp: {mean_mon_delta:+.1%}")

    mrk_frac = marking_injections / marking_bases_tested if marking_bases_tested > 0 else 0
    v3 = marking_bases_tested >= 4 and mrk_frac >= 0.75
    print(f"[{'PASS' if v3 else 'FAIL'}] MARKING injection in >= 3/4 bases: "
          f"{marking_injections}/{marking_bases_tested} = {mrk_frac:.1%}")

    overall = v1 and v2
    print(f"\n{'='*80}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'} (MONITORING >= 3/4 bases AND >= 10pp)")
    if v3:
        print(f"BONUS: MARKING injection also confirmed")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
