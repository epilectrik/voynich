# C669: Hazard Proximity Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Mean distance-to-nearest-hazard-class-token **decreases from early to late lines** within folios (rho=-0.104, p=8.3e-06, KW H=15.0, p=1.8e-03). Late-program lines pack non-hazard tokens closer to hazard-class tokens: Q1=2.75 tokens mean distance, Q4=2.45 tokens — a 0.30-token tightening.

This tightening is lane-specific: QO tokens show significant proximity tightening (rho=-0.082, p=0.003), while CHSH tokens do not (rho=-0.020, p=0.51). CHSH tokens are already closer to hazard (mean=2.67) than QO tokens are after tightening (mean=2.44), but CHSH proximity is static.

## Evidence

### Corpus-Wide Hazard Proximity (1831 lines with hazard-class tokens)

| Quartile | Mean Min Distance |
|----------|------------------|
| Q1 | 2.7498 |
| Q2 | 2.5743 |
| Q3 | 2.4902 |
| Q4 | 2.4543 |

Spearman rho = -0.104, p = 8.27e-06. KW H = 15.00, p = 1.82e-03.

### Lane Stratification

| Lane | N lines | Mean Distance | rho | p |
|------|---------|--------------|------|---|
| QO | 1274 | 2.440 | **-0.082** | **0.003** |
| CHSH | 1055 | 2.668 | -0.020 | 0.510 |

QO tokens tighten toward hazard late; CHSH tokens maintain constant proximity throughout.

### Regime Stratification

| Regime | N lines | Q1 | Q4 | Slope |
|--------|---------|-----|-----|-------|
| REGIME_1 | 643 | — | — | -0.212 |
| REGIME_2 | 479 | — | — | **-0.602** |
| REGIME_3 | 140 | — | — | **-0.551** |
| REGIME_4 | 569 | — | — | -0.051 |

REGIME_2 and REGIME_3 show the strongest proximity tightening. REGIME_4 is nearly flat, consistent with its precision-constrained behavior (C494).

## Interpretation

Late-program lines operate within a tighter risk envelope. Non-hazard tokens are positioned closer to hazard-class tokens as the program progresses, reducing the average "distance to risk." This is consistent with convergence behavior: the controller narrows its operating range as the program approaches its terminal state.

The lane asymmetry is informative: QO (energy lane) tokens tighten toward hazard while CHSH (stabilization lane) tokens maintain constant proximity. CHSH tokens are inherently closer to hazard (they include hazard-participating classes 8 and 31), so their proximity is structurally determined rather than positionally modulated. QO tokens, which start farther from hazard, are progressively drawn closer — consistent with the QO fraction decline (C668) that shifts the population CHSH-ward.

REGIME_4's flat proximity profile (slope=-0.051) matches its flat lane balance (C668: +1.4pp) and its precision-constrained identity (C494). REGIME_2's strongest tightening (-0.602) matches its strongest lane drift (C668: -9.9pp).

## Cross-References

- C668: Lane balance trajectory (QO fraction declines late) — QO proximity tightening may be partly compositional
- C645: CHSH post-hazard dominance (75.2%) — CHSH's constant proximity is consistent with its structural adjacency to hazard
- C458: Hazard clamped (CV=0.04-0.11) — hazard density is flat (C667), but proximity tightens: same amount of hazard, more tightly packed
- C494: REGIME_4 precision axis — uniquely flat proximity, lane balance, and kernel trajectories

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 2 (folio_temporal_dynamics.py), Test 6
