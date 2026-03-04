#!/usr/bin/env python3
"""
S-S5: s->h junction enrichment analysis

C1216 says s->h junction is 8.1x enriched (81 observed vs 10 expected).
Test whether this junction produces MONITORING+STAGING compounds.

Method:
1. For each Currier B token, extract MIDDLE
2. For MIDDLEs with length >= 2, identify all consecutive character pairs (junctions)
3. For each junction pair (a, b), count how many times it appears
4. Focus on s->h junction: collect all MIDDLEs containing 's' immediately followed by 'h'
5. For each such MIDDLE, classify its category
6. Compute MONITORING+STAGING fraction of s->h-containing MIDDLEs

Also compute:
- Cross-token s->h: s-terminal tokens followed by h-initial tokens. How enriched?
- Intra-token vs cross-token ratio

Predictions:
- s->h junction count >= 60 (conservative of C1216's 81)
- s->h compound MIDDLEs: MONITORING+STAGING >= 50%
- Cross-token s-terminal to h-initial enrichment < 2.0x
- Intra/cross ratio >= 5:1

Pass: junction count >= 60 AND MON+STAGING >= 50%
Controls: c->h junction (380 from Phase 499), p->c junction (306 from Phase 500)

KEY DISCRIMINANT: If MONITORING > 70% in sh-family compounds, favors H2 "sift".
If 40-65%, consistent with H1 "sequence".
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
    print("S-S5: s->h junction enrichment analysis")
    print("=" * 75)

    # ---- PASS 1: Count all junctions and category profiles ----
    junction_counts = Counter()                  # (char_a, char_b) -> count
    junction_cat_counts = defaultdict(Counter)   # (char_a, char_b) -> {cat: count}
    junction_middles = defaultdict(Counter)       # (char_a, char_b) -> {middle: count}
    global_cat_counts = Counter()
    global_total = 0

    # Per-MIDDLE category tracking for s->h detail
    sh_middle_cats = defaultdict(Counter)
    sh_middle_totals = Counter()

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

                # Track s->h detail
                if pair == ('s', 'h'):
                    sh_middle_cats[mid][cat] += 1
                    sh_middle_totals[mid] += 1

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
        marker = " <-- TARGET" if (a, b) == ('s', 'h') else ""
        print(f"  {a}->{b:<6} {count:>8} {freq:>7.2f}% {top_cat:>14}{marker}")

    # Show s->h rank if not in top 20
    sh_count = junction_counts.get(('s', 'h'), 0)
    sh_rank = sorted(junction_counts.values(), reverse=True).index(sh_count) + 1 if sh_count > 0 else 'N/A'
    if sh_count > 0 and ('s', 'h') not in [p for p, _ in junction_counts.most_common(20)]:
        print(f"  ...")
        print(f"  s->h     {sh_count:>8} {sh_count/total_junctions*100:>7.2f}%  (rank {sh_rank})")

    # ---- TEST 2: s->h junction detail ----
    print()
    print("-" * 75)
    print("TEST 2: s->h junction detail")
    print("-" * 75)
    print()

    print(f"s->h junction count: {sh_count}")
    print(f"  (Prediction: >= 60, from C1216's 81)")
    print()

    # Enrichment vs expected
    # Expected = freq(s_as_first) * freq(h_as_second) * total_junctions
    char_first_freq = Counter()
    char_second_freq = Counter()
    for (a, b), count in junction_counts.items():
        char_first_freq[a] += count
        char_second_freq[b] += count

    s_first_rate = char_first_freq.get('s', 0) / total_junctions if total_junctions > 0 else 0
    h_second_rate = char_second_freq.get('h', 0) / total_junctions if total_junctions > 0 else 0
    expected_sh = s_first_rate * h_second_rate * total_junctions
    enrichment_sh = sh_count / expected_sh if expected_sh > 0 else 0

    print(f"  Observed: {sh_count}")
    print(f"  Expected (from marginal freqs): {expected_sh:.1f}")
    print(f"  Enrichment: {enrichment_sh:.2f}x")
    print()

    # Category profile of s->h MIDDLEs
    sh_total = sum(sh_middle_totals.values())
    sh_cat_agg = Counter()
    for mid, cats in sh_middle_cats.items():
        for cat, n in cats.items():
            sh_cat_agg[cat] += n

    print(f"s->h-containing MIDDLEs category profile (N={sh_total}):")
    print(f"{'Category':<15} {'Count':>6} {'Frac%':>8} {'Global%':>9} {'Enrich':>8}")
    print("-" * 55)
    sh_mon_staging = 0
    sh_mon_only = 0
    for cat in CATEGORIES:
        n = sh_cat_agg.get(cat, 0)
        frac = n / sh_total if sh_total > 0 else 0
        g_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
        enrich = frac / g_frac if g_frac > 0 else 0
        if cat in ('MONITORING', 'STAGING'):
            sh_mon_staging += frac
        if cat == 'MONITORING':
            sh_mon_only = frac
        marker = "  <--" if cat in ('MONITORING', 'STAGING') else ""
        print(f"  {cat:<13} {n:>6} {frac*100:>7.1f}% {g_frac*100:>8.1f}% {enrich:>7.2f}x{marker}")

    print()
    print(f"  Combined MONITORING+STAGING: {sh_mon_staging*100:.1f}%")
    print(f"  MONITORING alone: {sh_mon_only*100:.1f}%")
    print()
    print(f"  KEY DISCRIMINANT:")
    if sh_mon_only > 0.70:
        print(f"    MONITORING > 70% ({sh_mon_only*100:.1f}%) --> favors H2 'sift'")
    elif sh_mon_only >= 0.40:
        print(f"    MONITORING 40-65% ({sh_mon_only*100:.1f}%) --> consistent with H1 'sequence'")
    else:
        print(f"    MONITORING < 40% ({sh_mon_only*100:.1f}%) --> neither H1 nor H2 clearly supported")

    # Per-MIDDLE detail
    print()
    print(f"  Per-MIDDLE breakdown (s->h containing):")
    print(f"  {'MIDDLE':<12} {'N':>5} {'Category':<15} {'MON+STAG%':>10}")
    print("  " + "-" * 48)
    for mid, total in sorted(sh_middle_totals.items(), key=lambda x: -x[1]):
        cats = sh_middle_cats[mid]
        top_cat = cats.most_common(1)[0][0] if cats else 'N/A'
        ms = cats.get('MONITORING', 0) + cats.get('STAGING', 0)
        ms_pct = ms / total * 100 if total > 0 else 0
        print(f"  {mid:<12} {total:>5} {top_cat:<15} {ms_pct:>9.1f}%")

    # ---- TEST 3: Cross-token s->h analysis ----
    print()
    print("-" * 75)
    print("TEST 3: Cross-token s-terminal to h-initial enrichment")
    print("-" * 75)
    print()

    # Count cross-token transitions
    cross_counts = Counter()       # (terminal_char, initial_char) -> count
    total_cross = 0
    cross_s_terminal = 0
    cross_h_initial = 0

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
            if terminal == 's':
                cross_s_terminal += 1
            if initial == 'h':
                cross_h_initial += 1

    cross_sh = cross_counts.get(('s', 'h'), 0)
    expected_cross_sh = (cross_s_terminal / total_cross * cross_h_initial) if total_cross > 0 else 0
    cross_enrichment = cross_sh / expected_cross_sh if expected_cross_sh > 0 else 0

    print(f"Total cross-token transitions: {total_cross}")
    print(f"s-terminal tokens: {cross_s_terminal} ({cross_s_terminal/total_cross*100:.2f}%)")
    print(f"h-initial tokens:  {cross_h_initial} ({cross_h_initial/total_cross*100:.2f}%)")
    print(f"Cross s->h count:  {cross_sh}")
    print(f"Expected:          {expected_cross_sh:.1f}")
    print(f"Cross enrichment:  {cross_enrichment:.2f}x")
    print()

    # Intra vs cross ratio
    intra_sh = sh_count
    ratio_intra_cross = intra_sh / cross_sh if cross_sh > 0 else float('inf')
    print(f"Intra-token s->h: {intra_sh}")
    print(f"Cross-token s->h: {cross_sh}")
    print(f"Intra/Cross ratio: {ratio_intra_cross:.2f}x")

    # ---- TEST 4: Controls ----
    print()
    print("-" * 75)
    print("TEST 4: Control junctions")
    print("-" * 75)
    print()

    controls = [('c', 'h'), ('p', 'c'), ('e', 'k'), ('k', 'e')]
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
        ms = cats.get('MONITORING', 0) + cats.get('STAGING', 0)
        ms_pct = ms / cat_total * 100 if cat_total > 0 else 0

        print(f"  {a}->{b}: count={count}, expected={expected:.1f}, enrichment={enrich:.2f}x, "
              f"top_cat={top_cat}, MON+STAG={ms_pct:.1f}%")

    # ---- SUMMARY ----
    print()
    print("=" * 75)
    print("SUMMARY: S-S5 s->h junction enrichment")
    print("=" * 75)
    print()

    pass_count = sh_count >= 60
    pass_mon_staging = sh_mon_staging >= 0.50
    pass_cross_low = cross_enrichment < 2.0
    pass_ratio = ratio_intra_cross >= 5.0

    results = [
        ("P1: s->h junction count >= 60",
         pass_count,
         f"{sh_count} (enrichment {enrichment_sh:.2f}x)"),
        ("P2: s->h compound MON+STAGING >= 50%",
         pass_mon_staging,
         f"{sh_mon_staging*100:.1f}%"),
        ("P3: Cross-token s->h enrichment < 2.0x",
         pass_cross_low,
         f"{cross_enrichment:.2f}x"),
        ("P4: Intra/cross ratio >= 5:1",
         pass_ratio,
         f"{ratio_intra_cross:.2f}x"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_count and pass_mon_staging
    print()
    print(f"  PRIMARY CRITERION (count >= 60 AND MON+STAGING >= 50%): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
