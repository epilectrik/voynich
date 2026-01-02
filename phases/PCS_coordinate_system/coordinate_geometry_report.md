# Coordinate Geometry Reconstruction

*Generated: 2026-01-01*
*Status: PIECEWISE_SEQUENTIAL*

---

## Purpose

Reconstruct the shape and dimensionality of the coordinate system encoded by
prefix/suffix usage across folios. Purely structural analysis - no semantics.

---

## Summary

| Test | Finding | Result |
|------|---------|--------|
| G-1 Dimensionality | 15 components (90% var) | LOW_DIM |
| G-2 Monotonicity | reversal rate=0.60, loop=False | MIXED |
| G-3 Radial | dist-hazard rho=0.045 | NON-RADIAL |
| G-4 Boundary | 46 boundary folios | NOT_DISTINCT |
| G-5 Continuity | 15 spikes | PUNCTUATED |

---

## G-1: Dimensionality Estimation

| Metric | Value |
|--------|-------|
| Components for 80% variance | 11 |
| Components for 90% variance | 15 |
| Components for 95% variance | 19 |
| Bootstrap stability | 14.7 +/- 0.47 |

**Variance explained (first 5 PCs):** 0.249, 0.118, 0.095, 0.069, 0.067

---

## G-2: Monotonicity vs Manifold

| Metric | Value |
|--------|-------|
| PC1-order correlation | rho=-0.624, p=0.0000 |
| Reversal count | 133 |
| Reversal rate | 0.599 |
| Is monotonic | False |
| Loop ratio | 0.502 |
| Has loop | False |
| Null percentile | 100.0% |

**Structure type:** MIXED

---

## G-3: Radial vs Axial Structure

| Metric | Value |
|--------|-------|
| Mean distance from centroid | 3.229 |
| Distance-hazard correlation | rho=0.045, p=0.4996 |
| Distance-kernel correlation | rho=0.040, p=0.5516 |
| Distance-link correlation | rho=-0.128, p=0.0556 |

**Radial structure:** NO

---

## G-4: Boundary Detection

| Metric | Boundary | Interior | p-value | Effect |
|--------|----------|----------|---------|--------|
| Hazard density | 0.540 | 0.528 | 0.5455 | 0.21 |
| Kernel contact | 0.553 | 0.541 | 0.4403 | 0.17 |
| Link density | 0.325 | 0.331 | 0.4403 | -0.09 |

**Boundaries distinct:** NO

---

## G-5: Local Continuity Geometry

| Metric | Value |
|--------|-------|
| Mean adjacent distance | 2.313 |
| Std adjacent distance | 1.455 |
| Spikes detected | 15 |
| Plateau regions | 54 |
| Null mean distance | 4.430 |
| Percentile (vs null) | 0.0% |

**Continuity type:** PUNCTUATED

---

## Final Verdict

**PIECEWISE_SEQUENTIAL**

Sequential progression with punctuated transitions at section boundaries

### Structural Signatures

- Linear (monotonic, no loop): False
- Radial (distance-intensity correlated): False
- Low-dimensional (<=3 components): False
- Distinct boundaries: False
- Gradual transitions: False

---

*Structural analysis only. No semantic interpretations.*
