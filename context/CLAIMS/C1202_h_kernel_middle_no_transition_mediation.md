# C1202: H-Kernel in MIDDLE Does Not Mediate Energy Transitions

**Tier:** 2 (ESTABLISHED -- negative result)
**Scope:** B
**Phase:** ENERGY_MODE_TRANSITION (Phase 426)
**Relates to:** C1154 (h-kernel domain dependence), C1200 (k/e state carryover), C1201 (PREFIX routing), C1174 (LINK artifact)

---

## Statement

The presence of h-kernel character in a token's MIDDLE does not mediate k/e energy state transitions. In the 3-token window A-B-C, mediator B's h-rate at k->e transitions (5.5%) is LOWER than at k->k continuations (7.2%), delta = -0.016, permutation p = 0.852. The transition-mediation function resides in the PREFIX layer (C1201), not in MIDDLE kernel content.

| Measure | Value |
|---------|-------|
| Mediator h-rate at k->e transitions | 5.5% (38/685) |
| Mediator h-rate at k->k continuations | 7.2% (32/445) |
| Delta (k direction) | -0.016 |
| Permutation p-value (1000 iterations) | 0.852 |
| Mediator h-rate at e->k transitions | 9.4% (20/213) |
| Mediator h-rate at e->e continuations | 4.1% (20/488) |
| Delta (e direction) | +0.053 |

One asymmetry: e->k transitions show elevated h-mediation (+0.053), suggesting h-kernel may play a weak role in cool-to-heat switches specifically. This was not formally tested with permutation and should be considered exploratory.

---

## Section Stratification (C1154 Prediction)

| Section | k->e h-rate | k->k h-rate | Delta | Sufficient |
|---------|-------------|-------------|-------|------------|
| STARS_RECIPE | 9.4% | 7.3% | +0.021 | Yes |
| HERBAL | 2.8% | 5.7% | -0.029 | Yes |
| BIO | 2.6% | 7.9% | -0.053 | Yes |

STARS_RECIPE is the only section with positive h-mediation delta, confirming C1154's prediction that h-kernel is most program-specific in STARS_RECIPE (2.18x variance). The global negative result is driven by BIO and HERBAL where h-kernel is section-determined rather than program-specific.

---

## Interpretation

The initial hypothesis -- that h-kernel tokens in MIDDLEs serve as conditional triggers for energy mode transitions -- is not supported. The h character in a MIDDLE encodes kernel composition of the operation itself, not a monitoring/switching function. The monitoring and state-routing function is carried by PREFIX ch/sh (C1201), confirming the architectural separation between PREFIX (control interface) and MIDDLE (operation content).

This result is consistent with C1174 (LINK as morphological artifact): the functional interpretation of h-containing morphemes should focus on PREFIX position (ch/sh), not MIDDLE position.

---

## Method

- 3-token windows A-B-C on 2,420 Currier B lines
- Classify by A's terminal and C's initial character (k or e)
- Measure B's h-kernel rate ('h' in B.middle) at transitions vs continuations
- Permutation test: 1000 within-line shuffles of MIDDLE order

**Script:** `phases/ENERGY_MODE_TRANSITION/scripts/h_kernel_transition_test.py`
**Results:** `phases/ENERGY_MODE_TRANSITION/results/h_kernel_transition_results.json`
