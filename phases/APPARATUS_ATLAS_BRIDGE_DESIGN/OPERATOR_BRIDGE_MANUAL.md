# Operator Bridge Manual

**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**

> **IMPORTANT:** This document is a SECONDARY HEURISTIC LAYER. The primary bridge is the manifold-to-knob mapping (APPARATUS_ATLAS.md). These interpretations are convenient operator-facing summaries, NOT the load-bearing structural bridge.

## Line-Level Control Cycle (Heuristic)

| Zone | Quintile | Physical Heuristic |
|------|----------|-------------------|
| SPEC | Q0 | Read apparatus state. Check temperatures, flow, seal integrity. Assess before acting. |
| WORK | Q1-Q3 | Execute thermal operation. Q1 = apply energy. Q2-Q3 = sustain and monitor. |
| CLOSURE | Q4 | End operation step. Arrest process, secure product, verify completion. |

## Macro-State to Operator Mode (Heuristic)

| Macro-State | Operator Mode | Physical Action |
|-------------|---------------|----------------|
| AXM | Maintain current state, routine monitoring | No changes needed. Monitor temperatures and flow. Apparatus ... |
| AXm | Adjust parameters, change settings | Modify a single control variable: temperature setpoint, valv... |
| CC | Initiate or terminate an operation | Major state change: light/extinguish fire, seal/unseal vesse... |
| FL_HAZ | Material in risky state -- immediate attention | Active hazard condition: bumping, overheating, unexpected bo... |
| FL_SAFE | Operation winding down safely | Process completing naturally. Monitor but do not intervene. ... |
| FQ | Repeat or exit a control loop | Decision point: is product quality sufficient? Repeat batch,... |

## REGIME to Fire Degree (Heuristic)

| REGIME | Brunschwig Degree | CEI | Setup |
|--------|-------------------|-----|-------|
| R2 | Second (warm) | 0.367 | Attenuated heat, collection-focused |
| R1 | First (balneum) | 0.51 | Water bath, sustained gentle heat |
| R4 | Fourth (precision) | 0.584 | Precision-controlled, narrow tolerance |
| R3 | Third (seething) | 0.717 | Direct heat, open-cycle batch |

## Section to Apparatus Style (Modulation Only)

- **Section B:** Distillation-biased -- Section B folios predominantly describe water-bath distillation operations with gentle sustained heat.
- **Section H:** Apparatus-diverse -- Section H folios cover the broadest range of apparatus configurations and operating modes.
- **Section S:** Output-distributed -- Section S folios emphasize product collection and output management.

## Softened Semantic Labels

### a_HEAD

- **Old label:** yield
- **Corrected label:** Active transformation / primary hazard-bearing operational domain
- **Reason:** Expert correction: a-HEAD marks the domain where active transformation occurs, not where yield is produced. It is hazard-bearing because active transformation is where things can go wrong.

### paragraph

- **Old label:** one complete run
- **Corrected label:** Self-contained operational subroutine or batch-emphasis packet
- **Reason:** Expert correction: paragraphs are self-contained operational units, not necessarily complete runs. A folio may contain multiple subroutines.

### terminal_y

- **Old label:** END (pseudo-translation)
- **Corrected label:** Operation step self-containment marker
- **Reason:** Terminal -y marks operational self-containment of the step, not a literal END command.

## Safety Architecture (Three Levels)

### level_1_construction_exclusion

**Structural mechanism:** ch/sh-initial compounds absent (5,821:0)

**Physical protocol:** Verify apparatus CAN physically perform instruction before executing. If a construction is absent from the grammar, the physical analog is a configuration that cannot exist in the apparatus design.

**Constraint basis:** C929 (ch/sh absence), C1298-C1299

### level_2_hazard_source_typing

**Structural mechanism:** k-HEAD complete immunity (0/16,819 hazard frames)

**Physical protocol:** Pure thermal adjustment (applying or reducing heat) is intrinsically safe. The hazard arises downstream -- from what happens to material after heat is applied. Monitor downstream consequences, not the heat source itself.

**Constraint basis:** C1446 (k complete hazard immunity), C1464 (k-IMMUNE)

### level_3_transition_prohibition

**Structural mechanism:** 17 forbidden transitions, 5 hazard classes

**Physical protocol:** Interpose verification between different hazard domains. Never transition directly from one hazard class to another without checking apparatus state.

**Constraint basis:** C109 (17 forbidden transitions), C216 (5 hazard classes), C789 (71/29 batch/apparatus hazard split)

## Five Hazard Classes

| Class | Fraction | Physical Failure | Prevention |
|-------|----------|-----------------|------------|
| PHASE_ORDERING | 41% | Wrong phase state for operation | Verify material phase before each operation. Do no... |
| CONTAINMENT_TIMING | 24% | Seals adjusted at wrong moment | Never adjust seals during active phase transitions... |
| COMPOSITION_JUMP | 24% | Discontinuous composition change | Monitor condensate quality continuously. Do not mi... |
| EQUIPMENT_OVERCOMMIT | 6% | Intensity exceeds apparatus capability | Match fire degree to configuration. Do not apply t... |
| RECYCLE_CONTAMINATION | 6% | Impure condensate returned to body | Verify condensate quality before recirculation. In... |

## Operator Judgment Boundaries

> The system deliberately does not encode all sensory gating. This prevents over-automation drift -- the operator remains essential for quality-critical decisions that require human sensory assessment.

### Encodable / Automatable

- Heater cuts (on/off at specified temperatures)
- Dwell timing windows (hold for N seconds/minutes)
- Seal-state logging (open/closed events)
- Temperature thresholds (act when T > X)
- Event annotation (packet start/end timestamps)
- Closure packet execution (follow specified sequence)

### Non-Encodable / Operator-Judged

- Smell / fraction quality assessment
- Visual condensate quality (clarity, color, turbidity)
- Leak character assessment (is this a problem?)
- When "enough" has been reached (batch completeness)
- Whether behavior is acceptable vs salvage-worthy
- Material readiness for next phase
- Sensory evaluation of product quality
- Anomaly recognition (something unexpected happening)
- Environmental conditions affecting operation
- Equipment wear and fatigue assessment
- Sound assessment (boiling character, hissing, bumping)
- Tactile assessment (vessel temperature by touch proximity)
- Timing judgment (pace of operation, rhythm)

---

*All interpretations in this document are Tier 3 heuristics unless otherwise noted. Safety protocols derive from Tier 2 constraints.*
