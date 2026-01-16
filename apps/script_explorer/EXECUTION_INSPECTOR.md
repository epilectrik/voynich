# Execution Inspector v0.1 — Frozen Specification

**Status:** FROZEN
**Date:** 2026-01-09
**Scope:** Grammar-anchored, context-conservative

---

## Overview

The Execution Inspector is an **opt-in extension** to Basic Inspection v1 that exposes Currier B execution semantics. It is:

- **Explicitly labeled** (checkbox + banner change)
- **Visually distinct** (orange-red banner, high-saturation colors)
- **System-scoped** (B folios only, auto-disabled elsewhere)
- **Context-conservative** (UNKNOWN = "not bound", not "error")

---

## Activation

1. Navigate to a **Currier B folio**
2. Check the **"Execution Inspector"** checkbox in the toolbar
3. Banner changes to: **"EXECUTION INSPECTOR ACTIVE"** (orange-red)
4. Tokens colored by kernel contact phase

To deactivate: uncheck the checkbox or navigate to A/AZC folio.

---

## Visual Mode: B_EXECUTION

The visual mode shows **kernel contact** (C372) as the primary axis:

| Phase | Prefix | Color | Hex |
|-------|--------|-------|-----|
| INTERVENTION | ch-, sh-, ok- | Bright red | #8A3030 |
| MONITORING | da-, sa- | Bright blue | #305A8A |
| ESCAPE | qo- | Bright green | #408A40 |
| Unclassified | other | Gray | #4A4A5A |

---

## Export Format

When exporting B tokens, the following fields are included:

```yaml
TOKEN: daiin
  primary_system: B
  prefix_family: d
  instruction_role: CORE_CONTROL
  grammar_bound: true
  surface_prefix: d
  surface_middle: -
  surface_suffix: aiin

TOKEN: chofochcphdy
  primary_system: B
  prefix_family: ch
  instruction_role: UNKNOWN
  grammar_bound: false
  surface_prefix: ch
  surface_middle: ofochcph
  surface_suffix: dy
```

### grammar_bound Field

| Value | Meaning |
|-------|---------|
| `true` | Token has explicit 49-class grammar binding |
| `false` | Token is UNKNOWN at this abstraction level |

**UNKNOWN does not mean "error"** — it means the token requires contextual analysis for classification.

---

## Grammar Mapping (49-class subset)

The following anchor tokens are explicitly bound:

| Token | Role | Constraint |
|-------|------|------------|
| daiin | CORE_CONTROL | C121 |
| ol | CORE_CONTROL | C121 |
| aiin | HIGH_IMPACT | C121 |
| dy | FREQUENT_OPERATOR | C121 |
| okedy, okeedy | FREQUENT_OPERATOR | C121 |
| shedy, sheey, shy | ENERGY_OPERATOR | C121 |
| qokedy, qokeedy | ENERGY_OPERATOR | C121 |
| chey, cheey, chedy | ENERGY_OPERATOR | C121 |
| dar | AUXILIARY | C121 (revised from FLOW_OPERATOR) |
| ar | AUXILIARY | C121 (revised from FLOW_OPERATOR) |
| saiin | AUXILIARY | C121 |
| ain | AUXILIARY | C121 |
| chol | FLOW_OPERATOR | C121 |

### Singleton Reclassifications

#### dar: FLOW_OPERATOR → AUXILIARY
`dar` was reclassified based on:
- `da-` prefix is kernel-light (monitoring phase)
- `-r` suffix is in kernel-light suffix group (C376: 6-12% contact)
- FLOW_OPERATOR typically requires stronger suffix signaling

#### ar: FLOW_OPERATOR → AUXILIARY
`ar` was reclassified based on:
- Bare singleton lacks suffix signaling for flow control
- Originally grouped with `chol` (ch- prefix, kernel-heavy) but morphologically dissimilar
- Moved from class 30 to class 46 (singletons like `ain`, `air`, `tar`)
- `chol` remains FLOW_OPERATOR (correct for ch- prefix)

---

## What Execution Inspector Does NOT Show

| Feature | Status | Future Work |
|---------|--------|-------------|
| Line position effects (C371) | Not in composite view | Use B_POSITION mode |
| LINK affinity (C373) | Not in composite view | Use LINK_AFFINITY mode |
| Hazard topology (C109) | Not implemented | Requires analysis layer |
| Forbidden transition proximity | Not implemented | Requires sequence context |
| UNKNOWN disambiguation | Not implemented | Optional UX enhancement |

---

## UNKNOWN Tokens

UNKNOWN tokens fall into several categories (not yet disambiguated):

| Category | Example | Reason |
|----------|---------|--------|
| Composite forms | chofochcphdy, shapchedyfeey | Multi-component, context-dependent |
| Damaged/partial | *aiin | Transcription uncertainty |
| Rare middles | Extended patterns | Insufficient frequency data |
| Context-required | Short tokens | Require line/position context |

**Future enhancement:** Add `unknown_reason` field to disambiguate.

---

## Constraints Referenced

| Constraint | Description | Usage |
|------------|-------------|-------|
| C121 | 49-class instruction grammar | Grammar role mapping |
| C357 | Lines as control blocks | Line semantics |
| C371 | Line-initial/final enrichment | Position mode |
| C372 | Kernel contact dichotomy | Primary visual axis |
| C373 | LINK affinity patterns | LINK mode |
| C376 | Suffix kernel dichotomy | dar reclassification |
| C397 | qo- escape route | Escape phase color |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-01-09 | Initial frozen specification |
| | | - B_EXECUTION visual mode |
| | | - grammar_bound export field |
| | | - dar reclassified to AUXILIARY |
| 0.1.1 | 2026-01-09 | Second-folio validation fixes |
| | | - ar reclassified to AUXILIARY (moved from class 30 to 46) |

---

## Future Directions (Not Committed)

These are potential extensions, not commitments:

1. **Composite overlay**: Show kernel contact + position + LINK simultaneously
2. **Hazard highlighting**: Color tokens near forbidden transitions
3. **UNKNOWN taxonomy**: Disambiguate UNKNOWN reasons
4. **Sequence context**: Show execution flow within lines

---

*This document freezes Execution Inspector v0.1. Changes require explicit versioning.*
