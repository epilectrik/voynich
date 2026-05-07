#!/usr/bin/env python3
"""
T4: Section x order-constraint magnitude.

Hypothesis: per-folio z_mu (from T2) differs across sections.
Specifically predict mean(z_mu_B) < mean(z_mu_H) — Currier B section
more order-constrained than Herbal section even after vocabulary normalization.

Pass: Kruskal-Wallis p<0.05 AND post-hoc B-vs-H p<0.05 AND mean(z_mu_B) < mean(z_mu_H).
"""
import sys
import json
import math
import statistics
from pathlib import Path
from collections import defaultdict


def kruskal_wallis(groups):
    """
    Kruskal-Wallis H test for k>=2 groups.
    Returns (H, df, p_approx).

    groups is a list of lists.
    """
    all_values = []
    for i, g in enumerate(groups):
        for v in g:
            all_values.append((v, i))
    all_values.sort(key=lambda x: x[0])

    # Average ranks for ties
    ranks = [0.0] * len(all_values)
    i = 0
    while i < len(all_values):
        j = i
        while j < len(all_values) and all_values[j][0] == all_values[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    rank_sums = defaultdict(float)
    n_per = defaultdict(int)
    for r, (_, gi) in zip(ranks, all_values):
        rank_sums[gi] += r
        n_per[gi] += 1

    N = len(all_values)
    H = 12.0 / (N * (N + 1)) * sum(
        (rank_sums[gi] ** 2) / n_per[gi] for gi in rank_sums
    ) - 3 * (N + 1)
    df = len(groups) - 1

    # Approximate p-value via chi-square survival
    # For df=3, P(X > H) ~ exp(-H/2) * something... use crude approximation
    # via incomplete gamma
    # Use scipy-free approximation: chi-square with df=3
    # Wilson-Hilferty: ((H/df)**(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df)) ~ N(0,1)
    if df > 0:
        z_wh = ((H / df) ** (1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        # P(Z > z_wh) one-sided upper tail
        p = 0.5 * (1 - math.erf(z_wh / math.sqrt(2)))
    else:
        p = 1.0
    return H, df, p


def mannwhitney_u(x, y):
    n_x, n_y = len(x), len(y)
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])

    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    rank_sum_x = sum(r for r, (_, label) in zip(ranks, combined) if label == 'x')
    u_x = rank_sum_x - n_x * (n_x + 1) / 2.0

    mean_u = n_x * n_y / 2.0
    std_u = math.sqrt(n_x * n_y * (n_x + n_y + 1) / 12.0)
    z = (u_x - mean_u) / std_u

    # two-sided p
    p_two = 2 * min(0.5 * (1 + math.erf(z / math.sqrt(2))),
                     0.5 * (1 - math.erf(z / math.sqrt(2))))
    return u_x, z, p_two


def main():
    in_path = Path(__file__).resolve().parent.parent / 'results' / 't2_per_folio_zscores.json'
    with open(in_path) as f:
        t2 = json.load(f)

    by_section = defaultdict(list)
    by_language = defaultdict(list)
    folio_section_lang = []
    for entry in t2['per_folio']:
        sec = entry.get('section', '?') or '?'
        lang = entry.get('language', '?') or '?'
        z = entry['z_mu']
        by_section[sec].append(z)
        by_language[lang].append(z)
        folio_section_lang.append({
            'folio': entry['folio'],
            'section': sec,
            'language': lang,
            'z_mu': z,
            'n_tokens': entry['n_tokens'],
        })

    print("Section labels found in transcript:")
    for sec in sorted(by_section.keys()):
        zs = by_section[sec]
        if len(zs) >= 1:
            mean_z = statistics.mean(zs)
            print(f"  {sec}: n={len(zs)} folios, mean z_mu = {mean_z:+.3f}")

    print("\nLanguage labels found:")
    for lang in sorted(by_language.keys()):
        zs = by_language[lang]
        if len(zs) >= 1:
            mean_z = statistics.mean(zs)
            print(f"  {lang}: n={len(zs)} folios, mean z_mu = {mean_z:+.3f}")

    # T4: Kruskal-Wallis across sections with at least 5 folios
    eligible = {sec: zs for sec, zs in by_section.items() if len(zs) >= 5}
    print(f"\nSections with >=5 folios for KW test: {sorted(eligible.keys())}")
    section_groups = [eligible[s] for s in sorted(eligible.keys())]
    H_stat, df, p_kw = kruskal_wallis(section_groups)
    print(f"  Kruskal-Wallis H = {H_stat:.3f}, df = {df}, p = {p_kw:.4f}")

    # Post-hoc: B vs H if both present
    b_zs = by_section.get('B', [])
    h_zs = by_section.get('H', [])
    if len(b_zs) >= 5 and len(h_zs) >= 5:
        mean_b = statistics.mean(b_zs)
        mean_h = statistics.mean(h_zs)
        u, z, p_bh = mannwhitney_u(b_zs, h_zs)
        print(f"\n  Post-hoc B vs H:")
        print(f"    mean z_mu_B = {mean_b:+.3f} (n={len(b_zs)})")
        print(f"    mean z_mu_H = {mean_h:+.3f} (n={len(h_zs)})")
        print(f"    MWU U_B = {u:.1f}, z = {z:.2f}, two-sided p = {p_bh:.4f}")

        pass_kw = p_kw < 0.05
        pass_bh = p_bh < 0.05
        pass_dir = mean_b < mean_h
        verdict = "PASS" if (pass_kw and pass_bh and pass_dir) else "FAIL"
        print(f"\n  Pre-reg: KW p<0.05 AND post-hoc B-vs-H p<0.05 AND mean_B < mean_H")
        print(f"  Verdict: {verdict}")
    else:
        verdict = "INSUFFICIENT_DATA"
        mean_b = mean_h = p_bh = u = z = None
        print(f"\n  Insufficient data for B vs H post-hoc")
        print(f"  B: {len(b_zs)} folios, H: {len(h_zs)} folios")

    # Also report by language for context (Currier A vs B vs AZC)
    print("\n--- Auxiliary by-language report (not part of pre-reg) ---")
    for lang in ['A', 'B', 'NA']:
        zs = by_language.get(lang, [])
        if zs:
            print(f"  {lang}: n={len(zs)}, mean z_mu = {statistics.mean(zs):+.3f}, "
                  f"frac<0 = {sum(1 for v in zs if v<0)/len(zs):.1%}")

    out = {
        'test': 'T4',
        'hypothesis': 'Sections differ in z_mu; B more constrained than H',
        'by_section_means': {sec: statistics.mean(zs) for sec, zs in by_section.items()},
        'by_section_counts': {sec: len(zs) for sec, zs in by_section.items()},
        'by_language_means': {lang: statistics.mean(zs) for lang, zs in by_language.items()},
        'by_language_counts': {lang: len(zs) for lang, zs in by_language.items()},
        'kruskal_wallis': {
            'H': H_stat,
            'df': df,
            'p': p_kw,
            'sections_in_test': sorted(eligible.keys()),
        },
        'post_hoc_B_vs_H': {
            'n_B': len(b_zs),
            'n_H': len(h_zs),
            'mean_B': mean_b,
            'mean_H': mean_h,
            'u': u,
            'z': z,
            'p_two_sided': p_bh,
        },
        'verdict': verdict,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't4_section_zmu.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
