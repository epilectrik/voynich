# C1269: AZC Zone Category Specialization

**Tier:** 2
**Scope:** AZC
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

AZC positional zones (R, C, S, P) have statistically distinct operational category distributions. Chi-squared=52.18 (4 zones x 8 categories), p=0.000180, Cramer's V=0.084. R (1,161 tokens) is TRANSITION/FLOW-heavy; C (546) is TRANSITION/OPERATION-enriched; P (357) is TRANSITION/STAGING-heavy; S (394) is TRANSITION/FLOW/OPERATION. The category system is not orthogonal to positional zone.

## Architecture

- **Position encodes category bias, not just legality.** C313 established that position constrains legality. C1269 extends this: positions also partition vocabulary by operational theme, not just by compatibility signature.
- **Effect is small but real.** V=0.084 is much weaker than A's record-level coherence (C1261, d=9.7). AZC's category structure is coarse relative to A.
- **All zones are TRANSITION-dominated.** The distinction is in secondary categories, not primary. TRANSITION ranges from 23.2% (A/C) to 27.9% (Zodiac) across the corpus.

## Key Findings

| Metric | Value |
|--------|-------|
| Zones tested | R, C, S, P |
| Total categorized tokens | 2,458 |
| Chi-squared | 52.18 |
| Cramer's V | 0.084 |
| p-value | 0.000180 |

## Provenance

- Extends C313 (position constrains legality) into category dimension
- Extends C442 (compatibility grouping) with category interpretation
- Complements C1261 (A record category coherence) at AZC level
