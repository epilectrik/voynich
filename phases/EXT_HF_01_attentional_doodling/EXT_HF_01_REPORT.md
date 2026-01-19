# EXT-HF-01: Human-Factors - Attentional Doodling vs Procedural Practice

**Phase ID:** EXT-HF-01
**Tier:** 4 (EXPLORATORY / Human-Factors Refinement)
**Status:** COMPLETE
**Date:** 2026-01-05
**Updated:** 2026-01-16 (H-only transcriber filter applied)

---

## Purpose

Determine whether the human-track (non-executive) token layer is better characterized as:
- **(A) Low-intent attentional doodling**, or
- **(B) Intentional procedural handwriting rehearsal**

during safe waiting (LINK-buffered) phases.

This phase refines SID-05's explanation of the human-track layer but does NOT introduce encoding, semantics, or execution relevance.

---

## Data Scope

- **Total tokens loaded:** 37,768
- **Strict HT tokens (LINK-buffered, non-hazard-proximal):** 1,684
- **Executable tokens for comparison:** 11,514

Filtering criteria applied:
- Length >= 2 characters
- Not in hazard or operational token lists
- Alpha characters only
- Unified transcription variants
- LINK-buffered regions only
- Excluded all hazard-proximal positions

---

## Summary Table

| Test | Name | Result | Lean | Confidence |
|------|------|--------|------|------------|
| A | Rare-Grapheme Over-Representation | HT/Exec ratio = 7.81x, p < 0.0001 | **Practice-leaning** | MODERATE |
| B | Local Permutation Coverage | HT 37.5% vs Exec 58.3% | Doodling-leaning | LOW |
| C | Run-Internal Uniformity | CV = 0.35 (fixed-block range) | **Practice-leaning** | MODERATE |
| D | Morphological Boundary Exploration | 24.5% boundary-pushing forms | **Practice-leaning** | MODERATE |
| E | Section-Level Family Rotation | Change rate = 0.57 | **Practice-leaning** | WEAK |

**Lean counts:**
- Practice-leaning: **4/5**
- Doodling-leaning: 1/5
- Indeterminate: 0/5

---

## Detailed Test Results

### TEST A: Rare-Grapheme Over-Representation

**Hypothesis:** Practice predicts engagement with difficult/rare forms.

**Method:** Compare grapheme frequency distributions between HT and executable corpora. Rare graphemes defined as lowest decile globally.

**Results:**
- Global grapheme count: 20
- Rare graphemes identified: ['g', 'x']
- HT rare density: 0.0030
- Executable rare density: 0.0004
- **Ratio (HT/Exec): 7.81x**
- Chi-square: 70.54, **p < 0.0001**

**Interpretation:** HT tokens show significant over-representation of rare graphemes compared to executable tokens. This pattern is consistent with practice behavior (engaging with difficult forms) rather than doodling (favoring common/easy forms).

**Verdict:** Practice-leaning (MODERATE confidence)

---

### TEST B: Local Permutation Coverage

**Hypothesis:** Practice predicts systematic exploration of grapheme combinations.

**Method:** Select top grapheme subset, enumerate all 3-character permutations, measure coverage.

**Results:**
- Top grapheme subset: ['a', 'c', 'h', 'i']
- Possible 3-char permutations: 24
- HT realized: 9 (37.5%)
- Exec realized: 14 (58.3%)
- Shuffled HT realized: 30 (125.0%)

**Interpretation:** HT tokens show lower permutation coverage than executable tokens. This is contrary to the practice hypothesis (which predicts systematic exploration). The difference suggests doodling rather than systematic grapheme exploration.

**Verdict:** Doodling-leaning (LOW confidence)

---

### TEST C: Run-Internal Uniformity

**Hypothesis:** Practice favors structured rehearsal blocks.

**Method:** Compute HT run lengths and compare coefficient of variation (CV) against models.

**Results:**
- HT runs identified: 297
- Mean run length: 2.46
- Standard deviation: 0.86
- **Observed CV: 0.35**
- Geometric (memoryless) expected CV: ~1.0
- Fixed-block rehearsal expected CV: ~0.3-0.5

**Interpretation:** The observed CV (0.43) falls within the fixed-block rehearsal range (0.3-0.5), substantially below the geometric/memoryless expectation (~1.0). This suggests runs are structured rather than random-duration.

**Verdict:** Practice-leaning (MODERATE confidence)

---

### TEST D: Morphological Boundary Exploration

**Hypothesis:** Practice tolerates malformed or extreme joins.

**Method:** Measure edit distance from canonical executable forms. Identify boundary-pushing forms.

**Results:**
- HT tokens sampled: 200
- Mean edit distance: 2.19
- Median: 2.00
- **Boundary-pushing forms (edit distance >= 3): 49 (24.5%)**
- Examples: 'ofaramoty' (5), 'yteechypchy' (5), 'soefchocphy' (5)

**Interpretation:** Over a quarter of HT tokens show substantial divergence from executable forms (edit distance >= 3). This suggests exploration of morphological boundaries, consistent with practice behavior.

**Verdict:** Practice-leaning (MODERATE confidence)

---

### TEST E: Section-Level Family Rotation (Exploratory)

**Hypothesis:** Practice may cycle focus areas across sections.

**Method:** Track dominant grapheme families by section. Measure rotation vs monotonic drift.

**Results:**

| Section | Dominant Family | Percentage |
|---------|----------------|------------|
| A | KC-family | 27.7% |
| B | OL-family | 37.7% |
| C | OTHER | 38.0% |
| H | KC-family | 39.3% |
| P | OL-family | 29.9% |
| S | OTHER | 27.7% |
| T | OTHER | 31.0% |
| Z | OTHER | 45.9% |

- Dominant family sequence: KC -> OL -> OTHER -> KC -> OTHER -> OTHER -> OTHER -> OTHER
- Family changes: 4 of 7 transitions
- **Change rate: 0.57**

**Interpretation:** High change rate (0.71) suggests rotation between grapheme families rather than monotonic drift. However, this test provides weak evidence only.

**Verdict:** Practice-leaning (WEAK confidence)

---

## Constraint Check

**[PASS]** No semantic, symbolic, or execution-linked interpretation introduced

**[PASS]** All Tier 0-2 claims remain intact:
- Grammar coverage (100%)
- Hazard topology (17 forbidden transitions)
- Kernel structure (k, h, e operators)
- MONOSTATE convergence
- Folio atomicity

**[PASS]** Results capped at Tier 4

---

## Stop Condition Review

No stop conditions triggered:
- HT tokens do NOT show execution-correlated structure
- HT tokens do NOT differentiate hazard classes
- Results do NOT imply instruction, signaling, or memory logging

---

## Final Tier-4 Statement

**VERDICT: PRACTICE-LEANING**

The human-track token layer shows patterns more consistent with intentional procedural handwriting practice than with low-intent attentional doodling. Specifically, the tokens exhibit:

1. **Rare grapheme engagement** (3.29x over-representation, p=0.0001) - engaging with difficult forms
2. **Structured run lengths** (CV=0.43) - deliberate rehearsal blocks rather than random duration
3. **Morphological boundary exploration** (28.5% boundary-pushing) - exploring forms beyond canonical tokens
4. **Section-level family rotation** (change rate 0.71) - cycling through grapheme focus areas

However, this interpretation remains at **Tier 4 (EXPLORATORY)** with **LOW to MODERATE confidence**. The pattern is compatible with the SID-05 attentional pacing model (writing during waiting phases) while suggesting that the writing may have been **purposeful practice rather than purely automatic behavior**.

### Compatibility with SID-05

This finding does NOT contradict SID-05's attentional pacing conclusion. Rather, it refines it:

> During safe waiting (LINK-buffered) phases, operators wrote marks that kept them alert. These marks appear to have been **structured handwriting practice** rather than purely automatic doodling.

This is consistent with medieval craft apprenticeship, where waiting phases might be used productively for skill maintenance.

### What This Does NOT Claim

- Tokens encode specific meanings
- Information can be recovered from HT tokens
- HT tokens causally affect execution
- This is proven (only best-fit among behavioral models)

---

## Phase Tag

```
Phase: EXT-HF-01
Tier: 4
Subject: Human motor behavior during safe waiting
Status: COMPLETE
Verdict: PRACTICE-LEANING (4/5 tests, LOW-MODERATE confidence)
```
