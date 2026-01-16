# Basic Inspection v1 — Frozen Schema

**Status:** FROZEN
**Date:** 2026-01-09
**Scope:** Structural coverage only — no execution semantics

---

## Overview

Basic Inspection v1 provides a **non-semantic, system-aware structural inspection layer** for the Voynich Manuscript. Every token is assigned:

1. A **primary system** (A, B, AZC, HT)
2. A **native role** specific to that system
3. **Global properties** shared across all systems

This layer exposes structure without interpretation. It does not execute, infer, or enforce.

---

## System Coverage

| System | Native Role Axis | Properties Exposed |
|--------|------------------|-------------------|
| **Currier A** | Registry role | `a_registry_role`: REGISTRY_ENTRY, VALID_MINIMAL, INFRASTRUCTURE_MINIMAL, UNKNOWN |
| **Currier B** | Instruction class | `b_instruction_class`: 49-class grammar (C400+), partial binding allowed |
| **AZC** | Placement class | `azc_placement`: C, P, R, R1-R3, S, S1-S2, Y, MULTI, UNKNOWN |
| **HT** | Classification | `ht_classification`: HT override (when applicable) |
| **Global** | Type system | prefix_family, kernel_affinity, escape, surface segmentation |

---

## Global Properties (All Systems)

Every token record includes:

```yaml
token: <surface form>
primary_system: A | B | AZC | HT
prefix_family: ch | sh | ok | qok | d | s | l | y | o | NONE
kernel_affinity: ol | or | al | ar | ain | aiin | NONE
escape: true | false
surface_prefix: <string> | -
surface_middle: <string> | -
surface_suffix: <string> | -
```

---

## Native Role Properties

### Currier A Tokens
```yaml
a_registry_role: REGISTRY_ENTRY | VALID_MINIMAL | INFRASTRUCTURE_MINIMAL | UNKNOWN
```

### Currier B Tokens
```yaml
b_instruction_class: <C4xx constraint class> | UNKNOWN
```
- Partial binding allowed (not all tokens have assigned classes)
- Grammar is 49-class system per C400-C411

### AZC Tokens
```yaml
azc_placement: C | P | R | R1 | R2 | R3 | S | S1 | S2 | Y | MULTI | UNKNOWN
azc_placement_set: [R, P, S]  # Only present when azc_placement = MULTI
```
- Placement derived from diagram positional codes (C306)
- MULTI indicates token appears in multiple diagram positions
- No legality enforcement at this layer

### HT Tokens
```yaml
ht_classification: <HT class>
```
- HT classification overrides other system assignments when present

---

## Explicit Non-Coverage

The following are **deliberately NOT exposed** at this layer:

| Category | What's Excluded | Why |
|----------|-----------------|-----|
| **Execution** | Kernel contact, line position effects, LINK behavior | Requires execution semantics |
| **Legality** | AZC placement windows, B grammar validation | Requires rule enforcement |
| **Sequence** | Token order constraints, diagram flow | Requires positional inference |
| **Semantics** | Meaning, translation, interpretation | Out of scope entirely |
| **Cross-system** | A↔B transitions, AZC↔B correlations | Requires analysis layer |

---

## UNKNOWN and MULTI Handling

### UNKNOWN
- Indicates binding not possible with current data
- **Preserve, do not infer**: UNKNOWN is honest signal, not failure
- May resolve with future constraint additions

### MULTI (AZC only)
- Indicates token appears in multiple diagram positions
- `azc_placement_set` lists all observed positions
- **Not an error**: AZC tokens legitimately occupy multiple slots
- Collapsing would lose structural information

---

## Interpretation Guidelines

1. **UNKNOWN means "not yet bound"** — not "invalid" or "error"
2. **MULTI means "multiple positions observed"** — not "ambiguous" or "conflicting"
3. **Partial binding is expected** — 100% coverage is not a goal
4. **No execution state** — this layer is purely structural
5. **System assignment is primary** — native role follows from system

---

## Schema Stability

This schema is **frozen**. Changes require:

1. New constraint number (C4xx series)
2. Documentation update
3. Explicit version bump

Do not add fields, remove fields, or change semantics without versioning.

---

## Export Format

Token records are exported as YAML blocks:

```yaml
# Example: Currier B token
- token: daiin
  primary_system: B
  prefix_family: d
  kernel_affinity: aiin
  escape: false
  b_instruction_class: C402
  surface_prefix: d
  surface_middle: -
  surface_suffix: aiin

# Example: AZC token with multiple placements
- token: okeey
  primary_system: AZC
  prefix_family: ok
  kernel_affinity: NONE
  escape: false
  azc_placement: MULTI
  azc_placement_set: [R, P, S]
  surface_prefix: ok
  surface_middle: ee
  surface_suffix: y

# Example: Currier A minimal
- token: dy
  primary_system: A
  prefix_family: d
  kernel_affinity: NONE
  escape: false
  a_registry_role: INFRASTRUCTURE_MINIMAL
  surface_prefix: d
  surface_middle: -
  surface_suffix: y
```

---

## Execution Inspector (Opt-In Extension)

Basic Inspection v1 deliberately excludes execution semantics. However, an **opt-in Execution Inspector** is available for Currier B folios.

### Enabling Execution Inspector

1. Navigate to a **Currier B folio** (any folio not in Currier A or AZC sets)
2. Check the **"Execution Inspector"** checkbox in the toolbar
3. The banner will change to orange-red: **"EXECUTION INSPECTOR ACTIVE"**
4. Tokens will be colored by kernel contact phase

### Execution Inspector Shows

| Property | Visual Encoding | Constraint |
|----------|-----------------|------------|
| Kernel contact | Background color | C372 |
| Phase: INTERVENTION | Red background (ch-, sh-, ok-) | C372 |
| Phase: MONITORING | Blue background (da-, sa-) | C372 |
| Phase: ESCAPE | Green background (qo-) | C397 |

### Execution Inspector Does NOT Show

- Line position effects (use B_POSITION mode separately)
- LINK affinity (use LINK_AFFINITY mode separately)
- Hazard topology (not yet implemented)
- Forbidden transition proximity (not yet implemented)

### Separation of Concerns

Execution Inspector is **visually distinct** from Basic Inspection:
- Different banner color (orange-red vs amber)
- Different color palette (high saturation)
- Explicit opt-in required
- Auto-disabled when leaving B system

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial frozen schema |
| 1.1 | 2026-01-09 | Added opt-in Execution Inspector (B_EXECUTION mode) |

---

*This document defines the structural inspection layer. Execution inspection is a separate, opt-in mode.*
