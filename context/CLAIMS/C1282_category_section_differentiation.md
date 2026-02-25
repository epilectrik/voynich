# C1282: Category Predicts B Section Membership

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

Folio-level category composition predicts B section membership. Chi2=759.8, V=0.106, p<0.001 (4 sections x 8 categories). 6/8 categories differentiate sections at Bonferroni level by Kruskal-Wallis (CONTAINMENT H=32.2, THERMAL H=35.4, MARKING H=28.4, TRANSITION H=26.1, STAGING H=24.7, FLOW H=17.1). Section B is THERMAL-heavy (26.9%), Section C is FLOW-heavy (23.5%), Section H is FLOW/TRANSITION-heavy, Section S is THERMAL/FLOW-heavy.

## Architecture

- **Categories compress section variation.** C1134 showed 74% of section JS divergence comes from PP frequency modulation. Categories capture meaningful section-level variation in an 8-dimensional representation rather than the full MIDDLE frequency vector.
- **6/8 categories differentiate.** Only MONITORING and OPERATION fail Bonferroni. The remaining 6 categories carry section-diagnostic information, meaning most of the category system is section-aware.
- **Extends C1029.** C1029 established section-parameterized grammar weights. C1282 shows categories are a natural compression of this parameterization — each section has a characteristic category profile.

## Key Findings

| Section | Top 3 Categories |
|---------|-----------------|
| B | THERMAL 26.9%, OPERATION 16.7%, FLOW 16.6% |
| C | FLOW 23.5%, TRANSITION 19.2%, THERMAL 16.4% |
| H | FLOW 18.8%, TRANSITION 17.0%, OPERATION 16.4% |
| S | THERMAL 25.5%, FLOW 21.0%, TRANSITION 16.2% |

| Metric | Value |
|--------|-------|
| Chi-squared | 759.8 |
| Cramer's V | 0.106 |
| KW significant at Bonferroni | 6/8 |
| N folios | 80 |

## Provenance

- Extends C1134 (PP frequency modulation) with category compression
- Extends C1029 (section-parameterized grammar) with category dimension
- Complements C1266 (A section atom differentiation) at B execution level
