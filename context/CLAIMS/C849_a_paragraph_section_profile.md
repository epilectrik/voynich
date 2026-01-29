# C849: A Paragraph Section Profile

**Tier:** 2
**Scope:** Currier-A
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

Section P (pharmaceutical) paragraphs have significantly higher RI rate (17.2%) and PP rate (67.5%) than section H (herbal). Section differences are highly significant.

## Evidence

| Section | n | RI Rate | PP Rate | Compound Rate |
|---------|---|---------|---------|---------------|
| H | 197 | 8.4% | 42.0% | 27.7% |
| P | 130 | **17.2%** | **67.5%** | 32.0% |
| T | 15 | 9.8% | 53.3% | 29.9% |

Kruskal-Wallis (RI by section): H = 14.71, p = 0.0006

## Interpretation

Section P paragraphs are more RI-dense and PP-dense than H paragraphs. This suggests:
- P paragraphs carry more structured information (higher RI)
- P paragraphs contain more operational vocabulary (higher PP)
- H paragraphs may be more narrative or less formulaic

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C552 | EXTENDS - Section effects at paragraph level |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/04_a_position_section_effects.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/a_position_section_effects.json`

## Status

CONFIRMED
