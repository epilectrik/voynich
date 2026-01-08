# Phase CAud: Currier A Executability Boundary Audit

**Phase ID:** CAud
**Tier:** 0 (STRUCTURAL FINDING - FALSIFIES GENERALIZATION CLAIM)
**Status:** COMPLETE
**Date:** 2026-01-06

---

## Purpose

Determine whether Currier A text is executable under the frozen B-derived grammar.

**Three Admissible Conclusions:**
1. EXECUTABLE — A operates under frozen grammar (same system)
2. RELATED_NON_EXECUTING — A is structurally related but non-executable layer
3. DISJOINT — A is a separate non-system layer

---

## VERDICT: DISJOINT

**Currier A is a structurally DISJOINT system from Currier B.**

The 49-class grammar derived from Currier B does NOT generalize to Currier A. Currier A operates under different vocabulary, different transition rules, and violates the forbidden transitions that define Currier B's hazard topology.

---

## Data Summary

| Corpus | Tokens | Folios | Unique Types |
|--------|--------|--------|--------------|
| Currier A | 11,415 | 114 | 3,446 |
| Currier B | 23,226 | 82 | 4,949 |
| Total | 37,940 | 196 | — |

**Note:** Currier A has MORE folios but FEWER tokens per folio (100 vs 283).

---

## Track Results Summary

| Track | Name | Verdict | Key Metric | Interpretation |
|-------|------|---------|------------|----------------|
| 0 | Folio Atomicity | AMBIGUOUS | overlap=0.66x | A has lower cross-folio dependency |
| 1-2 | Grammar Coverage | **FAIL** | cov=13.6%, val=2.1% | **Grammar does NOT apply** |
| 3 | Hazard Topology | **FAIL** | violations=5 | **Different hazard rules** |
| 4 | Track Classification | SYSTEM_TRACK | 2/3 conditions | Paradox: behaves like system |
| 5 | Morphology | DIVERGENT | 41% divergence | Different word-formation |
| 6 | LINK/Kernel | DIFFERENT | link=0.45x | Less waiting behavior |
| 7 | Density | SPARSE | 0.35x | Label-like vs procedural |
| 8 | Execution | **FAIL** | stall=86.4% | Cannot execute |

---

## Critical Findings

### 1. Grammar Coverage FAILS (13.6%)

Only 13.6% of Currier A tokens appear in the 49-class grammar (threshold: 70% for PASS).

- **A-only vocabulary:** 66.8% of A types do not appear in B
- **B-only vocabulary:** 14% of high-frequency B tokens missing from A
- **Vocabulary overlap:** ~33% between A and B

**Implication:** A and B have largely distinct vocabularies. The grammar derived from B describes only ~1/7 of A's tokens.

### 2. Transition Validity FAILS (2.1%)

Only 2.1% of adjacent token pairs in A form valid grammar transitions.

- 100% of Currier A folios have <50% transition validity
- Even when A uses grammar vocabulary, the sequences are invalid

**Implication:** A tokens are not arranged according to grammar rules.

### 3. Forbidden Transitions OCCUR (5 violations)

Five instances of forbidden transition pairs occur in Currier A:

- This should be **0** if A respects the same hazard topology
- B corpus has **0** violations by definition (constraints derived from B)

**Implication:** A operates under different transition rules. The 17 forbidden pairs are NOT universal constraints.

### 4. Paradox: A Shows System-Track Signatures

Despite DISJOINT grammar, A meets 2/3 system-track conditions:

| Condition | Result |
|-----------|--------|
| Appears near hazards | YES (12.2% hazard tokens, 22.8% near-hazard transitions) |
| Participates in seams | YES (5 forbidden seam crossings) |
| Has operational vocabulary | NO (25.9%, threshold 30%) |

**Interpretation:** A is not simply HT-like filler. It engages with the same token vocabulary (hazard tokens present) but uses them differently.

### 5. Morphological Independence (41% divergence)

- 21 A-only prefixes (not used in B)
- 35 A-only suffixes (not used in B)
- 59% prefix overlap, 59% suffix overlap

**Known from prior work:** "Prefix-suffix archetypes 1, 3, 4 never appear in B-text" — CONFIRMED.

### 6. LINK Density Halved (3.0% vs 6.6%)

A shows only 45% of B's LINK density.

- B: 6.6% LINK tokens (waiting/non-intervention)
- A: 3.0% LINK tokens

**Interpretation:** A is NOT a waiting-heavy text. Less "deliberate non-intervention" behavior.

### 7. Structural Density: Label-Like

| Metric | Currier A | Currier B |
|--------|-----------|-----------|
| Tokens/folio (mean) | 100.1 | 283.2 |
| Tokens/folio (median) | 86.0 | 303.5 |
| Vocabulary diversity | 0.302 | 0.213 |

A is 3x sparser than B, with higher vocabulary diversity. This suggests:
- A is NOT procedural instruction sequences
- A may be definitional, indexical, or label-like

### 8. Execution Stall Rate: 86.4%

86.4% of A tokens are unrecognized by the grammar (would cause immediate execution stall).

- 100% of A folios have >50% stall rate
- 7,255 "dead ends" (3+ consecutive unknown tokens)

**Implication:** Currier A cannot be executed under the frozen grammar.

---

## What This Means for the Frozen Model

### Falsified Generalization

**Prior claim (implicit):** The 49-class grammar describes the Voynich Manuscript.

**Revised claim:** The 49-class grammar describes **Currier B only** (~64.7% of tokens, 82 folios).

### What Remains Valid

| Claim | Status |
|-------|--------|
| 49-class grammar exists | VALID (for Currier B) |
| 17 forbidden transitions | VALID (for Currier B) |
| MONOSTATE convergence | VALID (for Currier B) |
| 83 enumerated programs | VALID (all are Currier B) |

### What is Invalidated

| Claim | Status |
|-------|--------|
| Grammar generalizes to manuscript | **FALSIFIED** |
| Single unified control system | **FALSIFIED** |
| Hazard topology is universal | **FALSIFIED** (5 A violations) |

---

## Possible Interpretations (Post-Audit Speculation)

The following are SPECULATIVE and do not modify the structural finding:

1. **A = different author/tradition:** A and B were written by different hands with different grammatical conventions

2. **A = definitional/indexical:** A labels or defines concepts that B then operates on

3. **A = different language variant:** A and B are dialectal variants with overlapping but distinct vocabulary

4. **A = earlier draft:** A is a proto-version that B supersedes

5. **A = complementary system:** A and B work together but serve different functions

**NOTE:** These interpretations are NOT conclusions. The structural finding is simply that A is DISJOINT.

---

## Constraint Update

### New Constraints (CAud)

| # | Constraint |
|---|------------|
| 224 | Currier A grammar coverage = 13.6% (threshold 70%); 49-class grammar does NOT generalize to A; A vocabulary 66.8% novel |
| 225 | Currier A transition validity = 2.1% (threshold 60%); 100% of A folios have <50% validity; A sequences are invalid under B grammar |
| 226 | Currier A has 5 forbidden transition violations (B has 0); hazard topology is NOT universal; A operates under different rules |
| 227 | Currier A LINK density = 3.0% (B = 6.6%); 0.45x ratio; A shows less waiting behavior |
| 228 | Currier A structural density = 0.35x B; 100 vs 283 tokens/folio; A is sparse/label-like |
| 229 | Currier A classification = DISJOINT; A is a separate system from B, not executable under frozen grammar |

### Scope Revisions

All prior Tier 0 claims should be scoped to "Currier B" rather than "the manuscript":
- "49-class grammar" → "49-class Currier B grammar"
- "100% coverage" → "100% Currier B coverage"
- "17 forbidden transitions" → "17 Currier B forbidden transitions"
- "83 programs" → "83 Currier B programs"

---

## Files Generated

- `caud_main.py` — Main analysis script (all 8 tracks)
- `CAud_REPORT.md` — This report
- `caud_results.json` — Raw results data

---

## Phase Tag

```
Phase: CAud
Tier: 0 (STRUCTURAL - FALSIFIES GENERALIZATION)
Subject: Currier A Executability Boundary
Type: Grammar generalization test
Status: COMPLETE
Verdict: DISJOINT (13.6% coverage, 5 hazard violations, 86.4% stall rate)
```
