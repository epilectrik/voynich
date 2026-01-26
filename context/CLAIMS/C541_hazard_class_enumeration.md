# C541: Hazard Class Enumeration

**Tier:** 2 | **Status:** CLOSED | **Scope:** HAZARD_TOPOLOGY

---

## Statement

> Only 6 of 49 instruction classes (12.2%) participate in the 17 forbidden transitions. The remaining 43 classes (87.8%) have zero direct hazard involvement.

---

## The 6 Hazard-Involved Classes

| Class | Role | Tokens | Hazard Types |
|-------|------|--------|--------------|
| 7 | FLOW_OPERATOR | ar, al | PHASE_ORDERING, RATE_MISMATCH |
| 8 | ENERGY_OPERATOR | chedy, shedy, chol | COMPOSITION_JUMP, PHASE_ORDERING, CONTAINMENT |
| 9 | FREQUENT_OPERATOR | aiin, or, o | PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT |
| 23 | FREQUENT_OPERATOR | dy, s, y | PHASE_ORDERING, CONTAINMENT |
| 30 | FLOW_OPERATOR | dar, dal, dain | CONTAINMENT, RATE_MISMATCH |
| 31 | ENERGY_OPERATOR | chey, shey, chor | PHASE_ORDERING (6 instances) |

---

## Role-Level Hazard Exposure

| Role | Hazard Exposure | Classes Involved |
|------|-----------------|------------------|
| FLOW_OPERATOR | 1.23% | 7, 30 |
| FREQUENT_OPERATOR | 0.42% | 9, 23 |
| ENERGY_OPERATOR | 0.23% | 8, 31 |
| CORE_CONTROL | **0%** | None |
| AUXILIARY | **0%** | None |

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_hazard_proximity.py`

- Mapped 17 forbidden transitions to instruction classes
- Analyzed 16,054 classified tokens for hazard adjacency
- CORE_CONTROL and all 20 AUXILIARY classes have zero hazard exposure

---

## Interpretation

Hazard architecture is **highly localized** to a small subset of basic operators. Complex forms (qo-family, articulated tokens, ok/ol-prefixed tokens) are structurally excluded from hazard participation.

This suggests deliberate design: hazards occur at fundamental operational boundaries (phase transitions, flow redirects, basic energy operations), not in elaborated forms.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C109 | Extended - enumerates which classes participate |
| C110 | Consistent - PHASE_ORDERING involves Class 31 heavily |
| C112 | Consistent - 59% distant from kernel |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_hazard_proximity.py

---

## Navigation

<- [C540_kernel_bound_morpheme.md](C540_kernel_bound_morpheme.md) | [C542_gateway_terminal_asymmetry.md](C542_gateway_terminal_asymmetry.md) ->
