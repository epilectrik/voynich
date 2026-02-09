# C728: PP Co-occurrence Incompatibility Compliance

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

PP MIDDLE co-occurrence within Currier A lines is non-random but **fully explained by MIDDLE incompatibility** (C475). Lines are compatibility-valid subsets drawn from the folio pool, not actively specified selections.

> **Aggregation Note (2026-01-30):** This constraint analyzes within-line MIDDLE co-occurrence.
> Line-level patterns describe A-internal structure. For A-B vocabulary correspondence, the
> operational unit is the A FOLIO (114 units, 81% coverage per C885).

| Metric | Value |
|--------|-------|
| Lines with 2+ PP tokens | 1,506 (96.4% of 1,562 lines) |
| Total within-line pair occurrences | 19,576 |
| Observed unique co-occurring pairs | 5,460 |
| Null (shuffled) unique pairs | 5,669 +/- 43 |
| p (fewer unique than null) | < 0.001 |
| Observed pair count variance | 80.93 |
| Null pair count variance | 84.27 +/- 2.16 |
| p (variance excess) | 0.934 |

The observed data has **fewer** unique co-occurring pairs than random shuffling produces, because the shuffle places incompatible MIDDLEs on the same line (inflating unique pair count). Among compatible pairs, variance is at or below null — no enrichment, no attraction, no clustering.

## Implication

Within-line PP MIDDLE selection is governed by a single mechanism: MIDDLE incompatibility (C475). After filtering for compatibility, the draw from the folio pool is effectively random. This confirms Scenario B from the phase design: C475 is the sole driver, and no structure beyond incompatibility exists at the MIDDLE co-occurrence level.

The top co-occurring pairs are high-frequency MIDDLEs (ol+or: 169, o+ol: 156, ol+y: 132) — frequency-driven, not structurally enriched.

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_cooccurrence_tests.py` (T1+T2)
- Extends: C703 (folio-level PP homogeneity), C475 (MIDDLE incompatibility)
- Consistent with: C233 (line independence), C234 (position-free within line)
