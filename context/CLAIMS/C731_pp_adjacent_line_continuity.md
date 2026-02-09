# C731: PP Adjacent Line Continuity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

Adjacent lines within Currier A folios share more PP MIDDLE vocabulary than non-adjacent lines. The effect is small but significant.

> **Aggregation Note (2026-01-30):** This constraint analyzes at line level and shows
> local sequential continuity. For A-B vocabulary correspondence, the operational unit
> is the A FOLIO (114 units, 81% coverage per C885). Line-level continuity contributes
> to folio-level coherence.

| Metric | Value |
|--------|-------|
| Adjacent line pairs | 1,422 |
| Non-adjacent line pairs | 10,223 |
| Adjacent mean Jaccard | 0.1016 |
| Non-adjacent mean Jaccard | 0.0921 |
| Adjacent/non-adjacent ratio | 1.104x |
| Null ratio (shuffled line order) | 1.020 +/- 0.027 |
| p (observed > null) | 0.001 |

When line order within a folio is shuffled, the adjacent/non-adjacent ratio drops to ~1.02 (near unity). The observed 1.10 ratio exceeds 999 out of 1,000 shuffled values.

## Implication

There is local sequential continuity in PP content — neighboring lines draw from overlapping portions of the folio PP pool more than distant lines do. This is consistent with records being organized into local clusters or "paragraphs" that share operational vocabulary.

This does NOT violate C233 (line independence in inter-line prediction) because C233 concerns predictability of line content from adjacent lines, not vocabulary overlap. Shared vocabulary is a population-level property, not a deterministic sequencing rule.

The effect size is modest (10% Jaccard increase, ~3 standard deviations above null), suggesting soft continuity rather than strict sequential dependencies.

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_dimension_tests.py` (T7)
- Consistent with: C233 (line independence — not violated), C703 (folio-level PP pool)
- Related to: C498-CHAR-A-SEGMENT (RI segments show position effects)
