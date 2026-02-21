# C1160: Boundary Divergence Is Section-Confounded but Carries Independent Signal

**Tier:** 2
**Scope:** B, line, section, AXM residual
**Phase:** BOUNDARY_DIVERGENCE_DECOMPOSITION (Phase 414)
**Depends on:** C1045, C1157

## Statement

Section membership explains 70.2% of boundary divergence variance (ANOVA F=38.22, p<0.0001). However, boundary divergence carries independent predictive power for AXM dynamics beyond section: partial correlation BD vs AXM controlling for section is rho=-0.459 (p=0.0001), and BD adds dR²=0.135 (F=17.28, p=0.0001) to a section-only AXM baseline. Boundary divergence is not purely a section proxy — it captures within-section variation in line-level transition structure that predicts folio dynamics.

## Evidence

| Test | Value |
|------|-------|
| Section R² on BD | 0.702 |
| Section ANOVA | F=38.22, p<0.0001 |
| Partial rho (BD vs AXM \| section) | -0.459, p=0.0001 |
| Section-only AXM R² | 0.364 |
| Section + BD AXM R² | 0.499 |
| BD increment on section | dR²=0.135, F=17.28, p=0.0001 |

**LOO R²:** Section-only 0.259, Section+BD 0.330. Genuine out-of-sample improvement.

## Structural Implication

C1045 showed section-dependent boundary role composition with moderate effect (Cramer's V=0.09-0.10). C1160 extends this: sections strongly determine the overall level of boundary divergence, but individual folios within a section still vary meaningfully. The section sets a "baseline reset intensity" for its material domain; individual programs then modulate around that baseline according to their specific procedural requirements. This two-level structure (section sets range, program sets position) parallels C1152's vocabulary-dynamics layer separation.
