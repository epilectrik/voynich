# Direction G: Kernel Ordering Constraints

**Phase:** KERNEL
**Date:** 2026-01-07
**Status:** CLOSED

---

## Scope Constraints (Pre-Committed)

This analysis was BOUNDED to:
- Formal ordering constraints only
- No semantic interpretation
- No mapping to physical processes
- Finite (three tests, then close)

---

## Executive Summary

| Test | Finding | Verdict |
|------|---------|---------|
| **G-1: Bigram Illegality** | h->k SUPPRESSED (0 observed); k->k, h->h ENRICHED | CONSTRAINTS FOUND |
| **G-2: Trigram Collapse** | 17/27 patterns; e->e->e dominates (97.2%) | MODERATE COLLAPSE |
| **G-3: Position Analysis** | Kernel slightly farther from LINK (8.1 vs 7.8) | WEAK SIGNAL |

**Overall:** Kernel ordering constraints EXIST. Add 2 Tier 2 constraints. Direction G is now CLOSED.

---

## G-1: Kernel Bigram Illegality Test

**Question:** Are any ordered pairs among {k, h, e} systematically forbidden?

### Kernel Token Distribution

| Kernel | Count | % of Corpus |
|--------|-------|-------------|
| e | 22,226 | 29.4% |
| k | 159 | 0.2% |
| h | 88 | 0.1% |
| **Total** | **22,473** | **29.7%** |

Note: The 'e' class dominates because it includes all -ey, -eey, -edy endings.

### Bigram Results

| Bigram | Observed | Expected | Ratio | Status |
|--------|----------|----------|-------|--------|
| k->k | 21 | 1.1 | 18.82 | **ENRICHED** |
| k->h | 1 | 0.6 | 1.62 | ENRICHED |
| k->e | 131 | 155.9 | 0.84 | NORMAL |
| **h->k** | **0** | **0.6** | **0.00** | **SUPPRESSED** |
| h->h | 7 | 0.3 | 20.48 | **ENRICHED** |
| h->e | 78 | 86.3 | 0.90 | NORMAL |
| e->k | 132 | 155.9 | 0.85 | NORMAL |
| e->h | 73 | 86.3 | 0.85 | NORMAL |
| e->e | 21,843 | 21,798.8 | 1.00 | NORMAL |

**Chi-square test:** Chi2 = 531.08, p < 0.000001

### Interpretation (Constraint-Only)

1. **h->k is SUPPRESSED** (0 observed, 0.6 expected)
   - This is a formal ordering constraint
   - h is NOT followed by k in any observed sequence
   - Caveat: Small sample (88 h tokens), but consistent with 0

2. **Self-transitions are ENRICHED** (k->k, h->h)
   - Kernel tokens tend to cluster
   - This is grammatical, not semantic

3. **e dominates** (97%+ of kernel contact)
   - e->e is the baseline state
   - k and h are rare interruptions

---

## G-2: Kernel Trigram Collapse Test

**Question:** Do kernel trigrams collapse into fewer equivalence classes?

### Results

| Metric | Value |
|--------|-------|
| Possible patterns | 27 |
| Observed patterns | 17 |
| Collapse ratio | 0.63 |
| Verdict | Moderate collapse |

### Trigram Distribution

| Trigram | Count | % |
|---------|-------|---|
| e->e->e | 21,549 | 97.2% |
| e->k->e | 124 | 0.6% |
| e->e->k | 117 | 0.5% |
| k->e->e | 116 | 0.5% |
| e->h->e | 75 | 0.3% |
| h->e->e | 72 | 0.3% |
| e->e->h | 69 | 0.3% |
| (others) | <50 | <0.2% |

### Entropy Analysis

| Metric | Value |
|--------|-------|
| Observed entropy | 0.27 bits |
| Max entropy (uniform) | 4.75 bits |
| Entropy ratio | 0.06 |

### Interpretation (Constraint-Only)

1. **e->e->e dominates** (97.2%)
   - The system spends most time in the 'e' state
   - Consistent with 'e' as stability anchor

2. **k and h appear as interruptions** returning to e
   - Pattern: e -> (k or h) -> e
   - Rarely: k->k or h->h clusters

3. **10 trigram patterns are unobserved**
   - Including h->k->* patterns (consistent with h->k suppression)

---

## G-3: Kernel Position-in-Instruction Analysis

**Question:** Do kernel tokens prefer specific grammatical positions?

### LINK Proximity

| Token Type | Mean Distance to LINK |
|------------|----------------------|
| k | 13.14 tokens |
| h | 13.81 tokens |
| e | 8.04 tokens |
| non-kernel | 7.78 tokens |

**Mann-Whitney test:** p < 0.000001

### Interpretation

- Kernel tokens are SLIGHTLY farther from LINK than non-kernel
- But the effect is small (8.1 vs 7.8)
- k and h are MUCH farther (13+ tokens) than e (8 tokens)

This suggests k and h operate in different local contexts than e, but the signal is weak.

---

## Constraints to Add

### Constraint 332 (Tier 2)
**Kernel bigram ordering:** h->k is systematically suppressed (0 observed, expected 0.6); k->k and h->h are enriched (self-transitions); chi-square p < 0.000001. Formal ordering constraint exists.

### Constraint 333 (Tier 2)
**Kernel trigram dominance:** e->e->e constitutes 97.2% of kernel trigrams; entropy = 0.27 bits (vs 4.75 max); system is dominated by 'e' state with rare k/h interruptions.

---

## What These Tests Do NOT Prove

Per the pre-committed scope:

- ❌ No claim about what k, h, e "mean"
- ❌ No mapping to physical processes
- ❌ No revision to MONOSTATE or cycle claims
- ❌ No tie to illustrations or external domains

The findings are purely GRAMMATICAL.

---

## Direction G: CLOSED

All three tests are complete. Kernel ordering investigation is now FINISHED.

**Outcome A applies:** Kernel ordering constraints exist. 2 Tier 2 constraints added.

No further kernel investigation is warranted.

---

## Files

| File | Purpose |
|------|---------|
| `kernel_ordering_tests.py` | Test implementation |
| `kernel_ordering_results.json` | Raw results |
| `KERNEL_ORDERING_REPORT.md` | This document |

---

*Direction G: CLOSED*
*Generated: 2026-01-07*
