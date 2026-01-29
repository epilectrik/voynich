# C725: Across-Line Accessibility Gradient

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** B

## Finding

Lines later in a B folio show higher mean accessibility under A-folio filtering (Spearman rho=0.124, p=8.6e-10). 56/82 B folios (68.3%) show positive correlation between line position and mean token accessibility. The effect is moderate: first-third mean=0.276, middle-third=0.286, last-third=0.306 (~10% increase).

This is consistent with C325 (Completion Gradient: STATE-C increases with position) and C556's SETUP-WORK transition: early lines establish B-specific scaffold vocabulary, later lines engage more pipeline-shared content.

## Implication

B folios have a directional accessibility trajectory: they open with more B-exclusive vocabulary and progressively incorporate more A-accessible tokens. This is a population tendency (68.3% of folios), not a universal rule (31.7% show the opposite). The gradient is weak (rho=0.124) — individual line accessibility varies widely, but the aggregate trend is real.

## Key Numbers

| Metric | Value |
|--------|-------|
| Global Spearman rho | 0.124 (p=8.6e-10) |
| Mean per-folio rho | 0.130 |
| Median per-folio rho | 0.152 |
| Positive folios | 56/82 (68.3%) |
| Negative folios | 26/82 (31.7%) |
| First-third mean accessibility | 0.276 |
| Middle-third mean accessibility | 0.286 |
| Last-third mean accessibility | 0.306 |

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (T3)
- Consistent with: C325 (completion gradient), C556 (SETUP-WORK transition)
- Note: Effect size is small; 31.7% of folios show reverse direction
