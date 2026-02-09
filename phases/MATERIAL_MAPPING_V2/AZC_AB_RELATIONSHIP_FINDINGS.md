# AZC and A-B Relationship Findings

**Date:** 2026-01-29
**Phase:** MATERIAL_MAPPING_V2 (extended investigation)

## Executive Summary

Through systematic testing, we resolved longstanding confusion about the AZC model and the A-B relationship. The key insight: **AZC is a reference legend, not a computational filter. A constrains B vocabulary, not through a pipeline, but by defining legality envelopes that an operator applies.**

---

## Part 1: AZC Is Not a Causal Filter

### The Test

We tested whether AZC adds predictive power beyond vocabulary composition:

- **Model 1:** Vocabulary features only (PREFIX/qo_rate)
- **Model 2:** Vocabulary + AZC overlap features

### Result

| Predictor | R² for B escape rate |
|-----------|---------------------|
| Vocabulary (qo_rate) | **1.0000** |
| AZC overlap (residual) | **0.0000** |

**Vocabulary fully determines B behavior. AZC adds nothing.**

### Interpretation

AZC doesn't "filter" or "propagate constraints" in any causal sense. The vocabulary itself has inherent behavioral properties (qo- prefix → escape behavior). These properties are consistent wherever the vocabulary appears.

### What AZC Actually Is

**AZC is a legend/key that documents vocabulary properties.**

- AZC positions (P, R, S, C) group vocabulary by behavioral properties
- P-position vocabulary has high-escape properties
- S-position vocabulary has locked/no-escape properties
- A reader can consult AZC to learn what tokens mean
- We (as researchers) used AZC to discover PREFIX-behavior correlations

**Analogy:** AZC is like a Rosetta Stone - it teaches you the code, but doesn't execute anything.

### Constraints Affected

| Constraint | Status | Note |
|------------|--------|------|
| C765 (AZC Kernel Access Bottleneck) | Valid but reframe | Describes correlation, not causation |
| C753 (Constraint propagation) | Misleading language | "Propagation" suggests causation; it's correlation |
| AZC-ACT contract | Needs revision | Mechanistic language should become descriptive |

---

## Part 2: AZC Position Correlates With Vocabulary Properties

### The Test

We compared B behavior for tokens appearing in different AZC positions:

| AZC Position Group | B Tokens | Escape Rate |
|-------------------|----------|-------------|
| Only HIGH-escape (P) | 2,161 | **23.4%** |
| Only LOW-escape (R3/S) | 2,173 | **1.4%** |
| BOTH positions | 5,464 | **3.1%** |

### Interpretation

- 16x escape difference between high-only and low-only vocabulary
- Tokens in BOTH positions show intermediate behavior
- This is consistent with vocabulary having inherent properties that AZC documents
- The "intermediate" behavior suggests AZC position has some correlation, but it's mediated by vocabulary composition

---

## Part 3: A-B Relationship Is Constraint-Based

### The Problem

We couldn't match specific A records to specific B folios:
- f58v alone is best match for 62/82 B folios
- Only 2 A folios cover almost all B vocabulary
- 78% of A-B pairings are "unusable"

### The Reframe

**A doesn't contribute content to B. A constrains what B content is legal.**

```
A Record = Constraint Specification
    - PP tokens define "vocabulary envelope"
    - RI tokens provide identity/discrimination
    - NOT a procedure, NOT a vocabulary list
    - It's a FILTER DEFINITION

B Folio = Procedure
    - Uses vocabulary from the 480-token grammar
    - Grammar is self-contained (BCSC)
    - Unique vocabulary = procedure identity

Relationship:
    - A doesn't "send" vocabulary to B
    - A specifies which B vocabulary is LEGAL in this context
    - Operator selects A (based on material) and B (based on desired procedure)
    - Execution uses vocabulary that survives both constraints
```

### Why A Has Repetition But No Grammar

- A is flat (no syntactic structure beyond morphology)
- But PP tokens repeat at 75% rate
- Resolution: Repetition represents "capacity markers" - emphasis/weight, not procedural sequence
- Constraint specifications don't need grammar; they're envelope definitions

### Why Most A-B Pairings Are Unusable

From C690: Most pairings produce >50% empty lines
From C502: Each A record makes ~80% of B vocabulary illegal

"Unusable" means too much vocabulary is filtered out - the procedure can't execute meaningfully. "Viable" pairings have enough vocabulary overlap.

### The Missing Piece: The Operator

A and B don't connect directly. A human operator connects them:

1. Operator has material → identifies via A's RI discrimination
2. A record's PP profile → constrains which B vocabulary is legal
3. Operator selects B folio → based on desired procedure
4. Execution uses vocabulary that survives the intersection

**A specifies constraints. B provides procedures. The operator makes the match.**

---

## Part 4: What Remains Unknown

### Operational Mechanics

If A constrains B vocabulary, what happens to B lines with illegal tokens?
- Skip lines entirely?
- Illegal tokens become no-ops?
- Only viable pairings should be used?

We haven't determined the operational mechanics of execution.

### How Operator Knows Viability

How does the operator know which A-B pairings are viable?
- Domain knowledge?
- Lookup table we haven't found?
- Trial and error?

### RI Discrimination

RI tokens are supposed to provide "fine discrimination" for identifying materials/contexts. We don't know how to read them.

---

## Part 5: The Coherent Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         THE SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A Records (342 paragraphs)                                      │
│  ├── RI tokens: Identity/discrimination (don't propagate)        │
│  └── PP tokens: Vocabulary envelope (constraint definition)      │
│       └── Repetition = capacity markers, not counts              │
│                                                                  │
│  AZC Diagrams (30 folios)                                        │
│  └── Legend/key that documents vocabulary properties             │
│       ├── P position: high-escape vocabulary                     │
│       ├── S position: locked vocabulary                          │
│       └── Reader learns token meanings by studying positions     │
│                                                                  │
│  B Programs (82 folios)                                          │
│  ├── 49 instruction classes with grammar                         │
│  ├── Hazard topology (17 forbidden transitions)                  │
│  └── Self-contained execution with legal vocabulary              │
│                                                                  │
│  OPERATOR (human user)                                           │
│  ├── Identifies material → selects A record                      │
│  ├── Selects procedure → chooses B folio                         │
│  └── Ensures viable pairing (enough vocabulary overlap)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 6: Proposed Constraint Updates

### New Tier 3 Interpretation

**AZC-LEGEND: AZC as Reference Legend**

> AZC diagrams function as a reference legend documenting vocabulary properties, not as a computational filter. AZC position correlates with behavioral properties (P=high escape, S=locked), but vocabulary alone fully determines B behavior (R²=1.0). AZC may have served both as an authoring guide (maintaining consistency) and a reader reference (learning the system).

### Revisions Needed

| Document | Revision |
|----------|----------|
| AZC-ACT | Replace mechanistic language ("propagates," "filters") with descriptive ("correlates with," "groups") |
| AZC-B-ACT | Clarify that B receives vocabulary, not "constraints from AZC" |
| MODEL_CONTEXT.md | Update AZC section to reflect legend interpretation |
| INTERPRETATION_SUMMARY.md | Add AZC-legend and A-B constraint model |

---

## Part 7: Evidence Summary

| Finding | Evidence | Tier |
|---------|----------|------|
| Vocabulary fully predicts B behavior | R² = 1.0 for PREFIX→escape | 2 |
| AZC adds no predictive power | Residual R² = 0.000 | 2 |
| AZC position correlates with vocabulary properties | 16x escape difference | 2 |
| No specific A→B mapping | f58v matches 62/82 B folios | 2 |
| A-B coverage is pool-size dominated | r = 0.883 | 2 |
| AZC is a legend/key | Interpretation of above | 3 |
| A constrains B vocabulary | Interpretation of above | 3 |
| Operator closes the loop | Inference from model | 3 |

---

## Provenance

Tests run:
- `18_azc_position_causality_test.py`
- `19_azc_causal_vs_epiphenomenal.py`
- `20_ab_pairing_specificity.py`
- `21_a_record_repetition_analysis.py`

Expert consultations: 4 sessions validating interpretations
