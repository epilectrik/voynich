# Negative Process Matches
> **SCOPE**: Process classes that are INCONSISTENT with the grammar constraints.

## Strongly Incompatible Process Classes

### PHASE_CHANGE_PROCESSES
**Incompatibility**: STRONG

**Why it fails**: Grammar explicitly avoids phase transitions. No reset-from-phase-change available.

**Evidence**:
- CLASS_C (phase-unstable) = only failing material class
- 480/480 CLASS_C failures = PHASE_COLLAPSE mode
- 17 forbidden transitions include phase-ordering violations

**Examples excluded**: Crystallization, condensation, evaporation, freezing

---

### ONE_PASS_EXTRACTION
**Incompatibility**: STRONG

**Why it fails**: Open flow cannot satisfy LINK operator physics. Perturbations propagate unchecked.

**Evidence**:
- G1 (linear open flow) = 93.5% failure rate
- Grammar requires recirculation for stability
- No endpoint signals = incompatible with single-pass logic

**Examples excluded**: Column chromatography, single-pass filtration, flow-through extraction

---

### ENDPOINT_DEFINED_RECIPES
**Incompatibility**: STRONG

**Why it fails**: Grammar encodes indefinite operation, not termination conditions.

**Evidence**:
- 0 identifier tokens in grammar
- 0 translation-eligible zones
- No completion signals detected

**Examples excluded**: Batch synthesis, reaction completion, titer testing

---

### HIGH_YIELD_BATCH
**Incompatibility**: STRONG

**Why it fails**: Batch operation lacks circulation feedback. LINK maps to nothing.

**Evidence**:
- G2 batch vessel = 20% LINK effectiveness (vs 135% for G5)
- Batch lacks intrinsic transport delay
- Conservation-focused grammar incompatible with draw-off

**Examples excluded**: Batch fermentation, reaction vessels, holding tanks

---

### EMULSION_PROCESSES
**Incompatibility**: STRONG

**Why it fails**: Phase instability at boundaries defeats control logic.

**Evidence**:
- CLASS_C = emulsion-forming materials = 19.8% failure
- Failure mode = PHASE_COLLAPSE exclusively
- Boundary_sharpness 0.2 = lowest of failing class

**Examples excluded**: Emulsification, foam formation, micelle creation

---

## Moderately Incompatible Process Classes

### RAPID_THERMAL_RAMPING
**Incompatibility**: MODERATE

**Why it fails**: Grammar prioritizes stability over speed. Rapid ramps trigger hazards.

**Evidence**:
- ENERGY_OVERSHOOT = hazard class (6/17 forbidden transitions)
- Kernel k (energy modulator) is most central
- High intervention frequency programs still rare (11/83)

**Examples excluded**: Flash heating, rapid quench, thermal shock protocols

---

### DISCRETE_PRODUCT_RECIPES
**Incompatibility**: MODERATE

**Why it fails**: Grammar describes operation, not product creation.

**Evidence**:
- Programs are continuous state maintenance, not production
- No batch-start or batch-end patterns detected
- 9.8x compression = highly regular cycling, not discrete steps

**Examples excluded**: Pharmaceutical synthesis, defined-product protocols

---

## Negative Match Summary
| Process Class | Incompatibility | Primary Reason |
|---------------|-----------------|----------------|
| PHASE_CHANGE_PROCESSES | STRONG | Grammar explicitly avoids phase transitions. No reset-from-p... |
| ONE_PASS_EXTRACTION | STRONG | Open flow cannot satisfy LINK operator physics. Perturbation... |
| ENDPOINT_DEFINED_RECIPES | STRONG | Grammar encodes indefinite operation, not termination condit... |
| HIGH_YIELD_BATCH | STRONG | Batch operation lacks circulation feedback. LINK maps to not... |
| RAPID_THERMAL_RAMPING | MODERATE | Grammar prioritizes stability over speed. Rapid ramps trigge... |
| EMULSION_PROCESSES | STRONG | Phase instability at boundaries defeats control logic. |
| DISCRETE_PRODUCT_RECIPES | MODERATE | Grammar describes operation, not product creation. |

## Discriminative Power of Negatives
The negative matches collectively rule out:
- All batch processes (no circulation feedback)
- All endpoint-defined recipes (no termination signals)
- All phase-transition processes (explicit hazard class)
- All single-pass operations (geometry incompatibility)
- All rapid-change protocols (stability priority)

This leaves a relatively narrow space of:
- **Closed-loop circulation processes**
- **Continuous indefinite operation**
- **Gradual cumulative change OR maintenance**
- **Phase-stable substrates only**
