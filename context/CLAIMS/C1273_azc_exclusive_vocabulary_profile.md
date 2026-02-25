# C1273: AZC-Exclusive Vocabulary is MARKING/THERMAL Enriched

**Tier:** 2
**Scope:** AZC
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

AZC's 356 UNK MIDDLEs (absent from the A/B MIDDLE dictionary) have a distinctive category profile when assigned by atom plurality vote: MARKING 27.2%, THERMAL 27.0%, OPERATION 12.6%, STAGING 12.6%, FLOW 11.2%, TRANSITION 6.5%, MONITORING 2.8%, CONTAINMENT 0%. This profile diverges strongly from bridge MIDDLEs (V=0.382, p<0.001), dark pipeline MIDDLEs (V=0.210, p<0.001), and overall PP (V=0.192, p<0.001).

## Architecture

- **AZC has a private vocabulary layer.** 356 MIDDLEs appear only in AZC, accounting for 57.7% of unique AZC MIDDLEs. These are not random noise -- they form a coherent population enriched in MARKING and THERMAL categories.
- **TRANSITION-depleted.** TRANSITION is the dominant category across AZC (C1269, C1270), but AZC-exclusive vocabulary is sharply depleted in it (6.5% vs ~25% corpus-wide). The exclusive vocabulary serves different operational roles than the shared vocabulary.
- **MARKING enrichment.** 27.2% MARKING is much higher than bridge (11%) or dark (36%) baselines. Combined with THERMAL enrichment, these MIDDLEs may serve position-specific annotation functions.
- **Extends C472.** C472 established MIDDLE as the primary carrier of AZC folio specificity (77% exclusive). C1273 shows this exclusive vocabulary is categorically specialized, not arbitrary.

## Key Findings

| Metric | Value |
|--------|-------|
| UNK MIDDLEs | 356 |
| Top categories | MARKING 27.2%, THERMAL 27.0% |
| Depleted | TRANSITION 6.5%, CONTAINMENT 0% |
| vs bridge (V) | 0.382 |
| vs dark (V) | 0.210 |
| vs PP-all (V) | 0.192 |

## Provenance

- Extends C472 (MIDDLE folio specificity) with category characterization
- Extends C469 (categorical resolution) -- exclusive MIDDLEs encode position-specific categories
- Diverges from C1264 (bridge/dark profiles) -- third distinct population
