"""
P-C10: CHSH+c compound enrichment

Tests whether CHSH-prefixed tokens with c-containing MIDDLEs are enriched
for MONITORING+MARKING categories.

Predictions:
- CHSH+c tokens: MONITORING+MARKING >= 40%
- MONITORING enrichment >= 2.0x (relative to CHSH+non-c)
- Controls: CHSH+o should be STAGING-enriched, CHSH+k should be THERMAL-enriched

Based on:
- {c,h} monitoring cluster r=+0.746 (C1207)
- c→h obligatory junction 100% (C1216)
- CategoryClassifier maps c → MARKING
- c standalone: 90% -hy suffix lock
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
CHSH_PREFIXES = {'ch', 'sh'}


def main():
    print("=" * 70)
    print("P-C10: CHSH+c compound enrichment")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # --- Collect all prefixed CHSH tokens ---
    # Groups: CHSH+c, CHSH+non-c, CHSH+o, CHSH+k
    groups = {
        'CHSH+c': defaultdict(int),
        'CHSH+non-c': defaultdict(int),
        'CHSH+o': defaultdict(int),
        'CHSH+k': defaultdict(int),
        'CHSH+all': defaultdict(int),
    }
    group_totals = defaultdict(int)
    group_middles = defaultdict(lambda: defaultdict(int))

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

        # Classify by MIDDLE content
        has_c = 'c' in mid
        has_o = 'o' in mid
        has_k = 'k' in mid

        groups['CHSH+all'][cat] += 1
        group_totals['CHSH+all'] += 1

        if has_c:
            groups['CHSH+c'][cat] += 1
            group_totals['CHSH+c'] += 1
            group_middles['CHSH+c'][mid] += 1
        else:
            groups['CHSH+non-c'][cat] += 1
            group_totals['CHSH+non-c'] += 1

        if has_o:
            groups['CHSH+o'][cat] += 1
            group_totals['CHSH+o'] += 1

        if has_k:
            groups['CHSH+k'][cat] += 1
            group_totals['CHSH+k'] += 1

    # --- Category profile tables ---
    print("\n--- Category profiles for CHSH prefix groups ---\n")

    display_groups = ['CHSH+c', 'CHSH+non-c', 'CHSH+o', 'CHSH+k', 'CHSH+all']
    print(f"{'Group':<15} {'N':>6}", end="")
    for cat in CATEGORIES:
        print(f" {cat[:6]:>7}", end="")
    print()
    print("-" * (15 + 6 + len(CATEGORIES) * 8))

    for grp in display_groups:
        total = group_totals[grp]
        print(f"{grp:<15} {total:>6}", end="")
        for cat in CATEGORIES:
            rate = groups[grp][cat] / total * 100 if total > 0 else 0
            print(f" {rate:>6.1f}%", end="")
        print()

    # --- Enrichment ratios: CHSH+c vs CHSH+non-c ---
    print("\n--- Enrichment: CHSH+c vs CHSH+non-c ---\n")
    print(f"{'Category':<15} {'CHSH+c%':>8} {'non-c%':>8} {'Ratio':>8}")
    print("-" * 45)

    total_c = group_totals['CHSH+c']
    total_nc = group_totals['CHSH+non-c']

    enrichments = {}
    for cat in CATEGORIES:
        rate_c = groups['CHSH+c'][cat] / total_c if total_c > 0 else 0
        rate_nc = groups['CHSH+non-c'][cat] / total_nc if total_nc > 0 else 0
        ratio = rate_c / rate_nc if rate_nc > 0 else float('inf')
        enrichments[cat] = ratio
        print(f"{cat:<15} {rate_c * 100:>7.1f}% {rate_nc * 100:>7.1f}% {ratio:>7.2f}x")

    # --- Top CHSH+c compounds ---
    print("\n--- Top 15 CHSH+c MIDDLEs ---\n")
    sorted_mids = sorted(group_middles['CHSH+c'].items(), key=lambda x: -x[1])
    print(f"{'MIDDLE':<15} {'Count':>6} {'Category':<15}")
    print("-" * 40)
    for mid, count in sorted_mids[:15]:
        cat = cc.classify(mid)
        print(f"{mid:<15} {count:>6} {cat:<15}")

    # --- Controls ---
    print("\n--- Control: CHSH+o category profile ---\n")
    total_o = group_totals['CHSH+o']
    if total_o > 0:
        print(f"{'Category':<15} {'CHSH+o%':>8} {'all%':>8} {'Ratio':>8}")
        print("-" * 45)
        total_all = group_totals['CHSH+all']
        for cat in CATEGORIES:
            rate_o = groups['CHSH+o'][cat] / total_o if total_o > 0 else 0
            rate_all = groups['CHSH+all'][cat] / total_all if total_all > 0 else 0
            ratio = rate_o / rate_all if rate_all > 0 else float('inf')
            marker = " <-- STAGING" if cat == 'STAGING' and ratio > 1.3 else ""
            print(f"{cat:<15} {rate_o * 100:>7.1f}% {rate_all * 100:>7.1f}% {ratio:>7.2f}x{marker}")
    else:
        print("(No CHSH+o tokens found)")

    print("\n--- Control: CHSH+k category profile ---\n")
    total_k = group_totals['CHSH+k']
    if total_k > 0:
        print(f"{'Category':<15} {'CHSH+k%':>8} {'all%':>8} {'Ratio':>8}")
        print("-" * 45)
        total_all = group_totals['CHSH+all']
        for cat in CATEGORIES:
            rate_k = groups['CHSH+k'][cat] / total_k if total_k > 0 else 0
            rate_all = groups['CHSH+all'][cat] / total_all if total_all > 0 else 0
            ratio = rate_k / rate_all if rate_all > 0 else float('inf')
            marker = " <-- THERMAL" if cat == 'THERMAL' and ratio > 1.3 else ""
            print(f"{cat:<15} {rate_k * 100:>7.1f}% {rate_all * 100:>7.1f}% {ratio:>7.2f}x{marker}")
    else:
        print("(No CHSH+k tokens found)")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # P1: CHSH+c: MONITORING+MARKING >= 40%
    if total_c > 0:
        mon_mark_rate = (groups['CHSH+c']['MONITORING'] + groups['CHSH+c']['MARKING']) / total_c * 100
    else:
        mon_mark_rate = 0
    p1 = mon_mark_rate >= 40.0
    print(f"P1: CHSH+c MONITORING+MARKING = {mon_mark_rate:.1f}% >= 40%: {'PASS' if p1 else 'FAIL'}")

    # P2: MONITORING enrichment >= 2.0x
    mon_enrich = enrichments.get('MONITORING', 0)
    p2 = mon_enrich >= 2.0
    print(f"P2: MONITORING enrichment = {mon_enrich:.2f}x >= 2.0x: {'PASS' if p2 else 'FAIL'}")

    overall = p1 and p2
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    if overall:
        print("  CHSH+c compounds confirm MONITORING/MARKING enrichment")
    else:
        print("  CHSH+c compounds do NOT confirm predicted enrichment pattern")
        if not p1:
            print(f"  MONITORING+MARKING only {mon_mark_rate:.1f}% (needed >= 40%)")
        if not p2:
            print(f"  MONITORING enrichment only {mon_enrich:.2f}x (needed >= 2.0x)")


if __name__ == '__main__':
    main()
