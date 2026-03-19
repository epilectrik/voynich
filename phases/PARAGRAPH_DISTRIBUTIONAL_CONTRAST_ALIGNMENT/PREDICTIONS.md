# Phase 606: Paragraph Distributional Contrast Alignment — Pre-Registered Predictions

**Phase:** 606
**Date:** 2026-03-18
**Status:** FROZEN (do not modify after hash computation)

## Design

Tests whether pseudo-Lull procedure-family contrasts predict Voynich folio paragraph-mixture shape, using EMD-based shape margin as the primary tested object. Follows Phase 605's partial recovery of the thermal axis (C1752) by moving to the resolution where C1573 says distributional shape carries folio-specific information (EMD z=6.21).

## Two Anchors

**Anchor A (primary): Shape Margin**
- For each folio: compute 4D zone distribution from C1398 paragraph zone assignments
- Compute EMD to PL distillation profile and EMD to PL monitoring-rich basin profile
- shape_margin = EMD_to_distillation - EMD_to_basin (positive = closer to basin)

**Anchor B (validation): h_ratio_resid**
- OLS residual of h_ratio on section dummies (S, H, B) + k_ratio
- Same computation as Phase 605

## PL Zone Profile Derivation

Recomputed directly from Phase 602 E1_chapters (not inherited from Phase 604):
1. Load 209 chapters with primary_family and per-chapter feature densities
2. Filter to operational families: distillation (n=16), sublimation (n=7), dissolution (n=12)
3. Compute per-chapter rates: monitoring_density, correction_rate (correction_count/operational_density), heat_rate (heat_count/operational_density), judgment_rate (judgment_count/operational_density), termination_rate (termination_count/operational_density), chain_rate (chain_count/operational_density), operational_density
4. Mean prototype per family across chapters
5. Z-score prototypes against pooled mean/std of the 3 families
6. Mapping matrix (frozen):
   - Zone 0 (THERMAL) = 0.5 * heat_z + 0.3 * operational_z + 0.2 * termination_z
   - Zone 1 (CONTAINMENT) = 0.4 * correction_z + 0.3 * termination_z + 0.3 * judgment_z
   - Zone 2 (ITERATION) = 0.4 * chain_z + 0.3 * operational_z + 0.3 * heat_z
   - Zone 3 (MONITORING) = 0.5 * monitoring_z + 0.3 * judgment_z + 0.2 * correction_z
7. Softmax normalize to 4D simplex
8. Basin profile = mean(sublimation_profile, dissolution_profile)

## Calibration Gates

- **S0:** n >= 40 folios with zone distributions AND h_resid. FAIL -> INSUFFICIENT_DATA.
- **S1:** h_resid vs THERMAL zone fraction, Spearman one-sided negative, p < 0.01. Replicates C1752. FAIL -> CALIBRATION_FAILURE.

## Primary Predictions (3)

| ID | Test | Direction | Method | Threshold |
|----|------|-----------|--------|-----------|
| P1 | shape_margin vs h_resid | positive | Spearman one-sided | p < 0.05 |
| P2 | shape_margin vs thermo_ke | negative | Spearman one-sided | p < 0.05 |
| P3 | Within-section shape_margin vs h_resid (Herbal OR Stars) | positive | Spearman one-sided | p < 0.05 in at least one section |

P1: Historical shape alignment tracks established monitoring axis.
P2: Shape alignment predicts thermal burden independently (not mediated through h_resid).
P3: Shape carries within-section information (not just section recapitulation).

## Secondary Predictions (2)

| ID | Test | Direction |
|----|------|-----------|
| S2 | h_resid vs MONITORING zone fraction | positive |
| S3 | shape_margin vs (OPERATION + MONITORING) combined fraction | positive |

## Exploratory Diagnostics (2)

| ID | Test | Notes |
|----|------|-------|
| D1 | h_resid vs OPERATION zone fraction | Direction unknown |
| D2 | JSD-based shape margin vs h_resid | Compare JSD vs EMD |

## Negative Controls (3)

| ID | Test | Expected |
|----|------|----------|
| N1 | Cross-folio zone permutation (500 shuffles, preserve folio para counts + global zone freq) | P1/P2 rho exceed 95th percentile |
| N2 | Random Dirichlet(1) profile pairs (500 draws) replacing PL profiles | P1 rho exceeds 95th percentile |
| N3 | shape_margin from theoretical_neg profile vs h_resid | No significant correlation (p > 0.10) |

N1: Shuffles paragraphs across folios (preserving folio paragraph count and overall zone frequencies).
N2: Tests whether PL-derived profiles are specifically informative vs arbitrary 4D profiles.
N3: Non-operational PL profile (127 theoretical chapters) should not predict V structure.

## Sensitivity Analyses

- Within-Herbal: P1, P2
- Within-Stars: P1, P2
- Section+REGIME control: h_ratio residualized on section + REGIME + k_ratio
- JSD as alternative distance metric for all primary tests

## Verdict Tree

```
S0 fails (n < 40)  -> INSUFFICIENT_DATA
S1 fails            -> CALIBRATION_FAILURE

K = primary predictions passing (P1, P2, P3)
K_perm = those surviving N1 permutation AND N2 for P1

K_perm = 3 AND N3 clean -> PARAGRAPH_DISTRIBUTIONAL_ALIGNMENT_CONFIRMED
K_perm = 2              -> PARTIAL_DISTRIBUTIONAL_ALIGNMENT
K_perm = 1              -> WEAK_SIGNAL
K_perm = 0              -> NOT_CONFIRMED
```

## EMD Implementation

```
emd_1d(p, q) = sum(|cumsum(p/sum(p)) - cumsum(q/sum(q))|)
```
Same as Phase 604.
