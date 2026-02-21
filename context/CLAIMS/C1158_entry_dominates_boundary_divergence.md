# C1158: Entry Divergence Dominates the Boundary Divergence Effect

**Tier:** 2
**Scope:** B, line, AXM residual
**Phase:** BOUNDARY_DIVERGENCE_DECOMPOSITION (Phase 414)
**Depends on:** C1156, C1157, C1007

## Statement

The C1157 boundary divergence effect on the AXM residual is entry-dominated: entry divergence (JSD of entry vs interior 6-state transitions) adds dR²=0.098 (F=17.06, p=0.0001) to the C1035 baseline, while exit divergence adds only dR²=0.028 (F=4.09, p=0.048). Entry is 3.5× stronger than exit. Partial correlations confirm: entry vs AXM controlling for exit is rho=-0.260 (p=0.020); exit vs AXM controlling for entry is rho=-0.192 (p=0.057, borderline). Adding both components together yields dR²=0.100, barely exceeding entry alone — exit carries almost no independent information.

## Evidence

| Component | dR² | F | p | LOO R² |
|-----------|-----|---|---|--------|
| Baseline (C1035) | — | — | — | 0.433 |
| + Entry only | 0.098 | 17.06 | 0.0001 | 0.501 |
| + Exit only | 0.028 | 4.09 | 0.048 | 0.447 |
| + Both | 0.100 | 8.66 | 0.0005 | 0.471 |

**Bivariate:** Entry vs AXM rho=-0.664 (p<0.0001); Exit vs AXM rho=-0.693 (p<0.0001). Both are strong bivariately, but entry carries the independent signal.

**Component means:** JSD_entry mean=0.174, JSD_exit mean=0.176 (similar magnitude; the dominance is in predictive power, not in divergence size).

## Structural Implication

This contradicts the gatekeeper hypothesis (C1007 predicts exit-enriched gatekeeping). The boundary divergence effect is NOT about how lines end (exit gatekeeping) — it's about how lines BEGIN relative to their interior. Folios where the entry transition profile is most distinct from the interior are folios with the most dynamic, varied macro-state behavior. The entry captures a "reset to base state" intensity that predicts procedural complexity.
