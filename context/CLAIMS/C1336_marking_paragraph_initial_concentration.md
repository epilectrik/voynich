# C1336: MARKING Paragraph-Initial Concentration in A

**Tier:** 2
**Scope:** A (all sections)
**Phase:** A_PARAGRAPH_CATEGORY_ARCHITECTURE (468)

## Constraint

MARKING tokens concentrate toward the beginning of A paragraphs. Mean normalized position is 0.429 (vs 0.5 expected for uniform), deviation 0.071, permutation p<0.001. MARKING is the only category with both statistically significant positional bias (p<0.01) and meaningful effect size (deviation > 0.03). First-token MARKING rate is 15.5% vs base rate 7.5% (2.07x enrichment).

## Evidence

From a_paragraph_category_architecture.py test A3 (238 paragraphs with 5+ categorized PP MIDDLEs):

**Category mean normalized positions (0=start, 1=end):**

| Category | Mean position | Deviation | Perm p | n tokens |
|----------|--------------|-----------|--------|----------|
| MARKING | **0.429** | **0.071** | **<0.001** | 747 |
| CONTAINMENT | 0.531 | 0.031 | 0.018 | 481 |
| STAGING | 0.515 | 0.015 | 0.004 | 2,308 |
| MONITORING | 0.517 | 0.017 | 0.192 | 505 |
| THERMAL | 0.510 | 0.010 | 0.152 | 1,438 |
| OPERATION | 0.504 | 0.004 | 0.666 | 988 |
| FLOW | 0.494 | 0.006 | 0.312 | 1,732 |
| TRANSITION | 0.493 | 0.007 | 0.260 | 1,780 |

**Boundary distributions (first/last token):**

| Category | First-token rate | Last-token rate | Base rate |
|----------|-----------------|-----------------|-----------|
| MARKING | **15.5%** | 9.2% | 7.5% |
| FLOW | **25.2%** | 14.3% | 17.3% |
| CONTAINMENT | 1.3% | **6.3%** | 4.8% |
| TRANSITION | 14.3% | **19.7%** | 17.9% |

## Interpretation

MARKING (mark, flag, note, pause, diagram, hazard, danger, link, adjust) concentrates at the front of A paragraphs. This is a cross-system pattern:

- **A paragraphs (C1336):** MARKING front-loaded at position 0.429
- **B paragraph headers (C1287):** MARKING enriched in paragraph headers
- **B block 0 (C1332):** Block-0-unique vocabulary is MARKING 2.48x enriched

Across both systems, MARKING vocabulary appears first — annotations and flags come before operational content. This is consistent with a documentation practice where what-to-watch-for precedes what-to-do.

All other categories show deviations < 0.03, confirming that C234 (POSITION_FREE) and C240 (NON_SEQUENTIAL) extend to the category level for 7 of 8 categories. MARKING is the sole systematic exception.

## Provenance

- a_paragraph_category_architecture.json: test A3
- Relates to: C1287 (B paragraph header MARKING enrichment), C1332 (B block-0 MARKING enrichment)
- Extends: C234 (POSITION_FREE — confirmed for 7/8 categories), C240 (NON_SEQUENTIAL — one exception)

## Status

CONFIRMED — MARKING is front-loaded in A paragraphs (p<0.001), the sole exception to paragraph-level position-free behavior.
