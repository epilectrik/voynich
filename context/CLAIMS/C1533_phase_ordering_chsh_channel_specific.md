# C1533: PHASE_ORDERING Is CHSH-Channel Specific

**Tier:** 2
**Scope:** B, MIDDLE, atom, PREFIX, hazard, PHASE_ORDERING, CHSH, channel, violation, C109, C929, C1449, C1451, C1529
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

PHASE_ORDERING is the only hazard class where CHSH (ch/sh PREFIX) is the dominant channel: 28.4% of PHASE_ORDERING source MIDDLE tokens are CHSH-prefixed, vs 0-12.2% for other classes. 7/11 actual corpus forbidden violations occur in CHSH-prefixed contexts. Other hazard classes are BARE-dominant: CONTAINMENT_TIMING 34.5% BARE, RATE_MISMATCH 36.6% BARE, COMPOSITION_JUMP 100% BARE. QO (thermal channel) has ZERO violations and minimal presence in any hazard class source vocabulary.

## Evidence

### PREFIX channel by hazard class

| Hazard Class | CHSH% | QO% | BARE% | Dominant |
|---|---|---|---|---|
| PHASE_ORDERING | 28.4% | 1.8% | 16.7% | CHSH |
| CONTAINMENT_TIMING | 8.1% | 12.2% | 34.5% | BARE |
| RATE_MISMATCH | 10.8% | 0.9% | 36.6% | BARE |
| COMPOSITION_JUMP | 0% | 0% | 100% | BARE |
| ENERGY_OVERSHOOT | 0% | 0% | 0% | Other |

### Violation channel attribution

- 7/11 corpus violations in CHSH-prefixed tokens (63.6%)
- 4/11 in other PREFIX contexts (likely BARE/ok/ot)
- 0/11 in QO-prefixed tokens

### Connection to C929

ch/sh encode sensory modality discrimination (C929): ch = active test, sh = passive monitor. PHASE_ORDERING failures concentrate in these checkpoint operations — phase ordering errors happen during sensory verification, when the operator is testing/monitoring and incorrectly sequences the next operation.

### QO immunity

QO (thermal channel) maintains its complete hazard immunity established in C601: zero participation as hazard source, zero violations. The safe energy pathway (F-B-002) extends to all 5 hazard classes.

## Falsification Criteria

1. If another hazard class exceeds PHASE_ORDERING in CHSH% (>28.4%)
2. If QO violations appear in any hazard class
3. If CHSH-attributed violations drop below 40% of total

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
