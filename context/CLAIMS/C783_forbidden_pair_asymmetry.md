# C783: Forbidden Pair Asymmetry

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

All 17 forbidden class pairs are asymmetric (directional). No symmetric forbidden pairs exist. Hazard is a directed graph, not an undirected constraint.

---

## Quantitative

| Pattern | Count | Pairs |
|---------|-------|-------|
| CC->FQ | 8 | (12,23), (12,9), (17,23), (17,9), (10,23), (10,9), (11,23), (11,9) |
| CC->CC | 4 | (10,12), (10,17), (11,12), (11,17) |
| EN->CC | 4 | (32,12), (32,17), (31,12), (31,17) |
| FQ->FQ | 1 | (23,9) |

- Symmetric pairs: 0
- Asymmetric pairs: 17

---

## Interpretation

Hazard flows in one direction. If A->B is forbidden, B->A is permitted. This creates:
- Clear "upstream" hazard sources (CC Group A: 10, 11)
- Clear "downstream" hazard targets (CC Group B: 12, 17; FQ: 9, 23)
- Directional control flow, not mutual exclusion

---

## Dependencies

- C467 (forbidden pair definitions)
- C782 (CC kernel paradox)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t2_forbidden_pair_pattern.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t2_forbidden_pair_pattern.json
```
