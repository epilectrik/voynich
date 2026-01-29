# C756: A Folio Coverage Optimization Confirmed

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_REASSESSMENT | **Scope:** A

## Finding

A folios are deliberately designed for vocabulary coverage optimization, not discriminative targeting. Real A folios show 11x higher pairwise similarity than randomly-assembled vocabulary pools.

### Evidence

| Metric | Real | Random | Ratio |
|--------|------|--------|-------|
| Mean pairwise Jaccard | 0.246 | 0.022 | 11.0x |
| z-score | 1144 | - | - |
| Percentile | 100th | - | - |

### Coverage Saturation

| A Folios Added | Total MIDDLEs | PP MIDDLEs | PP Coverage |
|----------------|---------------|------------|-------------|
| First 10 | 401 | 243 | 60.1% |
| First 20 | 533 | 288 | 71.3% |
| First 50 | 775 | 355 | 87.9% |
| All 114 | 1013 | 404 | 100% |

The first 10 A folios (by size) cover 60% of all PP vocabulary. The remaining 104 folios contribute only 40% additional coverage.

### Hub Structure

25 MIDDLEs appear in >50% of A folios. **100% of these hub MIDDLEs are PP** (shared with B). Binomial test: p < 0.0001.

The hub vocabulary is the shared operational vocabulary. A folios are structured to guarantee hub availability.

## Implication

This confirms C476 (Coverage Optimality) and explains C755 (A Folio Homogeneity). A folios are not designed to discriminate B programs — they are designed to maximize vocabulary availability for any B program.

### Revised Understanding

| Aspect | Finding |
|--------|---------|
| A folio design goal | Maximize coverage, not discriminate |
| Similarity is intentional | 11x higher than random |
| Hub MIDDLEs | 100% PP — operational vocabulary preserved |
| Coverage efficiency | 60% PP coverage from first 10 folios |

The T6 finding (real worse than random at discrimination) is now explained: A folios are optimized for the OPPOSITE of discrimination — they maximize overlap to ensure broad vocabulary availability.

## Provenance

- Phase: AZC_REASSESSMENT
- Script: t7_coverage_optimization.py
- Related: C476 (Coverage Optimality), C755 (A Folio Homogeneity)
