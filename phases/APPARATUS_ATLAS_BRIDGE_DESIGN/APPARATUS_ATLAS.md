# Apparatus Atlas

**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**

## Executive Summary

This atlas maps the abstract apparatus response manifold (5.88 effective dimensions, 76 folios) to physical control surfaces and observable configurations. The bridge is NOT instruction-to-action translation but rather:

> **Manifold position / closure morphology / process metric regime -> physical knob setting / observable response family**

All physical mappings are Tier 3-4 interpretation. Structural evidence underlying them is Tier 0-2.

## F-Axis to Physical Knob Mapping (Core)

| Axis | Name | Physical Knob Candidates | Knob Class | Tier |
|------|------|-------------------------|------------|------|
| F1 | Attractor / Forgiveness | Reflux ratio (condensate return vs collection); Recirculation tightness (return path diameter); Condensate return fraction | geometry | 3 |
| F2 | Closure Exploitability | Valve timing precision (stop/start sharpness); Seal completion speed; Collection diversion response time | performance | 3 |
| F3 | Thermal Accent | Bath temperature setpoint; Heater power slew rate; Heat transfer coefficient (medium: water vs sand vs direct) | geometry | 3 |
| F4_raw | Headless Infrastructure | Plumbing complexity (number of passive paths); Passive recirculation paths (side arms, auxiliary condensers); Condensate routing topology (valves, tees) | geometry | 4 |
| F5 | Containment Responsiveness | Gasket quality (ground glass vs wax vs PTFE); Seal completeness (number of sealed joints); Backpressure tolerance | performance | 3 |

### Knob Classification

- **geometry**: Moves you in Space A (apparatus configuration). Changing these changes what the apparatus IS.
- **performance**: Changes Space B outcomes (process quality). Changing these changes what the apparatus DOES.
- **readout**: Changes only observability, not behavior. Changing these changes what you can SEE.

## PC-to-Knob Cluster Mapping

| PC | Variance | Top Feature | Loading | Physical Cluster |
|----|----------|-------------|---------|-----------------|
| PC1 | 30.0% | abl_CLOSE_RECOVERY | +0.4450 | Ablation channel: abl_CLOSE_RECOVERY |
| PC2 | 17.2% | abl_CROSS_COUPLING | +0.4768 | Ablation channel: abl_CROSS_COUPLING |
| PC3 | 13.4% | abl_Y_SENSITIVITY | -0.5173 | Ablation channel: abl_Y_SENSITIVITY |
| PC4 | 13.1% | F4_raw | -0.7166 | Plumbing complexity (number of passive paths) |
| PC5 | 8.6% | F2 | +0.8562 | Valve timing precision (stop/start sharpness) |

## Family Analog Definitions

### A1_BATH_REFLUX

**Physical analog:** Moderated bath/reflux with open or loosely sealed head

**Dominant knob axis:** F1 (low attractor strength)

**CCS1 typical:** 0.013

**Key differentiators:**

- Sensitive to operator precision (low self-correction)
- Water bath provides thermal buffer but not error correction
- Open head allows vapor escape (no pressure feedback)
- Requires careful fire management

### A2_SEALED_RECIRCULATION

**Physical analog:** Sealed forgiving recirculation with tight joints

**Dominant knob axis:** F5 (high containment responsiveness)

**CCS1 typical:** 0.114

**Key differentiators:**

- Self-correcting via close-recovery (R1_C/R4_C channels)
- Sealed system creates pressure feedback loop
- Overheat -> increased vapor pressure -> faster condensation -> self-correction
- Strength-dependent: STRONG closures productive, WEAK closures lose to null (C1642)

### A3_DISTILL_COLLECT

**Physical analog:** Distill-collect bridge, intermediate configuration

**Dominant knob axis:** F2 (intermediate closure exploitability)

**CCS1 typical:** 0.053

**Key differentiators:**

- Spans A1-A2 geometry (54% are bridge folios)
- Standard collection operations with partial seal
- Intermediate self-correction capability
- Most common family (37/76 folios)

## Landscape Class Physical Interpretations

| Class | Name | Physical Regime | Observable Behavior |
|-------|------|----------------|-------------------|
| SA | Stable Attractor | Self-sustaining equilibrium operation | Minimal intervention needed, consistent output |
| TD | Transition Domain | Threshold-dependent behavior | Small perturbations can tip into different operating modes |
| FR | Forgiving Region | Error-tolerant recirculation | Apparatus self-corrects moderate operator errors |

## Per-Folio Apparatus Assignment

Total folios: 76

| Folio | Family | Landscape | Section |
|-------|--------|-----------|---------|
| f103r | A3 | THRESHOLD_DEPENDENT | S |
| f103v | A3 | THRESHOLD_DEPENDENT | S |
| f104r | A3 | THRESHOLD_DEPENDENT | S |
| f104v | A3 | THRESHOLD_DEPENDENT | S |
| f105r | A3 | STABLE_AMPLIFIER | S |
| f105v | A3 | STABLE_AMPLIFIER | S |
| f106r | A3 | THRESHOLD_DEPENDENT | S |
| f106v | A3 | THRESHOLD_DEPENDENT | S |
| f107r | A3 | STABLE_AMPLIFIER | S |
| f107v | A3 | THRESHOLD_DEPENDENT | S |
| f108r | A3 | THRESHOLD_DEPENDENT | S |
| f108v | A3 | THRESHOLD_DEPENDENT | S |
| f111r | A3 | STABLE_AMPLIFIER | S |
| f111v | A3 | THRESHOLD_DEPENDENT | S |
| f112r | A3 | THRESHOLD_DEPENDENT | S |
| f112v | A3 | THRESHOLD_DEPENDENT | S |
| f113r | A3 | THRESHOLD_DEPENDENT | S |
| f113v | A3 | STABLE_AMPLIFIER | S |
| f114r | A3 | THRESHOLD_DEPENDENT | S |
| f114v | A3 | THRESHOLD_DEPENDENT | S |
| f115r | A3 | THRESHOLD_DEPENDENT | S |
| f115v | A3 | THRESHOLD_DEPENDENT | S |
| f116r | A3 | THRESHOLD_DEPENDENT | S |
| f26r | A3 | STABLE_AMPLIFIER | H |
| f26v | A3 | THRESHOLD_DEPENDENT | H |
| f31r | A1 | STABLE_AMPLIFIER | H |
| f31v | A3 | STABLE_AMPLIFIER | H |
| f33r | A2 | THRESHOLD_DEPENDENT | H |
| f33v | A2 | STABLE_AMPLIFIER | H |
| f34r | A3 | THRESHOLD_DEPENDENT | H |
| f34v | A3 | STABLE_AMPLIFIER | H |
| f39r | A3 | STABLE_AMPLIFIER | H |
| f39v | A2 | FORGIVING_RECIRCULATOR | H |
| f40r | A2 | FORGIVING_RECIRCULATOR | H |
| f41r | A3 | STABLE_AMPLIFIER | H |
| f41v | A3 | THRESHOLD_DEPENDENT | H |
| f43v | A3 | THRESHOLD_DEPENDENT | H |
| f46r | A3 | STABLE_AMPLIFIER | H |
| f46v | A3 | FORGIVING_RECIRCULATOR | H |
| f48r | A3 | THRESHOLD_DEPENDENT | H |
| f48v | A3 | THRESHOLD_DEPENDENT | H |
| f50r | A2 | THRESHOLD_DEPENDENT | H |
| f50v | A2 | FORGIVING_RECIRCULATOR | H |
| f55r | A2 | THRESHOLD_DEPENDENT | H |
| f55v | A2 | FORGIVING_RECIRCULATOR | H |
| f66r | A2 | THRESHOLD_DEPENDENT | T |
| f75r | A1 | THRESHOLD_DEPENDENT | B |
| f75v | A1 | THRESHOLD_DEPENDENT | B |
| f76r | A1 | THRESHOLD_DEPENDENT | B |
| f76v | A1 | THRESHOLD_DEPENDENT | B |
| f77r | A1 | STABLE_AMPLIFIER | B |
| f77v | A1 | STABLE_AMPLIFIER | B |
| f78r | A1 | THRESHOLD_DEPENDENT | B |
| f78v | A1 | STABLE_AMPLIFIER | B |
| f79r | A1 | THRESHOLD_DEPENDENT | B |
| f79v | A1 | STABLE_AMPLIFIER | B |
| f80r | A1 | THRESHOLD_DEPENDENT | B |
| f80v | A1 | THRESHOLD_DEPENDENT | B |
| f81r | A1 | THRESHOLD_DEPENDENT | B |
| f82r | A1 | THRESHOLD_DEPENDENT | B |
| f82v | A1 | THRESHOLD_DEPENDENT | B |
| f83r | A1 | STABLE_AMPLIFIER | B |
| f83v | A1 | THRESHOLD_DEPENDENT | B |
| f84r | A1 | THRESHOLD_DEPENDENT | B |
| f84v | A1 | THRESHOLD_DEPENDENT | B |
| f85r1 | A2 | THRESHOLD_DEPENDENT | T |
| f85r2 | A2 | FORGIVING_RECIRCULATOR | C |
| f86v3 | A2 | THRESHOLD_DEPENDENT | C |
| f86v4 | A2 | THRESHOLD_DEPENDENT | C |
| f86v5 | A2 | FORGIVING_RECIRCULATOR | C |
| f86v6 | A2 | FORGIVING_RECIRCULATOR | C |
| f94r | A2 | THRESHOLD_DEPENDENT | H |
| f94v | A3 | STABLE_AMPLIFIER | H |
| f95r1 | A1 | THRESHOLD_DEPENDENT | H |
| f95r2 | A2 | FORGIVING_RECIRCULATOR | H |
| f95v2 | A2 | THRESHOLD_DEPENDENT | H |

## Equipment Specification (3 Levels)

### Level 1: MVP (~$560)

**Purpose:** Validate process-quality behavior. Map forgivingness / closure thresholds. Test productive disruption. Compute DVA_phys/YGA_phys/DYE_phys.

**Build time:** Buildable in a week with existing/readily available equipment

**Family coverage:** A1, A3

### Level 2: Recirculatory (~$735)

**Purpose:** Reproduce A1/A2/A3 family geometry. Test F1-F5 knob mappings. Closure threshold mapping under recirculation. Counterfeit closure testing.

**Build time:** Add to Level 1; requires glass connectors and variable-path plumbing

**Family coverage:** A1, A2, A3

### Level 3: Pelican (~$1235)

**Purpose:** Historical-physical convergence. Not required for initial validation. Provides closest match to manuscript iconography.

**Build time:** Commissioned or custom glass; weeks to months for fabrication

**Family coverage:** A1, A2, A3

### Common Monitoring Equipment

- K-type thermocouple (body) (REQUIRED) -- Body temperature measurement
- K-type thermocouple (head) (REQUIRED) -- Head temperature measurement
- K-type thermocouple (bath/source) (optional) -- Heat source monitoring
- K-type thermocouple (collection) (optional) -- Collection point temperature
- Thermocouple reader/logger (4-channel) (REQUIRED) -- Temperature logging
- FLIR thermal camera (optional) -- Body-head gradient, gradient collapse timing
- Digital scale (0.1g resolution) (REQUIRED) -- Condensate mass measurement
- Timer / event logger (REQUIRED) -- Event annotation timestamps
- Notebook + annotation protocol (REQUIRED) -- Manual event logging

---

*All physical mappings are Tier 3-4 interpretation. See constraint provenance for structural evidence tiers.*
