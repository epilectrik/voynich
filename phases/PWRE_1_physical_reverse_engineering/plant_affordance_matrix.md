# AXIS A: Plant Affordance Matrix

**Goal:** Identify minimal physical capabilities any viable plant must possess.

**Principle:** Each requirement is phrased negatively where possible - "Plants without X are impossible."

---

## Executive Summary

The controller architecture implies **12 necessary physical affordances**. Plants lacking ANY of these cannot be governed by this controller.

| Category | Affordances | Key Constraints |
|----------|-------------|-----------------|
| Feedback | 2 | C171, C366 |
| Stability | 2 | C105, C182 |
| Reversibility | 2 | C391, C074 |
| Risk Topology | 3 | C109, C107, C458 |
| State Structure | 3 | C469, C475, C383 |

---

## 1. Feedback Affordances

### A1: Continuous Observability
**Source:** C171 (Closed-loop only)

**Controller Feature:**
> "Of all purpose classes tested, only continuous closed-loop process control is structurally compatible with the Currier B grammar."

**Physical Requirement:**
The plant MUST provide continuous observable state variables that can be monitored without interrupting the process.

**Negative Formulation:**
> **Plants that cannot be observed during operation are IMPOSSIBLE.**

Examples of excluded plants:
- Sealed batch processes where state is unknown until opening
- Single-shot transformations with no intermediate readout
- Processes whose state is only known at completion

---

### A2: Intervention Points
**Source:** C366 (LINK marks monitoring-intervention boundary)

**Controller Feature:**
> "LINK is boundary between monitoring and intervention phases... LINK density 38%."

**Physical Requirement:**
The plant MUST support intervention at multiple points during operation. The controller assumes ~38% of operational cycles include decision points.

**Negative Formulation:**
> **Plants that cannot be intervened upon once started are IMPOSSIBLE.**

---

## 2. Stability Affordances

### A3: Equilibration Targets
**Source:** C105 (e = STABILITY_ANCHOR)

**Controller Feature:**
> "Kernel 'e' anchors system to stable state. 54.7% of recovery paths pass through 'e'."

**Physical Requirement:**
The plant MUST have stable equilibrium states that can serve as recovery targets. Over half of all recovery operations aim for a stability anchor.

**Negative Formulation:**
> **Plants without accessible stable equilibria are IMPOSSIBLE.**

This excludes:
- Runaway processes with no equilibrium
- Processes where stability is all-or-nothing (no partial return)
- Purely chaotic systems with no attractors

---

### A4: Restart Capability
**Source:** C182 (Restart = higher stability)

**Controller Feature:**
> "Restart-capable folios: 0.589 vs 0.393 stability."

**Physical Requirement:**
The plant MUST support restart/recovery operations that restore viability. The 50% stability improvement from restart capability indicates this is architecturally load-bearing.

**Negative Formulation:**
> **Plants that cannot be partially reset are IMPOSSIBLE.**

---

## 3. Reversibility Affordances

### A5: Bidirectional Phase Transitions
**Source:** C391 (Time-reversal symmetry)

**Controller Feature:**
> "H(X|past k) = H(X|future k). Bidirectional adjacency constraints."

**Physical Requirement:**
The plant MUST exhibit phase transitions that are reversible at the control timescale. The grammar encodes symmetric forward/backward predictability.

**Negative Formulation:**
> **Plants with irreversible phase transitions at control timescale are IMPOSSIBLE.**

This excludes:
- Combustion processes (irreversible oxidation)
- Hardening/curing processes (one-way polymerization)
- Processes where "undo" is not physically possible

---

### A6: Convergent Trajectories
**Source:** C074 (Dominant convergence)

**Controller Feature:**
> "Programs converge to STATE-C with high probability."

**Physical Requirement:**
The plant MUST have a convergent state-space structure where diverse trajectories funnel toward common endpoints.

**Negative Formulation:**
> **Plants with divergent or chaotic state-space are IMPOSSIBLE.**

---

## 4. Risk Topology Affordances

### A7: Categorizable Hazards
**Source:** C109 (5 Hazard Classes)

**Controller Feature:**
17 forbidden transitions cluster into exactly 5 failure classes:
- PHASE_ORDERING (41%)
- COMPOSITION_JUMP (24%)
- CONTAINMENT_TIMING (24%)
- RATE_MISMATCH (6%)
- ENERGY_OVERSHOOT (6%)

**Physical Requirement:**
The plant MUST have failure modes that are:
1. Categorically distinct (not continuous degradation)
2. Dominated by phase/ordering issues (41%)
3. Composition-sensitive (24%)
4. Timing-sensitive for containment (24%)

**Negative Formulation:**
> **Plants with uncategorizable or continuously-graded failure modes are IMPOSSIBLE.**

---

### A8: Kernel-Mediated Risk
**Source:** C107 (Kernel boundary-adjacent)

**Controller Feature:**
> "All kernel nodes are BOUNDARY_ADJACENT to forbidden transitions. Kernel controls hazard proximity."

**Physical Requirement:**
The plant's hazard states MUST be reachable primarily through a small set of control operations (k, h, e). Risk is not diffuse but concentrated at specific intervention points.

**Negative Formulation:**
> **Plants where hazards arise spontaneously without control intervention are IMPOSSIBLE.**

---

### A9: Controllable Hazard Exposure
**Source:** C458 (Design clamp)

**Controller Feature:**
> "Hazard exposure, kernel contact, and intervention diversity exhibit extremely low variance across folios (CV = 0.04-0.11)."

**Physical Requirement:**
The plant MUST allow hazard exposure to be tightly regulated. All programs maintain similar hazard levels (4-11% CV), indicating hazard is constrained by controller design, not by individual program needs.

**Negative Formulation:**
> **Plants where hazard exposure cannot be standardized are IMPOSSIBLE.**

---

## 5. State Structure Affordances

### A10: Categorical Discrimination
**Source:** C469 (Categorical resolution principle)

**Controller Feature:**
> "Operational conditions are represented categorically via token legality, not parametrically via encoded values. 73.5% of MIDDLEs appear in only 1 AZC folio."

**Physical Requirement:**
The plant's operational conditions MUST be categorically distinguishable. Temperature, pressure, material state must form discrete zones, not continuous gradients.

**Negative Formulation:**
> **Plants requiring fine-grained parametric control are IMPOSSIBLE.**

This excludes:
- Precision measurement processes
- Processes requiring numerical setpoints
- Continuously-variable control regimes

---

### A11: Sparse Compatibility Structure
**Source:** C475 (MIDDLE atomic incompatibility)

**Controller Feature:**
> "Only 4.3% of MIDDLE pairs can legally co-occur... 95.7% are statistically illegal."

**Physical Requirement:**
The plant's operational constraints MUST form a sparse compatibility lattice. Most combinations of conditions are forbidden; only specific allowed configurations are viable.

**Negative Formulation:**
> **Plants where most parameter combinations are legal are IMPOSSIBLE.**

This suggests:
- Strong interaction effects between conditions
- Non-linear constraint satisfaction
- "Either X or Y, rarely both" logic

---

### A12: Type-Based Behavior
**Source:** C383 (Global type system)

**Controller Feature:**
> "Type determines behavior, grammar determines sequence. No semantic transfer between systems."

**Physical Requirement:**
The plant's components MUST behave according to type categories, not individual identity. The same material class behaves the same way regardless of specific identity.

**Negative Formulation:**
> **Plants requiring substance-specific handling rules are IMPOSSIBLE.**

---

## Derived Plant Profile

Combining all affordances, the viable plant MUST exhibit:

| Property | Requirement |
|----------|-------------|
| **Observability** | Continuous, non-destructive state monitoring |
| **Controllability** | Intervention possible at ~38% of operational cycles |
| **Stability** | Accessible equilibrium states for recovery |
| **Reversibility** | Bidirectional phase transitions at control timescale |
| **Convergence** | Trajectories funnel toward common endpoints |
| **Hazard Structure** | Categorical failure modes, kernel-mediated |
| **State Space** | Sparse compatibility, categorical discrimination |
| **Type Semantics** | Behavior by type, not by individual identity |

---

## Eliminated Plant Classes (Preview of Axis D)

Based on affordance analysis, the following are already ruled out:

| Plant Class | Failing Affordance |
|-------------|-------------------|
| Sealed batch processes | A1 (no observability) |
| One-shot transformations | A2 (no intervention) |
| Runaway processes | A3 (no equilibrium) |
| Combustion/hardening | A5 (irreversible) |
| Precision measurement | A10 (parametric, not categorical) |
| Substance-specific handling | A12 (type-based, not identity-based) |

---

## Epistemic Status

All affordances are derived from Tier 0-2 constraints via logical necessity. Each represents a NECESSARY condition - the controller cannot function without it.

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

## Data Sources

| Constraint | Source File |
|------------|-------------|
| C171 | `context/CLAIMS/C171_closed_loop_only.md` |
| C105, C107 | `context/CLAIMS/grammar_system.md` |
| C109 | `context/CLAIMS/C109_hazard_classes.md` |
| C182 | `context/CLAIMS/operations.md` |
| C366 | `context/CLAIMS/morphology.md` |
| C391 | `context/CLAIMS/morphology.md` |
| C458 | `context/CLAIMS/C458_execution_design_clamp.md` |
| C469 | `context/CLAIMS/azc_system.md` |
| C475 | `context/CLAIMS/currier_a.md` |
| C383 | `context/CLAIMS/C383_global_type_system.md` |
| C074 | `context/CLAIMS/C074_dominant_convergence.md` |
