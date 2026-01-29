# C751: Coverage Pool-Size Confound

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

Raw best-match assignment is degenerate: f58v (77 MIDDLEs, Section T) serves 75/82 B folios, f58r (88 MIDDLEs) serves the remaining 7. Only 2 of 114 A folios are used. Removing f58r/v shifts dominance to f88v (60 MIDDLEs, Section P), which serves 67/82. Pool size explains this completely.

Coverage ~ pool_size linear regression: slope=0.0088, intercept=0.0170, r=0.883. Pool size explains 78% of coverage variance — even stronger than the Spearman rho=0.85 reported in C735.

### Residual Specificity (Pool-Size Removed)

After subtracting expected coverage (from pool-size regression), the assignment map differentiates:

| Metric | Raw | Residual |
|--------|-----|----------|
| Unique A folios used | 2 | 24 |
| Same-section matches | 1/82 (1%) | 27/82 (33%) |
| Mean gap (best vs 2nd) | N/A | 3.37pp |

The 24 residual-best A folios include folios from all sections (H, P, T), with varying pool sizes. Content specificity exists beneath the pool-size confound.

### Pool Size Driven by Folio Length

Pool size correlates with folio line count: Spearman r=0.584, p=9.1e-12. Section T folios (mean 36 lines) naturally accumulate larger pools than Herbal (mean 12.9 lines) or Pharma (mean 14.2 lines).

| Section | N | Mean Pool | Mean Lines |
|---------|---|-----------|------------|
| H | 95 | 35.6 | 12.9 |
| P | 16 | 51.1 | 14.2 |
| T | 3 | 78.0 | 36.0 |

Section T dominance is a length effect, not a content effect. Its residuals are negative everywhere (-2.3% to -10.5%).

## Implication

Any A-B analysis using raw coverage is confounded by pool size. The degenerate assignment (2 folios serve 82) is a measurement artifact, not structural evidence. C739's best-match lift (2.43x) is genuine specificity, but the identity of the best match is almost entirely pool-size-determined at the raw level. Residual analysis is required to reveal content-level differentiation.

This does NOT invalidate C734-C739 — those constraints describe the coverage architecture correctly. C751 adds the caution that raw best-match identity is pool-size-confounded.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/section_coverage.py` (T8-T10)
- Depends: C734 (coverage architecture), C735 (pool size dominance), C739 (best-match specificity)
