"""PHASE_699: Hapax MIDDLE concentration test.

PHASE_698 Test (c) showed Currier B MIDDLE hapax rate (63%) matches Catalan
hapax rate (64%). Both "operational productive tail" (open-class operational
variants) and "lexical content tail" (specific materials/parameters/names)
predict NL-like hapax rate. They diverge on folio distribution:

- Operational productive tail: hapaxes should distribute roughly proportional
  to folio MIDDLE token count (rare operational variants triggered randomly).
- Lexical content tail: hapaxes should CLUSTER on specific folios that
  describe distinctive content (different recipes have different specific
  materials/parameters → different specific MIDDLEs).

Test: per-folio hapax MIDDLE enrichment vs frequency-matched non-hapax control.
Threshold (C914 precedent): if hapax-enriched folios show ≥3× concentration
vs the matched control's per-folio distribution, lexical-content interpretation
wins.

Pre-registered binary criteria:
  H1: Hapax max enrichment ratio (most-enriched folio's hapax density vs
      manuscript-wide hapax density) >= 3.0 on at least one folio.
  H2: Hapax enrichment distribution Gini coefficient > 0.25 across folios
      (would indicate folio-specific clustering).
  H3: Hapax enrichment > frequency-matched (2-3-occurrence) non-hapax enrichment
      on the same top-enriched folios (paired comparison, sign test p<0.05).
  H4: Top-decile folios for hapax enrichment significantly OVERLAP with top-
      decile folios for token-count-normalized vocabulary diversity (TTR);
      otherwise hapax enrichment is a vocabulary-diversity confound, not
      content-specific.

If H1+H2+H3 PASS: lexical-content-tail interpretation supported (Tier 3 candidate).
If H1+H2 fail but H3 passes: operational-productive-tail with mild clustering.
If H1+H2+H3 all fail: pure operational productive tail.
H4 is calibration to detect confound.
"""
import json
import math
import random
import re
import sys
import io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()
random.seed(42)


def collect_middle_data():
    """Return (middle_folio_counts, folio_total_middles).
    middle_folio_counts[middle][folio] = count of (middle, folio) co-occurrences.
    folio_total_middles[folio] = total MIDDLE tokens on that folio.
    """
    tx = Transcript()
    middle_folio = defaultdict(lambda: Counter())  # middle -> {folio: count}
    folio_totals = Counter()
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not (t.placement and t.placement.startswith("P")):
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio[m.middle][t.folio] += 1
                folio_totals[t.folio] += 1
        except Exception:
            pass
    return dict(middle_folio), dict(folio_totals)


def main():
    print("Loading Currier B MIDDLE data...")
    middle_folio, folio_totals = collect_middle_data()
    print(f"  {len(middle_folio)} unique MIDDLEs")
    print(f"  {len(folio_totals)} folios")
    total_tokens = sum(folio_totals.values())
    print(f"  {total_tokens} total MIDDLE tokens")

    # =================================================================
    # 1. Identify frequency cohorts
    # =================================================================
    cohorts = {
        "hapax": [],         # n_occurrences == 1
        "n_2_3": [],          # 2 or 3 occurrences (frequency-matched low-freq control)
        "n_4_10": [],         # 4-10 occurrences (mid-frequency control)
        "n_11_plus": [],      # 11+ (high-frequency, core operational)
    }
    for m, fcounts in middle_folio.items():
        total = sum(fcounts.values())
        if total == 1:
            cohorts["hapax"].append(m)
        elif total <= 3:
            cohorts["n_2_3"].append(m)
        elif total <= 10:
            cohorts["n_4_10"].append(m)
        else:
            cohorts["n_11_plus"].append(m)

    print("\n=== COHORT SIZES ===")
    for name, lst in cohorts.items():
        print(f"  {name}: {len(lst)} unique MIDDLEs")

    # =================================================================
    # 2. Per-folio token counts per cohort
    # =================================================================
    per_folio_cohort = {name: Counter() for name in cohorts}
    for m, fcounts in middle_folio.items():
        # Determine cohort
        total = sum(fcounts.values())
        if total == 1:
            cohort = "hapax"
        elif total <= 3:
            cohort = "n_2_3"
        elif total <= 10:
            cohort = "n_4_10"
        else:
            cohort = "n_11_plus"
        for folio, count in fcounts.items():
            per_folio_cohort[cohort][folio] += count

    # =================================================================
    # 3. Per-folio enrichment per cohort
    # =================================================================
    cohort_totals = {name: sum(per_folio_cohort[name].values()) for name in cohorts}
    print("\n=== COHORT TOTAL TOKEN COUNTS ===")
    for name, tot in cohort_totals.items():
        print(f"  {name}: {tot} tokens ({100*tot/total_tokens:.1f}% of corpus)")

    folio_enrichments = {name: {} for name in cohorts}
    for folio, total in folio_totals.items():
        folio_frac = total / total_tokens
        for name in cohorts:
            obs = per_folio_cohort[name][folio]
            expected = cohort_totals[name] * folio_frac
            enrich = obs / expected if expected > 0 else 0
            folio_enrichments[name][folio] = enrich

    # =================================================================
    # 4. Top folios per cohort
    # =================================================================
    print("\n=== TOP 10 FOLIOS BY HAPAX ENRICHMENT ===")
    sorted_folios = sorted(folio_enrichments["hapax"].items(), key=lambda x: -x[1])
    print(f"{'Folio':>8} {'Hapax':>7} {'n_2_3':>7} {'n_4_10':>8} {'n_11+':>7} {'Folio_total':>12}")
    for folio, enrich in sorted_folios[:15]:
        h_e = folio_enrichments["hapax"][folio]
        n23 = folio_enrichments["n_2_3"][folio]
        n410 = folio_enrichments["n_4_10"][folio]
        n11 = folio_enrichments["n_11_plus"][folio]
        ft = folio_totals[folio]
        print(f"{folio:>8} {h_e:>6.2f}x {n23:>6.2f}x {n410:>7.2f}x {n11:>6.2f}x {ft:>11}")

    # =================================================================
    # 5. Pre-registered criteria
    # =================================================================
    print("\n=== PRE-REGISTERED BINARY CRITERIA ===")

    # H1: max hapax enrichment >= 3.0
    max_hapax = max(folio_enrichments["hapax"].values())
    H1 = max_hapax >= 3.0
    print(f"  H1: max hapax enrichment >= 3.0?  max = {max_hapax:.2f}x  --> {'PASS' if H1 else 'FAIL'}")

    # H2: Gini coefficient of hapax enrichment > 0.25
    def gini(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        cumsum = 0
        for i, v in enumerate(sorted_vals):
            cumsum += (i + 1) * v
        total = sum(sorted_vals)
        if total == 0:
            return 0
        return (2 * cumsum) / (n * total) - (n + 1) / n
    hapax_vals = list(folio_enrichments["hapax"].values())
    hapax_gini = gini(hapax_vals)
    H2 = hapax_gini > 0.25
    print(f"  H2: Hapax enrichment Gini > 0.25?  Gini = {hapax_gini:.4f}  --> {'PASS' if H2 else 'FAIL'}")

    # Also compute Gini for control cohorts (calibration)
    n23_gini = gini(list(folio_enrichments["n_2_3"].values()))
    n410_gini = gini(list(folio_enrichments["n_4_10"].values()))
    n11_gini = gini(list(folio_enrichments["n_11_plus"].values()))
    print(f"     (Control: n_2_3 Gini = {n23_gini:.4f}, n_4_10 = {n410_gini:.4f}, n_11+ = {n11_gini:.4f})")

    # H3: Paired comparison — hapax enrichment > n_2_3 enrichment on top-decile-hapax folios
    top_decile_n = max(1, len(folio_totals) // 10)
    top_hapax_folios = [f for f, e in sorted_folios[:top_decile_n]]
    paired_diffs = []
    n_hapax_gt_n23 = 0
    for folio in top_hapax_folios:
        h_e = folio_enrichments["hapax"][folio]
        n23 = folio_enrichments["n_2_3"][folio]
        diff = h_e - n23
        paired_diffs.append((folio, h_e, n23, diff))
        if h_e > n23:
            n_hapax_gt_n23 += 1
    # Sign test: P(k >= n_hapax_gt_n23 | p=0.5) using normal approximation for n=top_decile_n
    n_top = len(top_hapax_folios)
    # Two-sided p via binomial: 2 * sum binomial(n_top, k>=n_hapax_gt_n23) * 0.5^n_top
    import math
    def binom_tail(n, k):
        from math import comb
        return sum(comb(n, j) for j in range(k, n+1)) / (2**n)
    p_value_sign = binom_tail(n_top, n_hapax_gt_n23)
    H3 = (n_hapax_gt_n23 >= n_top * 0.7) and p_value_sign < 0.05
    print(f"  H3: Hapax > n_2_3 on top-decile hapax folios?  {n_hapax_gt_n23}/{n_top}, sign-test p={p_value_sign:.4f}  --> {'PASS' if H3 else 'FAIL'}")
    print(f"     Paired comparisons (top hapax folios):")
    for folio, h_e, n23, diff in paired_diffs:
        print(f"       {folio}: hapax={h_e:.2f}x, n_2_3={n23:.2f}x, diff={diff:+.2f}")

    # H4: Top-decile hapax folios overlap with top-decile TTR folios
    # Compute folio MIDDLE TTR
    folio_middle_types = Counter()
    for m, fcounts in middle_folio.items():
        for folio in fcounts:
            folio_middle_types[folio] += 1
    folio_ttr = {f: folio_middle_types[f] / folio_totals[f] if folio_totals[f] else 0 for f in folio_totals}
    sorted_ttr = sorted(folio_ttr.items(), key=lambda x: -x[1])
    top_ttr_folios = set(f for f, t in sorted_ttr[:top_decile_n])
    top_hapax_set = set(top_hapax_folios)
    overlap = len(top_hapax_set & top_ttr_folios)
    expected_overlap_uniform = (top_decile_n * top_decile_n) / len(folio_totals)
    H4 = overlap >= expected_overlap_uniform * 1.5  # Threshold: 50% above random
    print(f"  H4: Top-decile hapax folios overlap top-TTR folios?  overlap={overlap}/{top_decile_n}, expected={expected_overlap_uniform:.2f}  --> {'CONFOUND' if H4 else 'CLEAN'}")
    print(f"     (H4 PASS = potential TTR confound; CLEAN = hapax-enrichment independent of vocabulary diversity)")

    # =================================================================
    # 6. Summary verdict
    # =================================================================
    print("\n=== VERDICT ===")
    print(f"  H1 (max enrichment >= 3): {'PASS' if H1 else 'FAIL'}")
    print(f"  H2 (Gini > 0.25):         {'PASS' if H2 else 'FAIL'}")
    print(f"  H3 (paired sign test):    {'PASS' if H3 else 'FAIL'}")
    print(f"  H4 (TTR overlap):         {'CONFOUND' if H4 else 'CLEAN'}")
    if H1 and H2 and H3 and not H4:
        verdict = "LEXICAL-CONTENT-TAIL SUPPORTED — clean clustering, no TTR confound"
    elif H1 and H2 and H3 and H4:
        verdict = "LEXICAL-CONTENT-TAIL POSSIBLE but TTR-CONFOUNDED — needs follow-up"
    elif H1 or H2 or H3:
        verdict = "PARTIAL — some clustering signal but doesn't meet full pre-registered criteria"
    else:
        verdict = "OPERATIONAL-PRODUCTIVE-TAIL CONFIRMED — hapaxes distribute proportionally"
    print(f"\n  VERDICT: {verdict}")

    # =================================================================
    # 7. C914 comparison
    # =================================================================
    print(f"\n=== C914 PRECEDENT COMPARISON ===")
    print(f"  C914 label enrichment on illustrated folios: 3.7x")
    print(f"  Observed max hapax enrichment: {max_hapax:.2f}x ({'MATCHES' if max_hapax >= 3.0 else 'BELOW'} C914 threshold)")

    # Save results
    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/hapax_concentration.json"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "method": "Per-folio hapax MIDDLE enrichment vs frequency-matched non-hapax controls",
        "cohort_sizes": {n: len(l) for n, l in cohorts.items()},
        "cohort_totals": cohort_totals,
        "n_folios": len(folio_totals),
        "total_middle_tokens": total_tokens,
        "max_hapax_enrichment": max_hapax,
        "hapax_gini": hapax_gini,
        "n23_gini": n23_gini,
        "n410_gini": n410_gini,
        "n11_gini": n11_gini,
        "n_top_decile": top_decile_n,
        "top_hapax_folios": top_hapax_folios,
        "n_hapax_greater_n23": n_hapax_gt_n23,
        "sign_test_p": p_value_sign,
        "ttr_overlap": overlap,
        "expected_ttr_overlap_uniform": expected_overlap_uniform,
        "H1_pass": H1, "H2_pass": H2, "H3_pass": H3, "H4_confound": H4,
        "verdict": verdict,
        "paired_diffs": paired_diffs,
        "folio_enrichments_top15": sorted_folios[:15],
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
