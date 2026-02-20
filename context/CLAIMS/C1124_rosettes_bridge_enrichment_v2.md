# C1124: Rosettes Bridge Enrichment (Revalidated)

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout
**Phase:** 402 (ROSETTES_SYSTEM_REVALIDATION)
**Supersedes:** C1096 (deleted — built on incomplete data)

## Finding

The Rosettes foldout vocabulary is enriched in bridge MIDDLEs at **3.05x** the B corpus baseline: 21.5% of Rosettes unique MIDDLEs (38/177) are bridge MIDDLEs, vs 7.0% (85/1208) in the B corpus.

Bridge enrichment is universal across all entity sub-region types:
- Ring text: 32.1% (4.56x)
- Inner labels: 33.3% (4.74x)
- Outer labels: 36.4% (5.17x)
- Spiral: 25.0% (3.55x)
- Clock text: 50.0% (7.11x)

No entity type has a bridge fraction below 25%.

## Evidence

- Data source: `data/rosettes_annotated.json` (ZL transcription + manual spatial annotation)
- 177 unique MIDDLEs across 19 entities, 38 are bridge MIDDLEs
- Bridge set: 85 MIDDLEs from `phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json`
- Test X1 in Phase 402 battery

## Implication

The Rosettes foldout preferentially samples the vocabulary that mediates cross-system connections. This is consistent with an indexing/metalayer function rather than standalone B execution or AZC positional encoding.

## Provenance

- Source: Phase 402, Test X1
- Related: C1013 (bridge topological generality), C1014 (viability via bridge backbone)
