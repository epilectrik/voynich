# C1104: Bridge Density Enables Dynamical Freedom

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_BRIDGE_DYNAMICS (Phase 391)
**Extends:** C458 (recovery freedom), C980 (free variation envelope), C1035 (AXM residual irreducible)
**Mechanism for:** C1048 (BIO predictable, HERBAL unpredictable)

---

## Statement

Per-folio bridge MIDDLE density positively correlates with |c1017_residual| — the magnitude of unexplained AXM dynamics (Spearman rho=+0.277, p=0.025, n=65). Higher bridge density → MORE deviation from the structural model, not less. The relationship is monotonic (no quadratic term, p=0.757) and consistent across sections (all within-section rhos positive, none individually significant).

Bridge vocabulary provides behavioral options that programs exercise. The section with the highest bridge density (Herbal, 0.695) has the highest AXM variance (0.0148), while the section with the lowest bridge density among the three main sections (Stars/Recipe, 0.482) has the lowest variance (0.0059).

---

## Evidence

### P2: Bridge Density vs |C1017 Residual|
- Overall: rho=+0.277, p=0.025 (n=65, B/H/S sections)
- Within BIO (B): rho=+0.245, p=0.297 (n=20, same direction)
- Within Herbal (H): rho=+0.108, p=0.633 (n=22, same direction)
- Within Stars (S): rho=+0.187, p=0.394 (n=23, same direction)

All three sections show the same positive direction. Individual non-significance is expected at n=20-23.

### P3: AXM Variance by Section
| Section | Mean AXM | Variance | Std | Bridge Density |
|---------|----------|----------|-----|----------------|
| H (Herbal) | 0.573 | 0.0148 | 0.122 | 0.695 |
| B (Bio) | 0.743 | 0.0078 | 0.089 | 0.609 |
| S (Stars) | 0.689 | 0.0059 | 0.077 | 0.482 |

Levene's test: W=1.66, p=0.198 (not significant, but ranking is H > B > S consistently)

### P6: Monotonicity Confirmation
- Spearman rho: +0.277 (rank-based)
- Pearson r: +0.243 (linear)
- Same sign: yes. Magnitude ratio: 0.876 (within 20%)
- Quadratic term: F=0.097, p=0.757 (non-significant)

### P6 Secondary: Bridge Density vs AXM Self-Transition
- Spearman rho=-0.371, p=0.002 (replicates C1016.T8 rho=-0.308)
- Higher bridge density → weaker AXM attractor → more dynamical options

---

## Interpretation

The prediction was that bridge density would anticorrelate with residual magnitude — that more bridge vocabulary would make programs more predictable. The opposite is true. This reframes the C458/C980 design freedom finding:

**Design freedom is not noise — it is enabled by vocabulary composition.** Programs built from bridge vocabulary (general, compatible MIDDLEs per C1013) have more legal transitions available. They use this expanded option space to tune their dynamics program-specifically. Programs built from specialized vocabulary (non-bridge MIDDLEs) are more constrained and therefore more predictable.

This explains the C1048 paradox directly: BIO is predictable (LOO R²=0.754) because it has moderate bridge density (0.609) constrained within REGIME_1 (17/20 folios). Herbal is unpredictable (LOO R²=-0.242) because it has high bridge density (0.695) spread across REGIME_3 and REGIME_4 — maximum vocabulary freedom combined with maximum REGIME diversity.

---

## Provenance

- Phase: 391 (SECTION_BRIDGE_DYNAMICS), Tests P2, P3, P6
- Script: `phases/SECTION_BRIDGE_DYNAMICS/scripts/section_bridge_dynamics.py`
- Results: `phases/SECTION_BRIDGE_DYNAMICS/results/section_bridge_dynamics.json`
- Related: C458, C980, C1013, C1035, C1048, C1099
