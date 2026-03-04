#!/usr/bin/env python3
"""
F-F6: CHSH+f compound enrichment

Test whether CHSH-prefixed (ch/sh prefix) tokens with f-containing MIDDLEs
are enriched in MARKING.

f is classified as MARKING by the CategoryClassifier (gloss: "flag").
In CHSH context (process testing PREFIXes), f-containing MIDDLEs should
maintain the MARKING signal since f is a MARKING atom.

Groups:
  - CHSH+f:     ch/sh prefix, 'f' in MIDDLE
  - CHSH+non-f: ch/sh prefix, 'f' NOT in MIDDLE
  - CHSH+p:     ch/sh prefix, 'p' in MIDDLE (control -- MARKING atom, MON+MARK 87.4%)
  - CHSH+c:     ch/sh prefix, 'c' in MIDDLE (control -- MONITORING atom, 23.09x)
  - CHSH+k:     ch/sh prefix, 'k' in MIDDLE (control -- THERMAL atom)
  - CHSH+d:     ch/sh prefix, 'd' in MIDDLE (control -- another MARKING atom)

Predictions:
  - CHSH+f MARKING >= 30% AND enrichment >= 1.3x vs CHSH+non-f
  - OR: MARKING+MONITORING combined enrichment >= 1.3x

Pass: MARKING >= 30% AND (MARKING enrichment >= 1.3x OR MARK+MON enrichment >= 1.3x)
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
    print("F-F6: CHSH+f compound enrichment")
    print("=" * 75)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Groups: category counts and MIDDLE tracking
    groups = {
        'CHSH+f': Counter(),
        'CHSH+non-f': Counter(),
        'CHSH+p': Counter(),
        'CHSH+c': Counter(),
        'CHSH+k': Counter(),
        'CHSH+d': Counter(),
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

        has_f = 'f' in mid
        has_p = 'p' in mid
        has_c = 'c' in mid
        has_k = 'k' in mid
        has_d = 'd' in mid

        groups['CHSH+all'][cat] += 1
        group_totals['CHSH+all'] += 1

        if has_f:
            groups['CHSH+f'][cat] += 1
            group_totals['CHSH+f'] += 1
            group_middles['CHSH+f'][mid] += 1
        else:
            groups['CHSH+non-f'][cat] += 1
            group_totals['CHSH+non-f'] += 1

        if has_p:
            groups['CHSH+p'][cat] += 1
            group_totals['CHSH+p'] += 1

        if has_c:
            groups['CHSH+c'][cat] += 1
            group_totals['CHSH+c'] += 1

        if has_k:
            groups['CHSH+k'][cat] += 1
            group_totals['CHSH+k'] += 1

        if has_d:
            groups['CHSH+d'][cat] += 1
            group_totals['CHSH+d'] += 1

    # ---- Category profile table ----
    print()
    print("-" * 75)
    print("Category profiles for CHSH prefix groups")
    print("-" * 75)
    print()

    display_groups = ['CHSH+f', 'CHSH+non-f', 'CHSH+p', 'CHSH+c', 'CHSH+k', 'CHSH+d', 'CHSH+all']
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

    # ---- Enrichment: CHSH+f vs CHSH+non-f ----
    print()
    print("-" * 75)
    print("Enrichment: CHSH+f vs CHSH+non-f")
    print("-" * 75)
    print()

    total_f = group_totals['CHSH+f']
    total_nf = group_totals['CHSH+non-f']

    print(f"{'Category':<15} {'CHSH+f%':>9} {'non-f%':>9} {'Ratio':>8}")
    print("-" * 48)

    enrichments = {}
    for cat in CATEGORIES:
        rate_f = groups['CHSH+f'][cat] / total_f if total_f > 0 else 0
        rate_nf = groups['CHSH+non-f'][cat] / total_nf if total_nf > 0 else 0
        ratio = rate_f / rate_nf if rate_nf > 0 else float('inf')
        enrichments[cat] = ratio
        marker = "  <--" if cat in ('MARKING', 'MONITORING') else ""
        print(f"  {cat:<13} {rate_f*100:>8.1f}% {rate_nf*100:>8.1f}% {ratio:>7.2f}x{marker}")

    mark_f = groups['CHSH+f'].get('MARKING', 0) / total_f if total_f > 0 else 0
    mon_f = groups['CHSH+f'].get('MONITORING', 0) / total_f if total_f > 0 else 0
    mark_nf = groups['CHSH+non-f'].get('MARKING', 0) / total_nf if total_nf > 0 else 0
    mon_nf = groups['CHSH+non-f'].get('MONITORING', 0) / total_nf if total_nf > 0 else 0

    print()
    print(f"  MARKING:    CHSH+f = {mark_f*100:.1f}%, CHSH+non-f = {mark_nf*100:.1f}%")
    print(f"  MONITORING: CHSH+f = {mon_f*100:.1f}%, CHSH+non-f = {mon_nf*100:.1f}%")
    combined_mark_mon = mark_f + mon_f
    combined_nf = mark_nf + mon_nf
    combined_ratio = combined_mark_mon / combined_nf if combined_nf > 0 else float('inf')
    print(f"  MARK+MON:   CHSH+f = {combined_mark_mon*100:.1f}%, CHSH+non-f = {combined_nf*100:.1f}%, "
          f"ratio = {combined_ratio:.2f}x")

    # ---- Enrichment: CHSH+f vs CHSH+all (global baseline) ----
    print()
    print("-" * 75)
    print("Enrichment: CHSH+f vs CHSH+all (global baseline)")
    print("-" * 75)
    print()

    total_all = group_totals['CHSH+all']
    print(f"{'Category':<15} {'CHSH+f%':>9} {'all%':>9} {'Ratio':>8}")
    print("-" * 48)

    enrichments_global = {}
    for cat in CATEGORIES:
        rate_f = groups['CHSH+f'][cat] / total_f if total_f > 0 else 0
        rate_all = groups['CHSH+all'][cat] / total_all if total_all > 0 else 0
        ratio = rate_f / rate_all if rate_all > 0 else float('inf')
        enrichments_global[cat] = ratio
        marker = "  <--" if cat in ('MARKING', 'MONITORING') else ""
        print(f"  {cat:<13} {rate_f*100:>8.1f}% {rate_all*100:>8.1f}% {ratio:>7.2f}x{marker}")

    # ---- Top CHSH+f MIDDLEs ----
    print()
    print("-" * 75)
    print("Top CHSH+f MIDDLEs")
    print("-" * 75)
    print()

    sorted_mids = sorted(group_middles['CHSH+f'].items(), key=lambda x: -x[1])
    print(f"{'MIDDLE':<15} {'Count':>6} {'Category':<15}")
    print("-" * 40)
    for mid, count in sorted_mids[:20]:
        cat = cc.classify(mid)
        print(f"  {mid:<13} {count:>6} {cat}")

    if not sorted_mids:
        print("  (No CHSH+f tokens found)")

    # ---- Controls ----
    print()
    print("-" * 75)
    print("Control comparisons (vs CHSH+all)")
    print("-" * 75)
    print()

    control_atoms = [('CHSH+p', 'p', 'MARKING expected (co-MARKING atom)'),
                     ('CHSH+c', 'c', 'MONITORING expected (23.09x)'),
                     ('CHSH+k', 'k', 'THERMAL expected'),
                     ('CHSH+d', 'd', 'MARKING expected (co-MARKING atom)')]

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

    mark_enrich = enrichments.get('MARKING', 0)
    mon_enrich = enrichments.get('MONITORING', 0)

    p1 = mark_f * 100 >= 30.0
    print(f"  [{'PASS' if p1 else 'FAIL'}] P1: CHSH+f MARKING >= 30%: "
          f"{mark_f*100:.1f}%")

    p2 = mark_enrich >= 1.3 or combined_ratio >= 1.3
    print(f"  [{'PASS' if p2 else 'FAIL'}] P2: MARKING enrich >= 1.3x OR MARK+MON enrich >= 1.3x: "
          f"MARKING={mark_enrich:.2f}x, MARK+MON={combined_ratio:.2f}x")

    # Positive control: CHSH+k THERMAL enrichment
    total_k = group_totals['CHSH+k']
    if total_k > 0 and total_all > 0:
        thermal_k = groups['CHSH+k']['THERMAL'] / total_k
        thermal_all = groups['CHSH+all']['THERMAL'] / total_all
        k_thermal_enrich = thermal_k / thermal_all if thermal_all > 0 else 0
        ctrl_pass = k_thermal_enrich >= 1.3
        print(f"  [{'PASS' if ctrl_pass else 'FAIL'}] Control: CHSH+k THERMAL enrichment: "
              f"{k_thermal_enrich:.2f}x (expected >= 1.3x)")

    # Positive control: CHSH+p MARKING enrichment
    total_p = group_totals['CHSH+p']
    if total_p > 0 and total_all > 0:
        mark_p = groups['CHSH+p']['MARKING'] / total_p
        mark_all = groups['CHSH+all']['MARKING'] / total_all
        p_mark_enrich = mark_p / mark_all if mark_all > 0 else 0
        ctrl_pass2 = p_mark_enrich >= 1.0
        print(f"  [{'PASS' if ctrl_pass2 else 'FAIL'}] Control: CHSH+p MARKING enrichment: "
              f"{p_mark_enrich:.2f}x (expected >= 1.0x)")

    overall = p1 and p2
    print()
    print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
    if overall:
        print("  CHSH+f compounds confirm MARKING enrichment")
    else:
        print("  CHSH+f compounds do NOT confirm predicted enrichment pattern")
        if not p1:
            print(f"    MARKING only {mark_f*100:.1f}% (needed >= 30%)")
        if not p2:
            print(f"    Neither MARKING ({mark_enrich:.2f}x) nor MARK+MON ({combined_ratio:.2f}x) "
                  f"reached 1.3x enrichment")

    # Sparsity warning
    print()
    print("-" * 75)
    print("NOTE: f-atom sparsity")
    print("-" * 75)
    print()
    print(f"  f has only 215 total MIDDLE occurrences (17 standalone tokens).")
    print(f"  CHSH+f group has N={total_f} tokens.")
    if total_f < 20:
        print(f"  WARNING: Very small sample -- results are DIRECTIONAL, not robust.")
    elif total_f < 50:
        print(f"  CAUTION: Small sample -- interpret with care.")
    else:
        print(f"  Sample size adequate for category distribution testing.")


if __name__ == '__main__':
    main()
