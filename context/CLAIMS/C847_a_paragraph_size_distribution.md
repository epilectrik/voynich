# C847: A Paragraph Size Distribution

**Tier:** 2
**Scope:** Currier-A
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

A paragraphs average 4.8 lines with significant variation by folio position. "Only" paragraphs (single-paragraph folios) are much larger at 11.79 lines. Size differences between A and B are not statistically significant.

## Evidence

| Position | n | Mean Lines | Mean Tokens |
|----------|---|------------|-------------|
| first | 86 | 5.35 | 39.0 |
| middle | 142 | 2.75 | 18.7 |
| last | 86 | 5.36 | 36.2 |
| only | 28 | **11.79** | 73.4 |

Cross-system comparison (A vs B):
- A: mean 4.8 lines, B: mean 4.37 lines
- Cohen's d = 0.110 (negligible effect)
- Mann-Whitney p = 0.067 (not significant)

## Interpretation

Paragraph size is primarily determined by folio position:
- "Only" paragraphs serve as complete programs in single-paragraph folios
- "Middle" paragraphs are compact (2.75 lines) - possibly metadata records
- First/last paragraphs are symmetric in size

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C827 | CONFIRMS - Paragraphs as operational aggregation units |
| C840 | PARALLEL - B paragraph mean 4.37 lines |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/01_a_size_density_profile.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/a_size_density.json`

## Status

CONFIRMED
