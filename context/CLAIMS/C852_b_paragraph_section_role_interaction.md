# C852: B Paragraph Section-Role Interaction

**Tier:** 2
**Scope:** Currier-B
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

B paragraph role composition varies significantly by section. RECIPE_B dominates EN (44.5%), PHARMA dominates FQ (43.2%), and HERBAL_B shows highest HT delta (0.209). Section effects are highly significant.

## Evidence

| Section | n | HT Delta | EN Rate | FL Rate | FQ Rate |
|---------|---|----------|---------|---------|---------|
| BIO | 149 | 0.093 | 30.6% | 2.9% | 16.7% |
| HERBAL_B | 54 | **0.209** | 33.8% | 9.5% | 20.9% |
| PHARMA | 42 | 0.046 | 18.4% | 2.9% | **43.2%** |
| RECIPE_B | 289 | 0.144 | **44.5%** | 6.8% | 19.1% |

Kruskal-Wallis tests:
- HT delta by section: H=30.13, p<0.0001
- EN rate by section: H=57.33, p<0.0001

## Interpretation

Section specialization at paragraph level:
- **RECIPE_B**: EN-dominated (thermal/energy operations)
- **PHARMA**: FQ-dominated (frequency/repetition operations)
- **HERBAL_B**: Highest header effect (strongest identification marking)
- **BIO**: Balanced profile

Note: Some patterns differ from folio-level C552 expectations, suggesting section effects operate at different granularities.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C552 | PARTIAL - Section-role patterns at paragraph level differ from folio level |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/09_b_section_effects.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/b_section_effects.json`

## Status

CONFIRMED
