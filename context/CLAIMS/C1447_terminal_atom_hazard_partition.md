# C1447: Terminal Atom Hazard Partition

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, hazard, partition, FLOW, CONTAINMENT, C109, C1440, C1437
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

Terminal atoms partition into three hazard tiers: HIGH (>30%): r (92.58%), n (38.97%), l (30.88%); LOW (1-20%): e (16.49%), y (15.82%); ZERO (0%): k, m, h. r-terminal is the dominant hazard concentrator with 92.58% of its 1,962 tokens in hazard categories. The three ZERO-hazard terminals (k, m, h) align with THERMAL, batch-close, and MONITORING functions respectively.

## Evidence

### Terminal hazard rates

| Terminal | N tokens | Hazard rate | Role |
|----------|----------|------------|------|
| r | 1,962 | 92.58% | Pure hazard concentrator |
| n | 2,147 | 38.97% | Transition endpoint |
| l | 2,568 | 30.88% | State marker |
| e | 540 | 16.49% | Thermal target (ee frame only) |
| y | 4,780 | 15.82% | Operation closer |
| k | 909 | 0.0% | Safe thermal |
| m | 289 | 0.0% | Safe batch-close (confirms C1437) |
| h | 1,284 | 0.0% | Transparent monitor |

### Tier boundaries

- HIGH to LOW gap: 14.1 percentage points (l 30.88% to e 16.49%)
- LOW to ZERO gap: 15.8 percentage points (y 15.82% to k/m/h 0.0%)
- Within HIGH: r dominates at 2.4x the next highest (n)

### Relationship to C1440 opacity gradient

| Opacity Tier | Terminals | Mean hazard rate |
|-------------|-----------|-----------------|
| OPAQUE (n, y, m) | Mixed: n=38.97%, y=15.82%, m=0.0% | 18.3% |
| SEMI_TRANSPARENT (l, r) | Both HIGH: l=30.88%, r=92.58% | 56.5% |
| TRANSPARENT (h) | ZERO: h=0.0% | 0.0% |

The hazard partition cross-cuts the opacity gradient: OPAQUE terminals span all three hazard tiers (m=ZERO, y=LOW, n=HIGH).

## Interpretation

r-terminal (FLOW 76.2%, C1195 "respond") is the system's primary hazard vector. Material flow responses are inherently dangerous. The ZERO-hazard terminals represent three different safety domains: k=safe energy, m=safe closure, h=safe monitoring. Hazard is concentrated in the FLOW/TRANSITION terminal domain (r, n, l) and absent from the THERMAL/MONITORING/CLOSURE domain (k, m, h).

## Falsification Criteria

1. If any ZERO-tier terminal moves above 2% hazard
2. If r-terminal drops below 70% hazard

## Method

- 23,096 clean Currier B tokens classified by MIDDLE terminal atom
- Hazard = FLOW + CONTAINMENT categories (C1280)
- 8 terminal atoms with N >= 50 tokens analyzed

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions)
- C1195 (atom gloss confidence tiers)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1437 (m-terminal complete hazard exclusion)
- C1440 (three-tier terminal opacity gradient)
