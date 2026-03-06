# C1467: Paragraph Zone x Hazard Interaction (Non-Fractal)

**Tier:** 2
**Scope:** B, paragraph, zone, hazard, frame, routing, C1398, C1425, C1448, C1463
**Phase:** 529 (PARAGRAPH_HAZARD_GRADIENT)
**Date:** 2026-03-05

## Claim

The three-zone paragraph model (HEADER/BODY/TAIL) and frame hazard classification interact with a statistically overwhelming but topologically DIFFERENT pattern from the line-level gradient (C1463). Chi-squared=233.9, dof=6, p=1.15e-47, Cramer's V=0.071 (comparable to line-level V=0.085, ratio=0.84). However, the topology is INVERTED relative to the line-level pattern: HEADER concentrates LOW-hazard (1.130x) and depletes ZERO/IMMUNE, BODY concentrates safe vocabulary (ZERO 1.077x, IMMUNE 1.121x), and TAIL concentrates HIGH hazard (1.134x). The line-level "safe-first" design (ZERO at SPECIFICATION) is ABSENT at paragraph level -- replaced by "infrastructure-first" (LOW at HEADER). The paragraph hazard architecture is NOT a fractal repetition of the line architecture.

## Evidence

### Zone x Hazard Class Enrichment Table

| Zone | N | HIGH | LOW | ZERO | IMMUNE |
|------|---|------|-----|------|--------|
| HEADER | 5,982 | 1.057x | **1.130x** | 0.784x | 0.793x |
| BODY | 13,317 | 0.936x | 0.959x | **1.077x** | **1.121x** |
| TAIL | 3,791 | **1.134x** | 0.939x | 1.069x | 0.900x |

### Pairwise Zone Comparisons

| Comparison | chi2 | p | V |
|-----------|------|---|---|
| HEADER vs BODY | 198.3 | 9.62e-43 | 0.101 |
| HEADER vs TAIL | 86.0 | 1.62e-18 | 0.094 |
| BODY vs TAIL | 43.1 | 2.37e-09 | 0.050 |

### Hazard Rate by Zone (Absolute)

| Zone | HIGH% | LOW% | ZERO% | IMMUNE% |
|------|-------|------|-------|---------|
| HEADER | 21.9% | 51.6% | 15.8% | 10.6% |
| BODY | 19.4% | 43.8% | 21.7% | 15.1% |
| TAIL | 23.5% | 42.9% | 21.6% | 12.1% |

### Fractal Comparison with Line Level (C1463)

| Scale | V | chi2 | p | Pattern |
|-------|---|------|---|---------|
| Line (C1463) | 0.085 | 336.3 | 1.38e-69 | ZERO first, HIGH last |
| Paragraph | 0.071 | 233.9 | 1.15e-47 | LOW first, HIGH last |

Ratio (paragraph/line): 0.84 -- comparable magnitude, different topology.

### Paragraph Length Interaction

| Length | N | V | TAIL HIGH enrichment |
|--------|---|---|---------------------|
| Short (2-3 lines) | 5,895 | 0.057 | 1.014x |
| Medium (4-5 lines) | 5,917 | 0.061 | 1.019x |
| Long (6+ lines) | 10,504 | 0.060 | 1.274x |

LONG paragraphs show the strongest TAIL hazard concentration. The pattern strengthens with paragraph length.

## Interpretation

The paragraph and line levels each have their own hazard routing architecture, but they follow DIFFERENT organizing principles:

- **Line level (C1463):** Safe operations FIRST (e->y at SPECIFICATION), energy operations in WORK (k-HEAD), hazardous operations LAST (a/d-HEAD at CLOSURE). The line is a SAFETY ARCHITECTURE -- it opens safe.

- **Paragraph level:** Infrastructure operations FIRST (LOW at HEADER -- these are MARKING/STAGING specification tokens per C1287, C1426), functional operations in BODY (ZERO+IMMUNE -- the actual thermal work), hazardous operations LAST (HIGH at TAIL). The paragraph is a SPECIFICATION ARCHITECTURE -- it specifies first, works second, hazards accumulate at close.

The key difference: line-level SPECIFICATION uses categorically SAFE (e->y) vocabulary. Paragraph-level HEADER uses INFRASTRUCTURE (LOW/default) vocabulary. Safe vocabulary (ZERO) concentrates in the paragraph BODY where thermal work happens, not at the specification boundary. Headers don't need to be safe because they specify what to do; body lines are where actual hazardous operations could occur, but the safe vocabulary concentrates there to provide the stability anchor (C1457-C1462). Tail lines accumulate hazard because they close operations.

## Falsification Criteria

1. If overall chi-squared p rises above 0.01
2. If HEADER LOW enrichment drops below 1.05x
3. If TAIL HIGH enrichment drops below 1.05x
4. If BODY ZERO+IMMUNE enrichment both drop below 1.02x
5. If paragraph V exceeds 2x line V (would suggest different mechanism)

## Method

- 23,090 Currier B tokens (H-track, labels/uncertain excluded)
- Paragraph boundaries detected via gallows-initial lines (C864)
- Paragraph zones: HEADER (first line), BODY (middle lines), TAIL (last line)
- Frame hazard class from decoder_maps.json
- Chi-squared contingency tests with Cramer's V

**Script:** `phases/PARAGRAPH_HAZARD_GRADIENT/scripts/paragraph_hazard_gradient.py`
**Results:** `phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json`

## Dependencies

- C1463 (line-level zone-hazard routing -- comparable magnitude, different topology)
- C1448 (HEAD x TERM frame hazard map)
- C1425-C1430 (three-zone line model)
- C1287 (paragraph headers MARKING-enriched)
- C1398 (paragraph operational gradient -- continuous, not discrete)
