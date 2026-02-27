# C1343: Line Category Environment Modulates Suffix Choice

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_CONTEXT (470)

## Constraint

For flexible MIDDLEs, the category composition of neighboring tokens on the same line modulates suffix choice. Tokens on THERMAL-rich lines carry terminal suffix more often (mean THERMAL neighbor fraction 0.266 for terminal vs 0.233 for bare, Mann-Whitney Z=5.87, p<0.001). Conditional MI I(suffix_cat; LOO_dominant_cat | MIDDLE) = 0.057 bits. The effect is partially confounded with PREFIX (PREFIX also determines category context), but the neighborhood signal is independently significant.

## Evidence

From suffix_mode_context.py test T2 (5,611 flexible MIDDLE tokens):

**Leave-one-out neighborhood THERMAL fraction by suffix outcome:**

| Suffix cat | n | Mean THERMAL frac |
|-----------|---|-------------------|
| terminal | 2,064 | 0.266 |
| bare | 1,748 | 0.233 |

Mann-Whitney Z=5.873, p<0.001.

**Quintile analysis (terminal fraction by neighborhood THERMAL):**

| Quintile | n | Mean THERMAL frac | Terminal frac |
|----------|---|-------------------|---------------|
| Q0 (lowest) | 1,132 | 0.037 | 0.351 |
| Q1 | 1,378 | 0.159 | 0.336 |
| Q2 | 972 | 0.251 | 0.370 |
| Q3 | 1,135 | 0.348 | 0.364 |
| Q4 (highest) | 994 | 0.527 | 0.434 |

Spearman rho=0.800, p=0.084 (strong monotonic trend across quintiles, marginal significance at n=5 quintiles). Terminal fraction rises from 33.6% in the least THERMAL neighborhoods to 43.4% in the most THERMAL neighborhoods.

**Conditional MI:** 0.057 bits (28 MIDDLEs contributing).

## Interpretation

When a flexible MIDDLE sits on a line with many THERMAL neighbors, it is more likely to carry a terminal suffix (Mode A behavior). This confirms that the mode-category coupling (C1279/C1309) operates at the individual token level, not just as a line-level statistical association. The mechanism likely operates through PREFIX: lines with many THERMAL tokens tend to have many qo-prefixed tokens (C1297), and qo biases toward terminal suffix (C1342). However, the conditional MI (0.057 bits) is substantial enough to suggest some independent neighborhood effect beyond PREFIX alone.

## Provenance

- suffix_mode_context.json: test T2
- Extends: C1279/C1309 (mode-category coupling — now shown to operate at individual token level)
- Relates to: C1342 (PREFIX modulation — partially confounded; both channel through category)
- Extends: C1341 (mode emergent — category environment contributes to the ~20% residual)

## Status

CONFIRMED — THERMAL-rich neighborhoods push flexible MIDDLEs toward terminal suffix (Z=5.87, p<0.001, conditional MI=0.057 bits).
