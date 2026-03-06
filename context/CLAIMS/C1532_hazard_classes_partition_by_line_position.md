# C1532: Hazard Classes Partition by Line Position

**Tier:** 2
**Scope:** B, MIDDLE, hazard, failure-class, line, position, zone, gradient, C109, C1463, C1464, C1465, C1528
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

The 5 hazard failure classes occupy statistically distinct line positions (chi2=46.6, p=0.000079, V=0.066). Mean position ranges from 0.402 (COMPOSITION_JUMP, early/setup) to 0.581 (PHASE_ORDERING, late/closure), a range of 0.179. The ordering is physically coherent: setup errors (COMPOSITION_JUMP, ENERGY_OVERSHOOT) occur early/medially, while closure errors (PHASE_ORDERING, RATE_MISMATCH) occur late. This aligns with C1463's finding that HIGH-hazard frames concentrate at line-final CLOSURE (Q4).

## Evidence

### Positional gradient by hazard class

| Hazard Class | Mean Position | Q0 (Initial) | Q4 (Final) | Bias |
|---|---|---|---|---|
| COMPOSITION_JUMP | 0.402 | 40.0% | 20.0% | Early (N=5) |
| ENERGY_OVERSHOOT | 0.473 | 0% | 0% | Medial (N=2) |
| CONTAINMENT_TIMING | 0.510 | 22.9% | 27.0% | Slight late |
| RATE_MISMATCH | 0.551 | 17.6% | 30.6% | Late |
| PHASE_ORDERING | 0.581 | 13.2% | 30.2% | Late |

### Statistical significance

- Chi-squared: 46.6
- p-value: 0.000079
- Cramer's V: 0.066 (small but genuine effect)
- Positional range: 0.179

### Physical interpretation

The gradient makes operational sense:
- **Early hazards** (COMPOSITION_JUMP): setup errors where wrong material states are combined
- **Medial hazards** (ENERGY_OVERSHOOT): mid-process energy management failures
- **Late hazards** (PHASE_ORDERING, RATE_MISMATCH): closure sequencing errors where completed operations illegally restart

## Falsification Criteria

1. If chi-squared test becomes non-significant (p > 0.05)
2. If positional range drops below 0.10
3. If the early/late ordering inverts (closure errors appear early, setup errors late)

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
