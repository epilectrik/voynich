# C1419: ARTICULATOR e-HEAD Selectivity and k-HEAD Exclusion

**Tier:** 2
**Scope:** B, MIDDLE, ARTICULATOR, atom
**Phase:** 517 (ARTICULATOR_DEEP_DIVE)
**Date:** 2026-03-05

## Claim

Articulated tokens are 76-90% e-initial MIDDLE (vs 40% baseline = 1.9-2.3x enrichment). k-HEAD MIDDLEs categorically excluded from d,k,t articulators (4 forbidden pairs, all expected >= 4). PREFIX mediates 68.3% of this effect. Articulators mark stability/cooling operations, not heating.

## Evidence

- Script: `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` (T3, T9)
- Results: `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`

## Relationship to Existing Constraints

- Extends C1203 (ch/sh MIDDLE atom-level differentiation) -- sh-locked articulators inherit sh's e-MIDDLE bias
- Consistent with C1382 (k/a atom-initial suffix mode polarization) -- k-initial MIDDLEs have distinct suffix behavior, articulators avoid them
- Extends C908 (MIDDLE-kernel correlation) -- articulators select for stability-kernel MIDDLEs
- PREFIX mediation (68.3%) consistent with C1418 sh-locking: articulators -> sh PREFIX -> e-MIDDLEs
