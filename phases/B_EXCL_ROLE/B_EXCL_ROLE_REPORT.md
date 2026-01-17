# B-EXCL-ROLE: B-Exclusive MIDDLEs as Grammar-Internal Operators

**Phase ID:** B-EXCL-ROLE
**Tier:** 2 (Structural Inference)
**Status:** COMPLETE
**Date:** 2026-01-16

---

## Executive Summary

> **B-exclusive MIDDLEs are NOT grammar-internal operators.** They are enriched at line **boundaries** (1.64x, p < 0.0001), but NOT adjacent to LINK or kernel tokens. They form a **diffuse** vocabulary (top-10 cover only 17.1%) rather than a concentrated operator set.

**Final characterization:**
> B-exclusive MIDDLEs are **boundary-condition discriminators** whose role is to stabilize line transitions and encode edge-case variation without touching the execution grammar.

---

## Research Questions

1. **RQ-1:** Are B-EXCL preferentially adjacent to LINK/kernel/boundary positions?
2. **RQ-2:** Does positional rigidity correlate with CEI?
3. **RQ-3:** Do a few B-EXCL dominate usage (concentration)?

---

## Results

### TEST 1: Grammar Adjacency Enrichment

| Position | B-EXCL Rate | SHARED Rate | Enrichment | p-value |
|----------|-------------|-------------|------------|---------|
| LINK adjacent | 30.3% | 30.8% | 0.98x | 0.742 |
| Kernel adjacent | 2.0% | 2.4% | 0.82x | 0.504 |
| **Boundary** | **29.4%** | **17.9%** | **1.64x** | **< 0.0001*** |

**Result:** B-EXCL are enriched at **boundaries** (line-initial/final), NOT adjacent to LINK or kernel tokens.

**Interpretation:** B-EXCL function as **boundary markers**, not as grammar-internal operators that modify LINK/kernel behavior.

---

### TEST 2: Positional Rigidity vs CEI

| Metric | Value |
|--------|-------|
| Spearman rho | -0.207 |
| p-value | 0.0745 |
| Expected | Negative (high CEI = tighter localization) |

**Regime means (positional entropy):**
| Regime | Mean Entropy |
|--------|-------------|
| REGIME_2 | 1.397 |
| REGIME_1 | 1.378 |
| REGIME_4 | 1.125 |
| REGIME_3 | 1.284 |

**Result:** Direction is correct (negative correlation) but NOT significant at p < 0.05.

**Interpretation:** Weak trend toward rigidity at high CEI, but insufficient evidence.

---

### TEST 3: Type Concentration

| Vocabulary | Top-10 Coverage | Unique Types |
|------------|-----------------|--------------|
| B-EXCL | **17.1%** | 569 |
| SHARED | 81.6% | 268 |

**Top 15 B-EXCL MIDDLEs:**
| MIDDLE | Count |
|--------|-------|
| lk | 30 |
| ked | 26 |
| ched | 17 |
| ted | 16 |
| ech | 15 |
| lkee | 15 |
| cthe | 12 |
| edy | 9 |
| edai | 9 |
| teed | 8 |

**Result:** B-EXCL is a **diffuse** vocabulary. Top-10 cover only 17.1% - far below the 60% threshold.

**Interpretation:** B-EXCL are NOT a small set of reused operators. They are a large, specialized vocabulary used sparsely.

---

## Hypothesis Evaluation

| Test | Criterion | Result | Status |
|------|-----------|--------|--------|
| TEST 1 | Enrichment > 1.5x (p < 0.05) | Boundary 1.64x (p < 0.0001) | **PASS** |
| TEST 2 | rho < -0.2, p < 0.05 | rho = -0.207, p = 0.0745 | FAIL |
| TEST 3 | Top-10 > 60% | 17.1% | FAIL |

**Verdict: 1/3 tests passed - HYPOTHESIS NOT SUPPORTED**

---

## What We Learned

### B-EXCL Are NOT Grammar-Internal Operators

The hypothesis (from C298, C485) predicted B-EXCL would be:
- Adjacent to LINK/kernel (grammar-critical positions) ❌
- Concentrated (few types dominating) ❌
- Positionally rigid with complexity ❌ (marginal)

Instead, B-EXCL are:
- **Boundary-enriched** (1.64x at line start/end)
- **Diffuse** (569 types, sparse usage)
- **Weakly correlated** with complexity

### Revised Interpretation

B-EXCL may function as:

1. **Boundary markers** - Specialized tokens at line transitions
2. **Rare discriminators** - Infrequent but specific vocabulary for edge cases
3. **Scribal variation** - B-specific orthographic patterns (e.g., -ed suffix variants)

The L-compounds (lk, lkee, lch) identified in C298 ARE present but not dominant - they comprise only a small fraction of the B-EXCL population.

---

## Three-Way MIDDLE Separation (Key Synthesis)

The MIDDLE slot now has clear functional stratification:

| Class | Appears Where | Role |
|-------|---------------|------|
| **A-exclusive** | Currier A only | Pure discrimination coordinates (registry) |
| **A/B-shared** | Everywhere | Execution-safe compatibility substrate |
| **B-exclusive** | B boundaries | Boundary framing & edge discrimination |
| **L-compounds** | Rare, B only | True grammar operators (small subset of B-EXCL) |

This is exactly what the architecture wants:
- Registry discrimination (A)
- Stable execution basis (shared)
- Boundary handling (B-exclusive)
- Minimal control law (kernel + LINK)

---

## Constraint Reconciliation

### C360 (Grammar is LINE-INVARIANT) - STRENGTHENED

If grammar is invariant across lines, then line boundaries must be handled **outside grammar proper**.

Boundary-enriched B-EXCL MIDDLEs fit perfectly: they are **control-law framing artifacts**, not control law itself.

### C485 (Grammar Minimality) - STRENGTHENED

Grammar minimality says only k, h, e, LINK and a tiny equivalence class are load-bearing.

This test confirms:
- B-exclusive vocabulary is NOT load-bearing
- It is diffuse, sparse, non-concentrated
- Therefore it CANNOT be grammar

### C298 (L-compound operators) - REFINED, NOT BROKEN

C298 survives unchanged but scoped:
- L-compounds remain true B-specific operators
- They are rare by design
- They are NOT representative of B-exclusive MIDDLEs as a class

### Shared MIDDLEs - IMPORTANCE CONFIRMED

The ~95% shared vocabulary is NOT unimportant because it doesn't differentiate.

> **Shared MIDDLEs matter because they make execution possible everywhere.**
> **They don't explain variation - they make variation safe.**

They are:
- The stable compatibility basis
- The only vocabulary surviving A → AZC → B projection
- The substrate on which all meaningful variation operates

---

## Governance

### Falsified
- Broad hypothesis "B-exclusive = grammar operators" is **FALSIFIED** (Tier 1)

### Preserved
- C298 remains exactly as written (scoped to L-compounds)

### Clarification (Tier 2)
> B-exclusive MIDDLEs predominantly function as boundary-condition discriminators and orthographic variants, not as execution grammar operators.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| B-EXCL occurrences | 919 |
| SHARED occurrences | 18,520 |
| B-EXCL unique types | 569 |
| Boundary enrichment | 1.64x (p < 0.0001) |
| LINK enrichment | 0.98x (not significant) |
| Top-10 concentration | 17.1% (vs 81.6% for SHARED) |

---

## Files

| File | Purpose |
|------|---------|
| `phases/B_EXCL_ROLE/b_excl_role_test.py` | Main analysis |
| `results/b_excl_role.json` | Full results |
| `phases/B_EXCL_ROLE/B_EXCL_ROLE_REPORT.md` | This report |

---

## Phase Tag

```
Phase: B-EXCL-ROLE
Tier: 2 (Structural Inference)
Subject: B-Exclusive MIDDLEs as Grammar-Internal Operators
Type: Role characterization
Status: COMPLETE
Verdict: HYPOTHESIS_NOT_SUPPORTED
Finding: B-EXCL are boundary-enriched (1.64x), diffuse vocabulary - NOT grammar-internal operators
Constraints: None (negative result, C298 remains valid but narrow)
```
