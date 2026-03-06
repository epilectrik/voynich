# C1530: CONTAINMENT_TIMING Is l/r-Terminal SEMI_TRANSPARENT Class

**Tier:** 2
**Scope:** B, MIDDLE, atom, TERM, hazard, CONTAINMENT_TIMING, l-terminal, r-terminal, SEMI_TRANSPARENT, avoidance, C109, C1440, C1447, C1487
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

CONTAINMENT_TIMING (4/17 forbidden pairs, 24%) concentrates in the l/r-terminal SEMI_TRANSPARENT frame: 75% of source terminals and 100% of target terminals are l or r atoms. Source MIDDLEs (chol, l, or, he) appear 1,129 times in the corpus with ZERO forbidden violations — 100% avoidance rate, making CONTAINMENT_TIMING the most strictly avoided hazard class despite having the most source appearances. This connects to C1440's three-tier opacity gradient: the SEMI_TRANSPARENT tier (l, r: 17-20% suffix rate) is where containment decisions happen and where timing failures would be catastrophic.

## Evidence

### Terminal atom concentration

| Position | l or r atoms | Total | Rate |
|---|---|---|---|
| Source terminals | 3 (l, r, e) | 4 | 75% (l=50%, r=25%) |
| Target terminals | 4 (r, l) | 4 | 100% (r=50%, l=50%) |

### Near-miss analysis

| Source MIDDLE | Corpus appearances | Violations | Avoidance |
|---|---|---|---|
| chol | 0 (phantom) | 0 | N/A |
| l | 427 | 0 | 100% |
| or | 700 | 0 | 100% |
| he | 2 | 0 | 100% |
| **Total** | **1,129** | **0** | **100%** |

### Comparison with other classes

- PHASE_ORDERING: 558 appearances, 10 violations (98.21% avoidance)
- RATE_MISMATCH: 624 appearances, 1 violation (99.84% avoidance)
- CONTAINMENT_TIMING: 1,129 appearances, 0 violations (100% avoidance) -- STRICTEST

## Interpretation

CONTAINMENT_TIMING failures involve containment state changes (l = state/condition, r = flow/response) occurring in the wrong sequence. The SEMI_TRANSPARENT terminals are the hazard-boundary zone where suffix attachment is optional and containment decisions happen (C1440). The grammar enforces absolute avoidance of timing errors in this zone, suggesting containment failures are the highest-stakes failure mode — more dangerous than even phase ordering failures, which are merely disfavored (98.21%).

## Falsification Criteria

1. If CONTAINMENT_TIMING source l/r-terminal rate drops below 50%
2. If corpus violations appear for CONTAINMENT_TIMING (breaking 100% avoidance)
3. If another hazard class achieves a higher avoidance rate with comparable source appearances (>500)

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
