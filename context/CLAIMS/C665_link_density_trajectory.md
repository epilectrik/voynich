# C665: LINK Density Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

LINK density is **stationary within folios** (rho=+0.020, p=0.333, KW H=2.06, p=0.559). Monitoring does not concentrate at any particular folio position. Note: C365 (within-line uniformity) was refuted by C805 (LINK shows boundary enrichment at line edges). This finding (within-folio stationarity) remains valid independently.

Regime stratification shows REGIME_3 has the steepest positive LINK slope (+0.051) and REGIME_2 the only negative slope (-0.012), but no regime breaks the corpus-wide null result.

## Evidence

### Corpus-Wide LINK Trajectory (2420 lines)

| Quartile | LINK density |
|----------|-------------|
| Q1 | 0.1288 |
| Q2 | 0.1343 |
| Q3 | 0.1369 |
| Q4 | 0.1451 |

Spearman rho = +0.020, p = 0.333. KW H = 2.06, p = 0.559.

### Regime Stratification

| Regime | Q1 | Q4 | Slope |
|--------|-----|-----|-------|
| REGIME_1 | 0.148 | 0.176 | +0.029 |
| REGIME_2 | 0.128 | 0.116 | -0.012 |
| REGIME_3 | 0.139 | 0.190 | +0.051 |
| REGIME_4 | 0.108 | 0.126 | +0.019 |

## Interpretation

Monitoring is deployed uniformly throughout program execution. There is no "cautious startup" (early LINK) or "final verification" (late LINK) pattern. Every line of the program maintains the same monitoring posture.

Combined with C609 (13.2% corpus-wide), LINK density is stationary at the folio and cross-folio scales. Note: C365's within-line uniformity claim was refuted by C805 (LINK shows boundary enrichment), so the "all scales" position-invariance claim no longer holds. Within-line, LINK is boundary-enriched; within-folio and across-folio, LINK density is stationary.

## Cross-References

- C365: ~~LINK spatially uniform within lines~~ REFUTED by C805 (boundary enrichment)
- C609: LINK density 13.2% (token-level)
- C458.a: Hazard-LINK anticorrelation (r=-0.945) — if hazard is flat within folios (C667), LINK being flat is consistent

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 1 (folio_temporal_metrics.py), Test 2
