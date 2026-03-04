#!/usr/bin/env python3
"""
P-O16: CHSH+o STAGING enrichment (ordnen hypothesis)

If o = "ordnen" (arrange/prepare), then CHSH-prefixed tokens carrying o-MIDDLEs
should be strongly enriched in STAGING compared to CHSH+non-o tokens.

The logic: ch/sh = monitoring/testing PREFIX + o = preparation MIDDLE should
produce monitoring-of-preparation = STAGING.

Tests:
1. Compare CHSH+o vs CHSH+non-o full category profiles
2. Compute enrichment ratios
3. Show top CHSH+o compounds with their categories
4. Compare to QO+o (energy channel should have different pattern)

Pass: STAGING enrichment >= 3.0x AND STAGING is #1 enriched category for CHSH+o
      relative to CHSH+non-o.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    CHSH_PREFIXES = {'ch', 'sh'}
    QO_PREFIXES = {'qo'}

    # Collect: PREFIX group x (o-in-middle vs not) -> category counts
    chsh_o_cats = defaultdict(int)
    chsh_o_total = 0
    chsh_nono_cats = defaultdict(int)
    chsh_nono_total = 0

    qo_o_cats = defaultdict(int)
    qo_o_total = 0
    qo_nono_cats = defaultdict(int)
    qo_nono_total = 0

    # Track individual CHSH+o compounds
    chsh_o_middles = defaultdict(int)
    chsh_o_mid_cats = defaultdict(lambda: defaultdict(int))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or not m.prefix:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        has_o = 'o' in m.middle

        if m.prefix in CHSH_PREFIXES:
            if has_o:
                chsh_o_cats[cat] += 1
                chsh_o_total += 1
                chsh_o_middles[m.middle] += 1
                chsh_o_mid_cats[m.middle][cat] += 1
            else:
                chsh_nono_cats[cat] += 1
                chsh_nono_total += 1

        elif m.prefix in QO_PREFIXES:
            if has_o:
                qo_o_cats[cat] += 1
                qo_o_total += 1
            else:
                qo_nono_cats[cat] += 1
                qo_nono_total += 1

    print("=" * 70)
    print("P-O16: CHSH+o STAGING enrichment (ordnen hypothesis)")
    print("=" * 70)
    print()
    print(f"CHSH+o tokens: {chsh_o_total}")
    print(f"CHSH+non-o tokens: {chsh_nono_total}")
    print(f"QO+o tokens: {qo_o_total}")
    print(f"QO+non-o tokens: {qo_nono_total}")
    print()

    # ---- TEST 1: CHSH+o vs CHSH+non-o category profiles ----
    print("-" * 70)
    print("TEST 1: CHSH+o vs CHSH+non-o category profiles")
    print("-" * 70)
    print()

    staging_enrich = 0
    enrichments = []

    print(f"{'Category':<15} {'CHSH+o%':>9} {'CHSH-o%':>9} {'Enrichment':>11} {'Rank':>5}")
    print("-" * 55)

    cat_enrichments = []
    for cat in CATEGORIES:
        o_frac = chsh_o_cats[cat] / chsh_o_total if chsh_o_total > 0 else 0
        nono_frac = chsh_nono_cats[cat] / chsh_nono_total if chsh_nono_total > 0 else 0
        enrich = o_frac / nono_frac if nono_frac > 0 else (999 if o_frac > 0 else 0)
        cat_enrichments.append((cat, o_frac, nono_frac, enrich))
        if cat == 'STAGING':
            staging_enrich = enrich

    # Sort by enrichment for ranking
    cat_enrichments.sort(key=lambda x: -x[3])
    staging_rank = None
    for rank, (cat, o_frac, nono_frac, enrich) in enumerate(cat_enrichments, 1):
        marker = ""
        if cat == 'STAGING':
            marker = " <-- TARGET"
            staging_rank = rank
        print(f"  {cat:<13} {o_frac*100:>8.2f}% {nono_frac*100:>8.2f}% {enrich:>10.3f}x  #{rank}{marker}")

    print()
    print(f"  STAGING enrichment: {staging_enrich:.3f}x")
    print(f"  STAGING rank among enriched categories: #{staging_rank}")

    # ---- TEST 2: QO+o comparison (control) ----
    print()
    print("-" * 70)
    print("TEST 2: QO+o vs QO+non-o (control -- different channel)")
    print("-" * 70)
    print()

    qo_staging_enrich = 0
    print(f"{'Category':<15} {'QO+o%':>9} {'QO-o%':>9} {'Enrichment':>11}")
    print("-" * 50)
    for cat in CATEGORIES:
        o_frac = qo_o_cats[cat] / qo_o_total if qo_o_total > 0 else 0
        nono_frac = qo_nono_cats[cat] / qo_nono_total if qo_nono_total > 0 else 0
        enrich = o_frac / nono_frac if nono_frac > 0 else (999 if o_frac > 0 else 0)
        marker = " <--" if cat == 'STAGING' else ""
        if cat == 'STAGING':
            qo_staging_enrich = enrich
        print(f"  {cat:<13} {o_frac*100:>8.2f}% {nono_frac*100:>8.2f}% {enrich:>10.3f}x{marker}")

    print()
    print(f"  QO+o STAGING enrichment: {qo_staging_enrich:.3f}x (compare to CHSH: {staging_enrich:.3f}x)")

    # ---- TEST 3: Top CHSH+o compounds ----
    print()
    print("-" * 70)
    print("TEST 3: Top CHSH+o compound MIDDLEs with categories")
    print("-" * 70)
    print()

    sorted_mids = sorted(chsh_o_middles.items(), key=lambda x: -x[1])[:20]
    print(f"{'MIDDLE':<12} {'Count':>6} {'TopCategory':>15} {'STAGING%':>9}")
    print("-" * 48)
    for mid, count in sorted_mids:
        top_cat = max(chsh_o_mid_cats[mid], key=chsh_o_mid_cats[mid].get) if chsh_o_mid_cats[mid] else 'N/A'
        stg_n = chsh_o_mid_cats[mid].get('STAGING', 0)
        stg_pct = stg_n / count * 100 if count > 0 else 0
        print(f"  {mid:<10} {count:>6} {top_cat:>15} {stg_pct:>8.1f}%")

    # ---- TEST 4: ch+o vs sh+o breakdown ----
    print()
    print("-" * 70)
    print("TEST 4: ch+o vs sh+o sister pair breakdown")
    print("-" * 70)
    print()

    # Rebuild per sister
    sister_o_cats = defaultdict(lambda: defaultdict(int))
    sister_o_totals = defaultdict(int)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle or not m.prefix:
            continue
        if m.prefix not in CHSH_PREFIXES:
            continue
        if 'o' not in m.middle:
            continue
        cat = cc.classify(m.middle)
        if cat is None:
            continue
        sister_o_cats[m.prefix][cat] += 1
        sister_o_totals[m.prefix] += 1

    for sister in ['ch', 'sh']:
        total = sister_o_totals[sister]
        print(f"  {sister}+o (N={total}):")
        if total > 0:
            for cat in CATEGORIES:
                n = sister_o_cats[sister].get(cat, 0)
                if n > 0:
                    print(f"    {cat:<15} {n:>5} ({n/total*100:>5.1f}%)")
        print()

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O16 CHSH+o STAGING enrichment (ordnen)")
    print("=" * 70)

    pass_enrich = staging_enrich >= 3.0
    pass_rank = staging_rank == 1 if staging_rank is not None else False
    pass_n = chsh_o_total >= 50  # Sufficient data

    results = [
        ("STAGING enrichment >= 3.0x", pass_enrich,
         f"{staging_enrich:.3f}x"),
        ("STAGING is #1 enriched category", pass_rank,
         f"rank #{staging_rank}" if staging_rank else "N/A"),
        ("Sufficient data (N >= 50)", pass_n,
         f"N = {chsh_o_total}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_enrich and pass_rank
    print()
    print(f"  PRIMARY CRITERION (STAGING >= 3.0x AND #1 enriched): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
