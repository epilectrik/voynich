# SHARED-COMPLEXITY: Shared Vocabulary Evolution vs B Folio Complexity

**Phase ID:** SHARED-COMPLEXITY
**Tier:** 2 (Structural Inference)
**Status:** COMPLETE
**Date:** 2026-01-16

---

## Executive Summary

> **Shared MIDDLE vocabulary (A & B) is COMPLEXITY-INVARIANT.** ~95% of MIDDLEs used in B folios are SHARED, regardless of CEI or REGIME. Shared vocabulary serves a UNIFORM infrastructure role, not a complexity-graded one.

---

## Research Question

> As Currier B folios increase in execution complexity, does the *participation rate* of A&B shared MIDDLEs systematically change?

**Hypothesis (Expert-Predicted):**
- SHARED-hub usage should decrease with complexity
- SHARED-tail usage should increase with complexity
- B-EXCL usage should increase with complexity

---

## Results

### MIDDLE Class Participation

| Class | Count | % of B Usage |
|-------|-------|--------------|
| SHARED | 268 | **~95%** |
| B-EXCL | 569 | ~5% |
| A-EXCL | 349 | 0% (by definition) |

**Key finding:** B folios use almost exclusively SHARED vocabulary. Only ~5% of MIDDLEs used in B are B-exclusive.

### Regime Means (% SHARED)

| Regime | Mean % SHARED | n |
|--------|---------------|---|
| REGIME_2 (lowest CEI) | 94.2% | 10 |
| REGIME_1 | 95.7% | 31 |
| REGIME_4 | 94.6% | 25 |
| REGIME_3 (highest CEI) | 95.2% | 16 |

**Kruskal-Wallis:** H=5.19, p=0.159 (not significant)

The range is only 1.5 percentage points across all regimes. **Shared vocabulary is regime-invariant.**

### CEI Correlations

| Metric | Spearman rho | p-value | Result |
|--------|-------------|---------|--------|
| pct_shared vs CEI | 0.042 | 0.709 | NOT SIGNIFICANT |
| pct_shared_hub vs CEI | -0.102 | 0.364 | NOT SIGNIFICANT |
| pct_shared_tail vs CEI | 0.123 | 0.271 | NOT SIGNIFICANT |
| pct_b_excl vs CEI | -0.042 | 0.709 | NOT SIGNIFICANT |

**No complexity gradient detected.** The direction of pct_shared_hub (-0.102) and pct_shared_tail (+0.123) match the hypothesis, but neither reaches significance.

### Escape Density Correlation

| Metric | Spearman rho | p-value | Result |
|--------|-------------|---------|--------|
| pct_shared vs escape | 0.227 | 0.041 | SIGNIFICANT* |

**One significant finding:** Higher escape density (more forgiving folios) correlates with slightly higher SHARED usage. This suggests:
- More forgiving programs may use slightly broader (more shared) vocabulary
- Stricter programs may rely slightly more on B-exclusive vocabulary

### Permutation Control

| Test | Observed rho | Permutation p |
|------|--------------|---------------|
| pct_shared vs CEI | 0.042 | 0.705 |
| pct_shared_hub vs CEI | -0.102 | 0.336 |

Permutation p-values confirm no Zipf artifacts - the null result is robust.

---

## Interpretation

### Hypothesis Status: NOT SUPPORTED

| Prediction | Result |
|------------|--------|
| SHARED-hub decreases with CEI | Direction correct (rho=-0.102), not significant |
| SHARED-tail increases with CEI | Direction correct (rho=+0.123), not significant |
| B-EXCL increases with CEI | Direction WRONG (rho=-0.042), not significant |

**0/3 hypothesis checks passed.**

### What This Means

1. **Shared vocabulary is infrastructure, not content**
   - ~95% of B's MIDDLE usage comes from SHARED vocabulary
   - This percentage doesn't change with complexity
   - SHARED serves as stable procedural grammar

2. **Complexity lives in the ~5% B-EXCL space**
   - If complexity modulates vocabulary at all, it must operate within the small B-exclusive fraction
   - This may be too small a signal to detect

3. **The A→B boundary is simpler than hypothesized**
   - B doesn't "graduate" from shared to specialized vocabulary as complexity increases
   - Instead, B uniformly uses shared vocabulary across all complexity levels

### Tier 2 Implications

This is a **negative result with interpretive value**:

> **Shared MIDDLE vocabulary serves a uniform infrastructure role. Complexity differences between B folios do NOT manifest as vocabulary composition shifts.**

This constrains interpretations:
- ❌ SHARED vocabulary is NOT complexity-graded
- ❌ Hub/tail stratification within SHARED is NOT complexity-dependent
- ✅ SHARED serves uniform grammatical function across all B programs

---

## Constraint Implications

### No New Constraint Warranted

The hypothesis was not supported. Rather than add a constraint, this result:
- Confirms C384 (no entry-level A-B coupling) - vocabulary composition is also invariant
- Suggests complexity operates through structural mechanisms, not vocabulary selection

### Potential Model Update

Update interpretation in MODEL_CONTEXT.md:

> SHARED vocabulary (268 MIDDLEs) serves uniform infrastructure role across all B complexity levels (~95% usage invariant). Complexity differences manifest through structural grammar, not vocabulary composition.

---

## Files

| File | Purpose |
|------|---------|
| `phases/SHARED_COMPLEXITY/shared_complexity_test.py` | Main analysis script |
| `results/shared_complexity.json` | Full results with per-folio compositions |
| `phases/SHARED_COMPLEXITY/SHARED_COMPLEXITY_REPORT.md` | This report |

---

## Phase Tag

```
Phase: SHARED-COMPLEXITY
Tier: 2 (Structural Inference)
Subject: Shared Vocabulary Evolution vs B Folio Complexity
Type: Complexity correlation analysis
Status: COMPLETE
Verdict: HYPOTHESIS_NOT_SUPPORTED - Shared vocabulary is complexity-invariant
Constraints: None (negative result)
```
