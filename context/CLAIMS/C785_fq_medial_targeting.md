# C785: FQ Medial Targeting

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

When FQ escapes to FL, it targets MEDIAL state at 77.2%. FQ does not escape to arbitrary FL positions but preferentially routes to mid-process state.

---

## Quantitative

FQ -> FL state distribution:
| FL State | Count | Percentage |
|----------|-------|------------|
| MEDIAL | 129 | 77.2% |
| LATE | 21 | 12.6% |
| EARLY | 15 | 9.0% |
| OTHER | 2 | 1.2% |

FQ overall routing:
| Destination | Count |
|-------------|-------|
| EN | 770 |
| UN | 687 |
| FQ | 470 |
| AX | 409 |
| FL | 167 |
| CC | 110 |

FQ chain rate: 18.0%
FQ final rate: 15.0%

---

## Interpretation

FQ escape doesn't reset to process start (EARLY) or jump to completion (LATE). The 77% MEDIAL targeting suggests:
- Escape routes re-inject material at mid-process
- Recovery attempts from MEDIAL position
- Process continuation rather than restart

This integrates with C777 (FL state index) - FQ escape targets the "working" portion of the process.

---

## Dependencies

- C777 (FL state index)
- C781 (FQ phase bypass)
- C467 (escape definitions)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t3_fq_escape_destination.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t3_fq_escape_destination.json
```
