"""
P-P11: p Injects MARKING into Compounds
=========================================
Test whether adding p to a base atom consistently increases MARKING fraction.

Method:
1. For each base atom X that appears in both p+X and non-p+X contexts:
   - Collect all p+X tokens, compute MARKING fraction
   - Collect all non-p first-atom + X tokens, compute MARKING fraction
   - Compare: does p+X have higher MARKING than average-first+X?
2. Aggregate across all X: does p systematically inject MARKING?
3. Same analysis for MONITORING (given H-kernel affinity 0.711).
4. Combined MARKING+MONITORING analysis.

Pass: MARKING injection in >= 2/3 bases AND mean injection >= +5pp
(Lower thresholds than c-atom due to thinner data.)
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

    # Find base atoms X where both p+X and at least one non-p+X exist with N>=5
    p_bases = set()
    for (first, second), counts in pair_data.items():
        if first == 'p' and sum(counts.values()) >= 5:
            p_bases.add(second)

    print("=" * 80)
    print("P-P11: p Injects MARKING into Compounds")
    print("=" * 80)
    print(f"\nBase atoms with p+X N>=5: {sorted(p_bases)}")

    # --- MARKING Analysis ---
    print("\n--- MARKING Injection Analysis ---")
    print(f"{'Base X':<8} {'p+X Mrk%':<12} {'p+X N':<8} {'non-p+X Mrk%':<15} {'non-p+X N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    marking_injections = 0
    marking_bases_tested = 0
    marking_deltas = []

    for base in sorted(p_bases):
        # p+X data
        p_counts = pair_data.get(('p', base), Counter())
        p_total = sum(p_counts.values())
        if p_total < 5:
            continue

        p_mrk = p_counts.get('MARKING', 0) / p_total

        # non-p+X aggregate (all first atoms except p)
        non_p_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'p':
                non_p_counts += counts

        # Also include standalone X
        if base in standalone_data:
            non_p_counts += standalone_data[base]

        non_p_total = sum(non_p_counts.values())
        if non_p_total < 5:
            continue

        non_p_mrk = non_p_counts.get('MARKING', 0) / non_p_total
        delta = p_mrk - non_p_mrk
        injected = delta > 0

        marking_bases_tested += 1
        marking_deltas.append(delta)
        if injected:
            marking_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {p_mrk:<12.1%} {p_total:<8} {non_p_mrk:<15.1%} {non_p_total:<10} {delta:<+10.1%} {marker}")

    mean_mrk_delta = sum(marking_deltas) / len(marking_deltas) if marking_deltas else 0

    print(f"\nMARKING injection: {marking_injections}/{marking_bases_tested} bases")
    print(f"Mean MARKING delta: {mean_mrk_delta:+.1%}")

    # --- MONITORING Analysis ---
    print("\n--- MONITORING Injection Analysis ---")
    print(f"{'Base X':<8} {'p+X Mon%':<12} {'p+X N':<8} {'non-p+X Mon%':<15} {'non-p+X N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    monitoring_injections = 0
    monitoring_bases_tested = 0
    monitoring_deltas = []

    for base in sorted(p_bases):
        p_counts = pair_data.get(('p', base), Counter())
        p_total = sum(p_counts.values())
        if p_total < 5:
            continue

        p_mon = p_counts.get('MONITORING', 0) / p_total

        non_p_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'p':
                non_p_counts += counts
        if base in standalone_data:
            non_p_counts += standalone_data[base]

        non_p_total = sum(non_p_counts.values())
        if non_p_total < 5:
            continue

        non_p_mon = non_p_counts.get('MONITORING', 0) / non_p_total
        delta = p_mon - non_p_mon
        injected = delta > 0

        monitoring_bases_tested += 1
        monitoring_deltas.append(delta)
        if injected:
            monitoring_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {p_mon:<12.1%} {p_total:<8} {non_p_mon:<15.1%} {non_p_total:<10} {delta:<+10.1%} {marker}")

    mean_mon_delta = sum(monitoring_deltas) / len(monitoring_deltas) if monitoring_deltas else 0

    print(f"\nMONITORING injection: {monitoring_injections}/{monitoring_bases_tested} bases")
    print(f"Mean MONITORING delta: {mean_mon_delta:+.1%}")

    # --- Combined MARKING + MONITORING ---
    print("\n--- Combined MARKING + MONITORING Injection ---")
    print(f"{'Base X':<8} {'p+X M+M%':<12} {'p+X N':<8} {'non-p M+M%':<15} {'non-p N':<10} {'Delta':<10} {'Injected?'}")
    print("-" * 80)

    combined_injections = 0
    combined_bases_tested = 0
    combined_deltas = []

    for base in sorted(p_bases):
        p_counts = pair_data.get(('p', base), Counter())
        p_total = sum(p_counts.values())
        if p_total < 5:
            continue

        p_mm = (p_counts.get('MARKING', 0) + p_counts.get('MONITORING', 0)) / p_total

        non_p_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'p':
                non_p_counts += counts
        if base in standalone_data:
            non_p_counts += standalone_data[base]

        non_p_total = sum(non_p_counts.values())
        if non_p_total < 5:
            continue

        non_p_mm = (non_p_counts.get('MARKING', 0) + non_p_counts.get('MONITORING', 0)) / non_p_total
        delta = p_mm - non_p_mm
        injected = delta > 0

        combined_bases_tested += 1
        combined_deltas.append(delta)
        if injected:
            combined_injections += 1

        marker = "YES" if injected else "no"
        print(f"{base:<8} {p_mm:<12.1%} {p_total:<8} {non_p_mm:<15.1%} {non_p_total:<10} {delta:<+10.1%} {marker}")

    mean_comb_delta = sum(combined_deltas) / len(combined_deltas) if combined_deltas else 0

    print(f"\nCombined injection: {combined_injections}/{combined_bases_tested} bases")
    print(f"Mean combined delta: {mean_comb_delta:+.1%}")

    # --- Full category profile comparison ---
    print("\n--- Full Category Profile: p+X vs non-p+X ---")
    for base in sorted(p_bases):
        p_counts = pair_data.get(('p', base), Counter())
        p_total = sum(p_counts.values())
        if p_total < 5:
            continue

        non_p_counts = Counter()
        for (first, second), counts in pair_data.items():
            if second == base and first != 'p':
                non_p_counts += counts
        if base in standalone_data:
            non_p_counts += standalone_data[base]
        non_p_total = sum(non_p_counts.values())
        if non_p_total < 5:
            continue

        print(f"\n  Base atom: {base}")
        print(f"  {'Category':<15} {'p+' + base + ' (N=' + str(p_total) + ')':<20} {'non-p+' + base + ' (N=' + str(non_p_total) + ')':<25} {'Delta'}")
        for cat in CATEGORIES:
            p_frac = p_counts.get(cat, 0) / p_total
            nc_frac = non_p_counts.get(cat, 0) / non_p_total
            delta = p_frac - nc_frac
            flag = " ***" if abs(delta) > 0.10 else ""
            print(f"  {cat:<15} {p_frac:<20.1%} {nc_frac:<25.1%} {delta:+.1%}{flag}")

    # --- Verdicts ---
    print("\n" + "=" * 80)
    print("VERDICTS")
    print("=" * 80)

    # V1: MARKING injection in >= 2/3 bases
    mrk_frac = marking_injections / marking_bases_tested if marking_bases_tested > 0 else 0
    v1 = marking_bases_tested >= 3 and mrk_frac >= 2.0 / 3.0
    print(f"\n[{'PASS' if v1 else 'FAIL'}] MARKING injection in >= 2/3 bases: "
          f"{marking_injections}/{marking_bases_tested} = {mrk_frac:.1%}")

    # V2: Mean MARKING delta >= +5pp
    v2 = mean_mrk_delta >= 0.05
    print(f"[{'PASS' if v2 else 'FAIL'}] Mean MARKING injection >= +5pp: {mean_mrk_delta:+.1%}")

    # V3: MONITORING injection (informational)
    mon_frac = monitoring_injections / monitoring_bases_tested if monitoring_bases_tested > 0 else 0
    v3 = monitoring_bases_tested >= 3 and mon_frac >= 2.0 / 3.0
    print(f"[{'PASS' if v3 else 'FAIL'}] MONITORING injection in >= 2/3 bases: "
          f"{monitoring_injections}/{monitoring_bases_tested} = {mon_frac:.1%}")

    # V4: Combined MARKING+MONITORING
    comb_frac = combined_injections / combined_bases_tested if combined_bases_tested > 0 else 0
    v4 = combined_bases_tested >= 3 and comb_frac >= 2.0 / 3.0
    print(f"[{'PASS' if v4 else 'FAIL'}] Combined M+M injection in >= 2/3 bases: "
          f"{combined_injections}/{combined_bases_tested} = {comb_frac:.1%}")

    overall = v1 and v2
    print(f"\n{'=' * 80}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'} (MARKING >= 2/3 bases AND mean delta >= +5pp)")
    if v3:
        print(f"BONUS: MONITORING injection also confirmed ({monitoring_injections}/{monitoring_bases_tested})")
    if v4:
        print(f"BONUS: Combined MARKING+MONITORING injection confirmed ({combined_injections}/{combined_bases_tested})")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
