# C978: Hub-and-Spoke Topology with Sub-2-Token Mixing

**Tier:** 2 | **Scope:** B | **Phase:** MINIMAL_STATE_AUTOMATON

## Statement

The 6-state automaton has hub-and-spoke topology: S4 (AX/EN major, 68% mass) is the universal attractor with all states flowing to it at >56% probability. S1 (FQ, 18%) is the secondary hub. Spectral gap = 0.894, giving mixing time ~1.1 tokens. After 2 tokens, initial state information is effectively lost (max TV distance < 0.012).

## Topology Properties

- **All 36 edges exist** (fully connected), but dominated by S4 attraction
- **12 strong edges** (>0.10), **14 moderate** (0.03-0.10), **7 weak** (0.01-0.03), **3 negligible** (<0.01)
- **S4 self-loop:** 0.698 (expected dwell ~3.3 tokens)
- **FQ self-loop:** 0.251 (25% chaining rate)
- **CC/AXm/FL_SAFE:** Near-zero self-loops (~0.02-0.04), single-token transients

## Hazard Asymmetry

From S4 (AXM): P(→FL_HAZ) = 0.052, P(→FL_SAFE) = 0.008. Ratio = **6.5x**.
Hazard marking is 6.5x more likely than safe flow marking from the operational mass. Confirms C586 (HAZ/SAFE structural split) at automaton level.

## Control Flow Pattern

Every state's dominant exit is S4 (AXM). S4's dominant exit (excluding self) is S1 (FQ, 17.3%), then S0 (FL_HAZ, 5.2%). The pattern is:

```
Periphery (CC, FL_HAZ, FL_SAFE, AXm) → AXM (operational mass) ↔ FQ (scaffold)
```

## Interpretation

Fast mixing + hub dominance = no long-range sequential memory at the state level. Consistent with first-order Markov sufficiency (C966). The grammar is a rapidly-mixing recurrent controller, not a sequential processor.

## Provenance

- Confirms: C966 (first-order sufficiency), C586 (FL HAZ/SAFE split)
- Method: `phases/MINIMAL_STATE_AUTOMATON/scripts/t6_state_topology.py`
- Results: `phases/MINIMAL_STATE_AUTOMATON/results/t6_state_topology.json`
