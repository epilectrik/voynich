"""PHASE_699 v3 — Three controls required by expert consultation before registration:

(A) Placement-stratified H3: does hapax > n_2_3 paired sign test survive
    when we exclude L/R/S/C label placements? Crazy-expert: "labels carry
    instance-identification vocabulary (C914, C928) — including them
    contaminates the hapax cohort with KNOWN identification class."

(B) TTR-controlled logistic regression: P(MIDDLE in dark pipeline) ~ is_hapax
    + folio_TTR + folio_token_count. Does is_hapax survive controlling for
    vocabulary diversity? Crazy-expert: "TTR confound 3/8 vs 0.78 expected
    = 3.85× overlap, dominant alternative explanation."

(C) 70-MIDDLE distribution by section + placement: where do the truly-hapax
    × dark pipeline MIDDLEs actually live? Three signatures, three claims:
    - uniform across corpus → framework-consistent, weakest interpretation
    - Section S concentrated → C2028/C1995 section confound
    - Diagram-heavy concentrated → label-population artifact (kills v2)

Decision rule: if all three controls pass → register v2 confidently. If any
fail → register methodology constraint alone (P-only filter inflation).
"""
import json
import math
import sys, io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()


# Currier section per folio (from project knowledge; approximate via folio number ranges)
def folio_section(folio):
    """Rough section assignment — used for analysis only."""
    # Per project knowledge:
    # Section H (herbal): f1r through f57v approximately
    # Section A (astrological): f57v-f73v
    # Section B (biological/balneological): f75r-f86v6
    # Section T/Z/C/P: various
    # Section S (small recipe): f103r-f116v approximately
    if folio.startswith("f1") and len(folio) == 3:
        return "H"
    try:
        # Strip non-numeric prefix/suffix
        import re
        m = re.match(r"f(\d+)([rv])?(\d*)", folio)
        if not m: return "?"
        num = int(m.group(1))
        if num >= 1 and num <= 57: return "H"
        if num >= 58 and num <= 73: return "A_Z"  # astrological/zodiac
        if num >= 74 and num <= 102: return "B"
        if num >= 103 and num <= 116: return "S"
        return "?"
    except (ValueError, AttributeError):
        return "?"


def collect_data():
    """Collect MIDDLE data with placement detail."""
    tx = Transcript()
    middle_folio_placement = defaultdict(list)
    folio_total_p = Counter()      # P-only token count
    folio_total_all = Counter()    # All-placement token count
    folio_middles_p = defaultdict(set)
    folio_middles_all = defaultdict(set)
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not t.placement:
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio_placement[m.middle].append((t.folio, t.placement))
                folio_total_all[t.folio] += 1
                folio_middles_all[t.folio].add(m.middle)
                if t.placement.startswith("P"):
                    folio_total_p[t.folio] += 1
                    folio_middles_p[t.folio].add(m.middle)
        except Exception:
            pass
    return dict(middle_folio_placement), dict(folio_total_p), dict(folio_total_all), dict(folio_middles_p), dict(folio_middles_all)


def gini(values):
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0: return 0
    cumsum = 0
    for i, v in enumerate(sorted_vals):
        cumsum += (i + 1) * v
    total = sum(sorted_vals)
    if total == 0: return 0
    return (2 * cumsum) / (n * total) - (n + 1) / n


def main():
    middle_data, folio_tot_p, folio_tot_all, folio_mids_p, folio_mids_all = collect_data()

    # Frequency by different filters
    middle_freq_all = {m: len(occs) for m, occs in middle_data.items()}
    # P-only frequency
    middle_freq_p = {}
    for m, occs in middle_data.items():
        f = sum(1 for _, p in occs if p.startswith("P"))
        if f > 0:
            middle_freq_p[m] = f
    # P+L frequency (paragraph + labels, exclude rings/stars/circles)
    middle_freq_pl = {}
    for m, occs in middle_data.items():
        f = sum(1 for _, p in occs if p.startswith("P") or p.startswith("L"))
        if f > 0:
            middle_freq_pl[m] = f

    # Define cohorts and per-folio counts for each placement filter
    def cohort_stats(middle_freq, folio_tot, folio_middles, filter_name, allowed_prefixes):
        """Compute per-folio hapax + n_2_3 enrichment for the given placement filter."""
        cohorts = {"hapax": [], "n_2_3": [], "n_4_10": [], "n_11_plus": []}
        for m, f in middle_freq.items():
            if f == 1:
                cohorts["hapax"].append(m)
            elif f <= 3:
                cohorts["n_2_3"].append(m)
            elif f <= 10:
                cohorts["n_4_10"].append(m)
            else:
                cohorts["n_11_plus"].append(m)

        # Per-folio counts
        per_folio = {name: Counter() for name in cohorts}
        for m, f in middle_freq.items():
            cohort = "hapax" if f == 1 else ("n_2_3" if f <= 3 else ("n_4_10" if f <= 10 else "n_11_plus"))
            for folio, placement in middle_data[m]:
                if any(placement.startswith(pr) for pr in allowed_prefixes):
                    per_folio[cohort][folio] += 1

        # Enrichments
        cohort_totals = {n: sum(per_folio[n].values()) for n in cohorts}
        total_tokens = sum(folio_tot.values())
        folio_enrich = {name: {} for name in cohorts}
        for folio, total in folio_tot.items():
            ff = total / total_tokens if total_tokens else 0
            for name in cohorts:
                obs = per_folio[name][folio]
                expected = cohort_totals[name] * ff
                folio_enrich[name][folio] = obs / expected if expected > 0 else 0
        return cohorts, folio_enrich, total_tokens

    # ===========================================
    # CONTROL A: Placement-stratified H3
    # ===========================================
    print("="*70)
    print("CONTROL A: Placement-stratified H3 (hapax > n_2_3 paired sign test)")
    print("="*70)

    # Three variants
    variants = [
        ("P-only (v1)", middle_freq_p, folio_tot_p, ["P"]),
        ("P+L (paragraph + labels)", middle_freq_pl, folio_tot_p, ["P", "L"]),
        ("All placements (v2)", middle_freq_all, folio_tot_all, ["P", "L", "R", "S", "C", "X", "Y", "N"]),
    ]
    from math import comb
    def binom_tail(n, k):
        return sum(comb(n, j) for j in range(k, n+1)) / (2**n)

    h3_results = []
    for label, mfreq, ftot, prefixes in variants:
        cohorts, enrich, total = cohort_stats(mfreq, ftot, folio_mids_all, label, prefixes)
        n_h = len(cohorts["hapax"])
        max_hapax = max(enrich["hapax"].values()) if enrich["hapax"] else 0
        hapax_gini = gini(list(enrich["hapax"].values()))
        n_23_gini = gini(list(enrich["n_2_3"].values()))
        sorted_top = sorted(enrich["hapax"].items(), key=lambda x: -x[1])
        n_top = max(1, len(ftot) // 10)
        top_hapax_folios = [f for f, _ in sorted_top[:n_top]]
        n_gt = sum(1 for f in top_hapax_folios if enrich["hapax"][f] > enrich["n_2_3"][f])
        p_sign = binom_tail(n_top, n_gt)
        h3_pass = n_gt >= n_top * 0.7 and p_sign < 0.05
        print(f"\n  {label}:")
        print(f"    Hapax cohort: {n_h}")
        print(f"    Max enrichment: {max_hapax:.2f}x")
        print(f"    Hapax Gini: {hapax_gini:.4f}, n_2_3 Gini: {n_23_gini:.4f}")
        print(f"    H3 (top-decile sign test): {n_gt}/{n_top}, p={p_sign:.4f} → {'PASS' if h3_pass else 'FAIL'}")
        h3_results.append({"variant": label, "n_hapax": n_h, "max_enrichment": max_hapax,
                            "hapax_gini": hapax_gini, "n23_gini": n_23_gini,
                            "n_gt": n_gt, "n_top": n_top, "p_sign": p_sign, "h3_pass": h3_pass})

    # ===========================================
    # CONTROL B: TTR-controlled logistic / partial correlation
    # ===========================================
    print("\n" + "="*70)
    print("CONTROL B: TTR-controlled analysis")
    print("="*70)

    # For each folio: compute TTR (all placement) and hapax enrichment
    folio_ttr = {f: len(folio_mids_all[f]) / folio_tot_all[f] for f in folio_tot_all}
    # Hapax enrichment (v2, all placement)
    _, enrich_v2, _ = cohort_stats(middle_freq_all, folio_tot_all, folio_mids_all,
                                     "v2", ["P", "L", "R", "S", "C", "X", "Y", "N"])
    folio_hapax_enrich = enrich_v2["hapax"]

    # Compute correlation of hapax enrichment with TTR vs with folio_size
    folios = sorted(folio_tot_all.keys())
    ttr_vals = [folio_ttr[f] for f in folios]
    enrich_vals = [folio_hapax_enrich[f] for f in folios]
    size_vals = [folio_tot_all[f] for f in folios]

    def pearson(x, y):
        n = len(x)
        mx, my = sum(x)/n, sum(y)/n
        num = sum((x[i]-mx)*(y[i]-my) for i in range(n))
        dx = math.sqrt(sum((x[i]-mx)**2 for i in range(n)))
        dy = math.sqrt(sum((y[i]-my)**2 for i in range(n)))
        return num / (dx*dy) if dx*dy else 0

    r_ttr_enrich = pearson(ttr_vals, enrich_vals)
    r_size_enrich = pearson(size_vals, enrich_vals)
    r_ttr_size = pearson(ttr_vals, size_vals)
    print(f"\n  Hapax enrichment vs folio TTR: r = {r_ttr_enrich:.4f}")
    print(f"  Hapax enrichment vs folio size: r = {r_size_enrich:.4f}")
    print(f"  TTR vs folio size: r = {r_ttr_size:.4f}")

    # Partial correlation: hapax enrichment vs (something) controlling for TTR
    # We want to test whether HAPAX_DARK_OVERLAP at folio level survives TTR control
    # For each folio: count of dark-pipeline hapax tokens, total dark-pipeline tokens
    dark_data = json.loads((ROOT / "data/dark_pipeline_middles.json").read_text(encoding="utf-8"))
    dark_set = set(dark_data["middles"])
    hapax_dark = set(m for m, f in middle_freq_all.items() if f == 1) & dark_set
    # Per-folio count of hapax×dark occurrences
    folio_hapax_dark = Counter()
    folio_dark = Counter()
    for m, occs in middle_data.items():
        if m not in dark_set: continue
        for folio, _ in occs:
            folio_dark[folio] += 1
            if m in hapax_dark:
                folio_hapax_dark[folio] += 1
    # Express as rate per folio
    folios_with_dark = [f for f in folios if folio_dark[f] > 0]
    hapax_dark_rate = [folio_hapax_dark[f]/folio_tot_all[f] for f in folios_with_dark]
    ttr_subset = [folio_ttr[f] for f in folios_with_dark]
    enrich_subset = [folio_hapax_enrich[f] for f in folios_with_dark]

    r_dark_ttr = pearson(hapax_dark_rate, ttr_subset)
    r_dark_enrich = pearson(hapax_dark_rate, enrich_subset)
    print(f"\n  Per-folio hapax×dark RATE vs TTR: r = {r_dark_ttr:.4f}")
    print(f"  Per-folio hapax×dark RATE vs hapax enrichment: r = {r_dark_enrich:.4f}")

    # Partial correlation: hapax_dark_rate vs hapax_enrich controlling for TTR
    # Partial r_{XY|Z} = (r_xy - r_xz * r_yz) / sqrt((1 - r_xz^2)(1-r_yz^2))
    r_xy = r_dark_enrich  # hapax_dark_rate vs hapax_enrich
    r_xz = r_dark_ttr     # hapax_dark_rate vs TTR
    r_yz_sub = pearson(enrich_subset, ttr_subset)
    if (1 - r_xz**2) * (1 - r_yz_sub**2) > 0:
        partial_r = (r_xy - r_xz * r_yz_sub) / math.sqrt((1 - r_xz**2) * (1 - r_yz_sub**2))
    else:
        partial_r = float('nan')
    print(f"\n  Partial correlation (hapax_dark_rate vs hapax_enrich | TTR controlled):")
    print(f"    Raw r: {r_xy:.4f}")
    print(f"    TTR-controlled r: {partial_r:.4f}")
    print(f"    {'SIGNAL SURVIVES TTR CONTROL' if abs(partial_r) > 0.15 else 'SIGNAL COLLAPSES (TTR confounded)'}")

    # ===========================================
    # CONTROL C: 70-MIDDLE distribution by section + placement
    # ===========================================
    print("\n" + "="*70)
    print("CONTROL C: 70-MIDDLE hapax×dark distribution by section/placement")
    print("="*70)

    # Section assignment per folio
    section_hapax_dark = Counter()
    section_total_dark = Counter()
    placement_hapax_dark = Counter()
    placement_total_dark = Counter()
    for m, occs in middle_data.items():
        if m not in dark_set: continue
        for folio, placement in occs:
            sec = folio_section(folio)
            section_total_dark[sec] += 1
            placement_total_dark[placement[0] if placement else "?"] += 1
            if m in hapax_dark:
                section_hapax_dark[sec] += 1
                placement_hapax_dark[placement[0] if placement else "?"] += 1

    print("\n  Hapax × Dark Pipeline distribution by SECTION:")
    print(f"  {'Section':>10} {'Hapax×Dark':>12} {'Total Dark':>12} {'Frac':>8}")
    for sec in sorted(section_total_dark.keys()):
        hd = section_hapax_dark[sec]
        td = section_total_dark[sec]
        frac = hd/td if td else 0
        print(f"  {sec:>10} {hd:>12} {td:>12} {frac:>7.3f}")

    print("\n  Hapax × Dark Pipeline distribution by PLACEMENT TYPE:")
    print(f"  {'Placement':>10} {'Hapax×Dark':>12} {'Total Dark':>12} {'Frac':>8}")
    for p in sorted(placement_total_dark.keys()):
        hd = placement_hapax_dark[p]
        td = placement_total_dark[p]
        frac = hd/td if td else 0
        print(f"  {p:>10} {hd:>12} {td:>12} {frac:>7.3f}")

    # Compute expected uniform distribution
    total_hapax_dark = sum(section_hapax_dark.values())
    total_dark = sum(section_total_dark.values())
    if total_dark:
        print(f"\n  If uniform: hapax×dark fraction would be {total_hapax_dark/total_dark:.3f} across all sections.")
        print(f"  Test: significant section non-uniformity?")
        # Chi-square approximation
        expected_frac = total_hapax_dark / total_dark
        chi_sq = 0
        for sec, td in section_total_dark.items():
            obs = section_hapax_dark[sec]
            exp = td * expected_frac
            if exp > 0:
                chi_sq += (obs - exp)**2 / exp
        print(f"    Chi-square (df={len(section_total_dark)-1}): {chi_sq:.2f}")
        # Critical values for df=3 at p=0.05: 7.815; df=4: 9.488
        df = len(section_total_dark) - 1
        crit_005 = {1: 3.84, 2: 5.99, 3: 7.81, 4: 9.49, 5: 11.07}.get(df, 11.07)
        sec_uniform_fail = chi_sq > crit_005
        print(f"    p<0.05 critical for df={df}: {crit_005}, {'SECTION CONFOUND' if sec_uniform_fail else 'UNIFORM ACROSS SECTIONS'}")

    # ===========================================
    # FINAL VERDICT
    # ===========================================
    print("\n" + "="*70)
    print("V3 VERDICT")
    print("="*70)
    h3_passes = [r for r in h3_results if r["h3_pass"]]
    p_only_pass = h3_results[0]["h3_pass"]
    all_pass = h3_results[2]["h3_pass"]
    print(f"\n  Control A (placement-stratified H3):")
    for r in h3_results:
        print(f"    {r['variant']}: H3 {'PASS' if r['h3_pass'] else 'FAIL'} ({r['n_gt']}/{r['n_top']}, p={r['p_sign']:.4f})")

    print(f"\n  Control B (TTR-controlled hapax×dark):")
    print(f"    Raw r(hapax_dark_rate, hapax_enrich) = {r_xy:.4f}")
    print(f"    Partial r (TTR controlled) = {partial_r:.4f}")
    ttr_survives = abs(partial_r) > 0.15
    print(f"    {'SIGNAL SURVIVES TTR' if ttr_survives else 'SIGNAL COLLAPSES UNDER TTR'}")

    print(f"\n  Control C (70-MIDDLE distribution):")
    print(f"    Section chi-square: {chi_sq:.2f} (df={df})")
    print(f"    {'SECTION CONFOUND' if sec_uniform_fail else 'UNIFORM ACROSS SECTIONS'}")

    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/v3_three_controls.json"
    OUT.write_text(json.dumps({
        "control_a_placement_stratified": h3_results,
        "control_b_ttr_controlled": {
            "r_ttr_enrich": r_ttr_enrich,
            "r_size_enrich": r_size_enrich,
            "r_ttr_size": r_ttr_size,
            "r_dark_enrich_raw": r_xy,
            "r_dark_ttr": r_xz,
            "r_enrich_ttr_subset": r_yz_sub,
            "partial_r_ttr_controlled": partial_r,
            "ttr_signal_survives": ttr_survives,
        },
        "control_c_distribution": {
            "section_hapax_dark": dict(section_hapax_dark),
            "section_total_dark": dict(section_total_dark),
            "placement_hapax_dark": dict(placement_hapax_dark),
            "placement_total_dark": dict(placement_total_dark),
            "chi_square": chi_sq,
            "df": df,
            "section_confound": sec_uniform_fail,
        },
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
