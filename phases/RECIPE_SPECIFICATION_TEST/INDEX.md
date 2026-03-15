# Phase 588: RECIPE_SPECIFICATION_TEST

**Status:** COMPLETE
**Date:** 2026-03-14
**Version:** 5.61
**Constraints:** C1706-C1708

## Purpose

The crazy expert proposed that A folios are "preparation specifications" (recipes) whose PP MIDDLE sets define which B programs can run. The C475 graph would be a recipe co-occurrence network. But the expert then critiqued this: C755/C756 prove folios are coverage-optimized (generalized), which is the opposite of recipe-specific (specialized). This phase tests which interpretation holds with three targeted tests, incorporating size/hub controls and a coverage-matched null.

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/recipe_specification_test.py` | ~21s | 3 tests: PP content → B-side similarity (size-controlled), restricted PP discriminative power, specialization vs generalization |

## Results

### T1: PP Content Predicts B-Side Similarity (Size-Controlled)

| Metric | Value |
|--------|-------|
| Folio pairs | 6,441 |
| PP Jaccard mean | 0.300 |
| B-side cosine similarity mean | 0.969 |
| Raw Spearman rho | 0.470 |
| **Partial Spearman rho** (controlling size, hub, section) | **0.502** |
| Partial p-value | <1e-300 |
| Within-section rho | 0.467 |
| Between-section rho | 0.476 |

**PASS.** PP content genuinely predicts B-side operational similarity after controlling for pool size, hub fraction, and section membership. The partial correlation (0.502) is HIGHER than raw (0.470), meaning confounds were suppressing the signal, not inflating it. This overturns C753's class-level null (r=-0.038) — the signal exists at token level but not class level.

### T2: Folio-Restricted PP MIDDLEs as Recipe Signatures

| Metric | Value |
|--------|-------|
| Restricted PPs per folio (mean) | 2.3 |
| Multi-folio PPs per folio (mean) | 30.6 |
| Qualifying folios (≥4 each) | 19 |
| Restricted-PP between-folio distance | 0.520 |
| Multi-folio-PP between-folio distance | 0.005 |
| Cohen's d | 3.667 |
| Mann-Whitney p (one-sided) | 7.3e-58 |

**PASS.** Restricted-PP signatures differentiate folios massively more than multi-folio-PP signatures. But this is partly mechanical: the ~90 multi-folio hub MIDDLEs produce near-identical B-side signatures everywhere (distance 0.005), while the few restricted PPs have enough variation to discriminate. The N_restricted vs distinctiveness correlation is weak (rho=0.095, p=0.316).

### T3: Specialization vs Generalization (Category Diversity)

| Metric | Value |
|--------|-------|
| Real entropy mean | 2.830 |
| Coverage-matched null entropy mean | 2.816 |
| Mean z-score | 0.116 |
| Folios with z < -2 (specialized) | 3/114 |
| Folios with \|z\| < 1 (neutral) | 73/114 |
| Folios with z > 2 (generalized) | 0/114 |
| Real Gini mean | 0.247 |
| Null Gini mean | 0.258 |

**COVERAGE_MATCHED.** Folios are indistinguishable from coverage-matched random draws in category diversity. They are NOT specialized — every folio covers all 8 operational categories roughly equally. The "recipe" label's specialization prediction fails.

## Constraint Verdicts

| C# | Verdict | Description |
|----|---------|-------------|
| C1706 | PP_CONTENT_PREDICTS_BSIDE | Partial Spearman rho=0.502 (controlling size, hub fraction, section); PP MIDDLE content genuinely predicts B-side operational similarity at token level |
| C1707 | RESTRICTED_PP_DISCRIMINATIVE | Restricted-PP between-folio distance 0.520 vs multi-folio 0.005 (d=3.67); folio-restricted PPs carry disproportionate discriminative power but are rare (mean 2.3 per folio) |
| C1708 | FOLIO_CATEGORY_NOT_SPECIALIZED | Category entropy z=0.116 vs coverage-matched null; folios are category-generic, indistinguishable from coverage-optimized random draws |

## Verdict

**CONTENT_RELEVANT_NOT_SPECIALIZED.** PP content genuinely predicts B-side operational similarity (partial rho=0.502), overturning C753's class-level null. But folios are not categorically specialized — they are coverage-optimized pools spanning all operational categories equally. The "recipe" interpretation fails on specialization but succeeds on content relevance.

The emerging interpretation: A folios are **application-specific but category-generic**. Each folio selects a specific cross-category combination of PP MIDDLEs that enables specific B programs, without concentrating in any single operational category. The specialization is in WHICH tokens from each category, not WHICH categories.
