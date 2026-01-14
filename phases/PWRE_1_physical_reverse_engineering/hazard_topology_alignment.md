# AXIS B: Hazard Topology Alignment

**Goal:** Determine which physical process classes match the observed hazard distribution.

**Principle:** Compare against process archetypes WITHOUT naming specific processes. Focus on relative dominance, not mere presence.

---

## Observed Hazard Distribution

### Primary Distribution (C109)

| Hazard Class | Count | % | Description |
|--------------|-------|---|-------------|
| PHASE_ORDERING | 7 | 41% | Material in wrong phase/location |
| COMPOSITION_JUMP | 4 | 24% | Impure fractions passing |
| CONTAINMENT_TIMING | 4 | 24% | Overflow/pressure events |
| RATE_MISMATCH | 1 | 6% | Flow balance destroyed |
| ENERGY_OVERSHOOT | 1 | 6% | Thermal damage/scorching |

### Secondary Characteristics

| Property | Value | Source | Interpretation |
|----------|-------|--------|----------------|
| Asymmetric | 65% | C111 | Most hazards are one-way gates |
| Distant from kernel | 59% | C112 | Hazards arise in extended operation |
| Batch-focused | 71% | C216 | Opportunity-loss dominates |
| Apparatus-focused | 29% | C216 | Equipment protection secondary |
| LINK near apparatus hazards | 0 | C216 | Fast response required for equipment |

---

## Hazard Profile Requirements

Any compatible process class MUST exhibit:

1. **PHASE_ORDERING dominance (41%)** - Primary failure mode is wrong-phase-at-wrong-time
2. **COMPOSITION_JUMP significant (24%)** - Impurity transfer is a major concern
3. **CONTAINMENT_TIMING significant (24%)** - Pressure/overflow events matter
4. **RATE_MISMATCH rare (6%)** - Flow imbalance is minor concern
5. **ENERGY_OVERSHOOT rare (6%)** - Thermal damage is minor concern
6. **Batch-focused majority** - Most failures are opportunity-loss, not equipment damage
7. **Asymmetric hazards** - Most transitions are one-way (can fail going forward, not backward)

---

## Process Archetype Analysis

### Archetype 1: Batch Thermal Processes

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | Medium | Partial |
| COMPOSITION_JUMP | Low | NO |
| CONTAINMENT_TIMING | Medium | Partial |
| RATE_MISMATCH | Low | YES |
| ENERGY_OVERSHOOT | HIGH | NO |

**Verdict: POOR MATCH**

Batch thermal processes (heating solids, drying, calcination) would show ENERGY_OVERSHOOT as dominant, not rare. The observed 6% is incompatible.

**Eliminated by:** ENERGY_OVERSHOOT too low.

---

### Archetype 2: Circulatory Thermal Processes

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | HIGH | YES |
| COMPOSITION_JUMP | HIGH | YES |
| CONTAINMENT_TIMING | Medium | Partial |
| RATE_MISMATCH | Low | YES |
| ENERGY_OVERSHOOT | Low | YES |

**Verdict: GOOD MATCH**

Circulatory thermal processes (continuous heating with circulation, reflux systems) naturally prioritize:
- Phase ordering (keeping volatile vs condensed fractions separate)
- Composition purity (preventing cross-contamination between cycles)
- Timing (matching evaporation/condensation cycles)

Energy overshoot is controlled by the circulation buffer - thermal inertia protects against scorching.

**Compatible with observed distribution.**

---

### Archetype 3: Chemical Synthesis

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | Medium | Partial |
| COMPOSITION_JUMP | HIGH | Partial |
| CONTAINMENT_TIMING | Low | NO |
| RATE_MISMATCH | HIGH | NO |
| ENERGY_OVERSHOOT | Medium | NO |

**Verdict: POOR MATCH**

Chemical synthesis would show RATE_MISMATCH as critical (reagent ratios, reaction rates), but observed is only 6%.

**Eliminated by:** RATE_MISMATCH too low.

---

### Archetype 4: Mechanical Assembly

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | Low | NO |
| COMPOSITION_JUMP | Low | NO |
| CONTAINMENT_TIMING | Low | NO |
| RATE_MISMATCH | Medium | Partial |
| ENERGY_OVERSHOOT | Low | YES |

**Verdict: ELIMINATED**

Mechanical processes don't involve phase transitions or composition purity.

**Eliminated by:** No phase/composition hazards.

---

### Archetype 5: Biological Cultivation

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | Low | NO |
| COMPOSITION_JUMP | Medium | Partial |
| CONTAINMENT_TIMING | Low | NO |
| RATE_MISMATCH | HIGH | NO |
| ENERGY_OVERSHOOT | Low | YES |

**Verdict: POOR MATCH**

Biological processes emphasize rate matching (growth rates, nutrient timing) but show low phase ordering concerns.

**Eliminated by:** PHASE_ORDERING too low, RATE_MISMATCH too high expected.

---

### Archetype 6: Extraction/Separation

**Predicted Hazard Profile:**

| Hazard Class | Expected | Match? |
|--------------|----------|--------|
| PHASE_ORDERING | HIGH | YES |
| COMPOSITION_JUMP | HIGH | YES |
| CONTAINMENT_TIMING | Medium | YES |
| RATE_MISMATCH | Low | YES |
| ENERGY_OVERSHOOT | Low | YES |

**Verdict: EXCELLENT MATCH**

Extraction/separation processes naturally prioritize:
- Phase ordering (separating layers, timing of collection)
- Composition purity (preventing fraction mixing)
- Containment timing (managing pressure, vapor, overflow)
- Low rate concern (equilibrium-based, not rate-limited)
- Low energy concern (temperature is a control variable, not primary risk)

**Matches observed distribution closely.**

---

## Compatibility Summary

| Archetype | PHASE | COMP | CONTAIN | RATE | ENERGY | Overall |
|-----------|-------|------|---------|------|--------|---------|
| Batch Thermal | Partial | NO | Partial | YES | NO | ELIMINATED |
| Circulatory Thermal | YES | YES | Partial | YES | YES | COMPATIBLE |
| Chemical Synthesis | Partial | Partial | NO | NO | NO | ELIMINATED |
| Mechanical Assembly | NO | NO | NO | Partial | YES | ELIMINATED |
| Biological Cultivation | NO | Partial | NO | NO | YES | ELIMINATED |
| Extraction/Separation | YES | YES | YES | YES | YES | COMPATIBLE |

---

## Secondary Characteristic Matching

### Asymmetry Test (65%)

**Question:** Which processes have asymmetric hazards (fail going forward, not backward)?

| Archetype | Asymmetry Expected | Match? |
|-----------|-------------------|--------|
| Circulatory Thermal | HIGH (evaporation easy, condensation controlled) | YES |
| Extraction/Separation | HIGH (mixing easy, separating hard) | YES |

Both surviving archetypes naturally exhibit asymmetric hazards.

---

### Kernel Distance Test (59% distant)

**Question:** Which processes have hazards that arise in extended operation, not at control points?

| Archetype | Distant Hazards Expected | Match? |
|-----------|-------------------------|--------|
| Circulatory Thermal | YES (accumulation over cycles) | YES |
| Extraction/Separation | YES (impurity buildup over passes) | YES |

Both surviving archetypes have hazards that develop gradually.

---

### Batch vs Apparatus Focus (71%/29%)

**Question:** Which processes have opportunity-loss as the dominant failure mode?

| Archetype | Batch-Focused Expected | Match? |
|-----------|----------------------|--------|
| Circulatory Thermal | YES (losing volatile fraction) | YES |
| Extraction/Separation | YES (contaminating product) | YES |

Both surviving archetypes show batch-focused (opportunity-loss) dominance.

---

## Refined Compatible Profile

The hazard distribution is compatible with processes that:

1. **Involve phase transitions** (liquid/vapor/solid boundaries)
2. **Require composition purity** (separation or purification goal)
3. **Operate through multiple cycles** (not single-pass)
4. **Are equilibrium-based** (not rate-limited reactions)
5. **Use thermal energy as control** (not as direct product)

This profile is consistent with:
- **Circulatory thermal conditioning** (C177)
- **Volatile extraction** (C177)
- **Circulatory reflux** (C157)

All three were previously identified as viable process classes at Tier 2.

---

## Eliminated Process Classes

| Process Class | Primary Exclusion Reason |
|---------------|-------------------------|
| Batch thermal | ENERGY_OVERSHOOT too rare |
| Chemical synthesis | RATE_MISMATCH too rare |
| Mechanical assembly | No phase/composition hazards |
| Biological cultivation | PHASE_ORDERING too rare |
| Fermentation | RATE_MISMATCH would dominate |
| Glassmaking/metallurgy | ENERGY_OVERSHOOT would dominate |
| Dyeing/mordanting | Wrong phase structure |

---

## Hazard Topology Fit Score

| Constraint | Fit Status |
|------------|------------|
| PHASE_ORDERING dominant | CONFIRMED (41% matches thermal/separation) |
| COMPOSITION_JUMP significant | CONFIRMED (24% matches purity-critical) |
| CONTAINMENT_TIMING significant | CONFIRMED (24% matches circulatory) |
| RATE_MISMATCH rare | CONFIRMED (6% excludes chemical synthesis) |
| ENERGY_OVERSHOOT rare | CONFIRMED (6% excludes batch thermal) |
| Asymmetric hazards | CONFIRMED (65% matches thermal/separation) |
| Kernel-distant | CONFIRMED (59% matches accumulation processes) |
| Batch-focused | CONFIRMED (71% matches opportunity-loss) |

**All 8 criteria satisfied by circulatory thermal and extraction/separation archetypes.**

---

## Epistemic Status

This analysis uses the hazard distribution to constrain compatible process classes. It does NOT identify specific historical processes or substances.

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

## Data Sources

| Constraint | Source File |
|------------|-------------|
| C109 | `context/CLAIMS/C109_hazard_classes.md` |
| C110 | `context/CLAIMS/grammar_system.md` |
| C111 | `context/CLAIMS/grammar_system.md` |
| C112 | `context/CLAIMS/grammar_system.md` |
| C216 | `context/CLAIMS/grammar_system.md` |
| C157, C175, C177 | `context/CLAIMS/C171_closed_loop_only.md` |
