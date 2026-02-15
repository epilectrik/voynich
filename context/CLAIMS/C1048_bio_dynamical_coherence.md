# C1048: BIO Section Dynamical Coherence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_RESIDUAL_DECOMPOSITION (Phase 366)
**Extends:** C552 (section-specific role profiles: BIO = +CC +EN thermal-intensive)
**Relates to:** C458 (design freedom), C1017 (dynamics decomposition), C1035 (residual irreducible)

---

## Statement

BIO section (n=20 folios) shows uniquely high dynamical predictability:

| Section | n | R² (train) | R² (LOO) | Gap |
|---------|---|-----------|----------|-----|
| BIO | 20 | 0.860 | **0.754** | 0.106 |
| HERBAL | 22 | 0.226 | -0.242 | 0.468 |
| STARS_RECIPE | 23 | 0.301 | -0.319 | 0.620 |

C1017 predictors (PREFIX entropy, hazard density, bridge geometry) explain 75% of BIO's AXM variance even under LOO cross-validation. HERBAL and RECIPE contain genuine free variation that cannot be predicted from aggregate structural properties (negative LOO = worse than predicting the mean).

---

## Evidence

- Per-section OLS with adapted REGIME encoding (BIO: 1 dummy, HERBAL: 2, RECIPE: 2)
- BIO: 85.7% REGIME_1, tight operational clustering
- HERBAL: 68% REGIME_4, moderate regime spread
- RECIPE: 57% REGIME_1, 22% REGIME_2, 22% REGIME_3 — maximum regime diversity

---

## Interpretation

BIO programs cluster in REGIME_1 with high ENERGY density (C552). Their recovery strategy is constrained by thermal intensity — there is little room for design freedom. This makes BIO the section where C1017 predictors are genuinely load-bearing. HERBAL and RECIPE distribute across multiple REGIMEs, creating program-specific variation that the model cannot capture. The "design freedom" identified by C458 and C1035 is concentrated in non-BIO sections. Future work seeking new dynamical predictors should test in BIO first (where signal/noise is favorable) and expect that HERBAL/RECIPE will remain noise-dominated.

---

## Method

- Separate OLS regressions per section with within-section standardization
- LOO CV per section (critical for n=20-23)
- REGIME dummies adapted per section (levels with < 3 folios collapsed or dropped)
- Continuous predictors: PREFIX_entropy, hazard_density, bridge_PC1 (per C1017)

**Script:** `phases/SECTION_RESIDUAL_DECOMPOSITION/scripts/section_residual_decomposition.py`
**Results:** `phases/SECTION_RESIDUAL_DECOMPOSITION/results/section_residual_decomposition.json`
