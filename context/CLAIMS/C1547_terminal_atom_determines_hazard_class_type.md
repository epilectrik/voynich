# C1547: TERMINAL Atom Determines Hazard Class Type (V=0.306, Stronger Than HEAD V=0.219)

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, hazard, class, PHASE_ORDERING, CONTAINMENT_TIMING, y-terminal, l-terminal, C1447, C1483, C1487, C1528, C1546
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

The TERMINAL atom of hazard source MIDDLEs determines WHICH hazard class is triggered (chi-squared=8622.5, V=0.306), with stronger discriminative power than the HEAD slot (V=0.219). y-terminal MIDDLEs feed exclusively into PHASE_ORDERING (675/675 = 100%). l-terminal MIDDLEs feed exclusively into CONTAINMENT_TIMING (855/855 = 100%). bare-terminal feeds RATE_MISMATCH (5 tokens). h-terminal feeds ENERGY_OVERSHOOT (2 tokens). The TERMINAL atom is the hazard class SELECTOR — it determines not WHETHER hazard occurs (that is HEAD-mediated per C1546) but WHAT TYPE of hazard results.

## Evidence

### Terminal atom x hazard class contingency (B corpus, Phase 546)

| Terminal atom | Hazard class | Source tokens | % of class |
|---|---|---|---|
| y | PHASE_ORDERING | 675 | 100% |
| l | CONTAINMENT_TIMING | 855 | 100% |
| bare (no terminal) | RATE_MISMATCH | 5 | 100% |
| h | ENERGY_OVERSHOOT | 2 | 100% |

Chi-squared = 8622.5, Cramer's V = 0.306, p < 0.0001.

### Comparison with HEAD slot

| Slot | Chi-squared | Cramer's V | Interpretation |
|---|---|---|---|
| TERMINAL | 8622.5 | 0.306 | Determines hazard CLASS TYPE |
| HEAD | 4411.9 | 0.219 | Determines hazard PRESENCE (0% vs 24.5%) |

TERMINAL V is 1.40x HEAD V. The two slots carry COMPLEMENTARY hazard information: HEAD gates entry into hazard (binary), TERMINAL selects the hazard type (categorical).

### Mapping to C1487 terminal functional taxonomy

| Terminal tier (C1487) | Hazard class | Mechanism |
|---|---|---|
| CHANNELED: y (OPERATION) | PHASE_ORDERING | y = operation closure; ordering failure when operations sequenced incorrectly |
| SEMI-TRANSPARENT: l (STAGING) | CONTAINMENT_TIMING | l = state/staging marker; containment failure when staging is mistimed |
| OPAQUE: m (TRANSITION) | None | m = closure valve; too categorical for hazard entry |
| DIFFUSE: h (transparent) | ENERGY_OVERSHOOT | h = passthrough; residual energy from unconstrained terminal |

## Interpretation

The hazard topology is a COMPOSITIONAL property of the MIDDLE instruction grammar. HEAD absence permits hazard entry (C1546). TERMINAL atom then selects the failure mode. This creates a two-layer hazard architecture: (1) domain gate at INITIAL position, (2) failure-type selector at TERMINAL position. The modifier atoms in between are IRRELEVANT to hazard class — they modify the operation but not the failure mode. This extends C1447 (terminal atom hazard partition) with the quantitative dominance of TERMINAL over HEAD in class-type determination.

## Falsification Criteria

1. If a y-terminal source MIDDLE is found to feed into a non-PHASE_ORDERING hazard class
2. If an l-terminal source MIDDLE feeds into a non-CONTAINMENT_TIMING class
3. If TERMINAL V drops below HEAD V in extended data

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
