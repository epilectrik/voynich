# Sensory Affordance Mapping

**Tier:** 3-4 | **Status:** THEORETICAL FRAMEWORK | **Date:** 2026-01-12

---

## Critical Epistemic Constraint (No-Claim Contract)

> **This framework does not assert that Voynich grammar specifies sensory modalities.**
>
> **It enumerates which sensory modalities must be PRESUPPOSED for the human operator in order for the control architecture to function as observed.**

Sensory channels are:
- **Externally supplied perceptual capacities** necessary to resolve discrimination problems
- **NOT information explicitly specified by the text**

The grammar **RELIES ON** these capacities. It does **NOT ENCODE** them.

---

## Research Question

> Which sensory modalities must be available to the human operator in order for the control architecture to function as observed?

This is NOT asking: "What does token X mean?"

This IS asking: "What observations drive what decisions?"

---

## 1. Hazard Classes -> Primary Sensory Affordances

The 5 hazard failure classes (C109, Tier 0 FROZEN) map to physical observables that require specific sensory capacities to detect.

| Hazard Class | % | Physical Observable | Primary Affordance | Secondary |
|--------------|---|---------------------|-------------------|-----------|
| **PHASE_ORDERING** | 41% | Material in wrong phase/location | VISUAL | Tactile |
| **COMPOSITION_JUMP** | 24% | Impure fraction passing | OLFACTORY | Visual |
| **CONTAINMENT_TIMING** | 24% | Overflow/pressure event | ACOUSTIC | Tactile |
| **RATE_MISMATCH** | 6% | Flow balance destroyed | VISUAL | Acoustic |
| **ENERGY_OVERSHOOT** | 6% | Thermal damage/scorching | OLFACTORY | Visual |

### What This Means

- **PHASE_ORDERING (41%)**: Largest hazard class. Detectable by watching phase state, condensation patterns, liquid levels. **Visual observation is indispensable.**

- **COMPOSITION_JUMP (24%)**: Second-largest. Detectable by smelling fraction identity, purity changes, contamination. **Olfactory discrimination is indispensable.**

- **CONTAINMENT_TIMING (24%)**: Detectable by hearing bubbling changes, pressure sounds, feeling apparatus vibration. **Acoustic + tactile are supporting.**

- **RATE_MISMATCH + ENERGY_OVERSHOOT (12%)**: Minor hazard classes. Multiple modalities involved.

---

## 2. Kernel Roles -> Control Intervention Affordances

The 3 kernel operators (C103-105, Tier 0 FROZEN) correspond to physical control intervention points.

| Kernel | Role | Physical Control | Presupposed Affordance |
|--------|------|------------------|------------------------|
| **k** | ENERGY_MODULATOR | Heat input adjustment | THERMAL - apparatus temperature by touch |
| **h** | PHASE_MANAGER | Phase transition management | VISUAL - condensation, boiling, flow |
| **e** | STABILITY_ANCHOR | Recovery to stable state | MULTI-MODAL - system quiescence |

### What This Means

- **k-intervention**: Operator must sense thermal state to know when/how to adjust heat. Hand on apparatus, feel of hot air, color of flame.

- **h-intervention**: Operator must see phase state to manage transitions. Watching condensation, observing boil patterns, tracking liquid levels.

- **e-recovery**: Operator must sense overall system stability. Multiple channels confirm "safe to proceed."

---

## 3. Decision Archetypes -> Required Sensory Inputs

The 12 decision archetypes (ECR-3) each presuppose specific observational capacities.

| Archetype | Decision | Hazard Risk | Presupposed Affordance |
|-----------|----------|-------------|------------------------|
| **D1** | Is material in correct phase/location? | PHASE_ORDERING | VISUAL |
| **D2** | Is this the right fraction? | COMPOSITION_JUMP | OLFACTORY |
| **D3** | Is containment secure? | CONTAINMENT_TIMING | ACOUSTIC + TACTILE |
| **D4** | Are inputs/outputs balanced? | RATE_MISMATCH | VISUAL + ACOUSTIC |
| **D5** | Is energy appropriate? | ENERGY_OVERSHOOT | THERMAL + VISUAL |
| **D6** | Intervene or wait? | LINK (38%) | MULTI-MODAL |
| **D7** | How do I return to stability? | e-recovery | MULTI-MODAL |
| **D8** | Can I restart from here? | CEI dynamics | THERMAL |
| **D9** | Is this case like that case? | A registry | OLFACTORY (identity) |
| **D10** | Where should I be vigilant? | HT signal | OLFACTORY (ambiguity) |
| **D11** | Where am I in process? | AZC | VISUAL (orientation) |
| **D12** | What operating regime? | C179 | THERMAL + VISUAL |

---

## 4. HT Vigilance -> Discrimination Difficulty by Modality

HT correlates with discrimination difficulty (C477: r=0.504 with rare MIDDLEs).

### Hypothesis

If HT marks contexts requiring careful sensory discrimination, then:

| Sensory Modality | Discrimination Difficulty | Predicted HT Correlation |
|------------------|---------------------------|--------------------------|
| **OLFACTORY** | HIGH (ambiguous, learned) | STRONG positive |
| **VISUAL** | MEDIUM (clear but requires attention) | MODERATE positive |
| **THERMAL** | LOW (direct sensation) | WEAK positive |
| **ACOUSTIC** | MEDIUM (pattern-based) | MODERATE positive |

### Expected Pattern

- HT density should be HIGHEST in contexts presupposing olfactory discrimination
- HT density should be LOWEST in contexts presupposing visual-only discrimination
- This would explain why HT correlates with "tail pressure" (rare MIDDLEs) - rare variants require olfactory expertise

---

## 5. Preliminary Assessment: Instruments vs Human Senses

### Human Sensory Resolution Limits

| Modality | Unaided Resolution | Limitation |
|----------|-------------------|------------|
| Visual | Phase state, color, ~5% clarity change | Good for categorical |
| Thermal | ~2-3C temperature difference | Good for threshold |
| Olfactory | Qualitative identity | Categorical only |
| Acoustic | Pattern recognition | Categorical only |
| Temporal | ~30 sec attention span | Requires aids for longer |

### Available 15th-Century Instruments

| Instrument | What It Aids | Availability |
|------------|--------------|--------------|
| Hourglass | Timing intervals (1-5 min) | Common |
| Scales | Weight comparison | Common in guilds |
| Thermoscope | Temperature indication | Rare, specialist |
| Pressure valve | Overpressure relief | Built into apparatus |

### Preliminary Assessment

**Signs the grammar presupposes UNAIDED operation:**

1. **MIDDLE distribution is categorical** (discrete variants, not continuous)
2. **Hazard boundaries are sharp thresholds** (safe/unsafe, not degrees)
3. **Discrimination is pattern-based** (recognition, not measurement)
4. **No magnitude encoding** (no numbers, no quantities)

**Possible exception: Timing**

- LINK (38% of grammar) implies waiting periods
- If LINK durations exceed ~30 sec attention span, hourglass may be presupposed
- This would be HYBRID: instruments for timing, human for discrimination

---

## 6. Sensory Affordance Summary

### Indispensable Affordances (Primary)

| Affordance | Why Indispensable | Hazard Coverage |
|------------|-------------------|-----------------|
| **VISUAL** | Phase position detection | 41% + supporting |
| **OLFACTORY** | Fraction identity discrimination | 24% + supporting |
| **THERMAL** | Energy state assessment | 6% + k-intervention |

### Supporting Affordances (Secondary)

| Affordance | Role | Hazard Coverage |
|------------|------|-----------------|
| **ACOUSTIC** | Containment monitoring | 24% (avoidance-focused) |
| **TACTILE** | Viscosity, apparatus state | Supporting |

### Possibly Instrument-Aided

| Function | Instrument | Assessment |
|----------|------------|------------|
| **Timing** | Hourglass | Likely if LINK > 30 sec |
| **Temperature** | Thermoscope | Unlikely (categorical suffices) |
| **Weight** | Scales | Unlikely (not encoded) |

---

## 7. What This Framework Establishes

### What it DOES establish:

1. **Which sensory capacities are necessary** for the control architecture to function
2. **Which hazards require which observations** (structural mapping)
3. **Why HT might correlate with olfactory contexts** (discrimination difficulty)
4. **Whether instruments are likely presupposed** (preliminary: mostly no)

### What it does NOT establish:

- Which token means which smell
- Which suffix means which temperature
- Any entity-level semantic content

---

## 8. Testable Predictions

| Prediction | Test | Expected |
|------------|------|----------|
| P1 | High-discrimination MIDDLEs cluster near COMPOSITION_JUMP hazards | YES |
| P2 | HT density correlates with olfactory-presupposing contexts | YES |
| P3 | k-adjacent contexts show thermal-sensitive MIDDLE profiles | YES |
| P4 | h-adjacent contexts show visual-sensitive MIDDLE profiles | YES |
| P5 | Visual-only operation cannot explain 564 ENERGY MIDDLEs | YES (exclusion) |
| P6 | MIDDLE distribution is categorical, not continuous | YES (human suffices) |

---

## Navigation

- [a_behavioral_classification.md](a_behavioral_classification.md) - Currier A classification
- [ecr_decision_archetypes.md](ecr_decision_archetypes.md) - Decision archetype definitions
- [apparatus_centric_semantics.md](apparatus_centric_semantics.md) - Apparatus role mappings

---

*Theoretical framework established 2026-01-12. Computational validation pending.*
