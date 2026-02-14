# C1035: AXM Residual Is Irreducible — No Folio-Level Structural Predictor Explains the 40% Variance

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** AXM_RESIDUAL_DECOMPOSITION (Phase 357)
**Extends:** C1017 (40% residual identified), C1018 (archetype slope anomalies)
**Strengthens:** C458 (hazard clamped, recovery free), C980 (free variation envelope 66.3%)
**Relates to:** C1016 (folio archetypes), C605 (QO lane balance), C1007 (gatekeeper classes), C800 (HT density), C855 (paragraphs as parallel programs)

---

## Statement

The 40% unexplained folio-level AXM self-transition variance (C1017) cannot be decomposed by any tested folio-level structural predictor, either linearly or non-linearly. Six pre-registered predictors (4 primary, 2 secondary) all produce zero incremental R-squared beyond C1017's baseline. Random forest detects no non-linear signal. The residual is genuinely program-specific free variation, consistent with C458's recovery freedom axis and C980's 66.3% free variation envelope. Additionally, C1017's R-squared of 0.564 is moderately overfit (LOO CV R-squared = 0.433, gap = 0.132), suggesting the true explained fraction is closer to 43% than 56%.

---

## Evidence

### S1: C1017 Baseline Replication

| Model | R-squared |
|-------|-----------|
| REGIME + section | 0.413 |
| + PREFIX entropy + hazard density + bridge PC1 | 0.564 |
| LOO CV (full model) | 0.433 |
| Train-CV gap | 0.132 |

The C1017 model replicates exactly. The LOO CV gap of 0.132 exceeds the 0.10 stability threshold, indicating moderate overfitting. The "true" explained variance is approximately 43%, not 56%.

### S2: Univariate Screening (FAIL -- all zero residual signal)

| Predictor | rho(AXM) | p(AXM) | rho(residual) | p(residual) |
|-----------|----------|--------|---------------|-------------|
| paragraph_count | +0.355 | 0.002*** | -0.040 | 0.739 |
| ht_line1_density | -0.296 | 0.012* | +0.052 | 0.667 |
| gatekeeper_fraction | -0.211 | 0.076 | +0.016 | 0.894 |
| qo_fraction | +0.390 | 0.001*** | +0.058 | 0.626 |
| vocab_residual | -0.087 | 0.469 | -0.163 | 0.172 |
| line_count | +0.446 | 0.0001*** | +0.064 | 0.593 |

Three predictors (paragraph_count, qo_fraction, line_count) have Bonferroni-significant raw correlations with AXM self-transition. But ALL residual correlations are essentially zero (max |rho| = 0.163, min p = 0.172). These predictors are entirely absorbed by the existing model -- they predict the same variance that REGIME, section, PREFIX entropy, hazard density, and bridge geometry already capture.

### S3: Incremental R-squared (FAIL -- no predictor exceeds dR2 = 0.013)

| Predictor | dR2 | F | p |
|-----------|-----|---|---|
| paragraph_count | +0.0003 | 0.04 | 0.843 |
| ht_line1_density | +0.0002 | 0.03 | 0.868 |
| gatekeeper_fraction | +0.0028 | 0.39 | 0.537 |
| qo_fraction | +0.0128 | 1.82 | 0.182 |
| vocab_residual | +0.0045 | 0.62 | 0.434 |
| line_count | +0.0123 | 1.74 | 0.193 |

No predictor reaches even p < 0.05. The strongest (qo_fraction, dR2 = 0.013) falls far short of the 0.05 threshold. Adding all six would contribute at most dR2 ~ 0.03, well within overfitting range.

### S5: Archetype-Stratified Analysis (INFORMATIVE)

Within-archetype correlations show sign heterogeneity consistent with C1017's slope-flip finding:
- Archetype 1 (n=10): paragraph rho=-0.39, QO rho=-0.46 (both negative)
- Archetype 5 (n=7): QO rho=+0.68 (positive, p=0.094)
- Archetype 6 (n=30): paragraph rho=-0.31, line_count rho=-0.39* (negative)

But all within-archetype samples are too small for reliable inference (n=5-30). The sign heterogeneity confirms C1017's finding but does not resolve the residual.

### S5b: Archetype Interaction Tests (INFLATED -- confounded)

Adding archetype main effects + predictor x archetype interactions yields dR2 = 0.21-0.24 (all p < 0.0001). However, this test confounds archetype main effects (which trivially predict AXM since archetypes ARE dynamical categories) with genuine interaction effects. The result confirms that archetypes explain AXM variance but does not demonstrate that predictor effects differ across archetypes beyond the archetype intercept.

### S7: Random Forest Non-Linearity Check (FAIL -- no signal)

| Metric | Value |
|--------|-------|
| Train R-squared on C1017 residuals | 0.292 |
| 5-fold CV R-squared | -0.149 +/- 0.121 |
| Permutation z-score | 0.31 |
| Permutation p-value | 0.42 |

CV R-squared is NEGATIVE, meaning the random forest is worse than predicting the mean. Feature importances are near-uniform (0.03-0.22). There is no non-linear structure in the residuals that these predictors can capture.

### S9: Residual Archetype Structure (UNCHANGED)

C1017 residual ~ archetype: F=5.01, p=0.0006. Best model residual ~ archetype: identical (no new predictors entered the model). The archetype-specific structure in the residual is untouched.

---

## Interpretation

This is a definitive negative result with three structural implications:

**1. The 40% residual is genuine free variation, not missing predictors.** Six structurally motivated predictors -- paragraph count (C855), HT density (C800), gatekeeper fraction (C1007), QO lane balance (C605), vocabulary size, and line count -- all fail to explain any residual variance. These are not random choices; they were selected by expert consultation as the most likely candidates based on constraint system analysis. Their collective failure establishes that the residual is not addressable by aggregate folio-level properties.

**2. The C1017 model is moderately overfit.** LOO CV R-squared (0.433) is 0.132 below training R-squared (0.564). The true explained fraction is closer to 43%, making the genuine residual approximately 57%. This does not invalidate C1017's findings (the predictors are real) but calibrates the magnitude.

**3. The residual is the design freedom space.** C458 establishes that hazard transitions are clamped (CV = 0.04-0.11) while recovery transitions are free. C980 establishes a 66.3% program-specific free variation envelope. The 57% residual (LOO-corrected) is consistent with this: each folio's AXM dynamics are independently parameterized within their archetype, and this parameterization is not predictable from structural properties measurable at the folio level. The variation is real, structural, and by design.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | paragraph_count dR2 >= 0.05 | dR2 = 0.0003 | FAIL |
| P2 | gatekeeper_fraction dR2 >= 0.05 | dR2 = 0.0028 | FAIL |
| P3 | At least one predictor Bonferroni-significant with residuals | None (min p = 0.172) | FAIL |
| P4 | LOO CV R-squared within 0.10 of training | Gap = 0.132 | FAIL |
| P5 | RF non-linear signal (p < 0.05) | p = 0.42 | FAIL |
| P6 | Residual archetype F reduced >= 50% | 0% reduction | FAIL |
| P7 | Total explained variance >= 0.65 | R2 = 0.564 | FAIL |

0/7 passed -> RESIDUAL_IRREDUCIBLE

---

## Method

- 72 B folios with >= 50 state transitions (C1010 6-state partition)
- C1017 baseline replicated: REGIME + section dummies, standardized PREFIX entropy + hazard density + bridge geometry PC1
- Bridge geometry: 100D spectral embedding of A-derived compatibility matrix, per-folio bridge centroid PCA
- New predictor computation: paragraph count (par_initial flags), line-1 density, gatekeeper fraction (classes {15,20,21,22,25} of AXM tokens), QO fraction (qo/(qo+ch+sh)), vocabulary size (residualized against token count), line count
- Univariate Spearman with Bonferroni correction (p < 0.0083 for 6 tests)
- Incremental R-squared via F-test nested model comparison
- Random forest: 500 trees, sqrt features, min 5 leaf samples, 200-permutation null
- Leave-one-out cross-validation for model stability

**Script:** `phases/AXM_RESIDUAL_DECOMPOSITION/scripts/axm_residual_decomposition.py`
**Results:** `phases/AXM_RESIDUAL_DECOMPOSITION/results/axm_residual_decomposition.json`

---

## Verdict

**RESIDUAL_IRREDUCIBLE**: The 40% AXM self-transition residual (C1017) is not reducible to any tested folio-level structural predictor -- not paragraph count, HT density, gatekeeper fraction, QO fraction, vocabulary size, or line count; not linearly, not non-linearly, not through archetype interactions. The C1017 model is moderately overfit (LOO gap 0.132), making the true residual approximately 57%. This variance is the free design space: each program's AXM dynamics are independently tuned within the grammar's constraints, consistent with C458 (recovery freedom) and C980 (66.3% free variation envelope).
