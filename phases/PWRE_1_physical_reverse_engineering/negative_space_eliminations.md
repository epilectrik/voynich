# AXIS D: Process Class Exclusions (Negative Space)

**Goal:** Use the controller to eliminate large classes of physical processes.

**Principle:** Each exclusion STRENGTHENS the remaining hypothesis space. Structural reasons only.

---

## Executive Summary

The controller architecture **structurally excludes** 12 major classes of physical processes. Each exclusion is derived from Tier 0-2 constraints via logical necessity.

| Category | Excluded Classes | Primary Constraint |
|----------|-----------------|-------------------|
| Feedback | 3 | C171 |
| Reversibility | 2 | C391 |
| Quantification | 2 | C383, C469 |
| Memory | 1 | C384 |
| Stability | 2 | C105, C182 |
| Hazard Topology | 2 | C109 |

---

## Exclusion 1: One-Pass Batch Processes

**Constraint:** C171 (Closed-loop only)

**Controller Feature:**
> "Of all purpose classes tested, only continuous closed-loop process control is structurally compatible."

**Exclusion Logic:**
One-pass batch processes:
- Have no feedback loop (run to completion without adjustment)
- Cannot be interrupted and restarted
- Have no "in-process" state monitoring

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Single-batch cooking (no mid-course correction)
- One-shot reactions (reagent + catalyst → product)
- Linear manufacturing (A→B→C without branching)

---

## Exclusion 2: Open-Loop Scheduled Processes

**Constraint:** C171 (Closed-loop only), C366 (LINK = monitoring-intervention)

**Controller Feature:**
- 38% LINK density indicates continuous monitoring
- Grammar requires feedback-dependent branching

**Exclusion Logic:**
Open-loop scheduled processes:
- Follow a preset timeline
- Do not adjust based on observation
- Have no conditional intervention points

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Timer-based processes (bake for 30 minutes regardless)
- Scheduled additions (add X at time T regardless of state)
- Fixed-sequence protocols

---

## Exclusion 3: Observation-Terminated Processes

**Constraint:** C171 (Closed-loop only), C074 (Dominant convergence)

**Controller Feature:**
- Programs converge to STATE-C through operational steps
- Convergence is process-internal, not observation-terminated

**Exclusion Logic:**
Observation-terminated processes:
- Operate until an external criterion is met
- Do not have internal convergence structure
- "Watch until done" ≠ "operate to convergence"

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Observation-based termination ("heat until color changes")
- Threshold detection processes
- Endpoint titration (stop when indicator changes)

---

## Exclusion 4: Irreversible Transformations

**Constraint:** C391 (Time-reversal symmetry)

**Controller Feature:**
> "H(X|past k) = H(X|future k). Bidirectional adjacency constraints."

**Exclusion Logic:**
Irreversible transformations:
- Cannot be undone once initiated
- Have no backward-compatible grammar
- Recovery is impossible by definition

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Combustion (cannot un-burn)
- Polymerization/curing (cannot un-set)
- Precipitation with no redissolution
- Evaporation with no condensation

---

## Exclusion 5: Non-Equilibrating Transformations

**Constraint:** C105 (e = STABILITY_ANCHOR), C182 (Restart capability)

**Controller Feature:**
- 54.7% of recovery paths pass through stability anchor 'e'
- Restart-capable folios show 50% higher stability

**Exclusion Logic:**
Non-equilibrating transformations:
- Have no stable intermediate states
- Cannot park at equilibrium during recovery
- All-or-nothing outcome with no partial states

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Runaway reactions (no equilibrium point)
- Threshold-triggered events (explosive, cascade)
- Chaotic systems with no attractors

---

## Exclusion 6: Quantitative Ratio Processes

**Constraint:** C383 (Global type system), C469 (Categorical resolution)

**Controller Feature:**
- Type system has no quantity encoding
- Resolution is categorical (vocabulary presence/absence), not parametric
- 73.5% of MIDDLEs appear in only 1 AZC folio

**Exclusion Logic:**
Quantitative ratio processes:
- Require specific numerical proportions (3:1, 2:1, etc.)
- Depend on measured amounts
- Cannot be encoded categorically

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Stoichiometric reactions (exact reagent ratios)
- Alloy preparation (precise metal percentages)
- Dilution protocols (specific concentration targets)

---

## Exclusion 7: Precision Measurement Processes

**Constraint:** C469 (Categorical resolution), C383 (Global type system)

**Controller Feature:**
- Operational conditions represented categorically
- No numerical encoding in grammar
- Token legality is binary (legal/illegal)

**Exclusion Logic:**
Precision measurement processes:
- Require exact numerical values
- Cannot function with categorical approximations
- "Hot" vs "very hot" is insufficient precision

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Laboratory synthesis (exact temperatures)
- Metallurgical processes (precise temperature control)
- Calibration procedures

---

## Exclusion 8: Stored-Context Processes

**Constraint:** C384 (No A-B coupling)

**Controller Feature:**
> "No entry-level semantic connection between A and B."

**Exclusion Logic:**
Stored-context processes:
- Require remembering previous steps
- Reference earlier decisions later
- Need inter-layer memory

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Multi-stage recipes with back-references
- Conditional sequences based on prior outcomes
- Processes requiring "what we did in step 3"

---

## Exclusion 9: Rate-Critical Processes

**Constraint:** C109 (Hazard distribution: RATE_MISMATCH = 6%)

**Controller Feature:**
- Rate mismatch is only 6% of hazards
- Dominant concerns are phase ordering (41%) and composition (24%)

**Exclusion Logic:**
Rate-critical processes:
- Would show RATE_MISMATCH as dominant hazard
- Controller is optimized for phase/composition, not rate
- Rate-controlled processes excluded by hazard profile

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Flow-rate-dependent reactions
- Kinetically-controlled synthesis
- Diffusion-limited processes

---

## Exclusion 10: Energy-Dominant Processes

**Constraint:** C109 (Hazard distribution: ENERGY_OVERSHOOT = 6%)

**Controller Feature:**
- Energy overshoot is only 6% of hazards
- Thermal damage is minor concern

**Exclusion Logic:**
Energy-dominant processes:
- Would show ENERGY_OVERSHOOT as dominant hazard
- Controller is not optimized for thermal protection
- High-heat processes excluded by hazard profile

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- High-temperature metallurgy
- Direct-fire calcination
- Scorching/charring-sensitive processes

---

## Exclusion 11: Substance-Specific Processes

**Constraint:** C383 (Global type system: type determines behavior)

**Controller Feature:**
- Behavior is determined by TYPE (M-A, M-B, M-C, M-D)
- Same type = same handling, regardless of identity
- No individual substance discrimination

**Exclusion Logic:**
Substance-specific processes:
- Require different handling for same-type materials
- "This M-A but not that M-A"
- Individual identity matters

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Species-specific herbal preparations
- Mineral-specific treatments
- Processes where identity ≠ type

---

## Exclusion 12: Continuous Degradation Processes

**Constraint:** C109 (5 discrete hazard classes), C475 (Binary compatibility)

**Controller Feature:**
- Hazards are CATEGORICAL (5 classes)
- Compatibility is BINARY (legal/illegal)
- No gradient encoding

**Exclusion Logic:**
Continuous degradation processes:
- Fail gradually, not categorically
- "Slightly contaminated" ≠ "contaminated"
- Require gradient quality assessment

**Verdict: STRUCTURALLY EXCLUDED**

**Examples of excluded processes:**
- Quality decay monitoring
- Gradual degradation tracking
- Processes with analog failure modes

---

## Consolidated Exclusion Table

| # | Process Class | Excluding Constraint | Reason |
|---|---------------|---------------------|--------|
| 1 | One-pass batch | C171 | No feedback loop |
| 2 | Open-loop scheduled | C171, C366 | No conditional intervention |
| 3 | Observation-terminated | C171, C074 | No internal convergence |
| 4 | Irreversible transformations | C391 | No recovery possible |
| 5 | Non-equilibrating | C105, C182 | No stability anchor |
| 6 | Quantitative ratio | C383, C469 | No numerical encoding |
| 7 | Precision measurement | C469, C383 | No parametric precision |
| 8 | Stored-context | C384 | No inter-layer memory |
| 9 | Rate-critical | C109 | RATE_MISMATCH too minor |
| 10 | Energy-dominant | C109 | ENERGY_OVERSHOOT too minor |
| 11 | Substance-specific | C383 | Type-based, not identity-based |
| 12 | Continuous degradation | C109, C475 | Categorical, not gradient |

---

## What Remains

After 12 exclusions, the remaining viable plant classes are:

| Property | Requirement |
|----------|-------------|
| Feedback | Continuous, closed-loop |
| Reversibility | Bidirectional phase transitions |
| Quantification | Categorical, not parametric |
| Memory | Stateless (no inter-layer memory) |
| Stability | Accessible equilibria for recovery |
| Hazard profile | Phase/composition dominant |
| Behavior mode | Type-based handling |

**Compatible process archetypes:**
1. Circulatory thermal conditioning
2. Volatile extraction/separation
3. Circulatory reflux operations

These match the Tier 2 viable process classes identified in C171, C157, C175, C177.

---

## Epistemic Power of Exclusions

Each exclusion narrows the hypothesis space:

| Exclusion Count | Remaining Space |
|-----------------|-----------------|
| 0 | All physical processes |
| 3 (feedback) | Continuous processes only |
| 5 (+reversibility) | Equilibrium-seeking only |
| 7 (+quantification) | Categorical control only |
| 8 (+memory) | Stateless only |
| 10 (+stability) | Stable-equilibrium only |
| 12 (+hazard) | Phase/composition-focused only |

**Result:** A highly constrained class of circulatory, reversible, categorical, stateless, equilibrium-seeking processes.

---

## Epistemic Status

All exclusions are derived from Tier 0-2 constraints via logical necessity. Each represents a SUFFICIENT condition for exclusion — any process exhibiting the excluded property CANNOT be governed by this controller.

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

## Data Sources

| Constraint | Source File |
|------------|-------------|
| C171 | `context/CLAIMS/C171_closed_loop_only.md` |
| C391 | `context/CLAIMS/morphology.md` |
| C105 | `context/CLAIMS/grammar_system.md` |
| C182 | `context/CLAIMS/operations.md` |
| C383 | `context/CLAIMS/C383_global_type_system.md` |
| C384 | `context/CLAIMS/C384_no_entry_coupling.md` |
| C469 | `context/CLAIMS/azc_system.md` |
| C109 | `context/CLAIMS/C109_hazard_classes.md` |
| C366 | `context/CLAIMS/morphology.md` |
| C074 | `context/CLAIMS/C074_dominant_convergence.md` |
| C475 | `context/CLAIMS/currier_a.md` |
