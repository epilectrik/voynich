# C1966: HT Density Quantitatively Tracks Compound-Specification Load

**Tier:** 2
**Scope:** B, HT, compound, specification, per-folio, density
**Phase:** PHASE_651_HT_DENSITY_VALIDATION
**Date:** 2026-04-26
**Refines:** C935 (HT compound specification — promoted from corpus-wide claim to per-folio quantitative relationship)
**Extends:** C740 (HT = UN by definition), HTSC OPERATIONAL_REDUNDANCY guarantee
**Rejects:** Early Tier 4 attention-scaffolding hypothesis for HT (sh_rate correlation goes opposite predicted)

---

## Statement

HT density per Currier B folio correlates with the count of distinct compound MIDDLEs on that folio at **Spearman ρ = +0.602 (n = 82, p < 0.0001)**. The relationship survives within-section restriction in all three major sections:

- Section B (Bath, n=20): ρ = +0.764
- Section H (Herbal, n=32): ρ = +0.507
- Section S (Stars/Recipes, n=23): ρ = +0.686

This promotes C935 from "HT carries compound specification (corpus-wide)" to **"HT density quantitatively tracks per-folio compound specification load."** Folios with more diverse compound work deploy more HT tokens to specify it. The relationship is not section-driven, not driven by total folio length (mild positive +0.260, opposite the condensation prediction), and not driven by passive-monitoring intensity (negative -0.195, opposite the attention-scaffolding prediction).

---

## Mechanistic interpretation

HT tokens are defined by HTSC C740 as tokens with compound MIDDLEs (MIDDLE not in the simple core inventory). A folio with many *distinct* compound MIDDLEs has many different compound specs to encode; each instance of a distinct compound is one HT token.

The cross-folio correlation says HT density tracks compound *diversity*, not merely total compound instance count. High-HT folios deploy many different compound specs rather than repeating the same compound spec multiple times. This is an informational claim about how HT load distributes:

- Folios with operationally diverse compound work → high HT density (e.g., recipes-section folios with many different procedure templates)
- Folios with operationally simple/repeated work → low HT density (e.g., long bath procedures with one core operation repeated)

This refines C935's "operationally redundant, not non-operational" framing: the redundancy is *load-bearing* in the specification dimension. HT serves compound-specification needs; folios needing more compound work get more HT.

---

## Three competing readings tested

| Reading | Predictor | Result |
|---|---|---|
| **Specification (#3, current C935)** | distinct compound MIDDLE count | **rho = +0.602, p<0.0001 — STRONGLY SUPPORTED** |
| Attention scaffolding (#2, old Tier 4) | sh_rate (passive observation) | rho = -0.195, p = 0.075 — **REJECTED (opposite predicted direction)** |
| Condensation pressure | inverse total tokens | rho = +0.260 (positive, not negative) — opposite predicted; no condensation effect at corpus level |
| Active fire (control) | qo_rate | rho = +0.048, null |

Sub-finding: condensation effect IS present within Section H (rho = -0.335 vs total tokens) and Section S (-0.398) but not Section B. Long-form bath procedures don't compress; short herbal/recipes folios do. This is a section-localized secondary effect, not the primary function.

---

## What's resolved by C1966

- **C935 quantified.** From "HT carries compound specification" (qualitative) to "HT density tracks compound specification load at rho=+0.60 cross-folio, 0.51-0.76 within sections" (quantitative).
- **HT primary function is operational, not decorative.** Specification reading dominates; fluency-practice reading (early Tier 4) is left as a possible side effect but not primary.
- **Attention-scaffolding reading is empirically refuted.** The prediction was specific (sh_rate correlation positive) and the data shows the opposite. Removing this reading from the live interpretation set for HT specifically — though the broader scribe-attention infrastructure speculation (HT compound spec redundancy + line-as-safety-packet + transition markers + cycle-counting) remains open in INTERPRETATION_SUMMARY.md.

---

## Falsification

Would be falsified if:

1. The +0.602 correlation collapses below 0.20 under any well-powered stratification (we ran section; could also run REGIME, scribe identity)
2. A more refined "compound complexity" metric (e.g., compound MIDDLE atom-decomposition diversity) produces a different ranking across folios that doesn't track HT rate
3. The within-section robustness disappears when controlling for compound MIDDLE rarity (i.e., the relationship is mediated by rare-MIDDLE selection rather than compound diversity per se)

---

## Provenance

- `phases/PHASE_651_HT_DENSITY_VALIDATION/scripts/s2_ht_density_v2.py` (locked-in result)
- `phases/PHASE_651_HT_DENSITY_VALIDATION/scripts/s1_ht_density_v1.py` (initial crude test, preserved for transparency)
- `phases/PHASE_651_HT_DENSITY_VALIDATION/results/ht_density_v2.json`
- `context/STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml` (HT definitional anchor: HT = UN)
- C740 (HT/UN identity), C935 (HT compound specification, base constraint refined here)
