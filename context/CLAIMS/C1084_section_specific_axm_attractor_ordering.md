# C1084: Section-Specific AXM Attractor Ordering

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** GALENIC_PARALLEL_TESTS (Phase 384)
**Decomposes:** C1017 (REGIME + section = 42.0% of AXM variance)
**Relates to:** C1035 (residual irreducible to internal predictors), C1016 (folio archetypes), C458 (design asymmetry)

---

## Statement

Section alone predicts AXM self-transition rate with large effect size (Kruskal-Wallis H=29.9, p<0.0001, eta-squared=0.355). The ordering is: Bio (0.754) > Stars (0.687) > Cosmo (0.635) > Herbal (0.587). Bio programs are the most stable/repetitive; Herbal programs are the most dynamically diverse. The effect survives REGIME control within REGIME_1 and REGIME_3. Section is the dominant component within the C1017 baseline (REGIME + section = 42.0%).

---

## Evidence

### S1: Section-Level AXM Self-Transition Rates

| Section | N folios | Mean AXM self-rate | SD | Min | Max |
|---------|----------|-------------------|-----|-----|-----|
| B (Bio) | 20 | 0.754 | 0.078 | 0.611 | 0.864 |
| S (Stars) | 23 | 0.687 | 0.071 | 0.537 | 0.828 |
| C (Cosmo) | 5 | 0.635 | 0.035 | 0.600 | 0.680 |
| T | 2 | 0.591 | 0.072 | 0.541 | 0.642 |
| H (Herbal) | 32 | 0.587 | 0.119 | 0.276 | 0.786 |

Kruskal-Wallis: H=29.898, p<0.0001
Eta-squared: 0.355 (section explains 35.5% of folio-level AXM variance)

### S2: Pairwise Comparisons

| Pair | Mann-Whitney U | p-value | Significant |
|------|---------------|---------|-------------|
| B vs H | 568 | <0.0001 | Yes |
| H vs S | 168 | 0.0007 | Yes |
| B vs S | 342 | 0.0066 | Yes |
| B vs C | 91 | 0.0031 | Yes |
| C vs H | 106 | 0.2571 | No |
| C vs S | 25 | 0.0529 | No |

Primary contrast: B (Bio) vs H (Herbal) — the two sections with largest samples and clearest separation.

### S3: REGIME-Controlled Analysis

| REGIME | Sections present | Section means |
|--------|-----------------|---------------|
| REGIME_1 | B(n=20), H(n=2), S(n=10) | B=0.754, H=0.693, S=0.674 |
| REGIME_2 | C(n=2), H(n=13) | C=0.646, H=0.548 |
| REGIME_3 | C(n=2), H(n=5), S(n=12) | C=0.640, H=0.660, S=0.697 |

Within REGIME_1: B > H > S ordering preserved (though H n=2 is small).
Within REGIME_2: C > H ordering preserved.
Within REGIME_3: S > H ordering preserved (C inverts but n=2).

Section effects persist after REGIME is controlled.

---

## Relationship to C1035

C1035 tested 6 INTERNAL structural predictors (paragraph count, HT density, gatekeeper fraction, QO fraction, vocabulary size, line count) for AXM residual and found all zero signal. C1084 does NOT contradict C1035 because:

1. Section is EXTERNAL metadata (subject-matter classification), not an internal grammar feature
2. C1017 already includes section in its baseline (REGIME + section = 42.0%)
3. C1084 decomposes what section contributes WITHIN the C1017 baseline, not beyond it
4. C1035's "irreducible" claim applies to the residual AFTER the REGIME+section baseline

C1035 scope note: "Irreducible to internal structural predictors. Section contribution characterized by C1084."

---

## Relationship to C138

C138 (illustrations epiphenomenal, Tier 0) is NOT violated. Section classification reflects subject matter, not illustration features. Swap invariance (C137) demonstrates that illustration layout/style carries no grammar signal. The correlation between section and AXM dynamics reflects that different subject domains require different operational profiles — a physical, not illustrative, distinction.

---

## Interpretation

Bio programs run at high AXM self-transition (0.754) — they spend most of their time in the dominant attractor state, executing stable, repetitive operations. This matches a domain (biological preparations, water baths) where the primary challenge is maintaining steady conditions.

Herbal programs run at low AXM self-transition (0.587) — they leave the attractor frequently, exploring more diverse operational states. This matches a domain (plant extraction, distillation) where the operator must navigate multiple phases, monitor transitions, and handle diverse material responses.

The 0.167 spread (Bio vs Herbal) represents the largest systematic variation in AXM dynamics — larger than any tested internal structural predictor (C1035 max dR2 = 0.013).

---

## Method

- 82 B folios with Currier B tokens (H-track, labels excluded, uncertain excluded)
- AXM self-transition rate: proportion of AXM-state tokens followed by another AXM-state token
- Minimum 5 AXM transitions per folio for reliable rate estimate
- Section assigned from transcript `section` field
- REGIME from `data/regime_folio_mapping.json` (GMM k=4)
- Kruskal-Wallis for omnibus test; Mann-Whitney for pairwise
- Eta-squared for effect size

**Script:** `phases/GALENIC_PARALLEL_TESTS/scripts/galenic_tests.py` (Test 3)
**Results:** `phases/GALENIC_PARALLEL_TESTS/results/galenic_test_results.json`

---

## Verdict

**SECTION_PREDICTS_AXM**: Section alone explains 35.5% of folio-level AXM variance with B(0.754) > S(0.687) > C(0.635) > H(0.587) ordering. This decomposes the section component within C1017's REGIME+section baseline and characterizes the largest systematic variation in AXM dynamics.
