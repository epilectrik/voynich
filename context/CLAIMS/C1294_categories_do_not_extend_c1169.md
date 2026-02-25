# C1294: Category Fractions Do Not Extend C1169 AXM Model

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_REGIME_INTEGRATION (Phase 456)
**Date:** 2026-02-24

## Statement

No category fraction correlates with C1169 AXM model residuals. All 8 Spearman correlations are non-significant after Holm correction (all |rho| < 0.14, all p > 0.26). C1169 replication: R2=0.853, LOO=0.726. The 27% AXM residual variance is not explained by category composition. N=65 folios with complete data.

## Architecture

- **Validates C1169 closure.** C1289 found strong raw correlations (THERMAL rho=+0.520, TRANSITION rho=-0.519 with AXM self-transition). But the C1169 model already captures this signal through REGIME dummies + PREFIX entropy + hazard density + boundary geometry. Categories add zero incremental information.
- **Signal absorption pathway.** REGIME dummies absorb kernel-mediated category variance (C1291). PREFIX entropy absorbs PREFIX-mediated escape variance (C1277). The existing model predictors fully mediate the category-AXM relationship.
- **C1169 residual remains genuine design freedom.** The 27% unexplained AXM variance is not reducible to category composition, confirming C1169's characterization as irreducible design freedom within the grammar.

## Provenance

- Validates C1169 (27% residual, LOO R2=0.732) as comprehensive
- Resolves C1289 (THERMAL/TRANSITION AXM correlation) as absorbed by existing predictors
- Confirms C458 (design asymmetry) at category level: categories constrain execution grammar but not macro-state dynamics beyond what kernels already determine
