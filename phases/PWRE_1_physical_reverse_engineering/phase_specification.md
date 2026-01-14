# Phase: PWRE-1 Physical World Reverse Engineering

## Pre-Registration

- **Date:** 2026-01-13
- **Tier:** 3 (Exploratory, Non-Binding)
- **Status:** IN PROGRESS
- **Model Core (Tier 0-2):** FROZEN - No modifications permitted

---

## Purpose

Reverse-engineer the necessary properties of the physical world that could realize the frozen Voynich controller architecture.

**Core Question:**
> What class of physical systems could be governed by this controller - and which classes are structurally impossible?

**Key Principle:**
> You are not decoding a manuscript. You are reverse-engineering the physics implied by a medieval control architecture. Treat the manuscript as the controller, and the physical world as the unknown plant, and reason accordingly.

---

## Background

The internal structural reconstruction of the Voynich Manuscript is **complete at Tier 0-2**:
- 335 validated constraints
- Closed-loop control architecture confirmed (C171)
- 49 instruction classes with 17 forbidden transitions (C109)
- Global type system without semantic content (C383)
- Recovery architecture (C105, C182)
- Design clamp asymmetry (C458)

This phase does NOT investigate the manuscript as text. It investigates the **derived object**: a closed, non-semantic, categorical control architecture that must govern a real physical process ("the plant").

---

## Four Analytical Axes

### AXIS A: Plant Affordance Necessity

**Question:** What minimal physical capabilities must any viable plant possess?

**Controller Constraints → Physical Requirements:**

| Constraint | Controller Feature | Required Physical Affordance |
|------------|-------------------|------------------------------|
| C171 | Closed-loop only | Continuous feedback availability |
| C105 | e = STABILITY_ANCHOR (54.7% recovery paths) | Return/equilibration paths exist |
| C391 | Time-reversal symmetry H(X\|past k) = H(X\|future k) | Phase boundary reversibility |
| C182 | Restart-capable folios = 0.589 stability | Recovery without reset capability |
| C107 | Kernel BOUNDARY_ADJACENT to forbidden | Localized energy ingress risks |
| C109 | 5 hazard classes | Categorizable failure modes |
| C469 | Categorical resolution (73.5% single-folio MIDDLEs) | Categorical, not parametric encoding |
| C458 | Hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) | Controllable hazard exposure; multiple recovery paths |

**Prediction:** Each physical affordance is NECESSARY - plants lacking any one cannot be governed by this controller.

### AXIS B: Hazard Topology Matching

**Question:** Which physical process classes match the observed hazard distribution?

**Hazard Distribution (from C109):**

| Hazard Class | Count | % | Description |
|--------------|-------|---|-------------|
| PHASE_ORDERING | 7 | 41% | Material in wrong phase/location |
| COMPOSITION_JUMP | 4 | 24% | Impure fractions passing |
| CONTAINMENT_TIMING | 4 | 24% | Overflow/pressure events |
| RATE_MISMATCH | 1 | 6% | Flow balance destroyed |
| ENERGY_OVERSHOOT | 1 | 6% | Thermal damage/scorching |

**Additional hazard metrics:**
- 65% asymmetric transitions (C111)
- 59% distant from kernel (C112)
- 71% batch-focused (opportunity-loss), 29% apparatus-focused (C216)

**Task:** Compare against process archetypes (batch thermal, circulatory thermal, chemical synthesis, mechanical assembly, biological cultivation, extraction/separation) WITHOUT naming specific processes.

### AXIS C: State-Space Semantic Reconstruction

**Question:** What abstract property families are being tracked in the ~128 latent dimensions?

**Key Data:**
- C475: 95.7% MIDDLE incompatibility (only 4.3% of pairs legal)
- C469: 73.5% of MIDDLEs appear in only 1 AZC folio
- Zone-Material Orthogonality: p = 0.852 (independent axes)
- 1,187 unique MIDDLEs in 30 connected components
- Hub MIDDLEs: 'a', 'o', 'e', 'ee', 'eo' (universal connectors)

**Questions to Answer:**
1. What physical properties are CATEGORICAL, not scalar?
2. What properties require MUTUAL EXCLUSION?
3. Why must compatibility be so sparse (95.7% illegal)?
4. Why is identity irrecoverable but operation viable?

**Approach:** Group dimensions into property families (diffusivity-like, volatility-like, miscibility-like) WITHOUT identifying specific substances.

### AXIS D: Process Class Exclusion

**Question:** Which large classes of physical processes are structurally impossible?

**Exclusion Tests:**

| Process Class | Test Against | Prediction |
|---------------|--------------|------------|
| One-pass batch processes | C171 (closed-loop only) | EXCLUDED - no feedback |
| Processes requiring explicit ratios | C383 (global type, no quantities) | EXCLUDED - no parametric encoding |
| Processes without steady states | C105 (stability anchor) | EXCLUDED - no equilibration target |
| Fully irreversible transformations | C391 (time-reversal symmetry) | EXCLUDED - no recovery paths |
| Processes requiring stored semantic context | C384 (no A-B coupling) | EXCLUDED - no inter-layer memory |

---

## Required Inputs

| Input | Source | Tier |
|-------|--------|------|
| C171 Closed-loop only | `context/CLAIMS/C171_closed_loop_only.md` | 0 FROZEN |
| C109 5 Hazard Classes | `context/CLAIMS/C109_hazard_classes.md` | 0 FROZEN |
| C105 Stability Anchor | `context/CLAIMS/grammar_system.md` | 2 CLOSED |
| C107 Kernel Boundary-Adjacent | `context/CLAIMS/grammar_system.md` | 2 CLOSED |
| C391 Time-Reversal Symmetry | `context/CLAIMS/morphology.md` | 2 CLOSED |
| C182 Restart Stability | `context/CLAIMS/operations.md` | 2 CLOSED |
| C458 Design Clamp | `context/CLAIMS/C458_execution_design_clamp.md` | 2 CLOSED |
| C475 MIDDLE Incompatibility | `context/CLAIMS/currier_a.md` | 2 CLOSED |
| C469 Categorical Resolution | `context/CLAIMS/azc_system.md` | 2 CLOSED |
| C383 Global Type System | `context/CLAIMS/C383_global_type_system.md` | 2 CLOSED |
| C384 No A-B Coupling | `context/CLAIMS/C384_no_entry_coupling.md` | 2 CLOSED |
| C490 Categorical Strategy Exclusion | `context/CLAIMS/C490_categorical_strategy_exclusion.md` | 2 CLOSED |
| C492 PREFIX Phase Exclusivity | `context/CLAIMS/C492_prefix_phase_exclusion.md` | 2 CLOSED |
| ECR stress tests | `context/MODEL_FITS/ecr_stress_tests.md` | F3 |
| Zone-Material Orthogonality | `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` (I.M) | 3 |
| Two-Axis HT model | `context/SPECULATIVE/ht_two_axis_model.md` | 2-3 |
| Hazard distribution | `context/MODEL_FITS/fits_global.md` (F-ECR-001) | F3 |

---

## Epistemic Safeguards

### MUST NOT
- Assign meanings to tokens
- Identify substances, plants, minerals, or recipes
- Map components to apparatus parts ("k = furnace", etc.)
- Claim apparatus schematics or literal diagrams
- Propose new grammar, morphology, or token roles
- Modify or reinterpret Tier 0-2 constraints

### MAY
- Treat the Voynich system as a fully specified controller
- Treat the physical process as an unknown plant
- Use physics, chemistry, and control theory as constraint spaces
- Perform exclusion, necessity, and affordance analyses
- Propose state-space semantics (not entity semantics)

---

## Deliverables

| File | Purpose | Axis |
|------|---------|------|
| `plant_affordance_matrix.md` | Controller → Physical requirement mapping | A |
| `hazard_topology_alignment.md` | Hazard distributions vs process archetypes | B |
| `state_space_hypothesis.md` | Abstract property families, categorical encoding | C |
| `negative_space_eliminations.md` | Excluded plant classes | D |
| `PWRE_1_PHASE_SUMMARY.md` | Executive summary | - |
| `pwre_fit_table_additions.txt` | Fits documenting compatibility/exclusion | - |

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Process classes structurally excluded | >= 3 large classes |
| Coherent state-space model | Emerges without naming substances |
| Narrows plausible physical domain | Yes |
| Irrecoverability preserved | Not collapsed |
| Tier 0-2 constraints violated | 0 |

---

## Mandatory Epistemic Safety Clause

All outputs MUST include:

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

*Phase pre-registered 2026-01-13*
