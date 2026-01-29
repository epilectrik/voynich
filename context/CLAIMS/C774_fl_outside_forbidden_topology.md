# C774: FL Outside Forbidden Topology

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

FL classes (7, 30, 38, 40) are not present in any of the 17 forbidden transition pairs. FL operates below/outside the hazard topology layer.

## Evidence

From t4_fl_hazard_relationship.py:

**Forbidden Pair Check:**
- 17 forbidden pairs define hazard topology (C109-C114)
- FL classes present in forbidden pairs: 0

**Forbidden Pair Composition:**
The 17 forbidden pairs involve:
- CC classes (10, 11, 12, 17)
- FQ classes (9, 23)
- EN classes (31, 32)

FL (7, 30, 38, 40) is completely absent.

**FL Transition Patterns:**
Despite not being in forbidden pairs, FL participates in thousands of transitions:
- FL -> EN: 25.1%
- FL -> FQ: 22.5% (escape route)
- FL -> UN: 28.8%
- FL -> AX: 15.0%
- FL -> FL: 9.9%
- FL -> CC: 5.2%

None of these involve forbidden pairs because FL classes are not participants.

## Interpretation

FL's absence from forbidden pairs confirms it operates as primitive substrate:

1. **Layer Separation:** Hazard topology is defined at CC/FQ/EN level, not FL level
2. **Substrate Function:** FL provides material flow; hazard constraints operate on what happens AFTER FL
3. **Design Choice:** FL being outside hazards may allow unconstrained flow that other roles then modulate

The grammar architecture:
```
FL (substrate) -> [Hazard-free flow]
    |
    v
EN/CC/FQ (kernel layer) -> [Hazard topology applies here]
```

## Provenance

- t4_fl_hazard_relationship.json: fl_in_forbidden_pairs = 0
- Relates to: C109-C114 (hazard topology), C770-C772 (FL substrate)

## Status

CONFIRMED - FL is outside the 17-pair hazard topology.
