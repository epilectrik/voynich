# Phase 601: SAFETY_STYLE_MODERATION — Pre-Registration

**Date:** 2026-03-17
**Status:** LOCKED — hash this file before loading any Voynich response data

## Core Question

Does A2-like apparatus forgivingness/authenticity regime shift safety style toward transformative intervention? Tests the mechanism behind C1740 (Stars safety substitution) and C1739 (H:R2 reversal).

## Response Variable

**safety_balance** = ey_rate - ii_rate per folio
- ey_rate: fraction of Currier B text tokens (H-track, non-label, non-asterisk) with MIDDLE HEAD='e' AND TERMINAL='y'
- ii_rate: fraction with max_consecutive_i(middle) >= 2

## Moderator Variables

- **mean_null_dye**: per-folio apparatus forgivingness (from t0_opportunity_normalization.json)
- **strong_close_fraction**: per-folio fraction of eligible close events that are STRONG (from t0_opportunity_normalization.json)
- **profile**: apparatus family A1/A2/A3 (from t0_opportunity_normalization.json)
- **DYE_advantage**: per-folio intervention-productivity (from t0_feature_matrix_assembly.json, space_B.raw[][0])
- **section**: Currier B section (from Transcript)
- **REGIME**: thermal intensity proxy (from regime_folio_mapping.json)

## Sample

76 Currier B folios (intersection of manifold, opp_norm, REGIME mapping).

## Test Specifications

### S2: Stars Safety-Balance Confirmatory Anchor
- Mann-Whitney: S:R1 (n=10) vs S:R3 (n=12) safety_balance
- Prediction: R1 > R3
- If S2 FAILS: CALIBRATION_FAILURE

### P0: Within-Section Variance Diagnostic
- ICC of mean_null_dye partitioned by section
- NOT gated

### P1: A2-Like Forgivingness Predicts Transformative Safety Preference (n=76)
- Section-controlled partial Spearman: mean_null_dye vs safety_balance
- Prediction: NEGATIVE (high null-recoverability + high authenticity threshold → preventive insufficient → transformative rescue)
- Threshold: section-controlled p < 0.05
- Sensitivity: raw (no control), Herbal-only descriptive

### P2: Forgivingness Explains Within-REGIME Safety Variance in Herbal (n=25) — CORE TEST
- Herbal viable cells: H:R2 (11), H:R3 (5), H:R4 (9). Exclude H:R1 (n=2).
- Primary: Nested OLS — Model A (safety_balance ~ REGIME) vs Model B (safety_balance ~ REGIME + mean_null_dye). F-test.
- Robustness: Rank-based partial Spearman (mean_null_dye vs safety_balance, controlling for REGIME dummies)
- Prediction: mean_null_dye significant
- Threshold: F-test p < 0.05 OR delta-R² > 0.03 (OLS). Rank-partial p < 0.05 (Spearman).
- Sensitivity: full interaction model reported descriptively

### P3: Herbal A3 Surgery Test (n=14)
- Remove A2 from Herbal → H(A3):R3 = 5, H(A3):R4 = 9
- Mann-Whitney: R3 vs R4 safety_balance
- Prediction: R4 > R3 (tentative — precision axis C494, not simply "more preventive")
- Threshold: concordant direction AND p < 0.10

### P4: Closure Authenticity Interaction (n=76)
- Section-controlled partial Spearman: strong_close_fraction vs safety_balance
- Prediction: POSITIVE (folios with more strong closures sustain preventive safety)
- Threshold: p < 0.10

### S1a: DYE Orthogonality Within Stars (n=22)
- Partial Spearman: DYE_advantage vs safety_balance, controlling for REGIME
- Prediction: NOT significant

### S1b: DYE Orthogonality All Folios (n=76)
- Section-controlled partial Spearman: DYE_advantage vs safety_balance
- Prediction: weak/null

### S3: A2 Dummy Sensitivity (descriptive)
- OLS: safety_balance ~ is_A2 + section
- NOT gated

## Decision Logic

```
S2 FAILS:                    CALIBRATION_FAILURE (stop)
P2 passes + S2 passes:       SAFETY_STYLE_MODERATION_SUPPORTED
P2 passes + P3 trends right: A2_REVERSAL_MECHANISM_SUPPORTED
P1 passes + P2 passes:       FORGIVINGNESS_ASSOCIATED_WITH_SAFETY_STYLE
P1 passes + P2 fails:        GLOBAL_ASSOCIATION_WITHOUT_HERBAL_MECHANISM
Only S2 passes:              STARS_ONLY_REPLICATION
0 pass:                      SAFETY_STYLE_MODERATION_NOT_CONFIRMED
```
