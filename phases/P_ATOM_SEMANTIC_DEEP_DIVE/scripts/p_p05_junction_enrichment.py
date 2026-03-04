#!/usr/bin/env python3
"""
P-P5: p->c junction enrichment analysis

C1216 says p->c junction is 8.1x enriched (121 observed vs 14.9 expected).
Test whether this junction produces MONITORING+MARKING compounds.

Method:
1. For each Currier B token, extract MIDDLE
2. For MIDDLEs with length >= 2, identify all consecutive character pairs (junctions)
3. For each junction pair (a, b), count how many times it appears
4. Focus on p->c junction: collect all MIDDLEs containing 'p' immediately followed by 'c'
5. For each such MIDDLE, classify its category
6. Compute MONITORING+MARKING fraction of p->c-containing MIDDLEs

Also compute:
- Cross-token p->c: p-terminal tokens followed by c-initial tokens. How enriched?
- Intra-token vs cross-token ratio

Predictions:
- p->c junction count >= 80 (from C1216's 121)
- p->c compound MIDDLEs: MONITORING+MARKING >= 60%
- Cross-token p-terminal to c-initial enrichment < 2.0x

Pass: junction count confirmed AND MON+MARK >= 60%
Controls: c->h junction (should be massive), o->l junction
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
    print("P-P5: p->c junction enrichment analysis")
    print("=" * 75)

    # ---- PASS 1: Count all junctions and category profiles ----
    junction_counts = Counter()                  # (char_a, char_b) -> count
    junction_cat_counts = defaultdict(Counter)   # (char_a, char_b) -> {cat: count}
    junction_middles = defaultdict(Counter)       # (char_a, char_b) -> {middle: count}
    global_cat_counts = Counter()
    global_total = 0

    # Per-MIDDLE category tracking for p->c detail
    pc_middle_cats = defaultdict(Counter)
    pc_middle_totals = Counter()

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

                # Track p->c detail
                if pair == ('p', 'c'):
                    pc_middle_cats[mid][cat] += 1
                    pc_middle_totals[mid] += 1

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
        marker = " <-- TARGET" if (a, b) == ('p', 'c') else ""
        print(f"  {a}->{b:<6} {count:>8} {freq:>7.2f}% {top_cat:>14}{marker}")

    # ---- TEST 2: p->c junction detail ----
    print()
    print("-" * 75)
    print("TEST 2: p->c junction detail")
    print("-" * 75)
    print()

    pc_count = junction_counts.get(('p', 'c'), 0)
    print(f"p->c junction count: {pc_count}")
    print(f"  (Prediction: >= 80, from C1216's 121)")
    print()

    # Enrichment vs expected
    # Expected = freq(p) * freq(c) * total_junctions
    char_freq = Counter()
    for (a, b), count in junction_counts.items():
        char_freq[a] += count
        char_freq[b] += count
    total_char_occ = sum(char_freq.values())
    p_freq = char_freq.get('p', 0) / total_char_occ if total_char_occ > 0 else 0
    c_freq = char_freq.get('c', 0) / total_char_occ if total_char_occ > 0 else 0
    expected_pc = p_freq * c_freq * total_junctions
    enrichment_pc = pc_count / expected_pc if expected_pc > 0 else 0

    print(f"  Observed: {pc_count}")
    print(f"  Expected (from marginal freqs): {expected_pc:.1f}")
    print(f"  Enrichment: {enrichment_pc:.2f}x")
    print()

    # Category profile of p->c MIDDLEs
    pc_total = sum(pc_middle_totals.values())
    pc_cat_agg = Counter()
    for mid, cats in pc_middle_cats.items():
        for cat, n in cats.items():
            pc_cat_agg[cat] += n

    print(f"p->c-containing MIDDLEs category profile (N={pc_total}):")
    print(f"{'Category':<15} {'Count':>6} {'Frac%':>8} {'Global%':>9} {'Enrich':>8}")
    print("-" * 55)
    pc_mon_mark = 0
    for cat in CATEGORIES:
        n = pc_cat_agg.get(cat, 0)
        frac = n / pc_total if pc_total > 0 else 0
        g_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
        enrich = frac / g_frac if g_frac > 0 else 0
        if cat in ('MONITORING', 'MARKING'):
            pc_mon_mark += frac
        marker = "  <--" if cat in ('MONITORING', 'MARKING') else ""
        print(f"  {cat:<13} {n:>6} {frac*100:>7.1f}% {g_frac*100:>8.1f}% {enrich:>7.2f}x{marker}")

    print()
    print(f"  Combined MONITORING+MARKING: {pc_mon_mark*100:.1f}%")

    # Per-MIDDLE detail
    print()
    print(f"  Per-MIDDLE breakdown (p->c containing):")
    print(f"  {'MIDDLE':<12} {'N':>5} {'Category':<15} {'MON+MARK%':>10}")
    print("  " + "-" * 48)
    for mid, total in sorted(pc_middle_totals.items(), key=lambda x: -x[1]):
        cats = pc_middle_cats[mid]
        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        mm = cats.get('MONITORING', 0) + cats.get('MARKING', 0)
        mm_pct = mm / total * 100 if total > 0 else 0
        print(f"  {mid:<12} {total:>5} {top_cat:<15} {mm_pct:>9.1f}%")

    # ---- TEST 3: Cross-token p->c analysis ----
    print()
    print("-" * 75)
    print("TEST 3: Cross-token p-terminal to c-initial enrichment")
    print("-" * 75)
    print()

    # Count cross-token transitions
    cross_counts = Counter()       # (terminal_char, initial_char) -> count
    total_cross = 0
    cross_p_terminal = 0
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
            if terminal == 'p':
                cross_p_terminal += 1
            if initial == 'c':
                cross_c_initial += 1

    cross_pc = cross_counts.get(('p', 'c'), 0)
    expected_cross_pc = (cross_p_terminal / total_cross * cross_c_initial) if total_cross > 0 else 0
    cross_enrichment = cross_pc / expected_cross_pc if expected_cross_pc > 0 else 0

    print(f"Total cross-token transitions: {total_cross}")
    print(f"p-terminal tokens: {cross_p_terminal} ({cross_p_terminal/total_cross*100:.1f}%)")
    print(f"c-initial tokens:  {cross_c_initial} ({cross_c_initial/total_cross*100:.1f}%)")
    print(f"Cross p->c count:  {cross_pc}")
    print(f"Expected:          {expected_cross_pc:.1f}")
    print(f"Cross enrichment:  {cross_enrichment:.2f}x")
    print()

    # Intra vs cross ratio
    intra_pc = pc_count
    ratio_intra_cross = intra_pc / cross_pc if cross_pc > 0 else float('inf')
    print(f"Intra-token p->c: {intra_pc}")
    print(f"Cross-token p->c: {cross_pc}")
    print(f"Intra/Cross ratio: {ratio_intra_cross:.2f}x")

    # ---- TEST 4: Controls ----
    print()
    print("-" * 75)
    print("TEST 4: Control junctions")
    print("-" * 75)
    print()

    controls = [('c', 'h'), ('o', 'l'), ('e', 'k'), ('k', 'e')]
    for a, b in controls:
        count = junction_counts.get((a, b), 0)
        cats = junction_cat_counts.get((a, b), Counter())
        cat_total = sum(cats.values())

        # Enrichment
        a_freq = char_freq.get(a, 0) / total_char_occ if total_char_occ > 0 else 0
        b_freq = char_freq.get(b, 0) / total_char_occ if total_char_occ > 0 else 0
        expected = a_freq * b_freq * total_junctions
        enrich = count / expected if expected > 0 else 0

        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        mm = cats.get('MONITORING', 0) + cats.get('MARKING', 0)
        mm_pct = mm / cat_total * 100 if cat_total > 0 else 0

        print(f"  {a}->{b}: count={count}, expected={expected:.1f}, enrichment={enrich:.2f}x, "
              f"top_cat={top_cat}, MON+MARK={mm_pct:.1f}%")

    # ---- SUMMARY ----
    print()
    print("=" * 75)
    print("SUMMARY: P-P5 p->c junction enrichment")
    print("=" * 75)
    print()

    pass_count = pc_count >= 80
    pass_mon_mark = pc_mon_mark >= 0.60
    pass_cross_low = cross_enrichment < 2.0

    results = [
        ("P1: p->c junction count >= 80",
         pass_count,
         f"{pc_count} (enrichment {enrichment_pc:.2f}x)"),
        ("P2: p->c compound MON+MARK >= 60%",
         pass_mon_mark,
         f"{pc_mon_mark*100:.1f}%"),
        ("P3: Cross-token p->c enrichment < 2.0x",
         pass_cross_low,
         f"{cross_enrichment:.2f}x"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_count and pass_mon_mark
    print()
    print(f"  PRIMARY CRITERION (count >= 80 AND MON+MARK >= 60%): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
