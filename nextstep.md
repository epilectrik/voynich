# Next Research Phase: Within-AXM Dynamics

**Status:** READY
**Current state:** v3.85 | 901 constraints | 358 phases | Both remotes need push

---

## Context

Phase 358 (C1036) proved that C458's hazard/recovery asymmetry does NOT manifest at the AXM macro-state boundary. Exit allocation, ingress allocation, and dwell duration all show frequency-proportional CV (FQ < FL < CC < AXm). Exit pathways are independently routed (FL/CC rho=-0.003), consistent with PREFIX routing (C1023).

Combined with C1035 (aggregate folio statistics fail), this eliminates two entire categories from the 57% irreducible design freedom space:
1. Folio-level aggregate statistics (C1035)
2. AXM boundary transition proportions (C1036)

**What remains:** The design freedom must live in:
- Within-AXM micro-dynamics (which of 32 AXM classes are active, in what pattern)
- PREFIX routing distributions (how PREFIX channels traffic within AXM)
- Hazard adjacency depth (pre-exit structure, not exit destination)
- Dwell path composition (the sequence within AXM, not just its length)

---

## Proposed Directions (from expert consultation)

### Direction A: Within-AXM Class Composition
AXM contains 32 of 49 classes. For each folio, which are active and in what proportions? Two folios with the same AXM self-transition could have completely different internal profiles.

### Direction B: Pre-Exit Hazard Adjacency
Measure hazard-proximity slope immediately before exit. C1009 showed curvature. Does hazard adjacency variance differ across folios? This is where C458 might actually live.

### Direction C: Conditional Exit Sub-Role Composition
Instead of macro pathway (FQ/FL/CC/AXm), look at sub-role composition within each pathway. C601 shows hazard originates from 3 subgroups. Asymmetry may live at that granularity.

---

## Pending Action

1. Consult expert on which direction to prioritize
2. Design and execute Phase 359
