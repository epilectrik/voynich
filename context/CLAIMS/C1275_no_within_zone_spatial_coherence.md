# C1275: No Within-Zone Spatial Category Coherence

**Tier:** 2
**Scope:** AZC
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

AZC diagram spatial units (folio + line groups) do NOT show within-unit category coherence. Mean entropy 1.464 vs null 1.461, Cohen's d=-0.173, p=0.568. Across 264 groups with 2+ categorized PP MIDDLEs (2,626 tokens), category assignment is spatially random within zones. AZC's category structure operates at zone level (C1269), not at diagram-line level.

## Architecture

- **Zone-level yes, line-level no.** C1269 shows zones differ in category profile. C1275 shows that within any zone, adjacent tokens on the same line are not more category-similar than random. The organizational grain is coarser than A's record-level coherence (C1261, d=9.7).
- **Contrasts with A records.** A records show strong within-record category coherence (C1261, d=9.7). AZC diagram lines do not. This confirms AZC's positional classification operates differently from A's registry -- AZC classifies by zone, not by local group.
- **Consistent with static lookup table.** AZC is a static positional lookup table, not a sequential program. Line-level coherence would suggest sequential thematic ordering; its absence confirms the zone-level, non-sequential nature of AZC.

## Key Findings

| Metric | Value |
|--------|-------|
| Groups tested | 264 |
| Tokens | 2,626 |
| Observed entropy | 1.464 |
| Null entropy | 1.461 +/- 0.020 |
| Cohen's d | -0.173 |
| p-value | 0.568 |

## Provenance

- Contrasts C1261 (A record category coherence, d=9.7) -- A has it, AZC does not
- Complements C1269 (zone-level specialization) -- category structure is zone-grain only
- Consistent with AZC static lookup table characterization
