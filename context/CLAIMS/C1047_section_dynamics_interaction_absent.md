# C1047: Section-Dynamics Interaction Absent

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_RESIDUAL_DECOMPOSITION (Phase 366)
**Strengthens:** C1035 (AXM residual irreducible), C1029 (section-parameterized grammar)
**Relates to:** C1017 (macro-state dynamics decomposition), C458 (design freedom)

---

## Statement

Section modulates AXM dynamics **additively** (intercept only), not **interactively** (no slope changes). Three interaction terms tested against C1017 predictors all fail:

| Interaction | dR² | F-stat | p-value |
|-------------|-----|--------|---------|
| Section x PREFIX_entropy | 0.011 | 0.71 | 0.498 |
| Section x hazard_density | 0.007 | 0.43 | 0.650 |
| Section x bridge_PC1 | 0.010 | 0.63 | 0.536 |

Per-section slopes are consistent in direction (all negative for PREFIX and hazard, all positive for bridge) with no sign flips. The C1017 predictor-dynamics relationships are **universal across sections**. Per-section LOO (weighted 0.037) is dramatically worse than global LOO (0.412) — section stratification does not improve prediction.

---

## Evidence

- 65 folios: B=20, H=22, S=23 (C+T excluded: 7 folios, too few)
- Baseline: REGIME + section + PREFIX_entropy + hazard_density + bridge_PC1 (R²=0.558, LOO=0.412)
- Each interaction tested as 2-df F-test increment (section has 3 levels → 2 dummies per interaction)
- All LOO R² values WORSEN with interaction terms (overfitting exceeds signal)
- Conservation confirmed: combined model LOO=0.412 (= baseline), residual 58.8%

---

## Interpretation

C1029 established that sections parameterize grammar WEIGHTS (42.6% of classes section-dependent). C1042-C1046 showed sections modulate line-level grammar at both interior and boundary levels. But this parameterization is entirely captured by section main effects (intercept shifts). The SLOPES — how PREFIX entropy, hazard density, and bridge geometry relate to AXM dynamics — are universal. Section tells you the baseline level of AXM stability, but not how structural properties map to dynamics. This definitively closes the section-interaction pathway for C1035's residual.

---

## Method

- OLS regression with interaction terms (section x predictor) tested one at a time
- F-test for 2-df nested model comparison
- LOO CV for overfitting control
- Bonferroni threshold 0.0167 (3 tests); none even pass uncorrected 0.05

**Script:** `phases/SECTION_RESIDUAL_DECOMPOSITION/scripts/section_residual_decomposition.py`
**Results:** `phases/SECTION_RESIDUAL_DECOMPOSITION/results/section_residual_decomposition.json`
