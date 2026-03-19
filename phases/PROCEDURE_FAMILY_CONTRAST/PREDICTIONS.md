# Phase 605: Pre-Registration of Predictions

**Status:** FROZEN -- do not modify after SHA-256 hash is recorded.

## Anchor Variable

h_ratio_resid = residual of h_ratio after OLS regression on section dummies (S, H, B; exclude T/C for n<6) + k_ratio.
This isolates the monitoring signal beyond section membership and thermal intensity.

## PL Family Contrast Basis

Sublimation vs distillation per-chapter prototype densities (from Phase 604 Stage 1):
- monitoring_density: SUB 1.57 vs DIST 0.77 (2.0x, SUB >> DIST)
- termination_rate: SUB 12.20 vs DIST 4.87 (2.5x, SUB >> DIST)
- heat_rate: SUB 11.37 vs DIST 13.33 (0.85x, SUB < DIST)
- chain_rate: SUB 9.35 vs DIST 3.91 (2.4x, SUB >> DIST)
- judgment_rate: SUB 0.00 vs DIST 1.52 (0x, SUB << DIST)
- correction_rate: SUB 3.57 vs DIST 3.99 (0.89x, SUB ~ DIST)

Since sublimation = high monitoring = high h_ratio (C1750):
- Features where SUB > DIST should positively correlate with h_ratio_resid
- Features where SUB < DIST should negatively correlate with h_ratio_resid

## S0: Data Sufficiency Gate

n_common_folios (intersection of all feature sources) >= 60.
If FAIL: INSUFFICIENT_DATA, stop.

## S1: Calibration Anchor

Phase 604 Approach A sublimation-assigned folios have higher h_ratio_resid than distillation-assigned folios.
Mann-Whitney one-sided p < 0.01.
If FAIL: CALIBRATION_FAILURE, stop.

## Primary Prediction Battery (4 predictions, load-bearing)

### P1: PRED_TERM -- h_ratio_resid positively correlates with terminal_rate
- PL basis: sublimation termination_rate 2.5x distillation
- V feature: terminal_rate (from folio_operational_profiles.json)
- Direction: positive (h_resid up -> terminal_rate up)
- Test: Spearman correlation, one-sided p < 0.05
- Rationale: PL termination density -> V terminal tokens. C1746 links PL thresholding to V closure architecture.

### P2: PRED_ITER -- h_ratio_resid positively correlates with iteration_rate
- PL basis: sublimation chain_rate 2.4x distillation
- V feature: iteration_rate (from folio_operational_profiles.json)
- Direction: positive (h_resid up -> iteration_rate up)
- Test: Spearman correlation, one-sided p < 0.05
- Rationale: PL chain operations -> V iteration tokens. C1398 links MONITORING and OPERATION_ITERATION as real paragraph axes.

### P3: PRED_HEAT_NEG -- h_ratio_resid negatively correlates with thermo_ke
- PL basis: distillation heat_rate 1.17x sublimation (distillation is the heat-dominant family)
- V feature: thermo_ke (from folio_operational_profiles.json)
- Direction: negative (h_resid up -> thermo_ke down)
- Test: Spearman correlation, one-sided p < 0.05
- Rationale: C1735-C1736 confirm thermal burden and monitoring are distinct axes. Inverse relation expected.

### P4: PRED_THERMAL_NEG -- h_ratio_resid negatively correlates with thermal paragraph fraction
- PL basis: same as P3 (distillation = heat-dominant)
- V feature: fraction of paragraphs in cluster 0 (THERMAL-heavy cluster, centroid THERMAL=0.424) per folio, from paragraph_program_typing.json
- Direction: negative (h_resid up -> thermal_paragraph_fraction down)
- Test: Spearman correlation, one-sided p < 0.05
- Rationale: Independent confirmation of P3 using paragraph-level zone composition (different data source).

Pass: p < 0.05 one-sided in predicted direction.

## Secondary Battery (2 predictions, reported but not load-bearing)

### S1_pred: PRED_CYCLE -- h_ratio_resid positively correlates with cycle_regularity
- PL basis: sublimation chain_rate 2.4x distillation
- V feature: cycle_regularity (from b_macro_scaffold_audit.json)
- Direction: positive

### S2_pred: PRED_CHECKPOINT -- h_ratio_resid positively correlates with checkpoint_rate
- PL basis: sublimation monitoring_density 2.0x distillation
- V feature: checkpoint_rate (from folio_operational_profiles.json)
- Direction: positive

## Exploratory Diagnostics (no pass/fail, report only)

- D1: opaque_close_fraction (t0_opportunity_normalization.json)
- D2: strong_close_fraction (t0_opportunity_normalization.json)
- D3: intervention_frequency (b_macro_scaffold_audit.json)
- D4: recovery_ops_count / n_tokens (b_macro_scaffold_audit.json)

## Negative Controls

### N1: Permutation Control
Shuffle h_ratio_resid 1000 times. For each passing primary prediction, real |rho| must exceed 95th percentile of shuffled |rho|.
K_perm = number of primary predictions surviving permutation.

### N2: Random Axis Control
Replace h_ratio_resid with random standard-normal vector (seeded). Run all 4 primary predictions. If >= 2 pass: FAIL.

### N3: Wrong-Direction Check (Diagnostic)
For each passing primary prediction, test one-sided p in opposite direction. Flag if significant.

### N4: Dissolution Contrast (Diagnostic)
Dissolution monitoring_density 0.58 < distillation 0.77 (opposite direction from sublimation). Compute dissolution-derived predictions and check whether they match sublimation predictions.

## Sensitivity Analyses

- Within-Herbal-only: replicate primary battery using only Herbal folios
- Section + REGIME control: partial Spearman adding REGIME dummies
- Raw h_ratio: report all predictions using raw h_ratio (no residualization)

## Verdict Tree

```
S0 fails (n < 60) -> INSUFFICIENT_DATA
S1 fails -> CALIBRATION_FAILURE
S1 passes:
  K = primary predictions passing (out of 4)
  K_perm = primary predictions surviving N1 permutation
  N2 fails (>= 2 random-axis passes) -> SPECIFICITY_FAILURE
  K_perm >= 3 AND N2 passes -> FAMILY_CONTRAST_ALIGNMENT_CONFIRMED
  K_perm == 2 AND N2 passes -> PARTIAL_FAMILY_CONTRAST
  K_perm == 1 AND N2 passes -> WEAK_SIGNAL_ONLY
  K_perm == 0 OR N2 fails  -> FAMILY_CONTRAST_NOT_CONFIRMED
```
