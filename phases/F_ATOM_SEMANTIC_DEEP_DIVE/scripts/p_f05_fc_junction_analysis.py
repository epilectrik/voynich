#!/usr/bin/env python3
"""
F-F5: f->c junction enrichment analysis

f is a MARKING atom (gloss: "flag"). The dominant compound is fch (23 tokens,
glossed "note"). Most multi-atom f-compounds contain the c+h chain (fch, ofch,
cfh, efch), suggesting f->c is a structurally important junction.

Method:
1. For each Currier B token, extract MIDDLE
2. For MIDDLEs with length >= 2, identify all consecutive character pairs (junctions)
3. Focus on f->c junction: collect all MIDDLEs containing 'f' immediately followed by 'c'
4. For each such MIDDLE, classify its category
5. Compute MARKING fraction of f->c-containing MIDDLEs

Also compute:
- Cross-token f->c: f-terminal tokens followed by c-initial tokens. How enriched?
- Intra-token vs cross-token ratio

Predictions:
- f->c junction enrichment >= 2.0x
- f->c compound MIDDLEs: MARKING >= 50%
- Cross-token f->c enrichment < 2.0x
- Intra/cross ratio >= 5:1

Pass: junction enrichment >= 2.0x AND MARKING >= 50%
Controls: s->h junction (13.16x from S-atom), c->h junction (380 from Phase 499),
          p->c junction (306 from Phase 500)

KEY DISCRIMINANT: If MARKING > 60% in fc-compounds, confirms "flag" as annotation
trigger feeding into "check" (c) chains. If < 40%, f may have a different function
in compound context.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


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


def chi2_1df_p(chi2_val):
    """Approximate p-value for chi-square with 1 df."""
    if chi2_val <= 0:
        return 1.0
    z = math.sqrt(chi2_val)
    return 2.0 * (1.0 - normal_cdf(z))


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("F-F5: f->c junction enrichment analysis")
    print("=" * 75)

    # ---- PASS 1: Count all junctions and category profiles ----
    junction_counts = Counter()                  # (char_a, char_b) -> count
    junction_cat_counts = defaultdict(Counter)   # (char_a, char_b) -> {cat: count}
    junction_middles = defaultdict(Counter)       # (char_a, char_b) -> {middle: count}
    global_cat_counts = Counter()
    global_total = 0

    # Per-MIDDLE category tracking for f->c detail
    fc_middle_cats = defaultdict(Counter)
    fc_middle_totals = Counter()

    # For cross-token analysis: track terminal/initial chars per line
    line_tokens = defaultdict(list)  # (folio, line) -> [(middle, cat), ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        mid = m.middle
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        global_cat_counts[cat] += 1
        global_total += 1

        key = (token.folio, token.line)
        line_tokens[key].append((mid, cat))

        # Count all intra-token junctions
        if len(mid) >= 2:
            for i in range(len(mid) - 1):
                pair = (mid[i], mid[i + 1])
                junction_counts[pair] += 1
                junction_cat_counts[pair][cat] += 1
                junction_middles[pair][mid] += 1

                # Track f->c detail
                if pair == ('f', 'c'):
                    fc_middle_cats[mid][cat] += 1
                    fc_middle_totals[mid] += 1

    # ---- TEST 1: Junction census ----
    print()
    print("-" * 75)
    print("TEST 1: Junction census (all intra-token character pairs)")
    print("-" * 75)
    print()

    total_junctions = sum(junction_counts.values())
    unique_junctions = len(junction_counts)
    print(f"Total junctions: {total_junctions}")
    print(f"Unique junction types: {unique_junctions}")
    print()

    # Show top 20 junctions by count
    print(f"{'Junction':<10} {'Count':>8} {'Freq%':>8} {'TopCat':>14}")
    print("-" * 45)
    for (a, b), count in junction_counts.most_common(20):
        freq = count / total_junctions * 100
        cats = junction_cat_counts[(a, b)]
        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        marker = " <-- TARGET" if (a, b) == ('f', 'c') else ""
        print(f"  {a}->{b:<6} {count:>8} {freq:>7.2f}% {top_cat:>14}{marker}")

    # Show f->c rank if not in top 20
    fc_count = junction_counts.get(('f', 'c'), 0)
    ranked = sorted(junction_counts.values(), reverse=True)
    fc_rank = ranked.index(fc_count) + 1 if fc_count > 0 and fc_count in ranked else 'N/A'
    top20_pairs = [p for p, _ in junction_counts.most_common(20)]
    if fc_count > 0 and ('f', 'c') not in top20_pairs:
        print(f"  ...")
        print(f"  f->c     {fc_count:>8} {fc_count/total_junctions*100:>7.2f}%  (rank {fc_rank})")

    # Also show all f-involving junctions
    print()
    print("  All f-involving junctions:")
    f_junctions = [(pair, cnt) for pair, cnt in junction_counts.items()
                   if 'f' in pair]
    f_junctions.sort(key=lambda x: -x[1])
    for (a, b), count in f_junctions:
        cats = junction_cat_counts[(a, b)]
        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        marker = " <-- TARGET" if (a, b) == ('f', 'c') else ""
        print(f"    {a}->{b}: {count:>5}  top_cat={top_cat}{marker}")

    # ---- TEST 2: f->c junction detail ----
    print()
    print("-" * 75)
    print("TEST 2: f->c junction detail")
    print("-" * 75)
    print()

    print(f"f->c junction count: {fc_count}")
    print()

    # Enrichment vs expected
    char_first_freq = Counter()
    char_second_freq = Counter()
    for (a, b), count in junction_counts.items():
        char_first_freq[a] += count
        char_second_freq[b] += count

    f_first_rate = char_first_freq.get('f', 0) / total_junctions if total_junctions > 0 else 0
    c_second_rate = char_second_freq.get('c', 0) / total_junctions if total_junctions > 0 else 0
    expected_fc = f_first_rate * c_second_rate * total_junctions
    enrichment_fc = fc_count / expected_fc if expected_fc > 0 else 0

    print(f"  f as first in junction:  {char_first_freq.get('f', 0)} ({f_first_rate*100:.2f}%)")
    print(f"  c as second in junction: {char_second_freq.get('c', 0)} ({c_second_rate*100:.2f}%)")
    print(f"  Observed f->c: {fc_count}")
    print(f"  Expected (from marginal freqs): {expected_fc:.1f}")
    print(f"  Enrichment: {enrichment_fc:.2f}x")
    print(f"  (Prediction: >= 2.0x)")
    print()

    # Category profile of f->c MIDDLEs
    fc_total = sum(fc_middle_totals.values())
    fc_cat_agg = Counter()
    for mid, cats in fc_middle_cats.items():
        for cat, n in cats.items():
            fc_cat_agg[cat] += n

    print(f"f->c-containing MIDDLEs category profile (N={fc_total}):")
    print(f"{'Category':<15} {'Count':>6} {'Frac%':>8} {'Global%':>9} {'Enrich':>8}")
    print("-" * 55)
    fc_marking = 0
    for cat in CATEGORIES:
        n = fc_cat_agg.get(cat, 0)
        frac = n / fc_total if fc_total > 0 else 0
        g_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
        enrich = frac / g_frac if g_frac > 0 else 0
        if cat == 'MARKING':
            fc_marking = frac
        marker = "  <--" if cat == 'MARKING' else ""
        print(f"  {cat:<13} {n:>6} {frac*100:>7.1f}% {g_frac*100:>8.1f}% {enrich:>7.2f}x{marker}")

    print()
    print(f"  MARKING: {fc_marking*100:.1f}%")
    print(f"  (Prediction: >= 50%)")
    print()
    print(f"  KEY DISCRIMINANT:")
    if fc_marking > 0.60:
        print(f"    MARKING > 60% ({fc_marking*100:.1f}%) --> f->c is annotation trigger")
    elif fc_marking >= 0.40:
        print(f"    MARKING 40-60% ({fc_marking*100:.1f}%) --> partially supports MARKING role")
    else:
        print(f"    MARKING < 40% ({fc_marking*100:.1f}%) --> f may shift function in compound context")

    # Per-MIDDLE detail
    print()
    print(f"  Per-MIDDLE breakdown (f->c containing):")
    print(f"  {'MIDDLE':<12} {'N':>5} {'Category':<15} {'MARKING%':>10}")
    print("  " + "-" * 48)
    for mid, total in sorted(fc_middle_totals.items(), key=lambda x: -x[1]):
        cats = fc_middle_cats[mid]
        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        mark = cats.get('MARKING', 0)
        mark_pct = mark / total * 100 if total > 0 else 0
        print(f"  {mid:<12} {total:>5} {top_cat:<15} {mark_pct:>9.1f}%")

    # ---- TEST 3: Cross-token f->c analysis ----
    print()
    print("-" * 75)
    print("TEST 3: Cross-token f-terminal to c-initial enrichment")
    print("-" * 75)
    print()

    # Count cross-token transitions
    cross_counts = Counter()       # (terminal_char, initial_char) -> count
    total_cross = 0
    cross_f_terminal = 0
    cross_c_initial = 0

    for key in sorted(line_tokens.keys()):
        tokens = line_tokens[key]
        for i in range(len(tokens) - 1):
            mid_a = tokens[i][0]
            mid_b = tokens[i + 1][0]
            if not mid_a or not mid_b:
                continue
            terminal = mid_a[-1]
            initial = mid_b[0]
            cross_counts[(terminal, initial)] += 1
            total_cross += 1
            if terminal == 'f':
                cross_f_terminal += 1
            if initial == 'c':
                cross_c_initial += 1

    cross_fc = cross_counts.get(('f', 'c'), 0)
    expected_cross_fc = (cross_f_terminal / total_cross * cross_c_initial) if total_cross > 0 else 0
    cross_enrichment = cross_fc / expected_cross_fc if expected_cross_fc > 0 else 0

    print(f"Total cross-token transitions: {total_cross}")
    print(f"f-terminal tokens: {cross_f_terminal} ({cross_f_terminal/total_cross*100:.2f}%)" if total_cross > 0 else "N/A")
    print(f"c-initial tokens:  {cross_c_initial} ({cross_c_initial/total_cross*100:.2f}%)" if total_cross > 0 else "N/A")
    print(f"Cross f->c count:  {cross_fc}")
    print(f"Expected:          {expected_cross_fc:.1f}")
    print(f"Cross enrichment:  {cross_enrichment:.2f}x")
    print()

    # Intra vs cross ratio
    intra_fc = fc_count
    ratio_intra_cross = intra_fc / cross_fc if cross_fc > 0 else float('inf')
    print(f"Intra-token f->c: {intra_fc}")
    print(f"Cross-token f->c: {cross_fc}")
    print(f"Intra/Cross ratio: {ratio_intra_cross:.2f}x")

    # ---- TEST 4: Controls ----
    print()
    print("-" * 75)
    print("TEST 4: Control junctions")
    print("-" * 75)
    print()

    controls = [('s', 'h'), ('c', 'h'), ('p', 'c'), ('e', 'k'), ('k', 'e')]
    for a, b in controls:
        count = junction_counts.get((a, b), 0)
        cats = junction_cat_counts.get((a, b), Counter())
        cat_total = sum(cats.values())

        # Enrichment
        a_first = char_first_freq.get(a, 0) / total_junctions if total_junctions > 0 else 0
        b_second = char_second_freq.get(b, 0) / total_junctions if total_junctions > 0 else 0
        expected = a_first * b_second * total_junctions
        enrich = count / expected if expected > 0 else 0

        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        mark_n = cats.get('MARKING', 0)
        mark_pct = mark_n / cat_total * 100 if cat_total > 0 else 0

        print(f"  {a}->{b}: count={count}, expected={expected:.1f}, enrichment={enrich:.2f}x, "
              f"top_cat={top_cat}, MARKING={mark_pct:.1f}%")

    # ---- SUMMARY ----
    print()
    print("=" * 75)
    print("SUMMARY: F-F5 f->c junction enrichment")
    print("=" * 75)
    print()

    pass_enrichment = enrichment_fc >= 2.0
    pass_marking = fc_marking >= 0.50
    pass_cross_low = cross_enrichment < 2.0
    pass_ratio = ratio_intra_cross >= 5.0

    results = [
        ("P1: f->c junction enrichment >= 2.0x",
         pass_enrichment,
         f"{enrichment_fc:.2f}x (count={fc_count}, expected={expected_fc:.1f})"),
        ("P2: f->c compound MARKING >= 50%",
         pass_marking,
         f"{fc_marking*100:.1f}%"),
        ("P3: Cross-token f->c enrichment < 2.0x",
         pass_cross_low,
         f"{cross_enrichment:.2f}x"),
        ("P4: Intra/cross ratio >= 5:1",
         pass_ratio,
         f"{ratio_intra_cross:.2f}x"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_enrichment and pass_marking
    print()
    print(f"  PRIMARY CRITERION (enrichment >= 2.0x AND MARKING >= 50%): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
