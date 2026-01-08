# Phase CAS: Currier A Schema Investigation

**Phase ID:** CAS
**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** IN PROGRESS
**Date:** 2026-01-06

---

## Conceptual Pivot

This phase treats Currier A as a **non-sequential categorical data structure**, not a failed grammar.

| Old Frame (rejected) | New Frame (adopted) |
|---------------------|---------------------|
| Tokens | Fields |
| Grammar | Schema |
| Transitions | Constraints |
| Execution | Normalization |
| "What does it do?" | "What relations does it impose?" |

---

## What Currier A Is Allowed To Be

> **A non-sequential, formal symbolic schema used to organize or partition domains of discourse.**

May encode:
- Membership
- Classification
- Association
- Exclusion
- Hierarchy
- Identity vs non-identity

May NOT encode:
- Action
- Order
- Process
- Causality
- Transformation

---

## New Structural Primitives

| Primitive | Definition |
|-----------|------------|
| **Entry** | Atomic unit (not a run) |
| **Field** | Position-defined slot (not ordered step) |
| **Marker** | Prefix/suffix assigning category |
| **Payload** | Content token (not executable) |
| **Boundary** | Folio, section, layout constraint |

---

## Investigation Phases

### CAS-1: Atomicity Redefinition
**Question:** What is the smallest complete unit in Currier A?

Tests:
- Are entries line-bounded?
- Are they diagram-bounded?
- Do tokens interact across lines/entries?

Outcomes:
- Entry-level atomicity → record system
- Cross-entry dependencies → higher-order schema

---

### CAS-2: Slot/Field Detection
**Question:** Are token positions constrained by role?

Tests:
- Token position entropy (1st, 2nd, last)
- Prefix/suffix exclusivity by position
- Mutual exclusion patterns

Looking for: **positional invariants**, not order invariants

---

### CAS-3: Marker Taxonomy
**Question:** What marker categories exist (without meaning)?

Tests:
- Mutual exclusivity of markers
- Nesting/hierarchy patterns
- Section-specific marker sets
- Clean vocabulary partitioning

---

### CAS-4: Section-Schema Binding
**Question:** Do sections impose different schema constraints?

Tests:
- Section-specific marker activation
- Illegal markers per section
- Cross-section role variation

Determines: global taxonomy vs domain-local schemas

---

### CAS-5: Redundancy & Normalization
**Question:** Does A behave like a database?

Tests:
- Token reuse across entries
- Normalized vs expanded forms
- Key-value patterns

Testing for: indexing, referencing, denormalization

---

### CAS-6: Interaction Boundary with B
**Question:** Is A/B separation designed or accidental?

Tests:
- A-B adjacency patterns
- Boundary strictness
- Cross-system transition legality

Strong boundaries → designed separation

---

## Safe vs Unsafe Hypotheses

### SAFE (structure-only)
- A is a record schema (entries with fixed fields)
- A encodes category membership
- A supports many short identifiers
- A supports multiple orthogonal classification axes
- A is human-queryable but machine-blind

### UNSAFE (forbidden - introduces semantics)
- "This token names a plant"
- "This is preparation"
- "This refers to product X"
- "This means alcohol / medicine / dye"
- "This label corresponds to illustration Y"

---

## Expected Deliverable

> **Currier A behaves like a non-sequential categorical data structure:
> entries composed of repeated identifiers subject to section-dependent schema constraints, without operational semantics.**

This characterization:
- Specifies the formal object type
- Defines valid analyses
- Marks questions forever out of bounds
- Completes MS 408 internal architecture

---

## Files

```
phases/CAS_currier_a_schema/
├── CAS_CHARTER.md          # This document
├── cas_phase1_atomicity.py # Entry-level atomicity
├── cas_phase2_fields.py    # Slot/field detection
├── cas_phase3_markers.py   # Marker taxonomy
├── cas_phase4_sections.py  # Section-schema binding
├── cas_phase5_normalize.py # Redundancy/normalization
├── cas_phase6_boundary.py  # A/B interaction boundary
├── CAS_REPORT.md           # Final synthesis
└── cas_results.json        # Raw data
```
