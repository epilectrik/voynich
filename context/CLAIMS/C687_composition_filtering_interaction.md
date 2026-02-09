# C687: Composition-Filtering Interaction

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

A record composition (PURE_RI, PURE_PP, MIXED) is the **primary determinant** of filtering severity.

> **Aggregation Note (2026-01-30):** This constraint analyzes at line level (1,562 units).
> Per C881, A records are paragraphs (342 units). Per C885, the operational unit for
> A-B vocabulary correspondence is the A FOLIO (114 units, 81% coverage).

PURE_RI records admit near-zero B classes (mean 0.44), confirming that Registry-Internal tokens provide no B vocabulary access. MIXED and PURE_PP records are statistically indistinguishable (Mann-Whitney p=0.997, mean 11.26 vs 11.13 classes).

## Key Numbers

| Composition | N | Mean Classes | Median | Min | Max |
|-------------|---|-------------|--------|-----|-----|
| PURE_PP | 982 | 11.13 | 11.0 | 0 | 38 |
| MIXED | 565 | 11.26 | 10.0 | 0 | 37 |
| PURE_RI | 9 | 0.44 | 0.0 | 0 | 2 |
| UNKNOWN | 6 | 1.00 | 0.0 | 0 | 3 |

## Statistical Tests

| Comparison | Mann-Whitney U | p |
|------------|---------------|---|
| MIXED vs PURE_PP | 277,451 | 0.997 (ns) |
| MIXED vs PURE_RI | 5,052 | 3.6e-7 *** |
| PURE_PP vs PURE_RI | 8,777 | 3.3e-7 *** |
| PURE_RI vs UNKNOWN | 24 | 0.725 (ns) |

## Interpretation

The binary distinction between PP-containing and RI-only records is the fundamental divide. Once a record has ANY PP content, the specific proportion of PP vs RI tokens does not significantly affect filtering outcome. PURE_RI records (only 9 exist, 0.6% of all records) represent a structural edge case with near-total B incompatibility.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/structural_reshape_analysis.py` (Test 6)
- Extends: C498 (RI/PP bifurcation), C682 (distribution)
