# C1471: No Compensatory Safe Opening After Hazardous Closure

**Tier:** 2
**Scope:** B, line, hazard, cross-line, e->y, recovery, compensatory, C1457, C1462, C1463, C1470
**Phase:** 530 (CROSS_LINE_HAZARD)
**Date:** 2026-03-05

## Claim

Lines following high-hazard predecessors do NOT show enriched safe vocabulary at their opening. Instead, e->y (ZERO hazard) tokens are DEPLETED at Q0 of lines following above-median HIGH predecessors (0.223 vs 0.271 rate, 0.82x, Fisher p=0.0001). k-HEAD IMMUNE tokens are also depleted (0.103 vs 0.133, 0.78x). Direct HIGH-ending-to-next-opening analysis confirms: after a HIGH-ending line, the next line's opening has ZERO at 0.251 vs 0.262 baseline (0.96x) and IMMUNE at 0.108 vs 0.119 (0.91x), with Cramer's V=0.030 (negligible). The closure-to-opening bridge is effectively non-existent (V=0.042).

This finding means the e->y safe pathway (C1457-C1462) operates WITHIN lines only. It does not function as a cross-line recovery mechanism. The line-level safety architecture (C1463) is self-contained: each line independently opens safe and closes hazardous, without reference to what the previous line did.

## Evidence

### e->y (ZERO) Rate at Q0 After Above vs Below Median HIGH Lines

| HIGH exposure of line N | N pairs | Q0 ZERO rate (line N+1) | Q0 IMMUNE rate (line N+1) |
|------------------------|---------|------------------------|--------------------------|
| Above-median HIGH | 1,137 | 0.223 | 0.103 |
| Below-median HIGH | 1,201 | 0.271 | 0.133 |
| Ratio (above/below) | -- | **0.823x** | **0.775x** |
| Fisher p (ZERO) | -- | **0.0001** | -- |

Both safe categories are DEPLETED, not enriched. The direction is OPPOSITE to what a compensatory recovery mechanism would produce.

### Direct Closure-to-Opening Bridge

| Line N ending | N pairs | Next Q0 HIGH% | Next Q0 ZERO% | Next Q0 IMMUNE% |
|--------------|---------|---------------|---------------|-----------------|
| HIGH token | 504 | 18.5% | 25.1% | 10.8% |
| Non-HIGH token | 1,834 | 16.0% | 26.2% | 11.9% |
| V | -- | -- | -- | -- |

Cramer's V = 0.030 for full opening profile contingency. The Q4-to-Q0 bridge has near-zero predictive power (V=0.042 for Q4_HIGH tercile vs Q0_ZERO tercile).

### Why the Depletion?

The depletion is a FOLIO-LEVEL COMPOSITION EFFECT, not an anti-recovery mechanism. High-hazard folios have more HIGH tokens everywhere (both Q4 and Q0 of every line), which mechanically reduces the fraction available for ZERO and IMMUNE. This is confirmed by C1470: all cross-line correlation is folio-mediated. The 0.82x depletion disappears when controlling for folio identity.

## Interpretation

The e->y safe pathway (C1457-C1462) is a WITHIN-LINE architectural feature, not a cross-line recovery mechanism. C1462 showed that e->y rate predicts folio forgiveness (rho=+0.43) -- but this operates at folio level (folios with more e->y are safer overall), not at line level (a hazardous line does not trigger compensatory e->y in the next line). Combined with C1470 (all cross-line correlation is folio-mediated), this confirms that lines are independently composed safety units. Each line opens safe and closes hazardous (C1463) without needing or receiving information about the previous line's hazard exposure.

This has a strong implication for the Tier 3 process interpretation: if the system represents a thermal process, each line encodes a self-contained control cycle. The operator does not need to remember what the previous cycle's hazard level was -- the next cycle's safety margin is pre-determined by the folio's overall hazard budget.

## Falsification Criteria

1. If folio-residualized e->y enrichment after HIGH is >1.05x (would indicate genuine cross-line recovery)
2. If Q4_HIGH -> Q0_ZERO rho exceeds +0.10 after folio control (would indicate bridge effect)
3. If Cramer's V for closure-to-opening profile exceeds 0.10

## Method

- 2,338 consecutive line pairs across 82 Currier B folios
- Median split on line N's HIGH fraction (median=0.182)
- Fisher exact test for e->y (ZERO) rate at Q0 of line N+1
- Per-token hazard classification from C1448 frame hazard map
- Quintile assignment within each line for positional analysis

**Script:** `phases/CROSS_LINE_HAZARD/scripts/cross_line_hazard.py`
**Results:** `phases/CROSS_LINE_HAZARD/results/cross_line_hazard.json`

## Dependencies

- C1457-C1462 (e->y safe pathway -- within-line anchor, not cross-line)
- C1463 (line-level zone-hazard routing -- self-contained within each line)
- C1470 (cross-line hazard is folio-mediated -- explains depletion as composition effect)
- C1429 (cross-line category independence -- extended here to hazard resolution)
- C1448 (frame hazard map -- hazard classification)
