# C639: Sister Pair Variance Decomposition

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** SISTER_PAIR_CHOICE_DYNAMICS

## Statement

Hierarchical variance decomposition of folio-level ch_preference (n=79 folios with complete data) explains **47.1% of total variance** (adj R2=32.3%) using section, REGIME, quire, MIDDLE composition, and lane balance. The remaining **52.9% is unexplained "free choice"** -- each folio independently determines over half of its sister pair preference. The variance budget is dominated by **shared variance (36.4%)** among highly correlated predictors, with only 10.7% uniquely attributable to individual predictor groups. The largest unique contributor is quire (3.8%), followed by lane balance (2.7%) and MIDDLE composition (2.6%).

## Evidence

### Hierarchical Regression (Rank-Based OLS)

| Step | Predictors | R2 | adj_R2 | delta_R2 |
|------|-----------|------|--------|----------|
| 1 | Section | 0.354 | 0.319 | 0.354 |
| 2 | + REGIME | 0.360 | 0.297 | 0.006 |
| 3 | + Quire | 0.419 | 0.280 | 0.058 |
| 4 | + MIDDLE comp | 0.443 | 0.300 | 0.025 |
| 5 | + Lane balance | 0.471 | 0.323 | 0.027 |

Section alone explains 35.4%. REGIME adds negligible incremental variance (0.6%) because its information is already captured by section. The adjusted R2 decreases from Step 2 onward (model becoming overfit with 17 predictors and 79 observations).

### Unique Variance (Semipartial)

| Predictor | Unique R2 | % of Total |
|-----------|-----------|------------|
| Quire | 0.038 | 3.8% |
| Lane balance | 0.027 | 2.7% |
| MIDDLE comp | 0.026 | 2.6% |
| REGIME | 0.012 | 1.2% |
| Section | 0.004 | 0.4% |
| **Shared** | **0.364** | **36.4%** |
| **UNEXPLAINED** | **0.529** | **52.9%** |

The massive shared variance (36.4%) reflects tight correlations among predictors: section, REGIME, quire, and compositional metrics all partially capture the same underlying folio-level structure. Section explains 35.4% total but only 0.4% unique -- almost all section variance overlaps with other predictors.

### Residual Analysis

- Lag-1 autocorrelation: r=0.096 (no sequential dependency)
- Durbin-Watson: 1.695 (acceptable, no autocorrelation)
- Size effect (residuals vs token count): r=-0.063 (none)
- Outliers (|z|>2): 5 folios (expected ~4 by chance)
- Skewness: -0.330, excess kurtosis: -0.118 (approximately normal)
- Residuals show no structure -- the unexplained 52.9% appears genuinely random

### Definition Notes

Lane balance uses C603-C605 EN subfamily definitions (EN_CHSH=10 classes, EN_QO=7 classes), not canonical definitions (EN_CHSH=2, EN_QO=10), to maintain comparability with C605 (rho=-0.506).

## Interpretation

Sister pair choice (ch vs sh) is a **majority free-choice variable**: 52.9% of its variance cannot be explained by any measured structural predictor. The explained 47.1% is overwhelmingly shared among predictors (36.4%), reflecting the tight coupling between section, REGIME, class composition, and MIDDLE makeup. No single predictor "owns" the sister pair choice.

The practical implication: **a folio's section determines a baseline ch_preference** (section S/T have higher ch_preference, section B/C lower), but within any section, individual folios freely vary by over half the total range. This is consistent with sister pairs being genuine alternatives (C408) that encode per-folio "choices" not fully constrained by the grammar.

The clean residuals (no autocorrelation, no size effects) suggest the unexplained variance is not an artifact of missing spatial or temporal structure -- it appears to be genuine per-folio freedom.

## Extends

- **C412**: ch_preference anticorrelates with escape (rho=-0.326) -- now decomposed: ~47% structural, ~53% free
- **C604**: 27.6% of C412 is REGIME-mediated -- REGIME adds only 0.6% incremental and 1.2% unique beyond section
- **C605**: Lane balance predicts escape better than ch_preference -- lane balance contributes 2.7% unique to ch_preference itself
- **C637**: MIDDLE composition explains 22.9% total (here: 2.6% unique after other predictors)
- **C638**: Quire confounded with section; quire contributes 3.8% unique (likely residual section-within-quire variation)

## Related

C408, C410, C412, C604, C605, C637, C638

## Provenance

- **Phase:** SISTER_PAIR_CHOICE_DYNAMICS
- **Date:** 2026-01-26
- **Script:** choice_variance_decomposition.py
