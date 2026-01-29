# Phase: CONTROL_TOPOLOGY_ANALYSIS

**Status:** Complete
**Constraints:** C782-C787

---

## Objective

Map the topology of hazard/control relationships in B grammar: forbidden pair directionality, CC role bifurcation, FL/AX immunity, escape routing patterns, and FL state transition grammar.

---

## Background

FL_PRIMITIVE_ARCHITECTURE (C770-C781) established that FL is a state index and roles partition kernel responsibilities. This phase extends to examine the **control topology** - how hazard flows, what's exempt, and how state transitions work.

---

## Key Findings

### CC Kernel Paradox (C782)

CC role is not homogeneous. Two functional subgroups:
- **Group A (classes 10, 11):** 0% kernel rate, act as hazard **sources**
- **Group B (class 17):** 88.2% kernel rate, acts as hazard **buffer/target**

This explains why CC participates heavily in forbidden pairs - the two subgroups have different functions.

### Forbidden Pair Asymmetry (C783)

All 17 forbidden class pairs are **directional** (asymmetric). Zero symmetric pairs exist.

| Pattern | Count |
|---------|-------|
| CC->FQ | 8 |
| CC->CC | 4 |
| EN->CC | 4 |
| FQ->FQ | 1 |

Hazard flows one way. If A->B is forbidden, B->A is permitted.

### FL/AX Hazard Immunity (C784)

FL and AX never appear in any forbidden pair:
- CC: 12 participations
- FQ: 9 participations
- EN: 4 participations
- FL: 0 participations
- AX: 0 participations

FL and AX operate outside the hazard control layer. They provide infrastructure (state indexing, material substrate) without triggering or absorbing hazards.

### FQ Medial Targeting (C785)

When FQ escapes to FL, it routes to MEDIAL state at 77.2%:

| FL State | Percentage |
|----------|------------|
| MEDIAL | 77.2% |
| LATE | 12.6% |
| EARLY | 9.0% |

Escape doesn't reset to start or jump to completion. It re-injects at mid-process.

### FL Forward Bias (C786)

FL state transitions are forward-biased (5:1 ratio):

| Direction | Percentage |
|-----------|------------|
| FORWARD | 27.3% |
| SAME | 68.2% |
| BACKWARD | 4.5% |

State progression dominates regression. FL indexes a mostly one-way process.

### FL State Reset Prohibition (C787)

LATE->EARLY transition never occurs (0 instances). Full state reset is forbidden. Once FL reaches LATE, it cannot return directly to EARLY. Recovery must go through MEDIAL (if at all).

---

## Architectural Implications

1. **Hazard is directional:** Not mutual exclusion but directed flow. Sources (CC Group A) can trigger; targets (CC Group B, FQ) can receive. EN can trigger CC but not vice versa.

2. **FL/AX are infrastructure:** They don't participate in hazard topology. FL indexes state; AX provides material. Neither triggers nor absorbs hazards.

3. **Escape routes to mid-process:** FQ doesn't restart or complete - it re-injects at MEDIAL. Recovery is resumption, not restart.

4. **State progression is constrained:** Forward-biased with no full reset. LATE->EARLY is forbidden. This builds irreversibility into the process.

---

## Scripts

| Script | Test | Purpose |
|--------|------|---------|
| t1_cc_paradox.py | T1 | CC kernel profile by class |
| t2_forbidden_pair_pattern.py | T2 | Forbidden pair structure analysis |
| t3_fq_escape_destination.py | T3 | FQ routing destinations |
| t4_fl_state_transitions.py | T4 | FL state transition grammar |

---

## Dependencies

- C467 (forbidden pair definitions)
- C777 (FL state index)
- C780 (role kernel taxonomy)
- C781 (FQ phase bypass)

---

## Integration with Prior Work

| Prior Constraint | Integration |
|------------------|-------------|
| C774 (FL outside forbidden) | Confirmed and extended to AX (C784) |
| C777 (FL state index) | State machine characterized (C786, C787) |
| C781 (FQ phase bypass) | Escape destination mapped (C785) |
| C780 (role kernel taxonomy) | CC bifurcation explained (C782) |
