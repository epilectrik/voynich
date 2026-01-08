# EXT-HF-03: Procedural Fluency Reinforcement

**Phase ID:** EXT-HF-03
**Tier:** 4 (INTERPRETIVE / CONFIRMATORY)
**Status:** COMPLETE
**Date:** 2026-01-06

---

## Purpose

Evaluate whether the human-track (HT) token layer shows statistical signatures expected from **intentional handwriting practice** as opposed to **low-intent motor repetition/doodling**.

This phase is strictly **confirmatory** and **non-semantic**. Results may increase or decrease confidence in the practice hypothesis. No Tier 0-2 claims are modified.

---

## Data Scope

- **Total tokens loaded:** 120,768
- **HT tokens (strict filtered):** 6,002
- **Executable tokens:** 37,201
- **HT unique types:** 2,068
- **Exec unique types:** 5,268

Filtering criteria (identical to EXT-HF-01/02):
- Length >= 2 characters
- Alpha characters only
- Not in hazard, operational, kernel, or grammar token lists
- Non-hazard-proximal regions only

---

## Summary Table

| Test | Name | Metric | Lean | Strength |
|------|------|--------|------|----------|
| A | Grapheme Coverage Efficiency | HT=0.124 vs Exec=0.052 per token | **Practice-leaning** | MODERATE |
| B | Difficult Bigram Over-Rep | 5.75x ratio | **Practice-leaning** | MODERATE |
| C | Run-Internal Diversity | z=-86.2, div=0.927 | Doodling-leaning | MODERATE |
| D | Token Repetition Suppression | 17.1% vs 0.2% shuffled | Doodling-leaning | SUPPORTING |
| E | Alphabet Fidelity | 100% | Confirmed | PASS |

**Summary:**
- Practice-leaning: 2/5
- Doodling-leaning: 2/5 (1 supporting only)
- Confirmatory: 1/5

---

## Detailed Test Results

### TEST A: Grapheme Combination Coverage Efficiency

**Hypothesis:** Practice predicts higher combinatorial coverage per token.

**Results:**
- HT unique tokens: 2,068
- Exec unique tokens: 5,268
- **HT bigram coverage:** 256 unique bigrams, **0.124 per token**
- **Exec bigram coverage:** 273 unique bigrams, **0.052 per token**
- **Ratio (HT/Exec):** 2.38x
- HT trigram coverage: 1,018 unique, 0.492 per token
- Exec trigram coverage: 1,325 unique, 0.252 per token (ratio 1.95x)

**Shuffled baseline:**
- Mean: 0.172 per token
- Observed z-score: -24.29 (HT achieves LESS than shuffled)

**Interpretation:** Despite the negative z-score against shuffled baseline (which represents random character reordering), HT achieves **2.38x higher bigram coverage per token** than operational text. This means HT tokens explore more of the combinatorial space relative to their vocabulary size than operational tokens do.

The negative z-score indicates that HT tokens are not maximally diverse (random shuffling would be more diverse), but they are still significantly more exploratory than the operational vocabulary.

**Verdict:** Practice-leaning (MODERATE confidence)

---

### TEST B: Difficult Bigram Over-Representation

**Hypothesis:** Practice predicts engagement with rare/difficult character combinations.

**Results:**
- Bottom-decile (rare) bigrams in exec: 27 types
- Examples: 'nm', 'qn', 'yj', 'cy', 'sm', 'cc'
- **Exec rare density:** 27/170,603 = 0.000158
- **HT rare density:** 21/23,096 = 0.000909
- **Ratio (HT/Exec):** 5.75x

**Interpretation:** Rare bigrams are nearly **6x over-represented** in HT tokens compared to operational text. This strongly supports the practice hypothesis: writers intentionally engaged with difficult or unusual character combinations rather than favoring easy, common patterns.

**Verdict:** Practice-leaning (MODERATE confidence)

---

### TEST C: Run-Internal Combinatorial Diversity

**Hypothesis:** Practice predicts intentional variation within runs; doodling predicts repetitive patterns.

**Results:**
- HT runs (length >= 2): 809
- **Mean run diversity:** 0.927 (unique/total)
- **Mean run entropy:** 1.081 bits
- Exec run diversity: 0.924 (similar)
- **Shuffled baseline:** 0.999 +/- 0.001
- **Z-score:** -86.20

**Interpretation:** HT runs show **significantly LESS diversity** than the shuffled baseline (z=-86.2). This indicates within-run repetition—the same or similar tokens appearing together.

However, this finding is **ambiguous**:
- **Doodling interpretation:** Automatic repetition of comfortable patterns
- **Practice interpretation:** Deliberate repetition to master specific forms (drilling)

The exec runs show nearly identical diversity (0.924 vs 0.927), suggesting this pattern is not unique to HT.

**Verdict:** Doodling-leaning (MODERATE confidence) — but interpretation is ambiguous

---

### TEST D: Token Repetition Suppression (Supporting Only)

**Hypothesis:** Practice would suppress meaningless repetition; doodling would show elevated repetition.

**Results:**
- HT adjacent pairs: 1,247
- HT repetitions: 213
- **HT repeat rate:** 17.1%
- **Shuffled baseline:** 0.21% +/- 0.06%
- Percentile of observed: 0.0% (extreme outlier)
- Exec repeat rate: 3.5%

**Interpretation:** HT shows **extremely elevated adjacent repetition** (17.1% vs 0.2% baseline). This is 5x higher than even operational text (3.5%).

This could indicate:
- **Doodling:** Automatic repetition without intention
- **Practice:** Deliberate repetition to master a form (writing the same token multiple times)

Given the ambiguity, this test provides only **supporting** evidence, not decisive weight.

**Verdict:** Doodling-leaning (SUPPORTING only) — interpretation ambiguous

---

### TEST E: Operational Alphabet Fidelity (Guardrail)

**Hypothesis:** HT tokens should use exactly the operational alphabet if they represent practice.

**Results:**
- HT characters: 21
- Exec characters: 21
- Shared: 21 (100%)
- HT-only: 0
- Exec-only: 0
- **Alphabet fidelity:** 100%

**Interpretation:** HT uses **exactly the same grapheme inventory** as operational text. No deviations detected. This confirms that HT writing stays within the bounds of the operational writing system.

**Verdict:** Confirmed (PASS)

---

## Reconciliation of Apparent Contradiction

Tests A and B favor practice (higher coverage, rare bigram engagement), while Tests C and D favor doodling (low run diversity, high repetition). How do we reconcile this?

### Proposed Model: Exploration + Drilling

The data may reflect **two distinct practice behaviors**:

1. **Exploration (Tests A, B):** When starting new tokens, writers explored the combinatorial space more broadly than operational writing required. They engaged with rare bigrams and covered more of the possible character combinations per token.

2. **Drilling (Tests C, D):** Within runs, writers repeated similar forms—not randomly, but deliberately, to master specific patterns. This creates the elevated repetition signature.

This is consistent with **actual handwriting practice**, which typically involves:
- Writing many different forms (exploration)
- Repeating each form multiple times to build muscle memory (drilling)

### Alternative: True Doodling

A simpler interpretation is that HT tokens represent automatic motor behavior with:
- Incidentally diverse vocabulary (from extended exposure to the writing system)
- Naturally repetitive within-moment behavior

This cannot be ruled out from the current data.

---

## Constraint Check

**[PASS]** No semantic or encoding interpretations introduced

**[PASS]** All Tier 0-2 claims remain untouched:
- Grammar coverage (100%)
- Hazard topology (17 forbidden transitions)
- Kernel structure (k, h, e operators)
- MONOSTATE convergence
- Folio atomicity

**[PASS]** Results remain Tier 4 only

---

## Stop Condition Review

No stop conditions triggered:
- HT structure does NOT correlate with hazards or execution state
- Results do NOT imply instruction, signaling, or reader guidance
- No test suggests semantic differentiation

---

## Final Interpretive Statement (Tier 4)

**VERDICT: MIXED (Confidence: LOW)**

These confirmatory tests return **mixed results** for the handwriting-practice hypothesis. Of five tests:

- **2 tests favor practice:** Higher combinatorial coverage (A) and rare bigram engagement (B) suggest intentional exploration of the writing system's possibilities.

- **2 tests favor doodling:** Low run diversity (C) and high adjacent repetition (D) suggest automatic, repetitive motor behavior.

- **1 test confirms:** Alphabet fidelity (E) confirms HT stays within the operational character set.

The apparent contradiction may reflect **exploration + drilling** practice behavior (diverse vocabulary, repetitive execution) or may simply indicate automatic doodling with incidentally varied vocabulary.

**Key finding:** The 5.75x over-representation of rare bigrams (Test B) is the strongest signal. Doodling would predict the opposite—favoring easy, common patterns. This single result provides the most discriminating evidence for practice over doodling.

However, the overall confidence remains **LOW** due to the genuinely mixed signal. The practice hypothesis is **neither confirmed nor refuted** by these tests.

### What This Does NOT Claim

- HT tokens encode specific meanings
- Practice was instructional or for a reader
- HT tokens causally affect execution
- This is proven (interpretation remains speculative)

### Consistency with Prior Phases

These results are **compatible with** prior findings:
- **EXT-HF-01:** Practice-leaning (4/5 tests) — rare grapheme engagement, boundary exploration
- **EXT-HF-02:** No intentional layout function — opportunity-based placement
- **SID-05:** Attentional pacing — writing during waiting phases

The mixed signal here does not contradict these findings. The HT layer may reflect a combination of intentional practice and automatic motor behavior, with the balance undetermined.

---

## Phase Tag

```
Phase: EXT-HF-03
Tier: 4
Subject: Procedural handwriting fluency
Type: Confirmatory human-factors analysis
Status: COMPLETE
Verdict: MIXED (2 practice, 2 doodling, 1 confirmed; confidence LOW)
```
