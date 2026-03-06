# C1469: Line-Level Hazard Gradient Persists Independently Within All Paragraph Zones

**Tier:** 2
**Scope:** B, line, paragraph, zone, hazard, independence, nested, C1463, C1467
**Phase:** 529 (PARAGRAPH_HAZARD_GRADIENT)
**Date:** 2026-03-05

## Claim

The line-level hazard gradient (C1463: ZERO at SPECIFICATION, IMMUNE at THERMAL_WORK, HIGH at CLOSURE) operates independently within ALL three paragraph zones (HEADER, BODY, TAIL). Within-zone line-level V ranges from 0.079 to 0.094, comparable to the corpus-wide line V of 0.085. The line-level gradient within BODY (V=0.094) is actually STRONGER than corpus-wide. The two architectural levels (line position and paragraph zone) function as independent, layered safety mechanisms.

## Evidence

### Within-Zone Line-Level Gradients

| Paragraph Zone | N | Line-level chi2 | p | V |
|---------------|---|-----------------|---|---|
| HEADER | 5,982 | 74.7 | 4.47e-14 | 0.079 |
| BODY | 13,317 | 237.0 | 2.42e-48 | **0.094** |
| TAIL | 3,791 | 63.4 | 9.15e-12 | 0.091 |

Corpus-wide line-level V (C1463): 0.085.

### Within-Zone HIGH Hazard Rate by Line Position

| Paragraph Zone | Line-Q0 HIGH% | Line-Q4 HIGH% | Q4/Q0 Ratio |
|---------------|---------------|---------------|-------------|
| HEADER | 20.6% | 23.9% | 1.16 |
| BODY | 15.5% | 22.0% | 1.42 |
| TAIL | 18.4% | 27.8% | 1.51 |

In every paragraph zone, hazardous operations concentrate at line-final position. The BODY and TAIL zones show steeper gradients (1.42x, 1.51x) than HEADER (1.16x), indicating that the line safety architecture is especially active where thermal work and closure operations occur.

### Independence Evidence

The paragraph zone effect (V=0.071, C1467) and the line zone effect (V=0.085, C1463) operate simultaneously. Their combined effect is NOT simply additive:
- BODY lines have the safest paragraph-zone profile (ZERO+IMMUNE enriched)
- Within BODY, the line gradient is STRONGEST (V=0.094)
- This means the most thermally active paragraph zone has the strongest line-level safety architecture

### Section Universality

The TAIL line-Q4 HIGH concentration pattern (ratio > 1.0) is present in ALL five sections where tested (B, C, H, S, T). In 4/5 sections, TAIL HIGH rate exceeds HEADER HIGH rate.

## Interpretation

The manuscript implements a TWO-LEVEL safety architecture:

1. **Paragraph level (C1467):** Specification-first, hazard-last. Headers specify operations with infrastructure vocabulary. Tails accumulate hazardous closures.

2. **Line level (C1463):** Safe-first, hazard-last. Lines open with categorically safe (e->y) vocabulary and close with hazardous (a/d-HEAD) operations.

These two levels are INDEPENDENT -- the line gradient persists unchanged regardless of paragraph zone. This is NOT a fractal repetition (the topologies differ) but a LAYERED architecture: each line within each paragraph zone independently applies the safe-first/hazard-last principle at its own scale. The operator encounters safety at every line entry, even within the hazardous tail zone of a paragraph.

This connects to C1399 (paragraph ordering null) and C1400 (paragraph state-independent ordering): paragraphs are independently composed within folio envelopes, and WITHIN each paragraph, lines independently apply the same safety grammar. Safety is enforced at line level, not paragraph level.

## Falsification Criteria

1. If any paragraph zone's within-zone line V drops below 0.04
2. If BODY within-zone V drops below HEADER within-zone V (would suggest zone-dependent modulation)
3. If any zone's line-Q4/Q0 HIGH ratio drops below 1.0

## Method

- 23,090 Currier B tokens
- Each token has both line position (quintile/zone per C1463) and paragraph zone (HEADER/BODY/TAIL)
- Chi-squared contingency tests applied separately within each paragraph zone
- Cramer's V for effect size comparison

**Script:** `phases/PARAGRAPH_HAZARD_GRADIENT/scripts/paragraph_hazard_gradient.py`
**Results:** `phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json`

## Dependencies

- C1463 (line-level zone-hazard routing -- base pattern being tested within zones)
- C1467 (paragraph-level zone-hazard interaction -- parallel finding at paragraph scale)
- C1399 (paragraph ordering null -- paragraphs independently composed)
- C1400 (paragraph state-independent ordering -- no state dependence)
