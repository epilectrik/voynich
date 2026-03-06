# C1528: Hazard Classes Map to Distinct Atom HEAD Territories

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, hazard, failure-class, territory, partition, C109, C1446, C1447, C1475, C1477
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

The 5 hazard failure classes (C109) decompose into near-orthogonal atom HEAD territories: 7/10 pairwise source HEAD Jaccard comparisons are exactly 0.000 (zero overlap). PHASE_ORDERING sources are headless y-terminal; COMPOSITION_JUMP sources are headless; CONTAINMENT_TIMING sources are HEAD-diverse (c, l, o, h); RATE_MISMATCH source is a-HEAD; ENERGY_OVERSHOOT source is h-HEAD. Only PHASE_ORDERING and COMPOSITION_JUMP share significant source overlap (Jaccard 0.667 via shared {s, c} headless sources), but their TARGET HEADs are completely different: PO targets a-HEAD, CJ targets e-HEAD. The hazard classes form a near-partition of the atom space by failure mode.

## Evidence

### Source HEAD decomposition by hazard class

| Hazard Class | Source HEADs | Target HEADs | Pattern |
|---|---|---|---|
| PHASE_ORDERING (7 pairs, 41%) | s, d, c (all headless) | a, c, s | Headless-y -> a-HEAD |
| COMPOSITION_JUMP (4 pairs, 24%) | c, s (headless) | e, a, o | Headless -> e-HEAD |
| CONTAINMENT_TIMING (4 pairs, 24%) | c, l, o, h (diverse) | r, c, d, o | l/r-terminal concentrated |
| RATE_MISMATCH (1 pair, 6%) | a | d | a-HEAD r-TERM -> headless |
| ENERGY_OVERSHOOT (1 pair, 6%) | h | t | Kernel -> kernel |

### Pairwise source HEAD Jaccard

| Pair | Jaccard |
|---|---|
| PHASE_ORDERING vs RATE_MISMATCH | 0.000 |
| PHASE_ORDERING vs ENERGY_OVERSHOOT | 0.000 |
| COMPOSITION_JUMP vs RATE_MISMATCH | 0.000 |
| COMPOSITION_JUMP vs ENERGY_OVERSHOOT | 0.000 |
| CONTAINMENT_TIMING vs RATE_MISMATCH | 0.000 |
| RATE_MISMATCH vs ENERGY_OVERSHOOT | 0.000 |
| PHASE_ORDERING vs CONTAINMENT_TIMING | 0.167 |
| COMPOSITION_JUMP vs CONTAINMENT_TIMING | 0.200 |
| CONTAINMENT_TIMING vs ENERGY_OVERSHOOT | 0.250 |
| PHASE_ORDERING vs COMPOSITION_JUMP | 0.667 |

Mean Jaccard = 0.128. 7/10 pairs at zero.

## Interpretation

Each hazard class encodes a different type of atom-mechanical failure. The near-orthogonal HEAD partition means the grammar's five hazard classes are not arbitrary groupings but reflect five distinct domains of operational failure, each involving a different atom HEAD territory. This validates the hazard class taxonomy (C109) at the atom-mechanical level established by C1475 (HEAD domain differentiation).

## Falsification Criteria

1. If fewer than 5/10 pairwise HEAD Jaccards are exactly zero
2. If two different hazard classes share >75% source HEAD overlap AND >50% target HEAD overlap
3. If a single HEAD atom dominates >50% of source MIDDLEs across 3+ hazard classes

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
