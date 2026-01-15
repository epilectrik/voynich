# Brunschwig Projection Spec

**Type:** Interpretive Lens (NOT a structural contract)
**Version:** 1.0
**Date:** 2026-01-15
**Status:** ACTIVE

---

## Scope Limitation (CRITICAL)

> **This spec has no authority over parsing, grammar, inference, or validation.**
> **It governs display and explanation only.**
> **Removing it must not change any computed result.**

If deleting this spec breaks the app's *logic*, the spec is wrong.

This is a **read-only interpretive overlay** — a map overlay that highlights where external practice aligns with internal structure, without claiming the manuscript encodes that practice.

---

## Governing Principle

> **"This layer shows where external practice fits inside the Voynich control envelope; it never claims the manuscript encodes that practice."**

---

## What This Spec Is

- A non-binding, one-way, UI-only projection specification
- Takes frozen internal structure + annotated external fits
- Decides what may be shown, how it must be labeled, what must never be implied
- An explanatory lens, not a system feature

## What This Spec Is NOT

- A YAML contract like CASC/BCSC
- Involved in A→AZC→B processing
- Allowed to introduce new categories
- Allowed to collapse uncertainty
- Allowed to "decide" between interpretations
- Bidirectional or enforcing

---

## Display Primitives

### Structural (Tier 2) — Always Available

| Element | Source | Required Label |
|---------|--------|----------------|
| PREFIX profile histogram | C466-C467 | "Control-flow participation profile" |
| REGIME classification | C179-C185 | "Execution completeness regime" |
| MIDDLE incompatibility rate | C475 | "Compatibility constraint density" |
| Morphological decomposition | C267-C278 | "Compositional structure" |

### Fit-Based (F2-F3) — Requires Tier Badge

| Element | Source | Required Label |
|---------|--------|----------------|
| Product type envelope | F-BRU-001 | "Externally aligned product family (non-exclusive)" |
| Degree-REGIME mapping | F-BRU-002 | "Historical processing intensity alignment" |
| A-register signature similarity | F-BRU-005 | "Similarity under incompatibility topology" |
| MIDDLE hierarchy layer | F-BRU-005 | "Vocabulary sharing scope" |

---

## Tier Marking Rules (Non-Negotiable)

Every rendered element MUST carry its epistemic status visually.

| Badge | Meaning | Example Elements |
|-------|---------|------------------|
| **STRUCTURAL** | Derived from Tier 0-2 constraints | PREFIX bars, REGIME tag, morphology |
| **EXTERNAL FIT** | Derived from F-series alignment | Product type, degree mapping |
| **SPECULATIVE** | Tier 3-4 interpretation | (Not recommended for display) |

**Implementation:** Badges should be visible, not hidden in tooltips. The UI constantly reminds the viewer what is fixed and what is contingent.

---

## Required Phrasing

### Allowed Modal Language

Use relational, non-assertive phrasing:

- "compatible with"
- "aligns with"
- "falls within the envelope of"
- "requires similar execution completeness to"
- "structurally excludes"
- "consistent with procedures in"

### Example Correct Phrasing

> "This folio is compatible with procedures in the WATER_GENTLE class under the Brunschwig alignment model."

> "PREFIX profile aligns with OIL_RESIN execution requirements."

> "MIDDLE vocabulary falls within the cross-cutting layer (shared by 2-3 product types)."

---

## Hard Semantic Guardrails (Negative Rules)

The following are **PROHIBITED** in any UI element:

| Prohibited | Why |
|------------|-----|
| ❌ Naming substances | Violates C171 (zero material encoding) |
| ❌ Listing plants | Semantic assertion without structural basis |
| ❌ Recipe suggestions | Implies content, not structure |
| ❌ One-to-one mappings ("f17r = X") | Violates C384 (no entry-level mapping) |
| ❌ Token glossaries | Implies translation, which is impossible |
| ❌ "means", "stands for", "represents" | Asserts semantics |
| ❌ "is" (identity claims) | Use "aligns with" or "compatible with" |

### Prohibited Phrasing Examples

- ❌ "This folio is rose water"
- ❌ "daiin means heat application"
- ❌ "Try lavender here"
- ❌ "f32r represents delicate flowers"
- ❌ "WATER_GENTLE = aromatic florals"

---

## Provenance Links (Traceability)

Every displayed Brunschwig-related claim MUST link to:

1. **Fit ID** that supports it (e.g., F-BRU-001)
2. **Constraints it depends on** (e.g., C475, C476)
3. **Tooltip note** explaining derivation

### Tooltip Template

```
[EXTERNAL FIT]
Source: F-BRU-001 (Brunschwig Product Type Prediction)
Depends on: C475 (MIDDLE incompatibility), C476 (coverage optimality)
Note: Derived from external alignment analysis; not encoded in Voynich.
```

---

## Product Type Definitions

These are **alignment categories**, not material identities.

| Type | Structural Signature | Brunschwig Alignment |
|------|---------------------|---------------------|
| WATER_GENTLE | ok↑, ch↓, y~7% | 1st degree, balneum heat |
| WATER_STANDARD | ch~24%, d~18% | 2nd degree, moderate heat |
| OIL_RESIN | d↑, y↓, ch~21% | 3rd-4th degree, aggressive |
| PRECISION | Variable, LINK↑ | Any degree, timing-critical |

**Display Rule:** Always show as "compatible with [TYPE]" not "is [TYPE]".

---

## MIDDLE Hierarchy Display

| Layer | Definition | Display Color (suggested) |
|-------|------------|---------------------------|
| Universal | Appears in all 4 product types | Gray (infrastructure) |
| Cross-cutting | Appears in 2-3 types | Blue (shared constraint) |
| Type-specific | Appears in 1 type only | Green (local coordinate) |

**Display Rule:** Layer assignment is descriptive, not definitional. A MIDDLE being "universal" means it appears everywhere, not that it "means" something universal.

---

## Implementation Checklist

Before shipping any Brunschwig-related feature:

- [ ] Does removing this feature change any parsing/validation result? (Must be NO)
- [ ] Does every element carry a tier badge?
- [ ] Does phrasing use modal language only?
- [ ] Are all prohibited terms absent?
- [ ] Does every claim link to a fit ID?
- [ ] Can a user understand what is structural vs external?

---

## Mental Model

Think of this like a **map overlay in cartography**:

- The terrain (constraints) is fixed
- The overlay (Brunschwig) highlights where a different map happens to line up
- Turning the overlay off does not change the terrain
- Mistaking the overlay for the terrain is a category error

This spec exists solely to prevent that mistake.

---

## File Dependencies

| File | Role |
|------|------|
| `context/MODEL_FITS/fits_brunschwig.md` | Fit definitions (F-BRU-001 to F-BRU-005) |
| `context/MODEL_FITS/FIT_TABLE.txt` | Fit registry |
| `results/exclusive_middle_backprop.json` | Product type classifications |
| `results/cross_type_middle_analysis.json` | MIDDLE hierarchy data |

---

## Governance

This spec may be updated to add new display primitives as new fits are validated. It may NOT:

- Add structural claims
- Override constraint definitions
- Introduce bidirectional inference
- Collapse epistemic uncertainty

Changes require updating this file and noting in CHANGELOG.

---

*Projection Spec v1.0 | Display-only | No parsing authority | 2026-01-15*
