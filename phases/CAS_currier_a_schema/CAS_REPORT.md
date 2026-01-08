# Phase CAS: Currier A Schema Investigation

**Phase ID:** CAS
**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** COMPLETE
**Date:** 2026-01-06

---

## Executive Summary

> **Currier A is a non-sequential, flat categorical classification system operating as a registry of entries tagged by mutually exclusive marker prefixes.**

It is NOT a grammar. It is NOT a different grammar. It is a fundamentally different kind of formal system.

---

## Consolidated Findings

### What Currier A IS (Structurally Proven)

| Property | Evidence | Confidence |
|----------|----------|------------|
| LINE-ATOMIC | Median 3 tokens/line, MI=0 across lines | HIGH |
| POSITION-FREE | Zero JS divergence between positions | HIGH |
| CATEGORICAL TAGGING | 8+ mutually exclusive marker prefixes | HIGH |
| FLAT (not hierarchical) | Zero vocabulary overlap between markers | HIGH |
| DATABASE-LIKE | TTR=0.137, 70.7% bigram reuse | HIGH |
| REPETITIVE | Top patterns: "daiin daiin", "chol chol" | HIGH |
| SECTION-CONDITIONED | Same markers, different vocabulary per section | HIGH |
| DESIGNED SEPARATION from B | 25/112,733 cross-transitions (0.0%) | HIGH |

### What Currier A is NOT

| Claim | Status | Evidence |
|-------|--------|----------|
| A grammar (like B) | FALSIFIED | Silhouette 0.049, no transition structure |
| A different grammar | FALSIFIED | No positional constraints, no order invariants |
| A field/slot system | FALSIFIED | JS divergence = 0.0 (positions identical) |
| Free text | FALSIFIED | Highly stereotyped, 58% in top 5 patterns |
| Accidental variation | FALSIFIED | Hard boundary, designed separation |

---

## Phase Results

### CAS-1: Atomicity
**Verdict: LINE_ATOMIC**

- Each line is an atomic unit (record)
- Median line length: 3 tokens
- 28% single-token lines
- Zero cross-line dependencies

### CAS-2: Slot/Field Detection
**Verdict: POSITION_FREE**

- Tokens can appear anywhere in an entry
- No first/last positional preferences
- JS divergence = 0.0 between positions
- **BUT: Strong mutual exclusion detected**

### CAS-3: Marker Taxonomy
**Verdict: CATEGORICAL_TAGGING**

| Marker | Occurrences | Excludes |
|--------|-------------|----------|
| ch | 2,040 | 40 others |
| qo | 1,135 | 35 others |
| sh | 1,007 | 32 others |
| da | 677 | 27 others |
| ok | 630 | 27 others |
| ot | 568 | 25 others |
| ct | 448 | 18 others |
| ol | 289 | 10 others |

**Critical finding:** Co-occurrence matrix is ALL ZEROS. These prefixes NEVER appear together in the same entry. Vocabulary overlap is also ZERO.

### CAS-4: Section-Schema Binding
**Verdict: GLOBAL_SCHEMA_LOCAL_VOCABULARY**

- All 10 markers appear in ALL sections (H, P, T)
- ch dominates everywhere (H: 17.7%, P: 15.2%, T: 13.2%)
- BUT: 78.7% of H vocabulary is H-exclusive
- Same classification SYSTEM, different vocabulary per domain

### CAS-5: Redundancy & Normalization
**Verdict: DATABASE_LIKE (3/4)**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Type-Token Ratio | 0.137 | Heavy vocabulary reuse |
| Bigram reuse rate | 70.7% | Extremely formulaic |
| Pattern concentration | 58.5% | Few templates dominate |
| Top bigrams | "daiin daiin" (1651x) | Repetitive registry |

### CAS-6: A/B Interaction Boundary
**Verdict: DESIGNED_SEPARATION (3/3)**

| Metric | Value |
|--------|-------|
| Cross-language transitions | 25 / 112,733 (0.0%) |
| Vocabulary Jaccard | 0.141 |
| Mixed folios | 14.1% |

Section breakdown:
- P = 100% A (Pharmaceutical)
- H = 70% A (Herbal)
- B, C, S = 100% B

---

## Structural Model of Currier A

```
CURRIER A = CATEGORICAL REGISTRY

Structure:
  - Entry = line (atomic unit)
  - Entry = [MARKER] + [PAYLOAD?]
  - MARKER = one of {ch, qo, sh, da, ok, ot, ct, ol, yk, yt, ...}
  - MARKERS are MUTUALLY EXCLUSIVE (never co-occur)
  - PAYLOAD = 0+ additional tokens (often repetitions)

Properties:
  - Position-free (order within entry doesn't matter)
  - Flat taxonomy (no hierarchical nesting)
  - Section-conditioned (same markers, different vocabulary per section)
  - Repetitive (tokens repeat within entries)

Function:
  - Classification/tagging of items
  - Registry/catalog structure
  - Human-queryable, NOT machine-executable
```

---

## Relationship to Currier B

| Aspect | Currier A | Currier B |
|--------|-----------|-----------|
| Type | Categorical registry | Procedural grammar |
| Structure | Flat, position-free | Sequential, transition-based |
| Unit | Line (entry) | Folio (program) |
| Vocabulary | 70% exclusive | 79% exclusive |
| Markers | Tag category | Execute instruction |
| Purpose | Classification | Operation |

**They are TWO INTENTIONAL SYSTEMS with designed separation.**

---

## What This Means

### For the Manuscript

The Voynich Manuscript contains:
1. **Currier B:** An executable control grammar (49 classes, procedural)
2. **Currier A:** A categorical classification system (registry, non-procedural)

These serve DIFFERENT FUNCTIONS:
- B = "How to operate"
- A = "What we're operating on" (classification/catalog)

### For Analysis

- A cannot be analyzed as a grammar
- A cannot be "executed"
- A has no "hazards" or "forbidden transitions"
- A's structure is schema-based, not sequence-based
- Meaningful A analysis = schema/constraint architecture

### What Cannot Be Recovered

- What the categories MEAN (ch = ?, qo = ?)
- What is being classified
- The relationship between A categories and B operations
- Whether A "labels" B content or is independent

---

## CAS Deep Structure: Shared Structural Primitives

### The CORE_CONTROL Asymmetry

Analysis of B's grammar reveals that `daiin` and `ol` are the only two CORE_CONTROL terminals. Their behavior across A and B:

| Token | A Frequency | B Frequency | A:B Ratio | Affinity |
|-------|-------------|-------------|-----------|----------|
| `daiin` | 4.73% | 1.51% | **1.55** | A-enriched |
| `ol` | 0.80% | 1.84% | **0.21** | B-enriched |

**The control pair is broken in A:**
- In B: `daiin` and `ol` appear adjacent 54 times
- In A: Only 27 adjacent occurrences

### Neighborhood Flip

| Token | A Neighbors | B Neighbors |
|-------|-------------|-------------|
| `daiin` | Content: `chol`, `shol`, `chor` | Grammar: `chedy`, `ol`, `qoky` |
| `ol` | Content/marginal | Grammar: `qokain`, `daiin`, `shedy` |

The same token is surrounded by **content words** in A but **grammar particles** in B.

### Structural Primitive Reuse (Key Insight)

> **Analysis of shared tokens between Currier A and Currier B shows that certain symbols function as reusable structural primitives whose role is determined by the formal system in which they are embedded. The token `daiin`, one of two CORE_CONTROL elements in the Currier B executable grammar, appears in Currier A as a high-frequency articulation token linking payload elements within non-sequential records, while its counterpart `ol` remains functionally tied to sequential execution contexts. This demonstrates deliberate reuse of structural components across formally incompatible systems without semantic transfer.**

### What This Does NOT Mean

- `daiin` does NOT "mean" separator, boundary, item, and, with, or of
- This is NOT semantic decoding — it is structural role identification
- Repetition is NOT counting — it is a repetition-tolerant registry pattern

### What This DOES Mean

- The author thought in terms of **formal roles**, not words
- Tokens were selected for **structural affordance**, not reference
- **System polymorphism**, not meaning polymorphism
- This explains why semantic decoding inevitably fails despite apparent overlap

---

## New Constraints (CAS + CAS-DS)

| # | Constraint |
|---|------------|
| 233 | Currier A atomicity = LINE_ATOMIC; each line is an atomic unit (median 3 tokens); cross-line MI = 0 |
| 234 | Currier A positional structure = POSITION_FREE; JS divergence = 0.0 between positions; tokens appear freely |
| 235 | Currier A marker taxonomy: 8+ mutually exclusive prefix categories (ch, qo, sh, da, ok, ot, ct, ol); co-occurrence = 0; vocabulary overlap = 0 |
| 236 | Currier A marker structure = FLAT (no hierarchy); no subsumption relationships detected |
| 237 | Currier A is DATABASE_LIKE: TTR=0.137, bigram reuse 70.7%, pattern concentration 58.5%, repetitive entries |
| 238 | Currier A section binding: same markers in all sections, 78.7% section-exclusive vocabulary; global schema, local instantiation |
| 239 | Currier A/B separation = DESIGNED: 0.0% cross-transitions, Jaccard 0.141, hard boundaries at section level |
| 240 | Currier A formal type: non-sequential flat categorical classification system; registry/catalog, not grammar |
| 241 | CORE_CONTROL tokens (`daiin`, `ol`) show opposite system affinities: `daiin` A-enriched (1.55x), `ol` B-enriched (0.21x) |
| 242 | `daiin` neighborhood flip: in A surrounded by content words; in B surrounded by grammar particles; role is system-determined |
| 243 | `daiin`-`ol` pairing broken in A: 54 adjacent in B vs 27 in A; execution control structure absent in A |
| 244 | Structural primitive reuse: tokens function as reusable components whose role is system-determined; demonstrates infrastructure reuse without semantic transfer |

---

## Files Generated

### CAS Core (Schema Analysis)
- `cas_phase1_atomicity.py` - Atomicity tests
- `cas_phase2_fields.py` - Slot/field detection
- `cas_phase3_markers.py` - Marker taxonomy
- `cas_phase4_sections.py` - Section-schema binding
- `cas_phase5_normalize.py` - Database-like properties
- `cas_phase6_boundary.py` - A/B boundary analysis
- `cas_ab_encapsulation_test.py` - A/B encapsulation test (NO_ENCAPSULATION)
- `cas_phase*_results.json` - Raw results

### CAS Deep Structure (Structural Primitives)
- `cas_deep_structure_tests.py` - 5-test deep structure battery
- `analyze_daiin.py` - daiin usage pattern analysis
- `analyze_daiin_v2.py` - Corrected daiin analysis
- `analyze_daiin_relationships.py` - daiin relationship/bigram analysis
- `analyze_daiin_context.py` - daiin context analysis
- `compare_core_control.py` - CORE_CONTROL token comparison
- `check_daiin_grammar_v2.py` - Grammar class lookup
- `cas_deep_structure_results.json` - Deep structure raw results

### Reports
- `CAS_REPORT.md` - This report

---

## Phase Tag

```
Phase: CAS
Tier: 2 (STRUCTURAL INFERENCE)
Subject: Currier A Schema Architecture
Type: Data structure characterization
Status: COMPLETE
Verdict: NON_SEQUENTIAL_CATEGORICAL_REGISTRY
```
