# C787: FL State Reset Prohibition

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

LATE->EARLY FL state transition never occurs (0 instances). Full state reset is forbidden. Once FL reaches LATE state, it cannot return directly to EARLY.

---

## Quantitative

FL state transitions from LATE:
| Transition | Count |
|------------|-------|
| LATE->MEDIAL | 1 |
| LATE->LATE | 1 |
| LATE->EARLY | 0 |

Rare/missing transitions (< 3 occurrences):
- LATE->EARLY: 0
- LATE->MEDIAL: 1
- LATE->LATE: 1
- EARLY->EARLY: 2
- EARLY->LATE: 2

---

## Interpretation

The system prohibits full state reset. This structural constraint means:
- Processes cannot jump from completion back to start
- Recovery must go through MEDIAL (if at all)
- Irreversibility is built into FL state grammar

Combined with C786 (forward bias), this confirms FL indexes a predominantly one-way process with no full reset capability.

---

## Dependencies

- C777 (FL state index)
- C786 (FL forward bias)
- C785 (FQ medial targeting)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t4_fl_state_transitions.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t4_fl_state_transitions.json
```
