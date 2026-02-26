# C1315: REGIME B Token Profile Discrimination

**Tier:** 2
**Scope:** B
**Phase:** DISTILLATION_TERMINOLOGY_MAPPING (461)
**Date:** 2026-02-25

## Finding

The 4 REGIMEs produce statistically distinct B token profiles across 6 of 7 tested metrics:

| Metric | Kruskal-Wallis H | p-value | Significant |
|--------|-----------------|---------|-------------|
| k-fraction | significant | <0.01 | YES |
| e-fraction | significant | <0.01 | YES |
| h-fraction | significant | <0.01 | YES |
| THERMAL rate | significant | <0.01 | YES |
| MONITORING rate | significant | <0.01 | YES |
| CONTAINMENT rate | significant | <0.01 | YES |
| Mean line length | — | NS | NO |

6/7 metrics discriminate REGIMEs at p < 0.01.

## Negative Control: Currier A

The same 7 metrics applied to Currier A tokens grouped by the same REGIME assignments show 0/7 significant discriminations. REGIME discrimination is B-specific, not an artifact of folio grouping.

## Interpretation (Tier 2 only)

REGIME assignments (derived from F-B-003 folio classification) correspond to real B-internal token composition differences. The discrimination is not driven by line length (the only NS metric) but by the specific atom and category profiles of B tokens.

## Extends

- F-B-003 (REGIME folio classification) — REGIMEs capture real B-internal variation
- C494 (REGIME precision axis) — token profiles provide a second independent axis of REGIME differentiation

## Falsifiability

Would be falsified if A tokens show equal or greater REGIME discrimination (same metrics, same folio groupings), or if fewer than 4/7 metrics reach significance after Bonferroni correction.

## Evidence Files

- `phases/DISTILLATION_TERMINOLOGY_MAPPING/results/distillation_terminology_mapping.json` (T4)
