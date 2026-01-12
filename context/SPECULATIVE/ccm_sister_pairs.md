# Component-to-Class Mapping: Sister-Pair Analysis (CCM-3)

**Tier:** 3 | **Status:** COMPLETE | **Date:** 2026-01-10

> **Goal:** Determine what the sister-pair choice (ch vs sh, ok vs ot) encodes semantically.

---

## Key Finding

**Sister-pair choice encodes operational mode, not material identity.**

The choice between ch and sh (or ok and ot) is:
- Grammatically equivalent (same slot)
- Semantically distinct (different operational implications)
- Predictive of program behavior

---

## Data Sources

| Source | What It Provides |
|--------|------------------|
| C408 | Sister pairs are equivalence classes |
| C410 | Section conditioning of sister choice |
| C410.a | MIDDLE-driven preference (25.4% deviation) |
| C412 | **Sister-escape anticorrelation (rho = -0.326)** |

---

## The C412 Discovery

From C412:

| ch-Preference | Escape Density | Interpretation |
|---------------|----------------|----------------|
| 70.3% (Q1) | 7.1% (LOW) | "Brittle" programs |
| 61.9% (Q4) | 24.7% (HIGH) | "Forgiving" programs |

**Statistical validation:** rho = -0.326, p = 0.002

**Key insight:** Programs with more ch-forms have fewer recovery affordances. Programs with more sh-forms have more escape routes.

---

## Sister-Pair Semantic Content

### ch vs sh Distinction

| Preference | Escape Density | Mode | Interpretation |
|------------|----------------|------|----------------|
| **ch-dominant** | LOW | Brittle | "Stay on path, fewer recovery options" |
| **sh-dominant** | HIGH | Forgiving | "More escape routes, safer to explore" |

This is NOT about material identity. It's about **operational risk tolerance**.

### Hypothesis: Mode Selection

The sister-pair choice may encode:

| Sister | Operational Mode | Material Class Interaction |
|--------|------------------|---------------------------|
| **ch** | Precision mode | M-A operations with tight tolerances |
| **sh** | Recovery mode | M-A operations with escape routes |
| **ok** | (needs testing) | M-B operations, standard |
| **ot** | (needs testing) | M-B operations, variant |

---

## Conditioning Hierarchy (C410.a)

The choice is conditioned by (in order):

| Factor | Deviation | Role |
|--------|-----------|------|
| MIDDLE | 25.4% | Type refinement drives preference |
| Suffix | 22.1% | Surface realization compatibility |
| Adjacent token | 23.9% | Run continuation (ch→ch: 77%) |
| Section | V=0.078 | Background bias |
| Position | V=0.071 | Weak (sh-first, ch-last tendency) |
| DA context | V=0.001 | NONE — confirms DA is structural |

**Interpretation:** The MIDDLE component primarily determines sister choice. Different MIDDLEs have near-categorical preferences:

| MIDDLE | ch-Preference |
|--------|---------------|
| yk | 97.1% |
| okch | 96.3% |
| l | 96.2% |
| et | 93.8% |
| s | 92.5% |

Some MIDDLEs virtually require ch-form; others permit sh-form.

---

## Cross-Reference with Material Classes

From CCM-1, ch-/sh- operate on M-A class (mobile, distinct) materials.

The sister distinction adds a sub-dimension:

| Sister | Material Class | Operational Sub-Mode |
|--------|----------------|---------------------|
| **ch** | M-A | Precision handling (low escape) |
| **sh** | M-A | Tolerant handling (high escape) |

This is consistent with:
- Same material class (both handle mobile-distinct)
- Different operational risk profiles
- Section H preference for ch (78-92%) = more precision-critical operations

---

## CCM-3 Synthesis

### What Sister-Pair Choice Encodes

| Dimension | Encoded by Sister Choice |
|-----------|-------------------------|
| Material identity | NO — both sisters operate on same material class |
| Grammatical role | NO — both occupy identical slots |
| Operational mode | **YES** — precision vs. tolerance |
| Recovery affordance | **YES** — correlates with escape density |

### Compositional Meaning (Updated)

```
TOKEN = PREFIX (material-class operation)
      + SISTER-VARIANT (operational mode)
      + MIDDLE (type refinement + mode selection)
      + SUFFIX (decision type)
```

The sister variant encodes **how carefully** the operation must be executed:
- ch/ok = tight execution, fewer recovery options
- sh/ot = tolerant execution, more escape routes

---

## Section Conditioning Explained

Why does Section H prefer ch-forms (78-92%)?

From C299: Section H vocabulary dominates B procedures (91.6%).

If Section H materials are more actively used in operations, and those operations require precision:
- H = precision-critical materials → ch-preferred
- Other sections = more tolerance → sh-acceptable

This aligns with the hazard topology: PHASE_ORDERING (41%) and COMPOSITION_JUMP (24%) are the dominant hazards. Precision matters most for mobile, distinct materials in active operations.

---

## Remaining Questions

| Question | Status |
|----------|--------|
| Does ok/ot show similar brittleness correlation? | Not tested |
| What determines MIDDLE-level sister preference? | Partially explained |
| Can sister preference predict specific hazard types? | Not tested |

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C408 | Equivalence class structure preserved |
| C410 | Section conditioning explained |
| C412 | Anticorrelation interpreted as mode selection |
| C410.a | MIDDLE-driven preference maps to type-level mode |

---

## Semantic Achievement

**We can now say:**

> "The choice between ch and sh encodes operational mode within the same material class — ch-dominant sequences are precision-oriented with fewer recovery options, while sh-dominant sequences are tolerance-oriented with more escape routes."

This is class-level semantics. We're not saying what materials ch operates on — we're saying **how** it operates: with tight tolerances and limited recovery.

---

## Navigation

← [ccm_suffix_mapping.md](ccm_suffix_mapping.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
