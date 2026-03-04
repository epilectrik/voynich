#!/usr/bin/env python3
"""
S-S6: CHSH+s compound enrichment

Test whether CHSH-prefixed (ch/sh prefix) tokens with s-containing MIDDLEs
are enriched in MONITORING and/or STAGING.

s is classified as STAGING by the CategoryClassifier. In CHSH context
(process testing PREFIXes), s-containing MIDDLEs should maintain or amplify
the STAGING/MONITORING signal.

NOTE: s is one of the 4 PROBLEMATIC PREFIX atoms (c,h,s,p from C1191).
When s appears in MIDDLE under CHSH PREFIX, it may show emergent behavior.

Groups:
  - CHSH+s:     ch/sh prefix, 's' in MIDDLE
  - CHSH+non-s: ch/sh prefix, 's' NOT in MIDDLE
  - CHSH+c:     ch/sh prefix, 'c' in MIDDLE (control -- MONITORING atom, 23.09x)
  - CHSH+k:     ch/sh prefix, 'k' in MIDDLE (control -- THERMAL atom)
  - CHSH+o:     ch/sh prefix, 'o' in MIDDLE (control -- STAGING atom)
  - CHSH+p:     ch/sh prefix, 'p' in MIDDLE (control -- MARKING atom, MON+MARK 87.4%)

Predictions:
  - CHSH+s MONITORING >= 30% AND enrichment >= 1.3x
  - OR: STAGING enrichment >= 1.3x
  - CHSH+s should differ from CHSH+non-s

Pass: MONITORING >= 30% AND (MON enrichment >= 1.3x OR STAGING enrichment >= 1.3x)
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']
CHSH_PREFIXES = {'ch', 'sh'}


def main():
    print("=" * 75)
    print("S-S6: CHSH+s compound enrichment")
    print("=" * 75)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Groups: category counts and MIDDLE tracking
    groups = {
        'CHSH+s': Counter(),
        'CHSH+non-s': Counter(),
        'CHSH+c': Counter(),
        'CHSH+k': Counter(),
        'CHSH+o': Counter(),
        'CHSH+p': Counter(),
        'CHSH+all': Counter(),
    }
    group_totals = Counter()
    group_middles = defaultdict(Counter)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m or not m.middle or not m.prefix:
            continue

        if m.prefix not in CHSH_PREFIXES:
            continue

        mid = m.middle
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        has_s = 's' in mid
        has_c = 'c' in mid
        has_k = 'k' in mid
        has_o = 'o' in mid
        has_p = 'p' in mid

        groups['CHSH+all'][cat] += 1
        group_totals['CHSH+all'] += 1

        if has_s:
            groups['CHSH+s'][cat] += 1
            group_totals['CHSH+s'] += 1
            group_middles['CHSH+s'][mid] += 1
        else:
            groups['CHSH+non-s'][cat] += 1
            group_totals['CHSH+non-s'] += 1

        if has_c:
            groups['CHSH+c'][cat] += 1
            group_totals['CHSH+c'] += 1

        if has_k:
            groups['CHSH+k'][cat] += 1
            group_totals['CHSH+k'] += 1

        if has_o:
            groups['CHSH+o'][cat] += 1
            group_totals['CHSH+o'] += 1

        if has_p:
            groups['CHSH+p'][cat] += 1
            group_totals['CHSH+p'] += 1

    # ---- Category profile table ----
    print()
    print("-" * 75)
    print("Category profiles for CHSH prefix groups")
    print("-" * 75)
    print()

    display_groups = ['CHSH+s', 'CHSH+non-s', 'CHSH+c', 'CHSH+k', 'CHSH+o', 'CHSH+p', 'CHSH+all']
    header = f"{'Group':<15} {'N':>6}"
    for cat in CATEGORIES:
        header += f" {cat[:7]:>8}"
    print(header)
    print("-" * (15 + 6 + len(CATEGORIES) * 9))

    for grp in display_groups:
        total = group_totals[grp]
        line = f"{grp:<15} {total:>6}"
        for cat in CATEGORIES:
            rate = groups[grp][cat] / total * 100 if total > 0 else 0
            line += f" {rate:>7.1f}%"
        print(line)

    # ---- Enrichment: CHSH+s vs CHSH+non-s ----
    print()
    print("-" * 75)
    print("Enrichment: CHSH+s vs CHSH+non-s")
    print("-" * 75)
    print()

    total_s = group_totals['CHSH+s']
    total_ns = group_totals['CHSH+non-s']

    print(f"{'Category':<15} {'CHSH+s%':>9} {'non-s%':>9} {'Ratio':>8}")
    print("-" * 48)

    enrichments = {}
    for cat in CATEGORIES:
        rate_s = groups['CHSH+s'][cat] / total_s if total_s > 0 else 0
        rate_ns = groups['CHSH+non-s'][cat] / total_ns if total_ns > 0 else 0
        ratio = rate_s / rate_ns if rate_ns > 0 else float('inf')
        enrichments[cat] = ratio
        marker = "  <--" if cat in ('MONITORING', 'STAGING') else ""
        print(f"  {cat:<13} {rate_s*100:>8.1f}% {rate_ns*100:>8.1f}% {ratio:>7.2f}x{marker}")

    mon_s = groups['CHSH+s'].get('MONITORING', 0) / total_s if total_s > 0 else 0
    stag_s = groups['CHSH+s'].get('STAGING', 0) / total_s if total_s > 0 else 0
    mon_ns = groups['CHSH+non-s'].get('MONITORING', 0) / total_ns if total_ns > 0 else 0
    stag_ns = groups['CHSH+non-s'].get('STAGING', 0) / total_ns if total_ns > 0 else 0

    print()
    print(f"  MONITORING:  CHSH+s = {mon_s*100:.1f}%, CHSH+non-s = {mon_ns*100:.1f}%")
    print(f"  STAGING:     CHSH+s = {stag_s*100:.1f}%, CHSH+non-s = {stag_ns*100:.1f}%")
    combined_mon_stag = mon_s + stag_s
    combined_ns = mon_ns + stag_ns
    combined_ratio = combined_mon_stag / combined_ns if combined_ns > 0 else float('inf')
    print(f"  MON+STAGING: CHSH+s = {combined_mon_stag*100:.1f}%, CHSH+non-s = {combined_ns*100:.1f}%, "
          f"ratio = {combined_ratio:.2f}x")

    # ---- Enrichment: CHSH+s vs CHSH+all (global baseline) ----
    print()
    print("-" * 75)
    print("Enrichment: CHSH+s vs CHSH+all (global baseline)")
    print("-" * 75)
    print()

    total_all = group_totals['CHSH+all']
    print(f"{'Category':<15} {'CHSH+s%':>9} {'all%':>9} {'Ratio':>8}")
    print("-" * 48)

    enrichments_global = {}
    for cat in CATEGORIES:
        rate_s = groups['CHSH+s'][cat] / total_s if total_s > 0 else 0
        rate_all = groups['CHSH+all'][cat] / total_all if total_all > 0 else 0
        ratio = rate_s / rate_all if rate_all > 0 else float('inf')
        enrichments_global[cat] = ratio
        marker = "  <--" if cat in ('MONITORING', 'STAGING') else ""
        print(f"  {cat:<13} {rate_s*100:>8.1f}% {rate_all*100:>8.1f}% {ratio:>7.2f}x{marker}")

    # ---- Top CHSH+s MIDDLEs ----
    print()
    print("-" * 75)
    print("Top 20 CHSH+s MIDDLEs")
    print("-" * 75)
    print()

    sorted_mids = sorted(group_middles['CHSH+s'].items(), key=lambda x: -x[1])
    print(f"{'MIDDLE':<15} {'Count':>6} {'Category':<15}")
    print("-" * 40)
    for mid, count in sorted_mids[:20]:
        cat = cc.classify(mid)
        print(f"  {mid:<13} {count:>6} {cat}")

    # ---- Controls ----
    print()
    print("-" * 75)
    print("Control comparisons (vs CHSH+all)")
    print("-" * 75)
    print()

    control_atoms = [('CHSH+c', 'c', 'MONITORING expected'),
                     ('CHSH+k', 'k', 'THERMAL expected'),
                     ('CHSH+o', 'o', 'STAGING expected'),
                     ('CHSH+p', 'p', 'MARKING expected')]

    for grp_name, atom, desc in control_atoms:
        total_grp = group_totals[grp_name]
        if total_grp > 0 and total_all > 0:
            print(f"  {grp_name} (N={total_grp}) - {desc}:")
            top3 = groups[grp_name].most_common(3)
            parts = []
            for cat, n in top3:
                rate = n / total_grp * 100
                rate_all = groups['CHSH+all'][cat] / total_all * 100
                ratio = rate / rate_all if rate_all > 0 else 0
                parts.append(f"{cat}={rate:.1f}%({ratio:.2f}x)")
            print(f"    {', '.join(parts)}")
        else:
            print(f"  {grp_name}: (Insufficient data)")

    # ---- VERDICTS ----
    print()
    print("=" * 75)
    print("VERDICTS")
    print("=" * 75)
    print()

    mon_enrich = enrichments.get('MONITORING', 0)
    stag_enrich = enrichments.get('STAGING', 0)

    p1 = mon_s * 100 >= 30.0
    print(f"  [{'PASS' if p1 else 'FAIL'}] P1: CHSH+s MONITORING >= 30%: "
          f"{mon_s*100:.1f}%")

    p2 = mon_enrich >= 1.3 or stag_enrich >= 1.3
    print(f"  [{'PASS' if p2 else 'FAIL'}] P2: MON enrich >= 1.3x OR STAGING enrich >= 1.3x: "
          f"MON={mon_enrich:.2f}x, STAGING={stag_enrich:.2f}x")

    # Positive control: CHSH+k THERMAL enrichment
    total_k = group_totals['CHSH+k']
    if total_k > 0 and total_all > 0:
        thermal_k = groups['CHSH+k']['THERMAL'] / total_k
        thermal_all = groups['CHSH+all']['THERMAL'] / total_all
        k_thermal_enrich = thermal_k / thermal_all if thermal_all > 0 else 0
        ctrl_pass = k_thermal_enrich >= 1.3
        print(f"  [{'PASS' if ctrl_pass else 'FAIL'}] Control: CHSH+k THERMAL enrichment: "
              f"{k_thermal_enrich:.2f}x (expected >= 1.3x)")

    overall = p1 and p2
    print()
    print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
    if overall:
        print("  CHSH+s compounds confirm MONITORING/STAGING enrichment")
    else:
        print("  CHSH+s compounds do NOT confirm predicted enrichment pattern")
        if not p1:
            print(f"    MONITORING only {mon_s*100:.1f}% (needed >= 30%)")
        if not p2:
            print(f"    Neither MONITORING ({mon_enrich:.2f}x) nor STAGING ({stag_enrich:.2f}x) "
                  f"reached 1.3x enrichment")

    # Note on C1191 PROBLEMATIC status
    print()
    print("-" * 75)
    print("NOTE: C1191 PROBLEMATIC atom behavior")
    print("-" * 75)
    print()
    print("  s is one of 4 atoms (c,h,s,p) that show emergent behavior in PREFIX")
    print("  position (C1191 CPC score: 0.7794 CONSISTENT but PROBLEMATIC).")
    print("  If CHSH+s shows unexpected category enrichment, this may reflect")
    print("  the same emergent/non-compositional behavior seen in PREFIX position.")
    print(f"  Observed: MON={mon_s*100:.1f}%, STAG={stag_s*100:.1f}%, "
          f"THERMAL={groups['CHSH+s'].get('THERMAL', 0)/total_s*100 if total_s > 0 else 0:.1f}%")


if __name__ == '__main__':
    main()
