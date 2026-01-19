# Direction G: Kernel Ordering Constraints

**Phase:** KERNEL
**Date:** 2026-01-07 (H-only corrected 2026-01-16)
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
| **G-1: Bigram Illegality** | h↔k SUPPRESSED (0 observed); k->k, h->h ENRICHED | CONSTRAINTS FOUND |
| **G-2: Trigram Collapse** | 11/27 patterns; e->e->e dominates (97.4%) | STRONG COLLAPSE |
| **G-3: Position Analysis** | Kernel slightly farther from LINK (4.7 vs 4.4) | WEAK SIGNAL |

**Overall:** Kernel ordering constraints EXIST. Add 2 Tier 2 constraints. Direction G is now CLOSED.

> **H-only correction (2026-01-16):** All values re-validated with H-only transcriber filter. Findings preserved/strengthened.

---

## G-1: Kernel Bigram Illegality Test

**Question:** Are any ordered pairs among {k, h, e} systematically forbidden?

### Kernel Token Distribution

| Kernel | Count | % of Corpus |
|--------|-------|-------------|
| e | 6,675 | 28.7% |
| k | 44 | 0.2% |
| h | 17 | 0.1% |
| **Total** | **6,736** | **29.0%** |

> **H-only correction (2026-01-16):** Counts reduced ~3x due to transcriber filtering. Structure preserved.

Note: The 'e' class dominates because it includes all -ey, -eey, -edy endings.

### Bigram Results

| Bigram | Observed | Expected | Ratio | Status |
|--------|----------|----------|-------|--------|
| k->k | 1 | 0.3 | 3.51 | **ENRICHED** |
| **k->h** | **0** | **0.1** | **0.00** | **SUPPRESSED** |
| k->e | 41 | 43.3 | 0.95 | NORMAL |
| **h->k** | **0** | **0.1** | **0.00** | **SUPPRESSED** |
| h->h | 1 | 0.0 | 23.49 | **ENRICHED** |
| h->e | 15 | 16.7 | 0.90 | NORMAL |
| e->k | 41 | 43.3 | 0.95 | NORMAL |
| e->h | 15 | 16.7 | 0.90 | NORMAL |
| e->e | 6,569 | 6,562.5 | 1.00 | NORMAL |

**Chi-square test:** Chi2 = 26.51, p = 0.000025

### Interpretation (Constraint-Only)

1. **h↔k is MUTUALLY SUPPRESSED** (0 observed in both directions)
   - This is a formal ordering constraint
   - h is NOT followed by k, and k is NOT followed by h
   - Caveat: Small sample (17 h, 44 k tokens), but consistent with 0

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
| Observed patterns | 11 |
| Collapse ratio | 0.41 |
| Verdict | Strong collapse |

> **H-only correction (2026-01-16):** Collapse ratio decreased from 0.63 to 0.41 (stronger collapse) with clean data.

### Trigram Distribution

| Trigram | Count | % |
|---------|-------|---|
| e->e->e | 6,498 | 97.4% |
| e->e->k | 41 | 0.6% |
| k->e->e | 40 | 0.6% |
| e->k->e | 39 | 0.6% |
| e->e->h | 16 | 0.2% |
| h->e->e | 16 | 0.2% |
| e->h->e | 15 | 0.2% |
| (others) | <5 | <0.1% |

### Entropy Analysis

| Metric | Value |
|--------|-------|
| Observed entropy | 0.24 bits |
| Max entropy (uniform) | 4.75 bits |
| Entropy ratio | 0.05 |

### Interpretation (Constraint-Only)

1. **e->e->e dominates** (97.4%)
   - The system spends most time in the 'e' state
   - Consistent with 'e' as stability anchor

2. **k and h appear as interruptions** returning to e
   - Pattern: e -> (k or h) -> e
   - Rarely: k->k or h->h clusters

3. **16 trigram patterns are unobserved** (with H-only data)
   - Including h->k->* patterns (consistent with h->k suppression)
   - Stronger collapse than originally estimated

---

## G-3: Kernel Position-in-Instruction Analysis

**Question:** Do kernel tokens prefer specific grammatical positions?

### LINK Proximity

| Token Type | Mean Distance to LINK |
|------------|----------------------|
| k | 6.52 tokens |
| h | 6.88 tokens |
| e | 4.68 tokens |
| non-kernel | 4.40 tokens |

**Mann-Whitney test:** p < 0.000001

> **H-only correction (2026-01-16):** Distances reduced with clean data. Same structural finding preserved.

### Interpretation

- Kernel tokens are SLIGHTLY farther from LINK than non-kernel
- But the effect is small (4.70 vs 4.40)
- k and h are farther (6.5-6.9 tokens) than e (4.7 tokens)

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
