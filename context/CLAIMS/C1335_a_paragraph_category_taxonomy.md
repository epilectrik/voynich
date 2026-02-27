# C1335: A Paragraph Category Taxonomy

**Tier:** 2
**Scope:** A (all sections)
**Phase:** A_PARAGRAPH_CATEGORY_ARCHITECTURE (468)

## Constraint

A paragraphs form 5 distinct category-based types, defined by their dominant operational category. Paragraphs of the same type are significantly more similar to each other (within-type JSD 0.074) than to paragraphs of different types (between-type JSD 0.108). This gap (0.034) is far larger than null expectation (0.0002) and survives section stratification.

## Evidence

From a_paragraph_category_architecture.py test A2:

**5 types with 5+ members (241 eligible paragraphs):**

| Type | n | Dom. fraction | Top-2 secondary | Section dist |
|------|---|---------------|-----------------|--------------|
| STAGING | 105 | 30.3% | FLOW, TRANSITION | H:88, P:16, T:1 |
| FLOW | 48 | 28.4% | STAGING, TRANSITION | H:38, P:3, T:7 |
| TRANSITION | 42 | 30.0% | STAGING, FLOW | H:34, P:7, T:1 |
| THERMAL | 33 | 30.7% | STAGING, TRANSITION | H:11, P:21, T:1 |
| OPERATION | 12 | 29.7% | TRANSITION, MARKING | H:11, T:1 |

- 6th type (MARKING) has only 1 paragraph; CONTAINMENT and MONITORING have 0

**Type distinctness:**

- Within-type mean JSD: 0.074
- Between-type mean JSD: 0.108
- Gap: 0.034
- Mann-Whitney z: -45.67, p < 0.001
- Null mean gap (shuffled types): 0.0002
- Permutation p: < 0.001

**Section stratification:**

| Section | n | Within-type JSD | Between-type JSD | Gap |
|---------|---|-----------------|------------------|-----|
| H | 183 | 0.068 | 0.100 | 0.032 |
| P | 47 | 0.058 | 0.085 | 0.027 |
| T | 11 | 0.041 | 0.249 | 0.208 |

Gap survives in all three sections.

## Interpretation

The 5-type category taxonomy is independent of and complementary to C850's 5-type structural taxonomy (short, standard, long, only, metadata — based on size/RI features, not category). The two taxonomies classify paragraphs on orthogonal axes: C850 captures physical structure, C1335 captures operational content.

Each type has its dominant category at ~30% and draws secondary content from the same supporting pool (STAGING and TRANSITION are the most common secondary categories across all types). This suggests a modular architecture: each paragraph has a primary operational theme but draws from a shared set of supporting procedural and transitional vocabulary.

## Provenance

- a_paragraph_category_architecture.json: test A2
- Extends: C1263 (paragraph specialization d=12.5)
- Complements: C850 (structural taxonomy, 5 types, orthogonal)
- Relates to: C1266 (section differentiation), C1039 (cluster selectivity)

## Status

CONFIRMED — 5 category-based paragraph types with strong type distinctness surviving section stratification.
