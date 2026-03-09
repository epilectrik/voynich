# C1586: N3 line-shuffle null is non-destructive to coupled plant behavior

**Tier:** 2
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, null, line-shuffle, ordering, C1399, C1400, C1470, C1577

## Claim

N3 line-shuffle null is non-destructive: line ordering within folios carries less coupled-plant information than token composition. Only 3/7 folios pass N3 destruction test vs 5-6/7 for N1/N2/N4 null types. Consistent with C1399 (paragraph ordering null), C1400 (state-independent ordering), and C1470 (cross-line hazard folio-mediated). Validates the folio-as-program paradigm where line composition, not line order, is the critical coupling axis.

## Evidence

- P7 null destruction detail: N3 3/7 folios pass vs N1 6/7, N2 6/7, N4 5/7
- N1 (token-shuffle): destroys coupled behavior (6/7 pass destruction test)
- N2 (domain-preserving shuffle): destroys coupled behavior (6/7 pass)
- N3 (line-shuffle): resistant -- does NOT destroy coupled behavior (only 3/7 pass)
- N4 (terminal-shuffle): destroys coupled behavior (5/7 pass)
- Line ordering information < token composition information for plant coupling

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- Builds on: C1399 (paragraph ordering null), C1400 (paragraph state-independent ordering), C1470 (cross-line hazard folio-mediated), C1577 (4 null models confirm hierarchy)
