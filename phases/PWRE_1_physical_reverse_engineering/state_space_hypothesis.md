# AXIS C: State-Space Semantic Reconstruction

**Goal:** Infer what dimensions of physical state-space are being discretized and constrained by the controller.

**Key Principle:** Propose state-space semantics, NOT entity semantics. We identify property families without naming substances.

---

## Executive Summary

The controller tracks **two orthogonal axes** of physical state-space:

1. **Material Type Axis** (PREFIX) - "What category of stuff is this?"
2. **Handling Requirement Axis** (MIDDLE) - "How much operational latitude?"

These axes are deliberately kept **independent** (p = 0.852). This architecture explains:
- Why the registry is rich (~1,187 MIDDLEs)
- Why compatibility is sparse (95.7% illegal)
- Why substance identity is irrecoverable
- Why operational guidance remains viable

---

## The Two-Axis Architecture

### Axis 1: Material Type (PREFIX)

**Encoded by:** PREFIX morphology (ch, qo, sh, ok, ot, ct, da, ol)

**Structure:** 2×2 matrix of binary properties

| | Distinct | Homogeneous |
|---|----------|-------------|
| **Mobile** | M-A (ch, qo, sh) | M-B (ok, ot) |
| **Stable** | M-C (ct) | M-D (da, ol) |

**Physical Interpretation:**

| Class | Phase Behavior | Composition | Physical Analog |
|-------|---------------|-------------|-----------------|
| M-A | Mobile (vaporous, flowing) | Distinct (separable) | Volatile, pure fractions |
| M-B | Mobile | Homogeneous (mixing) | Flowing mixtures |
| M-C | Stable (solid, settled) | Distinct | Residues, precipitates |
| M-D | Stable | Homogeneous | Matrices, supports |

**Evidence (ECR Stress Tests):**
- 4-class structure is MINIMUM viable (B-4: RESISTS collapse)
- Phase mobility is binary at grammar level (B-1: RESISTS continuity)
- Classes cannot merge (B-3: M-B ≠ M-D)

---

### Axis 2: Handling Requirement (MIDDLE)

**Encoded by:** MIDDLE component (1,187 unique values)

**Structure:** Zone survival profiles cluster into 4 regimes

| Zone | Handling Character | Dominant Class |
|------|-------------------|----------------|
| C (entry) | Initial conditions | M-A |
| P (mid-process) | High intervention latitude | M-A |
| R (committed) | Restricted, low escape | M-A |
| S (late) | Boundary-sensitive | M-A |

**Key Finding:** M-A dominates ALL zones (57-72%).

**Physical Interpretation:**
- MIDDLE encodes "how to handle" independently of "what it is"
- Same material type can require different handling in different contexts
- Handling requirements form their own dimension

---

## Why the Axes Are Orthogonal

**Zone-Material Orthogonality Test (Section I.M):**

| Metric | Value |
|--------|-------|
| Predicted matches | 1/4 zones |
| P-value | 0.852 |
| Verdict | ORTHOGONAL |

**Interpretation:**

| Question | Answered By | NOT Answered By |
|----------|-------------|-----------------|
| "What category?" | PREFIX | MIDDLE |
| "How to handle?" | MIDDLE | PREFIX |

This orthogonality is **architecturally intentional**:
- Knowing the zone tells you NOTHING about material type
- Knowing material type tells you NOTHING about handling
- Both must be specified independently

**Why This Design?**
> Good apparatus design separates concerns. The manuscript encodes material type and handling latitude as **independent control dimensions**. This is optimal for closed-loop control where both matter but neither determines the other.

---

## The ~128 Latent Dimensions

### Source: MIDDLE Incompatibility Analysis (C475)

| Metric | Value |
|--------|-------|
| Unique MIDDLEs | 1,187 |
| Legal pairs | 4.3% |
| Illegal pairs | 95.7% |
| Connected components | 30 |
| Largest component | 1,141 (96%) |
| Hub MIDDLEs | 'a', 'o', 'e', 'ee', 'eo' |

### Dimensionality Estimate

The 30 connected components and hub structure suggest:
- ~128 effective dimensions of discrimination
- Sparse compatibility = highly constrained state-space
- Hub MIDDLEs = "universal" conditions that bridge components

### Property Families

Based on controller requirements, the latent dimensions likely encode:

| Property Family | Evidence | Physical Analog |
|----------------|----------|-----------------|
| **Phase State** | PHASE_ORDERING hazards (41%) | Solid/liquid/vapor |
| **Compositional Purity** | COMPOSITION_JUMP hazards (24%) | Fraction purity |
| **Volatility Class** | Zone survival (P-zone enrichment) | Boiling point regime |
| **Thermal Tolerance** | ENERGY_OVERSHOOT hazards (6%) | Heat sensitivity |
| **Pressure Sensitivity** | CONTAINMENT_TIMING hazards (24%) | Pressure tolerance |
| **Miscibility** | Incompatibility lattice | Solvent compatibility |
| **Reactivity** | Hub MIDDLEs (universal vs exclusive) | Chemical stability |

---

## Why Compatibility Is Sparse

### The 95.7% Incompatibility Question

**Why can only 4.3% of MIDDLE pairs coexist?**

**Hypothesis:** The controller tracks properties with **mutual exclusion**.

Physical examples of mutual exclusion:
- Temperature regimes (can't be both hot and cold)
- Phase states (can't be both liquid and solid simultaneously)
- Pressure regimes (can't be both high and low pressure)
- Volatility classes (can't be both volatile and involatile)

**The Constraint Satisfaction Model:**

```
MIDDLE = (phase_state, purity, volatility, thermal, pressure, ...)
```

Most combinations violate physical constraints:
- High volatility + high pressure → explosion risk
- Low volatility + high temperature → thermal damage
- Mixed phase + precise timing → race conditions

Only ~5% of combinations represent **physically viable operational regimes**.

### Hub MIDDLEs as Universal Conditions

The 5 hub MIDDLEs ('a', 'o', 'e', 'ee', 'eo') are compatible with almost everything.

**Physical Interpretation:**
These represent "neutral" or "ambient" conditions:
- Ambient temperature
- Atmospheric pressure
- Unspecified composition
- Default handling

---

## Why Identity Is Irrecoverable

### The Irrecoverability Question

**Why can we extract operational guidance but not substance identity?**

**Answer:** The architecture deliberately separates them.

| Information Layer | Encoded? | Recoverable? |
|-------------------|----------|--------------|
| Material type (PREFIX) | YES | PARTIALLY (4 classes) |
| Handling requirement (MIDDLE) | YES | YES |
| Specific substance | NO | NO |
| Quantity/ratio | NO | NO |
| Identity of entry | NO | NO |

### The Intersection Problem

Substance identity sits at the **intersection** of multiple axes:
- Material type + handling requirement + zone + context

But the controller keeps these **deliberately separate**:
- No coupling between PREFIX and MIDDLE (orthogonality)
- No entry-level A-B coupling (C384)
- No stored semantic context

**Why This Design?**
> The operator supplies identity from practice. The controller provides behavioral guidance. Neither needs the other's information to function.

### Irrecoverability Is Architectural

The barriers to identity recovery are **structural**, not cryptographic:

| Barrier | Mechanism | Constraint |
|---------|-----------|------------|
| Axis orthogonality | Can't infer type from handling | I.M (p=0.852) |
| Sparse compatibility | Can't infer from co-occurrence | C475 (95.7%) |
| No A-B coupling | Can't trace across systems | C384 |
| Categorical resolution | Can't recover parameters | C469 |
| Type-based behavior | Same handling for entire class | C383 |

---

## The Resulting State-Space Model

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PHYSICAL STATE-SPACE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Axis 1: MATERIAL TYPE (4 categories)                      │
│   ─────────────────────────────────────                     │
│   M-A: Mobile-Distinct (volatile fractions)                  │
│   M-B: Mobile-Homogeneous (flowing mixtures)                 │
│   M-C: Stable-Distinct (residues, precipitates)             │
│   M-D: Stable-Homogeneous (matrices, supports)              │
│                                                              │
│   Axis 2: HANDLING REQUIREMENT (~128 dimensions)            │
│   ─────────────────────────────────────────────             │
│   - Phase state (solid/liquid/vapor)                        │
│   - Compositional purity (fraction quality)                 │
│   - Volatility class (boiling point regime)                 │
│   - Thermal tolerance (heat sensitivity)                    │
│   - Pressure sensitivity (containment needs)                │
│   - Miscibility (solvent compatibility)                     │
│   - Reactivity (chemical stability)                         │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐  │
│   │           95.7% of combinations ILLEGAL              │  │
│   │           Only ~4.3% are viable regimes              │  │
│   │           5 hub conditions bridge components         │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                              │
│   CROSS-AXIS RELATIONSHIP: ORTHOGONAL (p = 0.852)          │
│   ─────────────────────────────────────────────────         │
│   - Material type does not predict handling                 │
│   - Handling does not predict material type                 │
│   - Both must be specified independently                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Why This Model Works

1. **Rich discrimination** - 1,187 MIDDLEs encode fine-grained handling
2. **Sparse legality** - 95.7% illegal pairs enforce physical constraints
3. **Hub bridging** - Universal conditions connect fragmented regimes
4. **Type abstraction** - 4 material classes capture relevant behavior
5. **Axis independence** - Orthogonality enables modular control

---

## Predictions

If this state-space model is correct:

| Prediction | Test |
|------------|------|
| Hub MIDDLEs correspond to "ambient" conditions | Verify hub MIDDLEs appear in recovery contexts |
| Incompatibility reflects physical mutual exclusion | Test if illegal pairs violate known physical laws |
| Zone survival reflects operational phase | Verify P-zone = active intervention, S-zone = boundary-sensitive |
| Material classes match hazard exposure | Verify M-A shows most PHASE_ORDERING hazards |

---

## Epistemic Status

This is a **Tier 3 state-space hypothesis**:
- Consistent with all Tier 0-2 constraints
- Provides explanatory power for observed patterns
- Does NOT identify specific substances
- Does NOT decode token meanings

> *This phase does not decode the Voynich Manuscript. It treats the manuscript as a completed controller and asks what classes of physical systems could realize it. All findings are contingent, non-binding, and do not alter any Tier 0-2 structural constraint.*

---

## Data Sources

| Finding | Source |
|---------|--------|
| 4-class material structure | `context/MODEL_FITS/ecr_stress_tests.md` |
| Zone-Material Orthogonality | `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` (I.M) |
| MIDDLE incompatibility | `context/CLAIMS/currier_a.md` (C475) |
| Categorical resolution | `context/CLAIMS/azc_system.md` (C469) |
| Global type system | `context/CLAIMS/C383_global_type_system.md` |
| No A-B coupling | `context/CLAIMS/C384_no_entry_coupling.md` |
