"""Peak-specificity test: is lag-19 a SHARP PEAK above neighboring lags, or just
part of generic elevation?

Discriminating refinement on the lag-19 metric. Synthetic computus shows lag-19
isolated peak above near-zero neighbors. Voynich shows lag-19 in a band of
generally elevated lags. Mesue NL shows lag-19 as part of broad topical
autocorrelation across many lags.

Metric: peak_specificity_19 = lag19_value - mean(lag17, lag18, lag20, lag21, lag22, lag23)
  Positive → lag-19 sticks out above neighbors (computus-like)
  Near zero → lag-19 is just background-elevated (not period-19-specific)
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phases/PHASE_700_COMPUTUS_ADVERSARIAL/scripts"))
from _computus_adversarial import (
    build_computus_metonic, build_computus_epacts, build_computus_paschal_moon,
    get_voynich_paragraphs, get_latin_paragraphs,
    lag_n_agreement_paragraphs
)


def peak_specificity(paragraphs, target_lag=19, neighbor_lags=(15, 16, 17, 18, 20, 21, 22, 23)):
    """Compute (target_lag rate) − (mean of neighbor_lags rates).
    Positive = target lag sticks out above neighbors (specific cycle signal).
    """
    target = lag_n_agreement_paragraphs(paragraphs, target_lag)
    neighbors = [lag_n_agreement_paragraphs(paragraphs, n) for n in neighbor_lags]
    mean_neighbors = sum(neighbors) / len(neighbors)
    return target, mean_neighbors, target - mean_neighbors


def main():
    print("="*70)
    print("PEAK-SPECIFICITY TEST: is lag-19 a sharp peak vs neighbors?")
    print("="*70)
    print()

    corpora = [
        ("Synthetic Metonic", build_computus_metonic(200)),
        ("Bedan Epacts", build_computus_epacts(200)),
        ("Paschal Moons", build_computus_paschal_moon(200)),
        ("Mesue Latin (NL)", get_latin_paragraphs("mesue")),
        ("Voynich Section B", get_voynich_paragraphs('section_b')),
        ("Voynich matched-S", get_voynich_paragraphs('matched_s')),
    ]

    print(f"{'Corpus':>25}  {'lag-19':>8}  {'neighbors':>10}  {'specificity':>12}  Verdict")
    print(f"{'-'*25}  {'-'*8}  {'-'*10}  {'-'*12}  {'-'*30}")
    results = []
    for name, paras in corpora:
        if not paras:
            print(f"{name:>25}  N/A (empty)")
            continue
        target, mean_n, spec = peak_specificity(paras)
        # Verdict thresholds
        if spec >= 0.10:
            verdict = "SHARP PEAK (period-19 specific)"
        elif spec >= 0.02:
            verdict = "Moderate peak"
        elif spec >= -0.005:
            verdict = "No peak (uniform elevation)"
        else:
            verdict = "Anti-peak"
        print(f"{name:>25}  {target:>8.4f}  {mean_n:>10.4f}  {spec:>+12.4f}  {verdict}")
        results.append({
            "corpus": name, "lag19": target, "mean_neighbors": mean_n,
            "specificity": spec, "verdict": verdict
        })

    print()
    print("="*70)
    print("INTERPRETATION")
    print("="*70)
    print()
    print("Pre-registered: Computus signature = SHARP peak at lag-19 above neighbors.")
    print("If Voynich specificity ≈ 0 or negative, lag-19 is just background-elevated,")
    print("NOT period-19-specific. This is the actual discriminator.")
    print()

    # Pre-committed verdict
    voy_sb = next(r for r in results if "Section B" in r["corpus"])
    voy_ms = next(r for r in results if "matched-S" in r["corpus"])
    syn = next(r for r in results if "Metonic" in r["corpus"])

    sb_share = voy_sb["specificity"] / syn["specificity"] if syn["specificity"] > 0 else 0
    ms_share = voy_ms["specificity"] / syn["specificity"] if syn["specificity"] > 0 else 0

    print(f"Synthetic computus specificity: {syn['specificity']:+.4f}")
    print(f"Voynich Section B specificity:  {voy_sb['specificity']:+.4f}  ({100*sb_share:.1f}% of computus)")
    print(f"Voynich matched-S specificity:  {voy_ms['specificity']:+.4f}  ({100*ms_share:.1f}% of computus)")

    if voy_sb["specificity"] < 0.02 and voy_ms["specificity"] < 0.02:
        print()
        print("*** COMPUTUS HYPOTHESIS FALSIFIED ***")
        print("  Voynich lacks the SHARP-PEAK signature that defines period-19 specificity.")
        print("  Neither Section B nor matched-S shows period-19 above generic neighbor lags.")
        print("  Computus added to alternative-class falsification series (after mensural).")

    OUT = ROOT / "phases/PHASE_700_COMPUTUS_ADVERSARIAL/results/peak_specificity.json"
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
