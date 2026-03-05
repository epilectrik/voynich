# C1418: ARTICULATOR PREFIX-Locked with BARE/qo Exclusion

**Tier:** 2
**Scope:** B, PREFIX, ARTICULATOR
**Phase:** 517 (ARTICULATOR_DEEP_DIVE)
**Date:** 2026-03-05

## Claim

29 forbidden ARTICULATOR x PREFIX pairs. Articulators categorically exclude BARE tokens (0/3,864) and qo-PREFIX (3/4,069 = 0.07%). Most articulators lock to sh-PREFIX family (t: 94%, k: 94%, d: 72%). y distributes across ch/te/ta/sh. V(ART,PREFIX) = 0.196, p < 1e-300, N = 23,096.

## Evidence

- Script: `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` (T2, T9)
- Results: `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`

## Relationship to Existing Constraints

- Extends C911 (PREFIX-MIDDLE compatibility constraints) to ARTICULATOR x PREFIX dimension
- Consistent with C1300 (qo near-pure THERMAL channel) -- qo's purity excludes articulators
- Extends C1063 (PREFIX-SUFFIX compatibility) -- articulators add a third forbidden-pair dimension
- y-articulator's te/ta/pch affinity links to C933 (prep verb early concentration)
