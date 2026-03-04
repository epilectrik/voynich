#!/usr/bin/env python3
"""
P-P6: CHSH+p compound enrichment

Test whether CHSH-prefixed (ch/sh prefix) tokens with p-containing MIDDLEs
are enriched in MONITORING+MARKING.

p is classified as MARKING by the CategoryClassifier. In CHSH context
(process testing PREFIXes), p-containing MIDDLEs should maintain or amplify
the MARKING/MONITORING signal.

Groups:
  - CHSH+p:     ch/sh prefix, 'p' in MIDDLE
  - CHSH+non-p: ch/sh prefix, 'p' NOT in MIDDLE
  - CHSH+c:     ch/sh prefix, 'c' in MIDDLE (control -- known MARKING atom)
  - CHSH+k:     ch/sh prefix, 'k' in MIDDLE (control -- known THERMAL atom)
  - CHSH+o:     ch/sh prefix, 'o' in MIDDLE (control -- known STAGING atom)

Predictions:
  - CHSH+p MON+MARK >= 35%
  - Enrichment >= 1.5x vs CHSH+non-p
  - CHSH+k should be THERMAL-enriched (positive control)

Pass: MON+MARK >= 35% AND (MONITORING enrichment >= 1.5x OR MARKING enrichment >= 1.5x)
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
    print("P-P6: CHSH+p compound enrichment")
    print("=" * 75)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Groups: category counts and MIDDLE tracking
    groups = {
        'CHSH+p': Counter(),
        'CHSH+non-p': Counter(),
        'CHSH+c': Counter(),
        'CHSH+k': Counter(),
        'CHSH+o': Counter(),
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

        has_p = 'p' in mid
        has_c = 'c' in mid
        has_k = 'k' in mid
        has_o = 'o' in mid

        groups['CHSH+all'][cat] += 1
        group_totals['CHSH+all'] += 1

        if has_p:
            groups['CHSH+p'][cat] += 1
            group_totals['CHSH+p'] += 1
            group_middles['CHSH+p'][mid] += 1
        else:
            groups['CHSH+non-p'][cat] += 1
            group_totals['CHSH+non-p'] += 1

        if has_c:
            groups['CHSH+c'][cat] += 1
            group_totals['CHSH+c'] += 1

        if has_k:
            groups['CHSH+k'][cat] += 1
            group_totals['CHSH+k'] += 1

        if has_o:
            groups['CHSH+o'][cat] += 1
            group_totals['CHSH+o'] += 1

    # ---- Category profile table ----
    print()
    print("-" * 75)
    print("Category profiles for CHSH prefix groups")
    print("-" * 75)
    print()

    display_groups = ['CHSH+p', 'CHSH+non-p', 'CHSH+c', 'CHSH+k', 'CHSH+o', 'CHSH+all']
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

    # ---- Enrichment: CHSH+p vs CHSH+non-p ----
    print()
    print("-" * 75)
    print("Enrichment: CHSH+p vs CHSH+non-p")
    print("-" * 75)
    print()

    total_p = group_totals['CHSH+p']
    total_np = group_totals['CHSH+non-p']

    print(f"{'Category':<15} {'CHSH+p%':>9} {'non-p%':>9} {'Ratio':>8}")
    print("-" * 48)

    enrichments = {}
    for cat in CATEGORIES:
        rate_p = groups['CHSH+p'][cat] / total_p if total_p > 0 else 0
        rate_np = groups['CHSH+non-p'][cat] / total_np if total_np > 0 else 0
        ratio = rate_p / rate_np if rate_np > 0 else float('inf')
        enrichments[cat] = ratio
        marker = "  <--" if cat in ('MONITORING', 'MARKING') else ""
        print(f"  {cat:<13} {rate_p*100:>8.1f}% {rate_np*100:>8.1f}% {ratio:>7.2f}x{marker}")

    mon_mark_p = 0
    mon_mark_np = 0
    if total_p > 0:
        mon_mark_p = (groups['CHSH+p']['MONITORING'] + groups['CHSH+p']['MARKING']) / total_p
    if total_np > 0:
        mon_mark_np = (groups['CHSH+non-p']['MONITORING'] + groups['CHSH+non-p']['MARKING']) / total_np

    print()
    print(f"  Combined MONITORING+MARKING:")
    print(f"    CHSH+p:     {mon_mark_p*100:.1f}%")
    print(f"    CHSH+non-p: {mon_mark_np*100:.1f}%")
    combined_ratio = mon_mark_p / mon_mark_np if mon_mark_np > 0 else float('inf')
    print(f"    Ratio:      {combined_ratio:.2f}x")

    # ---- Top CHSH+p MIDDLEs ----
    print()
    print("-" * 75)
    print("Top 20 CHSH+p MIDDLEs")
    print("-" * 75)
    print()

    sorted_mids = sorted(group_middles['CHSH+p'].items(), key=lambda x: -x[1])
    print(f"{'MIDDLE':<15} {'Count':>6} {'Category':<15}")
    print("-" * 40)
    for mid, count in sorted_mids[:20]:
        cat = cc.classify(mid)
        print(f"  {mid:<13} {count:>6} {cat}")

    # ---- Controls ----
    print()
    print("-" * 75)
    print("Control: CHSH+k (expected THERMAL enrichment)")
    print("-" * 75)
    print()

    total_k = group_totals['CHSH+k']
    total_all = group_totals['CHSH+all']
    if total_k > 0 and total_all > 0:
        print(f"{'Category':<15} {'CHSH+k%':>9} {'all%':>9} {'Ratio':>8}")
        print("-" * 48)
        for cat in CATEGORIES:
            rate_k = groups['CHSH+k'][cat] / total_k
            rate_all = groups['CHSH+all'][cat] / total_all
            ratio = rate_k / rate_all if rate_all > 0 else float('inf')
            marker = " <-- THERMAL" if cat == 'THERMAL' and ratio > 1.3 else ""
            print(f"  {cat:<13} {rate_k*100:>8.1f}% {rate_all*100:>8.1f}% {ratio:>7.2f}x{marker}")
    else:
        print("  (Insufficient data)")

    print()
    print("-" * 75)
    print("Control: CHSH+o (expected STAGING enrichment)")
    print("-" * 75)
    print()

    total_o = group_totals['CHSH+o']
    if total_o > 0 and total_all > 0:
        print(f"{'Category':<15} {'CHSH+o%':>9} {'all%':>9} {'Ratio':>8}")
        print("-" * 48)
        for cat in CATEGORIES:
            rate_o = groups['CHSH+o'][cat] / total_o
            rate_all = groups['CHSH+all'][cat] / total_all
            ratio = rate_o / rate_all if rate_all > 0 else float('inf')
            marker = " <-- STAGING" if cat == 'STAGING' and ratio > 1.3 else ""
            print(f"  {cat:<13} {rate_o*100:>8.1f}% {rate_all*100:>8.1f}% {ratio:>7.2f}x{marker}")
    else:
        print("  (Insufficient data)")

    print()
    print("-" * 75)
    print("Control: CHSH+c (expected MARKING/MONITORING enrichment)")
    print("-" * 75)
    print()

    total_c = group_totals['CHSH+c']
    if total_c > 0 and total_all > 0:
        print(f"{'Category':<15} {'CHSH+c%':>9} {'all%':>9} {'Ratio':>8}")
        print("-" * 48)
        for cat in CATEGORIES:
            rate_c = groups['CHSH+c'][cat] / total_c
            rate_all = groups['CHSH+all'][cat] / total_all
            ratio = rate_c / rate_all if rate_all > 0 else float('inf')
            marker = " <-- MON/MARK" if cat in ('MONITORING', 'MARKING') and ratio > 1.3 else ""
            print(f"  {cat:<13} {rate_c*100:>8.1f}% {rate_all*100:>8.1f}% {ratio:>7.2f}x{marker}")
    else:
        print("  (Insufficient data)")

    # ---- VERDICTS ----
    print()
    print("=" * 75)
    print("VERDICTS")
    print("=" * 75)
    print()

    p1 = mon_mark_p * 100 >= 35.0
    print(f"  [{'PASS' if p1 else 'FAIL'}] P1: CHSH+p MONITORING+MARKING >= 35%: "
          f"{mon_mark_p*100:.1f}%")

    mon_enrich = enrichments.get('MONITORING', 0)
    mark_enrich = enrichments.get('MARKING', 0)
    p2 = mon_enrich >= 1.5 or mark_enrich >= 1.5
    print(f"  [{'PASS' if p2 else 'FAIL'}] P2: MONITORING enrich >= 1.5x OR MARKING enrich >= 1.5x: "
          f"MON={mon_enrich:.2f}x, MARK={mark_enrich:.2f}x")

    # Positive control: CHSH+k THERMAL enrichment
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
        print("  CHSH+p compounds confirm MONITORING/MARKING enrichment")
    else:
        print("  CHSH+p compounds do NOT confirm predicted enrichment pattern")
        if not p1:
            print(f"    MON+MARK only {mon_mark_p*100:.1f}% (needed >= 35%)")
        if not p2:
            print(f"    Neither MONITORING ({mon_enrich:.2f}x) nor MARKING ({mark_enrich:.2f}x) "
                  f"reached 1.5x enrichment")


if __name__ == '__main__':
    main()
