# C1159: Boundary Divergence Is a Routing Shift, Not AXM Persistence Decay

**Tier:** 2
**Scope:** B, line, transition dynamics
**Phase:** BOUNDARY_DIVERGENCE_DECOMPOSITION (Phase 414)
**Depends on:** C1156, C1157

## Statement

The positional transition shift at line boundaries is driven by inter-state routing changes, not by AXM self-transition decay. AXM→AXM accounts for only 3.2% of total transition delta magnitude between zones. The dominant shifts are transitions between non-AXM states and AXM: at entry, AXm→AXM (+0.124) and FQ→AXM (+0.103) are elevated — the system routes back into AXM from other states. At exit, CC→AXM (-0.296) and FL_HAZ→AXM (-0.129) drop — return routes from control/hazard states weaken.

## Evidence

**Top entry deltas (entry - interior):**

| Transition | Delta |
|-----------|-------|
| AXm→AXM | +0.124 |
| FL_SAFE→CC | -0.115 |
| FQ→AXM | +0.103 |
| AXm→FQ | -0.092 |
| FL_SAFE→FL_HAZ | +0.090 |

**Top exit deltas (exit - interior):**

| Transition | Delta |
|-----------|-------|
| CC→AXM | -0.296 |
| FL_SAFE→AXM | +0.146 |
| FL_HAZ→AXM | -0.129 |
| CC→FQ | +0.125 |
| FL_SAFE→FQ | -0.115 |

**AXM→AXM fraction:** Entry 2.4%, Exit 3.6%, Combined 3.2%.

## Structural Implication

C1156 showed AXM self-transition drops from 0.730 (entry) to 0.633 (exit). This appeared to be about AXM persistence decay. C1159 reveals the mechanism is different: the shift is in ROUTING — how other states feed into and out of AXM. At line entry, the system is strongly routed BACK to AXM from wherever it was (AXm, FQ). The interior relaxes these routes, allowing the system to wander. The exit redistributes routing further away from AXM return paths. The line is a "reset → explore → hand off" arc at the routing level.
