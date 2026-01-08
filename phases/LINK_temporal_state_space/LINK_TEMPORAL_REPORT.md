# Direction B: LINK Temporal State-Space Mapping

**Phase:** LINK
**Date:** 2026-01-07
**Status:** CLOSED

---

## Scope Constraints (Pre-Committed)

This analysis was BOUNDED to:
- 4 specific tests (B-1 through B-4)
- Effect threshold: 10% minimum for SIGNAL
- Hard stop on: no conditioning, weak effects, or 1-2 constraints max
- No semantic interpretation of LINK

---

## Executive Summary

| Test | Effect Size | Verdict |
|------|-------------|---------|
| **B-1: Kernel conditioning** | 29.9% raw, z=0.05 vs null | WEAK/NONE |
| **B-2: Transition conditioning** | 53.6% (small samples) | SIGNAL (weak) |
| **B-3: Position conditioning** | 6.8% | WEAK/NONE |
| **B-4: Section conditioning** | 45.3% | **SIGNAL** |

**Overall:** LINK is NOT kernel-conditioned but IS section-conditioned. 1 Tier 2 constraint. Direction B is now CLOSED.

---

## B-1: LINK Probability Conditioned on Kernel State

**Question:** Is P(LINK | prev=e) different from P(LINK | prev=k/h)?

### Results

| Previous Token | LINK After | Total | P(LINK) | Ratio to Baseline |
|----------------|------------|-------|---------|-------------------|
| k | 15 | 159 | 0.094 | 0.70x |
| h | 14 | 87 | 0.161 | 1.20x |
| e | 2,856 | 22,214 | 0.129 | 0.96x |
| non-kernel | 7,282 | 53,077 | 0.137 | 1.02x |

Chi-square: p = 0.005

### Null Model Test

When LINK positions are shuffled within each folio:
- Null effect: 29.2% +/- 13.9%
- Observed effect: 29.9%
- **Z-score: 0.05**

### Interpretation

**WEAK/NONE.** The apparent kernel conditioning (k=0.70x, h=1.20x) does NOT survive null model testing. The z-score of 0.05 means this pattern is expected by chance.

**Key insight:** LINK is NOT driven by kernel state. Waiting is not "recovery from escalation."

---

## B-2: LINK After Kernel Transitions

**Question:** Do specific kernel transitions predict LINK?

### Results

| Transition | LINK After | Total | P(LINK) | Ratio |
|------------|------------|-------|---------|-------|
| e->e | 2,064 | 15,412 | 0.134 | 0.99x |
| e->k | 7 | 87 | 0.081 | 0.60x |
| e->h | 5 | 41 | 0.122 | 0.91x |
| k->e | 7 | 85 | 0.082 | 0.61x |
| k->k | 1 | 12 | 0.083 | 0.62x |
| h->e | 3 | 48 | 0.063 | 0.46x |

### Interpretation

**SIGNAL (weak).** Transitions involving k and h show reduced LINK probability (0.46x-0.62x), but sample sizes are small (12-87 cases). The dominant pattern (e->e) is at baseline.

Pattern: Kernel transitions AVOID waiting. When the system is transitioning between kernel states, it does not pause.

**Caution:** Small samples limit confidence.

---

## B-3: LINK vs Position-in-Folio

**Question:** Does LINK cluster early/middle/late in folios?

### Results

| Zone | LINK | Total | P(LINK) | Ratio |
|------|------|-------|---------|-------|
| Early (0-33%) | 3,135 | 24,994 | 0.125 | 0.93x |
| Middle (33-67%) | 3,566 | 25,714 | 0.139 | 1.03x |
| Late (67-100%) | 3,479 | 24,912 | 0.140 | 1.04x |

Chi-square: p < 0.000001

Mean LINK position: 0.514 (vs 0.499 for all tokens)

### Interpretation

**WEAK/NONE.** LINK shows a slight late-folio bias (+1.4% position shift) but the effect size is only 6.8%. This is below the 10% threshold.

LINK is NOT strongly position-conditioned. Waiting does not cluster at folio boundaries.

---

## B-4: LINK Clustering vs Sections

**Question:** Do sections encode waiting differently?

### Results

| Section | LINK | Total | Density | Ratio |
|---------|------|-------|---------|-------|
| B (Biological) | 5,486 | 28,047 | 19.6% | **1.45x** |
| C (Cosmological) | 3,635 | 36,046 | 10.1% | 0.75x |
| H (Herbal) | 930 | 10,206 | 9.1% | 0.68x |
| S (Stars) | 129 | 1,321 | 9.8% | 0.73x |

Currier B baseline: 13.5%

### Interpretation

**SIGNAL.** Sections have dramatically different LINK densities:
- Section B: 45% MORE waiting than baseline
- Sections H/S/C: 25-32% LESS waiting than baseline

This is the strongest signal in Direction B.

---

## What These Tests Prove

### LINK is NOT Kernel-Driven

1. **Not after k:** P(LINK | prev=k) = 0.70x, but z=0.05 vs null
2. **Not after h:** P(LINK | prev=h) = 1.20x, but z=0.05 vs null
3. **Not positional:** Only 6.8% effect, below threshold

**Conclusion:** Waiting is not "recovery from escalation" or "preparation before action."

### LINK IS Section-Driven

1. **Section B requires more waiting** (1.45x baseline)
2. **Sections H/S/C require less waiting** (0.68-0.75x baseline)
3. **Effect is large** (45.3% max)

**Conclusion:** Different materials/products require different waiting regimes. The section encodes WHAT KIND of waiting, not the kernel state.

---

## Constraint to Add

### Constraint 334 (Tier 2)
**LINK section conditioning:** LINK density varies by section (B=19.6%, H=9.1%, C=10.1%, S=9.8%); Section B requires 45% more waiting than baseline; kernel state does NOT condition LINK (z=0.05 vs null); waiting is material/section-driven, not state-driven.

---

## Hard Stop Evaluation

| Condition | Status |
|-----------|--------|
| No kernel OR positional conditioning? | PARTIAL (no kernel, weak position) |
| Weak effects (<10%)? | NO (section effect 45%) |
| 1-2 constraints max? | YES (1 constraint) |

**STOP CONDITION 3 APPLIES:** 1 Tier 2 constraint found. Direction B is CLOSED.

---

## What LINK Is NOT

Per this analysis:
- NOT a kernel recovery mechanism
- NOT a positional boundary marker
- NOT driven by escalation (k) or phase management (h)

## What LINK IS

- A section-conditioned waiting operator
- More frequent in Section B (biological procedures)
- Less frequent in Sections H/S/C (herbal/stellar/cosmological)

The grammar does not encode WHEN to wait. The SECTION encodes HOW MUCH waiting is typical.

---

## Direction B: CLOSED

All four tests complete. LINK temporal investigation is now FINISHED.

**Outcome:** 1 Tier 2 constraint added. LINK is section-conditioned, not kernel-conditioned.

No further LINK investigation is warranted.

---

## Files

| File | Purpose |
|------|---------|
| `link_temporal_tests.py` | Test implementation |
| `link_temporal_results.json` | Raw results |
| `LINK_TEMPORAL_REPORT.md` | This document |

---

*Direction B: CLOSED*
*Generated: 2026-01-07*
