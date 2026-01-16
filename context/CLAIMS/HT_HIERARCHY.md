# HT Formal Hierarchy

**Status:** FROZEN | **Version:** 1.0

---

## Design Principle

> **This hierarchy describes *constraints and alignment*, not *function or meaning*.**

**Permitted verbs:** aligned with, specialized for, correlated with, position-biased, system-conditioned

**Forbidden verbs:** encodes, annotates, represents, means, marks, defines

---

## Tier 0-1: Formal Status (Frozen)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Non-operational | C404, C405 | Terminal independence (p=0.92), causal decoupling (V=0.10) |
| Non-executing | C120 | PURE_OPERATIONAL verdict excludes HT |
| Removable without effect | C404 | Grammar unchanged after HT removal |
| Not read by any system | C415 | Non-predictivity (MAE worsens with HT conditioning) |
| Directionally downstream | C416 | System→HT: V=0.324; HT→System: V=0.202 (1.6x asymmetry) |

**Summary:** HT is formally inert. Systems do not consume it.

---

## Tier 2: Structural Properties (Frozen)

### HT-MORPH (Morphological Structure)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Modular morphology (PREFIX + CORE + SUFFIX) | C347 | 71.3% decompose into HT_PREFIX + MIDDLE + SUFFIX |
| Components are independent | C417 | No interaction or synergy (p=1.0) |
| Components are additive | C417 | Interaction model 3.9% worse than additive |
| CORE carries majority of positional signal | C418 | 'd'=69.6% line-initial, 'am'=52.8% line-final |
| Disjoint prefix vocabulary | C347 | Zero overlap with A/B prefixes |

### HT-POS (Positional Specialization)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Strong line-initial bias | C418, C419 | 2.61x enrichment (p < 10^-126) |
| Strong line-final bias (simplex) | C419 | 'd' = 55.8% line-final |
| Bias is system-conditioned | C419 | A: entry-aligned; B: phase-aligned |
| Bias is morphology-localized | C418 | CORE atoms carry positional signal |

### HT-SYS (System Conditioning)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Currier A: `-or/-ol`, simplex atoms | C419 | Category-aligned morphology |
| Currier B: `-edy`, complex forms | C347, C348 | Process-adjacent forms |
| Same inventory, different distributions | C419 | Shared vocabulary, divergent usage |

### HT-ASYM (Directional Asymmetry)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Strong correlation with system context | C414 | chi2=934, p<10^-145 |
| No predictive influence | C415 | MAE worsens by 0.003-0.005 |
| No causal influence | C405 | V=0.10 (negligible) |
| Unidirectional coupling | C416 | Grammar→HT only |

---

## Tier 2.5: System-Specific Specialization (Frozen)

### HT-A (Currier A Specialization)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Entry-boundary-aligned positional bias | C419 | 2.61x line-initial enrichment |
| Avoids category transition seams | C419 | 0 / 4,486 at seams |
| Weak category correlation | C419 | V=0.130 (above B, still non-predictive) |
| Does not define or gate categories | C419 | Removable without altering structure |

**Anchoring pressure:** Registry layout (entry boundaries)

### HT-B (Currier B Specialization)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Phase/waiting-aligned correlation | C341 | EXTREME: 15.9%, LOW: 5.7% |
| Zero predictivity over outcomes | C415 | MAE worsens with conditioning |
| Linked to non-intervention intervals | C341, C342 | Density tracks waiting profile |

**Anchoring pressure:** Temporal/attentional context (phase, complexity)

### HT-AZC (Diagram Specialization)

| Property | Constraint | Evidence |
|----------|------------|----------|
| Placement-synchronous with zones | C306, C317 | Follows positional grammar |
| Hybrid alignment | C301 | AZC is 69.7% B-compatible, 65.4% A-compatible |

**Anchoring pressure:** Diagram geometry

---

## Tier 3: Human-Behavior Interpretation (Open, Non-binding)

These interpretations are **consistent with** the structural evidence but **not entailed by it**.

**Dual-Purpose Attention Mechanism:**

| Function | Evidence |
|----------|----------|
| Attention maintenance during waiting | Phase-synchronized (C348), waiting-profile correlated (C341) |
| Guild training in written form | 7.81x rare grapheme engagement, 24.5% boundary-pushing, family rotation |

This is NOT "doodling" or "scribbling" - it is **deliberate skill acquisition** that doubles as attention maintenance.

| Structural Property | Interpretation |
|---------------------|----------------|
| Structured practice notation | Consistent with modular morphology |
| Context-synchronized writing | Consistent with system conditioning |
| Session/task influenced | Consistent with phase correlation |
| Intentional skill practice | Consistent with rare grapheme engagement, boundary exploration |

**Warning:** These are permitted as working hypotheses but must not be treated as structural facts.

---

## Tier 4: Narrative/Analogy (Optional, Non-inferential)

Available for communication, not for inference:

- Apprentice skill acquisition during operational waiting
- Medieval work-study combination model
- Attention externalization through deliberate practice

---

## Terminology Guardrail

When discussing HT in documentation, code, or UI:

### DO say:
- "HT is aligned with entry boundaries"
- "HT shows positional bias"
- "HT is system-conditioned"
- "HT correlates with phase"
- "HT is structurally present but non-operative"

### DO NOT say:
- "HT marks entries"
- "HT encodes position"
- "HT annotates content"
- "HT means X"
- "HT is for Y"

---

## Constraint Map

| Hierarchy Node | Constraints |
|----------------|-------------|
| Tier 0-1: Formal Status | C120, C404, C405, C415, C416 |
| HT-MORPH | C347, C417, C418 |
| HT-POS | C418, C419 |
| HT-SYS | C347, C348, C419 |
| HT-ASYM | C405, C414, C415, C416 |
| HT-A | C419 |
| HT-B | C341, C342, C415 |
| HT-AZC | C301, C306, C317 |

---

## Summary Statement

> **HT is a structured, modular, non-operative human-generated layer that exhibits system-conditioned positional alignment without predictive or causal influence on system behavior.**

- In Currier A: aligned with registry layout
- In Currier B: aligned with temporal/attentional context
- In AZC: aligned with diagram geometry

Same layer, **different anchoring pressures**.

---

## Navigation

← [human_track.md](human_track.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
