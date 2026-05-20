# C755: A Folio Coverage Homogeneity [DEMOTED Tier 2 → Tier 3, 2026-05-19]

**Status:** DEMOTED via batch-sweep audit | **Tier:** 3 (was Tier 2) | **Phase:** AZC_REASSESSMENT | **Scope:** A

**Demotion narrative (2026-05-19):** The descriptive measurement survives (real A folios at 0th percentile vs 100 synthetic for discrimination, mean discrimination 1.064 vs synthetic mean 1.281). The **interpretation as "deliberate coverage optimization" is demoted to Tier 3** because it depends on C476 (Coverage Optimality) which was retracted via audit (`phases/C476_AUDIT/`). With C476's "coverage" framing falsified, the C755 interpretation flip ("real worse than random = deliberate optimization") loses its foundation. This is structurally the same pattern that broke C476 — finding "real worse than baseline" reframed as "deliberate" without independent grounding. See `feedback_broken_baseline_audit.md`. The descriptive observation remains as Tier 3 measurement-only pending interpretation re-grounding.

## Finding

Real A folios are more homogeneous than randomly-assembled vocabulary pools. When compared against 100 synthetic A folio sets (same size distribution, random PP vocabulary), real A folios show LOWER discrimination of B folios.

### Comparison

| Metric | Real A Folios | Synthetic (mean) | Percentile |
|--------|---------------|------------------|------------|
| Mean discrimination | 1.064 | 1.281 | 0th |
| Unique best-matches | 3 | 5.3 | 19th |

Real A folios are at the **0th percentile** of synthetic discrimination — worse than every randomly-generated set.

## Implication

This is not a failure — it is evidence of **deliberate coverage optimization**. A folios are designed to provide BROAD, OVERLAPPING vocabulary coverage, not NARROW, DISCRIMINATIVE targeting.

### Interpretation

If A folios were meant to route specific content to specific B programs, they would need to be diverse (different vocabulary in different folios). Instead, they are highly similar, maximizing the vocabulary available to any B program regardless of which A context is active.

This aligns with C476 (Coverage Optimality): A achieves greedy-optimal coverage with hub savings. Homogeneity is the MECHANISM of coverage optimization.

### Revised A-B Model

| Aspect | Old Understanding | Revised Understanding |
|--------|-------------------|----------------------|
| A folio diversity | Expected (for routing) | Low (for coverage) |
| Discrimination source | A content | AZC position + role hierarchy |
| A folio function | Target selector | Vocabulary provider |

## Provenance

- Phase: AZC_REASSESSMENT
- Script: t6_null_model_comparison.py
- Related: C476 (Coverage Optimality)
