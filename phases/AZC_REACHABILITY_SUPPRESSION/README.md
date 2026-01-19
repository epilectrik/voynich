# Phase: AZC_REACHABILITY_SUPPRESSION

## Status: COMPLETE

## Question

> Can we give a mechanistically intelligible explanation of how AZC legality fields suppress parts of the B grammar without selection, branching, or semantics - at the instruction class level?

## Closure Statement Target

> "AZC does not modify B's grammar; it shortens the reachable language by forbidding certain class transitions at certain positions once particular constraint bundles are active."

---

## Phase 1 Results: Data Foundation

### 1.1 Forbidden Transitions (Token -> Class Mapping)

| Metric | Value |
|--------|-------|
| Token-level forbidden transitions | 17 |
| Class-level forbidden pairs | 13 |
| Unmapped transitions | 3 |
| Classes involved in hazards | 9 of 49 |
| Base graph edge density | 99.1% |

**The 9 hazard-involved classes:**

| Class | Role | Representative | Out | In |
|-------|------|----------------|-----|-----|
| 7 | FLOW_OPERATOR | ar | 1 | 1 |
| 8 | ENERGY_OPERATOR | chedy | 1 | 3 |
| 9 | FREQUENT_OPERATOR | aiin | 1 | 2 |
| 11 | CORE_CONTROL | ol | 1 | 0 |
| 23 | FREQUENT_OPERATOR | dy | 3 | 1 |
| 30 | FLOW_OPERATOR | dar | 1 | 1 |
| 31 | ENERGY_OPERATOR | chey | 3 | 3 |
| 33 | ENERGY_OPERATOR | qokeey | 1 | 2 |
| 41 | ENERGY_OPERATOR | qo | 1 | 0 |

**Class 31 (chey/shey)** is the most constrained: 3 forbidden outgoing + 3 forbidden incoming.

### 1.2 MIDDLE -> Instruction Class Index

| Metric | Value |
|--------|-------|
| Unique MIDDLEs in 49 classes | 62 |
| Exclusive MIDDLEs (1 class) | 23 |
| Shared MIDDLEs (2+ classes) | 39 |

**Critical finding: Two-tier hazard system**

| Class | Decomposable? | MIDDLEs | AZC Constrainable? |
|-------|---------------|---------|-------------------|
| 7 (ar) | NO (0/2) | 0 | NO - atomic |
| 8 (chedy) | YES (3/3) | 1 shared | YES |
| 9 (aiin) | NO (0/3) | 0 | NO - atomic |
| 11 (ol) | YES (1/1) | 1 shared | YES |
| 23 (dy) | NO (0/7) | 0 | NO - atomic |
| 30 (dar) | YES (5/5) | 3 (1 excl) | YES |
| 31 (chey) | YES (12/12) | 3 shared | YES |
| 33 (qokeey) | YES (13/13) | 4 shared | YES |
| 41 (qo) | YES (6/6) | 3 shared | YES |

**Interpretation:**
- **Atomic classes (7, 9, 23)**: Cannot be constrained by AZC MIDDLE restrictions
- **Decomposable classes (8, 11, 30, 31, 33, 41)**: Can be further constrained by AZC

This creates a **two-tier constraint system**:
1. Universal hazard topology (17 forbidden transitions)
2. AZC-conditioned suppression (affects only decomposable hazard classes)

---

## Files Created

- `reachability_analysis.py` - Main analysis script
- `phase1_results.json` - Forbidden transition mapping
- `middle_class_index.json` - MIDDLE -> class index

---

## Phase 2: Mechanism Synthesis

### The Two-Tier Constraint System

**Tier 1: Universal Grammar Constraints (Always Active)**
- 49 instruction classes
- 17 forbidden transitions (13 class pairs)
- 9 classes involved in hazards
- 99.1% base graph density

**Tier 2: AZC-Conditioned Constraints (Context-Dependent)**
- 77% of MIDDLEs appear in only 1 AZC folio (C472)
- 6 of 9 hazard classes are decomposable (affected by MIDDLE restrictions)
- 3 of 9 hazard classes are atomic (NOT affected by MIDDLE restrictions)

### The Mechanism

```
AZC provides "legality field"
    |
    v
Restricted MIDDLEs become unavailable
    |
    v
Decomposable classes lose effective membership:
- Class 8 (chedy): 1 shared MIDDLE
- Class 11 (ol): 1 shared MIDDLE
- Class 30 (dar): 3 MIDDLEs (1 exclusive!)
- Class 31 (chey): 3 shared MIDDLEs
- Class 33 (qokeey): 4 shared MIDDLEs
- Class 41 (qo): 3 shared MIDDLEs
    |
    v
Fewer paths through hazard-constrained region
    |
    v
"Reachable grammar manifold shrinks"
```

### Atomic vs Decomposable Hazard Classes

| Type | Classes | Behavior |
|------|---------|----------|
| **Atomic** | 7 (ar), 9 (aiin), 23 (dy) | Always fully available - universal hazard enforcement |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | Context-dependent availability - tunable hazard envelope |

**Interpretation:** The grammar has BOTH universal hazard constraints (atomic classes like `aiin`, `dy`, `ar`) AND context-tunable constraints (decomposable classes). AZC doesn't change the grammar - it changes which parts are reachable.

### Closure Statement

> "AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. The 49-class grammar and 17 forbidden transitions are universal. When AZC provides a legality field, 6 of 9 hazard-involved classes have reduced effective membership because their MIDDLEs become unavailable. The 3 atomic hazard classes remain fully active regardless of AZC context."

This is a **complete control-theoretic pipeline**:
- **A** supplies discrimination bundles (constraint signatures)
- **AZC** projects them into position-indexed legality fields
- **B** executes within the shrinking reachable language

With no semantics. With no branching. With no lookup. With no "if".

---

## Constraints Respected

- C313: Position constrains legality, not prediction
- C384: No entry-level A-B coupling
- C454/C455: No adjacency or cycle coupling
- C440: Uniform B sourcing across AZC folios
- C121/C124: 49-class grammar is universal
- C468: AZC constraint transfer to B
- C469: Categorical resolution (no parametric encoding)
- C470: Folio-specific MIDDLE restrictions
- C472: 77% MIDDLE exclusivity to single AZC folio

---

## Key Definitions

**Atomic Hazard Class**: An instruction class containing only tokens that have no MIDDLE component. These classes cannot be constrained by AZC vocabulary restrictions and enforce universal hazard behavior regardless of context.

**Decomposable Hazard Class**: An instruction class containing tokens with MIDDLE components. When AZC restricts a MIDDLE's availability (per C472), these classes have reduced effective membership, shrinking the reachable grammar manifold.

**Legality Field**: The ambient vocabulary availability determined by AZC context. This is not selection or branching - it is the set of MIDDLEs that are "legal" (available) at a given position.

**Reachable Grammar Manifold**: The subset of the 49-class grammar that can actually be traversed given a particular legality field. Same grammar everywhere, different reachable parts.
