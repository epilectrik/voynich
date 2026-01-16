# Phase CAS-MULT: Multiplicity Encoding in Currier A

**Phase ID:** CAS-MULT
**Tier:** 1 (FALSIFIED)
**Status:** **INVALIDATED** (2026-01-16)
**Date:** 2026-01-06

---

> ## **WARNING: THIS PHASE IS INVALIDATED**
>
> The "64.1% block repetition" pattern discovered in this phase was a **transcriber artifact**. When filtered to PRIMARY transcriber (H) only, block repetition is **0%**.
>
> The apparent `[BLOCK] × N` pattern was caused by interleaved readings from multiple transcribers (H, F, C, U, V, etc.) being loaded together. Each transcriber's reading of the same token appeared as a separate row, creating false repetition patterns.
>
> **All findings and constraints from this phase (C250-C266) are INVALIDATED.** See TRANSCRIBER_REVIEW.md for details.

---

## ~~Executive Summary~~ INVALIDATED

~~> **Currier A records categorical entities where multiplicity is encoded by literal repetition of a unit block, without abstraction, aggregation, or execution.**~~

~~This phase discovered that 64.1% of Currier A entries exhibit a **repeating block structure** of the form `[BLOCK] × N`, where the repetition itself encodes multiplicity. This is **enumerative instantiation**, not numeric counting.~~

---

## Key Finding

### The Pattern

```
[BLOCK] × N
```

Where:
- **BLOCK** = a sequence of tokens (typically 5-9 tokens)
- **N** = number of repetitions (typically 2-6)
- **Repetition IS the multiplicity** — no abstract count symbol exists

### Examples

```
[dol chokal schos] × 5           → 5 instances enumerated
[soiin chaiin chaiin] × 3        → 3 instances enumerated
[otchol odaiim] × 4              → 4 instances enumerated
[daiin ckhochy tchy koraiin] × 3 → 3 instances enumerated
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Entries with repeating blocks | **64.1%** (1013/1580) |
| Average repetition count | **2.79** |
| Repetition distribution | 2x: 416, 3x: 424, 4x: 148, 5x: 20, 6x: 5 |
| Blocks containing marker prefix | **97.1%** |
| Unique blocks (no cross-entry reuse) | **100%** |
| Most common block sizes | 5-9 tokens |

---

## Critical Distinction: Enumeration vs Counting

This is **NOT numeric counting**:

| Numeric Counting | Enumerative Instantiation (Currier A) |
|------------------|---------------------------------------|
| `ITEM = 5` | `ITEM, ITEM, ITEM, ITEM, ITEM` |
| Abstract quantity | Literal repetition |
| Allows arithmetic | No arithmetic possible |
| Aggregates across records | Intra-record only |
| Single symbol represents N | N copies represent N |

Currier A implements **enumerative instantiation** — each repetition instantiates the SAME record unit again, rather than incrementing a counter.

This is **exactly how medieval registries often worked** — proto-bureaucratic, pre-numeric records.

---

## Structural Consequences

| Property | Implication |
|----------|-------------|
| No abstract quantity | Cannot do `3 + 2 = 5` |
| No arithmetic | Cannot sum across entries |
| No summarization | No totals, no aggregation |
| Intra-record only | Multiplicity confined to single line |
| No cross-record linkage | Each entry self-contained |

---

## Why This Fits Currier A

| Feature | Why repetition fits |
|---------|---------------------|
| No grammar | Enumeration doesn't require grammar |
| Line-atomic | One category instance group per line |
| Marker exclusivity | One domain per registry entry |
| High intra-line repetition | Multiplicity encoded literally |
| No sequencing | Order irrelevant inside a record |
| No execution | Registration, not operation |
| Low TTR (0.137) | Same tokens repeated within entries |
| 70.7% bigram reuse | Blocks repeat exactly |

---

## Relationship to Currier B

The relationship is **NOT**:
> B = how to operate; A = what/how much was operated

That would violate the CAud finding of 0.0% cross-system transitions.

The **correct relationship** is:
> **B = executable control grammar**
> **A = non-executable categorical enumeration system**
> **They share infrastructure (structural primitives), not meaning**

Currier A enumerates **categories of things-that-exist**, NOT things-that-happened.

---

## What Currier A Resembles (Tier 3, speculative)

Without crossing into semantic claims:

**It resembles:**
- Specimen registers
- Holding inventories
- Ownership rolls
- Classification lists with abundance indication

**It is NOT:**
- Transactional
- Temporal
- Causal
- Procedural

Multiplicity answers **"how many exist under this classification"**, not **"how many were processed"**.

---

## What This Does NOT Claim

| Claim | Status |
|-------|--------|
| "Workshop production log" | ❌ NOT defensible |
| "Quantities processed" | ❌ Exceeds evidence |
| "Material counts" | ❌ Unsupported |
| "Inventory tied to B operations" | ❌ Violates CAud |
| Specific products or materials | ❌ Beyond internal analysis |

---

## New Constraints

| # | Constraint |
|---|------------|
| 250 | Currier A encodes multiplicity via **literal repetition**, not abstraction; 64.1% of entries show `[BLOCK] × N` structure (CAS-MULT) |
| 251 | Multiplicity repetition is **intra-record only**; no cross-record aggregation, arithmetic, or summarization exists (CAS-MULT) |
| 252 | Repetition scale bounded: typically 2-6 instances per entry; distribution peaks at 2x (416) and 3x (424) (CAS-MULT) |
| 253 | All repeating blocks are **unique** (0% cross-entry reuse); each entry defines its own enumeration unit (CAS-MULT) |
| 254 | Multiplicity does NOT interact with Currier B; enumerative registry is fully isolated from operational grammar (CAS-MULT) |

---

## Refined Characterization

Previous: `NON_SEQUENTIAL_CATEGORICAL_REGISTRY`

Refined: `MULTIPLICITY_ENCODED_CATEGORICAL_REGISTRY`

> **Currier A is a non-executable categorical registry that encodes multiplicity through literal block repetition, without abstraction, aggregation, or operational linkage.**

---

## Files Generated

- `currier_a_payload_analysis.py` — Initial payload pattern detection
- `currier_a_block_analysis.py` — Block repetition quantification
- `CAS_MULT_REPORT.md` — This report

---

## Phase Tag

```
Phase: CAS-MULT
Tier: 2 (STRUCTURAL INFERENCE)
Subject: Multiplicity Encoding in Currier A
Type: Structural pattern analysis
Status: COMPLETE
Verdict: MULTIPLICITY_ENCODED_CATEGORICAL_REGISTRY
```
