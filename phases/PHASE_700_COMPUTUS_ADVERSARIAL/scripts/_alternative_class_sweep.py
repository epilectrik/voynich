"""PHASE_700 extended: Alternative-class sweep beyond computus.

Per crazy-expert PHASE_699 follow-up, alternative-class adversarial tests should
cover the medieval-specific periodicities. Crazy-expert advised AGAINST bundling
in earlier consult, but user requested efficient sweep. Mitigation: each period
gets its own pre-registered peak-specificity threshold, treated as independent
test. Bonferroni-style correction: require Voynich peak-specificity to be at
least 10% of synthetic baseline for any class match.

ALTERNATIVE CLASSES TESTED (each with characteristic period):

  Mensural (period-2)         — already FALSIFIED via C2032 cross-language
  Computus Metonic (period-19) — FALSIFIED Step 1 of this phase
  Solar dominical (period-28)  — same family as computus
  Lunar synodic (period-30)    — medieval lunaria, calendar of lunar months
  Indiction (period-15)        — Roman/Byzantine civil cycle
  Zodiac (period-12)           — astrological monthly cycle
  Weekly (period-7)            — calendrical week

POSITIVE-CLASS-VALIDATION (Voynich's own pattern):
  Lag-2 peak-specificity should be HIGH for Voynich Section B (C2032 period-2)
  → validates that peak-specificity metric works in positive direction

PRE-REGISTERED CRITERIA:
  For each candidate period P in {7, 12, 15, 19, 28, 30}:
    - Synthetic corpus shows peak-specificity ≈ +1.0 at lag P (by construction)
    - NL Mesue shows peak-specificity ≈ 0 at lag P (generic-elevation baseline)
    - Voynich Section B and matched-S compared to (specificity / synthetic):
      ≥ 10% of synthetic → POSSIBLE class match
      < 10% of synthetic → ALTERNATIVE CLASS EXCLUDED

  POSITIVE CONTROL: Voynich Section B lag-2 specificity should be HIGH (validates metric).
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phases/PHASE_700_COMPUTUS_ADVERSARIAL/scripts"))
from _computus_adversarial import (
    get_voynich_paragraphs, get_latin_paragraphs,
    lag_n_agreement_paragraphs
)


def build_synthetic_period(period, n_cycles=200):
    """Generate synthetic corpus with exact period P (cycles 0, 1, ..., P-1 repeating)."""
    paragraphs = []
    para_length = max(2 * period + 10, 38)  # ensure paragraph covers at least 2 full cycles + buffer
    total_tokens = n_cycles * period
    n_paras = total_tokens // para_length
    for p in range(n_paras):
        para = []
        for offset in range(para_length):
            value = (p * para_length + offset) % period
            para.append(str(value))
        paragraphs.append(para)
    return paragraphs


def peak_specificity(paragraphs, target_lag, neighbor_offsets=(-4, -3, -2, -1, 1, 2, 3, 4)):
    """Compute (target_lag rate) − (mean of neighbor lags at target±offset)."""
    target = lag_n_agreement_paragraphs(paragraphs, target_lag)
    neighbors = []
    for offset in neighbor_offsets:
        n_lag = target_lag + offset
        if n_lag <= 0: continue
        neighbors.append(lag_n_agreement_paragraphs(paragraphs, n_lag))
    mean_n = sum(neighbors) / len(neighbors) if neighbors else 0
    return target, mean_n, target - mean_n


def main():
    print("="*70)
    print("PHASE_700 EXTENDED: Alternative-class sweep")
    print("="*70)
    print()

    # Test periods
    periods = [2, 7, 12, 15, 19, 28, 30]

    # Build synthetic corpora
    print("Building synthetic period corpora...")
    synthetic = {p: build_synthetic_period(p) for p in periods}
    for p in periods:
        print(f"  period-{p}: {len(synthetic[p])} paragraphs, mean length {sum(len(x) for x in synthetic[p])//len(synthetic[p])}")

    # Get Voynich + Mesue
    print("\nLoading Voynich + NL baselines...")
    voy_sb = get_voynich_paragraphs('section_b')
    voy_ms = get_voynich_paragraphs('matched_s')
    mesue = get_latin_paragraphs("mesue")
    print(f"  Voynich Section B: {len(voy_sb)} paras, {sum(len(p) for p in voy_sb)} tokens")
    print(f"  Voynich matched-S: {len(voy_ms)} paras, {sum(len(p) for p in voy_ms)} tokens")
    print(f"  Mesue Latin: {len(mesue)} paras, {sum(len(p) for p in mesue)} tokens")

    # =================================================================
    # Sweep: peak-specificity at each candidate period
    # =================================================================
    print()
    print("="*70)
    print("PEAK-SPECIFICITY SWEEP")
    print("="*70)
    print()
    print(f"{'period':>7}  {'synthetic':>10}  {'mesue':>10}  {'voy_SB':>10}  {'voy_MS':>10}  {'SB_share':>10}  {'MS_share':>10}  Class")
    print(f"{'-'*7}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*30}")

    results = {}
    for p in periods:
        syn_target, syn_n, syn_spec = peak_specificity(synthetic[p], p)
        mes_target, mes_n, mes_spec = peak_specificity(mesue, p)
        sb_target, sb_n, sb_spec = peak_specificity(voy_sb, p)
        ms_target, ms_n, ms_spec = peak_specificity(voy_ms, p)

        sb_share = sb_spec / syn_spec if syn_spec > 0 else 0
        ms_share = ms_spec / syn_spec if syn_spec > 0 else 0

        # Class identifier
        class_name = {
            2: "Mensural",
            7: "Weekly",
            12: "Zodiac",
            15: "Indiction",
            19: "Computus Metonic",
            28: "Solar dominical",
            30: "Lunaria",
        }.get(p, f"period-{p}")

        # Match verdict per pre-registered threshold (10% of synthetic)
        if sb_share >= 0.10 or ms_share >= 0.10:
            verdict = f"POSSIBLE MATCH ({class_name})"
        else:
            verdict = f"EXCLUDED ({class_name})"

        print(f"{p:>7}  {syn_spec:>+10.4f}  {mes_spec:>+10.4f}  {sb_spec:>+10.4f}  {ms_spec:>+10.4f}  "
              f"{100*sb_share:>9.2f}%  {100*ms_share:>9.2f}%  {verdict}")

        results[p] = {
            "class_name": class_name,
            "synthetic_specificity": syn_spec,
            "mesue_specificity": mes_spec,
            "voynich_sb_specificity": sb_spec,
            "voynich_ms_specificity": ms_spec,
            "sb_share_of_synthetic": sb_share,
            "ms_share_of_synthetic": ms_share,
            "verdict": verdict,
        }

    # =================================================================
    # Voynich own-pattern validation
    # =================================================================
    print()
    print("="*70)
    print("VOYNICH OWN-PATTERN POSITIVE CONTROL (period-2 should be HIGH)")
    print("="*70)
    p2_sb_share = results[2]["sb_share_of_synthetic"]
    p2_ms_share = results[2]["ms_share_of_synthetic"]
    print(f"\nVoynich Section B period-2 peak-specificity: {results[2]['voynich_sb_specificity']:+.4f}")
    print(f"  Share of synthetic period-2: {100*p2_sb_share:.2f}%")
    print(f"  This is the C2032 signature — should be HIGH")
    print(f"\nIf Voynich Section B period-2 < 10% of synthetic, peak-specificity metric is broken.")
    if p2_sb_share >= 0.10:
        print(f"  Validation: PASS — Voynich Section B shows period-2 signature consistent with C2032")
    else:
        print(f"  Validation: FAIL — metric doesn't detect Voynich's known period-2 grammar (concerning)")

    # =================================================================
    # Aggregate verdict
    # =================================================================
    print()
    print("="*70)
    print("ALTERNATIVE-CLASS SWEEP VERDICTS")
    print("="*70)

    matches = []
    exclusions = []
    for p, r in results.items():
        if p == 2: continue  # Voynich's own positive control
        if "POSSIBLE MATCH" in r["verdict"]:
            matches.append((p, r["class_name"]))
        else:
            exclusions.append((p, r["class_name"]))

    print(f"\nAlternative classes EXCLUDED ({len(exclusions)}):")
    for p, name in exclusions:
        print(f"  Period-{p}: {name}")

    print(f"\nAlternative classes POSSIBLY MATCHING ({len(matches)}):")
    if matches:
        for p, name in matches:
            print(f"  Period-{p}: {name}")
    else:
        print("  (none)")

    print()
    print("="*70)
    print("CUMULATIVE ALTERNATIVE-CLASS FALSIFICATION SERIES")
    print("="*70)
    print("""
  Mensural notation         FALSIFIED (C2032 cross-language test, 2026-05-16)
  Computus Metonic (P=19)   FALSIFIED (this phase, peak-specificity)
  Solar dominical (P=28)    {} (PHASE_700 sweep)
  Lunaria (P=30)            {} (PHASE_700 sweep)
  Indiction (P=15)          {} (PHASE_700 sweep)
  Zodiac (P=12)             {} (PHASE_700 sweep)
  Weekly (P=7)              {} (PHASE_700 sweep)
""".format(*[results[p]["verdict"].split(" ")[0] for p in [28, 30, 15, 12, 7]]))

    OUT = ROOT / "phases/PHASE_700_COMPUTUS_ADVERSARIAL/results/alternative_class_sweep.json"
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
