# C782: CC Kernel Paradox

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

CC role classes exhibit a bifurcated kernel profile: classes 10 and 11 have 0% kernel rate while class 17 has 88.2% kernel rate, creating two functionally distinct CC subgroups.

---

## Quantitative

| Class | Tokens | Kernel Rate |
|-------|--------|-------------|
| 10 | 314 | 0.0% |
| 11 | 421 | 0.0% |
| 12 | 0 | N/A |
| 17 | 288 | 88.2% |

CC divides into:
- **Group A (10, 11):** Zero kernel, pure hazard sources
- **Group B (17):** High kernel, hazard targets

---

## Interpretation

CC is not a homogeneous "control" role. The kernel bifurcation suggests:
- Classes 10, 11 are hazard **triggers** (no internal kernel substrate)
- Class 17 is a hazard **buffer** (kernel-rich, absorbs transitions)
- Class 12 may be structural placeholder (zero tokens observed)

---

## Dependencies

- C121 (49 classes)
- C756 (coverage optimization)
- C467 (kernel definitions)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t1_cc_paradox.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t1_cc_paradox.json
```
