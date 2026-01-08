# EXT-HF-02: Visual Layout Stabilization of Human-Track Tokens

**Phase ID:** EXT-HF-02
**Tier:** 4 (ARTIFACT DESIGN / PHENOMENOLOGICAL)
**Status:** COMPLETE
**Date:** 2026-01-05

---

## Purpose

Test whether human-track (HT) tokens correlate with visual regularization of page and line layout (line length, whitespace, page fill).

This phase is strictly **non-semantic** and **non-executive**. Results may refine interpretation only. No Tier 0-2 claims are altered.

---

## Data Scope

- **Total tokens loaded:** 37,371
- **Lines analyzed:** 4,345
- **Folios analyzed:** 225
- **HT tokens analyzed:** 2,233 (strict filtering)
- **Lines with HT tokens:** 1,467 (35.9%)

Filtering criteria applied:
- Length >= 2 characters
- Not in hazard or operational token lists
- Alpha characters only
- Unified transcription (Takahashi "H" only)
- Excluded hazard-proximal positions

---

## Summary Table

| Test | Name | Metric | Direction | Verdict |
|------|------|--------|-----------|---------|
| 1 | Line Length Variance | CV=0.884 (HT) vs 0.482 (non-HT) | Counter-layout | **COUNTER_LAYOUT** |
| 2 | End-of-Line Placement | Mean=0.540 (HT) vs 0.495 (non-HT) | Slight right-bias | **NULL** |
| 3 | Page-Level Fill | r=+0.224 (HT% vs CV) | Counter-layout | **COUNTER_LAYOUT** |
| 4 | Counterfactual Removal | +3.0% CV increase on removal | Layout support | **HT_REGULARIZES** |
| 5 | Section Layout Targets | rho=0.667, p=0.071 | Exploratory | **ILLUSTRATIVE** |

**Summary:**
- Layout-supportive: 1/5
- Null (no effect): 1/5
- Counter-layout: 2/5
- Exploratory: 1/5

---

## Detailed Test Results

### TEST 1: Line Length Variance Reduction

**Hypothesis:** Lines containing HT tokens exhibit lower line-length variance.

**Results:**
- HT-present lines (n=1,467): Mean length 10.12, Variance 79.89, **CV=0.884**
- HT-absent lines (n=2,734): Mean length 8.19, Variance 15.55, **CV=0.482**
- Levene's test: F=22.29, **p < 0.0001**
- Shuffled control: Observed difference at 100th percentile

**Interpretation:** Lines containing HT tokens have significantly HIGHER variance than lines without HT tokens. This contradicts the layout-supportive hypothesis.

**Verdict:** COUNTER_LAYOUT

---

### TEST 2: End-of-Line Placement Bias

**Hypothesis:** HT tokens are preferentially located near line endings (visual filling).

**Results:**
- HT token positions: Mean=0.540, Median=0.600
- Non-HT token positions: Mean=0.495, Median=0.500
- % in last 30% of line: HT=43.1%, Non-HT=30.5%
- Mann-Whitney U: p < 0.000001
- **Effect size (rank-biserial r): -0.079** (negligible)

**Interpretation:** Although statistically significant, the effect size is negligible (r < 0.1). HT tokens show only a marginal tendency toward line endings, insufficient for practical layout filling function.

**Verdict:** NULL (effect too small to be meaningful)

---

### TEST 3: Page-Level Fill Regularity

**Hypothesis:** Pages with higher HT density display more uniform vertical fill.

**Results:**
- HT proportion range: 0.0% - 37.5%
- Fill CV range: 0.102 - 3.149
- Pearson correlation: **r = +0.224, p = 0.0007**
- Spearman correlation: **rho = +0.231, p = 0.0005**
- Tertile comparison:
  - Low HT folios (n=74): mean Fill CV = 0.334
  - High HT folios (n=74): mean Fill CV = 0.606

**Interpretation:** Higher HT density correlates with LESS uniform fill (positive correlation with CV). This contradicts the layout-supportive hypothesis.

**Verdict:** COUNTER_LAYOUT

---

### TEST 4: Counterfactual Removal Test (Critical)

**Hypothesis:** Removing HT tokens degrades visual layout regularity.

**Results:**
- Original layout: Mean=9.08, Variance=38.56, **CV=0.684**
- After HT removal: Mean=8.53, Variance=36.10, **CV=0.704**
- Variance change: -6.4%
- **CV change: +3.0%**
- Bootstrap 95% CI for CV difference: [0.010, 0.030]
- **Zero NOT in CI** (statistically significant)

**Interpretation:** Removing HT tokens significantly INCREASES layout irregularity (higher CV). This SUPPORTS the layout-supportive hypothesis for this specific test.

**Verdict:** HT_REGULARIZES

---

### TEST 5: Section-Specific Layout Targets (Exploratory)

**Results:**

| Section | Lines | Tokens | HT Tokens | HT% | Line CV |
|---------|-------|--------|-----------|-----|---------|
| A | 126 | 751 | 104 | 13.8% | 1.698 |
| B | 763 | 6,933 | 259 | 3.7% | 0.264 |
| C | 215 | 2,445 | 146 | 6.0% | 1.357 |
| H | 1,593 | 11,290 | 768 | 6.8% | 0.368 |
| P | 224 | 2,461 | 178 | 7.2% | 0.409 |
| S | 1,076 | 10,609 | 637 | 6.0% | 0.251 |
| T | 174 | 1,583 | 113 | 7.1% | 0.274 |
| Z | 174 | 1,299 | 121 | 9.3% | 2.700 |

- Section-level correlation (HT% vs Line CV): rho = 0.667, p = 0.071
- HT% range: 3.7% - 13.8% (spread: 10.1pp)

**Interpretation:** Sections with higher HT density tend to have higher line CV (more irregular). However, this is illustrative only per phase requirements.

**Verdict:** ILLUSTRATIVE_ONLY

---

## Reconciliation of Apparent Contradiction

Tests 1 and 3 find HT-present lines/folios have HIGHER variance, while Test 4 finds removing HT tokens INCREASES variance. This apparent contradiction resolves when considering causation direction:

### Proposed Model: HT Tokens as Partial Compensation

1. **Lines that receive HT tokens are intrinsically longer and more variable** (Test 1)
   - HT-present lines average 10.12 tokens vs 8.19 for HT-absent
   - These are not random lines; they have distinct properties

2. **HT tokens appear WHERE variability already exists** (Test 3)
   - Folios with higher intrinsic variability attract more HT tokens
   - The correlation is observational, not causal

3. **Given those variable lines, HT tokens reduce their irregularity** (Test 4)
   - Removing HT tokens from already-variable lines makes them MORE irregular
   - HT tokens partially compensate for underlying layout instability

### Synthesis

HT tokens do NOT cause layout regularity. Instead:

> **HT tokens appear in regions of high layout variability and partially compensate for that variability, but do not eliminate it.**

This is consistent with:
- Attentional pacing hypothesis (EXT-HF-01): operators write during waiting phases, which may coincide with layout-variable regions
- Practice hypothesis: longer lines offer more opportunity for practice writing
- No intentional layout-filling function required

---

## Constraint Check

**[PASS]** No semantic or communicative interpretation introduced

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
- HT tokens do NOT appear to encode page-level signals
- HT placement does NOT correlate with hazard classes
- Results do NOT imply reader instruction or visual language

---

## Final Tier-4 Statement

**VERDICT: NO INTENTIONAL LAYOUT FUNCTION DETECTED**

The data shows that:

1. HT tokens **cluster in layout-variable regions** (Tests 1, 3)
2. HT tokens **partially compensate** for that variability (Test 4)
3. This is consistent with **incidental placement**, not intentional visual design

**Interpretation:**

> Human-track tokens do not appear to serve an intentional layout stabilization function. They tend to appear in regions of higher layout variability (longer lines, more variable folios), where they provide marginal regularization but do not achieve uniform layout.

This finding is **compatible with both**:
- Attentional pacing (operators write where there is time/space)
- Handwriting practice (longer lines offer more opportunity)

Neither interpretation requires intentional layout design.

### What This Does NOT Claim

- HT tokens serve no function (they may serve other functions)
- Layout is random (there are clear section-level patterns)
- This disproves any prior finding

### What This DOES Claim (Tier 4)

- No evidence for **intentional visual layout stabilization**
- HT placement is **compatible with opportunity-based behavior**
- Layout effects are **incidental**, not designed

---

## Phase Tag

```
Phase: EXT-HF-02
Tier: 4
Subject: Visual layout regularization
Status: COMPLETE
Verdict: NO_INTENTIONAL_LAYOUT_FUNCTION (partial compensation in variable regions)
```
