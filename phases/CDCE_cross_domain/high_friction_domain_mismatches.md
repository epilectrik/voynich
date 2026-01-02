# High-Friction Domain Mismatches

> **PURPOSE**: Document domains that superficially resemble the locked grammar but break under engineering scrutiny.

---

## Mismatch Classification

| Severity | Definition | Count |
|----------|------------|-------|
| HARD INCOMPATIBLE | Violates locked constraints directly | 7 |
| SOFT INCOMPATIBLE | Requires features grammar lacks | 4 |
| SUPERFICIAL MATCH | Looks similar but mechanism differs | 3 |

---

## HARD INCOMPATIBILITIES

### 1. Phase-Change Processes

**Examples**: Crystallization, condensation, evaporation, freezing, sublimation

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Material sensitivity | CLASS_C fails exclusively | Phase change required | **DIRECT** |
| Failure mode | 100% PHASE_COLLAPSE | Phase change is goal | **DIRECT** |
| Hazard class | 7/17 = PHASE_ORDERING | Phase must be ordered | **AMBIGUOUS** |

**Engineering Analysis**:

The grammar treats phase transitions as catastrophic failures. Every simulation with phase-unstable materials (CLASS_C) failed with PHASE_COLLAPSE mode. This is not a tunable parameter—it is a hard constraint.

An engineer would conclude: *"This control system is designed to avoid phase transitions at all costs. Any process requiring phase change cannot use this grammar."*

**Verdict**: **HARD INCOMPATIBLE** (100% certainty)

---

### 2. Open-Flow (Single-Pass) Processes

**Examples**: Column chromatography, flow-through extraction, single-pass filtration, once-through reactors

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Geometry | G1 fails (93.5%) | Open flow only | **DIRECT** |
| LINK effectiveness | 0.20 in G1 vs 1.35 in G5 | No residence return | **DIRECT** |
| Convergence | 6.5% in G1 | Must complete | **DIRECT** |

**Engineering Analysis**:

The LINK operator—38% of execution—maps to physical delay only when material recirculates. In open flow, perturbations propagate downstream without damping. The grammar's stability mechanism has nothing to attach to.

An engineer would conclude: *"This grammar was designed for a system where output returns to input. Any single-pass system would fail to implement the damping logic."*

**Verdict**: **HARD INCOMPATIBLE** (93.5% failure rate)

---

### 3. Batch (Non-Circulating) Processes

**Examples**: Batch fermentation, reaction vessels, holding tanks, batch distillation

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Recirculation | Required (G4/G5) | None (isolated vessel) | **DIRECT** |
| LINK effectiveness | 1.35 in G5 | 0.20 in batch | **DIRECT** |
| Flow topology | Closed loop | Closed vessel | **SEMANTIC** |

**Engineering Analysis**:

Batch vessels lack intrinsic transport delay. The grammar's LINK sequences (up to 7 consecutive) encode waiting for physical relaxation along a flow path. In a static vessel, this has no mechanical meaning.

An engineer would conclude: *"The control logic assumes material moves through a circuit. A batch vessel has no circuit—the grammar would be incoherent."*

**Verdict**: **HARD INCOMPATIBLE** (LINK semantics void)

---

### 4. Endpoint-Defined Recipes

**Examples**: Pharmaceutical synthesis, reaction completion, quality-gated production

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Termination signals | 0 detected | Endpoint required | **DIRECT** |
| Identifier tokens | 0 detected | Product ID required | **DIRECT** |
| Outcome specification | External | Embedded in recipe | **STRUCTURAL** |

**Engineering Analysis**:

The grammar contains zero completion signals. Every program runs indefinitely until externally terminated. No yield markers, no quality checks, no "done" states.

An engineer would conclude: *"There's no way to know when you're finished. This cannot encode any process with a defined end state."*

**Verdict**: **HARD INCOMPATIBLE** (0 endpoint markers)

---

### 5. High-Throughput Production

**Examples**: Continuous manufacturing, yield-optimized extraction, fast-cycle processing

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| LINK density | 38% (waiting) | Minimize dead time | **DIRECT** |
| Program priority | Stability >> speed | Speed >> stability | **INVERSE** |
| AGGRESSIVE programs | 18% (rare) | 80%+ expected | **INVERSE** |

**Engineering Analysis**:

The grammar spends 38% of execution waiting. High-throughput systems minimize wait time. The stability-first design is antithetical to production pressure.

An engineer would conclude: *"Whoever designed this prioritized not failing over getting output. This is a safety-conscious system, not a production system."*

**Verdict**: **HARD INCOMPATIBLE** (design inversion)

---

### 6. Emulsion/Foam Processes

**Examples**: Emulsification, foam formation, micelle creation, dispersion

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Material sensitivity | CLASS_C fails | Emulsion required | **DIRECT** |
| Boundary stability | Required | Unstable boundaries | **DIRECT** |
| Phase separation | Avoided | Desired | **DIRECT** |

**Engineering Analysis**:

Emulsions and foams exist at phase boundaries. The grammar's exclusive failure on CLASS_C materials indicates intrinsic incompatibility with interfacial instability.

An engineer would conclude: *"The control system collapses when material can exist in multiple phases simultaneously. Emulsion processes are structurally excluded."*

**Verdict**: **HARD INCOMPATIBLE** (CLASS_C = only failure)

---

### 7. Rapid Thermal Ramping

**Examples**: Flash heating, thermal shock, rapid quench, high-speed cycling

| Constraint | Grammar Value | Process Requirement | Conflict |
|------------|---------------|---------------------|----------|
| Hazard class | ENERGY_OVERSHOOT (6/17) | High energy rate | **DIRECT** |
| Intervention frequency | 5.9 mean | >>10 required | **INSUFFICIENT** |
| Conservative programs | 77% of library | <<20% expected | **INVERSE** |

**Engineering Analysis**:

ENERGY_OVERSHOOT is a named hazard class. The grammar actively prevents rapid energy input. Fast thermal cycling would trigger the hazard frequently.

An engineer would conclude: *"The system has guards against exactly the behavior rapid ramping requires. You'd be fighting the control logic."*

**Verdict**: **HARD INCOMPATIBLE** (explicit hazard class)

---

## SOFT INCOMPATIBILITIES

### 8. Discrete-Product Recipes

**Examples**: Traditional pharmacy, compounding, specific preparation

| Missing Feature | Implication |
|-----------------|-------------|
| Product identifiers | Cannot specify what to make |
| Quantity signals | Cannot specify how much |
| Ingredient encoding | Cannot specify inputs |

**Engineering Analysis**:

The grammar encodes *operation* without *specification*. It describes how to run a system, not what the system produces.

**Verdict**: **SOFT INCOMPATIBLE** (lacks product encoding)

---

### 9. Yield Measurement Systems

**Examples**: Production monitoring, quality control loops, efficiency tracking

| Missing Feature | Implication |
|-----------------|-------------|
| Output quantification | No yield tracking |
| Efficiency metrics | No throughput measurement |
| Accumulation signals | No cumulative accounting |

**Engineering Analysis**:

No mechanism exists in the grammar to track what has been produced. External measurement is assumed.

**Verdict**: **SOFT INCOMPATIBLE** (no quantification layer)

---

### 10. Automated Feedback Control

**Examples**: PID loops, adaptive control, sensor-driven operation

| Missing Feature | Implication |
|-----------------|-------------|
| Continuous parameters | 83 discrete programs only |
| Sensor integration | Operator judgment assumed |
| Automatic adjustment | Manual selection required |

**Engineering Analysis**:

The grammar offers 83 fixed programs, not continuous tuning. This is fundamentally pre-automation design.

**Verdict**: **SOFT INCOMPATIBLE** (pre-automation architecture)

---

### 11. Multi-Stage Cascaded Processes

**Examples**: Sequential reactors, staged separation, progressive extraction trains

| Missing Feature | Implication |
|-----------------|-------------|
| Stage transitions | All programs monolithic |
| Cascade coordination | No inter-unit signals |
| Sequential handoff | Each folio is atomic |

**Engineering Analysis**:

Each folio is a complete, self-contained program. No inter-folio coordination exists. Cascaded systems require coordination.

**Verdict**: **SOFT INCOMPATIBLE** (atomic program design)

---

## SUPERFICIAL MATCHES

### 12. Medical Recipe Books

**Similarity**: Enumerated procedures, expert use, learning progression

**Mismatch**: Medical recipes have ingredients, quantities, endpoints. Grammar has none.

**Engineering Verdict**: *"Looks like a recipe book structurally but lacks all semantic content of recipes."*

---

### 13. Alchemical Treatises

**Similarity**: Esoteric appearance, process focus, symbolic encoding

**Mismatch**: Alchemical texts describe transformations. Grammar describes steady-state operation.

**Engineering Verdict**: *"Wrong dynamics. Alchemy is endpoint-oriented; this grammar is maintenance-oriented."*

---

### 14. Industrial Control Manuals

**Similarity**: Operator procedures, safety constraints, equipment focus

**Mismatch**: Modern manuals integrate feedback. Grammar is open-loop.

**Engineering Verdict**: *"Right domain, wrong era. This is pre-instrumentation control."*

---

## Mismatch Summary Matrix

| Domain | Primary Conflict | Severity |
|--------|------------------|----------|
| Phase-change processes | CLASS_C failure | HARD |
| Open-flow systems | G1 failure | HARD |
| Batch processes | LINK incoherence | HARD |
| Endpoint recipes | 0 markers | HARD |
| Production systems | Priority inversion | HARD |
| Emulsions | Interface instability | HARD |
| Rapid thermal | ENERGY_OVERSHOOT | HARD |
| Product specification | No encoding | SOFT |
| Yield tracking | No quantification | SOFT |
| Automated control | Discrete programs | SOFT |
| Cascade systems | Atomic folios | SOFT |
| Medical recipes | No semantics | SUPERFICIAL |
| Alchemy | Wrong dynamics | SUPERFICIAL |
| Modern control | Wrong era | SUPERFICIAL |

---

## Negative Space Definition

What remains after exclusion:

> **Compatible Domain**: Closed-loop circulation systems, operating indefinitely without phase change, under expert manual control, prioritizing stability over throughput, without specified products or endpoints.

This describes a remarkably narrow engineering space.

---

*Analysis complete. See `engineer_intuition_summary.md` for synthesis.*
