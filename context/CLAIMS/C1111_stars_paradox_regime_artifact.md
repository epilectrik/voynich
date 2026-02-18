# C1111: Stars Paradox is a REGIME Composition Artifact

**Tier:** 2 (STRUCTURAL INFERENCE — RESOLUTION)
**Scope:** B
**Phase:** STARS_PARADOX_RESOLUTION (Phase 394)
**Resolves:** C1084 (section AXM ordering), the "Stars Paradox" from C1108
**Strengthens:** C979 (REGIME modulates weights, not topology)

---

## Statement

The Stars Paradox — Section S has the most REGIME diversity but the lowest AXM variance — is NOT a genuine structural anomaly. It dissolves under REGIME-matched controls.

**Gate 1.1 (PASS):** Stars AXM variance (0.00525) IS genuinely below the Herbal bootstrap 5th percentile (0.00671). Stars appears anomalous when compared to Herbal without REGIME matching.

**Gate 1.2 (FAIL):** Within-REGIME comparisons eliminate the paradox:
- REGIME_1: Stars var=0.00444, non-Stars var=0.00643. Ratio=1.45x. MW p=0.075 (not significant).
- REGIME_3: Stars var=0.00662, non-Stars var=0.00396. Ratio=0.60x — **non-Stars is MORE convergent than Stars.**

The apparent paradox arises because:
1. Stars spans R1 (10 folios) and R3 (12 folios), which produce similar AXM self-transition rates
2. Herbal is concentrated in R1 but has high within-R1 variance
3. Comparing un-REGIME-matched section-level statistics inflates Herbal's variance relative to Stars

No active mechanism is needed. The REGIME system (C979) already explains the variance pattern.

---

## Evidence

### Gate 1: Paradox Confirmation
| Test | Result | Key Value |
|------|--------|-----------|
| G1.1: Bootstrap (vs Herbal) | **PASS** | Stars at 1.6th percentile |
| G1.2: REGIME-matched | **FAIL** | R1: ratio 1.45, p=0.075; R3: ratio 0.60, p=0.480 |
| Gate 1 overall | **FAIL** | Paradox not confirmed under controls |

### Gate 2: All Four Mechanisms (0/11 PASS)
| Mechanism | Sub-tests | Result | Key Finding |
|-----------|-----------|--------|-------------|
| M1: LINK Regulation | 0/3 | FAIL | rho=-0.018, LINK removal +5% variance (not +20%) |
| M2: CC Channeling | 0/3 | FAIL | Stars CC entropy HIGHER (1.79 vs 1.55, wrong direction) |
| M3: Paragraph | 0/2 | FAIL | Stars JSD=0.114, higher than Bio JSD=0.076 |
| M4: Forbidden Transitions | 0/3 | FAIL | Stars has FEWER zeros (-25.5%, opposite prediction) |

### AXM Variance by Section (corrected)
| Section | AXM Variance | n | Dominant REGIME |
|---------|-------------|---|-----------------|
| Stars (S) | 0.00525 | 23 | R1 (10), R3 (12) |
| Bio (B) | 0.00590 | 20 | R4 (12) |
| Herbal (H) | 0.01303 | 32 | R1 (22) |

Stars and Bio have nearly identical AXM variance. The "paradox" was really a Herbal outlier (high variance), not a Stars anomaly (low variance). Herbal's high variance reflects R1's internal heterogeneity, not a Stars-specific mechanism.

---

## Interpretation

The Stars Paradox (C1108 "leaves open") is resolved without invoking any new mechanism. The resolution has three components:

1. **REGIME composition explains the apparent low variance.** Stars is split between R1 and R3, which happen to produce similar AXM rates. No active convergence mechanism is needed.

2. **Herbal is the outlier, not Stars.** Herbal has 2.5x the AXM variance of Stars, but this reflects R1's internal diversity across 22 Herbal folios. Stars and Bio are near-identical in variance (0.00525 vs 0.00590).

3. **All four alternative mechanisms are comprehensively falsified:**
   - **LINK regulation (M1):** Zero correlation between LINK density and AXM deviation within Stars (rho=-0.018). LINK removal barely affects variance (+5%). Cross-section partial correlation is zero.
   - **CC channeling (M2):** Stars CC triggers are MORE diverse than non-Stars (entropy 1.79 vs 1.55 — wrong direction). CC exit routing is wider (effective diversity 3.51 vs 3.17 — wrong direction).
   - **Paragraph constraint (M3):** Stars inter-paragraph JSD is higher than Bio (0.114 vs 0.076 — wrong direction). Interaction term is positive (more paragraphs = MORE deviation in Stars).
   - **De facto forbidden transitions (M4):** Stars has FEWER zero class-pair transitions than expected (-25.5% — opposite of prediction). Zero significant universally-absent pairs after Bonferroni correction.

The comprehensive failure of all four mechanisms across all 11 sub-tests (0/11 PASS) confirms that no active mechanism suppresses Stars' AXM variance. The REGIME system is sufficient.

---

## Constraint Implications

- **C979 strengthened**: REGIME modulates weights, not topology. No section-specific topology modifier is needed to explain Stars behavior.
- **C1084 qualified**: The section AXM ordering (S < B < H) is a REGIME-composition effect, not a section-intrinsic property.
- **C1108 resolved**: The "Stars Paradox" and its four untested mechanisms are now all addressed. None explains the paradox because the paradox is an artifact.

---

## Provenance

- Phase: 394 (STARS_PARADOX_RESOLUTION), 15-test battery (2 GATE + 11 mechanism + 2 sufficiency)
- Script: `phases/STARS_PARADOX_RESOLUTION/scripts/stars_paradox_resolution.py`
- Results: `phases/STARS_PARADOX_RESOLUTION/results/stars_paradox_resolution.json`
- Related: C979, C1084, C1108
