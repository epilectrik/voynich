# C671: MIDDLE Novelty Shape

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

MIDDLE vocabulary is **front-loaded** within Currier B folios. 87.3% of folios (69/79) concentrate >60% of unique MIDDLEs in the first half of lines. Zero folios are back-loaded (<40% in first half). Grand mean first-half fraction = 0.685, vs permuted baseline = 0.653.

## Method

For each folio: track cumulative unique MIDDLEs across lines in order. Compute first-half fraction = unique MIDDLEs by midpoint / total unique MIDDLEs. Classify: FRONT_LOADED (>0.6), BACK_LOADED (<0.4), UNIFORM. Permutation baseline: 1000 shuffles of line order within folio.

## Key Numbers

| Metric | Value |
|--------|-------|
| Grand first-half fraction | 0.685 |
| Grand permuted first-half | 0.653 |
| FRONT_LOADED | 69/79 (87.3%) |
| BACK_LOADED | 0/79 (0.0%) |
| UNIFORM | 10/79 (12.7%) |

## Regime Stratification

| Regime | Mean FH | FL | BL | UN |
|--------|---------|----|----|-----|
| REGIME_1 | 0.719 | 20 | 0 | 3 |
| REGIME_2 | 0.673 | 18 | 0 | 4 |
| REGIME_3 | 0.669 | 7 | 0 | 1 |
| REGIME_4 | 0.670 | 24 | 0 | 2 |

## Interpretation

Programs introduce their vocabulary repertoire early and reuse established MIDDLEs in later lines. This is not a recipe advancing through phases — it is consistent with a system that establishes its operational vocabulary in initial assessment lines and then re-applies those operators. The front-loading is mild over permuted baseline (+0.032), suggesting structural ordering rather than strict sequencing.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_sequential_coupling.py` (Test 2)
- Extends: C670 (no adjacent vocabulary coupling, but ordered vocabulary introduction)
