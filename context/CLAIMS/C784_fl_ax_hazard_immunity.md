# C784: FL/AX Hazard Immunity

**Tier:** 2 (Validated)
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

FL and AX roles never appear in any of the 17 forbidden class pairs. They are structurally exempt from hazard topology.

---

## Quantitative

Roles in forbidden pairs:
- CC: 12 participations (as source and target)
- EN: 4 participations (as source only: classes 31, 32)
- FQ: 9 participations (as target mostly)
- FL: 0 participations
- AX: 0 participations

---

## Interpretation

FL and AX operate in a "safe zone" outside hazard constraints:
- **FL** indexes state without triggering hazards (C774, C777)
- **AX** provides material substrate without hazard involvement

This confirms FL and AX as infrastructure layers, not control operators. Hazard topology is confined to CC/EN/FQ interactions.

---

## Dependencies

- C467 (forbidden pair definitions)
- C774 (FL outside forbidden topology)
- C780 (role kernel taxonomy)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t2_forbidden_pair_pattern.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t2_forbidden_pair_pattern.json
```
