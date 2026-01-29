# C786: FL Forward Bias

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

FL state transitions are forward-biased: 27% progress forward (EARLY->MEDIAL->LATE), 68% stay same, 5% regress backward. State progression dominates regression 5:1.

---

## Quantitative

Direct FL->FL transitions (N=88):

| Direction | Count | Percentage |
|-----------|-------|------------|
| FORWARD | 24 | 27.3% |
| SAME | 60 | 68.2% |
| BACKWARD | 4 | 4.5% |

State transition matrix:
| From->To | Count |
|----------|-------|
| MEDIAL->MEDIAL | 57 |
| EARLY->MEDIAL | 13 |
| MEDIAL->LATE | 9 |
| MEDIAL->EARLY | 3 |
| EARLY->EARLY | 2 |
| EARLY->LATE | 2 |
| LATE->MEDIAL | 1 |
| LATE->LATE | 1 |

---

## Interpretation

FL indexes a mostly-forward process. The 5:1 forward:backward ratio confirms:
- State progression is the dominant mode
- Regression occurs but is rare
- SAME (68%) suggests FL often marks sustained state, not just transitions

This supports the process-indexing interpretation from C777.

---

## Dependencies

- C777 (FL state index)
- C787 (state reset prohibition)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t4_fl_state_transitions.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t4_fl_state_transitions.json
```
