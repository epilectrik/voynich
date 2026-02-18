# C1105: Bridge Geometry and Density Are Collinear

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_BRIDGE_DYNAMICS (Phase 391)
**Qualifies:** C1017 (macro-dynamics variance decomposition)

---

## Statement

Per-folio bridge density (compositional fraction) and bridge_pc1 (geometric manifold position from C1016) correlate at r=-0.805 (p≈0). Adding bridge density to the C1017 model yields delta-R²=0.007 (F=0.92, p=0.342) — non-significant. The compositional fraction and geometric manifold position measure nearly the same structural property from different angles.

Within BIO specifically (n=20), bridge density adds LOO improvement of +0.0705 (baseline 0.668 → extended 0.738), suggesting it captures within-section variation that the geometric PC misses when REGIME diversity is low (BIO is 85% REGIME_1).

---

## Evidence

### Collinearity
- Pearson r(bridge_density, bridge_pc1): -0.805, p≈0
- Negative sign: bridge_pc1 is a manifold coordinate where high values correspond to low bridge composition

### Incremental R² (P4)
- C1017 baseline R² (B/H/S, n=65): 0.558
- Extended R² (+bridge_density): 0.566
- Delta-R²: 0.007
- F-test: F=0.92, p=0.342
- Bridge density coefficient: -0.177 (negative, consistent with freedom interpretation)

### BIO LOO Exception (P5)
- LOO R² baseline (n=20): 0.668
- LOO R² extended: 0.738
- Improvement: +0.071
- BIO REGIME distribution: 17 REGIME_1, 3 REGIME_3

The improvement within BIO likely occurs because BIO's narrow REGIME range (85% REGIME_1) reduces the geometric PC's discriminative power, allowing the simpler compositional fraction to capture residual variance.

---

## Implication

Bridge density is not a new independent predictor of AXM dynamics — it is the same information as bridge_pc1 in a different form. The C1017 model already captures bridge-related variance through the geometric manifold. The only exception is within-BIO prediction, where the compositional measure outperforms the geometric one due to REGIME homogeneity.

This means the C1035 irreducible residual (~57%) remains genuinely irreducible even after adding bridge density. The design freedom documented in C1104 operates through the SAME mechanism the geometric manifold already partially captures — not through a new, independent pathway.

---

## Provenance

- Phase: 391 (SECTION_BRIDGE_DYNAMICS), Tests P4, P5
- Script: `phases/SECTION_BRIDGE_DYNAMICS/scripts/section_bridge_dynamics.py`
- Results: `phases/SECTION_BRIDGE_DYNAMICS/results/section_bridge_dynamics.json`
- Related: C1016, C1017, C1035, C1048, C1104
