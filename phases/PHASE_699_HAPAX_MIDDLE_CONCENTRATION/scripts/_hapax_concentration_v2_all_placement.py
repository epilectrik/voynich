"""PHASE_699 v2 — Hapax MIDDLE concentration test with CORRECTED placement filter.

Original PHASE_699 used P-placement only, which artificially inflated the
"hapax" cohort (76 of 78 "hapax dark pipeline" MIDDLEs were actually multi-
folio under broader placement). v2 uses ALL placements (H-track + non-uncertain
only) for true corpus-wide MIDDLE frequencies.

Replicates the original four pre-registered criteria (H1-H4) with corrected
data, then runs hapax × dark pipeline overlap with true hapaxes.

H1: max hapax enrichment >= 3.0 on at least one folio
H2: hapax enrichment Gini > 0.25
H3: hapax > n_2_3 on top-decile hapax folios (sign test p<0.05)
H4: TTR overlap test (confound check)
"""
import json
import math
import random
import sys, io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()
random.seed(42)


def collect_middle_data():
    """Collect MIDDLE-folio data using ALL placements (no P-only filter)."""
    tx = Transcript()
    middle_folio = defaultdict(lambda: Counter())
    folio_totals = Counter()
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not t.placement:  # still require placement to be present
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio[m.middle][t.folio] += 1
                folio_totals[t.folio] += 1
        except Exception:
            pass
    return dict(middle_folio), dict(folio_totals)


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
    print("Loading Currier B MIDDLE data (ALL placements)...")
    middle_folio, folio_totals = collect_middle_data()
    print(f"  {len(middle_folio)} unique MIDDLEs")
    print(f"  {len(folio_totals)} folios")
    total_tokens = sum(folio_totals.values())
    print(f"  {total_tokens} total MIDDLE tokens")

    # Compare to v1 (P-only) numbers
    print(f"\n  PHASE_699 v1 (P-only) had: 1302 MIDDLEs, 80 folios, 21610 tokens")
    print(f"  PHASE_699 v2 (all placements): {len(middle_folio)} MIDDLEs, {len(folio_totals)} folios, {total_tokens} tokens")

    # =================================================================
    # 1. Cohorts
    # =================================================================
    cohorts = {"hapax": [], "n_2_3": [], "n_4_10": [], "n_11_plus": []}
    middle_freq = {}
    for m, fcounts in middle_folio.items():
        total = sum(fcounts.values())
        middle_freq[m] = total
        if total == 1:
            cohorts["hapax"].append(m)
        elif total <= 3:
            cohorts["n_2_3"].append(m)
        elif total <= 10:
            cohorts["n_4_10"].append(m)
        else:
            cohorts["n_11_plus"].append(m)

    print("\n=== COHORT SIZES (v2 corrected) ===")
    for name, lst in cohorts.items():
        print(f"  {name}: {len(lst)} unique MIDDLEs")
    print(f"\n  Compare v1: hapax=820, n_2_3=232, n_4_10=135, n_11+=115")
    delta_hapax = len(cohorts["hapax"]) - 820
    print(f"  Hapax delta: {delta_hapax:+d} ({100*delta_hapax/820:+.1f}%)")

    # =================================================================
    # 2. Per-folio cohort counts
    # =================================================================
    per_folio_cohort = {name: Counter() for name in cohorts}
    for m, fcounts in middle_folio.items():
        total = sum(fcounts.values())
        cohort = "hapax" if total == 1 else ("n_2_3" if total <= 3 else ("n_4_10" if total <= 10 else "n_11_plus"))
        for folio, count in fcounts.items():
            per_folio_cohort[cohort][folio] += count

    cohort_totals = {n: sum(per_folio_cohort[n].values()) for n in cohorts}
    print("\n=== COHORT TOTAL TOKENS (v2) ===")
    for n, t in cohort_totals.items():
        print(f"  {n}: {t} ({100*t/total_tokens:.1f}%)")

    # =================================================================
    # 3. Per-folio enrichment
    # =================================================================
    folio_enrichments = {name: {} for name in cohorts}
    for folio, total in folio_totals.items():
        folio_frac = total / total_tokens
        for name in cohorts:
            obs = per_folio_cohort[name][folio]
            expected = cohort_totals[name] * folio_frac
            enrich = obs / expected if expected > 0 else 0
            folio_enrichments[name][folio] = enrich

    # =================================================================
    # 4. Top folios by hapax enrichment
    # =================================================================
    print("\n=== TOP 15 FOLIOS BY HAPAX ENRICHMENT (v2) ===")
    sorted_folios = sorted(folio_enrichments["hapax"].items(), key=lambda x: -x[1])
    print(f"{'Folio':>8} {'Hapax':>7} {'n_2_3':>7} {'n_4_10':>8} {'n_11+':>7} {'Total':>8}")
    for folio, enrich in sorted_folios[:15]:
        h = folio_enrichments["hapax"][folio]
        n23 = folio_enrichments["n_2_3"][folio]
        n410 = folio_enrichments["n_4_10"][folio]
        n11 = folio_enrichments["n_11_plus"][folio]
        ft = folio_totals[folio]
        print(f"{folio:>8} {h:>6.2f}x {n23:>6.2f}x {n410:>7.2f}x {n11:>6.2f}x {ft:>8}")

    # =================================================================
    # 5. Pre-registered criteria
    # =================================================================
    print("\n=== PRE-REGISTERED CRITERIA (v2) ===")

    max_hapax = max(folio_enrichments["hapax"].values())
    H1 = max_hapax >= 3.0
    print(f"  H1: max hapax enrichment >= 3.0?  max = {max_hapax:.2f}x  --> {'PASS' if H1 else 'FAIL'}")

    hapax_vals = list(folio_enrichments["hapax"].values())
    hapax_gini = gini(hapax_vals)
    H2 = hapax_gini > 0.25
    print(f"  H2: Hapax Gini > 0.25?  Gini = {hapax_gini:.4f}  --> {'PASS' if H2 else 'FAIL'}")
    print(f"     v1 comparison: hapax_gini was 0.3253")

    n23_gini = gini(list(folio_enrichments["n_2_3"].values()))
    n410_gini = gini(list(folio_enrichments["n_4_10"].values()))
    n11_gini = gini(list(folio_enrichments["n_11_plus"].values()))
    print(f"     Control Ginis (v2): n_2_3={n23_gini:.4f}, n_4_10={n410_gini:.4f}, n_11+={n11_gini:.4f}")
    print(f"     v1 control Ginis: n_2_3=0.3064, n_4_10=0.2699, n_11+=0.0283")

    # H3: top-decile sign test
    top_decile_n = max(1, len(folio_totals) // 10)
    top_hapax_folios = [f for f, e in sorted_folios[:top_decile_n]]
    n_hapax_gt_n23 = 0
    paired = []
    for folio in top_hapax_folios:
        h = folio_enrichments["hapax"][folio]
        n23 = folio_enrichments["n_2_3"][folio]
        paired.append((folio, h, n23, h-n23))
        if h > n23: n_hapax_gt_n23 += 1
    from math import comb
    def binom_tail(n, k):
        return sum(comb(n, j) for j in range(k, n+1)) / (2**n)
    p_sign = binom_tail(len(top_hapax_folios), n_hapax_gt_n23)
    H3 = (n_hapax_gt_n23 >= len(top_hapax_folios) * 0.7) and p_sign < 0.05
    print(f"  H3: hapax > n_2_3 on top-decile? {n_hapax_gt_n23}/{len(top_hapax_folios)}, p={p_sign:.4f}  --> {'PASS' if H3 else 'FAIL'}")
    for folio, h, n23, diff in paired:
        print(f"     {folio}: hapax={h:.2f}x, n_2_3={n23:.2f}x, diff={diff:+.2f}")

    # H4: TTR confound
    folio_middle_types = Counter()
    for m, fcounts in middle_folio.items():
        for folio in fcounts:
            folio_middle_types[folio] += 1
    folio_ttr = {f: folio_middle_types[f] / folio_totals[f] if folio_totals[f] else 0 for f in folio_totals}
    sorted_ttr = sorted(folio_ttr.items(), key=lambda x: -x[1])
    top_ttr_folios = set(f for f, _ in sorted_ttr[:top_decile_n])
    overlap = len(set(top_hapax_folios) & top_ttr_folios)
    expected = (top_decile_n * top_decile_n) / len(folio_totals)
    H4 = overlap >= expected * 1.5
    print(f"  H4: TTR overlap (confound check)? {overlap}/{top_decile_n}, expected={expected:.2f}  --> {'CONFOUND' if H4 else 'CLEAN'}")

    # =================================================================
    # 6. Hapax × Dark Pipeline overlap (v2 — true hapaxes)
    # =================================================================
    print(f"\n=== HAPAX × DARK PIPELINE OVERLAP (v2) ===")
    dark_data = json.loads((ROOT / "data/dark_pipeline_middles.json").read_text(encoding="utf-8"))
    dark_middles = set(dark_data["middles"])
    hapax_set = set(cohorts["hapax"])
    overlap_v2 = hapax_set & dark_middles
    print(f"  v2 hapax cohort: {len(hapax_set)} MIDDLEs")
    print(f"  Dark pipeline (catalogued): {len(dark_middles)} MIDDLEs")
    print(f"  Hapax ∩ Dark Pipeline (TRUE hapaxes): {len(overlap_v2)}")
    print(f"  v1 reported overlap (P-only inflated): 78")
    if overlap_v2:
        print(f"\n  TRUE hapax × dark pipeline MIDDLEs:")
        for m in sorted(overlap_v2):
            folio = list(middle_folio[m].keys())[0]
            placement = "?"  # don't have placement detail at this point
            print(f"    {m}: 1× on {folio}")

    # =================================================================
    # 7. Dark pipeline frequency distribution (v2)
    # =================================================================
    print(f"\n=== DARK PIPELINE FREQUENCY DISTRIBUTION (v2) ===")
    dark_in_b = [m for m in dark_middles if m in middle_freq]
    dark_freqs_v2 = [middle_freq[m] for m in dark_in_b]
    print(f"  Dark pipeline present in v2 data: {len(dark_in_b)} of {len(dark_middles)}")
    print(f"  Frequency band counts:")
    bands = [(1, "n=1 (hapax)"), (2, "n=2"), (3, "n=3"), (4, "n=4-5"), (6, "n=6-10"), (11, "n=11-30"), (31, "n=31+")]
    for i, (low, label) in enumerate(bands):
        if i+1 < len(bands):
            high = bands[i+1][0]
            count = sum(1 for f in dark_freqs_v2 if low <= f < high)
        else:
            count = sum(1 for f in dark_freqs_v2 if f >= low)
        print(f"    {label}: {count}")
    print(f"  Mean: {sum(dark_freqs_v2)/len(dark_freqs_v2):.2f}, Median: {sorted(dark_freqs_v2)[len(dark_freqs_v2)//2]}")

    # =================================================================
    # 8. Summary verdict
    # =================================================================
    print(f"\n=== V2 VERDICT ===")
    print(f"  H1 (max enrichment ≥3): {'PASS' if H1 else 'FAIL'}")
    print(f"  H2 (Gini > 0.25):       {'PASS' if H2 else 'FAIL'}")
    print(f"  H3 (sign test):         {'PASS' if H3 else 'FAIL'}")
    print(f"  H4 (TTR confound):      {'CONFOUND' if H4 else 'CLEAN'}")

    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/hapax_concentration_v2.json"
    OUT.write_text(json.dumps({
        "method": "PHASE_699 v2: all-placement MIDDLE frequencies",
        "v1_p_only": {"hapax_cohort_size": 820, "max_enrichment": 3.94, "hapax_gini": 0.3253},
        "v2_all_placements": {
            "hapax_cohort_size": len(cohorts["hapax"]),
            "n_2_3_size": len(cohorts["n_2_3"]),
            "n_4_10_size": len(cohorts["n_4_10"]),
            "n_11_plus_size": len(cohorts["n_11_plus"]),
            "total_middles": len(middle_folio),
            "total_tokens": total_tokens,
            "max_hapax_enrichment": max_hapax,
            "hapax_gini": hapax_gini,
            "n23_gini": n23_gini,
            "n410_gini": n410_gini,
            "n11_gini": n11_gini,
            "top_hapax_folios": [(f, e) for f, e in sorted_folios[:15]],
        },
        "criteria": {"H1": H1, "H2": H2, "H3": H3, "H4_confound": H4},
        "hapax_dark_overlap_v2": sorted(overlap_v2),
        "n_hapax_dark_overlap_v2": len(overlap_v2),
        "dark_pipeline_freqs_v2": dark_freqs_v2,
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
