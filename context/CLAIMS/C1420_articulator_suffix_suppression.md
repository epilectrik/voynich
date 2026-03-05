# C1420: ARTICULATOR Suffix Suppression

**Tier:** 2
**Scope:** B, SUFFIX, ARTICULATOR
**Phase:** 517 (ARTICULATOR_DEEP_DIVE)
**Date:** 2026-03-05

## Claim

Articulated tokens have 16.7-27.2% suffix rate vs 49.3% baseline (0.34-0.55x). Only p-articulator matches baseline (58.2%). Suffix suppression is consistent with specification context (no execution-mode marking needed at line-opening positions).

## Evidence

- Script: `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` (T4)
- Results: `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`

## Relationship to Existing Constraints

- Extends C588 (suffix role selectivity) -- articulators create a new suffix-depleted stratum
- Consistent with C1236 (suffix scope markers) -- suffix marks execution mode; specification tokens don't need it
- Consistent with C1338 (MIDDLE suffix selectivity) -- suffix is MIDDLE-determined; articulators select for suffix-depleted MIDDLEs
- p-articulator exception (58.2%) may reflect p's MARKING/pause function (C1390)
