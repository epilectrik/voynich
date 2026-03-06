# C1513: Suffix atoms universally divergent from MIDDLE atoms (mean JSD=0.526)

**Tier:** 2
**Scope:** B, suffix, MIDDLE, atom, behavioral, divergence, category, cross-position, JSD
**Phase:** SUFFIX_ATOM_TAXONOMY (Phase 540)

## Claim

ALL 12 shared single-character atoms carry DIFFERENT category information in suffix vs MIDDLE position (12/12 divergent, mean JSD=0.526). The most stable atom is e (JSD=0.202, THERMAL-dominant in both positions). The most divergent is n (JSD=1.000, 100% TRANSITION in MIDDLE vs 100% FLOW in suffix -- complete categorical inversion). This extends C1409 with full category-level quantification and reveals that suffix position is not merely an attenuated version of MIDDLE behavior but a genuinely DIFFERENT semantic domain. The atom alphabet is shared but the category semantics are position-dependent.

## Evidence

Per-atom category JSD (MIDDLE position vs suffix position):
- e: 0.202 (THERMAL in both, but 35% MIDDLE vs 61% suffix)
- o: 0.223 (STAGING 32% MIDDLE vs THERMAL 35% suffix)
- a: 0.433 (FLOW 54% MIDDLE vs THERMAL 42% suffix)
- i: 0.402 (STAGING 71% MIDDLE vs TRANSITION 38% suffix)
- l: 0.408 (STAGING 76% MIDDLE vs TRANSITION 32% suffix)
- m: 0.510 (TRANSITION 99% MIDDLE vs MARKING 38% suffix)
- h: 0.517 (MONITORING 92% MIDDLE vs OPERATION 24% suffix)
- s: 0.599 (STAGING 88% MIDDLE vs THERMAL 43% suffix)
- d: 0.645 (CONTAINMENT 59% MIDDLE vs OPERATION 30% suffix)
- y: 0.671 (TRANSITION 88% MIDDLE vs THERMAL 36% suffix)
- r: 0.697 (FLOW 94% MIDDLE vs STAGING 43% suffix)
- n: 1.000 (TRANSITION 100% MIDDLE vs FLOW 100% suffix)

Mean JSD = 0.526
Most stable: e (0.202)
Most divergent: n (1.000)
0/12 atoms carry identical category profiles across positions

## Relationship to Prior Constraints

- **Extends C1409**: C1409 identified cross-position divergence (JSD 0.004-0.560 for 12 atoms). Phase 540 measures with category-level profiles: ALL atoms divergent (mean=0.526), confirming the earlier finding with deeper resolution
- **Extends C1191**: Position-dependent behavioral composition -- suffix imposes systematic shift on all atoms
- **Connects C1499**: Same alphabet shared across positions (manuscript-wide substrate), but semantics are position-specific
- **Connects C1508**: Same atom can carry intrinsically different category information depending on slot -- parallel to bridge atoms carrying different emphasis in A vs B

## Source

`phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` (T11)
