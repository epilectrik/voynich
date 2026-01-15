# Projection Specs

**Purpose:** Non-binding, one-way, UI-only specifications for displaying external alignments.

---

## What Projection Specs Are

Projection specs govern how **fits** (external alignments) are surfaced in tooling **without ever being allowed to act like structure**.

They are:
- Read-only interpretive overlays
- Display and explanation rules
- Semantic guardrails for UI

They are NOT:
- Structural contracts (like CASC, BCSC)
- Involved in parsing, inference, or validation
- Bidirectional or enforcing
- Authoritative over any computed result

---

## The Map Overlay Analogy

Think of projection specs like map overlays in cartography:

- **Terrain** = Structural contracts (fixed)
- **Overlay** = External alignment (highlights where another map lines up)
- **Turning off the overlay** does not change the terrain
- **Mistaking overlay for terrain** is a category error

Projection specs exist to prevent that mistake.

---

## Governing Principle

> **"This layer shows where external practice fits inside the Voynich control envelope; it never claims the manuscript encodes that practice."**

---

## Available Projection Specs

| Spec | Purpose | Status |
|------|---------|--------|
| [brunschwig_lens.md](brunschwig_lens.md) | Brunschwig distillation alignment display | ACTIVE |

---

## Key Requirements (All Specs)

1. **Scope Limitation:** No authority over parsing/validation
2. **Tier Marking:** Every element carries epistemic badge
3. **Modal Language:** "compatible with", not "is"
4. **Semantic Guardrails:** Explicit prohibited terms
5. **Provenance Links:** Every claim traces to fit ID

---

## Adding New Projection Specs

New specs may be added for other external alignments (e.g., Puff curriculum). They must:

- Follow the same structure as `brunschwig_lens.md`
- Include scope limitation at top
- Define display primitives with tier markers
- Specify prohibited phrasing
- Link to supporting fits

---

*This directory contains interpretive lenses, not structural truth.*
