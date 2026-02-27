# C1344: Position Within Line Modulates Suffix Choice

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_CONTEXT (470)

## Constraint

For flexible MIDDLEs, position within the line affects suffix category. MID-line tokens have the highest terminal fraction (40.6%) while EARLY tokens have the lowest (34.6%). Cramer's V=0.058 (p<0.001), continuous Spearman rho=0.095 (p<0.001). Conditional MI I(suffix_cat; position_zone | MIDDLE) = 0.024 bits. The effect is genuine but weaker than PREFIX (0.097) and neighborhood (0.057).

## Evidence

From suffix_mode_context.py test T3 (5,611 flexible MIDDLE tokens):

**Position zone suffix profiles:**

| Zone | n | terminal | bare |
|------|---|----------|------|
| EARLY (0.0-0.33) | 1,936 | 34.6% | 35.2% |
| MID (0.33-0.67) | 1,706 | 40.6% | 27.0% |
| LATE (0.67-1.0) | 1,969 | 35.7% | 30.8% |

**Statistics:**

| Metric | Value |
|--------|-------|
| Chi2 | 38.3 |
| Cramer's V | 0.058 |
| Chi2 p | <0.001 |
| Spearman rho (continuous) | 0.095 |
| Spearman p | <0.001 |
| Conditional MI | 0.024 bits |

**Per-MIDDLE position rho:** Mean |rho| = 0.179 across 28 MIDDLEs.

## Interpretation

The position effect shows a non-monotonic pattern: MID-line positions have the highest terminal fraction and lowest bare fraction. This is consistent with a "specification sandwich" — lines begin with relatively bare tokens (establishing context), peak in terminal specification at mid-line, and return toward bare at the end (continuation signal for the next line). The EARLY→MID increase in terminal fraction (+6pp) is larger than the MID→LATE decrease (-4.9pp), suggesting a net rightward shift toward suffixation.

This extends C1002 (suffix positional specialists: am/om are line-final) from locked MIDDLEs to flexible ones. The fact that per-MIDDLE |rho| averages 0.179 confirms this is not driven by a few positional specialists but is a distributed effect across the flexible MIDDLE population.

## Provenance

- suffix_mode_context.json: test T3
- Extends: C1002 (suffix positional grammar — now extends to flexible MIDDLEs)
- Extends: C1341 (mode emergent — position contributes 0.024 bits to the ~20% residual)
- Relates to: C1156 (transition dynamics by position — suffix modulation is the token-level manifestation)

## Status

CONFIRMED — MID-line position boosts terminal suffix for flexible MIDDLEs (V=0.058, conditional MI=0.024 bits).
