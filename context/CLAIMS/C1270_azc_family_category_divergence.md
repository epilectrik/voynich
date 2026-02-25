# C1270: AZC Family Category Divergence

**Tier:** 2
**Scope:** AZC
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

Zodiac and A/C families within AZC have statistically distinct operational category distributions. Chi-squared=40.23, p=0.000001, Cramer's V=0.122. Zodiac (1,099 tokens) is enriched in TRANSITION (27.9%) and FLOW (21.5%); A/C (1,620 tokens) is enriched in STAGING (17.0%) and OPERATION (13.6%). The family distinction carries operational category information, not just structural organization.

## Architecture

- **Family is not just scaffold.** C430-C436 established family-agnostic mechanism (legality works the same way in both families). C1270 shows the vocabulary content that populates each family differs in category composition.
- **Mechanism vs content distinction.** The legality mechanism is family-agnostic (C430-C436), but the vocabulary populating each family is category-biased. Different families serve different operational emphases.
- **Zodiac = more THERMAL.** Zodiac's 17.6% THERMAL vs A/C's 14.8% aligns with Zodiac's ordered R-series structure (C432) potentially serving thermal monitoring roles.

## Key Findings

| Metric | Value |
|--------|-------|
| A/C tokens | 1,620 |
| Zodiac tokens | 1,099 |
| Chi-squared | 40.23 |
| Cramer's V | 0.122 |
| p-value | 0.000001 |

## Provenance

- Extends C430-C436 (family-agnostic mechanism) with content-level distinction
- Extends C471 (PREFIX encodes family affinity) into category dimension
- Complements C1269 (zone category specialization) at family level
