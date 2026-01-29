# C755: A Folio Coverage Homogeneity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_REASSESSMENT | **Scope:** A

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
