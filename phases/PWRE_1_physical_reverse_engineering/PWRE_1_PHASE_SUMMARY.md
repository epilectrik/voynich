# PWRE-1: Physical World Reverse Engineering - Phase Summary

**Status:** COMPLETE
**Date:** 2026-01-13
**Tier:** 3 (Exploratory, Non-Binding)

---

## Executive Summary

The Voynich controller architecture **structurally requires** a narrow class of physical processes and **structurally excludes** 12 major process classes.

### What Physics Is REQUIRED

| Requirement | Source |
|-------------|--------|
| Continuous feedback availability | C171 |
| Intervention points during operation | C366 |
| Accessible equilibrium states | C105 |
| Restart/recovery capability | C182 |
| Bidirectional phase transitions | C391 |
| Convergent state-space | C074 |
| Categorizable failure modes | C109 |
| Kernel-mediated hazard access | C107 |
| Controllable hazard exposure | C458 |
| Categorical (not parametric) control | C469 |
| Sparse compatibility structure | C475 |
| Type-based (not identity-based) behavior | C383 |

### What Physics Is EXCLUDED

12 major process classes are structurally incompatible:

1. **One-pass batch** - No feedback loop (C171)
2. **Open-loop scheduled** - No conditional intervention (C171, C366)
3. **Observation-terminated** - No internal convergence (C171, C074)
4. **Irreversible transformations** - No recovery possible (C391)
5. **Non-equilibrating** - No stability anchor (C105, C182)
6. **Quantitative ratio** - No numerical encoding (C383, C469)
7. **Precision measurement** - No parametric precision (C469)
8. **Stored-context** - No inter-layer memory (C384)
9. **Rate-critical** - RATE_MISMATCH too minor (C109)
10. **Energy-dominant** - ENERGY_OVERSHOOT too minor (C109)
11. **Substance-specific** - Type-based, not identity-based (C383)
12. **Continuous degradation** - Categorical, not gradient (C109, C475)

### What Remains

**Circulatory, reversible, categorical, stateless, equilibrium-seeking processes** with phase/composition-dominant hazards:

- Circulatory thermal conditioning
- Volatile extraction/separation
- Circulatory reflux operations

---

## Axis Results

### Axis A: Plant Affordance Matrix

**12 necessary physical affordances** derived from controller constraints. Plants lacking ANY of these cannot be governed by this controller.

| Category | Count | Key Affordances |
|----------|-------|-----------------|
| Feedback | 2 | Observability, Intervention |
| Stability | 2 | Equilibration, Restart |
| Reversibility | 2 | Bidirectional, Convergent |
| Risk | 3 | Categorical, Kernel-mediated, Controllable |
| State | 3 | Categorical, Sparse, Type-based |

### Axis B: Hazard Topology Alignment

Hazard distribution (41% phase, 24% composition, 24% containment, 6% rate, 6% energy) **matches circulatory thermal and extraction/separation** archetypes.

| Archetype | Match |
|-----------|-------|
| Batch thermal | ELIMINATED (energy too dominant expected) |
| Chemical synthesis | ELIMINATED (rate too dominant expected) |
| Mechanical assembly | ELIMINATED (no phase/composition) |
| Biological cultivation | ELIMINATED (rate/phase mismatch) |
| **Circulatory thermal** | COMPATIBLE |
| **Extraction/separation** | COMPATIBLE |

### Axis C: State-Space Hypothesis

Two orthogonal axes track physical state-space:

1. **Material Type (PREFIX)** - 4 classes from 2×2 matrix (mobility × distinctness)
2. **Handling Requirement (MIDDLE)** - ~128 latent dimensions, 95.7% incompatibility

Axes are deliberately **orthogonal** (p = 0.852). This explains:
- Rich registry (1,187 MIDDLEs)
- Sparse legality (4.3% legal pairs)
- **Irrecoverable identity but viable operation**

### Axis D: Process Class Exclusions

**12 major process classes structurally excluded** by Tier 0-2 constraints.

Success criterion (≥3 classes) **exceeded** (12 classes eliminated).

---

## Success Criteria Assessment

| Criterion | Threshold | Result |
|-----------|-----------|--------|
| Process classes excluded | ≥3 | **12 EXCLUDED** |
| Coherent state-space model | Yes | **YES** (two-axis) |
| Narrows physical domain | Yes | **YES** (3 archetypes) |
| Irrecoverability preserved | Yes | **YES** (orthogonal axes) |
| Tier 0-2 constraints violated | 0 | **0** |

**Phase Status: SUCCESS**

---

## Key Findings

### 1. The Controller Implies Specific Physics

This is not arbitrary encoding. The controller's structural constraints **necessarily imply** physical properties of the plant:
- Continuous feedback → observable process
- Time-reversal symmetry → reversible transitions
- Stability anchor → accessible equilibria
- Categorical resolution → discrete operational regimes

### 2. Irrecoverability Is Architectural

Substance identity is irrecoverable because:
- Material type and handling requirement are **orthogonal** (p = 0.852)
- No A-B coupling preserves identity (C384)
- Type-based behavior abstracts identity (C383)

This is a **design feature**, not a decoding barrier.

### 3. The Viable Plant Class Is Narrow

After 12 exclusions, only circulatory/reversible/categorical processes remain. These match the Tier 2 viable process classes (C157, C175, C177).

---

## Epistemic Safety Clause

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

## Files Generated

| File | Purpose | Axis |
|------|---------|------|
| `phase_specification.md` | Pre-registration | - |
| `plant_affordance_matrix.md` | Controller → Physical requirements | A |
| `hazard_topology_alignment.md` | Hazard distribution vs archetypes | B |
| `state_space_hypothesis.md` | Property families, orthogonal axes | C |
| `negative_space_eliminations.md` | Excluded process classes | D |
| `pwre_fit_table_additions.txt` | Tier 3 fits | - |

---

## Connection to Prior Work

This phase validates and extends prior findings:

| Prior Finding | PWRE-1 Extension |
|---------------|-----------------|
| C171: Closed-loop only | → 12 formal exclusions derived |
| C157/C175/C177: 3 viable classes | → Structural basis established |
| Zone-Material Orthogonality | → Explains irrecoverability |
| 95.7% MIDDLE incompatibility | → Sparse compatibility = physical constraints |
| 4-class material structure | → Two-axis state-space model |

---

## Recommended Follow-Up

1. **Test hub MIDDLE correspondence** - Do 'a', 'o', 'e', 'ee', 'eo' appear in recovery/ambient contexts?
2. **Validate incompatibility physics** - Do illegal MIDDLE pairs violate known physical laws?
3. **Map hazard classes to physical failures** - Can PHASE_ORDERING/COMPOSITION_JUMP be matched to known failure modes?
4. **Expert review** - Validate structural reasoning for potential Tier 2 promotion

---

*Phase completed 2026-01-13*
